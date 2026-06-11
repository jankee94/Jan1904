import streamlit as st
import pandas as pd
from datetime import datetime
import io
import requests
import itertools

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
</style>
''', unsafe_allow_html=True)

# ========== INICIALIZACIÓN SEGURA DE SESSION STATE ==========
def init_session():
    """Inicializar todas las variables de session_state de forma segura"""
    if "auth" not in st.session_state:
        st.session_state.auth = False
    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False
    if "username" not in st.session_state:
        st.session_state.username = None
    if "user_role" not in st.session_state:
        st.session_state.user_role = None
    
    # Datos de la empresa
    if "empresa" not in st.session_state:
        st.session_state.empresa = {"nombre": "Constructora Segura SAS", "nit": "901.234.567-8"}
    
    # Datos de los módulos
    if "peligros" not in st.session_state:
        st.session_state.peligros = [
            {"id": 1, "tipo": "Físico", "descripcion": "Ruido excesivo", "probabilidad": 4, "severidad": 3, "nivel": "I", "fecha": "2024-01-15"},
            {"id": 2, "tipo": "Ergonómico", "descripcion": "Posturas forzadas", "probabilidad": 3, "severidad": 2, "nivel": "II", "fecha": "2024-01-20"},
        ]
    
    if "acciones" not in st.session_state:
        st.session_state.acciones = [
            {"id": 1, "descripcion": "Implementar barreras acústicas", "responsable": "SST", "fecha_limite": "2024-12-15", "estado": "Pendiente", "prioridad": "Alta"},
            {"id": 2, "descripcion": "Capacitación en pausas activas", "responsable": "SST", "fecha_limite": "2024-11-30", "estado": "Pendiente", "prioridad": "Media"},
        ]
    
    if "trabajadores" not in st.session_state:
        st.session_state.trabajadores = [
            {"id": 1, "nombre": "Carlos López", "cedula": "12345678", "cargo": "Operario", "area": "Producción"},
            {"id": 2, "nombre": "María Gómez", "cedula": "87654321", "cargo": "Supervisor", "area": "Producción"},
        ]
    
    if "incidentes" not in st.session_state:
        st.session_state.incidentes = [
            {"id": 1, "descripcion": "Caída desde andamio", "fecha": "2024-10-15", "gravedad": "Grave", "tipo": "Accidente"},
            {"id": 2, "descripcion": "Corte con herramienta", "fecha": "2024-10-20", "gravedad": "Leve", "tipo": "Incidente"},
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

# ========== CONFIGURACIÓN DE IA ==========
def get_all_gemini_keys():
    keys = []
    for i in range(1, 10):
        key = st.secrets.get(f"GEMINI_API_KEY_{i}")
        if key and key != "":
            keys.append(key)
    if not keys:
        key = st.secrets.get("GEMINI_API_KEY")
        if key and key != "":
            keys.append(key)
    return keys

GEMINI_KEYS = get_all_gemini_keys()
gemini_cycle = itertools.cycle(GEMINI_KEYS) if GEMINI_KEYS else None

def call_best_ia(prompt):
    if GEMINI_KEYS:
        for _ in range(len(GEMINI_KEYS) * 2):
            key = next(gemini_cycle)
            try:
                url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-flash-latest:generateContent"
                headers = {"Content-Type": "application/json", "X-goog-api-key": key}
                data = {"contents": [{"parts": [{"text": prompt}]}]}
                r = requests.post(url, json=data, headers=headers, timeout=30)
                if r.status_code == 200:
                    return r.json()["candidates"][0]["content"]["parts"][0]["text"]
            except:
                continue
    return "⚠️ IA no disponible. Intenta de nuevo."

def exportar_excel(data, nombre):
    df = pd.DataFrame(data)
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, sheet_name=nombre, index=False)
    return output.getvalue()

def importar_excel(uploaded_file, tipo):
    try:
        df = pd.read_excel(uploaded_file)
        if tipo == "peligros":
            for _, row in df.iterrows():
                nivel = "I" if row['probabilidad'] * row['severidad'] >= 6 else "II" if row['probabilidad'] * row['severidad'] >= 4 else "III"
                nuevo_id = len(st.session_state.peligros) + 1
                st.session_state.peligros.append({
                    "id": nuevo_id,
                    "tipo": row['tipo'],
                    "descripcion": row['descripcion'],
                    "probabilidad": int(row['probabilidad']),
                    "severidad": int(row['severidad']),
                    "nivel": nivel,
                    "fecha": datetime.now().strftime("%Y-%m-%d")
                })
            return True, f"✅ {len(df)} peligros importados"
        return False, "Formato no soportado"
    except Exception as e:
        return False, f"Error: {str(e)}"

# ========== INICIALIZAR ==========
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
                    st.session_state.logged_in = True
                    st.session_state.username = "Administrador"
                    st.session_state.user_role = "admin"
                    st.rerun()
                else:
                    st.error("❌ Usuario o contraseña incorrectos")
        
        st.markdown('<p style="text-align:center; font-size:11px; color:gray">SG-SST PHVA | JAN BENITEZ</p>', unsafe_allow_html=True)
    st.stop()

# ========== VERIFICACIÓN DE SESIÓN ==========
# Asegurar que las variables existen después del login
if st.session_state.auth:
    if "username" not in st.session_state or st.session_state.username is None:
        st.session_state.username = "Administrador"
    if "user_role" not in st.session_state or st.session_state.user_role is None:
        st.session_state.user_role = "admin"

# ========== SIDEBAR ==========
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/2917/2917995.png", width=50)
    
    # Mostrar nombre de usuario de forma segura
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
        st.session_state.auth = False
        st.session_state.logged_in = False
        st.session_state.username = None
        st.session_state.user_role = None
        st.rerun()

# ========== FUNCIÓN PARA MÓDULOS CON IMPORTAR/EXPORTAR ==========
def render_modulo(titulo, datos, session_key, columnas_required):
    st.markdown(f'<div class="main-header"><h1>{titulo}</h1></div>', unsafe_allow_html=True)
    
    tab1, tab2, tab3 = st.tabs(["📋 Lista", "📥 Exportar", "📎 Importar Excel"])
    
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
    
    with tab3:
        st.info(f"Formato requerido: columnas {', '.join(columnas_required)}")
        uploaded = st.file_uploader("Selecciona archivo Excel", type=['xlsx', 'xls'], key=f"import_{session_key}")
        if uploaded:
            if st.button("📤 Importar datos", use_container_width=True):
                success, msg = importar_excel(uploaded, session_key)
                if success:
                    st.success(msg)
                    st.rerun()
                else:
                    st.error(msg)

# ========== PÁGINAS ==========
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
    
    with st.expander("🤖 Prueba de IA"):
        if st.button("Probar Conexión IA"):
            with st.spinner("Consultando IA..."):
                res = call_best_ia("Responde: IA funcionando correctamente")
                st.write(res)

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
    render_modulo("⚠️ Gestión de Peligros", st.session_state.peligros, "peligros", ["tipo", "descripcion", "probabilidad", "severidad"])

elif menu == "Plan de Acción":
    render_modulo("✅ Plan de Acción", st.session_state.acciones, "acciones", ["descripcion", "responsable", "fecha_limite"])

elif menu == "Trabajadores":
    render_modulo("👥 Trabajadores", st.session_state.trabajadores, "trabajadores", ["nombre", "cedula", "cargo"])

elif menu == "Incidentes":
    render_modulo("📝 Incidentes", st.session_state.incidentes, "incidentes", ["descripcion", "fecha", "gravedad"])

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
    render_modulo("📚 Capacitaciones", st.session_state.capacitaciones, "capacitaciones", ["titulo", "fecha", "duracion"])

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
    st.markdown('<div class="main-header"><h1>💬 Chat IA</h1></div>', unsafe_allow_html=True)
    
    if not st.session_state.chat_messages:
        st.session_state.chat_messages = [{"role": "assistant", "content": "Hola, soy tu asistente SST. ¿En qué puedo ayudarte?"}]
    
    for msg in st.session_state.chat_messages:
        with st.chat_message(msg["role"]):
            st.write(msg["content"])
    
    if prompt := st.chat_input("Pregunta sobre SST..."):
        st.session_state.chat_messages.append({"role": "user", "content": prompt})
        with st.chat_message("assistant"):
            with st.spinner("🤖 Pensando..."):
                respuesta = call_best_ia(prompt)
                st.write(respuesta)
                st.session_state.chat_messages.append({"role": "assistant", "content": respuesta})

st.markdown("---")
st.markdown("<p style='text-align:center; font-size:11px; color:gray'>SG-SST PHVA | JAN BENITEZ</p>", unsafe_allow_html=True)

# ROBUSTO - 06/11/2026 08:45:46
