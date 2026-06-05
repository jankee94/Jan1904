import streamlit as st
from datetime import datetime, timedelta
from core.db import db
from core.ia_engine import ia

st.set_page_config(page_title="SG-SST PHVA", page_icon="🔄", layout="wide")

# Inicializar sesión
if "auth" not in st.session_state:
    st.session_state.auth = False
if "proceso_iniciado" not in st.session_state:
    st.session_state.proceso_iniciado = False

# ========== LOGIN ==========
if not st.session_state.auth:
    st.title("🔐 SG-SST PHVA")
    st.markdown("### Sistema de Gestión de Seguridad y Salud en el Trabajo")
    st.markdown("---")
    
    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        st.image("https://cdn-icons-png.flaticon.com/512/2917/2917995.png", width=100)
        user = st.text_input("Usuario", placeholder="admin")
        pwd = st.text_input("Contraseña", type="password", placeholder="••••••")
        
        if st.button("Ingresar al Sistema", use_container_width=True):
            if user == "admin" and pwd == "sst2024":
                st.session_state.auth = True
                st.rerun()
            else:
                st.error("❌ Usuario: admin / Contraseña: sst2024")
    
    st.markdown("---")
    st.markdown("<center>DESARROLLADO POR JAN BENITEZ</center>", unsafe_allow_html=True)
    st.stop()

# ========== PANTALLA DE BIENVENIDA ==========
if not st.session_state.proceso_iniciado:
    st.title("🔄 BIENVENIDO AL SISTEMA SG-SST PHVA")
    st.markdown("---")
    
    col1, col2 = st.columns([2,1])
    with col1:
        st.markdown("""
        ### 📋 ¿CÓMO FUNCIONA?
        
        **Paso 1:** Completa el diagnóstico IA con los datos de tu empresa
        **Paso 2:** La IA generará un diagnóstico completo
        **Paso 3:** Los datos se precargarán automáticamente en todos los módulos
        **Paso 4:** Revisa, completa y da seguimiento a cada fase
        
        ### ✅ FASES DEL CICLO PHVA
        
        | Fase | Módulo | Estado |
        |------|--------|--------|
        | 1 | Diagnóstico IA | ⬜ Pendiente |
        | 2 | Identificar Peligros | ⬜ Pendiente |
        | 3 | Evaluar Riesgos | ⬜ Pendiente |
        | 4 | Plan de Acción | ⬜ Pendiente |
        | 5 | Gestión de Trabajadores | ⬜ Pendiente |
        | 6 | Registro de Incidentes | ⬜ Pendiente |
        """)
    
    with col2:
        st.markdown("""
        <div style='
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 30px;
            border-radius: 20px;
            color: white;
            text-align: center;
        '>
            <h2>🚀</h2>
            <h3>¿LISTO PARA COMENZAR?</h3>
            <p>Completa el diagnóstico y la IA hará el trabajo pesado por ti.</p>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("🎯 COMENZAR PROCESO", use_container_width=True):
            st.session_state.proceso_iniciado = True
            st.rerun()
    
    st.markdown("---")
    st.markdown("<center>DESARROLLADO POR JAN BENITEZ</center>", unsafe_allow_html=True)
    st.stop()

# ========== SIDEBAR ==========
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/2917/2917995.png", width=80)
    
    empresa = db.obtener_empresa()
    if empresa:
        st.markdown(f"**🏢 {empresa.get('nombre', 'Empresa')[:30]}**")
        st.caption(f"📊 {empresa.get('trabajadores', 0)} trabajadores")
    
    st.markdown("---")
    
    menu = st.radio("📋 MENU", [
        "📊 Dashboard",
        "🤖 Diagnóstico IA",
        "⚠️ Peligros",
        "✅ Plan de Acción",
        "👥 Trabajadores",
        "📝 Incidentes",
        "💬 Chat IA"
    ])
    
    st.markdown("---")
    if st.button("🚪 Salir"):
        st.session_state.auth = False
        st.session_state.proceso_iniciado = False
        st.rerun()

# ========== OBTENER EMPRESA ==========
empresa = db.obtener_empresa()

# ========== DASHBOARD ==========
if menu == "📊 Dashboard":
    st.title("📊 Dashboard SST")
    
    if empresa:
        st.success(f"🏢 Empresa: **{empresa.get('nombre', '')}**")
        st.info(f"👥 {empresa.get('trabajadores', 0)} trabajadores | 🏥 ARL: {empresa.get('arl', '')}")
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("⚠️ Peligros", len(db.obtener_peligros()))
        with col2:
            st.metric("✅ Acciones", len(db.obtener_acciones()))
        with col3:
            st.metric("👥 Trabajadores", len(db.obtener_trabajadores()))
        
        if empresa.get('diagnostico'):
            with st.expander("📋 Ver diagnóstico completo"):
                st.markdown(empresa.get('diagnostico'))
    else:
        st.warning("⚠️ No hay empresa registrada. Ve a 'Diagnóstico IA' para comenzar.")

# ========== DIAGNÓSTICO IA ==========
elif menu == "🤖 Diagnóstico IA":
    st.title("🤖 DIAGNÓSTICO IA - FASE 1")
    st.markdown("Completa los datos y la IA generará un diagnóstico completo")
    st.markdown("---")
    
    with st.form("form_diagnostico"):
        st.subheader("📝 Datos de la empresa")
        
        col1, col2 = st.columns(2)
        with col1:
            nombre = st.text_input("Nombre de la empresa *", placeholder="Ej: Mi Empresa S.A.S.")
            trabajadores = st.number_input("Número de trabajadores *", min_value=1, value=10)
        with col2:
            nit = st.text_input("NIT (opcional)", placeholder="900.123.456-7")
            arl = st.selectbox("ARL *", ["Positiva", "Sura", "Colpatria", "Bolivar"])
        
        actividad = st.text_area("Actividad económica", placeholder="Ej: Construcción, Servicios, Manufactura...")
        
        st.info("🤖 La IA generará: peligros, riesgos, plan de acción y requisitos legales")
        
        if st.form_submit_button("🚀 GENERAR DIAGNÓSTICO", use_container_width=True):
            if not nombre:
                st.error("❌ El nombre de la empresa es obligatorio")
            else:
                with st.spinner("🤖 IA generando diagnóstico..."):
                    prompt = f"Diagnóstico SST para {nombre} con {trabajadores} trabajadores, ARL {arl}, actividad {actividad}. Incluye peligros, riesgos y plan de acción. Máximo 400 palabras."
                    respuesta = ia.call(prompt)
                    
                    if respuesta:
                        db.guardar_empresa(nombre, trabajadores, arl, respuesta)
                        
                        # Precargar peligros
                        peligros_base = [
                            ("Ergonómico", f"Posturas inadecuadas en {nombre}", 2, 2),
                            ("Seguridad", "Caídas al mismo nivel", 2, 2),
                            ("Psicosocial", "Estrés laboral", 2, 2),
                        ]
                        for p in peligros_base:
                            db.guardar_peligro(p[0], p[1], p[2], p[3])
                        
                        # Precargar acciones
                        fecha = datetime.now()
                        db.guardar_accion(f"Realizar matriz de riesgos para {nombre}", "SST", (fecha + timedelta(days=30)).strftime("%Y-%m-%d"))
                        db.guardar_accion("Capacitar al personal en prevención", "Coordinador", (fecha + timedelta(days=45)).strftime("%Y-%m-%d"))
                        
                        st.balloons()
                        st.success("✅ DIAGNÓSTICO COMPLETADO")
                        st.markdown(respuesta)
                        st.info(f"📋 Se precargaron {len(peligros_base)} peligros y 2 acciones")
                        
                        col1, col2 = st.columns(2)
                        with col1:
                            if st.button("⚠️ IR A PELIGROS"):
                                st.session_state.menu = "⚠️ Peligros"
                                st.rerun()
                        with col2:
                            if st.button("✅ IR A PLAN DE ACCIÓN"):
                                st.session_state.menu = "✅ Plan de Acción"
                                st.rerun()
                    else:
                        st.error("Error con IA. Verifica API key.")

# ========== PELIGROS ==========
elif menu == "⚠️ Peligros":
    st.title("⚠️ GESTIÓN DE PELIGROS - FASE 2")
    
    if not empresa:
        st.warning("⚠️ Primero completa el Diagnóstico IA")
    else:
        tab1, tab2 = st.tabs(["📋 Lista", "➕ Nuevo"])
        
        with tab1:
            df = db.obtener_peligros()
            if not df.empty:
                st.dataframe(df, use_container_width=True)
                with st.expander("Eliminar"):
                    id_elim = st.number_input("ID", min_value=1, step=1)
                    if st.button("Eliminar"):
                        db.eliminar_peligro(id_elim)
                        st.rerun()
            else:
                st.info("No hay peligros")
        
        with tab2:
            with st.form("form"):
                tipo = st.selectbox("Tipo", ["Físico", "Químico", "Biológico", "Ergonómico", "Psicosocial", "Seguridad"])
                desc = st.text_area("Descripción")
                prob = st.slider("Probabilidad", 1, 4, 2)
                sev = st.slider("Severidad", 1, 3, 2)
                if st.form_submit_button("Guardar"):
                    if desc:
                        db.guardar_peligro(tipo, desc, prob, sev)
                        st.rerun()

# ========== PLAN DE ACCIÓN ==========
elif menu == "✅ Plan de Acción":
    st.title("✅ PLAN DE ACCIÓN - FASE 4")
    
    if not empresa:
        st.warning("⚠️ Primero completa el Diagnóstico IA")
    else:
        tab1, tab2 = st.tabs(["📋 Seguimiento", "➕ Nueva"])
        
        with tab1:
            df = db.obtener_acciones()
            if not df.empty:
                for _, row in df.iterrows():
                    col1, col2 = st.columns([3,1])
                    with col1:
                        st.write(f"**{row['descripcion']}** - {row['responsable']}")
                    with col2:
                        nuevo = st.selectbox("Estado", ["Pendiente", "Completada"], key=row['id'])
                        if nuevo != row['estado']:
                            db.actualizar_estado(row['id'], nuevo)
                            st.rerun()
            else:
                st.info("No hay acciones")
        
        with tab2:
            with st.form("form"):
                desc = st.text_area("Descripción")
                resp = st.text_input("Responsable")
                if st.form_submit_button("Guardar"):
                    if desc:
                        db.guardar_accion(desc, resp, datetime.now().strftime("%Y-%m-%d"))
                        st.rerun()

# ========== TRABAJADORES ==========
elif menu == "👥 Trabajadores":
    st.title("👥 TRABAJADORES - FASE 5")
    
    tab1, tab2 = st.tabs(["📋 Lista", "➕ Nuevo"])
    
    with tab1:
        df = db.obtener_trabajadores()
        if not df.empty:
            st.dataframe(df, use_container_width=True)
    
    with tab2:
        with st.form("form"):
            nombre = st.text_input("Nombre")
            cedula = st.text_input("Cédula")
            cargo = st.text_input("Cargo")
            if st.form_submit_button("Guardar"):
                if nombre:
                    db.guardar_trabajador(nombre, cedula, cargo)
                    st.rerun()

# ========== INCIDENTES ==========
elif menu == "📝 Incidentes":
    st.title("📝 INCIDENTES - FASE 6")
    
    with st.form("form"):
        desc = st.text_area("Descripción")
        fecha = st.date_input("Fecha", datetime.now())
        if st.form_submit_button("Registrar"):
            if desc:
                db.guardar_incidente(desc, fecha.strftime("%Y-%m-%d"), "Leve")
                st.rerun()
    
    df = db.obtener_incidentes()
    if not df.empty:
        st.dataframe(df)

# ========== CHAT IA ==========
elif menu == "💬 Chat IA":
    st.title("💬 CHAT EXPERTO SST")
    
    if "msgs" not in st.session_state:
        st.session_state.msgs = []
    
    for msg in st.session_state.msgs:
        with st.chat_message(msg["role"]):
            st.write(msg["content"])
    
    if prompt := st.chat_input("Pregunta sobre SST..."):
        st.session_state.msgs.append({"role": "user", "content": prompt})
        respuesta = ia.call(prompt)
        st.session_state.msgs.append({"role": "assistant", "content": respuesta or "Error"})
        st.rerun()

st.markdown("---")
st.markdown("<center>DESARROLLADO POR JAN BENITEZ</center>", unsafe_allow_html=True)
