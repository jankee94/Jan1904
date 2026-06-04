import streamlit as st
import requests
import sys

st.set_page_config(page_title="Test IA", layout="centered")

st.title("🔧 DIAGNOSTICO DE IA")

st.write(f"Python version: {sys.version}")

# Verificar Secrets
try:
    key = st.secrets.get("GEMINI_API_KEY")
    if key:
        st.success(f"✅ API Key encontrada: {key[:15]}...")
    else:
        st.error("❌ GEMINI_API_KEY NO encontrada en Secrets")
except Exception as e:
    st.error(f"❌ Error leyendo Secrets: {e}")

# Probar conexion a Gemini
if st.button("Probar Gemini"):
    with st.spinner("Conectando..."):
        api_key = st.secrets.get("GEMINI_API_KEY")
        if api_key:
            url = "https://generativelanguage.googleapis.com/v1/models/gemini-pro:generateContent"
            headers = {"Content-Type": "application/json", "x-goog-api-key": api_key}
            data = {"contents": [{"parts": [{"text": "Responde solo: OK"}]}]}
            try:
                r = requests.post(url, json=data, headers=headers, timeout=10)
                st.write(f"Status code: {r.status_code}")
                if r.status_code == 200:
                    st.success("✅ Gemini FUNCIONA!")
                    st.json(r.json())
                else:
                    st.error(f"❌ Error {r.status_code}: {r.text[:200]}")
            except Exception as e:
                st.error(f"❌ Excepcion: {e}")
        else:
            st.error("❌ No hay API key")

st.info("""
**Instrucciones:**
1. En Streamlit Cloud → Settings → Secrets
2. Agrega: GEMINI_API_KEY = "tu_key_aqui"
3. Guarda y Reboot
""")
