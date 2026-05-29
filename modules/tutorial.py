import streamlit as st
import time

def mostrar_tutorial():
    st.markdown("""
    <style>
    .tutorial-step {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1rem;
        border-radius: 15px;
        color: white;
        margin-bottom: 1rem;
    }
    .demo-box {
        background: #1e1e2e;
        padding: 1rem;
        border-radius: 10px;
        border-left: 4px solid #00a86b;
        margin: 1rem 0;
    }
    </style>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    <div class="tutorial-step">
        <h2>🎓 Tutorial Interactivo</h2>
        <p>Aprende a usar el Asistente IA mientras ves cómo modifica la aplicación</p>
    </div>
    """, unsafe_allow_html=True)
    
    with st.expander("📌 Paso 1: ¿Qué puede hacer la IA?", expanded=True):
        st.markdown("""
        El asistente IA puede:
        - Modificar el diseño de la aplicación
        - Agregar nuevas funcionalidades
        - Revisar y corregir código
        - Exportar datos a Excel/CSV
        - Crear gráficos automaticamente
        """)
        
        if st.button("Ver demostracion 1"):
            with st.chat_message("assistant"):
                st.markdown("IA: Voy a modificar el color del header...")
                time.sleep(1)
                st.markdown("Cambio realizado: El header ahora es verde corporativo")
                st.balloons()
    
    with st.expander("📌 Paso 2: Como pedir cambios a la IA", expanded=False):
        st.markdown("""
        Ejemplos de comandos:
        
        | Comando | Que hace |
        |---------|----------|
        | Cambia el header a azul | Modifica colores |
        | Agrega exportar a Excel | Anade boton de descarga |
        | Revisa mi codigo | Analiza errores |
        | Haz un grafico | Crea visualizaciones |
        """)
        
        ejemplo = st.text_input("Prueba un comando aqui:")
        if ejemplo:
            with st.chat_message("assistant"):
                st.markdown(f"Procesando: {ejemplo}")
                st.info("Escribe este comando en el chat principal del Asistente IA")
    
    with st.expander("📌 Paso 3: Ver la IA en accion", expanded=False):
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Cambiar tema oscuro"):
                with st.chat_message("assistant"):
                    st.markdown("IA: Aplicando tema oscuro...")
                    st.markdown("Tema oscuro activado")
        with col2:
            if st.button("Mostrar ejemplo de grafico"):
                with st.chat_message("assistant"):
                    st.markdown("IA: Generando grafico...")
                    st.success("Grafico creado correctamente")
    
    with st.expander("📌 Paso 4: Comandos utiles", expanded=False):
        st.markdown("""
        Comandos que puedes copiar:
        
        - "Agrega un boton de exportar a Excel en trabajadores"
        - "Cambia el color del fondo a gris"
        - "Agrega un grafico de progreso"
        - "Revisa si hay errores en politicas_sst"
        """)

def mostrar_ejemplo_interactivo():
    st.markdown("### Demostracion Interactiva")
    
    cambio = st.text_area("Describe que quieres modificar:")
    
    if cambio:
        with st.chat_message("assistant"):
            st.markdown(f"IA analizando: {cambio}")
            st.markdown("""
            **Cambios sugeridos:**
            
            1. Archivo: app.py
            2. Seccion: CSS styles
            3. Copia el nuevo codigo y pegalo en app.py
            """)