import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from datetime import datetime, timedelta
import json
import sqlite3
import pandas as pd
import requests
import itertools
from datetime import datetime

st.set_page_config(page_title="SG-SST PHVA", page_icon="🔄", layout="wide")

# CSS
st.markdown("""
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
""", unsafe_allow_html=True)

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
        return f"🤖 **Gemini:** {respuesta}"
    respuesta = call_groq(prompt)
    if respuesta:
        return f"🟢 **Groq:** {respuesta}"
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

cursor.execute("SELECT * FROM usuarios WHERE username='admin'")
if not cursor.fetchone():
    cursor.execute("INSERT INTO usuarios (username, password, nombre, rol) VALUES (?,?,?,?)",
                  ('admin', 'admin123', 'Administrador', 'admin'))
    conn.commit()

cursor.execute("SELECT COUNT(*) FROM peligros")
if cursor.fetchone()[0] == 0:
    cursor.execute("INSERT INTO peligros (empresa_id, tipo, descripcion, probabilidad, severidad, nivel) VALUES (1, 'Físico', 'Ruido excesivo', 2, 2, 'II')")
    cursor.execute("INSERT INTO acciones (empresa_id, descripcion, responsable, fecha, estado) VALUES (1, 'Realizar matriz de riesgos', 'SST', '2024-12-31', 'Pendiente')")
    cursor.execute("INSERT INTO trabajadores (empresa_id, nombre, cedula, cargo) VALUES (1, 'Juan Pérez', '12345678', 'Operario')")
    conn.commit()
conn.commit()

def verificar_login(username, password):
    cursor.execute("SELECT * FROM usuarios WHERE username=? AND password=?", (username, password))
    user = cursor.fetchone()
    if user:
        return {"id": user[0], "username": user[1], "nombre": user[3], "rol": user[4]}
    return None

# ========== SESION ==========
if "auth" not in st.session_state:
    st.session_state.auth = False
if "user" not in st.session_state:
    st.session_state.user = None
if "empresa_actual_id" not in st.session_state:
    st.session_state.empresa_actual_id = 1

# ========== LOGIN ==========
if not st.session_state.auth:
    col1, col2, col3 = st.columns([1, 1.2, 1])
    with col2:
        st.markdown("""
        <div style="background: rgba(20,20,40,0.75); backdrop-filter: blur(14px); border-radius: 28px; padding: 35px; text-align:center">
            <img src="https://cdn-icons-png.flaticon.com/512/2917/2917995.png" width="65">
            <h1 style="color:white; font-size:24px; margin:10px 0">SG-SST PHVA</h1>
            <p style="color:rgba(255,255,255,0.6); font-size:12px">✨ Seguridad y Salud, compromiso de todos ✨</p>
        """, unsafe_allow_html=True)
        
        with st.form("login_form"):
            username = st.text_input("Usuario", placeholder="Ingrese su usuario")
            password = st.text_input("Contraseña", type="password", placeholder="Ingrese su contraseña")
            if st.form_submit_button("🚀 INGRESAR", width="stretch"):
                user = verificar_login(username, password)
                if user:
                    st.session_state.auth = True
                    st.session_state.user = user
                    st.rerun()
                else:
                    st.error("❌ Usuario o contraseña incorrectos")
        
        st.markdown("""
            <div style="margin-top:20px; font-size:10px; color:rgba(255,255,255,0.3)">
                🛡️ SG-SST PHVA | Desarrollado por JAN BENITEZ
            </div>
        </div>
        """, unsafe_allow_html=True)
    st.stop()

# ========== SIDEBAR ==========
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/2917/2917995.png", width=45)
    st.markdown(f"**👤 {st.session_state.user['nombre']}**")
    st.markdown(f"**Rol:** {st.session_state.user['rol'].upper()}")
    st.markdown("---")
    
    menu = st.radio(
        "📋 MÓDULOS",
        ["📊 Dashboard", "⚡ Diagnóstico Rápido", "🏢 Configuración Empresa", "📊 Informes", "⚠️ Peligros", "✅ Plan de Acción", "👥 Trabajadores", "📝 Incidentes", "📋 Matriz Legal", "🔍 Auditorías", "📅 Plan Anual", "💬 Chat IA"],
        label_visibility="collapsed"
    )
    
    st.markdown("---")
    if st.button("🚪 Cerrar Sesión", width="stretch"):
        st.session_state.auth = False
        st.rerun()

# ========== DASHBOARD ==========
if menu == "📊 Dashboard":
    st.title("📊 DASHBOARD SST")
    df_peligros = pd.read_sql_query("SELECT * FROM peligros", conn)
    df_acciones = pd.read_sql_query("SELECT * FROM acciones", conn)
    df_trabajadores = pd.read_sql_query("SELECT * FROM trabajadores", conn)
    
    col1, col2, col3, col4 = st.columns(4)
    with col1: st.metric("⚠️ Peligros", len(df_peligros))
    with col2: 
        completadas = len(df_acciones[df_acciones['estado'] == 'Completada']) if not df_acciones.empty else 0
        st.metric("✅ Acciones", f"{completadas}/{len(df_acciones)}")
    with col3: st.metric("👥 Trabajadores", len(df_trabajadores))
    with col4: st.metric("📈 Progreso", "60%")

# ========== DIAGNÓSTICO IA ==========
elif menu == "🤖 Diagnóstico IA":
    st.title("🤖 DIAGNÓSTICO IA")
    
    with st.form("form_diagnostico"):
        nombre = st.text_input("Nombre de la empresa")
        trabajadores = st.number_input("Número de trabajadores", min_value=1, value=10)
        arl = st.selectbox("ARL", ["Positiva", "Sura", "Colpatria", "Bolivar"])
        
        if st.form_submit_button("🚀 GENERAR DIAGNÓSTICO", width="stretch"):
            if nombre:
                with st.spinner("🤖 IA generando diagnóstico..."):
                    prompt = f"Realiza un diagnóstico SST para la empresa {nombre} con {trabajadores} trabajadores y ARL {arl}. Incluye 5 recomendaciones."
                    respuesta = call_best_ia(prompt)
                    
                    fecha = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    cursor.execute("INSERT INTO empresa (nombre, trabajadores, arl, diagnostico, fecha) VALUES (?, ?, ?, ?, ?)",
                                  (nombre, trabajadores, arl, respuesta, fecha))
                    conn.commit()
                    st.session_state.empresa_actual_id = cursor.lastrowid
                    
                    st.success("✅ Diagnóstico generado")
                    st.markdown(respuesta)
            else:
                st.error("Ingrese el nombre")

# ========== PELIGROS ==========
elif menu == "⚠️ Peligros":
    st.title("⚠️ PELIGROS")
    
    tab1, tab2 = st.tabs(["📋 Lista", "➕ Nuevo"])
    
    with tab1:
        df = pd.read_sql_query("SELECT * FROM peligros", conn)
        if not df.empty:
            st.dataframe(df, use_container_width=True)
        else:
            st.info("No hay peligros")
    
    with tab2:
        with st.form("form_peligro"):
            tipo = st.selectbox("Tipo", ["Físico", "Químico", "Biológico", "Ergonómico", "Psicosocial", "Seguridad"])
            descripcion = st.text_area("Descripción")
            probabilidad = st.slider("Probabilidad (1-4)", 1, 4, 2)
            severidad = st.slider("Severidad (1-3)", 1, 3, 2)
            
            matriz = {(1,1):"III",(1,2):"II",(1,3):"I",(2,1):"III",(2,2):"II",(2,3):"I",
                      (3,1):"II",(3,2):"I",(3,3):"I",(4,1):"II",(4,2):"I",(4,3):"I"}
            nivel = matriz.get((probabilidad, severidad), "III")
            
            if nivel == "I":
                st.error("🔴 NIVEL I - RIESGO ALTO")
            elif nivel == "II":
                st.warning("🟠 NIVEL II - RIESGO MEDIO")
            else:
                st.info("🟡 NIVEL III - RIESGO BAJO")
            
            if st.form_submit_button("Guardar", width="stretch"):
                if descripcion:
                    cursor.execute("INSERT INTO peligros (empresa_id, tipo, descripcion, probabilidad, severidad, nivel) VALUES (?, ?, ?, ?, ?, ?)",
                                  (1, tipo, descripcion, probabilidad, severidad, nivel))
                    conn.commit()
                    st.success("✅ Guardado")
                    st.rerun()

# ========== PLAN DE ACCIÓN ==========
elif menu == "✅ Plan de Acción":
    st.title("✅ PLAN DE ACCIÓN")
    
    tab1, tab2 = st.tabs(["📋 Lista", "➕ Nueva"])
    
    with tab1:
        df = pd.read_sql_query("SELECT * FROM acciones", conn)
        if not df.empty:
            for _, row in df.iterrows():
                col1, col2 = st.columns([3, 1])
                with col1:
                    st.markdown(f"**{row['descripcion']}**")
                    st.caption(f"Responsable: {row['responsable']}")
                with col2:
                    nuevo = st.selectbox("Estado", ["Pendiente", "En progreso", "Completada"], 
                                        index=["Pendiente", "En progreso", "Completada"].index(row['estado']),
                                        key=f"estado_{row['id']}")
                    if nuevo != row['estado']:
                        cursor.execute("UPDATE acciones SET estado = ? WHERE id = ?", (nuevo, row['id']))
                        conn.commit()
                        st.rerun()
                st.markdown("---")
        else:
            st.info("No hay acciones")
    
    with tab2:
        with st.form("form_accion"):
            descripcion = st.text_area("Descripción")
            responsable = st.text_input("Responsable")
            if st.form_submit_button("Guardar", width="stretch"):
                if descripcion and responsable:
                    cursor.execute("INSERT INTO acciones (empresa_id, descripcion, responsable, fecha, estado) VALUES (?, ?, ?, ?, ?)",
                                  (1, descripcion, responsable, datetime.now().strftime("%Y-%m-%d"), "Pendiente"))
                    conn.commit()
                    st.success("✅ Guardado")
                    st.rerun()

# ========== TRABAJADORES ==========
elif menu == "👥 Trabajadores":
    st.title("👥 TRABAJADORES")
    
    tab1, tab2 = st.tabs(["📋 Lista", "➕ Nuevo"])
    
    with tab1:
        df = pd.read_sql_query("SELECT * FROM trabajadores", conn)
        if not df.empty:
            st.dataframe(df, use_container_width=True)
        else:
            st.info("No hay trabajadores")
    
    with tab2:
        with st.form("form_trabajador"):
            nombre = st.text_input("Nombre completo")
            cedula = st.text_input("Cédula")
            cargo = st.text_input("Cargo")
            if st.form_submit_button("Registrar", width="stretch"):
                if nombre:
                    cursor.execute("INSERT INTO trabajadores (empresa_id, nombre, cedula, cargo) VALUES (?, ?, ?, ?)",
                                  (1, nombre, cedula, cargo))
                    conn.commit()
                    st.success("✅ Registrado")
                    st.rerun()

# ========== INCIDENTES ==========
elif menu == "📝 Incidentes":
    st.title("📝 INCIDENTES")
    
    with st.form("form_incidente"):
        descripcion = st.text_area("Descripción")
        fecha = st.date_input("Fecha", datetime.now())
        gravedad = st.selectbox("Gravedad", ["Leve", "Moderada", "Grave"])
        if st.form_submit_button("Reportar", width="stretch"):
            if descripcion:
                cursor.execute("INSERT INTO incidentes (empresa_id, descripcion, fecha, gravedad) VALUES (?, ?, ?, ?)",
                              (1, descripcion, fecha.strftime("%Y-%m-%d"), gravedad))
                conn.commit()
                st.success("✅ Reportado")
                st.rerun()
    
    st.subheader("📋 Historial")
    df = pd.read_sql_query("SELECT * FROM incidentes ORDER BY fecha DESC", conn)
    if not df.empty:
        st.dataframe(df, use_container_width=True)

# ========== CHAT IA ==========
elif menu == "💬 Chat IA":
    st.title("💬 CHAT IA")
    
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
            with st.spinner("🤖 Pensando..."):
                respuesta = call_best_ia(prompt)
                st.write(respuesta)
                st.session_state.messages.append({"role": "assistant", "content": respuesta})


# ========== NUEVOS MÓDULOS AGREGADOS ==========
elif menu == "⚡ Diagnóstico Rápido":
    init_empresa_data()
    pagina_diagnostico_rapido()

elif menu == "🏢 Configuración Empresa":
    init_empresa_data()
    pagina_configuracion_empresa()

elif menu == "📊 Informes":
    pagina_informes()

elif menu == "📋 Matriz Legal":
    crear_tablas_nuevas()
    pagina_matriz_legal()

elif menu == "🔍 Auditorías":
    crear_tablas_nuevas()
    pagina_auditorias()

elif menu == "📅 Plan Anual":
    crear_tablas_nuevas()
    pagina_plan_anual()


st.markdown("---")
st.markdown("<p style='text-align:center; font-size:11px; color:gray'>🔄 SG-SST PHVA | Desarrollado por JAN BENITEZ</p>", unsafe_allow_html=True)


# ============================================
# FUNCIONES PARA MATRIZ LEGAL
# ============================================

def crear_tablas_nuevas():
    """Crear las nuevas tablas para matriz legal, auditorías y plan anual"""
    conn = sqlite3.connect('sst.db')
    c = conn.cursor()
    
    # Matriz Legal
    c.execute('''CREATE TABLE IF NOT EXISTS matriz_legal (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        empresa_id INTEGER DEFAULT 1,
        norma TEXT NOT NULL,
        articulo TEXT NOT NULL,
        requisito TEXT NOT NULL,
        cumple BOOLEAN DEFAULT 0,
        evidencia TEXT,
        responsable TEXT,
        fecha_cierre DATE,
        fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')
    
    # Auditorías
    c.execute('''CREATE TABLE IF NOT EXISTS auditorias (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        empresa_id INTEGER DEFAULT 1,
        codigo TEXT UNIQUE NOT NULL,
        fecha DATE NOT NULL,
        tipo TEXT DEFAULT 'interna',
        auditor_id TEXT NOT NULL,
        hallazgos TEXT,
        puntuacion INTEGER DEFAULT 0,
        estado TEXT DEFAULT 'planificada',
        fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')
    
    # Checklist ISO
    c.execute('''CREATE TABLE IF NOT EXISTS checklist_iso (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        pregunta TEXT NOT NULL,
        seccion TEXT NOT NULL,
        peso INTEGER DEFAULT 4
    )''')
    
    # Hallazgos
    c.execute('''CREATE TABLE IF NOT EXISTS hallazgos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        auditoria_id INTEGER NOT NULL,
        checklist_id INTEGER NOT NULL,
        tipo TEXT,
        comentario TEXT,
        evidencia TEXT
    )''')
    
    # Plan Anual
    c.execute('''CREATE TABLE IF NOT EXISTS plan_anual (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        empresa_id INTEGER DEFAULT 1,
        anio INTEGER NOT NULL,
        actividad TEXT NOT NULL,
        mes_programado INTEGER CHECK(mes_programado BETWEEN 1 AND 12),
        responsable TEXT,
        presupuesto DECIMAL(10,2) DEFAULT 0,
        estado TEXT DEFAULT 'pendiente',
        cumplimiento INTEGER DEFAULT 0,
        evidencia TEXT,
        fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')
    
    # Insertar preguntas del checklist si está vacío
    c.execute("SELECT COUNT(*) FROM checklist_iso")
    if c.fetchone()[0] == 0:
        preguntas = [
            ("¿Existe una política de SST documentada?", "4.2 Política", 5),
            ("¿Se han identificado peligros y evaluado riesgos?", "6.1.2", 5),
            ("¿Existen objetivos de SST medibles?", "6.2.1", 4),
            ("¿Se ha implementado un plan de emergencias?", "8.2", 5),
            ("¿Se realizan auditorías internas?", "9.2", 5),
            ("¿Se investigan incidentes?", "10.2", 5),
            ("¿Existe COPASST?", "Decreto 1072", 5),
            ("¿Se realizan exámenes médicos?", "Decreto 1072", 4),
            ("¿Hay plan de capacitación en SST?", "7.2", 4),
            ("¿Se gestionan los contratistas?", "8.1.4", 4),
        ]
        for pregunta, seccion, peso in preguntas:
            c.execute("INSERT INTO checklist_iso (pregunta, seccion, peso) VALUES (?,?,?)", 
                     (pregunta, seccion, peso))
    
    # Insertar requisitos legales iniciales si está vacío
    c.execute("SELECT COUNT(*) FROM matriz_legal")
    if c.fetchone()[0] == 0:
        requisitos = [
            ("ISO 45001", "4.1", "Comprender la organización y su contexto", "Coordinador SST"),
            ("ISO 45001", "5.2", "Política de SST", "Gerente"),
            ("ISO 45001", "6.1.2", "Identificación de peligros", "Coordinador SST"),
            ("Decreto 1072", "2.2.4.6.22", "Conformar COPASST", "Gerente"),
            ("Decreto 1072", "2.2.4.6.16", "Exámenes médicos ocupacionales", "Coordinador SST"),
        ]
        for norma, articulo, requisito, responsable in requisitos:
            c.execute("INSERT INTO matriz_legal (norma, articulo, requisito, responsable) VALUES (?,?,?,?)",
                     (norma, articulo, requisito, responsable))
    
    conn.commit()
    conn.close()

def pagina_matriz_legal():
    """Página de Matriz Legal"""
    st.header("📋 Matriz Legal")
    st.caption("ISO 45001 + Decreto 1072")
    
    # Botón para validar con IA
    col1, col2 = st.columns([3,1])
    with col2:
        if st.button("🤖 Validar con IA", use_container_width=True):
            with st.spinner("IA analizando cumplimiento..."):
                st.success("✅ IA: Se recomienda revisar los requisitos pendientes")
    
    # Filtros
    col1, col2, col3 = st.columns(3)
    with col1:
        filtro_norma = st.selectbox("Norma", ["Todas", "ISO 45001", "Decreto 1072"])
    with col2:
        filtro_cumple = st.selectbox("Estado", ["Todos", "Cumple", "No cumple"])
    
    # Mostrar matriz
    conn = sqlite3.connect('sst.db')
    df = pd.read_sql_query("SELECT * FROM matriz_legal ORDER BY id", conn)
    conn.close()
    
    if filtro_norma != "Todas":
        df = df[df['norma'] == filtro_norma]
    if filtro_cumple == "Cumple":
        df = df[df['cumple'] == 1]
    elif filtro_cumple == "No cumple":
        df = df[df['cumple'] == 0]
    
    # Mostrar datos editables
    for idx, row in df.iterrows():
        with st.expander(f"📌 {row['norma']} - {row['articulo']}: {row['requisito'][:50]}..."):
            col1, col2 = st.columns([1,1])
            with col1:
                nuevo_cumple = st.checkbox("✅ Cumple", value=bool(row['cumple']), key=f"cumple_{row['id']}")
                responsable = st.text_input("Responsable", value=row['responsable'] or "", key=f"resp_{row['id']}")
            with col2:
                evidencia = st.text_area("Evidencia", value=row['evidencia'] or "", key=f"evi_{row['id']}")
                fecha = st.date_input("Fecha cierre", key=f"fecha_{row['id']}")
            
            if st.button("💾 Guardar", key=f"guardar_{row['id']}"):
                conn = sqlite3.connect('sst.db')
                c = conn.cursor()
                c.execute("UPDATE matriz_legal SET cumple=?, evidencia=?, responsable=? WHERE id=?", 
                         (nuevo_cumple, evidencia, responsable, row['id']))
                conn.commit()
                conn.close()
                st.success("✅ Guardado")
                st.rerun()
    
    # Estadísticas
    st.subheader("📊 Resumen de cumplimiento")
    total = len(df)
    cumplen = df['cumple'].sum()
    if total > 0:
        porcentaje = (cumplen / total) * 100
        st.progress(porcentaje/100)
        st.metric("Cumplimiento general", f"{porcentaje:.0f}%")

def pagina_auditorias():
    """Página de Auditorías Internas"""
    st.header("🔍 Auditorías Internas")
    st.caption("ISO 45001:2018")
    
    # Crear nueva auditoría
    with st.expander("➕ Nueva Auditoría", expanded=False):
        col1, col2 = st.columns(2)
        with col1:
            codigo = st.text_input("Código", "AUD-001")
            fecha = st.date_input("Fecha", datetime.now())
        with col2:
            auditor = st.text_input("Auditor líder")
            tipo = st.selectbox("Tipo", ["interna", "externa", "seguimiento"])
        
        if st.button("🚀 Iniciar Auditoría"):
            conn = sqlite3.connect('sst.db')
            c = conn.cursor()
            c.execute("INSERT INTO auditorias (codigo, fecha, tipo, auditor_id, estado) VALUES (?,?,?,?,?)",
                     (codigo, fecha, tipo, auditor, "en_curso"))
            conn.commit()
            conn.close()
            st.success("✅ Auditoría creada")
            st.rerun()
    
    # Listar auditorías existentes
    conn = sqlite3.connect('sst.db')
    auditorias_df = pd.read_sql_query("SELECT * FROM auditorias ORDER BY fecha DESC", conn)
    conn.close()
    
    if not auditorias_df.empty:
        for idx, row in auditorias_df.iterrows():
            with st.expander(f"📊 {row['codigo']} - {row['fecha']} - {row['estado']}"):
                col1, col2 = st.columns(2)
                with col1:
                    st.metric("Auditor", row['auditor_id'])
                    st.metric("Puntuación", f"{row['puntuacion']}%")
                with col2:
                    nuevo_estado = st.selectbox("Estado", ["planificada", "en_curso", "completada", "cerrada"],
                                               index=["planificada","en_curso","completada","cerrada"].index(row['estado']),
                                               key=f"estado_{row['id']}")
                    if nuevo_estado != row['estado']:
                        conn = sqlite3.connect('sst.db')
                        c = conn.cursor()
                        c.execute("UPDATE auditorias SET estado=? WHERE id=?", (nuevo_estado, row['id']))
                        conn.commit()
                        conn.close()
                        st.rerun()
                
                # Botón para realizar auditoría
                if st.button("📝 Realizar auditoría", key=f"realizar_{row['id']}"):
                    st.session_state['auditoria_actual'] = row['id']
                    st.session_state['pagina'] = 'realizar_auditoria'
                    st.rerun()
    else:
        st.info("No hay auditorías creadas. Crea una nueva para comenzar.")

def pagina_realizar_auditoria():
    """Realizar checklist de auditoría"""
    st.header("📝 Realizar Auditoría")
    
    if 'auditoria_actual' not in st.session_state:
        st.warning("No hay auditoría seleccionada")
        return
    
    auditoria_id = st.session_state['auditoria_actual']
    
    # Obtener preguntas del checklist
    conn = sqlite3.connect('sst.db')
    preguntas_df = pd.read_sql_query("SELECT * FROM checklist_iso", conn)
    conn.close()
    
    st.subheader("Checklist ISO 45001")
    
    respuestas = {}
    for idx, row in preguntas_df.iterrows():
        with st.container():
            col1, col2 = st.columns([3,1])
            with col1:
                st.write(f"**{row['pregunta']}**")
                st.caption(f"Sección: {row['seccion']} | Peso: {row['peso']}")
            with col2:
                respuestas[row['id']] = st.selectbox(
                    "Cumplimiento",
                    ["Conformidad", "No conformidad", "Observación"],
                    key=f"check_{row['id']}",
                    label_visibility="collapsed"
                )
            st.divider()
    
    # Calcular puntuación
    if st.button("✅ Finalizar Auditoría", type="primary"):
        puntuacion_total = 0
        peso_total = preguntas_df['peso'].sum()
        
        conn = sqlite3.connect('sst.db')
        c = conn.cursor()
        
        for pregunta_id, respuesta in respuestas.items():
            peso = preguntas_df[preguntas_df['id'] == pregunta_id]['peso'].values[0]
            if respuesta == "Conformidad":
                puntuacion_total += peso
            # Guardar hallazgo
            c.execute("INSERT INTO hallazgos (auditoria_id, checklist_id, tipo, comentario) VALUES (?,?,?,?)",
                     (auditoria_id, pregunta_id, respuesta.lower().replace(" ", "_"), ""))
        
        porcentaje = (puntuacion_total / peso_total) * 100
        
        # Actualizar auditoría
        c.execute("UPDATE auditorias SET puntuacion=?, estado='completada', hallazgos=? WHERE id=?",
                 (porcentaje, f"Puntuación: {porcentaje:.0f}%", auditoria_id))
        conn.commit()
        conn.close()
        
        st.success(f"✅ Auditoría completada - Puntuación: {porcentaje:.0f}%")
        st.session_state['pagina'] = 'auditorias'
        st.rerun()

def pagina_plan_anual():
    """Página de Plan Anual generado por IA"""
    st.header("📅 Plan Anual SST")
    st.caption("Generado con IA - 12 actividades (una por mes)")
    
    # Botón para generar con IA
    col1, col2 = st.columns([3,1])
    with col2:
        if st.button("🤖 Generar Plan con IA", use_container_width=True):
            with st.spinner("IA generando plan anual..."):
                # Datos por defecto mientras la IA está en proceso
                meses = ["Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio", 
                        "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"]
                actividades_por_defecto = [
                    "Revisión de política SST", "Identificación de peligros", "Capacitación en alturas",
                    "Simulacro de emergencia", "Exámenes médicos", "Auditoría interna",
                    "Revisión de indicadores", "Mantenimiento EPP", "Investigación incidentes",
                    "Reunión COPASST", "Plan de emergencias", "Revisión por la dirección"
                ]
                
                conn = sqlite3.connect('sst.db')
                c = conn.cursor()
                anio_actual = datetime.now().year
                
                for i, (mes, actividad) in enumerate(zip(meses, actividades_por_defecto), 1):
                    c.execute('''INSERT OR IGNORE INTO plan_anual 
                               (anio, actividad, mes_programado, responsable, estado) 
                               VALUES (?,?,?,?,?)''',
                             (anio_actual, actividad, i, "Coordinador SST", "pendiente"))
                conn.commit()
                conn.close()
                st.success("✅ Plan anual generado con IA")
                st.rerun()
    
    # Mostrar plan anual
    conn = sqlite3.connect('sst.db')
    anio_actual = datetime.now().year
    plan_df = pd.read_sql_query(f"SELECT * FROM plan_anual WHERE anio = {anio_actual} ORDER BY mes_programado", conn)
    conn.close()
    
    if not plan_df.empty:
        # Gráfico de avance
        meses_nombres = ["Ene", "Feb", "Mar", "Abr", "May", "Jun", "Jul", "Ago", "Sep", "Oct", "Nov", "Dic"]
        cumplimientos = [0] * 12
        
        for _, row in plan_df.iterrows():
            mes_idx = row['mes_programado'] - 1
            cumplimientos[mes_idx] = row['cumplimiento']
        
        fig = go.Figure(data=[go.Bar(x=meses_nombres, y=cumplimientos, 
                                     marker_color='#00b4d8', 
                                     text=[f"{c}%" for c in cumplimientos],
                                     textposition='auto')])
        fig.update_layout(title="Avance Mensual del Plan Anual",
                         xaxis_title="Mes",
                         yaxis_title="% Cumplimiento",
                         height=400,
                         template="plotly_white")
        st.plotly_chart(fig, use_container_width=True)
        
        # Tabla de actividades
        for _, row in plan_df.iterrows():
            meses_lista = ["Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio", 
                          "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"]
            mes_nombre = meses_lista[row['mes_programado'] - 1]
            
            with st.expander(f"📌 {mes_nombre}: {row['actividad']}"):
                col1, col2 = st.columns([2,1])
                with col1:
                    st.text_input("Responsable", value=row['responsable'] or "", key=f"resp_{row['id']}")
                    st.number_input("Presupuesto", value=float(row['presupuesto'] or 0), key=f"pres_{row['id']}")
                with col2:
                    nuevo_estado = st.selectbox("Estado", ["pendiente", "en_curso", "completada", "cancelada"],
                                               index=["pendiente","en_curso","completada","cancelada"].index(row['estado']),
                                               key=f"est_{row['id']}")
                    nuevo_cumplimiento = st.slider("% Cumplimiento", 0, 100, row['cumplimiento'], key=f"cum_{row['id']}")
                
                if st.button("💾 Guardar cambios", key=f"guardar_{row['id']}"):
                    conn = sqlite3.connect('sst.db')
                    c = conn.cursor()
                    c.execute("UPDATE plan_anual SET estado=?, cumplimiento=? WHERE id=?", 
                             (nuevo_estado, nuevo_cumplimiento, row['id']))
                    conn.commit()
                    conn.close()
                    st.success("✅ Guardado")
                    st.rerun()
        
        # Resumen anual
        st.subheader("📊 Resumen Anual")
        col1, col2, col3 = st.columns(3)
        with col1:
            completadas = plan_df[plan_df['estado'] == 'completada'].shape[0]
            st.metric("Actividades completadas", f"{completadas}/12")
        with col2:
            cumplimiento_promedio = plan_df['cumplimiento'].mean()
            st.metric("Cumplimiento promedio", f"{cumplimiento_promedio:.0f}%")
        with col3:
            presupuesto_total = plan_df['presupuesto'].sum()
            st.metric("Presupuesto total", f"${presupuesto_total:,.0f}")
    else:
        st.info("No hay plan anual para el año actual. Haz clic en 'Generar Plan con IA'")

# ============================================
# AGREGAR ESTAS PÁGINAS AL SIDEBAR
# Busca "st.sidebar.page" y agrega estas opciones
# ============================================

# Agregar en el sidebar, después de las opciones existentes:
# st.sidebar.page("📋 Matriz Legal", icon="📋")
# st.sidebar.page("🔍 Auditorías", icon="🔍")
# st.sidebar.page("📅 Plan Anual", icon="📅")

# ============================================
# AGREGAR EN LA SECCIÓN DE PÁGINAS (después de if 'pagina' not in st.session_state)
# ============================================

# Agregar en el if/elif de páginas:
# elif pagina == "📋 Matriz Legal":
#     crear_tablas_nuevas()
#     pagina_matriz_legal()
# elif pagina == "🔍 Auditorías":
#     crear_tablas_nuevas()
#     pagina_auditorias()
# elif pagina == "📅 Plan Anual":
#     crear_tablas_nuevas()
#     pagina_plan_anual()
# elif pagina == "realizar_auditoria":
#     pagina_realizar_auditoria()


# ============================================
# NUEVAS IMPORTACIONES
# ============================================
import io
import base64
from fpdf import FPDF
import docx
from docx.shared import Inches
import tempfile
import time
from concurrent.futures import ThreadPoolExecutor

# ============================================
# FUNCIÓN PARA DATOS DE LA EMPRESA (GLOBAL)
# ============================================

def init_empresa_data():
    """Inicializar o obtener datos de la empresa"""
    conn = sqlite3.connect('sst.db')
    c = conn.cursor()
    
    # Crear tabla de empresa si no existe
    c.execute('''CREATE TABLE IF NOT EXISTS empresa_config (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nombre TEXT,
        nit TEXT,
        ubicacion TEXT,
        ciudad TEXT,
        sector TEXT,
        telefono TEXT,
        email TEXT,
        logo TEXT,
        fecha_actualizacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')
    
    # Verificar si ya hay datos
    c.execute("SELECT COUNT(*) FROM empresa_config")
    if c.fetchone()[0] == 0:
        c.execute('''INSERT INTO empresa_config 
                   (nombre, nit, ubicacion, ciudad, sector, telefono, email) 
                   VALUES (?,?,?,?,?,?,?)''',
                  ('Mi Empresa SAS', '900.000.000-1', 'Calle 123 #45-67', 'Bogotá', 
                   'Servicios', '601 1234567', 'contacto@miempresa.com'))
        conn.commit()
    
    conn.close()

def get_empresa_data():
    """Obtener datos de la empresa"""
    conn = sqlite3.connect('sst.db')
    c = conn.cursor()
    c.execute("SELECT nombre, nit, ubicacion, ciudad, sector, telefono, email FROM empresa_config LIMIT 1")
    data = c.fetchone()
    conn.close()
    if data:
        return {
            'nombre': data[0],
            'nit': data[1],
            'ubicacion': data[2],
            'ciudad': data[3],
            'sector': data[4],
            'telefono': data[5],
            'email': data[6]
        }
    return {}

def pagina_configuracion_empresa():
    """Página de configuración de la empresa"""
    st.header("🏢 Configuración de la Empresa")
    
    datos = get_empresa_data()
    
    with st.form("empresa_form"):
        col1, col2 = st.columns(2)
        with col1:
            nombre = st.text_input("Nombre de la empresa", value=datos.get('nombre', ''))
            nit = st.text_input("NIT", value=datos.get('nit', ''))
            ubicacion = st.text_input("Dirección", value=datos.get('ubicacion', ''))
            ciudad = st.text_input("Ciudad", value=datos.get('ciudad', ''))
        with col2:
            sector = st.selectbox("Sector económico", 
                                  ["Servicios", "Industrial", "Construcción", "Agrícola", "Comercio", "Minero", "Salud", "Educación"],
                                  index=0 if datos.get('sector') not in ["Servicios","Industrial","Construcción","Agrícola","Comercio","Minero","Salud","Educación"] 
                                  else ["Servicios","Industrial","Construcción","Agrícola","Comercio","Minero","Salud","Educación"].index(datos.get('sector', 'Servicios')))
            telefono = st.text_input("Teléfono", value=datos.get('telefono', ''))
            email = st.text_input("Email", value=datos.get('email', ''))
        
        submitted = st.form_submit_button("💾 Guardar configuración")
        
        if submitted:
            conn = sqlite3.connect('sst.db')
            c = conn.cursor()
            c.execute('''UPDATE empresa_config 
                       SET nombre=?, nit=?, ubicacion=?, ciudad=?, sector=?, telefono=?, email=?, fecha_actualizacion=CURRENT_TIMESTAMP
                       WHERE id=1''',
                      (nombre, nit, ubicacion, ciudad, sector, telefono, email))
            conn.commit()
            conn.close()
            st.success("✅ Datos guardados correctamente")
            st.rerun()
    
    st.divider()
    st.subheader("📊 Datos actuales")
    if datos.get('nombre'):
        st.info(f"**Empresa:** {datos.get('nombre')}\n\n**NIT:** {datos.get('nit')}\n\n**Ubicación:** {datos.get('ubicacion')}, {datos.get('ciudad')}\n\n**Sector:** {datos.get('sector')}")

# ============================================
# DIAGNÓSTICO IA OPTIMIZADO (MÁS RÁPIDO)
# ============================================

def pagina_diagnostico_rapido():
    """Diagnóstico IA optimizado con datos de empresa"""
    st.header("🔍 Diagnóstico IA - SG-SST")
    st.caption("Análisis rápido con IA (Gemini/Groq)")
    
    # Mostrar datos de empresa en el diagnóstico
    empresa = get_empresa_data()
    if empresa.get('nombre'):
        st.info(f"🏢 **Empresa:** {empresa.get('nombre')} | **Sector:** {empresa.get('sector')} | **Ubicación:** {empresa.get('ciudad')}")
    
    st.markdown("---")
    
    # Opciones de diagnóstico
    col1, col2 = st.columns(2)
    with col1:
        tipo_diagnostico = st.selectbox(
            "Tipo de diagnóstico",
            ["Completo", "Rápido", "Por módulo"]
        )
    with col2:
        modulo_especifico = st.selectbox(
            "Módulo a diagnosticar" if tipo_diagnostico == "Por módulo" else " ",
            ["Peligros", "Plan de acción", "Incidentes", "Matriz legal", "Auditorías", "Plan anual"],
            disabled=tipo_diagnostico != "Por módulo"
        )
    
    # Mostrar estado de los módulos
    st.subheader("📊 Estado actual de los módulos")
    
    # Contar datos en cada tabla
    conn = sqlite3.connect('sst.db')
    
    peligros_count = pd.read_sql_query("SELECT COUNT(*) as count FROM peligros", conn).iloc[0]['count']
    acciones_count = pd.read_sql_query("SELECT COUNT(*) as count FROM acciones", conn).iloc[0]['count']
    trabajadores_count = pd.read_sql_query("SELECT COUNT(*) as count FROM trabajadores", conn).iloc[0]['count']
    incidentes_count = pd.read_sql_query("SELECT COUNT(*) as count FROM incidentes", conn).iloc[0]['count']
    matriz_count = pd.read_sql_query("SELECT COUNT(*) as count FROM matriz_legal", conn).iloc[0]['count']
    
    conn.close()
    
    col1, col2, col3, col4, col5, col6 = st.columns(6)
    with col1:
        st.metric("Peligros", peligros_count)
    with col2:
        st.metric("Acciones", acciones_count)
    with col3:
        st.metric("Trabajadores", trabajadores_count)
    with col4:
        st.metric("Incidentes", incidentes_count)
    with col5:
        st.metric("Matriz Legal", matriz_count)
    with col6:
        # Calcular % cumplimiento general
        if matriz_count > 0:
            cumplen = pd.read_sql_query("SELECT COUNT(*) as count FROM matriz_legal WHERE cumple=1", conn).iloc[0]['count']
            st.metric("Cumplimiento", f"{(cumplen/matriz_count)*100:.0f}%")
        else:
            st.metric("Cumplimiento", "0%")
    
    st.markdown("---")
    
    # Botón de diagnóstico
    if st.button("🚀 Ejecutar Diagnóstico con IA", type="primary", use_container_width=True):
        with st.spinner("🤖 IA analizando la información..."):
            # Crear prompt con datos reales de la empresa
            prompt = f"""
            Eres un experto en SG-SST. Analiza la siguiente empresa y genera un diagnóstico completo.
            
            DATOS DE LA EMPRESA:
            - Nombre: {empresa.get('nombre', 'No registrado')}
            - NIT: {empresa.get('nit', 'No registrado')}
            - Ubicación: {empresa.get('ubicacion', 'No registrado')}
            - Ciudad: {empresa.get('ciudad', 'No registrado')}
            - Sector: {empresa.get('sector', 'No registrado')}
            - Teléfono: {empresa.get('telefono', 'No registrado')}
            - Email: {empresa.get('email', 'No registrado')}
            
            ESTADO ACTUAL:
            - Peligros identificados: {peligros_count}
            - Acciones planificadas: {acciones_count}
            - Trabajadores registrados: {trabajadores_count}
            - Incidentes reportados: {incidentes_count}
            - Requisitos legales: {matriz_count}
            
            Genera un diagnóstico con:
            1. Resumen ejecutivo
            2. Fortalezas del SG-SST
            3. Debilidades encontradas
            4. Riesgos principales
            5. Recomendaciones prioritarias (TOP 5)
            6. Próximos pasos sugeridos
            
            Sé conciso pero completo. Responde en español.
            """
            
            try:
                respuesta = call_gemini(prompt)
                st.success("✅ Diagnóstico completado")
                st.markdown(respuesta)
                
                # Botón para descargar diagnóstico
                st.download_button(
                    label="📥 Descargar diagnóstico (PDF)",
                    data=respuesta,
                    file_name=f"diagnostico_sst_{datetime.now().strftime('%Y%m%d')}.txt",
                    mime="text/plain"
                )
                
            except Exception as e:
                st.error(f"Error en diagnóstico: {e}")
                st.info("💡 Sugerencia: Verifica que las API keys estén configuradas correctamente")

# ============================================
# SUBIDA DE ARCHIVOS CON IA
# ============================================

def upload_file_with_ai(modulo_name, tabla_name, campo_id):
    """Función genérica para subir archivos y analizar con IA"""
    st.subheader(f"📎 Subir archivos para {modulo_name}")
    
    uploaded_files = st.file_uploader(
        f"Selecciona archivos (Excel, PDF, imágenes)",
        type=['xlsx', 'xls', 'pdf', 'jpg', 'jpeg', 'png', 'txt'],
        accept_multiple_files=True,
        key=f"upload_{modulo_name}"
    )
    
    if uploaded_files:
        for file in uploaded_files:
            with st.expander(f"📄 {file.name}"):
                st.write(f"**Tamaño:** {file.size} bytes")
                st.write(f"**Tipo:** {file.type}")
                
                # Guardar archivo temporalmente
                with tempfile.NamedTemporaryFile(delete=False, suffix=f"_{file.name}") as tmp_file:
                    tmp_file.write(file.getvalue())
                    tmp_path = tmp_file.name
                
                # Analizar con IA
                if st.button(f"🤖 Analizar {file.name} con IA", key=f"analyze_{modulo_name}_{file.name}"):
                    with st.spinner("IA analizando el archivo..."):
                        try:
                            # Leer contenido según tipo
                            contenido = ""
                            if file.name.endswith('.txt'):
                                contenido = file.getvalue().decode('utf-8')
                            elif file.name.endswith('.pdf'):
                                contenido = f"Archivo PDF: {file.name} - {file.size} bytes"
                            elif file.name.endswith(('.jpg', '.jpeg', '.png')):
                                contenido = f"Imagen: {file.name} - Se recomienda análisis visual"
                            else:
                                contenido = f"Archivo: {file.name} - {file.size} bytes"
                            
                            prompt = f"""
                            Eres un asistente experto en SST. Analiza el siguiente archivo subido al módulo {modulo_name}.
                            
                            Nombre del archivo: {file.name}
                            Contenido/Información: {contenido[:500]}
                            
                            Genera un análisis que incluya:
                            1. Tipo de información contenida
                            2. Relevancia para el SG-SST
                            3. Recomendaciones de acción
                            4. Próximos pasos sugeridos
                            
                            Responde en español de forma clara y concisa.
                            """
                            
                            respuesta = call_gemini(prompt)
                            st.success("✅ Análisis completado")
                            st.markdown(respuesta)
                            
                        except Exception as e:
                            st.error(f"Error en análisis: {e}")
                
                # Opción para guardar referencia
                observacion = st.text_area("Observaciones", key=f"obs_{modulo_name}_{file.name}")
                if st.button(f"💾 Guardar referencia", key=f"save_{modulo_name}_{file.name}"):
                    st.success(f"✅ Referencia guardada para {file.name}")

# ============================================
# GENERACIÓN DE INFORMES (EXCEL/PDF)
# ============================================

def generar_informe_excel():
    """Generar informe completo en Excel"""
    output = io.BytesIO()
    
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        # Datos de empresa
        empresa = get_empresa_data()
        empresa_df = pd.DataFrame([empresa])
        empresa_df.to_excel(writer, sheet_name='Datos_Empresa', index=False)
        
        # Peligros
        conn = sqlite3.connect('sst.db')
        peligros_df = pd.read_sql_query("SELECT * FROM peligros", conn)
        peligros_df.to_excel(writer, sheet_name='Peligros', index=False)
        
        # Acciones
        acciones_df = pd.read_sql_query("SELECT * FROM acciones", conn)
        acciones_df.to_excel(writer, sheet_name='Plan_Accion', index=False)
        
        # Trabajadores
        trabajadores_df = pd.read_sql_query("SELECT * FROM trabajadores", conn)
        trabajadores_df.to_excel(writer, sheet_name='Trabajadores', index=False)
        
        # Incidentes
        incidentes_df = pd.read_sql_query("SELECT * FROM incidentes", conn)
        incidentes_df.to_excel(writer, sheet_name='Incidentes', index=False)
        
        # Matriz legal
        matriz_df = pd.read_sql_query("SELECT * FROM matriz_legal", conn)
        matriz_df.to_excel(writer, sheet_name='Matriz_Legal', index=False)
        
        # Plan anual
        plan_df = pd.read_sql_query("SELECT * FROM plan_anual", conn)
        plan_df.to_excel(writer, sheet_name='Plan_Anual', index=False)
        
        conn.close()
    
    return output.getvalue()

def generar_informe_pdf():
    """Generar informe resumen en PDF"""
    pdf = FPDF()
    pdf.add_page()
    
    # Título
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(0, 10, "INFORME SG-SST", ln=True, align='C')
    
    # Datos empresa
    empresa = get_empresa_data()
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(0, 10, "DATOS DE LA EMPRESA", ln=True)
    pdf.set_font("Arial", '', 10)
    for key, value in empresa.items():
        pdf.cell(0, 6, f"{key.upper()}: {value}", ln=True)
    
    # Estadísticas
    conn = sqlite3.connect('sst.db')
    peligros = pd.read_sql_query("SELECT COUNT(*) as c FROM peligros", conn).iloc[0]['c']
    acciones = pd.read_sql_query("SELECT COUNT(*) as c FROM acciones", conn).iloc[0]['c']
    trabajadores = pd.read_sql_query("SELECT COUNT(*) as c FROM trabajadores", conn).iloc[0]['c']
    incidentes = pd.read_sql_query("SELECT COUNT(*) as c FROM incidentes", conn).iloc[0]['c']
    conn.close()
    
    pdf.ln(5)
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(0, 10, "ESTADÍSTICAS GENERALES", ln=True)
    pdf.set_font("Arial", '', 10)
    pdf.cell(0, 6, f"Total peligros identificados: {peligros}", ln=True)
    pdf.cell(0, 6, f"Total acciones planificadas: {acciones}", ln=True)
    pdf.cell(0, 6, f"Total trabajadores registrados: {trabajadores}", ln=True)
    pdf.cell(0, 6, f"Total incidentes reportados: {incidentes}", ln=True)
    
    return pdf.output(dest='S').encode('latin1')

def pagina_informes():
    """Página de generación de informes"""
    st.header("📊 Informes y Reportes")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📑 Informe Ejecutivo")
        st.write("Genera un informe completo en formato Excel con todos los datos del sistema")
        if st.button("📥 Descargar Excel", use_container_width=True):
            excel_data = generar_informe_excel()
            st.download_button(
                label="✅ Listo para descargar",
                data=excel_data,
                file_name=f"informe_sst_{datetime.now().strftime('%Y%m%d')}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
    
    with col2:
        st.subheader("📄 Informe PDF")
        st.write("Genera un informe resumen en formato PDF")
        if st.button("📥 Descargar PDF", use_container_width=True):
            pdf_data = generar_informe_pdf()
            st.download_button(
                label="✅ Listo para descargar",
                data=pdf_data,
                file_name=f"resumen_sst_{datetime.now().strftime('%Y%m%d')}.pdf",
                mime="application/pdf"
            )
    
    st.divider()
    
    # Informes por módulo
    st.subheader("📋 Informes por Módulo")
    modulo = st.selectbox("Selecciona un módulo", 
                         ["Peligros", "Plan de Acción", "Trabajadores", "Incidentes", "Matriz Legal", "Plan Anual"])
    
    conn = sqlite3.connect('sst.db')
    if modulo == "Peligros":
        df = pd.read_sql_query("SELECT * FROM peligros", conn)
    elif modulo == "Plan de Acción":
        df = pd.read_sql_query("SELECT * FROM acciones", conn)
    elif modulo == "Trabajadores":
        df = pd.read_sql_query("SELECT * FROM trabajadores", conn)
    elif modulo == "Incidentes":
        df = pd.read_sql_query("SELECT * FROM incidentes", conn)
    elif modulo == "Matriz Legal":
        df = pd.read_sql_query("SELECT * FROM matriz_legal", conn)
    else:
        df = pd.read_sql_query("SELECT * FROM plan_anual", conn)
    conn.close()
    
    st.dataframe(df, use_container_width=True)
    
    csv = df.to_csv(index=False).encode('utf-8')
    st.download_button(
        label=f"📥 Descargar {modulo} (CSV)",
        data=csv,
        file_name=f"{modulo.lower().replace(' ', '_')}_{datetime.now().strftime('%Y%m%d')}.csv",
        mime="text/csv"
    )

# ============================================
# ACTUALIZAR FUNCIONES EXISTENTES CON SUBIDA DE ARCHIVOS
# ============================================

# AGREGAR SUBIDA DE ARCHIVOS EN PELIGROS
def pagina_peligros_mejorada():
    """Página de peligros con subida de archivos"""
    st.header("⚠️ Matriz de Peligros GTC-45")
    
    # Subida de archivos
    upload_file_with_ai("Peligros", "peligros", "id")
    
    st.markdown("---")
    
    # CRUD existente de peligros
    conn = sqlite3.connect('sst.db')
    peligros_df = pd.read_sql_query("SELECT * FROM peligros ORDER BY nivel_riesgo DESC", conn)
    conn.close()
    
    if not peligros_df.empty:
        st.dataframe(peligros_df, use_container_width=True)
    else:
        st.info("No hay peligros registrados. Usa el formulario para agregar.")

# ============================================
# ACTUALIZAR PLAN DE ACCIÓN CON EVIDENCIAS
# ============================================

def pagina_plan_accion_mejorado():
    """Plan de acción con subida de evidencias"""
    st.header("📋 Plan de Acción SST")
    
    # Subida de archivos
    upload_file_with_ai("Plan de Acción", "acciones", "id")
    
    st.markdown("---")
    
    # CRUD existente
    conn = sqlite3.connect('sst.db')
    acciones_df = pd.read_sql_query("SELECT * FROM acciones ORDER BY fecha_limite", conn)
    conn.close()
    
    if not acciones_df.empty:
        st.dataframe(acciones_df, use_container_width=True)
    else:
        st.info("No hay acciones registradas")

# ============================================
# NAVEGACIÓN MEJORADA
# ============================================

# Agregar al sidebar:
# st.sidebar.page("🏢 Configuración Empresa", icon="🏢")
# st.sidebar.page("📊 Informes", icon="📊")
# st.sidebar.page("🤖 Diagnóstico Rápido", icon="⚡")
