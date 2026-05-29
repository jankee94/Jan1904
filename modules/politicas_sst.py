"""
Módulo de Políticas SST
Autor: Ing. Jan Benitez & Ing. Neiris Pallares
Sistema SG-SST PHVA
"""

import streamlit as st
import pandas as pd
from datetime import datetime, date
import sqlite3
import os

DB_PATH = "sst.db"

def init_politicas_table():
    """Inicializar tabla de políticas SST"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS politicas_sst (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            codigo TEXT UNIQUE NOT NULL,
            titulo TEXT NOT NULL,
            descripcion TEXT NOT NULL,
            fecha_emision DATE NOT NULL,
            fecha_vigencia DATE NOT NULL,
            responsable TEXT NOT NULL,
            area_aplicacion TEXT NOT NULL,
            estado TEXT DEFAULT 'Activa',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    cursor.execute("SELECT COUNT(*) FROM politicas_sst")
    if cursor.fetchone()[0] == 0:
        cursor.execute("""
            INSERT INTO politicas_sst 
            (codigo, titulo, descripcion, fecha_emision, fecha_vigencia, responsable, area_aplicacion, estado)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            "POL-001",
            "Politica de Seguridad y Salud en el Trabajo",
            "La empresa se compromete a garantizar condiciones seguras para todos los trabajadores...",
            date.today().isoformat(),
            date(date.today().year + 1, date.today().month, date.today().day).isoformat(),
            "Gerencia General",
            "Toda la empresa",
            "Activa"
        ))
    
    conn.commit()
    conn.close()

def mostrar_politicas():
    """Mostrar listado de politicas"""
    st.subheader("Politicas SST")
    
    conn = sqlite3.connect(DB_PATH)
    
    col1, col2, col3 = st.columns(3)
    with col1:
        estado_filter = st.selectbox("Filtrar por estado", ["Todas", "Activa", "Inactiva", "En revision"])
    with col2:
        st.write("")
    with col3:
        if st.button("Nueva Politica", use_container_width=True):
            st.session_state.show_politica_form = True
    
    query = "SELECT id, codigo, titulo, fecha_emision, fecha_vigencia, responsable, area_aplicacion, estado FROM politicas_sst"
    df = pd.read_sql_query(query, conn)
    conn.close()
    
    if df.empty:
        st.info("No hay politicas registradas")
        return
    
    st.dataframe(df, use_container_width=True)

def formulario_politica():
    """Formulario para crear politica"""
    st.subheader("Nueva Politica SST")
    
    with st.form("form_politica"):
        codigo = st.text_input("Codigo", placeholder="Ej: POL-001")
        titulo = st.text_input("Titulo", placeholder="Politica de...")
        responsable = st.text_input("Responsable", placeholder="Gerencia General")
        area_aplicacion = st.text_input("Area de Aplicacion", placeholder="Toda la empresa")
        fecha_emision = st.date_input("Fecha de emision", datetime.now())
        fecha_vigencia = st.date_input("Fecha de vigencia", datetime.now().replace(year=datetime.now().year + 1))
        descripcion = st.text_area("Descripcion", height=150)
        estado = st.selectbox("Estado", ["Activa", "Inactiva", "En revision"])
        
        submitted = st.form_submit_button("Guardar Politica")
        
        if submitted:
            if not codigo or not titulo:
                st.error("Complete los campos obligatorios")
                return
            
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            try:
                cursor.execute("""
                    INSERT INTO politicas_sst 
                    (codigo, titulo, descripcion, fecha_emision, fecha_vigencia, 
                     responsable, area_aplicacion, estado)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (codigo, titulo, descripcion, fecha_emision.isoformat(), 
                      fecha_vigencia.isoformat(), responsable, area_aplicacion, estado))
                conn.commit()
                st.success("Politica creada exitosamente")
                st.session_state.show_politica_form = False
                st.rerun()
            except sqlite3.IntegrityError:
                st.error("El codigo ya existe")
            finally:
                conn.close()

def main():
    """Funcion principal"""
    init_politicas_table()
    
    if st.session_state.get('show_politica_form', False):
        formulario_politica()
        if st.button("Volver a lista"):
            st.session_state.show_politica_form = False
            st.rerun()
    else:
        mostrar_politicas()

if __name__ == "__main__":
    main()
