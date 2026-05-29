import streamlit as st
import requests
import json
import os

st.set_page_config(page_title="SG-SST PHVA", page_icon="🛡️", layout="wide")

# Leer secrets desde Streamlit Cloud o variables de entorno
try:
    GEMINI_API_KEY = st.secrets.get("GEMINI_API_KEY") or os.environ.get("GEMINI_API_KEY")
    GROQ_API_KEY = st.secrets.get("GROQ_API_KEY") or os.environ.get("GROQ_API_KEY")
except:
    GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
    GROQ_API_KEY = os.environ.get("GROQ_API_KEY")

if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

st.markdown("""
<style>
.main-header { background: linear-gradient(135deg, #1e3c72 0%, #2b5876 100%); padding: 1rem; border-radius: 10px; color: white; text-align: center; margin-bottom: 2rem; }
.metric-card { background: linear-gradient(135deg, #1e3c72 0%, #2b5876 100%); padding: 1rem; border-radius: 10px; color: white; text-align: center; }
</style>
""", unsafe_allow_html=True)

def call_gemini(prompt):
    if not GEMINI_API_KEY:
        return "❌ GEMINI_API_KEY no configurada", "❌"
    url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-flash-latest:generateContent"
    headers = {"Content-Type": "application/json", "X-goog-api-key": GEMINI_API_KEY}
    data = {"contents": [{"parts": [{"text": f"Eres experto en SST. Responde: {prompt}"}]}]}
    try:
        r = requests.post(url, headers=headers, json=data, timeout=30)
        if r.status_code == 200:
            return r.json()["candidates"][0]["content"]["parts"][0]["text"], "✅"
        return f"Error Gemini: {r.status_code}", "❌"
    except Exception as e:
        return f"Error: {e}", "❌"

def login():
    st.markdown('<div class="main-header"><h1>🛡️ SG-SST PHVA</h1><p>Planificar · Hacer · Verificar · Actuar</p></div>', unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        usuario = st.text_input("Usuario")
        password = st.text_input("Contraseña", type="password")
        if st.button("Ingresar", use_container_width=True):
            if usuario == "admin" and password == "sst2024":
                st.session_state.authenticated = True
                st.rerun()
            else:
                st.error("❌ Credenciales incorrectas")

def dashboard():
    st.markdown('<div class="main-header"><h1>📊 Dashboard SG-SST</h1><p>Panel de Control</p></div>', unsafe_allow_html=True)
    
    col1, col2, col3, col4 = st.columns(4)
    with col1: st.markdown('<div class="metric-card"><h3>👥</h3><h2>24</h2><p>Trabajadores</p></div>', unsafe_allow_html=True)
    with col2: st.markdown('<div class="metric-card"><h3>⚠️</h3><h2>8</h2><p>Peligros</p></div>', unsafe_allow_html=True)
    with col3: st.markdown('<div class="metric-card"><h3>📊</h3><h2>92%</h2><p>Cumplimiento</p></div>', unsafe_allow_html=True)
    with col4: st.markdown('<div class="metric-card"><h3>✅</h3><h2>9/18</h2><p>Módulos</p></div>', unsafe_allow_html=True)
    
    st.markdown("---")
    st.markdown("### 📡 Estado de las IA")
    col1, col2 = st.columns(2)
    with col1: st.success("✅ Gemini: Conectado" if GEMINI_API_KEY else "❌ Gemini: No configurada")
    with col2: st.success("✅ Groq: Conectado" if GROQ_API_KEY else "❌ Groq: No configurada")
    
    st.markdown("---")
    st.subheader("🤖 Asistente IA de SST")
    user_input = st.text_input("Escribe tu pregunta:")
    if st.button("Enviar") and user_input:
        with st.spinner("Consultando..."):
            respuesta, estado = call_gemini(user_input)
            if estado == "✅":
                st.success(f"**Respuesta:** {respuesta}")
            else:
                st.error(respuesta)
    
    st.markdown("---")
    st.markdown("<p style='text-align:center'>Desarrollado por: Ing. Jan Benitez & Ing. Neiris Pallares</p>", unsafe_allow_html=True)

if st.session_state.authenticated:
    dashboard()
else:
    login()
