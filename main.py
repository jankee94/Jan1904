import streamlit as st
import sqlite3
import pandas as pd
import requests
from datetime import datetime

st.set_page_config(page_title="SG-SST", page_icon="🔄", layout="centered")

# CSS ultra compacto
st.markdown("""
<style>
    .block-container {
        padding: 0.2rem !important;
        max-width: 220px !important;
    }
    .stTextInput > div > div > input {
        background: rgba(255,255,255,0.15) !important;
        border: none !important;
        border-radius: 8px !important;
        color: white !important;
        padding: 5px 10px !important;
        font-size: 12px !important;
        height: 32px !important;
    }
    .stButton > button {
        background: linear-gradient(135deg, #667eea, #764ba2) !important;
        border-radius: 8px !important;
        padding: 5px !important;
        font-size: 12px !important;
        height: 35px !important;
        width: 100% !important;
    }
    .stForm {
        background: rgba(255,255,255,0.08);
        backdrop-filter: blur(10px);
        border-radius: 15px;
        padding: 15px !important;
    }
    .st-emotion-cache-1v0mbdj {
        width: 220px !important;
    }
    footer { display: none; }
    hr { margin: 8px 0 !important; }
</style>
""", unsafe_allow_html=True)

# Base de datos
conn = sqlite3.connect("sst.db", check_same_thread=False)
cursor = conn.cursor()

cursor.execute('''CREATE TABLE IF NOT EXISTS usuarios (id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT, password TEXT, nombre TEXT, rol TEXT)''')
cursor.execute("SELECT * FROM usuarios WHERE username='admin'")
if not cursor.fetchone():
    cursor.execute("INSERT INTO usuarios (username, password, nombre, rol) VALUES (?,?,?,?)", ('admin','admin123','Admin','admin'))
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

# LOGIN ULTRA COMPACTO
if not st.session_state.auth:
    st.markdown("<div style='text-align:center'>", unsafe_allow_html=True)
    st.image("https://cdn-icons-png.flaticon.com/512/2917/2917995.png", width=40)
    st.markdown("<h3 style='color:white; font-size:16px; margin:2px 0'>SG-SST PHVA</h3>", unsafe_allow_html=True)
    st.markdown("<p style='color:gray; font-size:10px; margin:0'>Seguridad y Salud</p>", unsafe_allow_html=True)
    st.markdown("<hr>", unsafe_allow_html=True)
    
    with st.form("login"):
        u = st.text_input("Usuario", placeholder="usuario", label_visibility="collapsed")
        p = st.text_input("Clave", type="password", placeholder="clave", label_visibility="collapsed")
        if st.form_submit_button("Ingresar", use_container_width=True):
            user = verificar_login(u, p)
            if user:
                st.session_state.auth = True
                st.session_state.user = user
                st.rerun()
            else:
                st.error("Usuario o clave incorrectos")
    st.markdown("</div>", unsafe_allow_html=True)
    st.stop()

# Dashboard después del login
st.success(f"✅ Bienvenido {st.session_state.user['nombre']}")
if st.button("Cerrar Sesión"):
    st.session_state.auth = False
    st.rerun()

st.info("📌 Módulos en construcción... Próximamente: Matriz Legal, Auditorías, Plan Anual")
