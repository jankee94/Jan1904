import streamlit as st
from core.db import db

def render():
    st.title("⚠️ Peligros")
    
    tab1, tab2 = st.tabs(["Lista", "Nuevo"])
    
    with tab1:
        df = db.obtener_peligros()
        if not df.empty:
            st.dataframe(df)
    
    with tab2:
        with st.form("form"):
            tipo = st.selectbox("Tipo", ["Fisico", "Quimico", "Biologico", "Ergonomico", "Psicosocial"])
            desc = st.text_area("Descripcion")
            prob = st.slider("Probabilidad", 1, 4, 2)
            sev = st.slider("Severidad", 1, 3, 2)
            if st.form_submit_button("Guardar"):
                db.guardar_peligro(tipo, desc, "", prob, sev, 0)
                st.success("Guardado")
                st.rerun()
