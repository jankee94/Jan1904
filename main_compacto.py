import streamlit as st
from datetime import datetime, timedelta
import sqlite3
import pandas as pd
import requests

st.set_page_config(page_title="SG-SST PHVA", page_icon="🔄", layout="wide")

st.markdown("""
<style>
    .stApp { background: linear-gradient(135deg, #0f0c29 0%, #302b63 50%, #24243e 100%); }
    .login-card { background: rgba(255,255,255,0.08); backdrop-filter: blur(12px); border-radius: 20px; padding: 20px 15px; }
    .stTextInput > div > div > input { background: rgba(255,255,255,0.1) !important; border: 1px solid rgba(255,255,255,0.2) !important; border-radius: 10px !important; color: white !important; }
    .stButton > button { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important; border-radius: 10px !important; }
    .developer-footer { position: fixed; bottom: 0; left: 0; right: 0; text-align: center; padding: 8px; background: rgba(0,0,0,0.6); font-size: 10px; color: white; z-index: 999; }
</style>
""", unsafe_allow_html=True)

conn = sqlite3.connect("sst.db", check_same_thread=False)
cursor = conn.cursor()

cursor.execute('''CREATE TABLE IF NOT EXISTS usuarios (id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT UNIQUE, password TEXT, nombre TEXT, rol TEXT DEFAULT 'trabajador', activo INTEGER DEFAULT 1)''')
cursor.execute('''CREATE TABLE IF NOT EXISTS empresa (id INTEGER PRIMARY KEY AUTOINCREMENT, nit TEXT, nombre TEXT, trabajadores INTEGER, arl TEXT, diagnostico TEXT, fecha TEXT)''')
cursor.execute('''CREATE TABLE IF NOT EXISTS peligros (id INTEGER PRIMARY KEY AUTOINCREMENT, empresa_id INTEGER, tipo TEXT, descripcion TEXT, probabilidad INTEGER, severidad INTEGER, nivel TEXT)''')
cursor.execute('''CREATE TABLE IF NOT EXISTS acciones (id INTEGER PRIMARY KEY AUTOINCREMENT, empresa_id INTEGER, descripcion TEXT, responsable TEXT, fecha TEXT, estado TEXT)''')
cursor.execute('''CREATE TABLE IF NOT EXISTS trabajadores (id INTEGER PRIMARY KEY AUTOINCREMENT, empresa_id INTEGER, nombre TEXT, cedula TEXT, cargo TEXT)''')
cursor.execute('''CREATE TABLE IF NOT EXISTS incidentes (id INTEGER PRIMARY KEY AUTOINCREMENT, empresa_id INTEGER, descripcion TEXT, fecha TEXT, gravedad TEXT)''')

cursor.execute("SELECT * FROM usuarios WHERE username = 'admin'")
if not cursor.fetchone():
    cursor.execute("INSERT INTO usuarios (username, password, nombre, rol) VALUES (?, ?, ?, ?)", ('admin', 'admin123', 'Administrador', 'admin'))
    conn.commit()
conn.commit()

def verificar_login(username, password):
    cursor.execute("SELECT * FROM usuarios WHERE username = ? AND password = ? AND activo = 1", (username, password))
    user = cursor.fetchone()
    if user:
        return {"id": user[0], "username": user[1], "nombre": user[3], "rol": user[4]}
    return None

def guardar_diagnostico(nit, nombre, trabajadores, arl, diagnostico):
    cursor.execute("INSERT INTO empresa (nit, nombre, trabajadores, arl, diagnostico, fecha) VALUES (?, ?, ?, ?, ?, ?)", (nit, nombre, trabajadores, arl, diagnostico, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
    conn.commit()
    return cursor.lastrowid

def obtener_diagnosticos():
    return pd.read_sql_query("SELECT id, nit, nombre, trabajadores, arl, fecha FROM empresa ORDER BY id DESC", conn)

def obtener_diagnostico_por_id(id):
    df = pd.read_sql_query("SELECT * FROM empresa WHERE id = ?", conn, params=(id,))
    return df.iloc[0].to_dict() if not df.empty else None

def set_empresa_actual(id):
    st.session_state.empresa_actual_id = id
    st.session_state.empresa_actual = obtener_diagnostico_por_id(id)

def call_ia(prompt):
    try:
        url = "https://generativelanguage.googleapis.com/v1/models/gemini-pro:generateContent"
        headers = {"Content-Type": "application/json", "x-goog-api-key": "AIzaSyD3QhEohGJeYhVtM7JmBZ2nXvZJFxJZv3U"}
        r = requests.post(url, json={"contents": [{"parts": [{"text": prompt}]}]}, headers=headers, timeout=30)
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
if "empresa_actual" not in st.session_state:
    st.session_state.empresa_actual = None

if not st.session_state.auth:
    col1, col2, col3 = st.columns([1, 1.2, 1])
    with col2:
        st.markdown('<div class="login-card"><div style="text-align:center"><img src="https://cdn-icons-png.flaticon.com/512/2917/2917995.png" style="width:40px"><h1 style="font-size:18px;color:white">SG-SST PHVA</h1><p style="font-size:10px;color:gray">Seguridad y Salud</p></div>', unsafe_allow_html=True)
        with st.form("login_form"):
            username = st.text_input("Usuario", placeholder="usuario", label_visibility="collapsed")
            password = st.text_input("Contraseña", type="password", placeholder="contraseña", label_visibility="collapsed")
            if st.form_submit_button("Ingresar", use_container_width=True):
                user = verificar_login(username, password)
                if user:
                    st.session_state.auth = True
                    st.session_state.user = user
                    st.rerun()
                else:
                    st.error("Error")
        st.markdown("</div>", unsafe_allow_html=True)
    st.markdown('<div class="developer-footer">DESARROLLADO POR JAN BENITEZ</div>', unsafe_allow_html=True)
    st.stop()

with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/2917/2917995.png", width=40)
    st.markdown(f"**{st.session_state.user['nombre']}**")
    if st.session_state.user['rol'] == 'admin':
        diagnosticos = obtener_diagnosticos()
        if not diagnosticos.empty:
            opts = diagnosticos.apply(lambda x: f"{x['id']} - {x['nombre']}", axis=1).tolist()
            sel = st.selectbox("Empresa", ["-- Nueva --"] + opts)
            if sel != "-- Nueva --":
                id_emp = int(sel.split(" - ")[0])
                if st.session_state.empresa_actual_id != id_emp:
                    set_empresa_actual(id_emp)
                    st.rerun()
    if st.session_state.empresa_actual:
        st.info(f"🏢 {st.session_state.empresa_actual.get('nombre', '')}")
    menu = st.radio("MENU", ["Dashboard", "Diagnostico IA", "Peligros", "Plan Accion", "Trabajadores", "Incidentes", "Chat IA"])
    if st.button("Salir"):
        st.session_state.auth = False
        st.rerun()

if menu == "Dashboard":
    st.title("Dashboard")
    if st.session_state.empresa_actual:
        st.success(f"Empresa: {st.session_state.empresa_actual.get('nombre')}")
    else:
        st.warning("Cree una empresa en Diagnostico IA")

elif menu == "Diagnostico IA":
    st.title("Diagnostico IA")
    with st.form("f"):
        nombre = st.text_input("Nombre empresa")
        trabajadores = st.number_input("Trabajadores", 1, 1000, 10)
        arl = st.selectbox("ARL", ["Positiva", "Sura", "Colpatria"])
        if st.form_submit_button("Generar"):
            if nombre:
                resp = call_ia(f"Diagnostico SST para {nombre}")
                id_emp = guardar_diagnostico("", nombre, trabajadores, arl, resp)
                set_empresa_actual(id_emp)
                st.success("Listo")
                st.rerun()

elif menu == "Peligros":
    st.title("Peligros")
    if st.session_state.empresa_actual_id:
        df = pd.read_sql_query("SELECT * FROM peligros WHERE empresa_id = ?", conn, params=(st.session_state.empresa_actual_id,))
        st.dataframe(df)
        with st.form("add"):
            tipo = st.selectbox("Tipo", ["Fisico", "Quimico", "Biologico", "Ergonomico"])
            desc = st.text_area("Descripcion")
            if st.form_submit_button("Guardar"):
                cursor.execute("INSERT INTO peligros (empresa_id, tipo, descripcion) VALUES (?, ?, ?)", (st.session_state.empresa_actual_id, tipo, desc))
                conn.commit()
                st.rerun()

elif menu == "Plan Accion":
    st.title("Plan Accion")
    if st.session_state.empresa_actual_id:
        df = pd.read_sql_query("SELECT * FROM acciones WHERE empresa_id = ?", conn, params=(st.session_state.empresa_actual_id,))
        st.dataframe(df)
        with st.form("add"):
            desc = st.text_area("Accion")
            resp = st.text_input("Responsable")
            if st.form_submit_button("Guardar"):
                cursor.execute("INSERT INTO acciones (empresa_id, descripcion, responsable, estado) VALUES (?, ?, ?, ?)", (st.session_state.empresa_actual_id, desc, resp, "Pendiente"))
                conn.commit()
                st.rerun()

elif menu == "Trabajadores":
    st.title("Trabajadores")
    if st.session_state.empresa_actual_id:
        df = pd.read_sql_query("SELECT * FROM trabajadores WHERE empresa_id = ?", conn, params=(st.session_state.empresa_actual_id,))
        st.dataframe(df)
        with st.form("add"):
            nombre = st.text_input("Nombre")
            cedula = st.text_input("Cedula")
            cargo = st.text_input("Cargo")
            if st.form_submit_button("Guardar"):
                cursor.execute("INSERT INTO trabajadores (empresa_id, nombre, cedula, cargo) VALUES (?, ?, ?, ?)", (st.session_state.empresa_actual_id, nombre, cedula, cargo))
                conn.commit()
                st.rerun()

elif menu == "Incidentes":
    st.title("Incidentes")
    if st.session_state.empresa_actual_id:
        with st.form("add"):
            desc = st.text_area("Descripcion")
            gravedad = st.selectbox("Gravedad", ["Leve", "Moderada", "Grave"])
            if st.form_submit_button("Reportar"):
                cursor.execute("INSERT INTO incidentes (empresa_id, descripcion, fecha, gravedad) VALUES (?, ?, ?, ?)", (st.session_state.empresa_actual_id, desc, datetime.now().strftime("%Y-%m-%d"), gravedad))
                conn.commit()
                st.rerun()
        df = pd.read_sql_query("SELECT * FROM incidentes WHERE empresa_id = ?", conn, params=(st.session_state.empresa_actual_id,))
        st.dataframe(df)

elif menu == "Chat IA":
    st.title("Chat IA")
    if "msgs" not in st.session_state:
        st.session_state.msgs = []
    for msg in st.session_state.msgs:
        with st.chat_message(msg["role"]):
            st.write(msg["content"])
    if prompt := st.chat_input("Pregunta..."):
        st.session_state.msgs.append({"role": "user", "content": prompt})
        respuesta = call_ia(prompt)
        st.session_state.msgs.append({"role": "assistant", "content": respuesta})
        st.rerun()

st.markdown('<div class="developer-footer">SG-SST PHVA | DESARROLLADO POR JAN BENITEZ</div>', unsafe_allow_html=True)
