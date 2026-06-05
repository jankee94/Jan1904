import requests
import streamlit as st

class IAEngine:
    def __init__(self):
        self.api_key = st.secrets.get("GEMINI_API_KEY", "")
    
    def call(self, prompt):
        if not self.api_key:
            return None
        try:
            url = "https://generativelanguage.googleapis.com/v1/models/gemini-pro:generateContent"
            headers = {"Content-Type": "application/json", "x-goog-api-key": self.api_key}
            data = {"contents": [{"parts": [{"text": prompt}]}]}
            r = requests.post(url, json=data, headers=headers, timeout=30)
            if r.status_code == 200:
                return r.json()["candidates"][0]["content"]["parts"][0]["text"]
        except:
            pass
        return None

ia = IAEngine()