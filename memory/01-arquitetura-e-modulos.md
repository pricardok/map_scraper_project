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
