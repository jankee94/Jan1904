import streamlit as st
import hashlib
import sqlite3
import os

def init_auth_db():
    """Inicializar base de datos de usuarios"""
    conn = sqlite3.connect('sst.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            rol TEXT DEFAULT 'usuario',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    # Crear usuario admin por defecto
    admin_pass = hashlib.sha256("sst2024".encode()).hexdigest()
    cursor.execute("INSERT OR IGNORE INTO usuarios (username, password, rol) VALUES (?, ?, ?)",
                   ("admin", admin_pass, "admin"))
    conn.commit()
    conn.close()

def verificar_login(username, password):
    """Verificar credenciales"""
    conn = sqlite3.connect('sst.db')
    cursor = conn.cursor()
    hashed = hashlib.sha256(password.encode()).hexdigest()
    cursor.execute("SELECT * FROM usuarios WHERE username = ? AND password = ?", (username, hashed))
    user = cursor.fetchone()
    conn.close()
    return user is not None

# Inicializar BD al importar
init_auth_db()
