import streamlit as st
import sys
import pandas as pd
from datetime import datetime, timedelta
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
    
    empresa = db.obtener_empresa()
    if empresa:
        st.markdown(f"**🏢 {empresa.get('nombre', 'Empresa')[:30]}**")
        st.caption(f"📊 {empresa.get('trabajadores', 0)} trabajadores")
    else:
        st.markdown("**🏢 Sin empresa registrada**")
    
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
# OBTENER DATOS
# ============================================================
empresa = db.obtener_empresa()

# ============================================================
# DASHBOARD
# ============================================================
if menu == "🏠 Dashboard":
    st.title("📊 Dashboard SST")
    
    if empresa is None:
        st.warning("⚠️ **Primero realiza un Diagnóstico IA**")
        st.info("Ve a 'Diagnóstico IA' e ingresa el NIT o nombre de la empresa")
    else:
        stats = db.obtener_stats()
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("🏢 Empresa", empresa.get('nombre', '-')[:25])
        with col2:
            st.metric("👥 Trabajadores", empresa.get('trabajadores', 0))
        with col3:
            st.metric("⚠️ Peligros", stats['total_peligros'])
        with col4:
            progreso = stats['acciones_completadas'] / stats['total_acciones'] * 100 if stats['total_acciones'] > 0 else 0
            st.metric("✅ Progreso", f"{progreso:.0f}%")
        
        st.markdown("---")
        
        if empresa and empresa.get('diagnostico_ia'):
            with st.expander("📋 Ver Diagnóstico IA Generado"):
                st.markdown(empresa['diagnostico_ia'])
        
        peligros_df = db.obtener_peligros()
        if not peligros_df.empty:
            st.subheader("Distribución de Riesgos por Nivel")
            nivel_counts = peligros_df['nivel_riesgo'].value_counts()
            st.bar_chart(nivel_counts)

# ============================================================
# DIAGNÓSTICO IA - CAMPO ÚNICO
# ============================================================
elif menu == "🤖 Diagnóstico IA":
    st.title("🤖 Diagnóstico Inteligente con IA")
    st.markdown("La IA analizará tu empresa y generará un **diagnóstico completo**")
    st.markdown("---")
    
    with st.form("diagnostico_form"):
        st.markdown("### 📋 Datos básicos de la empresa")
        
        identificador = st.text_input(
            "NIT o nombre de la empresa *", 
            value=empresa['nit'] if empresa and empresa.get('nit') else (empresa['nombre'] if empresa else ""),
            placeholder="Ej: 900.123.456-7 o Mi Empresa S.A.S."
        )
        
        col1, col2 = st.columns(2)
        with col1:
            trabajadores = st.number_input(
                "Número de trabajadores *", 
                min_value=1, 
                value=int(empresa['trabajadores']) if empresa and empresa.get('trabajadores') else 10
            )
        with col2:
            arl = st.selectbox(
                "ARL *", 
                ["Positiva", "Sura", "Colpatria", "Bolivar", "Otra"],
                index=["Positiva", "Sura", "Colpatria", "Bolivar", "Otra"].index(empresa['arl']) if empresa and empresa.get('arl') in ["Positiva", "Sura", "Colpatria", "Bolivar", "Otra"] else 0
            )
        
        st.markdown("---")
        st.caption("🤖 La IA generará automáticamente: actividad económica, peligros, riesgos, plan de acción y requisitos legales")
        
        generar = st.form_submit_button("🚀 GENERAR DIAGNÓSTICO CON IA", use_container_width=True)
    
    if generar:
        if not identificador:
            st.error("❌ Debes ingresar el NIT o nombre de la empresa")
        else:
            with st.spinner("🤖 IA generando diagnóstico completo..."):
                prompt = f"""
                Eres un experto en Seguridad y Salud en el Trabajo (SST) en Colombia.
                Basado en estos datos, genera un diagnóstico SST completo:
                
                DATOS DE LA EMPRESA:
                - Identificador (NIT o nombre): {identificador}
                - Número de trabajadores: {trabajadores}
                - ARL: {arl}
                
                INFORME A GENERAR (estructura profesional en Markdown):
                
                ## 1. PERFIL DE LA EMPRESA
                ## 2. PELIGROS IDENTIFICADOS (mínimo 6)
                ## 3. RIESGOS PRIORITARIOS
                ## 4. PLAN DE ACCIÓN SUGERIDO (mínimo 4 acciones)
                ## 5. REQUISITOS LEGALES APLICABLES
                ## 6. RECOMENDACIONES GENERALES
                """
                
                respuesta = ia.call_best(prompt)  # Usar call_best que intenta Gemini y Groq
                
                if respuesta:
                    db.guardar_empresa(
                        nit=identificador if identificador[0].isdigit() else "", 
                        nombre=identificador, 
                        trabajadores=trabajadores, 
                        arl=arl, 
                        actividad="", 
                        diagnostico_ia=respuesta
                    )
                    st.session_state.empresa_nombre = identificador
                    
                    st.balloons()
                    st.success("✅ **DIAGNÓSTICO GENERADO EXITOSAMENTE**")
                    st.markdown("---")
                    st.markdown(respuesta)
                    
                    # Guardar peligros base
                    peligros_base = [
                        ("Seguridad", "Caídas al mismo nivel", "Todas las áreas", 2, 2),
                        ("Ergonómico", "Posturas inadecuadas", "Oficinas", 2, 2),
                        ("Psicosocial", "Estrés laboral", "Administrativo", 2, 2),
                        ("Físico", "Iluminación inadecuada", "Todas las áreas", 2, 1),
                        ("Biológico", "Exposición a virus", "Áreas comunes", 2, 2),
                    ]
                    
                    for peligro in peligros_base:
                        db.guardar_peligro(1, peligro[0], peligro[1], peligro[2], peligro[3], peligro[4], 1)
                    
                    acciones_base = [
                        ("Realizar matriz de riesgos GTC-45", "Responsable SST", (datetime.now() + timedelta(days=30)).strftime("%Y-%m-%d"), "Alta"),
                        ("Capacitar personal en SST", "Coordinador SST", (datetime.now() + timedelta(days=45)).strftime("%Y-%m-%d"), "Alta"),
                        ("Implementar pausas activas", "Líder de área", (datetime.now() + timedelta(days=15)).strftime("%Y-%m-%d"), "Media"),
                    ]
                    
                    for accion in acciones_base:
                        db.guardar_accion(1, 0, accion[0], accion[1], accion[2], accion[3], 1)
                    
                    st.success(f"✅ Se han pre-cargado {len(peligros_base)} peligros y {len(acciones_base)} acciones")
                else:
                    st.error("❌ Error al generar diagnóstico. Verifica las API keys en Secrets.")

# ============================================================
# PELIGROS (Fase 2)
# ============================================================
elif menu == "⚠️ Peligros (Fase 2)":
    st.title("⚠️ FASE 2: Identificar Peligros (GTC-45)")
    
    if empresa is None:
        st.warning("⚠️ **Primero realiza un Diagnóstico IA**")
    else:
        tab1, tab2 = st.tabs(["📋 Lista de Peligros", "➕ Agregar Peligro"])
        
        with tab1:
            df = db.obtener_peligros()
            if not df.empty:
                st.dataframe(df[['id', 'tipo', 'descripcion', 'ubicacion', 'nivel_riesgo']], use_container_width=True)
                
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
                    if nivel == "I":
                        st.error(f"🔴 NIVEL I - RIESGO ALTO")
                    elif nivel == "II":
                        st.warning(f"🟠 NIVEL II - RIESGO MEDIO")
                    else:
                        st.info(f"🟡 NIVEL III - RIESGO BAJO")
                
                if st.form_submit_button("💾 Guardar Peligro"):
                    if descripcion:
                        db.guardar_peligro(1, tipo, descripcion, ubicacion, prob, sev, 0)
                        st.success("Peligro guardado")
                        st.rerun()

# ============================================================
# RIESGOS (Fase 3) - simplificado
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
                st.metric("🔴 Riesgos Nivel I", nivel1)
            with col2:
                nivel_counts = peligros_df['nivel_riesgo'].value_counts()
                st.bar_chart(nivel_counts)
            
            st.markdown("---")
            st.subheader("Matriz de Riesgos")
            for nivel in ['I', 'II', 'III']:
                riesgos_nivel = peligros_df[peligros_df['nivel_riesgo'] == nivel]
                if not riesgos_nivel.empty:
                    if nivel == 'I':
                        st.error(f"### 🔴 Nivel I")
                    elif nivel == 'II':
                        st.warning(f"### 🟠 Nivel II")
                    else:
                        st.info(f"### 🟡 Nivel III")
                    for _, row in riesgos_nivel.iterrows():
                        st.markdown(f"- **{row['tipo']}**: {row['descripcion'][:60]}")
        else:
            st.info("📭 No hay peligros registrados")

# ============================================================
# ACCIONES (Fase 4) - simplificado
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
                    col1, col2 = st.columns([3, 1])
                    with col1:
                        st.markdown(f"**📌 {row['descripcion']}**")
                        st.caption(f"Responsable: {row['responsable']} | Límite: {row['fecha_limite']}")
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
            with st.form("nueva_accion"):
                descripcion = st.text_area("Descripción")
                responsable = st.text_input("Responsable")
                fecha_limite = st.date_input("Fecha límite", datetime.now())
                prioridad = st.selectbox("Prioridad", ["Alta", "Media", "Baja"])
                
                if st.form_submit_button("Guardar"):
                    if descripcion and responsable:
                        db.guardar_accion(1, 0, descripcion, responsable, fecha_limite, prioridad, 0)
                        st.success("Guardado")
                        st.rerun()

# ============================================================
# TRABAJADORES
# ============================================================
elif menu == "👥 Trabajadores":
    st.title("👥 Gestión de Trabajadores")
    
    if empresa is None:
        st.warning("⚠️ Primero realiza un Diagnóstico IA")
    else:
        tab1, tab2 = st.tabs(["📋 Lista", "➕ Nuevo"])
        
        with tab1:
            df = db.obtener_trabajadores()
            if not df.empty:
                st.dataframe(df[['cedula', 'nombre', 'cargo', 'area']], use_container_width=True)
            else:
                st.info("📭 No hay trabajadores")
        
        with tab2:
            with st.form("nuevo_trabajador"):
                cedula = st.text_input("Cédula")
                nombre = st.text_input("Nombre")
                cargo = st.text_input("Cargo")
                area = st.text_input("Área")
                if st.form_submit_button("Guardar"):
                    if cedula and nombre:
                        db.guardar_trabajador(1, cedula, nombre, "", cargo, area)
                        st.success("Guardado")
                        st.rerun()

# ============================================================
# INCIDENTES
# ============================================================
elif menu == "📝 Incidentes":
    st.title("📝 Incidentes")
    
    if empresa is None:
        st.warning("⚠️ Primero realiza un Diagnóstico IA")
    else:
        with st.form("nuevo_incidente"):
            tipo = st.selectbox("Tipo", ["Accidente", "Incidente", "Enfermedad Laboral"])
            descripcion = st.text_area("Descripción")
            fecha = st.date_input("Fecha", datetime.now())
            lugar = st.text_input("Lugar")
            gravedad = st.selectbox("Gravedad", ["Leve", "Moderada", "Grave"])
            
            if st.form_submit_button("Registrar"):
                db.guardar_incidente(1, tipo, descripcion, fecha, lugar, gravedad)
                st.success("Registrado")
                st.rerun()
        
        st.markdown("---")
        df = db.obtener_incidentes()
        if not df.empty:
            st.dataframe(df)

# ============================================================
# CHAT IA
# ============================================================
elif menu == "💬 Chat Experto":
    st.title("💬 Chat Experto SST")
    
    if "chat" not in st.session_state:
        st.session_state.chat = []
    
    for msg in st.session_state.chat:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])
    
    if prompt := st.chat_input("Pregunta sobre SST..."):
        st.session_state.chat.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
        
        contexto = ""
        if empresa:
            contexto = f"Contexto: Empresa {empresa.get('nombre', '')} con {empresa.get('trabajadores', 0)} trabajadores.\n"
        
        respuesta = ia.call_best(f"{contexto}Pregunta SST: {prompt}")
        
        with st.chat_message("assistant"):
            st.markdown(respuesta or "Error - Verifica API keys")
        st.session_state.chat.append({"role": "assistant", "content": respuesta or "Error"})
