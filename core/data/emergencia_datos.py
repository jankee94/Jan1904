# core/data/emergencia_datos.py

TIPOS_BRIGADA = [
    {"id": "primeros_auxilios", "nombre": "Primeros Auxilios", "descripcion": "Atención inicial de lesionados"},
    {"id": "contra_incendios", "nombre": "Contra Incendios", "descripcion": "Manejo de extintores y control de incendios"},
    {"id": "evacuacion", "nombre": "Evacuación", "descripcion": "Coordinación de evacuaciones"},
    {"id": "rescate", "nombre": "Rescate", "descripcion": "Rescate en alturas y espacios confinados"},
    {"id": "comunicaciones", "nombre": "Comunicaciones", "descripcion": "Coordinación de comunicaciones en emergencia"}
]

TIPOS_EQUIPO = [
    {"id": "extintor_pqs", "nombre": "Extintor PQS", "capacidad": "20 lb", "vida_util": 12},
    {"id": "extintor_co2", "nombre": "Extintor CO2", "capacidad": "10 lb", "vida_util": 12},
    {"id": "botiquin_tipo_a", "nombre": "Botiquín Tipo A", "capacidad": "50 piezas", "vida_util": 12},
    {"id": "botiquin_tipo_b", "nombre": "Botiquín Tipo B", "capacidad": "100 piezas", "vida_util": 12},
    {"id": "camilla_rigida", "nombre": "Camilla Rígida", "capacidad": "150 kg", "vida_util": 60},
    {"id": "camilla_evacuacion", "nombre": "Camilla de Evacuación", "capacidad": "200 kg", "vida_util": 60},
    {"id": "alarma_manual", "nombre": "Alarma Manual", "capacidad": "", "vida_util": 24},
    {"id": "linterna_emergencia", "nombre": "Linterna de Emergencia", "capacidad": "", "vida_util": 24},
    {"id": "radio_comunicacion", "nombre": "Radio de Comunicación", "capacidad": "", "vida_util": 24},
    {"id": "señalizacion", "nombre": "Señalización", "capacidad": "", "vida_util": 36}
]

TIPOS_SIMULACRO = [
    {"id": "incendio", "nombre": "Incendio", "color": "#e74c3c"},
    {"id": "sismo", "nombre": "Sismo", "color": "#f39c12"},
    {"id": "evacuacion", "nombre": "Evacuación General", "color": "#3498db"},
    {"id": "atentado", "nombre": "Atentado", "color": "#9b59b6"},
    {"id": "derrame", "nombre": "Derrame Químico", "color": "#1abc9c"}
]

NIVELES_ALERTA = [
    {"id": "bajo", "nombre": "Bajo", "color": "#27ae60", "acciones": "Monitoreo"},
    {"id": "medio", "nombre": "Medio", "color": "#f39c12", "acciones": "Preparación"},
    {"id": "alto", "nombre": "Alto", "color": "#e67e22", "acciones": "Alerta temprana"},
    {"id": "critico", "nombre": "Crítico", "color": "#e74c3c", "acciones": "Evacuación inmediata"}
]
