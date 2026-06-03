import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import plotly.graph_objects as go

st.set_page_config(
    page_title="SG-SST PHVA - Gestión SST",
    page_icon="🔄",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==================== INICIALIZACIÓN ====================
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
    st.session_state.empresa = {"nombre": "", "trabajadores": 1, "nit": "", "ciudad": ""}
if "plan_accion" not in st.session_state:
    st.session_state.plan_accion = []
if "matriz_riesgos" not in st.session_state:
    st.session_state.matriz_riesgos = []
if "ia_messages" not in st.session_state:
    st.session_state.ia_messages = []   # Solo para historial visual

# ==================== FUNCIONES ====================
def calcular_nivel_riesgo(p, s):
    puntaje = p * s
    if puntaje >= 9: return "I"
    elif puntaje >= 6: return "II"
    elif puntaje >= 4: return "III"
    else: return "IV"

def calcular_progreso():
    completadas = 0
    if st.session_state.empresa.get("nombre", "").strip() != "":
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

def responder_ia(pregunta):
    """Responde leyendo los valores actuales de session_state en tiempo real"""
    emp = st.session_state.empresa
    nombre_emp = emp.get("nombre", "").strip()
    if not nombre_emp:
        nombre_emp = "No registrada"
    
    progreso = calcular_progreso()
    fase = st.session_state.fase_actual
    total_peligros = len(st.session_state.peligros)
    total_cap = len(st.session_state.capacitaciones)
    total_inc = len(st.session_state.incidentes)
    total_acc = len(st.session_state.plan_accion)
    
    pregunta_low = pregunta.lower()
    
    if "empresa" in pregunta_low or "diagnóstico" in pregunta_low or "información" in pregunta_low:
        if nombre_emp != "No registrada":
            return f"**🏢 DATOS DE TU EMPRESA**\n\n- **Nombre:** {nombre_emp}\n- **NIT:** {emp.get('nit', 'No registrado')}\n- **Trabajadores:** {emp.get('trabajadores', 0)}\n- **Ciudad:** {emp.get('ciudad', 'No registrada')}\n- **Progreso:** {progreso}%\n- **Fase:** {fase}/6"
        else:
            return "⚠️ Aún no has registrado tu empresa. Ve a **Fase 1** y completa el formulario."
    
    elif "progreso" in pregunta_low or "avance" in pregunta_low or "fase" in pregunta_low:
        return f"**📊 PROGRESO ACTUAL**\n\n- **Progreso total:** {progreso}%\n- **Fase actual:** {fase}/6\n- **Detalle:**\n  - Diagnóstico: {'✅' if nombre_emp != 'No registrada' else '⏳'}\n  - Peligros: {total_peligros} identificados\n  - Riesgos: {len(st.session_state.matriz_riesgos)} evaluados\n  - Plan: {total_acc} acciones\n  - Capacitaciones: {total_cap}\n  - Incidentes: {total_inc}"
    
    elif "peligro" in pregunta_low or "gtc" in pregunta_low:
        if total_peligros > 0:
            lista = "\n".join([f"- {p['peligro']} (Nivel {p['nivel']})" for p in st.session_state.peligros[:5]])
            return f"**⚠️ PELIGROS IDENTIFICADOS**\n\n{lista}\n\n**Total:** {total_peligros}"
        else:
            return "⚠️ No hay peligros registrados. Ve a **Fase 2**."
    
    elif "capacitacion" in pregunta_low:
        if total_cap > 0:
            lista_cap = "\n".join([f"- {c['tema']} ({c['fecha']})" for c in st.session_state.capacitaciones])
            return f"**📚 CAPACITACIONES**\n\n{lista_cap}\n\n**Total:** {total_cap}"
        else:
            return "📚 No hay capacitaciones programadas. Ve a **Fase 5**."
    
    elif "incidente" in pregunta_low:
        if total_inc > 0:
            lista_inc = "\n".join([f"- {i['tipo']}: {i['descripcion'][:50]}" for i in st.session_state.incidentes])
            return f"**📋 INCIDENTES REPORTADOS**\n\n{lista_inc}\n\n**Total:** {total_inc}"
        else:
            return "✅ No se han reportado incidentes."
    
    else:
        return f"**🤖 ASISTENTE IA**\n\n- **Empresa:** {nombre_emp}\n- **Progreso:** {progreso}%\n- **Fase:** {fase}/6\n- **Peligros:** {total_peligros}\n- **Capacitaciones:** {total_cap}\n- **Incidentes:** {total_inc}\n\nPregúntame sobre: empresa, progreso, peligros, capacitaciones, incidentes."

# ==================== CSS (igual, se omite por brevedad, pero se mantiene) ====================
st.markdown("""
<style>
    @keyframes fadeIn { from { opacity: 0; transform: translateY(20px); } to { opacity: 1; transform: translateY(0); } }
    @keyframes slideIn { from { transform: translateX(-30px); opacity: 0; } to { transform: translateX(0); opacity: 1; } }
    @keyframes glow { 0% { box-shadow: 0 0 5px rgba(102,126,234,0.5); } 100% { box-shadow: 0 0 20px rgba(102,126,234,0.8); } }
    
    .stApp { background: linear-gradient(135deg, #0f2027, #203a43, #2c5364) !important; }
    
    .main-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.5rem;
        border-radius: 20px;
        color: white;
        text-align: center;
        margin-bottom: 1.5rem;
        animation: slideIn 0.6s;
        box-shadow: 0 10px 30px rgba(0,0,0,0.3);
    }
    
    .fase-card {
        background: rgba(255,255,255,0.1);
        backdrop-filter: blur(10px);
        padding: 0.8rem;
        border-radius: 15px;
        margin: 0.3rem;
        text-align: center;
        transition: all 0.3s;
    }
    .fase-card:hover { transform: translateY(-5px); background: rgba(255,255,255,0.2); }
    .fase-completada { border: 2px solid #00ff00; background: rgba(0,255,0,0.1); }
    .fase-actual { border: 2px solid #ffcc00; background: rgba(255,204,0,0.15); transform: scale(1.02); animation: glow 1.5s infinite; }
    
    .metric-card {
        background: rgba(255,255,255,0.1);
        backdrop-filter: blur(10px);
        padding: 1rem;
        border-radius: 15px;
        text-align: center;
        color: white;
        transition: all 0.3s;
    }
    .metric-card:hover { transform: translateY(-5px); background: rgba(255,255,255,0.2); }
    
    [data-testid="stSidebar"] { background: linear-gradient(180deg, #0f2027, #203a43); }
    [data-testid="stSidebar"] * { color: white; }
    
    .stButton > button {
        background: linear-gradient(135deg, #667eea, #764ba2);
        color: white;
        border: none;
        border-radius: 10px;
        font-weight: bold;
        transition: all 0.3s;
        width: 100%;
    }
    .stButton > button:hover { transform: translateY(-2px); box-shadow: 0 5px 15px rgba(102,126,234,0.4); }
    
    .login-card {
        background: rgba(255,255,255,0.1);
        backdrop-filter: blur(10px);
        padding: 2rem;
        border-radius: 20px;
        text-align: center;
        animation: fadeIn 0.6s;
    }
    
    .footer {
        text-align: center;
        padding: 1rem;
        margin-top: 2rem;
        color: rgba(255,255,255,0.5);
        border-top: 1px solid rgba(255,255,255,0.1);
    }
    
    .ia-message-user {
        background: linear-gradient(135deg, #667eea, #764ba2);
        border-radius: 15px;
        padding: 1rem;
        margin: 0.5rem 0;
        color: white;
        animation: slideIn 0.3s;
    }
    .ia-message-bot {
        background: rgba(102,126,234,0.2);
        border-radius: 15px;
        padding: 1rem;
        margin: 0.5rem 0;
        border-left: 3px solid #667eea;
        animation: slideIn 0.3s;
    }
    
    .fase-badge {
        background: linear-gradient(135deg, #667eea, #764ba2);
        padding: 0.5rem;
        border-radius: 20px;
        text-align: center;
        margin-bottom: 1rem;
    }
    
    .stProgress > div > div { background-color: #667eea; }
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
            if fase["num"] == 1 and st.session_state.empresa.get("nombre", "").strip() != "":
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
        st.markdown("<h3>Ciclo PHVA - 6 Fases Completas</h3>", unsafe_allow_html=True)
        
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
        st.markdown("---")
        st.caption("👨‍💻 Ing. Jan Benitez & Ing. Neiris Pallares")

def dashboard():
    st.markdown('<div class="main-header"><h1>📊 Dashboard SG-SST PHVA</h1><p>Planificar → Hacer → Verificar → Actuar</p></div>', unsafe_allow_html=True)
    mostrar_fases()
    st.markdown("---")
    
    col1, col2, col3, col4, col5, col6 = st.columns(6)
    with col1:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.metric("🔍 Fase 1", "✅" if st.session_state.empresa.get("nombre", "").strip() else "⏳")
        st.markdown('</div>', unsafe_allow_html=True)
    with col2:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.metric("⚠️ Fase 2", f"{len(st.session_state.peligros)}")
        st.markdown('</div>', unsafe_allow_html=True)
    with col3:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.metric("📊 Fase 3", f"{len(st.session_state.matriz_riesgos)}")
        st.markdown('</div>', unsafe_allow_html=True)
    with col4:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.metric("📋 Fase 4", f"{len(st.session_state.plan_accion)}")
        st.markdown('</div>', unsafe_allow_html=True)
    with col5:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.metric("🚀 Fase 5", f"{len(st.session_state.capacitaciones)}")
        st.markdown('</div>', unsafe_allow_html=True)
    with col6:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.metric("📈 Fase 6", f"{len(st.session_state.incidentes)}")
        st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown("---")
    datos = [100 if st.session_state.empresa.get("nombre", "").strip() else 0,
             min(100, len(st.session_state.peligros) * 33),
             min(100, len(st.session_state.matriz_riesgos) * 33),
             min(100, len(st.session_state.plan_accion) * 33),
             min(100, len(st.session_state.capacitaciones) * 33),
             min(100, len(st.session_state.incidentes) * 33)]
    
    fig = go.Figure(data=[go.Bar(x=['F1', 'F2', 'F3', 'F4', 'F5', 'F6'], y=datos, marker_color=['#4ECDC4','#FFB347','#45B7D1','#96CEB4','#FFEAA7','#FF6B6B'])])
    fig.update_layout(title="Progreso por Fase", paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(255,255,255,0.1)', font_color='white', height=400)
    st.plotly_chart(fig, use_container_width=True)

# ==================== FASES (simplificadas pero funcionales) ====================
def fase1_diagnostico():
    st.markdown('<div class="main-header"><h1>🔍 Fase 1: Diagnóstico Inicial</h1><p>Registra la información de tu empresa</p></div>', unsafe_allow_html=True)
    with st.form("fase1"):
        col1, col2 = st.columns(2)
        with col1:
            nombre = st.text_input("🏢 Nombre de la empresa", value=st.session_state.empresa.get("nombre", ""))
            nit = st.text_input("📄 NIT", value=st.session_state.empresa.get("nit", ""))
        with col2:
            trabajadores = st.number_input("👥 Número de trabajadores", min_value=1, value=st.session_state.empresa.get("trabajadores", 1))
            ciudad = st.text_input("📍 Ciudad", value=st.session_state.empresa.get("ciudad", ""))
        if st.form_submit_button("💾 Guardar Diagnóstico", use_container_width=True):
            if nombre.strip():
                st.session_state.empresa["nombre"] = nombre
                st.session_state.empresa["nit"] = nit
                st.session_state.empresa["trabajadores"] = trabajadores
                st.session_state.empresa["ciudad"] = ciudad
                st.success("✅ Información guardada. Progreso actualizado.")
                if st.session_state.fase_actual == 1:
                    st.session_state.fase_actual = 2
                    st.rerun()
            else:
                st.error("El nombre es obligatorio.")
    
    if st.session_state.empresa.get("nombre"):
        st.markdown("---")
        st.subheader("📋 Información actual")
        st.write(f"**Empresa:** {st.session_state.empresa['nombre']}")
        st.write(f"**NIT:** {st.session_state.empresa.get('nit', 'No registrado')}")
        st.write(f"**Trabajadores:** {st.session_state.empresa['trabajadores']}")
        st.write(f"**Ciudad:** {st.session_state.empresa.get('ciudad', 'No registrada')}")

def fase2_peligros():
    st.markdown('<div class="main-header"><h1>⚠️ Fase 2: Identificación de Peligros</h1><p>Metodología GTC-45</p></div>', unsafe_allow_html=True)
    tab1, tab2 = st.tabs(["📋 Lista de Peligros", "➕ Nuevo Peligro"])
    with tab1:
        if st.session_state.peligros:
            st.dataframe(pd.DataFrame(st.session_state.peligros), use_container_width=True)
            if st.button("✅ Avanzar a Fase 3", use_container_width=True):
                st.session_state.fase_actual = 3
                st.rerun()
        else:
            st.info("No hay peligros")
    with tab2:
        with st.form("nuevo_peligro"):
            col1, col2 = st.columns(2)
            with col1:
                proceso = st.selectbox("Proceso", ["Administrativo", "Operativo", "Mantenimiento", "Logística"])
                peligro = st.text_input("Descripción")
                tipo = st.selectbox("Tipo", ["Biológico", "Físico", "Químico", "Psicosocial", "Ergonómico", "Mecánico"])
            with col2:
                prob = st.slider("Probabilidad (1-4)", 1, 4, 3)
                sev = st.slider("Severidad (1-3)", 1, 3, 2)
                nivel = calcular_nivel_riesgo(prob, sev)
                st.info(f"Nivel: {nivel}")
            controles = st.text_area("Controles")
            if st.form_submit_button("Identificar"):
                if peligro:
                    st.session_state.peligros.append({
                        "proceso": proceso,
                        "peligro": peligro,
                        "tipo": tipo,
                        "probabilidad": prob,
                        "severidad": sev,
                        "nivel": nivel,
                        "controles": controles
                    })
                    st.rerun()

def fase3_riesgos():
    st.markdown('<div class="main-header"><h1>📊 Fase 3: Evaluación de Riesgos</h1></div>', unsafe_allow_html=True)
    if st.session_state.peligros:
        for p in st.session_state.peligros:
            st.markdown(f"- {p['peligro']} (Nivel {p['nivel']})")
        if st.button("Completar evaluación"):
            st.session_state.matriz_riesgos = st.session_state.peligros.copy()
            st.session_state.fase_actual = 4
            st.rerun()
    else:
        st.warning("Primero identifica peligros")

def fase4_plan_accion():
    st.markdown('<div class="main-header"><h1>📋 Fase 4: Plan de Acción</h1></div>', unsafe_allow_html=True)
    tab1, tab2 = st.tabs(["Plan", "Nueva Acción"])
    with tab1:
        if st.session_state.plan_accion:
            st.dataframe(pd.DataFrame(st.session_state.plan_accion))
            if st.button("Completar Plan"):
                st.session_state.fase_actual = 5
                st.rerun()
    with tab2:
        with st.form("nueva_accion"):
            accion = st.text_area("Acción")
            responsable = st.text_input("Responsable")
            if st.form_submit_button("Agregar"):
                st.session_state.plan_accion.append({"accion": accion, "responsable": responsable, "estado": "Pendiente"})
                st.rerun()

def fase5_implementacion():
    st.markdown('<div class="main-header"><h1>🚀 Fase 5: Implementación</h1></div>', unsafe_allow_html=True)
    with st.form("nueva_capacitacion"):
        tema = st.text_input("Capacitación")
        if st.form_submit_button("Programar"):
            st.session_state.capacitaciones.append({"tema": tema, "fecha": str(datetime.now())})
            st.rerun()
    if st.session_state.capacitaciones:
        st.write("Capacitaciones programadas:", len(st.session_state.capacitaciones))
    if st.button("Completar Implementación"):
        st.session_state.fase_actual = 6
        st.rerun()

def fase6_seguimiento():
    st.markdown('<div class="main-header"><h1>📈 Fase 6: Seguimiento</h1></div>', unsafe_allow_html=True)
    with st.form("nuevo_incidente"):
        tipo = st.selectbox("Tipo", ["Accidente", "Incidente"])
        desc = st.text_area("Descripción")
        if st.form_submit_button("Reportar"):
            st.session_state.incidentes.append({"tipo": tipo, "descripcion": desc, "fecha": str(datetime.now())})
            st.rerun()
    if calcular_progreso() >= 90:
        st.balloons()
        st.success("Proyecto completado")

# ==================== ASISTENTE IA ====================
def asistente_ia():
    st.markdown('<div class="main-header"><h1>🤖 Asistente IA</h1><p>Experto virtual en SST</p></div>', unsafe_allow_html=True)
    mostrar_fases()
    
    # Botón de recarga manual
    if st.button("🔄 Recargar contexto de IA", use_container_width=True):
        st.session_state.ia_messages = []  # Limpiar historial para refrescar
        st.rerun()
    
    # Mostrar estado actual en un cuadro de depuración
    with st.expander("📊 Datos actuales del proyecto (verificar)"):
        st.json({
            "Empresa": st.session_state.empresa.get("nombre", ""),
            "Progreso": calcular_progreso(),
            "Fase actual": st.session_state.fase_actual,
            "Peligros": len(st.session_state.peligros),
            "Capacitaciones": len(st.session_state.capacitaciones),
            "Incidentes": len(st.session_state.incidentes),
            "Plan de Acción": len(st.session_state.plan_accion)
        })
    
    if not st.session_state.ia_messages:
        nombre_emp = st.session_state.empresa.get("nombre", "").strip()
        if not nombre_emp:
            nombre_emp = "aún no registrada"
        bienvenida = f"**🤖 ¡Hola!** Tu empresa **{nombre_emp}** tiene un progreso del **{calcular_progreso()}%** (Fase {st.session_state.fase_actual}/6).\n\nPregúntame sobre: empresa, progreso, peligros, capacitaciones, incidentes."
        st.session_state.ia_messages = [{"role": "assistant", "content": bienvenida}]
    
    for msg in st.session_state.ia_messages:
        if msg["role"] == "user":
            st.markdown(f'<div class="ia-message-user">👤 {msg["content"]}</div>', unsafe_allow_html=True)
        else:
            st.markdown(f'<div class="ia-message-bot">🤖 {msg["content"]}</div>', unsafe_allow_html=True)
    
    if prompt := st.chat_input("Escribe tu consulta sobre SST..."):
        st.session_state.ia_messages.append({"role": "user", "content": prompt})
        respuesta = responder_ia(prompt)
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
        st.caption(f"{calcular_progreso()}% completado")
        st.markdown("---")
        menu = st.radio("📋 Módulos", [
            "📊 Dashboard",
            "🔍 Fase 1: Diagnóstico",
            "⚠️ Fase 2: Peligros",
            "📊 Fase 3: Riesgos",
            "📋 Fase 4: Plan de Acción",
            "🚀 Fase 5: Implementación",
            "📈 Fase 6: Seguimiento",
            "🤖 Asistente IA"
        ])
        st.markdown("---")
        st.caption("👨‍💻 Ing. Jan Benitez & Ing. Neiris Pallares")
        if st.button("🚪 Cerrar Sesión", use_container_width=True):
            st.session_state.authenticated = False
            st.rerun()
    
    if menu == "📊 Dashboard":
        dashboard()
    elif menu == "🔍 Fase 1: Diagnóstico":
        fase1_diagnostico()
    elif menu == "⚠️ Fase 2: Peligros":
        fase2_peligros()
    elif menu == "📊 Fase 3: Riesgos":
        fase3_riesgos()
    elif menu == "📋 Fase 4: Plan de Acción":
        fase4_plan_accion()
    elif menu == "🚀 Fase 5: Implementación":
        fase5_implementacion()
    elif menu == "📈 Fase 6: Seguimiento":
        fase6_seguimiento()
    elif menu == "🤖 Asistente IA":
        asistente_ia()

st.markdown('<div class="footer"><p>SG-SST PHVA - Sistema de Gestión de Seguridad y Salud en el Trabajo © 2024</p></div>', unsafe_allow_html=True)
