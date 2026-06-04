import streamlit as st
import requests
import json
from typing import Optional

st.set_page_config(page_title="SG-SST PHVA", page_icon="🔄", layout="wide")

# Inicializar session state
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
if "empresa" not in st.session_state:
    st.session_state.empresa = {}
if "chat_messages" not in st.session_state:
    st.session_state.chat_messages = []

def get_gemini_key():
    try:
        return st.secrets.get("GEMINI_API_KEY")
    except:
        import os
        return os.environ.get("GEMINI_API_KEY")

def call_gemini(prompt: str) -> Optional[str]:
    api_key = get_gemini_key()
    if not api_key:
        return None
    
    try:
        url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent"
        headers = {
            "Content-Type": "application/json",
            "X-goog-api-key": api_key
        }
        payload = {
            "contents": [{
                "parts": [{"text": prompt}]
            }]
        }
        response = requests.post(url, json=payload, headers=headers, timeout=30)
        
        if response.status_code == 200:
            data = response.json()
            candidates = data.get("candidates", [])
            if candidates:
                content = candidates[0].get("content", {})
                parts = content.get("parts", [])
                if parts:
                    return parts[0].get("text", None)
        return None
    except Exception as e:
        st.session_state.ultimo_error = str(e)
        return None

def test_ia():
    """Probar conexion con Gemini"""
    api_key = get_gemini_key()
    if not api_key:
        return "❌ API Key no encontrada. Configura GEMINI_API_KEY en Secrets"
    
    try:
        url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent"
        headers = {"Content-Type": "application/json", "X-goog-api-key": api_key}
        payload = {"contents": [{"parts": [{"text": "Responde solo: OK"}]}]}
        response = requests.post(url, json=payload, headers=headers, timeout=10)
        
        if response.status_code == 200:
            return "✅ IA conectada correctamente"
        else:
            return f"❌ Error HTTP {response.status_code}: {response.text[:200]}"
    except Exception as e:
        return f"❌ Error de conexion: {str(e)}"

# Login
if not st.session_state.authenticated:
    st.markdown("""
    <div style="text-align: center; padding: 3rem;">
        <h1>🔄 SG-SST PHVA</h1>
        <h3>Sistema de Gestion SST con IA</h3>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        user = st.text_input("Usuario")
        pwd = st.text_input("Contraseña", type="password")
        if st.button("Ingresar", use_container_width=True):
            if user == "admin" and pwd == "sst2024":
                st.session_state.authenticated = True
                st.rerun()
            else:
                st.error("Use: admin / sst2024")
else:
    # Sidebar
    with st.sidebar:
        st.image("https://cdn-icons-png.flaticon.com/512/2917/2917995.png", width=60)
        st.markdown("### SG-SST PHVA")
        
        if st.session_state.empresa.get("nombre"):
            st.success(f"📌 {st.session_state.empresa.get('nombre')}")
        
        st.markdown("---")
        
        menu = st.radio(
            "Menu Principal",
            ["🏠 Dashboard", "🔍 Diagnostico IA", "🤖 Asistente IA", "⚠️ Peligros", "📋 Plan Anual", "🔧 Test IA"]
        )
        
        st.markdown("---")
        if st.button("🚪 Cerrar Sesion"):
            st.session_state.authenticated = False
            st.rerun()
    
    # Dashboard
    if menu == "🏠 Dashboard":
        st.markdown("# 📊 Dashboard SG-SST PHVA")
        
        if st.session_state.empresa.get("nombre"):
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Empresa", st.session_state.empresa.get("nombre", "N/A"))
            with col2:
                st.metric("NIT", st.session_state.empresa.get("nit", "N/A"))
            with col3:
                st.metric("Trabajadores", st.session_state.empresa.get("trabajadores", 0))
        else:
            st.info("🎯 Ve a 'Diagnostico IA' para comenzar")
    
    # Test IA
    elif menu == "🔧 Test IA":
        st.markdown("# 🔧 Prueba de conexion con IA")
        
        st.markdown("### Configuracion actual:")
        api_key = get_gemini_key()
        if api_key:
            st.success(f"✅ API Key encontrada: {api_key[:10]}...")
        else:
            st.error("❌ API Key NO encontrada")
        
        if st.button("🔄 Probar conexion con Gemini"):
            with st.spinner("Probando..."):
                resultado = test_ia()
                if "✅" in resultado:
                    st.success(resultado)
                else:
                    st.error(resultado)
        
        st.markdown("---")
        st.markdown("### Instrucciones para configurar API Key:")
        st.code("""
        En Streamlit Cloud:
        1. Ve a Settings → Secrets
        2. Agrega:
           GEMINI_API_KEY = "tu_api_key_aqui"
        3. Haz clic en Save
        4. Reboot la app
        """)
    
    # Diagnostico IA
    elif menu == "🔍 Diagnostico IA":
        st.markdown("""
        <div style="background: linear-gradient(135deg, #667eea, #764ba2); padding: 2rem; border-radius: 20px; margin-bottom: 2rem;">
            <h1 style="color: white; text-align: center;">🔍 Diagnostico con IA</h1>
        </div>
        """, unsafe_allow_html=True)
        
        # Mostrar estado de IA
        api_key = get_gemini_key()
        if not api_key:
            st.error("⚠️ API Key de Gemini no configurada. Ve a 'Test IA' para instrucciones.")
        
        with st.form("empresa_form"):
            col1, col2, col3 = st.columns(3)
            with col1:
                nit = st.text_input("📄 NIT *", value=st.session_state.empresa.get("nit", ""))
            with col2:
                trabajadores = st.number_input("👥 Trabajadores *", min_value=1, value=st.session_state.empresa.get("trabajadores", 10))
            with col3:
                arl = st.selectbox("🛡️ ARL", ["Positiva", "Sura", "Colpatria", "Bolivar"])
            
            submitted = st.form_submit_button("🚀 Generar Diagnostico con IA", use_container_width=True, type="primary")
        
        if submitted and nit.strip():
            with st.spinner("🧠 IA generando diagnostico personalizado..."):
                prompt = f"""
                Eres experto en SST para empresas colombianas.
                
                NIT: {nit}
                Trabajadores: {trabajadores}
                ARL: {arl}
                
                Genera un diagnostico SST REAL y ESPECIFICO para esta empresa.
                Incluye:
                1. Analisis de riesgos segun tamaño de empresa
                2. Normativa aplicable con articulos especificos
                3. Plan de accion con plazos en dias
                4. Presupuesto realista en COP
                5. Checklist de cumplimiento inmediato
                
                Responde en español, formato profesional.
                """
                
                respuesta = call_gemini(prompt)
                
                if respuesta:
                    diagnostico = f"🤖 **DIAGNOSTICO IA (Gemini)**\n\n{respuesta}"
                    st.session_state.empresa = {"nit": nit, "trabajadores": trabajadores, "arl": arl, "nombre": f"Empresa {nit[-4:]}"}
                else:
                    diagnostico = f"""
❌ **ERROR: No se pudo conectar con la IA**

**Diagnostico del problema:**
- API Key: {'Configurada' if api_key else 'NO configurada'}
- Error: {st.session_state.get('ultimo_error', 'Desconocido')}

**Solucion:**
1. Ve al menu '🔧 Test IA'
2. Verifica que la API Key este correcta
3. Configura GEMINI_API_KEY en Secrets de Streamlit Cloud

**Datos ingresados:**
- NIT: {nit}
- Trabajadores: {trabajadores}
- ARL: {arl}
"""
                
                st.session_state.diagnostico_actual = diagnostico
        
        if st.session_state.get("diagnostico_actual"):
            st.markdown("---")
            st.markdown("### 📋 RESULTADO")
            st.markdown(st.session_state.diagnostico_actual)
    
    # Asistente IA
    elif menu == "🤖 Asistente IA":
        st.markdown("# 🤖 Asistente IA")
        
        for msg in st.session_state.chat_messages:
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])
        
        if prompt := st.chat_input("Consulta..."):
            st.session_state.chat_messages.append({"role": "user", "content": prompt})
            with st.chat_message("user"):
                st.markdown(prompt)
            
            with st.spinner("IA pensando..."):
                respuesta = call_gemini(f"Eres experto SST. Responde: {prompt}")
                if not respuesta:
                    respuesta = "⚠️ IA no disponible. Verifica la conexion en 'Test IA'"
            
            with st.chat_message("assistant"):
                st.markdown(respuesta)
            st.session_state.chat_messages.append({"role": "assistant", "content": respuesta})
    
    else:
        st.info("Modulo en desarrollo")

st.markdown("---")
st.markdown("<p style='text-align: center; color: gray;'>SG-SST PHVA</p>", unsafe_allow_html=True)
