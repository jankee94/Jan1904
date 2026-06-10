import streamlit as st
import sqlite3
import pandas as pd
import requests
import itertools
from datetime import datetime
import plotly.express as px
import plotly.graph_objects as go
import io
import base64
import tempfile

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

# ========== IA CON MULTIPLES KEYS ==========
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
            elif r.status_code == 429:
                continue
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
    return "⚠️ No se pudo obtener respuesta de ninguna IA. Verifica las API keys."

# ========== BASE DE DATOS ==========
conn = sqlite3.connect("sst.db", check_same_thread=False)
cursor = conn.cursor()

cursor.execute('''CREATE TABLE IF NOT EXISTS usuarios (
    id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT UNIQUE, password TEXT, nombre TEXT, rol TEXT DEFAULT 'trabajador'
)''')
cursor.execute('''CREATE TABLE IF NOT EXISTS empresa (
    id INTEGER PRIMARY KEY AUTOINCREMENT, nit TEXT, nombre TEXT, trabajadores INTEGER, arl TEXT, diagnostico TEXT, fecha TEXT
)''')
cursor.execute('''CREATE TABLE IF NOT EXISTS peligros (
    id INTEGER PRIMARY KEY AUTOINCREMENT, empresa_id INTEGER, tipo TEXT, descripcion TEXT, probabilidad INTEGER, severidad INTEGER, nivel TEXT
)''')
cursor.execute('''CREATE TABLE IF NOT EXISTS acciones (
    id INTEGER PRIMARY KEY AUTOINCREMENT, empresa_id INTEGER, descripcion TEXT, responsable TEXT, fecha TEXT, estado TEXT
)''')
cursor.execute('''CREATE TABLE IF NOT EXISTS trabajadores (
    id INTEGER PRIMARY KEY AUTOINCREMENT, empresa_id INTEGER, nombre TEXT, cedula TEXT, cargo TEXT
)''')
cursor.execute('''CREATE TABLE IF NOT EXISTS incidentes (
    id INTEGER PRIMARY KEY AUTOINCREMENT, empresa_id INTEGER, descripcion TEXT, fecha TEXT, gravedad TEXT
)''')
cursor.execute('''CREATE TABLE IF NOT EXISTS empresa_config (
    id INTEGER PRIMARY KEY AUTOINCREMENT, nombre TEXT, nit TEXT, ubicacion TEXT, ciudad TEXT, sector TEXT, telefono TEXT, email TEXT
)''')
cursor.execute('''CREATE TABLE IF NOT EXISTS matriz_legal (
    id INTEGER PRIMARY KEY AUTOINCREMENT, empresa_id INTEGER DEFAULT 1, norma TEXT, articulo TEXT, requisito TEXT, cumple INTEGER DEFAULT 0, evidencia TEXT, responsable TEXT, fecha_cierre DATE
)''')
cursor.execute('''CREATE TABLE IF NOT EXISTS auditorias (
    id INTEGER PRIMARY KEY AUTOINCREMENT, empresa_id INTEGER DEFAULT 1, codigo TEXT, fecha DATE, tipo TEXT, auditor_id TEXT, hallazgos TEXT, puntuacion INTEGER DEFAULT 0, estado TEXT DEFAULT 'planificada'
)''')
cursor.execute('''CREATE TABLE IF NOT EXISTS checklist_iso (
    id INTEGER PRIMARY KEY AUTOINCREMENT, pregunta TEXT, seccion TEXT, peso INTEGER DEFAULT 4
)''')
cursor.execute('''CREATE TABLE IF NOT EXISTS hallazgos (
    id INTEGER PRIMARY KEY AUTOINCREMENT, auditoria_id INTEGER, checklist_id INTEGER, tipo TEXT, comentario TEXT, evidencia TEXT
)''')
cursor.execute('''CREATE TABLE IF NOT EXISTS plan_anual (
    id INTEGER PRIMARY KEY AUTOINCREMENT, empresa_id INTEGER DEFAULT 1, anio INTEGER, actividad TEXT, mes_programado INTEGER, responsable TEXT, presupuesto REAL DEFAULT 0, estado TEXT DEFAULT 'pendiente', cumplimiento INTEGER DEFAULT 0, evidencia TEXT
)''')

cursor.execute("SELECT * FROM usuarios WHERE username='admin'")
if not cursor.fetchone():
    cursor.execute("INSERT INTO usuarios (username, password, nombre, rol) VALUES (?,?,?,?)",
                  ('admin', 'admin123', 'Administrador', 'admin'))
    conn.commit()

cursor.execute("SELECT COUNT(*) FROM empresa_config")
if cursor.fetchone()[0] == 0:
    cursor.execute("INSERT INTO empresa_config (nombre, nit, ubicacion, ciudad, sector, telefono, email) VALUES (?,?,?,?,?,?,?)",
                  ('Mi Empresa SAS', '900.000.000-1', 'Calle 123 #45-67', 'Bogota', 'Servicios', '6011234567', 'contacto@miempresa.com'))
    conn.commit()

cursor.execute("SELECT COUNT(*) FROM checklist_iso")
if cursor.fetchone()[0] == 0:
    preguntas = [
        ("Existe una politica de SST documentada?", "4.2 Politica", 5),
        ("Se han identificado peligros y evaluado riesgos?", "6.1.2", 5),
        ("Existen objetivos de SST medibles?", "6.2.1", 4),
        ("Se ha implementado un plan de emergencias?", "8.2", 5),
        ("Se realizan auditorias internas?", "9.2", 5),
        ("Se investigan incidentes?", "10.2", 5),
        ("Existe COPASST?", "Decreto 1072", 5),
        ("Se realizan examenes medicos?", "Decreto 1072", 4)
    ]
    for p, s, pe in preguntas:
        cursor.execute("INSERT INTO checklist_iso (pregunta, seccion, peso) VALUES (?,?,?)", (p, s, pe))
    conn.commit()

conn.commit()

def verificar_login(username, password):
    cursor.execute("SELECT * FROM usuarios WHERE username=? AND password=?", (username, password))
    user = cursor.fetchone()
    if user:
        return {"id": user[0], "username": user[1], "nombre": user[3], "rol": user[4]}
    return None

def init_empresa_data():
    pass

def get_empresa_data():
    cursor.execute("SELECT nombre, nit, ubicacion, ciudad, sector, telefono, email FROM empresa_config LIMIT 1")
    data = cursor.fetchone()
    if data:
        return {'nombre': data[0], 'nit': data[1], 'ubicacion': data[2], 'ciudad': data[3], 'sector': data[4], 'telefono': data[5], 'email': data[6]}
    return {}

def crear_tablas_nuevas():
    pass

def pagina_matriz_legal():
    st.header("Matriz Legal")
    df = pd.read_sql_query("SELECT * FROM matriz_legal", conn)
    st.dataframe(df, use_container_width=True)

def pagina_auditorias():
    st.header("Auditorias")
    df = pd.read_sql_query("SELECT * FROM auditorias", conn)
    st.dataframe(df, use_container_width=True)

def pagina_plan_anual():
    st.header("Plan Anual")
    df = pd.read_sql_query("SELECT * FROM plan_anual", conn)
    st.dataframe(df, use_container_width=True)

def pagina_configuracion_empresa():
    st.header("Configuracion Empresa")
    datos = get_empresa_data()
    with st.form("empresa_form"):
        nombre = st.text_input("Nombre", value=datos.get('nombre', ''))
        nit = st.text_input("NIT", value=datos.get('nit', ''))
        ubicacion = st.text_input("Ubicacion", value=datos.get('ubicacion', ''))
        ciudad = st.text_input("Ciudad", value=datos.get('ciudad', ''))
        sector = st.text_input("Sector", value=datos.get('sector', ''))
        telefono = st.text_input("Telefono", value=datos.get('telefono', ''))
        email = st.text_input("Email", value=datos.get('email', ''))
        if st.form_submit_button("Guardar"):
            cursor.execute("UPDATE empresa_config SET nombre=?, nit=?, ubicacion=?, ciudad=?, sector=?, telefono=?, email=?", 
                          (nombre, nit, ubicacion, ciudad, sector, telefono, email))
            conn.commit()
            st.success("Guardado")

def pagina_diagnostico_rapido():
    st.header("Diagnostico Rapido")
    empresa = get_empresa_data()
    st.info(f"Empresa: {empresa.get('nombre', 'No registrada')}")
    if st.button("Generar Diagnostico"):
        with st.spinner("IA generando..."):
            prompt = f"Genera diagnostico SST para empresa {empresa.get('nombre', 'Desconocida')}"
            respuesta = call_best_ia(prompt)
            st.markdown(respuesta)

def pagina_informes():
    st.header("Informes")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Exportar a Excel"):
            st.info("Funcionalidad en desarrollo")
    with col2:
        if st.button("Exportar a PDF"):
            st.info("Funcionalidad en desarrollo")

# ========== SESION ==========
if "auth" not in st.session_state:
    st.session_state.auth = False
if "user" not in st.session_state:
    st.session_state.user = None

# ========== LOGIN ==========
if not st.session_state.auth:
    col1, col2, col3 = st.columns([1, 1.2, 1])
    with col2:
        st.markdown('''
        <div style="background: rgba(20,20,40,0.75); backdrop-filter: blur(14px); border-radius: 28px; padding: 35px; text-align:center">
            <img src="https://cdn-icons-png.flaticon.com/512/2917/2917995.png" width="65">
            <h1 style="color:white; font-size:24px; margin:10px 0">SG-SST PHVA</h1>
            <p style="color:rgba(255,255,255,0.6); font-size:12px">Seguridad y Salud, compromiso de todos</p>
        </div>
        ''', unsafe_allow_html=True)
        
        with st.form("login_form"):
            username = st.text_input("Usuario", placeholder="Ingrese su usuario")
            password = st.text_input("Contraseña", type="password", placeholder="Ingrese su contraseña")
            if st.form_submit_button("INGRESAR", use_container_width=True):
                user = verificar_login(username, password)
                if user:
                    st.session_state.auth = True
                    st.session_state.user = user
                    st.rerun()
                else:
                    st.error("Usuario o contraseña incorrectos")
        
        st.markdown('<div style="margin-top:20px; font-size:10px; color:rgba(255,255,255,0.3)">SG-SST PHVA | Desarrollado por JAN BENITEZ</div></div>', unsafe_allow_html=True)
    st.stop()

# ========== SIDEBAR ==========
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/2917/2917995.png", width=45)
    st.markdown(f"**{st.session_state.user['nombre']}**")
    st.markdown(f"Rol: {st.session_state.user['rol'].upper()}")
    st.markdown("---")
    
    menu = st.radio(
        "MODULOS",
        ["Dashboard", "Diagnostico Rapido", "Configuracion Empresa", "Informes", "Peligros", "Plan de Accion", "Trabajadores", "Incidentes", "Matriz Legal", "Auditorias", "Plan Anual", "Chat IA"],
        label_visibility="collapsed"
    )
    
    st.markdown("---")
    if st.button("Cerrar Sesion", use_container_width=True):
        st.session_state.auth = False
        st.rerun()

# ========== NAVEGACION ==========
if menu == "Dashboard":
    st.title("Dashboard")
    df_p = pd.read_sql_query("SELECT * FROM peligros", conn)
    df_a = pd.read_sql_query("SELECT * FROM acciones", conn)
    df_t = pd.read_sql_query("SELECT * FROM trabajadores", conn)
    col1, col2, col3, col4 = st.columns(4)
    with col1: st.metric("Peligros", len(df_p))
    with col2: st.metric("Acciones", len(df_a))
    with col3: st.metric("Trabajadores", len(df_t))
    with col4: st.metric("Progreso", "60%")

elif menu == "Diagnostico Rapido":
    pagina_diagnostico_rapido()

elif menu == "Configuracion Empresa":
    pagina_configuracion_empresa()

elif menu == "Informes":
    pagina_informes()

elif menu == "Peligros":
    st.title("Peligros")
    with st.form("add_peligro"):
        tipo = st.selectbox("Tipo", ["Fisico", "Quimico", "Biologico", "Ergonomico", "Psicosocial", "Seguridad"])
        desc = st.text_area("Descripcion")
        prob = st.slider("Probabilidad", 1, 4, 2)
        sev = st.slider("Severidad", 1, 3, 2)
        if st.form_submit_button("Guardar"):
            if desc:
                cursor.execute("INSERT INTO peligros (empresa_id, tipo, descripcion, probabilidad, severidad) VALUES (1,?,?,?,?)", (tipo, desc, prob, sev))
                conn.commit()
                st.rerun()
    df = pd.read_sql_query("SELECT * FROM peligros", conn)
    st.dataframe(df, use_container_width=True)

elif menu == "Plan de Accion":
    st.title("Plan de Accion")
    with st.form("add_accion"):
        desc = st.text_area("Descripcion")
        resp = st.text_input("Responsable")
        if st.form_submit_button("Guardar"):
            if desc and resp:
                cursor.execute("INSERT INTO acciones (empresa_id, descripcion, responsable, fecha, estado) VALUES (1,?,?,?,?)", (desc, resp, datetime.now().strftime("%Y-%m-%d"), "Pendiente"))
                conn.commit()
                st.rerun()
    df = pd.read_sql_query("SELECT * FROM acciones", conn)
    st.dataframe(df, use_container_width=True)

elif menu == "Trabajadores":
    st.title("Trabajadores")
    with st.form("add_trabajador"):
        nombre = st.text_input("Nombre")
        cedula = st.text_input("Cedula")
        cargo = st.text_input("Cargo")
        if st.form_submit_button("Registrar"):
            if nombre:
                cursor.execute("INSERT INTO trabajadores (empresa_id, nombre, cedula, cargo) VALUES (1,?,?,?)", (nombre, cedula, cargo))
                conn.commit()
                st.rerun()
    df = pd.read_sql_query("SELECT * FROM trabajadores", conn)
    st.dataframe(df, use_container_width=True)

elif menu == "Incidentes":
    st.title("Incidentes")
    with st.form("add_incidente"):
        desc = st.text_area("Descripcion")
        fecha = st.date_input("Fecha", datetime.now())
        gravedad = st.selectbox("Gravedad", ["Leve", "Moderada", "Grave"])
        if st.form_submit_button("Reportar"):
            if desc:
                cursor.execute("INSERT INTO incidentes (empresa_id, descripcion, fecha, gravedad) VALUES (1,?,?,?)", (desc, fecha.strftime("%Y-%m-%d"), gravedad))
                conn.commit()
                st.rerun()
    df = pd.read_sql_query("SELECT * FROM incidentes ORDER BY fecha DESC", conn)
    st.dataframe(df, use_container_width=True)

elif menu == "Matriz Legal":
    crear_tablas_nuevas()
    pagina_matriz_legal()

elif menu == "Auditorias":
    crear_tablas_nuevas()
    pagina_auditorias()

elif menu == "Plan Anual":
    crear_tablas_nuevas()
    pagina_plan_anual()

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