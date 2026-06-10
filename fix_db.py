import sqlite3
conn = sqlite3.connect("sst.db")
cursor = conn.cursor()

# Agregar columnas faltantes a peligros
try:
    cursor.execute("ALTER TABLE peligros ADD COLUMN fecha_registro TEXT DEFAULT '2024-01-01'")
    print("✅ Columna fecha_registro agregada a peligros")
except:
    print("⚠️ Columna fecha_registro ya existe en peligros")

# Agregar columnas faltantes a acciones
try:
    cursor.execute("ALTER TABLE acciones ADD COLUMN fecha_registro TEXT DEFAULT '2024-01-01'")
    print("✅ Columna fecha_registro agregada a acciones")
except:
    print("⚠️ Columna fecha_registro ya existe en acciones")

# Agregar columnas faltantes a trabajadores
try:
    cursor.execute("ALTER TABLE trabajadores ADD COLUMN area TEXT DEFAULT 'General'")
    print("✅ Columna area agregada a trabajadores")
except:
    print("⚠️ Columna area ya existe en trabajadores")

try:
    cursor.execute("ALTER TABLE trabajadores ADD COLUMN fecha_registro TEXT DEFAULT '2024-01-01'")
    print("✅ Columna fecha_registro agregada a trabajadores")
except:
    print("⚠️ Columna fecha_registro ya existe en trabajadores")

# Agregar columnas faltantes a incidentes
try:
    cursor.execute("ALTER TABLE incidentes ADD COLUMN causa TEXT DEFAULT 'En investigacion'")
    print("✅ Columna causa agregada a incidentes")
except:
    print("⚠️ Columna causa ya existe en incidentes")

try:
    cursor.execute("ALTER TABLE incidentes ADD COLUMN fecha_registro TEXT DEFAULT '2024-01-01'")
    print("✅ Columna fecha_registro agregada a incidentes")
except:
    print("⚠️ Columna fecha_registro ya existe en incidentes")

# Crear tablas faltantes
cursor.execute('''CREATE TABLE IF NOT EXISTS matriz_legal (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    empresa_id INTEGER DEFAULT 1,
    norma TEXT,
    articulo TEXT,
    requisito TEXT,
    cumple INTEGER DEFAULT 0,
    responsable TEXT
)''')
print("✅ Tabla matriz_legal verificada")

cursor.execute('''CREATE TABLE IF NOT EXISTS auditorias (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    empresa_id INTEGER DEFAULT 1,
    codigo TEXT,
    fecha TEXT,
    auditor_id TEXT,
    puntuacion INTEGER DEFAULT 0,
    estado TEXT DEFAULT 'planificada'
)''')
print("✅ Tabla auditorias verificada")

cursor.execute('''CREATE TABLE IF NOT EXISTS plan_anual (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    empresa_id INTEGER DEFAULT 1,
    anio INTEGER,
    mes INTEGER,
    actividad TEXT,
    responsable TEXT,
    presupuesto REAL DEFAULT 0,
    cumplimiento INTEGER DEFAULT 0
)''')
print("✅ Tabla plan_anual verificada")

conn.commit()
conn.close()
print("\n✅ Base de datos corregida exitosamente!")
