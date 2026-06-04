import streamlit as st
from core.db import db

def render():
    st.title("📊 Riesgos")
    df = db.obtener_peligros()
    if not df.empty:
        st.bar_chart(df['nivel_riesgo'].value_counts())
