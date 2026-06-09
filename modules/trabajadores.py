import streamlit as st
import sqlite3
import pandas as pd

def render():
    st.title("👥 TRABAJADORES")
    
    conn = sqlite3.connect("sst.db", check_same_thread=False)
    cursor = conn.cursor()
    empresa_id = st.session_state.get("empresa_actual_id", 1)
    
    if not empresa_id:
        st.warning("⚠️ Primero debe crear un diagnóstico de empresa")
        return
    
    tab1, tab2 = st.tabs(["📋 Lista de Trabajadores", "➕ Nuevo Trabajador"])
    
    with tab1:
        df = pd.read_sql_query("SELECT * FROM trabajadores WHERE empresa_id = ?", conn, params=(empresa_id,))
        if not df.empty:
            st.dataframe(df, use_container_width=True)
        else:
            st.info("No hay trabajadores registrados")
    
    with tab2:
        with st.form("form_trabajador"):
            nombre = st.text_input("Nombre completo")
            cedula = st.text_input("Cédula")
            cargo = st.text_input("Cargo")
            
            if st.form_submit_button("💾 Registrar Trabajador", use_container_width=True):
                if nombre:
                    cursor.execute('''INSERT INTO trabajadores (empresa_id, nombre, cedula, cargo) 
                                      VALUES (?, ?, ?, ?)''',
                                  (empresa_id, nombre, cedula, cargo))
                    conn.commit()
                    st.success("✅ Trabajador registrado")
                    st.rerun()
                else:
                    st.error("Ingrese el nombre del trabajador")
    
    conn.close()
