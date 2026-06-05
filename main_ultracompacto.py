import streamlit as st
from datetime import datetime
import sqlite3
import pandas as pd
import requests

st.set_page_config(page_title="SG-SST", page_icon="🔄", layout="wide")

# CSS ultra compacto
st.markdown("""
<style>
    .stApp { background: linear-gradient(135deg, #0f0c29, #302b63, #24243e); }
    .login-card { background: rgba(255,255,255,0.1); backdrop-filter: blur(10px); border-radius: 15px; padding: 15px 10px !important; margin: 10px auto !important; max-width: 280px !important; }
    .stTextInput > div > div > input { background: rgba(255,255,255,0.15) !important; border: none !important; border-radius: 8px !important; color: white !important; padding: 6px 10px !important; font-size: 13px !important; height: 35px !important; }
    .stButton > button { background: linear-gradient(135deg, #667eea, #764ba2) !important; border-radius: 8px !important; padding: 5px !important; font-size: 13px !important; height: 35px !important; }
    .developer-footer { position: fixed; bottom: 0; left: 0; right: 0; text-align: center; padding: 5px; background: rgba(0,0,0,0.5); font-size: 9px; color: rgba(255,255,255,0.6); z-index: 999; }
    div[data-testid="stForm"] { padding: 5px !important; }
    .stMarkdown div { margin: 0 !important; }
</style>
""", unsafe_allow_html=True)

conn = sqlite3.connect("sst.db", check_same_thread=False)
cursor = conn.cursor()

cursor.execute('''CREATE TABLE IF NOT EXISTS usuarios (id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT UNIQUE, password TEXT, nombre TEXT, rol TEXT, activo INTEGER DEFAULT 1)''')
cursor.execute('''CREATE TABLE IF NOT EXISTS empresa (id INTEGER PRIMARY KEY AUTOINCREMENT, nit TEXT, nombre TEXT, trabajadores INTEGER, arl TEXT, diagnostico TEXT, fecha TEXT)''')
cursor.execute('''CREATE TABLE IF NOT EXISTS peligros (id INTEGER PRIMARY KEY AUTOINCREMENT, empresa_id INTEGER, tipo TEXT, descripcion TEXT)''')
cursor.execute('''CREATE TABLE IF NOT EXISTS acciones (id INTEGER PRIMARY KEY AUTOINCREMENT, empresa_id INTEGER, descripcion TEXT, responsable TEXT, estado TEXT)''')
cursor.execute('''CREATE TABLE IF NOT EXISTS trabajadores (id INTEGER PRIMARY KEY AUTOINCREMENT, empresa_id INTEGER, nombre TEXT, cedula TEXT, cargo TEXT)''')
cursor.execute('''CREATE TABLE IF NOT EXISTS incidentes (id INTEGER PRIMARY KEY AUTOINCREMENT, empresa_id INTEGER, descripcion TEXT, fecha TEXT, gravedad TEXT)''')

cursor.execute("SELECT * FROM usuarios WHERE username = 'admin'")
if not cursor.fetchone():
    cursor.execute("INSERT INTO usuarios (username, password, nombre, rol) VALUES (?, ?, ?, ?)", ('admin', 'admin123', 'Admin', 'admin'))
    conn.commit()
conn.commit()

def verificar_login(u, p):
    cursor.execute("SELECT * FROM usuarios WHERE username = ? AND password = ? AND activo = 1", (u, p))
    r = cursor.fetchone()
    return {"id": r[0], "username": r[1], "nombre": r[3], "rol": r[4]} if r else None

def call_ia(prompt):
    try:
        url = "https://generativelanguage.googleapis.com/v1/models/gemini-pro:generateContent"
        headers = {"Content-Type": "application/json", "x-goog-api-key": "AIzaSyD3QhEohGJeYhVtM7JmBZ2nXvZJFxJZv3U"}
        r = requests.post(url, json={"contents": [{"parts": [{"text": prompt}]}]}, headers=headers, timeout=15)
        if r.status_code == 200:
            return r.json()["candidates"][0]["content"]["parts"][0]["text"]
    except:
        pass
    return "IA no disponible"

if "auth" not in st.session_state:
    st.session_state.auth = False
if "user" not in st.session_state:
    st.session_state.user = None
if "empresa_actual_id" not in st.session_state:
    st.session_state.empresa_actual_id = None

# LOGIN ULTRA COMPACTO
if not st.session_state.auth:
    col1, col2, col3 = st.columns([1, 0.8, 1])
    with col2:
        st.markdown('<div class="login-card" style="text-align:center">', unsafe_allow_html=True)
        st.image("https://cdn-icons-png.flaticon.com/512/2917/2917995.png", width=35)
        st.markdown('<h3 style="color:white; margin:2px 0; font-size:16px">SG-SST PHVA</h3>', unsafe_allow_html=True)
        st.markdown('<p style="color:rgba(255,255,255,0.7); font-size:9px; margin:0">Seguridad y Salud</p>', unsafe_allow_html=True)
        st.markdown('<hr style="margin:8px 0">', unsafe_allow_html=True)
        
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
                    st.error("Error")
        st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown('<div class="developer-footer">JAN BENITEZ</div>', unsafe_allow_html=True)
    st.stop()

# SIDEBAR
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/2917/2917995.png", width=35)
    st.markdown(f"**{st.session_state.user['nombre']}**")
    st.caption(f"{st.session_state.user['rol'].upper()}")
    st.markdown("---")
    
    if st.session_state.user['rol'] == 'admin':
        df = pd.read_sql_query("SELECT id, nombre FROM empresa", conn)
        if not df.empty:
            opts = df.apply(lambda x: f"{x['id']} - {x['nombre']}", axis=1).tolist()
            sel = st.selectbox("Empresa", ["-- Nueva --"] + opts, key="emp_sel")
            if sel != "-- Nueva --":
                st.session_state.empresa_actual_id = int(sel.split(" - ")[0])
    
    menu = st.radio("", ["Dashboard", "Diagnóstico", "Peligros", "Acciones", "Chat"], label_visibility="collapsed")
    if st.button("Salir"):
        st.session_state.auth = False
        st.rerun()

# DASHBOARD
if menu == "Dashboard":
    st.title("Dashboard")
    if st.session_state.empresa_actual_id:
        df_p = pd.read_sql_query("SELECT * FROM peligros WHERE empresa_id = ?", conn, params=(st.session_state.empresa_actual_id,))
        df_a = pd.read_sql_query("SELECT * FROM acciones WHERE empresa_id = ?", conn, params=(st.session_state.empresa_actual_id,))
        col1, col2, col3 = st.columns(3)
        with col1: st.metric("Peligros", len(df_p))
        with col2: st.metric("Acciones", len(df_a))
        with col3: st.metric("Cumplimiento", "0%")
    else:
        st.info("Seleccione o cree una empresa en Diagnóstico")

# DIAGNÓSTICO
elif menu == "Diagnóstico":
    st.title("Diagnóstico IA")
    with st.form("diag"):
        nombre = st.text_input("Nombre empresa")
        trabajadores = st.number_input("Trabajadores", 1, 500, 10)
        if st.form_submit_button("Generar"):
            if nombre:
                resp = call_ia(f"Diagnóstico SST para {nombre}")
                cursor.execute("INSERT INTO empresa (nombre, trabajadores, diagnostico, fecha) VALUES (?, ?, ?, ?)", (nombre, trabajadores, resp, datetime.now().strftime("%Y-%m-%d")))
                conn.commit()
                st.session_state.empresa_actual_id = cursor.lastrowid
                st.success("✅ Creado")
                st.rerun()

# PELIGROS
elif menu == "Peligros":
    st.title("Peligros")
    if st.session_state.empresa_actual_id:
        with st.form("add"):
            tipo = st.selectbox("Tipo", ["Físico", "Químico", "Biológico", "Ergonómico"])
            desc = st.text_area("Descripción")
            if st.form_submit_button("Guardar"):
                cursor.execute("INSERT INTO peligros (empresa_id, tipo, descripcion) VALUES (?, ?, ?)", (st.session_state.empresa_actual_id, tipo, desc))
                conn.commit()
                st.rerun()
        df = pd.read_sql_query("SELECT * FROM peligros WHERE empresa_id = ?", conn, params=(st.session_state.empresa_actual_id,))
        st.dataframe(df, use_container_width=True)

# ACCIONES
elif menu == "Acciones":
    st.title("Plan de Acción")
    if st.session_state.empresa_actual_id:
        with st.form("add"):
            desc = st.text_area("Acción")
            resp = st.text_input("Responsable")
            if st.form_submit_button("Guardar"):
                cursor.execute("INSERT INTO acciones (empresa_id, descripcion, responsable, estado) VALUES (?, ?, ?, ?)", (st.session_state.empresa_actual_id, desc, resp, "Pendiente"))
                conn.commit()
                st.rerun()
        df = pd.read_sql_query("SELECT * FROM acciones WHERE empresa_id = ?", conn, params=(st.session_state.empresa_actual_id,))
        st.dataframe(df, use_container_width=True)

# CHAT
elif menu == "Chat":
    st.title("Chat IA")
    if "msgs" not in st.session_state:
        st.session_state.msgs = []
    for m in st.session_state.msgs:
        with st.chat_message(m["role"]):
            st.write(m["content"])
    if p := st.chat_input("Pregunta..."):
        st.session_state.msgs.append({"role": "user", "content": p})
        r = call_ia(p)
        st.session_state.msgs.append({"role": "assistant", "content": r})
        st.rerun()

st.markdown('<div class="developer-footer">SG-SST PHVA | DESARROLLADO POR JAN BENITEZ</div>', unsafe_allow_html=True)
