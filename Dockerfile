# Dockerfile — Map Scraper
# Imagem para rodar a coleta automática (sem menu) em container.
FROM python:3.11-slim

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

# Dependências de sistema (Playwright instala o resto com --with-deps).
RUN apt-get update \
    && apt-get install -y --no-install-recommends ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Dependências Python do projeto.
COPY requirements.txt .
RUN pip install -r requirements.txt

# Chromium do Playwright + bibliotecas de sistema necessárias.
RUN playwright install --with-deps chromium

# Código-fonte.
COPY src/ ./src/

# Volumes montados no compose: /app/data (DuckDB) e /app/output (Excel).
RUN mkdir -p /app/data /app/output

# Runner não-interativo (configuração via variáveis de ambiente).
CMD ["python", "src/coleta_auto.py"]
