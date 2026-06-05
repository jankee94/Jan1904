import streamlit as st
from datetime import datetime, timedelta
import sqlite3
import pandas as pd
import requests

st.set_page_config(page_title="SG-SST PHVA", page_icon="🔄", layout="wide")

# ========== ESTILOS CSS PROFESIONAL ==========
st.markdown("""
<style>
    /* Fondo gradiente completo */
    .stApp {
        background: linear-gradient(135deg, #0f0c29 0%, #302b63 50%, #24243e 100%);
        margin: 0;
        padding: 0;
    }
    
    /* Ocultar barra blanca de Streamlit */
    .main > div {
        background: transparent !important;
    }
    
    .stApp > header {
        background: transparent !important;
    }
    
    /* Tarjeta de login transparente */
    .login-card {
        background: rgba(255, 255, 255, 0.08);
        backdrop-filter: blur(12px);
        border-radius: 30px;
        padding: 50px 40px;
        box-shadow: 0 25px 45px rgba(0,0,0,0.3);
        border: 1px solid rgba(255,255,255,0.1);
    }
    
    /* Logo */
    .logo-container {
        text-align: center;
        margin-bottom: 25px;
    }
    
    .logo-img {
        width: 100px;
        margin-bottom: 15px;
    }
    
    /* Títulos */
    .main-title {
        font-size: 36px;
        font-weight: 800;
        background: linear-gradient(135deg, #fff 0%, #a8c0ff 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin: 10px 0 5px 0;
        letter-spacing: 2px;
    }
    
    .slogan {
        color: rgba(255,255,255,0.7);
        font-size: 16px;
        font-style: italic;
        margin-bottom: 30px;
        text-align: center;
    }
    
    .subtitle {
        color: rgba(255,255,255,0.5);
        font-size: 12px;
        text-align: center;
        margin-bottom: 30px;
    }
    
    /* Inputs transparentes */
    .stTextInput > div > div > input {
        background: rgba(255,255,255,0.1) !important;
        border: 1px solid rgba(255,255,255,0.2) !important;
        border-radius: 12px !important;
        color: white !important;
        padding: 12px 15px !important;
    }
    
    .stTextInput > div > div > input::placeholder {
        color: rgba(255,255,255,0.5) !important;
    }
    
    .stTextInput > div > div > input:focus {
        border-color: #667eea !important;
        box-shadow: 0 0 10px rgba(102,126,234,0.3) !important;
    }
    
    /* Labels */
    .stTextInput > label {
        color: rgba(255,255,255,0.8) !important;
        font-weight: 500 !important;
        margin-bottom: 5px !important;
    }
    
    /* Botón */
    .stButton > button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
        color: white !important;
        border: none !important;
        border-radius: 12px !important;
        padding: 12px !important;
        font-weight: bold !important;
        font-size: 16px !important;
        transition: all 0.3s ease !important;
        width: 100% !important;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 10px 25px rgba(102,126,234,0.4);
    }
    
    /* Botón olvidó clave */
    .stButton > button[kind="secondary"] {
        background: transparent !important;
        border: 1px solid rgba(255,255,255,0.3) !important;
    }
    
    /* Footer */
    .developer-footer {
        position: fixed;
        bottom: 0;
        left: 0;
        right: 0;
        text-align: center;
        padding: 15px;
        background: rgba(0,0,0,0.6);
        backdrop-filter: blur(10px);
        color: rgba(255,255,255,0.7);
        font-size: 13px;
        font-weight: 500;
        letter-spacing: 1px;
        z-index: 999;
    }
    
    /* Mensajes de error */
    .stAlert {
        background: rgba(255,0,0,0.2) !important;
        border: 1px solid rgba(255,0,0,0.3) !important;
        border-radius: 12px !important;
        color: #ff6b6b !important;
    }
    
    /* Selector */
    .stSelectbox > div > div {
        background: rgba(255,255,255,0.1) !important;
        border-radius: 12px !important;
        color: white !important;
    }
</style>
""", unsafe_allow_html=True)

# ========== BASE DE DATOS ==========
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

# Usuario admin por defecto (clave: admin123)
cursor.execute("SELECT * FROM usuarios WHERE username = 'admin'")
if not cursor.fetchone():
    cursor.execute("INSERT INTO usuarios (username, password, nombre, rol) VALUES (?, ?, ?, ?)",
                  ('admin', 'admin123', 'Administrador', 'admin'))
    conn.commit()

conn.commit()

# ========== FUNCIONES ==========
def verificar_login(username, password):
    cursor.execute("SELECT * FROM usuarios WHERE username = ? AND password = ? AND activo = 1", (username, password))
    user = cursor.fetchone()
    if user:
        return {"id": user[0], "username": user[1], "nombre": user[3], "rol": user[4]}
    return None

def crear_usuario(username, password, nombre, rol):
    try:
        cursor.execute("INSERT INTO usuarios (username, password, nombre, rol) VALUES (?, ?, ?, ?)",
                      (username, password, nombre, rol))
        conn.commit()
        return True
    except:
        return False

def obtener_usuarios():
    return pd.read_sql_query("SELECT id, username, nombre, rol, activo FROM usuarios", conn)

def actualizar_usuario(id, rol=None, activo=None):
    if rol:
        cursor.execute("UPDATE usuarios SET rol = ? WHERE id = ?", (rol, id))
    if activo is not None:
        cursor.execute("UPDATE usuarios SET activo = ? WHERE id = ?", (activo, id))
    conn.commit()

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

# ========== SESION ==========
if "auth" not in st.session_state:
    st.session_state.auth = False
if "user" not in st.session_state:
    st.session_state.user = None
if "empresa_actual_id" not in st.session_state:
    st.session_state.empresa_actual_id = None
if "empresa_actual" not in st.session_state:
    st.session_state.empresa_actual = None

# ========== LOGIN PROFESIONAL ==========
if not st.session_state.auth:
    col1, col2, col3 = st.columns([1, 2.5, 1])
    with col2:
        st.markdown("""
        <div class="login-card">
            <div class="logo-container">
                <img src="https://cdn-icons-png.flaticon.com/512/2917/2917995.png" class="logo-img">
                <h1 class="main-title">SG-SST PHVA</h1>
                <div class="slogan">"Seguridad y Salud, compromiso de todos"</div>
                <div class="subtitle">Sistema de Gestión PHVA con IA</div>
            </div>
        """, unsafe_allow_html=True)
        
        with st.form("login_form"):
            username = st.text_input("👤 USUARIO", placeholder="Ingrese su usuario")
            password = st.text_input("🔒 CONTRASEÑA", type="password", placeholder="Ingrese su contraseña")
            
            col1, col2 = st.columns(2)
            with col1:
                submitted = st.form_submit_button("🚀 INGRESAR", use_container_width=True)
            with col2:
                forgot = st.form_submit_button("❓ OLVIDÓ SU CLAVE", use_container_width=True)
            
            if submitted:
                user = verificar_login(username, password)
                if user:
                    st.session_state.auth = True
                    st.session_state.user = user
                    st.rerun()
                else:
                    st.error("❌ Usuario o contraseña incorrectos")
            
            if forgot:
                st.info("📧 Contacte al administrador: admin@sgsst.com para recuperar su contraseña")
        
        st.markdown("""
            <div style="text-align: center; margin-top: 25px; padding-top: 20px;">
                <p style="color: rgba(255,255,255,0.4); font-size: 11px;">© 2024 SG-SST PHVA - Todos los derechos reservados</p>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown('<div class="developer-footer">🔄 SG-SST PHVA | DESARROLLADO POR JAN BENITEZ | "Prevenir es vivir"</div>', unsafe_allow_html=True)
    st.stop()

# ========== SIDEBAR ==========
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/2917/2917995.png", width=80)
    st.markdown(f"**👤 {st.session_state.user['nombre']}**")
    st.markdown(f"**Rol:** {st.session_state.user['rol'].upper()}")
    st.markdown("---")
    
    if st.session_state.user['rol'] == 'admin':
        diagnosticos = obtener_diagnosticos()
        if not diagnosticos.empty:
            empresas_opciones = diagnosticos.apply(lambda x: f"{x['id']} - {x['nombre']} ({x['nit'] if x['nit'] else 'Sin NIT'})", axis=1).tolist()
            empresa_seleccionada = st.selectbox("🏢 Seleccionar empresa", ["-- Nueva empresa --"] + empresas_opciones)
            
            if empresa_seleccionada != "-- Nueva empresa --":
                id_empresa = int(empresa_seleccionada.split(" - ")[0])
                if st.session_state.empresa_actual_id != id_empresa:
                    set_empresa_actual(id_empresa)
                    st.rerun()
    
    if st.session_state.empresa_actual:
        st.markdown(f"**🏢 {st.session_state.empresa_actual.get('nombre', '')[:20]}**")
        st.caption(f"📊 {st.session_state.empresa_actual.get('trabajadores', 0)} trabajadores")
    
    st.markdown("---")
    
    if st.session_state.user['rol'] == 'admin':
        menu = st.radio("📋 MENU", [
            "📊 Dashboard",
            "🤖 Diagnóstico IA",
            "⚠️ Peligros",
            "✅ Plan de Acción",
            "👥 Trabajadores",
            "📝 Incidentes",
            "💬 Chat IA",
            "⚙️ Gestionar Usuarios"
        ])
    else:
        menu = st.radio("📋 MENU", [
            "📊 Dashboard",
            "📝 Reportar Incidente",
            "💬 Chat IA"
        ])
    
    st.markdown("---")
    if st.button("🚪 Cerrar Sesión", use_container_width=True):
        st.session_state.auth = False
        st.session_state.user = None
        st.rerun()

# ========== DASHBOARD ==========
if menu == "📊 Dashboard":
    st.title("📊 Dashboard SST")
    
    if st.session_state.empresa_actual:
        emp = st.session_state.empresa_actual
        st.success(f"🏢 **{emp.get('nombre', '')}** | NIT: {emp.get('nit', 'No registrado')} | 👥 {emp.get('trabajadores', 0)} trabajadores")
        
        empresa_id = st.session_state.empresa_actual_id
        df_peligros = pd.read_sql_query("SELECT * FROM peligros WHERE empresa_id = ?", conn, params=(empresa_id,))
        df_acciones = pd.read_sql_query("SELECT * FROM acciones WHERE empresa_id = ?", conn, params=(empresa_id,))
        df_trabajadores = pd.read_sql_query("SELECT * FROM trabajadores WHERE empresa_id = ?", conn, params=(empresa_id,))
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("⚠️ Peligros", len(df_peligros))
        with col2:
            completadas = len(df_acciones[df_acciones['estado'] == 'Completada']) if not df_acciones.empty else 0
            st.metric("✅ Acciones", f"{completadas}/{len(df_acciones)}")
        with col3:
            st.metric("👥 Trabajadores", len(df_trabajadores))
        with col4:
            st.metric("📈 Progreso", "60%")
    else:
        st.warning("⚠️ Seleccione o cree una empresa en 'Diagnóstico IA'")

# ========== DIAGNÓSTICO IA ==========
elif menu == "🤖 Diagnóstico IA":
    st.title("🤖 DIAGNÓSTICO IA")
    
    with st.form("form_diagnostico"):
        st.subheader("📝 Datos de la empresa")
        col1, col2 = st.columns(2)
        with col1:
            nit = st.text_input("NIT", placeholder="900.123.456-7")
            nombre = st.text_input("Nombre de la empresa *", placeholder="Mi Empresa S.A.S.")
        with col2:
            trabajadores = st.number_input("Número de trabajadores *", min_value=1, value=10)
            arl = st.selectbox("ARL *", ["Positiva", "Sura", "Colpatria", "Bolivar"])
        
        if st.form_submit_button("🚀 GENERAR DIAGNÓSTICO", use_container_width=True):
            if nombre:
                with st.spinner("🤖 IA generando diagnóstico..."):
                    prompt = f"Diagnóstico SST para {nombre} con {trabajadores} trabajadores, ARL {arl}. Máximo 300 palabras."
                    respuesta = call_ia(prompt)
                    if respuesta and "Error" not in respuesta:
                        empresa_id = guardar_diagnostico(nit, nombre, trabajadores, arl, respuesta)
                        set_empresa_actual(empresa_id)
                        
                        peligros_base = [("Ergonómico", f"Posturas en {nombre}", 2, 2), ("Seguridad", "Caídas", 2, 2)]
                        for p in peligros_base:
                            cursor.execute("INSERT INTO peligros (empresa_id, tipo, descripcion, probabilidad, severidad) VALUES (?, ?, ?, ?, ?)",
                                          (empresa_id, p[0], p[1], p[2], p[3]))
                        fecha = datetime.now()
                        cursor.execute("INSERT INTO acciones (empresa_id, descripcion, responsable, fecha) VALUES (?, ?, ?, ?)",
                                      (empresa_id, f"Matriz de riesgos para {nombre}", "SST", (fecha + timedelta(days=30)).strftime("%Y-%m-%d")))
                        conn.commit()
                        st.balloons()
                        st.success("✅ Diagnóstico generado")
                        st.rerun()
                    else:
                        st.error("Error con IA")
            else:
                st.error("Nombre obligatorio")
    
    st.markdown("---")
    st.subheader("📋 Historial")
    df = obtener_diagnosticos()
    for _, row in df.iterrows():
        col1, col2 = st.columns([3,1])
        with col1:
            st.write(f"**{row['nombre']}**")
        with col2:
            if st.button("Seleccionar", key=f"sel_{row['id']}"):
                set_empresa_actual(row['id'])
                st.rerun()
        st.markdown("---")

# ========== GESTIONAR USUARIOS ==========
elif menu == "⚙️ Gestionar Usuarios":
    st.title("⚙️ Gestión de Usuarios")
    
    tab1, tab2 = st.tabs(["📋 Usuarios", "➕ Crear"])
    
    with tab1:
        df = obtener_usuarios()
        st.dataframe(df)
    
    with tab2:
        with st.form("form_usuario"):
            username = st.text_input("Usuario")
            password = st.text_input("Contraseña", type="password")
            nombre = st.text_input("Nombre")
            rol = st.selectbox("Rol", ["trabajador", "supervisor", "responsable_sst", "auditor", "admin"])
            if st.form_submit_button("Crear"):
                if crear_usuario(username, password, nombre, rol):
                    st.success("Usuario creado")

# ========== REPORTAR INCIDENTE ==========
elif menu == "📝 Reportar Incidente":
    st.title("📝 Reportar Incidente")
    
    with st.form("form_incidente"):
        desc = st.text_area("Descripción")
        fecha = st.date_input("Fecha", datetime.now())
        gravedad = st.selectbox("Gravedad", ["Leve", "Moderada", "Grave"])
        if st.form_submit_button("Reportar"):
            if desc and st.session_state.empresa_actual_id:
                cursor.execute("INSERT INTO incidentes (empresa_id, descripcion, fecha, gravedad) VALUES (?, ?, ?, ?)",
                              (st.session_state.empresa_actual_id, desc, fecha.strftime("%Y-%m-%d"), gravedad))
                conn.commit()
                st.success("Reportado")

# ========== PELIGROS ==========
elif menu == "⚠️ Peligros":
    st.title("⚠️ Peligros")
    
    if st.session_state.empresa_actual_id:
        df = pd.read_sql_query("SELECT * FROM peligros WHERE empresa_id = ?", conn, params=(st.session_state.empresa_actual_id,))
        st.dataframe(df)
        
        with st.form("form"):
            tipo = st.selectbox("Tipo", ["Físico", "Químico", "Biológico", "Ergonómico", "Psicosocial", "Seguridad"])
            desc = st.text_area("Descripción")
            prob = st.slider("Probabilidad", 1, 4, 2)
            sev = st.slider("Severidad", 1, 3, 2)
            if st.form_submit_button("Guardar"):
                cursor.execute("INSERT INTO peligros (empresa_id, tipo, descripcion, probabilidad, severidad) VALUES (?, ?, ?, ?, ?)",
                              (st.session_state.empresa_actual_id, tipo, desc, prob, sev))
                conn.commit()
                st.rerun()

# ========== PLAN DE ACCIÓN ==========
elif menu == "✅ Plan de Acción":
    st.title("✅ Plan de Acción")
    
    if st.session_state.empresa_actual_id:
        df = pd.read_sql_query("SELECT * FROM acciones WHERE empresa_id = ?", conn, params=(st.session_state.empresa_actual_id,))
        for _, row in df.iterrows():
            col1, col2 = st.columns([3,1])
            with col1:
                st.write(f"**{row['descripcion']}** - {row['responsable']}")
            with col2:
                nuevo = st.selectbox("Estado", ["Pendiente", "Completada"], key=row['id'])
                if nuevo != row['estado']:
                    cursor.execute("UPDATE acciones SET estado = ? WHERE id = ?", (nuevo, row['id']))
                    conn.commit()
                    st.rerun()
        
        with st.form("form"):
            desc = st.text_area("Descripción")
            resp = st.text_input("Responsable")
            if st.form_submit_button("Guardar"):
                cursor.execute("INSERT INTO acciones (empresa_id, descripcion, responsable, fecha) VALUES (?, ?, ?, ?)",
                              (st.session_state.empresa_actual_id, desc, resp, datetime.now().strftime("%Y-%m-%d")))
                conn.commit()
                st.rerun()

# ========== TRABAJADORES ==========
elif menu == "👥 Trabajadores":
    st.title("👥 Trabajadores")
    
    if st.session_state.empresa_actual_id:
        df = pd.read_sql_query("SELECT * FROM trabajadores WHERE empresa_id = ?", conn, params=(st.session_state.empresa_actual_id,))
        st.dataframe(df)
        
        with st.form("form"):
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

# ========== FOOTER ==========
st.markdown('<div class="developer-footer">🔄 SG-SST PHVA | DESARROLLADO POR JAN BENITEZ</div>', unsafe_allow_html=True)
