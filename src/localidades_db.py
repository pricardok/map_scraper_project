# src/localidades_db.py
"""Cache (PostgreSQL ou DuckDB) da base de localidades do IBGE.

Guarda apenas o essencial, para não inflar o banco:
    localidades_estados     -> uf, nome
    localidades_municipios  -> id_municipio, nome, uf + estado da coleta de bairros
    localidades_bairros     -> id_municipio, nome, id_distrito

Cada operação abre e fecha a conexão, então o cache nunca segura uma conexão
aberta durante o scraping.
"""
from contextlib import contextmanager
from datetime import datetime

import pandas as pd

from src import backend

# Origem da lista de bairros gravada para uma cidade.
FONTE_IBGE = "ibge"           # distritos do IBGE (quantidade suficiente)
FONTE_OVERPASS = "overpass"   # complementado/obtido via OpenStreetMap
FONTE_CIDADE = "cidade"       # nenhum bairro usado: busca a cidade inteira


class CacheIndisponivel(Exception):
    """Não foi possível abrir/gravar a base de localidades (ex.: servidor fora)."""


@contextmanager
def _conexao():
    """Abre uma conexão transacional; commit no fim, rollback em caso de erro."""
    try:
        conn = backend.conectar()
    except Exception as e:
        raise CacheIndisponivel(f"não foi possível conectar ao banco: {e}") from e
    try:
        yield conn
        backend.commit(conn)
    except Exception:
        if not backend.IS_DUCKDB:
            conn.rollback()
        raise
    finally:
        backend.close(conn)


def _df(conn, sql, params=None):
    return backend.query_df(conn, sql, params)


def _inserir_upsert(conn, table, columns, df, conflict, set_clause):
    backend.bulk_upsert(
        conn,
        table=table,
        columns=columns,
        rows=backend.df_to_rows(df),
        conflict=conflict,
        set_clause=set_clause,
    )


def ler_estados():
    with _conexao() as conn:
        df = _df(conn, "SELECT uf, nome FROM localidades_estados ORDER BY nome")
    return df.to_dict("records")


def salvar_estados(registros):
    df = pd.DataFrame(list(registros), columns=["uf", "nome"]).drop_duplicates("uf")
    with _conexao() as conn:
        _inserir_upsert(conn, "localidades_estados", ["uf", "nome"], df,
                        conflict="uf", set_clause="nome = excluded.nome")
    return len(df)


def ler_municipios(uf):
    with _conexao() as conn:
        df = _df(conn, """
            SELECT id_municipio, nome, uf, bairros_fonte
            FROM localidades_municipios WHERE uf = %s ORDER BY nome
        """.replace("%s", backend.ph()), [uf])
    return df.to_dict("records")


def ler_municipios_pendentes(uf):
    """Municípios da UF cujos bairros ainda não foram resolvidos (bairros_fonte nulo)."""
    with _conexao() as conn:
        df = _df(conn, """
            SELECT id_municipio, nome
            FROM localidades_municipios
            WHERE uf = %s AND bairros_fonte IS NULL
            ORDER BY nome
        """.replace("%s", backend.ph()), [uf])
    return df.to_dict("records")


def salvar_municipios(registros):
    df = pd.DataFrame(list(registros), columns=["id_municipio", "nome", "uf"])
    df = df.dropna(subset=["id_municipio"]).drop_duplicates("id_municipio")
    with _conexao() as conn:
        # UPSERT preserva bairros_fonte/bairros_atualizado_em já gravados.
        _inserir_upsert(conn, "localidades_municipios", ["id_municipio", "nome", "uf"], df,
                        conflict="id_municipio",
                        set_clause="nome = excluded.nome, uf = excluded.uf")
    return len(df)


def buscar_municipio(cidade, uf):
    """Retorna {id_municipio, nome, uf, bairros_fonte} ou None se não estiver na base."""
    p = backend.ph()
    with _conexao() as conn:
        linha = backend.query_one(conn, f"""
            SELECT id_municipio, nome, uf, bairros_fonte
            FROM localidades_municipios
            WHERE uf = {p} AND lower(nome) = lower({p})
            LIMIT 1
        """, [uf, cidade])
    if not linha:
        return None
    return {
        "id_municipio": linha[0],
        "nome": linha[1],
        "uf": linha[2],
        "bairros_fonte": linha[3],
    }


def ler_bairros(id_municipio):
    with _conexao() as conn:
        df = _df(conn,
            "SELECT nome FROM localidades_bairros WHERE id_municipio = %s ORDER BY nome"
            .replace("%s", backend.ph()), [int(id_municipio)],
        )
    return df["nome"].tolist()


def _normalizar_bairros(registros):
    linhas = []
    for item in registros or []:
        if isinstance(item, dict):
            nome = str(item.get("nome") or "").strip()
            id_distrito = item.get("id_distrito")
        else:
            nome = str(item or "").strip()
            id_distrito = None
        if nome:
            linhas.append({"nome": nome, "id_distrito": id_distrito})

    df = pd.DataFrame(linhas, columns=["nome", "id_distrito"])
    if df.empty:
        return df
    df["id_distrito"] = df["id_distrito"].astype("Int64")
    return df.drop_duplicates("nome")


def salvar_bairros(id_municipio, registros, fonte):
    """Grava a lista final de bairros de uma cidade e marca a origem da coleta.

    A lista é autoritativa para a cidade: bairros que não estão nela são
    removidos (delete da cidade + re-insert), para o cache não acumular nomes
    de uma coleta anterior. `fonte` = 'ibge', 'overpass' ou 'cidade'.
    """
    id_municipio = int(id_municipio)
    df = _normalizar_bairros(registros)

    with _conexao() as conn:
        p = backend.ph()
        if df.empty:
            backend.execute(conn, f"DELETE FROM localidades_bairros WHERE id_municipio = {p}",
                            [id_municipio])
        else:
            df.insert(0, "id_municipio", id_municipio)
            # Autoritativo por cidade: apaga tudo da cidade e reinsere.
            backend.execute(conn, f"DELETE FROM localidades_bairros WHERE id_municipio = {p}",
                            [id_municipio])
            _inserir_upsert(
                conn, "localidades_bairros", ["id_municipio", "nome", "id_distrito"], df,
                conflict="id_municipio, nome",
                set_clause="id_distrito = excluded.id_distrito",
            )

        backend.execute(conn, f"""
            UPDATE localidades_municipios
            SET bairros_fonte = {p}, bairros_atualizado_em = {p}
            WHERE id_municipio = {p}
        """, [fonte, datetime.now(), id_municipio])
    return len(df)


def salvar_distritos_bulk(distritos, min_bairros=3):
    """Grava todos os distritos do IBGE de uma vez (sincronização completa).

    É aditivo (upsert por id_municipio+nome): não apaga bairros que já existem,
    para não destruir listas complementadas pelo OpenStreetMap.

    Marca como 'ibge' apenas os municípios com pelo menos `min_bairros` distritos
    úteis (desconsiderando o distrito que tem o mesmo nome da cidade).
    """
    df = pd.DataFrame(list(distritos), columns=["id_municipio", "nome", "id_distrito"])
    df = df.dropna(subset=["id_municipio", "nome"]).drop_duplicates(["id_municipio", "nome"])
    df["id_distrito"] = df["id_distrito"].astype("Int64")

    with _conexao() as conn:
        p = backend.ph()
        _inserir_upsert(
            conn, "localidades_bairros", ["id_municipio", "nome", "id_distrito"], df,
            conflict="id_municipio, nome",
            set_clause="id_distrito = excluded.id_distrito",
        )
        backend.execute(conn, f"""
            UPDATE localidades_municipios
            SET bairros_fonte = {p}, bairros_atualizado_em = {p}
            WHERE bairros_fonte IS NULL
              AND id_municipio IN (
                  SELECT b.id_municipio
                  FROM localidades_bairros b
                  JOIN localidades_municipios mm ON mm.id_municipio = b.id_municipio
                  WHERE lower(b.nome) <> lower(mm.nome)
                  GROUP BY b.id_municipio
                  HAVING COUNT(*) >= {p}
              )
        """, [FONTE_IBGE, datetime.now(), int(min_bairros)])
    return len(df)


def estatisticas():
    with _conexao() as conn:
        def _count(sql):
            return backend.query_one(conn, sql)[0]
        estados = _count("SELECT COUNT(*) FROM localidades_estados")
        municipios = _count("SELECT COUNT(*) FROM localidades_municipios")
        bairros = _count("SELECT COUNT(*) FROM localidades_bairros")
        prontas = _count("SELECT COUNT(*) FROM localidades_municipios WHERE bairros_fonte IS NOT NULL")
    return {
        "estados": estados,
        "municipios": municipios,
        "bairros": bairros,
        "cidades_prontas": prontas,
    }
