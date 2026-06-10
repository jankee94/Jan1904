# modules/inspecciones/ui.py
import streamlit as st
import pandas as pd
from datetime import datetime
import io

from core.services.inspeccion_service import inspeccion_service
from firebase.storage.storage_service import storage_service

def render_inspecciones():
    """Renderizar módulo de inspecciones"""
    st.markdown("""
    <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 20px; border-radius: 15px; margin-bottom: 20px;">
        <h1 style="color: white; margin: 0;">🔧 Gestión de Inspecciones</h1>
        <p style="color: rgba(255,255,255,0.8); margin: 5px 0 0 0;">Inspecciones locativas, equipos, EPP y más</p>
    </div>
    """, unsafe_allow_html=True)
    
    tabs = st.tabs(["📋 Programar", "✅ Realizar", "🔍 Hallazgos", "📊 Reportes"])
    
    with tabs[0]:
        render_programar_inspeccion()
    
    with tabs[1]:
        render_realizar_inspeccion()
    
    with tabs[2]:
        render_hallazgos()
    
    with tabs[3]:
        render_reportes_inspecciones()

def render_programar_inspeccion():
    """Programar nueva inspección"""
    st.subheader("📋 Programar Nueva Inspección")
    
    tipos = inspeccion_service.get_tipos_inspeccion()
    
    with st.form("programar_inspeccion"):
        col1, col2 = st.columns(2)
        
        with col1:
            tipo = st.selectbox("Tipo de Inspección", tipos)
            titulo = st.text_input("Título *")
            ubicacion = st.text_input("Ubicación *")
            fecha_programada = st.date_input("Fecha programada", datetime.now())
        
        with col2:
            inspector_nombre = st.text_input("Inspector *")
            inspector_cargo = st.text_input("Cargo del inspector")
            hora_inicio = st.time_input("Hora de inicio", datetime.now().time())
        
        descripcion = st.text_area("Descripción / Alcance")
        
        # Mostrar items del checklist predefinido
        checklist_predef = inspeccion_service.get_checklist_predefinido(tipo)
        if checklist_predef:
            st.info(f"📋 Checklist: {checklist_predef.get('nombre', '')} - {len(checklist_predef.get('items', []))} items")
        
        submitted = st.form_submit_button("✅ Programar Inspección", use_container_width=True)
        
        if submitted and titulo and ubicacion and inspector_nombre:
            checklist = []
            if checklist_predef:
                for item in checklist_predef.get("items", []):
                    checklist.append({
                        "item": item.get("item"),
                        "descripcion": item.get("descripcion"),
                        "peso": item.get("peso", 1),
                        "cumple": None,
                        "observacion": "",
                        "evidencia_url": ""
                    })
            
            data = {
                "tipo": tipo,
                "titulo": titulo,
                "descripcion": descripcion,
                "ubicacion": ubicacion,
                "fecha_programada": fecha_programada.strftime("%Y-%m-%d"),
                "hora_inicio": hora_inicio.strftime("%H:%M"),
                "inspector_nombre": inspector_nombre,
                "inspector_cargo": inspector_cargo,
                "checklist": checklist,
                "empresa_id": "empresa_default"
            }
            
            doc_id = inspeccion_service.create_inspeccion(data)
            if doc_id:
                st.success(f"✅ Inspección '{titulo}' programada exitosamente")
                st.rerun()
            else:
                st.error("Error al programar la inspección")

def render_realizar_inspeccion():
    """Realizar checklist de inspección"""
    st.subheader("✅ Realizar Inspección")
    
    inspecciones = inspeccion_service.get_inspecciones(estado="programada")
    if not inspecciones:
        st.info("No hay inspecciones programadas pendientes")
        return
    
    inspeccion_opts = {f"{c.get('titulo')} - {c.get('ubicacion')}": c.get('id') for c in inspecciones}
    seleccion = st.selectbox("Seleccionar inspección", list(inspeccion_opts.keys()))
    inspeccion_id = inspeccion_opts[seleccion]
    
    inspeccion = inspeccion_service.get_inspeccion(inspeccion_id)
    
    if inspeccion:
        st.write(f"**Tipo:** {inspeccion.get('tipo', 'N/A')}")
        st.write(f"**Ubicación:** {inspeccion.get('ubicacion', 'N/A')}")
        st.write(f"**Inspector:** {inspeccion.get('inspector_nombre', 'N/A')}")
        
        st.markdown("---")
        
        # Checklist
        st.subheader("📋 Checklist de Inspección")
        checklist = inspeccion.get("checklist", [])
        
        nuevo_checklist = []
        for i, item in enumerate(checklist):
            with st.container():
                col1, col2, col3 = st.columns([2, 1, 2])
                with col1:
                    st.write(f"**{item.get('item', 'N/A')}**")
                    st.caption(item.get('descripcion', ''))
                with col2:
                    cumple = st.selectbox("Cumple", ["Sí", "No", "N/A"], 
                                         index=0 if item.get("cumple") is True else 1 if item.get("cumple") is False else 2,
                                         key=f"check_{inspeccion_id}_{i}")
                with col3:
                    observacion = st.text_area("Observación", value=item.get("observacion", ""), key=f"obs_{inspeccion_id}_{i}")
                
                item["cumple"] = cumple == "Sí"
                item["observacion"] = observacion
                nuevo_checklist.append(item)
                st.markdown("---")
        
        # Registrar hallazgo
        st.subheader("🔍 Registrar Hallazgo")
        with st.expander("➕ Agregar Hallazgo"):
            descripcion_hallazgo = st.text_area("Descripción del hallazgo")
            tipo_hallazgo = st.selectbox("Tipo", ["leve", "grave", "critico"])
            responsable = st.text_input("Responsable de corrección")
            
            if st.button("Registrar Hallazgo"):
                if descripcion_hallazgo:
                    hallazgo = {
                        "descripcion": descripcion_hallazgo,
                        "tipo": tipo_hallazgo,
                        "prioridad": "alta" if tipo_hallazgo == "critico" else "media" if tipo_hallazgo == "grave" else "baja",
                        "responsable_nombre": responsable,
                        "created_at": datetime.now().isoformat()
                    }
                    if inspeccion_service.registrar_hallazgo(inspeccion_id, hallazgo):
                        st.success("✅ Hallazgo registrado")
                        st.rerun()
                    else:
                        st.error("Error al registrar hallazgo")
        
        # Finalizar
        col1, col2 = st.columns(2)
        with col1:
            if st.button("💾 Guardar Progreso", use_container_width=True):
                if inspeccion_service.registrar_checklist(inspeccion_id, nuevo_checklist):
                    st.success("✅ Progreso guardado")
                    st.rerun()
        
        with col2:
            if st.button("✅ Finalizar Inspección", use_container_width=True):
                inspeccion_service.registrar_checklist(inspeccion_id, nuevo_checklist)
                inspeccion_service.update_inspeccion(inspeccion_id, {
                    "estado": "completada",
                    "fecha_realizada": datetime.now().strftime("%Y-%m-%d"),
                    "hora_fin": datetime.now().strftime("%H:%M")
                })
                st.success("✅ Inspección finalizada")
                st.rerun()

def render_hallazgos():
    """Gestión de hallazgos"""
    st.subheader("🔍 Gestión de Hallazgos")
    
    inspecciones = inspeccion_service.get_inspecciones()
    
    if not inspecciones:
        st.info("No hay inspecciones registradas")
        return
    
    # Resumen de hallazgos
    total_hallazgos = 0
    hallazgos_abiertos = 0
    hallazgos_criticos = 0
    
    for ins in inspecciones:
        hallazgos = ins.get("hallazgos", [])
        total_hallazgos += len(hallazgos)
        hallazgos_abiertos += len([h for h in hallazgos if h.get("estado") != "cerrado"])
        hallazgos_criticos += len([h for h in hallazgos if h.get("tipo") == "critico"])
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Hallazgos", total_hallazgos)
    with col2:
        st.metric("Abiertos", hallazgos_abiertos)
    with col3:
        st.metric("Críticos", hallazgos_criticos)
    with col4:
        pct_cierre = ((total_hallazgos - hallazgos_abiertos) / total_hallazgos * 100) if total_hallazgos > 0 else 0
        st.metric("% Cierre", f"{pct_cierre:.0f}%")
    
    st.markdown("---")
    
    # Lista de hallazgos
    for ins in inspecciones:
        hallazgos = ins.get("hallazgos", [])
        if hallazgos:
            with st.expander(f"📌 {ins.get('titulo')} - {ins.get('ubicacion')}"):
                for h in hallazgos:
                    color = "🔴" if h.get("tipo") == "critico" else "🟠" if h.get("tipo") == "grave" else "🟡"
                    estado = "✅ Cerrado" if h.get("estado") == "cerrado" else "🟡 Abierto"
                    st.write(f"{color} **{h.get('tipo', 'leve').upper()}** - {h.get('descripcion')}")
                    st.write(f"   Responsable: {h.get('responsable_nombre', 'N/A')} | Estado: {estado}")
                    if h.get("estado") != "cerrado":
                        if st.button("Marcar como cerrado", key=f"cerrar_{h.get('id')}"):
                            inspeccion_service.cerrar_hallazgo(ins.get('id'), h.get('id'))
                            st.rerun()
                    st.markdown("---")

def render_reportes_inspecciones():
    """Reportes de inspecciones"""
    st.subheader("📊 Reportes de Inspecciones")
    
    inspecciones = inspeccion_service.get_inspecciones()
    
    if inspecciones:
        # Estadísticas por tipo
        tipos = {}
        for ins in inspecciones:
            tipo = ins.get("tipo", "otro")
            if tipo not in tipos:
                tipos[tipo] = {"total": 0, "aprobadas": 0}
            tipos[tipo]["total"] += 1
            if ins.get("calificacion", 0) >= 80:
                tipos[tipo]["aprobadas"] += 1
        
        st.subheader("📈 Estadísticas por Tipo")
        for tipo, stats in tipos.items():
            pct = (stats["aprobadas"] / stats["total"] * 100) if stats["total"] > 0 else 0
            st.metric(tipo.capitalize(), f"{stats['aprobadas']}/{stats['total']}", f"{pct:.0f}% aprobación")
        
        st.markdown("---")
        
        # Exportar
        col1, col2 = st.columns(2)
        with col1:
            if st.button("📥 Exportar a Excel", use_container_width=True):
                excel_data = inspeccion_service.exportar_inspecciones_excel(inspecciones)
                if excel_data:
                    st.download_button(
                        "Descargar Excel",
                        data=excel_data,
                        file_name=f"inspecciones_{datetime.now().strftime('%Y%m%d')}.xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                    )
        
        with col2:
            # Seleccionar inspección para PDF
            inspeccion_opts = {f"{c.get('titulo')}": c.get('id') for c in inspecciones if c.get("estado") == "completada"}
            if inspeccion_opts:
                seleccion = st.selectbox("Seleccionar para PDF", list(inspeccion_opts.keys()))
                if st.button("📄 Generar PDF", use_container_width=True):
                    pdf_data = inspeccion_service.generar_reporte_pdf(inspeccion_opts[seleccion])
                    if pdf_data:
                        st.download_button(
                            "Descargar PDF",
                            data=pdf_data,
                            file_name=f"informe_inspeccion_{datetime.now().strftime('%Y%m%d')}.pdf",
                            mime="application/pdf"
                        )
    else:
        st.info("No hay datos para generar reportes")
