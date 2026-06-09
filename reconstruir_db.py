import sqlite3

conn = sqlite3.connect("sst.db")
cursor = conn.cursor()

# Eliminar tablas existentes (para evitar conflictos)
cursor.execute("DROP TABLE IF EXISTS usuarios")
cursor.execute("DROP TABLE IF EXISTS empresa")
cursor.execute("DROP TABLE IF EXISTS peligros")
cursor.execute("DROP TABLE IF EXISTS acciones")
cursor.execute("DROP TABLE IF EXISTS trabajadores")
cursor.execute("DROP TABLE IF EXISTS incidentes")

# Crear tablas con estructura CORRECTA
cursor.execute('''CREATE TABLE usuarios (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE,
    password TEXT,
    nombre TEXT,
    rol TEXT DEFAULT 'trabajador'
)''')

cursor.execute('''CREATE TABLE empresa (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nit TEXT,
    nombre TEXT,
    trabajadores INTEGER,
    arl TEXT,
    diagnostico TEXT,
    fecha TEXT
)''')

cursor.execute('''CREATE TABLE peligros (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    empresa_id INTEGER,
    tipo TEXT,
    descripcion TEXT,
    probabilidad INTEGER,
    severidad INTEGER,
    nivel TEXT
)''')

cursor.execute('''CREATE TABLE acciones (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    empresa_id INTEGER,
    descripcion TEXT,
    responsable TEXT,
    fecha TEXT,
    estado TEXT
)''')

cursor.execute('''CREATE TABLE trabajadores (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    empresa_id INTEGER,
    nombre TEXT,
    cedula TEXT,
    cargo TEXT
)''')

cursor.execute('''CREATE TABLE incidentes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    empresa_id INTEGER,
    descripcion TEXT,
    fecha TEXT,
    gravedad TEXT
)''')

# Insertar usuario admin
cursor.execute("INSERT INTO usuarios (username, password, nombre, rol) VALUES (?,?,?,?)",
              ('admin', 'admin123', 'Administrador', 'admin'))

conn.commit()
conn.close()

print("✅ Base de datos reconstruida correctamente")
print("📌 Tablas creadas: usuarios, empresa, peligros, acciones, trabajadores, incidentes")
