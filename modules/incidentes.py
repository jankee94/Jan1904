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
            cargo_afectado TEXT,
            gravedad TEXT,
            dias_perdida INTEGER DEFAULT 0,
            acciones TEXT,
            estado TEXT DEFAULT 'Abierto'
        )
    ''')
    conn.commit()
    
    tab1, tab2 = st.tabs(["➕ Reportar", "📋 Historial"])
    
    with tab1:
        with st.form("reportar_incidente"):
            col1, col2 = st.columns(2)
            with col1:
                tipo = st.selectbox("Tipo de evento", ["Incidente", "Accidente", "Enfermedad Laboral", "Casi accidente"])
                fecha = st.date_input("Fecha del evento", datetime.now())
                lugar = st.text_input("Lugar")
            with col2:
                gravedad = st.selectbox("Gravedad", ["Leve", "Moderada", "Grave", "Mortal"])
                afectado = st.text_input("Nombre del afectado")
                cargo_afectado = st.text_input("Cargo")
            
            descripcion = st.text_area("Descripción detallada del evento")
            acciones = st.text_area("Acciones tomadas")
            dias_perdida = st.number_input("Días de incapacidad", min_value=0, step=1)
            
            submitted = st.form_submit_button("Registrar evento", use_container_width=True)
            if submitted and descripcion:
                cursor.execute('''
                    INSERT INTO incidentes (tipo, fecha, lugar, descripcion, afectado, cargo_afectado, gravedad, dias_perdida, acciones, estado)
                    VALUES (?,?,?,?,?,?,?,?,?,?)
                ''', (tipo, fecha, lugar, descripcion, afectado, cargo_afectado, gravedad, dias_perdida, acciones, "Abierto"))
                conn.commit()
                st.success("✅ Evento registrado")
                st.rerun()
    
    with tab2:
        df = pd.read_sql_query("SELECT * FROM incidentes ORDER BY fecha DESC", conn)
        if not df.empty:
            st.dataframe(df, use_container_width=True)
            
            # Estadísticas rápidas
            st.subheader("📊 Estadísticas")
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Total eventos", len(df))
            with col2:
                accidentes = len(df[df['tipo'] == 'Accidente'])
                st.metric("Accidentes", accidentes)
            with col3:
                dias = df['dias_perdida'].sum()
                st.metric("Días perdidos", dias)
        else:
            st.info("No hay eventos registrados")
    
    conn.close()
