import streamlit as st
import pandas as pd
from io import BytesIO

def exportar_datos(df, nombre_modulo):
    """Exportar datos a CSV y Excel"""
    if df is not None and not df.empty:
        col1, col2 = st.columns(2)
        with col1:
            csv = df.to_csv(index=False)
            st.download_button("📥 Descargar CSV", csv, f"{nombre_modulo}.csv", "text/csv")
        with col2:
            output = BytesIO()
            with pd.ExcelWriter(output, engine='openpyxl') as writer:
                df.to_excel(writer, index=False)
            st.download_button("📊 Descargar Excel", output.getvalue(), f"{nombre_modulo}.xlsx")
    else:
        st.info("No hay datos para exportar")
