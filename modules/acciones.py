import streamlit as st
import pandas as pd
from database import db
from datetime import datetime

def show():
    st.markdown("## ✅ FASE 4: Plan de Acción")
    st.markdown("---")
    
    # Obtener peligros para asociar acciones
    peligros_df = db.obtener_peligros()
    
    if not peligros_df.empty:
        with st.form("form_accion"):
            col1, col2 = st.columns(2)
            with col1:
                peligro_id = st.selectbox("Peligro asociado*", 
                    options=peligros_df['id'].tolist(),
                    format_func=lambda x: f"{x} - {peligros_df[peligros_df['id']==x]['descripcion'].iloc[0][:50]}")
                descripcion = st.text_area("Descripción de la acción*", height=80)
            with col2:
                responsable = st.text_input("Responsable*")
                fecha_limite = st.date_input("Fecha límite*", min_value=datetime.now())
                prioridad = st.selectbox("Prioridad", ["Alta", "Media", "Baja"])
            
            if st.form_submit_button("💾 Crear Acción", use_container_width=True):
                if descripcion and responsable:
                    conn = db.get_connection()
                    cursor = conn.cursor()
                    cursor.execute('''
                        INSERT INTO acciones (peligro_id, descripcion, responsable, fecha_limite, prioridad)
                        VALUES (?, ?, ?, ?, ?)
                    ''', (peligro_id, descripcion, responsable, fecha_limite, prioridad))
                    conn.commit()
                    conn.close()
                    st.success("✅ Acción creada exitosamente!")
                    st.rerun()
                else:
                    st.error("❌ Descripción y responsable son obligatorios")
        
        st.markdown("---")
        st.subheader("Seguimiento de Acciones")
        
        conn = db.get_connection()
        acciones_df = pd.read_sql_query('''
            SELECT a.*, p.descripcion as peligro_desc, p.nivel_riesgo
            FROM acciones a
            JOIN peligros p ON a.peligro_id = p.id
            ORDER BY 
                CASE a.estado
                    WHEN 'Pendiente' THEN 1
                    WHEN 'En progreso' THEN 2
                    WHEN 'Completada' THEN 3
                END,
                a.fecha_limite ASC
        ''', conn)
        conn.close()
        
        if not acciones_df.empty:
            for idx, row in acciones_df.iterrows():
                with st.container():
                    col1, col2, col3 = st.columns([3, 1, 1])
                    with col1:
                        st.markdown(f"**📌 {row['descripcion']}**")
                        st.caption(f"Peligro: {row['peligro_desc'][:60]}... | Responsable: {row['responsable']}")
                        st.caption(f"📅 Límite: {row['fecha_limite']} | Prioridad: {row['prioridad']}")
                    with col2:
                        nuevo_estado = st.selectbox(
                            "Estado",
                            ["Pendiente", "En progreso", "Completada"],
                            index=["Pendiente", "En progreso", "Completada"].index(row['estado']),
                            key=f"estado_{row['id']}"
                        )
                        if nuevo_estado != row['estado']:
                            conn = db.get_connection()
                            cursor = conn.cursor()
                            cursor.execute("UPDATE acciones SET estado = ? WHERE id = ?", (nuevo_estado, row['id']))
                            conn.commit()
                            conn.close()
                            st.rerun()
                    with col3:
                        st.write(f"**ID:** {row['id']}")
                    st.markdown("---")
        else:
            st.info("📭 No hay acciones registradas")
    else:
        st.warning("⚠️ Primero debes registrar peligros en la Fase 2")
