# core/services/alert_service.py
import streamlit as st
from datetime import datetime, timedelta
from typing import List, Dict

class AlertService:
    """Servicio para gestión de alertas y notificaciones"""
    
    def __init__(self):
        if "alertas" not in st.session_state:
            st.session_state.alertas = []
    
    def crear_alerta(self, titulo: str, descripcion: str, tipo: str, fecha_vencimiento: str, 
                     modulo: str, documento_id: str = "", empresa_id: str = ""):
        """Crear nueva alerta"""
        alerta = {
            "id": len(st.session_state.alertas) + 1,
            "titulo": titulo,
            "descripcion": descripcion,
            "tipo": tipo,  # warning, danger, info, success
            "fecha_creacion": datetime.now().isoformat(),
            "fecha_vencimiento": fecha_vencimiento,
            "modulo": modulo,
            "documento_id": documento_id,
            "empresa_id": empresa_id or st.session_state.get("empresa_id", ""),
            "leida": False,
            "activa": True
        }
        st.session_state.alertas.append(alerta)
    
    def obtener_alertas_activas(self, empresa_id: str = None) -> List[Dict]:
        """Obtener alertas activas"""
        alertas = [a for a in st.session_state.alertas if a.get("activa", True)]
        
        if empresa_id:
            alertas = [a for a in alertas if a.get("empresa_id") == empresa_id]
        
        # Ordenar por fecha
        alertas.sort(key=lambda x: x.get("fecha_vencimiento", ""))
        
        return alertas
    
    def marcar_leida(self, alerta_id: int):
        """Marcar alerta como leída"""
        for a in st.session_state.alertas:
            if a["id"] == alerta_id:
                a["leida"] = True
                break
    
    def cerrar_alerta(self, alerta_id: int):
        """Cerrar alerta"""
        for a in st.session_state.alertas:
            if a["id"] == alerta_id:
                a["activa"] = False
                break
    
    def verificar_vencimientos(self):
        """Verificar y generar alertas por vencimientos"""
        hoy = datetime.now().date()
        
        # Verificar documentos vencidos
        for doc in st.session_state.get("documentos", []):
            fecha_venc = doc.get("fecha_vencimiento")
            if fecha_venc:
                fecha_obj = datetime.strptime(fecha_venc, "%Y-%m-%d").date()
                dias = (fecha_obj - hoy).days
                
                if dias < 0:
                    self.crear_alerta(
                        f"Documento vencido: {doc.get('titulo')}",
                        f"El documento {doc.get('codigo')} venció el {fecha_venc}",
                        "danger", fecha_venc, "documentos", str(doc.get("id"))
                    )
                elif dias <= 30:
                    self.crear_alerta(
                        f"Documento por vencer: {doc.get('titulo')}",
                        f"El documento {doc.get('codigo')} vence en {dias} días",
                        "warning", fecha_venc, "documentos", str(doc.get("id"))
                    )

alert_service = AlertService()
