# core/data/tipos_documentos.py

TIPOS_DOCUMENTOS = [
    {"id": "politica", "nombre": "Política SST", "icono": "📜", "template": "politica_sst_template.docx"},
    {"id": "procedimiento", "nombre": "Procedimiento", "icono": "📋", "template": "procedimiento_template.docx"},
    {"id": "instructivo", "nombre": "Instructivo", "icono": "📖", "template": "instructivo_template.docx"},
    {"id": "formato", "nombre": "Formato", "icono": "📝", "template": "formato_template.xlsx"},
    {"id": "manual", "nombre": "Manual", "icono": "📘", "template": "manual_template.docx"},
    {"id": "plan", "nombre": "Plan", "icono": "📊", "template": "plan_template.docx"},
    {"id": "registro", "nombre": "Registro", "icono": "📒", "template": "registro_template.xlsx"},
    {"id": "certificado", "nombre": "Certificado", "icono": "🏅", "template": "certificado_template.docx"},
    {"id": "informe", "nombre": "Informe", "icono": "📑", "template": "informe_template.docx"}
]

CATEGORIAS_DOCUMENTOS = [
    {"id": "sst", "nombre": "Sistema de Gestión SST"},
    {"id": "legal", "nombre": "Marco Legal"},
    {"id": "capacitacion", "nombre": "Capacitaciones"},
    {"id": "incidentes", "nombre": "Incidentes"},
    {"id": "peligros", "nombre": "Peligros y Riesgos"},
    {"id": "auditoria", "nombre": "Auditorías"},
    {"id": "emergencia", "nombre": "Emergencias"},
    {"id": "inspeccion", "nombre": "Inspecciones"},
    {"id": "trabajadores", "nombre": "Trabajadores"}
]

PLANTILLAS_PREDEFINIDAS = {
    "politica_sst": {
        "titulo": "Política de Seguridad y Salud en el Trabajo",
        "contenido": """La empresa [NOMBRE_EMPRESA] se compromete con:

1. Proteger la seguridad y salud de todos los trabajadores.
2. Cumplir con la legislación vigente en SST.
3. Mejorar continuamente el SG-SST.
4. Prevenir lesiones y enfermedades laborales.
5. Consultar y participar a los trabajadores.

Firmado: [NOMBRE_REPRESENTANTE]
Cargo: [CARGO]
Fecha: [FECHA]"""
    },
    "procedimiento_general": {
        "titulo": "Procedimiento para [TITULO]",
        "contenido": """1. OBJETIVO
[Describir el objetivo]

2. ALCANCE
[Describir el alcance]

3. RESPONSABLES
[Listar responsables]

4. DEFINICIONES
[Definir términos]

5. DESARROLLO DEL PROCEDIMIENTO
| Paso | Actividad | Responsable | Registro |
|------|-----------|-------------|----------|
| 1    |           |             |          |
| 2    |           |             |          |

6. DOCUMENTOS RELACIONADOS
[Listar documentos]

7. CONTROL DE CAMBIOS
| Versión | Fecha | Cambios | Aprobado por |
|---------|-------|---------|--------------|
| 1.0     |       |         |              |"""
    },
    "formato_registro": {
        "titulo": "Registro de [TITULO]",
        "contenido": """FECHA: _______________
HORA: _______________
RESPONSABLE: _______________

DESCRIPCIÓN:
_________________________________
_________________________________

OBSERVACIONES:
_________________________________

FIRMA: ___________________"""
    }
}
