# 00 — Resumo do Projeto

**Map Scraper** — ferramenta de prospecção de leads B2B a partir do Google Maps.

- **Entrada:** UF + cidade + nicho (ex.: `RS`, `Canoas`, `barbearias`).
- **Processo:** divide a busca por bairros, raspa o Google Maps com Playwright em
  multithread e extrai nome, telefone, Instagram e site.
- **Saída:** leads num banco (PostgreSQL **ou** DuckDB) + Excel em `output/`.
- **Extra:** dispara mensagens de WhatsApp via WAHA para leads já coletados, com
  templates reutilizáveis, filtros (número/cidade/nicho), teste de envio, cache
  do chatId resolvido (`@lid`/`@c.us`) e **cadência aleatória** anti-bloqueio.

## Fluxo de alto nível

```
menu (src/main.py)
  └─ 1 Coletar    → locations.obter_termos_busca(cidade, uf)
                  → scraper.rodar_scraper_multithread(...)
                  → database.LeadDatabase.save_leads (UPSERT incremental)
                  → database.export_to_excel
  └─ 2 WhatsApp   → template ativo → filtros → teste → database.get_leads_para_envio
                  → whatsapp.disparar_campanha (WAHA, cadência aleatória)
  └─ 3 Sincronizar localidades (IBGE) → locations.sincronizar_base_localidades
  └─ 4 Aquecer bairros de uma UF       → locations.aquecer_bairros_uf
  └─ 5 Sair
```

## Stack

| Item | Tecnologia |
|---|---|
| Linguagem | Python 3.10+ (ambiente: `venv/`) |
| Scraping | Playwright (Chromium) + ThreadPoolExecutor |
| Banco | **PostgreSQL (externo) ou DuckDB (local)** — via `src/backend.py` |
| Dados | Pandas |
| Localidades | API IBGE + Nominatim/Overpass (OpenStreetMap) |
| WhatsApp | WAHA (WhatsApp HTTP API) |
| Config | `.env` carregado por `src/config.py` |

## Estrutura

```
map_scraper_project/
├── data/          leads.duckdb (usado quando DB_ENGINE=duckdb)
├── memory/        esta documentação para IA
├── output/        Excel gerado (ignorado no Git)
├── src/
│   ├── config.py          loader do .env + escolha do backend (DB_ENGINE)
│   ├── backend.py         abstração PostgreSQL/DuckDB (conexão, SQL, bulk upsert)
│   ├── database.py        LeadDatabase: leads, templates, log WAHA (via backend)
│   ├── localidades_db.py  cache IBGE (via backend)
│   ├── locations.py       IBGE + OSM + cache; sync e aquecimento por UF
│   ├── scraper.py         Playwright, multithread, anti-captcha
│   ├── schema.py          DDL + seed + migração (setup: python src/schema.py)
│   ├── utils.py           formatar_telefone → (telefone, tipo, link wa)
│   ├── whatsapp.py        envio via WAHA + cadência aleatória
│   └── main.py            menu interativo
├── .env / .env.example
├── requirements.txt
└── README.md
```

## Git — o que é versionado

| Versionado | Ignorado |
|---|---|
| `src/`, `memory/`, `README.md` | `.env` (segredos) |
| `.env.example` | `*.xlsx`, `*.csv`, `*.log` |
| | `venv/`, `__pycache__/`, `sessions/` |

> `data/leads.duckdb` é o banco local (modo `DB_ENGINE=duckdb`). O banco externo
> PostgreSQL (modo `DB_ENGINE=postgres`) fica no servidor e não é versionado.

Comando de sync usado pelo mantenedor (sobrescreve o remoto):

```powershell
git add -A; git commit -m "sync local $(Get-Date -Format 'yyyy-MM-dd HH:mm')"; git push --force-with-lease origin main
```
