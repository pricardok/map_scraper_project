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
