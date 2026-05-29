import streamlit as st
from groq import Groq
import os

def show():
    st.markdown("""
    <div style="background: linear-gradient(135deg, #ff6b6b, #ee5a24); padding: 1rem; border-radius: 20px; text-align: center; margin-bottom: 2rem;">
        <h1 style="color: white;">🐾 Asistente Peppet</h1>
        <p style="color: white;">Potenciado por Groq - Ultra rápido</p>
    </div>
    """, unsafe_allow_html=True)
    
    api_key = os.getenv("GROQ_API_KEY")
    
    if not api_key:
        st.error("❌ GROQ_API_KEY no encontrada")
        return
    
    client = Groq(api_key=api_key)
    
    if "peppet_messages" not in st.session_state:
        st.session_state.peppet_messages = [
            {"role": "system", "content": "Eres Peppet, un asistente experto en Python y Streamlit."},
            {"role": "assistant", "content": "🐾 Hola! Soy Peppet. ¿En qué puedo ayudarte?"}
        ]
    
    for msg in st.session_state.peppet_messages:
        if msg["role"] != "system":
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])
    
    if prompt := st.chat_input("Habla con Peppet..."):
        st.session_state.peppet_messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
        
        with st.spinner("🐾 Peppet pensando..."):
            try:
                response = client.chat.completions.create(
                    model="llama-3.3-70b-versatile",
                    messages=st.session_state.peppet_messages
                )
                respuesta = response.choices[0].message.content
            except Exception as e:
                respuesta = f"Error: {e}"
        
        with st.chat_message("assistant"):
            st.markdown(f"🐾 {respuesta}")
        
        st.session_state.peppet_messages.append({"role": "assistant", "content": respuesta})
        st.rerun()
    
    if st.button("🗑️ Limpiar"):
        st.session_state.peppet_messages = st.session_state.peppet_messages[:2]
        st.rerun()