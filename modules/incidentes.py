import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime

def show():
    st.markdown("## 📝 Registro de Incidentes, Accidentes y Enfermedades Laborales")
    st.markdown("---")
    
    conn = sqlite3.connect('sst.db', check_same_thread=False)
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS incidentes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            tipo TEXT,
            fecha DATE,
            lugar TEXT,
            descripcion TEXT,
            afectado TEXT,
            gravedad TEXT,
            acciones TEXT
        )
    ''')
    conn.commit()
    
    with st.form("reportar_incidente"):
        tipo = st.selectbox("Tipo", ["Incidente", "Accidente", "Enfermedad Laboral"])
        fecha = st.date_input("Fecha", datetime.now())
        lugar = st.text_input("Lugar")
        descripcion = st.text_area("Descripción del evento")
        afectado = st.text_input("Persona(s) afectada(s)")
        gravedad = st.selectbox("Gravedad", ["Leve", "Moderada", "Grave", "Mortal"])
        acciones = st.text_area("Acciones tomadas")
        
        submitted = st.form_submit_button("Registrar")
        if submitted:
            cursor.execute('''
                INSERT INTO incidentes (tipo, fecha, lugar, descripcion, afectado, gravedad, acciones)
                VALUES (?,?,?,?,?,?,?)
            ''', (tipo, fecha, lugar, descripcion, afectado, gravedad, acciones))
            conn.commit()
            st.success("✅ Incidente registrado")
            st.rerun()
    
    st.markdown("---")
    df = pd.read_sql_query("SELECT * FROM incidentes ORDER BY fecha DESC", conn)
    if not df.empty:
        st.dataframe(df, use_container_width=True)
    else:
        st.info("No hay registros")
    
    conn.close()
