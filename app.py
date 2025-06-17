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
from src.pages.comparar_cursos import main as comparar_cursos_main
from datetime import datetime, date

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
# IMPORTANTE: st.set_page_config() debe ser la primera llamada a un comando de Streamlit.
# Solo debe aparecer una vez en tu aplicación, idealmente en el script principal.
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
    :root {
        --cordoba-azul: #004A93;
        --cordoba-celeste: #2E75B5;
        --cordoba-gris: #58595B;
        --cordoba-gris-claro: #D9D9D9;
        --cordoba-rojo: #C00000;
        --cordoba-verde: #00B050;
        --cordoba-amarillo: #FFC000;
    }
    body, .main {
        background: linear-gradient(135deg, #f8f9fa 0%, #e7f3fe 100%);
        min-height: 100vh;
    }
    h1, h2, h3, .subheader {
        color: var(--cordoba-azul);
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        font-weight: 700;
        letter-spacing: 0.5px;
    }
    .stButton > button {
        background: linear-gradient(90deg, var(--cordoba-azul) 60%, var(--cordoba-celeste) 100%);
        color: white;
        border: none;
        border-radius: 6px;
        padding: 0.6rem 1.2rem;
        font-weight: 600;
        box-shadow: 0 2px 8px rgba(46,117,181,0.08);
        transition: background 0.3s, box-shadow 0.3s;
    }
    .stButton > button:hover {
        background: linear-gradient(90deg, var(--cordoba-celeste) 60%, var(--cordoba-azul) 100%);
        box-shadow: 0 4px 16px rgba(0,74,147,0.12);
    }
    .card {
        background: #fff;
        border-radius: 12px;
        padding: 1.5rem 1.2rem;
        margin-bottom: 1.5rem;
        border: 1px solid var(--cordoba-gris-claro);
        box-shadow: 0 2px 16px rgba(0,74,147,0.06);
        transition: box-shadow 0.2s;
    }
    .card:hover {
        box-shadow: 0 6px 24px rgba(0,74,147,0.12);
    }
    .stDataFrame {
        border-radius: 10px;
        border: 1px solid #dee2e6;
        overflow: hidden;
        margin-bottom: 2rem;
        box-shadow: 0 1px 8px rgba(0,74,147,0.07);
    }
    .stTextInput > div > div > input,
    .stSelectbox > div > div > select {
        border-radius: 6px;
        border: 1px solid #ced4da;
        padding: 0.5rem;
        font-size: 1rem;
        transition: border-color 0.2s, box-shadow 0.2s;
    }
    .stTextInput > div > div > input:focus {
        border-color: var(--cordoba-azul);
        box-shadow: 0 0 0 0.2rem rgba(0, 74, 147, 0.15);
    }
    .sidebar .sidebar-content {
        background-color: #f0f2f5;
        padding: 1rem;
    }
    .pagination-info {
        text-align: center;
        font-weight: 500;
        margin: 1rem 0;
        color: #495057;
    }
    .filter-container {
        background-color: white;
        padding: 1.5rem;
        border-radius: 10px;
        box-shadow: 0 2px 5px rgba(0, 0, 0, 0.05);
        margin-bottom: 2rem;
    }
    .success-message {
        color: #28a745;
        font-weight: 500;
    }
    .error-message {
        color: #dc3545;
        font-weight: 500;
    }
    hr {
        margin: 2rem 0;
        border: 0;
        height: 1px;
        background-image: linear-gradient(to right, rgba(0, 0, 0, 0), rgba(0, 102, 204, 0.5), rgba(0, 0, 0, 0));
    }
    .footer {
        text-align: center;
        padding: 1.2rem;
        margin-top: 2.5rem;
        border-top: 1px solid var(--cordoba-gris-claro);
        color: var(--cordoba-gris);
        font-size: 0.9rem;
        background: #f8f9fa;
        border-radius: 0 0 12px 12px;
    }
    .stDownloadButton>button {
        background: linear-gradient(90deg, var(--cordoba-celeste) 60%, var(--cordoba-azul) 100%);
        color: white;
        border-radius: 6px;
        font-weight: 600;
        transition: background 0.3s;
    }
    .stDownloadButton>button:hover {
        background: linear-gradient(90deg, var(--cordoba-azul) 60%, var(--cordoba-celeste) 100%);
    }
    ::-webkit-scrollbar {
        width: 10px;
        background: #e7f3fe;
    }
    ::-webkit-scrollbar-thumb {
        background: var(--cordoba-celeste);
        border-radius: 6px;
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
        with st.spinner("Cargando datos..."):
            # Descargamos el archivo desde Hugging Face
            logger.info(f"Descargando: {REPO_ID}")
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
            
            except Exception as e:
                st.error(f"Error al leer el archivo Parquet: {str(e)}")
                logging.error(f"Error detallado al leer Parquet: {traceback.format_exc()}")
                return None
            finally:
                # Limpieza de memoria
                gc.collect()
        
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
    col1, col2, col3, col4, col5 = st.columns(5)
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
        # Asegúrate de manejar la conversión a string antes de la búsqueda para CUIL
        filtros['CUIL'] = (
            df[df['CUIL'].astype(str).str.contains(cuil, case=False, na=False)]['CUIL'].unique()
            if cuil else df['CUIL'].unique()
        )

    with col5: # Nueva columna para el filtro de año
        st.markdown("<h3 class='subheader'>🗓️ Año de Fin</h3>", unsafe_allow_html=True)
        
        # Asegúrate de que 'FIN' sea de tipo datetime y extrae los años
        df['FIN'] = pd.to_datetime(df['FIN'], errors='coerce')
        # Filtra los NaT antes de obtener los años únicos
        available_years = sorted(df['FIN'].dropna().dt.year.unique(), reverse=True)
        
        if not available_years:
            st.warning("No hay años disponibles para filtrar.")
            selected_year = None
        else:
            # Opción para no filtrar por año
            years_options = ['Todos'] + available_years
            selected_year_str = st.selectbox(
                "Selecciona un año:",
                options=years_options,
                index=0 # Por defecto "Todos"
            )
            selected_year = int(selected_year_str) if selected_year_str != 'Todos' else None
        
        # ALMACENAR EL AÑO SELECCIONADO DIRECTAMENTE
        filtros['anio_fin'] = selected_year 

    st.markdown("</div>", unsafe_allow_html=True)
    return filtros

def aplicar_filtros(df: pd.DataFrame, filtros: dict) -> pd.DataFrame:
    df_filtrado = df.copy()

    # --- Aplicar el filtro de año de fin primero y de forma explícita ---
    # Asegurarse de que la columna 'FIN' sea datetime para poder extraer el año
    df_filtrado['FIN'] = pd.to_datetime(df_filtrado['FIN'], errors='coerce')

    if 'anio_fin' in filtros and filtros['anio_fin'] is not None:
        selected_year = filtros['anio_fin']
        # Filtra por el año de la columna 'FIN', ignorando NaT
        df_filtrado = df_filtrado[df_filtrado['FIN'].dt.year == selected_year]
    
    # --- Aplicar los demás filtros (texto, CUIL) ---
    for col, vals in filtros.items():
        # Ignorar 'anio_fin' ya que lo manejamos arriba y no es una columna de df
        if col == 'anio_fin':
            continue 

        # Asegurarse de que vals no sea None o vacío
        if vals is not None and len(vals) > 0:
            if col == 'CUIL':
                # Convertir a string para la comparación si CUIL puede ser numérico en df
                df_filtrado = df_filtrado[df_filtrado[col].astype(str).isin(vals.astype(str))]
            else:
                # Asegurarse de que la columna exista en el DataFrame antes de filtrar
                if col in df_filtrado.columns:
                    df_filtrado = df_filtrado[df_filtrado[col].isin(vals)]
                else:
                    logger.warning(f"La columna '{col}' no se encuentra en el DataFrame filtrado. Ignorando este filtro.")
        else:
            # Si el filtro predictivo para una columna de texto no encontró coincidencias,
            # el resultado debe ser un DataFrame vacío para esa columna.
            if col in df_filtrado.columns and not df[col].empty:
                 df_filtrado = df_filtrado[df_filtrado[col].isin([])]

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
        # Asegurarse de que el valor inicial sea válido si filas_por_pagina no está en las opciones
        current_filas_idx = filas_opciones.index(filas_por_pagina) if filas_por_pagina in filas_opciones else 0
        filas_por_pagina = st.selectbox("Registros por página:", filas_opciones, index=current_filas_idx)
        
    with col2:
        # Mostrar la tabla con los datos de la página actual
        if 'pagina_actual' not in st.session_state:
            st.session_state.pagina_actual = 1
        
        # Recalcular total de páginas si cambia filas_por_pagina
        total_paginas = (total_registros + filas_por_pagina - 1) // filas_por_pagina
        
        # Asegurar que la página actual es válida
        if st.session_state.pagina_actual > total_paginas:
            st.session_state.pagina_actual = total_paginas
        # Si no hay páginas, la página actual debería ser 1 (si hay registros)
        if total_paginas == 0 and total_registros > 0:
            st.session_state.pagina_actual = 1
        
        # Calcular índices de inicio y fin para la página actual
        inicio = (st.session_state.pagina_actual - 1) * filas_por_pagina
        fin = min(inicio + filas_por_pagina, total_registros)
    
    with col3:
        # Información de paginación
        st.markdown(f"<div class='pagination-info'>Página <b>{st.session_state.pagina_actual}</b> de <b>{total_paginas if total_paginas > 0 else 1}</b></div>", unsafe_allow_html=True)
    
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
        # Asegurarse de que el valor inicial sea el actual y los límites sean correctos
        nueva_pagina = st.number_input("Ir a página:", min_value=1, max_value=total_paginas if total_paginas > 0 else 1, value=st.session_state.pagina_actual, step=1)
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
        # Botón de descarga. El botón debe ser un st.download_button directamente si se genera el archivo.
        if formato == "CSV":
            csv = df.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="Descargar CSV",
                data=csv,
                file_name="datos_filtrados.csv",
                mime="text/csv",
                key="download_csv_button" # Añadir una key única
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
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                key="download_excel_button" # Añadir una key única
            )
        elif formato == "JSON":
            json_str = df.to_json(orient='records')
            st.download_button(
                label="Descargar JSON",
                data=json_str,
                file_name="datos_filtrados.json",
                mime="application/json",
                key="download_json_button" # Añadir una key única
            )
    st.markdown("</div>", unsafe_allow_html=True)

def main():
    try:
        # Título principal con estilo mejorado
        st.markdown("<h1>🎓 CBA ME CAPACITA - Dashboard de Alumnos</h1>", unsafe_allow_html=True)
        
        # Crear pestañas para la navegación
        tab1, tab2 = st.tabs(["📊 Dashboard Principal", "🔄 Comparación de Cursos"])
        
        with tab1:
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

        with tab2:
            # Asegúrate de que comparar_cursos_main no llame a st.set_page_config()
            comparar_cursos_main()
        
        
        # Pie de página
        st.markdown("""
        <hr>
        <div style="text-align: center; color: #6c757d; padding: 1rem;">
            <p>Desarrollado por la Dirección de Tecnología - Gobierno de la Provincia de Córdoba</p>
            <p>© 2025 CBA ME CAPACITA</p>
        </div>
        """, unsafe_allow_html=True)

    except Exception as e:
        logger.error(f"Error general en la aplicación: {traceback.format_exc()}")
        st.error("Ha ocurrido un error inesperado. Por favor, intenta más tarde.")
        # Aquí NO se usa st.stop() para no detener la app por cualquier error.

if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        logger.error(f"Error crítico: {traceback.format_exc()}")