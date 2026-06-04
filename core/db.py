import sqlite3
import pandas as pd
import os

class Database:
    def __init__(self, db_path="sst.db"):
        self.db_path = db_path
        self._init_tables()
    
    def _init_tables(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # TABLA EMPRESA (para diagnóstico)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS empresa (
                id INTEGER PRIMARY KEY,
                nit TEXT UNIQUE,
                nombre TEXT,
                trabajadores INTEGER,
                arl TEXT,
                actividad TEXT,
                diagnostico_ia TEXT,
                fecha_diagnostico TEXT
            )
        ''')
        
        # TABLA PELIGROS
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS peligros (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                empresa_id INTEGER,
                tipo TEXT,
                descripcion TEXT,
                ubicacion TEXT,
                probabilidad INTEGER,
                severidad INTEGER,
                nivel_riesgo TEXT,
                sugerido_ia INTEGER DEFAULT 0,
                FOREIGN KEY (empresa_id) REFERENCES empresa(id)
            )
        ''')
        
        # TABLA ACCIONES
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS acciones (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                empresa_id INTEGER,
                peligro_id INTEGER,
                descripcion TEXT,
                responsable TEXT,
                fecha_limite TEXT,
                estado TEXT DEFAULT 'Pendiente',
                prioridad TEXT,
                sugerido_ia INTEGER DEFAULT 0,
                FOREIGN KEY (empresa_id) REFERENCES empresa(id)
            )
        ''')
        
        # TABLA INCIDENTES
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS incidentes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                empresa_id INTEGER,
                tipo TEXT,
                descripcion TEXT,
                fecha TEXT,
                lugar TEXT,
                gravedad TEXT,
                FOREIGN KEY (empresa_id) REFERENCES empresa(id)
            )
        ''')
        
        # TABLA TRABAJADORES
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS trabajadores (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                empresa_id INTEGER,
                cedula TEXT,
                nombre TEXT,
                email TEXT,
                cargo TEXT,
                area TEXT,
                FOREIGN KEY (empresa_id) REFERENCES empresa(id)
            )
        ''')
        
        conn.commit()
        conn.close()
    
    # ========== EMPRESA ==========
    def guardar_empresa(self, nit, nombre, trabajadores, arl, actividad, diagnostico_ia):
        import datetime
        fecha = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT OR REPLACE INTO empresa (id, nit, nombre, trabajadores, arl, actividad, diagnostico_ia, fecha_diagnostico)
            VALUES (1, ?, ?, ?, ?, ?, ?, ?)
        ''', (nit, nombre, trabajadores, arl, actividad, diagnostico_ia, fecha))
        conn.commit()
        conn.close()
    
    def obtener_empresa(self):
        conn = sqlite3.connect(self.db_path)
        df = pd.read_sql_query("SELECT * FROM empresa WHERE id = 1", conn)
        conn.close()
        return df.iloc[0] if not df.empty else None
    
    # ========== PELIGROS ==========
    def guardar_peligro(self, empresa_id, tipo, descripcion, ubicacion, prob, sev, sugerido_ia=0):
        nivel = self.calcular_nivel(prob, sev)
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO peligros (empresa_id, tipo, descripcion, ubicacion, probabilidad, severidad, nivel_riesgo, sugerido_ia)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (empresa_id, tipo, descripcion, ubicacion, prob, sev, nivel, sugerido_ia))
        conn.commit()
        conn.close()
    
    def obtener_peligros(self, empresa_id=1):
        conn = sqlite3.connect(self.db_path)
        df = pd.read_sql_query("SELECT * FROM peligros WHERE empresa_id = ?", conn, params=(empresa_id,))
        conn.close()
        return df
    
    def eliminar_peligro(self, id):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM peligros WHERE id = ?", (id,))
        conn.commit()
        conn.close()
    
    # ========== ACCIONES ==========
    def guardar_accion(self, empresa_id, peligro_id, descripcion, responsable, fecha_limite, prioridad, sugerido_ia=0):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO acciones (empresa_id, peligro_id, descripcion, responsable, fecha_limite, prioridad, sugerido_ia)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (empresa_id, peligro_id, descripcion, responsable, fecha_limite, prioridad, sugerido_ia))
        conn.commit()
        conn.close()
    
    def obtener_acciones(self, empresa_id=1):
        conn = sqlite3.connect(self.db_path)
        df = pd.read_sql_query("SELECT * FROM acciones WHERE empresa_id = ?", conn, params=(empresa_id,))
        conn.close()
        return df
    
    def actualizar_estado_accion(self, id, estado):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("UPDATE acciones SET estado = ? WHERE id = ?", (estado, id))
        conn.commit()
        conn.close()
    
    # ========== TRABAJADORES ==========
    def guardar_trabajador(self, empresa_id, cedula, nombre, email, cargo, area):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO trabajadores (empresa_id, cedula, nombre, email, cargo, area)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (empresa_id, cedula, nombre, email, cargo, area))
        conn.commit()
        conn.close()
    
    def obtener_trabajadores(self, empresa_id=1):
        conn = sqlite3.connect(self.db_path)
        df = pd.read_sql_query("SELECT * FROM trabajadores WHERE empresa_id = ?", conn, params=(empresa_id,))
        conn.close()
        return df
    
    # ========== INCIDENTES ==========
    def guardar_incidente(self, empresa_id, tipo, descripcion, fecha, lugar, gravedad):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO incidentes (empresa_id, tipo, descripcion, fecha, lugar, gravedad)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (empresa_id, tipo, descripcion, fecha, lugar, gravedad))
        conn.commit()
        conn.close()
    
    def obtener_incidentes(self, empresa_id=1):
        conn = sqlite3.connect(self.db_path)
        df = pd.read_sql_query("SELECT * FROM incidentes WHERE empresa_id = ?", conn, params=(empresa_id,))
        conn.close()
        return df
    
    def calcular_nivel(self, prob, sev):
        matriz = {(1,1):"III",(1,2):"II",(1,3):"I",(2,1):"III",(2,2):"II",(2,3):"I",
                  (3,1):"II",(3,2):"I",(3,3):"I",(4,1):"II",(4,2):"I",(4,3):"I"}
        return matriz.get((prob, sev), "III")
    
    # ========== ESTADÍSTICAS ==========
    def obtener_stats(self, empresa_id=1):
        peligros = self.obtener_peligros(empresa_id)
        acciones = self.obtener_acciones(empresa_id)
        return {
            'total_peligros': len(peligros),
            'total_acciones': len(acciones),
            'acciones_completadas': len(acciones[acciones['estado'] == 'Completada']) if not acciones.empty else 0,
            'riesgos_nivel1': len(peligros[peligros['nivel_riesgo'] == 'I']) if not peligros.empty else 0
        }

db = Database()
