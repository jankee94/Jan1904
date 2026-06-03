import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import plotly.graph_objects as go
import requests
import json
import time

st.set_page_config(
    page_title="SG-SST PHVA - IA Inteligente",
    page_icon="🔄",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==================== INICIALIZACIÓN COMPLETA ====================
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
if "username" not in st.session_state:
    st.session_state.username = None
if "fase_actual" not in st.session_state:
    st.session_state.fase_actual = 1
if "peligros" not in st.session_state:
    st.session_state.peligros = []
if "capacitaciones" not in st.session_state:
    st.session_state.capacitaciones = []
if "incidentes" not in st.session_state:
    st.session_state.incidentes = []
if "empresa" not in st.session_state:
    st.session_state.empresa = {"nombre": "", "trabajadores": 1, "nit": "", "ciudad": "", "sector": "Construcción"}
if "plan_accion" not in st.session_state:
    st.session_state.plan_accion = []
if "matriz_riesgos" not in st.session_state:
    st.session_state.matriz_riesgos = []
if "diagnostico_generado" not in st.session_state:
    st.session_state.diagnostico_generado = ""
if "ia_messages" not in st.session_state:
    st.session_state.ia_messages = []

# ==================== FUNCIONES IA CON SECRETS ====================
def get_gemini_key():
    try:
        return st.secrets["gemini"]["api_key"]
    except:
        return None

def get_groq_key():
    try:
        return st.secrets["groq"]["api_key"]
    except:
        return None

def llamar_gemini(prompt):
    """Llama a Gemini API usando secret"""
    api_key = get_gemini_key()
    if not api_key:
        return None
    try:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={api_key}"
        payload = {"contents": [{"parts": [{"text": prompt}]}]}
        response = requests.post(url, json=payload, timeout=30)
        if response.status_code == 200:
            data = response.json()
            return data.get("candidates", [{}])[0].get("content", {}).get("parts", [{}])[0].get("text", None)
        return None
    except:
        return None

def llamar_groq(prompt):
    """Llama a Groq API usando secret"""
    api_key = get_groq_key()
    if not api_key:
        return None
    try:
        url = "https://api.groq.com/openai/v1/chat/completions"
        headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
        payload = {"model": "llama3-70b-8192", "messages": [{"role": "user", "content": prompt}], "temperature": 0.7}
        response = requests.post(url, json=payload, headers=headers, timeout=30)
        if response.status_code == 200:
            data = response.json()
            return data.get("choices", [{}])[0].get("message", {}).get("content", None)
        return None
    except:
        return None

def generar_con_ia(prompt, contexto=""):
    """Intenta Gemini, si falla usa Groq"""
    prompt_completo = f"{contexto}\n\n{prompt}" if contexto else prompt
    
    respuesta = llamar_gemini(prompt_completo)
    if respuesta:
        return f"🤖 **IA Gemini:** {respuesta}"
    
    respuesta = llamar_groq(prompt_completo)
    if respuesta:
        return f"🤖 **IA Groq:** {respuesta}"
    
    return None

def generar_diagnostico_ia():
    """Genera diagnóstico usando IA con datos reales"""
    empresa = st.session_state.empresa
    nombre = empresa.get("nombre", "").strip()
    if not nombre or empresa.get("trabajadores", 0) < 1:
        return "⚠️ Complete los datos de la empresa en Fase 1 primero."
    
    contexto = f"""
DATOS DE LA EMPRESA:
- Nombre: {nombre}
- NIT: {empresa.get('nit', 'No registrado')}
- Sector: {empresa.get('sector', 'Construcción')}
- Trabajadores: {empresa.get('trabajadores', 0)}
- Ciudad: {empresa.get('ciudad', 'No registrada')}
- Progreso actual: {calcular_progreso()}%
- Fase actual: {st.session_state.fase_actual}/6
"""
    
    prompt = """Genera un DIAGNÓSTICO COMPLETO DE SEGURIDAD Y SALUD EN EL TRABAJO para esta empresa.
Incluye: análisis de riesgos, normativa aplicable, recomendaciones inmediatas y próximos pasos."""
    
    respuesta = generar_con_ia(prompt, contexto)
    if respuesta:
        return respuesta
    else:
        return generar_diagnostico_local()

def generar_diagnostico_local():
    """Diagnóstico local de respaldo"""
    empresa = st.session_state.empresa
    sector = empresa.get("sector", "Construcción")
    analisis = {
        "Construcción": "Riesgos: Trabajo en alturas, caída de objetos, maquinaria pesada",
        "Manufactura": "Riesgos: Atrapamiento de maquinaria, exposición a químicos, ruido",
        "Salud": "Riesgos: Biológicos, carga mental, radiaciones",
    }
    return f"""**📋 DIAGNÓSTICO - {empresa.get('nombre', 'Empresa')}**

**Análisis por sector ({sector}):** {analisis.get(sector, 'Realizar matriz GTC-45')}

**Recomendaciones:** Conformar COPASST, matriz de peligros, capacitaciones anuales."""

def recomendar_con_ia(tipo, datos_adicionales=""):
    """IA recomienda acciones según el contexto"""
    prompts = {
        "peligro": f"Recomienda controles para este peligro: {datos_adicionales}",
        "capacitacion": f"Sector: {st.session_state.empresa.get('sector', 'General')}. Recomienda capacitaciones obligatorias en SST.",
        "accion": "Sugiere acciones correctivas para riesgos laborales.",
    }
    prompt = prompts.get(tipo, "Recomienda buenas prácticas en SST.")
    respuesta = generar_con_ia(prompt)
    return respuesta if respuesta else "✅ Recomendación: Implementar controles según normativa GTC-45."

def calcular_nivel_riesgo(p, s):
    puntaje = p * s
    if puntaje >= 9: return "I"
    elif puntaje >= 6: return "II"
    elif puntaje >= 4: return "III"
    else: return "IV"

def calcular_progreso():
    completadas = 0
    if st.session_state.empresa.get("nombre", "").strip() and st.session_state.empresa.get("trabajadores", 0) >= 1:
        completadas += 1
    if len(st.session_state.peligros) > 0:
        completadas += 1
    if len(st.session_state.matriz_riesgos) > 0:
        completadas += 1
    if len(st.session_state.plan_accion) > 0:
        completadas += 1
    if len(st.session_state.capacitaciones) > 0:
        completadas += 1
    if len(st.session_state.incidentes) > 0:
        completadas += 1
    return int((completadas / 6) * 100)

# ==================== CSS ====================
st.markdown("""
<style>
    @keyframes fadeIn { from { opacity: 0; transform: translateY(20px); } to { opacity: 1; transform: translateY(0); } }
    @keyframes slideIn { from { transform: translateX(-30px); opacity: 0; } to { transform: translateX(0); opacity: 1; } }
    @keyframes glow { 0% { box-shadow: 0 0 5px rgba(102,126,234,0.5); } 100% { box-shadow: 0 0 20px rgba(102,126,234,0.8); } }
    
    .stApp { background: linear-gradient(135deg, #0f2027, #203a43, #2c5364) !important; }
    .main-header { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 1.5rem; border-radius: 20px; color: white; text-align: center; margin-bottom: 1.5rem; animation: slideIn 0.6s; }
    .fase-card { background: rgba(255,255,255,0.1); backdrop-filter: blur(10px); padding: 0.8rem; border-radius: 15px; margin: 0.3rem; text-align: center; transition: all 0.3s; }
    .fase-card:hover { transform: translateY(-5px); background: rgba(255,255,255,0.2); }
    .fase-completada { border: 2px solid #00ff00; background: rgba(0,255,0,0.1); }
    .fase-actual { border: 2px solid #ffcc00; background: rgba(255,204,0,0.15); transform: scale(1.02); animation: glow 1.5s infinite; }
    .metric-card { background: rgba(255,255,255,0.1); backdrop-filter: blur(10px); padding: 1rem; border-radius: 15px; text-align: center; color: white; transition: all 0.3s; }
    [data-testid="stSidebar"] { background: linear-gradient(180deg, #0f2027, #203a43); }
    [data-testid="stSidebar"] * { color: white; }
    .stButton > button { background: linear-gradient(135deg, #667eea, #764ba2); color: white; border: none; border-radius: 10px; font-weight: bold; transition: all 0.3s; width: 100%; }
    .stButton > button:hover { transform: translateY(-2px); box-shadow: 0 5px 15px rgba(102,126,234,0.4); }
    .login-card { background: rgba(255,255,255,0.1); backdrop-filter: blur(10px); padding: 2rem; border-radius: 20px; text-align: center; animation: fadeIn 0.6s; }
    .footer { text-align: center; padding: 1rem; margin-top: 2rem; color: rgba(255,255,255,0.5); border-top: 1px solid rgba(255,255,255,0.1); }
    .ia-message-user { background: linear-gradient(135deg, #667eea, #764ba2); border-radius: 15px; padding: 1rem; margin: 0.5rem 0; color: white; }
    .ia-message-bot { background: rgba(102,126,234,0.2); border-radius: 15px; padding: 1rem; margin: 0.5rem 0; border-left: 3px solid #667eea; }
    .fase-badge { background: linear-gradient(135deg, #667eea, #764ba2); padding: 0.5rem; border-radius: 20px; text-align: center; margin-bottom: 1rem; }
    .stProgress > div > div { background-color: #667eea; }
    .diagnostico-box { background: linear-gradient(135deg, #667eea20, #764ba220); border-left: 4px solid #ff6600; padding: 1rem; border-radius: 10px; margin: 1rem 0; }
    .ia-status { background: #00b4db; padding: 0.3rem; border-radius: 10px; text-align: center; font-size: 0.8rem; margin-bottom: 0.5rem; }
</style>
""", unsafe_allow_html=True)

def mostrar_fases():
    fases = [
        {"num": 1, "nombre": "Diagnóstico", "icono": "🔍"},
        {"num": 2, "nombre": "Peligros GTC-45", "icono": "⚠️"},
        {"num": 3, "nombre": "Evaluación Riesgos", "icono": "📊"},
        {"num": 4, "nombre": "Plan de Acción", "icono": "📋"},
        {"num": 5, "nombre": "Implementación", "icono": "🚀"},
        {"num": 6, "nombre": "Seguimiento", "icono": "📈"}
    ]
    st.markdown("### 📍 Mapa del Proyecto - Ciclo PHVA")
    cols = st.columns(6)
    for i, fase in enumerate(fases):
        with cols[i]:
            completada = False
            if fase["num"] == 1 and st.session_state.empresa.get("nombre", "").strip() and st.session_state.empresa.get("trabajadores", 0) >= 1:
                completada = True
            elif fase["num"] == 2 and len(st.session_state.peligros) > 0:
                completada = True
            elif fase["num"] == 3 and len(st.session_state.matriz_riesgos) > 0:
                completada = True
            elif fase["num"] == 4 and len(st.session_state.plan_accion) > 0:
                completada = True
            elif fase["num"] == 5 and len(st.session_state.capacitaciones) > 0:
                completada = True
            elif fase["num"] == 6 and len(st.session_state.incidentes) > 0:
                completada = True
            clase = "fase-actual" if fase["num"] == st.session_state.fase_actual else "fase-completada" if completada else ""
            st.markdown(f'<div class="fase-card {clase}"><h2>{fase["icono"]}</h2><h4>Fase {fase["num"]}</h4><p><small>{fase["nombre"]}</small></p>{"✅" if completada else "○"}</div>', unsafe_allow_html=True)
    st.progress(calcular_progreso() / 100)
    st.caption(f"**Progreso total:** {calcular_progreso()}% completado")

def login_screen():
    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        st.markdown('<div class="login-card">', unsafe_allow_html=True)
        st.image("https://cdn-icons-png.flaticon.com/512/2917/2917995.png", width=100)
        st.markdown("<h1>🔄 SG-SST PHVA</h1>", unsafe_allow_html=True)
        st.markdown("<h3>IA Inteligente - Gemini + Groq</h3>", unsafe_allow_html=True)
        with st.form("login_form"):
            username = st.text_input("👤 Usuario")
            password = st.text_input("🔒 Contraseña", type="password")
            if st.form_submit_button("🚀 Ingresar", use_container_width=True):
                if username == "admin" and password == "sst2024":
                    st.session_state.authenticated = True
                    st.session_state.username = username
                    st.rerun()
                else:
                    st.error("❌ Use: admin / sst2024")
        st.markdown('</div>', unsafe_allow_html=True)
        st.caption("👨‍💻 Ing. Jan Benitez & Ing. Neiris Pallares")

def dashboard():
    st.markdown('<div class="main-header"><h1>📊 Dashboard SG-SST PHVA</h1><p>IA activa en todos los módulos</p></div>', unsafe_allow_html=True)
    mostrar_fases()
    st.markdown("---")
    col1, col2, col3, col4, col5, col6 = st.columns(6)
    with col1: st.metric("🔍 Fase 1", "✅" if st.session_state.empresa.get("nombre") else "⏳")
    with col2: st.metric("⚠️ Fase 2", f"{len(st.session_state.peligros)}")
    with col3: st.metric("📊 Fase 3", f"{len(st.session_state.matriz_riesgos)}")
    with col4: st.metric("📋 Fase 4", f"{len(st.session_state.plan_accion)}")
    with col5: st.metric("🚀 Fase 5", f"{len(st.session_state.capacitaciones)}")
    with col6: st.metric("📈 Fase 6", f"{len(st.session_state.incidentes)}")
    st.markdown("---")
    datos = [100 if st.session_state.empresa.get("nombre") else 0,
             min(100, len(st.session_state.peligros) * 33),
             min(100, len(st.session_state.matriz_riesgos) * 33),
             min(100, len(st.session_state.plan_accion) * 33),
             min(100, len(st.session_state.capacitaciones) * 33),
             min(100, len(st.session_state.incidentes) * 33)]
    fig = go.Figure(data=[go.Bar(x=['F1', 'F2', 'F3', 'F4', 'F5', 'F6'], y=datos, marker_color=['#4ECDC4','#FFB347','#45B7D1','#96CEB4','#FFEAA7','#FF6B6B'])])
    fig.update_layout(title="Progreso por Fase", paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(255,255,255,0.1)', font_color='white', height=400)
    st.plotly_chart(fig, use_container_width=True)
    st.markdown('<div class="ia-status">🤖 IA activa: Gemini + Groq (conecta en Settings → Secrets)</div>', unsafe_allow_html=True)

def fase1_diagnostico():
    st.markdown('<div class="main-header"><h1>🔍 Fase 1: Diagnóstico IA</h1></div>', unsafe_allow_html=True)
    trabajadores_actual = st.session_state.empresa.get("trabajadores", 1)
    with st.form("fase1_form"):
        col1, col2 = st.columns(2)
        with col1:
            nombre = st.text_input("🏢 Nombre de la empresa*", value=st.session_state.empresa.get("nombre", ""))
            nit = st.text_input("📄 NIT", value=st.session_state.empresa.get("nit", ""))
        with col2:
            trabajadores = st.number_input("👥 Número de trabajadores*", min_value=1, value=trabajadores_actual)
            ciudad = st.text_input("📍 Ciudad", value=st.session_state.empresa.get("ciudad", ""))
            sector = st.selectbox("🏭 Sector", ["Construcción", "Manufactura", "Servicios", "Minería", "Salud", "Educación", "Comercio"], 
                                 index=0 if not st.session_state.empresa.get("sector") else ["Construcción", "Manufactura", "Servicios", "Minería", "Salud", "Educación", "Comercio"].index(st.session_state.empresa.get("sector", "Construcción")))
        submitted = st.form_submit_button("💾 Guardar y Generar Diagnóstico con IA", use_container_width=True)
        if submitted and nombre.strip() and trabajadores >= 1:
            st.session_state.empresa = {"nombre": nombre, "nit": nit, "trabajadores": trabajadores, "ciudad": ciudad, "sector": sector}
            st.success("✅ Datos guardados. Generando diagnóstico...")
            with st.spinner("🧠 IA analizando..."):
                st.session_state.diagnostico_generado = generar_diagnostico_ia()
            if st.session_state.fase_actual == 1:
                st.session_state.fase_actual = 2
                st.rerun()
    if st.session_state.diagnostico_generado:
        st.markdown("### 📋 DIAGNÓSTICO GENERADO POR IA")
        st.markdown(f'<div class="diagnostico-box">{st.session_state.diagnostico_generado}</div>', unsafe_allow_html=True)

def fase2_peligros():
    st.markdown('<div class="main-header"><h1>⚠️ Fase 2: Identificación de Peligros IA</h1></div>', unsafe_allow_html=True)
    tab1, tab2 = st.tabs(["📋 Lista", "➕ IA Recomienda"])
    with tab1:
        if st.session_state.peligros:
            st.dataframe(pd.DataFrame(st.session_state.peligros), use_container_width=True)
            if st.button("✅ Avanzar a Fase 3"):
                st.session_state.fase_actual = 3
                st.rerun()
    with tab2:
        with st.form("peligro_ia"):
            descripcion = st.text_area("Describe la actividad", height=100)
            if st.form_submit_button("🤖 Recomendar con IA"):
                if descripcion:
                    with st.spinner("🧠 IA analizando..."):
                        recomendacion = recomendar_con_ia("peligro", descripcion)
                        st.info(recomendacion)

def fase3_riesgos():
    st.markdown('<div class="main-header"><h1>📊 Fase 3: Evaluación IA</h1></div>', unsafe_allow_html=True)
    if st.button("🤖 Evaluar con IA"):
        with st.spinner("🧠 IA evaluando..."):
            analisis = recomendar_con_ia("accion", "")
            st.info(analisis)
    if st.button("✅ Completar evaluación"):
        st.session_state.matriz_riesgos = st.session_state.peligros.copy()
        st.session_state.fase_actual = 4
        st.rerun()

def fase4_plan_accion():
    st.markdown('<div class="main-header"><h1>📋 Fase 4: Plan de Acción IA</h1></div>', unsafe_allow_html=True)
    if st.button("🤖 Recomendar acciones con IA"):
        with st.spinner("🧠 IA generando recomendaciones..."):
            recomendaciones = recomendar_con_ia("accion", "")
            st.info(recomendaciones)
    with st.form("nueva_accion"):
        accion = st.text_area("Acción")
        if st.form_submit_button("Agregar") and accion:
            st.session_state.plan_accion.append({"accion": accion, "estado": "Pendiente"})
            st.rerun()
    if st.button("✅ Completar Plan"):
        st.session_state.fase_actual = 5
        st.rerun()

def fase5_implementacion():
    st.markdown('<div class="main-header"><h1>🚀 Fase 5: Capacitaciones IA</h1></div>', unsafe_allow_html=True)
    if st.button("🤖 Recomendar capacitaciones con IA"):
        with st.spinner("🧠 IA generando plan..."):
            caps = recomendar_con_ia("capacitacion", "")
            st.info(caps)
    with st.form("nueva_capacitacion"):
        tema = st.text_input("Tema")
        if st.form_submit_button("Programar") and tema:
            st.session_state.capacitaciones.append({"tema": tema})
            st.rerun()
    if len(st.session_state.capacitaciones) >= 1:
        if st.button("✅ Completar Implementación"):
            st.session_state.fase_actual = 6
            st.rerun()

def fase6_seguimiento():
    st.markdown('<div class="main-header"><h1>📈 Fase 6: Seguimiento IA</h1></div>', unsafe_allow_html=True)
    with st.form("nuevo_incidente"):
        desc = st.text_area("Incidente")
        if st.form_submit_button("Reportar") and desc:
            st.session_state.incidentes.append({"desc": desc})
            st.rerun()
    if calcular_progreso() >= 90:
        st.balloons()
        st.success("🎉 PROYECTO COMPLETADO")

def asistente_ia():
    st.markdown('<div class="main-header"><h1>🤖 Asistente IA Virtual</h1><p>Gemini + Groq</p></div>', unsafe_allow_html=True)
    mostrar_fases()
    
    if not st.session_state.ia_messages:
        st.session_state.ia_messages = [{"role": "assistant", "content": f"**🤖 ¡Hola!** Empresa: {st.session_state.empresa.get('nombre', 'No registrada')} | Progreso: {calcular_progreso()}%\n\nPregunta: diagnóstico, recomendaciones, peligros, capacitaciones"}]
    
    for msg in st.session_state.ia_messages:
        if msg["role"] == "user":
            st.markdown(f'<div class="ia-message-user">👤 {msg["content"]}</div>', unsafe_allow_html=True)
        else:
            st.markdown(f'<div class="ia-message-bot">🤖 {msg["content"]}</div>', unsafe_allow_html=True)
    
    if prompt := st.chat_input("Escribe tu consulta..."):
        st.session_state.ia_messages.append({"role": "user", "content": prompt})
        with st.spinner("🧠 IA pensando..."):
            if "diagnóstico" in prompt.lower():
                respuesta = generar_diagnostico_ia()
            else:
                respuesta = generar_con_ia(prompt, f"Contexto: {st.session_state.empresa.get('nombre')}")
                if not respuesta:
                    respuesta = f"Datos actuales: {calcular_progreso()}% completado. ¿Necesitas diagnóstico o recomendaciones?"
        st.session_state.ia_messages.append({"role": "assistant", "content": respuesta})
        st.rerun()

# ==================== MAIN ====================
if not st.session_state.authenticated:
    login_screen()
else:
    with st.sidebar:
        st.image("https://cdn-icons-png.flaticon.com/512/2917/2917995.png", width=60)
        st.markdown("### 🔄 SG-SST PHVA")
        st.markdown(f"**👤** {st.session_state.username}")
        st.markdown("---")
        fases_nombres = {1:"🔍 Diagnóstico", 2:"⚠️ Peligros", 3:"📊 Riesgos", 4:"📋 Plan", 5:"🚀 Implementación", 6:"📈 Seguimiento"}
        st.markdown(f'<div class="fase-badge"><strong>📍 FASE ACTUAL</strong><br>{fases_nombres[st.session_state.fase_actual]}</div>', unsafe_allow_html=True)
        st.progress(calcular_progreso() / 100)
        st.markdown("---")
        menu = st.radio("📋 Módulos", ["📊 Dashboard", "🔍 Fase 1", "⚠️ Fase 2", "📊 Fase 3", "📋 Fase 4", "🚀 Fase 5", "📈 Fase 6", "🤖 Asistente IA"])
        st.markdown("---")
        st.caption("👨‍💻 Ing. Jan Benitez & Ing. Neiris Pallares")
        if st.button("🚪 Cerrar Sesión"):
            st.session_state.authenticated = False
            st.rerun()
    
    if menu == "📊 Dashboard":
        dashboard()
    elif menu == "🔍 Fase 1":
        fase1_diagnostico()
    elif menu == "⚠️ Fase 2":
        fase2_peligros()
    elif menu == "📊 Fase 3":
        fase3_riesgos()
    elif menu == "📋 Fase 4":
        fase4_plan_accion()
    elif menu == "🚀 Fase 5":
        fase5_implementacion()
    elif menu == "📈 Fase 6":
        fase6_seguimiento()
    elif menu == "🤖 Asistente IA":
        asistente_ia()

st.markdown('<div class="footer"><p>SG-SST PHVA - IA Gemini + Groq © 2024</p></div>', unsafe_allow_html=True)
