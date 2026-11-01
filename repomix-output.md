This file is a merged representation of the entire codebase, combined into a single document by Repomix.
The content has been processed where line numbers have been added.

# File Summary

## Purpose
This file contains a packed representation of the entire repository's contents.
It is designed to be easily consumable by AI systems for analysis, code review,
or other automated processes.

## File Format
The content is organized as follows:
1. This summary section
2. Repository information
3. Directory structure
4. Repository files (if enabled)
5. Multiple file entries, each consisting of:
  a. A header with the file path (## File: path/to/file)
  b. The full contents of the file in a code block

## Usage Guidelines
- This file should be treated as read-only. Any changes should be made to the
  original repository files, not this packed version.
- When processing this file, use the file path to distinguish
  between different files in the repository.
- Be aware that this file may contain sensitive information. Handle it with
  the same level of security as you would the original repository.

- Pay special attention to the Repository Instruction. These contain important context and guidelines specific to this project.

## Notes
- Some files may have been excluded based on .gitignore rules and Repomix's configuration
- Binary files are not included in this packed representation. Please refer to the Repository Structure section for a complete list of file paths, including binary files
- Files matching patterns in .gitignore are excluded
- Files matching default ignore patterns are excluded
- Line numbers have been added to the beginning of each line
- Files are sorted by Git change count (files with more changes are at the bottom)
- Git diffs from the worktree and staged changes are included

# Directory Structure
``````
data/
  leads.duckdb
memory/
  00-resumo-projeto.md
  01-arquitetura-e-modulos.md
  02-decisoes-e-armadilhas.md
  03-historico-de-mudancas.md
  04-como-contribuir.md
  05-plano-coleta-nacional-docker.md
  README.md
src/
  __init__.py
  backend.py
  coleta_auto.py
  config.py
  database.py
  localidades_db.py
  locations.py
  main.py
  schema.py
  scraper.py
  utils.py
  whatsapp.py
.dockerignore
.env.example
.gitignore
.gitkeep
.repomixignore
docker-compose.yml
Dockerfile
map_scraper.zip
README.md
repomix-instrucao.md
repomix.config.json
requirements.txt
``````

# Files

## File: src/backend.py
``````python
  1: # src/backend.py
  2: """Camada de acesso a dados independente do banco (PostgreSQL ou DuckDB).
  3: 
  4: Centraliza as diferenças entre os dois backends:
  5: - conexão
  6: - placeholder de parâmetro (`?` no DuckDB, `%s` no PostgreSQL)
  7: - leitura para DataFrame / tupla
  8: - bulk upsert (multi-row VALUES)
  9: 
 10: Os módulos `database.py`, `localidades_db.py` e `schema.py` usam apenas as
 11: funções daqui — nunca `duckdb`/`psycopg2` diretamente.
 12: """
 13: import os
 14: from urllib.parse import unquote, urlparse
 15: 
 16: import duckdb
 17: import numpy as np
 18: import pandas as pd
 19: import psycopg2
 20: 
 21: from src.config import (
 22:     DB_ENGINE,
 23:     DATABASE_URL,
 24:     DUCKDB_PATH,
 25:     DB_HOST,
 26:     DB_PORT,
 27:     DB_NAME,
 28:     DB_USER,
 29:     DB_PASSWORD,
 30: )
 31: 
 32: IS_DUCKDB = DB_ENGINE == "duckdb"
 33: 
 34: 
 35: def ph():
 36:     """Placeholder de parâmetro do backend atual (`?` ou `%s`)."""
 37:     return "?" if IS_DUCKDB else "%s"
 38: 
 39: 
 40: def conectar():
 41:     """Abre uma conexão com o backend configurado."""
 42:     if IS_DUCKDB:
 43:         diretorio = os.path.dirname(DUCKDB_PATH)
 44:         if diretorio:
 45:             os.makedirs(diretorio, exist_ok=True)
 46:         return duckdb.connect(DUCKDB_PATH)
 47: 
 48:     if DATABASE_URL:
 49:         parsed = urlparse(DATABASE_URL)
 50:         return psycopg2.connect(
 51:             host=parsed.hostname,
 52:             port=parsed.port or 5432,
 53:             dbname=(parsed.path or "").lstrip("/") or None,
 54:             user=unquote(parsed.username) if parsed.username else None,
 55:             password=unquote(parsed.password) if parsed.password else "",
 56:             connect_timeout=15,
 57:         )
 58: 
 59:     return psycopg2.connect(
 60:         host=DB_HOST,
 61:         port=DB_PORT,
 62:         dbname=DB_NAME,
 63:         user=DB_USER,
 64:         password=DB_PASSWORD,
 65:         connect_timeout=15,
 66:     )
 67: 
 68: 
 69: def commit(conn):
 70:     """Confirma a transação (no-op no DuckDB, que faz autocommit)."""
 71:     if not IS_DUCKDB:
 72:         conn.commit()
 73: 
 74: 
 75: def close(conn):
 76:     conn.close()
 77: 
 78: 
 79: def execute(conn, sql, params=None):
 80:     """Executa SQL e devolve cursor/relação (o chamador normalmente ignora)."""
 81:     params = params or []
 82:     if IS_DUCKDB:
 83:         return conn.execute(sql, params)
 84:     cur = conn.cursor()
 85:     cur.execute(sql, params)
 86:     return cur
 87: 
 88: 
 89: def query_df(conn, sql, params=None):
 90:     """Executa uma consulta e devolve um DataFrame."""
 91:     if IS_DUCKDB:
 92:         return conn.execute(sql, params or []).df()
 93:     cur = conn.cursor()
 94:     cur.execute(sql, params or [])
 95:     colunas = [d[0] for d in cur.description]
 96:     return pd.DataFrame(cur.fetchall(), columns=colunas)
 97: 
 98: 
 99: def query_one(conn, sql, params=None):
100:     """Executa uma consulta e devolve a primeira linha (tupla ou None)."""
101:     if IS_DUCKDB:
102:         return conn.execute(sql, params or []).fetchone()
103:     cur = conn.cursor()
104:     cur.execute(sql, params or [])
105:     return cur.fetchone()
106: 
107: 
108: def query_all(conn, sql, params=None):
109:     """Executa uma consulta e devolve todas as linhas (lista de tuplas)."""
110:     if IS_DUCKDB:
111:         return conn.execute(sql, params or []).fetchall()
112:     cur = conn.cursor()
113:     cur.execute(sql, params or [])
114:     return cur.fetchall()
115: 
116: 
117: def _valor(v):
118:     """Converte NaN/NaT e escalares numpy em tipos nativos do Python."""
119:     if v is None:
120:         return None
121:     try:
122:         if pd.isna(v):
123:             return None
124:     except (TypeError, ValueError):
125:         pass
126:     if isinstance(v, np.integer):
127:         return int(v)
128:     if isinstance(v, np.floating):
129:         return float(v)
130:     if isinstance(v, pd.Timestamp):
131:         return v.to_pydatetime()
132:     return v
133: 
134: 
135: def df_to_rows(df):
136:     """Converte um DataFrame em lista de tuplas (com NaN -> None)."""
137:     colunas = list(df.columns)
138:     return [
139:         tuple(_valor(r[c]) for c in colunas)
140:         for r in df.to_dict("records")
141:     ]
142: 
143: 
144: def bulk_upsert(conn, table, columns, rows, conflict, set_clause):
145:     """Bulk INSERT ... ON CONFLICT ... DO UPDATE (multi-row VALUES).
146: 
147:     - table: nome da tabela
148:     - columns: lista de colunas
149:     - rows: lista de tuplas (uma por linha)
150:     - conflict: colunas do conflito, ex. "nome, cidade"
151:     - set_clause: ex. "telefone = excluded.telefone, ..."
152:       (`excluded` em minúsculas funciona tanto no PostgreSQL quanto no DuckDB)
153:     """
154:     if not rows:
155:         return
156:     colunas_sql = ", ".join(columns)
157:     linha = "(" + ", ".join([ph()] * len(columns)) + ")"
158:     valores = ", ".join([linha] * len(rows))
159:     sql = (
160:         f"INSERT INTO {table} ({colunas_sql}) VALUES {valores} "
161:         f"ON CONFLICT ({conflict}) DO UPDATE SET {set_clause}"
162:     )
163:     params = [v for row in rows for v in row]
164:     execute(conn, sql, params)
``````

## File: src/coleta_auto.py
``````python
  1: # src/coleta_auto.py
  2: """Coleta automática não-interativa (para rodar em container/servidor).
  3: 
  4: Substitui o menu interativo por um loop contínuo orientado a variáveis de
  5: ambiente — nada de `input()`. Toda a configuração vem do `.env`:
  6: 
  7:     NICHO            nicho a coletar (default: barbearias)
  8:     UFS              lista de UFs separadas por vírgula (vazio = todas)
  9:     MAX_CIDADES      quantas cidades coletar por UF (0 = todas)
 10:     MAX_BAIRROS      quantos bairros usar por cidade (default: 30)
 11:     AQUECER_BAIRROS  pré-resolver bairros da UF antes de coletar (true/false)
 12:     SINCRONIZAR      baixar estados/municípios/distritos do IBGE antes (true/false)
 13:     MOSTRAR_NAVEGADOR abrir o Chromium visível (true/false, default false)
 14:     EXPORTAR_EXCEL   gerar Excel por cidade (true/false, default false)
 15:     LOOP             rodar em loop contínuo (true/false, default false)
 16:     LOOP_PAUSA_SEGUNDOS pausa entre ciclos quando LOOP=true (default 3600)
 17: 
 18: Uso:
 19:     python src/coleta_auto.py
 20: """
 21: import os
 22: import sys
 23: import time
 24: 
 25: sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
 26: 
 27: from src.config import carregar_env, str_para_bool, env_int
 28: from src.locations import (
 29:     obter_estados,
 30:     obter_cidades,
 31:     obter_termos_busca,
 32:     aquecer_bairros_uf,
 33:     sincronizar_base_localidades,
 34: )
 35: from src.scraper import rodar_scraper_multithread
 36: from src.database import LeadDatabase
 37: 
 38: carregar_env()
 39: 
 40: NICHO = os.environ.get("NICHO", "barbearias").strip().lower()
 41: UFS = [u.strip().upper() for u in os.environ.get("UFS", "").split(",") if u.strip()]
 42: MAX_CIDADES = max(0, env_int("MAX_CIDADES", 0))
 43: MAX_BAIRROS = max(1, env_int("MAX_BAIRROS", 30))
 44: AQUECER_BAIRROS = str_para_bool(os.environ.get("AQUECER_BAIRROS"), padrao=False)
 45: SINCRONIZAR = str_para_bool(os.environ.get("SINCRONIZAR"), padrao=False)
 46: MOSTRAR_NAVEGADOR = str_para_bool(os.environ.get("MOSTRAR_NAVEGADOR"), padrao=False)
 47: EXPORTAR_EXCEL = str_para_bool(os.environ.get("EXPORTAR_EXCEL"), padrao=False)
 48: LOOP = str_para_bool(os.environ.get("LOOP"), padrao=False)
 49: LOOP_PAUSA_SEGUNDOS = max(0, env_int("LOOP_PAUSA_SEGUNDOS", 3600))
 50: 
 51: 
 52: def _resolver_ufs():
 53:     """UFs alvo: as da env, ou todas do IBGE se vazio."""
 54:     if UFS:
 55:         return UFS
 56:     df = obter_estados()
 57:     if df.empty:
 58:         return []
 59:     return sorted(df["uf"].tolist())
 60: 
 61: 
 62: def _coletar_cidade(db, cidade, uf):
 63:     print(f"\n=== {cidade}-{uf} ({NICHO}) ===")
 64:     termos = obter_termos_busca(cidade, uf, max_bairros=MAX_BAIRROS)
 65:     df = rodar_scraper_multithread(
 66:         nicho=NICHO,
 67:         cidade=cidade,
 68:         uf=uf,
 69:         termos_lista=termos,
 70:         mostrar_navegador=MOSTRAR_NAVEGADOR,
 71:         save_callback=db.save_leads,
 72:     )
 73:     if EXPORTAR_EXCEL and not df.empty:
 74:         db.export_to_excel(NICHO, cidade)
 75: 
 76: 
 77: def executar_ciclo():
 78:     db = LeadDatabase()
 79:     try:
 80:         if SINCRONIZAR:
 81:             sincronizar_base_localidades()
 82: 
 83:         ufs = _resolver_ufs()
 84:         if not ufs:
 85:             print("Nenhuma UF disponível. Abortando ciclo.")
 86:             return
 87: 
 88:         for uf in ufs:
 89:             cidades = obter_cidades(uf)
 90:             if not cidades:
 91:                 print(f"[{uf}] nenhuma cidade encontrada. Pulando.")
 92:                 continue
 93: 
 94:             if AQUECER_BAIRROS:
 95:                 aquecer_bairros_uf(uf, max_cidades=MAX_CIDADES)
 96: 
 97:             if MAX_CIDADES:
 98:                 cidades = cidades[:MAX_CIDADES]
 99: 
100:             print(f"\n[{uf}] {len(cidades)} cidade(s) a coletar (nicho={NICHO}).")
101:             for cidade in cidades:
102:                 try:
103:                     _coletar_cidade(db, cidade, uf)
104:                 except Exception as e:
105:                     print(f"[{cidade}-{uf}] ERRO: {type(e).__name__}: {e}")
106:     finally:
107:         db.close()
108: 
109: 
110: def main():
111:     print(f"Map Scraper (auto) | nicho={NICHO} | UFs={UFS or 'todas'} | "
112:           f"max_cidades={MAX_CIDADES or 'todas'} | loop={LOOP}")
113:     while True:
114:         executar_ciclo()
115:         if not LOOP:
116:             break
117:         print(f"\nCiclo concluído. Aguardando {LOOP_PAUSA_SEGUNDOS}s para o próximo...")
118:         time.sleep(LOOP_PAUSA_SEGUNDOS)
119: 
120: 
121: if __name__ == "__main__":
122:     main()
``````

## File: src/schema.py
``````python
  1: # src/schema.py
  2: """Criação e população do schema do banco (setup inicial + migração).
  3: 
  4: Suporta PostgreSQL e DuckDB (definido por `DB_ENGINE` no `.env`). Separação de
  5: responsabilidades:
  6: - `database.py` / `localidades_db.py` apenas CONECTAM e operam sobre um schema
  7:   já existente.
  8: - Este módulo CRIA as tabelas/sequences e POPULA os templates. Rode uma vez ao
  9:   iniciar do zero (ou após mudar de banco):
 10: 
 11:       python src/schema.py
 12: 
 13: É idempotente: pode rodar de novo sem perder dados.
 14: """
 15: import os
 16: import sys
 17: 
 18: sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
 19: 
 20: from src import backend
 21: from src.config import DB_ENGINE
 22: 
 23: # Template padrão de WhatsApp, usado para popular a tabela de templates.
 24: # Segmento indica o nicho para o qual a mensagem foi criada (ex.: barbearias).
 25: # O markdown (**negrito**) é limpo antes do envio real no whatsapp.py.
 26: TEMPLATE_AGRUPAMENTO_PADRAO = """Opa, tudo certo?
 27: 
 28: Conhece o **Agendamento Já**? É uma plataforma 100% online para deixar sua agenda no piloto automático e acabar com a dor de cabeça de gerenciar horários pelo WhatsApp.
 29: 
 30: Com planos a partir de **R$ 29,90** no nosso aplicativo você consegue:
 31: 
 32: • Personalizar com a identidade da sua marca
 33: • Lembretes automatizados via Whatsapp
 34: • Divulgação de horários automatizadas
 35: • Controle de faturamento
 36: • Pagamentos antecipados
 37: 
 38: **Conheça nossa proposta**: https://agendamentoja.com/
 39: **Acompanhe nosso dia a dia**: https://www.instagram.com/agendamentoja_
 40: 
 41: Quer ver uma demonstração rápida de como funciona na prática para o seu tipo de serviço? É só me avisar!"""
 42: 
 43: # Segmento (nicho) padrão do template acima.
 44: TEMPLATE_SEGMENTO_PADRAO = "barbearias"
 45: 
 46: 
 47: def _schema_duckdb(conn):
 48:     """Schema do DuckDB local (ids via sequences; templates com id fixo)."""
 49:     conn.execute("CREATE SEQUENCE IF NOT EXISTS seq_leads_id")
 50:     conn.execute("CREATE SEQUENCE IF NOT EXISTS seq_whatsapp_envios_log_id")
 51: 
 52:     conn.execute("""
 53:         CREATE TABLE IF NOT EXISTS leads (
 54:             lead_id INTEGER DEFAULT nextval('seq_leads_id'),
 55:             nome VARCHAR,
 56:             telefone VARCHAR,
 57:             tipo_telefone VARCHAR,
 58:             whatsapp_link VARCHAR,
 59:             instagram VARCHAR,
 60:             site VARCHAR,
 61:             bairro VARCHAR,
 62:             cidade VARCHAR,
 63:             estado VARCHAR,
 64:             nicho VARCHAR,
 65:             status VARCHAR DEFAULT 'ativo',
 66:             data_extracao TIMESTAMP,
 67:             data_envio_whatsapp TIMESTAMP,
 68:             status_whatsapp VARCHAR DEFAULT 'pendente',
 69:             chat_id_waha VARCHAR,
 70:             PRIMARY KEY (lead_id),
 71:             UNIQUE (nome, cidade)
 72:         )
 73:     """)
 74:     conn.execute("""
 75:         CREATE TABLE IF NOT EXISTS templates_whatsapp (
 76:             id INTEGER PRIMARY KEY,
 77:             mensagem VARCHAR,
 78:             descricao VARCHAR,
 79:             segmento VARCHAR,
 80:             ativo BOOLEAN DEFAULT TRUE
 81:         )
 82:     """)
 83:     conn.execute("""
 84:         CREATE TABLE IF NOT EXISTS whatsapp_envios_log (
 85:             id INTEGER DEFAULT nextval('seq_whatsapp_envios_log_id'),
 86:             lead_id INTEGER,
 87:             nome VARCHAR,
 88:             cidade VARCHAR,
 89:             telefone VARCHAR,
 90:             telefone_normalizado VARCHAR,
 91:             chat_id VARCHAR,
 92:             status VARCHAR,
 93:             mensagem VARCHAR,
 94:             payload VARCHAR,
 95:             erro VARCHAR,
 96:             data_envio TIMESTAMP
 97:         )
 98:     """)
 99:     conn.execute("""
100:         CREATE TABLE IF NOT EXISTS localidades_estados (
101:             uf VARCHAR PRIMARY KEY,
102:             nome VARCHAR NOT NULL
103:         )
104:     """)
105:     conn.execute("""
106:         CREATE TABLE IF NOT EXISTS localidades_municipios (
107:             id_municipio BIGINT PRIMARY KEY,
108:             nome VARCHAR NOT NULL,
109:             uf VARCHAR NOT NULL,
110:             bairros_fonte VARCHAR,
111:             bairros_atualizado_em TIMESTAMP
112:         )
113:     """)
114:     conn.execute("""
115:         CREATE TABLE IF NOT EXISTS localidades_bairros (
116:             id_municipio BIGINT NOT NULL,
117:             nome VARCHAR NOT NULL,
118:             id_distrito BIGINT,
119:             PRIMARY KEY (id_municipio, nome)
120:         )
121:     """)
122: 
123:     # Seed com id fixo (o templates no DuckDB não tem auto-incremento).
124:     conn.execute("""
125:         INSERT INTO templates_whatsapp (id, mensagem, descricao, segmento, ativo)
126:         SELECT 1, ?, 'Apresentação Agendamento Já', ?, TRUE
127:         WHERE NOT EXISTS (SELECT 1 FROM templates_whatsapp WHERE id = 1)
128:     """, [TEMPLATE_AGRUPAMENTO_PADRAO, TEMPLATE_SEGMENTO_PADRAO])
129: 
130: 
131: def _schema_postgres(conn):
132:     """Schema do PostgreSQL (ids identity; migração da tabela `leads`)."""
133:     from psycopg2 import sql
134: 
135:     cur = conn.cursor()
136:     cur.execute("CREATE SEQUENCE IF NOT EXISTS seq_leads_id")
137: 
138:     cur.execute("""
139:         CREATE TABLE IF NOT EXISTS leads (
140:             lead_id INTEGER NOT NULL DEFAULT nextval('seq_leads_id'),
141:             nome TEXT,
142:             telefone TEXT,
143:             tipo_telefone TEXT,
144:             whatsapp_link TEXT,
145:             instagram TEXT,
146:             site TEXT,
147:             bairro TEXT,
148:             cidade TEXT,
149:             estado TEXT,
150:             nicho TEXT,
151:             status TEXT DEFAULT 'ativo',
152:             data_extracao TIMESTAMP,
153:             data_envio_whatsapp TIMESTAMP,
154:             status_whatsapp TEXT DEFAULT 'pendente',
155:             chat_id_waha TEXT,
156:             PRIMARY KEY (lead_id),
157:             UNIQUE (nome, cidade)
158:         )
159:     """)
160:     cur.execute("""
161:         CREATE TABLE IF NOT EXISTS templates_whatsapp (
162:             id INTEGER GENERATED BY DEFAULT AS IDENTITY PRIMARY KEY,
163:             mensagem TEXT,
164:             descricao TEXT,
165:             segmento TEXT,
166:             ativo BOOLEAN DEFAULT TRUE
167:         )
168:     """)
169:     cur.execute("""
170:         CREATE TABLE IF NOT EXISTS whatsapp_envios_log (
171:             id INTEGER GENERATED BY DEFAULT AS IDENTITY PRIMARY KEY,
172:             lead_id INTEGER,
173:             nome TEXT,
174:             cidade TEXT,
175:             telefone TEXT,
176:             telefone_normalizado TEXT,
177:             chat_id TEXT,
178:             status TEXT,
179:             mensagem TEXT,
180:             payload TEXT,
181:             erro TEXT,
182:             data_envio TIMESTAMP
183:         )
184:     """)
185:     cur.execute("""
186:         CREATE TABLE IF NOT EXISTS localidades_estados (
187:             uf TEXT PRIMARY KEY,
188:             nome TEXT NOT NULL
189:         )
190:     """)
191:     cur.execute("""
192:         CREATE TABLE IF NOT EXISTS localidades_municipios (
193:             id_municipio BIGINT PRIMARY KEY,
194:             nome TEXT NOT NULL,
195:             uf TEXT NOT NULL,
196:             bairros_fonte TEXT,
197:             bairros_atualizado_em TIMESTAMP
198:         )
199:     """)
200:     cur.execute("""
201:         CREATE TABLE IF NOT EXISTS localidades_bairros (
202:             id_municipio BIGINT NOT NULL,
203:             nome TEXT NOT NULL,
204:             id_distrito BIGINT,
205:             PRIMARY KEY (id_municipio, nome)
206:         )
207:     """)
208: 
209:     # Migração do gap conhecido: leads sem PK/default no lead_id (banco antigo).
210:     cur.execute("ALTER TABLE leads ALTER COLUMN lead_id SET DEFAULT nextval('seq_leads_id')")
211: 
212:     cur.execute("""
213:         SELECT 1 FROM information_schema.table_constraints
214:         WHERE table_schema = 'public' AND table_name = 'leads'
215:           AND constraint_name = 'leads_pkey'
216:     """)
217:     if not cur.fetchone():
218:         cur.execute("ALTER TABLE leads ADD CONSTRAINT leads_pkey PRIMARY KEY (lead_id)")
219: 
220:     cur.execute("""
221:         SELECT 1 FROM information_schema.table_constraints
222:         WHERE table_schema = 'public' AND table_name = 'leads'
223:           AND constraint_name = 'leads_nome_cidade_key'
224:     """)
225:     if not cur.fetchone():
226:         cur.execute("ALTER TABLE leads ADD CONSTRAINT leads_nome_cidade_key UNIQUE (nome, cidade)")
227: 
228:     cur.execute("""
229:         SELECT setval('seq_leads_id',
230:             GREATEST((SELECT COALESCE(MAX(lead_id), 0) + 1 FROM leads), 1), false)
231:     """)
232: 
233:     # Seed sem informar id (coluna IDENTITY gera sozinha).
234:     cur.execute("""
235:         INSERT INTO templates_whatsapp (mensagem, descricao, segmento, ativo)
236:         SELECT %s, 'Apresentação Agendamento Já', %s, TRUE
237:         WHERE NOT EXISTS (SELECT 1 FROM templates_whatsapp)
238:     """, [TEMPLATE_AGRUPAMENTO_PADRAO, TEMPLATE_SEGMENTO_PADRAO])
239: 
240: 
241: def inicializar_schema(conn):
242:     """Cria sequences, tabelas, corrige schema antigo e popula os templates."""
243:     if backend.IS_DUCKDB:
244:         _schema_duckdb(conn)
245:     else:
246:         _schema_postgres(conn)
247:     backend.commit(conn)
248: 
249: 
250: def main():
251:     conn = backend.conectar()
252:     try:
253:         inicializar_schema(conn)
254:     finally:
255:         backend.close(conn)
256:     print(f"Schema inicializado ({DB_ENGINE}).")
257: 
258: 
259: if __name__ == "__main__":
260:     main()
``````

## File: .dockerignore
``````
 1: # Arquivos que NÃO devem ir para o build context / imagem Docker.
 2: .git
 3: .gitignore
 4: .gitkeep
 5: 
 6: # Segredos (o .env é injetado via env_file no compose, não copiado).
 7: .env
 8: 
 9: # Ambiente virtual e cache Python.
10: venv
11: .venv
12: __pycache__
13: *.pyc
14: *.pyo
15: 
16: # Dados locais e saídas (são montados como volume, não copiados).
17: data
18: output
19: *.duckdb
20: *.duckdb.wal
21: *.duckdb.tmp
22: *.xlsx
23: *.csv
24: *.log
25: 
26: # Documentação interna (não necessária na imagem).
27: memory
28: repomix*
29: util
``````

## File: docker-compose.yml
``````yaml
 1: services:
 2:   app:
 3:     build: .
 4:     container_name: map_scraper
 5:     restart: unless-stopped
 6:     env_file:
 7:       - .env
 8:     environment:
 9:       # Configuração do runner (não-interativo). Valores padrão, sobrescreva
10:       # no .env do host ou direto aqui.
11:       NICHO: ${NICHO:-barbearias}
12:       UFS: ${UFS:-}
13:       MAX_CIDADES: ${MAX_CIDADES:-0}
14:       MAX_BAIRROS: ${MAX_BAIRROS:-30}
15:       AQUECER_BAIRROS: ${AQUECER_BAIRROS:-false}
16:       SINCRONIZAR: ${SINCRONIZAR:-false}
17:       MOSTRAR_NAVEGADOR: ${MOSTRAR_NAVEGADOR:-false}
18:       EXPORTAR_EXCEL: ${EXPORTAR_EXCEL:-false}
19:       LOOP: ${LOOP:-false}
20:       LOOP_PAUSA_SEGUNDOS: ${LOOP_PAUSA_SEGUNDOS:-3600}
21:     volumes:
22:       # Banco local (modo DB_ENGINE=duckdb) e Excel gerado.
23:       - ./data:/app/data
24:       - ./output:/app/output
``````

## File: Dockerfile
``````dockerfile
 1: # Dockerfile — Map Scraper
 2: # Imagem para rodar a coleta automática (sem menu) em container.
 3: FROM python:3.11-slim
 4: 
 5: ENV PYTHONUNBUFFERED=1 \
 6:     PYTHONDONTWRITEBYTECODE=1 \
 7:     PIP_NO_CACHE_DIR=1
 8: 
 9: WORKDIR /app
10: 
11: # Dependências de sistema (Playwright instala o resto com --with-deps).
12: RUN apt-get update \
13:     && apt-get install -y --no-install-recommends ca-certificates \
14:     && rm -rf /var/lib/apt/lists/*
15: 
16: # Dependências Python do projeto.
17: COPY requirements.txt .
18: RUN pip install -r requirements.txt
19: 
20: # Chromium do Playwright + bibliotecas de sistema necessárias.
21: RUN playwright install --with-deps chromium
22: 
23: # Código-fonte.
24: COPY src/ ./src/
25: 
26: # Volumes montados no compose: /app/data (DuckDB) e /app/output (Excel).
27: RUN mkdir -p /app/data /app/output
28: 
29: # Runner não-interativo (configuração via variáveis de ambiente).
30: CMD ["python", "src/coleta_auto.py"]
``````

## File: memory/04-como-contribuir.md
``````markdown
 1: # 04 — Como Contribuir: Padrões e Boas Práticas
 2: 
 3: Este documento detalha os padrões de código, estilo e comunicação esperados
 4: para novas contribuições, visando manter a consistência e facilitar a manutenção.
 5: 
 6: ---
 7: 
 8: ## 1. Organização de Código e Nomenclatura
 9: 
10: - **Imports:** Sempre absolutos, começando da raiz `src/`. Ex: `from src.config import ...`.
11: - **Constantes:** `MAIUSCULAS_COM_UNDERLINE`.
12: - **Funções privadas (internas ao módulo):** `_nome_da_funcao_privada` (com underscore inicial).
13: - **Variáveis locais:** `snake_case`.
14: - **Classes:** `CamelCase`.
15: - **Parâmetros de função:** `snake_case`.
16: 
17: ---
18: 
19: ## 2. Logs e Interação com o Usuário
20: 
21: - **Prints de progresso:** Use `print(f"[{area_da_busca}] Mensagem...")`.
22:   O `[área]` (ex: `[Canoas-RS]`, `[Assis Brasil]`) ajuda a identificar qual thread
23:   ou cidade está processando no momento.
24: - **Mensagens de erro:** Inclua `type(e).__name__` e `str(e)[:N]` para facilitar
25:   a depuração em ambientes remotos ou com logs limitados.
26: - **Interação:** Use `input()` para entradas do usuário no console. Evite `print()`
27:   seguido de `input()` em linhas separadas para prompts, a menos que seja intencional.
28: - **Mensagens para o usuário:** Devem ser claras e úteis, preferencialmente
29:   em português (padrão atual do projeto).
30: 
31: ---
32: 
33: ## 3. Variáveis de Ambiente e Configuração
34: 
35: - **Todas as configurações** devem ser lidas do `.env` via `src/config.py`.
36: - **Nunca faça hardcode** de URLs de APIs, chaves, limites, etc.
37: - **Novas variáveis:** Adicione ao `.env.example` com comentários explicativos.
38: - **Semântica:** Use `true`/`false` para booleanos, números para inteiros.
39:   O `src/config.py` já tem helpers para isso (`str_para_bool`, `env_int`).
40: 
41: ---
42: 
43: ## 4. Testes e Validação
44: 
45: - **Testes unitários/de integração:** Idealmente, adicione pequenos scripts de
46:   validação (como os que o modelo Gemini tem feito) para cobrir novas features
47:   ou refatorações.
48: - **DuckDB:** Para testes que não devem tocar no banco real, use um arquivo
49:   DuckDB temporário (`tempfile.gettempdir()`) e defina `localidades_db.DB_PATH_PADRAO`.
50: - **Encoding:** Mantenha os arquivos em **UTF-8 sem BOM**.
51:   Valide a acentuação após edições em lote: procure caracteres de dupla
52:   codificação (por exemplo, `A` com til U+00C3 seguido de símbolo de moeda).
53: 
54: ---
55: 
56: ## 5. Documentação
57: 
58: - **`README.md` (raiz):** Manual do usuário, instalação, execução, fluxo geral.
59: - **`memory/`:** Resumos densos para modelos de IA. **Atualize ao mudar comportamento**.
60:   - `00-resumo-projeto.md`: alto nível.
61:   - `01-arquitetura-e-modulos.md`: detalhe de cada módulo.
62:   - `02-decisoes-e-armadilhas.md`: o "porquê" das decisões, bugs conhecidos.
63:   - `03-historico-de-mudancas.md`: log recente das mudanças importantes.
64: - **Docstrings:** Use docstrings Python para explicar funções e classes.
65: - **Comentários de código:** Breves e pontuais, explicando lógica complexa ou escolhas não óbvias.
``````

## File: src/__init__.py
``````python
1: 
``````

## File: src/config.py
``````python
 1: # src/config.py
 2: """Carregamento centralizado do arquivo .env, leitura de flags e conexão com o banco.
 3: 
 4: Todos os módulos importam este arquivo, então o `.env` é lido uma única vez
 5: por processo, antes de qualquer constante de configuração ser calculada.
 6: """
 7: import os
 8: 
 9: PROJETO_RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
10: CAMINHO_ENV = os.path.join(PROJETO_RAIZ, ".env")
11: 
12: 
13: def carregar_env(caminho=None):
14:     """Carrega variáveis de um arquivo .env (formato CHAVE=VALOR).
15: 
16:     Não sobrescreve variáveis que já existem no ambiente. Ignora linhas em
17:     branco, comentários (#) e valores entre aspas.
18:     """
19:     caminho = caminho or CAMINHO_ENV
20:     if not os.path.isfile(caminho):
21:         return
22: 
23:     with open(caminho, "r", encoding="utf-8-sig") as arquivo:
24:         for linha in arquivo:
25:             linha = linha.strip()
26:             if not linha or linha.startswith("#") or "=" not in linha:
27:                 continue
28:             chave, _, valor = linha.partition("=")
29:             chave = chave.strip()
30:             valor = valor.strip().strip('"').strip("'")
31:             if chave and chave not in os.environ:
32:                 os.environ[chave] = valor
33: 
34: 
35: def str_para_bool(valor, padrao=False):
36:     """Converte strings comuns de booleano ('true', '1', 'sim', 's', 'yes') em bool."""
37:     if valor is None:
38:         return padrao
39:     return str(valor).strip().lower() in ("1", "true", "yes", "s", "sim", "on")
40: 
41: 
42: def env_int(nome, padrao):
43:     """Lê uma variável de ambiente inteira, com fallback para o padrão."""
44:     valor = os.environ.get(nome, "").strip()
45:     if not valor:
46:         return padrao
47:     try:
48:         return int(float(valor))
49:     except ValueError:
50:         return padrao
51: 
52: 
53: # Lido no import: qualquer módulo que importe `src.config` já tem o .env aplicado.
54: carregar_env()
55: 
56: # ---------------------------------------------------------------------------
57: # Banco de dados — engine independente (PostgreSQL ou DuckDB)
58: # ---------------------------------------------------------------------------
59: # Escolha do backend:
60: #   DB_ENGINE=postgres  -> PostgreSQL (DATABASE_URL ou DB_*)
61: #   DB_ENGINE=duckdb    -> DuckDB local (DUCKDB_PATH)
62: #
63: # Se DB_ENGINE não for definido, a inferência é:
64: #   DUCKDB_PATH  definido -> duckdb
65: #   DATABASE_URL definido -> postgres
66: #   nenhum dos dois       -> duckdb (padrão local/offline)
67: DATABASE_URL = os.environ.get("DATABASE_URL", "")
68: DUCKDB_PATH = os.environ.get("DUCKDB_PATH", "data/leads.duckdb")
69: 
70: DB_ENGINE = os.environ.get("DB_ENGINE", "").strip().lower()
71: if DB_ENGINE not in ("postgres", "duckdb"):
72:     if os.environ.get("DUCKDB_PATH"):
73:         DB_ENGINE = "duckdb"
74:     elif os.environ.get("DATABASE_URL"):
75:         DB_ENGINE = "postgres"
76:     else:
77:         DB_ENGINE = "duckdb"
78: 
79: # Configuração do PostgreSQL (usada apenas quando DB_ENGINE=postgres).
80: DB_HOST = os.environ.get("DB_HOST", "localhost")
81: DB_PORT = env_int("DB_PORT", 5432)
82: DB_NAME = os.environ.get("DB_NAME", "leads_db")
83: DB_USER = os.environ.get("DB_USER", "leads_app")
84: DB_PASSWORD = os.environ.get("DB_PASSWORD", "")
``````

## File: src/utils.py
``````python
 1: # src/utils.py
 2: import re
 3: 
 4: def formatar_telefone(telefone_bruto):
 5:     """
 6:     Limpa o telefone, identifica o tipo e gera o link do WhatsApp.
 7:     Retorna: (telefone_limpo, tipo, whatsapp_link)
 8:     """
 9:     if not telefone_bruto:
10:         return "", "Não Informado", ""
11:     
12:     # Remove tudo que não for número
13:     apenas_numeros = re.sub(r'\D', '', str(telefone_bruto))
14:     
15:     # Se o número já vier com DDI (55) e tiver 12 ou 13 dígitos, removemos o 55 
16:     # temporariamente para classificar o tipo corretamente (Fixo/Celular)
17:     if apenas_numeros.startswith('55') and len(apenas_numeros) > 11:
18:         numero_sem_ddi = apenas_numeros[2:]
19:     else:
20:         numero_sem_ddi = apenas_numeros
21: 
22:     # Classificação e formatação do Link
23:     if len(numero_sem_ddi) == 11: # Celular com 9 dígito
24:         tipo = "Celular"
25:         whatsapp_link = f"https://wa.me/55{numero_sem_ddi}"
26:     elif len(numero_sem_ddi) == 10: # Fixo
27:         tipo = "Fixo"
28:         whatsapp_link = f"https://wa.me/55{numero_sem_ddi}"
29:     elif len(apenas_numeros) > 0:
30:         tipo = "Desconhecido"
31:         whatsapp_link = f"https://wa.me/{apenas_numeros}"
32:     else:
33:         return "", "Não Informado", ""
34:         
35:     # Retorna apenas os números na coluna telefone, o tipo e o link pronto
36:     return apenas_numeros, tipo, whatsapp_link
``````

## File: .gitkeep
``````
1: 
``````

## File: requirements.txt
``````
 1: pandas
 2: openpyxl
 3: instagpy
 4: pip-system-certs
 5: playwright
 6: chromium
 7: geopy
 8: duckdb
 9: psycopg2-binary
10: requests
``````

## File: memory/00-resumo-projeto.md
``````markdown
 1: # 00 — Resumo do Projeto
 2: 
 3: **Map Scraper** — ferramenta de prospecção de leads B2B a partir do Google Maps.
 4: 
 5: - **Entrada:** UF + cidade + nicho (ex.: `RS`, `Canoas`, `barbearias`).
 6: - **Processo:** divide a busca por bairros, raspa o Google Maps com Playwright em
 7:   multithread e extrai nome, telefone, Instagram e site.
 8: - **Saída:** leads num banco (PostgreSQL **ou** DuckDB) + Excel em `output/`.
 9: - **Extra:** dispara mensagens de WhatsApp via WAHA para leads já coletados, com
10:   templates reutilizáveis, filtros (número/cidade/nicho), teste de envio, cache
11:   do chatId resolvido (`@lid`/`@c.us`) e **cadência aleatória** anti-bloqueio.
12: 
13: ## Fluxo de alto nível
14: 
15: ```
16: menu (src/main.py)
17:   └─ 1 Coletar    → locations.obter_termos_busca(cidade, uf)
18:                   → scraper.rodar_scraper_multithread(...)
19:                   → database.LeadDatabase.save_leads (UPSERT incremental)
20:                   → database.export_to_excel
21:   └─ 2 WhatsApp   → template ativo → filtros → teste → database.get_leads_para_envio
22:                   → whatsapp.disparar_campanha (WAHA, cadência aleatória)
23:   └─ 3 Sincronizar localidades (IBGE) → locations.sincronizar_base_localidades
24:   └─ 4 Aquecer bairros de uma UF       → locations.aquecer_bairros_uf
25:   └─ 5 Sair
26: ```
27: 
28: ## Stack
29: 
30: | Item | Tecnologia |
31: |---|---|
32: | Linguagem | Python 3.10+ (ambiente: `venv/`) |
33: | Scraping | Playwright (Chromium) + ThreadPoolExecutor |
34: | Banco | **PostgreSQL (externo) ou DuckDB (local)** — via `src/backend.py` |
35: | Dados | Pandas |
36: | Localidades | API IBGE + Nominatim/Overpass (OpenStreetMap) |
37: | WhatsApp | WAHA (WhatsApp HTTP API) |
38: | Config | `.env` carregado por `src/config.py` |
39: 
40: ## Estrutura
41: 
42: ```
43: map_scraper_project/
44: ├── data/          leads.duckdb (usado quando DB_ENGINE=duckdb)
45: ├── memory/        esta documentação para IA
46: ├── output/        Excel gerado (ignorado no Git)
47: ├── src/
48: │   ├── config.py          loader do .env + escolha do backend (DB_ENGINE)
49: │   ├── backend.py         abstração PostgreSQL/DuckDB (conexão, SQL, bulk upsert)
50: │   ├── database.py        LeadDatabase: leads, templates, log WAHA (via backend)
51: │   ├── localidades_db.py  cache IBGE (via backend)
52: │   ├── locations.py       IBGE + OSM + cache; sync e aquecimento por UF
53: │   ├── scraper.py         Playwright, multithread, anti-captcha
54: │   ├── schema.py          DDL + seed + migração (setup: python src/schema.py)
55: │   ├── utils.py           formatar_telefone → (telefone, tipo, link wa)
56: │   ├── whatsapp.py        envio via WAHA + cadência aleatória
57: │   └── main.py            menu interativo
58: ├── .env / .env.example
59: ├── requirements.txt
60: └── README.md
61: ```
62: 
63: ## Git — o que é versionado
64: 
65: | Versionado | Ignorado |
66: |---|---|
67: | `src/`, `memory/`, `README.md` | `.env` (segredos) |
68: | `.env.example` | `*.xlsx`, `*.csv`, `*.log` |
69: | | `venv/`, `__pycache__/`, `sessions/` |
70: 
71: > `data/leads.duckdb` é o banco local (modo `DB_ENGINE=duckdb`). O banco externo
72: > PostgreSQL (modo `DB_ENGINE=postgres`) fica no servidor e não é versionado.
73: 
74: Comando de sync usado pelo mantenedor (sobrescreve o remoto):
75: 
76: ```powershell
77: git add -A; git commit -m "sync local $(Get-Date -Format 'yyyy-MM-dd HH:mm')"; git push --force-with-lease origin main
78: ```
``````

## File: memory/02-decisoes-e-armadilhas.md
``````markdown
  1: # 02 — Decisões Técnicas e Armadilhas
  2: 
  3: Leia antes de mexer no código. Cada item já custou tempo de depuração.
  4: 
  5: ---
  6: 
  7: ## Banco: PostgreSQL OU DuckDB (via `src/backend.py`)
  8: 
  9: O projeto suporta dois backends, escolhidos por `DB_ENGINE` no `.env`:
 10: 
 11: - `DB_ENGINE=postgres` → banco externo (`DATABASE_URL` ou `DB_*`).
 12: - `DB_ENGINE=duckdb` → arquivo local (`DUCKDB_PATH`, default `data/leads.duckdb`).
 13: 
 14: **Regra de ouro:** nenhum módulo além de `src/backend.py` importa `duckdb` ou
 15: `psycopg2`. Todo acesso passa por `backend.execute/query_df/query_all/bulk_upsert`.
 16: - Placeholder de parâmetro: use `backend.ph()` (`?` no DuckDB, `%s` no Postgres),
 17:   NUNCA hardcode.
 18: - `excluded.col` funciona no `ON CONFLICT` dos dois bancos.
 19: - A DDL/seed fica em `schema.py` (roda uma vez: `python src/schema.py`).
 20: 
 21: ### Armadilha do DuckDB: um processo por arquivo
 22: 
 23: **O `data/leads.duckdb` só pode ser aberto por UM processo.** Não existe
 24: "read-only compartilhado" — até `duckdb.connect(..., read_only=True)` falha:
 25: 
 26: ```
 27: IO Error: Cannot open file "...data\leads.duckdb":
 28: O arquivo já está sendo usado por outro processo.
 29: ```
 30: 
 31: Causas mais comuns: **DBeaver conectado**, scraper rodando, notebook aberto.
 32: 
 33: Consequências:
 34: - `localidades_db` abre/fecha a conexão a cada operação (não mantém aberto).
 35: - `LeadDatabase` mantém aberto durante o scraping — **não** abra outra conexão
 36:   persistente no mesmo processo.
 37: - `CacheIndisponivel` degrada com aviso em vez de quebrar.
 38: 
 39: ### Armadilha do PostgreSQL: senha com `@` na URL
 40: 
 41: Na `DATABASE_URL`, caracteres especiais da senha devem ser "percent-encoded"
 42: (`@` → `%40`, `:` → `%3A`, `/` → `%2F`). O `config.py` já decodifica com `unquote`.
 43: Ex.: `aojbfoeub@@@111` → `aojbfoeub%40%40%40111`.
 44: 
 45: ### Armadilha: identidade vs sequence (PostgreSQL)
 46: 
 47: No Postgres, `templates_whatsapp.id`, `whatsapp_envios_log.id` e
 48: `localidades_bairros.id` são colunas **IDENTITY**. O `lead_id` de `leads` é
 49: `integer` com sequence manual (`seq_leads_id`). Não assuma que todas as PKs se
 50: comportam igual.
 51: 
 52: ---
 53: 
 54: ## IBGE: não existe bairro na API de Localidades
 55: 
 56: A API retorna **estados, municípios, distritos e subdistritos**. Nada de bairro.
 57: 
 58: - `distritos` são divisões administrativas; em muitos municípios resumem-se à
 59:   própria sede (mesmo nome da cidade).
 60: - Exemplo real: **Canoas-RS = 1 distrito ("Canoas") e 0 subdistritos**.
 61: - `obter_bairros` descarta o distrito-sede; se sobrarem `< MIN_BAIRROS`,
 62:   complementa com OpenStreetMap.
 63: - Cobertura: ~643 de 5.571 municípios têm distritos suficientes para dispensar OSM.
 64: 
 65: **Não "conserte" isso achando que é bug.** Para bairros oficiais existiria o
 66: CNEFE 2022 (`ftp.ibge.gov.br/.../Censo_Demografico_2022/Arquivos_CNEFE/CSV/UF/`,
 67: coluna `DSC_LOCALIDADE`, ex. `43_RS.zip` ≈ 236 MB) — **decisão do mantenedor:
 68: não implementar por ora**, evoluir aos poucos.
 69: 
 70: ---
 71: 
 72: ## OpenStreetMap: instável por natureza
 73: 
 74: Os espelhos do Overpass e o Nominatim respondem `502`, `400` e `ReadTimeout`
 75: com frequência. Regra de ouro:
 76: 
 77: > Falha de rede **não** significa "cidade sem bairros".
 78: 
 79: Por isso `_consultar_overpass` retorna `None` (serviço fora) em vez de
 80: `{"elements": []}`, e `_descobrir_bairros` devolve `fonte=None` para **não
 81: gravar** nada. A próxima execução tenta de novo. Se gravasse "cidade", o cache
 82: ficaria envenenado para sempre.
 83: 
 84: ---
 85: 
 86: ## Cache: `bairros_fonte` precisa vir na leitura
 87: 
 88: Bug corrigido em 2026-10-29: `ler_municipios()` selecionava só
 89: `id_municipio, nome`, então `_resolver_municipio` devolvia `bairros_fonte=None` e
 90: `obter_bairros` **ia à API mesmo com cache quente**. Agora a query inclui
 91: `uf` e `bairros_fonte`.
 92: 
 93: **Ao criar novas leituras de município, sempre inclua `bairros_fonte`.**
 94: 
 95: ---
 96: 
 97: ## Semântica de escrita (não inverter!)
 98: 
 99: | Função | Comportamento |
100: |---|---|
101: | `salvar_bairros` | **autoritativo** por cidade: remove nomes ausentes **daquela** cidade |
102: | `salvar_distritos_bulk` | **aditivo**: nunca apaga bairros do OSM |
103: | `salvar_municipios` | UPSERT — **preserva** `bairros_fonte`/`bairros_atualizado_em` |
104: 
105: Se `salvar_distritos_bulk` virasse autoritativo, destruiria as listas do
106: OpenStreetMap em toda sincronização.
107: 
108: ---
109: 
110: ## Flags `LOCALIDADES_*` são independentes
111: 
112: `USAR_CACHE` controla **leitura**; `SALVAR` controla **escrita**.
113: 
114: | USAR_CACHE | SALVAR | Efeito |
115: |---|---|---|
116: | true | true | padrão: lê do banco, grava o que faltar |
117: | false | true | ignora o banco, sempre API e regrava |
118: | true | false | lê do banco; o que falta vem da API sem gravar |
119: | false | false | sempre API, banco intocado |
120: 
121: - `SALVAR=false` também desativa a escrita local e os menus **3** e **4**.
122: - As flags são lidas **no import**: mudar o `.env` exige reiniciar o programa.
123: - Com `USAR_CACHE=false`, cada cidade baixa a lista da UF de novo (exceto pela
124:   memoização em memória `_municipios_da_uf`, válida só na execução atual).
125: 
126: ---
127: 
128: ## Cuidados ao editar arquivos (Windows/PowerShell)
129: 
130: - **Nunca** use `Get-Content ... -replace ... | Set-Content` para editar `.py`:
131:   ele reescreve em ANSI e **corrompe acentuação** (dupla codificação / mojibake).
132:   Use o editor (edit) ou grave via Python com `encoding="utf-8"`.
133: - Grave sempre **UTF-8 sem BOM** (BOM quebra a primeira chave do `.env`).
134: - Para testar, use o interpretador da venv: `venv\Scripts\python.exe`.
135:   O `python` global do mantenedor é 3.15 e pode não ter as dependências.
136: - Valide a acentuação após edições em lote: procure caracteres de dupla
137:   codificação (por exemplo, `A` com til U+00C3 seguido de símbolo de moeda).
138: 
139: ---
140: 
141: ## WAHA: chatId `@c.us` vs `@lid` (HTTP 500)
142: 
143: Enviar `POST /api/sendText` com `chatId = 55DDDNUMERO@c.us` **falha com HTTP 500**
144: para números recentes do WhatsApp. Esses números foram migrados para o formato
145: **`@lid`** (hidden user ID).
146: 
147: - Diagnóstico: `GET /api/checkNumberStatus?session=default&phone=55DDD9XXXXXXXX`
148:   responde `{"numberExists": true, "chatId": "143172869029943@lid"}`.
149: - Correção: **sempre resolver o chatId via `checkNumberStatus` antes de enviar**,
150:   em vez de montar `@c.us` na mão (é o que a documentação da WAHA recomenda para
151:   números brasileiros).
152: - O chatId resolvido é **cacheado** na coluna `leads.chat_id_waha` — a consulta
153:   extra só acontece uma vez por lead.
154: - ⚠️ O payload do `sendText` está correto (`{session, chatId, text}` + header
155:   `X-Api-Key`); o erro 500 era **só** o formato do `chatId`, não o endpoint.
156: 
157: ---
158: 
159: ## WAHA: cadência aleatória (anti-bloqueio)
160: 
161: Enviar com pausa fixa (ex.: 15s, 15s, 15s) é fácil de detectar e leva a bloqueio.
162: 
163: - `WAHA_CADENCIA="X:Y"` (ex.: `3:60` = 3 envios/minuto) faz os envios caírem em
164:   **pontos aleatórios** dentro de cada janela de Y segundos → pausas variáveis.
165: - Tem prioridade sobre `WAHA_INTERVALO` (pausa fixa, usada só se `WAHA_CADENCIA`
166:   estiver vazio).
167: - Implementação: `_pausas_cadencia(total, envios_janela, janela)` em `whatsapp.py`.
168: 
169: ---
170: 
171: ## `.env` e Git
172: 
173: - `.env` **é ignorado** (contém `WAHA_API_KEY`). `.env.example` **é versionado**.
174: - Formato: `CHAVE=VALOR`. Comentários só em **linha própria** — comentário na
175:   mesma linha vira parte do valor (`WAHA_LIMITE= # vazio` → `" # vazio"`).
176: - Não use `export`/aspas desnecessárias; o loader tira aspas simples/duplas.
177: - Nunca imprima nem comite segredos.
178: 
179: ---
180: 
181: ## Scraping: seletores frágeis
182: 
183: Dependem do DOM do Google Maps (podem mudar sem aviso):
184: 
185: | Dado | Seletor |
186: |---|---|
187: | lista de resultados | `div[role="feed"]` |
188: | links de perfis | `a[href*="/maps/place/"]` |
189: | nome | `h1` (ignora "Resultados" e vazio) |
190: | endereço | `button[data-item-id="address"]` (`aria-label`) |
191: | telefone | `button[data-item-id^="phone:tel:"]` (`aria-label`) |
192: | site | `a[data-item-id="authority"]` |
193: | Instagram | primeiro `a[href]` contendo `instagram.com` |
194: 
195: Bairro é extraído do endereço: `"Rua X, 123 - Bairro, Cidade - UF"` → parte
196: entre `" - "` e `","`. Se não casar, `"Não Informado"`.
197: 
198: ---
199: 
200: ## Concorrência
201: 
202: - `save_callback` é chamado **na thread principal** (dentro do loop de
203:   `as_completed`), então não há escrita concorrente no banco.
204: - O cooldown anti-captcha usa `_cooldown_lock` + variável global `_cooldown_ate`.
205: - `lock` protege a lista `vistos`/`todos_leads`.
206: 
207: ---
208: 
209: ## Coisas que parecem bug mas não são
210: 
211: - `"IBGE não publica bairros para X"` → cidade com 1 distrito (ver acima).
212: - `"Base local ... sem bairros (fonte: cidade)"` → já tentou, o OSM não tinha nada.
213: - `"LOCALIDADES_SALVAR=false: a base local não será alterada"` → modo leitura.
214: - `"Aviso: base local ... indisponível (arquivo em uso)"` → feche o DBeaver.
``````

## File: .repomixignore
``````
 1: # Add patterns to ignore here, one per line
 2: # Example:
 3: # *.log
 4: # tmp/
 5: 
 6: # Ignorar lixos de teste
 7: output/
 8: util/
 9: 
10: # Ignorar arquivos gerados pelo próprio Repomix
11: repomix-output.md
12: repomix-output.xml
``````

## File: repomix-instrucao.md
``````markdown
 1: # Instruções Mestras para o Assistente de IA (Map Scraper Project)
 2: 
 3: ## 1. Persona e Idioma
 4: - **Idioma:** Processe TODAS as solicitações, explicações, comentários de código e interações estritamente em **Português do Brasil (pt-BR)**.
 5: - **Perfil:** Você é um Engenheiro de Software Sênior, especialista em Python, Web Scraping, Engenharia de Dados e boas práticas de arquitetura. Suas respostas devem ser técnicas, precisas e focadas na escalabilidade e manutenção do código.
 6: 
 7: ## 2. Contexto Obrigatório (Leia ANTES de sugerir código)
 8: - **A pasta `memory/` é a fonte da verdade:** Antes de sugerir qualquer alteração arquitetural, leia os arquivos da pasta `memory/` (especialmente o `01-arquitetura-e-modulos.md` e o `02-decisoes-e-armadilhas.md`). Eles contêm o histórico do "porquê" das decisões e os bugs já solucionados. Não sugira soluções que contradigam o que está documentado lá.
 9: - **Módulos Críticos:** Preste atenção especial ao `src/database.py` (persistência e regras de negócio), `src/scraper.py` (coração do scraping e anti-bloqueio) e `src/locations.py` (cache do IBGE/OSM).
10: 
11: ## 3. Regras de Ouro do Projeto (Armadilhas Conhecidas)
12: - **DuckDB é Single-Process:** O arquivo `data/leads.duckdb` só aceita UMA conexão por vez. Nunca sugira abrir conexões persistentes paralelas no mesmo processo. A classe `LeadDatabase` já gerencia isso.
13: - **Seletores do Google Maps são Frágeis:** O DOM do Google muda. Se for sugerir alterações no `scraper.py`, lembre-se de usar `try/except` e sempre manter o mecanismo de *fallback* e retry.
14: - **Instagram sem API:** A extração do Instagram é feita puramente via DOM (buscando links `href`). Não sugira o uso de bibliotecas instáveis de API do Instagram (como `instagpy`) se não for estritamente necessário, pois o Google Maps já entrega o link.
15: - **Localidades (IBGE vs OSM):** O IBGE não fornece bairros, apenas distritos. O `locations.py` usa o OSM como *fallback*. Se o OSM falhar, o código é projetado para **não gravar** o cache e tentar de novo depois. Mantenha essa lógica.
16: 
17: ## 4. Padrões de Código e Estilo
18: - **Imports:** Sempre use imports absolutos (`from src.modulo import funcao`).
19: - **Configurações:** NUNCA faça hardcode de chaves, URLs ou limites. Tudo deve ser lido do `.env` usando os helpers do `src/config.py`.
20: - **Erros e Logs:** Use `print(f"[{contexto}] Mensagem de erro: {type(e).__name__} - {e}")` para facilitar a depuração. Siga o padrão visual dos logs já existentes.
21: - **Type Hints:** Use anotações de tipo (type hints) do Python sempre que possível para facilitar a leitura e manutenção.
22: - **Arquivos Novos:** Se criar um novo arquivo, siga o padrão de docstrings (explicando o propósito do módulo) e a divisão de responsabilidades (ex: um novo extrator deve ficar separado do banco de dados).
23: 
24: ## 5. O que NÃO fazer
25: - Não sugira refatorações massivas (reescrever o projeto inteiro) sem que seja explicitamente pedido.
26: - Não adicione bibliotecas externas pesadas se a biblioteca padrão do Python ou as dependências atuais (Pandas, Playwright, DuckDB) já resolverem o problema.
27: - Não ignore a estrutura de pastas atual (`src/`, `data/`, `output/`, `memory/`).
``````

## File: repomix.config.json
``````json
 1: {
 2:   "$schema": "https://repomix.com/schemas/latest/schema.json",
 3:   "input": {
 4:     "maxFileSize": 52428800
 5:   },
 6:   "output": {
 7:     "filePath": "repomix-output.md",
 8:     "style": "markdown",
 9:     "filePathStyle": "target-relative",
10:     "parsableStyle": false,
11:     "instructionFilePath": "repomix-instrucao.md",
12:     "fileSummary": true,
13:     "directoryStructure": true,
14:     "files": true,
15:     "removeComments": false,
16:     "removeEmptyLines": false,
17:     "compress": false,
18:     "topFilesLength": 5,
19:     "showLineNumbers": true,
20:     "truncateBase64": false,
21:     "copyToClipboard": false,
22:     "includeFullDirectoryStructure": true,
23:     "tokenCountTree": true,
24:     "git": {
25:       "sortByChanges": true,
26:       "sortByChangesMaxCommits": 100,
27:       "includeDiffs": true,
28:       "includeLogs": false,
29:       "includeLogsCount": 50
30:     }
31:   },
32:   "include": [],
33:   "ignore": {
34:     "useGitignore": true,
35:     "useDotIgnore": true,
36:     "useDefaultPatterns": true,
37:     "customPatterns": []
38:   },
39:   "security": {
40:     "enableSecurityCheck": true
41:   },
42:   "tokenCount": {
43:     "encoding": "o200k_base"
44:   }
45: }
``````

## File: src/localidades_db.py
``````python
  1: # src/localidades_db.py
  2: """Cache (PostgreSQL ou DuckDB) da base de localidades do IBGE.
  3: 
  4: Guarda apenas o essencial, para não inflar o banco:
  5:     localidades_estados     -> uf, nome
  6:     localidades_municipios  -> id_municipio, nome, uf + estado da coleta de bairros
  7:     localidades_bairros     -> id_municipio, nome, id_distrito
  8: 
  9: Cada operação abre e fecha a conexão, então o cache nunca segura uma conexão
 10: aberta durante o scraping.
 11: """
 12: from contextlib import contextmanager
 13: from datetime import datetime
 14: 
 15: import pandas as pd
 16: 
 17: from src import backend
 18: 
 19: # Origem da lista de bairros gravada para uma cidade.
 20: FONTE_IBGE = "ibge"           # distritos do IBGE (quantidade suficiente)
 21: FONTE_OVERPASS = "overpass"   # complementado/obtido via OpenStreetMap
 22: FONTE_CIDADE = "cidade"       # nenhum bairro usado: busca a cidade inteira
 23: 
 24: 
 25: class CacheIndisponivel(Exception):
 26:     """Não foi possível abrir/gravar a base de localidades (ex.: servidor fora)."""
 27: 
 28: 
 29: @contextmanager
 30: def _conexao():
 31:     """Abre uma conexão transacional; commit no fim, rollback em caso de erro."""
 32:     try:
 33:         conn = backend.conectar()
 34:     except Exception as e:
 35:         raise CacheIndisponivel(f"não foi possível conectar ao banco: {e}") from e
 36:     try:
 37:         yield conn
 38:         backend.commit(conn)
 39:     except Exception:
 40:         if not backend.IS_DUCKDB:
 41:             conn.rollback()
 42:         raise
 43:     finally:
 44:         backend.close(conn)
 45: 
 46: 
 47: def _df(conn, sql, params=None):
 48:     return backend.query_df(conn, sql, params)
 49: 
 50: 
 51: def _inserir_upsert(conn, table, columns, df, conflict, set_clause):
 52:     backend.bulk_upsert(
 53:         conn,
 54:         table=table,
 55:         columns=columns,
 56:         rows=backend.df_to_rows(df),
 57:         conflict=conflict,
 58:         set_clause=set_clause,
 59:     )
 60: 
 61: 
 62: def ler_estados():
 63:     with _conexao() as conn:
 64:         df = _df(conn, "SELECT uf, nome FROM localidades_estados ORDER BY nome")
 65:     return df.to_dict("records")
 66: 
 67: 
 68: def salvar_estados(registros):
 69:     df = pd.DataFrame(list(registros), columns=["uf", "nome"]).drop_duplicates("uf")
 70:     with _conexao() as conn:
 71:         _inserir_upsert(conn, "localidades_estados", ["uf", "nome"], df,
 72:                         conflict="uf", set_clause="nome = excluded.nome")
 73:     return len(df)
 74: 
 75: 
 76: def ler_municipios(uf):
 77:     with _conexao() as conn:
 78:         df = _df(conn, """
 79:             SELECT id_municipio, nome, uf, bairros_fonte
 80:             FROM localidades_municipios WHERE uf = %s ORDER BY nome
 81:         """.replace("%s", backend.ph()), [uf])
 82:     return df.to_dict("records")
 83: 
 84: 
 85: def ler_municipios_pendentes(uf):
 86:     """Municípios da UF cujos bairros ainda não foram resolvidos (bairros_fonte nulo)."""
 87:     with _conexao() as conn:
 88:         df = _df(conn, """
 89:             SELECT id_municipio, nome
 90:             FROM localidades_municipios
 91:             WHERE uf = %s AND bairros_fonte IS NULL
 92:             ORDER BY nome
 93:         """.replace("%s", backend.ph()), [uf])
 94:     return df.to_dict("records")
 95: 
 96: 
 97: def salvar_municipios(registros):
 98:     df = pd.DataFrame(list(registros), columns=["id_municipio", "nome", "uf"])
 99:     df = df.dropna(subset=["id_municipio"]).drop_duplicates("id_municipio")
100:     with _conexao() as conn:
101:         # UPSERT preserva bairros_fonte/bairros_atualizado_em já gravados.
102:         _inserir_upsert(conn, "localidades_municipios", ["id_municipio", "nome", "uf"], df,
103:                         conflict="id_municipio",
104:                         set_clause="nome = excluded.nome, uf = excluded.uf")
105:     return len(df)
106: 
107: 
108: def buscar_municipio(cidade, uf):
109:     """Retorna {id_municipio, nome, uf, bairros_fonte} ou None se não estiver na base."""
110:     p = backend.ph()
111:     with _conexao() as conn:
112:         linha = backend.query_one(conn, f"""
113:             SELECT id_municipio, nome, uf, bairros_fonte
114:             FROM localidades_municipios
115:             WHERE uf = {p} AND lower(nome) = lower({p})
116:             LIMIT 1
117:         """, [uf, cidade])
118:     if not linha:
119:         return None
120:     return {
121:         "id_municipio": linha[0],
122:         "nome": linha[1],
123:         "uf": linha[2],
124:         "bairros_fonte": linha[3],
125:     }
126: 
127: 
128: def ler_bairros(id_municipio):
129:     with _conexao() as conn:
130:         df = _df(conn,
131:             "SELECT nome FROM localidades_bairros WHERE id_municipio = %s ORDER BY nome"
132:             .replace("%s", backend.ph()), [int(id_municipio)],
133:         )
134:     return df["nome"].tolist()
135: 
136: 
137: def _normalizar_bairros(registros):
138:     linhas = []
139:     for item in registros or []:
140:         if isinstance(item, dict):
141:             nome = str(item.get("nome") or "").strip()
142:             id_distrito = item.get("id_distrito")
143:         else:
144:             nome = str(item or "").strip()
145:             id_distrito = None
146:         if nome:
147:             linhas.append({"nome": nome, "id_distrito": id_distrito})
148: 
149:     df = pd.DataFrame(linhas, columns=["nome", "id_distrito"])
150:     if df.empty:
151:         return df
152:     df["id_distrito"] = df["id_distrito"].astype("Int64")
153:     return df.drop_duplicates("nome")
154: 
155: 
156: def salvar_bairros(id_municipio, registros, fonte):
157:     """Grava a lista final de bairros de uma cidade e marca a origem da coleta.
158: 
159:     A lista é autoritativa para a cidade: bairros que não estão nela são
160:     removidos (delete da cidade + re-insert), para o cache não acumular nomes
161:     de uma coleta anterior. `fonte` = 'ibge', 'overpass' ou 'cidade'.
162:     """
163:     id_municipio = int(id_municipio)
164:     df = _normalizar_bairros(registros)
165: 
166:     with _conexao() as conn:
167:         p = backend.ph()
168:         if df.empty:
169:             backend.execute(conn, f"DELETE FROM localidades_bairros WHERE id_municipio = {p}",
170:                             [id_municipio])
171:         else:
172:             df.insert(0, "id_municipio", id_municipio)
173:             # Autoritativo por cidade: apaga tudo da cidade e reinsere.
174:             backend.execute(conn, f"DELETE FROM localidades_bairros WHERE id_municipio = {p}",
175:                             [id_municipio])
176:             _inserir_upsert(
177:                 conn, "localidades_bairros", ["id_municipio", "nome", "id_distrito"], df,
178:                 conflict="id_municipio, nome",
179:                 set_clause="id_distrito = excluded.id_distrito",
180:             )
181: 
182:         backend.execute(conn, f"""
183:             UPDATE localidades_municipios
184:             SET bairros_fonte = {p}, bairros_atualizado_em = {p}
185:             WHERE id_municipio = {p}
186:         """, [fonte, datetime.now(), id_municipio])
187:     return len(df)
188: 
189: 
190: def salvar_distritos_bulk(distritos, min_bairros=3):
191:     """Grava todos os distritos do IBGE de uma vez (sincronização completa).
192: 
193:     É aditivo (upsert por id_municipio+nome): não apaga bairros que já existem,
194:     para não destruir listas complementadas pelo OpenStreetMap.
195: 
196:     Marca como 'ibge' apenas os municípios com pelo menos `min_bairros` distritos
197:     úteis (desconsiderando o distrito que tem o mesmo nome da cidade).
198:     """
199:     df = pd.DataFrame(list(distritos), columns=["id_municipio", "nome", "id_distrito"])
200:     df = df.dropna(subset=["id_municipio", "nome"]).drop_duplicates(["id_municipio", "nome"])
201:     df["id_distrito"] = df["id_distrito"].astype("Int64")
202: 
203:     with _conexao() as conn:
204:         p = backend.ph()
205:         _inserir_upsert(
206:             conn, "localidades_bairros", ["id_municipio", "nome", "id_distrito"], df,
207:             conflict="id_municipio, nome",
208:             set_clause="id_distrito = excluded.id_distrito",
209:         )
210:         backend.execute(conn, f"""
211:             UPDATE localidades_municipios
212:             SET bairros_fonte = {p}, bairros_atualizado_em = {p}
213:             WHERE bairros_fonte IS NULL
214:               AND id_municipio IN (
215:                   SELECT b.id_municipio
216:                   FROM localidades_bairros b
217:                   JOIN localidades_municipios mm ON mm.id_municipio = b.id_municipio
218:                   WHERE lower(b.nome) <> lower(mm.nome)
219:                   GROUP BY b.id_municipio
220:                   HAVING COUNT(*) >= {p}
221:               )
222:         """, [FONTE_IBGE, datetime.now(), int(min_bairros)])
223:     return len(df)
224: 
225: 
226: def estatisticas():
227:     with _conexao() as conn:
228:         def _count(sql):
229:             return backend.query_one(conn, sql)[0]
230:         estados = _count("SELECT COUNT(*) FROM localidades_estados")
231:         municipios = _count("SELECT COUNT(*) FROM localidades_municipios")
232:         bairros = _count("SELECT COUNT(*) FROM localidades_bairros")
233:         prontas = _count("SELECT COUNT(*) FROM localidades_municipios WHERE bairros_fonte IS NOT NULL")
234:     return {
235:         "estados": estados,
236:         "municipios": municipios,
237:         "bairros": bairros,
238:         "cidades_prontas": prontas,
239:     }
``````

## File: memory/03-historico-de-mudancas.md
``````markdown
  1: # 03 — Histórico de Mudanças
  2: 
  3: Registro do que mudou, por quê e o que ficou pendente. Mais recente primeiro.
  4: 
  5: ---
  6: 
  7: ## 2026-10-31
  8: 
  9: ### Migração para PostgreSQL + suporte dual (PostgreSQL/DuckDB)
 10: 
 11: - Banco externo PostgreSQL (`vps.agendamentoja.com/leads_db`) + mantido o DuckDB
 12:   local como alternativa offline.
 13: - Novo `src/backend.py`: abstrai conexão, placeholder (`?`/`%s`), leitura
 14:   (DataFrame/tupla) e bulk upsert entre os dois bancos. `database.py`,
 15:   `localidades_db.py` e `schema.py` não importam mais `duckdb`/`psycopg2`.
 16: - `config.py` lê `DB_ENGINE` (postgres|duckdb), `DATABASE_URL` e `DUCKDB_PATH`.
 17:   Inferência: DUCKDB_PATH → duckdb; senão DATABASE_URL → postgres; senão duckdb.
 18: - `schema.py` reescrito para os dois bancos; corrige o gap da tabela `leads`
 19:   (PK `lead_id` + UNIQUE `(nome,cidade)` + default `nextval('seq_leads_id')`).
 20: - `requirements.txt`: readicionado `duckdb` + `psycopg2-binary`.
 21: - `.env`: seção "BANCO DE DADOS — engine independente" com `DATABASE_URL` (senha
 22:   com `@` percent-encoded) e config antiga comentada como referência.
 23: 
 24: ### Cadência aleatória de envio WhatsApp (anti-bloqueio)
 25: 
 26: - Nova `WAHA_CADENCIA="X:Y"` no `.env` (ex.: `3:60` = 3 envios por minuto).
 27: - `whatsapp.py`: `_parse_cadencia` + `_pausas_cadencia` distribuem os envios em
 28:   pontos **aleatórios** dentro de cada janela (pausas variáveis, não fixas).
 29: - Tem prioridade sobre `WAHA_INTERVALO` (fixo). `WAHA_CADENCIA` vazio → usa o fixo.
 30: 
 31: ### Tabela `whatsapp_envios_log` (rastreamento)
 32: 
 33: - Log por envio com `lead_id`, `telefone` (dígitos) e `telefone_normalizado`
 34:   (55DDDNUMERO), `chat_id`, `status`, `mensagem`, `payload`, `erro`, `data_envio`.
 35: - JOIN pronto por `lead_id` ou `telefone`.
 36: 
 37: ---
 38: 
 39: ## 2026-10-30
 40: 
 41: ### Templates de mensagem de WhatsApp (tabela + markdown)
 42: 
 43: - Nova tabela `templates_whatsapp` (`id`, `mensagem`, `descricao`, `ativo`),
 44:   criada e seedada no `LeadDatabase.__init__` (idempotente, `id=1` =
 45:   "Apresentação Agendamento Já").
 46: - `listar_templates_ativos()` retorna só os ativos para o menu de envio.
 47: - `_limpar_markdown_whatsapp` remove `**negrito**` e converte `[rótulo](url)` em
 48:   texto plano antes do envio (o template usa markdown; o WhatsApp não renderiza).
 49: 
 50: ### Menu de envio: template + filtros + teste
 51: 
 52: - `enviar_whatsapp_menu()` agora: escolhe template → aplica filtros → pergunta se
 53:   quer **teste de envio** → confirma e dispara.
 54: - Filtros de envio (menu "FILTROS DE ENVIO"): 0 todos / 1 por número / 2 por
 55:   cidade / 3 por nicho. Número aceita parte e compara só dígitos.
 56: - `testar_envio()`: digita um número com DDD ou escolhe um lead pendente.
 57: - `disparar_campanha` passou a aceitar `leads` (DataFrame já filtrado) — sem isso
 58:   os filtros eram ignorados no disparo (ele reconsultava o banco).
 59: 
 60: ### Correção crítica: chatId `@lid` vs `@c.us` (WAHA)
 61: 
 62: - **Sintoma:** `500 Server Error` no `/api/sendText` para o número do mantenedor.
 63: - **Causa:** número recente usa `@lid`; enviar `@c.us` retorna HTTP 500.
 64: - **Correção:** `_resolver_chatid_waha` consulta `/api/checkNumberStatus` e usa o
 65:   chatId retornado; fallback `@c.us` para números antigos.
 66: - **Cache:** coluna `leads.chat_id_waha` + `salvar_chat_id_waha` — a resolução é
 67:   feita uma única vez por lead (menos chamadas e reenvio mais rápido).
 68: - `data_envio_whatsapp` continua gravada só no sucesso; `status_whatsapp` em
 69:   `enviado`/`falhou`.
 70: 
 71: ---
 72: 
 73: ## 2026-10-29
 74: 
 75: ### Memória do projeto para IA
 76: 
 77: - Criada a pasta `memory/` com documentação densa para reduzir custo de contexto.
 78: - Arquivos: `README.md`, `00-resumo-projeto.md`, `01-arquitetura-e-modulos.md`,
 79:   `02-decisoes-e-armadilhas.md`, `03-historico-de-mudancas.md`,
 80:   `04-como-contribuir.md` (padrões de código, logs, config, testes e docs).
 81: - `README.md` limpo: removido o bloco "env temp:" (dump cru do `.env`) e
 82:   adicionadas as seções 12 (memória para IA) e 13 (observação sobre configuração).
 83: 
 84: ### Correção: cache de bairros ignorado (`bairros_fonte`)
 85: 
 86: - **Sintoma:** com `LOCALIDADES_USAR_CACHE=true` e base populada, a coleta ainda
 87:   consultava IBGE e Overpass.
 88: - **Causa:** `localidades_db.ler_municipios()` não retornava `bairros_fonte`;
 89:   `_resolver_municipio` repassava `None`, então o cache nunca era considerado.
 90: - **Correção:** query passou a trazer `uf` e `bairros_fonte`; o resolver repassa
 91:   o valor real.
 92: - **Teste:** com as funções de rede trocadas por `AssertionError`, os bairros de
 93:   Canoas (fonte `overpass`) e Bento Gonçalves (fonte `ibge`) vieram do banco.
 94: 
 95: ### Nome oficial do município (IBGE) na coleta
 96: 
 97: - `obter_municipio(cidade, uf)` confirma o município e devolve `id_municipio`,
 98:   `nome` oficial e `uf`.
 99: - `filtrar_cidades(cidades, termo)` compara **sem acento e sem caixa**:
100:   `canoas`, `sao leopoldo`, `CHAPECO` funcionam.
101: - `main.coletar_leads()` passa a usar o nome oficial no scraping, no banco e no
102:   nome do Excel, e imprime `Município (IBGE): Canoas-RS | código 4304606`.
103: - Lista de municípios **memoizada** por execução (`_municipios_da_uf`), evitando
104:   rebaixar a lista da UF a cada cidade (principalmente com `SALVAR=false`).
105: 
106: ### Mensagens de bairros mais honestas
107: 
108: - Antes: `IBGE retornou 0 distrito(s) útil(eis)`.
109: - Agora: `IBGE não publica bairros para Canoas-RS: o município tem apenas 1 distrito (a sede).`
110: - Motivo: a API de Localidades do IBGE **não tem bairros** (só distritos).
111: 
112: ### Aquecimento de bairros por UF (menu 4)
113: 
114: - `locations.aquecer_bairros_uf(uf, cidades=None, max_cidades=0, pausa_segundos=None)`.
115: - `localidades_db.ler_municipios_pendentes(uf)` → só `bairros_fonte IS NULL`.
116: - Retoma de onde parou; `Ctrl+C` preserva o que já foi gravado.
117: - Pausa (`AQUECER_PAUSA_SEGUNDOS`, default 2) só quando a cidade usou o OSM.
118: - Falha de rede não grava nada (`falhas` no resumo) e a cidade continua pendente.
119: - Bloqueado quando `LOCALIDADES_SALVAR=false`.
120: - Medido: AC 21 → 18 → 17 pendentes; SP 621 → 616.
121: 
122: ### Flag `LOCALIDADES_SALVAR`
123: 
124: - `false` = somente leitura: nenhuma escrita, **nem criação de tabelas**
125:   (`localidades_db.CRIAR_TABELAS = False`) e menus 3/4 desativados.
126: - Todas as escritas passam por `_salvar()`, que respeita a flag.
127: - Aviso único por execução para não poluir o log.
128: 
129: ### `.env` e `.env.example` comentados
130: 
131: - Cada variável com explicação, faixa de valores e efeito colateral.
132: - Tabela das 4 combinações `USAR_CACHE × SALVAR`.
133: - Regra explícita: comentário só em linha própria.
134: - Valores locais preservados (`USAR_CACHE=false` → depois `true`).
135: 
136: ### Base de localidades offline (IBGE) — menu 3
137: 
138: - Novo `src/localidades_db.py` com tabelas `localidades_estados`,
139:   `localidades_municipios`, `localidades_bairros` no mesmo `leads.duckdb`.
140: - `src/config.py` centraliza o loader do `.env` (antes duplicado no `whatsapp.py`).
141: - `src/locations.py` reescrito: cache → API → grava.
142: - Sync nacional: 27 estados, 5.571 municípios, 10.751 distritos; 643 cidades com
143:   bairros prontos pelo IBGE.
144: - Fallback OSM por cidade, gravado uma única vez.
145: 
146: ### Anti-captcha / bloqueio do Google Maps
147: 
148: - Detecção por URL `/sorry/`, seletores de captcha e textos ("tráfego incomum").
149: - Retry com pausa longa (`CAPTCHA_PAUSA_SEGUNDOS`) e **cooldown global**
150:   (`CAPTCHA_PAUSA_GLOBAL_SEGUNDOS`) entre todas as threads.
151: - Bloqueio persistente → aborta a área e **preserva os leads já extraídos**.
152: - Testado com Playwright real: página normal passa, página de captcha levanta
153:   `BloqueioDetectado` após `CAPTCHA_MAX_TENTATIVAS`.
154: 
155: ### Correção: menu não aparecia
156: 
157: - `src/main.py` definia `menu_interativo()` mas **nunca chamava**.
158: - Adicionado `if __name__ == "__main__": menu_interativo()`.
159: 
160: ### Banco DuckDB versionado
161: 
162: - `data/leads.duckdb` passou a ser versionado no Git.
163: - `.gitignore`: removidos `data/` e `*.duckdb` da lista de ignore; adicionados
164:   `*.duckdb.wal` e `*.duckdb.tmp`.
165: - `*.xlsx`, `*.csv`, `*.log` continuam ignorados (confirmado com
166:   `git check-ignore` e `git ls-files`).
167: - ⚠️ Comitar com o programa aberto sobe o `.duckdb` sem o `.wal` (dados
168:   desatualizados). Fechar antes.
169: 
170: ---
171: 
172: ## Pendências / próximos passos
173: 
174: | Item | Status |
175: |---|---|
176: | Bairros oficiais via CNEFE 2022 | **Não implementar por hora** (decisão do mantenedor) |
177: | Resolução automática de captcha (2Captcha/CapMonster) | Não implementado; hoje pausa e desiste da área |
178: | Enriquecimento de e-mail a partir dos sites | Não iniciado |
179: | Base de bairros offline nacional | Coberto parcialmente pelo IBGE (643 cidades) |
180: 
181: ## Problemas conhecidos (ambiente)
182: 
183: - **DBeaver aberto trava o DuckDB** → cache cai para as APIs.
184: - **Overpass/Nominatim instáveis** (502, timeout) → aquecimento por UF precisa de
185:   paciência e retomadas.
186: - Interprete global do mantenedor é Python 3.15; **usar `venv\Scripts\python.exe`**.
``````

## File: memory/README.md
``````markdown
 1: # memory/ — Memória do Projeto para IAs
 2: 
 3: Esta pasta contém documentação **resumida e densa** sobre o projeto Map Scraper,
 4: escrita para ser lida por modelos de IA antes de alterar código.
 5: 
 6: ## Por que existe
 7: 
 8: Ler esses arquivos curtos daqui custa muito menos tokens do que reler todo o código.
 9: Use esta pasta como **primeira fonte de contexto**.
10: 
11: ## Ordem de leitura recomendada
12: 
13: | # | Arquivo | Conteúdo |
14: |---|---|---|
15: | 1 | [00-resumo-projeto.md](./00-resumo-projeto.md) | O que o projeto faz, stack, estrutura |
16: | 2 | [01-arquitetura-e-modulos.md](./01-arquitetura-e-modulos.md) | Cada módulo, funções principais, fluxos |
17: | 3 | [02-decisoes-e-armadilhas.md](./02-decisoes-e-armadilhas.md) | Decisões técnicas, bugs conhecidos, cuidados |
18: | 4 | [03-historico-de-mudancas.md](./03-historico-de-mudancas.md) | O que mudou recentemente e por quê |
19: | 5 | [04-como-contribuir.md](./04-como-contribuir.md) | Padrões de código, logs, config, testes e documentação |
20: | 6 | [05-plano-coleta-nacional-docker.md](./05-plano-coleta-nacional-docker.md) | **Plano aprovado (não implementado):** banco plugável, fila de jobs, circuit breaker WAHA, Docker |
21: 
22: ## Regras de manutenção
23: 
24: - **Atualize ao mudar comportamento**, não a cada commit.
25: - Mantenha cada arquivo curto (ideal: < 200 linhas). Detalhe fica no código.
26: - Registre o **porquê** das decisões, não só o quê.
27: - Nunca coloque segredos aqui (API keys, tokens). Use `.env`.
28: - Datas no formato `AAAA-MM-DD`.
29: 
30: ## Arquivos que NÃO devem ser duplicados aqui
31: 
32: - `README.md` (raiz) — manual do usuário, instalação, uso.
33: - `.env.example` — valores e comentários de cada variável.
34: 
35: ## Git force
36: - Enviar
37: git add -A; git commit -m "Atualização"; git push --force origin main
38: 
39: 
40: ## git forçado
41: 
42: # Envia
43: git add -A; git commit -m "Melhorias no processo de coletas v3 $(Get-Date -Format 'yyyy-MM-dd HH:mm')"; git push --force-with-lease origin main
44: 
45: # Recebe
46: 
47: git fetch --all; git reset --hard origin/main
``````

## File: src/scraper.py
``````python
  1: # src/scraper.py
  2: from playwright.sync_api import sync_playwright
  3: import time
  4: import random
  5: import urllib.parse
  6: from concurrent.futures import ThreadPoolExecutor, as_completed
  7: import pandas as pd
  8: import threading
  9: from src.config import env_int
 10: from src.utils import formatar_telefone
 11: 
 12: lock = threading.Lock()
 13: 
 14: USER_AGENT = (
 15:     "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
 16:     "AppleWebKit/537.36 (KHTML, like Gecko) "
 17:     "Chrome/124.0.0.0 Safari/537.36"
 18: )
 19: 
 20: MAX_ROLAGENS = 40
 21: MAX_RODADAS_ESTAGNADAS = 3
 22: 
 23: # --- Anti-bloqueio (captcha) -------------------------------------------------
 24: # CAPTCHA_MAX_TENTATIVAS: quantas vezes uma mesma página é tentada antes de
 25: #   abortar a área (1 = nem tenta de novo, só pausa e desiste).
 26: # CAPTCHA_PAUSA_SEGUNDOS: pausa longa feita pela thread que levou o bloqueio.
 27: # CAPTCHA_PAUSA_GLOBAL_SEGUNDOS: pausa compartilhada, aplicada a TODAS as
 28: #   threads assim que uma delas detecta bloqueio (evita que as outras insistam).
 29: CAPTCHA_MAX_TENTATIVAS = max(1, env_int("CAPTCHA_MAX_TENTATIVAS", 2))
 30: CAPTCHA_PAUSA_SEGUNDOS = max(0, env_int("CAPTCHA_PAUSA_SEGUNDOS", 300))
 31: CAPTCHA_PAUSA_GLOBAL_SEGUNDOS = max(0, env_int("CAPTCHA_PAUSA_GLOBAL_SEGUNDOS", 180))
 32: 
 33: _MARCADORES_CAPTCHA = (
 34:     "unusual traffic",
 35:     "tráfego incomum",
 36:     "trafego incomum",
 37:     "não é possível acessar",
 38:     "nao e possivel acessar",
 39:     "our systems have detected",
 40:     "digite os caracteres",
 41:     "não sou um robô",
 42:     "i'm not a robot",
 43: )
 44: 
 45: _SELETORES_BLOQUEIO = (
 46:     'form[action*="sorry"]',
 47:     "#captcha-form",
 48:     "#recaptcha",
 49:     ".g-recaptcha",
 50:     'iframe[src*="recaptcha"]',
 51:     'iframe[src*="hcaptcha"]',
 52: )
 53: 
 54: _cooldown_ate = 0.0
 55: _cooldown_lock = threading.Lock()
 56: 
 57: 
 58: class BloqueioDetectado(Exception):
 59:     """Google Maps devolveu captcha/tela de bloqueio para a busca atual."""
 60: 
 61: 
 62: def _montar_query(nicho, termo_busca, cidade, uf):
 63:     if termo_busca.strip().lower() == cidade.strip().lower():
 64:         return f"{nicho} em {cidade}, {uf}"
 65:     return f"{nicho} em {termo_busca}, {cidade}, {uf}"
 66: 
 67: 
 68: def _pagina_bloqueada(page, checar_texto=True):
 69:     """Detecta captcha / tela de 'tráfego incomum' do Google."""
 70:     try:
 71:         url = (page.url or "").lower()
 72:     except Exception:
 73:         return False
 74:     if "/sorry/" in url:
 75:         return True
 76: 
 77:     try:
 78:         for seletor in _SELETORES_BLOQUEIO:
 79:             if page.query_selector(seletor):
 80:                 return True
 81:     except Exception:
 82:         return False
 83: 
 84:     if not checar_texto:
 85:         return False
 86: 
 87:     try:
 88:         texto = (page.inner_text("body") or "")[:4000].lower()
 89:     except Exception:
 90:         return False
 91:     return any(marcador in texto for marcador in _MARCADORES_CAPTCHA)
 92: 
 93: 
 94: def _marcar_bloqueio_global():
 95:     """Coloca todas as threads em pausa (cooldown compartilhado)."""
 96:     global _cooldown_ate
 97:     if CAPTCHA_PAUSA_GLOBAL_SEGUNDOS <= 0:
 98:         return
 99:     with _cooldown_lock:
100:         _cooldown_ate = max(_cooldown_ate, time.time() + CAPTCHA_PAUSA_GLOBAL_SEGUNDOS)
101: 
102: 
103: def _aguardar_cooldown(termo):
104:     """Espera o cooldown global, se alguma thread detectou bloqueio."""
105:     with _cooldown_lock:
106:         restante = _cooldown_ate - time.time()
107:     if restante <= 0:
108:         return
109: 
110:     print(f"[{termo}] Pausa global anti-bloqueio: aguardando {int(restante) + 1}s...")
111:     while restante > 0:
112:         time.sleep(min(restante, 10))
113:         with _cooldown_lock:
114:             restante = _cooldown_ate - time.time()
115: 
116: 
117: def _pausar_com_aviso(segundos, termo):
118:     print(f"[{termo}] Aguardando {segundos}s (pausa longa anti-bloqueio)...")
119:     restante = segundos
120:     while restante > 0:
121:         passo = min(restante, 15)
122:         time.sleep(passo)
123:         restante -= passo
124: 
125: 
126: def _navegar_com_retry(page, url, tentativas=3, timeout=30000, termo="?"):
127:     """Navega com retry e backoff; detecta captcha e aplica pausa longa.
128: 
129:     Levanta BloqueioDetectado quando o bloqueio persiste após as tentativas.
130:     """
131:     for tentativa in range(1, tentativas + 1):
132:         _aguardar_cooldown(termo)
133:         try:
134:             page.goto(url, timeout=timeout)
135:         except Exception as e:
136:             print(f"  Retry {tentativa}/{tentativas} ao navegar para {url}: {type(e).__name__}")
137:             time.sleep(2 * tentativa)
138:             continue
139: 
140:         if not _pagina_bloqueada(page):
141:             return True
142: 
143:         _marcar_bloqueio_global()
144:         print(f"[{termo}] ⚠ Google Maps bloqueou o acesso (captcha/tráfego incomum).")
145: 
146:         if tentativa >= min(tentativas, CAPTCHA_MAX_TENTATIVAS):
147:             print(f"[{termo}] Bloqueio persistente após {tentativa} tentativa(s). Abortando esta área.")
148:             raise BloqueioDetectado(termo)
149: 
150:         _pausar_com_aviso(CAPTCHA_PAUSA_SEGUNDOS, termo)
151: 
152:     return False
153: 
154: 
155: def _obter_urls_perfis(page):
156:     urls = set()
157:     for link in page.query_selector_all('a[href*="/maps/place/"]'):
158:         href = link.get_attribute('href')
159:         if href:
160:             urls.add(href)
161:     return urls
162: 
163: 
164: def _rolar_resultados(page, termo="?"):
165:     """Rola a lista até esgotar os resultados (ou atingir o limite de rolagens)."""
166:     ultimo_total = 0
167:     rodadas_estagnadas = 0
168:     for _ in range(MAX_ROLAGENS):
169:         if _pagina_bloqueada(page, checar_texto=False):
170:             _marcar_bloqueio_global()
171:             raise BloqueioDetectado(termo)
172: 
173:         total = len(_obter_urls_perfis(page))
174:         page.evaluate('''() => {
175:             const feed = document.querySelector('div[role="feed"]');
176:             if(feed) feed.scrollTop = feed.scrollHeight;
177:         }''')
178:         time.sleep(1.0 + random.uniform(0, 0.6))  # jitter anti-bloqueio
179: 
180:         if total == ultimo_total:
181:             rodadas_estagnadas += 1
182:             if rodadas_estagnadas >= MAX_RODADAS_ESTAGNADAS:
183:                 break
184:         else:
185:             rodadas_estagnadas = 0
186:         ultimo_total = total
187: 
188: 
189: def extrair_leads_local(nicho, termo_busca, cidade, uf, mostrar_navegador=False):
190:     query = _montar_query(nicho, termo_busca, cidade, uf)
191:     url = f"https://www.google.com/maps/search/{urllib.parse.quote(query)}"
192:     leads = []
193: 
194:     p = sync_playwright().start()
195:     browser = None
196:     try:
197:         browser = p.chromium.launch(headless=not mostrar_navegador)
198:         context = browser.new_context(
199:             user_agent=USER_AGENT,
200:             viewport={"width": 1366, "height": 768},
201:             locale="pt-BR",
202:         )
203:         page = context.new_page()
204: 
205:         if not _navegar_com_retry(page, url, timeout=60000, termo=termo_busca):
206:             print(f"[{termo_busca}] Falha ao carregar a busca.")
207:             return leads
208: 
209:         try:
210:             page.wait_for_selector('div[role="feed"]', timeout=10000)
211:         except Exception:
212:             print(f"[{termo_busca}] Nenhum resultado encontrado.")
213:             return leads
214: 
215:         print(f"[{termo_busca}] Rolando resultados...")
216:         _rolar_resultados(page, termo_busca)
217: 
218:         if _pagina_bloqueada(page):
219:             _marcar_bloqueio_global()
220:             raise BloqueioDetectado(termo_busca)
221: 
222:         urls = sorted(_obter_urls_perfis(page))
223:         print(f"[{termo_busca}] {len(urls)} perfis encontrados. Extraindo dados...")
224: 
225:         for i, place_url in enumerate(urls):
226:             try:
227:                 time.sleep(random.uniform(0.8, 2.5))  # pausa anti-bloqueio entre navegações
228:                 if not _navegar_com_retry(page, place_url, timeout=30000, termo=termo_busca):
229:                     continue
230:                 time.sleep(random.uniform(1.2, 2.8))
231: 
232:                 nome_elem = page.query_selector('h1')
233:                 nome = nome_elem.inner_text() if nome_elem else "Sem nome"
234:                 if nome in ("Resultados", ""):
235:                     continue
236: 
237:                 # Extração do Bairro (Endereço)
238:                 bairro_real = "Não Informado"
239:                 endereco_elem = page.query_selector('button[data-item-id="address"]')
240:                 if endereco_elem:
241:                     aria_endereco = endereco_elem.get_attribute('aria-label')
242:                     if aria_endereco:
243:                         texto_limpo = aria_endereco.replace('Endereço:', '').replace('Address:', '').strip()
244:                         try:
245:                             parts = texto_limpo.split(" - ")
246:                             if len(parts) >= 2:
247:                                 bairro_real = parts[1].split(",")[0].strip()
248:                         except Exception:
249:                             pass
250: 
251:                 # Extração do Telefone
252:                 telefone_bruto = ""
253:                 tel_elem = page.query_selector('button[data-item-id^="phone:tel:"]')
254:                 if tel_elem:
255:                     aria = tel_elem.get_attribute('aria-label')
256:                     if aria:
257:                         telefone_bruto = aria.replace('Telefone:', '').replace('Phone:', '').strip()
258: 
259:                 telefone_limpo, tipo_telefone, whatsapp_link = formatar_telefone(telefone_bruto)
260: 
261:                 link_site = ""
262:                 link_insta = ""
263: 
264:                 site_elem = page.query_selector('a[data-item-id="authority"]')
265:                 if site_elem:
266:                     link_site = site_elem.get_attribute('href')
267: 
268:                 for a in page.query_selector_all('a'):
269:                     href = a.get_attribute('href')
270:                     if href and "instagram.com" in href:
271:                         link_insta = href
272:                         break
273: 
274:                 leads.append({
275:                     'nome': nome,
276:                     'telefone': telefone_limpo,
277:                     'tipo_telefone': tipo_telefone,
278:                     'whatsapp_link': whatsapp_link,
279:                     'instagram': link_insta,
280:                     'site': link_site,
281:                     'bairro': bairro_real,
282:                     'cidade': cidade,
283:                     'estado': uf,
284:                     'nicho': nicho
285:                 })
286:                 print(f"[{termo_busca}] {i+1}/{len(urls)} - {nome} | {tipo_telefone} | {telefone_limpo}")
287: 
288:             except BloqueioDetectado:
289:                 raise
290:             except Exception as e:
291:                 print(f"[{termo_busca}] Erro ao extrair {place_url}: {e}")
292: 
293:     except BloqueioDetectado:
294:         print(f"[{termo_busca}] Área interrompida por bloqueio do Google Maps "
295:               f"({len(leads)} lead(s) preservado(s)).")
296:     finally:
297:         if browser:
298:             browser.close()
299:         p.stop()
300: 
301:     return leads
302: 
303: 
304: def rodar_scraper_multithread(nicho, cidade, uf, termos_lista, mostrar_navegador=False, save_callback=None):
305:     """
306:     Executa a coleta em multithread. Se save_callback for informado, cada lote
307:     (por área) é salvo assim que termina, evitando perder a coleta em caso de falha.
308:     """
309:     todos_leads = []
310:     vistos = set()
311:     max_workers = min(3, len(termos_lista))
312:     print(f"Iniciando scraper com {max_workers} threads em {len(termos_lista)} área(s)...")
313: 
314:     with ThreadPoolExecutor(max_workers=max_workers) as executor:
315:         futuros = {
316:             executor.submit(extrair_leads_local, nicho, termo, cidade, uf, mostrar_navegador): termo
317:             for termo in termos_lista
318:         }
319: 
320:         for futuro in as_completed(futuros):
321:             termo = futuros[futuro]
322:             try:
323:                 leads_area = futuro.result()
324:                 with lock:
325:                     novos = []
326:                     for lead in leads_area:
327:                         chave = (lead['nome'], lead['cidade'])
328:                         if chave not in vistos:
329:                             vistos.add(chave)
330:                             novos.append(lead)
331:                     todos_leads.extend(novos)
332: 
333:                 if novos and save_callback:
334:                     save_callback(pd.DataFrame(novos))
335: 
336:                 print(f"[{termo}] Finalizado. {len(novos)} leads novos (acumulado: {len(todos_leads)}).")
337:             except Exception as e:
338:                 print(f"Erro na busca {termo}: {e}")
339: 
340:     return pd.DataFrame(todos_leads)
``````

## File: src/database.py
``````python
  1: # src/database.py
  2: """Camada de acesso a dados (leads, templates e log de envio).
  3: 
  4: Usa `src/backend.py`, que abstrai PostgreSQL e DuckDB — o código daqui não
  5: depende do banco específico. A criação do schema e o seed dos templates ficam
  6: em `src/schema.py` (executado uma vez no setup: `python src/schema.py`).
  7: """
  8: import os
  9: import re
 10: import json
 11: from datetime import datetime
 12: 
 13: import pandas as pd
 14: 
 15: from src import backend
 16: 
 17: 
 18: class LeadDatabase:
 19:     def __init__(self, conn=None):
 20:         self.conn = conn if conn is not None else backend.conectar()
 21: 
 22:     def listar_templates_ativos(self):
 23:         """Retorna os templates ativos como lista de dicionários (id, mensagem, descricao, segmento, ativo)."""
 24:         return (
 25:             backend.query_df(self.conn, """
 26:                 SELECT id, mensagem, descricao, segmento, ativo
 27:                 FROM templates_whatsapp
 28:                 WHERE ativo = TRUE
 29:                 ORDER BY id
 30:             """)
 31:             .to_dict("records")
 32:         )
 33: 
 34:     def salvar_log_envio(self, lead_id, nome, cidade, telefone, chat_id, status,
 35:                          mensagem=None, payload=None, erro=None):
 36:         """Grava uma linha de log de envio com os campos normalizados.
 37: 
 38:         - `lead_id`: referencia `leads.lead_id` (vínculo por PK).
 39:         - `telefone` é reduzido a dígitos (mesma representação de `leads.telefone`),
 40:           permitindo JOIN direto: leads.telefone = whatsapp_envios_log.telefone.
 41:         """
 42:         telefone = re.sub(r"\D", "", str(telefone or ""))
 43:         telefone_normalizado = None
 44:         if telefone.startswith("55") and len(telefone) > 11:
 45:             base = telefone[2:]
 46:         else:
 47:             base = telefone
 48:         if len(base) == 11:
 49:             telefone_normalizado = f"55{base}"
 50:         elif telefone:
 51:             telefone_normalizado = telefone
 52: 
 53:         payload_str = None
 54:         if payload is not None:
 55:             if isinstance(payload, (dict, list)):
 56:                 try:
 57:                     payload_str = json.dumps(payload, ensure_ascii=False, default=str)
 58:                 except Exception:
 59:                     payload_str = str(payload)
 60:             else:
 61:                 payload_str = str(payload)
 62: 
 63:         p = backend.ph()
 64:         backend.execute(self.conn, f"""
 65:             INSERT INTO whatsapp_envios_log
 66:                 (lead_id, nome, cidade, telefone, telefone_normalizado, chat_id,
 67:                  status, mensagem, payload, erro, data_envio)
 68:             VALUES ({p}, {p}, {p}, {p}, {p}, {p}, {p}, {p}, {p}, {p}, {p})
 69:         """, [
 70:             lead_id, nome, cidade, telefone or None, telefone_normalizado, chat_id,
 71:             status, mensagem, payload_str, erro, datetime.now(),
 72:         ])
 73:         backend.commit(self.conn)
 74: 
 75:     def save_leads(self, df: pd.DataFrame):
 76:         if df.empty:
 77:             return 0
 78: 
 79:         descartados = set(backend.query_all(
 80:             self.conn, "SELECT nome, cidade FROM leads WHERE status = 'descartado'"
 81:         ))
 82:         df = df[~df.apply(lambda row: (row['nome'], row['cidade']) in descartados, axis=1)]
 83: 
 84:         if df.empty:
 85:             print("Todos os leads coletados já foram descartados anteriormente. Pulando salvamento.")
 86:             return 0
 87: 
 88:         df = df.copy()
 89:         df['data_extracao'] = datetime.now()
 90:         if 'status' not in df.columns:
 91:             df['status'] = 'ativo'
 92: 
 93:         colunas = [
 94:             'nome', 'telefone', 'tipo_telefone', 'whatsapp_link', 'instagram',
 95:             'site', 'bairro', 'cidade', 'estado', 'nicho', 'status', 'data_extracao',
 96:         ]
 97:         linhas = [
 98:             tuple(backend._valor(r.get(c)) for c in colunas)
 99:             for r in df.to_dict("records")
100:         ]
101: 
102:         # UPSERT preservando o status atual e as colunas de log do WhatsApp.
103:         # Assim, re-raspar um lead já enviado NÃO apaga data_envio_whatsapp/status_whatsapp.
104:         backend.bulk_upsert(
105:             self.conn,
106:             table="leads",
107:             columns=colunas,
108:             rows=linhas,
109:             conflict="nome, cidade",
110:             set_clause=(
111:                 "telefone = excluded.telefone, "
112:                 "tipo_telefone = excluded.tipo_telefone, "
113:                 "whatsapp_link = excluded.whatsapp_link, "
114:                 "instagram = excluded.instagram, "
115:                 "site = excluded.site, "
116:                 "bairro = excluded.bairro, "
117:                 "estado = excluded.estado, "
118:                 "nicho = excluded.nicho, "
119:                 "data_extracao = excluded.data_extracao"
120:             ),
121:         )
122:         backend.commit(self.conn)
123:         return len(df)
124: 
125:     def get_leads_para_envio(self, limite=None, numero=None, cidade=None, nicho=None):
126:         """Retorna leads ativos, celulares e ainda não enviados (evita spam/fixo).
127: 
128:         Filtros opcionais:
129:         - numero: filtra por telefone (completo ou parte; ignora não-dígitos)
130:         - cidade: filtra por nome exato da cidade
131:         - nicho:  filtra por nicho exato
132:         """
133:         p = backend.ph()
134:         query = f"""
135:             SELECT lead_id, nome, telefone, whatsapp_link, bairro, cidade, estado, nicho, chat_id_waha
136:             FROM leads
137:             WHERE status = 'ativo'
138:               AND tipo_telefone = 'Celular'
139:               AND (status_whatsapp IS NULL OR status_whatsapp = 'pendente')
140:         """
141:         params = []
142:         if numero:
143:             numero = re.sub(r"\D", "", str(numero))
144:             query += f" AND regexp_replace(telefone, '[^0-9]', '', 'g') LIKE {p}"
145:             params.append(f"%{numero}%")
146:         if cidade:
147:             query += f" AND cidade = {p}"
148:             params.append(cidade)
149:         if nicho:
150:             query += f" AND nicho = {p}"
151:             params.append(nicho)
152:         query += " ORDER BY cidade, bairro, nome"
153:         if limite:
154:             query += f" LIMIT {p}"
155:             params.append(int(limite))
156:         return backend.query_df(self.conn, query, params)
157: 
158:     def salvar_chat_id_waha(self, nome, cidade, chat_id):
159:         """Cacheia o chatId resolvido (ex.: 143172869029943@lid) para não repetir
160:         a chamada ao /api/checkNumberStatus em envios futuros."""
161:         p = backend.ph()
162:         backend.execute(self.conn, f"""
163:             UPDATE leads
164:             SET chat_id_waha = {p}
165:             WHERE nome = {p} AND cidade = {p}
166:         """, [chat_id, nome, cidade])
167:         backend.commit(self.conn)
168: 
169:     def marcar_envio(self, nome, cidade, status_whatsapp):
170:         """Registra o resultado do envio. 'data_envio_whatsapp' é gravado apenas no sucesso."""
171:         p = backend.ph()
172:         if status_whatsapp == 'enviado':
173:             backend.execute(self.conn, f"""
174:                 UPDATE leads
175:                 SET status_whatsapp = {p}, data_envio_whatsapp = {p}
176:                 WHERE nome = {p} AND cidade = {p}
177:             """, [status_whatsapp, datetime.now(), nome, cidade])
178:         else:
179:             backend.execute(self.conn, f"""
180:                 UPDATE leads
181:                 SET status_whatsapp = {p}
182:                 WHERE nome = {p} AND cidade = {p}
183:             """, [status_whatsapp, nome, cidade])
184:         backend.commit(self.conn)
185: 
186:     def export_to_excel(self, nicho: str, cidade: str):
187:         p = backend.ph()
188:         df = backend.query_df(self.conn, f"""
189:             SELECT nome, telefone, tipo_telefone, whatsapp_link, instagram, site, bairro, data_extracao
190:             FROM leads
191:             WHERE nicho = {p} AND cidade = {p} AND status = 'ativo'
192:             ORDER BY bairro, nome
193:         """, [nicho, cidade])
194: 
195:         if df.empty:
196:             print("Nenhum dado ativo para exportar.")
197:             return
198: 
199:         os.makedirs("output", exist_ok=True)
200:         nome_arquivo = f"output/leads_{nicho}_{cidade}.xlsx".replace(" ", "_").lower()
201:         df.to_excel(nome_arquivo, index=False)
202:         print(f"🎉 Exportação concluída: {nome_arquivo} ({len(df)} leads ativos)")
203: 
204:     def close(self):
205:         backend.close(self.conn)
``````

## File: src/locations.py
``````python
  1: # src/locations.py
  2: """Localidades (UF, cidade e bairros) com cache em PostgreSQL.
  3: 
  4: Fonte oficial: API de Localidades do IBGE.
  5:     estados    -> /api/v1/localidades/estados
  6:     municipios -> /api/v1/localidades/municipios
  7:     distritos  -> /api/v1/localidades/distritos
  8: 
  9: Com LOCALIDADES_USAR_CACHE=true (padrão), a base local é consultada primeiro;
 10: só vai para a rede o que ainda não existe no banco. Com a flag false, os dados
 11: são sempre buscados na API (e a base local é atualizada com o resultado).
 12: 
 13: Observação: os "distritos" do IBGE são divisões administrativas e, em muitos
 14: municípios, resumem-se à própria sede. Quando não há distritos suficientes,
 15: a lista é complementada com bairros do OpenStreetMap (Nominatim + Overpass).
 16: """
 17: import os
 18: import time
 19: import unicodedata
 20: 
 21: import pandas as pd
 22: import requests
 23: 
 24: from src import localidades_db
 25: from src.config import env_int, str_para_bool
 26: 
 27: IBGE_API = "https://servicodados.ibge.gov.br/api/v1/localidades"
 28: 
 29: # User-Agent identificável é exigido pela política de uso do Nominatim.
 30: HEADERS = {"User-Agent": "map-scraper-lead-prospecting/1.0 (prospeccao.mapscraper@gmail.com)"}
 31: 
 32: OVERPASS_ENDPOINTS = [
 33:     "https://overpass-api.de/api/interpreter",
 34:     "https://overpass.private.coffee/api/interpreter",
 35:     "https://overpass.osm.ch/api/interpreter",
 36:     "https://overpass.kumi.systems/api/interpreter",
 37: ]
 38: 
 39: # Se true: consulta o banco antes da API. Se false: sempre busca na API.
 40: USAR_CACHE = str_para_bool(os.environ.get("LOCALIDADES_USAR_CACHE"), padrao=True)
 41: 
 42: # Se false: NUNCA grava na base local. Funciona como "somente leitura":
 43: # o banco é consultado, mas nada é alterado.
 44: SALVAR = str_para_bool(os.environ.get("LOCALIDADES_SALVAR"), padrao=True)
 45: 
 46: # Quantidade mínima de distritos úteis para não precisar do OpenStreetMap.
 47: # Abaixo disso, a cidade é complementada com bairros do OSM.
 48: MIN_BAIRROS = max(1, env_int("LOCALIDADES_MIN_BAIRROS", 3))
 49: 
 50: # Pausa (segundos) entre cidades no aquecimento por UF, aplicada apenas quando o
 51: # OpenStreetMap foi consultado (política de uso do Nominatim: 1 req/s).
 52: AQUECER_PAUSA_PADRAO = max(0, env_int("AQUECER_PAUSA_SEGUNDOS", 2))
 53: 
 54: _avisou_cache_indisponivel = False
 55: _avisou_sem_gravacao = False
 56: 
 57: 
 58: def _cache(funcao, *args, **kwargs):
 59:     """Executa uma operação na base local, tolerando banco travado/indisponível."""
 60:     global _avisou_cache_indisponivel
 61:     try:
 62:         return funcao(*args, **kwargs)
 63:     except localidades_db.CacheIndisponivel as e:
 64:         if not _avisou_cache_indisponivel:
 65:             print(f"  Aviso: base local de localidades indisponível ({e}).")
 66:             print("         Seguindo apenas com as APIs (IBGE/OSM).")
 67:             _avisou_cache_indisponivel = True
 68:         return None
 69: 
 70: 
 71: def _salvar(funcao, *args, **kwargs):
 72:     """Grava na base local, respeitando LOCALIDADES_SALVAR=false."""
 73:     global _avisou_sem_gravacao
 74:     if not SALVAR:
 75:         if not _avisou_sem_gravacao:
 76:             print("  LOCALIDADES_SALVAR=false: a base local não será alterada.")
 77:             _avisou_sem_gravacao = True
 78:         return None
 79:     return _cache(funcao, *args, **kwargs)
 80: 
 81: 
 82: # ---------------------------------------------------------------------------
 83: # IBGE
 84: # ---------------------------------------------------------------------------
 85: def _get_json(url, params=None, timeout=60, tentativas=3):
 86:     for tentativa in range(1, tentativas + 1):
 87:         try:
 88:             resposta = requests.get(url, params=params, timeout=timeout, headers=HEADERS)
 89:             resposta.raise_for_status()
 90:             return resposta.json()
 91:         except Exception as e:
 92:             print(f"  IBGE indisponível (tentativa {tentativa}/{tentativas}): {type(e).__name__}")
 93:             if tentativa < tentativas:
 94:                 time.sleep(1.5 * tentativa)
 95:     return None
 96: 
 97: 
 98: def _baixar_estados():
 99:     dados = _get_json(f"{IBGE_API}/estados", params={"orderBy": "nome"}, timeout=30)
100:     if not dados:
101:         return None
102:     return [{"uf": e["sigla"], "nome": e["nome"]} for e in dados]
103: 
104: 
105: def _uf_do_municipio(municipio):
106:     try:
107:         return municipio["microrregiao"]["mesorregiao"]["UF"]["sigla"]
108:     except (KeyError, TypeError):
109:         try:
110:             return municipio["regiao-imediata"]["regiao-intermediaria"]["UF"]["sigla"]
111:         except (KeyError, TypeError):
112:             return None
113: 
114: 
115: def _baixar_municipios(uf=None):
116:     url = f"{IBGE_API}/estados/{uf}/municipios" if uf else f"{IBGE_API}/municipios"
117:     dados = _get_json(url, params={"orderBy": "nome"})
118:     if not dados:
119:         return None
120: 
121:     registros = []
122:     for municipio in dados:
123:         sigla = uf or _uf_do_municipio(municipio)
124:         if not sigla:
125:             continue
126:         registros.append({
127:             "id_municipio": municipio["id"],
128:             "nome": municipio["nome"],
129:             "uf": sigla,
130:         })
131:     return registros
132: 
133: 
134: def _baixar_distritos(id_municipio=None):
135:     url = (f"{IBGE_API}/municipios/{id_municipio}/distritos"
136:            if id_municipio else f"{IBGE_API}/distritos")
137:     dados = _get_json(url)
138:     if not dados:
139:         return None
140: 
141:     registros = []
142:     for distrito in dados:
143:         municipio = distrito.get("municipio") or {}
144:         registros.append({
145:             "id_distrito": distrito.get("id"),
146:             "nome": (distrito.get("nome") or "").strip(),
147:             "id_municipio": municipio.get("id"),
148:         })
149:     return [r for r in registros if r["id_municipio"] and r["nome"]]
150: 
151: 
152: _municipios_memoria = {}
153: 
154: 
155: def _municipios_da_uf(uf):
156:     """Lista de municípios da UF, memorizada na execução para não baixar duas vezes."""
157:     if uf not in _municipios_memoria:
158:         print(f"  Baixando a lista de municípios de {uf} do IBGE...")
159:         municipios = _baixar_municipios(uf)
160:         if municipios is None:
161:             return None
162:         _municipios_memoria[uf] = municipios
163:     return _municipios_memoria[uf]
164: 
165: 
166: # ---------------------------------------------------------------------------
167: # OpenStreetMap (fallback de bairros)
168: # ---------------------------------------------------------------------------
169: def _obter_bbox_cidade(cidade, uf):
170:     """Retorna (sul, norte, oeste, leste) da cidade via Nominatim."""
171:     url = "https://nominatim.openstreetmap.org/search"
172:     params = {"format": "json", "q": f"{cidade}, {uf}, Brazil", "limit": 1}
173:     try:
174:         resposta = requests.get(url, params=params, timeout=15, headers=HEADERS)
175:         resposta.raise_for_status()
176:         resultados = resposta.json()
177:         if not resultados:
178:             return None
179:         bb = resultados[0].get("boundingbox")
180:         if not bb or len(bb) != 4:
181:             return None
182:         sul, norte, oeste, leste = (float(v) for v in bb)
183:         return (sul, norte, oeste, leste)
184:     except Exception as e:
185:         print(f"Erro ao localizar a cidade no Nominatim: {e}")
186:         return None
187: 
188: 
189: def _consultar_overpass(query):
190:     """Tenta a consulta em vários espelhos do Overpass, com retry e backoff.
191: 
192:     Retorna o JSON da resposta, ou None quando nenhum espelho respondeu
193:     (serviço indisponível) — o que é diferente de responder vazio.
194:     """
195:     for endpoint in OVERPASS_ENDPOINTS:
196:         for tentativa in range(1, 3):
197:             try:
198:                 resposta = requests.get(endpoint, params={"data": query}, timeout=45, headers=HEADERS)
199:                 resposta.raise_for_status()
200:                 return resposta.json()
201:             except Exception as e:
202:                 print(f"  Overpass ({endpoint}) tentativa {tentativa} falhou: {type(e).__name__}")
203:                 time.sleep(1.5 * tentativa)
204:     return None
205: 
206: 
207: def _obter_bairros_overpass(sul, norte, oeste, leste):
208:     """Busca bairros dentro do bbox via Overpass (place=* e admin_level 9/10)."""
209:     bbox = f"({sul},{oeste},{norte},{leste})"
210: 
211:     query_leve = f"""
212: [out:json][timeout:40];
213: (
214:   node["place"~"^(suburb|neighbourhood|quarter)$"]{bbox};
215:   way["place"~"^(suburb|neighbourhood|quarter)$"]{bbox};
216: );
217: out center tags;
218: """
219: 
220:     query_admin = f"""
221: [out:json][timeout:55];
222: (
223:   relation["boundary"="administrative"]["admin_level"="9"]{bbox};
224:   relation["boundary"="administrative"]["admin_level"="10"]{bbox};
225: );
226: out center tags;
227: """
228: 
229:     data = _consultar_overpass(query_leve)
230:     if data is None:
231:         return None
232:     if data.get("elements"):
233:         return data
234:     return _consultar_overpass(query_admin)
235: 
236: 
237: def _bairros_via_overpass(cidade, uf):
238:     """Retorna a lista de bairros do OSM, ou None se o serviço estiver indisponível."""
239:     bbox = _obter_bbox_cidade(cidade, uf)
240:     if not bbox:
241:         return None
242: 
243:     data = _obter_bairros_overpass(*bbox)
244:     if data is None:
245:         return None
246: 
247:     nomes = set()
248:     for elemento in data.get("elements", []):
249:         tags = elemento.get("tags") or {}
250:         nome = tags.get("name")
251:         if not isinstance(nome, str):
252:             continue
253:         nome = nome.strip()
254:         if nome and nome.lower() != cidade.strip().lower():
255:             nomes.add(nome)
256:     return sorted(nomes)
257: 
258: 
259: # ---------------------------------------------------------------------------
260: # API pública do módulo
261: # ---------------------------------------------------------------------------
262: def obter_estados():
263:     if USAR_CACHE:
264:         estados = _cache(localidades_db.ler_estados)
265:         if estados:
266:             print(f"Base local: {len(estados)} estados.")
267:             return pd.DataFrame(estados)
268: 
269:     estados = _baixar_estados()
270:     if estados is None:
271:         estados = _cache(localidades_db.ler_estados)
272:         if estados:
273:             print("IBGE indisponível. Usando os estados gravados na base local.")
274:             return pd.DataFrame(estados)
275:         print("Erro ao buscar estados.")
276:         return pd.DataFrame()
277: 
278:     _salvar(localidades_db.salvar_estados, estados)
279:     return pd.DataFrame(estados)
280: 
281: 
282: def obter_cidades(uf):
283:     if USAR_CACHE:
284:         municipios = _cache(localidades_db.ler_municipios, uf)
285:         if municipios:
286:             print(f"Base local: {len(municipios)} cidades em {uf}.")
287:             return [m["nome"] for m in municipios]
288: 
289:     municipios = _municipios_da_uf(uf)
290:     if municipios is None:
291:         municipios = _cache(localidades_db.ler_municipios, uf)
292:         if municipios:
293:             print(f"IBGE indisponível. Usando as cidades de {uf} gravadas na base local.")
294:             return [m["nome"] for m in municipios]
295:         print(f"Erro ao buscar cidades para {uf}.")
296:         return []
297: 
298:     _salvar(localidades_db.salvar_municipios, municipios)
299:     return sorted(m["nome"] for m in municipios)
300: 
301: 
302: def _normalizar(texto):
303:     """Minúsculas e sem acentos, para comparar nomes digitados pelo usuário."""
304:     texto = unicodedata.normalize("NFKD", str(texto or ""))
305:     return "".join(c for c in texto if not unicodedata.combining(c)).strip().casefold()
306: 
307: 
308: def filtrar_cidades(cidades, termo):
309:     """Filtra a lista de cidades por um trecho, ignorando acentos e maiúsculas."""
310:     alvo = _normalizar(termo)
311:     if not alvo:
312:         return []
313:     return [c for c in cidades if alvo in _normalizar(c)]
314: 
315: 
316: def _descobrir_bairros(cidade, uf, municipio):
317:     """Monta a lista final de bairros: distritos do IBGE + complemento do OSM.
318: 
319:     Retorna (registros, fonte). fonte=None significa "não gravar no cache" —
320:     usado quando houve falha de rede, para tentar de novo na próxima execução.
321:     """
322:     registros = []
323:     total_distritos = 0
324:     if municipio:
325:         distritos = _baixar_distritos(municipio["id_municipio"]) or []
326:         total_distritos = len(distritos)
327:         for distrito in distritos:
328:             if _normalizar(distrito["nome"]) == _normalizar(cidade):
329:                 continue
330:             registros.append({"nome": distrito["nome"], "id_distrito": distrito["id_distrito"]})
331: 
332:     if len(registros) >= MIN_BAIRROS:
333:         print(f"  IBGE: {len(registros)} distritos de {cidade}-{uf} serão usados como áreas de busca.")
334:         return registros, localidades_db.FONTE_IBGE
335: 
336:     # A API de Localidades do IBGE só tem distritos/subdistritos — não tem bairros.
337:     # Quando o município tem apenas o distrito-sede, não há o que aproveitar.
338:     if total_distritos <= 1:
339:         print(f"  IBGE não publica bairros para {cidade}-{uf}: o município tem apenas "
340:               f"{total_distritos} distrito (a sede).")
341:     else:
342:         print(f"  IBGE: apenas {len(registros)} distrito(s) além da sede em {cidade}-{uf}.")
343: 
344:     print("  Buscando bairros no OpenStreetMap...")
345:     bairros_osm = _bairros_via_overpass(cidade, uf)
346: 
347:     if bairros_osm is None:
348:         print("  OpenStreetMap indisponível. Esta cidade NÃO será gravada no cache;")
349:         print("  os distritos do IBGE serão usados apenas nesta execução.")
350:         return registros, None
351: 
352:     vistos = {_normalizar(r["nome"]) for r in registros}
353:     for nome in bairros_osm:
354:         if _normalizar(nome) not in vistos:
355:             vistos.add(_normalizar(nome))
356:             registros.append({"nome": nome, "id_distrito": None})
357: 
358:     if bairros_osm:
359:         return registros, localidades_db.FONTE_OVERPASS
360:     if registros:
361:         return registros, localidades_db.FONTE_IBGE
362:     return [], localidades_db.FONTE_CIDADE
363: 
364: 
365: def _resolver_municipio(cidade, uf):
366:     """Descobre o município no IBGE: id e nome oficial.
367: 
368:     Primeiro tenta a base local; se não achar, baixa a lista da UF (e grava, se
369:     LOCALIDADES_SALVAR permitir). Retorna None quando o nome não existe na UF.
370:     """
371:     alvo = _normalizar(cidade)
372: 
373:     municipios = _cache(localidades_db.ler_municipios, uf) or []
374:     for item in municipios:
375:         if _normalizar(item["nome"]) == alvo:
376:             return {
377:                 "id_municipio": item["id_municipio"],
378:                 "nome": item["nome"],
379:                 "uf": uf,
380:                 "bairros_fonte": item.get("bairros_fonte"),
381:             }
382: 
383:     baixados = _municipios_da_uf(uf) or []
384:     _salvar(localidades_db.salvar_municipios, baixados)
385: 
386:     for item in baixados:
387:         if _normalizar(item["nome"]) == alvo:
388:             return {
389:                 "id_municipio": item["id_municipio"],
390:                 "nome": item["nome"],
391:                 "uf": item["uf"],
392:                 "bairros_fonte": None,
393:             }
394: 
395:     if mun := _cache(localidades_db.buscar_municipio, cidade, uf):
396:         return mun
397:     return None
398: 
399: 
400: def obter_municipio(cidade, uf):
401:     """Retorna o município do IBGE para o nome digitado (id, nome oficial e uf).
402: 
403:     Útil para gravar sempre o nome oficial, mesmo que o usuário digite sem
404:     acento ou em minúsculas (ex.: "canoas" -> "Canoas").
405:     """
406:     return _resolver_municipio(cidade, uf)
407: 
408: 
409: def obter_bairros(cidade, uf):
410:     """
411:     Retorna os bairros de uma cidade, usando a base local quando possível.
412:     Lista vazia significa "buscar a cidade inteira".
413:     """
414:     municipio = _resolver_municipio(cidade, uf)
415: 
416:     # Nome oficial do IBGE: evita divergência de acento/caixa nas buscas.
417:     nome_oficial = municipio["nome"] if municipio else cidade
418: 
419:     if USAR_CACHE and municipio and municipio.get("bairros_fonte"):
420:         bairros = _cache(localidades_db.ler_bairros, municipio["id_municipio"]) or []
421:         # O distrito-sede tem o mesmo nome da cidade e não ajuda na busca por área.
422:         bairros = [b for b in bairros if _normalizar(b) != _normalizar(nome_oficial)]
423:         fonte = municipio["bairros_fonte"]
424:         if fonte == localidades_db.FONTE_CIDADE or not bairros:
425:             print(f"Base local: {nome_oficial}-{uf} sem bairros (fonte: {fonte}).")
426:             return []
427:         print(f"Base local: {len(bairros)} bairros de {nome_oficial}-{uf} (fonte: {fonte}).")
428:         return bairros
429: 
430:     bairros, fonte = _descobrir_bairros(nome_oficial, uf, municipio)
431: 
432:     if municipio and fonte:
433:         _salvar(localidades_db.salvar_bairros, municipio["id_municipio"], bairros, fonte)
434: 
435:     return [b["nome"] for b in bairros]
436: 
437: 
438: def obter_termos_busca(cidade, uf, max_bairros=30):
439:     """
440:     Divide a coleta por bairros para ampliar a cobertura do Google Maps
441:     (que pagina os resultados e não entrega a cidade inteira em uma única busca).
442:     Se nenhum bairro for descoberto, busca a cidade inteira como fallback.
443:     """
444:     print(f"Descobrindo bairros de {cidade} - {uf}...")
445:     bairros = obter_bairros(cidade, uf)
446: 
447:     if bairros:
448:         bairros = bairros[:max_bairros]
449:         print(f"{len(bairros)} bairros encontrados. A coleta será dividida por bairro.")
450:         return bairros
451: 
452:     print("Nenhum bairro encontrado. Buscando a cidade inteira.")
453:     return [cidade]
454: 
455: 
456: def listar_municipios_pendentes(uf):
457:     """Lista os municípios da UF que ainda não têm bairros resolvidos.
458: 
459:     Se a UF ainda não estiver na base local, baixa a lista do IBGE (e grava, se
460:     LOCALIDADES_SALVAR permitir). Retorna [] quando todos já estão resolvidos.
461:     """
462:     pendentes = _cache(localidades_db.ler_municipios_pendentes, uf)
463:     if pendentes is None:
464:         return []
465:     if pendentes:
466:         return pendentes
467: 
468:     # Nada pendente: só é "tudo pronto" se a UF estiver na base local.
469:     if _cache(localidades_db.ler_municipios, uf):
470:         return []
471: 
472:     print(f"  {uf} ainda não está na base local. Baixando a lista de municípios do IBGE...")
473:     municipios = _baixar_municipios(uf)
474:     if not municipios:
475:         return []
476:     _salvar(localidades_db.salvar_municipios, municipios)
477:     return [{"id_municipio": m["id_municipio"], "nome": m["nome"]} for m in municipios]
478: 
479: 
480: def aquecer_bairros_uf(uf, cidades=None, max_cidades=0, pausa_segundos=None):
481:     """Resolve e grava os bairros de todas as cidades de uma UF (uma única vez).
482: 
483:     Útil para preparar o cache e depois rodar a coleta sem nenhuma consulta de
484:     rede. A pausa entre cidades é aplicada só quando o OpenStreetMap foi de fato
485:     consultado (cidades cobertas pelo IBGE são instantâneas).
486: 
487:     Retorna um dicionário com o resumo da execução.
488:     """
489:     if not SALVAR:
490:         print("\nLOCALIDADES_SALVAR=false: não é possível aquecer a base local.")
491:         print("Ative a flag LOCALIDADES_SALVAR para gravar os bairros.")
492:         return None
493: 
494:     pausa_segundos = AQUECER_PAUSA_PADRAO if pausa_segundos is None else pausa_segundos
495: 
496:     if cidades is None:
497:         print(f"\nVerificando quais cidades de {uf} ainda precisam de bairros...")
498:         cidades = listar_municipios_pendentes(uf)
499: 
500:     total_pendente = len(cidades)
501:     if not total_pendente:
502:         print(f"Todas as cidades de {uf} já têm bairros na base local. Nada a fazer.")
503:         return {"uf": uf, "pendentes": 0, "processadas": 0, "ibge": 0,
504:                 "osm": 0, "sem_bairros": 0, "falhas": 0}
505: 
506:     if max_cidades and max_cidades > 0:
507:         cidades = cidades[:max_cidades]
508: 
509:     print(f"\nAquecendo bairros de {len(cidades)} cidade(s) de {uf} "
510:           f"({total_pendente} pendente(s) no total).")
511:     print(f"Pausa entre cidades que usam OpenStreetMap: {pausa_segundos}s")
512:     print("Interrompa com Ctrl+C — o progresso já gravado é preservado.\n")
513: 
514:     resumo = {"uf": uf, "pendentes": total_pendente, "processadas": 0,
515:               "ibge": 0, "osm": 0, "sem_bairros": 0, "falhas": 0}
516: 
517:     try:
518:         for indice, cidade in enumerate(cidades, 1):
519:             nome = cidade["nome"]
520:             print(f"[{indice}/{len(cidades)}] {nome}-{uf}")
521: 
522:             bairros = obter_bairros(nome, uf)
523:             municipio = _cache(localidades_db.buscar_municipio, nome, uf)
524:             fonte = (municipio or {}).get("bairros_fonte")
525:             resumo["processadas"] += 1
526: 
527:             if fonte is None:
528:                 resumo["falhas"] += 1
529:                 print(f"  Falhou (nada gravado). Pulando.")
530:             elif fonte == localidades_db.FONTE_OVERPASS:
531:                 resumo["osm"] += 1
532:             elif fonte == localidades_db.FONTE_IBGE:
533:                 resumo["ibge"] += 1
534:             else:
535:                 resumo["sem_bairros"] += 1
536: 
537:             usou_osm = fonte in (localidades_db.FONTE_OVERPASS,
538:                                  localidades_db.FONTE_CIDADE)
539:             if usou_osm and indice < len(cidades):
540:                 time.sleep(pausa_segundos)
541:     except KeyboardInterrupt:
542:         print("\nInterrompido pelo usuário. O que já foi gravado está preservado.")
543: 
544:     print(f"\nResumo de {uf}: {resumo['processadas']} cidade(s) processada(s) "
545:           f"de {total_pendente} pendente(s).")
546:     print(f"  via IBGE: {resumo['ibge']} | via OpenStreetMap: {resumo['osm']} | "
547:           f"sem bairros: {resumo['sem_bairros']} | falhas: {resumo['falhas']}")
548:     restantes = total_pendente - resumo["processadas"]
549:     if restantes > 0:
550:         print(f"  {restantes} cidade(s) continuam pendentes — rode novamente para retomar.")
551:     return resumo
552: 
553: 
554: def _descrever_gravacao(total, recebidos):
555:     """Texto do resumo da sincronização (distingue gravado de apenas baixado)."""
556:     if total is None:
557:         return f"{recebidos} recebidos, NÃO gravados (base local indisponível)"
558:     return f"{total} gravados"
559: 
560: 
561: def sincronizar_base_localidades():
562:     """Baixa estados, municípios e distritos do IBGE para o DuckDB.
563: 
564:     Depois disso, com LOCALIDADES_USAR_CACHE=true, a coleta não faz chamadas de
565:     rede para descobrir bairros — exceto nas cidades em que o IBGE não tem
566:     distritos úteis (aí o OSM é consultado uma única vez e o resultado é gravado).
567:     """
568:     if not SALVAR:
569:         print("\nLOCALIDADES_SALVAR=false: a sincronização está desativada.")
570:         print("Nada foi baixado nem gravado. Ative a flag para popular a base local.")
571:         return False
572: 
573:     print("\nSincronizando base de localidades do IBGE...")
574: 
575:     estados = _baixar_estados()
576:     if estados is None:
577:         print("Falha ao baixar os estados. Sincronização abortada.")
578:         return False
579:     total = _salvar(localidades_db.salvar_estados, estados)
580:     print(f"  Estados: {_descrever_gravacao(total, len(estados))}.")
581: 
582:     municipios = _baixar_municipios()
583:     if municipios is None:
584:         print("Falha ao baixar os municípios. Sincronização abortada.")
585:         return False
586:     total = _salvar(localidades_db.salvar_municipios, municipios)
587:     print(f"  Municípios: {_descrever_gravacao(total, len(municipios))}.")
588: 
589:     print("  Baixando distritos (pode levar alguns segundos)...")
590:     distritos = _baixar_distritos()
591:     if distritos is None:
592:         print("Falha ao baixar os distritos. Estados e municípios foram gravados.")
593:         return False
594:     total = _salvar(localidades_db.salvar_distritos_bulk, distritos, MIN_BAIRROS)
595:     print(f"  Distritos: {_descrever_gravacao(total, len(distritos))}.")
596: 
597:     stats = _cache(localidades_db.estatisticas) or {}
598:     print(f"\nBase local: {stats.get('estados', 0)} estados, "
599:           f"{stats.get('municipios', 0)} municípios, {stats.get('bairros', 0)} bairros "
600:           f"({stats.get('cidades_prontas', 0)} cidades com bairros prontos).")
601:     print("Sincronização concluída.")
602:     return True
``````

## File: src/whatsapp.py
``````python
  1: # src/whatsapp.py
  2: """Integração com a WAHA (WhatsApp HTTP API) para envio de mensagens aos leads.
  3: 
  4: Configuração via variáveis de ambiente:
  5:     WAHA_API_URL   -> URL base da WAHA (padrão: http://localhost:3000)
  6:     WAHA_API_KEY   -> chave de API da WAHA (obrigatória se a instância exigir)
  7:     WAHA_SESSION   -> nome da sessão conectada na WAHA (padrão: "default")
  8: 
  9: O módulo só envia para leads:
 10:     - status = 'ativo'
 11:     - tipo_telefone = 'Celular'  (nunca fixo)
 12:     - ainda não enviados (status_whatsapp = 'pendente' ou NULL)
 13: """
 14: import os
 15: import random
 16: import re
 17: import time
 18: 
 19: import requests
 20: 
 21: from src.config import carregar_env, str_para_bool
 22: 
 23: carregar_env()
 24: 
 25: WAHA_API_URL = os.environ.get("WAHA_API_URL", "http://localhost:3000")
 26: WAHA_API_KEY = os.environ.get("WAHA_API_KEY", "")
 27: WAHA_SESSION = os.environ.get("WAHA_SESSION", "default")
 28: 
 29: # Se false, o módulo NÃO tenta enviar (desliga o envio de WhatsApp).
 30: WAHA_ATIVO = str_para_bool(os.environ.get("WAHA_ATIVO"), padrao=True)
 31: 
 32: # Se true, pula a coleta e vai direto para o envio (não coleta nada).
 33: SOMENTE_ENVIO = str_para_bool(os.environ.get("SOMENTE_ENVIO"), padrao=False)
 34: 
 35: # ---------------------------------------------------------------------------
 36: # Cadência de envio (anti-bloqueio)
 37: # ---------------------------------------------------------------------------
 38: # Formato "X a cada Y segundos", ex.: WAHA_CADENCIA=3:60  -> 3 envios por minuto.
 39: # Os envios são distribuídos ALEATORIAMENTE dentro da janela de Y segundos,
 40: # evitando pausas fixas (15s, 15s, ...) que são mais fáceis de detectar.
 41: WAHA_CADENCIA = os.environ.get("WAHA_CADENCIA", "").strip()
 42: 
 43: # Legado: WAHA_INTERVALO (pausa fixa) continua funcionando quando WAHA_CADENCIA
 44: # não é informado.
 45: WAHA_INTERVALO = int(os.environ.get("WAHA_INTERVALO", "13"))
 46: 
 47: # Limite de leads por campanha. Vazio = sem limite.
 48: WAHA_LIMITE = os.environ.get("WAHA_LIMITE", "").strip()
 49: WAHA_LIMITE = int(WAHA_LIMITE) if WAHA_LIMITE else None
 50: 
 51: 
 52: def _parse_cadencia(valor):
 53:     """Interpreta "N:Y" -> (envios_por_janela, janela_segundos).
 54: 
 55:     Retorna None quando o valor está vazio/inválido (usa o intervalo fixo).
 56:     """
 57:     if not valor:
 58:         return None
 59:     try:
 60:         envios, janela = valor.split(":", 1)
 61:         envios = int(envios.strip())
 62:         janela = int(janela.strip())
 63:     except (ValueError, AttributeError):
 64:         return None
 65:     if envios <= 0 or janela <= 0:
 66:         return None
 67:     return envios, janela
 68: 
 69: 
 70: def _intervalos_aleatorios(quantidade, janela_segundos):
 71:     """Gera as pausas (em segundos) para `quantidade` envios numa janela.
 72: 
 73:     Distribui os envios em pontos aleatórios crescentes dentro da janela e
 74:     retorna a diferença entre pontos consecutivos — o intervalo entre cada envio
 75:     varia, mas o total da janela é respeitado.
 76:     """
 77:     if quantidade <= 1:
 78:         return [0]
 79:     # Pontos aleatórios crescentes: 1 envio em cada "fatia" da janela, com
 80:     # jitter dentro da fatia, garantindo tempos diferentes entre os envios.
 81:     pontos = sorted(
 82:         random.uniform((i * janela_segundos) / quantidade,
 83:                        ((i + 1) * janela_segundos) / quantidade)
 84:         for i in range(quantidade)
 85:     )
 86:     return [round(pontos[i + 1] - pontos[i], 2) for i in range(quantidade - 1)]
 87: 
 88: 
 89: def _pausas_cadencia(total, envios_janela, janela_segundos):
 90:     """Gera as pausas da campanha inteira respeitando a cadência.
 91: 
 92:     Agrupa os `total` envios em janelas de `janela_segundos` segundos, com
 93:     `envios_janela` envios por janela (distribuídos aleatoriamente). Retorna uma
 94:     lista com `total - 1` pausas (uma entre cada par consecutivo).
 95:     """
 96:     if total <= 1:
 97:         return [0]
 98: 
 99:     # Timestamp de envio de cada lead: janela + posição aleatória dentro dela.
100:     tempos = []
101:     for idx in range(total):
102:         janela_idx = idx // envios_janela
103:         pos_na_janela = idx % envios_janela
104:         inicio = janela_idx * janela_segundos
105:         # posição aleatória dentro da fatia correspondente a este envio
106:         p = random.uniform(
107:             inicio + (pos_na_janela * janela_segundos) / envios_janela,
108:             inicio + ((pos_na_janela + 1) * janela_segundos) / envios_janela,
109:         )
110:         tempos.append(p)
111: 
112:     tempos.sort()
113:     return [round(tempos[i + 1] - tempos[i], 2) for i in range(len(tempos) - 1)]
114: 
115: # Mensagem padrão (placeholder). Use {nome}, {bairro} e {cidade}.
116: MENSAGEM_PADRAO = "Olá {nome}! Vi que vocês atendem no bairro {bairro}, em {cidade}. Podemos conversar?"
117: 
118: 
119: def _normalizar_chatid(telefone):
120:     """Converte o telefone salvo em um chatId clássico do WAHA (55DDDNUMERO@c.us)."""
121:     numero = re.sub(r"\D", "", str(telefone or ""))
122:     if not numero:
123:         return None
124: 
125:     # Se veio com DDI 55 e tem mais de 11 dígitos, remove o prefixo.
126:     if numero.startswith("55") and len(numero) > 11:
127:         numero = numero[2:]
128: 
129:     # Celular brasileiro tem 11 dígitos (DDD + 9 dígitos).
130:     if len(numero) != 11:
131:         return None
132: 
133:     return f"55{numero}@c.us"
134: 
135: 
136: def _resolver_chatid_waha(telefone, session=None, api_url=None, api_key=None):
137:     """Resolve o chatId correto via /api/checkNumberStatus.
138: 
139:     Números recentes no WhatsApp usam o formato @lid (hidden user ID) em vez do
140:     clássico @c.us. Enviar com @c.us para esses números retorna HTTP 500.
141:     A WAHA responde o chatId certo via checkNumberStatus; usamos ele e, se a
142:     consulta falhar ou o número não existir, caímos no formato clássico @c.us.
143:     """
144:     session = session or WAHA_SESSION
145:     api_url = api_url or WAHA_API_URL
146:     api_key = api_key if api_key is not None else WAHA_API_KEY
147: 
148:     numero = re.sub(r"\D", "", str(telefone or ""))
149:     if not numero:
150:         return None
151: 
152:     if numero.startswith("55") and len(numero) > 11:
153:         numero = numero[2:]
154:     if len(numero) != 11:
155:         return None
156: 
157:     telefone_internacional = f"55{numero}"
158: 
159:     headers = {"Accept": "application/json"}
160:     if api_key:
161:         headers["X-Api-Key"] = api_key
162: 
163:     url = f"{api_url.rstrip('/')}/api/checkNumberStatus"
164:     params = {"session": session, "phone": telefone_internacional}
165: 
166:     try:
167:         response = requests.get(url, params=params, headers=headers, timeout=20)
168:         response.raise_for_status()
169:         dados = response.json()
170:         if dados.get("numberExists") and dados.get("chatId"):
171:             return dados["chatId"]
172:     except Exception:
173:         pass
174: 
175:     # Fallback: formato clássico @c.us (funciona para números mais antigos).
176:     return f"{telefone_internacional}@c.us"
177: 
178: 
179: def _limpar_markdown_whatsapp(texto):
180:     """Remove marcação de markdown (negrito e links) antes de enviar ao WhatsApp.
181: 
182:     - **texto**  -> texto
183:     - [rótulo](url) -> url (quando o rótulo já é a própria URL) ou "rótulo (url)"
184:     """
185:     texto = re.sub(r"\*\*([^*]+)\*\*", r"\1", texto)
186: 
187:     def _sub_link(match):
188:         rotulo = match.group(1)
189:         url = match.group(2)
190:         if rotulo.strip() == url.strip():
191:             return url
192:         return f"{rotulo} ({url})"
193: 
194:     return re.sub(r"\[([^\]]+)\]\(([^)]+)\)", _sub_link, texto)
195: 
196: 
197: def _renderizar_mensagem(template, lead):
198:     """Substitui {nome}, {bairro} e {cidade} de forma segura e limpa o markdown."""
199:     bairro = str(lead.get("bairro") or "sua região")
200:     cidade = str(lead.get("cidade") or "")
201:     texto = (
202:         template
203:         .replace("{nome}", str(lead.get("nome") or ""))
204:         .replace("{bairro}", bairro)
205:         .replace("{cidade}", cidade)
206:     )
207:     return _limpar_markdown_whatsapp(texto)
208: 
209: 
210: def enviar_texto_waha(chat_id, texto, session=None, api_url=None, api_key=None):
211:     """Envia uma mensagem de texto via WAHA."""
212:     session = session or WAHA_SESSION
213:     api_url = api_url or WAHA_API_URL
214:     api_key = api_key if api_key is not None else WAHA_API_KEY
215:     url = f"{api_url.rstrip('/')}/api/sendText"
216: 
217:     payload = {
218:         "session": session,
219:         "chatId": chat_id,
220:         "text": texto,
221:     }
222: 
223:     headers = {"Accept": "application/json", "Content-Type": "application/json"}
224:     if api_key:
225:         headers["X-Api-Key"] = api_key
226: 
227:     response = requests.post(url, json=payload, headers=headers, timeout=30)
228:     response.raise_for_status()
229:     return response.json()
230: 
231: 
232: def enviar_texto_numero(numero, texto, session=None, api_url=None, api_key=None):
233:     """Envia uma mensagem de texto para um número bruto (com DDD), já normalizado.
234: 
235:     Útil para o envio de teste, sem precisar de um lead no banco.
236:     """
237:     texto = _limpar_markdown_whatsapp(texto)
238:     chat_id = _resolver_chatid_waha(numero, session=session, api_url=api_url, api_key=api_key)
239:     if not chat_id:
240:         raise ValueError(f"Número inválido para envio: {numero}")
241:     return enviar_texto_waha(chat_id, texto, session=session, api_url=api_url, api_key=api_key)
242: 
243: 
244: def disparar_campanha(db, mensagem_template=None, intervalo=13, limite=None, leads=None):
245:     """Envia mensagens para os leads celulares pendentes.
246: 
247:     - db: instância de LeadDatabase
248:     - mensagem_template: texto com {nome}, {bairro}, {cidade} (usa MENSAGEM_PADRAO se None)
249:     - intervalo: pausa fixa em segundos entre envios (usado se não houver cadência)
250:     - leads: DataFrame opcional já filtrado; se None, busca pendentes (com limite)
251:     """
252:     mensagem_template = mensagem_template or MENSAGEM_PADRAO
253:     if leads is None:
254:         leads = db.get_leads_para_envio(limite)
255: 
256:     if leads.empty:
257:         print("Nenhum lead celular pendente de envio.")
258:         return
259: 
260:     total = len(leads)
261: 
262:     # Cadência aleatória (ex.: 3 a cada 60s) tem prioridade sobre o intervalo fixo.
263:     cadencia = _parse_cadencia(WAHA_CADENCIA)
264:     if cadencia:
265:         envios_janela, janela = cadencia
266:         pausas = _pausas_cadencia(total, envios_janela, janela)
267:         print(f"Enviando para {total} lead(s), cadência {envios_janela} a cada {janela}s "
268:               f"(intervalos aleatórios)...")
269:     else:
270:         pausas = [intervalo] * max(0, total - 1)
271:         print(f"Enviando para {total} lead(s), com intervalo fixo de {intervalo}s...")
272: 
273:     for i, (_, lead) in enumerate(leads.iterrows(), 1):
274:         texto = _renderizar_mensagem(mensagem_template, lead)
275:         lead_id = lead.get("lead_id")
276:         telefone = lead.get("telefone")
277:         nome = lead.get("nome")
278:         cidade = lead.get("cidade")
279: 
280:         chat_id = lead.get("chat_id_waha")
281:         if not chat_id:
282:             # Resolve (e cacheia) o chatId uma única vez por lead. Números novos
283:             # usam @lid; a consulta ao checkNumberStatus é feita só na primeira vez.
284:             chat_id = _resolver_chatid_waha(telefone)
285:             if chat_id:
286:                 db.salvar_chat_id_waha(nome, cidade, chat_id)
287: 
288:         if not chat_id:
289:             db.marcar_envio(nome, cidade, "falhou")
290:             db.salvar_log_envio(
291:                 lead_id, nome, cidade, telefone, chat_id, "falhou",
292:                 mensagem=texto, erro="telefone inválido",
293:             )
294:             print(f"[{i}/{total}] {nome} - telefone inválido, marcado como falhou.")
295:             continue
296: 
297:         try:
298:             resposta = enviar_texto_waha(chat_id, texto)
299:             db.marcar_envio(nome, cidade, "enviado")
300:             db.salvar_log_envio(
301:                 lead_id, nome, cidade, telefone, chat_id, "enviado",
302:                 mensagem=texto, payload=resposta,
303:             )
304:             print(f"[{i}/{total}] ENVIADO -> {nome} ({chat_id})")
305:         except Exception as e:
306:             payload_erro = None
307:             if getattr(e, "response", None) is not None:
308:                 try:
309:                     payload_erro = e.response.text
310:                 except Exception:
311:                     payload_erro = None
312:             erro = f"{type(e).__name__}: {e}"
313:             db.marcar_envio(nome, cidade, "falhou")
314:             db.salvar_log_envio(
315:                 lead_id, nome, cidade, telefone, chat_id, "falhou",
316:                 mensagem=texto, payload=payload_erro, erro=erro,
317:             )
318:             print(f"[{i}/{total}] FALHOU -> {nome} ({chat_id}): {erro}")
319: 
320:         if i < total:
321:             time.sleep(pausas[i - 1])
322: 
323:     print("Campanha finalizada.")
``````

## File: .gitignore
``````
 1: # Dados: o banco DuckDB É versionado (data/leads.duckdb).
 2: # Apenas artefatos transientes do DuckDB e saídas geradas ficam de fora.
 3: *.duckdb.wal
 4: *.duckdb.tmp
 5: *.xlsx
 6: *.csv
 7: *.log
 8: 
 9: # Segredos e configuração local (contém a API key da WAHA)
10: .env
11: 
12: # Sessões do WhatsApp (WAHA)
13: sessions/
14: 
15: # Ambientes Virtuais
16: venv/
17: env/
18: .venv/
19: 
20: # Python Cache
21: __pycache__/
22: *.py[cod]
23: *$py.class
24: 
25: # Configurações de IDE
26: .vscode/
27: .idea/
28: 
29: # Sistema Operacional
30: .DS_Store
31: Thumbs.db
``````

## File: README.md
``````markdown
  1: Documentação do Projeto: MAP SCRAPER
  2: 
  3: 1. Objetivo do Projeto
  4: 
  5:     Ferramenta automatizada e gratuita para prospecção de leads B2B locais que muitas vezes não possuem site, mas estão presentes no Google Maps e no Instagram.
  6: 
  7:     O sistema é capaz de receber um Estado e Cidade, descobrir os bairros de forma dinâmica, raspar os dados do Google Maps (Nome, Telefone, Instagram, Site) e gerenciar esses dados em um banco local, evitando duplicatas e permitindo o descarte de leads já trabalhados.
  8: 
  9: 2. Funcionalidades
 10: 
 11:     A ferramenta foi construída com uma arquitetura modular e conta com os seguintes recursos:
 12: 
 13:         - Busca Dinâmica de Localidades: Integração com a API do IBGE para listar Estados, Cidades e Distritos, gravando tudo em tabelas locais (cache) para não depender da rede nas próximas execuções. O nome digitado é confirmado no IBGE (aceita sem acento e em minúsculas) e o nome oficial é usado nas buscas. Complemento com Nominatim + Overpass (OpenStreetMap) para descobrir bairros quando o IBGE não cobre a cidade. Se nenhum bairro for encontrado, ele faz fallback buscando a cidade inteira.
 14: 
 15:         - Scraping em Multithreading: Uso do Playwright com ThreadPoolExecutor para abrir múltiplos navegadores simultaneamente e acelerar a coleta em diferentes bairros.
 16: 
 17:         - Cobertura por Bairros: A coleta é dividida por bairros para contornar a paginação do Google Maps e capturar mais leads por cidade.
 18: 
 19:         - Rolagem Dinâmica: A lista de resultados é rolada até esgotar (com limite de segurança), em vez de um número fixo de rolagens.
 20: 
 21:         - Robustez: Retry com backoff em erros transitórios, deduplicação intra-execução e salvamento incremental no DuckDB a cada área concluída.
 22: 
 23:         - Anti-bloqueio: User-Agent realista, viewport configurado e pausas aleatórias entre as requisições para reduzir o risco de bloqueio.
 24: 
 25:         - Tratamento de Dados (Data Cleansing):
 26: 
 27:         - Formatação automática de telefones para o padrão brasileiro (XX) XXXXX-XXXX.
 28: 
 29:         - Classificação automática do telefone: Celular (11 dígitos) ou Fixo (10 dígitos).
 30: 
 31:         - Banco de Dados Local (DuckDB): Armazenamento rápido e seguro em um arquivo local.
 32: 
 33:         - UPSERT: Se o lead já existe, ele atualiza os dados e a data de extração. Se for novo, insere.
 34: 
 35:         - Controle de Status: Leads podem ser marcados como ativo ou descartado. Se um lead descartado for encontrado novamente, o robô ignora e não atualiza.
 36: 
 37:         - Exportação para Excel: Gera um relatório limpo e ordenado apenas com os leads ativos.
 38: 
 39:         - Envio de WhatsApp (WAHA): Envia mensagens para os leads via WAHA (WhatsApp HTTP API). Só envia para leads ativos do tipo Celular (nunca fixo) e ainda não enviados, com intervalo configurável entre disparos para evitar spam. Cada envio é registrado em `status_whatsapp` e `data_envio_whatsapp`.
 40: 
 41:         - Base de Localidades Offline: estados, municípios e distritos do IBGE são gravados no próprio DuckDB (`localidades_estados`, `localidades_municipios`, `localidades_bairros`). Na primeira consulta de uma cidade os dados vêm da API; nas seguintes, tudo sai do banco, sem rede. A sincronização completa fica no menu (opção 3).
 42: 
 43:         - Tratamento de Captcha/Bloqueio: detecta a tela de "tráfego incomum" do Google Maps e aplica pausa longa antes de tentar novamente, além de um cooldown compartilhado que pausa todas as threads ao mesmo tempo. Se o bloqueio persistir, a área é abortada preservando os leads já coletados.
 44: 
 45: 3. Stack Tecnológica
 46: 
 47:     - Linguagem: Python 3.10+
 48:     - Scraping: Playwright (Chromium)
 49:     - Banco de Dados: DuckDB
 50:     - Manipulação de Dados: Pandas
 51:     - APIs: IBGE (Localidades), Nominatim e Overpass (Bairros)
 52:     - Tratamento: Regex (para telefones)
 53:     - WhatsApp: WAHA (WhatsApp HTTP API)
 54: 
 55: 4. Estrutura de Pastas
 56: 
 57:     map_scraper_project/
 58:     │
 59:     ├── data/                  # Onde o banco leads.duckdb é salvo
 60:     ├── memory/                # Memória do projeto para modelos de IA (ver seção 12)
 61:     ├── output/                # Onde os arquivos Excel finais são gerados
 62:     │
 63:     ├── src/                   # Código-fonte
 64:     │   ├── __init__.py        
 65:     │   ├── config.py          # Leitura centralizada do .env e flags
 66:     │   ├── database.py        # Lógica do DuckDB (UPSERT, status, exportação, log de envio)
 67:     │   ├── localidades_db.py  # Cache local das localidades (tabelas IBGE no DuckDB)
 68:     │   ├── locations.py       # IBGE + OSM (Nominatim/Overpass), com cache no banco
 69:     │   ├── scraper.py         # Robô Playwright, multithreading e anti-bloqueio
 70:     │   ├── utils.py           # Formatação de telefone (Fixo/Celular)
 71:     │   ├── whatsapp.py        # Envio via WAHA (WhatsApp HTTP API)
 72:     │   └── main.py            # Menu interativo e orquestração
 73:     │
 74:     ├── .env.example           # Modelo das variáveis de ambiente
 75:     ├── requirements.txt       # Dependências do projeto
 76:     └── README.md              # Este documento
 77: 
 78: 5. Como Usar (Manual do Usuário)
 79: 
 80:     Passo 1: Instalação
 81:     No terminal, dentro da pasta raiz do projeto, instale as dependências e o navegador do Playwright:
 82: 
 83:     python -m venv venv
 84:     .\venv\Scripts\Activate
 85:     python -m pip install -r requirements.txt
 86:     python -m playwright install chromium
 87:     Passo 2: Execução
 88:     Antes de rodar, crie o seu `.env` a partir do modelo:
 89: 
 90:     Copy-Item .env.example .env
 91: 
 92:     Rode o arquivo principal:
 93: 
 94:     python src/main.py
 95:     Passo 3: Interação no Terminal
 96:     O menu tem 5 opções:
 97: 
 98:     1 - Coletar leads: faz 5 perguntas simples (UF, Cidade, Nicho, Bairros automáticos, Ver navegador).
 99:     2 - Enviar mensagens WhatsApp: envia para os leads celulares pendentes (ver seção 7).
100:     3 - Sincronizar base de localidades (IBGE): baixa estados, municípios e distritos para o DuckDB (ver seção 8).
101:     4 - Aquecer bairros de uma UF (OpenStreetMap): resolve e grava os bairros de todas as cidades do estado (ver seção 8).
102:     5 - Sair.
103: 
104:     Passo 4: Resultados
105: 
106:         O banco de dados será atualizado (PostgreSQL ou DuckDB, conforme o .env).
107: 
108:         Um arquivo Excel será gerado em output/leads_nicho_cidade.xlsx.
109: 
110:     Execução em Docker (servidor, sem menu)
111: 
112:     Para rodar sozinho num servidor (coleta automática contínua), o projeto tem
113:     um Dockerfile e um docker-compose.yml. O container usa o runner
114:     `src/coleta_auto.py` (não-interativo), configurado por variáveis de ambiente:
115: 
116:     ```
117:     NICHO=barbearias          # nicho a coletar
118:     UFS=                      # vazio = todas as UFs do Brasil; ou RS,SP,RJ
119:     MAX_CIDADES=0             # 0 = todas as cidades de cada UF
120:     MAX_BAIRROS=30            # bairros por cidade
121:     AQUECER_BAIRROS=false     # resolver bairros antes da coleta
122:     SINCRONIZAR=false         # baixar IBGE antes (banco novo)
123:     LOOP=false                # true = rodar em loop contínuo
124:     LOOP_PAUSA_SEGUNDOS=3600  # pausa entre ciclos (LOOP=true)
125:     ```
126: 
127:     Subir e acompanhar:
128: 
129:     ```
130:     docker compose up -d --build
131:     docker compose logs -f app
132:     ```
133: 
134:     O `.env` é injetado no container via `env_file` (banco e WAHA). Os volumes
135:     `./data` e `./output` são montados para persistir DuckDB/Excel localmente.
136: 
137: 
138: 6. Gerenciamento do Banco de Dados (Regras de Negócio)
139: 
140:     Se você quiser descartar um lead para que ele não seja mais exportado e não seja atualizado nas próximas buscas, você pode rodar um comando SQL direto no DuckDB (via DBeaver ou script Python):
141: 
142:     sql
143:     -- Para descartar um lead
144:     UPDATE leads SET status = 'descartado' WHERE nome = 'Nome da Barbearia';
145: 
146:     -- Para reativar um lead
147:     UPDATE leads SET status = 'ativo' WHERE nome = 'Nome da Barbearia';
148:     Nota: A regra do UPSERT no database.py garante que, se o robô achar uma barbearia "descartada", ele pula ela e não sobrescreve seus dados no banco.
149: 
150: 7. Envio de WhatsApp (WAHA)
151: 
152:     Pré-requisito: uma instância WAHA rodando com um número conectado via QR Code.
153: 
154:     Configuração (arquivo .env na raiz do projeto):
155:     Copie .env.example para .env e preencha os valores.
156: 
157:     ```
158:     WAHA_API_URL=http://localhost:3000
159:     WAHA_API_KEY=SUA_CHAVE_AQUI
160:     WAHA_SESSION=default
161:     WAHA_ATIVO=true
162:     SOMENTE_ENVIO=false
163:     WAHA_INTERVALO=13
164:     WAHA_LIMITE=
165:     ```
166: 
167:     Flags de comportamento:
168:     - WAHA_ATIVO: se false, desliga o envio de WhatsApp (não tenta enviar).
169:     - SOMENTE_ENVIO: se true, pula a coleta e vai direto para o envio
170:       (equivalente a rodar `python src/main.py --so-enviar`).
171:     - WAHA_LIMITE: quantidade máxima de leads por campanha (vazio = sem limite).
172: 
173:     Regras de envio (evita spam):
174:     - Só envia para leads com status = 'ativo'.
175:     - Só envia para tipo_telefone = 'Celular' (fixos são ignorados).
176:     - Só envia para leads ainda não enviados (status_whatsapp = 'pendente' ou NULL).
177:     - Intervalo de WAHA_INTERVALO segundos entre envios.
178: 
179:     Logs no banco:
180:     - status_whatsapp: 'pendente', 'enviado' ou 'falhou'.
181:     - data_envio_whatsapp: gravada apenas quando o envio é bem-sucedido.
182: 
183:     A mensagem pode usar as variáveis {nome}, {bairro} e {cidade}.
184: 
185: 
186: 8. Base de Localidades Offline (IBGE)
187: 
188:     O projeto mantém um cache local das localidades no próprio DuckDB, criado na
189:     primeira consulta e reaproveitado nas seguintes (sem rede).
190: 
191:     Tabelas criadas automaticamente (guardam apenas o essencial):
192:     - localidades_estados: uf, nome
193:     - localidades_municipios: id_municipio, nome, uf + estado da coleta de bairros
194:     - localidades_bairros: id_municipio, nome, id_distrito
195: 
196:     Fontes (API de Localidades do IBGE):
197:     - Estados:    https://servicodados.ibge.gov.br/api/v1/localidades/estados
198:     - Municípios: https://servicodados.ibge.gov.br/api/v1/localidades/municipios
199:     - Distritos:  https://servicodados.ibge.gov.br/api/v1/localidades/distritos
200: 
201:     Configuração (.env):
202:     ```
203:     LOCALIDADES_USAR_CACHE=true
204:     LOCALIDADES_SALVAR=true
205:     LOCALIDADES_MIN_BAIRROS=3
206:     AQUECER_PAUSA_SEGUNDOS=2
207:     ```
208: 
209:     - LOCALIDADES_USAR_CACHE=true (padrão): consulta o banco primeiro e só chama a
210:       API quando o dado ainda não existe (e aí grava o resultado).
211:     - LOCALIDADES_USAR_CACHE=false: sempre busca na API do IBGE e atualiza a base
212:       local com o que voltou.
213:     - LOCALIDADES_SALVAR=false: modo somente leitura. Nada é gravado e nem as
214:       tabelas são criadas; o banco só é consultado. A sincronização do menu fica
215:       desativada.
216:     - LOCALIDADES_MIN_BAIRROS: mínimo de distritos do IBGE para a cidade ser
217:       considerada coberta. Abaixo disso, os bairros são complementados com o
218:       OpenStreetMap (Nominatim + Overpass) e o resultado também fica em cache.
219:     - AQUECER_PAUSA_SEGUNDOS: pausa entre cidades no aquecimento por UF, aplicada
220:       somente quando a cidade usou o OpenStreetMap.
221: 
222:     As duas flags são independentes:
223: 
224:     | USAR_CACHE | SALVAR | Comportamento |
225:     |---|---|---|
226:     | true  | true  | lê do banco; grava o que faltar (recomendado) |
227:     | false | true  | sempre vai à API e regrava tudo (força atualização) |
228:     | true  | false | só lê o banco; o que não existe vai à API sem gravar |
229:     | false | false | sempre à API, sem tocar no banco |
230: 
231:     O que acontece ao rodar de novo para a mesma cidade:
232: 
233:     - localidades_estados: UPSERT por uf (só atualiza o nome).
234:     - localidades_municipios: UPSERT por id_municipio (atualiza nome/uf e
235:       PRESERVA bairros_fonte / bairros_atualizado_em).
236:     - localidades_bairros: a lista da cidade é tratada como autoritativa. Nomes
237:       iguais são atualizados, nomes novos são inseridos e nomes que não vieram mais
238:       são removidos — mas apenas daquela cidade.
239:     - Sincronização completa (menu opção 3): aditiva. Ela insere/atualiza os
240:       distritos do IBGE sem apagar bairros que já existem, então listas
241:       complementadas pelo OpenStreetMap são preservadas.
242: 
243:     Rodar só para um estado também é seguro: obter_cidades(uf) grava apenas os
244:     municípios daquela UF, e nada de outras UFs é alterado.
245: 
246:     Sincronização completa: menu opção 3 (ou `sincronizar_base_localidades()`), que
247:     baixa de uma vez todos os estados, municípios e distritos (~10,7 mil registros).
248: 
249:     Aquecimento por UF: menu opção 4 (ou `aquecer_bairros_uf('RS')`). Resolve e
250:     grava os bairros de TODAS as cidades de um estado, sem raspar nenhum lead.
251:     Depois disso, a coleta por cidade não consulta mais IBGE/OSM.
252: 
253:     - Processa apenas as cidades com `bairros_fonte IS NULL` (ou seja, retoma de
254:       onde parou em execuções anteriores).
255:     - Cidades cobertas pelo IBGE são instantâneas; as demais usam o OpenStreetMap.
256:     - A pausa entre cidades (AQUECER_PAUSA_SEGUNDOS) é aplicada somente quando o
257:       OSM foi consultado — respeitando o limite de 1 req/s do Nominatim.
258:     - Ctrl+C interrompe sem perder o que já foi gravado; basta rodar de novo.
259:     - É possível limitar quantas cidades processar por execução.
260: 
261:     Importante: os "distritos" do IBGE são divisões administrativas e, em muitos
262:     municípios, resumem-se à própria sede. Por isso o fallback com o OSM continua
263:     existindo — a diferença é que ele roda uma única vez por cidade e o resultado
264:     é gravado no banco. Se o OSM estiver fora do ar, nada é gravado (a próxima
265:     execução tenta de novo) e a coleta segue com os distritos do IBGE.
266: 
267:     A API de Localidades do IBGE NÃO fornece bairros — apenas distritos e
268:     subdistritos. Exemplo real: Canoas-RS tem 1 distrito (a própria sede) e 0
269:     subdistritos, então o IBGE não contribui com áreas para essa cidade e o robô
270:     informa isso e segue para o OpenStreetMap:
271: 
272:     ```
273:     IBGE não publica bairros para Canoas-RS: o município tem apenas 1 distrito (a sede).
274:     Buscando bairros no OpenStreetMap...
275:     ```
276: 
277:     Cidades com vários distritos (São Paulo: 96, Campinas: 7) usam o IBGE e não
278:     consultam o OSM. Das 5.571 cidades do país, 643 têm distritos suficientes.
279: 
280:     Como a cidade é resolvida: o nome digitado é comparado sem acento e sem
281:     diferenciar maiúsculas ("canoas", "sao leopoldo") com a lista do IBGE, e o nome
282:     oficial é exibido e usado no scraping, no banco e no Excel:
283: 
284:     ```
285:     Digite o nome da cidade: canoas
286:     Município (IBGE): Canoas-RS | código 4304606
287:     ```
288: 
289:     Para forçar a atualização de uma cidade já gravada, limpe a marca:
290:     ```sql
291:     UPDATE localidades_municipios SET bairros_fonte = NULL WHERE nome = 'Porto Alegre';
292:     ```
293: 
294: 9. Anti-bloqueio / Captcha (Google Maps)
295: 
296:     Quando o Google responde com a tela de "tráfego incomum" (captcha), o robô:
297:     1. detecta o bloqueio (URL /sorry/, formulários de captcha ou textos típicos);
298:     2. aplica um cooldown global, pausando TODAS as threads ao mesmo tempo;
299:     3. espera a pausa longa e tenta novamente até CAPTCHA_MAX_TENTATIVAS;
300:     4. se o bloqueio persistir, aborta apenas aquela área, preservando os leads
301:        já extraídos (que continuam sendo salvos incrementalmente).
302: 
303:     Configuração (.env):
304:     ```
305:     CAPTCHA_MAX_TENTATIVAS=2
306:     CAPTCHA_PAUSA_SEGUNDOS=300
307:     CAPTCHA_PAUSA_GLOBAL_SEGUNDOS=180
308:     ```
309: 
310:     - CAPTCHA_MAX_TENTATIVAS: tentativas por página antes de abortar a área.
311:     - CAPTCHA_PAUSA_SEGUNDOS: pausa longa da thread que levou o bloqueio.
312:     - CAPTCHA_PAUSA_GLOBAL_SEGUNDOS: pausa compartilhada entre as threads.
313: 
314:     A resolução automática de captcha por serviço externo (2Captcha, CapMonster
315:     etc.) não está implementada — o comportamento padrão é pausar e desistir da
316:     área em vez de insistir. Em coletas muito grandes, aumente as pausas acima.
317: 
318: 10. commit forçado
319: 
320:     git add -A; git commit -m "sync local $(Get-Date -Format 'yyyy-MM-dd HH:mm')"; git push --force-with-lease origin main
321: 
322: 11. Próximos Passos (Melhorias Futuras)
323: 
324:     Já implementado:
325:     - Base de localidades offline no DuckDB (estados, municípios e distritos do IBGE).
326:     - Detecção de captcha com pausa longa e cooldown compartilhado entre threads.
327: 
328:     Pendências sugeridas:
329:     - Resolução automática de captcha: integrar um serviço (2Captcha/CapMonster) para
330:       coletas muito grandes, hoje o robô apenas pausa e desiste da área.
331: 
332:     - Enriquecimento de E-mail: Criar um script secundário que lê os sites encontrados e busca e-mails de contato (usando Regex).
333: 
334: 
335: 12. Memória do Projeto para IA (pasta memory/)
336: 
337:     A pasta `memory/` reúne documentação resumida e densa, pensada para ser lida
338:     por modelos de IA antes de alterar o código (economiza contexto/custo).
339: 
340:     Ordem de leitura:
341:     1. memory/00-resumo-projeto.md        -> objetivo, stack e estrutura
342:     2. memory/01-arquitetura-e-modulos.md -> módulos, funções e fluxos
343:     3. memory/02-decisoes-e-armadilhas.md -> decisões, bugs conhecidos, cuidados
344:     4. memory/03-historico-de-mudancas.md -> o que mudou e o que ficou pendente
345:     5. memory/04-como-contribuir.md       -> padrões de código, logs, testes e docs
346: 
347:     Regras: manter os arquivos curtos, registrar o "porquê" das decisões e nunca
348:     colocar segredos ali (API keys ficam apenas no `.env`).
349: 
350: 
351: 13. Observação sobre configuração
352: 
353:     O modelo completo e comentado de todas as variáveis está em `.env.example`.
354:     Cada item traz a faixa de valores e o efeito colateral. Comentários devem
355:     ficar em linha própria; comentário na mesma linha do valor é lido como parte
356:     do valor.
``````

## File: src/main.py
``````python
  1: # src/main.py
  2: import sys
  3: import os
  4: 
  5: sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
  6: 
  7: from src.locations import (
  8:     obter_estados,
  9:     obter_cidades,
 10:     obter_termos_busca,
 11:     obter_municipio,
 12:     filtrar_cidades,
 13:     sincronizar_base_localidades,
 14:     listar_municipios_pendentes,
 15:     aquecer_bairros_uf,
 16:     SALVAR as LOCALIDADES_SALVAR,
 17: )
 18: from src.scraper import rodar_scraper_multithread
 19: from src.database import LeadDatabase
 20: from src.whatsapp import (
 21:     disparar_campanha,
 22:     enviar_texto_numero,
 23:     WAHA_INTERVALO,
 24:     WAHA_LIMITE,
 25:     WAHA_ATIVO,
 26:     SOMENTE_ENVIO,
 27: )
 28: 
 29: 
 30: def coletar_leads():
 31:     df_estados = obter_estados()
 32:     if df_estados.empty:
 33:         return
 34: 
 35:     uf_escolhida = input("Digite a UF (ex: RS, SP, RJ): ").strip().upper()
 36:     if uf_escolhida not in df_estados['uf'].values:
 37:         print("UF inválida.")
 38:         return
 39: 
 40:     cidades = obter_cidades(uf_escolhida)
 41:     termo_cidade = input("Digite o nome da cidade: ").strip()
 42:     cidades_filtradas = filtrar_cidades(cidades, termo_cidade)
 43: 
 44:     if not cidades_filtradas:
 45:         print("Cidade não encontrada.")
 46:         return
 47:     elif len(cidades_filtradas) > 1:
 48:         cidade_escolhida = input(
 49:             f"Várias encontradas ({', '.join(cidades_filtradas[:3])}...). Digite o nome exato: "
 50:         ).strip()
 51:         exatos = filtrar_cidades(cidades, cidade_escolhida)
 52:         cidade_escolhida = exatos[0] if exatos else cidade_escolhida
 53:     else:
 54:         cidade_escolhida = cidades_filtradas[0]
 55: 
 56:     # Confirma o município no IBGE e passa a usar o nome oficial (com acentos).
 57:     municipio = obter_municipio(cidade_escolhida, uf_escolhida)
 58:     if municipio:
 59:         cidade_escolhida = municipio["nome"]
 60:         print(f"Município (IBGE): {cidade_escolhida}-{uf_escolhida} | código {municipio['id_municipio']}")
 61:     else:
 62:         print(f"Aviso: {cidade_escolhida}-{uf_escolhida} não foi confirmado no IBGE.")
 63: 
 64:     nicho = input(f"\nQual o nicho para {cidade_escolhida}-{uf_escolhida}? ").strip().lower()
 65: 
 66:     termos_busca = obter_termos_busca(cidade_escolhida, uf_escolhida)
 67: 
 68:     mostrar_navegador = input("\nVer o navegador? (S/N): ").strip().upper() == 'S'
 69: 
 70:     print("\nIniciando extração...")
 71:     db = LeadDatabase()
 72: 
 73:     df_resultados = rodar_scraper_multithread(
 74:         nicho=nicho,
 75:         cidade=cidade_escolhida,
 76:         uf=uf_escolhida,
 77:         termos_lista=termos_busca,
 78:         mostrar_navegador=mostrar_navegador,
 79:         save_callback=db.save_leads,  # salvamento incremental (UPSERT) a cada área concluída
 80:     )
 81: 
 82:     if not df_resultados.empty:
 83:         print("\nLeads salvos incrementalmente no DuckDB (UPSERT).")
 84:         db.export_to_excel(nicho, cidade_escolhida)
 85:     else:
 86:         print("Nenhum dado extraído.")
 87: 
 88:     db.close()
 89: 
 90: 
 91: def _confirmar(texto):
 92:     """Pergunta S/N e retorna True para respostas afirmativas."""
 93:     return input(texto).strip().upper() in ("S", "SIM", "Y", "YES")
 94: 
 95: 
 96: def _escolher_template(templates):
 97:     """Lista os templates ativos e retorna a mensagem escolhida pelo usuário."""
 98:     print("\nTemplates ativos:")
 99:     for t in templates:
100:         segmento = t.get("segmento")
101:         sufixo = f"  [{segmento}]" if segmento else ""
102:         print(f"  {t['id']} - {t['descricao']}{sufixo}")
103: 
104:     escolha = input("Escolha o template (Enter = primeiro): ").strip()
105:     if not escolha:
106:         return templates[0]["mensagem"]
107: 
108:     for t in templates:
109:         if str(t["id"]) == escolha:
110:             return t["mensagem"]
111: 
112:     print("Opção inválida. Usando o primeiro template.")
113:     return templates[0]["mensagem"]
114: 
115: 
116: def _escolher_filtros():
117:     """Pergunta os filtros de envio; Enter = sem filtro (todos os leads)."""
118:     print("\n=== FILTROS DE ENVIO ===")
119:     print("0 - Todos (sem filtro)")
120:     print("1 - Por número")
121:     print("2 - Por cidade")
122:     print("3 - Por nicho")
123:     opcao = input("Escolha um filtro (Enter = 0): ").strip() or "0"
124: 
125:     numero = cidade = nicho = None
126:     if opcao == "1":
127:         numero = input("Número (completo ou parte): ").strip() or None
128:     elif opcao == "2":
129:         cidade = input("Cidade: ").strip() or None
130:     elif opcao == "3":
131:         nicho = input("Nicho: ").strip() or None
132:     elif opcao != "0":
133:         print("Opção inválida. Usando 'Todos'.")
134:     return numero, cidade, nicho
135: 
136: 
137: def testar_envio(db, mensagem, pendentes=None):
138:     """Envia um teste para um número digitado ou para um lead pendente.
139: 
140:     `pendentes` (opcional): DataFrame já filtrado; se None, busca até 10 pendentes.
141:     """
142:     print("\n--- TESTE DE ENVIO ---")
143:     print("1 - Digitar um número de teste")
144:     print("2 - Escolher um lead pendente")
145:     opcao = input("Escolha: ").strip()
146: 
147:     numero = None
148:     if opcao == "1":
149:         numero = input("Digite o número com DDD (ex: 51999998888): ").strip()
150:     elif opcao == "2":
151:         if pendentes is None:
152:             pendentes = db.get_leads_para_envio(limite=10)
153:         if pendentes.empty:
154:             print("Nenhum lead pendente para testar.")
155:             return
156:         amostra = pendentes.head(10)
157:         print("Leads pendentes:")
158:         for i, (_, lead) in enumerate(amostra.iterrows(), 1):
159:             print(f"  {i} - {lead['nome']} ({lead['telefone']})")
160:         escolha = input("Escolha o número do lead: ").strip()
161:         if not escolha.isdigit() or not (1 <= int(escolha) <= len(amostra)):
162:             print("Escolha inválida.")
163:             return
164:         numero = amostra.iloc[int(escolha) - 1]["telefone"]
165:     else:
166:         print("Opção inválida.")
167:         return
168: 
169:     if not numero:
170:         print("Nenhum número informado.")
171:         return
172: 
173:     try:
174:         enviar_texto_numero(numero, mensagem)
175:         print(f"✅ Teste enviado para {numero}")
176:     except Exception as e:
177:         print(f"❌ Falha no teste para {numero}: {e}")
178: 
179: 
180: def enviar_whatsapp_menu():
181:     print("\n=== ENVIO WHATSAPP (WAHA) ===")
182: 
183:     if not WAHA_ATIVO:
184:         print("Envio de WhatsApp desativado (WAHA_ATIVO=false no .env).")
185:         return
186: 
187:     db = LeadDatabase()
188: 
189:     templates = db.listar_templates_ativos()
190:     if not templates:
191:         print("Nenhum template ativo. Cadastre um template na tabela templates_whatsapp.")
192:         db.close()
193:         return
194: 
195:     mensagem = _escolher_template(templates)
196: 
197:     numero_f, cidade_f, nicho_f = _escolher_filtros()
198: 
199:     # Busca todos os pendentes (sem limitar ainda) para mostrar o total disponível.
200:     pendentes = db.get_leads_para_envio(numero=numero_f, cidade=cidade_f, nicho=nicho_f)
201: 
202:     if _confirmar("Deseja fazer um envio de teste antes? (S/N): "):
203:         testar_envio(db, mensagem, pendentes=pendentes)
204: 
205:     if pendentes.empty:
206:         print("Nenhum lead celular pendente de envio (com os filtros aplicados).")
207:         db.close()
208:         return
209: 
210:     total_disponivel = len(pendentes)
211:     print(f"\n{total_disponivel} lead(s) celular(es) pendentes (fixos são ignorados).")
212: 
213:     # Quantidade (range): Enter = todos (respeitando o limite do .env, se houver).
214:     if WAHA_LIMITE:
215:         print(f"Limite configurado no .env: {WAHA_LIMITE} lead(s) por campanha.")
216:         padrao = WAHA_LIMITE
217:     else:
218:         padrao = total_disponivel
219: 
220:     entrada = input(
221:         f"Quantos leads enviar? (Enter = {padrao}): "
222:     ).strip()
223: 
224:     if entrada:
225:         if entrada.isdigit() and int(entrada) > 0:
226:             quantidade = int(entrada)
227:         else:
228:             print("Valor inválido. Usando o padrão.")
229:             quantidade = padrao
230:     else:
231:         quantidade = padrao
232: 
233:     if WAHA_LIMITE and quantidade > WAHA_LIMITE:
234:         print(f"Ajustando para o limite do .env ({WAHA_LIMITE}).")
235:         quantidade = WAHA_LIMITE
236: 
237:     quantidade = min(quantidade, total_disponivel)
238:     pendentes = pendentes.head(quantidade)
239: 
240:     if not _confirmar(f"Enviar para {len(pendentes)} lead(s)? (S/N): "):
241:         print("Envio cancelado.")
242:         db.close()
243:         return
244: 
245:     disparar_campanha(
246:         db,
247:         mensagem_template=mensagem,
248:         intervalo=WAHA_INTERVALO,
249:         limite=quantidade,
250:         leads=pendentes,
251:     )
252:     db.close()
253: 
254: 
255: def aquecer_bairros_menu():
256:     """Prepara o cache de bairros de uma UF inteira (sem raspar leads)."""
257:     print("\n=== AQUECER BAIRROS DE UMA UF ===")
258: 
259:     if not LOCALIDADES_SALVAR:
260:         print("LOCALIDADES_SALVAR=false: o aquecimento está desativado.")
261:         print("Ative a flag LOCALIDADES_SALVAR no .env para gravar os bairros.")
262:         return
263: 
264:     print("Resolve e grava os bairros de todas as cidades da UF, uma única vez.")
265:     print("Depois disso a coleta por cidade não consulta mais IBGE/OSM.")
266: 
267:     df_estados = obter_estados()
268:     if df_estados.empty:
269:         print("Não foi possível obter a lista de estados.")
270:         return
271: 
272:     uf = input("Digite a UF (ex: RS, SP, RJ): ").strip().upper()
273:     if uf not in df_estados['uf'].values:
274:         print("UF inválida.")
275:         return
276: 
277:     print(f"\nVerificando quais cidades de {uf} ainda precisam de bairros...")
278:     pendentes = listar_municipios_pendentes(uf)
279:     if not pendentes:
280:         print(f"Todas as cidades de {uf} já estão na base local. Nada a fazer.")
281:         return
282: 
283:     print(f"{len(pendentes)} cidade(s) pendente(s) em {uf}.")
284:     print("As cidades cobertas pelo IBGE são instantâneas; as demais usam o")
285:     print("OpenStreetMap (Nominatim + Overpass), com pausa entre elas.")
286: 
287:     limite = input("Quantas cidades processar agora? (Enter = todas): ").strip()
288:     max_cidades = 0
289:     if limite:
290:         try:
291:             max_cidades = max(1, int(limite))
292:         except ValueError:
293:             print("Valor inválido. Usando todas.")
294:             max_cidades = 0
295: 
296:     previstas = min(max_cidades, len(pendentes)) if max_cidades else len(pendentes)
297:     confirmar = input(f"Processar {previstas} cidade(s)? (S/N): ").strip().upper()
298:     if confirmar != 'S':
299:         print("Operação cancelada.")
300:         return
301: 
302:     aquecer_bairros_uf(uf, cidades=pendentes, max_cidades=max_cidades)
303: 
304: 
305: def menu_interativo():
306:     # Flag de linha de comando: `python src/main.py --so-enviar` pula a coleta
307:     # e vai direto para o envio (equivale a SOMENTE_ENVIO=true no .env).
308:     so_enviar_cli = "--so-enviar" in sys.argv
309: 
310:     if SOMENTE_ENVIO or so_enviar_cli:
311:         enviar_whatsapp_menu()
312:         return
313: 
314:     while True:
315:         print("\n=== MAP SCRAPER ===")
316:         print("1 - Coletar leads")
317:         print("2 - Enviar mensagens WhatsApp")
318:         print("3 - Sincronizar base de localidades (IBGE)")
319:         print("4 - Aquecer bairros de uma UF (OpenStreetMap)")
320:         print("5 - Sair")
321:         opcao = input("Escolha uma opção: ").strip()
322: 
323:         if opcao == "1":
324:             coletar_leads()
325:         elif opcao == "2":
326:             enviar_whatsapp_menu()
327:         elif opcao == "3":
328:             sincronizar_base_localidades()
329:         elif opcao == "4":
330:             aquecer_bairros_menu()
331:         elif opcao == "5":
332:             print("Até mais!")
333:             break
334:         else:
335:             print("Opção inválida.")
336: 
337: 
338: if __name__ == "__main__":
339:     menu_interativo()
``````


# Git Diffs
## Git Diffs Working Tree
``````diff
diff --git a/.env.example b/.env.example
index 9c2506d..f1bccf6 100644
--- a/.env.example
+++ b/.env.example
@@ -14,6 +14,38 @@
 # =============================================================================
 
 
+# =============================================================================
+# BANCO DE DADOS — engine independente (PostgreSQL ou DuckDB)
+# =============================================================================
+
+# Qual banco usar?
+#   duckdb    = banco local (arquivo DUCKDB_PATH). Bom para rodar offline.
+#   postgres  = banco externo PostgreSQL (DATABASE_URL).
+# Se você DEIXAR ESTA LINHA COMENTADA, o sistema decide sozinho:
+#   - se DUCKDB_PATH estiver definido -> usa DuckDB
+#   - senão, se DATABASE_URL estiver definido -> usa PostgreSQL
+DB_ENGINE=postgres
+
+# ---- Opção 1: PostgreSQL (banco externo) ----------------------------------
+# URL de conexão: postgresql://usuario:senha@host:porta/banco
+# ATENÇÃO: se a senha tiver caracteres especiais (@, :, /), "percent-encode":
+#   @ -> %40
+DATABASE_URL=postgresql://usuario:senha@localhost:5432/leads_db
+
+# ---- Opção 2: DuckDB (banco local, para rodar offline) ---------------------
+# Para usar o DuckDB, comente/remova o DATABASE_URL acima e descomente a linha:
+#DUCKDB_PATH=data/leads.duckdb
+
+# ---- Configuração antiga (referência) --------------------------------------
+# As variáveis abaixo foram substituídas por DATABASE_URL. Funcionam se você
+# comentar/remover o DATABASE_URL E definir DB_ENGINE=postgres.
+#DB_HOST=localhost
+#DB_PORT=5432
+#DB_NAME=leads_db
+#DB_USER=leads_app
+#DB_PASSWORD=
+
+
 # =============================================================================
 # WHATSAPP - WAHA (WhatsApp HTTP API)
 # =============================================================================
@@ -43,9 +75,15 @@ WAHA_ATIVO=true
 SOMENTE_ENVIO=false
 
 # Pausa em SEGUNDOS entre um envio e o próximo (13s ≈ 4-5 mensagens por minuto).
-# Pausas muito curtas aumentam o risco de banimento do número.
+# Usado APENAS quando WAHA_CADENCIA está vazio (pausa fixa).
 WAHA_INTERVALO=13
 
+# Cadência de envio (anti-bloqueio): "X a cada Y segundos".
+# Ex.: WAHA_CADENCIA=3:60  -> 3 envios por minuto, com intervalos ALEATÓRIOS
+# (não manda de 15 em 15 segundos fixos). Tem prioridade sobre WAHA_INTERVALO.
+# Deixe vazio para usar a pausa fixa do WAHA_INTERVALO.
+WAHA_CADENCIA=
+
 # Quantidade máxima de leads por campanha. Vazio = sem limite (envia todos
 # os pendentes). Só conta leads celulares, ativos e ainda não enviados.
 WAHA_LIMITE=
@@ -108,3 +146,47 @@ CAPTCHA_PAUSA_SEGUNDOS=300
 # Pausa compartilhada em SEGUNDOS aplicada a TODAS as threads assim que uma
 # delas detecta bloqueio (evita que as outras continuem martelando o Google).
 CAPTCHA_PAUSA_GLOBAL_SEGUNDOS=180
+
+
+# =============================================================================
+# COLETA AUTOMÁTICA (rodar em servidor/container, sem menu)
+# -----------------------------------------------------------------------------
+# Usadas pelo runner `python src/coleta_auto.py` (não-interativo). O Docker
+# Compose já injeta estas variáveis com valores padrão; sobrescreva aqui ou no
+# docker-compose.yml conforme necessário.
+# =============================================================================
+
+# Nicho a coletar no modo automático.
+NICHO=barbearias
+
+# UFs a coletar, separadas por vírgula. Vazio = TODAS as UFs do Brasil.
+# Exemplo: UFS=RS,SP,RJ
+UFS=
+
+# Quantidade máxima de cidades por UF. 0 = todas.
+MAX_CIDADES=0
+
+# Quantidade máxima de bairros usados por cidade na busca (0 não é válido).
+MAX_BAIRROS=30
+
+# Pré-resolver (aquecer) os bairros da UF inteira antes de coletar?
+#   true  = resolve e grava todos os bairros da UF antes (pode demorar).
+#   false = resolve os bairros de cada cidade na hora da coleta (padrão).
+AQUECER_BAIRROS=false
+
+# Baixar estados/municípios/distritos do IBGE antes de coletar?
+#   true  = útil em banco novo (DuckDB local). No PostgreSQL já populado, deixe
+#           false para não rebaixar tudo do IBGE.
+SINCRONIZAR=false
+
+# Mostrar o navegador (Chromium) durante a coleta. Em servidor use false.
+MOSTRAR_NAVEGADOR=false
+
+# Gerar Excel por cidade ao final de cada coleta (true/false).
+EXPORTAR_EXCEL=false
+
+# Rodar em loop contínuo (true) ou executar um único ciclo (false).
+LOOP=false
+
+# Pausa (segundos) entre ciclos quando LOOP=true.
+LOOP_PAUSA_SEGUNDOS=3600
diff --git a/README.md b/README.md
index 68a5769..2bf11cf 100644
--- a/README.md
+++ b/README.md
@@ -103,10 +103,37 @@ Documentação do Projeto: MAP SCRAPER
 
     Passo 4: Resultados
 
-        O banco de dados será atualizado em data/leads.duckdb.
+        O banco de dados será atualizado (PostgreSQL ou DuckDB, conforme o .env).
 
         Um arquivo Excel será gerado em output/leads_nicho_cidade.xlsx.
 
+    Execução em Docker (servidor, sem menu)
+
+    Para rodar sozinho num servidor (coleta automática contínua), o projeto tem
+    um Dockerfile e um docker-compose.yml. O container usa o runner
+    `src/coleta_auto.py` (não-interativo), configurado por variáveis de ambiente:
+
+    ```
+    NICHO=barbearias          # nicho a coletar
+    UFS=                      # vazio = todas as UFs do Brasil; ou RS,SP,RJ
+    MAX_CIDADES=0             # 0 = todas as cidades de cada UF
+    MAX_BAIRROS=30            # bairros por cidade
+    AQUECER_BAIRROS=false     # resolver bairros antes da coleta
+    SINCRONIZAR=false         # baixar IBGE antes (banco novo)
+    LOOP=false                # true = rodar em loop contínuo
+    LOOP_PAUSA_SEGUNDOS=3600  # pausa entre ciclos (LOOP=true)
+    ```
+
+    Subir e acompanhar:
+
+    ```
+    docker compose up -d --build
+    docker compose logs -f app
+    ```
+
+    O `.env` é injetado no container via `env_file` (banco e WAHA). Os volumes
+    `./data` e `./output` são montados para persistir DuckDB/Excel localmente.
+
 
 6. Gerenciamento do Banco de Dados (Regras de Negócio)
 
diff --git a/data/leads.duckdb b/data/leads.duckdb
index 9afd0c3..a1b656b 100644
Binary files a/data/leads.duckdb and b/data/leads.duckdb differ
diff --git a/memory/00-resumo-projeto.md b/memory/00-resumo-projeto.md
index 8e4dbf2..63df724 100644
--- a/memory/00-resumo-projeto.md
+++ b/memory/00-resumo-projeto.md
@@ -1,14 +1,14 @@
 # 00 — Resumo do Projeto
 
-**Map Scraper** — ferramenta local de prospecção de leads B2B a partir do Google Maps.
+**Map Scraper** — ferramenta de prospecção de leads B2B a partir do Google Maps.
 
 - **Entrada:** UF + cidade + nicho (ex.: `RS`, `Canoas`, `barbearias`).
 - **Processo:** divide a busca por bairros, raspa o Google Maps com Playwright em
   multithread e extrai nome, telefone, Instagram e site.
-- **Saída:** leads no DuckDB (`data/leads.duckdb`) + Excel em `output/`.
+- **Saída:** leads num banco (PostgreSQL **ou** DuckDB) + Excel em `output/`.
 - **Extra:** dispara mensagens de WhatsApp via WAHA para leads já coletados, com
-  templates reutilizáveis, filtros (número/cidade/nicho), teste de envio e cache
-  do chatId resolvido (`@lid`/`@c.us`).
+  templates reutilizáveis, filtros (número/cidade/nicho), teste de envio, cache
+  do chatId resolvido (`@lid`/`@c.us`) e **cadência aleatória** anti-bloqueio.
 
 ## Fluxo de alto nível
 
@@ -19,7 +19,7 @@ menu (src/main.py)
                   → database.LeadDatabase.save_leads (UPSERT incremental)
                   → database.export_to_excel
   └─ 2 WhatsApp   → template ativo → filtros → teste → database.get_leads_para_envio
-                  → whatsapp.disparar_campanha (WAHA, chatId via checkNumberStatus)
+                  → whatsapp.disparar_campanha (WAHA, cadência aleatória)
   └─ 3 Sincronizar localidades (IBGE) → locations.sincronizar_base_localidades
   └─ 4 Aquecer bairros de uma UF       → locations.aquecer_bairros_uf
   └─ 5 Sair
@@ -31,7 +31,7 @@ menu (src/main.py)
 |---|---|
 | Linguagem | Python 3.10+ (ambiente: `venv/`) |
 | Scraping | Playwright (Chromium) + ThreadPoolExecutor |
-| Banco | DuckDB (arquivo único, 1 processo por vez) |
+| Banco | **PostgreSQL (externo) ou DuckDB (local)** — via `src/backend.py` |
 | Dados | Pandas |
 | Localidades | API IBGE + Nominatim/Overpass (OpenStreetMap) |
 | WhatsApp | WAHA (WhatsApp HTTP API) |
@@ -41,17 +41,19 @@ menu (src/main.py)
 
 ```
 map_scraper_project/
-├── data/          leads.duckdb (+ .wal transiente, ignorado no Git)
+├── data/          leads.duckdb (usado quando DB_ENGINE=duckdb)
 ├── memory/        esta documentação para IA
 ├── output/        Excel gerado (ignorado no Git)
 ├── src/
-│   ├── config.py          loader do .env + helpers (bool/int)
-│   ├── database.py        LeadDatabase: leads, templates_whatsapp, UPSERT, Excel, log WAHA
-│   ├── localidades_db.py  cache IBGE em DuckDB (tabelas localidades_*)
+│   ├── config.py          loader do .env + escolha do backend (DB_ENGINE)
+│   ├── backend.py         abstração PostgreSQL/DuckDB (conexão, SQL, bulk upsert)
+│   ├── database.py        LeadDatabase: leads, templates, log WAHA (via backend)
+│   ├── localidades_db.py  cache IBGE (via backend)
 │   ├── locations.py       IBGE + OSM + cache; sync e aquecimento por UF
 │   ├── scraper.py         Playwright, multithread, anti-captcha
+│   ├── schema.py          DDL + seed + migração (setup: python src/schema.py)
 │   ├── utils.py           formatar_telefone → (telefone, tipo, link wa)
-│   ├── whatsapp.py        envio via WAHA
+│   ├── whatsapp.py        envio via WAHA + cadência aleatória
 │   └── main.py            menu interativo
 ├── .env / .env.example
 ├── requirements.txt
@@ -62,11 +64,13 @@ map_scraper_project/
 
 | Versionado | Ignorado |
 |---|---|
-| `data/leads.duckdb` | `.env` (segredos) |
-| `src/`, `memory/`, `README.md` | `*.duckdb.wal`, `*.duckdb.tmp` |
+| `src/`, `memory/`, `README.md` | `.env` (segredos) |
 | `.env.example` | `*.xlsx`, `*.csv`, `*.log` |
 | | `venv/`, `__pycache__/`, `sessions/` |
 
+> `data/leads.duckdb` é o banco local (modo `DB_ENGINE=duckdb`). O banco externo
+> PostgreSQL (modo `DB_ENGINE=postgres`) fica no servidor e não é versionado.
+
 Comando de sync usado pelo mantenedor (sobrescreve o remoto):
 
 ```powershell
diff --git a/memory/01-arquitetura-e-modulos.md b/memory/01-arquitetura-e-modulos.md
index 15309a3..a169bb2 100644
--- a/memory/01-arquitetura-e-modulos.md
+++ b/memory/01-arquitetura-e-modulos.md
@@ -17,17 +17,49 @@ env_int(nome, padrao)           # inteiro com fallback
 PROJETO_RAIZ, CAMINHO_ENV
 ```
 
-> `src/whatsapp.py` chama `carregar_env()` no import (herança histórica).
-> `src/locations.py` e `src/scraper.py` dependem disso para ler suas flags.
+**Escolha do banco (engine independente):**
+
+```python
+DB_ENGINE        # 'postgres' ou 'duckdb' (inferido se vazio)
+DATABASE_URL     # postgresql://usuario:senha@host:porta/banco
+DUCKDB_PATH      # caminho do DuckDB local (default data/leads.duckdb)
+DB_HOST/DB_PORT/DB_NAME/DB_USER/DB_PASSWORD  # forma separada (legado)
+```
+
+Inferência de `DB_ENGINE` quando não definido: `DUCKDB_PATH` definido → duckdb;
+senão `DATABASE_URL` definido → postgres; senão → duckdb (padrão offline).
+
+---
+
+## src/backend.py — abstração de banco
+
+Camada única que conhece `duckdb` e `psycopg2` (os demais módulos **não** os
+importam). Expõe:
+
+```python
+IS_DUCKDB            # bool
+ph()                 # placeholder: '?' (duckdb) ou '%s' (postgres)
+conectar()           # abre conexão com o backend configurado
+commit(conn) / close(conn)
+execute(conn, sql, params)
+query_df(conn, sql, params)      # -> DataFrame
+query_one(conn, sql, params)     # -> tupla | None
+query_all(conn, sql, params)     # -> lista de tuplas
+df_to_rows(df)                   # DataFrame -> tuplas (NaN -> None)
+bulk_upsert(conn, table, columns, rows, conflict, set_clause)
+```
+
+`bulk_upsert` monta `INSERT ... VALUES ... ON CONFLICT (...) DO UPDATE ...` com
+multi-linhas, usando `excluded.col` (funciona nos dois bancos).
 
 ---
 
 ## src/localidades_db.py — cache de localidades
 
-Acesso ao **mesmo** `data/leads.duckdb`. **Abre e fecha conexão a cada operação**,
-para não segurar o arquivo durante o scraping (DuckDB permite só 1 processo).
+Usa `src/backend.py` (funciona em PostgreSQL ou DuckDB). **Abre e fecha conexão
+a cada operação**, para não segurar o banco durante o scraping.
 
-Tabelas (criadas automaticamente quando `CRIAR_TABELAS = True`):
+Tabelas:
 
 | Tabela | Colunas |
 |---|---|
@@ -40,7 +72,6 @@ Tabelas (criadas automaticamente quando `CRIAR_TABELAS = True`):
 Funções:
 
 ```python
-conexao(db_path=None)              # contextmanager; DDL se CRIAR_TABELAS
 ler_estados() / salvar_estados(registros)
 ler_municipios(uf)                 # inclui bairros_fonte (necessário p/ cache hit)
 ler_municipios_pendentes(uf)       # bairros_fonte IS NULL
@@ -49,7 +80,7 @@ buscar_municipio(cidade, uf)       # dict ou None
 ler_bairros(id_municipio) / salvar_bairros(id_municipio, registros, fonte)
 salvar_distritos_bulk(distritos, min_bairros=3)   # aditivo
 estatisticas()                     # dict com contagens
-CacheIndisponivel                  # exceção (arquivo travado / tabela ausente)
+CacheIndisponivel                  # exceção (servidor fora / conexão falhou)
 ```
 
 **Semânticas importantes**
@@ -158,12 +189,12 @@ Flags: `CAPTCHA_MAX_TENTATIVAS` (2), `CAPTCHA_PAUSA_SEGUNDOS` (300),
 
 ## src/database.py — leads
 
-`LeadDatabase(db_path="data/leads.duckdb")`
+`LeadDatabase(conn=None)` — usa `src/backend.py` (PostgreSQL ou DuckDB).
 
-Tabela `leads` — PK (`nome`, `cidade`):
+Tabela `leads` — PK `lead_id`, UNIQUE (`nome`, `cidade`):
 
 ```
-nome, telefone, tipo_telefone, whatsapp_link, instagram, site,
+lead_id, nome, telefone, tipo_telefone, whatsapp_link, instagram, site,
 bairro, cidade, estado, nicho, status (default 'ativo'),
 data_extracao, data_envio_whatsapp, status_whatsapp (default 'pendente'),
 chat_id_waha
@@ -172,13 +203,21 @@ chat_id_waha
 - `chat_id_waha`: cache do chatId resolvido pela WAHA (ex.: `143172869029943@lid`).
   Preenchido na primeira resolução; evita chamar `/api/checkNumberStatus` de novo.
 
-Tabela `templates_whatsapp` (criada e seedada no `__init__`):
+Tabela `templates_whatsapp`:
 
 ```
-id INTEGER PK, mensagem, descricao, ativo BOOLEAN (default TRUE)
+id PK, mensagem, descricao, segmento, ativo BOOLEAN (default TRUE)
 ```
 
-- Seed idempotente do template "Apresentação Agendamento Já" (`id=1`).
+- Seed do template "Apresentação Agendamento Já" (segmento `barbearias`) é feito
+  em `schema.py`, **não** no `__init__` (que agora só conecta).
+
+Tabela `whatsapp_envios_log` (log de rastreamento por envio):
+
+```
+id PK, lead_id, nome, cidade, telefone, telefone_normalizado, chat_id,
+status, mensagem, payload, erro, data_envio
+```
 
 ```python
 save_leads(df) -> int          # filtra descartados, UPSERT, não apaga log WAHA
@@ -186,7 +225,8 @@ get_leads_para_envio(limite=None, numero=None, cidade=None, nicho=None)
                                # ativo + Celular + pendente; filtros opcionais
 marcar_envio(nome, cidade, status_whatsapp)   # 'enviado' grava data
 salvar_chat_id_waha(nome, cidade, chat_id)    # cacheia o chatId resolvido
-listar_templates_ativos()      # [{id, mensagem, descricao, ativo}]
+salvar_log_envio(lead_id, nome, cidade, telefone, chat_id, status, ...)
+listar_templates_ativos()      # [{id, mensagem, descricao, segmento, ativo}]
 export_to_excel(nicho, cidade) # output/leads_{nicho}_{cidade}.xlsx
 close()
 ```
@@ -202,8 +242,11 @@ close()
 
 ```python
 WAHA_API_URL, WAHA_API_KEY, WAHA_SESSION
-WAHA_ATIVO, SOMENTE_ENVIO, WAHA_INTERVALO, WAHA_LIMITE
+WAHA_ATIVO, SOMENTE_ENVIO
+WAHA_CADENCIA, WAHA_INTERVALO, WAHA_LIMITE
 MENSAGEM_PADRAO
+_parse_cadencia(valor)                 # "N:Y" -> (envios_por_janela, janela_s)
+_pausas_cadencia(total, envios, janela)# pausas aleatórias anti-bloqueio
 _normalizar_chatid(telefone)            # 55DDDNUMERO@c.us (clássico)
 _resolver_chatid_waha(telefone, ...)    # GET /api/checkNumberStatus → @lid ou @c.us
 _limpar_markdown_whatsapp(texto)        # **negrito** → texto; [r](u) → u
@@ -216,6 +259,9 @@ disparar_campanha(db, mensagem_template=None, intervalo=13, limite=None, leads=N
 - **chatId:** números recentes usam `@lid`; enviar `@c.us` para eles retorna
   **HTTP 500**. `_resolver_chatid_waha` consulta `/api/checkNumberStatus`
   (`?session=&phone=55DDD9XXXXXXXX`) e usa o `chatId` retornado; fallback `@c.us`.
+- **Cadência (anti-bloqueio):** `WAHA_CADENCIA="X:Y"` (ex.: `3:60` = 3 envios por
+  minuto) distribui os envios **aleatoriamente** dentro de cada janela de Y
+  segundos, evitando pausas fixas. Tem prioridade sobre `WAHA_INTERVALO` (fixo).
 - `disparar_campanha` aceita `leads` (DataFrame já filtrado). Se recebido, **não**
   reconsulta o banco — respeita os filtros aplicados pelo menu.
 - O chatId resolvido é **cacheado** via `db.salvar_chat_id_waha` (só resolve na
diff --git a/memory/02-decisoes-e-armadilhas.md b/memory/02-decisoes-e-armadilhas.md
index 86df9dd..5f7e3b2 100644
--- a/memory/02-decisoes-e-armadilhas.md
+++ b/memory/02-decisoes-e-armadilhas.md
@@ -4,9 +4,23 @@ Leia antes de mexer no código. Cada item já custou tempo de depuração.
 
 ---
 
-## DuckDB: um processo por arquivo
+## Banco: PostgreSQL OU DuckDB (via `src/backend.py`)
 
-**O arquivo `data/leads.duckdb` só pode ser aberto por UM processo.** Não existe
+O projeto suporta dois backends, escolhidos por `DB_ENGINE` no `.env`:
+
+- `DB_ENGINE=postgres` → banco externo (`DATABASE_URL` ou `DB_*`).
+- `DB_ENGINE=duckdb` → arquivo local (`DUCKDB_PATH`, default `data/leads.duckdb`).
+
+**Regra de ouro:** nenhum módulo além de `src/backend.py` importa `duckdb` ou
+`psycopg2`. Todo acesso passa por `backend.execute/query_df/query_all/bulk_upsert`.
+- Placeholder de parâmetro: use `backend.ph()` (`?` no DuckDB, `%s` no Postgres),
+  NUNCA hardcode.
+- `excluded.col` funciona no `ON CONFLICT` dos dois bancos.
+- A DDL/seed fica em `schema.py` (roda uma vez: `python src/schema.py`).
+
+### Armadilha do DuckDB: um processo por arquivo
+
+**O `data/leads.duckdb` só pode ser aberto por UM processo.** Não existe
 "read-only compartilhado" — até `duckdb.connect(..., read_only=True)` falha:
 
 ```
@@ -16,16 +30,24 @@ O arquivo já está sendo usado por outro processo.
 
 Causas mais comuns: **DBeaver conectado**, scraper rodando, notebook aberto.
 
-Consequências no código:
-- `localidades_db.conexao()` abre/fecha a cada operação (não mantém aberto).
+Consequências:
+- `localidades_db` abre/fecha a conexão a cada operação (não mantém aberto).
 - `LeadDatabase` mantém aberto durante o scraping — **não** abra outra conexão
   persistente no mesmo processo.
-- `CacheIndisponivel` existe para degradar com aviso em vez de quebrar:
-  o sistema segue usando as APIs (IBGE/OSM) sem cache.
+- `CacheIndisponivel` degrada com aviso em vez de quebrar.
+
+### Armadilha do PostgreSQL: senha com `@` na URL
+
+Na `DATABASE_URL`, caracteres especiais da senha devem ser "percent-encoded"
+(`@` → `%40`, `:` → `%3A`, `/` → `%2F`). O `config.py` já decodifica com `unquote`.
+Ex.: `aojbfoeub@@@111` → `aojbfoeub%40%40%40111`.
 
-- ⚠️ **Um WAL pendente (`.wal`) indica dados não consolidados.** Se comitar o
-  `.duckdb` com o programa aberto, o `.wal` (ignorado no Git) fica de fora e o
-  commit sobe um estado desatualizado. Feche o programa antes de comitar.
+### Armadilha: identidade vs sequence (PostgreSQL)
+
+No Postgres, `templates_whatsapp.id`, `whatsapp_envios_log.id` e
+`localidades_bairros.id` são colunas **IDENTITY**. O `lead_id` de `leads` é
+`integer` com sequence manual (`seq_leads_id`). Não assuma que todas as PKs se
+comportam igual.
 
 ---
 
@@ -96,8 +118,7 @@ OpenStreetMap em toda sincronização.
 | true | false | lê do banco; o que falta vem da API sem gravar |
 | false | false | sempre API, banco intocado |
 
-- `SALVAR=false` também desativa a criação de tabelas (`CRIAR_TABELAS`) e os
-  menus **3** e **4**.
+- `SALVAR=false` também desativa a escrita local e os menus **3** e **4**.
 - As flags são lidas **no import**: mudar o `.env` exige reiniciar o programa.
 - Com `USAR_CACHE=false`, cada cidade baixa a lista da UF de novo (exceto pela
   memoização em memória `_municipios_da_uf`, válida só na execução atual).
@@ -135,6 +156,18 @@ para números recentes do WhatsApp. Esses números foram migrados para o formato
 
 ---
 
+## WAHA: cadência aleatória (anti-bloqueio)
+
+Enviar com pausa fixa (ex.: 15s, 15s, 15s) é fácil de detectar e leva a bloqueio.
+
+- `WAHA_CADENCIA="X:Y"` (ex.: `3:60` = 3 envios/minuto) faz os envios caírem em
+  **pontos aleatórios** dentro de cada janela de Y segundos → pausas variáveis.
+- Tem prioridade sobre `WAHA_INTERVALO` (pausa fixa, usada só se `WAHA_CADENCIA`
+  estiver vazio).
+- Implementação: `_pausas_cadencia(total, envios_janela, janela)` em `whatsapp.py`.
+
+---
+
 ## `.env` e Git
 
 - `.env` **é ignorado** (contém `WAHA_API_KEY`). `.env.example` **é versionado**.
@@ -167,7 +200,7 @@ entre `" - "` e `","`. Se não casar, `"Não Informado"`.
 ## Concorrência
 
 - `save_callback` é chamado **na thread principal** (dentro do loop de
-  `as_completed`), então não há escrita concorrente no DuckDB.
+  `as_completed`), então não há escrita concorrente no banco.
 - O cooldown anti-captcha usa `_cooldown_lock` + variável global `_cooldown_ate`.
 - `lock` protege a lista `vistos`/`todos_leads`.
 
diff --git a/memory/03-historico-de-mudancas.md b/memory/03-historico-de-mudancas.md
index 7e047dd..c51feff 100644
--- a/memory/03-historico-de-mudancas.md
+++ b/memory/03-historico-de-mudancas.md
@@ -4,6 +4,38 @@ Registro do que mudou, por quê e o que ficou pendente. Mais recente primeiro.
 
 ---
 
+## 2026-10-31
+
+### Migração para PostgreSQL + suporte dual (PostgreSQL/DuckDB)
+
+- Banco externo PostgreSQL (`vps.agendamentoja.com/leads_db`) + mantido o DuckDB
+  local como alternativa offline.
+- Novo `src/backend.py`: abstrai conexão, placeholder (`?`/`%s`), leitura
+  (DataFrame/tupla) e bulk upsert entre os dois bancos. `database.py`,
+  `localidades_db.py` e `schema.py` não importam mais `duckdb`/`psycopg2`.
+- `config.py` lê `DB_ENGINE` (postgres|duckdb), `DATABASE_URL` e `DUCKDB_PATH`.
+  Inferência: DUCKDB_PATH → duckdb; senão DATABASE_URL → postgres; senão duckdb.
+- `schema.py` reescrito para os dois bancos; corrige o gap da tabela `leads`
+  (PK `lead_id` + UNIQUE `(nome,cidade)` + default `nextval('seq_leads_id')`).
+- `requirements.txt`: readicionado `duckdb` + `psycopg2-binary`.
+- `.env`: seção "BANCO DE DADOS — engine independente" com `DATABASE_URL` (senha
+  com `@` percent-encoded) e config antiga comentada como referência.
+
+### Cadência aleatória de envio WhatsApp (anti-bloqueio)
+
+- Nova `WAHA_CADENCIA="X:Y"` no `.env` (ex.: `3:60` = 3 envios por minuto).
+- `whatsapp.py`: `_parse_cadencia` + `_pausas_cadencia` distribuem os envios em
+  pontos **aleatórios** dentro de cada janela (pausas variáveis, não fixas).
+- Tem prioridade sobre `WAHA_INTERVALO` (fixo). `WAHA_CADENCIA` vazio → usa o fixo.
+
+### Tabela `whatsapp_envios_log` (rastreamento)
+
+- Log por envio com `lead_id`, `telefone` (dígitos) e `telefone_normalizado`
+  (55DDDNUMERO), `chat_id`, `status`, `mensagem`, `payload`, `erro`, `data_envio`.
+- JOIN pronto por `lead_id` ou `telefone`.
+
+---
+
 ## 2026-10-30
 
 ### Templates de mensagem de WhatsApp (tabela + markdown)
diff --git a/memory/README.md b/memory/README.md
index d368177..6e4ffd8 100644
--- a/memory/README.md
+++ b/memory/README.md
@@ -38,7 +38,10 @@ git add -A; git commit -m "Atualização"; git push --force origin main
 
 
 ## git forçado
-- Envia
+
+# Envia
 git add -A; git commit -m "Melhorias no processo de coletas v3 $(Get-Date -Format 'yyyy-MM-dd HH:mm')"; git push --force-with-lease origin main
-- Recebe
+
+# Recebe
+
 git fetch --all; git reset --hard origin/main
\ No newline at end of file
diff --git a/repomix-output.md b/repomix-output.md
index b5ff654..220be58 100644
--- a/repomix-output.md
+++ b/repomix-output.md
@@ -38,7 +38,7 @@ The content is organized as follows:
 - Git diffs from the worktree and staged changes are included
 
 # Directory Structure
-`````
+````
 data/
   leads.duckdb
 memory/
@@ -47,31 +47,692 @@ memory/
   02-decisoes-e-armadilhas.md
   03-historico-de-mudancas.md
   04-como-contribuir.md
+  05-plano-coleta-nacional-docker.md
   README.md
 src/
   __init__.py
+  backend.py
+  coleta_auto.py
   config.py
   database.py
   localidades_db.py
   locations.py
   main.py
+  schema.py
   scraper.py
   utils.py
   whatsapp.py
+.dockerignore
 .env.example
 .gitignore
 .gitkeep
 .repomixignore
+docker-compose.yml
+Dockerfile
+map_scraper.zip
 README.md
 repomix-instrucao.md
 repomix.config.json
 requirements.txt
-`````
+````
 
 # Files
 
+## File: src/backend.py
+````python
+  1: # src/backend.py
+  2: """Camada de acesso a dados independente do banco (PostgreSQL ou DuckDB).
+  3: 
+  4: Centraliza as diferenças entre os dois backends:
+  5: - conexão
+  6: - placeholder de parâmetro (`?` no DuckDB, `%s` no PostgreSQL)
+  7: - leitura para DataFrame / tupla
+  8: - bulk upsert (multi-row VALUES)
+  9: 
+ 10: Os módulos `database.py`, `localidades_db.py` e `schema.py` usam apenas as
+ 11: funções daqui — nunca `duckdb`/`psycopg2` diretamente.
+ 12: """
+ 13: import os
+ 14: from urllib.parse import unquote, urlparse
+ 15: 
+ 16: import duckdb
+ 17: import numpy as np
+ 18: import pandas as pd
+ 19: import psycopg2
+ 20: 
+ 21: from src.config import (
+ 22:     DB_ENGINE,
+ 23:     DATABASE_URL,
+ 24:     DUCKDB_PATH,
+ 25:     DB_HOST,
+ 26:     DB_PORT,
+ 27:     DB_NAME,
+ 28:     DB_USER,
+ 29:     DB_PASSWORD,
+ 30: )
+ 31: 
+ 32: IS_DUCKDB = DB_ENGINE == "duckdb"
+ 33: 
+ 34: 
+ 35: def ph():
+ 36:     """Placeholder de parâmetro do backend atual (`?` ou `%s`)."""
+ 37:     return "?" if IS_DUCKDB else "%s"
+ 38: 
+ 39: 
+ 40: def conectar():
+ 41:     """Abre uma conexão com o backend configurado."""
+ 42:     if IS_DUCKDB:
+ 43:         diretorio = os.path.dirname(DUCKDB_PATH)
+ 44:         if diretorio:
+ 45:             os.makedirs(diretorio, exist_ok=True)
+ 46:         return duckdb.connect(DUCKDB_PATH)
+ 47: 
+ 48:     if DATABASE_URL:
+ 49:         parsed = urlparse(DATABASE_URL)
+ 50:         return psycopg2.connect(
+ 51:             host=parsed.hostname,
+ 52:             port=parsed.port or 5432,
+ 53:             dbname=(parsed.path or "").lstrip("/") or None,
+ 54:             user=unquote(parsed.username) if parsed.username else None,
+ 55:             password=unquote(parsed.password) if parsed.password else "",
+ 56:             connect_timeout=15,
+ 57:         )
+ 58: 
+ 59:     return psycopg2.connect(
+ 60:         host=DB_HOST,
+ 61:         port=DB_PORT,
+ 62:         dbname=DB_NAME,
+ 63:         user=DB_USER,
+ 64:         password=DB_PASSWORD,
+ 65:         connect_timeout=15,
+ 66:     )
+ 67: 
+ 68: 
+ 69: def commit(conn):
+ 70:     """Confirma a transação (no-op no DuckDB, que faz autocommit)."""
+ 71:     if not IS_DUCKDB:
+ 72:         conn.commit()
+ 73: 
+ 74: 
+ 75: def close(conn):
+ 76:     conn.close()
+ 77: 
+ 78: 
+ 79: def execute(conn, sql, params=None):
+ 80:     """Executa SQL e devolve cursor/relação (o chamador normalmente ignora)."""
+ 81:     params = params or []
+ 82:     if IS_DUCKDB:
+ 83:         return conn.execute(sql, params)
+ 84:     cur = conn.cursor()
+ 85:     cur.execute(sql, params)
+ 86:     return cur
+ 87: 
+ 88: 
+ 89: def query_df(conn, sql, params=None):
+ 90:     """Executa uma consulta e devolve um DataFrame."""
+ 91:     if IS_DUCKDB:
+ 92:         return conn.execute(sql, params or []).df()
+ 93:     cur = conn.cursor()
+ 94:     cur.execute(sql, params or [])
+ 95:     colunas = [d[0] for d in cur.description]
+ 96:     return pd.DataFrame(cur.fetchall(), columns=colunas)
+ 97: 
+ 98: 
+ 99: def query_one(conn, sql, params=None):
+100:     """Executa uma consulta e devolve a primeira linha (tupla ou None)."""
+101:     if IS_DUCKDB:
+102:         return conn.execute(sql, params or []).fetchone()
+103:     cur = conn.cursor()
+104:     cur.execute(sql, params or [])
+105:     return cur.fetchone()
+106: 
+107: 
+108: def query_all(conn, sql, params=None):
+109:     """Executa uma consulta e devolve todas as linhas (lista de tuplas)."""
+110:     if IS_DUCKDB:
+111:         return conn.execute(sql, params or []).fetchall()
+112:     cur = conn.cursor()
+113:     cur.execute(sql, params or [])
+114:     return cur.fetchall()
+115: 
+116: 
+117: def _valor(v):
+118:     """Converte NaN/NaT e escalares numpy em tipos nativos do Python."""
+119:     if v is None:
+120:         return None
+121:     try:
+122:         if pd.isna(v):
+123:             return None
+124:     except (TypeError, ValueError):
+125:         pass
+126:     if isinstance(v, np.integer):
+127:         return int(v)
+128:     if isinstance(v, np.floating):
+129:         return float(v)
+130:     if isinstance(v, pd.Timestamp):
+131:         return v.to_pydatetime()
+132:     return v
+133: 
+134: 
+135: def df_to_rows(df):
+136:     """Converte um DataFrame em lista de tuplas (com NaN -> None)."""
+137:     colunas = list(df.columns)
+138:     return [
+139:         tuple(_valor(r[c]) for c in colunas)
+140:         for r in df.to_dict("records")
+141:     ]
+142: 
+143: 
+144: def bulk_upsert(conn, table, columns, rows, conflict, set_clause):
+145:     """Bulk INSERT ... ON CONFLICT ... DO UPDATE (multi-row VALUES).
+146: 
+147:     - table: nome da tabela
+148:     - columns: lista de colunas
+149:     - rows: lista de tuplas (uma por linha)
+150:     - conflict: colunas do conflito, ex. "nome, cidade"
+151:     - set_clause: ex. "telefone = excluded.telefone, ..."
+152:       (`excluded` em minúsculas funciona tanto no PostgreSQL quanto no DuckDB)
+153:     """
+154:     if not rows:
+155:         return
+156:     colunas_sql = ", ".join(columns)
+157:     linha = "(" + ", ".join([ph()] * len(columns)) + ")"
+158:     valores = ", ".join([linha] * len(rows))
+159:     sql = (
+160:         f"INSERT INTO {table} ({colunas_sql}) VALUES {valores} "
+161:         f"ON CONFLICT ({conflict}) DO UPDATE SET {set_clause}"
+162:     )
+163:     params = [v for row in rows for v in row]
+164:     execute(conn, sql, params)
+````
+
+## File: src/coleta_auto.py
+````python
+  1: # src/coleta_auto.py
+  2: """Coleta automática não-interativa (para rodar em container/servidor).
+  3: 
+  4: Substitui o menu interativo por um loop contínuo orientado a variáveis de
+  5: ambiente — nada de `input()`. Toda a configuração vem do `.env`:
+  6: 
+  7:     NICHO            nicho a coletar (default: barbearias)
+  8:     UFS              lista de UFs separadas por vírgula (vazio = todas)
+  9:     MAX_CIDADES      quantas cidades coletar por UF (0 = todas)
+ 10:     MAX_BAIRROS      quantos bairros usar por cidade (default: 30)
+ 11:     AQUECER_BAIRROS  pré-resolver bairros da UF antes de coletar (true/false)
+ 12:     SINCRONIZAR      baixar estados/municípios/distritos do IBGE antes (true/false)
+ 13:     MOSTRAR_NAVEGADOR abrir o Chromium visível (true/false, default false)
+ 14:     EXPORTAR_EXCEL   gerar Excel por cidade (true/false, default false)
+ 15:     LOOP             rodar em loop contínuo (true/false, default false)
+ 16:     LOOP_PAUSA_SEGUNDOS pausa entre ciclos quando LOOP=true (default 3600)
+ 17: 
+ 18: Uso:
+ 19:     python src/coleta_auto.py
+ 20: """
+ 21: import os
+ 22: import sys
+ 23: import time
+ 24: 
+ 25: sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
+ 26: 
+ 27: from src.config import carregar_env, str_para_bool, env_int
+ 28: from src.locations import (
+ 29:     obter_estados,
+ 30:     obter_cidades,
+ 31:     obter_termos_busca,
+ 32:     aquecer_bairros_uf,
+ 33:     sincronizar_base_localidades,
+ 34: )
+ 35: from src.scraper import rodar_scraper_multithread
+ 36: from src.database import LeadDatabase
+ 37: 
+ 38: carregar_env()
+ 39: 
+ 40: NICHO = os.environ.get("NICHO", "barbearias").strip().lower()
+ 41: UFS = [u.strip().upper() for u in os.environ.get("UFS", "").split(",") if u.strip()]
+ 42: MAX_CIDADES = max(0, env_int("MAX_CIDADES", 0))
+ 43: MAX_BAIRROS = max(1, env_int("MAX_BAIRROS", 30))
+ 44: AQUECER_BAIRROS = str_para_bool(os.environ.get("AQUECER_BAIRROS"), padrao=False)
+ 45: SINCRONIZAR = str_para_bool(os.environ.get("SINCRONIZAR"), padrao=False)
+ 46: MOSTRAR_NAVEGADOR = str_para_bool(os.environ.get("MOSTRAR_NAVEGADOR"), padrao=False)
+ 47: EXPORTAR_EXCEL = str_para_bool(os.environ.get("EXPORTAR_EXCEL"), padrao=False)
+ 48: LOOP = str_para_bool(os.environ.get("LOOP"), padrao=False)
+ 49: LOOP_PAUSA_SEGUNDOS = max(0, env_int("LOOP_PAUSA_SEGUNDOS", 3600))
+ 50: 
+ 51: 
+ 52: def _resolver_ufs():
+ 53:     """UFs alvo: as da env, ou todas do IBGE se vazio."""
+ 54:     if UFS:
+ 55:         return UFS
+ 56:     df = obter_estados()
+ 57:     if df.empty:
+ 58:         return []
+ 59:     return sorted(df["uf"].tolist())
+ 60: 
+ 61: 
+ 62: def _coletar_cidade(db, cidade, uf):
+ 63:     print(f"\n=== {cidade}-{uf} ({NICHO}) ===")
+ 64:     termos = obter_termos_busca(cidade, uf, max_bairros=MAX_BAIRROS)
+ 65:     df = rodar_scraper_multithread(
+ 66:         nicho=NICHO,
+ 67:         cidade=cidade,
+ 68:         uf=uf,
+ 69:         termos_lista=termos,
+ 70:         mostrar_navegador=MOSTRAR_NAVEGADOR,
+ 71:         save_callback=db.save_leads,
+ 72:     )
+ 73:     if EXPORTAR_EXCEL and not df.empty:
+ 74:         db.export_to_excel(NICHO, cidade)
+ 75: 
+ 76: 
+ 77: def executar_ciclo():
+ 78:     db = LeadDatabase()
+ 79:     try:
+ 80:         if SINCRONIZAR:
+ 81:             sincronizar_base_localidades()
+ 82: 
+ 83:         ufs = _resolver_ufs()
+ 84:         if not ufs:
+ 85:             print("Nenhuma UF disponível. Abortando ciclo.")
+ 86:             return
+ 87: 
+ 88:         for uf in ufs:
+ 89:             cidades = obter_cidades(uf)
+ 90:             if not cidades:
+ 91:                 print(f"[{uf}] nenhuma cidade encontrada. Pulando.")
+ 92:                 continue
+ 93: 
+ 94:             if AQUECER_BAIRROS:
+ 95:                 aquecer_bairros_uf(uf, max_cidades=MAX_CIDADES)
+ 96: 
+ 97:             if MAX_CIDADES:
+ 98:                 cidades = cidades[:MAX_CIDADES]
+ 99: 
+100:             print(f"\n[{uf}] {len(cidades)} cidade(s) a coletar (nicho={NICHO}).")
+101:             for cidade in cidades:
+102:                 try:
+103:                     _coletar_cidade(db, cidade, uf)
+104:                 except Exception as e:
+105:                     print(f"[{cidade}-{uf}] ERRO: {type(e).__name__}: {e}")
+106:     finally:
+107:         db.close()
+108: 
+109: 
+110: def main():
+111:     print(f"Map Scraper (auto) | nicho={NICHO} | UFs={UFS or 'todas'} | "
+112:           f"max_cidades={MAX_CIDADES or 'todas'} | loop={LOOP}")
+113:     while True:
+114:         executar_ciclo()
+115:         if not LOOP:
+116:             break
+117:         print(f"\nCiclo concluído. Aguardando {LOOP_PAUSA_SEGUNDOS}s para o próximo...")
+118:         time.sleep(LOOP_PAUSA_SEGUNDOS)
+119: 
+120: 
+121: if __name__ == "__main__":
+122:     main()
+````
+
+## File: src/schema.py
+````python
+  1: # src/schema.py
+  2: """Criação e população do schema do banco (setup inicial + migração).
+  3: 
+  4: Suporta PostgreSQL e DuckDB (definido por `DB_ENGINE` no `.env`). Separação de
+  5: responsabilidades:
+  6: - `database.py` / `localidades_db.py` apenas CONECTAM e operam sobre um schema
+  7:   já existente.
+  8: - Este módulo CRIA as tabelas/sequences e POPULA os templates. Rode uma vez ao
+  9:   iniciar do zero (ou após mudar de banco):
+ 10: 
+ 11:       python src/schema.py
+ 12: 
+ 13: É idempotente: pode rodar de novo sem perder dados.
+ 14: """
+ 15: import os
+ 16: import sys
+ 17: 
+ 18: sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
+ 19: 
+ 20: from src import backend
+ 21: from src.config import DB_ENGINE
+ 22: 
+ 23: # Template padrão de WhatsApp, usado para popular a tabela de templates.
+ 24: # Segmento indica o nicho para o qual a mensagem foi criada (ex.: barbearias).
+ 25: # O markdown (**negrito**) é limpo antes do envio real no whatsapp.py.
+ 26: TEMPLATE_AGRUPAMENTO_PADRAO = """Opa, tudo certo?
+ 27: 
+ 28: Conhece o **Agendamento Já**? É uma plataforma 100% online para deixar sua agenda no piloto automático e acabar com a dor de cabeça de gerenciar horários pelo WhatsApp.
+ 29: 
+ 30: Com planos a partir de **R$ 29,90** no nosso aplicativo você consegue:
+ 31: 
+ 32: • Personalizar com a identidade da sua marca
+ 33: • Lembretes automatizados via Whatsapp
+ 34: • Divulgação de horários automatizadas
+ 35: • Controle de faturamento
+ 36: • Pagamentos antecipados
+ 37: 
+ 38: **Conheça nossa proposta**: https://agendamentoja.com/
+ 39: **Acompanhe nosso dia a dia**: https://www.instagram.com/agendamentoja_
+ 40: 
+ 41: Quer ver uma demonstração rápida de como funciona na prática para o seu tipo de serviço? É só me avisar!"""
+ 42: 
+ 43: # Segmento (nicho) padrão do template acima.
+ 44: TEMPLATE_SEGMENTO_PADRAO = "barbearias"
+ 45: 
+ 46: 
+ 47: def _schema_duckdb(conn):
+ 48:     """Schema do DuckDB local (ids via sequences; templates com id fixo)."""
+ 49:     conn.execute("CREATE SEQUENCE IF NOT EXISTS seq_leads_id")
+ 50:     conn.execute("CREATE SEQUENCE IF NOT EXISTS seq_whatsapp_envios_log_id")
+ 51: 
+ 52:     conn.execute("""
+ 53:         CREATE TABLE IF NOT EXISTS leads (
+ 54:             lead_id INTEGER DEFAULT nextval('seq_leads_id'),
+ 55:             nome VARCHAR,
+ 56:             telefone VARCHAR,
+ 57:             tipo_telefone VARCHAR,
+ 58:             whatsapp_link VARCHAR,
+ 59:             instagram VARCHAR,
+ 60:             site VARCHAR,
+ 61:             bairro VARCHAR,
+ 62:             cidade VARCHAR,
+ 63:             estado VARCHAR,
+ 64:             nicho VARCHAR,
+ 65:             status VARCHAR DEFAULT 'ativo',
+ 66:             data_extracao TIMESTAMP,
+ 67:             data_envio_whatsapp TIMESTAMP,
+ 68:             status_whatsapp VARCHAR DEFAULT 'pendente',
+ 69:             chat_id_waha VARCHAR,
+ 70:             PRIMARY KEY (lead_id),
+ 71:             UNIQUE (nome, cidade)
+ 72:         )
+ 73:     """)
+ 74:     conn.execute("""
+ 75:         CREATE TABLE IF NOT EXISTS templates_whatsapp (
+ 76:             id INTEGER PRIMARY KEY,
+ 77:             mensagem VARCHAR,
+ 78:             descricao VARCHAR,
+ 79:             segmento VARCHAR,
+ 80:             ativo BOOLEAN DEFAULT TRUE
+ 81:         )
+ 82:     """)
+ 83:     conn.execute("""
+ 84:         CREATE TABLE IF NOT EXISTS whatsapp_envios_log (
+ 85:             id INTEGER DEFAULT nextval('seq_whatsapp_envios_log_id'),
+ 86:             lead_id INTEGER,
+ 87:             nome VARCHAR,
+ 88:             cidade VARCHAR,
+ 89:             telefone VARCHAR,
+ 90:             telefone_normalizado VARCHAR,
+ 91:             chat_id VARCHAR,
+ 92:             status VARCHAR,
+ 93:             mensagem VARCHAR,
+ 94:             payload VARCHAR,
+ 95:             erro VARCHAR,
+ 96:             data_envio TIMESTAMP
+ 97:         )
+ 98:     """)
+ 99:     conn.execute("""
+100:         CREATE TABLE IF NOT EXISTS localidades_estados (
+101:             uf VARCHAR PRIMARY KEY,
+102:             nome VARCHAR NOT NULL
+103:         )
+104:     """)
+105:     conn.execute("""
+106:         CREATE TABLE IF NOT EXISTS localidades_municipios (
+107:             id_municipio BIGINT PRIMARY KEY,
+108:             nome VARCHAR NOT NULL,
+109:             uf VARCHAR NOT NULL,
+110:             bairros_fonte VARCHAR,
+111:             bairros_atualizado_em TIMESTAMP
+112:         )
+113:     """)
+114:     conn.execute("""
+115:         CREATE TABLE IF NOT EXISTS localidades_bairros (
+116:             id_municipio BIGINT NOT NULL,
+117:             nome VARCHAR NOT NULL,
+118:             id_distrito BIGINT,
+119:             PRIMARY KEY (id_municipio, nome)
+120:         )
+121:     """)
+122: 
+123:     # Seed com id fixo (o templates no DuckDB não tem auto-incremento).
+124:     conn.execute("""
+125:         INSERT INTO templates_whatsapp (id, mensagem, descricao, segmento, ativo)
+126:         SELECT 1, ?, 'Apresentação Agendamento Já', ?, TRUE
+127:         WHERE NOT EXISTS (SELECT 1 FROM templates_whatsapp WHERE id = 1)
+128:     """, [TEMPLATE_AGRUPAMENTO_PADRAO, TEMPLATE_SEGMENTO_PADRAO])
+129: 
+130: 
+131: def _schema_postgres(conn):
+132:     """Schema do PostgreSQL (ids identity; migração da tabela `leads`)."""
+133:     from psycopg2 import sql
+134: 
+135:     cur = conn.cursor()
+136:     cur.execute("CREATE SEQUENCE IF NOT EXISTS seq_leads_id")
+137: 
+138:     cur.execute("""
+139:         CREATE TABLE IF NOT EXISTS leads (
+140:             lead_id INTEGER NOT NULL DEFAULT nextval('seq_leads_id'),
+141:             nome TEXT,
+142:             telefone TEXT,
+143:             tipo_telefone TEXT,
+144:             whatsapp_link TEXT,
+145:             instagram TEXT,
+146:             site TEXT,
+147:             bairro TEXT,
+148:             cidade TEXT,
+149:             estado TEXT,
+150:             nicho TEXT,
+151:             status TEXT DEFAULT 'ativo',
+152:             data_extracao TIMESTAMP,
+153:             data_envio_whatsapp TIMESTAMP,
+154:             status_whatsapp TEXT DEFAULT 'pendente',
+155:             chat_id_waha TEXT,
+156:             PRIMARY KEY (lead_id),
+157:             UNIQUE (nome, cidade)
+158:         )
+159:     """)
+160:     cur.execute("""
+161:         CREATE TABLE IF NOT EXISTS templates_whatsapp (
+162:             id INTEGER GENERATED BY DEFAULT AS IDENTITY PRIMARY KEY,
+163:             mensagem TEXT,
+164:             descricao TEXT,
+165:             segmento TEXT,
+166:             ativo BOOLEAN DEFAULT TRUE
+167:         )
+168:     """)
+169:     cur.execute("""
+170:         CREATE TABLE IF NOT EXISTS whatsapp_envios_log (
+171:             id INTEGER GENERATED BY DEFAULT AS IDENTITY PRIMARY KEY,
+172:             lead_id INTEGER,
+173:             nome TEXT,
+174:             cidade TEXT,
+175:             telefone TEXT,
+176:             telefone_normalizado TEXT,
+177:             chat_id TEXT,
+178:             status TEXT,
+179:             mensagem TEXT,
+180:             payload TEXT,
+181:             erro TEXT,
+182:             data_envio TIMESTAMP
+183:         )
+184:     """)
+185:     cur.execute("""
+186:         CREATE TABLE IF NOT EXISTS localidades_estados (
+187:             uf TEXT PRIMARY KEY,
+188:             nome TEXT NOT NULL
+189:         )
+190:     """)
+191:     cur.execute("""
+192:         CREATE TABLE IF NOT EXISTS localidades_municipios (
+193:             id_municipio BIGINT PRIMARY KEY,
+194:             nome TEXT NOT NULL,
+195:             uf TEXT NOT NULL,
+196:             bairros_fonte TEXT,
+197:             bairros_atualizado_em TIMESTAMP
+198:         )
+199:     """)
+200:     cur.execute("""
+201:         CREATE TABLE IF NOT EXISTS localidades_bairros (
+202:             id_municipio BIGINT NOT NULL,
+203:             nome TEXT NOT NULL,
+204:             id_distrito BIGINT,
+205:             PRIMARY KEY (id_municipio, nome)
+206:         )
+207:     """)
+208: 
+209:     # Migração do gap conhecido: leads sem PK/default no lead_id (banco antigo).
+210:     cur.execute("ALTER TABLE leads ALTER COLUMN lead_id SET DEFAULT nextval('seq_leads_id')")
+211: 
+212:     cur.execute("""
+213:         SELECT 1 FROM information_schema.table_constraints
+214:         WHERE table_schema = 'public' AND table_name = 'leads'
+215:           AND constraint_name = 'leads_pkey'
+216:     """)
+217:     if not cur.fetchone():
+218:         cur.execute("ALTER TABLE leads ADD CONSTRAINT leads_pkey PRIMARY KEY (lead_id)")
+219: 
+220:     cur.execute("""
+221:         SELECT 1 FROM information_schema.table_constraints
+222:         WHERE table_schema = 'public' AND table_name = 'leads'
+223:           AND constraint_name = 'leads_nome_cidade_key'
+224:     """)
+225:     if not cur.fetchone():
+226:         cur.execute("ALTER TABLE leads ADD CONSTRAINT leads_nome_cidade_key UNIQUE (nome, cidade)")
+227: 
+228:     cur.execute("""
+229:         SELECT setval('seq_leads_id',
+230:             GREATEST((SELECT COALESCE(MAX(lead_id), 0) + 1 FROM leads), 1), false)
+231:     """)
+232: 
+233:     # Seed sem informar id (coluna IDENTITY gera sozinha).
+234:     cur.execute("""
+235:         INSERT INTO templates_whatsapp (mensagem, descricao, segmento, ativo)
+236:         SELECT %s, 'Apresentação Agendamento Já', %s, TRUE
+237:         WHERE NOT EXISTS (SELECT 1 FROM templates_whatsapp)
+238:     """, [TEMPLATE_AGRUPAMENTO_PADRAO, TEMPLATE_SEGMENTO_PADRAO])
+239: 
+240: 
+241: def inicializar_schema(conn):
+242:     """Cria sequences, tabelas, corrige schema antigo e popula os templates."""
+243:     if backend.IS_DUCKDB:
+244:         _schema_duckdb(conn)
+245:     else:
+246:         _schema_postgres(conn)
+247:     backend.commit(conn)
+248: 
+249: 
+250: def main():
+251:     conn = backend.conectar()
+252:     try:
+253:         inicializar_schema(conn)
+254:     finally:
+255:         backend.close(conn)
+256:     print(f"Schema inicializado ({DB_ENGINE}).")
+257: 
+258: 
+259: if __name__ == "__main__":
+260:     main()
+````
+
+## File: .dockerignore
+````
+ 1: # Arquivos que NÃO devem ir para o build context / imagem Docker.
+ 2: .git
+ 3: .gitignore
+ 4: .gitkeep
+ 5: 
+ 6: # Segredos (o .env é injetado via env_file no compose, não copiado).
+ 7: .env
+ 8: 
+ 9: # Ambiente virtual e cache Python.
+10: venv
+11: .venv
+12: __pycache__
+13: *.pyc
+14: *.pyo
+15: 
+16: # Dados locais e saídas (são montados como volume, não copiados).
+17: data
+18: output
+19: *.duckdb
+20: *.duckdb.wal
+21: *.duckdb.tmp
+22: *.xlsx
+23: *.csv
+24: *.log
+25: 
+26: # Documentação interna (não necessária na imagem).
+27: memory
+28: repomix*
+29: util
+````
+
+## File: docker-compose.yml
+````yaml
+ 1: services:
+ 2:   app:
+ 3:     build: .
+ 4:     container_name: map_scraper
+ 5:     restart: unless-stopped
+ 6:     env_file:
+ 7:       - .env
+ 8:     environment:
+ 9:       # Configuração do runner (não-interativo). Valores padrão, sobrescreva
+10:       # no .env do host ou direto aqui.
+11:       NICHO: ${NICHO:-barbearias}
+12:       UFS: ${UFS:-}
+13:       MAX_CIDADES: ${MAX_CIDADES:-0}
+14:       MAX_BAIRROS: ${MAX_BAIRROS:-30}
+15:       AQUECER_BAIRROS: ${AQUECER_BAIRROS:-false}
+16:       SINCRONIZAR: ${SINCRONIZAR:-false}
+17:       MOSTRAR_NAVEGADOR: ${MOSTRAR_NAVEGADOR:-false}
+18:       EXPORTAR_EXCEL: ${EXPORTAR_EXCEL:-false}
+19:       LOOP: ${LOOP:-false}
+20:       LOOP_PAUSA_SEGUNDOS: ${LOOP_PAUSA_SEGUNDOS:-3600}
+21:     volumes:
+22:       # Banco local (modo DB_ENGINE=duckdb) e Excel gerado.
+23:       - ./data:/app/data
+24:       - ./output:/app/output
+````
+
+## File: Dockerfile
+````dockerfile
+ 1: # Dockerfile — Map Scraper
+ 2: # Imagem para rodar a coleta automática (sem menu) em container.
+ 3: FROM python:3.11-slim
+ 4: 
+ 5: ENV PYTHONUNBUFFERED=1 \
+ 6:     PYTHONDONTWRITEBYTECODE=1 \
+ 7:     PIP_NO_CACHE_DIR=1
+ 8: 
+ 9: WORKDIR /app
+10: 
+11: # Dependências de sistema (Playwright instala o resto com --with-deps).
+12: RUN apt-get update \
+13:     && apt-get install -y --no-install-recommends ca-certificates \
+14:     && rm -rf /var/lib/apt/lists/*
+15: 
+16: # Dependências Python do projeto.
+17: COPY requirements.txt .
+18: RUN pip install -r requirements.txt
+19: 
+20: # Chromium do Playwright + bibliotecas de sistema necessárias.
+21: RUN playwright install --with-deps chromium
+22: 
+23: # Código-fonte.
+24: COPY src/ ./src/
+25: 
+26: # Volumes montados no compose: /app/data (DuckDB) e /app/output (Excel).
+27: RUN mkdir -p /app/data /app/output
+28: 
+29: # Runner não-interativo (configuração via variáveis de ambiente).
+30: CMD ["python", "src/coleta_auto.py"]
+````
+
 ## File: memory/04-como-contribuir.md
-`````markdown
+````markdown
  1: # 04 — Como Contribuir: Padrões e Boas Práticas
  2: 
  3: Este documento detalha os padrões de código, estilo e comunicação esperados
@@ -137,17 +798,17 @@ requirements.txt
 63:   - `03-historico-de-mudancas.md`: log recente das mudanças importantes.
 64: - **Docstrings:** Use docstrings Python para explicar funções e classes.
 65: - **Comentários de código:** Breves e pontuais, explicando lógica complexa ou escolhas não óbvias.
-`````
+````
 
 ## File: src/__init__.py
-`````python
+````python
 1: 
-`````
+````
 
 ## File: src/config.py
-`````python
+````python
  1: # src/config.py
- 2: """Carregamento centralizado do arquivo .env e leitura de flags.
+ 2: """Carregamento centralizado do arquivo .env, leitura de flags e conexão com o banco.
  3: 
  4: Todos os módulos importam este arquivo, então o `.env` é lido uma única vez
  5: por processo, antes de qualquer constante de configuração ser calculada.
@@ -200,10 +861,40 @@ requirements.txt
 52: 
 53: # Lido no import: qualquer módulo que importe `src.config` já tem o .env aplicado.
 54: carregar_env()
-`````
+55: 
+56: # ---------------------------------------------------------------------------
+57: # Banco de dados — engine independente (PostgreSQL ou DuckDB)
+58: # ---------------------------------------------------------------------------
+59: # Escolha do backend:
+60: #   DB_ENGINE=postgres  -> PostgreSQL (DATABASE_URL ou DB_*)
+61: #   DB_ENGINE=duckdb    -> DuckDB local (DUCKDB_PATH)
+62: #
+63: # Se DB_ENGINE não for definido, a inferência é:
+64: #   DUCKDB_PATH  definido -> duckdb
+65: #   DATABASE_URL definido -> postgres
+66: #   nenhum dos dois       -> duckdb (padrão local/offline)
+67: DATABASE_URL = os.environ.get("DATABASE_URL", "")
+68: DUCKDB_PATH = os.environ.get("DUCKDB_PATH", "data/leads.duckdb")
+69: 
+70: DB_ENGINE = os.environ.get("DB_ENGINE", "").strip().lower()
+71: if DB_ENGINE not in ("postgres", "duckdb"):
+72:     if os.environ.get("DUCKDB_PATH"):
+73:         DB_ENGINE = "duckdb"
+74:     elif os.environ.get("DATABASE_URL"):
+75:         DB_ENGINE = "postgres"
+76:     else:
+77:         DB_ENGINE = "duckdb"
+78: 
+79: # Configuração do PostgreSQL (usada apenas quando DB_ENGINE=postgres).
+80: DB_HOST = os.environ.get("DB_HOST", "localhost")
+81: DB_PORT = env_int("DB_PORT", 5432)
+82: DB_NAME = os.environ.get("DB_NAME", "leads_db")
+83: DB_USER = os.environ.get("DB_USER", "leads_app")
+84: DB_PASSWORD = os.environ.get("DB_PASSWORD", "")
+````
 
 ## File: src/utils.py
-`````python
+````python
  1: # src/utils.py
  2: import re
  3: 
@@ -240,39 +931,40 @@ requirements.txt
 34:         
 35:     # Retorna apenas os números na coluna telefone, o tipo e o link pronto
 36:     return apenas_numeros, tipo, whatsapp_link
-`````
+````
 
 ## File: .gitkeep
-`````
+````
 1: 
-`````
+````
 
 ## File: requirements.txt
-`````
-1: pandas
-2: openpyxl
-3: instagpy
-4: pip-system-certs
-5: playwright
-6: chromium
-7: geopy
-8: duckdb
-9: requests
-`````
+````
+ 1: pandas
+ 2: openpyxl
+ 3: instagpy
+ 4: pip-system-certs
+ 5: playwright
+ 6: chromium
+ 7: geopy
+ 8: duckdb
+ 9: psycopg2-binary
+10: requests
+````
 
 ## File: memory/00-resumo-projeto.md
-`````markdown
+````markdown
  1: # 00 — Resumo do Projeto
  2: 
- 3: **Map Scraper** — ferramenta local de prospecção de leads B2B a partir do Google Maps.
+ 3: **Map Scraper** — ferramenta de prospecção de leads B2B a partir do Google Maps.
  4: 
  5: - **Entrada:** UF + cidade + nicho (ex.: `RS`, `Canoas`, `barbearias`).
  6: - **Processo:** divide a busca por bairros, raspa o Google Maps com Playwright em
  7:   multithread e extrai nome, telefone, Instagram e site.
- 8: - **Saída:** leads no DuckDB (`data/leads.duckdb`) + Excel em `output/`.
+ 8: - **Saída:** leads num banco (PostgreSQL **ou** DuckDB) + Excel em `output/`.
  9: - **Extra:** dispara mensagens de WhatsApp via WAHA para leads já coletados, com
-10:   templates reutilizáveis, filtros (número/cidade/nicho), teste de envio e cache
-11:   do chatId resolvido (`@lid`/`@c.us`).
+10:   templates reutilizáveis, filtros (número/cidade/nicho), teste de envio, cache
+11:   do chatId resolvido (`@lid`/`@c.us`) e **cadência aleatória** anti-bloqueio.
 12: 
 13: ## Fluxo de alto nível
 14: 
@@ -283,7 +975,7 @@ requirements.txt
 19:                   → database.LeadDatabase.save_leads (UPSERT incremental)
 20:                   → database.export_to_excel
 21:   └─ 2 WhatsApp   → template ativo → filtros → teste → database.get_leads_para_envio
-22:                   → whatsapp.disparar_campanha (WAHA, chatId via checkNumberStatus)
+22:                   → whatsapp.disparar_campanha (WAHA, cadência aleatória)
 23:   └─ 3 Sincronizar localidades (IBGE) → locations.sincronizar_base_localidades
 24:   └─ 4 Aquecer bairros de uma UF       → locations.aquecer_bairros_uf
 25:   └─ 5 Sair
@@ -295,7 +987,7 @@ requirements.txt
 31: |---|---|
 32: | Linguagem | Python 3.10+ (ambiente: `venv/`) |
 33: | Scraping | Playwright (Chromium) + ThreadPoolExecutor |
-34: | Banco | DuckDB (arquivo único, 1 processo por vez) |
+34: | Banco | **PostgreSQL (externo) ou DuckDB (local)** — via `src/backend.py` |
 35: | Dados | Pandas |
 36: | Localidades | API IBGE + Nominatim/Overpass (OpenStreetMap) |
 37: | WhatsApp | WAHA (WhatsApp HTTP API) |
@@ -305,475 +997,263 @@ requirements.txt
 41: 
 42: ```
 43: map_scraper_project/
-44: ├── data/          leads.duckdb (+ .wal transiente, ignorado no Git)
+44: ├── data/          leads.duckdb (usado quando DB_ENGINE=duckdb)
 45: ├── memory/        esta documentação para IA
 46: ├── output/        Excel gerado (ignorado no Git)
 47: ├── src/
-48: │   ├── config.py          loader do .env + helpers (bool/int)
-49: │   ├── database.py        LeadDatabase: leads, templates_whatsapp, UPSERT, Excel, log WAHA
-50: │   ├── localidades_db.py  cache IBGE em DuckDB (tabelas localidades_*)
-51: │   ├── locations.py       IBGE + OSM + cache; sync e aquecimento por UF
-52: │   ├── scraper.py         Playwright, multithread, anti-captcha
-53: │   ├── utils.py           formatar_telefone → (telefone, tipo, link wa)
-54: │   ├── whatsapp.py        envio via WAHA
-55: │   └── main.py            menu interativo
-56: ├── .env / .env.example
-57: ├── requirements.txt
-58: └── README.md
-59: ```
-60: 
-61: ## Git — o que é versionado
+48: │   ├── config.py          loader do .env + escolha do backend (DB_ENGINE)
+49: │   ├── backend.py         abstração PostgreSQL/DuckDB (conexão, SQL, bulk upsert)
+50: │   ├── database.py        LeadDatabase: leads, templates, log WAHA (via backend)
+51: │   ├── localidades_db.py  cache IBGE (via backend)
+52: │   ├── locations.py       IBGE + OSM + cache; sync e aquecimento por UF
+53: │   ├── scraper.py         Playwright, multithread, anti-captcha
+54: │   ├── schema.py          DDL + seed + migração (setup: python src/schema.py)
+55: │   ├── utils.py           formatar_telefone → (telefone, tipo, link wa)
+56: │   ├── whatsapp.py        envio via WAHA + cadência aleatória
+57: │   └── main.py            menu interativo
+58: ├── .env / .env.example
+59: ├── requirements.txt
+60: └── README.md
+61: ```
 62: 
-63: | Versionado | Ignorado |
-64: |---|---|
-65: | `data/leads.duckdb` | `.env` (segredos) |
-66: | `src/`, `memory/`, `README.md` | `*.duckdb.wal`, `*.duckdb.tmp` |
-67: | `.env.example` | `*.xlsx`, `*.csv`, `*.log` |
-68: | | `venv/`, `__pycache__/`, `sessions/` |
-69: 
-70: Comando de sync usado pelo mantenedor (sobrescreve o remoto):
-71: 
-72: ```powershell
-73: git add -A; git commit -m "sync local $(Get-Date -Format 'yyyy-MM-dd HH:mm')"; git push --force-with-lease origin main
-74: ```
-`````
-
-## File: memory/01-arquitetura-e-modulos.md
-`````markdown
-  1: # 01 — Arquitetura e Módulos
-  2: 
-  3: Todos os módulos usam imports absolutos (`from src.x import y`). `src/main.py`
-  4: adiciona a raiz do projeto ao `sys.path` antes de importar.
-  5: 
-  6: ---
-  7: 
-  8: ## src/config.py
-  9: 
- 10: Único ponto de leitura do `.env`. **Chame `carregar_env()` antes de calcular
- 11: constantes de módulo** (o import já executa uma vez).
- 12: 
- 13: ```python
- 14: carregar_env(caminho=None)      # não sobrescreve variáveis já no ambiente
- 15: str_para_bool(valor, padrao)    # aceita 1/true/yes/s/sim/on
- 16: env_int(nome, padrao)           # inteiro com fallback
- 17: PROJETO_RAIZ, CAMINHO_ENV
- 18: ```
- 19: 
- 20: > `src/whatsapp.py` chama `carregar_env()` no import (herança histórica).
- 21: > `src/locations.py` e `src/scraper.py` dependem disso para ler suas flags.
- 22: 
- 23: ---
- 24: 
- 25: ## src/localidades_db.py — cache de localidades
- 26: 
- 27: Acesso ao **mesmo** `data/leads.duckdb`. **Abre e fecha conexão a cada operação**,
- 28: para não segurar o arquivo durante o scraping (DuckDB permite só 1 processo).
- 29: 
- 30: Tabelas (criadas automaticamente quando `CRIAR_TABELAS = True`):
- 31: 
- 32: | Tabela | Colunas |
- 33: |---|---|
- 34: | `localidades_estados` | `uf` PK, `nome` |
- 35: | `localidades_municipios` | `id_municipio` PK, `nome`, `uf`, `bairros_fonte`, `bairros_atualizado_em` |
- 36: | `localidades_bairros` | `id_municipio`, `nome`, `id_distrito` — PK (`id_municipio`,`nome`) |
- 37: 
- 38: `bairros_fonte` ∈ {`ibge`, `overpass`, `cidade`, `NULL` (não coletado)}.
- 39: 
- 40: Funções:
- 41: 
- 42: ```python
- 43: conexao(db_path=None)              # contextmanager; DDL se CRIAR_TABELAS
- 44: ler_estados() / salvar_estados(registros)
- 45: ler_municipios(uf)                 # inclui bairros_fonte (necessário p/ cache hit)
- 46: ler_municipios_pendentes(uf)       # bairros_fonte IS NULL
- 47: salvar_municipios(registros)       # UPSERT preserva bairros_fonte
- 48: buscar_municipio(cidade, uf)       # dict ou None
- 49: ler_bairros(id_municipio) / salvar_bairros(id_municipio, registros, fonte)
- 50: salvar_distritos_bulk(distritos, min_bairros=3)   # aditivo
- 51: estatisticas()                     # dict com contagens
- 52: CacheIndisponivel                  # exceção (arquivo travado / tabela ausente)
- 53: ```
- 54: 
- 55: **Semânticas importantes**
- 56: 
- 57: - `salvar_bairros` é **autoritativo por cidade**: apaga nomes daquela cidade que
- 58:   não vieram na lista nova (não toca em outras cidades).
- 59: - `salvar_distritos_bulk` é **aditivo**: não apaga bairros do OSM já gravados.
- 60: - `salvar_municipios` é UPSERT e **preserva** `bairros_fonte`.
- 61: 
- 62: ---
- 63: 
- 64: ## src/locations.py — IBGE + OpenStreetMap + cache
- 65: 
- 66: Endpoints usados (`IBGE_API`):
- 67: 
- 68: ```
- 69: /estados                         → UF (sigla, nome)
- 70: /estados/{uf}/municipios         → municípios da UF
- 71: /municipios                      → todos (usado na sync nacional)
- 72: /municipios/{id}/distritos       → distritos de uma cidade
- 73: /distritos                       → todos (sync nacional)
- 74: ```
- 75: 
- 76: Flags do módulo (lidas do `.env`):
- 77: 
- 78: | Constante | Env | Default |
- 79: |---|---|---|
- 80: | `USAR_CACHE` | `LOCALIDADES_USAR_CACHE` | `true` |
- 81: | `SALVAR` | `LOCALIDADES_SALVAR` | `true` |
- 82: | `MIN_BAIRROS` | `LOCALIDADES_MIN_BAIRROS` | `3` |
- 83: | `AQUECER_PAUSA_PADRAO` | `AQUECER_PAUSA_SEGUNDOS` | `2` |
- 84: 
- 85: Helpers internos relevantes:
- 86: 
- 87: ```python
- 88: _cache(fn, ...)   # executa no banco tolerando CacheIndisponivel (avisa 1x)
- 89: _salvar(fn, ...)  # respeita SALVAR=false (avisa 1x e retorna None)
- 90: _normalizar(t)    # minúsculas + sem acento
- 91: _municipios_da_uf(uf)   # memoizado em memória (evita rebaixar a lista)
- 92: ```
- 93: 
- 94: API pública:
- 95: 
- 96: ```python
- 97: obter_estados() -> DataFrame[uf, nome]
- 98: obter_cidades(uf) -> list[str]
- 99: obter_bairros(cidade, uf) -> list[str]        # [] = buscar cidade inteira
-100: obter_termos_busca(cidade, uf, max_bairros=30) -> list[str]
-101: obter_municipio(cidade, uf) -> dict|None      # nome oficial + id IBGE
-102: filtrar_cidades(cidades, termo) -> list[str]  # sem acento/caixa
-103: listar_municipios_pendentes(uf) -> list[dict]
-104: aquecer_bairros_uf(uf, cidades=None, max_cidades=0, pausa_segundos=None) -> dict|None
-105: sincronizar_base_localidades() -> bool        # nacional; bloqueada se SALVAR=false
-106: ```
-107: 
-108: ### Resolução de bairros (`obter_bairros`)
-109: 
-110: 1. Resolve o município (cache → lista da UF → grava se `SALVAR`).
-111: 2. Usa o **nome oficial** do IBGE daqui pra frente.
-112: 3. Se `USAR_CACHE` e `bairros_fonte` preenchido → lê `localidades_bairros`.
-113: 4. Senão:
-114:    - baixa distritos do IBGE; descarta o distrito-sede (mesmo nome da cidade);
-115:    - se `>= MIN_BAIRROS` → fonte `ibge`, **sem** chamar o OSM;
-116:    - senão → Nominatim (bbox) + Overpass (`place=suburb|neighbourhood|quarter`,
-117:      fallback `admin_level 9/10`);
-118:    - se o OSM falhar (serviço fora) → **não grava** (`fonte=None`), tenta de novo
-119:      na próxima execução.
-120: 
-121: ---
-122: 
-123: ## src/scraper.py — Playwright + anti-bloqueio
-124: 
-125: ```python
-126: extrair_leads_local(nicho, termo_busca, cidade, uf, mostrar_navegador=False) -> list[dict]
-127: rodar_scraper_multithread(nicho, cidade, uf, termos_lista,
-128:                           mostrar_navegador=False, save_callback=None) -> DataFrame
-129: ```
-130: 
-131: - `max_workers = min(3, len(termos_lista))`.
-132: - `save_callback(df)` é chamado a cada área concluída (salvamento incremental).
-133: - Deduplicação intra-execução por `(nome, cidade)`.
-134: - Dict de lead: `nome, telefone, tipo_telefone, whatsapp_link, instagram, site,
-135:   bairro, cidade, estado, nicho`.
-136: 
-137: Rolagem: `MAX_ROLAGENS = 40`, para após `MAX_RODADAS_ESTAGNADAS = 3` rodadas sem
-138: crescimento.
-139: 
-140: Anti-captcha:
-141: 
-142: ```python
-143: BloqueioDetectado(termo)      # exceção
-144: _pagina_bloqueada(page, checar_texto=True)
-145: _marcar_bloqueio_global()     # cooldown compartilhado entre threads
-146: _aguardar_cooldown(termo)     # todas as threads esperam
-147: _navegar_com_retry(page, url, tentativas=3, timeout=..., termo=...)
-148: ```
-149: 
-150: Detecção: URL `/sorry/`, seletores de captcha (`#captcha-form`, reCAPTCHA,
-151: hCaptcha) e textos como "unusual traffic" / "tráfego incomum".
-152: Persistindo o bloqueio, **aborta só a área** e preserva os leads já extraídos.
-153: 
-154: Flags: `CAPTCHA_MAX_TENTATIVAS` (2), `CAPTCHA_PAUSA_SEGUNDOS` (300),
-155: `CAPTCHA_PAUSA_GLOBAL_SEGUNDOS` (180).
-156: 
-157: ---
-158: 
-159: ## src/database.py — leads
-160: 
-161: `LeadDatabase(db_path="data/leads.duckdb")`
-162: 
-163: Tabela `leads` — PK (`nome`, `cidade`):
-164: 
-165: ```
-166: nome, telefone, tipo_telefone, whatsapp_link, instagram, site,
-167: bairro, cidade, estado, nicho, status (default 'ativo'),
-168: data_extracao, data_envio_whatsapp, status_whatsapp (default 'pendente'),
-169: chat_id_waha
-170: ```
-171: 
-172: - `chat_id_waha`: cache do chatId resolvido pela WAHA (ex.: `143172869029943@lid`).
-173:   Preenchido na primeira resolução; evita chamar `/api/checkNumberStatus` de novo.
-174: 
-175: Tabela `templates_whatsapp` (criada e seedada no `__init__`):
-176: 
-177: ```
-178: id INTEGER PK, mensagem, descricao, ativo BOOLEAN (default TRUE)
-179: ```
-180: 
-181: - Seed idempotente do template "Apresentação Agendamento Já" (`id=1`).
-182: 
-183: ```python
-184: save_leads(df) -> int          # filtra descartados, UPSERT, não apaga log WAHA
-185: get_leads_para_envio(limite=None, numero=None, cidade=None, nicho=None)
-186:                                # ativo + Celular + pendente; filtros opcionais
-187: marcar_envio(nome, cidade, status_whatsapp)   # 'enviado' grava data
-188: salvar_chat_id_waha(nome, cidade, chat_id)    # cacheia o chatId resolvido
-189: listar_templates_ativos()      # [{id, mensagem, descricao, ativo}]
-190: export_to_excel(nicho, cidade) # output/leads_{nicho}_{cidade}.xlsx
-191: close()
-192: ```
-193: 
-194: - `get_leads_para_envio`: `numero` compara por dígitos (regex `[^0-9]` removido),
-195:   aceita parte do número; `cidade`/`nicho` são match exato.
-196: - `save_leads` **preserva** `status`, `data_envio_whatsapp`, `status_whatsapp` e
-197:   `chat_id_waha` no re-UPSERT (não sobrescreve log de envio nem o chatId).
-198: 
-199: ---
-200: 
-201: ## src/whatsapp.py — WAHA
-202: 
-203: ```python
-204: WAHA_API_URL, WAHA_API_KEY, WAHA_SESSION
-205: WAHA_ATIVO, SOMENTE_ENVIO, WAHA_INTERVALO, WAHA_LIMITE
-206: MENSAGEM_PADRAO
-207: _normalizar_chatid(telefone)            # 55DDDNUMERO@c.us (clássico)
-208: _resolver_chatid_waha(telefone, ...)    # GET /api/checkNumberStatus → @lid ou @c.us
-209: _limpar_markdown_whatsapp(texto)        # **negrito** → texto; [r](u) → u
-210: _renderizar_mensagem(template, lead)    # placeholders + limpa markdown
-211: enviar_texto_waha(chat_id, texto, ...)  # POST /api/sendText
-212: enviar_texto_numero(numero, texto, ...) # resolve chatId e envia (p/ teste)
-213: disparar_campanha(db, mensagem_template=None, intervalo=13, limite=None, leads=None)
-214: ```
-215: 
-216: - **chatId:** números recentes usam `@lid`; enviar `@c.us` para eles retorna
-217:   **HTTP 500**. `_resolver_chatid_waha` consulta `/api/checkNumberStatus`
-218:   (`?session=&phone=55DDD9XXXXXXXX`) e usa o `chatId` retornado; fallback `@c.us`.
-219: - `disparar_campanha` aceita `leads` (DataFrame já filtrado). Se recebido, **não**
-220:   reconsulta o banco — respeita os filtros aplicados pelo menu.
-221: - O chatId resolvido é **cacheado** via `db.salvar_chat_id_waha` (só resolve na
-222:   primeira vez; reenvios pulam o checkNumberStatus).
-223: - Placeholders: `{nome}`, `{bairro}`, `{cidade}`.
-224: - `SOMENTE_ENVIO=true` (ou `--so-enviar`) pula o menu e vai direto ao envio.
-225: 
-226: ---
-227: 
-228: ## src/main.py — menu
-229: 
-230: ```
-231: 1 - Coletar leads
-232: 2 - Enviar mensagens WhatsApp
-233: 3 - Sincronizar base de localidades (IBGE)
-234: 4 - Aquecer bairros de uma UF (OpenStreetMap)
-235: 5 - Sair
-236: ```
-237: 
-238: `coletar_leads()`: UF → cidade (filtro sem acento) → **confirma no IBGE e usa o
-239: nome oficial** → nicho → termos → "Ver navegador?" → scraping → Excel.
-240: 
-241: `enviar_whatsapp_menu()`: escolhe **template ativo** → aplica **filtros de envio**
-242: (0 todos / 1 por número / 2 por cidade / 3 por nicho) → pergunta se quer
-243: **teste de envio** (digitar número ou escolher um lead pendente) → lista os
-244: pendentes filtrados e confirma o disparo. Helpers: `_confirmar`,
-245: `_escolher_template`, `_escolher_filtros`, `testar_envio`.
-`````
+63: ## Git — o que é versionado
+64: 
+65: | Versionado | Ignorado |
+66: |---|---|
+67: | `src/`, `memory/`, `README.md` | `.env` (segredos) |
+68: | `.env.example` | `*.xlsx`, `*.csv`, `*.log` |
+69: | | `venv/`, `__pycache__/`, `sessions/` |
+70: 
+71: > `data/leads.duckdb` é o banco local (modo `DB_ENGINE=duckdb`). O banco externo
+72: > PostgreSQL (modo `DB_ENGINE=postgres`) fica no servidor e não é versionado.
+73: 
+74: Comando de sync usado pelo mantenedor (sobrescreve o remoto):
+75: 
+76: ```powershell
+77: git add -A; git commit -m "sync local $(Get-Date -Format 'yyyy-MM-dd HH:mm')"; git push --force-with-lease origin main
+78: ```
+````
 
 ## File: memory/02-decisoes-e-armadilhas.md
-`````markdown
+````markdown
   1: # 02 — Decisões Técnicas e Armadilhas
   2: 
   3: Leia antes de mexer no código. Cada item já custou tempo de depuração.
   4: 
   5: ---
   6: 
-  7: ## DuckDB: um processo por arquivo
+  7: ## Banco: PostgreSQL OU DuckDB (via `src/backend.py`)
   8: 
-  9: **O arquivo `data/leads.duckdb` só pode ser aberto por UM processo.** Não existe
- 10: "read-only compartilhado" — até `duckdb.connect(..., read_only=True)` falha:
- 11: 
- 12: ```
- 13: IO Error: Cannot open file "...data\leads.duckdb":
- 14: O arquivo já está sendo usado por outro processo.
- 15: ```
- 16: 
- 17: Causas mais comuns: **DBeaver conectado**, scraper rodando, notebook aberto.
- 18: 
- 19: Consequências no código:
- 20: - `localidades_db.conexao()` abre/fecha a cada operação (não mantém aberto).
- 21: - `LeadDatabase` mantém aberto durante o scraping — **não** abra outra conexão
- 22:   persistente no mesmo processo.
- 23: - `CacheIndisponivel` existe para degradar com aviso em vez de quebrar:
- 24:   o sistema segue usando as APIs (IBGE/OSM) sem cache.
+  9: O projeto suporta dois backends, escolhidos por `DB_ENGINE` no `.env`:
+ 10: 
+ 11: - `DB_ENGINE=postgres` → banco externo (`DATABASE_URL` ou `DB_*`).
+ 12: - `DB_ENGINE=duckdb` → arquivo local (`DUCKDB_PATH`, default `data/leads.duckdb`).
+ 13: 
+ 14: **Regra de ouro:** nenhum módulo além de `src/backend.py` importa `duckdb` ou
+ 15: `psycopg2`. Todo acesso passa por `backend.execute/query_df/query_all/bulk_upsert`.
+ 16: - Placeholder de parâmetro: use `backend.ph()` (`?` no DuckDB, `%s` no Postgres),
+ 17:   NUNCA hardcode.
+ 18: - `excluded.col` funciona no `ON CONFLICT` dos dois bancos.
+ 19: - A DDL/seed fica em `schema.py` (roda uma vez: `python src/schema.py`).
+ 20: 
+ 21: ### Armadilha do DuckDB: um processo por arquivo
+ 22: 
+ 23: **O `data/leads.duckdb` só pode ser aberto por UM processo.** Não existe
+ 24: "read-only compartilhado" — até `duckdb.connect(..., read_only=True)` falha:
  25: 
- 26: - ⚠️ **Um WAL pendente (`.wal`) indica dados não consolidados.** Se comitar o
- 27:   `.duckdb` com o programa aberto, o `.wal` (ignorado no Git) fica de fora e o
- 28:   commit sobe um estado desatualizado. Feche o programa antes de comitar.
- 29: 
- 30: ---
- 31: 
- 32: ## IBGE: não existe bairro na API de Localidades
- 33: 
- 34: A API retorna **estados, municípios, distritos e subdistritos**. Nada de bairro.
- 35: 
- 36: - `distritos` são divisões administrativas; em muitos municípios resumem-se à
- 37:   própria sede (mesmo nome da cidade).
- 38: - Exemplo real: **Canoas-RS = 1 distrito ("Canoas") e 0 subdistritos**.
- 39: - `obter_bairros` descarta o distrito-sede; se sobrarem `< MIN_BAIRROS`,
- 40:   complementa com OpenStreetMap.
- 41: - Cobertura: ~643 de 5.571 municípios têm distritos suficientes para dispensar OSM.
- 42: 
- 43: **Não "conserte" isso achando que é bug.** Para bairros oficiais existiria o
- 44: CNEFE 2022 (`ftp.ibge.gov.br/.../Censo_Demografico_2022/Arquivos_CNEFE/CSV/UF/`,
- 45: coluna `DSC_LOCALIDADE`, ex. `43_RS.zip` ≈ 236 MB) — **decisão do mantenedor:
- 46: não implementar por ora**, evoluir aos poucos.
- 47: 
- 48: ---
- 49: 
- 50: ## OpenStreetMap: instável por natureza
+ 26: ```
+ 27: IO Error: Cannot open file "...data\leads.duckdb":
+ 28: O arquivo já está sendo usado por outro processo.
+ 29: ```
+ 30: 
+ 31: Causas mais comuns: **DBeaver conectado**, scraper rodando, notebook aberto.
+ 32: 
+ 33: Consequências:
+ 34: - `localidades_db` abre/fecha a conexão a cada operação (não mantém aberto).
+ 35: - `LeadDatabase` mantém aberto durante o scraping — **não** abra outra conexão
+ 36:   persistente no mesmo processo.
+ 37: - `CacheIndisponivel` degrada com aviso em vez de quebrar.
+ 38: 
+ 39: ### Armadilha do PostgreSQL: senha com `@` na URL
+ 40: 
+ 41: Na `DATABASE_URL`, caracteres especiais da senha devem ser "percent-encoded"
+ 42: (`@` → `%40`, `:` → `%3A`, `/` → `%2F`). O `config.py` já decodifica com `unquote`.
+ 43: Ex.: `aojbfoeub@@@111` → `aojbfoeub%40%40%40111`.
+ 44: 
+ 45: ### Armadilha: identidade vs sequence (PostgreSQL)
+ 46: 
+ 47: No Postgres, `templates_whatsapp.id`, `whatsapp_envios_log.id` e
+ 48: `localidades_bairros.id` são colunas **IDENTITY**. O `lead_id` de `leads` é
+ 49: `integer` com sequence manual (`seq_leads_id`). Não assuma que todas as PKs se
+ 50: comportam igual.
  51: 
- 52: Os espelhos do Overpass e o Nominatim respondem `502`, `400` e `ReadTimeout`
- 53: com frequência. Regra de ouro:
- 54: 
- 55: > Falha de rede **não** significa "cidade sem bairros".
- 56: 
- 57: Por isso `_consultar_overpass` retorna `None` (serviço fora) em vez de
- 58: `{"elements": []}`, e `_descobrir_bairros` devolve `fonte=None` para **não
- 59: gravar** nada. A próxima execução tenta de novo. Se gravasse "cidade", o cache
- 60: ficaria envenenado para sempre.
- 61: 
- 62: ---
- 63: 
- 64: ## Cache: `bairros_fonte` precisa vir na leitura
- 65: 
- 66: Bug corrigido em 2026-10-29: `ler_municipios()` selecionava só
- 67: `id_municipio, nome`, então `_resolver_municipio` devolvia `bairros_fonte=None` e
- 68: `obter_bairros` **ia à API mesmo com cache quente**. Agora a query inclui
- 69: `uf` e `bairros_fonte`.
- 70: 
- 71: **Ao criar novas leituras de município, sempre inclua `bairros_fonte`.**
- 72: 
- 73: ---
- 74: 
- 75: ## Semântica de escrita (não inverter!)
+ 52: ---
+ 53: 
+ 54: ## IBGE: não existe bairro na API de Localidades
+ 55: 
+ 56: A API retorna **estados, municípios, distritos e subdistritos**. Nada de bairro.
+ 57: 
+ 58: - `distritos` são divisões administrativas; em muitos municípios resumem-se à
+ 59:   própria sede (mesmo nome da cidade).
+ 60: - Exemplo real: **Canoas-RS = 1 distrito ("Canoas") e 0 subdistritos**.
+ 61: - `obter_bairros` descarta o distrito-sede; se sobrarem `< MIN_BAIRROS`,
+ 62:   complementa com OpenStreetMap.
+ 63: - Cobertura: ~643 de 5.571 municípios têm distritos suficientes para dispensar OSM.
+ 64: 
+ 65: **Não "conserte" isso achando que é bug.** Para bairros oficiais existiria o
+ 66: CNEFE 2022 (`ftp.ibge.gov.br/.../Censo_Demografico_2022/Arquivos_CNEFE/CSV/UF/`,
+ 67: coluna `DSC_LOCALIDADE`, ex. `43_RS.zip` ≈ 236 MB) — **decisão do mantenedor:
+ 68: não implementar por ora**, evoluir aos poucos.
+ 69: 
+ 70: ---
+ 71: 
+ 72: ## OpenStreetMap: instável por natureza
+ 73: 
+ 74: Os espelhos do Overpass e o Nominatim respondem `502`, `400` e `ReadTimeout`
+ 75: com frequência. Regra de ouro:
  76: 
- 77: | Função | Comportamento |
- 78: |---|---|
- 79: | `salvar_bairros` | **autoritativo** por cidade: remove nomes ausentes **daquela** cidade |
- 80: | `salvar_distritos_bulk` | **aditivo**: nunca apaga bairros do OSM |
- 81: | `salvar_municipios` | UPSERT — **preserva** `bairros_fonte`/`bairros_atualizado_em` |
- 82: 
- 83: Se `salvar_distritos_bulk` virasse autoritativo, destruiria as listas do
- 84: OpenStreetMap em toda sincronização.
+ 77: > Falha de rede **não** significa "cidade sem bairros".
+ 78: 
+ 79: Por isso `_consultar_overpass` retorna `None` (serviço fora) em vez de
+ 80: `{"elements": []}`, e `_descobrir_bairros` devolve `fonte=None` para **não
+ 81: gravar** nada. A próxima execução tenta de novo. Se gravasse "cidade", o cache
+ 82: ficaria envenenado para sempre.
+ 83: 
+ 84: ---
  85: 
- 86: ---
+ 86: ## Cache: `bairros_fonte` precisa vir na leitura
  87: 
- 88: ## Flags `LOCALIDADES_*` são independentes
- 89: 
- 90: `USAR_CACHE` controla **leitura**; `SALVAR` controla **escrita**.
- 91: 
- 92: | USAR_CACHE | SALVAR | Efeito |
- 93: |---|---|---|
- 94: | true | true | padrão: lê do banco, grava o que faltar |
- 95: | false | true | ignora o banco, sempre API e regrava |
- 96: | true | false | lê do banco; o que falta vem da API sem gravar |
- 97: | false | false | sempre API, banco intocado |
+ 88: Bug corrigido em 2026-10-29: `ler_municipios()` selecionava só
+ 89: `id_municipio, nome`, então `_resolver_municipio` devolvia `bairros_fonte=None` e
+ 90: `obter_bairros` **ia à API mesmo com cache quente**. Agora a query inclui
+ 91: `uf` e `bairros_fonte`.
+ 92: 
+ 93: **Ao criar novas leituras de município, sempre inclua `bairros_fonte`.**
+ 94: 
+ 95: ---
+ 96: 
+ 97: ## Semântica de escrita (não inverter!)
  98: 
- 99: - `SALVAR=false` também desativa a criação de tabelas (`CRIAR_TABELAS`) e os
-100:   menus **3** e **4**.
-101: - As flags são lidas **no import**: mudar o `.env` exige reiniciar o programa.
-102: - Com `USAR_CACHE=false`, cada cidade baixa a lista da UF de novo (exceto pela
-103:   memoização em memória `_municipios_da_uf`, válida só na execução atual).
+ 99: | Função | Comportamento |
+100: |---|---|
+101: | `salvar_bairros` | **autoritativo** por cidade: remove nomes ausentes **daquela** cidade |
+102: | `salvar_distritos_bulk` | **aditivo**: nunca apaga bairros do OSM |
+103: | `salvar_municipios` | UPSERT — **preserva** `bairros_fonte`/`bairros_atualizado_em` |
 104: 
-105: ---
-106: 
-107: ## Cuidados ao editar arquivos (Windows/PowerShell)
-108: 
-109: - **Nunca** use `Get-Content ... -replace ... | Set-Content` para editar `.py`:
-110:   ele reescreve em ANSI e **corrompe acentuação** (dupla codificação / mojibake).
-111:   Use o editor (edit) ou grave via Python com `encoding="utf-8"`.
-112: - Grave sempre **UTF-8 sem BOM** (BOM quebra a primeira chave do `.env`).
-113: - Para testar, use o interpretador da venv: `venv\Scripts\python.exe`.
-114:   O `python` global do mantenedor é 3.15 e pode não ter as dependências.
-115: - Valide a acentuação após edições em lote: procure caracteres de dupla
-116:   codificação (por exemplo, `A` com til U+00C3 seguido de símbolo de moeda).
-117: 
-118: ---
-119: 
-120: ## WAHA: chatId `@c.us` vs `@lid` (HTTP 500)
-121: 
-122: Enviar `POST /api/sendText` com `chatId = 55DDDNUMERO@c.us` **falha com HTTP 500**
-123: para números recentes do WhatsApp. Esses números foram migrados para o formato
-124: **`@lid`** (hidden user ID).
+105: Se `salvar_distritos_bulk` virasse autoritativo, destruiria as listas do
+106: OpenStreetMap em toda sincronização.
+107: 
+108: ---
+109: 
+110: ## Flags `LOCALIDADES_*` são independentes
+111: 
+112: `USAR_CACHE` controla **leitura**; `SALVAR` controla **escrita**.
+113: 
+114: | USAR_CACHE | SALVAR | Efeito |
+115: |---|---|---|
+116: | true | true | padrão: lê do banco, grava o que faltar |
+117: | false | true | ignora o banco, sempre API e regrava |
+118: | true | false | lê do banco; o que falta vem da API sem gravar |
+119: | false | false | sempre API, banco intocado |
+120: 
+121: - `SALVAR=false` também desativa a escrita local e os menus **3** e **4**.
+122: - As flags são lidas **no import**: mudar o `.env` exige reiniciar o programa.
+123: - Com `USAR_CACHE=false`, cada cidade baixa a lista da UF de novo (exceto pela
+124:   memoização em memória `_municipios_da_uf`, válida só na execução atual).
 125: 
-126: - Diagnóstico: `GET /api/checkNumberStatus?session=default&phone=55DDD9XXXXXXXX`
-127:   responde `{"numberExists": true, "chatId": "143172869029943@lid"}`.
-128: - Correção: **sempre resolver o chatId via `checkNumberStatus` antes de enviar**,
-129:   em vez de montar `@c.us` na mão (é o que a documentação da WAHA recomenda para
-130:   números brasileiros).
-131: - O chatId resolvido é **cacheado** na coluna `leads.chat_id_waha` — a consulta
-132:   extra só acontece uma vez por lead.
-133: - ⚠️ O payload do `sendText` está correto (`{session, chatId, text}` + header
-134:   `X-Api-Key`); o erro 500 era **só** o formato do `chatId`, não o endpoint.
-135: 
-136: ---
-137: 
-138: ## `.env` e Git
-139: 
-140: - `.env` **é ignorado** (contém `WAHA_API_KEY`). `.env.example` **é versionado**.
-141: - Formato: `CHAVE=VALOR`. Comentários só em **linha própria** — comentário na
-142:   mesma linha vira parte do valor (`WAHA_LIMITE= # vazio` → `" # vazio"`).
-143: - Não use `export`/aspas desnecessárias; o loader tira aspas simples/duplas.
-144: - Nunca imprima nem comite segredos.
-145: 
-146: ---
-147: 
-148: ## Scraping: seletores frágeis
-149: 
-150: Dependem do DOM do Google Maps (podem mudar sem aviso):
-151: 
-152: | Dado | Seletor |
-153: |---|---|
-154: | lista de resultados | `div[role="feed"]` |
-155: | links de perfis | `a[href*="/maps/place/"]` |
-156: | nome | `h1` (ignora "Resultados" e vazio) |
-157: | endereço | `button[data-item-id="address"]` (`aria-label`) |
-158: | telefone | `button[data-item-id^="phone:tel:"]` (`aria-label`) |
-159: | site | `a[data-item-id="authority"]` |
-160: | Instagram | primeiro `a[href]` contendo `instagram.com` |
-161: 
-162: Bairro é extraído do endereço: `"Rua X, 123 - Bairro, Cidade - UF"` → parte
-163: entre `" - "` e `","`. Se não casar, `"Não Informado"`.
-164: 
-165: ---
-166: 
-167: ## Concorrência
+126: ---
+127: 
+128: ## Cuidados ao editar arquivos (Windows/PowerShell)
+129: 
+130: - **Nunca** use `Get-Content ... -replace ... | Set-Content` para editar `.py`:
+131:   ele reescreve em ANSI e **corrompe acentuação** (dupla codificação / mojibake).
+132:   Use o editor (edit) ou grave via Python com `encoding="utf-8"`.
+133: - Grave sempre **UTF-8 sem BOM** (BOM quebra a primeira chave do `.env`).
+134: - Para testar, use o interpretador da venv: `venv\Scripts\python.exe`.
+135:   O `python` global do mantenedor é 3.15 e pode não ter as dependências.
+136: - Valide a acentuação após edições em lote: procure caracteres de dupla
+137:   codificação (por exemplo, `A` com til U+00C3 seguido de símbolo de moeda).
+138: 
+139: ---
+140: 
+141: ## WAHA: chatId `@c.us` vs `@lid` (HTTP 500)
+142: 
+143: Enviar `POST /api/sendText` com `chatId = 55DDDNUMERO@c.us` **falha com HTTP 500**
+144: para números recentes do WhatsApp. Esses números foram migrados para o formato
+145: **`@lid`** (hidden user ID).
+146: 
+147: - Diagnóstico: `GET /api/checkNumberStatus?session=default&phone=55DDD9XXXXXXXX`
+148:   responde `{"numberExists": true, "chatId": "143172869029943@lid"}`.
+149: - Correção: **sempre resolver o chatId via `checkNumberStatus` antes de enviar**,
+150:   em vez de montar `@c.us` na mão (é o que a documentação da WAHA recomenda para
+151:   números brasileiros).
+152: - O chatId resolvido é **cacheado** na coluna `leads.chat_id_waha` — a consulta
+153:   extra só acontece uma vez por lead.
+154: - ⚠️ O payload do `sendText` está correto (`{session, chatId, text}` + header
+155:   `X-Api-Key`); o erro 500 era **só** o formato do `chatId`, não o endpoint.
+156: 
+157: ---
+158: 
+159: ## WAHA: cadência aleatória (anti-bloqueio)
+160: 
+161: Enviar com pausa fixa (ex.: 15s, 15s, 15s) é fácil de detectar e leva a bloqueio.
+162: 
+163: - `WAHA_CADENCIA="X:Y"` (ex.: `3:60` = 3 envios/minuto) faz os envios caírem em
+164:   **pontos aleatórios** dentro de cada janela de Y segundos → pausas variáveis.
+165: - Tem prioridade sobre `WAHA_INTERVALO` (pausa fixa, usada só se `WAHA_CADENCIA`
+166:   estiver vazio).
+167: - Implementação: `_pausas_cadencia(total, envios_janela, janela)` em `whatsapp.py`.
 168: 
-169: - `save_callback` é chamado **na thread principal** (dentro do loop de
-170:   `as_completed`), então não há escrita concorrente no DuckDB.
-171: - O cooldown anti-captcha usa `_cooldown_lock` + variável global `_cooldown_ate`.
-172: - `lock` protege a lista `vistos`/`todos_leads`.
-173: 
-174: ---
-175: 
-176: ## Coisas que parecem bug mas não são
-177: 
-178: - `"IBGE não publica bairros para X"` → cidade com 1 distrito (ver acima).
-179: - `"Base local ... sem bairros (fonte: cidade)"` → já tentou, o OSM não tinha nada.
-180: - `"LOCALIDADES_SALVAR=false: a base local não será alterada"` → modo leitura.
-181: - `"Aviso: base local ... indisponível (arquivo em uso)"` → feche o DBeaver.
-`````
+169: ---
+170: 
+171: ## `.env` e Git
+172: 
+173: - `.env` **é ignorado** (contém `WAHA_API_KEY`). `.env.example` **é versionado**.
+174: - Formato: `CHAVE=VALOR`. Comentários só em **linha própria** — comentário na
+175:   mesma linha vira parte do valor (`WAHA_LIMITE= # vazio` → `" # vazio"`).
+176: - Não use `export`/aspas desnecessárias; o loader tira aspas simples/duplas.
+177: - Nunca imprima nem comite segredos.
+178: 
+179: ---
+180: 
+181: ## Scraping: seletores frágeis
+182: 
+183: Dependem do DOM do Google Maps (podem mudar sem aviso):
+184: 
+185: | Dado | Seletor |
+186: |---|---|
+187: | lista de resultados | `div[role="feed"]` |
+188: | links de perfis | `a[href*="/maps/place/"]` |
+189: | nome | `h1` (ignora "Resultados" e vazio) |
+190: | endereço | `button[data-item-id="address"]` (`aria-label`) |
+191: | telefone | `button[data-item-id^="phone:tel:"]` (`aria-label`) |
+192: | site | `a[data-item-id="authority"]` |
+193: | Instagram | primeiro `a[href]` contendo `instagram.com` |
+194: 
+195: Bairro é extraído do endereço: `"Rua X, 123 - Bairro, Cidade - UF"` → parte
+196: entre `" - "` e `","`. Se não casar, `"Não Informado"`.
+197: 
+198: ---
+199: 
+200: ## Concorrência
+201: 
+202: - `save_callback` é chamado **na thread principal** (dentro do loop de
+203:   `as_completed`), então não há escrita concorrente no banco.
+204: - O cooldown anti-captcha usa `_cooldown_lock` + variável global `_cooldown_ate`.
+205: - `lock` protege a lista `vistos`/`todos_leads`.
+206: 
+207: ---
+208: 
+209: ## Coisas que parecem bug mas não são
+210: 
+211: - `"IBGE não publica bairros para X"` → cidade com 1 distrito (ver acima).
+212: - `"Base local ... sem bairros (fonte: cidade)"` → já tentou, o OSM não tinha nada.
+213: - `"LOCALIDADES_SALVAR=false: a base local não será alterada"` → modo leitura.
+214: - `"Aviso: base local ... indisponível (arquivo em uso)"` → feche o DBeaver.
+````
 
 ## File: .repomixignore
-`````
+````
  1: # Add patterns to ignore here, one per line
  2: # Example:
  3: # *.log
@@ -786,10 +1266,10 @@ requirements.txt
 10: # Ignorar arquivos gerados pelo próprio Repomix
 11: repomix-output.md
 12: repomix-output.xml
-`````
+````
 
 ## File: repomix-instrucao.md
-`````markdown
+````markdown
  1: # Instruções Mestras para o Assistente de IA (Map Scraper Project)
  2: 
  3: ## 1. Persona e Idioma
@@ -817,10 +1297,10 @@ requirements.txt
 25: - Não sugira refatorações massivas (reescrever o projeto inteiro) sem que seja explicitamente pedido.
 26: - Não adicione bibliotecas externas pesadas se a biblioteca padrão do Python ou as dependências atuais (Pandas, Playwright, DuckDB) já resolverem o problema.
 27: - Não ignore a estrutura de pastas atual (`src/`, `data/`, `output/`, `memory/`).
-`````
+````
 
 ## File: repomix.config.json
-`````json
+````json
  1: {
  2:   "$schema": "https://repomix.com/schemas/latest/schema.json",
  3:   "input": {
@@ -866,628 +1346,494 @@ requirements.txt
 43:     "encoding": "o200k_base"
 44:   }
 45: }
-`````
-
-## File: memory/README.md
-`````markdown
- 1: # memory/ — Memória do Projeto para IAs
- 2: 
- 3: Esta pasta contém documentação **resumida e densa** sobre o projeto Map Scraper,
- 4: escrita para ser lida por modelos de IA antes de alterar código.
- 5: 
- 6: ## Por que existe
- 7: 
- 8: Ler esses arquivos curtos daqui custa muito menos tokens do que reler todo o código.
- 9: Use esta pasta como **primeira fonte de contexto**.
-10: 
-11: ## Ordem de leitura recomendada
-12: 
-13: | # | Arquivo | Conteúdo |
-14: |---|---|---|
-15: | 1 | [00-resumo-projeto.md](./00-resumo-projeto.md) | O que o projeto faz, stack, estrutura |
-16: | 2 | [01-arquitetura-e-modulos.md](./01-arquitetura-e-modulos.md) | Cada módulo, funções principais, fluxos |
-17: | 3 | [02-decisoes-e-armadilhas.md](./02-decisoes-e-armadilhas.md) | Decisões técnicas, bugs conhecidos, cuidados |
-18: | 4 | [03-historico-de-mudancas.md](./03-historico-de-mudancas.md) | O que mudou recentemente e por quê |
-19: | 5 | [04-como-contribuir.md](./04-como-contribuir.md) | Padrões de código, logs, config, testes e documentação |
-20: 
-21: ## Regras de manutenção
-22: 
-23: - **Atualize ao mudar comportamento**, não a cada commit.
-24: - Mantenha cada arquivo curto (ideal: < 200 linhas). Detalhe fica no código.
-25: - Registre o **porquê** das decisões, não só o quê.
-26: - Nunca coloque segredos aqui (API keys, tokens). Use `.env`.
-27: - Datas no formato `AAAA-MM-DD`.
-28: 
-29: ## Arquivos que NÃO devem ser duplicados aqui
-30: 
-31: - `README.md` (raiz) — manual do usuário, instalação, uso.
-32: - `.env.example` — valores e comentários de cada variável.
-33: 
-34: ## Git force
-35: - Enviar
-36: git add -A; git commit -m "Atualização"; git push --force origin main
-37: 
-38: 
-39: ## git forçado
-40: - Envia
-41: git add -A; git commit -m "Melhorias no processo de coletas v3 $(Get-Date -Format 'yyyy-MM-dd HH:mm')"; git push --force-with-lease origin main
-42: - Recebe
-43: git fetch --all; git reset --hard origin/main
-`````
+````
 
 ## File: src/localidades_db.py
-`````python
+````python
   1: # src/localidades_db.py
-  2: """Cache local (DuckDB) da base de localidades do IBGE.
+  2: """Cache (PostgreSQL ou DuckDB) da base de localidades do IBGE.
   3: 
   4: Guarda apenas o essencial, para não inflar o banco:
   5:     localidades_estados     -> uf, nome
   6:     localidades_municipios  -> id_municipio, nome, uf + estado da coleta de bairros
   7:     localidades_bairros     -> id_municipio, nome, id_distrito
   8: 
-  9: O arquivo é o mesmo DuckDB dos leads (data/leads.duckdb). Cada operação abre e
- 10: fecha a conexão, então o cache nunca segura o banco travado durante o scraping.
+  9: Cada operação abre e fecha a conexão, então o cache nunca segura uma conexão
+ 10: aberta durante o scraping.
  11: """
- 12: import os
- 13: from contextlib import contextmanager
- 14: from datetime import datetime
- 15: 
- 16: import duckdb
- 17: import pandas as pd
+ 12: from contextlib import contextmanager
+ 13: from datetime import datetime
+ 14: 
+ 15: import pandas as pd
+ 16: 
+ 17: from src import backend
  18: 
- 19: DB_PATH_PADRAO = os.path.join("data", "leads.duckdb")
- 20: 
- 21: # Origem da lista de bairros gravada para uma cidade.
- 22: FONTE_IBGE = "ibge"           # distritos do IBGE (quantidade suficiente)
- 23: FONTE_OVERPASS = "overpass"   # complementado/obtido via OpenStreetMap
- 24: FONTE_CIDADE = "cidade"       # nenhum bairro usado: busca a cidade inteira
- 25: 
- 26: 
- 27: class CacheIndisponivel(Exception):
- 28:     """Não foi possível abrir ou gravar a base local (ex.: arquivo travado)."""
- 29: 
- 30: 
- 31: _DDL = (
- 32:     """
- 33:     CREATE TABLE IF NOT EXISTS localidades_estados (
- 34:         uf VARCHAR PRIMARY KEY,
- 35:         nome VARCHAR NOT NULL
- 36:     )
- 37:     """,
- 38:     """
- 39:     CREATE TABLE IF NOT EXISTS localidades_municipios (
- 40:         id_municipio BIGINT PRIMARY KEY,
- 41:         nome VARCHAR NOT NULL,
- 42:         uf VARCHAR NOT NULL,
- 43:         bairros_fonte VARCHAR,
- 44:         bairros_atualizado_em TIMESTAMP
- 45:     )
- 46:     """,
- 47:     """
- 48:     CREATE TABLE IF NOT EXISTS localidades_bairros (
- 49:         id_municipio BIGINT NOT NULL,
- 50:         nome VARCHAR NOT NULL,
- 51:         id_distrito BIGINT,
- 52:         PRIMARY KEY (id_municipio, nome)
- 53:     )
- 54:     """,
- 55: )
- 56: 
- 57: 
- 58: # Se false, nenhuma DDL é executada: o cache é aberto somente para leitura.
- 59: # Definido por `src/locations.py` a partir de LOCALIDADES_SALVAR.
- 60: CRIAR_TABELAS = True
+ 19: # Origem da lista de bairros gravada para uma cidade.
+ 20: FONTE_IBGE = "ibge"           # distritos do IBGE (quantidade suficiente)
+ 21: FONTE_OVERPASS = "overpass"   # complementado/obtido via OpenStreetMap
+ 22: FONTE_CIDADE = "cidade"       # nenhum bairro usado: busca a cidade inteira
+ 23: 
+ 24: 
+ 25: class CacheIndisponivel(Exception):
+ 26:     """Não foi possível abrir/gravar a base de localidades (ex.: servidor fora)."""
+ 27: 
+ 28: 
+ 29: @contextmanager
+ 30: def _conexao():
+ 31:     """Abre uma conexão transacional; commit no fim, rollback em caso de erro."""
+ 32:     try:
+ 33:         conn = backend.conectar()
+ 34:     except Exception as e:
+ 35:         raise CacheIndisponivel(f"não foi possível conectar ao banco: {e}") from e
+ 36:     try:
+ 37:         yield conn
+ 38:         backend.commit(conn)
+ 39:     except Exception:
+ 40:         if not backend.IS_DUCKDB:
+ 41:             conn.rollback()
+ 42:         raise
+ 43:     finally:
+ 44:         backend.close(conn)
+ 45: 
+ 46: 
+ 47: def _df(conn, sql, params=None):
+ 48:     return backend.query_df(conn, sql, params)
+ 49: 
+ 50: 
+ 51: def _inserir_upsert(conn, table, columns, df, conflict, set_clause):
+ 52:     backend.bulk_upsert(
+ 53:         conn,
+ 54:         table=table,
+ 55:         columns=columns,
+ 56:         rows=backend.df_to_rows(df),
+ 57:         conflict=conflict,
+ 58:         set_clause=set_clause,
+ 59:     )
+ 60: 
  61: 
- 62: 
- 63: @contextmanager
- 64: def conexao(db_path=None):
- 65:     caminho = db_path or DB_PATH_PADRAO
- 66:     diretorio = os.path.dirname(caminho)
- 67:     if diretorio:
- 68:         os.makedirs(diretorio, exist_ok=True)
- 69:     try:
- 70:         con = duckdb.connect(caminho)
- 71:     except Exception as e:
- 72:         raise CacheIndisponivel(f"{caminho}: {e}") from e
- 73:     try:
- 74:         if CRIAR_TABELAS:
- 75:             for ddl in _DDL:
- 76:                 con.execute(ddl)
- 77:         yield con
- 78:     finally:
- 79:         con.close()
- 80: 
- 81: 
- 82: def _ler(con, sql, params=None):
- 83:     """Executa uma leitura, traduzindo 'tabela não existe' em CacheIndisponivel."""
- 84:     try:
- 85:         return con.execute(sql, params) if params else con.execute(sql)
- 86:     except duckdb.CatalogException as e:
- 87:         raise CacheIndisponivel(
- 88:             "tabelas de localidades não existem neste banco (rode a sincronização no menu)"
- 89:         ) from e
- 90: 
- 91: 
- 92: def _inserir_lote(con, df, sql):
- 93:     if df is None or df.empty:
- 94:         return
- 95:     con.register("_lote", df)
- 96:     try:
- 97:         con.execute(sql)
- 98:     finally:
- 99:         con.unregister("_lote")
-100: 
-101: 
-102: def ler_estados(db_path=None):
-103:     with conexao(db_path) as con:
-104:         df = _ler(con, "SELECT uf, nome FROM localidades_estados ORDER BY nome").df()
-105:     return df.to_dict("records")
+ 62: def ler_estados():
+ 63:     with _conexao() as conn:
+ 64:         df = _df(conn, "SELECT uf, nome FROM localidades_estados ORDER BY nome")
+ 65:     return df.to_dict("records")
+ 66: 
+ 67: 
+ 68: def salvar_estados(registros):
+ 69:     df = pd.DataFrame(list(registros), columns=["uf", "nome"]).drop_duplicates("uf")
+ 70:     with _conexao() as conn:
+ 71:         _inserir_upsert(conn, "localidades_estados", ["uf", "nome"], df,
+ 72:                         conflict="uf", set_clause="nome = excluded.nome")
+ 73:     return len(df)
+ 74: 
+ 75: 
+ 76: def ler_municipios(uf):
+ 77:     with _conexao() as conn:
+ 78:         df = _df(conn, """
+ 79:             SELECT id_municipio, nome, uf, bairros_fonte
+ 80:             FROM localidades_municipios WHERE uf = %s ORDER BY nome
+ 81:         """.replace("%s", backend.ph()), [uf])
+ 82:     return df.to_dict("records")
+ 83: 
+ 84: 
+ 85: def ler_municipios_pendentes(uf):
+ 86:     """Municípios da UF cujos bairros ainda não foram resolvidos (bairros_fonte nulo)."""
+ 87:     with _conexao() as conn:
+ 88:         df = _df(conn, """
+ 89:             SELECT id_municipio, nome
+ 90:             FROM localidades_municipios
+ 91:             WHERE uf = %s AND bairros_fonte IS NULL
+ 92:             ORDER BY nome
+ 93:         """.replace("%s", backend.ph()), [uf])
+ 94:     return df.to_dict("records")
+ 95: 
+ 96: 
+ 97: def salvar_municipios(registros):
+ 98:     df = pd.DataFrame(list(registros), columns=["id_municipio", "nome", "uf"])
+ 99:     df = df.dropna(subset=["id_municipio"]).drop_duplicates("id_municipio")
+100:     with _conexao() as conn:
+101:         # UPSERT preserva bairros_fonte/bairros_atualizado_em já gravados.
+102:         _inserir_upsert(conn, "localidades_municipios", ["id_municipio", "nome", "uf"], df,
+103:                         conflict="id_municipio",
+104:                         set_clause="nome = excluded.nome, uf = excluded.uf")
+105:     return len(df)
 106: 
 107: 
-108: def salvar_estados(registros, db_path=None):
-109:     df = pd.DataFrame(list(registros), columns=["uf", "nome"]).drop_duplicates("uf")
-110:     with conexao(db_path) as con:
-111:         _inserir_lote(con, df, """
-112:             INSERT INTO localidades_estados (uf, nome)
-113:             SELECT uf, nome FROM _lote
-114:             ON CONFLICT (uf) DO UPDATE SET nome = excluded.nome
-115:         """)
-116:     return len(df)
-117: 
-118: 
-119: def ler_municipios(uf, db_path=None):
-120:     with conexao(db_path) as con:
-121:         df = _ler(con,
-122:             """SELECT id_municipio, nome, uf, bairros_fonte
-123:                FROM localidades_municipios WHERE uf = ? ORDER BY nome""",
-124:             [uf],
-125:         ).df()
-126:     return df.to_dict("records")
+108: def buscar_municipio(cidade, uf):
+109:     """Retorna {id_municipio, nome, uf, bairros_fonte} ou None se não estiver na base."""
+110:     p = backend.ph()
+111:     with _conexao() as conn:
+112:         linha = backend.query_one(conn, f"""
+113:             SELECT id_municipio, nome, uf, bairros_fonte
+114:             FROM localidades_municipios
+115:             WHERE uf = {p} AND lower(nome) = lower({p})
+116:             LIMIT 1
+117:         """, [uf, cidade])
+118:     if not linha:
+119:         return None
+120:     return {
+121:         "id_municipio": linha[0],
+122:         "nome": linha[1],
+123:         "uf": linha[2],
+124:         "bairros_fonte": linha[3],
+125:     }
+126: 
 127: 
-128: 
-129: def ler_municipios_pendentes(uf, db_path=None):
-130:     """Municípios da UF cujos bairros ainda não foram resolvidos (bairros_fonte nulo)."""
-131:     with conexao(db_path) as con:
-132:         df = _ler(con, """
-133:             SELECT id_municipio, nome
-134:             FROM localidades_municipios
-135:             WHERE uf = ? AND bairros_fonte IS NULL
-136:             ORDER BY nome
-137:         """, [uf]).df()
-138:     return df.to_dict("records")
-139: 
-140: 
-141: def salvar_municipios(registros, db_path=None):
-142:     df = pd.DataFrame(list(registros), columns=["id_municipio", "nome", "uf"])
-143:     df = df.dropna(subset=["id_municipio"]).drop_duplicates("id_municipio")
-144:     with conexao(db_path) as con:
-145:         # UPSERT preserva bairros_fonte/bairros_atualizado_em já gravados.
-146:         _inserir_lote(con, df, """
-147:             INSERT INTO localidades_municipios (id_municipio, nome, uf)
-148:             SELECT id_municipio, nome, uf FROM _lote
-149:             ON CONFLICT (id_municipio) DO UPDATE SET
-150:                 nome = excluded.nome,
-151:                 uf = excluded.uf
-152:         """)
-153:     return len(df)
+128: def ler_bairros(id_municipio):
+129:     with _conexao() as conn:
+130:         df = _df(conn,
+131:             "SELECT nome FROM localidades_bairros WHERE id_municipio = %s ORDER BY nome"
+132:             .replace("%s", backend.ph()), [int(id_municipio)],
+133:         )
+134:     return df["nome"].tolist()
+135: 
+136: 
+137: def _normalizar_bairros(registros):
+138:     linhas = []
+139:     for item in registros or []:
+140:         if isinstance(item, dict):
+141:             nome = str(item.get("nome") or "").strip()
+142:             id_distrito = item.get("id_distrito")
+143:         else:
+144:             nome = str(item or "").strip()
+145:             id_distrito = None
+146:         if nome:
+147:             linhas.append({"nome": nome, "id_distrito": id_distrito})
+148: 
+149:     df = pd.DataFrame(linhas, columns=["nome", "id_distrito"])
+150:     if df.empty:
+151:         return df
+152:     df["id_distrito"] = df["id_distrito"].astype("Int64")
+153:     return df.drop_duplicates("nome")
 154: 
 155: 
-156: def buscar_municipio(cidade, uf, db_path=None):
-157:     """Retorna {id_municipio, nome, uf, bairros_fonte} ou None se não estiver na base."""
-158:     with conexao(db_path) as con:
-159:         linha = _ler(con, """
-160:             SELECT id_municipio, nome, uf, bairros_fonte
-161:             FROM localidades_municipios
-162:             WHERE uf = ? AND lower(nome) = lower(?)
-163:             LIMIT 1
-164:         """, [uf, cidade]).fetchone()
-165:     if not linha:
-166:         return None
-167:     return {
-168:         "id_municipio": linha[0],
-169:         "nome": linha[1],
-170:         "uf": linha[2],
-171:         "bairros_fonte": linha[3],
-172:     }
-173: 
-174: 
-175: def ler_bairros(id_municipio, db_path=None):
-176:     with conexao(db_path) as con:
-177:         df = _ler(con,
-178:             "SELECT nome FROM localidades_bairros WHERE id_municipio = ? ORDER BY nome",
-179:             [int(id_municipio)],
-180:         ).df()
-181:     return df["nome"].tolist()
-182: 
-183: 
-184: def _normalizar_bairros(registros):
-185:     linhas = []
-186:     for item in registros or []:
-187:         if isinstance(item, dict):
-188:             nome = str(item.get("nome") or "").strip()
-189:             id_distrito = item.get("id_distrito")
-190:         else:
-191:             nome = str(item or "").strip()
-192:             id_distrito = None
-193:         if nome:
-194:             linhas.append({"nome": nome, "id_distrito": id_distrito})
+156: def salvar_bairros(id_municipio, registros, fonte):
+157:     """Grava a lista final de bairros de uma cidade e marca a origem da coleta.
+158: 
+159:     A lista é autoritativa para a cidade: bairros que não estão nela são
+160:     removidos (delete da cidade + re-insert), para o cache não acumular nomes
+161:     de uma coleta anterior. `fonte` = 'ibge', 'overpass' ou 'cidade'.
+162:     """
+163:     id_municipio = int(id_municipio)
+164:     df = _normalizar_bairros(registros)
+165: 
+166:     with _conexao() as conn:
+167:         p = backend.ph()
+168:         if df.empty:
+169:             backend.execute(conn, f"DELETE FROM localidades_bairros WHERE id_municipio = {p}",
+170:                             [id_municipio])
+171:         else:
+172:             df.insert(0, "id_municipio", id_municipio)
+173:             # Autoritativo por cidade: apaga tudo da cidade e reinsere.
+174:             backend.execute(conn, f"DELETE FROM localidades_bairros WHERE id_municipio = {p}",
+175:                             [id_municipio])
+176:             _inserir_upsert(
+177:                 conn, "localidades_bairros", ["id_municipio", "nome", "id_distrito"], df,
+178:                 conflict="id_municipio, nome",
+179:                 set_clause="id_distrito = excluded.id_distrito",
+180:             )
+181: 
+182:         backend.execute(conn, f"""
+183:             UPDATE localidades_municipios
+184:             SET bairros_fonte = {p}, bairros_atualizado_em = {p}
+185:             WHERE id_municipio = {p}
+186:         """, [fonte, datetime.now(), id_municipio])
+187:     return len(df)
+188: 
+189: 
+190: def salvar_distritos_bulk(distritos, min_bairros=3):
+191:     """Grava todos os distritos do IBGE de uma vez (sincronização completa).
+192: 
+193:     É aditivo (upsert por id_municipio+nome): não apaga bairros que já existem,
+194:     para não destruir listas complementadas pelo OpenStreetMap.
 195: 
-196:     df = pd.DataFrame(linhas, columns=["nome", "id_distrito"])
-197:     if df.empty:
-198:         return df
-199:     df["id_distrito"] = df["id_distrito"].astype("Int64")
-200:     return df.drop_duplicates("nome")
-201: 
+196:     Marca como 'ibge' apenas os municípios com pelo menos `min_bairros` distritos
+197:     úteis (desconsiderando o distrito que tem o mesmo nome da cidade).
+198:     """
+199:     df = pd.DataFrame(list(distritos), columns=["id_municipio", "nome", "id_distrito"])
+200:     df = df.dropna(subset=["id_municipio", "nome"]).drop_duplicates(["id_municipio", "nome"])
+201:     df["id_distrito"] = df["id_distrito"].astype("Int64")
 202: 
-203: def salvar_bairros(id_municipio, registros, fonte, db_path=None):
-204:     """Grava a lista final de bairros de uma cidade e marca a origem da coleta.
-205: 
-206:     A lista é autoritativa para a cidade: bairros que não estão nela são
-207:     removidos, para o cache não acumular nomes de uma coleta anterior.
-208:     `fonte` = 'ibge', 'overpass' ou 'cidade' (sem bairros úteis).
-209:     """
-210:     id_municipio = int(id_municipio)
-211:     df = _normalizar_bairros(registros)
-212: 
-213:     with conexao(db_path) as con:
-214:         if df.empty:
-215:             con.execute(
-216:                 "DELETE FROM localidades_bairros WHERE id_municipio = ?", [id_municipio]
-217:             )
-218:         else:
-219:             df.insert(0, "id_municipio", id_municipio)
-220:             con.register("_lote", df)
-221:             try:
-222:                 con.execute("""
-223:                     DELETE FROM localidades_bairros
-224:                     WHERE id_municipio = ?
-225:                       AND nome NOT IN (SELECT nome FROM _lote)
-226:                 """, [id_municipio])
-227:                 con.execute("""
-228:                     INSERT OR REPLACE INTO localidades_bairros (id_municipio, nome, id_distrito)
-229:                     SELECT id_municipio, nome, id_distrito FROM _lote
-230:                 """)
-231:             finally:
-232:                 con.unregister("_lote")
-233: 
-234:         con.execute("""
-235:             UPDATE localidades_municipios
-236:             SET bairros_fonte = ?, bairros_atualizado_em = ?
-237:             WHERE id_municipio = ?
-238:         """, [fonte, datetime.now(), id_municipio])
-239:     return len(df)
-240: 
-241: 
-242: def salvar_distritos_bulk(distritos, min_bairros=3, db_path=None):
-243:     """Grava todos os distritos do IBGE de uma vez (sincronização completa).
-244: 
-245:     É aditivo (INSERT OR REPLACE por id_municipio+nome): não apaga bairros que já
-246:     existem, para não destruir listas complementadas pelo OpenStreetMap.
-247: 
-248:     Marca como 'ibge' apenas os municípios com pelo menos `min_bairros` distritos
-249:     úteis (ou seja, desconsiderando o distrito que tem o mesmo nome da cidade).
-250:     Os demais continuam sem fonte definida e serão complementados via Overpass
-251:     na primeira consulta.
-252:     """
-253:     df = pd.DataFrame(list(distritos), columns=["id_municipio", "nome", "id_distrito"])
-254:     df = df.dropna(subset=["id_municipio", "nome"]).drop_duplicates(["id_municipio", "nome"])
-255:     df["id_distrito"] = df["id_distrito"].astype("Int64")
-256: 
-257:     with conexao(db_path) as con:
-258:         _inserir_lote(con, df, """
-259:             INSERT OR REPLACE INTO localidades_bairros (id_municipio, nome, id_distrito)
-260:             SELECT id_municipio, nome, id_distrito FROM _lote
-261:         """)
-262:         con.execute("DROP TABLE IF EXISTS _cobertura")
-263:         con.execute("""
-264:             CREATE TEMP TABLE _cobertura AS
-265:             SELECT b.id_municipio
-266:             FROM localidades_bairros b
-267:             JOIN localidades_municipios m ON m.id_municipio = b.id_municipio
-268:             WHERE lower(b.nome) <> lower(m.nome)
-269:             GROUP BY b.id_municipio
-270:             HAVING COUNT(*) >= ?
-271:         """, [int(min_bairros)])
-272:         con.execute("""
-273:             UPDATE localidades_municipios
-274:             SET bairros_fonte = ?, bairros_atualizado_em = ?
-275:             WHERE bairros_fonte IS NULL
-276:               AND id_municipio IN (SELECT id_municipio FROM _cobertura)
-277:         """, [FONTE_IBGE, datetime.now()])
-278:         con.execute("DROP TABLE IF EXISTS _cobertura")
-279:     return len(df)
-280: 
-281: 
-282: def estatisticas(db_path=None):
-283:     with conexao(db_path) as con:
-284:         estados = _ler(con, "SELECT COUNT(*) FROM localidades_estados").fetchone()[0]
-285:         municipios = _ler(con, "SELECT COUNT(*) FROM localidades_municipios").fetchone()[0]
-286:         bairros = _ler(con, "SELECT COUNT(*) FROM localidades_bairros").fetchone()[0]
-287:         prontas = _ler(con, """
-288:             SELECT COUNT(*) FROM localidades_municipios WHERE bairros_fonte IS NOT NULL
-289:         """).fetchone()[0]
-290:     return {
-291:         "estados": estados,
-292:         "municipios": municipios,
-293:         "bairros": bairros,
-294:         "cidades_prontas": prontas,
-295:     }
-`````
-
-## File: .env.example
-`````
-  1: # =============================================================================
-  2: # MAP SCRAPER - arquivo de exemplo de configuração
-  3: # -----------------------------------------------------------------------------
-  4: # Copie para `.env` e ajuste:
-  5: #     Copy-Item .env.example .env
-  6: #
-  7: # REGRAS IMPORTANTES
-  8: #  - Formato: CHAVE=VALOR, uma por linha.
-  9: #  - Comentários (linhas que começam com #) podem ficar à vontade, mas SEMPRE em
- 10: #    linha própria. Não coloque comentário na mesma linha do valor, porque ele
- 11: #    seria lido como parte do valor.
- 12: #  - true/false: também aceita 1/0, sim/não, s/yes/on.
- 13: #  - O arquivo `.env` NÃO é versionado no Git (contém a API key da WAHA).
- 14: # =============================================================================
- 15: 
- 16: 
- 17: # =============================================================================
- 18: # WHATSAPP - WAHA (WhatsApp HTTP API)
- 19: # =============================================================================
- 20: 
- 21: # URL base da sua instância WAHA (Docker local, por exemplo).
- 22: # Usada em todas as chamadas de envio. Não coloque a barra final.
- 23: WAHA_API_URL=http://localhost:3000
- 24: 
- 25: # Chave de API da WAHA. É o valor de WHATSAPP_API_KEY no .env do Docker/init-waha.
- 26: # Deixe vazio se a sua instância estiver sem autenticação.
- 27: WAHA_API_KEY=
- 28: 
- 29: # Nome da sessão do WhatsApp já conectada (lida por QR Code), normalmente `default`.
- 30: # Precisa ser exatamente o nome que aparece em /api/sessions da WAHA.
- 31: WAHA_SESSION=default
- 32: 
- 33: # Liga/desliga TODO o envio de WhatsApp.
- 34: #   true  = o menu "2 - Enviar mensagens WhatsApp" funciona normalmente.
- 35: #   false = o menu avisa que o envio está desativado e não faz nada.
- 36: # Isso NÃO afeta a coleta de leads, apenas o disparo de mensagens.
- 37: WAHA_ATIVO=true
- 38: 
- 39: # Atalho que pula o menu e vai direto para o envio, sem coletar nada.
- 40: #   true  = equivale a rodar: python src/main.py --so-enviar
- 41: #   false = abre o menu normal (coleta + envio).
- 42: # Útil para rodar uma campanha agendada, por exemplo.
- 43: SOMENTE_ENVIO=false
- 44: 
- 45: # Pausa em SEGUNDOS entre um envio e o próximo (13s ≈ 4-5 mensagens por minuto).
- 46: # Pausas muito curtas aumentam o risco de banimento do número.
- 47: WAHA_INTERVALO=13
- 48: 
- 49: # Quantidade máxima de leads por campanha. Vazio = sem limite (envia todos
- 50: # os pendentes). Só conta leads celulares, ativos e ainda não enviados.
- 51: WAHA_LIMITE=
- 52: 
- 53: 
- 54: # =============================================================================
- 55: # BASE DE LOCALIDADES (IBGE) - cache em DuckDB: tabelas localidades_*
- 56: # -----------------------------------------------------------------------------
- 57: # As duas flags abaixo são independentes. Combinações possíveis:
- 58: #
- 59: #   USAR_CACHE  SALVAR   O que acontece
- 60: #   true        true     usa o banco; só vai à API do que falta e grava (padrão)
- 61: #   false       true     ignora o banco, sempre vai à API e regrava (força refresh)
- 62: #   true        false    usa o banco; o que falta vai à API mas NÃO é gravado
- 63: #   false       false    sempre API, e o banco nunca é tocado (somente leitura)
- 64: # =============================================================================
- 65: 
- 66: # Consultar a base local ANTES da API do IBGE?
- 67: #   true  = se o dado já existe no DuckDB, nem chama a internet (rápido).
- 68: #   false = sempre chama a API do IBGE, mesmo que o dado já esteja no banco.
- 69: LOCALIDADES_USAR_CACHE=true
- 70: 
- 71: # Permitir GRAVAR na base local?
- 72: #   true  = pode inserir/atualizar (UPSERT) os estados, municípios e bairros.
- 73: #   false = modo somente leitura: nada é gravado e nem as tabelas são criadas.
- 74: # ATENÇÃO: com false, os menus "3 - Sincronizar" e "4 - Aquecer bairros" ficam
- 75: # desativados, e cada execução consulta as APIs de novo.
- 76: LOCALIDADES_SALVAR=true
- 77: 
- 78: # Mínimo de distritos do IBGE para considerar a cidade "coberta" pelo IBGE.
- 79: # A API de Localidades do IBGE tem distritos (não bairros). Cidade com menos
- 80: # distritos que este número é complementada com o OpenStreetMap.
- 81: # Exemplo: Campinas-SP tem 7 distritos -> usa só o IBGE.
- 82: #          Canoas-RS tem 1 distrito (a sede) -> vai para o OpenStreetMap.
- 83: LOCALIDADES_MIN_BAIRROS=3
- 84: 
- 85: # Pausa em SEGUNDOS entre cidades no menu "4 - Aquecer bairros de uma UF".
- 86: # Só é aplicada quando a cidade precisou do OpenStreetMap (Nominatim permite
- 87: # ~1 requisição por segundo). Cidades resolvidas pelo IBGE não esperam.
- 88: AQUECER_PAUSA_SEGUNDOS=2
- 89: 
- 90: 
- 91: # =============================================================================
- 92: # GOOGLE MAPS - captcha / bloqueio ("tráfego incomum")
- 93: # -----------------------------------------------------------------------------
- 94: # Quando o Google bloqueia, o robô pausa e tenta de novo. Se continuar bloqueado,
- 95: # ele aborta APENAS aquela área e mantém os leads já coletados.
- 96: # =============================================================================
- 97: 
- 98: # Quantas tentativas por página antes de desistir da área.
- 99: #   1  = não tenta de novo, só pausa uma vez e desiste.
-100: #   2  = pausa e tenta mais uma vez (padrão).
-101: # Valores altos aumentam o risco de piorar o bloqueio.
-102: CAPTCHA_MAX_TENTATIVAS=2
-103: 
-104: # Pausa longa em SEGUNDOS feita pela thread que recebeu o captcha antes de
-105: # tentar a mesma página novamente.
-106: CAPTCHA_PAUSA_SEGUNDOS=300
-107: 
-108: # Pausa compartilhada em SEGUNDOS aplicada a TODAS as threads assim que uma
-109: # delas detecta bloqueio (evita que as outras continuem martelando o Google).
-110: CAPTCHA_PAUSA_GLOBAL_SEGUNDOS=180
-`````
+203:     with _conexao() as conn:
+204:         p = backend.ph()
+205:         _inserir_upsert(
+206:             conn, "localidades_bairros", ["id_municipio", "nome", "id_distrito"], df,
+207:             conflict="id_municipio, nome",
+208:             set_clause="id_distrito = excluded.id_distrito",
+209:         )
+210:         backend.execute(conn, f"""
+211:             UPDATE localidades_municipios
+212:             SET bairros_fonte = {p}, bairros_atualizado_em = {p}
+213:             WHERE bairros_fonte IS NULL
+214:               AND id_municipio IN (
+215:                   SELECT b.id_municipio
+216:                   FROM localidades_bairros b
+217:                   JOIN localidades_municipios mm ON mm.id_municipio = b.id_municipio
+218:                   WHERE lower(b.nome) <> lower(mm.nome)
+219:                   GROUP BY b.id_municipio
+220:                   HAVING COUNT(*) >= {p}
+221:               )
+222:         """, [FONTE_IBGE, datetime.now(), int(min_bairros)])
+223:     return len(df)
+224: 
+225: 
+226: def estatisticas():
+227:     with _conexao() as conn:
+228:         def _count(sql):
+229:             return backend.query_one(conn, sql)[0]
+230:         estados = _count("SELECT COUNT(*) FROM localidades_estados")
+231:         municipios = _count("SELECT COUNT(*) FROM localidades_municipios")
+232:         bairros = _count("SELECT COUNT(*) FROM localidades_bairros")
+233:         prontas = _count("SELECT COUNT(*) FROM localidades_municipios WHERE bairros_fonte IS NOT NULL")
+234:     return {
+235:         "estados": estados,
+236:         "municipios": municipios,
+237:         "bairros": bairros,
+238:         "cidades_prontas": prontas,
+239:     }
+````
 
 ## File: memory/03-historico-de-mudancas.md
-`````markdown
+````markdown
   1: # 03 — Histórico de Mudanças
   2: 
   3: Registro do que mudou, por quê e o que ficou pendente. Mais recente primeiro.
   4: 
   5: ---
   6: 
-  7: ## 2026-10-30
+  7: ## 2026-10-31
   8: 
-  9: ### Templates de mensagem de WhatsApp (tabela + markdown)
+  9: ### Migração para PostgreSQL + suporte dual (PostgreSQL/DuckDB)
  10: 
- 11: - Nova tabela `templates_whatsapp` (`id`, `mensagem`, `descricao`, `ativo`),
- 12:   criada e seedada no `LeadDatabase.__init__` (idempotente, `id=1` =
- 13:   "Apresentação Agendamento Já").
- 14: - `listar_templates_ativos()` retorna só os ativos para o menu de envio.
- 15: - `_limpar_markdown_whatsapp` remove `**negrito**` e converte `[rótulo](url)` em
- 16:   texto plano antes do envio (o template usa markdown; o WhatsApp não renderiza).
- 17: 
- 18: ### Menu de envio: template + filtros + teste
- 19: 
- 20: - `enviar_whatsapp_menu()` agora: escolhe template → aplica filtros → pergunta se
- 21:   quer **teste de envio** → confirma e dispara.
- 22: - Filtros de envio (menu "FILTROS DE ENVIO"): 0 todos / 1 por número / 2 por
- 23:   cidade / 3 por nicho. Número aceita parte e compara só dígitos.
- 24: - `testar_envio()`: digita um número com DDD ou escolhe um lead pendente.
- 25: - `disparar_campanha` passou a aceitar `leads` (DataFrame já filtrado) — sem isso
- 26:   os filtros eram ignorados no disparo (ele reconsultava o banco).
- 27: 
- 28: ### Correção crítica: chatId `@lid` vs `@c.us` (WAHA)
- 29: 
- 30: - **Sintoma:** `500 Server Error` no `/api/sendText` para o número do mantenedor.
- 31: - **Causa:** número recente usa `@lid`; enviar `@c.us` retorna HTTP 500.
- 32: - **Correção:** `_resolver_chatid_waha` consulta `/api/checkNumberStatus` e usa o
- 33:   chatId retornado; fallback `@c.us` para números antigos.
- 34: - **Cache:** coluna `leads.chat_id_waha` + `salvar_chat_id_waha` — a resolução é
- 35:   feita uma única vez por lead (menos chamadas e reenvio mais rápido).
- 36: - `data_envio_whatsapp` continua gravada só no sucesso; `status_whatsapp` em
- 37:   `enviado`/`falhou`.
+ 11: - Banco externo PostgreSQL (`vps.agendamentoja.com/leads_db`) + mantido o DuckDB
+ 12:   local como alternativa offline.
+ 13: - Novo `src/backend.py`: abstrai conexão, placeholder (`?`/`%s`), leitura
+ 14:   (DataFrame/tupla) e bulk upsert entre os dois bancos. `database.py`,
+ 15:   `localidades_db.py` e `schema.py` não importam mais `duckdb`/`psycopg2`.
+ 16: - `config.py` lê `DB_ENGINE` (postgres|duckdb), `DATABASE_URL` e `DUCKDB_PATH`.
+ 17:   Inferência: DUCKDB_PATH → duckdb; senão DATABASE_URL → postgres; senão duckdb.
+ 18: - `schema.py` reescrito para os dois bancos; corrige o gap da tabela `leads`
+ 19:   (PK `lead_id` + UNIQUE `(nome,cidade)` + default `nextval('seq_leads_id')`).
+ 20: - `requirements.txt`: readicionado `duckdb` + `psycopg2-binary`.
+ 21: - `.env`: seção "BANCO DE DADOS — engine independente" com `DATABASE_URL` (senha
+ 22:   com `@` percent-encoded) e config antiga comentada como referência.
+ 23: 
+ 24: ### Cadência aleatória de envio WhatsApp (anti-bloqueio)
+ 25: 
+ 26: - Nova `WAHA_CADENCIA="X:Y"` no `.env` (ex.: `3:60` = 3 envios por minuto).
+ 27: - `whatsapp.py`: `_parse_cadencia` + `_pausas_cadencia` distribuem os envios em
+ 28:   pontos **aleatórios** dentro de cada janela (pausas variáveis, não fixas).
+ 29: - Tem prioridade sobre `WAHA_INTERVALO` (fixo). `WAHA_CADENCIA` vazio → usa o fixo.
+ 30: 
+ 31: ### Tabela `whatsapp_envios_log` (rastreamento)
+ 32: 
+ 33: - Log por envio com `lead_id`, `telefone` (dígitos) e `telefone_normalizado`
+ 34:   (55DDDNUMERO), `chat_id`, `status`, `mensagem`, `payload`, `erro`, `data_envio`.
+ 35: - JOIN pronto por `lead_id` ou `telefone`.
+ 36: 
+ 37: ---
  38: 
- 39: ---
+ 39: ## 2026-10-30
  40: 
- 41: ## 2026-10-29
+ 41: ### Templates de mensagem de WhatsApp (tabela + markdown)
  42: 
- 43: ### Memória do projeto para IA
- 44: 
- 45: - Criada a pasta `memory/` com documentação densa para reduzir custo de contexto.
- 46: - Arquivos: `README.md`, `00-resumo-projeto.md`, `01-arquitetura-e-modulos.md`,
- 47:   `02-decisoes-e-armadilhas.md`, `03-historico-de-mudancas.md`,
- 48:   `04-como-contribuir.md` (padrões de código, logs, config, testes e docs).
- 49: - `README.md` limpo: removido o bloco "env temp:" (dump cru do `.env`) e
- 50:   adicionadas as seções 12 (memória para IA) e 13 (observação sobre configuração).
+ 43: - Nova tabela `templates_whatsapp` (`id`, `mensagem`, `descricao`, `ativo`),
+ 44:   criada e seedada no `LeadDatabase.__init__` (idempotente, `id=1` =
+ 45:   "Apresentação Agendamento Já").
+ 46: - `listar_templates_ativos()` retorna só os ativos para o menu de envio.
+ 47: - `_limpar_markdown_whatsapp` remove `**negrito**` e converte `[rótulo](url)` em
+ 48:   texto plano antes do envio (o template usa markdown; o WhatsApp não renderiza).
+ 49: 
+ 50: ### Menu de envio: template + filtros + teste
  51: 
- 52: ### Correção: cache de bairros ignorado (`bairros_fonte`)
- 53: 
- 54: - **Sintoma:** com `LOCALIDADES_USAR_CACHE=true` e base populada, a coleta ainda
- 55:   consultava IBGE e Overpass.
- 56: - **Causa:** `localidades_db.ler_municipios()` não retornava `bairros_fonte`;
- 57:   `_resolver_municipio` repassava `None`, então o cache nunca era considerado.
- 58: - **Correção:** query passou a trazer `uf` e `bairros_fonte`; o resolver repassa
- 59:   o valor real.
- 60: - **Teste:** com as funções de rede trocadas por `AssertionError`, os bairros de
- 61:   Canoas (fonte `overpass`) e Bento Gonçalves (fonte `ibge`) vieram do banco.
- 62: 
- 63: ### Nome oficial do município (IBGE) na coleta
- 64: 
- 65: - `obter_municipio(cidade, uf)` confirma o município e devolve `id_municipio`,
- 66:   `nome` oficial e `uf`.
- 67: - `filtrar_cidades(cidades, termo)` compara **sem acento e sem caixa**:
- 68:   `canoas`, `sao leopoldo`, `CHAPECO` funcionam.
- 69: - `main.coletar_leads()` passa a usar o nome oficial no scraping, no banco e no
- 70:   nome do Excel, e imprime `Município (IBGE): Canoas-RS | código 4304606`.
- 71: - Lista de municípios **memoizada** por execução (`_municipios_da_uf`), evitando
- 72:   rebaixar a lista da UF a cada cidade (principalmente com `SALVAR=false`).
- 73: 
- 74: ### Mensagens de bairros mais honestas
- 75: 
- 76: - Antes: `IBGE retornou 0 distrito(s) útil(eis)`.
- 77: - Agora: `IBGE não publica bairros para Canoas-RS: o município tem apenas 1 distrito (a sede).`
- 78: - Motivo: a API de Localidades do IBGE **não tem bairros** (só distritos).
- 79: 
- 80: ### Aquecimento de bairros por UF (menu 4)
- 81: 
- 82: - `locations.aquecer_bairros_uf(uf, cidades=None, max_cidades=0, pausa_segundos=None)`.
- 83: - `localidades_db.ler_municipios_pendentes(uf)` → só `bairros_fonte IS NULL`.
- 84: - Retoma de onde parou; `Ctrl+C` preserva o que já foi gravado.
- 85: - Pausa (`AQUECER_PAUSA_SEGUNDOS`, default 2) só quando a cidade usou o OSM.
- 86: - Falha de rede não grava nada (`falhas` no resumo) e a cidade continua pendente.
- 87: - Bloqueado quando `LOCALIDADES_SALVAR=false`.
- 88: - Medido: AC 21 → 18 → 17 pendentes; SP 621 → 616.
- 89: 
- 90: ### Flag `LOCALIDADES_SALVAR`
- 91: 
- 92: - `false` = somente leitura: nenhuma escrita, **nem criação de tabelas**
- 93:   (`localidades_db.CRIAR_TABELAS = False`) e menus 3/4 desativados.
- 94: - Todas as escritas passam por `_salvar()`, que respeita a flag.
- 95: - Aviso único por execução para não poluir o log.
+ 52: - `enviar_whatsapp_menu()` agora: escolhe template → aplica filtros → pergunta se
+ 53:   quer **teste de envio** → confirma e dispara.
+ 54: - Filtros de envio (menu "FILTROS DE ENVIO"): 0 todos / 1 por número / 2 por
+ 55:   cidade / 3 por nicho. Número aceita parte e compara só dígitos.
+ 56: - `testar_envio()`: digita um número com DDD ou escolhe um lead pendente.
+ 57: - `disparar_campanha` passou a aceitar `leads` (DataFrame já filtrado) — sem isso
+ 58:   os filtros eram ignorados no disparo (ele reconsultava o banco).
+ 59: 
+ 60: ### Correção crítica: chatId `@lid` vs `@c.us` (WAHA)
+ 61: 
+ 62: - **Sintoma:** `500 Server Error` no `/api/sendText` para o número do mantenedor.
+ 63: - **Causa:** número recente usa `@lid`; enviar `@c.us` retorna HTTP 500.
+ 64: - **Correção:** `_resolver_chatid_waha` consulta `/api/checkNumberStatus` e usa o
+ 65:   chatId retornado; fallback `@c.us` para números antigos.
+ 66: - **Cache:** coluna `leads.chat_id_waha` + `salvar_chat_id_waha` — a resolução é
+ 67:   feita uma única vez por lead (menos chamadas e reenvio mais rápido).
+ 68: - `data_envio_whatsapp` continua gravada só no sucesso; `status_whatsapp` em
+ 69:   `enviado`/`falhou`.
+ 70: 
+ 71: ---
+ 72: 
+ 73: ## 2026-10-29
+ 74: 
+ 75: ### Memória do projeto para IA
+ 76: 
+ 77: - Criada a pasta `memory/` com documentação densa para reduzir custo de contexto.
+ 78: - Arquivos: `README.md`, `00-resumo-projeto.md`, `01-arquitetura-e-modulos.md`,
+ 79:   `02-decisoes-e-armadilhas.md`, `03-historico-de-mudancas.md`,
+ 80:   `04-como-contribuir.md` (padrões de código, logs, config, testes e docs).
+ 81: - `README.md` limpo: removido o bloco "env temp:" (dump cru do `.env`) e
+ 82:   adicionadas as seções 12 (memória para IA) e 13 (observação sobre configuração).
+ 83: 
+ 84: ### Correção: cache de bairros ignorado (`bairros_fonte`)
+ 85: 
+ 86: - **Sintoma:** com `LOCALIDADES_USAR_CACHE=true` e base populada, a coleta ainda
+ 87:   consultava IBGE e Overpass.
+ 88: - **Causa:** `localidades_db.ler_municipios()` não retornava `bairros_fonte`;
+ 89:   `_resolver_municipio` repassava `None`, então o cache nunca era considerado.
+ 90: - **Correção:** query passou a trazer `uf` e `bairros_fonte`; o resolver repassa
+ 91:   o valor real.
+ 92: - **Teste:** com as funções de rede trocadas por `AssertionError`, os bairros de
+ 93:   Canoas (fonte `overpass`) e Bento Gonçalves (fonte `ibge`) vieram do banco.
+ 94: 
+ 95: ### Nome oficial do município (IBGE) na coleta
  96: 
- 97: ### `.env` e `.env.example` comentados
- 98: 
- 99: - Cada variável com explicação, faixa de valores e efeito colateral.
-100: - Tabela das 4 combinações `USAR_CACHE × SALVAR`.
-101: - Regra explícita: comentário só em linha própria.
-102: - Valores locais preservados (`USAR_CACHE=false` → depois `true`).
-103: 
-104: ### Base de localidades offline (IBGE) — menu 3
+ 97: - `obter_municipio(cidade, uf)` confirma o município e devolve `id_municipio`,
+ 98:   `nome` oficial e `uf`.
+ 99: - `filtrar_cidades(cidades, termo)` compara **sem acento e sem caixa**:
+100:   `canoas`, `sao leopoldo`, `CHAPECO` funcionam.
+101: - `main.coletar_leads()` passa a usar o nome oficial no scraping, no banco e no
+102:   nome do Excel, e imprime `Município (IBGE): Canoas-RS | código 4304606`.
+103: - Lista de municípios **memoizada** por execução (`_municipios_da_uf`), evitando
+104:   rebaixar a lista da UF a cada cidade (principalmente com `SALVAR=false`).
 105: 
-106: - Novo `src/localidades_db.py` com tabelas `localidades_estados`,
-107:   `localidades_municipios`, `localidades_bairros` no mesmo `leads.duckdb`.
-108: - `src/config.py` centraliza o loader do `.env` (antes duplicado no `whatsapp.py`).
-109: - `src/locations.py` reescrito: cache → API → grava.
-110: - Sync nacional: 27 estados, 5.571 municípios, 10.751 distritos; 643 cidades com
-111:   bairros prontos pelo IBGE.
-112: - Fallback OSM por cidade, gravado uma única vez.
+106: ### Mensagens de bairros mais honestas
+107: 
+108: - Antes: `IBGE retornou 0 distrito(s) útil(eis)`.
+109: - Agora: `IBGE não publica bairros para Canoas-RS: o município tem apenas 1 distrito (a sede).`
+110: - Motivo: a API de Localidades do IBGE **não tem bairros** (só distritos).
+111: 
+112: ### Aquecimento de bairros por UF (menu 4)
 113: 
-114: ### Anti-captcha / bloqueio do Google Maps
-115: 
-116: - Detecção por URL `/sorry/`, seletores de captcha e textos ("tráfego incomum").
-117: - Retry com pausa longa (`CAPTCHA_PAUSA_SEGUNDOS`) e **cooldown global**
-118:   (`CAPTCHA_PAUSA_GLOBAL_SEGUNDOS`) entre todas as threads.
-119: - Bloqueio persistente → aborta a área e **preserva os leads já extraídos**.
-120: - Testado com Playwright real: página normal passa, página de captcha levanta
-121:   `BloqueioDetectado` após `CAPTCHA_MAX_TENTATIVAS`.
-122: 
-123: ### Correção: menu não aparecia
-124: 
-125: - `src/main.py` definia `menu_interativo()` mas **nunca chamava**.
-126: - Adicionado `if __name__ == "__main__": menu_interativo()`.
-127: 
-128: ### Banco DuckDB versionado
-129: 
-130: - `data/leads.duckdb` passou a ser versionado no Git.
-131: - `.gitignore`: removidos `data/` e `*.duckdb` da lista de ignore; adicionados
-132:   `*.duckdb.wal` e `*.duckdb.tmp`.
-133: - `*.xlsx`, `*.csv`, `*.log` continuam ignorados (confirmado com
-134:   `git check-ignore` e `git ls-files`).
-135: - ⚠️ Comitar com o programa aberto sobe o `.duckdb` sem o `.wal` (dados
-136:   desatualizados). Fechar antes.
+114: - `locations.aquecer_bairros_uf(uf, cidades=None, max_cidades=0, pausa_segundos=None)`.
+115: - `localidades_db.ler_municipios_pendentes(uf)` → só `bairros_fonte IS NULL`.
+116: - Retoma de onde parou; `Ctrl+C` preserva o que já foi gravado.
+117: - Pausa (`AQUECER_PAUSA_SEGUNDOS`, default 2) só quando a cidade usou o OSM.
+118: - Falha de rede não grava nada (`falhas` no resumo) e a cidade continua pendente.
+119: - Bloqueado quando `LOCALIDADES_SALVAR=false`.
+120: - Medido: AC 21 → 18 → 17 pendentes; SP 621 → 616.
+121: 
+122: ### Flag `LOCALIDADES_SALVAR`
+123: 
+124: - `false` = somente leitura: nenhuma escrita, **nem criação de tabelas**
+125:   (`localidades_db.CRIAR_TABELAS = False`) e menus 3/4 desativados.
+126: - Todas as escritas passam por `_salvar()`, que respeita a flag.
+127: - Aviso único por execução para não poluir o log.
+128: 
+129: ### `.env` e `.env.example` comentados
+130: 
+131: - Cada variável com explicação, faixa de valores e efeito colateral.
+132: - Tabela das 4 combinações `USAR_CACHE × SALVAR`.
+133: - Regra explícita: comentário só em linha própria.
+134: - Valores locais preservados (`USAR_CACHE=false` → depois `true`).
+135: 
+136: ### Base de localidades offline (IBGE) — menu 3
 137: 
-138: ---
-139: 
-140: ## Pendências / próximos passos
-141: 
-142: | Item | Status |
-143: |---|---|
-144: | Bairros oficiais via CNEFE 2022 | **Não implementar por hora** (decisão do mantenedor) |
-145: | Resolução automática de captcha (2Captcha/CapMonster) | Não implementado; hoje pausa e desiste da área |
-146: | Enriquecimento de e-mail a partir dos sites | Não iniciado |
-147: | Base de bairros offline nacional | Coberto parcialmente pelo IBGE (643 cidades) |
-148: 
-149: ## Problemas conhecidos (ambiente)
-150: 
-151: - **DBeaver aberto trava o DuckDB** → cache cai para as APIs.
-152: - **Overpass/Nominatim instáveis** (502, timeout) → aquecimento por UF precisa de
-153:   paciência e retomadas.
-154: - Interprete global do mantenedor é Python 3.15; **usar `venv\Scripts\python.exe`**.
-`````
+138: - Novo `src/localidades_db.py` com tabelas `localidades_estados`,
+139:   `localidades_municipios`, `localidades_bairros` no mesmo `leads.duckdb`.
+140: - `src/config.py` centraliza o loader do `.env` (antes duplicado no `whatsapp.py`).
+141: - `src/locations.py` reescrito: cache → API → grava.
+142: - Sync nacional: 27 estados, 5.571 municípios, 10.751 distritos; 643 cidades com
+143:   bairros prontos pelo IBGE.
+144: - Fallback OSM por cidade, gravado uma única vez.
+145: 
+146: ### Anti-captcha / bloqueio do Google Maps
+147: 
+148: - Detecção por URL `/sorry/`, seletores de captcha e textos ("tráfego incomum").
+149: - Retry com pausa longa (`CAPTCHA_PAUSA_SEGUNDOS`) e **cooldown global**
+150:   (`CAPTCHA_PAUSA_GLOBAL_SEGUNDOS`) entre todas as threads.
+151: - Bloqueio persistente → aborta a área e **preserva os leads já extraídos**.
+152: - Testado com Playwright real: página normal passa, página de captcha levanta
+153:   `BloqueioDetectado` após `CAPTCHA_MAX_TENTATIVAS`.
+154: 
+155: ### Correção: menu não aparecia
+156: 
+157: - `src/main.py` definia `menu_interativo()` mas **nunca chamava**.
+158: - Adicionado `if __name__ == "__main__": menu_interativo()`.
+159: 
+160: ### Banco DuckDB versionado
+161: 
+162: - `data/leads.duckdb` passou a ser versionado no Git.
+163: - `.gitignore`: removidos `data/` e `*.duckdb` da lista de ignore; adicionados
+164:   `*.duckdb.wal` e `*.duckdb.tmp`.
+165: - `*.xlsx`, `*.csv`, `*.log` continuam ignorados (confirmado com
+166:   `git check-ignore` e `git ls-files`).
+167: - ⚠️ Comitar com o programa aberto sobe o `.duckdb` sem o `.wal` (dados
+168:   desatualizados). Fechar antes.
+169: 
+170: ---
+171: 
+172: ## Pendências / próximos passos
+173: 
+174: | Item | Status |
+175: |---|---|
+176: | Bairros oficiais via CNEFE 2022 | **Não implementar por hora** (decisão do mantenedor) |
+177: | Resolução automática de captcha (2Captcha/CapMonster) | Não implementado; hoje pausa e desiste da área |
+178: | Enriquecimento de e-mail a partir dos sites | Não iniciado |
+179: | Base de bairros offline nacional | Coberto parcialmente pelo IBGE (643 cidades) |
+180: 
+181: ## Problemas conhecidos (ambiente)
+182: 
+183: - **DBeaver aberto trava o DuckDB** → cache cai para as APIs.
+184: - **Overpass/Nominatim instáveis** (502, timeout) → aquecimento por UF precisa de
+185:   paciência e retomadas.
+186: - Interprete global do mantenedor é Python 3.15; **usar `venv\Scripts\python.exe`**.
+````
+
+## File: memory/README.md
+````markdown
+ 1: # memory/ — Memória do Projeto para IAs
+ 2: 
+ 3: Esta pasta contém documentação **resumida e densa** sobre o projeto Map Scraper,
+ 4: escrita para ser lida por modelos de IA antes de alterar código.
+ 5: 
+ 6: ## Por que existe
+ 7: 
+ 8: Ler esses arquivos curtos daqui custa muito menos tokens do que reler todo o código.
+ 9: Use esta pasta como **primeira fonte de contexto**.
+10: 
+11: ## Ordem de leitura recomendada
+12: 
+13: | # | Arquivo | Conteúdo |
+14: |---|---|---|
+15: | 1 | [00-resumo-projeto.md](./00-resumo-projeto.md) | O que o projeto faz, stack, estrutura |
+16: | 2 | [01-arquitetura-e-modulos.md](./01-arquitetura-e-modulos.md) | Cada módulo, funções principais, fluxos |
+17: | 3 | [02-decisoes-e-armadilhas.md](./02-decisoes-e-armadilhas.md) | Decisões técnicas, bugs conhecidos, cuidados |
+18: | 4 | [03-historico-de-mudancas.md](./03-historico-de-mudancas.md) | O que mudou recentemente e por quê |
+19: | 5 | [04-como-contribuir.md](./04-como-contribuir.md) | Padrões de código, logs, config, testes e documentação |
+20: | 6 | [05-plano-coleta-nacional-docker.md](./05-plano-coleta-nacional-docker.md) | **Plano aprovado (não implementado):** banco plugável, fila de jobs, circuit breaker WAHA, Docker |
+21: 
+22: ## Regras de manutenção
+23: 
+24: - **Atualize ao mudar comportamento**, não a cada commit.
+25: - Mantenha cada arquivo curto (ideal: < 200 linhas). Detalhe fica no código.
+26: - Registre o **porquê** das decisões, não só o quê.
+27: - Nunca coloque segredos aqui (API keys, tokens). Use `.env`.
+28: - Datas no formato `AAAA-MM-DD`.
+29: 
+30: ## Arquivos que NÃO devem ser duplicados aqui
+31: 
+32: - `README.md` (raiz) — manual do usuário, instalação, uso.
+33: - `.env.example` — valores e comentários de cada variável.
+34: 
+35: ## Git force
+36: - Enviar
+37: git add -A; git commit -m "Atualização"; git push --force origin main
+38: 
+39: 
+40: ## git forçado
+41: 
+42: # Envia
+43: git add -A; git commit -m "Melhorias no processo de coletas v3 $(Get-Date -Format 'yyyy-MM-dd HH:mm')"; git push --force-with-lease origin main
+44: 
+45: # Recebe
+46: 
+47: git fetch --all; git reset --hard origin/main
+````
 
 ## File: src/scraper.py
-`````python
+````python
   1: # src/scraper.py
   2: from playwright.sync_api import sync_playwright
   3: import time
@@ -1828,323 +2174,221 @@ requirements.txt
 338:                 print(f"Erro na busca {termo}: {e}")
 339: 
 340:     return pd.DataFrame(todos_leads)
-`````
+````
 
 ## File: src/database.py
-`````python
+````python
   1: # src/database.py
-  2: import duckdb
-  3: import pandas as pd
-  4: import os
-  5: import re
-  6: import json
-  7: from datetime import datetime
-  8: 
-  9: # Template padrão de WhatsApp, usado para popular a tabela de templates.
- 10: # Segmento indica o nicho para o qual a mensagem foi criada (ex.: barbearias).
- 11: TEMPLATE_AGRUPAMENTO_PADRAO = """Opa, tudo certo?
+  2: """Camada de acesso a dados (leads, templates e log de envio).
+  3: 
+  4: Usa `src/backend.py`, que abstrai PostgreSQL e DuckDB — o código daqui não
+  5: depende do banco específico. A criação do schema e o seed dos templates ficam
+  6: em `src/schema.py` (executado uma vez no setup: `python src/schema.py`).
+  7: """
+  8: import os
+  9: import re
+ 10: import json
+ 11: from datetime import datetime
  12: 
- 13: Conhece o Agendamento Já? É uma plataforma 100% online para deixar sua agenda no piloto automático e acabar com a dor de cabeça de gerenciar horários pelo WhatsApp.
+ 13: import pandas as pd
  14: 
- 15: Com planos a partir de R$ 60,00 no nosso aplicativo você consegue:
+ 15: from src import backend
  16: 
- 17: • Personalizar com a identidade da sua marca
- 18: • Lembretes automatizados via Whatsapp
- 19: • Divulgação de horários automatizadas
- 20: • Controle de faturamento
- 21: • Pagamentos antecipados
- 22: 
- 23: Conheça nossa proposta: https://agendamentoja.com/
- 24: Acompanhe nosso dia a dia: https://www.instagram.com/agendamentoja_
- 25: 
- 26: Quer ver uma demonstração rápida de como funciona na prática para o seu tipo de serviço? É só me avisar!"""
- 27: 
- 28: # Segmento (nicho) padrão do template acima.
- 29: TEMPLATE_SEGMENTO_PADRAO = "barbearias"
- 30: 
- 31: class LeadDatabase:
- 32:     def __init__(self, db_path="data/leads.duckdb"):
- 33:         os.makedirs(os.path.dirname(db_path), exist_ok=True)
- 34:         self.db_path = db_path
- 35:         self.conn = duckdb.connect(self.db_path)
- 36:         self._create_sequences()
- 37:         self._create_table()
- 38:         self._ensure_whatsapp_columns()
- 39:         self._ensure_lead_id()
- 40:         self._create_templates_table()
- 41:         self._seed_templates()
- 42:         self._create_envios_log_table()
- 43: 
- 44:     def _create_sequences(self):
- 45:         """Sequências de ids numéricos (leads e log de envios)."""
- 46:         self.conn.execute("CREATE SEQUENCE IF NOT EXISTS seq_leads_id")
- 47:         self.conn.execute("CREATE SEQUENCE IF NOT EXISTS seq_whatsapp_envios_log_id")
- 48: 
- 49:     def _create_table(self):
- 50:         self.conn.execute("""
- 51:             CREATE TABLE IF NOT EXISTS leads (
- 52:                 lead_id INTEGER DEFAULT nextval('seq_leads_id'),
- 53:                 nome VARCHAR,
- 54:                 telefone VARCHAR,
- 55:                 tipo_telefone VARCHAR,
- 56:                 whatsapp_link VARCHAR,
- 57:                 instagram VARCHAR,
- 58:                 site VARCHAR,
- 59:                 bairro VARCHAR,
- 60:                 cidade VARCHAR,
- 61:                 estado VARCHAR,
- 62:                 nicho VARCHAR,
- 63:                 status VARCHAR DEFAULT 'ativo',
- 64:                 data_extracao TIMESTAMP,
- 65:                 data_envio_whatsapp TIMESTAMP,
- 66:                 status_whatsapp VARCHAR DEFAULT 'pendente',
- 67:                 chat_id_waha VARCHAR,
- 68:                 PRIMARY KEY (nome, cidade)
- 69:             )
- 70:         """)
- 71: 
- 72:     def _ensure_whatsapp_columns(self):
- 73:         """Adiciona as colunas de log de WhatsApp em bancos criados antes da migração."""
- 74:         colunas = {row[1] for row in self.conn.execute("PRAGMA table_info(leads)").fetchall()}
- 75:         if 'data_envio_whatsapp' not in colunas:
- 76:             self.conn.execute("ALTER TABLE leads ADD COLUMN data_envio_whatsapp TIMESTAMP")
- 77:         if 'status_whatsapp' not in colunas:
- 78:             self.conn.execute("ALTER TABLE leads ADD COLUMN status_whatsapp VARCHAR DEFAULT 'pendente'")
- 79:         if 'chat_id_waha' not in colunas:
- 80:             self.conn.execute("ALTER TABLE leads ADD COLUMN chat_id_waha VARCHAR")
- 81: 
- 82:     def _ensure_lead_id(self):
- 83:         """Adiciona o id numérico em bancos antigos (backfill automático via DEFAULT)."""
- 84:         colunas = {row[1] for row in self.conn.execute("PRAGMA table_info(leads)").fetchall()}
- 85:         if 'lead_id' not in colunas:
- 86:             self.conn.execute(
- 87:                 "ALTER TABLE leads ADD COLUMN lead_id INTEGER DEFAULT nextval('seq_leads_id')"
- 88:             )
- 89: 
- 90:     def _create_templates_table(self):
- 91:         """Tabela de templates de mensagem de WhatsApp (mensagem, descrição, segmento e ativo)."""
- 92:         self.conn.execute("""
- 93:             CREATE TABLE IF NOT EXISTS templates_whatsapp (
- 94:                 id INTEGER PRIMARY KEY,
- 95:                 mensagem VARCHAR,
- 96:                 descricao VARCHAR,
- 97:                 segmento VARCHAR,
- 98:                 ativo BOOLEAN DEFAULT TRUE
- 99:             )
-100:         """)
-101:         colunas = {row[1] for row in self.conn.execute("PRAGMA table_info(templates_whatsapp)").fetchall()}
-102:         if 'segmento' not in colunas:
-103:             self.conn.execute("ALTER TABLE templates_whatsapp ADD COLUMN segmento VARCHAR")
-104: 
-105:     def _seed_templates(self):
-106:         """Garante o template padrão do Agendamento Já (id=1), atualizando se já existir."""
-107:         self.conn.execute("""
-108:             INSERT INTO templates_whatsapp (id, mensagem, descricao, segmento, ativo)
-109:             VALUES (1, ?, 'Apresentação Agendamento Já', ?, TRUE)
-110:             ON CONFLICT (id) DO UPDATE SET
-111:                 mensagem = excluded.mensagem,
-112:                 descricao = excluded.descricao,
-113:                 segmento = excluded.segmento,
-114:                 ativo = excluded.ativo
-115:         """, [TEMPLATE_AGRUPAMENTO_PADRAO, TEMPLATE_SEGMENTO_PADRAO])
-116: 
-117:     def listar_templates_ativos(self):
-118:         """Retorna os templates ativos como lista de dicionários (id, mensagem, descricao, segmento, ativo)."""
-119:         return (
-120:             self.conn.execute("""
-121:                 SELECT id, mensagem, descricao, segmento, ativo
-122:                 FROM templates_whatsapp
-123:                 WHERE ativo = TRUE
-124:                 ORDER BY id
-125:             """)
-126:             .df()
-127:             .to_dict("records")
-128:         )
-129: 
-130:     def _create_envios_log_table(self):
-131:         """Tabela de log dos envios de WhatsApp (rastreamento de cada disparo).
-132: 
-133:         - `lead_id`: FK lógica para `leads.lead_id` (DuckDB não aplica FK).
-134:         - `telefone`: somente dígitos, igual a `leads.telefone` → chave de JOIN.
-135:         - `telefone_normalizado`: formato canônico 55DDDNUMERO (quando 11 dígitos).
-136:         - `payload`: retorno bruto da WAHA (JSON), útil para auditoria.
-137:         """
-138:         self.conn.execute("""
-139:             CREATE TABLE IF NOT EXISTS whatsapp_envios_log (
-140:                 id INTEGER PRIMARY KEY DEFAULT nextval('seq_whatsapp_envios_log_id'),
-141:                 lead_id INTEGER,
-142:                 nome VARCHAR,
-143:                 cidade VARCHAR,
-144:                 telefone VARCHAR,
-145:                 telefone_normalizado VARCHAR,
-146:                 chat_id VARCHAR,
-147:                 status VARCHAR,
-148:                 mensagem VARCHAR,
-149:                 payload VARCHAR,
-150:                 erro VARCHAR,
-151:                 data_envio TIMESTAMP
-152:             )
-153:         """)
-154: 
-155:     def salvar_log_envio(self, lead_id, nome, cidade, telefone, chat_id, status,
-156:                          mensagem=None, payload=None, erro=None):
-157:         """Grava uma linha de log de envio com os campos normalizados.
-158: 
-159:         - `lead_id`: referencia `leads.lead_id` (vínculo por PK).
-160:         - `telefone` é reduzido a dígitos (mesma representação de `leads.telefone`),
-161:           permitindo JOIN direto: leads.telefone = whatsapp_envios_log.telefone.
-162:         """
-163:         telefone = re.sub(r"\D", "", str(telefone or ""))
-164:         telefone_normalizado = None
-165:         if telefone.startswith("55") and len(telefone) > 11:
-166:             base = telefone[2:]
-167:         else:
-168:             base = telefone
-169:         if len(base) == 11:
-170:             telefone_normalizado = f"55{base}"
-171:         elif telefone:
-172:             telefone_normalizado = telefone
-173: 
-174:         payload_str = None
-175:         if payload is not None:
-176:             if isinstance(payload, (dict, list)):
-177:                 try:
-178:                     payload_str = json.dumps(payload, ensure_ascii=False, default=str)
-179:                 except Exception:
-180:                     payload_str = str(payload)
-181:             else:
-182:                 payload_str = str(payload)
-183: 
-184:         self.conn.execute("""
-185:             INSERT INTO whatsapp_envios_log
-186:                 (lead_id, nome, cidade, telefone, telefone_normalizado, chat_id,
-187:                  status, mensagem, payload, erro, data_envio)
-188:             VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
-189:         """, [lead_id, nome, cidade, telefone or None, telefone_normalizado, chat_id,
-190:               status, mensagem, payload_str, erro, datetime.now()])
-191: 
-192:     def save_leads(self, df: pd.DataFrame):
-193:         if df.empty:
-194:             return 0
-195:         
-196:         descartados_db = self.conn.execute("SELECT nome, cidade FROM leads WHERE status = 'descartado'").fetchall()
-197:         descartados_set = set(descartados_db)
-198:         
-199:         df = df[~df.apply(lambda row: (row['nome'], row['cidade']) in descartados_set, axis=1)]
-200:         
-201:         if df.empty:
-202:             print("Todos os leads coletados já foram descartados anteriormente. Pulando salvamento.")
-203:             return 0
-204:             
-205:         df['data_extracao'] = datetime.now()
-206:         
-207:         if 'status' not in df.columns:
-208:             df['status'] = 'ativo'
-209: 
-210:         self.conn.register('df_temp', df)
-211: 
-212:         # UPSERT preservando o status atual e as colunas de log do WhatsApp.
-213:         # Assim, re-raspar um lead já enviado NÃO apaga data_envio_whatsapp/status_whatsapp.
-214:         self.conn.execute("""
-215:             INSERT INTO leads (nome, telefone, tipo_telefone, whatsapp_link, instagram, site, bairro, cidade, estado, nicho, status, data_extracao)
-216:             SELECT nome, telefone, tipo_telefone, whatsapp_link, instagram, site, bairro, cidade, estado, nicho, status, data_extracao
-217:             FROM df_temp
-218:             ON CONFLICT (nome, cidade) DO UPDATE SET
-219:                 telefone = excluded.telefone,
-220:                 tipo_telefone = excluded.tipo_telefone,
-221:                 whatsapp_link = excluded.whatsapp_link,
-222:                 instagram = excluded.instagram,
-223:                 site = excluded.site,
-224:                 bairro = excluded.bairro,
-225:                 estado = excluded.estado,
-226:                 nicho = excluded.nicho,
-227:                 data_extracao = excluded.data_extracao
-228:         """)
-229: 
-230:         self.conn.unregister('df_temp')
-231:         return len(df)
-232: 
-233:     def get_leads_para_envio(self, limite=None, numero=None, cidade=None, nicho=None):
-234:         """Retorna leads ativos, celulares e ainda não enviados (evita spam/fixo).
-235: 
-236:         Filtros opcionais:
-237:         - numero: filtra por telefone (completo ou parte; ignora não-dígitos)
-238:         - cidade: filtra por nome exato da cidade
-239:         - nicho:  filtra por nicho exato
-240:         """
-241:         query = """
-242:             SELECT lead_id, nome, telefone, whatsapp_link, bairro, cidade, estado, nicho, chat_id_waha
-243:             FROM leads
-244:             WHERE status = 'ativo'
-245:               AND tipo_telefone = 'Celular'
-246:               AND (status_whatsapp IS NULL OR status_whatsapp = 'pendente')
-247:         """
-248:         params = []
-249:         if numero:
-250:             numero = re.sub(r"\D", "", str(numero))
-251:             query += " AND regexp_replace(telefone, '[^0-9]', '', 'g') LIKE ?"
-252:             params.append(f"%{numero}%")
-253:         if cidade:
-254:             query += " AND cidade = ?"
-255:             params.append(cidade)
-256:         if nicho:
-257:             query += " AND nicho = ?"
-258:             params.append(nicho)
-259:         query += " ORDER BY cidade, bairro, nome"
-260:         if limite:
-261:             query += " LIMIT ?"
-262:             params.append(int(limite))
-263:         return self.conn.execute(query, params).df()
-264: 
-265:     def salvar_chat_id_waha(self, nome, cidade, chat_id):
-266:         """Cacheia o chatId resolvido (ex.: 143172869029943@lid) para não repetir
-267:         a chamada ao /api/checkNumberStatus em envios futuros."""
-268:         self.conn.execute("""
-269:             UPDATE leads
-270:             SET chat_id_waha = ?
-271:             WHERE nome = ? AND cidade = ?
-272:         """, [chat_id, nome, cidade])
-273: 
-274:     def marcar_envio(self, nome, cidade, status_whatsapp):
-275:         """Registra o resultado do envio. 'data_envio_whatsapp' é gravado apenas no sucesso."""
-276:         if status_whatsapp == 'enviado':
-277:             self.conn.execute("""
-278:                 UPDATE leads
-279:                 SET status_whatsapp = ?, data_envio_whatsapp = ?
-280:                 WHERE nome = ? AND cidade = ?
-281:             """, [status_whatsapp, datetime.now(), nome, cidade])
-282:         else:
-283:             self.conn.execute("""
-284:                 UPDATE leads
-285:                 SET status_whatsapp = ?
-286:                 WHERE nome = ? AND cidade = ?
-287:             """, [status_whatsapp, nome, cidade])
-288: 
-289:     def export_to_excel(self, nicho: str, cidade: str):
-290:         df = self.conn.execute("""
-291:             SELECT nome, telefone, tipo_telefone, whatsapp_link, instagram, site, bairro, data_extracao 
-292:             FROM leads 
-293:             WHERE nicho = ? AND cidade = ? AND status = 'ativo'
-294:             ORDER BY bairro, nome
-295:         """, [nicho, cidade]).df()
-296:         
-297:         if df.empty:
-298:             print("Nenhum dado ativo para exportar.")
-299:             return
-300:             
-301:         os.makedirs("output", exist_ok=True)
-302:         nome_arquivo = f"output/leads_{nicho}_{cidade}.xlsx".replace(" ", "_").lower()
-303:         df.to_excel(nome_arquivo, index=False)
-304:         print(f"🎉 Exportação concluída: {nome_arquivo} ({len(df)} leads ativos)")
-305: 
-306:     def close(self):
-307:         self.conn.close()
-`````
+ 17: 
+ 18: class LeadDatabase:
+ 19:     def __init__(self, conn=None):
+ 20:         self.conn = conn if conn is not None else backend.conectar()
+ 21: 
+ 22:     def listar_templates_ativos(self):
+ 23:         """Retorna os templates ativos como lista de dicionários (id, mensagem, descricao, segmento, ativo)."""
+ 24:         return (
+ 25:             backend.query_df(self.conn, """
+ 26:                 SELECT id, mensagem, descricao, segmento, ativo
+ 27:                 FROM templates_whatsapp
+ 28:                 WHERE ativo = TRUE
+ 29:                 ORDER BY id
+ 30:             """)
+ 31:             .to_dict("records")
+ 32:         )
+ 33: 
+ 34:     def salvar_log_envio(self, lead_id, nome, cidade, telefone, chat_id, status,
+ 35:                          mensagem=None, payload=None, erro=None):
+ 36:         """Grava uma linha de log de envio com os campos normalizados.
+ 37: 
+ 38:         - `lead_id`: referencia `leads.lead_id` (vínculo por PK).
+ 39:         - `telefone` é reduzido a dígitos (mesma representação de `leads.telefone`),
+ 40:           permitindo JOIN direto: leads.telefone = whatsapp_envios_log.telefone.
+ 41:         """
+ 42:         telefone = re.sub(r"\D", "", str(telefone or ""))
+ 43:         telefone_normalizado = None
+ 44:         if telefone.startswith("55") and len(telefone) > 11:
+ 45:             base = telefone[2:]
+ 46:         else:
+ 47:             base = telefone
+ 48:         if len(base) == 11:
+ 49:             telefone_normalizado = f"55{base}"
+ 50:         elif telefone:
+ 51:             telefone_normalizado = telefone
+ 52: 
+ 53:         payload_str = None
+ 54:         if payload is not None:
+ 55:             if isinstance(payload, (dict, list)):
+ 56:                 try:
+ 57:                     payload_str = json.dumps(payload, ensure_ascii=False, default=str)
+ 58:                 except Exception:
+ 59:                     payload_str = str(payload)
+ 60:             else:
+ 61:                 payload_str = str(payload)
+ 62: 
+ 63:         p = backend.ph()
+ 64:         backend.execute(self.conn, f"""
+ 65:             INSERT INTO whatsapp_envios_log
+ 66:                 (lead_id, nome, cidade, telefone, telefone_normalizado, chat_id,
+ 67:                  status, mensagem, payload, erro, data_envio)
+ 68:             VALUES ({p}, {p}, {p}, {p}, {p}, {p}, {p}, {p}, {p}, {p}, {p})
+ 69:         """, [
+ 70:             lead_id, nome, cidade, telefone or None, telefone_normalizado, chat_id,
+ 71:             status, mensagem, payload_str, erro, datetime.now(),
+ 72:         ])
+ 73:         backend.commit(self.conn)
+ 74: 
+ 75:     def save_leads(self, df: pd.DataFrame):
+ 76:         if df.empty:
+ 77:             return 0
+ 78: 
+ 79:         descartados = set(backend.query_all(
+ 80:             self.conn, "SELECT nome, cidade FROM leads WHERE status = 'descartado'"
+ 81:         ))
+ 82:         df = df[~df.apply(lambda row: (row['nome'], row['cidade']) in descartados, axis=1)]
+ 83: 
+ 84:         if df.empty:
+ 85:             print("Todos os leads coletados já foram descartados anteriormente. Pulando salvamento.")
+ 86:             return 0
+ 87: 
+ 88:         df = df.copy()
+ 89:         df['data_extracao'] = datetime.now()
+ 90:         if 'status' not in df.columns:
+ 91:             df['status'] = 'ativo'
+ 92: 
+ 93:         colunas = [
+ 94:             'nome', 'telefone', 'tipo_telefone', 'whatsapp_link', 'instagram',
+ 95:             'site', 'bairro', 'cidade', 'estado', 'nicho', 'status', 'data_extracao',
+ 96:         ]
+ 97:         linhas = [
+ 98:             tuple(backend._valor(r.get(c)) for c in colunas)
+ 99:             for r in df.to_dict("records")
+100:         ]
+101: 
+102:         # UPSERT preservando o status atual e as colunas de log do WhatsApp.
+103:         # Assim, re-raspar um lead já enviado NÃO apaga data_envio_whatsapp/status_whatsapp.
+104:         backend.bulk_upsert(
+105:             self.conn,
+106:             table="leads",
+107:             columns=colunas,
+108:             rows=linhas,
+109:             conflict="nome, cidade",
+110:             set_clause=(
+111:                 "telefone = excluded.telefone, "
+112:                 "tipo_telefone = excluded.tipo_telefone, "
+113:                 "whatsapp_link = excluded.whatsapp_link, "
+114:                 "instagram = excluded.instagram, "
+115:                 "site = excluded.site, "
+116:                 "bairro = excluded.bairro, "
+117:                 "estado = excluded.estado, "
+118:                 "nicho = excluded.nicho, "
+119:                 "data_extracao = excluded.data_extracao"
+120:             ),
+121:         )
+122:         backend.commit(self.conn)
+123:         return len(df)
+124: 
+125:     def get_leads_para_envio(self, limite=None, numero=None, cidade=None, nicho=None):
+126:         """Retorna leads ativos, celulares e ainda não enviados (evita spam/fixo).
+127: 
+128:         Filtros opcionais:
+129:         - numero: filtra por telefone (completo ou parte; ignora não-dígitos)
+130:         - cidade: filtra por nome exato da cidade
+131:         - nicho:  filtra por nicho exato
+132:         """
+133:         p = backend.ph()
+134:         query = f"""
+135:             SELECT lead_id, nome, telefone, whatsapp_link, bairro, cidade, estado, nicho, chat_id_waha
+136:             FROM leads
+137:             WHERE status = 'ativo'
+138:               AND tipo_telefone = 'Celular'
+139:               AND (status_whatsapp IS NULL OR status_whatsapp = 'pendente')
+140:         """
+141:         params = []
+142:         if numero:
+143:             numero = re.sub(r"\D", "", str(numero))
+144:             query += f" AND regexp_replace(telefone, '[^0-9]', '', 'g') LIKE {p}"
+145:             params.append(f"%{numero}%")
+146:         if cidade:
+147:             query += f" AND cidade = {p}"
+148:             params.append(cidade)
+149:         if nicho:
+150:             query += f" AND nicho = {p}"
+151:             params.append(nicho)
+152:         query += " ORDER BY cidade, bairro, nome"
+153:         if limite:
+154:             query += f" LIMIT {p}"
+155:             params.append(int(limite))
+156:         return backend.query_df(self.conn, query, params)
+157: 
+158:     def salvar_chat_id_waha(self, nome, cidade, chat_id):
+159:         """Cacheia o chatId resolvido (ex.: 143172869029943@lid) para não repetir
+160:         a chamada ao /api/checkNumberStatus em envios futuros."""
+161:         p = backend.ph()
+162:         backend.execute(self.conn, f"""
+163:             UPDATE leads
+164:             SET chat_id_waha = {p}
+165:             WHERE nome = {p} AND cidade = {p}
+166:         """, [chat_id, nome, cidade])
+167:         backend.commit(self.conn)
+168: 
+169:     def marcar_envio(self, nome, cidade, status_whatsapp):
+170:         """Registra o resultado do envio. 'data_envio_whatsapp' é gravado apenas no sucesso."""
+171:         p = backend.ph()
+172:         if status_whatsapp == 'enviado':
+173:             backend.execute(self.conn, f"""
+174:                 UPDATE leads
+175:                 SET status_whatsapp = {p}, data_envio_whatsapp = {p}
+176:                 WHERE nome = {p} AND cidade = {p}
+177:             """, [status_whatsapp, datetime.now(), nome, cidade])
+178:         else:
+179:             backend.execute(self.conn, f"""
+180:                 UPDATE leads
+181:                 SET status_whatsapp = {p}
+182:                 WHERE nome = {p} AND cidade = {p}
+183:             """, [status_whatsapp, nome, cidade])
+184:         backend.commit(self.conn)
+185: 
+186:     def export_to_excel(self, nicho: str, cidade: str):
+187:         p = backend.ph()
+188:         df = backend.query_df(self.conn, f"""
+189:             SELECT nome, telefone, tipo_telefone, whatsapp_link, instagram, site, bairro, data_extracao
+190:             FROM leads
+191:             WHERE nicho = {p} AND cidade = {p} AND status = 'ativo'
+192:             ORDER BY bairro, nome
+193:         """, [nicho, cidade])
+194: 
+195:         if df.empty:
+196:             print("Nenhum dado ativo para exportar.")
+197:             return
+198: 
+199:         os.makedirs("output", exist_ok=True)
+200:         nome_arquivo = f"output/leads_{nicho}_{cidade}.xlsx".replace(" ", "_").lower()
+201:         df.to_excel(nome_arquivo, index=False)
+202:         print(f"🎉 Exportação concluída: {nome_arquivo} ({len(df)} leads ativos)")
+203: 
+204:     def close(self):
+205:         backend.close(self.conn)
+````
 
 ## File: src/locations.py
-`````python
+````python
   1: # src/locations.py
-  2: """Localidades (UF, cidade e bairros) com cache local em DuckDB.
+  2: """Localidades (UF, cidade e bairros) com cache em PostgreSQL.
   3: 
   4: Fonte oficial: API de Localidades do IBGE.
   5:     estados    -> /api/v1/localidades/estados
@@ -2184,574 +2428,571 @@ requirements.txt
  39: # Se true: consulta o banco antes da API. Se false: sempre busca na API.
  40: USAR_CACHE = str_para_bool(os.environ.get("LOCALIDADES_USAR_CACHE"), padrao=True)
  41: 
- 42: # Se false: NUNCA grava na base local (nem cria tabelas). Funciona como
- 43: # "somente leitura": o banco é consultado, mas nada é alterado.
+ 42: # Se false: NUNCA grava na base local. Funciona como "somente leitura":
+ 43: # o banco é consultado, mas nada é alterado.
  44: SALVAR = str_para_bool(os.environ.get("LOCALIDADES_SALVAR"), padrao=True)
  45: 
- 46: # Reflete a flag no módulo de acesso ao banco (controla a criação das tabelas).
- 47: localidades_db.CRIAR_TABELAS = SALVAR
- 48: 
- 49: # Quantidade mínima de distritos úteis para não precisar do OpenStreetMap.
- 50: # Abaixo disso, a cidade é complementada com bairros do OSM.
- 51: MIN_BAIRROS = max(1, env_int("LOCALIDADES_MIN_BAIRROS", 3))
- 52: 
- 53: # Pausa (segundos) entre cidades no aquecimento por UF, aplicada apenas quando o
- 54: # OpenStreetMap foi consultado (política de uso do Nominatim: 1 req/s).
- 55: AQUECER_PAUSA_PADRAO = max(0, env_int("AQUECER_PAUSA_SEGUNDOS", 2))
+ 46: # Quantidade mínima de distritos úteis para não precisar do OpenStreetMap.
+ 47: # Abaixo disso, a cidade é complementada com bairros do OSM.
+ 48: MIN_BAIRROS = max(1, env_int("LOCALIDADES_MIN_BAIRROS", 3))
+ 49: 
+ 50: # Pausa (segundos) entre cidades no aquecimento por UF, aplicada apenas quando o
+ 51: # OpenStreetMap foi consultado (política de uso do Nominatim: 1 req/s).
+ 52: AQUECER_PAUSA_PADRAO = max(0, env_int("AQUECER_PAUSA_SEGUNDOS", 2))
+ 53: 
+ 54: _avisou_cache_indisponivel = False
+ 55: _avisou_sem_gravacao = False
  56: 
- 57: _avisou_cache_indisponivel = False
- 58: _avisou_sem_gravacao = False
- 59: 
- 60: 
- 61: def _cache(funcao, *args, **kwargs):
- 62:     """Executa uma operação na base local, tolerando banco travado/indisponível."""
- 63:     global _avisou_cache_indisponivel
- 64:     try:
- 65:         return funcao(*args, **kwargs)
- 66:     except localidades_db.CacheIndisponivel as e:
- 67:         if not _avisou_cache_indisponivel:
- 68:             print(f"  Aviso: base local de localidades indisponível ({e}).")
- 69:             print("         Seguindo apenas com as APIs (IBGE/OSM).")
- 70:             _avisou_cache_indisponivel = True
- 71:         return None
- 72: 
- 73: 
- 74: def _salvar(funcao, *args, **kwargs):
- 75:     """Grava na base local, respeitando LOCALIDADES_SALVAR=false."""
- 76:     global _avisou_sem_gravacao
- 77:     if not SALVAR:
- 78:         if not _avisou_sem_gravacao:
- 79:             print("  LOCALIDADES_SALVAR=false: a base local não será alterada.")
- 80:             _avisou_sem_gravacao = True
- 81:         return None
- 82:     return _cache(funcao, *args, **kwargs)
- 83: 
- 84: 
- 85: # ---------------------------------------------------------------------------
- 86: # IBGE
- 87: # ---------------------------------------------------------------------------
- 88: def _get_json(url, params=None, timeout=60, tentativas=3):
- 89:     for tentativa in range(1, tentativas + 1):
- 90:         try:
- 91:             resposta = requests.get(url, params=params, timeout=timeout, headers=HEADERS)
- 92:             resposta.raise_for_status()
- 93:             return resposta.json()
- 94:         except Exception as e:
- 95:             print(f"  IBGE indisponível (tentativa {tentativa}/{tentativas}): {type(e).__name__}")
- 96:             if tentativa < tentativas:
- 97:                 time.sleep(1.5 * tentativa)
- 98:     return None
- 99: 
-100: 
-101: def _baixar_estados():
-102:     dados = _get_json(f"{IBGE_API}/estados", params={"orderBy": "nome"}, timeout=30)
-103:     if not dados:
-104:         return None
-105:     return [{"uf": e["sigla"], "nome": e["nome"]} for e in dados]
-106: 
-107: 
-108: def _uf_do_municipio(municipio):
-109:     try:
-110:         return municipio["microrregiao"]["mesorregiao"]["UF"]["sigla"]
-111:     except (KeyError, TypeError):
-112:         try:
-113:             return municipio["regiao-imediata"]["regiao-intermediaria"]["UF"]["sigla"]
-114:         except (KeyError, TypeError):
-115:             return None
-116: 
-117: 
-118: def _baixar_municipios(uf=None):
-119:     url = f"{IBGE_API}/estados/{uf}/municipios" if uf else f"{IBGE_API}/municipios"
-120:     dados = _get_json(url, params={"orderBy": "nome"})
-121:     if not dados:
-122:         return None
-123: 
-124:     registros = []
-125:     for municipio in dados:
-126:         sigla = uf or _uf_do_municipio(municipio)
-127:         if not sigla:
-128:             continue
-129:         registros.append({
-130:             "id_municipio": municipio["id"],
-131:             "nome": municipio["nome"],
-132:             "uf": sigla,
-133:         })
-134:     return registros
-135: 
-136: 
-137: def _baixar_distritos(id_municipio=None):
-138:     url = (f"{IBGE_API}/municipios/{id_municipio}/distritos"
-139:            if id_municipio else f"{IBGE_API}/distritos")
-140:     dados = _get_json(url)
-141:     if not dados:
-142:         return None
-143: 
-144:     registros = []
-145:     for distrito in dados:
-146:         municipio = distrito.get("municipio") or {}
-147:         registros.append({
-148:             "id_distrito": distrito.get("id"),
-149:             "nome": (distrito.get("nome") or "").strip(),
-150:             "id_municipio": municipio.get("id"),
-151:         })
-152:     return [r for r in registros if r["id_municipio"] and r["nome"]]
+ 57: 
+ 58: def _cache(funcao, *args, **kwargs):
+ 59:     """Executa uma operação na base local, tolerando banco travado/indisponível."""
+ 60:     global _avisou_cache_indisponivel
+ 61:     try:
+ 62:         return funcao(*args, **kwargs)
+ 63:     except localidades_db.CacheIndisponivel as e:
+ 64:         if not _avisou_cache_indisponivel:
+ 65:             print(f"  Aviso: base local de localidades indisponível ({e}).")
+ 66:             print("         Seguindo apenas com as APIs (IBGE/OSM).")
+ 67:             _avisou_cache_indisponivel = True
+ 68:         return None
+ 69: 
+ 70: 
+ 71: def _salvar(funcao, *args, **kwargs):
+ 72:     """Grava na base local, respeitando LOCALIDADES_SALVAR=false."""
+ 73:     global _avisou_sem_gravacao
+ 74:     if not SALVAR:
+ 75:         if not _avisou_sem_gravacao:
+ 76:             print("  LOCALIDADES_SALVAR=false: a base local não será alterada.")
+ 77:             _avisou_sem_gravacao = True
+ 78:         return None
+ 79:     return _cache(funcao, *args, **kwargs)
+ 80: 
+ 81: 
+ 82: # ---------------------------------------------------------------------------
+ 83: # IBGE
+ 84: # ---------------------------------------------------------------------------
+ 85: def _get_json(url, params=None, timeout=60, tentativas=3):
+ 86:     for tentativa in range(1, tentativas + 1):
+ 87:         try:
+ 88:             resposta = requests.get(url, params=params, timeout=timeout, headers=HEADERS)
+ 89:             resposta.raise_for_status()
+ 90:             return resposta.json()
+ 91:         except Exception as e:
+ 92:             print(f"  IBGE indisponível (tentativa {tentativa}/{tentativas}): {type(e).__name__}")
+ 93:             if tentativa < tentativas:
+ 94:                 time.sleep(1.5 * tentativa)
+ 95:     return None
+ 96: 
+ 97: 
+ 98: def _baixar_estados():
+ 99:     dados = _get_json(f"{IBGE_API}/estados", params={"orderBy": "nome"}, timeout=30)
+100:     if not dados:
+101:         return None
+102:     return [{"uf": e["sigla"], "nome": e["nome"]} for e in dados]
+103: 
+104: 
+105: def _uf_do_municipio(municipio):
+106:     try:
+107:         return municipio["microrregiao"]["mesorregiao"]["UF"]["sigla"]
+108:     except (KeyError, TypeError):
+109:         try:
+110:             return municipio["regiao-imediata"]["regiao-intermediaria"]["UF"]["sigla"]
+111:         except (KeyError, TypeError):
+112:             return None
+113: 
+114: 
+115: def _baixar_municipios(uf=None):
+116:     url = f"{IBGE_API}/estados/{uf}/municipios" if uf else f"{IBGE_API}/municipios"
+117:     dados = _get_json(url, params={"orderBy": "nome"})
+118:     if not dados:
+119:         return None
+120: 
+121:     registros = []
+122:     for municipio in dados:
+123:         sigla = uf or _uf_do_municipio(municipio)
+124:         if not sigla:
+125:             continue
+126:         registros.append({
+127:             "id_municipio": municipio["id"],
+128:             "nome": municipio["nome"],
+129:             "uf": sigla,
+130:         })
+131:     return registros
+132: 
+133: 
+134: def _baixar_distritos(id_municipio=None):
+135:     url = (f"{IBGE_API}/municipios/{id_municipio}/distritos"
+136:            if id_municipio else f"{IBGE_API}/distritos")
+137:     dados = _get_json(url)
+138:     if not dados:
+139:         return None
+140: 
+141:     registros = []
+142:     for distrito in dados:
+143:         municipio = distrito.get("municipio") or {}
+144:         registros.append({
+145:             "id_distrito": distrito.get("id"),
+146:             "nome": (distrito.get("nome") or "").strip(),
+147:             "id_municipio": municipio.get("id"),
+148:         })
+149:     return [r for r in registros if r["id_municipio"] and r["nome"]]
+150: 
+151: 
+152: _municipios_memoria = {}
 153: 
 154: 
-155: _municipios_memoria = {}
-156: 
-157: 
-158: def _municipios_da_uf(uf):
-159:     """Lista de municípios da UF, memorizada na execução para não baixar duas vezes."""
-160:     if uf not in _municipios_memoria:
-161:         print(f"  Baixando a lista de municípios de {uf} do IBGE...")
-162:         municipios = _baixar_municipios(uf)
-163:         if municipios is None:
-164:             return None
-165:         _municipios_memoria[uf] = municipios
-166:     return _municipios_memoria[uf]
-167: 
-168: 
-169: # ---------------------------------------------------------------------------
-170: # OpenStreetMap (fallback de bairros)
-171: # ---------------------------------------------------------------------------
-172: def _obter_bbox_cidade(cidade, uf):
-173:     """Retorna (sul, norte, oeste, leste) da cidade via Nominatim."""
-174:     url = "https://nominatim.openstreetmap.org/search"
-175:     params = {"format": "json", "q": f"{cidade}, {uf}, Brazil", "limit": 1}
-176:     try:
-177:         resposta = requests.get(url, params=params, timeout=15, headers=HEADERS)
-178:         resposta.raise_for_status()
-179:         resultados = resposta.json()
-180:         if not resultados:
+155: def _municipios_da_uf(uf):
+156:     """Lista de municípios da UF, memorizada na execução para não baixar duas vezes."""
+157:     if uf not in _municipios_memoria:
+158:         print(f"  Baixando a lista de municípios de {uf} do IBGE...")
+159:         municipios = _baixar_municipios(uf)
+160:         if municipios is None:
+161:             return None
+162:         _municipios_memoria[uf] = municipios
+163:     return _municipios_memoria[uf]
+164: 
+165: 
+166: # ---------------------------------------------------------------------------
+167: # OpenStreetMap (fallback de bairros)
+168: # ---------------------------------------------------------------------------
+169: def _obter_bbox_cidade(cidade, uf):
+170:     """Retorna (sul, norte, oeste, leste) da cidade via Nominatim."""
+171:     url = "https://nominatim.openstreetmap.org/search"
+172:     params = {"format": "json", "q": f"{cidade}, {uf}, Brazil", "limit": 1}
+173:     try:
+174:         resposta = requests.get(url, params=params, timeout=15, headers=HEADERS)
+175:         resposta.raise_for_status()
+176:         resultados = resposta.json()
+177:         if not resultados:
+178:             return None
+179:         bb = resultados[0].get("boundingbox")
+180:         if not bb or len(bb) != 4:
 181:             return None
-182:         bb = resultados[0].get("boundingbox")
-183:         if not bb or len(bb) != 4:
-184:             return None
-185:         sul, norte, oeste, leste = (float(v) for v in bb)
-186:         return (sul, norte, oeste, leste)
-187:     except Exception as e:
-188:         print(f"Erro ao localizar a cidade no Nominatim: {e}")
-189:         return None
-190: 
+182:         sul, norte, oeste, leste = (float(v) for v in bb)
+183:         return (sul, norte, oeste, leste)
+184:     except Exception as e:
+185:         print(f"Erro ao localizar a cidade no Nominatim: {e}")
+186:         return None
+187: 
+188: 
+189: def _consultar_overpass(query):
+190:     """Tenta a consulta em vários espelhos do Overpass, com retry e backoff.
 191: 
-192: def _consultar_overpass(query):
-193:     """Tenta a consulta em vários espelhos do Overpass, com retry e backoff.
-194: 
-195:     Retorna o JSON da resposta, ou None quando nenhum espelho respondeu
-196:     (serviço indisponível) — o que é diferente de responder vazio.
-197:     """
-198:     for endpoint in OVERPASS_ENDPOINTS:
-199:         for tentativa in range(1, 3):
-200:             try:
-201:                 resposta = requests.get(endpoint, params={"data": query}, timeout=45, headers=HEADERS)
-202:                 resposta.raise_for_status()
-203:                 return resposta.json()
-204:             except Exception as e:
-205:                 print(f"  Overpass ({endpoint}) tentativa {tentativa} falhou: {type(e).__name__}")
-206:                 time.sleep(1.5 * tentativa)
-207:     return None
-208: 
-209: 
-210: def _obter_bairros_overpass(sul, norte, oeste, leste):
-211:     """Busca bairros dentro do bbox via Overpass (place=* e admin_level 9/10)."""
-212:     bbox = f"({sul},{oeste},{norte},{leste})"
-213: 
-214:     query_leve = f"""
-215: [out:json][timeout:40];
-216: (
-217:   node["place"~"^(suburb|neighbourhood|quarter)$"]{bbox};
-218:   way["place"~"^(suburb|neighbourhood|quarter)$"]{bbox};
-219: );
-220: out center tags;
-221: """
-222: 
-223:     query_admin = f"""
-224: [out:json][timeout:55];
-225: (
-226:   relation["boundary"="administrative"]["admin_level"="9"]{bbox};
-227:   relation["boundary"="administrative"]["admin_level"="10"]{bbox};
-228: );
-229: out center tags;
-230: """
-231: 
-232:     data = _consultar_overpass(query_leve)
-233:     if data is None:
-234:         return None
-235:     if data.get("elements"):
-236:         return data
-237:     return _consultar_overpass(query_admin)
-238: 
-239: 
-240: def _bairros_via_overpass(cidade, uf):
-241:     """Retorna a lista de bairros do OSM, ou None se o serviço estiver indisponível."""
-242:     bbox = _obter_bbox_cidade(cidade, uf)
-243:     if not bbox:
-244:         return None
-245: 
-246:     data = _obter_bairros_overpass(*bbox)
-247:     if data is None:
-248:         return None
-249: 
-250:     nomes = set()
-251:     for elemento in data.get("elements", []):
-252:         tags = elemento.get("tags") or {}
-253:         nome = tags.get("name")
-254:         if not isinstance(nome, str):
-255:             continue
-256:         nome = nome.strip()
-257:         if nome and nome.lower() != cidade.strip().lower():
-258:             nomes.add(nome)
-259:     return sorted(nomes)
-260: 
-261: 
-262: # ---------------------------------------------------------------------------
-263: # API pública do módulo
-264: # ---------------------------------------------------------------------------
-265: def obter_estados():
-266:     if USAR_CACHE:
-267:         estados = _cache(localidades_db.ler_estados)
-268:         if estados:
-269:             print(f"Base local: {len(estados)} estados.")
-270:             return pd.DataFrame(estados)
-271: 
-272:     estados = _baixar_estados()
-273:     if estados is None:
-274:         estados = _cache(localidades_db.ler_estados)
-275:         if estados:
-276:             print("IBGE indisponível. Usando os estados gravados na base local.")
-277:             return pd.DataFrame(estados)
-278:         print("Erro ao buscar estados.")
-279:         return pd.DataFrame()
+192:     Retorna o JSON da resposta, ou None quando nenhum espelho respondeu
+193:     (serviço indisponível) — o que é diferente de responder vazio.
+194:     """
+195:     for endpoint in OVERPASS_ENDPOINTS:
+196:         for tentativa in range(1, 3):
+197:             try:
+198:                 resposta = requests.get(endpoint, params={"data": query}, timeout=45, headers=HEADERS)
+199:                 resposta.raise_for_status()
+200:                 return resposta.json()
+201:             except Exception as e:
+202:                 print(f"  Overpass ({endpoint}) tentativa {tentativa} falhou: {type(e).__name__}")
+203:                 time.sleep(1.5 * tentativa)
+204:     return None
+205: 
+206: 
+207: def _obter_bairros_overpass(sul, norte, oeste, leste):
+208:     """Busca bairros dentro do bbox via Overpass (place=* e admin_level 9/10)."""
+209:     bbox = f"({sul},{oeste},{norte},{leste})"
+210: 
+211:     query_leve = f"""
+212: [out:json][timeout:40];
+213: (
+214:   node["place"~"^(suburb|neighbourhood|quarter)$"]{bbox};
+215:   way["place"~"^(suburb|neighbourhood|quarter)$"]{bbox};
+216: );
+217: out center tags;
+218: """
+219: 
+220:     query_admin = f"""
+221: [out:json][timeout:55];
+222: (
+223:   relation["boundary"="administrative"]["admin_level"="9"]{bbox};
+224:   relation["boundary"="administrative"]["admin_level"="10"]{bbox};
+225: );
+226: out center tags;
+227: """
+228: 
+229:     data = _consultar_overpass(query_leve)
+230:     if data is None:
+231:         return None
+232:     if data.get("elements"):
+233:         return data
+234:     return _consultar_overpass(query_admin)
+235: 
+236: 
+237: def _bairros_via_overpass(cidade, uf):
+238:     """Retorna a lista de bairros do OSM, ou None se o serviço estiver indisponível."""
+239:     bbox = _obter_bbox_cidade(cidade, uf)
+240:     if not bbox:
+241:         return None
+242: 
+243:     data = _obter_bairros_overpass(*bbox)
+244:     if data is None:
+245:         return None
+246: 
+247:     nomes = set()
+248:     for elemento in data.get("elements", []):
+249:         tags = elemento.get("tags") or {}
+250:         nome = tags.get("name")
+251:         if not isinstance(nome, str):
+252:             continue
+253:         nome = nome.strip()
+254:         if nome and nome.lower() != cidade.strip().lower():
+255:             nomes.add(nome)
+256:     return sorted(nomes)
+257: 
+258: 
+259: # ---------------------------------------------------------------------------
+260: # API pública do módulo
+261: # ---------------------------------------------------------------------------
+262: def obter_estados():
+263:     if USAR_CACHE:
+264:         estados = _cache(localidades_db.ler_estados)
+265:         if estados:
+266:             print(f"Base local: {len(estados)} estados.")
+267:             return pd.DataFrame(estados)
+268: 
+269:     estados = _baixar_estados()
+270:     if estados is None:
+271:         estados = _cache(localidades_db.ler_estados)
+272:         if estados:
+273:             print("IBGE indisponível. Usando os estados gravados na base local.")
+274:             return pd.DataFrame(estados)
+275:         print("Erro ao buscar estados.")
+276:         return pd.DataFrame()
+277: 
+278:     _salvar(localidades_db.salvar_estados, estados)
+279:     return pd.DataFrame(estados)
 280: 
-281:     _salvar(localidades_db.salvar_estados, estados)
-282:     return pd.DataFrame(estados)
-283: 
-284: 
-285: def obter_cidades(uf):
-286:     if USAR_CACHE:
-287:         municipios = _cache(localidades_db.ler_municipios, uf)
-288:         if municipios:
-289:             print(f"Base local: {len(municipios)} cidades em {uf}.")
-290:             return [m["nome"] for m in municipios]
-291: 
-292:     municipios = _municipios_da_uf(uf)
-293:     if municipios is None:
-294:         municipios = _cache(localidades_db.ler_municipios, uf)
-295:         if municipios:
-296:             print(f"IBGE indisponível. Usando as cidades de {uf} gravadas na base local.")
-297:             return [m["nome"] for m in municipios]
-298:         print(f"Erro ao buscar cidades para {uf}.")
-299:         return []
+281: 
+282: def obter_cidades(uf):
+283:     if USAR_CACHE:
+284:         municipios = _cache(localidades_db.ler_municipios, uf)
+285:         if municipios:
+286:             print(f"Base local: {len(municipios)} cidades em {uf}.")
+287:             return [m["nome"] for m in municipios]
+288: 
+289:     municipios = _municipios_da_uf(uf)
+290:     if municipios is None:
+291:         municipios = _cache(localidades_db.ler_municipios, uf)
+292:         if municipios:
+293:             print(f"IBGE indisponível. Usando as cidades de {uf} gravadas na base local.")
+294:             return [m["nome"] for m in municipios]
+295:         print(f"Erro ao buscar cidades para {uf}.")
+296:         return []
+297: 
+298:     _salvar(localidades_db.salvar_municipios, municipios)
+299:     return sorted(m["nome"] for m in municipios)
 300: 
-301:     _salvar(localidades_db.salvar_municipios, municipios)
-302:     return sorted(m["nome"] for m in municipios)
-303: 
-304: 
-305: def _normalizar(texto):
-306:     """Minúsculas e sem acentos, para comparar nomes digitados pelo usuário."""
-307:     texto = unicodedata.normalize("NFKD", str(texto or ""))
-308:     return "".join(c for c in texto if not unicodedata.combining(c)).strip().casefold()
-309: 
-310: 
-311: def filtrar_cidades(cidades, termo):
-312:     """Filtra a lista de cidades por um trecho, ignorando acentos e maiúsculas."""
-313:     alvo = _normalizar(termo)
-314:     if not alvo:
-315:         return []
-316:     return [c for c in cidades if alvo in _normalizar(c)]
-317: 
+301: 
+302: def _normalizar(texto):
+303:     """Minúsculas e sem acentos, para comparar nomes digitados pelo usuário."""
+304:     texto = unicodedata.normalize("NFKD", str(texto or ""))
+305:     return "".join(c for c in texto if not unicodedata.combining(c)).strip().casefold()
+306: 
+307: 
+308: def filtrar_cidades(cidades, termo):
+309:     """Filtra a lista de cidades por um trecho, ignorando acentos e maiúsculas."""
+310:     alvo = _normalizar(termo)
+311:     if not alvo:
+312:         return []
+313:     return [c for c in cidades if alvo in _normalizar(c)]
+314: 
+315: 
+316: def _descobrir_bairros(cidade, uf, municipio):
+317:     """Monta a lista final de bairros: distritos do IBGE + complemento do OSM.
 318: 
-319: def _descobrir_bairros(cidade, uf, municipio):
-320:     """Monta a lista final de bairros: distritos do IBGE + complemento do OSM.
-321: 
-322:     Retorna (registros, fonte). fonte=None significa "não gravar no cache" —
-323:     usado quando houve falha de rede, para tentar de novo na próxima execução.
-324:     """
-325:     registros = []
-326:     total_distritos = 0
-327:     if municipio:
-328:         distritos = _baixar_distritos(municipio["id_municipio"]) or []
-329:         total_distritos = len(distritos)
-330:         for distrito in distritos:
-331:             if _normalizar(distrito["nome"]) == _normalizar(cidade):
-332:                 continue
-333:             registros.append({"nome": distrito["nome"], "id_distrito": distrito["id_distrito"]})
-334: 
-335:     if len(registros) >= MIN_BAIRROS:
-336:         print(f"  IBGE: {len(registros)} distritos de {cidade}-{uf} serão usados como áreas de busca.")
-337:         return registros, localidades_db.FONTE_IBGE
-338: 
-339:     # A API de Localidades do IBGE só tem distritos/subdistritos — não tem bairros.
-340:     # Quando o município tem apenas o distrito-sede, não há o que aproveitar.
-341:     if total_distritos <= 1:
-342:         print(f"  IBGE não publica bairros para {cidade}-{uf}: o município tem apenas "
-343:               f"{total_distritos} distrito (a sede).")
-344:     else:
-345:         print(f"  IBGE: apenas {len(registros)} distrito(s) além da sede em {cidade}-{uf}.")
+319:     Retorna (registros, fonte). fonte=None significa "não gravar no cache" —
+320:     usado quando houve falha de rede, para tentar de novo na próxima execução.
+321:     """
+322:     registros = []
+323:     total_distritos = 0
+324:     if municipio:
+325:         distritos = _baixar_distritos(municipio["id_municipio"]) or []
+326:         total_distritos = len(distritos)
+327:         for distrito in distritos:
+328:             if _normalizar(distrito["nome"]) == _normalizar(cidade):
+329:                 continue
+330:             registros.append({"nome": distrito["nome"], "id_distrito": distrito["id_distrito"]})
+331: 
+332:     if len(registros) >= MIN_BAIRROS:
+333:         print(f"  IBGE: {len(registros)} distritos de {cidade}-{uf} serão usados como áreas de busca.")
+334:         return registros, localidades_db.FONTE_IBGE
+335: 
+336:     # A API de Localidades do IBGE só tem distritos/subdistritos — não tem bairros.
+337:     # Quando o município tem apenas o distrito-sede, não há o que aproveitar.
+338:     if total_distritos <= 1:
+339:         print(f"  IBGE não publica bairros para {cidade}-{uf}: o município tem apenas "
+340:               f"{total_distritos} distrito (a sede).")
+341:     else:
+342:         print(f"  IBGE: apenas {len(registros)} distrito(s) além da sede em {cidade}-{uf}.")
+343: 
+344:     print("  Buscando bairros no OpenStreetMap...")
+345:     bairros_osm = _bairros_via_overpass(cidade, uf)
 346: 
-347:     print("  Buscando bairros no OpenStreetMap...")
-348:     bairros_osm = _bairros_via_overpass(cidade, uf)
-349: 
-350:     if bairros_osm is None:
-351:         print("  OpenStreetMap indisponível. Esta cidade NÃO será gravada no cache;")
-352:         print("  os distritos do IBGE serão usados apenas nesta execução.")
-353:         return registros, None
-354: 
-355:     vistos = {_normalizar(r["nome"]) for r in registros}
-356:     for nome in bairros_osm:
-357:         if _normalizar(nome) not in vistos:
-358:             vistos.add(_normalizar(nome))
-359:             registros.append({"nome": nome, "id_distrito": None})
-360: 
-361:     if bairros_osm:
-362:         return registros, localidades_db.FONTE_OVERPASS
-363:     if registros:
-364:         return registros, localidades_db.FONTE_IBGE
-365:     return [], localidades_db.FONTE_CIDADE
-366: 
+347:     if bairros_osm is None:
+348:         print("  OpenStreetMap indisponível. Esta cidade NÃO será gravada no cache;")
+349:         print("  os distritos do IBGE serão usados apenas nesta execução.")
+350:         return registros, None
+351: 
+352:     vistos = {_normalizar(r["nome"]) for r in registros}
+353:     for nome in bairros_osm:
+354:         if _normalizar(nome) not in vistos:
+355:             vistos.add(_normalizar(nome))
+356:             registros.append({"nome": nome, "id_distrito": None})
+357: 
+358:     if bairros_osm:
+359:         return registros, localidades_db.FONTE_OVERPASS
+360:     if registros:
+361:         return registros, localidades_db.FONTE_IBGE
+362:     return [], localidades_db.FONTE_CIDADE
+363: 
+364: 
+365: def _resolver_municipio(cidade, uf):
+366:     """Descobre o município no IBGE: id e nome oficial.
 367: 
-368: def _resolver_municipio(cidade, uf):
-369:     """Descobre o município no IBGE: id e nome oficial.
-370: 
-371:     Primeiro tenta a base local; se não achar, baixa a lista da UF (e grava, se
-372:     LOCALIDADES_SALVAR permitir). Retorna None quando o nome não existe na UF.
-373:     """
-374:     alvo = _normalizar(cidade)
-375: 
-376:     municipios = _cache(localidades_db.ler_municipios, uf) or []
-377:     for item in municipios:
-378:         if _normalizar(item["nome"]) == alvo:
-379:             return {
-380:                 "id_municipio": item["id_municipio"],
-381:                 "nome": item["nome"],
-382:                 "uf": uf,
-383:                 "bairros_fonte": item.get("bairros_fonte"),
-384:             }
+368:     Primeiro tenta a base local; se não achar, baixa a lista da UF (e grava, se
+369:     LOCALIDADES_SALVAR permitir). Retorna None quando o nome não existe na UF.
+370:     """
+371:     alvo = _normalizar(cidade)
+372: 
+373:     municipios = _cache(localidades_db.ler_municipios, uf) or []
+374:     for item in municipios:
+375:         if _normalizar(item["nome"]) == alvo:
+376:             return {
+377:                 "id_municipio": item["id_municipio"],
+378:                 "nome": item["nome"],
+379:                 "uf": uf,
+380:                 "bairros_fonte": item.get("bairros_fonte"),
+381:             }
+382: 
+383:     baixados = _municipios_da_uf(uf) or []
+384:     _salvar(localidades_db.salvar_municipios, baixados)
 385: 
-386:     baixados = _municipios_da_uf(uf) or []
-387:     _salvar(localidades_db.salvar_municipios, baixados)
-388: 
-389:     for item in baixados:
-390:         if _normalizar(item["nome"]) == alvo:
-391:             return {
-392:                 "id_municipio": item["id_municipio"],
-393:                 "nome": item["nome"],
-394:                 "uf": item["uf"],
-395:                 "bairros_fonte": None,
-396:             }
-397: 
-398:     if mun := _cache(localidades_db.buscar_municipio, cidade, uf):
-399:         return mun
-400:     return None
-401: 
+386:     for item in baixados:
+387:         if _normalizar(item["nome"]) == alvo:
+388:             return {
+389:                 "id_municipio": item["id_municipio"],
+390:                 "nome": item["nome"],
+391:                 "uf": item["uf"],
+392:                 "bairros_fonte": None,
+393:             }
+394: 
+395:     if mun := _cache(localidades_db.buscar_municipio, cidade, uf):
+396:         return mun
+397:     return None
+398: 
+399: 
+400: def obter_municipio(cidade, uf):
+401:     """Retorna o município do IBGE para o nome digitado (id, nome oficial e uf).
 402: 
-403: def obter_municipio(cidade, uf):
-404:     """Retorna o município do IBGE para o nome digitado (id, nome oficial e uf).
-405: 
-406:     Útil para gravar sempre o nome oficial, mesmo que o usuário digite sem
-407:     acento ou em minúsculas (ex.: "canoas" -> "Canoas").
-408:     """
-409:     return _resolver_municipio(cidade, uf)
-410: 
-411: 
-412: def obter_bairros(cidade, uf):
+403:     Útil para gravar sempre o nome oficial, mesmo que o usuário digite sem
+404:     acento ou em minúsculas (ex.: "canoas" -> "Canoas").
+405:     """
+406:     return _resolver_municipio(cidade, uf)
+407: 
+408: 
+409: def obter_bairros(cidade, uf):
+410:     """
+411:     Retorna os bairros de uma cidade, usando a base local quando possível.
+412:     Lista vazia significa "buscar a cidade inteira".
 413:     """
-414:     Retorna os bairros de uma cidade, usando a base local quando possível.
-415:     Lista vazia significa "buscar a cidade inteira".
-416:     """
-417:     municipio = _resolver_municipio(cidade, uf)
+414:     municipio = _resolver_municipio(cidade, uf)
+415: 
+416:     # Nome oficial do IBGE: evita divergência de acento/caixa nas buscas.
+417:     nome_oficial = municipio["nome"] if municipio else cidade
 418: 
-419:     # Nome oficial do IBGE: evita divergência de acento/caixa nas buscas.
-420:     nome_oficial = municipio["nome"] if municipio else cidade
-421: 
-422:     if USAR_CACHE and municipio and municipio.get("bairros_fonte"):
-423:         bairros = _cache(localidades_db.ler_bairros, municipio["id_municipio"]) or []
-424:         # O distrito-sede tem o mesmo nome da cidade e não ajuda na busca por área.
-425:         bairros = [b for b in bairros if _normalizar(b) != _normalizar(nome_oficial)]
-426:         fonte = municipio["bairros_fonte"]
-427:         if fonte == localidades_db.FONTE_CIDADE or not bairros:
-428:             print(f"Base local: {nome_oficial}-{uf} sem bairros (fonte: {fonte}).")
-429:             return []
-430:         print(f"Base local: {len(bairros)} bairros de {nome_oficial}-{uf} (fonte: {fonte}).")
-431:         return bairros
-432: 
-433:     bairros, fonte = _descobrir_bairros(nome_oficial, uf, municipio)
+419:     if USAR_CACHE and municipio and municipio.get("bairros_fonte"):
+420:         bairros = _cache(localidades_db.ler_bairros, municipio["id_municipio"]) or []
+421:         # O distrito-sede tem o mesmo nome da cidade e não ajuda na busca por área.
+422:         bairros = [b for b in bairros if _normalizar(b) != _normalizar(nome_oficial)]
+423:         fonte = municipio["bairros_fonte"]
+424:         if fonte == localidades_db.FONTE_CIDADE or not bairros:
+425:             print(f"Base local: {nome_oficial}-{uf} sem bairros (fonte: {fonte}).")
+426:             return []
+427:         print(f"Base local: {len(bairros)} bairros de {nome_oficial}-{uf} (fonte: {fonte}).")
+428:         return bairros
+429: 
+430:     bairros, fonte = _descobrir_bairros(nome_oficial, uf, municipio)
+431: 
+432:     if municipio and fonte:
+433:         _salvar(localidades_db.salvar_bairros, municipio["id_municipio"], bairros, fonte)
 434: 
-435:     if municipio and fonte:
-436:         _salvar(localidades_db.salvar_bairros, municipio["id_municipio"], bairros, fonte)
+435:     return [b["nome"] for b in bairros]
+436: 
 437: 
-438:     return [b["nome"] for b in bairros]
-439: 
-440: 
-441: def obter_termos_busca(cidade, uf, max_bairros=30):
-442:     """
-443:     Divide a coleta por bairros para ampliar a cobertura do Google Maps
-444:     (que pagina os resultados e não entrega a cidade inteira em uma única busca).
-445:     Se nenhum bairro for descoberto, busca a cidade inteira como fallback.
-446:     """
-447:     print(f"Descobrindo bairros de {cidade} - {uf}...")
-448:     bairros = obter_bairros(cidade, uf)
-449: 
-450:     if bairros:
-451:         bairros = bairros[:max_bairros]
-452:         print(f"{len(bairros)} bairros encontrados. A coleta será dividida por bairro.")
-453:         return bairros
+438: def obter_termos_busca(cidade, uf, max_bairros=30):
+439:     """
+440:     Divide a coleta por bairros para ampliar a cobertura do Google Maps
+441:     (que pagina os resultados e não entrega a cidade inteira em uma única busca).
+442:     Se nenhum bairro for descoberto, busca a cidade inteira como fallback.
+443:     """
+444:     print(f"Descobrindo bairros de {cidade} - {uf}...")
+445:     bairros = obter_bairros(cidade, uf)
+446: 
+447:     if bairros:
+448:         bairros = bairros[:max_bairros]
+449:         print(f"{len(bairros)} bairros encontrados. A coleta será dividida por bairro.")
+450:         return bairros
+451: 
+452:     print("Nenhum bairro encontrado. Buscando a cidade inteira.")
+453:     return [cidade]
 454: 
-455:     print("Nenhum bairro encontrado. Buscando a cidade inteira.")
-456:     return [cidade]
-457: 
+455: 
+456: def listar_municipios_pendentes(uf):
+457:     """Lista os municípios da UF que ainda não têm bairros resolvidos.
 458: 
-459: def listar_municipios_pendentes(uf):
-460:     """Lista os municípios da UF que ainda não têm bairros resolvidos.
-461: 
-462:     Se a UF ainda não estiver na base local, baixa a lista do IBGE (e grava, se
-463:     LOCALIDADES_SALVAR permitir). Retorna [] quando todos já estão resolvidos.
-464:     """
-465:     pendentes = _cache(localidades_db.ler_municipios_pendentes, uf)
-466:     if pendentes is None:
-467:         return []
-468:     if pendentes:
-469:         return pendentes
-470: 
-471:     # Nada pendente: só é "tudo pronto" se a UF estiver na base local.
-472:     if _cache(localidades_db.ler_municipios, uf):
-473:         return []
-474: 
-475:     print(f"  {uf} ainda não está na base local. Baixando a lista de municípios do IBGE...")
-476:     municipios = _baixar_municipios(uf)
-477:     if not municipios:
-478:         return []
-479:     _salvar(localidades_db.salvar_municipios, municipios)
-480:     return [{"id_municipio": m["id_municipio"], "nome": m["nome"]} for m in municipios]
-481: 
+459:     Se a UF ainda não estiver na base local, baixa a lista do IBGE (e grava, se
+460:     LOCALIDADES_SALVAR permitir). Retorna [] quando todos já estão resolvidos.
+461:     """
+462:     pendentes = _cache(localidades_db.ler_municipios_pendentes, uf)
+463:     if pendentes is None:
+464:         return []
+465:     if pendentes:
+466:         return pendentes
+467: 
+468:     # Nada pendente: só é "tudo pronto" se a UF estiver na base local.
+469:     if _cache(localidades_db.ler_municipios, uf):
+470:         return []
+471: 
+472:     print(f"  {uf} ainda não está na base local. Baixando a lista de municípios do IBGE...")
+473:     municipios = _baixar_municipios(uf)
+474:     if not municipios:
+475:         return []
+476:     _salvar(localidades_db.salvar_municipios, municipios)
+477:     return [{"id_municipio": m["id_municipio"], "nome": m["nome"]} for m in municipios]
+478: 
+479: 
+480: def aquecer_bairros_uf(uf, cidades=None, max_cidades=0, pausa_segundos=None):
+481:     """Resolve e grava os bairros de todas as cidades de uma UF (uma única vez).
 482: 
-483: def aquecer_bairros_uf(uf, cidades=None, max_cidades=0, pausa_segundos=None):
-484:     """Resolve e grava os bairros de todas as cidades de uma UF (uma única vez).
-485: 
-486:     Útil para preparar o cache e depois rodar a coleta sem nenhuma consulta de
-487:     rede. A pausa entre cidades é aplicada só quando o OpenStreetMap foi de fato
-488:     consultado (cidades cobertas pelo IBGE são instantâneas).
-489: 
-490:     Retorna um dicionário com o resumo da execução.
-491:     """
-492:     if not SALVAR:
-493:         print("\nLOCALIDADES_SALVAR=false: não é possível aquecer a base local.")
-494:         print("Ative a flag LOCALIDADES_SALVAR para gravar os bairros.")
-495:         return None
-496: 
-497:     pausa_segundos = AQUECER_PAUSA_PADRAO if pausa_segundos is None else pausa_segundos
-498: 
-499:     if cidades is None:
-500:         print(f"\nVerificando quais cidades de {uf} ainda precisam de bairros...")
-501:         cidades = listar_municipios_pendentes(uf)
-502: 
-503:     total_pendente = len(cidades)
-504:     if not total_pendente:
-505:         print(f"Todas as cidades de {uf} já têm bairros na base local. Nada a fazer.")
-506:         return {"uf": uf, "pendentes": 0, "processadas": 0, "ibge": 0,
-507:                 "osm": 0, "sem_bairros": 0, "falhas": 0}
+483:     Útil para preparar o cache e depois rodar a coleta sem nenhuma consulta de
+484:     rede. A pausa entre cidades é aplicada só quando o OpenStreetMap foi de fato
+485:     consultado (cidades cobertas pelo IBGE são instantâneas).
+486: 
+487:     Retorna um dicionário com o resumo da execução.
+488:     """
+489:     if not SALVAR:
+490:         print("\nLOCALIDADES_SALVAR=false: não é possível aquecer a base local.")
+491:         print("Ative a flag LOCALIDADES_SALVAR para gravar os bairros.")
+492:         return None
+493: 
+494:     pausa_segundos = AQUECER_PAUSA_PADRAO if pausa_segundos is None else pausa_segundos
+495: 
+496:     if cidades is None:
+497:         print(f"\nVerificando quais cidades de {uf} ainda precisam de bairros...")
+498:         cidades = listar_municipios_pendentes(uf)
+499: 
+500:     total_pendente = len(cidades)
+501:     if not total_pendente:
+502:         print(f"Todas as cidades de {uf} já têm bairros na base local. Nada a fazer.")
+503:         return {"uf": uf, "pendentes": 0, "processadas": 0, "ibge": 0,
+504:                 "osm": 0, "sem_bairros": 0, "falhas": 0}
+505: 
+506:     if max_cidades and max_cidades > 0:
+507:         cidades = cidades[:max_cidades]
 508: 
-509:     if max_cidades and max_cidades > 0:
-510:         cidades = cidades[:max_cidades]
-511: 
-512:     print(f"\nAquecendo bairros de {len(cidades)} cidade(s) de {uf} "
-513:           f"({total_pendente} pendente(s) no total).")
-514:     print(f"Pausa entre cidades que usam OpenStreetMap: {pausa_segundos}s")
-515:     print("Interrompa com Ctrl+C — o progresso já gravado é preservado.\n")
+509:     print(f"\nAquecendo bairros de {len(cidades)} cidade(s) de {uf} "
+510:           f"({total_pendente} pendente(s) no total).")
+511:     print(f"Pausa entre cidades que usam OpenStreetMap: {pausa_segundos}s")
+512:     print("Interrompa com Ctrl+C — o progresso já gravado é preservado.\n")
+513: 
+514:     resumo = {"uf": uf, "pendentes": total_pendente, "processadas": 0,
+515:               "ibge": 0, "osm": 0, "sem_bairros": 0, "falhas": 0}
 516: 
-517:     resumo = {"uf": uf, "pendentes": total_pendente, "processadas": 0,
-518:               "ibge": 0, "osm": 0, "sem_bairros": 0, "falhas": 0}
-519: 
-520:     try:
-521:         for indice, cidade in enumerate(cidades, 1):
-522:             nome = cidade["nome"]
-523:             print(f"[{indice}/{len(cidades)}] {nome}-{uf}")
-524: 
-525:             bairros = obter_bairros(nome, uf)
-526:             municipio = _cache(localidades_db.buscar_municipio, nome, uf)
-527:             fonte = (municipio or {}).get("bairros_fonte")
-528:             resumo["processadas"] += 1
-529: 
-530:             if fonte is None:
-531:                 resumo["falhas"] += 1
-532:                 print(f"  Falhou (nada gravado). Pulando.")
-533:             elif fonte == localidades_db.FONTE_OVERPASS:
-534:                 resumo["osm"] += 1
-535:             elif fonte == localidades_db.FONTE_IBGE:
-536:                 resumo["ibge"] += 1
-537:             else:
-538:                 resumo["sem_bairros"] += 1
-539: 
-540:             usou_osm = fonte in (localidades_db.FONTE_OVERPASS,
-541:                                  localidades_db.FONTE_CIDADE)
-542:             if usou_osm and indice < len(cidades):
-543:                 time.sleep(pausa_segundos)
-544:     except KeyboardInterrupt:
-545:         print("\nInterrompido pelo usuário. O que já foi gravado está preservado.")
-546: 
-547:     print(f"\nResumo de {uf}: {resumo['processadas']} cidade(s) processada(s) "
-548:           f"de {total_pendente} pendente(s).")
-549:     print(f"  via IBGE: {resumo['ibge']} | via OpenStreetMap: {resumo['osm']} | "
-550:           f"sem bairros: {resumo['sem_bairros']} | falhas: {resumo['falhas']}")
-551:     restantes = total_pendente - resumo["processadas"]
-552:     if restantes > 0:
-553:         print(f"  {restantes} cidade(s) continuam pendentes — rode novamente para retomar.")
-554:     return resumo
-555: 
-556: 
-557: def _descrever_gravacao(total, recebidos):
-558:     """Texto do resumo da sincronização (distingue gravado de apenas baixado)."""
-559:     if total is None:
-560:         return f"{recebidos} recebidos, NÃO gravados (base local indisponível)"
-561:     return f"{total} gravados"
-562: 
+517:     try:
+518:         for indice, cidade in enumerate(cidades, 1):
+519:             nome = cidade["nome"]
+520:             print(f"[{indice}/{len(cidades)}] {nome}-{uf}")
+521: 
+522:             bairros = obter_bairros(nome, uf)
+523:             municipio = _cache(localidades_db.buscar_municipio, nome, uf)
+524:             fonte = (municipio or {}).get("bairros_fonte")
+525:             resumo["processadas"] += 1
+526: 
+527:             if fonte is None:
+528:                 resumo["falhas"] += 1
+529:                 print(f"  Falhou (nada gravado). Pulando.")
+530:             elif fonte == localidades_db.FONTE_OVERPASS:
+531:                 resumo["osm"] += 1
+532:             elif fonte == localidades_db.FONTE_IBGE:
+533:                 resumo["ibge"] += 1
+534:             else:
+535:                 resumo["sem_bairros"] += 1
+536: 
+537:             usou_osm = fonte in (localidades_db.FONTE_OVERPASS,
+538:                                  localidades_db.FONTE_CIDADE)
+539:             if usou_osm and indice < len(cidades):
+540:                 time.sleep(pausa_segundos)
+541:     except KeyboardInterrupt:
+542:         print("\nInterrompido pelo usuário. O que já foi gravado está preservado.")
+543: 
+544:     print(f"\nResumo de {uf}: {resumo['processadas']} cidade(s) processada(s) "
+545:           f"de {total_pendente} pendente(s).")
+546:     print(f"  via IBGE: {resumo['ibge']} | via OpenStreetMap: {resumo['osm']} | "
+547:           f"sem bairros: {resumo['sem_bairros']} | falhas: {resumo['falhas']}")
+548:     restantes = total_pendente - resumo["processadas"]
+549:     if restantes > 0:
+550:         print(f"  {restantes} cidade(s) continuam pendentes — rode novamente para retomar.")
+551:     return resumo
+552: 
+553: 
+554: def _descrever_gravacao(total, recebidos):
+555:     """Texto do resumo da sincronização (distingue gravado de apenas baixado)."""
+556:     if total is None:
+557:         return f"{recebidos} recebidos, NÃO gravados (base local indisponível)"
+558:     return f"{total} gravados"
+559: 
+560: 
+561: def sincronizar_base_localidades():
+562:     """Baixa estados, municípios e distritos do IBGE para o DuckDB.
 563: 
-564: def sincronizar_base_localidades():
-565:     """Baixa estados, municípios e distritos do IBGE para o DuckDB.
-566: 
-567:     Depois disso, com LOCALIDADES_USAR_CACHE=true, a coleta não faz chamadas de
-568:     rede para descobrir bairros — exceto nas cidades em que o IBGE não tem
-569:     distritos úteis (aí o OSM é consultado uma única vez e o resultado é gravado).
-570:     """
-571:     if not SALVAR:
-572:         print("\nLOCALIDADES_SALVAR=false: a sincronização está desativada.")
-573:         print("Nada foi baixado nem gravado. Ative a flag para popular a base local.")
-574:         return False
-575: 
-576:     print("\nSincronizando base de localidades do IBGE...")
-577: 
-578:     estados = _baixar_estados()
-579:     if estados is None:
-580:         print("Falha ao baixar os estados. Sincronização abortada.")
-581:         return False
-582:     total = _salvar(localidades_db.salvar_estados, estados)
-583:     print(f"  Estados: {_descrever_gravacao(total, len(estados))}.")
-584: 
-585:     municipios = _baixar_municipios()
-586:     if municipios is None:
-587:         print("Falha ao baixar os municípios. Sincronização abortada.")
-588:         return False
-589:     total = _salvar(localidades_db.salvar_municipios, municipios)
-590:     print(f"  Municípios: {_descrever_gravacao(total, len(municipios))}.")
-591: 
-592:     print("  Baixando distritos (pode levar alguns segundos)...")
-593:     distritos = _baixar_distritos()
-594:     if distritos is None:
-595:         print("Falha ao baixar os distritos. Estados e municípios foram gravados.")
-596:         return False
-597:     total = _salvar(localidades_db.salvar_distritos_bulk, distritos, MIN_BAIRROS)
-598:     print(f"  Distritos: {_descrever_gravacao(total, len(distritos))}.")
-599: 
-600:     stats = _cache(localidades_db.estatisticas) or {}
-601:     print(f"\nBase local: {stats.get('estados', 0)} estados, "
-602:           f"{stats.get('municipios', 0)} municípios, {stats.get('bairros', 0)} bairros "
-603:           f"({stats.get('cidades_prontas', 0)} cidades com bairros prontos).")
-604:     print("Sincronização concluída.")
-605:     return True
-`````
+564:     Depois disso, com LOCALIDADES_USAR_CACHE=true, a coleta não faz chamadas de
+565:     rede para descobrir bairros — exceto nas cidades em que o IBGE não tem
+566:     distritos úteis (aí o OSM é consultado uma única vez e o resultado é gravado).
+567:     """
+568:     if not SALVAR:
+569:         print("\nLOCALIDADES_SALVAR=false: a sincronização está desativada.")
+570:         print("Nada foi baixado nem gravado. Ative a flag para popular a base local.")
+571:         return False
+572: 
+573:     print("\nSincronizando base de localidades do IBGE...")
+574: 
+575:     estados = _baixar_estados()
+576:     if estados is None:
+577:         print("Falha ao baixar os estados. Sincronização abortada.")
+578:         return False
+579:     total = _salvar(localidades_db.salvar_estados, estados)
+580:     print(f"  Estados: {_descrever_gravacao(total, len(estados))}.")
+581: 
+582:     municipios = _baixar_municipios()
+583:     if municipios is None:
+584:         print("Falha ao baixar os municípios. Sincronização abortada.")
+585:         return False
+586:     total = _salvar(localidades_db.salvar_municipios, municipios)
+587:     print(f"  Municípios: {_descrever_gravacao(total, len(municipios))}.")
+588: 
+589:     print("  Baixando distritos (pode levar alguns segundos)...")
+590:     distritos = _baixar_distritos()
+591:     if distritos is None:
+592:         print("Falha ao baixar os distritos. Estados e municípios foram gravados.")
+593:         return False
+594:     total = _salvar(localidades_db.salvar_distritos_bulk, distritos, MIN_BAIRROS)
+595:     print(f"  Distritos: {_descrever_gravacao(total, len(distritos))}.")
+596: 
+597:     stats = _cache(localidades_db.estatisticas) or {}
+598:     print(f"\nBase local: {stats.get('estados', 0)} estados, "
+599:           f"{stats.get('municipios', 0)} municípios, {stats.get('bairros', 0)} bairros "
+600:           f"({stats.get('cidades_prontas', 0)} cidades com bairros prontos).")
+601:     print("Sincronização concluída.")
+602:     return True
+````
 
 ## File: src/whatsapp.py
-`````python
+````python
   1: # src/whatsapp.py
   2: """Integração com a WAHA (WhatsApp HTTP API) para envio de mensagens aos leads.
   3: 
@@ -2766,234 +3007,319 @@ requirements.txt
  12:     - ainda não enviados (status_whatsapp = 'pendente' ou NULL)
  13: """
  14: import os
- 15: import re
- 16: import time
- 17: 
- 18: import requests
- 19: 
- 20: from src.config import carregar_env, str_para_bool
- 21: 
- 22: carregar_env()
- 23: 
- 24: WAHA_API_URL = os.environ.get("WAHA_API_URL", "http://localhost:3000")
- 25: WAHA_API_KEY = os.environ.get("WAHA_API_KEY", "")
- 26: WAHA_SESSION = os.environ.get("WAHA_SESSION", "default")
- 27: 
- 28: # Se false, o módulo NÃO tenta enviar (desliga o envio de WhatsApp).
- 29: WAHA_ATIVO = str_para_bool(os.environ.get("WAHA_ATIVO"), padrao=True)
- 30: 
- 31: # Se true, pula a coleta e vai direto para o envio (não coleta nada).
- 32: SOMENTE_ENVIO = str_para_bool(os.environ.get("SOMENTE_ENVIO"), padrao=False)
- 33: 
- 34: # Intervalo (segundos) entre envios e limite de leads por campanha.
- 35: # WAHA_LIMITE vazio = sem limite (envia todos os pendentes).
- 36: WAHA_INTERVALO = int(os.environ.get("WAHA_INTERVALO", "13"))
- 37: WAHA_LIMITE = os.environ.get("WAHA_LIMITE", "").strip()
- 38: WAHA_LIMITE = int(WAHA_LIMITE) if WAHA_LIMITE else None
- 39: 
- 40: # Mensagem padrão (placeholder). Use {nome}, {bairro} e {cidade}.
- 41: MENSAGEM_PADRAO = "Olá {nome}! Vi que vocês atendem no bairro {bairro}, em {cidade}. Podemos conversar?"
+ 15: import random
+ 16: import re
+ 17: import time
+ 18: 
+ 19: import requests
+ 20: 
+ 21: from src.config import carregar_env, str_para_bool
+ 22: 
+ 23: carregar_env()
+ 24: 
+ 25: WAHA_API_URL = os.environ.get("WAHA_API_URL", "http://localhost:3000")
+ 26: WAHA_API_KEY = os.environ.get("WAHA_API_KEY", "")
+ 27: WAHA_SESSION = os.environ.get("WAHA_SESSION", "default")
+ 28: 
+ 29: # Se false, o módulo NÃO tenta enviar (desliga o envio de WhatsApp).
+ 30: WAHA_ATIVO = str_para_bool(os.environ.get("WAHA_ATIVO"), padrao=True)
+ 31: 
+ 32: # Se true, pula a coleta e vai direto para o envio (não coleta nada).
+ 33: SOMENTE_ENVIO = str_para_bool(os.environ.get("SOMENTE_ENVIO"), padrao=False)
+ 34: 
+ 35: # ---------------------------------------------------------------------------
+ 36: # Cadência de envio (anti-bloqueio)
+ 37: # ---------------------------------------------------------------------------
+ 38: # Formato "X a cada Y segundos", ex.: WAHA_CADENCIA=3:60  -> 3 envios por minuto.
+ 39: # Os envios são distribuídos ALEATORIAMENTE dentro da janela de Y segundos,
+ 40: # evitando pausas fixas (15s, 15s, ...) que são mais fáceis de detectar.
+ 41: WAHA_CADENCIA = os.environ.get("WAHA_CADENCIA", "").strip()
  42: 
- 43: 
- 44: def _normalizar_chatid(telefone):
- 45:     """Converte o telefone salvo em um chatId clássico do WAHA (55DDDNUMERO@c.us)."""
- 46:     numero = re.sub(r"\D", "", str(telefone or ""))
- 47:     if not numero:
- 48:         return None
- 49: 
- 50:     # Se veio com DDI 55 e tem mais de 11 dígitos, remove o prefixo.
- 51:     if numero.startswith("55") and len(numero) > 11:
- 52:         numero = numero[2:]
- 53: 
- 54:     # Celular brasileiro tem 11 dígitos (DDD + 9 dígitos).
- 55:     if len(numero) != 11:
- 56:         return None
- 57: 
- 58:     return f"55{numero}@c.us"
- 59: 
- 60: 
- 61: def _resolver_chatid_waha(telefone, session=None, api_url=None, api_key=None):
- 62:     """Resolve o chatId correto via /api/checkNumberStatus.
- 63: 
- 64:     Números recentes no WhatsApp usam o formato @lid (hidden user ID) em vez do
- 65:     clássico @c.us. Enviar com @c.us para esses números retorna HTTP 500.
- 66:     A WAHA responde o chatId certo via checkNumberStatus; usamos ele e, se a
- 67:     consulta falhar ou o número não existir, caímos no formato clássico @c.us.
- 68:     """
- 69:     session = session or WAHA_SESSION
- 70:     api_url = api_url or WAHA_API_URL
- 71:     api_key = api_key if api_key is not None else WAHA_API_KEY
+ 43: # Legado: WAHA_INTERVALO (pausa fixa) continua funcionando quando WAHA_CADENCIA
+ 44: # não é informado.
+ 45: WAHA_INTERVALO = int(os.environ.get("WAHA_INTERVALO", "13"))
+ 46: 
+ 47: # Limite de leads por campanha. Vazio = sem limite.
+ 48: WAHA_LIMITE = os.environ.get("WAHA_LIMITE", "").strip()
+ 49: WAHA_LIMITE = int(WAHA_LIMITE) if WAHA_LIMITE else None
+ 50: 
+ 51: 
+ 52: def _parse_cadencia(valor):
+ 53:     """Interpreta "N:Y" -> (envios_por_janela, janela_segundos).
+ 54: 
+ 55:     Retorna None quando o valor está vazio/inválido (usa o intervalo fixo).
+ 56:     """
+ 57:     if not valor:
+ 58:         return None
+ 59:     try:
+ 60:         envios, janela = valor.split(":", 1)
+ 61:         envios = int(envios.strip())
+ 62:         janela = int(janela.strip())
+ 63:     except (ValueError, AttributeError):
+ 64:         return None
+ 65:     if envios <= 0 or janela <= 0:
+ 66:         return None
+ 67:     return envios, janela
+ 68: 
+ 69: 
+ 70: def _intervalos_aleatorios(quantidade, janela_segundos):
+ 71:     """Gera as pausas (em segundos) para `quantidade` envios numa janela.
  72: 
- 73:     numero = re.sub(r"\D", "", str(telefone or ""))
- 74:     if not numero:
- 75:         return None
- 76: 
- 77:     if numero.startswith("55") and len(numero) > 11:
- 78:         numero = numero[2:]
- 79:     if len(numero) != 11:
- 80:         return None
- 81: 
- 82:     telefone_internacional = f"55{numero}"
- 83: 
- 84:     headers = {"Accept": "application/json"}
- 85:     if api_key:
- 86:         headers["X-Api-Key"] = api_key
+ 73:     Distribui os envios em pontos aleatórios crescentes dentro da janela e
+ 74:     retorna a diferença entre pontos consecutivos — o intervalo entre cada envio
+ 75:     varia, mas o total da janela é respeitado.
+ 76:     """
+ 77:     if quantidade <= 1:
+ 78:         return [0]
+ 79:     # Pontos aleatórios crescentes: 1 envio em cada "fatia" da janela, com
+ 80:     # jitter dentro da fatia, garantindo tempos diferentes entre os envios.
+ 81:     pontos = sorted(
+ 82:         random.uniform((i * janela_segundos) / quantidade,
+ 83:                        ((i + 1) * janela_segundos) / quantidade)
+ 84:         for i in range(quantidade)
+ 85:     )
+ 86:     return [round(pontos[i + 1] - pontos[i], 2) for i in range(quantidade - 1)]
  87: 
- 88:     url = f"{api_url.rstrip('/')}/api/checkNumberStatus"
- 89:     params = {"session": session, "phone": telefone_internacional}
- 90: 
- 91:     try:
- 92:         response = requests.get(url, params=params, headers=headers, timeout=20)
- 93:         response.raise_for_status()
- 94:         dados = response.json()
- 95:         if dados.get("numberExists") and dados.get("chatId"):
- 96:             return dados["chatId"]
- 97:     except Exception:
- 98:         pass
- 99: 
-100:     # Fallback: formato clássico @c.us (funciona para números mais antigos).
-101:     return f"{telefone_internacional}@c.us"
-102: 
-103: 
-104: def _limpar_markdown_whatsapp(texto):
-105:     """Remove marcação de markdown (negrito e links) antes de enviar ao WhatsApp.
-106: 
-107:     - **texto**  -> texto
-108:     - [rótulo](url) -> url (quando o rótulo já é a própria URL) ou "rótulo (url)"
-109:     """
-110:     texto = re.sub(r"\*\*([^*]+)\*\*", r"\1", texto)
+ 88: 
+ 89: def _pausas_cadencia(total, envios_janela, janela_segundos):
+ 90:     """Gera as pausas da campanha inteira respeitando a cadência.
+ 91: 
+ 92:     Agrupa os `total` envios em janelas de `janela_segundos` segundos, com
+ 93:     `envios_janela` envios por janela (distribuídos aleatoriamente). Retorna uma
+ 94:     lista com `total - 1` pausas (uma entre cada par consecutivo).
+ 95:     """
+ 96:     if total <= 1:
+ 97:         return [0]
+ 98: 
+ 99:     # Timestamp de envio de cada lead: janela + posição aleatória dentro dela.
+100:     tempos = []
+101:     for idx in range(total):
+102:         janela_idx = idx // envios_janela
+103:         pos_na_janela = idx % envios_janela
+104:         inicio = janela_idx * janela_segundos
+105:         # posição aleatória dentro da fatia correspondente a este envio
+106:         p = random.uniform(
+107:             inicio + (pos_na_janela * janela_segundos) / envios_janela,
+108:             inicio + ((pos_na_janela + 1) * janela_segundos) / envios_janela,
+109:         )
+110:         tempos.append(p)
 111: 
-112:     def _sub_link(match):
-113:         rotulo = match.group(1)
-114:         url = match.group(2)
-115:         if rotulo.strip() == url.strip():
-116:             return url
-117:         return f"{rotulo} ({url})"
+112:     tempos.sort()
+113:     return [round(tempos[i + 1] - tempos[i], 2) for i in range(len(tempos) - 1)]
+114: 
+115: # Mensagem padrão (placeholder). Use {nome}, {bairro} e {cidade}.
+116: MENSAGEM_PADRAO = "Olá {nome}! Vi que vocês atendem no bairro {bairro}, em {cidade}. Podemos conversar?"
+117: 
 118: 
-119:     return re.sub(r"\[([^\]]+)\]\(([^)]+)\)", _sub_link, texto)
-120: 
-121: 
-122: def _renderizar_mensagem(template, lead):
-123:     """Substitui {nome}, {bairro} e {cidade} de forma segura e limpa o markdown."""
-124:     bairro = str(lead.get("bairro") or "sua região")
-125:     cidade = str(lead.get("cidade") or "")
-126:     texto = (
-127:         template
-128:         .replace("{nome}", str(lead.get("nome") or ""))
-129:         .replace("{bairro}", bairro)
-130:         .replace("{cidade}", cidade)
-131:     )
-132:     return _limpar_markdown_whatsapp(texto)
-133: 
+119: def _normalizar_chatid(telefone):
+120:     """Converte o telefone salvo em um chatId clássico do WAHA (55DDDNUMERO@c.us)."""
+121:     numero = re.sub(r"\D", "", str(telefone or ""))
+122:     if not numero:
+123:         return None
+124: 
+125:     # Se veio com DDI 55 e tem mais de 11 dígitos, remove o prefixo.
+126:     if numero.startswith("55") and len(numero) > 11:
+127:         numero = numero[2:]
+128: 
+129:     # Celular brasileiro tem 11 dígitos (DDD + 9 dígitos).
+130:     if len(numero) != 11:
+131:         return None
+132: 
+133:     return f"55{numero}@c.us"
 134: 
-135: def enviar_texto_waha(chat_id, texto, session=None, api_url=None, api_key=None):
-136:     """Envia uma mensagem de texto via WAHA."""
-137:     session = session or WAHA_SESSION
-138:     api_url = api_url or WAHA_API_URL
-139:     api_key = api_key if api_key is not None else WAHA_API_KEY
-140:     url = f"{api_url.rstrip('/')}/api/sendText"
-141: 
-142:     payload = {
-143:         "session": session,
-144:         "chatId": chat_id,
-145:         "text": texto,
-146:     }
+135: 
+136: def _resolver_chatid_waha(telefone, session=None, api_url=None, api_key=None):
+137:     """Resolve o chatId correto via /api/checkNumberStatus.
+138: 
+139:     Números recentes no WhatsApp usam o formato @lid (hidden user ID) em vez do
+140:     clássico @c.us. Enviar com @c.us para esses números retorna HTTP 500.
+141:     A WAHA responde o chatId certo via checkNumberStatus; usamos ele e, se a
+142:     consulta falhar ou o número não existir, caímos no formato clássico @c.us.
+143:     """
+144:     session = session or WAHA_SESSION
+145:     api_url = api_url or WAHA_API_URL
+146:     api_key = api_key if api_key is not None else WAHA_API_KEY
 147: 
-148:     headers = {"Accept": "application/json", "Content-Type": "application/json"}
-149:     if api_key:
-150:         headers["X-Api-Key"] = api_key
+148:     numero = re.sub(r"\D", "", str(telefone or ""))
+149:     if not numero:
+150:         return None
 151: 
-152:     response = requests.post(url, json=payload, headers=headers, timeout=30)
-153:     response.raise_for_status()
-154:     return response.json()
-155: 
+152:     if numero.startswith("55") and len(numero) > 11:
+153:         numero = numero[2:]
+154:     if len(numero) != 11:
+155:         return None
 156: 
-157: def enviar_texto_numero(numero, texto, session=None, api_url=None, api_key=None):
-158:     """Envia uma mensagem de texto para um número bruto (com DDD), já normalizado.
-159: 
-160:     Útil para o envio de teste, sem precisar de um lead no banco.
-161:     """
-162:     texto = _limpar_markdown_whatsapp(texto)
-163:     chat_id = _resolver_chatid_waha(numero, session=session, api_url=api_url, api_key=api_key)
-164:     if not chat_id:
-165:         raise ValueError(f"Número inválido para envio: {numero}")
-166:     return enviar_texto_waha(chat_id, texto, session=session, api_url=api_url, api_key=api_key)
-167: 
-168: 
-169: def disparar_campanha(db, mensagem_template=None, intervalo=13, limite=None, leads=None):
-170:     """Envia mensagens para os leads celulares pendentes.
-171: 
-172:     - db: instância de LeadDatabase
-173:     - mensagem_template: texto com {nome}, {bairro}, {cidade} (usa MENSAGEM_PADRAO se None)
-174:     - intervalo: pausa em segundos entre envios (evita spam e banimento)
-175:     - leads: DataFrame opcional já filtrado; se None, busca pendentes (com limite)
-176:     """
-177:     mensagem_template = mensagem_template or MENSAGEM_PADRAO
-178:     if leads is None:
-179:         leads = db.get_leads_para_envio(limite)
-180: 
-181:     if leads.empty:
-182:         print("Nenhum lead celular pendente de envio.")
-183:         return
-184: 
-185:     total = len(leads)
-186:     print(f"Enviando para {total} lead(s) celular(es), com intervalo de {intervalo}s...")
-187: 
-188:     for i, (_, lead) in enumerate(leads.iterrows(), 1):
-189:         texto = _renderizar_mensagem(mensagem_template, lead)
-190:         lead_id = lead.get("lead_id")
-191:         telefone = lead.get("telefone")
-192:         nome = lead.get("nome")
-193:         cidade = lead.get("cidade")
-194: 
-195:         chat_id = lead.get("chat_id_waha")
-196:         if not chat_id:
-197:             # Resolve (e cacheia) o chatId uma única vez por lead. Números novos
-198:             # usam @lid; a consulta ao checkNumberStatus é feita só na primeira vez.
-199:             chat_id = _resolver_chatid_waha(telefone)
-200:             if chat_id:
-201:                 db.salvar_chat_id_waha(nome, cidade, chat_id)
-202: 
-203:         if not chat_id:
-204:             db.marcar_envio(nome, cidade, "falhou")
-205:             db.salvar_log_envio(
-206:                 lead_id, nome, cidade, telefone, chat_id, "falhou",
-207:                 mensagem=texto, erro="telefone inválido",
-208:             )
-209:             print(f"[{i}/{total}] {nome} - telefone inválido, marcado como falhou.")
-210:             continue
-211: 
-212:         try:
-213:             resposta = enviar_texto_waha(chat_id, texto)
-214:             db.marcar_envio(nome, cidade, "enviado")
-215:             db.salvar_log_envio(
-216:                 lead_id, nome, cidade, telefone, chat_id, "enviado",
-217:                 mensagem=texto, payload=resposta,
-218:             )
-219:             print(f"[{i}/{total}] ENVIADO -> {nome} ({chat_id})")
-220:         except Exception as e:
-221:             payload_erro = None
-222:             if getattr(e, "response", None) is not None:
-223:                 try:
-224:                     payload_erro = e.response.text
-225:                 except Exception:
-226:                     payload_erro = None
-227:             erro = f"{type(e).__name__}: {e}"
-228:             db.marcar_envio(nome, cidade, "falhou")
-229:             db.salvar_log_envio(
-230:                 lead_id, nome, cidade, telefone, chat_id, "falhou",
-231:                 mensagem=texto, payload=payload_erro, erro=erro,
-232:             )
-233:             print(f"[{i}/{total}] FALHOU -> {nome} ({chat_id}): {erro}")
+157:     telefone_internacional = f"55{numero}"
+158: 
+159:     headers = {"Accept": "application/json"}
+160:     if api_key:
+161:         headers["X-Api-Key"] = api_key
+162: 
+163:     url = f"{api_url.rstrip('/')}/api/checkNumberStatus"
+164:     params = {"session": session, "phone": telefone_internacional}
+165: 
+166:     try:
+167:         response = requests.get(url, params=params, headers=headers, timeout=20)
+168:         response.raise_for_status()
+169:         dados = response.json()
+170:         if dados.get("numberExists") and dados.get("chatId"):
+171:             return dados["chatId"]
+172:     except Exception:
+173:         pass
+174: 
+175:     # Fallback: formato clássico @c.us (funciona para números mais antigos).
+176:     return f"{telefone_internacional}@c.us"
+177: 
+178: 
+179: def _limpar_markdown_whatsapp(texto):
+180:     """Remove marcação de markdown (negrito e links) antes de enviar ao WhatsApp.
+181: 
+182:     - **texto**  -> texto
+183:     - [rótulo](url) -> url (quando o rótulo já é a própria URL) ou "rótulo (url)"
+184:     """
+185:     texto = re.sub(r"\*\*([^*]+)\*\*", r"\1", texto)
+186: 
+187:     def _sub_link(match):
+188:         rotulo = match.group(1)
+189:         url = match.group(2)
+190:         if rotulo.strip() == url.strip():
+191:             return url
+192:         return f"{rotulo} ({url})"
+193: 
+194:     return re.sub(r"\[([^\]]+)\]\(([^)]+)\)", _sub_link, texto)
+195: 
+196: 
+197: def _renderizar_mensagem(template, lead):
+198:     """Substitui {nome}, {bairro} e {cidade} de forma segura e limpa o markdown."""
+199:     bairro = str(lead.get("bairro") or "sua região")
+200:     cidade = str(lead.get("cidade") or "")
+201:     texto = (
+202:         template
+203:         .replace("{nome}", str(lead.get("nome") or ""))
+204:         .replace("{bairro}", bairro)
+205:         .replace("{cidade}", cidade)
+206:     )
+207:     return _limpar_markdown_whatsapp(texto)
+208: 
+209: 
+210: def enviar_texto_waha(chat_id, texto, session=None, api_url=None, api_key=None):
+211:     """Envia uma mensagem de texto via WAHA."""
+212:     session = session or WAHA_SESSION
+213:     api_url = api_url or WAHA_API_URL
+214:     api_key = api_key if api_key is not None else WAHA_API_KEY
+215:     url = f"{api_url.rstrip('/')}/api/sendText"
+216: 
+217:     payload = {
+218:         "session": session,
+219:         "chatId": chat_id,
+220:         "text": texto,
+221:     }
+222: 
+223:     headers = {"Accept": "application/json", "Content-Type": "application/json"}
+224:     if api_key:
+225:         headers["X-Api-Key"] = api_key
+226: 
+227:     response = requests.post(url, json=payload, headers=headers, timeout=30)
+228:     response.raise_for_status()
+229:     return response.json()
+230: 
+231: 
+232: def enviar_texto_numero(numero, texto, session=None, api_url=None, api_key=None):
+233:     """Envia uma mensagem de texto para um número bruto (com DDD), já normalizado.
 234: 
-235:         if i < total:
-236:             time.sleep(intervalo)
-237: 
-238:     print("Campanha finalizada.")
-`````
+235:     Útil para o envio de teste, sem precisar de um lead no banco.
+236:     """
+237:     texto = _limpar_markdown_whatsapp(texto)
+238:     chat_id = _resolver_chatid_waha(numero, session=session, api_url=api_url, api_key=api_key)
+239:     if not chat_id:
+240:         raise ValueError(f"Número inválido para envio: {numero}")
+241:     return enviar_texto_waha(chat_id, texto, session=session, api_url=api_url, api_key=api_key)
+242: 
+243: 
+244: def disparar_campanha(db, mensagem_template=None, intervalo=13, limite=None, leads=None):
+245:     """Envia mensagens para os leads celulares pendentes.
+246: 
+247:     - db: instância de LeadDatabase
+248:     - mensagem_template: texto com {nome}, {bairro}, {cidade} (usa MENSAGEM_PADRAO se None)
+249:     - intervalo: pausa fixa em segundos entre envios (usado se não houver cadência)
+250:     - leads: DataFrame opcional já filtrado; se None, busca pendentes (com limite)
+251:     """
+252:     mensagem_template = mensagem_template or MENSAGEM_PADRAO
+253:     if leads is None:
+254:         leads = db.get_leads_para_envio(limite)
+255: 
+256:     if leads.empty:
+257:         print("Nenhum lead celular pendente de envio.")
+258:         return
+259: 
+260:     total = len(leads)
+261: 
+262:     # Cadência aleatória (ex.: 3 a cada 60s) tem prioridade sobre o intervalo fixo.
+263:     cadencia = _parse_cadencia(WAHA_CADENCIA)
+264:     if cadencia:
+265:         envios_janela, janela = cadencia
+266:         pausas = _pausas_cadencia(total, envios_janela, janela)
+267:         print(f"Enviando para {total} lead(s), cadência {envios_janela} a cada {janela}s "
+268:               f"(intervalos aleatórios)...")
+269:     else:
+270:         pausas = [intervalo] * max(0, total - 1)
+271:         print(f"Enviando para {total} lead(s), com intervalo fixo de {intervalo}s...")
+272: 
+273:     for i, (_, lead) in enumerate(leads.iterrows(), 1):
+274:         texto = _renderizar_mensagem(mensagem_template, lead)
+275:         lead_id = lead.get("lead_id")
+276:         telefone = lead.get("telefone")
+277:         nome = lead.get("nome")
+278:         cidade = lead.get("cidade")
+279: 
+280:         chat_id = lead.get("chat_id_waha")
+281:         if not chat_id:
+282:             # Resolve (e cacheia) o chatId uma única vez por lead. Números novos
+283:             # usam @lid; a consulta ao checkNumberStatus é feita só na primeira vez.
+284:             chat_id = _resolver_chatid_waha(telefone)
+285:             if chat_id:
+286:                 db.salvar_chat_id_waha(nome, cidade, chat_id)
+287: 
+288:         if not chat_id:
+289:             db.marcar_envio(nome, cidade, "falhou")
+290:             db.salvar_log_envio(
+291:                 lead_id, nome, cidade, telefone, chat_id, "falhou",
+292:                 mensagem=texto, erro="telefone inválido",
+293:             )
+294:             print(f"[{i}/{total}] {nome} - telefone inválido, marcado como falhou.")
+295:             continue
+296: 
+297:         try:
+298:             resposta = enviar_texto_waha(chat_id, texto)
+299:             db.marcar_envio(nome, cidade, "enviado")
+300:             db.salvar_log_envio(
+301:                 lead_id, nome, cidade, telefone, chat_id, "enviado",
+302:                 mensagem=texto, payload=resposta,
+303:             )
+304:             print(f"[{i}/{total}] ENVIADO -> {nome} ({chat_id})")
+305:         except Exception as e:
+306:             payload_erro = None
+307:             if getattr(e, "response", None) is not None:
+308:                 try:
+309:                     payload_erro = e.response.text
+310:                 except Exception:
+311:                     payload_erro = None
+312:             erro = f"{type(e).__name__}: {e}"
+313:             db.marcar_envio(nome, cidade, "falhou")
+314:             db.salvar_log_envio(
+315:                 lead_id, nome, cidade, telefone, chat_id, "falhou",
+316:                 mensagem=texto, payload=payload_erro, erro=erro,
+317:             )
+318:             print(f"[{i}/{total}] FALHOU -> {nome} ({chat_id}): {erro}")
+319: 
+320:         if i < total:
+321:             time.sleep(pausas[i - 1])
+322: 
+323:     print("Campanha finalizada.")
+````
 
 ## File: .gitignore
-`````
+````
  1: # Dados: o banco DuckDB É versionado (data/leads.duckdb).
  2: # Apenas artefatos transientes do DuckDB e saídas geradas ficam de fora.
  3: *.duckdb.wal
@@ -3025,10 +3351,10 @@ requirements.txt
 29: # Sistema Operacional
 30: .DS_Store
 31: Thumbs.db
-`````
+````
 
 ## File: README.md
-`````markdown
+````markdown
   1: Documentação do Projeto: MAP SCRAPER
   2: 
   3: 1. Objetivo do Projeto
@@ -3134,234 +3460,261 @@ requirements.txt
 103: 
 104:     Passo 4: Resultados
 105: 
-106:         O banco de dados será atualizado em data/leads.duckdb.
+106:         O banco de dados será atualizado (PostgreSQL ou DuckDB, conforme o .env).
 107: 
 108:         Um arquivo Excel será gerado em output/leads_nicho_cidade.xlsx.
 109: 
-110: 
-111: 6. Gerenciamento do Banco de Dados (Regras de Negócio)
-112: 
-113:     Se você quiser descartar um lead para que ele não seja mais exportado e não seja atualizado nas próximas buscas, você pode rodar um comando SQL direto no DuckDB (via DBeaver ou script Python):
-114: 
-115:     sql
-116:     -- Para descartar um lead
-117:     UPDATE leads SET status = 'descartado' WHERE nome = 'Nome da Barbearia';
-118: 
-119:     -- Para reativar um lead
-120:     UPDATE leads SET status = 'ativo' WHERE nome = 'Nome da Barbearia';
-121:     Nota: A regra do UPSERT no database.py garante que, se o robô achar uma barbearia "descartada", ele pula ela e não sobrescreve seus dados no banco.
-122: 
-123: 7. Envio de WhatsApp (WAHA)
-124: 
-125:     Pré-requisito: uma instância WAHA rodando com um número conectado via QR Code.
+110:     Execução em Docker (servidor, sem menu)
+111: 
+112:     Para rodar sozinho num servidor (coleta automática contínua), o projeto tem
+113:     um Dockerfile e um docker-compose.yml. O container usa o runner
+114:     `src/coleta_auto.py` (não-interativo), configurado por variáveis de ambiente:
+115: 
+116:     ```
+117:     NICHO=barbearias          # nicho a coletar
+118:     UFS=                      # vazio = todas as UFs do Brasil; ou RS,SP,RJ
+119:     MAX_CIDADES=0             # 0 = todas as cidades de cada UF
+120:     MAX_BAIRROS=30            # bairros por cidade
+121:     AQUECER_BAIRROS=false     # resolver bairros antes da coleta
+122:     SINCRONIZAR=false         # baixar IBGE antes (banco novo)
+123:     LOOP=false                # true = rodar em loop contínuo
+124:     LOOP_PAUSA_SEGUNDOS=3600  # pausa entre ciclos (LOOP=true)
+125:     ```
 126: 
-127:     Configuração (arquivo .env na raiz do projeto):
-128:     Copie .env.example para .env e preencha os valores.
-129: 
-130:     ```
-131:     WAHA_API_URL=http://localhost:3000
-132:     WAHA_API_KEY=SUA_CHAVE_AQUI
-133:     WAHA_SESSION=default
-134:     WAHA_ATIVO=true
-135:     SOMENTE_ENVIO=false
-136:     WAHA_INTERVALO=13
-137:     WAHA_LIMITE=
-138:     ```
+127:     Subir e acompanhar:
+128: 
+129:     ```
+130:     docker compose up -d --build
+131:     docker compose logs -f app
+132:     ```
+133: 
+134:     O `.env` é injetado no container via `env_file` (banco e WAHA). Os volumes
+135:     `./data` e `./output` são montados para persistir DuckDB/Excel localmente.
+136: 
+137: 
+138: 6. Gerenciamento do Banco de Dados (Regras de Negócio)
 139: 
-140:     Flags de comportamento:
-141:     - WAHA_ATIVO: se false, desliga o envio de WhatsApp (não tenta enviar).
-142:     - SOMENTE_ENVIO: se true, pula a coleta e vai direto para o envio
-143:       (equivalente a rodar `python src/main.py --so-enviar`).
-144:     - WAHA_LIMITE: quantidade máxima de leads por campanha (vazio = sem limite).
+140:     Se você quiser descartar um lead para que ele não seja mais exportado e não seja atualizado nas próximas buscas, você pode rodar um comando SQL direto no DuckDB (via DBeaver ou script Python):
+141: 
+142:     sql
+143:     -- Para descartar um lead
+144:     UPDATE leads SET status = 'descartado' WHERE nome = 'Nome da Barbearia';
 145: 
-146:     Regras de envio (evita spam):
-147:     - Só envia para leads com status = 'ativo'.
-148:     - Só envia para tipo_telefone = 'Celular' (fixos são ignorados).
-149:     - Só envia para leads ainda não enviados (status_whatsapp = 'pendente' ou NULL).
-150:     - Intervalo de WAHA_INTERVALO segundos entre envios.
+146:     -- Para reativar um lead
+147:     UPDATE leads SET status = 'ativo' WHERE nome = 'Nome da Barbearia';
+148:     Nota: A regra do UPSERT no database.py garante que, se o robô achar uma barbearia "descartada", ele pula ela e não sobrescreve seus dados no banco.
+149: 
+150: 7. Envio de WhatsApp (WAHA)
 151: 
-152:     Logs no banco:
-153:     - status_whatsapp: 'pendente', 'enviado' ou 'falhou'.
-154:     - data_envio_whatsapp: gravada apenas quando o envio é bem-sucedido.
-155: 
-156:     A mensagem pode usar as variáveis {nome}, {bairro} e {cidade}.
-157: 
-158: 
-159: 8. Base de Localidades Offline (IBGE)
-160: 
-161:     O projeto mantém um cache local das localidades no próprio DuckDB, criado na
-162:     primeira consulta e reaproveitado nas seguintes (sem rede).
-163: 
-164:     Tabelas criadas automaticamente (guardam apenas o essencial):
-165:     - localidades_estados: uf, nome
-166:     - localidades_municipios: id_municipio, nome, uf + estado da coleta de bairros
-167:     - localidades_bairros: id_municipio, nome, id_distrito
-168: 
-169:     Fontes (API de Localidades do IBGE):
-170:     - Estados:    https://servicodados.ibge.gov.br/api/v1/localidades/estados
-171:     - Municípios: https://servicodados.ibge.gov.br/api/v1/localidades/municipios
-172:     - Distritos:  https://servicodados.ibge.gov.br/api/v1/localidades/distritos
-173: 
-174:     Configuração (.env):
-175:     ```
-176:     LOCALIDADES_USAR_CACHE=true
-177:     LOCALIDADES_SALVAR=true
-178:     LOCALIDADES_MIN_BAIRROS=3
-179:     AQUECER_PAUSA_SEGUNDOS=2
-180:     ```
-181: 
-182:     - LOCALIDADES_USAR_CACHE=true (padrão): consulta o banco primeiro e só chama a
-183:       API quando o dado ainda não existe (e aí grava o resultado).
-184:     - LOCALIDADES_USAR_CACHE=false: sempre busca na API do IBGE e atualiza a base
-185:       local com o que voltou.
-186:     - LOCALIDADES_SALVAR=false: modo somente leitura. Nada é gravado e nem as
-187:       tabelas são criadas; o banco só é consultado. A sincronização do menu fica
-188:       desativada.
-189:     - LOCALIDADES_MIN_BAIRROS: mínimo de distritos do IBGE para a cidade ser
-190:       considerada coberta. Abaixo disso, os bairros são complementados com o
-191:       OpenStreetMap (Nominatim + Overpass) e o resultado também fica em cache.
-192:     - AQUECER_PAUSA_SEGUNDOS: pausa entre cidades no aquecimento por UF, aplicada
-193:       somente quando a cidade usou o OpenStreetMap.
-194: 
-195:     As duas flags são independentes:
-196: 
-197:     | USAR_CACHE | SALVAR | Comportamento |
-198:     |---|---|---|
-199:     | true  | true  | lê do banco; grava o que faltar (recomendado) |
-200:     | false | true  | sempre vai à API e regrava tudo (força atualização) |
-201:     | true  | false | só lê o banco; o que não existe vai à API sem gravar |
-202:     | false | false | sempre à API, sem tocar no banco |
-203: 
-204:     O que acontece ao rodar de novo para a mesma cidade:
-205: 
-206:     - localidades_estados: UPSERT por uf (só atualiza o nome).
-207:     - localidades_municipios: UPSERT por id_municipio (atualiza nome/uf e
-208:       PRESERVA bairros_fonte / bairros_atualizado_em).
-209:     - localidades_bairros: a lista da cidade é tratada como autoritativa. Nomes
-210:       iguais são atualizados, nomes novos são inseridos e nomes que não vieram mais
-211:       são removidos — mas apenas daquela cidade.
-212:     - Sincronização completa (menu opção 3): aditiva. Ela insere/atualiza os
-213:       distritos do IBGE sem apagar bairros que já existem, então listas
-214:       complementadas pelo OpenStreetMap são preservadas.
-215: 
-216:     Rodar só para um estado também é seguro: obter_cidades(uf) grava apenas os
-217:     municípios daquela UF, e nada de outras UFs é alterado.
-218: 
-219:     Sincronização completa: menu opção 3 (ou `sincronizar_base_localidades()`), que
-220:     baixa de uma vez todos os estados, municípios e distritos (~10,7 mil registros).
+152:     Pré-requisito: uma instância WAHA rodando com um número conectado via QR Code.
+153: 
+154:     Configuração (arquivo .env na raiz do projeto):
+155:     Copie .env.example para .env e preencha os valores.
+156: 
+157:     ```
+158:     WAHA_API_URL=http://localhost:3000
+159:     WAHA_API_KEY=SUA_CHAVE_AQUI
+160:     WAHA_SESSION=default
+161:     WAHA_ATIVO=true
+162:     SOMENTE_ENVIO=false
+163:     WAHA_INTERVALO=13
+164:     WAHA_LIMITE=
+165:     ```
+166: 
+167:     Flags de comportamento:
+168:     - WAHA_ATIVO: se false, desliga o envio de WhatsApp (não tenta enviar).
+169:     - SOMENTE_ENVIO: se true, pula a coleta e vai direto para o envio
+170:       (equivalente a rodar `python src/main.py --so-enviar`).
+171:     - WAHA_LIMITE: quantidade máxima de leads por campanha (vazio = sem limite).
+172: 
+173:     Regras de envio (evita spam):
+174:     - Só envia para leads com status = 'ativo'.
+175:     - Só envia para tipo_telefone = 'Celular' (fixos são ignorados).
+176:     - Só envia para leads ainda não enviados (status_whatsapp = 'pendente' ou NULL).
+177:     - Intervalo de WAHA_INTERVALO segundos entre envios.
+178: 
+179:     Logs no banco:
+180:     - status_whatsapp: 'pendente', 'enviado' ou 'falhou'.
+181:     - data_envio_whatsapp: gravada apenas quando o envio é bem-sucedido.
+182: 
+183:     A mensagem pode usar as variáveis {nome}, {bairro} e {cidade}.
+184: 
+185: 
+186: 8. Base de Localidades Offline (IBGE)
+187: 
+188:     O projeto mantém um cache local das localidades no próprio DuckDB, criado na
+189:     primeira consulta e reaproveitado nas seguintes (sem rede).
+190: 
+191:     Tabelas criadas automaticamente (guardam apenas o essencial):
+192:     - localidades_estados: uf, nome
+193:     - localidades_municipios: id_municipio, nome, uf + estado da coleta de bairros
+194:     - localidades_bairros: id_municipio, nome, id_distrito
+195: 
+196:     Fontes (API de Localidades do IBGE):
+197:     - Estados:    https://servicodados.ibge.gov.br/api/v1/localidades/estados
+198:     - Municípios: https://servicodados.ibge.gov.br/api/v1/localidades/municipios
+199:     - Distritos:  https://servicodados.ibge.gov.br/api/v1/localidades/distritos
+200: 
+201:     Configuração (.env):
+202:     ```
+203:     LOCALIDADES_USAR_CACHE=true
+204:     LOCALIDADES_SALVAR=true
+205:     LOCALIDADES_MIN_BAIRROS=3
+206:     AQUECER_PAUSA_SEGUNDOS=2
+207:     ```
+208: 
+209:     - LOCALIDADES_USAR_CACHE=true (padrão): consulta o banco primeiro e só chama a
+210:       API quando o dado ainda não existe (e aí grava o resultado).
+211:     - LOCALIDADES_USAR_CACHE=false: sempre busca na API do IBGE e atualiza a base
+212:       local com o que voltou.
+213:     - LOCALIDADES_SALVAR=false: modo somente leitura. Nada é gravado e nem as
+214:       tabelas são criadas; o banco só é consultado. A sincronização do menu fica
+215:       desativada.
+216:     - LOCALIDADES_MIN_BAIRROS: mínimo de distritos do IBGE para a cidade ser
+217:       considerada coberta. Abaixo disso, os bairros são complementados com o
+218:       OpenStreetMap (Nominatim + Overpass) e o resultado também fica em cache.
+219:     - AQUECER_PAUSA_SEGUNDOS: pausa entre cidades no aquecimento por UF, aplicada
+220:       somente quando a cidade usou o OpenStreetMap.
 221: 
-222:     Aquecimento por UF: menu opção 4 (ou `aquecer_bairros_uf('RS')`). Resolve e
-223:     grava os bairros de TODAS as cidades de um estado, sem raspar nenhum lead.
-224:     Depois disso, a coleta por cidade não consulta mais IBGE/OSM.
-225: 
-226:     - Processa apenas as cidades com `bairros_fonte IS NULL` (ou seja, retoma de
-227:       onde parou em execuções anteriores).
-228:     - Cidades cobertas pelo IBGE são instantâneas; as demais usam o OpenStreetMap.
-229:     - A pausa entre cidades (AQUECER_PAUSA_SEGUNDOS) é aplicada somente quando o
-230:       OSM foi consultado — respeitando o limite de 1 req/s do Nominatim.
-231:     - Ctrl+C interrompe sem perder o que já foi gravado; basta rodar de novo.
-232:     - É possível limitar quantas cidades processar por execução.
-233: 
-234:     Importante: os "distritos" do IBGE são divisões administrativas e, em muitos
-235:     municípios, resumem-se à própria sede. Por isso o fallback com o OSM continua
-236:     existindo — a diferença é que ele roda uma única vez por cidade e o resultado
-237:     é gravado no banco. Se o OSM estiver fora do ar, nada é gravado (a próxima
-238:     execução tenta de novo) e a coleta segue com os distritos do IBGE.
-239: 
-240:     A API de Localidades do IBGE NÃO fornece bairros — apenas distritos e
-241:     subdistritos. Exemplo real: Canoas-RS tem 1 distrito (a própria sede) e 0
-242:     subdistritos, então o IBGE não contribui com áreas para essa cidade e o robô
-243:     informa isso e segue para o OpenStreetMap:
-244: 
-245:     ```
-246:     IBGE não publica bairros para Canoas-RS: o município tem apenas 1 distrito (a sede).
-247:     Buscando bairros no OpenStreetMap...
-248:     ```
-249: 
-250:     Cidades com vários distritos (São Paulo: 96, Campinas: 7) usam o IBGE e não
-251:     consultam o OSM. Das 5.571 cidades do país, 643 têm distritos suficientes.
+222:     As duas flags são independentes:
+223: 
+224:     | USAR_CACHE | SALVAR | Comportamento |
+225:     |---|---|---|
+226:     | true  | true  | lê do banco; grava o que faltar (recomendado) |
+227:     | false | true  | sempre vai à API e regrava tudo (força atualização) |
+228:     | true  | false | só lê o banco; o que não existe vai à API sem gravar |
+229:     | false | false | sempre à API, sem tocar no banco |
+230: 
+231:     O que acontece ao rodar de novo para a mesma cidade:
+232: 
+233:     - localidades_estados: UPSERT por uf (só atualiza o nome).
+234:     - localidades_municipios: UPSERT por id_municipio (atualiza nome/uf e
+235:       PRESERVA bairros_fonte / bairros_atualizado_em).
+236:     - localidades_bairros: a lista da cidade é tratada como autoritativa. Nomes
+237:       iguais são atualizados, nomes novos são inseridos e nomes que não vieram mais
+238:       são removidos — mas apenas daquela cidade.
+239:     - Sincronização completa (menu opção 3): aditiva. Ela insere/atualiza os
+240:       distritos do IBGE sem apagar bairros que já existem, então listas
+241:       complementadas pelo OpenStreetMap são preservadas.
+242: 
+243:     Rodar só para um estado também é seguro: obter_cidades(uf) grava apenas os
+244:     municípios daquela UF, e nada de outras UFs é alterado.
+245: 
+246:     Sincronização completa: menu opção 3 (ou `sincronizar_base_localidades()`), que
+247:     baixa de uma vez todos os estados, municípios e distritos (~10,7 mil registros).
+248: 
+249:     Aquecimento por UF: menu opção 4 (ou `aquecer_bairros_uf('RS')`). Resolve e
+250:     grava os bairros de TODAS as cidades de um estado, sem raspar nenhum lead.
+251:     Depois disso, a coleta por cidade não consulta mais IBGE/OSM.
 252: 
-253:     Como a cidade é resolvida: o nome digitado é comparado sem acento e sem
-254:     diferenciar maiúsculas ("canoas", "sao leopoldo") com a lista do IBGE, e o nome
-255:     oficial é exibido e usado no scraping, no banco e no Excel:
-256: 
-257:     ```
-258:     Digite o nome da cidade: canoas
-259:     Município (IBGE): Canoas-RS | código 4304606
-260:     ```
-261: 
-262:     Para forçar a atualização de uma cidade já gravada, limpe a marca:
-263:     ```sql
-264:     UPDATE localidades_municipios SET bairros_fonte = NULL WHERE nome = 'Porto Alegre';
-265:     ```
+253:     - Processa apenas as cidades com `bairros_fonte IS NULL` (ou seja, retoma de
+254:       onde parou em execuções anteriores).
+255:     - Cidades cobertas pelo IBGE são instantâneas; as demais usam o OpenStreetMap.
+256:     - A pausa entre cidades (AQUECER_PAUSA_SEGUNDOS) é aplicada somente quando o
+257:       OSM foi consultado — respeitando o limite de 1 req/s do Nominatim.
+258:     - Ctrl+C interrompe sem perder o que já foi gravado; basta rodar de novo.
+259:     - É possível limitar quantas cidades processar por execução.
+260: 
+261:     Importante: os "distritos" do IBGE são divisões administrativas e, em muitos
+262:     municípios, resumem-se à própria sede. Por isso o fallback com o OSM continua
+263:     existindo — a diferença é que ele roda uma única vez por cidade e o resultado
+264:     é gravado no banco. Se o OSM estiver fora do ar, nada é gravado (a próxima
+265:     execução tenta de novo) e a coleta segue com os distritos do IBGE.
 266: 
-267: 9. Anti-bloqueio / Captcha (Google Maps)
-268: 
-269:     Quando o Google responde com a tela de "tráfego incomum" (captcha), o robô:
-270:     1. detecta o bloqueio (URL /sorry/, formulários de captcha ou textos típicos);
-271:     2. aplica um cooldown global, pausando TODAS as threads ao mesmo tempo;
-272:     3. espera a pausa longa e tenta novamente até CAPTCHA_MAX_TENTATIVAS;
-273:     4. se o bloqueio persistir, aborta apenas aquela área, preservando os leads
-274:        já extraídos (que continuam sendo salvos incrementalmente).
-275: 
-276:     Configuração (.env):
-277:     ```
-278:     CAPTCHA_MAX_TENTATIVAS=2
-279:     CAPTCHA_PAUSA_SEGUNDOS=300
-280:     CAPTCHA_PAUSA_GLOBAL_SEGUNDOS=180
-281:     ```
-282: 
-283:     - CAPTCHA_MAX_TENTATIVAS: tentativas por página antes de abortar a área.
-284:     - CAPTCHA_PAUSA_SEGUNDOS: pausa longa da thread que levou o bloqueio.
-285:     - CAPTCHA_PAUSA_GLOBAL_SEGUNDOS: pausa compartilhada entre as threads.
-286: 
-287:     A resolução automática de captcha por serviço externo (2Captcha, CapMonster
-288:     etc.) não está implementada — o comportamento padrão é pausar e desistir da
-289:     área em vez de insistir. Em coletas muito grandes, aumente as pausas acima.
-290: 
-291: 10. commit forçado
-292: 
-293:     git add -A; git commit -m "sync local $(Get-Date -Format 'yyyy-MM-dd HH:mm')"; git push --force-with-lease origin main
-294: 
-295: 11. Próximos Passos (Melhorias Futuras)
-296: 
-297:     Já implementado:
-298:     - Base de localidades offline no DuckDB (estados, municípios e distritos do IBGE).
-299:     - Detecção de captcha com pausa longa e cooldown compartilhado entre threads.
-300: 
-301:     Pendências sugeridas:
-302:     - Resolução automática de captcha: integrar um serviço (2Captcha/CapMonster) para
-303:       coletas muito grandes, hoje o robô apenas pausa e desiste da área.
-304: 
-305:     - Enriquecimento de E-mail: Criar um script secundário que lê os sites encontrados e busca e-mails de contato (usando Regex).
-306: 
-307: 
-308: 12. Memória do Projeto para IA (pasta memory/)
+267:     A API de Localidades do IBGE NÃO fornece bairros — apenas distritos e
+268:     subdistritos. Exemplo real: Canoas-RS tem 1 distrito (a própria sede) e 0
+269:     subdistritos, então o IBGE não contribui com áreas para essa cidade e o robô
+270:     informa isso e segue para o OpenStreetMap:
+271: 
+272:     ```
+273:     IBGE não publica bairros para Canoas-RS: o município tem apenas 1 distrito (a sede).
+274:     Buscando bairros no OpenStreetMap...
+275:     ```
+276: 
+277:     Cidades com vários distritos (São Paulo: 96, Campinas: 7) usam o IBGE e não
+278:     consultam o OSM. Das 5.571 cidades do país, 643 têm distritos suficientes.
+279: 
+280:     Como a cidade é resolvida: o nome digitado é comparado sem acento e sem
+281:     diferenciar maiúsculas ("canoas", "sao leopoldo") com a lista do IBGE, e o nome
+282:     oficial é exibido e usado no scraping, no banco e no Excel:
+283: 
+284:     ```
+285:     Digite o nome da cidade: canoas
+286:     Município (IBGE): Canoas-RS | código 4304606
+287:     ```
+288: 
+289:     Para forçar a atualização de uma cidade já gravada, limpe a marca:
+290:     ```sql
+291:     UPDATE localidades_municipios SET bairros_fonte = NULL WHERE nome = 'Porto Alegre';
+292:     ```
+293: 
+294: 9. Anti-bloqueio / Captcha (Google Maps)
+295: 
+296:     Quando o Google responde com a tela de "tráfego incomum" (captcha), o robô:
+297:     1. detecta o bloqueio (URL /sorry/, formulários de captcha ou textos típicos);
+298:     2. aplica um cooldown global, pausando TODAS as threads ao mesmo tempo;
+299:     3. espera a pausa longa e tenta novamente até CAPTCHA_MAX_TENTATIVAS;
+300:     4. se o bloqueio persistir, aborta apenas aquela área, preservando os leads
+301:        já extraídos (que continuam sendo salvos incrementalmente).
+302: 
+303:     Configuração (.env):
+304:     ```
+305:     CAPTCHA_MAX_TENTATIVAS=2
+306:     CAPTCHA_PAUSA_SEGUNDOS=300
+307:     CAPTCHA_PAUSA_GLOBAL_SEGUNDOS=180
+308:     ```
 309: 
-310:     A pasta `memory/` reúne documentação resumida e densa, pensada para ser lida
-311:     por modelos de IA antes de alterar o código (economiza contexto/custo).
-312: 
-313:     Ordem de leitura:
-314:     1. memory/00-resumo-projeto.md        -> objetivo, stack e estrutura
-315:     2. memory/01-arquitetura-e-modulos.md -> módulos, funções e fluxos
-316:     3. memory/02-decisoes-e-armadilhas.md -> decisões, bugs conhecidos, cuidados
-317:     4. memory/03-historico-de-mudancas.md -> o que mudou e o que ficou pendente
-318:     5. memory/04-como-contribuir.md       -> padrões de código, logs, testes e docs
+310:     - CAPTCHA_MAX_TENTATIVAS: tentativas por página antes de abortar a área.
+311:     - CAPTCHA_PAUSA_SEGUNDOS: pausa longa da thread que levou o bloqueio.
+312:     - CAPTCHA_PAUSA_GLOBAL_SEGUNDOS: pausa compartilhada entre as threads.
+313: 
+314:     A resolução automática de captcha por serviço externo (2Captcha, CapMonster
+315:     etc.) não está implementada — o comportamento padrão é pausar e desistir da
+316:     área em vez de insistir. Em coletas muito grandes, aumente as pausas acima.
+317: 
+318: 10. commit forçado
 319: 
-320:     Regras: manter os arquivos curtos, registrar o "porquê" das decisões e nunca
-321:     colocar segredos ali (API keys ficam apenas no `.env`).
-322: 
+320:     git add -A; git commit -m "sync local $(Get-Date -Format 'yyyy-MM-dd HH:mm')"; git push --force-with-lease origin main
+321: 
+322: 11. Próximos Passos (Melhorias Futuras)
 323: 
-324: 13. Observação sobre configuração
-325: 
-326:     O modelo completo e comentado de todas as variáveis está em `.env.example`.
-327:     Cada item traz a faixa de valores e o efeito colateral. Comentários devem
-328:     ficar em linha própria; comentário na mesma linha do valor é lido como parte
-329:     do valor.
-`````
+324:     Já implementado:
+325:     - Base de localidades offline no DuckDB (estados, municípios e distritos do IBGE).
+326:     - Detecção de captcha com pausa longa e cooldown compartilhado entre threads.
+327: 
+328:     Pendências sugeridas:
+329:     - Resolução automática de captcha: integrar um serviço (2Captcha/CapMonster) para
+330:       coletas muito grandes, hoje o robô apenas pausa e desiste da área.
+331: 
+332:     - Enriquecimento de E-mail: Criar um script secundário que lê os sites encontrados e busca e-mails de contato (usando Regex).
+333: 
+334: 
+335: 12. Memória do Projeto para IA (pasta memory/)
+336: 
+337:     A pasta `memory/` reúne documentação resumida e densa, pensada para ser lida
+338:     por modelos de IA antes de alterar o código (economiza contexto/custo).
+339: 
+340:     Ordem de leitura:
+341:     1. memory/00-resumo-projeto.md        -> objetivo, stack e estrutura
+342:     2. memory/01-arquitetura-e-modulos.md -> módulos, funções e fluxos
+343:     3. memory/02-decisoes-e-armadilhas.md -> decisões, bugs conhecidos, cuidados
+344:     4. memory/03-historico-de-mudancas.md -> o que mudou e o que ficou pendente
+345:     5. memory/04-como-contribuir.md       -> padrões de código, logs, testes e docs
+346: 
+347:     Regras: manter os arquivos curtos, registrar o "porquê" das decisões e nunca
+348:     colocar segredos ali (API keys ficam apenas no `.env`).
+349: 
+350: 
+351: 13. Observação sobre configuração
+352: 
+353:     O modelo completo e comentado de todas as variáveis está em `.env.example`.
+354:     Cada item traz a faixa de valores e o efeito colateral. Comentários devem
+355:     ficar em linha própria; comentário na mesma linha do valor é lido como parte
+356:     do valor.
+````
 
 ## File: src/main.py
-`````python
+````python
   1: # src/main.py
   2: import sys
   3: import os
@@ -3560,2691 +3913,1747 @@ requirements.txt
 196: 
 197:     numero_f, cidade_f, nicho_f = _escolher_filtros()
 198: 
-199:     pendentes = db.get_leads_para_envio(
-200:         limite=WAHA_LIMITE, numero=numero_f, cidade=cidade_f, nicho=nicho_f
-201:     )
-202: 
-203:     if _confirmar("Deseja fazer um envio de teste antes? (S/N): "):
-204:         testar_envio(db, mensagem, pendentes=pendentes)
-205: 
-206:     if pendentes.empty:
-207:         print("Nenhum lead celular pendente de envio (com os filtros aplicados).")
-208:         db.close()
-209:         return
-210: 
-211:     print(f"\n{len(pendentes)} lead(s) celular(es) pendentes (fixos são ignorados).")
-212:     if WAHA_LIMITE:
-213:         print(f"Limite configurado: {WAHA_LIMITE} lead(s) por campanha.")
-214: 
-215:     if not _confirmar(f"Enviar para {len(pendentes)} lead(s)? (S/N): "):
-216:         print("Envio cancelado.")
-217:         db.close()
-218:         return
+199:     # Busca todos os pendentes (sem limitar ainda) para mostrar o total disponível.
+200:     pendentes = db.get_leads_para_envio(numero=numero_f, cidade=cidade_f, nicho=nicho_f)
+201: 
+202:     if _confirmar("Deseja fazer um envio de teste antes? (S/N): "):
+203:         testar_envio(db, mensagem, pendentes=pendentes)
+204: 
+205:     if pendentes.empty:
+206:         print("Nenhum lead celular pendente de envio (com os filtros aplicados).")
+207:         db.close()
+208:         return
+209: 
+210:     total_disponivel = len(pendentes)
+211:     print(f"\n{total_disponivel} lead(s) celular(es) pendentes (fixos são ignorados).")
+212: 
+213:     # Quantidade (range): Enter = todos (respeitando o limite do .env, se houver).
+214:     if WAHA_LIMITE:
+215:         print(f"Limite configurado no .env: {WAHA_LIMITE} lead(s) por campanha.")
+216:         padrao = WAHA_LIMITE
+217:     else:
+218:         padrao = total_disponivel
 219: 
-220:     disparar_campanha(
-221:         db,
-222:         mensagem_template=mensagem,
-223:         intervalo=WAHA_INTERVALO,
-224:         limite=WAHA_LIMITE,
-225:         leads=pendentes,
-226:     )
-227:     db.close()
-228: 
-229: 
-230: def aquecer_bairros_menu():
-231:     """Prepara o cache de bairros de uma UF inteira (sem raspar leads)."""
-232:     print("\n=== AQUECER BAIRROS DE UMA UF ===")
-233: 
-234:     if not LOCALIDADES_SALVAR:
-235:         print("LOCALIDADES_SALVAR=false: o aquecimento está desativado.")
-236:         print("Ative a flag LOCALIDADES_SALVAR no .env para gravar os bairros.")
-237:         return
-238: 
-239:     print("Resolve e grava os bairros de todas as cidades da UF, uma única vez.")
-240:     print("Depois disso a coleta por cidade não consulta mais IBGE/OSM.")
-241: 
-242:     df_estados = obter_estados()
-243:     if df_estados.empty:
-244:         print("Não foi possível obter a lista de estados.")
-245:         return
-246: 
-247:     uf = input("Digite a UF (ex: RS, SP, RJ): ").strip().upper()
-248:     if uf not in df_estados['uf'].values:
-249:         print("UF inválida.")
-250:         return
-251: 
-252:     print(f"\nVerificando quais cidades de {uf} ainda precisam de bairros...")
-253:     pendentes = listar_municipios_pendentes(uf)
-254:     if not pendentes:
-255:         print(f"Todas as cidades de {uf} já estão na base local. Nada a fazer.")
-256:         return
-257: 
-258:     print(f"{len(pendentes)} cidade(s) pendente(s) em {uf}.")
-259:     print("As cidades cobertas pelo IBGE são instantâneas; as demais usam o")
-260:     print("OpenStreetMap (Nominatim + Overpass), com pausa entre elas.")
-261: 
-262:     limite = input("Quantas cidades processar agora? (Enter = todas): ").strip()
-263:     max_cidades = 0
-264:     if limite:
-265:         try:
-266:             max_cidades = max(1, int(limite))
-267:         except ValueError:
-268:             print("Valor inválido. Usando todas.")
-269:             max_cidades = 0
-270: 
-271:     previstas = min(max_cidades, len(pendentes)) if max_cidades else len(pendentes)
-272:     confirmar = input(f"Processar {previstas} cidade(s)? (S/N): ").strip().upper()
-273:     if confirmar != 'S':
-274:         print("Operação cancelada.")
+220:     entrada = input(
+221:         f"Quantos leads enviar? (Enter = {padrao}): "
+222:     ).strip()
+223: 
+224:     if entrada:
+225:         if entrada.isdigit() and int(entrada) > 0:
+226:             quantidade = int(entrada)
+227:         else:
+228:             print("Valor inválido. Usando o padrão.")
+229:             quantidade = padrao
+230:     else:
+231:         quantidade = padrao
+232: 
+233:     if WAHA_LIMITE and quantidade > WAHA_LIMITE:
+234:         print(f"Ajustando para o limite do .env ({WAHA_LIMITE}).")
+235:         quantidade = WAHA_LIMITE
+236: 
+237:     quantidade = min(quantidade, total_disponivel)
+238:     pendentes = pendentes.head(quantidade)
+239: 
+240:     if not _confirmar(f"Enviar para {len(pendentes)} lead(s)? (S/N): "):
+241:         print("Envio cancelado.")
+242:         db.close()
+243:         return
+244: 
+245:     disparar_campanha(
+246:         db,
+247:         mensagem_template=mensagem,
+248:         intervalo=WAHA_INTERVALO,
+249:         limite=quantidade,
+250:         leads=pendentes,
+251:     )
+252:     db.close()
+253: 
+254: 
+255: def aquecer_bairros_menu():
+256:     """Prepara o cache de bairros de uma UF inteira (sem raspar leads)."""
+257:     print("\n=== AQUECER BAIRROS DE UMA UF ===")
+258: 
+259:     if not LOCALIDADES_SALVAR:
+260:         print("LOCALIDADES_SALVAR=false: o aquecimento está desativado.")
+261:         print("Ative a flag LOCALIDADES_SALVAR no .env para gravar os bairros.")
+262:         return
+263: 
+264:     print("Resolve e grava os bairros de todas as cidades da UF, uma única vez.")
+265:     print("Depois disso a coleta por cidade não consulta mais IBGE/OSM.")
+266: 
+267:     df_estados = obter_estados()
+268:     if df_estados.empty:
+269:         print("Não foi possível obter a lista de estados.")
+270:         return
+271: 
+272:     uf = input("Digite a UF (ex: RS, SP, RJ): ").strip().upper()
+273:     if uf not in df_estados['uf'].values:
+274:         print("UF inválida.")
 275:         return
 276: 
-277:     aquecer_bairros_uf(uf, cidades=pendentes, max_cidades=max_cidades)
-278: 
-279: 
-280: def menu_interativo():
-281:     # Flag de linha de comando: `python src/main.py --so-enviar` pula a coleta
-282:     # e vai direto para o envio (equivale a SOMENTE_ENVIO=true no .env).
-283:     so_enviar_cli = "--so-enviar" in sys.argv
-284: 
-285:     if SOMENTE_ENVIO or so_enviar_cli:
-286:         enviar_whatsapp_menu()
-287:         return
-288: 
-289:     while True:
-290:         print("\n=== MAP SCRAPER ===")
-291:         print("1 - Coletar leads")
-292:         print("2 - Enviar mensagens WhatsApp")
-293:         print("3 - Sincronizar base de localidades (IBGE)")
-294:         print("4 - Aquecer bairros de uma UF (OpenStreetMap)")
-295:         print("5 - Sair")
-296:         opcao = input("Escolha uma opção: ").strip()
-297: 
-298:         if opcao == "1":
-299:             coletar_leads()
-300:         elif opcao == "2":
-301:             enviar_whatsapp_menu()
-302:         elif opcao == "3":
-303:             sincronizar_base_localidades()
-304:         elif opcao == "4":
-305:             aquecer_bairros_menu()
-306:         elif opcao == "5":
-307:             print("Até mais!")
-308:             break
-309:         else:
-310:             print("Opção inválida.")
-311: 
-312: 
-313: if __name__ == "__main__":
-314:     menu_interativo()
-`````
+277:     print(f"\nVerificando quais cidades de {uf} ainda precisam de bairros...")
+278:     pendentes = listar_municipios_pendentes(uf)
+279:     if not pendentes:
+280:         print(f"Todas as cidades de {uf} já estão na base local. Nada a fazer.")
+281:         return
+282: 
+283:     print(f"{len(pendentes)} cidade(s) pendente(s) em {uf}.")
+284:     print("As cidades cobertas pelo IBGE são instantâneas; as demais usam o")
+285:     print("OpenStreetMap (Nominatim + Overpass), com pausa entre elas.")
+286: 
+287:     limite = input("Quantas cidades processar agora? (Enter = todas): ").strip()
+288:     max_cidades = 0
+289:     if limite:
+290:         try:
+291:             max_cidades = max(1, int(limite))
+292:         except ValueError:
+293:             print("Valor inválido. Usando todas.")
+294:             max_cidades = 0
+295: 
+296:     previstas = min(max_cidades, len(pendentes)) if max_cidades else len(pendentes)
+297:     confirmar = input(f"Processar {previstas} cidade(s)? (S/N): ").strip().upper()
+298:     if confirmar != 'S':
+299:         print("Operação cancelada.")
+300:         return
+301: 
+302:     aquecer_bairros_uf(uf, cidades=pendentes, max_cidades=max_cidades)
+303: 
+304: 
+305: def menu_interativo():
+306:     # Flag de linha de comando: `python src/main.py --so-enviar` pula a coleta
+307:     # e vai direto para o envio (equivale a SOMENTE_ENVIO=true no .env).
+308:     so_enviar_cli = "--so-enviar" in sys.argv
+309: 
+310:     if SOMENTE_ENVIO or so_enviar_cli:
+311:         enviar_whatsapp_menu()
+312:         return
+313: 
+314:     while True:
+315:         print("\n=== MAP SCRAPER ===")
+316:         print("1 - Coletar leads")
+317:         print("2 - Enviar mensagens WhatsApp")
+318:         print("3 - Sincronizar base de localidades (IBGE)")
+319:         print("4 - Aquecer bairros de uma UF (OpenStreetMap)")
+320:         print("5 - Sair")
+321:         opcao = input("Escolha uma opção: ").strip()
+322: 
+323:         if opcao == "1":
+324:             coletar_leads()
+325:         elif opcao == "2":
+326:             enviar_whatsapp_menu()
+327:         elif opcao == "3":
+328:             sincronizar_base_localidades()
+329:         elif opcao == "4":
+330:             aquecer_bairros_menu()
+331:         elif opcao == "5":
+332:             print("Até mais!")
+333:             break
+334:         else:
+335:             print("Opção inválida.")
+336: 
+337: 
+338: if __name__ == "__main__":
+339:     menu_interativo()
+````
 
 
 # Git Diffs
 ## Git Diffs Working Tree
-`````diff
+````diff
+diff --git a/.env.example b/.env.example
+index 9c2506d..f1bccf6 100644
+--- a/.env.example
++++ b/.env.example
+@@ -14,6 +14,38 @@
+ # =============================================================================
+ 
+ 
++# =============================================================================
++# BANCO DE DADOS — engine independente (PostgreSQL ou DuckDB)
++# =============================================================================
++
++# Qual banco usar?
++#   duckdb    = banco local (arquivo DUCKDB_PATH). Bom para rodar offline.
++#   postgres  = banco externo PostgreSQL (DATABASE_URL).
++# Se você DEIXAR ESTA LINHA COMENTADA, o sistema decide sozinho:
++#   - se DUCKDB_PATH estiver definido -> usa DuckDB
++#   - senão, se DATABASE_URL estiver definido -> usa PostgreSQL
++DB_ENGINE=postgres
++
++# ---- Opção 1: PostgreSQL (banco externo) ----------------------------------
++# URL de conexão: postgresql://usuario:senha@host:porta/banco
++# ATENÇÃO: se a senha tiver caracteres especiais (@, :, /), "percent-encode":
++#   @ -> %40
++DATABASE_URL=postgresql://usuario:senha@localhost:5432/leads_db
++
++# ---- Opção 2: DuckDB (banco local, para rodar offline) ---------------------
++# Para usar o DuckDB, comente/remova o DATABASE_URL acima e descomente a linha:
++#DUCKDB_PATH=data/leads.duckdb
++
++# ---- Configuração antiga (referência) --------------------------------------
++# As variáveis abaixo foram substituídas por DATABASE_URL. Funcionam se você
++# comentar/remover o DATABASE_URL E definir DB_ENGINE=postgres.
++#DB_HOST=localhost
++#DB_PORT=5432
++#DB_NAME=leads_db
++#DB_USER=leads_app
++#DB_PASSWORD=
++
++
+ # =============================================================================
+ # WHATSAPP - WAHA (WhatsApp HTTP API)
+ # =============================================================================
+@@ -43,9 +75,15 @@ WAHA_ATIVO=true
+ SOMENTE_ENVIO=false
+ 
+ # Pausa em SEGUNDOS entre um envio e o próximo (13s ≈ 4-5 mensagens por minuto).
+-# Pausas muito curtas aumentam o risco de banimento do número.
++# Usado APENAS quando WAHA_CADENCIA está vazio (pausa fixa).
+ WAHA_INTERVALO=13
+ 
++# Cadência de envio (anti-bloqueio): "X a cada Y segundos".
++# Ex.: WAHA_CADENCIA=3:60  -> 3 envios por minuto, com intervalos ALEATÓRIOS
++# (não manda de 15 em 15 segundos fixos). Tem prioridade sobre WAHA_INTERVALO.
++# Deixe vazio para usar a pausa fixa do WAHA_INTERVALO.
++WAHA_CADENCIA=
++
+ # Quantidade máxima de leads por campanha. Vazio = sem limite (envia todos
+ # os pendentes). Só conta leads celulares, ativos e ainda não enviados.
+ WAHA_LIMITE=
+@@ -108,3 +146,47 @@ CAPTCHA_PAUSA_SEGUNDOS=300
+ # Pausa compartilhada em SEGUNDOS aplicada a TODAS as threads assim que uma
+ # delas detecta bloqueio (evita que as outras continuem martelando o Google).
+ CAPTCHA_PAUSA_GLOBAL_SEGUNDOS=180
++
++
++# =============================================================================
++# COLETA AUTOMÁTICA (rodar em servidor/container, sem menu)
++# -----------------------------------------------------------------------------
++# Usadas pelo runner `python src/coleta_auto.py` (não-interativo). O Docker
++# Compose já injeta estas variáveis com valores padrão; sobrescreva aqui ou no
++# docker-compose.yml conforme necessário.
++# =============================================================================
++
++# Nicho a coletar no modo automático.
++NICHO=barbearias
++
++# UFs a coletar, separadas por vírgula. Vazio = TODAS as UFs do Brasil.
++# Exemplo: UFS=RS,SP,RJ
++UFS=
++
++# Quantidade máxima de cidades por UF. 0 = todas.
++MAX_CIDADES=0
++
++# Quantidade máxima de bairros usados por cidade na busca (0 não é válido).
++MAX_BAIRROS=30
++
++# Pré-resolver (aquecer) os bairros da UF inteira antes de coletar?
++#   true  = resolve e grava todos os bairros da UF antes (pode demorar).
++#   false = resolve os bairros de cada cidade na hora da coleta (padrão).
++AQUECER_BAIRROS=false
++
++# Baixar estados/municípios/distritos do IBGE antes de coletar?
++#   true  = útil em banco novo (DuckDB local). No PostgreSQL já populado, deixe
++#           false para não rebaixar tudo do IBGE.
++SINCRONIZAR=false
++
++# Mostrar o navegador (Chromium) durante a coleta. Em servidor use false.
++MOSTRAR_NAVEGADOR=false
++
++# Gerar Excel por cidade ao final de cada coleta (true/false).
++EXPORTAR_EXCEL=false
++
++# Rodar em loop contínuo (true) ou executar um único ciclo (false).
++LOOP=false
++
++# Pausa (segundos) entre ciclos quando LOOP=true.
++LOOP_PAUSA_SEGUNDOS=3600
+diff --git a/README.md b/README.md
+index 68a5769..2bf11cf 100644
+--- a/README.md
++++ b/README.md
+@@ -103,10 +103,37 @@ Documentação do Projeto: MAP SCRAPER
+ 
+     Passo 4: Resultados
+ 
+-        O banco de dados será atualizado em data/leads.duckdb.
++        O banco de dados será atualizado (PostgreSQL ou DuckDB, conforme o .env).
+ 
+         Um arquivo Excel será gerado em output/leads_nicho_cidade.xlsx.
+ 
++    Execução em Docker (servidor, sem menu)
++
++    Para rodar sozinho num servidor (coleta automática contínua), o projeto tem
++    um Dockerfile e um docker-compose.yml. O container usa o runner
++    `src/coleta_auto.py` (não-interativo), configurado por variáveis de ambiente:
++
++    ```
++    NICHO=barbearias          # nicho a coletar
++    UFS=                      # vazio = todas as UFs do Brasil; ou RS,SP,RJ
++    MAX_CIDADES=0             # 0 = todas as cidades de cada UF
++    MAX_BAIRROS=30            # bairros por cidade
++    AQUECER_BAIRROS=false     # resolver bairros antes da coleta
++    SINCRONIZAR=false         # baixar IBGE antes (banco novo)
++    LOOP=false                # true = rodar em loop contínuo
++    LOOP_PAUSA_SEGUNDOS=3600  # pausa entre ciclos (LOOP=true)
++    ```
++
++    Subir e acompanhar:
++
++    ```
++    docker compose up -d --build
++    docker compose logs -f app
++    ```
++
++    O `.env` é injetado no container via `env_file` (banco e WAHA). Os volumes
++    `./data` e `./output` são montados para persistir DuckDB/Excel localmente.
++
+ 
+ 6. Gerenciamento do Banco de Dados (Regras de Negócio)
+ 
 diff --git a/data/leads.duckdb b/data/leads.duckdb
-index 3f1852f..9579887 100644
+index 9afd0c3..a1b656b 100644
 Binary files a/data/leads.duckdb and b/data/leads.duckdb differ
-diff --git a/repomix-output.md b/repomix-output.md
-index ac7782a..22f3bbd 100644
---- a/repomix-output.md
-+++ b/repomix-output.md
-@@ -1,37 +1,44 @@
--Este arquivo é uma representação mesclada de todo o código-fonte, combinado em um único documento pelo Repomix.
--O conteúdo foi processado onde números de linha foram adicionados.
-+This file is a merged representation of the entire codebase, combined into a single document by Repomix.
-+The content has been processed where line numbers have been added.
- 
--# Resumo do Arquivo
-+# File Summary
- 
--## Propósito
--Este arquivo contém uma representação empacotada de todo o conteúdo do repositório. Ele foi projetado para ser facilmente consumível por sistemas de IA para análise, revisão de código ou outros processos automatizados.
-+## Purpose
-+This file contains a packed representation of the entire repository's contents.
-+It is designed to be easily consumable by AI systems for analysis, code review,
-+or other automated processes.
- 
--## Formato do Arquivo
--O conteúdo está organizado da seguinte forma:
--1. Esta seção de resumo
--2. Informações do repositório
--3. Estrutura de diretórios
--4. Arquivos do repositório (se habilitado)
--5. Múltiplas entradas de arquivos, cada uma consistindo de:
--  a. Um cabeçalho com o caminho do arquivo (## File: path/to/file)
--  b. O conteúdo completo do arquivo em um bloco de código
-+## File Format
-+The content is organized as follows:
-+1. This summary section
-+2. Repository information
-+3. Directory structure
-+4. Repository files (if enabled)
-+5. Multiple file entries, each consisting of:
-+  a. A header with the file path (## File: path/to/file)
-+  b. The full contents of the file in a code block
- 
--## Diretrizes de Uso
--- Este arquivo deve ser tratado como somente leitura. Quaisquer alterações devem ser feitas nos arquivos originais do repositório, não nesta versão empacotada.
--- Ao processar este arquivo, use o caminho do arquivo para distinguir entre os diferentes arquivos no repositório.
--- Esteja ciente de que este arquivo pode conter informações confidenciais. Manuseie-o com o mesmo nível de segurança que você faria com o repositório original.
--- Preste atenção especial às Instruções do Repositório. Elas contêm contexto importante e diretrizes específicas para este projeto.
-+## Usage Guidelines
-+- This file should be treated as read-only. Any changes should be made to the
-+  original repository files, not this packed version.
-+- When processing this file, use the file path to distinguish
-+  between different files in the repository.
-+- Be aware that this file may contain sensitive information. Handle it with
-+  the same level of security as you would the original repository.
- 
--## Notas
--- Alguns arquivos podem ter sido excluídos com base nas regras do .gitignore e na configuração do Repomix.
--- Arquivos binários não estão incluídos nesta representação empacotada. Consulte a seção de Estrutura do Repositório para obter uma lista completa de caminhos de arquivos, incluindo arquivos binários.
--- Arquivos que correspondem a padrões no .gitignore são excluídos.
--- Arquivos que correspondem a padrões de ignore padrão são excluídos.
--- Números de linha foram adicionados ao início de cada linha.
--- Os arquivos são classificados por contagem de alterações do Git (arquivos com mais alterações estão na parte inferior).
--- Os diffs do Git da árvore de trabalho e das alterações preparadas estão incluídos.
-+- Pay special attention to the Repository Instruction. These contain important context and guidelines specific to this project.
- 
--# Estrutura de Diretórios
-+## Notes
-+- Some files may have been excluded based on .gitignore rules and Repomix's configuration
-+- Binary files are not included in this packed representation. Please refer to the Repository Structure section for a complete list of file paths, including binary files
-+- Files matching patterns in .gitignore are excluded
-+- Files matching default ignore patterns are excluded
-+- Line numbers have been added to the beginning of each line
-+- Files are sorted by Git change count (files with more changes are at the bottom)
-+- Git diffs from the worktree and staged changes are included
+diff --git a/memory/00-resumo-projeto.md b/memory/00-resumo-projeto.md
+index 8e4dbf2..63df724 100644
+--- a/memory/00-resumo-projeto.md
++++ b/memory/00-resumo-projeto.md
+@@ -1,14 +1,14 @@
+ # 00 — Resumo do Projeto
+ 
+-**Map Scraper** — ferramenta local de prospecção de leads B2B a partir do Google Maps.
++**Map Scraper** — ferramenta de prospecção de leads B2B a partir do Google Maps.
+ 
+ - **Entrada:** UF + cidade + nicho (ex.: `RS`, `Canoas`, `barbearias`).
+ - **Processo:** divide a busca por bairros, raspa o Google Maps com Playwright em
+   multithread e extrai nome, telefone, Instagram e site.
+-- **Saída:** leads no DuckDB (`data/leads.duckdb`) + Excel em `output/`.
++- **Saída:** leads num banco (PostgreSQL **ou** DuckDB) + Excel em `output/`.
+ - **Extra:** dispara mensagens de WhatsApp via WAHA para leads já coletados, com
+-  templates reutilizáveis, filtros (número/cidade/nicho), teste de envio e cache
+-  do chatId resolvido (`@lid`/`@c.us`).
++  templates reutilizáveis, filtros (número/cidade/nicho), teste de envio, cache
++  do chatId resolvido (`@lid`/`@c.us`) e **cadência aleatória** anti-bloqueio.
+ 
+ ## Fluxo de alto nível
+ 
+@@ -19,7 +19,7 @@ menu (src/main.py)
+                   → database.LeadDatabase.save_leads (UPSERT incremental)
+                   → database.export_to_excel
+   └─ 2 WhatsApp   → template ativo → filtros → teste → database.get_leads_para_envio
+-                  → whatsapp.disparar_campanha (WAHA, chatId via checkNumberStatus)
++                  → whatsapp.disparar_campanha (WAHA, cadência aleatória)
+   └─ 3 Sincronizar localidades (IBGE) → locations.sincronizar_base_localidades
+   └─ 4 Aquecer bairros de uma UF       → locations.aquecer_bairros_uf
+   └─ 5 Sair
+@@ -31,7 +31,7 @@ menu (src/main.py)
+ |---|---|
+ | Linguagem | Python 3.10+ (ambiente: `venv/`) |
+ | Scraping | Playwright (Chromium) + ThreadPoolExecutor |
+-| Banco | DuckDB (arquivo único, 1 processo por vez) |
++| Banco | **PostgreSQL (externo) ou DuckDB (local)** — via `src/backend.py` |
+ | Dados | Pandas |
+ | Localidades | API IBGE + Nominatim/Overpass (OpenStreetMap) |
+ | WhatsApp | WAHA (WhatsApp HTTP API) |
+@@ -41,17 +41,19 @@ menu (src/main.py)
+ 
+ ```
+ map_scraper_project/
+-├── data/          leads.duckdb (+ .wal transiente, ignorado no Git)
++├── data/          leads.duckdb (usado quando DB_ENGINE=duckdb)
+ ├── memory/        esta documentação para IA
+ ├── output/        Excel gerado (ignorado no Git)
+ ├── src/
+-│   ├── config.py          loader do .env + helpers (bool/int)
+-│   ├── database.py        LeadDatabase: leads, templates_whatsapp, UPSERT, Excel, log WAHA
+-│   ├── localidades_db.py  cache IBGE em DuckDB (tabelas localidades_*)
++│   ├── config.py          loader do .env + escolha do backend (DB_ENGINE)
++│   ├── backend.py         abstração PostgreSQL/DuckDB (conexão, SQL, bulk upsert)
++│   ├── database.py        LeadDatabase: leads, templates, log WAHA (via backend)
++│   ├── localidades_db.py  cache IBGE (via backend)
+ │   ├── locations.py       IBGE + OSM + cache; sync e aquecimento por UF
+ │   ├── scraper.py         Playwright, multithread, anti-captcha
++│   ├── schema.py          DDL + seed + migração (setup: python src/schema.py)
+ │   ├── utils.py           formatar_telefone → (telefone, tipo, link wa)
+-│   ├── whatsapp.py        envio via WAHA
++│   ├── whatsapp.py        envio via WAHA + cadência aleatória
+ │   └── main.py            menu interativo
+ ├── .env / .env.example
+ ├── requirements.txt
+@@ -62,11 +64,13 @@ map_scraper_project/
+ 
+ | Versionado | Ignorado |
+ |---|---|
+-| `data/leads.duckdb` | `.env` (segredos) |
+-| `src/`, `memory/`, `README.md` | `*.duckdb.wal`, `*.duckdb.tmp` |
++| `src/`, `memory/`, `README.md` | `.env` (segredos) |
+ | `.env.example` | `*.xlsx`, `*.csv`, `*.log` |
+ | | `venv/`, `__pycache__/`, `sessions/` |
+ 
++> `data/leads.duckdb` é o banco local (modo `DB_ENGINE=duckdb`). O banco externo
++> PostgreSQL (modo `DB_ENGINE=postgres`) fica no servidor e não é versionado.
 +
-+# Directory Structure
-+````
- data/
-   leads.duckdb
- memory/
-@@ -63,6 +70,196 @@ requirements.txt
- 
- # Files
- 
-+## File: memory/04-como-contribuir.md
-+````markdown
-+ 1: # 04 — Como Contribuir: Padrões e Boas Práticas
-+ 2: 
-+ 3: Este documento detalha os padrões de código, estilo e comunicação esperados
-+ 4: para novas contribuições, visando manter a consistência e facilitar a manutenção.
-+ 5: 
-+ 6: ---
-+ 7: 
-+ 8: ## 1. Organização de Código e Nomenclatura
-+ 9: 
-+10: - **Imports:** Sempre absolutos, começando da raiz `src/`. Ex: `from src.config import ...`.
-+11: - **Constantes:** `MAIUSCULAS_COM_UNDERLINE`.
-+12: - **Funções privadas (internas ao módulo):** `_nome_da_funcao_privada` (com underscore inicial).
-+13: - **Variáveis locais:** `snake_case`.
-+14: - **Classes:** `CamelCase`.
-+15: - **Parâmetros de função:** `snake_case`.
-+16: 
-+17: ---
-+18: 
-+19: ## 2. Logs e Interação com o Usuário
-+20: 
-+21: - **Prints de progresso:** Use `print(f"[{area_da_busca}] Mensagem...")`.
-+22:   O `[área]` (ex: `[Canoas-RS]`, `[Assis Brasil]`) ajuda a identificar qual thread
-+23:   ou cidade está processando no momento.
-+24: - **Mensagens de erro:** Inclua `type(e).__name__` e `str(e)[:N]` para facilitar
-+25:   a depuração em ambientes remotos ou com logs limitados.
-+26: - **Interação:** Use `input()` para entradas do usuário no console. Evite `print()`
-+27:   seguido de `input()` em linhas separadas para prompts, a menos que seja intencional.
-+28: - **Mensagens para o usuário:** Devem ser claras e úteis, preferencialmente
-+29:   em português (padrão atual do projeto).
-+30: 
-+31: ---
-+32: 
-+33: ## 3. Variáveis de Ambiente e Configuração
-+34: 
-+35: - **Todas as configurações** devem ser lidas do `.env` via `src/config.py`.
-+36: - **Nunca faça hardcode** de URLs de APIs, chaves, limites, etc.
-+37: - **Novas variáveis:** Adicione ao `.env.example` com comentários explicativos.
-+38: - **Semântica:** Use `true`/`false` para booleanos, números para inteiros.
-+39:   O `src/config.py` já tem helpers para isso (`str_para_bool`, `env_int`).
-+40: 
-+41: ---
-+42: 
-+43: ## 4. Testes e Validação
-+44: 
-+45: - **Testes unitários/de integração:** Idealmente, adicione pequenos scripts de
-+46:   validação (como os que o modelo Gemini tem feito) para cobrir novas features
-+47:   ou refatorações.
-+48: - **DuckDB:** Para testes que não devem tocar no banco real, use um arquivo
-+49:   DuckDB temporário (`tempfile.gettempdir()`) e defina `localidades_db.DB_PATH_PADRAO`.
-+50: - **Encoding:** Mantenha os arquivos em **UTF-8 sem BOM**.
-+51:   Valide a acentuação após edições em lote: procure caracteres de dupla
-+52:   codificação (por exemplo, `A` com til U+00C3 seguido de símbolo de moeda).
-+53: 
-+54: ---
-+55: 
-+56: ## 5. Documentação
-+57: 
-+58: - **`README.md` (raiz):** Manual do usuário, instalação, execução, fluxo geral.
-+59: - **`memory/`:** Resumos densos para modelos de IA. **Atualize ao mudar comportamento**.
-+60:   - `00-resumo-projeto.md`: alto nível.
-+61:   - `01-arquitetura-e-modulos.md`: detalhe de cada módulo.
-+62:   - `02-decisoes-e-armadilhas.md`: o "porquê" das decisões, bugs conhecidos.
-+63:   - `03-historico-de-mudancas.md`: log recente das mudanças importantes.
-+64: - **Docstrings:** Use docstrings Python para explicar funções e classes.
-+65: - **Comentários de código:** Breves e pontuais, explicando lógica complexa ou escolhas não óbvias.
-+````
+ Comando de sync usado pelo mantenedor (sobrescreve o remoto):
+ 
+ ```powershell
+diff --git a/memory/01-arquitetura-e-modulos.md b/memory/01-arquitetura-e-modulos.md
+index 15309a3..a169bb2 100644
+--- a/memory/01-arquitetura-e-modulos.md
++++ b/memory/01-arquitetura-e-modulos.md
+@@ -17,17 +17,49 @@ env_int(nome, padrao)           # inteiro com fallback
+ PROJETO_RAIZ, CAMINHO_ENV
+ ```
+ 
+-> `src/whatsapp.py` chama `carregar_env()` no import (herança histórica).
+-> `src/locations.py` e `src/scraper.py` dependem disso para ler suas flags.
++**Escolha do banco (engine independente):**
 +
-+## File: src/__init__.py
-+````python
-+1: 
-+````
++```python
++DB_ENGINE        # 'postgres' ou 'duckdb' (inferido se vazio)
++DATABASE_URL     # postgresql://usuario:senha@host:porta/banco
++DUCKDB_PATH      # caminho do DuckDB local (default data/leads.duckdb)
++DB_HOST/DB_PORT/DB_NAME/DB_USER/DB_PASSWORD  # forma separada (legado)
++```
 +
-+## File: src/config.py
-+````python
-+ 1: # src/config.py
-+ 2: """Carregamento centralizado do arquivo .env e leitura de flags.
-+ 3: 
-+ 4: Todos os módulos importam este arquivo, então o `.env` é lido uma única vez
-+ 5: por processo, antes de qualquer constante de configuração ser calculada.
-+ 6: """
-+ 7: import os
-+ 8: 
-+ 9: PROJETO_RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
-+10: CAMINHO_ENV = os.path.join(PROJETO_RAIZ, ".env")
-+11: 
-+12: 
-+13: def carregar_env(caminho=None):
-+14:     """Carrega variáveis de um arquivo .env (formato CHAVE=VALOR).
-+15: 
-+16:     Não sobrescreve variáveis que já existem no ambiente. Ignora linhas em
-+17:     branco, comentários (#) e valores entre aspas.
-+18:     """
-+19:     caminho = caminho or CAMINHO_ENV
-+20:     if not os.path.isfile(caminho):
-+21:         return
-+22: 
-+23:     with open(caminho, "r", encoding="utf-8-sig") as arquivo:
-+24:         for linha in arquivo:
-+25:             linha = linha.strip()
-+26:             if not linha or linha.startswith("#") or "=" not in linha:
-+27:                 continue
-+28:             chave, _, valor = linha.partition("=")
-+29:             chave = chave.strip()
-+30:             valor = valor.strip().strip('"').strip("'")
-+31:             if chave and chave not in os.environ:
-+32:                 os.environ[chave] = valor
-+33: 
-+34: 
-+35: def str_para_bool(valor, padrao=False):
-+36:     """Converte strings comuns de booleano ('true', '1', 'sim', 's', 'yes') em bool."""
-+37:     if valor is None:
-+38:         return padrao
-+39:     return str(valor).strip().lower() in ("1", "true", "yes", "s", "sim", "on")
-+40: 
-+41: 
-+42: def env_int(nome, padrao):
-+43:     """Lê uma variável de ambiente inteira, com fallback para o padrão."""
-+44:     valor = os.environ.get(nome, "").strip()
-+45:     if not valor:
-+46:         return padrao
-+47:     try:
-+48:         return int(float(valor))
-+49:     except ValueError:
-+50:         return padrao
-+51: 
-+52: 
-+53: # Lido no import: qualquer módulo que importe `src.config` já tem o .env aplicado.
-+54: carregar_env()
-+````
++Inferência de `DB_ENGINE` quando não definido: `DUCKDB_PATH` definido → duckdb;
++senão `DATABASE_URL` definido → postgres; senão → duckdb (padrão offline).
 +
-+## File: src/utils.py
-+````python
-+ 1: # src/utils.py
-+ 2: import re
-+ 3: 
-+ 4: def formatar_telefone(telefone_bruto):
-+ 5:     """
-+ 6:     Limpa o telefone, identifica o tipo e gera o link do WhatsApp.
-+ 7:     Retorna: (telefone_limpo, tipo, whatsapp_link)
-+ 8:     """
-+ 9:     if not telefone_bruto:
-+10:         return "", "Não Informado", ""
-+11:     
-+12:     # Remove tudo que não for número
-+13:     apenas_numeros = re.sub(r'\D', '', str(telefone_bruto))
-+14:     
-+15:     # Se o número já vier com DDI (55) e tiver 12 ou 13 dígitos, removemos o 55 
-+16:     # temporariamente para classificar o tipo corretamente (Fixo/Celular)
-+17:     if apenas_numeros.startswith('55') and len(apenas_numeros) > 11:
-+18:         numero_sem_ddi = apenas_numeros[2:]
-+19:     else:
-+20:         numero_sem_ddi = apenas_numeros
-+21: 
-+22:     # Classificação e formatação do Link
-+23:     if len(numero_sem_ddi) == 11: # Celular com 9 dígito
-+24:         tipo = "Celular"
-+25:         whatsapp_link = f"https://wa.me/55{numero_sem_ddi}"
-+26:     elif len(numero_sem_ddi) == 10: # Fixo
-+27:         tipo = "Fixo"
-+28:         whatsapp_link = f"https://wa.me/55{numero_sem_ddi}"
-+29:     elif len(apenas_numeros) > 0:
-+30:         tipo = "Desconhecido"
-+31:         whatsapp_link = f"https://wa.me/{apenas_numeros}"
-+32:     else:
-+33:         return "", "Não Informado", ""
-+34:         
-+35:     # Retorna apenas os números na coluna telefone, o tipo e o link pronto
-+36:     return apenas_numeros, tipo, whatsapp_link
-+````
++---
 +
-+## File: .gitkeep
-+````
-+1: 
-+````
++## src/backend.py — abstração de banco
 +
-+## File: requirements.txt
-+````
-+1: pandas
-+2: openpyxl
-+3: instagpy
-+4: pip-system-certs
-+5: playwright
-+6: chromium
-+7: geopy
-+8: duckdb
-+9: requests
-+````
++Camada única que conhece `duckdb` e `psycopg2` (os demais módulos **não** os
++importam). Expõe:
 +
- ## File: memory/00-resumo-projeto.md
- ````markdown
-  1: # 00 — Resumo do Projeto
-@@ -73,70 +270,72 @@ requirements.txt
-  6: - **Processo:** divide a busca por bairros, raspa o Google Maps com Playwright em
-  7:   multithread e extrai nome, telefone, Instagram e site.
-  8: - **Saída:** leads no DuckDB (`data/leads.duckdb`) + Excel em `output/`.
-- 9: - **Extra:** dispara mensagens de WhatsApp via WAHA para leads já coletados.
--10: 
--11: ## Fluxo de alto nível
-+ 9: - **Extra:** dispara mensagens de WhatsApp via WAHA para leads já coletados, com
-+10:   templates reutilizáveis, filtros (número/cidade/nicho), teste de envio e cache
-+11:   do chatId resolvido (`@lid`/`@c.us`).
- 12: 
--13: ```
--14: menu (src/main.py)
--15:   └─ 1 Coletar    → locations.obter_termos_busca(cidade, uf)
--16:                   → scraper.rodar_scraper_multithread(...)
--17:                   → database.LeadDatabase.save_leads (UPSERT incremental)
--18:                   → database.export_to_excel
--19:   └─ 2 WhatsApp   → database.get_leads_para_envio
--20:                   → whatsapp.disparar_campanha (WAHA)
--21:   └─ 3 Sincronizar localidades (IBGE) → locations.sincronizar_base_localidades
--22:   └─ 4 Aquecer bairros de uma UF       → locations.aquecer_bairros_uf
--23:   └─ 5 Sair
--24: ```
--25: 
--26: ## Stack
-+13: ## Fluxo de alto nível
-+14: 
-+15: ```
-+16: menu (src/main.py)
-+17:   └─ 1 Coletar    → locations.obter_termos_busca(cidade, uf)
-+18:                   → scraper.rodar_scraper_multithread(...)
-+19:                   → database.LeadDatabase.save_leads (UPSERT incremental)
-+20:                   → database.export_to_excel
-+21:   └─ 2 WhatsApp   → template ativo → filtros → teste → database.get_leads_para_envio
-+22:                   → whatsapp.disparar_campanha (WAHA, chatId via checkNumberStatus)
-+23:   └─ 3 Sincronizar localidades (IBGE) → locations.sincronizar_base_localidades
-+24:   └─ 4 Aquecer bairros de uma UF       → locations.aquecer_bairros_uf
-+25:   └─ 5 Sair
-+26: ```
- 27: 
--28: | Item | Tecnologia |
--29: |---|---|
--30: | Linguagem | Python 3.10+ (ambiente: `venv/`) |
--31: | Scraping | Playwright (Chromium) + ThreadPoolExecutor |
--32: | Banco | DuckDB (arquivo único, 1 processo por vez) |
--33: | Dados | Pandas |
--34: | Localidades | API IBGE + Nominatim/Overpass (OpenStreetMap) |
--35: | WhatsApp | WAHA (WhatsApp HTTP API) |
--36: | Config | `.env` carregado por `src/config.py` |
--37: 
--38: ## Estrutura
-+28: ## Stack
-+29: 
-+30: | Item | Tecnologia |
-+31: |---|---|
-+32: | Linguagem | Python 3.10+ (ambiente: `venv/`) |
-+33: | Scraping | Playwright (Chromium) + ThreadPoolExecutor |
-+34: | Banco | DuckDB (arquivo único, 1 processo por vez) |
-+35: | Dados | Pandas |
-+36: | Localidades | API IBGE + Nominatim/Overpass (OpenStreetMap) |
-+37: | WhatsApp | WAHA (WhatsApp HTTP API) |
-+38: | Config | `.env` carregado por `src/config.py` |
- 39: 
--40: ```
--41: map_scraper_project/
--42: ├── data/          leads.duckdb (+ .wal transiente, ignorado no Git)
--43: ├── memory/        esta documentação para IA
--44: ├── output/        Excel gerado (ignorado no Git)
--45: ├── src/
--46: │   ├── config.py          loader do .env + helpers (bool/int)
--47: │   ├── database.py        LeadDatabase: tabela leads, UPSERT, Excel, log WAHA
--48: │   ├── localidades_db.py  cache IBGE em DuckDB (tabelas localidades_*)
--49: │   ├── locations.py       IBGE + OSM + cache; sync e aquecimento por UF
--50: │   ├── scraper.py         Playwright, multithread, anti-captcha
--51: │   ├── utils.py           formatar_telefone → (telefone, tipo, link wa)
--52: │   ├── whatsapp.py        envio via WAHA
--53: │   └── main.py            menu interativo
--54: ├── .env / .env.example
--55: ├── requirements.txt
--56: └── README.md
--57: ```
--58: 
--59: ## Git — o que é versionado
-+40: ## Estrutura
-+41: 
-+42: ```
-+43: map_scraper_project/
-+44: ├── data/          leads.duckdb (+ .wal transiente, ignorado no Git)
-+45: ├── memory/        esta documentação para IA
-+46: ├── output/        Excel gerado (ignorado no Git)
-+47: ├── src/
-+48: │   ├── config.py          loader do .env + helpers (bool/int)
-+49: │   ├── database.py        LeadDatabase: leads, templates_whatsapp, UPSERT, Excel, log WAHA
-+50: │   ├── localidades_db.py  cache IBGE em DuckDB (tabelas localidades_*)
-+51: │   ├── locations.py       IBGE + OSM + cache; sync e aquecimento por UF
-+52: │   ├── scraper.py         Playwright, multithread, anti-captcha
-+53: │   ├── utils.py           formatar_telefone → (telefone, tipo, link wa)
-+54: │   ├── whatsapp.py        envio via WAHA
-+55: │   └── main.py            menu interativo
-+56: ├── .env / .env.example
-+57: ├── requirements.txt
-+58: └── README.md
-+59: ```
- 60: 
--61: | Versionado | Ignorado |
--62: |---|---|
--63: | `data/leads.duckdb` | `.env` (segredos) |
--64: | `src/`, `memory/`, `README.md` | `*.duckdb.wal`, `*.duckdb.tmp` |
--65: | `.env.example` | `*.xlsx`, `*.csv`, `*.log` |
--66: | | `venv/`, `__pycache__/`, `sessions/` |
--67: 
--68: Comando de sync usado pelo mantenedor (sobrescreve o remoto):
-+61: ## Git — o que é versionado
-+62: 
-+63: | Versionado | Ignorado |
-+64: |---|---|
-+65: | `data/leads.duckdb` | `.env` (segredos) |
-+66: | `src/`, `memory/`, `README.md` | `*.duckdb.wal`, `*.duckdb.tmp` |
-+67: | `.env.example` | `*.xlsx`, `*.csv`, `*.log` |
-+68: | | `venv/`, `__pycache__/`, `sessions/` |
- 69: 
--70: ```powershell
--71: git add -A; git commit -m "sync local $(Get-Date -Format 'yyyy-MM-dd HH:mm')"; git push --force-with-lease origin main
--72: ```
-+70: Comando de sync usado pelo mantenedor (sobrescreve o remoto):
-+71: 
-+72: ```powershell
-+73: git add -A; git commit -m "sync local $(Get-Date -Format 'yyyy-MM-dd HH:mm')"; git push --force-with-lease origin main
-+74: ```
- ````
- 
- ## File: memory/01-arquitetura-e-modulos.md
-@@ -308,47 +507,84 @@ requirements.txt
- 165: ```
- 166: nome, telefone, tipo_telefone, whatsapp_link, instagram, site,
- 167: bairro, cidade, estado, nicho, status (default 'ativo'),
--168: data_extracao, data_envio_whatsapp, status_whatsapp (default 'pendente')
--169: ```
--170: 
--171: ```python
--172: save_leads(df) -> int          # filtra descartados, UPSERT, não apaga log WAHA
--173: get_leads_para_envio(limite)   # ativo + Celular + pendente
--174: marcar_envio(nome, cidade, status_whatsapp)   # 'enviado' grava data
--175: export_to_excel(nicho, cidade) # output/leads_{nicho}_{cidade}.xlsx
--176: close()
-+168: data_extracao, data_envio_whatsapp, status_whatsapp (default 'pendente'),
-+169: chat_id_waha
-+170: ```
-+171: 
-+172: - `chat_id_waha`: cache do chatId resolvido pela WAHA (ex.: `143172869029943@lid`).
-+173:   Preenchido na primeira resolução; evita chamar `/api/checkNumberStatus` de novo.
-+174: 
-+175: Tabela `templates_whatsapp` (criada e seedada no `__init__`):
-+176: 
- 177: ```
--178: 
--179: ---
-+178: id INTEGER PK, mensagem, descricao, ativo BOOLEAN (default TRUE)
-+179: ```
- 180: 
--181: ## src/whatsapp.py — WAHA
-+181: - Seed idempotente do template "Apresentação Agendamento Já" (`id=1`).
- 182: 
- 183: ```python
--184: WAHA_API_URL, WAHA_API_KEY, WAHA_SESSION
--185: WAHA_ATIVO, SOMENTE_ENVIO, WAHA_INTERVALO, WAHA_LIMITE
--186: MENSAGEM_PADRAO
--187: enviar_texto_waha(chat_id, texto, ...)   # POST /api/sendText
--188: disparar_campanha(db, mensagem_template=None, intervalo=13, limite=None)
--189: ```
--190: 
--191: - `chat_id` = `55DDD9XXXXXXXX@c.us` (só 11 dígitos; fixo é rejeitado).
--192: - Placeholders: `{nome}`, `{bairro}`, `{cidade}`.
--193: - `SOMENTE_ENVIO=true` (ou `--so-enviar`) pula o menu e vai direto ao envio.
--194: 
--195: ---
--196: 
--197: ## src/main.py — menu
-+184: save_leads(df) -> int          # filtra descartados, UPSERT, não apaga log WAHA
-+185: get_leads_para_envio(limite=None, numero=None, cidade=None, nicho=None)
-+186:                                # ativo + Celular + pendente; filtros opcionais
-+187: marcar_envio(nome, cidade, status_whatsapp)   # 'enviado' grava data
-+188: salvar_chat_id_waha(nome, cidade, chat_id)    # cacheia o chatId resolvido
-+189: listar_templates_ativos()      # [{id, mensagem, descricao, ativo}]
-+190: export_to_excel(nicho, cidade) # output/leads_{nicho}_{cidade}.xlsx
-+191: close()
-+192: ```
-+193: 
-+194: - `get_leads_para_envio`: `numero` compara por dígitos (regex `[^0-9]` removido),
-+195:   aceita parte do número; `cidade`/`nicho` são match exato.
-+196: - `save_leads` **preserva** `status`, `data_envio_whatsapp`, `status_whatsapp` e
-+197:   `chat_id_waha` no re-UPSERT (não sobrescreve log de envio nem o chatId).
- 198: 
--199: ```
--200: 1 - Coletar leads
--201: 2 - Enviar mensagens WhatsApp
--202: 3 - Sincronizar base de localidades (IBGE)
--203: 4 - Aquecer bairros de uma UF (OpenStreetMap)
--204: 5 - Sair
--205: ```
--206: 
--207: `coletar_leads()`: UF → cidade (filtro sem acento) → **confirma no IBGE e usa o
--208: nome oficial** → nicho → termos → "Ver navegador?" → scraping → Excel.
-+199: ---
-+200: 
-+201: ## src/whatsapp.py — WAHA
-+202: 
-+203: ```python
-+204: WAHA_API_URL, WAHA_API_KEY, WAHA_SESSION
-+205: WAHA_ATIVO, SOMENTE_ENVIO, WAHA_INTERVALO, WAHA_LIMITE
-+206: MENSAGEM_PADRAO
-+207: _normalizar_chatid(telefone)            # 55DDDNUMERO@c.us (clássico)
-+208: _resolver_chatid_waha(telefone, ...)    # GET /api/checkNumberStatus → @lid ou @c.us
-+209: _limpar_markdown_whatsapp(texto)        # **negrito** → texto; [r](u) → u
-+210: _renderizar_mensagem(template, lead)    # placeholders + limpa markdown
-+211: enviar_texto_waha(chat_id, texto, ...)  # POST /api/sendText
-+212: enviar_texto_numero(numero, texto, ...) # resolve chatId e envia (p/ teste)
-+213: disparar_campanha(db, mensagem_template=None, intervalo=13, limite=None, leads=None)
-+214: ```
-+215: 
-+216: - **chatId:** números recentes usam `@lid`; enviar `@c.us` para eles retorna
-+217:   **HTTP 500**. `_resolver_chatid_waha` consulta `/api/checkNumberStatus`
-+218:   (`?session=&phone=55DDD9XXXXXXXX`) e usa o `chatId` retornado; fallback `@c.us`.
-+219: - `disparar_campanha` aceita `leads` (DataFrame já filtrado). Se recebido, **não**
-+220:   reconsulta o banco — respeita os filtros aplicados pelo menu.
-+221: - O chatId resolvido é **cacheado** via `db.salvar_chat_id_waha` (só resolve na
-+222:   primeira vez; reenvios pulam o checkNumberStatus).
-+223: - Placeholders: `{nome}`, `{bairro}`, `{cidade}`.
-+224: - `SOMENTE_ENVIO=true` (ou `--so-enviar`) pula o menu e vai direto ao envio.
-+225: 
-+226: ---
-+227: 
-+228: ## src/main.py — menu
-+229: 
-+230: ```
-+231: 1 - Coletar leads
-+232: 2 - Enviar mensagens WhatsApp
-+233: 3 - Sincronizar base de localidades (IBGE)
-+234: 4 - Aquecer bairros de uma UF (OpenStreetMap)
-+235: 5 - Sair
-+236: ```
-+237: 
-+238: `coletar_leads()`: UF → cidade (filtro sem acento) → **confirma no IBGE e usa o
-+239: nome oficial** → nicho → termos → "Ver navegador?" → scraping → Excel.
-+240: 
-+241: `enviar_whatsapp_menu()`: escolhe **template ativo** → aplica **filtros de envio**
-+242: (0 todos / 1 por número / 2 por cidade / 3 por nicho) → pergunta se quer
-+243: **teste de envio** (digitar número ou escolher um lead pendente) → lista os
-+244: pendentes filtrados e confirma o disparo. Helpers: `_confirmar`,
-+245: `_escolher_template`, `_escolher_filtros`, `testar_envio`.
- ````
- 
- ## File: memory/02-decisoes-e-armadilhas.md
-@@ -472,227 +708,68 @@ requirements.txt
- 117: 
- 118: ---
- 119: 
--120: ## `.env` e Git
-+120: ## WAHA: chatId `@c.us` vs `@lid` (HTTP 500)
- 121: 
--122: - `.env` **é ignorado** (contém `WAHA_API_KEY`). `.env.example` **é versionado**.
--123: - Formato: `CHAVE=VALOR`. Comentários só em **linha própria** — comentário na
--124:   mesma linha vira parte do valor (`WAHA_LIMITE= # vazio` → `" # vazio"`).
--125: - Não use `export`/aspas desnecessárias; o loader tira aspas simples/duplas.
--126: - Nunca imprima nem comite segredos.
--127: 
--128: ---
--129: 
--130: ## Scraping: seletores frágeis
--131: 
--132: Dependem do DOM do Google Maps (podem mudar sem aviso):
--133: 
--134: | Dado | Seletor |
--135: |---|---|
--136: | lista de resultados | `div[role="feed"]` |
--137: | links de perfis | `a[href*="/maps/place/"]` |
--138: | nome | `h1` (ignora "Resultados" e vazio) |
--139: | endereço | `button[data-item-id="address"]` (`aria-label`) |
--140: | telefone | `button[data-item-id^="phone:tel:"]` (`aria-label`) |
--141: | site | `a[data-item-id="authority"]` |
--142: | Instagram | primeiro `a[href]` contendo `instagram.com` |
--143: 
--144: Bairro é extraído do endereço: `"Rua X, 123 - Bairro, Cidade - UF"` → parte
--145: entre `" - "` e `","`. Se não casar, `"Não Informado"`.
--146: 
--147: ---
--148: 
--149: ## Concorrência
--150: 
--151: - `save_callback` é chamado **na thread principal** (dentro do loop de
--152:   `as_completed`), então não há escrita concorrente no DuckDB.
--153: - O cooldown anti-captcha usa `_cooldown_lock` + variável global `_cooldown_ate`.
--154: - `lock` protege a lista `vistos`/`todos_leads`.
--155: 
--156: ---
--157: 
--158: ## Coisas que parecem bug mas não são
--159: 
--160: - `"IBGE não publica bairros para X"` → cidade com 1 distrito (ver acima).
--161: - `"Base local ... sem bairros (fonte: cidade)"` → já tentou, o OSM não tinha nada.
--162: - `"LOCALIDADES_SALVAR=false: a base local não será alterada"` → modo leitura.
--163: - `"Aviso: base local ... indisponível (arquivo em uso)"` → feche o DBeaver.
--````
++```python
++IS_DUCKDB            # bool
++ph()                 # placeholder: '?' (duckdb) ou '%s' (postgres)
++conectar()           # abre conexão com o backend configurado
++commit(conn) / close(conn)
++execute(conn, sql, params)
++query_df(conn, sql, params)      # -> DataFrame
++query_one(conn, sql, params)     # -> tupla | None
++query_all(conn, sql, params)     # -> lista de tuplas
++df_to_rows(df)                   # DataFrame -> tuplas (NaN -> None)
++bulk_upsert(conn, table, columns, rows, conflict, set_clause)
++```
++
++`bulk_upsert` monta `INSERT ... VALUES ... ON CONFLICT (...) DO UPDATE ...` com
++multi-linhas, usando `excluded.col` (funciona nos dois bancos).
+ 
+ ---
+ 
+ ## src/localidades_db.py — cache de localidades
+ 
+-Acesso ao **mesmo** `data/leads.duckdb`. **Abre e fecha conexão a cada operação**,
+-para não segurar o arquivo durante o scraping (DuckDB permite só 1 processo).
++Usa `src/backend.py` (funciona em PostgreSQL ou DuckDB). **Abre e fecha conexão
++a cada operação**, para não segurar o banco durante o scraping.
+ 
+-Tabelas (criadas automaticamente quando `CRIAR_TABELAS = True`):
++Tabelas:
+ 
+ | Tabela | Colunas |
+ |---|---|
+@@ -40,7 +72,6 @@ Tabelas (criadas automaticamente quando `CRIAR_TABELAS = True`):
+ Funções:
+ 
+ ```python
+-conexao(db_path=None)              # contextmanager; DDL se CRIAR_TABELAS
+ ler_estados() / salvar_estados(registros)
+ ler_municipios(uf)                 # inclui bairros_fonte (necessário p/ cache hit)
+ ler_municipios_pendentes(uf)       # bairros_fonte IS NULL
+@@ -49,7 +80,7 @@ buscar_municipio(cidade, uf)       # dict ou None
+ ler_bairros(id_municipio) / salvar_bairros(id_municipio, registros, fonte)
+ salvar_distritos_bulk(distritos, min_bairros=3)   # aditivo
+ estatisticas()                     # dict com contagens
+-CacheIndisponivel                  # exceção (arquivo travado / tabela ausente)
++CacheIndisponivel                  # exceção (servidor fora / conexão falhou)
+ ```
+ 
+ **Semânticas importantes**
+@@ -158,12 +189,12 @@ Flags: `CAPTCHA_MAX_TENTATIVAS` (2), `CAPTCHA_PAUSA_SEGUNDOS` (300),
+ 
+ ## src/database.py — leads
+ 
+-`LeadDatabase(db_path="data/leads.duckdb")`
++`LeadDatabase(conn=None)` — usa `src/backend.py` (PostgreSQL ou DuckDB).
+ 
+-Tabela `leads` — PK (`nome`, `cidade`):
++Tabela `leads` — PK `lead_id`, UNIQUE (`nome`, `cidade`):
+ 
+ ```
+-nome, telefone, tipo_telefone, whatsapp_link, instagram, site,
++lead_id, nome, telefone, tipo_telefone, whatsapp_link, instagram, site,
+ bairro, cidade, estado, nicho, status (default 'ativo'),
+ data_extracao, data_envio_whatsapp, status_whatsapp (default 'pendente'),
+ chat_id_waha
+@@ -172,13 +203,21 @@ chat_id_waha
+ - `chat_id_waha`: cache do chatId resolvido pela WAHA (ex.: `143172869029943@lid`).
+   Preenchido na primeira resolução; evita chamar `/api/checkNumberStatus` de novo.
+ 
+-Tabela `templates_whatsapp` (criada e seedada no `__init__`):
++Tabela `templates_whatsapp`:
+ 
+ ```
+-id INTEGER PK, mensagem, descricao, ativo BOOLEAN (default TRUE)
++id PK, mensagem, descricao, segmento, ativo BOOLEAN (default TRUE)
+ ```
+ 
+-- Seed idempotente do template "Apresentação Agendamento Já" (`id=1`).
++- Seed do template "Apresentação Agendamento Já" (segmento `barbearias`) é feito
++  em `schema.py`, **não** no `__init__` (que agora só conecta).
++
++Tabela `whatsapp_envios_log` (log de rastreamento por envio):
++
++```
++id PK, lead_id, nome, cidade, telefone, telefone_normalizado, chat_id,
++status, mensagem, payload, erro, data_envio
++```
+ 
+ ```python
+ save_leads(df) -> int          # filtra descartados, UPSERT, não apaga log WAHA
+@@ -186,7 +225,8 @@ get_leads_para_envio(limite=None, numero=None, cidade=None, nicho=None)
+                                # ativo + Celular + pendente; filtros opcionais
+ marcar_envio(nome, cidade, status_whatsapp)   # 'enviado' grava data
+ salvar_chat_id_waha(nome, cidade, chat_id)    # cacheia o chatId resolvido
+-listar_templates_ativos()      # [{id, mensagem, descricao, ativo}]
++salvar_log_envio(lead_id, nome, cidade, telefone, chat_id, status, ...)
++listar_templates_ativos()      # [{id, mensagem, descricao, segmento, ativo}]
+ export_to_excel(nicho, cidade) # output/leads_{nicho}_{cidade}.xlsx
+ close()
+ ```
+@@ -202,8 +242,11 @@ close()
+ 
+ ```python
+ WAHA_API_URL, WAHA_API_KEY, WAHA_SESSION
+-WAHA_ATIVO, SOMENTE_ENVIO, WAHA_INTERVALO, WAHA_LIMITE
++WAHA_ATIVO, SOMENTE_ENVIO
++WAHA_CADENCIA, WAHA_INTERVALO, WAHA_LIMITE
+ MENSAGEM_PADRAO
++_parse_cadencia(valor)                 # "N:Y" -> (envios_por_janela, janela_s)
++_pausas_cadencia(total, envios, janela)# pausas aleatórias anti-bloqueio
+ _normalizar_chatid(telefone)            # 55DDDNUMERO@c.us (clássico)
+ _resolver_chatid_waha(telefone, ...)    # GET /api/checkNumberStatus → @lid ou @c.us
+ _limpar_markdown_whatsapp(texto)        # **negrito** → texto; [r](u) → u
+@@ -216,6 +259,9 @@ disparar_campanha(db, mensagem_template=None, intervalo=13, limite=None, leads=N
+ - **chatId:** números recentes usam `@lid`; enviar `@c.us` para eles retorna
+   **HTTP 500**. `_resolver_chatid_waha` consulta `/api/checkNumberStatus`
+   (`?session=&phone=55DDD9XXXXXXXX`) e usa o `chatId` retornado; fallback `@c.us`.
++- **Cadência (anti-bloqueio):** `WAHA_CADENCIA="X:Y"` (ex.: `3:60` = 3 envios por
++  minuto) distribui os envios **aleatoriamente** dentro de cada janela de Y
++  segundos, evitando pausas fixas. Tem prioridade sobre `WAHA_INTERVALO` (fixo).
+ - `disparar_campanha` aceita `leads` (DataFrame já filtrado). Se recebido, **não**
+   reconsulta o banco — respeita os filtros aplicados pelo menu.
+ - O chatId resolvido é **cacheado** via `db.salvar_chat_id_waha` (só resolve na
+diff --git a/memory/02-decisoes-e-armadilhas.md b/memory/02-decisoes-e-armadilhas.md
+index 86df9dd..5f7e3b2 100644
+--- a/memory/02-decisoes-e-armadilhas.md
++++ b/memory/02-decisoes-e-armadilhas.md
+@@ -4,9 +4,23 @@ Leia antes de mexer no código. Cada item já custou tempo de depuração.
+ 
+ ---
+ 
+-## DuckDB: um processo por arquivo
++## Banco: PostgreSQL OU DuckDB (via `src/backend.py`)
+ 
+-**O arquivo `data/leads.duckdb` só pode ser aberto por UM processo.** Não existe
++O projeto suporta dois backends, escolhidos por `DB_ENGINE` no `.env`:
++
++- `DB_ENGINE=postgres` → banco externo (`DATABASE_URL` ou `DB_*`).
++- `DB_ENGINE=duckdb` → arquivo local (`DUCKDB_PATH`, default `data/leads.duckdb`).
++
++**Regra de ouro:** nenhum módulo além de `src/backend.py` importa `duckdb` ou
++`psycopg2`. Todo acesso passa por `backend.execute/query_df/query_all/bulk_upsert`.
++- Placeholder de parâmetro: use `backend.ph()` (`?` no DuckDB, `%s` no Postgres),
++  NUNCA hardcode.
++- `excluded.col` funciona no `ON CONFLICT` dos dois bancos.
++- A DDL/seed fica em `schema.py` (roda uma vez: `python src/schema.py`).
++
++### Armadilha do DuckDB: um processo por arquivo
++
++**O `data/leads.duckdb` só pode ser aberto por UM processo.** Não existe
+ "read-only compartilhado" — até `duckdb.connect(..., read_only=True)` falha:
+ 
+ ```
+@@ -16,16 +30,24 @@ O arquivo já está sendo usado por outro processo.
+ 
+ Causas mais comuns: **DBeaver conectado**, scraper rodando, notebook aberto.
+ 
+-Consequências no código:
+-- `localidades_db.conexao()` abre/fecha a cada operação (não mantém aberto).
++Consequências:
++- `localidades_db` abre/fecha a conexão a cada operação (não mantém aberto).
+ - `LeadDatabase` mantém aberto durante o scraping — **não** abra outra conexão
+   persistente no mesmo processo.
+-- `CacheIndisponivel` existe para degradar com aviso em vez de quebrar:
+-  o sistema segue usando as APIs (IBGE/OSM) sem cache.
++- `CacheIndisponivel` degrada com aviso em vez de quebrar.
++
++### Armadilha do PostgreSQL: senha com `@` na URL
++
++Na `DATABASE_URL`, caracteres especiais da senha devem ser "percent-encoded"
++(`@` → `%40`, `:` → `%3A`, `/` → `%2F`). O `config.py` já decodifica com `unquote`.
++Ex.: `aojbfoeub@@@111` → `aojbfoeub%40%40%40111`.
+ 
+-- ⚠️ **Um WAL pendente (`.wal`) indica dados não consolidados.** Se comitar o
+-  `.duckdb` com o programa aberto, o `.wal` (ignorado no Git) fica de fora e o
+-  commit sobe um estado desatualizado. Feche o programa antes de comitar.
++### Armadilha: identidade vs sequence (PostgreSQL)
++
++No Postgres, `templates_whatsapp.id`, `whatsapp_envios_log.id` e
++`localidades_bairros.id` são colunas **IDENTITY**. O `lead_id` de `leads` é
++`integer` com sequence manual (`seq_leads_id`). Não assuma que todas as PKs se
++comportam igual.
+ 
+ ---
+ 
+@@ -96,8 +118,7 @@ OpenStreetMap em toda sincronização.
+ | true | false | lê do banco; o que falta vem da API sem gravar |
+ | false | false | sempre API, banco intocado |
+ 
+-- `SALVAR=false` também desativa a criação de tabelas (`CRIAR_TABELAS`) e os
+-  menus **3** e **4**.
++- `SALVAR=false` também desativa a escrita local e os menus **3** e **4**.
+ - As flags são lidas **no import**: mudar o `.env` exige reiniciar o programa.
+ - Com `USAR_CACHE=false`, cada cidade baixa a lista da UF de novo (exceto pela
+   memoização em memória `_municipios_da_uf`, válida só na execução atual).
+@@ -135,6 +156,18 @@ para números recentes do WhatsApp. Esses números foram migrados para o formato
+ 
+ ---
+ 
++## WAHA: cadência aleatória (anti-bloqueio)
++
++Enviar com pausa fixa (ex.: 15s, 15s, 15s) é fácil de detectar e leva a bloqueio.
++
++- `WAHA_CADENCIA="X:Y"` (ex.: `3:60` = 3 envios/minuto) faz os envios caírem em
++  **pontos aleatórios** dentro de cada janela de Y segundos → pausas variáveis.
++- Tem prioridade sobre `WAHA_INTERVALO` (pausa fixa, usada só se `WAHA_CADENCIA`
++  estiver vazio).
++- Implementação: `_pausas_cadencia(total, envios_janela, janela)` em `whatsapp.py`.
++
++---
++
+ ## `.env` e Git
+ 
+ - `.env` **é ignorado** (contém `WAHA_API_KEY`). `.env.example` **é versionado**.
+@@ -167,7 +200,7 @@ entre `" - "` e `","`. Se não casar, `"Não Informado"`.
+ ## Concorrência
+ 
+ - `save_callback` é chamado **na thread principal** (dentro do loop de
+-  `as_completed`), então não há escrita concorrente no DuckDB.
++  `as_completed`), então não há escrita concorrente no banco.
+ - O cooldown anti-captcha usa `_cooldown_lock` + variável global `_cooldown_ate`.
+ - `lock` protege a lista `vistos`/`todos_leads`.
+ 
+diff --git a/memory/03-historico-de-mudancas.md b/memory/03-historico-de-mudancas.md
+index 7e047dd..c51feff 100644
+--- a/memory/03-historico-de-mudancas.md
++++ b/memory/03-historico-de-mudancas.md
+@@ -4,6 +4,38 @@ Registro do que mudou, por quê e o que ficou pendente. Mais recente primeiro.
+ 
+ ---
+ 
++## 2026-10-31
++
++### Migração para PostgreSQL + suporte dual (PostgreSQL/DuckDB)
++
++- Banco externo PostgreSQL (`vps.agendamentoja.com/leads_db`) + mantido o DuckDB
++  local como alternativa offline.
++- Novo `src/backend.py`: abstrai conexão, placeholder (`?`/`%s`), leitura
++  (DataFrame/tupla) e bulk upsert entre os dois bancos. `database.py`,
++  `localidades_db.py` e `schema.py` não importam mais `duckdb`/`psycopg2`.
++- `config.py` lê `DB_ENGINE` (postgres|duckdb), `DATABASE_URL` e `DUCKDB_PATH`.
++  Inferência: DUCKDB_PATH → duckdb; senão DATABASE_URL → postgres; senão duckdb.
++- `schema.py` reescrito para os dois bancos; corrige o gap da tabela `leads`
++  (PK `lead_id` + UNIQUE `(nome,cidade)` + default `nextval('seq_leads_id')`).
++- `requirements.txt`: readicionado `duckdb` + `psycopg2-binary`.
++- `.env`: seção "BANCO DE DADOS — engine independente" com `DATABASE_URL` (senha
++  com `@` percent-encoded) e config antiga comentada como referência.
++
++### Cadência aleatória de envio WhatsApp (anti-bloqueio)
++
++- Nova `WAHA_CADENCIA="X:Y"` no `.env` (ex.: `3:60` = 3 envios por minuto).
++- `whatsapp.py`: `_parse_cadencia` + `_pausas_cadencia` distribuem os envios em
++  pontos **aleatórios** dentro de cada janela (pausas variáveis, não fixas).
++- Tem prioridade sobre `WAHA_INTERVALO` (fixo). `WAHA_CADENCIA` vazio → usa o fixo.
++
++### Tabela `whatsapp_envios_log` (rastreamento)
++
++- Log por envio com `lead_id`, `telefone` (dígitos) e `telefone_normalizado`
++  (55DDDNUMERO), `chat_id`, `status`, `mensagem`, `payload`, `erro`, `data_envio`.
++- JOIN pronto por `lead_id` ou `telefone`.
++
++---
++
+ ## 2026-10-30
+ 
+ ### Templates de mensagem de WhatsApp (tabela + markdown)
+diff --git a/memory/README.md b/memory/README.md
+index d368177..6e4ffd8 100644
+--- a/memory/README.md
++++ b/memory/README.md
+@@ -38,7 +38,10 @@ git add -A; git commit -m "Atualização"; git push --force origin main
+ 
+ 
+ ## git forçado
+-- Envia
++
++# Envia
+ git add -A; git commit -m "Melhorias no processo de coletas v3 $(Get-Date -Format 'yyyy-MM-dd HH:mm')"; git push --force-with-lease origin main
+-- Recebe
++
++# Recebe
++
+ git fetch --all; git reset --hard origin/main
+\ No newline at end of file
+diff --git a/requirements.txt b/requirements.txt
+index 8bfac01..6e167ed 100644
+--- a/requirements.txt
++++ b/requirements.txt
+@@ -6,4 +6,5 @@ playwright
+ chromium
+ geopy
+ duckdb
++psycopg2-binary
+ requests
+diff --git a/src/config.py b/src/config.py
+index 5d585ca..fa7e3e2 100644
+--- a/src/config.py
++++ b/src/config.py
+@@ -1,5 +1,5 @@
+ # src/config.py
+-"""Carregamento centralizado do arquivo .env e leitura de flags.
++"""Carregamento centralizado do arquivo .env, leitura de flags e conexão com o banco.
+ 
+ Todos os módulos importam este arquivo, então o `.env` é lido uma única vez
+ por processo, antes de qualquer constante de configuração ser calculada.
+@@ -52,3 +52,33 @@ def env_int(nome, padrao):
+ 
+ # Lido no import: qualquer módulo que importe `src.config` já tem o .env aplicado.
+ carregar_env()
++
++# ---------------------------------------------------------------------------
++# Banco de dados — engine independente (PostgreSQL ou DuckDB)
++# ---------------------------------------------------------------------------
++# Escolha do backend:
++#   DB_ENGINE=postgres  -> PostgreSQL (DATABASE_URL ou DB_*)
++#   DB_ENGINE=duckdb    -> DuckDB local (DUCKDB_PATH)
++#
++# Se DB_ENGINE não for definido, a inferência é:
++#   DUCKDB_PATH  definido -> duckdb
++#   DATABASE_URL definido -> postgres
++#   nenhum dos dois       -> duckdb (padrão local/offline)
++DATABASE_URL = os.environ.get("DATABASE_URL", "")
++DUCKDB_PATH = os.environ.get("DUCKDB_PATH", "data/leads.duckdb")
++
++DB_ENGINE = os.environ.get("DB_ENGINE", "").strip().lower()
++if DB_ENGINE not in ("postgres", "duckdb"):
++    if os.environ.get("DUCKDB_PATH"):
++        DB_ENGINE = "duckdb"
++    elif os.environ.get("DATABASE_URL"):
++        DB_ENGINE = "postgres"
++    else:
++        DB_ENGINE = "duckdb"
++
++# Configuração do PostgreSQL (usada apenas quando DB_ENGINE=postgres).
++DB_HOST = os.environ.get("DB_HOST", "localhost")
++DB_PORT = env_int("DB_PORT", 5432)
++DB_NAME = os.environ.get("DB_NAME", "leads_db")
++DB_USER = os.environ.get("DB_USER", "leads_app")
++DB_PASSWORD = os.environ.get("DB_PASSWORD", "")
+diff --git a/src/database.py b/src/database.py
+index f59ddc6..b8a4df2 100644
+--- a/src/database.py
++++ b/src/database.py
+@@ -1,157 +1,36 @@
+ # src/database.py
+-import duckdb
+-import pandas as pd
++"""Camada de acesso a dados (leads, templates e log de envio).
++
++Usa `src/backend.py`, que abstrai PostgreSQL e DuckDB — o código daqui não
++depende do banco específico. A criação do schema e o seed dos templates ficam
++em `src/schema.py` (executado uma vez no setup: `python src/schema.py`).
++"""
+ import os
+ import re
+ import json
+ from datetime import datetime
+ 
+-# Template padrão de WhatsApp, usado para popular a tabela de templates.
+-# Segmento indica o nicho para o qual a mensagem foi criada (ex.: barbearias).
+-TEMPLATE_AGRUPAMENTO_PADRAO = """Opa, tudo certo?
+-
+-Conhece o Agendamento Já? É uma plataforma 100% online para deixar sua agenda no piloto automático e acabar com a dor de cabeça de gerenciar horários pelo WhatsApp.
+-
+-Com planos a partir de R$ 60,00 no nosso aplicativo você consegue:
+-
+-• Personalizar com a identidade da sua marca
+-• Lembretes automatizados via Whatsapp
+-• Divulgação de horários automatizadas
+-• Controle de faturamento
+-• Pagamentos antecipados
 -
--## File: memory/04-como-contribuir.md
--````markdown
-- 1: # 04 — Como Contribuir: Padrões e Boas Práticas
-- 2: 
-- 3: Este documento detalha os padrões de código, estilo e comunicação esperados
-- 4: para novas contribuições, visando manter a consistência e facilitar a manutenção.
-- 5: 
-- 6: ---
-- 7: 
-- 8: ## 1. Organização de Código e Nomenclatura
-- 9: 
--10: - **Imports:** Sempre absolutos, começando da raiz `src/`. Ex: `from src.config import ...`.
--11: - **Constantes:** `MAIUSCULAS_COM_UNDERLINE`.
--12: - **Funções privadas (internas ao módulo):** `_nome_da_funcao_privada` (com underscore inicial).
--13: - **Variáveis locais:** `snake_case`.
--14: - **Classes:** `CamelCase`.
--15: - **Parâmetros de função:** `snake_case`.
--16: 
--17: ---
--18: 
--19: ## 2. Logs e Interação com o Usuário
--20: 
--21: - **Prints de progresso:** Use `print(f"[{area_da_busca}] Mensagem...")`.
--22:   O `[área]` (ex: `[Canoas-RS]`, `[Assis Brasil]`) ajuda a identificar qual thread
--23:   ou cidade está processando no momento.
--24: - **Mensagens de erro:** Inclua `type(e).__name__` e `str(e)[:N]` para facilitar
--25:   a depuração em ambientes remotos ou com logs limitados.
--26: - **Interação:** Use `input()` para entradas do usuário no console. Evite `print()`
--27:   seguido de `input()` em linhas separadas para prompts, a menos que seja intencional.
--28: - **Mensagens para o usuário:** Devem ser claras e úteis, preferencialmente
--29:   em português (padrão atual do projeto).
--30: 
--31: ---
--32: 
--33: ## 3. Variáveis de Ambiente e Configuração
--34: 
--35: - **Todas as configurações** devem ser lidas do `.env` via `src/config.py`.
--36: - **Nunca faça hardcode** de URLs de APIs, chaves, limites, etc.
--37: - **Novas variáveis:** Adicione ao `.env.example` com comentários explicativos.
--38: - **Semântica:** Use `true`/`false` para booleanos, números para inteiros.
--39:   O `src/config.py` já tem helpers para isso (`str_para_bool`, `env_int`).
--40: 
--41: ---
--42: 
--43: ## 4. Testes e Validação
--44: 
--45: - **Testes unitários/de integração:** Idealmente, adicione pequenos scripts de
--46:   validação (como os que o modelo Gemini tem feito) para cobrir novas features
--47:   ou refatorações.
--48: - **DuckDB:** Para testes que não devem tocar no banco real, use um arquivo
--49:   DuckDB temporário (`tempfile.gettempdir()`) e defina `localidades_db.DB_PATH_PADRAO`.
--50: - **Encoding:** Mantenha os arquivos em **UTF-8 sem BOM**.
--51:   Valide a acentuação após edições em lote: procure caracteres de dupla
--52:   codificação (por exemplo, `A` com til U+00C3 seguido de símbolo de moeda).
--53: 
--54: ---
--55: 
--56: ## 5. Documentação
--57: 
--58: - **`README.md` (raiz):** Manual do usuário, instalação, execução, fluxo geral.
--59: - **`memory/`:** Resumos densos para modelos de IA. **Atualize ao mudar comportamento**.
--60:   - `00-resumo-projeto.md`: alto nível.
--61:   - `01-arquitetura-e-modulos.md`: detalhe de cada módulo.
--62:   - `02-decisoes-e-armadilhas.md`: o "porquê" das decisões, bugs conhecidos.
--63:   - `03-historico-de-mudancas.md`: log recente das mudanças importantes.
--64: - **Docstrings:** Use docstrings Python para explicar funções e classes.
--65: - **Comentários de código:** Breves e pontuais, explicando lógica complexa ou escolhas não óbvias.
--````
+-Conheça nossa proposta: https://agendamentoja.com/
+-Acompanhe nosso dia a dia: https://www.instagram.com/agendamentoja_
++import pandas as pd
+ 
+-Quer ver uma demonstração rápida de como funciona na prática para o seu tipo de serviço? É só me avisar!"""
++from src import backend
+ 
+-# Segmento (nicho) padrão do template acima.
+-TEMPLATE_SEGMENTO_PADRAO = "barbearias"
+ 
+ class LeadDatabase:
+-    def __init__(self, db_path="data/leads.duckdb"):
+-        os.makedirs(os.path.dirname(db_path), exist_ok=True)
+-        self.db_path = db_path
+-        self.conn = duckdb.connect(self.db_path)
+-        self._create_sequences()
+-        self._create_table()
+-        self._ensure_whatsapp_columns()
+-        self._ensure_lead_id()
+-        self._create_templates_table()
+-        self._seed_templates()
+-        self._create_envios_log_table()
 -
--## File: src/__init__.py
--````python
--1: 
--````
+-    def _create_sequences(self):
+-        """Sequências de ids numéricos (leads e log de envios)."""
+-        self.conn.execute("CREATE SEQUENCE IF NOT EXISTS seq_leads_id")
+-        self.conn.execute("CREATE SEQUENCE IF NOT EXISTS seq_whatsapp_envios_log_id")
 -
--## File: src/config.py
--````python
-- 1: # src/config.py
-- 2: """Carregamento centralizado do arquivo .env e leitura de flags.
-- 3: 
-- 4: Todos os módulos importam este arquivo, então o `.env` é lido uma única vez
-- 5: por processo, antes de qualquer constante de configuração ser calculada.
-- 6: """
-- 7: import os
-- 8: 
-- 9: PROJETO_RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
--10: CAMINHO_ENV = os.path.join(PROJETO_RAIZ, ".env")
--11: 
--12: 
--13: def carregar_env(caminho=None):
--14:     """Carrega variáveis de um arquivo .env (formato CHAVE=VALOR).
--15: 
--16:     Não sobrescreve variáveis que já existem no ambiente. Ignora linhas em
--17:     branco, comentários (#) e valores entre aspas.
--18:     """
--19:     caminho = caminho or CAMINHO_ENV
--20:     if not os.path.isfile(caminho):
--21:         return
--22: 
--23:     with open(caminho, "r", encoding="utf-8-sig") as arquivo:
--24:         for linha in arquivo:
--25:             linha = linha.strip()
--26:             if not linha or linha.startswith("#") or "=" not in linha:
--27:                 continue
--28:             chave, _, valor = linha.partition("=")
--29:             chave = chave.strip()
--30:             valor = valor.strip().strip('"').strip("'")
--31:             if chave and chave not in os.environ:
--32:                 os.environ[chave] = valor
--33: 
--34: 
--35: def str_para_bool(valor, padrao=False):
--36:     """Converte strings comuns de booleano ('true', '1', 'sim', 's', 'yes') em bool."""
--37:     if valor is None:
--38:         return padrao
--39:     return str(valor).strip().lower() in ("1", "true", "yes", "s", "sim", "on")
--40: 
--41: 
--42: def env_int(nome, padrao):
--43:     """Lê uma variável de ambiente inteira, com fallback para o padrão."""
--44:     valor = os.environ.get(nome, "").strip()
--45:     if not valor:
--46:         return padrao
--47:     try:
--48:         return int(float(valor))
--49:     except ValueError:
--50:         return padrao
--51: 
--52: 
--53: # Lido no import: qualquer módulo que importe `src.config` já tem o .env aplicado.
--54: carregar_env()
--````
+-    def _create_table(self):
+-        self.conn.execute("""
+-            CREATE TABLE IF NOT EXISTS leads (
+-                lead_id INTEGER DEFAULT nextval('seq_leads_id'),
+-                nome VARCHAR,
+-                telefone VARCHAR,
+-                tipo_telefone VARCHAR,
+-                whatsapp_link VARCHAR,
+-                instagram VARCHAR,
+-                site VARCHAR,
+-                bairro VARCHAR,
+-                cidade VARCHAR,
+-                estado VARCHAR,
+-                nicho VARCHAR,
+-                status VARCHAR DEFAULT 'ativo',
+-                data_extracao TIMESTAMP,
+-                data_envio_whatsapp TIMESTAMP,
+-                status_whatsapp VARCHAR DEFAULT 'pendente',
+-                chat_id_waha VARCHAR,
+-                PRIMARY KEY (nome, cidade)
+-            )
+-        """)
 -
--## File: src/utils.py
--````python
-- 1: # src/utils.py
-- 2: import re
-- 3: 
-- 4: def formatar_telefone(telefone_bruto):
-- 5:     """
-- 6:     Limpa o telefone, identifica o tipo e gera o link do WhatsApp.
-- 7:     Retorna: (telefone_limpo, tipo, whatsapp_link)
-- 8:     """
-- 9:     if not telefone_bruto:
--10:         return "", "Não Informado", ""
--11:     
--12:     # Remove tudo que não for número
--13:     apenas_numeros = re.sub(r'\D', '', str(telefone_bruto))
--14:     
--15:     # Se o número já vier com DDI (55) e tiver 12 ou 13 dígitos, removemos o 55 
--16:     # temporariamente para classificar o tipo corretamente (Fixo/Celular)
--17:     if apenas_numeros.startswith('55') and len(apenas_numeros) > 11:
--18:         numero_sem_ddi = apenas_numeros[2:]
--19:     else:
--20:         numero_sem_ddi = apenas_numeros
--21: 
--22:     # Classificação e formatação do Link
--23:     if len(numero_sem_ddi) == 11: # Celular com 9 dígito
--24:         tipo = "Celular"
--25:         whatsapp_link = f"https://wa.me/55{numero_sem_ddi}"
--26:     elif len(numero_sem_ddi) == 10: # Fixo
--27:         tipo = "Fixo"
--28:         whatsapp_link = f"https://wa.me/55{numero_sem_ddi}"
--29:     elif len(apenas_numeros) > 0:
--30:         tipo = "Desconhecido"
--31:         whatsapp_link = f"https://wa.me/{apenas_numeros}"
--32:     else:
--33:         return "", "Não Informado", ""
--34:         
--35:     # Retorna apenas os números na coluna telefone, o tipo e o link pronto
--36:     return apenas_numeros, tipo, whatsapp_link
--````
+-    def _ensure_whatsapp_columns(self):
+-        """Adiciona as colunas de log de WhatsApp em bancos criados antes da migração."""
+-        colunas = {row[1] for row in self.conn.execute("PRAGMA table_info(leads)").fetchall()}
+-        if 'data_envio_whatsapp' not in colunas:
+-            self.conn.execute("ALTER TABLE leads ADD COLUMN data_envio_whatsapp TIMESTAMP")
+-        if 'status_whatsapp' not in colunas:
+-            self.conn.execute("ALTER TABLE leads ADD COLUMN status_whatsapp VARCHAR DEFAULT 'pendente'")
+-        if 'chat_id_waha' not in colunas:
+-            self.conn.execute("ALTER TABLE leads ADD COLUMN chat_id_waha VARCHAR")
 -
--## File: .gitkeep
--````
--1: 
-+122: Enviar `POST /api/sendText` com `chatId = 55DDDNUMERO@c.us` **falha com HTTP 500**
-+123: para números recentes do WhatsApp. Esses números foram migrados para o formato
-+124: **`@lid`** (hidden user ID).
-+125: 
-+126: - Diagnóstico: `GET /api/checkNumberStatus?session=default&phone=55DDD9XXXXXXXX`
-+127:   responde `{"numberExists": true, "chatId": "143172869029943@lid"}`.
-+128: - Correção: **sempre resolver o chatId via `checkNumberStatus` antes de enviar**,
-+129:   em vez de montar `@c.us` na mão (é o que a documentação da WAHA recomenda para
-+130:   números brasileiros).
-+131: - O chatId resolvido é **cacheado** na coluna `leads.chat_id_waha` — a consulta
-+132:   extra só acontece uma vez por lead.
-+133: - ⚠️ O payload do `sendText` está correto (`{session, chatId, text}` + header
-+134:   `X-Api-Key`); o erro 500 era **só** o formato do `chatId`, não o endpoint.
-+135: 
-+136: ---
-+137: 
-+138: ## `.env` e Git
-+139: 
-+140: - `.env` **é ignorado** (contém `WAHA_API_KEY`). `.env.example` **é versionado**.
-+141: - Formato: `CHAVE=VALOR`. Comentários só em **linha própria** — comentário na
-+142:   mesma linha vira parte do valor (`WAHA_LIMITE= # vazio` → `" # vazio"`).
-+143: - Não use `export`/aspas desnecessárias; o loader tira aspas simples/duplas.
-+144: - Nunca imprima nem comite segredos.
-+145: 
-+146: ---
-+147: 
-+148: ## Scraping: seletores frágeis
-+149: 
-+150: Dependem do DOM do Google Maps (podem mudar sem aviso):
-+151: 
-+152: | Dado | Seletor |
-+153: |---|---|
-+154: | lista de resultados | `div[role="feed"]` |
-+155: | links de perfis | `a[href*="/maps/place/"]` |
-+156: | nome | `h1` (ignora "Resultados" e vazio) |
-+157: | endereço | `button[data-item-id="address"]` (`aria-label`) |
-+158: | telefone | `button[data-item-id^="phone:tel:"]` (`aria-label`) |
-+159: | site | `a[data-item-id="authority"]` |
-+160: | Instagram | primeiro `a[href]` contendo `instagram.com` |
-+161: 
-+162: Bairro é extraído do endereço: `"Rua X, 123 - Bairro, Cidade - UF"` → parte
-+163: entre `" - "` e `","`. Se não casar, `"Não Informado"`.
-+164: 
-+165: ---
-+166: 
-+167: ## Concorrência
-+168: 
-+169: - `save_callback` é chamado **na thread principal** (dentro do loop de
-+170:   `as_completed`), então não há escrita concorrente no DuckDB.
-+171: - O cooldown anti-captcha usa `_cooldown_lock` + variável global `_cooldown_ate`.
-+172: - `lock` protege a lista `vistos`/`todos_leads`.
-+173: 
-+174: ---
-+175: 
-+176: ## Coisas que parecem bug mas não são
-+177: 
-+178: - `"IBGE não publica bairros para X"` → cidade com 1 distrito (ver acima).
-+179: - `"Base local ... sem bairros (fonte: cidade)"` → já tentou, o OSM não tinha nada.
-+180: - `"LOCALIDADES_SALVAR=false: a base local não será alterada"` → modo leitura.
-+181: - `"Aviso: base local ... indisponível (arquivo em uso)"` → feche o DBeaver.
- ````
- 
- ## File: .repomixignore
-@@ -776,156 +853,19 @@ requirements.txt
- 30:     }
- 31:   },
- 32:   "include": [],
--33:   "ignore": {
--34:     "useGitignore": true,
--35:     "useDotIgnore": true,
--36:     "useDefaultPatterns": true,
--37:     "customPatterns": []
--38:   },
--39:   "security": {
--40:     "enableSecurityCheck": true
--41:   },
--42:   "tokenCount": {
--43:     "encoding": "o200k_base"
--44:   }
--45: }
--````
+-    def _ensure_lead_id(self):
+-        """Adiciona o id numérico em bancos antigos (backfill automático via DEFAULT)."""
+-        colunas = {row[1] for row in self.conn.execute("PRAGMA table_info(leads)").fetchall()}
+-        if 'lead_id' not in colunas:
+-            self.conn.execute(
+-                "ALTER TABLE leads ADD COLUMN lead_id INTEGER DEFAULT nextval('seq_leads_id')"
+-            )
 -
--## File: requirements.txt
--````
--1: pandas
--2: openpyxl
--3: instagpy
--4: pip-system-certs
--5: playwright
--6: chromium
--7: geopy
--8: duckdb
--9: requests
--````
+-    def _create_templates_table(self):
+-        """Tabela de templates de mensagem de WhatsApp (mensagem, descrição, segmento e ativo)."""
+-        self.conn.execute("""
+-            CREATE TABLE IF NOT EXISTS templates_whatsapp (
+-                id INTEGER PRIMARY KEY,
+-                mensagem VARCHAR,
+-                descricao VARCHAR,
+-                segmento VARCHAR,
+-                ativo BOOLEAN DEFAULT TRUE
+-            )
+-        """)
+-        colunas = {row[1] for row in self.conn.execute("PRAGMA table_info(templates_whatsapp)").fetchall()}
+-        if 'segmento' not in colunas:
+-            self.conn.execute("ALTER TABLE templates_whatsapp ADD COLUMN segmento VARCHAR")
 -
--## File: memory/03-historico-de-mudancas.md
--````markdown
--  1: # 03 — Histórico de Mudanças
--  2: 
--  3: Registro do que mudou, por quê e o que ficou pendente. Mais recente primeiro.
--  4: 
--  5: ---
--  6: 
--  7: ## 2026-10-29
--  8: 
--  9: ### Memória do projeto para IA
-- 10: 
-- 11: - Criada a pasta `memory/` com documentação densa para reduzir custo de contexto.
-- 12: - Arquivos: `README.md`, `00-resumo-projeto.md`, `01-arquitetura-e-modulos.md`,
-- 13:   `02-decisoes-e-armadilhas.md`, `03-historico-de-mudancas.md`,
-- 14:   `04-como-contribuir.md` (padrões de código, logs, config, testes e docs).
-- 15: - `README.md` limpo: removido o bloco "env temp:" (dump cru do `.env`) e
-- 16:   adicionadas as seções 12 (memória para IA) e 13 (observação sobre configuração).
-- 17: 
-- 18: ### Correção: cache de bairros ignorado (`bairros_fonte`)
-- 19: 
-- 20: - **Sintoma:** com `LOCALIDADES_USAR_CACHE=true` e base populada, a coleta ainda
-- 21:   consultava IBGE e Overpass.
-- 22: - **Causa:** `localidades_db.ler_municipios()` não retornava `bairros_fonte`;
-- 23:   `_resolver_municipio` repassava `None`, então o cache nunca era considerado.
-- 24: - **Correção:** query passou a trazer `uf` e `bairros_fonte`; o resolver repassa
-- 25:   o valor real.
-- 26: - **Teste:** com as funções de rede trocadas por `AssertionError`, os bairros de
-- 27:   Canoas (fonte `overpass`) e Bento Gonçalves (fonte `ibge`) vieram do banco.
-- 28: 
-- 29: ### Nome oficial do município (IBGE) na coleta
-- 30: 
-- 31: - `obter_municipio(cidade, uf)` confirma o município e devolve `id_municipio`,
-- 32:   `nome` oficial e `uf`.
-- 33: - `filtrar_cidades(cidades, termo)` compara **sem acento e sem caixa**:
-- 34:   `canoas`, `sao leopoldo`, `CHAPECO` funcionam.
-- 35: - `main.coletar_leads()` passa a usar o nome oficial no scraping, no banco e no
-- 36:   nome do Excel, e imprime `Município (IBGE): Canoas-RS | código 4304606`.
-- 37: - Lista de municípios **memoizada** por execução (`_municipios_da_uf`), evitando
-- 38:   rebaixar a lista da UF a cada cidade (principalmente com `SALVAR=false`).
-- 39: 
-- 40: ### Mensagens de bairros mais honestas
-- 41: 
-- 42: - Antes: `IBGE retornou 0 distrito(s) útil(eis)`.
-- 43: - Agora: `IBGE não publica bairros para Canoas-RS: o município tem apenas 1 distrito (a sede).`
-- 44: - Motivo: a API de Localidades do IBGE **não tem bairros** (só distritos).
-- 45: 
-- 46: ### Aquecimento de bairros por UF (menu 4)
-- 47: 
-- 48: - `locations.aquecer_bairros_uf(uf, cidades=None, max_cidades=0, pausa_segundos=None)`.
-- 49: - `localidades_db.ler_municipios_pendentes(uf)` → só `bairros_fonte IS NULL`.
-- 50: - Retoma de onde parou; `Ctrl+C` preserva o que já foi gravado.
-- 51: - Pausa (`AQUECER_PAUSA_SEGUNDOS`, default 2) só quando a cidade usou o OSM.
-- 52: - Falha de rede não grava nada (`falhas` no resumo) e a cidade continua pendente.
-- 53: - Bloqueado quando `LOCALIDADES_SALVAR=false`.
-- 54: - Medido: AC 21 → 18 → 17 pendentes; SP 621 → 616.
-- 55: 
-- 56: ### Flag `LOCALIDADES_SALVAR`
-- 57: 
-- 58: - `false` = somente leitura: nenhuma escrita, **nem criação de tabelas**
-- 59:   (`localidades_db.CRIAR_TABELAS = False`) e menus 3/4 desativados.
-- 60: - Todas as escritas passam por `_salvar()`, que respeita a flag.
-- 61: - Aviso único por execução para não poluir o log.
-- 62: 
-- 63: ### `.env` e `.env.example` comentados
-- 64: 
-- 65: - Cada variável com explicação, faixa de valores e efeito colateral.
-- 66: - Tabela das 4 combinações `USAR_CACHE × SALVAR`.
-- 67: - Regra explícita: comentário só em linha própria.
-- 68: - Valores locais preservados (`USAR_CACHE=false` → depois `true`).
-- 69: 
-- 70: ### Base de localidades offline (IBGE) — menu 3
-- 71: 
-- 72: - Novo `src/localidades_db.py` com tabelas `localidades_estados`,
-- 73:   `localidades_municipios`, `localidades_bairros` no mesmo `leads.duckdb`.
-- 74: - `src/config.py` centraliza o loader do `.env` (antes duplicado no `whatsapp.py`).
-- 75: - `src/locations.py` reescrito: cache → API → grava.
-- 76: - Sync nacional: 27 estados, 5.571 municípios, 10.751 distritos; 643 cidades com
-- 77:   bairros prontos pelo IBGE.
-- 78: - Fallback OSM por cidade, gravado uma única vez.
-- 79: 
-- 80: ### Anti-captcha / bloqueio do Google Maps
-- 81: 
-- 82: - Detecção por URL `/sorry/`, seletores de captcha e textos ("tráfego incomum").
-- 83: - Retry com pausa longa (`CAPTCHA_PAUSA_SEGUNDOS`) e **cooldown global**
-- 84:   (`CAPTCHA_PAUSA_GLOBAL_SEGUNDOS`) entre todas as threads.
-- 85: - Bloqueio persistente → aborta a área e **preserva os leads já extraídos**.
-- 86: - Testado com Playwright real: página normal passa, página de captcha levanta
-- 87:   `BloqueioDetectado` após `CAPTCHA_MAX_TENTATIVAS`.
-- 88: 
-- 89: ### Correção: menu não aparecia
-- 90: 
-- 91: - `src/main.py` definia `menu_interativo()` mas **nunca chamava**.
-- 92: - Adicionado `if __name__ == "__main__": menu_interativo()`.
-- 93: 
-- 94: ### Banco DuckDB versionado
-- 95: 
-- 96: - `data/leads.duckdb` passou a ser versionado no Git.
-- 97: - `.gitignore`: removidos `data/` e `*.duckdb` da lista de ignore; adicionados
-- 98:   `*.duckdb.wal` e `*.duckdb.tmp`.
-- 99: - `*.xlsx`, `*.csv`, `*.log` continuam ignorados (confirmado com
--100:   `git check-ignore` e `git ls-files`).
--101: - ⚠️ Comitar com o programa aberto sobe o `.duckdb` sem o `.wal` (dados
--102:   desatualizados). Fechar antes.
--103: 
--104: ---
--105: 
--106: ## Pendências / próximos passos
--107: 
--108: | Item | Status |
--109: |---|---|
--110: | Bairros oficiais via CNEFE 2022 | **Não implementar por hora** (decisão do mantenedor) |
--111: | Resolução automática de captcha (2Captcha/CapMonster) | Não implementado; hoje pausa e desiste da área |
--112: | Enriquecimento de e-mail a partir dos sites | Não iniciado |
--113: | Base de bairros offline nacional | Coberto parcialmente pelo IBGE (643 cidades) |
--114: 
--115: ## Problemas conhecidos (ambiente)
--116: 
--117: - **DBeaver aberto trava o DuckDB** → cache cai para as APIs.
--118: - **Overpass/Nominatim instáveis** (502, timeout) → aquecimento por UF precisa de
--119:   paciência e retomadas.
--120: - Interprete global do mantenedor é Python 3.15; **usar `venv\Scripts\python.exe`**.
-+33:   "ignore": {
-+34:     "useGitignore": true,
-+35:     "useDotIgnore": true,
-+36:     "useDefaultPatterns": true,
-+37:     "customPatterns": []
-+38:   },
-+39:   "security": {
-+40:     "enableSecurityCheck": true
-+41:   },
-+42:   "tokenCount": {
-+43:     "encoding": "o200k_base"
-+44:   }
-+45: }
- ````
- 
- ## File: memory/README.md
-@@ -962,278 +902,17 @@ requirements.txt
- 30: 
- 31: - `README.md` (raiz) — manual do usuário, instalação, uso.
- 32: - `.env.example` — valores e comentários de cada variável.
--````
+-    def _seed_templates(self):
+-        """Garante o template padrão do Agendamento Já (id=1), atualizando se já existir."""
+-        self.conn.execute("""
+-            INSERT INTO templates_whatsapp (id, mensagem, descricao, segmento, ativo)
+-            VALUES (1, ?, 'Apresentação Agendamento Já', ?, TRUE)
+-            ON CONFLICT (id) DO UPDATE SET
+-                mensagem = excluded.mensagem,
+-                descricao = excluded.descricao,
+-                segmento = excluded.segmento,
+-                ativo = excluded.ativo
+-        """, [TEMPLATE_AGRUPAMENTO_PADRAO, TEMPLATE_SEGMENTO_PADRAO])
++    def __init__(self, conn=None):
++        self.conn = conn if conn is not None else backend.conectar()
+ 
+     def listar_templates_ativos(self):
+         """Retorna os templates ativos como lista de dicionários (id, mensagem, descricao, segmento, ativo)."""
+         return (
+-            self.conn.execute("""
++            backend.query_df(self.conn, """
+                 SELECT id, mensagem, descricao, segmento, ativo
+                 FROM templates_whatsapp
+                 WHERE ativo = TRUE
+                 ORDER BY id
+             """)
+-            .df()
+             .to_dict("records")
+         )
+ 
+-    def _create_envios_log_table(self):
+-        """Tabela de log dos envios de WhatsApp (rastreamento de cada disparo).
 -
--## File: src/database.py
--````python
--  1: # src/database.py
--  2: import duckdb
--  3: import pandas as pd
--  4: import os
--  5: from datetime import datetime
--  6: 
--  7: class LeadDatabase:
--  8:     def __init__(self, db_path="data/leads.duckdb"):
--  9:         os.makedirs(os.path.dirname(db_path), exist_ok=True)
-- 10:         self.db_path = db_path
-- 11:         self.conn = duckdb.connect(self.db_path)
-- 12:         self._create_table()
-- 13:         self._ensure_whatsapp_columns()
-- 14: 
-- 15:     def _create_table(self):
-- 16:         self.conn.execute("""
-- 17:             CREATE TABLE IF NOT EXISTS leads (
-- 18:                 nome VARCHAR,
-- 19:                 telefone VARCHAR,
-- 20:                 tipo_telefone VARCHAR,
-- 21:                 whatsapp_link VARCHAR,
-- 22:                 instagram VARCHAR,
-- 23:                 site VARCHAR,
-- 24:                 bairro VARCHAR,
-- 25:                 cidade VARCHAR,
-- 26:                 estado VARCHAR,
-- 27:                 nicho VARCHAR,
-- 28:                 status VARCHAR DEFAULT 'ativo',
-- 29:                 data_extracao TIMESTAMP,
-- 30:                 data_envio_whatsapp TIMESTAMP,
-- 31:                 status_whatsapp VARCHAR DEFAULT 'pendente',
-- 32:                 PRIMARY KEY (nome, cidade)
-- 33:             )
-- 34:         """)
-- 35: 
-- 36:     def _ensure_whatsapp_columns(self):
-- 37:         """Adiciona as colunas de log de WhatsApp em bancos criados antes da migração."""
-- 38:         colunas = {row[1] for row in self.conn.execute("PRAGMA table_info(leads)").fetchall()}
-- 39:         if 'data_envio_whatsapp' not in colunas:
-- 40:             self.conn.execute("ALTER TABLE leads ADD COLUMN data_envio_whatsapp TIMESTAMP")
-- 41:         if 'status_whatsapp' not in colunas:
-- 42:             self.conn.execute("ALTER TABLE leads ADD COLUMN status_whatsapp VARCHAR DEFAULT 'pendente'")
-- 43: 
-- 44:     def save_leads(self, df: pd.DataFrame):
-- 45:         if df.empty:
-- 46:             return 0
-- 47:         
-- 48:         descartados_db = self.conn.execute("SELECT nome, cidade FROM leads WHERE status = 'descartado'").fetchall()
-- 49:         descartados_set = set(descartados_db)
-- 50:         
-- 51:         df = df[~df.apply(lambda row: (row['nome'], row['cidade']) in descartados_set, axis=1)]
-- 52:         
-- 53:         if df.empty:
-- 54:             print("Todos os leads coletados já foram descartados anteriormente. Pulando salvamento.")
-- 55:             return 0
-- 56:             
-- 57:         df['data_extracao'] = datetime.now()
-- 58:         
-- 59:         if 'status' not in df.columns:
-- 60:             df['status'] = 'ativo'
-- 61: 
-- 62:         self.conn.register('df_temp', df)
-- 63: 
-- 64:         # UPSERT preservando o status atual e as colunas de log do WhatsApp.
-- 65:         # Assim, re-raspar um lead já enviado NÃO apaga data_envio_whatsapp/status_whatsapp.
-- 66:         self.conn.execute("""
-- 67:             INSERT INTO leads (nome, telefone, tipo_telefone, whatsapp_link, instagram, site, bairro, cidade, estado, nicho, status, data_extracao)
-- 68:             SELECT nome, telefone, tipo_telefone, whatsapp_link, instagram, site, bairro, cidade, estado, nicho, status, data_extracao
-- 69:             FROM df_temp
-- 70:             ON CONFLICT (nome, cidade) DO UPDATE SET
-- 71:                 telefone = excluded.telefone,
-- 72:                 tipo_telefone = excluded.tipo_telefone,
-- 73:                 whatsapp_link = excluded.whatsapp_link,
-- 74:                 instagram = excluded.instagram,
-- 75:                 site = excluded.site,
-- 76:                 bairro = excluded.bairro,
-- 77:                 estado = excluded.estado,
-- 78:                 nicho = excluded.nicho,
-- 79:                 data_extracao = excluded.data_extracao
-- 80:         """)
-- 81: 
-- 82:         self.conn.unregister('df_temp')
-- 83:         return len(df)
-- 84: 
-- 85:     def get_leads_para_envio(self, limite=None):
-- 86:         """Retorna leads ativos, celulares e ainda não enviados (evita spam/fixo)."""
-- 87:         query = """
-- 88:             SELECT nome, telefone, whatsapp_link, bairro, cidade, estado, nicho
-- 89:             FROM leads
-- 90:             WHERE status = 'ativo'
-- 91:               AND tipo_telefone = 'Celular'
-- 92:               AND (status_whatsapp IS NULL OR status_whatsapp = 'pendente')
-- 93:             ORDER BY cidade, bairro, nome
-- 94:         """
-- 95:         if limite:
-- 96:             query += f" LIMIT {int(limite)}"
-- 97:         return self.conn.execute(query).df()
-- 98: 
-- 99:     def marcar_envio(self, nome, cidade, status_whatsapp):
--100:         """Registra o resultado do envio. 'data_envio_whatsapp' é gravado apenas no sucesso."""
--101:         if status_whatsapp == 'enviado':
--102:             self.conn.execute("""
--103:                 UPDATE leads
--104:                 SET status_whatsapp = ?, data_envio_whatsapp = ?
--105:                 WHERE nome = ? AND cidade = ?
--106:             """, [status_whatsapp, datetime.now(), nome, cidade])
--107:         else:
--108:             self.conn.execute("""
--109:                 UPDATE leads
--110:                 SET status_whatsapp = ?
--111:                 WHERE nome = ? AND cidade = ?
--112:             """, [status_whatsapp, nome, cidade])
--113: 
--114:     def export_to_excel(self, nicho: str, cidade: str):
--115:         df = self.conn.execute("""
--116:             SELECT nome, telefone, tipo_telefone, whatsapp_link, instagram, site, bairro, data_extracao 
--117:             FROM leads 
--118:             WHERE nicho = ? AND cidade = ? AND status = 'ativo'
--119:             ORDER BY bairro, nome
--120:         """, [nicho, cidade]).df()
--121:         
--122:         if df.empty:
--123:             print("Nenhum dado ativo para exportar.")
--124:             return
--125:             
--126:         os.makedirs("output", exist_ok=True)
--127:         nome_arquivo = f"output/leads_{nicho}_{cidade}.xlsx".replace(" ", "_").lower()
--128:         df.to_excel(nome_arquivo, index=False)
--129:         print(f"🎉 Exportação concluída: {nome_arquivo} ({len(df)} leads ativos)")
--130: 
--131:     def close(self):
--132:         self.conn.close()
--````
+-        - `lead_id`: FK lógica para `leads.lead_id` (DuckDB não aplica FK).
+-        - `telefone`: somente dígitos, igual a `leads.telefone` → chave de JOIN.
+-        - `telefone_normalizado`: formato canônico 55DDDNUMERO (quando 11 dígitos).
+-        - `payload`: retorno bruto da WAHA (JSON), útil para auditoria.
+-        """
+-        self.conn.execute("""
+-            CREATE TABLE IF NOT EXISTS whatsapp_envios_log (
+-                id INTEGER PRIMARY KEY DEFAULT nextval('seq_whatsapp_envios_log_id'),
+-                lead_id INTEGER,
+-                nome VARCHAR,
+-                cidade VARCHAR,
+-                telefone VARCHAR,
+-                telefone_normalizado VARCHAR,
+-                chat_id VARCHAR,
+-                status VARCHAR,
+-                mensagem VARCHAR,
+-                payload VARCHAR,
+-                erro VARCHAR,
+-                data_envio TIMESTAMP
+-            )
+-        """)
 -
--## File: src/whatsapp.py
--````python
--  1: # src/whatsapp.py
--  2: """Integração com a WAHA (WhatsApp HTTP API) para envio de mensagens aos leads.
--  3: 
--  4: Configuração via variáveis de ambiente:
--  5:     WAHA_API_URL   -> URL base da WAHA (padrão: http://localhost:3000)
--  6:     WAHA_API_KEY   -> chave de API da WAHA (obrigatória se a instância exigir)
--  7:     WAHA_SESSION   -> nome da sessão conectada na WAHA (padrão: "default")
--  8: 
--  9: O módulo só envia para leads:
-- 10:     - status = 'ativo'
-- 11:     - tipo_telefone = 'Celular'  (nunca fixo)
-- 12:     - ainda não enviados (status_whatsapp = 'pendente' ou NULL)
-- 13: """
-- 14: import os
-- 15: import re
-- 16: import time
-- 17: 
-- 18: import requests
-- 19: 
-- 20: from src.config import carregar_env, str_para_bool
-- 21: 
-- 22: carregar_env()
-- 23: 
-- 24: WAHA_API_URL = os.environ.get("WAHA_API_URL", "http://localhost:3000")
-- 25: WAHA_API_KEY = os.environ.get("WAHA_API_KEY", "")
-- 26: WAHA_SESSION = os.environ.get("WAHA_SESSION", "default")
-- 27: 
-- 28: # Se false, o módulo NÃO tenta enviar (desliga o envio de WhatsApp).
-- 29: WAHA_ATIVO = str_para_bool(os.environ.get("WAHA_ATIVO"), padrao=True)
-- 30: 
-- 31: # Se true, pula a coleta e vai direto para o envio (não coleta nada).
-- 32: SOMENTE_ENVIO = str_para_bool(os.environ.get("SOMENTE_ENVIO"), padrao=False)
-- 33: 
-- 34: # Intervalo (segundos) entre envios e limite de leads por campanha.
-- 35: # WAHA_LIMITE vazio = sem limite (envia todos os pendentes).
-- 36: WAHA_INTERVALO = int(os.environ.get("WAHA_INTERVALO", "13"))
-- 37: WAHA_LIMITE = os.environ.get("WAHA_LIMITE", "").strip()
-- 38: WAHA_LIMITE = int(WAHA_LIMITE) if WAHA_LIMITE else None
-- 39: 
-- 40: # Mensagem padrão (placeholder). Use {nome}, {bairro} e {cidade}.
-- 41: MENSAGEM_PADRAO = "Olá {nome}! Vi que vocês atendem no bairro {bairro}, em {cidade}. Podemos conversar?"
-- 42: 
-- 43: 
-- 44: def _normalizar_chatid(telefone):
-- 45:     """Converte o telefone salvo em um chatId do WAHA (55DDDNUMERO@c.us)."""
-- 46:     numero = re.sub(r"\D", "", str(telefone or ""))
-- 47:     if not numero:
-- 48:         return None
-- 49: 
-- 50:     # Se veio com DDI 55 e tem mais de 11 dígitos, remove o prefixo.
-- 51:     if numero.startswith("55") and len(numero) > 11:
-- 52:         numero = numero[2:]
-- 53: 
-- 54:     # Celular brasileiro tem 11 dígitos (DDD + 9 dígitos).
-- 55:     if len(numero) != 11:
-- 56:         return None
-- 57: 
-- 58:     return f"55{numero}@c.us"
-- 59: 
-- 60: 
-- 61: def _renderizar_mensagem(template, lead):
-- 62:     """Substitui {nome}, {bairro} e {cidade} de forma segura (sem quebrar com chaves soltas)."""
-- 63:     bairro = str(lead.get("bairro") or "sua região")
-- 64:     cidade = str(lead.get("cidade") or "")
-- 65:     return (
-- 66:         template
-- 67:         .replace("{nome}", str(lead.get("nome") or ""))
-- 68:         .replace("{bairro}", bairro)
-- 69:         .replace("{cidade}", cidade)
-- 70:     )
-- 71: 
-- 72: 
-- 73: def enviar_texto_waha(chat_id, texto, session=None, api_url=None, api_key=None):
-- 74:     """Envia uma mensagem de texto via WAHA."""
-- 75:     session = session or WAHA_SESSION
-- 76:     api_url = api_url or WAHA_API_URL
-- 77:     api_key = api_key if api_key is not None else WAHA_API_KEY
-- 78:     url = f"{api_url.rstrip('/')}/api/sendText"
-- 79: 
-- 80:     payload = {
-- 81:         "session": session,
-- 82:         "chatId": chat_id,
-- 83:         "text": texto,
-- 84:     }
-- 85: 
-- 86:     headers = {"Accept": "application/json", "Content-Type": "application/json"}
-- 87:     if api_key:
-- 88:         headers["X-Api-Key"] = api_key
-- 89: 
-- 90:     response = requests.post(url, json=payload, headers=headers, timeout=30)
-- 91:     response.raise_for_status()
-- 92:     return response.json()
-- 93: 
-- 94: 
-- 95: def disparar_campanha(db, mensagem_template=None, intervalo=13, limite=None):
-- 96:     """Envia mensagens para todos os leads celulares pendentes.
-- 97: 
-- 98:     - db: instância de LeadDatabase
-- 99:     - mensagem_template: texto com {nome}, {bairro}, {cidade} (usa MENSAGEM_PADRAO se None)
--100:     - intervalo: pausa em segundos entre envios (evita spam e banimento)
--101:     """
--102:     mensagem_template = mensagem_template or MENSAGEM_PADRAO
--103:     leads = db.get_leads_para_envio(limite)
--104: 
--105:     if leads.empty:
--106:         print("Nenhum lead celular pendente de envio.")
--107:         return
--108: 
--109:     total = len(leads)
--110:     print(f"Enviando para {total} lead(s) celular(es), com intervalo de {intervalo}s...")
--111: 
--112:     for i, (_, lead) in enumerate(leads.iterrows(), 1):
--113:         chat_id = _normalizar_chatid(lead.get("telefone"))
--114:         if not chat_id:
--115:             db.marcar_envio(lead["nome"], lead["cidade"], "falhou")
--116:             print(f"[{i}/{total}] {lead['nome']} - telefone inválido, marcado como falhou.")
--117:             continue
--118: 
--119:         texto = _renderizar_mensagem(mensagem_template, lead)
--120: 
--121:         try:
--122:             enviar_texto_waha(chat_id, texto)
--123:             db.marcar_envio(lead["nome"], lead["cidade"], "enviado")
--124:             print(f"[{i}/{total}] ENVIADO -> {lead['nome']} ({chat_id})")
--125:         except Exception as e:
--126:             db.marcar_envio(lead["nome"], lead["cidade"], "falhou")
--127:             print(f"[{i}/{total}] FALHOU -> {lead['nome']} ({chat_id}): {e}")
--128: 
--129:         if i < total:
--130:             time.sleep(intervalo)
--131: 
--132:     print("Campanha finalizada.")
-+33: 
-+34: ## Git force
-+35: - Enviar
-+36: git add -A; git commit -m "Atualização"; git push --force origin main
-+37: 
-+38: 
-+39: ## git forçado
-+40: - Envia
-+41: git add -A; git commit -m "Melhorias no processo de coletas v3 $(Get-Date -Format 'yyyy-MM-dd HH:mm')"; git push --force-with-lease origin main
-+42: - Recebe
-+43: git fetch --all; git reset --hard origin/main
- ````
- 
- ## File: src/localidades_db.py
-@@ -1649,6 +1328,164 @@ requirements.txt
- 110: CAPTCHA_PAUSA_GLOBAL_SEGUNDOS=180
- ````
- 
-+## File: memory/03-historico-de-mudancas.md
-+````markdown
-+  1: # 03 — Histórico de Mudanças
-+  2: 
-+  3: Registro do que mudou, por quê e o que ficou pendente. Mais recente primeiro.
-+  4: 
-+  5: ---
-+  6: 
-+  7: ## 2026-10-30
-+  8: 
-+  9: ### Templates de mensagem de WhatsApp (tabela + markdown)
-+ 10: 
-+ 11: - Nova tabela `templates_whatsapp` (`id`, `mensagem`, `descricao`, `ativo`),
-+ 12:   criada e seedada no `LeadDatabase.__init__` (idempotente, `id=1` =
-+ 13:   "Apresentação Agendamento Já").
-+ 14: - `listar_templates_ativos()` retorna só os ativos para o menu de envio.
-+ 15: - `_limpar_markdown_whatsapp` remove `**negrito**` e converte `[rótulo](url)` em
-+ 16:   texto plano antes do envio (o template usa markdown; o WhatsApp não renderiza).
-+ 17: 
-+ 18: ### Menu de envio: template + filtros + teste
-+ 19: 
-+ 20: - `enviar_whatsapp_menu()` agora: escolhe template → aplica filtros → pergunta se
-+ 21:   quer **teste de envio** → confirma e dispara.
-+ 22: - Filtros de envio (menu "FILTROS DE ENVIO"): 0 todos / 1 por número / 2 por
-+ 23:   cidade / 3 por nicho. Número aceita parte e compara só dígitos.
-+ 24: - `testar_envio()`: digita um número com DDD ou escolhe um lead pendente.
-+ 25: - `disparar_campanha` passou a aceitar `leads` (DataFrame já filtrado) — sem isso
-+ 26:   os filtros eram ignorados no disparo (ele reconsultava o banco).
-+ 27: 
-+ 28: ### Correção crítica: chatId `@lid` vs `@c.us` (WAHA)
-+ 29: 
-+ 30: - **Sintoma:** `500 Server Error` no `/api/sendText` para o número do mantenedor.
-+ 31: - **Causa:** número recente usa `@lid`; enviar `@c.us` retorna HTTP 500.
-+ 32: - **Correção:** `_resolver_chatid_waha` consulta `/api/checkNumberStatus` e usa o
-+ 33:   chatId retornado; fallback `@c.us` para números antigos.
-+ 34: - **Cache:** coluna `leads.chat_id_waha` + `salvar_chat_id_waha` — a resolução é
-+ 35:   feita uma única vez por lead (menos chamadas e reenvio mais rápido).
-+ 36: - `data_envio_whatsapp` continua gravada só no sucesso; `status_whatsapp` em
-+ 37:   `enviado`/`falhou`.
-+ 38: 
-+ 39: ---
-+ 40: 
-+ 41: ## 2026-10-29
-+ 42: 
-+ 43: ### Memória do projeto para IA
-+ 44: 
-+ 45: - Criada a pasta `memory/` com documentação densa para reduzir custo de contexto.
-+ 46: - Arquivos: `README.md`, `00-resumo-projeto.md`, `01-arquitetura-e-modulos.md`,
-+ 47:   `02-decisoes-e-armadilhas.md`, `03-historico-de-mudancas.md`,
-+ 48:   `04-como-contribuir.md` (padrões de código, logs, config, testes e docs).
-+ 49: - `README.md` limpo: removido o bloco "env temp:" (dump cru do `.env`) e
-+ 50:   adicionadas as seções 12 (memória para IA) e 13 (observação sobre configuração).
-+ 51: 
-+ 52: ### Correção: cache de bairros ignorado (`bairros_fonte`)
-+ 53: 
-+ 54: - **Sintoma:** com `LOCALIDADES_USAR_CACHE=true` e base populada, a coleta ainda
-+ 55:   consultava IBGE e Overpass.
-+ 56: - **Causa:** `localidades_db.ler_municipios()` não retornava `bairros_fonte`;
-+ 57:   `_resolver_municipio` repassava `None`, então o cache nunca era considerado.
-+ 58: - **Correção:** query passou a trazer `uf` e `bairros_fonte`; o resolver repassa
-+ 59:   o valor real.
-+ 60: - **Teste:** com as funções de rede trocadas por `AssertionError`, os bairros de
-+ 61:   Canoas (fonte `overpass`) e Bento Gonçalves (fonte `ibge`) vieram do banco.
-+ 62: 
-+ 63: ### Nome oficial do município (IBGE) na coleta
-+ 64: 
-+ 65: - `obter_municipio(cidade, uf)` confirma o município e devolve `id_municipio`,
-+ 66:   `nome` oficial e `uf`.
-+ 67: - `filtrar_cidades(cidades, termo)` compara **sem acento e sem caixa**:
-+ 68:   `canoas`, `sao leopoldo`, `CHAPECO` funcionam.
-+ 69: - `main.coletar_leads()` passa a usar o nome oficial no scraping, no banco e no
-+ 70:   nome do Excel, e imprime `Município (IBGE): Canoas-RS | código 4304606`.
-+ 71: - Lista de municípios **memoizada** por execução (`_municipios_da_uf`), evitando
-+ 72:   rebaixar a lista da UF a cada cidade (principalmente com `SALVAR=false`).
-+ 73: 
-+ 74: ### Mensagens de bairros mais honestas
-+ 75: 
-+ 76: - Antes: `IBGE retornou 0 distrito(s) útil(eis)`.
-+ 77: - Agora: `IBGE não publica bairros para Canoas-RS: o município tem apenas 1 distrito (a sede).`
-+ 78: - Motivo: a API de Localidades do IBGE **não tem bairros** (só distritos).
-+ 79: 
-+ 80: ### Aquecimento de bairros por UF (menu 4)
-+ 81: 
-+ 82: - `locations.aquecer_bairros_uf(uf, cidades=None, max_cidades=0, pausa_segundos=None)`.
-+ 83: - `localidades_db.ler_municipios_pendentes(uf)` → só `bairros_fonte IS NULL`.
-+ 84: - Retoma de onde parou; `Ctrl+C` preserva o que já foi gravado.
-+ 85: - Pausa (`AQUECER_PAUSA_SEGUNDOS`, default 2) só quando a cidade usou o OSM.
-+ 86: - Falha de rede não grava nada (`falhas` no resumo) e a cidade continua pendente.
-+ 87: - Bloqueado quando `LOCALIDADES_SALVAR=false`.
-+ 88: - Medido: AC 21 → 18 → 17 pendentes; SP 621 → 616.
-+ 89: 
-+ 90: ### Flag `LOCALIDADES_SALVAR`
-+ 91: 
-+ 92: - `false` = somente leitura: nenhuma escrita, **nem criação de tabelas**
-+ 93:   (`localidades_db.CRIAR_TABELAS = False`) e menus 3/4 desativados.
-+ 94: - Todas as escritas passam por `_salvar()`, que respeita a flag.
-+ 95: - Aviso único por execução para não poluir o log.
-+ 96: 
-+ 97: ### `.env` e `.env.example` comentados
-+ 98: 
-+ 99: - Cada variável com explicação, faixa de valores e efeito colateral.
-+100: - Tabela das 4 combinações `USAR_CACHE × SALVAR`.
-+101: - Regra explícita: comentário só em linha própria.
-+102: - Valores locais preservados (`USAR_CACHE=false` → depois `true`).
-+103: 
-+104: ### Base de localidades offline (IBGE) — menu 3
-+105: 
-+106: - Novo `src/localidades_db.py` com tabelas `localidades_estados`,
-+107:   `localidades_municipios`, `localidades_bairros` no mesmo `leads.duckdb`.
-+108: - `src/config.py` centraliza o loader do `.env` (antes duplicado no `whatsapp.py`).
-+109: - `src/locations.py` reescrito: cache → API → grava.
-+110: - Sync nacional: 27 estados, 5.571 municípios, 10.751 distritos; 643 cidades com
-+111:   bairros prontos pelo IBGE.
-+112: - Fallback OSM por cidade, gravado uma única vez.
-+113: 
-+114: ### Anti-captcha / bloqueio do Google Maps
-+115: 
-+116: - Detecção por URL `/sorry/`, seletores de captcha e textos ("tráfego incomum").
-+117: - Retry com pausa longa (`CAPTCHA_PAUSA_SEGUNDOS`) e **cooldown global**
-+118:   (`CAPTCHA_PAUSA_GLOBAL_SEGUNDOS`) entre todas as threads.
-+119: - Bloqueio persistente → aborta a área e **preserva os leads já extraídos**.
-+120: - Testado com Playwright real: página normal passa, página de captcha levanta
-+121:   `BloqueioDetectado` após `CAPTCHA_MAX_TENTATIVAS`.
-+122: 
-+123: ### Correção: menu não aparecia
-+124: 
-+125: - `src/main.py` definia `menu_interativo()` mas **nunca chamava**.
-+126: - Adicionado `if __name__ == "__main__": menu_interativo()`.
-+127: 
-+128: ### Banco DuckDB versionado
-+129: 
-+130: - `data/leads.duckdb` passou a ser versionado no Git.
-+131: - `.gitignore`: removidos `data/` e `*.duckdb` da lista de ignore; adicionados
-+132:   `*.duckdb.wal` e `*.duckdb.tmp`.
-+133: - `*.xlsx`, `*.csv`, `*.log` continuam ignorados (confirmado com
-+134:   `git check-ignore` e `git ls-files`).
-+135: - ⚠️ Comitar com o programa aberto sobe o `.duckdb` sem o `.wal` (dados
-+136:   desatualizados). Fechar antes.
-+137: 
-+138: ---
-+139: 
-+140: ## Pendências / próximos passos
-+141: 
-+142: | Item | Status |
-+143: |---|---|
-+144: | Bairros oficiais via CNEFE 2022 | **Não implementar por hora** (decisão do mantenedor) |
-+145: | Resolução automática de captcha (2Captcha/CapMonster) | Não implementado; hoje pausa e desiste da área |
-+146: | Enriquecimento de e-mail a partir dos sites | Não iniciado |
-+147: | Base de bairros offline nacional | Coberto parcialmente pelo IBGE (643 cidades) |
-+148: 
-+149: ## Problemas conhecidos (ambiente)
-+150: 
-+151: - **DBeaver aberto trava o DuckDB** → cache cai para as APIs.
-+152: - **Overpass/Nominatim instáveis** (502, timeout) → aquecimento por UF precisa de
-+153:   paciência e retomadas.
-+154: - Interprete global do mantenedor é Python 3.15; **usar `venv\Scripts\python.exe`**.
-+````
+     def salvar_log_envio(self, lead_id, nome, cidade, telefone, chat_id, status,
+                          mensagem=None, payload=None, erro=None):
+         """Grava uma linha de log de envio com os campos normalizados.
+@@ -181,53 +60,66 @@ class LeadDatabase:
+             else:
+                 payload_str = str(payload)
+ 
+-        self.conn.execute("""
++        p = backend.ph()
++        backend.execute(self.conn, f"""
+             INSERT INTO whatsapp_envios_log
+                 (lead_id, nome, cidade, telefone, telefone_normalizado, chat_id,
+                  status, mensagem, payload, erro, data_envio)
+-            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
+-        """, [lead_id, nome, cidade, telefone or None, telefone_normalizado, chat_id,
+-              status, mensagem, payload_str, erro, datetime.now()])
++            VALUES ({p}, {p}, {p}, {p}, {p}, {p}, {p}, {p}, {p}, {p}, {p})
++        """, [
++            lead_id, nome, cidade, telefone or None, telefone_normalizado, chat_id,
++            status, mensagem, payload_str, erro, datetime.now(),
++        ])
++        backend.commit(self.conn)
+ 
+     def save_leads(self, df: pd.DataFrame):
+         if df.empty:
+             return 0
+-        
+-        descartados_db = self.conn.execute("SELECT nome, cidade FROM leads WHERE status = 'descartado'").fetchall()
+-        descartados_set = set(descartados_db)
+-        
+-        df = df[~df.apply(lambda row: (row['nome'], row['cidade']) in descartados_set, axis=1)]
+-        
 +
- ## File: src/scraper.py
- ````python
-   1: # src/scraper.py
-@@ -1993,6 +1830,317 @@ requirements.txt
- 340:     return pd.DataFrame(todos_leads)
- ````
- 
-+## File: src/database.py
-+````python
-+  1: # src/database.py
-+  2: import duckdb
-+  3: import pandas as pd
-+  4: import os
-+  5: import re
-+  6: import json
-+  7: from datetime import datetime
-+  8: 
-+  9: # Template padrão de WhatsApp, usado para popular a tabela de templates.
-+ 10: # Segmento indica o nicho para o qual a mensagem foi criada (ex.: barbearias).
-+ 11: TEMPLATE_AGRUPAMENTO_PADRAO = """Opa, tudo certo?
-+ 12: 
-+ 13: Conhece o Agendamento Já? É uma plataforma 100% online para deixar sua agenda no piloto automático e acabar com a dor de cabeça de gerenciar horários pelo WhatsApp.
-+ 14: 
-+ 15: Com planos a partir de R$ 60,00 no nosso aplicativo você consegue:
-+ 16: 
-+ 17: • Personalizar com a identidade da sua marca
-+ 18: • Lembretes automatizados via Whatsapp
-+ 19: • Divulgação de horários automatizadas
-+ 20: • Controle de faturamento
-+ 21: • Pagamentos antecipados
-+ 22: 
-+ 23: Conheça nossa proposta: https://agendamentoja.com/
-+ 24: Acompanhe nosso dia a dia: https://www.instagram.com/agendamentoja_
-+ 25: 
-+ 26: Quer ver uma demonstração rápida de como funciona na prática para o seu tipo de serviço? É só me avisar!"""
-+ 27: 
-+ 28: # Segmento (nicho) padrão do template acima.
-+ 29: TEMPLATE_SEGMENTO_PADRAO = "barbearias"
-+ 30: 
-+ 31: class LeadDatabase:
-+ 32:     def __init__(self, db_path="data/leads.duckdb"):
-+ 33:         os.makedirs(os.path.dirname(db_path), exist_ok=True)
-+ 34:         self.db_path = db_path
-+ 35:         self.conn = duckdb.connect(self.db_path)
-+ 36:         self._create_sequences()
-+ 37:         self._create_table()
-+ 38:         self._ensure_whatsapp_columns()
-+ 39:         self._ensure_lead_id()
-+ 40:         self._create_templates_table()
-+ 41:         self._seed_templates()
-+ 42:         self._create_envios_log_table()
-+ 43: 
-+ 44:     def _create_sequences(self):
-+ 45:         """Sequências de ids numéricos (leads e log de envios)."""
-+ 46:         self.conn.execute("CREATE SEQUENCE IF NOT EXISTS seq_leads_id")
-+ 47:         self.conn.execute("CREATE SEQUENCE IF NOT EXISTS seq_whatsapp_envios_log_id")
-+ 48: 
-+ 49:     def _create_table(self):
-+ 50:         self.conn.execute("""
-+ 51:             CREATE TABLE IF NOT EXISTS leads (
-+ 52:                 lead_id INTEGER DEFAULT nextval('seq_leads_id'),
-+ 53:                 nome VARCHAR,
-+ 54:                 telefone VARCHAR,
-+ 55:                 tipo_telefone VARCHAR,
-+ 56:                 whatsapp_link VARCHAR,
-+ 57:                 instagram VARCHAR,
-+ 58:                 site VARCHAR,
-+ 59:                 bairro VARCHAR,
-+ 60:                 cidade VARCHAR,
-+ 61:                 estado VARCHAR,
-+ 62:                 nicho VARCHAR,
-+ 63:                 status VARCHAR DEFAULT 'ativo',
-+ 64:                 data_extracao TIMESTAMP,
-+ 65:                 data_envio_whatsapp TIMESTAMP,
-+ 66:                 status_whatsapp VARCHAR DEFAULT 'pendente',
-+ 67:                 chat_id_waha VARCHAR,
-+ 68:                 PRIMARY KEY (nome, cidade)
-+ 69:             )
-+ 70:         """)
-+ 71: 
-+ 72:     def _ensure_whatsapp_columns(self):
-+ 73:         """Adiciona as colunas de log de WhatsApp em bancos criados antes da migração."""
-+ 74:         colunas = {row[1] for row in self.conn.execute("PRAGMA table_info(leads)").fetchall()}
-+ 75:         if 'data_envio_whatsapp' not in colunas:
-+ 76:             self.conn.execute("ALTER TABLE leads ADD COLUMN data_envio_whatsapp TIMESTAMP")
-+ 77:         if 'status_whatsapp' not in colunas:
-+ 78:             self.conn.execute("ALTER TABLE leads ADD COLUMN status_whatsapp VARCHAR DEFAULT 'pendente'")
-+ 79:         if 'chat_id_waha' not in colunas:
-+ 80:             self.conn.execute("ALTER TABLE leads ADD COLUMN chat_id_waha VARCHAR")
-+ 81: 
-+ 82:     def _ensure_lead_id(self):
-+ 83:         """Adiciona o id numérico em bancos antigos (backfill automático via DEFAULT)."""
-+ 84:         colunas = {row[1] for row in self.conn.execute("PRAGMA table_info(leads)").fetchall()}
-+ 85:         if 'lead_id' not in colunas:
-+ 86:             self.conn.execute(
-+ 87:                 "ALTER TABLE leads ADD COLUMN lead_id INTEGER DEFAULT nextval('seq_leads_id')"
-+ 88:             )
-+ 89: 
-+ 90:     def _create_templates_table(self):
-+ 91:         """Tabela de templates de mensagem de WhatsApp (mensagem, descrição, segmento e ativo)."""
-+ 92:         self.conn.execute("""
-+ 93:             CREATE TABLE IF NOT EXISTS templates_whatsapp (
-+ 94:                 id INTEGER PRIMARY KEY,
-+ 95:                 mensagem VARCHAR,
-+ 96:                 descricao VARCHAR,
-+ 97:                 segmento VARCHAR,
-+ 98:                 ativo BOOLEAN DEFAULT TRUE
-+ 99:             )
-+100:         """)
-+101:         colunas = {row[1] for row in self.conn.execute("PRAGMA table_info(templates_whatsapp)").fetchall()}
-+102:         if 'segmento' not in colunas:
-+103:             self.conn.execute("ALTER TABLE templates_whatsapp ADD COLUMN segmento VARCHAR")
-+104: 
-+105:     def _seed_templates(self):
-+106:         """Garante o template padrão do Agendamento Já (id=1), atualizando se já existir."""
-+107:         self.conn.execute("""
-+108:             INSERT INTO templates_whatsapp (id, mensagem, descricao, segmento, ativo)
-+109:             VALUES (1, ?, 'Apresentação Agendamento Já', ?, TRUE)
-+110:             ON CONFLICT (id) DO UPDATE SET
-+111:                 mensagem = excluded.mensagem,
-+112:                 descricao = excluded.descricao,
-+113:                 segmento = excluded.segmento,
-+114:                 ativo = excluded.ativo
-+115:         """, [TEMPLATE_AGRUPAMENTO_PADRAO, TEMPLATE_SEGMENTO_PADRAO])
-+116: 
-+117:     def listar_templates_ativos(self):
-+118:         """Retorna os templates ativos como lista de dicionários (id, mensagem, descricao, segmento, ativo)."""
-+119:         return (
-+120:             self.conn.execute("""
-+121:                 SELECT id, mensagem, descricao, segmento, ativo
-+122:                 FROM templates_whatsapp
-+123:                 WHERE ativo = TRUE
-+124:                 ORDER BY id
-+125:             """)
-+126:             .df()
-+127:             .to_dict("records")
-+128:         )
-+129: 
-+130:     def _create_envios_log_table(self):
-+131:         """Tabela de log dos envios de WhatsApp (rastreamento de cada disparo).
-+132: 
-+133:         - `lead_id`: FK lógica para `leads.lead_id` (DuckDB não aplica FK).
-+134:         - `telefone`: somente dígitos, igual a `leads.telefone` → chave de JOIN.
-+135:         - `telefone_normalizado`: formato canônico 55DDDNUMERO (quando 11 dígitos).
-+136:         - `payload`: retorno bruto da WAHA (JSON), útil para auditoria.
-+137:         """
-+138:         self.conn.execute("""
-+139:             CREATE TABLE IF NOT EXISTS whatsapp_envios_log (
-+140:                 id INTEGER PRIMARY KEY DEFAULT nextval('seq_whatsapp_envios_log_id'),
-+141:                 lead_id INTEGER,
-+142:                 nome VARCHAR,
-+143:                 cidade VARCHAR,
-+144:                 telefone VARCHAR,
-+145:                 telefone_normalizado VARCHAR,
-+146:                 chat_id VARCHAR,
-+147:                 status VARCHAR,
-+148:                 mensagem VARCHAR,
-+149:                 payload VARCHAR,
-+150:                 erro VARCHAR,
-+151:                 data_envio TIMESTAMP
-+152:             )
-+153:         """)
-+154: 
-+155:     def salvar_log_envio(self, lead_id, nome, cidade, telefone, chat_id, status,
-+156:                          mensagem=None, payload=None, erro=None):
-+157:         """Grava uma linha de log de envio com os campos normalizados.
-+158: 
-+159:         - `lead_id`: referencia `leads.lead_id` (vínculo por PK).
-+160:         - `telefone` é reduzido a dígitos (mesma representação de `leads.telefone`),
-+161:           permitindo JOIN direto: leads.telefone = whatsapp_envios_log.telefone.
-+162:         """
-+163:         telefone = re.sub(r"\D", "", str(telefone or ""))
-+164:         telefone_normalizado = None
-+165:         if telefone.startswith("55") and len(telefone) > 11:
-+166:             base = telefone[2:]
-+167:         else:
-+168:             base = telefone
-+169:         if len(base) == 11:
-+170:             telefone_normalizado = f"55{base}"
-+171:         elif telefone:
-+172:             telefone_normalizado = telefone
-+173: 
-+174:         payload_str = None
-+175:         if payload is not None:
-+176:             if isinstance(payload, (dict, list)):
-+177:                 try:
-+178:                     payload_str = json.dumps(payload, ensure_ascii=False, default=str)
-+179:                 except Exception:
-+180:                     payload_str = str(payload)
-+181:             else:
-+182:                 payload_str = str(payload)
-+183: 
-+184:         self.conn.execute("""
-+185:             INSERT INTO whatsapp_envios_log
-+186:                 (lead_id, nome, cidade, telefone, telefone_normalizado, chat_id,
-+187:                  status, mensagem, payload, erro, data_envio)
-+188:             VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
-+189:         """, [lead_id, nome, cidade, telefone or None, telefone_normalizado, chat_id,
-+190:               status, mensagem, payload_str, erro, datetime.now()])
-+191: 
-+192:     def save_leads(self, df: pd.DataFrame):
-+193:         if df.empty:
-+194:             return 0
-+195:         
-+196:         descartados_db = self.conn.execute("SELECT nome, cidade FROM leads WHERE status = 'descartado'").fetchall()
-+197:         descartados_set = set(descartados_db)
-+198:         
-+199:         df = df[~df.apply(lambda row: (row['nome'], row['cidade']) in descartados_set, axis=1)]
-+200:         
-+201:         if df.empty:
-+202:             print("Todos os leads coletados já foram descartados anteriormente. Pulando salvamento.")
-+203:             return 0
-+204:             
-+205:         df['data_extracao'] = datetime.now()
-+206:         
-+207:         if 'status' not in df.columns:
-+208:             df['status'] = 'ativo'
-+209: 
-+210:         self.conn.register('df_temp', df)
-+211: 
-+212:         # UPSERT preservando o status atual e as colunas de log do WhatsApp.
-+213:         # Assim, re-raspar um lead já enviado NÃO apaga data_envio_whatsapp/status_whatsapp.
-+214:         self.conn.execute("""
-+215:             INSERT INTO leads (nome, telefone, tipo_telefone, whatsapp_link, instagram, site, bairro, cidade, estado, nicho, status, data_extracao)
-+216:             SELECT nome, telefone, tipo_telefone, whatsapp_link, instagram, site, bairro, cidade, estado, nicho, status, data_extracao
-+217:             FROM df_temp
-+218:             ON CONFLICT (nome, cidade) DO UPDATE SET
-+219:                 telefone = excluded.telefone,
-+220:                 tipo_telefone = excluded.tipo_telefone,
-+221:                 whatsapp_link = excluded.whatsapp_link,
-+222:                 instagram = excluded.instagram,
-+223:                 site = excluded.site,
-+224:                 bairro = excluded.bairro,
-+225:                 estado = excluded.estado,
-+226:                 nicho = excluded.nicho,
-+227:                 data_extracao = excluded.data_extracao
-+228:         """)
-+229: 
-+230:         self.conn.unregister('df_temp')
-+231:         return len(df)
-+232: 
-+233:     def get_leads_para_envio(self, limite=None, numero=None, cidade=None, nicho=None):
-+234:         """Retorna leads ativos, celulares e ainda não enviados (evita spam/fixo).
-+235: 
-+236:         Filtros opcionais:
-+237:         - numero: filtra por telefone (completo ou parte; ignora não-dígitos)
-+238:         - cidade: filtra por nome exato da cidade
-+239:         - nicho:  filtra por nicho exato
-+240:         """
-+241:         query = """
-+242:             SELECT lead_id, nome, telefone, whatsapp_link, bairro, cidade, estado, nicho, chat_id_waha
-+243:             FROM leads
-+244:             WHERE status = 'ativo'
-+245:               AND tipo_telefone = 'Celular'
-+246:               AND (status_whatsapp IS NULL OR status_whatsapp = 'pendente')
-+247:         """
-+248:         params = []
-+249:         if numero:
-+250:             numero = re.sub(r"\D", "", str(numero))
-+251:             query += " AND regexp_replace(telefone, '[^0-9]', '', 'g') LIKE ?"
-+252:             params.append(f"%{numero}%")
-+253:         if cidade:
-+254:             query += " AND cidade = ?"
-+255:             params.append(cidade)
-+256:         if nicho:
-+257:             query += " AND nicho = ?"
-+258:             params.append(nicho)
-+259:         query += " ORDER BY cidade, bairro, nome"
-+260:         if limite:
-+261:             query += " LIMIT ?"
-+262:             params.append(int(limite))
-+263:         return self.conn.execute(query, params).df()
-+264: 
-+265:     def salvar_chat_id_waha(self, nome, cidade, chat_id):
-+266:         """Cacheia o chatId resolvido (ex.: 143172869029943@lid) para não repetir
-+267:         a chamada ao /api/checkNumberStatus em envios futuros."""
-+268:         self.conn.execute("""
-+269:             UPDATE leads
-+270:             SET chat_id_waha = ?
-+271:             WHERE nome = ? AND cidade = ?
-+272:         """, [chat_id, nome, cidade])
-+273: 
-+274:     def marcar_envio(self, nome, cidade, status_whatsapp):
-+275:         """Registra o resultado do envio. 'data_envio_whatsapp' é gravado apenas no sucesso."""
-+276:         if status_whatsapp == 'enviado':
-+277:             self.conn.execute("""
-+278:                 UPDATE leads
-+279:                 SET status_whatsapp = ?, data_envio_whatsapp = ?
-+280:                 WHERE nome = ? AND cidade = ?
-+281:             """, [status_whatsapp, datetime.now(), nome, cidade])
-+282:         else:
-+283:             self.conn.execute("""
-+284:                 UPDATE leads
-+285:                 SET status_whatsapp = ?
-+286:                 WHERE nome = ? AND cidade = ?
-+287:             """, [status_whatsapp, nome, cidade])
-+288: 
-+289:     def export_to_excel(self, nicho: str, cidade: str):
-+290:         df = self.conn.execute("""
-+291:             SELECT nome, telefone, tipo_telefone, whatsapp_link, instagram, site, bairro, data_extracao 
-+292:             FROM leads 
-+293:             WHERE nicho = ? AND cidade = ? AND status = 'ativo'
-+294:             ORDER BY bairro, nome
-+295:         """, [nicho, cidade]).df()
-+296:         
-+297:         if df.empty:
-+298:             print("Nenhum dado ativo para exportar.")
-+299:             return
-+300:             
-+301:         os.makedirs("output", exist_ok=True)
-+302:         nome_arquivo = f"output/leads_{nicho}_{cidade}.xlsx".replace(" ", "_").lower()
-+303:         df.to_excel(nome_arquivo, index=False)
-+304:         print(f"🎉 Exportação concluída: {nome_arquivo} ({len(df)} leads ativos)")
-+305: 
-+306:     def close(self):
-+307:         self.conn.close()
-+````
++        descartados = set(backend.query_all(
++            self.conn, "SELECT nome, cidade FROM leads WHERE status = 'descartado'"
++        ))
++        df = df[~df.apply(lambda row: (row['nome'], row['cidade']) in descartados, axis=1)]
 +
- ## File: src/locations.py
- ````python
-   1: # src/locations.py
-@@ -2602,6 +2750,248 @@ requirements.txt
- 605:     return True
- ````
- 
-+## File: src/whatsapp.py
-+````python
-+  1: # src/whatsapp.py
-+  2: """Integração com a WAHA (WhatsApp HTTP API) para envio de mensagens aos leads.
-+  3: 
-+  4: Configuração via variáveis de ambiente:
-+  5:     WAHA_API_URL   -> URL base da WAHA (padrão: http://localhost:3000)
-+  6:     WAHA_API_KEY   -> chave de API da WAHA (obrigatória se a instância exigir)
-+  7:     WAHA_SESSION   -> nome da sessão conectada na WAHA (padrão: "default")
-+  8: 
-+  9: O módulo só envia para leads:
-+ 10:     - status = 'ativo'
-+ 11:     - tipo_telefone = 'Celular'  (nunca fixo)
-+ 12:     - ainda não enviados (status_whatsapp = 'pendente' ou NULL)
-+ 13: """
-+ 14: import os
-+ 15: import re
-+ 16: import time
-+ 17: 
-+ 18: import requests
-+ 19: 
-+ 20: from src.config import carregar_env, str_para_bool
-+ 21: 
-+ 22: carregar_env()
-+ 23: 
-+ 24: WAHA_API_URL = os.environ.get("WAHA_API_URL", "http://localhost:3000")
-+ 25: WAHA_API_KEY = os.environ.get("WAHA_API_KEY", "")
-+ 26: WAHA_SESSION = os.environ.get("WAHA_SESSION", "default")
-+ 27: 
-+ 28: # Se false, o módulo NÃO tenta enviar (desliga o envio de WhatsApp).
-+ 29: WAHA_ATIVO = str_para_bool(os.environ.get("WAHA_ATIVO"), padrao=True)
-+ 30: 
-+ 31: # Se true, pula a coleta e vai direto para o envio (não coleta nada).
-+ 32: SOMENTE_ENVIO = str_para_bool(os.environ.get("SOMENTE_ENVIO"), padrao=False)
-+ 33: 
-+ 34: # Intervalo (segundos) entre envios e limite de leads por campanha.
-+ 35: # WAHA_LIMITE vazio = sem limite (envia todos os pendentes).
-+ 36: WAHA_INTERVALO = int(os.environ.get("WAHA_INTERVALO", "13"))
-+ 37: WAHA_LIMITE = os.environ.get("WAHA_LIMITE", "").strip()
-+ 38: WAHA_LIMITE = int(WAHA_LIMITE) if WAHA_LIMITE else None
-+ 39: 
-+ 40: # Mensagem padrão (placeholder). Use {nome}, {bairro} e {cidade}.
-+ 41: MENSAGEM_PADRAO = "Olá {nome}! Vi que vocês atendem no bairro {bairro}, em {cidade}. Podemos conversar?"
-+ 42: 
-+ 43: 
-+ 44: def _normalizar_chatid(telefone):
-+ 45:     """Converte o telefone salvo em um chatId clássico do WAHA (55DDDNUMERO@c.us)."""
-+ 46:     numero = re.sub(r"\D", "", str(telefone or ""))
-+ 47:     if not numero:
-+ 48:         return None
-+ 49: 
-+ 50:     # Se veio com DDI 55 e tem mais de 11 dígitos, remove o prefixo.
-+ 51:     if numero.startswith("55") and len(numero) > 11:
-+ 52:         numero = numero[2:]
-+ 53: 
-+ 54:     # Celular brasileiro tem 11 dígitos (DDD + 9 dígitos).
-+ 55:     if len(numero) != 11:
-+ 56:         return None
-+ 57: 
-+ 58:     return f"55{numero}@c.us"
-+ 59: 
-+ 60: 
-+ 61: def _resolver_chatid_waha(telefone, session=None, api_url=None, api_key=None):
-+ 62:     """Resolve o chatId correto via /api/checkNumberStatus.
-+ 63: 
-+ 64:     Números recentes no WhatsApp usam o formato @lid (hidden user ID) em vez do
-+ 65:     clássico @c.us. Enviar com @c.us para esses números retorna HTTP 500.
-+ 66:     A WAHA responde o chatId certo via checkNumberStatus; usamos ele e, se a
-+ 67:     consulta falhar ou o número não existir, caímos no formato clássico @c.us.
-+ 68:     """
-+ 69:     session = session or WAHA_SESSION
-+ 70:     api_url = api_url or WAHA_API_URL
-+ 71:     api_key = api_key if api_key is not None else WAHA_API_KEY
-+ 72: 
-+ 73:     numero = re.sub(r"\D", "", str(telefone or ""))
-+ 74:     if not numero:
-+ 75:         return None
-+ 76: 
-+ 77:     if numero.startswith("55") and len(numero) > 11:
-+ 78:         numero = numero[2:]
-+ 79:     if len(numero) != 11:
-+ 80:         return None
-+ 81: 
-+ 82:     telefone_internacional = f"55{numero}"
-+ 83: 
-+ 84:     headers = {"Accept": "application/json"}
-+ 85:     if api_key:
-+ 86:         headers["X-Api-Key"] = api_key
-+ 87: 
-+ 88:     url = f"{api_url.rstrip('/')}/api/checkNumberStatus"
-+ 89:     params = {"session": session, "phone": telefone_internacional}
-+ 90: 
-+ 91:     try:
-+ 92:         response = requests.get(url, params=params, headers=headers, timeout=20)
-+ 93:         response.raise_for_status()
-+ 94:         dados = response.json()
-+ 95:         if dados.get("numberExists") and dados.get("chatId"):
-+ 96:             return dados["chatId"]
-+ 97:     except Exception:
-+ 98:         pass
-+ 99: 
-+100:     # Fallback: formato clássico @c.us (funciona para números mais antigos).
-+101:     return f"{telefone_internacional}@c.us"
-+102: 
-+103: 
-+104: def _limpar_markdown_whatsapp(texto):
-+105:     """Remove marcação de markdown (negrito e links) antes de enviar ao WhatsApp.
-+106: 
-+107:     - **texto**  -> texto
-+108:     - [rótulo](url) -> url (quando o rótulo já é a própria URL) ou "rótulo (url)"
-+109:     """
-+110:     texto = re.sub(r"\*\*([^*]+)\*\*", r"\1", texto)
-+111: 
-+112:     def _sub_link(match):
-+113:         rotulo = match.group(1)
-+114:         url = match.group(2)
-+115:         if rotulo.strip() == url.strip():
-+116:             return url
-+117:         return f"{rotulo} ({url})"
-+118: 
-+119:     return re.sub(r"\[([^\]]+)\]\(([^)]+)\)", _sub_link, texto)
-+120: 
-+121: 
-+122: def _renderizar_mensagem(template, lead):
-+123:     """Substitui {nome}, {bairro} e {cidade} de forma segura e limpa o markdown."""
-+124:     bairro = str(lead.get("bairro") or "sua região")
-+125:     cidade = str(lead.get("cidade") or "")
-+126:     texto = (
-+127:         template
-+128:         .replace("{nome}", str(lead.get("nome") or ""))
-+129:         .replace("{bairro}", bairro)
-+130:         .replace("{cidade}", cidade)
-+131:     )
-+132:     return _limpar_markdown_whatsapp(texto)
-+133: 
-+134: 
-+135: def enviar_texto_waha(chat_id, texto, session=None, api_url=None, api_key=None):
-+136:     """Envia uma mensagem de texto via WAHA."""
-+137:     session = session or WAHA_SESSION
-+138:     api_url = api_url or WAHA_API_URL
-+139:     api_key = api_key if api_key is not None else WAHA_API_KEY
-+140:     url = f"{api_url.rstrip('/')}/api/sendText"
-+141: 
-+142:     payload = {
-+143:         "session": session,
-+144:         "chatId": chat_id,
-+145:         "text": texto,
-+146:     }
-+147: 
-+148:     headers = {"Accept": "application/json", "Content-Type": "application/json"}
-+149:     if api_key:
-+150:         headers["X-Api-Key"] = api_key
-+151: 
-+152:     response = requests.post(url, json=payload, headers=headers, timeout=30)
-+153:     response.raise_for_status()
-+154:     return response.json()
-+155: 
-+156: 
-+157: def enviar_texto_numero(numero, texto, session=None, api_url=None, api_key=None):
-+158:     """Envia uma mensagem de texto para um número bruto (com DDD), já normalizado.
-+159: 
-+160:     Útil para o envio de teste, sem precisar de um lead no banco.
-+161:     """
-+162:     texto = _limpar_markdown_whatsapp(texto)
-+163:     chat_id = _resolver_chatid_waha(numero, session=session, api_url=api_url, api_key=api_key)
-+164:     if not chat_id:
-+165:         raise ValueError(f"Número inválido para envio: {numero}")
-+166:     return enviar_texto_waha(chat_id, texto, session=session, api_url=api_url, api_key=api_key)
-+167: 
-+168: 
-+169: def disparar_campanha(db, mensagem_template=None, intervalo=13, limite=None, leads=None):
-+170:     """Envia mensagens para os leads celulares pendentes.
-+171: 
-+172:     - db: instância de LeadDatabase
-+173:     - mensagem_template: texto com {nome}, {bairro}, {cidade} (usa MENSAGEM_PADRAO se None)
-+174:     - intervalo: pausa em segundos entre envios (evita spam e banimento)
-+175:     - leads: DataFrame opcional já filtrado; se None, busca pendentes (com limite)
-+176:     """
-+177:     mensagem_template = mensagem_template or MENSAGEM_PADRAO
-+178:     if leads is None:
-+179:         leads = db.get_leads_para_envio(limite)
-+180: 
-+181:     if leads.empty:
-+182:         print("Nenhum lead celular pendente de envio.")
-+183:         return
-+184: 
-+185:     total = len(leads)
-+186:     print(f"Enviando para {total} lead(s) celular(es), com intervalo de {intervalo}s...")
-+187: 
-+188:     for i, (_, lead) in enumerate(leads.iterrows(), 1):
-+189:         texto = _renderizar_mensagem(mensagem_template, lead)
-+190:         lead_id = lead.get("lead_id")
-+191:         telefone = lead.get("telefone")
-+192:         nome = lead.get("nome")
-+193:         cidade = lead.get("cidade")
-+194: 
-+195:         chat_id = lead.get("chat_id_waha")
-+196:         if not chat_id:
-+197:             # Resolve (e cacheia) o chatId uma única vez por lead. Números novos
-+198:             # usam @lid; a consulta ao checkNumberStatus é feita só na primeira vez.
-+199:             chat_id = _resolver_chatid_waha(telefone)
-+200:             if chat_id:
-+201:                 db.salvar_chat_id_waha(nome, cidade, chat_id)
-+202: 
-+203:         if not chat_id:
-+204:             db.marcar_envio(nome, cidade, "falhou")
-+205:             db.salvar_log_envio(
-+206:                 lead_id, nome, cidade, telefone, chat_id, "falhou",
-+207:                 mensagem=texto, erro="telefone inválido",
-+208:             )
-+209:             print(f"[{i}/{total}] {nome} - telefone inválido, marcado como falhou.")
-+210:             continue
-+211: 
-+212:         try:
-+213:             resposta = enviar_texto_waha(chat_id, texto)
-+214:             db.marcar_envio(nome, cidade, "enviado")
-+215:             db.salvar_log_envio(
-+216:                 lead_id, nome, cidade, telefone, chat_id, "enviado",
-+217:                 mensagem=texto, payload=resposta,
-+218:             )
-+219:             print(f"[{i}/{total}] ENVIADO -> {nome} ({chat_id})")
-+220:         except Exception as e:
-+221:             payload_erro = None
-+222:             if getattr(e, "response", None) is not None:
-+223:                 try:
-+224:                     payload_erro = e.response.text
-+225:                 except Exception:
-+226:                     payload_erro = None
-+227:             erro = f"{type(e).__name__}: {e}"
-+228:             db.marcar_envio(nome, cidade, "falhou")
-+229:             db.salvar_log_envio(
-+230:                 lead_id, nome, cidade, telefone, chat_id, "falhou",
-+231:                 mensagem=texto, payload=payload_erro, erro=erro,
-+232:             )
-+233:             print(f"[{i}/{total}] FALHOU -> {nome} ({chat_id}): {erro}")
-+234: 
-+235:         if i < total:
-+236:             time.sleep(intervalo)
-+237: 
-+238:     print("Campanha finalizada.")
-+````
+         if df.empty:
+             print("Todos os leads coletados já foram descartados anteriormente. Pulando salvamento.")
+             return 0
+-            
 +
- ## File: .gitignore
- ````
-  1: # Dados: o banco DuckDB É versionado (data/leads.duckdb).
-@@ -2637,219 +3027,6 @@ requirements.txt
- 31: Thumbs.db
- ````
- 
--## File: src/main.py
--````python
--  1: # src/main.py
--  2: import sys
--  3: import os
--  4: 
--  5: sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
--  6: 
--  7: from src.locations import (
--  8:     obter_estados,
--  9:     obter_cidades,
-- 10:     obter_termos_busca,
-- 11:     obter_municipio,
-- 12:     filtrar_cidades,
-- 13:     sincronizar_base_localidades,
-- 14:     listar_municipios_pendentes,
-- 15:     aquecer_bairros_uf,
-- 16:     SALVAR as LOCALIDADES_SALVAR,
-- 17: )
-- 18: from src.scraper import rodar_scraper_multithread
-- 19: from src.database import LeadDatabase
-- 20: from src.whatsapp import (
-- 21:     disparar_campanha,
-- 22:     MENSAGEM_PADRAO,
-- 23:     WAHA_INTERVALO,
-- 24:     WAHA_LIMITE,
-- 25:     WAHA_ATIVO,
-- 26:     SOMENTE_ENVIO,
-- 27: )
-- 28: 
-- 29: 
-- 30: def coletar_leads():
-- 31:     df_estados = obter_estados()
-- 32:     if df_estados.empty:
-- 33:         return
-- 34: 
-- 35:     uf_escolhida = input("Digite a UF (ex: RS, SP, RJ): ").strip().upper()
-- 36:     if uf_escolhida not in df_estados['uf'].values:
-- 37:         print("UF inválida.")
-- 38:         return
-- 39: 
-- 40:     cidades = obter_cidades(uf_escolhida)
-- 41:     termo_cidade = input("Digite o nome da cidade: ").strip()
-- 42:     cidades_filtradas = filtrar_cidades(cidades, termo_cidade)
-- 43: 
-- 44:     if not cidades_filtradas:
-- 45:         print("Cidade não encontrada.")
-- 46:         return
-- 47:     elif len(cidades_filtradas) > 1:
-- 48:         cidade_escolhida = input(
-- 49:             f"Várias encontradas ({', '.join(cidades_filtradas[:3])}...). Digite o nome exato: "
-- 50:         ).strip()
-- 51:         exatos = filtrar_cidades(cidades, cidade_escolhida)
-- 52:         cidade_escolhida = exatos[0] if exatos else cidade_escolhida
-- 53:     else:
-- 54:         cidade_escolhida = cidades_filtradas[0]
-- 55: 
-- 56:     # Confirma o município no IBGE e passa a usar o nome oficial (com acentos).
-- 57:     municipio = obter_municipio(cidade_escolhida, uf_escolhida)
-- 58:     if municipio:
-- 59:         cidade_escolhida = municipio["nome"]
-- 60:         print(f"Município (IBGE): {cidade_escolhida}-{uf_escolhida} | código {municipio['id_municipio']}")
-- 61:     else:
-- 62:         print(f"Aviso: {cidade_escolhida}-{uf_escolhida} não foi confirmado no IBGE.")
-- 63: 
-- 64:     nicho = input(f"\nQual o nicho para {cidade_escolhida}-{uf_escolhida}? ").strip().lower()
-- 65: 
-- 66:     termos_busca = obter_termos_busca(cidade_escolhida, uf_escolhida)
-- 67: 
-- 68:     mostrar_navegador = input("\nVer o navegador? (S/N): ").strip().upper() == 'S'
-- 69: 
-- 70:     print("\nIniciando extração...")
-- 71:     db = LeadDatabase()
-- 72: 
-- 73:     df_resultados = rodar_scraper_multithread(
-- 74:         nicho=nicho,
-- 75:         cidade=cidade_escolhida,
-- 76:         uf=uf_escolhida,
-- 77:         termos_lista=termos_busca,
-- 78:         mostrar_navegador=mostrar_navegador,
-- 79:         save_callback=db.save_leads,  # salvamento incremental (UPSERT) a cada área concluída
-- 80:     )
-- 81: 
-- 82:     if not df_resultados.empty:
-- 83:         print("\nLeads salvos incrementalmente no DuckDB (UPSERT).")
-- 84:         db.export_to_excel(nicho, cidade_escolhida)
-- 85:     else:
-- 86:         print("Nenhum dado extraído.")
-- 87: 
-- 88:     db.close()
-- 89: 
-- 90: 
-- 91: def enviar_whatsapp_menu():
-- 92:     print("\n=== ENVIO WHATSAPP (WAHA) ===")
-- 93: 
-- 94:     if not WAHA_ATIVO:
-- 95:         print("Envio de WhatsApp desativado (WAHA_ATIVO=false no .env).")
-- 96:         return
-- 97: 
-- 98:     db = LeadDatabase()
-- 99: 
--100:     pendentes = db.get_leads_para_envio(limite=WAHA_LIMITE)
--101:     if pendentes.empty:
--102:         print("Nenhum lead celular pendente de envio.")
--103:         db.close()
--104:         return
--105: 
--106:     print(f"{len(pendentes)} lead(s) celular(es) pendentes (fixos são ignorados).")
--107:     if WAHA_LIMITE:
--108:         print(f"Limite configurado: {WAHA_LIMITE} lead(s) por campanha.")
--109: 
--110:     print(f"Mensagem padrão: {MENSAGEM_PADRAO}")
--111:     mensagem = input("Digite a mensagem (ou Enter para usar a padrão): ").strip()
--112:     if not mensagem:
--113:         mensagem = MENSAGEM_PADRAO
--114: 
--115:     confirmar = input(f"Enviar para {len(pendentes)} lead(s)? (S/N): ").strip().upper()
--116:     if confirmar != 'S':
--117:         print("Envio cancelado.")
--118:         db.close()
--119:         return
--120: 
--121:     disparar_campanha(db, mensagem_template=mensagem, intervalo=WAHA_INTERVALO, limite=WAHA_LIMITE)
--122:     db.close()
--123: 
--124: 
--125: def aquecer_bairros_menu():
--126:     """Prepara o cache de bairros de uma UF inteira (sem raspar leads)."""
--127:     print("\n=== AQUECER BAIRROS DE UMA UF ===")
--128: 
--129:     if not LOCALIDADES_SALVAR:
--130:         print("LOCALIDADES_SALVAR=false: o aquecimento está desativado.")
--131:         print("Ative a flag LOCALIDADES_SALVAR no .env para gravar os bairros.")
--132:         return
--133: 
--134:     print("Resolve e grava os bairros de todas as cidades da UF, uma única vez.")
--135:     print("Depois disso a coleta por cidade não consulta mais IBGE/OSM.")
--136: 
--137:     df_estados = obter_estados()
--138:     if df_estados.empty:
--139:         print("Não foi possível obter a lista de estados.")
--140:         return
--141: 
--142:     uf = input("Digite a UF (ex: RS, SP, RJ): ").strip().upper()
--143:     if uf not in df_estados['uf'].values:
--144:         print("UF inválida.")
--145:         return
--146: 
--147:     print(f"\nVerificando quais cidades de {uf} ainda precisam de bairros...")
--148:     pendentes = listar_municipios_pendentes(uf)
--149:     if not pendentes:
--150:         print(f"Todas as cidades de {uf} já estão na base local. Nada a fazer.")
--151:         return
--152: 
--153:     print(f"{len(pendentes)} cidade(s) pendente(s) em {uf}.")
--154:     print("As cidades cobertas pelo IBGE são instantâneas; as demais usam o")
--155:     print("OpenStreetMap (Nominatim + Overpass), com pausa entre elas.")
--156: 
--157:     limite = input("Quantas cidades processar agora? (Enter = todas): ").strip()
--158:     max_cidades = 0
--159:     if limite:
--160:         try:
--161:             max_cidades = max(1, int(limite))
--162:         except ValueError:
--163:             print("Valor inválido. Usando todas.")
--164:             max_cidades = 0
--165: 
--166:     previstas = min(max_cidades, len(pendentes)) if max_cidades else len(pendentes)
--167:     confirmar = input(f"Processar {previstas} cidade(s)? (S/N): ").strip().upper()
--168:     if confirmar != 'S':
--169:         print("Operação cancelada.")
--170:         return
--171: 
--172:     aquecer_bairros_uf(uf, cidades=pendentes, max_cidades=max_cidades)
--173: 
--174: 
--175: def menu_interativo():
--176:     # Flag de linha de comando: `python src/main.py --so-enviar` pula a coleta
--177:     # e vai direto para o envio (equivale a SOMENTE_ENVIO=true no .env).
--178:     so_enviar_cli = "--so-enviar" in sys.argv
--179: 
--180:     if SOMENTE_ENVIO or so_enviar_cli:
--181:         enviar_whatsapp_menu()
--182:         return
--183: 
--184:     while True:
--185:         print("\n=== MAP SCRAPER ===")
--186:         print("1 - Coletar leads")
--187:         print("2 - Enviar mensagens WhatsApp")
--188:         print("3 - Sincronizar base de localidades (IBGE)")
--189:         print("4 - Aquecer bairros de uma UF (OpenStreetMap)")
--190:         print("5 - Sair")
--191:         opcao = input("Escolha uma opção: ").strip()
--192: 
--193:         if opcao == "1":
--194:             coletar_leads()
--195:         elif opcao == "2":
--196:             enviar_whatsapp_menu()
--197:         elif opcao == "3":
--198:             sincronizar_base_localidades()
--199:         elif opcao == "4":
--200:             aquecer_bairros_menu()
--201:         elif opcao == "5":
--202:             print("Até mais!")
--203:             break
--204:         else:
--205:             print("Opção inválida.")
--206: 
--207: 
--208: if __name__ == "__main__":
--209:     menu_interativo()
--````
++        df = df.copy()
+         df['data_extracao'] = datetime.now()
+-        
+         if 'status' not in df.columns:
+             df['status'] = 'ativo'
+ 
+-        self.conn.register('df_temp', df)
++        colunas = [
++            'nome', 'telefone', 'tipo_telefone', 'whatsapp_link', 'instagram',
++            'site', 'bairro', 'cidade', 'estado', 'nicho', 'status', 'data_extracao',
++        ]
++        linhas = [
++            tuple(backend._valor(r.get(c)) for c in colunas)
++            for r in df.to_dict("records")
++        ]
+ 
+         # UPSERT preservando o status atual e as colunas de log do WhatsApp.
+         # Assim, re-raspar um lead já enviado NÃO apaga data_envio_whatsapp/status_whatsapp.
+-        self.conn.execute("""
+-            INSERT INTO leads (nome, telefone, tipo_telefone, whatsapp_link, instagram, site, bairro, cidade, estado, nicho, status, data_extracao)
+-            SELECT nome, telefone, tipo_telefone, whatsapp_link, instagram, site, bairro, cidade, estado, nicho, status, data_extracao
+-            FROM df_temp
+-            ON CONFLICT (nome, cidade) DO UPDATE SET
+-                telefone = excluded.telefone,
+-                tipo_telefone = excluded.tipo_telefone,
+-                whatsapp_link = excluded.whatsapp_link,
+-                instagram = excluded.instagram,
+-                site = excluded.site,
+-                bairro = excluded.bairro,
+-                estado = excluded.estado,
+-                nicho = excluded.nicho,
+-                data_extracao = excluded.data_extracao
+-        """)
 -
- ## File: README.md
- ````markdown
-   1: Documentação do Projeto: MAP SCRAPER
-@@ -3183,6 +3360,324 @@ requirements.txt
- 329:     do valor.
- ````
- 
-+## File: src/main.py
-+````python
-+  1: # src/main.py
-+  2: import sys
-+  3: import os
-+  4: 
-+  5: sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
-+  6: 
-+  7: from src.locations import (
-+  8:     obter_estados,
-+  9:     obter_cidades,
-+ 10:     obter_termos_busca,
-+ 11:     obter_municipio,
-+ 12:     filtrar_cidades,
-+ 13:     sincronizar_base_localidades,
-+ 14:     listar_municipios_pendentes,
-+ 15:     aquecer_bairros_uf,
-+ 16:     SALVAR as LOCALIDADES_SALVAR,
-+ 17: )
-+ 18: from src.scraper import rodar_scraper_multithread
-+ 19: from src.database import LeadDatabase
-+ 20: from src.whatsapp import (
-+ 21:     disparar_campanha,
-+ 22:     enviar_texto_numero,
-+ 23:     WAHA_INTERVALO,
-+ 24:     WAHA_LIMITE,
-+ 25:     WAHA_ATIVO,
-+ 26:     SOMENTE_ENVIO,
-+ 27: )
-+ 28: 
-+ 29: 
-+ 30: def coletar_leads():
-+ 31:     df_estados = obter_estados()
-+ 32:     if df_estados.empty:
-+ 33:         return
-+ 34: 
-+ 35:     uf_escolhida = input("Digite a UF (ex: RS, SP, RJ): ").strip().upper()
-+ 36:     if uf_escolhida not in df_estados['uf'].values:
-+ 37:         print("UF inválida.")
-+ 38:         return
-+ 39: 
-+ 40:     cidades = obter_cidades(uf_escolhida)
-+ 41:     termo_cidade = input("Digite o nome da cidade: ").strip()
-+ 42:     cidades_filtradas = filtrar_cidades(cidades, termo_cidade)
-+ 43: 
-+ 44:     if not cidades_filtradas:
-+ 45:         print("Cidade não encontrada.")
-+ 46:         return
-+ 47:     elif len(cidades_filtradas) > 1:
-+ 48:         cidade_escolhida = input(
-+ 49:             f"Várias encontradas ({', '.join(cidades_filtradas[:3])}...). Digite o nome exato: "
-+ 50:         ).strip()
-+ 51:         exatos = filtrar_cidades(cidades, cidade_escolhida)
-+ 52:         cidade_escolhida = exatos[0] if exatos else cidade_escolhida
-+ 53:     else:
-+ 54:         cidade_escolhida = cidades_filtradas[0]
-+ 55: 
-+ 56:     # Confirma o município no IBGE e passa a usar o nome oficial (com acentos).
-+ 57:     municipio = obter_municipio(cidade_escolhida, uf_escolhida)
-+ 58:     if municipio:
-+ 59:         cidade_escolhida = municipio["nome"]
-+ 60:         print(f"Município (IBGE): {cidade_escolhida}-{uf_escolhida} | código {municipio['id_municipio']}")
-+ 61:     else:
-+ 62:         print(f"Aviso: {cidade_escolhida}-{uf_escolhida} não foi confirmado no IBGE.")
-+ 63: 
-+ 64:     nicho = input(f"\nQual o nicho para {cidade_escolhida}-{uf_escolhida}? ").strip().lower()
-+ 65: 
-+ 66:     termos_busca = obter_termos_busca(cidade_escolhida, uf_escolhida)
-+ 67: 
-+ 68:     mostrar_navegador = input("\nVer o navegador? (S/N): ").strip().upper() == 'S'
-+ 69: 
-+ 70:     print("\nIniciando extração...")
-+ 71:     db = LeadDatabase()
-+ 72: 
-+ 73:     df_resultados = rodar_scraper_multithread(
-+ 74:         nicho=nicho,
-+ 75:         cidade=cidade_escolhida,
-+ 76:         uf=uf_escolhida,
-+ 77:         termos_lista=termos_busca,
-+ 78:         mostrar_navegador=mostrar_navegador,
-+ 79:         save_callback=db.save_leads,  # salvamento incremental (UPSERT) a cada área concluída
-+ 80:     )
-+ 81: 
-+ 82:     if not df_resultados.empty:
-+ 83:         print("\nLeads salvos incrementalmente no DuckDB (UPSERT).")
-+ 84:         db.export_to_excel(nicho, cidade_escolhida)
-+ 85:     else:
-+ 86:         print("Nenhum dado extraído.")
-+ 87: 
-+ 88:     db.close()
-+ 89: 
-+ 90: 
-+ 91: def _confirmar(texto):
-+ 92:     """Pergunta S/N e retorna True para respostas afirmativas."""
-+ 93:     return input(texto).strip().upper() in ("S", "SIM", "Y", "YES")
-+ 94: 
-+ 95: 
-+ 96: def _escolher_template(templates):
-+ 97:     """Lista os templates ativos e retorna a mensagem escolhida pelo usuário."""
-+ 98:     print("\nTemplates ativos:")
-+ 99:     for t in templates:
-+100:         segmento = t.get("segmento")
-+101:         sufixo = f"  [{segmento}]" if segmento else ""
-+102:         print(f"  {t['id']} - {t['descricao']}{sufixo}")
-+103: 
-+104:     escolha = input("Escolha o template (Enter = primeiro): ").strip()
-+105:     if not escolha:
-+106:         return templates[0]["mensagem"]
-+107: 
-+108:     for t in templates:
-+109:         if str(t["id"]) == escolha:
-+110:             return t["mensagem"]
-+111: 
-+112:     print("Opção inválida. Usando o primeiro template.")
-+113:     return templates[0]["mensagem"]
-+114: 
-+115: 
-+116: def _escolher_filtros():
-+117:     """Pergunta os filtros de envio; Enter = sem filtro (todos os leads)."""
-+118:     print("\n=== FILTROS DE ENVIO ===")
-+119:     print("0 - Todos (sem filtro)")
-+120:     print("1 - Por número")
-+121:     print("2 - Por cidade")
-+122:     print("3 - Por nicho")
-+123:     opcao = input("Escolha um filtro (Enter = 0): ").strip() or "0"
-+124: 
-+125:     numero = cidade = nicho = None
-+126:     if opcao == "1":
-+127:         numero = input("Número (completo ou parte): ").strip() or None
-+128:     elif opcao == "2":
-+129:         cidade = input("Cidade: ").strip() or None
-+130:     elif opcao == "3":
-+131:         nicho = input("Nicho: ").strip() or None
-+132:     elif opcao != "0":
-+133:         print("Opção inválida. Usando 'Todos'.")
-+134:     return numero, cidade, nicho
-+135: 
-+136: 
-+137: def testar_envio(db, mensagem, pendentes=None):
-+138:     """Envia um teste para um número digitado ou para um lead pendente.
-+139: 
-+140:     `pendentes` (opcional): DataFrame já filtrado; se None, busca até 10 pendentes.
-+141:     """
-+142:     print("\n--- TESTE DE ENVIO ---")
-+143:     print("1 - Digitar um número de teste")
-+144:     print("2 - Escolher um lead pendente")
-+145:     opcao = input("Escolha: ").strip()
-+146: 
-+147:     numero = None
-+148:     if opcao == "1":
-+149:         numero = input("Digite o número com DDD (ex: 51999998888): ").strip()
-+150:     elif opcao == "2":
-+151:         if pendentes is None:
-+152:             pendentes = db.get_leads_para_envio(limite=10)
-+153:         if pendentes.empty:
-+154:             print("Nenhum lead pendente para testar.")
-+155:             return
-+156:         amostra = pendentes.head(10)
-+157:         print("Leads pendentes:")
-+158:         for i, (_, lead) in enumerate(amostra.iterrows(), 1):
-+159:             print(f"  {i} - {lead['nome']} ({lead['telefone']})")
-+160:         escolha = input("Escolha o número do lead: ").strip()
-+161:         if not escolha.isdigit() or not (1 <= int(escolha) <= len(amostra)):
-+162:             print("Escolha inválida.")
-+163:             return
-+164:         numero = amostra.iloc[int(escolha) - 1]["telefone"]
-+165:     else:
-+166:         print("Opção inválida.")
-+167:         return
-+168: 
-+169:     if not numero:
-+170:         print("Nenhum número informado.")
-+171:         return
-+172: 
-+173:     try:
-+174:         enviar_texto_numero(numero, mensagem)
-+175:         print(f"✅ Teste enviado para {numero}")
-+176:     except Exception as e:
-+177:         print(f"❌ Falha no teste para {numero}: {e}")
-+178: 
-+179: 
-+180: def enviar_whatsapp_menu():
-+181:     print("\n=== ENVIO WHATSAPP (WAHA) ===")
-+182: 
-+183:     if not WAHA_ATIVO:
-+184:         print("Envio de WhatsApp desativado (WAHA_ATIVO=false no .env).")
-+185:         return
-+186: 
-+187:     db = LeadDatabase()
-+188: 
-+189:     templates = db.listar_templates_ativos()
-+190:     if not templates:
-+191:         print("Nenhum template ativo. Cadastre um template na tabela templates_whatsapp.")
-+192:         db.close()
-+193:         return
-+194: 
-+195:     mensagem = _escolher_template(templates)
-+196: 
-+197:     numero_f, cidade_f, nicho_f = _escolher_filtros()
-+198: 
-+199:     pendentes = db.get_leads_para_envio(
-+200:         limite=WAHA_LIMITE, numero=numero_f, cidade=cidade_f, nicho=nicho_f
-+201:     )
-+202: 
-+203:     if _confirmar("Deseja fazer um envio de teste antes? (S/N): "):
-+204:         testar_envio(db, mensagem, pendentes=pendentes)
-+205: 
-+206:     if pendentes.empty:
-+207:         print("Nenhum lead celular pendente de envio (com os filtros aplicados).")
-+208:         db.close()
-+209:         return
-+210: 
-+211:     print(f"\n{len(pendentes)} lead(s) celular(es) pendentes (fixos são ignorados).")
-+212:     if WAHA_LIMITE:
-+213:         print(f"Limite configurado: {WAHA_LIMITE} lead(s) por campanha.")
-+214: 
-+215:     if not _confirmar(f"Enviar para {len(pendentes)} lead(s)? (S/N): "):
-+216:         print("Envio cancelado.")
-+217:         db.close()
-+218:         return
-+219: 
-+220:     disparar_campanha(
-+221:         db,
-+222:         mensagem_template=mensagem,
-+223:         intervalo=WAHA_INTERVALO,
-+224:         limite=WAHA_LIMITE,
-+225:         leads=pendentes,
-+226:     )
-+227:     db.close()
-+228: 
-+229: 
-+230: def aquecer_bairros_menu():
-+231:     """Prepara o cache de bairros de uma UF inteira (sem raspar leads)."""
-+232:     print("\n=== AQUECER BAIRROS DE UMA UF ===")
-+233: 
-+234:     if not LOCALIDADES_SALVAR:
-+235:         print("LOCALIDADES_SALVAR=false: o aquecimento está desativado.")
-+236:         print("Ative a flag LOCALIDADES_SALVAR no .env para gravar os bairros.")
-+237:         return
-+238: 
-+239:     print("Resolve e grava os bairros de todas as cidades da UF, uma única vez.")
-+240:     print("Depois disso a coleta por cidade não consulta mais IBGE/OSM.")
-+241: 
-+242:     df_estados = obter_estados()
-+243:     if df_estados.empty:
-+244:         print("Não foi possível obter a lista de estados.")
-+245:         return
-+246: 
-+247:     uf = input("Digite a UF (ex: RS, SP, RJ): ").strip().upper()
-+248:     if uf not in df_estados['uf'].values:
-+249:         print("UF inválida.")
-+250:         return
-+251: 
-+252:     print(f"\nVerificando quais cidades de {uf} ainda precisam de bairros...")
-+253:     pendentes = listar_municipios_pendentes(uf)
-+254:     if not pendentes:
-+255:         print(f"Todas as cidades de {uf} já estão na base local. Nada a fazer.")
-+256:         return
-+257: 
-+258:     print(f"{len(pendentes)} cidade(s) pendente(s) em {uf}.")
-+259:     print("As cidades cobertas pelo IBGE são instantâneas; as demais usam o")
-+260:     print("OpenStreetMap (Nominatim + Overpass), com pausa entre elas.")
-+261: 
-+262:     limite = input("Quantas cidades processar agora? (Enter = todas): ").strip()
-+263:     max_cidades = 0
-+264:     if limite:
-+265:         try:
-+266:             max_cidades = max(1, int(limite))
-+267:         except ValueError:
-+268:             print("Valor inválido. Usando todas.")
-+269:             max_cidades = 0
-+270: 
-+271:     previstas = min(max_cidades, len(pendentes)) if max_cidades else len(pendentes)
-+272:     confirmar = input(f"Processar {previstas} cidade(s)? (S/N): ").strip().upper()
-+273:     if confirmar != 'S':
-+274:         print("Operação cancelada.")
-+275:         return
-+276: 
-+277:     aquecer_bairros_uf(uf, cidades=pendentes, max_cidades=max_cidades)
-+278: 
-+279: 
-+280: def menu_interativo():
-+281:     # Flag de linha de comando: `python src/main.py --so-enviar` pula a coleta
-+282:     # e vai direto para o envio (equivale a SOMENTE_ENVIO=true no .env).
-+283:     so_enviar_cli = "--so-enviar" in sys.argv
-+284: 
-+285:     if SOMENTE_ENVIO or so_enviar_cli:
-+286:         enviar_whatsapp_menu()
-+287:         return
-+288: 
-+289:     while True:
-+290:         print("\n=== MAP SCRAPER ===")
-+291:         print("1 - Coletar leads")
-+292:         print("2 - Enviar mensagens WhatsApp")
-+293:         print("3 - Sincronizar base de localidades (IBGE)")
-+294:         print("4 - Aquecer bairros de uma UF (OpenStreetMap)")
-+295:         print("5 - Sair")
-+296:         opcao = input("Escolha uma opção: ").strip()
-+297: 
-+298:         if opcao == "1":
-+299:             coletar_leads()
-+300:         elif opcao == "2":
-+301:             enviar_whatsapp_menu()
-+302:         elif opcao == "3":
-+303:             sincronizar_base_localidades()
-+304:         elif opcao == "4":
-+305:             aquecer_bairros_menu()
-+306:         elif opcao == "5":
-+307:             print("Até mais!")
-+308:             break
-+309:         else:
-+310:             print("Opção inválida.")
-+311: 
-+312: 
-+313: if __name__ == "__main__":
-+314:     menu_interativo()
-+````
+-        self.conn.unregister('df_temp')
++        backend.bulk_upsert(
++            self.conn,
++            table="leads",
++            columns=colunas,
++            rows=linhas,
++            conflict="nome, cidade",
++            set_clause=(
++                "telefone = excluded.telefone, "
++                "tipo_telefone = excluded.tipo_telefone, "
++                "whatsapp_link = excluded.whatsapp_link, "
++                "instagram = excluded.instagram, "
++                "site = excluded.site, "
++                "bairro = excluded.bairro, "
++                "estado = excluded.estado, "
++                "nicho = excluded.nicho, "
++                "data_extracao = excluded.data_extracao"
++            ),
++        )
++        backend.commit(self.conn)
+         return len(df)
+ 
+     def get_leads_para_envio(self, limite=None, numero=None, cidade=None, nicho=None):
+@@ -238,7 +130,8 @@ class LeadDatabase:
+         - cidade: filtra por nome exato da cidade
+         - nicho:  filtra por nicho exato
+         """
+-        query = """
++        p = backend.ph()
++        query = f"""
+             SELECT lead_id, nome, telefone, whatsapp_link, bairro, cidade, estado, nicho, chat_id_waha
+             FROM leads
+             WHERE status = 'ativo'
+@@ -248,60 +141,65 @@ class LeadDatabase:
+         params = []
+         if numero:
+             numero = re.sub(r"\D", "", str(numero))
+-            query += " AND regexp_replace(telefone, '[^0-9]', '', 'g') LIKE ?"
++            query += f" AND regexp_replace(telefone, '[^0-9]', '', 'g') LIKE {p}"
+             params.append(f"%{numero}%")
+         if cidade:
+-            query += " AND cidade = ?"
++            query += f" AND cidade = {p}"
+             params.append(cidade)
+         if nicho:
+-            query += " AND nicho = ?"
++            query += f" AND nicho = {p}"
+             params.append(nicho)
+         query += " ORDER BY cidade, bairro, nome"
+         if limite:
+-            query += " LIMIT ?"
++            query += f" LIMIT {p}"
+             params.append(int(limite))
+-        return self.conn.execute(query, params).df()
++        return backend.query_df(self.conn, query, params)
+ 
+     def salvar_chat_id_waha(self, nome, cidade, chat_id):
+         """Cacheia o chatId resolvido (ex.: 143172869029943@lid) para não repetir
+         a chamada ao /api/checkNumberStatus em envios futuros."""
+-        self.conn.execute("""
++        p = backend.ph()
++        backend.execute(self.conn, f"""
+             UPDATE leads
+-            SET chat_id_waha = ?
+-            WHERE nome = ? AND cidade = ?
++            SET chat_id_waha = {p}
++            WHERE nome = {p} AND cidade = {p}
+         """, [chat_id, nome, cidade])
++        backend.commit(self.conn)
+ 
+     def marcar_envio(self, nome, cidade, status_whatsapp):
+         """Registra o resultado do envio. 'data_envio_whatsapp' é gravado apenas no sucesso."""
++        p = backend.ph()
+         if status_whatsapp == 'enviado':
+-            self.conn.execute("""
++            backend.execute(self.conn, f"""
+                 UPDATE leads
+-                SET status_whatsapp = ?, data_envio_whatsapp = ?
+-                WHERE nome = ? AND cidade = ?
++                SET status_whatsapp = {p}, data_envio_whatsapp = {p}
++                WHERE nome = {p} AND cidade = {p}
+             """, [status_whatsapp, datetime.now(), nome, cidade])
+         else:
+-            self.conn.execute("""
++            backend.execute(self.conn, f"""
+                 UPDATE leads
+-                SET status_whatsapp = ?
+-                WHERE nome = ? AND cidade = ?
++                SET status_whatsapp = {p}
++                WHERE nome = {p} AND cidade = {p}
+             """, [status_whatsapp, nome, cidade])
++        backend.commit(self.conn)
+ 
+     def export_to_excel(self, nicho: str, cidade: str):
+-        df = self.conn.execute("""
+-            SELECT nome, telefone, tipo_telefone, whatsapp_link, instagram, site, bairro, data_extracao 
+-            FROM leads 
+-            WHERE nicho = ? AND cidade = ? AND status = 'ativo'
++        p = backend.ph()
++        df = backend.query_df(self.conn, f"""
++            SELECT nome, telefone, tipo_telefone, whatsapp_link, instagram, site, bairro, data_extracao
++            FROM leads
++            WHERE nicho = {p} AND cidade = {p} AND status = 'ativo'
+             ORDER BY bairro, nome
+-        """, [nicho, cidade]).df()
+-        
++        """, [nicho, cidade])
 +
+         if df.empty:
+             print("Nenhum dado ativo para exportar.")
+             return
+-            
++
+         os.makedirs("output", exist_ok=True)
+         nome_arquivo = f"output/leads_{nicho}_{cidade}.xlsx".replace(" ", "_").lower()
+         df.to_excel(nome_arquivo, index=False)
+         print(f"🎉 Exportação concluída: {nome_arquivo} ({len(df)} leads ativos)")
+ 
+     def close(self):
+-        self.conn.close()
+\ No newline at end of file
++        backend.close(self.conn)
+diff --git a/src/localidades_db.py b/src/localidades_db.py
+index fbf1c56..d528ed8 100644
+--- a/src/localidades_db.py
++++ b/src/localidades_db.py
+@@ -1,22 +1,20 @@
+ # src/localidades_db.py
+-"""Cache local (DuckDB) da base de localidades do IBGE.
++"""Cache (PostgreSQL ou DuckDB) da base de localidades do IBGE.
+ 
+ Guarda apenas o essencial, para não inflar o banco:
+     localidades_estados     -> uf, nome
+     localidades_municipios  -> id_municipio, nome, uf + estado da coleta de bairros
+     localidades_bairros     -> id_municipio, nome, id_distrito
+ 
+-O arquivo é o mesmo DuckDB dos leads (data/leads.duckdb). Cada operação abre e
+-fecha a conexão, então o cache nunca segura o banco travado durante o scraping.
++Cada operação abre e fecha a conexão, então o cache nunca segura uma conexão
++aberta durante o scraping.
+ """
+-import os
+ from contextlib import contextmanager
+ from datetime import datetime
+ 
+-import duckdb
+ import pandas as pd
+ 
+-DB_PATH_PADRAO = os.path.join("data", "leads.duckdb")
++from src import backend
+ 
+ # Origem da lista de bairros gravada para uma cidade.
+ FONTE_IBGE = "ibge"           # distritos do IBGE (quantidade suficiente)
+@@ -25,143 +23,98 @@ FONTE_CIDADE = "cidade"       # nenhum bairro usado: busca a cidade inteira
+ 
+ 
+ class CacheIndisponivel(Exception):
+-    """Não foi possível abrir ou gravar a base local (ex.: arquivo travado)."""
+-
+-
+-_DDL = (
+-    """
+-    CREATE TABLE IF NOT EXISTS localidades_estados (
+-        uf VARCHAR PRIMARY KEY,
+-        nome VARCHAR NOT NULL
+-    )
+-    """,
+-    """
+-    CREATE TABLE IF NOT EXISTS localidades_municipios (
+-        id_municipio BIGINT PRIMARY KEY,
+-        nome VARCHAR NOT NULL,
+-        uf VARCHAR NOT NULL,
+-        bairros_fonte VARCHAR,
+-        bairros_atualizado_em TIMESTAMP
+-    )
+-    """,
+-    """
+-    CREATE TABLE IF NOT EXISTS localidades_bairros (
+-        id_municipio BIGINT NOT NULL,
+-        nome VARCHAR NOT NULL,
+-        id_distrito BIGINT,
+-        PRIMARY KEY (id_municipio, nome)
+-    )
+-    """,
+-)
+-
+-
+-# Se false, nenhuma DDL é executada: o cache é aberto somente para leitura.
+-# Definido por `src/locations.py` a partir de LOCALIDADES_SALVAR.
+-CRIAR_TABELAS = True
++    """Não foi possível abrir/gravar a base de localidades (ex.: servidor fora)."""
+ 
+ 
+ @contextmanager
+-def conexao(db_path=None):
+-    caminho = db_path or DB_PATH_PADRAO
+-    diretorio = os.path.dirname(caminho)
+-    if diretorio:
+-        os.makedirs(diretorio, exist_ok=True)
++def _conexao():
++    """Abre uma conexão transacional; commit no fim, rollback em caso de erro."""
+     try:
+-        con = duckdb.connect(caminho)
++        conn = backend.conectar()
+     except Exception as e:
+-        raise CacheIndisponivel(f"{caminho}: {e}") from e
++        raise CacheIndisponivel(f"não foi possível conectar ao banco: {e}") from e
+     try:
+-        if CRIAR_TABELAS:
+-            for ddl in _DDL:
+-                con.execute(ddl)
+-        yield con
++        yield conn
++        backend.commit(conn)
++    except Exception:
++        if not backend.IS_DUCKDB:
++            conn.rollback()
++        raise
+     finally:
+-        con.close()
++        backend.close(conn)
+ 
+ 
+-def _ler(con, sql, params=None):
+-    """Executa uma leitura, traduzindo 'tabela não existe' em CacheIndisponivel."""
+-    try:
+-        return con.execute(sql, params) if params else con.execute(sql)
+-    except duckdb.CatalogException as e:
+-        raise CacheIndisponivel(
+-            "tabelas de localidades não existem neste banco (rode a sincronização no menu)"
+-        ) from e
++def _df(conn, sql, params=None):
++    return backend.query_df(conn, sql, params)
+ 
+ 
+-def _inserir_lote(con, df, sql):
+-    if df is None or df.empty:
+-        return
+-    con.register("_lote", df)
+-    try:
+-        con.execute(sql)
+-    finally:
+-        con.unregister("_lote")
++def _inserir_upsert(conn, table, columns, df, conflict, set_clause):
++    backend.bulk_upsert(
++        conn,
++        table=table,
++        columns=columns,
++        rows=backend.df_to_rows(df),
++        conflict=conflict,
++        set_clause=set_clause,
++    )
+ 
+ 
+-def ler_estados(db_path=None):
+-    with conexao(db_path) as con:
+-        df = _ler(con, "SELECT uf, nome FROM localidades_estados ORDER BY nome").df()
++def ler_estados():
++    with _conexao() as conn:
++        df = _df(conn, "SELECT uf, nome FROM localidades_estados ORDER BY nome")
+     return df.to_dict("records")
+ 
+ 
+-def salvar_estados(registros, db_path=None):
++def salvar_estados(registros):
+     df = pd.DataFrame(list(registros), columns=["uf", "nome"]).drop_duplicates("uf")
+-    with conexao(db_path) as con:
+-        _inserir_lote(con, df, """
+-            INSERT INTO localidades_estados (uf, nome)
+-            SELECT uf, nome FROM _lote
+-            ON CONFLICT (uf) DO UPDATE SET nome = excluded.nome
+-        """)
++    with _conexao() as conn:
++        _inserir_upsert(conn, "localidades_estados", ["uf", "nome"], df,
++                        conflict="uf", set_clause="nome = excluded.nome")
+     return len(df)
+ 
+ 
+-def ler_municipios(uf, db_path=None):
+-    with conexao(db_path) as con:
+-        df = _ler(con,
+-            """SELECT id_municipio, nome, uf, bairros_fonte
+-               FROM localidades_municipios WHERE uf = ? ORDER BY nome""",
+-            [uf],
+-        ).df()
++def ler_municipios(uf):
++    with _conexao() as conn:
++        df = _df(conn, """
++            SELECT id_municipio, nome, uf, bairros_fonte
++            FROM localidades_municipios WHERE uf = %s ORDER BY nome
++        """.replace("%s", backend.ph()), [uf])
+     return df.to_dict("records")
+ 
+ 
+-def ler_municipios_pendentes(uf, db_path=None):
++def ler_municipios_pendentes(uf):
+     """Municípios da UF cujos bairros ainda não foram resolvidos (bairros_fonte nulo)."""
+-    with conexao(db_path) as con:
+-        df = _ler(con, """
++    with _conexao() as conn:
++        df = _df(conn, """
+             SELECT id_municipio, nome
+             FROM localidades_municipios
+-            WHERE uf = ? AND bairros_fonte IS NULL
++            WHERE uf = %s AND bairros_fonte IS NULL
+             ORDER BY nome
+-        """, [uf]).df()
++        """.replace("%s", backend.ph()), [uf])
+     return df.to_dict("records")
+ 
+ 
+-def salvar_municipios(registros, db_path=None):
++def salvar_municipios(registros):
+     df = pd.DataFrame(list(registros), columns=["id_municipio", "nome", "uf"])
+     df = df.dropna(subset=["id_municipio"]).drop_duplicates("id_municipio")
+-    with conexao(db_path) as con:
++    with _conexao() as conn:
+         # UPSERT preserva bairros_fonte/bairros_atualizado_em já gravados.
+-        _inserir_lote(con, df, """
+-            INSERT INTO localidades_municipios (id_municipio, nome, uf)
+-            SELECT id_municipio, nome, uf FROM _lote
+-            ON CONFLICT (id_municipio) DO UPDATE SET
+-                nome = excluded.nome,
+-                uf = excluded.uf
+-        """)
++        _inserir_upsert(conn, "localidades_municipios", ["id_municipio", "nome", "uf"], df,
++                        conflict="id_municipio",
++                        set_clause="nome = excluded.nome, uf = excluded.uf")
+     return len(df)
+ 
+ 
+-def buscar_municipio(cidade, uf, db_path=None):
++def buscar_municipio(cidade, uf):
+     """Retorna {id_municipio, nome, uf, bairros_fonte} ou None se não estiver na base."""
+-    with conexao(db_path) as con:
+-        linha = _ler(con, """
++    p = backend.ph()
++    with _conexao() as conn:
++        linha = backend.query_one(conn, f"""
+             SELECT id_municipio, nome, uf, bairros_fonte
+             FROM localidades_municipios
+-            WHERE uf = ? AND lower(nome) = lower(?)
++            WHERE uf = {p} AND lower(nome) = lower({p})
+             LIMIT 1
+-        """, [uf, cidade]).fetchone()
++        """, [uf, cidade])
+     if not linha:
+         return None
+     return {
+@@ -172,12 +125,12 @@ def buscar_municipio(cidade, uf, db_path=None):
+     }
+ 
+ 
+-def ler_bairros(id_municipio, db_path=None):
+-    with conexao(db_path) as con:
+-        df = _ler(con,
+-            "SELECT nome FROM localidades_bairros WHERE id_municipio = ? ORDER BY nome",
+-            [int(id_municipio)],
+-        ).df()
++def ler_bairros(id_municipio):
++    with _conexao() as conn:
++        df = _df(conn,
++            "SELECT nome FROM localidades_bairros WHERE id_municipio = %s ORDER BY nome"
++            .replace("%s", backend.ph()), [int(id_municipio)],
++        )
+     return df["nome"].tolist()
+ 
+ 
+@@ -200,93 +153,84 @@ def _normalizar_bairros(registros):
+     return df.drop_duplicates("nome")
+ 
+ 
+-def salvar_bairros(id_municipio, registros, fonte, db_path=None):
++def salvar_bairros(id_municipio, registros, fonte):
+     """Grava a lista final de bairros de uma cidade e marca a origem da coleta.
+ 
+     A lista é autoritativa para a cidade: bairros que não estão nela são
+-    removidos, para o cache não acumular nomes de uma coleta anterior.
+-    `fonte` = 'ibge', 'overpass' ou 'cidade' (sem bairros úteis).
++    removidos (delete da cidade + re-insert), para o cache não acumular nomes
++    de uma coleta anterior. `fonte` = 'ibge', 'overpass' ou 'cidade'.
+     """
+     id_municipio = int(id_municipio)
+     df = _normalizar_bairros(registros)
+ 
+-    with conexao(db_path) as con:
++    with _conexao() as conn:
++        p = backend.ph()
+         if df.empty:
+-            con.execute(
+-                "DELETE FROM localidades_bairros WHERE id_municipio = ?", [id_municipio]
+-            )
++            backend.execute(conn, f"DELETE FROM localidades_bairros WHERE id_municipio = {p}",
++                            [id_municipio])
+         else:
+             df.insert(0, "id_municipio", id_municipio)
+-            con.register("_lote", df)
+-            try:
+-                con.execute("""
+-                    DELETE FROM localidades_bairros
+-                    WHERE id_municipio = ?
+-                      AND nome NOT IN (SELECT nome FROM _lote)
+-                """, [id_municipio])
+-                con.execute("""
+-                    INSERT OR REPLACE INTO localidades_bairros (id_municipio, nome, id_distrito)
+-                    SELECT id_municipio, nome, id_distrito FROM _lote
+-                """)
+-            finally:
+-                con.unregister("_lote")
+-
+-        con.execute("""
++            # Autoritativo por cidade: apaga tudo da cidade e reinsere.
++            backend.execute(conn, f"DELETE FROM localidades_bairros WHERE id_municipio = {p}",
++                            [id_municipio])
++            _inserir_upsert(
++                conn, "localidades_bairros", ["id_municipio", "nome", "id_distrito"], df,
++                conflict="id_municipio, nome",
++                set_clause="id_distrito = excluded.id_distrito",
++            )
++
++        backend.execute(conn, f"""
+             UPDATE localidades_municipios
+-            SET bairros_fonte = ?, bairros_atualizado_em = ?
+-            WHERE id_municipio = ?
++            SET bairros_fonte = {p}, bairros_atualizado_em = {p}
++            WHERE id_municipio = {p}
+         """, [fonte, datetime.now(), id_municipio])
+     return len(df)
+ 
+ 
+-def salvar_distritos_bulk(distritos, min_bairros=3, db_path=None):
++def salvar_distritos_bulk(distritos, min_bairros=3):
+     """Grava todos os distritos do IBGE de uma vez (sincronização completa).
+ 
+-    É aditivo (INSERT OR REPLACE por id_municipio+nome): não apaga bairros que já
+-    existem, para não destruir listas complementadas pelo OpenStreetMap.
++    É aditivo (upsert por id_municipio+nome): não apaga bairros que já existem,
++    para não destruir listas complementadas pelo OpenStreetMap.
+ 
+     Marca como 'ibge' apenas os municípios com pelo menos `min_bairros` distritos
+-    úteis (ou seja, desconsiderando o distrito que tem o mesmo nome da cidade).
+-    Os demais continuam sem fonte definida e serão complementados via Overpass
+-    na primeira consulta.
++    úteis (desconsiderando o distrito que tem o mesmo nome da cidade).
+     """
+     df = pd.DataFrame(list(distritos), columns=["id_municipio", "nome", "id_distrito"])
+     df = df.dropna(subset=["id_municipio", "nome"]).drop_duplicates(["id_municipio", "nome"])
+     df["id_distrito"] = df["id_distrito"].astype("Int64")
+ 
+-    with conexao(db_path) as con:
+-        _inserir_lote(con, df, """
+-            INSERT OR REPLACE INTO localidades_bairros (id_municipio, nome, id_distrito)
+-            SELECT id_municipio, nome, id_distrito FROM _lote
+-        """)
+-        con.execute("DROP TABLE IF EXISTS _cobertura")
+-        con.execute("""
+-            CREATE TEMP TABLE _cobertura AS
+-            SELECT b.id_municipio
+-            FROM localidades_bairros b
+-            JOIN localidades_municipios m ON m.id_municipio = b.id_municipio
+-            WHERE lower(b.nome) <> lower(m.nome)
+-            GROUP BY b.id_municipio
+-            HAVING COUNT(*) >= ?
+-        """, [int(min_bairros)])
+-        con.execute("""
++    with _conexao() as conn:
++        p = backend.ph()
++        _inserir_upsert(
++            conn, "localidades_bairros", ["id_municipio", "nome", "id_distrito"], df,
++            conflict="id_municipio, nome",
++            set_clause="id_distrito = excluded.id_distrito",
++        )
++        backend.execute(conn, f"""
+             UPDATE localidades_municipios
+-            SET bairros_fonte = ?, bairros_atualizado_em = ?
++            SET bairros_fonte = {p}, bairros_atualizado_em = {p}
+             WHERE bairros_fonte IS NULL
+-              AND id_municipio IN (SELECT id_municipio FROM _cobertura)
+-        """, [FONTE_IBGE, datetime.now()])
+-        con.execute("DROP TABLE IF EXISTS _cobertura")
++              AND id_municipio IN (
++                  SELECT b.id_municipio
++                  FROM localidades_bairros b
++                  JOIN localidades_municipios mm ON mm.id_municipio = b.id_municipio
++                  WHERE lower(b.nome) <> lower(mm.nome)
++                  GROUP BY b.id_municipio
++                  HAVING COUNT(*) >= {p}
++              )
++        """, [FONTE_IBGE, datetime.now(), int(min_bairros)])
+     return len(df)
+ 
+ 
+-def estatisticas(db_path=None):
+-    with conexao(db_path) as con:
+-        estados = _ler(con, "SELECT COUNT(*) FROM localidades_estados").fetchone()[0]
+-        municipios = _ler(con, "SELECT COUNT(*) FROM localidades_municipios").fetchone()[0]
+-        bairros = _ler(con, "SELECT COUNT(*) FROM localidades_bairros").fetchone()[0]
+-        prontas = _ler(con, """
+-            SELECT COUNT(*) FROM localidades_municipios WHERE bairros_fonte IS NOT NULL
+-        """).fetchone()[0]
++def estatisticas():
++    with _conexao() as conn:
++        def _count(sql):
++            return backend.query_one(conn, sql)[0]
++        estados = _count("SELECT COUNT(*) FROM localidades_estados")
++        municipios = _count("SELECT COUNT(*) FROM localidades_municipios")
++        bairros = _count("SELECT COUNT(*) FROM localidades_bairros")
++        prontas = _count("SELECT COUNT(*) FROM localidades_municipios WHERE bairros_fonte IS NOT NULL")
+     return {
+         "estados": estados,
+         "municipios": municipios,
+diff --git a/src/locations.py b/src/locations.py
+index 23d0a47..6cfcd91 100644
+--- a/src/locations.py
++++ b/src/locations.py
+@@ -1,5 +1,5 @@
+ # src/locations.py
+-"""Localidades (UF, cidade e bairros) com cache local em DuckDB.
++"""Localidades (UF, cidade e bairros) com cache em PostgreSQL.
+ 
+ Fonte oficial: API de Localidades do IBGE.
+     estados    -> /api/v1/localidades/estados
+@@ -39,13 +39,10 @@ OVERPASS_ENDPOINTS = [
+ # Se true: consulta o banco antes da API. Se false: sempre busca na API.
+ USAR_CACHE = str_para_bool(os.environ.get("LOCALIDADES_USAR_CACHE"), padrao=True)
+ 
+-# Se false: NUNCA grava na base local (nem cria tabelas). Funciona como
+-# "somente leitura": o banco é consultado, mas nada é alterado.
++# Se false: NUNCA grava na base local. Funciona como "somente leitura":
++# o banco é consultado, mas nada é alterado.
+ SALVAR = str_para_bool(os.environ.get("LOCALIDADES_SALVAR"), padrao=True)
+ 
+-# Reflete a flag no módulo de acesso ao banco (controla a criação das tabelas).
+-localidades_db.CRIAR_TABELAS = SALVAR
+-
+ # Quantidade mínima de distritos úteis para não precisar do OpenStreetMap.
+ # Abaixo disso, a cidade é complementada com bairros do OSM.
+ MIN_BAIRROS = max(1, env_int("LOCALIDADES_MIN_BAIRROS", 3))
+diff --git a/src/main.py b/src/main.py
+index 5887015..bcaf6b9 100644
+--- a/src/main.py
++++ b/src/main.py
+@@ -196,9 +196,8 @@ def enviar_whatsapp_menu():
+ 
+     numero_f, cidade_f, nicho_f = _escolher_filtros()
+ 
+-    pendentes = db.get_leads_para_envio(
+-        limite=WAHA_LIMITE, numero=numero_f, cidade=cidade_f, nicho=nicho_f
+-    )
++    # Busca todos os pendentes (sem limitar ainda) para mostrar o total disponível.
++    pendentes = db.get_leads_para_envio(numero=numero_f, cidade=cidade_f, nicho=nicho_f)
+ 
+     if _confirmar("Deseja fazer um envio de teste antes? (S/N): "):
+         testar_envio(db, mensagem, pendentes=pendentes)
+@@ -208,9 +207,35 @@ def enviar_whatsapp_menu():
+         db.close()
+         return
+ 
+-    print(f"\n{len(pendentes)} lead(s) celular(es) pendentes (fixos são ignorados).")
++    total_disponivel = len(pendentes)
++    print(f"\n{total_disponivel} lead(s) celular(es) pendentes (fixos são ignorados).")
++
++    # Quantidade (range): Enter = todos (respeitando o limite do .env, se houver).
+     if WAHA_LIMITE:
+-        print(f"Limite configurado: {WAHA_LIMITE} lead(s) por campanha.")
++        print(f"Limite configurado no .env: {WAHA_LIMITE} lead(s) por campanha.")
++        padrao = WAHA_LIMITE
++    else:
++        padrao = total_disponivel
++
++    entrada = input(
++        f"Quantos leads enviar? (Enter = {padrao}): "
++    ).strip()
++
++    if entrada:
++        if entrada.isdigit() and int(entrada) > 0:
++            quantidade = int(entrada)
++        else:
++            print("Valor inválido. Usando o padrão.")
++            quantidade = padrao
++    else:
++        quantidade = padrao
++
++    if WAHA_LIMITE and quantidade > WAHA_LIMITE:
++        print(f"Ajustando para o limite do .env ({WAHA_LIMITE}).")
++        quantidade = WAHA_LIMITE
++
++    quantidade = min(quantidade, total_disponivel)
++    pendentes = pendentes.head(quantidade)
+ 
+     if not _confirmar(f"Enviar para {len(pendentes)} lead(s)? (S/N): "):
+         print("Envio cancelado.")
+@@ -221,7 +246,7 @@ def enviar_whatsapp_menu():
+         db,
+         mensagem_template=mensagem,
+         intervalo=WAHA_INTERVALO,
+-        limite=WAHA_LIMITE,
++        limite=quantidade,
+         leads=pendentes,
+     )
+     db.close()
+diff --git a/src/whatsapp.py b/src/whatsapp.py
+index 4715b67..989db52 100644
+--- a/src/whatsapp.py
++++ b/src/whatsapp.py
+@@ -12,6 +12,7 @@ O módulo só envia para leads:
+     - ainda não enviados (status_whatsapp = 'pendente' ou NULL)
+ """
+ import os
++import random
+ import re
+ import time
+ 
+@@ -31,12 +32,86 @@ WAHA_ATIVO = str_para_bool(os.environ.get("WAHA_ATIVO"), padrao=True)
+ # Se true, pula a coleta e vai direto para o envio (não coleta nada).
+ SOMENTE_ENVIO = str_para_bool(os.environ.get("SOMENTE_ENVIO"), padrao=False)
+ 
+-# Intervalo (segundos) entre envios e limite de leads por campanha.
+-# WAHA_LIMITE vazio = sem limite (envia todos os pendentes).
++# ---------------------------------------------------------------------------
++# Cadência de envio (anti-bloqueio)
++# ---------------------------------------------------------------------------
++# Formato "X a cada Y segundos", ex.: WAHA_CADENCIA=3:60  -> 3 envios por minuto.
++# Os envios são distribuídos ALEATORIAMENTE dentro da janela de Y segundos,
++# evitando pausas fixas (15s, 15s, ...) que são mais fáceis de detectar.
++WAHA_CADENCIA = os.environ.get("WAHA_CADENCIA", "").strip()
++
++# Legado: WAHA_INTERVALO (pausa fixa) continua funcionando quando WAHA_CADENCIA
++# não é informado.
+ WAHA_INTERVALO = int(os.environ.get("WAHA_INTERVALO", "13"))
++
++# Limite de leads por campanha. Vazio = sem limite.
+ WAHA_LIMITE = os.environ.get("WAHA_LIMITE", "").strip()
+ WAHA_LIMITE = int(WAHA_LIMITE) if WAHA_LIMITE else None
+ 
++
++def _parse_cadencia(valor):
++    """Interpreta "N:Y" -> (envios_por_janela, janela_segundos).
++
++    Retorna None quando o valor está vazio/inválido (usa o intervalo fixo).
++    """
++    if not valor:
++        return None
++    try:
++        envios, janela = valor.split(":", 1)
++        envios = int(envios.strip())
++        janela = int(janela.strip())
++    except (ValueError, AttributeError):
++        return None
++    if envios <= 0 or janela <= 0:
++        return None
++    return envios, janela
++
++
++def _intervalos_aleatorios(quantidade, janela_segundos):
++    """Gera as pausas (em segundos) para `quantidade` envios numa janela.
++
++    Distribui os envios em pontos aleatórios crescentes dentro da janela e
++    retorna a diferença entre pontos consecutivos — o intervalo entre cada envio
++    varia, mas o total da janela é respeitado.
++    """
++    if quantidade <= 1:
++        return [0]
++    # Pontos aleatórios crescentes: 1 envio em cada "fatia" da janela, com
++    # jitter dentro da fatia, garantindo tempos diferentes entre os envios.
++    pontos = sorted(
++        random.uniform((i * janela_segundos) / quantidade,
++                       ((i + 1) * janela_segundos) / quantidade)
++        for i in range(quantidade)
++    )
++    return [round(pontos[i + 1] - pontos[i], 2) for i in range(quantidade - 1)]
++
++
++def _pausas_cadencia(total, envios_janela, janela_segundos):
++    """Gera as pausas da campanha inteira respeitando a cadência.
++
++    Agrupa os `total` envios em janelas de `janela_segundos` segundos, com
++    `envios_janela` envios por janela (distribuídos aleatoriamente). Retorna uma
++    lista com `total - 1` pausas (uma entre cada par consecutivo).
++    """
++    if total <= 1:
++        return [0]
++
++    # Timestamp de envio de cada lead: janela + posição aleatória dentro dela.
++    tempos = []
++    for idx in range(total):
++        janela_idx = idx // envios_janela
++        pos_na_janela = idx % envios_janela
++        inicio = janela_idx * janela_segundos
++        # posição aleatória dentro da fatia correspondente a este envio
++        p = random.uniform(
++            inicio + (pos_na_janela * janela_segundos) / envios_janela,
++            inicio + ((pos_na_janela + 1) * janela_segundos) / envios_janela,
++        )
++        tempos.append(p)
++
++    tempos.sort()
++    return [round(tempos[i + 1] - tempos[i], 2) for i in range(len(tempos) - 1)]
++
+ # Mensagem padrão (placeholder). Use {nome}, {bairro} e {cidade}.
+ MENSAGEM_PADRAO = "Olá {nome}! Vi que vocês atendem no bairro {bairro}, em {cidade}. Podemos conversar?"
+ 
+@@ -171,7 +246,7 @@ def disparar_campanha(db, mensagem_template=None, intervalo=13, limite=None, lea
+ 
+     - db: instância de LeadDatabase
+     - mensagem_template: texto com {nome}, {bairro}, {cidade} (usa MENSAGEM_PADRAO se None)
+-    - intervalo: pausa em segundos entre envios (evita spam e banimento)
++    - intervalo: pausa fixa em segundos entre envios (usado se não houver cadência)
+     - leads: DataFrame opcional já filtrado; se None, busca pendentes (com limite)
+     """
+     mensagem_template = mensagem_template or MENSAGEM_PADRAO
+@@ -183,7 +258,17 @@ def disparar_campanha(db, mensagem_template=None, intervalo=13, limite=None, lea
+         return
+ 
+     total = len(leads)
+-    print(f"Enviando para {total} lead(s) celular(es), com intervalo de {intervalo}s...")
++
++    # Cadência aleatória (ex.: 3 a cada 60s) tem prioridade sobre o intervalo fixo.
++    cadencia = _parse_cadencia(WAHA_CADENCIA)
++    if cadencia:
++        envios_janela, janela = cadencia
++        pausas = _pausas_cadencia(total, envios_janela, janela)
++        print(f"Enviando para {total} lead(s), cadência {envios_janela} a cada {janela}s "
++              f"(intervalos aleatórios)...")
++    else:
++        pausas = [intervalo] * max(0, total - 1)
++        print(f"Enviando para {total} lead(s), com intervalo fixo de {intervalo}s...")
+ 
+     for i, (_, lead) in enumerate(leads.iterrows(), 1):
+         texto = _renderizar_mensagem(mensagem_template, lead)
+@@ -233,6 +318,6 @@ def disparar_campanha(db, mensagem_template=None, intervalo=13, limite=None, lea
+             print(f"[{i}/{total}] FALHOU -> {nome} ({chat_id}): {erro}")
+ 
+         if i < total:
+-            time.sleep(intervalo)
++            time.sleep(pausas[i - 1])
  
- # Git Diffs
- ## Git Diffs Working Tree
+     print("Campanha finalizada.")
 
-`````
+````
 
 ## Git Diffs Staged
-`````diff
+````diff
 
-`````
+````
 
 
 
diff --git a/requirements.txt b/requirements.txt
index 8bfac01..6e167ed 100644
--- a/requirements.txt
+++ b/requirements.txt
@@ -6,4 +6,5 @@ playwright
 chromium
 geopy
 duckdb
+psycopg2-binary
 requests
diff --git a/src/config.py b/src/config.py
index 5d585ca..fa7e3e2 100644
--- a/src/config.py
+++ b/src/config.py
@@ -1,5 +1,5 @@
 # src/config.py
-"""Carregamento centralizado do arquivo .env e leitura de flags.
+"""Carregamento centralizado do arquivo .env, leitura de flags e conexão com o banco.
 
 Todos os módulos importam este arquivo, então o `.env` é lido uma única vez
 por processo, antes de qualquer constante de configuração ser calculada.
@@ -52,3 +52,33 @@ def env_int(nome, padrao):
 
 # Lido no import: qualquer módulo que importe `src.config` já tem o .env aplicado.
 carregar_env()
+
+# ---------------------------------------------------------------------------
+# Banco de dados — engine independente (PostgreSQL ou DuckDB)
+# ---------------------------------------------------------------------------
+# Escolha do backend:
+#   DB_ENGINE=postgres  -> PostgreSQL (DATABASE_URL ou DB_*)
+#   DB_ENGINE=duckdb    -> DuckDB local (DUCKDB_PATH)
+#
+# Se DB_ENGINE não for definido, a inferência é:
+#   DUCKDB_PATH  definido -> duckdb
+#   DATABASE_URL definido -> postgres
+#   nenhum dos dois       -> duckdb (padrão local/offline)
+DATABASE_URL = os.environ.get("DATABASE_URL", "")
+DUCKDB_PATH = os.environ.get("DUCKDB_PATH", "data/leads.duckdb")
+
+DB_ENGINE = os.environ.get("DB_ENGINE", "").strip().lower()
+if DB_ENGINE not in ("postgres", "duckdb"):
+    if os.environ.get("DUCKDB_PATH"):
+        DB_ENGINE = "duckdb"
+    elif os.environ.get("DATABASE_URL"):
+        DB_ENGINE = "postgres"
+    else:
+        DB_ENGINE = "duckdb"
+
+# Configuração do PostgreSQL (usada apenas quando DB_ENGINE=postgres).
+DB_HOST = os.environ.get("DB_HOST", "localhost")
+DB_PORT = env_int("DB_PORT", 5432)
+DB_NAME = os.environ.get("DB_NAME", "leads_db")
+DB_USER = os.environ.get("DB_USER", "leads_app")
+DB_PASSWORD = os.environ.get("DB_PASSWORD", "")
diff --git a/src/database.py b/src/database.py
index f59ddc6..b8a4df2 100644
--- a/src/database.py
+++ b/src/database.py
@@ -1,157 +1,36 @@
 # src/database.py
-import duckdb
-import pandas as pd
+"""Camada de acesso a dados (leads, templates e log de envio).
+
+Usa `src/backend.py`, que abstrai PostgreSQL e DuckDB — o código daqui não
+depende do banco específico. A criação do schema e o seed dos templates ficam
+em `src/schema.py` (executado uma vez no setup: `python src/schema.py`).
+"""
 import os
 import re
 import json
 from datetime import datetime
 
-# Template padrão de WhatsApp, usado para popular a tabela de templates.
-# Segmento indica o nicho para o qual a mensagem foi criada (ex.: barbearias).
-TEMPLATE_AGRUPAMENTO_PADRAO = """Opa, tudo certo?
-
-Conhece o Agendamento Já? É uma plataforma 100% online para deixar sua agenda no piloto automático e acabar com a dor de cabeça de gerenciar horários pelo WhatsApp.
-
-Com planos a partir de R$ 60,00 no nosso aplicativo você consegue:
-
-• Personalizar com a identidade da sua marca
-• Lembretes automatizados via Whatsapp
-• Divulgação de horários automatizadas
-• Controle de faturamento
-• Pagamentos antecipados
-
-Conheça nossa proposta: https://agendamentoja.com/
-Acompanhe nosso dia a dia: https://www.instagram.com/agendamentoja_
+import pandas as pd
 
-Quer ver uma demonstração rápida de como funciona na prática para o seu tipo de serviço? É só me avisar!"""
+from src import backend
 
-# Segmento (nicho) padrão do template acima.
-TEMPLATE_SEGMENTO_PADRAO = "barbearias"
 
 class LeadDatabase:
-    def __init__(self, db_path="data/leads.duckdb"):
-        os.makedirs(os.path.dirname(db_path), exist_ok=True)
-        self.db_path = db_path
-        self.conn = duckdb.connect(self.db_path)
-        self._create_sequences()
-        self._create_table()
-        self._ensure_whatsapp_columns()
-        self._ensure_lead_id()
-        self._create_templates_table()
-        self._seed_templates()
-        self._create_envios_log_table()
-
-    def _create_sequences(self):
-        """Sequências de ids numéricos (leads e log de envios)."""
-        self.conn.execute("CREATE SEQUENCE IF NOT EXISTS seq_leads_id")
-        self.conn.execute("CREATE SEQUENCE IF NOT EXISTS seq_whatsapp_envios_log_id")
-
-    def _create_table(self):
-        self.conn.execute("""
-            CREATE TABLE IF NOT EXISTS leads (
-                lead_id INTEGER DEFAULT nextval('seq_leads_id'),
-                nome VARCHAR,
-                telefone VARCHAR,
-                tipo_telefone VARCHAR,
-                whatsapp_link VARCHAR,
-                instagram VARCHAR,
-                site VARCHAR,
-                bairro VARCHAR,
-                cidade VARCHAR,
-                estado VARCHAR,
-                nicho VARCHAR,
-                status VARCHAR DEFAULT 'ativo',
-                data_extracao TIMESTAMP,
-                data_envio_whatsapp TIMESTAMP,
-                status_whatsapp VARCHAR DEFAULT 'pendente',
-                chat_id_waha VARCHAR,
-                PRIMARY KEY (nome, cidade)
-            )
-        """)
-
-    def _ensure_whatsapp_columns(self):
-        """Adiciona as colunas de log de WhatsApp em bancos criados antes da migração."""
-        colunas = {row[1] for row in self.conn.execute("PRAGMA table_info(leads)").fetchall()}
-        if 'data_envio_whatsapp' not in colunas:
-            self.conn.execute("ALTER TABLE leads ADD COLUMN data_envio_whatsapp TIMESTAMP")
-        if 'status_whatsapp' not in colunas:
-            self.conn.execute("ALTER TABLE leads ADD COLUMN status_whatsapp VARCHAR DEFAULT 'pendente'")
-        if 'chat_id_waha' not in colunas:
-            self.conn.execute("ALTER TABLE leads ADD COLUMN chat_id_waha VARCHAR")
-
-    def _ensure_lead_id(self):
-        """Adiciona o id numérico em bancos antigos (backfill automático via DEFAULT)."""
-        colunas = {row[1] for row in self.conn.execute("PRAGMA table_info(leads)").fetchall()}
-        if 'lead_id' not in colunas:
-            self.conn.execute(
-                "ALTER TABLE leads ADD COLUMN lead_id INTEGER DEFAULT nextval('seq_leads_id')"
-            )
-
-    def _create_templates_table(self):
-        """Tabela de templates de mensagem de WhatsApp (mensagem, descrição, segmento e ativo)."""
-        self.conn.execute("""
-            CREATE TABLE IF NOT EXISTS templates_whatsapp (
-                id INTEGER PRIMARY KEY,
-                mensagem VARCHAR,
-                descricao VARCHAR,
-                segmento VARCHAR,
-                ativo BOOLEAN DEFAULT TRUE
-            )
-        """)
-        colunas = {row[1] for row in self.conn.execute("PRAGMA table_info(templates_whatsapp)").fetchall()}
-        if 'segmento' not in colunas:
-            self.conn.execute("ALTER TABLE templates_whatsapp ADD COLUMN segmento VARCHAR")
-
-    def _seed_templates(self):
-        """Garante o template padrão do Agendamento Já (id=1), atualizando se já existir."""
-        self.conn.execute("""
-            INSERT INTO templates_whatsapp (id, mensagem, descricao, segmento, ativo)
-            VALUES (1, ?, 'Apresentação Agendamento Já', ?, TRUE)
-            ON CONFLICT (id) DO UPDATE SET
-                mensagem = excluded.mensagem,
-                descricao = excluded.descricao,
-                segmento = excluded.segmento,
-                ativo = excluded.ativo
-        """, [TEMPLATE_AGRUPAMENTO_PADRAO, TEMPLATE_SEGMENTO_PADRAO])
+    def __init__(self, conn=None):
+        self.conn = conn if conn is not None else backend.conectar()
 
     def listar_templates_ativos(self):
         """Retorna os templates ativos como lista de dicionários (id, mensagem, descricao, segmento, ativo)."""
         return (
-            self.conn.execute("""
+            backend.query_df(self.conn, """
                 SELECT id, mensagem, descricao, segmento, ativo
                 FROM templates_whatsapp
                 WHERE ativo = TRUE
                 ORDER BY id
             """)
-            .df()
             .to_dict("records")
         )
 
-    def _create_envios_log_table(self):
-        """Tabela de log dos envios de WhatsApp (rastreamento de cada disparo).
-
-        - `lead_id`: FK lógica para `leads.lead_id` (DuckDB não aplica FK).
-        - `telefone`: somente dígitos, igual a `leads.telefone` → chave de JOIN.
-        - `telefone_normalizado`: formato canônico 55DDDNUMERO (quando 11 dígitos).
-        - `payload`: retorno bruto da WAHA (JSON), útil para auditoria.
-        """
-        self.conn.execute("""
-            CREATE TABLE IF NOT EXISTS whatsapp_envios_log (
-                id INTEGER PRIMARY KEY DEFAULT nextval('seq_whatsapp_envios_log_id'),
-                lead_id INTEGER,
-                nome VARCHAR,
-                cidade VARCHAR,
-                telefone VARCHAR,
-                telefone_normalizado VARCHAR,
-                chat_id VARCHAR,
-                status VARCHAR,
-                mensagem VARCHAR,
-                payload VARCHAR,
-                erro VARCHAR,
-                data_envio TIMESTAMP
-            )
-        """)
-
     def salvar_log_envio(self, lead_id, nome, cidade, telefone, chat_id, status,
                          mensagem=None, payload=None, erro=None):
         """Grava uma linha de log de envio com os campos normalizados.
@@ -181,53 +60,66 @@ class LeadDatabase:
             else:
                 payload_str = str(payload)
 
-        self.conn.execute("""
+        p = backend.ph()
+        backend.execute(self.conn, f"""
             INSERT INTO whatsapp_envios_log
                 (lead_id, nome, cidade, telefone, telefone_normalizado, chat_id,
                  status, mensagem, payload, erro, data_envio)
-            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
-        """, [lead_id, nome, cidade, telefone or None, telefone_normalizado, chat_id,
-              status, mensagem, payload_str, erro, datetime.now()])
+            VALUES ({p}, {p}, {p}, {p}, {p}, {p}, {p}, {p}, {p}, {p}, {p})
+        """, [
+            lead_id, nome, cidade, telefone or None, telefone_normalizado, chat_id,
+            status, mensagem, payload_str, erro, datetime.now(),
+        ])
+        backend.commit(self.conn)
 
     def save_leads(self, df: pd.DataFrame):
         if df.empty:
             return 0
-        
-        descartados_db = self.conn.execute("SELECT nome, cidade FROM leads WHERE status = 'descartado'").fetchall()
-        descartados_set = set(descartados_db)
-        
-        df = df[~df.apply(lambda row: (row['nome'], row['cidade']) in descartados_set, axis=1)]
-        
+
+        descartados = set(backend.query_all(
+            self.conn, "SELECT nome, cidade FROM leads WHERE status = 'descartado'"
+        ))
+        df = df[~df.apply(lambda row: (row['nome'], row['cidade']) in descartados, axis=1)]
+
         if df.empty:
             print("Todos os leads coletados já foram descartados anteriormente. Pulando salvamento.")
             return 0
-            
+
+        df = df.copy()
         df['data_extracao'] = datetime.now()
-        
         if 'status' not in df.columns:
             df['status'] = 'ativo'
 
-        self.conn.register('df_temp', df)
+        colunas = [
+            'nome', 'telefone', 'tipo_telefone', 'whatsapp_link', 'instagram',
+            'site', 'bairro', 'cidade', 'estado', 'nicho', 'status', 'data_extracao',
+        ]
+        linhas = [
+            tuple(backend._valor(r.get(c)) for c in colunas)
+            for r in df.to_dict("records")
+        ]
 
         # UPSERT preservando o status atual e as colunas de log do WhatsApp.
         # Assim, re-raspar um lead já enviado NÃO apaga data_envio_whatsapp/status_whatsapp.
-        self.conn.execute("""
-            INSERT INTO leads (nome, telefone, tipo_telefone, whatsapp_link, instagram, site, bairro, cidade, estado, nicho, status, data_extracao)
-            SELECT nome, telefone, tipo_telefone, whatsapp_link, instagram, site, bairro, cidade, estado, nicho, status, data_extracao
-            FROM df_temp
-            ON CONFLICT (nome, cidade) DO UPDATE SET
-                telefone = excluded.telefone,
-                tipo_telefone = excluded.tipo_telefone,
-                whatsapp_link = excluded.whatsapp_link,
-                instagram = excluded.instagram,
-                site = excluded.site,
-                bairro = excluded.bairro,
-                estado = excluded.estado,
-                nicho = excluded.nicho,
-                data_extracao = excluded.data_extracao
-        """)
-
-        self.conn.unregister('df_temp')
+        backend.bulk_upsert(
+            self.conn,
+            table="leads",
+            columns=colunas,
+            rows=linhas,
+            conflict="nome, cidade",
+            set_clause=(
+                "telefone = excluded.telefone, "
+                "tipo_telefone = excluded.tipo_telefone, "
+                "whatsapp_link = excluded.whatsapp_link, "
+                "instagram = excluded.instagram, "
+                "site = excluded.site, "
+                "bairro = excluded.bairro, "
+                "estado = excluded.estado, "
+                "nicho = excluded.nicho, "
+                "data_extracao = excluded.data_extracao"
+            ),
+        )
+        backend.commit(self.conn)
         return len(df)
 
     def get_leads_para_envio(self, limite=None, numero=None, cidade=None, nicho=None):
@@ -238,7 +130,8 @@ class LeadDatabase:
         - cidade: filtra por nome exato da cidade
         - nicho:  filtra por nicho exato
         """
-        query = """
+        p = backend.ph()
+        query = f"""
             SELECT lead_id, nome, telefone, whatsapp_link, bairro, cidade, estado, nicho, chat_id_waha
             FROM leads
             WHERE status = 'ativo'
@@ -248,60 +141,65 @@ class LeadDatabase:
         params = []
         if numero:
             numero = re.sub(r"\D", "", str(numero))
-            query += " AND regexp_replace(telefone, '[^0-9]', '', 'g') LIKE ?"
+            query += f" AND regexp_replace(telefone, '[^0-9]', '', 'g') LIKE {p}"
             params.append(f"%{numero}%")
         if cidade:
-            query += " AND cidade = ?"
+            query += f" AND cidade = {p}"
             params.append(cidade)
         if nicho:
-            query += " AND nicho = ?"
+            query += f" AND nicho = {p}"
             params.append(nicho)
         query += " ORDER BY cidade, bairro, nome"
         if limite:
-            query += " LIMIT ?"
+            query += f" LIMIT {p}"
             params.append(int(limite))
-        return self.conn.execute(query, params).df()
+        return backend.query_df(self.conn, query, params)
 
     def salvar_chat_id_waha(self, nome, cidade, chat_id):
         """Cacheia o chatId resolvido (ex.: 143172869029943@lid) para não repetir
         a chamada ao /api/checkNumberStatus em envios futuros."""
-        self.conn.execute("""
+        p = backend.ph()
+        backend.execute(self.conn, f"""
             UPDATE leads
-            SET chat_id_waha = ?
-            WHERE nome = ? AND cidade = ?
+            SET chat_id_waha = {p}
+            WHERE nome = {p} AND cidade = {p}
         """, [chat_id, nome, cidade])
+        backend.commit(self.conn)
 
     def marcar_envio(self, nome, cidade, status_whatsapp):
         """Registra o resultado do envio. 'data_envio_whatsapp' é gravado apenas no sucesso."""
+        p = backend.ph()
         if status_whatsapp == 'enviado':
-            self.conn.execute("""
+            backend.execute(self.conn, f"""
                 UPDATE leads
-                SET status_whatsapp = ?, data_envio_whatsapp = ?
-                WHERE nome = ? AND cidade = ?
+                SET status_whatsapp = {p}, data_envio_whatsapp = {p}
+                WHERE nome = {p} AND cidade = {p}
             """, [status_whatsapp, datetime.now(), nome, cidade])
         else:
-            self.conn.execute("""
+            backend.execute(self.conn, f"""
                 UPDATE leads
-                SET status_whatsapp = ?
-                WHERE nome = ? AND cidade = ?
+                SET status_whatsapp = {p}
+                WHERE nome = {p} AND cidade = {p}
             """, [status_whatsapp, nome, cidade])
+        backend.commit(self.conn)
 
     def export_to_excel(self, nicho: str, cidade: str):
-        df = self.conn.execute("""
-            SELECT nome, telefone, tipo_telefone, whatsapp_link, instagram, site, bairro, data_extracao 
-            FROM leads 
-            WHERE nicho = ? AND cidade = ? AND status = 'ativo'
+        p = backend.ph()
+        df = backend.query_df(self.conn, f"""
+            SELECT nome, telefone, tipo_telefone, whatsapp_link, instagram, site, bairro, data_extracao
+            FROM leads
+            WHERE nicho = {p} AND cidade = {p} AND status = 'ativo'
             ORDER BY bairro, nome
-        """, [nicho, cidade]).df()
-        
+        """, [nicho, cidade])
+
         if df.empty:
             print("Nenhum dado ativo para exportar.")
             return
-            
+
         os.makedirs("output", exist_ok=True)
         nome_arquivo = f"output/leads_{nicho}_{cidade}.xlsx".replace(" ", "_").lower()
         df.to_excel(nome_arquivo, index=False)
         print(f"🎉 Exportação concluída: {nome_arquivo} ({len(df)} leads ativos)")
 
     def close(self):
-        self.conn.close()
\ No newline at end of file
+        backend.close(self.conn)
diff --git a/src/localidades_db.py b/src/localidades_db.py
index fbf1c56..d528ed8 100644
--- a/src/localidades_db.py
+++ b/src/localidades_db.py
@@ -1,22 +1,20 @@
 # src/localidades_db.py
-"""Cache local (DuckDB) da base de localidades do IBGE.
+"""Cache (PostgreSQL ou DuckDB) da base de localidades do IBGE.
 
 Guarda apenas o essencial, para não inflar o banco:
     localidades_estados     -> uf, nome
     localidades_municipios  -> id_municipio, nome, uf + estado da coleta de bairros
     localidades_bairros     -> id_municipio, nome, id_distrito
 
-O arquivo é o mesmo DuckDB dos leads (data/leads.duckdb). Cada operação abre e
-fecha a conexão, então o cache nunca segura o banco travado durante o scraping.
+Cada operação abre e fecha a conexão, então o cache nunca segura uma conexão
+aberta durante o scraping.
 """
-import os
 from contextlib import contextmanager
 from datetime import datetime
 
-import duckdb
 import pandas as pd
 
-DB_PATH_PADRAO = os.path.join("data", "leads.duckdb")
+from src import backend
 
 # Origem da lista de bairros gravada para uma cidade.
 FONTE_IBGE = "ibge"           # distritos do IBGE (quantidade suficiente)
@@ -25,143 +23,98 @@ FONTE_CIDADE = "cidade"       # nenhum bairro usado: busca a cidade inteira
 
 
 class CacheIndisponivel(Exception):
-    """Não foi possível abrir ou gravar a base local (ex.: arquivo travado)."""
-
-
-_DDL = (
-    """
-    CREATE TABLE IF NOT EXISTS localidades_estados (
-        uf VARCHAR PRIMARY KEY,
-        nome VARCHAR NOT NULL
-    )
-    """,
-    """
-    CREATE TABLE IF NOT EXISTS localidades_municipios (
-        id_municipio BIGINT PRIMARY KEY,
-        nome VARCHAR NOT NULL,
-        uf VARCHAR NOT NULL,
-        bairros_fonte VARCHAR,
-        bairros_atualizado_em TIMESTAMP
-    )
-    """,
-    """
-    CREATE TABLE IF NOT EXISTS localidades_bairros (
-        id_municipio BIGINT NOT NULL,
-        nome VARCHAR NOT NULL,
-        id_distrito BIGINT,
-        PRIMARY KEY (id_municipio, nome)
-    )
-    """,
-)
-
-
-# Se false, nenhuma DDL é executada: o cache é aberto somente para leitura.
-# Definido por `src/locations.py` a partir de LOCALIDADES_SALVAR.
-CRIAR_TABELAS = True
+    """Não foi possível abrir/gravar a base de localidades (ex.: servidor fora)."""
 
 
 @contextmanager
-def conexao(db_path=None):
-    caminho = db_path or DB_PATH_PADRAO
-    diretorio = os.path.dirname(caminho)
-    if diretorio:
-        os.makedirs(diretorio, exist_ok=True)
+def _conexao():
+    """Abre uma conexão transacional; commit no fim, rollback em caso de erro."""
     try:
-        con = duckdb.connect(caminho)
+        conn = backend.conectar()
     except Exception as e:
-        raise CacheIndisponivel(f"{caminho}: {e}") from e
+        raise CacheIndisponivel(f"não foi possível conectar ao banco: {e}") from e
     try:
-        if CRIAR_TABELAS:
-            for ddl in _DDL:
-                con.execute(ddl)
-        yield con
+        yield conn
+        backend.commit(conn)
+    except Exception:
+        if not backend.IS_DUCKDB:
+            conn.rollback()
+        raise
     finally:
-        con.close()
+        backend.close(conn)
 
 
-def _ler(con, sql, params=None):
-    """Executa uma leitura, traduzindo 'tabela não existe' em CacheIndisponivel."""
-    try:
-        return con.execute(sql, params) if params else con.execute(sql)
-    except duckdb.CatalogException as e:
-        raise CacheIndisponivel(
-            "tabelas de localidades não existem neste banco (rode a sincronização no menu)"
-        ) from e
+def _df(conn, sql, params=None):
+    return backend.query_df(conn, sql, params)
 
 
-def _inserir_lote(con, df, sql):
-    if df is None or df.empty:
-        return
-    con.register("_lote", df)
-    try:
-        con.execute(sql)
-    finally:
-        con.unregister("_lote")
+def _inserir_upsert(conn, table, columns, df, conflict, set_clause):
+    backend.bulk_upsert(
+        conn,
+        table=table,
+        columns=columns,
+        rows=backend.df_to_rows(df),
+        conflict=conflict,
+        set_clause=set_clause,
+    )
 
 
-def ler_estados(db_path=None):
-    with conexao(db_path) as con:
-        df = _ler(con, "SELECT uf, nome FROM localidades_estados ORDER BY nome").df()
+def ler_estados():
+    with _conexao() as conn:
+        df = _df(conn, "SELECT uf, nome FROM localidades_estados ORDER BY nome")
     return df.to_dict("records")
 
 
-def salvar_estados(registros, db_path=None):
+def salvar_estados(registros):
     df = pd.DataFrame(list(registros), columns=["uf", "nome"]).drop_duplicates("uf")
-    with conexao(db_path) as con:
-        _inserir_lote(con, df, """
-            INSERT INTO localidades_estados (uf, nome)
-            SELECT uf, nome FROM _lote
-            ON CONFLICT (uf) DO UPDATE SET nome = excluded.nome
-        """)
+    with _conexao() as conn:
+        _inserir_upsert(conn, "localidades_estados", ["uf", "nome"], df,
+                        conflict="uf", set_clause="nome = excluded.nome")
     return len(df)
 
 
-def ler_municipios(uf, db_path=None):
-    with conexao(db_path) as con:
-        df = _ler(con,
-            """SELECT id_municipio, nome, uf, bairros_fonte
-               FROM localidades_municipios WHERE uf = ? ORDER BY nome""",
-            [uf],
-        ).df()
+def ler_municipios(uf):
+    with _conexao() as conn:
+        df = _df(conn, """
+            SELECT id_municipio, nome, uf, bairros_fonte
+            FROM localidades_municipios WHERE uf = %s ORDER BY nome
+        """.replace("%s", backend.ph()), [uf])
     return df.to_dict("records")
 
 
-def ler_municipios_pendentes(uf, db_path=None):
+def ler_municipios_pendentes(uf):
     """Municípios da UF cujos bairros ainda não foram resolvidos (bairros_fonte nulo)."""
-    with conexao(db_path) as con:
-        df = _ler(con, """
+    with _conexao() as conn:
+        df = _df(conn, """
             SELECT id_municipio, nome
             FROM localidades_municipios
-            WHERE uf = ? AND bairros_fonte IS NULL
+            WHERE uf = %s AND bairros_fonte IS NULL
             ORDER BY nome
-        """, [uf]).df()
+        """.replace("%s", backend.ph()), [uf])
     return df.to_dict("records")
 
 
-def salvar_municipios(registros, db_path=None):
+def salvar_municipios(registros):
     df = pd.DataFrame(list(registros), columns=["id_municipio", "nome", "uf"])
     df = df.dropna(subset=["id_municipio"]).drop_duplicates("id_municipio")
-    with conexao(db_path) as con:
+    with _conexao() as conn:
         # UPSERT preserva bairros_fonte/bairros_atualizado_em já gravados.
-        _inserir_lote(con, df, """
-            INSERT INTO localidades_municipios (id_municipio, nome, uf)
-            SELECT id_municipio, nome, uf FROM _lote
-            ON CONFLICT (id_municipio) DO UPDATE SET
-                nome = excluded.nome,
-                uf = excluded.uf
-        """)
+        _inserir_upsert(conn, "localidades_municipios", ["id_municipio", "nome", "uf"], df,
+                        conflict="id_municipio",
+                        set_clause="nome = excluded.nome, uf = excluded.uf")
     return len(df)
 
 
-def buscar_municipio(cidade, uf, db_path=None):
+def buscar_municipio(cidade, uf):
     """Retorna {id_municipio, nome, uf, bairros_fonte} ou None se não estiver na base."""
-    with conexao(db_path) as con:
-        linha = _ler(con, """
+    p = backend.ph()
+    with _conexao() as conn:
+        linha = backend.query_one(conn, f"""
             SELECT id_municipio, nome, uf, bairros_fonte
             FROM localidades_municipios
-            WHERE uf = ? AND lower(nome) = lower(?)
+            WHERE uf = {p} AND lower(nome) = lower({p})
             LIMIT 1
-        """, [uf, cidade]).fetchone()
+        """, [uf, cidade])
     if not linha:
         return None
     return {
@@ -172,12 +125,12 @@ def buscar_municipio(cidade, uf, db_path=None):
     }
 
 
-def ler_bairros(id_municipio, db_path=None):
-    with conexao(db_path) as con:
-        df = _ler(con,
-            "SELECT nome FROM localidades_bairros WHERE id_municipio = ? ORDER BY nome",
-            [int(id_municipio)],
-        ).df()
+def ler_bairros(id_municipio):
+    with _conexao() as conn:
+        df = _df(conn,
+            "SELECT nome FROM localidades_bairros WHERE id_municipio = %s ORDER BY nome"
+            .replace("%s", backend.ph()), [int(id_municipio)],
+        )
     return df["nome"].tolist()
 
 
@@ -200,93 +153,84 @@ def _normalizar_bairros(registros):
     return df.drop_duplicates("nome")
 
 
-def salvar_bairros(id_municipio, registros, fonte, db_path=None):
+def salvar_bairros(id_municipio, registros, fonte):
     """Grava a lista final de bairros de uma cidade e marca a origem da coleta.
 
     A lista é autoritativa para a cidade: bairros que não estão nela são
-    removidos, para o cache não acumular nomes de uma coleta anterior.
-    `fonte` = 'ibge', 'overpass' ou 'cidade' (sem bairros úteis).
+    removidos (delete da cidade + re-insert), para o cache não acumular nomes
+    de uma coleta anterior. `fonte` = 'ibge', 'overpass' ou 'cidade'.
     """
     id_municipio = int(id_municipio)
     df = _normalizar_bairros(registros)
 
-    with conexao(db_path) as con:
+    with _conexao() as conn:
+        p = backend.ph()
         if df.empty:
-            con.execute(
-                "DELETE FROM localidades_bairros WHERE id_municipio = ?", [id_municipio]
-            )
+            backend.execute(conn, f"DELETE FROM localidades_bairros WHERE id_municipio = {p}",
+                            [id_municipio])
         else:
             df.insert(0, "id_municipio", id_municipio)
-            con.register("_lote", df)
-            try:
-                con.execute("""
-                    DELETE FROM localidades_bairros
-                    WHERE id_municipio = ?
-                      AND nome NOT IN (SELECT nome FROM _lote)
-                """, [id_municipio])
-                con.execute("""
-                    INSERT OR REPLACE INTO localidades_bairros (id_municipio, nome, id_distrito)
-                    SELECT id_municipio, nome, id_distrito FROM _lote
-                """)
-            finally:
-                con.unregister("_lote")
-
-        con.execute("""
+            # Autoritativo por cidade: apaga tudo da cidade e reinsere.
+            backend.execute(conn, f"DELETE FROM localidades_bairros WHERE id_municipio = {p}",
+                            [id_municipio])
+            _inserir_upsert(
+                conn, "localidades_bairros", ["id_municipio", "nome", "id_distrito"], df,
+                conflict="id_municipio, nome",
+                set_clause="id_distrito = excluded.id_distrito",
+            )
+
+        backend.execute(conn, f"""
             UPDATE localidades_municipios
-            SET bairros_fonte = ?, bairros_atualizado_em = ?
-            WHERE id_municipio = ?
+            SET bairros_fonte = {p}, bairros_atualizado_em = {p}
+            WHERE id_municipio = {p}
         """, [fonte, datetime.now(), id_municipio])
     return len(df)
 
 
-def salvar_distritos_bulk(distritos, min_bairros=3, db_path=None):
+def salvar_distritos_bulk(distritos, min_bairros=3):
     """Grava todos os distritos do IBGE de uma vez (sincronização completa).
 
-    É aditivo (INSERT OR REPLACE por id_municipio+nome): não apaga bairros que já
-    existem, para não destruir listas complementadas pelo OpenStreetMap.
+    É aditivo (upsert por id_municipio+nome): não apaga bairros que já existem,
+    para não destruir listas complementadas pelo OpenStreetMap.
 
     Marca como 'ibge' apenas os municípios com pelo menos `min_bairros` distritos
-    úteis (ou seja, desconsiderando o distrito que tem o mesmo nome da cidade).
-    Os demais continuam sem fonte definida e serão complementados via Overpass
-    na primeira consulta.
+    úteis (desconsiderando o distrito que tem o mesmo nome da cidade).
     """
     df = pd.DataFrame(list(distritos), columns=["id_municipio", "nome", "id_distrito"])
     df = df.dropna(subset=["id_municipio", "nome"]).drop_duplicates(["id_municipio", "nome"])
     df["id_distrito"] = df["id_distrito"].astype("Int64")
 
-    with conexao(db_path) as con:
-        _inserir_lote(con, df, """
-            INSERT OR REPLACE INTO localidades_bairros (id_municipio, nome, id_distrito)
-            SELECT id_municipio, nome, id_distrito FROM _lote
-        """)
-        con.execute("DROP TABLE IF EXISTS _cobertura")
-        con.execute("""
-            CREATE TEMP TABLE _cobertura AS
-            SELECT b.id_municipio
-            FROM localidades_bairros b
-            JOIN localidades_municipios m ON m.id_municipio = b.id_municipio
-            WHERE lower(b.nome) <> lower(m.nome)
-            GROUP BY b.id_municipio
-            HAVING COUNT(*) >= ?
-        """, [int(min_bairros)])
-        con.execute("""
+    with _conexao() as conn:
+        p = backend.ph()
+        _inserir_upsert(
+            conn, "localidades_bairros", ["id_municipio", "nome", "id_distrito"], df,
+            conflict="id_municipio, nome",
+            set_clause="id_distrito = excluded.id_distrito",
+        )
+        backend.execute(conn, f"""
             UPDATE localidades_municipios
-            SET bairros_fonte = ?, bairros_atualizado_em = ?
+            SET bairros_fonte = {p}, bairros_atualizado_em = {p}
             WHERE bairros_fonte IS NULL
-              AND id_municipio IN (SELECT id_municipio FROM _cobertura)
-        """, [FONTE_IBGE, datetime.now()])
-        con.execute("DROP TABLE IF EXISTS _cobertura")
+              AND id_municipio IN (
+                  SELECT b.id_municipio
+                  FROM localidades_bairros b
+                  JOIN localidades_municipios mm ON mm.id_municipio = b.id_municipio
+                  WHERE lower(b.nome) <> lower(mm.nome)
+                  GROUP BY b.id_municipio
+                  HAVING COUNT(*) >= {p}
+              )
+        """, [FONTE_IBGE, datetime.now(), int(min_bairros)])
     return len(df)
 
 
-def estatisticas(db_path=None):
-    with conexao(db_path) as con:
-        estados = _ler(con, "SELECT COUNT(*) FROM localidades_estados").fetchone()[0]
-        municipios = _ler(con, "SELECT COUNT(*) FROM localidades_municipios").fetchone()[0]
-        bairros = _ler(con, "SELECT COUNT(*) FROM localidades_bairros").fetchone()[0]
-        prontas = _ler(con, """
-            SELECT COUNT(*) FROM localidades_municipios WHERE bairros_fonte IS NOT NULL
-        """).fetchone()[0]
+def estatisticas():
+    with _conexao() as conn:
+        def _count(sql):
+            return backend.query_one(conn, sql)[0]
+        estados = _count("SELECT COUNT(*) FROM localidades_estados")
+        municipios = _count("SELECT COUNT(*) FROM localidades_municipios")
+        bairros = _count("SELECT COUNT(*) FROM localidades_bairros")
+        prontas = _count("SELECT COUNT(*) FROM localidades_municipios WHERE bairros_fonte IS NOT NULL")
     return {
         "estados": estados,
         "municipios": municipios,
diff --git a/src/locations.py b/src/locations.py
index 23d0a47..6cfcd91 100644
--- a/src/locations.py
+++ b/src/locations.py
@@ -1,5 +1,5 @@
 # src/locations.py
-"""Localidades (UF, cidade e bairros) com cache local em DuckDB.
+"""Localidades (UF, cidade e bairros) com cache em PostgreSQL.
 
 Fonte oficial: API de Localidades do IBGE.
     estados    -> /api/v1/localidades/estados
@@ -39,13 +39,10 @@ OVERPASS_ENDPOINTS = [
 # Se true: consulta o banco antes da API. Se false: sempre busca na API.
 USAR_CACHE = str_para_bool(os.environ.get("LOCALIDADES_USAR_CACHE"), padrao=True)
 
-# Se false: NUNCA grava na base local (nem cria tabelas). Funciona como
-# "somente leitura": o banco é consultado, mas nada é alterado.
+# Se false: NUNCA grava na base local. Funciona como "somente leitura":
+# o banco é consultado, mas nada é alterado.
 SALVAR = str_para_bool(os.environ.get("LOCALIDADES_SALVAR"), padrao=True)
 
-# Reflete a flag no módulo de acesso ao banco (controla a criação das tabelas).
-localidades_db.CRIAR_TABELAS = SALVAR
-
 # Quantidade mínima de distritos úteis para não precisar do OpenStreetMap.
 # Abaixo disso, a cidade é complementada com bairros do OSM.
 MIN_BAIRROS = max(1, env_int("LOCALIDADES_MIN_BAIRROS", 3))
diff --git a/src/main.py b/src/main.py
index 5887015..bcaf6b9 100644
--- a/src/main.py
+++ b/src/main.py
@@ -196,9 +196,8 @@ def enviar_whatsapp_menu():
 
     numero_f, cidade_f, nicho_f = _escolher_filtros()
 
-    pendentes = db.get_leads_para_envio(
-        limite=WAHA_LIMITE, numero=numero_f, cidade=cidade_f, nicho=nicho_f
-    )
+    # Busca todos os pendentes (sem limitar ainda) para mostrar o total disponível.
+    pendentes = db.get_leads_para_envio(numero=numero_f, cidade=cidade_f, nicho=nicho_f)
 
     if _confirmar("Deseja fazer um envio de teste antes? (S/N): "):
         testar_envio(db, mensagem, pendentes=pendentes)
@@ -208,9 +207,35 @@ def enviar_whatsapp_menu():
         db.close()
         return
 
-    print(f"\n{len(pendentes)} lead(s) celular(es) pendentes (fixos são ignorados).")
+    total_disponivel = len(pendentes)
+    print(f"\n{total_disponivel} lead(s) celular(es) pendentes (fixos são ignorados).")
+
+    # Quantidade (range): Enter = todos (respeitando o limite do .env, se houver).
     if WAHA_LIMITE:
-        print(f"Limite configurado: {WAHA_LIMITE} lead(s) por campanha.")
+        print(f"Limite configurado no .env: {WAHA_LIMITE} lead(s) por campanha.")
+        padrao = WAHA_LIMITE
+    else:
+        padrao = total_disponivel
+
+    entrada = input(
+        f"Quantos leads enviar? (Enter = {padrao}): "
+    ).strip()
+
+    if entrada:
+        if entrada.isdigit() and int(entrada) > 0:
+            quantidade = int(entrada)
+        else:
+            print("Valor inválido. Usando o padrão.")
+            quantidade = padrao
+    else:
+        quantidade = padrao
+
+    if WAHA_LIMITE and quantidade > WAHA_LIMITE:
+        print(f"Ajustando para o limite do .env ({WAHA_LIMITE}).")
+        quantidade = WAHA_LIMITE
+
+    quantidade = min(quantidade, total_disponivel)
+    pendentes = pendentes.head(quantidade)
 
     if not _confirmar(f"Enviar para {len(pendentes)} lead(s)? (S/N): "):
         print("Envio cancelado.")
@@ -221,7 +246,7 @@ def enviar_whatsapp_menu():
         db,
         mensagem_template=mensagem,
         intervalo=WAHA_INTERVALO,
-        limite=WAHA_LIMITE,
+        limite=quantidade,
         leads=pendentes,
     )
     db.close()
diff --git a/src/whatsapp.py b/src/whatsapp.py
index 4715b67..989db52 100644
--- a/src/whatsapp.py
+++ b/src/whatsapp.py
@@ -12,6 +12,7 @@ O módulo só envia para leads:
     - ainda não enviados (status_whatsapp = 'pendente' ou NULL)
 """
 import os
+import random
 import re
 import time
 
@@ -31,12 +32,86 @@ WAHA_ATIVO = str_para_bool(os.environ.get("WAHA_ATIVO"), padrao=True)
 # Se true, pula a coleta e vai direto para o envio (não coleta nada).
 SOMENTE_ENVIO = str_para_bool(os.environ.get("SOMENTE_ENVIO"), padrao=False)
 
-# Intervalo (segundos) entre envios e limite de leads por campanha.
-# WAHA_LIMITE vazio = sem limite (envia todos os pendentes).
+# ---------------------------------------------------------------------------
+# Cadência de envio (anti-bloqueio)
+# ---------------------------------------------------------------------------
+# Formato "X a cada Y segundos", ex.: WAHA_CADENCIA=3:60  -> 3 envios por minuto.
+# Os envios são distribuídos ALEATORIAMENTE dentro da janela de Y segundos,
+# evitando pausas fixas (15s, 15s, ...) que são mais fáceis de detectar.
+WAHA_CADENCIA = os.environ.get("WAHA_CADENCIA", "").strip()
+
+# Legado: WAHA_INTERVALO (pausa fixa) continua funcionando quando WAHA_CADENCIA
+# não é informado.
 WAHA_INTERVALO = int(os.environ.get("WAHA_INTERVALO", "13"))
+
+# Limite de leads por campanha. Vazio = sem limite.
 WAHA_LIMITE = os.environ.get("WAHA_LIMITE", "").strip()
 WAHA_LIMITE = int(WAHA_LIMITE) if WAHA_LIMITE else None
 
+
+def _parse_cadencia(valor):
+    """Interpreta "N:Y" -> (envios_por_janela, janela_segundos).
+
+    Retorna None quando o valor está vazio/inválido (usa o intervalo fixo).
+    """
+    if not valor:
+        return None
+    try:
+        envios, janela = valor.split(":", 1)
+        envios = int(envios.strip())
+        janela = int(janela.strip())
+    except (ValueError, AttributeError):
+        return None
+    if envios <= 0 or janela <= 0:
+        return None
+    return envios, janela
+
+
+def _intervalos_aleatorios(quantidade, janela_segundos):
+    """Gera as pausas (em segundos) para `quantidade` envios numa janela.
+
+    Distribui os envios em pontos aleatórios crescentes dentro da janela e
+    retorna a diferença entre pontos consecutivos — o intervalo entre cada envio
+    varia, mas o total da janela é respeitado.
+    """
+    if quantidade <= 1:
+        return [0]
+    # Pontos aleatórios crescentes: 1 envio em cada "fatia" da janela, com
+    # jitter dentro da fatia, garantindo tempos diferentes entre os envios.
+    pontos = sorted(
+        random.uniform((i * janela_segundos) / quantidade,
+                       ((i + 1) * janela_segundos) / quantidade)
+        for i in range(quantidade)
+    )
+    return [round(pontos[i + 1] - pontos[i], 2) for i in range(quantidade - 1)]
+
+
+def _pausas_cadencia(total, envios_janela, janela_segundos):
+    """Gera as pausas da campanha inteira respeitando a cadência.
+
+    Agrupa os `total` envios em janelas de `janela_segundos` segundos, com
+    `envios_janela` envios por janela (distribuídos aleatoriamente). Retorna uma
+    lista com `total - 1` pausas (uma entre cada par consecutivo).
+    """
+    if total <= 1:
+        return [0]
+
+    # Timestamp de envio de cada lead: janela + posição aleatória dentro dela.
+    tempos = []
+    for idx in range(total):
+        janela_idx = idx // envios_janela
+        pos_na_janela = idx % envios_janela
+        inicio = janela_idx * janela_segundos
+        # posição aleatória dentro da fatia correspondente a este envio
+        p = random.uniform(
+            inicio + (pos_na_janela * janela_segundos) / envios_janela,
+            inicio + ((pos_na_janela + 1) * janela_segundos) / envios_janela,
+        )
+        tempos.append(p)
+
+    tempos.sort()
+    return [round(tempos[i + 1] - tempos[i], 2) for i in range(len(tempos) - 1)]
+
 # Mensagem padrão (placeholder). Use {nome}, {bairro} e {cidade}.
 MENSAGEM_PADRAO = "Olá {nome}! Vi que vocês atendem no bairro {bairro}, em {cidade}. Podemos conversar?"
 
@@ -171,7 +246,7 @@ def disparar_campanha(db, mensagem_template=None, intervalo=13, limite=None, lea
 
     - db: instância de LeadDatabase
     - mensagem_template: texto com {nome}, {bairro}, {cidade} (usa MENSAGEM_PADRAO se None)
-    - intervalo: pausa em segundos entre envios (evita spam e banimento)
+    - intervalo: pausa fixa em segundos entre envios (usado se não houver cadência)
     - leads: DataFrame opcional já filtrado; se None, busca pendentes (com limite)
     """
     mensagem_template = mensagem_template or MENSAGEM_PADRAO
@@ -183,7 +258,17 @@ def disparar_campanha(db, mensagem_template=None, intervalo=13, limite=None, lea
         return
 
     total = len(leads)
-    print(f"Enviando para {total} lead(s) celular(es), com intervalo de {intervalo}s...")
+
+    # Cadência aleatória (ex.: 3 a cada 60s) tem prioridade sobre o intervalo fixo.
+    cadencia = _parse_cadencia(WAHA_CADENCIA)
+    if cadencia:
+        envios_janela, janela = cadencia
+        pausas = _pausas_cadencia(total, envios_janela, janela)
+        print(f"Enviando para {total} lead(s), cadência {envios_janela} a cada {janela}s "
+              f"(intervalos aleatórios)...")
+    else:
+        pausas = [intervalo] * max(0, total - 1)
+        print(f"Enviando para {total} lead(s), com intervalo fixo de {intervalo}s...")
 
     for i, (_, lead) in enumerate(leads.iterrows(), 1):
         texto = _renderizar_mensagem(mensagem_template, lead)
@@ -233,6 +318,6 @@ def disparar_campanha(db, mensagem_template=None, intervalo=13, limite=None, lea
             print(f"[{i}/{total}] FALHOU -> {nome} ({chat_id}): {erro}")
 
         if i < total:
-            time.sleep(intervalo)
+            time.sleep(pausas[i - 1])
 
     print("Campanha finalizada.")

``````

## Git Diffs Staged
``````diff

``````



# Instruction
# Instruções Mestras para o Assistente de IA (Map Scraper Project)

## 1. Persona e Idioma
- **Idioma:** Processe TODAS as solicitações, explicações, comentários de código e interações estritamente em **Português do Brasil (pt-BR)**.
- **Perfil:** Você é um Engenheiro de Software Sênior, especialista em Python, Web Scraping, Engenharia de Dados e boas práticas de arquitetura. Suas respostas devem ser técnicas, precisas e focadas na escalabilidade e manutenção do código.

## 2. Contexto Obrigatório (Leia ANTES de sugerir código)
- **A pasta `memory/` é a fonte da verdade:** Antes de sugerir qualquer alteração arquitetural, leia os arquivos da pasta `memory/` (especialmente o `01-arquitetura-e-modulos.md` e o `02-decisoes-e-armadilhas.md`). Eles contêm o histórico do "porquê" das decisões e os bugs já solucionados. Não sugira soluções que contradigam o que está documentado lá.
- **Módulos Críticos:** Preste atenção especial ao `src/database.py` (persistência e regras de negócio), `src/scraper.py` (coração do scraping e anti-bloqueio) e `src/locations.py` (cache do IBGE/OSM).

## 3. Regras de Ouro do Projeto (Armadilhas Conhecidas)
- **DuckDB é Single-Process:** O arquivo `data/leads.duckdb` só aceita UMA conexão por vez. Nunca sugira abrir conexões persistentes paralelas no mesmo processo. A classe `LeadDatabase` já gerencia isso.
- **Seletores do Google Maps são Frágeis:** O DOM do Google muda. Se for sugerir alterações no `scraper.py`, lembre-se de usar `try/except` e sempre manter o mecanismo de *fallback* e retry.
- **Instagram sem API:** A extração do Instagram é feita puramente via DOM (buscando links `href`). Não sugira o uso de bibliotecas instáveis de API do Instagram (como `instagpy`) se não for estritamente necessário, pois o Google Maps já entrega o link.
- **Localidades (IBGE vs OSM):** O IBGE não fornece bairros, apenas distritos. O `locations.py` usa o OSM como *fallback*. Se o OSM falhar, o código é projetado para **não gravar** o cache e tentar de novo depois. Mantenha essa lógica.

## 4. Padrões de Código e Estilo
- **Imports:** Sempre use imports absolutos (`from src.modulo import funcao`).
- **Configurações:** NUNCA faça hardcode de chaves, URLs ou limites. Tudo deve ser lido do `.env` usando os helpers do `src/config.py`.
- **Erros e Logs:** Use `print(f"[{contexto}] Mensagem de erro: {type(e).__name__} - {e}")` para facilitar a depuração. Siga o padrão visual dos logs já existentes.
- **Type Hints:** Use anotações de tipo (type hints) do Python sempre que possível para facilitar a leitura e manutenção.
- **Arquivos Novos:** Se criar um novo arquivo, siga o padrão de docstrings (explicando o propósito do módulo) e a divisão de responsabilidades (ex: um novo extrator deve ficar separado do banco de dados).

## 5. O que NÃO fazer
- Não sugira refatorações massivas (reescrever o projeto inteiro) sem que seja explicitamente pedido.
- Não adicione bibliotecas externas pesadas se a biblioteca padrão do Python ou as dependências atuais (Pandas, Playwright, DuckDB) já resolverem o problema.
- Não ignore a estrutura de pastas atual (`src/`, `data/`, `output/`, `memory/`).
