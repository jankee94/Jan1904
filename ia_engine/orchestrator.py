import requests
import streamlit as st

class OrquestadorIA:
    def __init__(self):
        self.gemini_key = st.secrets.get("GEMINI_API_KEY", "")
    
    def call_gemini(self, prompt):
        if not self.gemini_key:
            return "IA no configurada"
        try:
            url = "https://generativelanguage.googleapis.com/v1/models/gemini-pro:generateContent"
            headers = {"Content-Type": "application/json", "x-goog-api-key": self.gemini_key}
            data = {"contents": [{"parts": [{"text": prompt}]}]}
            r = requests.post(url, json=data, headers=headers, timeout=30)
            if r.status_code == 200:
                return r.json()["candidates"][0]["content"]["parts"][0]["text"]
        except:
            pass
        return "Error con IA"
