import streamlit as st
import sys
import pandas as pd
import PyPDF2
import docx
from datetime import datetime, timedelta
from pathlib import Path
import json
import re

sys.path.insert(0, str(Path(__file__).parent))

st.set_page_config(page_title="SG-SST PHVA", page_icon="🔄", layout="wide")

from core.db import db
from core.ia_engine import ia
from core.logger import Logger

logger = Logger("main")

# ============================================================
# ESTILOS CSS MODERNOS
# ============================================================
st.markdown("""
<style>
    .stApp {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    }
    .stButton > button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border-radius: 10px;
        border: none;
        padding: 12px 24px;
        font-weight: bold;
        transition: all 0.3s ease;
        width: 100%;
    }
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 5px 15px rgba(0,0,0,0.2);
    }
    .footer {
        position: fixed;
        bottom: 0;
        left: 0;
        right: 0;
        text-align: center;
        padding: 15px;
        background: rgba(0,0,0,0.85);
        color: white;
        font-size: 16px;
        font-weight: bold;
        z-index: 999;
        letter-spacing: 2px;
    }
</style>
""", unsafe_allow_html=True)

# ============================================================
# FUNCIONES
# ============================================================
def leer_pdf(file):
    try:
        pdf_reader = PyPDF2.PdfReader(file)
        texto = ""
        for page in pdf_reader.pages:
            texto += page.extract_text()
        return texto
    except:
        return ""

def leer_docx(file):
    try:
        doc = docx.Document(file)
        texto = "\n".join([paragraph.text for paragraph in doc.paragraphs])
        return texto
    except:
        return ""

def leer_excel(file):
    try:
        df = pd.read_excel(file)
        return df.to_string()
    except:
        return ""

def leer_txt(file):
    try:
        texto = file.read().decode("utf-8")
        return texto
    except:
        return ""

# ============================================================
# INICIALIZAR SESIÓN
# ============================================================
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
if "checklist" not in st.session_state:
    st.session_state.checklist = {
        "diagnostico": False,
        "peligros": False,
        "trabajadores": False,
        "acciones": False,
        "incidentes": False
    }

# ============================================================
# LOGIN
# ============================================================
if not st.session_state.authenticated:
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("""
        <div style='
            background: rgba(255,255,255,0.95);
            border-radius: 30px;
            padding: 50px 40px;
            text-align: center;
            box-shadow: 0 25px 50px rgba(0,0,0,0.3);
        '>
            <h1 style='color: #667eea; font-size: 64px; margin: 0;'>🔄</h1>
            <h1 style='color: #333; margin: 10px 0 5px 0;'>SG-SST PHVA</h1>
            <p style='color: #666; font-size: 16px;'>Sistema de Gestión de Seguridad y Salud</p>
            <p style='color: #999; font-size: 14px; margin-top: 5px;'>Nivel DIOS - IA Protagonista</p>
        </div>
        """, unsafe_allow_html=True)
        
        with st.form("login_form"):
            user = st.text_input("👤 Usuario", placeholder="admin")
            pwd = st.text_input("🔒 Contraseña", type="password", placeholder="••••••")
            
            if st.form_submit_button("🚀 ACCEDER AL SISTEMA", use_container_width=True):
                if user == "admin" and pwd == "sst2024":
                    st.session_state.authenticated = True
                    st.rerun()
                else:
                    st.error("❌ Credenciales: admin / sst2024")
        
        st.markdown("""
        <div style='text-align: center; margin-top: 40px;'>
            <hr>
            <p style='color: white; font-size: 18px; font-weight: bold;'>DESARROLLADO POR</p>
            <p style='color: white; font-size: 32px; font-weight: bold; letter-spacing: 3px;'>JAN BENITEZ</p>
        </div>
        """, unsafe_allow_html=True)
    
    st.stop()

# ============================================================
# OBTENER DATOS
# ============================================================
empresa = db.obtener_empresa()

# Actualizar checklist
st.session_state.checklist["diagnostico"] = empresa is not None
st.session_state.checklist["peligros"] = len(db.obtener_peligros()) > 0
st.session_state.checklist["trabajadores"] = len(db.obtener_trabajadores()) > 0
st.session_state.checklist["acciones"] = len(db.obtener_acciones()) > 0
st.session_state.checklist["incidentes"] = len(db.obtener_incidentes()) > 0

completados = sum(st.session_state.checklist.values())
progreso_total = int(completados / 5 * 100)

# ============================================================
# SIDEBAR
# ============================================================
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/2917/2917995.png", width=80)
    
    if empresa:
        st.markdown(f"**🏢 {empresa.get('nombre', 'Empresa')[:30]}**")
        st.caption(f"📊 {empresa.get('trabajadores', 0)} trabajadores")
    else:
        st.markdown("**🏢 Sin empresa**")
    
    st.markdown("---")
    st.markdown(f"### 📋 Progreso: {progreso_total}%")
    st.progress(progreso_total / 100)
    
    for key, label in [("diagnostico", "🤖 Diagnóstico"), ("peligros", "⚠️ Peligros"), 
                       ("trabajadores", "👥 Trabajadores"), ("acciones", "✅ Acciones"), 
                       ("incidentes", "📝 Incidentes")]:
        if st.session_state.checklist[key]:
            st.markdown(f"✅ {label}")
        else:
            st.markdown(f"⬜ {label}")
    
    st.markdown("---")
    
    menu = st.radio("📋 MENU", [
        "🏠 Dashboard", "🤖 Diagnóstico IA", "⚠️ Peligros", 
        "📊 Riesgos", "✅ Plan de Acción", "👥 Trabajadores", 
        "📝 Incidentes", "💬 Chat Experto"
    ])
    
    if st.button("🚪 Salir", use_container_width=True):
        st.session_state.authenticated = False
        st.rerun()

# ============================================================
# DASHBOARD
# ============================================================
if menu == "🏠 Dashboard":
    st.title("📊 Dashboard SST")
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("🏢 Empresa", empresa.get('nombre', 'Pendiente')[:20] if empresa else "Pendiente")
    with col2:
        st.metric("⚠️ Peligros", len(db.obtener_peligros()))
    with col3:
        st.metric("✅ Progreso", f"{progreso_total}%")
    with col4:
        st.metric("📋 Módulos", f"{completados}/5")
    
    st.markdown("---")
    
    faltantes = [label for key, label in [("diagnostico", "Diagnóstico IA"), ("peligros", "Peligros"), 
                                          ("trabajadores", "Trabajadores"), ("acciones", "Plan de Acción"), 
                                          ("incidentes", "Incidentes")] if not st.session_state.checklist[key]]
    if faltantes:
        st.subheader("📋 Pendientes")
        for item in faltantes:
            st.warning(f"⬜ {item}")
    else:
        st.success("🎉 ¡Sistema completado al 100%!")

# ============================================================
# DIAGNÓSTICO IA
# ============================================================
elif menu == "🤖 Diagnóstico IA":
    st.title("🤖 Diagnóstico IA")
    
    with st.form("diagnostico_form"):
        nombre_empresa = st.text_input("Nombre de la empresa *", value=empresa.get('nombre', '') if empresa else "")
        trabajadores = st.number_input("Trabajadores *", min_value=1, value=empresa.get('trabajadores', 10) if empresa else 10)
        arl = st.selectbox("ARL *", ["Positiva", "Sura", "Colpatria", "Bolivar"], 
                          index=["Positiva", "Sura", "Colpatria", "Bolivar"].index(empresa.get('arl', 'Positiva')) if empresa else 0)
        
        if st.form_submit_button("🚀 Generar Diagnóstico", use_container_width=True):
            if nombre_empresa:
                with st.spinner("🤖 IA generando..."):
                    prompt = f"Diagnóstico SST corto para {nombre_empresa} con {trabajadores} trabajadores, ARL {arl}. Máximo 300 palabras."
                    respuesta = ia.call_best(prompt)
                    if respuesta:
                        db.guardar_empresa("", nombre_empresa, trabajadores, arl, "", respuesta)
                        st.success("✅ Diagnóstico guardado")
                        st.rerun()

# ============================================================
# PELIGROS
# ============================================================
elif menu == "⚠️ Peligros":
    st.title("⚠️ Peligros")
    
    tab1, tab2 = st.tabs(["📋 Lista", "➕ Nuevo"])
    
    with tab1:
        df = db.obtener_peligros()
        if not df.empty:
            st.dataframe(df[['id', 'tipo', 'descripcion', 'nivel_riesgo']], use_container_width=True)
        else:
            st.info("📭 No hay peligros")
    
    with tab2:
        with st.form("nuevo_peligro"):
            tipo = st.selectbox("Tipo", ["Físico", "Químico", "Biológico", "Ergonómico", "Psicosocial", "Seguridad"])
            desc = st.text_area("Descripción")
            prob = st.slider("Probabilidad", 1, 4, 2)
            sev = st.slider("Severidad", 1, 3, 2)
            if st.form_submit_button("Guardar"):
                if desc:
                    db.guardar_peligro(tipo, desc, "", prob, sev, 0)
                    st.success("Guardado")
                    st.rerun()

# ============================================================
# RIESGOS
# ============================================================
elif menu == "📊 Riesgos":
    st.title("📊 Riesgos")
    df = db.obtener_peligros()
    if not df.empty:
        st.bar_chart(df['nivel_riesgo'].value_counts())
        st.dataframe(df[['tipo', 'descripcion', 'nivel_riesgo']], use_container_width=True)

# ============================================================
# PLAN DE ACCIÓN
# ============================================================
elif menu == "✅ Plan de Acción":
    st.title("✅ Plan de Acción")
    
    tab1, tab2 = st.tabs(["📋 Seguimiento", "➕ Nueva"])
    
    with tab1:
        df = db.obtener_acciones()
        if not df.empty:
            for _, row in df.iterrows():
                col1, col2 = st.columns([3, 1])
                with col1:
                    st.markdown(f"**{row['descripcion']}**")
                    st.caption(f"Responsable: {row['responsable']} | Vence: {row['fecha_limite']}")
                with col2:
                    nuevo = st.selectbox("Estado", ["Pendiente", "En progreso", "Completada"], 
                                        index=["Pendiente", "En progreso", "Completada"].index(row['estado']),
                                        key=f"act_{row['id']}")
                    if nuevo != row['estado']:
                        db.actualizar_estado_accion(row['id'], nuevo)
                        st.rerun()
                st.markdown("---")
    
    with tab2:
        with st.form("nueva_accion"):
            desc = st.text_area("Descripción")
            responsable = st.text_input("Responsable")
            fecha = st.date_input("Fecha límite", datetime.now())
            if st.form_submit_button("Guardar"):
                if desc:
                    db.guardar_accion(0, desc, responsable, fecha, "Media", 0)
                    st.success("Guardado")
                    st.rerun()

# ============================================================
# TRABAJADORES
# ============================================================
elif menu == "👥 Trabajadores":
    st.title("👥 Trabajadores")
    
    tab1, tab2 = st.tabs(["📋 Lista", "➕ Nuevo"])
    
    with tab1:
        df = db.obtener_trabajadores()
        if not df.empty:
            st.dataframe(df[['cedula', 'nombre', 'cargo']], use_container_width=True)
    
    with tab2:
        with st.form("nuevo_trabajador"):
            cedula = st.text_input("Cédula")
            nombre = st.text_input("Nombre")
            cargo = st.text_input("Cargo")
            if st.form_submit_button("Guardar"):
                if cedula and nombre:
                    db.guardar_trabajador(cedula, nombre, "", cargo, "")
                    st.success("Guardado")
                    st.rerun()

# ============================================================
# INCIDENTES
# ============================================================
elif menu == "📝 Incidentes":
    st.title("📝 Incidentes")
    
    with st.form("nuevo_incidente"):
        desc = st.text_area("Descripción")
        fecha = st.date_input("Fecha", datetime.now())
        if st.form_submit_button("Registrar"):
            if desc:
                db.guardar_incidente("Incidente", desc, fecha, "", "Leve")
                st.success("Registrado")
                st.rerun()
    
    df = db.obtener_incidentes()
    if not df.empty:
        st.dataframe(df)

# ============================================================
# CHAT
# ============================================================
elif menu == "💬 Chat Experto":
    st.title("💬 Chat Experto")
    
    if "msgs" not in st.session_state:
        st.session_state.msgs = []
    
    for msg in st.session_state.msgs:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])
    
    if prompt := st.chat_input("Pregunta sobre SST..."):
        st.session_state.msgs.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
        
        with st.spinner("🤖..."):
            respuesta = ia.call_best(prompt)
        
        with st.chat_message("assistant"):
            st.markdown(respuesta or "Error")
        st.session_state.msgs.append({"role": "assistant", "content": respuesta or "Error"})

# ============================================================
# FOOTER
# ============================================================
st.markdown("""
<div class='footer'>
    🔄 SG-SST PHVA | DESARROLLADO POR JAN BENITEZ | IA Protagonista
</div>
""", unsafe_allow_html=True)
