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

# ==================== CSS COMPLETO CON DISEÑO ORIGINAL ====================
st.markdown("""
<style>
    /* Animaciones */
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(20px); }
        to { opacity: 1; transform: translateY(0); }
    }
    @keyframes slideIn {
        from { transform: translateX(-30px); opacity: 0; }
        to { transform: translateX(0); opacity: 1; }
    }
    @keyframes pulse {
        0%, 100% { transform: scale(1); }
        50% { transform: scale(1.05); }
    }
    @keyframes glow {
        0% { box-shadow: 0 0 5px rgba(102,126,234,0.5); }
        100% { box-shadow: 0 0 20px rgba(102,126,234,0.8); }
    }
    
    /* Fondo principal */
    .stApp {
        background: linear-gradient(135deg, #0f2027, #203a43, #2c5364) !important;
    }
    
    /* Header principal */
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
    
    .main-header h1 {
        font-size: 2.5rem;
        margin: 0;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.2);
    }
    
    .main-header p {
        font-size: 1.1rem;
        opacity: 0.9;
    }
    
    /* Tarjetas de fase */
    .fase-card {
        background: rgba(255,255,255,0.1);
        backdrop-filter: blur(10px);
        padding: 1.2rem;
        border-radius: 15px;
        margin: 0.5rem;
        text-align: center;
        transition: all 0.3s;
        cursor: pointer;
        animation: fadeIn 0.5s;
    }
    
    .fase-card:hover {
        transform: translateY(-5px);
        background: rgba(255,255,255,0.2);
        box-shadow: 0 10px 25px rgba(0,0,0,0.2);
    }
    
    .fase-completada {
        border: 2px solid #00ff00;
        background: rgba(0,255,0,0.1);
    }
    
    .fase-actual {
        border: 2px solid #ffcc00;
        background: rgba(255,204,0,0.15);
        transform: scale(1.02);
        animation: glow 1.5s infinite;
    }
    
    .fase-pendiente {
        border: 2px solid rgba(255,255,255,0.3);
    }
    
    /* Tarjetas de métricas */
    .metric-card {
        background: rgba(255,255,255,0.1);
        backdrop-filter: blur(10px);
        padding: 1.5rem;
        border-radius: 15px;
        text-align: center;
        color: white;
        transition: all 0.3s;
        cursor: pointer;
        animation: fadeIn 0.5s;
    }
    
    .metric-card:hover {
        transform: translateY(-5px);
        background: rgba(255,255,255,0.2);
        box-shadow: 0 10px 25px rgba(0,0,0,0.2);
    }
    
    .metric-card h2 {
        font-size: 2rem;
        margin: 0;
    }
    
    /* Tarjetas de pasos */
    .step-card {
        background: rgba(255,255,255,0.1);
        backdrop-filter: blur(10px);
        padding: 1rem;
        border-radius: 10px;
        margin: 0.5rem 0;
        border-left: 4px solid #667eea;
        transition: all 0.3s;
    }
    
    .step-card:hover {
        transform: translateX(10px);
        background: rgba(255,255,255,0.15);
    }
    
    /* Tarjetas de riesgo */
    .riesgo-I {
        background: rgba(255,0,0,0.2);
        border-left: 4px solid #ff0000;
    }
    .riesgo-II {
        background: rgba(255,102,0,0.2);
        border-left: 4px solid #ff6600;
    }
    .riesgo-III {
        background: rgba(255,204,0,0.2);
        border-left: 4px solid #ffcc00;
    }
    .riesgo-IV {
        background: rgba(0,255,0,0.2);
        border-left: 4px solid #00ff00;
    }
    
    /* Sidebar */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0f2027, #203a43);
    }
    
    [data-testid="stSidebar"] * {
        color: white;
    }
    
    /* Botones */
    .stButton > button {
        background: linear-gradient(135deg, #667eea, #764ba2);
        color: white;
        border: none;
        border-radius: 10px;
        font-weight: bold;
        transition: all 0.3s;
        width: 100%;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 5px 15px rgba(102,126,234,0.4);
    }
    
    /* Login */
    .login-card {
        background: rgba(255,255,255,0.1);
        backdrop-filter: blur(10px);
        padding: 2rem;
        border-radius: 20px;
        text-align: center;
        animation: fadeIn 0.6s;
    }
    
    /* Footer */
    .footer {
        text-align: center;
        padding: 1rem;
        margin-top: 2rem;
        color: rgba(255,255,255,0.5);
        border-top: 1px solid rgba(255,255,255,0.1);
    }
    
    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }
    
    .stTabs [data-baseweb="tab"] {
        background: rgba(255,255,255,0.1);
        border-radius: 10px;
        padding: 0.5rem 1rem;
    }
    
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #667eea, #764ba2);
    }
    
    /* Expander */
    .streamlit-expanderHeader {
        background: rgba(255,255,255,0.1);
        border-radius: 10px;
    }
    
    /* Dataframe */
    .dataframe {
        background: rgba(255,255,255,0.05) !important;
        color: white !important;
    }
    
    /* Mensajes IA */
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
    
    /* Badge de fase */
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
            st.markdown(f'''
            <div class="fase-card {clase}">
                <h2>{fase["icono"]}</h2>
                <h4>Fase {fase["num"]}</h4>
                <p><small>{fase["nombre"]}</small></p>
                <h3>{"✅" if completada else "○"}</h3>
            </div>
            ''', unsafe_allow_html=True)
    st.progress(calcular_progreso() / 100)
    st.caption(f"**Progreso total:** {calcular_progreso()}% completado")

def login_screen():
    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        st.markdown('<div class="login-card">', unsafe_allow_html=True)
        st.image("https://cdn-icons-png.flaticon.com/512/2917/2917995.png", width=100)
        st.markdown("<h1>🔄 SG-SST PHVA</h1>", unsafe_allow_html=True)
        st.markdown("<h3>Ciclo PHVA - 6 Fases Completas</h3>", unsafe_allow_html=True)
        st.markdown("<p>Sistema de Gestión de Seguridad y Salud en el Trabajo</p>", unsafe_allow_html=True)
        
        with st.form("login_form"):
            username = st.text_input("👤 Usuario")
            password = st.text_input("🔒 Contraseña", type="password")
            if st.form_submit_button("🚀 Ingresar al Sistema", use_container_width=True):
                if username.lower() == "admin" and password.lower() == "sst2024":
                    st.session_state.authenticated = True
                    st.session_state.username = username
                    st.rerun()
                else:
                    st.error("❌ Credenciales incorrectas")
                    st.info("📝 Use: **admin** / **sst2024**")
        
        if FIREBASE_CONECTADO:
            st.success("☁️ Conectado a Firebase Cloud")
        else:
            st.info("📡 Modo Local - Datos guardados localmente")
        
        st.markdown('</div>', unsafe_allow_html=True)
        st.markdown("---")
        st.caption("👨‍💻 Desarrolladores: Ing. Jan Benitez & Ing. Neiris Pallares")

def dashboard():
    st.markdown('''
    <div class="main-header">
        <h1>📊 Dashboard SG-SST PHVA</h1>
        <p>Planificar → Hacer → Verificar → Actuar</p>
    </div>
    ''', unsafe_allow_html=True)
    
    mostrar_fases()
    st.markdown("---")
    
    col1, col2, col3, col4, col5, col6 = st.columns(6)
    
    with col1:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.markdown("<h2>🔍</h2>", unsafe_allow_html=True)
        st.metric("Fase 1", "✅" if st.session_state.empresa.get("nombre") else "⏳", "Diagnóstico")
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.markdown("<h2>⚠️</h2>", unsafe_allow_html=True)
        st.metric("Fase 2", f"{len(st.session_state.peligros)}", "Peligros")
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col3:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.markdown("<h2>📊</h2>", unsafe_allow_html=True)
        st.metric("Fase 3", f"{len(st.session_state.matriz_riesgos)}", "Riesgos")
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col4:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.markdown("<h2>📋</h2>", unsafe_allow_html=True)
        st.metric("Fase 4", f"{len(st.session_state.plan_accion)}", "Acciones")
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col5:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.markdown("<h2>🚀</h2>", unsafe_allow_html=True)
        st.metric("Fase 5", f"{len(st.session_state.capacitaciones)}", "Capacitaciones")
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col6:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.markdown("<h2>📈</h2>", unsafe_allow_html=True)
        st.metric("Fase 6", f"{len(st.session_state.incidentes)}", "Incidentes")
        st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Gráfico de progreso
    fig = go.Figure(data=[go.Bar(
        x=['Fase 1', 'Fase 2', 'Fase 3', 'Fase 4', 'Fase 5', 'Fase 6'],
        y=[
            100 if st.session_state.empresa.get("nombre") else 0,
            min(100, len(st.session_state.peligros) * 33),
            min(100, len(st.session_state.matriz_riesgos) * 33),
            min(100, len(st.session_state.plan_accion) * 33),
            min(100, len(st.session_state.capacitaciones) * 33),
            min(100, len(st.session_state.incidentes) * 33)
        ],
        marker_color=['#4ECDC4', '#FFB347', '#45B7D1', '#96CEB4', '#FFEAA7', '#FF6B6B'],
        text_auto=True
    )])
    fig.update_layout(
        title="Progreso por Fase del Proyecto",
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(255,255,255,0.1)',
        font_color='white',
        xaxis_title="Fases del Ciclo PHVA",
        yaxis_title="Porcentaje Completado (%)",
        height=500
    )
    st.plotly_chart(fig, use_container_width=True)
    
    st.markdown("---")
    
    # Recomendación
    fases_recomendaciones = [
        "🎯 Comienza registrando la información de tu empresa en la Fase 1",
        "⚠️ Identifica los peligros por proceso según metodología GTC-45",
        "📊 Evalúa probabilidad (1-4) y severidad (1-3) de cada peligro",
        "📋 Define acciones correctivas con responsables y fechas límite",
        "🚀 Programa capacitaciones y ejecuta el plan de acción",
        "📈 Monitorea indicadores y reporta incidentes oportunamente"
    ]
    st.info(f"**🎯 Próxima acción recomendada:** {fases_recomendaciones[st.session_state.fase_actual-1]}")

# ==================== FASES COMPLETAS ====================

def fase1_diagnostico():
    st.markdown('''
    <div class="main-header">
        <h1>🔍 Fase 1: Diagnóstico Inicial</h1>
        <p>Registra la información básica de tu empresa</p>
    </div>
    ''', unsafe_allow_html=True)
    
    with st.form("fase1_form"):
        col1, col2 = st.columns(2)
        with col1:
            nombre = st.text_input("🏢 Nombre de la empresa", value=st.session_state.empresa.get("nombre", ""))
            nit = st.text_input("📄 NIT", value=st.session_state.empresa.get("nit", ""))
            sector = st.selectbox("🏭 Sector económico", 
                                 ["Construcción", "Manufactura", "Servicios", "Minería", "Salud", "Educación", "Comercio"],
                                 index=["Construcción", "Manufactura", "Servicios", "Minería", "Salud", "Educación", "Comercio"].index(st.session_state.empresa.get("sector", "Construcción")))
        with col2:
            trabajadores = st.number_input("👥 Número de trabajadores", min_value=1, value=st.session_state.empresa.get("trabajadores", 45))
            ciudad = st.text_input("📍 Ciudad", value=st.session_state.empresa.get("ciudad", ""))
            arl = st.selectbox("🛡️ ARL", ["Positiva", "Sura", "Colpatria", "Bolívar"],
                              index=["Positiva", "Sura", "Colpatria", "Bolívar"].index(st.session_state.empresa.get("arl", "Positiva")))
        
        if st.form_submit_button("💾 Guardar Diagnóstico", use_container_width=True):
            st.session_state.empresa = {
                "nombre": nombre,
                "nit": nit,
                "sector": sector,
                "trabajadores": trabajadores,
                "ciudad": ciudad,
                "arl": arl
            }
            st.success("✅ ¡Fase 1 completada! Información guardada correctamente.")
            st.balloons()
            st.session_state.fase_actual = 2
            st.rerun()
    
    if st.session_state.empresa.get("nombre"):
        st.markdown("---")
        st.subheader("📋 Información actual de la empresa")
        col1, col2 = st.columns(2)
        with col1:
            st.write(f"**🏢 Empresa:** {st.session_state.empresa.get('nombre')}")
            st.write(f"**📄 NIT:** {st.session_state.empresa.get('nit')}")
            st.write(f"**🏭 Sector:** {st.session_state.empresa.get('sector')}")
        with col2:
            st.write(f"**👥 Trabajadores:** {st.session_state.empresa.get('trabajadores')}")
            st.write(f"**📍 Ciudad:** {st.session_state.empresa.get('ciudad')}")
            st.write(f"**🛡️ ARL:** {st.session_state.empresa.get('arl')}")

def fase2_peligros():
    st.markdown('''
    <div class="main-header">
        <h1>⚠️ Fase 2: Identificación de Peligros</h1>
        <p>Metodología GTC-45 - Identifica y clasifica los peligros</p>
    </div>
    ''', unsafe_allow_html=True)
    
    tab1, tab2 = st.tabs(["📋 Lista de Peligros Identificados", "➕ Identificar Nuevo Peligro"])
    
    with tab1:
        if st.session_state.peligros:
            df = pd.DataFrame(st.session_state.peligros)
            st.dataframe(df, use_container_width=True)
            
            # Resumen por niveles
            st.subheader("📊 Resumen por Nivel de Riesgo")
            col1, col2, col3, col4 = st.columns(4)
            niveles = pd.DataFrame(st.session_state.peligros)['nivel'].value_counts()
            col1.metric("🔴 Nivel I", niveles.get("I", 0), "Riesgo Extremo")
            col2.metric("🟠 Nivel II", niveles.get("II", 0), "Riesgo Alto")
            col3.metric("🟡 Nivel III", niveles.get("III", 0), "Riesgo Medio")
            col4.metric("🟢 Nivel IV", niveles.get("IV", 0), "Riesgo Bajo")
            
            st.markdown("---")
            if st.button("✅ Avanzar a Fase 3 - Evaluación de Riesgos", use_container_width=True):
                st.session_state.fase_actual = 3
                st.rerun()
        else:
            st.info("📌 No hay peligros identificados. Usa el formulario para comenzar.")
    
    with tab2:
        with st.form("nuevo_peligro"):
            col1, col2 = st.columns(2)
            with col1:
                proceso = st.selectbox("📌 Proceso/Área", ["Administrativo", "Operativo", "Mantenimiento", "Logística", "Oficinas", "Campo"])
                peligro = st.text_area("📝 Descripción del peligro", height=80, placeholder="Ej: Trabajo en alturas, Ruido excesivo, Posturas forzadas...")
                tipo = st.selectbox("🏷️ Tipo de Peligro", 
                                   ["Biológico", "Físico (Ruido)", "Físico (Iluminación)", "Físico (Temperatura)",
                                    "Químico", "Psicosocial", "Ergonómico", "Mecánico", "Eléctrico", "Locativo"])
            with col2:
                st.markdown("#### 📊 Evaluación GTC-45")
                probabilidad = st.select_slider("Probabilidad", options=[1,2,3,4],
                                               format_func=lambda x: {1:"Baja",2:"Media",3:"Alta",4:"Muy Alta"}[x])
                severidad = st.select_slider("Severidad", options=[1,2,3],
                                            format_func=lambda x: {1:"Leve",2:"Grave",3:"Mortal"}[x])
                nivel = calcular_nivel_riesgo(probabilidad, severidad)
                
                niveles_texto = {
                    "I": "🔴 Nivel I - Riesgo Extremo - Intervención inmediata",
                    "II": "🟠 Nivel II - Riesgo Alto - Corregir ASAP",
                    "III": "🟡 Nivel III - Riesgo Medio - Mejorar",
                    "IV": "🟢 Nivel IV - Riesgo Bajo - Mantener"
                }
                st.info(f"**Nivel de Riesgo calculado:** {niveles_texto[nivel]}")
            
            controles = st.text_area("🛡️ Controles existentes", height=80, placeholder="Describir las barreras de control actuales...")
            responsable = st.text_input("👤 Responsable del control")
            
            if st.form_submit_button("✅ Identificar Peligro", use_container_width=True):
                if peligro:
                    nuevo = {
                        "id": len(st.session_state.peligros)+1,
                        "proceso": proceso,
                        "peligro": peligro,
                        "tipo": tipo,
                        "probabilidad": probabilidad,
                        "severidad": severidad,
                        "nivel": nivel,
                        "controles": controles,
                        "responsable": responsable,
                        "fecha": datetime.now().strftime("%Y-%m-%d")
                    }
                    st.session_state.peligros.append(nuevo)
                    st.success(f"✅ Peligro nivel {nivel} identificado correctamente")
                    st.rerun()
                else:
                    st.error("❌ Complete la descripción del peligro")

def fase3_riesgos():
    st.markdown('''
    <div class="main-header">
        <h1>📊 Fase 3: Evaluación de Riesgos</h1>
        <p>Análisis detallado de probabilidad y severidad</p>
    </div>
    ''', unsafe_allow_html=True)
    
    if st.session_state.peligros:
        st.subheader("📋 Matriz de Riesgos Evaluados")
        for p in st.session_state.peligros:
            riesgo_clase = f"riesgo-{p['nivel']}"
            st.markdown(f'''
            <div class="step-card {riesgo_clase}">
                <h4>📍 {p['peligro']}</h4>
                <p><strong>Proceso:</strong> {p['proceso']} | <strong>Tipo:</strong> {p.get('tipo', 'No especificado')}</p>
                <p><strong>Evaluación:</strong> Probabilidad {p['probabilidad']}/4 × Severidad {p['severidad']}/3 = <strong>Nivel {p['nivel']}</strong></p>
                <p><strong>Controles actuales:</strong> {p['controles']}</p>
                <small>Responsable: {p.get('responsable', 'No asignado')}</small>
            </div>
            ''', unsafe_allow_html=True)
        
        st.markdown("---")
        if st.button("✅ Completar Evaluación de Riesgos", use_container_width=True):
            st.session_state.matriz_riesgos = st.session_state.peligros.copy()
            st.session_state.fase_actual = 4
            st.success("¡Fase 3 completada! Ahora define el plan de acción.")
            st.rerun()
    else:
        st.warning("⚠️ Primero identifica peligros en la Fase 2")

def fase4_plan_accion():
    st.markdown('''
    <div class="main-header">
        <h1>📋 Fase 4: Plan de Acción</h1>
        <p>Define acciones correctivas con responsables y fechas</p>
    </div>
    ''', unsafe_allow_html=True)
    
    tab1, tab2 = st.tabs(["📋 Plan de Acción Actual", "➕ Nueva Acción Correctiva"])
    
    with tab1:
        if st.session_state.plan_accion:
            df = pd.DataFrame(st.session_state.plan_accion)
            st.dataframe(df, use_container_width=True)
            
            st.markdown("---")
            if st.button("✅ Completar Plan de Acción", use_container_width=True):
                st.session_state.fase_actual = 5
                st.success("¡Fase 4 completada! Ahora implementa las acciones.")
                st.rerun()
        else:
            st.info("📌 No hay acciones en el plan")
    
    with tab2:
        with st.form("nueva_accion"):
            accion = st.text_area("📝 Acción correctiva", height=80, placeholder="Describir la acción a realizar...")
            responsable = st.text_input("👤 Responsable")
            fecha = st.date_input("📅 Fecha límite", datetime.now() + timedelta(days=30))
            estado = st.selectbox("📊 Estado", ["Pendiente", "En progreso", "Completada"])
            
            if st.form_submit_button("➕ Agregar Acción al Plan", use_container_width=True):
                if accion:
                    st.session_state.plan_accion.append({
                        "accion": accion,
                        "responsable": responsable,
                        "fecha": str(fecha),
                        "estado": estado
                    })
                    st.success("✅ Acción agregada al plan correctamente")
                    st.rerun()
                else:
                    st.error("❌ Complete la descripción de la acción")

def fase5_implementacion():
    st.markdown('''
    <div class="main-header">
        <h1>🚀 Fase 5: Implementación</h1>
        <p>Ejecuta el plan de acción y programa capacitaciones</p>
    </div>
    ''', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📚 Capacitaciones Programadas")
        with st.form("nueva_capacitacion"):
            tema = st.text_input("Tema de capacitación")
            fecha = st.date_input("Fecha programada", datetime.now() + timedelta(days=7))
            if st.form_submit_button("📅 Programar Capacitación", use_container_width=True):
                if tema:
                    st.session_state.capacitaciones.append({
                        "tema": tema,
                        "fecha": str(fecha),
                        "estado": "Programada",
                        "fecha_registro": datetime.now().strftime("%Y-%m-%d")
                    })
                    st.success("✅ Capacitación programada exitosamente")
                    st.rerun()
        
        if st.session_state.capacitaciones:
            st.markdown("---")
            for c in st.session_state.capacitaciones:
                st.info(f"📅 **{c['tema']}** - {c['fecha']}")
    
    with col2:
        st.subheader("✅ Ejecución del Plan de Acción")
        for i, accion in enumerate(st.session_state.plan_accion):
            if st.checkbox(f"✓ {accion['accion'][:60]}...", key=f"check_{i}"):
                st.session_state.plan_accion[i]['estado'] = "Completada"
                st.success(f"✅ Acción completada: {accion['accion'][:50]}")
        
        st.markdown("---")
        if len(st.session_state.capacitaciones) >= 1:
            if st.button("✅ Completar Fase de Implementación", use_container_width=True):
                st.session_state.fase_actual = 6
                st.success("¡Fase 5 completada! Ahora monitorea los resultados.")
                st.rerun()

def fase6_seguimiento():
    st.markdown('''
    <div class="main-header">
        <h1>📈 Fase 6: Seguimiento y Control</h1>
        <p>Monitorea indicadores y reporta incidentes</p>
    </div>
    ''', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📊 Indicadores Clave de Gestión")
        
        # Calcular indicadores
        total_peligros = len(st.session_state.peligros)
        riesgos_criticos = sum(1 for p in st.session_state.peligros if p.get('nivel') in ['I', 'II'])
        acciones_completadas = sum(1 for a in st.session_state.plan_accion if a.get('estado') == 'Completada')
        
        col_a, col_b = st.columns(2)
        with col_a:
            st.markdown('<div class="metric-card">', unsafe_allow_html=True)
            st.metric("⚠️ Peligros", total_peligros, "Identificados")
            st.markdown('</div>', unsafe_allow_html=True)
            
            st.markdown('<div class="metric-card">', unsafe_allow_html=True)
            st.metric("🔴 Riesgos Críticos", riesgos_criticos, "Nivel I y II")
            st.markdown('</div>', unsafe_allow_html=True)
        
        with col_b:
            st.markdown('<div class="metric-card">', unsafe_allow_html=True)
            st.metric("📋 Acciones", f"{acciones_completadas}/{len(st.session_state.plan_accion)}", "Completadas")
            st.markdown('</div>', unsafe_allow_html=True)
            
            st.markdown('<div class="metric-card">', unsafe_allow_html=True)
            st.metric("📚 Capacitaciones", len(st.session_state.capacitaciones), "Programadas")
            st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.subheader("📋 Registro de Incidentes")
        with st.form("nuevo_incidente"):
            tipo = st.selectbox("Tipo de incidente", ["Accidente de trabajo", "Incidente sin lesión", "Enfermedad laboral", "Acto inseguro", "Condición insegura", "Casi accidente"])
            descripcion = st.text_area("Descripción detallada", height=100)
            if st.form_submit_button("📋 Reportar Incidente", use_container_width=True):
                if descripcion:
                    st.session_state.incidentes.append({
                        "tipo": tipo,
                        "descripcion": descripcion,
                        "fecha": datetime.now().strftime("%Y-%m-%d %H:%M"),
                        "estado": "Registrado"
                    })
                    st.success("✅ Incidente reportado correctamente")
                    st.rerun()
        
        if st.session_state.incidentes:
            st.markdown("---")
            for i in st.session_state.incidentes:
                st.warning(f"⚠️ **{i['tipo']}** - {i['fecha']}\n\n{i['descripcion'][:100]}...")
    
    progreso_total = calcular_progreso()
    if progreso_total >= 90:
        st.balloons()
        st.success("🎉 ¡FELICITACIONES! Has completado todas las fases del ciclo PHVA")
        st.balloons()

def asistente_ia():
    st.markdown('''
    <div class="main-header">
        <h1>🤖 Asistente IA - Experto en SST</h1>
        <p>Tu asistente virtual especializado en Seguridad y Salud en el Trabajo</p>
    </div>
    ''', unsafe_allow_html=True)
    
    mostrar_fases()
    st.markdown("---")
    
    if not st.session_state.ia_messages:
        st.session_state.ia_messages = [{
            "role": "assistant",
            "content": f"""**🤖 ¡Hola! Soy tu Asistente IA especializado en SST**

Estamos en **Fase {st.session_state.fase_actual}** del proyecto.
**Progreso actual:** {calcular_progreso()}% completado

Puedo ayudarte con:

📌 **Fase 1:** Registrar información de la empresa
📌 **Fase 2:** Identificar peligros según GTC-45
📌 **Fase 3:** Evaluar probabilidad y severidad
📌 **Fase 4:** Crear plan de acción
📌 **Fase 5:** Programar capacitaciones
📌 **Fase 6:** Monitorear indicadores

**¿En qué puedo ayudarte hoy?**"""
        }]
    
    for msg in st.session_state.ia_messages:
        if msg["role"] == "user":
            st.markdown(f'<div class="ia-message-user">👤 {msg["content"]}</div>', unsafe_allow_html=True)
        else:
            st.markdown(f'<div class="ia-message-bot">🤖 {msg["content"]}</div>', unsafe_allow_html=True)
    
    if prompt := st.chat_input("Escribe tu consulta sobre SST..."):
        st.session_state.ia_messages.append({"role": "user", "content": prompt})
        
        prompt_lower = prompt.lower()
        
        # Respuestas contextuales
        if any(word in prompt_lower for word in ["fase", "progreso", "avance"]):
            respuesta = f"**📊 Progreso del proyecto:** {calcular_progreso()}% completado\n\nEstamos en **Fase {st.session_state.fase_actual}**. Recomiendo continuar con las actividades de esta fase para avanzar al siguiente nivel."
        
        elif any(word in prompt_lower for word in ["peligro", "riesgo", "gtc", "identificar"]):
            respuesta = """**⚠️ Identificación de Peligros según GTC-45**

**Pasos a seguir:**
1. Identificar actividades de la empresa
2. Listar peligros asociados a cada actividad
3. Clasificar por tipo (físico, químico, biológico, etc.)
4. Evaluar probabilidad (1-4) y severidad (1-3)
5. Calcular nivel de riesgo (I, II, III, IV)

**¿Necesitas ayuda con algún peligro específico?"""
        
        elif any(word in prompt_lower for word in ["capacitacion", "curso", "entrenamiento"]):
            respuesta = """**📚 Capacitaciones Obligatorias SST**

**Temas requeridos anualmente:**
- Sistema de Gestión de Seguridad y Salud en el Trabajo (8 horas)
- Prevención de riesgos laborales (8 horas)
- Manejo de extintores y emergencias (4 horas)
- Primeros auxilios básicos (8 horas)
- Trabajo en alturas (si aplica - 40 horas)

**¿Deseas programar alguna capacitación?"""
        
        elif any(word in prompt_lower for word in ["incidente", "accidente", "reporte"]):
            respuesta = """**📋 Reporte de Incidentes**

**Información requerida para reportar:**
- Tipo de incidente (accidente, incidente, casi accidente)
- Fecha y hora del evento
- Descripción detallada
- Causas identificadas
- Acciones tomadas

**Plazo máximo para reportar:** 24 horas hábiles

**¿Deseas reportar un incidente ahora?"""
        
        elif any(word in prompt_lower for word in ["norma", "ley", "decreto", "legal"]):
            respuesta = """**📜 Normativa SST Aplicable**

**Principales disposiciones legales:**
- **Ley 1562 de 2012:** Sistema General de Riesgos Laborales
- **Decreto 1072 de 2015:** Único Reglamentario del Sector Trabajo
- **Resolución 0312 de 2019:** Estándares mínimos SST
- **GTC-45:** Guía para identificación de peligros

**¿Necesitas información específica sobre alguna norma?"""
        
        else:
            respuesta = f"""**🤖 Asistente SST**

He recibido tu consulta: "{prompt}"

**¿Te ayudo con alguno de estos temas?**
- 📊 Estado del proyecto y fases
- ⚠️ Identificación de peligros GTC-45
- 📚 Capacitaciones obligatorias
- 📋 Reporte de incidentes
- 📜 Normativa SST aplicable

**Escribe el tema que te interesa y con gusto te ayudo.**"""
        
        st.session_state.ia_messages.append({"role": "assistant", "content": respuesta})
        st.rerun()

# ==================== MAIN ====================
if not st.session_state.authenticated:
    login_screen()
else:
    with st.sidebar:
        st.image("https://cdn-icons-png.flaticon.com/512/2917/2917995.png", width=60)
        st.markdown("### 🔄 SG-SST PHVA")
        st.markdown(f"**👤 Usuario:** {st.session_state.username}")
        
        if FIREBASE_CONECTADO:
            st.success("☁️ Cloud Sync")
        
        st.markdown("---")
        
        fases_nombres = {1:"🔍 Diagnóstico", 2:"⚠️ Peligros", 3:"📊 Riesgos", 4:"📋 Plan", 5:"🚀 Implementación", 6:"📈 Seguimiento"}
        
        st.markdown(f'''
        <div class="fase-badge">
            <strong>📍 FASE ACTUAL</strong><br>
            {fases_nombres[st.session_state.fase_actual]}
        </div>
        ''', unsafe_allow_html=True)
        
        st.progress(calcular_progreso() / 100)
        st.caption(f"**{calcular_progreso()}% completado**")
        
        st.markdown("---")
        
        menu = st.radio(
            "📋 **Módulos del Sistema**",
            [
                "📊 Dashboard",
                "🔍 Fase 1: Diagnóstico",
                "⚠️ Fase 2: Peligros GTC-45",
                "📊 Fase 3: Evaluación de Riesgos",
                "📋 Fase 4: Plan de Acción",
                "🚀 Fase 5: Implementación",
                "📈 Fase 6: Seguimiento",
                "🤖 Asistente IA"
            ],
            index=0
        )
        
        st.markdown("---")
        st.caption("**👨‍💻 Desarrolladores:**")
        st.caption("Ing. Jan Benitez")
        st.caption("Ing. Neiris Pallares")
        st.markdown("---")
        st.caption("📌 **Ciclo PHVA Continuo**")
        
        if st.button("🚪 Cerrar Sesión", use_container_width=True):
            st.session_state.authenticated = False
            st.rerun()
    
    # Router de módulos
    if menu == "📊 Dashboard":
        dashboard()
    elif menu == "🔍 Fase 1: Diagnóstico":
        fase1_diagnostico()
    elif menu == "⚠️ Fase 2: Peligros GTC-45":
        fase2_peligros()
    elif menu == "📊 Fase 3: Evaluación de Riesgos":
        fase3_riesgos()
    elif menu == "📋 Fase 4: Plan de Acción":
        fase4_plan_accion()
    elif menu == "🚀 Fase 5: Implementación":
        fase5_implementacion()
    elif menu == "📈 Fase 6: Seguimiento":
        fase6_seguimiento()
    elif menu == "🤖 Asistente IA":
        asistente_ia()

st.markdown('''
<div class="footer">
    <p>SG-SST PHVA - Sistema de Gestión de Seguridad y Salud en el Trabajo</p>
    <p>Ciclo PHVA: Planificar → Hacer → Verificar → Actuar</p>
    <p>© 2024 - Todos los derechos reservados</p>
</div>
''', unsafe_allow_html=True)
