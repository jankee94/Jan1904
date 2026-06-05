import firebase_admin
from firebase_admin import credentials, firestore
import streamlit as st
import json

class FirebaseDB:
    def __init__(self):
        try:
            if not firebase_admin._apps:
                # Configuración Firebase
                firebase_config = {
                    "apiKey": "AIzaSyDFb8VnVSOvVrKHwa7xR4HT5jJuhLOsKGQ",
                    "authDomain": "programa-sst.firebaseapp.com",
                    "projectId": "programa-sst",
                    "storageBucket": "programa-sst.firebasestorage.app",
                    "messagingSenderId": "308946243574",
                    "appId": "1:308946243574:web:d7758e756a669dd27f01d7",
                    "measurementId": "G-HKXV1LGDHW"
                }
                cred = credentials.Certificate("firebase-credentials.json")
                firebase_admin.initialize_app(cred)
            self.db = firestore.client()
        except:
            self.db = None
            st.warning("Firebase no disponible, usando SQLite local")
    
    def guardar_empresa(self, nombre, trabajadores, arl, diagnostico):
        if self.db:
            doc_ref = self.db.collection('empresas').document('actual')
            doc_ref.set({
                'nombre': nombre,
                'trabajadores': trabajadores,
                'arl': arl,
                'diagnostico': diagnostico,
                'fecha': firestore.SERVER_TIMESTAMP
            })
    
    def obtener_empresa(self):
        if self.db:
            doc_ref = self.db.collection('empresas').document('actual')
            doc = doc_ref.get()
            if doc.exists:
                return doc.to_dict()
        return None
    
    def guardar_peligro(self, datos):
        if self.db:
            self.db.collection('peligros').add(datos)
    
    def obtener_peligros(self):
        if self.db:
            docs = self.db.collection('peligros').stream()
            return [doc.to_dict() for doc in docs]
        return []
    
    def guardar_accion(self, datos):
        if self.db:
            self.db.collection('acciones').add(datos)
    
    def obtener_acciones(self):
        if self.db:
            docs = self.db.collection('acciones').stream()
            return [doc.to_dict() for doc in docs]
        return []

firebase_db = FirebaseDB()