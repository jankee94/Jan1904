# core/models/capacitacion.py
from typing import Optional, List, Dict
from dataclasses import dataclass, field
from datetime import datetime
from core.models.base import BaseModel

@dataclass
class Capacitacion(BaseModel):
    """Modelo de Capacitación"""
    empresa_id: str = ""
    titulo: str = ""
    descripcion: str = ""
    tipo: str = ""  # induccion, entrenamiento, actualizacion, especializacion
    modalidad: str = ""  # presencial, virtual, mixta
    duracion_horas: int = 0
    fecha_inicio: str = ""
    fecha_fin: str = ""
    hora_inicio: str = ""
    hora_fin: str = ""
    lugar: str = ""
    direccion: str = ""
    cupo_maximo: int = 0
    cupo_disponible: int = 0
    instructor: str = ""
    instructor_cedula: str = ""
    instructor_telefono: str = ""
    instructor_email: str = ""
    contenido: str = ""
    objetivos: List[str] = field(default_factory=list)
    temario: List[str] = field(default_factory=list)
    requisitos: List[str] = field(default_factory=list)
    materiales_url: List[str] = field(default_factory=list)
    evaluacion_requerida: bool = False
    nota_aprobacion: float = 70.0
    certificado_automatico: bool = True
    estado: str = "programada"  # programada, en_curso, finalizada, cancelada
    asistentes: List[Dict] = field(default_factory=list)  # [{trabajador_id, nombre, asistio, fecha, firma_url, nota, certificado_url}]
    created_by: str = ""
    
    def get_porcentaje_asistencia(self) -> float:
        """Calcular porcentaje de asistencia"""
        if not self.asistentes or self.cupo_maximo == 0:
            return 0.0
        asistentes_count = len([a for a in self.asistentes if a.get("asistio")])
        return (asistentes_count / self.cupo_maximo) * 100
    
    def get_porcentaje_aprobacion(self) -> float:
        """Calcular porcentaje de aprobación"""
        if not self.asistentes:
            return 0.0
        aprobados = len([a for a in self.asistentes if a.get("nota", 0) >= self.nota_aprobacion])
        return (aprobados / len(self.asistentes)) * 100
    
    def esta_llena(self) -> bool:
        """Verificar si el cupo está lleno"""
        asistentes_count = len([a for a in self.asistentes if a.get("asistio")])
        return asistentes_count >= self.cupo_maximo
    
    def to_dict(self) -> Dict:
        data = super().to_dict()
        # Convertir listas de objetos a listas de dicts
        return data

@dataclass
class AsistenciaCapacitacion:
    """Modelo de Asistencia a Capacitación"""
    capacitacion_id: str = ""
    trabajador_id: str = ""
    trabajador_nombre: str = ""
    trabajador_cedula: str = ""
    trabajador_cargo: str = ""
    trabajador_area: str = ""
    fecha_asistencia: str = ""
    hora_llegada: str = ""
    hora_salida: str = ""
    asistio: bool = False
    justificacion: str = ""
    firma_url: str = ""
    firma_data: str = ""  # Base64 de la firma
    evaluacion_nota: float = 0.0
    evaluacion_comentario: str = ""
    certificado_url: str = ""
    certificado_generado: bool = False
    created_at: str = ""

@dataclass
class EvaluacionCapacitacion:
    """Modelo de Evaluación de Capacitación"""
    capacitacion_id: str = ""
    trabajador_id: str = ""
    preguntas: List[Dict] = field(default_factory=list)  # [{pregunta, respuesta, puntaje}]
    puntaje_total: float = 0.0
    puntaje_obtenido: float = 0.0
    porcentaje: float = 0.0
    aprobo: bool = False
    fecha_evaluacion: str = ""
    feedback: str = ""
