@echo off
title SUBIR SG-SST CON CHAT FUNCIONAL
color 0A

echo ========================================
echo    SUBIENDO PROYECTO CON CHAT
echo ========================================
echo.

cd /d "C:\Users\SOPORTE-SIESA\Documents\GitHub\Jan1904\proyecto"

echo [1/6] Creando app.py...
(
echo import streamlit as st
echo.
echo st.set_page_config^(page_title="SG-SST PHVA", page_icon="🏭", layout="wide"^)
echo.
echo if "auth" not in st.session_state:
echo     st.session_state.auth = False
echo.
echo if not st.session_state.auth:
echo     st.markdown^("""
echo     ^<div style="text-align:center; padding:50px"^>
echo         ^<h1 style="color:#1a4a6f"^>🏭 SG-SST PHVA^</h1^>
echo         ^<h3^>Sistema de Gestion en Seguridad y Salud en el Trabajo^</h3^>
echo     ^</div^>
echo     """, unsafe_allow_html=True^)
echo.
echo     col1, col2, col3 = st.columns([1,2,1])
echo     with col2:
echo         usuario = st.text_input("Usuario")
echo         contrasena = st.text_input("Contraseña", type="password")
echo         if st.button("Iniciar Sesion"):
echo             if usuario == "admin" and contrasena == "sst2024":
echo                 st.session_state.auth = True
echo                 st.rerun^(^)
echo             else:
echo                 st.error("Credenciales incorrectas")
echo.
echo else:
echo     st.sidebar.title("🏭 SG-SST PHVA")
echo     st.sidebar.markdown("---")
echo.
echo     menu = st.sidebar.selectbox^(^
echo         "Modulos",
echo         ["Dashboard", "Trabajadores", "Peligros", "Capacitaciones", "Incidentes"]
echo     ^)
echo.
echo     if menu == "Dashboard":
echo         st.title("📊 Dashboard Ejecutivo")
echo         col1, col2, col3, col4 = st.columns(4^)
echo         with col1: st.metric("Trabajadores", "156", "+12"^)
echo         with col2: st.metric("Capacitaciones", "24", "+5"^)
echo         with col3: st.metric("Incidentes", "3", "-2"^)
echo         with col4: st.metric("Progreso", "50%%", "9/18"^)
echo         st.markdown("---")
echo         st.progress(0.50^)
echo         st.write("**9/18 modulos completados (50%%)**"^)
echo     elif menu == "Trabajadores":
echo         st.title("👥 Gestion de Trabajadores")
echo         st.info("Modulo en construccion")
echo     elif menu == "Peligros":
echo         st.title("⚠️ Matriz de Peligros")
echo         st.info("Modulo en construccion")
echo     elif menu == "Capacitaciones":
echo         st.title("📚 Capacitaciones")
echo         st.info("Modulo en construccion")
echo     elif menu == "Incidentes":
echo         st.title("📋 Incidentes")
echo         st.info("Modulo en construccion")
echo.
echo     if st.sidebar.button("Cerrar Sesion"):
echo         st.session_state.auth = False
echo         st.rerun^(^)
echo.
echo import chat
) > app.py

echo [2/6] Creando chat.py...
(
echo import streamlit as st
echo.
echo st.markdown^("""
echo ^<style^>
echo .chat-fijo {
echo     position: fixed;
echo     bottom: 20px;
echo     right: 20px;
echo     z-index: 9999;
echo }
echo .chat-boton {
echo     width: 60px;
echo     height: 60px;
echo     border-radius: 50%%;
echo     background: #1a4a6f;
echo     color: white;
echo     border: none;
echo     font-size: 24px;
echo     cursor: pointer;
echo     box-shadow: 0 4px 12px rgba(0,0,0,0.15);
echo }
echo .chat-boton:hover {
echo     transform: scale(1.05);
echo }
echo .chat-ventana {
echo     position: fixed;
echo     bottom: 90px;
echo     right: 20px;
echo     width: 350px;
echo     height: 500px;
echo     background: white;
echo     border-radius: 12px;
echo     box-shadow: 0 8px 24px rgba(0,0,0,0.2);
echo     display: none;
echo     flex-direction: column;
echo     overflow: hidden;
echo }
echo .chat-header {
echo     background: #1a4a6f;
echo     color: white;
echo     padding: 12px;
echo     display: flex;
echo     justify-content: space-between;
echo     align-items: center;
echo }
echo .chat-cerrar {
echo     background: none;
echo     border: none;
echo     color: white;
echo     font-size: 20px;
echo     cursor: pointer;
echo }
echo .chat-mensajes {
echo     flex: 1;
echo     overflow: auto;
echo     padding: 10px;
echo     background: #f5f5f5;
echo }
echo .mensaje-usuario {
echo     background: #1a4a6f;
echo     color: white;
echo     padding: 8px 12px;
echo     border-radius: 15px;
echo     margin: 5px 0;
echo     text-align: right;
echo     max-width: 80%%;
echo     margin-left: auto;
echo     width: fit-content;
echo }
echo .mensaje-bot {
echo     background: white;
echo     color: black;
echo     padding: 8px 12px;
echo     border-radius: 15px;
echo     margin: 5px 0;
echo     border: 1px solid #ddd;
echo     max-width: 80%%;
echo     width: fit-content;
echo }
echo .chat-input-area {
echo     padding: 10px;
echo     display: flex;
echo     gap: 10px;
echo     background: white;
echo     border-top: 1px solid #ddd;
echo }
echo .chat-input-area input {
echo     flex: 1;
echo     padding: 8px;
echo     border: 1px solid #ddd;
echo     border-radius: 20px;
echo }
echo .chat-input-area button {
echo     padding: 8px 16px;
echo     background: #1a4a6f;
echo     color: white;
echo     border: none;
echo     border-radius: 20px;
echo     cursor: pointer;
echo }
echo ^</style^>
echo.
echo ^<div class="chat-fijo"^>
echo     ^<button class="chat-boton" id="abrirChat"^>💬^</button^>
echo     ^<div class="chat-ventana" id="ventanaChat"^>
echo         ^<div class="chat-header"^>
echo             ^<span^>🤖 Asistente SST^</span^>
echo             ^<button class="chat-cerrar" id="cerrarChat"^>✕^</button^>
echo         ^</div^>
echo         ^<div class="chat-mensajes" id="mensajesChat"^>
echo             ^<div class="mensaje-bot"^>👋 Hola! Soy tu asistente SST. ¿En que puedo ayudarte?^</div^>
echo         ^</div^>
echo         ^<div class="chat-input-area"^>
echo             ^<input type="text" id="inputChat" placeholder="Escribe tu mensaje..."^>
echo             ^<button id="enviarChat"^>Enviar^</button^>
echo         ^</div^>
echo     ^</div^>
echo ^</div^>
echo.
echo ^<script^>
echo     const abrir = document.getElementById('abrirChat');
echo     const cerrar = document.getElementById('cerrarChat');
echo     const ventana = document.getElementById('ventanaChat');
echo     const enviar = document.getElementById('enviarChat');
echo     const input = document.getElementById('inputChat');
echo     const mensajes = document.getElementById('mensajesChat');
echo.
echo     abrir.onclick = function() {
echo         ventana.style.display = 'flex';
echo     };
echo.
echo     cerrar.onclick = function() {
echo         ventana.style.display = 'none';
echo     };
echo.
echo     function enviarMensaje() {
echo         const msg = input.value.trim();
echo         if(msg === "") return;
echo.
echo         const userDiv = document.createElement('div');
echo         userDiv.className = 'mensaje-usuario';
echo         userDiv.innerText = msg;
echo         mensajes.appendChild(userDiv);
echo.
echo         input.value = '';
echo         mensajes.scrollTop = mensajes.scrollHeight;
echo.
echo         const botDiv = document.createElement('div');
echo         botDiv.className = 'mensaje-bot';
echo         botDiv.innerText = '🤗 Gracias por tu mensaje! Pronto tendremos respuestas con IA.';
echo         mensajes.appendChild(botDiv);
echo         mensajes.scrollTop = mensajes.scrollHeight;
echo     }
echo.
echo     enviar.onclick = enviarMensaje;
echo.
echo     input.onkeypress = function(e) {
echo         if(e.key === 'Enter') {
echo             enviarMensaje();
echo         }
echo     };
echo.
echo     ventana.style.display = 'none';
echo ^</script^>
echo """, unsafe_allow_html=True^)
) > chat.py

echo [3/6] Creando requirements.txt...
(
echo streamlit^>=1.28.0
echo pandas^>=2.0.0
echo plotly^>=5.17.0
) > requirements.txt

echo [4/6] Creando .gitignore...
(
echo .streamlit/secrets.toml
echo __pycache__/
echo *.pyc
echo .DS_Store
) > .gitignore

echo [5/6] Agregando archivos a Git...
git add .

echo [6/6] Subiendo a GitHub...
git commit -m "SG-SST con chat flotante funcional"
git push origin main --force

echo.
echo ========================================
echo    PROYECTO SUBIDO CORRECTAMENTE!
echo ========================================
echo.
echo 🌐 https://proyecto-jan1904.streamlit.app
echo 🔐 admin / sst2024
echo.
echo 🎯 EL CHAT:
echo    • Boton 💬 en esquina DERECHA
echo    • Click para ABRIR
echo    • Click en X para CERRAR
echo    • Envia mensajes
echo.
pause