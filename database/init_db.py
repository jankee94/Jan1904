import sqlite3

def init_database():
    conn = sqlite3.connect('sst.db')
    cursor = conn.cursor()
    
    # Usuarios
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            rol TEXT DEFAULT 'usuario',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Trabajadores
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS trabajadores (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            cedula TEXT UNIQUE NOT NULL,
            cargo TEXT,
            area TEXT,
            fecha_ingreso DATE,
            eps TEXT,
            arl TEXT,
            estado TEXT DEFAULT 'Activo'
        )
    ''')
    
    # Peligros
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS peligros (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            proceso TEXT,
            peligro TEXT,
            efecto TEXT,
            probabilidad TEXT,
            severidad TEXT,
            nivel_riesgo TEXT,
            control TEXT,
            fecha_registro DATE
        )
    ''')
    
    # Capacitaciones
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS capacitaciones (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            tema TEXT NOT NULL,
            fecha DATE,
            duracion INTEGER,
            asistentes INTEGER DEFAULT 0,
            estado TEXT DEFAULT 'Programada'
        )
    ''')
    
    # Incidentes
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS incidentes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            tipo TEXT,
            fecha DATE,
            lugar TEXT,
            descripcion TEXT,
            afectado TEXT,
            gravedad TEXT,
            acciones TEXT
        )
    ''')
    
    # Plan Anual
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS plan_anual (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            actividad TEXT,
            mes INTEGER,
            responsable TEXT,
            recursos TEXT,
            estado TEXT DEFAULT 'Pendiente'
        )
    ''')
    
    # Auditorías
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS auditorias (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            fecha DATE,
            tipo TEXT,
            hallazgos TEXT,
            acciones TEXT,
            cumplimiento REAL
        )
    ''')
    
    # Políticas
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS politicas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            titulo TEXT,
            contenido TEXT,
            fecha_aprobacion DATE,
            version TEXT,
            estado TEXT DEFAULT 'Activa'
        )
    ''')
    
    # Matriz Legal
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS matriz_legal (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            norma TEXT,
            articulo TEXT,
            requisito TEXT,
            cumplimiento TEXT,
            responsable TEXT
        )
    ''')
    
    # Plan de Emergencias
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS plan_emergencias (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            tipo_emergencia TEXT,
            procedimiento TEXT,
            responsable TEXT,
            recursos TEXT,
            simulacro DATE
        )
    ''')
    
    conn.commit()
    conn.close()
    print("✅ Base de datos inicializada")

if __name__ == "__main__":
    init_database()
