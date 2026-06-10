# core/models/empresa.py
from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Dict, Optional

@dataclass
class Empresa:
    id: str = ""
    nombre: str = ""
    nit: str = ""
    razon_social: str = ""
    direccion: str = ""
    ciudad: str = ""
    departamento: str = ""
    pais: str = "Colombia"
    telefono: str = ""
    email: str = ""
    sector: str = ""
    numero_trabajadores: int = 0
    arl: str = ""
    eps: str = ""
    plan: str = "basico"  # basico, profesional, empresarial
    activa: bool = True
    fecha_registro: str = ""
    fecha_vencimiento: str = ""
    logo_url: str = ""
    created_at: str = ""
    updated_at: str = ""

@dataclass
class Usuario:
    id: str = ""
    email: str = ""
    nombre: str = ""
    apellido: str = ""
    documento: str = ""
    rol: str = "trabajador"  # admin, responsable_sst, auditor, jefe_area, trabajador
    empresa_id: str = ""
    cargo: str = ""
    telefono: str = ""
    activo: bool = True
    ultimo_acceso: str = ""
    created_at: str = ""
    
    def tiene_permiso(self, modulo: str, accion: str = "leer") -> bool:
        if self.rol == "admin":
            return True
        permisos = {
            "responsable_sst": ["peligros", "acciones", "trabajadores", "incidentes", "matriz_legal", "capacitaciones", "inspecciones", "emergencias", "documentos", "indicadores"],
            "auditor": ["auditorias", "matriz_legal", "incidentes"],
            "jefe_area": ["trabajadores", "incidentes", "inspecciones"],
            "trabajador": ["incidentes", "capacitaciones"]
        }
        return modulo in permisos.get(self.rol, [])

@dataclass
class LogAuditoria:
    id: str = ""
    usuario_id: str = ""
    usuario_email: str = ""
    empresa_id: str = ""
    accion: str = ""  # crear, leer, actualizar, eliminar, login, logout
    modulo: str = ""
    documento_id: str = ""
    valor_anterior: str = ""
    valor_nuevo: str = ""
    ip: str = ""
    user_agent: str = ""
    fecha: str = ""
