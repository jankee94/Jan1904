# config/settings.py
import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    # App
    APP_NAME = os.getenv("APP_NAME", "SG-SST PHVA")
    APP_ENV = os.getenv("APP_ENV", "development")
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-key")
    
    # Firebase
    FIREBASE_CREDENTIALS_PATH = os.getenv("FIREBASE_CREDENTIALS_PATH", "firebase-credentials.json")
    FIREBASE_PROJECT_ID = os.getenv("FIREBASE_PROJECT_ID", "programa-sst")
    
    # APIs
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
    DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY", "")
    
    # Collections
    COLLECTIONS = {
        "usuarios": "usuarios",
        "trabajadores": "trabajadores",
        "incidentes": "incidentes",
        "peligros": "peligros",
        "capacitaciones": "capacitaciones",
        "auditorias": "auditorias",
        "plan_anual": "plan_anual",
        "politicas_sst": "politicas_sst",
        "matriz_legal": "matriz_legal",
        "plan_emergencias": "plan_emergencias",
        "auditoria_cambios": "auditoria_cambios",
        "configuracion": "configuracion"
    }
    
    # Roles
    ROLES = ["admin", "responsable_sst", "supervisor", "trabajador", "auditor"]
    
    # Pagination
    PAGE_SIZE = 20

settings = Settings()