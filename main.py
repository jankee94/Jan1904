import streamlit as st
import pandas as pd
from datetime import datetime
import io
import requests
import json

st.set_page_config(page_title="SG-SST PHVA", page_icon="🔄", layout="wide")

# ========== CSS ==========
st.markdown('''
<style>
    .stApp { background: linear-gradient(135deg, #0f0c29 0%, #302b63 50%, #24243e 100%); }
    header[data-testid="stHeader"] { display: none; }
    footer { display: none !important; }
    .main-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 20px;
        border-radius: 15px;
        margin-bottom: 20px;
    }
    .main-header h1 { color: white; margin: 0; font-size: 1.8rem; }
</style>
''', unsafe_allow_html=True)

# ========== FUNCIONES ==========
def exportar_excel(data, nombre):
    df = pd.DataFrame(data)
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, sheet_name=nombre, index=False)
    return output.getvalue()

# ========== INICIALIZACIÓN ==========
def init_session():
    if "auth" not in st.session_state:
        st.session_state.auth = False
    if "username" not in st.session_state:
        st.session_state.username = None
    if "chat_messages" not in st.session_state:
        st.session_state.chat_messages = []
    
    if "empresa" not in st.session_state:
        st.session_state.empresa = {"nombre": "Constructora Segura SAS", "nit": "901.234.567-8"}
    
    if "peligros" not in st.session_state:
        st.session_state.peligros = [
            {"id": 1, "tipo": "Físico", "descripcion": "Ruido excesivo", "probabilidad": 4, "severidad": 3, "nivel": "I"},
            {"id": 2, "tipo": "Ergonómico", "descripcion": "Posturas forzadas", "probabilidad": 3, "severidad": 2, "nivel": "II"},
        ]
    
    if "acciones" not in st.session_state:
        st.session_state.acciones = [
            {"id": 1, "descripcion": "Implementar barreras acústicas", "responsable": "SST", "fecha_limite": "2024-12-15", "estado": "Pendiente"},
        ]
    
    if "trabajadores" not in st.session_state:
        st.session_state.trabajadores = [
            {"id": 1, "nombre": "Carlos López", "cedula": "12345678", "cargo": "Operario"},
            {"id": 2, "nombre": "María Gómez", "cedula": "87654321", "cargo": "Supervisor"},
        ]
    
    if "incidentes" not in st.session_state:
        st.session_state.incidentes = [
            {"id": 1, "descripcion": "Caída desde andamio", "fecha": "2024-10-15", "gravedad": "Grave"},
        ]
    
    if "capacitaciones" not in st.session_state:
        st.session_state.capacitaciones = []
    if "inspecciones" not in st.session_state:
        st.session_state.inspecciones = []
    if "emergencias" not in st.session_state:
        st.session_state.emergencias = {"brigadistas": [], "equipos": [], "alertas": []}
    if "documentos" not in st.session_state:
        st.session_state.documentos = []
    if "auditorias" not in st.session_state:
        st.session_state.auditorias = []

init_session()

# ========== LOGIN ==========
if not st.session_state.auth:
    col1, col2, col3 = st.columns([1, 1.5, 1])
    with col2:
        st.markdown('''
        <div style="background: rgba(20,20,40,0.8); backdrop-filter: blur(14px); border-radius: 28px; padding: 40px; text-align:center">
            <img src="https://cdn-icons-png.flaticon.com/512/2917/2917995.png" width="70">
            <h1 style="color:white;">SG-SST PHVA</h1>
            <p style="color:rgba(255,255,255,0.6)">Sistema de Gestión en Seguridad y Salud en el Trabajo</p>
        </div>
        ''', unsafe_allow_html=True)
        
        with st.form("login_form"):
            username = st.text_input("Usuario", placeholder="admin")
            password = st.text_input("Contraseña", type="password", placeholder="admin123")
            if st.form_submit_button("🚀 INGRESAR", use_container_width=True):
                if username == "admin" and password == "admin123":
                    st.session_state.auth = True
                    st.session_state.username = "Administrador"
                    st.rerun()
                else:
                    st.error("❌ Usuario o contraseña incorrectos")
        
        st.markdown('<p style="text-align:center; font-size:11px; color:gray">SG-SST PHVA | JAN BENITEZ</p>', unsafe_allow_html=True)
    st.stop()

# ========== SIDEBAR ==========
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/2917/2917995.png", width=50)
    st.markdown(f"### {st.session_state.username}")
    st.markdown("---")
    
    menu = st.radio("📋 MÓDULOS", [
        "Dashboard", "Empresa", "Peligros", "Plan de Acción",
        "Trabajadores", "Incidentes", "Matriz Legal", "Auditorías",
        "Capacitaciones", "Inspecciones", "Emergencias", "Documentos",
        "Indicadores", "Chat IA"
    ])
    
    st.markdown("---")
    if st.button("🚪 Cerrar Sesión", use_container_width=True):
        st.session_state.auth = False
        st.rerun()

# ========== FUNCIONES DE RENDER ==========
def render_dashboard():
    st.markdown(f'<div class="main-header"><h1>📊 Dashboard SST</h1><p>{st.session_state.empresa["nombre"]}</p></div>', unsafe_allow_html=True)
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("⚠️ Peligros", len(st.session_state.peligros))
    with col2:
        st.metric("✅ Acciones", len(st.session_state.acciones))
    with col3:
        st.metric("👥 Trabajadores", len(st.session_state.trabajadores))
    with col4:
        st.metric("📝 Incidentes", len(st.session_state.incidentes))

def render_modulo(titulo, datos, session_key):
    st.markdown(f'<div class="main-header"><h1>{titulo}</h1></div>', unsafe_allow_html=True)
    
    tab1, tab2 = st.tabs(["📋 Lista", "📥 Exportar"])
    
    with tab1:
        if datos and len(datos) > 0:
            st.dataframe(pd.DataFrame(datos), use_container_width=True)
        else:
            st.info("No hay datos registrados")
    
    with tab2:
        if datos and len(datos) > 0:
            excel_data = exportar_excel(datos, session_key)
            st.download_button("📥 Descargar Excel", data=excel_data, file_name=f"{session_key}_{datetime.now().strftime('%Y%m%d')}.xlsx")

def render_chat_ia():
    st.markdown('<div class="main-header"><h1>💬 Chat IA</h1><p>Asistente virtual - Escribe tu pregunta</p></div>', unsafe_allow_html=True)
    
    # Función local para IA solo en el chat
    def call_groq_only(prompt):
        try:
            key = st.secrets.get("GROQ_API_KEY")
            if not key:
                return "⚠️ No hay API key de Groq configurada"
            
            url = "https://api.groq.com/openai/v1/chat/completions"
            headers = {"Authorization": f"Bearer {key}", "Content-Type": "application/json"}
            data = {
                "model": "llama-3.3-70b-versatile",
                "messages": [{"role": "user", "content": prompt}],
                "temperature": 0.7
            }
            r = requests.post(url, json=data, headers=headers, timeout=30)
            if r.status_code == 200:
                return r.json()["choices"][0]["message"]["content"]
            else:
                return f"Error {r.status_code}: {r.text[:100]}"
        except Exception as e:
            return f"Error: {str(e)}"
    
    if not st.session_state.chat_messages:
        st.session_state.chat_messages = [{"role": "assistant", "content": "Hola, soy tu asistente SST. Uso Groq para responder. ¿En qué puedo ayudarte?"}]
    
    for msg in st.session_state.chat_messages:
        with st.chat_message(msg["role"]):
            st.write(msg["content"])
    
    if prompt := st.chat_input("Pregunta sobre SST..."):
        st.session_state.chat_messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.write(prompt)
        
        with st.chat_message("assistant"):
            with st.spinner("Consultando IA..."):
                respuesta = call_groq_only(prompt)
                st.write(respuesta)
                st.session_state.chat_messages.append({"role": "assistant", "content": respuesta})

def render_matriz_legal():
    st.markdown('<div class="main-header"><h1>📋 Matriz Legal</h1><p>ISO 45001 + Decreto 1072</p></div>', unsafe_allow_html=True)
    requisitos = [
        {"norma": "ISO 45001", "articulo": "4.1", "requisito": "Comprender la organización"},
        {"norma": "ISO 45001", "articulo": "5.2", "requisito": "Política de SST"},
        {"norma": "Decreto 1072", "articulo": "2.2.4.6.22", "requisito": "Conformar COPASST"},
    ]
    for req in requisitos:
        st.write(f"**{req['norma']} - {req['articulo']}**: {req['requisito']}")
        st.checkbox("Cumple", key=req['articulo'])
        st.markdown("---")

def render_indicadores():
    st.markdown('<div class="main-header"><h1>📊 Indicadores</h1></div>', unsafe_allow_html=True)
    total = len(st.session_state.trabajadores)
    incidentes = len(st.session_state.incidentes)
    tasa = (incidentes * 100 / total) if total > 0 else 0
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Tasa Accidentalidad", f"{tasa:.1f}%")
    with col2:
        st.metric("Trabajadores", total)

# ========== RUTEO ==========
if menu == "Dashboard":
    render_dashboard()
elif menu == "Empresa":
    st.markdown('<div class="main-header"><h1>🏢 Configuración</h1></div>', unsafe_allow_html=True)
    with st.form("empresa_form"):
        nombre = st.text_input("Nombre", value=st.session_state.empresa["nombre"])
        nit = st.text_input("NIT", value=st.session_state.empresa["nit"])
        if st.form_submit_button("Guardar"):
            st.session_state.empresa["nombre"] = nombre
            st.session_state.empresa["nit"] = nit
            st.success("✅ Guardado")
elif menu == "Peligros":
    render_modulo("⚠️ Peligros", st.session_state.peligros, "peligros")
elif menu == "Plan de Acción":
    render_modulo("✅ Plan de Acción", st.session_state.acciones, "acciones")
elif menu == "Trabajadores":
    render_modulo("👥 Trabajadores", st.session_state.trabajadores, "trabajadores")
elif menu == "Incidentes":
    render_modulo("📝 Incidentes", st.session_state.incidentes, "incidentes")
elif menu == "Matriz Legal":
    render_matriz_legal()
elif menu == "Auditorías":
    st.info("Módulo de auditorías - En desarrollo")
elif menu == "Capacitaciones":
    render_modulo("📚 Capacitaciones", st.session_state.capacitaciones, "capacitaciones")
elif menu == "Inspecciones":
    st.info("Módulo de inspecciones - En desarrollo")
elif menu == "Emergencias":
    st.info("Módulo de emergencias - En desarrollo")
elif menu == "Documentos":
    st.info("Módulo de documentos - En desarrollo")
elif menu == "Indicadores":
    render_indicadores()
elif menu == "Chat IA":
    render_chat_ia()

st.markdown("---")
st.markdown("<p style='text-align:center; font-size:11px; color:gray'>SG-SST PHVA | JAN BENITEZ</p>", unsafe_allow_html=True)

# NO_AUTO_IA - 06/11/2026 09:44:00
