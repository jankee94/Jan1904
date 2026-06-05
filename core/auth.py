# core/auth.py
import streamlit as st
import firebase_admin
from firebase_admin import auth, firestore
from typing import Optional, Tuple, Dict, List
from enum import Enum
from datetime import datetime
import re

class UserRole(Enum):
    ADMIN = "admin"
    RESPONSABLE_SST = "responsable_sst"
    SUPERVISOR = "supervisor"
    TRABAJADOR = "trabajador"
    AUDITOR = "auditor"

class AuthManager:
    """Sistema de autenticación y RBAC con Firebase Auth"""
    
    def __init__(self):
        self.init_firebase_auth()
        self.db = firestore.client()
    
    def init_firebase_auth(self):
        """Inicializar Firebase Auth si no está iniciado"""
        if not firebase_admin._apps:
            try:
                cred = firebase_admin.credentials.Certificate("firebase-credentials.json")
                firebase_admin.initialize_app(cred)
            except:
                pass
    
    def login(self, email: str, password: str) -> Tuple[bool, str]:
        """Iniciar sesión con email y password"""
        try:
            # Autenticar con Firebase Auth
            user = auth.get_user_by_email(email)
            
            # Obtener usuario de Firestore
            user_doc = self.db.collection("usuarios").document(user.uid).get()
            
            if not user_doc.exists:
                return False, "Usuario no registrado en el sistema"
            
            user_data = user_doc.to_dict()
            
            # Verificar estado
            if user_data.get("estado") != "activo":
                return False, "Usuario inactivo"
            
            # Guardar en sesión
            st.session_state.user_id = user.uid
            st.session_state.user_email = email
            st.session_state.user_name = user_data.get("nombre", "")
            st.session_state.user_role = UserRole(user_data.get("rol", "trabajador"))
            st.session_state.authenticated = True
            
            # Registrar login
            self.registrar_auditoria("login", "usuario", user.uid, None, {"email": email})
            
            return True, "Login exitoso"
            
        except auth.UserNotFoundError:
            return False, "Usuario no encontrado"
        except Exception as e:
            return False, f"Error: {str(e)}"
    
    def register(self, email: str, password: str, nombre: str, rol: str) -> Tuple[bool, str]:
        """Registrar nuevo usuario solo ADMIN"""
        if not self.tiene_permiso("usuarios", "crear"):
            return False, "No tienes permisos"
        
        try:
            # Crear en Firebase Auth
            user = auth.create_user(
                email=email,
                password=password,
                display_name=nombre
            )
            
            # Guardar en Firestore
            user_data = {
                "email": email,
                "nombre": nombre,
                "rol": rol,
                "estado": "activo",
                "created_at": datetime.now(),
                "created_by": st.session_state.user_id
            }
            
            self.db.collection("usuarios").document(user.uid).set(user_data)
            
            self.registrar_auditoria("crear_usuario", "usuarios", user.uid, None, user_data)
            
            return True, f"Usuario {email} creado exitosamente"
            
        except auth.EmailAlreadyExistsError:
            return False, "Email ya registrado"
        except Exception as e:
            return False, f"Error: {str(e)}"
    
    def logout(self):
        """Cerrar sesión"""
        if self.authenticated():
            self.registrar_auditoria("logout", "usuario", st.session_state.user_id, None, {})
        
        st.session_state.authenticated = False
        st.session_state.user_id = None
        st.session_state.user_email = None
        st.session_state.user_name = None
        st.session_state.user_role = None
    
    def authenticated(self) -> bool:
        """Verificar si usuario está autenticado"""
        return st.session_state.get("authenticated", False)
    
    def get_user_role(self) -> UserRole:
        """Obtener rol del usuario actual"""
        return st.session_state.get("user_role", UserRole.TRABAJADOR)
    
    def get_user_id(self) -> str:
        """Obtener ID del usuario actual"""
        return st.session_state.get("user_id", "")
    
    def tiene_permiso(self, recurso: str, accion: str) -> bool:
        """Verificar permisos según rol y recurso"""
        rol = self.get_user_role()
        
        # ADMIN tiene acceso total
        if rol == UserRole.ADMIN:
            return True
        
        # Matriz de permisos
        permisos = {
            "trabajadores": {
                UserRole.RESPONSABLE_SST: ["crear", "leer", "editar"],
                UserRole.SUPERVISOR: ["leer", "leer_equipo"],
                UserRole.TRABAJADOR: ["leer_propio"],
                UserRole.AUDITOR: ["leer"]
            },
            "incidentes": {
                UserRole.RESPONSABLE_SST: ["crear", "leer", "editar"],
                UserRole.SUPERVISOR: ["crear", "leer"],
                UserRole.TRABAJADOR: ["crear_propio"],
                UserRole.AUDITOR: ["leer"]
            },
            "peligros": {
                UserRole.RESPONSABLE_SST: ["crear", "leer", "editar"],
                UserRole.AUDITOR: ["leer"]
            },
            "auditorias": {
                UserRole.RESPONSABLE_SST: ["crear", "leer"],
                UserRole.AUDITOR: ["leer", "ejecutar"]
            },
            "configuracion": {
                UserRole.RESPONSABLE_SST: ["leer"]
            }
        }
        
        permisos_recurso = permisos.get(recurso, {})
        permisos_rol = permisos_recurso.get(rol, [])
        
        return accion in permisos_rol
    
    def registrar_auditoria(self, accion: str, coleccion: str, documento_id: str, 
                           valor_anterior: Dict = None, valor_nuevo: Dict = None):
        """Registrar cambios en auditoría"""
        audit_data = {
            "usuario_id": self.get_user_id(),
            "usuario_email": st.session_state.get("user_email", ""),
            "accion": accion,
            "coleccion": coleccion,
            "documento_id": documento_id,
            "valor_anterior": valor_anterior,
            "valor_nuevo": valor_nuevo,
            "timestamp": datetime.now()
        }
        
        self.db.collection("auditoria_cambios").add(audit_data)
    
    def reset_password(self, email: str) -> Tuple[bool, str]:
        """Enviar correo de recuperación"""
        try:
            auth.generate_password_reset_link(email)
            return True, f"Enlace de recuperación enviado a {email}"
        except Exception as e:
            return False, f"Error: {str(e)}"

auth_manager = AuthManager()