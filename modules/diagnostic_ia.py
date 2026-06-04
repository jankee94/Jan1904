import streamlit as st
from core.ia_engine import ia_engine

def show():
    st.markdown("# 🔍 Diagnostico con IA")
    
    if not st.session_state.empresa.get("nombre"):
        st.warning("Primero completa los datos de la empresa")
        return
    
    col1, col2 = st.columns(2)
    with col1:
        nombre = st.text_input("Nombre empresa", value=st.session_state.empresa.get("nombre", ""))
        sector = st.selectbox("Sector", ["Construccion", "Manufactura", "Servicios", "Mineria", "Salud"])
        trabajadores = st.number_input("Trabajadores", min_value=1, value=st.session_state.empresa.get("trabajadores", 10))
    
    if st.button("Guardar y Generar Diagnostico"):
        st.session_state.empresa = {
            "nombre": nombre,
            "sector": sector,
            "trabajadores": trabajadores
        }
        with st.spinner("IA analizando..."):
            diagnostico = ia_engine.generar_diagnostico(st.session_state.empresa)
            st.session_state.diagnostico_actual = diagnostico
    
    if st.session_state.get("diagnostico_actual"):
        st.markdown("---")
        st.markdown("### Diagnostico Generado")
        st.markdown(st.session_state.diagnostico_actual)
        st.download_button("Descargar Diagnostico", st.session_state.diagnostico_actual, "diagnostico.txt")
