# core/logger.py
import logging
from datetime import datetime
import streamlit as st
from core.db import db

class Logger:
    """Sistema de logging profesional"""
    
    def __init__(self, name: str = "SG-SST"):
        self.name = name
        self.setup_logging()
    
    def setup_logging(self):
        """Configurar logging"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(self.name)
    
    def info(self, message: str):
        """Log nivel info"""
        self.logger.info(message)
        self.save_to_db("INFO", message)
    
    def error(self, message: str):
        """Log nivel error"""
        self.logger.error(message)
        self.save_to_db("ERROR", message)
        st.error(f"Error: {message}")
    
    def warning(self, message: str):
        """Log nivel warning"""
        self.logger.warning(message)
        self.save_to_db("WARNING", message)
    
    def save_to_db(self, level: str, message: str):
        """Guardar log en Firestore"""
        try:
            log_data = {
                "level": level,
                "message": message,
                "timestamp": datetime.now(),
                "usuario_id": st.session_state.get("user_id", "anonymous")
            }
            db.create_document("logs", log_data)
        except:
            pass  # No fallar por logs

logger = Logger()