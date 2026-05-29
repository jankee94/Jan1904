import streamlit as st
import sys
import os
from datetime import datetime

# Configuración de página
st.set_page_config(
    page_title="SG-SST PHVA",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Estilos CSS
st.markdown("""
    <style>
    .main-header {
        background: linear-gradient(135deg, #0b3b5f 0%, #1b5a7a 100%);
        padding: 1.5rem;
        border-radius: 20px;
        color: white;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background: linear-gradient(135deg, #0b3b5f 0%, #1b5a7a 100%);
        padding: 1rem;
        border-radius: 15px;
        color: white;
        text-align: center;
        transition: transform 0.3s;
    }
    .metric-card:hover {
        transform: translateY(-5px);
    }
    </style>
""", unsafe_allow_html=True)

# Inicializar sesión
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
if "username" not in st.session_state:
    st.session_state.username = None

# Importar módulos
from security.auth import verificar_login, login_ui
from modules import trabajadores, peligros, capacitaciones, incidentes

# Módulos pendientes (estructura base)
def modulo_en_construccion(nombre):
    st.info(f"📌 Módulo '{nombre}' - En desarrollo")
    st.markdown("""
    ### 🚧 Próximamente
    Este módulo estará disponible en la próxima actualización con las siguientes funcionalidades:
    - Gestión completa de registros
    - Reportes y exportaciones
    - Integración con IA
    - Dashboards específicos
    """)

def login():
    st.markdown('<div class="main-header"><h1>🛡️ SG-SST PHVA</h1><p>Planificar · Hacer · Verificar · Actuar</p></div>', unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        with st.container():
            st.markdown('<div style="background: white; padding: 2rem; border-radius: 15px; box-shadow: 0 4px 12px rgba(0,0,0,0.1);">', unsafe_allow_html=True)
            login_ui()
            st.markdown('</div>', unsafe_allow_html=True)

def dashboard():
    st.markdown(f'<div class="main-header"><h1>📊 Dashboard SG-SST</h1><p>Bienvenido, {st.session_state.username}</p></div>', unsafe_allow_html=True)
    
    # Métricas principales
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown('<div class="metric-card"><h2>👥</h2><h3>24</h3><p>Trabajadores Activos</p></div>', unsafe_allow_html=True)
    with col2:
        st.markdown('<div class="metric-card"><h2>⚠️</h2><h3>8</h3><p>Peligros Identificados</p></div>', unsafe_allow_html=True)
    with col3:
        st.markdown('<div class="metric-card"><h2>📊</h2><h3>92%</h3><p>Cumplimiento General</p></div>', unsafe_allow_html=True)
    with col4:
        st.markdown('<div class="metric-card"><h2>✅</h2><h3>9/18</h3><p>Módulos Activos</p></div>', unsafe_allow_html=True)
    
    st.markdown("---")
    st.subheader("📈 Progreso del Sistema")
    st.progress(50)
    st.caption("9 de 18 módulos completados - 50%")

# Sidebar de navegación
with st.sidebar:
    st.image("https://img.icons8.com/color/96/000000/security-checked--v1.png", width=80)
    st.markdown("## 🛡️ SG-SST PHVA")
    st.markdown(f"**Usuario:** {st.session_state.username if st.session_state.authenticated else 'No autenticado'}")
    st.markdown("---")
    
    menu = st.radio("📋 Módulos del Sistema", [
        "🏠 Dashboard",
        "👥 Trabajadores",
        "⚠️ Peligros GTC-45",
        "📚 Capacitaciones",
        "📝 Incidentes",
        "📅 Plan Anual SST",
        "🔍 Auditorías",
        "📊 Indicadores",
        "🤖 Asistente IA",
        "📜 Políticas SST",
        "📋 Procedimientos",
        "👥 COPASST",
        "📈 Reportes",
        "⚖️ Matriz Legal",
        "🚨 Gestión de Riesgos",
        "🚒 Plan de Emergencias",
        "📉 Estadísticas Avanzadas"
    ])
    
    st.markdown("---")
    if st.button("🚪 Cerrar sesión", use_container_width=True):
        st.session_state.authenticated = False
        st.rerun()
    
    st.caption("Desarrollado por: Ing. Jan Benitez & Ing. Neiris Pallares")

# Autenticación y contenido principal
if not st.session_state.authenticated:
    login()
else:
    if menu == "🏠 Dashboard":
        dashboard()
    elif menu == "👥 Trabajadores":
        trabajadores.show()
    elif menu == "⚠️ Peligros GTC-45":
        peligros.show()
    elif menu == "📚 Capacitaciones":
        capacitaciones.show()
    elif menu == "📝 Incidentes":
        incidentes.show()
    else:
        modulo_en_construccion(menu)
