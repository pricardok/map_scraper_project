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
