import streamlit as st
import pandas as pd
import io
import traceback
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s - %(levelname)s - %(message)s',
                    filename='app_log.txt')

from supabase import create_client, Client

# Configuración de página
st.set_page_config(page_title="CBA ME CAPACITA", page_icon="🎓", layout="wide")

# Configuración de las credenciales
try:
    url = st.secrets["supabase"]["url"]
    key = st.secrets["supabase"]["key"]
except KeyError as e:
    st.error(f"❌ Error en configuración de credenciales: {e}")
    logging.error(f"Configuración de credenciales fallida: {e}")
    st.stop()

# Intentar crear el cliente sin el parámetro proxy
try:
    supabase = create_client(url, key)
    logging.info("Cliente Supabase creado exitosamente")
except Exception as e:
    st.error(f"Error al crear el cliente: {str(e)}")
    logging.error(f"Error al crear cliente Supabase: {traceback.format_exc()}")
    st.stop()

def cargar_datos_supabase() -> pd.DataFrame:
    try:
        # Descargamos el archivo
        respuesta = supabase.storage.from_('CBAMECAPACITA').download('ALUMNOS_X_LOCALIDAD.parquet')
        
        # Guardamos temporalmente el contenido en un BytesIO
        buffer = io.BytesIO(respuesta)
        buffer.seek(0)
        
        try:
            df = pd.read_parquet(buffer)
        except Exception as e:
            st.error(f"Error al leer el archivo Parquet: {str(e)}")
            logging.error(f"Error detallado al leer Parquet: {traceback.format_exc()}")
            return None

        st.write(f"✅ Datos cargados: {len(df)} registros")
        logging.info(f"Datos cargados exitosamente: {len(df)} registros")

        # Eliminar columnas específicas
        columnas_a_eliminar = ['CONFIAMOS', 'GCAL','NOC','LUNES','MARTES','MIERCOLES','JUEVES','VIERNES','SABADO','DOMINGO','DESDE','HASTA','C_MES_DESOC', 'JUBILADO', 'DESOCUPADO', 'TRAB_INFORMAL', 'TRAB_REG', 'REL_DEPENDENCIA', 'CTA_PROPIA', 'BENEFICIARIO', 'BEN_VAT', 'BEN_ASIGNACION', 'BEN_PEC', 'BEN_SCE', 'BEN_PJ', 'D_BEN_OTRO','PRIMARIA','CICLO_BASICO','SECUNDARIA','D_SECUNDARIA','TERCIARIA','D_TERCIARIA','UNIVERSITARIA','D_UNIVERSITARIA']  
        df = df.drop(columns=columnas_a_eliminar, errors='ignore')        
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

def mostrar_tabla_paginada(df: pd.DataFrame):
    st.subheader("📜 Datos Filtrados")
    n_filas = st.slider("Filas por página", min_value=5, max_value=100, value=20)
    total_filas = len(df)
    pagina = st.number_input(
        "Número de página", min_value=1, max_value=(total_filas // n_filas) + 1, value=1
    )
    inicio = (pagina - 1) * n_filas
    fin = inicio + n_filas
    st.dataframe(df.iloc[inicio:fin], use_container_width=True)

def descargar_datos(df: pd.DataFrame):
    col1, col2 = st.columns(2)
    
    with col1:
        # Descarga en CSV
        csv = df.to_csv(index=False, encoding='utf-8')
        st.download_button(
            "📝 Descargar datos (CSV)", 
            data=csv, 
            file_name='datos_filtrados.csv', 
            mime='text/csv'
        )
    
    with col2:
        # Descarga en Excel
        excel_buffer = io.BytesIO()
        with pd.ExcelWriter(excel_buffer, engine='xlsxwriter') as writer:
            df.to_excel(writer, index=False, sheet_name='Datos')
        excel_buffer.seek(0)
        st.download_button(
            "📝 Descargar datos (XLSX)", 
            data=excel_buffer, 
            file_name='datos_filtrados.xlsx', 
            mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )

def main():
    st.title('🎓 CBA ME CAPACITA - Dashboard de Alumnos')
    st.markdown("---")

    # Cargar datos
    df = cargar_datos_supabase()
    
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

if __name__ == '__main__':
    main()