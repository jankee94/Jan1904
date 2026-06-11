import streamlit as st
import requests

st.set_page_config(page_title="SG-SST PHVA", layout="wide")

st.markdown("""
<style>
.stApp { background: linear-gradient(135deg, #0f0c29, #302b63, #24243e); }
.main-header { background: linear-gradient(135deg, #667eea, #764ba2); padding: 20px; border-radius: 15px; }
</style>
""", unsafe_allow_html=True)

# ========== SOLO GROQ ==========
def call_groq():
    try:
        key = st.secrets.get("GROQ_API_KEY")
        if not key:
            return "No hay Groq key configurada"
        
        # Probar modelos de Groq
        modelos = ["llama3-70b-8192", "llama3-8b-8192", "mixtral-8x7b-32768"]
        
        for modelo in modelos:
            url = "https://api.groq.com/openai/v1/chat/completions"
            headers = {"Authorization": f"Bearer {key}", "Content-Type": "application/json"}
            data = {"model": modelo, "messages": [{"role": "user", "content": "Responde solo: OK"}], "temperature": 0.7}
            
            try:
                r = requests.post(url, json=data, headers=headers, timeout=10)
                if r.status_code == 200:
                    texto = r.json()["choices"][0]["message"]["content"]
                    return f"✅ Groq ({modelo}): {texto}"
            except:
                continue
        
        return "❌ Error: No se encontró modelo válido"
    except Exception as e:
        return f"❌ Error: {e}"

def chat_groq(pregunta):
    try:
        key = st.secrets.get("GROQ_API_KEY")
        if not key:
            return "No hay Groq key"
        
        url = "https://api.groq.com/openai/v1/chat/completions"
        headers = {"Authorization": f"Bearer {key}", "Content-Type": "application/json"}
        data = {"model": "llama3-70b-8192", "messages": [{"role": "user", "content": f"Eres un experto en SST. Responde: {pregunta}"}], "temperature": 0.7}
        
        r = requests.post(url, json=data, headers=headers, timeout=30)
        
        if r.status_code == 200:
            return r.json()["choices"][0]["message"]["content"]
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
    
    st.subheader("🤖 Prueba de Groq API")
    
    if st.button("🔌 Probar Groq", use_container_width=True):
        with st.spinner("Probando Groq..."):
            r = call_groq()
            if "✅" in r:
                st.success(r)
                st.balloons()
            else:
                st.error(r)
    
    st.markdown("---")
    st.warning("⚠️ Gemini no está configurado. Usando solo Groq.")
    st.info("Para usar Gemini, crea una nueva API key en: https://makersuite.google.com/app/apikey")

elif menu == "Chat IA":
    st.markdown('<div class="main-header"><h1>Chat IA</h1></div>', unsafe_allow_html=True)
    
    if "msgs" not in st.session_state:
        st.session_state.msgs = [{"role": "assistant", "content": "Hola, soy tu asistente SST (usando Groq). ¿En qué puedo ayudarte?"}]
    
    for m in st.session_state.msgs:
        with st.chat_message(m["role"]):
            st.write(m["content"])
    
    if p := st.chat_input("Pregunta sobre SST..."):
        st.session_state.msgs.append({"role": "user", "content": p})
        with st.chat_message("assistant"):
            with st.spinner("Consultando Groq..."):
                r = chat_groq(p)
                st.write(r)
                st.session_state.msgs.append({"role": "assistant", "content": r})

st.markdown("---")
st.markdown("<p style='text-align:center'>SG-SST PHVA | JAN BENITEZ</p>", unsafe_allow_html=True)
