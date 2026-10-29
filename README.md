Documentação do Projeto: MAP SCRAPER

1. Objetivo do Projeto

    Ferramenta automatizada e gratuita para prospecção de leads B2B locais que muitas vezes não possuem site, mas estão presentes no Google Maps e no Instagram.

    O sistema é capaz de receber um Estado e Cidade, descobrir os bairros de forma dinâmica, raspar os dados do Google Maps (Nome, Telefone, Instagram, Site) e gerenciar esses dados em um banco local, evitando duplicatas e permitindo o descarte de leads já trabalhados.

2. Funcionalidades

    A ferramenta foi construída com uma arquitetura modular e conta com os seguintes recursos:

        - Busca Dinâmica de Localidades: Integração com a API do IBGE para listar Estados e Cidades, e uso do Nominatim + Overpass (OpenStreetMap) para descobrir os bairros da cidade. Se nenhum bairro for encontrado, ele faz fallback buscando a cidade inteira.

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
    ├── output/                # Onde os arquivos Excel finais são gerados
    │
    ├── src/                   # Código-fonte
    │   ├── __init__.py        
    │   ├── database.py        # Lógica do DuckDB (UPSERT, status, exportação, log de envio)
    │   ├── locations.py       # Integração com IBGE, Nominatim e Overpass
    │   ├── scraper.py         # Robô Playwright e multithreading
    │   ├── utils.py           # Formatação de telefone (Fixo/Celular)
    │   ├── whatsapp.py        # Envio via WAHA (WhatsApp HTTP API)
    │   └── main.py            # Menu interativo e orquestração
    │
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
    Rode o arquivo principal:

    python src/main.py
    Passo 3: Interação no Terminal
    O menu tem 3 opções:

    1 - Coletar leads: faz 5 perguntas simples (UF, Cidade, Nicho, Bairros automáticos, Ver navegador).
    2 - Enviar mensagens WhatsApp: envia para os leads celulares pendentes (ver seção 7).
    3 - Sair.

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

8. Próximos Passos (Melhorias Futuras)

    Já implementado:
    - Cobertura por bairros (Nominatim + Overpass) com fallback para a cidade inteira.
    - Rolagem dinâmica dos resultados do Google Maps.
    - Retry, deduplicação intra-execução e salvamento incremental.
    - Medidas anti-bloqueio (user-agent, viewport e pausas aleatórias).
    - Envio de WhatsApp via WAHA com log de envio (só celulares, sem spam).

    Pendências sugeridas:
    - Base de Bairros Offline: Baixar o dataset do Kaggle (bairros do Brasil) e jogar no DuckDB para não depender das APIs do OpenStreetMap (Nominatim/Overpass).

    - Captcha Handling: Implementar um serviço de resolução ou lógica de pausa mais longa para evitar bloqueios do Google Maps em coletas muito grandes.

    - Enriquecimento de E-mail: Criar um script secundário que lê os sites encontrados e busca e-mails de contato (usando Regex).

