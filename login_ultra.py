import streamlit as st
import sqlite3
import pandas as pd
import requests
from datetime import datetime

st.set_page_config(page_title="SG-SST", page_icon="🔄", layout="centered")

# CSS que SÍ funciona
st.markdown("""
<style>
    /* Ocultar todo el padding de Streamlit */
    .main > div {
        padding: 0 !important;
    }
    
    .block-container {
        padding: 0.5rem !important;
        max-width: 200px !important;
    }
    
    /* Tarjeta pequeña */
    .stForm {
        background: rgba(255,255,255,0.1);
        backdrop-filter: blur(10px);
        border-radius: 12px;
        padding: 15px 10px !important;
        width: 180px;
        margin: 0 auto;
    }
    
    /* Inputs pequeños */
    .stTextInput > div > div > input {
        background: rgba(255,255,255,0.2) !important;
        border: none !important;
        border-radius: 6px !important;
        color: white !important;
        padding: 4px 8px !important;
        font-size: 11px !important;
        height: 28px !important;
    }
    
    /* Botón pequeño */
    .stButton > button {
        background: #667eea !important;
        border-radius: 6px !important;
        padding: 4px !important;
        font-size: 11px !important;
        height: 30px !important;
    }
    
    /* Texto pequeño */
    p, h1, h2, h3, label {
        margin: 0 !important;
        padding: 0 !important;
    }
    
    .st-emotion-cache-1v0mbdj {
        width: 180px !important;
    }
    
    footer {
        display: none;
    }
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

def verificar(u,p):
    cursor.execute("SELECT * FROM usuarios WHERE username=? AND password=?", (u,p))
    r = cursor.fetchone()
    return {"nombre": r[3], "rol": r[4]} if r else None

if "auth" not in st.session_state:
    st.session_state.auth = False

if not st.session_state.auth:
    # Logo pequeño
    st.image("https://cdn-icons-png.flaticon.com/512/2917/2917995.png", width=40)
    st.markdown("<h3 style='text-align:center; color:white; font-size:14px; margin:0'>SG-SST PHVA</h3>", unsafe_allow_html=True)
    st.markdown("<p style='text-align:center; color:gray; font-size:9px; margin:0'>Seguridad y Salud</p>", unsafe_allow_html=True)
    
    with st.form("login"):
        u = st.text_input("Usuario", placeholder="usuario", label_visibility="collapsed")
        p = st.text_input("Clave", type="password", placeholder="clave", label_visibility="collapsed")
        if st.form_submit_button("Ingresar", use_container_width=True):
            user = verificar(u,p)
            if user:
                st.session_state.auth = True
                st.session_state.user = user
                st.rerun()
            else:
                st.error("Error")
    
    st.stop()

st.success(f"Bienvenido {st.session_state.user['nombre']}")
if st.button("Salir"):
    st.session_state.auth = False
    st.rerun()
