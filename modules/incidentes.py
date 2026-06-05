import streamlit as st
from datetime import datetime
from core.db import db
from utils.exporters import boton_exportar

def render():
    st.title("📝 REGISTRO DE INCIDENTES - FASE 6")
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        with st.form("form_incidente"):
            st.subheader("➕ Nuevo Incidente")
            desc = st.text_area("Descripción del incidente")
            fecha = st.date_input("Fecha del incidente", datetime.now())
            gravedad = st.selectbox("Gravedad", ["Leve", "Moderada", "Grave", "Mortal"])
            tipo = st.selectbox("Tipo", ["Accidente", "Incidente", "Enfermedad Laboral", "Casi accidente"])
            
            if st.form_submit_button("📝 Registrar Incidente", use_container_width=True):
                if desc:
                    db.guardar_incidente(desc, fecha.strftime("%Y-%m-%d"), gravedad)
                    st.success("✅ Incidente registrado")
                    st.rerun()
    
    with col2:
        st.subheader("📊 Estadísticas Rápidas")
        df = db.obtener_incidentes()
        if not df.empty:
            st.metric("Total Incidentes", len(df))
            st.metric("Graves", len(df[df['gravedad'] == 'Grave']) if 'gravedad' in df.columns else 0)
            st.metric("Este Mes", len([i for i in df['fecha'] if i.startswith(datetime.now().strftime("%Y-%m"))]) if 'fecha' in df.columns else 0)
    
    st.markdown("---")
    st.subheader("📋 Historial de Incidentes")
    df = db.obtener_incidentes()
    if not df.empty:
        st.dataframe(df, use_container_width=True)
        boton_exportar(df, "Incidentes")
