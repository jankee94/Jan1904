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
    header[data-testid="stHeader"] {
        display: none;
    }
    footer {
        display: none !important;
    }
    .stButton > button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
        border: none !important;
        border-radius: 12px !important;
        font-weight: 600 !important;
    }
    .stSelectbox, .stTextInput, .stNumberInput {
        margin-bottom: 10px;
    }
    /* Sidebar más elegante */
    [data-testid="stSidebar"] {
        background: rgba(20, 20, 40, 0.5);
        backdrop-filter: blur(10px);
    }
</style>
""", unsafe_allow_html=True)

# ========== BASE DE DATOS ==========
conn = sqlite3.connect("sst.db", check_same_thread=False)
cursor = conn.cursor()

# Crear todas las tablas
cursor.execute('''CREATE TABLE IF NOT EXISTS usuarios (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE,
    password TEXT,
    nombre TEXT,
    rol TEXT DEFAULT 'trabajador'
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

# Usuario admin
cursor.execute("SELECT * FROM usuarios WHERE username='admin'")
if not cursor.fetchone():
    cursor.execute("INSERT INTO usuarios (username, password, nombre, rol) VALUES (?,?,?,?)",
                  ('admin', 'admin123', 'Administrador', 'admin'))
    conn.commit()

# Insertar datos demo
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

def call_ia(prompt):
    try:
        url = "https://generativelanguage.googleapis.com/v1/models/gemini-pro:generateContent"
        headers = {"Content-Type": "application/json", "x-goog-api-key": "AIzaSyD3QhEohGJeYhVtM7JmBZ2nXvZJFxJZv3U"}
        data = {"contents": [{"parts": [{"text": prompt}]}]}
        r = requests.post(url, json=data, headers=headers, timeout=30)
        if r.status_code == 200:
            return r.json()["candidates"][0]["content"]["parts"][0]["text"]
    except:
        pass
    return "⚠️ IA no disponible. Usando modo offline."

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
            if st.form_submit_button("🚀 INGRESAR", use_container_width=True):
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

# ========== SIDEBAR CON MODULOS FIJOS ==========
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/2917/2917995.png", width=45)
    st.markdown(f"**👤 {st.session_state.user['nombre']}**")
    st.markdown(f"**Rol:** {st.session_state.user['rol'].upper()}")
    st.markdown("---")
    
    # Módulos fijos visibles siempre
    st.markdown("### 📋 MÓDULOS")
    
    menu = st.radio(
        "Seleccione un módulo:",
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
    if st.button("🚪 Cerrar Sesión", use_container_width=True):
        st.session_state.auth = False
        st.rerun()

# ========== DASHBOARD ==========
if menu == "📊 Dashboard":
    st.title("📊 DASHBOARD SST")
    
    df_peligros = pd.read_sql_query("SELECT * FROM peligros", conn)
    df_acciones = pd.read_sql_query("SELECT * FROM acciones", conn)
    df_trabajadores = pd.read_sql_query("SELECT * FROM trabajadores", conn)
    df_incidentes = pd.read_sql_query("SELECT * FROM incidentes", conn)
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("⚠️ Peligros", len(df_peligros))
    with col2:
        completadas = len(df_acciones[df_acciones['estado'] == 'Completada']) if not df_acciones.empty else 0
        st.metric("✅ Acciones", f"{completadas}/{len(df_acciones)}")
    with col3:
        st.metric("👥 Trabajadores", len(df_trabajadores))
    with col4:
        st.metric("📝 Incidentes", len(df_incidentes))
    
    st.markdown("---")
    
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("⚠️ Peligros registrados")
        if not df_peligros.empty:
            st.dataframe(df_peligros[['tipo', 'descripcion', 'nivel']], use_container_width=True)
        else:
            st.info("No hay peligros")
    
    with col2:
        st.subheader("✅ Acciones pendientes")
        if not df_acciones.empty:
            pendientes = df_acciones[df_acciones['estado'] != 'Completada']
            st.dataframe(pendientes[['descripcion', 'responsable', 'estado']], use_container_width=True)
        else:
            st.info("No hay acciones")

# ========== DIAGNÓSTICO IA ==========
elif menu == "🤖 Diagnóstico IA":
    st.title("🤖 DIAGNÓSTICO IA")
    
    with st.form("form_diagnostico"):
        nombre = st.text_input("Nombre de la empresa")
        trabajadores = st.number_input("Número de trabajadores", min_value=1, value=10)
        arl = st.selectbox("ARL", ["Positiva", "Sura", "Colpatria", "Bolivar"])
        
        if st.form_submit_button("🚀 GENERAR DIAGNÓSTICO", use_container_width=True):
            if nombre:
                with st.spinner("🤖 IA generando diagnóstico..."):
                    prompt = f"Realiza un diagnóstico SST para la empresa {nombre} con {trabajadores} trabajadores y ARL {arl}. Incluye recomendaciones iniciales."
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
            
            # Botón para eliminar
            with st.expander("🗑️ Eliminar peligro"):
                id_eliminar = st.number_input("ID del peligro a eliminar", min_value=1, step=1)
                if st.button("Eliminar"):
                    cursor.execute("DELETE FROM peligros WHERE id = ?", (id_eliminar,))
                    conn.commit()
                    st.success("✅ Eliminado")
                    st.rerun()
        else:
            st.info("No hay peligros registrados")
    
    with tab2:
        with st.form("form_peligro"):
            tipo = st.selectbox("Tipo de Peligro", ["Físico", "Químico", "Biológico", "Ergonómico", "Psicosocial", "Seguridad"])
            descripcion = st.text_area("Descripción detallada")
            probabilidad = st.slider("Probabilidad (1-4)", 1, 4, 2, help="1:Baja, 2:Media, 3:Alta, 4:Muy Alta")
            severidad = st.slider("Severidad (1-3)", 1, 3, 2, help="1:Ligero, 2:Dañino, 3:Extremo")
            
            # Calcular nivel de riesgo
            matriz = {(1,1):"III",(1,2):"II",(1,3):"I",(2,1):"III",(2,2):"II",(2,3):"I",
                      (3,1):"II",(3,2):"I",(3,3):"I",(4,1):"II",(4,2):"I",(4,3):"I"}
            nivel = matriz.get((probabilidad, severidad), "III")
            
            if nivel == "I":
                st.error("🔴 NIVEL I - RIESGO ALTO - Requiere intervención inmediata")
            elif nivel == "II":
                st.warning("🟠 NIVEL II - RIESGO MEDIO - Requiere seguimiento")
            else:
                st.info("🟡 NIVEL III - RIESGO BAJO - Monitorear")
            
            if st.form_submit_button("💾 Guardar Peligro", use_container_width=True):
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
    st.title("✅ PLAN DE ACCIÓN - FASE 4")
    
    tab1, tab2 = st.tabs(["📋 Seguimiento", "➕ Nueva Acción"])
    
    with tab1:
        df = pd.read_sql_query("SELECT * FROM acciones", conn)
        if not df.empty:
            for _, row in df.iterrows():
                with st.container():
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
                        nuevo_estado = st.selectbox(
                            "Estado", 
                            ["Pendiente", "En progreso", "Completada"], 
                            index=["Pendiente", "En progreso", "Completada"].index(row['estado']),
                            key=f"estado_{row['id']}"
                        )
                        if nuevo_estado != row['estado']:
                            cursor.execute("UPDATE acciones SET estado = ? WHERE id = ?", (nuevo_estado, row['id']))
                            conn.commit()
                            st.rerun()
                    st.markdown("---")
        else:
            st.info("📭 No hay acciones registradas")
    
    with tab2:
        with st.form("form_accion"):
            descripcion = st.text_area("Descripción de la acción")
            responsable = st.text_input("Responsable")
            fecha_limite = st.date_input("Fecha límite", datetime.now())
            prioridad = st.selectbox("Prioridad", ["Alta", "Media", "Baja"])
            
            if st.form_submit_button("💾 Guardar Acción", use_container_width=True):
                if descripcion and responsable:
                    cursor.execute('''INSERT INTO acciones (empresa_id, descripcion, responsable, fecha, estado) 
                                      VALUES (?, ?, ?, ?, ?)''',
                                  (1, descripcion, responsable, fecha_limite.strftime("%Y-%m-%d"), "Pendiente"))
                    conn.commit()
                    st.success("✅ Acción guardada")
                    st.rerun()
                else:
                    st.error("Complete todos los campos")

# ========== TRABAJADORES ==========
elif menu == "👥 Trabajadores":
    st.title("👥 GESTIÓN DE TRABAJADORES")
    
    tab1, tab2 = st.tabs(["📋 Lista de Trabajadores", "➕ Nuevo Trabajador"])
    
    with tab1:
        df = pd.read_sql_query("SELECT * FROM trabajadores", conn)
        if not df.empty:
            st.dataframe(df, use_container_width=True)
        else:
            st.info("📭 No hay trabajadores registrados")
    
    with tab2:
        with st.form("form_trabajador"):
            col1, col2 = st.columns(2)
            with col1:
                nombre = st.text_input("Nombre completo")
                cedula = st.text_input("Cédula")
            with col2:
                cargo = st.text_input("Cargo")
                area = st.text_input("Área/Dependencia")
            
            if st.form_submit_button("💾 Registrar Trabajador", use_container_width=True):
                if nombre:
                    cursor.execute('''INSERT INTO trabajadores (empresa_id, nombre, cedula, cargo) 
                                      VALUES (?, ?, ?, ?)''', (1, nombre, cedula, cargo))
                    conn.commit()
                    st.success("✅ Trabajador registrado")
                    st.rerun()
                else:
                    st.error("Ingrese el nombre del trabajador")

# ========== INCIDENTES ==========
elif menu == "📝 Incidentes":
    st.title("📝 REGISTRO DE INCIDENTES")
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        with st.form("form_incidente"):
            st.subheader("➕ Nuevo Incidente")
            descripcion = st.text_area("Descripción del incidente")
            fecha = st.date_input("Fecha del incidente", datetime.now())
            gravedad = st.selectbox("Gravedad", ["Leve", "Moderada", "Grave", "Mortal"])
            tipo = st.selectbox("Tipo", ["Accidente", "Incidente", "Enfermedad Laboral", "Casi accidente"])
            
            if st.form_submit_button("📝 Reportar Incidente", use_container_width=True):
                if descripcion:
                    cursor.execute('''INSERT INTO incidentes (empresa_id, descripcion, fecha, gravedad) 
                                      VALUES (?, ?, ?, ?)''', (1, descripcion, fecha.strftime("%Y-%m-%d"), gravedad))
                    conn.commit()
                    st.success("✅ Incidente reportado")
                    st.rerun()
                else:
                    st.error("Ingrese una descripción")
    
    with col2:
        st.subheader("📊 Estadísticas")
        df = pd.read_sql_query("SELECT * FROM incidentes", conn)
        if not df.empty:
            st.metric("Total Incidentes", len(df))
            st.metric("Graves", len(df[df['gravedad'] == 'Grave']) if 'gravedad' in df.columns else 0)
        else:
            st.info("Sin datos")
    
    st.markdown("---")
    st.subheader("📋 Historial de Incidentes")
    df = pd.read_sql_query("SELECT * FROM incidentes ORDER BY fecha DESC", conn)
    if not df.empty:
        st.dataframe(df, use_container_width=True)

# ========== CHAT IA ==========
elif menu == "💬 Chat IA":
    st.title("💬 CHAT IA - Asistente SST")
    
    if "messages" not in st.session_state:
        st.session_state.messages = [
            {"role": "assistant", "content": "¡Hola! Soy tu asistente SST. ¿En qué puedo ayudarte hoy?"}
        ]
    
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.write(msg["content"])
    
    if prompt := st.chat_input("Pregunta sobre SST, peligros, normativas..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.write(prompt)
        
        with st.chat_message("assistant"):
            with st.spinner("🤖 Analizando tu consulta..."):
                respuesta = call_ia(prompt)
                st.write(respuesta)
                st.session_state.messages.append({"role": "assistant", "content": respuesta})

# Footer
st.markdown("---")
st.markdown("<p style='text-align:center; font-size:11px; color:gray'>🔄 SG-SST PHVA | Sistema de Gestión PHVA con IA | Desarrollado por JAN BENITEZ</p>", unsafe_allow_html=True)
