import streamlit as st
import sqlite3
import pandas as pd
import requests
from datetime import datetime

st.set_page_config(
    page_title="SG-SST PHVA",
    page_icon="🔄",
    layout="centered",
    initial_sidebar_state="collapsed"
)

st.markdown("""
<style>
    .stApp {
        background: linear-gradient(135deg, #0f0c29 0%, #302b63 50%, #24243e 100%);
        height: 100vh;
    }
    header[data-testid="stHeader"] {
        display: none;
    }
    .block-container {
        padding: 0 !important;
        max-width: 340px !important;
        margin: 0 auto !important;
    }
    .stApp > div {
        display: flex;
        align-items: center;
        justify-content: center;
        height: 100vh;
        flex-direction: column;
    }
    .stForm {
        background: rgba(20, 20, 40, 0.75);
        backdrop-filter: blur(14px);
        border-radius: 28px;
        padding: 32px 28px !important;
        border: 1px solid rgba(255,255,255,0.12);
        box-shadow: 0 25px 45px rgba(0,0,0,0.3);
        width: 100%;
    }
    .login-logo {
        text-align: center;
        margin-bottom: 20px;
    }
    .login-logo img {
        width: 60px;
        margin-bottom: 10px;
    }
    .login-title {
        font-size: 24px;
        font-weight: 800;
        background: linear-gradient(135deg, #fff, #a8c0ff, #667eea);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin: 0;
    }
    .login-slogan {
        font-size: 11px;
        color: rgba(255,255,255,0.55);
        text-align: center;
        margin-top: 5px;
    }
    .stTextInput label {
        color: rgba(255,255,255,0.75) !important;
        font-size: 12px !important;
        font-weight: 500 !important;
        margin-bottom: 5px !important;
    }
    .stTextInput input {
        background: rgba(255,255,255,0.08) !important;
        border: 1px solid rgba(255,255,255,0.2) !important;
        border-radius: 14px !important;
        color: white !important;
        padding: 10px 15px !important;
        font-size: 13px !important;
        width: 100% !important;
    }
    .stTextInput input:focus {
        border-color: #667eea !important;
        box-shadow: 0 0 0 2px rgba(102,126,234,0.3) !important;
        outline: none !important;
    }
    .stButton button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
        border: none !important;
        border-radius: 14px !important;
        padding: 10px !important;
        font-weight: 600 !important;
        font-size: 14px !important;
        width: 100% !important;
        margin-top: 12px !important;
        cursor: pointer !important;
    }
    .stButton button:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 20px rgba(102,126,234,0.4);
    }
    .forgot-link {
        text-align: center;
        margin-top: 18px;
    }
    .forgot-link a {
        color: rgba(255,255,255,0.45);
        font-size: 11px;
        text-decoration: none;
    }
    .forgot-link a:hover {
        color: #a8c0ff;
    }
    .login-footer {
        text-align: center;
        font-size: 9px;
        color: rgba(255,255,255,0.25);
        margin-top: 18px;
        padding-top: 12px;
        border-top: 1px solid rgba(255,255,255,0.08);
    }
    .stAlert {
        background: rgba(255,50,50,0.12) !important;
        border: none !important;
        border-radius: 12px !important;
        font-size: 11px !important;
        padding: 8px !important;
        margin-top: 12px !important;
    }
    footer {
        display: none !important;
    }
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="login-logo">
    <img src="https://cdn-icons-png.flaticon.com/512/2917/2917995.png">
    <div class="login-title">SG-SST PHVA</div>
    <div class="login-slogan">✨ Seguridad y Salud, compromiso de todos ✨</div>
</div>
""", unsafe_allow_html=True)

conn = sqlite3.connect("sst.db", check_same_thread=False)
cursor = conn.cursor()

cursor.execute('''CREATE TABLE IF NOT EXISTS usuarios (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE,
    password TEXT,
    nombre TEXT,
    rol TEXT DEFAULT 'trabajador'
)''')

cursor.execute('''CREATE TABLE IF NOT EXISTS empresa (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nit TEXT,
    nombre TEXT,
    trabajadores INTEGER,
    arl TEXT,
    diagnostico TEXT,
    fecha TEXT
)''')

cursor.execute('''CREATE TABLE IF NOT EXISTS peligros (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    empresa_id INTEGER,
    tipo TEXT,
    descripcion TEXT
)''')

cursor.execute('''CREATE TABLE IF NOT EXISTS acciones (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    empresa_id INTEGER,
    descripcion TEXT,
    responsable TEXT,
    estado TEXT
)''')

cursor.execute('''CREATE TABLE IF NOT EXISTS trabajadores (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    empresa_id INTEGER,
    nombre TEXT,
    cedula TEXT,
    cargo TEXT
)''')

cursor.execute('''CREATE TABLE IF NOT EXISTS incidentes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    empresa_id INTEGER,
    descripcion TEXT,
    fecha TEXT,
    gravedad TEXT
)''')

cursor.execute("SELECT * FROM usuarios WHERE username='admin'")
if not cursor.fetchone():
    cursor.execute("INSERT INTO usuarios (username, password, nombre, rol) VALUES (?,?,?,?)",
                  ('admin', 'admin123', 'Administrador', 'admin'))
    conn.commit()
conn.commit()

def verificar_login(username, password):
    cursor.execute("SELECT * FROM usuarios WHERE username=? AND password=?", (username, password))
    user = cursor.fetchone()
    if user:
        return {"id": user[0], "username": user[1], "nombre": user[3], "rol": user[4]}
    return None

if "auth" not in st.session_state:
    st.session_state.auth = False
if "user" not in st.session_state:
    st.session_state.user = None

if not st.session_state.auth:
    with st.form("login_form"):
        username = st.text_input("👤 Usuario", placeholder="Ingrese su usuario")
        password = st.text_input("🔒 Contraseña", type="password", placeholder="Ingrese su contraseña")
        
        if st.form_submit_button("🚀 INGRESAR", use_container_width=True):
            user = verificar_login(username, password)
            if user:
                st.session_state.auth = True
                st.session_state.user = user
                st.rerun()
            else:
                st.error("❌ Usuario o contraseña incorrectos")
    
    st.markdown("""
    <div class="forgot-link">
        <a href="#">🔐 ¿Olvidaste tu contraseña?</a>
    </div>
    <div class="login-footer">
        🛡️ SG-SST PHVA | Desarrollado por JAN BENITEZ
    </div>
    """, unsafe_allow_html=True)
    st.stop()

st.set_page_config(page_title="SG-SST PHVA", page_icon="🔄", layout="wide")

st.success(f"✅ Bienvenido, {st.session_state.user['nombre']}!")

if st.button("🚪 Cerrar Sesión", use_container_width=True):
    st.session_state.auth = False
    st.rerun()

st.info("📌 Módulos disponibles próximamente: Diagnóstico IA, Peligros, Plan de Acción, Trabajadores, Incidentes, Chat IA")
