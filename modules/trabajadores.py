import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime

def show():
    st.markdown("## 👥 Gestión de Trabajadores")
    st.markdown("---")
    
    conn = sqlite3.connect('sst.db', check_same_thread=False)
    cursor = conn.cursor()
    
    # Crear tabla si no existe
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS trabajadores (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            cedula TEXT UNIQUE NOT NULL,
            cargo TEXT,
            area TEXT,
            fecha_ingreso DATE,
            eps TEXT,
            arl TEXT,
            estado TEXT DEFAULT 'Activo'
        )
    ''')
    conn.commit()
    
    tab1, tab2, tab3 = st.tabs(["📋 Lista", "➕ Agregar", "✏️ Editar"])
    
    with tab1:
        df = pd.read_sql_query("SELECT id, nombre, cedula, cargo, area, estado FROM trabajadores ORDER BY nombre", conn)
        if not df.empty:
            st.dataframe(df, use_container_width=True)
            st.metric("Total trabajadores", len(df))
        else:
            st.info("No hay trabajadores registrados")
    
    with tab2:
        with st.form("agregar_trabajador"):
            col1, col2 = st.columns(2)
            with col1:
                nombre = st.text_input("Nombre completo*")
                cedula = st.text_input("Cédula*")
                cargo = st.text_input("Cargo")
            with col2:
                area = st.text_input("Área")
                eps = st.text_input("EPS")
                arl = st.text_input("ARL")
            fecha_ingreso = st.date_input("Fecha de ingreso", datetime.now())
            
            submitted = st.form_submit_button("Guardar", use_container_width=True)
            if submitted:
                if not nombre or not cedula:
                    st.error("Nombre y cédula son obligatorios")
                else:
                    try:
                        cursor.execute('''
                            INSERT INTO trabajadores (nombre, cedula, cargo, area, fecha_ingreso, eps, arl)
                            VALUES (?,?,?,?,?,?,?)
                        ''', (nombre, cedula, cargo, area, fecha_ingreso, eps, arl))
                        conn.commit()
                        st.success("✅ Trabajador agregado")
                        st.rerun()
                    except sqlite3.IntegrityError:
                        st.error("❌ Ya existe un trabajador con esa cédula")
    
    with tab3:
        trabajadores = pd.read_sql_query("SELECT id, nombre, cedula, estado FROM trabajadores", conn)
        if not trabajadores.empty:
            seleccion = st.selectbox("Seleccionar trabajador", trabajadores.to_dict('records'), 
                                     format_func=lambda x: f"{x['nombre']} - {x['cedula']}")
            if seleccion:
                nuevo_estado = st.selectbox("Estado", ["Activo", "Inactivo", "Vacaciones", "Retirado"])
                if st.button("Actualizar estado", use_container_width=True):
                    cursor.execute("UPDATE trabajadores SET estado = ? WHERE id = ?", (nuevo_estado, seleccion['id']))
                    conn.commit()
                    st.success("✅ Estado actualizado")
                    st.rerun()
                
                if st.button("🗑️ Eliminar trabajador", type="secondary", use_container_width=True):
                    cursor.execute("DELETE FROM trabajadores WHERE id = ?", (seleccion['id'],))
                    conn.commit()
                    st.success("✅ Trabajador eliminado")
                    st.rerun()
        else:
            st.info("No hay trabajadores")
    
    conn.close()
