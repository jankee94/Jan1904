import sqlite3
import pandas as pd
import os

class Database:
    def __init__(self, db_path="sst.db"):
        self.db_path = db_path
        self._init_tables()
    
    def get_connection(self):
        return sqlite3.connect(self.db_path)
    
    def _init_tables(self):
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS empresa (
                id INTEGER PRIMARY KEY DEFAULT 1,
                nit TEXT,
                nombre TEXT,
                trabajadores INTEGER,
                arl TEXT,
                actividad TEXT,
                diagnostico_ia TEXT,
                fecha_diagnostico TEXT
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS peligros (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                tipo TEXT,
                descripcion TEXT,
                ubicacion TEXT,
                probabilidad INTEGER,
                severidad INTEGER,
                nivel_riesgo TEXT,
                sugerido_ia INTEGER DEFAULT 0
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS acciones (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                peligro_id INTEGER,
                descripcion TEXT,
                responsable TEXT,
                fecha_limite TEXT,
                estado TEXT DEFAULT 'Pendiente',
                prioridad TEXT,
                sugerido_ia INTEGER DEFAULT 0
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS trabajadores (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                cedula TEXT,
                nombre TEXT,
                email TEXT,
                cargo TEXT,
                area TEXT
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS incidentes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                tipo TEXT,
                descripcion TEXT,
                fecha TEXT,
                lugar TEXT,
                gravedad TEXT
            )
        """)
        
        conn.commit()
        conn.close()
    
    def guardar_empresa(self, nit, nombre, trabajadores, arl, actividad, diagnostico_ia):
        import datetime
        fecha = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM empresa WHERE id = 1")
        existe = cursor.fetchone()
        if existe:
            cursor.execute("UPDATE empresa SET nit=?, nombre=?, trabajadores=?, arl=?, actividad=?, diagnostico_ia=?, fecha_diagnostico=? WHERE id=1",
                          (nit, nombre, trabajadores, arl, actividad, diagnostico_ia, fecha))
        else:
            cursor.execute("INSERT INTO empresa (id, nit, nombre, trabajadores, arl, actividad, diagnostico_ia, fecha_diagnostico) VALUES (1, ?, ?, ?, ?, ?, ?, ?)",
                          (nit, nombre, trabajadores, arl, actividad, diagnostico_ia, fecha))
        conn.commit()
        conn.close()
    
    def obtener_empresa(self):
        conn = self.get_connection()
        try:
            df = pd.read_sql_query("SELECT * FROM empresa WHERE id = 1", conn)
            conn.close()
            if df.empty:
                return None
            return df.iloc[0].to_dict()
        except:
            conn.close()
            return None
    
    def guardar_peligro(self, tipo, descripcion, ubicacion, probabilidad, severidad, sugerido_ia=0):
        matriz = {(1,1):"III",(1,2):"II",(1,3):"I",(2,1):"III",(2,2):"II",(2,3):"I",
                  (3,1):"II",(3,2):"I",(3,3):"I",(4,1):"II",(4,2):"I",(4,3):"I"}
        nivel = matriz.get((probabilidad, severidad), "III")
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO peligros (tipo, descripcion, ubicacion, probabilidad, severidad, nivel_riesgo, sugerido_ia) VALUES (?, ?, ?, ?, ?, ?, ?)",
                      (tipo, descripcion, ubicacion, probabilidad, severidad, nivel, sugerido_ia))
        conn.commit()
        conn.close()
    
    def obtener_peligros(self):
        conn = self.get_connection()
        df = pd.read_sql_query("SELECT * FROM peligros ORDER BY id DESC", conn)
        conn.close()
        return df
    
    def eliminar_peligro(self, id):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM peligros WHERE id = ?", (id,))
        conn.commit()
        conn.close()
    
    def guardar_accion(self, peligro_id, descripcion, responsable, fecha_limite, prioridad, sugerido_ia=0):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO acciones (peligro_id, descripcion, responsable, fecha_limite, prioridad, sugerido_ia) VALUES (?, ?, ?, ?, ?, ?)",
                      (peligro_id, descripcion, responsable, fecha_limite, prioridad, sugerido_ia))
        conn.commit()
        conn.close()
    
    def obtener_acciones(self):
        conn = self.get_connection()
        df = pd.read_sql_query("SELECT * FROM acciones ORDER BY id DESC", conn)
        conn.close()
        return df
    
    def actualizar_estado_accion(self, id, estado):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("UPDATE acciones SET estado = ? WHERE id = ?", (estado, id))
        conn.commit()
        conn.close()
    
    def guardar_trabajador(self, cedula, nombre, email, cargo, area):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO trabajadores (cedula, nombre, email, cargo, area) VALUES (?, ?, ?, ?, ?)",
                      (cedula, nombre, email, cargo, area))
        conn.commit()
        conn.close()
    
    def obtener_trabajadores(self):
        conn = self.get_connection()
        df = pd.read_sql_query("SELECT * FROM trabajadores ORDER BY id DESC", conn)
        conn.close()
        return df
    
    def guardar_incidente(self, tipo, descripcion, fecha, lugar, gravedad):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO incidentes (tipo, descripcion, fecha, lugar, gravedad) VALUES (?, ?, ?, ?, ?)",
                      (tipo, descripcion, fecha, lugar, gravedad))
        conn.commit()
        conn.close()
    
    def obtener_incidentes(self):
        conn = self.get_connection()
        df = pd.read_sql_query("SELECT * FROM incidentes ORDER BY id DESC", conn)
        conn.close()
        return df
    
    def calcular_nivel(self, prob, sev):
        matriz = {(1,1):"III",(1,2):"II",(1,3):"I",(2,1):"III",(2,2):"II",(2,3):"I",
                  (3,1):"II",(3,2):"I",(3,3):"I",(4,1):"II",(4,2):"I",(4,3):"I"}
        return matriz.get((prob, sev), "III")

db = Database()
