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

        O banco de dados será atualizado (PostgreSQL ou DuckDB, conforme o .env).

        Um arquivo Excel será gerado em output/leads_nicho_cidade.xlsx.

    Execução em Docker (servidor, sem menu)

    Para rodar sozinho num servidor (coleta automática contínua), o projeto tem
    um Dockerfile e um docker-compose.yml. O container usa o runner
    `src/coleta_auto.py` (não-interativo), configurado por variáveis de ambiente:

    ```
    NICHO=barbearias          # nicho a coletar
    UFS=                      # vazio = todas as UFs do Brasil; ou RS,SP,RJ
    MAX_CIDADES=0             # 0 = todas as cidades de cada UF
    MAX_BAIRROS=30            # bairros por cidade
    AQUECER_BAIRROS=false     # resolver bairros antes da coleta
    SINCRONIZAR=false         # baixar IBGE antes (banco novo)
    LOOP=false                # true = rodar em loop contínuo
    LOOP_PAUSA_SEGUNDOS=3600  # pausa entre ciclos (LOOP=true)
    RETOMAR_COLETA=true       # pular cidades já concluídas (retoma de onde parou)
    RECAPTURA_DIAS=30         # refazer concluídas há mais de N dias (0 = nunca)
    SEMEAR_PROGRESSO=true     # 1ª execução: cidades com leads viram concluídas
    SCRAPER_THREADS=3         # navegadores em paralelo (VPS pequena: 1 ou 2)
    BLOQUEAR_RECURSOS=true    # desliga imagens/mídia (reduz CPU)
    MAX_CONTEXTOS_POR_NAVEGADOR=40  # recicla o Chromium a cada N áreas
    ```

    Os comentários acima são ilustrativos. No `.env` real o comentário deve ficar
    em linha própria — na mesma linha ele passa a fazer parte do valor.

    Subir e acompanhar:

    ```
    docker compose up -d --build
    docker compose logs -f app
    ```

    Os comandos do dia a dia (rebuild, parar, reiniciar, ver progresso) estão
    na seção 14; sem Docker, use a seção 15.

    O `.env` é injetado no container via `env_file` (banco e WAHA). Os volumes
    `./data` e `./output` são montados para persistir DuckDB/Excel localmente.


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
    WAHA_CADENCIA=3:60
    WAHA_JANELA_ENVIO=08:00-19:00
    WAHA_LIMITE=
    WAHA_LIMITE_DIA=150
    ```

    Flags de comportamento:
    - WAHA_ATIVO: se false, desliga o envio de WhatsApp (não tenta enviar).
    - SOMENTE_ENVIO: se true, pula a coleta e vai direto para o envio
      (equivalente a rodar `python src/main.py --so-enviar`).

    Os quatro controles abaixo são independentes — não confunda:
    - WAHA_CADENCIA (ritmo): "X a cada Y segundos". `3:60` = 3 mensagens por
      minuto, com intervalos aleatórios. Vazio = usa WAHA_INTERVALO (pausa fixa
      de 13s).
    - WAHA_JANELA_ENVIO (horário): "INÍCIO-FIM". `08:00-19:00` = só no horário
      comercial. Vazio = a qualquer hora. Aceita travessia de meia-noite
      (`22:00-06:00`). Formato curto também vale (`8-19`).
    - WAHA_LIMITE (campanha): máximo de leads por execução do envio.
    - WAHA_LIMITE_DIA (dia): máximo de mensagens por dia, somando todas as
      campanhas. Vazio/0 = sem teto diário.

    Exemplo: `WAHA_CADENCIA=3:60` + `WAHA_JANELA_ENVIO=08:00-19:00` +
    `WAHA_LIMITE_DIA=150` = 3 por minuto, apenas entre 8h e 19h, parando quando o
    dia chegar a 150 envios. Os demais leads ficam pendentes para o dia
    seguinte. Rodar de novo no mesmo dia não fura o teto: o contador vem do log
    no banco, não da memória do processo.

    Como a janela se comporta:
    - Fora dela, o menu avisa e não envia nada (nem o teste) e mostra quando
      reabre (ex.: "Próximo envio a partir de 03/11 às 08:00").
    - Campanha que chega no fim da janela é interrompida no meio; os leads
      restantes continuam pendentes para o próximo horário.
    - O teto diário renova na **abertura da janela** (às 08:00 no exemplo), não
      à meia-noite.
    - Janela inválida (ex.: `25:00-19:00`) gera aviso e o envio fica liberado
      24h, para não travar a operação por erro de digitação.

    Observação: o envio de **teste** (antes da campanha) não é registrado no
    log, então não consome o teto diário.

    Regras de envio (evita spam):
    - Só envia para leads com status = 'ativo'.
    - Só envia para tipo_telefone = 'Celular' (fixos são ignorados).
    - Só envia para leads ainda não enviados (status_whatsapp = 'pendente' ou NULL).
    - Intervalo de WAHA_INTERVALO segundos entre envios (se não houver cadência).

    Logs no banco:
    - status_whatsapp: 'pendente', 'enviado' ou 'falhou'.
    - data_envio_whatsapp: gravada apenas quando o envio é bem-sucedido.
    - whatsapp_envios_log: uma linha por tentativa, com data_envio. É a fonte
      usada para contar o teto diário (só status = 'enviado' conta).

    Consultar o consumo do dia:
    ```sql
    SELECT COUNT(*) FROM whatsapp_envios_log
    WHERE status = 'enviado' AND data_envio >= CURRENT_DATE;
    ```

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

14. Rodando via Docker (comandos do dia a dia)

    Todos os comandos são executados na raiz do projeto (onde está o
    docker-compose.yml), no terminal do host.

    Subir / atualizar
    ```
    docker compose up -d --build     # build da imagem + sobe em background
    docker compose logs -f app       # acompanha os logs em tempo real
    docker compose ps                # status do container
    ```

    Rebuild (`--build`) é obrigatório sempre que mudar algo em `src/`, no
    Dockerfile ou no requirements.txt. `docker compose restart` NÃO pega código
    nem `.env` novos — ele só reinicia o processo.

    Parar / reiniciar
    ```
    docker compose stop      # para o container (o progresso no banco é preservado)
    docker compose start     # sobe o mesmo container de novo
    docker compose restart   # reinicia o processo (sem rebuild e sem reler o .env)
    docker compose down      # remove o container (os dados ficam nos volumes)
    ```

    Depois de editar o `.env`:
    ```
    docker compose up -d     # recria o container com as novas variáveis
    ```

    Abrir shell / rodar utilitários dentro do container:
    ```
    docker compose exec app sh
    docker compose exec app python src/schema.py   # cria/ajusta tabelas (idempotente)
    ```

    Ver o progresso da coleta de dentro do container:
    ```
    docker compose exec app python -c "from src.database import LeadDatabase as L; db=L(); p=db.progresso_carregar('barbearias'); print('cidades:', len(p), '| concluidas:', sum(1 for v in p.values() if v['status']=='concluida')); db.close()"
    ```

    Diagnóstico:
    ```
    docker compose logs --tail=100 app   # últimas 100 linhas
    docker compose top                   # processos dentro do container
    docker stats map_scraper             # CPU e memória em tempo real
    ```

    O compose usa `restart: unless-stopped`: se a VPS reiniciar, o container volta
    sozinho e, como o progresso está no banco, ele retoma da cidade seguinte.

15. Rodando sem Docker (local)

    Requisitos: Python 3.11+ e o `.env` na raiz. Instalação (uma única vez):

    Windows (PowerShell):
    ```
    python -m venv venv
    .\venv\Scripts\Activate.ps1
    python -m pip install -r requirements.txt
    python -m playwright install chromium
    Copy-Item .env.example .env
    ```

    Linux/macOS:
    ```
    python3 -m venv venv
    source venv/bin/activate
    python -m pip install -r requirements.txt
    python -m playwright install --with-deps chromium
    cp .env.example .env
    ```

    Comandos de execução:
    ```
    python src/main.py              # menu interativo (coleta, envio, IBGE, bairros)
    python src/main.py --so-enviar  # pula a coleta e só dispara o WhatsApp
    python src/coleta_auto.py       # coleta automática contínua (mesmo runner do Docker)
    python src/schema.py            # cria/ajusta as tabelas do banco
    ```

    O `coleta_auto.py` é o equivalente ao container: lê o `.env`, percorre as
    UFs/cidades e grava o progresso em `coleta_progresso`. Para deixar rodando
    depois de fechar o terminal:

    Linux/macOS:
    ```
    nohup python src/coleta_auto.py > coleta.log 2>&1 &
    tail -f coleta.log
    ```

    Windows (PowerShell):
    ```
    Start-Process -FilePath ".\venv\Scripts\python.exe" -ArgumentList "src\coleta_auto.py" -RedirectStandardOutput coleta.log -RedirectStandardError coleta.err -WindowStyle Hidden
    Get-Content coleta.log -Wait
    ```

    Para parar: `Ctrl+C` no terminal (ou `Stop-Process -Id <PID>` no Windows).
    O que já foi coletado fica salvo e a próxima execução retoma de onde parou.

    Diferença em relação ao Docker: no Docker o `.env` entra por `env_file` e
    `./data`/`./output` são volumes; localmente os caminhos são os do próprio
    projeto (`data/leads.duckdb` e `output/`). O banco usado depende do `.env`
    (`DB_ENGINE=postgres` ou `duckdb`).

16. Retomada e acompanhamento da coleta

    - `RETOMAR_COLETA=true` (padrão): pula as cidades já concluídas, registradas
      em `coleta_progresso`.
    - `RECAPTURA_DIAS=30`: cidade concluída volta para a fila depois de 30 dias
      (`0` = nunca refazer).
    - `SEMEAR_PROGRESSO=true`: na primeira execução com a tabela vazia, cidades
      que já têm leads no banco são marcadas como concluídas.
    - Cidade interrompida (captcha, timeout, máquina desligada) fica
      `em_andamento`, `parcial` ou `erro` e volta automaticamente no próximo ciclo.
    - `RETOMAR_COLETA=false` restaura o comportamento antigo (refaz tudo a cada
      ciclo), útil para um passe completo de atualização.

    Consultas úteis (DBeaver, psql ou qualquer cliente do banco):
    ```sql
    -- panorama por UF
    SELECT uf, status, COUNT(*) FROM coleta_progresso
    GROUP BY uf, status ORDER BY uf, status;

    -- o que está sendo coletado agora
    SELECT uf, cidade, status, leads_total, tentativas, atualizado_em
    FROM coleta_progresso
    WHERE status IN ('em_andamento', 'parcial', 'erro')
    ORDER BY atualizado_em DESC;

    -- total concluído x pendente
    SELECT status, COUNT(*) FROM coleta_progresso GROUP BY status;
    ```

    Se a tabela ainda não existir no banco (imagem antiga), rode
    `python src/schema.py` ou `docker compose exec app python src/schema.py`.
    Ela também é criada sozinha na primeira cidade coletada.