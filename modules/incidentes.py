import streamlit as st
from datetime import datetime
from core.db import db

def render():
    st.title("📝 Incidentes")
    
    with st.form("form"):
        desc = st.text_area("Descripcion")
        fecha = st.date_input("Fecha", datetime.now())
        if st.form_submit_button("Registrar"):
            db.guardar_incidente("Incidente", desc, fecha, "", "Leve")
            st.success("Registrado")
            st.rerun()
    
    df = db.obtener_incidentes()
    if not df.empty:
        st.dataframe(df)
