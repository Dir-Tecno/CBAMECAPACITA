import streamlit as st
import pandas as pd
from huggingface_hub import hf_hub_download
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime

# Page configuration
st.set_page_config(page_title="Cursos CBAME", page_icon="📚", layout="wide")

# Custom CSS for better styling
st.markdown("""
<style>
    .main {
        padding: 1rem 2rem;
    }
    .stApp {
        background-color: #ffffff;
    }
    .stTitle {
        font-size: 2.5rem;
        font-weight: bold;
        color: #2c3e50;
    }
    .stSidebar {
        background-color: #f7f9fc;
        padding: 1rem;
    }
    .stButton > button {
        background-color: #3498db;
        color: white;
        border-radius: 5px;
        border: none;
        padding: 0.5rem 1rem;
    }
    .stDataFrame {
        border: 1px solid #ddd;
        border-radius: 5px;
        overflow: hidden;
    }
    .stDataFrame th, .stDataFrame td {
        padding: 0.5rem;
        text-align: left;
    }
    .stDataFrame th {
        background-color: #f2f2f2;
    }
</style>
""", unsafe_allow_html=True)

# Title and description
st.title("📚 Dashboard de Cursos CBAME")
st.markdown("""---""")

# Configuration for Hugging Face
REPO_ID = "Dir-Tecno/CBAMECAPACITA"
HF_TOKEN = st.secrets["HuggingFace"]["huggingface_token"]

# Function to load data from HuggingFace
def load_data_from_huggingface(repo_id, token):
    file_path_1 = hf_hub_download(repo_id, filename="VT_CURSOS_X_LOCALIDAD.csv", token=token, repo_type='dataset')
    file_path_2 = hf_hub_download(repo_id, filename="VT_DOCENTES_X_CURSO.csv", token=token, repo_type='dataset')
    
    df_cursos = pd.read_csv(file_path_1)
    df_docentes = pd.read_csv(file_path_2)
    
    return [df_cursos, df_docentes], [file_path_1, file_path_2]

# Function to load data
def load_data():
    try:
        # Load data using the helper function
        dfs, file_dates = load_data_from_huggingface(REPO_ID, token=HF_TOKEN)
        
        # Assign dataframes
        df_cursos = dfs[0]  # Assuming VT_CURSO_X_LOCALIDAD.csv is the first file
        df_docentes = dfs[1]  # Assuming VT_DOCENTES_X_CURSO.csv is the second file
        
        return df_cursos, df_docentes
    except Exception as e:
        st.error(f"Error loading data: {str(e)}")
        return None, None

# Load the data
df_cursos, df_docentes = load_data()

# ... existing code ...

if df_cursos is not None and df_docentes is not None:
    # Convert 'FEC_INICIO' and 'FEC_FIN' to datetime with specified format
    df_cursos['FEC_INICIO'] = pd.to_datetime(df_cursos['FEC_INICIO'], format='%d/%m/%Y %H:%M:%S', errors='coerce')
    df_cursos['FEC_FIN'] = pd.to_datetime(df_cursos['FEC_FIN'], format='%d/%m/%Y %H:%M:%S', errors='coerce')
    
    # Sidebar filters
    st.sidebar.title("Filtros")
    
    # Date range slider
    st.sidebar.subheader("Rango de Fechas")
    min_date = df_cursos['FEC_INICIO'].min().date()
    max_date = df_cursos['FEC_FIN'].max().date()
    date_range = st.sidebar.slider(
        "Seleccionar rango de fechas",
        min_value=min_date,
        max_value=max_date,
        value=(min_date, max_date),
        format="DD/MM/YYYY"
    )
    
    # Apply date filter
    filtered_cursos = df_cursos[(df_cursos['FEC_INICIO'] >= pd.to_datetime(date_range[0])) & (df_cursos['FEC_FIN'] <= pd.to_datetime(date_range[1]))]
        
    # Sector Productivo filter
    sectores = ['Todos'] + sorted(df_cursos['N_SECTOR_PRODUCTIVO'].unique().tolist())
    sector_selected = st.sidebar.selectbox("Sector Productivo", sectores)
    
    # Localidad filter
    localidades = ['Todas'] + sorted(df_cursos['N_LOCALIDAD'].unique().tolist())
    localidad_selected = st.sidebar.selectbox("Localidad", localidades)
    
    # Apply filters
    filtered_cursos = df_cursos.copy()
    if sector_selected != 'Todos':
        filtered_cursos = filtered_cursos[filtered_cursos['N_SECTOR_PRODUCTIVO'] == sector_selected]
    if localidad_selected != 'Todas':
        filtered_cursos = filtered_cursos[filtered_cursos['N_LOCALIDAD'] == localidad_selected]
    
    # Main dashboard content
    col1, col2 = st.columns(2)
    
    with col1:
        # Cursos por Sector Productivo
        st.subheader("Cursos por Sector Productivo")
        fig_sector = px.pie(
            filtered_cursos,
            names='N_SECTOR_PRODUCTIVO',
            values='CUPO',
            title='Distribución de Cupos por Sector Productivo'
        )
        st.plotly_chart(fig_sector, use_container_width=True)
    
    with col2:
        # Cursos por Localidad
        st.subheader("Cursos por Localidad")
        fig_localidad = px.bar(
            filtered_cursos.groupby('N_LOCALIDAD').size().reset_index(name='count'),
            x='N_LOCALIDAD',
            y='count',
            title='Cantidad de Cursos por Localidad'
        )
        st.plotly_chart(fig_localidad, use_container_width=True)
    
    # Detailed information
    st.markdown("""---""")
    st.subheader("Detalle de Cursos")
    
    # Display filtered courses in a table
    st.dataframe(
        filtered_cursos[[
            'N_CURSO', 'N_CERTIFICACION', 'N_TRAYECTO_FORMATIVO',
            'N_SECTOR_PRODUCTIVO', 'CUPO', 'FEC_INICIO', 'FEC_FIN',
            'N_LOCALIDAD', 'N_BARRIO'
        ]]
    )
else:
    st.error("No se pudieron cargar los datos. Por favor, verifica la conexión y los archivos.")