import streamlit as st
import pandas as pd
import io
import traceback
import logging
import sys
import os
from streamlit import runtime
import gc
from huggingface_hub import hf_hub_download

# Configurar logging para mostrar en la consola
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('app_log.txt')
    ]
)

logger = logging.getLogger(__name__)

# Configuración de página
try:
    st.set_page_config(
        page_title="CBA ME CAPACITA",
        page_icon="🎓",
        layout="wide",
        initial_sidebar_state="expanded"
    )
except Exception as e:
    logger.error(f"Error en configuración de página: {e}")

# Aplicar estilos personalizados para mejorar la apariencia
st.markdown("""
<style>
    /* Estilos generales */
    .main {
        background-color: #f8f9fa;
        padding: 2rem;
    }
    
    /* Títulos y encabezados */
    h1 {
        color: #0066cc;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        font-weight: 700;
        padding-bottom: 1rem;
        border-bottom: 2px solid #0066cc;
        margin-bottom: 2rem;
    }
    
    h2, h3, .subheader {
        color: #0066cc;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        margin-top: 1.5rem;
        margin-bottom: 1rem;
    }
    
    /* Contenedores y tarjetas */
    .stDataFrame {
        border-radius: 10px;
        border: 1px solid #dee2e6;
        overflow: hidden;
        margin-bottom: 2rem;
    }
    
    /* Botones */
    .stButton > button {
        background-color: #0066cc;
        color: white;
        border-radius: 5px;
        border: none;
        padding: 0.5rem 1rem;
        font-weight: 500;
        transition: all 0.3s;
    }
    
    .stButton > button:hover {
        background-color: #004c99;
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
    }
    
    /* Inputs y selectores */
    .stTextInput > div > div > input,
    .stSelectbox > div > div > select {
        border-radius: 5px;
        border: 1px solid #ced4da;
        padding: 0.5rem;
    }
    
    /* Sidebar */
    .sidebar .sidebar-content {
        background-color: #f0f2f5;
        padding: 1rem;
    }
    
    /* Paginación */
    .pagination-info {
        text-align: center;
        font-weight: 500;
        margin: 1rem 0;
        color: #495057;
    }
    
    /* Contenedores de filtros */
    .filter-container {
        background-color: white;
        padding: 1.5rem;
        border-radius: 10px;
        box-shadow: 0 2px 5px rgba(0, 0, 0, 0.05);
        margin-bottom: 2rem;
    }
    
    /* Mensajes */
    .success-message {
        color: #28a745;
        font-weight: 500;
    }
    
    .error-message {
        color: #dc3545;
        font-weight: 500;
    }
    
    /* Separadores */
    hr {
        margin: 2rem 0;
        border: 0;
        height: 1px;
        background-image: linear-gradient(to right, rgba(0, 0, 0, 0), rgba(0, 102, 204, 0.5), rgba(0, 0, 0, 0));
    }
</style>
""", unsafe_allow_html=True)

# Verificar variables de entorno para Hugging Face
def verificar_configuracion():
    try:
        hf_token = st.secrets["HuggingFace"]["huggingface_token"]
        logger.info("Configuración de Hugging Face cargada correctamente")
        return hf_token
    except Exception as e:
        logger.error(f"Error al cargar configuración: {e}")
        st.error("Error al cargar la configuración. Por favor, verifica las variables de entorno.")
        return None

@st.cache_data(ttl=3600)  # Cache por 1 hora
def cargar_datos_huggingface(hf_token) -> pd.DataFrame:
    try:
        # Configuración para Hugging Face
        REPO_ID = "Dir-Tecno/CBAMECAPACITA"
        
        # Mostrar mensaje de carga
        with st.spinner("Cargando datos desde Hugging Face..."):
            # Descargamos el archivo desde Hugging Face
            logger.info(f"Descargando archivo desde Hugging Face: {REPO_ID}")
            file_path = hf_hub_download(
                REPO_ID, 
                filename="ALUMNOS_X_LOCALIDAD.parquet", 
                token=hf_token, 
                repo_type='dataset'
            )
            
            try:
                # Leer el Parquet con optimizaciones
                df = pd.read_parquet(
                    file_path,
                    engine='pyarrow',
                    columns=[
                        'N_CURSO',
                        'N_SECTOR',
                        'N_INSTITUCION',
                        'CUIL',
                        'NOMBRE_ALUMNO',
                        'NRO_DOCUMENTO',
                        'FEC_NACIMIENTO',
                        'N_TIPO_SEXO',
                        'N_LOCALIDAD',
                        'BARRIO',
                        'ASISTENCIA',
                        'FEC_INICIO',
                        'FEC_FIN',
                        'N_TIPO',
                        'NRO_EXPEDIENTE',
                        'NRO_RESOLUCION',
                        'CANTIDAD_HS',
                        'EMAIL',
                        'NRO_TELEFONO'
                    ]
                )
                
                # Renombrar algunas columnas para mejor legibilidad
                df = df.rename(columns={
                    'NOMBRE_ALUMNO': 'NOMBRE',
                    'NRO_DOCUMENTO': 'DNI',
                    'FEC_NACIMIENTO': 'FECHA_NAC',
                    'N_TIPO_SEXO': 'SEXO',
                    'FEC_INICIO': 'INICIO',
                    'FEC_FIN': 'FIN'
                })
                
                # Filtrar registros con FEC_INICIO a partir del 1 de enero de 2018
                df['INICIO'] = pd.to_datetime(df['INICIO'], format='%d/%m/%Y', errors='coerce')
                fecha_filtro = pd.Timestamp('2018-01-01')
                df = df[df['INICIO'] >= fecha_filtro]

                # Formatear la columna 'INICIO' para mostrar en formato dd/mm/yyyy
                df['INICIO'] = df['INICIO'].dt.strftime('%d/%m/%Y')

            except Exception as e:
                st.error(f"Error al leer el archivo Parquet: {str(e)}")
                logging.error(f"Error detallado al leer Parquet: {traceback.format_exc()}")
                return None
            finally:
                # Limpieza de memoria
                gc.collect()

        # Mostrar mensaje de éxito con estilo personalizado
        st.markdown(f"<div class='success-message'>✅ Datos cargados: {len(df)} registros</div>", unsafe_allow_html=True)
        logging.info(f"Datos cargados exitosamente: {len(df)} registros")
        
        return df
        
    except Exception as e:
        st.markdown("<div class='error-message'>❌ Error al cargar los datos</div>", unsafe_allow_html=True)
        logging.error(f"Error al cargar datos: {traceback.format_exc()}")
        with st.expander("Detalles del error"):
            st.error(traceback.format_exc())
        return None

def crear_filtros_predictivos(df: pd.DataFrame):
    st.markdown("<div class='filter-container'>", unsafe_allow_html=True)
    st.subheader("🔍 Filtros de búsqueda")
    
    filtros = {}
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.markdown("<h3 class='subheader'>📚 Cursos</h3>", unsafe_allow_html=True)
        curso = st.text_input("Escribe el nombre del curso", placeholder="Ej: Programación")
        filtros['N_CURSO'] = (
            df[df['N_CURSO'].str.contains(curso, case=False, na=False)]['N_CURSO'].unique()
            if curso else df['N_CURSO'].unique()
        )

    with col2:
        st.markdown("<h3 class='subheader'>🏢 Sectores</h3>", unsafe_allow_html=True)
        sector = st.text_input("Escribe el nombre del sector", placeholder="Ej: Tecnología")
        filtros['N_SECTOR'] = (
            df[df['N_SECTOR'].str.contains(sector, case=False, na=False)]['N_SECTOR'].unique()
            if sector else df['N_SECTOR'].unique()
        )

    with col3:
        st.markdown("<h3 class='subheader'>🏫 Instituciones</h3>", unsafe_allow_html=True)
        institucion = st.text_input("Escribe el nombre de la institución", placeholder="Ej: Universidad")
        filtros['N_INSTITUCION'] = (
            df[df['N_INSTITUCION'].str.contains(institucion, case=False, na=False)]['N_INSTITUCION'].unique()
            if institucion else df['N_INSTITUCION'].unique()
        )

    with col4:
        st.markdown("<h3 class='subheader'>🔑 CUIL</h3>", unsafe_allow_html=True)
        cuil = st.text_input("Escribe el CUIL", placeholder="Ej: 20123456789")
        filtros['CUIL'] = (
            df[df['CUIL'].astype(str).str.contains(cuil, case=False, na=False)]['CUIL'].unique()
            if cuil else df['CUIL'].unique()
        )
    
    st.markdown("</div>", unsafe_allow_html=True)
    return filtros

def aplicar_filtros(df: pd.DataFrame, filtros: dict) -> pd.DataFrame:
    df_filtrado = df.copy()
    for col, vals in filtros.items():
        df_filtrado = df_filtrado[df_filtrado[col].isin(vals)]
    return df_filtrado

@st.cache_data
def get_page_data(df: pd.DataFrame, inicio: int, fin: int) -> pd.DataFrame:
    return df.iloc[inicio:fin]

def mostrar_tabla_paginada(df: pd.DataFrame, filas_por_pagina: int = 10):
    st.markdown("<div class='filter-container'>", unsafe_allow_html=True)
    
    # Mostrar número total de registros
    total_registros = len(df)
    st.markdown(f"<div class='pagination-info'>Total de registros: <b>{total_registros}</b></div>", unsafe_allow_html=True)
    
    # Si no hay registros, mostrar mensaje y salir
    if total_registros == 0:
        st.warning("No hay registros que coincidan con los filtros seleccionados.")
        st.markdown("</div>", unsafe_allow_html=True)
        return
    
    # Calcular número total de páginas
    total_paginas = (total_registros + filas_por_pagina - 1) // filas_por_pagina
    
    # Crear una interfaz de paginación más profesional
    col1, col2, col3 = st.columns([1, 3, 1])
    
    with col1:
        # Selector de registros por página
        filas_opciones = [10, 25, 50, 100]
        filas_por_pagina = st.selectbox("Registros por página:", filas_opciones, index=filas_opciones.index(filas_por_pagina) if filas_por_pagina in filas_opciones else 0)
        
    with col2:
        # Mostrar la tabla con los datos de la página actual
        if 'pagina_actual' not in st.session_state:
            st.session_state.pagina_actual = 1
        
        # Recalcular total de páginas si cambia filas_por_pagina
        total_paginas = (total_registros + filas_por_pagina - 1) // filas_por_pagina
        
        # Asegurar que la página actual es válida
        if st.session_state.pagina_actual > total_paginas:
            st.session_state.pagina_actual = total_paginas
        
        # Calcular índices de inicio y fin para la página actual
        inicio = (st.session_state.pagina_actual - 1) * filas_por_pagina
        fin = min(inicio + filas_por_pagina, total_registros)
    
    with col3:
        # Información de paginación
        st.markdown(f"<div class='pagination-info'>Página <b>{st.session_state.pagina_actual}</b> de <b>{total_paginas}</b></div>", unsafe_allow_html=True)
    
    # Obtener datos para la página actual
    datos_pagina = get_page_data(df, inicio, fin)
    
    # Mostrar la tabla con los datos de la página actual
    st.dataframe(datos_pagina, use_container_width=True)
    
    # Controles de navegación de paginación
    col1, col2, col3, col4, col5 = st.columns([1, 1, 3, 1, 1])
    
    with col1:
        # Botón para ir a la primera página
        if st.button("⏮️ Primera"):
            st.session_state.pagina_actual = 1
            st.rerun()
    
    with col2:
        # Botón para ir a la página anterior
        if st.button("◀️ Anterior") and st.session_state.pagina_actual > 1:
            st.session_state.pagina_actual -= 1
            st.rerun()
    
    with col3:
        # Selector de página (input numérico)
        nueva_pagina = st.number_input("Ir a página:", min_value=1, max_value=total_paginas, value=st.session_state.pagina_actual, step=1)
        if nueva_pagina != st.session_state.pagina_actual:
            st.session_state.pagina_actual = nueva_pagina
            st.rerun()
    
    with col4:
        # Botón para ir a la página siguiente
        if st.button("▶️ Siguiente") and st.session_state.pagina_actual < total_paginas:
            st.session_state.pagina_actual += 1
            st.rerun()
    
    with col5:
        # Botón para ir a la última página
        if st.button("⏭️ Última"):
            st.session_state.pagina_actual = total_paginas
            st.rerun()
    
    # Mostrar información detallada de paginación
    st.markdown(f"<div class='pagination-info'>Mostrando registros <b>{inicio + 1}</b> a <b>{fin}</b> de <b>{total_registros}</b></div>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

def descargar_datos(df: pd.DataFrame):
    st.markdown("<div class='filter-container'>", unsafe_allow_html=True)
    st.subheader("📥 Descargar Datos")
    
    col1, col2 = st.columns([1, 3])
    
    with col1:
        # Opciones de formato
        formato = st.selectbox("Formato de descarga:", ["CSV", "Excel", "JSON"])
    
    with col2:
        # Botón de descarga
        if st.button("📥 Descargar datos filtrados"):
            if formato == "CSV":
                csv = df.to_csv(index=False).encode('utf-8')
                st.download_button(
                    label="Descargar CSV",
                    data=csv,
                    file_name="datos_filtrados.csv",
                    mime="text/csv"
                )
            elif formato == "Excel":
                output = io.BytesIO()
                with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                    df.to_excel(writer, index=False, sheet_name='Datos')
                excel_data = output.getvalue()
                st.download_button(
                    label="Descargar Excel",
                    data=excel_data,
                    file_name="datos_filtrados.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )
            elif formato == "JSON":
                json_str = df.to_json(orient='records')
                st.download_button(
                    label="Descargar JSON",
                    data=json_str,
                    file_name="datos_filtrados.json",
                    mime="application/json"
                )
    st.markdown("</div>", unsafe_allow_html=True)

def main():
    try:
        # Título principal con estilo mejorado
        st.markdown("<h1>🎓 CBA ME CAPACITA - Dashboard de Alumnos</h1>", unsafe_allow_html=True)
        
        # Información del dashboard
        st.markdown("""
        <div style="background-color: #e9f5ff; padding: 1rem; border-radius: 10px; margin-bottom: 2rem;">
            <p style="margin: 0;">Este dashboard permite visualizar y filtrar información sobre los alumnos de los cursos de CBA ME CAPACITA. 
            Utilice los filtros para encontrar información específica y descargue los datos según sus necesidades.</p>
        </div>
        """, unsafe_allow_html=True)

        # Verificar configuración de Hugging Face
        hf_token = verificar_configuracion()
        if not hf_token:
            st.stop()

        # Cargar datos desde Hugging Face
        df = cargar_datos_huggingface(hf_token)
        
        # Verificar si se cargaron los datos correctamente
        if df is None:
            st.error("No se pudieron cargar los datos. Por favor, verifica el archivo y vuelve a intentarlo.")
            st.stop()
            return

        # Crear filtros predictivos
        filtros = crear_filtros_predictivos(df)

        # Aplicar filtros
        df_filtrado = aplicar_filtros(df, filtros)

        # Mostrar tabla paginada
        mostrar_tabla_paginada(df_filtrado)

        # Descargar datos filtrados
        descargar_datos(df_filtrado)
        
        # Pie de página
        st.markdown("""
        <hr>
        <div style="text-align: center; color: #6c757d; padding: 1rem;">
            <p>Desarrollado por la Dirección de Tecnología - Gobierno de la Provincia de Córdoba</p>
            <p>© 2023 CBA ME CAPACITA</p>
        </div>
        """, unsafe_allow_html=True)

    except Exception as e:
        logger.error(f"Error general en la aplicación: {traceback.format_exc()}")
        st.error("Ha ocurrido un error inesperado. Por favor, intenta más tarde.")
        st.stop()

if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        logger.error(f"Error crítico: {traceback.format_exc()}")