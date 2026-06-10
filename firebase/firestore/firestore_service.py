# firebase/firestore/firestore_service.py
import streamlit as st
from google.cloud import firestore
from google.oauth2 import service_account
from typing import Optional, List, Dict, Any
import json
from datetime import datetime

class FirestoreService:
    """Servicio Firestore con soporte multiempresa"""
    
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
        self._initialized = True
        self.db = None
        self._init_firestore()
    
    def _init_firestore(self):
        try:
            if st.secrets.get("FIREBASE_CREDENTIALS"):
                cred_dict = json.loads(st.secrets["FIREBASE_CREDENTIALS"])
                credentials = service_account.Credentials.from_service_account_info(cred_dict)
                self.db = firestore.Client(credentials=credentials)
        except Exception as e:
            st.warning(f"Firestore no disponible: {e}")
    
    def get_empresa_path(self, empresa_id: str) -> str:
        """Obtener path base de una empresa"""
        return f"empresas/{empresa_id}"
    
    def create_document(self, empresa_id: str, coleccion: str, data: Dict) -> Optional[str]:
        try:
            doc_ref = self.db.collection("empresas").document(empresa_id).collection(coleccion).add(data)
            return doc_ref[1].id
        except Exception as e:
            st.error(f"Error creando: {e}")
            return None
    
    def get_documents(self, empresa_id: str, coleccion: str, filters: List = None) -> List[Dict]:
        try:
            query = self.db.collection("empresas").document(empresa_id).collection(coleccion)
            if filters:
                for field, op, value in filters:
                    query = query.where(field, op, value)
            docs = query.stream()
            return [{"id": doc.id, **doc.to_dict()} for doc in docs]
        except Exception as e:
            st.error(f"Error obteniendo: {e}")
            return []
    
    def update_document(self, empresa_id: str, coleccion: str, doc_id: str, data: Dict) -> bool:
        try:
            data["updated_at"] = datetime.now().isoformat()
            self.db.collection("empresas").document(empresa_id).collection(coleccion).document(doc_id).update(data)
            return True
        except Exception as e:
            st.error(f"Error actualizando: {e}")
            return False
    
    def delete_document(self, empresa_id: str, coleccion: str, doc_id: str) -> bool:
        try:
            self.db.collection("empresas").document(empresa_id).collection(coleccion).document(doc_id).delete()
            return True
        except Exception as e:
            st.error(f"Error eliminando: {e}")
            return False

firestore_service = FirestoreService()
