import streamlit as st
import sqlite3
import pandas as pd
import requests
import random
import string
from datetime import datetime

st.set_page_config(page_title="SG-SST PHVA", page_icon="🔄", layout="centered")

# CSS para login ultra compacto y centrado
st.markdown("""
<style>
    /* Ocultar header y footer */
    header, footer {
        display: none !important;
    }
    
    /* Eliminar padding del main */
    .main > div, .block-container {
        padding: 0 !important;
        margin: 0 !important;
        max-width: 100% !important;
    }
    
    /* Fondo */
    .stApp {
        background: linear-gradient(135deg, #0f0c29 0%, #302b63 50%, #24243e 100%);
        height: 100vh;
    }
    
    /* Contenedor flex para centrar verticalmente */
    .centered-container {
        display: flex;
        align-items: center;
        justify-content: center;
        min-height: 100vh;
        width: 100%;
    }
    
    /* Tarjeta compacta */
    .login-card {
        background: rgba(255, 255, 255, 0.08);
        backdrop-filter: blur(12px);
        border-radius: 20px;
        padding: 20px 25px;
        border: 1px solid rgba(255,255,255,0.1);
        box-shadow: 0 15px 35px rgba(0,0,0,0.2);
        width: 320px;
        margin: 0 auto;
    }
    
    /* Logo */
    .logo {
        text-align: center;
        margin-bottom: 10px;
    }
    .logo img {
        width: 50px;
    }
    .title {
        text-align: center;
        font-size: 18px;
        font-weight: 700;
        color: white;
        margin: 5px 0;
    }
    .slogan {
        text-align: center;
        font-size: 10px;
        color: rgba(255,255,255,0.6);
        margin-bottom: 20px;
    }
    
    /* Inputs */
    .stTextInput > div > div > input {
        background: rgba(255,255,255,0.1) !important;
        border: 1px solid rgba(255,255,255,0.2) !important;
        border-radius: 10px !important;
        color: white !important;
        padding: 8px 12px !important;
        font-size: 13px !important;
        height: 38px !important;
    }
    .stTextInput > div > div > input:focus {
        border-color: #667eea !important;
        outline: none !important;
    }
    label {
        color: rgba(255,255,255,0.7) !important;
        font-size: 12px !important;
        margin-bottom: 4px !important;
    }
    
    /* Botón */
    .stButton > button {
        background: linear-gradient(135deg, #667eea, #764ba2) !important;
        border: none !important;
        border-radius: 10px !important;
        padding: 8px !important;
        font-size: 13px !important;
        font-weight: 600 !important;
        width: 100% !important;
        height: 38px !important;
        margin-top: 5px !important;
    }
    .stButton > button:hover {
        transform: translateY(-1px);
        box-shadow: 0 5px 15px rgba(102,126,234,0.4);
    }
    
    /* Link */
    .forgot {
        text-align: center;
        margin-top: 12px;
    }
    .forgot a {
        color: rgba(255,255,255,0.5);
        font-size: 11px;
        text-decoration: none;
    }
    .forgot a:hover {
        color: #a8c0ff;
    }
    
    /* Footer */
    .footer {
        text-align: center;
        font-size: 9px;
        color: rgba(255,255,255,0.3);
        margin-top: 15px;
        padding-top: 10px;
        border-top: 1px solid rgba(255,255,255,0.1);
    }
    
    /* Mensaje error */
    .stAlert {
        background: rgba(255,0,0,0.15) !important;
        border: none !important;
        border-radius: 8px !important;
        font-size: 11px !important;
        padding: 6px !important;
        margin-top: 8px !important;
    }
</style>
""", unsafe_allow_html=True)

# Base de datos
conn = sqlite3.connect("sst.db", check_same_thread=False)
cursor = conn.cursor()

cursor.execute('''CREATE TABLE IF NOT EXISTS usuarios (id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT UNIQUE, password TEXT, nombre TEXT, rol TEXT, email TEXT, activo INTEGER DEFAULT 1)''')
cursor.execute('''CREATE TABLE IF NOT EXISTS empresa (id INTEGER PRIMARY KEY AUTOINCREMENT, nit TEXT, nombre TEXT, trabajadores INTEGER, arl TEXT, diagnostico TEXT, fecha TEXT)''')
cursor.execute('''CREATE TABLE IF NOT EXISTS peligros (id INTEGER PRIMARY KEY AUTOINCREMENT, empresa_id INTEGER, tipo TEXT, descripcion TEXT)''')
cursor.execute('''CREATE TABLE IF NOT EXISTS acciones (id INTEGER PRIMARY KEY AUTOINCREMENT, empresa_id INTEGER, descripcion TEXT, responsable TEXT, estado TEXT)''')
cursor.execute('''CREATE TABLE IF NOT EXISTS trabajadores (id INTEGER PRIMARY KEY AUTOINCREMENT, empresa_id INTEGER, nombre TEXT, cedula TEXT, cargo TEXT)''')
cursor.execute('''CREATE TABLE IF NOT EXISTS incidentes (id INTEGER PRIMARY KEY AUTOINCREMENT, empresa_id INTEGER, descripcion TEXT, fecha TEXT, gravedad TEXT)''')

cursor.execute("SELECT * FROM usuarios WHERE username='admin'")
if not cursor.fetchone():
    cursor.execute("INSERT INTO usuarios (username, password, nombre, rol, email) VALUES (?,?,?,?,?)", ('admin','admin123','Administrador','admin','admin@sgsst.com'))
    conn.commit()
conn.commit()

def verificar_login(u, p):
    cursor.execute("SELECT * FROM usuarios WHERE username=? AND password=? AND activo=1", (u, p))
    r = cursor.fetchone()
    if r:
        return {"nombre": r[3], "rol": r[4]}
    return None

if "auth" not in st.session_state:
    st.session_state.auth = False
if "user" not in st.session_state:
    st.session_state.user = None

if not st.session_state.auth:
    # Contenedor centrado
    st.markdown('<div class="centered-container">', unsafe_allow_html=True)
    st.markdown('<div class="login-card">', unsafe_allow_html=True)
    
    # Logo y título
    st.markdown("""
    <div class="logo">
        <img src="https://cdn-icons-png.flaticon.com/512/2917/2917995.png">
    </div>
    <div class="title">SG-SST PHVA</div>
    <div class="slogan">Seguridad y Salud, compromiso de todos</div>
    """, unsafe_allow_html=True)
    
    # Formulario
    with st.form("login_form"):
        username = st.text_input("Usuario", placeholder="Ingrese su usuario", key="user_input")
        password = st.text_input("Contraseña", type="password", placeholder="Ingrese su contraseña", key="pass_input")
        
        if st.form_submit_button("🚀 INGRESAR", use_container_width=True):
            user = verificar_login(username, password)
            if user:
                st.session_state.auth = True
                st.session_state.user = user
                st.rerun()
            else:
                st.error("❌ Usuario o contraseña incorrectos")
    
    # Link olvidó contraseña
    st.markdown('<div class="forgot"><a href="#">🔐 ¿Olvidaste tu contraseña?</a></div>', unsafe_allow_html=True)
    
    # Footer
    st.markdown('<div class="footer">🛡️ SG-SST PHVA | Desarrollado por JAN BENITEZ</div>', unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
    st.stop()

# ========== DASHBOARD POST LOGIN ==========
st.set_page_config(page_title="SG-SST PHVA", page_icon="🔄", layout="wide")

st.success(f"✅ Bienvenido {st.session_state.user['nombre']}")

col1, col2 = st.columns([3, 1])
with col2:
    if st.button("🚪 Cerrar Sesión", use_container_width=True):
        st.session_state.auth = False
        st.rerun()

st.info("📌 Módulos: Dashboard | Diagnóstico IA | Peligros | Plan de Acción | Trabajadores | Incidentes | Chat IA")