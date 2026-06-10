import streamlit as st
import requests
import itertools

st.set_page_config(page_title="SG-SST PHVA", page_icon="🔄", layout="wide")

# CSS
st.markdown('''
<style>
    .stApp { background: linear-gradient(135deg, #0f0c29 0%, #302b63 50%, #24243e 100%); }
    header[data-testid="stHeader"] { display: none; }
    footer { display: none !important; }
    .main-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 20px;
        border-radius: 15px;
        margin-bottom: 20px;
    }
    .main-header h1 { color: white; margin: 0; font-size: 1.8rem; }
    .metric-card {
        background: rgba(255,255,255,0.15);
        border-radius: 12px;
        padding: 15px;
        text-align: center;
    }
    .metric-value { font-size: 2rem; font-weight: bold; color: #667eea; }
    .metric-label { font-size: 0.8rem; color: rgba(255,255,255,0.7); }
</style>
''', unsafe_allow_html=True)

# ========== CONFIGURACIÓN DE IA ==========
def get_gemini_keys():
    keys = []
    for i in range(1, 10):
        try:
            key = st.secrets.get(f"GEMINI_API_KEY_{i}")
            if key and key != "":
                keys.append(key)
        except:
            pass
    if not keys:
        try:
            key = st.secrets.get("GEMINI_API_KEY")
            if key and key != "":
                keys.append(key)
        except:
            pass
    return keys

def get_groq_key():
    try:
        key = st.secrets.get("GROQ_API_KEY")
        if key and key != "":
            return key
    except:
        pass
    return None

GEMINI_KEYS = get_gemini_keys()
GROQ_KEY = get_groq_key()
gemini_cycle = itertools.cycle(GEMINI_KEYS) if GEMINI_KEYS else None

def call_gemini(prompt):
    if not GEMINI_KEYS:
        return None
    for _ in range(len(GEMINI_KEYS)):
        key = next(gemini_cycle)
        try:
            url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent"
            headers = {"Content-Type": "application/json", "x-goog-api-key": key}
            data = {"contents": [{"parts": [{"text": prompt}]}]}
            r = requests.post(url, json=data, headers=headers, timeout=30)
            if r.status_code == 200:
                return r.json()["candidates"][0]["content"]["parts"][0]["text"]
        except:
            continue
    return None

def call_groq(prompt):
    if not GROQ_KEY:
        return None
    try:
        url = "https://api.groq.com/openai/v1/chat/completions"
        headers = {"Authorization": f"Bearer {GROQ_KEY}", "Content-Type": "application/json"}
        data = {"model": "llama-3.3-70b-versatile", "messages": [{"role": "user", "content": prompt}], "temperature": 0.7}
        r = requests.post(url, json=data, headers=headers, timeout=30)
        if r.status_code == 200:
            return r.json()["choices"][0]["message"]["content"]
    except:
        pass
    return None

def call_best_ia(prompt):
    res = call_gemini(prompt)
    if res:
        return res
    res = call_groq(prompt)
    if res:
        return res
    return None

# ========== LOGIN ==========
if "auth" not in st.session_state:
    st.session_state.auth = False

if not st.session_state.auth:
    col1, col2, col3 = st.columns([1, 1.5, 1])
    with col2:
        st.markdown('''
        <div style="background: rgba(20,20,40,0.8); backdrop-filter: blur(14px); border-radius: 28px; padding: 40px; text-align:center">
            <img src="https://cdn-icons-png.flaticon.com/512/2917/2917995.png" width="70">
            <h1 style="color:white;">SG-SST PHVA</h1>
            <p style="color:rgba(255,255,255,0.6)">Sistema de Gestión en Seguridad y Salud en el Trabajo</p>
        </div>
        ''', unsafe_allow_html=True)
        
        with st.form("login_form"):
            username = st.text_input("Usuario", placeholder="admin")
            password = st.text_input("Contraseña", type="password", placeholder="admin123")
            if st.form_submit_button("INGRESAR", use_container_width=True):
                if username == "admin" and password == "admin123":
                    st.session_state.auth = True
                    st.rerun()
                else:
                    st.error("Usuario o contraseña incorrectos")
        
        st.markdown('<p style="text-align:center; font-size:11px; color:gray">SG-SST PHVA | JAN BENITEZ</p>', unsafe_allow_html=True)
    st.stop()

# ========== SIDEBAR ==========
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/2917/2917995.png", width=50)
    st.markdown("### Administrador")
    st.markdown("---")
    
    menu = st.radio("MÓDULOS", [
        "Dashboard",
        "Chat IA"
    ])
    
    if st.button("Cerrar Sesión", use_container_width=True):
        st.session_state.auth = False
        st.rerun()

# ========== DASHBOARD ==========
if menu == "Dashboard":
    st.markdown('<div class="main-header"><h1>📊 Dashboard SST</h1><p>Resumen ejecutivo del sistema</p></div>', unsafe_allow_html=True)
    
    # KPIs
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown('<div class="metric-card"><div class="metric-value">4</div><div class="metric-label">Peligros</div></div>', unsafe_allow_html=True)
    with col2:
        st.markdown('<div class="metric-card"><div class="metric-value">3</div><div class="metric-label">Acciones</div></div>', unsafe_allow_html=True)
    with col3:
        st.markdown('<div class="metric-card"><div class="metric-value">5</div><div class="metric-label">Trabajadores</div></div>', unsafe_allow_html=True)
    with col4:
        st.markdown('<div class="metric-card"><div class="metric-value">2</div><div class="metric-label">Incidentes</div></div>', unsafe_allow_html=True)
    
    st.markdown("---")
    
    # ========== PRUEBA DE IA - VISIBLE ==========
    st.subheader("🤖 PRUEBA DE CONEXIÓN IA")
    st.caption("Verifica que las API keys de Gemini y Groq estén funcionando correctamente")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🔌 PROBAR GEMINI", use_container_width=True, type="primary"):
            with st.spinner("Conectando con Gemini API..."):
                try:
                    resultado = call_gemini("Responde solo con la palabra: OK")
                    if resultado:
                        st.success(f"✅ Gemini responde: {resultado}")
                        st.balloons()
                    else:
                        st.error("❌ Gemini NO responde")
                        st.info("Verifica que GEMINI_API_KEY_1 esté configurada en Secrets")
                except Exception as e:
                    st.error(f"Error: {e}")
    
    with col2:
        if st.button("🔌 PROBAR GROQ", use_container_width=True, type="primary"):
            with st.spinner("Conectando con Groq API..."):
                try:
                    resultado = call_groq("Responde solo con la palabra: OK")
                    if resultado:
                        st.success(f"✅ Groq responde: {resultado}")
                        st.balloons()
                    else:
                        st.error("❌ Groq NO responde")
                        st.info("Verifica que GROQ_API_KEY esté configurada en Secrets")
                except Exception as e:
                    st.error(f"Error: {e}")
    
    st.markdown("---")
    
    # Estado de las keys
    with st.expander("📋 VER ESTADO DE API KEYS"):
        try:
            gemini_keys = get_gemini_keys()
            groq_key = get_groq_key()
            st.write(f"**Gemini keys encontradas:** {len(gemini_keys)}")
            st.write(f"**Groq key encontrada:** {'✅ Sí' if groq_key else '❌ No'}")
            
            if len(gemini_keys) == 0:
                st.warning("No hay Gemini keys configuradas")
                st.code("GEMINI_API_KEY_1 = 'tu_key_aqui'", language="toml")
            
            if not groq_key:
                st.warning("No hay Groq key configurada")
                st.code("GROQ_API_KEY = 'tu_key_aqui'", language="toml")
        except Exception as e:
            st.error(f"Error leyendo Secrets: {e}")

# ========== CHAT IA ==========
elif menu == "Chat IA":
    st.markdown('<div class="main-header"><h1>💬 Chat IA</h1><p>Asistente virtual especializado en SST</p></div>', unsafe_allow_html=True)
    
    if "messages" not in st.session_state:
        st.session_state.messages = [{"role": "assistant", "content": "Hola, soy tu asistente SST. ¿En qué puedo ayudarte?"}]
    
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.write(msg["content"])
    
    if prompt := st.chat_input("Escribe tu pregunta sobre SST..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.write(prompt)
        
        with st.chat_message("assistant"):
            with st.spinner("🤖 IA analizando tu consulta..."):
                respuesta = call_best_ia(prompt)
                if respuesta:
                    st.write(respuesta)
                    st.session_state.messages.append({"role": "assistant", "content": respuesta})
                else:
                    st.error("No se pudo obtener respuesta de la IA. Verifica las API keys en Secrets.")
                    st.info("Ve a Dashboard y prueba la conexión con Gemini y Groq")

st.markdown("---")
st.markdown("<p style='text-align:center; font-size:11px; color:gray'>SG-SST PHVA | Sistema de Gestión con IA | Desarrollado por JAN BENITEZ</p>", unsafe_allow_html=True)
