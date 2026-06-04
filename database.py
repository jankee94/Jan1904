import sqlite3
import pandas as pd
import os

class Database:
    def __init__(self, db_path="data/sst.db"):
        os.makedirs("data", exist_ok=True)
        self.db_path = db_path
        self.init_db()
    
    def get_connection(self):
        return sqlite3.connect(self.db_path)
    
    def init_db(self):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS peligros (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                tipo TEXT NOT NULL,
                descripcion TEXT NOT NULL,
                ubicacion TEXT NOT NULL,
                probabilidad INTEGER CHECK(probabilidad BETWEEN 1 AND 4),
                severidad INTEGER CHECK(severidad BETWEEN 1 AND 3),
                nivel_riesgo TEXT,
                controles_sugeridos TEXT,
                fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS acciones (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                peligro_id INTEGER,
                descripcion TEXT NOT NULL,
                responsable TEXT NOT NULL,
                fecha_limite DATE NOT NULL,
                estado TEXT DEFAULT 'Pendiente',
                prioridad TEXT,
                FOREIGN KEY (peligro_id) REFERENCES peligros(id)
            )
        ''')
        conn.commit()
        conn.close()
    
    def crear_peligro(self, tipo, descripcion, ubicacion, probabilidad, severidad):
        nivel = self.calcular_nivel(probabilidad, severidad)
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO peligros (tipo, descripcion, ubicacion, probabilidad, severidad, nivel_riesgo)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (tipo, descripcion, ubicacion, probabilidad, severidad, nivel))
        conn.commit()
        pid = cursor.lastrowid
        conn.close()
        return pid
    
    def obtener_peligros(self):
        conn = self.get_connection()
        df = pd.read_sql_query("SELECT * FROM peligros ORDER BY fecha_creacion DESC", conn)
        conn.close()
        return df
    
    def calcular_nivel(self, prob, sev):
        matriz = {(1,1):"III",(1,2):"II",(1,3):"I",(2,1):"III",(2,2):"II",(2,3):"I",
                  (3,1):"II",(3,2):"I",(3,3):"I",(4,1):"II",(4,2):"I",(4,3):"I"}
        return matriz.get((prob, sev), "III")
    
    def crear_accion(self, peligro_id, descripcion, responsable, fecha_limite, prioridad):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO acciones (peligro_id, descripcion, responsable, fecha_limite, prioridad)
            VALUES (?, ?, ?, ?, ?)
        ''', (peligro_id, descripcion, responsable, fecha_limite, prioridad))
        conn.commit()
        conn.close()
        return True

db = Database()
