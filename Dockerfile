# Usar una imagen oficial de Python como base - cambiando de Alpine a Slim
FROM python:3.9-slim

# Instalar git y dependencias necesarias para PyArrow
RUN apt-get update && apt-get install -y \
    git \
    build-essential \
    cmake \
    libboost-dev \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Establecer el directorio de trabajo
WORKDIR /app

# Clonar el repositorio directamente desde GitHub
RUN git clone https://github.com/Dir-Tecno/CBAMECAPACITA.git .

# Instalar dependencias
RUN pip install --no-cache-dir -r requirements.txt

# Crear directorios necesarios
RUN mkdir -p /app/logs /app/.streamlit /app/src/pages /app/src/config /app/src/utils

# Modificar el script para incluir las credenciales de la base de datos
RUN echo '#!/bin/bash\n\
echo "[db_credentials]" > /app/.streamlit/secrets.toml\n\
echo "DB_USER = \"$DB_USER\"" >> /app/.streamlit/secrets.toml\n\
echo "DB_PASSWORD = \"$DB_PASSWORD\"" >> /app/.streamlit/secrets.toml\n\
echo "DB_HOST = \"$DB_HOST\"" >> /app/.streamlit/secrets.toml\n\
echo "DB_PORT = \"$DB_PORT\"" >> /app/.streamlit/secrets.toml\n\
echo "DB_NAME = \"$DB_NAME\"" >> /app/.streamlit/secrets.toml\n\
echo "\n[HuggingFace]" >> /app/.streamlit/secrets.toml\n\
echo "huggingface_token = \"$HUGGINGFACE_TOKEN\"" >> /app/.streamlit/secrets.toml\n\
exec "$@"' > /app/entrypoint.sh && \
chmod +x /app/entrypoint.sh

# Agregar variables de entorno para la base de datos
ENV DB_USER=""
ENV DB_PASSWORD=""
ENV DB_HOST=""
ENV DB_PORT="3306"
ENV DB_NAME="CBAMECAPACITA"

# Exponer el puerto que usa Streamlit
EXPOSE 8501

# Variables de entorno para Python y logging
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app
ENV LOG_DIR=/app/logs

# Variable para el token de Hugging Face (se sobrescribirá al ejecutar el contenedor)
ENV HUGGINGFACE_TOKEN=""

# Usar el script como punto de entrada
ENTRYPOINT ["/app/entrypoint.sh"]

# Comando para ejecutar la aplicación
CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]