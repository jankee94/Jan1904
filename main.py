import streamlit as st
import sqlite3
import pandas as pd
import requests
import itertools
from datetime import datetime
import io

st.set_page_config(page_title="SG-SST PHVA", page_icon="🔄", layout="wide")

# ========== CSS ==========
st.markdown('''
<style>
    .stApp { background: linear-gradient(135deg, #0f0c29 0%, #302b63 50%, #24243e 100%); }
    header[data-testid="stHeader"] { display: none; }
    footer { display: none !important; }
    .stButton > button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
        border: none !important;
        border-radius: 12px !important;
        font-weight: 600 !important;
    }
    [data-testid="stSidebar"] {
        background: rgba(20, 20, 40, 0.5);
        backdrop-filter: blur(10px);
    }
</style>
''', unsafe_allow_html=True)

# ========== IA ==========
def get_gemini_keys():
    keys = []
    i = 1
    while True:
        key = st.secrets.get(f"GEMINI_API_KEY_{i}")
        if not key:
            break
        keys.append(key)
        i += 1
    if not keys:
        old_key = st.secrets.get("GEMINI_API_KEY")
        if old_key:
            keys.append(old_key)
    return keys

def get_groq_key():
    return st.secrets.get("GROQ_API_KEY")

GEMINI_KEYS = get_gemini_keys()
GROQ_KEY = get_groq_key()
gemini_cycle = itertools.cycle(GEMINI_KEYS) if GEMINI_KEYS else None

def call_gemini(prompt):
    if not GEMINI_KEYS:
        return None
    for _ in range(len(GEMINI_KEYS)):
        key = next(gemini_cycle)
        try:
            url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-flash-latest:generateContent"
            headers = {"Content-Type": "application/json", "x-goog-api-key": key}
            data = {"contents": [{"parts": [{"text": prompt}]}]}
            r = requests.post(url, json=data, headers=headers, timeout=30)
            if r.status_code == 200:
                return r.json()["candidates"][0]["content"]["parts"][0]["text"]
        except:
            continue
    return None

def call_groq(prompt):
    if not GROQ_KEY:
        return None
    try:
        url = "https://api.groq.com/openai/v1/chat/completions"
        headers = {"Authorization": f"Bearer {GROQ_KEY}", "Content-Type": "application/json"}
        data = {"model": "llama-3.3-70b-versatile", "messages": [{"role": "user", "content": prompt}], "temperature": 0.7}
        r = requests.post(url, json=data, headers=headers, timeout=30)
        if r.status_code == 200:
            return r.json()["choices"][0]["message"]["content"]
    except:
        pass
    return None

def call_best_ia(prompt):
    respuesta = call_gemini(prompt)
    if respuesta:
        return respuesta
    respuesta = call_groq(prompt)
    if respuesta:
        return respuesta
    return "⚠️ No se pudo obtener respuesta de ninguna IA."

# ========== BASE DE DATOS ==========
conn = sqlite3.connect("sst.db", check_same_thread=False)
cursor = conn.cursor()

# Tablas
cursor.execute('''CREATE TABLE IF NOT EXISTS usuarios (id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT UNIQUE, password TEXT, nombre TEXT, rol TEXT)''')
cursor.execute('''CREATE TABLE IF NOT EXISTS peligros (id INTEGER PRIMARY KEY AUTOINCREMENT, empresa_id INTEGER, tipo TEXT, descripcion TEXT, probabilidad INTEGER, severidad INTEGER, nivel TEXT)''')
cursor.execute('''CREATE TABLE IF NOT EXISTS acciones (id INTEGER PRIMARY KEY AUTOINCREMENT, empresa_id INTEGER, descripcion TEXT, responsable TEXT, fecha TEXT, estado TEXT)''')
cursor.execute('''CREATE TABLE IF NOT EXISTS trabajadores (id INTEGER PRIMARY KEY AUTOINCREMENT, empresa_id INTEGER, nombre TEXT, cedula TEXT, cargo TEXT)''')
cursor.execute('''CREATE TABLE IF NOT EXISTS incidentes (id INTEGER PRIMARY KEY AUTOINCREMENT, empresa_id INTEGER, descripcion TEXT, fecha TEXT, gravedad TEXT)''')
cursor.execute('''CREATE TABLE IF NOT EXISTS empresa_config (id INTEGER PRIMARY KEY AUTOINCREMENT, nombre TEXT, nit TEXT, ubicacion TEXT, ciudad TEXT, sector TEXT, telefono TEXT, email TEXT)''')
cursor.execute('''CREATE TABLE IF NOT EXISTS matriz_legal (id INTEGER PRIMARY KEY AUTOINCREMENT, empresa_id INTEGER, norma TEXT, articulo TEXT, requisito TEXT, cumple INTEGER)''')
cursor.execute('''CREATE TABLE IF NOT EXISTS auditorias (id INTEGER PRIMARY KEY AUTOINCREMENT, empresa_id INTEGER, codigo TEXT, fecha TEXT, auditor_id TEXT, puntuacion INTEGER)''')
cursor.execute('''CREATE TABLE IF NOT EXISTS plan_anual (id INTEGER PRIMARY KEY AUTOINCREMENT, empresa_id INTEGER, anio INTEGER, actividad TEXT, mes_programado INTEGER, responsable TEXT, cumplimiento INTEGER)''')

# Usuario admin
cursor.execute("SELECT * FROM usuarios WHERE username='admin'")
if not cursor.fetchone():
    cursor.execute("INSERT INTO usuarios (username, password, nombre, rol) VALUES (?,?,?,?)", ('admin', 'admin123', 'Administrador', 'admin'))
    conn.commit()

# Datos empresa por defecto
cursor.execute("SELECT COUNT(*) FROM empresa_config")
if cursor.fetchone()[0] == 0:
    cursor.execute("INSERT INTO empresa_config (nombre, nit, ubicacion, ciudad, sector, telefono, email) VALUES (?,?,?,?,?,?,?)", ('Mi Empresa SAS', '900.000.000-1', 'Calle 123', 'Bogota', 'Servicios', '6011234567', 'contacto@miempresa.com'))
    conn.commit()

conn.commit()

def verificar_login(username, password):
    cursor.execute("SELECT * FROM usuarios WHERE username=? AND password=?", (username, password))
    user = cursor.fetchone()
    if user:
        return {"id": user[0], "username": user[1], "nombre": user[3], "rol": user[4]}
    return None

def get_empresa_data():
    cursor.execute("SELECT nombre, nit, ubicacion, ciudad, sector FROM empresa_config LIMIT 1")
    data = cursor.fetchone()
    if data:
        return {"nombre": data[0], "nit": data[1], "ubicacion": data[2], "ciudad": data[3], "sector": data[4]}
    return {}

# ========== DATOS DE PRUEBA ==========
def cargar_datos_prueba():
    with st.spinner("Cargando datos de prueba..."):
        cursor.execute("SELECT COUNT(*) FROM peligros")
        if cursor.fetchone()[0] == 0:
            # Peligros
            peligros = [("Fisico", "Ruido excesivo", 3, 2, "II"), ("Ergonomico", "Posturas prolongadas", 2, 2, "II"), ("Quimico", "Exposicion a solventes", 2, 3, "I")]
            for p in peligros:
                cursor.execute("INSERT INTO peligros (empresa_id, tipo, descripcion, probabilidad, severidad, nivel) VALUES (1,?,?,?,?,?)", p)
            # Acciones
            acciones = [("Implementar barreras acusticas", "Coordinador SST", "2024-12-15", "En progreso"), ("Capacitacion pausas activas", "SST", "2024-11-30", "Pendiente")]
            for a in acciones:
                cursor.execute("INSERT INTO acciones (empresa_id, descripcion, responsable, fecha, estado) VALUES (1,?,?,?,?)", a)
            # Trabajadores
            trabajadores = [("Carlos Lopez", "12345678", "Operario"), ("Maria Gomez", "87654321", "Supervisor")]
            for t in trabajadores:
                cursor.execute("INSERT INTO trabajadores (empresa_id, nombre, cedula, cargo) VALUES (1,?,?,?)", t)
            # Incidentes
            incidentes = [("Caida desde altura", "2024-10-15", "Grave"), ("Corte con herramienta", "2024-10-20", "Leve")]
            for i in incidentes:
                cursor.execute("INSERT INTO incidentes (empresa_id, descripcion, fecha, gravedad) VALUES (1,?,?,?)", i)
            conn.commit()
            st.success("Datos de prueba cargados!")
            st.balloons()
        else:
            st.info("Ya hay datos en el sistema")

# ========== EXPORTAR ==========
def exportar_excel(df, nombre):
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, sheet_name=nombre, index=False)
    return output.getvalue()

# ========== SESION ==========
if "auth" not in st.session_state:
    st.session_state.auth = False
if "user" not in st.session_state:
    st.session_state.user = None

# ========== LOGIN ==========
if not st.session_state.auth:
    col1, col2, col3 = st.columns([1, 1.2, 1])
    with col2:
        st.markdown('<div style="background: rgba(20,20,40,0.75); backdrop-filter: blur(14px); border-radius: 28px; padding: 35px; text-align:center"><img src="https://cdn-icons-png.flaticon.com/512/2917/2917995.png" width="65"><h1 style="color:white; font-size:24px">SG-SST PHVA</h1><p style="color:rgba(255,255,255,0.6)">Seguridad y Salud, compromiso de todos</p></div>', unsafe_allow_html=True)
        with st.form("login_form"):
            username = st.text_input("Usuario", placeholder="usuario")
            password = st.text_input("Contraseña", type="password", placeholder="contraseña")
            if st.form_submit_button("INGRESAR", use_container_width=True):
                user = verificar_login(username, password)
                if user:
                    st.session_state.auth = True
                    st.session_state.user = user
                    st.rerun()
                else:
                    st.error("Usuario o contraseña incorrectos. Use admin/admin123")
        st.markdown('<div style="text-align:center; font-size:10px; color:gray">SG-SST PHVA | JAN BENITEZ</div>', unsafe_allow_html=True)
    st.stop()

# ========== SIDEBAR ==========
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/2917/2917995.png", width=45)
    st.markdown(f"**{st.session_state.user['nombre']}**")
    st.markdown("---")
    menu = st.radio("MODULOS", ["Dashboard", "Peligros", "Plan de Accion", "Trabajadores", "Incidentes", "Matriz Legal", "Auditorias", "Plan Anual", "Chat IA"])
    if st.button("Cerrar Sesion", use_container_width=True):
        st.session_state.auth = False
        st.rerun()

# ========== DASHBOARD ==========
if menu == "Dashboard":
    st.title("Dashboard")
    col1, col2, col3, col4 = st.columns(4)
    with col1: st.metric("Peligros", pd.read_sql_query("SELECT COUNT(*) FROM peligros", conn).iloc[0,0])
    with col2: st.metric("Acciones", pd.read_sql_query("SELECT COUNT(*) FROM acciones", conn).iloc[0,0])
    with col3: st.metric("Trabajadores", pd.read_sql_query("SELECT COUNT(*) FROM trabajadores", conn).iloc[0,0])
    with col4: st.metric("Incidentes", pd.read_sql_query("SELECT COUNT(*) FROM incidentes", conn).iloc[0,0])
    st.markdown("---")
    if st.button("Cargar Datos de Prueba", use_container_width=True):
        cargar_datos_prueba()
        st.rerun()

# ========== PELIGROS ==========
elif menu == "Peligros":
    st.header("Peligros")
    df = pd.read_sql_query("SELECT * FROM peligros", conn)
    st.dataframe(df, use_container_width=True)
    excel_data = exportar_excel(df, "peligros")
    st.download_button("Exportar a Excel", data=excel_data, file_name=f"peligros_{datetime.now().strftime('%Y%m%d')}.xlsx")

# ========== PLAN DE ACCION ==========
elif menu == "Plan de Accion":
    st.header("Plan de Accion")
    df = pd.read_sql_query("SELECT * FROM acciones", conn)
    st.dataframe(df, use_container_width=True)
    excel_data = exportar_excel(df, "acciones")
    st.download_button("Exportar a Excel", data=excel_data, file_name=f"acciones_{datetime.now().strftime('%Y%m%d')}.xlsx")

# ========== TRABAJADORES ==========
elif menu == "Trabajadores":
    st.header("Trabajadores")
    df = pd.read_sql_query("SELECT * FROM trabajadores", conn)
    st.dataframe(df, use_container_width=True)
    excel_data = exportar_excel(df, "trabajadores")
    st.download_button("Exportar a Excel", data=excel_data, file_name=f"trabajadores_{datetime.now().strftime('%Y%m%d')}.xlsx")

# ========== INCIDENTES ==========
elif menu == "Incidentes":
    st.header("Incidentes")
    df = pd.read_sql_query("SELECT * FROM incidentes ORDER BY fecha DESC", conn)
    st.dataframe(df, use_container_width=True)
    excel_data = exportar_excel(df, "incidentes")
    st.download_button("Exportar a Excel", data=excel_data, file_name=f"incidentes_{datetime.now().strftime('%Y%m%d')}.xlsx")

# ========== MATRIZ LEGAL ==========
elif menu == "Matriz Legal":
    st.header("Matriz Legal")
    df = pd.read_sql_query("SELECT * FROM matriz_legal", conn)
    st.dataframe(df, use_container_width=True)

# ========== AUDITORIAS ==========
elif menu == "Auditorias":
    st.header("Auditorias")
    df = pd.read_sql_query("SELECT * FROM auditorias", conn)
    st.dataframe(df, use_container_width=True)

# ========== PLAN ANUAL ==========
elif menu == "Plan Anual":
    st.header("Plan Anual")
    df = pd.read_sql_query("SELECT * FROM plan_anual", conn)
    st.dataframe(df, use_container_width=True)

# ========== CHAT IA ==========
elif menu == "Chat IA":
    st.title("Chat IA")
    if "messages" not in st.session_state:
        st.session_state.messages = []
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.write(msg["content"])
    if prompt := st.chat_input("Pregunta sobre SST..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.write(prompt)
        with st.chat_message("assistant"):
            with st.spinner("Pensando..."):
                respuesta = call_best_ia(prompt)
                st.write(respuesta)
                st.session_state.messages.append({"role": "assistant", "content": respuesta})

st.markdown("---")
st.markdown("<p style='text-align:center; font-size:11px; color:gray'>SG-SST PHVA | Desarrollado por JAN BENITEZ</p>", unsafe_allow_html=True)
