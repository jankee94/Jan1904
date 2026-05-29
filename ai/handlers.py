import streamlit as st
import requests
import json

def get_gemini_key():
    """Obtener API key de Gemini desde secrets o variables de entorno"""
    try:
        return st.secrets.get("GEMINI_API_KEY")
    except:
        import os
        return os.environ.get("GEMINI_API_KEY")

def get_groq_key():
    """Obtener API key de Groq desde secrets o variables de entorno"""
    try:
        return st.secrets.get("GROQ_API_KEY")
    except:
        import os
        return os.environ.get("GROQ_API_KEY")

def call_gemini(prompt):
    """Llamar a Gemini API"""
    api_key = get_gemini_key()
    if not api_key:
        return "❌ GEMINI_API_KEY no configurada"
    
    url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-flash-latest:generateContent"
    headers = {"Content-Type": "application/json", "X-goog-api-key": api_key}
    data = {"contents": [{"parts": [{"text": f"Eres experto en SST. Responde: {prompt}"}]}]}
    
    try:
        r = requests.post(url, headers=headers, json=data, timeout=30)
        if r.status_code == 200:
            return r.json()["candidates"][0]["content"]["parts"][0]["text"]
        return f"Error Gemini: {r.status_code}"
    except Exception as e:
        return f"Error: {e}"

def call_groq(prompt):
    """Llamar a Groq API"""
    api_key = get_groq_key()
    if not api_key:
        return "❌ GROQ_API_KEY no configurada"
    
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    data = {"model": "llama-3.3-70b-versatile", "messages": [{"role": "user", "content": prompt}]}
    
    try:
        r = requests.post(url, headers=headers, json=data, timeout=30)
        if r.status_code == 200:
            return r.json()["choices"][0]["message"]["content"]
        return f"Error Groq: {r.status_code}"
    except Exception as e:
        return f"Error: {e}"
