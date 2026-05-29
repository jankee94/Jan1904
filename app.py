import streamlit as st
from modules import trabajadores, peligros, capacitaciones, incidentes

st.set_page_config(page_title="SG-SST PHVA", page_icon="🛡️", layout="wide")

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

# Sidebar con navegación
with st.sidebar:
    st.image("https://img.icons8.com/color/96/000000/security-checked--v1.png", width=80)
    st.markdown("## 🛡️ SG-SST PHVA")
    st.markdown("---")
    
    menu = st.radio("📋 Módulos del Sistema", [
        "🏠 Dashboard",
        "👥 Trabajadores",
        "⚠️ Peligros GTC-45",
        "📚 Capacitaciones",
        "📝 Incidentes",
        "📅 Plan Anual SST",
        "🔍 Auditorías",
        "📊 Indicadores",
        "🤖 Asistente Guía IA",
        "📜 Políticas SST",
        "📋 Procedimientos",
        "👥 COPASST",
        "📈 Reportes",
        "⚖️ Matriz Legal",
        "🚨 Gestión de Riesgos",
        "🚒 Plan de Emergencias"
    ])
    
    st.markdown("---")
    st.caption("Desarrollado por: Ing. Jan Benitez & Ing. Neiris Pallares")

# Contenido principal
st.markdown('<div class="main-header"><h1>📊 SG-SST PHVA</h1><p>Planificar · Hacer · Verificar · Actuar</p></div>', unsafe_allow_html=True)

if menu == "🏠 Dashboard":
    col1, col2, col3, col4 = st.columns(4)
    with col1: st.metric("👥 Trabajadores", "24", "+2")
    with col2: st.metric("⚠️ Peligros", "8", "+1")
    with col3: st.metric("📊 Cumplimiento", "92%", "+5%")
    with col4: st.metric("✅ Módulos", "9/18", "50%")
    st.progress(50)
    st.info("💡 Usa el módulo **Asistente Guía IA** para construir tu sistema SST personalizado.")

elif menu == "👥 Trabajadores":
    trabajadores.show()
elif menu == "⚠️ Peligros GTC-45":
    peligros.show()
elif menu == "📚 Capacitaciones":
    capacitaciones.show()
elif menu == "📝 Incidentes":
    incidentes.show()
else:
    st.info(f"📌 Módulo '{menu}' - En desarrollo. Próximamente disponible con todas las funcionalidades.")
