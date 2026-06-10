# modules/emergencias/ui.py
import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import io

from core.services.emergencia_service import emergencia_service
from core.data.emergencia_datos import TIPOS_BRIGADA, TIPOS_EQUIPO, TIPOS_SIMULACRO, NIVELES_ALERTA

def render_emergencias():
    """Renderizar módulo de emergencias"""
    st.markdown("""
    <div style="background: linear-gradient(135deg, #e74c3c 0%, #c0392b 100%); padding: 20px; border-radius: 15px; margin-bottom: 20px;">
        <h1 style="color: white; margin: 0;">🚨 Gestión de Emergencias</h1>
        <p style="color: rgba(255,255,255,0.8); margin: 5px 0 0 0;">Brigadistas, equipos, simulacros y plan de emergencia</p>
    </div>
    """, unsafe_allow_html=True)
    
    tabs = st.tabs(["👥 Brigadistas", "🛠️ Equipos", "🎯 Simulacros", "📋 Plan Emergencia", "⚠️ Alertas", "📊 Reportes"])
    
    with tabs[0]:
        render_brigadistas()
    
    with tabs[1]:
        render_equipos()
    
    with tabs[2]:
        render_simulacros()
    
    with tabs[3]:
        render_plan_emergencia()
    
    with tabs[4]:
        render_alertas()
    
    with tabs[5]:
        render_reportes_emergencia()

def render_brigadistas():
    """Gestión de brigadistas"""
    st.subheader("👥 Brigadistas de Emergencia")
    
    tab1, tab2 = st.tabs(["➕ Registrar", "📋 Lista"])
    
    with tab1:
        with st.form("registrar_brigadista"):
            col1, col2 = st.columns(2)
            with col1:
                nombre = st.text_input("Nombre completo *")
                cedula = st.text_input("Cédula *")
                cargo = st.text_input("Cargo")
                area = st.text_input("Área")
            with col2:
                telefono = st.text_input("Teléfono")
                email = st.text_input("Email")
                tipo_brigada = st.multiselect("Tipo de Brigada", 
                                              [t["nombre"] for t in TIPOS_BRIGADA])
                nivel = st.selectbox("Nivel de entrenamiento", ["básico", "intermedio", "avanzado"])
            
            fecha_entrenamiento = st.date_input("Fecha último entrenamiento", datetime.now())
            fecha_vencimiento = st.date_input("Fecha vencimiento certificación", 
                                              datetime.now() + timedelta(days=365))
            
            submitted = st.form_submit_button("✅ Registrar Brigadista", use_container_width=True)
            
            if submitted and nombre and cedula:
                data = {
                    "nombre": nombre,
                    "cedula": cedula,
                    "cargo": cargo,
                    "area": area,
                    "telefono": telefono,
                    "email": email,
                    "tipo_brigada": tipo_brigada,
                    "nivel_entrenamiento": nivel,
                    "fecha_entrenamiento": fecha_entrenamiento.strftime("%Y-%m-%d"),
                    "fecha_vencimiento": fecha_vencimiento.strftime("%Y-%m-%d"),
                    "empresa_id": "empresa_default"
                }
                if emergencia_service.create_brigadista(data):
                    st.success("✅ Brigadista registrado")
                    st.rerun()
    
    with tab2:
        brigadistas = emergencia_service.get_brigadistas("empresa_default")
        if brigadistas:
            df = pd.DataFrame(brigadistas)
            st.dataframe(df[["nombre", "cedula", "tipo_brigada", "nivel_entrenamiento", "fecha_vencimiento"]], use_container_width=True)
            
            # Alerta vencimientos
            hoy = datetime.now().date()
            vencidos = [b for b in brigadistas if b.get("fecha_vencimiento") and 
                       datetime.strptime(b["fecha_vencimiento"], "%Y-%m-%d").date() < hoy]
            if vencidos:
                st.warning(f"⚠️ {len(vencidos)} brigadistas tienen certificación vencida")
        else:
            st.info("No hay brigadistas registrados")

def render_equipos():
    """Gestión de equipos de emergencia"""
    st.subheader("🛠️ Inventario de Equipos de Emergencia")
    
    tab1, tab2 = st.tabs(["➕ Registrar", "📋 Inventario"])
    
    with tab1:
        with st.form("registrar_equipo"):
            col1, col2 = st.columns(2)
            with col1:
                tipo = st.selectbox("Tipo de Equipo", [t["nombre"] for t in TIPOS_EQUIPO])
                codigo = st.text_input("Código/Serial *")
                ubicacion = st.text_input("Ubicación *")
            with col2:
                estado = st.selectbox("Estado", ["operativo", "mantenimiento", "dañado"])
                fecha_mantenimiento = st.date_input("Último mantenimiento", datetime.now())
                fecha_proximo = st.date_input("Próximo mantenimiento", datetime.now() + timedelta(days=180))
            
            observaciones = st.text_area("Observaciones")
            
            submitted = st.form_submit_button("✅ Registrar Equipo", use_container_width=True)
            
            if submitted and codigo and ubicacion:
                data = {
                    "tipo": tipo,
                    "codigo": codigo,
                    "ubicacion": ubicacion,
                    "estado": estado,
                    "fecha_ultimo_mantenimiento": fecha_mantenimiento.strftime("%Y-%m-%d"),
                    "fecha_proximo_mantenimiento": fecha_proximo.strftime("%Y-%m-%d"),
                    "observaciones": observaciones,
                    "empresa_id": "empresa_default"
                }
                if emergencia_service.create_equipo(data):
                    st.success("✅ Equipo registrado")
                    st.rerun()
    
    with tab2:
        equipos = emergencia_service.get_equipos("empresa_default")
        if equipos:
            df = pd.DataFrame(equipos)
            st.dataframe(df[["codigo", "tipo", "ubicacion", "estado", "fecha_proximo_mantenimiento"]], use_container_width=True)
            
            # Alertas mantenimiento
            vencidos = emergencia_service.get_equipos_vencidos("empresa_default")
            if vencidos:
                st.error(f"⚠️ {len(vencidos)} equipos requieren mantenimiento")
        else:
            st.info("No hay equipos registrados")

def render_simulacros():
    """Gestión de simulacros"""
    st.subheader("🎯 Simulacros de Emergencia")
    
    tab1, tab2 = st.tabs(["➕ Programar", "📋 Historial"])
    
    with tab1:
        with st.form("programar_simulacro"):
            col1, col2 = st.columns(2)
            with col1:
                tipo = st.selectbox("Tipo de Simulacro", [t["nombre"] for t in TIPOS_SIMULACRO])
                fecha = st.date_input("Fecha", datetime.now())
                hora_inicio = st.time_input("Hora de inicio", datetime.now().time())
            with col2:
                duracion = st.number_input("Duración estimada (minutos)", min_value=5, max_value=120, value=30)
                participantes = st.number_input("Participantes esperados", min_value=1, value=50)
            
            observaciones = st.text_area("Observaciones")
            
            submitted = st.form_submit_button("✅ Programar Simulacro", use_container_width=True)
            
            if submitted:
                data = {
                    "tipo": tipo,
                    "fecha": fecha.strftime("%Y-%m-%d"),
                    "hora_inicio": hora_inicio.strftime("%H:%M"),
                    "duracion_minutos": duracion,
                    "participantes": participantes,
                    "observaciones": observaciones,
                    "estado": "programado",
                    "empresa_id": "empresa_default"
                }
                if emergencia_service.create_simulacro(data):
                    st.success("✅ Simulacro programado")
                    st.rerun()
    
    with tab2:
        simulacros = emergencia_service.get_simulacros("empresa_default")
        if simulacros:
            for s in simulacros:
                with st.expander(f"📌 {s.get('tipo')} - {s.get('fecha')}"):
                    col1, col2 = st.columns(2)
                    with col1:
                        st.write(f"**Participantes:** {s.get('participantes', 0)}")
                        st.write(f"**Duración:** {s.get('duracion_minutos', 0)} minutos")
                    with col2:
                        st.write(f"**Estado:** {s.get('estado', 'N/A')}")
                        if s.get("tiempo_evacuacion"):
                            st.write(f"**Tiempo evacuación:** {s.get('tiempo_evacuacion')} seg")
                    
                    if s.get("lecciones_aprendidas"):
                        st.write("**Lecciones aprendidas:**")
                        for l in s.get("lecciones_aprendidas", []):
                            st.write(f"- {l}")
        else:
            st.info("No hay simulacros registrados")

def render_plan_emergencia():
    """Plan de emergencia"""
    st.subheader("📋 Plan de Emergencia")
    
    plan = emergencia_service.get_plan_emergencia("empresa_default")
    
    with st.form("plan_emergencia_form"):
        objetivo = st.text_area("Objetivo del Plan", value=plan.get("objetivo", "") if plan else "")
        alcance = st.text_area("Alcance", value=plan.get("alcance", "") if plan else "")
        
        st.subheader("Puntos de Encuentro")
        puntos_text = st.text_area("Puntos de encuentro (uno por línea)", 
                                   value="\n".join([p.get("nombre") for p in plan.get("puntos_encuentro", [])]) if plan else "")
        
        st.subheader("Procedimientos de Emergencia")
        procedimientos_text = st.text_area("Procedimientos (uno por línea)", 
                                          value="\n".join([p.get("procedimiento") for p in plan.get("procedimientos", [])]) if plan else "")
        
        submitted = st.form_submit_button("💾 Guardar Plan de Emergencia", use_container_width=True)
        
        if submitted:
            data = {
                "objetivo": objetivo,
                "alcance": alcance,
                "puntos_encuentro": [{"nombre": p.strip()} for p in puntos_text.split("\n") if p.strip()],
                "procedimientos": [{"procedimiento": p.strip()} for p in procedimientos_text.split("\n") if p.strip()],
                "version": f"{(int(plan.get('version', '0').split('.')[0]) + 1) if plan else 1}.0",
                "fecha_aprobacion": datetime.now().strftime("%Y-%m-%d"),
                "empresa_id": "empresa_default"
            }
            if emergencia_service.save_plan_emergencia(data):
                st.success("✅ Plan de emergencia guardado")
                st.rerun()

def render_alertas():
    """Alertas de emergencia"""
    st.subheader("⚠️ Alertas de Emergencia")
    
    col1, col2 = st.columns(2)
    
    with col1:
        with st.form("nueva_alerta"):
            st.write("### Nueva Alerta")
            tipo = st.selectbox("Tipo", ["incendio", "sismo", "inundacion", "atentado", "accidente"])
            nivel = st.selectbox("Nivel", [n["nombre"] for n in NIVELES_ALERTA])
            ubicacion = st.text_input("Ubicación")
            descripcion = st.text_area("Descripción")
            contacto = st.text_input("Teléfono de contacto")
            
            if st.form_submit_button("🚨 ACTIVAR ALERTA", use_container_width=True):
                data = {
                    "tipo": tipo,
                    "nivel": nivel,
                    "ubicacion": ubicacion,
                    "descripcion": descripcion,
                    "telefono_contacto": contacto,
                    "reportado_por": "usuario",
                    "fecha_hora": datetime.now().isoformat(),
                    "empresa_id": "empresa_default"
                }
                if emergencia_service.create_alerta(data):
                    st.success("✅ Alerta activada")
                    st.rerun()
    
    with col2:
        st.write("### Alertas Activas")
        alertas = emergencia_service.get_alertas_activas("empresa_default")
        if alertas:
            for a in alertas:
                nivel_info = next((n for n in NIVELES_ALERTA if n["nombre"] == a.get("nivel")), {})
                color = nivel_info.get("color", "#e74c3c")
                st.markdown(f"""
                <div style="background: {color}20; border-left: 4px solid {color}; padding: 10px; margin: 5px 0; border-radius: 5px;">
                    <b>{a.get('tipo', 'N/A').upper()}</b> - Nivel {a.get('nivel', 'N/A')}<br>
                    📍 {a.get('ubicacion', 'N/A')}<br>
                    {a.get('descripcion', 'N/A')[:100]}<br>
                    <small>Reportado: {a.get('fecha_hora', 'N/A')[:19]}</small>
                </div>
                """, unsafe_allow_html=True)
                
                if st.button("Cerrar Alerta", key=f"cerrar_{a.get('id')}"):
                    emergencia_service.cerrar_alerta(a.get("id"), "usuario")
                    st.rerun()
        else:
            st.info("No hay alertas activas")

def render_reportes_emergencia():
    """Reportes de emergencias"""
    st.subheader("📊 Reportes de Emergencia")
    
    # Estadísticas
    brigadistas = emergencia_service.get_brigadistas("empresa_default")
    equipos = emergencia_service.get_equipos("empresa_default")
    stats = emergencia_service.get_estadisticas_simulacros("empresa_default")
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Brigadistas", len(brigadistas))
    with col2:
        st.metric("Equipos", len(equipos))
    with col3:
        st.metric("Simulacros", stats.get("total", 0))
    with col4:
        st.metric("Promedio Participantes", stats.get("promedio_participantes", 0))
    
    st.markdown("---")
    
    # Equipos por estado
    if equipos:
        estados = {}
        for e in equipos:
            estado = e.get("estado", "desconocido")
            estados[estado] = estados.get(estado, 0) + 1
        
        st.subheader("Distribución de Equipos")
        st.bar_chart(estados)
    
    st.markdown("---")
    
    # Exportar
    if st.button("📥 Exportar Reporte a Excel", use_container_width=True):
        excel_data = emergencia_service.generar_reporte_emergencias("empresa_default")
        if excel_data:
            st.download_button(
                "Descargar Excel",
                data=excel_data,
                file_name=f"reporte_emergencias_{datetime.now().strftime('%Y%m%d')}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
