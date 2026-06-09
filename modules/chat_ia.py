import streamlit as st
import requests

def render():
    st.title("💬 CHAT IA")
    
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
        return "⚠️ IA no disponible. Intente más tarde."
    
    if "chat_messages" not in st.session_state:
        st.session_state.chat_messages = []
    
    for msg in st.session_state.chat_messages:
        with st.chat_message(msg["role"]):
            st.write(msg["content"])
    
    if prompt := st.chat_input("Pregunta sobre SST..."):
        st.session_state.chat_messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.write(prompt)
        
        with st.chat_message("assistant"):
            with st.spinner("🤖 Pensando..."):
                respuesta = call_ia(prompt)
                st.write(respuesta)
                st.session_state.chat_messages.append({"role": "assistant", "content": respuesta})
