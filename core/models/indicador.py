# core/models/indicador.py
from typing import Optional, List, Dict
from dataclasses import dataclass, field
from datetime import datetime
from core.models.base import BaseModel

@dataclass
class IndicadorSST(BaseModel):
    """Modelo de Indicador SST"""
    empresa_id: str = ""
    codigo: str = ""
    nombre: str = ""
    tipo: str = ""  # frecuencia, severidad, accidentalidad, ausentismo, cumplimiento
    formula: str = ""
    unidad: str = ""
    meta: float = 0.0
    valor_actual: float = 0.0
    periodo: str = ""  # mensual, trimestral, semestral, anual
    fecha_calculo: str = ""
    tendencia: str = "estable"  # alza, baja, estable
    umbral_alerta: float = 0.0
    umbral_critico: float = 0.0
    color: str = "#27ae60"
    historico: List[Dict] = field(default_factory=list)  # [{periodo, valor, fecha}]
    responsable_id: str = ""
    responsable_nombre: str = ""
    comentarios: str = ""

@dataclass
class CalculoIndicador:
    """Modelo para cálculo de indicadores"""
    trabajadores_total: int = 0
    horas_trabajadas: int = 0
    incidentes_total: int = 0
    incidentes_leves: int = 0
    incidentes_graves: int = 0
    incidentes_mortales: int = 0
    dias_perdidos: int = 0
    acciones_completadas: int = 0
    acciones_totales: int = 0
    capacitaciones_realizadas: int = 0
    capacitaciones_programadas: int = 0
    inspecciones_realizadas: int = 0
    inspecciones_programadas: int = 0
    hallazgos_cerrados: int = 0
    hallazgos_totales: int = 0
    peligros_identificados: int = 0
    peligros_controlados: int = 0
    
    def get_indice_frecuencia(self) -> float:
        """IF = (N° incidentes × 1,000,000) / Horas trabajadas"""
        if self.horas_trabajadas == 0:
            return 0.0
        return (self.incidentes_total * 1000000) / self.horas_trabajadas
    
    def get_indice_severidad(self) -> float:
        """IS = (Días perdidos × 1,000,000) / Horas trabajadas"""
        if self.horas_trabajadas == 0:
            return 0.0
        return (self.dias_perdidos * 1000000) / self.horas_trabajadas
    
    def get_tasa_accidentalidad(self) -> float:
        """TA = (N° incidentes × 100) / Trabajadores"""
        if self.trabajadores_total == 0:
            return 0.0
        return (self.incidentes_total * 100) / self.trabajadores_total
    
    def get_porcentaje_cumplimiento_phva(self) -> float:
        """% Cumplimiento PHVA = (Acciones completadas / Acciones totales) × 100"""
        if self.acciones_totales == 0:
            return 0.0
        return (self.acciones_completadas / self.acciones_totales) * 100
    
    def get_porcentaje_cumplimiento_legal(self, requisitos_cumplen: int, requisitos_totales: int) -> float:
        """% Cumplimiento Legal = (Requisitos cumplen / Requisitos totales) × 100"""
        if requisitos_totales == 0:
            return 0.0
        return (requisitos_cumplen / requisitos_totales) * 100
