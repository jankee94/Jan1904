# modules/documental/ui.py
import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import io

from core.services.documento_service import documento_service
from core.data.tipos_documentos import TIPOS_DOCUMENTOS, CATEGORIAS_DOCUMENTOS

def render_documental():
    """Renderizar módulo de gestión documental"""
    st.markdown("""
    <div style="background: linear-gradient(135deg, #1a365d 0%, #2c5282 100%); padding: 20px; border-radius: 15px; margin-bottom: 20px;">
        <h1 style="color: white; margin: 0;">📄 Gestión Documental SG-SST</h1>
        <p style="color: rgba(255,255,255,0.8); margin: 5px 0 0 0;">Políticas, procedimientos, formatos y control documental</p>
    </div>
    """, unsafe_allow_html=True)
    
    tabs = st.tabs(["📁 Documentos", "➕ Nuevo Documento", "📋 Control Cambios", "⏰ Vencimientos", "📊 Reportes"])
    
    with tabs[0]:
        render_lista_documentos()
    
    with tabs[1]:
        render_crear_documento()
    
    with tabs[2]:
        render_control_cambios()
    
    with tabs[3]:
        render_vencimientos()
    
    with tabs[4]:
        render_reportes_documentos()

def render_lista_documentos():
    """Lista de documentos con filtros"""
    st.subheader("📁 Biblioteca Documental")
    
    # Filtros
    col1, col2, col3 = st.columns(3)
    with col1:
        tipo_filtro = st.selectbox("Tipo", ["Todos"] + [t["nombre"] for t in TIPOS_DOCUMENTOS])
    with col2:
        categoria_filtro = st.selectbox("Categoría", ["Todas"] + [c["nombre"] for c in CATEGORIAS_DOCUMENTOS])
    with col3:
        estado_filtro = st.selectbox("Estado", ["Todos", "borrador", "revision", "aprobado", "obsoleto"])
    
    # Obtener documentos
    documentos = documento_service.get_documentos("empresa_default")
    
    # Aplicar filtros
    if tipo_filtro != "Todos":
        tipo_id = next((t["id"] for t in TIPOS_DOCUMENTOS if t["nombre"] == tipo_filtro), None)
        documentos = [d for d in documentos if d.get("tipo") == tipo_id]
    
    if categoria_filtro != "Todas":
        cat_id = next((c["id"] for c in CATEGORIAS_DOCUMENTOS if c["nombre"] == categoria_filtro), None)
        documentos = [d for d in documentos if d.get("categoria") == cat_id]
    
    if estado_filtro != "Todos":
        documentos = [d for d in documentos if d.get("estado") == estado_filtro]
    
    if documentos:
        for doc in documentos:
            tipo_info = next((t for t in TIPOS_DOCUMENTOS if t["id"] == doc.get("tipo")), {})
            color_estado = {
                "aprobado": "#27ae60",
                "revision": "#f39c12",
                "borrador": "#95a5a6",
                "obsoleto": "#e74c3c"
            }.get(doc.get("estado"), "#95a5a6")
            
            with st.expander(f"{tipo_info.get('icono', '📄')} {doc.get('codigo')} - {doc.get('titulo')} (v{doc.get('version', '1.0')})"):
                col1, col2 = st.columns(2)
                with col1:
                    st.write(f"**Tipo:** {tipo_info.get('nombre', 'N/A')}")
                    st.write(f"**Categoría:** {doc.get('categoria', 'N/A')}")
                    st.write(f"**Responsable:** {doc.get('area_responsable', 'N/A')}")
                with col2:
                    st.write(f"**Estado:** <span style='color:{color_estado}'>{doc.get('estado', 'N/A')}</span>", unsafe_allow_html=True)
                    st.write(f"**Creado:** {doc.get('fecha_creacion', 'N/A')[:10]}")
                    if doc.get("fecha_vencimiento"):
                        st.write(f"**Vence:** {doc.get('fecha_vencimiento')}")
                
                st.write("**Descripción:**")
                st.write(doc.get("descripcion", "Sin descripción")[:200])
                
                st.markdown("---")
                col1, col2, col3 = st.columns(3)
                with col1:
                    if st.button("📄 Ver Documento", key=f"ver_{doc.get('id')}"):
                        st.info("Vista previa del documento")
                with col2:
                    if st.button("✏️ Editar", key=f"editar_{doc.get('id')}"):
                        st.session_state["editar_doc"] = doc.get("id")
                        st.rerun()
                with col3:
                    if st.button("🗑️ Eliminar", key=f"eliminar_{doc.get('id')}"):
                        if documento_service.delete_documento(doc.get("id")):
                            st.success("Documento eliminado")
                            st.rerun()
    else:
        st.info("No hay documentos que coincidan con los filtros")

def render_crear_documento():
    """Formulario para crear nuevo documento"""
    st.subheader("➕ Crear Nuevo Documento")
    
    with st.form("crear_documento"):
        col1, col2 = st.columns(2)
        with col1:
            tipo = st.selectbox("Tipo de Documento", 
                               [t["nombre"] for t in TIPOS_DOCUMENTOS])
            tipo_id = next((t["id"] for t in TIPOS_DOCUMENTOS if t["nombre"] == tipo), None)
            
            titulo = st.text_input("Título del Documento *")
            codigo = st.text_input("Código (ej: POL-SST-001) *")
        with col2:
            categoria = st.selectbox("Categoría", [c["nombre"] for c in CATEGORIAS_DOCUMENTOS])
            categoria_id = next((c["id"] for c in CATEGORIAS_DOCUMENTOS if c["nombre"] == categoria), None)
            
            area_responsable = st.text_input("Área Responsable")
        
        descripcion = st.text_area("Descripción")
        contenido = st.text_area("Contenido del Documento", height=200)
        
        col1, col2 = st.columns(2)
        with col1:
            fecha_vencimiento = st.date_input("Fecha de Vencimiento", 
                                             datetime.now() + timedelta(days=365))
            requiere_firma = st.checkbox("Requiere firma digital")
        with col2:
            version = st.text_input("Versión", "1.0")
            requiere_aprobacion = st.checkbox("Requiere aprobación", value=True)
        
        submitted = st.form_submit_button("✅ Crear Documento", use_container_width=True)
        
        if submitted and titulo and codigo:
            data = {
                "tipo": tipo_id,
                "categoria": categoria_id,
                "titulo": titulo,
                "codigo": codigo,
                "descripcion": descripcion,
                "contenido": contenido,
                "version": version,
                "area_responsable": area_responsable,
                "fecha_vencimiento": fecha_vencimiento.strftime("%Y-%m-%d"),
                "requiere_firma": requiere_firma,
                "requiere_aprobacion": requiere_aprobacion,
                "empresa_id": "empresa_default",
                "creado_por": "usuario_actual"
            }
            
            doc_id = documento_service.create_documento(data)
            if doc_id:
                st.success(f"✅ Documento '{titulo}' creado exitosamente")
                st.rerun()

def render_control_cambios():
    """Control de cambios de documentos"""
    st.subheader("📋 Control de Cambios")
    
    documentos = documento_service.get_documentos("empresa_default")
    
    if documentos:
        for doc in documentos:
            with st.expander(f"📌 {doc.get('codigo')} - {doc.get('titulo')} (v{doc.get('version')})"):
                # Historial de versiones
                historial = doc.get("historial_versiones", [])
                if historial:
                    st.write("**Historial de Versiones:**")
                    for h in historial:
                        st.write(f"- v{h.get('version')}: {h.get('cambios')} ({h.get('fecha')[:10]})")
                
                # Nueva versión
                st.markdown("---")
                cambios = st.text_area("Descripción de cambios para nueva versión", 
                                      key=f"cambios_{doc.get('id')}")
                if st.button("Crear Nueva Versión", key=f"nueva_ver_{doc.get('id')}"):
                    if cambios:
                        if documento_service.crear_nueva_version(doc.get("id"), cambios, "usuario_actual"):
                            st.success("✅ Nueva versión creada")
                            st.rerun()
                    else:
                        st.warning("Ingrese la descripción de los cambios")
    else:
        st.info("No hay documentos registrados")

def render_vencimientos():
    """Alertas de documentos por vencer"""
    st.subheader("⏰ Alertas de Vencimiento")
    
    # Documentos por vencer
    por_vencer = documento_service.get_documentos_por_vencer("empresa_default", 30)
    if por_vencer:
        st.warning(f"⚠️ {len(por_vencer)} documentos están por vencer en los próximos 30 días")
        for doc in por_vencer:
            st.write(f"- **{doc.get('codigo')}** - {doc.get('titulo')} (Vence: {doc.get('fecha_vencimiento')})")
    else:
        st.success("✅ No hay documentos por vencer")
    
    st.markdown("---")
    
    # Documentos vencidos
    vencidos = documento_service.get_documentos_vencidos("empresa_default")
    if vencidos:
        st.error(f"❌ {len(vencidos)} documentos están VENCIDOS")
        for doc in vencidos:
            st.write(f"- **{doc.get('codigo')}** - {doc.get('titulo')} (Vencido: {doc.get('fecha_vencimiento')})")
            
            col1, col2 = st.columns([3, 1])
            with col2:
                if st.button("Revisar", key=f"revisar_{doc.get('id')}"):
                    st.info(f"Programar revisión para {doc.get('titulo')}")
    else:
        st.success("✅ No hay documentos vencidos")

def render_reportes_documentos():
    """Reportes de documentos"""
    st.subheader("📊 Reportes Documentales")
    
    documentos = documento_service.get_documentos("empresa_default")
    
    if documentos:
        # Estadísticas por tipo
        tipos_count = {}
        for doc in documentos:
            tipo = doc.get("tipo", "otro")
            tipos_count[tipo] = tipos_count.get(tipo, 0) + 1
        
        st.subheader("📈 Documentos por Tipo")
        st.bar_chart(tipos_count)
        
        # Estadísticas por estado
        estados_count = {}
        for doc in documentos:
            estado = doc.get("estado", "borrador")
            estados_count[estado] = estados_count.get(estado, 0) + 1
        
        st.subheader("📊 Documentos por Estado")
        st.bar_chart(estados_count)
        
        st.markdown("---")
        
        # Exportar
        if st.button("📥 Exportar Inventario a Excel", use_container_width=True):
            excel_data = documento_service.exportar_documentos_excel(documentos)
            if excel_data:
                st.download_button(
                    "Descargar Excel",
                    data=excel_data,
                    file_name=f"inventario_documentos_{datetime.now().strftime('%Y%m%d')}.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )
    else:
        st.info("No hay documentos para generar reportes")
