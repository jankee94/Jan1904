import streamlit as st
from core.ia_engine import ia

st.set_page_config(page_title="SST PHVA")

if "auth" not in st.session_state:
    st.session_state.auth = False

if not st.session_state.auth:
    st.title("SG-SST PHVA")
    u = st.text_input("Usuario")
    p = st.text_input("Contraseña", type="password")
    if st.button("Ingresar"):
        if u == "admin" and p == "sst2024":
            st.session_state.auth = True
            st.rerun()
else:
    st.sidebar.title("Menu")
    op = st.sidebar.radio("", ["Diagnostico", "Chat"])
    
    if op == "Diagnostico":
        st.title("Diagnostico")
        with st.form("f"):
            nit = st.text_input("NIT")
            tra = st.number_input("Trabajadores", min_value=1, value=10)
            arl = st.selectbox("ARL", ["Positiva", "Sura"])
            if st.form_submit_button("Generar"):
                res = ia.generar_diagnostico({"nit": nit, "trabajadores": tra, "arl": arl})
                st.write(res)
    else:
        st.title("Chat")
        if "m" not in st.session_state:
            st.session_state.m = []
        for msg in st.session_state.m:
            st.chat_message(msg["r"]).write(msg["c"])
        p = st.chat_input("Pregunta:")
        if p:
            st.session_state.m.append({"r": "user", "c": p})
            st.chat_message("user").write(p)
            r = ia.call_gemini(p) or "Error"
            st.chat_message("assistant").write(r)
            st.session_state.m.append({"r": "assistant", "c": r})
