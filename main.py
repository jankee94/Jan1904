import streamlit as st

st.set_page_config(page_title="SG-SST PHVA", page_icon="🔄", layout="wide")

# Login
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

# Sidebar
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/2917/2917995.png", width=80)
    menu = st.radio("Menu", [
        "Dashboard", "Diagnóstico IA", "Peligros", "Riesgos", "Plan de Acción", "Trabajadores", "Incidentes", "Chat IA"
    ])
    if st.button("Salir"):
        st.session_state.auth = False
        st.rerun()

# Render módulos
if menu == "Dashboard":
    from modules.dashboard import render
    render()
elif menu == "Diagnóstico IA":
    from modules.diagnostico_ia import render
    render()
elif menu == "Peligros":
    from modules.peligros import render
    render()
elif menu == "Riesgos":
    from modules.riesgos import render
    render()
elif menu == "Plan de Acción":
    from modules.acciones import render
    render()
elif menu == "Trabajadores":
    from modules.trabajadores import render
    render()
elif menu == "Incidentes":
    from modules.incidentes import render
    render()
elif menu == "Chat IA":
    from modules.chat_ia import render
    render()

st.markdown("---")
st.markdown("<center>DESARROLLADO POR JAN BENITEZ</center>", unsafe_allow_html=True)
