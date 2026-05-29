import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime, timedelta

def show():
    st.markdown("## 📚 Gestión de Capacitaciones SST")
    st.markdown("---")
    
    conn = sqlite3.connect('sst.db', check_same_thread=False)
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS capacitaciones (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            tema TEXT NOT NULL,
            fecha DATE,
            duracion INTEGER,
            asistentes INTEGER DEFAULT 0,
            instructor TEXT,
            estado TEXT DEFAULT 'Programada'
        )
    ''')
    conn.commit()
    
    tab1, tab2 = st.tabs(["📅 Programar", "📋 Historial"])
    
    with tab1:
        with st.form("programar_capacitacion"):
            tema = st.text_input("Tema de la capacitación*")
            fecha = st.date_input("Fecha", datetime.now())
            duracion = st.number_input("Duración (horas)", min_value=1, step=1, value=4)
            instructor = st.text_input("Instructor/Proveedor")
            
            submitted = st.form_submit_button("Programar", use_container_width=True)
            if submitted and tema:
                cursor.execute('''
                    INSERT INTO capacitaciones (tema, fecha, duracion, instructor, estado)
                    VALUES (?,?,?,?,?)
                ''', (tema, fecha, duracion, instructor, "Programada"))
                conn.commit()
                st.success("✅ Capacitación programada")
                st.rerun()
    
    with tab2:
        df = pd.read_sql_query("SELECT * FROM capacitaciones ORDER BY fecha DESC", conn)
        if not df.empty:
            st.dataframe(df, use_container_width=True)
            
            # Capacitaciones próximas
            st.subheader("📅 Próximas capacitaciones")
            proximas = df[df['fecha'] >= datetime.now().date()]
            if not proximas.empty:
                for _, row in proximas.iterrows():
                    st.info(f"**{row['tema']}** - {row['fecha']} ({row['duracion']} horas)")
            else:
                st.success("No hay capacitaciones pendientes")
        else:
            st.info("No hay capacitaciones registradas")
    
    conn.close()
