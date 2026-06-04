"""
Motor IA para SG-SST PHVA
"""
import streamlit as st
import requests
import json
from typing import Optional, Dict, Any

class IAEngine:
    def __init__(self):
        self.gemini_key = self._get_gemini_key()
        self.groq_key = self._get_groq_key()
    
    def _get_gemini_key(self):
        try:
            return st.secrets.get("GEMINI_API_KEY")
        except:
            import os
            return os.environ.get("GEMINI_API_KEY")
    
    def _get_groq_key(self):
        try:
            return st.secrets.get("GROQ_API_KEY")
        except:
            import os
            return os.environ.get("GROQ_API_KEY")
    
    def call_gemini(self, prompt: str, system_prompt: str = "") -> Optional[str]:
        if not self.gemini_key:
            return None
        try:
            url = "https://generativelanguage.googleapis.com/v1/models/gemini-pro:generateContent"
            headers = {
                "Content-Type": "application/json",
                "x-goog-api-key": self.gemini_key
            }
            full_prompt = f"{system_prompt}\n\n{prompt}" if system_prompt else prompt
            payload = {
                "contents": [
                    {
                        "parts": [
                            {"text": full_prompt}
                        ]
                    }
                ]
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
            return None
    
    def call_groq(self, prompt: str) -> Optional[str]:
        if not self.groq_key:
            return None
        try:
            url = "https://api.groq.com/openai/v1/chat/completions"
            headers = {
                "Authorization": f"Bearer {self.groq_key}",
                "Content-Type": "application/json"
            }
            payload = {
                "model": "llama-3.3-70b-versatile",
                "messages": [{"role": "user", "content": prompt}],
                "temperature": 0.7
            }
            response = requests.post(url, json=payload, headers=headers, timeout=30)
            if response.status_code == 200:
                data = response.json()
                choices = data.get("choices", [])
                if choices:
                    message = choices[0].get("message", {})
                    return message.get("content", None)
            return None
        except Exception as e:
            return None
    
    def generar_diagnostico(self, empresa_data: Dict) -> str:
        prompt = f"""
        DATOS:
        - NIT: {empresa_data.get('nit', 'No')}
        - Trabajadores: {empresa_data.get('trabajadores', 0)}
        - ARL: {empresa_data.get('arl', 'No')}
        
        Genera diagnostico SST para PYME en Colombia.
        Incluye: riesgos, normativa, acciones, presupuesto.
        """
        respuesta = self.call_gemini(prompt, "Eres experto SST en Colombia")
        if respuesta:
            return f"🤖 Diagnostico IA:\n\n{respuesta}"
        respuesta = self.call_groq(prompt)
        if respuesta:
            return f"🤖 Diagnostico IA:\n\n{respuesta}"
        return self._diagnostico_local(empresa_data)
    
    def _diagnostico_local(self, empresa_data: Dict) -> str:
        t = empresa_data.get('trabajadores', 0)
        return f"""
DIAGNOSTICO SST

NIT: {empresa_data.get('nit', 'No')}
Trabajadores: {t}
ARL: {empresa_data.get('arl', 'No')}

ACCIONES:
1. Constituir COPASST
2. Matriz de peligros GTC-45
3. Capacitaciones SST (8 horas)

PRESUPUESTO: ${t * 150000:,} COP
"""
    
    def responder_chat(self, pregunta: str, contexto: Dict) -> str:
        respuesta = self.call_gemini(f"Pregunta SST: {pregunta}", "Eres experto SST")
        if respuesta:
            return respuesta
        respuesta = self.call_groq(f"Pregunta SST: {pregunta}")
        if respuesta:
            return respuesta
        return "IA no disponible. Ve a Test IA."

ia_engine = IAEngine()
