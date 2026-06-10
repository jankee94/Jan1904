# core/models/inspeccion.py
from typing import Optional, List, Dict
from dataclasses import dataclass, field
from datetime import datetime
from core.models.base import BaseModel

@dataclass
class Inspeccion(BaseModel):
    """Modelo de Inspección"""
    empresa_id: str = ""
    tipo: str = ""  # locativa, equipos, epp, vehicular, andamios, electrica
    titulo: str = ""
    descripcion: str = ""
    ubicacion: str = ""
    fecha_programada: str = ""
    fecha_realizada: str = ""
    hora_inicio: str = ""
    hora_fin: str = ""
    inspector_id: str = ""
    inspector_nombre: str = ""
    inspector_cargo: str = ""
    checklist: List[Dict] = field(default_factory=list)  # [{item, cumple, observacion, evidencia_url}]
    hallazgos: List[Dict] = field(default_factory=list)  # [{descripcion, tipo, prioridad, accion_id}]
    recomendaciones: List[str] = field(default_factory=list)
    fotos_urls: List[str] = field(default_factory=list)
    documentos_urls: List[str] = field(default_factory=list)
    calificacion: float = 0.0  # 0-100
    estado: str = "programada"  # programada, en_curso, completada, cerrada
    acciones_generadas: List[str] = field(default_factory=list)
    created_by: str = ""
    
    def get_porcentaje_cumplimiento(self) -> float:
        """Calcular porcentaje de cumplimiento"""
        if not self.checklist:
            return 0.0
        cumplen = len([c for c in self.checklist if c.get("cumple")])
        return (cumplen / len(self.checklist)) * 100
    
    def get_hallazgos_por_tipo(self) -> Dict:
        """Contar hallazgos por tipo"""
        tipos = {"critico": 0, "grave": 0, "leve": 0}
        for h in self.hallazgos:
            tipo = h.get("tipo", "leve")
            if tipo in tipos:
                tipos[tipo] += 1
        return tipos

@dataclass
class ChecklistItem:
    """Item de checklist predefinido"""
    id: str = ""
    tipo_inspeccion: str = ""  # locativa, equipos, epp, etc.
    categoria: str = ""
    item: str = ""
    descripcion: str = ""
    peso: int = 1
    normativa: str = ""
    activo: bool = True

@dataclass
class HallazgoInspeccion:
    """Modelo de Hallazgo"""
    inspeccion_id: str = ""
    descripcion: str = ""
    tipo: str = ""  # critico, grave, leve
    prioridad: str = ""  # alta, media, baja
    evidencia_url: str = ""
    foto_url: str = ""
    accion_correctiva: str = ""
    responsable_id: str = ""
    responsable_nombre: str = ""
    fecha_cierre: str = ""
    estado: str = "abierto"  # abierto, en_proceso, cerrado
    created_at: str = ""
