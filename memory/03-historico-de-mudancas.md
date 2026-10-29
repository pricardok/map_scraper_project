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
| Bairros oficiais via CNEFE 2022 | **Não implementar por hora** (decisão do mantenedor) |
| Resolução automática de captcha (2Captcha/CapMonster) | Não implementado; hoje pausa e desiste da área |
| Enriquecimento de e-mail a partir dos sites | Não iniciado |
| Base de bairros offline nacional | Coberto parcialmente pelo IBGE (643 cidades) |

## Problemas conhecidos (ambiente)

- **DBeaver aberto trava o DuckDB** → cache cai para as APIs.
- **Overpass/Nominatim instáveis** (502, timeout) → aquecimento por UF precisa de
  paciência e retomadas.
- Interprete global do mantenedor é Python 3.15; **usar `venv\Scripts\python.exe`**.
