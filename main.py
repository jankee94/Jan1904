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
# ESTILOS CSS
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
    .guia-card {
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
        border-radius: 15px;
        padding: 20px;
        margin: 10px 0;
        border-left: 5px solid #667eea;
    }
    .paso-completado {
        background: #d4edda;
        border-left: 5px solid #28a745;
    }
    .paso-actual {
        background: #fff3cd;
        border-left: 5px solid #ffc107;
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

def extraer_con_ia(texto):
    prompt = f"""
    Extrae del siguiente texto información clave para SST:
    
    TEXTO:
    {texto[:2000]}
    
    Devuelve JSON con:
    - peligros: lista de {{"tipo": "", "descripcion": "", "probabilidad": 2, "severidad": 2}}
    - trabajadores_sugeridos: lista de {{"nombre": "", "cargo": ""}}
    - acciones_sugeridas: lista de {{"descripcion": "", "responsable": "", "prioridad": "Media"}}
    """
    
    respuesta = ia.call_best(prompt)
    try:
        json_match = re.search(r'\{.*\}', respuesta, re.DOTALL)
        if json_match:
            return json.loads(json_match.group())
    except:
        pass
    return {"peligros": [], "trabajadores_sugeridos": [], "acciones_sugeridas": []}

# ============================================================
# INICIALIZAR SESIÓN
# ============================================================
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
if "paso_actual" not in st.session_state:
    st.session_state.paso_actual = 1
if "diagnostico_generado" not in st.session_state:
    st.session_state.diagnostico_generado = False
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
            <h1 style='color: #667eea; font-size: 64px;'>🔄</h1>
            <h1 style='color: #333;'>SG-SST PHVA</h1>
            <p style='color: #666;'>Sistema de Gestión de Seguridad y Salud</p>
            <p style='color: #999;'>Nivel DIOS - IA Protagonista</p>
        </div>
        """, unsafe_allow_html=True)
        
        with st.form("login_form"):
            user = st.text_input("👤 Usuario", placeholder="admin")
            pwd = st.text_input("🔒 Contraseña", type="password", placeholder="••••••")
            
            if st.form_submit_button("🚀 ACCEDER", use_container_width=True):
                if user == "admin" and pwd == "sst2024":
                    st.session_state.authenticated = True
                    st.rerun()
                else:
                    st.error("❌ Usuario: admin / Contraseña: sst2024")
        
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

# Determinar paso actual
if not st.session_state.checklist["diagnostico"]:
    st.session_state.paso_actual = 1
elif not st.session_state.checklist["peligros"]:
    st.session_state.paso_actual = 2
elif not st.session_state.checklist["trabajadores"]:
    st.session_state.paso_actual = 3
elif not st.session_state.checklist["acciones"]:
    st.session_state.paso_actual = 4
elif not st.session_state.checklist["incidentes"]:
    st.session_state.paso_actual = 5
else:
    st.session_state.paso_actual = 6

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
    
    # Mostrar fases
    fases = [
        ("1️⃣ Diagnóstico IA", st.session_state.checklist["diagnostico"]),
        ("2️⃣ Peligros", st.session_state.checklist["peligros"]),
        ("3️⃣ Trabajadores", st.session_state.checklist["trabajadores"]),
        ("4️⃣ Plan de Acción", st.session_state.checklist["acciones"]),
        ("5️⃣ Incidentes", st.session_state.checklist["incidentes"]),
    ]
    
    for fase, completado in fases:
        if completado:
            st.markdown(f"✅ {fase}")
        else:
            st.markdown(f"⬜ {fase}")
    
    st.markdown("---")
    
    menu = st.radio("📋 MENU", [
        "🏠 Dashboard",
        "🤖 Diagnóstico IA",
        "⚠️ Peligros",
        "👥 Trabajadores",
        "✅ Plan de Acción",
        "📝 Incidentes",
        "📊 Riesgos",
        "💬 Chat Experto"
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
        st.metric("👥 Trabajadores", len(db.obtener_trabajadores()))
    with col4:
        st.metric("✅ Progreso", f"{progreso_total}%")
    
    st.markdown("---")
    
    # GUÍA DE FASES
    st.subheader("🎯 GUÍA DE IMPLEMENTACIÓN PHVA")
    
    if st.session_state.paso_actual == 1:
        st.markdown("""
        <div class='guia-card paso-actual'>
            <h3>📍 PASO 1: DIAGNÓSTICO IA</h3>
            <p>Ve a la sección <strong>🤖 Diagnóstico IA</strong> y completa los datos de tu empresa.</p>
            <p>La IA generará automáticamente un diagnóstico y precargará información.</p>
        </div>
        """, unsafe_allow_html=True)
    elif st.session_state.paso_actual == 2:
        st.markdown("""
        <div class='guia-card paso-actual'>
            <h3>📍 PASO 2: IDENTIFICAR PELIGROS</h3>
            <p>Ve a la sección <strong>⚠️ Peligros</strong> y registra los peligros de tu empresa.</p>
            <p>La IA ya ha precargado algunos peligros sugeridos. Revisa y confirma.</p>
            <button onclick="window.location.href='#peligros'">Ir a Peligros →</button>
        </div>
        """, unsafe_allow_html=True)
    elif st.session_state.paso_actual == 3:
        st.markdown("""
        <div class='guia-card paso-actual'>
            <h3>📍 PASO 3: REGISTRAR TRABAJADORES</h3>
            <p>Ve a la sección <strong>👥 Trabajadores</strong> y registra tu personal.</p>
            <p>Puedes hacerlo manualmente o con carga masiva por Excel.</p>
        </div>
        """, unsafe_allow_html=True)
    elif st.session_state.paso_actual == 4:
        st.markdown("""
        <div class='guia-card paso-actual'>
            <h3>📍 PASO 4: PLAN DE ACCIÓN</h3>
            <p>Ve a la sección <strong>✅ Plan de Acción</strong> y crea las acciones correctivas.</p>
            <p>La IA ha sugerido acciones basadas en los peligros identificados.</p>
        </div>
        """, unsafe_allow_html=True)
    elif st.session_state.paso_actual == 5:
        st.markdown("""
        <div class='guia-card paso-actual'>
            <h3>📍 PASO 5: REGISTRAR INCIDENTES</h3>
            <p>Ve a la sección <strong>📝 Incidentes</strong> y registra cualquier incidente ocurrido.</p>
            <p>Esto alimentará los indicadores de frecuencia y severidad.</p>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div class='guia-card'>
            <h3>🎉 ¡FELICITACIONES!</h3>
            <p>Has completado todas las fases del ciclo PHVA.</p>
            <p>Tu sistema SST está completamente implementado.</p>
        </div>
        """, unsafe_allow_html=True)
    
    # Mostrar resumen
    st.markdown("---")
    st.subheader("📋 Resumen por Módulo")
    
    for fase, completado, url in [
        ("🤖 Diagnóstico IA", st.session_state.checklist["diagnostico"], "Diagnóstico IA"),
        ("⚠️ Peligros", st.session_state.checklist["peligros"], "Peligros"),
        ("👥 Trabajadores", st.session_state.checklist["trabajadores"], "Trabajadores"),
        ("✅ Plan de Acción", st.session_state.checklist["acciones"], "Plan de Acción"),
        ("📝 Incidentes", st.session_state.checklist["incidentes"], "Incidentes"),
    ]:
        col1, col2 = st.columns([3, 1])
        with col1:
            if completado:
                st.markdown(f"✅ **{fase}** - Completado")
            else:
                st.markdown(f"⬜ **{fase}** - Pendiente")
        with col2:
            if not completado:
                if st.button(f"Ir", key=f"btn_{fase}"):
                    st.session_state.menu_seleccion = url
                    st.rerun()

# ============================================================
# DIAGNÓSTICO IA
# ============================================================
elif menu == "🤖 Diagnóstico IA":
    st.title("🤖 Diagnóstico IA")
    st.markdown("Completa estos datos y la IA generará un diagnóstico completo.")
    st.markdown("---")
    
    with st.form("diagnostico_form"):
        nombre_empresa = st.text_input("📛 Nombre de la empresa *", 
                                       value=empresa.get('nombre', '') if empresa else "")
        col1, col2 = st.columns(2)
        with col1:
            trabajadores = st.number_input("👥 Número de trabajadores *", 
                                          min_value=1, 
                                          value=empresa.get('trabajadores', 10) if empresa else 10)
        with col2:
            arl = st.selectbox("🏥 ARL *", ["Positiva", "Sura", "Colpatria", "Bolivar"], 
                              index=["Positiva", "Sura", "Colpatria", "Bolivar"].index(empresa.get('arl', 'Positiva')) if empresa else 0)
        
        st.markdown("---")
        st.info("🤖 La IA generará automáticamente: diagnóstico, peligros sugeridos y acciones recomendadas")
        
        if st.form_submit_button("🚀 GENERAR DIAGNÓSTICO", use_container_width=True):
            if nombre_empresa:
                with st.spinner("🤖 IA generando diagnóstico completo..."):
                    # Prompt para diagnóstico completo
                    prompt = f"""
                    Genera un diagnóstico SST completo para {nombre_empresa} con {trabajadores} trabajadores, ARL {arl}.
                    
                    INCLUYE:
                    1. Perfil de la empresa
                    2. Peligros típicos (mínimo 5)
                    3. Riesgos prioritarios
                    4. Plan de acción sugerido (mínimo 3 acciones)
                    5. Requisitos legales aplicables
                    
                    Formato: Markdown profesional.
                    """
                    respuesta = ia.call_best(prompt)
                    
                    if respuesta:
                        # Guardar empresa
                        db.guardar_empresa("", nombre_empresa, trabajadores, arl, "", respuesta)
                        
                        # PRECARGAR PELIGROS SUGERIDOS
                        peligros_base = [
                            ("Ergonómico", f"Posturas inadecuadas en {nombre_empresa}", "Todas las áreas", 2, 2),
                            ("Psicosocial", "Estrés laboral por carga de trabajo", "Administrativo", 2, 2),
                            ("Seguridad", "Caídas al mismo nivel", "Todas las áreas", 2, 2),
                            ("Físico", "Iluminación inadecuada", "Oficinas", 2, 1),
                            ("Biológico", "Exposición a virus en áreas comunes", "Áreas comunes", 2, 2),
                        ]
                        
                        for p in peligros_base:
                            db.guardar_peligro(p[0], p[1], p[2], p[3], p[4], 1)
                        
                        # PRECARGAR ACCIONES SUGERIDAS
                        acciones_base = [
                            (f"Realizar matriz de riesgos para {nombre_empresa}", "Responsable SST", (datetime.now() + timedelta(days=30)).strftime("%Y-%m-%d"), "Alta"),
                            ("Capacitar al personal en prevención de riesgos", "Coordinador SST", (datetime.now() + timedelta(days=45)).strftime("%Y-%m-%d"), "Alta"),
                            (f"Implementar pausas activas en {nombre_empresa}", "Líder de área", (datetime.now() + timedelta(days=15)).strftime("%Y-%m-%d"), "Media"),
                        ]
                        
                        for a in acciones_base:
                            db.guardar_accion(0, a[0], a[1], a[2], a[3], 1)
                        
                        st.balloons()
                        st.success("✅ **DIAGNÓSTICO COMPLETADO CON ÉXITO**")
                        st.markdown("---")
                        st.markdown(respuesta)
                        
                        st.markdown("---")
                        st.info("📋 **La IA ha precargado información en los módulos:**")
                        st.markdown("""
                        - ✅ Peligros sugeridos (5 registros precargados)
                        - ✅ Plan de Acción sugerido (3 acciones precargadas)
                        """)
                        
                        st.markdown("---")
                        st.subheader("🎯 ¿QUÉ SIGUE?")
                        
                        col1, col2 = st.columns(2)
                        with col1:
                            if st.button("⚠️ IR A PELIGROS", use_container_width=True):
                                st.session_state.menu_seleccion = "⚠️ Peligros"
                                st.rerun()
                        with col2:
                            if st.button("✅ IR A PLAN DE ACCIÓN", use_container_width=True):
                                st.session_state.menu_seleccion = "✅ Plan de Acción"
                                st.rerun()
                    else:
                        st.error("❌ Error al generar diagnóstico. Verifica API keys.")
            else:
                st.error("❌ Ingresa el nombre de la empresa")

# ============================================================
# PELIGROS
# ============================================================
elif menu == "⚠️ Peligros":
    st.title("⚠️ Peligros - Fase 2")
    
    # Mostrar guía
    if not st.session_state.checklist["peligros"]:
        st.info("📌 **PASO 2 DEL PHVA**: Identifica y registra los peligros de tu empresa.")
        st.markdown("""
        La IA ya ha precargado algunos peligros sugeridos.  
        **Revisa, modifica o agrega más peligros según tu realidad.**
        """)
    
    tab1, tab2 = st.tabs(["📋 Lista de Peligros", "➕ Agregar Peligro"])
    
    with tab1:
        df = db.obtener_peligros()
        if not df.empty:
            st.dataframe(df[['id', 'tipo', 'descripcion', 'nivel_riesgo']], use_container_width=True)
            
            if len(df) >= 3 and not st.session_state.checklist["peligros"]:
                st.success("✅ ¡Bien! Ya tienes suficientes peligros registrados.")
                if st.button("➡️ CONTINUAR CON TRABAJADORES", use_container_width=True):
                    st.rerun()
        else:
            st.info("📭 No hay peligros registrados. Usa el formulario para agregar.")
    
    with tab2:
        with st.form("nuevo_peligro"):
            col1, col2 = st.columns(2)
            with col1:
                tipo = st.selectbox("Tipo", ["Físico", "Químico", "Biológico", "Ergonómico", "Psicosocial", "Seguridad"])
                desc = st.text_area("Descripción")
            with col2:
                prob = st.slider("Probabilidad (1-4)", 1, 4, 2)
                sev = st.slider("Severidad (1-3)", 1, 3, 2)
                nivel = db.calcular_nivel(prob, sev)
                st.info(f"📊 Nivel de riesgo: **{nivel}**")
            
            if st.form_submit_button("💾 Guardar Peligro"):
                if desc:
                    db.guardar_peligro(tipo, desc, "", prob, sev, 0)
                    st.success("✅ Peligro guardado")
                    st.rerun()

# ============================================================
# TRABAJADORES
# ============================================================
elif menu == "👥 Trabajadores":
    st.title("👥 Trabajadores - Fase 3")
    
    if not st.session_state.checklist["trabajadores"]:
        st.info("📌 **PASO 3 DEL PHVA**: Registra los trabajadores de tu empresa.")
    
    tab1, tab2 = st.tabs(["📋 Lista", "➕ Nuevo"])
    
    with tab1:
        df = db.obtener_trabajadores()
        if not df.empty:
            st.dataframe(df[['cedula', 'nombre', 'cargo']], use_container_width=True)
            
            if len(df) >= 1 and not st.session_state.checklist["trabajadores"]:
                st.success("✅ ¡Bien! Trabajadores registrados.")
                if st.button("➡️ CONTINUAR CON PLAN DE ACCIÓN", use_container_width=True):
                    st.rerun()
        else:
            st.info("📭 No hay trabajadores registrados")
    
    with tab2:
        with st.form("nuevo_trabajador"):
            cedula = st.text_input("Cédula")
            nombre = st.text_input("Nombre")
            cargo = st.text_input("Cargo")
            if st.form_submit_button("Guardar"):
                if cedula and nombre:
                    db.guardar_trabajador(cedula, nombre, "", cargo, "")
                    st.success("✅ Guardado")
                    st.rerun()

# ============================================================
# PLAN DE ACCIÓN
# ============================================================
elif menu == "✅ Plan de Acción":
    st.title("✅ Plan de Acción - Fase 4")
    
    if not st.session_state.checklist["acciones"]:
        st.info("📌 **PASO 4 DEL PHVA**: Crea acciones para mitigar los riesgos identificados.")
    
    tab1, tab2 = st.tabs(["📋 Seguimiento", "➕ Nueva Acción"])
    
    with tab1:
        df = db.obtener_acciones()
        if not df.empty:
            for _, row in df.iterrows():
                col1, col2 = st.columns([3, 1])
                with col1:
                    st.markdown(f"**📌 {row['descripcion']}**")
                    st.caption(f"Responsable: {row['responsable']} | Vence: {row['fecha_limite']}")
                with col2:
                    nuevo = st.selectbox("Estado", ["Pendiente", "En progreso", "Completada"], 
                                        index=["Pendiente", "En progreso", "Completada"].index(row['estado']),
                                        key=f"act_{row['id']}")
                    if nuevo != row['estado']:
                        db.actualizar_estado_accion(row['id'], nuevo)
                        st.rerun()
                st.markdown("---")
            
            if len(df) >= 2 and not st.session_state.checklist["acciones"]:
                st.success("✅ ¡Bien! Plan de acción en marcha.")
                if st.button("➡️ CONTINUAR CON INCIDENTES", use_container_width=True):
                    st.rerun()
        else:
            st.info("📭 No hay acciones registradas")
    
    with tab2:
        with st.form("nueva_accion"):
            desc = st.text_area("Descripción")
            responsable = st.text_input("Responsable")
            fecha = st.date_input("Fecha límite", datetime.now() + timedelta(days=30))
            if st.form_submit_button("Guardar"):
                if desc:
                    db.guardar_accion(0, desc, responsable, fecha, "Media", 0)
                    st.success("✅ Guardado")
                    st.rerun()

# ============================================================
# INCIDENTES
# ============================================================
elif menu == "📝 Incidentes":
    st.title("📝 Incidentes - Fase 5")
    
    if not st.session_state.checklist["incidentes"]:
        st.info("📌 **PASO 5 DEL PHVA**: Registra los incidentes ocurridos para calcular indicadores.")
    
    with st.form("nuevo_incidente"):
        desc = st.text_area("Descripción del incidente")
        fecha = st.date_input("Fecha", datetime.now())
        gravedad = st.selectbox("Gravedad", ["Leve", "Moderada", "Grave"])
        
        if st.form_submit_button("Registrar Incidente"):
            if desc:
                db.guardar_incidente("Incidente", desc, fecha, "", gravedad)
                st.success("✅ Registrado")
                st.rerun()
    
    st.markdown("---")
    df = db.obtener_incidentes()
    if not df.empty:
        st.dataframe(df)

# ============================================================
# RIESGOS
# ============================================================
elif menu == "📊 Riesgos":
    st.title("📊 Matriz de Riesgos")
    df = db.obtener_peligros()
    if not df.empty:
        st.bar_chart(df['nivel_riesgo'].value_counts())
        st.dataframe(df[['tipo', 'descripcion', 'nivel_riesgo']], use_container_width=True)

# ============================================================
# CHAT
# ============================================================
elif menu == "💬 Chat Experto":
    st.title("💬 Chat Experto SST")
    
    if "msgs" not in st.session_state:
        st.session_state.msgs = []
    
    for msg in st.session_state.msgs:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])
    
    if prompt := st.chat_input("Pregunta sobre SST..."):
        st.session_state.msgs.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
        
        contexto = ""
        if empresa:
            contexto = f"Empresa: {empresa.get('nombre', '')} con {empresa.get('trabajadores', 0)} trabajadores.\n"
        
        with st.spinner("🤖..."):
            respuesta = ia.call_best(f"{contexto}Pregunta SST: {prompt}")
        
        with st.chat_message("assistant"):
            st.markdown(respuesta or "Error")
        st.session_state.msgs.append({"role": "assistant", "content": respuesta or "Error"})

# ============================================================
# FOOTER
# ============================================================
st.markdown("""
<div class='footer'>
    🔄 SG-SST PHVA | DESARROLLADO POR JAN BENITEZ | IA Protagonista | Ciclo PHVA
</div>
""", unsafe_allow_html=True)
