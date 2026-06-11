import streamlit as st
import requests

st.set_page_config(page_title="SG-SST PHVA", layout="wide")

st.markdown("""
<style>
.stApp { background: linear-gradient(135deg, #0f0c29, #302b63, #24243e); }
.main-header { background: linear-gradient(135deg, #667eea, #764ba2); padding: 20px; border-radius: 15px; }
</style>
""", unsafe_allow_html=True)

# ========== IA CON MODELO ESTABLE ==========

# Gemini - modelo más estable: gemini-1.5-flash (debería funcionar)
def call_gemini():
    try:
        key = st.secrets.get("GEMINI_API_KEY_1")
        if not key:
            key = st.secrets.get("GEMINI_API_KEY")
        if not key:
            return "No hay Gemini key"
        
        # Intentar con múltiples modelos hasta que uno funcione
        modelos = [
            "gemini-1.5-flash",
            "gemini-1.5-pro", 
            "gemini-pro-vision",
            "gemini-pro"
        ]
        
        for modelo in modelos:
            url = f"https://generativelanguage.googleapis.com/v1beta/models/{modelo}:generateContent"
            headers = {"Content-Type": "application/json", "x-goog-api-key": key}
            data = {"contents": [{"parts": [{"text": "Responde solo: OK"}]}]}
            
            try:
                r = requests.post(url, json=data, headers=headers, timeout=10)
                if r.status_code == 200:
                    texto = r.json()["candidates"][0]["content"]["parts"][0]["text"]
                    return f"✅ Gemini ({modelo}): {texto}"
            except:
                continue
        
        return f"❌ Error: No se encontró modelo válido. Prueba con: {modelos}"
    except Exception as e:
        return f"❌ Error: {e}"

# Groq - modelos activos
def call_groq():
    try:
        key = st.secrets.get("GROQ_API_KEY")
        if not key:
            return "No hay Groq key"
        
        modelos_groq = [
            "llama3-70b-8192",
            "llama3-8b-8192",
            "mixtral-8x7b-32768"
        ]
        
        for modelo in modelos_groq:
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
        
        return f"❌ Error: No se encontró modelo válido"
    except Exception as e:
        return f"❌ Error: {e}"

def chat_gemini(pregunta):
    try:
        key = st.secrets.get("GEMINI_API_KEY_1")
        if not key:
            key = st.secrets.get("GEMINI_API_KEY")
        
        # Probar con modelos en orden
        modelos = ["gemini-1.5-flash", "gemini-1.5-pro", "gemini-pro"]
        
        for modelo in modelos:
            url = f"https://generativelanguage.googleapis.com/v1beta/models/{modelo}:generateContent"
            headers = {"Content-Type": "application/json", "x-goog-api-key": key}
            data = {"contents": [{"parts": [{"text": f"Eres un experto en SST. Responde: {pregunta}"}]}]}
            
            try:
                r = requests.post(url, json=data, headers=headers, timeout=30)
                if r.status_code == 200:
                    return r.json()["candidates"][0]["content"]["parts"][0]["text"]
            except:
                continue
        
        return "Error: No se pudo conectar con Gemini"
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
    st.caption("El sistema probará automáticamente varios modelos hasta encontrar uno que funcione")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🔌 Probar Gemini", use_container_width=True):
            with st.spinner("Probando modelos de Gemini..."):
                r = call_gemini()
                if "✅" in r:
                    st.success(r)
                    st.balloons()
                else:
                    st.error(r)
    with col2:
        if st.button("🔌 Probar Groq", use_container_width=True):
            with st.spinner("Probando modelos de Groq..."):
                r = call_groq()
                if "✅" in r:
                    st.success(r)
                    st.balloons()
                else:
                    st.error(r)
    
    st.markdown("---")
    st.info("El sistema probará múltiples modelos automáticamente hasta encontrar uno que funcione")

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
