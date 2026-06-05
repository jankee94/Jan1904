import streamlit as st
import pandas as pd
from core.db import db
from utils.exporters import boton_exportar

def render():
    st.title("⚠️ PELIGROS - FASE 2 (GTC-45)")
    
    tab1, tab2 = st.tabs(["📋 Lista de Peligros", "➕ Agregar Peligro"])
    
    with tab1:
        df = db.obtener_peligros()
        if not df.empty:
            st.dataframe(df, use_container_width=True)
            boton_exportar(df, "Peligros")
            
            with st.expander("🗑️ Eliminar peligro"):
                id_elim = st.number_input("ID del peligro", min_value=1, step=1)
                if st.button("Eliminar"):
                    db.eliminar_peligro(id_elim)
                    st.rerun()
        else:
            st.info("📭 No hay peligros registrados")
    
    with tab2:
        with st.form("form_peligro"):
            col1, col2 = st.columns(2)
            with col1:
                tipo = st.selectbox("Tipo", ["Físico", "Químico", "Biológico", "Ergonómico", "Psicosocial", "Seguridad"])
                desc = st.text_area("Descripción detallada")
            with col2:
                prob = st.slider("Probabilidad (1-4)", 1, 4, 2, help="1:Baja, 2:Media, 3:Alta, 4:Muy Alta")
                sev = st.slider("Severidad (1-3)", 1, 3, 2, help="1:Ligero, 2:Dañino, 3:Extremo")
                matriz = {(1,1):"III",(1,2):"II",(1,3):"I",(2,1):"III",(2,2):"II",(2,3):"I",
                          (3,1):"II",(3,2):"I",(3,3):"I",(4,1):"II",(4,2):"I",(4,3):"I"}
                nivel = matriz.get((prob, sev), "III")
                if nivel == "I":
                    st.error(f"🔴 NIVEL I - RIESGO ALTO")
                elif nivel == "II":
                    st.warning(f"🟠 NIVEL II - RIESGO MEDIO")
                else:
                    st.info(f"🟡 NIVEL III - RIESGO BAJO")
            
            if st.form_submit_button("💾 Guardar Peligro", use_container_width=True):
                if desc:
                    db.guardar_peligro(tipo, desc, prob, sev)
                    st.success("✅ Peligro guardado")
                    st.rerun()
