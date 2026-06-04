import streamlit as st
import requests

st.set_page_config(page_title="SG-SST PHVA", page_icon="🔄", layout="wide")

if "auth" not in st.session_state:
    st.session_state.auth = False
if "emp" not in st.session_state:
    st.session_state.emp = {}

def get_key():
    try:
        return st.secrets.get("GEMINI_API_KEY")
    except:
        return None

def call_gemini(prompt):
    key = get_key()
    if not key:
        return None
    try:
        url = "https://generativelanguage.googleapis.com/v1/models/gemini-pro:generateContent"
        headers = {"Content-Type": "application/json", "x-goog-api-key": key}
        data = {"contents": [{"parts": [{"text": prompt}]}]}
        r = requests.post(url, json=data, headers=headers, timeout=30)
        if r.status_code == 200:
            return r.json()["candidates"][0]["content"]["parts"][0]["text"]
        return None
    except:
        return None

if not st.session_state.auth:
    st.title("SG-SST PHVA")
    u = st.text_input("Usuario")
    p = st.text_input("Contraseña", type="password")
    if st.button("Ingresar"):
        if u == "admin" and p == "sst2024":
            st.session_state.auth = True
            st.rerun()
        else:
            st.error("Use admin / sst2024")
else:
    with st.sidebar:
        st.image("https://cdn-icons-png.flaticon.com/512/2917/2917995.png", width=60)
        opcion = st.radio("Menu", ["Diagnostico", "Chat", "Test IA"])
        if st.button("Salir"):
            st.session_state.auth = False
            st.rerun()
    
    if opcion == "Test IA":
        st.title("Test IA")
        if st.button("Probar Gemini"):
            key = get_key()
            if not key:
                st.error("No hay API key")
            else:
                st.success(f"Key: {key[:10]}...")
                res = call_gemini("Responde OK")
                if res:
                    st.success(f"Respuesta: {res}")
                else:
                    st.error("Gemini no responde")
        st.info("Configurar Secrets: GEMINI_API_KEY = tu_key")
    
    elif opcion == "Diagnostico":
        st.title("Diagnostico IA")
        with st.form("f"):
            nit = st.text_input("NIT")
            tra = st.number_input("Trabajadores", min_value=1, value=10)
            arl = st.selectbox("ARL", ["Positiva", "Sura", "Colpatria"])
            if st.form_submit_button("Generar"):
                with st.spinner("IA..."):
                    prompt = f"NIT:{nit} Trabajadores:{tra} ARL:{arl}. Genera diagnostico SST."
                    res = call_gemini(prompt)
                    if res:
                        st.markdown(res)
                    else:
                        st.error("IA no disponible. Verifica API key.")
    
    else:
        st.title("Chat IA")
        if "msgs" not in st.session_state:
            st.session_state.msgs = []
        for m in st.session_state.msgs:
            with st.chat_message(m["r"]):
                st.markdown(m["c"])
        p = st.chat_input("Pregunta:")
        if p:
            st.session_state.msgs.append({"r": "user", "c": p})
            with st.chat_message("user"):
                st.markdown(p)
            r = call_gemini(p)
            if not r:
                r = "IA no disponible"
            with st.chat_message("assistant"):
                st.markdown(r)
            st.session_state.msgs.append({"r": "assistant", "c": r})
