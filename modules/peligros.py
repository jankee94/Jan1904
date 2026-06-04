import streamlit as st

def render(db, ia, auth_manager):
    st.title("⚠️ Peligros")
    
    with st.form("form"):
        tipo = st.selectbox("Tipo", ["Físico", "Químico", "Biológico", "Ergonómico", "Psicosocial"])
        descripcion = st.text_area("Descripción")
        ubicacion = st.text_input("Ubicación")
        prob = st.slider("Probabilidad", 1, 4, 2)
        sev = st.slider("Severidad", 1, 3, 2)
        
        matriz = {(1,1):"III",(1,2):"II",(1,3):"I",(2,1):"III",(2,2):"II",(2,3):"I",
                  (3,1):"II",(3,2):"I",(3,3):"I",(4,1):"II",(4,2):"I",(4,3):"I"}
        nivel = matriz.get((prob, sev), "III")
        st.info(f"Nivel: {nivel}")
        
        if st.form_submit_button("Guardar"):
            db.execute_query('''
                INSERT INTO peligros (tipo, descripcion, ubicacion, probabilidad, severidad, nivel_riesgo)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (tipo, descripcion, ubicacion, prob, sev, nivel))
            st.success("Guardado")
            st.rerun()
    
    df = db.fetch_all("SELECT * FROM peligros")
    if not df.empty:
        st.dataframe(df)
