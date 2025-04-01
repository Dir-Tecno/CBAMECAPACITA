import streamlit as st
import pandas as pd
from huggingface_hub import hf_hub_download
import plotly.express as px
from datetime import datetime, timedelta

# Page configuration
st.set_page_config(page_title="Cursos CBAME", page_icon="📚", layout="wide")

st.markdown("""
<style>
    .main {
        padding: 2rem 3rem;
        background-color: #f0f2f5;
    }
    .stApp {
        background-color: #ffffff;
    }
    .stTitle {
        font-size: 3rem;
        font-weight: bold;
        color: #2c3e50;
        font-family: 'Arial', sans-serif;
    }
    .stSidebar {
        background-color: #f8f9fa;
        padding: 1rem;
        border-right: 1px solid #dee2e6;
    }
    .stButton > button {
        background-color: #007bff;
        color: white;
        border-radius: 5px;
        border: none;
        padding: 0.5rem 1rem;
        font-family: 'Arial', sans-serif;
    }
    .stDataFrame {
        border: 1px solid #dee2e6;
        border-radius: 5px;
        overflow: hidden;
    }
    .stDataFrame th, .stDataFrame td {
        padding: 0.75rem;
        text-align: left;
        font-family: 'Arial', sans-serif;
    }
    .stDataFrame th {
        background-color: #e9ecef;
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
    file_path_geojson = hf_hub_download(repo_id, filename="capa_gobiernoslocales_2010.geojson", token=token, repo_type='dataset')
    
    df_cursos = pd.read_csv(file_path_1)
    df_docentes = pd.read_csv(file_path_2)
    
    return [df_cursos, df_docentes, file_path_geojson], [file_path_1, file_path_2, file_path_geojson]

# Function to load data
def load_data():
    try:
        # Load data using the helper function
        dfs, file_dates = load_data_from_huggingface(REPO_ID, token=HF_TOKEN)
        
        # Assign dataframes
        df_cursos = dfs[0]  # Assuming VT_CURSO_X_LOCALIDAD.csv is the first file
        df_docentes = dfs[1]  # Assuming VT_DOCENTES_X_CURSO.csv is the second file
        geojson_path = dfs[2]  # Assuming capa_gobiernoslocales_2010.geojson is the third file
        
        return df_cursos, df_docentes, geojson_path
    except Exception as e:
        st.error(f"Error loading data: {str(e)}")
        return None, None, None

# Load the data
df_cursos, df_docentes, geojson_path = load_data()

if df_cursos is not None and df_docentes is not None:

    # Convertir fechas permitiendo valores nulos en FEC_FIN
    df_cursos['FEC_INICIO'] = pd.to_datetime(df_cursos['FEC_INICIO'], format='%d/%m/%Y %H:%M', errors='coerce')
    df_cursos['FEC_FIN'] = pd.to_datetime(df_cursos['FEC_FIN'], format='%d/%m/%Y %H:%M', errors='coerce')

    # Tabs
    tab1, tab2 = st.tabs(["📊 Análisis de Cursos", "👨‍🏫 Análisis de Docentes"])
    
    with tab1:
        st.title("📊 Reporte de Cursos CBAME")
        
        # Sidebar filters
        st.sidebar.title("Filtros")
        
        # Sector Productivo filter
        sectores = ['Todos'] + sorted(df_cursos['N_SECTOR_PRODUCTIVO'].unique().tolist())
        sector_selected = st.sidebar.selectbox("Sector Productivo", sectores)
        
        # Localidad filter
        localidades = ['Todas'] + sorted(df_cursos['N_LOCALIDAD'].unique().tolist())
        localidad_selected = st.sidebar.selectbox("Localidad", localidades)
        
        # Apply filters
        filtered_cursos = df_cursos
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



        # Mapa de cursos por localidad
        st.subheader("Mapa de Cursos por Localidad")
        try:
          with open(geojson_path) as f:
              geojson_data = f.read()
        except Exception as e:
          st.error(f"Error reading geojson file: {e}")

        
        # Asegúrate de que 'N_LOCALIDAD' coincida con 'properties.NOMBRE' en el GeoJSON
        locality_counts = filtered_cursos.groupby('N_LOCALIDAD').size().reset_index(name='count')
        
        fig_map = px.choropleth_mapbox(
            locality_counts,
            geojson=geojson_data,
            locations='N_LOCALIDAD',
            color='count',
            featureidkey="properties.NOMBRE",  # Change this if necessary!
            mapbox_style="carto-positron",
            zoom=6,
            center={"lat": -31.4201, "lon": -64.1888},  # Centrar en Córdoba
            opacity=0.5,
            title='Mapa de Cursos por Localidad'
        )
        st.plotly_chart(fig_map, use_container_width=True)


        
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

 # Download buttons for dataframes
        st.sidebar.subheader("Descargar Datos Cursos")
        csv_cursos = df_cursos.to_csv(index=False).encode('utf-8')
        st.sidebar.download_button(
            label="Descargar Cursos",
            data=csv_cursos,
            file_name='cursos.csv',
            mime='text/csv'
        )
        
        csv_docentes = df_docentes.to_csv(index=False).encode('utf-8')
        st.sidebar.download_button(
            label="Descargar Docentes",
            data=csv_docentes,
            file_name='docentes.csv',
            mime='text/csv'
        )


    
    with tab2:
        st.title("👨‍🏫 Análisis de Docentes")
        
        # Filter out rows without 'ID_DOCENTE'
        filtered_docentes = df_docentes.dropna(subset=['ID_DOCENTE'])
        
        # Calculate total number of unique docentes
        total_docentes = filtered_docentes['ID_DOCENTE'].nunique()
        
        # Display total number of docentes
        st.metric(label="Total de Docentes", value=total_docentes)
        
        # Group docentes by course
        docentes_por_curso = filtered_docentes.groupby('N_CURSO')['NRO_DOCUMENTO'].nunique().reset_index()
        
        # Layout with two columns
        col1, col2 = st.columns(2)
        
        with col1:
            # Display docentes by course as a pie chart
            st.subheader("Docentes por Curso")
            fig_docentes_curso = px.pie(
                docentes_por_curso,
                names='N_CURSO',
                values='NRO_DOCUMENTO',
                title='Distribución de Docentes por Curso'
            )
            st.plotly_chart(fig_docentes_curso, use_container_width=True)
        
        with col2:
            # Detailed information
            st.subheader("Detalle de Docentes")
            
            # Display docentes details in a table
            st.dataframe(
                filtered_docentes[[ 
                    'NRO_DOCUMENTO', 'ID_DOCENTE', 'N_CURSO', 'HS_ASIGNADAS'
                ]]
            )

else:
    st.error("No se pudieron cargar los datos. Por favor, verifica la conexión y los archivos.")