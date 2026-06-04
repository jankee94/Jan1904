import streamlit as st
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

st.set_page_config(page_title="SG-SST PHVA", page_icon="🔄", layout="wide")

from core.db import Database
from core.ia_engine import IAEngine
from core.logger import Logger

db = Database("sst.db")
ia = IAEngine()
logger = Logger("main")

if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

if not st.session_state.authenticated:
    st.title("🔐 SG-SST PHVA")
    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        user = st.text_input("Usuario")
        pwd = st.text_input("Contraseña", type="password")
        if st.button("Ingresar"):
            if user == "admin" and pwd == "sst2024":
                st.session_state.authenticated = True
                st.rerun()
            else:
                st.error("Usuario: admin / Contraseña: sst2024")
    st.stop()

with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/2917/2917995.png", width=80)
    menu = st.radio("MENU", [
        "📊 Dashboard", "⚠️ Peligros", "📈 Riesgos", "✅ Acciones",
        "👥 Trabajadores", "📝 Incidentes", "🤖 Chat IA"
    ])
    if st.button("Salir"):
        st.session_state.authenticated = False
        st.rerun()

if menu == "📊 Dashboard":
    from modules.dashboard import render
    render(db, ia)
elif menu == "⚠️ Peligros":
    from modules.peligros import render
    render(db, ia, None)
elif menu == "📈 Riesgos":
    from modules.riesgos import render
    render(db, ia, None)
elif menu == "✅ Acciones":
    from modules.acciones import render
    render(db, ia, None)
elif menu == "👥 Trabajadores":
    from modules.trabajadores import render
    render(db, None)
elif menu == "📝 Incidentes":
    from modules.incidentes import render
    render(db, ia, None)
elif menu == "🤖 Chat IA":
    from modules.chat_ia import render
    render(db, ia, None)
