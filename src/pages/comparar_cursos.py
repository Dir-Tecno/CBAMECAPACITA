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
    h1, h2, h3 {
        color: var(--cordoba-azul);
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        font-weight: 700;
        letter-spacing: 0.5px;
    }
    .stButton>button {
        background: linear-gradient(90deg, var(--cordoba-azul) 60%, var(--cordoba-celeste) 100%);
        color: white;
        border: none;
        border-radius: 6px;
        padding: 0.6rem 1.2rem;
        font-weight: 600;
        box-shadow: 0 2px 8px rgba(46,117,181,0.08);
        transition: background 0.3s, box-shadow 0.3s;
    }
    .stButton>button:hover {
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
    .header-container {
        display: flex;
        align-items: center;
        margin-bottom: 1.2rem;
        border-bottom: 2px solid var(--cordoba-azul);
        padding-bottom: 0.7rem;
        background: linear-gradient(90deg, #e7f3fe 60%, #fff 100%);
        border-radius: 8px 8px 0 0;
        box-shadow: 0 1px 4px rgba(0,74,147,0.04);
    }
    .header-icon {
        font-size: 2rem;
        margin-right: 0.7rem;
        color: var(--cordoba-azul);
        filter: drop-shadow(0 2px 4px #2e75b533);
    }
    .header-text {
        font-size: 1.3rem;
        font-weight: 700;
        color: var(--cordoba-azul);
        letter-spacing: 0.5px;
    }
    .badge {
        display: inline-block;
        padding: 0.3rem 0.7rem;
        background: linear-gradient(90deg, var(--cordoba-celeste) 60%, var(--cordoba-azul) 100%);
        color: white;
        border-radius: 6px;
        margin: 0.2rem;
        font-size: 0.85rem;
        font-weight: 500;
        box-shadow: 0 1px 4px rgba(46,117,181,0.10);
    }
    .info-text, .success-text, .warning-text, .error-text {
        border-radius: 8px;
        margin-bottom: 1.2rem;
        font-size: 1rem;
        font-weight: 500;
        box-shadow: 0 1px 4px rgba(0,0,0,0.04);
    }
    .info-text {
        background: #e7f3fe;
        border-left: 4px solid var(--cordoba-celeste);
        color: #004A93;
    }
    .success-text {
        background: #e8f5e9;
        border-left: 4px solid var(--cordoba-verde);
        color: #006b3c;
    }
    .warning-text {
        background: #fff8e1;
        border-left: 4px solid var(--cordoba-amarillo);
        color: #b38f00;
    }
    .error-text {
        background: #ffebee;
        border-left: 4px solid var(--cordoba-rojo);
        color: #c00000;
    }
    .stDataFrame {
        border: 1px solid var(--cordoba-gris-claro);
        border-radius: 8px;
        box-shadow: 0 1px 8px rgba(0,74,147,0.07);
    }
    .stSelectbox, .stMultiSelect {
        border-radius: 6px;
        box-shadow: 0 1px 4px rgba(0,74,147,0.04);
    }
    .gobierno-logo {
        text-align: center;
        margin-bottom: 1.5rem;
    }
    .gobierno-logo img {
        max-width: 220px;
        filter: drop-shadow(0 2px 8px #004a9322);
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
    .stTextInput>div>div>input {
        border: 1px solid var(--cordoba-gris-claro);
        border-radius: 6px;
        font-size: 1rem;
        padding: 0.5rem;
        transition: border-color 0.2s, box-shadow 0.2s;
    }
    .stTextInput>div>div>input:focus {
        border-color: var(--cordoba-azul);
        box-shadow: 0 0 0 0.2rem rgba(0, 74, 147, 0.15);
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
    /* Scrollbar personalizado */
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

def eliminar_equivalencia_con_auditoria(engine, id_equivalencia, usuario):
    """Elimina una equivalencia y registra la acción en la tabla de auditoría"""
    with engine.connect() as conn:
        conn.execute(
            text("CALL FN_ELIMINA_EQUIVALENCIAS_AUDITA(:id_equivalencia, :usuario)"),
            {"id_equivalencia": id_equivalencia, "usuario": usuario}
        )
        conn.commit()

def crear_equivalencia_con_auditoria(engine, id_curso, n_curso, id_certificacion, n_certificacion, observaciones, usuario):
    """Crea una equivalencia y registra la acción en la tabla de auditoría"""
    with engine.connect() as conn:
        result = conn.execute(
            text("CALL FN_INSERTA_EQUIVALENCIA_AUDITA (:id_curso, :n_curso, :id_certificacion, :n_certificacion, :observaciones, :usuario)"),
            {
                "id_curso": id_curso,
                "n_curso": n_curso,
                "id_certificacion": id_certificacion,
                "n_certificacion": n_certificacion,
                "observaciones": observaciones,
                "usuario": usuario
            }
        )
        conn.commit()
        return result.fetchone()

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
        
        # Cargar datos de certificaciones - incluir ID_CERTIFICACION
        query_certificaciones = """
            SELECT cl.ID_CERTIFICACION, cl.N_CERTIFICACION
            FROM T_CERTIF_X_LOCALIDAD cl
            GROUP BY cl.N_CERTIFICACION, cl.ID_CERTIFICACION
            ORDER BY cl.N_CERTIFICACION
        """
        
        df_historico = pd.read_sql(query_historico, engine)
        df_certificaciones = pd.read_sql(query_certificaciones, engine)
        
        # Procesar el campo N_CERTIFICACION para extraer el sector
        df_certificaciones['N_SECTOR'] = df_certificaciones['N_CERTIFICACION'].apply(
            lambda x: x.split(' - ')[1] if ' - ' in x else '')
        df_certificaciones['N_CERTIFICACION'] = df_certificaciones['N_CERTIFICACION'].apply(
            lambda x: x.split(' - ')[0] if ' - ' in x else x)
        
        # Eliminar duplicados después de procesar
        df_certificaciones = df_certificaciones.drop_duplicates(subset=['N_CERTIFICACION'])
        
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
            df_filtrado[['N_CURSO', 'N_SECTOR']],  # Eliminamos ID_CURSO
            use_container_width=True,
            hide_index=True,
            column_config={
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
        sector_options = ['Todos'] + sorted(df_certificaciones['N_SECTOR'].unique().tolist())
        sector_selected = st.selectbox("Sector", sector_options)
    
    # Aplicar filtros
    df_filtrado = df_certificaciones.copy()
    
    if sector_selected != 'Todos':
        df_filtrado = df_filtrado[df_filtrado['N_SECTOR'] == sector_selected]
        
    if busqueda_cert:
        df_filtrado = df_filtrado[df_filtrado['N_CERTIFICACION'].str.contains(busqueda_cert, case=False, na=False)]
    
    # Mostrar resultados
    st.caption(f"Mostrando {len(df_filtrado)} de {len(df_certificaciones)} certificaciones")
    
    if not df_filtrado.empty:
        st.dataframe(
            df_filtrado[['N_CERTIFICACION', 'N_SECTOR']],  # Solo mostramos estos campos, pero ID_CERTIFICACION sigue en el DataFrame
            use_container_width=True,
            hide_index=True,
            column_config={
                "N_CERTIFICACION": st.column_config.TextColumn("Nombre de Certificación"),
                "N_SECTOR": st.column_config.TextColumn("Sector")
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
        
        for curso in cursos_historicos:
            curso_info = df_historico[df_historico['N_CURSO'] == curso].iloc[0]
            st.markdown(f"""
            <div class="seleccion-card">
            <div class="card-title"><span class="card-title-icon">📚</span> Cursos seleccionados</div> 
            <p><strong>Nombre:</strong> {curso_info["N_CURSO"]}</p>
            <p><strong>Sector:</strong> {curso_info["N_SECTOR"]}</p>
            <hr style="margin: 0.5rem 0; border-color: #e0e0e0;">
            """, unsafe_allow_html=True)
            
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
            <p><strong>Sector:</strong> {cert_info["N_SECTOR"]}</p>
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
    
    # Crear un contenedor para mostrar resultados
    resultado_container = st.container()
    
    # En la parte donde se procesa el botón de crear equivalencia
    if st.button("Crear Equivalencia", key="crear_equivalencia", disabled=not (cursos_historicos and certificacion)):
        if not cursos_historicos or not certificacion:
            st.warning("Debe seleccionar al menos un curso histórico y una certificación.")
        else:
            try:
                # Obtener el ID de la certificación seleccionada
                cert_row = df_certificaciones[df_certificaciones['N_CERTIFICACION'] == certificacion]
                
                if cert_row.empty:
                    st.error(f"No se encontró el ID para la certificación {certificacion}")
                    # Mostrar información de depuración
                    st.write("Certificaciones disponibles:")
                    st.write(df_certificaciones[['N_CERTIFICACION', 'ID_CERTIFICACION']].head(10))
                    st.write(f"Certificación buscada: '{certificacion}'")
                    st.write("Primeros 5 caracteres de cada certificación:")
                    st.write(df_certificaciones['N_CERTIFICACION'].apply(lambda x: x[:5]).head(10))
                else:
                    id_certificacion = cert_row.iloc[0]['ID_CERTIFICACION']
                    
                    # Continuar con la creación de equivalencias
                    engine = get_database_connection()
                    if engine:
                        # Crear equivalencias para cada curso seleccionado
                        for curso in cursos_historicos:
                            curso_info = df_historico[df_historico['N_CURSO'] == curso].iloc[0]
                            id_curso = curso_info['ID_CURSO']
                            
                            # Llamar al procedimiento almacenado para crear la equivalencia
                            crear_equivalencia_con_auditoria(
                                engine, 
                                id_curso, 
                                curso, 
                                id_certificacion, 
                                certificacion, 
                                observacion, 
                                st.session_state.get('usuario', 'sistema')
                            )
                        
                        # Mostrar mensaje de éxito
                        st.markdown(f"""
                        <div class="success-message">
                            <div class="success-title">✅ Equivalencia creada con éxito</div>
                            <p>Se ha establecido la equivalencia entre {len(cursos_historicos)} curso(s) y la certificación "{certificacion}".</p>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        # Limpiar selecciones después de crear la equivalencia
                        st.rerun()
            except Exception as e:
                st.error(f"Error al crear la equivalencia: {str(e)}")
                logger.error(f"Error al crear equivalencia: {traceback.format_exc()}")
    elif not (cursos_historicos and certificacion):
        resultado_container.markdown("<div class='warning-text'>Debe seleccionar al menos un curso histórico y una certificación.</div>", unsafe_allow_html=True)

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
                                # Obtener el usuario actual (puedes adaptarlo según tu sistema de autenticación)
                                usuario_actual = "admin"  # Por defecto o desde sesión: st.session_state.get('usuario', 'sistema')
                                
                                # Llamar al procedimiento almacenado en lugar de hacer DELETE directo
                                eliminar_equivalencia_con_auditoria(engine, id_seleccionado, usuario_actual)
                                
                                st.markdown('<div class="success-text">Equivalencia eliminada correctamente</div>', unsafe_allow_html=True) 
                                st.rerun() 
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
        btn1 = st.button("📚 Explorar Cursos y Certificaciones actuales", use_container_width=True)
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