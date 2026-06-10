# core/models/emergencia.py
from typing import Optional, List, Dict
from dataclasses import dataclass, field
from datetime import datetime
from core.models.base import BaseModel

@dataclass
class Brigadista(BaseModel):
    """Modelo de Brigadista de Emergencia"""
    empresa_id: str = ""
    nombre: str = ""
    cedula: str = ""
    cargo: str = ""
    area: str = ""
    telefono: str = ""
    email: str = ""
    tipo_brigada: List[str] = field(default_factory=list)  # primeros_auxilios, contra_incendios, evacuacion, rescate
    nivel_entrenamiento: str = "basico"  # basico, intermedio, avanzado
    fecha_entrenamiento: str = ""
    fecha_vencimiento: str = ""
    certificado_url: str = ""
    activo: bool = True
    horario: str = ""  # diurno, nocturno, ambos
    ubicacion_trabajo: str = ""

@dataclass
class EquipoEmergencia(BaseModel):
    """Modelo de Equipo de Emergencia"""
    empresa_id: str = ""
    tipo: str = ""  # extintor, botiquin, camilla, etc.
    codigo: str = ""
    ubicacion: str = ""
    estado: str = "operativo"  # operativo, mantenimiento, dañado
    fecha_ultimo_mantenimiento: str = ""
    fecha_proximo_mantenimiento: str = ""
    proveedor: str = ""
    telefono_proveedor: str = ""
    observaciones: str = ""
    fotos_urls: List[str] = field(default_factory=list)
    documentos_urls: List[str] = field(default_factory=list)

@dataclass
class Simulacro(BaseModel):
    """Modelo de Simulacro de Emergencia"""
    empresa_id: str = ""
    tipo: str = ""  # incendio, sismo, evacuacion, atentado, derrame
    fecha: str = ""
    hora_inicio: str = ""
    hora_fin: str = ""
    duracion_minutos: int = 0
    participantes: int = 0
    evacuados: int = 0
    heridos: int = 0
    tiempo_evacuacion: int = 0  # segundos
    observaciones: str = ""
    lecciones_aprendidas: List[str] = field(default_factory=list)
    recomendaciones: List[str] = field(default_factory=list)
    fotos_urls: List[str] = field(default_factory=list)
    calificacion: int = 0  # 0-100
    estado: str = "programado"  # programado, realizado, cancelado

@dataclass
class PlanEmergencia(BaseModel):
    """Modelo de Plan de Emergencia"""
    empresa_id: str = ""
    version: str = "1.0"
    fecha_aprobacion: str = ""
    fecha_revision: str = ""
    objetivo: str = ""
    alcance: str = ""
    responsables: List[Dict] = field(default_factory=list)
    brigadas: List[str] = field(default_factory=list)
    rutas_evacuacion: List[Dict] = field(default_factory=list)  # [{nombre, puntos_encuentro, mapa_url}]
    puntos_encuentro: List[Dict] = field(default_factory=list)  # [{nombre, ubicacion, capacidad}]
    recursos: List[str] = field(default_factory=list)
    procedimientos: List[Dict] = field(default_factory=list)  # [{tipo, pasos}]
    anexos_urls: List[str] = field(default_factory=list)
    aprobado_por: str = ""
    estado: str = "activo"  # activo, revision, archivado

@dataclass
class AlertaEmergencia(BaseModel):
    """Modelo de Alerta de Emergencia"""
    empresa_id: str = ""
    tipo: str = ""  # incendio, sismo, inundacion, atentado, accidente
    nivel: str = ""  # bajo, medio, alto, critico
    ubicacion: str = ""
    descripcion: str = ""
    fecha_hora: str = ""
    reportado_por: str = ""
    telefono_contacto: str = ""
    afectados: int = 0
    acciones_tomadas: str = ""
    estado: str = "activa"  # activa, controlada, resuelta
    cerrada_por: str = ""
    fecha_cierre: str = ""
