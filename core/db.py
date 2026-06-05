import sqlite3
import pandas as pd

class Database:
    def __init__(self):
        self.conn = sqlite3.connect("sst.db", check_same_thread=False)
        self._init_tables()
    
    def _init_tables(self):
        cursor = self.conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS empresa (
                id INTEGER PRIMARY KEY DEFAULT 1,
                nombre TEXT,
                trabajadores INTEGER,
                arl TEXT,
                diagnostico TEXT
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS peligros (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                tipo TEXT,
                descripcion TEXT,
                probabilidad INTEGER,
                severidad INTEGER,
                nivel TEXT
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS acciones (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                descripcion TEXT,
                responsable TEXT,
                fecha TEXT,
                estado TEXT
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS trabajadores (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nombre TEXT,
                cedula TEXT,
                cargo TEXT
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS incidentes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                descripcion TEXT,
                fecha TEXT,
                gravedad TEXT
            )
        ''')
        
        self.conn.commit()
    
    def guardar_empresa(self, nombre, trabajadores, arl, diagnostico):
        cursor = self.conn.cursor()
        cursor.execute("DELETE FROM empresa")
        cursor.execute("INSERT INTO empresa (nombre, trabajadores, arl, diagnostico) VALUES (?, ?, ?, ?)",
                      (nombre, trabajadores, arl, diagnostico))
        self.conn.commit()
    
    def obtener_empresa(self):
        df = pd.read_sql_query("SELECT * FROM empresa", self.conn)
        return df.iloc[0].to_dict() if not df.empty else None
    
    def guardar_peligro(self, tipo, desc, prob, sev):
        matriz = {(1,1):"III",(1,2):"II",(1,3):"I",(2,1):"III",(2,2):"II",(2,3):"I",
                  (3,1):"II",(3,2):"I",(3,3):"I",(4,1):"II",(4,2):"I",(4,3):"I"}
        nivel = matriz.get((prob, sev), "III")
        cursor = self.conn.cursor()
        cursor.execute("INSERT INTO peligros (tipo, descripcion, probabilidad, severidad, nivel) VALUES (?, ?, ?, ?, ?)",
                      (tipo, desc, prob, sev, nivel))
        self.conn.commit()
    
    def obtener_peligros(self):
        return pd.read_sql_query("SELECT * FROM peligros", self.conn)
    
    def eliminar_peligro(self, id):
        cursor = self.conn.cursor()
        cursor.execute("DELETE FROM peligros WHERE id = ?", (id,))
        self.conn.commit()
    
    def guardar_accion(self, desc, responsable, fecha):
        cursor = self.conn.cursor()
        cursor.execute("INSERT INTO acciones (descripcion, responsable, fecha, estado) VALUES (?, ?, ?, 'Pendiente')",
                      (desc, responsable, fecha))
        self.conn.commit()
    
    def obtener_acciones(self):
        return pd.read_sql_query("SELECT * FROM acciones", self.conn)
    
    def actualizar_estado(self, id, estado):
        cursor = self.conn.cursor()
        cursor.execute("UPDATE acciones SET estado = ? WHERE id = ?", (estado, id))
        self.conn.commit()
    
    def guardar_trabajador(self, nombre, cedula, cargo):
        cursor = self.conn.cursor()
        cursor.execute("INSERT INTO trabajadores (nombre, cedula, cargo) VALUES (?, ?, ?)", (nombre, cedula, cargo))
        self.conn.commit()
    
    def obtener_trabajadores(self):
        return pd.read_sql_query("SELECT * FROM trabajadores", self.conn)
    
    def guardar_incidente(self, desc, fecha, gravedad):
        cursor = self.conn.cursor()
        cursor.execute("INSERT INTO incidentes (descripcion, fecha, gravedad) VALUES (?, ?, ?)", (desc, fecha, gravedad))
        self.conn.commit()
    
    def obtener_incidentes(self):
        return pd.read_sql_query("SELECT * FROM incidentes", self.conn)

db = Database()