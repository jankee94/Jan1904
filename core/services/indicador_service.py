# core/services/indicador_service.py
import streamlit as st
from typing import Optional, List, Dict
from datetime import datetime, timedelta
import pandas as pd
import io
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, landscape
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
import plotly.graph_objects as go
import plotly.express as px

from firebase.firestore.client import firestore_client
from config.settings import settings

class IndicadorService:
    """Servicio para gestión de indicadores SST"""
    
    def __init__(self):
        self.collection = "indicadores"
    
    def calcular_indicadores(self, empresa_id: str) -> Dict:
        """Calcular todos los indicadores a partir de los datos existentes"""
        # Obtener datos necesarios
        trabajadores = firestore_client.query("trabajadores", filters=[["empresa_id", "==", empresa_id]])
        incidentes = firestore_client.query("incidentes", filters=[["empresa_id", "==", empresa_id]])
        acciones = firestore_client.query("acciones", filters=[["empresa_id", "==", empresa_id]])
        peligros = firestore_client.query("peligros", filters=[["empresa_id", "==", empresa_id]])
        matriz_legal = firestore_client.query("matriz_legal", filters=[["empresa_id", "==", empresa_id]])
        capacitaciones = firestore_client.query("capacitaciones", filters=[["empresa_id", "==", empresa_id]])
        inspecciones = firestore_client.query("inspecciones", filters=[["empresa_id", "==", empresa_id]])
        
        # Calcular horas trabajadas (estimado: 8 horas/día, 20 días/mes, 12 meses)
        total_trabajadores = len(trabajadores)
        horas_trabajadas = total_trabajadores * 8 * 20 * 12
        
        # Incidentes por gravedad
        incidentes_leves = len([i for i in incidentes if i.get("gravedad") == "leve"])
        incidentes_graves = len([i for i in incidentes if i.get("gravedad") == "grave"])
        incidentes_mortales = len([i for i in incidentes if i.get("gravedad") == "mortal"])
        
        # Días perdidos estimados
        pesos = {"leve": 1, "moderada": 7, "grave": 30, "mortal": 180}
        dias_perdidos = sum(pesos.get(i.get("gravedad", "leve"), 1) for i in incidentes)
        
        # Acciones
        acciones_completadas = len([a for a in acciones if a.get("estado") == "completada"])
        
        # Peligros controlados
        peligros_controlados = len([p for p in peligros if p.get("nivel", "III") in ["I", "II"]])
        
        # Hallazgos
        hallazgos_totales = 0
        hallazgos_cerrados = 0
        for ins in inspecciones:
            hallazgos = ins.get("hallazgos", [])
            hallazgos_totales += len(hallazgos)
            hallazgos_cerrados += len([h for h in hallazgos if h.get("estado") == "cerrado"])
        
        # Requisitos legales
        requisitos_cumplen = len([r for r in matriz_legal if r.get("cumple") == 1])
        
        calculo = CalculoIndicador(
            trabajadores_total=total_trabajadores,
            horas_trabajadas=horas_trabajadas,
            incidentes_total=len(incidentes),
            incidentes_leves=incidentes_leves,
            incidentes_graves=incidentes_graves,
            incidentes_mortales=incidentes_mortales,
            dias_perdidos=dias_perdidos,
            acciones_completadas=acciones_completadas,
            acciones_totales=len(acciones),
            capacitaciones_realizadas=len([c for c in capacitaciones if c.get("estado") == "finalizada"]),
            capacitaciones_programadas=len([c for c in capacitaciones if c.get("estado") == "programada"]),
            inspecciones_realizadas=len([i for i in inspecciones if i.get("estado") == "completada"]),
            inspecciones_programadas=len([i for i in inspecciones if i.get("estado") == "programada"]),
            hallazgos_cerrados=hallazgos_cerrados,
            hallazgos_totales=hallazgos_totales,
            peligros_identificados=len(peligros),
            peligros_controlados=peligros_controlados
        )
        
        return {
            "indice_frecuencia": calculo.get_indice_frecuencia(),
            "indice_severidad": calculo.get_indice_severidad(),
            "tasa_accidentalidad": calculo.get_tasa_accidentalidad(),
            "cumplimiento_phva": calculo.get_porcentaje_cumplimiento_phva(),
            "cumplimiento_legal": calculo.get_porcentaje_cumplimiento_legal(requisitos_cumplen, len(matriz_legal)),
            "tasa_capacitacion": (calculo.capacitaciones_realizadas / calculo.capacitaciones_programadas * 100) if calculo.capacitaciones_programadas > 0 else 0,
            "tasa_inspeccion": (calculo.inspecciones_realizadas / calculo.inspecciones_programadas * 100) if calculo.inspecciones_programadas > 0 else 0,
            "tasa_cierre_hallazgos": (calculo.hallazgos_cerrados / calculo.hallazgos_totales * 100) if calculo.hallazgos_totales > 0 else 0,
            "tasa_control_peligros": (calculo.peligros_controlados / calculo.peligros_identificados * 100) if calculo.peligros_identificados > 0 else 0,
            "datos_base": calculo
        }
    
    def get_color_indicador(self, valor: float, meta: float, es_menor_mejor: bool = True) -> str:
        """Determinar color del indicador según valor vs meta"""
        if es_menor_mejor:
            if valor <= meta:
                return "#27ae60"  # verde
            elif valor <= meta * 1.5:
                return "#f39c12"  # amarillo
            else:
                return "#e74c3c"  # rojo
        else:
            if valor >= meta:
                return "#27ae60"  # verde
            elif valor >= meta * 0.7:
                return "#f39c12"  # amarillo
            else:
                return "#e74c3c"  # rojo
    
    def generar_dashboard_html(self, indicadores: Dict) -> str:
        """Generar HTML para dashboard"""
        html = f'''
        <div style="display: grid; grid-template-columns: repeat(4, 1fr); gap: 16px; margin-bottom: 24px;">
            <div style="background: {self.get_color_indicador(indicadores.get("indice_frecuencia", 0), 5)}20; border-radius: 12px; padding: 16px; text-align: center;">
                <div style="font-size: 28px; font-weight: bold; color: {self.get_color_indicador(indicadores.get("indice_frecuencia", 0), 5)}">{indicadores.get("indice_frecuencia", 0):.1f}</div>
                <div style="font-size: 12px; color: #666;">Índice de Frecuencia</div>
                <div style="font-size: 10px; color: #999;">Meta: ≤5</div>
            </div>
            <div style="background: {self.get_color_indicador(indicadores.get("indice_severidad", 0), 100)}20; border-radius: 12px; padding: 16px; text-align: center;">
                <div style="font-size: 28px; font-weight: bold; color: {self.get_color_indicador(indicadores.get("indice_severidad", 0), 100)}">{indicadores.get("indice_severidad", 0):.1f}</div>
                <div style="font-size: 12px; color: #666;">Índice de Severidad</div>
                <div style="font-size: 10px; color: #999;">Meta: ≤100</div>
            </div>
            <div style="background: {self.get_color_indicador(indicadores.get("tasa_accidentalidad", 0), 5)}20; border-radius: 12px; padding: 16px; text-align: center;">
                <div style="font-size: 28px; font-weight: bold; color: {self.get_color_indicador(indicadores.get("tasa_accidentalidad", 0), 5)}">{indicadores.get("tasa_accidentalidad", 0):.1f}%</div>
                <div style="font-size: 12px; color: #666;">Tasa de Accidentalidad</div>
                <div style="font-size: 10px; color: #999;">Meta: ≤5%</div>
            </div>
            <div style="background: {self.get_color_indicador(indicadores.get("cumplimiento_phva", 0), 80, False)}20; border-radius: 12px; padding: 16px; text-align: center;">
                <div style="font-size: 28px; font-weight: bold; color: {self.get_color_indicador(indicadores.get("cumplimiento_phva", 0), 80, False)}">{indicadores.get("cumplimiento_phva", 0):.0f}%</div>
                <div style="font-size: 12px; color: #666;">Cumplimiento PHVA</div>
                <div style="font-size: 10px; color: #999;">Meta: ≥80%</div>
            </div>
        </div>
        '''
        return html
    
    def exportar_dashboard_excel(self, indicadores: Dict) -> Optional[bytes]:
        """Exportar dashboard a Excel"""
        try:
            data = [
                {"Indicador": "Índice de Frecuencia", "Valor": indicadores.get("indice_frecuencia", 0), "Meta": 5, "Unidad": "x 1,000,000 horas"},
                {"Indicador": "Índice de Severidad", "Valor": indicadores.get("indice_severidad", 0), "Meta": 100, "Unidad": "días x 1,000,000 horas"},
                {"Indicador": "Tasa de Accidentalidad", "Valor": f"{indicadores.get('tasa_accidentalidad', 0):.1f}%", "Meta": "5%", "Unidad": "%"},
                {"Indicador": "Cumplimiento PHVA", "Valor": f"{indicadores.get('cumplimiento_phva', 0):.0f}%", "Meta": "80%", "Unidad": "%"},
                {"Indicador": "Cumplimiento Legal", "Valor": f"{indicadores.get('cumplimiento_legal', 0):.0f}%", "Meta": "90%", "Unidad": "%"},
                {"Indicador": "Tasa de Capacitación", "Valor": f"{indicadores.get('tasa_capacitacion', 0):.0f}%", "Meta": "100%", "Unidad": "%"},
                {"Indicador": "Tasa de Inspección", "Valor": f"{indicadores.get('tasa_inspeccion', 0):.0f}%", "Meta": "95%", "Unidad": "%"},
                {"Indicador": "Tasa de Cierre de Hallazgos", "Valor": f"{indicadores.get('tasa_cierre_hallazgos', 0):.0f}%", "Meta": "90%", "Unidad": "%"},
                {"Indicador": "Tasa de Control de Peligros", "Valor": f"{indicadores.get('tasa_control_peligros', 0):.0f}%", "Meta": "85%", "Unidad": "%"}
            ]
            
            df = pd.DataFrame(data)
            output = io.BytesIO()
            with pd.ExcelWriter(output, engine='openpyxl') as writer:
                df.to_excel(writer, sheet_name="Indicadores SST", index=False)
            
            return output.getvalue()
        except Exception as e:
            st.error(f"Error exportando: {e}")
            return None

indicador_service = IndicadorService()
