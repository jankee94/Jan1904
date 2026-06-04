"""
Motor IA para SG-SST PHVA
"""
import streamlit as st
import requests
import json
from typing import Optional, Dict, Any
from datetime import datetime

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
            url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent"
            headers = {
                "Content-Type": "application/json",
                "X-goog-api-key": self.gemini_key
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
            return None
        except Exception as e:
            return None
    
    def generar_diagnostico(self, empresa_data: Dict) -> str:
        prompt = f"""
DATOS DE LA EMPRESA:
- Nombre: {empresa_data.get('nombre', 'No registrado')}
- Sector: {empresa_data.get('sector', 'No especificado')}
- Trabajadores: {empresa_data.get('trabajadores', 0)}

Genera un DIAGNOSTICO INICIAL DE SST para PYME en Colombia.
Incluye: riesgos del sector, normativa aplicable, acciones prioritarias.
"""
        respuesta = self.call_gemini(prompt, "Eres un consultor experto en SST")
        if respuesta:
            return f"🤖 Diagnostico IA:\n\n{respuesta}"
        respuesta = self.call_groq(prompt)
        if respuesta:
            return f"🤖 Diagnostico IA:\n\n{respuesta}"
        return self._diagnostico_local(empresa_data)
    
    def _diagnostico_local(self, empresa_data: Dict) -> str:
        sector = empresa_data.get('sector', 'General')
        if sector == "Construccion":
            return """
DIAGNOSTICO - CONSTRUCCION
Riesgos: Trabajo en alturas, maquinaria pesada
Acciones: Implementar lineas de vida, capacitaciones
Presupuesto: $2-5 millones COP
"""
        else:
            return """
DIAGNOSTICO BASE
Acciones: Constituir COPASST, matriz de peligros, capacitaciones
Presupuesto: $1-3 millones COP
"""
    
    def responder_chat(self, pregunta: str, contexto: Dict) -> str:
        prompt = f"Contexto: {contexto}\nPregunta: {pregunta}\nResponde como experto SST:"
        respuesta = self.call_gemini(prompt)
        if respuesta:
            return respuesta
        respuesta = self.call_groq(prompt)
        if respuesta:
            return respuesta
        return "Puedo ayudarte con peligros, capacitaciones, incidentes o normativa SST."

ia_engine = IAEngine()
