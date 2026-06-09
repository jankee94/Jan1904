import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime

def render():
    st.title("📝 INCIDENTES")
    
    conn = sqlite3.connect("sst.db", check_same_thread=False)
    cursor = conn.cursor()
    empresa_id = st.session_state.get("empresa_actual_id", 1)
    
    if not empresa_id:
        st.warning("⚠️ Primero debe crear un diagnóstico de empresa")
        return
    
    tab1, tab2 = st.tabs(["📋 Historial", "➕ Reportar Incidente"])
    
    with tab1:
        df = pd.read_sql_query("SELECT * FROM incidentes WHERE empresa_id = ? ORDER BY fecha DESC", conn, params=(empresa_id,))
        if not df.empty:
            st.dataframe(df, use_container_width=True)
        else:
            st.info("No hay incidentes registrados")
    
    with tab2:
        with st.form("form_incidente"):
            descripcion = st.text_area("Descripción del incidente")
            fecha = st.date_input("Fecha", datetime.now())
            gravedad = st.selectbox("Gravedad", ["Leve", "Moderada", "Grave", "Mortal"])
            
            if st.form_submit_button("📝 Reportar Incidente", use_container_width=True):
                if descripcion:
                    cursor.execute('''INSERT INTO incidentes (empresa_id, descripcion, fecha, gravedad) 
                                      VALUES (?, ?, ?, ?)''',
                                  (empresa_id, descripcion, fecha.strftime("%Y-%m-%d"), gravedad))
                    conn.commit()
                    st.success("✅ Incidente reportado")
                    st.rerun()
                else:
                    st.error("Ingrese una descripción del incidente")
    
    conn.close()
