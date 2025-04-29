import streamlit as st
import pandas as pd
from sqlalchemy import create_engine, text
import logging
import traceback
import sys
import os

# Configuración de la página - DEBE SER LA PRIMERA LLAMADA A STREAMLIT
st.set_page_config(
    page_title="Comparación de Cursos y Certificaciones",
    page_icon="🔄",
    layout="wide"
)

# Estilo personalizado
st.markdown("""
    <style>
    .main {
        padding: 2rem;
        background-color: #f9f9f9;
    }
    .stButton>button {
        width: 100%;
        background-color: #0066cc;
        color: white;
        border-radius: 5px;
        padding: 0.75rem 1rem;
        font-weight: 500;
        transition: all 0.3s ease;
    }
    .stButton>button:hover {
        background-color: #004c99;
        box-shadow: 0 4px 8px rgba(0,0,0,0.1);
        transform: translateY(-2px);
    }
    .stSelectbox {
        margin-bottom: 1rem;
    }
    .stMultiSelect {
        margin-bottom: 1rem;
    }
    .stDataFrame {
        border: 1px solid #e6e6e6;
        border-radius: 8px;
        padding: 1rem;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
    .info-box {
        background-color: #e9f5ff;
        padding: 1.5rem;
        border-radius: 10px;
        border-left: 5px solid #0066cc;
        margin-bottom: 2rem;
        box-shadow: 0 2px 5px rgba(0,0,0,0.05);
    }
    .metric-card {
        background-color: white;
        padding: 1.5rem;
        border-radius: 10px;
        box-shadow: 0 3px 10px rgba(0,0,0,0.08);
        transition: all 0.3s ease;
    }
    .metric-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 5px 15px rgba(0,0,0,0.1);
    }
    .curso-badge {
        display: inline-block;
        background-color: #e6f2ff;
        border: 1px solid #99ccff;
        border-radius: 15px;
        padding: 0.4rem 1rem;
        margin: 0.3rem;
        font-size: 0.9rem;
        transition: all 0.2s ease;
    }
    .curso-badge:hover {
        background-color: #cce5ff;
        border-color: #66b3ff;
    }
    h1, h2, h3, h4, h5, h6 {
        color: #2c3e50;
        font-weight: 600;
    }
    .stExpander {
        border-radius: 8px;
        box-shadow: 0 2px 5px rgba(0,0,0,0.05);
    }
    .stTextInput>div>div>input {
        border-radius: 5px;
    }
    .stDateInput>div>div>input {
        border-radius: 5px;
    }
    </style>
""", unsafe_allow_html=True)

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
        # Obtener credenciales desde secrets.toml
        db_credentials = st.secrets["db_credentials"]
        connection_string = f"mysql+pymysql://{db_credentials['DB_USER']}:{db_credentials['DB_PASSWORD']}@{db_credentials['DB_HOST']}:{db_credentials['DB_PORT']}/{db_credentials['DB_NAME']}"
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

        # Cargar datos de la nueva tabla T_CURSOS_X_SECTOR en lugar de T_CURSOS_HISTORICO
        query_historico = """
            SELECT DISTINCT cs.ID_CURSO, cs.N_CURSO, cs.ID_SECTOR, cs.N_SECTOR
            FROM T_CURSOS_X_SECTOR cs
            ORDER BY cs.N_CURSO
        """
        query_certificaciones = """
            SELECT DISTINCT cl.ID_CERTIFICACION, cl.N_CERTIFICACION, cl.LUGAR_CURSADO 
            FROM T_CERTIF_X_LOCALIDAD cl
            ORDER BY cl.N_CERTIFICACION
        """
        
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
        
        # Filtros mejorados para cursos históricos
        with st.expander("Filtros Avanzados", expanded=False):
            # Filtro por sector
            sectores = ['Todos'] + sorted(df_historico['N_SECTOR'].unique().tolist())
            sector_selected = st.selectbox("Filtrar por Sector", sectores, key="sector_filter")
            
            # Filtro por texto
            busqueda_curso = st.text_input("Buscar curso histórico", key="busqueda_curso")
            
            # Ordenar por
            orden_options = ["Nombre (A-Z)", "Nombre (Z-A)", "Sector (A-Z)", "Sector (Z-A)"]
            orden_selected = st.selectbox("Ordenar por", orden_options, key="orden_historico")
        
        # Aplicar filtros
        df_historico_filtrado = df_historico.copy()
        
        # Filtrar por sector
        if sector_selected != 'Todos':
            df_historico_filtrado = df_historico_filtrado[df_historico_filtrado['N_SECTOR'] == sector_selected]
            
        # Filtrar por texto
        if busqueda_curso:
            df_historico_filtrado = df_historico_filtrado[df_historico_filtrado['N_CURSO'].str.contains(busqueda_curso, case=False, na=False)]
        
        # Aplicar ordenamiento
        if orden_selected == "Nombre (A-Z)":
            df_historico_filtrado = df_historico_filtrado.sort_values('N_CURSO')
        elif orden_selected == "Nombre (Z-A)":
            df_historico_filtrado = df_historico_filtrado.sort_values('N_CURSO', ascending=False)
        elif orden_selected == "Sector (A-Z)":
            df_historico_filtrado = df_historico_filtrado.sort_values('N_SECTOR')
        elif orden_selected == "Sector (Z-A)":
            df_historico_filtrado = df_historico_filtrado.sort_values('N_SECTOR', ascending=False)
            
        # Mostrar contador de resultados
        st.caption(f"Mostrando {len(df_historico_filtrado)} de {len(df_historico)} cursos")
            
        if not df_historico_filtrado.empty:
            st.dataframe(
                df_historico_filtrado,
                use_container_width=True,
                hide_index=True,
                column_config={
                    "ID_CURSO": st.column_config.NumberColumn("ID", format="%d"),
                    "N_CURSO": st.column_config.TextColumn("Nombre del Curso"),
                    "N_SECTOR": st.column_config.TextColumn("Sector")
                }
            )
        else:
            st.warning("No hay datos históricos disponibles con los filtros seleccionados")

    with col2:
        st.subheader("Certificaciones Actuales")
        
        # Filtros mejorados para certificaciones
        with st.expander("Filtros Avanzados", expanded=False):
            # Filtro por lugar de cursado
            lugares = ['Todos'] + sorted(df_certificaciones['LUGAR_CURSADO'].unique().tolist())
            lugar_selected = st.selectbox("Filtrar por Lugar", lugares, key="lugar_filter")
            
            # Filtro por texto
            busqueda_cert = st.text_input("Buscar certificación", key="busqueda_cert")
            
            # Ordenar por
            orden_cert_options = ["Nombre (A-Z)", "Nombre (Z-A)", "Lugar (A-Z)", "Lugar (Z-A)"]
            orden_cert_selected = st.selectbox("Ordenar por", orden_cert_options, key="orden_cert")
        
        # Aplicar filtros
        df_certificaciones_filtrado = df_certificaciones.copy()
        
        # Filtrar por lugar
        if lugar_selected != 'Todos':
            df_certificaciones_filtrado = df_certificaciones_filtrado[df_certificaciones_filtrado['LUGAR_CURSADO'] == lugar_selected]
            
        # Filtrar por texto
        if busqueda_cert:
            df_certificaciones_filtrado = df_certificaciones_filtrado[
                df_certificaciones_filtrado['N_CERTIFICACION'].str.contains(busqueda_cert, case=False, na=False)
            ]
        
        # Aplicar ordenamiento
        if orden_cert_selected == "Nombre (A-Z)":
            df_certificaciones_filtrado = df_certificaciones_filtrado.sort_values('N_CERTIFICACION')
        elif orden_cert_selected == "Nombre (Z-A)":
            df_certificaciones_filtrado = df_certificaciones_filtrado.sort_values('N_CERTIFICACION', ascending=False)
        elif orden_cert_selected == "Lugar (A-Z)":
            df_certificaciones_filtrado = df_certificaciones_filtrado.sort_values('LUGAR_CURSADO')
        elif orden_cert_selected == "Lugar (Z-A)":
            df_certificaciones_filtrado = df_certificaciones_filtrado.sort_values('LUGAR_CURSADO', ascending=False)
            
        # Mostrar contador de resultados
        st.caption(f"Mostrando {len(df_certificaciones_filtrado)} de {len(df_certificaciones)} certificaciones")
            
        if not df_certificaciones_filtrado.empty:
            st.dataframe(
                df_certificaciones_filtrado,
                use_container_width=True,
                hide_index=True,
                column_config={
                    "ID_CERTIFICACION": st.column_config.NumberColumn("ID", format="%d"),
                    "N_CERTIFICACION": st.column_config.TextColumn("Nombre de Certificación"),
                    "LUGAR_CURSADO": st.column_config.TextColumn("Lugar")
                }
            )
        else:
            st.warning("No hay certificaciones disponibles con los filtros seleccionados")

def marcar_equivalencias(df_historico, df_certificaciones):
    """Función para marcar equivalencias entre cursos históricos y certificaciones"""
    st.subheader("Marcar Equivalencias")
    
    # Crear dos columnas para la selección
    col1, col2 = st.columns(2)
    
    with col1:
        # Selector MÚLTIPLE de cursos históricos
        cursos_historicos = st.multiselect(
            "Seleccionar Cursos Históricos",
            df_historico['N_CURSO'].unique(),
            format_func=lambda x: f"{x}"  # Simplificar el formato
        )
        
        if cursos_historicos:
            st.markdown("**Detalles de los Cursos Históricos:**")
            for curso in cursos_historicos:
                curso_info = df_historico[df_historico['N_CURSO'] == curso].iloc[0]
                st.markdown(f"""
                <div class="curso-badge">
                    <strong>{curso_info['N_CURSO']}</strong> - Sector: {curso_info['N_SECTOR']}
                </div>
                """, unsafe_allow_html=True)
    
    with col2:
        # Selector de certificación con búsqueda
        certificacion = st.selectbox(
            "Seleccionar Certificación",
            df_certificaciones['N_CERTIFICACION'].unique(),
            format_func=lambda x: f"{x}"  # Simplificar el formato
        )
        
        if certificacion:
            cert_info = df_certificaciones[df_certificaciones['N_CERTIFICACION'] == certificacion].iloc[0]
            st.info(f"""
            **Detalles de la Certificación:**
            - Certificación: {cert_info['N_CERTIFICACION']}
            - Lugar: {cert_info['LUGAR_CURSADO']}
            """)
    
    # Agregar campo para observaciones personalizadas
    observacion = st.text_area(
        "Observaciones (opcional)",
        value="",
        placeholder="Ingrese observaciones sobre esta equivalencia...",
        help="Puede dejar comentarios o notas sobre esta equivalencia"
    )
    
    # Botón para guardar la equivalencia
    if st.button("Guardar Equivalencias"):
        try:
            if not cursos_historicos:
                st.warning("Debe seleccionar al menos un curso histórico.")
                return
                
            if not certificacion:
                st.warning("Debe seleccionar una certificación.")
                return
                
            # Si no se ingresó observación, usar un valor predeterminado
            if not observacion.strip():
                if len(cursos_historicos) > 1:
                    observacion = "Equivalencia múltiple"
                else:
                    observacion = "Equivalencia directa"
                
            engine = get_database_connection()
            if engine is not None:
                # Insertar las equivalencias
                with engine.connect() as conn:
                    # Contador para equivalencias existentes y nuevas
                    existentes = 0
                    nuevas = 0
                    
                    # Obtener ID_CERTIFICACION
                    id_cert_query = text("""
                        SELECT ID_CERTIFICACION 
                        FROM T_CERTIF_X_LOCALIDAD 
                        WHERE N_CERTIFICACION = :cert
                    """)
                    id_cert_result = conn.execute(id_cert_query, {"cert": certificacion}).fetchone()
                    
                    if not id_cert_result:
                        st.warning(f"No se encontró el ID para la certificación {certificacion}")
                        return
                    
                    id_certificacion = id_cert_result[0]
                    
                    for curso_historico in cursos_historicos:
                        # Obtener el ID_CURSO de la tabla T_CURSOS_X_SECTOR
                        id_curso_query = text("""
                            SELECT ID_CURSO 
                            FROM T_CURSOS_X_SECTOR 
                            WHERE N_CURSO = :curso
                        """)
                        id_curso_result = conn.execute(id_curso_query, {"curso": curso_historico}).fetchone()
                        
                        if not id_curso_result:
                            st.warning(f"No se encontró el ID para el curso {curso_historico}")
                            continue
                        
                        id_curso = id_curso_result[0]
                        
                        # Verificar si ya existe la equivalencia
                        check_sql = text("""
                            SELECT ID_EQUIVALENCIA 
                            FROM T_EQUIVALENCIAS_CURSOS eq
                            JOIN T_ESTADOS_EQUIVALENCIAS ee ON eq.ID_ESTADO = ee.ID_ESTADO
                            WHERE eq.ID_CURSO_HISTORICO = :id_curso 
                            AND eq.ID_CERTIF_ACTUAL = :id_cert 
                            AND ee.N_ESTADO = 'ACTIVO'
                        """)
                        result = conn.execute(check_sql, {"id_curso": id_curso, "id_cert": id_certificacion}).fetchone()

                        
                        if result:
                            existentes += 1
                            continue
                        
                        #Insertar nueva equivalencia con los nuevos nombres de campos
                        sql = text("""
                            INSERT INTO T_EQUIVALENCIAS_CURSOS 
                            (ID_CURSO_HISTORICO, N_CURSO_HISTORICO, ID_CERTIF_ACTUAL, N_CERTIF_ACTUAL, OBSERVACIONES, ID_ESTADO)
                            VALUES (:id_curso, :curso, :id_cert, :cert, :obs, 
                                (SELECT ID_ESTADO FROM T_ESTADOS_EQUIVALENCIAS WHERE N_ESTADO = 'ACTIVO')
                            )
                        """)
                        conn.execute(sql, {
                            "id_curso": id_curso,
                            "curso": curso_historico,
                            "id_cert": id_certificacion,
                            "cert": certificacion,
                            "obs": observacion
                        })
                        nuevas += 1
                        
                    conn.commit()
                    
                if nuevas > 0:
                    st.success(f"¡Se guardaron {nuevas} nuevas equivalencias exitosamente!")
                if existentes > 0:
                    st.info(f"{existentes} equivalencias ya existían y no fueron modificadas.")
                if nuevas == 0 and existentes > 0:
                    st.warning("Todas las equivalencias seleccionadas ya existían.")
        except Exception as e:
            st.error(f"Error al guardar las equivalencias: {str(e)}")
            logger.error(f"Error al guardar equivalencias: {traceback.format_exc()}")

def mostrar_equivalencias_existentes():
    """Función para mostrar las equivalencias existentes"""
    try:
        engine = get_database_connection()
        if engine is not None:
            query = """
                SELECT 
                    eq.ID_EQUIVALENCIA,
                    eq.N_CURSO_HISTORICO as curso_historico,
                    cs.N_SECTOR as sector_curso,
                    eq.N_CERTIF_ACTUAL as certificacion_actual,
                    eq.FECH_EQUIVALENCIA as fecha_creacion,
                    eq.OBSERVACIONES as observaciones,
                    ee.N_ESTADO as estado
                FROM T_EQUIVALENCIAS_CURSOS eq
                JOIN T_ESTADOS_EQUIVALENCIAS ee ON eq.ID_ESTADO = ee.ID_ESTADO
                LEFT JOIN T_CURSOS_X_SECTOR cs ON eq.ID_CURSO_HISTORICO = cs.ID_CURSO
                WHERE ee.N_ESTADO = 'ACTIVO'
                ORDER BY eq.FECH_EQUIVALENCIA DESC
            """
            df_equivalencias = pd.read_sql(query, engine)
            
            st.subheader("Equivalencias Existentes")
            
            # Filtros para equivalencias existentes
            with st.expander("Filtros de Equivalencias", expanded=False):
                # Filtro por curso histórico
                if not df_equivalencias.empty:
                    cursos_eq = ['Todos'] + sorted(df_equivalencias['curso_historico'].unique().tolist())
                    curso_eq_selected = st.selectbox("Filtrar por Curso Histórico", cursos_eq, key="curso_eq_filter")
                    
                    # Filtro por certificación
                    certs_eq = ['Todas'] + sorted(df_equivalencias['certificacion_actual'].unique().tolist())
                    cert_eq_selected = st.selectbox("Filtrar por Certificación", certs_eq, key="cert_eq_filter")
                    
                    # Filtro por sector
                    sectores_eq = ['Todos'] + sorted(df_equivalencias['sector_curso'].dropna().unique().tolist())
                    sector_eq_selected = st.selectbox("Filtrar por Sector", sectores_eq, key="sector_eq_filter")
                    
                    # Filtro por fecha
                    col1, col2 = st.columns(2)
                    with col1:
                        fecha_desde = st.date_input("Desde", value=None, key="fecha_desde")
                    with col2:
                        fecha_hasta = st.date_input("Hasta", value=None, key="fecha_hasta")
            
            # Aplicar filtros a equivalencias
            df_eq_filtrado = df_equivalencias.copy()
            
            if not df_equivalencias.empty:
                # Filtrar por curso histórico
                if curso_eq_selected != 'Todos':
                    df_eq_filtrado = df_eq_filtrado[df_eq_filtrado['curso_historico'] == curso_eq_selected]
                    
                # Filtrar por certificación
                if cert_eq_selected != 'Todas':
                    df_eq_filtrado = df_eq_filtrado[df_eq_filtrado['certificacion_actual'] == cert_eq_selected]
                    
                # Filtrar por sector
                if sector_eq_selected != 'Todos':
                    df_eq_filtrado = df_eq_filtrado[df_eq_filtrado['sector_curso'] == sector_eq_selected]
                    
                # Filtrar por fecha
                if fecha_desde:
                    df_eq_filtrado = df_eq_filtrado[df_eq_filtrado['fecha_creacion'].dt.date >= fecha_desde]
                if fecha_hasta:
                    df_eq_filtrado = df_eq_filtrado[df_eq_filtrado['fecha_creacion'].dt.date <= fecha_hasta]
                
                # Mostrar contador de resultados
                st.caption(f"Mostrando {len(df_eq_filtrado)} de {len(df_equivalencias)} equivalencias")
            
            if df_equivalencias.empty:
                st.info("No hay equivalencias registradas aún.")
            else:
                # Botón para exportar a Excel
                csv = df_eq_filtrado.to_csv(index=False).encode('utf-8')
                st.download_button(
                    label="Exportar a CSV",
                    data=csv,
                    file_name="equivalencias.csv",
                    mime="text/csv",
                    help="Descargar las equivalencias filtradas en formato CSV"
                )
                
                # Mostrar tabla con mejoras visuales
                st.dataframe(
                    df_eq_filtrado,
                    use_container_width=True,
                    hide_index=True,
                    column_config={
                        "ID_EQUIVALENCIA": st.column_config.NumberColumn("ID", format="%d"),
                        "curso_historico": st.column_config.TextColumn("Curso Histórico"),
                        "sector_curso": st.column_config.TextColumn("Sector"),
                        "certificacion_actual": st.column_config.TextColumn("Certificación Actual"),
                        "fecha_creacion": st.column_config.DatetimeColumn(
                            "Fecha de Equivalencia",
                            format="DD/MM/YYYY HH:mm"
                        ),
                        "observaciones": st.column_config.TextColumn("Observaciones"),
                        "estado": st.column_config.TextColumn("Estado")
                    }
                )
                
                # Sección para eliminar equivalencias
                st.subheader("Eliminar Equivalencia")
                id_a_eliminar = st.number_input("ID de la equivalencia a eliminar", min_value=1, step=1)
                
                if st.button("Eliminar Equivalencia"):
                    # Verificar si el ID existe
                    if id_a_eliminar in df_equivalencias['ID_EQUIVALENCIA'].values:
                        # Mostrar confirmación
                        st.warning(f"¿Está seguro de eliminar la equivalencia con ID {id_a_eliminar}?")
                        col1, col2 = st.columns(2)
                        with col1:
                            if st.button("Confirmar Eliminación", key="confirm_delete"):
                                try:
                                    with engine.connect() as conn:
                                        # Actualizar el estado a INACTIVO en lugar de eliminar físicamente
                                        sql = text("""
                                            UPDATE T_EQUIVALENCIAS_CURSOS 
                                            SET ID_ESTADO = (SELECT ID_ESTADO FROM T_ESTADOS_EQUIVALENCIAS WHERE N_ESTADO = 'INACTIVO')
                                            WHERE ID_EQUIVALENCIA = :id
                                        """)
                                        conn.execute(sql, {"id": id_a_eliminar})
                                        conn.commit()
                                    
                                    st.success(f"Equivalencia con ID {id_a_eliminar} eliminada correctamente.")
                                    st.experimental_rerun()
                                except Exception as e:
                                    st.error(f"Error al eliminar la equivalencia: {str(e)}")
                                    logger.error(f"Error al eliminar equivalencia: {traceback.format_exc()}")
                        with col2:
                            if st.button("Cancelar", key="cancel_delete"):
                                st.experimental_rerun()
                    else:
                        st.error(f"No existe una equivalencia con el ID {id_a_eliminar}")
    except Exception as e:
        st.error(f"Error al cargar equivalencias existentes: {str(e)}")
        logger.error(f"Error al cargar equivalencias: {traceback.format_exc()}")

def main():
    try:
        # Encabezado con diseño mejorado
        st.markdown("""
            <h1 style='text-align: center; color: #0066cc; margin-bottom: 2rem;'>
                🔄 Sistema de Equivalencias de Cursos
            </h1>
        """, unsafe_allow_html=True)
        
        # Descripción mejorada
        st.markdown("""
            <div class="info-box">
                <h4 style='margin: 0; color: #0066cc;'>Acerca de esta herramienta</h4>
                <p style='margin-top: 0.5rem;'>Esta herramienta permite establecer equivalencias entre cursos históricos y certificaciones actuales. 
                Facilita la gestión y seguimiento de las correspondencias entre programas educativos.</p>
            </div>
        """, unsafe_allow_html=True)

        # Cargar datos
        df_historico, df_certificaciones = load_data()
        
        if df_historico is None or df_certificaciones is None:
            st.error("No se pudieron cargar los datos. Por favor, verifica la conexión a la base de datos.")
            return

        # Métricas en tarjetas mejoradas
        col1, col2 = st.columns(2)
        with col1:
            st.markdown(f"""
                <div class="metric-card">
                    <h3 style='margin: 0; color: #0066cc;'>Cursos Históricos</h3>
                    <h2 style='margin: 0; margin-top: 0.5rem;'>{len(df_historico)}</h2>
                </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown(f"""
                <div class="metric-card">
                    <h3 style='margin: 0; color: #0066cc;'>Certificaciones</h3>
                    <h2 style='margin: 0; margin-top: 0.5rem;'>{len(df_certificaciones)}</h2>
                </div>
            """, unsafe_allow_html=True)

        # Separador visual
        st.markdown("<hr style='margin: 2rem 0;'>", unsafe_allow_html=True)

        # Mostrar tablas comparativas con diseño mejorado
        mostrar_tabla_comparativa(df_historico, df_certificaciones)
        
        # Separador visual
        st.markdown("<hr style='margin: 2rem 0;'>", unsafe_allow_html=True)
        
        # Sección para marcar equivalencias (solo una vez)
        marcar_equivalencias(df_historico, df_certificaciones)
        
        # Separador visual
        st.markdown("<hr style='margin: 2rem 0;'>", unsafe_allow_html=True)
        
        # Mostrar tabla de equivalencias existentes al final
        mostrar_equivalencias_existentes()

    except Exception as e:
        logger.error(f"Error en la aplicación: {traceback.format_exc()}")
        st.error("Ha ocurrido un error inesperado. Por favor, intenta más tarde.")

if __name__ == "__main__":
    main()