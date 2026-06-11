import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import io
import requests
import time
import itertools

st.set_page_config(page_title="SG-SST PHVA", page_icon="🔄", layout="wide")

# ========== CSS ==========
st.markdown('''
<style>
    .stApp { background: linear-gradient(135deg, #0f0c29 0%, #302b63 50%, #24243e 100%); }
    header[data-testid="stHeader"] { display: none; }
    footer { display: none !important; }
    .main-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 20px;
        border-radius: 15px;
        margin-bottom: 20px;
    }
    .main-header h1 { color: white; margin: 0; font-size: 1.8rem; }
    .main-header p { color: rgba(255,255,255,0.8); margin: 5px 0 0 0; }
    .card {
        background: rgba(255,255,255,0.1);
        backdrop-filter: blur(10px);
        border-radius: 15px;
        padding: 20px;
        margin: 10px 0;
    }
    .metric-card {
        background: rgba(255,255,255,0.15);
        border-radius: 12px;
        padding: 15px;
        text-align: center;
    }
    .metric-value { font-size: 2rem; font-weight: bold; color: #667eea; }
    .metric-label { font-size: 0.8rem; color: rgba(255,255,255,0.7); }
    .success-badge { background: #27ae60; color: white; padding: 2px 8px; border-radius: 20px; font-size: 11px; }
    .warning-badge { background: #f39c12; color: white; padding: 2px 8px; border-radius: 20px; font-size: 11px; }
    .danger-badge { background: #e74c3c; color: white; padding: 2px 8px; border-radius: 20px; font-size: 11px; }
</style>
''', unsafe_allow_html=True)

# ========== CONFIGURACIÓN DE IA ==========
def get_all_gemini_keys():
    keys = []
    for i in range(1, 10):
        key = st.secrets.get(f"GEMINI_API_KEY_{i}")
        if key and key != "":
            keys.append(key)
    if not keys:
        key = st.secrets.get("GEMINI_API_KEY")
        if key and key != "":
            keys.append(key)
    return keys

def get_groq_key():
    return st.secrets.get("GROQ_API_KEY")

GEMINI_KEYS = get_all_gemini_keys()
GROQ_KEY = get_groq_key()
gemini_cycle = itertools.cycle(GEMINI_KEYS) if GEMINI_KEYS else None

def call_best_ia(prompt):
    # Intentar Gemini
    if GEMINI_KEYS:
        for _ in range(len(GEMINI_KEYS) * 2):
            key = next(gemini_cycle)
            try:
                url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-flash-latest:generateContent"
                headers = {"Content-Type": "application/json", "X-goog-api-key": key}
                data = {"contents": [{"parts": [{"text": prompt}]}]}
                r = requests.post(url, json=data, headers=headers, timeout=30)
                if r.status_code == 200:
                    return r.json()["candidates"][0]["content"]["parts"][0]["text"]
            except:
                continue
    
    # Intentar Groq
    if GROQ_KEY:
        modelos = ["llama-3.3-70b-versatile", "llama-3.1-70b-versatile"]
        for modelo in modelos:
            try:
                url = "https://api.groq.com/openai/v1/chat/completions"
                headers = {"Authorization": f"Bearer {GROQ_KEY}", "Content-Type": "application/json"}
                data = {"model": modelo, "messages": [{"role": "user", "content": prompt}], "temperature": 0.7}
                r = requests.post(url, json=data, headers=headers, timeout=30)
                if r.status_code == 200:
                    return r.json()["choices"][0]["message"]["content"]
            except:
                continue
    
    return "⚠️ IA no disponible en este momento. Intenta de nuevo."

def exportar_excel(data, nombre):
    df = pd.DataFrame(data)
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, sheet_name=nombre, index=False)
    return output.getvalue()

# ========== INICIALIZAR DATOS ==========
def init_data():
    if "auth" not in st.session_state:
        st.session_state.auth = False
    if "current_user" not in st.session_state:
        st.session_state.current_user = None
    
    # Datos de empresa
    if "empresa" not in st.session_state:
        st.session_state.empresa = {
            "nombre": "Constructora Segura SAS",
            "nit": "901.234.567-8",
            "ubicacion": "Calle 80 #45-67, Bogotá",
            "sector": "Construcción",
            "telefono": "6015551234",
            "email": "sst@constructora.com"
        }
    
    # Peligros
    if "peligros" not in st.session_state:
        st.session_state.peligros = [
            {"id": 1, "tipo": "Físico", "descripcion": "Ruido excesivo en maquinaria", "probabilidad": 4, "severidad": 3, "nivel": "I", "fecha": "2024-01-15"},
            {"id": 2, "tipo": "Ergonómico", "descripcion": "Posturas forzadas en oficinas", "probabilidad": 3, "severidad": 2, "nivel": "II", "fecha": "2024-01-20"},
            {"id": 3, "tipo": "Químico", "descripcion": "Exposición a solventes", "probabilidad": 2, "severidad": 3, "nivel": "I", "fecha": "2024-02-01"},
        ]
    
    # Acciones
    if "acciones" not in st.session_state:
        st.session_state.acciones = [
            {"id": 1, "descripcion": "Implementar barreras acústicas", "responsable": "Coordinador SST", "fecha_limite": "2024-12-15", "estado": "En progreso", "prioridad": "Alta"},
            {"id": 2, "descripcion": "Capacitación en pausas activas", "responsable": "SST", "fecha_limite": "2024-11-30", "estado": "Pendiente", "prioridad": "Media"},
            {"id": 3, "descripcion": "Instalar extractores de aire", "responsable": "Mantenimiento", "fecha_limite": "2024-12-20", "estado": "Pendiente", "prioridad": "Alta"},
        ]
    
    # Trabajadores
    if "trabajadores" not in st.session_state:
        st.session_state.trabajadores = [
            {"id": 1, "nombre": "Carlos López", "cedula": "12345678", "cargo": "Operario", "area": "Producción", "eps": "Sura", "arl": "Positiva"},
            {"id": 2, "nombre": "María Gómez", "cedula": "87654321", "cargo": "Supervisor", "area": "Producción", "eps": "Sura", "arl": "Positiva"},
            {"id": 3, "nombre": "Juan Pérez", "cedula": "11122233", "cargo": "Coordinador SST", "area": "SST", "eps": "Sura", "arl": "Positiva"},
        ]
    
    # Incidentes
    if "incidentes" not in st.session_state:
        st.session_state.incidentes = [
            {"id": 1, "descripcion": "Caída desde andamio", "fecha": "2024-10-15", "gravedad": "Grave", "tipo": "Accidente", "causa": "Falta de barandas"},
            {"id": 2, "descripcion": "Corte con herramienta", "fecha": "2024-10-20", "gravedad": "Leve", "tipo": "Incidente", "causa": "Falta de entrenamiento"},
        ]
    
    # Capacitaciones
    if "capacitaciones" not in st.session_state:
        st.session_state.capacitaciones = [
            {"id": 1, "titulo": "Trabajo en Alturas", "fecha": "2024-11-15", "duracion": 8, "participantes": 15, "estado": "Finalizada"},
            {"id": 2, "titulo": "Primeros Auxilios", "fecha": "2024-11-25", "duracion": 4, "participantes": 0, "estado": "Programada"},
        ]
    
    # Inspecciones
    if "inspecciones" not in st.session_state:
        st.session_state.inspecciones = []
    
    # Emergencias
    if "emergencias" not in st.session_state:
        st.session_state.emergencias = {
            "brigadistas": [
                {"nombre": "Carlos López", "tipo": "Primeros Auxilios", "telefono": "3001234567"},
                {"nombre": "María Gómez", "tipo": "Contra Incendios", "telefono": "3001234568"},
            ],
            "equipos": [
                {"tipo": "Extintor PQS", "ubicacion": "Planta", "estado": "Operativo"},
                {"tipo": "Botiquín", "ubicacion": "Oficinas", "estado": "Operativo"},
            ],
            "alertas": []
        }
    
    # Documentos
    if "documentos" not in st.session_state:
        st.session_state.documentos = [
            {"id": 1, "titulo": "Política SST", "codigo": "POL-SST-001", "version": "1.0", "fecha_vencimiento": "2025-12-31"},
            {"id": 2, "titulo": "Matriz de Riesgos", "codigo": "MAT-RIS-001", "version": "2.0", "fecha_vencimiento": "2025-06-30"},
        ]

init_data()

# ========== LOGIN ==========
if not st.session_state.auth:
    col1, col2, col3 = st.columns([1, 1.5, 1])
    with col2:
        st.markdown('''
        <div style="background: rgba(20,20,40,0.8); backdrop-filter: blur(14px); border-radius: 28px; padding: 40px; text-align:center">
            <img src="https://cdn-icons-png.flaticon.com/512/2917/2917995.png" width="70">
            <h1 style="color:white;">SG-SST PHVA</h1>
            <p style="color:rgba(255,255,255,0.6)">Sistema de Gestión en Seguridad y Salud en el Trabajo</p>
            <p style="color:rgba(255,255,255,0.4); font-size:12px">14 Módulos | IA Integrada | Reportes Excel</p>
        </div>
        ''', unsafe_allow_html=True)
        
        with st.form("login_form"):
            username = st.text_input("Usuario", placeholder="admin")
            password = st.text_input("Contraseña", type="password", placeholder="admin123")
            if st.form_submit_button("🚀 INGRESAR", use_container_width=True):
                if username == "admin" and password == "admin123":
                    st.session_state.auth = True
                    st.session_state.current_user = {"nombre": "Administrador", "rol": "admin"}
                    st.rerun()
                else:
                    st.error("❌ Usuario o contraseña incorrectos")
        
        st.markdown('<p style="text-align:center; font-size:11px; color:gray">SG-SST PHVA | Desarrollado por JAN BENITEZ</p>', unsafe_allow_html=True)
    st.stop()

# ========== SIDEBAR CON 14 MÓDULOS ==========
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/2917/2917995.png", width=50)
    st.markdown(f"### {st.session_state.current_user.get('nombre', 'Usuario')}")
    st.caption("Administrador")
    st.markdown("---")
    
    menu = st.radio("📋 MÓDULOS", [
        "🏠 Dashboard",
        "🏢 Empresa",
        "⚠️ Peligros",
        "✅ Plan de Acción",
        "👥 Trabajadores",
        "📝 Incidentes",
        "📋 Matriz Legal",
        "🔍 Auditorías",
        "📚 Capacitaciones",
        "🔧 Inspecciones",
        "🚨 Emergencias",
        "📄 Documentos",
        "📊 Indicadores",
        "💬 Chat IA"
    ])
    
    st.markdown("---")
    if st.button("🚪 Cerrar Sesión", use_container_width=True):
        st.session_state.auth = False
        st.rerun()

# ========== DASHBOARD ==========
if menu == "🏠 Dashboard":
    st.markdown(f'<div class="main-header"><h1>📊 Dashboard SST</h1><p>{st.session_state.empresa["nombre"]}</p></div>', unsafe_allow_html=True)
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown(f'<div class="metric-card"><div class="metric-value">{len(st.session_state.peligros)}</div><div class="metric-label">Peligros</div></div>', unsafe_allow_html=True)
    with col2:
        completadas = len([a for a in st.session_state.acciones if a["estado"] == "Completada"])
        st.markdown(f'<div class="metric-card"><div class="metric-value">{completadas}/{len(st.session_state.acciones)}</div><div class="metric-label">Acciones</div></div>', unsafe_allow_html=True)
    with col3:
        st.markdown(f'<div class="metric-card"><div class="metric-value">{len(st.session_state.trabajadores)}</div><div class="metric-label">Trabajadores</div></div>', unsafe_allow_html=True)
    with col4:
        st.markdown(f'<div class="metric-card"><div class="metric-value">{len(st.session_state.incidentes)}</div><div class="metric-label">Incidentes</div></div>', unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Gráficos
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("⚠️ Peligros por Nivel")
        niveles = [p["nivel"] for p in st.session_state.peligros]
        niveles_count = {"I": niveles.count("I"), "II": niveles.count("II"), "III": niveles.count("III")}
        fig = go.Figure(data=[go.Bar(x=list(niveles_count.keys()), y=list(niveles_count.values()), marker_color=["#e74c3c", "#f39c12", "#27ae60"])])
        fig.update_layout(height=300, margin=dict(l=0, r=0, t=30, b=0))
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("📈 Acciones por Estado")
        estados = [a["estado"] for a in st.session_state.acciones]
        estados_count = {"Pendiente": estados.count("Pendiente"), "En progreso": estados.count("En progreso"), "Completada": estados.count("Completada")}
        fig = go.Figure(data=[go.Pie(labels=list(estados_count.keys()), values=list(estados_count.values()))])
        fig.update_layout(height=300, margin=dict(l=0, r=0, t=30, b=0))
        st.plotly_chart(fig, use_container_width=True)
    
    # Test de IA
    with st.expander("🤖 Prueba de Conexión IA"):
        st.caption(f"Gemini Keys: {len(GEMINI_KEYS)} | Groq: {'✅' if GROQ_KEY else '❌'}")
        
        if st.button("🔌 Probar IA"):
            with st.spinner("Consultando IA..."):
                respuesta = call_best_ia("Responde solo: La IA funciona correctamente")
                if respuesta and "⚠️" not in respuesta:
                    st.success(f"✅ {respuesta}")
                    st.balloons()
                else:
                    st.error(f"❌ {respuesta}")

# ========== EMPRESA ==========
elif menu == "🏢 Empresa":
    st.markdown('<div class="main-header"><h1>🏢 Configuración de la Empresa</h1></div>', unsafe_allow_html=True)
    
    with st.form("empresa_form"):
        col1, col2 = st.columns(2)
        with col1:
            nombre = st.text_input("Nombre", value=st.session_state.empresa["nombre"])
            nit = st.text_input("NIT", value=st.session_state.empresa["nit"])
            ubicacion = st.text_input("Ubicación", value=st.session_state.empresa["ubicacion"])
        with col2:
            sector = st.text_input("Sector", value=st.session_state.empresa["sector"])
            telefono = st.text_input("Teléfono", value=st.session_state.empresa["telefono"])
            email = st.text_input("Email", value=st.session_state.empresa["email"])
        
        if st.form_submit_button("💾 Guardar", use_container_width=True):
            st.session_state.empresa = {"nombre": nombre, "nit": nit, "ubicacion": ubicacion, "sector": sector, "telefono": telefono, "email": email}
            st.success("✅ Datos guardados")

# ========== PELIGROS ==========
elif menu == "⚠️ Peligros":
    st.markdown('<div class="main-header"><h1>⚠️ Gestión de Peligros</h1><p>Matriz de identificación y evaluación de riesgos GTC-45</p></div>', unsafe_allow_html=True)
    
    tab1, tab2 = st.tabs(["📋 Lista", "➕ Agregar"])
    
    with tab1:
        df = pd.DataFrame(st.session_state.peligros)
        st.dataframe(df, use_container_width=True)
        excel_data = exportar_excel(st.session_state.peligros, "peligros")
        st.download_button("📥 Exportar a Excel", data=excel_data, file_name=f"peligros_{datetime.now().strftime('%Y%m%d')}.xlsx")
    
    with tab2:
        with st.form("add_peligro"):
            tipo = st.selectbox("Tipo", ["Físico", "Químico", "Biológico", "Ergonómico", "Psicosocial", "Seguridad"])
            descripcion = st.text_area("Descripción")
            col1, col2 = st.columns(2)
            with col1:
                probabilidad = st.slider("Probabilidad (1-4)", 1, 4, 2)
            with col2:
                severidad = st.slider("Severidad (1-3)", 1, 3, 2)
            
            nivel = "I" if probabilidad * severidad >= 6 else "II" if probabilidad * severidad >= 4 else "III"
            st.markdown(f"**Nivel de Riesgo:** <span class='{'danger-badge' if nivel=='I' else 'warning-badge' if nivel=='II' else 'success-badge'}'>Nivel {nivel}</span>", unsafe_allow_html=True)
            
            if st.form_submit_button("Guardar"):
                nuevo_id = max([p["id"] for p in st.session_state.peligros]) + 1 if st.session_state.peligros else 1
                st.session_state.peligros.append({
                    "id": nuevo_id, "tipo": tipo, "descripcion": descripcion,
                    "probabilidad": probabilidad, "severidad": severidad, "nivel": nivel,
                    "fecha": datetime.now().strftime("%Y-%m-%d")
                })
                st.success("✅ Peligro guardado")
                st.rerun()

# ========== PLAN DE ACCIÓN ==========
elif menu == "✅ Plan de Acción":
    st.markdown('<div class="main-header"><h1>✅ Plan de Acción</h1><p>Seguimiento de acciones correctivas y preventivas</p></div>', unsafe_allow_html=True)
    
    for accion in st.session_state.acciones:
        with st.expander(f"📌 {accion['descripcion']}"):
            col1, col2 = st.columns(2)
            with col1:
                st.write(f"**Responsable:** {accion['responsable']}")
                st.write(f"**Fecha límite:** {accion['fecha_limite']}")
                st.write(f"**Prioridad:** {accion['prioridad']}")
            with col2:
                estados = ["Pendiente", "En progreso", "Completada"]
                nuevo_estado = st.selectbox("Estado", estados, index=estados.index(accion["estado"]), key=f"estado_{accion['id']}")
                if nuevo_estado != accion["estado"]:
                    accion["estado"] = nuevo_estado
                    st.rerun()
    
    excel_data = exportar_excel(st.session_state.acciones, "acciones")
    st.download_button("📥 Exportar Plan de Acción", data=excel_data, file_name=f"plan_accion_{datetime.now().strftime('%Y%m%d')}.xlsx")

# ========== TRABAJADORES ==========
elif menu == "👥 Trabajadores":
    st.markdown('<div class="main-header"><h1>👥 Gestión de Trabajadores</h1></div>', unsafe_allow_html=True)
    
    df = pd.DataFrame(st.session_state.trabajadores)
    st.dataframe(df, use_container_width=True)
    excel_data = exportar_excel(st.session_state.trabajadores, "trabajadores")
    st.download_button("📥 Exportar Trabajadores", data=excel_data, file_name=f"trabajadores_{datetime.now().strftime('%Y%m%d')}.xlsx")

# ========== INCIDENTES ==========
elif menu == "📝 Incidentes":
    st.markdown('<div class="main-header"><h1>📝 Gestión de Incidentes</h1></div>', unsafe_allow_html=True)
    
    tab1, tab2 = st.tabs(["📋 Historial", "➕ Reportar"])
    
    with tab1:
        df = pd.DataFrame(st.session_state.incidentes)
        st.dataframe(df, use_container_width=True)
        excel_data = exportar_excel(st.session_state.incidentes, "incidentes")
        st.download_button("📥 Exportar Incidentes", data=excel_data, file_name=f"incidentes_{datetime.now().strftime('%Y%m%d')}.xlsx")
    
    with tab2:
        with st.form("add_incidente"):
            descripcion = st.text_area("Descripción")
            fecha = st.date_input("Fecha", datetime.now())
            tipo = st.selectbox("Tipo", ["Accidente", "Incidente", "Enfermedad Laboral"])
            gravedad = st.selectbox("Gravedad", ["Leve", "Moderada", "Grave", "Mortal"])
            causa = st.text_area("Causa probable")
            
            if st.form_submit_button("Reportar"):
                nuevo_id = max([i["id"] for i in st.session_state.incidentes]) + 1 if st.session_state.incidentes else 1
                st.session_state.incidentes.append({
                    "id": nuevo_id, "descripcion": descripcion, "fecha": fecha.strftime("%Y-%m-%d"),
                    "tipo": tipo, "gravedad": gravedad, "causa": causa
                })
                st.success("✅ Incidente reportado")
                st.rerun()

# ========== MATRIZ LEGAL ==========
elif menu == "📋 Matriz Legal":
    st.markdown('<div class="main-header"><h1>📋 Matriz Legal</h1><p>ISO 45001:2018 + Decreto 1072 de 2015</p></div>', unsafe_allow_html=True)
    
    requisitos = [
        {"norma": "ISO 45001", "articulo": "4.1", "requisito": "Comprender la organización y su contexto", "cumple": False},
        {"norma": "ISO 45001", "articulo": "5.2", "requisito": "Política de SST", "cumple": False},
        {"norma": "ISO 45001", "articulo": "6.1.2", "requisito": "Identificación de peligros", "cumple": True},
        {"norma": "Decreto 1072", "articulo": "2.2.4.6.22", "requisito": "Conformar COPASST", "cumple": False},
        {"norma": "Decreto 1072", "articulo": "2.2.4.6.16", "requisito": "Exámenes médicos ocupacionales", "cumple": True},
    ]
    
    for req in requisitos:
        col1, col2, col3 = st.columns([3, 1, 1])
        with col1:
            st.write(f"**{req['norma']} - {req['articulo']}**")
            st.caption(req['requisito'])
        with col2:
            cumple = st.checkbox("Cumple", value=req["cumple"], key=f"cumple_{req['articulo']}")
            req["cumple"] = cumple
        with col3:
            if cumple:
                st.markdown('<span class="success-badge">✅ Cumple</span>', unsafe_allow_html=True)
            else:
                st.markdown('<span class="danger-badge">❌ No cumple</span>', unsafe_allow_html=True)
        st.markdown("---")
    
    # Calcular cumplimiento
    total = len(requisitos)
    cumplen = sum(1 for r in requisitos if r["cumple"])
    st.progress(cumplen/total)
    st.metric("Cumplimiento General", f"{(cumplen/total)*100:.0f}%")

# ========== AUDITORÍAS ==========
elif menu == "🔍 Auditorías":
    st.markdown('<div class="main-header"><h1>🔍 Auditorías Internas</h1></div>', unsafe_allow_html=True)
    
    if "auditorias" not in st.session_state:
        st.session_state.auditorias = []
    
    tab1, tab2 = st.tabs(["📋 Lista", "➕ Nueva"])
    
    with tab1:
        if st.session_state.auditorias:
            df = pd.DataFrame(st.session_state.auditorias)
            st.dataframe(df, use_container_width=True)
        else:
            st.info("No hay auditorías registradas")
    
    with tab2:
        with st.form("add_auditoria"):
            codigo = st.text_input("Código", "AUD-001")
            fecha = st.date_input("Fecha", datetime.now())
            auditor = st.text_input("Auditor líder")
            
            if st.form_submit_button("Crear Auditoría"):
                st.session_state.auditorias.append({
                    "id": len(st.session_state.auditorias) + 1,
                    "codigo": codigo,
                    "fecha": fecha.strftime("%Y-%m-%d"),
                    "auditor": auditor,
                    "estado": "Planificada"
                })
                st.success(f"✅ Auditoría {codigo} creada")
                st.rerun()

# ========== CAPACITACIONES ==========
elif menu == "📚 Capacitaciones":
    st.markdown('<div class="main-header"><h1>📚 Capacitaciones</h1><p>Gestión de capacitaciones y entrenamientos</p></div>', unsafe_allow_html=True)
    
    tab1, tab2 = st.tabs(["📋 Programadas", "➕ Nueva"])
    
    with tab1:
        for cap in st.session_state.capacitaciones:
            with st.expander(f"📌 {cap['titulo']} - {cap['fecha']}"):
                col1, col2 = st.columns(2)
                with col1:
                    st.write(f"**Duración:** {cap['duracion']} horas")
                    st.write(f"**Participantes:** {cap['participantes']}")
                with col2:
                    estado_color = "success-badge" if cap['estado'] == "Finalizada" else "warning-badge"
                    st.markdown(f"**Estado:** <span class='{estado_color}'>{cap['estado']}</span>", unsafe_allow_html=True)
    
    with tab2:
        with st.form("add_capacitacion"):
            titulo = st.text_input("Título")
            fecha = st.date_input("Fecha", datetime.now())
            duracion = st.number_input("Duración (horas)", min_value=1, value=8)
            
            if st.form_submit_button("Programar"):
                nuevo_id = len(st.session_state.capacitaciones) + 1
                st.session_state.capacitaciones.append({
                    "id": nuevo_id, "titulo": titulo, "fecha": fecha.strftime("%Y-%m-%d"),
                    "duracion": duracion, "participantes": 0, "estado": "Programada"
                })
                st.success("✅ Capacitación programada")
                st.rerun()

# ========== INSPECCIONES ==========
elif menu == "🔧 Inspecciones":
    st.markdown('<div class="main-header"><h1>🔧 Inspecciones</h1><p>Inspecciones locativas, equipos y EPP</p></div>', unsafe_allow_html=True)
    
    checklists = {
        "Locativa": ["Pisos en buen estado", "Techos sin filtraciones", "Puertas operativas", "Escaleras con barandas"],
        "Equipos": ["Guardas de seguridad", "Sistema eléctrico", "Botón de paro", "Manuales disponibles"],
        "EPP": ["Casco de seguridad", "Gafas protectoras", "Guantes", "Botas de seguridad"]
    }
    
    with st.form("add_inspeccion"):
        tipo = st.selectbox("Tipo", list(checklists.keys()))
        ubicacion = st.text_input("Ubicación")
        
        st.subheader("📋 Checklist")
        resultados = {}
        for item in checklists[tipo]:
            resultados[item] = st.checkbox(item)
        
        if st.form_submit_button("Completar Inspección"):
            hallazgos = [item for item, cumple in resultados.items() if not cumple]
            calificacion = ((len(checklists[tipo]) - len(hallazgos)) / len(checklists[tipo])) * 100
            
            st.session_state.inspecciones.append({
                "tipo": tipo, "ubicacion": ubicacion, "fecha": datetime.now().strftime("%Y-%m-%d"),
                "hallazgos": len(hallazgos), "calificacion": f"{calificacion:.0f}%"
            })
            
            if hallazgos:
                st.warning(f"⚠️ Hallazgos encontrados: {', '.join(hallazgos)}")
            st.success(f"✅ Inspección completada - Calificación: {calificacion:.0f}%")
            st.rerun()

# ========== EMERGENCIAS ==========
elif menu == "🚨 Emergencias":
    st.markdown('<div class="main-header"><h1>🚨 Emergencias</h1><p>Brigadistas, equipos y alertas</p></div>', unsafe_allow_html=True)
    
    tab1, tab2, tab3 = st.tabs(["👥 Brigadistas", "🛠️ Equipos", "⚠️ Alertas"])
    
    with tab1:
        for b in st.session_state.emergencias["brigadistas"]:
            st.write(f"**{b['nombre']}** - {b['tipo']}")
            st.caption(f"Teléfono: {b['telefono']}")
            st.markdown("---")
    
    with tab2:
        for e in st.session_state.emergencias["equipos"]:
            st.write(f"**{e['tipo']}** - {e['ubicacion']}")
            st.caption(f"Estado: {e['estado']}")
            st.markdown("---")
    
    with tab3:
        with st.form("activar_alerta"):
            tipo_alerta = st.selectbox("Tipo", ["Incendio", "Sismo", "Evacuación", "Emergencia Médica"])
            ubicacion = st.text_input("Ubicación")
            if st.form_submit_button("🚨 Activar Alerta", use_container_width=True):
                st.session_state.emergencias["alertas"].append({
                    "tipo": tipo_alerta, "ubicacion": ubicacion, "fecha": datetime.now().strftime("%H:%M:%S"), "estado": "Activa"
                })
                st.error("🚨 ALERTA DE EMERGENCIA ACTIVADA")
                st.balloons()
                st.rerun()
        
        for a in st.session_state.emergencias["alertas"]:
            if a["estado"] == "Activa":
                st.warning(f"⚠️ {a['tipo']} - {a['ubicacion']} - {a['fecha']}")

# ========== DOCUMENTOS ==========
elif menu == "📄 Documentos":
    st.markdown('<div class="main-header"><h1>📄 Gestión Documental</h1><p>Control de documentos del SG-SST</p></div>', unsafe_allow_html=True)
    
    for doc in st.session_state.documentos:
        with st.expander(f"📄 {doc['titulo']} - {doc['codigo']} (v{doc['version']})"):
            col1, col2 = st.columns(2)
            with col1:
                st.write(f"**Código:** {doc['codigo']}")
                st.write(f"**Versión:** {doc['version']}")
            with col2:
                st.write(f"**Vence:** {doc['fecha_vencimiento']}")
            
            if st.button(f"📥 Descargar", key=f"desc_{doc['id']}"):
                st.info(f"Documento {doc['titulo']} listo para descargar")

# ========== INDICADORES ==========
elif menu == "📊 Indicadores":
    st.markdown('<div class="main-header"><h1>📊 Indicadores SST</h1><p>Dashboard ejecutivo de indicadores clave</p></div>', unsafe_allow_html=True)
    
    total_incidentes = len(st.session_state.incidentes)
    total_trabajadores = len(st.session_state.trabajadores)
    acciones_completadas = len([a for a in st.session_state.acciones if a["estado"] == "Completada"])
    total_acciones = len(st.session_state.acciones)
    
    tasa_accidentalidad = (total_incidentes * 100 / total_trabajadores) if total_trabajadores > 0 else 0
    cumplimiento_phva = (acciones_completadas * 100 / total_acciones) if total_acciones > 0 else 0
    peligros_criticos = len([p for p in st.session_state.peligros if p["nivel"] == "I"])
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Índice de Frecuencia", f"{tasa_accidentalidad:.1f}%", delta="Meta ≤5%")
    with col2:
        st.metric("Cumplimiento PHVA", f"{cumplimiento_phva:.0f}%", delta="Meta ≥80%")
    with col3:
        st.metric("Peligros Críticos", peligros_criticos, delta="Requieren atención")
    with col4:
        st.metric("Incidentes", total_incidentes, delta="Último año")
    
    excel_data = exportar_excel([
        {"Indicador": "Índice de Frecuencia", "Valor": f"{tasa_accidentalidad:.1f}%"},
        {"Indicador": "Cumplimiento PHVA", "Valor": f"{cumplimiento_phva:.0f}%"},
        {"Indicador": "Peligros Críticos", "Valor": peligros_criticos}
    ], "indicadores")
    st.download_button("📥 Exportar Indicadores", data=excel_data, file_name=f"indicadores_{datetime.now().strftime('%Y%m%d')}.xlsx")

# ========== CHAT IA ==========
elif menu == "💬 Chat IA":
    st.markdown('<div class="main-header"><h1>💬 Chat IA</h1><p>Asistente virtual especializado en SST</p></div>', unsafe_allow_html=True)
    
    if "chat_messages" not in st.session_state:
        st.session_state.chat_messages = [{"role": "assistant", "content": f"Hola, soy tu asistente SST. Uso {len(GEMINI_KEYS)} keys de Gemini y Groq como respaldo. ¿En qué puedo ayudarte?"}]
    
    for msg in st.session_state.chat_messages:
        with st.chat_message(msg["role"]):
            st.write(msg["content"])
    
    if prompt := st.chat_input("Escribe tu pregunta sobre SST..."):
        st.session_state.chat_messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.write(prompt)
        
        with st.chat_message("assistant"):
            with st.spinner("🤖 IA analizando tu consulta..."):
                respuesta = call_best_ia(f"Eres un experto en Seguridad y Salud en el Trabajo (SST) en Colombia. Responde de forma clara y profesional: {prompt}")
                st.write(respuesta)
                st.session_state.chat_messages.append({"role": "assistant", "content": respuesta})

st.markdown("---")
st.markdown("<p style='text-align:center; font-size:11px; color:rgba(255,255,255,0.4)'>🔄 SG-SST PHVA | Sistema de Gestión PHVA con IA | Desarrollado por JAN BENITEZ</p>", unsafe_allow_html=True)

# FINAL - 06/11/2026 08:38:39


# FIX - 06/11/2026 08:39:12
