import streamlit as st

def render(db, auth_manager):
    st.title("👥 Trabajadores")
    
    with st.form("form"):
        nombre = st.text_input("Nombre")
        cedula = st.text_input("Cédula")
        if st.form_submit_button("Guardar"):
            if nombre:
                db.execute_query("INSERT INTO trabajadores (nombre, cedula) VALUES (?, ?)", (nombre, cedula))
                st.success("Guardado")
                st.rerun()
    
    df = db.fetch_all("SELECT * FROM trabajadores")
    if not df.empty:
        st.dataframe(df)
