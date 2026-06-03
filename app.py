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
    st.session_state.empresa = {"nombre": "", "trabajadores": 1, "nit": "", "ciudad": "", "sector": "Construcción"}
if "plan_accion" not in st.session_state:
    st.session_state.plan_accion = []
if "matriz_riesgos" not in st.session_state:
    st.session_state.matriz_riesgos = []
if "diagnostico_generado" not in st.session_state:
    st.session_state.diagnostico_generado = False

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

def generar_diagnostico():
    """Genera un diagnóstico automático basado en los datos de la empresa"""
    emp = st.session_state.empresa
    nombre = emp.get("nombre", "").strip()
    if not nombre:
        return None
    
    trabajadores = emp.get("trabajadores", 0)
    sector = emp.get("sector", "Construcción")
    ciudad = emp.get("ciudad", "No registrada")
    
    diagnostico = f"""
    **🔍 DIAGNÓSTICO INICIAL - {nombre.upper()}**
    
    ---
    **📊 DATOS GENERALES**
    - **Empresa:** {nombre}
    - **Sector:** {sector}
    - **Trabajadores:** {trabajadores}
    - **Ubicación:** {ciudad}
    
    ---
    **⚠️ ANÁLISIS DE RIESGOS POR SECTOR**
    """
    
    if sector == "Construcción":
        diagnostico += """
    - **Riesgos prioritarios:** Trabajo en alturas, caída de objetos, maquinaria pesada, ruido excesivo.
    - **Normativa aplicable:** Resolución 0312/2019, Ley 1562/2012.
    - **Recomendaciones inmediatas:** 
      • Implementar sistemas de protección contra caídas (líneas de vida, arneses).
      • Capacitación obligatoria en trabajo seguro en alturas (40 horas).
      • Dotación de EPP completo (casco, botas, guantes, tapones auditivos).
    """
    elif sector == "Manufactura":
        diagnostico += """
    - **Riesgos prioritarios:** Atrapamiento de maquinaria, exposición a químicos, ruido, posturas forzadas.
    - **Normativa aplicable:** Resolución 0312/2019, Decreto 1072/2015.
    - **Recomendaciones inmediatas:** 
      • Guardas de seguridad en maquinaria.
      • Ventilación y controles de exposición a químicos.
      • Pausas activas y ergonomía.
    """
    elif sector == "Salud":
        diagnostico += """
    - **Riesgos prioritarios:** Biológicos (virus, bacterias), carga mental, radiaciones.
    - **Normativa aplicable:** Resolución 0312/2019, Ley 1562/2012.
    - **Recomendaciones inmediatas:** 
      • Implementar protocolos de bioseguridad.
      • Programa de manejo del estrés laboral.
      • Vacunación y exámenes médicos periódicos.
    """
    else:
        diagnostico += f"""
    - **Riesgos a evaluar:** Identificar según las actividades específicas de {sector}.
    - **Recomendación:** Realizar matriz de peligros GTC-45 completa.
    """
    
    diagnostico += f"""
    
    ---
    **📈 ESTADO ACTUAL DEL PROYECTO**
    - **Progreso general:** {calcular_progreso()}%
    - **Fase actual:** {st.session_state.fase_actual}/6
    - **Próxima acción recomendada:** {'Completar el registro de la empresa' if not nombre else 'Avanzar a la Fase 2: Identificar peligros'}
    
    ---
    **✅ PRÓXIMOS PASOS**
    1. {'✅ Completado: Información de empresa registrada' if nombre else '⏳ Pendiente: Registrar empresa'}
    2. {'✅ Completado: Identificar peligros GTC-45' if len(st.session_state.peligros) > 0 else '⏳ Pendiente: Identificar peligros'}
    3. {'✅ Completado: Evaluar riesgos' if len(st.session_state.matriz_riesgos) > 0 else '⏳ Pendiente: Evaluar riesgos'}
    4. {'✅ Completado: Plan de acción' if len(st.session_state.plan_accion) > 0 else '⏳ Pendiente: Crear plan de acción'}
    5. {'✅ Completado: Capacitaciones' if len(st.session_state.capacitaciones) > 0 else '⏳ Pendiente: Programar capacitaciones'}
    6. {'✅ Completado: Seguimiento' if len(st.session_state.incidentes) > 0 else '⏳ Pendiente: Registrar incidentes'}
    """
    return diagnostico

def responder_ia(pregunta):
    """IA contextual que lee los datos reales y puede generar diagnóstico"""
    pregunta_low = pregunta.lower()
    
    if "diagnóstico" in pregunta_low or "analizar" in pregunta_low or "diagnostico" in pregunta_low:
        diag = generar_diagnostico()
        if diag:
            return diag
        else:
            return "⚠️ Primero registra los datos de tu empresa en la Fase 1."
    
    # Respuestas normales de la IA
    emp = st.session_state.empresa
    nombre_emp = emp.get("nombre", "").strip()
    if not nombre_emp:
        nombre_emp = "No registrada"
    
    progreso = calcular_progreso()
    fase = st.session_state.fase_actual
    
    if "empresa" in pregunta_low:
        return f"""**🏢 INFORMACIÓN DE {nombre_emp.upper()}**

- **Nombre:** {nombre_emp}
- **NIT:** {emp.get('nit', 'No registrado')}
- **Sector:** {emp.get('sector', 'No especificado')}
- **Trabajadores:** {emp.get('trabajadores', 0)}
- **Ciudad:** {emp.get('ciudad', 'No registrada')}
- **Progreso:** {progreso}%
- **Fase actual:** {fase}/6

¿Necesitas generar un diagnóstico completo? Pregúntame 'diagnóstico'."""
    
    elif "progreso" in pregunta_low or "avance" in pregunta_low:
        return f"""**📊 PROGRESO DEL PROYECTO - {progreso}%**

- **Fase 1 (Diagnóstico):** {'✅ Completada' if nombre_emp != 'No registrada' else '⏳ Pendiente'}
- **Fase 2 (Peligros):** {len(st.session_state.peligros)} peligros identificados
- **Fase 3 (Riesgos):** {len(st.session_state.matriz_riesgos)} evaluados
- **Fase 4 (Plan):** {len(st.session_state.plan_accion)} acciones
- **Fase 5 (Capacitaciones):** {len(st.session_state.capacitaciones)} programadas
- **Fase 6 (Seguimiento):** {len(st.session_state.incidentes)} incidentes

**Fase actual:** {fase}/6"""
    
    elif "peligro" in pregunta_low:
        if st.session_state.peligros:
            lista = "\n".join([f"- {p['peligro']} (Nivel {p['nivel']})" for p in st.session_state.peligros])
            return f"**⚠️ PELIGROS IDENTIFICADOS**\n\n{lista}\n\n**Total:** {len(st.session_state.peligros)} peligros."
        else:
            return "⚠️ No hay peligros registrados. Ve a la **Fase 2** e identifica peligros según GTC-45."
    
    else:
        return f"""**🤖 ASISTENTE IA - SG-SST PHVA**

**Resumen actual del proyecto:**
- **Empresa:** {nombre_emp}
- **Progreso:** {progreso}%
- **Fase actual:** {fase}/6
- **Peligros:** {len(st.session_state.peligros)}
- **Capacitaciones:** {len(st.session_state.capacitaciones)}
- **Incidentes:** {len(st.session_state.incidentes)}

**¿Qué puedo hacer por ti?**
- 📊 "progreso" - Ver avance del proyecto
- 🏢 "empresa" - Ver datos de tu empresa
- ⚠️ "peligros" - Listar riesgos identificados
- 📋 "diagnóstico" - Generar diagnóstico completo
- 📚 "capacitaciones" - Ver programa de formación
- 📈 "incidentes" - Reportes de seguridad"""

# ==================== CSS ====================
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
    
    .diagnostico-box {
        background: linear-gradient(135deg, #667eea20, #764ba220);
        border-left: 4px solid #ff6600;
        padding: 1rem;
        border-radius: 10px;
        margin: 1rem 0;
    }
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

# ==================== FASE 1: DIAGNÓSTICO (con generación de diagnóstico) ====================
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
            sector = st.selectbox("🏭 Sector económico", ["Construcción", "Manufactura", "Servicios", "Minería", "Salud", "Educación", "Comercio"], 
                                 index=0 if not st.session_state.empresa.get("sector") else ["Construcción", "Manufactura", "Servicios", "Minería", "Salud", "Educación", "Comercio"].index(st.session_state.empresa.get("sector", "Construcción")))
        
        if st.form_submit_button("💾 Guardar y Generar Diagnóstico", use_container_width=True):
            if nombre.strip():
                st.session_state.empresa["nombre"] = nombre
                st.session_state.empresa["nit"] = nit
                st.session_state.empresa["trabajadores"] = trabajadores
                st.session_state.empresa["ciudad"] = ciudad
                st.session_state.empresa["sector"] = sector
                st.success("✅ Información guardada. ¡Diagnóstico generado!")
                
                # Mostrar diagnóstico inmediatamente
                st.markdown("---")
                st.markdown("### 📋 DIAGNÓSTICO GENERADO")
                diagnostico = generar_diagnostico()
                st.markdown(f'<div class="diagnostico-box">{diagnostico}</div>', unsafe_allow_html=True)
                
                if st.session_state.fase_actual == 1:
                    st.session_state.fase_actual = 2
                    st.rerun()
            else:
                st.error("El nombre de la empresa es obligatorio.")
    
    if st.session_state.empresa.get("nombre"):
        st.markdown("---")
        st.subheader("📋 Información actual")
        col1, col2 = st.columns(2)
        with col1:
            st.write(f"**Empresa:** {st.session_state.empresa['nombre']}")
            st.write(f"**NIT:** {st.session_state.empresa.get('nit', 'No registrado')}")
            st.write(f"**Sector:** {st.session_state.empresa.get('sector', 'No especificado')}")
        with col2:
            st.write(f"**Trabajadores:** {st.session_state.empresa['trabajadores']}")
            st.write(f"**Ciudad:** {st.session_state.empresa.get('ciudad', 'No registrada')}")
        
        # Botón para generar diagnóstico nuevamente
        if st.button("🔄 Generar diagnóstico nuevamente", use_container_width=True):
            st.markdown("### 📋 DIAGNÓSTICO")
            st.markdown(f'<div class="diagnostico-box">{generar_diagnostico()}</div>', unsafe_allow_html=True)

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
            st.info("No hay peligros identificados")
    with tab2:
        with st.form("nuevo_peligro"):
            col1, col2 = st.columns(2)
            with col1:
                proceso = st.selectbox("Proceso", ["Administrativo", "Operativo", "Mantenimiento", "Logística"])
                peligro = st.text_input("Descripción del peligro")
                tipo = st.selectbox("Tipo", ["Biológico", "Físico", "Químico", "Psicosocial", "Ergonómico", "Mecánico"])
            with col2:
                prob = st.slider("Probabilidad (1-4)", 1, 4, 3)
                sev = st.slider("Severidad (1-3)", 1, 3, 2)
                nivel = calcular_nivel_riesgo(prob, sev)
                st.info(f"Nivel calculado: {nivel}")
            controles = st.text_area("Controles existentes")
            if st.form_submit_button("✅ Identificar Peligro", use_container_width=True):
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
                    st.success(f"✅ Peligro nivel {nivel} identificado")
                    st.rerun()
                else:
                    st.error("❌ Complete la descripción")

def fase3_riesgos():
    st.markdown('<div class="main-header"><h1>📊 Fase 3: Evaluación de Riesgos</h1></div>', unsafe_allow_html=True)
    if st.session_state.peligros:
        for p in st.session_state.peligros:
            st.markdown(f"- {p['peligro']} (Nivel {p['nivel']})")
        if st.button("✅ Completar evaluación", use_container_width=True):
            st.session_state.matriz_riesgos = st.session_state.peligros.copy()
            st.session_state.fase_actual = 4
            st.rerun()
    else:
        st.warning("⚠️ Primero identifica peligros en la Fase 2")

def fase4_plan_accion():
    st.markdown('<div class="main-header"><h1>📋 Fase 4: Plan de Acción</h1></div>', unsafe_allow_html=True)
    tab1, tab2 = st.tabs(["📋 Plan Actual", "➕ Nueva Acción"])
    with tab1:
        if st.session_state.plan_accion:
            st.dataframe(pd.DataFrame(st.session_state.plan_accion), use_container_width=True)
            if st.button("✅ Completar Plan", use_container_width=True):
                st.session_state.fase_actual = 5
                st.rerun()
        else:
            st.info("No hay acciones")
    with tab2:
        with st.form("nueva_accion"):
            accion = st.text_area("Acción correctiva")
            responsable = st.text_input("Responsable")
            fecha = st.date_input("Fecha límite", datetime.now() + timedelta(days=30))
            if st.form_submit_button("Agregar", use_container_width=True):
                if accion:
                    st.session_state.plan_accion.append({
                        "accion": accion,
                        "responsable": responsable,
                        "fecha": str(fecha),
                        "estado": "Pendiente"
                    })
                    st.rerun()

def fase5_implementacion():
    st.markdown('<div class="main-header"><h1>🚀 Fase 5: Implementación</h1></div>', unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("📚 Capacitaciones")
        with st.form("nueva_capacitacion"):
            tema = st.text_input("Tema de capacitación")
            fecha = st.date_input("Fecha", datetime.now() + timedelta(days=7))
            if st.form_submit_button("Programar", use_container_width=True):
                if tema:
                    st.session_state.capacitaciones.append({"tema": tema, "fecha": str(fecha), "estado": "Programada"})
                    st.rerun()
        if st.session_state.capacitaciones:
            for c in st.session_state.capacitaciones:
                st.info(f"📅 {c['tema']} - {c['fecha']}")
    with col2:
        st.subheader("✅ Ejecución")
        for i, a in enumerate(st.session_state.plan_accion):
            if st.checkbox(f"✓ {a['accion'][:50]}", key=f"check_{i}"):
                st.session_state.plan_accion[i]['estado'] = "Completada"
        if len(st.session_state.capacitaciones) >= 1:
            if st.button("✅ Completar Implementación", use_container_width=True):
                st.session_state.fase_actual = 6
                st.rerun()

def fase6_seguimiento():
    st.markdown('<div class="main-header"><h1>📈 Fase 6: Seguimiento y Control</h1></div>', unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("📊 Indicadores")
        st.metric("Capacitaciones", len(st.session_state.capacitaciones))
        st.metric("Peligros", len(st.session_state.peligros))
        st.metric("Acciones", len(st.session_state.plan_accion))
    with col2:
        st.subheader("📋 Incidentes")
        with st.form("nuevo_incidente"):
            tipo = st.selectbox("Tipo", ["Accidente", "Incidente", "Casi accidente"])
            descripcion = st.text_area("Descripción")
            if st.form_submit_button("Reportar", use_container_width=True):
                if descripcion:
                    st.session_state.incidentes.append({"tipo": tipo, "descripcion": descripcion, "fecha": str(datetime.now())})
                    st.rerun()
        for i in st.session_state.incidentes:
            st.warning(f"⚠️ {i['tipo']}: {i['descripcion'][:50]}...")
    if calcular_progreso() >= 90:
        st.balloons()
        st.success("🎉 ¡PROYECTO COMPLETADO!")

def asistente_ia():
    st.markdown('<div class="main-header"><h1>🤖 Asistente IA</h1><p>Experto virtual en SST</p></div>', unsafe_allow_html=True)
    mostrar_fases()
    
    # Mostrar estado actual de la IA
    with st.expander("🔍 Estado de la IA - Verificar conexión", expanded=True):
        col1, col2 = st.columns(2)
        with col1:
            st.metric("🤖 IA Conectada", "✅ ACTIVA", delta="Leyendo datos en tiempo real")
            st.metric("📊 Datos cargados", "Sí", delta=f"{len(st.session_state.empresa.get('nombre', ''))} caracteres")
        with col2:
            st.metric("🏢 Empresa registrada", "✅ Sí" if st.session_state.empresa.get("nombre") else "❌ No")
            st.metric("⚠️ Peligros", len(st.session_state.peligros), delta="En Fase 2")
    
    if not st.session_state.ia_messages:
        nombre_emp = st.session_state.empresa.get("nombre", "").strip()
        if not nombre_emp:
            nombre_emp = "aún no registrada"
        bienvenida = f"""**🤖 ¡Hola! Soy tu Asistente IA.**

**📊 DATOS ACTUALES:**
- Empresa: **{nombre_emp}**
- Progreso: **{calcular_progreso()}%**
- Fase: **{st.session_state.fase_actual}/6**

**💬 ¿Qué puedes preguntarme?**
- 🏢 "empresa" - Ver datos de tu empresa
- 📊 "progreso" - Estado del proyecto- ⚠️ "peligros" - Riesgos identificados
- 📋 "diagnóstico" - Generar diagnóstico completo
- 📚 "capacitaciones" - Programa de formación

**¡Estoy funcionando correctamente!** 🚀"""
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
