import streamlit as st
import sys
import pandas as pd
import PyPDF2
import docx
from datetime import datetime, timedelta
from pathlib import Path
import json
import re

sys.path.insert(0, str(Path(__file__).parent))

st.set_page_config(page_title="SG-SST PHVA", page_icon="🔄", layout="wide")

from core.db import db
from core.ia_engine import ia
from core.logger import Logger

logger = Logger("main")

# ============================================================
# ESTILOS CSS MODERNOS
# ============================================================
st.markdown("""
<style>
    /* Fondo moderno */
    .stApp {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    }
    
    /* Tarjetas modernas */
    .css-1r6slb0 {
        background: rgba(255, 255, 255, 0.95);
        border-radius: 20px;
        padding: 20px;
        box-shadow: 0 8px 32px rgba(0,0,0,0.1);
    }
    
    /* Botones modernos */
    .stButton > button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border-radius: 10px;
        border: none;
        padding: 10px 20px;
        font-weight: bold;
        transition: all 0.3s ease;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 5px 15px rgba(0,0,0,0.2);
    }
    
    /* Footer */
    .footer {
        position: fixed;
        bottom: 0;
        left: 0;
        right: 0;
        text-align: center;
        padding: 10px;
        background: rgba(0,0,0,0.8);
        color: white;
        font-size: 14px;
        z-index: 999;
    }
</style>
""", unsafe_allow_html=True)

# ============================================================
# FUNCIONES DE LECTURA DE DOCUMENTOS
# ============================================================
def leer_pdf(file):
    """Extrae texto de PDF"""
    try:
        pdf_reader = PyPDF2.PdfReader(file)
        texto = ""
        for page in pdf_reader.pages:
            texto += page.extract_text()
        return texto
    except:
        return ""

def leer_docx(file):
    """Extrae texto de Word"""
    try:
        doc = docx.Document(file)
        texto = "\n".join([paragraph.text for paragraph in doc.paragraphs])
        return texto
    except:
        return ""

def leer_excel(file):
    """Lee archivo Excel"""
    try:
        df = pd.read_excel(file)
        return df.to_string()
    except:
        return ""

def leer_txt(file):
    """Lee archivo TXT"""
    try:
        texto = file.read().decode("utf-8")
        return texto
    except:
        return ""

def extraer_informacion_con_ia(texto, tipo_info):
    """IA extrae información específica del documento"""
    prompt = f"""
    Extrae del siguiente texto la información de {tipo_info}:
    
    TEXTO:
    {texto[:3000]}
    
    Devuelve SOLO JSON con:
    - datos_encontrados: lista de items encontrados
    - confianza: porcentaje de confianza
    - sugerencias: campos que faltan
    
    Formato JSON:
    {{"datos_encontrados": [], "confianza": 0, "sugerencias": []}}
    """
    
    respuesta = ia.call_best(prompt)
    try:
        # Intentar extraer JSON
        json_match = re.search(r'\{.*\}', respuesta, re.DOTALL)
        if json_match:
            return json.loads(json_match.group())
    except:
        pass
    return {"datos_encontrados": [], "confianza": 0, "sugerencias": []}

# ============================================================
# INICIALIZAR SESIÓN
# ============================================================
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
if "empresa_id" not in st.session_state:
    st.session_state.empresa_id = 1
if "checklist" not in st.session_state:
    st.session_state.checklist = {
        "diagnostico": False,
        "peligros": False,
        "trabajadores": False,
        "acciones": False,
        "incidentes": False
    }

# ============================================================
# LOGIN MODERNO
# ============================================================
if not st.session_state.authenticated:
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("""
        <div style='
            background: rgba(255,255,255,0.95);
            border-radius: 20px;
            padding: 40px;
            text-align: center;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
        '>
            <h1 style='color: #667eea; font-size: 48px;'>🔄</h1>
            <h1 style='color: #333;'>SG-SST PHVA</h1>
            <p style='color: #666;'>Sistema de Gestión de Seguridad y Salud</p>
            <p style='color: #999;'>Nivel DIOS - IA Protagonista</p>
        </div>
        """, unsafe_allow_html=True)
        
        with st.form("login_form"):
            user = st.text_input("Usuario", placeholder="admin", key="login_user")
            pwd = st.text_input("Contraseña", type="password", placeholder="••••••", key="login_pwd")
            
            if st.form_submit_button("🚀 ACCEDER", use_container_width=True):
                if user == "admin" and pwd == "sst2024":
                    st.session_state.authenticated = True
                    st.rerun()
                else:
                    st.error("❌ Usuario: admin / Contraseña: sst2024")
        
        # Footer en login
        st.markdown("""
        <div style='text-align: center; margin-top: 30px;'>
            <p style='color: white; font-size: 16px; font-weight: bold;'>
                DESARROLLADO POR<br>
                <span style='font-size: 24px; letter-spacing: 2px;'>JAN BENITEZ</span>
            </p>
        </div>
        """, unsafe_allow_html=True)
    
    st.stop()

# ============================================================
# SIDEBAR CON PROGRESO
# ============================================================
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/2917/2917995.png", width=80)
    
    empresa = db.obtener_empresa()
    if empresa:
        st.markdown(f"**🏢 {empresa.get('nombre', 'Empresa')[:30]}**")
        st.caption(f"📊 {empresa.get('trabajadores', 0)} trabajadores")
    
    st.markdown("---")
    
    # CHECKLIST DE PROGRESO
    st.markdown("### 📋 Progreso del Sistema")
    
    check_items = {
        "diagnostico": "🤖 Diagnóstico IA",
        "peligros": "⚠️ Peligros (Fase 2)",
        "trabajadores": "👥 Trabajadores",
        "acciones": "✅ Plan de Acción",
        "incidentes": "📝 Incidentes"
    }
    
    completados = 0
    for key, label in check_items.items():
        if st.session_state.checklist[key]:
            st.markdown(f"✅ {label}")
            completados += 1
        else:
            st.markdown(f"⬜ {label}")
    
    st.progress(completados / len(check_items))
    st.caption(f"Completado: {completados}/{len(check_items)} módulos")
    
    st.markdown("---")
    
    menu = st.radio("📋 MENU", [
        "🏠 Dashboard",
        "🤖 Diagnóstico IA",
        "⚠️ Peligros (Fase 2)",
        "📊 Riesgos (Fase 3)",
        "✅ Acciones (Fase 4)",
        "👥 Trabajadores",
        "📝 Incidentes",
        "💬 Chat Experto"
    ])
    
    st.markdown("---")
    if st.button("🚪 Salir"):
        st.session_state.authenticated = False
        st.rerun()

# ============================================================
# OBTENER DATOS
# ============================================================
empresa = db.obtener_empresa()

# Actualizar checklist
st.session_state.checklist["diagnostico"] = empresa is not None
st.session_state.checklist["peligros"] = len(db.obtener_peligros()) > 0
st.session_state.checklist["trabajadores"] = len(db.obtener_trabajadores()) > 0
st.session_state.checklist["acciones"] = len(db.obtener_acciones()) > 0
st.session_state.checklist["incidentes"] = len(db.obtener_incidentes()) > 0

# ============================================================
# DASHBOARD
# ============================================================
if menu == "🏠 Dashboard":
    st.title("📊 Dashboard SST")
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("🏢 Estado", "Configurado" if empresa else "Pendiente")
    with col2:
        st.metric("⚠️ Peligros", len(db.obtener_peligros()))
    with col3:
        st.metric("✅ Acciones", len(db.obtener_acciones()))
    with col4:
        progreso = sum(st.session_state.checklist.values()) / len(st.session_state.checklist) * 100
        st.metric("📈 Progreso", f"{progreso:.0f}%")
    
    st.markdown("---")
    
    # Mostrar qué falta
    st.subheader("📋 Pendientes por completar")
    faltantes = [label for key, label in check_items.items() if not st.session_state.checklist[key]]
    if faltantes:
        for item in faltantes:
            st.warning(f"⬜ {item}")
    else:
        st.success("🎉 ¡Sistema completado al 100%!")
    
    if empresa and empresa.get('diagnostico_ia'):
        with st.expander("📋 Ver Diagnóstico IA"):
            st.markdown(empresa['diagnostico_ia'])

# ============================================================
# DIAGNÓSTICO IA - CON CARGA DE DOCUMENTOS
# ============================================================
elif menu == "🤖 Diagnóstico IA":
    st.title("🤖 Diagnóstico Inteligente con IA")
    st.markdown("---")
    
    tab1, tab2 = st.tabs(["📝 Datos básicos", "📄 Carga masiva de documentos"])
    
    with tab1:
        with st.form("diagnostico_form"):
            identificador = st.text_input("Nombre de la empresa *", placeholder="Mi Empresa S.A.S.")
            trabajadores = st.number_input("Número de trabajadores *", min_value=1, value=10)
            arl = st.selectbox("ARL *", ["Positiva", "Sura", "Colpatria", "Bolivar"])
            
            if st.form_submit_button("🚀 Generar Diagnóstico", use_container_width=True):
                if identificador:
                    with st.spinner("🤖 IA generando diagnóstico..."):
                        prompt = f"Genera diagnóstico SST para {identificador} con {trabajadores} trabajadores, ARL {arl}. Resumen ejecutivo corto de máximo 500 palabras."
                        respuesta = ia.call_best(prompt)
                        
                        if respuesta:
                            db.guardar_empresa("", identificador, trabajadores, arl, "", respuesta)
                            st.success("✅ Diagnóstico guardado")
                            st.rerun()
    
    with tab2:
        st.subheader("📄 Carga documentos de tu empresa")
        st.info("La IA leerá los documentos y extraerá automáticamente la información")
        
        archivo = st.file_uploader("Sube documento (PDF, Word, Excel, TXT)", 
                                   type=['pdf', 'docx', 'xlsx', 'xls', 'txt'])
        
        if archivo:
            with st.spinner("🤖 IA leyendo documento..."):
                # Leer según tipo
                if archivo.type == "application/pdf":
                    texto = leer_pdf(archivo)
                elif archivo.type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
                    texto = leer_docx(archivo)
                elif archivo.type in ["application/vnd.ms-excel", "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"]:
                    texto = leer_excel(archivo)
                else:
                    texto = leer_txt(archivo)
                
                if texto:
                    # Extraer info con IA
                    info_empresa = extraer_informacion_con_ia(texto, "nombre de empresa, número de trabajadores, ARL")
                    st.success(f"✅ Documento procesado - Confianza: {info_empresa.get('confianza', 0)}%")
                    
                    if info_empresa.get('datos_encontrados'):
                        st.json(info_empresa['datos_encontrados'])
                        
                        # Guardar automáticamente
                        nombre = info_empresa['datos_encontrados'][0] if info_empresa['datos_encontrados'] else "Empresa"
                        db.guardar_empresa("", nombre, 10, "Positiva", "", texto[:2000])
                        st.rerun()
                else:
                    st.error("No se pudo leer el documento")

# ============================================================
# PELIGROS - CARGA MASIVA
# ============================================================
elif menu == "⚠️ Peligros (Fase 2)":
    st.title("⚠️ FASE 2: Identificar Peligros")
    
    if empresa is None:
        st.warning("Primero realiza el Diagnóstico IA")
    else:
        tab1, tab2, tab3 = st.tabs(["📋 Lista", "➕ Manual", "📤 Carga Masiva"])
        
        with tab1:
            df = db.obtener_peligros()
            if not df.empty:
                st.dataframe(df, use_container_width=True)
        
        with tab2:
            with st.form("nuevo_peligro"):
                col1, col2 = st.columns(2)
                with col1:
                    tipo = st.selectbox("Tipo", ["Físico", "Químico", "Biológico", "Ergonómico", "Psicosocial", "Seguridad"])
                    descripcion = st.text_area("Descripción")
                with col2:
                    prob = st.slider("Probabilidad", 1, 4, 2)
                    sev = st.slider("Severidad", 1, 3, 2)
                    nivel = db.calcular_nivel(prob, sev)
                    st.info(f"Nivel: {nivel}")
                
                if st.form_submit_button("Guardar"):
                    db.guardar_peligro(1, tipo, descripcion, "", prob, sev, 0)
                    st.success("Guardado")
                    st.rerun()
        
        with tab3:
            st.subheader("Carga masiva de peligros")
            archivo = st.file_uploader("Excel con peligros", type=['xlsx', 'xls'], key="peligros_file")
            if archivo:
                df_carga = pd.read_excel(archivo)
                st.dataframe(df_carga.head())
                if st.button("Cargar {len(df_carga)} peligros"):
                    for _, row in df_carga.iterrows():
                        db.guardar_peligro(1, row.get('tipo', 'Seguridad'), row.get('descripcion', ''), 
                                         row.get('ubicacion', ''), row.get('probabilidad', 2), 
                                         row.get('severidad', 2), 0)
                    st.success("Carga completada")
                    st.rerun()

# ============================================================
# TRABAJADORES - CARGA MASIVA
# ============================================================
elif menu == "👥 Trabajadores":
    st.title("👥 Gestión de Trabajadores")
    
    tab1, tab2, tab3 = st.tabs(["📋 Lista", "➕ Manual", "📤 Carga Masiva"])
    
    with tab1:
        df = db.obtener_trabajadores()
        if not df.empty:
            st.dataframe(df, use_container_width=True)
    
    with tab2:
        with st.form("nuevo_trabajador"):
            col1, col2 = st.columns(2)
            with col1:
                cedula = st.text_input("Cédula")
                nombre = st.text_input("Nombre")
            with col2:
                cargo = st.text_input("Cargo")
                area = st.text_input("Área")
            if st.form_submit_button("Guardar"):
                db.guardar_trabajador(1, cedula, nombre, "", cargo, area)
                st.success("Guardado")
                st.rerun()
    
    with tab3:
        st.subheader("Carga masiva de trabajadores")
        archivo = st.file_uploader("Excel con trabajadores", type=['xlsx', 'xls'], key="trabajadores_file")
        if archivo:
            df_carga = pd.read_excel(archivo)
            st.dataframe(df_carga.head())
            if st.button(f"Cargar {len(df_carga)} trabajadores"):
                for _, row in df_carga.iterrows():
                    db.guardar_trabajador(1, str(row.get('cedula', '')), row.get('nombre', ''), 
                                         row.get('email', ''), row.get('cargo', ''), row.get('area', ''))
                st.success("Carga completada")
                st.rerun()

# ============================================================
# RIESGOS (Fase 3)
# ============================================================
elif menu == "📊 Riesgos (Fase 3)":
    st.title("📊 FASE 3: Evaluación de Riesgos")
    
    peligros_df = db.obtener_peligros()
    if not peligros_df.empty:
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Total", len(peligros_df))
            nivel1 = len(peligros_df[peligros_df['nivel_riesgo'] == 'I'])
            st.metric("Nivel I", nivel1)
        with col2:
            st.bar_chart(peligros_df['nivel_riesgo'].value_counts())
    else:
        st.info("Registra peligros primero")

# ============================================================
# ACCIONES (Fase 4)
# ============================================================
elif menu == "✅ Acciones (Fase 4)":
    st.title("✅ FASE 4: Plan de Acción")
    
    tab1, tab2 = st.tabs(["📋 Seguimiento", "➕ Nueva"])
    
    with tab1:
        df = db.obtener_acciones()
        if not df.empty:
            for _, row in df.iterrows():
                col1, col2 = st.columns([3,1])
                with col1:
                    st.markdown(f"**{row['descripcion']}**")
                    st.caption(f"Responsable: {row['responsable']}")
                with col2:
                    nuevo = st.selectbox("Estado", ["Pendiente", "En progreso", "Completada"], 
                                        index=["Pendiente", "En progreso", "Completada"].index(row['estado']),
                                        key=f"acc_{row['id']}")
                    if nuevo != row['estado']:
                        db.actualizar_estado_accion(row['id'], nuevo)
                        st.rerun()
                st.markdown("---")
    
    with tab2:
        with st.form("nueva"):
            desc = st.text_area("Descripción")
            responsable = st.text_input("Responsable")
            if st.form_submit_button("Guardar"):
                db.guardar_accion(1, 0, desc, responsable, datetime.now().strftime("%Y-%m-%d"), "Media", 0)
                st.success("Guardado")
                st.rerun()

# ============================================================
# INCIDENTES
# ============================================================
elif menu == "📝 Incidentes":
    st.title("📝 Incidentes")
    
    with st.form("nuevo"):
        desc = st.text_area("Descripción")
        fecha = st.date_input("Fecha", datetime.now())
        if st.form_submit_button("Registrar"):
            db.guardar_incidente(1, "Incidente", desc, fecha, "", "Leve")
            st.success("Registrado")
            st.rerun()
    
    st.markdown("---")
    df = db.obtener_incidentes()
    if not df.empty:
        st.dataframe(df)

# ============================================================
# CHAT IA
# ============================================================
elif menu == "💬 Chat Experto":
    st.title("💬 Chat Experto SST")
    
    if "msgs" not in st.session_state:
        st.session_state.msgs = []
    
    for msg in st.session_state.msgs:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])
    
    if prompt := st.chat_input("Pregunta..."):
        st.session_state.msgs.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
        
        respuesta = ia.call_best(prompt)
        with st.chat_message("assistant"):
            st.markdown(respuesta or "Error")
        st.session_state.msgs.append({"role": "assistant", "content": respuesta or "Error"})

# ============================================================
# FOOTER GLOBAL
# ============================================================
st.markdown("""
<div class='footer'>
    <strong>DESARROLLADO POR JAN BENITEZ</strong> | SG-SST PHVA Nivel DIOS | IA Protagonista
</div>
""", unsafe_allow_html=True)
