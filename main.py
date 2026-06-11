import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import io
import requests
import time
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
    .success-badge { background: #27ae60; color: white; padding: 2px 8px; border-radius: 20px; font-size: 11px; }
    .warning-badge { background: #f39c12; color: white; padding: 2px 8px; border-radius: 20px; font-size: 11px; }
    .danger-badge { background: #e74c3c; color: white; padding: 2px 8px; border-radius: 20px; font-size: 11px; }
</style>
''', unsafe_allow_html=True)

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

def get_groq_key():
    return st.secrets.get("GROQ_API_KEY")

GEMINI_KEYS = get_all_gemini_keys()
GROQ_KEY = get_groq_key()
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
    
    if GROQ_KEY:
        modelos = ["llama-3.3-70b-versatile", "llama-3.1-70b-versatile"]
        for modelo in modelos:
            try:
                url = "https://api.groq.com/openai/v1/chat/completions"
                headers = {"Authorization": f"Bearer {GROQ_KEY}", "Content-Type": "application/json"}
                data = {"model": modelo, "messages": [{"role": "user", "content": prompt}], "temperature": 0.7}
                r = requests.post(url, json=data, headers=headers, timeout=30)
                if r.status_code == 200:
                    return r.json()["choices"][0]["message"]["content"]
            except:
                continue
    
    return "⚠️ IA no disponible en este momento."

# ========== FUNCIONES DE EXPORTAR E IMPORTAR ==========
def exportar_excel(data, nombre):
    df = pd.DataFrame(data)
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, sheet_name=nombre, index=False)
    return output.getvalue()

def importar_excel(uploaded_file, tipo):
    """Importar datos desde Excel según el tipo de módulo"""
    try:
        df = pd.read_excel(uploaded_file)
        
        if tipo == "peligros":
            required = ['tipo', 'descripcion', 'probabilidad', 'severidad']
            if all(col in df.columns for col in required):
                for _, row in df.iterrows():
                    nivel = "I" if row['probabilidad'] * row['severidad'] >= 6 else "II" if row['probabilidad'] * row['severidad'] >= 4 else "III"
                    nuevo_id = max([p["id"] for p in st.session_state.peligros]) + 1 if st.session_state.peligros else 1
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
            return False, f"Columnas requeridas: {', '.join(required)}"
        
        elif tipo == "trabajadores":
            required = ['nombre', 'cedula', 'cargo']
            if all(col in df.columns for col in required):
                for _, row in df.iterrows():
                    nuevo_id = max([t["id"] for t in st.session_state.trabajadores]) + 1 if st.session_state.trabajadores else 1
                    st.session_state.trabajadores.append({
                        "id": nuevo_id,
                        "nombre": row['nombre'],
                        "cedula": str(row['cedula']),
                        "cargo": row['cargo'],
                        "area": row.get('area', 'General'),
                        "eps": row.get('eps', 'Sura'),
                        "arl": row.get('arl', 'Positiva')
                    })
                return True, f"✅ {len(df)} trabajadores importados"
            return False, f"Columnas requeridas: {', '.join(required)}"
        
        elif tipo == "acciones":
            required = ['descripcion', 'responsable', 'fecha_limite']
            if all(col in df.columns for col in required):
                for _, row in df.iterrows():
                    nuevo_id = max([a["id"] for a in st.session_state.acciones]) + 1 if st.session_state.acciones else 1
                    st.session_state.acciones.append({
                        "id": nuevo_id,
                        "descripcion": row['descripcion'],
                        "responsable": row['responsable'],
                        "fecha_limite": str(row['fecha_limite']),
                        "estado": row.get('estado', 'Pendiente'),
                        "prioridad": row.get('prioridad', 'Media')
                    })
                return True, f"✅ {len(df)} acciones importadas"
            return False, f"Columnas requeridas: {', '.join(required)}"
        
        elif tipo == "incidentes":
            required = ['descripcion', 'fecha', 'gravedad']
            if all(col in df.columns for col in required):
                for _, row in df.iterrows():
                    nuevo_id = max([i["id"] for i in st.session_state.incidentes]) + 1 if st.session_state.incidentes else 1
                    st.session_state.incidentes.append({
                        "id": nuevo_id,
                        "descripcion": row['descripcion'],
                        "fecha": str(row['fecha']),
                        "gravedad": row['gravedad'],
                        "tipo": row.get('tipo', 'Incidente'),
                        "causa": row.get('causa', 'En investigación')
                    })
                return True, f"✅ {len(df)} incidentes importados"
            return False, f"Columnas requeridas: {', '.join(required)}"
        
        else:
            return False, "Tipo de importación no soportado"
    except Exception as e:
        return False, f"Error al leer el archivo: {str(e)}"

# ========== INICIALIZAR DATOS ==========
def init_data():
    if "auth" not in st.session_state:
        st.session_state.auth = False
    if "current_user" not in st.session_state:
        st.session_state.current_user = None
    
    if "empresa" not in st.session_state:
        st.session_state.empresa = {
            "nombre": "Constructora Segura SAS",
            "nit": "901.234.567-8",
            "ubicacion": "Calle 80 #45-67, Bogotá",
            "sector": "Construcción",
            "telefono": "6015551234",
            "email": "sst@constructora.com"
        }
    
    if "peligros" not in st.session_state:
        st.session_state.peligros = [
            {"id": 1, "tipo": "Físico", "descripcion": "Ruido excesivo", "probabilidad": 4, "severidad": 3, "nivel": "I", "fecha": "2024-01-15"},
        ]
    
    if "acciones" not in st.session_state:
        st.session_state.acciones = [
            {"id": 1, "descripcion": "Implementar barreras", "responsable": "SST", "fecha_limite": "2024-12-15", "estado": "Pendiente", "prioridad": "Alta"},
        ]
    
    if "trabajadores" not in st.session_state:
        st.session_state.trabajadores = [
            {"id": 1, "nombre": "Carlos López", "cedula": "12345678", "cargo": "Operario", "area": "Producción", "eps": "Sura", "arl": "Positiva"},
        ]
    
    if "incidentes" not in st.session_state:
        st.session_state.incidentes = [
            {"id": 1, "descripcion": "Caída desde andamio", "fecha": "2024-10-15", "gravedad": "Grave", "tipo": "Accidente", "causa": "Falta de barandas"},
        ]
    
    if "capacitaciones" not in st.session_state:
        st.session_state.capacitaciones = []
    
    if "inspecciones" not in st.session_state:
        st.session_state.inspecciones = []
    
    if "emergencias" not in st.session_state:
        st.session_state.emergencias = {"brigadistas": [], "equipos": [], "alertas": []}
    
    if "documentos" not in st.session_state:
        st.session_state.documentos = []

init_data()

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
                    st.session_state.current_user = {"nombre": "Administrador", "rol": "admin"}
                    st.rerun()
                else:
                    st.error("❌ Usuario o contraseña incorrectos")
        
        st.markdown('<p style="text-align:center; font-size:11px; color:gray">SG-SST PHVA | JAN BENITEZ</p>', unsafe_allow_html=True)
    st.stop()

# ========== SIDEBAR ==========
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/2917/2917995.png", width=50)
    user_name = st.session_state.current_user.get("nombre", "Usuario") if st.session_state.current_user else "Usuario"
    st.markdown(f"### {user_name}")
    st.caption("Administrador")
    st.markdown("---")
    
    menu = st.radio("📋 MÓDULOS", [
        "🏠 Dashboard", "🏢 Empresa", "⚠️ Peligros", "✅ Plan de Acción",
        "👥 Trabajadores", "📝 Incidentes", "📋 Matriz Legal", "🔍 Auditorías",
        "📚 Capacitaciones", "🔧 Inspecciones", "🚨 Emergencias", "📄 Documentos",
        "📊 Indicadores", "💬 Chat IA"
    ])
    
    st.markdown("---")
    if st.button("🚪 Cerrar Sesión", use_container_width=True):
        st.session_state.auth = False
        st.rerun()

# ========== DASHBOARD ==========
if menu == "🏠 Dashboard":
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

# ========== FUNCIÓN GENÉRICA PARA MÓDULOS CON IMPORTAR/EXPORTAR ==========
def modulo_con_importar(titulo, datos, tipo, columnas_required):
    """Función genérica para módulos con importar y exportar"""
    st.markdown(f'<div class="main-header"><h1>{titulo}</h1></div>', unsafe_allow_html=True)
    
    tab1, tab2, tab3 = st.tabs(["📋 Lista", "📥 Exportar", "📎 Importar Excel"])
    
    with tab1:
        if datos:
            df = pd.DataFrame(datos)
            st.dataframe(df, use_container_width=True)
        else:
            st.info("No hay datos registrados")
    
    with tab2:
        if datos:
            excel_data = exportar_excel(datos, tipo)
            st.download_button("📥 Descargar Excel", data=excel_data, file_name=f"{tipo}_{datetime.now().strftime('%Y%m%d')}.xlsx")
        else:
            st.info("No hay datos para exportar")
    
    with tab3:
        st.info(f"Formato requerido: columnas {', '.join(columnas_required)}")
        uploaded = st.file_uploader(f"Selecciona archivo Excel", type=['xlsx', 'xls'], key=f"import_{tipo}")
        if uploaded:
            if st.button("📤 Importar datos", use_container_width=True):
                success, msg = importar_excel(uploaded, tipo)
                if success:
                    st.success(msg)
                    st.rerun()
                else:
                    st.error(msg)

# ========== PÁGINAS ==========
if menu == "🏠 Dashboard":
    pass  # Ya mostrado arriba

elif menu == "🏢 Empresa":
    st.markdown('<div class="main-header"><h1>🏢 Configuración de la Empresa</h1></div>', unsafe_allow_html=True)
    with st.form("empresa_form"):
        col1, col2 = st.columns(2)
        with col1:
            nombre = st.text_input("Nombre", value=st.session_state.empresa["nombre"])
            nit = st.text_input("NIT", value=st.session_state.empresa["nit"])
        with col2:
            ubicacion = st.text_input("Ubicación", value=st.session_state.empresa["ubicacion"])
            sector = st.text_input("Sector", value=st.session_state.empresa["sector"])
        if st.form_submit_button("💾 Guardar"):
            st.session_state.empresa["nombre"] = nombre
            st.session_state.empresa["nit"] = nit
            st.session_state.empresa["ubicacion"] = ubicacion
            st.session_state.empresa["sector"] = sector
            st.success("✅ Datos guardados")

elif menu == "⚠️ Peligros":
    modulo_con_importar("⚠️ Gestión de Peligros", st.session_state.peligros, "peligros", ["tipo", "descripcion", "probabilidad", "severidad"])

elif menu == "✅ Plan de Acción":
    modulo_con_importar("✅ Plan de Acción", st.session_state.acciones, "acciones", ["descripcion", "responsable", "fecha_limite"])

elif menu == "👥 Trabajadores":
    modulo_con_importar("👥 Gestión de Trabajadores", st.session_state.trabajadores, "trabajadores", ["nombre", "cedula", "cargo"])

elif menu == "📝 Incidentes":
    modulo_con_importar("📝 Gestión de Incidentes", st.session_state.incidentes, "incidentes", ["descripcion", "fecha", "gravedad"])

elif menu == "📋 Matriz Legal":
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

elif menu == "🔍 Auditorías":
    st.markdown('<div class="main-header"><h1>🔍 Auditorías Internas</h1></div>', unsafe_allow_html=True)
    if "auditorias" not in st.session_state:
        st.session_state.auditorias = []
    with st.form("add_auditoria"):
        codigo = st.text_input("Código", "AUD-001")
        if st.form_submit_button("Crear"):
            st.session_state.auditorias.append({"codigo": codigo, "fecha": datetime.now().strftime("%Y-%m-%d")})
            st.success(f"✅ Auditoría {codigo} creada")

elif menu == "📚 Capacitaciones":
    modulo_con_importar("📚 Capacitaciones", st.session_state.capacitaciones, "capacitaciones", ["titulo", "fecha", "duracion"])

elif menu == "🔧 Inspecciones":
    st.markdown('<div class="main-header"><h1>🔧 Inspecciones</h1></div>', unsafe_allow_html=True)
    st.info("Módulo de inspecciones - Usa el botón Exportar/Importar")

elif menu == "🚨 Emergencias":
    st.markdown('<div class="main-header"><h1>🚨 Emergencias</h1></div>', unsafe_allow_html=True)
    st.info("Módulo de emergencias - Usa el botón Exportar/Importar")

elif menu == "📄 Documentos":
    st.markdown('<div class="main-header"><h1>📄 Gestión Documental</h1></div>', unsafe_allow_html=True)
    st.info("Módulo de documentos - Usa el botón Exportar/Importar")

elif menu == "📊 Indicadores":
    st.markdown('<div class="main-header"><h1>📊 Indicadores SST</h1></div>', unsafe_allow_html=True)
    total_trabajadores = len(st.session_state.trabajadores)
    total_incidentes = len(st.session_state.incidentes)
    tasa = (total_incidentes * 100 / total_trabajadores) if total_trabajadores > 0 else 0
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Índice de Frecuencia", f"{tasa:.1f}%")
    with col2:
        st.metric("Trabajadores", total_trabajadores)
    with col3:
        st.metric("Incidentes", total_incidentes)

elif menu == "💬 Chat IA":
    st.markdown('<div class="main-header"><h1>💬 Chat IA</h1></div>', unsafe_allow_html=True)
    
    if "chat_messages" not in st.session_state:
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

# IMPORT - 06/11/2026 08:41:31
