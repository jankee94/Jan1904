import streamlit as st
from datetime import datetime, timedelta
from core.db import db
from core.ia_engine import ia

st.set_page_config(page_title="SG-SST PHVA", page_icon="🔄", layout="wide")

if "auth" not in st.session_state:
    st.session_state.auth = False

if not st.session_state.auth:
    st.title("🔐 SG-SST PHVA")
    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        user = st.text_input("Usuario")
        pwd = st.text_input("Contraseña", type="password")
        if st.button("Ingresar"):
            if user == "admin" and pwd == "sst2024":
                st.session_state.auth = True
                st.rerun()
            else:
                st.error("Usuario: admin / Contraseña: sst2024")
    st.stop()

with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/2917/2917995.png", width=80)
    menu = st.radio("MENU", [
        "📊 Dashboard",
        "🤖 Diagnóstico IA",
        "⚠️ Peligros",
        "✅ Plan de Acción",
        "👥 Trabajadores",
        "📝 Incidentes",
        "💬 Chat IA"
    ])
    if st.button("Salir"):
        st.session_state.auth = False
        st.rerun()

empresa = db.obtener_empresa()

if menu == "📊 Dashboard":
    st.title("📊 Dashboard SST")
    if empresa:
        st.success(f"Empresa: {empresa.get('nombre', '')}")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Peligros", len(db.obtener_peligros()))
    with col2:
        st.metric("Acciones", len(db.obtener_acciones()))
    with col3:
        st.metric("Trabajadores", len(db.obtener_trabajadores()))
    st.markdown("---")
    st.caption("DESARROLLADO POR JAN BENITEZ")

elif menu == "🤖 Diagnóstico IA":
    st.title("🤖 Diagnóstico IA")
    
    if empresa:
        st.success(f"✅ Empresa: {empresa.get('nombre', '')}")
        with st.expander("Ver diagnóstico"):
            st.write(empresa.get('diagnostico', ''))
        if st.button("⚠️ Ir a Peligros"):
            st.session_state.menu = "⚠️ Peligros"
            st.rerun()
    else:
        with st.form("form_diagnostico"):
            nombre = st.text_input("Nombre de la empresa")
            trabajadores = st.number_input("Trabajadores", min_value=1, value=10)
            arl = st.selectbox("ARL", ["Positiva", "Sura", "Colpatria"])
            if st.form_submit_button("Generar Diagnóstico"):
                if nombre:
                    with st.spinner("IA generando..."):
                        respuesta = ia.call(f"Diagnóstico SST para {nombre} con {trabajadores} trabajadores. Máximo 200 palabras.")
                        if respuesta:
                            db.guardar_empresa(nombre, trabajadores, arl, respuesta)
                            peligros = [("Ergonómico", f"Posturas en {nombre}", 2, 2), ("Seguridad", "Caídas", 2, 2)]
                            for p in peligros:
                                db.guardar_peligro(p[0], p[1], p[2], p[3])
                            fecha = datetime.now()
                            db.guardar_accion(f"Matriz de riesgos para {nombre}", "SST", (fecha + timedelta(days=30)).strftime("%Y-%m-%d"))
                            st.success("Diagnóstico generado")
                            st.rerun()

elif menu == "⚠️ Peligros":
    st.title("⚠️ Peligros")
    tab1, tab2 = st.tabs(["Lista", "Nuevo"])
    with tab1:
        df = db.obtener_peligros()
        if not df.empty:
            st.dataframe(df)
            with st.expander("Eliminar"):
                id_elim = st.number_input("ID", min_value=1, step=1)
                if st.button("Eliminar"):
                    db.eliminar_peligro(id_elim)
                    st.rerun()
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

elif menu == "✅ Plan de Acción":
    st.title("✅ Plan de Acción")
    tab1, tab2 = st.tabs(["Seguimiento", "Nueva"])
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
            fecha = st.date_input("Fecha límite", datetime.now())
            if st.form_submit_button("Guardar"):
                if desc:
                    db.guardar_accion(desc, resp, fecha.strftime("%Y-%m-%d"))
                    st.rerun()

elif menu == "👥 Trabajadores":
    st.title("👥 Trabajadores")
    tab1, tab2 = st.tabs(["Lista", "Nuevo"])
    with tab1:
        df = db.obtener_trabajadores()
        if not df.empty:
            st.dataframe(df)
        else:
            st.info("No hay trabajadores")
    with tab2:
        with st.form("form"):
            nombre = st.text_input("Nombre")
            cedula = st.text_input("Cédula")
            cargo = st.text_input("Cargo")
            if st.form_submit_button("Guardar"):
                if nombre:
                    db.guardar_trabajador(nombre, cedula, cargo)
                    st.rerun()

elif menu == "📝 Incidentes":
    st.title("📝 Incidentes")
    with st.form("form"):
        desc = st.text_area("Descripción")
        fecha = st.date_input("Fecha", datetime.now())
        gravedad = st.selectbox("Gravedad", ["Leve", "Moderada", "Grave"])
        if st.form_submit_button("Registrar"):
            if desc:
                db.guardar_incidente(desc, fecha.strftime("%Y-%m-%d"), gravedad)
                st.rerun()
    st.markdown("---")
    df = db.obtener_incidentes()
    if not df.empty:
        st.dataframe(df)

elif menu == "💬 Chat IA":
    st.title("💬 Chat IA")
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
