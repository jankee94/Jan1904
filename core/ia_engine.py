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
        r = requests.post(url, json=data, headers=headers)
        if r.status_code == 200:
            return r.json()["candidates"][0]["content"]["parts"][0]["text"]
        return None
    
    def generar_diagnostico(self, empresa):
        prompt = f"NIT: {empresa.get('nit')} Trabajadores: {empresa.get('trabajadores')} ARL: {empresa.get('arl')}"
        res = self.call_gemini(prompt)
        return res if res else "IA no disponible"

ia = IAEngine()
