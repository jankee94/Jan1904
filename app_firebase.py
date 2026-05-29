import streamlit as st
import pandas as pd
from datetime import datetime

st.set_page_config(
    page_title="SG-SST PHVA",
    page_icon="🏭",
    layout="wide"
)

st.markdown("""
<style>
    .stApp { background: linear-gradient(135deg, #0f2027, #203a43, #2c5364) !important; }
    .login-card { background: rgba(255,255,255,0.1); backdrop-filter: blur(10px); padding: 2rem; border-radius: 20px; }
    .main-header { background: linear-gradient(135deg, #00b4db, #0083b0); padding: 2rem; border-radius: 20px; color: white; text-align: center; }
    .metric-card { background: rgba(255,255,255,0.1); padding: 1.5rem; border-radius: 15px; text-align: center; color: white; }
    .admin-card { background: rgba(255,215,0,0.15); padding: 1rem; border-radius: 15px; border: 1px solid gold; }
</style>
""", unsafe_allow_html=True)

if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
if "usuario_nombre" not in st.session_state:
    st.session_state.usuario_nombre = None
if "es_admin" not in st.session_state:
    st.session_state.es_admin = False

def login():
    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        st.markdown('<div class="login-card">', unsafe_allow_html=True)
        st.markdown("<h1 style='text-align:center'>🏭 SG-SST PHVA</h1>", unsafe_allow_html=True)
        
        with st.form("login_form"):
            username = st.text_input("Usuario")
            password = st.text_input("Contraseña", type="password")
            if st.form_submit_button("Ingresar", use_container_width=True):
                if username == "admin" and password == "sst2024":
                    st.session_state.authenticated = True
                    st.session_state.usuario_nombre = "Administrador"
                    st.session_state.es_admin = True
                    st.rerun()
                else:
                    st.error("❌ Use: admin / sst2024")
        st.markdown('</div>', unsafe_allow_html=True)

def admin_panel():
    st.markdown('<div class="admin-card">', unsafe_allow_html=True)
    st.markdown("### 👑 Panel de Administrador")
    st.markdown('</div>', unsafe_allow_html=True)
    
    with st.form("crear_usuario"):
        nombre = st.text_input("Nombre")
        email = st.text_input("Email")
        password = st.text_input("Password", type="password")
        if st.form_submit_button("Crear Usuario"):
            st.success(f"✅ Usuario {nombre} creado")

def dashboard():
    st.markdown('<div class="main-header"><h1>🏭 SG-SST PHVA</h1></div>', unsafe_allow_html=True)
    col1, col2, col3, col4 = st.columns(4)
    for col in [col1, col2, col3, col4]:
        with col:
            st.markdown('<div class="metric-card"><h2>📊</h2><h3>0</h3><p>Módulo</p></div>', unsafe_allow_html=True)

def info_empresa():
    st.markdown("### 🏢 Información de la Empresa")
    with st.form("empresa"):
        nombre = st.text_input("Nombre")
        sector = st.selectbox("Sector", ["Construcción", "Manufactura", "Servicios"])
        if st.form_submit_button("Guardar"):
            st.success("✅ Guardado")

def asistente_ia():
    st.markdown("### 🤖 Asistente IA")
    if "msg" not in st.session_state:
        st.session_state.msg = [{"role": "assistant", "content": "Hola! ¿En qué ayudo?"}]
    for m in st.session_state.msg:
        with st.chat_message(m["role"]):
            st.markdown(m["content"])
    if prompt := st.chat_input("Escribe..."):
        st.session_state.msg.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
        respuesta = "✅ Recibido"
        with st.chat_message("assistant"):
            st.markdown(respuesta)
        st.session_state.msg.append({"role": "assistant", "content": respuesta})
        st.rerun()

def cargar_excel():
    st.markdown("### 📁 Cargar Excel")
    archivo = st.file_uploader("Subir archivo", type=["xlsx", "csv"])
    if archivo:
        st.success("✅ Archivo cargado")

def progreso():
    st.markdown("### 📊 Progreso")
    fases = ["Fase 1", "Fase 2", "Fase 3", "Fase 4", "Fase 5", "Fase 6"]
    for i, fase in enumerate(fases):
        st.progress((i+1)/len(fases))
        st.markdown(f"**{fase}**")

if not st.session_state.authenticated:
    login()
else:
    st.sidebar.markdown(f"**👤 {st.session_state.usuario_nombre}**")
    
    if st.session_state.es_admin:
        menu = st.sidebar.radio("Menú", ["Dashboard", "👑 Admin", "Empresa", "IA", "Excel", "Progreso"])
    else:
        menu = st.sidebar.radio("Menú", ["Dashboard", "Empresa", "IA", "Excel", "Progreso"])
    
    if st.sidebar.button("Cerrar sesión"):
        st.session_state.authenticated = False
        st.rerun()
    
    if menu == "Dashboard":
        dashboard()
    elif menu == "👑 Admin":
        admin_panel()
    elif menu == "Empresa":
        info_empresa()
    elif menu == "IA":
        asistente_ia()
    elif menu == "Excel":
        cargar_excel()
    elif menu == "Progreso":
        progreso()
