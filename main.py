import streamlit as st
import sqlite3
import pandas as pd
import requests
import random
import string
from datetime import datetime

st.set_page_config(page_title="SG-SST PHVA", page_icon="🔄", layout="centered")

# CSS para forzar centrado absoluto
st.markdown("""
<style>
    /* Eliminar TODO el padding de Streamlit */
    .main > div {
        padding: 0 !important;
        margin: 0 !important;
    }
    .block-container {
        padding: 0 !important;
        margin: 0 !important;
        max-width: 100% !important;
        position: relative !important;
        top: 0 !important;
    }
    .stApp {
        background: linear-gradient(135deg, #0f0c29 0%, #302b63 50%, #24243e 100%);
    }
    /* Centrado absoluto con position fixed */
    .login-wrapper {
        position: fixed;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        display: flex;
        align-items: center;
        justify-content: center;
        z-index: 999;
    }
    .login-card {
        background: rgba(20, 20, 40, 0.75);
        backdrop-filter: blur(15px);
        border-radius: 32px;
        padding: 40px 35px;
        border: 1px solid rgba(255,255,255,0.15);
        box-shadow: 0 25px 50px -12px rgba(0,0,0,0.5);
        width: 380px;
        text-align: center;
        animation: fadeIn 0.6s ease-out;
    }
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(-20px); }
        to { opacity: 1; transform: translateY(0); }
    }
    .logo-img {
        width: 70px;
        display: block;
        margin: 0 auto 15px auto;
    }
    .app-title {
        font-size: 26px;
        font-weight: 800;
        background: linear-gradient(135deg, #fff, #a8c0ff, #667eea);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin: 0 0 5px 0;
    }
    .app-slogan {
        font-size: 12px;
        color: rgba(255,255,255,0.65);
        margin-bottom: 25px;
        font-style: italic;
    }
    .stTextInput > div > div > input {
        background: rgba(255,255,255,0.08) !important;
        border: 1px solid rgba(255,255,255,0.2) !important;
        border-radius: 14px !important;
        color: white !important;
        padding: 12px 15px !important;
        font-size: 14px !important;
    }
    .stTextInput > div > div > input:focus {
        border-color: #667eea !important;
        box-shadow: 0 0 0 3px rgba(102,126,234,0.2) !important;
    }
    .stButton > button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
        border: none !important;
        border-radius: 14px !important;
        padding: 12px !important;
        font-weight: 600 !important;
        font-size: 15px !important;
        width: 100% !important;
    }
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 10px 25px rgba(102,126,234,0.4);
    }
    .forgot-link {
        text-align: center;
        margin-top: 20px;
    }
    .forgot-link button {
        background: transparent !important;
        color: rgba(255,255,255,0.6) !important;
        font-size: 12px !important;
        box-shadow: none !important;
    }
    .forgot-link button:hover {
        color: #a8c0ff !important;
        transform: none !important;
    }
    .footer {
        text-align: center;
        margin-top: 25px;
        font-size: 10px;
        color: rgba(255,255,255,0.35);
    }
    hr {
        margin: 20px 0;
        border-color: rgba(255,255,255,0.1);
    }
    .success-msg {
        background: rgba(0,255,0,0.1);
        border: 1px solid rgba(0,255,0,0.3);
        border-radius: 12px;
        padding: 10px;
        text-align: center;
        color: #00ff88;
        font-size: 13px;
    }
    label {
        color: rgba(255,255,255,0.8) !important;
        font-size: 13px !important;
        text-align: left !important;
        display: block !important;
        margin-bottom: 5px !important;
    }
    /* Ocultar header de Streamlit */
    header {
        display: none !important;
    }
</style>
""", unsafe_allow_html=True)

# Base de datos
conn = sqlite3.connect("sst.db", check_same_thread=False)
cursor = conn.cursor()

cursor.execute('''CREATE TABLE IF NOT EXISTS usuarios (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE,
    password TEXT,
    nombre TEXT,
    rol TEXT DEFAULT 'trabajador',
    email TEXT,
    activo INTEGER DEFAULT 1
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
    descripcion TEXT,
    probabilidad INTEGER,
    severidad INTEGER,
    nivel TEXT
)''')

cursor.execute('''CREATE TABLE IF NOT EXISTS acciones (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    empresa_id INTEGER,
    descripcion TEXT,
    responsable TEXT,
    fecha TEXT,
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

# Usuario admin
cursor.execute("SELECT * FROM usuarios WHERE username = 'admin'")
if not cursor.fetchone():
    cursor.execute("INSERT INTO usuarios (username, password, nombre, rol, email) VALUES (?, ?, ?, ?, ?)",
                  ('admin', 'admin123', 'Administrador', 'admin', 'admin@sgsst.com'))
    conn.commit()

conn.commit()

def verificar_login(username, password):
    cursor.execute("SELECT * FROM usuarios WHERE username = ? AND password = ? AND activo = 1", (username, password))
    user = cursor.fetchone()
    if user:
        return {"id": user[0], "username": user[1], "nombre": user[3], "rol": user[4]}
    return None

def reset_password(username, email):
    cursor.execute("SELECT * FROM usuarios WHERE username = ? AND email = ?", (username, email))
    user = cursor.fetchone()
    if user:
        nueva_password = ''.join(random.choices(string.ascii_letters + string.digits, k=8))
        cursor.execute("UPDATE usuarios SET password = ? WHERE id = ?", (nueva_password, user[0]))
        conn.commit()
        return True, nueva_password
    return False, None

def call_ia(prompt):
    try:
        url = "https://generativelanguage.googleapis.com/v1/models/gemini-pro:generateContent"
        headers = {"Content-Type": "application/json", "x-goog-api-key": "AIzaSyD3QhEohGJeYhVtM7JmBZ2nXvZJFxJZv3U"}
        data = {"contents": [{"parts": [{"text": prompt}]}]}
        r = requests.post(url, json=data, headers=headers, timeout=30)
        if r.status_code == 200:
            return r.json()["candidates"][0]["content"]["parts"][0]["text"]
    except:
        pass
    return "Error al conectar con IA."

# Sesión
if "auth" not in st.session_state:
    st.session_state.auth = False
if "user" not in st.session_state:
    st.session_state.user = None
if "show_reset" not in st.session_state:
    st.session_state.show_reset = False
if "empresa_actual_id" not in st.session_state:
    st.session_state.empresa_actual_id = None
if "empresa_actual" not in st.session_state:
    st.session_state.empresa_actual = None

# ========== LOGIN CENTRADO ABSOLUTO ==========
if not st.session_state.auth:
    st.markdown('<div class="login-wrapper">', unsafe_allow_html=True)
    
    if not st.session_state.show_reset:
        st.markdown("""
        <div class="login-card">
            <img src="https://cdn-icons-png.flaticon.com/512/2917/2917995.png" class="logo-img">
            <div class="app-title">SG-SST PHVA</div>
            <div class="app-slogan">✨ Seguridad y Salud, compromiso de todos ✨</div>
        """, unsafe_allow_html=True)
        
        with st.form("login_form"):
            username = st.text_input("Usuario", placeholder="Ingrese su usuario")
            password = st.text_input("Contraseña", type="password", placeholder="Ingrese su contraseña")
            
            if st.form_submit_button("🚀 INGRESAR", use_container_width=True):
                user = verificar_login(username, password)
                if user:
                    st.session_state.auth = True
                    st.session_state.user = user
                    st.rerun()
                else:
                    st.error("❌ Usuario o contraseña incorrectos")
        
        st.markdown('<div class="forgot-link">', unsafe_allow_html=True)
        if st.button("🔐 ¿Olvidaste tu contraseña?", use_container_width=True):
            st.session_state.show_reset = True
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)
        
        st.markdown('<hr>', unsafe_allow_html=True)
        st.markdown('<div class="footer">🛡️ SG-SST PHVA | Desarrollado por JAN BENITEZ</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    else:
        st.markdown("""
        <div class="login-card">
            <img src="https://cdn-icons-png.flaticon.com/512/2917/2917995.png" class="logo-img">
            <div class="app-title">Recuperar Contraseña</div>
            <div class="app-slogan">✨ Te enviaremos una nueva contraseña ✨</div>
        """, unsafe_allow_html=True)
        
        with st.form("reset_form"):
            username = st.text_input("Usuario", placeholder="Ingrese su usuario")
            email = st.text_input("Email", placeholder="Ingrese su email registrado")
            
            if st.form_submit_button("📧 ENVIAR NUEVA CONTRASEÑA", use_container_width=True):
                success, new_pass = reset_password(username, email)
                if success:
                    st.markdown(f'<div class="success-msg">✅ Contraseña restablecida: <strong>{new_pass}</strong><br>Guárdala e inicia sesión</div>', unsafe_allow_html=True)
                else:
                    st.error("❌ Usuario o email no encontrados")
        
        st.markdown('<div class="forgot-link">', unsafe_allow_html=True)
        if st.button("← Volver al inicio de sesión", use_container_width=True):
            st.session_state.show_reset = False
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)
        
        st.markdown('<div class="footer">🛡️ SG-SST PHVA | Desarrollado por JAN BENITEZ</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)
    st.stop()

# ========== DASHBOARD ==========
st.set_page_config(page_title="SG-SST PHVA", page_icon="🔄", layout="wide")

st.success(f"✅ Bienvenido {st.session_state.user['nombre']}")

if st.button("🚪 Cerrar Sesión"):
    st.session_state.auth = False
    st.session_state.show_reset = False
    st.rerun()

st.info("📌 Módulos disponibles: Dashboard, Diagnóstico IA, Peligros, Plan de Acción, Trabajadores, Incidentes, Chat IA")