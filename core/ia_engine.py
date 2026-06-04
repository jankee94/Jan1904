import streamlit as st
import requests
import itertools

class IAEngine:
    def __init__(self):
        # Cargar keys desde secrets
        self.gemini_keys = self._get_gemini_keys()
        self.groq_key = st.secrets.get("GROQ_API_KEY", "")
        self.gemini_cycle = itertools.cycle(self.gemini_keys) if self.gemini_keys else None
    
    def _get_gemini_keys(self):
        keys = []
        i = 1
        while True:
            key = st.secrets.get(f"GEMINI_API_KEY_{i}")
            if not key:
                break
            keys.append(key)
            i += 1
        if not keys:
            old_key = st.secrets.get("GEMINI_API_KEY")
            if old_key:
                keys.append(old_key)
        return keys
    
    def call_gemini(self, prompt):
        """Llama a Gemini con rotación de keys"""
        if not self.gemini_keys:
            return None
        
        for _ in range(len(self.gemini_keys)):
            key = next(self.gemini_cycle)
            try:
                url = "https://generativelanguage.googleapis.com/v1/models/gemini-pro:generateContent"
                headers = {"Content-Type": "application/json", "x-goog-api-key": key}
                data = {"contents": [{"parts": [{"text": prompt}]}]}
                r = requests.post(url, json=data, headers=headers, timeout=30)
                if r.status_code == 200:
                    return r.json()["candidates"][0]["content"]["parts"][0]["text"]
            except:
                continue
        return None
    
    def call_groq(self, prompt):
        """Llama a Groq API"""
        if not self.groq_key:
            return None
        try:
            url = "https://api.groq.com/openai/v1/chat/completions"
            headers = {
                "Authorization": f"Bearer {self.groq_key}",
                "Content-Type": "application/json"
            }
            data = {
                "model": "llama-3.3-70b-versatile",
                "messages": [{"role": "user", "content": prompt}],
                "temperature": 0.7
            }
            r = requests.post(url, json=data, headers=headers, timeout=30)
            if r.status_code == 200:
                return r.json()["choices"][0]["message"]["content"]
        except:
            pass
        return None
    
    def call_best(self, prompt):
        """Intenta Gemini primero, si falla usa Groq"""
        respuesta = self.call_gemini(prompt)
        if respuesta:
            return respuesta
        respuesta = self.call_groq(prompt)
        if respuesta:
            return respuesta
        return None

# Instancia global
ia = IAEngine()
