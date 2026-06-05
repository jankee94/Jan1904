import streamlit as st
from datetime import datetime, timedelta
import sqlite3
import pandas as pd
import requests

st.set_page_config(page_title="SG-SST PHVA", page_icon="🔄", layout="wide")

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

# ========== LOGIN ==========
if not st.session_state.auth:
    st.title("🔐 SG-SST PHVA")
    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        st.image("https://cdn-icons-png.flaticon.com/512/2917/2917995.png", width=100)
        user = st.text_input("Usuario")
        pwd = st.text_input("Contraseña", type="password")
        if st.button("Ingresar"):
            if user == "admin" and pwd == "sst2024":
                st.session_state.auth = True
                st.rerun()
            else:
                st.error("Usuario: admin / Contraseña: sst2024")
    st.stop()

# ========== BIENVENIDA ==========
if not st.session_state.proceso_iniciado:
    st.title("🔄 BIENVENIDO AL SG-SST PHVA")
    st.markdown("---")
    col1, col2 = st.columns([2,1])
    with col1:
        st.markdown("""
        ### 📋 ¿CÓMO FUNCIONA?
        **Paso 1:** Completa el diagnóstico IA  
        **Paso 2:** La IA generará diagnóstico y precargará datos  
        **Paso 3:** Revisa y completa los módulos  
        """)
    with col2:
        if st.button("🎯 COMENZAR PROCESO"):
            st.session_state.proceso_iniciado = True
            st.rerun()
    st.stop()

# ========== SIDEBAR ==========
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/2917/2917995.png", width=80)
    empresa = obtener_empresa()
    if empresa:
        st.markdown(f"**🏢 {empresa.get('nombre', 'Empresa')[:20]}**")
    menu = st.radio("MENU", [
        "📊 Dashboard",
        "🤖 Diagnóstico IA",
        "⚠️ Peligros",
        "✅ Plan de Acción",
        "👥 Trabajadores",
        "📝 Incidentes",
        "💬 Chat IA"
    ])
    if st.button("Salir"):
        st.session_state.auth = False
        st.session_state.proceso_iniciado = False
        st.rerun()

empresa = obtener_empresa()

# ========== DASHBOARD ==========
if menu == "📊 Dashboard":
    st.title("📊 Dashboard")
    if empresa:
        st.success(f"Empresa: {empresa.get('nombre', '')}")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Peligros", len(obtener_peligros()))
    with col2:
        st.metric("Acciones", len(obtener_acciones()))
    with col3:
        st.metric("Trabajadores", len(obtener_trabajadores()))
    st.markdown("---")
    st.caption("DESARROLLADO POR JAN BENITEZ")

# ========== DIAGNÓSTICO IA ==========
elif menu == "🤖 Diagnóstico IA":
    st.title("🤖 DIAGNÓSTICO IA")
    
    if empresa:
        st.success(f"✅ Empresa: {empresa.get('nombre', '')}")
        with st.expander("Ver diagnóstico"):
            st.write(empresa.get('diagnostico', ''))
        if st.button("⚠️ Ir a Peligros"):
            st.session_state.menu = "⚠️ Peligros"
            st.rerun()
    else:
        with st.form("form_diagnostico"):
            nombre = st.text_input("Nombre de la empresa")
            trabajadores = st.number_input("Trabajadores", min_value=1, value=10)
            arl = st.selectbox("ARL", ["Positiva", "Sura", "Colpatria"])
            if st.form_submit_button("Generar Diagnóstico"):
                if nombre:
                    with st.spinner("IA generando..."):
                        prompt = f"Diagnóstico SST para {nombre} con {trabajadores} trabajadores. Máximo 200 palabras."
                        respuesta = call_ia(prompt)
                        if respuesta and "Error" not in respuesta:
                            guardar_empresa(nombre, trabajadores, arl, respuesta)
                            # Precargar peligros
                            guardar_peligro("Ergonómico", f"Posturas en {nombre}", 2, 2)
                            guardar_peligro("Seguridad", "Caídas al mismo nivel", 2, 2)
                            guardar_peligro("Psicosocial", "Estrés laboral", 2, 2)
                            # Precargar acciones
                            fecha = datetime.now()
                            guardar_accion(f"Matriz de riesgos para {nombre}", "SST", (fecha + timedelta(days=30)).strftime("%Y-%m-%d"))
                            guardar_accion("Capacitar al personal", "Coordinador", (fecha + timedelta(days=45)).strftime("%Y-%m-%d"))
                            st.balloons()
                            st.success("✅ Diagnóstico generado y datos precargados")
                            st.rerun()
                        else:
                            st.error("Error con IA. Usando modo offline.")

# ========== PELIGROS ==========
elif menu == "⚠️ Peligros":
    st.title("⚠️ Peligros")
    tab1, tab2 = st.tabs(["Lista", "Nuevo"])
    with tab1:
        df = obtener_peligros()
        if not df.empty:
            st.dataframe(df)
            with st.expander("Eliminar"):
                id_elim = st.number_input("ID", min_value=1, step=1)
                if st.button("Eliminar"):
                    eliminar_peligro(id_elim)
                    st.rerun()
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

# ========== PLAN DE ACCIÓN ==========
elif menu == "✅ Plan de Acción":
    st.title("✅ Plan de Acción")
    tab1, tab2 = st.tabs(["Seguimiento", "Nueva"])
    with tab1:
        df = obtener_acciones()
        for _, row in df.iterrows():
            col1, col2 = st.columns([3,1])
            with col1:
                st.write(f"**{row['descripcion']}** - {row['responsable']}")
            with col2:
                nuevo = st.selectbox("Estado", ["Pendiente", "Completada"], key=row['id'])
                if nuevo != row['estado']:
                    actualizar_estado(row['id'], nuevo)
                    st.rerun()
    with tab2:
        with st.form("form"):
            desc = st.text_area("Descripción")
            resp = st.text_input("Responsable")
            fecha = st.date_input("Fecha límite", datetime.now())
            if st.form_submit_button("Guardar"):
                if desc:
                    guardar_accion(desc, resp, fecha.strftime("%Y-%m-%d"))
                    st.rerun()

# ========== TRABAJADORES ==========
elif menu == "👥 Trabajadores":
    st.title("👥 Trabajadores")
    tab1, tab2 = st.tabs(["Lista", "Nuevo"])
    with tab1:
        df = obtener_trabajadores()
        st.dataframe(df)
    with tab2:
        with st.form("form"):
            nombre = st.text_input("Nombre")
            cedula = st.text_input("Cédula")
            cargo = st.text_input("Cargo")
            if st.form_submit_button("Guardar"):
                if nombre:
                    guardar_trabajador(nombre, cedula, cargo)
                    st.rerun()

# ========== INCIDENTES ==========
elif menu == "📝 Incidentes":
    st.title("📝 Incidentes")
    with st.form("form"):
        desc = st.text_area("Descripción")
        fecha = st.date_input("Fecha", datetime.now())
        gravedad = st.selectbox("Gravedad", ["Leve", "Moderada", "Grave"])
        if st.form_submit_button("Registrar"):
            if desc:
                guardar_incidente(desc, fecha.strftime("%Y-%m-%d"), gravedad)
                st.rerun()
    df = obtener_incidentes()
    st.dataframe(df)

# ========== CHAT IA ==========
elif menu == "💬 Chat IA":
    st.title("💬 Chat IA")
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

st.markdown("---")
st.markdown("<center>DESARROLLADO POR JAN BENITEZ</center>", unsafe_allow_html=True)
