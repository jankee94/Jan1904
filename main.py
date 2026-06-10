# app/main.py - Versión actualizada con Capacitaciones
import streamlit as st
from datetime import datetime
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config.settings import settings
from firebase.auth.auth_service import auth_service
from firebase.firestore.client import firestore_client

# Importar módulos
from modules.capacitaciones.ui import render_capacitaciones
from modules.inspecciones.ui import render_inspecciones
from modules.emergencias.ui import render_emergencias
from modules.documental.ui import render_documental
from modules.indicadores.ui import render_indicadores

st.set_page_config(
    page_title=settings.APP_NAME,
    page_icon="🔄",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS Global
st.markdown('''
<style>
    .stApp {
        background: linear-gradient(135deg, #0f0c29 0%, #302b63 50%, #24243e 100%);
    }
    .main-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1rem 2rem;
        border-radius: 15px;
        margin-bottom: 2rem;
    }
    .main-header h1 {
        color: white;
        margin: 0;
        font-size: 1.8rem;
    }
    .main-header p {
        color: rgba(255,255,255,0.8);
        margin: 0;
    }
    .card {
        background: rgba(255,255,255,0.1);
        backdrop-filter: blur(10px);
        border-radius: 15px;
        padding: 1.5rem;
        margin: 1rem 0;
    }
    .metric-card {
        background: rgba(255,255,255,0.15);
        border-radius: 12px;
        padding: 1rem;
        text-align: center;
    }
    .metric-value {
        font-size: 2rem;
        font-weight: bold;
        color: #667eea;
    }
    .metric-label {
        font-size: 0.8rem;
        color: rgba(255,255,255,0.7);
    }
</style>
''', unsafe_allow_html=True)

# Inicializar estado de sesión
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
if "user" not in st.session_state:
    st.session_state.user = None
if "user_uid" not in st.session_state:
    st.session_state.user_uid = None
if "empresa_id" not in st.session_state:
    st.session_state.empresa_id = None

# ========== LOGIN ==========
if not st.session_state.authenticated:
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("""
        <div style="text-align: center; margin-bottom: 2rem;">
            <img src="https://cdn-icons-png.flaticon.com/512/2917/2917995.png" width="80">
            <h1 style="color: white;">SG-SST PHVA</h1>
            <p style="color: rgba(255,255,255,0.7);">Plataforma Empresarial de Seguridad y Salud en el Trabajo</p>
        </div>
        """, unsafe_allow_html=True)
        
        tab1, tab2, tab3 = st.tabs(["🔐 Iniciar Sesión", "📝 Registrarse", "🔑 Recuperar Contraseña"])
        
        with tab1:
            with st.form("login_form"):
                email = st.text_input("Correo electrónico")
                password = st.text_input("Contraseña", type="password")
                
                if st.form_submit_button("Iniciar Sesión", use_container_width=True):
                    if email == "admin@sg-sst.com" and password == "admin123":
                        st.session_state.authenticated = True
                        st.session_state.user = {"email": email, "nombre": "Administrador"}
                        st.rerun()
                    else:
                        st.error("Credenciales incorrectas. Use admin@sg-sst.com / admin123")
        
        with tab2:
            with st.form("register_form"):
                nombre = st.text_input("Nombre completo")
                email = st.text_input("Correo electrónico")
                password = st.text_input("Contraseña", type="password")
                confirm_password = st.text_input("Confirmar contraseña", type="password")
                
                if st.form_submit_button("Registrarse", use_container_width=True):
                    if password != confirm_password:
                        st.error("Las contraseñas no coinciden")
                    else:
                        st.success("Registro exitoso. Contacte al administrador para activar su cuenta.")
        
        with tab3:
            with st.form("reset_form"):
                email = st.text_input("Correo electrónico")
                if st.form_submit_button("Enviar enlace de recuperación", use_container_width=True):
                    st.success("Si el correo existe, recibirás un enlace de recuperación")
    
    st.stop()

# ========== SIDEBAR ==========
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/2917/2917995.png", width=60)
    st.markdown(f"### {st.session_state.user.get('nombre', 'Usuario')}")
    st.caption(st.session_state.user.get('email', ''))
    st.markdown("---")
    
    # Menú principal
    menu_options = {
        "🏠 Dashboard": "dashboard",
        "🏢 Empresa": "empresa",
        "⚠️ Peligros": "peligros",
        "✅ Plan de Acción": "acciones",
        "👥 Trabajadores": "trabajadores",
        "📝 Incidentes": "incidentes",
        "📋 Matriz Legal": "matriz_legal",
        "🔍 Auditorías": "auditorias",
        "📚 Capacitaciones": "capacitaciones",
        "🔧 Inspecciones": "inspecciones",
        "🚨 Emergencias": "emergencias",
        "📄 Documentos": "documentos",
        "📊 Indicadores": "indicadores",
        "🤖 Chat IA": "chat",
        "⚙️ Configuración": "config"
    }
    
    menu = st.radio("MÓDULOS", list(menu_options.keys()))
    selected_module = menu_options[menu]
    
    st.markdown("---")
    if st.button("🚪 Cerrar Sesión", use_container_width=True):
        st.session_state.authenticated = False
        st.session_state.user = None
        st.rerun()

# ========== PÁGINAS ==========
def show_dashboard():
    st.markdown('<div class="main-header"><h1>🏠 Dashboard Ejecutivo</h1><p>Bienvenido al Sistema de Gestión SST</p></div>', unsafe_allow_html=True)
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown('<div class="metric-card"><div class="metric-value">0</div><div class="metric-label">Peligros</div></div>', unsafe_allow_html=True)
    with col2:
        st.markdown('<div class="metric-card"><div class="metric-value">0</div><div class="metric-label">Acciones</div></div>', unsafe_allow_html=True)
    with col3:
        st.markdown('<div class="metric-card"><div class="metric-value">0</div><div class="metric-label">Trabajadores</div></div>', unsafe_allow_html=True)
    with col4:
        st.markdown('<div class="metric-card"><div class="metric-value">0</div><div class="metric-label">Incidentes</div></div>', unsafe_allow_html=True)
    
    st.info("📌 Los módulos están siendo migrados a Firebase. Próximamente disponible.")

def show_empresa():
    st.info("Módulo en construcción - Configuración de empresa")

def show_peligros():
    st.info("Módulo en construcción - CRUD Peligros con Firestore")

def show_acciones():
    st.info("Módulo en construcción - Plan de acción")

def show_trabajadores():
    st.info("Módulo en construcción - Gestión de trabajadores")

def show_incidentes():
    st.info("Módulo en construcción - Reporte de incidentes")

def show_matriz_legal():
    st.info("Módulo en construcción - Matriz legal")

def show_auditorias():
    st.info("Módulo en construcción - Auditorías")

def show_capacitaciones():
    render_capacitaciones()

def show_inspecciones():
    st.info("Módulo en construcción - Inspecciones")

def show_emergencias():
    st.info("Módulo en construcción - Emergencias")

def show_documentos():
    st.info("Módulo en construcción - Documentos")

def show_indicadores():
    st.info("Módulo en construcción - Indicadores")

def show_chat():
    st.info("Módulo en construcción - Chat con IA")

def show_config():
    st.info("Módulo en construcción - Configuración")

# Router
pages = {
    "dashboard": show_dashboard,
    "empresa": show_empresa,
    "peligros": show_peligros,
    "acciones": show_acciones,
    "trabajadores": show_trabajadores,
    "incidentes": show_incidentes,
    "matriz_legal": show_matriz_legal,
    "auditorias": show_auditorias,
    "capacitaciones": show_capacitaciones,
    "inspecciones": show_inspecciones,
    "emergencias": show_emergencias,
    "documentos": show_documentos,
    "indicadores": show_indicadores,
    "chat": show_chat,
    "config": show_config
}

pages.get(selected_module, show_dashboard)()

# Footer
st.markdown("---")
st.markdown(f"<p style='text-align: center; color: rgba(255,255,255,0.4); font-size: 12px;'>🔄 {settings.APP_NAME} v{settings.APP_VERSION} | Desarrollado por JAN BENITEZ</p>", unsafe_allow_html=True)







