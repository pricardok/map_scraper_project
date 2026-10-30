# 00 — Resumo do Projeto

**Map Scraper** — ferramenta local de prospecção de leads B2B a partir do Google Maps.

- **Entrada:** UF + cidade + nicho (ex.: `RS`, `Canoas`, `barbearias`).
- **Processo:** divide a busca por bairros, raspa o Google Maps com Playwright em
  multithread e extrai nome, telefone, Instagram e site.
- **Saída:** leads no DuckDB (`data/leads.duckdb`) + Excel em `output/`.
- **Extra:** dispara mensagens de WhatsApp via WAHA para leads já coletados, com
  templates reutilizáveis, filtros (número/cidade/nicho), teste de envio e cache
  do chatId resolvido (`@lid`/`@c.us`).

## Fluxo de alto nível

```
menu (src/main.py)
  └─ 1 Coletar    → locations.obter_termos_busca(cidade, uf)
                  → scraper.rodar_scraper_multithread(...)
                  → database.LeadDatabase.save_leads (UPSERT incremental)
                  → database.export_to_excel
  └─ 2 WhatsApp   → template ativo → filtros → teste → database.get_leads_para_envio
                  → whatsapp.disparar_campanha (WAHA, chatId via checkNumberStatus)
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
│   ├── database.py        LeadDatabase: leads, templates_whatsapp, UPSERT, Excel, log WAHA
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
