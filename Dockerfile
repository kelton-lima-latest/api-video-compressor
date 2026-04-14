# --- ESTÁGIO 1: Builder ---
FROM python:3.11-slim AS builder

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Instalar apenas o necessário para COMPILAR as dependências (ex: psycopg2, ujson)
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Criar um virtualenv para isolar as dependências
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt


# --- ESTÁGIO 2: Final (Runtime) ---
FROM python:3.11-slim

# Dependências de execução (ex: ffmpeg e a biblioteca runtime do postgres)
RUN apt-get update && apt-get install -y \
    ffmpeg \
    libpq5 \
    && rm -rf /var/lib/apt/lists/*

# Configuração de segurança
RUN adduser --disabled-password --gecos '' appuser

WORKDIR /code

# Copiar o ambiente Python inteiro do estágio anterior
COPY --from=builder /opt/venv /opt/venv

# Garantir que o Python do container use o virtualenv copiado
ENV PATH="/opt/venv/bin:$PATH" \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Copiar o código fonte
COPY --chown=appuser:appuser . /code/

USER appuser

CMD ["python", "main.py"]