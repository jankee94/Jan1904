# core/services/documento_service.py
import streamlit as st
from typing import Optional, List, Dict
from datetime import datetime, timedelta
import io
import json
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from docx import Document
from docx.shared import Inches, Pt
import pandas as pd

from firebase.firestore.client import firestore_client
from firebase.storage.storage_service import storage_service
from config.settings import settings

class DocumentoService:
    """Servicio para gestión documental"""
    
    def __init__(self):
        self.collection = "documentos"
        self.controles_collection = "controles_cambio"
    
    # ========== CRUD DOCUMENTOS ==========
    def create_documento(self, data: Dict) -> Optional[str]:
        """Crear nuevo documento"""
        data["created_at"] = datetime.now().isoformat()
        data["updated_at"] = datetime.now().isoformat()
        data["estado"] = "borrador"
        data["historial_versiones"] = [{
            "version": "1.0",
            "fecha": datetime.now().isoformat(),
            "cambios": "Creación inicial",
            "aprobado_por": data.get("creado_por", "")
        }]
        
        return firestore_client.create(self.collection, data)
    
    def get_documentos(self, empresa_id: str = None, tipo: str = None, 
                       estado: str = None, categoria: str = None) -> List[Dict]:
        """Obtener documentos con filtros"""
        filters = []
        if empresa_id:
            filters.append(["empresa_id", "==", empresa_id])
        if tipo:
            filters.append(["tipo", "==", tipo])
        if estado:
            filters.append(["estado", "==", estado])
        if categoria:
            filters.append(["categoria", "==", categoria])
        
        return firestore_client.query(self.collection, filters=filters, order_by="fecha_creacion")
    
    def get_documento(self, documento_id: str) -> Optional[Dict]:
        """Obtener documento por ID"""
        return firestore_client.read(self.collection, documento_id)
    
    def update_documento(self, documento_id: str, data: Dict) -> bool:
        """Actualizar documento"""
        data["updated_at"] = datetime.now().isoformat()
        return firestore_client.update(self.collection, documento_id, data)
    
    def delete_documento(self, documento_id: str) -> bool:
        """Eliminar documento (soft delete)"""
        return firestore_client.delete(self.collection, documento_id)
    
    # ========== VERSIONAMIENTO ==========
    def crear_nueva_version(self, documento_id: str, cambios: str, realizado_por: str) -> bool:
        """Crear nueva versión de un documento"""
        doc = self.get_documento(documento_id)
        if not doc:
            return False
        
        version_actual = doc.get("version", "1.0")
        partes = version_actual.split(".")
        nueva_version = f"{partes[0]}.{int(partes[1]) + 1}" if len(partes) > 1 else f"{int(partes[0]) + 1}.0"
        
        # Registrar control de cambio
        control = {
            "documento_id": documento_id,
            "documento_codigo": doc.get("codigo", ""),
            "version_anterior": version_actual,
            "version_nueva": nueva_version,
            "fecha_cambio": datetime.now().isoformat(),
            "realizado_por": realizado_por,
            "cambios_realizados": cambios,
            "estado": "pendiente"
        }
        firestore_client.create(self.controles_collection, control)
        
        # Actualizar documento
        historial = doc.get("historial_versiones", [])
        historial.append({
            "version": nueva_version,
            "fecha": datetime.now().isoformat(),
            "cambios": cambios,
            "aprobado_por": realizado_por
        })
        
        return self.update_documento(documento_id, {
            "version": nueva_version,
            "historial_versiones": historial,
            "estado": "revision"
        })
    
    def aprobar_version(self, documento_id: str, aprobado_por: str, comentario: str = "") -> bool:
        """Aprobar una versión de documento"""
        doc = self.get_documento(documento_id)
        if not doc:
            return False
        
        return self.update_documento(documento_id, {
            "estado": "aprobado",
            "fecha_aprobacion": datetime.now().isoformat(),
            "aprobado_por": aprobado_por
        })
    
    # ========== FIRMAS ==========
    def agregar_firma(self, documento_id: str, firmante_nombre: str, 
                      firmante_cargo: str, firma_url: str) -> bool:
        """Agregar firma a documento"""
        doc = self.get_documento(documento_id)
        if not doc:
            return False
        
        firmas = doc.get("firmas", [])
        firmas.append({
            "nombre": firmante_nombre,
            "cargo": firmante_cargo,
            "fecha_firma": datetime.now().isoformat(),
            "firma_url": firma_url
        })
        
        return self.update_documento(documento_id, {"firmas": firmas})
    
    def verificar_firmas_completas(self, documento_id: str) -> bool:
        """Verificar si el documento tiene todas las firmas requeridas"""
        doc = self.get_documento(documento_id)
        if not doc:
            return False
        
        requiere_firma = doc.get("requiere_firma", False)
        firmas = doc.get("firmas", [])
        
        if not requiere_firma:
            return True
        
        # Por ahora, asumimos que se necesita al menos una firma
        return len(firmas) > 0
    
    # ========== VENCIMIENTOS ==========
    def get_documentos_por_vencer(self, empresa_id: str = None, dias: int = 30) -> List[Dict]:
        """Obtener documentos que vencen próximamente"""
        documentos = self.get_documentos(empresa_id)
        hoy = datetime.now().date()
        fecha_limite = hoy + timedelta(days=dias)
        
        por_vencer = []
        for doc in documentos:
            fecha_vencimiento = doc.get("fecha_vencimiento")
            if fecha_vencimiento:
                fecha_obj = datetime.strptime(fecha_vencimiento, "%Y-%m-%d").date()
                if hoy <= fecha_obj <= fecha_limite:
                    por_vencer.append(doc)
        
        return por_vencer
    
    def get_documentos_vencidos(self, empresa_id: str = None) -> List[Dict]:
        """Obtener documentos vencidos"""
        documentos = self.get_documentos(empresa_id)
        hoy = datetime.now().date()
        
        vencidos = []
        for doc in documentos:
            fecha_vencimiento = doc.get("fecha_vencimiento")
            if fecha_vencimiento:
                fecha_obj = datetime.strptime(fecha_vencimiento, "%Y-%m-%d").date()
                if fecha_obj < hoy:
                    vencidos.append(doc)
        
        return vencidos
    
    # ========== GENERACIÓN DE DOCUMENTOS ==========
    def generar_documento_word(self, documento_id: str) -> Optional[bytes]:
        """Generar documento Word a partir de plantilla"""
        try:
            doc = self.get_documento(documento_id)
            if not doc:
                return None
            
            document = Document()
            
            # Título
            title = document.add_heading(doc.get("titulo", "Documento SST"), 0)
            title.alignment = 1
            
            # Código y versión
            document.add_paragraph(f"Código: {doc.get('codigo', 'N/A')}")
            document.add_paragraph(f"Versión: {doc.get('version', '1.0')}")
            document.add_paragraph(f"Fecha: {doc.get('fecha_creacion', datetime.now().strftime('%Y-%m-%d'))}")
            document.add_paragraph("")
            
            # Contenido
            document.add_heading("Contenido", level=1)
            for linea in doc.get("contenido", "").split("\n"):
                document.add_paragraph(linea)
            
            # Firmas
            firmas = doc.get("firmas", [])
            if firmas:
                document.add_heading("Firmas", level=1)
                for f in firmas:
                    document.add_paragraph(f"Nombre: {f.get('nombre', 'N/A')}")
                    document.add_paragraph(f"Cargo: {f.get('cargo', 'N/A')}")
                    document.add_paragraph(f"Fecha: {f.get('fecha_firma', 'N/A')[:10]}")
                    document.add_paragraph("")
            
            # Guardar en buffer
            buffer = io.BytesIO()
            document.save(buffer)
            buffer.seek(0)
            
            return buffer.getvalue()
        except Exception as e:
            st.error(f"Error generando Word: {e}")
            return None
    
    def exportar_documentos_excel(self, documentos: List[Dict]) -> Optional[bytes]:
        """Exportar lista de documentos a Excel"""
        try:
            data = []
            for doc in documentos:
                data.append({
                    "Código": doc.get("codigo", ""),
                    "Título": doc.get("titulo", ""),
                    "Tipo": doc.get("tipo", ""),
                    "Categoría": doc.get("categoria", ""),
                    "Versión": doc.get("version", ""),
                    "Estado": doc.get("estado", ""),
                    "Fecha Creación": doc.get("fecha_creacion", ""),
                    "Fecha Vencimiento": doc.get("fecha_vencimiento", ""),
                    "Responsable": doc.get("area_responsable", "")
                })
            
            df = pd.DataFrame(data)
            output = io.BytesIO()
            with pd.ExcelWriter(output, engine='openpyxl') as writer:
                df.to_excel(writer, sheet_name="Documentos", index=False)
            
            return output.getvalue()
        except Exception as e:
            st.error(f"Error exportando: {e}")
            return None

documento_service = DocumentoService()
