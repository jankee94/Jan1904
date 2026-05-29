import streamlit as st
import time

def mostrar_bienvenida():
    st.markdown("""
    <style>
    .welcome-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 20px;
        color: white;
        text-align: center;
        margin-bottom: 2rem;
    }
    .step-card {
        background: rgba(255,255,255,0.15) !important;
        backdrop-filter: blur(10px);
        padding: 1.5rem;
        border-radius: 15px;
        margin-bottom: 1rem;
        box-shadow: 0 4px 12px rgba(0,0,0,0.2);
        border: 1px solid rgba(255,255,255,0.2);
        color: white !important;
    }
    .step-card h3, .step-card p {
        color: white !important;
    }
    </style>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    <div class="welcome-header">
        <h1>🎓 Bienvenido al Sistema SG-SST PHVA</h1>
        <p>Tutorial interactivo - Aprende a usar el Asistente IA</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("### 📌 ¿Qué vas a aprender?")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown('<div class="step-card"><h3>1️⃣</h3><p>Qué puede hacer la IA</p></div>', unsafe_allow_html=True)
    with col2:
        st.markdown('<div class="step-card"><h3>2️⃣</h3><p>Cómo pedir cambios</p></div>', unsafe_allow_html=True)
    with col3:
        st.markdown('<div class="step-card"><h3>3️⃣</h3><p>Ver la IA en acción</p></div>', unsafe_allow_html=True)
    
    st.markdown("---")
    
    with st.expander("🎯 Paso 1: ¿Qué puede hacer el Asistente IA?", expanded=True):
        st.markdown("""
        El Asistente IA puede modificar la aplicación en tiempo real.
        
        - Cambia colores y diseños
        - Agrega exportar a Excel
        - Revisa y corrige código
        - Crea gráficos automaticamente
        """)
        
        if st.button("Ver IA en accion"):
            with st.spinner("La IA está trabajando..."):
                time.sleep(1)
            st.success("Listo! La IA puede hacer esto y mas")
            st.balloons()
    
    with st.expander("💬 Paso 2: Cómo hablar con la IA", expanded=False):
        st.markdown("""
        Comandos que funcionan:
        
        - "Cambia el color del header a azul"
        - "Agrega exportar a Excel en trabajadores"
        - "Revisa si hay errores en politicas_sst"
        """)
    
    with st.expander("🚀 Paso 3: Demostración en vivo", expanded=False):
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Cambiar tema oscuro"):
                with st.chat_message("assistant"):
                    st.markdown("IA: Aplicando tema oscuro...")
                    st.success("Tema oscuro activado")
        with col2:
            if st.button("Crear grafico ejemplo"):
                with st.chat_message("assistant"):
                    st.markdown("IA: Generando grafico...")
                    st.success("Grafico creado")
    
    st.markdown("---")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Entendido, ir al Asistente IA"):
            st.session_state.tutorial_completado = True
            st.rerun()
    with col2:
        if st.button("Ver tutorial despues"):
            st.session_state.tutorial_completado = True
            st.rerun()
