import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import plotly.express as px
import plotly.graph_objects as go
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

# ==================== CSS ====================
st.markdown("""
<style>
    @keyframes fadeIn { from { opacity: 0; transform: translateY(20px); } to { opacity: 1; transform: translateY(0); } }
    @keyframes slideIn { from { transform: translateX(-30px); opacity: 0; } to { transform: translateX(0); opacity: 1; } }
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
        
        st.markdown('</div>', unsafe_allow_html=True)
        st.markdown("---")
        st.caption("👨‍💻 Ing. Jan Benitez & Ing. Neiris Pallares")

def dashboard():
    st.markdown('<div class="main-header"><h1>📊 Dashboard SG-SST PHVA</h1><p>Planificar → Hacer → Verificar → Actuar</p></div>', unsafe_allow_html=True)
    mostrar_fases()
    st.markdown("---")
    
    col1, col2, col3, col4, col5, col6 = st.columns(6)
    with col1: st.metric("🔍 Fase 1", "✅" if st.session_state.empresa.get("nombre") else "⏳")
    with col2: st.metric("⚠️ Fase 2", f"{len(st.session_state.peligros)}")
    with col3: st.metric("📊 Fase 3", f"{len(st.session_state.matriz_riesgos)}")
    with col4: st.metric("📋 Fase 4", f"{len(st.session_state.plan_accion)}")
    with col5: st.metric("🚀 Fase 5", f"{len(st.session_state.capacitaciones)}")
    with col6: st.metric("📈 Fase 6", f"{len(st.session_state.incidentes)}")
    
    st.markdown("---")
    fig = go.Figure(data=[go.Bar(x=['F1','F2','F3','F4','F5','F6'], y=[100 if st.session_state.empresa.get("nombre") else 0, min(100, len(st.session_state.peligros)*33), min(100, len(st.session_state.matriz_riesgos)*33), min(100, len(st.session_state.plan_accion)*33), min(100, len(st.session_state.capacitaciones)*33), min(100, len(st.session_state.incidentes)*33)], marker_color=['#4ECDC4','#FFB347','#45B7D1','#96CEB4','#FFEAA7','#FF6B6B'])])
    fig.update_layout(title="Progreso por Fase", paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(255,255,255,0.1)', font_color='white')
    st.plotly_chart(fig, use_container_width=True)

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
        respuesta = f"**Progreso:** {calcular_progreso()}% - Fase {st.session_state.fase_actual}. Consulta: '{prompt}'"
        st.session_state.ia_messages.append({"role": "assistant", "content": respuesta})
        st.rerun()

# ==================== FASES ====================
def fase1_diagnostico():
    st.markdown('<div class="main-header"><h1>🔍 Fase 1: Diagnóstico</h1></div>', unsafe_allow_html=True)
    with st.form("fase1"):
        nombre = st.text_input("Empresa", value=st.session_state.empresa.get("nombre", ""))
        if st.form_submit_button("Guardar"):
            st.session_state.empresa["nombre"] = nombre
            st.success("✅ Guardado")
            st.session_state.fase_actual = 2
            st.rerun()

def fase2_peligros():
    st.markdown('<div class="main-header"><h1>⚠️ Fase 2: Peligros</h1></div>', unsafe_allow_html=True)
    with st.form("peligro"):
        peligro = st.text_input("Peligro")
        if st.form_submit_button("Guardar"):
            st.session_state.peligros.append({"peligro": peligro})
            st.rerun()
    st.dataframe(pd.DataFrame(st.session_state.peligros))

def fase3_riesgos():
    st.markdown('<div class="main-header"><h1>📊 Fase 3: Riesgos</h1></div>', unsafe_allow_html=True)
    st.write("En desarrollo")

def fase4_plan_accion():
    st.markdown('<div class="main-header"><h1>📋 Fase 4: Plan</h1></div>', unsafe_allow_html=True)
    st.write("En desarrollo")

def fase5_implementacion():
    st.markdown('<div class="main-header"><h1>🚀 Fase 5: Implementación</h1></div>', unsafe_allow_html=True)
    st.write("En desarrollo")

def fase6_seguimiento():
    st.markdown('<div class="main-header"><h1>📈 Fase 6: Seguimiento</h1></div>', unsafe_allow_html=True)
    st.write("En desarrollo")

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
        menu = st.radio("📋 Módulos", ["📊 Dashboard", "🔍 Fase 1", "⚠️ Fase 2", "📊 Fase 3", "📋 Fase 4", "🚀 Fase 5", "📈 Fase 6", "🤖 Asistente IA"])
        st.markdown("---")
        st.caption("👨‍💻 Ing. Jan Benitez & Ing. Neiris Pallares")
        if st.button("🚪 Cerrar Sesión"):
            st.session_state.authenticated = False
            st.rerun()
    
    if menu == "📊 Dashboard":
        dashboard()
    elif menu == "🔍 Fase 1":
        fase1_diagnostico()
    elif menu == "⚠️ Fase 2":
        fase2_peligros()
    elif menu == "📊 Fase 3":
        fase3_riesgos()
    elif menu == "📋 Fase 4":
        fase4_plan_accion()
    elif menu == "🚀 Fase 5":
        fase5_implementacion()
    elif menu == "📈 Fase 6":
        fase6_seguimiento()
    elif menu == "🤖 Asistente IA":
        asistente_ia()

st.markdown('<div class="footer"><p>SG-SST PHVA - Sistema de Gestión SST © 2024</p></div>', unsafe_allow_html=True)
