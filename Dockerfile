# Usar una imagen oficial de Python como base
FROM python:3.9-slim

# Instalar solo las dependencias necesarias
RUN apt-get update && apt-get install -y \
    git \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Establecer el directorio de trabajo
WORKDIR /app

# Clonar el repositorio manteniendo el historial de Git
RUN git clone https://github.com/Dir-Tecno/CBAMECAPACITA.git . && \
    git fetch origin && \
    git reset --hard origin/main

# Crear directorios necesarios
RUN mkdir -p /app/logs /app/.streamlit /app/src/pages /app/src/config /app/src/utils

# Copiar requirements e instalar dependencias
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Script para las credenciales
RUN echo '#!/bin/bash\n\
echo "[db_credentials]" > /app/.streamlit/secrets.toml\n\
echo "DB_USER = \"${DB_USER}\"" >> /app/.streamlit/secrets.toml\n\
echo "DB_PASSWORD = \"${DB_PASSWORD}\"" >> /app/.streamlit/secrets.toml\n\
echo "DB_HOST = \"${DB_HOST}\"" >> /app/.streamlit/secrets.toml\n\
echo "DB_PORT = \"${DB_PORT}\"" >> /app/.streamlit/secrets.toml\n\
echo "DB_NAME = \"${DB_NAME}\"" >> /app/.streamlit/secrets.toml\n\
echo "\n[HuggingFace]" >> /app/.streamlit/secrets.toml\n\
echo "huggingface_token = \"${HUGGINGFACE_TOKEN}\"" >> /app/.streamlit/secrets.toml\n\
exec "$@"' > /app/entrypoint.sh && \
chmod +x /app/entrypoint.sh

# Variables de entorno
ENV DB_USER="" \
    DB_PASSWORD="" \
    DB_HOST="" \
    DB_PORT="3306" \
    DB_NAME="CBAMECAPACITA" \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app \
    LOG_DIR=/app/logs \
    HUGGINGFACE_TOKEN=""

# Exponer el puerto que usa Streamlit
EXPOSE 8501

# Punto de entrada y comando
ENTRYPOINT ["/app/entrypoint.sh"]
CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]