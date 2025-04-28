import streamlit as st
import pandas as pd
from sqlalchemy import create_engine, text
import logging
import traceback
import sys

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('comparacion_log.txt')
    ]
)

logger = logging.getLogger(__name__)

def get_database_connection():
    try:
        # Configuración para MariaDB
        connection_string = "mysql+pymysql://usuario1:usuario1@5.161.118.67:3306/CBAMECAPACITA"
        engine = create_engine(connection_string)
        return engine
    except Exception as e:
        st.error(f"Error al conectar con la base de datos: {str(e)}")
        return None

def load_data():
    try:
        engine = get_database_connection()
        if engine is None:
            return None, None

        # Cargar las dos vistas con los nombres correctos de las tablas
        query_historico = """
            SELECT DISTINCT N_CURSO, N_SECTOR, N_INSTITUCI
            FROM T_CURSOS_HISTORICO 
            ORDER BY N_CURSO
        """
        query_certificaciones = "SELECT * FROM T_CERTIF_X_LOCALIDAD"
        
        df_historico = pd.read_sql(query_historico, engine)
        df_certificaciones = pd.read_sql(query_certificaciones, engine)
        
        return df_historico, df_certificaciones
    except Exception as e:
        logger.error(f"Error al cargar datos: {traceback.format_exc()}")
        st.error(f"Error al cargar los datos: {str(e)}")
        return None, None

def mostrar_tabla_comparativa(df_historico, df_certificaciones):
    # Crear dos columnas para las tablas
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Histórico de Cursos")
        # Agregar campo de búsqueda para cursos históricos
        busqueda_curso = st.text_input("Buscar curso histórico", key="busqueda_curso")
        
        # Filtrar cursos históricos según la búsqueda
        if busqueda_curso:
            df_historico_filtrado = df_historico[df_historico['N_CURSO'].str.contains(busqueda_curso, case=False, na=False)]
        else:
            df_historico_filtrado = df_historico
            
        if not df_historico_filtrado.empty:
            st.dataframe(df_historico_filtrado, use_container_width=True,  hide_index=True)
        else:
            st.warning("No hay datos históricos disponibles")

    with col2:
        st.subheader("Certificaciones Actuales")
        # Agregar campo de búsqueda para certificaciones
        busqueda_cert = st.text_input("Buscar certificación", key="busqueda_cert")
        
        # Filtrar certificaciones según la búsqueda
        if busqueda_cert:
            df_certificaciones_filtrado = df_certificaciones[
                df_certificaciones['N_CERTIFICACION'].str.contains(busqueda_cert, case=False, na=False) |
                df_certificaciones['nombre_certificacion'].str.contains(busqueda_cert, case=False, na=False)
            ]
        else:
            df_certificaciones_filtrado = df_certificaciones
            
        if not df_certificaciones_filtrado.empty:
            st.dataframe(df_certificaciones_filtrado, use_container_width=True, hide_index=True)
        else:
            st.warning("No hay certificaciones disponibles")

def analizar_compatibilidad(df_historico, df_certificaciones):
    st.subheader("Análisis de Compatibilidad")
    
    try:
        if df_historico is not None and df_certificaciones is not None:
            # Mostrar estadísticas básicas
            col1, col2 = st.columns(2)
            
            with col1:
                st.metric("Total Cursos Históricos", len(df_historico))
            
            with col2:
                st.metric("Total Certificaciones", len(df_certificaciones))
            
            # Agregar selector para marcar equivalencias
            st.subheader("Marcar Equivalencias")
            
            # Crear dos columnas para la selección
            col1, col2 = st.columns(2)
            
            with col1:
                # Selector de curso histórico con búsqueda
                curso_historico = st.selectbox(
                    "Seleccionar Curso Histórico",
                    df_historico['N_CURSO'].unique(),
                    format_func=lambda x: f"Curso: {x}"
                )
                
                if curso_historico:
                    curso_info = df_historico[df_historico['N_CURSO'] == curso_historico].iloc[0]
                    st.info(f"""
                    **Detalles del Curso Histórico:**
                    - Curso: {curso_info['N_CURSO']}
                    - Sector: {curso_info.get('N_SECTOR', 'No disponible')}
                    """)
            
            with col2:
                # Selector de certificación con búsqueda
                certificacion = st.selectbox(
                    "Seleccionar Certificación",
                    df_certificaciones['N_CERTIFICACION'].unique(),
                    format_func=lambda x: f"Certificación: {x}"
                )
                
                if certificacion:
                    cert_info = df_certificaciones[df_certificaciones['N_CERTIFICACION'] == certificacion].iloc[0]
                    st.info(f"""
                    **Detalles de la Certificación:**
                    - Certificación: {cert_info['N_CERTIFICACION']}
                    - Nombre: {cert_info.get('nombre_certificacion', 'No disponible')}
                    """)
            
             # Botón para guardar la equivalencia
            if st.button("Guardar Equivalencia"):
                try:
                    engine = get_database_connection()
                    if engine is not None:
                        # Insertar la equivalencia
                        with engine.connect() as conn:
                            # Corregir la forma de ejecutar la consulta
                            sql = text("""
                                INSERT INTO T_EQUIVALENCIAS_CURSOS (n_curso, n_certificacion)
                                VALUES (:curso, :cert)
                            """)
                            conn.execute(sql, {"curso": curso_historico, "cert": certificacion})
                            conn.commit()
                            
                        st.success("¡Equivalencia guardada exitosamente!")
                except Exception as e:
                    st.error(f"Error al guardar la equivalencia: {str(e)}")
                    logger.error(f"Error al guardar equivalencia: {traceback.format_exc()}")
            
            # Mostrar equivalencias existentes
            try:
                engine = get_database_connection()
                if engine is not None:
                    # Fix: Remove fecha_creacion from the query since it doesn't exist
                    query = """
                        SELECT 
                            id_equivalencia,
                            n_curso,
                            n_certificacion
                        FROM T_EQUIVALENCIAS_CURSOS
                        ORDER BY id_equivalencia DESC
                    """
                    df_equivalencias = pd.read_sql(query, engine)
                    
                    st.subheader("Equivalencias Existentes")
                    if df_equivalencias.empty:
                        st.info("No hay equivalencias registradas aún.")
                    else:
                        st.dataframe(df_equivalencias, use_container_width=True,hide_index=True)
            except Exception as e:
                st.error(f"Error al cargar equivalencias existentes: {str(e)}")
                logger.error(f"Error al cargar equivalencias: {traceback.format_exc()}")
            
                
    except Exception as e:
        st.error(f"Error al analizar compatibilidad: {str(e)}")
        logger.error(f"Error en análisis de compatibilidad: {traceback.format_exc()}")

def main():
    try:
        st.title("🔄 Comparación de Cursos y Certificaciones")
        
        st.markdown("""
        <div style="background-color: #e9f5ff; padding: 1rem; border-radius: 10px; margin-bottom: 2rem;">
            <p style="margin: 0;">Esta sección permite comparar los cursos históricos con las certificaciones actuales.
            Se mostrarán las compatibilidades entre ambos conjuntos de datos para facilitar su análisis.</p>
        </div>
        """, unsafe_allow_html=True)

        # Cargar datos
        df_historico, df_certificaciones = load_data()
        
        if df_historico is None or df_certificaciones is None:
            st.error("No se pudieron cargar los datos. Por favor, verifica la conexión a la base de datos.")
            return

        # Mostrar tablas comparativas
        mostrar_tabla_comparativa(df_historico, df_certificaciones)
        
        # Mostrar análisis de compatibilidad
        analizar_compatibilidad(df_historico, df_certificaciones)

    except Exception as e:
        logger.error(f"Error en la aplicación: {traceback.format_exc()}")
        st.error("Ha ocurrido un error inesperado. Por favor, intenta más tarde.")

if __name__ == "__main__":
    main()