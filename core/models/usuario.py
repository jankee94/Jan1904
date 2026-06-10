# core/models/usuario.py
from datetime import datetime
from typing import Optional, List
from dataclasses import dataclass, field
from core.models.base import BaseModel

@dataclass
class Usuario(BaseModel):
    """Modelo de Usuario"""
    email: str = ""
    nombre: str = ""
    apellido: str = ""
    documento: str = ""
    rol: str = "trabajador"
    empresa_id: str = ""
    cargo: str = ""
    telefono: str = ""
    foto_url: str = ""
    areas_permiso: List[str] = field(default_factory=list)
    ultimo_acceso: Optional[datetime] = None
    email_verificado: bool = False
    activo: bool = True
    
    def tiene_permiso(self, modulo: str, accion: str = "leer") -> bool:
        """Verificar si el usuario tiene permiso para un módulo"""
        from config.settings import settings
        
        if self.rol == "admin":
            return True
        
        modulos_permitidos = settings.ROLES.get(self.rol, [])
        if modulo == "todos":
            return True
        return modulo in modulos_permitidos
    
    def puede_editar(self, creado_por: str) -> bool:
        """Verificar si puede editar un registro"""
        if self.rol == "admin":
            return True
        if self.rol == "responsable_sst":
            return True
        return creado_por == self.id
