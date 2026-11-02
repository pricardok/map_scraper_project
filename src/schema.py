# src/schema.py
"""Criação e população do schema do banco (setup inicial + migração).

Suporta PostgreSQL e DuckDB (definido por `DB_ENGINE` no `.env`). Separação de
responsabilidades:
- `database.py` / `localidades_db.py` apenas CONECTAM e operam sobre um schema
  já existente.
- Este módulo CRIA as tabelas/sequences e POPULA os templates. Rode uma vez ao
  iniciar do zero (ou após mudar de banco):

      python src/schema.py

É idempotente: pode rodar de novo sem perder dados.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src import backend
from src.config import DB_ENGINE

# Template padrão de WhatsApp, usado para popular a tabela de templates.
# Segmento indica o nicho para o qual a mensagem foi criada (ex.: barbearias).
# O markdown (**negrito**) é limpo antes do envio real no whatsapp.py.
TEMPLATE_AGRUPAMENTO_PADRAO = """Opa, tudo certo?

Conhece o **Agendamento Já**? É uma plataforma 100% online para deixar sua agenda no piloto automático e acabar com a dor de cabeça de gerenciar horários pelo WhatsApp.

Com planos a partir de **R$ 29,90** no nosso aplicativo você consegue:

• Personalizar com a identidade da sua marca
• Lembretes automatizados via Whatsapp
• Divulgação de horários automatizadas
• Controle de faturamento
• Pagamentos antecipados

**Conheça nossa proposta**: https://agendamentoja.com/
**Acompanhe nosso dia a dia**: https://www.instagram.com/agendamentoja_

Quer ver uma demonstração rápida de como funciona na prática para o seu tipo de serviço? É só me avisar!"""

# Segmento (nicho) padrão do template acima.
TEMPLATE_SEGMENTO_PADRAO = "barbearias"


def _schema_duckdb(conn):
    """Schema do DuckDB local (ids via sequences; templates com id fixo)."""
    conn.execute("CREATE SEQUENCE IF NOT EXISTS seq_leads_id")
    conn.execute("CREATE SEQUENCE IF NOT EXISTS seq_whatsapp_envios_log_id")

    conn.execute("""
        CREATE TABLE IF NOT EXISTS leads (
            lead_id INTEGER DEFAULT nextval('seq_leads_id'),
            nome VARCHAR,
            telefone VARCHAR,
            tipo_telefone VARCHAR,
            whatsapp_link VARCHAR,
            instagram VARCHAR,
            site VARCHAR,
            bairro VARCHAR,
            cidade VARCHAR,
            estado VARCHAR,
            nicho VARCHAR,
            status VARCHAR DEFAULT 'ativo',
            data_extracao TIMESTAMP,
            data_envio_whatsapp TIMESTAMP,
            status_whatsapp VARCHAR DEFAULT 'pendente',
            chat_id_waha VARCHAR,
            PRIMARY KEY (lead_id),
            UNIQUE (nome, cidade)
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS templates_whatsapp (
            id INTEGER PRIMARY KEY,
            mensagem VARCHAR,
            descricao VARCHAR,
            segmento VARCHAR,
            ativo BOOLEAN DEFAULT TRUE
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS whatsapp_envios_log (
            id INTEGER DEFAULT nextval('seq_whatsapp_envios_log_id'),
            lead_id INTEGER,
            nome VARCHAR,
            cidade VARCHAR,
            telefone VARCHAR,
            telefone_normalizado VARCHAR,
            chat_id VARCHAR,
            status VARCHAR,
            mensagem VARCHAR,
            payload VARCHAR,
            erro VARCHAR,
            data_envio TIMESTAMP
        )
    """)
    # Contagem do teto diário de envios filtra por data_envio.
    conn.execute("""
        CREATE INDEX IF NOT EXISTS idx_whatsapp_envios_log_data
        ON whatsapp_envios_log (data_envio)
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS localidades_estados (
            uf VARCHAR PRIMARY KEY,
            nome VARCHAR NOT NULL
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS localidades_municipios (
            id_municipio BIGINT PRIMARY KEY,
            nome VARCHAR NOT NULL,
            uf VARCHAR NOT NULL,
            bairros_fonte VARCHAR,
            bairros_atualizado_em TIMESTAMP
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS localidades_bairros (
            id_municipio BIGINT NOT NULL,
            nome VARCHAR NOT NULL,
            id_distrito BIGINT,
            PRIMARY KEY (id_municipio, nome)
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS coleta_progresso (
            nicho VARCHAR NOT NULL,
            uf VARCHAR NOT NULL,
            cidade VARCHAR NOT NULL,
            status VARCHAR NOT NULL DEFAULT 'pendente',
            termos_total INTEGER,
            leads_total INTEGER,
            tentativas INTEGER DEFAULT 0,
            erro VARCHAR,
            iniciado_em TIMESTAMP,
            atualizado_em TIMESTAMP,
            concluido_em TIMESTAMP,
            PRIMARY KEY (nicho, uf, cidade)
        )
    """)

    # Seed com id fixo (o templates no DuckDB não tem auto-incremento).
    conn.execute("""
        INSERT INTO templates_whatsapp (id, mensagem, descricao, segmento, ativo)
        SELECT 1, ?, 'Apresentação Agendamento Já', ?, TRUE
        WHERE NOT EXISTS (SELECT 1 FROM templates_whatsapp WHERE id = 1)
    """, [TEMPLATE_AGRUPAMENTO_PADRAO, TEMPLATE_SEGMENTO_PADRAO])


def _schema_postgres(conn):
    """Schema do PostgreSQL (ids identity; migração da tabela `leads`)."""
    from psycopg2 import sql

    cur = conn.cursor()
    cur.execute("CREATE SEQUENCE IF NOT EXISTS seq_leads_id")

    cur.execute("""
        CREATE TABLE IF NOT EXISTS leads (
            lead_id INTEGER NOT NULL DEFAULT nextval('seq_leads_id'),
            nome TEXT,
            telefone TEXT,
            tipo_telefone TEXT,
            whatsapp_link TEXT,
            instagram TEXT,
            site TEXT,
            bairro TEXT,
            cidade TEXT,
            estado TEXT,
            nicho TEXT,
            status TEXT DEFAULT 'ativo',
            data_extracao TIMESTAMP,
            data_envio_whatsapp TIMESTAMP,
            status_whatsapp TEXT DEFAULT 'pendente',
            chat_id_waha TEXT,
            PRIMARY KEY (lead_id),
            UNIQUE (nome, cidade)
        )
    """)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS templates_whatsapp (
            id INTEGER GENERATED BY DEFAULT AS IDENTITY PRIMARY KEY,
            mensagem TEXT,
            descricao TEXT,
            segmento TEXT,
            ativo BOOLEAN DEFAULT TRUE
        )
    """)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS whatsapp_envios_log (
            id INTEGER GENERATED BY DEFAULT AS IDENTITY PRIMARY KEY,
            lead_id INTEGER,
            nome TEXT,
            cidade TEXT,
            telefone TEXT,
            telefone_normalizado TEXT,
            chat_id TEXT,
            status TEXT,
            mensagem TEXT,
            payload TEXT,
            erro TEXT,
            data_envio TIMESTAMP
        )
    """)
    # Contagem do teto diário de envios filtra por data_envio.
    cur.execute("""
        CREATE INDEX IF NOT EXISTS idx_whatsapp_envios_log_data
        ON whatsapp_envios_log (data_envio)
    """)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS localidades_estados (
            uf TEXT PRIMARY KEY,
            nome TEXT NOT NULL
        )
    """)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS localidades_municipios (
            id_municipio BIGINT PRIMARY KEY,
            nome TEXT NOT NULL,
            uf TEXT NOT NULL,
            bairros_fonte TEXT,
            bairros_atualizado_em TIMESTAMP
        )
    """)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS localidades_bairros (
            id_municipio BIGINT NOT NULL,
            nome TEXT NOT NULL,
            id_distrito BIGINT,
            PRIMARY KEY (id_municipio, nome)
        )
    """)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS coleta_progresso (
            nicho TEXT NOT NULL,
            uf TEXT NOT NULL,
            cidade TEXT NOT NULL,
            status TEXT NOT NULL DEFAULT 'pendente',
            termos_total INTEGER,
            leads_total INTEGER,
            tentativas INTEGER DEFAULT 0,
            erro TEXT,
            iniciado_em TIMESTAMP,
            atualizado_em TIMESTAMP,
            concluido_em TIMESTAMP,
            PRIMARY KEY (nicho, uf, cidade)
        )
    """)

    # Migração do gap conhecido: leads sem PK/default no lead_id (banco antigo).
    cur.execute("ALTER TABLE leads ALTER COLUMN lead_id SET DEFAULT nextval('seq_leads_id')")

    cur.execute("""
        SELECT 1 FROM information_schema.table_constraints
        WHERE table_schema = 'public' AND table_name = 'leads'
          AND constraint_name = 'leads_pkey'
    """)
    if not cur.fetchone():
        cur.execute("ALTER TABLE leads ADD CONSTRAINT leads_pkey PRIMARY KEY (lead_id)")

    cur.execute("""
        SELECT 1 FROM information_schema.table_constraints
        WHERE table_schema = 'public' AND table_name = 'leads'
          AND constraint_name = 'leads_nome_cidade_key'
    """)
    if not cur.fetchone():
        cur.execute("ALTER TABLE leads ADD CONSTRAINT leads_nome_cidade_key UNIQUE (nome, cidade)")

    cur.execute("""
        SELECT setval('seq_leads_id',
            GREATEST((SELECT COALESCE(MAX(lead_id), 0) + 1 FROM leads), 1), false)
    """)

    # Seed sem informar id (coluna IDENTITY gera sozinha).
    cur.execute("""
        INSERT INTO templates_whatsapp (mensagem, descricao, segmento, ativo)
        SELECT %s, 'Apresentação Agendamento Já', %s, TRUE
        WHERE NOT EXISTS (SELECT 1 FROM templates_whatsapp)
    """, [TEMPLATE_AGRUPAMENTO_PADRAO, TEMPLATE_SEGMENTO_PADRAO])


def inicializar_schema(conn):
    """Cria sequences, tabelas, corrige schema antigo e popula os templates."""
    if backend.IS_DUCKDB:
        _schema_duckdb(conn)
    else:
        _schema_postgres(conn)
    backend.commit(conn)


def main():
    conn = backend.conectar()
    try:
        inicializar_schema(conn)
    finally:
        backend.close(conn)
    print(f"Schema inicializado ({DB_ENGINE}).")


if __name__ == "__main__":
    main()
