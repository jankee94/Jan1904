# utils/kpis.py
import pandas as pd
from datetime import datetime, timedelta

def calcular_kpis(incidentes_df, trabajadores_df):
    """Calcular KPIs SST"""
    kpis = {
        "if": 0,
        "is": 0,
        "ia": 0,
        "frecuencia_mensual": [],
        "gravedad_por_tipo": {},
        "tendencia": []
    }
    
    if incidentes_df.empty:
        return kpis
    
    # Horas trabajadas estimadas (8 horas diarias, 20 días al mes)
    total_trabajadores = len(trabajadores_df) if not trabajadores_df.empty else 1
    horas_trabajadas = total_trabajadores * 8 * 20 * 12  # anual
    
    # Índice de Frecuencia (IF) = (N° incidentes × 200,000) / Horas trabajadas
    total_incidentes = len(incidentes_df)
    kpis["if"] = (total_incidentes * 200000) / horas_trabajadas if horas_trabajadas > 0 else 0
    
    # Índice de Severidad (IS) = (Días perdidos × 200,000) / Horas trabajadas
    pesos = {"Leve": 1, "Moderada": 7, "Grave": 30, "Mortal": 180}
    dias_perdidos = sum(pesos.get(row.get("gravedad", "Leve"), 1) for _, row in incidentes_df.iterrows())
    kpis["is"] = (dias_perdidos * 200000) / horas_trabajadas if horas_trabajadas > 0 else 0
    
    # Índice de Accidentalidad (IA) = IF × IS / 1000
    kpis["ia"] = (kpis["if"] * kpis["is"]) / 1000
    
    # Frecuencia mensual
    for i in range(12):
        mes = datetime.now().replace(day=1) - timedelta(days=30*i)
        count = len([1 for _, row in incidentes_df.iterrows() 
                    if row.get("fecha", "").startswith(mes.strftime("%Y-%m"))])
        kpis["frecuencia_mensual"].append({"mes": mes.strftime("%B"), "incidentes": count})
    
    # Gravedad por tipo
    for _, row in incidentes_df.iterrows():
        tipo = row.get("tipo", "Otro")
        gravedad = row.get("gravedad", "Leve")
        if tipo not in kpis["gravedad_por_tipo"]:
            kpis["gravedad_por_tipo"][tipo] = {"Leve": 0, "Moderada": 0, "Grave": 0, "Mortal": 0}
        kpis["gravedad_por_tipo"][tipo][gravedad] = kpis["gravedad_por_tipo"][tipo].get(gravedad, 0) + 1
    
    return kpis

def get_nivel_riesgo_kpi(if_valor):
    """Clasificar nivel de riesgo según IF"""
    if if_valor < 5:
        return "Bajo", "🟢"
    elif if_valor < 15:
        return "Medio", "🟡"
    elif if_valor < 30:
        return "Alto", "🟠"
    else:
        return "Crítico", "🔴"
