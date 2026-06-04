import streamlit as st
import pandas as pd
from database import db
from core.ia_engine import ia

def show():
    st.markdown("## ⚠️ FASE 2: Identificar Peligros (GTC-45)")
    st.markdown("---")
    
    tab1, tab2 = st.tabs(["➕ Nuevo Peligro", "📋 Lista y Gestión"])
    
    with tab1:
        with st.form("form_peligro"):
            col1, col2 = st.columns(2)
            with col1:
                tipo = st.selectbox("Tipo de peligro*", 
                    ["Físicos", "Químicos", "Biológicos", "Ergonómicos", "Psicosociales", "Seguridad"])
                descripcion = st.text_area("Descripción detallada*", height=100)
                ubicacion = st.text_input("Ubicación / Área*")
            with col2:
                st.markdown("### Evaluación del riesgo")
                probabilidad = st.slider("Probabilidad (1-4)", 1, 4, 2,
                    help="1:Baja 2:Media 3:Alta 4:Muy Alta")
                severidad = st.slider("Severidad (1-3)", 1, 3, 2,
                    help="1:Ligero 2:Dañino 3:Extremo")
                nivel = db.calcular_nivel(probabilidad, severidad)
                colores = {"I": "🔴 Nivel I - Alto", "II": "🟠 Nivel II - Medio", "III": "🟡 Nivel III - Bajo"}
                st.info(f"**Nivel de riesgo:** {colores.get(nivel, nivel)}")
            
            if st.form_submit_button("💾 Guardar Peligro", use_container_width=True):
                if descripcion and ubicacion:
                    db.crear_peligro(tipo, descripcion, ubicacion, probabilidad, severidad)
                    st.success("✅ Peligro guardado exitosamente!")
                    st.rerun()
                else:
                    st.error("❌ Descripción y ubicación son obligatorios")
    
    with tab2:
        st.subheader("Peligros Registrados")
        df = db.obtener_peligros()
        if not df.empty:
            st.dataframe(df[['id', 'tipo', 'descripcion', 'ubicacion', 'nivel_riesgo', 'fecha_creacion']], 
                        use_container_width=True)
            
            # Eliminar peligro
            st.markdown("---")
            col1, col2 = st.columns([3,1])
            with col1:
                id_eliminar = st.number_input("ID del peligro a eliminar", min_value=1, step=1)
            with col2:
                if st.button("🗑️ Eliminar", use_container_width=True):
                    conn = db.get_connection()
                    cursor = conn.cursor()
                    cursor.execute("DELETE FROM peligros WHERE id = ?", (id_eliminar,))
                    conn.commit()
                    conn.close()
                    st.success(f"✅ Peligro {id_eliminar} eliminado")
                    st.rerun()
        else:
            st.info("📭 No hay peligros registrados. Agrega uno en la pestaña 'Nuevo Peligro'")
