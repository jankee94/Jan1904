import streamlit as st

def render(db, ia, auth_manager):
    st.title("🤖 Chat IA")
    
    if "msg" not in st.session_state:
        st.session_state.msg = []
    
    for m in st.session_state.msg:
        with st.chat_message(m["rol"]):
            st.markdown(m["contenido"])
    
    if p := st.chat_input("Pregunta:"):
        st.session_state.msg.append({"rol": "user", "contenido": p})
        r = ia.call_gemini(p)
        st.session_state.msg.append({"rol": "assistant", "contenido": r})
        st.rerun()
