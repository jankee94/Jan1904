import streamlit as st
import requests

st.set_page_config(page_title="SG-SST PHVA", layout="wide")

st.markdown("""
<style>
.stApp { background: linear-gradient(135deg, #0f0c29, #302b63, #24243e); }
.main-header { background: linear-gradient(135deg, #667eea, #764ba2); padding: 20px; border-radius: 15px; }
</style>
""", unsafe_allow_html=True)

# ========== IA CON MODELOS ACTIVOS ==========

# Gemini - modelo activo: gemini-2.0-flash-exp
def call_gemini():
    try:
        key = st.secrets.get("GEMINI_API_KEY_1")
        if not key:
            key = st.secrets.get("GEMINI_API_KEY")
        if not key:
            return "No hay Gemini key"
        
        # Modelo activo de Gemini
        url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash-exp:generateContent"
        headers = {"Content-Type": "application/json", "x-goog-api-key": key}
        data = {"contents": [{"parts": [{"text": "Responde solo: OK"}]}]}
        
        r = requests.post(url, json=data, headers=headers, timeout=30)
        
        if r.status_code == 200:
            texto = r.json()["candidates"][0]["content"]["parts"][0]["text"]
            return f"✅ Gemini: {texto}"
        else:
            return f"❌ Error {r.status_code}: {r.text[:150]}"
    except Exception as e:
        return f"❌ Error: {e}"

# Groq - modelo activo: llama-3.3-70b-specdec
def call_groq():
    try:
        key = st.secrets.get("GROQ_API_KEY")
        if not key:
            return "No hay Groq key"
        
        url = "https://api.groq.com/openai/v1/chat/completions"
        headers = {"Authorization": f"Bearer {key}", "Content-Type": "application/json"}
        data = {"model": "llama-3.3-70b-specdec", "messages": [{"role": "user", "content": "Responde solo: OK"}], "temperature": 0.7}
        
        r = requests.post(url, json=data, headers=headers, timeout=30)
        
        if r.status_code == 200:
            texto = r.json()["choices"][0]["message"]["content"]
            return f"✅ Groq: {texto}"
        else:
            return f"❌ Error {r.status_code}: {r.text[:150]}"
    except Exception as e:
        return f"❌ Error: {e}"

def chat_gemini(pregunta):
    try:
        key = st.secrets.get("GEMINI_API_KEY_1")
        if not key:
            key = st.secrets.get("GEMINI_API_KEY")
        
        url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash-exp:generateContent"
        headers = {"Content-Type": "application/json", "x-goog-api-key": key}
        data = {"contents": [{"parts": [{"text": f"Eres un experto en Seguridad y Salud en el Trabajo (SST) en Colombia. Responde de forma clara y profesional: {pregunta}"}]}]}
        
        r = requests.post(url, json=data, headers=headers, timeout=30)
        
        if r.status_code == 200:
            return r.json()["candidates"][0]["content"]["parts"][0]["text"]
        else:
            return f"Error: {r.status_code}"
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

with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/2917/2917995.png", width=50)
    menu = st.radio("Menu", ["Dashboard", "Chat IA"])
    if st.button("Salir"):
        st.session_state.auth = False
        st.rerun()

if menu == "Dashboard":
    st.markdown('<div class="main-header"><h1>Dashboard</h1></div>', unsafe_allow_html=True)
    
    st.subheader("🤖 Prueba de API Keys")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🔌 Probar Gemini", use_container_width=True):
            with st.spinner("Probando Gemini..."):
                r = call_gemini()
                if "✅" in r:
                    st.success(r)
                    st.balloons()
                else:
                    st.error(r)
    with col2:
        if st.button("🔌 Probar Groq", use_container_width=True):
            with st.spinner("Probando Groq..."):
                r = call_groq()
                if "✅" in r:
                    st.success(r)
                    st.balloons()
                else:
                    st.error(r)
    
    st.markdown("---")
    st.info("Gemini: gemini-2.0-flash-exp | Groq: llama-3.3-70b-specdec")

elif menu == "Chat IA":
    st.markdown('<div class="main-header"><h1>Chat IA</h1></div>', unsafe_allow_html=True)
    
    if "msgs" not in st.session_state:
        st.session_state.msgs = [{"role": "assistant", "content": "Hola, soy tu asistente SST. ¿En qué puedo ayudarte?"}]
    
    for m in st.session_state.msgs:
        with st.chat_message(m["role"]):
            st.write(m["content"])
    
    if p := st.chat_input("Pregunta sobre SST..."):
        st.session_state.msgs.append({"role": "user", "content": p})
        with st.chat_message("assistant"):
            with st.spinner("Consultando IA..."):
                r = chat_gemini(p)
                st.write(r)
                st.session_state.msgs.append({"role": "assistant", "content": r})

st.markdown("---")
st.markdown("<p style='text-align:center'>SG-SST PHVA | JAN BENITEZ</p>", unsafe_allow_html=True)
