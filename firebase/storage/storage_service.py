# firebase/storage/storage_service.py
import streamlit as st
from firebase_admin import storage
from typing import Optional, List
import io
from datetime import datetime

class FirebaseStorageService:
    """Servicio de almacenamiento Firebase Storage"""
    
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
        self.bucket = None
        self._init_storage()
    
    def _init_storage(self):
        """Inicializar Firebase Storage"""
        try:
            self.bucket = storage.bucket()
            st.success("✅ Firebase Storage inicializado")
        except Exception as e:
            st.warning(f"⚠️ Firebase Storage no disponible: {e}")
    
    def upload_file(self, file, path: str, content_type: str = None) -> Optional[str]:
        """Subir archivo a Storage"""
        try:
            blob = self.bucket.blob(path)
            if content_type:
                blob.content_type = content_type
            blob.upload_from_file(file)
            blob.make_public()
            return blob.public_url
        except Exception as e:
            st.error(f"Error subiendo archivo: {e}")
            return None
    
    def upload_bytes(self, data: bytes, path: str, content_type: str = None) -> Optional[str]:
        """Subir bytes a Storage"""
        try:
            blob = self.bucket.blob(path)
            if content_type:
                blob.content_type = content_type
            blob.upload_from_string(data)
            blob.make_public()
            return blob.public_url
        except Exception as e:
            st.error(f"Error subiendo archivo: {e}")
            return None
    
    def download_file(self, path: str) -> Optional[bytes]:
        """Descargar archivo de Storage"""
        try:
            blob = self.bucket.blob(path)
            return blob.download_as_bytes()
        except Exception as e:
            st.error(f"Error descargando archivo: {e}")
            return None
    
    def delete_file(self, path: str) -> bool:
        """Eliminar archivo de Storage"""
        try:
            blob = self.bucket.blob(path)
            blob.delete()
            return True
        except Exception as e:
            st.error(f"Error eliminando archivo: {e}")
            return False
    
    def list_files(self, prefix: str = "") -> List[str]:
        """Listar archivos en Storage"""
        try:
            blobs = self.bucket.list_blobs(prefix=prefix)
            return [blob.name for blob in blobs]
        except Exception as e:
            st.error(f"Error listando archivos: {e}")
            return []
    
    def get_url(self, path: str) -> Optional[str]:
        """Obtener URL pública de un archivo"""
        try:
            blob = self.bucket.blob(path)
            return blob.public_url
        except Exception as e:
            st.error(f"Error obteniendo URL: {e}")
            return None

storage_service = FirebaseStorageService()
