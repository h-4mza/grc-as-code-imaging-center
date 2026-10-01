import streamlit as st

st.set_page_config(page_title="GRC Dashboard", layout="wide")

st.title("Dashboard GRC")
st.write("Bienvenue sur le tableau de bord de pilotage GRC.")

# Navigation simulée pour l'instant (à remplacer par des pages st.Page plus tard)
st.sidebar.title("Navigation")
page = st.sidebar.radio("Aller vers", ["Vue d'ensemble", "Heatmap", "SoA", "Conformité", "Plan de traitement"])

if page == "Vue d'ensemble":
    st.header("Vue d'ensemble")
    st.metric(label="Risques critiques", value=0)
elif page == "Heatmap":
    st.header("Heatmap")
    st.write("Heatmap 4x4 à implémenter.")
