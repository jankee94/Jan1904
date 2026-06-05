# actualizar_login.py
import re

# Leer el archivo main.py
with open("main.py", "r", encoding="utf-8") as f:
    contenido = f.read()

# Buscar la sección de login y reemplazarla
patron_login = r'if not st\.session_state\.auth:.*?(?=st\.markdown\(\'<div class="developer-footer")'
nuevo_login = '''if not st.session_state.auth:
    col1, col2, col3 = st.columns([1, 1.5, 1])
    with col2:
        st.markdown("""
        <div class="login-card" style="padding: 20px 15px; margin: 10px 0;">
            <div style="text-align: center; margin-bottom: 8px;">
                <img src="https://cdn-icons-png.flaticon.com/512/2917/2917995.png" style="width: 45px;">
                <h1 style="font-size: 20px; margin: 5px 0; background: linear-gradient(135deg, #fff 0%, #a8c0ff 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">SG-SST PHVA</h1>
                <div style="font-size: 11px; color: rgba(255,255,255,0.7);">"Seguridad y Salud, compromiso de todos"</div>
                <div style="font-size: 9px; color: rgba(255,255,255,0.5);">Sistema de Gestión PHVA con IA</div>
            </div>
        """, unsafe_allow_html=True)
        
        with st.form("login_form"):
            username = st.text_input("👤 USUARIO", placeholder="Ingrese su usuario", label_visibility="collapsed")
            password = st.text_input("🔒 CONTRASEÑA", type="password", placeholder="Ingrese su contraseña", label_visibility="collapsed")
            
            col1, col2 = st.columns(2)
            with col1:
                submitted = st.form_submit_button("🚀 INGRESAR", use_container_width=True)
            with col2:
                forgot = st.form_submit_button("❓ OLVIDÓ SU CLAVE", use_container_width=True)
            
            if submitted:
                user = verificar_login(username, password)
                if user:
                    st.session_state.auth = True
                    st.session_state.user = user
                    st.rerun()
                else:
                    st.error("❌ Usuario o contraseña incorrectos")
            
            if forgot:
                st.info("📧 Contacte al administrador: admin@sgsst.com")
        
        st.markdown("""
            <div style="text-align: center; margin-top: 10px;">
                <p style="color: rgba(255,255,255,0.4); font-size: 8px;">© 2024 SG-SST PHVA</p>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown('<div class="developer-footer">🔄 SG-SST PHVA | DESARROLLADO POR JAN BENITEZ | "Prevenir es vivir"</div>', unsafe_allow_html=True)
    st.stop()'''

# Reemplazar (versión simplificada - buscar manualmente)
print("✅ Abre main.py y busca 'if not st.session_state.auth:'")
print("📝 Reemplaza manualmente hasta 'st.stop()' con el código de arriba")
print("")
print("O usa este comando para hacer backup:")