import streamlit as st
import sqlite3
import pandas as pd
from datetime import date

def calcular_nivel_riesgo(probabilidad, severidad):
    matriz = {
        ("Baja", "Leve"): "Bajo",
        ("Baja", "Moderada"): "Medio",
        ("Baja", "Grave"): "Alto",
        ("Media", "Leve"): "Medio",
        ("Media", "Moderada"): "Alto",
        ("Media", "Grave"): "Crítico",
        ("Alta", "Leve"): "Alto",
        ("Alta", "Moderada"): "Crítico",
        ("Alta", "Grave"): "Crítico",
    }
    return matriz.get((probabilidad, severidad), "No determinado")

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
            control TEXT,
            fecha_registro DATE
        )
    ''')
    conn.commit()
    
    tab1, tab2 = st.tabs(["➕ Registrar Peligro", "📋 Matriz de Riesgos"])
    
    with tab1:
        with st.form("registro_peligro"):
            col1, col2 = st.columns(2)
            with col1:
                proceso = st.text_input("Proceso/Actividad")
                peligro = st.text_input("Peligro identificado*")
                efecto = st.text_area("Posibles efectos")
            with col2:
                probabilidad = st.selectbox("Probabilidad", ["Baja", "Media", "Alta"])
                severidad = st.selectbox("Severidad", ["Leve", "Moderada", "Grave"])
                control = st.text_area("Medidas de control")
            
            nivel = calcular_nivel_riesgo(probabilidad, severidad)
            st.info(f"**Nivel de riesgo calculado:** {nivel}")
            
            submitted = st.form_submit_button("Registrar peligro", use_container_width=True)
            if submitted and peligro:
                cursor.execute('''
                    INSERT INTO peligros (proceso, peligro, efecto, probabilidad, severidad, nivel_riesgo, control, fecha_registro)
                    VALUES (?,?,?,?,?,?,?,?)
                ''', (proceso, peligro, efecto, probabilidad, severidad, nivel, control, date.today()))
                conn.commit()
                st.success("✅ Peligro registrado")
                st.rerun()
    
    with tab2:
        df = pd.read_sql_query("SELECT * FROM peligros ORDER BY fecha_registro DESC", conn)
        if not df.empty:
            st.dataframe(df, use_container_width=True)
            
            # Resumen por nivel de riesgo
            st.subheader("📊 Resumen por Nivel de Riesgo")
            resumen = df['nivel_riesgo'].value_counts()
            st.bar_chart(resumen)
        else:
            st.info("No hay peligros registrados")
    
    conn.close()
