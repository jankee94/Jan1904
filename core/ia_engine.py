import streamlit as st
import requests

class IAEngine:
    def __init__(self):
        self.key = st.secrets.get("GEMINI_API_KEY")
    
    def call_gemini(self, prompt):
        if not self.key:
            return None
        url = "https://generativelanguage.googleapis.com/v1/models/gemini-pro:generateContent"
        headers = {"Content-Type": "application/json", "x-goog-api-key": self.key}
        data = {"contents": [{"parts": [{"text": prompt}]}]}
        try:
            r = requests.post(url, json=data, headers=headers, timeout=30)
            if r.status_code == 200:
                return r.json()["candidates"][0]["content"]["parts"][0]["text"]
        except:
            pass
        return None
    
    def generar_diagnostico(self, empresa):
        nit = empresa.get("nit", "")
        tra = empresa.get("trabajadores", 0)
        arl = empresa.get("arl", "")
        prompt = f"NIT: {nit}, Trabajadores: {tra}, ARL: {arl}. Genera diagnostico SST completo para Colombia."
        res = self.call_gemini(prompt)
        return res if res else f"DIAGNOSTICO BASICO: Empresa con {tra} trabajadores. Acciones: 1. COPASST 2. Matriz de peligros 3. Capacitaciones. Presupuesto: ${tra*150000:,} COP"

ia = IAEngine()
