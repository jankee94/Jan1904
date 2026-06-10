import streamlit as st
import sqlite3
import pandas as pd
import requests
import itertools
from datetime import datetime
import io
import json

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
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }
    .stTabs [data-baseweb="tab"] {
        background: rgba(255,255,255,0.1);
        border-radius: 8px;
        padding: 8px 16px;
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

# Tablas principales
cursor.execute('''CREATE TABLE IF NOT EXISTS usuarios (id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT UNIQUE, password TEXT, nombre TEXT, rol TEXT)''')
cursor.execute('''CREATE TABLE IF NOT EXISTS peligros (id INTEGER PRIMARY KEY AUTOINCREMENT, empresa_id INTEGER, tipo TEXT, descripcion TEXT, probabilidad INTEGER, severidad INTEGER, nivel TEXT, fecha_registro TEXT)''')
cursor.execute('''CREATE TABLE IF NOT EXISTS acciones (id INTEGER PRIMARY KEY AUTOINCREMENT, empresa_id INTEGER, descripcion TEXT, responsable TEXT, fecha_limite TEXT, estado TEXT, fecha_registro TEXT)''')
cursor.execute('''CREATE TABLE IF NOT EXISTS trabajadores (id INTEGER PRIMARY KEY AUTOINCREMENT, empresa_id INTEGER, nombre TEXT, cedula TEXT, cargo TEXT, area TEXT, fecha_registro TEXT)''')
cursor.execute('''CREATE TABLE IF NOT EXISTS incidentes (id INTEGER PRIMARY KEY AUTOINCREMENT, empresa_id INTEGER, descripcion TEXT, fecha TEXT, gravedad TEXT, causa TEXT, fecha_registro TEXT)''')
cursor.execute('''CREATE TABLE IF NOT EXISTS matriz_legal (id INTEGER PRIMARY KEY AUTOINCREMENT, empresa_id INTEGER, norma TEXT, articulo TEXT, requisito TEXT, cumple INTEGER, responsable TEXT)''')
cursor.execute('''CREATE TABLE IF NOT EXISTS auditorias (id INTEGER PRIMARY KEY AUTOINCREMENT, empresa_id INTEGER, codigo TEXT, fecha TEXT, auditor_id TEXT, puntuacion INTEGER, estado TEXT)''')
cursor.execute('''CREATE TABLE IF NOT EXISTS plan_anual (id INTEGER PRIMARY KEY AUTOINCREMENT, empresa_id INTEGER, anio INTEGER, mes INTEGER, actividad TEXT, responsable TEXT, presupuesto REAL, cumplimiento INTEGER)''')
cursor.execute('''CREATE TABLE IF NOT EXISTS empresa_config (id INTEGER PRIMARY KEY AUTOINCREMENT, nombre TEXT, nit TEXT, ubicacion TEXT, ciudad TEXT, sector TEXT, telefono TEXT, email TEXT)''')

# Usuario admin
cursor.execute("SELECT * FROM usuarios WHERE username='admin'")
if not cursor.fetchone():
    cursor.execute("INSERT INTO usuarios (username, password, nombre, rol) VALUES (?,?,?,?)", ('admin', 'admin123', 'Administrador', 'admin'))
    conn.commit()

# Configuración empresa por defecto
cursor.execute("SELECT COUNT(*) FROM empresa_config")
if cursor.fetchone()[0] == 0:
    cursor.execute("INSERT INTO empresa_config (nombre, nit, ubicacion, ciudad, sector, telefono, email) VALUES (?,?,?,?,?,?,?)", 
                  ('Constructora Segura SAS', '901.234.567-8', 'Calle 80 #45-67', 'Bogota', 'Construccion', '6015551234', 'sst@constructora.com'))
    conn.commit()

conn.commit()

def verificar_login(username, password):
    cursor.execute("SELECT * FROM usuarios WHERE username=? AND password=?", (username, password))
    user = cursor.fetchone()
    return {"id": user[0], "username": user[1], "nombre": user[3], "rol": user[4]} if user else None

def get_empresa():
    cursor.execute("SELECT nombre, nit, ubicacion, ciudad, sector FROM empresa_config LIMIT 1")
    data = cursor.fetchone()
    return {"nombre": data[0], "nit": data[1], "ubicacion": data[2], "ciudad": data[3], "sector": data[4]} if data else {}

# ========== FUNCIONES DE IMPORTAR/EXPORTAR ==========
def exportar_excel(df, nombre_modulo):
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, sheet_name=nombre_modulo, index=False)
    return output.getvalue()

def importar_excel(uploaded_file, tabla, columnas_requeridas, mapeo=None):
    try:
        df = pd.read_excel(uploaded_file)
        # Verificar columnas
        missing = [col for col in columnas_requeridas if col not in df.columns]
        if missing:
            return False, f"Faltan columnas: {missing}", None
        # Insertar datos
        fecha_reg = datetime.now().strftime("%Y-%m-%d")
        for _, row in df.iterrows():
            if tabla == "peligros":
                cursor.execute("INSERT INTO peligros (empresa_id, tipo, descripcion, probabilidad, severidad, nivel, fecha_registro) VALUES (1,?,?,?,?,?,?)",
                              (row['tipo'], row['descripcion'], int(row['probabilidad']), int(row['severidad']), row.get('nivel', 'II'), fecha_reg))
            elif tabla == "acciones":
                cursor.execute("INSERT INTO acciones (empresa_id, descripcion, responsable, fecha_limite, estado, fecha_registro) VALUES (1,?,?,?,?,?)",
                              (row['descripcion'], row['responsable'], row['fecha_limite'], row.get('estado', 'Pendiente'), fecha_reg))
            elif tabla == "trabajadores":
                cursor.execute("INSERT INTO trabajadores (empresa_id, nombre, cedula, cargo, area, fecha_registro) VALUES (1,?,?,?,?,?)",
                              (row['nombre'], row['cedula'], row['cargo'], row.get('area', 'General'), fecha_reg))
            elif tabla == "incidentes":
                cursor.execute("INSERT INTO incidentes (empresa_id, descripcion, fecha, gravedad, causa, fecha_registro) VALUES (1,?,?,?,?,?)",
                              (row['descripcion'], row['fecha'], row['gravedad'], row.get('causa', 'En investigacion'), fecha_reg))
        conn.commit()
        return True, f"{len(df)} registros importados", df
    except Exception as e:
        return False, f"Error: {str(e)}", None

def analizar_con_ia(datos, tipo):
    prompt = f"""
    Eres un experto en SST. Analiza los siguientes datos del módulo {tipo}:
    
    {datos}
    
    Genera un análisis breve con:
    1. Calidad de los datos
    2. Riesgos identificados
    3. Recomendaciones
    """
    return call_best_ia(prompt)

# ========== DATOS DE PRUEBA COMPLETOS ==========
def cargar_datos_prueba():
    with st.spinner("Cargando datos de prueba simulados..."):
        # Limpiar datos existentes
        cursor.execute("DELETE FROM peligros")
        cursor.execute("DELETE FROM acciones")
        cursor.execute("DELETE FROM trabajadores")
        cursor.execute("DELETE FROM incidentes")
        cursor.execute("DELETE FROM matriz_legal")
        
        fecha = datetime.now().strftime("%Y-%m-%d")
        
        # PELIGROS (10 registros)
        peligros_data = [
            ("Fisico", "Ruido excesivo en zona de maquinaria pesada", 4, 3, "I"),
            ("Fisico", "Vibraciones en equipos de perforacion", 3, 2, "II"),
            ("Ergonomico", "Posturas forzadas en area de oficinas", 3, 2, "II"),
            ("Quimico", "Exposicion a solventes en taller de pintura", 2, 3, "I"),
            ("Psicosocial", "Estrés laboral por altas cargas de trabajo", 3, 2, "II"),
            ("Seguridad", "Andamios sin proteccion en altura", 4, 3, "I"),
            ("Biologico", "Exposicion a hongos en areas humedas", 2, 2, "II"),
            ("Fisico", "Iluminacion insuficiente en bodega", 2, 2, "II"),
            ("Ergonomico", "Levantamiento manual de cargas", 3, 2, "II"),
            ("Quimico", "Polvo de silice en area de corte", 3, 3, "I"),
        ]
        for p in peligros_data:
            cursor.execute("INSERT INTO peligros (empresa_id, tipo, descripcion, probabilidad, severidad, nivel, fecha_registro) VALUES (1,?,?,?,?,?,?)", 
                          (p[0], p[1], p[2], p[3], p[4], fecha))
        
        # ACCIONES (8 registros)
        acciones_data = [
            ("Implementar barreras acusticas en zona de maquinaria", "Coordinador SST", "2025-01-15", "En progreso"),
            ("Capacitacion en pausas activas", "SST", "2024-12-10", "Pendiente"),
            ("Instalar extractores de aire en taller", "Mantenimiento", "2024-12-20", "Pendiente"),
            ("Evaluacion de cargas laborales", "Psicologia", "2025-01-05", "En progreso"),
            ("Instalar barandas en andamios", "Seguridad", "2024-11-30", "Completada"),
            ("Estudio de iluminacion en bodega", "Infraestructura", "2025-01-20", "Pendiente"),
            ("Compra de equipos de proteccion", "Compras", "2024-12-15", "En progreso"),
            ("Simulacro de emergencia", "SST", "2025-01-25", "Planificada"),
        ]
        for a in acciones_data:
            cursor.execute("INSERT INTO acciones (empresa_id, descripcion, responsable, fecha_limite, estado, fecha_registro) VALUES (1,?,?,?,?,?)", 
                          (a[0], a[1], a[2], a[3], fecha))
        
        # TRABAJADORES (15 registros)
        trabajadores_data = [
            ("Carlos Lopez", "12345678", "Operario", "Produccion"),
            ("Maria Gomez", "87654321", "Supervisor", "Produccion"),
            ("Juan Perez", "11122233", "Coordinador SST", "SST"),
            ("Ana Rodriguez", "44455566", "Auxiliar", "Administracion"),
            ("Luis Martinez", "77788899", "Jefe de produccion", "Produccion"),
            ("Sofia Ramirez", "99900011", "Ingeniero", "Ingenieria"),
            ("Pedro Sanchez", "22233344", "Operario", "Produccion"),
            ("Laura Fernandez", "55566677", "Secretaria", "Administracion"),
            ("Andres Torres", "88899900", "Tecnico", "Mantenimiento"),
            ("Carolina Diaz", "11122233", "Enfermera", "Salud"),
            ("Jorge Mora", "33344455", "Conductor", "Logistica"),
            ("Diana Rios", "66677788", "Almacenista", "Logistica"),
            ("Ricardo Pardo", "99900011", "Vigilante", "Seguridad"),
            ("Patricia Vega", "22211133", "Limpieza", "Servicios"),
            ("Fernando Castro", "55544466", "Supervisor", "Mantenimiento"),
        ]
        for t in trabajadores_data:
            cursor.execute("INSERT INTO trabajadores (empresa_id, nombre, cedula, cargo, area, fecha_registro) VALUES (1,?,?,?,?,?)", 
                          (t[0], t[1], t[2], t[3], fecha))
        
        # INCIDENTES (10 registros)
        incidentes_data = [
            ("Caida desde andamio de 3m", "2024-10-15", "Grave", "Falta de barandas"),
            ("Corte con herramienta manual", "2024-10-20", "Leve", "Falta de entrenamiento"),
            ("Exposicion a quimicos", "2024-11-01", "Moderada", "Falta de EPP"),
            ("Golpe con maquinaria", "2024-11-10", "Leve", "Distraccion"),
            ("Incendio en taller", "2024-11-15", "Grave", "Corto circuito"),
            ("Resbalon en piso humedo", "2024-11-20", "Leve", "Senalizacion insuficiente"),
            ("Caida de objeto", "2024-11-25", "Moderada", "Mal almacenamiento"),
            ("Intoxicacion por humos", "2024-12-01", "Moderada", "Ventilacion deficiente"),
            ("Atrapamiento", "2024-12-05", "Grave", "Falta de guardas"),
            ("Sobreesfuerzo", "2024-12-10", "Leve", "Mala postura"),
        ]
        for i in incidentes_data:
            cursor.execute("INSERT INTO incidentes (empresa_id, descripcion, fecha, gravedad, causa, fecha_registro) VALUES (1,?,?,?,?,?)", 
                          (i[0], i[1], i[2], i[3], fecha))
        
        # MATRIZ LEGAL (8 registros)
        legal_data = [
            ("ISO 45001", "4.1", "Contexto de la organizacion", 0, "Gerente"),
            ("ISO 45001", "5.2", "Politica de SST", 0, "Gerente"),
            ("ISO 45001", "6.1.2", "Identificacion de peligros", 1, "SST"),
            ("Decreto 1072", "2.2.4.6.22", "COPASST", 0, "Gerente"),
            ("Decreto 1072", "2.2.4.6.16", "Examenes medicos", 1, "SST"),
            ("ISO 45001", "7.2", "Competencia", 0, "SST"),
            ("ISO 45001", "8.2", "Preparacion emergencias", 0, "SST"),
            ("ISO 45001", "9.2", "Auditorias internas", 0, "Auditor"),
        ]
        for l in legal_data:
            cursor.execute("INSERT INTO matriz_legal (empresa_id, norma, articulo, requisito, cumple, responsable) VALUES (1,?,?,?,?,?)", 
                          (l[0], l[1], l[2], l[3], l[4]))
        
        conn.commit()
        st.success("✅ DATOS DE PRUEBA CARGADOS EXITOSAMENTE")
        st.balloons()
        
        # Mostrar resumen
        st.info(f"""
        **Resumen de datos cargados:**
        - ⚠️ Peligros: {len(peligros_data)}
        - ✅ Acciones: {len(acciones_data)}
        - 👥 Trabajadores: {len(trabajadores_data)}
        - 📝 Incidentes: {len(incidentes_data)}
        - 📋 Matriz Legal: {len(legal_data)}
        """)

# ========== MODULO GENERICO CON IMPORTAR/EXPORTAR ==========
def modulo_completo(titulo, tabla, columnas_requeridas, df_func, template_data=None):
    st.header(titulo)
    
    tab1, tab2, tab3, tab4 = st.tabs(["📋 Lista", "📤 Exportar", "📥 Importar Excel", "🤖 IA Analizar"])
    
    with tab1:
        df = df_func()
        if not df.empty:
            st.dataframe(df, use_container_width=True)
            st.caption(f"Total: {len(df)} registros")
        else:
            st.info("No hay datos. Usa 'Cargar Datos de Prueba' en Dashboard o importa desde Excel.")
    
    with tab2:
        df = df_func()
        if not df.empty:
            excel_data = exportar_excel(df, tabla)
            st.download_button("📊 Descargar Excel", data=excel_data, file_name=f"{tabla}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx", use_container_width=True)
            st.caption("Exporta todos los datos del módulo a Excel")
        else:
            st.info("No hay datos para exportar")
    
    with tab3:
        uploaded = st.file_uploader(f"Selecciona archivo Excel para {titulo}", type=['xlsx', 'xls'], key=f"import_{tabla}")
        if uploaded:
            if st.button("📎 Importar datos", key=f"btn_import_{tabla}"):
                success, msg, df_import = importar_excel(uploaded, tabla, columnas_requeridas)
                if success:
                    st.success(f"✅ {msg}")
                    # Analizar con IA
                    with st.spinner("🤖 IA analizando los datos importados..."):
                        analisis = analizar_con_ia(df_import.head(10).to_string(), titulo)
                        if analisis:
                            st.info(f"🤖 **Análisis IA:** {analisis[:500]}")
                    st.rerun()
                else:
                    st.error(msg)
        
        if template_data:
            with st.expander("📄 Ver formato requerido"):
                st.dataframe(pd.DataFrame(template_data), use_container_width=True)
                st.caption(f"Columnas requeridas: {', '.join(columnas_requeridas)}")
    
    with tab4:
        df = df_func()
        if not df.empty:
            with st.spinner("🤖 IA analizando los datos..."):
                analisis = analizar_con_ia(df.to_string(), titulo)
                if analisis:
                    st.markdown("### 🤖 Análisis de IA")
                    st.markdown(analisis)
                else:
                    st.warning("No se pudo obtener análisis de IA")
        else:
            st.info("No hay datos para analizar")

# ========== FUNCIONES PARA OBTENER DATAFRAMES ==========
def get_peligros():
    return pd.read_sql_query("SELECT id, tipo, descripcion, probabilidad, severidad, nivel, fecha_registro FROM peligros", conn)

def get_acciones():
    return pd.read_sql_query("SELECT id, descripcion, responsable, fecha_limite, estado, fecha_registro FROM acciones", conn)

def get_trabajadores():
    return pd.read_sql_query("SELECT id, nombre, cedula, cargo, area, fecha_registro FROM trabajadores", conn)

def get_incidentes():
    return pd.read_sql_query("SELECT id, descripcion, fecha, gravedad, causa, fecha_registro FROM incidentes ORDER BY fecha DESC", conn)

def get_matriz_legal():
    return pd.read_sql_query("SELECT id, norma, articulo, requisito, cumple, responsable FROM matriz_legal", conn)

# ========== SESION ==========
if "auth" not in st.session_state:
    st.session_state.auth = False
if "user" not in st.session_state:
    st.session_state.user = None

# ========== LOGIN ==========
if not st.session_state.auth:
    col1, col2, col3 = st.columns([1, 1.3, 1])
    with col2:
        st.markdown('''
        <div style="background: rgba(20,20,40,0.75); backdrop-filter: blur(14px); border-radius: 28px; padding: 40px; text-align:center">
            <img src="https://cdn-icons-png.flaticon.com/512/2917/2917995.png" width="70">
            <h1 style="color:white; font-size:28px; margin:10px 0">SG-SST PHVA</h1>
            <p style="color:rgba(255,255,255,0.6)">Seguridad y Salud, compromiso de todos</p>
            <p style="color:rgba(255,255,255,0.4); font-size:12px">Sistema de Gestión PHVA con IA</p>
        </div>
        ''', unsafe_allow_html=True)
        
        with st.form("login_form"):
            username = st.text_input("Usuario", placeholder="usuario")
            password = st.text_input("Contraseña", type="password", placeholder="contraseña")
            if st.form_submit_button("INGRESAR", use_container_width=True):
                user = verificar_login(username, password)
                if user:
                    st.session_state.auth = True
                    st.session_state.user = user
                    st.rerun()
                else:
                    st.error("Usuario o contraseña incorrectos. Use: admin / admin123")
        
        st.markdown('<p style="text-align:center; font-size:11px; color:rgba(255,255,255,0.3); margin-top:20px">SG-SST PHVA | Desarrollado por JAN BENITEZ</p>', unsafe_allow_html=True)
    st.stop()

# ========== SIDEBAR ==========
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/2917/2917995.png", width=50)
    st.markdown(f"### {st.session_state.user['nombre']}")
    st.caption(f"Rol: {st.session_state.user['rol'].upper()}")
    st.markdown("---")
    
    menu = st.radio("MENU PRINCIPAL", [
        "🏠 Dashboard",
        "⚠️ Peligros",
        "✅ Plan de Accion",
        "👥 Trabajadores", 
        "📝 Incidentes",
        "📋 Matriz Legal",
        "🔍 Auditorias",
        "📅 Plan Anual",
        "💬 Chat IA"
    ])
    
    st.markdown("---")
    if st.button("🚪 Cerrar Sesion", use_container_width=True):
        st.session_state.auth = False
        st.rerun()

# ========== DASHBOARD ==========
if menu == "🏠 Dashboard":
    st.title("🏠 Dashboard SST")
    
    empresa = get_empresa()
    st.info(f"🏢 **{empresa.get('nombre', 'No registrada')}** | NIT: {empresa.get('nit', 'N/A')} | {empresa.get('ciudad', 'N/A')}")
    
    col1, col2, col3, col4 = st.columns(4)
    with col1: st.metric("⚠️ Peligros", len(get_peligros()), delta="+5")
    with col2: st.metric("✅ Acciones", len(get_acciones()), delta="+3")
    with col3: st.metric("👥 Trabajadores", len(get_trabajadores()), delta="+10")
    with col4: st.metric("📝 Incidentes", len(get_incidentes()), delta="-2")
    
    st.markdown("---")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🚀 CARGAR DATOS DE PRUEBA COMPLETOS", use_container_width=True, type="primary"):
            cargar_datos_prueba()
            st.rerun()
    with col2:
        st.caption("✅ Simula 50+ registros: Peligros, Acciones, Trabajadores, Incidentes y Matriz Legal")
    
    st.markdown("---")
    st.subheader("📊 Estadisticas rapidas")
    
    col1, col2, col3 = st.columns(3)
    peligros_df = get_peligros()
    if not peligros_df.empty:
        with col1:
            niveles = peligros_df['nivel'].value_counts()
            st.bar_chart(niveles)
            st.caption("Distribucion por nivel de riesgo")
    
    acciones_df = get_acciones()
    if not acciones_df.empty:
        with col2:
            estados = acciones_df['estado'].value_counts()
            st.bar_chart(estados)
            st.caption("Estado de acciones")
    
    incidentes_df = get_incidentes()
    if not incidentes_df.empty:
        with col3:
            gravedades = incidentes_df['gravedad'].value_counts()
            st.bar_chart(gravedades)
            st.caption("Gravedad de incidentes")

# ========== MODULOS ==========
elif menu == "⚠️ Peligros":
    template = [{"tipo": "Fisico", "descripcion": "Ejemplo de peligro", "probabilidad": 3, "severidad": 2}]
    modulo_completo("⚠️ GESTION DE PELIGROS", "peligros", ['tipo', 'descripcion', 'probabilidad', 'severidad'], get_peligros, template)

elif menu == "✅ Plan de Accion":
    template = [{"descripcion": "Ejemplo de accion", "responsable": "SST", "fecha_limite": "2024-12-31", "estado": "Pendiente"}]
    modulo_completo("✅ PLAN DE ACCION", "acciones", ['descripcion', 'responsable', 'fecha_limite', 'estado'], get_acciones, template)

elif menu == "👥 Trabajadores":
    template = [{"nombre": "Ejemplo", "cedula": "12345678", "cargo": "Operario", "area": "Produccion"}]
    modulo_completo("👥 TRABAJADORES", "trabajadores", ['nombre', 'cedula', 'cargo', 'area'], get_trabajadores, template)

elif menu == "📝 Incidentes":
    template = [{"descripcion": "Ejemplo incidente", "fecha": "2024-12-01", "gravedad": "Leve", "causa": "Ejemplo"}]
    modulo_completo("📝 INCIDENTES", "incidentes", ['descripcion', 'fecha', 'gravedad', 'causa'], get_incidentes, template)

elif menu == "📋 Matriz Legal":
    df = get_matriz_legal()
    st.header("📋 MATRIZ LEGAL")
    st.dataframe(df, use_container_width=True)
    if st.button("Exportar Matriz Legal"):
        excel_data = exportar_excel(df, "matriz_legal")
        st.download_button("Descargar Excel", data=excel_data, file_name=f"matriz_legal_{datetime.now().strftime('%Y%m%d')}.xlsx")

elif menu == "🔍 Auditorias":
    st.header("🔍 AUDITORIAS")
    df = pd.read_sql_query("SELECT * FROM auditorias", conn)
    st.dataframe(df, use_container_width=True)
    st.info("Funcionalidad en desarrollo - Proximamente podras crear auditorias completas")

elif menu == "📅 Plan Anual":
    st.header("📅 PLAN ANUAL")
    df = pd.read_sql_query("SELECT * FROM plan_anual", conn)
    st.dataframe(df, use_container_width=True)
    st.info("Funcionalidad en desarrollo - Proximamente generacion con IA")

elif menu == "💬 Chat IA":
    st.title("💬 CHAT IA - Consultor SST")
    
    empresa = get_empresa()
    st.caption(f"Consultando sobre: {empresa.get('nombre', 'Empresa')}")
    
    if "messages" not in st.session_state:
        st.session_state.messages = []
    
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.write(msg["content"])
    
    if prompt := st.chat_input("Pregunta sobre SST, peligros, incidentes o normativa..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.write(prompt)
        with st.chat_message("assistant"):
            with st.spinner("🤖 IA consultando..."):
                # Contexto de la empresa
                contexto = f"Empresa: {empresa.get('nombre', 'N/A')}, Sector: {empresa.get('sector', 'N/A')}"
                respuesta = call_best_ia(f"{contexto}\n\nPregunta: {prompt}")
                st.write(respuesta)
                st.session_state.messages.append({"role": "assistant", "content": respuesta})

st.markdown("---")

# ============================================
# FUNCIÓN PARA VISTA PREVIA DE INFORME
# ============================================

def mostrar_vista_previa_informe():
    """Muestra una vista previa del informe antes de descargar"""
    st.subheader("📄 VISTA PREVIA DEL INFORME SST")
    
    # Obtener datos
    peligros_df = get_peligros()
    acciones_df = get_acciones()
    trabajadores_df = get_trabajadores()
    incidentes_df = get_incidentes()
    empresa = get_empresa()
    
    # Fecha del informe
    fecha_informe = datetime.now().strftime("%d/%m/%Y %H:%M")
    
    # ========== ENCABEZADO ==========
    st.markdown(f'''
    <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 20px; border-radius: 15px; margin-bottom: 20px;">
        <h2 style="color: white; margin: 0;">INFORME SG-SST PHVA</h2>
        <p style="color: rgba(255,255,255,0.8); margin: 5px 0 0 0;">Generado: {fecha_informe}</p>
    </div>
    ''', unsafe_allow_html=True)
    
    # ========== DATOS DE LA EMPRESA ==========
    with st.expander("🏢 DATOS DE LA EMPRESA", expanded=True):
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Nombre", empresa.get('nombre', 'No registrado'))
            st.metric("NIT", empresa.get('nit', 'No registrado'))
        with col2:
            st.metric("Ubicación", empresa.get('ubicacion', 'No registrado'))
            st.metric("Ciudad", empresa.get('ciudad', 'No registrado'))
        with col3:
            st.metric("Sector", empresa.get('sector', 'No registrado'))
            st.metric("Teléfono", empresa.get('telefono', 'No registrado'))
    
    # ========== RESUMEN GENERAL ==========
    st.subheader("📊 RESUMEN GENERAL")
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("⚠️ Peligros", len(peligros_df), delta="Identificados")
    with col2:
        completadas = len(acciones_df[acciones_df['estado'] == 'Completada']) if not acciones_df.empty else 0
        st.metric("✅ Acciones", f"{completadas}/{len(acciones_df)}", delta="En progreso")
    with col3:
        st.metric("👥 Trabajadores", len(trabajadores_df))
    with col4:
        st.metric("📝 Incidentes", len(incidentes_df))
    
    # ========== GRÁFICOS ==========
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("⚠️ Peligros por Nivel de Riesgo")
        if not peligros_df.empty:
            niveles = peligros_df['nivel'].value_counts()
            fig_niveles = go.Figure(data=[go.Bar(
                x=niveles.index, 
                y=niveles.values,
                marker_color=['#dc2626', '#f59e0b', '#10b981']
            )])
            fig_niveles.update_layout(height=300, margin=dict(l=0, r=0, t=30, b=0))
            st.plotly_chart(fig_niveles, use_container_width=True)
        else:
            st.info("No hay datos de peligros")
    
    with col2:
        st.subheader("📝 Incidentes por Gravedad")
        if not incidentes_df.empty:
            gravedades = incidentes_df['gravedad'].value_counts()
            fig_grav = go.Figure(data=[go.Pie(
                labels=gravedades.index,
                values=gravedades.values,
                marker_colors=['#dc2626', '#f59e0b', '#10b981']
            )])
            fig_grav.update_layout(height=300, margin=dict(l=0, r=0, t=30, b=0))
            st.plotly_chart(fig_grav, use_container_width=True)
        else:
            st.info("No hay datos de incidentes")
    
    # ========== TABLAS DE DATOS ==========
    tabs = st.tabs(["⚠️ Peligros", "✅ Acciones", "👥 Trabajadores", "📝 Incidentes"])
    
    with tabs[0]:
        if not peligros_df.empty:
            st.dataframe(peligros_df[['tipo', 'descripcion', 'probabilidad', 'severidad', 'nivel']].head(10), use_container_width=True)
            if len(peligros_df) > 10:
                st.caption(f"Mostrando 10 de {len(peligros_df)} registros")
        else:
            st.info("No hay peligros registrados")
    
    with tabs[1]:
        if not acciones_df.empty:
            st.dataframe(acciones_df[['descripcion', 'responsable', 'fecha_limite', 'estado']].head(10), use_container_width=True)
        else:
            st.info("No hay acciones registradas")
    
    with tabs[2]:
        if not trabajadores_df.empty:
            st.dataframe(trabajadores_df[['nombre', 'cedula', 'cargo', 'area']].head(10), use_container_width=True)
        else:
            st.info("No hay trabajadores registrados")
    
    with tabs[3]:
        if not incidentes_df.empty:
            st.dataframe(incidentes_df[['descripcion', 'fecha', 'gravedad', 'causa']].head(10), use_container_width=True)
        else:
            st.info("No hay incidentes registrados")
    
    # ========== INDICADORES SST ==========
    st.subheader("📈 INDICADORES SST")
    
    if not incidentes_df.empty and not trabajadores_df.empty:
        # Calcular índices
        total_incidentes = len(incidentes_df)
        total_trabajadores = len(trabajadores_df)
        indice_frecuencia = (total_incidentes * 1000) / total_trabajadores if total_trabajadores > 0 else 0
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Índice de Frecuencia", f"{indice_frecuencia:.1f}", delta="Incidentes x 1000 trabajadores")
        with col2:
            # Porcentaje de acciones completadas
            if not acciones_df.empty:
                pct_completadas = (len(acciones_df[acciones_df['estado'] == 'Completada']) / len(acciones_df)) * 100
                st.metric("Cumplimiento Plan", f"{pct_completadas:.0f}%", delta="Acciones completadas")
            else:
                st.metric("Cumplimiento Plan", "0%")
        with col3:
            # Riesgo predominante
            if not peligros_df.empty:
                riesgo_alto = len(peligros_df[peligros_df['nivel'] == 'I'])
                st.metric("Riesgos Altos", riesgo_alto, delta="Requieren atención inmediata")
            else:
                st.metric("Riesgos Altos", "0")
    
    # ========== RECOMENDACIONES IA ==========
    st.subheader("🤖 RECOMENDACIONES IA")
    with st.spinner("Generando recomendaciones..."):
        recomendaciones = call_best_ia(f"""
        Basado en el siguiente resumen SST de la empresa {empresa.get('nombre', '')}:
        - Peligros identificados: {len(peligros_df)}
        - Acciones: {len(acciones_df)}
        - Incidentes reportados: {len(incidentes_df)}
        - Trabajadores: {len(trabajadores_df)}
        
        Genera 5 recomendaciones prioritarias para mejorar el SG-SST.
        """)
        if recomendaciones:
            st.info(recomendaciones)
        else:
            st.warning("No se pudieron generar recomendaciones automáticas")
    
    # ========== FOOTER ==========
    st.markdown("---")
    st.caption(f"Informe generado automáticamente por SG-SST PHVA - {fecha_informe}")

def generar_informe_completo():
    """Genera el informe completo para descargar (Excel)"""
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        # Datos empresa
        empresa = get_empresa()
        empresa_df = pd.DataFrame([empresa])
        empresa_df.to_excel(writer, sheet_name='Datos_Empresa', index=False)
        
        # Peligros
        get_peligros().to_excel(writer, sheet_name='Peligros', index=False)
        
        # Acciones
        get_acciones().to_excel(writer, sheet_name='Acciones', index=False)
        
        # Trabajadores
        get_trabajadores().to_excel(writer, sheet_name='Trabajadores', index=False)
        
        # Incidentes
        get_incidentes().to_excel(writer, sheet_name='Incidentes', index=False)
        
        # Matriz Legal
        get_matriz_legal().to_excel(writer, sheet_name='Matriz_Legal', index=False)
    return output.getvalue()


st.markdown("<p style='text-align:center; font-size:12px; color:rgba(255,255,255,0.4)'>🔄 SG-SST PHVA | Sistema de Gestión PHVA con IA | Desarrollado por JAN BENITEZ</p>", unsafe_allow_html=True)
