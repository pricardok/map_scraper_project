# src/localidades_db.py
"""Cache local (DuckDB) da base de localidades do IBGE.

Guarda apenas o essencial, para não inflar o banco:
    localidades_estados     -> uf, nome
    localidades_municipios  -> id_municipio, nome, uf + estado da coleta de bairros
    localidades_bairros     -> id_municipio, nome, id_distrito

O arquivo é o mesmo DuckDB dos leads (data/leads.duckdb). Cada operação abre e
fecha a conexão, então o cache nunca segura o banco travado durante o scraping.
"""
import os
from contextlib import contextmanager
from datetime import datetime

import duckdb
import pandas as pd

DB_PATH_PADRAO = os.path.join("data", "leads.duckdb")

# Origem da lista de bairros gravada para uma cidade.
FONTE_IBGE = "ibge"           # distritos do IBGE (quantidade suficiente)
FONTE_OVERPASS = "overpass"   # complementado/obtido via OpenStreetMap
FONTE_CIDADE = "cidade"       # nenhum bairro usado: busca a cidade inteira


class CacheIndisponivel(Exception):
    """Não foi possível abrir ou gravar a base local (ex.: arquivo travado)."""


_DDL = (
    """
    CREATE TABLE IF NOT EXISTS localidades_estados (
        uf VARCHAR PRIMARY KEY,
        nome VARCHAR NOT NULL
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS localidades_municipios (
        id_municipio BIGINT PRIMARY KEY,
        nome VARCHAR NOT NULL,
        uf VARCHAR NOT NULL,
        bairros_fonte VARCHAR,
        bairros_atualizado_em TIMESTAMP
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS localidades_bairros (
        id_municipio BIGINT NOT NULL,
        nome VARCHAR NOT NULL,
        id_distrito BIGINT,
        PRIMARY KEY (id_municipio, nome)
    )
    """,
)


# Se false, nenhuma DDL é executada: o cache é aberto somente para leitura.
# Definido por `src/locations.py` a partir de LOCALIDADES_SALVAR.
CRIAR_TABELAS = True


@contextmanager
def conexao(db_path=None):
    caminho = db_path or DB_PATH_PADRAO
    diretorio = os.path.dirname(caminho)
    if diretorio:
        os.makedirs(diretorio, exist_ok=True)
    try:
        con = duckdb.connect(caminho)
    except Exception as e:
        raise CacheIndisponivel(f"{caminho}: {e}") from e
    try:
        if CRIAR_TABELAS:
            for ddl in _DDL:
                con.execute(ddl)
        yield con
    finally:
        con.close()


def _ler(con, sql, params=None):
    """Executa uma leitura, traduzindo 'tabela não existe' em CacheIndisponivel."""
    try:
        return con.execute(sql, params) if params else con.execute(sql)
    except duckdb.CatalogException as e:
        raise CacheIndisponivel(
            "tabelas de localidades não existem neste banco (rode a sincronização no menu)"
        ) from e


def _inserir_lote(con, df, sql):
    if df is None or df.empty:
        return
    con.register("_lote", df)
    try:
        con.execute(sql)
    finally:
        con.unregister("_lote")


def ler_estados(db_path=None):
    with conexao(db_path) as con:
        df = _ler(con, "SELECT uf, nome FROM localidades_estados ORDER BY nome").df()
    return df.to_dict("records")


def salvar_estados(registros, db_path=None):
    df = pd.DataFrame(list(registros), columns=["uf", "nome"]).drop_duplicates("uf")
    with conexao(db_path) as con:
        _inserir_lote(con, df, """
            INSERT INTO localidades_estados (uf, nome)
            SELECT uf, nome FROM _lote
            ON CONFLICT (uf) DO UPDATE SET nome = excluded.nome
        """)
    return len(df)


def ler_municipios(uf, db_path=None):
    with conexao(db_path) as con:
        df = _ler(con,
            """SELECT id_municipio, nome, uf, bairros_fonte
               FROM localidades_municipios WHERE uf = ? ORDER BY nome""",
            [uf],
        ).df()
    return df.to_dict("records")


def ler_municipios_pendentes(uf, db_path=None):
    """Municípios da UF cujos bairros ainda não foram resolvidos (bairros_fonte nulo)."""
    with conexao(db_path) as con:
        df = _ler(con, """
            SELECT id_municipio, nome
            FROM localidades_municipios
            WHERE uf = ? AND bairros_fonte IS NULL
            ORDER BY nome
        """, [uf]).df()
    return df.to_dict("records")


def salvar_municipios(registros, db_path=None):
    df = pd.DataFrame(list(registros), columns=["id_municipio", "nome", "uf"])
    df = df.dropna(subset=["id_municipio"]).drop_duplicates("id_municipio")
    with conexao(db_path) as con:
        # UPSERT preserva bairros_fonte/bairros_atualizado_em já gravados.
        _inserir_lote(con, df, """
            INSERT INTO localidades_municipios (id_municipio, nome, uf)
            SELECT id_municipio, nome, uf FROM _lote
            ON CONFLICT (id_municipio) DO UPDATE SET
                nome = excluded.nome,
                uf = excluded.uf
        """)
    return len(df)


def buscar_municipio(cidade, uf, db_path=None):
    """Retorna {id_municipio, nome, uf, bairros_fonte} ou None se não estiver na base."""
    with conexao(db_path) as con:
        linha = _ler(con, """
            SELECT id_municipio, nome, uf, bairros_fonte
            FROM localidades_municipios
            WHERE uf = ? AND lower(nome) = lower(?)
            LIMIT 1
        """, [uf, cidade]).fetchone()
    if not linha:
        return None
    return {
        "id_municipio": linha[0],
        "nome": linha[1],
        "uf": linha[2],
        "bairros_fonte": linha[3],
    }


def ler_bairros(id_municipio, db_path=None):
    with conexao(db_path) as con:
        df = _ler(con,
            "SELECT nome FROM localidades_bairros WHERE id_municipio = ? ORDER BY nome",
            [int(id_municipio)],
        ).df()
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


def salvar_bairros(id_municipio, registros, fonte, db_path=None):
    """Grava a lista final de bairros de uma cidade e marca a origem da coleta.

    A lista é autoritativa para a cidade: bairros que não estão nela são
    removidos, para o cache não acumular nomes de uma coleta anterior.
    `fonte` = 'ibge', 'overpass' ou 'cidade' (sem bairros úteis).
    """
    id_municipio = int(id_municipio)
    df = _normalizar_bairros(registros)

    with conexao(db_path) as con:
        if df.empty:
            con.execute(
                "DELETE FROM localidades_bairros WHERE id_municipio = ?", [id_municipio]
            )
        else:
            df.insert(0, "id_municipio", id_municipio)
            con.register("_lote", df)
            try:
                con.execute("""
                    DELETE FROM localidades_bairros
                    WHERE id_municipio = ?
                      AND nome NOT IN (SELECT nome FROM _lote)
                """, [id_municipio])
                con.execute("""
                    INSERT OR REPLACE INTO localidades_bairros (id_municipio, nome, id_distrito)
                    SELECT id_municipio, nome, id_distrito FROM _lote
                """)
            finally:
                con.unregister("_lote")

        con.execute("""
            UPDATE localidades_municipios
            SET bairros_fonte = ?, bairros_atualizado_em = ?
            WHERE id_municipio = ?
        """, [fonte, datetime.now(), id_municipio])
    return len(df)


def salvar_distritos_bulk(distritos, min_bairros=3, db_path=None):
    """Grava todos os distritos do IBGE de uma vez (sincronização completa).

    É aditivo (INSERT OR REPLACE por id_municipio+nome): não apaga bairros que já
    existem, para não destruir listas complementadas pelo OpenStreetMap.

    Marca como 'ibge' apenas os municípios com pelo menos `min_bairros` distritos
    úteis (ou seja, desconsiderando o distrito que tem o mesmo nome da cidade).
    Os demais continuam sem fonte definida e serão complementados via Overpass
    na primeira consulta.
    """
    df = pd.DataFrame(list(distritos), columns=["id_municipio", "nome", "id_distrito"])
    df = df.dropna(subset=["id_municipio", "nome"]).drop_duplicates(["id_municipio", "nome"])
    df["id_distrito"] = df["id_distrito"].astype("Int64")

    with conexao(db_path) as con:
        _inserir_lote(con, df, """
            INSERT OR REPLACE INTO localidades_bairros (id_municipio, nome, id_distrito)
            SELECT id_municipio, nome, id_distrito FROM _lote
        """)
        con.execute("DROP TABLE IF EXISTS _cobertura")
        con.execute("""
            CREATE TEMP TABLE _cobertura AS
            SELECT b.id_municipio
            FROM localidades_bairros b
            JOIN localidades_municipios m ON m.id_municipio = b.id_municipio
            WHERE lower(b.nome) <> lower(m.nome)
            GROUP BY b.id_municipio
            HAVING COUNT(*) >= ?
        """, [int(min_bairros)])
        con.execute("""
            UPDATE localidades_municipios
            SET bairros_fonte = ?, bairros_atualizado_em = ?
            WHERE bairros_fonte IS NULL
              AND id_municipio IN (SELECT id_municipio FROM _cobertura)
        """, [FONTE_IBGE, datetime.now()])
        con.execute("DROP TABLE IF EXISTS _cobertura")
    return len(df)


def estatisticas(db_path=None):
    with conexao(db_path) as con:
        estados = _ler(con, "SELECT COUNT(*) FROM localidades_estados").fetchone()[0]
        municipios = _ler(con, "SELECT COUNT(*) FROM localidades_municipios").fetchone()[0]
        bairros = _ler(con, "SELECT COUNT(*) FROM localidades_bairros").fetchone()[0]
        prontas = _ler(con, """
            SELECT COUNT(*) FROM localidades_municipios WHERE bairros_fonte IS NOT NULL
        """).fetchone()[0]
    return {
        "estados": estados,
        "municipios": municipios,
        "bairros": bairros,
        "cidades_prontas": prontas,
    }
