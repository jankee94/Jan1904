import streamlit as st
import sqlite3
import pandas as pd

def render():
    st.title("⚠️ PELIGROS - FASE 2 GTC-45")
    
    conn = sqlite3.connect("sst.db", check_same_thread=False)
    cursor = conn.cursor()
    empresa_id = st.session_state.get("empresa_actual_id", 1)
    
    tab1, tab2 = st.tabs(["📋 Lista de Peligros", "➕ Agregar Peligro"])
    
    with tab1:
        try:
            df = pd.read_sql_query("SELECT * FROM peligros", conn)
            if not df.empty:
                st.dataframe(df, use_container_width=True)
            else:
                st.info("No hay peligros registrados")
        except:
            st.info("No hay peligros registrados")
    
    with tab2:
        with st.form("form_peligro"):
            tipo = st.selectbox("Tipo de Peligro", ["Físico", "Químico", "Biológico", "Ergonómico", "Psicosocial", "Seguridad"])
            descripcion = st.text_area("Descripción")
            probabilidad = st.slider("Probabilidad (1-4)", 1, 4, 2)
            severidad = st.slider("Severidad (1-3)", 1, 3, 2)
            
            # Calcular nivel de riesgo
            matriz = {(1,1):"III",(1,2):"II",(1,3):"I",(2,1):"III",(2,2):"II",(2,3):"I",
                      (3,1):"II",(3,2):"I",(3,3):"I",(4,1):"II",(4,2):"I",(4,3):"I"}
            nivel = matriz.get((probabilidad, severidad), "III")
            
            if nivel == "I":
                st.error("🔴 NIVEL I - RIESGO ALTO")
            elif nivel == "II":
                st.warning("🟠 NIVEL II - RIESGO MEDIO")
            else:
                st.info("🟡 NIVEL III - RIESGO BAJO")
            
            if st.form_submit_button("💾 Guardar Peligro", use_container_width=True):
                if descripcion:
                    cursor.execute('''INSERT INTO peligros (empresa_id, tipo, descripcion, probabilidad, severidad, nivel) 
                                      VALUES (?, ?, ?, ?, ?, ?)''',
                                  (empresa_id, tipo, descripcion, probabilidad, severidad, nivel))
                    conn.commit()
                    st.success("✅ Peligro guardado")
                    st.rerun()
                else:
                    st.error("Ingrese una descripción")
    
    conn.close()
