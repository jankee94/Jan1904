import streamlit as st
from datetime import datetime, timedelta
from core.db import db
from core.ia_engine import ia
from core.firebase_db import firebase_db

st.set_page_config(page_title="SG-SST PHVA", page_icon="🔄", layout="wide")

# Inicializar sesión
if "auth" not in st.session_state:
    st.session_state.auth = False
if "proceso_iniciado" not in st.session_state:
    st.session_state.proceso_iniciado = False
if "paso_actual" not in st.session_state:
    st.session_state.paso_actual = 1

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
    
    empresa = firebase_db.obtener_empresa() or db.obtener_empresa()
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
empresa = firebase_db.obtener_empresa() or db.obtener_empresa()

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
    st.markdown("Completa los datos y la IA generará un diagnóstico completo que alimentará todos los módulos")
    st.markdown("---")
    
    # Verificar si ya existe empresa
    if empresa:
        st.info(f"📌 Empresa actual: **{empresa.get('nombre', '')}**")
        if st.button("📝 ¿Deseas cambiar o actualizar la empresa?"):
            st.session_state.cambiar_empresa = True
            st.rerun()
        
        if not st.session_state.get("cambiar_empresa", False):
            with st.expander("Ver diagnóstico generado"):
                st.markdown(empresa.get('diagnostico', 'No hay diagnóstico aún'))
            
            st.markdown("---")
            st.subheader("🎯 Datos precargados automáticamente")
            
            col1, col2 = st.columns(2)
            with col1:
                st.success(f"⚠️ {len(db.obtener_peligros())} peligros precargados")
                if st.button("Ver Peligros"):
                    st.session_state.menu = "⚠️ Peligros"
                    st.rerun()
            with col2:
                st.success(f"✅ {len(db.obtener_acciones())} acciones precargadas")
                if st.button("Ver Plan de Acción"):
                    st.session_state.menu = "✅ Plan de Acción"
                    st.rerun()
            return
    
    # Formulario de diagnóstico
    with st.form("form_diagnostico"):
        st.subheader("📝 Datos de la empresa")
        
        col1, col2 = st.columns(2)
        with col1:
            nombre = st.text_input("Nombre de la empresa *", 
                                   value=empresa.get('nombre', '') if empresa else "",
                                   placeholder="Ej: Mi Empresa S.A.S.")
            trabajadores = st.number_input("Número de trabajadores *", 
                                          min_value=1, 
                                          value=empresa.get('trabajadores', 10) if empresa else 10)
        with col2:
            nit = st.text_input("NIT (opcional)", 
                               value=empresa.get('nit', '') if empresa else "",
                               placeholder="900.123.456-7")
            arl = st.selectbox("ARL *", ["Positiva", "Sura", "Colpatria", "Bolivar"],
                              index=["Positiva", "Sura", "Colpatria", "Bolivar"].index(empresa.get('arl', 'Positiva')) if empresa else 0)
        
        actividad = st.text_area("Actividad económica", 
                                 value=empresa.get('actividad', '') if empresa else "",
                                 placeholder="Ej: Construcción, Servicios, Manufactura, Comercio...")
        
        st.markdown("---")
        st.info("🤖 La IA generará: perfil de empresa, peligros identificados, riesgos prioritarios, plan de acción y requisitos legales")
        
        if st.form_submit_button("🚀 GENERAR DIAGNÓSTICO", use_container_width=True):
            if not nombre:
                st.error("❌ El nombre de la empresa es obligatorio")
            else:
                with st.spinner("🤖 IA analizando y generando diagnóstico completo..."):
                    prompt = f"""
                    Eres un experto en Seguridad y Salud en el Trabajo en Colombia.
                    
                    Genera un diagnóstico SST completo para:
                    
                    EMPRESA: {nombre}
                    NIT: {nit if nit else 'No especificado'}
                    TRABAJADORES: {trabajadores}
                    ARL: {arl}
                    ACTIVIDAD: {actividad if actividad else 'No especificada'}
                    
                    El diagnóstico debe incluir (formato claro):
                    
                    1. PERFIL DE LA EMPRESA: tamaño, nivel de riesgo, obligaciones legales
                    2. PELIGROS IDENTIFICADOS (mínimo 5 peligros específicos para esta actividad)
                    3. RIESGOS PRIORITARIOS (clasificados por nivel: Alto, Medio, Bajo)
                    4. PLAN DE ACCIÓN SUGERIDO (mínimo 3 acciones concretas con responsables y plazos)
                    5. REQUISITOS LEGALES (normas aplicables según tamaño y actividad)
                    6. RECOMENDACIONES GENERALES
                    
                    Sé específico y práctico. Máximo 800 palabras.
                    """
                    
                    respuesta = ia.call(prompt)
                    
                    if respuesta:
                        # Guardar en Firebase y SQLite
                        datos_empresa = {
                            'nombre': nombre,
                            'nit': nit,
                            'trabajadores': trabajadores,
                            'arl': arl,
                            'actividad': actividad,
                            'diagnostico': respuesta
                        }
                        
                        # Guardar en Firebase
                        try:
                            firebase_db.guardar_empresa(nombre, trabajadores, arl, respuesta)
                            st.success("✅ Datos guardados en Firebase Cloud")
                        except:
                            pass
                        
                        # Guardar en SQLite local
                        db.guardar_empresa(nombre, trabajadores, arl, respuesta)
                        
                        # PRECARGAR PELIGROS según actividad
                        peligros_precargados = [
                            ("Ergonómico", f"Posturas inadecuadas en {nombre}", 2, 2),
                            ("Seguridad", "Caídas al mismo nivel", 2, 2),
                            ("Psicosocial", "Estrés laboral por carga de trabajo", 2, 2),
                            ("Físico", "Iluminación y ventilación inadecuada", 2, 1),
                            ("Biológico", "Exposición a virus y bacterias", 2, 2),
                        ]
                        
                        # Agregar peligros específicos por actividad
                        if "construccion" in actividad.lower():
                            peligros_precargados.append(("Seguridad", "Trabajo en alturas", 3, 3))
                            peligros_precargados.append(("Físico", "Ruido y vibraciones", 3, 2))
                        elif "manufactura" in actividad.lower() or "produccion" in actividad.lower():
                            peligros_precargados.append(("Seguridad", "Atrapamiento por maquinaria", 3, 3))
                            peligros_precargados.append(("Químico", "Exposición a sustancias peligrosas", 2, 3))
                        
                        for p in peligros_precargados:
                            db.guardar_peligro(p[0], p[1], p[2], p[3])
                        
                        # PRECARGAR ACCIONES
                        fecha = datetime.now()
                        acciones_precargadas = [
                            (f"Realizar matriz de riesgos GTC-45 para {nombre}", "Responsable SST", (fecha + timedelta(days=30)).strftime("%Y-%m-%d")),
                            ("Capacitar a todo el personal en prevención de riesgos", "Coordinador SST", (fecha + timedelta(days=45)).strftime("%Y-%m-%d")),
                            ("Implementar programa de pausas activas", "Líder de área", (fecha + timedelta(days=15)).strftime("%Y-%m-%d")),
                            ("Adquirir y distribuir EPP según matriz de riesgos", "Compras", (fecha + timedelta(days=20)).strftime("%Y-%m-%d")),
                        ]
                        
                        for a in acciones_precargadas:
                            db.guardar_accion(a[0], a[1], a[2])
                        
                        st.balloons()
                        st.success("✅ DIAGNÓSTICO COMPLETADO EXITOSAMENTE")
                        st.markdown("---")
                        st.markdown(respuesta)
                        st.markdown("---")
                        
                        st.info(f"📋 Se han precargado {len(peligros_precargados)} peligros y {len(acciones_precargadas)} acciones")
                        
                        col1, col2 = st.columns(2)
                        with col1:
                            if st.button("⚠️ IR A PELIGROS", use_container_width=True):
                                st.session_state.menu = "⚠️ Peligros"
                                st.rerun()
                        with col2:
                            if st.button("✅ IR A PLAN DE ACCIÓN", use_container_width=True):
                                st.session_state.menu = "✅ Plan de Acción"
                                st.rerun()
                    else:
                        st.error("❌ Error al generar diagnóstico. Verifica la API key de Gemini en Secrets")

# ========== PELIGROS ==========
elif menu == "⚠️ Peligros":
    st.title("⚠️ GESTIÓN DE PELIGROS - FASE 2")
    
    if not empresa:
        st.warning("⚠️ Primero completa el Diagnóstico IA")
    else:
        tab1, tab2 = st.tabs(["📋 Lista de Peligros", "➕ Agregar Peligro"])
        
        with tab1:
            df = db.obtener_peligros()
            if not df.empty:
                st.dataframe(df, use_container_width=True)
                with st.expander("🗑️ Eliminar peligro"):
                    id_elim = st.number_input("ID del peligro", min_value=1, step=1)
                    if st.button("Eliminar"):
                        db.eliminar_peligro(id_elim)
                        st.rerun()
            else:
                st.info("📭 No hay peligros registrados")
        
        with tab2:
            with st.form("form_peligro"):
                col1, col2 = st.columns(2)
                with col1:
                    tipo = st.selectbox("Tipo", ["Físico", "Químico", "Biológico", "Ergonómico", "Psicosocial", "Seguridad"])
                    desc = st.text_area("Descripción detallada")
                with col2:
                    prob = st.slider("Probabilidad (1-4)", 1, 4, 2, help="1:Baja, 2:Media, 3:Alta, 4:Muy Alta")
                    sev = st.slider("Severidad (1-3)", 1, 3, 2, help="1:Ligero, 2:Dañino, 3:Extremo")
                    nivel = db.calcular_nivel(prob, sev) if hasattr(db, 'calcular_nivel') else "III"
                    st.info(f"📊 Nivel de riesgo: **{nivel}**")
                
                if st.form_submit_button("💾 Guardar Peligro", use_container_width=True):
                    if desc:
                        db.guardar_peligro(tipo, desc, prob, sev)
                        st.success("Peligro guardado")
                        st.rerun()

# ========== PLAN DE ACCIÓN ==========
elif menu == "✅ Plan de Acción":
    st.title("✅ PLAN DE ACCIÓN - FASE 4")
    
    if not empresa:
        st.warning("⚠️ Primero completa el Diagnóstico IA")
    else:
        tab1, tab2 = st.tabs(["📋 Seguimiento", "➕ Nueva Acción"])
        
        with tab1:
            df = db.obtener_acciones()
            if not df.empty:
                for _, row in df.iterrows():
                    with st.container():
                        col1, col2 = st.columns([3, 1])
                        with col1:
                            st.markdown(f"**📌 {row['descripcion']}**")
                            st.caption(f"Responsable: {row['responsable']} | Vence: {row['fecha']}")
                        with col2:
                            nuevo = st.selectbox("Estado", ["Pendiente", "En progreso", "Completada"], 
                                                key=f"act_{row['id']}",
                                                label_visibility="collapsed")
                            if hasattr(db, 'actualizar_estado') and nuevo != row.get('estado', 'Pendiente'):
                                db.actualizar_estado(row['id'], nuevo)
                                st.rerun()
                        st.markdown("---")
            else:
                st.info("📭 No hay acciones registradas")
        
        with tab2:
            with st.form("form_accion"):
                desc = st.text_area("Descripción de la acción")
                responsable = st.text_input("Responsable")
                fecha = st.date_input("Fecha límite", datetime.now())
                if st.form_submit_button("Guardar Acción"):
                    if desc and responsable:
                        db.guardar_accion(desc, responsable, fecha.strftime("%Y-%m-%d"))
                        st.success("Acción guardada")
                        st.rerun()

# ========== TRABAJADORES ==========
elif menu == "👥 Trabajadores":
    st.title("👥 GESTIÓN DE TRABAJADORES - FASE 5")
    
    tab1, tab2 = st.tabs(["📋 Lista", "➕ Nuevo Trabajador"])
    
    with tab1:
        df = db.obtener_trabajadores()
        if not df.empty:
            st.dataframe(df, use_container_width=True)
        else:
            st.info("📭 No hay trabajadores registrados")
    
    with tab2:
        with st.form("form_trabajador"):
            col1, col2 = st.columns(2)
            with col1:
                nombre = st.text_input("Nombre completo")
                cedula = st.text_input("Cédula")
            with col2:
                cargo = st.text_input("Cargo")
                area = st.text_input("Área/Dependencia")
            if st.form_submit_button("Registrar Trabajador"):
                if nombre:
                    db.guardar_trabajador(nombre, cedula, cargo)
                    st.success("Trabajador registrado")
                    st.rerun()

# ========== INCIDENTES ==========
elif menu == "📝 Incidentes":
    st.title("📝 REGISTRO DE INCIDENTES - FASE 6")
    
    with st.form("form_incidente"):
        desc = st.text_area("Descripción del incidente")
        col1, col2 = st.columns(2)
        with col1:
            fecha = st.date_input("Fecha del incidente", datetime.now())
        with col2:
            gravedad = st.selectbox("Gravedad", ["Leve", "Moderada", "Grave", "Mortal"])
        if st.form_submit_button("Registrar Incidente"):
            if desc:
                db.guardar_incidente(desc, fecha.strftime("%Y-%m-%d"), gravedad)
                st.success("Incidente registrado")
                st.rerun()
    
    st.markdown("---")
    st.subheader("Historial de Incidentes")
    df = db.obtener_incidentes()
    if not df.empty:
        st.dataframe(df, use_container_width=True)

# ========== CHAT IA ==========
elif menu == "💬 Chat IA":
    st.title("💬 CHAT EXPERTO EN SST")
    st.markdown("Consulta sobre normativa, riesgos, o cualquier tema de Seguridad y Salud en el Trabajo")
    
    if "chat_msgs" not in st.session_state:
        st.session_state.chat_msgs = []
    
    for msg in st.session_state.chat_msgs:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])
    
    if prompt := st.chat_input("Escribe tu pregunta sobre SST..."):
        st.session_state.chat_msgs.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
        
        contexto = ""
        if empresa:
            contexto = f"Contexto: Empresa {empresa.get('nombre', '')} del sector {empresa.get('actividad', '')} con {empresa.get('trabajadores', 0)} trabajadores.\n"
        
        with st.spinner("🤖 IA analizando..."):
            respuesta = ia.call(f"{contexto}Pregunta sobre SST: {prompt}")
        
        with st.chat_message("assistant"):
            st.markdown(respuesta or "Error al conectar con IA. Verifica API key.")
        st.session_state.chat_msgs.append({"role": "assistant", "content": respuesta or "Error"})