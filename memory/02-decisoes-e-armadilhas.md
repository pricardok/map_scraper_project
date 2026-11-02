# 02 — Decisões Técnicas e Armadilhas

Leia antes de mexer no código. Cada item já custou tempo de depuração.

---

## Banco: PostgreSQL OU DuckDB (via `src/backend.py`)

O projeto suporta dois backends, escolhidos por `DB_ENGINE` no `.env`:

- `DB_ENGINE=postgres` → banco externo (`DATABASE_URL` ou `DB_*`).
- `DB_ENGINE=duckdb` → arquivo local (`DUCKDB_PATH`, default `data/leads.duckdb`).

**Regra de ouro:** nenhum módulo além de `src/backend.py` importa `duckdb` ou
`psycopg2`. Todo acesso passa por `backend.execute/query_df/query_all/bulk_upsert`.
- Placeholder de parâmetro: use `backend.ph()` (`?` no DuckDB, `%s` no Postgres),
  NUNCA hardcode.
- `excluded.col` funciona no `ON CONFLICT` dos dois bancos.
- A DDL/seed fica em `schema.py` (roda uma vez: `python src/schema.py`).

### Armadilha do DuckDB: um processo por arquivo

**O `data/leads.duckdb` só pode ser aberto por UM processo.** Não existe
"read-only compartilhado" — até `duckdb.connect(..., read_only=True)` falha:

```
IO Error: Cannot open file "...data\leads.duckdb":
O arquivo já está sendo usado por outro processo.
```

Causas mais comuns: **DBeaver conectado**, scraper rodando, notebook aberto.

Consequências:
- `localidades_db` abre/fecha a conexão a cada operação (não mantém aberto).
- `LeadDatabase` mantém aberto durante o scraping — **não** abra outra conexão
  persistente no mesmo processo.
- `CacheIndisponivel` degrada com aviso em vez de quebrar.

### Armadilha do PostgreSQL: senha com `@` na URL

Na `DATABASE_URL`, caracteres especiais da senha devem ser "percent-encoded"
(`@` → `%40`, `:` → `%3A`, `/` → `%2F`). O `config.py` já decodifica com `unquote`.
Ex.: `aojbfoeub@@@111` → `aojbfoeub%40%40%40111`.

### Armadilha: identidade vs sequence (PostgreSQL)

No Postgres, `templates_whatsapp.id`, `whatsapp_envios_log.id` e
`localidades_bairros.id` são colunas **IDENTITY**. O `lead_id` de `leads` é
`integer` com sequence manual (`seq_leads_id`). Não assuma que todas as PKs se
comportam igual.

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

- `SALVAR=false` também desativa a escrita local e os menus **3** e **4**.
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

## WAHA: chatId `@c.us` vs `@lid` (HTTP 500)

Enviar `POST /api/sendText` com `chatId = 55DDDNUMERO@c.us` **falha com HTTP 500**
para números recentes do WhatsApp. Esses números foram migrados para o formato
**`@lid`** (hidden user ID).

- Diagnóstico: `GET /api/checkNumberStatus?session=default&phone=55DDD9XXXXXXXX`
  responde `{"numberExists": true, "chatId": "143172869029943@lid"}`.
- Correção: **sempre resolver o chatId via `checkNumberStatus` antes de enviar**,
  em vez de montar `@c.us` na mão (é o que a documentação da WAHA recomenda para
  números brasileiros).
- O chatId resolvido é **cacheado** na coluna `leads.chat_id_waha` — a consulta
  extra só acontece uma vez por lead.
- ⚠️ O payload do `sendText` está correto (`{session, chatId, text}` + header
  `X-Api-Key`); o erro 500 era **só** o formato do `chatId`, não o endpoint.

---

## WAHA: cadência aleatória (anti-bloqueio)

Enviar com pausa fixa (ex.: 15s, 15s, 15s) é fácil de detectar e leva a bloqueio.

- `WAHA_CADENCIA="X:Y"` (ex.: `3:60` = 3 envios/minuto) faz os envios caírem em
  **pontos aleatórios** dentro de cada janela de Y segundos → pausas variáveis.
- Tem prioridade sobre `WAHA_INTERVALO` (pausa fixa, usada só se `WAHA_CADENCIA`
  estiver vazio).
- Implementação: `_pausas_cadencia(total, envios_janela, janela)` em `whatsapp.py`.

---

## WAHA: limites e janela (coisas diferentes)

Confusão comum: achar que `WAHA_LIMITE` é o teto diário. Não é.

| Variável | O que faz | Reiniciar zera? |
|---|---|---|
| `WAHA_CADENCIA` (`3:60`) | **ritmo**: 3 por minuto | — |
| `WAHA_JANELA_ENVIO` (`08:00-19:00`) | **horário**: só envia dentro | — |
| `WAHA_LIMITE` (`150`) | **campanha**: máximo por execução | sim |
| `WAHA_LIMITE_DIA` (`150`) | **dia**: soma todas as campanhas | **não** (lê o log) |

- O contador do dia vem de `whatsapp_envios_log` (`status='enviado'`) e não da
  memória do processo — por isso reiniciar o programa/container não "libera"
  mais envios.
- O corte do dia é `inicio_da_janela_diaria()`, que devolve a **abertura da
  janela** (08:00 no exemplo). Sem janela, é meia-noite. Comparado com o
  `data_envio` gravado pelo próprio processo: não depende do timezone do banco.
- Envios com `status='falhou'` **não** contam para o teto.
- `disparar_campanha` reconsulta janela e contador **a cada envio**: campanha
  longa que cruza o fim do horário ou a virada do dia para no ponto certo, e
  duas campanhas em paralelo continuam respeitando o teto.
- Janela que atravessa a meia-noite (`22:00-06:00`) é válida: `janela_aberta`
  compara minutos e trata `início > fim` como travessia.
- Janela inválida (ex.: `25:00-19:00`) imprime aviso e vira "sem janela" (24h).
  A escolha é deliberada: não travar a operação por erro de digitação.
- `inicio == fim` (ex.: `08:00-08:00`) também é tratado como 24h, não como
  janela de duração zero.

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

- O runner usa uma fila (`queue.Queue`) + N threads trabalhadoras
  (`SCRAPER_THREADS`). Cada worker tem seu próprio Chromium (thread-local,
  criado e fechado na mesma thread) e reusa entre as áreas da cidade.
- Os workers **não** escrevem no banco: devolvem o resultado por outra fila e o
  `save_callback` roda na thread principal, mantendo uma única conexão.
- O cooldown anti-captcha usa `_cooldown_lock` + variável global `_cooldown_ate`.
- `vistos`/`todos_leads` são tocados só pela thread principal (não precisa de
  lock).

---

## Retomada da coleta (`coleta_progresso`)

- A fonte da verdade do "onde parou" é a tabela `coleta_progresso`
  (`nicho, uf, cidade`) — **não** o `leads`, que não sabe se a cidade terminou.
- Só `status='concluida'` é pulado. `em_andamento` (container morto no meio),
  `parcial` (captcha/timeout em alguma área) e `erro` voltam para a fila no
  próximo ciclo.
- `RECAPTURA_DIAS=30` faz a cidade concluída voltar depois de 30 dias;
  `0` = nunca refazer.
- `SEMEAR_PROGRESSO=true` só roda quando a tabela está vazia e usa
  `ON CONFLICT DO NOTHING`: nunca sobrescreve progresso real.
- `RETOMAR_COLETA=false` restaura o comportamento antigo (refaz tudo a cada
  ciclo) — útil para um "passe" completo de atualização.

### Limite do seed a partir de `leads`

`semear_progresso_de_leads` enxerga só cidades que **têm** lead. Cidade
coletada que voltou vazia (comum em município pequeno) não aparece em `leads`,
então é recolhida uma vez depois do restart — barato e sem duplicar.

### Criar a tabela manualmente (PostgreSQL)

A tabela é criada sozinha na primeira gravação (`_garantir_tabela_progresso`)
e também por `python src/schema.py`. Se precisar criar na mão:

```sql
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
);
```

Panorama:

```sql
SELECT uf, status, COUNT(*)
FROM coleta_progresso
GROUP BY uf, status ORDER BY uf, status;
```

## CPU: o gargalo é o Chromium, não o Python

- `image`/`media`/`font` bloqueados (`BLOQUEAR_RECURSOS`) e flags de render
  reduzem bastante o uso de CPU; a extração continua igual (DOM).
- Escalar `SCRAPER_THREADS` acima de 3 não acelera: esbarra no
  `_marcar_bloqueio_global` do Google. Em máquina pequena, 1–2 threads.
- Se a CPU continuar em 100%, o próximo passo é limitar o container
  (`cpus: 1.5` no compose) — não adianta reduzir sleep, que não consome CPU.

---

## Coisas que parecem bug mas não são

- `"IBGE não publica bairros para X"` → cidade com 1 distrito (ver acima).
- `"Base local ... sem bairros (fonte: cidade)"` → já tentou, o OSM não tinha nada.
- `"LOCALIDADES_SALVAR=false: a base local não será alterada"` → modo leitura.
- `"Aviso: base local ... indisponível (arquivo em uso)"` → feche o DBeaver.
