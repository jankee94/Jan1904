# core/models/incidente.py
from typing import Optional, List
from dataclasses import dataclass, field
from core.models.base import BaseModel

@dataclass
class Incidente(BaseModel):
    """Modelo de Incidente/Accidente"""
    empresa_id: str = ""
    tipo: str = ""  # Accidente, Incidente, Enfermedad Laboral
    descripcion: str = ""
    fecha: str = ""
    hora: str = ""
    lugar: str = ""
    area: str = ""
    proceso: str = ""
    trabajador_id: str = ""
    trabajador_nombre: str = ""
    cargo: str = ""
    antiguedad: str = ""
    testigos: List[str] = field(default_factory=list)
    descripcion_evento: str = ""
    causa_basica: str = ""
    causa_inmediata: str = ""
    causa_raiz: str = ""
    arl_reportado: bool = False
    arl_fecha: str = ""
    incapacidad_dias: int = 0
    gravedad: str = "leve"  # leve, moderada, grave, mortal
    acciones_tomadas: str = ""
    acciones_correctivas: List[str] = field(default_factory=list)
    evidencias_urls: List[str] = field(default_factory=list)
    investigador_id: str = ""
    estado: str = "abierto"  # abierto, investigando, cerrado
    fecha_cierre: str = ""
    
    def get_indice_frecuencia(self, horas_trabajadas: int) -> float:
        """Calcular índice de frecuencia"""
        return (1 * 1000000) / horas_trabajadas if horas_trabajadas > 0 else 0
    
    def get_porcentaje_cumplimiento(self, total_acciones: int) -> float:
        """Calcular porcentaje de acciones completadas"""
        completadas = len([a for a in self.acciones_correctivas if a])
        return (completadas / total_acciones * 100) if total_acciones > 0 else 0
