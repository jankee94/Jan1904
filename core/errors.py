# core/errors.py
import streamlit as st

class SGSTError(Exception):
    """Excepción base del sistema"""
    pass

class AuthError(SGSTError):
    """Error de autenticación"""
    pass

class ValidationError(SGSTError):
    """Error de validación"""
    pass

class DatabaseError(SGSTError):
    """Error de base de datos"""
    pass

class IAError(SGSTError):
    """Error de IA"""
    pass

def handle_error(error: Exception):
    """Manejar errores de forma amigable"""
    if isinstance(error, AuthError):
        st.error("🔐 Error de autenticación. Por favor inicia sesión nuevamente.")
    elif isinstance(error, ValidationError):
        st.error(f"📋 Error de validación: {str(error)}")
    elif isinstance(error, DatabaseError):
        st.error("💾 Error de base de datos. Contacta a soporte.")
    elif isinstance(error, IAError):
        st.error("🤖 Error de IA. Intenta nuevamente.")
    else:
        st.error(f"❌ Error inesperado: {str(error)}")
    
    # Loggear error
    from core.logger import logger
    logger.error(f"{type(error).__name__}: {str(error)}")