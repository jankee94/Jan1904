import sqlite3
import streamlit as st

def get_connection():
    conn = sqlite3.connect('sst.db')
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_connection()
    cursor = conn.cursor()
    
    # Tabla trabajadores
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS trabajadores (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            cedula TEXT UNIQUE NOT NULL,
            cargo TEXT,
            area TEXT,
            fecha_ingreso DATE
        )
    ''')
    
    conn.commit()
    conn.close()
