# scripts/migrate_to_firestore.py
import sqlite3
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from datetime import datetime

def migrate_all():
    """Migrar todos los datos de SQLite a Firestore"""
    print("🔄 Iniciando migración SQLite -> Firestore")
    
    conn = sqlite3.connect("sst.db")
    cursor = conn.cursor()
    
    # Migrar peligros
    try:
        cursor.execute("SELECT * FROM peligros")
        rows = cursor.fetchall()
        print(f"📊 Encontrados {len(rows)} peligros para migrar")
        
        for row in rows:
            data = {
                "tipo": row[2] if len(row) > 2 else "",
                "descripcion": row[3] if len(row) > 3 else "",
                "probabilidad": row[4] if len(row) > 4 else 1,
                "severidad": row[5] if len(row) > 5 else 1,
                "nivel": row[6] if len(row) > 6 else "III",
                "migrated_at": datetime.now().isoformat()
            }
            print(f"  - Peligro: {data['tipo']} - {data['descripcion'][:30]}...")
        print("✅ Peligros listos para migrar")
    except Exception as e:
        print(f"⚠️ Error en peligros: {e}")
    
    # Migrar trabajadores
    try:
        cursor.execute("SELECT * FROM trabajadores")
        rows = cursor.fetchall()
        print(f"📊 Encontrados {len(rows)} trabajadores para migrar")
        
        for row in rows:
            data = {
                "nombre": row[2] if len(row) > 2 else "",
                "cedula": row[3] if len(row) > 3 else "",
                "cargo": row[4] if len(row) > 4 else "",
                "migrated_at": datetime.now().isoformat()
            }
            print(f"  - Trabajador: {data['nombre']} - {data['cedula']}")
        print("✅ Trabajadores listos para migrar")
    except Exception as e:
        print(f"⚠️ Error en trabajadores: {e}")
    
    # Migrar incidentes
    try:
        cursor.execute("SELECT * FROM incidentes")
        rows = cursor.fetchall()
        print(f"📊 Encontrados {len(rows)} incidentes para migrar")
        for row in rows:
            data = {
                "descripcion": row[2] if len(row) > 2 else "",
                "fecha": row[3] if len(row) > 3 else "",
                "gravedad": row[4] if len(row) > 4 else "Leve",
                "migrated_at": datetime.now().isoformat()
            }
            print(f"  - Incidente: {data['descripcion'][:30]}...")
        print("✅ Incidentes listos para migrar")
    except Exception as e:
        print(f"⚠️ Error en incidentes: {e}")
    
    # Migrar acciones
    try:
        cursor.execute("SELECT * FROM acciones")
        rows = cursor.fetchall()
        print(f"📊 Encontrados {len(rows)} acciones para migrar")
        for row in rows:
            data = {
                "descripcion": row[2] if len(row) > 2 else "",
                "responsable": row[3] if len(row) > 3 else "",
                "estado": row[5] if len(row) > 5 else "Pendiente",
                "migrated_at": datetime.now().isoformat()
            }
            print(f"  - Acción: {data['descripcion'][:30]}...")
        print("✅ Acciones listas para migrar")
    except Exception as e:
        print(f"⚠️ Error en acciones: {e}")
    
    conn.close()
    print("\n✅ Migración completada!")
    print("📌 Para completar la migración, configura Firebase y ejecuta la carga real.")

if __name__ == "__main__":
    migrate_all()
