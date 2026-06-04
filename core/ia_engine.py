import streamlit as st
import requests
from typing import Optional

class IAEngine:
    def __init__(self):
        self.gemini_key = self._get_gemini_key()
    
    def _get_gemini_key(self):
        try:
            return st.secrets.get("GEMINI_API_KEY")
        except:
            import os
            return os.environ.get("GEMINI_API_KEY")
    
    def call_gemini(self, prompt: str) -> Optional[str]:
        if not self.gemini_key:
            return None
        try:
            url = "https://generativelanguage.googleapis.com/v1/models/gemini-pro:generateContent"
            headers = {"Content-Type": "application/json", "x-goog-api-key": self.gemini_key}
            payload = {"contents": [{"parts": [{"text": prompt}]}]}
            response = requests.post(url, json=payload, headers=headers, timeout=30)
            if response.status_code == 200:
                data = response.json()
                candidates = data.get("candidates", [])
                if candidates:
                    parts = candidates[0].get("content", {}).get("parts", [])
                    if parts:
                        return parts[0].get("text")
            return None
        except:
            return None
    
    def generar_diagnostico(self, empresa_data: dict) -> str:
        nit = empresa_data.get('nit', 'No')
        trabajadores = empresa_data.get('trabajadores', 0)
        arl = empresa_data.get('arl', 'No')
        
        prompt = f"""
        Eres experto en SST en Colombia.
        NIT: {nit}
        Trabajadores: {trabajadores}
        ARL: {arl}
        
        Genera un diagnostico SST para esta empresa.
        Incluye: riesgos, normativa, acciones, presupuesto.
        Responde en español.
        """
        
        respuesta = self.call_gemini(prompt)
        if respuesta:
            return f"🤖 DIAGNOSTICO IA:\n\n{respuesta}"
        
        # Fallback local
        return f"""
DIAGNOSTICO SST

NIT: {nit}
Trabajadores: {trabajadores}
ARL: {arl}

ACCIONES PRIORITARIAS:
1. Constituir COPASST
2. Matriz de peligros GTC-45
3. Capacitaciones SST (8 horas anuales)

PRESUPUESTO ESTIMADO: ${trabajadores * 150000:,} COP/año

NORMATIVA: Decreto 1072/2015, Resolucion 0312/2019
"""
    
    def responder_chat(self, pregunta: str, contexto: dict) -> str:
        respuesta = self.call_gemini(f"Pregunta SST: {pregunta}")
        if respuesta:
            return respuesta
        return "IA no disponible. Verifica la API key en Secrets."

ia_engine = IAEngine()
