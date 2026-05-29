import streamlit as st
import hashlib
import sqlite3
import re
from datetime import datetime

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def verificar_login(username, password):
    conn = sqlite3.connect('sst.db')
    cursor = conn.cursor()
    hashed = hash_password(password)
    cursor.execute("SELECT * FROM usuarios WHERE username = ? AND password = ?", (username, hashed))
    user = cursor.fetchone()
    conn.close()
    return user is not None

def registrar_usuario(username, password, rol="usuario"):
    if len(password) < 6:
        return False, "La contraseña debe tener al menos 6 caracteres"
    conn = sqlite3.connect('sst.db')
    cursor = conn.cursor()
    hashed = hash_password(password)
    try:
        cursor.execute("INSERT INTO usuarios (username, password, rol) VALUES (?, ?, ?)", (username, hashed, rol))
        conn.commit()
        return True, "Usuario registrado"
    except sqlite3.IntegrityError:
        return False, "El usuario ya existe"
    finally:
        conn.close()

def cambiar_password(username, old_password, new_password):
    conn = sqlite3.connect('sst.db')
    cursor = conn.cursor()
    old_hashed = hash_password(old_password)
    cursor.execute("SELECT * FROM usuarios WHERE username = ? AND password = ?", (username, old_hashed))
    if cursor.fetchone():
        new_hashed = hash_password(new_password)
        cursor.execute("UPDATE usuarios SET password = ? WHERE username = ?", (new_hashed, username))
        conn.commit()
        conn.close()
        return True
    conn.close()
    return False

def login_ui():
    st.markdown("### 🔐 Inicio de Sesión")
    col1, col2 = st.columns(2)
    with col1:
        usuario = st.text_input("Usuario")
        password = st.text_input("Contraseña", type="password")
        if st.button("Ingresar", use_container_width=True):
            if verificar_login(usuario, password):
                st.session_state.authenticated = True
                st.session_state.username = usuario
                st.rerun()
            else:
                st.error("Credenciales incorrectas")
    with col2:
        st.markdown("#### Registrar nuevo usuario")
        new_user = st.text_input("Nuevo usuario")
        new_pass = st.text_input("Nueva contraseña", type="password")
        if st.button("Registrar", use_container_width=True):
            ok, msg = registrar_usuario(new_user, new_pass)
            if ok:
                st.success(msg)
            else:
                st.error(msg)
