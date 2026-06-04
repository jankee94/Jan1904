import streamlit as st
import requests
from core.ia_engine import ia_engine

st.set_page_config(page_title="SG-SST PHVA", page_icon="🔄", layout="wide")

if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
if "empresa" not in st.session_state:
    st.session_state.empresa = {}
if "chat_messages" not in st.session_state:
    st.session_state.chat_messages = []

def get_gemini_key():
    try:
        return st.secrets.get("GEMINI_API_KEY")
    except:
        import os
        return os.environ.get("GEMINI_API_KEY")

def test_gemini():
    api_key = get_gemini_key()
    if not api_key:
        return "❌ API Key no encontrada"
    try:
        url = "https://generativelanguage.googleapis.com/v1/models/gemini-pro:generateContent"
        headers = {"Content-Type": "application/json", "x-goog-api-key": api_key}
        payload = {"contents": [{"parts": [{"text": "Responde OK"}]}]}
        response = requests.post(url, json=payload, headers=headers, timeout=10)
        if response.status_code == 200:
            return "✅ Gemini conectado!"
        else:
            return f"❌ Error: {response.status_code}"
    except Exception as e:
        return f"❌ Error: {str(e)}"

if not st.session_state.authenticated:
    st.markdown("<h1 style='text-align:center'>SG-SST PHVA</h1>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        user = st.text_input("Usuario")
        pwd = st.text_input("Contraseña", type="password")
        if st.button("Ingresar"):
            if user == "admin" and pwd == "sst2024":
                st.session_state.authenticated = True
                st.rerun()
            else:
                st.error("Use: admin / sst2024")
else:
    with st.sidebar:
        st.image("https://cdn-icons-png.flaticon.com/512/2917/2917995.png", width=60)
        menu = st.radio("Menu", ["Dashboard", "Diagnostico IA", "Asistente IA", "Test IA"])
        if st.button("Cerrar Sesion"):
            st.session_state.authenticated = False
            st.rerun()
    
    if menu == "Test IA":
        st.title("Prueba de IA")
        if st.button("Probar Gemini"):
            resultado = test_gemini()
            if "✅" in resultado:
                st.success(resultado)
            else:
                st.error(resultado)
        st.info("Configurar secrets: GEMINI_API_KEY = 'tu_key'")
    
    elif menu == "Diagnostico IA":
        st.title("Diagnostico con IA")
        with st.form("form"):
            col1, col2, col3 = st.columns(3)
            with col1:
                nit = st.text_input("NIT", value=st.session_state.empresa.get("nit", ""))
            with col2:
                trabajadores = st.number_input("Trabajadores", min_value=1, value=10)
            with col3:
                arl = st.selectbox("ARL", ["Positiva", "Sura", "Colpatria"])
            if st.form_submit_button("Generar"):
                with st.spinner("IA generando..."):
                    st.session_state.empresa = {"nit": nit, "trabajadores": trabajadores, "arl": arl}
                    resultado = ia_engine.generar_diagnostico(st.session_state.empresa)
                    st.markdown(resultado)
    
    elif menu == "Asistente IA":
        st.title("Asistente IA")
        for msg in st.session_state.chat_messages:
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])
        if prompt := st.chat_input("Pregunta:"):
            st.session_state.chat_messages.append({"role": "user", "content": prompt})
            with st.chat_message("user"):
                st.markdown(prompt)
            respuesta = ia_engine.responder_chat(prompt, {})
            with st.chat_message("assistant"):
                st.markdown(respuesta)
            st.session_state.chat_messages.append({"role": "assistant", "content": respuesta})
    
    else:
        st.title("Dashboard")
        if st.session_state.empresa.get("nit"):
            st.metric("NIT", st.session_state.empresa.get("nit"))
            st.metric("Trabajadores", st.session_state.empresa.get("trabajadores", 0))
