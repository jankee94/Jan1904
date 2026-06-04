import streamlit as st
import pandas as pd
from database import db

def show():
    st.markdown("## 📊 FASE 3: Evaluar Riesgos")
    st.markdown("---")
    
    df = db.obtener_peligros()
    
    if not df.empty:
        st.subheader("Matriz de Riesgos GTC-45")
        
        # Mostrar matriz visual
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("### Distribución por nivel")
            nivel_counts = df['nivel_riesgo'].value_counts()
            st.bar_chart(nivel_counts)
        
        with col2:
            st.markdown("### Resumen")
            st.metric("Total peligros", len(df))
            st.metric("Nivel I (Alto)", len(df[df['nivel_riesgo'] == 'I']))
            st.metric("Nivel II (Medio)", len(df[df['nivel_riesgo'] == 'II']))
            st.metric("Nivel III (Bajo)", len(df[df['nivel_riesgo'] == 'III']))
        
        st.markdown("---")
        st.subheader("Detalle de Evaluación")
        st.dataframe(df[['id', 'tipo', 'descripcion', 'ubicacion', 'probabilidad', 'severidad', 'nivel_riesgo']], 
                    use_container_width=True)
        
        # Alertas
        riesgos_criticos = df[df['nivel_riesgo'] == 'I']
        if not riesgos_criticos.empty:
            st.error(f"🚨 ALERTA: {len(riesgos_criticos)} riesgo(s) nivel I detectados. Requieren acción inmediata.")
    else:
        st.warning("⚠️ No hay peligros registrados. Ve a 'Fase 2: Identificar Peligros' primero.")
