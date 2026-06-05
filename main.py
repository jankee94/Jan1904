import streamlit as st
import sqlite3
import pandas as pd
import requests
from datetime import datetime

st.set_page_config(page_title="SG-SST PHVA", page_icon="🔄", layout="centered")

# CSS MODERNO Y ATRACTIVO
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    * {
        font-family: 'Inter', sans-serif;
    }
    
    .stApp {
        background: linear-gradient(135deg, #0f0c29 0%, #302b63 50%, #24243e 100%);
        position: relative;
        overflow: hidden;
    }
    
    /* Partículas de fondo */
    .stApp::before {
        content: '';
        position: absolute;
        width: 200%;
        height: 200%;
        top: -50%;
        left: -50%;
        background: radial-gradient(circle, rgba(255,255,255,0.03) 1px, transparent 1px);
        background-size: 40px 40px;
        animation: float 20s linear infinite;
        pointer-events: none;
    }
    
    @keyframes float {
        0% { transform: translate(0, 0) rotate(0deg); }
        100% { transform: translate(-10%, -10%) rotate(5deg); }
    }
    
    /* Tarjeta moderna */
    .modern-card {
        background: rgba(20, 20, 40, 0.65);
        backdrop-filter: blur(15px);
        border-radius: 32px;
        padding: 35px 30px;
        border: 1px solid rgba(255,255,255,0.15);
        box-shadow: 0 25px 50px -12px rgba(0,0,0,0.5);
        transition: all 0.3s ease;
        position: relative;
        overflow: hidden;
    }
    
    .modern-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: -100%;
        width: 100%;
        height: 100%;
        background: linear-gradient(90deg, transparent, rgba(255,255,255,0.05), transparent);
        transition: left 0.5s;
    }
    
    .modern-card:hover::before {
        left: 100%;
    }
    
    /* Logo animado */
    .logo-wrapper {
        text-align: center;
        margin-bottom: 15px;
        animation: fadeInDown 0.8s ease;
    }
    
    .logo-img {
        width: 70px;
        filter: drop-shadow(0 8px 20px rgba(0,0,0,0.3));
        transition: transform 0.3s ease;
    }
    
    .logo-img:hover {
        transform: scale(1.05);
    }
    
    @keyframes fadeInDown {
        from {
            opacity: 0;
            transform: translateY(-20px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
    
    /* Títulos */
    .app-title {
        font-size: 28px;
        font-weight: 700;
        background: linear-gradient(135deg, #fff, #a0c0ff, #667eea);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin: 8px 0 4px 0;
        letter-spacing: -0.5px;
    }
    
    .app-slogan {
        font-size: 13px;
        color: rgba(255,255,255,0.7);
        font-weight: 400;
        margin-bottom: 20px;
        border-bottom: 1px dashed rgba(255,255,255,0.2);
        display: inline-block;
        padding-bottom: 5px;
    }
    
    /* Inputs modernos */
    .stTextInput > div > div > input {
        background: rgba(255,255,255,0.08) !important;
        border: 1px solid rgba(255,255,255,0.2) !important;
        border-radius: 14px !important;
        color: white !important;
        padding: 12px 15px 12px 42px !important;
        font-size: 14px !important;
        transition: all 0.3s ease !important;
    }
    
    .stTextInput > div > div > input:focus {
        border-color: #667eea !important;
        box-shadow: 0 0 0 3px rgba(102,126,234,0.3) !important;
        background: rgba(255,255,255,0.12) !important;
    }
    
    .stTextInput > div > div > input::placeholder {
        color: rgba(255,255,255,0.5);
        font-size: 13px;
    }
    
    /* Iconos dentro de inputs con pseudo-elementos */
    .stTextInput {
        position: relative;
    }
    
    .stTextInput:first-of-type::before {
        content: '👤';
        position: absolute;
        left: 12px;
        top: 50%;
        transform: translateY(-50%);
        z-index: 10;
        font-size: 16px;
        opacity: 0.7;
        pointer-events: none;
    }
    
    .stTextInput:last-of-type::before {
        content: '🔒';
        position: absolute;
        left: 12px;
        top: 50%;
        transform: translateY(-50%);
        z-index: 10;
        font-size: 16px;
        opacity: 0.7;
        pointer-events: none;
    }
    
    /* Botón elegante */
    .stButton > button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
        border: none !important;
        border-radius: 14px !important;
        padding: 12px !important;
        font-weight: 600 !important;
        font-size: 15px !important;
        letter-spacing: 0.5px;
        transition: all 0.3s ease !important;
        box-shadow: 0 8px 20px rgba(102,126,234,0.3);
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 12px 28px rgba(102,126,234,0.5);
        background: linear-gradient(135deg, #764ba2 0%, #667eea 100%) !important;
    }
    
    /* Link olvidó clave */
    .forgot-link {
        text-align: center;
        margin-top: 15px;
    }
    
    .forgot-link a {
        color: rgba(255,255,255,0.6);
        text-decoration: none;
        font-size: 12px;
        transition: color 0.2s;
    }
    
    .forgot-link a:hover {
        color: #a0c0ff;
        text-decoration: underline;
    }
    
    /* Footer */
    .footer-modern {
        position: fixed;
        bottom: 15px;
        left: 0;
        right: 0;
        text-align: center;
        font-size: 11px;
        color: rgba(255,255,255,0.4);
        background: transparent;
        padding: 8px;
        z-index: 999;
    }
    
    /* Animación de entrada de la tarjeta */
    .modern-card {
        animation: slideUp 0.6s ease-out;
    }
    
    @keyframes slideUp {
        from {
            opacity: 0;
            transform: translateY(30px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
    
    /* Ajustes responsivos */
    @media (max-width: 600px) {
        .modern-card {
            padding: 25px 20px;
            margin: 10px;
        }
        .app-title {
            font-size: 24px;
        }
    }
</style>
""", unsafe_allow_html=True)

# Base de datos
conn = sqlite3.connect("sst.db", check_same_thread=False)
cursor = conn.cursor()

cursor.execute('''CREATE TABLE IF NOT EXISTS usuarios (id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT, password TEXT, nombre TEXT, rol TEXT)''')
cursor.execute("SELECT * FROM usuarios WHERE username='admin'")
if not cursor.fetchone():
    cursor.execute("INSERT INTO usuarios (username, password, nombre, rol) VALUES (?,?,?,?)", ('admin','admin123','Administrador','admin'))
    conn.commit()

def verificar_login(u, p):
    cursor.execute("SELECT * FROM usuarios WHERE username=? AND password=?", (u, p))
    r = cursor.fetchone()
    if r:
        return {"nombre": r[3], "rol": r[4]}
    return None

# Sesión
if "auth" not in st.session_state:
    st.session_state.auth = False
    st.session_state.user = None

# LOGIN MODERNO
if not st.session_state.auth:
    # Contenedor centrado
    col1, col2, col3 = st.columns([1, 1.2, 1])
    with col2:
        st.markdown('<div class="modern-card">', unsafe_allow_html=True)
        
        # Logo y título
        st.markdown("""
        <div class="logo-wrapper">
            <img src="https://cdn-icons-png.flaticon.com/512/2917/2917995.png" class="logo-img">
            <div class="app-title">SG-SST PHVA</div>
            <div class="app-slogan">✨ Seguridad y Salud, compromiso de todos ✨</div>
        </div>
        """, unsafe_allow_html=True)
        
        # Formulario
        with st.form("login_moderno"):
            # Usuario con icono (el CSS agrega el icono)
            username = st.text_input("", placeholder="Usuario", label_visibility="collapsed", key="user_input")
            password = st.text_input("", type="password", placeholder="Contraseña", label_visibility="collapsed", key="pass_input")
            
            submitted = st.form_submit_button("🚀 INGRESAR AL SISTEMA", use_container_width=True)
            
            if submitted:
                user = verificar_login(username, password)
                if user:
                    st.session_state.auth = True
                    st.session_state.user = user
                    st.rerun()
                else:
                    st.error("❌ Usuario o contraseña incorrectos")
        
        # Enlace de ayuda
        st.markdown("""
        <div class="forgot-link">
            <a href="#">🔐 ¿Olvidaste tu contraseña? Contacta al administrador</a>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Footer
    st.markdown("""
    <div class="footer-modern">
        🛡️ SG-SST PHVA | Sistema de Gestión con IA | Desarrollado por JAN BENITEZ
    </div>
    """, unsafe_allow_html=True)
    st.stop()

# DASHBOARD POST-LOGIN (simple por ahora)
st.markdown("""
<style>
    .dashboard-header {
        background: linear-gradient(135deg, #667eea, #764ba2);
        padding: 20px;
        border-radius: 20px;
        margin-bottom: 20px;
        text-align: center;
    }
    .welcome-text {
        font-size: 24px;
        font-weight: 600;
        color: white;
    }
</style>
""", unsafe_allow_html=True)

st.markdown(f"""
<div class="dashboard-header">
    <div class="welcome-text">👋 ¡Bienvenido, {st.session_state.user['nombre']}!</div>
    <p style="color:rgba(255,255,255,0.8); margin-top:5px">Rol: {st.session_state.user['rol'].upper()}</p>
</div>
""", unsafe_allow_html=True)

if st.button("🚪 Cerrar Sesión", use_container_width=True):
    st.session_state.auth = False
    st.rerun()

st.info("📌 Próximamente: Módulos de Matriz Legal, Auditorías, Plan Anual y más...")
