import streamlit as st
import requests

st.set_page_config(page_title="SG-SST PHVA", layout="wide")

st.markdown("""
<style>
.stApp { background: linear-gradient(135deg, #0f0c29, #302b63, #24243e); }
.main-header { background: linear-gradient(135deg, #667eea, #764ba2); padding: 20px; border-radius: 15px; }
</style>
""", unsafe_allow_html=True)

# ========== IA CORREGIDA ==========
def call_gemini():
    try:
        key = st.secrets.get("GEMINI_API_KEY_1")
        if not key:
            key = st.secrets.get("GEMINI_API_KEY")
        if not key:
            return "No hay Gemini key configurada"
        
        # IMPORTANTE: Usar el modelo correcto gemini-1.5-flash
        url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent"
        headers = {"Content-Type": "application/json", "x-goog-api-key": key}
        data = {"contents": [{"parts": [{"text": "Responde solo: OK"}]}]}
        
        response = requests.post(url, json=data, headers=headers, timeout=30)
        
        if response.status_code == 200:
            result = response.json()
            texto = result["candidates"][0]["content"]["parts"][0]["text"]
            return f"✅ Gemini responde: {texto}"
        else:
            return f"❌ Error {response.status_code}: {response.text[:200]}"
    except Exception as e:
        return f"❌ Error: {e}"

def call_groq():
    try:
        key = st.secrets.get("GROQ_API_KEY")
        if not key:
            return "No hay Groq key configurada"
        
        url = "https://api.groq.com/openai/v1/chat/completions"
        headers = {"Authorization": f"Bearer {key}", "Content-Type": "application/json"}
        data = {"model": "llama-3.3-70b-versatile", "messages": [{"role": "user", "content": "Responde solo: OK"}], "temperature": 0.7}
        
        response = requests.post(url, json=data, headers=headers, timeout=30)
        
        if response.status_code == 200:
            texto = response.json()["choices"][0]["message"]["content"]
            return f"✅ Groq responde: {texto}"
        else:
            return f"❌ Error {response.status_code}: {response.text[:200]}"
    except Exception as e:
        return f"❌ Error: {e}"

def chat_ia(pregunta):
    try:
        key = st.secrets.get("GEMINI_API_KEY_1")
        if not key:
            key = st.secrets.get("GEMINI_API_KEY")
        
        url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent"
        headers = {"Content-Type": "application/json", "x-goog-api-key": key}
        data = {"contents": [{"parts": [{"text": f"Eres un experto en SST. Responde: {pregunta}"}]}]}
        
        response = requests.post(url, json=data, headers=headers, timeout=30)
        
        if response.status_code == 200:
            return response.json()["candidates"][0]["content"]["parts"][0]["text"]
        else:
            return f"Error: {response.status_code}"
    except Exception as e:
        return f"Error: {e}"

# ========== LOGIN ==========
if "auth" not in st.session_state:
    st.session_state.auth = False

if not st.session_state.auth:
    col1, col2, col3 = st.columns([1, 1.2, 1])
    with col2:
        st.markdown('<div class="main-header"><h1 style="text-align:center">SG-SST PHVA</h1></div>', unsafe_allow_html=True)
        with st.form("login"):
            u = st.text_input("Usuario")
            p = st.text_input("Contraseña", type="password")
            if st.form_submit_button("Ingresar"):
                if u == "admin" and p == "admin123":
                    st.session_state.auth = True
                    st.rerun()
                else:
                    st.error("Use admin / admin123")
    st.stop()

# ========== SIDEBAR ==========
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/2917/2917995.png", width=50)
    menu = st.radio("Menú", ["Dashboard", "Chat IA"])
    if st.button("Salir"):
        st.session_state.auth = False
        st.rerun()

# ========== DASHBOARD ==========
if menu == "Dashboard":
    st.markdown('<div class="main-header"><h1>📊 Dashboard</h1></div>', unsafe_allow_html=True)
    
    st.subheader("🤖 Prueba de API Keys")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🔌 Probar Gemini", use_container_width=True):
            with st.spinner("Conectando con Gemini..."):
                resultado = call_gemini()
                if "✅" in resultado:
                    st.success(resultado)
                    st.balloons()
                else:
                    st.error(resultado)
    
    with col2:
        if st.button("🔌 Probar Groq", use_container_width=True):
            with st.spinner("Conectando con Groq..."):
                resultado = call_groq()
                if "✅" in resultado:
                    st.success(resultado)
                    st.balloons()
                else:
                    st.error(resultado)
    
    st.markdown("---")
    st.info("Gemini: modelo gemini-1.5-flash | Groq: modelo llama-3.3-70b-versatile")

# ========== CHAT IA ==========
elif menu == "Chat IA":
    st.markdown('<div class="main-header"><h1>💬 Chat IA</h1></div>', unsafe_allow_html=True)
    
    if "messages" not in st.session_state:
        st.session_state.messages = []
    
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.write(msg["content"])
    
    if prompt := st.chat_input("Pregunta sobre SST..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("assistant"):
            with st.spinner("Pensando..."):
                respuesta = chat_ia(prompt)
                st.write(respuesta)
                st.session_state.messages.append({"role": "assistant", "content": respuesta})

st.markdown("---")
st.markdown("<p style='text-align:center'>SG-SST PHVA | JAN BENITEZ</p>", unsafe_allow_html=True)
