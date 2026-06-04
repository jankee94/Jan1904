import streamlit as st

def render(db, ia):
    st.title("📊 Dashboard")
    peligros = db.fetch_all("SELECT * FROM peligros")
    st.metric("Total Peligros", len(peligros))
