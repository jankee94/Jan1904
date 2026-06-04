import streamlit as st
from core.db import db

def render():
    st.title("👥 Trabajadores")
    
    tab1, tab2 = st.tabs(["Lista", "Nuevo"])
    
    with tab1:
        df = db.obtener_trabajadores()
        if not df.empty:
            st.dataframe(df)
    
    with tab2:
        with st.form("form"):
            cedula = st.text_input("Cedula")
            nombre = st.text_input("Nombre")
            cargo = st.text_input("Cargo")
            if st.form_submit_button("Guardar"):
                db.guardar_trabajador(cedula, nombre, "", cargo, "")
                st.success("Guardado")
                st.rerun()
