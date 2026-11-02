# 03 — Histórico de Mudanças

Registro do que mudou, por quê e o que ficou pendente. Mais recente primeiro.

---

## 2026-11-02 (segundo lote)

### Janela de envio (`WAHA_JANELA_ENVIO`)

- `WAHA_DIA_INICIO_HORA` (só a hora de início) foi substituída por
  `WAHA_JANELA_ENVIO="08:00-19:00"`: horário de **início e fim**, vazio = 24h.
- `whatsapp.py`: `_parse_janela`, `descrever_janela`, `janela_aberta`,
  `proxima_abertura`, `aviso_fora_da_janela`. Aceita `8-19`, `08:00-19:00` e
  atravessar a meia-noite; inválida → aviso e libera 24h.
- Fora da janela o menu bloqueia (inclusive o teste) e informa a próxima
  abertura. Campanha que chega no fim da janela é interrompida e deixa os leads
  restantes pendentes.
- O teto diário agora renova na **abertura da janela** (`inicio_da_janela_diaria`
  usa o início dela), coerente com "horário comercial".

### Teto diário de envios de WhatsApp (`WAHA_LIMITE_DIA`)

- Antes existia só `WAHA_LIMITE` (**por campanha**, não por dia) e a cadência
  `WAHA_CADENCIA` (ritmo, ex. `3:60` = 3/min). Não havia teto diário: rodar o
  menu várias vezes no mesmo dia reiniciava a contagem.
- Nova `WAHA_LIMITE_DIA` (vazio/0 = sem teto).
- Contador em `whatsapp.py`: `inicio_da_janela_diaria()`, `envios_hoje(db)`
  (COUNT em `whatsapp_envios_log` com `status='enviado'`; fallback para
  `leads.data_envio_whatsapp` se o log não existir) e `resumo_limite_dia(db)`.
- `disparar_campanha` corta o lote pelo restante do dia, aborta se o teto já
  estourou e **reconfere a cada envio** (campanha longa que cruza a virada do
  dia / outra campanha em paralelo).
- Menu (`main.py`) mostra `enviados/teto` antes dos filtros, bloqueia quando
  esgotado e usa o restante como padrão na pergunta de quantidade.
- Índice `idx_whatsapp_envios_log_data (data_envio)` no `schema.py` (PG e DuckDB).
- O contador é lido do banco, então reiniciar o programa/container não zera o dia.

## 2026-11-02

### Retomada de coleta (`coleta_progresso`)

- Antes: cada ciclo do `coleta_auto.py` percorria **todas** as UFs/cidades do
  zero. Parar o container no meio de uma coleta nacional significava recomeçar
  do Acre (os leads já gravados não duplicavam por causa do UPSERT, mas o
  trabalho era refeito).
- Nova tabela `coleta_progresso` (`nicho`, `uf`, `cidade` PK; `status`,
  `termos_total`, `leads_total`, `tentativas`, `erro`, timestamps), criada de
  forma idempotente pelo `LeadDatabase` na primeira gravação e também no
  `schema.py`.
- `LeadDatabase`: `progresso_carregar/iniciar/concluir/parcial/erro` e
  `semear_progresso_de_leads`.
- `coleta_auto.py`: `RETOMAR_COLETA=true` (padrão) filtra cidades já
  concluídas; `RECAPTURA_DIAS` (padrão 30; `0` = nunca refazer) define quando
  uma cidade concluída volta para a fila.
- Cidade com área bloqueada (captcha/timeout) fica `parcial` e é tentada de
  novo no ciclo seguinte — não fica 30 dias marcada como concluída.
- `SEMEAR_PROGRESSO=true` (padrão): na primeira execução com a tabela vazia,
  cidades que já têm leads no banco viram `concluida` (retoma uma coleta que
  rodou antes deste recurso). Nunca sobrescreve progresso existente.
- Validado nos dois backends: PostgreSQL (produção — tabela criada e semeada com
  405 cidades, 5.166 restantes das 5.571) e DuckDB (setup novo).

### CPU do scraper

- Navegador reaproveitado por thread: antes cada termo de busca abria um
  Chromium novo (~30 launches por cidade). Agora cada worker mantém um Chromium
  e abre só um contexto isolado por termo, reciclando o browser a cada
  `MAX_CONTEXTOS_POR_NAVEGADOR` (padrão 40) para conter memória.
- `BLOQUEAR_RECURSOS=true` (padrão) aborta `image`/`media`/`font` — a extração
  é no DOM, então nada de dados se perde e a CPU cai.
- Flags do Chromium para reduzir trabalho de renderização/rede.
- Contagem de perfis na rolagem passou a ser feita em JS (`page.evaluate`) em
  vez de `query_selector_all` + `get_attribute` por link a cada rolagem.
- Busca de Instagram usa seletor direto (`a[href*="instagram.com"]`).
- `SCRAPER_THREADS` (padrão 3) configurável: em VPS pequena, 1 ou 2.
- Runner passou a usar fila + workers (`queue`) com persistência na thread
  principal; `estatisticas` informa `areas_total/areas_ok/areas_erro`.


## 2026-10-31

### Migração para PostgreSQL + suporte dual (PostgreSQL/DuckDB)

- Banco externo PostgreSQL (`vps.agendamentoja.com/leads_db`) + mantido o DuckDB
  local como alternativa offline.
- Novo `src/backend.py`: abstrai conexão, placeholder (`?`/`%s`), leitura
  (DataFrame/tupla) e bulk upsert entre os dois bancos. `database.py`,
  `localidades_db.py` e `schema.py` não importam mais `duckdb`/`psycopg2`.
- `config.py` lê `DB_ENGINE` (postgres|duckdb), `DATABASE_URL` e `DUCKDB_PATH`.
  Inferência: DUCKDB_PATH → duckdb; senão DATABASE_URL → postgres; senão duckdb.
- `schema.py` reescrito para os dois bancos; corrige o gap da tabela `leads`
  (PK `lead_id` + UNIQUE `(nome,cidade)` + default `nextval('seq_leads_id')`).
- `requirements.txt`: readicionado `duckdb` + `psycopg2-binary`.
- `.env`: seção "BANCO DE DADOS — engine independente" com `DATABASE_URL` (senha
  com `@` percent-encoded) e config antiga comentada como referência.

### Cadência aleatória de envio WhatsApp (anti-bloqueio)

- Nova `WAHA_CADENCIA="X:Y"` no `.env` (ex.: `3:60` = 3 envios por minuto).
- `whatsapp.py`: `_parse_cadencia` + `_pausas_cadencia` distribuem os envios em
  pontos **aleatórios** dentro de cada janela (pausas variáveis, não fixas).
- Tem prioridade sobre `WAHA_INTERVALO` (fixo). `WAHA_CADENCIA` vazio → usa o fixo.

### Tabela `whatsapp_envios_log` (rastreamento)

- Log por envio com `lead_id`, `telefone` (dígitos) e `telefone_normalizado`
  (55DDDNUMERO), `chat_id`, `status`, `mensagem`, `payload`, `erro`, `data_envio`.
- JOIN pronto por `lead_id` ou `telefone`.

---

## 2026-10-30

### Templates de mensagem de WhatsApp (tabela + markdown)

- Nova tabela `templates_whatsapp` (`id`, `mensagem`, `descricao`, `ativo`),
  criada e seedada no `LeadDatabase.__init__` (idempotente, `id=1` =
  "Apresentação Agendamento Já").
- `listar_templates_ativos()` retorna só os ativos para o menu de envio.
- `_limpar_markdown_whatsapp` remove `**negrito**` e converte `[rótulo](url)` em
  texto plano antes do envio (o template usa markdown; o WhatsApp não renderiza).

### Menu de envio: template + filtros + teste

- `enviar_whatsapp_menu()` agora: escolhe template → aplica filtros → pergunta se
  quer **teste de envio** → confirma e dispara.
- Filtros de envio (menu "FILTROS DE ENVIO"): 0 todos / 1 por número / 2 por
  cidade / 3 por nicho. Número aceita parte e compara só dígitos.
- `testar_envio()`: digita um número com DDD ou escolhe um lead pendente.
- `disparar_campanha` passou a aceitar `leads` (DataFrame já filtrado) — sem isso
  os filtros eram ignorados no disparo (ele reconsultava o banco).

### Correção crítica: chatId `@lid` vs `@c.us` (WAHA)

- **Sintoma:** `500 Server Error` no `/api/sendText` para o número do mantenedor.
- **Causa:** número recente usa `@lid`; enviar `@c.us` retorna HTTP 500.
- **Correção:** `_resolver_chatid_waha` consulta `/api/checkNumberStatus` e usa o
  chatId retornado; fallback `@c.us` para números antigos.
- **Cache:** coluna `leads.chat_id_waha` + `salvar_chat_id_waha` — a resolução é
  feita uma única vez por lead (menos chamadas e reenvio mais rápido).
- `data_envio_whatsapp` continua gravada só no sucesso; `status_whatsapp` em
  `enviado`/`falhou`.

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
| Bairros oficiais via CNEFE 2022 | **Não implementar por hora** (decisão do mantenedor) |
| Resolução automática de captcha (2Captcha/CapMonster) | Não implementado; hoje pausa e desiste da área |
| Enriquecimento de e-mail a partir dos sites | Não iniciado |
| Base de bairros offline nacional | Coberto parcialmente pelo IBGE (643 cidades) |

## Problemas conhecidos (ambiente)

- **DBeaver aberto trava o DuckDB** → cache cai para as APIs.
- **Overpass/Nominatim instáveis** (502, timeout) → aquecimento por UF precisa de
  paciência e retomadas.
- Interprete global do mantenedor é Python 3.15; **usar `venv\Scripts\python.exe`**.
