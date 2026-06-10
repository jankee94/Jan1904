import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import io
import json
import random
import requests
import itertools

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
            url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent"
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
        data = {"model": "llama-3.1-70b-versatile", "messages": [{"role": "user", "content": prompt}], "temperature": 0.7}
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
    return None

def chat_ia(pregunta):
    contexto = f"""
    Eres un asistente experto en Seguridad y Salud en el Trabajo (SST).
    
    Pregunta: {pregunta}
    
    Responde de forma clara, concisa y profesional.
    """
    return call_best_ia(contexto)

# ========== INICIALIZAR DATOS ==========
def init_data():
    if "auth" not in st.session_state:
        st.session_state.auth = False
    if "current_user" not in st.session_state:
        st.session_state.current_user = None
    if "empresa" not in st.session_state:
        st.session_state.empresa = {"nombre": "Constructora Segura SAS", "nit": "901.234.567-8"}
    if "trabajadores" not in st.session_state:
        st.session_state.trabajadores = [
            {"id": 1, "nombre": "Carlos Lopez", "cedula": "12345678", "cargo": "Operario"},
            {"id": 2, "nombre": "Maria Gomez", "cedula": "87654321", "cargo": "Supervisor"},
        ]
    if "peligros" not in st.session_state:
        st.session_state.peligros = [
            {"id": 1, "tipo": "Fisico", "descripcion": "Ruido excesivo", "nivel": "I"},
        ]
    if "incidentes" not in st.session_state:
        st.session_state.incidentes = [
            {"id": 1, "descripcion": "Caida desde andamio", "fecha": "2024-10-15", "gravedad": "Grave"},
        ]
    if "acciones" not in st.session_state:
        st.session_state.acciones = [
            {"id": 1, "descripcion": "Implementar barreras", "responsable": "SST", "estado": "Pendiente"},
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
                    st.rerun()
                else:
                    st.error("Usuario o contraseña incorrectos")
        
        st.markdown('<p style="text-align:center; font-size:11px; color:gray">SG-SST PHVA | Desarrollado por JAN BENITEZ</p>', unsafe_allow_html=True)
    st.stop()

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
    st.markdown(f'<div class="main-header"><h1>Dashboard</h1><p>{st.session_state.empresa["nombre"]}</p></div>', unsafe_allow_html=True)
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Trabajadores", len(st.session_state.trabajadores))
    with col2:
        st.metric("Peligros", len(st.session_state.peligros))
    with col3:
        st.metric("Incidentes", len(st.session_state.incidentes))
    with col4:
        st.metric("Acciones", len(st.session_state.acciones))
    
    st.markdown("---")
    
    # Test de IA
    with st.expander("🤖 Prueba de Conexion IA"):
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Probar Gemini"):
                with st.spinner("Probando Gemini..."):
                    res = call_gemini("Responde solo: OK")
                    if res:
                        st.success(f"Gemini responde: {res}")
                    else:
                        st.error("Gemini no responde - Verifica API keys")
        with col2:
            if st.button("Probar Groq"):
                with st.spinner("Probando Groq..."):
                    res = call_groq("Responde solo: OK")
                    if res:
                        st.success(f"Groq responde: {res}")
                    else:
                        st.error("Groq no responde - Verifica API keys")

# ========== EMPRESA ==========
elif menu == "Empresa":
    st.markdown('<div class="main-header"><h1>Configuracion de Empresa</h1></div>', unsafe_allow_html=True)
    with st.form("empresa_form"):
        nombre = st.text_input("Nombre", value=st.session_state.empresa.get("nombre", ""))
        nit = st.text_input("NIT", value=st.session_state.empresa.get("nit", ""))
        if st.form_submit_button("Guardar"):
            st.session_state.empresa["nombre"] = nombre
            st.session_state.empresa["nit"] = nit
            st.success("Datos guardados")

# ========== PELIGROS ==========
elif menu == "Peligros":
    st.markdown('<div class="main-header"><h1>Gestion de Peligros</h1></div>', unsafe_allow_html=True)
    df = pd.DataFrame(st.session_state.peligros)
    st.dataframe(df, use_container_width=True)

# ========== PLAN DE ACCION ==========
elif menu == "Plan de Accion":
    st.markdown('<div class="main-header"><h1>Plan de Accion</h1></div>', unsafe_allow_html=True)
    for accion in st.session_state.acciones:
        with st.expander(accion["descripcion"]):
            st.write(f"Responsable: {accion['responsable']}")
            nuevo = st.selectbox("Estado", ["Pendiente", "En progreso", "Completada"], 
                               index=["Pendiente", "En progreso", "Completada"].index(accion["estado"]),
                               key=f"estado_{accion['id']}")
            if nuevo != accion["estado"]:
                accion["estado"] = nuevo
                st.rerun()

# ========== TRABAJADORES ==========
elif menu == "Trabajadores":
    st.markdown('<div class="main-header"><h1>Trabajadores</h1></div>', unsafe_allow_html=True)
    df = pd.DataFrame(st.session_state.trabajadores)
    st.dataframe(df, use_container_width=True)

# ========== INCIDENTES ==========
elif menu == "Incidentes":
    st.markdown('<div class="main-header"><h1>Incidentes</h1></div>', unsafe_allow_html=True)
    df = pd.DataFrame(st.session_state.incidentes)
    st.dataframe(df, use_container_width=True)

# ========== MATRIZ LEGAL ==========
elif menu == "Matriz Legal":
    st.markdown('<div class="main-header"><h1>Matriz Legal</h1><p>ISO 45001 + Decreto 1072</p></div>', unsafe_allow_html=True)
    requisitos = [
        {"norma": "ISO 45001", "articulo": "4.1", "requisito": "Comprender la organizacion"},
        {"norma": "ISO 45001", "articulo": "5.2", "requisito": "Politica de SST"},
        {"norma": "Decreto 1072", "articulo": "2.2.4.6.22", "requisito": "Conformar COPASST"},
    ]
    for req in requisitos:
        st.write(f"**{req['norma']} - {req['articulo']}**: {req['requisito']}")
        st.checkbox("Cumple", key=req['articulo'])
        st.markdown("---")

# ========== AUDITORIAS ==========
elif menu == "Auditorias":
    st.markdown('<div class="main-header"><h1>Auditorias Internas</h1></div>', unsafe_allow_html=True)
    with st.form("add_auditoria"):
        codigo = st.text_input("Codigo", "AUD-001")
        if st.form_submit_button("Crear"):
            st.success(f"Auditoria {codigo} creada")

# ========== CAPACITACIONES ==========
elif menu == "Capacitaciones":
    st.markdown('<div class="main-header"><h1>Capacitaciones</h1></div>', unsafe_allow_html=True)
    st.info("Modulo de capacitaciones - Proximamente mas funciones")

# ========== INSPECCIONES ==========
elif menu == "Inspecciones":
    st.markdown('<div class="main-header"><h1>Inspecciones</h1></div>', unsafe_allow_html=True)
    st.info("Modulo de inspecciones - Proximamente mas funciones")

# ========== EMERGENCIAS ==========
elif menu == "Emergencias":
    st.markdown('<div class="main-header"><h1>Emergencias</h1></div>', unsafe_allow_html=True)
    st.info("Modulo de emergencias - Proximamente mas funciones")

# ========== DOCUMENTOS ==========
elif menu == "Documentos":
    st.markdown('<div class="main-header"><h1>Gestion Documental</h1></div>', unsafe_allow_html=True)
    st.info("Modulo de documentos - Proximamente mas funciones")

# ========== INDICADORES ==========
elif menu == "Indicadores":
    st.markdown('<div class="main-header"><h1>Indicadores SST</h1></div>', unsafe_allow_html=True)
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Indice de Frecuencia", "2.5")
    with col2:
        st.metric("Cumplimiento PHVA", "75%")
    with col3:
        st.metric("Tasa Accidentalidad", "3.2%")

# ========== CHAT IA ==========
elif menu == "Chat IA":
    st.markdown('<div class="main-header"><h1>Chat IA</h1><p>Asistente virtual especializado en SST</p></div>', unsafe_allow_html=True)
    
    if "chat_messages" not in st.session_state:
        st.session_state.chat_messages = [{"role": "assistant", "content": "Hola, soy tu asistente SST. Puedo ayudarte con consultas sobre normativa, peligros, incidentes y mas. ¿En que puedo ayudarte?"}]
    
    for msg in st.session_state.chat_messages:
        with st.chat_message(msg["role"]):
            st.write(msg["content"])
    
    if prompt := st.chat_input("Escribe tu pregunta sobre SST..."):
        st.session_state.chat_messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.write(prompt)
        
        with st.chat_message("assistant"):
            with st.spinner("🤖 IA analizando tu consulta..."):
                respuesta = chat_ia(prompt)
                if respuesta:
                    st.write(respuesta)
                    st.session_state.chat_messages.append({"role": "assistant", "content": respuesta})
                else:
                    st.warning("No se pudo obtener respuesta de la IA. Verifica que las API keys esten configuradas en Secrets.")
                    st.info("Para configurar: Ve a Settings -> Secrets en Streamlit Cloud y agrega GEMINI_API_KEY_1 y GROQ_API_KEY")

st.markdown("---")
st.markdown("<p style='text-align:center; font-size:11px; color:gray'>SG-SST PHVA | Sistema de Gestion con IA | Desarrollado por JAN BENITEZ</p>", unsafe_allow_html=True)
