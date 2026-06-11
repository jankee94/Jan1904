import streamlit as st
import time
import pandas as pd
from datetime import datetime
import io
import traceback
import sys

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
    .error-screen {
        background: rgba(20,20,40,0.95);
        border: 3px solid #e74c3c;
        border-radius: 20px;
        padding: 40px;
        margin: 50px auto;
        max-width: 800px;
        text-align: center;
    }
    .error-screen h1 { color: #e74c3c; font-size: 2rem; }
    .error-screen code {
        background: #1a1a2e;
        padding: 10px;
        display: block;
        text-align: left;
        overflow-x: auto;
        margin: 20px 0;
        border-radius: 8px;
    }
    .safe-card {
        background: rgba(255,255,255,0.1);
        border-radius: 15px;
        padding: 20px;
        margin: 10px 0;
    }
</style>
''', unsafe_allow_html=True)

# ========== SISTEMA DE CAPTURA DE ERRORES ==========
error_global = None
error_traceback = None

def safe_execute(func, *args, **kwargs):
    """Ejecutar función de forma segura, capturando cualquier error"""
    global error_global, error_traceback
    try:
        error_global = None
        error_traceback = None
        return func(*args, **kwargs)
    except Exception as e:
        error_global = str(e)
        error_traceback = traceback.format_exc()
        return None

def show_error_screen():
    """Mostrar pantalla de error cuando algo falla"""
    global error_global, error_traceback
    
    st.markdown(f'''
    <div class="error-screen">
        <h1>⚠️ Error Detectado</h1>
        <p>La aplicación ha detectado un error y se ha detenido para evitar daños.</p>
        <p><strong>Error:</strong> {error_global}</p>
        <details>
            <summary>Ver detalles técnicos</summary>
            <code>{error_traceback}</code>
        </details>
        <button onclick="location.reload()" style="background: #667eea; color: white; border: none; padding: 10px 20px; border-radius: 8px; cursor: pointer;">
            🔄 Recargar Aplicación
        </button>
    </div>
    ''', unsafe_allow_html=True)
    
    # Botón de recarga alternativo
    if st.button("🔄 Recargar aplicación", use_container_width=True):
        st.rerun()

# ========== FUNCIÓN SEGURA PARA CADA MÓDULO ==========
def render_module_safe(module_name, render_func):
    """Renderizar módulo de forma segura"""
    global error_global
    
    # Limpiar error previo
    error_global = None
    
    try:
        render_func()
        return True
    except Exception as e:
        error_global = str(e)
        error_traceback = traceback.format_exc()
        
        # Mostrar error en la misma página sin recargar
        st.markdown(f'''
        <div class="safe-card" style="border-left: 4px solid #e74c3c;">
            <b>❌ Error en el módulo "{module_name}"</b><br>
            <code>{str(e)[:200]}</code><br>
            <small>La aplicación continúa funcionando. Puedes cambiar de módulo o recargar.</small>
        </div>
        ''', unsafe_allow_html=True)
        
        with st.expander("Ver detalles del error"):
            st.code(traceback.format_exc())
        
        return False

# ========== FUNCIONES DE LA APLICACIÓN ==========
def exportar_excel(data, nombre):
    df = pd.DataFrame(data)
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, sheet_name=nombre, index=False)
    return output.getvalue()

# ========== INICIALIZACIÓN ==========
def init_session():
    if "auth" not in st.session_state:
        st.session_state.auth = False
    if "username" not in st.session_state:
        st.session_state.username = None
    if "chat_messages" not in st.session_state:
        st.session_state.chat_messages = []
    if "last_error" not in st.session_state:
        st.session_state.last_error = None
    
    if "empresa" not in st.session_state:
        st.session_state.empresa = {"nombre": "Constructora Segura SAS", "nit": "901.234.567-8"}
    
    if "peligros" not in st.session_state:
        st.session_state.peligros = [
            {"id": 1, "tipo": "Físico", "descripcion": "Ruido excesivo", "probabilidad": 4, "severidad": 3, "nivel": "I"},
            {"id": 2, "tipo": "Ergonómico", "descripcion": "Posturas forzadas", "probabilidad": 3, "severidad": 2, "nivel": "II"},
        ]
    
    if "acciones" not in st.session_state:
        st.session_state.acciones = [
            {"id": 1, "descripcion": "Implementar barreras acústicas", "responsable": "SST", "fecha_limite": "2024-12-15", "estado": "Pendiente"},
        ]
    
    if "trabajadores" not in st.session_state:
        st.session_state.trabajadores = [
            {"id": 1, "nombre": "Carlos López", "cedula": "12345678", "cargo": "Operario"},
            {"id": 2, "nombre": "María Gómez", "cedula": "87654321", "cargo": "Supervisor"},
        ]
    
    if "incidentes" not in st.session_state:
        st.session_state.incidentes = [
            {"id": 1, "descripcion": "Caída desde andamio", "fecha": "2024-10-15", "gravedad": "Grave"},
        ]
    
    if "capacitaciones" not in st.session_state:
        st.session_state.capacitaciones = []
    if "inspecciones" not in st.session_state:
        st.session_state.inspecciones = []
    if "emergencias" not in st.session_state:
        st.session_state.emergencias = {"brigadistas": [], "equipos": [], "alertas": []}
    if "documentos" not in st.session_state:
        st.session_state.documentos = []
    if "auditorias" not in st.session_state:
        st.session_state.auditorias = []

init_session()

# ========== LOGIN SEGURO ==========
if not st.session_state.auth:
    col1, col2, col3 = st.columns([1, 1.5, 1])
    with col2:
        st.markdown('''
        <div style="background: rgba(20,20,40,0.8); backdrop-filter: blur(14px); border-radius: 28px; padding: 40px; text-align:center">
            <img src="https://cdn-icons-png.flaticon.com/512/2917/2917995.png" width="70">
            <h1 style="color:white;">SG-SST PHVA</h1>
            <p style="color:rgba(255,255,255,0.6)">Sistema de Gestión en Seguridad y Salud en el Trabajo</p>
        </div>
        ''', unsafe_allow_html=True)
        
        with st.form("login_form"):
            username = st.text_input("Usuario", placeholder="admin")
            password = st.text_input("Contraseña", type="password", placeholder="admin123")
            if st.form_submit_button("🚀 INGRESAR", use_container_width=True):
                try:
                    if username == "admin" and password == "admin123":
                        st.session_state.auth = True
                        st.session_state.username = "Administrador"
                        st.rerun()
                    else:
                        st.error("❌ Usuario o contraseña incorrectos")
                except Exception as e:
                    st.error(f"Error en login: {str(e)}")
        
        st.markdown('<p style="text-align:center; font-size:11px; color:gray">SG-SST PHVA | JAN BENITEZ</p>', unsafe_allow_html=True)
    st.stop()

# ========== SIDEBAR ==========
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/2917/2917995.png", width=50)
    st.markdown(f"### {st.session_state.username}")
    st.markdown("---")
    
    # Mostrar indicador de error si existe
    if error_global:
        st.warning("⚠️ Último error capturado")
    
    menu = st.radio("📋 MÓDULOS", [
        "Dashboard", "Empresa", "Peligros", "Plan de Acción",
        "Trabajadores", "Incidentes", "Matriz Legal", "Auditorías",
        "Capacitaciones", "Inspecciones", "Emergencias", "Documentos",
        "Indicadores", "Chat IA"
    ])
    
    st.markdown("---")
    if st.button("🚪 Cerrar Sesión", use_container_width=True):
        st.session_state.auth = False
        st.rerun()

# ========== RENDER DE MÓDULOS (TODOS ENVUELTOS EN TRY-CATCH) ==========

# Dashboard
if menu == "Dashboard":
    try:
        st.markdown(f'<div class="main-header"><h1>📊 Dashboard SST</h1><p>{st.session_state.empresa["nombre"]}</p></div>', unsafe_allow_html=True)
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("⚠️ Peligros", len(st.session_state.peligros))
        with col2:
            st.metric("✅ Acciones", len(st.session_state.acciones))
        with col3:
            st.metric("👥 Trabajadores", len(st.session_state.trabajadores))
        with col4:
            st.metric("📝 Incidentes", len(st.session_state.incidentes))
        
        if error_global:
            with st.expander("⚠️ Error capturado anteriormente"):
                st.code(error_global)
                st.code(error_traceback if error_traceback else "")
    except Exception as e:
        st.error(f"Error en Dashboard: {str(e)}")
        with st.expander("Detalles"):
            st.code(traceback.format_exc())

# Empresa
elif menu == "Empresa":
    try:
        st.markdown('<div class="main-header"><h1>🏢 Configuración de la Empresa</h1></div>', unsafe_allow_html=True)
        with st.form("empresa_form"):
            nombre = st.text_input("Nombre", value=st.session_state.empresa["nombre"])
            nit = st.text_input("NIT", value=st.session_state.empresa["nit"])
            if st.form_submit_button("💾 Guardar", use_container_width=True):
                st.session_state.empresa["nombre"] = nombre
                st.session_state.empresa["nit"] = nit
                st.success("✅ Datos guardados")
    except Exception as e:
        st.error(f"Error en Empresa: {str(e)}")
        with st.expander("Detalles"):
            st.code(traceback.format_exc())

# Peligros
elif menu == "Peligros":
    try:
        st.markdown('<div class="main-header"><h1>⚠️ Gestión de Peligros</h1></div>', unsafe_allow_html=True)
        if st.session_state.peligros:
            st.dataframe(pd.DataFrame(st.session_state.peligros), use_container_width=True)
            excel_data = exportar_excel(st.session_state.peligros, "peligros")
            st.download_button("📥 Exportar Excel", data=excel_data, file_name=f"peligros_{datetime.now().strftime('%Y%m%d')}.xlsx")
        else:
            st.info("No hay peligros registrados")
    except Exception as e:
        st.error(f"Error en Peligros: {str(e)}")

# Plan de Acción
elif menu == "Plan de Acción":
    try:
        st.markdown('<div class="main-header"><h1>✅ Plan de Acción</h1></div>', unsafe_allow_html=True)
        if st.session_state.acciones:
            st.dataframe(pd.DataFrame(st.session_state.acciones), use_container_width=True)
            excel_data = exportar_excel(st.session_state.acciones, "acciones")
            st.download_button("📥 Exportar Excel", data=excel_data, file_name=f"acciones_{datetime.now().strftime('%Y%m%d')}.xlsx")
        else:
            st.info("No hay acciones registradas")
    except Exception as e:
        st.error(f"Error en Plan de Acción: {str(e)}")

# Trabajadores
elif menu == "Trabajadores":
    try:
        st.markdown('<div class="main-header"><h1>👥 Trabajadores</h1></div>', unsafe_allow_html=True)
        if st.session_state.trabajadores:
            st.dataframe(pd.DataFrame(st.session_state.trabajadores), use_container_width=True)
            excel_data = exportar_excel(st.session_state.trabajadores, "trabajadores")
            st.download_button("📥 Exportar Excel", data=excel_data, file_name=f"trabajadores_{datetime.now().strftime('%Y%m%d')}.xlsx")
        else:
            st.info("No hay trabajadores registrados")
    except Exception as e:
        st.error(f"Error en Trabajadores: {str(e)}")

# Incidentes
elif menu == "Incidentes":
    try:
        st.markdown('<div class="main-header"><h1>📝 Incidentes</h1></div>', unsafe_allow_html=True)
        if st.session_state.incidentes:
            st.dataframe(pd.DataFrame(st.session_state.incidentes), use_container_width=True)
            excel_data = exportar_excel(st.session_state.incidentes, "incidentes")
            st.download_button("📥 Exportar Excel", data=excel_data, file_name=f"incidentes_{datetime.now().strftime('%Y%m%d')}.xlsx")
        else:
            st.info("No hay incidentes registrados")
    except Exception as e:
        st.error(f"Error en Incidentes: {str(e)}")

# Matriz Legal
elif menu == "Matriz Legal":
    try:
        st.markdown('<div class="main-header"><h1>📋 Matriz Legal</h1><p>ISO 45001 + Decreto 1072</p></div>', unsafe_allow_html=True)
        requisitos = [
            {"norma": "ISO 45001", "articulo": "4.1", "requisito": "Comprender la organización"},
            {"norma": "ISO 45001", "articulo": "5.2", "requisito": "Política de SST"},
            {"norma": "Decreto 1072", "articulo": "2.2.4.6.22", "requisito": "Conformar COPASST"},
        ]
        for req in requisitos:
            st.write(f"**{req['norma']} - {req['articulo']}**: {req['requisito']}")
            st.checkbox("Cumple", key=req['articulo'])
            st.markdown("---")
    except Exception as e:
        st.error(f"Error en Matriz Legal: {str(e)}")

# Auditorías
elif menu == "Auditorías":
    try:
        st.markdown('<div class="main-header"><h1>🔍 Auditorías</h1></div>', unsafe_allow_html=True)
        with st.form("add_auditoria"):
            codigo = st.text_input("Código", "AUD-001")
            if st.form_submit_button("Crear"):
                st.session_state.auditorias.append({"codigo": codigo, "fecha": datetime.now().strftime("%Y-%m-%d")})
                st.success(f"✅ Auditoría {codigo} creada")
    except Exception as e:
        st.error(f"Error en Auditorías: {str(e)}")

# Capacitaciones
elif menu == "Capacitaciones":
    try:
        st.markdown('<div class="main-header"><h1>📚 Capacitaciones</h1></div>', unsafe_allow_html=True)
        if st.session_state.capacitaciones:
            st.dataframe(pd.DataFrame(st.session_state.capacitaciones), use_container_width=True)
        else:
            st.info("No hay capacitaciones registradas")
    except Exception as e:
        st.error(f"Error en Capacitaciones: {str(e)}")

# Inspecciones
elif menu == "Inspecciones":
    st.markdown('<div class="main-header"><h1>🔧 Inspecciones</h1></div>', unsafe_allow_html=True)
    st.info("Módulo de inspecciones - En desarrollo")

# Emergencias
elif menu == "Emergencias":
    st.markdown('<div class="main-header"><h1>🚨 Emergencias</h1></div>', unsafe_allow_html=True)
    st.info("Módulo de emergencias - En desarrollo")

# Documentos
elif menu == "Documentos":
    st.markdown('<div class="main-header"><h1>📄 Documentos</h1></div>', unsafe_allow_html=True)
    st.info("Módulo de documentos - En desarrollo")

# Indicadores
elif menu == "Indicadores":
    try:
        st.markdown('<div class="main-header"><h1>📊 Indicadores</h1></div>', unsafe_allow_html=True)
        total = len(st.session_state.trabajadores)
        incidentes = len(st.session_state.incidentes)
        tasa = (incidentes * 100 / total) if total > 0 else 0
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Tasa Accidentalidad", f"{tasa:.1f}%")
        with col2:
            st.metric("Trabajadores", total)
    except Exception as e:
        st.error(f"Error en Indicadores: {str(e)}")

# Chat IA
elif menu == "Chat IA":
    try:
        st.markdown('<div class="main-header"><h1>💬 Chat IA</h1></div>', unsafe_allow_html=True)
        
        def call_groq(prompt):
            try:
                import requests
                key = st.secrets.get("GROQ_API_KEY")
                if not key:
                    return "No hay API key de Groq"
                url = "https://api.groq.com/openai/v1/chat/completions"
                headers = {"Authorization": f"Bearer {key}", "Content-Type": "application/json"}
                data = {"model": "llama-3.3-70b-versatile", "messages": [{"role": "user", "content": prompt}], "temperature": 0.7}
                r = requests.post(url, json=data, headers=headers, timeout=30)
                if r.status_code == 200:
                    return r.json()["choices"][0]["message"]["content"]
                return f"Error: {r.status_code}"
            except Exception as e:
                return f"Error: {str(e)}"
        
        if not st.session_state.chat_messages:
            st.session_state.chat_messages = [{"role": "assistant", "content": "Hola, soy tu asistente SST. ¿En qué puedo ayudarte?"}]
        
        for msg in st.session_state.chat_messages:
            with st.chat_message(msg["role"]):
                st.write(msg["content"])
        
        if prompt := st.chat_input("Escribe tu pregunta..."):
            st.session_state.chat_messages.append({"role": "user", "content": prompt})
            with st.chat_message("assistant"):
                with st.spinner("Consultando IA..."):
                    respuesta = call_groq(prompt)
                    st.write(respuesta)
                    st.session_state.chat_messages.append({"role": "assistant", "content": respuesta})
    except Exception as e:
        st.error(f"Error en Chat IA: {str(e)}")

st.markdown("---")
st.markdown("<p style='text-align:center; font-size:11px; color:gray'>SG-SST PHVA | JAN BENITEZ</p>", unsafe_allow_html=True)

# ANTI_ERROR - 06/11/2026 10:02:13


# DELAY - 06/11/2026 10:03:57
