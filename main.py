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

# ========== INICIALIZAR DATOS ==========
def init_session_state():
    if "usuarios" not in st.session_state:
        st.session_state.usuarios = [{"id": 1, "nombre": "Administrador", "email": "admin@sg-sst.com", "rol": "admin"}]
    
    if "empresa" not in st.session_state:
        st.session_state.empresa = {
            "nombre": "Constructora Segura SAS", "nit": "901.234.567-8",
            "ubicacion": "Calle 80 #45-67, Bogota", "sector": "Construccion",
            "telefono": "6015551234", "email": "sst@constructora.com"
        }
    
    if "peligros" not in st.session_state:
        st.session_state.peligros = [
            {"id": 1, "tipo": "Fisico", "descripcion": "Ruido excesivo", "probabilidad": 4, "severidad": 3, "nivel": "I", "fecha": "2024-01-15"},
            {"id": 2, "tipo": "Ergonomico", "descripcion": "Posturas forzadas", "probabilidad": 3, "severidad": 2, "nivel": "II", "fecha": "2024-01-20"},
        ]
    
    if "acciones" not in st.session_state:
        st.session_state.acciones = [
            {"id": 1, "descripcion": "Implementar barreras acusticas", "responsable": "Coordinador SST", "fecha_limite": "2024-12-15", "estado": "En progreso", "prioridad": "Alta"},
            {"id": 2, "descripcion": "Capacitacion en pausas activas", "responsable": "SST", "fecha_limite": "2024-11-30", "estado": "Pendiente", "prioridad": "Media"},
        ]
    
    if "trabajadores" not in st.session_state:
        st.session_state.trabajadores = [
            {"id": 1, "nombre": "Carlos Lopez", "cedula": "12345678", "cargo": "Operario", "area": "Produccion", "eps": "Sura", "arl": "Positiva"},
            {"id": 2, "nombre": "Maria Gomez", "cedula": "87654321", "cargo": "Supervisor", "area": "Produccion", "eps": "Sura", "arl": "Positiva"},
        ]
    
    if "incidentes" not in st.session_state:
        st.session_state.incidentes = [
            {"id": 1, "descripcion": "Caida desde andamio", "fecha": "2024-10-15", "gravedad": "Grave", "tipo": "Accidente", "causa": "Falta de barandas"},
            {"id": 2, "descripcion": "Corte con herramienta", "fecha": "2024-10-20", "gravedad": "Leve", "tipo": "Incidente", "causa": "Falta de entrenamiento"},
        ]
    
    if "capacitaciones" not in st.session_state:
        st.session_state.capacitaciones = [
            {"id": 1, "titulo": "Trabajo en Alturas", "fecha": "2024-11-15", "duracion": 8, "participantes": 15, "estado": "Finalizada", "asistentes": [], "certificados": []},
            {"id": 2, "titulo": "Primeros Auxilios", "fecha": "2024-11-25", "duracion": 4, "participantes": 0, "estado": "Programada", "asistentes": [], "certificados": []},
        ]
    
    if "inspecciones" not in st.session_state:
        st.session_state.inspecciones = []
    
    if "emergencias" not in st.session_state:
        st.session_state.emergencias = {
            "brigadistas": [
                {"nombre": "Carlos Lopez", "tipo": "Primeros Auxilios", "telefono": "3001234567", "certificado": "2025-06-01"},
                {"nombre": "Maria Gomez", "tipo": "Contra Incendios", "telefono": "3001234568", "certificado": "2025-06-01"},
            ],
            "equipos": [
                {"tipo": "Extintor PQS", "ubicacion": "Planta Principal", "estado": "Operativo", "vencimiento": "2025-12-31"},
                {"tipo": "Botiquin Tipo A", "ubicacion": "Oficinas", "estado": "Operativo", "vencimiento": "2025-06-30"},
            ],
            "alertas": []
        }
    
    if "documentos" not in st.session_state:
        st.session_state.documentos = [
            {"id": 1, "titulo": "Politica SST", "codigo": "POL-SST-001", "version": "1.0", "fecha_vencimiento": "2025-12-31", "historial": []},
            {"id": 2, "titulo": "Matriz de Riesgos", "codigo": "MAT-RIS-001", "version": "2.0", "fecha_vencimiento": "2025-06-30", "historial": []},
        ]

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
            <p style="color:rgba(255,255,255,0.6)">Sistema de Gestion en Seguridad y Salud en el Trabajo</p>
        </div>
        ''', unsafe_allow_html=True)
        
        with st.form("login_form"):
            username = st.text_input("Usuario", placeholder="admin")
            password = st.text_input("Contraseña", type="password", placeholder="admin123")
            if st.form_submit_button("INGRESAR", use_container_width=True):
                if username == "admin" and password == "admin123":
                    st.session_state.auth = True
                    st.session_state.current_user = {"nombre": "Administrador", "rol": "admin"}
                    init_session_state()
                    st.rerun()
                else:
                    st.error("Usuario o contraseña incorrectos")
        
        st.markdown('<p style="text-align:center; font-size:11px; color:gray">SG-SST PHVA | Desarrollado por JAN BENITEZ</p>', unsafe_allow_html=True)
    st.stop()

init_session_state()

# ========== SIDEBAR ==========
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/2917/2917995.png", width=50)
    st.markdown(f"### {st.session_state.current_user.get('nombre', 'Usuario')}")
    st.markdown("---")
    
    menu = st.radio("MODULOS", [
        "Dashboard", "Empresa", "Peligros", "Plan de Accion", "Trabajadores",
        "Incidentes", "Matriz Legal", "Auditorias", "Capacitaciones",
        "Inspecciones", "Emergencias", "Documentos", "Indicadores", "Chat IA"
    ])
    
    if st.button("Cerrar Sesion", use_container_width=True):
        st.session_state.auth = False
        st.rerun()

# ========== DASHBOARD ==========
if menu == "Dashboard":
    st.markdown('<div class="main-header"><h1>Dashboard SST</h1><p>Resumen ejecutivo del Sistema de Gestion</p></div>', unsafe_allow_html=True)
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Peligros", len(st.session_state.peligros))
    with col2:
        completadas = len([a for a in st.session_state.acciones if a["estado"] == "Completada"])
        st.metric("Acciones", f"{completadas}/{len(st.session_state.acciones)}")
    with col3:
        st.metric("Trabajadores", len(st.session_state.trabajadores))
    with col4:
        st.metric("Incidentes", len(st.session_state.incidentes))

# ========== EMPRESA ==========
elif menu == "Empresa":
    st.markdown('<div class="main-header"><h1>Configuracion de la Empresa</h1></div>', unsafe_allow_html=True)
    with st.form("empresa_form"):
        col1, col2 = st.columns(2)
        with col1:
            nombre = st.text_input("Nombre", value=st.session_state.empresa["nombre"])
            nit = st.text_input("NIT", value=st.session_state.empresa["nit"])
        with col2:
            ubicacion = st.text_input("Ubicacion", value=st.session_state.empresa["ubicacion"])
            sector = st.text_input("Sector", value=st.session_state.empresa["sector"])
        if st.form_submit_button("Guardar"):
            st.session_state.empresa = {"nombre": nombre, "nit": nit, "ubicacion": ubicacion, "sector": sector}
            st.success("Datos guardados")

# ========== PELIGROS ==========
elif menu == "Peligros":
    st.markdown('<div class="main-header"><h1>Gestion de Peligros</h1></div>', unsafe_allow_html=True)
    df = pd.DataFrame(st.session_state.peligros)
    st.dataframe(df, use_container_width=True)
    excel_data = exportar_excel(st.session_state.peligros, "peligros")
    st.download_button("Exportar a Excel", data=excel_data, file_name=f"peligros_{datetime.now().strftime('%Y%m%d')}.xlsx")

# ========== PLAN DE ACCION ==========
elif menu == "Plan de Accion":
    st.markdown('<div class="main-header"><h1>Plan de Accion</h1></div>', unsafe_allow_html=True)
    for accion in st.session_state.acciones:
        with st.expander(f"{accion['descripcion']}"):
            st.write(f"Responsable: {accion['responsable']}")
            st.write(f"Fecha limite: {accion['fecha_limite']}")
            estados = ["Pendiente", "En progreso", "Completada"]
            nuevo = st.selectbox("Estado", estados, index=estados.index(accion["estado"]), key=f"estado_{accion['id']}")
            if nuevo != accion["estado"]:
                accion["estado"] = nuevo
                st.rerun()
    excel_data = exportar_excel(st.session_state.acciones, "acciones")
    st.download_button("Exportar a Excel", data=excel_data, file_name=f"acciones_{datetime.now().strftime('%Y%m%d')}.xlsx")

# ========== TRABAJADORES ==========
elif menu == "Trabajadores":
    st.markdown('<div class="main-header"><h1>Trabajadores</h1></div>', unsafe_allow_html=True)
    df = pd.DataFrame(st.session_state.trabajadores)
    st.dataframe(df, use_container_width=True)
    excel_data = exportar_excel(st.session_state.trabajadores, "trabajadores")
    st.download_button("Exportar a Excel", data=excel_data, file_name=f"trabajadores_{datetime.now().strftime('%Y%m%d')}.xlsx")

# ========== INCIDENTES ==========
elif menu == "Incidentes":
    st.markdown('<div class="main-header"><h1>Incidentes</h1></div>', unsafe_allow_html=True)
    df = pd.DataFrame(st.session_state.incidentes)
    st.dataframe(df, use_container_width=True)
    excel_data = exportar_excel(st.session_state.incidentes, "incidentes")
    st.download_button("Exportar a Excel", data=excel_data, file_name=f"incidentes_{datetime.now().strftime('%Y%m%d')}.xlsx")

# ========== MATRIZ LEGAL ==========
elif menu == "Matriz Legal":
    st.markdown('<div class="main-header"><h1>Matriz Legal</h1><p>ISO 45001 + Decreto 1072</p></div>', unsafe_allow_html=True)
    requisitos = [
        {"norma": "ISO 45001", "articulo": "4.1", "requisito": "Comprender la organizacion", "cumple": False},
        {"norma": "ISO 45001", "articulo": "5.2", "requisito": "Politica de SST", "cumple": False},
        {"norma": "Decreto 1072", "articulo": "2.2.4.6.22", "requisito": "Conformar COPASST", "cumple": False},
    ]
    for req in requisitos:
        col1, col2 = st.columns([3,1])
        with col1:
            st.write(f"**{req['norma']} - {req['articulo']}**")
            st.caption(req['requisito'])
        with col2:
            cumple = st.checkbox("Cumple", value=req["cumple"], key=req['articulo'])
            if cumple:
                st.markdown('<span class="success-badge">Cumple</span>', unsafe_allow_html=True)

# ========== AUDITORIAS ==========
elif menu == "Auditorias":
    st.markdown('<div class="main-header"><h1>Auditorias Internas</h1></div>', unsafe_allow_html=True)
    with st.form("add_auditoria"):
        codigo = st.text_input("Codigo", "AUD-001")
        fecha = st.date_input("Fecha", datetime.now())
        if st.form_submit_button("Crear Auditoria"):
            st.success(f"Auditoria {codigo} creada")

# ========== CAPACITACIONES ==========
elif menu == "Capacitaciones":
    st.markdown('<div class="main-header"><h1>Capacitaciones</h1><p>Gestion de capacitaciones y certificados</p></div>', unsafe_allow_html=True)
    
    tab1, tab2 = st.tabs(["Programadas", "Nueva"])
    
    with tab1:
        for cap in st.session_state.capacitaciones:
            with st.expander(f"{cap['titulo']} - {cap['fecha']}"):
                st.write(f"Duracion: {cap['duracion']} horas")
                st.write(f"Participantes: {cap['participantes']}")
                
                if cap['estado'] == "Programada":
                    with st.form(key=f"asis_{cap['id']}"):
                        nombre = st.text_input("Nombre participante")
                        if st.form_submit_button("Registrar Asistencia"):
                            if "asistentes" not in cap:
                                cap["asistentes"] = []
                            cap["asistentes"].append({"nombre": nombre, "fecha": datetime.now().strftime("%Y-%m-%d")})
                            cap["participantes"] = len(cap["asistentes"])
                            st.success(f"Asistencia registrada")
                            st.rerun()
                        
                        if st.form_submit_button("Generar Certificado"):
                            if nombre:
                                cap["certificados"] = cap.get("certificados", [])
                                cap["certificados"].append({"nombre": nombre, "fecha": datetime.now().strftime("%Y-%m-%d")})
                                st.success(f"Certificado generado para {nombre}")
                                st.balloons()
    
    with tab2:
        with st.form("add_capacitacion"):
            titulo = st.text_input("Titulo")
            fecha = st.date_input("Fecha", datetime.now())
            duracion = st.number_input("Duracion (horas)", min_value=1, value=8)
            if st.form_submit_button("Programar"):
                nuevo_id = len(st.session_state.capacitaciones) + 1
                st.session_state.capacitaciones.append({
                    "id": nuevo_id, "titulo": titulo, "fecha": fecha.strftime("%Y-%m-%d"),
                    "duracion": duracion, "participantes": 0, "estado": "Programada",
                    "asistentes": [], "certificados": []
                })
                st.success("Capacitacion programada")
                st.rerun()

# ========== INSPECCIONES ==========
elif menu == "Inspecciones":
    st.markdown('<div class="main-header"><h1>Inspecciones</h1><p>Checklists predefinidos</p></div>', unsafe_allow_html=True)
    
    checklists = {
        "Locativa": ["Pisos en buen estado", "Techos sin filtraciones", "Puertas operativas", "Escaleras con barandas"],
        "Equipos": ["Guardas de seguridad", "Sistema electrico", "Boton de paro", "Manuales disponibles"],
        "EPP": ["Casco de seguridad", "Gafas protectoras", "Guantes", "Botas de seguridad"]
    }
    
    with st.form("add_inspeccion"):
        tipo = st.selectbox("Tipo", list(checklists.keys()))
        ubicacion = st.text_input("Ubicacion")
        
        st.subheader("Checklist")
        resultados = {}
        for item in checklists[tipo]:
            resultados[item] = st.checkbox(item)
        
        if st.form_submit_button("Completar Inspeccion"):
            hallazgos = [item for item, cumple in resultados.items() if not cumple]
            calificacion = ((len(checklists[tipo]) - len(hallazgos)) / len(checklists[tipo])) * 100
            
            st.session_state.inspecciones.append({
                "tipo": tipo, "ubicacion": ubicacion, "fecha": datetime.now().strftime("%Y-%m-%d"),
                "hallazgos": len(hallazgos), "calificacion": f"{calificacion:.0f}%"
            })
            
            if hallazgos:
                st.warning(f"Hallazgos: {', '.join(hallazgos)}")
                st.session_state.acciones.append({
                    "id": len(st.session_state.acciones) + 1,
                    "descripcion": f"Corregir: {hallazgos[0]}",
                    "responsable": "Inspector",
                    "fecha_limite": (datetime.now().replace(day=datetime.now().day + 15)).strftime("%Y-%m-%d"),
                    "estado": "Pendiente", "prioridad": "Alta"
                })
            st.success(f"Inspeccion completada - Calificacion: {calificacion:.0f}%")
            st.rerun()

# ========== EMERGENCIAS ==========
elif menu == "Emergencias":
    st.markdown('<div class="main-header"><h1>Emergencias</h1><p>Brigadistas, equipos y alertas</p></div>', unsafe_allow_html=True)
    
    tab1, tab2, tab3 = st.tabs(["Brigadistas", "Equipos", "Alertas"])
    
    with tab1:
        for b in st.session_state.emergencias["brigadistas"]:
            st.write(f"**{b['nombre']}** - {b['tipo']}")
            st.caption(f"Telefono: {b['telefono']} | Certificado: {b['certificado']}")
            st.markdown("---")
    
    with tab2:
        for e in st.session_state.emergencias["equipos"]:
            st.write(f"**{e['tipo']}** - {e['ubicacion']}")
            st.caption(f"Estado: {e['estado']} | Mantenimiento: {e['vencimiento']}")
            st.markdown("---")
    
    with tab3:
        with st.form("activar_alerta"):
            tipo = st.selectbox("Tipo", ["Incendio", "Sismo", "Evacuacion", "Emergencia Medica"])
            ubicacion = st.text_input("Ubicacion")
            if st.form_submit_button("Activar Alerta", use_container_width=True):
                st.session_state.emergencias["alertas"].append({
                    "tipo": tipo, "ubicacion": ubicacion, "fecha": datetime.now().strftime("%Y-%m-%d %H:%M"), "estado": "Activa"
                })
                st.error("ALERTA DE EMERGENCIA ACTIVADA")
                st.balloons()
                st.rerun()
        
        for a in st.session_state.emergencias["alertas"]:
            if a["estado"] == "Activa":
                st.warning(f"{a['tipo']} - {a['ubicacion']} - {a['fecha']}")

# ========== DOCUMENTOS ==========
elif menu == "Documentos":
    st.markdown('<div class="main-header"><h1>Gestion Documental</h1><p>Control de versiones</p></div>', unsafe_allow_html=True)
    
    for doc in st.session_state.documentos:
        with st.expander(f"{doc['titulo']} - v{doc['version']}"):
            st.write(f"**Codigo:** {doc['codigo']}")
            st.write(f"**Vence:** {doc['fecha_vencimiento']}")
            
            nueva_version = st.text_input("Nueva version", key=f"ver_{doc['id']}")
            cambios = st.text_area("Cambios", key=f"cam_{doc['id']}")
            
            if st.button("Crear Version", key=f"btn_{doc['id']}"):
                if nueva_version and cambios:
                    doc["historial"].append({"version": doc["version"], "cambios": cambios})
                    doc["version"] = nueva_version
                    st.success(f"Nueva version {nueva_version} creada")
                    st.rerun()

# ========== INDICADORES ==========
elif menu == "Indicadores":
    st.markdown('<div class="main-header"><h1>Indicadores SST</h1><p>KPIs automaticos</p></div>', unsafe_allow_html=True)
    
    total_trabajadores = len(st.session_state.trabajadores)
    total_incidentes = len(st.session_state.incidentes)
    acciones_completadas = len([a for a in st.session_state.acciones if a["estado"] == "Completada"])
    total_acciones = len(st.session_state.acciones)
    
    tasa = (total_incidentes * 100 / total_trabajadores) if total_trabajadores > 0 else 0
    cumplimiento = (acciones_completadas * 100 / total_acciones) if total_acciones > 0 else 0
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Indice de Frecuencia", f"{tasa:.1f}%")
    with col2:
        st.metric("Cumplimiento PHVA", f"{cumplimiento:.0f}%")
    with col3:
        st.metric("Total Peligros", len(st.session_state.peligros))
    with col4:
        st.metric("Incidentes", total_incidentes)
    
    excel_data = exportar_excel([{"Indicador": "Frecuencia", "Valor": f"{tasa:.1f}%"}], "indicadores")
    st.download_button("Exportar Indicadores", data=excel_data, file_name=f"indicadores_{datetime.now().strftime('%Y%m%d')}.xlsx")

# ========== CHAT IA ==========
elif menu == "Chat IA":
    st.markdown('<div class="main-header"><h1>Chat IA</h1><p>Asistente virtual SST</p></div>', unsafe_allow_html=True)
    
    if "chat_messages" not in st.session_state:
        st.session_state.chat_messages = [{"role": "assistant", "content": "Hola, soy tu asistente SST. ¿En que puedo ayudarte?"}]
    
    for msg in st.session_state.chat_messages:
        with st.chat_message(msg["role"]):
            st.write(msg["content"])
    
    if prompt := st.chat_input("Pregunta sobre SST..."):
        st.session_state.chat_messages.append({"role": "user", "content": prompt})
        
        respuestas = {
            "peligro": "Los peligros se clasifican en: Fisicos, Quimicos, Biologicos, Ergonomicos, Psicosociales y de Seguridad.",
            "incidente": "Todo incidente debe ser investigado para identificar causas basicas e inmediatas.",
            "capacitacion": "Las capacitaciones en SST deben programarse minimo una vez al ano.",
            "norma": "Las normas aplicables son ISO 45001:2018 y Decreto 1072 de 2015."
        }
        
        respuesta = "Para mas informacion, consulta la Matriz Legal."
        for key, value in respuestas.items():
            if key in prompt.lower():
                respuesta = value
                break
        
        with st.chat_message("assistant"):
            st.write(respuesta)
            st.session_state.chat_messages.append({"role": "assistant", "content": respuesta})

st.markdown("---")
st.markdown("<p style='text-align:center; font-size:11px; color:gray'>SG-SST PHVA | Desarrollado por JAN BENITEZ</p>", unsafe_allow_html=True)
