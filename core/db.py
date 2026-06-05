# core/db.py
import streamlit as st
import firebase_admin
from firebase_admin import firestore, credentials
from typing import Optional, List, Dict, Any
from datetime import datetime
from config.settings import settings

class FirestoreDB:
    """Gestor de base de datos Firestore"""
    
    def __init__(self):
        self.db = self.init_firestore()
    
    def init_firestore(self):
        """Inicializar Firestore"""
        if not firebase_admin._apps:
            try:
                cred = credentials.Certificate(settings.FIREBASE_CREDENTIALS_PATH)
                firebase_admin.initialize_app(cred)
            except Exception as e:
                st.error(f"Error Firebase: {e}")
                return None
        return firestore.client()
    
    def get_collection(self, name: str):
        """Obtener referencia a colección"""
        if not self.db:
            return None
        return self.db.collection(name)
    
    def create_document(self, collection: str, data: Dict[str, Any]) -> Optional[str]:
        """Crear documento y devolver ID"""
        try:
            data["created_at"] = datetime.now()
            data["updated_at"] = datetime.now()
            
            doc_ref = self.db.collection(collection).add(data)
            return doc_ref[1].id
        except Exception as e:
            st.error(f"Error crear documento: {e}")
            return None
    
    def get_document(self, collection: str, doc_id: str) -> Optional[Dict]:
        """Obtener documento por ID"""
        try:
            doc = self.db.collection(collection).document(doc_id).get()
            if doc.exists:
                return {"id": doc.id, **doc.to_dict()}
            return None
        except Exception as e:
            st.error(f"Error obtener documento: {e}")
            return None
    
    def get_all(self, collection: str, filters: List = None, limit: int = None) -> List[Dict]:
        """Obtener todos los documentos con filtros"""
        try:
            query = self.db.collection(collection)
            
            if filters:
                for field, op, value in filters:
                    query = query.where(field, op, value)
            
            if limit:
                query = query.limit(limit)
            
            docs = query.stream()
            return [{"id": doc.id, **doc.to_dict()} for doc in docs]
        except Exception as e:
            st.error(f"Error obtener documentos: {e}")
            return []
    
    def update_document(self, collection: str, doc_id: str, data: Dict[str, Any]) -> bool:
        """Actualizar documento"""
        try:
            data["updated_at"] = datetime.now()
            self.db.collection(collection).document(doc_id).update(data)
            return True
        except Exception as e:
            st.error(f"Error actualizar: {e}")
            return False
    
    def delete_document(self, collection: str, doc_id: str) -> bool:
        """Eliminar documento (soft delete)"""
        try:
            self.update_document(collection, doc_id, {"estado": "inactivo"})
            return True
        except Exception as e:
            st.error(f"Error eliminar: {e}")
            return False

db = FirestoreDB()