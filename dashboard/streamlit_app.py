import streamlit as st
import requests
import os
import pandas as pd

API_URL = os.getenv("API_URL", "http://localhost:8000")

st.set_page_config(page_title="GRC Dashboard", layout="wide", page_icon="🛡️")

st.sidebar.title("Navigation GRC")
page = st.sidebar.radio("Menu", ["Vue d'ensemble", "Heatmap des Risques", "SoA (ISO 27001)", "Conformité Globale", "Plan de Traitement"])

def fetch_data(endpoint):
    try:
        response = requests.get(f"{API_URL}{endpoint}")
        response.raise_for_status()
        return response.json()
    except Exception as e:
        st.error(f"Erreur de connexion à l'API: {e}")
        return None

if page == "Vue d'ensemble":
    st.title("🛡️ Vue d'ensemble GRC - Imagerie Médicale")
    data = fetch_data("/kpi/overview")
    
    if data:
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Risques Totaux", data["total_risks"])
        col2.metric("Risques Critiques", data["risques_critiques"], delta_color="inverse")
        col3.metric("Contrôles en place", f"{data['controls_en_place_pct']}%")
        col4.metric("Vulnérabilités Ouvertes", data["total_findings"])
        
        st.markdown("---")
        st.subheader("Bienvenue sur le tableau de bord de pilotage.")
        st.write("Ce portail centralise l'analyse EBIOS RM, la déclaration d'applicabilité ISO 27001 et le suivi des vulnérabilités de notre centre d'imagerie.")

elif page == "Heatmap des Risques":
    st.title("🔥 Heatmap des Risques (Inhérent vs Résiduel)")
    data = fetch_data("/kpi/heatmap")
    if data:
        df = pd.DataFrame(data)
        st.dataframe(df[["id", "nom", "gravite", "vraisemblance_inherente", "niveau_inherent", "niveau_residuel"]], use_container_width=True)
        
        st.subheader("Matrice Inhérente (Gravité x Vraisemblance)")
        st.scatter_chart(df, x="gravite", y="vraisemblance_inherente", color="niveau_inherent")

elif page == "SoA (ISO 27001)":
    st.title("✅ Déclaration d'Applicabilité (ISO 27001)")
    data = fetch_data("/kpi/soa")
    if data:
        df = pd.DataFrame(data)
        df["progression (%)"] = (df["en_place"] / df["total"] * 100).round(1)
        st.dataframe(df, use_container_width=True)
        st.bar_chart(df.set_index("theme")[["en_place", "total"]])

elif page == "Conformité Globale":
    st.title("🌍 Mappings de Conformité (NIS2, ATT&CK, NIST)")
    data = fetch_data("/kpi/compliance")
    if data:
        df = pd.DataFrame(data)
        st.write("Couverture des frameworks de conformité à travers nos contrôles :")
        st.dataframe(df, use_container_width=True)
        st.bar_chart(df.set_index("framework"))

elif page == "Plan de Traitement":
    st.title("🚀 Plan de Traitement de Sécurité (PTS)")
    data = fetch_data("/kpi/treatments")
    if data:
        df = pd.DataFrame(data)
        st.dataframe(df, use_container_width=True)
        st.success("Les traitements sont synchronisés avec Jira via GRC as-code.")
