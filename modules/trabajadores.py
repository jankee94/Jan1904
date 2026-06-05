import streamlit as st
from core.db import db
from utils.exporters import boton_exportar

def render():
    st.title("👥 GESTIÓN DE TRABAJADORES - FASE 5")
    
    tab1, tab2 = st.tabs(["📋 Lista", "➕ Nuevo Trabajador"])
    
    with tab1:
        df = db.obtener_trabajadores()
        if not df.empty:
            st.dataframe(df, use_container_width=True)
            boton_exportar(df, "Trabajadores")
        else:
            st.info("📭 No hay trabajadores registrados")
    
    with tab2:
        with st.form("form_trabajador"):
            col1, col2 = st.columns(2)
            with col1:
                nombre = st.text_input("Nombre completo")
                cedula = st.text_input("Cédula")
            with col2:
                cargo = st.text_input("Cargo")
                area = st.text_input("Área/Dependencia")
            
            if st.form_submit_button("💾 Registrar Trabajador", use_container_width=True):
                if nombre:
                    db.guardar_trabajador(nombre, cedula, cargo)
                    st.success("✅ Trabajador registrado")
                    st.rerun()
