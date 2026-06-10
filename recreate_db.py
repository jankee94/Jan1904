import sqlite3
import pandas as pd
from datetime import datetime

conn = sqlite3.connect("sst.db")
cursor = conn.cursor()

# 1. TABLA USUARIOS
cursor.execute('''
CREATE TABLE IF NOT EXISTS usuarios (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE,
    password TEXT,
    nombre TEXT,
    rol TEXT DEFAULT 'trabajador'
)
''')

# 2. TABLA EMPRESA_CONFIG
cursor.execute('''
CREATE TABLE IF NOT EXISTS empresa_config (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre TEXT,
    nit TEXT,
    ubicacion TEXT,
    ciudad TEXT,
    sector TEXT,
    telefono TEXT,
    email TEXT
)
''')

# 3. TABLA PELIGROS (con todas las columnas)
cursor.execute('''
CREATE TABLE IF NOT EXISTS peligros (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    empresa_id INTEGER DEFAULT 1,
    tipo TEXT,
    descripcion TEXT,
    probabilidad INTEGER,
    severidad INTEGER,
    nivel TEXT,
    fecha_registro TEXT
)
''')

# 4. TABLA ACCIONES
cursor.execute('''
CREATE TABLE IF NOT EXISTS acciones (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    empresa_id INTEGER DEFAULT 1,
    descripcion TEXT,
    responsable TEXT,
    fecha_limite TEXT,
    estado TEXT,
    fecha_registro TEXT
)
''')

# 5. TABLA TRABAJADORES
cursor.execute('''
CREATE TABLE IF NOT EXISTS trabajadores (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    empresa_id INTEGER DEFAULT 1,
    nombre TEXT,
    cedula TEXT,
    cargo TEXT,
    area TEXT,
    fecha_registro TEXT
)
''')

# 6. TABLA INCIDENTES
cursor.execute('''
CREATE TABLE IF NOT EXISTS incidentes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    empresa_id INTEGER DEFAULT 1,
    descripcion TEXT,
    fecha TEXT,
    gravedad TEXT,
    causa TEXT,
    fecha_registro TEXT
)
''')

# 7. TABLA MATRIZ_LEGAL
cursor.execute('''
CREATE TABLE IF NOT EXISTS matriz_legal (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    empresa_id INTEGER DEFAULT 1,
    norma TEXT,
    articulo TEXT,
    requisito TEXT,
    cumple INTEGER DEFAULT 0,
    responsable TEXT
)
''')

# 8. TABLA AUDITORIAS
cursor.execute('''
CREATE TABLE IF NOT EXISTS auditorias (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    empresa_id INTEGER DEFAULT 1,
    codigo TEXT,
    fecha TEXT,
    auditor_id TEXT,
    puntuacion INTEGER DEFAULT 0,
    estado TEXT DEFAULT 'planificada'
)
''')

# 9. TABLA PLAN_ANUAL
cursor.execute('''
CREATE TABLE IF NOT EXISTS plan_anual (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    empresa_id INTEGER DEFAULT 1,
    anio INTEGER,
    mes INTEGER,
    actividad TEXT,
    responsable TEXT,
    presupuesto REAL DEFAULT 0,
    cumplimiento INTEGER DEFAULT 0
)
''')

# Insertar usuario admin
cursor.execute("DELETE FROM usuarios WHERE username='admin'")
cursor.execute("INSERT INTO usuarios (username, password, nombre, rol) VALUES (?,?,?,?)",
              ('admin', 'admin123', 'Administrador', 'admin'))

# Insertar datos de empresa por defecto
cursor.execute("DELETE FROM empresa_config")
cursor.execute("INSERT INTO empresa_config (nombre, nit, ubicacion, ciudad, sector, telefono, email) VALUES (?,?,?,?,?,?,?)",
              ('Constructora Segura SAS', '901.234.567-8', 'Calle 80 #45-67', 'Bogota', 'Construccion', '6015551234', 'sst@constructora.com'))

# Insertar datos de prueba
fecha = datetime.now().strftime("%Y-%m-%d")

# Peligros de prueba
peligros_data = [
    ("Fisico", "Ruido excesivo en zona de maquinaria", 4, 3, "I", fecha),
    ("Ergonomico", "Posturas forzadas en oficinas", 3, 2, "II", fecha),
    ("Quimico", "Exposicion a solventes", 2, 3, "I", fecha),
]
for p in peligros_data:
    cursor.execute("INSERT INTO peligros (tipo, descripcion, probabilidad, severidad, nivel, fecha_registro) VALUES (?,?,?,?,?,?)", p)

# Acciones de prueba
acciones_data = [
    ("Implementar barreras acusticas", "Coordinador SST", "2025-01-15", "En progreso", fecha),
    ("Capacitacion en pausas activas", "SST", "2024-12-10", "Pendiente", fecha),
]
for a in acciones_data:
    cursor.execute("INSERT INTO acciones (descripcion, responsable, fecha_limite, estado, fecha_registro) VALUES (?,?,?,?,?)", a)

# Trabajadores de prueba
trabajadores_data = [
    ("Carlos Lopez", "12345678", "Operario", "Produccion", fecha),
    ("Maria Gomez", "87654321", "Supervisor", "Produccion", fecha),
]
for t in trabajadores_data:
    cursor.execute("INSERT INTO trabajadores (nombre, cedula, cargo, area, fecha_registro) VALUES (?,?,?,?,?)", t)

# Incidentes de prueba
incidentes_data = [
    ("Caida desde andamio", "2024-10-15", "Grave", "Falta de barandas", fecha),
    ("Corte con herramienta", "2024-10-20", "Leve", "Falta de entrenamiento", fecha),
]
for i in incidentes_data:
    cursor.execute("INSERT INTO incidentes (descripcion, fecha, gravedad, causa, fecha_registro) VALUES (?,?,?,?,?)", i)

conn.commit()
conn.close()

print("✅ Base de datos recreada exitosamente!")
print("✅ Usuario: admin / admin123")
print("✅ Datos de prueba cargados")
