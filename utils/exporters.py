# utils/exporters.py
import pandas as pd
from datetime import datetime
import streamlit as st

def exportar_excel(df, nombre_archivo):
    """Exportar DataFrame a Excel"""
    if df.empty:
        st.warning("No hay datos para exportar")
        return None
    
    fecha = datetime.now().strftime("%Y%m%d_%H%M%S")
    nombre_completo = f"{nombre_archivo}_{fecha}.xlsx"
    
    with pd.ExcelWriter(nombre_completo, engine='openpyxl') as writer:
        df.to_excel(writer, sheet_name='Datos', index=False)
        
        # Ajustar ancho de columnas
        for column in df:
            column_width = max(df[column].astype(str).map(len).max(), len(column))
            writer.sheets['Datos'].column_dimensions[column].width = min(column_width + 2, 50)
    
    return nombre_completo

def exportar_csv(df, nombre_archivo):
    """Exportar DataFrame a CSV"""
    if df.empty:
        st.warning("No hay datos para exportar")
        return None
    
    fecha = datetime.now().strftime("%Y%m%d_%H%M%S")
    nombre_completo = f"{nombre_archivo}_{fecha}.csv"
    df.to_csv(nombre_completo, index=False, encoding='utf-8-sig')
    return nombre_completo

def boton_exportar(df, nombre, formatos=["Excel"]):
    """Botón genérico para exportar"""
    col1, col2 = st.columns(2)
    with col1:
        if st.button(f"📊 Exportar {nombre} a Excel", key=f"excel_{nombre}"):
            archivo = exportar_excel(df, nombre)
            if archivo:
                with open(archivo, "rb") as f:
                    st.download_button(
                        label="📥 Descargar Excel",
                        data=f,
                        file_name=archivo,
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                    )
    with col2:
        if st.button(f"📄 Exportar {nombre} a CSV", key=f"csv_{nombre}"):
            archivo = exportar_csv(df, nombre)
            if archivo:
                with open(archivo, "rb") as f:
                    st.download_button(
                        label="📥 Descargar CSV",
                        data=f,
                        file_name=archivo,
                        mime="text/csv"
                    )
