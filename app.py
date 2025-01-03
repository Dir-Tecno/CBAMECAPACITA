import streamlit as st
import pandas as pd
import io
import traceback
import logging
import sys
import os
from streamlit import runtime
import gc

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

# Verificar variables de entorno
def verificar_configuracion():
    try:
        url = st.secrets["supabase"]["url"]
        key = st.secrets["supabase"]["key"]
        logger.info("Configuración de Supabase cargada correctamente")
        return url, key
    except Exception as e:
        logger.error(f"Error al cargar configuración: {e}")
        st.error("Error al cargar la configuración. Por favor, verifica las variables de entorno.")
        return None, None

# Inicializar Supabase
def inicializar_supabase(url, key):
    try:
        from supabase import create_client
        client = create_client(url, key)
        logger.info("Cliente Supabase inicializado correctamente")
        return client
    except Exception as e:
        logger.error(f"Error al inicializar Supabase: {e}")
        st.error("Error al conectar con la base de datos.")
        return None

@st.cache_data(ttl=3600)  # Cache por 1 hora
def cargar_datos_supabase(_supabase_client) -> pd.DataFrame:
    try:
        # Descargamos el archivo
        respuesta = _supabase_client.storage.from_('CBAMECAPACITA').download('ALUMNOS_X_LOCALIDAD.parquet')
        
        # Guardamos temporalmente el contenido en un BytesIO
        buffer = io.BytesIO(respuesta)
        buffer.seek(0)
        
        try:
            # Leer el Parquet con optimizaciones
            df = pd.read_parquet(
                buffer,
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
            buffer.close()
            del respuesta
            gc.collect()

        st.write(f"✅ Datos cargados: {len(df)} registros")
        logging.info(f"Datos cargados exitosamente: {len(df)} registros")
        
        return df
        
    except Exception as e:
        st.error("❌ Error al cargar los datos")
        logging.error(f"Error al cargar datos: {traceback.format_exc()}")
        with st.expander("Detalles del error"):
            st.error(traceback.format_exc())
        return None

def crear_filtros_predictivos(df: pd.DataFrame):
    filtros = {}
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.subheader("📚 Cursos")
        curso = st.text_input("Escribe el nombre del curso")
        filtros['N_CURSO'] = (
            df[df['N_CURSO'].str.contains(curso, case=False, na=False)]['N_CURSO'].unique()
            if curso else df['N_CURSO'].unique()
        )

    with col2:
        st.subheader("🏢 Sectores")
        sector = st.text_input("Escribe el nombre del sector")
        filtros['N_SECTOR'] = (
            df[df['N_SECTOR'].str.contains(sector, case=False, na=False)]['N_SECTOR'].unique()
            if sector else df['N_SECTOR'].unique()
        )

    with col3:
        st.subheader("🏫 Instituciones")
        institucion = st.text_input("Escribe el nombre de la institución")
        filtros['N_INSTITUCION'] = (
            df[df['N_INSTITUCION'].str.contains(institucion, case=False, na=False)]['N_INSTITUCION'].unique()
            if institucion else df['N_INSTITUCION'].unique()
        )

    with col4:
        st.subheader("🔑 CUIL")
        cuil = st.text_input("Escribe el CUIL")
        filtros['CUIL'] = (
            df[df['CUIL'].astype(str).str.contains(cuil, case=False, na=False)]['CUIL'].unique()
            if cuil else df['CUIL'].unique()
        )

    return filtros

def aplicar_filtros(df: pd.DataFrame, filtros: dict) -> pd.DataFrame:
    df_filtrado = df.copy()
    for col, vals in filtros.items():
        df_filtrado = df_filtrado[df_filtrado[col].isin(vals)]
    return df_filtrado

@st.cache_data
def get_page_data(df: pd.DataFrame, inicio: int, fin: int) -> pd.DataFrame:
    return df.iloc[inicio:fin].copy()

def mostrar_tabla_paginada(df: pd.DataFrame):
    st.subheader("📜 Datos Filtrados")
    
    # Fila superior con controles en una línea
    col1, col2, col3, col4 = st.columns([1, 2, 1, 1])
    with col1:
        n_filas = st.selectbox(
            "Filas por página",
            options=[10, 20, 30, 40, 50],
            index=1,  # 20 filas por defecto
        )
    
    # Calcular paginación
    total_filas = len(df)
    n_paginas = (total_filas // n_filas) + (1 if total_filas % n_filas > 0 else 0)
    
    with col3:
        pagina = st.number_input(
            "Página",
            min_value=1,
            max_value=n_paginas,
            value=1,
            help=f"Total de páginas disponibles: {n_paginas}"
        )
    
    with col4:
        st.caption(f"Total: {total_filas} registros")
    
    # Calcular registros a mostrar
    inicio = (pagina - 1) * n_filas
    fin = min(inicio + n_filas, total_filas)
    
    # Mostrar la tabla
    datos_pagina = get_page_data(df, inicio, fin)
    st.dataframe(datos_pagina, use_container_width=True)
    
    # Información de paginación al pie de la tabla
    st.caption(f"Mostrando registros {inicio+1} a {fin} de {total_filas} | Página {pagina} de {n_paginas}")

def descargar_datos(df: pd.DataFrame):
    # Solo mantener la descarga CSV
    csv_buffer = io.StringIO()
    chunk_size = 10000  # Procesar en chunks de 10000 filas
    
    for i in range(0, len(df), chunk_size):
        chunk = df.iloc[i:i+chunk_size]
        chunk.to_csv(csv_buffer, index=False, encoding='utf-8', 
                    header=(i==0), mode='a')
    
    csv_buffer.seek(0)
    st.download_button(
        "📝 Descargar datos (CSV)", 
        data=csv_buffer.getvalue(), 
        file_name='datos_filtrados.csv', 
        mime='text/csv'
    )

def main():
    try:
        st.title('🎓 CBA ME CAPACITA - Dashboard de Alumnos')
        st.markdown("---")

        # Verificar configuración
        url, key = verificar_configuracion()
        if not url or not key:
            st.stop()

        # Inicializar Supabase
        supabase = inicializar_supabase(url, key)
        if not supabase:
            st.stop()

        # Cargar datos
        df = cargar_datos_supabase(supabase)
        
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

    except Exception as e:
        logger.error(f"Error general en la aplicación: {traceback.format_exc()}")
        st.error("Ha ocurrido un error inesperado. Por favor, intenta más tarde.")
        st.stop()

if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        logger.error(f"Error crítico: {traceback.format_exc()}")