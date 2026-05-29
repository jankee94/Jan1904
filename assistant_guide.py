import streamlit as st
import requests
import json
import PyPDF2
import docx
import io

class AssistantGuide:
    def __init__(self):
        self.api_key = st.secrets.get("GEMINI_API_KEY")
        self.conversation_history = []
        self.empresa_data = {}
        
    def call_gemini(self, prompt, system_prompt=""):
        url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-flash-latest:generateContent"
        headers = {"Content-Type": "application/json", "X-goog-api-key": self.api_key}
        full_prompt = system_prompt + "\n\n" + prompt if system_prompt else prompt
        data = {"contents": [{"parts": [{"text": full_prompt}]}]}
        try:
            r = requests.post(url, headers=headers, json=data, timeout=60)
            if r.status_code == 200:
                return r.json()["candidates"][0]["content"]["parts"][0]["text"]
            return f"Error: {r.status_code}"
        except Exception as e:
            return f"Error: {e}"
    
    def extract_text_from_pdf(self, file):
        reader = PyPDF2.PdfReader(file)
        text = ""
        for page in reader.pages:
            text += page.extract_text()
        return text
    
    def extract_text_from_docx(self, file):
        doc = docx.Document(file)
        text = "\n".join([para.text for para in doc.paragraphs])
        return text
    
    def generar_estructura_completa(self, datos_empresa, normativa_aplicable=""):
        prompt = f"""
        Basado en la siguiente información de la empresa:
        - Nombre: {datos_empresa.get('nombre', 'No especificado')}
        - Sector: {datos_empresa.get('sector', 'No especificado')}
        - Riesgos principales: {datos_empresa.get('riesgos', 'No especificados')}
        - Número de empleados: {datos_empr式sa.get('empleados', 'No especificado')}
        - Normativa aplicable: {normativa_aplicable}
        
        Genera un plan completo de Seguridad y Salud en el Trabajo (SST) que incluya:
        1. ESTRUCTURA DE DATOS (tablas necesarias y sus campos)
        2. DOCUMENTOS REQUERIDOS (políticas, procedimientos, matrices)
        3. CARGOS Y RESPONSABILIDADES (roles SST)
        4. PLAN DE ACCIÓN (tareas, plazos, indicadores)
        
        Devuelve la respuesta en formato JSON con estas secciones.
        """
        respuesta = self.call_gemini(prompt, "Eres un experto ingeniero de SST y desarrollador de software. Genera estructuras técnicas claras.")
        return respuesta
    
    def generar_documento_politica(self, datos_empresa):
        prompt = f"""
        Crea una Política de Seguridad y Salud en el Trabajo para:
        Empresa: {datos_empresa.get('nombre')}
        Sector: {datos_empresa.get('sector')}
        Riesgos: {datos_empresa.get('riesgos')}
        
        La política debe incluir:
        - Declaración de compromiso
        - Objetivos generales y específicos
        - Alcance
        - Responsabilidades
        - Mecanismos de seguimiento
        
        Redacta en lenguaje profesional.
        """
        return self.call_gemini(prompt, "Eres un redactor de políticas SST.")

    def generar_matriz_riesgos(self, datos_empresa):
        prompt = f"""
        Genera una matriz de identificación de peligros y valoración de riesgos (GTC-45) para:
        Empresa: {datos_empresa.get('nombre')}
        Sector: {datos_empresa.get('sector')}
        Riesgos listados: {datos_empresa.get('riesgos')}
        
        Para cada riesgo, incluye:
        - Fuente
        - Efectos posibles
        - Probabilidad (baja, media, alta)
        - Severidad (leve, moderado, grave)
        - Nivel de riesgo
        - Medidas de control propuestas
        
        Devuelve como tabla markdown.
        """
        return self.call_gemini(prompt, "Eres un especialista en riesgos laborales.")

    def generar_plan_emergencia(self, datos_empresa):
        prompt = f"""
        Elabora un Plan de Emergencias para:
        Empresa: {datos_empresa.get('nombre')}
        Sector: {datos_empresa.get('sector')}
        Empleados: {datos_empresa.get('empleados', '?')}
        
        Incluye:
        - Tipos de emergencias consideradas
        - Organización (brigadas, responsables)
        - Rutas de evacuación y puntos de encuentro
        - Equipos de emergencia necesarios
        - Programa de simulacros
        """
        return self.call_gemini(prompt, "Eres un experto en gestión de emergencias.")
    
    def generar_cargos_sst(self, datos_empresa):
        prompt = f"""
        Define la estructura de cargos SST para una empresa de {datos_empresa.get('sector')} con {datos_empresa.get('empleados')} empleados.
        Incluye:
        - Responsable del SG-SST (perfil, funciones)
        - Comité Paritario (COPASST) – conformación y funciones
        - Vigías en SST (si aplica)
        - Roles específicos para cada riesgo identificado: {datos_empresa.get('riesgos')}
        """
        return self.call_gemini(prompt, "Eres un especialista en organización SST.")
