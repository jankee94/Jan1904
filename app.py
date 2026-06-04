import streamlit as st
import requests
import itertools

st.set_page_config(page_title="SG-SST PHVA", page_icon="🔄", layout="wide")

if "auth" not in st.session_state:
    st.session_state.auth = False
if "emp" not in st.session_state:
    st.session_state.emp = {}

# ============================================================
# CARGA DE MÚLTIPLES KEYS DE GEMINI
# ============================================================
def get_gemini_keys():
    keys = []
    i = 1
    while True:
        key = st.secrets.get(f"GEMINI_API_KEY_{i}")
        if not key:
            break
        keys.append(key)
        i += 1
    if not keys:
        old_key = st.secrets.get("GEMINI_API_KEY")
        if old_key:
            keys.append(old_key)
    return keys

def get_groq_key():
    return st.secrets.get("GROQ_API_KEY")

GEMINI_KEYS = get_gemini_keys()
GROQ_KEY = get_groq_key()

# Rotador circular para Gemini
gemini_cycle = itertools.cycle(GEMINI_KEYS) if GEMINI_KEYS else None

# ============================================================
# LLAMADAS A CADA IA
# ============================================================
def call_gemini(prompt):
    """Intenta con todas las keys de Gemini hasta que una responda"""
    if not GEMINI_KEYS:
        return None
    for _ in range(len(GEMINI_KEYS)):
        key = next(gemini_cycle)
        try:
            url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-flash-latest:generateContent"
            headers = {"Content-Type": "application/json", "X-goog-api-key": key}
            data = {"contents": [{"parts": [{"text": prompt}]}]}
            r = requests.post(url, json=data, headers=headers, timeout=30)
            if r.status_code == 200:
                return r.json()["candidates"][0]["content"]["parts"][0]["text"]
            elif r.status_code == 429:
                continue
            else:
                continue
        except:
            continue
    return None

def call_groq(prompt):
    """Llama a Groq con llama-3.3-70b-versatile"""
    if not GROQ_KEY:
        return None
    try:
        url = "https://api.groq.com/openai/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {GROQ_KEY}",
            "Content-Type": "application/json"
        }
        data = {
            "model": "llama-3.3-70b-versatile",
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.7
        }
        r = requests.post(url, json=data, headers=headers, timeout=30)
        if r.status_code == 200:
            return r.json()["choices"][0]["message"]["content"]
        return None
    except:
        return None

def call_best_ia(prompt):
    """Intenta Gemini primero, si falla usa Groq"""
    respuesta = call_gemini(prompt)
    if respuesta:
        return f"🤖 **Gemini:** {respuesta}"
    respuesta = call_groq(prompt)
    if respuesta:
        return f"🟢 **Groq:** {respuesta}"
    return None

# ============================================================
# LOGIN Y UI
# ============================================================
if not st.session_state.auth:
    st.title("SG-SST PHVA")
    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        u = st.text_input("Usuario")
        p = st.text_input("Contraseña", type="password")
        if st.button("Ingresar"):
            if u == "admin" and p == "sst2024":
                st.session_state.auth = True
                st.rerun()
            else:
                st.error("Use admin / sst2024")
else:
    with st.sidebar:
        st.image("https://cdn-icons-png.flaticon.com/512/2917/2917995.png", width=60)
        opcion = st.radio("Menú", ["Diagnóstico", "Chat", "Test IA"])
        if st.button("Salir"):
            st.session_state.auth = False
            st.rerun()
    
    if opcion == "Test IA":
        st.title("🔧 Test de IAs")
        st.write(f"**Gemini keys:** {len(GEMINI_KEYS)}")
        st.write(f"**Groq key:** {'✅ Configurada' if GROQ_KEY else '❌ No configurada'}")
        
        if st.button("Probar Gemini"):
            res = call_gemini("Responde solo: OK")
            if res:
                st.success(f"Gemini responde: {res}")
            else:
                st.error("Gemini no respondió")
        
        if st.button("Probar Groq"):
            res = call_groq("Responde solo: OK")
            if res:
                st.success(f"Groq responde: {res}")
            else:
                st.error("Groq no respondió")
        
        if st.button("Probar fallback (Gemini → Groq)"):
            res = call_best_ia("Responde solo: OK")
            if res:
                st.success(res)
            else:
                st.error("Ninguna IA respondió")
        
        st.info("""
        **Secrets configurados:**
        - GEMINI_API_KEY_1, GEMINI_API_KEY_2, ...
        - GROQ_API_KEY
        """)
    
    elif opcion == "Diagnóstico":
        st.title("Diagnóstico IA")
        with st.form("f"):
            nit = st.text_input("NIT")
            tra = st.number_input("Trabajadores", min_value=1, value=10)
            arl = st.selectbox("ARL", ["Positiva", "Sura", "Colpatria"])
            if st.form_submit_button("Generar diagnóstico"):
                with st.spinner("IA trabajando..."):
                    prompt = f"NIT:{nit} Trabajadores:{tra} ARL:{arl}. Genera diagnóstico SST completo."
                    res = call_best_ia(prompt)
                    if res:
                        st.markdown(res)
                    else:
                        st.error("No se pudo obtener respuesta de ninguna IA")
    
    else:  # Chat
        st.title("Chat IA")
        if "msgs" not in st.session_state:
            st.session_state.msgs = []
        for m in st.session_state.msgs:
            with st.chat_message(m["r"]):
                st.markdown(m["c"])
        p = st.chat_input("Pregunta:")
        if p:
            st.session_state.msgs.append({"r": "user", "c": p})
            with st.chat_message("user"):
                st.markdown(p)
            r = call_best_ia(p)
            if not r:
                r = "Lo siento, no pude procesar tu consulta. Verifica las API keys."
            with st.chat_message("assistant"):
                st.markdown(r)
            st.session_state.msgs.append({"r": "assistant", "c": r})
