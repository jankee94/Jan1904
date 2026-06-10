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
    .edit-card {
        background: rgba(255,255,255,0.1);
        border-radius: 15px;
        padding: 20px;
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

# Tablas
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
    tipo TEXT,
    descripcion TEXT,
    probabilidad INTEGER,
    severidad INTEGER,
    nivel TEXT,
    controls TEXT,
    fecha_registro TEXT
)''')

cursor.execute('''CREATE TABLE IF NOT EXISTS acciones (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    descripcion TEXT,
    responsable TEXT,
    fecha_limite TEXT,
    estado TEXT,
    prioridad TEXT,
    evidencia TEXT,
    fecha_registro TEXT
)''')

cursor.execute('''CREATE TABLE IF NOT EXISTS trabajadores (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre TEXT,
    cedula TEXT,
    cargo TEXT,
    area TEXT,
    eps TEXT,
    arl TEXT,
    fecha_ingreso TEXT,
    examenes TEXT,
    fecha_registro TEXT
)''')

cursor.execute('''CREATE TABLE IF NOT EXISTS incidentes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tipo TEXT,
    descripcion TEXT,
    fecha TEXT,
    lugar TEXT,
    gravedad TEXT,
    causa TEXT,
    afectado TEXT,
    acciones_tomadas TEXT,
    fecha_registro TEXT
)''')

cursor.execute('''CREATE TABLE IF NOT EXISTS matriz_legal (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    norma TEXT,
    articulo TEXT,
    requisito TEXT,
    cumple INTEGER,
    responsable TEXT,
    evidencia TEXT,
    fecha_cierre TEXT
)''')

cursor.execute('''CREATE TABLE IF NOT EXISTS auditorias (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    codigo TEXT,
    fecha TEXT,
    auditor TEXT,
    hallazgos TEXT,
    puntuacion INTEGER,
    estado TEXT
)''')

cursor.execute('''CREATE TABLE IF NOT EXISTS plan_anual (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
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

# Datos empresa
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

def update_empresa(data):
    cursor.execute("UPDATE empresa_config SET nombre=?, nit=?, ubicacion=?, ciudad=?, sector=?, telefono=?, email=? WHERE id=1",
                  (data['nombre'], data['nit'], data['ubicacion'], data['ciudad'], data['sector'], data['telefono'], data['email']))
    conn.commit()

# ========== CRUD FUNCTIONS ==========
def create_peligro(tipo, desc, prob, sev, controls):
    nivel = "I" if prob * sev >= 6 else "II" if prob * sev >= 4 else "III"
    cursor.execute("INSERT INTO peligros (tipo, descripcion, probabilidad, severidad, nivel, controls, fecha_registro) VALUES (?,?,?,?,?,?,?)",
                  (tipo, desc, prob, sev, nivel, controls, datetime.now().strftime("%Y-%m-%d")))
    conn.commit()
    return cursor.lastrowid

def update_peligro(id, tipo, desc, prob, sev, controls):
    nivel = "I" if prob * sev >= 6 else "II" if prob * sev >= 4 else "III"
    cursor.execute("UPDATE peligros SET tipo=?, descripcion=?, probabilidad=?, severidad=?, nivel=?, controls=? WHERE id=?", 
                  (tipo, desc, prob, sev, nivel, controls, id))
    conn.commit()

def delete_peligro(id):
    cursor.execute("DELETE FROM peligros WHERE id=?", (id,))
    conn.commit()

def get_peligros():
    return pd.read_sql_query("SELECT * FROM peligros ORDER BY nivel, probabilidad DESC", conn)

# Acciones CRUD
def create_accion(desc, responsable, fecha_limite, prioridad):
    cursor.execute("INSERT INTO acciones (descripcion, responsable, fecha_limite, estado, prioridad, fecha_registro) VALUES (?,?,?,?,?,?)",
                  (desc, responsable, fecha_limite, 'Pendiente', prioridad, datetime.now().strftime("%Y-%m-%d")))
    conn.commit()

def update_accion(id, estado, evidencia):
    cursor.execute("UPDATE acciones SET estado=?, evidencia=? WHERE id=?", (estado, evidencia, id))
    conn.commit()

def delete_accion(id):
    cursor.execute("DELETE FROM acciones WHERE id=?", (id,))
    conn.commit()

def get_acciones():
    return pd.read_sql_query("SELECT * FROM acciones ORDER BY fecha_limite", conn)

# Trabajadores CRUD
def create_trabajador(nombre, cedula, cargo, area, eps, arl, fecha_ingreso):
    cursor.execute("INSERT INTO trabajadores (nombre, cedula, cargo, area, eps, arl, fecha_ingreso, fecha_registro) VALUES (?,?,?,?,?,?,?,?)",
                  (nombre, cedula, cargo, area, eps, arl, fecha_ingreso, datetime.now().strftime("%Y-%m-%d")))
    conn.commit()

def update_trabajador(id, nombre, cedula, cargo, area, eps, arl):
    cursor.execute("UPDATE trabajadores SET nombre=?, cedula=?, cargo=?, area=?, eps=?, arl=? WHERE id=?", 
                  (nombre, cedula, cargo, area, eps, arl, id))
    conn.commit()

def delete_trabajador(id):
    cursor.execute("DELETE FROM trabajadores WHERE id=?", (id,))
    conn.commit()

def get_trabajadores():
    return pd.read_sql_query("SELECT * FROM trabajadores", conn)

# Incidentes CRUD
def create_incidente(tipo, desc, fecha, lugar, gravedad, causa, afectado, acciones):
    cursor.execute("INSERT INTO incidentes (tipo, descripcion, fecha, lugar, gravedad, causa, afectado, acciones_tomadas, fecha_registro) VALUES (?,?,?,?,?,?,?,?,?)",
                  (tipo, desc, fecha, lugar, gravedad, causa, afectado, acciones, datetime.now().strftime("%Y-%m-%d")))
    conn.commit()

def update_incidente(id, acciones_tomadas):
    cursor.execute("UPDATE incidentes SET acciones_tomadas=? WHERE id=?", (acciones_tomadas, id))
    conn.commit()

def delete_incidente(id):
    cursor.execute("DELETE FROM incidentes WHERE id=?", (id,))
    conn.commit()

def get_incidentes():
    return pd.read_sql_query("SELECT * FROM incidentes ORDER BY fecha DESC", conn)

# Matriz Legal CRUD
def update_matriz_legal(id, cumple, evidencia, fecha_cierre):
    cursor.execute("UPDATE matriz_legal SET cumple=?, evidencia=?, fecha_cierre=? WHERE id=?", (cumple, evidencia, fecha_cierre, id))
    conn.commit()

def get_matriz_legal():
    return pd.read_sql_query("SELECT * FROM matriz_legal", conn)

# ========== IMPORTAR EXCEL ==========
def importar_excel_peligros(file):
    try:
        df = pd.read_excel(file)
        for _, row in df.iterrows():
            nivel = "I" if int(row['probabilidad']) * int(row['severidad']) >= 6 else "II" if int(row['probabilidad']) * int(row['severidad']) >= 4 else "III"
            cursor.execute("INSERT INTO peligros (tipo, descripcion, probabilidad, severidad, nivel, controls, fecha_registro) VALUES (?,?,?,?,?,?,?)",
                          (row['tipo'], row['descripcion'], int(row['probabilidad']), int(row['severidad']), nivel, row.get('controls', ''), datetime.now().strftime("%Y-%m-%d")))
        conn.commit()
        return True, f"{len(df)} peligros importados"
    except Exception as e:
        return False, str(e)

def importar_excel_trabajadores(file):
    try:
        df = pd.read_excel(file)
        for _, row in df.iterrows():
            cursor.execute("INSERT INTO trabajadores (nombre, cedula, cargo, area, eps, arl, fecha_ingreso, fecha_registro) VALUES (?,?,?,?,?,?,?,?)",
                          (row['nombre'], row['cedula'], row['cargo'], row.get('area', ''), row.get('eps', ''), row.get('arl', ''), row.get('fecha_ingreso', ''), datetime.now().strftime("%Y-%m-%d")))
        conn.commit()
        return True, f"{len(df)} trabajadores importados"
    except Exception as e:
        return False, str(e)

# ========== EXPORTAR EXCEL ==========
def exportar_excel(df, nombre):
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, sheet_name=nombre, index=False)
    return output.getvalue()

# ========== DATOS DE PRUEBA ==========
def cargar_datos_prueba():
    with st.spinner("Cargando datos de prueba..."):
        cursor.execute("DELETE FROM peligros")
        cursor.execute("DELETE FROM acciones")
        cursor.execute("DELETE FROM trabajadores")
        cursor.execute("DELETE FROM incidentes")
        cursor.execute("DELETE FROM matriz_legal")
        
        fecha = datetime.now().strftime("%Y-%m-%d")
        
        # Peligros
        peligros_data = [
            ("Fisico", "Ruido excesivo en zona de maquinaria", 4, 3, "Instalar barreras acusticas", fecha),
            ("Ergonomico", "Posturas forzadas en oficinas", 3, 2, "Capacitacion pausas activas", fecha),
            ("Quimico", "Exposicion a solventes en taller", 2, 3, "Instalar extractores de aire", fecha),
            ("Psicosocial", "Estrés laboral", 3, 2, "Evaluacion de cargas laborales", fecha),
            ("Seguridad", "Andamios sin proteccion", 4, 3, "Instalar barandas", fecha),
        ]
        for p in peligros_data:
            nivel = "I" if p[2] * p[3] >= 6 else "II" if p[2] * p[3] >= 4 else "III"
            cursor.execute("INSERT INTO peligros (tipo, descripcion, probabilidad, severidad, nivel, controls, fecha_registro) VALUES (?,?,?,?,?,?,?)", (p[0], p[1], p[2], p[3], nivel, p[4], fecha))
        
        # Acciones
        acciones_data = [
            ("Implementar barreras acusticas", "Coordinador SST", "2025-01-15", "En progreso", "Alta"),
            ("Capacitacion en pausas activas", "SST", "2024-12-10", "Pendiente", "Media"),
            ("Instalar extractores de aire", "Mantenimiento", "2024-12-20", "Pendiente", "Alta"),
        ]
        for a in acciones_data:
            cursor.execute("INSERT INTO acciones (descripcion, responsable, fecha_limite, estado, prioridad, fecha_registro) VALUES (?,?,?,?,?,?)", (a[0], a[1], a[2], a[3], a[4], fecha))
        
        # Trabajadores
        trabajadores_data = [
            ("Carlos Lopez", "12345678", "Operario", "Produccion", "Sura", "Positiva", "2024-01-15"),
            ("Maria Gomez", "87654321", "Supervisor", "Produccion", "Sura", "Positiva", "2024-02-20"),
            ("Juan Perez", "11122233", "Coordinador SST", "SST", "Sura", "Positiva", "2024-03-10"),
        ]
        for t in trabajadores_data:
            cursor.execute("INSERT INTO trabajadores (nombre, cedula, cargo, area, eps, arl, fecha_ingreso, fecha_registro) VALUES (?,?,?,?,?,?,?,?)", (t[0], t[1], t[2], t[3], t[4], t[5], t[6], fecha))
        
        # Incidentes
        incidentes_data = [
            ("Accidente", "Caida desde andamio", "2024-10-15", "Zona A", "Grave", "Falta de barandas", "Carlos Lopez", "Instalacion de barandas"),
            ("Incidente", "Corte con herramienta", "2024-10-20", "Taller", "Leve", "Falta de entrenamiento", "Maria Gomez", "Capacitacion en herramientas"),
        ]
        for i in incidentes_data:
            cursor.execute("INSERT INTO incidentes (tipo, descripcion, fecha, lugar, gravedad, causa, afectado, acciones_tomadas, fecha_registro) VALUES (?,?,?,?,?,?,?,?,?)", (i[0], i[1], i[2], i[3], i[4], i[5], i[6], i[7], fecha))
        
        # Matriz Legal (Normativa)
        legal_data = [
            ("ISO 45001", "4.1", "Comprender la organización y su contexto", 0, "Gerente", "", ""),
            ("ISO 45001", "5.2", "Política de SST", 0, "Gerente", "", ""),
            ("ISO 45001", "6.1.2", "Identificación de peligros", 1, "SST", "Matriz actualizada", "2024-11-30"),
            ("ISO 45001", "7.2", "Competencia", 0, "SST", "", ""),
            ("ISO 45001", "8.2", "Preparación y respuesta ante emergencias", 0, "SST", "", ""),
            ("ISO 45001", "9.2", "Auditoría interna", 0, "Auditor", "", ""),
            ("ISO 45001", "10.2", "No conformidad y acción correctiva", 0, "SST", "", ""),
            ("Decreto 1072", "2.2.4.6.22", "Conformar COPASST", 0, "Gerente", "", ""),
            ("Decreto 1072", "2.2.4.6.16", "Exámenes médicos ocupacionales", 1, "SST", "Exámenes realizados", "2024-10-15"),
            ("Decreto 1072", "2.2.4.6.23", "Inspecciones de seguridad", 0, "SST", "", ""),
        ]
        for l in legal_data:
            cursor.execute("INSERT INTO matriz_legal (norma, articulo, requisito, cumple, responsable, evidencia, fecha_cierre) VALUES (?,?,?,?,?,?,?)", l)
        
        conn.commit()
        st.success("✅ Datos de prueba cargados!")
        st.balloons()
        st.rerun()

# ========== VISTA PREVIA INFORME CON NORMATIVA ==========
def mostrar_informe():
    st.title("📊 INFORME SST - VISTA PREVIA")
    
    empresa = get_empresa()
    peligros_df = get_peligros()
    acciones_df = get_acciones()
    trabajadores_df = get_trabajadores()
    incidentes_df = get_incidentes()
    matriz_df = get_matriz_legal()
    
    st.markdown(f'''
    <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 20px; border-radius: 15px; margin-bottom: 20px;">
        <h2 style="color: white; margin: 0;">INFORME SG-SST PHVA</h2>
        <p style="color: rgba(255,255,255,0.8);">Empresa: {empresa.get('nombre', 'No registrada')}</p>
        <p style="color: rgba(255,255,255,0.8);">NIT: {empresa.get('nit', 'N/A')} | Sector: {empresa.get('sector', 'N/A')}</p>
        <p style="color: rgba(255,255,255,0.6); font-size: 12px;">Fecha: {datetime.now().strftime('%d/%m/%Y %H:%M')}</p>
    </div>
    ''', unsafe_allow_html=True)
    
    # KPIs
    col1, col2, col3, col4 = st.columns(4)
    with col1: st.metric("⚠️ Peligros", len(peligros_df))
    with col2: 
        completadas = len(acciones_df[acciones_df['estado'] == 'Completada']) if not acciones_df.empty else 0
        st.metric("✅ Acciones", f"{completadas}/{len(acciones_df)}")
    with col3: st.metric("👥 Trabajadores", len(trabajadores_df))
    with col4: st.metric("📝 Incidentes", len(incidentes_df))
    
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
    tabs = st.tabs(["Peligros", "Acciones", "Trabajadores", "Incidentes", "Matriz Legal"])
    with tabs[0]:
        st.dataframe(peligros_df, use_container_width=True)
    with tabs[1]:
        st.dataframe(acciones_df, use_container_width=True)
    with tabs[2]:
        st.dataframe(trabajadores_df, use_container_width=True)
    with tabs[3]:
        st.dataframe(incidentes_df, use_container_width=True)
    with tabs[4]:
        st.subheader("📋 MATRIZ LEGAL - ISO 45001 + DECRETO 1072")
        st.dataframe(matriz_df, use_container_width=True)
        # Cumplimiento
        if not matriz_df.empty:
            cumplimiento = matriz_df['cumple'].sum()
            total = len(matriz_df)
            st.progress(cumplimiento/total)
            st.metric("Cumplimiento Normativo", f"{(cumplimiento/total)*100:.0f}%")
    
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
        "Empresa",
        "Peligros",
        "Plan de Accion",
        "Trabajadores",
        "Incidentes",
        "Matriz Legal",
        "Auditorias",
        "Informes",
        "Chat IA"
    ])
    
    st.markdown("---")
    if st.button("Cerrar Sesion", use_container_width=True):
        st.session_state.auth = False
        st.rerun()

# ========== DASHBOARD ==========
if menu == "Dashboard":
    st.title("Dashboard SST")
    
    col1, col2 = st.columns([2,1])
    with col1:
        empresa = get_empresa()
        st.info(f"🏢 Empresa: {empresa.get('nombre', 'No registrada')} | {empresa.get('ciudad', '')}")
    with col2:
        if st.button("🚀 Cargar Datos de Prueba", use_container_width=True):
            cargar_datos_prueba()
    
    col1, col2, col3, col4 = st.columns(4)
    with col1: st.metric("⚠️ Peligros", len(get_peligros()))
    with col2: st.metric("✅ Acciones", len(get_acciones()))
    with col3: st.metric("👥 Trabajadores", len(get_trabajadores()))
    with col4: st.metric("📝 Incidentes", len(get_incidentes()))
    
    st.markdown("---")
    st.subheader("📋 Últimos Incidentes")
    incidentes = get_incidentes().head(5)
    if not incidentes.empty:
        st.dataframe(incidentes[['fecha', 'tipo', 'descripcion', 'gravedad']], use_container_width=True)

# ========== EMPRESA ==========
elif menu == "Empresa":
    st.header("🏢 Configuración de la Empresa")
    
    empresa = get_empresa()
    with st.form("empresa_form"):
        col1, col2 = st.columns(2)
        with col1:
            nombre = st.text_input("Nombre de la empresa", value=empresa.get('nombre', ''))
            nit = st.text_input("NIT", value=empresa.get('nit', ''))
            ubicacion = st.text_input("Dirección", value=empresa.get('ubicacion', ''))
            ciudad = st.text_input("Ciudad", value=empresa.get('ciudad', ''))
        with col2:
            sector = st.selectbox("Sector", ["Construccion", "Industrial", "Servicios", "Comercio", "Agropecuario", "Mineria", "Salud"], 
                                 index=["Construccion","Industrial","Servicios","Comercio","Agropecuario","Mineria","Salud"].index(empresa.get('sector', 'Construccion')))
            telefono = st.text_input("Teléfono", value=empresa.get('telefono', ''))
            email = st.text_input("Email", value=empresa.get('email', ''))
        
        if st.form_submit_button("Guardar Configuración", use_container_width=True):
            update_empresa({"nombre": nombre, "nit": nit, "ubicacion": ubicacion, "ciudad": ciudad, "sector": sector, "telefono": telefono, "email": email})
            st.success("✅ Datos guardados")
            st.rerun()

# ========== PELIGROS (CRUD + IMPORTAR) ==========
elif menu == "Peligros":
    st.header("⚠️ GESTIÓN DE PELIGROS")
    
    tab1, tab2, tab3, tab4 = st.tabs(["➕ Agregar", "📋 Lista", "✏️ Editar/Eliminar", "📎 Importar Excel"])
    
    with tab1:
        with st.form("add_peligro"):
            tipo = st.selectbox("Tipo", ["Fisico", "Quimico", "Biologico", "Ergonomico", "Psicosocial", "Seguridad"])
            descripcion = st.text_area("Descripción")
            col1, col2 = st.columns(2)
            with col1:
                probabilidad = st.slider("Probabilidad (1-4)", 1, 4, 2)
            with col2:
                severidad = st.slider("Severidad (1-3)", 1, 3, 2)
            controls = st.text_area("Controles sugeridos")
            
            if st.form_submit_button("Guardar Peligro", use_container_width=True):
                if descripcion:
                    create_peligro(tipo, descripcion, probabilidad, severidad, controls)
                    st.success("✅ Peligro guardado")
                    st.rerun()
    
    with tab2:
        df = get_peligros()
        st.dataframe(df, use_container_width=True)
        excel_data = exportar_excel(df, "peligros")
        st.download_button("📥 Exportar a Excel", data=excel_data, file_name=f"peligros_{datetime.now().strftime('%Y%m%d')}.xlsx")
    
    with tab3:
        df = get_peligros()
        if not df.empty:
            peligro_id = st.selectbox("Seleccionar peligro", df['id'].tolist(), format_func=lambda x: f"{x} - {df[df['id']==x]['descripcion'].iloc[0][:50]}")
            row = df[df['id'] == peligro_id].iloc[0]
            
            with st.form("edit_peligro"):
                tipo = st.selectbox("Tipo", ["Fisico", "Quimico", "Biologico", "Ergonomico", "Psicosocial", "Seguridad"], index=["Fisico","Quimico","Biologico","Ergonomico","Psicosocial","Seguridad"].index(row['tipo']))
                desc = st.text_area("Descripción", value=row['descripcion'])
                prob = st.slider("Probabilidad", 1, 4, int(row['probabilidad']))
                sev = st.slider("Severidad", 1, 3, int(row['severidad']))
                controls = st.text_area("Controles", value=row['controls'] if row['controls'] else "")
                
                col1, col2 = st.columns(2)
                with col1:
                    if st.form_submit_button("Actualizar", use_container_width=True):
                        update_peligro(peligro_id, tipo, desc, prob, sev, controls)
                        st.success("✅ Actualizado")
                        st.rerun()
                with col2:
                    if st.form_submit_button("Eliminar", use_container_width=True):
                        delete_peligro(peligro_id)
                        st.success("✅ Eliminado")
                        st.rerun()
    
    with tab4:
        uploaded = st.file_uploader("Selecciona archivo Excel", type=['xlsx', 'xls'])
        if uploaded:
            if st.button("Importar", use_container_width=True):
                success, msg = importar_excel_peligros(uploaded)
                if success:
                    st.success(msg)
                    st.rerun()
                else:
                    st.error(msg)
        st.caption("Formato requerido: columnas 'tipo', 'descripcion', 'probabilidad', 'severidad', 'controls'")

# ========== PLAN DE ACCION ==========
elif menu == "Plan de Accion":
    st.header("✅ PLAN DE ACCIÓN")
    
    tab1, tab2 = st.tabs(["➕ Nueva Acción", "📋 Lista y Seguimiento"])
    
    with tab1:
        with st.form("add_accion"):
            descripcion = st.text_area("Descripción de la acción")
            responsable = st.text_input("Responsable")
            fecha_limite = st.date_input("Fecha límite", datetime.now())
            prioridad = st.selectbox("Prioridad", ["Alta", "Media", "Baja"])
            
            if st.form_submit_button("Guardar Acción", use_container_width=True):
                if descripcion and responsable:
                    create_accion(descripcion, responsable, fecha_limite.strftime("%Y-%m-%d"), prioridad)
                    st.success("✅ Acción guardada")
                    st.rerun()
    
    with tab2:
        df = get_acciones()
        if not df.empty:
            for _, row in df.iterrows():
                with st.expander(f"{row['descripcion'][:50]} - {row['responsable']}"):
                    col1, col2 = st.columns(2)
                    with col1:
                        nuevo_estado = st.selectbox("Estado", ["Pendiente", "En progreso", "Completada"], 
                                                   index=["Pendiente","En progreso","Completada"].index(row['estado']),
                                                   key=f"estado_{row['id']}")
                        evidencia = st.text_area("Evidencia", value=row['evidencia'] if row['evidencia'] else "", key=f"evi_{row['id']}")
                    with col2:
                        st.metric("Prioridad", row['prioridad'])
                        st.metric("Fecha límite", row['fecha_limite'])
                    
                    if st.button("Actualizar", key=f"update_{row['id']}"):
                        update_accion(row['id'], nuevo_estado, evidencia)
                        st.success("✅ Actualizado")
                        st.rerun()
                    
                    if st.button("Eliminar", key=f"delete_{row['id']}"):
                        delete_accion(row['id'])
                        st.rerun()
            
            st.markdown("---")
            excel_data = exportar_excel(df, "acciones")
            st.download_button("📥 Exportar Plan de Acción", data=excel_data, file_name=f"plan_accion_{datetime.now().strftime('%Y%m%d')}.xlsx")

# ========== TRABAJADORES ==========
elif menu == "Trabajadores":
    st.header("👥 GESTIÓN DE TRABAJADORES")
    
    tab1, tab2, tab3 = st.tabs(["➕ Registrar", "📋 Lista", "✏️ Editar/Eliminar"])
    
    with tab1:
        with st.form("add_trabajador"):
            col1, col2 = st.columns(2)
            with col1:
                nombre = st.text_input("Nombre completo")
                cedula = st.text_input("Cédula")
                cargo = st.text_input("Cargo")
                area = st.text_input("Área")
            with col2:
                eps = st.selectbox("EPS", ["Sura", "Nueva EPS", "Sanitas", "Compensar", "Famisanar"])
                arl = st.selectbox("ARL", ["Positiva", "Sura", "Colpatria", "Bolivar"])
                fecha_ingreso = st.date_input("Fecha de ingreso", datetime.now())
            
            if st.form_submit_button("Registrar Trabajador", use_container_width=True):
                if nombre:
                    create_trabajador(nombre, cedula, cargo, area, eps, arl, fecha_ingreso.strftime("%Y-%m-%d"))
                    st.success("✅ Trabajador registrado")
                    st.rerun()
    
    with tab2:
        df = get_trabajadores()
        st.dataframe(df, use_container_width=True)
        excel_data = exportar_excel(df, "trabajadores")
        st.download_button("📥 Exportar Trabajadores", data=excel_data, file_name=f"trabajadores_{datetime.now().strftime('%Y%m%d')}.xlsx")
    
    with tab3:
        df = get_trabajadores()
        if not df.empty:
            trabajador_id = st.selectbox("Seleccionar trabajador", df['id'].tolist(), format_func=lambda x: f"{x} - {df[df['id']==x]['nombre'].iloc[0]}")
            row = df[df['id'] == trabajador_id].iloc[0]
            
            with st.form("edit_trabajador"):
                nombre = st.text_input("Nombre", value=row['nombre'])
                cedula = st.text_input("Cédula", value=row['cedula'])
                cargo = st.text_input("Cargo", value=row['cargo'])
                area = st.text_input("Área", value=row['area'] if row['area'] else "")
                
                col1, col2 = st.columns(2)
                with col1:
                    if st.form_submit_button("Actualizar", use_container_width=True):
                        update_trabajador(trabajador_id, nombre, cedula, cargo, area, row['eps'], row['arl'])
                        st.success("✅ Actualizado")
                        st.rerun()
                with col2:
                    if st.form_submit_button("Eliminar", use_container_width=True):
                        delete_trabajador(trabajador_id)
                        st.success("✅ Eliminado")
                        st.rerun()

# ========== INCIDENTES ==========
elif menu == "Incidentes":
    st.header("📝 GESTIÓN DE INCIDENTES")
    
    tab1, tab2 = st.tabs(["➕ Reportar", "📋 Historial"])
    
    with tab1:
        with st.form("add_incidente"):
            tipo = st.selectbox("Tipo", ["Accidente", "Incidente", "Enfermedad Laboral", "Casi accidente"])
            descripcion = st.text_area("Descripción del incidente")
            fecha = st.date_input("Fecha", datetime.now())
            lugar = st.text_input("Lugar")
            gravedad = st.selectbox("Gravedad", ["Leve", "Moderada", "Grave", "Mortal"])
            causa = st.text_area("Causa probable")
            afectado = st.text_input("Trabajador afectado")
            acciones = st.text_area("Acciones tomadas")
            
            if st.form_submit_button("Reportar Incidente", use_container_width=True):
                if descripcion:
                    create_incidente(tipo, descripcion, fecha.strftime("%Y-%m-%d"), lugar, gravedad, causa, afectado, acciones)
                    st.success("✅ Incidente reportado")
                    st.rerun()
    
    with tab2:
        df = get_incidentes()
        st.dataframe(df, use_container_width=True)
        excel_data = exportar_excel(df, "incidentes")
        st.download_button("📥 Exportar Incidentes", data=excel_data, file_name=f"incidentes_{datetime.now().strftime('%Y%m%d')}.xlsx")

# ========== MATRIZ LEGAL ==========
elif menu == "Matriz Legal":
    st.header("📋 MATRIZ LEGAL - ISO 45001 + DECRETO 1072")
    
    df = get_matriz_legal()
    
    # Resumen de cumplimiento
    if not df.empty:
        cumplimiento = df['cumple'].sum()
        total = len(df)
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Requisitos totales", total)
        with col2:
            st.metric("Cumplen", cumplimiento)
        with col3:
            st.metric("% Cumplimiento", f"{(cumplimiento/total)*100:.0f}%")
        st.progress(cumplimiento/total)
        st.markdown("---")
    
    # Tabla editable
    for _, row in df.iterrows():
        with st.expander(f"{row['norma']} - {row['articulo']}: {row['requisito'][:60]}..."):
            col1, col2 = st.columns(2)
            with col1:
                cumple = st.checkbox("✅ Cumple", value=bool(row['cumple']), key=f"cumple_{row['id']}")
                responsable = st.text_input("Responsable", value=row['responsable'] if row['responsable'] else "", key=f"resp_{row['id']}")
            with col2:
                evidencia = st.text_area("Evidencia", value=row['evidencia'] if row['evidencia'] else "", key=f"evi_{row['id']}")
                fecha_cierre = st.date_input("Fecha cierre", key=f"fecha_{row['id']}")
            
            if st.button("Guardar", key=f"save_{row['id']}"):
                update_matriz_legal(row['id'], 1 if cumple else 0, evidencia, fecha_cierre.strftime("%Y-%m-%d") if fecha_cierre else "")
                st.success("✅ Guardado")
                st.rerun()
    
    st.markdown("---")
    excel_data = exportar_excel(df, "matriz_legal")
    st.download_button("📥 Exportar Matriz Legal", data=excel_data, file_name=f"matriz_legal_{datetime.now().strftime('%Y%m%d')}.xlsx")

# ========== AUDITORIAS ==========
elif menu == "Auditorias":
    st.header("🔍 AUDITORÍAS INTERNAS")
    
    col1, col2 = st.columns([1,2])
    with col1:
        with st.form("add_auditoria"):
            codigo = st.text_input("Código", "AUD-001")
            fecha = st.date_input("Fecha", datetime.now())
            auditor = st.text_input("Auditor")
            if st.form_submit_button("Crear Auditoría", use_container_width=True):
                cursor.execute("INSERT INTO auditorias (codigo, fecha, auditor, estado) VALUES (?,?,?,?)",
                              (codigo, fecha.strftime("%Y-%m-%d"), auditor, "Planificada"))
                conn.commit()
                st.success("✅ Auditoría creada")
                st.rerun()
    
    with col2:
        df = pd.read_sql_query("SELECT * FROM auditorias", conn)
        if not df.empty:
            st.dataframe(df, use_container_width=True)

# ========== INFORMES ==========
elif menu == "Informes":
    mostrar_informe()

# ========== CHAT IA ==========
elif menu == "Chat IA":
    st.title("💬 CHAT IA - Consultor SST")
    
    if "messages" not in st.session_state:
        st.session_state.messages = []
    
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.write(msg["content"])
    
    if prompt := st.chat_input("Pregunta sobre SST, normativa ISO 45001, peligros, incidentes..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.write(prompt)
        with st.chat_message("assistant"):
            with st.spinner("🤖 Consultando IA..."):
                respuesta = call_best_ia(prompt)
                st.write(respuesta)
                st.session_state.messages.append({"role": "assistant", "content": respuesta})

st.markdown("---")
st.markdown("<p style='text-align:center; font-size:11px; color:gray'>🔄 SG-SST PHVA | Sistema de Gestión PHVA con IA | Desarrollado por JAN BENITEZ</p>", unsafe_allow_html=True)
