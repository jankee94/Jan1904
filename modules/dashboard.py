# modules/dashboard.py
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
from core.db import db
from utils.kpis import calcular_kpis, get_nivel_riesgo_kpi
from utils.exporters import boton_exportar

def render():
    st.title("📊 DASHBOARD SST - INDICADORES EN TIEMPO REAL")
    
    # Obtener datos
    empresa = db.obtener_empresa()
    peligros_df = db.obtener_peligros()
    acciones_df = db.obtener_acciones()
    trabajadores_df = db.obtener_trabajadores()
    incidentes_df = db.obtener_incidentes()
    
    # Calcular KPIs
    kpis = calcular_kpis(incidentes_df, trabajadores_df)
    nivel, color = get_nivel_riesgo_kpi(kpis["if"])
    
    # Mostrar empresa
    if empresa:
        st.success(f"🏢 **{empresa.get('nombre', 'Empresa')}** | 👥 {empresa.get('trabajadores', 0)} trabajadores")
    
    st.markdown("---")
    
    # KPIs principales
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "📊 Índice de Frecuencia (IF)",
            f"{kpis['if']:.2f}",
            delta=nivel,
            delta_color="inverse" if kpis["if"] > 10 else "normal"
        )
        st.caption(f"Nivel: {color} {nivel}")
    
    with col2:
        st.metric(
            "⚠️ Índice de Severidad (IS)",
            f"{kpis['is']:.2f}",
            delta="Días perdidos",
            delta_color="inverse"
        )
    
    with col3:
        st.metric(
            "💥 Índice de Accidentalidad (IA)",
            f"{kpis['ia']:.2f}",
            delta="Riesgo global",
            delta_color="inverse" if kpis["ia"] > 1 else "normal"
        )
    
    with col4:
        progreso = len(acciones_df[acciones_df['estado'] == 'Completada']) / len(acciones_df) * 100 if len(acciones_df) > 0 else 0
        st.metric(
            "✅ Cumplimiento Plan",
            f"{progreso:.0f}%",
            delta=f"{len(acciones_df)} acciones",
            delta_color="normal"
        )
    
    st.markdown("---")
    
    # ALERTAS AUTOMÁTICAS
    st.subheader("🚨 ALERTAS AUTOMÁTICAS")
    
    alertas = []
    
    # Alerta por IF alto
    if kpis["if"] > 15:
        alertas.append(f"🔴 **ALERTA CRÍTICA:** Índice de Frecuencia alto ({kpis['if']:.2f}). Revisar medidas preventivas.")
    
    # Alerta por riesgos nivel I sin acciones
    riesgos_nivel1 = peligros_df[peligros_df['nivel'] == 'I'] if not peligros_df.empty else pd.DataFrame()
    if len(riesgos_nivel1) > 0:
        alertas.append(f"🟠 **ALERTA:** {len(riesgos_nivel1)} riesgo(s) nivel I sin acciones asignadas.")
    
    # Alerta por acciones vencidas
    acciones_vencidas = acciones_df[acciones_df['fecha'] < datetime.now().strftime("%Y-%m-%d")] if not acciones_df.empty else pd.DataFrame()
    if len(acciones_vencidas) > 0:
        alertas.append(f"⚠️ **ALERTA:** {len(acciones_vencidas)} acción(es) vencidas sin completar.")
    
    # Alerta por falta de trabajadores
    if trabajadores_df.empty:
        alertas.append(f"📋 **INFORMACIÓN:** No hay trabajadores registrados. Completa el módulo.")
    
    if alertas:
        for alerta in alertas:
            if "CRÍTICA" in alerta:
                st.error(alerta)
            elif "ALERTA" in alerta:
                st.warning(alerta)
            else:
                st.info(alerta)
    else:
        st.success("✅ No hay alertas activas. Todo en orden.")
    
    st.markdown("---")
    
    # GRÁFICOS
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📈 Tendencia de Incidentes")
        if kpis["frecuencia_mensual"]:
            df_tendencia = pd.DataFrame(kpis["frecuencia_mensual"])
            fig = px.line(df_tendencia, x="mes", y="incidentes", 
                         title="Incidentes por mes",
                         markers=True)
            fig.update_layout(height=350)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Sin datos suficientes")
    
    with col2:
        st.subheader("⚠️ Distribución de Riesgos")
        if not peligros_df.empty:
            niveles = peligros_df['nivel'].value_counts().reset_index()
            niveles.columns = ['Nivel', 'Cantidad']
            fig = px.pie(niveles, values='Cantidad', names='Nivel',
                        title="Riesgos por Nivel",
                        color_discrete_map={'I': '#ff4444', 'II': '#ffa500', 'III': '#ffff00'})
            fig.update_layout(height=350)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Sin datos de peligros")
    
    # Matriz de calor de riesgos
    st.subheader("🔥 Matriz de Calor de Riesgos")
    if not peligros_df.empty:
        matriz_data = []
        for _, row in peligros_df.iterrows():
            matriz_data.append({
                "Tipo": row.get('tipo', 'Otro'),
                "Probabilidad": row.get('probabilidad', 2),
                "Severidad": row.get('severidad', 2),
                "Nivel": row.get('nivel', 'III')
            })
        df_matriz = pd.DataFrame(matriz_data)
        
        fig = px.density_heatmap(
            df_matriz, x="Probabilidad", y="Severidad",
            title="Matriz de Calor de Riesgos",
            labels={"Probabilidad": "Probabilidad (1-4)", "Severidad": "Severidad (1-3)"}
        )
        fig.update_layout(height=400)
        st.plotly_chart(fig, use_container_width=True)
    
    # Resumen de módulos
    st.markdown("---")
    st.subheader("📋 Resumen de Implementación PHVA")
    
    col1, col2, col3, col4, col5 = st.columns(5)
    with col1:
        st.metric("📊 Dashboard", "✅", help="Módulo activo")
    with col2:
        st.metric("⚠️ Peligros", len(peligros_df), help="Riesgos identificados")
    with col3:
        st.metric("✅ Acciones", len(acciones_df), help="Plan de acción")
    with col4:
        st.metric("👥 Trabajadores", len(trabajadores_df), help="Personal registrado")
    with col5:
        st.metric("📝 Incidentes", len(incidentes_df), help="Eventos reportados")
    
    # Exportar dashboard
    st.markdown("---")
    with st.expander("📥 Exportar Dashboard"):
        if st.button("Generar Reporte PDF"):
            st.info("Reporte PDF en construcción - Próximamente")
    
    st.caption(f"🔄 Última actualización: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
