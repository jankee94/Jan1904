import streamlit as st
import pandas as pd
from database import db

def show():
    st.markdown("## ⚠️ FASE 2: Identificar Peligros")
    
    with st.form("nuevo_peligro"):
        col1, col2 = st.columns(2)
        with col1:
            tipo = st.selectbox("Tipo", ["Físicos", "Químicos", "Biológicos", "Ergonómicos", "Psicosociales", "Seguridad"])
            descripcion = st.text_area("Descripción")
            ubicacion = st.text_input("Ubicación")
        with col2:
            probabilidad = st.slider("Probabilidad (1-4)", 1, 4, 2)
            severidad = st.slider("Severidad (1-3)", 1, 3, 2)
            nivel = db.calcular_nivel(probabilidad, severidad)
            st.info(f"Nivel de riesgo: {nivel}")
        
        if st.form_submit_button("Guardar"):
            db.crear_peligro(tipo, descripcion, ubicacion, probabilidad, severidad)
            st.success("¡Peligro guardado!")
            st.rerun()
    
    st.markdown("---")
    st.subheader("Peligros registrados")
    df = db.obtener_peligros()
    if not df.empty:
        st.dataframe(df[['id', 'tipo', 'descripcion', 'ubicacion', 'nivel_riesgo']])
