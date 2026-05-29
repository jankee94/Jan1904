import streamlit as st
import json
from assistant_guide import AssistantGuide
from chat import chat_floating_button

st.set_page_config(page_title="SG-SST PHVA", page_icon="🛡️", layout="wide")

# Inicializar asistente
if "guide" not in st.session_state:
    st.session_state.guide = AssistantGuide()
if "company_data" not in st.session_state:
    st.session_state.company_data = {}
if "step" not in st.session_state:
    st.session_state.step = 0  # 0: bienvenida, 1: recolección, 2: generación

st.markdown("""
<style>
.main-header {
    background: linear-gradient(135deg, #0b3b5f, #1b5a7a);
    padding: 1.5rem;
    border-radius: 20px;
    color: white;
    text-align: center;
    margin-bottom: 2rem;
}
</style>
""", unsafe_allow_html=True)

def show_guide():
    st.markdown('<div class="main-header"><h1>🛡️ Asistente Guía SST</h1><p>Construye tu sistema SG-SST paso a paso</p></div>', unsafe_allow_html=True)
    
    # Panel de carga de documentos
    with st.expander("📄 Subir documentos (normativas, políticas existentes)"):
        uploaded_file = st.file_uploader("Selecciona PDF o DOCX", type=["pdf", "docx"])
        if uploaded_file:
            if uploaded_file.type == "application/pdf":
                text = st.session_state.guide.extract_text_from_pdf(uploaded_file)
            else:
                text = st.session_state.guide.extract_text_from_docx(uploaded_file)
            st.session_state.company_data["documentos_extra"] = text[:3000]  # limitar
            st.success("Documento procesado. La IA lo tendrá en cuenta.")
    
    # Formulario de datos de la empresa
    with st.form("datos_empresa"):
        nombre = st.text_input("Nombre de la empresa", value=st.session_state.company_data.get("nombre", ""))
        sector = st.selectbox("Sector económico", ["Construcción", "Manufactura", "Servicios", "Minero", "Agropecuario", "Salud", "Otro"])
        empleados = st.number_input("Número de empleados", min_value=1, step=1, value=st.session_state.company_data.get("empleados", 10))
        riesgos = st.text_area("Principales riesgos (separados por comas)", value=st.session_state.company_data.get("riesgos", ""))
        normativa = st.text_area("Normativa aplicable (opcional)", value=st.session_state.company_data.get("normativa", ""))
        submitted = st.form_submit_button("Generar estructura completa")
    
    if submitted:
        st.session_state.company_data.update({
            "nombre": nombre, "sector": sector, "empleados": empleados,
            "riesgos": riesgos, "normativa": normativa
        })
        with st.spinner("La IA está construyendo tu sistema SST..."):
            estructura = st.session_state.guide.generar_estructura_completa(
                st.session_state.company_data,
                normativa_aplicable=normativa
            )
            st.session_state.estructura = estructura
            st.success("✅ Estructura generada")
    
    if "estructura" in st.session_state:
        st.markdown("## 📋 Resultado generado por IA")
        try:
            data = json.loads(st.session_state.estructura)
            tab1, tab2, tab3, tab4 = st.tabs(["📊 Estructura de Datos", "📄 Documentos", "👥 Cargos", "✅ Plan de Acción"])
            with tab1:
                st.json(data.get("ESTRUCTURA DE DATOS", {}))
            with tab2:
                st.markdown(data.get("DOCUMENTOS REQUERIDOS", ""))
                if st.button("Generar Política SST"):
                    politica = st.session_state.guide.generar_documento_politica(st.session_state.company_data)
                    st.download_button("Descargar Política", politica, file_name="politica_sst.md")
            with tab3:
                st.markdown(data.get("CARGOS Y RESPONSABILIDADES", ""))
            with tab4:
                st.markdown(data.get("PLAN DE ACCIÓN", ""))
        except:
            st.markdown(st.session_state.estructura)

def dashboard_normal():
    st.markdown('<div class="main-header"><h1>📊 Dashboard SG-SST</h1></div>', unsafe_allow_html=True)
    col1, col2, col3, col4 = st.columns(4)
    with col1: st.metric("👥 Trabajadores", "24", "+2")
    with col2: st.metric("⚠️ Peligros", "8", "+1")
    with col3: st.metric("📊 Cumplimiento", "92%", "+5%")
    with col4: st.metric("✅ Módulos", "9/18", "50%")
    st.info("💡 Usa el botón flotante 💬 para iniciar el asistente guía.")

menu = st.sidebar.radio("Navegación", ["Dashboard", "Asistente Guía", "Módulos SST"])
if menu == "Dashboard":
    dashboard_normal()
elif menu == "Asistente Guía":
    show_guide()
else:
    st.info("Módulos en desarrollo...")

# Agregar chat flotante en todas las páginas
chat_floating_button()
