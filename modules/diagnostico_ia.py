import streamlit as st
from datetime import datetime, timedelta
from core.db import db
from core.ia_engine import ia

def render():
    st.title("🤖 Diagnóstico IA")
    
    empresa = db.obtener_empresa()
    
    with st.form("diagnostico_form"):
        nombre = st.text_input("Nombre empresa", value=empresa.get("nombre", "") if empresa else "")
        trabajadores = st.number_input("Trabajadores", min_value=1, value=empresa.get("trabajadores", 10) if empresa else 10)
        arl = st.selectbox("ARL", ["Positiva", "Sura", "Colpatria"])
        
        if st.form_submit_button("Generar"):
            if nombre:
                with st.spinner("IA generando..."):
                    respuesta = ia.call_best(f"Diagnóstico SST para {nombre} con {trabajadores} trabajadores")
                    if respuesta:
                        db.guardar_empresa("", nombre, trabajadores, arl, "", respuesta)
                        st.success("Diagnóstico guardado")
                        st.rerun()
