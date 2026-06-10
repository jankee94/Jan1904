# core/data/checklists_predefinidos.py
# Checklists predefinidos según normativa ISO 45001 y Decreto 1072

CHECKLISTS_PREDEFINIDOS = {
    "locativa": {
        "nombre": "Inspección Locativa",
        "items": [
            {"item": "Pisos y superficies", "descripcion": "Pisos en buen estado, sin grietas, desniveles o superficies resbalosas", "peso": 5},
            {"item": "Techos y cubiertas", "descripcion": "Techos sin filtraciones, grietas o riesgo de desplome", "peso": 5},
            {"item": "Paredes y divisiones", "descripcion": "Paredes estables, sin humedad o desprendimientos", "peso": 3},
            {"item": "Puertas y ventanas", "descripcion": "Puertas operativas, ventanas seguras sin roturas", "peso": 2},
            {"item": "Escaleras", "descripcion": "Escaleras con barandas, pasamanos y superficies antideslizantes", "peso": 5},
            {"item": "Rampas", "descripcion": "Rampas con pendiente adecuada, superficie antideslizante", "peso": 3},
            {"item": "Señalización", "descripcion": "Señales de seguridad visibles y en buen estado", "peso": 4},
            {"item": "Iluminación", "descripcion": "Niveles de iluminación adecuados para cada área", "peso": 3},
            {"item": "Ventilación", "descripcion": "Sistemas de ventilación funcionando correctamente", "peso": 4},
            {"item": "Temperatura", "descripcion": "Temperatura ambiente dentro de rangos permitidos", "peso": 2},
            {"item": "Orden y limpieza", "descripcion": "Áreas ordenadas, libres de obstáculos y limpias", "peso": 4},
            {"item": "Almacenamiento", "descripcion": "Materiales almacenados de forma segura y ordenada", "peso": 4},
            {"item": "Vías de evacuación", "descripcion": "Vías despejadas, señalizadas y libres de obstáculos", "peso": 5},
            {"item": "Salidas de emergencia", "descripcion": "Salidas identificadas, desbloqueadas y operativas", "peso": 5},
            {"item": "Sistemas contra incendios", "descripcion": "Extintores cargados, visibles y vigentes", "peso": 5},
            {"item": "Botiquines", "descripcion": "Botiquines completos, accesibles y vigentes", "peso": 4},
            {"item": "Puntos de encuentro", "descripcion": "Puntos de encuentro señalizados y accesibles", "peso": 3},
            {"item": "Baños y vestieres", "descripcion": "Baños limpios, dotados y en funcionamiento", "peso": 2},
            {"item": "Cocinas y comedores", "descripcion": "Áreas limpias, equipos funcionando", "peso": 2},
            {"item": "Zonas de descanso", "descripcion": "Áreas de descanso adecuadas y limpias", "peso": 2}
        ]
    },
    "equipos": {
        "nombre": "Inspección de Equipos",
        "items": [
            {"item": "Estado general", "descripcion": "Equipo en buen estado estético y estructural", "peso": 4},
            {"item": "Guardas de seguridad", "descripcion": "Guardas instaladas y en buen estado", "peso": 5},
            {"item": "Sistema eléctrico", "descripcion": "Cables, enchufes y conexiones en buen estado", "peso": 5},
            {"item": "Botón de paro de emergencia", "descripcion": "Botón visible y funcionando", "peso": 5},
            {"item": "Señalización", "descripcion": "Señales de riesgo y operación visibles", "peso": 3},
            {"item": "Manuales disponibles", "descripcion": "Manuales de operación y mantenimiento disponibles", "peso": 2},
            {"item": "Certificados vigentes", "descripcion": "Certificados de mantenimiento y calibración vigentes", "peso": 4},
            {"item": "Registro de mantenimiento", "descripcion": "Bitácora de mantenimiento actualizada", "peso": 3},
            {"item": "Ruido", "descripcion": "Niveles de ruido dentro de lo permitido", "peso": 3},
            {"item": "Vibraciones", "descripcion": "Niveles de vibración aceptables", "peso": 2}
        ]
    },
    "epp": {
        "nombre": "Inspección de Elementos de Protección Personal",
        "items": [
            {"item": "Casco de seguridad", "descripcion": "Casco en buen estado, sin grietas, fecha vigente", "peso": 5},
            {"item": "Gafas de seguridad", "descripcion": "Gafas sin rayones, limpias, bien ajustadas", "peso": 4},
            {"item": "Protectores auditivos", "descripcion": "Tapones u orejeras en buen estado", "peso": 4},
            {"item": "Guantes", "descripcion": "Guantes sin perforaciones, según riesgo", "peso": 5},
            {"item": "Botas de seguridad", "descripcion": "Botas con punta de acero, suela antideslizante", "peso": 5},
            {"item": "Arnés de seguridad", "descripcion": "Arnés sin desgaste, argollas sin deformación", "peso": 5},
            {"item": "Línea de vida", "descripcion": "Línea de vida en buen estado, anclajes seguros", "peso": 5},
            {"item": "Chaleco reflectivo", "descripcion": "Chaleco limpio, reflectivo visible", "peso": 3},
            {"item": "Mascarilla/respirador", "descripcion": "Mascarilla sellada, filtros vigentes", "peso": 5},
            {"item": "Uniforme de trabajo", "descripcion": "Uniforme en buen estado, adecuado al riesgo", "peso": 3}
        ]
    },
    "vehicular": {
        "nombre": "Inspección Vehicular",
        "items": [
            {"item": "Luces", "descripcion": "Luces delanteras, traseras, direccionales funcionando", "peso": 5},
            {"item": "Frenos", "descripcion": "Sistema de frenos funcionando correctamente", "peso": 5},
            {"item": "Neumáticos", "descripcion": "Neumáticos con buena profundidad y presión", "peso": 5},
            {"item": "Dirección", "descripcion": "Dirección suave sin holguras", "peso": 4},
            {"item": "Limpiaparabrisas", "descripcion": "Limpiaparabrisas funcionando, líquido disponible", "peso": 3},
            {"item": "Cinturones de seguridad", "descripcion": "Cinturones operativos y en buen estado", "peso": 5},
            {"item": "Espejos", "descripcion": "Espejos ajustados y sin roturas", "peso": 4},
            {"item": "Claxon", "descripcion": "Claxon funcionando", "peso": 2},
            {"item": "Kit de carretera", "descripcion": "Kit completo y vigente", "peso": 3},
            {"item": "Extintor", "descripcion": "Extintor cargado y vigente", "peso": 5},
            {"item": "Botiquín", "descripcion": "Botiquín completo y vigente", "peso": 3},
            {"item": "Documentos", "descripcion": "SOAT, tecnomecánica, licencia vigentes", "peso": 5}
        ]
    },
    "andamios": {
        "nombre": "Inspección de Andamios",
        "items": [
            {"item": "Estructura general", "descripcion": "Andamio estable, sin deformaciones", "peso": 5},
            {"item": "Bases niveladoras", "descripcion": "Bases firmes y niveladas", "peso": 5},
            {"item": "Plataforma de trabajo", "descripcion": "Plataforma completa y firme", "peso": 5},
            {"item": "Barandas", "descripcion": "Barandas superiores, intermedias y rodapiés instalados", "peso": 5},
            {"item": "Acceso", "descripcion": "Escalera de acceso segura", "peso": 4},
            {"item": "Arriostramientos", "descripcion": "Cruces de San Andrés instalados", "peso": 5},
            {"item": "Anclajes", "descripcion": "Anclajes seguros a estructura", "peso": 5},
            {"item": "Ruedas", "descripcion": "Ruedas con frenos funcionando", "peso": 3}
        ]
    }
}
