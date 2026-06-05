# modules/dashboard.py
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from datetime import datetime, timedelta
from core.db import db
from core.auth import auth_manager
from core.logger import logger

def render():
    st.title("📊 Dashboard SST")
    
    if not auth_manager.authenticated():
        st.warning("Por favor inicia sesión")
        return
    
    # Obtener datos de Firestore
    trabajadores = db.get_all("trabajadores", limit=100)
    incidentes = db.get_all("incidentes", limit=100)
    peligros = db.get_all("peligros", limit=100)
    
    # KPIs principales
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "👥 Trabajadores",
            len(trabajadores),
            delta="Activos",
            delta_color="normal"
        )
    
    with col2:
        incidentes_mes = len([i for i in incidentes 
                              if i.get("fecha", "").startswith(datetime.now().strftime("%Y-%m"))])
        st.metric(
            "📝 Incidentes (mes)",
            incidentes_mes,
            delta="Este mes",
            delta_color="inverse"
        )
    
    with col3:
        peligros_altos = len([p for p in peligros if p.get("nivel_riesgo") == "I"])
        st.metric(
            "⚠️ Riesgos Altos",
            peligros_altos,
            delta="Nivel I",
            delta_color="off"
        )
    
    with col4:
        # Cumplimiento básico
        cumplimiento = 0
        if trabajadores:
            cumplimiento = 65
        st.metric(
            "✅ Cumplimiento",
            f"{cumplimiento}%",
            delta="General",
            delta_color="normal"
        )
    
    st.markdown("---")
    
    # Gráficos
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Incidentes por Tipo")
        if incidentes:
            tipos = {}
            for i in incidentes:
                tipo = i.get("tipo", "Otro")
                tipos[tipo] = tipos.get(tipo, 0) + 1
            
            fig = px.pie(
                values=list(tipos.values()),
                names=list(tipos.keys()),
                title="Distribución de Incidentes"
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Sin datos de incidentes")
    
    with col2:
        st.subheader("Riesgos por Nivel")
        if peligros:
            niveles = {"I": 0, "II": 0, "III": 0}
            for p in peligros:
                nivel = p.get("nivel_riesgo", "III")
                niveles[nivel] = niveles.get(nivel, 0) + 1
            
            fig = go.Figure(data=[
                go.Bar(
                    x=list(niveles.keys()),
                    y=list(niveles.values()),
                    marker_color=["#ff4444", "#ffa500", "#ffff00"]
                )
            ])
            fig.update_layout(title="Matriz de Riesgos")
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Sin datos de peligros")
    
    # Últimos incidentes
    st.markdown("---")
    st.subheader("📋 Últimos Incidentes Registrados")
    
    if incidentes:
        incidentes_recientes = sorted(incidentes, 
                                      key=lambda x: x.get("fecha", ""), 
                                      reverse=True)[:5]
        
        for inc in incidentes_recientes:
            with st.container():
                col1, col2, col3 = st.columns([3, 1, 1])
                with col1:
                    st.write(f"**{inc.get('tipo', '')}** - {inc.get('descripcion', '')[:100]}")
                with col2:
                    st.write(f"📅 {inc.get('fecha', '')}")
                with col3:
                    st.write(f"⚠️ {inc.get('gravedad', '')}")
                st.markdown("---")
    else:
        st.info("No hay incidentes registrados")
    
    # Próximas acciones
    st.subheader("✅ Próximas Acciones")
    st.info("Completa el Diagnóstico IA para generar acciones automáticas")
    
    # Footer
    st.markdown("---")
    st.caption(f"Última actualización: {datetime.now().strftime('%Y-%m-%d %H:%M')}")