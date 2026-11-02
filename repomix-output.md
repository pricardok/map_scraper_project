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
````
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
README.md
repomix-instrucao.md
repomix.config.json
requirements.txt
````

# Files

## File: memory/04-como-contribuir.md
````markdown
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
````

## File: src/__init__.py
````python
1: 
````

## File: src/backend.py
````python
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
````

## File: src/utils.py
````python
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
````

## File: .dockerignore
````
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
````

## File: .gitkeep
````
1: 
````

## File: Dockerfile
````dockerfile
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
````

## File: src/coleta_auto.py
````python
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
 17:     RETOMAR_COLETA   pular cidades já concluídas (true/false, default true)
 18:     RECAPTURA_DIAS   refazer cidades concluídas há mais de N dias (default 30;
 19:                      0 = nunca refazer)
 20:     SEMEAR_PROGRESSO marcar como concluídas as cidades que já têm leads no banco
 21:                      na primeira execução (true/false, default true)
 22: 
 23: Uso:
 24:     python src/coleta_auto.py
 25: """
 26: import os
 27: import sys
 28: import time
 29: from datetime import datetime, timedelta
 30: 
 31: sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
 32: 
 33: from src.config import carregar_env, str_para_bool, env_int
 34: from src.locations import (
 35:     obter_estados,
 36:     obter_cidades,
 37:     obter_termos_busca,
 38:     aquecer_bairros_uf,
 39:     sincronizar_base_localidades,
 40: )
 41: from src.scraper import rodar_scraper_multithread
 42: from src.database import LeadDatabase
 43: 
 44: carregar_env()
 45: 
 46: NICHO = os.environ.get("NICHO", "barbearias").strip().lower()
 47: UFS = [u.strip().upper() for u in os.environ.get("UFS", "").split(",") if u.strip()]
 48: MAX_CIDADES = max(0, env_int("MAX_CIDADES", 0))
 49: MAX_BAIRROS = max(1, env_int("MAX_BAIRROS", 30))
 50: AQUECER_BAIRROS = str_para_bool(os.environ.get("AQUECER_BAIRROS"), padrao=False)
 51: SINCRONIZAR = str_para_bool(os.environ.get("SINCRONIZAR"), padrao=False)
 52: MOSTRAR_NAVEGADOR = str_para_bool(os.environ.get("MOSTRAR_NAVEGADOR"), padrao=False)
 53: EXPORTAR_EXCEL = str_para_bool(os.environ.get("EXPORTAR_EXCEL"), padrao=False)
 54: LOOP = str_para_bool(os.environ.get("LOOP"), padrao=False)
 55: LOOP_PAUSA_SEGUNDOS = max(0, env_int("LOOP_PAUSA_SEGUNDOS", 3600))
 56: RETOMAR = str_para_bool(os.environ.get("RETOMAR_COLETA"), padrao=True)
 57: RECAPTURA_DIAS = max(0, env_int("RECAPTURA_DIAS", 30))
 58: SEMEAR_PROGRESSO = str_para_bool(os.environ.get("SEMEAR_PROGRESSO"), padrao=True)
 59: 
 60: 
 61: def _resolver_ufs():
 62:     """UFs alvo: as da env, ou todas do IBGE se vazio."""
 63:     if UFS:
 64:         return UFS
 65:     df = obter_estados()
 66:     if df.empty:
 67:         return []
 68:     return sorted(df["uf"].tolist())
 69: 
 70: 
 71: def _coletar_cidade(db, cidade, uf):
 72:     print(f"\n=== {cidade}-{uf} ({NICHO}) ===")
 73:     termos = obter_termos_busca(cidade, uf, max_bairros=MAX_BAIRROS)
 74:     if RETOMAR:
 75:         db.progresso_iniciar(NICHO, uf, cidade, len(termos))
 76: 
 77:     stats = {}
 78:     df = rodar_scraper_multithread(
 79:         nicho=NICHO,
 80:         cidade=cidade,
 81:         uf=uf,
 82:         termos_lista=termos,
 83:         mostrar_navegador=MOSTRAR_NAVEGADOR,
 84:         save_callback=db.save_leads,
 85:         estatisticas=stats,
 86:     )
 87: 
 88:     if RETOMAR:
 89:         # Área que falhou (bloqueio/timeout) deixa a cidade como parcial, para
 90:         # ser tentada de novo em vez de ficar 30 dias marcada como concluída.
 91:         if stats.get("areas_erro"):
 92:             db.progresso_parcial(
 93:                 NICHO, uf, cidade, len(df),
 94:                 f"{stats['areas_erro']}/{stats.get('areas_total', 0)} área(s) sem coleta",
 95:             )
 96:         else:
 97:             db.progresso_concluir(NICHO, uf, cidade, len(df))
 98: 
 99:     if EXPORTAR_EXCEL and not df.empty:
100:         db.export_to_excel(NICHO, cidade)
101: 
102: 
103: def _cidade_ja_coletada(registro):
104:     """True quando a cidade já foi concluída dentro da janela de recaptura.
105: 
106:     Com RETOMAR_COLETA=false nada é pulado (comportamento antigo, que recomeça
107:     o país inteiro a cada ciclo).
108:     """
109:     if not RETOMAR or not registro:
110:         return False
111:     if (registro.get("status") or "").lower() != "concluida":
112:         return False
113:     if RECAPTURA_DIAS <= 0:
114:         return True
115: 
116:     concluido = registro.get("concluido_em")
117:     if concluido is None:
118:         return True
119:     return concluido >= datetime.now() - timedelta(days=RECAPTURA_DIAS)
120: 
121: 
122: def _carregar_progresso(db):
123:     """Carrega o progresso do nicho, semeando a partir dos leads na 1ª execução."""
124:     if not RETOMAR:
125:         return {}
126: 
127:     progresso = db.progresso_carregar(NICHO)
128:     if not progresso and SEMEAR_PROGRESSO:
129:         semeadas = db.semear_progresso_de_leads(NICHO)
130:         if semeadas:
131:             print(f"[progresso] {semeadas} cidade(s) com leads já gravados foram "
132:                   f"marcadas como concluídas (SEMEAR_PROGRESSO=true).")
133:         progresso = db.progresso_carregar(NICHO)
134: 
135:     if progresso:
136:         concluidas = sum(
137:             1 for r in progresso.values()
138:             if (r.get("status") or "").lower() == "concluida"
139:         )
140:         print(f"[progresso] {concluidas} cidade(s) concluída(s) no banco "
141:               f"(recaptura após {RECAPTURA_DIAS} dia(s)).")
142:     return progresso
143: 
144: 
145: def executar_ciclo():
146:     db = LeadDatabase()
147:     try:
148:         if SINCRONIZAR:
149:             sincronizar_base_localidades()
150: 
151:         ufs = _resolver_ufs()
152:         if not ufs:
153:             print("Nenhuma UF disponível. Abortando ciclo.")
154:             return
155: 
156:         progresso = _carregar_progresso(db)
157: 
158:         for uf in ufs:
159:             cidades = obter_cidades(uf)
160:             if not cidades:
161:                 print(f"[{uf}] nenhuma cidade encontrada. Pulando.")
162:                 continue
163: 
164:             if AQUECER_BAIRROS:
165:                 aquecer_bairros_uf(uf, max_cidades=MAX_CIDADES)
166: 
167:             pendentes = [c for c in cidades if not _cidade_ja_coletada(progresso.get((uf, c)))]
168:             if not pendentes:
169:                 print(f"[{uf}] {len(cidades)} cidade(s) já coletada(s). Pulando.")
170:                 continue
171: 
172:             if MAX_CIDADES:
173:                 pendentes = pendentes[:MAX_CIDADES]
174: 
175:             print(f"\n[{uf}] {len(pendentes)} de {len(cidades)} cidade(s) pendente(s) "
176:                   f"(nicho={NICHO}).")
177:             for cidade in pendentes:
178:                 try:
179:                     _coletar_cidade(db, cidade, uf)
180:                 except Exception as e:
181:                     print(f"[{cidade}-{uf}] ERRO: {type(e).__name__}: {e}")
182:                     if RETOMAR:
183:                         try:
184:                             db.progresso_erro(NICHO, uf, cidade, f"{type(e).__name__}: {e}")
185:                         except Exception:
186:                             pass
187:     finally:
188:         db.close()
189: 
190: 
191: def main():
192:     print(f"Map Scraper (auto) | nicho={NICHO} | UFs={UFS or 'todas'} | "
193:           f"max_cidades={MAX_CIDADES or 'todas'} | loop={LOOP} | "
194:           f"retomar={RETOMAR} | recaptura={RECAPTURA_DIAS}d")
195:     while True:
196:         executar_ciclo()
197:         if not LOOP:
198:             break
199:         print(f"\nCiclo concluído. Aguardando {LOOP_PAUSA_SEGUNDOS}s para o próximo...")
200:         time.sleep(LOOP_PAUSA_SEGUNDOS)
201: 
202: 
203: if __name__ == "__main__":
204:     main()
````

## File: src/config.py
````python
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
````

## File: src/schema.py
````python
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
122:     conn.execute("""
123:         CREATE TABLE IF NOT EXISTS coleta_progresso (
124:             nicho VARCHAR NOT NULL,
125:             uf VARCHAR NOT NULL,
126:             cidade VARCHAR NOT NULL,
127:             status VARCHAR NOT NULL DEFAULT 'pendente',
128:             termos_total INTEGER,
129:             leads_total INTEGER,
130:             tentativas INTEGER DEFAULT 0,
131:             erro VARCHAR,
132:             iniciado_em TIMESTAMP,
133:             atualizado_em TIMESTAMP,
134:             concluido_em TIMESTAMP,
135:             PRIMARY KEY (nicho, uf, cidade)
136:         )
137:     """)
138: 
139:     # Seed com id fixo (o templates no DuckDB não tem auto-incremento).
140:     conn.execute("""
141:         INSERT INTO templates_whatsapp (id, mensagem, descricao, segmento, ativo)
142:         SELECT 1, ?, 'Apresentação Agendamento Já', ?, TRUE
143:         WHERE NOT EXISTS (SELECT 1 FROM templates_whatsapp WHERE id = 1)
144:     """, [TEMPLATE_AGRUPAMENTO_PADRAO, TEMPLATE_SEGMENTO_PADRAO])
145: 
146: 
147: def _schema_postgres(conn):
148:     """Schema do PostgreSQL (ids identity; migração da tabela `leads`)."""
149:     from psycopg2 import sql
150: 
151:     cur = conn.cursor()
152:     cur.execute("CREATE SEQUENCE IF NOT EXISTS seq_leads_id")
153: 
154:     cur.execute("""
155:         CREATE TABLE IF NOT EXISTS leads (
156:             lead_id INTEGER NOT NULL DEFAULT nextval('seq_leads_id'),
157:             nome TEXT,
158:             telefone TEXT,
159:             tipo_telefone TEXT,
160:             whatsapp_link TEXT,
161:             instagram TEXT,
162:             site TEXT,
163:             bairro TEXT,
164:             cidade TEXT,
165:             estado TEXT,
166:             nicho TEXT,
167:             status TEXT DEFAULT 'ativo',
168:             data_extracao TIMESTAMP,
169:             data_envio_whatsapp TIMESTAMP,
170:             status_whatsapp TEXT DEFAULT 'pendente',
171:             chat_id_waha TEXT,
172:             PRIMARY KEY (lead_id),
173:             UNIQUE (nome, cidade)
174:         )
175:     """)
176:     cur.execute("""
177:         CREATE TABLE IF NOT EXISTS templates_whatsapp (
178:             id INTEGER GENERATED BY DEFAULT AS IDENTITY PRIMARY KEY,
179:             mensagem TEXT,
180:             descricao TEXT,
181:             segmento TEXT,
182:             ativo BOOLEAN DEFAULT TRUE
183:         )
184:     """)
185:     cur.execute("""
186:         CREATE TABLE IF NOT EXISTS whatsapp_envios_log (
187:             id INTEGER GENERATED BY DEFAULT AS IDENTITY PRIMARY KEY,
188:             lead_id INTEGER,
189:             nome TEXT,
190:             cidade TEXT,
191:             telefone TEXT,
192:             telefone_normalizado TEXT,
193:             chat_id TEXT,
194:             status TEXT,
195:             mensagem TEXT,
196:             payload TEXT,
197:             erro TEXT,
198:             data_envio TIMESTAMP
199:         )
200:     """)
201:     cur.execute("""
202:         CREATE TABLE IF NOT EXISTS localidades_estados (
203:             uf TEXT PRIMARY KEY,
204:             nome TEXT NOT NULL
205:         )
206:     """)
207:     cur.execute("""
208:         CREATE TABLE IF NOT EXISTS localidades_municipios (
209:             id_municipio BIGINT PRIMARY KEY,
210:             nome TEXT NOT NULL,
211:             uf TEXT NOT NULL,
212:             bairros_fonte TEXT,
213:             bairros_atualizado_em TIMESTAMP
214:         )
215:     """)
216:     cur.execute("""
217:         CREATE TABLE IF NOT EXISTS localidades_bairros (
218:             id_municipio BIGINT NOT NULL,
219:             nome TEXT NOT NULL,
220:             id_distrito BIGINT,
221:             PRIMARY KEY (id_municipio, nome)
222:         )
223:     """)
224:     cur.execute("""
225:         CREATE TABLE IF NOT EXISTS coleta_progresso (
226:             nicho TEXT NOT NULL,
227:             uf TEXT NOT NULL,
228:             cidade TEXT NOT NULL,
229:             status TEXT NOT NULL DEFAULT 'pendente',
230:             termos_total INTEGER,
231:             leads_total INTEGER,
232:             tentativas INTEGER DEFAULT 0,
233:             erro TEXT,
234:             iniciado_em TIMESTAMP,
235:             atualizado_em TIMESTAMP,
236:             concluido_em TIMESTAMP,
237:             PRIMARY KEY (nicho, uf, cidade)
238:         )
239:     """)
240: 
241:     # Migração do gap conhecido: leads sem PK/default no lead_id (banco antigo).
242:     cur.execute("ALTER TABLE leads ALTER COLUMN lead_id SET DEFAULT nextval('seq_leads_id')")
243: 
244:     cur.execute("""
245:         SELECT 1 FROM information_schema.table_constraints
246:         WHERE table_schema = 'public' AND table_name = 'leads'
247:           AND constraint_name = 'leads_pkey'
248:     """)
249:     if not cur.fetchone():
250:         cur.execute("ALTER TABLE leads ADD CONSTRAINT leads_pkey PRIMARY KEY (lead_id)")
251: 
252:     cur.execute("""
253:         SELECT 1 FROM information_schema.table_constraints
254:         WHERE table_schema = 'public' AND table_name = 'leads'
255:           AND constraint_name = 'leads_nome_cidade_key'
256:     """)
257:     if not cur.fetchone():
258:         cur.execute("ALTER TABLE leads ADD CONSTRAINT leads_nome_cidade_key UNIQUE (nome, cidade)")
259: 
260:     cur.execute("""
261:         SELECT setval('seq_leads_id',
262:             GREATEST((SELECT COALESCE(MAX(lead_id), 0) + 1 FROM leads), 1), false)
263:     """)
264: 
265:     # Seed sem informar id (coluna IDENTITY gera sozinha).
266:     cur.execute("""
267:         INSERT INTO templates_whatsapp (mensagem, descricao, segmento, ativo)
268:         SELECT %s, 'Apresentação Agendamento Já', %s, TRUE
269:         WHERE NOT EXISTS (SELECT 1 FROM templates_whatsapp)
270:     """, [TEMPLATE_AGRUPAMENTO_PADRAO, TEMPLATE_SEGMENTO_PADRAO])
271: 
272: 
273: def inicializar_schema(conn):
274:     """Cria sequences, tabelas, corrige schema antigo e popula os templates."""
275:     if backend.IS_DUCKDB:
276:         _schema_duckdb(conn)
277:     else:
278:         _schema_postgres(conn)
279:     backend.commit(conn)
280: 
281: 
282: def main():
283:     conn = backend.conectar()
284:     try:
285:         inicializar_schema(conn)
286:     finally:
287:         backend.close(conn)
288:     print(f"Schema inicializado ({DB_ENGINE}).")
289: 
290: 
291: if __name__ == "__main__":
292:     main()
````

## File: .repomixignore
````
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
````

## File: docker-compose.yml
````yaml
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
21:       # Retomada de onde parou + desempenho.
22:       RETOMAR_COLETA: ${RETOMAR_COLETA:-true}
23:       RECAPTURA_DIAS: ${RECAPTURA_DIAS:-30}
24:       SEMEAR_PROGRESSO: ${SEMEAR_PROGRESSO:-true}
25:       SCRAPER_THREADS: ${SCRAPER_THREADS:-3}
26:       BLOQUEAR_RECURSOS: ${BLOQUEAR_RECURSOS:-true}
27:       MAX_CONTEXTOS_POR_NAVEGADOR: ${MAX_CONTEXTOS_POR_NAVEGADOR:-40}
28:     volumes:
29:       # Banco local (modo DB_ENGINE=duckdb) e Excel gerado.
30:       - ./data:/app/data
31:       - ./output:/app/output
````

## File: repomix-instrucao.md
````markdown
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
````

## File: repomix.config.json
````json
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
````

## File: requirements.txt
````
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
````

## File: memory/00-resumo-projeto.md
````markdown
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
````

## File: memory/02-decisoes-e-armadilhas.md
````markdown
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
202: - O runner usa uma fila (`queue.Queue`) + N threads trabalhadoras
203:   (`SCRAPER_THREADS`). Cada worker tem seu próprio Chromium (thread-local,
204:   criado e fechado na mesma thread) e reusa entre as áreas da cidade.
205: - Os workers **não** escrevem no banco: devolvem o resultado por outra fila e o
206:   `save_callback` roda na thread principal, mantendo uma única conexão.
207: - O cooldown anti-captcha usa `_cooldown_lock` + variável global `_cooldown_ate`.
208: - `vistos`/`todos_leads` são tocados só pela thread principal (não precisa de
209:   lock).
210: 
211: ---
212: 
213: ## Retomada da coleta (`coleta_progresso`)
214: 
215: - A fonte da verdade do "onde parou" é a tabela `coleta_progresso`
216:   (`nicho, uf, cidade`) — **não** o `leads`, que não sabe se a cidade terminou.
217: - Só `status='concluida'` é pulado. `em_andamento` (container morto no meio),
218:   `parcial` (captcha/timeout em alguma área) e `erro` voltam para a fila no
219:   próximo ciclo.
220: - `RECAPTURA_DIAS=30` faz a cidade concluída voltar depois de 30 dias;
221:   `0` = nunca refazer.
222: - `SEMEAR_PROGRESSO=true` só roda quando a tabela está vazia e usa
223:   `ON CONFLICT DO NOTHING`: nunca sobrescreve progresso real.
224: - `RETOMAR_COLETA=false` restaura o comportamento antigo (refaz tudo a cada
225:   ciclo) — útil para um "passe" completo de atualização.
226: 
227: ### Limite do seed a partir de `leads`
228: 
229: `semear_progresso_de_leads` enxerga só cidades que **têm** lead. Cidade
230: coletada que voltou vazia (comum em município pequeno) não aparece em `leads`,
231: então é recolhida uma vez depois do restart — barato e sem duplicar.
232: 
233: ### Criar a tabela manualmente (PostgreSQL)
234: 
235: A tabela é criada sozinha na primeira gravação (`_garantir_tabela_progresso`)
236: e também por `python src/schema.py`. Se precisar criar na mão:
237: 
238: ```sql
239: CREATE TABLE IF NOT EXISTS coleta_progresso (
240:     nicho TEXT NOT NULL,
241:     uf TEXT NOT NULL,
242:     cidade TEXT NOT NULL,
243:     status TEXT NOT NULL DEFAULT 'pendente',
244:     termos_total INTEGER,
245:     leads_total INTEGER,
246:     tentativas INTEGER DEFAULT 0,
247:     erro TEXT,
248:     iniciado_em TIMESTAMP,
249:     atualizado_em TIMESTAMP,
250:     concluido_em TIMESTAMP,
251:     PRIMARY KEY (nicho, uf, cidade)
252: );
253: ```
254: 
255: Panorama:
256: 
257: ```sql
258: SELECT uf, status, COUNT(*)
259: FROM coleta_progresso
260: GROUP BY uf, status ORDER BY uf, status;
261: ```
262: 
263: ## CPU: o gargalo é o Chromium, não o Python
264: 
265: - `image`/`media`/`font` bloqueados (`BLOQUEAR_RECURSOS`) e flags de render
266:   reduzem bastante o uso de CPU; a extração continua igual (DOM).
267: - Escalar `SCRAPER_THREADS` acima de 3 não acelera: esbarra no
268:   `_marcar_bloqueio_global` do Google. Em máquina pequena, 1–2 threads.
269: - Se a CPU continuar em 100%, o próximo passo é limitar o container
270:   (`cpus: 1.5` no compose) — não adianta reduzir sleep, que não consome CPU.
271: 
272: ---
273: 
274: ## Coisas que parecem bug mas não são
275: 
276: - `"IBGE não publica bairros para X"` → cidade com 1 distrito (ver acima).
277: - `"Base local ... sem bairros (fonte: cidade)"` → já tentou, o OSM não tinha nada.
278: - `"LOCALIDADES_SALVAR=false: a base local não será alterada"` → modo leitura.
279: - `"Aviso: base local ... indisponível (arquivo em uso)"` → feche o DBeaver.
````

## File: src/localidades_db.py
````python
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
````

## File: memory/README.md
````markdown
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
````

## File: src/scraper.py
````python
  1: # src/scraper.py
  2: from playwright.sync_api import sync_playwright
  3: import os
  4: import queue
  5: import time
  6: import random
  7: import urllib.parse
  8: import pandas as pd
  9: import threading
 10: from src.config import env_int, str_para_bool
 11: from src.utils import formatar_telefone
 12: 
 13: USER_AGENT = (
 14:     "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
 15:     "AppleWebKit/537.36 (KHTML, like Gecko) "
 16:     "Chrome/124.0.0.0 Safari/537.36"
 17: )
 18: 
 19: MAX_ROLAGENS = 40
 20: MAX_RODADAS_ESTAGNADAS = 3
 21: 
 22: # --- Desempenho ---------------------------------------------------------------
 23: # SCRAPER_THREADS: navegadores rodando em paralelo por cidade. Cada Chromium é
 24: #   um processo pesado; em VPS pequena use 1 ou 2 para não saturar a CPU.
 25: # BLOQUEAR_RECURSOS: desliga imagens no próprio Chromium e aborta mídia/fontes
 26: #   (o Google Maps carrega muita imagem). A extração é feita no DOM
 27: #   (texto/atributos), então não é afetada.
 28: SCRAPER_THREADS = max(1, env_int("SCRAPER_THREADS", 3))
 29: BLOQUEAR_RECURSOS = str_para_bool(os.environ.get("BLOQUEAR_RECURSOS"), padrao=True)
 30: # Recicla o Chromium a cada N áreas para conter crescimento de memória em
 31: # execuções longas (o mesmo browser é reutilizado entre as áreas).
 32: MAX_CONTEXTOS_POR_NAVEGADOR = max(1, env_int("MAX_CONTEXTOS_POR_NAVEGADOR", 40))
 33: 
 34: _TIPOS_BLOQUEADOS = ("media", "font")
 35: 
 36: # Flags que reduzem trabalho de renderização/rede do Chromium.
 37: _CHROMIUM_ARGS = (
 38:     "--disable-dev-shm-usage",
 39:     "--disable-extensions",
 40:     "--disable-sync",
 41:     "--disable-default-apps",
 42:     "--disable-background-networking",
 43:     "--disable-background-timer-throttling",
 44:     "--disable-renderer-backgrounding",
 45:     "--disable-backgrounding-occluded-windows",
 46:     "--no-first-run",
 47:     "--no-default-browser-check",
 48:     "--mute-audio",
 49: )
 50: 
 51: 
 52: def _args_chromium():
 53:     """Flags do Chromium; desligar imagens no próprio browser é mais barato que
 54:     interceptar cada requisição no Python."""
 55:     args = list(_CHROMIUM_ARGS)
 56:     if BLOQUEAR_RECURSOS:
 57:         args.append("--blink-settings=imagesEnabled=false")
 58:     return args
 59: 
 60: # Reaproveitamento de navegador por thread: um Chromium novo por termo de busca
 61: # era o maior gasto de CPU do processo. Agora cada worker reusa o mesmo browser
 62: # e abre apenas um contexto isolado por termo.
 63: _tls = threading.local()
 64: 
 65: # --- Anti-bloqueio (captcha) -------------------------------------------------
 66: # CAPTCHA_MAX_TENTATIVAS: quantas vezes uma mesma página é tentada antes de
 67: #   abortar a área (1 = nem tenta de novo, só pausa e desiste).
 68: # CAPTCHA_PAUSA_SEGUNDOS: pausa longa feita pela thread que levou o bloqueio.
 69: # CAPTCHA_PAUSA_GLOBAL_SEGUNDOS: pausa compartilhada, aplicada a TODAS as
 70: #   threads assim que uma delas detecta bloqueio (evita que as outras insistam).
 71: CAPTCHA_MAX_TENTATIVAS = max(1, env_int("CAPTCHA_MAX_TENTATIVAS", 2))
 72: CAPTCHA_PAUSA_SEGUNDOS = max(0, env_int("CAPTCHA_PAUSA_SEGUNDOS", 300))
 73: CAPTCHA_PAUSA_GLOBAL_SEGUNDOS = max(0, env_int("CAPTCHA_PAUSA_GLOBAL_SEGUNDOS", 180))
 74: 
 75: _MARCADORES_CAPTCHA = (
 76:     "unusual traffic",
 77:     "tráfego incomum",
 78:     "trafego incomum",
 79:     "não é possível acessar",
 80:     "nao e possivel acessar",
 81:     "our systems have detected",
 82:     "digite os caracteres",
 83:     "não sou um robô",
 84:     "i'm not a robot",
 85: )
 86: 
 87: _SELETORES_BLOQUEIO = (
 88:     'form[action*="sorry"]',
 89:     "#captcha-form",
 90:     "#recaptcha",
 91:     ".g-recaptcha",
 92:     'iframe[src*="recaptcha"]',
 93:     'iframe[src*="hcaptcha"]',
 94: )
 95: 
 96: _cooldown_ate = 0.0
 97: _cooldown_lock = threading.Lock()
 98: 
 99: 
100: class BloqueioDetectado(Exception):
101:     """Google Maps devolveu captcha/tela de bloqueio para a busca atual."""
102: 
103: 
104: def _montar_query(nicho, termo_busca, cidade, uf):
105:     if termo_busca.strip().lower() == cidade.strip().lower():
106:         return f"{nicho} em {cidade}, {uf}"
107:     return f"{nicho} em {termo_busca}, {cidade}, {uf}"
108: 
109: 
110: def _pagina_bloqueada(page, checar_texto=True):
111:     """Detecta captcha / tela de 'tráfego incomum' do Google."""
112:     try:
113:         url = (page.url or "").lower()
114:     except Exception:
115:         return False
116:     if "/sorry/" in url:
117:         return True
118: 
119:     try:
120:         for seletor in _SELETORES_BLOQUEIO:
121:             if page.query_selector(seletor):
122:                 return True
123:     except Exception:
124:         return False
125: 
126:     if not checar_texto:
127:         return False
128: 
129:     try:
130:         texto = (page.inner_text("body") or "")[:4000].lower()
131:     except Exception:
132:         return False
133:     return any(marcador in texto for marcador in _MARCADORES_CAPTCHA)
134: 
135: 
136: def _marcar_bloqueio_global():
137:     """Coloca todas as threads em pausa (cooldown compartilhado)."""
138:     global _cooldown_ate
139:     if CAPTCHA_PAUSA_GLOBAL_SEGUNDOS <= 0:
140:         return
141:     with _cooldown_lock:
142:         _cooldown_ate = max(_cooldown_ate, time.time() + CAPTCHA_PAUSA_GLOBAL_SEGUNDOS)
143: 
144: 
145: def _aguardar_cooldown(termo):
146:     """Espera o cooldown global, se alguma thread detectou bloqueio."""
147:     with _cooldown_lock:
148:         restante = _cooldown_ate - time.time()
149:     if restante <= 0:
150:         return
151: 
152:     print(f"[{termo}] Pausa global anti-bloqueio: aguardando {int(restante) + 1}s...")
153:     while restante > 0:
154:         time.sleep(min(restante, 10))
155:         with _cooldown_lock:
156:             restante = _cooldown_ate - time.time()
157: 
158: 
159: def _pausar_com_aviso(segundos, termo):
160:     print(f"[{termo}] Aguardando {segundos}s (pausa longa anti-bloqueio)...")
161:     restante = segundos
162:     while restante > 0:
163:         passo = min(restante, 15)
164:         time.sleep(passo)
165:         restante -= passo
166: 
167: 
168: def _navegador_local(mostrar_navegador=False):
169:     """Playwright + Chromium reaproveitados na thread atual."""
170:     browser = getattr(_tls, "browser", None)
171:     if browser is not None:
172:         try:
173:             if (browser.is_connected()
174:                     and getattr(_tls, "contextos", 0) < MAX_CONTEXTOS_POR_NAVEGADOR):
175:                 _tls.contextos = getattr(_tls, "contextos", 0) + 1
176:                 return browser
177:         except Exception:
178:             pass
179:     fechar_navegador_local()
180: 
181:     playwright = sync_playwright().start()
182:     _tls.playwright = playwright
183:     _tls.browser = playwright.chromium.launch(
184:         headless=not mostrar_navegador,
185:         args=_args_chromium(),
186:     )
187:     _tls.contextos = 1
188:     return _tls.browser
189: 
190: 
191: def fechar_navegador_local():
192:     """Fecha o navegador da thread atual (chamado ao encerrar cada worker)."""
193:     browser = getattr(_tls, "browser", None)
194:     playwright = getattr(_tls, "playwright", None)
195:     _tls.browser = None
196:     _tls.playwright = None
197:     _tls.contextos = 0
198:     if browser is not None:
199:         try:
200:             browser.close()
201:         except Exception:
202:             pass
203:     if playwright is not None:
204:         try:
205:             playwright.stop()
206:         except Exception:
207:             pass
208: 
209: 
210: def _bloquear_recurso(route):
211:     """Aborta mídia e fontes (imagens já são desligadas por flag no browser)."""
212:     try:
213:         if route.request.resource_type in _TIPOS_BLOQUEADOS:
214:             route.abort()
215:         else:
216:             route.continue_()
217:     except Exception:
218:         pass
219: 
220: 
221: def _navegar_com_retry(page, url, tentativas=3, timeout=30000, termo="?"):
222:     """Navega com retry e backoff; detecta captcha e aplica pausa longa.
223: 
224:     Levanta BloqueioDetectado quando o bloqueio persiste após as tentativas.
225:     """
226:     for tentativa in range(1, tentativas + 1):
227:         _aguardar_cooldown(termo)
228:         try:
229:             page.goto(url, timeout=timeout)
230:         except Exception as e:
231:             print(f"  Retry {tentativa}/{tentativas} ao navegar para {url}: {type(e).__name__}")
232:             time.sleep(2 * tentativa)
233:             continue
234: 
235:         if not _pagina_bloqueada(page):
236:             return True
237: 
238:         _marcar_bloqueio_global()
239:         print(f"[{termo}] ⚠ Google Maps bloqueou o acesso (captcha/tráfego incomum).")
240: 
241:         if tentativa >= min(tentativas, CAPTCHA_MAX_TENTATIVAS):
242:             print(f"[{termo}] Bloqueio persistente após {tentativa} tentativa(s). Abortando esta área.")
243:             raise BloqueioDetectado(termo)
244: 
245:         _pausar_com_aviso(CAPTCHA_PAUSA_SEGUNDOS, termo)
246: 
247:     return False
248: 
249: 
250: def _obter_urls_perfis(page):
251:     urls = set()
252:     for link in page.query_selector_all('a[href*="/maps/place/"]'):
253:         href = link.get_attribute('href')
254:         if href:
255:             urls.add(href)
256:     return urls
257: 
258: 
259: # Conta os perfis direto no navegador: evita centenas de idas e voltas
260: # (query_selector_all + get_attribute) a cada rolagem.
261: _CONTAR_PERFIS_JS = """() => {
262:     const vistos = new Set();
263:     for (const a of document.querySelectorAll('a[href*="/maps/place/"]')) {
264:         vistos.add(a.href);
265:     }
266:     return vistos.size;
267: }"""
268: 
269: 
270: def _rolar_resultados(page, termo="?"):
271:     """Rola a lista até esgotar os resultados (ou atingir o limite de rolagens)."""
272:     ultimo_total = 0
273:     rodadas_estagnadas = 0
274:     for _ in range(MAX_ROLAGENS):
275:         if _pagina_bloqueada(page, checar_texto=False):
276:             _marcar_bloqueio_global()
277:             raise BloqueioDetectado(termo)
278: 
279:         total = page.evaluate(_CONTAR_PERFIS_JS) or 0
280:         page.evaluate('''() => {
281:             const feed = document.querySelector('div[role="feed"]');
282:             if(feed) feed.scrollTop = feed.scrollHeight;
283:         }''')
284:         time.sleep(1.0 + random.uniform(0, 0.6))  # jitter anti-bloqueio
285: 
286:         if total == ultimo_total:
287:             rodadas_estagnadas += 1
288:             if rodadas_estagnadas >= MAX_RODADAS_ESTAGNADAS:
289:                 break
290:         else:
291:             rodadas_estagnadas = 0
292:         ultimo_total = total
293: 
294: 
295: def extrair_leads_local(nicho, termo_busca, cidade, uf, mostrar_navegador=False):
296:     query = _montar_query(nicho, termo_busca, cidade, uf)
297:     url = f"https://www.google.com/maps/search/{urllib.parse.quote(query)}"
298:     leads = []
299:     _tls.area_incompleta = False
300: 
301:     context = None
302:     try:
303:         browser = _navegador_local(mostrar_navegador)
304:         context = browser.new_context(
305:             user_agent=USER_AGENT,
306:             viewport={"width": 1366, "height": 768},
307:             locale="pt-BR",
308:         )
309:         if BLOQUEAR_RECURSOS:
310:             context.route("**/*", _bloquear_recurso)
311:         page = context.new_page()
312: 
313:         if not _navegar_com_retry(page, url, timeout=60000, termo=termo_busca):
314:             print(f"[{termo_busca}] Falha ao carregar a busca.")
315:             _tls.area_incompleta = True
316:             return leads
317: 
318:         try:
319:             page.wait_for_selector('div[role="feed"]', timeout=10000)
320:         except Exception:
321:             print(f"[{termo_busca}] Nenhum resultado encontrado.")
322:             return leads
323: 
324:         print(f"[{termo_busca}] Rolando resultados...")
325:         _rolar_resultados(page, termo_busca)
326: 
327:         if _pagina_bloqueada(page):
328:             _marcar_bloqueio_global()
329:             raise BloqueioDetectado(termo_busca)
330: 
331:         urls = sorted(_obter_urls_perfis(page))
332:         print(f"[{termo_busca}] {len(urls)} perfis encontrados. Extraindo dados...")
333: 
334:         for i, place_url in enumerate(urls):
335:             try:
336:                 time.sleep(random.uniform(0.8, 2.5))  # pausa anti-bloqueio entre navegações
337:                 if not _navegar_com_retry(page, place_url, timeout=30000, termo=termo_busca):
338:                     continue
339:                 time.sleep(random.uniform(1.2, 2.8))
340: 
341:                 nome_elem = page.query_selector('h1')
342:                 nome = nome_elem.inner_text() if nome_elem else "Sem nome"
343:                 if nome in ("Resultados", ""):
344:                     continue
345: 
346:                 # Extração do Bairro (Endereço)
347:                 bairro_real = "Não Informado"
348:                 endereco_elem = page.query_selector('button[data-item-id="address"]')
349:                 if endereco_elem:
350:                     aria_endereco = endereco_elem.get_attribute('aria-label')
351:                     if aria_endereco:
352:                         texto_limpo = aria_endereco.replace('Endereço:', '').replace('Address:', '').strip()
353:                         try:
354:                             parts = texto_limpo.split(" - ")
355:                             if len(parts) >= 2:
356:                                 bairro_real = parts[1].split(",")[0].strip()
357:                         except Exception:
358:                             pass
359: 
360:                 # Extração do Telefone
361:                 telefone_bruto = ""
362:                 tel_elem = page.query_selector('button[data-item-id^="phone:tel:"]')
363:                 if tel_elem:
364:                     aria = tel_elem.get_attribute('aria-label')
365:                     if aria:
366:                         telefone_bruto = aria.replace('Telefone:', '').replace('Phone:', '').strip()
367: 
368:                 telefone_limpo, tipo_telefone, whatsapp_link = formatar_telefone(telefone_bruto)
369: 
370:                 link_site = ""
371:                 link_insta = ""
372: 
373:                 site_elem = page.query_selector('a[data-item-id="authority"]')
374:                 if site_elem:
375:                     link_site = site_elem.get_attribute('href')
376: 
377:                 insta_elem = page.query_selector('a[href*="instagram.com"]')
378:                 if insta_elem:
379:                     link_insta = insta_elem.get_attribute('href') or ""
380: 
381:                 leads.append({
382:                     'nome': nome,
383:                     'telefone': telefone_limpo,
384:                     'tipo_telefone': tipo_telefone,
385:                     'whatsapp_link': whatsapp_link,
386:                     'instagram': link_insta,
387:                     'site': link_site,
388:                     'bairro': bairro_real,
389:                     'cidade': cidade,
390:                     'estado': uf,
391:                     'nicho': nicho
392:                 })
393:                 print(f"[{termo_busca}] {i+1}/{len(urls)} - {nome} | {tipo_telefone} | {telefone_limpo}")
394: 
395:             except BloqueioDetectado:
396:                 raise
397:             except Exception as e:
398:                 print(f"[{termo_busca}] Erro ao extrair {place_url}: {e}")
399: 
400:     except BloqueioDetectado:
401:         _tls.area_incompleta = True
402:         print(f"[{termo_busca}] Área interrompida por bloqueio do Google Maps "
403:               f"({len(leads)} lead(s) preservado(s)).")
404:     finally:
405:         if context is not None:
406:             try:
407:                 context.close()
408:             except Exception:
409:                 pass
410: 
411:     return leads
412: 
413: 
414: def rodar_scraper_multithread(nicho, cidade, uf, termos_lista, mostrar_navegador=False,
415:                               save_callback=None, estatisticas=None):
416:     """
417:     Executa a coleta em multithread. Se save_callback for informado, cada lote
418:     (por área) é salvo assim que termina, evitando perder a coleta em caso de falha.
419: 
420:     Os workers reutilizam o mesmo Chromium entre as áreas (cada área abre apenas
421:     um contexto isolado) e o processamento/persistência acontece na thread
422:     principal, mantendo o acesso ao banco em uma única conexão.
423: 
424:     `estatisticas`, quando informado, recebe `areas_total`, `areas_ok` e
425:     `areas_erro` (áreas que terminaram sem coleta: bloqueio, timeout, crash).
426:     """
427:     todos_leads = []
428:     vistos = set()
429:     if estatisticas is not None:
430:         estatisticas.update({"areas_total": len(termos_lista), "areas_ok": 0, "areas_erro": 0})
431:     if not termos_lista:
432:         return pd.DataFrame(todos_leads)
433: 
434:     max_workers = min(SCRAPER_THREADS, len(termos_lista))
435:     print(f"Iniciando scraper com {max_workers} threads em {len(termos_lista)} área(s)...")
436: 
437:     pendentes = queue.Queue()
438:     for termo in termos_lista:
439:         pendentes.put(termo)
440:     resultados = queue.Queue()
441: 
442:     def _trabalhador():
443:         try:
444:             while True:
445:                 try:
446:                     termo = pendentes.get_nowait()
447:                 except queue.Empty:
448:                     return
449:                 try:
450:                     leads_area = extrair_leads_local(
451:                         nicho, termo, cidade, uf, mostrar_navegador
452:                     )
453:                     resultados.put(
454:                         (termo, leads_area, None, getattr(_tls, "area_incompleta", False))
455:                     )
456:                 except Exception as e:
457:                     resultados.put((termo, None, e, False))
458:         finally:
459:             fechar_navegador_local()
460: 
461:     threads = [
462:         threading.Thread(target=_trabalhador, daemon=True)
463:         for _ in range(max_workers)
464:     ]
465:     for t in threads:
466:         t.start()
467: 
468:     restantes = len(termos_lista)
469:     while restantes:
470:         try:
471:             termo, leads_area, erro, incompleta = resultados.get(timeout=0.5)
472:         except queue.Empty:
473:             if not any(t.is_alive() for t in threads):
474:                 break
475:             continue
476: 
477:         restantes -= 1
478:         if incompleta and estatisticas is not None:
479:             estatisticas["areas_erro"] += 1
480: 
481:         if erro is not None:
482:             print(f"Erro na busca {termo}: {erro}")
483:             if estatisticas is not None:
484:                 estatisticas["areas_erro"] += 1
485:             continue
486: 
487:         novos = []
488:         for lead in leads_area:
489:             chave = (lead['nome'], lead['cidade'])
490:             if chave not in vistos:
491:                 vistos.add(chave)
492:                 novos.append(lead)
493:         todos_leads.extend(novos)
494: 
495:         if estatisticas is not None:
496:             estatisticas["areas_ok"] += 1
497: 
498:         if novos and save_callback:
499:             save_callback(pd.DataFrame(novos))
500: 
501:         print(f"[{termo}] Finalizado. {len(novos)} leads novos (acumulado: {len(todos_leads)}).")
502: 
503:     for t in threads:
504:         t.join(timeout=30)
505: 
506:     return pd.DataFrame(todos_leads)
````

## File: .gitignore
````
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
````

## File: memory/03-historico-de-mudancas.md
````markdown
  1: # 03 — Histórico de Mudanças
  2: 
  3: Registro do que mudou, por quê e o que ficou pendente. Mais recente primeiro.
  4: 
  5: ---
  6: 
  7: ## 2026-11-02
  8: 
  9: ### Retomada de coleta (`coleta_progresso`)
 10: 
 11: - Antes: cada ciclo do `coleta_auto.py` percorria **todas** as UFs/cidades do
 12:   zero. Parar o container no meio de uma coleta nacional significava recomeçar
 13:   do Acre (os leads já gravados não duplicavam por causa do UPSERT, mas o
 14:   trabalho era refeito).
 15: - Nova tabela `coleta_progresso` (`nicho`, `uf`, `cidade` PK; `status`,
 16:   `termos_total`, `leads_total`, `tentativas`, `erro`, timestamps), criada de
 17:   forma idempotente pelo `LeadDatabase` na primeira gravação e também no
 18:   `schema.py`.
 19: - `LeadDatabase`: `progresso_carregar/iniciar/concluir/parcial/erro` e
 20:   `semear_progresso_de_leads`.
 21: - `coleta_auto.py`: `RETOMAR_COLETA=true` (padrão) filtra cidades já
 22:   concluídas; `RECAPTURA_DIAS` (padrão 30; `0` = nunca refazer) define quando
 23:   uma cidade concluída volta para a fila.
 24: - Cidade com área bloqueada (captcha/timeout) fica `parcial` e é tentada de
 25:   novo no ciclo seguinte — não fica 30 dias marcada como concluída.
 26: - `SEMEAR_PROGRESSO=true` (padrão): na primeira execução com a tabela vazia,
 27:   cidades que já têm leads no banco viram `concluida` (retoma uma coleta que
 28:   rodou antes deste recurso). Nunca sobrescreve progresso existente.
 29: - Validado nos dois backends: PostgreSQL (produção — tabela criada e semeada com
 30:   405 cidades, 5.166 restantes das 5.571) e DuckDB (setup novo).
 31: 
 32: ### CPU do scraper
 33: 
 34: - Navegador reaproveitado por thread: antes cada termo de busca abria um
 35:   Chromium novo (~30 launches por cidade). Agora cada worker mantém um Chromium
 36:   e abre só um contexto isolado por termo, reciclando o browser a cada
 37:   `MAX_CONTEXTOS_POR_NAVEGADOR` (padrão 40) para conter memória.
 38: - `BLOQUEAR_RECURSOS=true` (padrão) aborta `image`/`media`/`font` — a extração
 39:   é no DOM, então nada de dados se perde e a CPU cai.
 40: - Flags do Chromium para reduzir trabalho de renderização/rede.
 41: - Contagem de perfis na rolagem passou a ser feita em JS (`page.evaluate`) em
 42:   vez de `query_selector_all` + `get_attribute` por link a cada rolagem.
 43: - Busca de Instagram usa seletor direto (`a[href*="instagram.com"]`).
 44: - `SCRAPER_THREADS` (padrão 3) configurável: em VPS pequena, 1 ou 2.
 45: - Runner passou a usar fila + workers (`queue`) com persistência na thread
 46:   principal; `estatisticas` informa `areas_total/areas_ok/areas_erro`.
 47: 
 48: 
 49: ## 2026-10-31
 50: 
 51: ### Migração para PostgreSQL + suporte dual (PostgreSQL/DuckDB)
 52: 
 53: - Banco externo PostgreSQL (`vps.agendamentoja.com/leads_db`) + mantido o DuckDB
 54:   local como alternativa offline.
 55: - Novo `src/backend.py`: abstrai conexão, placeholder (`?`/`%s`), leitura
 56:   (DataFrame/tupla) e bulk upsert entre os dois bancos. `database.py`,
 57:   `localidades_db.py` e `schema.py` não importam mais `duckdb`/`psycopg2`.
 58: - `config.py` lê `DB_ENGINE` (postgres|duckdb), `DATABASE_URL` e `DUCKDB_PATH`.
 59:   Inferência: DUCKDB_PATH → duckdb; senão DATABASE_URL → postgres; senão duckdb.
 60: - `schema.py` reescrito para os dois bancos; corrige o gap da tabela `leads`
 61:   (PK `lead_id` + UNIQUE `(nome,cidade)` + default `nextval('seq_leads_id')`).
 62: - `requirements.txt`: readicionado `duckdb` + `psycopg2-binary`.
 63: - `.env`: seção "BANCO DE DADOS — engine independente" com `DATABASE_URL` (senha
 64:   com `@` percent-encoded) e config antiga comentada como referência.
 65: 
 66: ### Cadência aleatória de envio WhatsApp (anti-bloqueio)
 67: 
 68: - Nova `WAHA_CADENCIA="X:Y"` no `.env` (ex.: `3:60` = 3 envios por minuto).
 69: - `whatsapp.py`: `_parse_cadencia` + `_pausas_cadencia` distribuem os envios em
 70:   pontos **aleatórios** dentro de cada janela (pausas variáveis, não fixas).
 71: - Tem prioridade sobre `WAHA_INTERVALO` (fixo). `WAHA_CADENCIA` vazio → usa o fixo.
 72: 
 73: ### Tabela `whatsapp_envios_log` (rastreamento)
 74: 
 75: - Log por envio com `lead_id`, `telefone` (dígitos) e `telefone_normalizado`
 76:   (55DDDNUMERO), `chat_id`, `status`, `mensagem`, `payload`, `erro`, `data_envio`.
 77: - JOIN pronto por `lead_id` ou `telefone`.
 78: 
 79: ---
 80: 
 81: ## 2026-10-30
 82: 
 83: ### Templates de mensagem de WhatsApp (tabela + markdown)
 84: 
 85: - Nova tabela `templates_whatsapp` (`id`, `mensagem`, `descricao`, `ativo`),
 86:   criada e seedada no `LeadDatabase.__init__` (idempotente, `id=1` =
 87:   "Apresentação Agendamento Já").
 88: - `listar_templates_ativos()` retorna só os ativos para o menu de envio.
 89: - `_limpar_markdown_whatsapp` remove `**negrito**` e converte `[rótulo](url)` em
 90:   texto plano antes do envio (o template usa markdown; o WhatsApp não renderiza).
 91: 
 92: ### Menu de envio: template + filtros + teste
 93: 
 94: - `enviar_whatsapp_menu()` agora: escolhe template → aplica filtros → pergunta se
 95:   quer **teste de envio** → confirma e dispara.
 96: - Filtros de envio (menu "FILTROS DE ENVIO"): 0 todos / 1 por número / 2 por
 97:   cidade / 3 por nicho. Número aceita parte e compara só dígitos.
 98: - `testar_envio()`: digita um número com DDD ou escolhe um lead pendente.
 99: - `disparar_campanha` passou a aceitar `leads` (DataFrame já filtrado) — sem isso
100:   os filtros eram ignorados no disparo (ele reconsultava o banco).
101: 
102: ### Correção crítica: chatId `@lid` vs `@c.us` (WAHA)
103: 
104: - **Sintoma:** `500 Server Error` no `/api/sendText` para o número do mantenedor.
105: - **Causa:** número recente usa `@lid`; enviar `@c.us` retorna HTTP 500.
106: - **Correção:** `_resolver_chatid_waha` consulta `/api/checkNumberStatus` e usa o
107:   chatId retornado; fallback `@c.us` para números antigos.
108: - **Cache:** coluna `leads.chat_id_waha` + `salvar_chat_id_waha` — a resolução é
109:   feita uma única vez por lead (menos chamadas e reenvio mais rápido).
110: - `data_envio_whatsapp` continua gravada só no sucesso; `status_whatsapp` em
111:   `enviado`/`falhou`.
112: 
113: ---
114: 
115: ## 2026-10-29
116: 
117: ### Memória do projeto para IA
118: 
119: - Criada a pasta `memory/` com documentação densa para reduzir custo de contexto.
120: - Arquivos: `README.md`, `00-resumo-projeto.md`, `01-arquitetura-e-modulos.md`,
121:   `02-decisoes-e-armadilhas.md`, `03-historico-de-mudancas.md`,
122:   `04-como-contribuir.md` (padrões de código, logs, config, testes e docs).
123: - `README.md` limpo: removido o bloco "env temp:" (dump cru do `.env`) e
124:   adicionadas as seções 12 (memória para IA) e 13 (observação sobre configuração).
125: 
126: ### Correção: cache de bairros ignorado (`bairros_fonte`)
127: 
128: - **Sintoma:** com `LOCALIDADES_USAR_CACHE=true` e base populada, a coleta ainda
129:   consultava IBGE e Overpass.
130: - **Causa:** `localidades_db.ler_municipios()` não retornava `bairros_fonte`;
131:   `_resolver_municipio` repassava `None`, então o cache nunca era considerado.
132: - **Correção:** query passou a trazer `uf` e `bairros_fonte`; o resolver repassa
133:   o valor real.
134: - **Teste:** com as funções de rede trocadas por `AssertionError`, os bairros de
135:   Canoas (fonte `overpass`) e Bento Gonçalves (fonte `ibge`) vieram do banco.
136: 
137: ### Nome oficial do município (IBGE) na coleta
138: 
139: - `obter_municipio(cidade, uf)` confirma o município e devolve `id_municipio`,
140:   `nome` oficial e `uf`.
141: - `filtrar_cidades(cidades, termo)` compara **sem acento e sem caixa**:
142:   `canoas`, `sao leopoldo`, `CHAPECO` funcionam.
143: - `main.coletar_leads()` passa a usar o nome oficial no scraping, no banco e no
144:   nome do Excel, e imprime `Município (IBGE): Canoas-RS | código 4304606`.
145: - Lista de municípios **memoizada** por execução (`_municipios_da_uf`), evitando
146:   rebaixar a lista da UF a cada cidade (principalmente com `SALVAR=false`).
147: 
148: ### Mensagens de bairros mais honestas
149: 
150: - Antes: `IBGE retornou 0 distrito(s) útil(eis)`.
151: - Agora: `IBGE não publica bairros para Canoas-RS: o município tem apenas 1 distrito (a sede).`
152: - Motivo: a API de Localidades do IBGE **não tem bairros** (só distritos).
153: 
154: ### Aquecimento de bairros por UF (menu 4)
155: 
156: - `locations.aquecer_bairros_uf(uf, cidades=None, max_cidades=0, pausa_segundos=None)`.
157: - `localidades_db.ler_municipios_pendentes(uf)` → só `bairros_fonte IS NULL`.
158: - Retoma de onde parou; `Ctrl+C` preserva o que já foi gravado.
159: - Pausa (`AQUECER_PAUSA_SEGUNDOS`, default 2) só quando a cidade usou o OSM.
160: - Falha de rede não grava nada (`falhas` no resumo) e a cidade continua pendente.
161: - Bloqueado quando `LOCALIDADES_SALVAR=false`.
162: - Medido: AC 21 → 18 → 17 pendentes; SP 621 → 616.
163: 
164: ### Flag `LOCALIDADES_SALVAR`
165: 
166: - `false` = somente leitura: nenhuma escrita, **nem criação de tabelas**
167:   (`localidades_db.CRIAR_TABELAS = False`) e menus 3/4 desativados.
168: - Todas as escritas passam por `_salvar()`, que respeita a flag.
169: - Aviso único por execução para não poluir o log.
170: 
171: ### `.env` e `.env.example` comentados
172: 
173: - Cada variável com explicação, faixa de valores e efeito colateral.
174: - Tabela das 4 combinações `USAR_CACHE × SALVAR`.
175: - Regra explícita: comentário só em linha própria.
176: - Valores locais preservados (`USAR_CACHE=false` → depois `true`).
177: 
178: ### Base de localidades offline (IBGE) — menu 3
179: 
180: - Novo `src/localidades_db.py` com tabelas `localidades_estados`,
181:   `localidades_municipios`, `localidades_bairros` no mesmo `leads.duckdb`.
182: - `src/config.py` centraliza o loader do `.env` (antes duplicado no `whatsapp.py`).
183: - `src/locations.py` reescrito: cache → API → grava.
184: - Sync nacional: 27 estados, 5.571 municípios, 10.751 distritos; 643 cidades com
185:   bairros prontos pelo IBGE.
186: - Fallback OSM por cidade, gravado uma única vez.
187: 
188: ### Anti-captcha / bloqueio do Google Maps
189: 
190: - Detecção por URL `/sorry/`, seletores de captcha e textos ("tráfego incomum").
191: - Retry com pausa longa (`CAPTCHA_PAUSA_SEGUNDOS`) e **cooldown global**
192:   (`CAPTCHA_PAUSA_GLOBAL_SEGUNDOS`) entre todas as threads.
193: - Bloqueio persistente → aborta a área e **preserva os leads já extraídos**.
194: - Testado com Playwright real: página normal passa, página de captcha levanta
195:   `BloqueioDetectado` após `CAPTCHA_MAX_TENTATIVAS`.
196: 
197: ### Correção: menu não aparecia
198: 
199: - `src/main.py` definia `menu_interativo()` mas **nunca chamava**.
200: - Adicionado `if __name__ == "__main__": menu_interativo()`.
201: 
202: ### Banco DuckDB versionado
203: 
204: - `data/leads.duckdb` passou a ser versionado no Git.
205: - `.gitignore`: removidos `data/` e `*.duckdb` da lista de ignore; adicionados
206:   `*.duckdb.wal` e `*.duckdb.tmp`.
207: - `*.xlsx`, `*.csv`, `*.log` continuam ignorados (confirmado com
208:   `git check-ignore` e `git ls-files`).
209: - ⚠️ Comitar com o programa aberto sobe o `.duckdb` sem o `.wal` (dados
210:   desatualizados). Fechar antes.
211: 
212: ---
213: 
214: ## Pendências / próximos passos
215: 
216: | Item | Status |
217: |---|---|
218: | Bairros oficiais via CNEFE 2022 | **Não implementar por hora** (decisão do mantenedor) |
219: | Resolução automática de captcha (2Captcha/CapMonster) | Não implementado; hoje pausa e desiste da área |
220: | Enriquecimento de e-mail a partir dos sites | Não iniciado |
221: | Base de bairros offline nacional | Coberto parcialmente pelo IBGE (643 cidades) |
222: 
223: ## Problemas conhecidos (ambiente)
224: 
225: - **DBeaver aberto trava o DuckDB** → cache cai para as APIs.
226: - **Overpass/Nominatim instáveis** (502, timeout) → aquecimento por UF precisa de
227:   paciência e retomadas.
228: - Interprete global do mantenedor é Python 3.15; **usar `venv\Scripts\python.exe`**.
````

## File: src/locations.py
````python
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
````

## File: src/whatsapp.py
````python
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
````

## File: src/database.py
````python
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
 21:         self._progresso_pronto = False
 22: 
 23:     def listar_templates_ativos(self):
 24:         """Retorna os templates ativos como lista de dicionários (id, mensagem, descricao, segmento, ativo)."""
 25:         return (
 26:             backend.query_df(self.conn, """
 27:                 SELECT id, mensagem, descricao, segmento, ativo
 28:                 FROM templates_whatsapp
 29:                 WHERE ativo = TRUE
 30:                 ORDER BY id
 31:             """)
 32:             .to_dict("records")
 33:         )
 34: 
 35:     def salvar_log_envio(self, lead_id, nome, cidade, telefone, chat_id, status,
 36:                          mensagem=None, payload=None, erro=None):
 37:         """Grava uma linha de log de envio com os campos normalizados.
 38: 
 39:         - `lead_id`: referencia `leads.lead_id` (vínculo por PK).
 40:         - `telefone` é reduzido a dígitos (mesma representação de `leads.telefone`),
 41:           permitindo JOIN direto: leads.telefone = whatsapp_envios_log.telefone.
 42:         """
 43:         telefone = re.sub(r"\D", "", str(telefone or ""))
 44:         telefone_normalizado = None
 45:         if telefone.startswith("55") and len(telefone) > 11:
 46:             base = telefone[2:]
 47:         else:
 48:             base = telefone
 49:         if len(base) == 11:
 50:             telefone_normalizado = f"55{base}"
 51:         elif telefone:
 52:             telefone_normalizado = telefone
 53: 
 54:         payload_str = None
 55:         if payload is not None:
 56:             if isinstance(payload, (dict, list)):
 57:                 try:
 58:                     payload_str = json.dumps(payload, ensure_ascii=False, default=str)
 59:                 except Exception:
 60:                     payload_str = str(payload)
 61:             else:
 62:                 payload_str = str(payload)
 63: 
 64:         p = backend.ph()
 65:         backend.execute(self.conn, f"""
 66:             INSERT INTO whatsapp_envios_log
 67:                 (lead_id, nome, cidade, telefone, telefone_normalizado, chat_id,
 68:                  status, mensagem, payload, erro, data_envio)
 69:             VALUES ({p}, {p}, {p}, {p}, {p}, {p}, {p}, {p}, {p}, {p}, {p})
 70:         """, [
 71:             lead_id, nome, cidade, telefone or None, telefone_normalizado, chat_id,
 72:             status, mensagem, payload_str, erro, datetime.now(),
 73:         ])
 74:         backend.commit(self.conn)
 75: 
 76:     def save_leads(self, df: pd.DataFrame):
 77:         if df.empty:
 78:             return 0
 79: 
 80:         descartados = set(backend.query_all(
 81:             self.conn, "SELECT nome, cidade FROM leads WHERE status = 'descartado'"
 82:         ))
 83:         df = df[~df.apply(lambda row: (row['nome'], row['cidade']) in descartados, axis=1)]
 84: 
 85:         if df.empty:
 86:             print("Todos os leads coletados já foram descartados anteriormente. Pulando salvamento.")
 87:             return 0
 88: 
 89:         df = df.copy()
 90:         df['data_extracao'] = datetime.now()
 91:         if 'status' not in df.columns:
 92:             df['status'] = 'ativo'
 93: 
 94:         colunas = [
 95:             'nome', 'telefone', 'tipo_telefone', 'whatsapp_link', 'instagram',
 96:             'site', 'bairro', 'cidade', 'estado', 'nicho', 'status', 'data_extracao',
 97:         ]
 98:         linhas = [
 99:             tuple(backend._valor(r.get(c)) for c in colunas)
100:             for r in df.to_dict("records")
101:         ]
102: 
103:         # UPSERT preservando o status atual e as colunas de log do WhatsApp.
104:         # Assim, re-raspar um lead já enviado NÃO apaga data_envio_whatsapp/status_whatsapp.
105:         backend.bulk_upsert(
106:             self.conn,
107:             table="leads",
108:             columns=colunas,
109:             rows=linhas,
110:             conflict="nome, cidade",
111:             set_clause=(
112:                 "telefone = excluded.telefone, "
113:                 "tipo_telefone = excluded.tipo_telefone, "
114:                 "whatsapp_link = excluded.whatsapp_link, "
115:                 "instagram = excluded.instagram, "
116:                 "site = excluded.site, "
117:                 "bairro = excluded.bairro, "
118:                 "estado = excluded.estado, "
119:                 "nicho = excluded.nicho, "
120:                 "data_extracao = excluded.data_extracao"
121:             ),
122:         )
123:         backend.commit(self.conn)
124:         return len(df)
125: 
126:     def get_leads_para_envio(self, limite=None, numero=None, cidade=None, nicho=None):
127:         """Retorna leads ativos, celulares e ainda não enviados (evita spam/fixo).
128: 
129:         Filtros opcionais:
130:         - numero: filtra por telefone (completo ou parte; ignora não-dígitos)
131:         - cidade: filtra por nome exato da cidade
132:         - nicho:  filtra por nicho exato
133:         """
134:         p = backend.ph()
135:         query = f"""
136:             SELECT lead_id, nome, telefone, whatsapp_link, bairro, cidade, estado, nicho, chat_id_waha
137:             FROM leads
138:             WHERE status = 'ativo'
139:               AND tipo_telefone = 'Celular'
140:               AND (status_whatsapp IS NULL OR status_whatsapp = 'pendente')
141:         """
142:         params = []
143:         if numero:
144:             numero = re.sub(r"\D", "", str(numero))
145:             query += f" AND regexp_replace(telefone, '[^0-9]', '', 'g') LIKE {p}"
146:             params.append(f"%{numero}%")
147:         if cidade:
148:             query += f" AND cidade = {p}"
149:             params.append(cidade)
150:         if nicho:
151:             query += f" AND nicho = {p}"
152:             params.append(nicho)
153:         query += " ORDER BY cidade, bairro, nome"
154:         if limite:
155:             query += f" LIMIT {p}"
156:             params.append(int(limite))
157:         return backend.query_df(self.conn, query, params)
158: 
159:     def salvar_chat_id_waha(self, nome, cidade, chat_id):
160:         """Cacheia o chatId resolvido (ex.: 143172869029943@lid) para não repetir
161:         a chamada ao /api/checkNumberStatus em envios futuros."""
162:         p = backend.ph()
163:         backend.execute(self.conn, f"""
164:             UPDATE leads
165:             SET chat_id_waha = {p}
166:             WHERE nome = {p} AND cidade = {p}
167:         """, [chat_id, nome, cidade])
168:         backend.commit(self.conn)
169: 
170:     def marcar_envio(self, nome, cidade, status_whatsapp):
171:         """Registra o resultado do envio. 'data_envio_whatsapp' é gravado apenas no sucesso."""
172:         p = backend.ph()
173:         if status_whatsapp == 'enviado':
174:             backend.execute(self.conn, f"""
175:                 UPDATE leads
176:                 SET status_whatsapp = {p}, data_envio_whatsapp = {p}
177:                 WHERE nome = {p} AND cidade = {p}
178:             """, [status_whatsapp, datetime.now(), nome, cidade])
179:         else:
180:             backend.execute(self.conn, f"""
181:                 UPDATE leads
182:                 SET status_whatsapp = {p}
183:                 WHERE nome = {p} AND cidade = {p}
184:             """, [status_whatsapp, nome, cidade])
185:         backend.commit(self.conn)
186: 
187:     def export_to_excel(self, nicho: str, cidade: str):
188:         p = backend.ph()
189:         df = backend.query_df(self.conn, f"""
190:             SELECT nome, telefone, tipo_telefone, whatsapp_link, instagram, site, bairro, data_extracao
191:             FROM leads
192:             WHERE nicho = {p} AND cidade = {p} AND status = 'ativo'
193:             ORDER BY bairro, nome
194:         """, [nicho, cidade])
195: 
196:         if df.empty:
197:             print("Nenhum dado ativo para exportar.")
198:             return
199: 
200:         os.makedirs("output", exist_ok=True)
201:         nome_arquivo = f"output/leads_{nicho}_{cidade}.xlsx".replace(" ", "_").lower()
202:         df.to_excel(nome_arquivo, index=False)
203:         print(f"🎉 Exportação concluída: {nome_arquivo} ({len(df)} leads ativos)")
204: 
205:     # ------------------------------------------------------------------
206:     # Progresso da coleta (permite retomar de onde parou)
207:     # ------------------------------------------------------------------
208:     def _garantir_tabela_progresso(self):
209:         """Cria `coleta_progresso` na primeira utilização (idempotente)."""
210:         if self._progresso_pronto:
211:             return
212: 
213:         tipo = "VARCHAR" if backend.IS_DUCKDB else "TEXT"
214:         backend.execute(self.conn, f"""
215:             CREATE TABLE IF NOT EXISTS coleta_progresso (
216:                 nicho {tipo} NOT NULL,
217:                 uf {tipo} NOT NULL,
218:                 cidade {tipo} NOT NULL,
219:                 status {tipo} NOT NULL DEFAULT 'pendente',
220:                 termos_total INTEGER,
221:                 leads_total INTEGER,
222:                 tentativas INTEGER DEFAULT 0,
223:                 erro {tipo},
224:                 iniciado_em TIMESTAMP,
225:                 atualizado_em TIMESTAMP,
226:                 concluido_em TIMESTAMP,
227:                 PRIMARY KEY (nicho, uf, cidade)
228:             )
229:         """)
230:         backend.commit(self.conn)
231:         self._progresso_pronto = True
232: 
233:     def progresso_carregar(self, nicho):
234:         """Retorna {(uf, cidade): {status, tentativas, leads_total, concluido_em}}."""
235:         self._garantir_tabela_progresso()
236:         p = backend.ph()
237:         linhas = backend.query_all(self.conn, f"""
238:             SELECT uf, cidade, status, tentativas, leads_total, concluido_em
239:             FROM coleta_progresso
240:             WHERE nicho = {p}
241:         """, [nicho])
242:         return {
243:             (uf, cidade): {
244:                 "status": status,
245:                 "tentativas": tentativas or 0,
246:                 "leads_total": leads_total or 0,
247:                 "concluido_em": concluido_em,
248:             }
249:             for uf, cidade, status, tentativas, leads_total, concluido_em in linhas
250:         }
251: 
252:     def progresso_iniciar(self, nicho, uf, cidade, termos_total):
253:         """Marca a cidade como em andamento (incrementa o contador de tentativas)."""
254:         self._garantir_tabela_progresso()
255:         p = backend.ph()
256:         linha = backend.query_one(self.conn, f"""
257:             SELECT tentativas FROM coleta_progresso
258:             WHERE nicho = {p} AND uf = {p} AND cidade = {p}
259:         """, [nicho, uf, cidade])
260:         tentativas = (int(linha[0] or 0) if linha else 0) + 1
261:         agora = datetime.now()
262:         backend.execute(self.conn, f"""
263:             INSERT INTO coleta_progresso
264:                 (nicho, uf, cidade, status, termos_total, tentativas,
265:                  erro, iniciado_em, atualizado_em, concluido_em)
266:             VALUES ({p}, {p}, {p}, {p}, {p}, {p}, NULL, {p}, {p}, NULL)
267:             ON CONFLICT (nicho, uf, cidade) DO UPDATE SET
268:                 status = excluded.status,
269:                 termos_total = excluded.termos_total,
270:                 tentativas = excluded.tentativas,
271:                 erro = NULL,
272:                 iniciado_em = excluded.iniciado_em,
273:                 atualizado_em = excluded.atualizado_em,
274:                 concluido_em = NULL
275:         """, [nicho, uf, cidade, "em_andamento", int(termos_total), tentativas, agora, agora])
276:         backend.commit(self.conn)
277: 
278:     def progresso_concluir(self, nicho, uf, cidade, leads_total=0):
279:         """Marca a cidade como concluída."""
280:         self._garantir_tabela_progresso()
281:         p = backend.ph()
282:         agora = datetime.now()
283:         backend.execute(self.conn, f"""
284:             UPDATE coleta_progresso
285:             SET status = {p}, leads_total = {p}, erro = NULL,
286:                 atualizado_em = {p}, concluido_em = {p}
287:             WHERE nicho = {p} AND uf = {p} AND cidade = {p}
288:         """, ["concluida", int(leads_total or 0), agora, agora, nicho, uf, cidade])
289:         backend.commit(self.conn)
290: 
291:     def progresso_erro(self, nicho, uf, cidade, erro):
292:         """Registra a falha da cidade (será tentada novamente no próximo ciclo)."""
293:         self._garantir_tabela_progresso()
294:         p = backend.ph()
295:         backend.execute(self.conn, f"""
296:             UPDATE coleta_progresso
297:             SET status = {p}, erro = {p}, atualizado_em = {p}
298:             WHERE nicho = {p} AND uf = {p} AND cidade = {p}
299:         """, ["erro", str(erro)[:500], datetime.now(), nicho, uf, cidade])
300:         backend.commit(self.conn)
301: 
302:     def progresso_parcial(self, nicho, uf, cidade, leads_total, motivo):
303:         """Cidade coletada em parte (bloqueio/timeout em alguma área).
304: 
305:         Fica fora do filtro de "concluída" para ser tentada de novo no próximo
306:         ciclo, sem perder os leads já gravados.
307:         """
308:         self._garantir_tabela_progresso()
309:         p = backend.ph()
310:         backend.execute(self.conn, f"""
311:             UPDATE coleta_progresso
312:             SET status = {p}, leads_total = {p}, erro = {p}, atualizado_em = {p}
313:             WHERE nicho = {p} AND uf = {p} AND cidade = {p}
314:         """, ["parcial", int(leads_total or 0), str(motivo)[:500], datetime.now(),
315:               nicho, uf, cidade])
316:         backend.commit(self.conn)
317: 
318:     def semear_progresso_de_leads(self, nicho):
319:         """Marca como concluídas as cidades que já possuem leads no banco.
320: 
321:         Serve para retomar a partir de uma coleta que rodou antes de existir o
322:         progresso. É idempotente e nunca sobrescreve um registro já existente.
323:         Retorna quantas cidades foram marcadas.
324:         """
325:         self._garantir_tabela_progresso()
326:         p = backend.ph()
327:         linhas = backend.query_all(self.conn, f"""
328:             SELECT estado, cidade, COUNT(*) AS total, MAX(data_extracao) AS ultima
329:             FROM leads
330:             WHERE nicho = {p} AND estado IS NOT NULL AND cidade IS NOT NULL
331:             GROUP BY estado, cidade
332:         """, [nicho])
333: 
334:         agora = datetime.now()
335:         for uf, cidade, total, ultima in linhas:
336:             backend.execute(self.conn, f"""
337:                 INSERT INTO coleta_progresso
338:                     (nicho, uf, cidade, status, leads_total, tentativas,
339:                      iniciado_em, atualizado_em, concluido_em)
340:                 VALUES ({p}, {p}, {p}, {p}, {p}, 1, {p}, {p}, {p})
341:                 ON CONFLICT (nicho, uf, cidade) DO NOTHING
342:             """, [
343:                 nicho, uf, cidade, "concluida", int(total or 0),
344:                 ultima or agora, ultima or agora, ultima or agora,
345:             ])
346:         backend.commit(self.conn)
347:         return len(linhas)
348: 
349:     def close(self):
350:         backend.close(self.conn)
````

## File: src/main.py
````python
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
````

## File: README.md
````markdown
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
125:     RETOMAR_COLETA=true       # pular cidades já concluídas (retoma de onde parou)
126:     RECAPTURA_DIAS=30         # refazer concluídas há mais de N dias (0 = nunca)
127:     SEMEAR_PROGRESSO=true     # 1ª execução: cidades com leads viram concluídas
128:     SCRAPER_THREADS=3         # navegadores em paralelo (VPS pequena: 1 ou 2)
129:     BLOQUEAR_RECURSOS=true    # desliga imagens/mídia (reduz CPU)
130:     MAX_CONTEXTOS_POR_NAVEGADOR=40  # recicla o Chromium a cada N áreas
131:     ```
132: 
133:     Os comentários acima são ilustrativos. No `.env` real o comentário deve ficar
134:     em linha própria — na mesma linha ele passa a fazer parte do valor.
135: 
136:     Subir e acompanhar:
137: 
138:     ```
139:     docker compose up -d --build
140:     docker compose logs -f app
141:     ```
142: 
143:     Os comandos do dia a dia (rebuild, parar, reiniciar, ver progresso) estão
144:     na seção 14; sem Docker, use a seção 15.
145: 
146:     O `.env` é injetado no container via `env_file` (banco e WAHA). Os volumes
147:     `./data` e `./output` são montados para persistir DuckDB/Excel localmente.
148: 
149: 
150: 6. Gerenciamento do Banco de Dados (Regras de Negócio)
151: 
152:     Se você quiser descartar um lead para que ele não seja mais exportado e não seja atualizado nas próximas buscas, você pode rodar um comando SQL direto no DuckDB (via DBeaver ou script Python):
153: 
154:     sql
155:     -- Para descartar um lead
156:     UPDATE leads SET status = 'descartado' WHERE nome = 'Nome da Barbearia';
157: 
158:     -- Para reativar um lead
159:     UPDATE leads SET status = 'ativo' WHERE nome = 'Nome da Barbearia';
160:     Nota: A regra do UPSERT no database.py garante que, se o robô achar uma barbearia "descartada", ele pula ela e não sobrescreve seus dados no banco.
161: 
162: 7. Envio de WhatsApp (WAHA)
163: 
164:     Pré-requisito: uma instância WAHA rodando com um número conectado via QR Code.
165: 
166:     Configuração (arquivo .env na raiz do projeto):
167:     Copie .env.example para .env e preencha os valores.
168: 
169:     ```
170:     WAHA_API_URL=http://localhost:3000
171:     WAHA_API_KEY=SUA_CHAVE_AQUI
172:     WAHA_SESSION=default
173:     WAHA_ATIVO=true
174:     SOMENTE_ENVIO=false
175:     WAHA_INTERVALO=13
176:     WAHA_LIMITE=
177:     ```
178: 
179:     Flags de comportamento:
180:     - WAHA_ATIVO: se false, desliga o envio de WhatsApp (não tenta enviar).
181:     - SOMENTE_ENVIO: se true, pula a coleta e vai direto para o envio
182:       (equivalente a rodar `python src/main.py --so-enviar`).
183:     - WAHA_LIMITE: quantidade máxima de leads por campanha (vazio = sem limite).
184: 
185:     Regras de envio (evita spam):
186:     - Só envia para leads com status = 'ativo'.
187:     - Só envia para tipo_telefone = 'Celular' (fixos são ignorados).
188:     - Só envia para leads ainda não enviados (status_whatsapp = 'pendente' ou NULL).
189:     - Intervalo de WAHA_INTERVALO segundos entre envios.
190: 
191:     Logs no banco:
192:     - status_whatsapp: 'pendente', 'enviado' ou 'falhou'.
193:     - data_envio_whatsapp: gravada apenas quando o envio é bem-sucedido.
194: 
195:     A mensagem pode usar as variáveis {nome}, {bairro} e {cidade}.
196: 
197: 
198: 8. Base de Localidades Offline (IBGE)
199: 
200:     O projeto mantém um cache local das localidades no próprio DuckDB, criado na
201:     primeira consulta e reaproveitado nas seguintes (sem rede).
202: 
203:     Tabelas criadas automaticamente (guardam apenas o essencial):
204:     - localidades_estados: uf, nome
205:     - localidades_municipios: id_municipio, nome, uf + estado da coleta de bairros
206:     - localidades_bairros: id_municipio, nome, id_distrito
207: 
208:     Fontes (API de Localidades do IBGE):
209:     - Estados:    https://servicodados.ibge.gov.br/api/v1/localidades/estados
210:     - Municípios: https://servicodados.ibge.gov.br/api/v1/localidades/municipios
211:     - Distritos:  https://servicodados.ibge.gov.br/api/v1/localidades/distritos
212: 
213:     Configuração (.env):
214:     ```
215:     LOCALIDADES_USAR_CACHE=true
216:     LOCALIDADES_SALVAR=true
217:     LOCALIDADES_MIN_BAIRROS=3
218:     AQUECER_PAUSA_SEGUNDOS=2
219:     ```
220: 
221:     - LOCALIDADES_USAR_CACHE=true (padrão): consulta o banco primeiro e só chama a
222:       API quando o dado ainda não existe (e aí grava o resultado).
223:     - LOCALIDADES_USAR_CACHE=false: sempre busca na API do IBGE e atualiza a base
224:       local com o que voltou.
225:     - LOCALIDADES_SALVAR=false: modo somente leitura. Nada é gravado e nem as
226:       tabelas são criadas; o banco só é consultado. A sincronização do menu fica
227:       desativada.
228:     - LOCALIDADES_MIN_BAIRROS: mínimo de distritos do IBGE para a cidade ser
229:       considerada coberta. Abaixo disso, os bairros são complementados com o
230:       OpenStreetMap (Nominatim + Overpass) e o resultado também fica em cache.
231:     - AQUECER_PAUSA_SEGUNDOS: pausa entre cidades no aquecimento por UF, aplicada
232:       somente quando a cidade usou o OpenStreetMap.
233: 
234:     As duas flags são independentes:
235: 
236:     | USAR_CACHE | SALVAR | Comportamento |
237:     |---|---|---|
238:     | true  | true  | lê do banco; grava o que faltar (recomendado) |
239:     | false | true  | sempre vai à API e regrava tudo (força atualização) |
240:     | true  | false | só lê o banco; o que não existe vai à API sem gravar |
241:     | false | false | sempre à API, sem tocar no banco |
242: 
243:     O que acontece ao rodar de novo para a mesma cidade:
244: 
245:     - localidades_estados: UPSERT por uf (só atualiza o nome).
246:     - localidades_municipios: UPSERT por id_municipio (atualiza nome/uf e
247:       PRESERVA bairros_fonte / bairros_atualizado_em).
248:     - localidades_bairros: a lista da cidade é tratada como autoritativa. Nomes
249:       iguais são atualizados, nomes novos são inseridos e nomes que não vieram mais
250:       são removidos — mas apenas daquela cidade.
251:     - Sincronização completa (menu opção 3): aditiva. Ela insere/atualiza os
252:       distritos do IBGE sem apagar bairros que já existem, então listas
253:       complementadas pelo OpenStreetMap são preservadas.
254: 
255:     Rodar só para um estado também é seguro: obter_cidades(uf) grava apenas os
256:     municípios daquela UF, e nada de outras UFs é alterado.
257: 
258:     Sincronização completa: menu opção 3 (ou `sincronizar_base_localidades()`), que
259:     baixa de uma vez todos os estados, municípios e distritos (~10,7 mil registros).
260: 
261:     Aquecimento por UF: menu opção 4 (ou `aquecer_bairros_uf('RS')`). Resolve e
262:     grava os bairros de TODAS as cidades de um estado, sem raspar nenhum lead.
263:     Depois disso, a coleta por cidade não consulta mais IBGE/OSM.
264: 
265:     - Processa apenas as cidades com `bairros_fonte IS NULL` (ou seja, retoma de
266:       onde parou em execuções anteriores).
267:     - Cidades cobertas pelo IBGE são instantâneas; as demais usam o OpenStreetMap.
268:     - A pausa entre cidades (AQUECER_PAUSA_SEGUNDOS) é aplicada somente quando o
269:       OSM foi consultado — respeitando o limite de 1 req/s do Nominatim.
270:     - Ctrl+C interrompe sem perder o que já foi gravado; basta rodar de novo.
271:     - É possível limitar quantas cidades processar por execução.
272: 
273:     Importante: os "distritos" do IBGE são divisões administrativas e, em muitos
274:     municípios, resumem-se à própria sede. Por isso o fallback com o OSM continua
275:     existindo — a diferença é que ele roda uma única vez por cidade e o resultado
276:     é gravado no banco. Se o OSM estiver fora do ar, nada é gravado (a próxima
277:     execução tenta de novo) e a coleta segue com os distritos do IBGE.
278: 
279:     A API de Localidades do IBGE NÃO fornece bairros — apenas distritos e
280:     subdistritos. Exemplo real: Canoas-RS tem 1 distrito (a própria sede) e 0
281:     subdistritos, então o IBGE não contribui com áreas para essa cidade e o robô
282:     informa isso e segue para o OpenStreetMap:
283: 
284:     ```
285:     IBGE não publica bairros para Canoas-RS: o município tem apenas 1 distrito (a sede).
286:     Buscando bairros no OpenStreetMap...
287:     ```
288: 
289:     Cidades com vários distritos (São Paulo: 96, Campinas: 7) usam o IBGE e não
290:     consultam o OSM. Das 5.571 cidades do país, 643 têm distritos suficientes.
291: 
292:     Como a cidade é resolvida: o nome digitado é comparado sem acento e sem
293:     diferenciar maiúsculas ("canoas", "sao leopoldo") com a lista do IBGE, e o nome
294:     oficial é exibido e usado no scraping, no banco e no Excel:
295: 
296:     ```
297:     Digite o nome da cidade: canoas
298:     Município (IBGE): Canoas-RS | código 4304606
299:     ```
300: 
301:     Para forçar a atualização de uma cidade já gravada, limpe a marca:
302:     ```sql
303:     UPDATE localidades_municipios SET bairros_fonte = NULL WHERE nome = 'Porto Alegre';
304:     ```
305: 
306: 9. Anti-bloqueio / Captcha (Google Maps)
307: 
308:     Quando o Google responde com a tela de "tráfego incomum" (captcha), o robô:
309:     1. detecta o bloqueio (URL /sorry/, formulários de captcha ou textos típicos);
310:     2. aplica um cooldown global, pausando TODAS as threads ao mesmo tempo;
311:     3. espera a pausa longa e tenta novamente até CAPTCHA_MAX_TENTATIVAS;
312:     4. se o bloqueio persistir, aborta apenas aquela área, preservando os leads
313:        já extraídos (que continuam sendo salvos incrementalmente).
314: 
315:     Configuração (.env):
316:     ```
317:     CAPTCHA_MAX_TENTATIVAS=2
318:     CAPTCHA_PAUSA_SEGUNDOS=300
319:     CAPTCHA_PAUSA_GLOBAL_SEGUNDOS=180
320:     ```
321: 
322:     - CAPTCHA_MAX_TENTATIVAS: tentativas por página antes de abortar a área.
323:     - CAPTCHA_PAUSA_SEGUNDOS: pausa longa da thread que levou o bloqueio.
324:     - CAPTCHA_PAUSA_GLOBAL_SEGUNDOS: pausa compartilhada entre as threads.
325: 
326:     A resolução automática de captcha por serviço externo (2Captcha, CapMonster
327:     etc.) não está implementada — o comportamento padrão é pausar e desistir da
328:     área em vez de insistir. Em coletas muito grandes, aumente as pausas acima.
329: 
330: 10. commit forçado
331: 
332:     git add -A; git commit -m "sync local $(Get-Date -Format 'yyyy-MM-dd HH:mm')"; git push --force-with-lease origin main
333: 
334: 11. Próximos Passos (Melhorias Futuras)
335: 
336:     Já implementado:
337:     - Base de localidades offline no DuckDB (estados, municípios e distritos do IBGE).
338:     - Detecção de captcha com pausa longa e cooldown compartilhado entre threads.
339: 
340:     Pendências sugeridas:
341:     - Resolução automática de captcha: integrar um serviço (2Captcha/CapMonster) para
342:       coletas muito grandes, hoje o robô apenas pausa e desiste da área.
343: 
344:     - Enriquecimento de E-mail: Criar um script secundário que lê os sites encontrados e busca e-mails de contato (usando Regex).
345: 
346: 
347: 12. Memória do Projeto para IA (pasta memory/)
348: 
349:     A pasta `memory/` reúne documentação resumida e densa, pensada para ser lida
350:     por modelos de IA antes de alterar o código (economiza contexto/custo).
351: 
352:     Ordem de leitura:
353:     1. memory/00-resumo-projeto.md        -> objetivo, stack e estrutura
354:     2. memory/01-arquitetura-e-modulos.md -> módulos, funções e fluxos
355:     3. memory/02-decisoes-e-armadilhas.md -> decisões, bugs conhecidos, cuidados
356:     4. memory/03-historico-de-mudancas.md -> o que mudou e o que ficou pendente
357:     5. memory/04-como-contribuir.md       -> padrões de código, logs, testes e docs
358: 
359:     Regras: manter os arquivos curtos, registrar o "porquê" das decisões e nunca
360:     colocar segredos ali (API keys ficam apenas no `.env`).
361: 
362: 
363: 13. Observação sobre configuração
364: 
365:     O modelo completo e comentado de todas as variáveis está em `.env.example`.
366:     Cada item traz a faixa de valores e o efeito colateral. Comentários devem
367:     ficar em linha própria; comentário na mesma linha do valor é lido como parte
368:     do valor.
369: 
370: 14. Rodando via Docker (comandos do dia a dia)
371: 
372:     Todos os comandos são executados na raiz do projeto (onde está o
373:     docker-compose.yml), no terminal do host.
374: 
375:     Subir / atualizar
376:     ```
377:     docker compose up -d --build     # build da imagem + sobe em background
378:     docker compose logs -f app       # acompanha os logs em tempo real
379:     docker compose ps                # status do container
380:     ```
381: 
382:     Rebuild (`--build`) é obrigatório sempre que mudar algo em `src/`, no
383:     Dockerfile ou no requirements.txt. `docker compose restart` NÃO pega código
384:     nem `.env` novos — ele só reinicia o processo.
385: 
386:     Parar / reiniciar
387:     ```
388:     docker compose stop      # para o container (o progresso no banco é preservado)
389:     docker compose start     # sobe o mesmo container de novo
390:     docker compose restart   # reinicia o processo (sem rebuild e sem reler o .env)
391:     docker compose down      # remove o container (os dados ficam nos volumes)
392:     ```
393: 
394:     Depois de editar o `.env`:
395:     ```
396:     docker compose up -d     # recria o container com as novas variáveis
397:     ```
398: 
399:     Abrir shell / rodar utilitários dentro do container:
400:     ```
401:     docker compose exec app sh
402:     docker compose exec app python src/schema.py   # cria/ajusta tabelas (idempotente)
403:     ```
404: 
405:     Ver o progresso da coleta de dentro do container:
406:     ```
407:     docker compose exec app python -c "from src.database import LeadDatabase as L; db=L(); p=db.progresso_carregar('barbearias'); print('cidades:', len(p), '| concluidas:', sum(1 for v in p.values() if v['status']=='concluida')); db.close()"
408:     ```
409: 
410:     Diagnóstico:
411:     ```
412:     docker compose logs --tail=100 app   # últimas 100 linhas
413:     docker compose top                   # processos dentro do container
414:     docker stats map_scraper             # CPU e memória em tempo real
415:     ```
416: 
417:     O compose usa `restart: unless-stopped`: se a VPS reiniciar, o container volta
418:     sozinho e, como o progresso está no banco, ele retoma da cidade seguinte.
419: 
420: 15. Rodando sem Docker (local)
421: 
422:     Requisitos: Python 3.11+ e o `.env` na raiz. Instalação (uma única vez):
423: 
424:     Windows (PowerShell):
425:     ```
426:     python -m venv venv
427:     .\venv\Scripts\Activate.ps1
428:     python -m pip install -r requirements.txt
429:     python -m playwright install chromium
430:     Copy-Item .env.example .env
431:     ```
432: 
433:     Linux/macOS:
434:     ```
435:     python3 -m venv venv
436:     source venv/bin/activate
437:     python -m pip install -r requirements.txt
438:     python -m playwright install --with-deps chromium
439:     cp .env.example .env
440:     ```
441: 
442:     Comandos de execução:
443:     ```
444:     python src/main.py              # menu interativo (coleta, envio, IBGE, bairros)
445:     python src/main.py --so-enviar  # pula a coleta e só dispara o WhatsApp
446:     python src/coleta_auto.py       # coleta automática contínua (mesmo runner do Docker)
447:     python src/schema.py            # cria/ajusta as tabelas do banco
448:     ```
449: 
450:     O `coleta_auto.py` é o equivalente ao container: lê o `.env`, percorre as
451:     UFs/cidades e grava o progresso em `coleta_progresso`. Para deixar rodando
452:     depois de fechar o terminal:
453: 
454:     Linux/macOS:
455:     ```
456:     nohup python src/coleta_auto.py > coleta.log 2>&1 &
457:     tail -f coleta.log
458:     ```
459: 
460:     Windows (PowerShell):
461:     ```
462:     Start-Process -FilePath ".\venv\Scripts\python.exe" -ArgumentList "src\coleta_auto.py" -RedirectStandardOutput coleta.log -RedirectStandardError coleta.err -WindowStyle Hidden
463:     Get-Content coleta.log -Wait
464:     ```
465: 
466:     Para parar: `Ctrl+C` no terminal (ou `Stop-Process -Id <PID>` no Windows).
467:     O que já foi coletado fica salvo e a próxima execução retoma de onde parou.
468: 
469:     Diferença em relação ao Docker: no Docker o `.env` entra por `env_file` e
470:     `./data`/`./output` são volumes; localmente os caminhos são os do próprio
471:     projeto (`data/leads.duckdb` e `output/`). O banco usado depende do `.env`
472:     (`DB_ENGINE=postgres` ou `duckdb`).
473: 
474: 16. Retomada e acompanhamento da coleta
475: 
476:     - `RETOMAR_COLETA=true` (padrão): pula as cidades já concluídas, registradas
477:       em `coleta_progresso`.
478:     - `RECAPTURA_DIAS=30`: cidade concluída volta para a fila depois de 30 dias
479:       (`0` = nunca refazer).
480:     - `SEMEAR_PROGRESSO=true`: na primeira execução com a tabela vazia, cidades
481:       que já têm leads no banco são marcadas como concluídas.
482:     - Cidade interrompida (captcha, timeout, máquina desligada) fica
483:       `em_andamento`, `parcial` ou `erro` e volta automaticamente no próximo ciclo.
484:     - `RETOMAR_COLETA=false` restaura o comportamento antigo (refaz tudo a cada
485:       ciclo), útil para um passe completo de atualização.
486: 
487:     Consultas úteis (DBeaver, psql ou qualquer cliente do banco):
488:     ```sql
489:     -- panorama por UF
490:     SELECT uf, status, COUNT(*) FROM coleta_progresso
491:     GROUP BY uf, status ORDER BY uf, status;
492: 
493:     -- o que está sendo coletado agora
494:     SELECT uf, cidade, status, leads_total, tentativas, atualizado_em
495:     FROM coleta_progresso
496:     WHERE status IN ('em_andamento', 'parcial', 'erro')
497:     ORDER BY atualizado_em DESC;
498: 
499:     -- total concluído x pendente
500:     SELECT status, COUNT(*) FROM coleta_progresso GROUP BY status;
501:     ```
502: 
503:     Se a tabela ainda não existir no banco (imagem antiga), rode
504:     `python src/schema.py` ou `docker compose exec app python src/schema.py`.
505:     Ela também é criada sozinha na primeira cidade coletada.
````


# Git Diffs
## Git Diffs Working Tree
````diff

````

## Git Diffs Staged
````diff

````



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
