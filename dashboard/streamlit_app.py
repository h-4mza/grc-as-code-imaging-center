import streamlit as st
import requests
import os
import pandas as pd

API_URL = os.getenv("API_URL", "http://localhost:8000")

st.set_page_config(page_title="GRC Dashboard", layout="wide", page_icon="🛡️")

st.sidebar.title("Navigation GRC")
page = st.sidebar.radio("Menu", [
    "Vue d'ensemble", 
    "Heatmap des Risques", 
    "SoA (ISO 27001)", 
    "Conformité Globale", 
    "Plan de Traitement",
    "Rapports Documentaires"
])

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
        
    st.subheader("Détail des Contrôles de l'Annexe A")
    controls_data = fetch_data("/controls")
    if controls_data:
        df_ctrl = pd.DataFrame(controls_data)
        # On réorganise les colonnes pour que ce soit lisible
        cols = ["id", "nom", "description", "theme", "applicable", "etat", "maturite", "justification", "preuve"]
        st.dataframe(df_ctrl[cols], use_container_width=True)

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

elif page == "Rapports Documentaires":
    st.title("📄 Rapports Documentaires GRC")
    
    st.write("Visualisation des rapports générés (EBIOS, ISO 27001).")
    
    report = st.selectbox("Sélectionnez un document à consulter", [
        "Déclaration d'Applicabilité (SoA) - ISO 27001",
        "EBIOS RM - Atelier 4 (Scénarios Opérationnels)"
    ])
    
    file_map = {
        "Déclaration d'Applicabilité (SoA) - ISO 27001": "docs/iso27001/soa.md",
        "EBIOS RM - Atelier 4 (Scénarios Opérationnels)": "docs/ebios/atelier4.md"
    }
    
    filepath = file_map.get(report)
    
    if report == "Déclaration d'Applicabilité (SoA) - ISO 27001":
        # CSS pour un rendu de document officiel professionnel
        st.markdown("""
        <style>
        .report-page {
            background-color: white;
            color: #333;
            padding: 40px 60px;
            border-radius: 8px;
            box-shadow: 0 4px 8px rgba(0,0,0,0.1);
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            margin-bottom: 20px;
        }
        .report-header {
            text-align: right;
            font-size: 12px;
            color: #7f8c8d;
            border-bottom: 1px solid #ecf0f1;
            padding-bottom: 10px;
            margin-bottom: 40px;
        }
        .report-title {
            color: #2c3e50;
            font-size: 32px;
            font-weight: 800;
            text-align: center;
            margin-bottom: 10px;
        }
        .report-subtitle {
            color: #34495e;
            font-size: 18px;
            text-align: center;
            margin-bottom: 50px;
        }
        .chapter-title {
            color: #2980b9;
            font-size: 22px;
            border-bottom: 2px solid #2980b9;
            padding-bottom: 5px;
            margin-top: 40px;
            margin-bottom: 20px;
        }
        .control-box {
            background-color: #f8f9fa;
            border: 1px solid #e0e0e0;
            border-left: 4px solid #2980b9;
            padding: 15px;
            margin-bottom: 15px;
            border-radius: 4px;
        }
        .control-title {
            font-size: 16px;
            font-weight: bold;
            color: #2c3e50;
            margin-bottom: 8px;
        }
        .control-desc {
            font-size: 14px;
            color: #555;
            font-style: italic;
            margin-bottom: 12px;
        }
        .control-meta {
            font-size: 13px;
            color: #444;
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 10px;
        }
        .badge {
            padding: 3px 8px;
            border-radius: 12px;
            font-size: 11px;
            font-weight: bold;
            color: white;
            text-transform: uppercase;
        }
        .bg-success { background-color: #27ae60; }
        .bg-warning { background-color: #f39c12; }
        .bg-danger { background-color: #c0392b; }
        </style>
        """, unsafe_allow_html=True)
        
        controls_data = fetch_data("/controls")
        if controls_data:
            import pandas as pd
            df = pd.DataFrame(controls_data)
            
            html_content = f"""
            <div class="report-page">
                <div class="report-header">
                    <strong>Aéroport Tanger Ibn Batouta — ONDA</strong><br>
                    Référence : ONDA-TNG-SEC-CYBER-001 | Version : v1.5 — Juin 2026<br>
                    Classification : CONFIDENTIEL
                </div>
                
                <div class="report-title">
                    DÉCLARATION D'APPLICABILITÉ (SoA)
                </div>
                <div class="report-subtitle">
                    Référentiel des 93 contrôles de sécurité — Norme ISO/IEC 27001:2022
                </div>
                
                <p style="text-align: justify; font-size: 14px; line-height: 1.6; color: #555;">
                    Le présent document constitue la Déclaration d'Applicabilité (SoA) requise par l'exigence 6.1.3 d) de la norme ISO/IEC 27001:2022. 
                    Il identifie les contrôles de sécurité nécessaires pour traiter les risques liés à la sécurité de l'information pour l'infrastructure 
                    de l'Aéroport Tanger Ibn Batouta, justifie leur inclusion ou exclusion, et précise leur statut d'implémentation actuel.
                </p>
            """
            
            # Map des thèmes aux chapitres ISO 27001:2022
            chapitres = {
                "Organisationnel": "Chapitre 5 — Contrôles Organisationnels",
                "Personnes": "Chapitre 6 — Contrôles liés aux Personnes",
                "Physique": "Chapitre 7 — Contrôles Physiques",
                "Technologique": "Chapitre 8 — Contrôles Technologiques"
            }
            
            for theme in df['theme'].unique():
                theme_controls = df[df['theme'] == theme]
                titre_chapitre = chapitres.get(theme, f"Contrôles : {theme}")
                
                html_content += f'<div class="chapter-title">{titre_chapitre}</div>'
                
                for _, row in theme_controls.iterrows():
                    etat = row['etat']
                    badge_class = "bg-success" if etat == "En place" else "bg-warning" if etat == "Partiel" else "bg-danger"
                    desc = row['description'] if row.get('description') else 'Description non spécifiée.'
                    
                    html_content += f"""
                    <div class="control-box">
                        <div class="control-title">{row['id']} - {row['nom']}</div>
                        <div class="control-desc">« {desc} »</div>
                        <div class="control-meta">
                            <div>
                                <strong>Statut d'implémentation :</strong> <span class="badge {badge_class}">{etat}</span>
                            </div>
                            <div>
                                <strong>Niveau de Maturité :</strong> {row['maturite']}/5
                            </div>
                            <div style="grid-column: span 2; margin-top: 5px;">
                                <strong>Justification / Preuves :</strong> {row['justification']} (Réf: {row['preuve']})
                            </div>
                        </div>
                    </div>
                    """
                    
            html_content += "</div>"
            st.markdown(html_content, unsafe_allow_html=True)
    elif filepath and os.path.exists(filepath):
        st.markdown("---")
        with open(filepath, "r", encoding="utf-8") as f:
            st.markdown(f.read())
    else:
        st.warning("Le fichier de rapport est introuvable sur le volume Docker.")
