import streamlit as st
import requests
import time
import itertools

st.set_page_config(page_title="SG-SST PHVA", layout="wide")

st.markdown("""
<style>
.stApp { background: linear-gradient(135deg, #0f0c29, #302b63, #24243e); }
.main-header { background: linear-gradient(135deg, #667eea, #764ba2); padding: 20px; border-radius: 15px; }
</style>
""", unsafe_allow_html=True)

# ========== CONFIGURACIÓN DE MÚLTIPLES KEYS ==========

def get_all_gemini_keys():
    """Obtener todas las keys de Gemini desde secrets"""
    keys = []
    for i in range(1, 10):
        key = st.secrets.get(f"GEMINI_API_KEY_{i}")
        if key and key != "":
            keys.append(key)
    if not keys:
        key = st.secrets.get("GEMINI_API_KEY")
        if key and key != "":
            keys.append(key)
    return keys

def get_groq_key():
    return st.secrets.get("GROQ_API_KEY")

# Obtener todas las keys
GEMINI_KEYS = get_all_gemini_keys()
GROQ_KEY = get_groq_key()

# Crear ciclo rotador para Gemini
gemini_cycle = itertools.cycle(GEMINI_KEYS) if GEMINI_KEYS else None

def call_gemini_with_retry(prompt, max_attempts=10):
    """Llamar a Gemini con rotación de keys"""
    if not GEMINI_KEYS:
        return None, "No hay Gemini keys configuradas"
    
    url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-flash-latest:generateContent"
    data = {"contents": [{"parts": [{"text": prompt}]}]}
    
    for intento in range(max_attempts):
        key = next(gemini_cycle)
        
        try:
            headers = {"Content-Type": "application/json", "X-goog-api-key": key}
            r = requests.post(url, json=data, headers=headers, timeout=30)
            
            if r.status_code == 200:
                texto = r.json()["candidates"][0]["content"]["parts"][0]["text"]
                return texto, None
            elif r.status_code == 503:
                time.sleep(0.5)
                continue
            elif r.status_code == 429:
                time.sleep(0.5)
                continue
        except:
            continue
    
    return None, "Todas las keys de Gemini están ocupadas. Intenta de nuevo."

def call_groq_with_retry(prompt):
    """Llamar a Groq con modelos correctos"""
    if not GROQ_KEY:
        return None, "No hay Groq key configurada"
    
    # Modelos actualmente activos en Groq
    modelos = ["llama-3.3-70b-versatile", "llama-3.1-70b-versatile", "mixtral-8x7b-32768"]
    
    for modelo in modelos:
        try:
            url = "https://api.groq.com/openai/v1/chat/completions"
            headers = {"Authorization": f"Bearer {GROQ_KEY}", "Content-Type": "application/json"}
            data = {"model": modelo, "messages": [{"role": "user", "content": prompt}], "temperature": 0.7}
            
            r = requests.post(url, json=data, headers=headers, timeout=30)
            
            if r.status_code == 200:
                texto = r.json()["choices"][0]["message"]["content"]
                return texto, None
            elif r.status_code == 400:
                continue  # Probar siguiente modelo
            else:
                continue
        except:
            continue
    
    return None, "No se pudo conectar con Groq"

def call_best_ia(prompt):
    """Intentar Gemini primero, luego Groq"""
    # Primero Gemini
    resultado, error = call_gemini_with_retry(prompt, max_attempts=6)
    if resultado:
        return resultado
    
    # Si Gemini falla, intentar Groq
    resultado, error = call_groq_with_retry(prompt)
    if resultado:
        return resultado
    
    return "⚠️ Todos los servicios de IA están ocupados. Por favor, intenta de nuevo en unos momentos."

# ========== FUNCIONES PARA PRUEBAS ==========

def test_gemini():
    resultado, error = call_gemini_with_retry("Responde solo: OK", max_attempts=6)
    if resultado:
        return f"✅ Gemini OK: {resultado}"
    else:
        return f"❌ Gemini: {error}"

def test_groq():
    resultado, error = call_groq_with_retry("Responde solo: OK")
    if resultado:
        return f"✅ Groq OK: {resultado}"
    else:
        return f"❌ Groq: {error}"

def chat_ia(pregunta):
    return call_best_ia(f"Eres un experto en Seguridad y Salud en el Trabajo (SST) en Colombia. Responde de forma clara y profesional: {pregunta}")

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
    
    # Estado de las keys
    st.subheader("📊 Estado de API Keys")
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Gemini Keys", len(GEMINI_KEYS))
        for i, key in enumerate(GEMINI_KEYS):
            st.caption(f"Key {i+1}: {key[:20]}...")
    with col2:
        st.metric("Groq Key", "✅ Configurada" if GROQ_KEY else "❌ No configurada")
        if GROQ_KEY:
            st.caption(f"Key: {GROQ_KEY[:20]}...")
    
    st.markdown("---")
    st.subheader("🤖 Prueba de Conexión")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🔌 Probar Gemini (rotación)", use_container_width=True):
            with st.spinner(f"Probando {len(GEMINI_KEYS)} keys..."):
                r = test_gemini()
                if "✅" in r:
                    st.success(r)
                    st.balloons()
                else:
                    st.error(r)
    
    with col2:
        if st.button("🔌 Probar Groq", use_container_width=True):
            with st.spinner("Probando modelos de Groq..."):
                r = test_groq()
                if "✅" in r:
                    st.success(r)
                    st.balloons()
                else:
                    st.error(r)
    
    st.markdown("---")
    st.info("💡 Gemini probará todas tus keys en rotación. Groq probará múltiples modelos.")

elif menu == "Chat IA":
    st.markdown('<div class="main-header"><h1>Chat IA</h1></div>', unsafe_allow_html=True)
    
    if "msgs" not in st.session_state:
        st.session_state.msgs = [{"role": "assistant", "content": f"Hola, soy tu asistente SST. Uso {len(GEMINI_KEYS)} keys de Gemini y Groq como respaldo. ¿En qué puedo ayudarte?"}]
    
    for m in st.session_state.msgs:
        with st.chat_message(m["role"]):
            st.write(m["content"])
    
    if p := st.chat_input("Pregunta sobre SST..."):
        st.session_state.msgs.append({"role": "user", "content": p})
        with st.chat_message("assistant"):
            with st.spinner("Consultando IA (Gemini + Groq)..."):
                r = chat_ia(p)
                st.write(r)
                st.session_state.msgs.append({"role": "assistant", "content": r})

st.markdown("---")
st.markdown("<p style='text-align:center'>SG-SST PHVA | JAN BENITEZ</p>", unsafe_allow_html=True)
