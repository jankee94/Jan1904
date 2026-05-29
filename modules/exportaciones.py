import streamlit as st
import pandas as pd
from io import BytesIO

def exportar_csv(df, nombre):
    csv = df.to_csv(index=False)
    st.download_button("📥 Exportar CSV", csv, f"{nombre}.csv", "text/csv")

def exportar_excel(df, nombre):
    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False)
    st.download_button("📊 Exportar Excel", output.getvalue(), f"{nombre}.xlsx")
