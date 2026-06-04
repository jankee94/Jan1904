import streamlit as st
from core.db import db

def render():
    st.title("📊 Dashboard")
    
    empresa = db.obtener_empresa()
    if empresa:
        st.metric("Empresa", empresa.get("nombre", "-"))
        st.metric("Trabajadores", empresa.get("trabajadores", 0))
    
    st.metric("Peligros", len(db.obtener_peligros()))
    st.metric("Acciones", len(db.obtener_acciones()))
