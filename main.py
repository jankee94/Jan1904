import streamlit as st
import pandas as pd
from datetime import datetime
import io

st.set_page_config(page_title="SG-SST PHVA", page_icon="🔄", layout="wide")

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
    .main-header h1 { color: white; margin: 0; font-size: 1.8rem; }
    .metric-card {
        background: rgba(255,255,255,0.15);
        border-radius: 12px;
        padding: 15px;
        text-align: center;
    }
    .metric-value { font-size: 2rem; font-weight: bold; color: #667eea; }
    .metric-label { font-size: 0.8rem; color: rgba(255,255,255,0.7); }
    .alert-warning { background: #f39c12; color: white; padding: 10px; border-radius: 8px; margin: 5px 0; }
    .alert-danger { background: #e74c3c; color: white; padding: 10px; border-radius: 8px; margin: 5px 0; }
</style>
''', unsafe_allow_html=True)

# ========== DATOS DE PRUEBA MULTIEMPRESA ==========
def init_multiempresa():
    if "empresas" not in st.session_state:
        st.session_state.empresas = {
            "empresa_1": {
                "nombre": "Constructora Segura SAS",
                "nit": "901.234.567-8",
                "plan": "profesional",
                "trabajadores": [
                    {"id": 1, "nombre": "Carlos Lopez", "cedula": "12345678", "cargo": "Operario"},
                    {"id": 2, "nombre": "Maria Gomez", "cedula": "87654321", "cargo": "Supervisor"},
                ],
                "peligros": [
                    {"id": 1, "tipo": "Fisico", "descripcion": "Ruido excesivo", "nivel": "I"},
                ],
                "incidentes": [
                    {"id": 1, "descripcion": "Caida desde andamio", "fecha": "2024-10-15", "gravedad": "Grave"},
                ]
            },
            "empresa_2": {
                "nombre": "Industrias Metalicas SA",
                "nit": "901.876.543-2",
                "plan": "basico",
                "trabajadores": [
                    {"id": 1, "nombre": "Pedro Ramirez", "cedula": "11122233", "cargo": "Soldador"},
                    {"id": 2, "nombre": "Ana Torres", "cedula": "44455566", "cargo": "Inspector"},
                ],
                "peligros": [
                    {"id": 1, "tipo": "Quimico", "descripcion": "Humos de soldadura", "nivel": "I"},
                ],
                "incidentes": [
                    {"id": 1, "descripcion": "Quemadura", "fecha": "2024-11-01", "gravedad": "Moderada"},
                ]
            }
        }
    
    if "current_empresa" not in st.session_state:
        st.session_state.current_empresa = "empresa_1"
    
    if "auth" not in st.session_state:
        st.session_state.auth = False
    if "current_user" not in st.session_state:
        st.session_state.current_user = None
    if "user_role" not in st.session_state:
        st.session_state.user_role = "admin"

def exportar_excel(data, nombre):
    df = pd.DataFrame(data)
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, sheet_name=nombre, index=False)
    return output.getvalue()

init_multiempresa()

# ========== LOGIN ==========
if not st.session_state.auth:
    col1, col2, col3 = st.columns([1, 1.5, 1])
    with col2:
        st.markdown('''
        <div style="background: rgba(20,20,40,0.8); backdrop-filter: blur(14px); border-radius: 28px; padding: 40px; text-align:center">
            <img src="https://cdn-icons-png.flaticon.com/512/2917/2917995.png" width="70">
            <h1 style="color:white;">SG-SST PHVA</h1>
            <p style="color:rgba(255,255,255,0.6)">Sistema Multiempresa de Gestión SST</p>
        </div>
        ''', unsafe_allow_html=True)
        
        with st.form("login_form"):
            username = st.text_input("Usuario", placeholder="admin")
            password = st.text_input("Contraseña", type="password", placeholder="admin123")
            
            col1, col2 = st.columns(2)
            with col1:
                if st.form_submit_button("Ingresar", use_container_width=True):
                    if username == "admin" and password == "admin123":
                        st.session_state.auth = True
                        st.session_state.current_user = {"nombre": "Administrador", "rol": "admin"}
                        st.rerun()
                    else:
                        st.error("Credenciales incorrectas")
            with col2:
                if st.form_submit_button("Recuperar Contraseña", use_container_width=True):
                    st.info("Contacte al administrador del sistema")
        
        st.markdown('<p style="text-align:center; font-size:11px; color:gray">SG-SST PHVA | JAN BENITEZ</p>', unsafe_allow_html=True)
    st.stop()

# ========== SIDEBAR MULTIEMPRESA ==========
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/2917/2917995.png", width=50)
    st.markdown(f"### {st.session_state.current_user.get('nombre', 'Usuario')}")
    st.caption(f"Rol: {st.session_state.user_role.upper() if st.session_state.user_role else 'ADMIN'}")
    st.markdown("---")
    
    # Selector de empresa (solo admin)
    if st.session_state.current_user.get("rol") == "admin":
        empresas_opciones = list(st.session_state.empresas.keys())
        empresas_nombres = [st.session_state.empresas[e]["nombre"] for e in empresas_opciones]
        idx = empresas_opciones.index(st.session_state.current_empresa) if st.session_state.current_empresa in empresas_opciones else 0
        
        empresa_seleccionada = st.selectbox("Empresa", empresas_nombres, index=idx)
        st.session_state.current_empresa = empresas_opciones[empresas_nombres.index(empresa_seleccionada)]
        
        st.markdown(f"**Plan:** {st.session_state.empresas[st.session_state.current_empresa]['plan'].upper()}")
        st.markdown("---")
    
    # Menú principal
    menu = st.radio("MÓDULOS", [
        "Dashboard", "Empresa", "Peligros", "Plan de Acción", "Trabajadores",
        "Incidentes", "Matriz Legal", "Auditorías", "Capacitaciones",
        "Inspecciones", "Emergencias", "Documentos", "Indicadores", "Bitácora", "Chat IA"
    ])
    
    st.markdown("---")
    if st.button("Cerrar Sesión", use_container_width=True):
        st.session_state.auth = False
        st.rerun()

# Obtener datos de la empresa actual
empresa_actual = st.session_state.empresas[st.session_state.current_empresa]

# ========== DASHBOARD MULTIEMPRESA ==========
if menu == "Dashboard":
    st.markdown(f'<div class="main-header"><h1>Dashboard - {empresa_actual["nombre"]}</h1><p>Resumen ejecutivo del SG-SST</p></div>', unsafe_allow_html=True)
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Trabajadores", len(empresa_actual.get("trabajadores", [])))
    with col2:
        st.metric("Peligros", len(empresa_actual.get("peligros", [])))
    with col3:
        st.metric("Incidentes", len(empresa_actual.get("incidentes", [])))
    with col4:
        st.metric("Plan", empresa_actual.get("plan", "basico").upper())
    
    st.markdown("---")
    
    # Alertas del sistema
    st.subheader("⚠️ Alertas del Sistema")
    alerts = [
        {"tipo": "warning", "msg": "Documentos por vencer: Política SST (30 días)"},
        {"tipo": "danger", "msg": "Extintor vencido en Planta Principal"},
    ]
    for a in alerts:
        if a["tipo"] == "warning":
            st.warning(a["msg"])
        else:
            st.error(a["msg"])

# ========== EMPRESA ==========
elif menu == "Empresa":
    st.markdown('<div class="main-header"><h1>Configuración de Empresa</h1></div>', unsafe_allow_html=True)
    
    with st.form("empresa_form"):
        col1, col2 = st.columns(2)
        with col1:
            nombre = st.text_input("Nombre", value=empresa_actual.get("nombre", ""))
            nit = st.text_input("NIT", value=empresa_actual.get("nit", ""))
        with col2:
            plan = st.selectbox("Plan", ["basico", "profesional", "empresarial"], 
                               index=["basico", "profesional", "empresarial"].index(empresa_actual.get("plan", "basico")))
        
        if st.form_submit_button("Guardar"):
            empresa_actual["nombre"] = nombre
            empresa_actual["nit"] = nit
            empresa_actual["plan"] = plan
            st.success("Datos actualizados")

# ========== TRABAJADORES ==========
elif menu == "Trabajadores":
    st.markdown('<div class="main-header"><h1>Trabajadores</h1></div>', unsafe_allow_html=True)
    
    trabajadores = empresa_actual.get("trabajadores", [])
    df = pd.DataFrame(trabajadores)
    st.dataframe(df, use_container_width=True)
    
    with st.form("add_trabajador"):
        nombre = st.text_input("Nombre")
        cedula = st.text_input("Cédula")
        cargo = st.text_input("Cargo")
        if st.form_submit_button("Agregar"):
            nuevo_id = max([t["id"] for t in trabajadores]) + 1 if trabajadores else 1
            trabajadores.append({"id": nuevo_id, "nombre": nombre, "cedula": cedula, "cargo": cargo})
            st.success("Trabajador agregado")
            st.rerun()

# ========== PELIGROS ==========
elif menu == "Peligros":
    st.markdown('<div class="main-header"><h1>Peligros</h1></div>', unsafe_allow_html=True)
    
    peligros = empresa_actual.get("peligros", [])
    df = pd.DataFrame(peligros)
    st.dataframe(df, use_container_width=True)

# ========== INCIDENTES ==========
elif menu == "Incidentes":
    st.markdown('<div class="main-header"><h1>Incidentes</h1></div>', unsafe_allow_html=True)
    
    incidentes = empresa_actual.get("incidentes", [])
    df = pd.DataFrame(incidentes)
    st.dataframe(df, use_container_width=True)

# ========== BITÁCORA ==========
elif menu == "Bitácora":
    st.markdown('<div class="main-header"><h1>Bitácora de Cambios</h1><p>Registro de todas las acciones del sistema</p></div>', unsafe_allow_html=True)
    
    logs = st.session_state.get("logs", [])
    if logs:
        df = pd.DataFrame(logs)
        st.dataframe(df[["fecha", "usuario_nombre", "accion", "modulo", "documento_id"]], use_container_width=True)
    else:
        st.info("No hay registros en la bitácora")

# ========== CHAT IA ==========
elif menu == "Chat IA":
    st.markdown('<div class="main-header"><h1>Chat IA</h1><p>Asistente virtual SST</p></div>', unsafe_allow_html=True)
    
    if "chat_messages" not in st.session_state:
        st.session_state.chat_messages = []
    
    for msg in st.session_state.chat_messages:
        with st.chat_message(msg["role"]):
            st.write(msg["content"])
    
    if prompt := st.chat_input("Pregunta sobre SST..."):
        st.session_state.chat_messages.append({"role": "user", "content": prompt})
        with st.chat_message("assistant"):
            st.write("Soy un asistente SST. Por ahora, consulta la documentación del sistema.")

# ========== OTROS MÓDULOS ==========
else:
    st.markdown(f'<div class="main-header"><h1>{menu}</h1><p>Módulo en desarrollo</p></div>', unsafe_allow_html=True)
    st.info(f"El módulo {menu} está en construcción")

st.markdown("---")
st.markdown("<p style='text-align:center; font-size:11px; color:gray'>SG-SST PHVA | Sistema Multiempresa | Desarrollado por JAN BENITEZ</p>", unsafe_allow_html=True)

