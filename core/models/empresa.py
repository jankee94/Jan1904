# core/models/empresa.py
from typing import Optional, List
from dataclasses import dataclass, field
from core.models.base import BaseModel

@dataclass
class Empresa(BaseModel):
    """Modelo de Empresa"""
    nombre: str = ""
    nit: str = ""
    razon_social: str = ""
    direccion: str = ""
    ciudad: str = ""
    departamento: str = ""
    pais: str = "Colombia"
    telefono: str = ""
    email: str = ""
    sitio_web: str = ""
    sector: str = ""
    numero_trabajadores: int = 0
    arl: str = ""
    eps: str = ""
    ccf: str = ""
    logo_url: str = ""
    certificaciones: List[str] = field(default_factory=list)
    plan: str = "basico"  # basico, profesional, empresarial
    suscripcion_activa: bool = True
    fecha_vencimiento: Optional[str] = None
