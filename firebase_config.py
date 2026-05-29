import streamlit as st
import firebase_admin
from firebase_admin import credentials, firestore
import json
import os

def init_firebase():
    """Inicializar Firebase - Funciona local y en la nube"""
    if not firebase_admin._apps:
        try:
            # Para Streamlit Cloud (usar secrets)
            if hasattr(st, "secrets") and "firebase" in st.secrets:
                firebase_config = {
                    "type": st.secrets["firebase"]["type"],
                    "project_id": st.secrets["firebase"]["project_id"],
                    "private_key_id": st.secrets["firebase"]["private_key_id"],
                    "private_key": st.secrets["firebase"]["private_key"].replace('\\n', '\n'),
                    "client_email": st.secrets["firebase"]["client_email"],
                    "client_id": st.secrets["firebase"]["client_id"],
                    "auth_uri": st.secrets["firebase"]["auth_uri"],
                    "token_uri": st.secrets["firebase"]["token_uri"]
                }
                cred = credentials.Certificate(firebase_config)
                firebase_admin.initialize_app(cred)
                return True
            
            # Para desarrollo local
            elif os.path.exists("firebase-credentials.json"):
                cred = credentials.Certificate("firebase-credentials.json")
                firebase_admin.initialize_app(cred)
                return True
            else:
                return False
        except Exception as e:
            print(f"Error Firebase: {e}")
            return False
    return True

def get_firestore_db():
    """Obtener instancia de Firestore"""
    if firebase_admin._apps:
        return firestore.client()
    return None

def sincronizar_datos(coleccion, datos):
    """Sincronizar datos a Firebase"""
    db = get_firestore_db()
    if db:
        try:
            for dato in datos:
                db.collection(coleccion).add(dato)
            return True
        except:
            return False
    return False

def cargar_datos(coleccion):
    """Cargar datos desde Firebase"""
    db = get_firestore_db()
    if db:
        try:
            docs = db.collection(coleccion).stream()
            return [doc.to_dict() for doc in docs]
        except:
            return []
    return []

# Inicializar al importar
FIREBASE_LISTO = init_firebase()
