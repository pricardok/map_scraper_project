📄 Documentação do Projeto: MAP SCRAPER

🎯 1. Objetivo do Projeto

    Ferramenta automatizada e gratuita para prospecção de leads B2B locais que muitas vezes não possuem site, mas estão presentes no Google Maps e no Instagram.

    O sistema é capaz de receber um Estado e Cidade, descobrir os bairros de forma dinâmica, raspar os dados do Google Maps (Nome, Telefone, Instagram, Site) e gerenciar esses dados em um banco local, evitando duplicatas e permitindo o descarte de leads já trabalhados.

📦 2. Funcionalidades
A ferramenta foi construída com uma arquitetura modular e conta com os seguintes recursos:

    - Busca Dinâmica de Localidades: Integração com a API do IBGE para listar Estados e Cidades, e uso do Geopy (OpenStreetMap) como fallback para buscar bairros. Se o bairro não for encontrado, ele agrupa como "Geral" (buscando a cidade inteira).

    - Scraping em Multithreading: Uso do Playwright com ThreadPoolExecutor para abrir múltiplos navegadores simultaneamente e acelerar a coleta em diferentes bairros.

    - Tratamento de Dados (Data Cleansing):

    - Formatação automática de telefones para o padrão brasileiro (XX) XXXXX-XXXX.

    - Classificação automática do telefone: Celular (11 dígitos) ou Fixo (10 dígitos).

    - Banco de Dados Local (DuckDB): Armazenamento rápido e seguro em um arquivo local.

    - UPSERT: Se o lead já existe, ele atualiza os dados e a data de extração. Se for novo, insere.

    - Controle de Status: Leads podem ser marcados como ativo ou descartado. Se um lead descartado for encontrado novamente, o robô ignora e não atualiza.

    - Exportação para Excel: Gera um relatório limpo e ordenado apenas com os leads ativos.

🛠️ 3. Stack Tecnológica

    - Linguagem: Python 3.10+
    - Scraping: Playwright (Chromium)
    - Banco de Dados: DuckDB
    - Manipulação de Dados: Pandas
    - APIs: IBGE (Localidades) e Nominatim/Geopy (Bairros)
    - Tratamento: Regex (para telefones)

📁 4. Estrutura de Pastas

    map_scraper_project/
    │
    ├── data/                  # Onde o banco leads.duckdb é salvo
    ├── output/                # Onde os arquivos Excel finais são gerados
    │
    ├── src/                   # Código-fonte
    │   ├── __init__.py        
    │   ├── database.py        # Lógica do DuckDB (UPSERT, status, exportação)
    │   ├── locations.py       # Integração com IBGE e Geopy
    │   ├── scraper.py         # Robô Playwright e multithreading
    │   ├── utils.py           # Formatação de telefone (Fixo/Celular)
    │   └── main.py            # Menu interativo e orquestração
    │
    ├── requirements.txt       # Dependências do projeto
    └── README.md              # Este documento

🚀 5. Como Usar (Manual do Usuário)

    Passo 1: Instalação
    No terminal, dentro da pasta raiz do projeto, instale as dependências e o navegador do Playwright:

    python -m pip install -r requirements.txt
    python -m playwright install chromium
    Passo 2: Execução
    Rode o arquivo principal:

    python src/main.py
    Passo 3: Interação no Terminal
    O script fará 5 perguntas simples:

    UF do estado: Digite a sigla (ex: RS, SP, RJ).
    Cidade: Digite o nome (ex: Porto Alegre). Se houver mais de uma, ele pedirá para especificar.
    Nicho: Digite o que quer buscar (ex: barbearia, salao de beleza).
    Bairros: O robô buscará automaticamente. (Se não achar, ele usará Geral).
    Ver o navegador? Digite S se quiser ver o robô trabalhando na tela, ou N para rodar em segundo plano (mais rápido).

Passo 4: Resultados

    O banco de dados será atualizado em data/leads.duckdb.

    Um arquivo Excel será gerado em output/leads_nicho_cidade.xlsx.


🗄️ 6. Gerenciamento do Banco de Dados (Regras de Negócio)

    Se você quiser descartar um lead para que ele não seja mais exportado e não seja atualizado nas próximas buscas, você pode rodar um comando SQL direto no DuckDB (via DBeaver ou script Python):

    sql
    -- Para descartar um lead
    UPDATE leads SET status = 'descartado' WHERE nome = 'Nome da Barbearia';

    -- Para reativar um lead
    UPDATE leads SET status = 'ativo' WHERE nome = 'Nome da Barbearia';
    Nota: A regra do UPSERT no database.py garante que, se o robô achar uma barbearia "descartada", ele pula ela e não sobrescreve seus dados no banco.


🔮 7. Próximos Passos (Melhorias Futuras)

    Para escalar ainda mais este projeto, os próximos passos sugeridos são:

    Base de Bairros Offline: Baixar o dataset do Kaggle (bairros do Brasil) e jogar no DuckDB para não depender da API do Geopy (que limita a busca a 1 bairro por vez).

    Captcha Handling: Implementar um serviço ou lógica de pausa para evitar bloqueios do Google Maps em coletas muito grandes.

    Enriquecimento de E-mail: Criar um script secundário que lê os sites encontrados e busca e-mails de contato (usando Regex).