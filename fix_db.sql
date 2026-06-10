-- Agregar columna fecha_registro a peligros si no existe
ALTER TABLE peligros ADD COLUMN fecha_registro TEXT DEFAULT '2024-01-01';

-- Agregar columna fecha_registro a acciones si no existe
ALTER TABLE acciones ADD COLUMN fecha_registro TEXT DEFAULT '2024-01-01';

-- Agregar columna area a trabajadores si no existe
ALTER TABLE trabajadores ADD COLUMN area TEXT DEFAULT 'General';

-- Agregar columna fecha_registro a trabajadores si no existe
ALTER TABLE trabajadores ADD COLUMN fecha_registro TEXT DEFAULT '2024-01-01';

-- Agregar columna causa a incidentes si no existe
ALTER TABLE incidentes ADD COLUMN causa TEXT DEFAULT 'En investigacion';

-- Agregar columna fecha_registro a incidentes si no existe
ALTER TABLE incidentes ADD COLUMN fecha_registro TEXT DEFAULT '2024-01-01';

-- Crear tabla matriz_legal si no existe
CREATE TABLE IF NOT EXISTS matriz_legal (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    empresa_id INTEGER DEFAULT 1,
    norma TEXT,
    articulo TEXT,
    requisito TEXT,
    cumple INTEGER DEFAULT 0,
    responsable TEXT
);

-- Crear tabla auditorias si no existe
CREATE TABLE IF NOT EXISTS auditorias (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    empresa_id INTEGER DEFAULT 1,
    codigo TEXT,
    fecha TEXT,
    auditor_id TEXT,
    puntuacion INTEGER DEFAULT 0,
    estado TEXT DEFAULT 'planificada'
);

-- Crear tabla plan_anual si no existe
CREATE TABLE IF NOT EXISTS plan_anual (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    empresa_id INTEGER DEFAULT 1,
    anio INTEGER,
    mes INTEGER,
    actividad TEXT,
    responsable TEXT,
    presupuesto REAL DEFAULT 0,
    cumplimiento INTEGER DEFAULT 0
);
