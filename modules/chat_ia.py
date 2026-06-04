import streamlit as st
from core.ia_engine import ia

def render():
    st.title("💬 Chat")
    
    if "msgs" not in st.session_state:
        st.session_state.msgs = []
    
    for msg in st.session_state.msgs:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])
    
    if prompt := st.chat_input("Pregunta..."):
        st.session_state.msgs.append({"role": "user", "content": prompt})
        respuesta = ia.call_best(prompt)
        st.session_state.msgs.append({"role": "assistant", "content": respuesta or "Error"})
        st.rerun()
