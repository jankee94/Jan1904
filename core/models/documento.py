# core/models/documento.py
from typing import Optional, List, Dict
from dataclasses import dataclass, field
from datetime import datetime
from core.models.base import BaseModel

@dataclass
class Documento(BaseModel):
    """Modelo de Documento del SG-SST"""
    empresa_id: str = ""
    codigo: str = ""
    titulo: str = ""
    tipo: str = ""  # politica, procedimiento, instructivo, formato, manual, plan, registro, certificado, informe
    categoria: str = ""  # sst, legal, capacitacion, incidentes, peligros, auditoria
    version: str = "1.0"
    fecha_creacion: str = ""
    fecha_aprobacion: str = ""
    fecha_revision: str = ""
    fecha_vencimiento: str = ""
    creado_por: str = ""
    aprobado_por: str = ""
    revisado_por: str = ""
    area_responsable: str = ""
    palabras_clave: List[str] = field(default_factory=list)
    descripcion: str = ""
    contenido: str = ""  # texto del documento
    archivo_url: str = ""
    archivo_nombre: str = ""
    archivo_tipo: str = ""
    historial_versiones: List[Dict] = field(default_factory=list)  # [{version, fecha, cambios, aprobado_por}]
    firmas: List[Dict] = field(default_factory=list)  # [{nombre, cargo, fecha_firma, firma_url}]
    requiere_firma: bool = False
    requiere_aprobacion: bool = True
    estado: str = "borrador"  # borrador, revision, aprobado, obsoleto
    visible_para: List[str] = field(default_factory=list)  # roles que pueden ver
    tags: List[str] = field(default_factory=list)
    notificaciones: List[str] = field(default_factory=list)

@dataclass
class ControlCambio(BaseModel):
    """Modelo de Control de Cambios"""
    documento_id: str = ""
    documento_codigo: str = ""
    version_anterior: str = ""
    version_nueva: str = ""
    fecha_cambio: str = ""
    realizado_por: str = ""
    cambios_realizados: str = ""
    justificacion: str = ""
    aprobado_por: str = ""
    fecha_aprobacion: str = ""

@dataclass
class AprobacionDocumento(BaseModel):
    """Modelo de Aprobación de Documento"""
    documento_id: str = ""
    documento_codigo: str = ""
    aprobador_id: str = ""
    aprobador_nombre: str = ""
    aprobador_cargo: str = ""
    fecha_aprobacion: str = ""
    comentario: str = ""
    firma_url: str = ""
    estado: str = "pendiente"  # pendiente, aprobado, rechazado
