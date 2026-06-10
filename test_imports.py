# test_imports.py - Script para verificar que los módulos se importan correctamente
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

print("Verificando imports de módulos...")

try:
    from modules.capacitaciones.ui import render_capacitaciones
    print("✅ Capacitaciones - OK")
except Exception as e:
    print(f"❌ Capacitaciones - Error: {e}")

try:
    from modules.inspecciones.ui import render_inspecciones
    print("✅ Inspecciones - OK")
except Exception as e:
    print(f"❌ Inspecciones - Error: {e}")

try:
    from modules.emergencias.ui import render_emergencias
    print("✅ Emergencias - OK")
except Exception as e:
    print(f"❌ Emergencias - Error: {e}")

try:
    from modules.documental.ui import render_documental
    print("✅ Gestión Documental - OK")
except Exception as e:
    print(f"❌ Gestión Documental - Error: {e}")

print("\n✅ Verificación completada")
