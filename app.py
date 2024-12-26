import streamlit as st
import pandas as pd
import io
import traceback
from supabase import create_client, Client

# Configuración de página
st.set_page_config(page_title="CBA ME CAPACITA", page_icon="🎓", layout="wide")

# Configuración de Supabase desde Streamlit secrets
url = st.secrets["supabase"]["url"]
key = st.secrets["supabase"]["key"]

supabase = create_client(url, key)

# Inicialización segura del cliente Supabase
def inicializar_supabase() -> Client:
    try:
        supabase: Client = create_client(supabase_url=url, supabase_key=key)
        return supabase
    except Exception as e:
        st.error("❌ Error al conectar con Supabase")
        with st.expander("Detalles del error"):
            st.error(traceback.format_exc())
        st.stop()

# Inicializar Supabase
supabase = inicializar_supabase()

def cargar_datos_supabase() -> pd.DataFrame:
    try:
        respuesta = supabase.storage.from_('CBAMECAPACITA').download('ALUMNOS_X_LOCALIDAD.parquet')
        df = pd.read_parquet(io.BytesIO(respuesta))
        st.write(f"✅ Datos cargados: {len(df)} registros")
        return df
    except Exception as e:
        st.error("❌ Error al cargar los datos")
        with st.expander("Detalles del error"):
            st.error(traceback.format_exc())
        st.stop()

def crear_filtros_predictivos(df: pd.DataFrame):
    filtros = {}
    col1, col2, col3 = st.columns(3)

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

    return filtros

def aplicar_filtros(df: pd.DataFrame, filtros: dict) -> pd.DataFrame:
    df_filtrado = df.copy()
    for col, vals in filtros.items():
        df_filtrado = df_filtrado[df_filtrado[col].isin(vals)]
    return df_filtrado

def mostrar_tabla_paginada(df: pd.DataFrame):
    st.subheader("📋 Datos Filtrados")
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
            "📥 Descargar datos (CSV)", 
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
            "📥 Descargar datos (XLSX)", 
            data=excel_buffer, 
            file_name='datos_filtrados.xlsx', 
            mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )

def main():
    st.title('🎓 CBA ME CAPACITA - Dashboard de Alumnos')
    st.markdown("---")

    # Cargar datos
    df = cargar_datos_supabase()

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
