# src/backend.py
"""Camada de acesso a dados independente do banco (PostgreSQL ou DuckDB).

Centraliza as diferenças entre os dois backends:
- conexão
- placeholder de parâmetro (`?` no DuckDB, `%s` no PostgreSQL)
- leitura para DataFrame / tupla
- bulk upsert (multi-row VALUES)

Os módulos `database.py`, `localidades_db.py` e `schema.py` usam apenas as
funções daqui — nunca `duckdb`/`psycopg2` diretamente.
"""
import os
from urllib.parse import unquote, urlparse

import duckdb
import numpy as np
import pandas as pd
import psycopg2

from src.config import (
    DB_ENGINE,
    DATABASE_URL,
    DUCKDB_PATH,
    DB_HOST,
    DB_PORT,
    DB_NAME,
    DB_USER,
    DB_PASSWORD,
)

IS_DUCKDB = DB_ENGINE == "duckdb"


def ph():
    """Placeholder de parâmetro do backend atual (`?` ou `%s`)."""
    return "?" if IS_DUCKDB else "%s"


def conectar():
    """Abre uma conexão com o backend configurado."""
    if IS_DUCKDB:
        diretorio = os.path.dirname(DUCKDB_PATH)
        if diretorio:
            os.makedirs(diretorio, exist_ok=True)
        return duckdb.connect(DUCKDB_PATH)

    if DATABASE_URL:
        parsed = urlparse(DATABASE_URL)
        return psycopg2.connect(
            host=parsed.hostname,
            port=parsed.port or 5432,
            dbname=(parsed.path or "").lstrip("/") or None,
            user=unquote(parsed.username) if parsed.username else None,
            password=unquote(parsed.password) if parsed.password else "",
            connect_timeout=15,
        )

    return psycopg2.connect(
        host=DB_HOST,
        port=DB_PORT,
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD,
        connect_timeout=15,
    )


def commit(conn):
    """Confirma a transação (no-op no DuckDB, que faz autocommit)."""
    if not IS_DUCKDB:
        conn.commit()


def close(conn):
    conn.close()


def execute(conn, sql, params=None):
    """Executa SQL e devolve cursor/relação (o chamador normalmente ignora)."""
    params = params or []
    if IS_DUCKDB:
        return conn.execute(sql, params)
    cur = conn.cursor()
    cur.execute(sql, params)
    return cur


def query_df(conn, sql, params=None):
    """Executa uma consulta e devolve um DataFrame."""
    if IS_DUCKDB:
        return conn.execute(sql, params or []).df()
    cur = conn.cursor()
    cur.execute(sql, params or [])
    colunas = [d[0] for d in cur.description]
    return pd.DataFrame(cur.fetchall(), columns=colunas)


def query_one(conn, sql, params=None):
    """Executa uma consulta e devolve a primeira linha (tupla ou None)."""
    if IS_DUCKDB:
        return conn.execute(sql, params or []).fetchone()
    cur = conn.cursor()
    cur.execute(sql, params or [])
    return cur.fetchone()


def query_all(conn, sql, params=None):
    """Executa uma consulta e devolve todas as linhas (lista de tuplas)."""
    if IS_DUCKDB:
        return conn.execute(sql, params or []).fetchall()
    cur = conn.cursor()
    cur.execute(sql, params or [])
    return cur.fetchall()


def _valor(v):
    """Converte NaN/NaT e escalares numpy em tipos nativos do Python."""
    if v is None:
        return None
    try:
        if pd.isna(v):
            return None
    except (TypeError, ValueError):
        pass
    if isinstance(v, np.integer):
        return int(v)
    if isinstance(v, np.floating):
        return float(v)
    if isinstance(v, pd.Timestamp):
        return v.to_pydatetime()
    return v


def df_to_rows(df):
    """Converte um DataFrame em lista de tuplas (com NaN -> None)."""
    colunas = list(df.columns)
    return [
        tuple(_valor(r[c]) for c in colunas)
        for r in df.to_dict("records")
    ]


def bulk_upsert(conn, table, columns, rows, conflict, set_clause):
    """Bulk INSERT ... ON CONFLICT ... DO UPDATE (multi-row VALUES).

    - table: nome da tabela
    - columns: lista de colunas
    - rows: lista de tuplas (uma por linha)
    - conflict: colunas do conflito, ex. "nome, cidade"
    - set_clause: ex. "telefone = excluded.telefone, ..."
      (`excluded` em minúsculas funciona tanto no PostgreSQL quanto no DuckDB)
    """
    if not rows:
        return
    colunas_sql = ", ".join(columns)
    linha = "(" + ", ".join([ph()] * len(columns)) + ")"
    valores = ", ".join([linha] * len(rows))
    sql = (
        f"INSERT INTO {table} ({colunas_sql}) VALUES {valores} "
        f"ON CONFLICT ({conflict}) DO UPDATE SET {set_clause}"
    )
    params = [v for row in rows for v in row]
    execute(conn, sql, params)
