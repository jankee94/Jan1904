# firebase/firestore/client.py
import streamlit as st
from google.cloud import firestore
from google.oauth2 import service_account
from typing import Optional, List, Dict, Any, Tuple
from datetime import datetime
import json

class FirestoreClient:
    """Cliente Firestore para operaciones CRUD"""
    
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
        """Inicializar conexión a Firestore"""
        try:
            if st.secrets.get("FIREBASE_CREDENTIALS"):
                cred_dict = json.loads(st.secrets["FIREBASE_CREDENTIALS"])
                credentials = service_account.Credentials.from_service_account_info(cred_dict)
                self.db = firestore.Client(credentials=credentials, project=cred_dict.get("project_id"))
                st.success("✅ Conectado a Firestore")
        except Exception as e:
            st.warning(f"⚠️ Firestore no disponible: {e}")
            self.db = None
    
    def get_collection(self, collection_name: str):
        """Obtener referencia a una colección"""
        if self.db:
            return self.db.collection(collection_name)
        return None
    
    def create(self, collection: str, data: Dict[str, Any]) -> Optional[str]:
        """Crear documento"""
        try:
            doc_ref = self.get_collection(collection).add(data)
            return doc_ref[1].id
        except Exception as e:
            st.error(f"Error creando documento: {e}")
            return None
    
    def read(self, collection: str, doc_id: str) -> Optional[Dict]:
        """Leer documento por ID"""
        try:
            doc = self.get_collection(collection).document(doc_id).get()
            if doc.exists:
                return {"id": doc.id, **doc.to_dict()}
            return None
        except Exception as e:
            st.error(f"Error leyendo documento: {e}")
            return None
    
    def update(self, collection: str, doc_id: str, data: Dict[str, Any]) -> bool:
        """Actualizar documento"""
        try:
            data["updated_at"] = datetime.now().isoformat()
            self.get_collection(collection).document(doc_id).update(data)
            return True
        except Exception as e:
            st.error(f"Error actualizando documento: {e}")
            return False
    
    def delete(self, collection: str, doc_id: str) -> bool:
        """Eliminar documento (soft delete)"""
        try:
            self.update(collection, doc_id, {"is_active": False, "deleted_at": datetime.now().isoformat()})
            return True
        except Exception as e:
            st.error(f"Error eliminando documento: {e}")
            return False
    
    def query(self, collection: str, filters: List = None, order_by: str = None, 
              limit: int = None, start_after: str = None) -> List[Dict]:
        """Query con filtros"""
        try:
            query = self.get_collection(collection)
            
            if filters:
                for field, op, value in filters:
                    query = query.where(field, op, value)
            
            if order_by:
                query = query.order_by(order_by)
            
            if limit:
                query = query.limit(limit)
            
            docs = query.stream()
            return [{"id": doc.id, **doc.to_dict()} for doc in docs]
        except Exception as e:
            st.error(f"Error en query: {e}")
            return []
    
    def paginate(self, collection: str, page: int = 1, page_size: int = 20,
                 filters: List = None, order_by: str = None) -> Dict:
        """Paginación de resultados"""
        start_at = (page - 1) * page_size
        results = self.query(collection, filters, order_by, limit=page_size + 1)
        
        has_next = len(results) > page_size
        items = results[:page_size]
        
        return {
            "items": items,
            "page": page,
            "page_size": page_size,
            "has_next": has_next,
            "has_prev": page > 1,
            "total": len(items)
        }

firestore_client = FirestoreClient()
