# src/config.py
"""Carregamento centralizado do arquivo .env, leitura de flags e conexão com o banco.

Todos os módulos importam este arquivo, então o `.env` é lido uma única vez
por processo, antes de qualquer constante de configuração ser calculada.
"""
import os

PROJETO_RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CAMINHO_ENV = os.path.join(PROJETO_RAIZ, ".env")


def carregar_env(caminho=None):
    """Carrega variáveis de um arquivo .env (formato CHAVE=VALOR).

    Não sobrescreve variáveis que já existem no ambiente. Ignora linhas em
    branco, comentários (#) e valores entre aspas.
    """
    caminho = caminho or CAMINHO_ENV
    if not os.path.isfile(caminho):
        return

    with open(caminho, "r", encoding="utf-8-sig") as arquivo:
        for linha in arquivo:
            linha = linha.strip()
            if not linha or linha.startswith("#") or "=" not in linha:
                continue
            chave, _, valor = linha.partition("=")
            chave = chave.strip()
            valor = valor.strip().strip('"').strip("'")
            if chave and chave not in os.environ:
                os.environ[chave] = valor


def str_para_bool(valor, padrao=False):
    """Converte strings comuns de booleano ('true', '1', 'sim', 's', 'yes') em bool."""
    if valor is None:
        return padrao
    return str(valor).strip().lower() in ("1", "true", "yes", "s", "sim", "on")


def env_int(nome, padrao):
    """Lê uma variável de ambiente inteira, com fallback para o padrão."""
    valor = os.environ.get(nome, "").strip()
    if not valor:
        return padrao
    try:
        return int(float(valor))
    except ValueError:
        return padrao


# Lido no import: qualquer módulo que importe `src.config` já tem o .env aplicado.
carregar_env()

# ---------------------------------------------------------------------------
# Banco de dados — engine independente (PostgreSQL ou DuckDB)
# ---------------------------------------------------------------------------
# Escolha do backend:
#   DB_ENGINE=postgres  -> PostgreSQL (DATABASE_URL ou DB_*)
#   DB_ENGINE=duckdb    -> DuckDB local (DUCKDB_PATH)
#
# Se DB_ENGINE não for definido, a inferência é:
#   DUCKDB_PATH  definido -> duckdb
#   DATABASE_URL definido -> postgres
#   nenhum dos dois       -> duckdb (padrão local/offline)
DATABASE_URL = os.environ.get("DATABASE_URL", "")
DUCKDB_PATH = os.environ.get("DUCKDB_PATH", "data/leads.duckdb")

DB_ENGINE = os.environ.get("DB_ENGINE", "").strip().lower()
if DB_ENGINE not in ("postgres", "duckdb"):
    if os.environ.get("DUCKDB_PATH"):
        DB_ENGINE = "duckdb"
    elif os.environ.get("DATABASE_URL"):
        DB_ENGINE = "postgres"
    else:
        DB_ENGINE = "duckdb"

# Configuração do PostgreSQL (usada apenas quando DB_ENGINE=postgres).
DB_HOST = os.environ.get("DB_HOST", "localhost")
DB_PORT = env_int("DB_PORT", 5432)
DB_NAME = os.environ.get("DB_NAME", "leads_db")
DB_USER = os.environ.get("DB_USER", "leads_app")
DB_PASSWORD = os.environ.get("DB_PASSWORD", "")
