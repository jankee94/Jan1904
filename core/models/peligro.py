# core/models/peligro.py
from typing import Optional, List
from dataclasses import dataclass, field
from core.models.base import BaseModel

@dataclass
class Peligro(BaseModel):
    """Modelo de Peligro según GTC-45"""
    empresa_id: str = ""
    tipo: str = ""  # Físico, Químico, Biológico, Ergonómico, Psicosocial, Seguridad
    descripcion: str = ""
    ubicacion: str = ""
    proceso: str = ""
    actividad: str = ""
    exposicion: str = ""
    probabilidad: int = 1  # 1-4
    severidad: int = 1  # 1-3
    nivel_riesgo: str = ""  # I, II, III
    controles_existentes: str = ""
    controles_sugeridos: str = ""
    prioridad: str = "media"  # alta, media, baja
    evidencia_urls: List[str] = field(default_factory=list)
    fecha_identificacion: str = ""
    responsable_id: str = ""
    
    def calcular_nivel_riesgo(self) -> str:
        """Calcular nivel de riesgo según GTC-45"""
        matriz = {
            (1,1): "III", (1,2): "II", (1,3): "I",
            (2,1): "III", (2,2): "II", (2,3): "I",
            (3,1): "II", (3,2): "I", (3,3): "I",
            (4,1): "II", (4,2): "I", (4,3): "I"
        }
        return matriz.get((self.probabilidad, self.severidad), "III")
    
    def get_color_nivel(self) -> str:
        """Obtener color según nivel de riesgo"""
        colores = {"I": "#dc2626", "II": "#f59e0b", "III": "#10b981"}
        return colores.get(self.nivel_riesgo, "#6b7280")
