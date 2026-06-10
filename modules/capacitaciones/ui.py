# modules/capacitaciones/ui.py
import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import io
import base64
from PIL import Image

from core.services.capacitacion_service import capacitacion_service
from firebase.storage.storage_service import storage_service
from config.settings import settings

def render_capacitaciones():
    """Renderizar módulo de capacitaciones"""
    st.markdown("""
    <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 20px; border-radius: 15px; margin-bottom: 20px;">
        <h1 style="color: white; margin: 0;">📚 Gestión de Capacitaciones</h1>
        <p style="color: rgba(255,255,255,0.8); margin: 5px 0 0 0;">Programación, asistencia, evaluaciones y certificados</p>
    </div>
    """, unsafe_allow_html=True)
    
    tabs = st.tabs(["📋 Calendario", "➕ Programar", "📝 Asistencia", "📊 Evaluaciones", "📜 Certificados", "📈 Reportes"])
    
    with tabs[0]:
        render_calendario()
    
    with tabs[1]:
        render_programar_capacitacion()
    
    with tabs[2]:
        render_registro_asistencia()
    
    with tabs[3]:
        render_evaluaciones()
    
    with tabs[4]:
        render_certificados()
    
    with tabs[5]:
        render_reportes()

def render_calendario():
    """Mostrar calendario de capacitaciones"""
    st.subheader("📅 Calendario de Capacitaciones")
    
    # Filtros
    col1, col2, col3 = st.columns(3)
    with col1:
        mes = st.selectbox("Mes", list(range(1, 13)), index=datetime.now().month - 1)
    with col2:
        anio = st.selectbox("Año", list(range(2023, 2026)), index=datetime.now().year - 2023)
    with col3:
        estado = st.selectbox("Estado", ["Todas", "programada", "en_curso", "finalizada", "cancelada"])
    
    # Obtener capacitaciones
    capacitaciones = capacitacion_service.get_capacitaciones()
    
    # Filtrar
    if estado != "Todas":
        capacitaciones = [c for c in capacitaciones if c.get("estado") == estado]
    
    if capacitaciones:
        for cap in capacitaciones:
            fecha = cap.get("fecha_inicio", "")
            if fecha and fecha.startswith(f"{anio}-{mes:02d}"):
                with st.expander(f"📌 {cap.get('titulo', 'Sin título')} - {fecha}"):
                    col1, col2 = st.columns(2)
                    with col1:
                        st.write(f"**Modalidad:** {cap.get('modalidad', 'N/A')}")
                        st.write(f"**Duración:** {cap.get('duracion_horas', 0)} horas")
                        st.write(f"**Instructor:** {cap.get('instructor', 'N/A')}")
                    with col2:
                        cupos = cap.get("cupo_disponible", 0)
                        cupo_max = cap.get("cupo_maximo", 0)
                        st.write(f"**Cupos:** {cupos}/{cupo_max}")
                        st.write(f"**Estado:** {cap.get('estado', 'N/A')}")
                        st.progress(1 - (cupos / cupo_max) if cupo_max > 0 else 0)
                    
                    st.write(f"**Descripción:** {cap.get('descripcion', 'N/A')}")
    else:
        st.info("No hay capacitaciones programadas para este período")

def render_programar_capacitacion():
    """Formulario para programar capacitación"""
    st.subheader("➕ Programar Nueva Capacitación")
    
    with st.form("programar_capacitacion"):
        col1, col2 = st.columns(2)
        
        with col1:
            titulo = st.text_input("Título de la capacitación *")
            tipo = st.selectbox("Tipo", ["induccion", "entrenamiento", "actualizacion", "especializacion"])
            modalidad = st.selectbox("Modalidad", ["presencial", "virtual", "mixta"])
            duracion_horas = st.number_input("Duración (horas)", min_value=1, max_value=200, value=8)
            fecha_inicio = st.date_input("Fecha de inicio", datetime.now())
            hora_inicio = st.time_input("Hora de inicio", datetime.now().time())
        
        with col2:
            cupo_maximo = st.number_input("Cupo máximo", min_value=1, max_value=500, value=20)
            instructor = st.text_input("Instructor *")
            instructor_email = st.text_input("Email del instructor")
            instructor_telefono = st.text_input("Teléfono del instructor")
            lugar = st.text_input("Lugar")
        
        descripcion = st.text_area("Descripción")
        
        # Temario
        st.subheader("📋 Temario")
        temario_text = st.text_area("Temario (un tema por línea)", height=100)
        temario = [t.strip() for t in temario_text.split("\n") if t.strip()]
        
        # Objetivos
        st.subheader("🎯 Objetivos")
        objetivos_text = st.text_area("Objetivos (uno por línea)", height=100)
        objetivos = [o.strip() for o in objetivos_text.split("\n") if o.strip()]
        
        # Evaluación
        col1, col2 = st.columns(2)
        with col1:
            evaluacion_requerida = st.checkbox("Requiere evaluación", value=True)
        with col2:
            nota_aprobacion = st.number_input("Nota de aprobación (%)", min_value=0, max_value=100, value=70)
        
        submitted = st.form_submit_button("✅ Programar Capacitación", use_container_width=True)
        
        if submitted and titulo and instructor:
            data = {
                "titulo": titulo,
                "tipo": tipo,
                "modalidad": modalidad,
                "duracion_horas": duracion_horas,
                "fecha_inicio": fecha_inicio.strftime("%Y-%m-%d"),
                "hora_inicio": hora_inicio.strftime("%H:%M"),
                "cupo_maximo": cupo_maximo,
                "instructor": instructor,
                "instructor_email": instructor_email,
                "instructor_telefono": instructor_telefono,
                "lugar": lugar,
                "descripcion": descripcion,
                "temario": temario,
                "objetivos": objetivos,
                "evaluacion_requerida": evaluacion_requerida,
                "nota_aprobacion": nota_aprobacion
            }
            
            doc_id = capacitacion_service.create_capacitacion(data)
            if doc_id:
                st.success(f"✅ Capacitación '{titulo}' programada exitosamente")
                st.rerun()
            else:
                st.error("Error al programar la capacitación")

def render_registro_asistencia():
    """Registro de asistencia con firma digital"""
    st.subheader("📝 Registro de Asistencia")
    
    # Seleccionar capacitación
    capacitaciones = capacitacion_service.get_capacitaciones(estado="programada")
    if not capacitaciones:
        capacitaciones = capacitacion_service.get_capacitaciones(estado="en_curso")
    
    if not capacitaciones:
        st.info("No hay capacitaciones activas para registrar asistencia")
        return
    
    capacitacion_opts = {f"{c.get('titulo')} - {c.get('fecha_inicio')}": c.get('id') for c in capacitaciones}
    seleccion = st.selectbox("Seleccionar capacitación", list(capacitacion_opts.keys()))
    capacitacion_id = capacitacion_opts[seleccion]
    
    capacitacion = capacitacion_service.get_capacitacion(capacitacion_id)
    
    if capacitacion:
        st.write(f"**Cupos disponibles:** {capacitacion.get('cupo_disponible', capacitacion.get('cupo_maximo', 0))}/{capacitacion.get('cupo_maximo', 0)}")
        
        # Formulario de registro
        with st.form("registro_asistencia"):
            col1, col2 = st.columns(2)
            with col1:
                trabajador_id = st.text_input("ID del trabajador")
                trabajador_nombre = st.text_input("Nombre completo *")
                trabajador_cedula = st.text_input("Cédula *")
            with col2:
                trabajador_cargo = st.text_input("Cargo")
                trabajador_area = st.text_input("Área")
            
            # Firma digital
            st.subheader("✍️ Firma Digital")
            firma_data = st.text_input("Firma (pegar imagen base64 o usar componente)")
            
            submitted = st.form_submit_button("✅ Registrar Asistencia", use_container_width=True)
            
            if submitted and trabajador_nombre and trabajador_cedula:
                if capacitacion_service.registrar_asistencia(
                    capacitacion_id, trabajador_id, trabajador_nombre, trabajador_cedula, firma_data
                ):
                    st.success("✅ Asistencia registrada exitosamente")
                    st.rerun()
                else:
                    st.error("Error al registrar asistencia")

def render_evaluaciones():
    """Registro de evaluaciones"""
    st.subheader("📊 Registro de Evaluaciones")
    
    # Seleccionar capacitación
    capacitaciones = capacitacion_service.get_capacitaciones(estado="en_curso")
    capacitaciones += capacitacion_service.get_capacitaciones(estado="finalizada")
    
    if not capacitaciones:
        st.info("No hay capacitaciones para evaluar")
        return
    
    capacitacion_opts = {f"{c.get('titulo')} - {c.get('fecha_inicio')}": c.get('id') for c in capacitaciones}
    seleccion = st.selectbox("Seleccionar capacitación", list(capacitacion_opts.keys()))
    capacitacion_id = capacitacion_opts[seleccion]
    
    capacitacion = capacitacion_service.get_capacitacion(capacitacion_id)
    
    if capacitacion:
        asistentes = capacitacion.get("asistentes", [])
        asistentes_sin_evaluar = [a for a in asistentes if "evaluacion_nota" not in a]
        
        if asistentes_sin_evaluar:
            st.write(f"**Pendientes por evaluar:** {len(asistentes_sin_evaluar)}")
            
            for asistente in asistentes_sin_evaluar:
                with st.expander(f"📝 {asistente.get('trabajador_nombre')} - {asistente.get('trabajador_cedula')}"):
                    nota = st.slider("Nota (%)", 0, 100, 70, key=f"nota_{asistente.get('trabajador_id')}")
                    comentario = st.text_area("Comentario", key=f"comentario_{asistente.get('trabajador_id')}")
                    
                    if st.button("Registrar Evaluación", key=f"eval_{asistente.get('trabajador_id')}"):
                        if capacitacion_service.registrar_evaluacion(capacitacion_id, asistente.get("trabajador_id"), nota, comentario):
                            st.success("✅ Evaluación registrada")
                            st.rerun()
        else:
            st.success("✅ Todos los asistentes han sido evaluados")

def render_certificados():
    """Gestión de certificados"""
    st.subheader("📜 Certificados")
    
    # Buscar certificados por trabajador
    busqueda = st.text_input("Buscar por cédula o nombre")
    
    if busqueda:
        capacitaciones = capacitacion_service.get_capacitaciones()
        certificados = []
        
        for cap in capacitaciones:
            for asistente in cap.get("asistentes", []):
                if (busqueda in asistente.get("trabajador_nombre", "") or 
                    busqueda in asistente.get("trabajador_cedula", "")):
                    if asistente.get("certificado_url"):
                        certificados.append({
                            "capacitacion": cap.get("titulo"),
                            "fecha": cap.get("fecha_inicio"),
                            "trabajador": asistente.get("trabajador_nombre"),
                            "nota": asistente.get("evaluacion_nota", "N/A"),
                            "certificado_url": asistente.get("certificado_url")
                        })
        
        if certificados:
            for cert in certificados:
                with st.expander(f"📄 {cert['capacitacion']} - {cert['trabajador']}"):
                    st.write(f"**Fecha:** {cert['fecha']}")
                    st.write(f"**Nota:** {cert['nota']}%")
                    if cert['certificado_url']:
                        st.markdown(f"[📥 Descargar Certificado]({cert['certificado_url']})")
        else:
            st.info("No se encontraron certificados")

def render_reportes():
    """Reportes y estadísticas"""
    st.subheader("📈 Reportes de Capacitaciones")
    
    capacitaciones = capacitacion_service.get_capacitaciones()
    
    if capacitaciones:
        # Estadísticas generales
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Total Capacitaciones", len(capacitaciones))
        with col2:
            finalizadas = len([c for c in capacitaciones if c.get("estado") == "finalizada"])
            st.metric("Finalizadas", finalizadas)
        with col3:
            total_asistentes = sum(len(c.get("asistentes", [])) for c in capacitaciones)
            st.metric("Total Asistentes", total_asistentes)
        with col4:
            tasa_aprobacion = 0
            total_evaluados = 0
            for c in capacitaciones:
                for a in c.get("asistentes", []):
                    if "evaluacion_nota" in a:
                        total_evaluados += 1
                        if a.get("evaluacion_nota", 0) >= c.get("nota_aprobacion", 70):
                            tasa_aprobacion += 1
            tasa = (tasa_aprobacion / total_evaluados * 100) if total_evaluados > 0 else 0
            st.metric("Tasa Aprobación", f"{tasa:.0f}%")
        
        # Exportar reporte
        st.subheader("📥 Exportar Reporte")
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Exportar a Excel", use_container_width=True):
                reporte_data = []
                for c in capacitaciones:
                    for a in c.get("asistentes", []):
                        reporte_data.append({
                            "Capacitación": c.get("titulo"),
                            "Fecha": c.get("fecha_inicio"),
                            "Trabajador": a.get("trabajador_nombre"),
                            "Cédula": a.get("trabajador_cedula"),
                            "Asistió": "Sí" if a.get("asistio") else "No",
                            "Nota": a.get("evaluacion_nota", "N/A"),
                            "Certificado": "Sí" if a.get("certificado_url") else "No"
                        })
                
                df = pd.DataFrame(reporte_data)
                output = io.BytesIO()
                with pd.ExcelWriter(output, engine='openpyxl') as writer:
                    df.to_excel(writer, sheet_name="Reporte Capacitaciones", index=False)
                
                st.download_button(
                    "📥 Descargar Reporte Excel",
                    data=output.getvalue(),
                    file_name=f"reporte_capacitaciones_{datetime.now().strftime('%Y%m%d')}.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )
    else:
        st.info("No hay datos para generar reportes")
