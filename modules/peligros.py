import streamlit as st
import sqlite3
import pandas as pd

def render():
    st.title("⚠️ PELIGROS - FASE 2 GTC-45")
    
    conn = sqlite3.connect("sst.db", check_same_thread=False)
    cursor = conn.cursor()
    empresa_id = st.session_state.get("empresa_actual_id", 1)
    
    if not empresa_id:
        st.warning("⚠️ Primero debe crear un diagnóstico de empresa")
        return
    
    tab1, tab2 = st.tabs(["📋 Lista de Peligros", "➕ Agregar Peligro"])
    
    with tab1:
        df = pd.read_sql_query("SELECT * FROM peligros WHERE empresa_id = ?", conn, params=(empresa_id,))
        if not df.empty:
            st.dataframe(df, use_container_width=True)
        else:
            st.info("No hay peligros registrados")
    
    with tab2:
        with st.form("form_peligro"):
            tipo = st.selectbox("Tipo de Peligro", ["Físico", "Químico", "Biológico", "Ergonómico", "Psicosocial", "Seguridad"])
            descripcion = st.text_area("Descripción")
            
            if st.form_submit_button("💾 Guardar Peligro", use_container_width=True):
                if descripcion:
                    cursor.execute('''INSERT INTO peligros (empresa_id, tipo, descripcion) VALUES (?, ?, ?)''',
                                  (empresa_id, tipo, descripcion))
                    conn.commit()
                    st.success("✅ Peligro guardado")
                    st.rerun()
                else:
                    st.error("Ingrese una descripción")
    
    conn.close()
