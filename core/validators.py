# core/validators.py
from pydantic import BaseModel, EmailStr, Field, validator
from datetime import datetime
from typing import Optional
import re

class TrabajadorValidator(BaseModel):
    """Validaciones para trabajadores"""
    cedula: str = Field(..., min_length=5, max_length=20)
    nombre: str = Field(..., min_length=3, max_length=100)
    email: EmailStr
    cargo: str = Field(..., min_length=2, max_length=50)
    area: str = Field(..., min_length=2, max_length=50)
    fecha_ingreso: str
    eps: str
    arl: str
    
    @validator("cedula")
    def validar_cedula(cls, v):
        if not v.isdigit():
            raise ValueError("Cédula debe contener solo números")
        return v
    
    @validator("fecha_ingreso")
    def validar_fecha(cls, v):
        try:
            datetime.strptime(v, "%Y-%m-%d")
            return v
        except:
            raise ValueError("Formato fecha debe ser YYYY-MM-DD")

class IncidenteValidator(BaseModel):
    """Validaciones para incidentes"""
    tipo: str = Field(..., pattern="^(Accidente|Incidente|Enfermedad Laboral|Casi accidente)$")
    descripcion: str = Field(..., min_length=10, max_length=1000)
    fecha: str
    lugar: str = Field(..., min_length=3, max_length=100)
    gravedad: str = Field(..., pattern="^(Leve|Moderada|Grave|Mortal)$")
    trabajador_afectado_id: str
    
    @validator("fecha")
    def validar_fecha(cls, v):
        try:
            datetime.strptime(v, "%Y-%m-%d")
            return v
        except:
            raise ValueError("Formato fecha debe ser YYYY-MM-DD")

class PeligroValidator(BaseModel):
    """Validaciones para peligros"""
    tipo: str = Field(..., pattern="^(Físico|Químico|Biológico|Ergonómico|Psicosocial|Seguridad)$")
    descripcion: str = Field(..., min_length=10, max_length=500)
    ubicacion: str = Field(..., min_length=3, max_length=100)
    probabilidad: int = Field(..., ge=1, le=4)
    severidad: int = Field(..., ge=1, le=3)
    
    @validator("probabilidad")
    def validar_probabilidad(cls, v):
        if v not in [1, 2, 3, 4]:
            raise ValueError("Probabilidad debe ser 1-4")
        return v
    
    @validator("severidad")
    def validar_severidad(cls, v):
        if v not in [1, 2, 3]:
            raise ValueError("Severidad debe ser 1-3")
        return v

def validar_entrada(tipo: str, datos: dict) -> tuple:
    """Validar entrada según tipo"""
    try:
        if tipo == "trabajador":
            TrabajadorValidator(**datos)
        elif tipo == "incidente":
            IncidenteValidator(**datos)
        elif tipo == "peligro":
            PeligroValidator(**datos)
        return True, "Validación exitosa"
    except Exception as e:
        return False, str(e)