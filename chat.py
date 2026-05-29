import streamlit as st
import time

def chat_floating_button():
    st.markdown("""
    <style>
    /* Botón flotante animado */
    .float-chat {
        position: fixed;
        bottom: 25px;
        right: 25px;
        width: 65px;
        height: 65px;
        background: linear-gradient(135deg, #0b3b5f, #1b5a7a);
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        cursor: pointer;
        z-index: 1000;
        box-shadow: 0 6px 14px rgba(0,0,0,0.3);
        transition: all 0.3s ease;
        border: none;
        color: white;
        font-size: 32px;
    }
    .float-chat:hover {
        transform: scale(1.08);
        background: linear-gradient(135deg, #0a2e4a, #124a64);
        box-shadow: 0 8px 20px rgba(0,0,0,0.4);
    }
    /* Ventana del chat */
    .chat-window {
        position: fixed;
        bottom: 100px;
        right: 25px;
        width: 380px;
        height: 550px;
        background: white;
        border-radius: 20px;
        box-shadow: 0 10px 30px rgba(0,0,0,0.2);
        display: flex;
        flex-direction: column;
        z-index: 999;
        overflow: hidden;
        font-family: 'Segoe UI', sans-serif;
        transition: all 0.2s;
        border: 1px solid #ddd;
    }
    .chat-header {
        background: linear-gradient(90deg, #0b3b5f, #1b5a7a);
        color: white;
        padding: 12px 15px;
        font-weight: bold;
        font-size: 16px;
        display: flex;
        justify-content: space-between;
        align-items: center;
    }
    .chat-close {
        cursor: pointer;
        font-size: 22px;
        font-weight: bold;
    }
    .chat-messages {
        flex: 1;
        padding: 12px;
        overflow-y: auto;
        background: #f4f7fb;
    }
    .message {
        margin-bottom: 12px;
        padding: 8px 12px;
        border-radius: 18px;
        max-width: 85%;
        font-size: 14px;
        line-height: 1.4;
    }
    .user {
        background: #1b5a7a;
        color: white;
        margin-left: auto;
        text-align: right;
        border-bottom-right-radius: 4px;
    }
    .bot {
        background: white;
        color: #1e2a3a;
        border: 1px solid #dce4ec;
        margin-right: auto;
        border-bottom-left-radius: 4px;
    }
    .chat-input-area {
        display: flex;
        padding: 12px;
        border-top: 1px solid #e2e8f0;
        background: white;
    }
    .chat-input {
        flex: 1;
        padding: 10px;
        border: 1px solid #cbd5e0;
        border-radius: 30px;
        font-size: 14px;
        outline: none;
    }
    .chat-send {
        background: #0b3b5f;
        border: none;
        color: white;
        border-radius: 30px;
        padding: 8px 18px;
        margin-left: 8px;
        cursor: pointer;
        font-weight: bold;
    }
    </style>
    
    <div id="floatChatBtn" class="float-chat">💬</div>
    <div id="chatWindow" class="chat-window" style="display: none;">
        <div class="chat-header">
            <span>🤖 Asistente SST Guía</span>
            <span id="closeChat" class="chat-close">×</span>
        </div>
        <div id="chatMessages" class="chat-messages">
            <div class="message bot">¡Hola! Soy tu asistente guía de SST. Cuéntame sobre tu empresa y riesgos, y te ayudaré a construir todo el sistema.</div>
        </div>
        <div class="chat-input-area">
            <input type="text" id="chatInput" class="chat-input" placeholder="Escribe tu mensaje...">
            <button id="sendChat" class="chat-send">Enviar</button>
        </div>
    </div>
    
    <script>
    const btn = document.getElementById('floatChatBtn');
    const win = document.getElementById('chatWindow');
    const closeBtn = document.getElementById('closeChat');
    const sendBtn = document.getElementById('sendChat');
    const input = document.getElementById('chatInput');
    const messagesDiv = document.getElementById('chatMessages');
    
    btn.onclick = () => { win.style.display = 'flex'; };
    closeBtn.onclick = () => { win.style.display = 'none'; };
    
    async function sendMessage() {
        const msg = input.value.trim();
        if (!msg) return;
        // mostrar mensaje usuario
        messagesDiv.innerHTML += `<div class="message user">${escapeHtml(msg)}</div>`;
        messagesDiv.scrollTop = messagesDiv.scrollHeight;
        input.value = '';
        // indicador
        messagesDiv.innerHTML += `<div class="message bot" id="typing">🤔 Pensando...</div>`;
        messagesDiv.scrollTop = messagesDiv.scrollHeight;
        
        try {
            const response = await fetch('/_stcore/guide-chat', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({message: msg})
            });
            const data = await response.json();
            document.getElementById('typing')?.remove();
            messagesDiv.innerHTML += `<div class="message bot">${escapeHtml(data.reply)}</div>`;
        } catch(e) {
            document.getElementById('typing')?.remove();
            messagesDiv.innerHTML += `<div class="message bot">⚠️ Error de conexión</div>`;
        }
        messagesDiv.scrollTop = messagesDiv.scrollHeight;
    }
    
    sendBtn.onclick = sendMessage;
    input.onkeypress = (e) => { if(e.key === 'Enter') sendMessage(); };
    
    function escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }
    </script>
    """, unsafe_allow_html=True)
