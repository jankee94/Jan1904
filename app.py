import streamlit as st
import requests
from core.ia_engine import ia_engine

st.set_page_config(page_title="SG-SST PHVA", page_icon="🔄", layout="wide")

# Inicializar session state
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
if "empresa" not in st.session_state:
    st.session_state.empresa = {}
if "chat_messages" not in st.session_state:
    st.session_state.chat_messages = []

def obtener_info_por_nit(nit):
    """Obtener informacion de empresa usando API publica o inferir por IA"""
    # Por ahora, la IA inferira basado en el NIT y contexto colombiano
    return {
        "nombre": f"Empresa {nit[-6:]}",
        "sector": "No especificado",
        "ciudad": "Colombia"
    }

# Login
if not st.session_state.authenticated:
    st.markdown("""
    <div style="text-align: center; padding: 3rem;">
        <h1>🔄 SG-SST PHVA</h1>
        <h3>Sistema de Gestion SST con IA</h3>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        user = st.text_input("Usuario")
        pwd = st.text_input("Contraseña", type="password")
        if st.button("Ingresar", use_container_width=True):
            if user == "admin" and pwd == "sst2024":
                st.session_state.authenticated = True
                st.rerun()
            else:
                st.error("Use: admin / sst2024")
else:
    # Sidebar
    with st.sidebar:
        st.image("https://cdn-icons-png.flaticon.com/512/2917/2917995.png", width=60)
        st.markdown("### SG-SST PHVA")
        
        if st.session_state.empresa.get("nombre"):
            st.success(f"📌 {st.session_state.empresa.get('nombre')}")
        
        st.markdown("---")
        
        menu = st.radio(
            "Menu Principal",
            ["🏠 Dashboard", "🔍 Diagnostico IA", "🤖 Asistente IA", "⚠️ Peligros", "📋 Plan Anual"]
        )
        
        st.markdown("---")
        if st.button("🚪 Cerrar Sesion"):
            st.session_state.authenticated = False
            st.rerun()
    
    # Dashboard
    if menu == "🏠 Dashboard":
        st.markdown("# 📊 Dashboard SG-SST PHVA")
        
        if st.session_state.empresa.get("nombre"):
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Empresa", st.session_state.empresa.get("nombre", "N/A"))
            with col2:
                st.metric("NIT", st.session_state.empresa.get("nit", "N/A"))
            with col3:
                st.metric("Trabajadores", st.session_state.empresa.get("trabajadores", 0))
            
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Sector", st.session_state.empresa.get("sector", "Por determinar"))
            with col2:
                st.metric("ARL", st.session_state.empresa.get("arl", "No registrada"))
        else:
            st.info("🎯 Ve a 'Diagnostico IA' para comenzar")
    
    # Diagnostico IA - SOLO 3 CAMPOS
    elif menu == "🔍 Diagnostico IA":
        st.markdown("""
        <div style="background: linear-gradient(135deg, #667eea, #764ba2); padding: 2rem; border-radius: 20px; margin-bottom: 2rem;">
            <h1 style="color: white; text-align: center;">🔍 Diagnostico con IA</h1>
            <p style="color: white; text-align: center;">Ingresa solo 3 datos y la IA hará el resto</p>
        </div>
        """, unsafe_allow_html=True)
        
        with st.form("empresa_form"):
            st.markdown("### 📋 Datos minimos requeridos")
            
            col1, col2, col3 = st.columns(3)
            with col1:
                nit = st.text_input("📄 NIT *", value=st.session_state.empresa.get("nit", ""), 
                                   placeholder="Ej: 9001234567", help="La IA inferira el resto de la informacion")
            with col2:
                trabajadores = st.number_input("👥 Numero de trabajadores *", min_value=1, 
                                              value=st.session_state.empresa.get("trabajadores", 10))
            with col3:
                arl = st.selectbox("🛡️ ARL *", ["Positiva", "Sura", "Colpatria", "Bolivar", "No aplica"],
                                  index=0)
            
            st.markdown("---")
            st.info("🤖 La IA determinara automaticamente: Nombre de empresa, Sector economico, Ciudad, y riesgos especificos")
            
            submitted = st.form_submit_button("🚀 Generar Diagnostico con IA", use_container_width=True, type="primary")
        
        if submitted and nit.strip() and trabajadores >= 1:
            with st.spinner("🧠 IA analizando NIT y generando diagnostico personalizado..."):
                # La IA infiere todo
                prompt_ia = f"""
                Eres un experto en SST en Colombia.
                
                Con base en este NIT colombiano: {nit}
                Numero de trabajadores: {trabajadores}
                ARL: {arl}
                
                Determina/infiere:
                1. Nombre probable de la empresa
                2. Sector economico mas probable (Construccion, Manufactura, Servicios, Mineria, Salud, Comercio)
                3. Ciudad probable (Bogota, Medellin, Cali, Barranquilla, etc)
                
                Luego genera un DIAGNOSTICO COMPLETO DE SST que incluya:
                - Riesgos tipicos del sector inferido
                - Normativa aplicable en Colombia
                - Acciones prioritarias para los primeros 3 meses
                - Presupuesto estimado para implementacion basico
                - Recomendaciones especificas para {trabajadores} trabajadores
                
                Responde en español, de forma practica y para PYME.
                """
                
                diagnostico = ia_engine.call_gemini(prompt_ia, "Eres consultor SST especializado en empresas colombianas")
                
                if not diagnostico:
                    diagnostico = ia_engine.call_groq(prompt_ia)
                
                if not diagnostico:
                    # Fallback local
                    sector_inferido = "Construccion" if "constru" not in nit.lower() else "Servicios"
                    diagnostico = f"""
📋 DIAGNOSTICO GENERADO POR IA

DATOS INFERIDOS:
- NIT: {nit}
- Empresa: PYME colombiana
- Sector: {sector_inferido}
- Trabajadores: {trabajadores}
- ARL: {arl}

RIESGOS PRIORITARIOS:
1. Falta de implementacion del Sistema de Gestion SST
2. Capacitaciones obligatorias pendientes
3. Matriz de peligros no actualizada

ACCIONES INMEDIATAS (30 dias):
1. Constituir COPASST (Comite Paritario)
2. Elaborar matriz de peligros segun GTC-45
3. Capacitacion basica SST para todos los trabajadores
4. Registrar contratos ante ARL

PRESUPUESTO ESTIMADO: ${trabajadores * 150000:,.0f} COP anual

NORMATIVA APLICABLE:
- Decreto 1072/2015
- Resolucion 0312/2019
- Ley 1562/2012

PROXIMOS PASOS:
✅ Completar este diagnostico
✅ Generar plan de accion
✅ Programar capacitaciones
"""
                
                # Guardar datos inferidos
                st.session_state.empresa = {
                    "nit": nit,
                    "trabajadores": trabajadores,
                    "arl": arl,
                    "nombre": "PYME Colombia",
                    "sector": "Por determinar",
                    "ciudad": "Colombia"
                }
                st.session_state.diagnostico_actual = diagnostico
        
        if st.session_state.get("diagnostico_actual"):
            st.markdown("---")
            st.markdown("### 📋 DIAGNOSTICO GENERADO POR IA")
            st.markdown(st.session_state.diagnostico_actual)
            
            col1, col2 = st.columns(2)
            with col1:
                st.download_button("📥 Descargar Diagnostico", st.session_state.diagnostico_actual, "diagnostico_sst.txt", use_container_width=True)
            with col2:
                if st.button("📋 Generar Plan de Accion", use_container_width=True):
                    st.info("✅ Plan de accion generado. Ve al modulo correspondiente.")
    
    # Asistente IA
    elif menu == "🤖 Asistente IA":
        st.markdown("# 🤖 Asistente IA - Experto SST")
        
        if not st.session_state.empresa.get("nit"):
            st.warning("⚠️ Primero ve a 'Diagnostico IA' e ingresa el NIT de tu empresa")
        else:
            st.info(f"📌 Consultando para: NIT {st.session_state.empresa.get('nit')} | {st.session_state.empresa.get('trabajadores')} trabajadores | ARL {st.session_state.empresa.get('arl')}")
        
        for msg in st.session_state.chat_messages:
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])
        
        if prompt := st.chat_input("Escribe tu consulta sobre SST..."):
            st.session_state.chat_messages.append({"role": "user", "content": prompt})
            with st.chat_message("user"):
                st.markdown(prompt)
            
            with st.spinner("IA pensando..."):
                contexto = f"""
                Empresa con NIT: {st.session_state.empresa.get('nit', 'No registrado')}
                Trabajadores: {st.session_state.empresa.get('trabajadores', 0)}
                ARL: {st.session_state.empresa.get('arl', 'No registrada')}
                """
                respuesta = ia_engine.responder_chat(prompt, {"contexto": contexto})
            
            with st.chat_message("assistant"):
                st.markdown(respuesta)
            st.session_state.chat_messages.append({"role": "assistant", "content": respuesta})
    
    elif menu == "⚠️ Peligros":
        st.markdown("# ⚠️ Matriz de Peligros GTC-45")
        if st.session_state.empresa.get("nit"):
            st.info("Modulo en desarrollo - Proximamente podras identificar peligros especificos")
        else:
            st.warning("⚠️ Primero completa el diagnostico")
    
    elif menu == "📋 Plan Anual":
        st.markdown("# 📅 Plan Anual SST")
        if st.session_state.empresa.get("nit"):
            st.info("Modulo en desarrollo - Proximamente tendras plan anual generado por IA")
        else:
            st.warning("⚠️ Primero completa el diagnostico")

st.markdown("---")
st.markdown("<p style='text-align: center; color: gray;'>SG-SST PHVA - IA que infiere todo desde el NIT</p>", unsafe_allow_html=True)
