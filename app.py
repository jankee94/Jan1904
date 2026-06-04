import streamlit as st
from modules import diagnostic_ia
from core.ia_engine import ia_engine

st.set_page_config(page_title="SG-SST PHVA", page_icon="🔄", layout="wide")

# Inicializar session state
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
if "empresa" not in st.session_state:
    st.session_state.empresa = {}
if "chat_messages" not in st.session_state:
    st.session_state.chat_messages = []

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
        else:
            st.info("⚠️ Complete datos en Diagnostico IA")
        
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
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Empresa", st.session_state.empresa.get("nombre", "No registrada"))
        with col2:
            st.metric("Sector", st.session_state.empresa.get("sector", "No especificado"))
        with col3:
            st.metric("Trabajadores", st.session_state.empresa.get("trabajadores", 0))
        
        if not st.session_state.empresa.get("nombre"):
            st.info("🎯 Ve a 'Diagnostico IA' para comenzar")
    
    # Diagnostico IA - FORMULARIO COMPLETO
    elif menu == "🔍 Diagnostico IA":
        st.markdown("""
        <div style="background: linear-gradient(135deg, #667eea, #764ba2); padding: 2rem; border-radius: 20px; margin-bottom: 2rem;">
            <h1 style="color: white; text-align: center;">🔍 Diagnostico con IA</h1>
            <p style="color: white; text-align: center;">Ingresa los datos de tu empresa</p>
        </div>
        """, unsafe_allow_html=True)
        
        with st.form("empresa_form"):
            st.markdown("### 📋 Datos de la empresa")
            
            col1, col2 = st.columns(2)
            with col1:
                nombre = st.text_input("🏢 Nombre de la empresa *", value=st.session_state.empresa.get("nombre", ""))
                nit = st.text_input("📄 NIT", value=st.session_state.empresa.get("nit", ""))
                ciudad = st.text_input("📍 Ciudad", value=st.session_state.empresa.get("ciudad", ""))
            
            with col2:
                sector = st.selectbox("🏭 Sector economico *", ["Construccion", "Manufactura", "Servicios", "Mineria", "Salud", "Educacion", "Comercio"])
                trabajadores = st.number_input("👥 Numero de trabajadores *", min_value=1, value=st.session_state.empresa.get("trabajadores", 10))
                arl = st.selectbox("🛡️ ARL", ["Positiva", "Sura", "Colpatria", "Bolivar", "No aplica"])
            
            submitted = st.form_submit_button("🚀 Guardar y Generar Diagnostico", use_container_width=True, type="primary")
        
        if submitted and nombre.strip() and trabajadores >= 1:
            st.session_state.empresa = {
                "nombre": nombre,
                "nit": nit,
                "sector": sector,
                "trabajadores": trabajadores,
                "ciudad": ciudad,
                "arl": arl
            }
            with st.spinner("🧠 IA analizando..."):
                diagnostico = ia_engine.generar_diagnostico(st.session_state.empresa)
                st.session_state.diagnostico_actual = diagnostico
        
        if st.session_state.get("diagnostico_actual"):
            st.markdown("---")
            st.markdown("### 📋 DIAGNOSTICO GENERADO")
            st.markdown(st.session_state.diagnostico_actual)
            st.download_button("📥 Descargar", st.session_state.diagnostico_actual, "diagnostico.txt")
    
    # Asistente IA
    elif menu == "🤖 Asistente IA":
        st.markdown("# 🤖 Asistente IA - Experto SST")
        
        if not st.session_state.empresa.get("nombre"):
            st.warning("⚠️ Primero registra los datos de la empresa en Diagnostico IA")
        
        for msg in st.session_state.chat_messages:
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])
        
        if prompt := st.chat_input("Escribe tu consulta sobre SST..."):
            st.session_state.chat_messages.append({"role": "user", "content": prompt})
            with st.chat_message("user"):
                st.markdown(prompt)
            with st.spinner("IA pensando..."):
                contexto = {"empresa": st.session_state.empresa.get("nombre", ""), "sector": st.session_state.empresa.get("sector", "")}
                respuesta = ia_engine.responder_chat(prompt, contexto)
            with st.chat_message("assistant"):
                st.markdown(respuesta)
            st.session_state.chat_messages.append({"role": "assistant", "content": respuesta})
    
    elif menu == "⚠️ Peligros":
        st.markdown("# ⚠️ Matriz de Peligros")
        st.info("Modulo en desarrollo - Proximamente")
    
    elif menu == "📋 Plan Anual":
        st.markdown("# 📅 Plan Anual SST")
        st.info("Modulo en desarrollo - Proximamente")

st.markdown("---")
st.markdown("<p style='text-align: center; color: gray;'>SG-SST PHVA - Sistema con IA para PYMES</p>", unsafe_allow_html=True)
