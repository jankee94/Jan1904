import streamlit as st
import sqlite3
import pandas as pd
import requests
from datetime import datetime

st.set_page_config(page_title="SG-SST PHVA", page_icon="🔄", layout="wide")

# CSS profesional
st.markdown("""
<style>
    .stApp {
        background: linear-gradient(135deg, #0f0c29 0%, #302b63 50%, #24243e 100%);
    }
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
    cursor.execute("INSERT INTO peligros (empresa_id, tipo, descripcion, probabilidad, severidad, nivel) VALUES (1, 'Físico', 'Ruido excesivo en planta', 2, 2, 'II')")
    cursor.execute("INSERT INTO peligros (empresa_id, tipo, descripcion, probabilidad, severidad, nivel) VALUES (1, 'Ergonómico', 'Posturas inadecuadas', 3, 2, 'II')")
    cursor.execute("INSERT INTO acciones (empresa_id, descripcion, responsable, fecha, estado) VALUES (1, 'Realizar matriz de riesgos', 'Coordinador SST', '2024-12-31', 'Pendiente')")
    cursor.execute("INSERT INTO acciones (empresa_id, descripcion, responsable, fecha, estado) VALUES (1, 'Capacitación en prevención', 'SST', '2024-11-30', 'En progreso')")
    cursor.execute("INSERT INTO trabajadores (empresa_id, nombre, cedula, cargo) VALUES (1, 'Juan Pérez', '12345678', 'Operario')")
    cursor.execute("INSERT INTO trabajadores (empresa_id, nombre, cedula, cargo) VALUES (1, 'María Gómez', '87654321', 'Supervisora')")
    conn.commit()

conn.commit()

def verificar_login(username, password):
    cursor.execute("SELECT * FROM usuarios WHERE username=? AND password=?", (username, password))
    user = cursor.fetchone()
    if user:
        return {"id": user[0], "username": user[1], "nombre": user[3], "rol": user[4]}
    return None

# ========== IA CORREGIDA ==========
def call_ia(prompt):
    # Intentar obtener API key de secrets primero
    api_key = st.secrets.get("GEMINI_API_KEY", "AIzaSyD3QhEohGJeYhVtM7JmBZ2nXvZJFxJZv3U")
    
    try:
        url = "https://generativelanguage.googleapis.com/v1/models/gemini-pro:generateContent"
        headers = {"Content-Type": "application/json", "x-goog-api-key": api_key}
        data = {"contents": [{"parts": [{"text": prompt}]}]}
        response = requests.post(url, json=data, headers=headers, timeout=30)
        
        if response.status_code == 200:
            result = response.json()
            return result["candidates"][0]["content"]["parts"][0]["text"]
        else:
            return f"⚠️ Error {response.status_code}: No se pudo conectar con la IA. Verifica la API key."
    except Exception as e:
        return f"⚠️ Error de conexión: {str(e)}. Verifica tu conexión a internet."

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
        [
            "📊 Dashboard",
            "🤖 Diagnóstico IA",
            "⚠️ Peligros",
            "✅ Plan de Acción",
            "👥 Trabajadores",
            "📝 Incidentes",
            "💬 Chat IA"
        ],
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
    
    st.markdown("---")
    st.subheader("⚠️ Últimos peligros registrados")
    if not df_peligros.empty:
        st.dataframe(df_peligros[['tipo', 'descripcion', 'nivel']], use_container_width=True)

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
                    prompt = f"Realiza un diagnóstico SST para la empresa {nombre} con {trabajadores} trabajadores y ARL {arl}. Incluye 5 recomendaciones iniciales importantes."
                    respuesta = call_ia(prompt)
                    
                    fecha = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    cursor.execute('''INSERT INTO empresa (nombre, trabajadores, arl, diagnostico, fecha) 
                                      VALUES (?, ?, ?, ?, ?)''', (nombre, trabajadores, arl, respuesta, fecha))
                    conn.commit()
                    st.session_state.empresa_actual_id = cursor.lastrowid
                    
                    st.success("✅ Diagnóstico generado exitosamente")
                    st.markdown(respuesta)
            else:
                st.error("Ingrese el nombre de la empresa")
    
    st.markdown("---")
    st.subheader("📋 Diagnósticos anteriores")
    df = pd.read_sql_query("SELECT id, nombre, trabajadores, arl, fecha FROM empresa ORDER BY id DESC", conn)
    if not df.empty:
        st.dataframe(df, use_container_width=True)

# ========== PELIGROS ==========
elif menu == "⚠️ Peligros":
    st.title("⚠️ PELIGROS - FASE 2 GTC-45")
    
    tab1, tab2 = st.tabs(["📋 Lista de Peligros", "➕ Agregar Peligro"])
    
    with tab1:
        df = pd.read_sql_query("SELECT * FROM peligros", conn)
        if not df.empty:
            st.dataframe(df, use_container_width=True)
        else:
            st.info("No hay peligros registrados")
    
    with tab2:
        with st.form("form_peligro"):
            tipo = st.selectbox("Tipo de Peligro", ["Físico", "Químico", "Biológico", "Ergonómico", "Psicosocial", "Seguridad"])
            descripcion = st.text_area("Descripción detallada")
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
            
            if st.form_submit_button("💾 Guardar Peligro", width="stretch"):
                if descripcion:
                    cursor.execute('''INSERT INTO peligros (empresa_id, tipo, descripcion, probabilidad, severidad, nivel) 
                                      VALUES (?, ?, ?, ?, ?, ?)''',
                                  (1, tipo, descripcion, probabilidad, severidad, nivel))
                    conn.commit()
                    st.success("✅ Peligro guardado")
                    st.rerun()
                else:
                    st.error("Ingrese una descripción")

# ========== PLAN DE ACCIÓN ==========
elif menu == "✅ Plan de Acción":
    st.title("✅ PLAN DE ACCIÓN")
    
    tab1, tab2 = st.tabs(["📋 Seguimiento", "➕ Nueva Acción"])
    
    with tab1:
        df = pd.read_sql_query("SELECT * FROM acciones", conn)
        if not df.empty:
            for _, row in df.iterrows():
                col1, col2 = st.columns([3, 1])
                with col1:
                    st.markdown(f"**📌 {row['descripcion']}**")
                    st.caption(f"👤 {row['responsable']} | 📅 {row['fecha']}")
                    if row['estado'] == "Completada":
                        st.success("✅ Completada")
                    elif row['estado'] == "En progreso":
                        st.warning("⏳ En progreso")
                    else:
                        st.info("📋 Pendiente")
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
            st.info("No hay acciones registradas")
    
    with tab2:
        with st.form("form_accion"):
            descripcion = st.text_area("Descripción de la acción")
            responsable = st.text_input("Responsable")
            fecha_limite = st.date_input("Fecha límite", datetime.now())
            if st.form_submit_button("💾 Guardar Acción", width="stretch"):
                if descripcion and responsable:
                    cursor.execute('''INSERT INTO acciones (empresa_id, descripcion, responsable, fecha, estado) 
                                      VALUES (?, ?, ?, ?, ?)''',
                                  (1, descripcion, responsable, fecha_limite.strftime("%Y-%m-%d"), "Pendiente"))
                    conn.commit()
                    st.success("✅ Acción guardada")
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
            st.info("No hay trabajadores registrados")
    
    with tab2:
        with st.form("form_trabajador"):
            nombre = st.text_input("Nombre completo")
            cedula = st.text_input("Cédula")
            cargo = st.text_input("Cargo")
            if st.form_submit_button("Registrar", width="stretch"):
                if nombre:
                    cursor.execute('''INSERT INTO trabajadores (empresa_id, nombre, cedula, cargo) 
                                      VALUES (?, ?, ?, ?)''', (1, nombre, cedula, cargo))
                    conn.commit()
                    st.success("✅ Registrado")
                    st.rerun()

# ========== INCIDENTES ==========
elif menu == "📝 Incidentes":
    st.title("📝 INCIDENTES")
    
    with st.form("form_incidente"):
        descripcion = st.text_area("Descripción del incidente")
        fecha = st.date_input("Fecha", datetime.now())
        gravedad = st.selectbox("Gravedad", ["Leve", "Moderada", "Grave", "Mortal"])
        if st.form_submit_button("Reportar", width="stretch"):
            if descripcion:
                cursor.execute('''INSERT INTO incidentes (empresa_id, descripcion, fecha, gravedad) 
                                  VALUES (?, ?, ?, ?)''', (1, descripcion, fecha.strftime("%Y-%m-%d"), gravedad))
                conn.commit()
                st.success("✅ Reportado")
                st.rerun()
    
    st.markdown("---")
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
                respuesta = call_ia(prompt)
                st.write(respuesta)
                st.session_state.messages.append({"role": "assistant", "content": respuesta})

st.markdown("---")
st.markdown("<p style='text-align:center; font-size:11px; color:gray'>🔄 SG-SST PHVA | Desarrollado por JAN BENITEZ</p>", unsafe_allow_html=True)
