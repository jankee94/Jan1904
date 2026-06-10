import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import io
import json
import random

st.set_page_config(
    page_title="SG-SST PHVA",
    page_icon="🔄",
    layout="wide",
    initial_sidebar_state="expanded"
)

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

# ========== INICIALIZAR DATOS EN SESSION STATE ==========
def init_session_state():
    """Inicializar datos de ejemplo en session state"""
    
    # Usuarios
    if "usuarios" not in st.session_state:
        st.session_state.usuarios = [
            {"id": 1, "nombre": "Administrador", "email": "admin@sg-sst.com", "rol": "admin", "activo": True}
        ]
    
    # Empresa
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
            {"id": 1, "tipo": "Físico", "descripcion": "Ruido excesivo en zona de maquinaria", "probabilidad": 4, "severidad": 3, "nivel": "I", "fecha": "2024-01-15"},
            {"id": 2, "tipo": "Ergonómico", "descripcion": "Posturas forzadas en oficinas", "probabilidad": 3, "severidad": 2, "nivel": "II", "fecha": "2024-01-20"},
            {"id": 3, "tipo": "Químico", "descripcion": "Exposición a solventes", "probabilidad": 2, "severidad": 3, "nivel": "I", "fecha": "2024-02-01"},
            {"id": 4, "tipo": "Psicosocial", "descripcion": "Estrés laboral", "probabilidad": 3, "severidad": 2, "nivel": "II", "fecha": "2024-02-10"},
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
            {"id": 2, "titulo": "Primeros Auxilios", "fecha": "2024-11-25", "duracion": 4, "participantes": 20, "estado": "Programada"},
            {"id": 3, "titulo": "Manejo de Extintores", "fecha": "2024-12-05", "duracion": 4, "participantes": 25, "estado": "Programada"},
        ]
    
    # Inspecciones
    if "inspecciones" not in st.session_state:
        st.session_state.inspecciones = [
            {"id": 1, "tipo": "Locativa", "ubicacion": "Planta Principal", "fecha": "2024-11-10", "hallazgos": 3, "estado": "Completada"},
            {"id": 2, "tipo": "Equipos", "ubicacion": "Taller Mecánico", "fecha": "2024-11-20", "hallazgos": 2, "estado": "En progreso"},
        ]
    
    # Emergencias
    if "emergencias" not in st.session_state:
        st.session_state.emergencias = {
            "brigadistas": [
                {"nombre": "Carlos López", "tipo": "Primeros Auxilios", "certificado": "2025-06-01"},
                {"nombre": "María Gómez", "tipo": "Contra Incendios", "certificado": "2025-06-01"},
            ],
            "equipos": [
                {"tipo": "Extintor PQS", "ubicacion": "Planta", "estado": "Operativo"},
                {"tipo": "Botiquín", "ubicacion": "Oficinas", "estado": "Operativo"},
            ]
        }
    
    # Documentos
    if "documentos" not in st.session_state:
        st.session_state.documentos = [
            {"id": 1, "titulo": "Política SST", "codigo": "POL-SST-001", "version": "1.0", "fecha_vencimiento": "2025-12-31"},
            {"id": 2, "titulo": "Matriz de Riesgos", "codigo": "MAT-RIS-001", "version": "2.0", "fecha_vencimiento": "2025-06-30"},
        ]

# ========== FUNCIONES DE AYUDA ==========
def get_nivel_color(nivel):
    colores = {"I": "#e74c3c", "II": "#f39c12", "III": "#27ae60"}
    return colores.get(nivel, "#95a5a6")

def exportar_excel(data, nombre):
    df = pd.DataFrame(data)
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, sheet_name=nombre, index=False)
    return output.getvalue()

# ========== LOGIN ==========
if "auth" not in st.session_state:
    st.session_state.auth = False
if "current_user" not in st.session_state:
    st.session_state.current_user = None

if not st.session_state.auth:
    col1, col2, col3 = st.columns([1, 1.5, 1])
    with col2:
        st.markdown('''
        <div style="background: rgba(20,20,40,0.8); backdrop-filter: blur(14px); border-radius: 28px; padding: 40px; text-align:center">
            <img src="https://cdn-icons-png.flaticon.com/512/2917/2917995.png" width="70">
            <h1 style="color:white;">SG-SST PHVA</h1>
            <p style="color:rgba(255,255,255,0.6)">Sistema de Gestión en Seguridad y Salud en el Trabajo</p>
            <p style="color:rgba(255,255,255,0.4); font-size:12px">Módulos completos: Peligros | Inspecciones | Emergencias | Capacitaciones | Documentos | Indicadores</p>
        </div>
        ''', unsafe_allow_html=True)
        
        with st.form("login_form"):
            username = st.text_input("Usuario", placeholder="admin")
            password = st.text_input("Contraseña", type="password", placeholder="admin123")
            
            if st.form_submit_button("🚀 INGRESAR", use_container_width=True):
                if username == "admin" and password == "admin123":
                    st.session_state.auth = True
                    st.session_state.current_user = {"nombre": "Administrador", "rol": "admin"}
                    init_session_state()
                    st.rerun()
                else:
                    st.error("❌ Usuario o contraseña incorrectos")
        
        st.markdown('<p style="text-align:center; font-size:11px; color:gray; margin-top:20px">SG-SST PHVA | Desarrollado por JAN BENITEZ</p>', unsafe_allow_html=True)
    st.stop()

# Inicializar datos si no existen
init_session_state()

# ========== SIDEBAR ==========
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
    st.markdown('<div class="main-header"><h1>📊 Dashboard SST</h1><p>Resumen ejecutivo del Sistema de Gestión</p></div>', unsafe_allow_html=True)
    
    # KPIs
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
    st.markdown('<div class="main-header"><h1>⚠️ Gestión de Peligros</h1><p>Matriz de identificación y evaluación de riesgos</p></div>', unsafe_allow_html=True)
    
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
            prob = st.slider("Probabilidad (1-4)", 1, 4, 2)
            sev = st.slider("Severidad (1-3)", 1, 3, 2)
            
            nivel = "I" if prob * sev >= 6 else "II" if prob * sev >= 4 else "III"
            st.markdown(f"**Nivel de Riesgo:** <span class='{'danger-badge' if nivel=='I' else 'warning-badge' if nivel=='II' else 'success-badge'}'>Nivel {nivel}</span>", unsafe_allow_html=True)
            
            if st.form_submit_button("Guardar"):
                nuevo_id = max([p["id"] for p in st.session_state.peligros]) + 1 if st.session_state.peligros else 1
                st.session_state.peligros.append({
                    "id": nuevo_id, "tipo": tipo, "descripcion": descripcion,
                    "probabilidad": prob, "severidad": sev, "nivel": nivel,
                    "fecha": datetime.now().strftime("%Y-%m-%d")
                })
                st.success("✅ Peligro guardado")
                st.rerun()

# ========== PLAN DE ACCIÓN ==========
elif menu == "✅ Plan de Acción":
    st.markdown('<div class="main-header"><h1>✅ Plan de Acción</h1><p>Seguimiento de acciones correctivas y preventivas</p></div>', unsafe_allow_html=True)
    
    tab1, tab2 = st.tabs(["📋 Lista", "➕ Nueva"])
    
    with tab1:
        for accion in st.session_state.acciones:
            col1, col2 = st.columns([3, 1])
            with col1:
                st.markdown(f"**{accion['descripcion']}**")
                st.caption(f"Responsable: {accion['responsable']} | Límite: {accion['fecha_limite']} | Prioridad: {accion['prioridad']}")
            with col2:
                estados = ["Pendiente", "En progreso", "Completada"]
                nuevo_estado = st.selectbox("Estado", estados, index=estados.index(accion["estado"]), key=f"estado_{accion['id']}")
                if nuevo_estado != accion["estado"]:
                    accion["estado"] = nuevo_estado
                    st.rerun()
            st.markdown("---")
        
        excel_data = exportar_excel(st.session_state.acciones, "acciones")
        st.download_button("📥 Exportar a Excel", data=excel_data, file_name=f"plan_accion_{datetime.now().strftime('%Y%m%d')}.xlsx")
    
    with tab2:
        with st.form("add_accion"):
            desc = st.text_area("Descripción")
            resp = st.text_input("Responsable")
            fecha = st.date_input("Fecha límite", datetime.now())
            prioridad = st.selectbox("Prioridad", ["Alta", "Media", "Baja"])
            
            if st.form_submit_button("Guardar"):
                nuevo_id = max([a["id"] for a in st.session_state.acciones]) + 1 if st.session_state.acciones else 1
                st.session_state.acciones.append({
                    "id": nuevo_id, "descripcion": desc, "responsable": resp,
                    "fecha_limite": fecha.strftime("%Y-%m-%d"), "estado": "Pendiente", "prioridad": prioridad
                })
                st.success("✅ Acción guardada")
                st.rerun()

# ========== TRABAJADORES ==========
elif menu == "👥 Trabajadores":
    st.markdown('<div class="main-header"><h1>👥 Trabajadores</h1><p>Gestión del personal</p></div>', unsafe_allow_html=True)
    
    df = pd.DataFrame(st.session_state.trabajadores)
    st.dataframe(df, use_container_width=True)
    excel_data = exportar_excel(st.session_state.trabajadores, "trabajadores")
    st.download_button("📥 Exportar a Excel", data=excel_data, file_name=f"trabajadores_{datetime.now().strftime('%Y%m%d')}.xlsx")

# ========== INCIDENTES ==========
elif menu == "📝 Incidentes":
    st.markdown('<div class="main-header"><h1>📝 Incidentes</h1><p>Registro de accidentes e incidentes laborales</p></div>', unsafe_allow_html=True)
    
    tab1, tab2 = st.tabs(["📋 Historial", "➕ Reportar"])
    
    with tab1:
        df = pd.DataFrame(st.session_state.incidentes)
        st.dataframe(df, use_container_width=True)
        excel_data = exportar_excel(st.session_state.incidentes, "incidentes")
        st.download_button("📥 Exportar a Excel", data=excel_data, file_name=f"incidentes_{datetime.now().strftime('%Y%m%d')}.xlsx")
    
    with tab2:
        with st.form("add_incidente"):
            desc = st.text_area("Descripción")
            fecha = st.date_input("Fecha", datetime.now())
            tipo = st.selectbox("Tipo", ["Accidente", "Incidente", "Enfermedad Laboral"])
            gravedad = st.selectbox("Gravedad", ["Leve", "Moderada", "Grave", "Mortal"])
            causa = st.text_area("Causa probable")
            
            if st.form_submit_button("Reportar"):
                nuevo_id = max([i["id"] for i in st.session_state.incidentes]) + 1 if st.session_state.incidentes else 1
                st.session_state.incidentes.append({
                    "id": nuevo_id, "descripcion": desc, "fecha": fecha.strftime("%Y-%m-%d"),
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
        col1, col2, col3 = st.columns([2, 1, 1])
        with col1:
            st.write(f"**{req['norma']} - {req['articulo']}**")
            st.caption(req['requisito'])
        with col2:
            cumple = st.checkbox("Cumple", value=req["cumple"], key=f"cumple_{req['articulo']}")
        with col3:
            if cumple:
                st.markdown('<span class="success-badge">✅ Cumple</span>', unsafe_allow_html=True)
            else:
                st.markdown('<span class="danger-badge">❌ No cumple</span>', unsafe_allow_html=True)
        st.markdown("---")

# ========== AUDITORÍAS ==========
elif menu == "🔍 Auditorías":
    st.markdown('<div class="main-header"><h1>🔍 Auditorías Internas</h1><p>Planificación y ejecución de auditorías SST</p></div>', unsafe_allow_html=True)
    
    with st.form("add_auditoria"):
        col1, col2 = st.columns(2)
        with col1:
            codigo = st.text_input("Código", "AUD-001")
            fecha = st.date_input("Fecha", datetime.now())
        with col2:
            auditor = st.text_input("Auditor líder")
            
        if st.form_submit_button("Crear Auditoría"):
            st.success(f"✅ Auditoría {codigo} creada")

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
            participantes = st.number_input("Participantes", min_value=1, value=20)
            
            if st.form_submit_button("Programar"):
                nuevo_id = max([c["id"] for c in st.session_state.capacitaciones]) + 1 if st.session_state.capacitaciones else 1
                st.session_state.capacitaciones.append({
                    "id": nuevo_id, "titulo": titulo, "fecha": fecha.strftime("%Y-%m-%d"),
                    "duracion": duracion, "participantes": participantes, "estado": "Programada"
                })
                st.success("✅ Capacitación programada")
                st.rerun()

# ========== INSPECCIONES ==========
elif menu == "🔧 Inspecciones":
    st.markdown('<div class="main-header"><h1>🔧 Inspecciones</h1><p>Inspecciones locativas, equipos y EPP</p></div>', unsafe_allow_html=True)
    
    tab1, tab2 = st.tabs(["📋 Historial", "➕ Nueva"])
    
    with tab1:
        df = pd.DataFrame(st.session_state.inspecciones)
        st.dataframe(df, use_container_width=True)
    
    with tab2:
        with st.form("add_inspeccion"):
            tipo = st.selectbox("Tipo", ["Locativa", "Equipos", "EPP", "Vehicular", "Andamios"])
            ubicacion = st.text_input("Ubicación")
            fecha = st.date_input("Fecha", datetime.now())
            
            if st.form_submit_button("Iniciar Inspección"):
                nuevo_id = max([i["id"] for i in st.session_state.inspecciones]) + 1 if st.session_state.inspecciones else 1
                st.session_state.inspecciones.append({
                    "id": nuevo_id, "tipo": tipo, "ubicacion": ubicacion,
                    "fecha": fecha.strftime("%Y-%m-%d"), "hallazgos": 0, "estado": "Programada"
                })
                st.success("✅ Inspección programada")
                st.rerun()

# ========== EMERGENCIAS ==========
elif menu == "🚨 Emergencias":
    st.markdown('<div class="main-header"><h1>🚨 Emergencias</h1><p>Brigadistas, equipos y plan de emergencia</p></div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("👥 Brigadistas")
        for b in st.session_state.emergencias["brigadistas"]:
            st.write(f"**{b['nombre']}** - {b['tipo']}")
            st.caption(f"Certificado vigente hasta: {b['certificado']}")
            st.markdown("---")
    
    with col2:
        st.subheader("🛠️ Equipos de Emergencia")
        for e in st.session_state.emergencias["equipos"]:
            estado_color = "success-badge" if e['estado'] == "Operativo" else "danger-badge"
            st.write(f"**{e['tipo']}**")
            st.write(f"Ubicación: {e['ubicacion']}")
            st.markdown(f"Estado: <span class='{estado_color}'>{e['estado']}</span>", unsafe_allow_html=True)
            st.markdown("---")

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
            
            if st.button("📥 Descargar", key=f"desc_{doc['id']}"):
                st.info("Documento disponible para descarga")

# ========== INDICADORES ==========
elif menu == "📊 Indicadores":
    st.markdown('<div class="main-header"><h1>📊 Indicadores SST</h1><p>Dashboard ejecutivo de indicadores clave</p></div>', unsafe_allow_html=True)
    
    # Calcular indicadores
    total_incidentes = len(st.session_state.incidentes)
    total_trabajadores = len(st.session_state.trabajadores)
    acciones_completadas = len([a for a in st.session_state.acciones if a["estado"] == "Completada"])
    total_acciones = len(st.session_state.acciones)
    
    tasa_accidentalidad = (total_incidentes * 100 / total_trabajadores) if total_trabajadores > 0 else 0
    cumplimiento_phva = (acciones_completadas * 100 / total_acciones) if total_acciones > 0 else 0
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Índice de Frecuencia", f"{tasa_accidentalidad:.1f}", delta="vs 5%")
    with col2:
        st.metric("Cumplimiento PHVA", f"{cumplimiento_phva:.0f}%", delta="Meta 80%")
    with col3:
        st.metric("Peligros Identificados", len(st.session_state.peligros))
    with col4:
        capacitaciones_realizadas = len([c for c in st.session_state.capacitaciones if c["estado"] == "Finalizada"])
        st.metric("Capacitaciones", f"{capacitaciones_realizadas}/{len(st.session_state.capacitaciones)}")
    
    st.markdown("---")
    
    # Gráfico de tendencia
    st.subheader("📈 Tendencia de Incidentes")
    incidentes_por_mes = {}
    for inc in st.session_state.incidentes:
        mes = inc["fecha"][:7]
        incidentes_por_mes[mes] = incidentes_por_mes.get(mes, 0) + 1
    
    if incidentes_por_mes:
        fig = go.Figure(data=[go.Scatter(x=list(incidentes_por_mes.keys()), y=list(incidentes_por_mes.values()), mode='lines+markers')])
        fig.update_layout(height=300, title="Incidentes reportados por mes")
        st.plotly_chart(fig, use_container_width=True)

# ========== CHAT IA ==========
elif menu == "💬 Chat IA":
    st.markdown('<div class="main-header"><h1>💬 Chat IA</h1><p>Asistente virtual para consultas SST</p></div>', unsafe_allow_html=True)
    
    if "chat_messages" not in st.session_state:
        st.session_state.chat_messages = [{"role": "assistant", "content": "Hola, soy tu asistente SST. ¿En qué puedo ayudarte?"}]
    
    for msg in st.session_state.chat_messages:
        with st.chat_message(msg["role"]):
            st.write(msg["content"])
    
    if prompt := st.chat_input("Escribe tu pregunta sobre SST..."):
        st.session_state.chat_messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.write(prompt)
        
        # Respuestas predefinidas
        respuestas = {
            "peligro": "Los peligros se clasifican en: Físicos, Químicos, Biológicos, Ergonómicos, Psicosociales y de Seguridad.",
            "incidente": "Todo incidente debe ser investigado para identificar causas básicas e inmediatas.",
            "capacitacion": "Las capacitaciones en SST deben programarse mínimo una vez al año según normativa.",
            "norma": "Las normas aplicables son ISO 45001:2018 y Decreto 1072 de 2015.",
            "default": "Para más información, consulta la Matriz Legal o contacta al área SST."
        }
        
        respuesta = "No tengo información específica sobre eso."
        for key, value in respuestas.items():
            if key in prompt.lower():
                respuesta = value
                break
        
        with st.chat_message("assistant"):
            st.write(respuesta)
            st.session_state.chat_messages.append({"role": "assistant", "content": respuesta})

st.markdown("---")
st.markdown("<p style='text-align:center; font-size:11px; color:rgba(255,255,255,0.4)'>🔄 SG-SST PHVA | Sistema de Gestión PHVA con IA | Desarrollado por JAN BENITEZ</p>", unsafe_allow_html=True)
