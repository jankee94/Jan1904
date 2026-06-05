import streamlit as st
from datetime import datetime, timedelta
import sqlite3
import pandas as pd
import requests

st.set_page_config(page_title="SG-SST PHVA", page_icon="🔄", layout="wide")

# ========== ESTILOS CSS PROFESIONAL ==========
st.markdown("""
<style>
    /* Fondo gradiente corporativo */
    .stApp {
        background: linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%);
    }
    
    /* Tarjeta de login */
    .login-card {
        background: rgba(255, 255, 255, 0.95);
        border-radius: 20px;
        padding: 40px;
        box-shadow: 0 20px 60px rgba(0,0,0,0.3);
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255,255,255,0.2);
    }
    
    /* Título principal */
    .main-title {
        text-align: center;
        font-size: 42px;
        font-weight: 800;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 10px;
    }
    
    /* Subtítulo */
    .subtitle {
        text-align: center;
        color: #666;
        font-size: 16px;
        margin-bottom: 30px;
    }
    
    /* Logo */
    .logo-container {
        text-align: center;
        margin-bottom: 20px;
    }
    
    /* Footer desarrollador */
    .developer-footer {
        position: fixed;
        bottom: 0;
        left: 0;
        right: 0;
        text-align: center;
        padding: 15px;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        font-size: 16px;
        font-weight: bold;
        letter-spacing: 2px;
        z-index: 999;
    }
    
    /* Botón personalizado */
    .stButton > button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        border-radius: 10px;
        padding: 12px;
        font-weight: bold;
        font-size: 16px;
        transition: all 0.3s ease;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 5px 20px rgba(102, 126, 234, 0.4);
    }
    
    /* Input fields */
    .stTextInput > div > div > input {
        border-radius: 10px;
        border: 1px solid #ddd;
        padding: 10px 15px;
    }
    
    /* Sidebar */
    .css-1d391kg {
        background: rgba(255,255,255,0.95);
    }
    
    /* Cards en dashboard */
    .metric-card {
        background: white;
        border-radius: 15px;
        padding: 20px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
    }
</style>
""", unsafe_allow_html=True)

# ========== BASE DE DATOS ==========
conn = sqlite3.connect("sst.db", check_same_thread=False)
cursor = conn.cursor()

cursor.execute('''
    CREATE TABLE IF NOT EXISTS empresa (
        id INTEGER PRIMARY KEY DEFAULT 1,
        nombre TEXT,
        trabajadores INTEGER,
        arl TEXT,
        diagnostico TEXT
    )
''')

cursor.execute('''
    CREATE TABLE IF NOT EXISTS peligros (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        tipo TEXT,
        descripcion TEXT,
        probabilidad INTEGER,
        severidad INTEGER,
        nivel TEXT
    )
''')

cursor.execute('''
    CREATE TABLE IF NOT EXISTS acciones (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        descripcion TEXT,
        responsable TEXT,
        fecha TEXT,
        estado TEXT
    )
''')

cursor.execute('''
    CREATE TABLE IF NOT EXISTS trabajadores (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nombre TEXT,
        cedula TEXT,
        cargo TEXT
    )
''')

cursor.execute('''
    CREATE TABLE IF NOT EXISTS incidentes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        descripcion TEXT,
        fecha TEXT,
        gravedad TEXT
    )
''')

conn.commit()

def guardar_empresa(nombre, trabajadores, arl, diagnostico):
    cursor.execute("DELETE FROM empresa")
    cursor.execute("INSERT INTO empresa (nombre, trabajadores, arl, diagnostico) VALUES (?, ?, ?, ?)",
                  (nombre, trabajadores, arl, diagnostico))
    conn.commit()

def obtener_empresa():
    df = pd.read_sql_query("SELECT * FROM empresa", conn)
    return df.iloc[0].to_dict() if not df.empty else None

def guardar_peligro(tipo, desc, prob, sev):
    matriz = {(1,1):"III",(1,2):"II",(1,3):"I",(2,1):"III",(2,2):"II",(2,3):"I",
              (3,1):"II",(3,2):"I",(3,3):"I",(4,1):"II",(4,2):"I",(4,3):"I"}
    nivel = matriz.get((prob, sev), "III")
    cursor.execute("INSERT INTO peligros (tipo, descripcion, probabilidad, severidad, nivel) VALUES (?, ?, ?, ?, ?)",
                  (tipo, desc, prob, sev, nivel))
    conn.commit()

def obtener_peligros():
    return pd.read_sql_query("SELECT * FROM peligros", conn)

def eliminar_peligro(id):
    cursor.execute("DELETE FROM peligros WHERE id = ?", (id,))
    conn.commit()

def guardar_accion(desc, responsable, fecha):
    cursor.execute("INSERT INTO acciones (descripcion, responsable, fecha, estado) VALUES (?, ?, ?, 'Pendiente')",
                  (desc, responsable, fecha))
    conn.commit()

def obtener_acciones():
    return pd.read_sql_query("SELECT * FROM acciones", conn)

def actualizar_estado(id, estado):
    cursor.execute("UPDATE acciones SET estado = ? WHERE id = ?", (estado, id))
    conn.commit()

def guardar_trabajador(nombre, cedula, cargo):
    cursor.execute("INSERT INTO trabajadores (nombre, cedula, cargo) VALUES (?, ?, ?)", (nombre, cedula, cargo))
    conn.commit()

def obtener_trabajadores():
    return pd.read_sql_query("SELECT * FROM trabajadores", conn)

def guardar_incidente(desc, fecha, gravedad):
    cursor.execute("INSERT INTO incidentes (descripcion, fecha, gravedad) VALUES (?, ?, ?)", (desc, fecha, gravedad))
    conn.commit()

def obtener_incidentes():
    return pd.read_sql_query("SELECT * FROM incidentes", conn)

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
    return "Error al conectar con IA. Verifica tu conexión."

# ========== SESION ==========
if "auth" not in st.session_state:
    st.session_state.auth = False
if "proceso_iniciado" not in st.session_state:
    st.session_state.proceso_iniciado = False

# ========== LOGIN PROFESIONAL ==========
if not st.session_state.auth:
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown("""
        <div class="login-card">
            <div class="logo-container">
                <h1 class="main-title">🔄 SG-SST PHVA</h1>
                <p class="subtitle">Sistema de Gestión de Seguridad y Salud en el Trabajo</p>
            </div>
        """, unsafe_allow_html=True)
        
        with st.form("login_form"):
            st.markdown("### 🔐 Acceso al Sistema")
            user = st.text_input("👤 Usuario", placeholder="admin", key="login_user")
            pwd = st.text_input("🔒 Contraseña", type="password", placeholder="••••••", key="login_pwd")
            
            col1, col2, col3 = st.columns([1, 2, 1])
            with col2:
                submitted = st.form_submit_button("🚀 INGRESAR AL SISTEMA", use_container_width=True)
            
            if submitted:
                if user == "admin" and pwd == "sst2024":
                    st.session_state.auth = True
                    st.rerun()
                else:
                    st.error("❌ Credenciales incorrectas. Use: admin / sst2024")
        
        st.markdown("""
            <div style="text-align: center; margin-top: 30px; padding-top: 20px; border-top: 1px solid #eee;">
                <p style="color: #666; font-size: 12px;">© 2024 - Todos los derechos reservados</p>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    # Footer visible en login
    st.markdown("""
    <div class="developer-footer">
        🔄 SG-SST PHVA | DESARROLLADO POR JAN BENITEZ | IA Protagonista | Nivel DIOS
    </div>
    """, unsafe_allow_html=True)
    
    st.stop()

# ========== BIENVENIDA ==========
if not st.session_state.proceso_iniciado:
    st.title("🔄 BIENVENIDO AL SG-SST PHVA")
    st.markdown("---")
    
    col1, col2 = st.columns([2,1])
    with col1:
        st.markdown("""
        ### 📋 ¿CÓMO FUNCIONA?
        
        **Paso 1:** Completa el diagnóstico IA con los datos de tu empresa  
        **Paso 2:** La IA generará un diagnóstico completo  
        **Paso 3:** Los datos se precargarán automáticamente en todos los módulos  
        **Paso 4:** Revisa, completa y da seguimiento a cada fase del ciclo PHVA
        
        ### ✅ FASES DEL CICLO PHVA
        
        | Fase | Módulo | Estado |
        |------|--------|--------|
        | 1 | Diagnóstico IA | ⬜ Pendiente |
        | 2 | Identificar Peligros (GTC-45) | ⬜ Pendiente |
        | 3 | Evaluar Riesgos | ⬜ Pendiente |
        | 4 | Plan de Acción | ⬜ Pendiente |
        | 5 | Gestión de Trabajadores | ⬜ Pendiente |
        | 6 | Registro de Incidentes | ⬜ Pendiente |
        """)
    
    with col2:
        st.markdown("""
        <div style='
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 40px 30px;
            border-radius: 20px;
            color: white;
            text-align: center;
            box-shadow: 0 10px 30px rgba(0,0,0,0.2);
        '>
            <h2 style="font-size: 48px; margin: 0;">🚀</h2>
            <h3 style="margin: 10px 0;">¿LISTO PARA COMENZAR?</h3>
            <p>Completa el diagnóstico y la IA hará el trabajo pesado por ti.</p>
            <p style="margin-top: 20px; font-size: 12px; opacity: 0.8;">Powered by Gemini AI</p>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("🎯 COMENZAR PROCESO", use_container_width=True):
            st.session_state.proceso_iniciado = True
            st.rerun()
    
    st.markdown("---")
    st.markdown("<center>DESARROLLADO POR JAN BENITEZ</center>", unsafe_allow_html=True)
    st.stop()

# ========== SIDEBAR ==========
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/2917/2917995.png", width=80)
    st.markdown(f"**👤 {st.session_state.get('user', 'Administrador')}**")
    st.markdown("---")
    
    empresa = obtener_empresa()
    if empresa:
        st.markdown(f"**🏢 {empresa.get('nombre', 'Empresa')[:20]}**")
        st.caption(f"📊 {empresa.get('trabajadores', 0)} trabajadores")
    else:
        st.info("Sin empresa registrada")
    
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
    
    st.markdown("---")
    if st.button("🚪 Cerrar Sesión", use_container_width=True):
        st.session_state.auth = False
        st.session_state.proceso_iniciado = False
        st.rerun()

# ========== RESTANTE DEL CÓDIGO (MÓDULOS) ==========
empresa = obtener_empresa()

if menu == "📊 Dashboard":
    st.title("📊 Dashboard SST - Indicadores en Tiempo Real")
    
    if empresa:
        st.success(f"🏢 **{empresa.get('nombre', '')}** | 👥 {empresa.get('trabajadores', 0)} trabajadores")
    
    col1, col2, col3 = st.columns(3)
    peligros = obtener_peligros()
    acciones = obtener_acciones()
    trabajadores = obtener_trabajadores()
    
    with col1:
        st.metric("⚠️ Peligros", len(peligros))
    with col2:
        completadas = len(acciones[acciones['estado'] == 'Completada']) if not acciones.empty else 0
        st.metric("✅ Acciones", f"{completadas}/{len(acciones)}")
    with col3:
        st.metric("👥 Trabajadores", len(trabajadores))
    
    st.markdown("---")
    st.caption("DESARROLLADO POR JAN BENITEZ")

elif menu == "🤖 Diagnóstico IA":
    st.title("🤖 DIAGNÓSTICO IA - FASE 1")
    
    if empresa:
        st.success(f"✅ Empresa: {empresa.get('nombre', '')}")
        with st.expander("📋 Ver diagnóstico completo"):
            st.write(empresa.get('diagnostico', ''))
        if st.button("⚠️ Ir a Peligros"):
            st.session_state.menu = "⚠️ Peligros"
            st.rerun()
    else:
        with st.form("form_diagnostico"):
            nombre = st.text_input("📛 Nombre de la empresa *")
            trabajadores = st.number_input("👥 Número de trabajadores *", min_value=1, value=10)
            arl = st.selectbox("🏥 ARL *", ["Positiva", "Sura", "Colpatria"])
            if st.form_submit_button("🚀 GENERAR DIAGNÓSTICO"):
                if nombre:
                    with st.spinner("🤖 IA generando diagnóstico..."):
                        prompt = f"Diagnóstico SST profesional para {nombre} con {trabajadores} trabajadores, ARL {arl}. Incluye peligros, riesgos y plan de acción."
                        respuesta = call_ia(prompt)
                        if respuesta and "Error" not in respuesta:
                            guardar_empresa(nombre, trabajadores, arl, respuesta)
                            guardar_peligro("Ergonómico", f"Posturas inadecuadas en {nombre}", 2, 2)
                            guardar_peligro("Seguridad", "Caídas al mismo nivel", 2, 2)
                            guardar_peligro("Psicosocial", "Estrés laboral", 2, 2)
                            fecha = datetime.now()
                            guardar_accion(f"Matriz de riesgos para {nombre}", "SST", (fecha + timedelta(days=30)).strftime("%Y-%m-%d"))
                            guardar_accion("Capacitación en prevención", "Coordinador", (fecha + timedelta(days=45)).strftime("%Y-%m-%d"))
                            st.balloons()
                            st.success("✅ Diagnóstico generado y datos precargados")
                            st.rerun()
                        else:
                            st.error("Error con IA. Verifica conexión.")

# MÓDULOS RESTANTES (Peligros, Acciones, Trabajadores, Incidentes, Chat IA)
elif menu == "⚠️ Peligros":
    st.title("⚠️ PELIGROS - FASE 2 (GTC-45)")
    tab1, tab2 = st.tabs(["📋 Lista", "➕ Nuevo"])
    with tab1:
        df = obtener_peligros()
        if not df.empty:
            st.dataframe(df)
    with tab2:
        with st.form("form"):
            tipo = st.selectbox("Tipo", ["Físico", "Químico", "Biológico", "Ergonómico", "Psicosocial", "Seguridad"])
            desc = st.text_area("Descripción")
            prob = st.slider("Probabilidad", 1, 4, 2)
            sev = st.slider("Severidad", 1, 3, 2)
            if st.form_submit_button("Guardar"):
                if desc:
                    guardar_peligro(tipo, desc, prob, sev)
                    st.rerun()

elif menu == "✅ Plan de Acción":
    st.title("✅ PLAN DE ACCIÓN - FASE 4")
    tab1, tab2 = st.tabs(["📋 Seguimiento", "➕ Nueva"])
    with tab1:
        df = obtener_acciones()
        for _, row in df.iterrows():
            col1, col2 = st.columns([3,1])
            st.write(f"**{row['descripcion']}** - {row['responsable']}")
            nuevo = st.selectbox("Estado", ["Pendiente", "Completada"], key=row['id'])
            if nuevo != row['estado']:
                actualizar_estado(row['id'], nuevo)
                st.rerun()
    with tab2:
        with st.form("form"):
            desc = st.text_area("Descripción")
            resp = st.text_input("Responsable")
            if st.form_submit_button("Guardar"):
                if desc:
                    guardar_accion(desc, resp, datetime.now().strftime("%Y-%m-%d"))
                    st.rerun()

elif menu == "👥 Trabajadores":
    st.title("👥 TRABAJADORES - FASE 5")
    tab1, tab2 = st.tabs(["📋 Lista", "➕ Nuevo"])
    with tab1:
        st.dataframe(obtener_trabajadores())
    with tab2:
        with st.form("form"):
            nombre = st.text_input("Nombre")
            cedula = st.text_input("Cédula")
            cargo = st.text_input("Cargo")
            if st.form_submit_button("Guardar"):
                if nombre:
                    guardar_trabajador(nombre, cedula, cargo)
                    st.rerun()

elif menu == "📝 Incidentes":
    st.title("📝 INCIDENTES - FASE 6")
    with st.form("form"):
        desc = st.text_area("Descripción")
        fecha = st.date_input("Fecha", datetime.now())
        gravedad = st.selectbox("Gravedad", ["Leve", "Moderada", "Grave"])
        if st.form_submit_button("Registrar"):
            if desc:
                guardar_incidente(desc, fecha.strftime("%Y-%m-%d"), gravedad)
                st.rerun()
    st.dataframe(obtener_incidentes())

elif menu == "💬 Chat IA":
    st.title("💬 CHAT EXPERTO EN SST")
    if "msgs" not in st.session_state:
        st.session_state.msgs = []
    for msg in st.session_state.msgs:
        with st.chat_message(msg["role"]):
            st.write(msg["content"])
    if prompt := st.chat_input("Pregunta sobre SST..."):
        st.session_state.msgs.append({"role": "user", "content": prompt})
        respuesta = call_ia(prompt)
        st.session_state.msgs.append({"role": "assistant", "content": respuesta or "Error"})
        st.rerun()

# ========== FOOTER GLOBAL ==========
st.markdown("""
<div style='
    position: fixed;
    bottom: 0;
    left: 0;
    right: 0;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
    text-align: center;
    padding: 12px;
    font-size: 14px;
    font-weight: bold;
    letter-spacing: 1px;
    z-index: 999;
'>
    🔄 SG-SST PHVA | DESARROLLADO POR JAN BENITEZ | IA Protagonista | Nivel DIOS
</div>
""", unsafe_allow_html=True)
