import streamlit as st
import sqlite3
import pandas as pd

def render():
    st.title("📊 DASHBOARD SST")
    
    conn = sqlite3.connect("sst.db", check_same_thread=False)
    empresa_id = st.session_state.get("empresa_actual_id", 1)
    
    # Verificar si existe empresa_id en las tablas
    try:
        df_peligros = pd.read_sql_query("SELECT * FROM peligros", conn)
        df_acciones = pd.read_sql_query("SELECT * FROM acciones", conn)
        df_trabajadores = pd.read_sql_query("SELECT * FROM trabajadores", conn)
        df_incidentes = pd.read_sql_query("SELECT * FROM incidentes", conn)
    except:
        df_peligros = pd.DataFrame()
        df_acciones = pd.DataFrame()
        df_trabajadores = pd.DataFrame()
        df_incidentes = pd.DataFrame()
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("⚠️ Peligros", len(df_peligros))
    with col2:
        completadas = len(df_acciones[df_acciones['estado'] == 'Completada']) if not df_acciones.empty else 0
        st.metric("✅ Acciones", f"{completadas}/{len(df_acciones)}")
    with col3:
        st.metric("👥 Trabajadores", len(df_trabajadores))
    with col4:
        st.metric("📝 Incidentes", len(df_incidentes))
    
    st.markdown("---")
    st.subheader("📋 Últimas acciones")
    if not df_acciones.empty:
        st.dataframe(df_acciones.head(5), use_container_width=True)
    else:
        st.info("No hay acciones registradas")
    
    conn.close()
