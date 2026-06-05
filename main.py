import streamlit as st
import sqlite3
import pandas as pd
import requests
from datetime import datetime

st.set_page_config(page_title="SG-SST PHVA", page_icon="🔄", layout="wide")

# CSS para login moderno
st.markdown("""
<style>
    .stApp {
        background: linear-gradient(135deg, #0f0c29 0%, #302b63 50%, #24243e 100%);
    }
    .login-card {
        background: rgba(255,255,255,0.08);
        backdrop-filter: blur(12px);
        border-radius: 30px;
        padding: 40px 30px;
        box-shadow: 0 25px 45px rgba(0,0,0,0.3);
        border: 1px solid rgba(255,255,255,0.1);
    }
    .logo-img {
        width: 80px;
        display: block;
        margin: 0 auto 15px auto;
    }
    .main-title {
        font-size: 32px;
        font-weight: 800;
        background: linear-gradient(135deg, #fff 0%, #a8c0ff 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        margin: 10px 0 5px 0;
    }
    .slogan {
        color: rgba(255,255,255,0.7);
        font-size: 14px;
        font-style: italic;
        text-align: center;
        margin-bottom: 30px;
    }
    .stTextInput > div > div > input {
        background: rgba(255,255,255,0.1) !important;
        border: 1px solid rgba(255,255,255,0.2) !important;
        border-radius: 12px !important;
        color: white !important;
        padding: 12px 15px !important;
    }
    .stButton > button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
        border: none !important;
        border-radius: 12px !important;
        padding: 12px !important;
        font-weight: bold !important;
        font-size: 16px !important;
        width: 100% !important;
    }
    .developer-footer {
        position: fixed;
        bottom: 0;
        left: 0;
        right: 0;
        text-align: center;
        padding: 10px;
        background: rgba(0,0,0,0.6);
        color: rgba(255,255,255,0.6);
        font-size: 12px;
        z-index: 999;
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

# Usuario admin por defecto
cursor.execute("SELECT * FROM usuarios WHERE username = 'admin'")
if not cursor.fetchone():
    cursor.execute("INSERT INTO usuarios (username, password, nombre, rol) VALUES (?, ?, ?, ?)",
                  ('admin', 'admin123', 'Administrador', 'admin'))
    conn.commit()

conn.commit()

def verificar_login(username, password):
    cursor.execute("SELECT * FROM usuarios WHERE username = ? AND password = ? AND activo = 1", (username, password))
    user = cursor.fetchone()
    if user:
        return {"id": user[0], "username": user[1], "nombre": user[3], "rol": user[4]}
    return None

def guardar_diagnostico(nit, nombre, trabajadores, arl, diagnostico):
    fecha = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cursor.execute("INSERT INTO empresa (nit, nombre, trabajadores, arl, diagnostico, fecha) VALUES (?, ?, ?, ?, ?, ?)",
                  (nit, nombre, trabajadores, arl, diagnostico, fecha))
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
    api_key = "AIzaSyD3QhEohGJeYhVtM7JmBZ2nXvZJFxJZv3U"
    try:
        url = "https://generativelanguage.googleapis.com/v1/models/gemini-pro:generateContent"
        headers = {"Content-Type": "application/json", "x-goog-api-key": api_key}
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
if "empresa_actual_id" not in st.session_state:
    st.session_state.empresa_actual_id = None
if "empresa_actual" not in st.session_state:
    st.session_state.empresa_actual = None

# ========== LOGIN ==========
if not st.session_state.auth:
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown('<div class="login-card">', unsafe_allow_html=True)
        st.image("https://cdn-icons-png.flaticon.com/512/2917/2917995.png", width=80)
        st.markdown('<h1 class="main-title">SG-SST PHVA</h1>', unsafe_allow_html=True)
        st.markdown('<div class="slogan">"Seguridad y Salud, compromiso de todos"</div>', unsafe_allow_html=True)
        
        with st.form("login_form"):
            username = st.text_input("USUARIO", placeholder="Ingrese su usuario")
            password = st.text_input("CONTRASEÑA", type="password", placeholder="Ingrese su contraseña")
            
            submitted = st.form_submit_button("INGRESAR", use_container_width=True)
            
            if submitted:
                user = verificar_login(username, password)
                if user:
                    st.session_state.auth = True
                    st.session_state.user = user
                    st.rerun()
                else:
                    st.error("❌ Usuario o contraseña incorrectos")
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown('<div class="developer-footer">🔄 SG-SST PHVA | DESARROLLADO POR JAN BENITEZ</div>', unsafe_allow_html=True)
    st.stop()

# ========== SIDEBAR ==========
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/2917/2917995.png", width=50)
    st.markdown(f"**👤 {st.session_state.user['nombre']}**")
    st.markdown(f"**Rol:** {st.session_state.user['rol'].upper()}")
    st.markdown("---")
    
    if st.session_state.user['rol'] == 'admin':
        diagnosticos = obtener_diagnosticos()
        if not diagnosticos.empty:
            empresas_opciones = diagnosticos.apply(lambda x: f"{x['id']} - {x['nombre']}", axis=1).tolist()
            empresa_seleccionada = st.selectbox("🏢 Empresa", ["-- Nueva --"] + empresas_opciones)
            if empresa_seleccionada != "-- Nueva --":
                id_empresa = int(empresa_seleccionada.split(" - ")[0])
                if st.session_state.empresa_actual_id != id_empresa:
                    set_empresa_actual(id_empresa)
                    st.rerun()
    
    if st.session_state.empresa_actual:
        st.success(f"🏢 {st.session_state.empresa_actual.get('nombre', '')[:20]}")
    
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

# ========== DASHBOARD ==========
if menu == "📊 Dashboard":
    st.title("📊 Dashboard SST")
    if st.session_state.empresa_actual:
        emp = st.session_state.empresa_actual
        st.success(f"🏢 **{emp.get('nombre', '')}** | 👥 {emp.get('trabajadores', 0)} trabajadores")
    else:
        st.warning("⚠️ Seleccione o cree una empresa en 'Diagnóstico IA'")

# ========== DIAGNÓSTICO IA ==========
elif menu == "🤖 Diagnóstico IA":
    st.title("🤖 DIAGNÓSTICO IA")
    
    with st.form("form_diagnostico"):
        nombre = st.text_input("Nombre de la empresa *")
        trabajadores = st.number_input("Número de trabajadores *", min_value=1, value=10)
        arl = st.selectbox("ARL *", ["Positiva", "Sura", "Colpatria"])
        
        if st.form_submit_button("🚀 GENERAR DIAGNÓSTICO", use_container_width=True):
            if nombre:
                with st.spinner("🤖 IA generando diagnóstico..."):
                    respuesta = call_ia(f"Diagnóstico SST para {nombre} con {trabajadores} trabajadores")
                    empresa_id = guardar_diagnostico("", nombre, trabajadores, arl, respuesta)
                    set_empresa_actual(empresa_id)
                    st.success("✅ Diagnóstico generado")
                    st.rerun()
            else:
                st.error("Nombre obligatorio")

# ========== PELIGROS ==========
elif menu == "⚠️ Peligros":
    st.title("⚠️ Peligros")
    if st.session_state.empresa_actual_id:
        df = pd.read_sql_query("SELECT * FROM peligros WHERE empresa_id = ?", conn, params=(st.session_state.empresa_actual_id,))
        st.dataframe(df)
        with st.form("add_peligro"):
            tipo = st.selectbox("Tipo", ["Físico", "Químico", "Biológico", "Ergonómico", "Psicosocial", "Seguridad"])
            desc = st.text_area("Descripción")
            if st.form_submit_button("Guardar"):
                cursor.execute("INSERT INTO peligros (empresa_id, tipo, descripcion) VALUES (?, ?, ?)",
                              (st.session_state.empresa_actual_id, tipo, desc))
                conn.commit()
                st.rerun()

# ========== PLAN DE ACCIÓN ==========
elif menu == "✅ Plan de Acción":
    st.title("✅ Plan de Acción")
    if st.session_state.empresa_actual_id:
        df = pd.read_sql_query("SELECT * FROM acciones WHERE empresa_id = ?", conn, params=(st.session_state.empresa_actual_id,))
        st.dataframe(df)
        with st.form("add_accion"):
            desc = st.text_area("Acción")
            resp = st.text_input("Responsable")
            if st.form_submit_button("Guardar"):
                cursor.execute("INSERT INTO acciones (empresa_id, descripcion, responsable, estado) VALUES (?, ?, ?, ?)",
                              (st.session_state.empresa_actual_id, desc, resp, "Pendiente"))
                conn.commit()
                st.rerun()

# ========== TRABAJADORES ==========
elif menu == "👥 Trabajadores":
    st.title("👥 Trabajadores")
    if st.session_state.empresa_actual_id:
        df = pd.read_sql_query("SELECT * FROM trabajadores WHERE empresa_id = ?", conn, params=(st.session_state.empresa_actual_id,))
        st.dataframe(df)
        with st.form("add_trabajador"):
            nombre = st.text_input("Nombre")
            cedula = st.text_input("Cédula")
            cargo = st.text_input("Cargo")
            if st.form_submit_button("Guardar"):
                cursor.execute("INSERT INTO trabajadores (empresa_id, nombre, cedula, cargo) VALUES (?, ?, ?, ?)",
                              (st.session_state.empresa_actual_id, nombre, cedula, cargo))
                conn.commit()
                st.rerun()

# ========== INCIDENTES ==========
elif menu == "📝 Incidentes":
    st.title("📝 Incidentes")
    if st.session_state.empresa_actual_id:
        with st.form("add_incidente"):
            desc = st.text_area("Descripción")
            gravedad = st.selectbox("Gravedad", ["Leve", "Moderada", "Grave"])
            if st.form_submit_button("Reportar"):
                cursor.execute("INSERT INTO incidentes (empresa_id, descripcion, fecha, gravedad) VALUES (?, ?, ?, ?)",
                              (st.session_state.empresa_actual_id, desc, datetime.now().strftime("%Y-%m-%d"), gravedad))
                conn.commit()
                st.rerun()
        df = pd.read_sql_query("SELECT * FROM incidentes WHERE empresa_id = ?", conn, params=(st.session_state.empresa_actual_id,))
        st.dataframe(df)

# ========== CHAT IA ==========
elif menu == "💬 Chat IA":
    st.title("💬 Chat IA")
    if "msgs" not in st.session_state:
        st.session_state.msgs = []
    for msg in st.session_state.msgs:
        with st.chat_message(msg["role"]):
            st.write(msg["content"])
    if prompt := st.chat_input("Pregunta..."):
        st.session_state.msgs.append({"role": "user", "content": prompt})
        respuesta = call_ia(prompt)
        st.session_state.msgs.append({"role": "assistant", "content": respuesta or "Error"})
        st.rerun()

st.markdown('<div class="developer-footer">🔄 SG-SST PHVA | DESARROLLADO POR JAN BENITEZ</div>', unsafe_allow_html=True)