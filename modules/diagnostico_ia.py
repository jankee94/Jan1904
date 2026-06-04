import streamlit as st
from datetime import datetime, timedelta
from core.db import db
from core.ia_engine import ia

def render():
    st.title("🤖 DIAGNÓSTICO IA")
    
    empresa = db.obtener_empresa()
    
    if empresa:
        st.success(f"✅ Empresa: {empresa.get('nombre', '')}")
        st.info(f"👥 {empresa.get('trabajadores', 0)} trabajadores | ARL: {empresa.get('arl', '')}")
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            if st.button("⚠️ Peligros"):
                st.session_state.page = "Peligros"
                st.rerun()
        with col2:
            if st.button("👥 Trabajadores"):
                st.session_state.page = "Trabajadores"
                st.rerun()
        with col3:
            if st.button("✅ Plan Acción"):
                st.session_state.page = "Plan de Acción"
                st.rerun()
        with col4:
            if st.button("📝 Incidentes"):
                st.session_state.page = "Incidentes"
                st.rerun()
        
        with st.expander("Ver diagnóstico completo"):
            st.markdown(empresa.get('diagnostico_ia', ''))
        return
    
    with st.form("form_diagnostico"):
        nombre = st.text_input("Nombre empresa *")
        trabajadores = st.number_input("Trabajadores", min_value=1, value=10)
        arl = st.selectbox("ARL", ["Positiva", "Sura", "Colpatria"])
        
        if st.form_submit_button("Generar Diagnóstico"):
            if nombre:
                with st.spinner("IA generando..."):
                    prompt = f"Diagnóstico SST para {nombre} con {trabajadores} trabajadores, ARL {arl}"
                    respuesta = ia.call_best(prompt)
                    
                    if respuesta:
                        db.guardar_empresa("", nombre, trabajadores, arl, "", respuesta)
                        
                        peligros = [
                            ("Ergonómico", f"Posturas inadecuadas en {nombre}", "Oficinas", 2, 2),
                            ("Seguridad", "Caídas al mismo nivel", "Todas", 2, 2),
                            ("Psicosocial", "Estrés laboral", "Administrativo", 2, 2),
                        ]
                        for p in peligros:
                            db.guardar_peligro(p[0], p[1], p[2], p[3], p[4], 1)
                        
                        fecha = datetime.now()
                        acciones = [
                            (f"Matriz de riesgos para {nombre}", "SST", (fecha + timedelta(days=30)).strftime("%Y-%m-%d"), "Alta"),
                            ("Capacitación en prevención", "SST", (fecha + timedelta(days=45)).strftime("%Y-%m-%d"), "Alta"),
                        ]
                        for a in acciones:
                            db.guardar_accion(0, a[0], a[1], a[2], a[3], 1)
                        
                        st.success("✅ Diagnóstico generado")
                        st.rerun()
