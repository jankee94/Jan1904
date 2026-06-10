# modules/indicadores/ui.py
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime

from core.services.indicador_service import indicador_service

def render_indicadores():
    """Renderizar módulo de indicadores SST"""
    st.markdown("""
    <div style="background: linear-gradient(135deg, #1a365d 0%, #2c5282 100%); padding: 20px; border-radius: 15px; margin-bottom: 20px;">
        <h1 style="color: white; margin: 0;">📊 Indicadores SST</h1>
        <p style="color: rgba(255,255,255,0.8); margin: 5px 0 0 0;">Dashboard ejecutivo - Indicadores clave de desempeño</p>
    </div>
    """, unsafe_allow_html=True)
    
    tabs = st.tabs(["📈 Dashboard", "📊 Análisis", "📋 Reportes", "⚙️ Configuración"])
    
    with tabs[0]:
        render_dashboard()
    
    with tabs[1]:
        render_analisis()
    
    with tabs[2]:
        render_reportes_indicadores()
    
    with tabs[3]:
        render_configuracion_indicadores()

def render_dashboard():
    """Dashboard de indicadores"""
    st.subheader("📈 Dashboard Ejecutivo SST")
    
    with st.spinner("Calculando indicadores..."):
        indicadores = indicador_service.calcular_indicadores("empresa_default")
        datos_base = indicadores.get("datos_base", {})
    
    # KPIs principales
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        ifr = indicadores.get("indice_frecuencia", 0)
        color = indicador_service.get_color_indicador(ifr, 5)
        st.markdown(f"""
        <div style="background: {color}20; border-radius: 12px; padding: 16px; text-align: center;">
            <div style="font-size: 32px; font-weight: bold; color: {color}">{ifr:.1f}</div>
            <div style="font-size: 14px; color: #333;">Índice de Frecuencia</div>
            <div style="font-size: 11px; color: #666;">Meta: ≤5 | Real: {ifr:.1f}</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        isv = indicadores.get("indice_severidad", 0)
        color = indicador_service.get_color_indicador(isv, 100)
        st.markdown(f"""
        <div style="background: {color}20; border-radius: 12px; padding: 16px; text-align: center;">
            <div style="font-size: 32px; font-weight: bold; color: {color}">{isv:.1f}</div>
            <div style="font-size: 14px; color: #333;">Índice de Severidad</div>
            <div style="font-size: 11px; color: #666;">Meta: ≤100 | Real: {isv:.1f}</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        ta = indicadores.get("tasa_accidentalidad", 0)
        color = indicador_service.get_color_indicador(ta, 5)
        st.markdown(f"""
        <div style="background: {color}20; border-radius: 12px; padding: 16px; text-align: center;">
            <div style="font-size: 32px; font-weight: bold; color: {color}">{ta:.1f}%</div>
            <div style="font-size: 14px; color: #333;">Tasa Accidentalidad</div>
            <div style="font-size: 11px; color: #666;">Meta: ≤5% | Real: {ta:.1f}%</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        cp = indicadores.get("cumplimiento_phva", 0)
        color = indicador_service.get_color_indicador(cp, 80, False)
        st.markdown(f"""
        <div style="background: {color}20; border-radius: 12px; padding: 16px; text-align: center;">
            <div style="font-size: 32px; font-weight: bold; color: {color}">{cp:.0f}%</div>
            <div style="font-size: 14px; color: #333;">Cumplimiento PHVA</div>
            <div style="font-size: 11px; color: #666;">Meta: ≥80% | Real: {cp:.0f}%</div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Gráficos
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Indicadores de Gestión")
        indicadores_gestion = {
            "Cumplimiento Legal": indicadores.get("cumplimiento_legal", 0),
            "Tasa Capacitación": indicadores.get("tasa_capacitacion", 0),
            "Tasa Inspección": indicadores.get("tasa_inspeccion", 0),
            "Cierre Hallazgos": indicadores.get("tasa_cierre_hallazgos", 0),
            "Control Peligros": indicadores.get("tasa_control_peligros", 0)
        }
        
        fig = go.Figure(data=[go.Bar(
            x=list(indicadores_gestion.keys()),
            y=list(indicadores_gestion.values()),
            marker_color=['#27ae60' if v >= 80 else '#f39c12' if v >= 60 else '#e74c3c' for v in indicadores_gestion.values()],
            text=[f"{v:.0f}%" for v in indicadores_gestion.values()],
            textposition='auto'
        )])
        fig.update_layout(height=400, title="Indicadores de Gestión (%)")
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("Resumen de Datos Base")
        datos_resumen = {
            "Trabajadores": datos_base.get("trabajadores_total", 0),
            "Incidentes": datos_base.get("incidentes_total", 0),
            "Acciones": datos_base.get("acciones_totales", 0),
            "Peligros": datos_base.get("peligros_identificados", 0),
            "Capacitaciones": datos_base.get("capacitaciones_programadas", 0),
            "Inspecciones": datos_base.get("inspecciones_programadas", 0)
        }
        
        fig = go.Figure(data=[go.Bar(
            x=list(datos_resumen.keys()),
            y=list(datos_resumen.values()),
            marker_color='#3498db'
        )])
        fig.update_layout(height=400, title="Datos Base del Sistema")
        st.plotly_chart(fig, use_container_width=True)
    
    st.markdown("---")
    
    # Indicadores detallados
    st.subheader("Detalle de Indicadores")
    
    detalles = [
        {"Indicador": "Índice de Frecuencia", "Valor": f"{indicadores.get('indice_frecuencia', 0):.2f}", "Meta": "≤5", "Estado": "✅ Cumple" if indicadores.get('indice_frecuencia', 0) <= 5 else "⚠️ No cumple"},
        {"Indicador": "Índice de Severidad", "Valor": f"{indicadores.get('indice_severidad', 0):.2f}", "Meta": "≤100", "Estado": "✅ Cumple" if indicadores.get('indice_severidad', 0) <= 100 else "⚠️ No cumple"},
        {"Indicador": "Tasa de Accidentalidad", "Valor": f"{indicadores.get('tasa_accidentalidad', 0):.1f}%", "Meta": "≤5%", "Estado": "✅ Cumple" if indicadores.get('tasa_accidentalidad', 0) <= 5 else "⚠️ No cumple"},
        {"Indicador": "Cumplimiento PHVA", "Valor": f"{indicadores.get('cumplimiento_phva', 0):.0f}%", "Meta": "≥80%", "Estado": "✅ Cumple" if indicadores.get('cumplimiento_phva', 0) >= 80 else "⚠️ No cumple"},
        {"Indicador": "Cumplimiento Legal", "Valor": f"{indicadores.get('cumplimiento_legal', 0):.0f}%", "Meta": "≥90%", "Estado": "✅ Cumple" if indicadores.get('cumplimiento_legal', 0) >= 90 else "⚠️ No cumple"},
        {"Indicador": "Tasa de Capacitación", "Valor": f"{indicadores.get('tasa_capacitacion', 0):.0f}%", "Meta": "100%", "Estado": "✅ Cumple" if indicadores.get('tasa_capacitacion', 0) >= 100 else "⚠️ No cumple"},
        {"Indicador": "Tasa de Inspección", "Valor": f"{indicadores.get('tasa_inspeccion', 0):.0f}%", "Meta": "≥95%", "Estado": "✅ Cumple" if indicadores.get('tasa_inspeccion', 0) >= 95 else "⚠️ No cumple"},
        {"Indicador": "Tasa de Cierre de Hallazgos", "Valor": f"{indicadores.get('tasa_cierre_hallazgos', 0):.0f}%", "Meta": "≥90%", "Estado": "✅ Cumple" if indicadores.get('tasa_cierre_hallazgos', 0) >= 90 else "⚠️ No cumple"},
        {"Indicador": "Tasa de Control de Peligros", "Valor": f"{indicadores.get('tasa_control_peligros', 0):.0f}%", "Meta": "≥85%", "Estado": "✅ Cumple" if indicadores.get('tasa_control_peligros', 0) >= 85 else "⚠️ No cumple"}
    ]
    
    st.dataframe(pd.DataFrame(detalles), use_container_width=True)

def render_analisis():
    """Análisis detallado de indicadores"""
    st.subheader("📊 Análisis de Indicadores")
    
    with st.spinner("Cargando datos..."):
        indicadores = indicador_service.calcular_indicadores("empresa_default")
    
    # Tendencia
    st.subheader("📈 Análisis de Tendencia")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.metric(
            "Tendencia Índice de Frecuencia",
            f"{indicadores.get('indice_frecuencia', 0):.2f}",
            delta="-0.5" if indicadores.get('indice_frecuencia', 0) < 5 else "+0.3",
            delta_color="normal" if indicadores.get('indice_frecuencia', 0) < 5 else "inverse"
        )
        st.caption("Comparación con período anterior")
    
    with col2:
        st.metric(
            "Tendencia Cumplimiento PHVA",
            f"{indicadores.get('cumplimiento_phva', 0):.0f}%",
            delta="+5%",
            delta_color="normal"
        )
    
    # Recomendaciones
    st.subheader("💡 Recomendaciones")
    
    recomendaciones = []
    
    if indicadores.get('indice_frecuencia', 0) > 5:
        recomendaciones.append("🔴 El índice de frecuencia está por encima de la meta. Revisar programas de prevención.")
    
    if indicadores.get('cumplimiento_phva', 0) < 80:
        recomendaciones.append("🟡 El cumplimiento PHVA está por debajo del objetivo. Acelerar ejecución de acciones.")
    
    if indicadores.get('tasa_cierre_hallazgos', 0) < 90:
        recomendaciones.append("🟡 Alta tasa de hallazgos abiertos. Priorizar cierre de hallazgos críticos.")
    
    if indicadores.get('tasa_control_peligros', 0) < 85:
        recomendaciones.append("🟡 Controles de peligros insuficientes. Implementar medidas de control adicionales.")
    
    if not recomendaciones:
        recomendaciones.append("✅ Todos los indicadores están dentro de los rangos esperados. Mantener las buenas prácticas.")
    
    for rec in recomendaciones:
        st.write(rec)

def render_reportes_indicadores():
    """Reportes de indicadores"""
    st.subheader("📋 Reportes")
    
    indicadores = indicador_service.calcular_indicadores("empresa_default")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("📥 Exportar Dashboard a Excel", use_container_width=True):
            excel_data = indicador_service.exportar_dashboard_excel(indicadores)
            if excel_data:
                st.download_button(
                    "Descargar Excel",
                    data=excel_data,
                    file_name=f"dashboard_indicadores_{datetime.now().strftime('%Y%m%d')}.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )
    
    with col2:
        st.info("""
        **Indicadores calculados automáticamente:**
        - Índice de Frecuencia
        - Índice de Severidad
        - Tasa de Accidentalidad
        - Cumplimiento PHVA
        - Cumplimiento Legal
        - Tasas de gestión
        """)

def render_configuracion_indicadores():
    """Configuración de metas de indicadores"""
    st.subheader("⚙️ Configuración de Metas")
    st.info("Las metas están preconfiguradas según estándares ISO 45001. Para modificar las metas, contacte al administrador.")
    
    st.markdown("""
    ### Metas por Defecto
    
    | Indicador | Meta | Justificación |
    |-----------|------|---------------|
    | Índice de Frecuencia | ≤5 | Estándar ISO 45001 |
    | Índice de Severidad | ≤100 | Estándar ISO 45001 |
    | Tasa de Accidentalidad | ≤5% | Promedio sectorial |
    | Cumplimiento PHVA | ≥80% | Ciclo de mejora continua |
    | Cumplimiento Legal | ≥90% | Requisito Decreto 1072 |
    | Tasa de Capacitación | 100% | Cobertura total |
    | Tasa de Inspección | ≥95% | Cobertura programada |
    | Cierre de Hallazgos | ≥90% | Efectividad correctiva |
    | Control de Peligros | ≥85% | Gestión de riesgos |
    """)
