import streamlit as st

st.markdown("""
<style>
/* Chat flotante fijo */
.chat-fijo {
    position: fixed;
    bottom: 20px;
    right: 20px;
    z-index: 9999;
}
.chat-boton {
    width: 60px;
    height: 60px;
    border-radius: 50%;
    background: #1a4a6f;
    color: white;
    border: none;
    font-size: 24px;
    cursor: pointer;
    box-shadow: 0 4px 12px rgba(0,0,0,0.15);
}
.chat-boton:hover {
    transform: scale(1.05);
}
.chat-ventana {
    position: fixed;
    bottom: 90px;
    right: 20px;
    width: 350px;
    height: 500px;
    background: white;
    border-radius: 12px;
    box-shadow: 0 8px 24px rgba(0,0,0,0.2);
    display: none;
    flex-direction: column;
    overflow: hidden;
}
.chat-header {
    background: #1a4a6f;
    color: white;
    padding: 12px;
    display: flex;
    justify-content: space-between;
    align-items: center;
}
.chat-cerrar {
    background: none;
    border: none;
    color: white;
    font-size: 20px;
    cursor: pointer;
}
.chat-mensajes {
    flex: 1;
    overflow: auto;
    padding: 10px;
    background: #f5f5f5;
}
.mensaje-usuario {
    background: #1a4a6f;
    color: white;
    padding: 8px 12px;
    border-radius: 15px;
    margin: 5px 0;
    text-align: right;
    max-width: 80%;
    margin-left: auto;
    width: fit-content;
}
.mensaje-bot {
    background: white;
    color: black;
    padding: 8px 12px;
    border-radius: 15px;
    margin: 5px 0;
    border: 1px solid #ddd;
    max-width: 80%;
    width: fit-content;
}
.chat-input-area {
    padding: 10px;
    display: flex;
    gap: 10px;
    background: white;
    border-top: 1px solid #ddd;
}
.chat-input-area input {
    flex: 1;
    padding: 8px;
    border: 1px solid #ddd;
    border-radius: 20px;
}
.chat-input-area button {
    padding: 8px 16px;
    background: #1a4a6f;
    color: white;
    border: none;
    border-radius: 20px;
    cursor: pointer;
}
</style>

<div class="chat-fijo">
    <button class="chat-boton" id="abrirChat">??</button>
    <div class="chat-ventana" id="ventanaChat">
        <div class="chat-header">
            <span>?? Asistente SST</span>
            <button class="chat-cerrar" id="cerrarChat">?</button>
        </div>
        <div class="chat-mensajes" id="mensajesChat">
            <div class="mensaje-bot">?? Hola! Soy tu asistente SST. ?En que puedo ayudarte?</div>
        </div>
        <div class="chat-input-area">
            <input type="text" id="inputChat" placeholder="Escribe tu mensaje...">
            <button id="enviarChat">Enviar</button>
        </div>
    </div>
</div>

<script>
    const abrir = document.getElementById('abrirChat');
    const cerrar = document.getElementById('cerrarChat');
    const ventana = document.getElementById('ventanaChat');
    const enviar = document.getElementById('enviarChat');
    const input = document.getElementById('inputChat');
    const mensajes = document.getElementById('mensajesChat');
    
    // Abrir chat
    abrir.onclick = function() {
        ventana.style.display = 'flex';
    };
    
    // Cerrar chat
    cerrar.onclick = function() {
        ventana.style.display = 'none';
    };
    
    // Enviar mensaje
    function enviarMensaje() {
        const msg = input.value.trim();
        if(msg === "") return;
        
        // Mensaje del usuario
        const userDiv = document.createElement('div');
        userDiv.className = 'mensaje-usuario';
        userDiv.innerText = msg;
        mensajes.appendChild(userDiv);
        
        input.value = '';
        mensajes.scrollTop = mensajes.scrollHeight;
        
        // Respuesta del bot
        const botDiv = document.createElement('div');
        botDiv.className = 'mensaje-bot';
        botDiv.innerText = '?? Gracias por tu mensaje! Pronto tendremos respuestas con IA.';
        mensajes.appendChild(botDiv);
        mensajes.scrollTop = mensajes.scrollHeight;
    }
    
    enviar.onclick = enviarMensaje;
    
    // Enter para enviar
    input.onkeypress = function(e) {
        if(e.key === 'Enter') {
            enviarMensaje();
        }
    };
    
    // Iniciar cerrado
    ventana.style.display = 'none';
</script>
""", unsafe_allow_html=True)
