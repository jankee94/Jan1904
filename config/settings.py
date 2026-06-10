# config/settings.py
import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    # App
    APP_NAME = "SG-SST PHVA"
    APP_VERSION = "3.0.0"
    APP_ENV = os.getenv("APP_ENV", "production")
    
    # Firebase
    FIREBASE_API_KEY = os.getenv("FIREBASE_API_KEY", "")
    FIREBASE_AUTH_DOMAIN = os.getenv("FIREBASE_AUTH_DOMAIN", "")
    FIREBASE_PROJECT_ID = os.getenv("FIREBASE_PROJECT_ID", "")
    FIREBASE_STORAGE_BUCKET = os.getenv("FIREBASE_STORAGE_BUCKET", "")
    FIREBASE_MESSAGING_SENDER_ID = os.getenv("FIREBASE_MESSAGING_SENDER_ID", "")
    FIREBASE_APP_ID = os.getenv("FIREBASE_APP_ID", "")
    
    # Collections Firestore
    COLLECTIONS = {
        "usuarios": "usuarios",
        "empresas": "empresas",
        "trabajadores": "trabajadores",
        "peligros": "peligros",
        "acciones": "acciones",
        "incidentes": "incidentes",
        "matriz_legal": "matriz_legal",
        "auditorias": "auditorias",
        "planes_anuales": "planes_anuales",
        "capacitaciones": "capacitaciones",
        "inspecciones": "inspecciones",
        "emergencias": "emergencias",
        "documentos": "documentos",
        "indicadores": "indicadores",
        "logs": "logs",
        "configuracion": "configuracion"
    }
    
    # Roles
    ROLES = {
        "admin": ["todos"],
        "responsable_sst": ["peligros", "acciones", "trabajadores", "incidentes", "matriz_legal", "capacitaciones", "inspecciones"],
        "auditor": ["auditorias", "matriz_legal", "incidentes"],
        "jefe_area": ["trabajadores", "incidentes", "inspecciones"],
        "trabajador": ["incidentes", "capacitaciones"]
    }
    
    # Paginación
    PAGE_SIZE = 20
    MAX_UPLOAD_SIZE = 10 * 1024 * 1024  # 10MB
    
    # IA
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
    GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
    
settings = Settings()
