import streamlit as st
from datetime import datetime
from core.db import db
from utils.exporters import boton_exportar

def render():
    st.title("✅ PLAN DE ACCIÓN - FASE 4")
    
    tab1, tab2 = st.tabs(["📋 Seguimiento", "➕ Nueva Acción"])
    
    with tab1:
        df = db.obtener_acciones()
        if not df.empty:
            for _, row in df.iterrows():
                col1, col2 = st.columns([3, 1])
                with col1:
                    st.markdown(f"**📌 {row['descripcion']}**")
                    st.caption(f"👤 {row['responsable']} | 📅 {row['fecha']}")
                    if row['estado'] == "Completada":
                        st.success("✅ Completada")
                    else:
                        st.warning("⏳ Pendiente")
                with col2:
                    nuevo = st.selectbox("Estado", ["Pendiente", "En progreso", "Completada"], 
                                        index=["Pendiente", "En progreso", "Completada"].index(row['estado']),
                                        key=f"act_{row['id']}")
                    if nuevo != row['estado']:
                        db.actualizar_estado(row['id'], nuevo)
                        st.rerun()
                st.markdown("---")
            
            boton_exportar(df, "Plan_Accion")
        else:
            st.info("📭 No hay acciones registradas")
    
    with tab2:
        with st.form("form_accion"):
            desc = st.text_area("Descripción de la acción")
            responsable = st.text_input("Responsable")
            fecha = st.date_input("Fecha límite", datetime.now())
            prioridad = st.selectbox("Prioridad", ["Alta", "Media", "Baja"])
            
            if st.form_submit_button("💾 Guardar Acción", use_container_width=True):
                if desc and responsable:
                    db.guardar_accion(desc, responsable, fecha.strftime("%Y-%m-%d"))
                    st.success("✅ Acción guardada")
                    st.rerun()
