# core/services/emergencia_service.py
import streamlit as st
from typing import Optional, List, Dict
from datetime import datetime, timedelta
import io
import pandas as pd
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet

from firebase.firestore.client import firestore_client
from firebase.storage.storage_service import storage_service
from config.settings import settings

class EmergenciaService:
    """Servicio para gestión de emergencias"""
    
    def __init__(self):
        self.brigadistas_collection = "brigadistas"
        self.equipos_collection = "equipos_emergencia"
        self.simulacros_collection = "simulacros"
        self.plan_emergencia_collection = "plan_emergencia"
        self.alertas_collection = "alertas_emergencia"
    
    # ========== BRIGADISTAS ==========
    def create_brigadista(self, data: Dict) -> Optional[str]:
        data["created_at"] = datetime.now().isoformat()
        data["activo"] = True
        return firestore_client.create(self.brigadistas_collection, data)
    
    def get_brigadistas(self, empresa_id: str = None) -> List[Dict]:
        filters = [["empresa_id", "==", empresa_id]] if empresa_id else []
        return firestore_client.query(self.brigadistas_collection, filters=filters)
    
    def update_brigadista(self, brigadista_id: str, data: Dict) -> bool:
        data["updated_at"] = datetime.now().isoformat()
        return firestore_client.update(self.brigadistas_collection, brigadista_id, data)
    
    def delete_brigadista(self, brigadista_id: str) -> bool:
        return firestore_client.delete(self.brigadistas_collection, brigadista_id)
    
    # ========== EQUIPOS ==========
    def create_equipo(self, data: Dict) -> Optional[str]:
        data["created_at"] = datetime.now().isoformat()
        return firestore_client.create(self.equipos_collection, data)
    
    def get_equipos(self, empresa_id: str = None, estado: str = None) -> List[Dict]:
        filters = []
        if empresa_id:
            filters.append(["empresa_id", "==", empresa_id])
        if estado:
            filters.append(["estado", "==", estado])
        return firestore_client.query(self.equipos_collection, filters=filters)
    
    def update_equipo(self, equipo_id: str, data: Dict) -> bool:
        data["updated_at"] = datetime.now().isoformat()
        return firestore_client.update(self.equipos_collection, equipo_id, data)
    
    def get_equipos_vencidos(self, empresa_id: str = None) -> List[Dict]:
        equipos = self.get_equipos(empresa_id)
        hoy = datetime.now().date()
        vencidos = []
        for e in equipos:
            fecha_mantenimiento = e.get("fecha_proximo_mantenimiento")
            if fecha_mantenimiento:
                fecha_obj = datetime.strptime(fecha_mantenimiento, "%Y-%m-%d").date()
                if fecha_obj < hoy:
                    vencidos.append(e)
        return vencidos
    
    # ========== SIMULACROS ==========
    def create_simulacro(self, data: Dict) -> Optional[str]:
        data["created_at"] = datetime.now().isoformat()
        return firestore_client.create(self.simulacros_collection, data)
    
    def get_simulacros(self, empresa_id: str = None) -> List[Dict]:
        filters = [["empresa_id", "==", empresa_id]] if empresa_id else []
        return firestore_client.query(self.simulacros_collection, filters=filters, order_by="fecha")
    
    def get_estadisticas_simulacros(self, empresa_id: str = None) -> Dict:
        simulacros = self.get_simulacros(empresa_id)
        if not simulacros:
            return {"total": 0, "promedio_participantes": 0, "promedio_tiempo": 0}
        
        total = len(simulacros)
        total_participantes = sum(s.get("participantes", 0) for s in simulacros)
        total_tiempo = sum(s.get("tiempo_evacuacion", 0) for s in simulacros)
        
        return {
            "total": total,
            "promedio_participantes": total_participantes // total if total > 0 else 0,
            "promedio_tiempo": total_tiempo // total if total > 0 else 0
        }
    
    # ========== PLAN DE EMERGENCIA ==========
    def save_plan_emergencia(self, data: Dict) -> Optional[str]:
        # Buscar plan existente
        existing = firestore_client.query(self.plan_emergencia_collection, 
                                          filters=[["empresa_id", "==", data.get("empresa_id")]])
        if existing:
            return firestore_client.update(self.plan_emergencia_collection, existing[0]["id"], data)
        return firestore_client.create(self.plan_emergencia_collection, data)
    
    def get_plan_emergencia(self, empresa_id: str) -> Optional[Dict]:
        results = firestore_client.query(self.plan_emergencia_collection, 
                                         filters=[["empresa_id", "==", empresa_id]])
        return results[0] if results else None
    
    # ========== ALERTAS ==========
    def create_alerta(self, data: Dict) -> Optional[str]:
        data["created_at"] = datetime.now().isoformat()
        data["estado"] = "activa"
        return firestore_client.create(self.alertas_collection, data)
    
    def get_alertas_activas(self, empresa_id: str = None) -> List[Dict]:
        filters = [["estado", "==", "activa"]]
        if empresa_id:
            filters.append(["empresa_id", "==", empresa_id])
        return firestore_client.query(self.alertas_collection, filters=filters, order_by="fecha_hora")
    
    def cerrar_alerta(self, alerta_id: str, cerrada_por: str) -> bool:
        return firestore_client.update(self.alertas_collection, alerta_id, {
            "estado": "resuelta",
            "cerrada_por": cerrada_por,
            "fecha_cierre": datetime.now().isoformat()
        })
    
    # ========== REPORTES ==========
    def generar_reporte_emergencias(self, empresa_id: str) -> Optional[bytes]:
        brigadistas = self.get_brigadistas(empresa_id)
        equipos = self.get_equipos(empresa_id)
        simulacros = self.get_simulacros(empresa_id)
        
        data = []
        for b in brigadistas:
            data.append({
                "Tipo": "Brigadista",
                "Nombre": b.get("nombre"),
                "Cédula": b.get("cedula"),
                "Tipo Brigada": ", ".join(b.get("tipo_brigada", [])),
                "Estado": "Activo" if b.get("activo") else "Inactivo"
            })
        
        for e in equipos:
            data.append({
                "Tipo": "Equipo",
                "Nombre": e.get("codigo"),
                "Ubicación": e.get("ubicacion"),
                "Estado": e.get("estado"),
                "Próximo Mantenimiento": e.get("fecha_proximo_mantenimiento", "N/A")
            })
        
        for s in simulacros:
            data.append({
                "Tipo": "Simulacro",
                "Nombre": s.get("tipo"),
                "Fecha": s.get("fecha"),
                "Participantes": s.get("participantes", 0),
                "Tiempo Evacuación": f"{s.get('tiempo_evacuacion', 0)} seg"
            })
        
        df = pd.DataFrame(data)
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name="Emergencias", index=False)
        
        return output.getvalue()

emergencia_service = EmergenciaService()
