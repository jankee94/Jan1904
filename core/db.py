import sqlite3
import pandas as pd

class Database:
    def __init__(self, db_path="sst.db"):
        self.db_path = db_path
        self.init()
    
    def get_connection(self):
        return sqlite3.connect(self.db_path)
    
    def init(self):
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS trabajadores (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                cedula TEXT,
                nombre TEXT,
                email TEXT,
                cargo TEXT,
                area TEXT
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS peligros (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                tipo TEXT,
                descripcion TEXT,
                ubicacion TEXT,
                probabilidad INTEGER,
                severidad INTEGER,
                nivel_riesgo TEXT
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS incidentes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                tipo TEXT,
                descripcion TEXT,
                fecha TEXT,
                lugar TEXT,
                gravedad TEXT
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS acciones (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                peligro_id INTEGER,
                descripcion TEXT,
                responsable TEXT,
                fecha_limite TEXT,
                estado TEXT,
                prioridad TEXT
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def execute_query(self, query, params=()):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute(query, params)
        conn.commit()
        conn.close()
    
    def fetch_all(self, query, params=()):
        conn = self.get_connection()
        df = pd.read_sql_query(query, conn, params=params)
        conn.close()
        return df
