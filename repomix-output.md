Este arquivo é uma representação mesclada de todo o código-fonte, combinado em um único documento pelo Repomix.
O conteúdo foi processado onde números de linha foram adicionados.

# Resumo do Arquivo

## Propósito
Este arquivo contém uma representação empacotada de todo o conteúdo do repositório. Ele foi projetado para ser facilmente consumível por sistemas de IA para análise, revisão de código ou outros processos automatizados.

## Formato do Arquivo
O conteúdo está organizado da seguinte forma:
1. Esta seção de resumo
2. Informações do repositório
3. Estrutura de diretórios
4. Arquivos do repositório (se habilitado)
5. Múltiplas entradas de arquivos, cada uma consistindo de:
  a. Um cabeçalho com o caminho do arquivo (## File: path/to/file)
  b. O conteúdo completo do arquivo em um bloco de código

## Diretrizes de Uso
- Este arquivo deve ser tratado como somente leitura. Quaisquer alterações devem ser feitas nos arquivos originais do repositório, não nesta versão empacotada.
- Ao processar este arquivo, use o caminho do arquivo para distinguir entre os diferentes arquivos no repositório.
- Esteja ciente de que este arquivo pode conter informações confidenciais. Manuseie-o com o mesmo nível de segurança que você faria com o repositório original.
- Preste atenção especial às Instruções do Repositório. Elas contêm contexto importante e diretrizes específicas para este projeto.

## Notas
- Alguns arquivos podem ter sido excluídos com base nas regras do .gitignore e na configuração do Repomix.
- Arquivos binários não estão incluídos nesta representação empacotada. Consulte a seção de Estrutura do Repositório para obter uma lista completa de caminhos de arquivos, incluindo arquivos binários.
- Arquivos que correspondem a padrões no .gitignore são excluídos.
- Arquivos que correspondem a padrões de ignore padrão são excluídos.
- Números de linha foram adicionados ao início de cada linha.
- Os arquivos são classificados por contagem de alterações do Git (arquivos com mais alterações estão na parte inferior).
- Os diffs do Git da árvore de trabalho e das alterações preparadas estão incluídos.

# Estrutura de Diretórios
data/
  leads.duckdb
memory/
  00-resumo-projeto.md
  01-arquitetura-e-modulos.md
  02-decisoes-e-armadilhas.md
  03-historico-de-mudancas.md
  04-como-contribuir.md
  README.md
src/
  __init__.py
  config.py
  database.py
  localidades_db.py
  locations.py
  main.py
  scraper.py
  utils.py
  whatsapp.py
.env.example
.gitignore
.gitkeep
.repomixignore
README.md
repomix-instrucao.md
repomix.config.json
requirements.txt
````

# Files

## File: memory/00-resumo-projeto.md
````markdown
 1: # 00 — Resumo do Projeto
 2: 
 3: **Map Scraper** — ferramenta local de prospecção de leads B2B a partir do Google Maps.
 4: 
 5: - **Entrada:** UF + cidade + nicho (ex.: `RS`, `Canoas`, `barbearias`).
 6: - **Processo:** divide a busca por bairros, raspa o Google Maps com Playwright em
 7:   multithread e extrai nome, telefone, Instagram e site.
 8: - **Saída:** leads no DuckDB (`data/leads.duckdb`) + Excel em `output/`.
 9: - **Extra:** dispara mensagens de WhatsApp via WAHA para leads já coletados.
10: 
11: ## Fluxo de alto nível
12: 
13: ```
14: menu (src/main.py)
15:   └─ 1 Coletar    → locations.obter_termos_busca(cidade, uf)
16:                   → scraper.rodar_scraper_multithread(...)
17:                   → database.LeadDatabase.save_leads (UPSERT incremental)
18:                   → database.export_to_excel
19:   └─ 2 WhatsApp   → database.get_leads_para_envio
20:                   → whatsapp.disparar_campanha (WAHA)
21:   └─ 3 Sincronizar localidades (IBGE) → locations.sincronizar_base_localidades
22:   └─ 4 Aquecer bairros de uma UF       → locations.aquecer_bairros_uf
23:   └─ 5 Sair
24: ```
25: 
26: ## Stack
27: 
28: | Item | Tecnologia |
29: |---|---|
30: | Linguagem | Python 3.10+ (ambiente: `venv/`) |
31: | Scraping | Playwright (Chromium) + ThreadPoolExecutor |
32: | Banco | DuckDB (arquivo único, 1 processo por vez) |
33: | Dados | Pandas |
34: | Localidades | API IBGE + Nominatim/Overpass (OpenStreetMap) |
35: | WhatsApp | WAHA (WhatsApp HTTP API) |
36: | Config | `.env` carregado por `src/config.py` |
37: 
38: ## Estrutura
39: 
40: ```
41: map_scraper_project/
42: ├── data/          leads.duckdb (+ .wal transiente, ignorado no Git)
43: ├── memory/        esta documentação para IA
44: ├── output/        Excel gerado (ignorado no Git)
45: ├── src/
46: │   ├── config.py          loader do .env + helpers (bool/int)
47: │   ├── database.py        LeadDatabase: tabela leads, UPSERT, Excel, log WAHA
48: │   ├── localidades_db.py  cache IBGE em DuckDB (tabelas localidades_*)
49: │   ├── locations.py       IBGE + OSM + cache; sync e aquecimento por UF
50: │   ├── scraper.py         Playwright, multithread, anti-captcha
51: │   ├── utils.py           formatar_telefone → (telefone, tipo, link wa)
52: │   ├── whatsapp.py        envio via WAHA
53: │   └── main.py            menu interativo
54: ├── .env / .env.example
55: ├── requirements.txt
56: └── README.md
57: ```
58: 
59: ## Git — o que é versionado
60: 
61: | Versionado | Ignorado |
62: |---|---|
63: | `data/leads.duckdb` | `.env` (segredos) |
64: | `src/`, `memory/`, `README.md` | `*.duckdb.wal`, `*.duckdb.tmp` |
65: | `.env.example` | `*.xlsx`, `*.csv`, `*.log` |
66: | | `venv/`, `__pycache__/`, `sessions/` |
67: 
68: Comando de sync usado pelo mantenedor (sobrescreve o remoto):
69: 
70: ```powershell
71: git add -A; git commit -m "sync local $(Get-Date -Format 'yyyy-MM-dd HH:mm')"; git push --force-with-lease origin main
72: ```
````

## File: memory/01-arquitetura-e-modulos.md
````markdown
  1: # 01 — Arquitetura e Módulos
  2: 
  3: Todos os módulos usam imports absolutos (`from src.x import y`). `src/main.py`
  4: adiciona a raiz do projeto ao `sys.path` antes de importar.
  5: 
  6: ---
  7: 
  8: ## src/config.py
  9: 
 10: Único ponto de leitura do `.env`. **Chame `carregar_env()` antes de calcular
 11: constantes de módulo** (o import já executa uma vez).
 12: 
 13: ```python
 14: carregar_env(caminho=None)      # não sobrescreve variáveis já no ambiente
 15: str_para_bool(valor, padrao)    # aceita 1/true/yes/s/sim/on
 16: env_int(nome, padrao)           # inteiro com fallback
 17: PROJETO_RAIZ, CAMINHO_ENV
 18: ```
 19: 
 20: > `src/whatsapp.py` chama `carregar_env()` no import (herança histórica).
 21: > `src/locations.py` e `src/scraper.py` dependem disso para ler suas flags.
 22: 
 23: ---
 24: 
 25: ## src/localidades_db.py — cache de localidades
 26: 
 27: Acesso ao **mesmo** `data/leads.duckdb`. **Abre e fecha conexão a cada operação**,
 28: para não segurar o arquivo durante o scraping (DuckDB permite só 1 processo).
 29: 
 30: Tabelas (criadas automaticamente quando `CRIAR_TABELAS = True`):
 31: 
 32: | Tabela | Colunas |
 33: |---|---|
 34: | `localidades_estados` | `uf` PK, `nome` |
 35: | `localidades_municipios` | `id_municipio` PK, `nome`, `uf`, `bairros_fonte`, `bairros_atualizado_em` |
 36: | `localidades_bairros` | `id_municipio`, `nome`, `id_distrito` — PK (`id_municipio`,`nome`) |
 37: 
 38: `bairros_fonte` ∈ {`ibge`, `overpass`, `cidade`, `NULL` (não coletado)}.
 39: 
 40: Funções:
 41: 
 42: ```python
 43: conexao(db_path=None)              # contextmanager; DDL se CRIAR_TABELAS
 44: ler_estados() / salvar_estados(registros)
 45: ler_municipios(uf)                 # inclui bairros_fonte (necessário p/ cache hit)
 46: ler_municipios_pendentes(uf)       # bairros_fonte IS NULL
 47: salvar_municipios(registros)       # UPSERT preserva bairros_fonte
 48: buscar_municipio(cidade, uf)       # dict ou None
 49: ler_bairros(id_municipio) / salvar_bairros(id_municipio, registros, fonte)
 50: salvar_distritos_bulk(distritos, min_bairros=3)   # aditivo
 51: estatisticas()                     # dict com contagens
 52: CacheIndisponivel                  # exceção (arquivo travado / tabela ausente)
 53: ```
 54: 
 55: **Semânticas importantes**
 56: 
 57: - `salvar_bairros` é **autoritativo por cidade**: apaga nomes daquela cidade que
 58:   não vieram na lista nova (não toca em outras cidades).
 59: - `salvar_distritos_bulk` é **aditivo**: não apaga bairros do OSM já gravados.
 60: - `salvar_municipios` é UPSERT e **preserva** `bairros_fonte`.
 61: 
 62: ---
 63: 
 64: ## src/locations.py — IBGE + OpenStreetMap + cache
 65: 
 66: Endpoints usados (`IBGE_API`):
 67: 
 68: ```
 69: /estados                         → UF (sigla, nome)
 70: /estados/{uf}/municipios         → municípios da UF
 71: /municipios                      → todos (usado na sync nacional)
 72: /municipios/{id}/distritos       → distritos de uma cidade
 73: /distritos                       → todos (sync nacional)
 74: ```
 75: 
 76: Flags do módulo (lidas do `.env`):
 77: 
 78: | Constante | Env | Default |
 79: |---|---|---|
 80: | `USAR_CACHE` | `LOCALIDADES_USAR_CACHE` | `true` |
 81: | `SALVAR` | `LOCALIDADES_SALVAR` | `true` |
 82: | `MIN_BAIRROS` | `LOCALIDADES_MIN_BAIRROS` | `3` |
 83: | `AQUECER_PAUSA_PADRAO` | `AQUECER_PAUSA_SEGUNDOS` | `2` |
 84: 
 85: Helpers internos relevantes:
 86: 
 87: ```python
 88: _cache(fn, ...)   # executa no banco tolerando CacheIndisponivel (avisa 1x)
 89: _salvar(fn, ...)  # respeita SALVAR=false (avisa 1x e retorna None)
 90: _normalizar(t)    # minúsculas + sem acento
 91: _municipios_da_uf(uf)   # memoizado em memória (evita rebaixar a lista)
 92: ```
 93: 
 94: API pública:
 95: 
 96: ```python
 97: obter_estados() -> DataFrame[uf, nome]
 98: obter_cidades(uf) -> list[str]
 99: obter_bairros(cidade, uf) -> list[str]        # [] = buscar cidade inteira
100: obter_termos_busca(cidade, uf, max_bairros=30) -> list[str]
101: obter_municipio(cidade, uf) -> dict|None      # nome oficial + id IBGE
102: filtrar_cidades(cidades, termo) -> list[str]  # sem acento/caixa
103: listar_municipios_pendentes(uf) -> list[dict]
104: aquecer_bairros_uf(uf, cidades=None, max_cidades=0, pausa_segundos=None) -> dict|None
105: sincronizar_base_localidades() -> bool        # nacional; bloqueada se SALVAR=false
106: ```
107: 
108: ### Resolução de bairros (`obter_bairros`)
109: 
110: 1. Resolve o município (cache → lista da UF → grava se `SALVAR`).
111: 2. Usa o **nome oficial** do IBGE daqui pra frente.
112: 3. Se `USAR_CACHE` e `bairros_fonte` preenchido → lê `localidades_bairros`.
113: 4. Senão:
114:    - baixa distritos do IBGE; descarta o distrito-sede (mesmo nome da cidade);
115:    - se `>= MIN_BAIRROS` → fonte `ibge`, **sem** chamar o OSM;
116:    - senão → Nominatim (bbox) + Overpass (`place=suburb|neighbourhood|quarter`,
117:      fallback `admin_level 9/10`);
118:    - se o OSM falhar (serviço fora) → **não grava** (`fonte=None`), tenta de novo
119:      na próxima execução.
120: 
121: ---
122: 
123: ## src/scraper.py — Playwright + anti-bloqueio
124: 
125: ```python
126: extrair_leads_local(nicho, termo_busca, cidade, uf, mostrar_navegador=False) -> list[dict]
127: rodar_scraper_multithread(nicho, cidade, uf, termos_lista,
128:                           mostrar_navegador=False, save_callback=None) -> DataFrame
129: ```
130: 
131: - `max_workers = min(3, len(termos_lista))`.
132: - `save_callback(df)` é chamado a cada área concluída (salvamento incremental).
133: - Deduplicação intra-execução por `(nome, cidade)`.
134: - Dict de lead: `nome, telefone, tipo_telefone, whatsapp_link, instagram, site,
135:   bairro, cidade, estado, nicho`.
136: 
137: Rolagem: `MAX_ROLAGENS = 40`, para após `MAX_RODADAS_ESTAGNADAS = 3` rodadas sem
138: crescimento.
139: 
140: Anti-captcha:
141: 
142: ```python
143: BloqueioDetectado(termo)      # exceção
144: _pagina_bloqueada(page, checar_texto=True)
145: _marcar_bloqueio_global()     # cooldown compartilhado entre threads
146: _aguardar_cooldown(termo)     # todas as threads esperam
147: _navegar_com_retry(page, url, tentativas=3, timeout=..., termo=...)
148: ```
149: 
150: Detecção: URL `/sorry/`, seletores de captcha (`#captcha-form`, reCAPTCHA,
151: hCaptcha) e textos como "unusual traffic" / "tráfego incomum".
152: Persistindo o bloqueio, **aborta só a área** e preserva os leads já extraídos.
153: 
154: Flags: `CAPTCHA_MAX_TENTATIVAS` (2), `CAPTCHA_PAUSA_SEGUNDOS` (300),
155: `CAPTCHA_PAUSA_GLOBAL_SEGUNDOS` (180).
156: 
157: ---
158: 
159: ## src/database.py — leads
160: 
161: `LeadDatabase(db_path="data/leads.duckdb")`
162: 
163: Tabela `leads` — PK (`nome`, `cidade`):
164: 
165: ```
166: nome, telefone, tipo_telefone, whatsapp_link, instagram, site,
167: bairro, cidade, estado, nicho, status (default 'ativo'),
168: data_extracao, data_envio_whatsapp, status_whatsapp (default 'pendente')
169: ```
170: 
171: ```python
172: save_leads(df) -> int          # filtra descartados, UPSERT, não apaga log WAHA
173: get_leads_para_envio(limite)   # ativo + Celular + pendente
174: marcar_envio(nome, cidade, status_whatsapp)   # 'enviado' grava data
175: export_to_excel(nicho, cidade) # output/leads_{nicho}_{cidade}.xlsx
176: close()
177: ```
178: 
179: ---
180: 
181: ## src/whatsapp.py — WAHA
182: 
183: ```python
184: WAHA_API_URL, WAHA_API_KEY, WAHA_SESSION
185: WAHA_ATIVO, SOMENTE_ENVIO, WAHA_INTERVALO, WAHA_LIMITE
186: MENSAGEM_PADRAO
187: enviar_texto_waha(chat_id, texto, ...)   # POST /api/sendText
188: disparar_campanha(db, mensagem_template=None, intervalo=13, limite=None)
189: ```
190: 
191: - `chat_id` = `55DDD9XXXXXXXX@c.us` (só 11 dígitos; fixo é rejeitado).
192: - Placeholders: `{nome}`, `{bairro}`, `{cidade}`.
193: - `SOMENTE_ENVIO=true` (ou `--so-enviar`) pula o menu e vai direto ao envio.
194: 
195: ---
196: 
197: ## src/main.py — menu
198: 
199: ```
200: 1 - Coletar leads
201: 2 - Enviar mensagens WhatsApp
202: 3 - Sincronizar base de localidades (IBGE)
203: 4 - Aquecer bairros de uma UF (OpenStreetMap)
204: 5 - Sair
205: ```
206: 
207: `coletar_leads()`: UF → cidade (filtro sem acento) → **confirma no IBGE e usa o
208: nome oficial** → nicho → termos → "Ver navegador?" → scraping → Excel.
````

## File: memory/02-decisoes-e-armadilhas.md
````markdown
  1: # 02 — Decisões Técnicas e Armadilhas
  2: 
  3: Leia antes de mexer no código. Cada item já custou tempo de depuração.
  4: 
  5: ---
  6: 
  7: ## DuckDB: um processo por arquivo
  8: 
  9: **O arquivo `data/leads.duckdb` só pode ser aberto por UM processo.** Não existe
 10: "read-only compartilhado" — até `duckdb.connect(..., read_only=True)` falha:
 11: 
 12: ```
 13: IO Error: Cannot open file "...data\leads.duckdb":
 14: O arquivo já está sendo usado por outro processo.
 15: ```
 16: 
 17: Causas mais comuns: **DBeaver conectado**, scraper rodando, notebook aberto.
 18: 
 19: Consequências no código:
 20: - `localidades_db.conexao()` abre/fecha a cada operação (não mantém aberto).
 21: - `LeadDatabase` mantém aberto durante o scraping — **não** abra outra conexão
 22:   persistente no mesmo processo.
 23: - `CacheIndisponivel` existe para degradar com aviso em vez de quebrar:
 24:   o sistema segue usando as APIs (IBGE/OSM) sem cache.
 25: 
 26: - ⚠️ **Um WAL pendente (`.wal`) indica dados não consolidados.** Se comitar o
 27:   `.duckdb` com o programa aberto, o `.wal` (ignorado no Git) fica de fora e o
 28:   commit sobe um estado desatualizado. Feche o programa antes de comitar.
 29: 
 30: ---
 31: 
 32: ## IBGE: não existe bairro na API de Localidades
 33: 
 34: A API retorna **estados, municípios, distritos e subdistritos**. Nada de bairro.
 35: 
 36: - `distritos` são divisões administrativas; em muitos municípios resumem-se à
 37:   própria sede (mesmo nome da cidade).
 38: - Exemplo real: **Canoas-RS = 1 distrito ("Canoas") e 0 subdistritos**.
 39: - `obter_bairros` descarta o distrito-sede; se sobrarem `< MIN_BAIRROS`,
 40:   complementa com OpenStreetMap.
 41: - Cobertura: ~643 de 5.571 municípios têm distritos suficientes para dispensar OSM.
 42: 
 43: **Não "conserte" isso achando que é bug.** Para bairros oficiais existiria o
 44: CNEFE 2022 (`ftp.ibge.gov.br/.../Censo_Demografico_2022/Arquivos_CNEFE/CSV/UF/`,
 45: coluna `DSC_LOCALIDADE`, ex. `43_RS.zip` ≈ 236 MB) — **decisão do mantenedor:
 46: não implementar por ora**, evoluir aos poucos.
 47: 
 48: ---
 49: 
 50: ## OpenStreetMap: instável por natureza
 51: 
 52: Os espelhos do Overpass e o Nominatim respondem `502`, `400` e `ReadTimeout`
 53: com frequência. Regra de ouro:
 54: 
 55: > Falha de rede **não** significa "cidade sem bairros".
 56: 
 57: Por isso `_consultar_overpass` retorna `None` (serviço fora) em vez de
 58: `{"elements": []}`, e `_descobrir_bairros` devolve `fonte=None` para **não
 59: gravar** nada. A próxima execução tenta de novo. Se gravasse "cidade", o cache
 60: ficaria envenenado para sempre.
 61: 
 62: ---
 63: 
 64: ## Cache: `bairros_fonte` precisa vir na leitura
 65: 
 66: Bug corrigido em 2026-10-29: `ler_municipios()` selecionava só
 67: `id_municipio, nome`, então `_resolver_municipio` devolvia `bairros_fonte=None` e
 68: `obter_bairros` **ia à API mesmo com cache quente**. Agora a query inclui
 69: `uf` e `bairros_fonte`.
 70: 
 71: **Ao criar novas leituras de município, sempre inclua `bairros_fonte`.**
 72: 
 73: ---
 74: 
 75: ## Semântica de escrita (não inverter!)
 76: 
 77: | Função | Comportamento |
 78: |---|---|
 79: | `salvar_bairros` | **autoritativo** por cidade: remove nomes ausentes **daquela** cidade |
 80: | `salvar_distritos_bulk` | **aditivo**: nunca apaga bairros do OSM |
 81: | `salvar_municipios` | UPSERT — **preserva** `bairros_fonte`/`bairros_atualizado_em` |
 82: 
 83: Se `salvar_distritos_bulk` virasse autoritativo, destruiria as listas do
 84: OpenStreetMap em toda sincronização.
 85: 
 86: ---
 87: 
 88: ## Flags `LOCALIDADES_*` são independentes
 89: 
 90: `USAR_CACHE` controla **leitura**; `SALVAR` controla **escrita**.
 91: 
 92: | USAR_CACHE | SALVAR | Efeito |
 93: |---|---|---|
 94: | true | true | padrão: lê do banco, grava o que faltar |
 95: | false | true | ignora o banco, sempre API e regrava |
 96: | true | false | lê do banco; o que falta vem da API sem gravar |
 97: | false | false | sempre API, banco intocado |
 98: 
 99: - `SALVAR=false` também desativa a criação de tabelas (`CRIAR_TABELAS`) e os
100:   menus **3** e **4**.
101: - As flags são lidas **no import**: mudar o `.env` exige reiniciar o programa.
102: - Com `USAR_CACHE=false`, cada cidade baixa a lista da UF de novo (exceto pela
103:   memoização em memória `_municipios_da_uf`, válida só na execução atual).
104: 
105: ---
106: 
107: ## Cuidados ao editar arquivos (Windows/PowerShell)
108: 
109: - **Nunca** use `Get-Content ... -replace ... | Set-Content` para editar `.py`:
110:   ele reescreve em ANSI e **corrompe acentuação** (dupla codificação / mojibake).
111:   Use o editor (edit) ou grave via Python com `encoding="utf-8"`.
112: - Grave sempre **UTF-8 sem BOM** (BOM quebra a primeira chave do `.env`).
113: - Para testar, use o interpretador da venv: `venv\Scripts\python.exe`.
114:   O `python` global do mantenedor é 3.15 e pode não ter as dependências.
115: - Valide a acentuação após edições em lote: procure caracteres de dupla
116:   codificação (por exemplo, `A` com til U+00C3 seguido de símbolo de moeda).
117: 
118: ---
119: 
120: ## `.env` e Git
121: 
122: - `.env` **é ignorado** (contém `WAHA_API_KEY`). `.env.example` **é versionado**.
123: - Formato: `CHAVE=VALOR`. Comentários só em **linha própria** — comentário na
124:   mesma linha vira parte do valor (`WAHA_LIMITE= # vazio` → `" # vazio"`).
125: - Não use `export`/aspas desnecessárias; o loader tira aspas simples/duplas.
126: - Nunca imprima nem comite segredos.
127: 
128: ---
129: 
130: ## Scraping: seletores frágeis
131: 
132: Dependem do DOM do Google Maps (podem mudar sem aviso):
133: 
134: | Dado | Seletor |
135: |---|---|
136: | lista de resultados | `div[role="feed"]` |
137: | links de perfis | `a[href*="/maps/place/"]` |
138: | nome | `h1` (ignora "Resultados" e vazio) |
139: | endereço | `button[data-item-id="address"]` (`aria-label`) |
140: | telefone | `button[data-item-id^="phone:tel:"]` (`aria-label`) |
141: | site | `a[data-item-id="authority"]` |
142: | Instagram | primeiro `a[href]` contendo `instagram.com` |
143: 
144: Bairro é extraído do endereço: `"Rua X, 123 - Bairro, Cidade - UF"` → parte
145: entre `" - "` e `","`. Se não casar, `"Não Informado"`.
146: 
147: ---
148: 
149: ## Concorrência
150: 
151: - `save_callback` é chamado **na thread principal** (dentro do loop de
152:   `as_completed`), então não há escrita concorrente no DuckDB.
153: - O cooldown anti-captcha usa `_cooldown_lock` + variável global `_cooldown_ate`.
154: - `lock` protege a lista `vistos`/`todos_leads`.
155: 
156: ---
157: 
158: ## Coisas que parecem bug mas não são
159: 
160: - `"IBGE não publica bairros para X"` → cidade com 1 distrito (ver acima).
161: - `"Base local ... sem bairros (fonte: cidade)"` → já tentou, o OSM não tinha nada.
162: - `"LOCALIDADES_SALVAR=false: a base local não será alterada"` → modo leitura.
163: - `"Aviso: base local ... indisponível (arquivo em uso)"` → feche o DBeaver.
````

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

## File: src/config.py
````python
 1: # src/config.py
 2: """Carregamento centralizado do arquivo .env e leitura de flags.
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

## File: .gitkeep
````
1: 
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
9: requests
````

## File: memory/03-historico-de-mudancas.md
````markdown
  1: # 03 — Histórico de Mudanças
  2: 
  3: Registro do que mudou, por quê e o que ficou pendente. Mais recente primeiro.
  4: 
  5: ---
  6: 
  7: ## 2026-10-29
  8: 
  9: ### Memória do projeto para IA
 10: 
 11: - Criada a pasta `memory/` com documentação densa para reduzir custo de contexto.
 12: - Arquivos: `README.md`, `00-resumo-projeto.md`, `01-arquitetura-e-modulos.md`,
 13:   `02-decisoes-e-armadilhas.md`, `03-historico-de-mudancas.md`,
 14:   `04-como-contribuir.md` (padrões de código, logs, config, testes e docs).
 15: - `README.md` limpo: removido o bloco "env temp:" (dump cru do `.env`) e
 16:   adicionadas as seções 12 (memória para IA) e 13 (observação sobre configuração).
 17: 
 18: ### Correção: cache de bairros ignorado (`bairros_fonte`)
 19: 
 20: - **Sintoma:** com `LOCALIDADES_USAR_CACHE=true` e base populada, a coleta ainda
 21:   consultava IBGE e Overpass.
 22: - **Causa:** `localidades_db.ler_municipios()` não retornava `bairros_fonte`;
 23:   `_resolver_municipio` repassava `None`, então o cache nunca era considerado.
 24: - **Correção:** query passou a trazer `uf` e `bairros_fonte`; o resolver repassa
 25:   o valor real.
 26: - **Teste:** com as funções de rede trocadas por `AssertionError`, os bairros de
 27:   Canoas (fonte `overpass`) e Bento Gonçalves (fonte `ibge`) vieram do banco.
 28: 
 29: ### Nome oficial do município (IBGE) na coleta
 30: 
 31: - `obter_municipio(cidade, uf)` confirma o município e devolve `id_municipio`,
 32:   `nome` oficial e `uf`.
 33: - `filtrar_cidades(cidades, termo)` compara **sem acento e sem caixa**:
 34:   `canoas`, `sao leopoldo`, `CHAPECO` funcionam.
 35: - `main.coletar_leads()` passa a usar o nome oficial no scraping, no banco e no
 36:   nome do Excel, e imprime `Município (IBGE): Canoas-RS | código 4304606`.
 37: - Lista de municípios **memoizada** por execução (`_municipios_da_uf`), evitando
 38:   rebaixar a lista da UF a cada cidade (principalmente com `SALVAR=false`).
 39: 
 40: ### Mensagens de bairros mais honestas
 41: 
 42: - Antes: `IBGE retornou 0 distrito(s) útil(eis)`.
 43: - Agora: `IBGE não publica bairros para Canoas-RS: o município tem apenas 1 distrito (a sede).`
 44: - Motivo: a API de Localidades do IBGE **não tem bairros** (só distritos).
 45: 
 46: ### Aquecimento de bairros por UF (menu 4)
 47: 
 48: - `locations.aquecer_bairros_uf(uf, cidades=None, max_cidades=0, pausa_segundos=None)`.
 49: - `localidades_db.ler_municipios_pendentes(uf)` → só `bairros_fonte IS NULL`.
 50: - Retoma de onde parou; `Ctrl+C` preserva o que já foi gravado.
 51: - Pausa (`AQUECER_PAUSA_SEGUNDOS`, default 2) só quando a cidade usou o OSM.
 52: - Falha de rede não grava nada (`falhas` no resumo) e a cidade continua pendente.
 53: - Bloqueado quando `LOCALIDADES_SALVAR=false`.
 54: - Medido: AC 21 → 18 → 17 pendentes; SP 621 → 616.
 55: 
 56: ### Flag `LOCALIDADES_SALVAR`
 57: 
 58: - `false` = somente leitura: nenhuma escrita, **nem criação de tabelas**
 59:   (`localidades_db.CRIAR_TABELAS = False`) e menus 3/4 desativados.
 60: - Todas as escritas passam por `_salvar()`, que respeita a flag.
 61: - Aviso único por execução para não poluir o log.
 62: 
 63: ### `.env` e `.env.example` comentados
 64: 
 65: - Cada variável com explicação, faixa de valores e efeito colateral.
 66: - Tabela das 4 combinações `USAR_CACHE × SALVAR`.
 67: - Regra explícita: comentário só em linha própria.
 68: - Valores locais preservados (`USAR_CACHE=false` → depois `true`).
 69: 
 70: ### Base de localidades offline (IBGE) — menu 3
 71: 
 72: - Novo `src/localidades_db.py` com tabelas `localidades_estados`,
 73:   `localidades_municipios`, `localidades_bairros` no mesmo `leads.duckdb`.
 74: - `src/config.py` centraliza o loader do `.env` (antes duplicado no `whatsapp.py`).
 75: - `src/locations.py` reescrito: cache → API → grava.
 76: - Sync nacional: 27 estados, 5.571 municípios, 10.751 distritos; 643 cidades com
 77:   bairros prontos pelo IBGE.
 78: - Fallback OSM por cidade, gravado uma única vez.
 79: 
 80: ### Anti-captcha / bloqueio do Google Maps
 81: 
 82: - Detecção por URL `/sorry/`, seletores de captcha e textos ("tráfego incomum").
 83: - Retry com pausa longa (`CAPTCHA_PAUSA_SEGUNDOS`) e **cooldown global**
 84:   (`CAPTCHA_PAUSA_GLOBAL_SEGUNDOS`) entre todas as threads.
 85: - Bloqueio persistente → aborta a área e **preserva os leads já extraídos**.
 86: - Testado com Playwright real: página normal passa, página de captcha levanta
 87:   `BloqueioDetectado` após `CAPTCHA_MAX_TENTATIVAS`.
 88: 
 89: ### Correção: menu não aparecia
 90: 
 91: - `src/main.py` definia `menu_interativo()` mas **nunca chamava**.
 92: - Adicionado `if __name__ == "__main__": menu_interativo()`.
 93: 
 94: ### Banco DuckDB versionado
 95: 
 96: - `data/leads.duckdb` passou a ser versionado no Git.
 97: - `.gitignore`: removidos `data/` e `*.duckdb` da lista de ignore; adicionados
 98:   `*.duckdb.wal` e `*.duckdb.tmp`.
 99: - `*.xlsx`, `*.csv`, `*.log` continuam ignorados (confirmado com
100:   `git check-ignore` e `git ls-files`).
101: - ⚠️ Comitar com o programa aberto sobe o `.duckdb` sem o `.wal` (dados
102:   desatualizados). Fechar antes.
103: 
104: ---
105: 
106: ## Pendências / próximos passos
107: 
108: | Item | Status |
109: |---|---|
110: | Bairros oficiais via CNEFE 2022 | **Não implementar por hora** (decisão do mantenedor) |
111: | Resolução automática de captcha (2Captcha/CapMonster) | Não implementado; hoje pausa e desiste da área |
112: | Enriquecimento de e-mail a partir dos sites | Não iniciado |
113: | Base de bairros offline nacional | Coberto parcialmente pelo IBGE (643 cidades) |
114: 
115: ## Problemas conhecidos (ambiente)
116: 
117: - **DBeaver aberto trava o DuckDB** → cache cai para as APIs.
118: - **Overpass/Nominatim instáveis** (502, timeout) → aquecimento por UF precisa de
119:   paciência e retomadas.
120: - Interprete global do mantenedor é Python 3.15; **usar `venv\Scripts\python.exe`**.
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
20: 
21: ## Regras de manutenção
22: 
23: - **Atualize ao mudar comportamento**, não a cada commit.
24: - Mantenha cada arquivo curto (ideal: < 200 linhas). Detalhe fica no código.
25: - Registre o **porquê** das decisões, não só o quê.
26: - Nunca coloque segredos aqui (API keys, tokens). Use `.env`.
27: - Datas no formato `AAAA-MM-DD`.
28: 
29: ## Arquivos que NÃO devem ser duplicados aqui
30: 
31: - `README.md` (raiz) — manual do usuário, instalação, uso.
32: - `.env.example` — valores e comentários de cada variável.
````

## File: src/database.py
````python
  1: # src/database.py
  2: import duckdb
  3: import pandas as pd
  4: import os
  5: from datetime import datetime
  6: 
  7: class LeadDatabase:
  8:     def __init__(self, db_path="data/leads.duckdb"):
  9:         os.makedirs(os.path.dirname(db_path), exist_ok=True)
 10:         self.db_path = db_path
 11:         self.conn = duckdb.connect(self.db_path)
 12:         self._create_table()
 13:         self._ensure_whatsapp_columns()
 14: 
 15:     def _create_table(self):
 16:         self.conn.execute("""
 17:             CREATE TABLE IF NOT EXISTS leads (
 18:                 nome VARCHAR,
 19:                 telefone VARCHAR,
 20:                 tipo_telefone VARCHAR,
 21:                 whatsapp_link VARCHAR,
 22:                 instagram VARCHAR,
 23:                 site VARCHAR,
 24:                 bairro VARCHAR,
 25:                 cidade VARCHAR,
 26:                 estado VARCHAR,
 27:                 nicho VARCHAR,
 28:                 status VARCHAR DEFAULT 'ativo',
 29:                 data_extracao TIMESTAMP,
 30:                 data_envio_whatsapp TIMESTAMP,
 31:                 status_whatsapp VARCHAR DEFAULT 'pendente',
 32:                 PRIMARY KEY (nome, cidade)
 33:             )
 34:         """)
 35: 
 36:     def _ensure_whatsapp_columns(self):
 37:         """Adiciona as colunas de log de WhatsApp em bancos criados antes da migração."""
 38:         colunas = {row[1] for row in self.conn.execute("PRAGMA table_info(leads)").fetchall()}
 39:         if 'data_envio_whatsapp' not in colunas:
 40:             self.conn.execute("ALTER TABLE leads ADD COLUMN data_envio_whatsapp TIMESTAMP")
 41:         if 'status_whatsapp' not in colunas:
 42:             self.conn.execute("ALTER TABLE leads ADD COLUMN status_whatsapp VARCHAR DEFAULT 'pendente'")
 43: 
 44:     def save_leads(self, df: pd.DataFrame):
 45:         if df.empty:
 46:             return 0
 47:         
 48:         descartados_db = self.conn.execute("SELECT nome, cidade FROM leads WHERE status = 'descartado'").fetchall()
 49:         descartados_set = set(descartados_db)
 50:         
 51:         df = df[~df.apply(lambda row: (row['nome'], row['cidade']) in descartados_set, axis=1)]
 52:         
 53:         if df.empty:
 54:             print("Todos os leads coletados já foram descartados anteriormente. Pulando salvamento.")
 55:             return 0
 56:             
 57:         df['data_extracao'] = datetime.now()
 58:         
 59:         if 'status' not in df.columns:
 60:             df['status'] = 'ativo'
 61: 
 62:         self.conn.register('df_temp', df)
 63: 
 64:         # UPSERT preservando o status atual e as colunas de log do WhatsApp.
 65:         # Assim, re-raspar um lead já enviado NÃO apaga data_envio_whatsapp/status_whatsapp.
 66:         self.conn.execute("""
 67:             INSERT INTO leads (nome, telefone, tipo_telefone, whatsapp_link, instagram, site, bairro, cidade, estado, nicho, status, data_extracao)
 68:             SELECT nome, telefone, tipo_telefone, whatsapp_link, instagram, site, bairro, cidade, estado, nicho, status, data_extracao
 69:             FROM df_temp
 70:             ON CONFLICT (nome, cidade) DO UPDATE SET
 71:                 telefone = excluded.telefone,
 72:                 tipo_telefone = excluded.tipo_telefone,
 73:                 whatsapp_link = excluded.whatsapp_link,
 74:                 instagram = excluded.instagram,
 75:                 site = excluded.site,
 76:                 bairro = excluded.bairro,
 77:                 estado = excluded.estado,
 78:                 nicho = excluded.nicho,
 79:                 data_extracao = excluded.data_extracao
 80:         """)
 81: 
 82:         self.conn.unregister('df_temp')
 83:         return len(df)
 84: 
 85:     def get_leads_para_envio(self, limite=None):
 86:         """Retorna leads ativos, celulares e ainda não enviados (evita spam/fixo)."""
 87:         query = """
 88:             SELECT nome, telefone, whatsapp_link, bairro, cidade, estado, nicho
 89:             FROM leads
 90:             WHERE status = 'ativo'
 91:               AND tipo_telefone = 'Celular'
 92:               AND (status_whatsapp IS NULL OR status_whatsapp = 'pendente')
 93:             ORDER BY cidade, bairro, nome
 94:         """
 95:         if limite:
 96:             query += f" LIMIT {int(limite)}"
 97:         return self.conn.execute(query).df()
 98: 
 99:     def marcar_envio(self, nome, cidade, status_whatsapp):
100:         """Registra o resultado do envio. 'data_envio_whatsapp' é gravado apenas no sucesso."""
101:         if status_whatsapp == 'enviado':
102:             self.conn.execute("""
103:                 UPDATE leads
104:                 SET status_whatsapp = ?, data_envio_whatsapp = ?
105:                 WHERE nome = ? AND cidade = ?
106:             """, [status_whatsapp, datetime.now(), nome, cidade])
107:         else:
108:             self.conn.execute("""
109:                 UPDATE leads
110:                 SET status_whatsapp = ?
111:                 WHERE nome = ? AND cidade = ?
112:             """, [status_whatsapp, nome, cidade])
113: 
114:     def export_to_excel(self, nicho: str, cidade: str):
115:         df = self.conn.execute("""
116:             SELECT nome, telefone, tipo_telefone, whatsapp_link, instagram, site, bairro, data_extracao 
117:             FROM leads 
118:             WHERE nicho = ? AND cidade = ? AND status = 'ativo'
119:             ORDER BY bairro, nome
120:         """, [nicho, cidade]).df()
121:         
122:         if df.empty:
123:             print("Nenhum dado ativo para exportar.")
124:             return
125:             
126:         os.makedirs("output", exist_ok=True)
127:         nome_arquivo = f"output/leads_{nicho}_{cidade}.xlsx".replace(" ", "_").lower()
128:         df.to_excel(nome_arquivo, index=False)
129:         print(f"🎉 Exportação concluída: {nome_arquivo} ({len(df)} leads ativos)")
130: 
131:     def close(self):
132:         self.conn.close()
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
 15: import re
 16: import time
 17: 
 18: import requests
 19: 
 20: from src.config import carregar_env, str_para_bool
 21: 
 22: carregar_env()
 23: 
 24: WAHA_API_URL = os.environ.get("WAHA_API_URL", "http://localhost:3000")
 25: WAHA_API_KEY = os.environ.get("WAHA_API_KEY", "")
 26: WAHA_SESSION = os.environ.get("WAHA_SESSION", "default")
 27: 
 28: # Se false, o módulo NÃO tenta enviar (desliga o envio de WhatsApp).
 29: WAHA_ATIVO = str_para_bool(os.environ.get("WAHA_ATIVO"), padrao=True)
 30: 
 31: # Se true, pula a coleta e vai direto para o envio (não coleta nada).
 32: SOMENTE_ENVIO = str_para_bool(os.environ.get("SOMENTE_ENVIO"), padrao=False)
 33: 
 34: # Intervalo (segundos) entre envios e limite de leads por campanha.
 35: # WAHA_LIMITE vazio = sem limite (envia todos os pendentes).
 36: WAHA_INTERVALO = int(os.environ.get("WAHA_INTERVALO", "13"))
 37: WAHA_LIMITE = os.environ.get("WAHA_LIMITE", "").strip()
 38: WAHA_LIMITE = int(WAHA_LIMITE) if WAHA_LIMITE else None
 39: 
 40: # Mensagem padrão (placeholder). Use {nome}, {bairro} e {cidade}.
 41: MENSAGEM_PADRAO = "Olá {nome}! Vi que vocês atendem no bairro {bairro}, em {cidade}. Podemos conversar?"
 42: 
 43: 
 44: def _normalizar_chatid(telefone):
 45:     """Converte o telefone salvo em um chatId do WAHA (55DDDNUMERO@c.us)."""
 46:     numero = re.sub(r"\D", "", str(telefone or ""))
 47:     if not numero:
 48:         return None
 49: 
 50:     # Se veio com DDI 55 e tem mais de 11 dígitos, remove o prefixo.
 51:     if numero.startswith("55") and len(numero) > 11:
 52:         numero = numero[2:]
 53: 
 54:     # Celular brasileiro tem 11 dígitos (DDD + 9 dígitos).
 55:     if len(numero) != 11:
 56:         return None
 57: 
 58:     return f"55{numero}@c.us"
 59: 
 60: 
 61: def _renderizar_mensagem(template, lead):
 62:     """Substitui {nome}, {bairro} e {cidade} de forma segura (sem quebrar com chaves soltas)."""
 63:     bairro = str(lead.get("bairro") or "sua região")
 64:     cidade = str(lead.get("cidade") or "")
 65:     return (
 66:         template
 67:         .replace("{nome}", str(lead.get("nome") or ""))
 68:         .replace("{bairro}", bairro)
 69:         .replace("{cidade}", cidade)
 70:     )
 71: 
 72: 
 73: def enviar_texto_waha(chat_id, texto, session=None, api_url=None, api_key=None):
 74:     """Envia uma mensagem de texto via WAHA."""
 75:     session = session or WAHA_SESSION
 76:     api_url = api_url or WAHA_API_URL
 77:     api_key = api_key if api_key is not None else WAHA_API_KEY
 78:     url = f"{api_url.rstrip('/')}/api/sendText"
 79: 
 80:     payload = {
 81:         "session": session,
 82:         "chatId": chat_id,
 83:         "text": texto,
 84:     }
 85: 
 86:     headers = {"Accept": "application/json", "Content-Type": "application/json"}
 87:     if api_key:
 88:         headers["X-Api-Key"] = api_key
 89: 
 90:     response = requests.post(url, json=payload, headers=headers, timeout=30)
 91:     response.raise_for_status()
 92:     return response.json()
 93: 
 94: 
 95: def disparar_campanha(db, mensagem_template=None, intervalo=13, limite=None):
 96:     """Envia mensagens para todos os leads celulares pendentes.
 97: 
 98:     - db: instância de LeadDatabase
 99:     - mensagem_template: texto com {nome}, {bairro}, {cidade} (usa MENSAGEM_PADRAO se None)
100:     - intervalo: pausa em segundos entre envios (evita spam e banimento)
101:     """
102:     mensagem_template = mensagem_template or MENSAGEM_PADRAO
103:     leads = db.get_leads_para_envio(limite)
104: 
105:     if leads.empty:
106:         print("Nenhum lead celular pendente de envio.")
107:         return
108: 
109:     total = len(leads)
110:     print(f"Enviando para {total} lead(s) celular(es), com intervalo de {intervalo}s...")
111: 
112:     for i, (_, lead) in enumerate(leads.iterrows(), 1):
113:         chat_id = _normalizar_chatid(lead.get("telefone"))
114:         if not chat_id:
115:             db.marcar_envio(lead["nome"], lead["cidade"], "falhou")
116:             print(f"[{i}/{total}] {lead['nome']} - telefone inválido, marcado como falhou.")
117:             continue
118: 
119:         texto = _renderizar_mensagem(mensagem_template, lead)
120: 
121:         try:
122:             enviar_texto_waha(chat_id, texto)
123:             db.marcar_envio(lead["nome"], lead["cidade"], "enviado")
124:             print(f"[{i}/{total}] ENVIADO -> {lead['nome']} ({chat_id})")
125:         except Exception as e:
126:             db.marcar_envio(lead["nome"], lead["cidade"], "falhou")
127:             print(f"[{i}/{total}] FALHOU -> {lead['nome']} ({chat_id}): {e}")
128: 
129:         if i < total:
130:             time.sleep(intervalo)
131: 
132:     print("Campanha finalizada.")
````

## File: src/localidades_db.py
````python
  1: # src/localidades_db.py
  2: """Cache local (DuckDB) da base de localidades do IBGE.
  3: 
  4: Guarda apenas o essencial, para não inflar o banco:
  5:     localidades_estados     -> uf, nome
  6:     localidades_municipios  -> id_municipio, nome, uf + estado da coleta de bairros
  7:     localidades_bairros     -> id_municipio, nome, id_distrito
  8: 
  9: O arquivo é o mesmo DuckDB dos leads (data/leads.duckdb). Cada operação abre e
 10: fecha a conexão, então o cache nunca segura o banco travado durante o scraping.
 11: """
 12: import os
 13: from contextlib import contextmanager
 14: from datetime import datetime
 15: 
 16: import duckdb
 17: import pandas as pd
 18: 
 19: DB_PATH_PADRAO = os.path.join("data", "leads.duckdb")
 20: 
 21: # Origem da lista de bairros gravada para uma cidade.
 22: FONTE_IBGE = "ibge"           # distritos do IBGE (quantidade suficiente)
 23: FONTE_OVERPASS = "overpass"   # complementado/obtido via OpenStreetMap
 24: FONTE_CIDADE = "cidade"       # nenhum bairro usado: busca a cidade inteira
 25: 
 26: 
 27: class CacheIndisponivel(Exception):
 28:     """Não foi possível abrir ou gravar a base local (ex.: arquivo travado)."""
 29: 
 30: 
 31: _DDL = (
 32:     """
 33:     CREATE TABLE IF NOT EXISTS localidades_estados (
 34:         uf VARCHAR PRIMARY KEY,
 35:         nome VARCHAR NOT NULL
 36:     )
 37:     """,
 38:     """
 39:     CREATE TABLE IF NOT EXISTS localidades_municipios (
 40:         id_municipio BIGINT PRIMARY KEY,
 41:         nome VARCHAR NOT NULL,
 42:         uf VARCHAR NOT NULL,
 43:         bairros_fonte VARCHAR,
 44:         bairros_atualizado_em TIMESTAMP
 45:     )
 46:     """,
 47:     """
 48:     CREATE TABLE IF NOT EXISTS localidades_bairros (
 49:         id_municipio BIGINT NOT NULL,
 50:         nome VARCHAR NOT NULL,
 51:         id_distrito BIGINT,
 52:         PRIMARY KEY (id_municipio, nome)
 53:     )
 54:     """,
 55: )
 56: 
 57: 
 58: # Se false, nenhuma DDL é executada: o cache é aberto somente para leitura.
 59: # Definido por `src/locations.py` a partir de LOCALIDADES_SALVAR.
 60: CRIAR_TABELAS = True
 61: 
 62: 
 63: @contextmanager
 64: def conexao(db_path=None):
 65:     caminho = db_path or DB_PATH_PADRAO
 66:     diretorio = os.path.dirname(caminho)
 67:     if diretorio:
 68:         os.makedirs(diretorio, exist_ok=True)
 69:     try:
 70:         con = duckdb.connect(caminho)
 71:     except Exception as e:
 72:         raise CacheIndisponivel(f"{caminho}: {e}") from e
 73:     try:
 74:         if CRIAR_TABELAS:
 75:             for ddl in _DDL:
 76:                 con.execute(ddl)
 77:         yield con
 78:     finally:
 79:         con.close()
 80: 
 81: 
 82: def _ler(con, sql, params=None):
 83:     """Executa uma leitura, traduzindo 'tabela não existe' em CacheIndisponivel."""
 84:     try:
 85:         return con.execute(sql, params) if params else con.execute(sql)
 86:     except duckdb.CatalogException as e:
 87:         raise CacheIndisponivel(
 88:             "tabelas de localidades não existem neste banco (rode a sincronização no menu)"
 89:         ) from e
 90: 
 91: 
 92: def _inserir_lote(con, df, sql):
 93:     if df is None or df.empty:
 94:         return
 95:     con.register("_lote", df)
 96:     try:
 97:         con.execute(sql)
 98:     finally:
 99:         con.unregister("_lote")
100: 
101: 
102: def ler_estados(db_path=None):
103:     with conexao(db_path) as con:
104:         df = _ler(con, "SELECT uf, nome FROM localidades_estados ORDER BY nome").df()
105:     return df.to_dict("records")
106: 
107: 
108: def salvar_estados(registros, db_path=None):
109:     df = pd.DataFrame(list(registros), columns=["uf", "nome"]).drop_duplicates("uf")
110:     with conexao(db_path) as con:
111:         _inserir_lote(con, df, """
112:             INSERT INTO localidades_estados (uf, nome)
113:             SELECT uf, nome FROM _lote
114:             ON CONFLICT (uf) DO UPDATE SET nome = excluded.nome
115:         """)
116:     return len(df)
117: 
118: 
119: def ler_municipios(uf, db_path=None):
120:     with conexao(db_path) as con:
121:         df = _ler(con,
122:             """SELECT id_municipio, nome, uf, bairros_fonte
123:                FROM localidades_municipios WHERE uf = ? ORDER BY nome""",
124:             [uf],
125:         ).df()
126:     return df.to_dict("records")
127: 
128: 
129: def ler_municipios_pendentes(uf, db_path=None):
130:     """Municípios da UF cujos bairros ainda não foram resolvidos (bairros_fonte nulo)."""
131:     with conexao(db_path) as con:
132:         df = _ler(con, """
133:             SELECT id_municipio, nome
134:             FROM localidades_municipios
135:             WHERE uf = ? AND bairros_fonte IS NULL
136:             ORDER BY nome
137:         """, [uf]).df()
138:     return df.to_dict("records")
139: 
140: 
141: def salvar_municipios(registros, db_path=None):
142:     df = pd.DataFrame(list(registros), columns=["id_municipio", "nome", "uf"])
143:     df = df.dropna(subset=["id_municipio"]).drop_duplicates("id_municipio")
144:     with conexao(db_path) as con:
145:         # UPSERT preserva bairros_fonte/bairros_atualizado_em já gravados.
146:         _inserir_lote(con, df, """
147:             INSERT INTO localidades_municipios (id_municipio, nome, uf)
148:             SELECT id_municipio, nome, uf FROM _lote
149:             ON CONFLICT (id_municipio) DO UPDATE SET
150:                 nome = excluded.nome,
151:                 uf = excluded.uf
152:         """)
153:     return len(df)
154: 
155: 
156: def buscar_municipio(cidade, uf, db_path=None):
157:     """Retorna {id_municipio, nome, uf, bairros_fonte} ou None se não estiver na base."""
158:     with conexao(db_path) as con:
159:         linha = _ler(con, """
160:             SELECT id_municipio, nome, uf, bairros_fonte
161:             FROM localidades_municipios
162:             WHERE uf = ? AND lower(nome) = lower(?)
163:             LIMIT 1
164:         """, [uf, cidade]).fetchone()
165:     if not linha:
166:         return None
167:     return {
168:         "id_municipio": linha[0],
169:         "nome": linha[1],
170:         "uf": linha[2],
171:         "bairros_fonte": linha[3],
172:     }
173: 
174: 
175: def ler_bairros(id_municipio, db_path=None):
176:     with conexao(db_path) as con:
177:         df = _ler(con,
178:             "SELECT nome FROM localidades_bairros WHERE id_municipio = ? ORDER BY nome",
179:             [int(id_municipio)],
180:         ).df()
181:     return df["nome"].tolist()
182: 
183: 
184: def _normalizar_bairros(registros):
185:     linhas = []
186:     for item in registros or []:
187:         if isinstance(item, dict):
188:             nome = str(item.get("nome") or "").strip()
189:             id_distrito = item.get("id_distrito")
190:         else:
191:             nome = str(item or "").strip()
192:             id_distrito = None
193:         if nome:
194:             linhas.append({"nome": nome, "id_distrito": id_distrito})
195: 
196:     df = pd.DataFrame(linhas, columns=["nome", "id_distrito"])
197:     if df.empty:
198:         return df
199:     df["id_distrito"] = df["id_distrito"].astype("Int64")
200:     return df.drop_duplicates("nome")
201: 
202: 
203: def salvar_bairros(id_municipio, registros, fonte, db_path=None):
204:     """Grava a lista final de bairros de uma cidade e marca a origem da coleta.
205: 
206:     A lista é autoritativa para a cidade: bairros que não estão nela são
207:     removidos, para o cache não acumular nomes de uma coleta anterior.
208:     `fonte` = 'ibge', 'overpass' ou 'cidade' (sem bairros úteis).
209:     """
210:     id_municipio = int(id_municipio)
211:     df = _normalizar_bairros(registros)
212: 
213:     with conexao(db_path) as con:
214:         if df.empty:
215:             con.execute(
216:                 "DELETE FROM localidades_bairros WHERE id_municipio = ?", [id_municipio]
217:             )
218:         else:
219:             df.insert(0, "id_municipio", id_municipio)
220:             con.register("_lote", df)
221:             try:
222:                 con.execute("""
223:                     DELETE FROM localidades_bairros
224:                     WHERE id_municipio = ?
225:                       AND nome NOT IN (SELECT nome FROM _lote)
226:                 """, [id_municipio])
227:                 con.execute("""
228:                     INSERT OR REPLACE INTO localidades_bairros (id_municipio, nome, id_distrito)
229:                     SELECT id_municipio, nome, id_distrito FROM _lote
230:                 """)
231:             finally:
232:                 con.unregister("_lote")
233: 
234:         con.execute("""
235:             UPDATE localidades_municipios
236:             SET bairros_fonte = ?, bairros_atualizado_em = ?
237:             WHERE id_municipio = ?
238:         """, [fonte, datetime.now(), id_municipio])
239:     return len(df)
240: 
241: 
242: def salvar_distritos_bulk(distritos, min_bairros=3, db_path=None):
243:     """Grava todos os distritos do IBGE de uma vez (sincronização completa).
244: 
245:     É aditivo (INSERT OR REPLACE por id_municipio+nome): não apaga bairros que já
246:     existem, para não destruir listas complementadas pelo OpenStreetMap.
247: 
248:     Marca como 'ibge' apenas os municípios com pelo menos `min_bairros` distritos
249:     úteis (ou seja, desconsiderando o distrito que tem o mesmo nome da cidade).
250:     Os demais continuam sem fonte definida e serão complementados via Overpass
251:     na primeira consulta.
252:     """
253:     df = pd.DataFrame(list(distritos), columns=["id_municipio", "nome", "id_distrito"])
254:     df = df.dropna(subset=["id_municipio", "nome"]).drop_duplicates(["id_municipio", "nome"])
255:     df["id_distrito"] = df["id_distrito"].astype("Int64")
256: 
257:     with conexao(db_path) as con:
258:         _inserir_lote(con, df, """
259:             INSERT OR REPLACE INTO localidades_bairros (id_municipio, nome, id_distrito)
260:             SELECT id_municipio, nome, id_distrito FROM _lote
261:         """)
262:         con.execute("DROP TABLE IF EXISTS _cobertura")
263:         con.execute("""
264:             CREATE TEMP TABLE _cobertura AS
265:             SELECT b.id_municipio
266:             FROM localidades_bairros b
267:             JOIN localidades_municipios m ON m.id_municipio = b.id_municipio
268:             WHERE lower(b.nome) <> lower(m.nome)
269:             GROUP BY b.id_municipio
270:             HAVING COUNT(*) >= ?
271:         """, [int(min_bairros)])
272:         con.execute("""
273:             UPDATE localidades_municipios
274:             SET bairros_fonte = ?, bairros_atualizado_em = ?
275:             WHERE bairros_fonte IS NULL
276:               AND id_municipio IN (SELECT id_municipio FROM _cobertura)
277:         """, [FONTE_IBGE, datetime.now()])
278:         con.execute("DROP TABLE IF EXISTS _cobertura")
279:     return len(df)
280: 
281: 
282: def estatisticas(db_path=None):
283:     with conexao(db_path) as con:
284:         estados = _ler(con, "SELECT COUNT(*) FROM localidades_estados").fetchone()[0]
285:         municipios = _ler(con, "SELECT COUNT(*) FROM localidades_municipios").fetchone()[0]
286:         bairros = _ler(con, "SELECT COUNT(*) FROM localidades_bairros").fetchone()[0]
287:         prontas = _ler(con, """
288:             SELECT COUNT(*) FROM localidades_municipios WHERE bairros_fonte IS NOT NULL
289:         """).fetchone()[0]
290:     return {
291:         "estados": estados,
292:         "municipios": municipios,
293:         "bairros": bairros,
294:         "cidades_prontas": prontas,
295:     }
````

## File: .env.example
````
  1: # =============================================================================
  2: # MAP SCRAPER - arquivo de exemplo de configuração
  3: # -----------------------------------------------------------------------------
  4: # Copie para `.env` e ajuste:
  5: #     Copy-Item .env.example .env
  6: #
  7: # REGRAS IMPORTANTES
  8: #  - Formato: CHAVE=VALOR, uma por linha.
  9: #  - Comentários (linhas que começam com #) podem ficar à vontade, mas SEMPRE em
 10: #    linha própria. Não coloque comentário na mesma linha do valor, porque ele
 11: #    seria lido como parte do valor.
 12: #  - true/false: também aceita 1/0, sim/não, s/yes/on.
 13: #  - O arquivo `.env` NÃO é versionado no Git (contém a API key da WAHA).
 14: # =============================================================================
 15: 
 16: 
 17: # =============================================================================
 18: # WHATSAPP - WAHA (WhatsApp HTTP API)
 19: # =============================================================================
 20: 
 21: # URL base da sua instância WAHA (Docker local, por exemplo).
 22: # Usada em todas as chamadas de envio. Não coloque a barra final.
 23: WAHA_API_URL=http://localhost:3000
 24: 
 25: # Chave de API da WAHA. É o valor de WHATSAPP_API_KEY no .env do Docker/init-waha.
 26: # Deixe vazio se a sua instância estiver sem autenticação.
 27: WAHA_API_KEY=
 28: 
 29: # Nome da sessão do WhatsApp já conectada (lida por QR Code), normalmente `default`.
 30: # Precisa ser exatamente o nome que aparece em /api/sessions da WAHA.
 31: WAHA_SESSION=default
 32: 
 33: # Liga/desliga TODO o envio de WhatsApp.
 34: #   true  = o menu "2 - Enviar mensagens WhatsApp" funciona normalmente.
 35: #   false = o menu avisa que o envio está desativado e não faz nada.
 36: # Isso NÃO afeta a coleta de leads, apenas o disparo de mensagens.
 37: WAHA_ATIVO=true
 38: 
 39: # Atalho que pula o menu e vai direto para o envio, sem coletar nada.
 40: #   true  = equivale a rodar: python src/main.py --so-enviar
 41: #   false = abre o menu normal (coleta + envio).
 42: # Útil para rodar uma campanha agendada, por exemplo.
 43: SOMENTE_ENVIO=false
 44: 
 45: # Pausa em SEGUNDOS entre um envio e o próximo (13s ≈ 4-5 mensagens por minuto).
 46: # Pausas muito curtas aumentam o risco de banimento do número.
 47: WAHA_INTERVALO=13
 48: 
 49: # Quantidade máxima de leads por campanha. Vazio = sem limite (envia todos
 50: # os pendentes). Só conta leads celulares, ativos e ainda não enviados.
 51: WAHA_LIMITE=
 52: 
 53: 
 54: # =============================================================================
 55: # BASE DE LOCALIDADES (IBGE) - cache em DuckDB: tabelas localidades_*
 56: # -----------------------------------------------------------------------------
 57: # As duas flags abaixo são independentes. Combinações possíveis:
 58: #
 59: #   USAR_CACHE  SALVAR   O que acontece
 60: #   true        true     usa o banco; só vai à API do que falta e grava (padrão)
 61: #   false       true     ignora o banco, sempre vai à API e regrava (força refresh)
 62: #   true        false    usa o banco; o que falta vai à API mas NÃO é gravado
 63: #   false       false    sempre API, e o banco nunca é tocado (somente leitura)
 64: # =============================================================================
 65: 
 66: # Consultar a base local ANTES da API do IBGE?
 67: #   true  = se o dado já existe no DuckDB, nem chama a internet (rápido).
 68: #   false = sempre chama a API do IBGE, mesmo que o dado já esteja no banco.
 69: LOCALIDADES_USAR_CACHE=true
 70: 
 71: # Permitir GRAVAR na base local?
 72: #   true  = pode inserir/atualizar (UPSERT) os estados, municípios e bairros.
 73: #   false = modo somente leitura: nada é gravado e nem as tabelas são criadas.
 74: # ATENÇÃO: com false, os menus "3 - Sincronizar" e "4 - Aquecer bairros" ficam
 75: # desativados, e cada execução consulta as APIs de novo.
 76: LOCALIDADES_SALVAR=true
 77: 
 78: # Mínimo de distritos do IBGE para considerar a cidade "coberta" pelo IBGE.
 79: # A API de Localidades do IBGE tem distritos (não bairros). Cidade com menos
 80: # distritos que este número é complementada com o OpenStreetMap.
 81: # Exemplo: Campinas-SP tem 7 distritos -> usa só o IBGE.
 82: #          Canoas-RS tem 1 distrito (a sede) -> vai para o OpenStreetMap.
 83: LOCALIDADES_MIN_BAIRROS=3
 84: 
 85: # Pausa em SEGUNDOS entre cidades no menu "4 - Aquecer bairros de uma UF".
 86: # Só é aplicada quando a cidade precisou do OpenStreetMap (Nominatim permite
 87: # ~1 requisição por segundo). Cidades resolvidas pelo IBGE não esperam.
 88: AQUECER_PAUSA_SEGUNDOS=2
 89: 
 90: 
 91: # =============================================================================
 92: # GOOGLE MAPS - captcha / bloqueio ("tráfego incomum")
 93: # -----------------------------------------------------------------------------
 94: # Quando o Google bloqueia, o robô pausa e tenta de novo. Se continuar bloqueado,
 95: # ele aborta APENAS aquela área e mantém os leads já coletados.
 96: # =============================================================================
 97: 
 98: # Quantas tentativas por página antes de desistir da área.
 99: #   1  = não tenta de novo, só pausa uma vez e desiste.
100: #   2  = pausa e tenta mais uma vez (padrão).
101: # Valores altos aumentam o risco de piorar o bloqueio.
102: CAPTCHA_MAX_TENTATIVAS=2
103: 
104: # Pausa longa em SEGUNDOS feita pela thread que recebeu o captcha antes de
105: # tentar a mesma página novamente.
106: CAPTCHA_PAUSA_SEGUNDOS=300
107: 
108: # Pausa compartilhada em SEGUNDOS aplicada a TODAS as threads assim que uma
109: # delas detecta bloqueio (evita que as outras continuem martelando o Google).
110: CAPTCHA_PAUSA_GLOBAL_SEGUNDOS=180
````

## File: src/scraper.py
````python
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
````

## File: src/locations.py
````python
  1: # src/locations.py
  2: """Localidades (UF, cidade e bairros) com cache local em DuckDB.
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
 42: # Se false: NUNCA grava na base local (nem cria tabelas). Funciona como
 43: # "somente leitura": o banco é consultado, mas nada é alterado.
 44: SALVAR = str_para_bool(os.environ.get("LOCALIDADES_SALVAR"), padrao=True)
 45: 
 46: # Reflete a flag no módulo de acesso ao banco (controla a criação das tabelas).
 47: localidades_db.CRIAR_TABELAS = SALVAR
 48: 
 49: # Quantidade mínima de distritos úteis para não precisar do OpenStreetMap.
 50: # Abaixo disso, a cidade é complementada com bairros do OSM.
 51: MIN_BAIRROS = max(1, env_int("LOCALIDADES_MIN_BAIRROS", 3))
 52: 
 53: # Pausa (segundos) entre cidades no aquecimento por UF, aplicada apenas quando o
 54: # OpenStreetMap foi consultado (política de uso do Nominatim: 1 req/s).
 55: AQUECER_PAUSA_PADRAO = max(0, env_int("AQUECER_PAUSA_SEGUNDOS", 2))
 56: 
 57: _avisou_cache_indisponivel = False
 58: _avisou_sem_gravacao = False
 59: 
 60: 
 61: def _cache(funcao, *args, **kwargs):
 62:     """Executa uma operação na base local, tolerando banco travado/indisponível."""
 63:     global _avisou_cache_indisponivel
 64:     try:
 65:         return funcao(*args, **kwargs)
 66:     except localidades_db.CacheIndisponivel as e:
 67:         if not _avisou_cache_indisponivel:
 68:             print(f"  Aviso: base local de localidades indisponível ({e}).")
 69:             print("         Seguindo apenas com as APIs (IBGE/OSM).")
 70:             _avisou_cache_indisponivel = True
 71:         return None
 72: 
 73: 
 74: def _salvar(funcao, *args, **kwargs):
 75:     """Grava na base local, respeitando LOCALIDADES_SALVAR=false."""
 76:     global _avisou_sem_gravacao
 77:     if not SALVAR:
 78:         if not _avisou_sem_gravacao:
 79:             print("  LOCALIDADES_SALVAR=false: a base local não será alterada.")
 80:             _avisou_sem_gravacao = True
 81:         return None
 82:     return _cache(funcao, *args, **kwargs)
 83: 
 84: 
 85: # ---------------------------------------------------------------------------
 86: # IBGE
 87: # ---------------------------------------------------------------------------
 88: def _get_json(url, params=None, timeout=60, tentativas=3):
 89:     for tentativa in range(1, tentativas + 1):
 90:         try:
 91:             resposta = requests.get(url, params=params, timeout=timeout, headers=HEADERS)
 92:             resposta.raise_for_status()
 93:             return resposta.json()
 94:         except Exception as e:
 95:             print(f"  IBGE indisponível (tentativa {tentativa}/{tentativas}): {type(e).__name__}")
 96:             if tentativa < tentativas:
 97:                 time.sleep(1.5 * tentativa)
 98:     return None
 99: 
100: 
101: def _baixar_estados():
102:     dados = _get_json(f"{IBGE_API}/estados", params={"orderBy": "nome"}, timeout=30)
103:     if not dados:
104:         return None
105:     return [{"uf": e["sigla"], "nome": e["nome"]} for e in dados]
106: 
107: 
108: def _uf_do_municipio(municipio):
109:     try:
110:         return municipio["microrregiao"]["mesorregiao"]["UF"]["sigla"]
111:     except (KeyError, TypeError):
112:         try:
113:             return municipio["regiao-imediata"]["regiao-intermediaria"]["UF"]["sigla"]
114:         except (KeyError, TypeError):
115:             return None
116: 
117: 
118: def _baixar_municipios(uf=None):
119:     url = f"{IBGE_API}/estados/{uf}/municipios" if uf else f"{IBGE_API}/municipios"
120:     dados = _get_json(url, params={"orderBy": "nome"})
121:     if not dados:
122:         return None
123: 
124:     registros = []
125:     for municipio in dados:
126:         sigla = uf or _uf_do_municipio(municipio)
127:         if not sigla:
128:             continue
129:         registros.append({
130:             "id_municipio": municipio["id"],
131:             "nome": municipio["nome"],
132:             "uf": sigla,
133:         })
134:     return registros
135: 
136: 
137: def _baixar_distritos(id_municipio=None):
138:     url = (f"{IBGE_API}/municipios/{id_municipio}/distritos"
139:            if id_municipio else f"{IBGE_API}/distritos")
140:     dados = _get_json(url)
141:     if not dados:
142:         return None
143: 
144:     registros = []
145:     for distrito in dados:
146:         municipio = distrito.get("municipio") or {}
147:         registros.append({
148:             "id_distrito": distrito.get("id"),
149:             "nome": (distrito.get("nome") or "").strip(),
150:             "id_municipio": municipio.get("id"),
151:         })
152:     return [r for r in registros if r["id_municipio"] and r["nome"]]
153: 
154: 
155: _municipios_memoria = {}
156: 
157: 
158: def _municipios_da_uf(uf):
159:     """Lista de municípios da UF, memorizada na execução para não baixar duas vezes."""
160:     if uf not in _municipios_memoria:
161:         print(f"  Baixando a lista de municípios de {uf} do IBGE...")
162:         municipios = _baixar_municipios(uf)
163:         if municipios is None:
164:             return None
165:         _municipios_memoria[uf] = municipios
166:     return _municipios_memoria[uf]
167: 
168: 
169: # ---------------------------------------------------------------------------
170: # OpenStreetMap (fallback de bairros)
171: # ---------------------------------------------------------------------------
172: def _obter_bbox_cidade(cidade, uf):
173:     """Retorna (sul, norte, oeste, leste) da cidade via Nominatim."""
174:     url = "https://nominatim.openstreetmap.org/search"
175:     params = {"format": "json", "q": f"{cidade}, {uf}, Brazil", "limit": 1}
176:     try:
177:         resposta = requests.get(url, params=params, timeout=15, headers=HEADERS)
178:         resposta.raise_for_status()
179:         resultados = resposta.json()
180:         if not resultados:
181:             return None
182:         bb = resultados[0].get("boundingbox")
183:         if not bb or len(bb) != 4:
184:             return None
185:         sul, norte, oeste, leste = (float(v) for v in bb)
186:         return (sul, norte, oeste, leste)
187:     except Exception as e:
188:         print(f"Erro ao localizar a cidade no Nominatim: {e}")
189:         return None
190: 
191: 
192: def _consultar_overpass(query):
193:     """Tenta a consulta em vários espelhos do Overpass, com retry e backoff.
194: 
195:     Retorna o JSON da resposta, ou None quando nenhum espelho respondeu
196:     (serviço indisponível) — o que é diferente de responder vazio.
197:     """
198:     for endpoint in OVERPASS_ENDPOINTS:
199:         for tentativa in range(1, 3):
200:             try:
201:                 resposta = requests.get(endpoint, params={"data": query}, timeout=45, headers=HEADERS)
202:                 resposta.raise_for_status()
203:                 return resposta.json()
204:             except Exception as e:
205:                 print(f"  Overpass ({endpoint}) tentativa {tentativa} falhou: {type(e).__name__}")
206:                 time.sleep(1.5 * tentativa)
207:     return None
208: 
209: 
210: def _obter_bairros_overpass(sul, norte, oeste, leste):
211:     """Busca bairros dentro do bbox via Overpass (place=* e admin_level 9/10)."""
212:     bbox = f"({sul},{oeste},{norte},{leste})"
213: 
214:     query_leve = f"""
215: [out:json][timeout:40];
216: (
217:   node["place"~"^(suburb|neighbourhood|quarter)$"]{bbox};
218:   way["place"~"^(suburb|neighbourhood|quarter)$"]{bbox};
219: );
220: out center tags;
221: """
222: 
223:     query_admin = f"""
224: [out:json][timeout:55];
225: (
226:   relation["boundary"="administrative"]["admin_level"="9"]{bbox};
227:   relation["boundary"="administrative"]["admin_level"="10"]{bbox};
228: );
229: out center tags;
230: """
231: 
232:     data = _consultar_overpass(query_leve)
233:     if data is None:
234:         return None
235:     if data.get("elements"):
236:         return data
237:     return _consultar_overpass(query_admin)
238: 
239: 
240: def _bairros_via_overpass(cidade, uf):
241:     """Retorna a lista de bairros do OSM, ou None se o serviço estiver indisponível."""
242:     bbox = _obter_bbox_cidade(cidade, uf)
243:     if not bbox:
244:         return None
245: 
246:     data = _obter_bairros_overpass(*bbox)
247:     if data is None:
248:         return None
249: 
250:     nomes = set()
251:     for elemento in data.get("elements", []):
252:         tags = elemento.get("tags") or {}
253:         nome = tags.get("name")
254:         if not isinstance(nome, str):
255:             continue
256:         nome = nome.strip()
257:         if nome and nome.lower() != cidade.strip().lower():
258:             nomes.add(nome)
259:     return sorted(nomes)
260: 
261: 
262: # ---------------------------------------------------------------------------
263: # API pública do módulo
264: # ---------------------------------------------------------------------------
265: def obter_estados():
266:     if USAR_CACHE:
267:         estados = _cache(localidades_db.ler_estados)
268:         if estados:
269:             print(f"Base local: {len(estados)} estados.")
270:             return pd.DataFrame(estados)
271: 
272:     estados = _baixar_estados()
273:     if estados is None:
274:         estados = _cache(localidades_db.ler_estados)
275:         if estados:
276:             print("IBGE indisponível. Usando os estados gravados na base local.")
277:             return pd.DataFrame(estados)
278:         print("Erro ao buscar estados.")
279:         return pd.DataFrame()
280: 
281:     _salvar(localidades_db.salvar_estados, estados)
282:     return pd.DataFrame(estados)
283: 
284: 
285: def obter_cidades(uf):
286:     if USAR_CACHE:
287:         municipios = _cache(localidades_db.ler_municipios, uf)
288:         if municipios:
289:             print(f"Base local: {len(municipios)} cidades em {uf}.")
290:             return [m["nome"] for m in municipios]
291: 
292:     municipios = _municipios_da_uf(uf)
293:     if municipios is None:
294:         municipios = _cache(localidades_db.ler_municipios, uf)
295:         if municipios:
296:             print(f"IBGE indisponível. Usando as cidades de {uf} gravadas na base local.")
297:             return [m["nome"] for m in municipios]
298:         print(f"Erro ao buscar cidades para {uf}.")
299:         return []
300: 
301:     _salvar(localidades_db.salvar_municipios, municipios)
302:     return sorted(m["nome"] for m in municipios)
303: 
304: 
305: def _normalizar(texto):
306:     """Minúsculas e sem acentos, para comparar nomes digitados pelo usuário."""
307:     texto = unicodedata.normalize("NFKD", str(texto or ""))
308:     return "".join(c for c in texto if not unicodedata.combining(c)).strip().casefold()
309: 
310: 
311: def filtrar_cidades(cidades, termo):
312:     """Filtra a lista de cidades por um trecho, ignorando acentos e maiúsculas."""
313:     alvo = _normalizar(termo)
314:     if not alvo:
315:         return []
316:     return [c for c in cidades if alvo in _normalizar(c)]
317: 
318: 
319: def _descobrir_bairros(cidade, uf, municipio):
320:     """Monta a lista final de bairros: distritos do IBGE + complemento do OSM.
321: 
322:     Retorna (registros, fonte). fonte=None significa "não gravar no cache" —
323:     usado quando houve falha de rede, para tentar de novo na próxima execução.
324:     """
325:     registros = []
326:     total_distritos = 0
327:     if municipio:
328:         distritos = _baixar_distritos(municipio["id_municipio"]) or []
329:         total_distritos = len(distritos)
330:         for distrito in distritos:
331:             if _normalizar(distrito["nome"]) == _normalizar(cidade):
332:                 continue
333:             registros.append({"nome": distrito["nome"], "id_distrito": distrito["id_distrito"]})
334: 
335:     if len(registros) >= MIN_BAIRROS:
336:         print(f"  IBGE: {len(registros)} distritos de {cidade}-{uf} serão usados como áreas de busca.")
337:         return registros, localidades_db.FONTE_IBGE
338: 
339:     # A API de Localidades do IBGE só tem distritos/subdistritos — não tem bairros.
340:     # Quando o município tem apenas o distrito-sede, não há o que aproveitar.
341:     if total_distritos <= 1:
342:         print(f"  IBGE não publica bairros para {cidade}-{uf}: o município tem apenas "
343:               f"{total_distritos} distrito (a sede).")
344:     else:
345:         print(f"  IBGE: apenas {len(registros)} distrito(s) além da sede em {cidade}-{uf}.")
346: 
347:     print("  Buscando bairros no OpenStreetMap...")
348:     bairros_osm = _bairros_via_overpass(cidade, uf)
349: 
350:     if bairros_osm is None:
351:         print("  OpenStreetMap indisponível. Esta cidade NÃO será gravada no cache;")
352:         print("  os distritos do IBGE serão usados apenas nesta execução.")
353:         return registros, None
354: 
355:     vistos = {_normalizar(r["nome"]) for r in registros}
356:     for nome in bairros_osm:
357:         if _normalizar(nome) not in vistos:
358:             vistos.add(_normalizar(nome))
359:             registros.append({"nome": nome, "id_distrito": None})
360: 
361:     if bairros_osm:
362:         return registros, localidades_db.FONTE_OVERPASS
363:     if registros:
364:         return registros, localidades_db.FONTE_IBGE
365:     return [], localidades_db.FONTE_CIDADE
366: 
367: 
368: def _resolver_municipio(cidade, uf):
369:     """Descobre o município no IBGE: id e nome oficial.
370: 
371:     Primeiro tenta a base local; se não achar, baixa a lista da UF (e grava, se
372:     LOCALIDADES_SALVAR permitir). Retorna None quando o nome não existe na UF.
373:     """
374:     alvo = _normalizar(cidade)
375: 
376:     municipios = _cache(localidades_db.ler_municipios, uf) or []
377:     for item in municipios:
378:         if _normalizar(item["nome"]) == alvo:
379:             return {
380:                 "id_municipio": item["id_municipio"],
381:                 "nome": item["nome"],
382:                 "uf": uf,
383:                 "bairros_fonte": item.get("bairros_fonte"),
384:             }
385: 
386:     baixados = _municipios_da_uf(uf) or []
387:     _salvar(localidades_db.salvar_municipios, baixados)
388: 
389:     for item in baixados:
390:         if _normalizar(item["nome"]) == alvo:
391:             return {
392:                 "id_municipio": item["id_municipio"],
393:                 "nome": item["nome"],
394:                 "uf": item["uf"],
395:                 "bairros_fonte": None,
396:             }
397: 
398:     if mun := _cache(localidades_db.buscar_municipio, cidade, uf):
399:         return mun
400:     return None
401: 
402: 
403: def obter_municipio(cidade, uf):
404:     """Retorna o município do IBGE para o nome digitado (id, nome oficial e uf).
405: 
406:     Útil para gravar sempre o nome oficial, mesmo que o usuário digite sem
407:     acento ou em minúsculas (ex.: "canoas" -> "Canoas").
408:     """
409:     return _resolver_municipio(cidade, uf)
410: 
411: 
412: def obter_bairros(cidade, uf):
413:     """
414:     Retorna os bairros de uma cidade, usando a base local quando possível.
415:     Lista vazia significa "buscar a cidade inteira".
416:     """
417:     municipio = _resolver_municipio(cidade, uf)
418: 
419:     # Nome oficial do IBGE: evita divergência de acento/caixa nas buscas.
420:     nome_oficial = municipio["nome"] if municipio else cidade
421: 
422:     if USAR_CACHE and municipio and municipio.get("bairros_fonte"):
423:         bairros = _cache(localidades_db.ler_bairros, municipio["id_municipio"]) or []
424:         # O distrito-sede tem o mesmo nome da cidade e não ajuda na busca por área.
425:         bairros = [b for b in bairros if _normalizar(b) != _normalizar(nome_oficial)]
426:         fonte = municipio["bairros_fonte"]
427:         if fonte == localidades_db.FONTE_CIDADE or not bairros:
428:             print(f"Base local: {nome_oficial}-{uf} sem bairros (fonte: {fonte}).")
429:             return []
430:         print(f"Base local: {len(bairros)} bairros de {nome_oficial}-{uf} (fonte: {fonte}).")
431:         return bairros
432: 
433:     bairros, fonte = _descobrir_bairros(nome_oficial, uf, municipio)
434: 
435:     if municipio and fonte:
436:         _salvar(localidades_db.salvar_bairros, municipio["id_municipio"], bairros, fonte)
437: 
438:     return [b["nome"] for b in bairros]
439: 
440: 
441: def obter_termos_busca(cidade, uf, max_bairros=30):
442:     """
443:     Divide a coleta por bairros para ampliar a cobertura do Google Maps
444:     (que pagina os resultados e não entrega a cidade inteira em uma única busca).
445:     Se nenhum bairro for descoberto, busca a cidade inteira como fallback.
446:     """
447:     print(f"Descobrindo bairros de {cidade} - {uf}...")
448:     bairros = obter_bairros(cidade, uf)
449: 
450:     if bairros:
451:         bairros = bairros[:max_bairros]
452:         print(f"{len(bairros)} bairros encontrados. A coleta será dividida por bairro.")
453:         return bairros
454: 
455:     print("Nenhum bairro encontrado. Buscando a cidade inteira.")
456:     return [cidade]
457: 
458: 
459: def listar_municipios_pendentes(uf):
460:     """Lista os municípios da UF que ainda não têm bairros resolvidos.
461: 
462:     Se a UF ainda não estiver na base local, baixa a lista do IBGE (e grava, se
463:     LOCALIDADES_SALVAR permitir). Retorna [] quando todos já estão resolvidos.
464:     """
465:     pendentes = _cache(localidades_db.ler_municipios_pendentes, uf)
466:     if pendentes is None:
467:         return []
468:     if pendentes:
469:         return pendentes
470: 
471:     # Nada pendente: só é "tudo pronto" se a UF estiver na base local.
472:     if _cache(localidades_db.ler_municipios, uf):
473:         return []
474: 
475:     print(f"  {uf} ainda não está na base local. Baixando a lista de municípios do IBGE...")
476:     municipios = _baixar_municipios(uf)
477:     if not municipios:
478:         return []
479:     _salvar(localidades_db.salvar_municipios, municipios)
480:     return [{"id_municipio": m["id_municipio"], "nome": m["nome"]} for m in municipios]
481: 
482: 
483: def aquecer_bairros_uf(uf, cidades=None, max_cidades=0, pausa_segundos=None):
484:     """Resolve e grava os bairros de todas as cidades de uma UF (uma única vez).
485: 
486:     Útil para preparar o cache e depois rodar a coleta sem nenhuma consulta de
487:     rede. A pausa entre cidades é aplicada só quando o OpenStreetMap foi de fato
488:     consultado (cidades cobertas pelo IBGE são instantâneas).
489: 
490:     Retorna um dicionário com o resumo da execução.
491:     """
492:     if not SALVAR:
493:         print("\nLOCALIDADES_SALVAR=false: não é possível aquecer a base local.")
494:         print("Ative a flag LOCALIDADES_SALVAR para gravar os bairros.")
495:         return None
496: 
497:     pausa_segundos = AQUECER_PAUSA_PADRAO if pausa_segundos is None else pausa_segundos
498: 
499:     if cidades is None:
500:         print(f"\nVerificando quais cidades de {uf} ainda precisam de bairros...")
501:         cidades = listar_municipios_pendentes(uf)
502: 
503:     total_pendente = len(cidades)
504:     if not total_pendente:
505:         print(f"Todas as cidades de {uf} já têm bairros na base local. Nada a fazer.")
506:         return {"uf": uf, "pendentes": 0, "processadas": 0, "ibge": 0,
507:                 "osm": 0, "sem_bairros": 0, "falhas": 0}
508: 
509:     if max_cidades and max_cidades > 0:
510:         cidades = cidades[:max_cidades]
511: 
512:     print(f"\nAquecendo bairros de {len(cidades)} cidade(s) de {uf} "
513:           f"({total_pendente} pendente(s) no total).")
514:     print(f"Pausa entre cidades que usam OpenStreetMap: {pausa_segundos}s")
515:     print("Interrompa com Ctrl+C — o progresso já gravado é preservado.\n")
516: 
517:     resumo = {"uf": uf, "pendentes": total_pendente, "processadas": 0,
518:               "ibge": 0, "osm": 0, "sem_bairros": 0, "falhas": 0}
519: 
520:     try:
521:         for indice, cidade in enumerate(cidades, 1):
522:             nome = cidade["nome"]
523:             print(f"[{indice}/{len(cidades)}] {nome}-{uf}")
524: 
525:             bairros = obter_bairros(nome, uf)
526:             municipio = _cache(localidades_db.buscar_municipio, nome, uf)
527:             fonte = (municipio or {}).get("bairros_fonte")
528:             resumo["processadas"] += 1
529: 
530:             if fonte is None:
531:                 resumo["falhas"] += 1
532:                 print(f"  Falhou (nada gravado). Pulando.")
533:             elif fonte == localidades_db.FONTE_OVERPASS:
534:                 resumo["osm"] += 1
535:             elif fonte == localidades_db.FONTE_IBGE:
536:                 resumo["ibge"] += 1
537:             else:
538:                 resumo["sem_bairros"] += 1
539: 
540:             usou_osm = fonte in (localidades_db.FONTE_OVERPASS,
541:                                  localidades_db.FONTE_CIDADE)
542:             if usou_osm and indice < len(cidades):
543:                 time.sleep(pausa_segundos)
544:     except KeyboardInterrupt:
545:         print("\nInterrompido pelo usuário. O que já foi gravado está preservado.")
546: 
547:     print(f"\nResumo de {uf}: {resumo['processadas']} cidade(s) processada(s) "
548:           f"de {total_pendente} pendente(s).")
549:     print(f"  via IBGE: {resumo['ibge']} | via OpenStreetMap: {resumo['osm']} | "
550:           f"sem bairros: {resumo['sem_bairros']} | falhas: {resumo['falhas']}")
551:     restantes = total_pendente - resumo["processadas"]
552:     if restantes > 0:
553:         print(f"  {restantes} cidade(s) continuam pendentes — rode novamente para retomar.")
554:     return resumo
555: 
556: 
557: def _descrever_gravacao(total, recebidos):
558:     """Texto do resumo da sincronização (distingue gravado de apenas baixado)."""
559:     if total is None:
560:         return f"{recebidos} recebidos, NÃO gravados (base local indisponível)"
561:     return f"{total} gravados"
562: 
563: 
564: def sincronizar_base_localidades():
565:     """Baixa estados, municípios e distritos do IBGE para o DuckDB.
566: 
567:     Depois disso, com LOCALIDADES_USAR_CACHE=true, a coleta não faz chamadas de
568:     rede para descobrir bairros — exceto nas cidades em que o IBGE não tem
569:     distritos úteis (aí o OSM é consultado uma única vez e o resultado é gravado).
570:     """
571:     if not SALVAR:
572:         print("\nLOCALIDADES_SALVAR=false: a sincronização está desativada.")
573:         print("Nada foi baixado nem gravado. Ative a flag para popular a base local.")
574:         return False
575: 
576:     print("\nSincronizando base de localidades do IBGE...")
577: 
578:     estados = _baixar_estados()
579:     if estados is None:
580:         print("Falha ao baixar os estados. Sincronização abortada.")
581:         return False
582:     total = _salvar(localidades_db.salvar_estados, estados)
583:     print(f"  Estados: {_descrever_gravacao(total, len(estados))}.")
584: 
585:     municipios = _baixar_municipios()
586:     if municipios is None:
587:         print("Falha ao baixar os municípios. Sincronização abortada.")
588:         return False
589:     total = _salvar(localidades_db.salvar_municipios, municipios)
590:     print(f"  Municípios: {_descrever_gravacao(total, len(municipios))}.")
591: 
592:     print("  Baixando distritos (pode levar alguns segundos)...")
593:     distritos = _baixar_distritos()
594:     if distritos is None:
595:         print("Falha ao baixar os distritos. Estados e municípios foram gravados.")
596:         return False
597:     total = _salvar(localidades_db.salvar_distritos_bulk, distritos, MIN_BAIRROS)
598:     print(f"  Distritos: {_descrever_gravacao(total, len(distritos))}.")
599: 
600:     stats = _cache(localidades_db.estatisticas) or {}
601:     print(f"\nBase local: {stats.get('estados', 0)} estados, "
602:           f"{stats.get('municipios', 0)} municípios, {stats.get('bairros', 0)} bairros "
603:           f"({stats.get('cidades_prontas', 0)} cidades com bairros prontos).")
604:     print("Sincronização concluída.")
605:     return True
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
 22:     MENSAGEM_PADRAO,
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
 91: def enviar_whatsapp_menu():
 92:     print("\n=== ENVIO WHATSAPP (WAHA) ===")
 93: 
 94:     if not WAHA_ATIVO:
 95:         print("Envio de WhatsApp desativado (WAHA_ATIVO=false no .env).")
 96:         return
 97: 
 98:     db = LeadDatabase()
 99: 
100:     pendentes = db.get_leads_para_envio(limite=WAHA_LIMITE)
101:     if pendentes.empty:
102:         print("Nenhum lead celular pendente de envio.")
103:         db.close()
104:         return
105: 
106:     print(f"{len(pendentes)} lead(s) celular(es) pendentes (fixos são ignorados).")
107:     if WAHA_LIMITE:
108:         print(f"Limite configurado: {WAHA_LIMITE} lead(s) por campanha.")
109: 
110:     print(f"Mensagem padrão: {MENSAGEM_PADRAO}")
111:     mensagem = input("Digite a mensagem (ou Enter para usar a padrão): ").strip()
112:     if not mensagem:
113:         mensagem = MENSAGEM_PADRAO
114: 
115:     confirmar = input(f"Enviar para {len(pendentes)} lead(s)? (S/N): ").strip().upper()
116:     if confirmar != 'S':
117:         print("Envio cancelado.")
118:         db.close()
119:         return
120: 
121:     disparar_campanha(db, mensagem_template=mensagem, intervalo=WAHA_INTERVALO, limite=WAHA_LIMITE)
122:     db.close()
123: 
124: 
125: def aquecer_bairros_menu():
126:     """Prepara o cache de bairros de uma UF inteira (sem raspar leads)."""
127:     print("\n=== AQUECER BAIRROS DE UMA UF ===")
128: 
129:     if not LOCALIDADES_SALVAR:
130:         print("LOCALIDADES_SALVAR=false: o aquecimento está desativado.")
131:         print("Ative a flag LOCALIDADES_SALVAR no .env para gravar os bairros.")
132:         return
133: 
134:     print("Resolve e grava os bairros de todas as cidades da UF, uma única vez.")
135:     print("Depois disso a coleta por cidade não consulta mais IBGE/OSM.")
136: 
137:     df_estados = obter_estados()
138:     if df_estados.empty:
139:         print("Não foi possível obter a lista de estados.")
140:         return
141: 
142:     uf = input("Digite a UF (ex: RS, SP, RJ): ").strip().upper()
143:     if uf not in df_estados['uf'].values:
144:         print("UF inválida.")
145:         return
146: 
147:     print(f"\nVerificando quais cidades de {uf} ainda precisam de bairros...")
148:     pendentes = listar_municipios_pendentes(uf)
149:     if not pendentes:
150:         print(f"Todas as cidades de {uf} já estão na base local. Nada a fazer.")
151:         return
152: 
153:     print(f"{len(pendentes)} cidade(s) pendente(s) em {uf}.")
154:     print("As cidades cobertas pelo IBGE são instantâneas; as demais usam o")
155:     print("OpenStreetMap (Nominatim + Overpass), com pausa entre elas.")
156: 
157:     limite = input("Quantas cidades processar agora? (Enter = todas): ").strip()
158:     max_cidades = 0
159:     if limite:
160:         try:
161:             max_cidades = max(1, int(limite))
162:         except ValueError:
163:             print("Valor inválido. Usando todas.")
164:             max_cidades = 0
165: 
166:     previstas = min(max_cidades, len(pendentes)) if max_cidades else len(pendentes)
167:     confirmar = input(f"Processar {previstas} cidade(s)? (S/N): ").strip().upper()
168:     if confirmar != 'S':
169:         print("Operação cancelada.")
170:         return
171: 
172:     aquecer_bairros_uf(uf, cidades=pendentes, max_cidades=max_cidades)
173: 
174: 
175: def menu_interativo():
176:     # Flag de linha de comando: `python src/main.py --so-enviar` pula a coleta
177:     # e vai direto para o envio (equivale a SOMENTE_ENVIO=true no .env).
178:     so_enviar_cli = "--so-enviar" in sys.argv
179: 
180:     if SOMENTE_ENVIO or so_enviar_cli:
181:         enviar_whatsapp_menu()
182:         return
183: 
184:     while True:
185:         print("\n=== MAP SCRAPER ===")
186:         print("1 - Coletar leads")
187:         print("2 - Enviar mensagens WhatsApp")
188:         print("3 - Sincronizar base de localidades (IBGE)")
189:         print("4 - Aquecer bairros de uma UF (OpenStreetMap)")
190:         print("5 - Sair")
191:         opcao = input("Escolha uma opção: ").strip()
192: 
193:         if opcao == "1":
194:             coletar_leads()
195:         elif opcao == "2":
196:             enviar_whatsapp_menu()
197:         elif opcao == "3":
198:             sincronizar_base_localidades()
199:         elif opcao == "4":
200:             aquecer_bairros_menu()
201:         elif opcao == "5":
202:             print("Até mais!")
203:             break
204:         else:
205:             print("Opção inválida.")
206: 
207: 
208: if __name__ == "__main__":
209:     menu_interativo()
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
106:         O banco de dados será atualizado em data/leads.duckdb.
107: 
108:         Um arquivo Excel será gerado em output/leads_nicho_cidade.xlsx.
109: 
110: 
111: 6. Gerenciamento do Banco de Dados (Regras de Negócio)
112: 
113:     Se você quiser descartar um lead para que ele não seja mais exportado e não seja atualizado nas próximas buscas, você pode rodar um comando SQL direto no DuckDB (via DBeaver ou script Python):
114: 
115:     sql
116:     -- Para descartar um lead
117:     UPDATE leads SET status = 'descartado' WHERE nome = 'Nome da Barbearia';
118: 
119:     -- Para reativar um lead
120:     UPDATE leads SET status = 'ativo' WHERE nome = 'Nome da Barbearia';
121:     Nota: A regra do UPSERT no database.py garante que, se o robô achar uma barbearia "descartada", ele pula ela e não sobrescreve seus dados no banco.
122: 
123: 7. Envio de WhatsApp (WAHA)
124: 
125:     Pré-requisito: uma instância WAHA rodando com um número conectado via QR Code.
126: 
127:     Configuração (arquivo .env na raiz do projeto):
128:     Copie .env.example para .env e preencha os valores.
129: 
130:     ```
131:     WAHA_API_URL=http://localhost:3000
132:     WAHA_API_KEY=SUA_CHAVE_AQUI
133:     WAHA_SESSION=default
134:     WAHA_ATIVO=true
135:     SOMENTE_ENVIO=false
136:     WAHA_INTERVALO=13
137:     WAHA_LIMITE=
138:     ```
139: 
140:     Flags de comportamento:
141:     - WAHA_ATIVO: se false, desliga o envio de WhatsApp (não tenta enviar).
142:     - SOMENTE_ENVIO: se true, pula a coleta e vai direto para o envio
143:       (equivalente a rodar `python src/main.py --so-enviar`).
144:     - WAHA_LIMITE: quantidade máxima de leads por campanha (vazio = sem limite).
145: 
146:     Regras de envio (evita spam):
147:     - Só envia para leads com status = 'ativo'.
148:     - Só envia para tipo_telefone = 'Celular' (fixos são ignorados).
149:     - Só envia para leads ainda não enviados (status_whatsapp = 'pendente' ou NULL).
150:     - Intervalo de WAHA_INTERVALO segundos entre envios.
151: 
152:     Logs no banco:
153:     - status_whatsapp: 'pendente', 'enviado' ou 'falhou'.
154:     - data_envio_whatsapp: gravada apenas quando o envio é bem-sucedido.
155: 
156:     A mensagem pode usar as variáveis {nome}, {bairro} e {cidade}.
157: 
158: 
159: 8. Base de Localidades Offline (IBGE)
160: 
161:     O projeto mantém um cache local das localidades no próprio DuckDB, criado na
162:     primeira consulta e reaproveitado nas seguintes (sem rede).
163: 
164:     Tabelas criadas automaticamente (guardam apenas o essencial):
165:     - localidades_estados: uf, nome
166:     - localidades_municipios: id_municipio, nome, uf + estado da coleta de bairros
167:     - localidades_bairros: id_municipio, nome, id_distrito
168: 
169:     Fontes (API de Localidades do IBGE):
170:     - Estados:    https://servicodados.ibge.gov.br/api/v1/localidades/estados
171:     - Municípios: https://servicodados.ibge.gov.br/api/v1/localidades/municipios
172:     - Distritos:  https://servicodados.ibge.gov.br/api/v1/localidades/distritos
173: 
174:     Configuração (.env):
175:     ```
176:     LOCALIDADES_USAR_CACHE=true
177:     LOCALIDADES_SALVAR=true
178:     LOCALIDADES_MIN_BAIRROS=3
179:     AQUECER_PAUSA_SEGUNDOS=2
180:     ```
181: 
182:     - LOCALIDADES_USAR_CACHE=true (padrão): consulta o banco primeiro e só chama a
183:       API quando o dado ainda não existe (e aí grava o resultado).
184:     - LOCALIDADES_USAR_CACHE=false: sempre busca na API do IBGE e atualiza a base
185:       local com o que voltou.
186:     - LOCALIDADES_SALVAR=false: modo somente leitura. Nada é gravado e nem as
187:       tabelas são criadas; o banco só é consultado. A sincronização do menu fica
188:       desativada.
189:     - LOCALIDADES_MIN_BAIRROS: mínimo de distritos do IBGE para a cidade ser
190:       considerada coberta. Abaixo disso, os bairros são complementados com o
191:       OpenStreetMap (Nominatim + Overpass) e o resultado também fica em cache.
192:     - AQUECER_PAUSA_SEGUNDOS: pausa entre cidades no aquecimento por UF, aplicada
193:       somente quando a cidade usou o OpenStreetMap.
194: 
195:     As duas flags são independentes:
196: 
197:     | USAR_CACHE | SALVAR | Comportamento |
198:     |---|---|---|
199:     | true  | true  | lê do banco; grava o que faltar (recomendado) |
200:     | false | true  | sempre vai à API e regrava tudo (força atualização) |
201:     | true  | false | só lê o banco; o que não existe vai à API sem gravar |
202:     | false | false | sempre à API, sem tocar no banco |
203: 
204:     O que acontece ao rodar de novo para a mesma cidade:
205: 
206:     - localidades_estados: UPSERT por uf (só atualiza o nome).
207:     - localidades_municipios: UPSERT por id_municipio (atualiza nome/uf e
208:       PRESERVA bairros_fonte / bairros_atualizado_em).
209:     - localidades_bairros: a lista da cidade é tratada como autoritativa. Nomes
210:       iguais são atualizados, nomes novos são inseridos e nomes que não vieram mais
211:       são removidos — mas apenas daquela cidade.
212:     - Sincronização completa (menu opção 3): aditiva. Ela insere/atualiza os
213:       distritos do IBGE sem apagar bairros que já existem, então listas
214:       complementadas pelo OpenStreetMap são preservadas.
215: 
216:     Rodar só para um estado também é seguro: obter_cidades(uf) grava apenas os
217:     municípios daquela UF, e nada de outras UFs é alterado.
218: 
219:     Sincronização completa: menu opção 3 (ou `sincronizar_base_localidades()`), que
220:     baixa de uma vez todos os estados, municípios e distritos (~10,7 mil registros).
221: 
222:     Aquecimento por UF: menu opção 4 (ou `aquecer_bairros_uf('RS')`). Resolve e
223:     grava os bairros de TODAS as cidades de um estado, sem raspar nenhum lead.
224:     Depois disso, a coleta por cidade não consulta mais IBGE/OSM.
225: 
226:     - Processa apenas as cidades com `bairros_fonte IS NULL` (ou seja, retoma de
227:       onde parou em execuções anteriores).
228:     - Cidades cobertas pelo IBGE são instantâneas; as demais usam o OpenStreetMap.
229:     - A pausa entre cidades (AQUECER_PAUSA_SEGUNDOS) é aplicada somente quando o
230:       OSM foi consultado — respeitando o limite de 1 req/s do Nominatim.
231:     - Ctrl+C interrompe sem perder o que já foi gravado; basta rodar de novo.
232:     - É possível limitar quantas cidades processar por execução.
233: 
234:     Importante: os "distritos" do IBGE são divisões administrativas e, em muitos
235:     municípios, resumem-se à própria sede. Por isso o fallback com o OSM continua
236:     existindo — a diferença é que ele roda uma única vez por cidade e o resultado
237:     é gravado no banco. Se o OSM estiver fora do ar, nada é gravado (a próxima
238:     execução tenta de novo) e a coleta segue com os distritos do IBGE.
239: 
240:     A API de Localidades do IBGE NÃO fornece bairros — apenas distritos e
241:     subdistritos. Exemplo real: Canoas-RS tem 1 distrito (a própria sede) e 0
242:     subdistritos, então o IBGE não contribui com áreas para essa cidade e o robô
243:     informa isso e segue para o OpenStreetMap:
244: 
245:     ```
246:     IBGE não publica bairros para Canoas-RS: o município tem apenas 1 distrito (a sede).
247:     Buscando bairros no OpenStreetMap...
248:     ```
249: 
250:     Cidades com vários distritos (São Paulo: 96, Campinas: 7) usam o IBGE e não
251:     consultam o OSM. Das 5.571 cidades do país, 643 têm distritos suficientes.
252: 
253:     Como a cidade é resolvida: o nome digitado é comparado sem acento e sem
254:     diferenciar maiúsculas ("canoas", "sao leopoldo") com a lista do IBGE, e o nome
255:     oficial é exibido e usado no scraping, no banco e no Excel:
256: 
257:     ```
258:     Digite o nome da cidade: canoas
259:     Município (IBGE): Canoas-RS | código 4304606
260:     ```
261: 
262:     Para forçar a atualização de uma cidade já gravada, limpe a marca:
263:     ```sql
264:     UPDATE localidades_municipios SET bairros_fonte = NULL WHERE nome = 'Porto Alegre';
265:     ```
266: 
267: 9. Anti-bloqueio / Captcha (Google Maps)
268: 
269:     Quando o Google responde com a tela de "tráfego incomum" (captcha), o robô:
270:     1. detecta o bloqueio (URL /sorry/, formulários de captcha ou textos típicos);
271:     2. aplica um cooldown global, pausando TODAS as threads ao mesmo tempo;
272:     3. espera a pausa longa e tenta novamente até CAPTCHA_MAX_TENTATIVAS;
273:     4. se o bloqueio persistir, aborta apenas aquela área, preservando os leads
274:        já extraídos (que continuam sendo salvos incrementalmente).
275: 
276:     Configuração (.env):
277:     ```
278:     CAPTCHA_MAX_TENTATIVAS=2
279:     CAPTCHA_PAUSA_SEGUNDOS=300
280:     CAPTCHA_PAUSA_GLOBAL_SEGUNDOS=180
281:     ```
282: 
283:     - CAPTCHA_MAX_TENTATIVAS: tentativas por página antes de abortar a área.
284:     - CAPTCHA_PAUSA_SEGUNDOS: pausa longa da thread que levou o bloqueio.
285:     - CAPTCHA_PAUSA_GLOBAL_SEGUNDOS: pausa compartilhada entre as threads.
286: 
287:     A resolução automática de captcha por serviço externo (2Captcha, CapMonster
288:     etc.) não está implementada — o comportamento padrão é pausar e desistir da
289:     área em vez de insistir. Em coletas muito grandes, aumente as pausas acima.
290: 
291: 10. commit forçado
292: 
293:     git add -A; git commit -m "sync local $(Get-Date -Format 'yyyy-MM-dd HH:mm')"; git push --force-with-lease origin main
294: 
295: 11. Próximos Passos (Melhorias Futuras)
296: 
297:     Já implementado:
298:     - Base de localidades offline no DuckDB (estados, municípios e distritos do IBGE).
299:     - Detecção de captcha com pausa longa e cooldown compartilhado entre threads.
300: 
301:     Pendências sugeridas:
302:     - Resolução automática de captcha: integrar um serviço (2Captcha/CapMonster) para
303:       coletas muito grandes, hoje o robô apenas pausa e desiste da área.
304: 
305:     - Enriquecimento de E-mail: Criar um script secundário que lê os sites encontrados e busca e-mails de contato (usando Regex).
306: 
307: 
308: 12. Memória do Projeto para IA (pasta memory/)
309: 
310:     A pasta `memory/` reúne documentação resumida e densa, pensada para ser lida
311:     por modelos de IA antes de alterar o código (economiza contexto/custo).
312: 
313:     Ordem de leitura:
314:     1. memory/00-resumo-projeto.md        -> objetivo, stack e estrutura
315:     2. memory/01-arquitetura-e-modulos.md -> módulos, funções e fluxos
316:     3. memory/02-decisoes-e-armadilhas.md -> decisões, bugs conhecidos, cuidados
317:     4. memory/03-historico-de-mudancas.md -> o que mudou e o que ficou pendente
318:     5. memory/04-como-contribuir.md       -> padrões de código, logs, testes e docs
319: 
320:     Regras: manter os arquivos curtos, registrar o "porquê" das decisões e nunca
321:     colocar segredos ali (API keys ficam apenas no `.env`).
322: 
323: 
324: 13. Observação sobre configuração
325: 
326:     O modelo completo e comentado de todas as variáveis está em `.env.example`.
327:     Cada item traz a faixa de valores e o efeito colateral. Comentários devem
328:     ficar em linha própria; comentário na mesma linha do valor é lido como parte
329:     do valor.
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
