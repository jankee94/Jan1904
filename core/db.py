import sqlite3
import pandas as pd
import os

class Database:
    def __init__(self, db_path):
        self.db_path = db_path
        self._init_tables()
    
    def _init_tables(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS peligros (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                tipo TEXT, descripcion TEXT, ubicacion TEXT,
                probabilidad INTEGER, severidad INTEGER, nivel_riesgo TEXT
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS acciones (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                peligro_id INTEGER, descripcion TEXT,
                responsable TEXT, fecha_limite TEXT, estado TEXT
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS trabajadores (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                cedula TEXT, nombre TEXT, email TEXT, cargo TEXT, area TEXT
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS incidentes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                tipo TEXT, descripcion TEXT, fecha TEXT, lugar TEXT, gravedad TEXT
            )
        ''')
        conn.commit()
        conn.close()
    
    def execute_query(self, query, params=()):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(query, params)
        conn.commit()
        conn.close()
    
    def fetch_all(self, query, params=()):
        conn = sqlite3.connect(self.db_path)
        df = pd.read_sql_query(query, conn, params=params)
        conn.close()
        return df
