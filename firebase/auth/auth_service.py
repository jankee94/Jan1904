# firebase/auth/auth_service.py
import streamlit as st
import firebase_admin
from firebase_admin import auth, credentials
from typing import Optional, Dict, List, Tuple
import json

class FirebaseAuthService:
    """Servicio de autenticación con Firebase"""
    
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
        self._init_firebase()
    
    def _init_firebase(self):
        try:
            if not firebase_admin._apps:
                if st.secrets.get("FIREBASE_CREDENTIALS"):
                    cred_dict = json.loads(st.secrets["FIREBASE_CREDENTIALS"])
                    cred = credentials.Certificate(cred_dict)
                    firebase_admin.initialize_app(cred)
        except Exception as e:
            st.warning(f"Firebase no disponible: {e}")
    
    def login(self, email: str, password: str) -> Tuple[bool, str, Optional[Dict]]:
        try:
            user = auth.get_user_by_email(email)
            return True, "Login exitoso", {"uid": user.uid, "email": user.email}
        except auth.UserNotFoundError:
            return False, "Usuario no encontrado", None
        except Exception as e:
            return False, str(e), None
    
    def create_user(self, email: str, password: str, nombre: str, rol: str, empresa_id: str) -> Tuple[bool, str]:
        try:
            user = auth.create_user(email=email, password=password, display_name=nombre)
            auth.set_custom_user_claims(user.uid, {"rol": rol, "empresa_id": empresa_id})
            return True, user.uid
        except auth.EmailAlreadyExistsError:
            return False, "Email ya registrado"
        except Exception as e:
            return False, str(e)
    
    def update_user_role(self, uid: str, rol: str) -> bool:
        try:
            auth.set_custom_user_claims(uid, {"rol": rol})
            return True
        except Exception as e:
            return False
    
    def disable_user(self, uid: str) -> bool:
        try:
            auth.update_user(uid, disabled=True)
            return True
        except Exception as e:
            return False
    
    def get_user(self, uid: str) -> Optional[Dict]:
        try:
            user = auth.get_user(uid)
            return {"uid": user.uid, "email": user.email, "nombre": user.display_name}
        except Exception as e:
            return None

auth_service = FirebaseAuthService()
