# core/services/log_service.py
import streamlit as st
from datetime import datetime
from typing import Optional
import streamlit as st

class LogService:
    """Servicio para registro de auditoría y bitácora"""
    
    def __init__(self):
        pass
    
    def registrar(self, accion: str, modulo: str, documento_id: str = "", 
                  valor_anterior: str = "", valor_nuevo: str = "", empresa_id: str = ""):
        """Registrar acción en la bitácora"""
        try:
            log_entry = {
                "usuario_id": st.session_state.get("user_uid", ""),
                "usuario_email": st.session_state.get("user_email", ""),
                "usuario_nombre": st.session_state.get("user_nombre", ""),
                "empresa_id": empresa_id or st.session_state.get("empresa_id", ""),
                "accion": accion,
                "modulo": modulo,
                "documento_id": documento_id,
                "valor_anterior": valor_anterior,
                "valor_nuevo": valor_nuevo,
                "fecha": datetime.now().isoformat(),
                "ip": st.request.headers.get("X-Forwarded-For", "unknown") if hasattr(st, 'request') else "unknown"
            }
            
            # Guardar en session state para debug
            if "logs" not in st.session_state:
                st.session_state.logs = []
            st.session_state.logs.insert(0, log_entry)
            
            # Mantener solo últimos 100 logs
            st.session_state.logs = st.session_state.logs[:100]
            
        except Exception as e:
            pass
    
    def obtener_logs(self, empresa_id: str = None, modulo: str = None, limite: int = 50) -> list:
        """Obtener logs filtrados"""
        logs = st.session_state.get("logs", [])
        
        if empresa_id:
            logs = [l for l in logs if l.get("empresa_id") == empresa_id]
        if modulo:
            logs = [l for l in logs if l.get("modulo") == modulo]
        
        return logs[:limite]

log_service = LogService()
