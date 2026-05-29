import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime, timedelta

def show():
    st.markdown("## 📚 Plan de Capacitaciones SST")
    st.markdown("---")
    
    conn = sqlite3.connect('sst.db', check_same_thread=False)
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS capacitaciones (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            tema TEXT NOT NULL,
            fecha DATE,
            duracion INTEGER,
            asistentes INTEGER,
            estado TEXT DEFAULT 'Programada'
        )
    ''')
    conn.commit()
    
    with st.form("nueva_capacitacion"):
        tema = st.text_input("Tema de la capacitación")
        fecha = st.date_input("Fecha", datetime.now())
        duracion = st.number_input("Duración (horas)", min_value=1, step=1)
        submitted = st.form_submit_button("Programar")
        if submitted and tema:
            cursor.execute("INSERT INTO capacitaciones (tema, fecha, duracion) VALUES (?,?,?)", (tema, fecha, duracion))
            conn.commit()
            st.success("✅ Capacitación programada")
            st.rerun()
    
    st.markdown("---")
    df = pd.read_sql_query("SELECT * FROM capacitaciones ORDER BY fecha DESC", conn)
    if not df.empty:
        st.dataframe(df, use_container_width=True)
    else:
        st.info("No hay capacitaciones programadas")
    
    conn.close()
