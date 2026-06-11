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
    # Intentar obtener múltiples keys
    for i in range(1, 10):
        key = st.secrets.get(f"GEMINI_API_KEY_{i}")
        if key and key != "":
            keys.append(key)
    # Si no hay keys con sufijo, intentar con la key simple
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

# Estado de las keys
st.session_state.gemini_keys_count = len(GEMINI_KEYS)
st.session_state.current_key_index = 0

def call_gemini_with_retry(prompt, max_retries=3):
    """Llamar a Gemini con rotación de keys y reintentos"""
    if not GEMINI_KEYS:
        return None, "No hay Gemini keys configuradas"
    
    url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-flash-latest:generateContent"
    data = {
        "contents": [
            {
                "parts": [
                    {
                        "text": prompt
                    }
                ]
            }
        ]
    }
    
    # Probar cada key varias veces
    for intento in range(max_retries * len(GEMINI_KEYS)):
        key = next(gemini_cycle)
        
        try:
            headers = {
                "Content-Type": "application/json",
                "X-goog-api-key": key
            }
            r = requests.post(url, json=data, headers=headers, timeout=30)
            
            if r.status_code == 200:
                texto = r.json()["candidates"][0]["content"]["parts"][0]["text"]
                return texto, None
            elif r.status_code == 503:
                # Servicio ocupado, probar siguiente key
                time.sleep(1)
                continue
            elif r.status_code == 429:
                # Rate limit, probar siguiente key
                time.sleep(1)
                continue
            else:
                continue
        except Exception as e:
            continue
    
    return None, "Todas las keys de Gemini están ocupadas o no disponibles. Intenta de nuevo en unos momentos."

def call_gemini_test():
    """Función para pruebas en Dashboard"""
    resultado, error = call_gemini_with_retry("Responde solo: OK", max_retries=2)
    if resultado:
        return f"✅ Gemini: {resultado}"
    else:
        return f"❌ {error}"

def call_groq():
    try:
        if not GROQ_KEY:
            return "No hay Groq key configurada"
        
        url = "https://api.groq.com/openai/v1/chat/completions"
        headers = {"Authorization": f"Bearer {GROQ_KEY}", "Content-Type": "application/json"}
        data = {"model": "llama3-70b-8192", "messages": [{"role": "user", "content": "Responde solo: OK"}], "temperature": 0.7}
        
        r = requests.post(url, json=data, headers=headers, timeout=30)
        
        if r.status_code == 200:
            texto = r.json()["choices"][0]["message"]["content"]
            return f"✅ Groq: {texto}"
        else:
            return f"❌ Error {r.status_code}"
    except Exception as e:
        return f"❌ Error: {e}"

def chat_gemini(pregunta):
    """Chat con rotación de keys"""
    resultado, error = call_gemini_with_retry(
        f"Eres un experto en Seguridad y Salud en el Trabajo (SST) en Colombia. Responde de forma clara y profesional: {pregunta}",
        max_retries=3
    )
    if resultado:
        return resultado
    else:
        return f"⚠️ {error}"

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
    
    # Mostrar estado de las keys
    st.subheader("📊 Estado de API Keys")
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Gemini Keys", len(GEMINI_KEYS))
        for i, key in enumerate(GEMINI_KEYS):
            st.caption(f"Key {i+1}: {key[:15]}...{key[-5:]}")
    with col2:
        st.metric("Groq Key", "✅ Configurada" if GROQ_KEY else "❌ No configurada")
        if GROQ_KEY:
            st.caption(f"Key: {GROQ_KEY[:15]}...{GROQ_KEY[-5:]}")
    
    st.markdown("---")
    st.subheader("🤖 Prueba de Conexión")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🔌 Probar Gemini (con rotación)", use_container_width=True):
            with st.spinner(f"Probando {len(GEMINI_KEYS)} keys de Gemini..."):
                r = call_gemini_test()
                if "✅" in r:
                    st.success(r)
                    st.balloons()
                else:
                    st.error(r)
                    st.info("El sistema probará automáticamente las 3 keys")
    
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
    st.info(f"⚙️ Configuración actual: {len(GEMINI_KEYS)} keys de Gemini en rotación | Groq como respaldo")

elif menu == "Chat IA":
    st.markdown('<div class="main-header"><h1>Chat IA</h1></div>', unsafe_allow_html=True)
    
    if "msgs" not in st.session_state:
        st.session_state.msgs = [{"role": "assistant", "content": f"Hola, soy tu asistente SST. Estoy usando {len(GEMINI_KEYS)} keys de Gemini en rotación. ¿En qué puedo ayudarte?"}]
    
    for m in st.session_state.msgs:
        with st.chat_message(m["role"]):
            st.write(m["content"])
    
    if p := st.chat_input("Pregunta sobre SST..."):
        st.session_state.msgs.append({"role": "user", "content": p})
        with st.chat_message("assistant"):
            with st.spinner(f"Consultando {len(GEMINI_KEYS)} keys de Gemini..."):
                r = chat_gemini(p)
                st.write(r)
                st.session_state.msgs.append({"role": "assistant", "content": r})

st.markdown("---")
st.markdown("<p style='text-align:center'>SG-SST PHVA | JAN BENITEZ</p>", unsafe_allow_html=True)
