# core/services/inspeccion_service.py
import streamlit as st
from typing import Optional, List, Dict
from datetime import datetime
import io
import pandas as pd
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet

from firebase.firestore.client import firestore_client
from firebase.storage.storage_service import storage_service
from config.settings import settings
from core.data.checklists_predefinidos import CHECKLISTS_PREDEFINIDOS

class InspeccionService:
    """Servicio para gestión de inspecciones"""
    
    def __init__(self):
        self.collection = "inspecciones"
    
    def get_checklist_predefinido(self, tipo: str) -> Dict:
        """Obtener checklist predefinido por tipo"""
        return CHECKLISTS_PREDEFINIDOS.get(tipo, {})
    
    def get_tipos_inspeccion(self) -> List[str]:
        """Obtener tipos de inspección disponibles"""
        return list(CHECKLISTS_PREDEFINIDOS.keys())
    
    def create_inspeccion(self, data: Dict) -> Optional[str]:
        """Crear nueva inspección"""
        try:
            data["created_at"] = datetime.now().isoformat()
            data["updated_at"] = datetime.now().isoformat()
            data["estado"] = "programada"
            data["hallazgos"] = []
            data["checklist"] = data.get("checklist", [])
            
            doc_id = firestore_client.create(self.collection, data)
            return doc_id
        except Exception as e:
            st.error(f"Error creando inspección: {e}")
            return None
    
    def get_inspecciones(self, empresa_id: str = None, estado: str = None) -> List[Dict]:
        """Obtener inspecciones con filtros"""
        try:
            filters = []
            if empresa_id:
                filters.append(["empresa_id", "==", empresa_id])
            if estado:
                filters.append(["estado", "==", estado])
            
            return firestore_client.query(self.collection, filters=filters, order_by="fecha_programada")
        except Exception as e:
            st.error(f"Error obteniendo inspecciones: {e}")
            return []
    
    def get_inspeccion(self, inspeccion_id: str) -> Optional[Dict]:
        """Obtener inspección por ID"""
        try:
            return firestore_client.read(self.collection, inspeccion_id)
        except Exception as e:
            st.error(f"Error obteniendo inspección: {e}")
            return None
    
    def update_inspeccion(self, inspeccion_id: str, data: Dict) -> bool:
        """Actualizar inspección"""
        try:
            data["updated_at"] = datetime.now().isoformat()
            return firestore_client.update(self.collection, inspeccion_id, data)
        except Exception as e:
            st.error(f"Error actualizando inspección: {e}")
            return False
    
    def registrar_checklist(self, inspeccion_id: str, checklist: List[Dict]) -> bool:
        """Registrar checklist de inspección"""
        try:
            cumplimiento = sum(1 for c in checklist if c.get("cumple"))
            total = len(checklist)
            calificacion = (cumplimiento / total) * 100 if total > 0 else 0
            
            return self.update_inspeccion(inspeccion_id, {
                "checklist": checklist,
                "calificacion": calificacion
            })
        except Exception as e:
            st.error(f"Error registrando checklist: {e}")
            return False
    
    def registrar_hallazgo(self, inspeccion_id: str, hallazgo: Dict) -> bool:
        """Registrar hallazgo y generar acción automática"""
        try:
            inspeccion = self.get_inspeccion(inspeccion_id)
            if not inspeccion:
                return False
            
            hallazgo["id"] = datetime.now().strftime("%Y%m%d%H%M%S")
            hallazgo["created_at"] = datetime.now().isoformat()
            hallazgo["estado"] = "abierto"
            
            hallazgos = inspeccion.get("hallazgos", [])
            hallazgos.append(hallazgo)
            
            # Generar acción correctiva automática
            if hallazgo.get("tipo") in ["critico", "grave"]:
                accion = {
                    "descripcion": f"Corregir hallazgo: {hallazgo.get('descripcion')}",
                    "responsable": hallazgo.get("responsable_nombre", ""),
                    "fecha_limite": (datetime.now().replace(day=datetime.now().day + 7)).strftime("%Y-%m-%d"),
                    "inspeccion_id": inspeccion_id,
                    "hallazgo_id": hallazgo.get("id"),
                    "created_at": datetime.now().isoformat()
                }
                # Guardar acción en colección de acciones
                firestore_client.create("acciones", accion)
                hallazgo["accion_generada"] = True
            
            return self.update_inspeccion(inspeccion_id, {"hallazgos": hallazgos})
        except Exception as e:
            st.error(f"Error registrando hallazgo: {e}")
            return False
    
    def cerrar_hallazgo(self, inspeccion_id: str, hallazgo_id: str, evidencia_url: str = None) -> bool:
        """Cerrar hallazgo"""
        try:
            inspeccion = self.get_inspeccion(inspeccion_id)
            if not inspeccion:
                return False
            
            hallazgos = inspeccion.get("hallazgos", [])
            for h in hallazgos:
                if h.get("id") == hallazgo_id:
                    h["estado"] = "cerrado"
                    h["fecha_cierre"] = datetime.now().isoformat()
                    if evidencia_url:
                        h["evidencia_cierre"] = evidencia_url
                    break
            
            return self.update_inspeccion(inspeccion_id, {"hallazgos": hallazgos})
        except Exception as e:
            st.error(f"Error cerrando hallazgo: {e}")
            return False
    
    def generar_reporte_pdf(self, inspeccion_id: str) -> Optional[bytes]:
        """Generar reporte PDF de inspección"""
        try:
            inspeccion = self.get_inspeccion(inspeccion_id)
            if not inspeccion:
                return None
            
            buffer = io.BytesIO()
            doc = SimpleDocTemplate(buffer, pagesize=letter)
            styles = getSampleStyleSheet()
            content = []
            
            # Título
            title_style = styles['Title']
            content.append(Paragraph(f"Informe de Inspección", title_style))
            content.append(Spacer(1, 12))
            
            # Datos generales
            content.append(Paragraph(f"<b>Tipo:</b> {inspeccion.get('tipo', 'N/A')}", styles['Normal']))
            content.append(Paragraph(f"<b>Ubicación:</b> {inspeccion.get('ubicacion', 'N/A')}", styles['Normal']))
            content.append(Paragraph(f"<b>Inspector:</b> {inspeccion.get('inspector_nombre', 'N/A')}", styles['Normal']))
            content.append(Paragraph(f"<b>Fecha:</b> {inspeccion.get('fecha_realizada', inspeccion.get('fecha_programada', 'N/A'))}", styles['Normal']))
            content.append(Spacer(1, 12))
            
            # Calificación
            calificacion = inspeccion.get('calificacion', 0)
            color = "#27ae60" if calificacion >= 80 else "#f39c12" if calificacion >= 60 else "#e74c3c"
            content.append(Paragraph(f"<b>Calificación:</b> {calificacion:.1f}%", styles['Normal']))
            content.append(Spacer(1, 12))
            
            # Hallazgos
            hallazgos = inspeccion.get("hallazgos", [])
            if hallazgos:
                content.append(Paragraph("<b>Hallazgos Encontrados:</b>", styles['Heading4']))
                for h in hallazgos:
                    color_tipo = "#e74c3c" if h.get("tipo") == "critico" else "#f39c12" if h.get("tipo") == "grave" else "#27ae60"
                    content.append(Paragraph(f"• <font color='{color_tipo}'><b>{h.get('tipo', 'leve').upper()}:</b></font> {h.get('descripcion', 'N/A')}", styles['Normal']))
                content.append(Spacer(1, 12))
            
            doc.build(content)
            buffer.seek(0)
            return buffer.getvalue()
        except Exception as e:
            st.error(f"Error generando reporte: {e}")
            return None
    
    def exportar_inspecciones_excel(self, inspecciones: List[Dict]) -> Optional[bytes]:
        """Exportar inspecciones a Excel"""
        try:
            data = []
            for ins in inspecciones:
                data.append({
                    "Tipo": ins.get("tipo", ""),
                    "Título": ins.get("titulo", ""),
                    "Ubicación": ins.get("ubicacion", ""),
                    "Inspector": ins.get("inspector_nombre", ""),
                    "Fecha": ins.get("fecha_realizada", ins.get("fecha_programada", "")),
                    "Calificación": ins.get("calificacion", 0),
                    "Hallazgos": len(ins.get("hallazgos", [])),
                    "Estado": ins.get("estado", "")
                })
            
            df = pd.DataFrame(data)
            output = io.BytesIO()
            with pd.ExcelWriter(output, engine='openpyxl') as writer:
                df.to_excel(writer, sheet_name="Inspecciones", index=False)
            
            return output.getvalue()
        except Exception as e:
            st.error(f"Error exportando inspecciones: {e}")
            return None

inspeccion_service = InspeccionService()
