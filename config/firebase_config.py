# config/firebase_config.py
import streamlit as st
from config.settings import settings

def get_firebase_config():
    """Obtener configuración de Firebase desde secrets o variables de entorno"""
    # Prioridad: Streamlit Secrets > Variables de entorno
    try:
        config = {
            "apiKey": st.secrets.get("FIREBASE_API_KEY", settings.FIREBASE_API_KEY),
            "authDomain": st.secrets.get("FIREBASE_AUTH_DOMAIN", settings.FIREBASE_AUTH_DOMAIN),
            "projectId": st.secrets.get("FIREBASE_PROJECT_ID", settings.FIREBASE_PROJECT_ID),
            "storageBucket": st.secrets.get("FIREBASE_STORAGE_BUCKET", settings.FIREBASE_STORAGE_BUCKET),
            "messagingSenderId": st.secrets.get("FIREBASE_MESSAGING_SENDER_ID", settings.FIREBASE_MESSAGING_SENDER_ID),
            "appId": st.secrets.get("FIREBASE_APP_ID", settings.FIREBASE_APP_ID),
        }
        return config
    except:
        return {
            "apiKey": settings.FIREBASE_API_KEY,
            "authDomain": settings.FIREBASE_AUTH_DOMAIN,
            "projectId": settings.FIREBASE_PROJECT_ID,
            "storageBucket": settings.FIREBASE_STORAGE_BUCKET,
            "messagingSenderId": settings.FIREBASE_MESSAGING_SENDER_ID,
            "appId": settings.FIREBASE_APP_ID,
        }
