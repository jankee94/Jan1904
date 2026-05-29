import streamlit as st
import sqlite3
import pandas as pd

def show():
    st.markdown("## ⚠️ Matriz de Peligros (GTC-45)")
    st.markdown("---")
    
    conn = sqlite3.connect('sst.db', check_same_thread=False)
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS peligros (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            proceso TEXT,
            peligro TEXT,
            efecto TEXT,
            probabilidad TEXT,
            severidad TEXT,
            nivel_riesgo TEXT,
            control TEXT
        )
    ''')
    conn.commit()
    
    with st.form("agregar_peligro"):
        col1, col2 = st.columns(2)
        with col1:
            proceso = st.text_input("Proceso/Actividad")
            peligro = st.text_input("Peligro identificado")
            efecto = st.text_area("Posibles efectos")
        with col2:
            probabilidad = st.selectbox("Probabilidad", ["Baja", "Media", "Alta"])
            severidad = st.selectbox("Severidad", ["Leve", "Moderada", "Grave"])
            control = st.text_area("Medidas de control")
        
        if probabilidad == "Baja" and severidad == "Leve":
            nivel = "Bajo"
        elif probabilidad == "Alta" and severidad == "Grave":
            nivel = "Crítico"
        elif probabilidad in ["Media", "Alta"] and severidad in ["Moderada", "Grave"]:
            nivel = "Alto"
        else:
            nivel = "Medio"
        
        st.info(f"**Nivel de riesgo calculado:** {nivel}")
        
        submitted = st.form_submit_button("Registrar peligro")
        if submitted:
            cursor.execute('''
                INSERT INTO peligros (proceso, peligro, efecto, probabilidad, severidad, nivel_riesgo, control)
                VALUES (?,?,?,?,?,?,?)
            ''', (proceso, peligro, efecto, probabilidad, severidad, nivel, control))
            conn.commit()
            st.success("✅ Peligro registrado")
            st.rerun()
    
    st.markdown("---")
    st.subheader("📋 Peligros registrados")
    df = pd.read_sql_query("SELECT * FROM peligros", conn)
    if not df.empty:
        st.dataframe(df, use_container_width=True)
    else:
        st.info("No hay peligros registrados")
    
    conn.close()
