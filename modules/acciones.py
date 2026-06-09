import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime

def render():
    st.title("✅ PLAN DE ACCIÓN")
    
    conn = sqlite3.connect("sst.db", check_same_thread=False)
    cursor = conn.cursor()
    empresa_id = st.session_state.get("empresa_actual_id", 1)
    
    if not empresa_id:
        st.warning("⚠️ Primero debe crear un diagnóstico de empresa")
        return
    
    tab1, tab2 = st.tabs(["📋 Lista de Acciones", "➕ Nueva Acción"])
    
    with tab1:
        df = pd.read_sql_query("SELECT * FROM acciones WHERE empresa_id = ?", conn, params=(empresa_id,))
        if not df.empty:
            for _, row in df.iterrows():
                col1, col2 = st.columns([3, 1])
                with col1:
                    st.markdown(f"**{row['descripcion']}**")
                    st.caption(f"Responsable: {row['responsable']} | Estado: {row['estado']}")
                with col2:
                    nuevo_estado = st.selectbox("Estado", ["Pendiente", "En progreso", "Completada"], 
                                               index=["Pendiente", "En progreso", "Completada"].index(row['estado']),
                                               key=f"estado_{row['id']}")
                    if nuevo_estado != row['estado']:
                        cursor.execute("UPDATE acciones SET estado = ? WHERE id = ?", (nuevo_estado, row['id']))
                        conn.commit()
                        st.rerun()
                st.markdown("---")
        else:
            st.info("No hay acciones registradas")
    
    with tab2:
        with st.form("form_accion"):
            descripcion = st.text_area("Descripción de la acción")
            responsable = st.text_input("Responsable")
            fecha_limite = st.date_input("Fecha límite", datetime.now())
            prioridad = st.selectbox("Prioridad", ["Alta", "Media", "Baja"])
            
            if st.form_submit_button("💾 Guardar Acción", use_container_width=True):
                if descripcion and responsable:
                    cursor.execute('''INSERT INTO acciones (empresa_id, descripcion, responsable, fecha, estado) 
                                      VALUES (?, ?, ?, ?, ?)''',
                                  (empresa_id, descripcion, responsable, fecha_limite.strftime("%Y-%m-%d"), "Pendiente"))
                    conn.commit()
                    st.success("✅ Acción guardada")
                    st.rerun()
                else:
                    st.error("Complete todos los campos")
    
    conn.close()
