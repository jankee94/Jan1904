import streamlit as st
from core.ia_engine import ia_engine

def show():
    st.markdown("# 🔍 Diagnostico con IA")
    
    with st.form("empresa_form"):
        nit = st.text_input("NIT")
        trabajadores = st.number_input("Trabajadores", min_value=1, value=10)
        arl = st.selectbox("ARL", ["Positiva", "Sura", "Colpatria", "Bolivar"])
        
        if st.form_submit_button("Generar Diagnostico"):
            with st.spinner("IA generando..."):
                empresa_data = {"nit": nit, "trabajadores": trabajadores, "arl": arl}
                resultado = ia_engine.generar_diagnostico(empresa_data)
                st.markdown(resultado)
