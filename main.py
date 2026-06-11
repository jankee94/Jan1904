import streamlit as st
import pandas as pd
from datetime import datetime
import io
import requests
import itertools
import traceback

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
    .main-header p { color: rgba(255,255,255,0.8); margin: 5px 0 0 0; }
    .metric-card {
        background: rgba(255,255,255,0.15);
        border-radius: 12px;
        padding: 15px;
        text-align: center;
    }
    .metric-value { font-size: 2rem; font-weight: bold; color: #667eea; }
    .metric-label { font-size: 0.8rem; color: rgba(255,255,255,0.7); }
    .error-box {
        background: rgba(231, 76, 60, 0.2);
        border-left: 4px solid #e74c3c;
        padding: 10px;
        margin: 10px 0;
        border-radius: 5px;
        font-family: monospace;
        font-size: 12px;
        white-space: pre-wrap;
    }
</style>
''', unsafe_allow_html=True)

# ========== DEPURACIÓN ==========
def show_error(error_msg, error_detail=""):
    """Mostrar error de forma visible"""
    st.markdown(f'''
    <div class="error-box">
        <b>❌ Error:</b> {error_msg}<br>
        <details>
            <summary>Ver detalles</summary>
            <code>{error_detail}</code>
        </details>
    </div>
    ''', unsafe_allow_html=True)

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
        st.error(f"Error leyendo secrets: {e}")
    return keys

def get_groq_key():
    try:
        return st.secrets.get("GROQ_API_KEY")
    except:
        return None

GEMINI_KEYS = get_all_gemini_keys()
GROQ_KEY = get_groq_key()
gemini_cycle = itertools.cycle(GEMINI_KEYS) if GEMINI_KEYS else None

def call_gemini(prompt):
    """Llamar a Gemini API"""
    if not GEMINI_KEYS:
        return None
    
    for intento in range(len(GEMINI_KEYS) * 2):
        key = next(gemini_cycle)
        try:
            url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-flash-latest:generateContent"
            headers = {"Content-Type": "application/json", "X-goog-api-key": key}
            data = {"contents": [{"parts": [{"text": prompt}]}]}
            r = requests.post(url, json=data, headers=headers, timeout=30)
            
            if r.status_code == 200:
                return r.json()["candidates"][0]["content"]["parts"][0]["text"]
            elif r.status_code == 503:
                continue
        except:
            continue
    return None

def call_groq(prompt):
    """Llamar a Groq API"""
    if not GROQ_KEY:
        return None
    
    try:
        url = "https://api.groq.com/openai/v1/chat/completions"
        headers = {"Authorization": f"Bearer {GROQ_KEY}", "Content-Type": "application/json"}
        data = {
            "model": "llama-3.3-70b-versatile",
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.7,
            "max_tokens": 1024
        }
        r = requests.post(url, json=data, headers=headers, timeout=30)
        if r.status_code == 200:
            return r.json()["choices"][0]["message"]["content"]
    except:
        pass
    return None

def call_best_ia(prompt):
    """Intentar Gemini primero, luego Groq"""
    respuesta = call_gemini(prompt)
    if respuesta:
        return respuesta
    respuesta = call_groq(prompt)
    if respuesta:
        return respuesta
    return None

def chat_ia(pregunta):
    """Chat IA especializado en SST"""
    contexto = f"""Eres un asistente experto en Seguridad y Salud en el Trabajo (SST) en Colombia.
Responde de forma clara, concisa y profesional.
Si no sabes algo, dilo honestamente.

Pregunta: {pregunta}"""
    
    respuesta = call_best_ia(contexto)
    if respuesta:
        return respuesta
    return "⚠️ Lo siento, no pude procesar tu consulta en este momento. Por favor, intenta de nuevo."

# ========== FUNCIONES DE EXPORTAR/IMPORTAR ==========
def exportar_excel(data, nombre):
    df = pd.DataFrame(data)
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, sheet_name=nombre, index=False)
    return output.getvalue()

# ========== INICIALIZACIÓN SEGURA ==========
def init_session():
    if "auth" not in st.session_state:
        st.session_state.auth = False
    if "username" not in st.session_state:
        st.session_state.username = None
    if "user_role" not in st.session_state:
        st.session_state.user_role = None
    if "last_error" not in st.session_state:
        st.session_state.last_error = None
    
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
            {"id": 2, "descripcion": "Capacitación en pausas activas", "responsable": "SST", "fecha_limite": "2024-11-30", "estado": "Pendiente"},
        ]
    
    if "trabajadores" not in st.session_state:
        st.session_state.trabajadores = [
            {"id": 1, "nombre": "Carlos López", "cedula": "12345678", "cargo": "Operario"},
            {"id": 2, "nombre": "María Gómez", "cedula": "87654321", "cargo": "Supervisor"},
        ]
    
    if "incidentes" not in st.session_state:
        st.session_state.incidentes = [
            {"id": 1, "descripcion": "Caída desde andamio", "fecha": "2024-10-15", "gravedad": "Grave"},
            {"id": 2, "descripcion": "Corte con herramienta", "fecha": "2024-10-20", "gravedad": "Leve"},
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
    
    if "chat_messages" not in st.session_state:
        st.session_state.chat_messages = []

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
                try:
                    if username == "admin" and password == "admin123":
                        st.session_state.auth = True
                        st.session_state.username = "Administrador"
                        st.session_state.user_role = "admin"
                        st.rerun()
                    else:
                        st.error("❌ Usuario o contraseña incorrectos")
                except Exception as e:
                    show_error(str(e), traceback.format_exc())
        
        st.markdown('<p style="text-align:center; font-size:11px; color:gray">SG-SST PHVA | JAN BENITEZ</p>', unsafe_allow_html=True)
    st.stop()

# ========== SIDEBAR ==========
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/2917/2917995.png", width=50)
    
    nombre_display = st.session_state.username if st.session_state.username else "Usuario"
    st.markdown(f"### {nombre_display}")
    st.caption(f"Rol: {st.session_state.user_role if st.session_state.user_role else 'admin'}")
    st.markdown("---")
    
    menu = st.radio("📋 MÓDULOS", [
        "Dashboard", "Empresa", "Peligros", "Plan de Acción",
        "Trabajadores", "Incidentes", "Matriz Legal", "Auditorías",
        "Capacitaciones", "Inspecciones", "Emergencias", "Documentos",
        "Indicadores", "Chat IA"
    ], key="menu_selector")
    
    st.markdown("---")
    if st.button("🚪 Cerrar Sesión", use_container_width=True):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()

# ========== RENDER MÓDULOS ==========
def render_modulo(titulo, datos, session_key):
    st.markdown(f'<div class="main-header"><h1>{titulo}</h1></div>', unsafe_allow_html=True)
    
    tab1, tab2 = st.tabs(["📋 Lista", "📥 Exportar"])
    
    with tab1:
        if datos and len(datos) > 0:
            df = pd.DataFrame(datos)
            st.dataframe(df, use_container_width=True)
        else:
            st.info("No hay datos registrados")
    
    with tab2:
        if datos and len(datos) > 0:
            excel_data = exportar_excel(datos, session_key)
            st.download_button("📥 Descargar Excel", data=excel_data, file_name=f"{session_key}_{datetime.now().strftime('%Y%m%d')}.xlsx")
        else:
            st.info("No hay datos para exportar")

# ========== PÁGINAS ==========
try:
    if menu == "Dashboard":
        st.markdown(f'<div class="main-header"><h1>📊 Dashboard SST</h1><p>{st.session_state.empresa["nombre"]}</p></div>', unsafe_allow_html=True)
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("⚠️ Peligros", len(st.session_state.peligros))
        with col2:
            completadas = len([a for a in st.session_state.acciones if a["estado"] == "Completada"])
            st.metric("✅ Acciones", f"{completadas}/{len(st.session_state.acciones)}")
        with col3:
            st.metric("👥 Trabajadores", len(st.session_state.trabajadores))
        with col4:
            st.metric("📝 Incidentes", len(st.session_state.incidentes))
        
        # Mostrar estado de IA
        with st.expander("🤖 Estado de IA"):
            st.write(f"**Gemini Keys:** {len(GEMINI_KEYS)}")
            st.write(f"**Groq Key:** {'✅ Configurada' if GROQ_KEY else '❌ No configurada'}")
            
            if st.button("Probar IA"):
                with st.spinner("Probando conexión..."):
                    test = call_best_ia("Responde solo: OK")
                    if test:
                        st.success(f"✅ IA responde: {test}")
                    else:
                        st.error("❌ IA no responde. Verifica las API keys en Secrets")

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
        render_modulo("⚠️ Gestión de Peligros", st.session_state.peligros, "peligros")

    elif menu == "Plan de Acción":
        render_modulo("✅ Plan de Acción", st.session_state.acciones, "acciones")

    elif menu == "Trabajadores":
        render_modulo("👥 Trabajadores", st.session_state.trabajadores, "trabajadores")

    elif menu == "Incidentes":
        render_modulo("📝 Incidentes", st.session_state.incidentes, "incidentes")

    elif menu == "Matriz Legal":
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

    elif menu == "Auditorías":
        st.markdown('<div class="main-header"><h1>🔍 Auditorías</h1></div>', unsafe_allow_html=True)
        with st.form("add_auditoria"):
            codigo = st.text_input("Código", "AUD-001")
            if st.form_submit_button("Crear"):
                st.session_state.auditorias.append({"codigo": codigo, "fecha": datetime.now().strftime("%Y-%m-%d")})
                st.success(f"✅ Auditoría {codigo} creada")

    elif menu == "Capacitaciones":
        render_modulo("📚 Capacitaciones", st.session_state.capacitaciones, "capacitaciones")

    elif menu == "Inspecciones":
        st.markdown('<div class="main-header"><h1>🔧 Inspecciones</h1></div>', unsafe_allow_html=True)
        st.info("Módulo de inspecciones - En desarrollo")

    elif menu == "Emergencias":
        st.markdown('<div class="main-header"><h1>🚨 Emergencias</h1></div>', unsafe_allow_html=True)
        st.info("Módulo de emergencias - En desarrollo")

    elif menu == "Documentos":
        st.markdown('<div class="main-header"><h1>📄 Documentos</h1></div>', unsafe_allow_html=True)
        st.info("Módulo de documentos - En desarrollo")

    elif menu == "Indicadores":
        st.markdown('<div class="main-header"><h1>📊 Indicadores</h1></div>', unsafe_allow_html=True)
        total = len(st.session_state.trabajadores)
        incidentes = len(st.session_state.incidentes)
        tasa = (incidentes * 100 / total) if total > 0 else 0
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Tasa Accidentalidad", f"{tasa:.1f}%")
        with col2:
            st.metric("Trabajadores", total)
        with col3:
            st.metric("Incidentes", incidentes)

    elif menu == "Chat IA":
        st.markdown('<div class="main-header"><h1>💬 Chat IA</h1><p>Asistente virtual especializado en SST</p></div>', unsafe_allow_html=True)
        
        if not st.session_state.chat_messages:
            st.session_state.chat_messages = [{"role": "assistant", "content": f"Hola, soy tu asistente SST. Uso {len(GEMINI_KEYS)} keys de Gemini. ¿En qué puedo ayudarte?"}]
        
        for msg in st.session_state.chat_messages:
            with st.chat_message(msg["role"]):
                st.write(msg["content"])
        
        if prompt := st.chat_input("Escribe tu pregunta sobre SST..."):
            st.session_state.chat_messages.append({"role": "user", "content": prompt})
            with st.chat_message("user"):
                st.write(prompt)
            
            with st.chat_message("assistant"):
                with st.spinner("🤖 Consultando IA..."):
                    respuesta = chat_ia(prompt)
                    if respuesta:
                        st.write(respuesta)
                        st.session_state.chat_messages.append({"role": "assistant", "content": respuesta})
                    else:
                        error_msg = "No se pudo obtener respuesta. Verifica las API keys en Secrets."
                        st.error(error_msg)
                        st.session_state.chat_messages.append({"role": "assistant", "content": error_msg})

except Exception as e:
    show_error(str(e), traceback.format_exc())

st.markdown("---")
st.markdown("<p style='text-align:center; font-size:11px; color:gray'>SG-SST PHVA | JAN BENITEZ</p>", unsafe_allow_html=True)

# DEPURADO - 06/11/2026 08:49:48
