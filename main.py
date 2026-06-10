import streamlit as st
import sqlite3
import pandas as pd
import requests
import itertools
from datetime import datetime
import io
import plotly.express as px
import plotly.graph_objects as go

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
    .report-card {
        background: rgba(255,255,255,0.1);
        border-radius: 15px;
        padding: 15px;
        margin: 10px 0;
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
    return "⚠️ IA no disponible en este momento"

# ========== BASE DE DATOS ==========
conn = sqlite3.connect("sst.db", check_same_thread=False)
cursor = conn.cursor()

# Crear todas las tablas
cursor.execute('''CREATE TABLE IF NOT EXISTS usuarios (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE,
    password TEXT,
    nombre TEXT,
    rol TEXT
)''')

cursor.execute('''CREATE TABLE IF NOT EXISTS empresa_config (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre TEXT,
    nit TEXT,
    ubicacion TEXT,
    ciudad TEXT,
    sector TEXT,
    telefono TEXT,
    email TEXT
)''')

cursor.execute('''CREATE TABLE IF NOT EXISTS peligros (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    empresa_id INTEGER DEFAULT 1,
    tipo TEXT,
    descripcion TEXT,
    probabilidad INTEGER,
    severidad INTEGER,
    nivel TEXT,
    fecha_registro TEXT
)''')

cursor.execute('''CREATE TABLE IF NOT EXISTS acciones (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    empresa_id INTEGER DEFAULT 1,
    descripcion TEXT,
    responsable TEXT,
    fecha_limite TEXT,
    estado TEXT,
    fecha_registro TEXT
)''')

cursor.execute('''CREATE TABLE IF NOT EXISTS trabajadores (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    empresa_id INTEGER DEFAULT 1,
    nombre TEXT,
    cedula TEXT,
    cargo TEXT,
    area TEXT,
    fecha_registro TEXT
)''')

cursor.execute('''CREATE TABLE IF NOT EXISTS incidentes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    empresa_id INTEGER DEFAULT 1,
    descripcion TEXT,
    fecha TEXT,
    gravedad TEXT,
    causa TEXT,
    fecha_registro TEXT
)''')

cursor.execute('''CREATE TABLE IF NOT EXISTS matriz_legal (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    empresa_id INTEGER DEFAULT 1,
    norma TEXT,
    articulo TEXT,
    requisito TEXT,
    cumple INTEGER DEFAULT 0,
    responsable TEXT
)''')

cursor.execute('''CREATE TABLE IF NOT EXISTS auditorias (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    empresa_id INTEGER DEFAULT 1,
    codigo TEXT,
    fecha TEXT,
    auditor_id TEXT,
    puntuacion INTEGER DEFAULT 0,
    estado TEXT
)''')

cursor.execute('''CREATE TABLE IF NOT EXISTS plan_anual (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    empresa_id INTEGER DEFAULT 1,
    anio INTEGER,
    mes INTEGER,
    actividad TEXT,
    responsable TEXT,
    presupuesto REAL,
    cumplimiento INTEGER
)''')

# Usuario admin
cursor.execute("SELECT * FROM usuarios WHERE username='admin'")
if not cursor.fetchone():
    cursor.execute("INSERT INTO usuarios (username, password, nombre, rol) VALUES (?,?,?,?)",
                  ('admin', 'admin123', 'Administrador', 'admin'))

# Datos empresa por defecto
cursor.execute("SELECT COUNT(*) FROM empresa_config")
if cursor.fetchone()[0] == 0:
    cursor.execute("INSERT INTO empresa_config (nombre, nit, ubicacion, ciudad, sector, telefono, email) VALUES (?,?,?,?,?,?,?)",
                  ('Constructora Segura SAS', '901.234.567-8', 'Calle 80 #45-67', 'Bogota', 'Construccion', '6015551234', 'sst@constructora.com'))

conn.commit()

def verificar_login(username, password):
    cursor.execute("SELECT * FROM usuarios WHERE username=? AND password=?", (username, password))
    user = cursor.fetchone()
    if user:
        return {"id": user[0], "username": user[1], "nombre": user[3], "rol": user[4]}
    return None

def get_empresa():
    cursor.execute("SELECT nombre, nit, ubicacion, ciudad, sector, telefono, email FROM empresa_config LIMIT 1")
    data = cursor.fetchone()
    if data:
        return {"nombre": data[0], "nit": data[1], "ubicacion": data[2], "ciudad": data[3], "sector": data[4], "telefono": data[5], "email": data[6]}
    return {}

# ========== FUNCIONES DE DATOS ==========
def get_peligros():
    return pd.read_sql_query("SELECT id, tipo, descripcion, probabilidad, severidad, nivel FROM peligros", conn)

def get_acciones():
    return pd.read_sql_query("SELECT id, descripcion, responsable, fecha_limite, estado FROM acciones", conn)

def get_trabajadores():
    return pd.read_sql_query("SELECT id, nombre, cedula, cargo, area FROM trabajadores", conn)

def get_incidentes():
    return pd.read_sql_query("SELECT id, descripcion, fecha, gravedad, causa FROM incidentes ORDER BY fecha DESC", conn)

def get_matriz_legal():
    return pd.read_sql_query("SELECT id, norma, articulo, requisito, cumple, responsable FROM matriz_legal", conn)

# ========== DATOS DE PRUEBA ==========
def cargar_datos_prueba():
    with st.spinner("Cargando datos de prueba..."):
        # Limpiar datos existentes
        cursor.execute("DELETE FROM peligros")
        cursor.execute("DELETE FROM acciones")
        cursor.execute("DELETE FROM trabajadores")
        cursor.execute("DELETE FROM incidentes")
        
        fecha = datetime.now().strftime("%Y-%m-%d")
        
        # Peligros
        peligros_data = [
            ("Fisico", "Ruido excesivo en zona de maquinaria", 4, 3, "I"),
            ("Ergonomico", "Posturas forzadas en oficinas", 3, 2, "II"),
            ("Quimico", "Exposicion a solventes en taller", 2, 3, "I"),
            ("Psicosocial", "Estrés laboral por altas cargas", 3, 2, "II"),
            ("Seguridad", "Andamios sin proteccion", 4, 3, "I"),
            ("Biologico", "Exposicion a hongos", 2, 2, "II"),
        ]
        for p in peligros_data:
            cursor.execute("INSERT INTO peligros (tipo, descripcion, probabilidad, severidad, nivel) VALUES (?,?,?,?,?)", p)
        
        # Acciones
        acciones_data = [
            ("Implementar barreras acusticas", "Coordinador SST", "2025-01-15", "En progreso"),
            ("Capacitacion en pausas activas", "SST", "2024-12-10", "Pendiente"),
            ("Instalar extractores de aire", "Mantenimiento", "2024-12-20", "Pendiente"),
            ("Instalar barandas", "Seguridad", "2024-11-30", "Completada"),
        ]
        for a in acciones_data:
            cursor.execute("INSERT INTO acciones (descripcion, responsable, fecha_limite, estado) VALUES (?,?,?,?)", a)
        
        # Trabajadores
        trabajadores_data = [
            ("Carlos Lopez", "12345678", "Operario", "Produccion"),
            ("Maria Gomez", "87654321", "Supervisor", "Produccion"),
            ("Juan Perez", "11122233", "Coordinador SST", "SST"),
            ("Ana Rodriguez", "44455566", "Auxiliar", "Administracion"),
        ]
        for t in trabajadores_data:
            cursor.execute("INSERT INTO trabajadores (nombre, cedula, cargo, area) VALUES (?,?,?,?)", t)
        
        # Incidentes
        incidentes_data = [
            ("Caida desde andamio", "2024-10-15", "Grave", "Falta de barandas"),
            ("Corte con herramienta", "2024-10-20", "Leve", "Falta de entrenamiento"),
            ("Exposicion a quimicos", "2024-11-01", "Moderada", "Falta de EPP"),
        ]
        for i in incidentes_data:
            cursor.execute("INSERT INTO incidentes (descripcion, fecha, gravedad, causa) VALUES (?,?,?,?)", i)
        
        conn.commit()
        st.success("✅ Datos de prueba cargados exitosamente!")
        st.balloons()
        st.rerun()

# ========== EXPORTAR ==========
def exportar_excel(df, nombre):
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, sheet_name=nombre, index=False)
    return output.getvalue()

# ========== VISTA PREVIA INFORME ==========
def mostrar_informe():
    st.title("📊 INFORME SST - VISTA PREVIA")
    
    empresa = get_empresa()
    peligros_df = get_peligros()
    acciones_df = get_acciones()
    trabajadores_df = get_trabajadores()
    incidentes_df = get_incidentes()
    
    st.markdown(f'''
    <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 20px; border-radius: 15px; margin-bottom: 20px;">
        <h2 style="color: white; margin: 0;">INFORME SG-SST PHVA</h2>
        <p style="color: rgba(255,255,255,0.8);">Empresa: {empresa.get('nombre', 'No registrada')}</p>
        <p style="color: rgba(255,255,255,0.6); font-size: 12px;">Fecha: {datetime.now().strftime('%d/%m/%Y %H:%M')}</p>
    </div>
    ''', unsafe_allow_html=True)
    
    # KPIs
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("⚠️ Peligros", len(peligros_df))
    with col2:
        completadas = len(acciones_df[acciones_df['estado'] == 'Completada']) if not acciones_df.empty else 0
        st.metric("✅ Acciones", f"{completadas}/{len(acciones_df)}")
    with col3:
        st.metric("👥 Trabajadores", len(trabajadores_df))
    with col4:
        st.metric("📝 Incidentes", len(incidentes_df))
    
    # Gráficos
    col1, col2 = st.columns(2)
    with col1:
        if not peligros_df.empty:
            st.subheader("Peligros por Nivel")
            niveles = peligros_df['nivel'].value_counts()
            fig = go.Figure(data=[go.Bar(x=niveles.index, y=niveles.values, marker_color=['#dc2626', '#f59e0b', '#10b981'])])
            fig.update_layout(height=300)
            st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        if not incidentes_df.empty:
            st.subheader("Incidentes por Gravedad")
            gravedades = incidentes_df['gravedad'].value_counts()
            fig = go.Figure(data=[go.Pie(labels=gravedades.index, values=gravedades.values)])
            fig.update_layout(height=300)
            st.plotly_chart(fig, use_container_width=True)
    
    # Tablas
    st.subheader("📋 Datos del Sistema")
    tab1, tab2, tab3, tab4 = st.tabs(["Peligros", "Acciones", "Trabajadores", "Incidentes"])
    with tab1:
        st.dataframe(peligros_df, use_container_width=True)
    with tab2:
        st.dataframe(acciones_df, use_container_width=True)
    with tab3:
        st.dataframe(trabajadores_df, use_container_width=True)
    with tab4:
        st.dataframe(incidentes_df, use_container_width=True)
    
    # Botón descargar
    st.markdown("---")
    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        excel_data = exportar_excel(peligros_df, "peligros")
        st.download_button("📥 DESCARGAR INFORME COMPLETO (EXCEL)", data=excel_data, file_name=f"informe_sst_{datetime.now().strftime('%Y%m%d')}.xlsx", use_container_width=True)

# ========== LOGIN ==========
if "auth" not in st.session_state:
    st.session_state.auth = False
if "user" not in st.session_state:
    st.session_state.user = None

if not st.session_state.auth:
    col1, col2, col3 = st.columns([1, 1.3, 1])
    with col2:
        st.markdown('''
        <div style="background: rgba(20,20,40,0.75); backdrop-filter: blur(14px); border-radius: 28px; padding: 40px; text-align:center">
            <img src="https://cdn-icons-png.flaticon.com/512/2917/2917995.png" width="70">
            <h1 style="color:white;">SG-SST PHVA</h1>
            <p style="color:rgba(255,255,255,0.6)">Seguridad y Salud, compromiso de todos</p>
        </div>
        ''', unsafe_allow_html=True)
        
        with st.form("login_form"):
            username = st.text_input("Usuario")
            password = st.text_input("Contraseña", type="password")
            if st.form_submit_button("INGRESAR", use_container_width=True):
                user = verificar_login(username, password)
                if user:
                    st.session_state.auth = True
                    st.session_state.user = user
                    st.rerun()
                else:
                    st.error("Usuario o contraseña incorrectos. Use: admin / admin123")
        
        st.markdown('<p style="text-align:center; font-size:11px; color:gray">SG-SST PHVA | Desarrollado por JAN BENITEZ</p>', unsafe_allow_html=True)
    st.stop()

# ========== SIDEBAR ==========
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/2917/2917995.png", width=50)
    st.markdown(f"### {st.session_state.user['nombre']}")
    st.caption(f"Rol: {st.session_state.user['rol'].upper()}")
    st.markdown("---")
    
    menu = st.radio("MENU", [
        "Dashboard",
        "Peligros",
        "Plan de Accion",
        "Trabajadores",
        "Incidentes",
        "Matriz Legal",
        "Informes",
        "Chat IA"
    ])
    
    st.markdown("---")
    if st.button("Cerrar Sesion", use_container_width=True):
        st.session_state.auth = False
        st.rerun()

# ========== PAGINAS ==========
if menu == "Dashboard":
    st.title("Dashboard SST")
    
    col1, col2 = st.columns([2,1])
    with col1:
        st.info(f"🏢 Empresa: {get_empresa().get('nombre', 'No registrada')}")
    with col2:
        if st.button("Cargar Datos de Prueba", use_container_width=True):
            cargar_datos_prueba()
    
    col1, col2, col3, col4 = st.columns(4)
    with col1: st.metric("Peligros", len(get_peligros()))
    with col2: st.metric("Acciones", len(get_acciones()))
    with col3: st.metric("Trabajadores", len(get_trabajadores()))
    with col4: st.metric("Incidentes", len(get_incidentes()))

elif menu == "Peligros":
    st.header("Peligros")
    st.dataframe(get_peligros(), use_container_width=True)
    excel_data = exportar_excel(get_peligros(), "peligros")
    st.download_button("Exportar a Excel", data=excel_data, file_name="peligros.xlsx")

elif menu == "Plan de Accion":
    st.header("Plan de Accion")
    st.dataframe(get_acciones(), use_container_width=True)
    excel_data = exportar_excel(get_acciones(), "acciones")
    st.download_button("Exportar a Excel", data=excel_data, file_name="acciones.xlsx")

elif menu == "Trabajadores":
    st.header("Trabajadores")
    st.dataframe(get_trabajadores(), use_container_width=True)
    excel_data = exportar_excel(get_trabajadores(), "trabajadores")
    st.download_button("Exportar a Excel", data=excel_data, file_name="trabajadores.xlsx")

elif menu == "Incidentes":
    st.header("Incidentes")
    st.dataframe(get_incidentes(), use_container_width=True)
    excel_data = exportar_excel(get_incidentes(), "incidentes")
    st.download_button("Exportar a Excel", data=excel_data, file_name="incidentes.xlsx")

elif menu == "Matriz Legal":
    st.header("Matriz Legal")
    st.dataframe(get_matriz_legal(), use_container_width=True)

elif menu == "Informes":
    mostrar_informe()

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
