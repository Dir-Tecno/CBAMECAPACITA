#!/bin/bash

# Cambiar al directorio del proyecto
cd "$(dirname "$0")"

# Activar el entorno virtual
source venv/bin/activate

# Ejecutar la aplicación Streamlit
streamlit run app.py

# Desactivar el entorno virtual al salir
deactivate
