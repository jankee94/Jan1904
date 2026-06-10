# core/services/capacitacion_service.py
import streamlit as st
from typing import Optional, List, Dict
from datetime import datetime
import io
import base64
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.pdfgen import canvas
import pandas as pd
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment

from firebase.firestore.client import firestore_client
from firebase.storage.storage_service import storage_service
from config.settings import settings

class CapacitacionService:
    """Servicio para gestión de capacitaciones"""
    
    def __init__(self):
        self.collection = settings.COLLECTIONS.get("capacitaciones", "capacitaciones")
    
    def create_capacitacion(self, data: Dict) -> Optional[str]:
        """Crear nueva capacitación"""
        try:
            data["created_at"] = datetime.now().isoformat()
            data["updated_at"] = datetime.now().isoformat()
            data["estado"] = "programada"
            data["asistentes"] = []
            data["cupo_disponible"] = data.get("cupo_maximo", 0)
            
            doc_id = firestore_client.create(self.collection, data)
            return doc_id
        except Exception as e:
            st.error(f"Error creando capacitación: {e}")
            return None
    
    def get_capacitaciones(self, empresa_id: str = None, estado: str = None) -> List[Dict]:
        """Obtener capacitaciones con filtros"""
        try:
            filters = []
            if empresa_id:
                filters.append(["empresa_id", "==", empresa_id])
            if estado:
                filters.append(["estado", "==", estado])
            
            return firestore_client.query(self.collection, filters=filters, order_by="fecha_inicio")
        except Exception as e:
            st.error(f"Error obteniendo capacitaciones: {e}")
            return []
    
    def get_capacitacion(self, capacitacion_id: str) -> Optional[Dict]:
        """Obtener capacitación por ID"""
        try:
            return firestore_client.read(self.collection, capacitacion_id)
        except Exception as e:
            st.error(f"Error obteniendo capacitación: {e}")
            return None
    
    def update_capacitacion(self, capacitacion_id: str, data: Dict) -> bool:
        """Actualizar capacitación"""
        try:
            data["updated_at"] = datetime.now().isoformat()
            return firestore_client.update(self.collection, capacitacion_id, data)
        except Exception as e:
            st.error(f"Error actualizando capacitación: {e}")
            return False
    
    def delete_capacitacion(self, capacitacion_id: str) -> bool:
        """Eliminar capacitación (soft delete)"""
        try:
            return firestore_client.delete(self.collection, capacitacion_id)
        except Exception as e:
            st.error(f"Error eliminando capacitación: {e}")
            return False
    
    def registrar_asistencia(self, capacitacion_id: str, trabajador_id: str, trabajador_nombre: str, 
                            trabajador_cedula: str, firma_data: str = None) -> bool:
        """Registrar asistencia de trabajador"""
        try:
            capacitacion = self.get_capacitacion(capacitacion_id)
            if not capacitacion:
                return False
            
            # Subir firma si existe
            firma_url = None
            if firma_data:
                firma_bytes = base64.b64decode(firma_data.split(",")[1])
                firma_path = f"firmas/capacitaciones/{capacitacion_id}/{trabajador_id}_{datetime.now().strftime('%Y%m%d%H%M%S')}.png"
                firma_url = storage_service.upload_bytes(firma_bytes, firma_path, "image/png")
            
            asistencia = {
                "trabajador_id": trabajador_id,
                "trabajador_nombre": trabajador_nombre,
                "trabajador_cedula": trabajador_cedula,
                "fecha_asistencia": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "asistio": True,
                "firma_url": firma_url,
                "certificado_generado": False
            }
            
            asistentes = capacitacion.get("asistentes", [])
            # Verificar si ya existe
            existente = False
            for i, a in enumerate(asistentes):
                if a.get("trabajador_id") == trabajador_id:
                    asistentes[i] = asistencia
                    existente = True
                    break
            if not existente:
                asistentes.append(asistencia)
            
            # Actualizar cupo disponible
            cupo_disponible = capacitacion.get("cupo_disponible", capacitacion.get("cupo_maximo", 0))
            if not existente:
                cupo_disponible -= 1
            
            return self.update_capacitacion(capacitacion_id, {
                "asistentes": asistentes,
                "cupo_disponible": cupo_disponible
            })
        except Exception as e:
            st.error(f"Error registrando asistencia: {e}")
            return False
    
    def registrar_evaluacion(self, capacitacion_id: str, trabajador_id: str, nota: float, 
                            comentario: str = "", respuestas: List[Dict] = None) -> bool:
        """Registrar evaluación de trabajador"""
        try:
            capacitacion = self.get_capacitacion(capacitacion_id)
            if not capacitacion:
                return False
            
            asistentes = capacitacion.get("asistentes", [])
            for i, a in enumerate(asistentes):
                if a.get("trabajador_id") == trabajador_id:
                    asistentes[i]["evaluacion_nota"] = nota
                    asistentes[i]["evaluacion_comentario"] = comentario
                    asistentes[i]["evaluacion_respuestas"] = respuestas
                    asistentes[i]["evaluacion_fecha"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    
                    # Generar certificado si aprobó
                    nota_aprobacion = capacitacion.get("nota_aprobacion", 70)
                    if nota >= nota_aprobacion and capacitacion.get("certificado_automatico", True):
                        certificado_url = self.generar_certificado(capacitacion, a)
                        asistentes[i]["certificado_url"] = certificado_url
                        asistentes[i]["certificado_generado"] = True
                    break
            
            return self.update_capacitacion(capacitacion_id, {"asistentes": asistentes})
        except Exception as e:
            st.error(f"Error registrando evaluación: {e}")
            return False
    
    def generar_certificado(self, capacitacion: Dict, asistente: Dict) -> Optional[str]:
        """Generar certificado PDF"""
        try:
            buffer = io.BytesIO()
            doc = SimpleDocTemplate(buffer, pagesize=A4)
            styles = getSampleStyleSheet()
            
            # Estilo personalizado
            title_style = ParagraphStyle(
                'CustomTitle',
                parent=styles['Heading1'],
                fontSize=24,
                textColor=colors.HexColor('#1a365d'),
                alignment=1,
                spaceAfter=30
            )
            
            content = []
            
            # Título
            content.append(Paragraph("CERTIFICADO DE PARTICIPACIÓN", title_style))
            content.append(Spacer(1, 20))
            
            # Texto del certificado
            text_style = ParagraphStyle(
                'CustomText',
                parent=styles['Normal'],
                fontSize=12,
                alignment=1
            )
            
            content.append(Paragraph(f"El presente certificado se otorga a:", text_style))
            content.append(Spacer(1, 10))
            content.append(Paragraph(f"<b>{asistente.get('trabajador_nombre', '')}</b>", title_style))
            content.append(Spacer(1, 10))
            content.append(Paragraph(f"Con cédula {asistente.get('trabajador_cedula', '')}", text_style))
            content.append(Spacer(1, 20))
            content.append(Paragraph(f"Por haber participado en la capacitación:", text_style))
            content.append(Spacer(1, 10))
            content.append(Paragraph(f"<b>{capacitacion.get('titulo', '')}</b>", text_style))
            content.append(Spacer(1, 10))
            content.append(Paragraph(f"Con una duración de {capacitacion.get('duracion_horas', 0)} horas", text_style))
            
            if asistente.get("evaluacion_nota", 0) > 0:
                content.append(Spacer(1, 10))
                content.append(Paragraph(f"Nota obtenida: {asistente.get('evaluacion_nota', 0)}%", text_style))
            
            content.append(Spacer(1, 30))
            content.append(Paragraph(f"Fecha: {datetime.now().strftime('%d/%m/%Y')}", text_style))
            
            doc.build(content)
            
            # Subir a Storage
            buffer.seek(0)
            certificado_path = f"certificados/capacitaciones/{capacitacion.get('id')}/{asistente.get('trabajador_id')}_{datetime.now().strftime('%Y%m%d')}.pdf"
            certificado_url = storage_service.upload_bytes(buffer.getvalue(), certificado_path, "application/pdf")
            
            return certificado_url
        except Exception as e:
            st.error(f"Error generando certificado: {e}")
            return None
    
    def exportar_asistentes_excel(self, capacitacion_id: str) -> Optional[bytes]:
        """Exportar lista de asistentes a Excel"""
        try:
            capacitacion = self.get_capacitacion(capacitacion_id)
            if not capacitacion:
                return None
            
            asistentes = capacitacion.get("asistentes", [])
            df = pd.DataFrame(asistentes)
            
            output = io.BytesIO()
            with pd.ExcelWriter(output, engine='openpyxl') as writer:
                df.to_excel(writer, sheet_name="Asistentes", index=False)
            
            return output.getvalue()
        except Exception as e:
            st.error(f"Error exportando asistentes: {e}")
            return None

capacitacion_service = CapacitacionService()
