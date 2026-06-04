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
    .css-1r6slb0, .stAlert, .stInfo, .stSuccess, .stWarning, .stError {
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
        padding: 12px 24px;
        font-weight: bold;
        transition: all 0.3s ease;
        width: 100%;
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
        padding: 15px;
        background: rgba(0,0,0,0.85);
        color: white;
        font-size: 16px;
        font-weight: bold;
        z-index: 999;
        letter-spacing: 2px;
    }
    
    /* Sidebar */
    .css-1d391kg {
        background: rgba(255,255,255,0.95);
    }
    
    /* Títulos */
    h1, h2, h3 {
        color: #333;
    }
</style>
""", unsafe_allow_html=True)

# ============================================================
# FUNCIONES DE LECTURA DE DOCUMENTOS
# ============================================================
def leer_pdf(file):
    try:
        pdf_reader = PyPDF2.PdfReader(file)
        texto = ""
        for page in pdf_reader.pages:
            texto += page.extract_text()
        return texto
    except:
        return ""

def leer_docx(file):
    try:
        doc = docx.Document(file)
        texto = "\n".join([paragraph.text for paragraph in doc.paragraphs])
        return texto
    except:
        return ""

def leer_excel(file):
    try:
        df = pd.read_excel(file)
        return df.to_string()
    except:
        return ""

def leer_txt(file):
    try:
        texto = file.read().decode("utf-8")
        return texto
    except:
        return ""

def extraer_informacion_con_ia(texto, tipo_info):
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
        json_match = re.search(r'\{.*\}', respuesta, re.DOTALL)
        if json_match:
            return json.loads(json_match.group())
    except:
        pass
    return {"datos_encontrados": [], "confianza": 0, "sugerencias": []}

# ============================================================
# FUNCIÓN PARA OBTENER EMPRESA (segura)
# ============================================================
def get_empresa():
    try:
        emp = db.obtener_empresa()
        if emp is None or emp.empty:
            return None
        return emp
    except:
        return None

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
            border-radius: 30px;
            padding: 50px 40px;
            text-align: center;
            box-shadow: 0 25px 50px rgba(0,0,0,0.3);
        '>
            <h1 style='color: #667eea; font-size: 64px; margin: 0;'>🔄</h1>
            <h1 style='color: #333; margin: 10px 0 5px 0;'>SG-SST PHVA</h1>
            <p style='color: #666; font-size: 16px;'>Sistema de Gestión de Seguridad y Salud</p>
            <p style='color: #999; font-size: 14px; margin-top: 5px;'>Nivel DIOS - IA Protagonista</p>
        </div>
        """, unsafe_allow_html=True)
        
        with st.form("login_form"):
            user = st.text_input("👤 Usuario", placeholder="admin", key="login_user")
            pwd = st.text_input("🔒 Contraseña", type="password", placeholder="••••••", key="login_pwd")
            
            if st.form_submit_button("🚀 ACCEDER AL SISTEMA", use_container_width=True):
                if user == "admin" and pwd == "sst2024":
                    st.session_state.authenticated = True
                    st.rerun()
                else:
                    st.error("❌ Credenciales incorrectas. Use: admin / sst2024")
        
        st.markdown("""
        <div style='text-align: center; margin-top: 40px;'>
            <hr style='border-color: rgba(255,255,255,0.3);'>
            <p style='color: white; font-size: 18px; font-weight: bold; margin: 20px 0 5px 0;'>
                DESARROLLADO POR
            </p>
            <p style='color: white; font-size: 32px; font-weight: bold; letter-spacing: 3px; margin: 0;'>
                JAN BENITEZ
            </p>
            <p style='color: rgba(255,255,255,0.7); font-size: 12px; margin-top: 10px;'>
                © 2024 - Todos los derechos reservados
            </p>
        </div>
        """, unsafe_allow_html=True)
    
    st.stop()

# ============================================================
# OBTENER EMPRESA DE FORMA SEGURA
# ============================================================
empresa = get_empresa()

# Actualizar checklist
st.session_state.checklist["diagnostico"] = empresa is not None
st.session_state.checklist["peligros"] = len(db.obtener_peligros()) > 0
st.session_state.checklist["trabajadores"] = len(db.obtener_trabajadores()) > 0
st.session_state.checklist["acciones"] = len(db.obtener_acciones()) > 0
st.session_state.checklist["incidentes"] = len(db.obtener_incidentes()) > 0

# ============================================================
# SIDEBAR CON PROGRESO
# ============================================================
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/2917/2917995.png", width=80)
    
    if empresa is not None:
        try:
            nombre_emp = empresa.get('nombre', 'Empresa') if isinstance(empresa, dict) else empresa['nombre'].iloc[0] if hasattr(empresa, 'iloc') else 'Empresa'
            trabajadores_emp = empresa.get('trabajadores', 0) if isinstance(empresa, dict) else empresa['trabajadores'].iloc[0] if hasattr(empresa, 'iloc') else 0
            st.markdown(f"**🏢 {nombre_emp[:30]}**")
            st.caption(f"📊 {trabajadores_emp} trabajadores")
        except:
            st.markdown("**🏢 Empresa**")
    else:
        st.markdown("**🏢 Sin empresa registrada**")
    
    st.markdown("---")
    
    # CHECKLIST DE PROGRESO
    st.markdown("### 📋 Progreso")
    
    check_items = {
        "diagnostico": "🤖 Diagnóstico IA",
        "peligros": "⚠️ Peligros",
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
    
    progreso_total = int(completados / len(check_items) * 100)
    st.progress(progreso_total / 100)
    st.caption(f"📊 {progreso_total}% Completado")
    
    st.markdown("---")
    
    menu = st.radio("📋 MENU", [
        "🏠 Dashboard",
        "🤖 Diagnóstico IA",
        "⚠️ Peligros",
        "📊 Riesgos",
        "✅ Plan de Acción",
        "👥 Trabajadores",
        "📝 Incidentes",
        "💬 Chat Experto"
    ])
    
    st.markdown("---")
    if st.button("🚪 Cerrar Sesión", use_container_width=True):
        st.session_state.authenticated = False
        st.rerun()

# ============================================================
# DASHBOARD
# ============================================================
if menu == "🏠 Dashboard":
    st.title("📊 Dashboard SST")
    st.markdown("---")
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("🏢 Empresa", "Registrada" if empresa else "Pendiente")
    with col2:
        st.metric("⚠️ Peligros", len(db.obtener_peligros()))
    with col3:
        acc = db.obtener_acciones()
        completadas = len(acc[acc['estado'] == 'Completada']) if not acc.empty else 0
        st.metric("✅ Acciones", f"{completadas}/{len(acc)}")
    with col4:
        st.metric("📈 Progreso", f"{progreso_total}%")
    
    st.markdown("---")
    
    # Mostrar qué falta
    st.subheader("📋 Módulos Pendientes")
    faltantes = [label for key, label in check_items.items() if not st.session_state.checklist[key]]
    if faltantes:
        for item in faltantes:
            st.warning(f"⬜ {item}")
    else:
        st.success("🎉 ¡Felicidades! Sistema completado al 100%")
    
    # Mostrar diagnóstico si existe
    if empresa is not None:
        try:
            diagnostico = empresa.get('diagnostico_ia', '') if isinstance(empresa, dict) else empresa['diagnostico_ia'].iloc[0] if hasattr(empresa, 'iloc') and 'diagnostico_ia' in empresa.columns else ''
            if diagnostico:
                with st.expander("📋 Ver Diagnóstico IA Generado"):
                    st.markdown(diagnostico)
        except:
            pass

# ============================================================
# DIAGNÓSTICO IA
# ============================================================
elif menu == "🤖 Diagnóstico IA":
    st.title("🤖 Diagnóstico Inteligente")
    st.markdown("---")
    
    tab1, tab2 = st.tabs(["📝 Datos básicos", "📄 Carga documentos"])
    
    with tab1:
        with st.form("diagnostico_form"):
            nombre_empresa = st.text_input("Nombre de la empresa *", placeholder="Mi Empresa S.A.S.")
            trabajadores = st.number_input("Número de trabajadores *", min_value=1, value=10)
            arl = st.selectbox("ARL *", ["Positiva", "Sura", "Colpatria", "Bolivar"])
            
            if st.form_submit_button("🚀 GENERAR DIAGNÓSTICO", use_container_width=True):
                if nombre_empresa:
                    with st.spinner("🤖 IA generando diagnóstico..."):
                        prompt = f"Genera diagnóstico SST corto para {nombre_empresa} con {trabajadores} trabajadores, ARL {arl}. Máximo 300 palabras."
                        respuesta = ia.call_best(prompt)
                        
                        if respuesta:
                            db.guardar_empresa("", nombre_empresa, trabajadores, arl, "", respuesta)
                            st.success("✅ Diagnóstico guardado")
                            st.balloons()
                            st.rerun()
    
    with tab2:
        st.info("📄 Sube documentos de tu empresa y la IA extraerá la información automáticamente")
        archivo = st.file_uploader("Documento (PDF, Word, Excel, TXT)", 
                                   type=['pdf', 'docx', 'xlsx', 'xls', 'txt'])
        
        if archivo:
            with st.spinner("🤖 IA procesando documento..."):
                if archivo.type == "application/pdf":
                    texto = leer_pdf(archivo)
                elif archivo.type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
                    texto = leer_docx(archivo)
                elif archivo.type in ["application/vnd.ms-excel", "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"]:
                    texto = leer_excel(archivo)
                else:
                    texto = leer_txt(archivo)
                
                if texto:
                    st.success(f"✅ Documento leído - {len(texto)} caracteres")
                    
                    # Extraer info con IA
                    info = extraer_informacion_con_ia(texto, "nombre de empresa")
                    
                    if info.get('datos_encontrados'):
                        st.json(info)
                        
                        nombre = info['datos_encontrados'][0] if info['datos_encontrados'] else "Empresa"
                        db.guardar_empresa("", nombre, 10, "Positiva", "", texto[:2000])
                        st.success("✅ Información extraída y guardada")
                        st.rerun()
                    else:
                        st.warning("No se pudo extraer información automática. Usa el modo manual.")
                else:
                    st.error("No se pudo leer el documento")

# ============================================================
# PELIGROS
# ============================================================
elif menu == "⚠️ Peligros":
    st.title("⚠️ Gestión de Peligros")
    
    if empresa is None:
        st.warning("⚠️ Primero realiza el Diagnóstico IA")
    else:
        tab1, tab2 = st.tabs(["📋 Lista", "➕ Agregar"])
        
        with tab1:
            df = db.obtener_peligros()
            if not df.empty:
                st.dataframe(df[['id', 'tipo', 'descripcion', 'nivel_riesgo']], use_container_width=True)
                
                with st.expander("🗑️ Eliminar"):
                    id_elim = st.number_input("ID", min_value=1, step=1)
                    if st.button("Eliminar"):
                        db.eliminar_peligro(id_elim)
                        st.rerun()
            else:
                st.info("📭 No hay peligros")
        
        with tab2:
            with st.form("nuevo_peligro"):
                col1, col2 = st.columns(2)
                with col1:
                    tipo = st.selectbox("Tipo", ["Físico", "Químico", "Biológico", "Ergonómico", "Psicosocial", "Seguridad"])
                    desc = st.text_area("Descripción")
                with col2:
                    prob = st.slider("Probabilidad", 1, 4, 2)
                    sev = st.slider("Severidad", 1, 3, 2)
                    nivel = db.calcular_nivel(prob, sev)
                    st.info(f"📊 Nivel: {nivel}")
                
                if st.form_submit_button("💾 Guardar"):
                    if desc:
                        db.guardar_peligro(1, tipo, desc, "", prob, sev, 0)
                        st.success("Guardado")
                        st.rerun()

# ============================================================
# RIESGOS
# ============================================================
elif menu == "📊 Riesgos":
    st.title("📊 Evaluación de Riesgos")
    
    df = db.obtener_peligros()
    if not df.empty:
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Total Peligros", len(df))
            nivel1 = len(df[df['nivel_riesgo'] == 'I'])
            st.metric("🔴 Nivel I", nivel1)
        with col2:
            st.bar_chart(df['nivel_riesgo'].value_counts())
        
        st.markdown("---")
        st.subheader("Matriz de Riesgos")
        st.dataframe(df[['tipo', 'descripcion', 'nivel_riesgo']], use_container_width=True)
    else:
        st.info("📭 Registra peligros primero")

# ============================================================
# PLAN DE ACCIÓN
# ============================================================
elif menu == "✅ Plan de Acción":
    st.title("✅ Plan de Acción")
    
    tab1, tab2 = st.tabs(["📋 Seguimiento", "➕ Nueva"])
    
    with tab1:
        df = db.obtener_acciones()
        if not df.empty:
            for _, row in df.iterrows():
                col1, col2 = st.columns([3, 1])
                with col1:
                    st.markdown(f"**📌 {row['descripcion']}**")
                    st.caption(f"👤 {row['responsable']} | 📅 {row['fecha_limite']}")
                with col2:
                    nuevo = st.selectbox("Estado", ["Pendiente", "En progreso", "Completada"], 
                                        index=["Pendiente", "En progreso", "Completada"].index(row['estado']),
                                        key=f"act_{row['id']}")
                    if nuevo != row['estado']:
                        db.actualizar_estado_accion(row['id'], nuevo)
                        st.rerun()
                st.markdown("---")
        else:
            st.info("📭 No hay acciones")
    
    with tab2:
        with st.form("nueva_accion"):
            desc = st.text_area("Descripción")
            responsable = st.text_input("Responsable")
            fecha = st.date_input("Fecha límite", datetime.now())
            prioridad = st.selectbox("Prioridad", ["Alta", "Media", "Baja"])
            
            if st.form_submit_button("Guardar"):
                if desc and responsable:
                    db.guardar_accion(1, 0, desc, responsable, fecha, prioridad, 0)
                    st.success("Guardado")
                    st.rerun()

# ============================================================
# TRABAJADORES
# ============================================================
elif menu == "👥 Trabajadores":
    st.title("👥 Trabajadores")
    
    tab1, tab2 = st.tabs(["📋 Lista", "➕ Nuevo"])
    
    with tab1:
        df = db.obtener_trabajadores()
        if not df.empty:
            st.dataframe(df[['cedula', 'nombre', 'cargo', 'area']], use_container_width=True)
        else:
            st.info("📭 No hay trabajadores")
    
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
                if cedula and nombre:
                    db.guardar_trabajador(1, cedula, nombre, "", cargo, area)
                    st.success("Guardado")
                    st.rerun()

# ============================================================
# INCIDENTES
# ============================================================
elif menu == "📝 Incidentes":
    st.title("📝 Incidentes")
    
    with st.form("nuevo_incidente"):
        tipo = st.selectbox("Tipo", ["Accidente", "Incidente", "Enfermedad Laboral"])
        desc = st.text_area("Descripción")
        fecha = st.date_input("Fecha", datetime.now())
        gravedad = st.selectbox("Gravedad", ["Leve", "Moderada", "Grave"])
        
        if st.form_submit_button("Registrar"):
            if desc:
                db.guardar_incidente(1, tipo, desc, fecha, "", gravedad)
                st.success("Registrado")
                st.rerun()
    
    st.markdown("---")
    df = db.obtener_incidentes()
    if not df.empty:
        st.dataframe(df)

# ============================================================
# CHAT EXPERTO
# ============================================================
elif menu == "💬 Chat Experto":
    st.title("💬 Chat Experto SST")
    
    if "chat_msgs" not in st.session_state:
        st.session_state.chat_msgs = []
    
    for msg in st.session_state.chat_msgs:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])
    
    if prompt := st.chat_input("Pregunta sobre SST..."):
        st.session_state.chat_msgs.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
        
        with st.spinner("🤖 Pensando..."):
            respuesta = ia.call_best(prompt)
        
        with st.chat_message("assistant"):
            st.markdown(respuesta or "Error - Verifica API keys")
        st.session_state.chat_msgs.append({"role": "assistant", "content": respuesta or "Error"})

# ============================================================
# FOOTER
# ============================================================
st.markdown("""
<div class='footer'>
    🔄 SG-SST PHVA | DESARROLLADO POR JAN BENITEZ | IA Protagonista | Nivel DIOS
</div>
""", unsafe_allow_html=True)
