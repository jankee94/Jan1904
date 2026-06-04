import streamlit as st
import sys
import pandas as pd
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

st.set_page_config(page_title="SG-SST PHVA", page_icon="🔄", layout="wide")

from core.db import db
from core.ia_engine import ia
from core.logger import Logger

logger = Logger("main")

# Inicializar sesión
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
if "empresa_id" not in st.session_state:
    st.session_state.empresa_id = 1

# ============================================================
# LOGIN
# ============================================================
if not st.session_state.authenticated:
    st.title("🔐 SG-SST PHVA")
    st.markdown("### Sistema de Gestión de Seguridad y Salud en el Trabajo")
    
    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        user = st.text_input("Usuario")
        pwd = st.text_input("Contraseña", type="password")
        if st.button("Ingresar"):
            if user == "admin" and pwd == "sst2024":
                st.session_state.authenticated = True
                st.rerun()
            else:
                st.error("❌ Usuario: admin / Contraseña: sst2024")
    st.stop()

# ============================================================
# SIDEBAR
# ============================================================
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/2917/2917995.png", width=80)
    st.markdown(f"**Empresa:** {st.session_state.get('empresa_nombre', 'No registrada')}")
    st.markdown("---")
    
    menu = st.radio("📋 MENU", [
        "🏠 Dashboard",
        "🤖 Diagnóstico IA",
        "⚠️ Peligros (Fase 2)",
        "📊 Riesgos (Fase 3)",
        "✅ Acciones (Fase 4)",
        "👥 Trabajadores",
        "📝 Incidentes",
        "💬 Chat Experto"
    ])
    
    st.markdown("---")
    if st.button("🚪 Salir"):
        st.session_state.authenticated = False
        st.rerun()

# ============================================================
# OBTENER DATOS DE EMPRESA
# ============================================================
empresa = db.obtener_empresa()

# ============================================================
# DASHBOARD
# ============================================================
if menu == "🏠 Dashboard":
    st.title("📊 Dashboard SST")
    
    if empresa is None:
        st.warning("⚠️ **Primero realiza un Diagnóstico IA** para configurar tu empresa")
        st.info("Ve a 'Diagnóstico IA' y completa el formulario")
    else:
        stats = db.obtener_stats()
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("🏢 Empresa", empresa['nombre'][:20] if empresa else "-")
        with col2:
            st.metric("👥 Trabajadores", empresa['trabajadores'] if empresa else 0)
        with col3:
            st.metric("⚠️ Peligros", stats['total_peligros'])
        with col4:
            st.metric("✅ Acciones", stats['total_acciones'])
        
        st.markdown("---")
        
        # Mostrar diagnóstico guardado
        if empresa and empresa.get('diagnostico_ia'):
            with st.expander("📋 Ver Diagnóstico IA Generado"):
                st.markdown(empresa['diagnostico_ia'])
        
        # Gráficos
        peligros_df = db.obtener_peligros()
        if not peligros_df.empty:
            st.subheader("Distribución de Riesgos")
            nivel_counts = peligros_df['nivel_riesgo'].value_counts()
            st.bar_chart(nivel_counts)

# ============================================================
# DIAGNÓSTICO IA (CENTRAL)
# ============================================================
elif menu == "🤖 Diagnóstico IA":
    st.title("🤖 Diagnóstico Inteligente con IA")
    st.markdown("La IA analizará tu empresa y generará un diagnóstico completo que alimentará todos los módulos")
    st.markdown("---")
    
    with st.form("diagnostico_form"):
        col1, col2 = st.columns(2)
        with col1:
            nit = st.text_input("NIT *", value=empresa['nit'] if empresa else "")
            nombre = st.text_input("Nombre de la empresa *", value=empresa['nombre'] if empresa else "")
            trabajadores = st.number_input("Número de trabajadores *", min_value=1, value=int(empresa['trabajadores']) if empresa else 10)
        with col2:
            arl = st.selectbox("ARL", ["Positiva", "Sura", "Colpatria", "Bolivar"], 
                              index=["Positiva", "Sura", "Colpatria", "Bolivar"].index(empresa['arl']) if empresa and empresa['arl'] else 0)
            actividad = st.text_area("Actividad económica principal", value=empresa['actividad'] if empresa else "")
        
        generar = st.form_submit_button("🚀 GENERAR DIAGNÓSTICO CON IA", use_container_width=True)
    
    if generar:
        if not nit or not nombre:
            st.error("❌ NIT y Nombre son obligatorios")
        else:
            with st.spinner("🤖 IA analizando la información de la empresa..."):
                # Prompt para IA
                prompt = f"""
                Eres un experto en Seguridad y Salud en el Trabajo (SST) en Colombia.
                
                Realiza un diagnóstico completo para esta empresa:
                
                EMPRESA: {nombre}
                NIT: {nit}
                TRABAJADORES: {trabajadores}
                ARL: {arl}
                ACTIVIDAD: {actividad if actividad else 'No especificada'}
                
                GENERA UN INFORME PROFESIONAL QUE INCLUYA:
                
                1. **PELIGROS IDENTIFICADOS** (mínimo 5):
                   - Tipo (Físico, Químico, Biológico, Ergonómico, Psicosocial, Seguridad)
                   - Descripción
                   - Ubicación sugerida
                   - Probabilidad (1-4)
                   - Severidad (1-3)
                
                2. **RIESGOS PRIORITARIOS**:
                   - Nivel de riesgo por área
                   - Justificación
                
                3. **PLAN DE ACCIÓN SUGERIDO** (mínimo 3 acciones):
                   - Descripción
                   - Responsable sugerido
                   - Fecha límite (días)
                   - Prioridad
                
                4. **REQUISITOS LEGALES APLICABLES**:
                   - Decreto 1072/2015
                   - Resolución 0312/2019
                   - ISO 45001
                
                5. **RECOMENDACIONES GENERALES**
                
                FORMATO: Markdown profesional y detallado.
                """
                
                respuesta = ia.call_gemini(prompt)
                
                if not respuesta:
                    respuesta = ia.call_groq(prompt)
                
                if respuesta:
                    # Guardar empresa
                    db.guardar_empresa(nit, nombre, trabajadores, arl, actividad, respuesta)
                    st.session_state.empresa_nombre = nombre
                    
                    st.success("✅ **DIAGNÓSTICO COMPLETADO**")
                    st.markdown("---")
                    st.markdown(respuesta)
                    
                    # Extraer y guardar peligros sugeridos por IA
                    st.info("🤖 **La IA ha sugerido los siguientes peligros. Revisa y confirma en la sección Peligros:**")
                    
                    # Mostrar resumen
                    with st.expander("📋 Ver peligros sugeridos para registrar"):
                        st.markdown("""
                        **Los peligros identificados por IA serán pre-cargados en el módulo de Peligros**
                        
                        Ve a la sección **'Peligros (Fase 2)'** para:
                        - Revisar los peligros sugeridos
                        - Confirmar o modificar
                        - Agregar más peligros
                        """)
                    
                    if st.button("📋 Ir a Peligros sugeridos"):
                        st.rerun()
                else:
                    st.error("❌ Error al generar diagnóstico. Verifica las API keys.")

# ============================================================
# PELIGROS (Fase 2) - con sugerencias de IA
# ============================================================
elif menu == "⚠️ Peligros (Fase 2)":
    st.title("⚠️ FASE 2: Identificar Peligros (GTC-45)")
    
    if empresa is None:
        st.warning("⚠️ **Primero realiza un Diagnóstico IA**")
        st.info("Ve a 'Diagnóstico IA' para configurar tu empresa")
    else:
        tab1, tab2, tab3 = st.tabs(["📋 Lista de Peligros", "➕ Nuevo Peligro", "🤖 Sugerencias de IA"])
        
        with tab1:
            df = db.obtener_peligros()
            if not df.empty:
                st.dataframe(df[['id', 'tipo', 'descripcion', 'ubicacion', 'nivel_riesgo']], use_container_width=True)
                
                # Eliminar
                with st.expander("🗑️ Eliminar peligro"):
                    id_eliminar = st.number_input("ID a eliminar", min_value=1, step=1)
                    if st.button("Eliminar"):
                        db.eliminar_peligro(id_eliminar)
                        st.success("Eliminado")
                        st.rerun()
            else:
                st.info("📭 No hay peligros registrados")
        
        with tab2:
            with st.form("nuevo_peligro"):
                col1, col2 = st.columns(2)
                with col1:
                    tipo = st.selectbox("Tipo", ["Físico", "Químico", "Biológico", "Ergonómico", "Psicosocial", "Seguridad"])
                    descripcion = st.text_area("Descripción")
                    ubicacion = st.text_input("Ubicación/Área")
                with col2:
                    prob = st.slider("Probabilidad (1-4)", 1, 4, 2)
                    sev = st.slider("Severidad (1-3)", 1, 3, 2)
                    nivel = db.calcular_nivel(prob, sev)
                    st.info(f"**Nivel de riesgo:** {nivel}")
                
                if st.form_submit_button("💾 Guardar"):
                    if descripcion:
                        db.guardar_peligro(1, tipo, descripcion, ubicacion, prob, sev, 0)
                        st.success("Guardado")
                        st.rerun()
        
        with tab3:
            st.subheader("Peligros sugeridos por el Diagnóstico IA")
            if empresa and empresa.get('diagnostico_ia'):
                st.info("Los peligros identificados en el diagnóstico están listados arriba. Usa el formulario para agregarlos manualmente.")
                st.markdown("**Para facilitar el registro, puedes copiar los peligros sugeridos del diagnóstico:**")
                
                # Botón para sugerir peligros típicos por actividad
                actividad = empresa['actividad'].lower() if empresa.get('actividad') else ""
                
                peligros_tipicos = {
                    "construccion": ["Caídas en altura", "Ruido excesivo", "Polvo de sílice", "Manejo de cargas pesadas", "Herrramientas eléctricas"],
                    "manufactura": ["Atrapamiento por máquinas", "Químicos industriales", "Ruido", "Posturas forzadas", "Iluminación inadecuada"],
                    "oficina": ["Estrés laboral", "Posturas sedentarias", "Pantallas de computador", "Riesgo eléctrico", "Caídas al mismo nivel"]
                }
                
                for key, peligros_list in peligros_tipicos.items():
                    if key in actividad:
                        st.success(f"**Peligros típicos para {actividad}:**")
                        for p in peligros_list:
                            st.write(f"- {p}")
                        break
            else:
                st.warning("Realiza el diagnóstico IA primero")

# ============================================================
# RIESGOS (Fase 3)
# ============================================================
elif menu == "📊 Riesgos (Fase 3)":
    st.title("📊 FASE 3: Evaluación de Riesgos")
    
    if empresa is None:
        st.warning("⚠️ Primero realiza un Diagnóstico IA")
    else:
        peligros_df = db.obtener_peligros()
        
        if not peligros_df.empty:
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Total Peligros", len(peligros_df))
                nivel1 = len(peligros_df[peligros_df['nivel_riesgo'] == 'I'])
                st.metric("🔴 Riesgos Nivel I (Alto)", nivel1)
            with col2:
                st.subheader("Distribución")
                nivel_counts = peligros_df['nivel_riesgo'].value_counts()
                st.bar_chart(nivel_counts)
            
            st.markdown("---")
            st.subheader("Matriz de Riesgos")
            st.dataframe(peligros_df, use_container_width=True)
        else:
            st.info("📭 No hay peligros registrados. Ve a 'Peligros' primero")

# ============================================================
# ACCIONES (Fase 4)
# ============================================================
elif menu == "✅ Acciones (Fase 4)":
    st.title("✅ FASE 4: Plan de Acción")
    
    if empresa is None:
        st.warning("⚠️ Primero realiza un Diagnóstico IA")
    else:
        tab1, tab2 = st.tabs(["📋 Seguimiento", "➕ Nueva Acción"])
        
        with tab1:
            acciones_df = db.obtener_acciones()
            if not acciones_df.empty:
                for idx, row in acciones_df.iterrows():
                    col1, col2 = st.columns([3,1])
                    with col1:
                        st.markdown(f"**📌 {row['descripcion']}**")
                        st.caption(f"Responsable: {row['responsable']} | Límite: {row['fecha_limite']} | Prioridad: {row['prioridad']}")
                    with col2:
                        nuevo_estado = st.selectbox("Estado", ["Pendiente", "En progreso", "Completada"], 
                                                   index=["Pendiente", "En progreso", "Completada"].index(row['estado']),
                                                   key=f"estado_{row['id']}")
                        if nuevo_estado != row['estado']:
                            db.actualizar_estado_accion(row['id'], nuevo_estado)
                            st.rerun()
                    st.markdown("---")
            else:
                st.info("📭 No hay acciones registradas")
        
        with tab2:
            peligros_df = db.obtener_peligros()
            if not peligros_df.empty:
                with st.form("nueva_accion"):
                    peligro_id = st.selectbox("Peligro asociado", peligros_df['id'].tolist(),
                                             format_func=lambda x: f"{x} - {peligros_df[peligros_df['id']==x]['descripcion'].iloc[0][:50]}")
                    descripcion = st.text_area("Descripción")
                    responsable = st.text_input("Responsable")
                    fecha_limite = st.date_input("Fecha límite", datetime.now())
                    prioridad = st.selectbox("Prioridad", ["Alta", "Media", "Baja"])
                    
                    if st.form_submit_button("Guardar"):
                        db.guardar_accion(1, peligro_id, descripcion, responsable, fecha_limite, prioridad, 0)
                        st.success("Acción guardada")
                        st.rerun()
            else:
                st.warning("Primero registra peligros")

# ============================================================
# TRABAJADORES
# ============================================================
elif menu == "👥 Trabajadores":
    st.title("👥 Gestión de Trabajadores")
    
    tab1, tab2 = st.tabs(["📋 Lista", "➕ Nuevo"])
    
    with tab1:
        df = db.obtener_trabajadores()
        if not df.empty:
            st.dataframe(df, use_container_width=True)
        else:
            st.info("No hay trabajadores")
    
    with tab2:
        with st.form("nuevo_trabajador"):
            cedula = st.text_input("Cédula")
            nombre = st.text_input("Nombre")
            email = st.text_input("Email")
            cargo = st.text_input("Cargo")
            area = st.text_input("Área")
            if st.form_submit_button("Guardar"):
                db.guardar_trabajador(1, cedula, nombre, email, cargo, area)
                st.success("Guardado")
                st.rerun()

# ============================================================
# INCIDENTES
# ============================================================
elif menu == "📝 Incidentes":
    st.title("📝 Registro de Incidentes")
    
    with st.form("nuevo_incidente"):
        tipo = st.selectbox("Tipo", ["Accidente", "Incidente", "Enfermedad Laboral", "Casi accidente"])
        descripcion = st.text_area("Descripción")
        fecha = st.date_input("Fecha", datetime.now())
        lugar = st.text_input("Lugar")
        gravedad = st.selectbox("Gravedad", ["Leve", "Moderada", "Grave", "Mortal"])
        
        if st.form_submit_button("Registrar"):
            db.guardar_incidente(1, tipo, descripcion, fecha, lugar, gravedad)
            st.success("Incidente registrado")
            st.rerun()
    
    st.markdown("---")
    st.subheader("Historial de Incidentes")
    df = db.obtener_incidentes()
    if not df.empty:
        st.dataframe(df, use_container_width=True)

# ============================================================
# CHAT EXPERTO
# ============================================================
elif menu == "💬 Chat Experto":
    st.title("💬 Chat Experto SST")
    
    if "chat_messages" not in st.session_state:
        st.session_state.chat_messages = []
    
    for msg in st.session_state.chat_messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])
    
    if prompt := st.chat_input("Pregunta sobre SST..."):
        st.session_state.chat_messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # Contexto de la empresa si existe
        contexto = ""
        if empresa:
            contexto = f"""
            Contexto de la empresa:
            - Nombre: {empresa.get('nombre', 'No registrada')}
            - Trabajadores: {empresa.get('trabajadores', 0)}
            - Actividad: {empresa.get('actividad', 'No especificada')}
            """
        
        respuesta = ia.call_gemini(f"{contexto}\n\nPregunta: {prompt}")
        if not respuesta:
            respuesta = ia.call_groq(f"{contexto}\n\nPregunta: {prompt}")
        
        with st.chat_message("assistant"):
            st.markdown(respuesta or "Error al conectar con IA")
        
        st.session_state.chat_messages.append({"role": "assistant", "content": respuesta or "Error"})
