# Usamos a versão slim para manter a imagem leve
FROM python:3.11-slim

# Definir variáveis de ambiente para o Python
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# 1. Instalar dependências do sistema operacional (Obrigatoriamente como root)
RUN apt-get update && apt-get install -y \
    ffmpeg \
    libpq-dev \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# 2. Cria o usuário de sistema restrito
RUN adduser --disabled-password --gecos '' appuser

WORKDIR /code

# 3. Copia e instala as dependências do Python (Ainda como root para gravar no sistema)
COPY requirements.txt /code/
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# 4. Copia TODO o código fonte já passando a propriedade para o appuser
# (Isso evita a necessidade de rodar um RUN chown separado, deixando a imagem mais leve)
COPY --chown=appuser:appuser . /code/

# 5. Última linha: Diz ao Docker para assumir o usuário seguro daqui em diante
USER appuser