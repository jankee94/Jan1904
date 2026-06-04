import streamlit as st
import pandas as pd
from database import db

def show():
    st.markdown("## 📊 FASE 3: Evaluar Riesgos")
    df = db.obtener_peligros()
    if not df.empty:
        st.dataframe(df[['id', 'tipo', 'descripcion', 'nivel_riesgo']])
        st.info("Matriz de riesgos visual aquí")
    else:
        st.warning("No hay peligros registrados")
