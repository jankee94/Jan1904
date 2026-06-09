import streamlit as st
import sqlite3
import requests
from datetime import datetime

def render():
    st.title("🤖 DIAGNÓSTICO IA")
    
    conn = sqlite3.connect("sst.db", check_same_thread=False)
    cursor = conn.cursor()
    
    def call_ia(prompt):
        try:
            url = "https://generativelanguage.googleapis.com/v1/models/gemini-pro:generateContent"
            headers = {"Content-Type": "application/json", "x-goog-api-key": "AIzaSyD3QhEohGJeYhVtM7JmBZ2nXvZJFxJZv3U"}
            data = {"contents": [{"parts": [{"text": prompt}]}]}
            r = requests.post(url, json=data, headers=headers, timeout=30)
            if r.status_code == 200:
                return r.json()["candidates"][0]["content"]["parts"][0]["text"]
        except:
            pass
        return "⚠️ IA no disponible. Usando modo offline."
    
    with st.form("diagnostico_form"):
        nombre = st.text_input("Nombre de la empresa")
        trabajadores = st.number_input("Número de trabajadores", min_value=1, value=10)
        arl = st.selectbox("ARL", ["Positiva", "Sura", "Colpatria", "Bolivar"])
        
        if st.form_submit_button("🚀 Generar Diagnóstico", use_container_width=True):
            if nombre:
                with st.spinner("🤖 IA generando diagnóstico..."):
                    prompt = f"Realiza un diagnóstico SST para la empresa {nombre} con {trabajadores} trabajadores y ARL {arl}. Incluye recomendaciones iniciales."
                    respuesta = call_ia(prompt)
                    
                    # Guardar en base de datos
                    fecha = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    cursor.execute('''INSERT INTO empresa (nombre, trabajadores, arl, diagnostico, fecha) 
                                      VALUES (?, ?, ?, ?, ?)''', (nombre, trabajadores, arl, respuesta, fecha))
                    conn.commit()
                    empresa_id = cursor.lastrowid
                    st.session_state.empresa_actual_id = empresa_id
                    
                    st.success("✅ Diagnóstico generado exitosamente")
                    st.markdown(respuesta)
            else:
                st.error("Por favor ingrese el nombre de la empresa")
    
    # Mostrar diagnósticos anteriores
    st.markdown("---")
    st.subheader("📋 Diagnósticos anteriores")
    df = pd.read_sql_query("SELECT id, nombre, trabajadores, arl, fecha FROM empresa ORDER BY id DESC", conn)
    if not df.empty:
        st.dataframe(df, use_container_width=True)
    else:
        st.info("No hay diagnósticos previos")
    
    conn.close()
