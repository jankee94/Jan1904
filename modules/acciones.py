import streamlit as st
from datetime import datetime
from core.db import db

def render():
    st.title("✅ Plan de Acción")
    
    tab1, tab2 = st.tabs(["Seguimiento", "Nueva"])
    
    with tab1:
        df = db.obtener_acciones()
        if not df.empty:
            for _, row in df.iterrows():
                st.markdown(f"**{row['descripcion']}** - {row['estado']}")
    
    with tab2:
        with st.form("form"):
            desc = st.text_area("Descripcion")
            resp = st.text_input("Responsable")
            if st.form_submit_button("Guardar"):
                db.guardar_accion(0, desc, resp, datetime.now().strftime("%Y-%m-%d"), "Media", 0)
                st.success("Guardado")
                st.rerun()
