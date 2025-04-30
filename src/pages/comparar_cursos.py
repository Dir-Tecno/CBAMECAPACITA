import streamlit as st
import pandas as pd
from sqlalchemy import create_engine, text
import logging
import traceback
import sys

# Configuración de la página
st.set_page_config(
    page_title="Comparación de Cursos",
    page_icon="🔄",
    layout="wide"
)

# Estilo con colores del Gobierno de la Provincia de Córdoba
st.markdown("""
    <style>
    /* Colores del Gobierno de Córdoba */
    :root {
        --cordoba-azul: #004A93;
        --cordoba-celeste: #2E75B5;
        --cordoba-gris: #58595B;
        --cordoba-gris-claro: #D9D9D9;
        --cordoba-rojo: #C00000;
        --cordoba-verde: #00B050;
        --cordoba-amarillo: #FFC000;
    }
    
    .main {
        padding: 1.5rem;
        background-color: #ffffff;
    }
    
    h1, h2, h3 {
        color: var(--cordoba-azul);
    }
    
    .stButton>button {
        background-color: var(--cordoba-azul);
        color: white;
        border: none;
        border-radius: 4px;
        padding: 0.5rem 1rem;
        font-weight: 500;
    }
    
    .stButton>button:hover {
        background-color: var(--cordoba-celeste);
    }
    
    .card {
        background-color: #f8f9fa;
        border-radius: 5px;
        padding: 1rem;
        margin-bottom: 1rem;
        border: 1px solid var(--cordoba-gris-claro);
    }
    
    .header-container {
        display: flex;
        align-items: center;
        margin-bottom: 1rem;
        border-bottom: 2px solid var(--cordoba-azul);
        padding-bottom: 0.5rem;
    }
    
    .header-icon {
        font-size: 1.5rem;
        margin-right: 0.5rem;
        color: var(--cordoba-azul);
    }
    
    .header-text {
        font-size: 1.2rem;
        font-weight: 600;
        color: var(--cordoba-azul);
    }
    
    .badge {
        display: inline-block;
        padding: 0.25rem 0.5rem;
        background-color: var(--cordoba-celeste);
        color: white;
        border-radius: 4px;
        margin: 0.2rem;
        font-size: 0.8rem;
    }
    
    .info-text {
        background-color: #e7f3fe;
        border-left: 3px solid var(--cordoba-celeste);
        padding: 0.8rem;
        margin-bottom: 1rem;
    }
    
    .success-text {
        background-color: #e8f5e9;
        border-left: 3px solid var(--cordoba-verde);
        padding: 0.8rem;
        margin-bottom: 1rem;
    }
    
    .warning-text {
        background-color: #fff8e1;
        border-left: 3px solid var(--cordoba-amarillo);
        padding: 0.8rem;
        margin-bottom: 1rem;
    }
    
    .error-text {
        background-color: #ffebee;
        border-left: 3px solid var(--cordoba-rojo);
        padding: 0.8rem;
        margin-bottom: 1rem;
    }
    
    /* Estilo para los dataframes */
    .stDataFrame {
        border: 1px solid var(--cordoba-gris-claro);
        border-radius: 5px;
    }
    
    /* Estilo para los selectbox y multiselect */
    .stSelectbox, .stMultiSelect {
        border-radius: 4px;
    }
    
    /* Logo del Gobierno */
    .gobierno-logo {
        text-align: center;
        margin-bottom: 1rem;
    }
    
    .gobierno-logo img {
        max-width: 200px;
    }
    
    /* Pie de página */
    .footer {
        text-align: center;
        padding: 1rem;
        margin-top: 2rem;
        border-top: 1px solid var(--cordoba-gris-claro);
        color: var(--cordoba-gris);
        font-size: 0.8rem;
    }
    
    /* Mejoras en los inputs */
    .stTextInput>div>div>input {
        border: 1px solid var(--cordoba-gris-claro);
        border-radius: 4px;
    }
    
    .stTextInput>div>div>input:focus {
        border-color: var(--cordoba-azul);
        box-shadow: 0 0 0 0.2rem rgba(0, 74, 147, 0.25);
    }
    
    /* Mejoras en los botones de descarga */
    .stDownloadButton>button {
        background-color: var(--cordoba-celeste);
        color: white;
    }
    
    .stDownloadButton>button:hover {
        background-color: var(--cordoba-azul);
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

        # Cargar datos de cursos históricos
        query_historico = """
            SELECT DISTINCT cs.ID_CURSO, cs.N_CURSO, cs.ID_SECTOR, cs.N_SECTOR
            FROM T_CURSOS_X_SECTOR cs
            ORDER BY cs.N_CURSO
        """
        
        # Cargar datos de certificaciones
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

def mostrar_cursos_historicos(df_historico):
    """Muestra la tabla de cursos históricos con filtros simplificados"""
    st.markdown('<div class="header-container"><span class="header-icon">📚</span><span class="header-text">Cursos Históricos</span></div>', unsafe_allow_html=True)
    
    # Filtros simplificados en una línea
    col1, col2 = st.columns([3, 1])
    with col1:
        busqueda_curso = st.text_input("🔍 Buscar curso", placeholder="Escriba para filtrar...")
    with col2:
        sector_options = ['Todos'] + sorted(df_historico['N_SECTOR'].unique().tolist())
        sector_selected = st.selectbox("Sector", sector_options)
    
    # Aplicar filtros
    df_filtrado = df_historico.copy()
    
    if sector_selected != 'Todos':
        df_filtrado = df_filtrado[df_filtrado['N_SECTOR'] == sector_selected]
        
    if busqueda_curso:
        df_filtrado = df_filtrado[df_filtrado['N_CURSO'].str.contains(busqueda_curso, case=False, na=False)]
    
    # Mostrar resultados
    st.caption(f"Mostrando {len(df_filtrado)} de {len(df_historico)} cursos")
    
    if not df_filtrado.empty:
        st.dataframe(
            df_filtrado,
            use_container_width=True,
            hide_index=True,
            column_config={
                "ID_CURSO": st.column_config.NumberColumn("ID", format="%d"),
                "N_CURSO": st.column_config.TextColumn("Nombre del Curso"),
                "N_SECTOR": st.column_config.TextColumn("Sector")
            }
        )
    else:
        st.info("No se encontraron cursos con los filtros aplicados")

def mostrar_certificaciones(df_certificaciones):
    """Muestra la tabla de certificaciones con filtros simplificados"""
    st.markdown('<div class="header-container"><span class="header-icon">🏆</span><span class="header-text">Certificaciones Actuales</span></div>', unsafe_allow_html=True)
    
    # Filtros simplificados en una línea
    col1, col2 = st.columns([3, 1])
    with col1:
        busqueda_cert = st.text_input("🔍 Buscar certificación", placeholder="Escriba para filtrar...")
    with col2:
        lugar_options = ['Todos'] + sorted(df_certificaciones['LUGAR_CURSADO'].unique().tolist())
        lugar_selected = st.selectbox("Lugar", lugar_options)
    
    # Aplicar filtros
    df_filtrado = df_certificaciones.copy()
    
    if lugar_selected != 'Todos':
        df_filtrado = df_filtrado[df_filtrado['LUGAR_CURSADO'] == lugar_selected]
        
    if busqueda_cert:
        df_filtrado = df_filtrado[df_filtrado['N_CERTIFICACION'].str.contains(busqueda_cert, case=False, na=False)]
    
    # Mostrar resultados
    st.caption(f"Mostrando {len(df_filtrado)} de {len(df_certificaciones)} certificaciones")
    
    if not df_filtrado.empty:
        st.dataframe(
            df_filtrado,
            use_container_width=True,
            hide_index=True,
            column_config={
                "ID_CERTIFICACION": st.column_config.NumberColumn("ID", format="%d"),
                "N_CERTIFICACION": st.column_config.TextColumn("Nombre de Certificación"),
                "LUGAR_CURSADO": st.column_config.TextColumn("Lugar")
            }
        )
    else:
        st.info("No se encontraron certificaciones con los filtros aplicados")

def marcar_equivalencias(df_historico, df_certificaciones):
    st.markdown('<div class="header-container"><span class="header-icon">🔗</span><span class="header-text">Crear Equivalencias</span></div>', unsafe_allow_html=True)
    
    # Estilos adicionales para mejorar la presentación
    st.markdown("""
    <style>
    /* Contenedor principal de equivalencias */
    .equivalencias-container {
        background-color: #f8f9fa;
        border-radius: 8px;
        border: 1px solid var(--cordoba-gris-claro);
        padding: 1.5rem;
        margin-bottom: 2rem;
        box-shadow: 0 2px 10px rgba(0,0,0,0.05);
    }
    
    /* Secciones dentro del contenedor */
    .equivalencias-section {
        margin-bottom: 1.5rem;
    }
    
    /* Título de sección */
    .section-title {
        color: var(--cordoba-azul);
        font-weight: 600;
        font-size: 1.1rem;
        margin-bottom: 0.8rem;
        border-bottom: 1px solid var(--cordoba-celeste);
        padding-bottom: 0.5rem;
    }
    
    /* Contenedor de selecciones */
    .selecciones-container {
        display: flex;
        flex-direction: column;
        gap: 1rem;
        background-color: white;
        border-radius: 6px;
        padding: 1rem;
        border: 1px solid #e0e0e0;
    }
    
    /* Tarjeta de selección */
    .seleccion-card {
        background-color: #f0f7ff;
        border-left: 4px solid var(--cordoba-celeste);
        border-radius: 6px;
        padding: 1rem;
        margin-bottom: 1rem;
    }
    
    /* Título de tarjeta */
    .card-title {
        font-weight: 600;
        color: var(--cordoba-azul);
        margin-bottom: 0.5rem;
        display: flex;
        align-items: center;
    }
    
    .card-title-icon {
        margin-right: 0.5rem;
        font-size: 1.2rem;
    }
    
    /* Contenedor de badges */
    .badges-container {
        display: flex;
        flex-wrap: wrap;
        gap: 0.5rem;
        margin-top: 0.5rem;
    }
    
    /* Badge mejorado */
    .badge-item {
        display: inline-flex;
        align-items: center;
        background-color: var(--cordoba-celeste);
        color: white;
        padding: 0.4rem 0.8rem;
        border-radius: 20px;
        font-size: 0.85rem;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        transition: all 0.2s ease;
    }
    
    .badge-item:hover {
        background-color: var(--cordoba-azul);
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(0,0,0,0.15);
    }
    
    /* Resumen de equivalencia */
    .resumen-equivalencia {
        background-color: #e8f5e9;
        border-left: 4px solid var(--cordoba-verde);
        border-radius: 6px;
        padding: 1rem;
        margin: 1.5rem 0;
    }
    
    /* Botón de acción */
    .action-button {
        background-color: var(--cordoba-azul);
        color: white;
        border: none;
        border-radius: 6px;
        padding: 0.8rem 1.5rem;
        font-weight: 500;
        cursor: pointer;
        width: 100%;
        text-align: center;
        transition: background-color 0.3s ease;
        margin-top: 1rem;
    }
    
    .action-button:hover {
        background-color: var(--cordoba-celeste);
    }
    
    /* Mensaje de éxito animado */
    @keyframes slideIn {
        from { opacity: 0; transform: translateY(-20px); }
        to { opacity: 1; transform: translateY(0); }
    }
    
    .success-message {
        background-color: var(--cordoba-verde);
        color: white;
        border-radius: 6px;
        padding: 1.2rem;
        text-align: center;
        margin: 1.5rem 0;
        animation: slideIn 0.5s ease-out;
        box-shadow: 0 4px 12px rgba(0,0,0,0.15);
    }
    
    .success-title {
        font-size: 1.2rem;
        font-weight: 600;
        margin-bottom: 0.5rem;
    }
    
    /* Tooltip mejorado */
    .tooltip {
        position: relative;
        display: inline-block;
        cursor: help;
    }
    
    .tooltip .tooltip-text {
        visibility: hidden;
        width: 200px;
        background-color: var(--cordoba-azul);
        color: white;
        text-align: center;
        border-radius: 6px;
        padding: 0.5rem;
        position: absolute;
        z-index: 1;
        bottom: 125%;
        left: 50%;
        margin-left: -100px;
        opacity: 0;
        transition: opacity 0.3s;
        font-size: 0.8rem;
        box-shadow: 0 2px 8px rgba(0,0,0,0.2);
    }
    
    .tooltip:hover .tooltip-text {
        visibility: visible;
        opacity: 1;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Instrucciones iniciales
    st.markdown("""
    <div class="info-text">
        <span class="tooltip">
            Seleccione uno o más cursos históricos y una certificación para crear equivalencias
            <span class="tooltip-text">Las equivalencias permiten reconocer cursos históricos como parte de certificaciones actuales</span>
        </span>
    </div>
    """, unsafe_allow_html=True)
    
    
    # Sección de selección de cursos
    st.markdown('<div class="equivalencias-section">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">Paso 1: Seleccionar cursos históricos</div>', unsafe_allow_html=True)
    
    # Selector de cursos históricos
    cursos_historicos = st.multiselect(
        "🔍 Buscar y seleccionar cursos históricos",
        df_historico['N_CURSO'].unique(),
        format_func=lambda x: f"{x}",
        help="Seleccione uno o más cursos históricos para crear equivalencias"
    )
    
    # Mostrar cursos seleccionados en un diseño mejorado
    if cursos_historicos:
        st.markdown('<div class="seleccion-card">', unsafe_allow_html=True)
        st.markdown('<div class="card-title"><span class="card-title-icon">📚</span> Cursos seleccionados</div>', unsafe_allow_html=True)
        st.markdown('<div class="badges-container">', unsafe_allow_html=True)
        
        for curso in cursos_historicos:
            curso_info = df_historico[df_historico['N_CURSO'] == curso].iloc[0]
            st.markdown(f"""
            <div class="badge-item" title="Sector: {curso_info['N_SECTOR']}">
                {curso_info['N_CURSO']}
            </div>
            """, unsafe_allow_html=True)
            
        st.markdown('</div></div>', unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)  # Cierre de sección de cursos
    
    # Sección de selección de certificación
    st.markdown('<div class="equivalencias-section">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">Paso 2: Seleccionar certificación</div>', unsafe_allow_html=True)
    
    # Selector de certificación
    certificacion = st.selectbox(
        "🔍 Buscar y seleccionar certificación",
        df_certificaciones['N_CERTIFICACION'].unique(),
        format_func=lambda x: f"{x}",
        help="Seleccione la certificación actual a la que equivalen los cursos históricos"
    )
    
    # Mostrar certificación seleccionada en un diseño mejorado
    if certificacion:
        cert_info = df_certificaciones[df_certificaciones['N_CERTIFICACION'] == certificacion].iloc[0]
        st.markdown(f"""
        <div class="seleccion-card">
            <div class="card-title"><span class="card-title-icon">🏆</span> Certificación seleccionada</div>
            <p><strong>Nombre:</strong> {cert_info["N_CERTIFICACION"]}</p>
            <p><strong>Lugar:</strong> {cert_info["LUGAR_CURSADO"]}</p>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)  # Cierre de sección de certificación
    
    # Sección de observaciones
    st.markdown('<div class="equivalencias-section">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">Paso 3: Agregar observaciones (opcional)</div>', unsafe_allow_html=True)
    
    # Campo de observaciones
    observacion = st.text_area(
        "Observaciones",
        placeholder="Ingrese observaciones sobre esta equivalencia...",
        help="Puede agregar notas o aclaraciones sobre esta equivalencia"
    )
    
    st.markdown('</div>', unsafe_allow_html=True)  # Cierre de sección de observaciones
    
    # Resumen de la equivalencia a crear
    if cursos_historicos and certificacion:
        st.markdown(f"""
        <div class="resumen-equivalencia">
            <div class="card-title"><span class="card-title-icon">📋</span> Resumen de equivalencia</div>
            <p>Se establecerá que <strong>{len(cursos_historicos)} curso(s)</strong> histórico(s) son equivalentes a la certificación <strong>"{certificacion}"</strong>.</p>
            <p><strong>Observaciones:</strong> {observacion if observacion.strip() else "Sin observaciones adicionales"}</p>
        </div>
        """, unsafe_allow_html=True)
    
    # Botón para guardar
    guardar_btn = st.button(
        "Guardar Equivalencias", 
        use_container_width=True,
        help="Guarda las equivalencias entre los cursos históricos y la certificación seleccionada"
    )
    
    st.markdown('</div>', unsafe_allow_html=True)  # Cierre del contenedor principal
    
    # Contenedor para mensajes de resultado
    resultado_container = st.empty()
    
    if guardar_btn:
        try:
            if not cursos_historicos:
                resultado_container.markdown('<div class="warning-text">Debe seleccionar al menos un curso histórico</div>', unsafe_allow_html=True)
                return
                
            if not certificacion:
                resultado_container.markdown('<div class="warning-text">Debe seleccionar una certificación</div>', unsafe_allow_html=True)
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
                        resultado_container.markdown(f'<div class="warning-text">No se encontró el ID para la certificación {certificacion}</div>', unsafe_allow_html=True)
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
                            resultado_container.markdown(f'<div class="warning-text">No se encontró el ID para el curso {curso_historico}</div>', unsafe_allow_html=True)
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
                        
                        # Insertar nueva equivalencia
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
                    
                # Mensaje de éxito mejorado y más visual
                if nuevas > 0:
                    # Mensaje de éxito animado y destacado
                    resultado_container.markdown(f"""
                    <div class="success-message">
                        <div class="success-title">✅ ¡Equivalencias guardadas con éxito!</div>
                        <p>Se crearon {nuevas} nuevas equivalencias</p>
                    </div>
                    
                    <div class="seleccion-card" style="background-color: #e8f5e9; border-left-color: var(--cordoba-verde);">
                        <div class="card-title"><span class="card-title-icon">📋</span> Detalle de la operación</div>
                        <p><strong>Cursos históricos:</strong> {", ".join(cursos_historicos)}</p>
                        <p><strong>Certificación:</strong> {certificacion}</p>
                        <p><strong>Observaciones:</strong> {observacion}</p>
                        <p><strong>Fecha y hora:</strong> {pd.Timestamp.now().strftime("%d/%m/%Y %H:%M:%S")}</p>
                    </div>
                    """, unsafe_allow_html=True)
                    
                if existentes > 0:
                    st.markdown(f'<div class="info-text">{existentes} equivalencias ya existían y no fueron modificadas</div>', unsafe_allow_html=True)
                
                if nuevas == 0 and existentes > 0:
                    resultado_container.markdown('<div class="warning-text">Todas las equivalencias seleccionadas ya existían</div>', unsafe_allow_html=True)
        except Exception as e:
            resultado_container.markdown(f'<div class="error-text">Error al guardar las equivalencias: {str(e)}</div>', unsafe_allow_html=True)
            logger.error(f"Error al guardar equivalencias: {traceback.format_exc()}")

def mostrar_equivalencias_existentes():
    """Función simplificada para mostrar equivalencias existentes"""
    st.markdown('<div class="header-container"><span class="header-icon">📋</span><span class="header-text">Equivalencias Existentes</span></div>', unsafe_allow_html=True)
    
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
            
            # Filtros simplificados
            busqueda = st.text_input("🔍 Buscar equivalencia", placeholder="Buscar por curso o certificación...")
            
            # Aplicar filtro de búsqueda
            df_eq_filtrado = df_equivalencias.copy()
            if busqueda:
                df_eq_filtrado = df_eq_filtrado[
                    df_eq_filtrado['curso_historico'].str.contains(busqueda, case=False, na=False) |
                    df_eq_filtrado['certificacion_actual'].str.contains(busqueda, case=False, na=False)
                ]
            
            # Mostrar contador de resultados
            st.caption(f"Mostrando {len(df_eq_filtrado)} de {len(df_equivalencias)} equivalencias")
            
            if df_equivalencias.empty:
                st.markdown('<div class="info-text">No hay equivalencias registradas aún. Utilice la sección "Crear Equivalencias" para comenzar.</div>', unsafe_allow_html=True)
            else:
                # Mostrar tabla de equivalencias
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
                            "Fecha",
                            format="DD/MM/YYYY"
                        ),
                        "observaciones": st.column_config.TextColumn("Observaciones"),
                        "estado": st.column_config.TextColumn("Estado")
                    }
                )
                
                # Exportar a CSV
                csv = df_eq_filtrado.to_csv(index=False).encode('utf-8')
                st.download_button(
                    label="Exportar a CSV",
                    data=csv,
                    file_name="equivalencias.csv",
                    mime="text/csv"
                )
                
                # Sección para eliminar equivalencias
                st.markdown('<div class="header-container"><span class="header-icon">🗑️</span><span class="header-text">Eliminar Equivalencia</span></div>', unsafe_allow_html=True)
                
                # Selector de ID con dropdown
                ids_disponibles = df_eq_filtrado['ID_EQUIVALENCIA'].tolist()
                if ids_disponibles:
                    id_seleccionado = st.selectbox(
                        "Seleccione la equivalencia a eliminar",
                        options=ids_disponibles,
                        format_func=lambda x: f"ID: {x} - {df_eq_filtrado[df_eq_filtrado['ID_EQUIVALENCIA'] == x]['curso_historico'].values[0]} → {df_eq_filtrado[df_eq_filtrado['ID_EQUIVALENCIA'] == x]['certificacion_actual'].values[0]}"
                    )
                    
                    # Mostrar detalles de la equivalencia seleccionada
                    if id_seleccionado:
                        eq_seleccionada = df_eq_filtrado[df_eq_filtrado['ID_EQUIVALENCIA'] == id_seleccionado].iloc[0]
                        st.markdown(f"""
                        <div class="info-text">
                        <strong>Curso:</strong> {eq_seleccionada['curso_historico']}<br>
                        <strong>Sector:</strong> {eq_seleccionada['sector_curso'] if pd.notna(eq_seleccionada['sector_curso']) else 'No especificado'}<br>
                        <strong>Certificación:</strong> {eq_seleccionada['certificacion_actual']}<br>
                        <strong>Observaciones:</strong> {eq_seleccionada['observaciones']}
                        </div>
                        """, unsafe_allow_html=True)
                        
                        # Botón de eliminación
                        if st.button("Eliminar Equivalencia", type="primary"):
                            try:
                                with engine.connect() as conn:
                                    # Eliminar físicamente el registro
                                    sql = text("""
                                        DELETE FROM T_EQUIVALENCIAS_CURSOS 
                                        WHERE ID_EQUIVALENCIA = :id
                                    """)
                                    conn.execute(sql, {"id": id_seleccionado})
                                    conn.commit()
                                
                                st.markdown('<div class="success-text">Equivalencia eliminada correctamente</div>', unsafe_allow_html=True)
                                st.experimental_rerun()
                            except Exception as e:
                                st.markdown(f'<div class="error-text">Error al eliminar la equivalencia: {str(e)}</div>', unsafe_allow_html=True)
                                logger.error(f"Error al eliminar equivalencia: {traceback.format_exc()}")
    except Exception as e:
        st.markdown(f'<div class="error-text">Error al mostrar equivalencias existentes: {str(e)}</div>', unsafe_allow_html=True)
        logger.error(f"Error al mostrar equivalencias: {traceback.format_exc()}")

def main():
    """Función principal con diseño mejorado"""
    # Encabezado con logo
    st.markdown("""
    <div class="gobierno-logo">
        <h1 style="color: #004A93;">Comparación de Cursos y Certificaciones</h1>
        <p style="color: #58595B;">Sistema de Gestión de Capacitaciones - Gobierno de Córdoba</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Cargar datos
    df_historico, df_certificaciones = load_data()
    
    if df_historico is None or df_certificaciones is None:
        st.error("No se pudieron cargar los datos. Por favor, verifica la conexión a la base de datos.")
        return
    
    # Menú de navegación mejorado
    menu = ["Explorar Cursos", "Crear Equivalencias", "Ver Equivalencias"]
    
    # Crear pestañas con estilo mejorado
    col1, col2, col3 = st.columns(3)
    with col1:
        btn1 = st.button("📚 Explorar Cursos", use_container_width=True)
    with col2:
        btn2 = st.button("🔗 Crear Equivalencias", use_container_width=True)
    with col3:
        btn3 = st.button("📋 Ver Equivalencias", use_container_width=True)
    
    # Inicializar estado de sesión si no existe
    if 'menu_option' not in st.session_state:
        st.session_state.menu_option = "Explorar Cursos"
    
    # Actualizar opción según botón presionado
    if btn1:
        st.session_state.menu_option = "Explorar Cursos"
    elif btn2:
        st.session_state.menu_option = "Crear Equivalencias"
    elif btn3:
        st.session_state.menu_option = "Ver Equivalencias"
    
    st.markdown("<hr>", unsafe_allow_html=True)
    
    # Mostrar contenido según la opción seleccionada
    if st.session_state.menu_option == "Explorar Cursos":
        col1, col2 = st.columns(2)
        with col1:
            mostrar_cursos_historicos(df_historico)
        with col2:
            mostrar_certificaciones(df_certificaciones)
    
    elif st.session_state.menu_option == "Crear Equivalencias":
        marcar_equivalencias(df_historico, df_certificaciones)
    
    elif st.session_state.menu_option == "Ver Equivalencias":
        mostrar_equivalencias_existentes()
    
    # Pie de página
    st.markdown("""
    <div class="footer">
        <p>© 2025 Gobierno de la Provincia de Córdoba - Todos los derechos reservados</p>
        <p>Sistema de Gestión de Capacitaciones</p>
    </div>
    """, unsafe_allow_html=True)

# Ejecutar la aplicación
if __name__ == "__main__":
    main()