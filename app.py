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
        url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-flash-latest:generateContent"
        headers = {
            "Content-Type": "application/json",
            "X-goog-api-key": key
        }
        payload = {
            "contents": [
                {
                    "parts": [
                        {"text": prompt}
                    ]
                }
            ]
        }
        r = requests.post(url, json=payload, headers=headers, timeout=30)
        if r.status_code == 200:
            data = r.json()
            return data["candidates"][0]["content"]["parts"][0]["text"]
        else:
            st.error(f"API error: {r.status_code} - {r.text[:200]}")
            return None
    except Exception as e:
        st.error(f"Exception: {e}")
        return None

# Login
if not st.session_state.auth:
    st.title("SG-SST PHVA")
    col1, col2, col3 = st.columns([1,2,1])
    with col2:
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
        opcion = st.radio("Menú", ["Diagnóstico", "Chat", "Test IA"])
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
                st.success(f"Key encontrada: {key[:15]}...")
                res = call_gemini("Responde solo: OK")
                if res:
                    st.success(f"Respuesta: {res}")
                else:
                    st.error("Gemini no respondió (ver detalle arriba)")
        st.info("Secrets configurado correctamente")
    
    elif opcion == "Diagnóstico":
        st.title("Diagnóstico IA")
        with st.form("f"):
            nit = st.text_input("NIT")
            tra = st.number_input("Trabajadores", min_value=1, value=10)
            arl = st.selectbox("ARL", ["Positiva", "Sura", "Colpatria"])
            if st.form_submit_button("Generar diagnóstico"):
                with st.spinner("IA..."):
                    prompt = f"NIT:{nit} Trabajadores:{tra} ARL:{arl}. Genera diagnóstico SST completo."
                    res = call_gemini(prompt)
                    if res:
                        st.markdown(res)
                    else:
                        st.error("No se pudo obtener respuesta")
    
    else:  # Chat
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
                r = "Lo siento, no pude procesar tu consulta."
            with st.chat_message("assistant"):
                st.markdown(r)
            st.session_state.msgs.append({"r": "assistant", "c": r})
