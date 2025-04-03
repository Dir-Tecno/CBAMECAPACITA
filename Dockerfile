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

# Crear directorio para logs y secrets
RUN mkdir -p /app/logs /app/.streamlit

# Crear un script para generar el archivo secrets.toml en tiempo de ejecución
RUN echo '#!/bin/bash\necho "[HuggingFace]" > /app/.streamlit/secrets.toml\necho "huggingface_token = \"$HUGGINGFACE_TOKEN\"" >> /app/.streamlit/secrets.toml\nexec "$@"' > /app/entrypoint.sh && \
    chmod +x /app/entrypoint.sh

# Exponer el puerto que usa Streamlit
EXPOSE 8501

# Variables de entorno para Python
ENV PYTHONUNBUFFERED=1
# Variable para el token de Hugging Face (se sobrescribirá al ejecutar el contenedor)
ENV HUGGINGFACE_TOKEN=""

# Usar el script como punto de entrada
ENTRYPOINT ["/app/entrypoint.sh"]

# Comando para ejecutar la aplicación
CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]