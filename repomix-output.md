This file is a merged representation of the entire codebase, combined into a single document by Repomix.

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
- Files are sorted by Git change count (files with more changes are at the bottom)

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
  README.md
output/
  teste.txt
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
repomix-output.xml
repomix.config.json
requirements.txt
````

# Files

## File: .repomixignore
````
# Add patterns to ignore here, one per line
# Example:
# *.log
# tmp/
````

## File: repomix-instrucao.md
````markdown
# Instruções para o Assistente de IA
Você é um desenvolvedor especialista trabalhando neste projeto de Map Scraper.
Por favor, processe todas as solicitações, explicações, comentários de código e interações estritamente em Português do Brasil (pt-BR).
````

## File: repomix-output.xml
````xml
This file is a merged representation of the entire codebase, combined into a single document by Repomix.

<file_summary>
This section contains a summary of this file.

<purpose>
This file contains a packed representation of the entire repository's contents.
It is designed to be easily consumable by AI systems for analysis, code review,
or other automated processes.
</purpose>

<file_format>
The content is organized as follows:
1. This summary section
2. Repository information
3. Directory structure
4. Repository files (if enabled)
5. Multiple file entries, each consisting of:
  - File path as an attribute
  - Full contents of the file
</file_format>

<usage_guidelines>
- This file should be treated as read-only. Any changes should be made to the
  original repository files, not this packed version.
- When processing this file, use the file path to distinguish
  between different files in the repository.
- Be aware that this file may contain sensitive information. Handle it with
  the same level of security as you would the original repository.

- Pay special attention to the Repository Instruction. These contain important context and guidelines specific to this project.
</usage_guidelines>

<notes>
- Some files may have been excluded based on .gitignore rules and Repomix's configuration
- Binary files are not included in this packed representation. Please refer to the Repository Structure section for a complete list of file paths, including binary files
- Files matching patterns in .gitignore are excluded
- Files matching default ignore patterns are excluded
- Files are sorted by Git change count (files with more changes are at the bottom)
</notes>

</file_summary>

<directory_structure>
data/
  leads.duckdb
memory/
  00-resumo-projeto.md
  01-arquitetura-e-modulos.md
  02-decisoes-e-armadilhas.md
  03-historico-de-mudancas.md
  04-como-contribuir.md
  README.md
output/
  teste.txt
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
README.md
repomix-instrucao.md
requirements.txt
</directory_structure>

<files>
This section contains the contents of the repository's files.

<file path="repomix-instrucao.md">
# Instruções para o Assistente de IA
Você é um desenvolvedor especialista trabalhando neste projeto de Map Scraper.
Por favor, processe todas as solicitações, explicações, comentários de código e interações estritamente em Português do Brasil (pt-BR).
</file>

<file path="memory/00-resumo-projeto.md">
# 00 — Resumo do Projeto

**Map Scraper** — ferramenta local de prospecção de leads B2B a partir do Google Maps.

- **Entrada:** UF + cidade + nicho (ex.: `RS`, `Canoas`, `barbearias`).
- **Processo:** divide a busca por bairros, raspa o Google Maps com Playwright em
  multithread e extrai nome, telefone, Instagram e site.
- **Saída:** leads no DuckDB (`data/leads.duckdb`) + Excel em `output/`.
- **Extra:** dispara mensagens de WhatsApp via WAHA para leads já coletados.

## Fluxo de alto nível

```
menu (src/main.py)
  └─ 1 Coletar    → locations.obter_termos_busca(cidade, uf)
                  → scraper.rodar_scraper_multithread(...)
                  → database.LeadDatabase.save_leads (UPSERT incremental)
                  → database.export_to_excel
  └─ 2 WhatsApp   → database.get_leads_para_envio
                  → whatsapp.disparar_campanha (WAHA)
  └─ 3 Sincronizar localidades (IBGE) → locations.sincronizar_base_localidades
  └─ 4 Aquecer bairros de uma UF       → locations.aquecer_bairros_uf
  └─ 5 Sair
```

## Stack

| Item | Tecnologia |
|---|---|
| Linguagem | Python 3.10+ (ambiente: `venv/`) |
| Scraping | Playwright (Chromium) + ThreadPoolExecutor |
| Banco | DuckDB (arquivo único, 1 processo por vez) |
| Dados | Pandas |
| Localidades | API IBGE + Nominatim/Overpass (OpenStreetMap) |
| WhatsApp | WAHA (WhatsApp HTTP API) |
| Config | `.env` carregado por `src/config.py` |

## Estrutura

```
map_scraper_project/
├── data/          leads.duckdb (+ .wal transiente, ignorado no Git)
├── memory/        esta documentação para IA
├── output/        Excel gerado (ignorado no Git)
├── src/
│   ├── config.py          loader do .env + helpers (bool/int)
│   ├── database.py        LeadDatabase: tabela leads, UPSERT, Excel, log WAHA
│   ├── localidades_db.py  cache IBGE em DuckDB (tabelas localidades_*)
│   ├── locations.py       IBGE + OSM + cache; sync e aquecimento por UF
│   ├── scraper.py         Playwright, multithread, anti-captcha
│   ├── utils.py           formatar_telefone → (telefone, tipo, link wa)
│   ├── whatsapp.py        envio via WAHA
│   └── main.py            menu interativo
├── .env / .env.example
├── requirements.txt
└── README.md
```

## Git — o que é versionado

| Versionado | Ignorado |
|---|---|
| `data/leads.duckdb` | `.env` (segredos) |
| `src/`, `memory/`, `README.md` | `*.duckdb.wal`, `*.duckdb.tmp` |
| `.env.example` | `*.xlsx`, `*.csv`, `*.log` |
| | `venv/`, `__pycache__/`, `sessions/` |

Comando de sync usado pelo mantenedor (sobrescreve o remoto):

```powershell
git add -A; git commit -m "sync local $(Get-Date -Format 'yyyy-MM-dd HH:mm')"; git push --force-with-lease origin main
```
</file>

<file path="memory/01-arquitetura-e-modulos.md">
# 01 — Arquitetura e Módulos

Todos os módulos usam imports absolutos (`from src.x import y`). `src/main.py`
adiciona a raiz do projeto ao `sys.path` antes de importar.

---

## src/config.py

Único ponto de leitura do `.env`. **Chame `carregar_env()` antes de calcular
constantes de módulo** (o import já executa uma vez).

```python
carregar_env(caminho=None)      # não sobrescreve variáveis já no ambiente
str_para_bool(valor, padrao)    # aceita 1/true/yes/s/sim/on
env_int(nome, padrao)           # inteiro com fallback
PROJETO_RAIZ, CAMINHO_ENV
```

> `src/whatsapp.py` chama `carregar_env()` no import (herança histórica).
> `src/locations.py` e `src/scraper.py` dependem disso para ler suas flags.

---

## src/localidades_db.py — cache de localidades

Acesso ao **mesmo** `data/leads.duckdb`. **Abre e fecha conexão a cada operação**,
para não segurar o arquivo durante o scraping (DuckDB permite só 1 processo).

Tabelas (criadas automaticamente quando `CRIAR_TABELAS = True`):

| Tabela | Colunas |
|---|---|
| `localidades_estados` | `uf` PK, `nome` |
| `localidades_municipios` | `id_municipio` PK, `nome`, `uf`, `bairros_fonte`, `bairros_atualizado_em` |
| `localidades_bairros` | `id_municipio`, `nome`, `id_distrito` — PK (`id_municipio`,`nome`) |

`bairros_fonte` ∈ {`ibge`, `overpass`, `cidade`, `NULL` (não coletado)}.

Funções:

```python
conexao(db_path=None)              # contextmanager; DDL se CRIAR_TABELAS
ler_estados() / salvar_estados(registros)
ler_municipios(uf)                 # inclui bairros_fonte (necessário p/ cache hit)
ler_municipios_pendentes(uf)       # bairros_fonte IS NULL
salvar_municipios(registros)       # UPSERT preserva bairros_fonte
buscar_municipio(cidade, uf)       # dict ou None
ler_bairros(id_municipio) / salvar_bairros(id_municipio, registros, fonte)
salvar_distritos_bulk(distritos, min_bairros=3)   # aditivo
estatisticas()                     # dict com contagens
CacheIndisponivel                  # exceção (arquivo travado / tabela ausente)
```

**Semânticas importantes**

- `salvar_bairros` é **autoritativo por cidade**: apaga nomes daquela cidade que
  não vieram na lista nova (não toca em outras cidades).
- `salvar_distritos_bulk` é **aditivo**: não apaga bairros do OSM já gravados.
- `salvar_municipios` é UPSERT e **preserva** `bairros_fonte`.

---

## src/locations.py — IBGE + OpenStreetMap + cache

Endpoints usados (`IBGE_API`):

```
/estados                         → UF (sigla, nome)
/estados/{uf}/municipios         → municípios da UF
/municipios                      → todos (usado na sync nacional)
/municipios/{id}/distritos       → distritos de uma cidade
/distritos                       → todos (sync nacional)
```

Flags do módulo (lidas do `.env`):

| Constante | Env | Default |
|---|---|---|
| `USAR_CACHE` | `LOCALIDADES_USAR_CACHE` | `true` |
| `SALVAR` | `LOCALIDADES_SALVAR` | `true` |
| `MIN_BAIRROS` | `LOCALIDADES_MIN_BAIRROS` | `3` |
| `AQUECER_PAUSA_PADRAO` | `AQUECER_PAUSA_SEGUNDOS` | `2` |

Helpers internos relevantes:

```python
_cache(fn, ...)   # executa no banco tolerando CacheIndisponivel (avisa 1x)
_salvar(fn, ...)  # respeita SALVAR=false (avisa 1x e retorna None)
_normalizar(t)    # minúsculas + sem acento
_municipios_da_uf(uf)   # memoizado em memória (evita rebaixar a lista)
```

API pública:

```python
obter_estados() -> DataFrame[uf, nome]
obter_cidades(uf) -> list[str]
obter_bairros(cidade, uf) -> list[str]        # [] = buscar cidade inteira
obter_termos_busca(cidade, uf, max_bairros=30) -> list[str]
obter_municipio(cidade, uf) -> dict|None      # nome oficial + id IBGE
filtrar_cidades(cidades, termo) -> list[str]  # sem acento/caixa
listar_municipios_pendentes(uf) -> list[dict]
aquecer_bairros_uf(uf, cidades=None, max_cidades=0, pausa_segundos=None) -> dict|None
sincronizar_base_localidades() -> bool        # nacional; bloqueada se SALVAR=false
```

### Resolução de bairros (`obter_bairros`)

1. Resolve o município (cache → lista da UF → grava se `SALVAR`).
2. Usa o **nome oficial** do IBGE daqui pra frente.
3. Se `USAR_CACHE` e `bairros_fonte` preenchido → lê `localidades_bairros`.
4. Senão:
   - baixa distritos do IBGE; descarta o distrito-sede (mesmo nome da cidade);
   - se `>= MIN_BAIRROS` → fonte `ibge`, **sem** chamar o OSM;
   - senão → Nominatim (bbox) + Overpass (`place=suburb|neighbourhood|quarter`,
     fallback `admin_level 9/10`);
   - se o OSM falhar (serviço fora) → **não grava** (`fonte=None`), tenta de novo
     na próxima execução.

---

## src/scraper.py — Playwright + anti-bloqueio

```python
extrair_leads_local(nicho, termo_busca, cidade, uf, mostrar_navegador=False) -> list[dict]
rodar_scraper_multithread(nicho, cidade, uf, termos_lista,
                          mostrar_navegador=False, save_callback=None) -> DataFrame
```

- `max_workers = min(3, len(termos_lista))`.
- `save_callback(df)` é chamado a cada área concluída (salvamento incremental).
- Deduplicação intra-execução por `(nome, cidade)`.
- Dict de lead: `nome, telefone, tipo_telefone, whatsapp_link, instagram, site,
  bairro, cidade, estado, nicho`.

Rolagem: `MAX_ROLAGENS = 40`, para após `MAX_RODADAS_ESTAGNADAS = 3` rodadas sem
crescimento.

Anti-captcha:

```python
BloqueioDetectado(termo)      # exceção
_pagina_bloqueada(page, checar_texto=True)
_marcar_bloqueio_global()     # cooldown compartilhado entre threads
_aguardar_cooldown(termo)     # todas as threads esperam
_navegar_com_retry(page, url, tentativas=3, timeout=..., termo=...)
```

Detecção: URL `/sorry/`, seletores de captcha (`#captcha-form`, reCAPTCHA,
hCaptcha) e textos como "unusual traffic" / "tráfego incomum".
Persistindo o bloqueio, **aborta só a área** e preserva os leads já extraídos.

Flags: `CAPTCHA_MAX_TENTATIVAS` (2), `CAPTCHA_PAUSA_SEGUNDOS` (300),
`CAPTCHA_PAUSA_GLOBAL_SEGUNDOS` (180).

---

## src/database.py — leads

`LeadDatabase(db_path="data/leads.duckdb")`

Tabela `leads` — PK (`nome`, `cidade`):

```
nome, telefone, tipo_telefone, whatsapp_link, instagram, site,
bairro, cidade, estado, nicho, status (default 'ativo'),
data_extracao, data_envio_whatsapp, status_whatsapp (default 'pendente')
```

```python
save_leads(df) -> int          # filtra descartados, UPSERT, não apaga log WAHA
get_leads_para_envio(limite)   # ativo + Celular + pendente
marcar_envio(nome, cidade, status_whatsapp)   # 'enviado' grava data
export_to_excel(nicho, cidade) # output/leads_{nicho}_{cidade}.xlsx
close()
```

---

## src/whatsapp.py — WAHA

```python
WAHA_API_URL, WAHA_API_KEY, WAHA_SESSION
WAHA_ATIVO, SOMENTE_ENVIO, WAHA_INTERVALO, WAHA_LIMITE
MENSAGEM_PADRAO
enviar_texto_waha(chat_id, texto, ...)   # POST /api/sendText
disparar_campanha(db, mensagem_template=None, intervalo=13, limite=None)
```

- `chat_id` = `55DDD9XXXXXXXX@c.us` (só 11 dígitos; fixo é rejeitado).
- Placeholders: `{nome}`, `{bairro}`, `{cidade}`.
- `SOMENTE_ENVIO=true` (ou `--so-enviar`) pula o menu e vai direto ao envio.

---

## src/main.py — menu

```
1 - Coletar leads
2 - Enviar mensagens WhatsApp
3 - Sincronizar base de localidades (IBGE)
4 - Aquecer bairros de uma UF (OpenStreetMap)
5 - Sair
```

`coletar_leads()`: UF → cidade (filtro sem acento) → **confirma no IBGE e usa o
nome oficial** → nicho → termos → "Ver navegador?" → scraping → Excel.
</file>

<file path="memory/02-decisoes-e-armadilhas.md">
# 02 — Decisões Técnicas e Armadilhas

Leia antes de mexer no código. Cada item já custou tempo de depuração.

---

## DuckDB: um processo por arquivo

**O arquivo `data/leads.duckdb` só pode ser aberto por UM processo.** Não existe
"read-only compartilhado" — até `duckdb.connect(..., read_only=True)` falha:

```
IO Error: Cannot open file "...data\leads.duckdb":
O arquivo já está sendo usado por outro processo.
```

Causas mais comuns: **DBeaver conectado**, scraper rodando, notebook aberto.

Consequências no código:
- `localidades_db.conexao()` abre/fecha a cada operação (não mantém aberto).
- `LeadDatabase` mantém aberto durante o scraping — **não** abra outra conexão
  persistente no mesmo processo.
- `CacheIndisponivel` existe para degradar com aviso em vez de quebrar:
  o sistema segue usando as APIs (IBGE/OSM) sem cache.

- ⚠️ **Um WAL pendente (`.wal`) indica dados não consolidados.** Se comitar o
  `.duckdb` com o programa aberto, o `.wal` (ignorado no Git) fica de fora e o
  commit sobe um estado desatualizado. Feche o programa antes de comitar.

---

## IBGE: não existe bairro na API de Localidades

A API retorna **estados, municípios, distritos e subdistritos**. Nada de bairro.

- `distritos` são divisões administrativas; em muitos municípios resumem-se à
  própria sede (mesmo nome da cidade).
- Exemplo real: **Canoas-RS = 1 distrito ("Canoas") e 0 subdistritos**.
- `obter_bairros` descarta o distrito-sede; se sobrarem `< MIN_BAIRROS`,
  complementa com OpenStreetMap.
- Cobertura: ~643 de 5.571 municípios têm distritos suficientes para dispensar OSM.

**Não "conserte" isso achando que é bug.** Para bairros oficiais existiria o
CNEFE 2022 (`ftp.ibge.gov.br/.../Censo_Demografico_2022/Arquivos_CNEFE/CSV/UF/`,
coluna `DSC_LOCALIDADE`, ex. `43_RS.zip` ≈ 236 MB) — **decisão do mantenedor:
não implementar por ora**, evoluir aos poucos.

---

## OpenStreetMap: instável por natureza

Os espelhos do Overpass e o Nominatim respondem `502`, `400` e `ReadTimeout`
com frequência. Regra de ouro:

> Falha de rede **não** significa "cidade sem bairros".

Por isso `_consultar_overpass` retorna `None` (serviço fora) em vez de
`{"elements": []}`, e `_descobrir_bairros` devolve `fonte=None` para **não
gravar** nada. A próxima execução tenta de novo. Se gravasse "cidade", o cache
ficaria envenenado para sempre.

---

## Cache: `bairros_fonte` precisa vir na leitura

Bug corrigido em 2026-10-29: `ler_municipios()` selecionava só
`id_municipio, nome`, então `_resolver_municipio` devolvia `bairros_fonte=None` e
`obter_bairros` **ia à API mesmo com cache quente**. Agora a query inclui
`uf` e `bairros_fonte`.

**Ao criar novas leituras de município, sempre inclua `bairros_fonte`.**

---

## Semântica de escrita (não inverter!)

| Função | Comportamento |
|---|---|
| `salvar_bairros` | **autoritativo** por cidade: remove nomes ausentes **daquela** cidade |
| `salvar_distritos_bulk` | **aditivo**: nunca apaga bairros do OSM |
| `salvar_municipios` | UPSERT — **preserva** `bairros_fonte`/`bairros_atualizado_em` |

Se `salvar_distritos_bulk` virasse autoritativo, destruiria as listas do
OpenStreetMap em toda sincronização.

---

## Flags `LOCALIDADES_*` são independentes

`USAR_CACHE` controla **leitura**; `SALVAR` controla **escrita**.

| USAR_CACHE | SALVAR | Efeito |
|---|---|---|
| true | true | padrão: lê do banco, grava o que faltar |
| false | true | ignora o banco, sempre API e regrava |
| true | false | lê do banco; o que falta vem da API sem gravar |
| false | false | sempre API, banco intocado |

- `SALVAR=false` também desativa a criação de tabelas (`CRIAR_TABELAS`) e os
  menus **3** e **4**.
- As flags são lidas **no import**: mudar o `.env` exige reiniciar o programa.
- Com `USAR_CACHE=false`, cada cidade baixa a lista da UF de novo (exceto pela
  memoização em memória `_municipios_da_uf`, válida só na execução atual).

---

## Cuidados ao editar arquivos (Windows/PowerShell)

- **Nunca** use `Get-Content ... -replace ... | Set-Content` para editar `.py`:
  ele reescreve em ANSI e **corrompe acentuação** (dupla codificação / mojibake).
  Use o editor (edit) ou grave via Python com `encoding="utf-8"`.
- Grave sempre **UTF-8 sem BOM** (BOM quebra a primeira chave do `.env`).
- Para testar, use o interpretador da venv: `venv\Scripts\python.exe`.
  O `python` global do mantenedor é 3.15 e pode não ter as dependências.
- Valide a acentuação após edições em lote: procure caracteres de dupla
  codificação (por exemplo, `A` com til U+00C3 seguido de símbolo de moeda).

---

## `.env` e Git

- `.env` **é ignorado** (contém `WAHA_API_KEY`). `.env.example` **é versionado**.
- Formato: `CHAVE=VALOR`. Comentários só em **linha própria** — comentário na
  mesma linha vira parte do valor (`WAHA_LIMITE= # vazio` → `" # vazio"`).
- Não use `export`/aspas desnecessárias; o loader tira aspas simples/duplas.
- Nunca imprima nem comite segredos.

---

## Scraping: seletores frágeis

Dependem do DOM do Google Maps (podem mudar sem aviso):

| Dado | Seletor |
|---|---|
| lista de resultados | `div[role="feed"]` |
| links de perfis | `a[href*="/maps/place/"]` |
| nome | `h1` (ignora "Resultados" e vazio) |
| endereço | `button[data-item-id="address"]` (`aria-label`) |
| telefone | `button[data-item-id^="phone:tel:"]` (`aria-label`) |
| site | `a[data-item-id="authority"]` |
| Instagram | primeiro `a[href]` contendo `instagram.com` |

Bairro é extraído do endereço: `"Rua X, 123 - Bairro, Cidade - UF"` → parte
entre `" - "` e `","`. Se não casar, `"Não Informado"`.

---

## Concorrência

- `save_callback` é chamado **na thread principal** (dentro do loop de
  `as_completed`), então não há escrita concorrente no DuckDB.
- O cooldown anti-captcha usa `_cooldown_lock` + variável global `_cooldown_ate`.
- `lock` protege a lista `vistos`/`todos_leads`.

---

## Coisas que parecem bug mas não são

- `"IBGE não publica bairros para X"` → cidade com 1 distrito (ver acima).
- `"Base local ... sem bairros (fonte: cidade)"` → já tentou, o OSM não tinha nada.
- `"LOCALIDADES_SALVAR=false: a base local não será alterada"` → modo leitura.
- `"Aviso: base local ... indisponível (arquivo em uso)"` → feche o DBeaver.
</file>

<file path="memory/04-como-contribuir.md">
# 04 — Como Contribuir: Padrões e Boas Práticas

Este documento detalha os padrões de código, estilo e comunicação esperados
para novas contribuições, visando manter a consistência e facilitar a manutenção.

---

## 1. Organização de Código e Nomenclatura

- **Imports:** Sempre absolutos, começando da raiz `src/`. Ex: `from src.config import ...`.
- **Constantes:** `MAIUSCULAS_COM_UNDERLINE`.
- **Funções privadas (internas ao módulo):** `_nome_da_funcao_privada` (com underscore inicial).
- **Variáveis locais:** `snake_case`.
- **Classes:** `CamelCase`.
- **Parâmetros de função:** `snake_case`.

---

## 2. Logs e Interação com o Usuário

- **Prints de progresso:** Use `print(f"[{area_da_busca}] Mensagem...")`.
  O `[área]` (ex: `[Canoas-RS]`, `[Assis Brasil]`) ajuda a identificar qual thread
  ou cidade está processando no momento.
- **Mensagens de erro:** Inclua `type(e).__name__` e `str(e)[:N]` para facilitar
  a depuração em ambientes remotos ou com logs limitados.
- **Interação:** Use `input()` para entradas do usuário no console. Evite `print()`
  seguido de `input()` em linhas separadas para prompts, a menos que seja intencional.
- **Mensagens para o usuário:** Devem ser claras e úteis, preferencialmente
  em português (padrão atual do projeto).

---

## 3. Variáveis de Ambiente e Configuração

- **Todas as configurações** devem ser lidas do `.env` via `src/config.py`.
- **Nunca faça hardcode** de URLs de APIs, chaves, limites, etc.
- **Novas variáveis:** Adicione ao `.env.example` com comentários explicativos.
- **Semântica:** Use `true`/`false` para booleanos, números para inteiros.
  O `src/config.py` já tem helpers para isso (`str_para_bool`, `env_int`).

---

## 4. Testes e Validação

- **Testes unitários/de integração:** Idealmente, adicione pequenos scripts de
  validação (como os que o modelo Gemini tem feito) para cobrir novas features
  ou refatorações.
- **DuckDB:** Para testes que não devem tocar no banco real, use um arquivo
  DuckDB temporário (`tempfile.gettempdir()`) e defina `localidades_db.DB_PATH_PADRAO`.
- **Encoding:** Mantenha os arquivos em **UTF-8 sem BOM**.
  Valide a acentuação após edições em lote: procure caracteres de dupla
  codificação (por exemplo, `A` com til U+00C3 seguido de símbolo de moeda).

---

## 5. Documentação

- **`README.md` (raiz):** Manual do usuário, instalação, execução, fluxo geral.
- **`memory/`:** Resumos densos para modelos de IA. **Atualize ao mudar comportamento**.
  - `00-resumo-projeto.md`: alto nível.
  - `01-arquitetura-e-modulos.md`: detalhe de cada módulo.
  - `02-decisoes-e-armadilhas.md`: o "porquê" das decisões, bugs conhecidos.
  - `03-historico-de-mudancas.md`: log recente das mudanças importantes.
- **Docstrings:** Use docstrings Python para explicar funções e classes.
- **Comentários de código:** Breves e pontuais, explicando lógica complexa ou escolhas não óbvias.
</file>

<file path="output/teste.txt">

</file>

<file path="src/__init__.py">

</file>

<file path="src/config.py">
# src/config.py
"""Carregamento centralizado do arquivo .env e leitura de flags.

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
</file>

<file path="src/utils.py">
# src/utils.py
import re

def formatar_telefone(telefone_bruto):
    """
    Limpa o telefone, identifica o tipo e gera o link do WhatsApp.
    Retorna: (telefone_limpo, tipo, whatsapp_link)
    """
    if not telefone_bruto:
        return "", "Não Informado", ""
    
    # Remove tudo que não for número
    apenas_numeros = re.sub(r'\D', '', str(telefone_bruto))
    
    # Se o número já vier com DDI (55) e tiver 12 ou 13 dígitos, removemos o 55 
    # temporariamente para classificar o tipo corretamente (Fixo/Celular)
    if apenas_numeros.startswith('55') and len(apenas_numeros) > 11:
        numero_sem_ddi = apenas_numeros[2:]
    else:
        numero_sem_ddi = apenas_numeros

    # Classificação e formatação do Link
    if len(numero_sem_ddi) == 11: # Celular com 9 dígito
        tipo = "Celular"
        whatsapp_link = f"https://wa.me/55{numero_sem_ddi}"
    elif len(numero_sem_ddi) == 10: # Fixo
        tipo = "Fixo"
        whatsapp_link = f"https://wa.me/55{numero_sem_ddi}"
    elif len(apenas_numeros) > 0:
        tipo = "Desconhecido"
        whatsapp_link = f"https://wa.me/{apenas_numeros}"
    else:
        return "", "Não Informado", ""
        
    # Retorna apenas os números na coluna telefone, o tipo e o link pronto
    return apenas_numeros, tipo, whatsapp_link
</file>

<file path=".gitkeep">

</file>

<file path="requirements.txt">
pandas
openpyxl
instagpy
pip-system-certs
playwright
chromium
geopy
duckdb
requests
</file>

<file path="memory/03-historico-de-mudancas.md">
# 03 — Histórico de Mudanças

Registro do que mudou, por quê e o que ficou pendente. Mais recente primeiro.

---

## 2026-10-29

### Memória do projeto para IA

- Criada a pasta `memory/` com documentação densa para reduzir custo de contexto.
- Arquivos: `README.md`, `00-resumo-projeto.md`, `01-arquitetura-e-modulos.md`,
  `02-decisoes-e-armadilhas.md`, `03-historico-de-mudancas.md`,
  `04-como-contribuir.md` (padrões de código, logs, config, testes e docs).
- `README.md` limpo: removido o bloco "env temp:" (dump cru do `.env`) e
  adicionadas as seções 12 (memória para IA) e 13 (observação sobre configuração).

### Correção: cache de bairros ignorado (`bairros_fonte`)

- **Sintoma:** com `LOCALIDADES_USAR_CACHE=true` e base populada, a coleta ainda
  consultava IBGE e Overpass.
- **Causa:** `localidades_db.ler_municipios()` não retornava `bairros_fonte`;
  `_resolver_municipio` repassava `None`, então o cache nunca era considerado.
- **Correção:** query passou a trazer `uf` e `bairros_fonte`; o resolver repassa
  o valor real.
- **Teste:** com as funções de rede trocadas por `AssertionError`, os bairros de
  Canoas (fonte `overpass`) e Bento Gonçalves (fonte `ibge`) vieram do banco.

### Nome oficial do município (IBGE) na coleta

- `obter_municipio(cidade, uf)` confirma o município e devolve `id_municipio`,
  `nome` oficial e `uf`.
- `filtrar_cidades(cidades, termo)` compara **sem acento e sem caixa**:
  `canoas`, `sao leopoldo`, `CHAPECO` funcionam.
- `main.coletar_leads()` passa a usar o nome oficial no scraping, no banco e no
  nome do Excel, e imprime `Município (IBGE): Canoas-RS | código 4304606`.
- Lista de municípios **memoizada** por execução (`_municipios_da_uf`), evitando
  rebaixar a lista da UF a cada cidade (principalmente com `SALVAR=false`).

### Mensagens de bairros mais honestas

- Antes: `IBGE retornou 0 distrito(s) útil(eis)`.
- Agora: `IBGE não publica bairros para Canoas-RS: o município tem apenas 1 distrito (a sede).`
- Motivo: a API de Localidades do IBGE **não tem bairros** (só distritos).

### Aquecimento de bairros por UF (menu 4)

- `locations.aquecer_bairros_uf(uf, cidades=None, max_cidades=0, pausa_segundos=None)`.
- `localidades_db.ler_municipios_pendentes(uf)` → só `bairros_fonte IS NULL`.
- Retoma de onde parou; `Ctrl+C` preserva o que já foi gravado.
- Pausa (`AQUECER_PAUSA_SEGUNDOS`, default 2) só quando a cidade usou o OSM.
- Falha de rede não grava nada (`falhas` no resumo) e a cidade continua pendente.
- Bloqueado quando `LOCALIDADES_SALVAR=false`.
- Medido: AC 21 → 18 → 17 pendentes; SP 621 → 616.

### Flag `LOCALIDADES_SALVAR`

- `false` = somente leitura: nenhuma escrita, **nem criação de tabelas**
  (`localidades_db.CRIAR_TABELAS = False`) e menus 3/4 desativados.
- Todas as escritas passam por `_salvar()`, que respeita a flag.
- Aviso único por execução para não poluir o log.

### `.env` e `.env.example` comentados

- Cada variável com explicação, faixa de valores e efeito colateral.
- Tabela das 4 combinações `USAR_CACHE × SALVAR`.
- Regra explícita: comentário só em linha própria.
- Valores locais preservados (`USAR_CACHE=false` → depois `true`).

### Base de localidades offline (IBGE) — menu 3

- Novo `src/localidades_db.py` com tabelas `localidades_estados`,
  `localidades_municipios`, `localidades_bairros` no mesmo `leads.duckdb`.
- `src/config.py` centraliza o loader do `.env` (antes duplicado no `whatsapp.py`).
- `src/locations.py` reescrito: cache → API → grava.
- Sync nacional: 27 estados, 5.571 municípios, 10.751 distritos; 643 cidades com
  bairros prontos pelo IBGE.
- Fallback OSM por cidade, gravado uma única vez.

### Anti-captcha / bloqueio do Google Maps

- Detecção por URL `/sorry/`, seletores de captcha e textos ("tráfego incomum").
- Retry com pausa longa (`CAPTCHA_PAUSA_SEGUNDOS`) e **cooldown global**
  (`CAPTCHA_PAUSA_GLOBAL_SEGUNDOS`) entre todas as threads.
- Bloqueio persistente → aborta a área e **preserva os leads já extraídos**.
- Testado com Playwright real: página normal passa, página de captcha levanta
  `BloqueioDetectado` após `CAPTCHA_MAX_TENTATIVAS`.

### Correção: menu não aparecia

- `src/main.py` definia `menu_interativo()` mas **nunca chamava**.
- Adicionado `if __name__ == "__main__": menu_interativo()`.

### Banco DuckDB versionado

- `data/leads.duckdb` passou a ser versionado no Git.
- `.gitignore`: removidos `data/` e `*.duckdb` da lista de ignore; adicionados
  `*.duckdb.wal` e `*.duckdb.tmp`.
- `*.xlsx`, `*.csv`, `*.log` continuam ignorados (confirmado com
  `git check-ignore` e `git ls-files`).
- ⚠️ Comitar com o programa aberto sobe o `.duckdb` sem o `.wal` (dados
  desatualizados). Fechar antes.

---

## Pendências / próximos passos

| Item | Status |
|---|---|
| Bairros oficiais via CNEFE 2022 | **Não implementar por ora** (decisão do mantenedor) |
| Resolução automática de captcha (2Captcha/CapMonster) | Não implementado; hoje pausa e desiste da área |
| Enriquecimento de e-mail a partir dos sites | Não iniciado |
| Base de bairros offline nacional | Coberto parcialmente pelo IBGE (643 cidades) |

## Problemas conhecidos (ambiente)

- **DBeaver aberto trava o DuckDB** → cache cai para as APIs.
- **Overpass/Nominatim instáveis** (502, timeout) → aquecimento por UF precisa de
  paciência e retomadas.
- Interprete global do mantenedor é Python 3.15; **usar `venv\Scripts\python.exe`**.
</file>

<file path="memory/README.md">
# memory/ — Memória do Projeto para IAs

Esta pasta contém documentação **resumida e densa** sobre o projeto Map Scraper,
escrita para ser lida por modelos de IA antes de alterar código.

## Por que existe

Ler esses arquivos curtos daqui custa muito menos tokens do que reler todo o código.
Use esta pasta como **primeira fonte de contexto**.

## Ordem de leitura recomendada

| # | Arquivo | Conteúdo |
|---|---|---|
| 1 | [00-resumo-projeto.md](./00-resumo-projeto.md) | O que o projeto faz, stack, estrutura |
| 2 | [01-arquitetura-e-modulos.md](./01-arquitetura-e-modulos.md) | Cada módulo, funções principais, fluxos |
| 3 | [02-decisoes-e-armadilhas.md](./02-decisoes-e-armadilhas.md) | Decisões técnicas, bugs conhecidos, cuidados |
| 4 | [03-historico-de-mudancas.md](./03-historico-de-mudancas.md) | O que mudou recentemente e por quê |
| 5 | [04-como-contribuir.md](./04-como-contribuir.md) | Padrões de código, logs, config, testes e documentação |

## Regras de manutenção

- **Atualize ao mudar comportamento**, não a cada commit.
- Mantenha cada arquivo curto (ideal: < 200 linhas). Detalhe fica no código.
- Registre o **porquê** das decisões, não só o quê.
- Nunca coloque segredos aqui (API keys, tokens). Use `.env`.
- Datas no formato `AAAA-MM-DD`.

## Arquivos que NÃO devem ser duplicados aqui

- `README.md` (raiz) — manual do usuário, instalação, uso.
- `.env.example` — valores e comentários de cada variável.
</file>

<file path="src/database.py">
# src/database.py
import duckdb
import pandas as pd
import os
from datetime import datetime

class LeadDatabase:
    def __init__(self, db_path="data/leads.duckdb"):
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        self.db_path = db_path
        self.conn = duckdb.connect(self.db_path)
        self._create_table()
        self._ensure_whatsapp_columns()

    def _create_table(self):
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS leads (
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
                PRIMARY KEY (nome, cidade)
            )
        """)

    def _ensure_whatsapp_columns(self):
        """Adiciona as colunas de log de WhatsApp em bancos criados antes da migração."""
        colunas = {row[1] for row in self.conn.execute("PRAGMA table_info(leads)").fetchall()}
        if 'data_envio_whatsapp' not in colunas:
            self.conn.execute("ALTER TABLE leads ADD COLUMN data_envio_whatsapp TIMESTAMP")
        if 'status_whatsapp' not in colunas:
            self.conn.execute("ALTER TABLE leads ADD COLUMN status_whatsapp VARCHAR DEFAULT 'pendente'")

    def save_leads(self, df: pd.DataFrame):
        if df.empty:
            return 0
        
        descartados_db = self.conn.execute("SELECT nome, cidade FROM leads WHERE status = 'descartado'").fetchall()
        descartados_set = set(descartados_db)
        
        df = df[~df.apply(lambda row: (row['nome'], row['cidade']) in descartados_set, axis=1)]
        
        if df.empty:
            print("Todos os leads coletados já foram descartados anteriormente. Pulando salvamento.")
            return 0
            
        df['data_extracao'] = datetime.now()
        
        if 'status' not in df.columns:
            df['status'] = 'ativo'

        self.conn.register('df_temp', df)

        # UPSERT preservando o status atual e as colunas de log do WhatsApp.
        # Assim, re-raspar um lead já enviado NÃO apaga data_envio_whatsapp/status_whatsapp.
        self.conn.execute("""
            INSERT INTO leads (nome, telefone, tipo_telefone, whatsapp_link, instagram, site, bairro, cidade, estado, nicho, status, data_extracao)
            SELECT nome, telefone, tipo_telefone, whatsapp_link, instagram, site, bairro, cidade, estado, nicho, status, data_extracao
            FROM df_temp
            ON CONFLICT (nome, cidade) DO UPDATE SET
                telefone = excluded.telefone,
                tipo_telefone = excluded.tipo_telefone,
                whatsapp_link = excluded.whatsapp_link,
                instagram = excluded.instagram,
                site = excluded.site,
                bairro = excluded.bairro,
                estado = excluded.estado,
                nicho = excluded.nicho,
                data_extracao = excluded.data_extracao
        """)

        self.conn.unregister('df_temp')
        return len(df)

    def get_leads_para_envio(self, limite=None):
        """Retorna leads ativos, celulares e ainda não enviados (evita spam/fixo)."""
        query = """
            SELECT nome, telefone, whatsapp_link, bairro, cidade, estado, nicho
            FROM leads
            WHERE status = 'ativo'
              AND tipo_telefone = 'Celular'
              AND (status_whatsapp IS NULL OR status_whatsapp = 'pendente')
            ORDER BY cidade, bairro, nome
        """
        if limite:
            query += f" LIMIT {int(limite)}"
        return self.conn.execute(query).df()

    def marcar_envio(self, nome, cidade, status_whatsapp):
        """Registra o resultado do envio. 'data_envio_whatsapp' é gravado apenas no sucesso."""
        if status_whatsapp == 'enviado':
            self.conn.execute("""
                UPDATE leads
                SET status_whatsapp = ?, data_envio_whatsapp = ?
                WHERE nome = ? AND cidade = ?
            """, [status_whatsapp, datetime.now(), nome, cidade])
        else:
            self.conn.execute("""
                UPDATE leads
                SET status_whatsapp = ?
                WHERE nome = ? AND cidade = ?
            """, [status_whatsapp, nome, cidade])

    def export_to_excel(self, nicho: str, cidade: str):
        df = self.conn.execute("""
            SELECT nome, telefone, tipo_telefone, whatsapp_link, instagram, site, bairro, data_extracao 
            FROM leads 
            WHERE nicho = ? AND cidade = ? AND status = 'ativo'
            ORDER BY bairro, nome
        """, [nicho, cidade]).df()
        
        if df.empty:
            print("Nenhum dado ativo para exportar.")
            return
            
        os.makedirs("output", exist_ok=True)
        nome_arquivo = f"output/leads_{nicho}_{cidade}.xlsx".replace(" ", "_").lower()
        df.to_excel(nome_arquivo, index=False)
        print(f"🎉 Exportação concluída: {nome_arquivo} ({len(df)} leads ativos)")

    def close(self):
        self.conn.close()
</file>

<file path="src/whatsapp.py">
# src/whatsapp.py
"""Integração com a WAHA (WhatsApp HTTP API) para envio de mensagens aos leads.

Configuração via variáveis de ambiente:
    WAHA_API_URL   -> URL base da WAHA (padrão: http://localhost:3000)
    WAHA_API_KEY   -> chave de API da WAHA (obrigatória se a instância exigir)
    WAHA_SESSION   -> nome da sessão conectada na WAHA (padrão: "default")

O módulo só envia para leads:
    - status = 'ativo'
    - tipo_telefone = 'Celular'  (nunca fixo)
    - ainda não enviados (status_whatsapp = 'pendente' ou NULL)
"""
import os
import re
import time

import requests

from src.config import carregar_env, str_para_bool

carregar_env()

WAHA_API_URL = os.environ.get("WAHA_API_URL", "http://localhost:3000")
WAHA_API_KEY = os.environ.get("WAHA_API_KEY", "")
WAHA_SESSION = os.environ.get("WAHA_SESSION", "default")

# Se false, o módulo NÃO tenta enviar (desliga o envio de WhatsApp).
WAHA_ATIVO = str_para_bool(os.environ.get("WAHA_ATIVO"), padrao=True)

# Se true, pula a coleta e vai direto para o envio (não coleta nada).
SOMENTE_ENVIO = str_para_bool(os.environ.get("SOMENTE_ENVIO"), padrao=False)

# Intervalo (segundos) entre envios e limite de leads por campanha.
# WAHA_LIMITE vazio = sem limite (envia todos os pendentes).
WAHA_INTERVALO = int(os.environ.get("WAHA_INTERVALO", "13"))
WAHA_LIMITE = os.environ.get("WAHA_LIMITE", "").strip()
WAHA_LIMITE = int(WAHA_LIMITE) if WAHA_LIMITE else None

# Mensagem padrão (placeholder). Use {nome}, {bairro} e {cidade}.
MENSAGEM_PADRAO = "Olá {nome}! Vi que vocês atendem no bairro {bairro}, em {cidade}. Podemos conversar?"


def _normalizar_chatid(telefone):
    """Converte o telefone salvo em um chatId do WAHA (55DDDNUMERO@c.us)."""
    numero = re.sub(r"\D", "", str(telefone or ""))
    if not numero:
        return None

    # Se veio com DDI 55 e tem mais de 11 dígitos, remove o prefixo.
    if numero.startswith("55") and len(numero) > 11:
        numero = numero[2:]

    # Celular brasileiro tem 11 dígitos (DDD + 9 dígitos).
    if len(numero) != 11:
        return None

    return f"55{numero}@c.us"


def _renderizar_mensagem(template, lead):
    """Substitui {nome}, {bairro} e {cidade} de forma segura (sem quebrar com chaves soltas)."""
    bairro = str(lead.get("bairro") or "sua região")
    cidade = str(lead.get("cidade") or "")
    return (
        template
        .replace("{nome}", str(lead.get("nome") or ""))
        .replace("{bairro}", bairro)
        .replace("{cidade}", cidade)
    )


def enviar_texto_waha(chat_id, texto, session=None, api_url=None, api_key=None):
    """Envia uma mensagem de texto via WAHA."""
    session = session or WAHA_SESSION
    api_url = api_url or WAHA_API_URL
    api_key = api_key if api_key is not None else WAHA_API_KEY
    url = f"{api_url.rstrip('/')}/api/sendText"

    payload = {
        "session": session,
        "chatId": chat_id,
        "text": texto,
    }

    headers = {"Accept": "application/json", "Content-Type": "application/json"}
    if api_key:
        headers["X-Api-Key"] = api_key

    response = requests.post(url, json=payload, headers=headers, timeout=30)
    response.raise_for_status()
    return response.json()


def disparar_campanha(db, mensagem_template=None, intervalo=13, limite=None):
    """Envia mensagens para todos os leads celulares pendentes.

    - db: instância de LeadDatabase
    - mensagem_template: texto com {nome}, {bairro}, {cidade} (usa MENSAGEM_PADRAO se None)
    - intervalo: pausa em segundos entre envios (evita spam e banimento)
    """
    mensagem_template = mensagem_template or MENSAGEM_PADRAO
    leads = db.get_leads_para_envio(limite)

    if leads.empty:
        print("Nenhum lead celular pendente de envio.")
        return

    total = len(leads)
    print(f"Enviando para {total} lead(s) celular(es), com intervalo de {intervalo}s...")

    for i, (_, lead) in enumerate(leads.iterrows(), 1):
        chat_id = _normalizar_chatid(lead.get("telefone"))
        if not chat_id:
            db.marcar_envio(lead["nome"], lead["cidade"], "falhou")
            print(f"[{i}/{total}] {lead['nome']} - telefone inválido, marcado como falhou.")
            continue

        texto = _renderizar_mensagem(mensagem_template, lead)

        try:
            enviar_texto_waha(chat_id, texto)
            db.marcar_envio(lead["nome"], lead["cidade"], "enviado")
            print(f"[{i}/{total}] ENVIADO -> {lead['nome']} ({chat_id})")
        except Exception as e:
            db.marcar_envio(lead["nome"], lead["cidade"], "falhou")
            print(f"[{i}/{total}] FALHOU -> {lead['nome']} ({chat_id}): {e}")

        if i < total:
            time.sleep(intervalo)

    print("Campanha finalizada.")
</file>

<file path="src/localidades_db.py">
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
</file>

<file path=".env.example">
# =============================================================================
# MAP SCRAPER - arquivo de exemplo de configuração
# -----------------------------------------------------------------------------
# Copie para `.env` e ajuste:
#     Copy-Item .env.example .env
#
# REGRAS IMPORTANTES
#  - Formato: CHAVE=VALOR, uma por linha.
#  - Comentários (linhas que começam com #) podem ficar à vontade, mas SEMPRE em
#    linha própria. Não coloque comentário na mesma linha do valor, porque ele
#    seria lido como parte do valor.
#  - true/false: também aceita 1/0, sim/não, s/yes/on.
#  - O arquivo `.env` NÃO é versionado no Git (contém a API key da WAHA).
# =============================================================================


# =============================================================================
# WHATSAPP - WAHA (WhatsApp HTTP API)
# =============================================================================

# URL base da sua instância WAHA (Docker local, por exemplo).
# Usada em todas as chamadas de envio. Não coloque a barra final.
WAHA_API_URL=http://localhost:3000

# Chave de API da WAHA. É o valor de WHATSAPP_API_KEY no .env do Docker/init-waha.
# Deixe vazio se a sua instância estiver sem autenticação.
WAHA_API_KEY=

# Nome da sessão do WhatsApp já conectada (lida por QR Code), normalmente `default`.
# Precisa ser exatamente o nome que aparece em /api/sessions da WAHA.
WAHA_SESSION=default

# Liga/desliga TODO o envio de WhatsApp.
#   true  = o menu "2 - Enviar mensagens WhatsApp" funciona normalmente.
#   false = o menu avisa que o envio está desativado e não faz nada.
# Isso NÃO afeta a coleta de leads, apenas o disparo de mensagens.
WAHA_ATIVO=true

# Atalho que pula o menu e vai direto para o envio, sem coletar nada.
#   true  = equivale a rodar: python src/main.py --so-enviar
#   false = abre o menu normal (coleta + envio).
# Útil para rodar uma campanha agendada, por exemplo.
SOMENTE_ENVIO=false

# Pausa em SEGUNDOS entre um envio e o próximo (13s ≈ 4-5 mensagens por minuto).
# Pausas muito curtas aumentam o risco de banimento do número.
WAHA_INTERVALO=13

# Quantidade máxima de leads por campanha. Vazio = sem limite (envia todos
# os pendentes). Só conta leads celulares, ativos e ainda não enviados.
WAHA_LIMITE=


# =============================================================================
# BASE DE LOCALIDADES (IBGE) - cache em DuckDB: tabelas localidades_*
# -----------------------------------------------------------------------------
# As duas flags abaixo são independentes. Combinações possíveis:
#
#   USAR_CACHE  SALVAR   O que acontece
#   true        true     usa o banco; só vai à API do que falta e grava (padrão)
#   false       true     ignora o banco, sempre vai à API e regrava (força refresh)
#   true        false    usa o banco; o que falta vai à API mas NÃO é gravado
#   false       false    sempre API, e o banco nunca é tocado (somente leitura)
# =============================================================================

# Consultar a base local ANTES da API do IBGE?
#   true  = se o dado já existe no DuckDB, nem chama a internet (rápido).
#   false = sempre chama a API do IBGE, mesmo que o dado já esteja no banco.
LOCALIDADES_USAR_CACHE=true

# Permitir GRAVAR na base local?
#   true  = pode inserir/atualizar (UPSERT) os estados, municípios e bairros.
#   false = modo somente leitura: nada é gravado e nem as tabelas são criadas.
# ATENÇÃO: com false, os menus "3 - Sincronizar" e "4 - Aquecer bairros" ficam
# desativados, e cada execução consulta as APIs de novo.
LOCALIDADES_SALVAR=true

# Mínimo de distritos do IBGE para considerar a cidade "coberta" pelo IBGE.
# A API de Localidades do IBGE tem distritos (não bairros). Cidade com menos
# distritos que este número é complementada com o OpenStreetMap.
# Exemplo: Campinas-SP tem 7 distritos -> usa só o IBGE.
#          Canoas-RS tem 1 distrito (a sede) -> vai para o OpenStreetMap.
LOCALIDADES_MIN_BAIRROS=3

# Pausa em SEGUNDOS entre cidades no menu "4 - Aquecer bairros de uma UF".
# Só é aplicada quando a cidade precisou do OpenStreetMap (Nominatim permite
# ~1 requisição por segundo). Cidades resolvidas pelo IBGE não esperam.
AQUECER_PAUSA_SEGUNDOS=2


# =============================================================================
# GOOGLE MAPS - captcha / bloqueio ("tráfego incomum")
# -----------------------------------------------------------------------------
# Quando o Google bloqueia, o robô pausa e tenta de novo. Se continuar bloqueado,
# ele aborta APENAS aquela área e mantém os leads já coletados.
# =============================================================================

# Quantas tentativas por página antes de desistir da área.
#   1  = não tenta de novo, só pausa uma vez e desiste.
#   2  = pausa e tenta mais uma vez (padrão).
# Valores altos aumentam o risco de piorar o bloqueio.
CAPTCHA_MAX_TENTATIVAS=2

# Pausa longa em SEGUNDOS feita pela thread que recebeu o captcha antes de
# tentar a mesma página novamente.
CAPTCHA_PAUSA_SEGUNDOS=300

# Pausa compartilhada em SEGUNDOS aplicada a TODAS as threads assim que uma
# delas detecta bloqueio (evita que as outras continuem martelando o Google).
CAPTCHA_PAUSA_GLOBAL_SEGUNDOS=180
</file>

<file path="src/scraper.py">
# src/scraper.py
from playwright.sync_api import sync_playwright
import time
import random
import urllib.parse
from concurrent.futures import ThreadPoolExecutor, as_completed
import pandas as pd
import threading
from src.config import env_int
from src.utils import formatar_telefone

lock = threading.Lock()

USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/124.0.0.0 Safari/537.36"
)

MAX_ROLAGENS = 40
MAX_RODADAS_ESTAGNADAS = 3

# --- Anti-bloqueio (captcha) -------------------------------------------------
# CAPTCHA_MAX_TENTATIVAS: quantas vezes uma mesma página é tentada antes de
#   abortar a área (1 = nem tenta de novo, só pausa e desiste).
# CAPTCHA_PAUSA_SEGUNDOS: pausa longa feita pela thread que levou o bloqueio.
# CAPTCHA_PAUSA_GLOBAL_SEGUNDOS: pausa compartilhada, aplicada a TODAS as
#   threads assim que uma delas detecta bloqueio (evita que as outras insistam).
CAPTCHA_MAX_TENTATIVAS = max(1, env_int("CAPTCHA_MAX_TENTATIVAS", 2))
CAPTCHA_PAUSA_SEGUNDOS = max(0, env_int("CAPTCHA_PAUSA_SEGUNDOS", 300))
CAPTCHA_PAUSA_GLOBAL_SEGUNDOS = max(0, env_int("CAPTCHA_PAUSA_GLOBAL_SEGUNDOS", 180))

_MARCADORES_CAPTCHA = (
    "unusual traffic",
    "tráfego incomum",
    "trafego incomum",
    "não é possível acessar",
    "nao e possivel acessar",
    "our systems have detected",
    "digite os caracteres",
    "não sou um robô",
    "i'm not a robot",
)

_SELETORES_BLOQUEIO = (
    'form[action*="sorry"]',
    "#captcha-form",
    "#recaptcha",
    ".g-recaptcha",
    'iframe[src*="recaptcha"]',
    'iframe[src*="hcaptcha"]',
)

_cooldown_ate = 0.0
_cooldown_lock = threading.Lock()


class BloqueioDetectado(Exception):
    """Google Maps devolveu captcha/tela de bloqueio para a busca atual."""


def _montar_query(nicho, termo_busca, cidade, uf):
    if termo_busca.strip().lower() == cidade.strip().lower():
        return f"{nicho} em {cidade}, {uf}"
    return f"{nicho} em {termo_busca}, {cidade}, {uf}"


def _pagina_bloqueada(page, checar_texto=True):
    """Detecta captcha / tela de 'tráfego incomum' do Google."""
    try:
        url = (page.url or "").lower()
    except Exception:
        return False
    if "/sorry/" in url:
        return True

    try:
        for seletor in _SELETORES_BLOQUEIO:
            if page.query_selector(seletor):
                return True
    except Exception:
        return False

    if not checar_texto:
        return False

    try:
        texto = (page.inner_text("body") or "")[:4000].lower()
    except Exception:
        return False
    return any(marcador in texto for marcador in _MARCADORES_CAPTCHA)


def _marcar_bloqueio_global():
    """Coloca todas as threads em pausa (cooldown compartilhado)."""
    global _cooldown_ate
    if CAPTCHA_PAUSA_GLOBAL_SEGUNDOS <= 0:
        return
    with _cooldown_lock:
        _cooldown_ate = max(_cooldown_ate, time.time() + CAPTCHA_PAUSA_GLOBAL_SEGUNDOS)


def _aguardar_cooldown(termo):
    """Espera o cooldown global, se alguma thread detectou bloqueio."""
    with _cooldown_lock:
        restante = _cooldown_ate - time.time()
    if restante <= 0:
        return

    print(f"[{termo}] Pausa global anti-bloqueio: aguardando {int(restante) + 1}s...")
    while restante > 0:
        time.sleep(min(restante, 10))
        with _cooldown_lock:
            restante = _cooldown_ate - time.time()


def _pausar_com_aviso(segundos, termo):
    print(f"[{termo}] Aguardando {segundos}s (pausa longa anti-bloqueio)...")
    restante = segundos
    while restante > 0:
        passo = min(restante, 15)
        time.sleep(passo)
        restante -= passo


def _navegar_com_retry(page, url, tentativas=3, timeout=30000, termo="?"):
    """Navega com retry e backoff; detecta captcha e aplica pausa longa.

    Levanta BloqueioDetectado quando o bloqueio persiste após as tentativas.
    """
    for tentativa in range(1, tentativas + 1):
        _aguardar_cooldown(termo)
        try:
            page.goto(url, timeout=timeout)
        except Exception as e:
            print(f"  Retry {tentativa}/{tentativas} ao navegar para {url}: {type(e).__name__}")
            time.sleep(2 * tentativa)
            continue

        if not _pagina_bloqueada(page):
            return True

        _marcar_bloqueio_global()
        print(f"[{termo}] ⚠ Google Maps bloqueou o acesso (captcha/tráfego incomum).")

        if tentativa >= min(tentativas, CAPTCHA_MAX_TENTATIVAS):
            print(f"[{termo}] Bloqueio persistente após {tentativa} tentativa(s). Abortando esta área.")
            raise BloqueioDetectado(termo)

        _pausar_com_aviso(CAPTCHA_PAUSA_SEGUNDOS, termo)

    return False


def _obter_urls_perfis(page):
    urls = set()
    for link in page.query_selector_all('a[href*="/maps/place/"]'):
        href = link.get_attribute('href')
        if href:
            urls.add(href)
    return urls


def _rolar_resultados(page, termo="?"):
    """Rola a lista até esgotar os resultados (ou atingir o limite de rolagens)."""
    ultimo_total = 0
    rodadas_estagnadas = 0
    for _ in range(MAX_ROLAGENS):
        if _pagina_bloqueada(page, checar_texto=False):
            _marcar_bloqueio_global()
            raise BloqueioDetectado(termo)

        total = len(_obter_urls_perfis(page))
        page.evaluate('''() => {
            const feed = document.querySelector('div[role="feed"]');
            if(feed) feed.scrollTop = feed.scrollHeight;
        }''')
        time.sleep(1.0 + random.uniform(0, 0.6))  # jitter anti-bloqueio

        if total == ultimo_total:
            rodadas_estagnadas += 1
            if rodadas_estagnadas >= MAX_RODADAS_ESTAGNADAS:
                break
        else:
            rodadas_estagnadas = 0
        ultimo_total = total


def extrair_leads_local(nicho, termo_busca, cidade, uf, mostrar_navegador=False):
    query = _montar_query(nicho, termo_busca, cidade, uf)
    url = f"https://www.google.com/maps/search/{urllib.parse.quote(query)}"
    leads = []

    p = sync_playwright().start()
    browser = None
    try:
        browser = p.chromium.launch(headless=not mostrar_navegador)
        context = browser.new_context(
            user_agent=USER_AGENT,
            viewport={"width": 1366, "height": 768},
            locale="pt-BR",
        )
        page = context.new_page()

        if not _navegar_com_retry(page, url, timeout=60000, termo=termo_busca):
            print(f"[{termo_busca}] Falha ao carregar a busca.")
            return leads

        try:
            page.wait_for_selector('div[role="feed"]', timeout=10000)
        except Exception:
            print(f"[{termo_busca}] Nenhum resultado encontrado.")
            return leads

        print(f"[{termo_busca}] Rolando resultados...")
        _rolar_resultados(page, termo_busca)

        if _pagina_bloqueada(page):
            _marcar_bloqueio_global()
            raise BloqueioDetectado(termo_busca)

        urls = sorted(_obter_urls_perfis(page))
        print(f"[{termo_busca}] {len(urls)} perfis encontrados. Extraindo dados...")

        for i, place_url in enumerate(urls):
            try:
                time.sleep(random.uniform(0.8, 2.5))  # pausa anti-bloqueio entre navegações
                if not _navegar_com_retry(page, place_url, timeout=30000, termo=termo_busca):
                    continue
                time.sleep(random.uniform(1.2, 2.8))

                nome_elem = page.query_selector('h1')
                nome = nome_elem.inner_text() if nome_elem else "Sem nome"
                if nome in ("Resultados", ""):
                    continue

                # Extração do Bairro (Endereço)
                bairro_real = "Não Informado"
                endereco_elem = page.query_selector('button[data-item-id="address"]')
                if endereco_elem:
                    aria_endereco = endereco_elem.get_attribute('aria-label')
                    if aria_endereco:
                        texto_limpo = aria_endereco.replace('Endereço:', '').replace('Address:', '').strip()
                        try:
                            parts = texto_limpo.split(" - ")
                            if len(parts) >= 2:
                                bairro_real = parts[1].split(",")[0].strip()
                        except Exception:
                            pass

                # Extração do Telefone
                telefone_bruto = ""
                tel_elem = page.query_selector('button[data-item-id^="phone:tel:"]')
                if tel_elem:
                    aria = tel_elem.get_attribute('aria-label')
                    if aria:
                        telefone_bruto = aria.replace('Telefone:', '').replace('Phone:', '').strip()

                telefone_limpo, tipo_telefone, whatsapp_link = formatar_telefone(telefone_bruto)

                link_site = ""
                link_insta = ""

                site_elem = page.query_selector('a[data-item-id="authority"]')
                if site_elem:
                    link_site = site_elem.get_attribute('href')

                for a in page.query_selector_all('a'):
                    href = a.get_attribute('href')
                    if href and "instagram.com" in href:
                        link_insta = href
                        break

                leads.append({
                    'nome': nome,
                    'telefone': telefone_limpo,
                    'tipo_telefone': tipo_telefone,
                    'whatsapp_link': whatsapp_link,
                    'instagram': link_insta,
                    'site': link_site,
                    'bairro': bairro_real,
                    'cidade': cidade,
                    'estado': uf,
                    'nicho': nicho
                })
                print(f"[{termo_busca}] {i+1}/{len(urls)} - {nome} | {tipo_telefone} | {telefone_limpo}")

            except BloqueioDetectado:
                raise
            except Exception as e:
                print(f"[{termo_busca}] Erro ao extrair {place_url}: {e}")

    except BloqueioDetectado:
        print(f"[{termo_busca}] Área interrompida por bloqueio do Google Maps "
              f"({len(leads)} lead(s) preservado(s)).")
    finally:
        if browser:
            browser.close()
        p.stop()

    return leads


def rodar_scraper_multithread(nicho, cidade, uf, termos_lista, mostrar_navegador=False, save_callback=None):
    """
    Executa a coleta em multithread. Se save_callback for informado, cada lote
    (por área) é salvo assim que termina, evitando perder a coleta em caso de falha.
    """
    todos_leads = []
    vistos = set()
    max_workers = min(3, len(termos_lista))
    print(f"Iniciando scraper com {max_workers} threads em {len(termos_lista)} área(s)...")

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futuros = {
            executor.submit(extrair_leads_local, nicho, termo, cidade, uf, mostrar_navegador): termo
            for termo in termos_lista
        }

        for futuro in as_completed(futuros):
            termo = futuros[futuro]
            try:
                leads_area = futuro.result()
                with lock:
                    novos = []
                    for lead in leads_area:
                        chave = (lead['nome'], lead['cidade'])
                        if chave not in vistos:
                            vistos.add(chave)
                            novos.append(lead)
                    todos_leads.extend(novos)

                if novos and save_callback:
                    save_callback(pd.DataFrame(novos))

                print(f"[{termo}] Finalizado. {len(novos)} leads novos (acumulado: {len(todos_leads)}).")
            except Exception as e:
                print(f"Erro na busca {termo}: {e}")

    return pd.DataFrame(todos_leads)
</file>

<file path="src/locations.py">
# src/locations.py
"""Localidades (UF, cidade e bairros) com cache local em DuckDB.

Fonte oficial: API de Localidades do IBGE.
    estados    -> /api/v1/localidades/estados
    municipios -> /api/v1/localidades/municipios
    distritos  -> /api/v1/localidades/distritos

Com LOCALIDADES_USAR_CACHE=true (padrão), a base local é consultada primeiro;
só vai para a rede o que ainda não existe no banco. Com a flag false, os dados
são sempre buscados na API (e a base local é atualizada com o resultado).

Observação: os "distritos" do IBGE são divisões administrativas e, em muitos
municípios, resumem-se à própria sede. Quando não há distritos suficientes,
a lista é complementada com bairros do OpenStreetMap (Nominatim + Overpass).
"""
import os
import time
import unicodedata

import pandas as pd
import requests

from src import localidades_db
from src.config import env_int, str_para_bool

IBGE_API = "https://servicodados.ibge.gov.br/api/v1/localidades"

# User-Agent identificável é exigido pela política de uso do Nominatim.
HEADERS = {"User-Agent": "map-scraper-lead-prospecting/1.0 (prospeccao.mapscraper@gmail.com)"}

OVERPASS_ENDPOINTS = [
    "https://overpass-api.de/api/interpreter",
    "https://overpass.private.coffee/api/interpreter",
    "https://overpass.osm.ch/api/interpreter",
    "https://overpass.kumi.systems/api/interpreter",
]

# Se true: consulta o banco antes da API. Se false: sempre busca na API.
USAR_CACHE = str_para_bool(os.environ.get("LOCALIDADES_USAR_CACHE"), padrao=True)

# Se false: NUNCA grava na base local (nem cria tabelas). Funciona como
# "somente leitura": o banco é consultado, mas nada é alterado.
SALVAR = str_para_bool(os.environ.get("LOCALIDADES_SALVAR"), padrao=True)

# Reflete a flag no módulo de acesso ao banco (controla a criação das tabelas).
localidades_db.CRIAR_TABELAS = SALVAR

# Quantidade mínima de distritos úteis para não precisar do OpenStreetMap.
# Abaixo disso, a cidade é complementada com bairros do OSM.
MIN_BAIRROS = max(1, env_int("LOCALIDADES_MIN_BAIRROS", 3))

# Pausa (segundos) entre cidades no aquecimento por UF, aplicada apenas quando o
# OpenStreetMap foi consultado (política de uso do Nominatim: 1 req/s).
AQUECER_PAUSA_PADRAO = max(0, env_int("AQUECER_PAUSA_SEGUNDOS", 2))

_avisou_cache_indisponivel = False
_avisou_sem_gravacao = False


def _cache(funcao, *args, **kwargs):
    """Executa uma operação na base local, tolerando banco travado/indisponível."""
    global _avisou_cache_indisponivel
    try:
        return funcao(*args, **kwargs)
    except localidades_db.CacheIndisponivel as e:
        if not _avisou_cache_indisponivel:
            print(f"  Aviso: base local de localidades indisponível ({e}).")
            print("         Seguindo apenas com as APIs (IBGE/OSM).")
            _avisou_cache_indisponivel = True
        return None


def _salvar(funcao, *args, **kwargs):
    """Grava na base local, respeitando LOCALIDADES_SALVAR=false."""
    global _avisou_sem_gravacao
    if not SALVAR:
        if not _avisou_sem_gravacao:
            print("  LOCALIDADES_SALVAR=false: a base local não será alterada.")
            _avisou_sem_gravacao = True
        return None
    return _cache(funcao, *args, **kwargs)


# ---------------------------------------------------------------------------
# IBGE
# ---------------------------------------------------------------------------
def _get_json(url, params=None, timeout=60, tentativas=3):
    for tentativa in range(1, tentativas + 1):
        try:
            resposta = requests.get(url, params=params, timeout=timeout, headers=HEADERS)
            resposta.raise_for_status()
            return resposta.json()
        except Exception as e:
            print(f"  IBGE indisponível (tentativa {tentativa}/{tentativas}): {type(e).__name__}")
            if tentativa < tentativas:
                time.sleep(1.5 * tentativa)
    return None


def _baixar_estados():
    dados = _get_json(f"{IBGE_API}/estados", params={"orderBy": "nome"}, timeout=30)
    if not dados:
        return None
    return [{"uf": e["sigla"], "nome": e["nome"]} for e in dados]


def _uf_do_municipio(municipio):
    try:
        return municipio["microrregiao"]["mesorregiao"]["UF"]["sigla"]
    except (KeyError, TypeError):
        try:
            return municipio["regiao-imediata"]["regiao-intermediaria"]["UF"]["sigla"]
        except (KeyError, TypeError):
            return None


def _baixar_municipios(uf=None):
    url = f"{IBGE_API}/estados/{uf}/municipios" if uf else f"{IBGE_API}/municipios"
    dados = _get_json(url, params={"orderBy": "nome"})
    if not dados:
        return None

    registros = []
    for municipio in dados:
        sigla = uf or _uf_do_municipio(municipio)
        if not sigla:
            continue
        registros.append({
            "id_municipio": municipio["id"],
            "nome": municipio["nome"],
            "uf": sigla,
        })
    return registros


def _baixar_distritos(id_municipio=None):
    url = (f"{IBGE_API}/municipios/{id_municipio}/distritos"
           if id_municipio else f"{IBGE_API}/distritos")
    dados = _get_json(url)
    if not dados:
        return None

    registros = []
    for distrito in dados:
        municipio = distrito.get("municipio") or {}
        registros.append({
            "id_distrito": distrito.get("id"),
            "nome": (distrito.get("nome") or "").strip(),
            "id_municipio": municipio.get("id"),
        })
    return [r for r in registros if r["id_municipio"] and r["nome"]]


_municipios_memoria = {}


def _municipios_da_uf(uf):
    """Lista de municípios da UF, memorizada na execução para não baixar duas vezes."""
    if uf not in _municipios_memoria:
        print(f"  Baixando a lista de municípios de {uf} do IBGE...")
        municipios = _baixar_municipios(uf)
        if municipios is None:
            return None
        _municipios_memoria[uf] = municipios
    return _municipios_memoria[uf]


# ---------------------------------------------------------------------------
# OpenStreetMap (fallback de bairros)
# ---------------------------------------------------------------------------
def _obter_bbox_cidade(cidade, uf):
    """Retorna (sul, norte, oeste, leste) da cidade via Nominatim."""
    url = "https://nominatim.openstreetmap.org/search"
    params = {"format": "json", "q": f"{cidade}, {uf}, Brazil", "limit": 1}
    try:
        resposta = requests.get(url, params=params, timeout=15, headers=HEADERS)
        resposta.raise_for_status()
        resultados = resposta.json()
        if not resultados:
            return None
        bb = resultados[0].get("boundingbox")
        if not bb or len(bb) != 4:
            return None
        sul, norte, oeste, leste = (float(v) for v in bb)
        return (sul, norte, oeste, leste)
    except Exception as e:
        print(f"Erro ao localizar a cidade no Nominatim: {e}")
        return None


def _consultar_overpass(query):
    """Tenta a consulta em vários espelhos do Overpass, com retry e backoff.

    Retorna o JSON da resposta, ou None quando nenhum espelho respondeu
    (serviço indisponível) — o que é diferente de responder vazio.
    """
    for endpoint in OVERPASS_ENDPOINTS:
        for tentativa in range(1, 3):
            try:
                resposta = requests.get(endpoint, params={"data": query}, timeout=45, headers=HEADERS)
                resposta.raise_for_status()
                return resposta.json()
            except Exception as e:
                print(f"  Overpass ({endpoint}) tentativa {tentativa} falhou: {type(e).__name__}")
                time.sleep(1.5 * tentativa)
    return None


def _obter_bairros_overpass(sul, norte, oeste, leste):
    """Busca bairros dentro do bbox via Overpass (place=* e admin_level 9/10)."""
    bbox = f"({sul},{oeste},{norte},{leste})"

    query_leve = f"""
[out:json][timeout:40];
(
  node["place"~"^(suburb|neighbourhood|quarter)$"]{bbox};
  way["place"~"^(suburb|neighbourhood|quarter)$"]{bbox};
);
out center tags;
"""

    query_admin = f"""
[out:json][timeout:55];
(
  relation["boundary"="administrative"]["admin_level"="9"]{bbox};
  relation["boundary"="administrative"]["admin_level"="10"]{bbox};
);
out center tags;
"""

    data = _consultar_overpass(query_leve)
    if data is None:
        return None
    if data.get("elements"):
        return data
    return _consultar_overpass(query_admin)


def _bairros_via_overpass(cidade, uf):
    """Retorna a lista de bairros do OSM, ou None se o serviço estiver indisponível."""
    bbox = _obter_bbox_cidade(cidade, uf)
    if not bbox:
        return None

    data = _obter_bairros_overpass(*bbox)
    if data is None:
        return None

    nomes = set()
    for elemento in data.get("elements", []):
        tags = elemento.get("tags") or {}
        nome = tags.get("name")
        if not isinstance(nome, str):
            continue
        nome = nome.strip()
        if nome and nome.lower() != cidade.strip().lower():
            nomes.add(nome)
    return sorted(nomes)


# ---------------------------------------------------------------------------
# API pública do módulo
# ---------------------------------------------------------------------------
def obter_estados():
    if USAR_CACHE:
        estados = _cache(localidades_db.ler_estados)
        if estados:
            print(f"Base local: {len(estados)} estados.")
            return pd.DataFrame(estados)

    estados = _baixar_estados()
    if estados is None:
        estados = _cache(localidades_db.ler_estados)
        if estados:
            print("IBGE indisponível. Usando os estados gravados na base local.")
            return pd.DataFrame(estados)
        print("Erro ao buscar estados.")
        return pd.DataFrame()

    _salvar(localidades_db.salvar_estados, estados)
    return pd.DataFrame(estados)


def obter_cidades(uf):
    if USAR_CACHE:
        municipios = _cache(localidades_db.ler_municipios, uf)
        if municipios:
            print(f"Base local: {len(municipios)} cidades em {uf}.")
            return [m["nome"] for m in municipios]

    municipios = _municipios_da_uf(uf)
    if municipios is None:
        municipios = _cache(localidades_db.ler_municipios, uf)
        if municipios:
            print(f"IBGE indisponível. Usando as cidades de {uf} gravadas na base local.")
            return [m["nome"] for m in municipios]
        print(f"Erro ao buscar cidades para {uf}.")
        return []

    _salvar(localidades_db.salvar_municipios, municipios)
    return sorted(m["nome"] for m in municipios)


def _normalizar(texto):
    """Minúsculas e sem acentos, para comparar nomes digitados pelo usuário."""
    texto = unicodedata.normalize("NFKD", str(texto or ""))
    return "".join(c for c in texto if not unicodedata.combining(c)).strip().casefold()


def filtrar_cidades(cidades, termo):
    """Filtra a lista de cidades por um trecho, ignorando acentos e maiúsculas."""
    alvo = _normalizar(termo)
    if not alvo:
        return []
    return [c for c in cidades if alvo in _normalizar(c)]


def _descobrir_bairros(cidade, uf, municipio):
    """Monta a lista final de bairros: distritos do IBGE + complemento do OSM.

    Retorna (registros, fonte). fonte=None significa "não gravar no cache" —
    usado quando houve falha de rede, para tentar de novo na próxima execução.
    """
    registros = []
    total_distritos = 0
    if municipio:
        distritos = _baixar_distritos(municipio["id_municipio"]) or []
        total_distritos = len(distritos)
        for distrito in distritos:
            if _normalizar(distrito["nome"]) == _normalizar(cidade):
                continue
            registros.append({"nome": distrito["nome"], "id_distrito": distrito["id_distrito"]})

    if len(registros) >= MIN_BAIRROS:
        print(f"  IBGE: {len(registros)} distritos de {cidade}-{uf} serão usados como áreas de busca.")
        return registros, localidades_db.FONTE_IBGE

    # A API de Localidades do IBGE só tem distritos/subdistritos — não tem bairros.
    # Quando o município tem apenas o distrito-sede, não há o que aproveitar.
    if total_distritos <= 1:
        print(f"  IBGE não publica bairros para {cidade}-{uf}: o município tem apenas "
              f"{total_distritos} distrito (a sede).")
    else:
        print(f"  IBGE: apenas {len(registros)} distrito(s) além da sede em {cidade}-{uf}.")

    print("  Buscando bairros no OpenStreetMap...")
    bairros_osm = _bairros_via_overpass(cidade, uf)

    if bairros_osm is None:
        print("  OpenStreetMap indisponível. Esta cidade NÃO será gravada no cache;")
        print("  os distritos do IBGE serão usados apenas nesta execução.")
        return registros, None

    vistos = {_normalizar(r["nome"]) for r in registros}
    for nome in bairros_osm:
        if _normalizar(nome) not in vistos:
            vistos.add(_normalizar(nome))
            registros.append({"nome": nome, "id_distrito": None})

    if bairros_osm:
        return registros, localidades_db.FONTE_OVERPASS
    if registros:
        return registros, localidades_db.FONTE_IBGE
    return [], localidades_db.FONTE_CIDADE


def _resolver_municipio(cidade, uf):
    """Descobre o município no IBGE: id e nome oficial.

    Primeiro tenta a base local; se não achar, baixa a lista da UF (e grava, se
    LOCALIDADES_SALVAR permitir). Retorna None quando o nome não existe na UF.
    """
    alvo = _normalizar(cidade)

    municipios = _cache(localidades_db.ler_municipios, uf) or []
    for item in municipios:
        if _normalizar(item["nome"]) == alvo:
            return {
                "id_municipio": item["id_municipio"],
                "nome": item["nome"],
                "uf": uf,
                "bairros_fonte": item.get("bairros_fonte"),
            }

    baixados = _municipios_da_uf(uf) or []
    _salvar(localidades_db.salvar_municipios, baixados)

    for item in baixados:
        if _normalizar(item["nome"]) == alvo:
            return {
                "id_municipio": item["id_municipio"],
                "nome": item["nome"],
                "uf": item["uf"],
                "bairros_fonte": None,
            }

    if mun := _cache(localidades_db.buscar_municipio, cidade, uf):
        return mun
    return None


def obter_municipio(cidade, uf):
    """Retorna o município do IBGE para o nome digitado (id, nome oficial e uf).

    Útil para gravar sempre o nome oficial, mesmo que o usuário digite sem
    acento ou em minúsculas (ex.: "canoas" -> "Canoas").
    """
    return _resolver_municipio(cidade, uf)


def obter_bairros(cidade, uf):
    """
    Retorna os bairros de uma cidade, usando a base local quando possível.
    Lista vazia significa "buscar a cidade inteira".
    """
    municipio = _resolver_municipio(cidade, uf)

    # Nome oficial do IBGE: evita divergência de acento/caixa nas buscas.
    nome_oficial = municipio["nome"] if municipio else cidade

    if USAR_CACHE and municipio and municipio.get("bairros_fonte"):
        bairros = _cache(localidades_db.ler_bairros, municipio["id_municipio"]) or []
        # O distrito-sede tem o mesmo nome da cidade e não ajuda na busca por área.
        bairros = [b for b in bairros if _normalizar(b) != _normalizar(nome_oficial)]
        fonte = municipio["bairros_fonte"]
        if fonte == localidades_db.FONTE_CIDADE or not bairros:
            print(f"Base local: {nome_oficial}-{uf} sem bairros (fonte: {fonte}).")
            return []
        print(f"Base local: {len(bairros)} bairros de {nome_oficial}-{uf} (fonte: {fonte}).")
        return bairros

    bairros, fonte = _descobrir_bairros(nome_oficial, uf, municipio)

    if municipio and fonte:
        _salvar(localidades_db.salvar_bairros, municipio["id_municipio"], bairros, fonte)

    return [b["nome"] for b in bairros]


def obter_termos_busca(cidade, uf, max_bairros=30):
    """
    Divide a coleta por bairros para ampliar a cobertura do Google Maps
    (que pagina os resultados e não entrega a cidade inteira em uma única busca).
    Se nenhum bairro for descoberto, busca a cidade inteira como fallback.
    """
    print(f"Descobrindo bairros de {cidade} - {uf}...")
    bairros = obter_bairros(cidade, uf)

    if bairros:
        bairros = bairros[:max_bairros]
        print(f"{len(bairros)} bairros encontrados. A coleta será dividida por bairro.")
        return bairros

    print("Nenhum bairro encontrado. Buscando a cidade inteira.")
    return [cidade]


def listar_municipios_pendentes(uf):
    """Lista os municípios da UF que ainda não têm bairros resolvidos.

    Se a UF ainda não estiver na base local, baixa a lista do IBGE (e grava, se
    LOCALIDADES_SALVAR permitir). Retorna [] quando todos já estão resolvidos.
    """
    pendentes = _cache(localidades_db.ler_municipios_pendentes, uf)
    if pendentes is None:
        return []
    if pendentes:
        return pendentes

    # Nada pendente: só é "tudo pronto" se a UF estiver na base local.
    if _cache(localidades_db.ler_municipios, uf):
        return []

    print(f"  {uf} ainda não está na base local. Baixando a lista de municípios do IBGE...")
    municipios = _baixar_municipios(uf)
    if not municipios:
        return []
    _salvar(localidades_db.salvar_municipios, municipios)
    return [{"id_municipio": m["id_municipio"], "nome": m["nome"]} for m in municipios]


def aquecer_bairros_uf(uf, cidades=None, max_cidades=0, pausa_segundos=None):
    """Resolve e grava os bairros de todas as cidades de uma UF (uma única vez).

    Útil para preparar o cache e depois rodar a coleta sem nenhuma consulta de
    rede. A pausa entre cidades é aplicada só quando o OpenStreetMap foi de fato
    consultado (cidades cobertas pelo IBGE são instantâneas).

    Retorna um dicionário com o resumo da execução.
    """
    if not SALVAR:
        print("\nLOCALIDADES_SALVAR=false: não é possível aquecer a base local.")
        print("Ative a flag LOCALIDADES_SALVAR para gravar os bairros.")
        return None

    pausa_segundos = AQUECER_PAUSA_PADRAO if pausa_segundos is None else pausa_segundos

    if cidades is None:
        print(f"\nVerificando quais cidades de {uf} ainda precisam de bairros...")
        cidades = listar_municipios_pendentes(uf)

    total_pendente = len(cidades)
    if not total_pendente:
        print(f"Todas as cidades de {uf} já têm bairros na base local. Nada a fazer.")
        return {"uf": uf, "pendentes": 0, "processadas": 0, "ibge": 0,
                "osm": 0, "sem_bairros": 0, "falhas": 0}

    if max_cidades and max_cidades > 0:
        cidades = cidades[:max_cidades]

    print(f"\nAquecendo bairros de {len(cidades)} cidade(s) de {uf} "
          f"({total_pendente} pendente(s) no total).")
    print(f"Pausa entre cidades que usam OpenStreetMap: {pausa_segundos}s")
    print("Interrompa com Ctrl+C — o progresso já gravado é preservado.\n")

    resumo = {"uf": uf, "pendentes": total_pendente, "processadas": 0,
              "ibge": 0, "osm": 0, "sem_bairros": 0, "falhas": 0}

    try:
        for indice, cidade in enumerate(cidades, 1):
            nome = cidade["nome"]
            print(f"[{indice}/{len(cidades)}] {nome}-{uf}")

            bairros = obter_bairros(nome, uf)
            municipio = _cache(localidades_db.buscar_municipio, nome, uf)
            fonte = (municipio or {}).get("bairros_fonte")
            resumo["processadas"] += 1

            if fonte is None:
                resumo["falhas"] += 1
                print(f"  Falhou (nada gravado). Pulando.")
            elif fonte == localidades_db.FONTE_OVERPASS:
                resumo["osm"] += 1
            elif fonte == localidades_db.FONTE_IBGE:
                resumo["ibge"] += 1
            else:
                resumo["sem_bairros"] += 1

            usou_osm = fonte in (localidades_db.FONTE_OVERPASS,
                                 localidades_db.FONTE_CIDADE)
            if usou_osm and indice < len(cidades):
                time.sleep(pausa_segundos)
    except KeyboardInterrupt:
        print("\nInterrompido pelo usuário. O que já foi gravado está preservado.")

    print(f"\nResumo de {uf}: {resumo['processadas']} cidade(s) processada(s) "
          f"de {total_pendente} pendente(s).")
    print(f"  via IBGE: {resumo['ibge']} | via OpenStreetMap: {resumo['osm']} | "
          f"sem bairros: {resumo['sem_bairros']} | falhas: {resumo['falhas']}")
    restantes = total_pendente - resumo["processadas"]
    if restantes > 0:
        print(f"  {restantes} cidade(s) continuam pendentes — rode novamente para retomar.")
    return resumo


def _descrever_gravacao(total, recebidos):
    """Texto do resumo da sincronização (distingue gravado de apenas baixado)."""
    if total is None:
        return f"{recebidos} recebidos, NÃO gravados (base local indisponível)"
    return f"{total} gravados"


def sincronizar_base_localidades():
    """Baixa estados, municípios e distritos do IBGE para o DuckDB.

    Depois disso, com LOCALIDADES_USAR_CACHE=true, a coleta não faz chamadas de
    rede para descobrir bairros — exceto nas cidades em que o IBGE não tem
    distritos úteis (aí o OSM é consultado uma única vez e o resultado é gravado).
    """
    if not SALVAR:
        print("\nLOCALIDADES_SALVAR=false: a sincronização está desativada.")
        print("Nada foi baixado nem gravado. Ative a flag para popular a base local.")
        return False

    print("\nSincronizando base de localidades do IBGE...")

    estados = _baixar_estados()
    if estados is None:
        print("Falha ao baixar os estados. Sincronização abortada.")
        return False
    total = _salvar(localidades_db.salvar_estados, estados)
    print(f"  Estados: {_descrever_gravacao(total, len(estados))}.")

    municipios = _baixar_municipios()
    if municipios is None:
        print("Falha ao baixar os municípios. Sincronização abortada.")
        return False
    total = _salvar(localidades_db.salvar_municipios, municipios)
    print(f"  Municípios: {_descrever_gravacao(total, len(municipios))}.")

    print("  Baixando distritos (pode levar alguns segundos)...")
    distritos = _baixar_distritos()
    if distritos is None:
        print("Falha ao baixar os distritos. Estados e municípios foram gravados.")
        return False
    total = _salvar(localidades_db.salvar_distritos_bulk, distritos, MIN_BAIRROS)
    print(f"  Distritos: {_descrever_gravacao(total, len(distritos))}.")

    stats = _cache(localidades_db.estatisticas) or {}
    print(f"\nBase local: {stats.get('estados', 0)} estados, "
          f"{stats.get('municipios', 0)} municípios, {stats.get('bairros', 0)} bairros "
          f"({stats.get('cidades_prontas', 0)} cidades com bairros prontos).")
    print("Sincronização concluída.")
    return True
</file>

<file path=".gitignore">
# Dados: o banco DuckDB É versionado (data/leads.duckdb).
# Apenas artefatos transientes do DuckDB e saídas geradas ficam de fora.
*.duckdb.wal
*.duckdb.tmp
*.xlsx
*.csv
*.log

# Segredos e configuração local (contém a API key da WAHA)
.env

# Sessões do WhatsApp (WAHA)
sessions/

# Ambientes Virtuais
venv/
env/
.venv/

# Python Cache
__pycache__/
*.py[cod]
*$py.class

# Configurações de IDE
.vscode/
.idea/

# Sistema Operacional
.DS_Store
Thumbs.db
</file>

<file path="src/main.py">
# src/main.py
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.locations import (
    obter_estados,
    obter_cidades,
    obter_termos_busca,
    obter_municipio,
    filtrar_cidades,
    sincronizar_base_localidades,
    listar_municipios_pendentes,
    aquecer_bairros_uf,
    SALVAR as LOCALIDADES_SALVAR,
)
from src.scraper import rodar_scraper_multithread
from src.database import LeadDatabase
from src.whatsapp import (
    disparar_campanha,
    MENSAGEM_PADRAO,
    WAHA_INTERVALO,
    WAHA_LIMITE,
    WAHA_ATIVO,
    SOMENTE_ENVIO,
)


def coletar_leads():
    df_estados = obter_estados()
    if df_estados.empty:
        return

    uf_escolhida = input("Digite a UF (ex: RS, SP, RJ): ").strip().upper()
    if uf_escolhida not in df_estados['uf'].values:
        print("UF inválida.")
        return

    cidades = obter_cidades(uf_escolhida)
    termo_cidade = input("Digite o nome da cidade: ").strip()
    cidades_filtradas = filtrar_cidades(cidades, termo_cidade)

    if not cidades_filtradas:
        print("Cidade não encontrada.")
        return
    elif len(cidades_filtradas) > 1:
        cidade_escolhida = input(
            f"Várias encontradas ({', '.join(cidades_filtradas[:3])}...). Digite o nome exato: "
        ).strip()
        exatos = filtrar_cidades(cidades, cidade_escolhida)
        cidade_escolhida = exatos[0] if exatos else cidade_escolhida
    else:
        cidade_escolhida = cidades_filtradas[0]

    # Confirma o município no IBGE e passa a usar o nome oficial (com acentos).
    municipio = obter_municipio(cidade_escolhida, uf_escolhida)
    if municipio:
        cidade_escolhida = municipio["nome"]
        print(f"Município (IBGE): {cidade_escolhida}-{uf_escolhida} | código {municipio['id_municipio']}")
    else:
        print(f"Aviso: {cidade_escolhida}-{uf_escolhida} não foi confirmado no IBGE.")

    nicho = input(f"\nQual o nicho para {cidade_escolhida}-{uf_escolhida}? ").strip().lower()

    termos_busca = obter_termos_busca(cidade_escolhida, uf_escolhida)

    mostrar_navegador = input("\nVer o navegador? (S/N): ").strip().upper() == 'S'

    print("\nIniciando extração...")
    db = LeadDatabase()

    df_resultados = rodar_scraper_multithread(
        nicho=nicho,
        cidade=cidade_escolhida,
        uf=uf_escolhida,
        termos_lista=termos_busca,
        mostrar_navegador=mostrar_navegador,
        save_callback=db.save_leads,  # salvamento incremental (UPSERT) a cada área concluída
    )

    if not df_resultados.empty:
        print("\nLeads salvos incrementalmente no DuckDB (UPSERT).")
        db.export_to_excel(nicho, cidade_escolhida)
    else:
        print("Nenhum dado extraído.")

    db.close()


def enviar_whatsapp_menu():
    print("\n=== ENVIO WHATSAPP (WAHA) ===")

    if not WAHA_ATIVO:
        print("Envio de WhatsApp desativado (WAHA_ATIVO=false no .env).")
        return

    db = LeadDatabase()

    pendentes = db.get_leads_para_envio(limite=WAHA_LIMITE)
    if pendentes.empty:
        print("Nenhum lead celular pendente de envio.")
        db.close()
        return

    print(f"{len(pendentes)} lead(s) celular(es) pendentes (fixos são ignorados).")
    if WAHA_LIMITE:
        print(f"Limite configurado: {WAHA_LIMITE} lead(s) por campanha.")

    print(f"Mensagem padrão: {MENSAGEM_PADRAO}")
    mensagem = input("Digite a mensagem (ou Enter para usar a padrão): ").strip()
    if not mensagem:
        mensagem = MENSAGEM_PADRAO

    confirmar = input(f"Enviar para {len(pendentes)} lead(s)? (S/N): ").strip().upper()
    if confirmar != 'S':
        print("Envio cancelado.")
        db.close()
        return

    disparar_campanha(db, mensagem_template=mensagem, intervalo=WAHA_INTERVALO, limite=WAHA_LIMITE)
    db.close()


def aquecer_bairros_menu():
    """Prepara o cache de bairros de uma UF inteira (sem raspar leads)."""
    print("\n=== AQUECER BAIRROS DE UMA UF ===")

    if not LOCALIDADES_SALVAR:
        print("LOCALIDADES_SALVAR=false: o aquecimento está desativado.")
        print("Ative a flag LOCALIDADES_SALVAR no .env para gravar os bairros.")
        return

    print("Resolve e grava os bairros de todas as cidades da UF, uma única vez.")
    print("Depois disso a coleta por cidade não consulta mais IBGE/OSM.")

    df_estados = obter_estados()
    if df_estados.empty:
        print("Não foi possível obter a lista de estados.")
        return

    uf = input("Digite a UF (ex: RS, SP, RJ): ").strip().upper()
    if uf not in df_estados['uf'].values:
        print("UF inválida.")
        return

    print(f"\nVerificando quais cidades de {uf} ainda precisam de bairros...")
    pendentes = listar_municipios_pendentes(uf)
    if not pendentes:
        print(f"Todas as cidades de {uf} já estão na base local. Nada a fazer.")
        return

    print(f"{len(pendentes)} cidade(s) pendente(s) em {uf}.")
    print("As cidades cobertas pelo IBGE são instantâneas; as demais usam o")
    print("OpenStreetMap (Nominatim + Overpass), com pausa entre elas.")

    limite = input("Quantas cidades processar agora? (Enter = todas): ").strip()
    max_cidades = 0
    if limite:
        try:
            max_cidades = max(1, int(limite))
        except ValueError:
            print("Valor inválido. Usando todas.")
            max_cidades = 0

    previstas = min(max_cidades, len(pendentes)) if max_cidades else len(pendentes)
    confirmar = input(f"Processar {previstas} cidade(s)? (S/N): ").strip().upper()
    if confirmar != 'S':
        print("Operação cancelada.")
        return

    aquecer_bairros_uf(uf, cidades=pendentes, max_cidades=max_cidades)


def menu_interativo():
    # Flag de linha de comando: `python src/main.py --so-enviar` pula a coleta
    # e vai direto para o envio (equivale a SOMENTE_ENVIO=true no .env).
    so_enviar_cli = "--so-enviar" in sys.argv

    if SOMENTE_ENVIO or so_enviar_cli:
        enviar_whatsapp_menu()
        return

    while True:
        print("\n=== MAP SCRAPER ===")
        print("1 - Coletar leads")
        print("2 - Enviar mensagens WhatsApp")
        print("3 - Sincronizar base de localidades (IBGE)")
        print("4 - Aquecer bairros de uma UF (OpenStreetMap)")
        print("5 - Sair")
        opcao = input("Escolha uma opção: ").strip()

        if opcao == "1":
            coletar_leads()
        elif opcao == "2":
            enviar_whatsapp_menu()
        elif opcao == "3":
            sincronizar_base_localidades()
        elif opcao == "4":
            aquecer_bairros_menu()
        elif opcao == "5":
            print("Até mais!")
            break
        else:
            print("Opção inválida.")


if __name__ == "__main__":
    menu_interativo()
</file>

<file path="README.md">
Documentação do Projeto: MAP SCRAPER

1. Objetivo do Projeto

    Ferramenta automatizada e gratuita para prospecção de leads B2B locais que muitas vezes não possuem site, mas estão presentes no Google Maps e no Instagram.

    O sistema é capaz de receber um Estado e Cidade, descobrir os bairros de forma dinâmica, raspar os dados do Google Maps (Nome, Telefone, Instagram, Site) e gerenciar esses dados em um banco local, evitando duplicatas e permitindo o descarte de leads já trabalhados.

2. Funcionalidades

    A ferramenta foi construída com uma arquitetura modular e conta com os seguintes recursos:

        - Busca Dinâmica de Localidades: Integração com a API do IBGE para listar Estados, Cidades e Distritos, gravando tudo em tabelas locais (cache) para não depender da rede nas próximas execuções. O nome digitado é confirmado no IBGE (aceita sem acento e em minúsculas) e o nome oficial é usado nas buscas. Complemento com Nominatim + Overpass (OpenStreetMap) para descobrir bairros quando o IBGE não cobre a cidade. Se nenhum bairro for encontrado, ele faz fallback buscando a cidade inteira.

        - Scraping em Multithreading: Uso do Playwright com ThreadPoolExecutor para abrir múltiplos navegadores simultaneamente e acelerar a coleta em diferentes bairros.

        - Cobertura por Bairros: A coleta é dividida por bairros para contornar a paginação do Google Maps e capturar mais leads por cidade.

        - Rolagem Dinâmica: A lista de resultados é rolada até esgotar (com limite de segurança), em vez de um número fixo de rolagens.

        - Robustez: Retry com backoff em erros transitórios, deduplicação intra-execução e salvamento incremental no DuckDB a cada área concluída.

        - Anti-bloqueio: User-Agent realista, viewport configurado e pausas aleatórias entre as requisições para reduzir o risco de bloqueio.

        - Tratamento de Dados (Data Cleansing):

        - Formatação automática de telefones para o padrão brasileiro (XX) XXXXX-XXXX.

        - Classificação automática do telefone: Celular (11 dígitos) ou Fixo (10 dígitos).

        - Banco de Dados Local (DuckDB): Armazenamento rápido e seguro em um arquivo local.

        - UPSERT: Se o lead já existe, ele atualiza os dados e a data de extração. Se for novo, insere.

        - Controle de Status: Leads podem ser marcados como ativo ou descartado. Se um lead descartado for encontrado novamente, o robô ignora e não atualiza.

        - Exportação para Excel: Gera um relatório limpo e ordenado apenas com os leads ativos.

        - Envio de WhatsApp (WAHA): Envia mensagens para os leads via WAHA (WhatsApp HTTP API). Só envia para leads ativos do tipo Celular (nunca fixo) e ainda não enviados, com intervalo configurável entre disparos para evitar spam. Cada envio é registrado em `status_whatsapp` e `data_envio_whatsapp`.

        - Base de Localidades Offline: estados, municípios e distritos do IBGE são gravados no próprio DuckDB (`localidades_estados`, `localidades_municipios`, `localidades_bairros`). Na primeira consulta de uma cidade os dados vêm da API; nas seguintes, tudo sai do banco, sem rede. A sincronização completa fica no menu (opção 3).

        - Tratamento de Captcha/Bloqueio: detecta a tela de "tráfego incomum" do Google Maps e aplica pausa longa antes de tentar novamente, além de um cooldown compartilhado que pausa todas as threads ao mesmo tempo. Se o bloqueio persistir, a área é abortada preservando os leads já coletados.

3. Stack Tecnológica

    - Linguagem: Python 3.10+
    - Scraping: Playwright (Chromium)
    - Banco de Dados: DuckDB
    - Manipulação de Dados: Pandas
    - APIs: IBGE (Localidades), Nominatim e Overpass (Bairros)
    - Tratamento: Regex (para telefones)
    - WhatsApp: WAHA (WhatsApp HTTP API)

4. Estrutura de Pastas

    map_scraper_project/
    │
    ├── data/                  # Onde o banco leads.duckdb é salvo
    ├── memory/                # Memória do projeto para modelos de IA (ver seção 12)
    ├── output/                # Onde os arquivos Excel finais são gerados
    │
    ├── src/                   # Código-fonte
    │   ├── __init__.py        
    │   ├── config.py          # Leitura centralizada do .env e flags
    │   ├── database.py        # Lógica do DuckDB (UPSERT, status, exportação, log de envio)
    │   ├── localidades_db.py  # Cache local das localidades (tabelas IBGE no DuckDB)
    │   ├── locations.py       # IBGE + OSM (Nominatim/Overpass), com cache no banco
    │   ├── scraper.py         # Robô Playwright, multithreading e anti-bloqueio
    │   ├── utils.py           # Formatação de telefone (Fixo/Celular)
    │   ├── whatsapp.py        # Envio via WAHA (WhatsApp HTTP API)
    │   └── main.py            # Menu interativo e orquestração
    │
    ├── .env.example           # Modelo das variáveis de ambiente
    ├── requirements.txt       # Dependências do projeto
    └── README.md              # Este documento

5. Como Usar (Manual do Usuário)

    Passo 1: Instalação
    No terminal, dentro da pasta raiz do projeto, instale as dependências e o navegador do Playwright:

    python -m venv venv
    .\venv\Scripts\Activate
    python -m pip install -r requirements.txt
    python -m playwright install chromium
    Passo 2: Execução
    Antes de rodar, crie o seu `.env` a partir do modelo:

    Copy-Item .env.example .env

    Rode o arquivo principal:

    python src/main.py
    Passo 3: Interação no Terminal
    O menu tem 5 opções:

    1 - Coletar leads: faz 5 perguntas simples (UF, Cidade, Nicho, Bairros automáticos, Ver navegador).
    2 - Enviar mensagens WhatsApp: envia para os leads celulares pendentes (ver seção 7).
    3 - Sincronizar base de localidades (IBGE): baixa estados, municípios e distritos para o DuckDB (ver seção 8).
    4 - Aquecer bairros de uma UF (OpenStreetMap): resolve e grava os bairros de todas as cidades do estado (ver seção 8).
    5 - Sair.

    Passo 4: Resultados

        O banco de dados será atualizado em data/leads.duckdb.

        Um arquivo Excel será gerado em output/leads_nicho_cidade.xlsx.


6. Gerenciamento do Banco de Dados (Regras de Negócio)

    Se você quiser descartar um lead para que ele não seja mais exportado e não seja atualizado nas próximas buscas, você pode rodar um comando SQL direto no DuckDB (via DBeaver ou script Python):

    sql
    -- Para descartar um lead
    UPDATE leads SET status = 'descartado' WHERE nome = 'Nome da Barbearia';

    -- Para reativar um lead
    UPDATE leads SET status = 'ativo' WHERE nome = 'Nome da Barbearia';
    Nota: A regra do UPSERT no database.py garante que, se o robô achar uma barbearia "descartada", ele pula ela e não sobrescreve seus dados no banco.

7. Envio de WhatsApp (WAHA)

    Pré-requisito: uma instância WAHA rodando com um número conectado via QR Code.

    Configuração (arquivo .env na raiz do projeto):
    Copie .env.example para .env e preencha os valores.

    ```
    WAHA_API_URL=http://localhost:3000
    WAHA_API_KEY=SUA_CHAVE_AQUI
    WAHA_SESSION=default
    WAHA_ATIVO=true
    SOMENTE_ENVIO=false
    WAHA_INTERVALO=13
    WAHA_LIMITE=
    ```

    Flags de comportamento:
    - WAHA_ATIVO: se false, desliga o envio de WhatsApp (não tenta enviar).
    - SOMENTE_ENVIO: se true, pula a coleta e vai direto para o envio
      (equivalente a rodar `python src/main.py --so-enviar`).
    - WAHA_LIMITE: quantidade máxima de leads por campanha (vazio = sem limite).

    Regras de envio (evita spam):
    - Só envia para leads com status = 'ativo'.
    - Só envia para tipo_telefone = 'Celular' (fixos são ignorados).
    - Só envia para leads ainda não enviados (status_whatsapp = 'pendente' ou NULL).
    - Intervalo de WAHA_INTERVALO segundos entre envios.

    Logs no banco:
    - status_whatsapp: 'pendente', 'enviado' ou 'falhou'.
    - data_envio_whatsapp: gravada apenas quando o envio é bem-sucedido.

    A mensagem pode usar as variáveis {nome}, {bairro} e {cidade}.


8. Base de Localidades Offline (IBGE)

    O projeto mantém um cache local das localidades no próprio DuckDB, criado na
    primeira consulta e reaproveitado nas seguintes (sem rede).

    Tabelas criadas automaticamente (guardam apenas o essencial):
    - localidades_estados: uf, nome
    - localidades_municipios: id_municipio, nome, uf + estado da coleta de bairros
    - localidades_bairros: id_municipio, nome, id_distrito

    Fontes (API de Localidades do IBGE):
    - Estados:    https://servicodados.ibge.gov.br/api/v1/localidades/estados
    - Municípios: https://servicodados.ibge.gov.br/api/v1/localidades/municipios
    - Distritos:  https://servicodados.ibge.gov.br/api/v1/localidades/distritos

    Configuração (.env):
    ```
    LOCALIDADES_USAR_CACHE=true
    LOCALIDADES_SALVAR=true
    LOCALIDADES_MIN_BAIRROS=3
    AQUECER_PAUSA_SEGUNDOS=2
    ```

    - LOCALIDADES_USAR_CACHE=true (padrão): consulta o banco primeiro e só chama a
      API quando o dado ainda não existe (e aí grava o resultado).
    - LOCALIDADES_USAR_CACHE=false: sempre busca na API do IBGE e atualiza a base
      local com o que voltou.
    - LOCALIDADES_SALVAR=false: modo somente leitura. Nada é gravado e nem as
      tabelas são criadas; o banco só é consultado. A sincronização do menu fica
      desativada.
    - LOCALIDADES_MIN_BAIRROS: mínimo de distritos do IBGE para a cidade ser
      considerada coberta. Abaixo disso, os bairros são complementados com o
      OpenStreetMap (Nominatim + Overpass) e o resultado também fica em cache.
    - AQUECER_PAUSA_SEGUNDOS: pausa entre cidades no aquecimento por UF, aplicada
      somente quando a cidade usou o OpenStreetMap.

    As duas flags são independentes:

    | USAR_CACHE | SALVAR | Comportamento |
    |---|---|---|
    | true  | true  | lê do banco; grava o que faltar (recomendado) |
    | false | true  | sempre vai à API e regrava tudo (força atualização) |
    | true  | false | só lê o banco; o que não existe vai à API sem gravar |
    | false | false | sempre à API, sem tocar no banco |

    O que acontece ao rodar de novo para a mesma cidade:

    - localidades_estados: UPSERT por uf (só atualiza o nome).
    - localidades_municipios: UPSERT por id_municipio (atualiza nome/uf e
      PRESERVA bairros_fonte / bairros_atualizado_em).
    - localidades_bairros: a lista da cidade é tratada como autoritativa. Nomes
      iguais são atualizados, nomes novos são inseridos e nomes que não vieram mais
      são removidos — mas apenas daquela cidade.
    - Sincronização completa (menu opção 3): aditiva. Ela insere/atualiza os
      distritos do IBGE sem apagar bairros que já existem, então listas
      complementadas pelo OpenStreetMap são preservadas.

    Rodar só para um estado também é seguro: obter_cidades(uf) grava apenas os
    municípios daquela UF, e nada de outras UFs é alterado.

    Sincronização completa: menu opção 3 (ou `sincronizar_base_localidades()`), que
    baixa de uma vez todos os estados, municípios e distritos (~10,7 mil registros).

    Aquecimento por UF: menu opção 4 (ou `aquecer_bairros_uf('RS')`). Resolve e
    grava os bairros de TODAS as cidades de um estado, sem raspar nenhum lead.
    Depois disso, a coleta por cidade não consulta mais IBGE/OSM.

    - Processa apenas as cidades com `bairros_fonte IS NULL` (ou seja, retoma de
      onde parou em execuções anteriores).
    - Cidades cobertas pelo IBGE são instantâneas; as demais usam o OpenStreetMap.
    - A pausa entre cidades (AQUECER_PAUSA_SEGUNDOS) é aplicada somente quando o
      OSM foi consultado — respeitando o limite de 1 req/s do Nominatim.
    - Ctrl+C interrompe sem perder o que já foi gravado; basta rodar de novo.
    - É possível limitar quantas cidades processar por execução.

    Importante: os "distritos" do IBGE são divisões administrativas e, em muitos
    municípios, resumem-se à própria sede. Por isso o fallback com o OSM continua
    existindo — a diferença é que ele roda uma única vez por cidade e o resultado
    é gravado no banco. Se o OSM estiver fora do ar, nada é gravado (a próxima
    execução tenta de novo) e a coleta segue com os distritos do IBGE.

    A API de Localidades do IBGE NÃO fornece bairros — apenas distritos e
    subdistritos. Exemplo real: Canoas-RS tem 1 distrito (a própria sede) e 0
    subdistritos, então o IBGE não contribui com áreas para essa cidade e o robô
    informa isso e segue para o OpenStreetMap:

    ```
    IBGE não publica bairros para Canoas-RS: o município tem apenas 1 distrito (a sede).
    Buscando bairros no OpenStreetMap...
    ```

    Cidades com vários distritos (São Paulo: 96, Campinas: 7) usam o IBGE e não
    consultam o OSM. Das 5.571 cidades do país, 643 têm distritos suficientes.

    Como a cidade é resolvida: o nome digitado é comparado sem acento e sem
    diferenciar maiúsculas ("canoas", "sao leopoldo") com a lista do IBGE, e o nome
    oficial é exibido e usado no scraping, no banco e no Excel:

    ```
    Digite o nome da cidade: canoas
    Município (IBGE): Canoas-RS | código 4304606
    ```

    Para forçar a atualização de uma cidade já gravada, limpe a marca:
    ```sql
    UPDATE localidades_municipios SET bairros_fonte = NULL WHERE nome = 'Porto Alegre';
    ```

9. Anti-bloqueio / Captcha (Google Maps)

    Quando o Google responde com a tela de "tráfego incomum" (captcha), o robô:
    1. detecta o bloqueio (URL /sorry/, formulários de captcha ou textos típicos);
    2. aplica um cooldown global, pausando TODAS as threads ao mesmo tempo;
    3. espera a pausa longa e tenta novamente até CAPTCHA_MAX_TENTATIVAS;
    4. se o bloqueio persistir, aborta apenas aquela área, preservando os leads
       já extraídos (que continuam sendo salvos incrementalmente).

    Configuração (.env):
    ```
    CAPTCHA_MAX_TENTATIVAS=2
    CAPTCHA_PAUSA_SEGUNDOS=300
    CAPTCHA_PAUSA_GLOBAL_SEGUNDOS=180
    ```

    - CAPTCHA_MAX_TENTATIVAS: tentativas por página antes de abortar a área.
    - CAPTCHA_PAUSA_SEGUNDOS: pausa longa da thread que levou o bloqueio.
    - CAPTCHA_PAUSA_GLOBAL_SEGUNDOS: pausa compartilhada entre as threads.

    A resolução automática de captcha por serviço externo (2Captcha, CapMonster
    etc.) não está implementada — o comportamento padrão é pausar e desistir da
    área em vez de insistir. Em coletas muito grandes, aumente as pausas acima.

10. commit forçado

    git add -A; git commit -m "sync local $(Get-Date -Format 'yyyy-MM-dd HH:mm')"; git push --force-with-lease origin main

11. Próximos Passos (Melhorias Futuras)

    Já implementado:
    - Base de localidades offline no DuckDB (estados, municípios e distritos do IBGE).
    - Detecção de captcha com pausa longa e cooldown compartilhado entre threads.

    Pendências sugeridas:
    - Resolução automática de captcha: integrar um serviço (2Captcha/CapMonster) para
      coletas muito grandes, hoje o robô apenas pausa e desiste da área.

    - Enriquecimento de E-mail: Criar um script secundário que lê os sites encontrados e busca e-mails de contato (usando Regex).


12. Memória do Projeto para IA (pasta memory/)

    A pasta `memory/` reúne documentação resumida e densa, pensada para ser lida
    por modelos de IA antes de alterar o código (economiza contexto/custo).

    Ordem de leitura:
    1. memory/00-resumo-projeto.md        -> objetivo, stack e estrutura
    2. memory/01-arquitetura-e-modulos.md -> módulos, funções e fluxos
    3. memory/02-decisoes-e-armadilhas.md -> decisões, bugs conhecidos, cuidados
    4. memory/03-historico-de-mudancas.md -> o que mudou e o que ficou pendente
    5. memory/04-como-contribuir.md       -> padrões de código, logs, testes e docs

    Regras: manter os arquivos curtos, registrar o "porquê" das decisões e nunca
    colocar segredos ali (API keys ficam apenas no `.env`).


13. Observação sobre configuração

    O modelo completo e comentado de todas as variáveis está em `.env.example`.
    Cada item traz a faixa de valores e o efeito colateral. Comentários devem
    ficar em linha própria; comentário na mesma linha do valor é lido como parte
    do valor.
</file>

</files>



<instruction>
# Instruções para o Assistente de IA
Você é um desenvolvedor especialista trabalhando neste projeto de Map Scraper.
Por favor, processe todas as solicitações, explicações, comentários de código e interações estritamente em Português do Brasil (pt-BR).

</instruction>
````

## File: repomix.config.json
````json
{
  "$schema": "https://repomix.com/schemas/latest/schema.json",
  "input": {
    "maxFileSize": 52428800
  },
  "output": {
    "filePath": "repomix-output.md",
    "style": "markdown",
    "filePathStyle": "target-relative",
    "parsableStyle": false,
    "instructionFilePath": "repomix-instrucao.md",
    "fileSummary": true,
    "directoryStructure": true,
    "files": true,
    "removeComments": false,
    "removeEmptyLines": false,
    "compress": false,
    "topFilesLength": 5,
    "showLineNumbers": false,
    "truncateBase64": false,
    "copyToClipboard": false,
    "includeFullDirectoryStructure": false,
    "tokenCountTree": false,
    "git": {
      "sortByChanges": true,
      "sortByChangesMaxCommits": 100,
      "includeDiffs": false,
      "includeLogs": false,
      "includeLogsCount": 50
    }
  },
  "include": [],
  "ignore": {
    "useGitignore": true,
    "useDotIgnore": true,
    "useDefaultPatterns": true,
    "customPatterns": []
  },
  "security": {
    "enableSecurityCheck": true
  },
  "tokenCount": {
    "encoding": "o200k_base"
  }
}
````

## File: memory/00-resumo-projeto.md
````markdown
# 00 — Resumo do Projeto

**Map Scraper** — ferramenta local de prospecção de leads B2B a partir do Google Maps.

- **Entrada:** UF + cidade + nicho (ex.: `RS`, `Canoas`, `barbearias`).
- **Processo:** divide a busca por bairros, raspa o Google Maps com Playwright em
  multithread e extrai nome, telefone, Instagram e site.
- **Saída:** leads no DuckDB (`data/leads.duckdb`) + Excel em `output/`.
- **Extra:** dispara mensagens de WhatsApp via WAHA para leads já coletados.

## Fluxo de alto nível

```
menu (src/main.py)
  └─ 1 Coletar    → locations.obter_termos_busca(cidade, uf)
                  → scraper.rodar_scraper_multithread(...)
                  → database.LeadDatabase.save_leads (UPSERT incremental)
                  → database.export_to_excel
  └─ 2 WhatsApp   → database.get_leads_para_envio
                  → whatsapp.disparar_campanha (WAHA)
  └─ 3 Sincronizar localidades (IBGE) → locations.sincronizar_base_localidades
  └─ 4 Aquecer bairros de uma UF       → locations.aquecer_bairros_uf
  └─ 5 Sair
```

## Stack

| Item | Tecnologia |
|---|---|
| Linguagem | Python 3.10+ (ambiente: `venv/`) |
| Scraping | Playwright (Chromium) + ThreadPoolExecutor |
| Banco | DuckDB (arquivo único, 1 processo por vez) |
| Dados | Pandas |
| Localidades | API IBGE + Nominatim/Overpass (OpenStreetMap) |
| WhatsApp | WAHA (WhatsApp HTTP API) |
| Config | `.env` carregado por `src/config.py` |

## Estrutura

```
map_scraper_project/
├── data/          leads.duckdb (+ .wal transiente, ignorado no Git)
├── memory/        esta documentação para IA
├── output/        Excel gerado (ignorado no Git)
├── src/
│   ├── config.py          loader do .env + helpers (bool/int)
│   ├── database.py        LeadDatabase: tabela leads, UPSERT, Excel, log WAHA
│   ├── localidades_db.py  cache IBGE em DuckDB (tabelas localidades_*)
│   ├── locations.py       IBGE + OSM + cache; sync e aquecimento por UF
│   ├── scraper.py         Playwright, multithread, anti-captcha
│   ├── utils.py           formatar_telefone → (telefone, tipo, link wa)
│   ├── whatsapp.py        envio via WAHA
│   └── main.py            menu interativo
├── .env / .env.example
├── requirements.txt
└── README.md
```

## Git — o que é versionado

| Versionado | Ignorado |
|---|---|
| `data/leads.duckdb` | `.env` (segredos) |
| `src/`, `memory/`, `README.md` | `*.duckdb.wal`, `*.duckdb.tmp` |
| `.env.example` | `*.xlsx`, `*.csv`, `*.log` |
| | `venv/`, `__pycache__/`, `sessions/` |

Comando de sync usado pelo mantenedor (sobrescreve o remoto):

```powershell
git add -A; git commit -m "sync local $(Get-Date -Format 'yyyy-MM-dd HH:mm')"; git push --force-with-lease origin main
```
````

## File: memory/01-arquitetura-e-modulos.md
````markdown
# 01 — Arquitetura e Módulos

Todos os módulos usam imports absolutos (`from src.x import y`). `src/main.py`
adiciona a raiz do projeto ao `sys.path` antes de importar.

---

## src/config.py

Único ponto de leitura do `.env`. **Chame `carregar_env()` antes de calcular
constantes de módulo** (o import já executa uma vez).

```python
carregar_env(caminho=None)      # não sobrescreve variáveis já no ambiente
str_para_bool(valor, padrao)    # aceita 1/true/yes/s/sim/on
env_int(nome, padrao)           # inteiro com fallback
PROJETO_RAIZ, CAMINHO_ENV
```

> `src/whatsapp.py` chama `carregar_env()` no import (herança histórica).
> `src/locations.py` e `src/scraper.py` dependem disso para ler suas flags.

---

## src/localidades_db.py — cache de localidades

Acesso ao **mesmo** `data/leads.duckdb`. **Abre e fecha conexão a cada operação**,
para não segurar o arquivo durante o scraping (DuckDB permite só 1 processo).

Tabelas (criadas automaticamente quando `CRIAR_TABELAS = True`):

| Tabela | Colunas |
|---|---|
| `localidades_estados` | `uf` PK, `nome` |
| `localidades_municipios` | `id_municipio` PK, `nome`, `uf`, `bairros_fonte`, `bairros_atualizado_em` |
| `localidades_bairros` | `id_municipio`, `nome`, `id_distrito` — PK (`id_municipio`,`nome`) |

`bairros_fonte` ∈ {`ibge`, `overpass`, `cidade`, `NULL` (não coletado)}.

Funções:

```python
conexao(db_path=None)              # contextmanager; DDL se CRIAR_TABELAS
ler_estados() / salvar_estados(registros)
ler_municipios(uf)                 # inclui bairros_fonte (necessário p/ cache hit)
ler_municipios_pendentes(uf)       # bairros_fonte IS NULL
salvar_municipios(registros)       # UPSERT preserva bairros_fonte
buscar_municipio(cidade, uf)       # dict ou None
ler_bairros(id_municipio) / salvar_bairros(id_municipio, registros, fonte)
salvar_distritos_bulk(distritos, min_bairros=3)   # aditivo
estatisticas()                     # dict com contagens
CacheIndisponivel                  # exceção (arquivo travado / tabela ausente)
```

**Semânticas importantes**

- `salvar_bairros` é **autoritativo por cidade**: apaga nomes daquela cidade que
  não vieram na lista nova (não toca em outras cidades).
- `salvar_distritos_bulk` é **aditivo**: não apaga bairros do OSM já gravados.
- `salvar_municipios` é UPSERT e **preserva** `bairros_fonte`.

---

## src/locations.py — IBGE + OpenStreetMap + cache

Endpoints usados (`IBGE_API`):

```
/estados                         → UF (sigla, nome)
/estados/{uf}/municipios         → municípios da UF
/municipios                      → todos (usado na sync nacional)
/municipios/{id}/distritos       → distritos de uma cidade
/distritos                       → todos (sync nacional)
```

Flags do módulo (lidas do `.env`):

| Constante | Env | Default |
|---|---|---|
| `USAR_CACHE` | `LOCALIDADES_USAR_CACHE` | `true` |
| `SALVAR` | `LOCALIDADES_SALVAR` | `true` |
| `MIN_BAIRROS` | `LOCALIDADES_MIN_BAIRROS` | `3` |
| `AQUECER_PAUSA_PADRAO` | `AQUECER_PAUSA_SEGUNDOS` | `2` |

Helpers internos relevantes:

```python
_cache(fn, ...)   # executa no banco tolerando CacheIndisponivel (avisa 1x)
_salvar(fn, ...)  # respeita SALVAR=false (avisa 1x e retorna None)
_normalizar(t)    # minúsculas + sem acento
_municipios_da_uf(uf)   # memoizado em memória (evita rebaixar a lista)
```

API pública:

```python
obter_estados() -> DataFrame[uf, nome]
obter_cidades(uf) -> list[str]
obter_bairros(cidade, uf) -> list[str]        # [] = buscar cidade inteira
obter_termos_busca(cidade, uf, max_bairros=30) -> list[str]
obter_municipio(cidade, uf) -> dict|None      # nome oficial + id IBGE
filtrar_cidades(cidades, termo) -> list[str]  # sem acento/caixa
listar_municipios_pendentes(uf) -> list[dict]
aquecer_bairros_uf(uf, cidades=None, max_cidades=0, pausa_segundos=None) -> dict|None
sincronizar_base_localidades() -> bool        # nacional; bloqueada se SALVAR=false
```

### Resolução de bairros (`obter_bairros`)

1. Resolve o município (cache → lista da UF → grava se `SALVAR`).
2. Usa o **nome oficial** do IBGE daqui pra frente.
3. Se `USAR_CACHE` e `bairros_fonte` preenchido → lê `localidades_bairros`.
4. Senão:
   - baixa distritos do IBGE; descarta o distrito-sede (mesmo nome da cidade);
   - se `>= MIN_BAIRROS` → fonte `ibge`, **sem** chamar o OSM;
   - senão → Nominatim (bbox) + Overpass (`place=suburb|neighbourhood|quarter`,
     fallback `admin_level 9/10`);
   - se o OSM falhar (serviço fora) → **não grava** (`fonte=None`), tenta de novo
     na próxima execução.

---

## src/scraper.py — Playwright + anti-bloqueio

```python
extrair_leads_local(nicho, termo_busca, cidade, uf, mostrar_navegador=False) -> list[dict]
rodar_scraper_multithread(nicho, cidade, uf, termos_lista,
                          mostrar_navegador=False, save_callback=None) -> DataFrame
```

- `max_workers = min(3, len(termos_lista))`.
- `save_callback(df)` é chamado a cada área concluída (salvamento incremental).
- Deduplicação intra-execução por `(nome, cidade)`.
- Dict de lead: `nome, telefone, tipo_telefone, whatsapp_link, instagram, site,
  bairro, cidade, estado, nicho`.

Rolagem: `MAX_ROLAGENS = 40`, para após `MAX_RODADAS_ESTAGNADAS = 3` rodadas sem
crescimento.

Anti-captcha:

```python
BloqueioDetectado(termo)      # exceção
_pagina_bloqueada(page, checar_texto=True)
_marcar_bloqueio_global()     # cooldown compartilhado entre threads
_aguardar_cooldown(termo)     # todas as threads esperam
_navegar_com_retry(page, url, tentativas=3, timeout=..., termo=...)
```

Detecção: URL `/sorry/`, seletores de captcha (`#captcha-form`, reCAPTCHA,
hCaptcha) e textos como "unusual traffic" / "tráfego incomum".
Persistindo o bloqueio, **aborta só a área** e preserva os leads já extraídos.

Flags: `CAPTCHA_MAX_TENTATIVAS` (2), `CAPTCHA_PAUSA_SEGUNDOS` (300),
`CAPTCHA_PAUSA_GLOBAL_SEGUNDOS` (180).

---

## src/database.py — leads

`LeadDatabase(db_path="data/leads.duckdb")`

Tabela `leads` — PK (`nome`, `cidade`):

```
nome, telefone, tipo_telefone, whatsapp_link, instagram, site,
bairro, cidade, estado, nicho, status (default 'ativo'),
data_extracao, data_envio_whatsapp, status_whatsapp (default 'pendente')
```

```python
save_leads(df) -> int          # filtra descartados, UPSERT, não apaga log WAHA
get_leads_para_envio(limite)   # ativo + Celular + pendente
marcar_envio(nome, cidade, status_whatsapp)   # 'enviado' grava data
export_to_excel(nicho, cidade) # output/leads_{nicho}_{cidade}.xlsx
close()
```

---

## src/whatsapp.py — WAHA

```python
WAHA_API_URL, WAHA_API_KEY, WAHA_SESSION
WAHA_ATIVO, SOMENTE_ENVIO, WAHA_INTERVALO, WAHA_LIMITE
MENSAGEM_PADRAO
enviar_texto_waha(chat_id, texto, ...)   # POST /api/sendText
disparar_campanha(db, mensagem_template=None, intervalo=13, limite=None)
```

- `chat_id` = `55DDD9XXXXXXXX@c.us` (só 11 dígitos; fixo é rejeitado).
- Placeholders: `{nome}`, `{bairro}`, `{cidade}`.
- `SOMENTE_ENVIO=true` (ou `--so-enviar`) pula o menu e vai direto ao envio.

---

## src/main.py — menu

```
1 - Coletar leads
2 - Enviar mensagens WhatsApp
3 - Sincronizar base de localidades (IBGE)
4 - Aquecer bairros de uma UF (OpenStreetMap)
5 - Sair
```

`coletar_leads()`: UF → cidade (filtro sem acento) → **confirma no IBGE e usa o
nome oficial** → nicho → termos → "Ver navegador?" → scraping → Excel.
````

## File: memory/02-decisoes-e-armadilhas.md
````markdown
# 02 — Decisões Técnicas e Armadilhas

Leia antes de mexer no código. Cada item já custou tempo de depuração.

---

## DuckDB: um processo por arquivo

**O arquivo `data/leads.duckdb` só pode ser aberto por UM processo.** Não existe
"read-only compartilhado" — até `duckdb.connect(..., read_only=True)` falha:

```
IO Error: Cannot open file "...data\leads.duckdb":
O arquivo já está sendo usado por outro processo.
```

Causas mais comuns: **DBeaver conectado**, scraper rodando, notebook aberto.

Consequências no código:
- `localidades_db.conexao()` abre/fecha a cada operação (não mantém aberto).
- `LeadDatabase` mantém aberto durante o scraping — **não** abra outra conexão
  persistente no mesmo processo.
- `CacheIndisponivel` existe para degradar com aviso em vez de quebrar:
  o sistema segue usando as APIs (IBGE/OSM) sem cache.

- ⚠️ **Um WAL pendente (`.wal`) indica dados não consolidados.** Se comitar o
  `.duckdb` com o programa aberto, o `.wal` (ignorado no Git) fica de fora e o
  commit sobe um estado desatualizado. Feche o programa antes de comitar.

---

## IBGE: não existe bairro na API de Localidades

A API retorna **estados, municípios, distritos e subdistritos**. Nada de bairro.

- `distritos` são divisões administrativas; em muitos municípios resumem-se à
  própria sede (mesmo nome da cidade).
- Exemplo real: **Canoas-RS = 1 distrito ("Canoas") e 0 subdistritos**.
- `obter_bairros` descarta o distrito-sede; se sobrarem `< MIN_BAIRROS`,
  complementa com OpenStreetMap.
- Cobertura: ~643 de 5.571 municípios têm distritos suficientes para dispensar OSM.

**Não "conserte" isso achando que é bug.** Para bairros oficiais existiria o
CNEFE 2022 (`ftp.ibge.gov.br/.../Censo_Demografico_2022/Arquivos_CNEFE/CSV/UF/`,
coluna `DSC_LOCALIDADE`, ex. `43_RS.zip` ≈ 236 MB) — **decisão do mantenedor:
não implementar por ora**, evoluir aos poucos.

---

## OpenStreetMap: instável por natureza

Os espelhos do Overpass e o Nominatim respondem `502`, `400` e `ReadTimeout`
com frequência. Regra de ouro:

> Falha de rede **não** significa "cidade sem bairros".

Por isso `_consultar_overpass` retorna `None` (serviço fora) em vez de
`{"elements": []}`, e `_descobrir_bairros` devolve `fonte=None` para **não
gravar** nada. A próxima execução tenta de novo. Se gravasse "cidade", o cache
ficaria envenenado para sempre.

---

## Cache: `bairros_fonte` precisa vir na leitura

Bug corrigido em 2026-10-29: `ler_municipios()` selecionava só
`id_municipio, nome`, então `_resolver_municipio` devolvia `bairros_fonte=None` e
`obter_bairros` **ia à API mesmo com cache quente**. Agora a query inclui
`uf` e `bairros_fonte`.

**Ao criar novas leituras de município, sempre inclua `bairros_fonte`.**

---

## Semântica de escrita (não inverter!)

| Função | Comportamento |
|---|---|
| `salvar_bairros` | **autoritativo** por cidade: remove nomes ausentes **daquela** cidade |
| `salvar_distritos_bulk` | **aditivo**: nunca apaga bairros do OSM |
| `salvar_municipios` | UPSERT — **preserva** `bairros_fonte`/`bairros_atualizado_em` |

Se `salvar_distritos_bulk` virasse autoritativo, destruiria as listas do
OpenStreetMap em toda sincronização.

---

## Flags `LOCALIDADES_*` são independentes

`USAR_CACHE` controla **leitura**; `SALVAR` controla **escrita**.

| USAR_CACHE | SALVAR | Efeito |
|---|---|---|
| true | true | padrão: lê do banco, grava o que faltar |
| false | true | ignora o banco, sempre API e regrava |
| true | false | lê do banco; o que falta vem da API sem gravar |
| false | false | sempre API, banco intocado |

- `SALVAR=false` também desativa a criação de tabelas (`CRIAR_TABELAS`) e os
  menus **3** e **4**.
- As flags são lidas **no import**: mudar o `.env` exige reiniciar o programa.
- Com `USAR_CACHE=false`, cada cidade baixa a lista da UF de novo (exceto pela
  memoização em memória `_municipios_da_uf`, válida só na execução atual).

---

## Cuidados ao editar arquivos (Windows/PowerShell)

- **Nunca** use `Get-Content ... -replace ... | Set-Content` para editar `.py`:
  ele reescreve em ANSI e **corrompe acentuação** (dupla codificação / mojibake).
  Use o editor (edit) ou grave via Python com `encoding="utf-8"`.
- Grave sempre **UTF-8 sem BOM** (BOM quebra a primeira chave do `.env`).
- Para testar, use o interpretador da venv: `venv\Scripts\python.exe`.
  O `python` global do mantenedor é 3.15 e pode não ter as dependências.
- Valide a acentuação após edições em lote: procure caracteres de dupla
  codificação (por exemplo, `A` com til U+00C3 seguido de símbolo de moeda).

---

## `.env` e Git

- `.env` **é ignorado** (contém `WAHA_API_KEY`). `.env.example` **é versionado**.
- Formato: `CHAVE=VALOR`. Comentários só em **linha própria** — comentário na
  mesma linha vira parte do valor (`WAHA_LIMITE= # vazio` → `" # vazio"`).
- Não use `export`/aspas desnecessárias; o loader tira aspas simples/duplas.
- Nunca imprima nem comite segredos.

---

## Scraping: seletores frágeis

Dependem do DOM do Google Maps (podem mudar sem aviso):

| Dado | Seletor |
|---|---|
| lista de resultados | `div[role="feed"]` |
| links de perfis | `a[href*="/maps/place/"]` |
| nome | `h1` (ignora "Resultados" e vazio) |
| endereço | `button[data-item-id="address"]` (`aria-label`) |
| telefone | `button[data-item-id^="phone:tel:"]` (`aria-label`) |
| site | `a[data-item-id="authority"]` |
| Instagram | primeiro `a[href]` contendo `instagram.com` |

Bairro é extraído do endereço: `"Rua X, 123 - Bairro, Cidade - UF"` → parte
entre `" - "` e `","`. Se não casar, `"Não Informado"`.

---

## Concorrência

- `save_callback` é chamado **na thread principal** (dentro do loop de
  `as_completed`), então não há escrita concorrente no DuckDB.
- O cooldown anti-captcha usa `_cooldown_lock` + variável global `_cooldown_ate`.
- `lock` protege a lista `vistos`/`todos_leads`.

---

## Coisas que parecem bug mas não são

- `"IBGE não publica bairros para X"` → cidade com 1 distrito (ver acima).
- `"Base local ... sem bairros (fonte: cidade)"` → já tentou, o OSM não tinha nada.
- `"LOCALIDADES_SALVAR=false: a base local não será alterada"` → modo leitura.
- `"Aviso: base local ... indisponível (arquivo em uso)"` → feche o DBeaver.
````

## File: memory/04-como-contribuir.md
````markdown
# 04 — Como Contribuir: Padrões e Boas Práticas

Este documento detalha os padrões de código, estilo e comunicação esperados
para novas contribuições, visando manter a consistência e facilitar a manutenção.

---

## 1. Organização de Código e Nomenclatura

- **Imports:** Sempre absolutos, começando da raiz `src/`. Ex: `from src.config import ...`.
- **Constantes:** `MAIUSCULAS_COM_UNDERLINE`.
- **Funções privadas (internas ao módulo):** `_nome_da_funcao_privada` (com underscore inicial).
- **Variáveis locais:** `snake_case`.
- **Classes:** `CamelCase`.
- **Parâmetros de função:** `snake_case`.

---

## 2. Logs e Interação com o Usuário

- **Prints de progresso:** Use `print(f"[{area_da_busca}] Mensagem...")`.
  O `[área]` (ex: `[Canoas-RS]`, `[Assis Brasil]`) ajuda a identificar qual thread
  ou cidade está processando no momento.
- **Mensagens de erro:** Inclua `type(e).__name__` e `str(e)[:N]` para facilitar
  a depuração em ambientes remotos ou com logs limitados.
- **Interação:** Use `input()` para entradas do usuário no console. Evite `print()`
  seguido de `input()` em linhas separadas para prompts, a menos que seja intencional.
- **Mensagens para o usuário:** Devem ser claras e úteis, preferencialmente
  em português (padrão atual do projeto).

---

## 3. Variáveis de Ambiente e Configuração

- **Todas as configurações** devem ser lidas do `.env` via `src/config.py`.
- **Nunca faça hardcode** de URLs de APIs, chaves, limites, etc.
- **Novas variáveis:** Adicione ao `.env.example` com comentários explicativos.
- **Semântica:** Use `true`/`false` para booleanos, números para inteiros.
  O `src/config.py` já tem helpers para isso (`str_para_bool`, `env_int`).

---

## 4. Testes e Validação

- **Testes unitários/de integração:** Idealmente, adicione pequenos scripts de
  validação (como os que o modelo Gemini tem feito) para cobrir novas features
  ou refatorações.
- **DuckDB:** Para testes que não devem tocar no banco real, use um arquivo
  DuckDB temporário (`tempfile.gettempdir()`) e defina `localidades_db.DB_PATH_PADRAO`.
- **Encoding:** Mantenha os arquivos em **UTF-8 sem BOM**.
  Valide a acentuação após edições em lote: procure caracteres de dupla
  codificação (por exemplo, `A` com til U+00C3 seguido de símbolo de moeda).

---

## 5. Documentação

- **`README.md` (raiz):** Manual do usuário, instalação, execução, fluxo geral.
- **`memory/`:** Resumos densos para modelos de IA. **Atualize ao mudar comportamento**.
  - `00-resumo-projeto.md`: alto nível.
  - `01-arquitetura-e-modulos.md`: detalhe de cada módulo.
  - `02-decisoes-e-armadilhas.md`: o "porquê" das decisões, bugs conhecidos.
  - `03-historico-de-mudancas.md`: log recente das mudanças importantes.
- **Docstrings:** Use docstrings Python para explicar funções e classes.
- **Comentários de código:** Breves e pontuais, explicando lógica complexa ou escolhas não óbvias.
````

## File: output/teste.txt
````

````

## File: src/__init__.py
````python

````

## File: src/config.py
````python
# src/config.py
"""Carregamento centralizado do arquivo .env e leitura de flags.

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
````

## File: src/utils.py
````python
# src/utils.py
import re

def formatar_telefone(telefone_bruto):
    """
    Limpa o telefone, identifica o tipo e gera o link do WhatsApp.
    Retorna: (telefone_limpo, tipo, whatsapp_link)
    """
    if not telefone_bruto:
        return "", "Não Informado", ""
    
    # Remove tudo que não for número
    apenas_numeros = re.sub(r'\D', '', str(telefone_bruto))
    
    # Se o número já vier com DDI (55) e tiver 12 ou 13 dígitos, removemos o 55 
    # temporariamente para classificar o tipo corretamente (Fixo/Celular)
    if apenas_numeros.startswith('55') and len(apenas_numeros) > 11:
        numero_sem_ddi = apenas_numeros[2:]
    else:
        numero_sem_ddi = apenas_numeros

    # Classificação e formatação do Link
    if len(numero_sem_ddi) == 11: # Celular com 9 dígito
        tipo = "Celular"
        whatsapp_link = f"https://wa.me/55{numero_sem_ddi}"
    elif len(numero_sem_ddi) == 10: # Fixo
        tipo = "Fixo"
        whatsapp_link = f"https://wa.me/55{numero_sem_ddi}"
    elif len(apenas_numeros) > 0:
        tipo = "Desconhecido"
        whatsapp_link = f"https://wa.me/{apenas_numeros}"
    else:
        return "", "Não Informado", ""
        
    # Retorna apenas os números na coluna telefone, o tipo e o link pronto
    return apenas_numeros, tipo, whatsapp_link
````

## File: .gitkeep
````

````

## File: requirements.txt
````
pandas
openpyxl
instagpy
pip-system-certs
playwright
chromium
geopy
duckdb
requests
````

## File: memory/03-historico-de-mudancas.md
````markdown
# 03 — Histórico de Mudanças

Registro do que mudou, por quê e o que ficou pendente. Mais recente primeiro.

---

## 2026-10-29

### Memória do projeto para IA

- Criada a pasta `memory/` com documentação densa para reduzir custo de contexto.
- Arquivos: `README.md`, `00-resumo-projeto.md`, `01-arquitetura-e-modulos.md`,
  `02-decisoes-e-armadilhas.md`, `03-historico-de-mudancas.md`,
  `04-como-contribuir.md` (padrões de código, logs, config, testes e docs).
- `README.md` limpo: removido o bloco "env temp:" (dump cru do `.env`) e
  adicionadas as seções 12 (memória para IA) e 13 (observação sobre configuração).

### Correção: cache de bairros ignorado (`bairros_fonte`)

- **Sintoma:** com `LOCALIDADES_USAR_CACHE=true` e base populada, a coleta ainda
  consultava IBGE e Overpass.
- **Causa:** `localidades_db.ler_municipios()` não retornava `bairros_fonte`;
  `_resolver_municipio` repassava `None`, então o cache nunca era considerado.
- **Correção:** query passou a trazer `uf` e `bairros_fonte`; o resolver repassa
  o valor real.
- **Teste:** com as funções de rede trocadas por `AssertionError`, os bairros de
  Canoas (fonte `overpass`) e Bento Gonçalves (fonte `ibge`) vieram do banco.

### Nome oficial do município (IBGE) na coleta

- `obter_municipio(cidade, uf)` confirma o município e devolve `id_municipio`,
  `nome` oficial e `uf`.
- `filtrar_cidades(cidades, termo)` compara **sem acento e sem caixa**:
  `canoas`, `sao leopoldo`, `CHAPECO` funcionam.
- `main.coletar_leads()` passa a usar o nome oficial no scraping, no banco e no
  nome do Excel, e imprime `Município (IBGE): Canoas-RS | código 4304606`.
- Lista de municípios **memoizada** por execução (`_municipios_da_uf`), evitando
  rebaixar a lista da UF a cada cidade (principalmente com `SALVAR=false`).

### Mensagens de bairros mais honestas

- Antes: `IBGE retornou 0 distrito(s) útil(eis)`.
- Agora: `IBGE não publica bairros para Canoas-RS: o município tem apenas 1 distrito (a sede).`
- Motivo: a API de Localidades do IBGE **não tem bairros** (só distritos).

### Aquecimento de bairros por UF (menu 4)

- `locations.aquecer_bairros_uf(uf, cidades=None, max_cidades=0, pausa_segundos=None)`.
- `localidades_db.ler_municipios_pendentes(uf)` → só `bairros_fonte IS NULL`.
- Retoma de onde parou; `Ctrl+C` preserva o que já foi gravado.
- Pausa (`AQUECER_PAUSA_SEGUNDOS`, default 2) só quando a cidade usou o OSM.
- Falha de rede não grava nada (`falhas` no resumo) e a cidade continua pendente.
- Bloqueado quando `LOCALIDADES_SALVAR=false`.
- Medido: AC 21 → 18 → 17 pendentes; SP 621 → 616.

### Flag `LOCALIDADES_SALVAR`

- `false` = somente leitura: nenhuma escrita, **nem criação de tabelas**
  (`localidades_db.CRIAR_TABELAS = False`) e menus 3/4 desativados.
- Todas as escritas passam por `_salvar()`, que respeita a flag.
- Aviso único por execução para não poluir o log.

### `.env` e `.env.example` comentados

- Cada variável com explicação, faixa de valores e efeito colateral.
- Tabela das 4 combinações `USAR_CACHE × SALVAR`.
- Regra explícita: comentário só em linha própria.
- Valores locais preservados (`USAR_CACHE=false` → depois `true`).

### Base de localidades offline (IBGE) — menu 3

- Novo `src/localidades_db.py` com tabelas `localidades_estados`,
  `localidades_municipios`, `localidades_bairros` no mesmo `leads.duckdb`.
- `src/config.py` centraliza o loader do `.env` (antes duplicado no `whatsapp.py`).
- `src/locations.py` reescrito: cache → API → grava.
- Sync nacional: 27 estados, 5.571 municípios, 10.751 distritos; 643 cidades com
  bairros prontos pelo IBGE.
- Fallback OSM por cidade, gravado uma única vez.

### Anti-captcha / bloqueio do Google Maps

- Detecção por URL `/sorry/`, seletores de captcha e textos ("tráfego incomum").
- Retry com pausa longa (`CAPTCHA_PAUSA_SEGUNDOS`) e **cooldown global**
  (`CAPTCHA_PAUSA_GLOBAL_SEGUNDOS`) entre todas as threads.
- Bloqueio persistente → aborta a área e **preserva os leads já extraídos**.
- Testado com Playwright real: página normal passa, página de captcha levanta
  `BloqueioDetectado` após `CAPTCHA_MAX_TENTATIVAS`.

### Correção: menu não aparecia

- `src/main.py` definia `menu_interativo()` mas **nunca chamava**.
- Adicionado `if __name__ == "__main__": menu_interativo()`.

### Banco DuckDB versionado

- `data/leads.duckdb` passou a ser versionado no Git.
- `.gitignore`: removidos `data/` e `*.duckdb` da lista de ignore; adicionados
  `*.duckdb.wal` e `*.duckdb.tmp`.
- `*.xlsx`, `*.csv`, `*.log` continuam ignorados (confirmado com
  `git check-ignore` e `git ls-files`).
- ⚠️ Comitar com o programa aberto sobe o `.duckdb` sem o `.wal` (dados
  desatualizados). Fechar antes.

---

## Pendências / próximos passos

| Item | Status |
|---|---|
| Bairros oficiais via CNEFE 2022 | **Não implementar por ora** (decisão do mantenedor) |
| Resolução automática de captcha (2Captcha/CapMonster) | Não implementado; hoje pausa e desiste da área |
| Enriquecimento de e-mail a partir dos sites | Não iniciado |
| Base de bairros offline nacional | Coberto parcialmente pelo IBGE (643 cidades) |

## Problemas conhecidos (ambiente)

- **DBeaver aberto trava o DuckDB** → cache cai para as APIs.
- **Overpass/Nominatim instáveis** (502, timeout) → aquecimento por UF precisa de
  paciência e retomadas.
- Interprete global do mantenedor é Python 3.15; **usar `venv\Scripts\python.exe`**.
````

## File: memory/README.md
````markdown
# memory/ — Memória do Projeto para IAs

Esta pasta contém documentação **resumida e densa** sobre o projeto Map Scraper,
escrita para ser lida por modelos de IA antes de alterar código.

## Por que existe

Ler esses arquivos curtos daqui custa muito menos tokens do que reler todo o código.
Use esta pasta como **primeira fonte de contexto**.

## Ordem de leitura recomendada

| # | Arquivo | Conteúdo |
|---|---|---|
| 1 | [00-resumo-projeto.md](./00-resumo-projeto.md) | O que o projeto faz, stack, estrutura |
| 2 | [01-arquitetura-e-modulos.md](./01-arquitetura-e-modulos.md) | Cada módulo, funções principais, fluxos |
| 3 | [02-decisoes-e-armadilhas.md](./02-decisoes-e-armadilhas.md) | Decisões técnicas, bugs conhecidos, cuidados |
| 4 | [03-historico-de-mudancas.md](./03-historico-de-mudancas.md) | O que mudou recentemente e por quê |
| 5 | [04-como-contribuir.md](./04-como-contribuir.md) | Padrões de código, logs, config, testes e documentação |

## Regras de manutenção

- **Atualize ao mudar comportamento**, não a cada commit.
- Mantenha cada arquivo curto (ideal: < 200 linhas). Detalhe fica no código.
- Registre o **porquê** das decisões, não só o quê.
- Nunca coloque segredos aqui (API keys, tokens). Use `.env`.
- Datas no formato `AAAA-MM-DD`.

## Arquivos que NÃO devem ser duplicados aqui

- `README.md` (raiz) — manual do usuário, instalação, uso.
- `.env.example` — valores e comentários de cada variável.
````

## File: src/database.py
````python
# src/database.py
import duckdb
import pandas as pd
import os
from datetime import datetime

class LeadDatabase:
    def __init__(self, db_path="data/leads.duckdb"):
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        self.db_path = db_path
        self.conn = duckdb.connect(self.db_path)
        self._create_table()
        self._ensure_whatsapp_columns()

    def _create_table(self):
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS leads (
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
                PRIMARY KEY (nome, cidade)
            )
        """)

    def _ensure_whatsapp_columns(self):
        """Adiciona as colunas de log de WhatsApp em bancos criados antes da migração."""
        colunas = {row[1] for row in self.conn.execute("PRAGMA table_info(leads)").fetchall()}
        if 'data_envio_whatsapp' not in colunas:
            self.conn.execute("ALTER TABLE leads ADD COLUMN data_envio_whatsapp TIMESTAMP")
        if 'status_whatsapp' not in colunas:
            self.conn.execute("ALTER TABLE leads ADD COLUMN status_whatsapp VARCHAR DEFAULT 'pendente'")

    def save_leads(self, df: pd.DataFrame):
        if df.empty:
            return 0
        
        descartados_db = self.conn.execute("SELECT nome, cidade FROM leads WHERE status = 'descartado'").fetchall()
        descartados_set = set(descartados_db)
        
        df = df[~df.apply(lambda row: (row['nome'], row['cidade']) in descartados_set, axis=1)]
        
        if df.empty:
            print("Todos os leads coletados já foram descartados anteriormente. Pulando salvamento.")
            return 0
            
        df['data_extracao'] = datetime.now()
        
        if 'status' not in df.columns:
            df['status'] = 'ativo'

        self.conn.register('df_temp', df)

        # UPSERT preservando o status atual e as colunas de log do WhatsApp.
        # Assim, re-raspar um lead já enviado NÃO apaga data_envio_whatsapp/status_whatsapp.
        self.conn.execute("""
            INSERT INTO leads (nome, telefone, tipo_telefone, whatsapp_link, instagram, site, bairro, cidade, estado, nicho, status, data_extracao)
            SELECT nome, telefone, tipo_telefone, whatsapp_link, instagram, site, bairro, cidade, estado, nicho, status, data_extracao
            FROM df_temp
            ON CONFLICT (nome, cidade) DO UPDATE SET
                telefone = excluded.telefone,
                tipo_telefone = excluded.tipo_telefone,
                whatsapp_link = excluded.whatsapp_link,
                instagram = excluded.instagram,
                site = excluded.site,
                bairro = excluded.bairro,
                estado = excluded.estado,
                nicho = excluded.nicho,
                data_extracao = excluded.data_extracao
        """)

        self.conn.unregister('df_temp')
        return len(df)

    def get_leads_para_envio(self, limite=None):
        """Retorna leads ativos, celulares e ainda não enviados (evita spam/fixo)."""
        query = """
            SELECT nome, telefone, whatsapp_link, bairro, cidade, estado, nicho
            FROM leads
            WHERE status = 'ativo'
              AND tipo_telefone = 'Celular'
              AND (status_whatsapp IS NULL OR status_whatsapp = 'pendente')
            ORDER BY cidade, bairro, nome
        """
        if limite:
            query += f" LIMIT {int(limite)}"
        return self.conn.execute(query).df()

    def marcar_envio(self, nome, cidade, status_whatsapp):
        """Registra o resultado do envio. 'data_envio_whatsapp' é gravado apenas no sucesso."""
        if status_whatsapp == 'enviado':
            self.conn.execute("""
                UPDATE leads
                SET status_whatsapp = ?, data_envio_whatsapp = ?
                WHERE nome = ? AND cidade = ?
            """, [status_whatsapp, datetime.now(), nome, cidade])
        else:
            self.conn.execute("""
                UPDATE leads
                SET status_whatsapp = ?
                WHERE nome = ? AND cidade = ?
            """, [status_whatsapp, nome, cidade])

    def export_to_excel(self, nicho: str, cidade: str):
        df = self.conn.execute("""
            SELECT nome, telefone, tipo_telefone, whatsapp_link, instagram, site, bairro, data_extracao 
            FROM leads 
            WHERE nicho = ? AND cidade = ? AND status = 'ativo'
            ORDER BY bairro, nome
        """, [nicho, cidade]).df()
        
        if df.empty:
            print("Nenhum dado ativo para exportar.")
            return
            
        os.makedirs("output", exist_ok=True)
        nome_arquivo = f"output/leads_{nicho}_{cidade}.xlsx".replace(" ", "_").lower()
        df.to_excel(nome_arquivo, index=False)
        print(f"🎉 Exportação concluída: {nome_arquivo} ({len(df)} leads ativos)")

    def close(self):
        self.conn.close()
````

## File: src/whatsapp.py
````python
# src/whatsapp.py
"""Integração com a WAHA (WhatsApp HTTP API) para envio de mensagens aos leads.

Configuração via variáveis de ambiente:
    WAHA_API_URL   -> URL base da WAHA (padrão: http://localhost:3000)
    WAHA_API_KEY   -> chave de API da WAHA (obrigatória se a instância exigir)
    WAHA_SESSION   -> nome da sessão conectada na WAHA (padrão: "default")

O módulo só envia para leads:
    - status = 'ativo'
    - tipo_telefone = 'Celular'  (nunca fixo)
    - ainda não enviados (status_whatsapp = 'pendente' ou NULL)
"""
import os
import re
import time

import requests

from src.config import carregar_env, str_para_bool

carregar_env()

WAHA_API_URL = os.environ.get("WAHA_API_URL", "http://localhost:3000")
WAHA_API_KEY = os.environ.get("WAHA_API_KEY", "")
WAHA_SESSION = os.environ.get("WAHA_SESSION", "default")

# Se false, o módulo NÃO tenta enviar (desliga o envio de WhatsApp).
WAHA_ATIVO = str_para_bool(os.environ.get("WAHA_ATIVO"), padrao=True)

# Se true, pula a coleta e vai direto para o envio (não coleta nada).
SOMENTE_ENVIO = str_para_bool(os.environ.get("SOMENTE_ENVIO"), padrao=False)

# Intervalo (segundos) entre envios e limite de leads por campanha.
# WAHA_LIMITE vazio = sem limite (envia todos os pendentes).
WAHA_INTERVALO = int(os.environ.get("WAHA_INTERVALO", "13"))
WAHA_LIMITE = os.environ.get("WAHA_LIMITE", "").strip()
WAHA_LIMITE = int(WAHA_LIMITE) if WAHA_LIMITE else None

# Mensagem padrão (placeholder). Use {nome}, {bairro} e {cidade}.
MENSAGEM_PADRAO = "Olá {nome}! Vi que vocês atendem no bairro {bairro}, em {cidade}. Podemos conversar?"


def _normalizar_chatid(telefone):
    """Converte o telefone salvo em um chatId do WAHA (55DDDNUMERO@c.us)."""
    numero = re.sub(r"\D", "", str(telefone or ""))
    if not numero:
        return None

    # Se veio com DDI 55 e tem mais de 11 dígitos, remove o prefixo.
    if numero.startswith("55") and len(numero) > 11:
        numero = numero[2:]

    # Celular brasileiro tem 11 dígitos (DDD + 9 dígitos).
    if len(numero) != 11:
        return None

    return f"55{numero}@c.us"


def _renderizar_mensagem(template, lead):
    """Substitui {nome}, {bairro} e {cidade} de forma segura (sem quebrar com chaves soltas)."""
    bairro = str(lead.get("bairro") or "sua região")
    cidade = str(lead.get("cidade") or "")
    return (
        template
        .replace("{nome}", str(lead.get("nome") or ""))
        .replace("{bairro}", bairro)
        .replace("{cidade}", cidade)
    )


def enviar_texto_waha(chat_id, texto, session=None, api_url=None, api_key=None):
    """Envia uma mensagem de texto via WAHA."""
    session = session or WAHA_SESSION
    api_url = api_url or WAHA_API_URL
    api_key = api_key if api_key is not None else WAHA_API_KEY
    url = f"{api_url.rstrip('/')}/api/sendText"

    payload = {
        "session": session,
        "chatId": chat_id,
        "text": texto,
    }

    headers = {"Accept": "application/json", "Content-Type": "application/json"}
    if api_key:
        headers["X-Api-Key"] = api_key

    response = requests.post(url, json=payload, headers=headers, timeout=30)
    response.raise_for_status()
    return response.json()


def disparar_campanha(db, mensagem_template=None, intervalo=13, limite=None):
    """Envia mensagens para todos os leads celulares pendentes.

    - db: instância de LeadDatabase
    - mensagem_template: texto com {nome}, {bairro}, {cidade} (usa MENSAGEM_PADRAO se None)
    - intervalo: pausa em segundos entre envios (evita spam e banimento)
    """
    mensagem_template = mensagem_template or MENSAGEM_PADRAO
    leads = db.get_leads_para_envio(limite)

    if leads.empty:
        print("Nenhum lead celular pendente de envio.")
        return

    total = len(leads)
    print(f"Enviando para {total} lead(s) celular(es), com intervalo de {intervalo}s...")

    for i, (_, lead) in enumerate(leads.iterrows(), 1):
        chat_id = _normalizar_chatid(lead.get("telefone"))
        if not chat_id:
            db.marcar_envio(lead["nome"], lead["cidade"], "falhou")
            print(f"[{i}/{total}] {lead['nome']} - telefone inválido, marcado como falhou.")
            continue

        texto = _renderizar_mensagem(mensagem_template, lead)

        try:
            enviar_texto_waha(chat_id, texto)
            db.marcar_envio(lead["nome"], lead["cidade"], "enviado")
            print(f"[{i}/{total}] ENVIADO -> {lead['nome']} ({chat_id})")
        except Exception as e:
            db.marcar_envio(lead["nome"], lead["cidade"], "falhou")
            print(f"[{i}/{total}] FALHOU -> {lead['nome']} ({chat_id}): {e}")

        if i < total:
            time.sleep(intervalo)

    print("Campanha finalizada.")
````

## File: src/localidades_db.py
````python
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
````

## File: .env.example
````
# =============================================================================
# MAP SCRAPER - arquivo de exemplo de configuração
# -----------------------------------------------------------------------------
# Copie para `.env` e ajuste:
#     Copy-Item .env.example .env
#
# REGRAS IMPORTANTES
#  - Formato: CHAVE=VALOR, uma por linha.
#  - Comentários (linhas que começam com #) podem ficar à vontade, mas SEMPRE em
#    linha própria. Não coloque comentário na mesma linha do valor, porque ele
#    seria lido como parte do valor.
#  - true/false: também aceita 1/0, sim/não, s/yes/on.
#  - O arquivo `.env` NÃO é versionado no Git (contém a API key da WAHA).
# =============================================================================


# =============================================================================
# WHATSAPP - WAHA (WhatsApp HTTP API)
# =============================================================================

# URL base da sua instância WAHA (Docker local, por exemplo).
# Usada em todas as chamadas de envio. Não coloque a barra final.
WAHA_API_URL=http://localhost:3000

# Chave de API da WAHA. É o valor de WHATSAPP_API_KEY no .env do Docker/init-waha.
# Deixe vazio se a sua instância estiver sem autenticação.
WAHA_API_KEY=

# Nome da sessão do WhatsApp já conectada (lida por QR Code), normalmente `default`.
# Precisa ser exatamente o nome que aparece em /api/sessions da WAHA.
WAHA_SESSION=default

# Liga/desliga TODO o envio de WhatsApp.
#   true  = o menu "2 - Enviar mensagens WhatsApp" funciona normalmente.
#   false = o menu avisa que o envio está desativado e não faz nada.
# Isso NÃO afeta a coleta de leads, apenas o disparo de mensagens.
WAHA_ATIVO=true

# Atalho que pula o menu e vai direto para o envio, sem coletar nada.
#   true  = equivale a rodar: python src/main.py --so-enviar
#   false = abre o menu normal (coleta + envio).
# Útil para rodar uma campanha agendada, por exemplo.
SOMENTE_ENVIO=false

# Pausa em SEGUNDOS entre um envio e o próximo (13s ≈ 4-5 mensagens por minuto).
# Pausas muito curtas aumentam o risco de banimento do número.
WAHA_INTERVALO=13

# Quantidade máxima de leads por campanha. Vazio = sem limite (envia todos
# os pendentes). Só conta leads celulares, ativos e ainda não enviados.
WAHA_LIMITE=


# =============================================================================
# BASE DE LOCALIDADES (IBGE) - cache em DuckDB: tabelas localidades_*
# -----------------------------------------------------------------------------
# As duas flags abaixo são independentes. Combinações possíveis:
#
#   USAR_CACHE  SALVAR   O que acontece
#   true        true     usa o banco; só vai à API do que falta e grava (padrão)
#   false       true     ignora o banco, sempre vai à API e regrava (força refresh)
#   true        false    usa o banco; o que falta vai à API mas NÃO é gravado
#   false       false    sempre API, e o banco nunca é tocado (somente leitura)
# =============================================================================

# Consultar a base local ANTES da API do IBGE?
#   true  = se o dado já existe no DuckDB, nem chama a internet (rápido).
#   false = sempre chama a API do IBGE, mesmo que o dado já esteja no banco.
LOCALIDADES_USAR_CACHE=true

# Permitir GRAVAR na base local?
#   true  = pode inserir/atualizar (UPSERT) os estados, municípios e bairros.
#   false = modo somente leitura: nada é gravado e nem as tabelas são criadas.
# ATENÇÃO: com false, os menus "3 - Sincronizar" e "4 - Aquecer bairros" ficam
# desativados, e cada execução consulta as APIs de novo.
LOCALIDADES_SALVAR=true

# Mínimo de distritos do IBGE para considerar a cidade "coberta" pelo IBGE.
# A API de Localidades do IBGE tem distritos (não bairros). Cidade com menos
# distritos que este número é complementada com o OpenStreetMap.
# Exemplo: Campinas-SP tem 7 distritos -> usa só o IBGE.
#          Canoas-RS tem 1 distrito (a sede) -> vai para o OpenStreetMap.
LOCALIDADES_MIN_BAIRROS=3

# Pausa em SEGUNDOS entre cidades no menu "4 - Aquecer bairros de uma UF".
# Só é aplicada quando a cidade precisou do OpenStreetMap (Nominatim permite
# ~1 requisição por segundo). Cidades resolvidas pelo IBGE não esperam.
AQUECER_PAUSA_SEGUNDOS=2


# =============================================================================
# GOOGLE MAPS - captcha / bloqueio ("tráfego incomum")
# -----------------------------------------------------------------------------
# Quando o Google bloqueia, o robô pausa e tenta de novo. Se continuar bloqueado,
# ele aborta APENAS aquela área e mantém os leads já coletados.
# =============================================================================

# Quantas tentativas por página antes de desistir da área.
#   1  = não tenta de novo, só pausa uma vez e desiste.
#   2  = pausa e tenta mais uma vez (padrão).
# Valores altos aumentam o risco de piorar o bloqueio.
CAPTCHA_MAX_TENTATIVAS=2

# Pausa longa em SEGUNDOS feita pela thread que recebeu o captcha antes de
# tentar a mesma página novamente.
CAPTCHA_PAUSA_SEGUNDOS=300

# Pausa compartilhada em SEGUNDOS aplicada a TODAS as threads assim que uma
# delas detecta bloqueio (evita que as outras continuem martelando o Google).
CAPTCHA_PAUSA_GLOBAL_SEGUNDOS=180
````

## File: src/scraper.py
````python
# src/scraper.py
from playwright.sync_api import sync_playwright
import time
import random
import urllib.parse
from concurrent.futures import ThreadPoolExecutor, as_completed
import pandas as pd
import threading
from src.config import env_int
from src.utils import formatar_telefone

lock = threading.Lock()

USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/124.0.0.0 Safari/537.36"
)

MAX_ROLAGENS = 40
MAX_RODADAS_ESTAGNADAS = 3

# --- Anti-bloqueio (captcha) -------------------------------------------------
# CAPTCHA_MAX_TENTATIVAS: quantas vezes uma mesma página é tentada antes de
#   abortar a área (1 = nem tenta de novo, só pausa e desiste).
# CAPTCHA_PAUSA_SEGUNDOS: pausa longa feita pela thread que levou o bloqueio.
# CAPTCHA_PAUSA_GLOBAL_SEGUNDOS: pausa compartilhada, aplicada a TODAS as
#   threads assim que uma delas detecta bloqueio (evita que as outras insistam).
CAPTCHA_MAX_TENTATIVAS = max(1, env_int("CAPTCHA_MAX_TENTATIVAS", 2))
CAPTCHA_PAUSA_SEGUNDOS = max(0, env_int("CAPTCHA_PAUSA_SEGUNDOS", 300))
CAPTCHA_PAUSA_GLOBAL_SEGUNDOS = max(0, env_int("CAPTCHA_PAUSA_GLOBAL_SEGUNDOS", 180))

_MARCADORES_CAPTCHA = (
    "unusual traffic",
    "tráfego incomum",
    "trafego incomum",
    "não é possível acessar",
    "nao e possivel acessar",
    "our systems have detected",
    "digite os caracteres",
    "não sou um robô",
    "i'm not a robot",
)

_SELETORES_BLOQUEIO = (
    'form[action*="sorry"]',
    "#captcha-form",
    "#recaptcha",
    ".g-recaptcha",
    'iframe[src*="recaptcha"]',
    'iframe[src*="hcaptcha"]',
)

_cooldown_ate = 0.0
_cooldown_lock = threading.Lock()


class BloqueioDetectado(Exception):
    """Google Maps devolveu captcha/tela de bloqueio para a busca atual."""


def _montar_query(nicho, termo_busca, cidade, uf):
    if termo_busca.strip().lower() == cidade.strip().lower():
        return f"{nicho} em {cidade}, {uf}"
    return f"{nicho} em {termo_busca}, {cidade}, {uf}"


def _pagina_bloqueada(page, checar_texto=True):
    """Detecta captcha / tela de 'tráfego incomum' do Google."""
    try:
        url = (page.url or "").lower()
    except Exception:
        return False
    if "/sorry/" in url:
        return True

    try:
        for seletor in _SELETORES_BLOQUEIO:
            if page.query_selector(seletor):
                return True
    except Exception:
        return False

    if not checar_texto:
        return False

    try:
        texto = (page.inner_text("body") or "")[:4000].lower()
    except Exception:
        return False
    return any(marcador in texto for marcador in _MARCADORES_CAPTCHA)


def _marcar_bloqueio_global():
    """Coloca todas as threads em pausa (cooldown compartilhado)."""
    global _cooldown_ate
    if CAPTCHA_PAUSA_GLOBAL_SEGUNDOS <= 0:
        return
    with _cooldown_lock:
        _cooldown_ate = max(_cooldown_ate, time.time() + CAPTCHA_PAUSA_GLOBAL_SEGUNDOS)


def _aguardar_cooldown(termo):
    """Espera o cooldown global, se alguma thread detectou bloqueio."""
    with _cooldown_lock:
        restante = _cooldown_ate - time.time()
    if restante <= 0:
        return

    print(f"[{termo}] Pausa global anti-bloqueio: aguardando {int(restante) + 1}s...")
    while restante > 0:
        time.sleep(min(restante, 10))
        with _cooldown_lock:
            restante = _cooldown_ate - time.time()


def _pausar_com_aviso(segundos, termo):
    print(f"[{termo}] Aguardando {segundos}s (pausa longa anti-bloqueio)...")
    restante = segundos
    while restante > 0:
        passo = min(restante, 15)
        time.sleep(passo)
        restante -= passo


def _navegar_com_retry(page, url, tentativas=3, timeout=30000, termo="?"):
    """Navega com retry e backoff; detecta captcha e aplica pausa longa.

    Levanta BloqueioDetectado quando o bloqueio persiste após as tentativas.
    """
    for tentativa in range(1, tentativas + 1):
        _aguardar_cooldown(termo)
        try:
            page.goto(url, timeout=timeout)
        except Exception as e:
            print(f"  Retry {tentativa}/{tentativas} ao navegar para {url}: {type(e).__name__}")
            time.sleep(2 * tentativa)
            continue

        if not _pagina_bloqueada(page):
            return True

        _marcar_bloqueio_global()
        print(f"[{termo}] ⚠ Google Maps bloqueou o acesso (captcha/tráfego incomum).")

        if tentativa >= min(tentativas, CAPTCHA_MAX_TENTATIVAS):
            print(f"[{termo}] Bloqueio persistente após {tentativa} tentativa(s). Abortando esta área.")
            raise BloqueioDetectado(termo)

        _pausar_com_aviso(CAPTCHA_PAUSA_SEGUNDOS, termo)

    return False


def _obter_urls_perfis(page):
    urls = set()
    for link in page.query_selector_all('a[href*="/maps/place/"]'):
        href = link.get_attribute('href')
        if href:
            urls.add(href)
    return urls


def _rolar_resultados(page, termo="?"):
    """Rola a lista até esgotar os resultados (ou atingir o limite de rolagens)."""
    ultimo_total = 0
    rodadas_estagnadas = 0
    for _ in range(MAX_ROLAGENS):
        if _pagina_bloqueada(page, checar_texto=False):
            _marcar_bloqueio_global()
            raise BloqueioDetectado(termo)

        total = len(_obter_urls_perfis(page))
        page.evaluate('''() => {
            const feed = document.querySelector('div[role="feed"]');
            if(feed) feed.scrollTop = feed.scrollHeight;
        }''')
        time.sleep(1.0 + random.uniform(0, 0.6))  # jitter anti-bloqueio

        if total == ultimo_total:
            rodadas_estagnadas += 1
            if rodadas_estagnadas >= MAX_RODADAS_ESTAGNADAS:
                break
        else:
            rodadas_estagnadas = 0
        ultimo_total = total


def extrair_leads_local(nicho, termo_busca, cidade, uf, mostrar_navegador=False):
    query = _montar_query(nicho, termo_busca, cidade, uf)
    url = f"https://www.google.com/maps/search/{urllib.parse.quote(query)}"
    leads = []

    p = sync_playwright().start()
    browser = None
    try:
        browser = p.chromium.launch(headless=not mostrar_navegador)
        context = browser.new_context(
            user_agent=USER_AGENT,
            viewport={"width": 1366, "height": 768},
            locale="pt-BR",
        )
        page = context.new_page()

        if not _navegar_com_retry(page, url, timeout=60000, termo=termo_busca):
            print(f"[{termo_busca}] Falha ao carregar a busca.")
            return leads

        try:
            page.wait_for_selector('div[role="feed"]', timeout=10000)
        except Exception:
            print(f"[{termo_busca}] Nenhum resultado encontrado.")
            return leads

        print(f"[{termo_busca}] Rolando resultados...")
        _rolar_resultados(page, termo_busca)

        if _pagina_bloqueada(page):
            _marcar_bloqueio_global()
            raise BloqueioDetectado(termo_busca)

        urls = sorted(_obter_urls_perfis(page))
        print(f"[{termo_busca}] {len(urls)} perfis encontrados. Extraindo dados...")

        for i, place_url in enumerate(urls):
            try:
                time.sleep(random.uniform(0.8, 2.5))  # pausa anti-bloqueio entre navegações
                if not _navegar_com_retry(page, place_url, timeout=30000, termo=termo_busca):
                    continue
                time.sleep(random.uniform(1.2, 2.8))

                nome_elem = page.query_selector('h1')
                nome = nome_elem.inner_text() if nome_elem else "Sem nome"
                if nome in ("Resultados", ""):
                    continue

                # Extração do Bairro (Endereço)
                bairro_real = "Não Informado"
                endereco_elem = page.query_selector('button[data-item-id="address"]')
                if endereco_elem:
                    aria_endereco = endereco_elem.get_attribute('aria-label')
                    if aria_endereco:
                        texto_limpo = aria_endereco.replace('Endereço:', '').replace('Address:', '').strip()
                        try:
                            parts = texto_limpo.split(" - ")
                            if len(parts) >= 2:
                                bairro_real = parts[1].split(",")[0].strip()
                        except Exception:
                            pass

                # Extração do Telefone
                telefone_bruto = ""
                tel_elem = page.query_selector('button[data-item-id^="phone:tel:"]')
                if tel_elem:
                    aria = tel_elem.get_attribute('aria-label')
                    if aria:
                        telefone_bruto = aria.replace('Telefone:', '').replace('Phone:', '').strip()

                telefone_limpo, tipo_telefone, whatsapp_link = formatar_telefone(telefone_bruto)

                link_site = ""
                link_insta = ""

                site_elem = page.query_selector('a[data-item-id="authority"]')
                if site_elem:
                    link_site = site_elem.get_attribute('href')

                for a in page.query_selector_all('a'):
                    href = a.get_attribute('href')
                    if href and "instagram.com" in href:
                        link_insta = href
                        break

                leads.append({
                    'nome': nome,
                    'telefone': telefone_limpo,
                    'tipo_telefone': tipo_telefone,
                    'whatsapp_link': whatsapp_link,
                    'instagram': link_insta,
                    'site': link_site,
                    'bairro': bairro_real,
                    'cidade': cidade,
                    'estado': uf,
                    'nicho': nicho
                })
                print(f"[{termo_busca}] {i+1}/{len(urls)} - {nome} | {tipo_telefone} | {telefone_limpo}")

            except BloqueioDetectado:
                raise
            except Exception as e:
                print(f"[{termo_busca}] Erro ao extrair {place_url}: {e}")

    except BloqueioDetectado:
        print(f"[{termo_busca}] Área interrompida por bloqueio do Google Maps "
              f"({len(leads)} lead(s) preservado(s)).")
    finally:
        if browser:
            browser.close()
        p.stop()

    return leads


def rodar_scraper_multithread(nicho, cidade, uf, termos_lista, mostrar_navegador=False, save_callback=None):
    """
    Executa a coleta em multithread. Se save_callback for informado, cada lote
    (por área) é salvo assim que termina, evitando perder a coleta em caso de falha.
    """
    todos_leads = []
    vistos = set()
    max_workers = min(3, len(termos_lista))
    print(f"Iniciando scraper com {max_workers} threads em {len(termos_lista)} área(s)...")

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futuros = {
            executor.submit(extrair_leads_local, nicho, termo, cidade, uf, mostrar_navegador): termo
            for termo in termos_lista
        }

        for futuro in as_completed(futuros):
            termo = futuros[futuro]
            try:
                leads_area = futuro.result()
                with lock:
                    novos = []
                    for lead in leads_area:
                        chave = (lead['nome'], lead['cidade'])
                        if chave not in vistos:
                            vistos.add(chave)
                            novos.append(lead)
                    todos_leads.extend(novos)

                if novos and save_callback:
                    save_callback(pd.DataFrame(novos))

                print(f"[{termo}] Finalizado. {len(novos)} leads novos (acumulado: {len(todos_leads)}).")
            except Exception as e:
                print(f"Erro na busca {termo}: {e}")

    return pd.DataFrame(todos_leads)
````

## File: src/locations.py
````python
# src/locations.py
"""Localidades (UF, cidade e bairros) com cache local em DuckDB.

Fonte oficial: API de Localidades do IBGE.
    estados    -> /api/v1/localidades/estados
    municipios -> /api/v1/localidades/municipios
    distritos  -> /api/v1/localidades/distritos

Com LOCALIDADES_USAR_CACHE=true (padrão), a base local é consultada primeiro;
só vai para a rede o que ainda não existe no banco. Com a flag false, os dados
são sempre buscados na API (e a base local é atualizada com o resultado).

Observação: os "distritos" do IBGE são divisões administrativas e, em muitos
municípios, resumem-se à própria sede. Quando não há distritos suficientes,
a lista é complementada com bairros do OpenStreetMap (Nominatim + Overpass).
"""
import os
import time
import unicodedata

import pandas as pd
import requests

from src import localidades_db
from src.config import env_int, str_para_bool

IBGE_API = "https://servicodados.ibge.gov.br/api/v1/localidades"

# User-Agent identificável é exigido pela política de uso do Nominatim.
HEADERS = {"User-Agent": "map-scraper-lead-prospecting/1.0 (prospeccao.mapscraper@gmail.com)"}

OVERPASS_ENDPOINTS = [
    "https://overpass-api.de/api/interpreter",
    "https://overpass.private.coffee/api/interpreter",
    "https://overpass.osm.ch/api/interpreter",
    "https://overpass.kumi.systems/api/interpreter",
]

# Se true: consulta o banco antes da API. Se false: sempre busca na API.
USAR_CACHE = str_para_bool(os.environ.get("LOCALIDADES_USAR_CACHE"), padrao=True)

# Se false: NUNCA grava na base local (nem cria tabelas). Funciona como
# "somente leitura": o banco é consultado, mas nada é alterado.
SALVAR = str_para_bool(os.environ.get("LOCALIDADES_SALVAR"), padrao=True)

# Reflete a flag no módulo de acesso ao banco (controla a criação das tabelas).
localidades_db.CRIAR_TABELAS = SALVAR

# Quantidade mínima de distritos úteis para não precisar do OpenStreetMap.
# Abaixo disso, a cidade é complementada com bairros do OSM.
MIN_BAIRROS = max(1, env_int("LOCALIDADES_MIN_BAIRROS", 3))

# Pausa (segundos) entre cidades no aquecimento por UF, aplicada apenas quando o
# OpenStreetMap foi consultado (política de uso do Nominatim: 1 req/s).
AQUECER_PAUSA_PADRAO = max(0, env_int("AQUECER_PAUSA_SEGUNDOS", 2))

_avisou_cache_indisponivel = False
_avisou_sem_gravacao = False


def _cache(funcao, *args, **kwargs):
    """Executa uma operação na base local, tolerando banco travado/indisponível."""
    global _avisou_cache_indisponivel
    try:
        return funcao(*args, **kwargs)
    except localidades_db.CacheIndisponivel as e:
        if not _avisou_cache_indisponivel:
            print(f"  Aviso: base local de localidades indisponível ({e}).")
            print("         Seguindo apenas com as APIs (IBGE/OSM).")
            _avisou_cache_indisponivel = True
        return None


def _salvar(funcao, *args, **kwargs):
    """Grava na base local, respeitando LOCALIDADES_SALVAR=false."""
    global _avisou_sem_gravacao
    if not SALVAR:
        if not _avisou_sem_gravacao:
            print("  LOCALIDADES_SALVAR=false: a base local não será alterada.")
            _avisou_sem_gravacao = True
        return None
    return _cache(funcao, *args, **kwargs)


# ---------------------------------------------------------------------------
# IBGE
# ---------------------------------------------------------------------------
def _get_json(url, params=None, timeout=60, tentativas=3):
    for tentativa in range(1, tentativas + 1):
        try:
            resposta = requests.get(url, params=params, timeout=timeout, headers=HEADERS)
            resposta.raise_for_status()
            return resposta.json()
        except Exception as e:
            print(f"  IBGE indisponível (tentativa {tentativa}/{tentativas}): {type(e).__name__}")
            if tentativa < tentativas:
                time.sleep(1.5 * tentativa)
    return None


def _baixar_estados():
    dados = _get_json(f"{IBGE_API}/estados", params={"orderBy": "nome"}, timeout=30)
    if not dados:
        return None
    return [{"uf": e["sigla"], "nome": e["nome"]} for e in dados]


def _uf_do_municipio(municipio):
    try:
        return municipio["microrregiao"]["mesorregiao"]["UF"]["sigla"]
    except (KeyError, TypeError):
        try:
            return municipio["regiao-imediata"]["regiao-intermediaria"]["UF"]["sigla"]
        except (KeyError, TypeError):
            return None


def _baixar_municipios(uf=None):
    url = f"{IBGE_API}/estados/{uf}/municipios" if uf else f"{IBGE_API}/municipios"
    dados = _get_json(url, params={"orderBy": "nome"})
    if not dados:
        return None

    registros = []
    for municipio in dados:
        sigla = uf or _uf_do_municipio(municipio)
        if not sigla:
            continue
        registros.append({
            "id_municipio": municipio["id"],
            "nome": municipio["nome"],
            "uf": sigla,
        })
    return registros


def _baixar_distritos(id_municipio=None):
    url = (f"{IBGE_API}/municipios/{id_municipio}/distritos"
           if id_municipio else f"{IBGE_API}/distritos")
    dados = _get_json(url)
    if not dados:
        return None

    registros = []
    for distrito in dados:
        municipio = distrito.get("municipio") or {}
        registros.append({
            "id_distrito": distrito.get("id"),
            "nome": (distrito.get("nome") or "").strip(),
            "id_municipio": municipio.get("id"),
        })
    return [r for r in registros if r["id_municipio"] and r["nome"]]


_municipios_memoria = {}


def _municipios_da_uf(uf):
    """Lista de municípios da UF, memorizada na execução para não baixar duas vezes."""
    if uf not in _municipios_memoria:
        print(f"  Baixando a lista de municípios de {uf} do IBGE...")
        municipios = _baixar_municipios(uf)
        if municipios is None:
            return None
        _municipios_memoria[uf] = municipios
    return _municipios_memoria[uf]


# ---------------------------------------------------------------------------
# OpenStreetMap (fallback de bairros)
# ---------------------------------------------------------------------------
def _obter_bbox_cidade(cidade, uf):
    """Retorna (sul, norte, oeste, leste) da cidade via Nominatim."""
    url = "https://nominatim.openstreetmap.org/search"
    params = {"format": "json", "q": f"{cidade}, {uf}, Brazil", "limit": 1}
    try:
        resposta = requests.get(url, params=params, timeout=15, headers=HEADERS)
        resposta.raise_for_status()
        resultados = resposta.json()
        if not resultados:
            return None
        bb = resultados[0].get("boundingbox")
        if not bb or len(bb) != 4:
            return None
        sul, norte, oeste, leste = (float(v) for v in bb)
        return (sul, norte, oeste, leste)
    except Exception as e:
        print(f"Erro ao localizar a cidade no Nominatim: {e}")
        return None


def _consultar_overpass(query):
    """Tenta a consulta em vários espelhos do Overpass, com retry e backoff.

    Retorna o JSON da resposta, ou None quando nenhum espelho respondeu
    (serviço indisponível) — o que é diferente de responder vazio.
    """
    for endpoint in OVERPASS_ENDPOINTS:
        for tentativa in range(1, 3):
            try:
                resposta = requests.get(endpoint, params={"data": query}, timeout=45, headers=HEADERS)
                resposta.raise_for_status()
                return resposta.json()
            except Exception as e:
                print(f"  Overpass ({endpoint}) tentativa {tentativa} falhou: {type(e).__name__}")
                time.sleep(1.5 * tentativa)
    return None


def _obter_bairros_overpass(sul, norte, oeste, leste):
    """Busca bairros dentro do bbox via Overpass (place=* e admin_level 9/10)."""
    bbox = f"({sul},{oeste},{norte},{leste})"

    query_leve = f"""
[out:json][timeout:40];
(
  node["place"~"^(suburb|neighbourhood|quarter)$"]{bbox};
  way["place"~"^(suburb|neighbourhood|quarter)$"]{bbox};
);
out center tags;
"""

    query_admin = f"""
[out:json][timeout:55];
(
  relation["boundary"="administrative"]["admin_level"="9"]{bbox};
  relation["boundary"="administrative"]["admin_level"="10"]{bbox};
);
out center tags;
"""

    data = _consultar_overpass(query_leve)
    if data is None:
        return None
    if data.get("elements"):
        return data
    return _consultar_overpass(query_admin)


def _bairros_via_overpass(cidade, uf):
    """Retorna a lista de bairros do OSM, ou None se o serviço estiver indisponível."""
    bbox = _obter_bbox_cidade(cidade, uf)
    if not bbox:
        return None

    data = _obter_bairros_overpass(*bbox)
    if data is None:
        return None

    nomes = set()
    for elemento in data.get("elements", []):
        tags = elemento.get("tags") or {}
        nome = tags.get("name")
        if not isinstance(nome, str):
            continue
        nome = nome.strip()
        if nome and nome.lower() != cidade.strip().lower():
            nomes.add(nome)
    return sorted(nomes)


# ---------------------------------------------------------------------------
# API pública do módulo
# ---------------------------------------------------------------------------
def obter_estados():
    if USAR_CACHE:
        estados = _cache(localidades_db.ler_estados)
        if estados:
            print(f"Base local: {len(estados)} estados.")
            return pd.DataFrame(estados)

    estados = _baixar_estados()
    if estados is None:
        estados = _cache(localidades_db.ler_estados)
        if estados:
            print("IBGE indisponível. Usando os estados gravados na base local.")
            return pd.DataFrame(estados)
        print("Erro ao buscar estados.")
        return pd.DataFrame()

    _salvar(localidades_db.salvar_estados, estados)
    return pd.DataFrame(estados)


def obter_cidades(uf):
    if USAR_CACHE:
        municipios = _cache(localidades_db.ler_municipios, uf)
        if municipios:
            print(f"Base local: {len(municipios)} cidades em {uf}.")
            return [m["nome"] for m in municipios]

    municipios = _municipios_da_uf(uf)
    if municipios is None:
        municipios = _cache(localidades_db.ler_municipios, uf)
        if municipios:
            print(f"IBGE indisponível. Usando as cidades de {uf} gravadas na base local.")
            return [m["nome"] for m in municipios]
        print(f"Erro ao buscar cidades para {uf}.")
        return []

    _salvar(localidades_db.salvar_municipios, municipios)
    return sorted(m["nome"] for m in municipios)


def _normalizar(texto):
    """Minúsculas e sem acentos, para comparar nomes digitados pelo usuário."""
    texto = unicodedata.normalize("NFKD", str(texto or ""))
    return "".join(c for c in texto if not unicodedata.combining(c)).strip().casefold()


def filtrar_cidades(cidades, termo):
    """Filtra a lista de cidades por um trecho, ignorando acentos e maiúsculas."""
    alvo = _normalizar(termo)
    if not alvo:
        return []
    return [c for c in cidades if alvo in _normalizar(c)]


def _descobrir_bairros(cidade, uf, municipio):
    """Monta a lista final de bairros: distritos do IBGE + complemento do OSM.

    Retorna (registros, fonte). fonte=None significa "não gravar no cache" —
    usado quando houve falha de rede, para tentar de novo na próxima execução.
    """
    registros = []
    total_distritos = 0
    if municipio:
        distritos = _baixar_distritos(municipio["id_municipio"]) or []
        total_distritos = len(distritos)
        for distrito in distritos:
            if _normalizar(distrito["nome"]) == _normalizar(cidade):
                continue
            registros.append({"nome": distrito["nome"], "id_distrito": distrito["id_distrito"]})

    if len(registros) >= MIN_BAIRROS:
        print(f"  IBGE: {len(registros)} distritos de {cidade}-{uf} serão usados como áreas de busca.")
        return registros, localidades_db.FONTE_IBGE

    # A API de Localidades do IBGE só tem distritos/subdistritos — não tem bairros.
    # Quando o município tem apenas o distrito-sede, não há o que aproveitar.
    if total_distritos <= 1:
        print(f"  IBGE não publica bairros para {cidade}-{uf}: o município tem apenas "
              f"{total_distritos} distrito (a sede).")
    else:
        print(f"  IBGE: apenas {len(registros)} distrito(s) além da sede em {cidade}-{uf}.")

    print("  Buscando bairros no OpenStreetMap...")
    bairros_osm = _bairros_via_overpass(cidade, uf)

    if bairros_osm is None:
        print("  OpenStreetMap indisponível. Esta cidade NÃO será gravada no cache;")
        print("  os distritos do IBGE serão usados apenas nesta execução.")
        return registros, None

    vistos = {_normalizar(r["nome"]) for r in registros}
    for nome in bairros_osm:
        if _normalizar(nome) not in vistos:
            vistos.add(_normalizar(nome))
            registros.append({"nome": nome, "id_distrito": None})

    if bairros_osm:
        return registros, localidades_db.FONTE_OVERPASS
    if registros:
        return registros, localidades_db.FONTE_IBGE
    return [], localidades_db.FONTE_CIDADE


def _resolver_municipio(cidade, uf):
    """Descobre o município no IBGE: id e nome oficial.

    Primeiro tenta a base local; se não achar, baixa a lista da UF (e grava, se
    LOCALIDADES_SALVAR permitir). Retorna None quando o nome não existe na UF.
    """
    alvo = _normalizar(cidade)

    municipios = _cache(localidades_db.ler_municipios, uf) or []
    for item in municipios:
        if _normalizar(item["nome"]) == alvo:
            return {
                "id_municipio": item["id_municipio"],
                "nome": item["nome"],
                "uf": uf,
                "bairros_fonte": item.get("bairros_fonte"),
            }

    baixados = _municipios_da_uf(uf) or []
    _salvar(localidades_db.salvar_municipios, baixados)

    for item in baixados:
        if _normalizar(item["nome"]) == alvo:
            return {
                "id_municipio": item["id_municipio"],
                "nome": item["nome"],
                "uf": item["uf"],
                "bairros_fonte": None,
            }

    if mun := _cache(localidades_db.buscar_municipio, cidade, uf):
        return mun
    return None


def obter_municipio(cidade, uf):
    """Retorna o município do IBGE para o nome digitado (id, nome oficial e uf).

    Útil para gravar sempre o nome oficial, mesmo que o usuário digite sem
    acento ou em minúsculas (ex.: "canoas" -> "Canoas").
    """
    return _resolver_municipio(cidade, uf)


def obter_bairros(cidade, uf):
    """
    Retorna os bairros de uma cidade, usando a base local quando possível.
    Lista vazia significa "buscar a cidade inteira".
    """
    municipio = _resolver_municipio(cidade, uf)

    # Nome oficial do IBGE: evita divergência de acento/caixa nas buscas.
    nome_oficial = municipio["nome"] if municipio else cidade

    if USAR_CACHE and municipio and municipio.get("bairros_fonte"):
        bairros = _cache(localidades_db.ler_bairros, municipio["id_municipio"]) or []
        # O distrito-sede tem o mesmo nome da cidade e não ajuda na busca por área.
        bairros = [b for b in bairros if _normalizar(b) != _normalizar(nome_oficial)]
        fonte = municipio["bairros_fonte"]
        if fonte == localidades_db.FONTE_CIDADE or not bairros:
            print(f"Base local: {nome_oficial}-{uf} sem bairros (fonte: {fonte}).")
            return []
        print(f"Base local: {len(bairros)} bairros de {nome_oficial}-{uf} (fonte: {fonte}).")
        return bairros

    bairros, fonte = _descobrir_bairros(nome_oficial, uf, municipio)

    if municipio and fonte:
        _salvar(localidades_db.salvar_bairros, municipio["id_municipio"], bairros, fonte)

    return [b["nome"] for b in bairros]


def obter_termos_busca(cidade, uf, max_bairros=30):
    """
    Divide a coleta por bairros para ampliar a cobertura do Google Maps
    (que pagina os resultados e não entrega a cidade inteira em uma única busca).
    Se nenhum bairro for descoberto, busca a cidade inteira como fallback.
    """
    print(f"Descobrindo bairros de {cidade} - {uf}...")
    bairros = obter_bairros(cidade, uf)

    if bairros:
        bairros = bairros[:max_bairros]
        print(f"{len(bairros)} bairros encontrados. A coleta será dividida por bairro.")
        return bairros

    print("Nenhum bairro encontrado. Buscando a cidade inteira.")
    return [cidade]


def listar_municipios_pendentes(uf):
    """Lista os municípios da UF que ainda não têm bairros resolvidos.

    Se a UF ainda não estiver na base local, baixa a lista do IBGE (e grava, se
    LOCALIDADES_SALVAR permitir). Retorna [] quando todos já estão resolvidos.
    """
    pendentes = _cache(localidades_db.ler_municipios_pendentes, uf)
    if pendentes is None:
        return []
    if pendentes:
        return pendentes

    # Nada pendente: só é "tudo pronto" se a UF estiver na base local.
    if _cache(localidades_db.ler_municipios, uf):
        return []

    print(f"  {uf} ainda não está na base local. Baixando a lista de municípios do IBGE...")
    municipios = _baixar_municipios(uf)
    if not municipios:
        return []
    _salvar(localidades_db.salvar_municipios, municipios)
    return [{"id_municipio": m["id_municipio"], "nome": m["nome"]} for m in municipios]


def aquecer_bairros_uf(uf, cidades=None, max_cidades=0, pausa_segundos=None):
    """Resolve e grava os bairros de todas as cidades de uma UF (uma única vez).

    Útil para preparar o cache e depois rodar a coleta sem nenhuma consulta de
    rede. A pausa entre cidades é aplicada só quando o OpenStreetMap foi de fato
    consultado (cidades cobertas pelo IBGE são instantâneas).

    Retorna um dicionário com o resumo da execução.
    """
    if not SALVAR:
        print("\nLOCALIDADES_SALVAR=false: não é possível aquecer a base local.")
        print("Ative a flag LOCALIDADES_SALVAR para gravar os bairros.")
        return None

    pausa_segundos = AQUECER_PAUSA_PADRAO if pausa_segundos is None else pausa_segundos

    if cidades is None:
        print(f"\nVerificando quais cidades de {uf} ainda precisam de bairros...")
        cidades = listar_municipios_pendentes(uf)

    total_pendente = len(cidades)
    if not total_pendente:
        print(f"Todas as cidades de {uf} já têm bairros na base local. Nada a fazer.")
        return {"uf": uf, "pendentes": 0, "processadas": 0, "ibge": 0,
                "osm": 0, "sem_bairros": 0, "falhas": 0}

    if max_cidades and max_cidades > 0:
        cidades = cidades[:max_cidades]

    print(f"\nAquecendo bairros de {len(cidades)} cidade(s) de {uf} "
          f"({total_pendente} pendente(s) no total).")
    print(f"Pausa entre cidades que usam OpenStreetMap: {pausa_segundos}s")
    print("Interrompa com Ctrl+C — o progresso já gravado é preservado.\n")

    resumo = {"uf": uf, "pendentes": total_pendente, "processadas": 0,
              "ibge": 0, "osm": 0, "sem_bairros": 0, "falhas": 0}

    try:
        for indice, cidade in enumerate(cidades, 1):
            nome = cidade["nome"]
            print(f"[{indice}/{len(cidades)}] {nome}-{uf}")

            bairros = obter_bairros(nome, uf)
            municipio = _cache(localidades_db.buscar_municipio, nome, uf)
            fonte = (municipio or {}).get("bairros_fonte")
            resumo["processadas"] += 1

            if fonte is None:
                resumo["falhas"] += 1
                print(f"  Falhou (nada gravado). Pulando.")
            elif fonte == localidades_db.FONTE_OVERPASS:
                resumo["osm"] += 1
            elif fonte == localidades_db.FONTE_IBGE:
                resumo["ibge"] += 1
            else:
                resumo["sem_bairros"] += 1

            usou_osm = fonte in (localidades_db.FONTE_OVERPASS,
                                 localidades_db.FONTE_CIDADE)
            if usou_osm and indice < len(cidades):
                time.sleep(pausa_segundos)
    except KeyboardInterrupt:
        print("\nInterrompido pelo usuário. O que já foi gravado está preservado.")

    print(f"\nResumo de {uf}: {resumo['processadas']} cidade(s) processada(s) "
          f"de {total_pendente} pendente(s).")
    print(f"  via IBGE: {resumo['ibge']} | via OpenStreetMap: {resumo['osm']} | "
          f"sem bairros: {resumo['sem_bairros']} | falhas: {resumo['falhas']}")
    restantes = total_pendente - resumo["processadas"]
    if restantes > 0:
        print(f"  {restantes} cidade(s) continuam pendentes — rode novamente para retomar.")
    return resumo


def _descrever_gravacao(total, recebidos):
    """Texto do resumo da sincronização (distingue gravado de apenas baixado)."""
    if total is None:
        return f"{recebidos} recebidos, NÃO gravados (base local indisponível)"
    return f"{total} gravados"


def sincronizar_base_localidades():
    """Baixa estados, municípios e distritos do IBGE para o DuckDB.

    Depois disso, com LOCALIDADES_USAR_CACHE=true, a coleta não faz chamadas de
    rede para descobrir bairros — exceto nas cidades em que o IBGE não tem
    distritos úteis (aí o OSM é consultado uma única vez e o resultado é gravado).
    """
    if not SALVAR:
        print("\nLOCALIDADES_SALVAR=false: a sincronização está desativada.")
        print("Nada foi baixado nem gravado. Ative a flag para popular a base local.")
        return False

    print("\nSincronizando base de localidades do IBGE...")

    estados = _baixar_estados()
    if estados is None:
        print("Falha ao baixar os estados. Sincronização abortada.")
        return False
    total = _salvar(localidades_db.salvar_estados, estados)
    print(f"  Estados: {_descrever_gravacao(total, len(estados))}.")

    municipios = _baixar_municipios()
    if municipios is None:
        print("Falha ao baixar os municípios. Sincronização abortada.")
        return False
    total = _salvar(localidades_db.salvar_municipios, municipios)
    print(f"  Municípios: {_descrever_gravacao(total, len(municipios))}.")

    print("  Baixando distritos (pode levar alguns segundos)...")
    distritos = _baixar_distritos()
    if distritos is None:
        print("Falha ao baixar os distritos. Estados e municípios foram gravados.")
        return False
    total = _salvar(localidades_db.salvar_distritos_bulk, distritos, MIN_BAIRROS)
    print(f"  Distritos: {_descrever_gravacao(total, len(distritos))}.")

    stats = _cache(localidades_db.estatisticas) or {}
    print(f"\nBase local: {stats.get('estados', 0)} estados, "
          f"{stats.get('municipios', 0)} municípios, {stats.get('bairros', 0)} bairros "
          f"({stats.get('cidades_prontas', 0)} cidades com bairros prontos).")
    print("Sincronização concluída.")
    return True
````

## File: .gitignore
````
# Dados: o banco DuckDB É versionado (data/leads.duckdb).
# Apenas artefatos transientes do DuckDB e saídas geradas ficam de fora.
*.duckdb.wal
*.duckdb.tmp
*.xlsx
*.csv
*.log

# Segredos e configuração local (contém a API key da WAHA)
.env

# Sessões do WhatsApp (WAHA)
sessions/

# Ambientes Virtuais
venv/
env/
.venv/

# Python Cache
__pycache__/
*.py[cod]
*$py.class

# Configurações de IDE
.vscode/
.idea/

# Sistema Operacional
.DS_Store
Thumbs.db
````

## File: src/main.py
````python
# src/main.py
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.locations import (
    obter_estados,
    obter_cidades,
    obter_termos_busca,
    obter_municipio,
    filtrar_cidades,
    sincronizar_base_localidades,
    listar_municipios_pendentes,
    aquecer_bairros_uf,
    SALVAR as LOCALIDADES_SALVAR,
)
from src.scraper import rodar_scraper_multithread
from src.database import LeadDatabase
from src.whatsapp import (
    disparar_campanha,
    MENSAGEM_PADRAO,
    WAHA_INTERVALO,
    WAHA_LIMITE,
    WAHA_ATIVO,
    SOMENTE_ENVIO,
)


def coletar_leads():
    df_estados = obter_estados()
    if df_estados.empty:
        return

    uf_escolhida = input("Digite a UF (ex: RS, SP, RJ): ").strip().upper()
    if uf_escolhida not in df_estados['uf'].values:
        print("UF inválida.")
        return

    cidades = obter_cidades(uf_escolhida)
    termo_cidade = input("Digite o nome da cidade: ").strip()
    cidades_filtradas = filtrar_cidades(cidades, termo_cidade)

    if not cidades_filtradas:
        print("Cidade não encontrada.")
        return
    elif len(cidades_filtradas) > 1:
        cidade_escolhida = input(
            f"Várias encontradas ({', '.join(cidades_filtradas[:3])}...). Digite o nome exato: "
        ).strip()
        exatos = filtrar_cidades(cidades, cidade_escolhida)
        cidade_escolhida = exatos[0] if exatos else cidade_escolhida
    else:
        cidade_escolhida = cidades_filtradas[0]

    # Confirma o município no IBGE e passa a usar o nome oficial (com acentos).
    municipio = obter_municipio(cidade_escolhida, uf_escolhida)
    if municipio:
        cidade_escolhida = municipio["nome"]
        print(f"Município (IBGE): {cidade_escolhida}-{uf_escolhida} | código {municipio['id_municipio']}")
    else:
        print(f"Aviso: {cidade_escolhida}-{uf_escolhida} não foi confirmado no IBGE.")

    nicho = input(f"\nQual o nicho para {cidade_escolhida}-{uf_escolhida}? ").strip().lower()

    termos_busca = obter_termos_busca(cidade_escolhida, uf_escolhida)

    mostrar_navegador = input("\nVer o navegador? (S/N): ").strip().upper() == 'S'

    print("\nIniciando extração...")
    db = LeadDatabase()

    df_resultados = rodar_scraper_multithread(
        nicho=nicho,
        cidade=cidade_escolhida,
        uf=uf_escolhida,
        termos_lista=termos_busca,
        mostrar_navegador=mostrar_navegador,
        save_callback=db.save_leads,  # salvamento incremental (UPSERT) a cada área concluída
    )

    if not df_resultados.empty:
        print("\nLeads salvos incrementalmente no DuckDB (UPSERT).")
        db.export_to_excel(nicho, cidade_escolhida)
    else:
        print("Nenhum dado extraído.")

    db.close()


def enviar_whatsapp_menu():
    print("\n=== ENVIO WHATSAPP (WAHA) ===")

    if not WAHA_ATIVO:
        print("Envio de WhatsApp desativado (WAHA_ATIVO=false no .env).")
        return

    db = LeadDatabase()

    pendentes = db.get_leads_para_envio(limite=WAHA_LIMITE)
    if pendentes.empty:
        print("Nenhum lead celular pendente de envio.")
        db.close()
        return

    print(f"{len(pendentes)} lead(s) celular(es) pendentes (fixos são ignorados).")
    if WAHA_LIMITE:
        print(f"Limite configurado: {WAHA_LIMITE} lead(s) por campanha.")

    print(f"Mensagem padrão: {MENSAGEM_PADRAO}")
    mensagem = input("Digite a mensagem (ou Enter para usar a padrão): ").strip()
    if not mensagem:
        mensagem = MENSAGEM_PADRAO

    confirmar = input(f"Enviar para {len(pendentes)} lead(s)? (S/N): ").strip().upper()
    if confirmar != 'S':
        print("Envio cancelado.")
        db.close()
        return

    disparar_campanha(db, mensagem_template=mensagem, intervalo=WAHA_INTERVALO, limite=WAHA_LIMITE)
    db.close()


def aquecer_bairros_menu():
    """Prepara o cache de bairros de uma UF inteira (sem raspar leads)."""
    print("\n=== AQUECER BAIRROS DE UMA UF ===")

    if not LOCALIDADES_SALVAR:
        print("LOCALIDADES_SALVAR=false: o aquecimento está desativado.")
        print("Ative a flag LOCALIDADES_SALVAR no .env para gravar os bairros.")
        return

    print("Resolve e grava os bairros de todas as cidades da UF, uma única vez.")
    print("Depois disso a coleta por cidade não consulta mais IBGE/OSM.")

    df_estados = obter_estados()
    if df_estados.empty:
        print("Não foi possível obter a lista de estados.")
        return

    uf = input("Digite a UF (ex: RS, SP, RJ): ").strip().upper()
    if uf not in df_estados['uf'].values:
        print("UF inválida.")
        return

    print(f"\nVerificando quais cidades de {uf} ainda precisam de bairros...")
    pendentes = listar_municipios_pendentes(uf)
    if not pendentes:
        print(f"Todas as cidades de {uf} já estão na base local. Nada a fazer.")
        return

    print(f"{len(pendentes)} cidade(s) pendente(s) em {uf}.")
    print("As cidades cobertas pelo IBGE são instantâneas; as demais usam o")
    print("OpenStreetMap (Nominatim + Overpass), com pausa entre elas.")

    limite = input("Quantas cidades processar agora? (Enter = todas): ").strip()
    max_cidades = 0
    if limite:
        try:
            max_cidades = max(1, int(limite))
        except ValueError:
            print("Valor inválido. Usando todas.")
            max_cidades = 0

    previstas = min(max_cidades, len(pendentes)) if max_cidades else len(pendentes)
    confirmar = input(f"Processar {previstas} cidade(s)? (S/N): ").strip().upper()
    if confirmar != 'S':
        print("Operação cancelada.")
        return

    aquecer_bairros_uf(uf, cidades=pendentes, max_cidades=max_cidades)


def menu_interativo():
    # Flag de linha de comando: `python src/main.py --so-enviar` pula a coleta
    # e vai direto para o envio (equivale a SOMENTE_ENVIO=true no .env).
    so_enviar_cli = "--so-enviar" in sys.argv

    if SOMENTE_ENVIO or so_enviar_cli:
        enviar_whatsapp_menu()
        return

    while True:
        print("\n=== MAP SCRAPER ===")
        print("1 - Coletar leads")
        print("2 - Enviar mensagens WhatsApp")
        print("3 - Sincronizar base de localidades (IBGE)")
        print("4 - Aquecer bairros de uma UF (OpenStreetMap)")
        print("5 - Sair")
        opcao = input("Escolha uma opção: ").strip()

        if opcao == "1":
            coletar_leads()
        elif opcao == "2":
            enviar_whatsapp_menu()
        elif opcao == "3":
            sincronizar_base_localidades()
        elif opcao == "4":
            aquecer_bairros_menu()
        elif opcao == "5":
            print("Até mais!")
            break
        else:
            print("Opção inválida.")


if __name__ == "__main__":
    menu_interativo()
````

## File: README.md
````markdown
Documentação do Projeto: MAP SCRAPER

1. Objetivo do Projeto

    Ferramenta automatizada e gratuita para prospecção de leads B2B locais que muitas vezes não possuem site, mas estão presentes no Google Maps e no Instagram.

    O sistema é capaz de receber um Estado e Cidade, descobrir os bairros de forma dinâmica, raspar os dados do Google Maps (Nome, Telefone, Instagram, Site) e gerenciar esses dados em um banco local, evitando duplicatas e permitindo o descarte de leads já trabalhados.

2. Funcionalidades

    A ferramenta foi construída com uma arquitetura modular e conta com os seguintes recursos:

        - Busca Dinâmica de Localidades: Integração com a API do IBGE para listar Estados, Cidades e Distritos, gravando tudo em tabelas locais (cache) para não depender da rede nas próximas execuções. O nome digitado é confirmado no IBGE (aceita sem acento e em minúsculas) e o nome oficial é usado nas buscas. Complemento com Nominatim + Overpass (OpenStreetMap) para descobrir bairros quando o IBGE não cobre a cidade. Se nenhum bairro for encontrado, ele faz fallback buscando a cidade inteira.

        - Scraping em Multithreading: Uso do Playwright com ThreadPoolExecutor para abrir múltiplos navegadores simultaneamente e acelerar a coleta em diferentes bairros.

        - Cobertura por Bairros: A coleta é dividida por bairros para contornar a paginação do Google Maps e capturar mais leads por cidade.

        - Rolagem Dinâmica: A lista de resultados é rolada até esgotar (com limite de segurança), em vez de um número fixo de rolagens.

        - Robustez: Retry com backoff em erros transitórios, deduplicação intra-execução e salvamento incremental no DuckDB a cada área concluída.

        - Anti-bloqueio: User-Agent realista, viewport configurado e pausas aleatórias entre as requisições para reduzir o risco de bloqueio.

        - Tratamento de Dados (Data Cleansing):

        - Formatação automática de telefones para o padrão brasileiro (XX) XXXXX-XXXX.

        - Classificação automática do telefone: Celular (11 dígitos) ou Fixo (10 dígitos).

        - Banco de Dados Local (DuckDB): Armazenamento rápido e seguro em um arquivo local.

        - UPSERT: Se o lead já existe, ele atualiza os dados e a data de extração. Se for novo, insere.

        - Controle de Status: Leads podem ser marcados como ativo ou descartado. Se um lead descartado for encontrado novamente, o robô ignora e não atualiza.

        - Exportação para Excel: Gera um relatório limpo e ordenado apenas com os leads ativos.

        - Envio de WhatsApp (WAHA): Envia mensagens para os leads via WAHA (WhatsApp HTTP API). Só envia para leads ativos do tipo Celular (nunca fixo) e ainda não enviados, com intervalo configurável entre disparos para evitar spam. Cada envio é registrado em `status_whatsapp` e `data_envio_whatsapp`.

        - Base de Localidades Offline: estados, municípios e distritos do IBGE são gravados no próprio DuckDB (`localidades_estados`, `localidades_municipios`, `localidades_bairros`). Na primeira consulta de uma cidade os dados vêm da API; nas seguintes, tudo sai do banco, sem rede. A sincronização completa fica no menu (opção 3).

        - Tratamento de Captcha/Bloqueio: detecta a tela de "tráfego incomum" do Google Maps e aplica pausa longa antes de tentar novamente, além de um cooldown compartilhado que pausa todas as threads ao mesmo tempo. Se o bloqueio persistir, a área é abortada preservando os leads já coletados.

3. Stack Tecnológica

    - Linguagem: Python 3.10+
    - Scraping: Playwright (Chromium)
    - Banco de Dados: DuckDB
    - Manipulação de Dados: Pandas
    - APIs: IBGE (Localidades), Nominatim e Overpass (Bairros)
    - Tratamento: Regex (para telefones)
    - WhatsApp: WAHA (WhatsApp HTTP API)

4. Estrutura de Pastas

    map_scraper_project/
    │
    ├── data/                  # Onde o banco leads.duckdb é salvo
    ├── memory/                # Memória do projeto para modelos de IA (ver seção 12)
    ├── output/                # Onde os arquivos Excel finais são gerados
    │
    ├── src/                   # Código-fonte
    │   ├── __init__.py        
    │   ├── config.py          # Leitura centralizada do .env e flags
    │   ├── database.py        # Lógica do DuckDB (UPSERT, status, exportação, log de envio)
    │   ├── localidades_db.py  # Cache local das localidades (tabelas IBGE no DuckDB)
    │   ├── locations.py       # IBGE + OSM (Nominatim/Overpass), com cache no banco
    │   ├── scraper.py         # Robô Playwright, multithreading e anti-bloqueio
    │   ├── utils.py           # Formatação de telefone (Fixo/Celular)
    │   ├── whatsapp.py        # Envio via WAHA (WhatsApp HTTP API)
    │   └── main.py            # Menu interativo e orquestração
    │
    ├── .env.example           # Modelo das variáveis de ambiente
    ├── requirements.txt       # Dependências do projeto
    └── README.md              # Este documento

5. Como Usar (Manual do Usuário)

    Passo 1: Instalação
    No terminal, dentro da pasta raiz do projeto, instale as dependências e o navegador do Playwright:

    python -m venv venv
    .\venv\Scripts\Activate
    python -m pip install -r requirements.txt
    python -m playwright install chromium
    Passo 2: Execução
    Antes de rodar, crie o seu `.env` a partir do modelo:

    Copy-Item .env.example .env

    Rode o arquivo principal:

    python src/main.py
    Passo 3: Interação no Terminal
    O menu tem 5 opções:

    1 - Coletar leads: faz 5 perguntas simples (UF, Cidade, Nicho, Bairros automáticos, Ver navegador).
    2 - Enviar mensagens WhatsApp: envia para os leads celulares pendentes (ver seção 7).
    3 - Sincronizar base de localidades (IBGE): baixa estados, municípios e distritos para o DuckDB (ver seção 8).
    4 - Aquecer bairros de uma UF (OpenStreetMap): resolve e grava os bairros de todas as cidades do estado (ver seção 8).
    5 - Sair.

    Passo 4: Resultados

        O banco de dados será atualizado em data/leads.duckdb.

        Um arquivo Excel será gerado em output/leads_nicho_cidade.xlsx.


6. Gerenciamento do Banco de Dados (Regras de Negócio)

    Se você quiser descartar um lead para que ele não seja mais exportado e não seja atualizado nas próximas buscas, você pode rodar um comando SQL direto no DuckDB (via DBeaver ou script Python):

    sql
    -- Para descartar um lead
    UPDATE leads SET status = 'descartado' WHERE nome = 'Nome da Barbearia';

    -- Para reativar um lead
    UPDATE leads SET status = 'ativo' WHERE nome = 'Nome da Barbearia';
    Nota: A regra do UPSERT no database.py garante que, se o robô achar uma barbearia "descartada", ele pula ela e não sobrescreve seus dados no banco.

7. Envio de WhatsApp (WAHA)

    Pré-requisito: uma instância WAHA rodando com um número conectado via QR Code.

    Configuração (arquivo .env na raiz do projeto):
    Copie .env.example para .env e preencha os valores.

    ```
    WAHA_API_URL=http://localhost:3000
    WAHA_API_KEY=SUA_CHAVE_AQUI
    WAHA_SESSION=default
    WAHA_ATIVO=true
    SOMENTE_ENVIO=false
    WAHA_INTERVALO=13
    WAHA_LIMITE=
    ```

    Flags de comportamento:
    - WAHA_ATIVO: se false, desliga o envio de WhatsApp (não tenta enviar).
    - SOMENTE_ENVIO: se true, pula a coleta e vai direto para o envio
      (equivalente a rodar `python src/main.py --so-enviar`).
    - WAHA_LIMITE: quantidade máxima de leads por campanha (vazio = sem limite).

    Regras de envio (evita spam):
    - Só envia para leads com status = 'ativo'.
    - Só envia para tipo_telefone = 'Celular' (fixos são ignorados).
    - Só envia para leads ainda não enviados (status_whatsapp = 'pendente' ou NULL).
    - Intervalo de WAHA_INTERVALO segundos entre envios.

    Logs no banco:
    - status_whatsapp: 'pendente', 'enviado' ou 'falhou'.
    - data_envio_whatsapp: gravada apenas quando o envio é bem-sucedido.

    A mensagem pode usar as variáveis {nome}, {bairro} e {cidade}.


8. Base de Localidades Offline (IBGE)

    O projeto mantém um cache local das localidades no próprio DuckDB, criado na
    primeira consulta e reaproveitado nas seguintes (sem rede).

    Tabelas criadas automaticamente (guardam apenas o essencial):
    - localidades_estados: uf, nome
    - localidades_municipios: id_municipio, nome, uf + estado da coleta de bairros
    - localidades_bairros: id_municipio, nome, id_distrito

    Fontes (API de Localidades do IBGE):
    - Estados:    https://servicodados.ibge.gov.br/api/v1/localidades/estados
    - Municípios: https://servicodados.ibge.gov.br/api/v1/localidades/municipios
    - Distritos:  https://servicodados.ibge.gov.br/api/v1/localidades/distritos

    Configuração (.env):
    ```
    LOCALIDADES_USAR_CACHE=true
    LOCALIDADES_SALVAR=true
    LOCALIDADES_MIN_BAIRROS=3
    AQUECER_PAUSA_SEGUNDOS=2
    ```

    - LOCALIDADES_USAR_CACHE=true (padrão): consulta o banco primeiro e só chama a
      API quando o dado ainda não existe (e aí grava o resultado).
    - LOCALIDADES_USAR_CACHE=false: sempre busca na API do IBGE e atualiza a base
      local com o que voltou.
    - LOCALIDADES_SALVAR=false: modo somente leitura. Nada é gravado e nem as
      tabelas são criadas; o banco só é consultado. A sincronização do menu fica
      desativada.
    - LOCALIDADES_MIN_BAIRROS: mínimo de distritos do IBGE para a cidade ser
      considerada coberta. Abaixo disso, os bairros são complementados com o
      OpenStreetMap (Nominatim + Overpass) e o resultado também fica em cache.
    - AQUECER_PAUSA_SEGUNDOS: pausa entre cidades no aquecimento por UF, aplicada
      somente quando a cidade usou o OpenStreetMap.

    As duas flags são independentes:

    | USAR_CACHE | SALVAR | Comportamento |
    |---|---|---|
    | true  | true  | lê do banco; grava o que faltar (recomendado) |
    | false | true  | sempre vai à API e regrava tudo (força atualização) |
    | true  | false | só lê o banco; o que não existe vai à API sem gravar |
    | false | false | sempre à API, sem tocar no banco |

    O que acontece ao rodar de novo para a mesma cidade:

    - localidades_estados: UPSERT por uf (só atualiza o nome).
    - localidades_municipios: UPSERT por id_municipio (atualiza nome/uf e
      PRESERVA bairros_fonte / bairros_atualizado_em).
    - localidades_bairros: a lista da cidade é tratada como autoritativa. Nomes
      iguais são atualizados, nomes novos são inseridos e nomes que não vieram mais
      são removidos — mas apenas daquela cidade.
    - Sincronização completa (menu opção 3): aditiva. Ela insere/atualiza os
      distritos do IBGE sem apagar bairros que já existem, então listas
      complementadas pelo OpenStreetMap são preservadas.

    Rodar só para um estado também é seguro: obter_cidades(uf) grava apenas os
    municípios daquela UF, e nada de outras UFs é alterado.

    Sincronização completa: menu opção 3 (ou `sincronizar_base_localidades()`), que
    baixa de uma vez todos os estados, municípios e distritos (~10,7 mil registros).

    Aquecimento por UF: menu opção 4 (ou `aquecer_bairros_uf('RS')`). Resolve e
    grava os bairros de TODAS as cidades de um estado, sem raspar nenhum lead.
    Depois disso, a coleta por cidade não consulta mais IBGE/OSM.

    - Processa apenas as cidades com `bairros_fonte IS NULL` (ou seja, retoma de
      onde parou em execuções anteriores).
    - Cidades cobertas pelo IBGE são instantâneas; as demais usam o OpenStreetMap.
    - A pausa entre cidades (AQUECER_PAUSA_SEGUNDOS) é aplicada somente quando o
      OSM foi consultado — respeitando o limite de 1 req/s do Nominatim.
    - Ctrl+C interrompe sem perder o que já foi gravado; basta rodar de novo.
    - É possível limitar quantas cidades processar por execução.

    Importante: os "distritos" do IBGE são divisões administrativas e, em muitos
    municípios, resumem-se à própria sede. Por isso o fallback com o OSM continua
    existindo — a diferença é que ele roda uma única vez por cidade e o resultado
    é gravado no banco. Se o OSM estiver fora do ar, nada é gravado (a próxima
    execução tenta de novo) e a coleta segue com os distritos do IBGE.

    A API de Localidades do IBGE NÃO fornece bairros — apenas distritos e
    subdistritos. Exemplo real: Canoas-RS tem 1 distrito (a própria sede) e 0
    subdistritos, então o IBGE não contribui com áreas para essa cidade e o robô
    informa isso e segue para o OpenStreetMap:

    ```
    IBGE não publica bairros para Canoas-RS: o município tem apenas 1 distrito (a sede).
    Buscando bairros no OpenStreetMap...
    ```

    Cidades com vários distritos (São Paulo: 96, Campinas: 7) usam o IBGE e não
    consultam o OSM. Das 5.571 cidades do país, 643 têm distritos suficientes.

    Como a cidade é resolvida: o nome digitado é comparado sem acento e sem
    diferenciar maiúsculas ("canoas", "sao leopoldo") com a lista do IBGE, e o nome
    oficial é exibido e usado no scraping, no banco e no Excel:

    ```
    Digite o nome da cidade: canoas
    Município (IBGE): Canoas-RS | código 4304606
    ```

    Para forçar a atualização de uma cidade já gravada, limpe a marca:
    ```sql
    UPDATE localidades_municipios SET bairros_fonte = NULL WHERE nome = 'Porto Alegre';
    ```

9. Anti-bloqueio / Captcha (Google Maps)

    Quando o Google responde com a tela de "tráfego incomum" (captcha), o robô:
    1. detecta o bloqueio (URL /sorry/, formulários de captcha ou textos típicos);
    2. aplica um cooldown global, pausando TODAS as threads ao mesmo tempo;
    3. espera a pausa longa e tenta novamente até CAPTCHA_MAX_TENTATIVAS;
    4. se o bloqueio persistir, aborta apenas aquela área, preservando os leads
       já extraídos (que continuam sendo salvos incrementalmente).

    Configuração (.env):
    ```
    CAPTCHA_MAX_TENTATIVAS=2
    CAPTCHA_PAUSA_SEGUNDOS=300
    CAPTCHA_PAUSA_GLOBAL_SEGUNDOS=180
    ```

    - CAPTCHA_MAX_TENTATIVAS: tentativas por página antes de abortar a área.
    - CAPTCHA_PAUSA_SEGUNDOS: pausa longa da thread que levou o bloqueio.
    - CAPTCHA_PAUSA_GLOBAL_SEGUNDOS: pausa compartilhada entre as threads.

    A resolução automática de captcha por serviço externo (2Captcha, CapMonster
    etc.) não está implementada — o comportamento padrão é pausar e desistir da
    área em vez de insistir. Em coletas muito grandes, aumente as pausas acima.

10. commit forçado

    git add -A; git commit -m "sync local $(Get-Date -Format 'yyyy-MM-dd HH:mm')"; git push --force-with-lease origin main

11. Próximos Passos (Melhorias Futuras)

    Já implementado:
    - Base de localidades offline no DuckDB (estados, municípios e distritos do IBGE).
    - Detecção de captcha com pausa longa e cooldown compartilhado entre threads.

    Pendências sugeridas:
    - Resolução automática de captcha: integrar um serviço (2Captcha/CapMonster) para
      coletas muito grandes, hoje o robô apenas pausa e desiste da área.

    - Enriquecimento de E-mail: Criar um script secundário que lê os sites encontrados e busca e-mails de contato (usando Regex).


12. Memória do Projeto para IA (pasta memory/)

    A pasta `memory/` reúne documentação resumida e densa, pensada para ser lida
    por modelos de IA antes de alterar o código (economiza contexto/custo).

    Ordem de leitura:
    1. memory/00-resumo-projeto.md        -> objetivo, stack e estrutura
    2. memory/01-arquitetura-e-modulos.md -> módulos, funções e fluxos
    3. memory/02-decisoes-e-armadilhas.md -> decisões, bugs conhecidos, cuidados
    4. memory/03-historico-de-mudancas.md -> o que mudou e o que ficou pendente
    5. memory/04-como-contribuir.md       -> padrões de código, logs, testes e docs

    Regras: manter os arquivos curtos, registrar o "porquê" das decisões e nunca
    colocar segredos ali (API keys ficam apenas no `.env`).


13. Observação sobre configuração

    O modelo completo e comentado de todas as variáveis está em `.env.example`.
    Cada item traz a faixa de valores e o efeito colateral. Comentários devem
    ficar em linha própria; comentário na mesma linha do valor é lido como parte
    do valor.
````




# Instruction
# Instruções para o Assistente de IA
Você é um desenvolvedor especialista trabalhando neste projeto de Map Scraper.
Por favor, processe todas as solicitações, explicações, comentários de código e interações estritamente em Português do Brasil (pt-BR).
