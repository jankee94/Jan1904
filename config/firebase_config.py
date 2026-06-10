# config/firebase_config.py
import streamlit as st
import json

FIREBASE_CONFIG = {
    "apiKey": st.secrets.get("FIREBASE_API_KEY", ""),
    "authDomain": st.secrets.get("FIREBASE_AUTH_DOMAIN", ""),
    "projectId": st.secrets.get("FIREBASE_PROJECT_ID", ""),
    "storageBucket": st.secrets.get("FIREBASE_STORAGE_BUCKET", ""),
    "messagingSenderId": st.secrets.get("FIREBASE_MESSAGING_SENDER_ID", ""),
    "appId": st.secrets.get("FIREBASE_APP_ID", "")
}

def get_firebase_config():
    return FIREBASE_CONFIG
