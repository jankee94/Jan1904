import streamlit as st
from datetime import datetime

st.set_page_config(
    page_title="SG-SST PHVA",
    page_icon="🔄",
    layout="wide"
)

# CSS
st.markdown('''
<style>
    .stApp { background: linear-gradient(135deg, #0f0c29 0%, #302b63 50%, #24243e 100%); }
    header[data-testid="stHeader"] { display: none; }
    footer { display: none !important; }
    .main-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 20px;
        border-radius: 15px;
        margin-bottom: 20px;
    }
    .main-header h1 { color: white; margin: 0; }
    .card {
        background: rgba(255,255,255,0.1);
        backdrop-filter: blur(10px);
        border-radius: 15px;
        padding: 20px;
        margin: 10px 0;
    }
</style>
''', unsafe_allow_html=True)

# Login simple para pruebas
if "auth" not in st.session_state:
    st.session_state.auth = False
if "user" not in st.session_state:
    st.session_state.user = None

if not st.session_state.auth:
    col1, col2, col3 = st.columns([1, 1.5, 1])
    with col2:
        st.markdown('<div class="main-header"><h1 style="text-align:center">SG-SST PHVA</h1></div>', unsafe_allow_html=True)
        
        with st.form("login_form"):
            username = st.text_input("Usuario")
            password = st.text_input("Contraseña", type="password")
            
            if st.form_submit_button("Ingresar", use_container_width=True):
                if username == "admin" and password == "admin123":
                    st.session_state.auth = True
                    st.session_state.user = {"nombre": "Administrador"}
                    st.rerun()
                else:
                    st.error("Usuario o contraseña incorrectos. Use admin/admin123")
    st.stop()

# Sidebar
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/2917/2917995.png", width=50)
    st.markdown(f"### {st.session_state.user.get('nombre', 'Usuario')}")
    st.markdown("---")
    
    menu = st.radio("MÓDULOS", [
        "Dashboard",
        "Capacitaciones",
        "Inspecciones",
        "Emergencias",
        "Documentos",
        "Indicadores"
    ])
    
    if st.button("Cerrar Sesión", use_container_width=True):
        st.session_state.auth = False
        st.rerun()

# Dashboard
if menu == "Dashboard":
    st.markdown('<div class="main-header"><h1>Dashboard SST</h1></div>', unsafe_allow_html=True)
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Módulos Activos", "6")
    with col2:
        st.metric("Versión", "3.0")
    with col3:
        st.metric("Estado", "Online")
    with col4:
        st.metric("Última Actualización", datetime.now().strftime("%d/%m"))

# Capacitaciones
elif menu == "Capacitaciones":
    st.markdown('<div class="main-header"><h1>📚 Capacitaciones</h1></div>', unsafe_allow_html=True)
    
    tab1, tab2 = st.tabs(["Programar", "Lista"])
    
    with tab1:
        with st.form("programar_capacitacion"):
            titulo = st.text_input("Título de la capacitación")
            instructor = st.text_input("Instructor")
            fecha = st.date_input("Fecha", datetime.now())
            duracion = st.number_input("Duración (horas)", min_value=1, value=8)
            
            if st.form_submit_button("Programar"):
                st.success(f"✅ Capacitación '{titulo}' programada para {fecha}")

# Inspecciones
elif menu == "Inspecciones":
    st.markdown('<div class="main-header"><h1>🔧 Inspecciones</h1></div>', unsafe_allow_html=True)
    
    tipo = st.selectbox("Tipo de inspección", ["Locativa", "Equipos", "EPP", "Vehicular", "Andamios"])
    ubicacion = st.text_input("Ubicación")
    
    if st.button("Iniciar Inspección"):
        st.success(f"✅ Inspección {tipo} iniciada en {ubicacion}")

# Emergencias
elif menu == "Emergencias":
    st.markdown('<div class="main-header"><h1>🚨 Emergencias</h1></div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Brigadistas")
        st.info("3 brigadistas activos")
    with col2:
        st.subheader("Equipos")
        st.info("12 equipos registrados")

# Documentos
elif menu == "Documentos":
    st.markdown('<div class="main-header"><h1>📄 Documentos</h1></div>', unsafe_allow_html=True)
    
    uploaded = st.file_uploader("Subir documento", type=["pdf", "docx", "xlsx"])
    if uploaded:
        st.success(f"✅ Documento '{uploaded.name}' subido")

# Indicadores
elif menu == "Indicadores":
    st.markdown('<div class="main-header"><h1>📊 Indicadores SST</h1></div>', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Índice de Frecuencia", "2.5", delta="-0.3")
    with col2:
        st.metric("Cumplimiento PHVA", "85%", delta="+5%")
    with col3:
        st.metric("Tasa Accidentalidad", "3.2%", delta="-0.8%")

st.markdown("---")
st.markdown("<p style='text-align:center; color:gray'>SG-SST PHVA | Desarrollado por JAN BENITEZ</p>", unsafe_allow_html=True)
