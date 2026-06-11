import streamlit as st
import pandas as pd
from datetime import datetime
import io
import requests
import itertools
import json
import sys
import traceback

st.set_page_config(page_title="SG-SST PHVA", page_icon="🔄", layout="wide")

# ========== CSS PARA ERRORES VISIBLES ==========
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
    .error-global {
        background: rgba(231, 76, 60, 0.4);
        border: 2px solid #e74c3c;
        border-radius: 10px;
        padding: 15px;
        margin: 10px 0;
        font-family: monospace;
        font-size: 13px;
        white-space: pre-wrap;
        color: white;
    }
    .error-global summary {
        cursor: pointer;
        color: #ff6b6b;
        font-weight: bold;
    }
</style>
''', unsafe_allow_html=True)

# ========== CAPTURA GLOBAL DE ERRORES ==========
error_global_log = []

def log_error(error_msg, error_detail=""):
    """Registrar error global"""
    error_entry = {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3],
        "message": str(error_msg),
        "detail": str(error_detail),
        "traceback": traceback.format_exc()
    }
    error_global_log.append(error_entry)
    
    # Mostrar error visiblemente
    st.markdown(f'''
    <div class="error-global">
        <details open>
            <summary>🔴 ERROR DETECTADO</summary>
            <b>Hora:</b> {error_entry['timestamp']}<br>
            <b>Mensaje:</b> {error_msg}<br>
            <b>Detalle:</b><br><code>{error_detail[:500] if error_detail else 'Sin detalle'}</code><br>
            <b>Traceback:</b><br><code>{traceback.format_exc()[:1000]}</code>
        </details>
    </div>
    ''', unsafe_allow_html=True)
    
    return error_entry

# ========== CONFIGURACIÓN DE IA ==========
def get_all_gemini_keys():
    keys = []
    try:
        for i in range(1, 10):
            key = st.secrets.get(f"GEMINI_API_KEY_{i}")
            if key and key != "":
                keys.append(key)
        if not keys:
            key = st.secrets.get("GEMINI_API_KEY")
            if key and key != "":
                keys.append(key)
    except Exception as e:
        log_error("Error leyendo Gemini keys", str(e))
    return keys

def get_groq_key():
    try:
        return st.secrets.get("GROQ_API_KEY")
    except Exception as e:
        log_error("Error leyendo Groq key", str(e))
        return None

GEMINI_KEYS = get_all_gemini_keys()
GROQ_KEY = get_groq_key()
gemini_cycle = itertools.cycle(GEMINI_KEYS) if GEMINI_KEYS else None

def call_gemini(prompt):
    if not GEMINI_KEYS:
        return None
    for _ in range(len(GEMINI_KEYS) * 2):
        try:
            key = next(gemini_cycle)
            url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-flash-latest:generateContent"
            headers = {"Content-Type": "application/json", "X-goog-api-key": key}
            data = {"contents": [{"parts": [{"text": prompt}]}]}
            r = requests.post(url, json=data, headers=headers, timeout=30)
            if r.status_code == 200:
                return r.json()["candidates"][0]["content"]["parts"][0]["text"]
            elif r.status_code == 429:
                log_error(f"Rate limit en Gemini (429)", f"Key: {key[:20]}...")
                continue
        except Exception as e:
            log_error("Error en llamada Gemini", str(e))
            continue
    return None

def call_best_ia(prompt):
    respuesta = call_gemini(prompt)
    if respuesta:
        return respuesta
    return "⚠️ IA no disponible. Las keys de Gemini están en rate limit. Intenta de nuevo en unos segundos."

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
    if "current_menu" not in st.session_state:
        st.session_state.current_menu = "Dashboard"
    if "error_log" not in st.session_state:
        st.session_state.error_log = []
    
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
    
    nuevo_menu = st.radio("📋 MÓDULOS", [
        "Dashboard", "Empresa", "Peligros", "Plan de Acción",
        "Trabajadores", "Incidentes", "Matriz Legal", "Auditorías",
        "Capacitaciones", "Inspecciones", "Emergencias", "Documentos",
        "Indicadores", "Chat IA"
    ])
    
    # Detectar cambio de módulo
    if nuevo_menu != st.session_state.get("current_menu", ""):
        st.session_state.current_menu = nuevo_menu
        # Limpiar errores anteriores al cambiar
        st.session_state.error_log = []
    
    st.markdown("---")
    if st.button("🚪 Cerrar Sesión", use_container_width=True):
        st.session_state.auth = False
        st.rerun()

menu = st.session_state.current_menu

# ========== WRAPPER PARA CAPTURAR ERRORES EN CADA MÓDULO ==========
def run_module_safe(module_func, module_name):
    """Ejecutar módulo capturando cualquier error"""
    try:
        module_func()
    except Exception as e:
        error_msg = f"Error en módulo {module_name}: {str(e)}"
        error_detail = traceback.format_exc()
        log_error(error_msg, error_detail)
        st.error(f"❌ {error_msg}")
        st.code(error_detail)

# ========== DEFINICIÓN DE MÓDULOS ==========
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
    
    # Mostrar errores capturados
    if error_global_log:
        with st.expander(f"⚠️ Ver {len(error_global_log)} errores capturados", expanded=True):
            for err in error_global_log[-5:]:
                st.code(f"[{err['timestamp']}] {err['message']}\n{err['detail'][:300]}")
    
    with st.expander("🤖 Estado IA"):
        st.write(f"Gemini Keys: {len(GEMINI_KEYS)}")
        if st.button("Probar IA"):
            with st.spinner("Probando..."):
                test = call_best_ia("Responde solo: OK")
                if test and "⚠️" not in test:
                    st.success(f"✅ {test}")
                else:
                    st.error(f"❌ {test}")

def render_empresa():
    st.markdown('<div class="main-header"><h1>🏢 Configuración</h1></div>', unsafe_allow_html=True)
    with st.form("empresa_form"):
        nombre = st.text_input("Nombre", value=st.session_state.empresa["nombre"])
        nit = st.text_input("NIT", value=st.session_state.empresa["nit"])
        if st.form_submit_button("Guardar"):
            st.session_state.empresa["nombre"] = nombre
            st.session_state.empresa["nit"] = nit
            st.success("✅ Guardado")

def render_modulo(titulo, datos, session_key):
    st.markdown(f'<div class="main-header"><h1>{titulo}</h1></div>', unsafe_allow_html=True)
    if datos and len(datos) > 0:
        df = pd.DataFrame(datos)
        st.dataframe(df, use_container_width=True)
        excel_data = exportar_excel(datos, session_key)
        st.download_button("📥 Exportar Excel", data=excel_data, file_name=f"{session_key}_{datetime.now().strftime('%Y%m%d')}.xlsx")
    else:
        st.info("No hay datos registrados")

def render_chat_ia():
    st.markdown('<div class="main-header"><h1>💬 Chat IA</h1><p>Pregunta sobre SST o sobre errores de la app</p></div>', unsafe_allow_html=True)
    
    if not st.session_state.chat_messages:
        st.session_state.chat_messages = [{"role": "assistant", "content": f"Hola, uso {len(GEMINI_KEYS)} keys de Gemini. ¿En qué puedo ayudarte?"}]
    
    for msg in st.session_state.chat_messages:
        with st.chat_message(msg["role"]):
            st.write(msg["content"])
    
    if prompt := st.chat_input("Escribe tu pregunta..."):
        st.session_state.chat_messages.append({"role": "user", "content": prompt})
        with st.chat_message("assistant"):
            with st.spinner("Pensando..."):
                # Incluir errores en el contexto
                error_context = f"\n\nERRORES CAPTURADOS:\n{json.dumps(error_global_log[-5:], indent=2)}" if error_global_log else ""
                respuesta = call_best_ia(prompt + error_context)
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

# ========== RUTEO CON CAPTURA DE ERRORES ==========
if menu == "Dashboard":
    render_dashboard()
elif menu == "Empresa":
    render_empresa()
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

# GLOBAL_ERROR - 06/11/2026 09:30:36
