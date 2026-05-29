import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import plotly.express as px
import plotly.graph_objects as go
import firebase_admin
from firebase_admin import credentials, firestore
import json
import os

st.set_page_config(
    page_title="SG-SST PHVA - Gestión SST",
    page_icon="🔄",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==================== INICIALIZACIÓN ====================
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
if "username" not in st.session_state:
    st.session_state.username = None
if "fase_actual" not in st.session_state:
    st.session_state.fase_actual = 1
if "ia_messages" not in st.session_state:
    st.session_state.ia_messages = []
if "trabajadores" not in st.session_state:
    st.session_state.trabajadores = []
if "peligros" not in st.session_state:
    st.session_state.peligros = []
if "capacitaciones" not in st.session_state:
    st.session_state.capacitaciones = []
if "incidentes" not in st.session_state:
    st.session_state.incidentes = []
if "empresa" not in st.session_state:
    st.session_state.empresa = {}
if "plan_accion" not in st.session_state:
    st.session_state.plan_accion = []
if "matriz_riesgos" not in st.session_state:
    st.session_state.matriz_riesgos = []

# Datos de ejemplo
if not st.session_state.empresa:
    st.session_state.empresa = {
        "nombre": "Constructora Ejemplo SAS",
        "nit": "900.123.456-7",
        "sector": "Construcción",
        "trabajadores": 45,
        "ciudad": "Bogotá",
        "arl": "Positiva"
    }

if len(st.session_state.peligros) == 0:
    st.session_state.peligros = [
        {"id": 1, "proceso": "Obras", "peligro": "Trabajo en alturas", "probabilidad": 4, "severidad": 3, "nivel": "I", "controles": "Líneas de vida, arneses"},
        {"id": 2, "proceso": "Obras", "peligro": "Ruido excesivo", "probabilidad": 3, "severidad": 2, "nivel": "II", "controles": "Tapones auditivos"},
        {"id": 3, "proceso": "Oficinas", "peligro": "Posturas prolongadas", "probabilidad": 3, "severidad": 1, "nivel": "III", "controles": "Pausas activas"}
    ]

if len(st.session_state.plan_accion) == 0:
    st.session_state.plan_accion = [
        {"accion": "Implementar líneas de vida en todas las obras", "responsable": "Coordinador SST", "fecha": "2024-04-15", "estado": "Pendiente"},
        {"accion": "Dotar de EPP completo a todos los trabajadores", "responsable": "Almacén", "fecha": "2024-04-10", "estado": "En progreso"},
        {"accion": "Capacitación en trabajo seguro en alturas", "responsable": "Proveedor externo", "fecha": "2024-04-20", "estado": "Pendiente"}
    ]

# ==================== FIREBASE ====================
def init_firebase():
    if not firebase_admin._apps:
        try:
            if os.path.exists("firebase-credentials.json"):
                cred = credentials.Certificate("firebase-credentials.json")
                firebase_admin.initialize_app(cred)
                return True
            elif hasattr(st, "secrets") and "firebase" in st.secrets:
                firebase_config = {
                    "type": st.secrets["firebase"]["type"],
                    "project_id": st.secrets["firebase"]["project_id"],
                    "private_key_id": st.secrets["firebase"]["private_key_id"],
                    "private_key": st.secrets["firebase"]["private_key"].replace('\\n', '\n'),
                    "client_email": st.secrets["firebase"]["client_email"],
                    "client_id": st.secrets["firebase"]["client_id"],
                    "auth_uri": st.secrets["firebase"]["auth_uri"],
                    "token_uri": st.secrets["firebase"]["token_uri"]
                }
                cred = credentials.Certificate(firebase_config)
                firebase_admin.initialize_app(cred)
                return True
            return False
        except:
            return False
    return True

try:
    FIREBASE_CONECTADO = init_firebase()
    if FIREBASE_CONECTADO:
        db = firestore.client()
except:
    FIREBASE_CONECTADO = False

# ==================== FUNCIONES ====================
def calcular_nivel_riesgo(p, s):
    puntaje = p * s
    if puntaje >= 9: return "I"
    elif puntaje >= 6: return "II"
    elif puntaje >= 4: return "III"
    else: return "IV"

def calcular_progreso():
    completadas = 0
    if st.session_state.empresa.get("nombre"): completadas += 1
    if len(st.session_state.peligros) > 0: completadas += 1
    if len(st.session_state.matriz_riesgos) > 0: completadas += 1
    if len(st.session_state.plan_accion) > 0: completadas += 1
    if len(st.session_state.capacitaciones) > 0: completadas += 1
    if len(st.session_state.incidentes) > 0: completadas += 1
    return int((completadas / 6) * 100)

# ==================== CSS COMPLETO ====================
st.markdown("""
<style>
    @keyframes fadeIn { from { opacity: 0; transform: translateY(20px); } to { opacity: 1; transform: translateY(0); } }
    @keyframes slideIn { from { transform: translateX(-30px); opacity: 0; } to { transform: translateX(0); opacity: 1; } }
    @keyframes pulse { 0%,100% { transform: scale(1); } 50% { transform: scale(1.05); } }
    @keyframes glow { 0% { box-shadow: 0 0 5px rgba(102,126,234,0.5); } 100% { box-shadow: 0 0 20px rgba(102,126,234,0.8); } }
    
    .stApp { background: linear-gradient(135deg, #0f2027, #203a43, #2c5364) !important; }
    
    .main-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 20px;
        color: white;
        text-align: center;
        margin-bottom: 2rem;
        animation: slideIn 0.6s;
        box-shadow: 0 10px 30px rgba(0,0,0,0.3);
    }
    
    .fase-card {
        background: rgba(255,255,255,0.1);
        backdrop-filter: blur(10px);
        padding: 1.2rem;
        border-radius: 15px;
        margin: 0.5rem;
        text-align: center;
        transition: all 0.3s;
        animation: fadeIn 0.5s;
    }
    .fase-card:hover { transform: translateY(-5px); background: rgba(255,255,255,0.2); }
    .fase-completada { border: 2px solid #00ff00; background: rgba(0,255,0,0.1); }
    .fase-actual { border: 2px solid #ffcc00; background: rgba(255,204,0,0.15); transform: scale(1.02); animation: glow 1.5s infinite; }
    
    .metric-card {
        background: rgba(255,255,255,0.1);
        backdrop-filter: blur(10px);
        padding: 1.5rem;
        border-radius: 15px;
        text-align: center;
        color: white;
        transition: all 0.3s;
    }
    .metric-card:hover { transform: translateY(-5px); background: rgba(255,255,255,0.2); }
    
    .step-card {
        background: rgba(255,255,255,0.1);
        backdrop-filter: blur(10px);
        padding: 1rem;
        border-radius: 10px;
        margin: 0.5rem 0;
        border-left: 4px solid #667eea;
        transition: all 0.3s;
    }
    .step-card:hover { transform: translateX(10px); background: rgba(255,255,255,0.15); }
    
    .riesgo-I { background: rgba(255,0,0,0.2); border-left: 4px solid #ff0000; }
    .riesgo-II { background: rgba(255,102,0,0.2); border-left: 4px solid #ff6600; }
    .riesgo-III { background: rgba(255,204,0,0.2); border-left: 4px solid #ffcc00; }
    .riesgo-IV { background: rgba(0,255,0,0.2); border-left: 4px solid #00ff00; }
    
    [data-testid="stSidebar"] { background: linear-gradient(180deg, #0f2027, #203a43); }
    [data-testid="stSidebar"] * { color: white; }
    
    .stButton > button {
        background: linear-gradient(135deg, #667eea, #764ba2);
        color: white;
        border: none;
        border-radius: 10px;
        font-weight: bold;
        transition: all 0.3s;
        width: 100%;
    }
    .stButton > button:hover { transform: translateY(-2px); box-shadow: 0 5px 15px rgba(102,126,234,0.4); }
    
    .login-card {
        background: rgba(255,255,255,0.1);
        backdrop-filter: blur(10px);
        padding: 2rem;
        border-radius: 20px;
        text-align: center;
        animation: fadeIn 0.6s;
    }
    
    .footer {
        text-align: center;
        padding: 1rem;
        margin-top: 2rem;
        color: rgba(255,255,255,0.5);
        border-top: 1px solid rgba(255,255,255,0.1);
    }
    
    .ia-message-user {
        background: linear-gradient(135deg, #667eea, #764ba2);
        border-radius: 15px;
        padding: 1rem;
        margin: 0.5rem 0;
        color: white;
        animation: slideIn 0.3s;
    }
    .ia-message-bot {
        background: rgba(102,126,234,0.2);
        border-radius: 15px;
        padding: 1rem;
        margin: 0.5rem 0;
        border-left: 3px solid #667eea;
        animation: slideIn 0.3s;
    }
    
    .fase-badge {
        background: linear-gradient(135deg, #667eea, #764ba2);
        padding: 0.5rem 1rem;
        border-radius: 20px;
        text-align: center;
        margin-bottom: 1rem;
    }
</style>
""", unsafe_allow_html=True)

def mostrar_fases():
    fases = [
        {"num": 1, "nombre": "Diagnóstico Inicial", "icono": "🔍"},
        {"num": 2, "nombre": "Identificación de Peligros", "icono": "⚠️"},
        {"num": 3, "nombre": "Evaluación de Riesgos", "icono": "📊"},
        {"num": 4, "nombre": "Plan de Acción", "icono": "📋"},
        {"num": 5, "nombre": "Implementación", "icono": "🚀"},
        {"num": 6, "nombre": "Seguimiento y Control", "icono": "📈"}
    ]
    st.markdown("### 📍 Mapa del Proyecto - Ciclo PHVA")
    cols = st.columns(6)
    for i, fase in enumerate(fases):
        with cols[i]:
            completada = False
            if fase["num"] == 1 and st.session_state.empresa.get("nombre"): completada = True
            elif fase["num"] == 2 and len(st.session_state.peligros) > 0: completada = True
            elif fase["num"] == 3 and len(st.session_state.matriz_riesgos) > 0: completada = True
            elif fase["num"] == 4 and len(st.session_state.plan_accion) > 0: completada = True
            elif fase["num"] == 5 and len(st.session_state.capacitaciones) > 0: completada = True
            elif fase["num"] == 6 and len(st.session_state.incidentes) > 0: completada = True
            clase = "fase-actual" if fase["num"] == st.session_state.fase_actual else "fase-completada" if completada else "fase-pendiente"
            st.markdown(f'<div class="fase-card {clase}"><h2>{fase["icono"]}</h2><h4>Fase {fase["num"]}</h4><p><small>{fase["nombre"]}</small></p>{"✅" if completada else "○"}</div>', unsafe_allow_html=True)
    st.progress(calcular_progreso() / 100)
    st.caption(f"**Progreso total:** {calcular_progreso()}% completado")

def login_screen():
    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        st.markdown('<div class="login-card">', unsafe_allow_html=True)
        st.image("https://cdn-icons-png.flaticon.com/512/2917/2917995.png", width=100)
        st.markdown("<h1>🔄 SG-SST PHVA</h1>", unsafe_allow_html=True)
        st.markdown("<h3>Ciclo PHVA - 6 Fases Completas</h3>", unsafe_allow_html=True)
        with st.form("login_form"):
            username = st.text_input("👤 Usuario")
            password = st.text_input("🔒 Contraseña", type="password")
            if st.form_submit_button("🚀 Ingresar", use_container_width=True):
                if username.lower() == "admin" and password.lower() == "sst2024":
                    st.session_state.authenticated = True
                    st.session_state.username = username
                    st.rerun()
                else:
                    st.error("❌ Use: admin / sst2024")
        if FIREBASE_CONECTADO:
            st.success("☁️ Conectado a Firebase")
        st.markdown('</div>', unsafe_allow_html=True)
        st.caption("👨‍💻 Ing. Jan Benitez & Ing. Neiris Pallares")

def dashboard():
    st.markdown('<div class="main-header"><h1>📊 Dashboard SG-SST PHVA</h1><p>Planificar → Hacer → Verificar → Actuar</p></div>', unsafe_allow_html=True)
    mostrar_fases()
    st.markdown("---")
    col1, col2, col3, col4, col5, col6 = st.columns(6)
    with col1: st.markdown('<div class="metric-card"><h2>🔍</h2><h3>Fase 1</h3><p>✅' + ("✅" if st.session_state.empresa.get("nombre") else "⏳") + '</p></div>', unsafe_allow_html=True)
    with col2: st.markdown('<div class="metric-card"><h2>⚠️</h2><h3>Fase 2</h3><p>' + str(len(st.session_state.peligros)) + '</p></div>', unsafe_allow_html=True)
    with col3: st.markdown('<div class="metric-card"><h2>📊</h2><h3>Fase 3</h3><p>' + str(len(st.session_state.matriz_riesgos)) + '</p></div>', unsafe_allow_html=True)
    with col4: st.markdown('<div class="metric-card"><h2>📋</h2><h3>Fase 4</h3><p>' + str(len(st.session_state.plan_accion)) + '</p></div>', unsafe_allow_html=True)
    with col5: st.markdown('<div class="metric-card"><h2>🚀</h2><h3>Fase 5</h3><p>' + str(len(st.session_state.capacitaciones)) + '</p></div>', unsafe_allow_html=True)
    with col6: st.markdown('<div class="metric-card"><h2>📈</h2><h3>Fase 6</h3><p>' + str(len(st.session_state.incidentes)) + '</p></div>', unsafe_allow_html=True)
    st.markdown("---")
    fig = go.Figure(data=[go.Bar(x=['F1','F2','F3','F4','F5','F6'], y=[100 if st.session_state.empresa.get("nombre") else 0, min(100, len(st.session_state.peligros)*33), min(100, len(st.session_state.matriz_riesgos)*33), min(100, len(st.session_state.plan_accion)*33), min(100, len(st.session_state.capacitaciones)*33), min(100, len(st.session_state.incidentes)*33)], marker_color=['#4ECDC4','#FFB347','#45B7D1','#96CEB4','#FFEAA7','#FF6B6B'])])
    fig.update_layout(title="Progreso por Fase", paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(255,255,255,0.1)', font_color='white')
    st.plotly_chart(fig, use_container_width=True)

# ==================== FASE 1: DIAGNÓSTICO ====================
def fase1_diagnostico():
    st.markdown('<div class="main-header"><h1>🔍 Fase 1: Diagnóstico Inicial</h1><p>Registra la información de tu empresa</p></div>', unsafe_allow_html=True)
    with st.form("fase1_form"):
        col1, col2 = st.columns(2)
        with col1:
            nombre = st.text_input("🏢 Nombre de la empresa", value=st.session_state.empresa.get("nombre", ""))
            nit = st.text_input("📄 NIT", value=st.session_state.empresa.get("nit", ""))
        with col2:
            trabajadores = st.number_input("👥 Número de trabajadores", min_value=1, value=st.session_state.empresa.get("trabajadores", 45))
            ciudad = st.text_input("📍 Ciudad", value=st.session_state.empresa.get("ciudad", ""))
        if st.form_submit_button("💾 Guardar", use_container_width=True):
            st.session_state.empresa["nombre"] = nombre
            st.session_state.empresa["nit"] = nit
            st.session_state.empresa["trabajadores"] = trabajadores
            st.session_state.empresa["ciudad"] = ciudad
            st.success("✅ Fase 1 completada")
            st.session_state.fase_actual = 2
            st.rerun()

# ==================== FASE 2: PELIGROS ====================
def fase2_peligros():
    st.markdown('<div class="main-header"><h1>⚠️ Fase 2: Identificación de Peligros</h1><p>Metodología GTC-45</p></div>', unsafe_allow_html=True)
    tab1, tab2 = st.tabs(["📋 Lista de Peligros", "➕ Nuevo Peligro"])
    with tab1:
        if st.session_state.peligros:
            df = pd.DataFrame(st.session_state.peligros)
            st.dataframe(df, use_container_width=True)
            if st.button("✅ Avanzar a Fase 3", use_container_width=True):
                st.session_state.fase_actual = 3
                st.rerun()
        else:
            st.info("No hay peligros identificados")
    with tab2:
        with st.form("nuevo_peligro"):
            col1, col2 = st.columns(2)
            with col1:
                proceso = st.selectbox("Proceso", ["Administrativo", "Operativo", "Mantenimiento", "Logística"])
                peligro = st.text_area("Descripción del peligro")
                tipo = st.selectbox("Tipo", ["Biológico", "Físico", "Químico", "Psicosocial", "Ergonómico", "Mecánico"])
            with col2:
                probabilidad = st.select_slider("Probabilidad (1-4)", options=[1,2,3,4])
                severidad = st.select_slider("Severidad (1-3)", options=[1,2,3])
                nivel = calcular_nivel_riesgo(probabilidad, severidad)
                st.info(f"**Nivel calculado:** {nivel}")
            controles = st.text_area("Controles existentes")
            if st.form_submit_button("✅ Identificar", use_container_width=True):
                if peligro:
                    st.session_state.peligros.append({"proceso": proceso, "peligro": peligro, "tipo": tipo, "probabilidad": probabilidad, "severidad": severidad, "nivel": nivel, "controles": controles})
                    st.success(f"✅ Peligro nivel {nivel} identificado")
                    st.rerun()

# ==================== FASE 3: RIESGOS ====================
def fase3_riesgos():
    st.markdown('<div class="main-header"><h1>📊 Fase 3: Evaluación de Riesgos</h1><p>Análisis detallado</p></div>', unsafe_allow_html=True)
    if st.session_state.peligros:
        for p in st.session_state.peligros:
            riesgo_clase = f"riesgo-{p['nivel']}"
            st.markdown(f'<div class="step-card {riesgo_clase}"><h4>📍 {p["peligro"]}</h4><p>Proceso: {p["proceso"]} | Prob: {p["probabilidad"]} | Sev: {p["severidad"]}</p><p><strong>Nivel: {p["nivel"]}</strong></p></div>', unsafe_allow_html=True)
        if st.button("✅ Completar Evaluación", use_container_width=True):
            st.session_state.matriz_riesgos = st.session_state.peligros.copy()
            st.session_state.fase_actual = 4
            st.success("¡Fase 3 completada!")
            st.rerun()
    else:
        st.warning("⚠️ Primero identifica peligros en la Fase 2")

# ==================== FASE 4: PLAN DE ACCIÓN ====================
def fase4_plan_accion():
    st.markdown('<div class="main-header"><h1>📋 Fase 4: Plan de Acción</h1><p>Define acciones correctivas</p></div>', unsafe_allow_html=True)
    tab1, tab2 = st.tabs(["📋 Plan Actual", "➕ Nueva Acción"])
    with tab1:
        if st.session_state.plan_accion:
            df = pd.DataFrame(st.session_state.plan_accion)
            st.dataframe(df, use_container_width=True)
            if st.button("✅ Completar Plan", use_container_width=True):
                st.session_state.fase_actual = 5
                st.success("¡Fase 4 completada!")
                st.rerun()
    with tab2:
        with st.form("nueva_accion"):
            accion = st.text_area("Acción correctiva")
            responsable = st.text_input("Responsable")
            fecha = st.date_input("Fecha límite", datetime.now() + timedelta(days=30))
            if st.form_submit_button("Agregar", use_container_width=True):
                if accion:
                    st.session_state.plan_accion.append({"accion": accion, "responsable": responsable, "fecha": str(fecha), "estado": "Pendiente"})
                    st.success("✅ Acción agregada")
                    st.rerun()

# ==================== FASE 5: IMPLEMENTACIÓN ====================
def fase5_implementacion():
    st.markdown('<div class="main-header"><h1>🚀 Fase 5: Implementación</h1><p>Ejecuta el plan de acción</p></div>', unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("📚 Capacitaciones")
        with st.form("nueva_capacitacion"):
            tema = st.text_input("Tema")
            fecha = st.date_input("Fecha", datetime.now() + timedelta(days=7))
            if st.form_submit_button("Programar"):
                if tema:
                    st.session_state.capacitaciones.append({"tema": tema, "fecha": str(fecha), "estado": "Programada"})
                    st.success("✅ Programada")
                    st.rerun()
    with col2:
        st.subheader("✅ Ejecución")
        if len(st.session_state.capacitaciones) >= 1:
            if st.button("✅ Completar Implementación"):
                st.session_state.fase_actual = 6
                st.success("¡Fase 5 completada!")
                st.rerun()

# ==================== FASE 6: SEGUIMIENTO ====================
def fase6_seguimiento():
    st.markdown('<div class="main-header"><h1>📈 Fase 6: Seguimiento y Control</h1><p>Monitorea indicadores</p></div>', unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("📊 Indicadores")
        st.metric("Capacitaciones", len(st.session_state.capacitaciones))
    with col2:
        st.subheader("📋 Incidentes")
        with st.form("nuevo_incidente"):
            descripcion = st.text_area("Descripción")
            if st.form_submit_button("Reportar"):
                if descripcion:
                    st.session_state.incidentes.append({"descripcion": descripcion, "fecha": str(datetime.now())})
                    st.success("✅ Reportado")
                    st.rerun()

# ==================== ASISTENTE IA ====================
def asistente_ia():
    st.markdown('<div class="main-header"><h1>🤖 Asistente IA</h1><p>Experto virtual en SST</p></div>', unsafe_allow_html=True)
    mostrar_fases()
    if not st.session_state.ia_messages:
        st.session_state.ia_messages = [{"role": "assistant", "content": f"**🤖 Hola!** Estamos en Fase {st.session_state.fase_actual}. Progreso: {calcular_progreso()}%. ¿En qué te ayudo?"}]
    for msg in st.session_state.ia_messages:
        if msg["role"] == "user":
            st.markdown(f'<div class="ia-message-user">👤 {msg["content"]}</div>', unsafe_allow_html=True)
        else:
            st.markdown(f'<div class="ia-message-bot">🤖 {msg["content"]}</div>', unsafe_allow_html=True)
    if prompt := st.chat_input("Consulta sobre SST..."):
        st.session_state.ia_messages.append({"role": "user", "content": prompt})
        respuesta = f"**Progreso:** {calcular_progreso()}% - Fase {st.session_state.fase_actual}. Consulta recibida: '{prompt}'"
        st.session_state.ia_messages.append({"role": "assistant", "content": respuesta})
        st.rerun()

# ==================== MAIN ====================
if not st.session_state.authenticated:
    login_screen()
else:
    with st.sidebar:
        st.image("https://cdn-icons-png.flaticon.com/512/2917/2917995.png", width=60)
        st.markdown("### 🔄 SG-SST PHVA")
        st.markdown(f"**👤** {st.session_state.username}")
        st.markdown("---")
        fases_nombres = {1:"🔍 Diagnóstico", 2:"⚠️ Peligros", 3:"📊 Riesgos", 4:"📋 Plan", 5:"🚀 Implementación", 6:"📈 Seguimiento"}
        st.markdown(f'<div class="fase-badge"><strong>📍 FASE ACTUAL</strong><br>{fases_nombres[st.session_state.fase_actual]}</div>', unsafe_allow_html=True)
        st.progress(calcular_progreso() / 100)
        st.markdown("---")
        menu = st.radio("📋 Módulos", ["📊 Dashboard", "🔍 Fase 1: Diagnóstico", "⚠️ Fase 2: Peligros", "📊 Fase 3: Riesgos", "📋 Fase 4: Plan de Acción", "🚀 Fase 5: Implementación", "📈 Fase 6: Seguimiento", "🤖 Asistente IA"])
        st.markdown("---")
        st.caption("👨‍💻 Ing. Jan Benitez & Ing. Neiris Pallares")
        if st.button("🚪 Cerrar Sesión", use_container_width=True):
            st.session_state.authenticated = False
            st.rerun()
    
    if menu == "📊 Dashboard":
        dashboard()
    elif menu == "🔍 Fase 1: Diagnóstico":
        fase1_diagnostico()
    elif menu == "⚠️ Fase 2: Peligros":
        fase2_peligros()
    elif menu == "📊 Fase 3: Riesgos":
        fase3_riesgos()
    elif menu == "📋 Fase 4: Plan de Acción":
        fase4_plan_accion()
    elif menu == "🚀 Fase 5: Implementación":
        fase5_implementacion()
    elif menu == "📈 Fase 6: Seguimiento":
        fase6_seguimiento()
    elif menu == "🤖 Asistente IA":
        asistente_ia()

st.markdown('<div class="footer"><p>SG-SST PHVA - Sistema de Gestión SST © 2024</p></div>', unsafe_allow_html=True)
