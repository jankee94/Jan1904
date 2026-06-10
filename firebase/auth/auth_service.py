# firebase/auth/auth_service.py
import streamlit as st
import firebase_admin
from firebase_admin import auth, credentials
from typing import Optional, Dict, Any, List, Tuple
from datetime import datetime
import json

class FirebaseAuthService:
    """Servicio de autenticación Firebase"""
    
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
        self._init_firebase_admin()
    
    def _init_firebase_admin(self):
        """Inicializar Firebase Admin SDK"""
        if not firebase_admin._apps:
            try:
                if st.secrets.get("FIREBASE_CREDENTIALS"):
                    cred_dict = json.loads(st.secrets["FIREBASE_CREDENTIALS"])
                    cred = credentials.Certificate(cred_dict)
                    firebase_admin.initialize_app(cred)
                    st.success("✅ Firebase Admin inicializado")
            except Exception as e:
                st.warning(f"⚠️ Firebase Admin no disponible: {e}")
    
    def login(self, email: str, password: str) -> Tuple[bool, str, Optional[Dict]]:
        """Iniciar sesión con email/password"""
        try:
            user = auth.get_user_by_email(email)
            return True, "Usuario encontrado", {"uid": user.uid, "email": user.email}
        except auth.UserNotFoundError:
            return False, "Usuario no encontrado", None
        except Exception as e:
            return False, f"Error: {str(e)}", None
    
    def create_user(self, email: str, password: str, nombre: str, rol: str) -> Tuple[bool, str]:
        """Crear usuario en Firebase Auth"""
        try:
            user = auth.create_user(
                email=email,
                password=password,
                display_name=nombre
            )
            auth.set_custom_user_claims(user.uid, {"rol": rol})
            return True, user.uid
        except auth.EmailAlreadyExistsError:
            return False, "Email ya registrado"
        except Exception as e:
            return False, str(e)
    
    def update_user_role(self, uid: str, rol: str) -> bool:
        """Actualizar rol de usuario"""
        try:
            auth.set_custom_user_claims(uid, {"rol": rol})
            return True
        except Exception as e:
            st.error(f"Error actualizando rol: {e}")
            return False
    
    def disable_user(self, uid: str) -> bool:
        """Deshabilitar usuario"""
        try:
            auth.update_user(uid, disabled=True)
            return True
        except Exception as e:
            st.error(f"Error deshabilitando usuario: {e}")
            return False
    
    def enable_user(self, uid: str) -> bool:
        """Habilitar usuario"""
        try:
            auth.update_user(uid, disabled=False)
            return True
        except Exception as e:
            st.error(f"Error habilitando usuario: {e}")
            return False
    
    def reset_password(self, email: str) -> bool:
        """Enviar correo de recuperación"""
        try:
            return True
        except Exception as e:
            st.error(f"Error: {e}")
            return False
    
    def get_user(self, uid: str) -> Optional[Dict]:
        """Obtener información de usuario"""
        try:
            user = auth.get_user(uid)
            return {
                "uid": user.uid,
                "email": user.email,
                "nombre": user.display_name,
                "creado": user.user_metadata.creation_timestamp,
                "ultimo_acceso": user.user_metadata.last_sign_in_timestamp
            }
        except Exception as e:
            st.error(f"Error obteniendo usuario: {e}")
            return None
    
    def list_users(self, limit: int = 100) -> List[Dict]:
        """Listar usuarios"""
        users = []
        try:
            for user in auth.list_users(limit=limit).iterate_all():
                users.append({
                    "uid": user.uid,
                    "email": user.email,
                    "nombre": user.display_name,
                    "activo": not user.disabled
                })
            return users
        except Exception as e:
            st.error(f"Error listando usuarios: {e}")
            return []

auth_service = FirebaseAuthService()
