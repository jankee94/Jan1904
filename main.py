import streamlit as st
import sqlite3
import pandas as pd
from modules import dashboard, diagnostico_ia, peligros, acciones, trabajadores, incidentes, chat_ia

st.set_page_config(page_title="SG-SST PHVA", page_icon="🔄", layout="wide")

# CSS PROFESIONAL
st.markdown("""
<style>
    .stApp {
        background: linear-gradient(135deg, #0f0c29 0%, #302b63 50%, #24243e 100%);
    }
    header[data-testid="stHeader"] {
        display: none;
    }
    footer {
        display: none !important;
    }
    .stButton > button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
        border: none !important;
        border-radius: 12px !important;
        padding: 8px 16px !important;
        font-weight: 600 !important;
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
    rol TEXT DEFAULT 'trabajador'
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
if "empresa_actual_id" not in st.session_state:
    st.session_state.empresa_actual_id = None

if not st.session_state.auth:
    st.markdown("""
    <div style="display: flex; align-items: center; justify-content: center; height: 100vh;">
        <div style="background: rgba(20,20,40,0.75); backdrop-filter: blur(14px); border-radius: 28px; padding: 40px; width: 360px;">
            <div style="text-align:center">
                <img src="https://cdn-icons-png.flaticon.com/512/2917/2917995.png" width="60">
                <h1 style="color:white; font-size:24px; margin:10px 0">SG-SST PHVA</h1>
                <p style="color:rgba(255,255,255,0.6); font-size:12px">✨ Seguridad y Salud, compromiso de todos ✨</p>
            </div>
    """, unsafe_allow_html=True)
    
    with st.form("login"):
        username = st.text_input("Usuario", placeholder="Ingrese su usuario")
        password = st.text_input("Contraseña", type="password", placeholder="Ingrese su contraseña")
        if st.form_submit_button("Ingresar", use_container_width=True):
            user = verificar_login(username, password)
            if user:
                st.session_state.auth = True
                st.session_state.user = user
                st.rerun()
            else:
                st.error("Usuario o contraseña incorrectos")
    
    st.markdown("""
            <div style="text-align:center; margin-top:20px; font-size:10px; color:rgba(255,255,255,0.3)">
                🛡️ SG-SST PHVA | Desarrollado por JAN BENITEZ
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    st.stop()

# SIDEBAR
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/2917/2917995.png", width=50)
    st.markdown(f"**👤 {st.session_state.user['nombre']}**")
    st.markdown(f"**Rol:** {st.session_state.user['rol'].upper()}")
    st.markdown("---")
    
    menu = st.radio("📋 MENU", [
        "📊 Dashboard",
        "🤖 Diagnóstico IA",
        "⚠️ Peligros",
        "✅ Plan de Acción",
        "👥 Trabajadores",
        "📝 Incidentes",
        "💬 Chat IA"
    ])
    
    if st.button("🚪 Cerrar Sesión", use_container_width=True):
        st.session_state.auth = False
        st.rerun()

# RENDER MODULOS
if menu == "📊 Dashboard":
    dashboard.render()
elif menu == "🤖 Diagnóstico IA":
    diagnostico_ia.render()
elif menu == "⚠️ Peligros":
    peligros.render()
elif menu == "✅ Plan de Acción":
    from modules.acciones import render as acciones_render
    acciones_render()
elif menu == "👥 Trabajadores":
    from modules.trabajadores import render as trabajadores_render
    trabajadores_render()
elif menu == "📝 Incidentes":
    from modules.incidentes import render as incidentes_render
    incidentes_render()
elif menu == "💬 Chat IA":
    from modules.chat_ia import render as chat_render
    chat_render()
