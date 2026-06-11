import streamlit as st
import json
import pandas as pd
from datetime import datetime
import io
import requests
import itertools
import traceback
import sys

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
    .error-box {
        background: rgba(231, 76, 60, 0.3);
        border-left: 4px solid #e74c3c;
        padding: 15px;
        margin: 10px 0;
        border-radius: 8px;
        font-family: monospace;
        font-size: 12px;
        white-space: pre-wrap;
        overflow-x: auto;
    }
    .error-box summary {
        cursor: pointer;
        color: #e74c3c;
        font-weight: bold;
    }
</style>
''', unsafe_allow_html=True)

# ========== CAPTURADOR DE ERRORES ==========
error_log = []

def capture_error(error_msg, error_detail=""):
    """Capturar error para mostrarlo y que la IA pueda verlo"""
    error_entry = {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "message": str(error_msg),
        "detail": str(error_detail),
        "traceback": traceback.format_exc()
    }
    error_log.append(error_entry)
    
    # Mostrar en la interfaz
    st.markdown(f'''
    <div class="error-box">
        <details>
            <summary>❌ Error capturado: {str(error_msg)[:100]}</summary>
            <b>Mensaje:</b> {error_msg}<br><br>
            <b>Detalle:</b><br><code>{error_detail}</code><br><br>
            <b>Traceback:</b><br><code>{traceback.format_exc()}</code>
        </details>
    </div>
    ''', unsafe_allow_html=True)
    
    return error_entry

def get_error_summary():
    """Obtener resumen de errores para la IA"""
    if not error_log:
        return "No hay errores capturados"
    
    summary = "=== ERRORES CAPTURADOS ===\n"
    for i, err in enumerate(error_log[-5:], 1):  # Últimos 5 errores
        summary += f"\nERROR {i}:\n"
        summary += f"  Hora: {err['timestamp']}\n"
        summary += f"  Mensaje: {err['message']}\n"
        if err['detail']:
            summary += f"  Detalle: {err['detail'][:500]}\n"
    return summary

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
        capture_error("Error leyendo Gemini keys", str(e))
    return keys

def get_groq_key():
    try:
        return st.secrets.get("GROQ_API_KEY")
    except Exception as e:
        capture_error("Error leyendo Groq key", str(e))
        return None

GEMINI_KEYS = get_all_gemini_keys()
GROQ_KEY = get_groq_key()
gemini_cycle = itertools.cycle(GEMINI_KEYS) if GEMINI_KEYS else None

def call_gemini(prompt):
    if not GEMINI_KEYS:
        capture_error("No hay Gemini keys", "GEMINI_KEYS está vacío")
        return None
    
    for intento in range(len(GEMINI_KEYS) * 2):
        try:
            key = next(gemini_cycle)
            url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-flash-latest:generateContent"
            headers = {"Content-Type": "application/json", "X-goog-api-key": key}
            data = {"contents": [{"parts": [{"text": prompt}]}]}
            r = requests.post(url, json=data, headers=headers, timeout=30)
            
            if r.status_code == 200:
                return r.json()["candidates"][0]["content"]["parts"][0]["text"]
            elif r.status_code == 503:
                continue
            else:
                capture_error(f"Gemini error {r.status_code}", r.text[:200])
        except Exception as e:
            capture_error("Error en llamada Gemini", str(e))
            continue
    return None

def call_groq(prompt):
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
    except Exception as e:
        capture_error("Error en Groq", str(e))
    return None

def call_best_ia(prompt):
    respuesta = call_gemini(prompt)
    if respuesta:
        return respuesta
    respuesta = call_groq(prompt)
    if respuesta:
        return respuesta
    return None

def chat_ia_con_contexto(pregunta):
    """Chat IA con contexto de la app y sus errores"""
    
    # Recopilar contexto de la aplicación
    context = {
        "app_name": "SG-SST PHVA",
        "empresa": st.session_state.get("empresa", {}),
        "estadisticas": {
            "peligros": len(st.session_state.get("peligros", [])),
            "acciones": len(st.session_state.get("acciones", [])),
            "trabajadores": len(st.session_state.get("trabajadores", [])),
            "incidentes": len(st.session_state.get("incidentes", []))
        },
        "ia_config": {
            "gemini_keys": len(GEMINI_KEYS),
            "groq_key": GROQ_KEY is not None
        },
        "errores": get_error_summary()
    }
    
    contexto = f"""
    Eres un asistente experto en SST y en depuración de aplicaciones Streamlit.
    
    === CONTEXTO DE LA APLICACIÓN ===
    App: {context['app_name']}
    Empresa: {json.dumps(context['empresa'], ensure_ascii=False)}
    Estadísticas: {json.dumps(context['estadisticas'], ensure_ascii=False)}
    Configuración IA: {json.dumps(context['ia_config'], ensure_ascii=False)}
    
    === ERRORES CAPTURADOS ===
    {context['errores']}
    
    === PREGUNTA DEL USUARIO ===
    {pregunta}
    
    Por favor, responde de forma clara. Si hay errores capturados, analízalos y sugiere soluciones.
    """
    
    respuesta = call_best_ia(contexto)
    if respuesta:
        return respuesta
    return "⚠️ No pude procesar tu consulta. Por favor, verifica las API keys en Secrets."

# ========== FUNCIONES DE EXPORTAR ==========
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
                try:
                    if username == "admin" and password == "admin123":
                        st.session_state.auth = True
                        st.session_state.username = "Administrador"
                        st.rerun()
                    else:
                        st.error("❌ Usuario o contraseña incorrectos")
                except Exception as e:
                    capture_error("Error en login", str(e))
        
        st.markdown('<p style="text-align:center; font-size:11px; color:gray">SG-SST PHVA | JAN BENITEZ</p>', unsafe_allow_html=True)
    st.stop()

# ========== SIDEBAR ==========
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/2917/2917995.png", width=50)
    nombre_display = st.session_state.username if st.session_state.username else "Usuario"
    st.markdown(f"### {nombre_display}")
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

# ========== PÁGINAS ==========
try:
    if menu == "Dashboard":
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
        
        # Panel de errores
        if error_log:
            with st.expander("⚠️ Ver errores capturados", expanded=True):
                for err in error_log[-3:]:
                    st.code(f"[{err['timestamp']}] {err['message']}\n{err['detail'][:300] if err['detail'] else ''}")
                st.caption(f"Total errores: {len(error_log)}")
        
        # Estado IA
        with st.expander("🤖 Estado de IA"):
            st.write(f"**Gemini Keys:** {len(GEMINI_KEYS)}")
            st.write(f"**Groq Key:** {'✅' if GROQ_KEY else '❌'}")
            if st.button("Probar IA"):
                with st.spinner("Probando..."):
                    test = call_best_ia("Responde solo: OK")
                    if test:
                        st.success(f"✅ IA responde: {test}")
                    else:
                        st.error("❌ IA no responde")

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
        st.markdown('<div class="main-header"><h1>📋 Matriz Legal</h1></div>', unsafe_allow_html=True)
        st.info("ISO 45001 + Decreto 1072 - En desarrollo")
    elif menu == "Auditorías":
        st.markdown('<div class="main-header"><h1>🔍 Auditorías</h1></div>', unsafe_allow_html=True)
        st.info("Módulo de auditorías - En desarrollo")
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
        st.metric("Tasa Accidentalidad", f"{(incidentes * 100 / total) if total > 0 else 0:.1f}%")

    elif menu == "Chat IA":
        st.markdown('<div class="main-header"><h1>💬 Chat IA con Diagnóstico</h1><p>Puedo ver los errores y analizar la app</p></div>', unsafe_allow_html=True)
        
        if not st.session_state.chat_messages:
            st.session_state.chat_messages = [{"role": "assistant", "content": f"Hola, soy tu asistente. Puedo ver los errores de la app. Uso {len(GEMINI_KEYS)} keys de Gemini. ¿En qué puedo ayudarte?"}]
        
        for msg in st.session_state.chat_messages:
            with st.chat_message(msg["role"]):
                st.write(msg["content"])
        
        if prompt := st.chat_input("Pregunta sobre SST o sobre errores de la aplicación..."):
            st.session_state.chat_messages.append({"role": "user", "content": prompt})
            with st.chat_message("user"):
                st.write(prompt)
            
            with st.chat_message("assistant"):
                with st.spinner("🔍 Analizando..."):
                    respuesta = chat_ia_con_contexto(prompt)
                    st.write(respuesta)
                    st.session_state.chat_messages.append({"role": "assistant", "content": respuesta})

except Exception as e:
    capture_error("Error en módulo", str(e))
    st.error(f"Error en el módulo {menu}: {str(e)}")

st.markdown("---")
st.markdown("<p style='text-align:center; font-size:11px; color:gray'>SG-SST PHVA | JAN BENITEZ</p>", unsafe_allow_html=True)

# ERROR_CAPTURE - 06/11/2026 09:06:12


# FIX_JSON - 06/11/2026 09:09:50
