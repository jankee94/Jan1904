import streamlit as st
from datetime import datetime

def render(db, ia, auth_manager):
    st.title("📝 Incidentes")
    
    with st.form("form"):
        descripcion = st.text_area("Descripción")
        fecha = st.date_input("Fecha", datetime.now())
        if st.form_submit_button("Registrar"):
            db.execute_query("INSERT INTO incidentes (descripcion, fecha) VALUES (?, ?)", (descripcion, fecha))
            st.success("Registrado")
            st.rerun()
    
    df = db.fetch_all("SELECT * FROM incidentes")
    if not df.empty:
        st.dataframe(df)
