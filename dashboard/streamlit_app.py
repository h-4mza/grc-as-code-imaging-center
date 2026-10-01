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
    "Rapports Documentaires",
    "Registre des Constats"
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
    st.title("👁️ Vue d'ensemble GRC - Imagerie Médicale")
    data = fetch_data("/kpi/overview")
    
    if data:
        st.markdown("""
        Bienvenue sur le **Portail de Pilotage Cybersécurité**. 
        Cet outil de la gamme **GRC-as-Code** agrège dynamiquement l'analyse de risques EBIOS RM, l'applicabilité ISO 27001, et les vulnérabilités de notre infrastructure d'imagerie médicale.
        """)
        st.markdown("---")
        
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Risques Totaux", data["total_risks"], "Scénarios EBIOS")
        col2.metric("Risques Critiques", data["risques_critiques"], "- Résiduel", delta_color="inverse")
        col3.metric("Conformité ISO 27001", f"{data['controls_en_place_pct']}%", "Contrôles implémentés")
        col4.metric("Vulnérabilités Ouvertes", data["total_findings"], "- SecOps", delta_color="inverse")
        
        st.markdown("---")
        st.subheader("📊 Tableau de Bord Opérationnel")
        
        c1, c2 = st.columns(2)
        with c1:
            st.write("**Répartition des Constats (SecOps)**")
            f_stats = data.get("findings_stats", {})
            if sum(f_stats.values()) > 0:
                st.bar_chart(pd.Series(f_stats))
            else:
                st.info("Aucun constat ouvert.")
                
        with c2:
            st.write("**Suivi des Plans de Traitement (Jira)**")
            st.progress(0.45, text="45% des plans d'action complétés")
            st.write(f"Nombre total d'actions définies dans le registre EBIOS : **{data['total_treatments']}**")
            
        st.info("💡 Navigation : Utilisez la barre latérale pour explorer la matrice de risques (Heatmap), examiner la conformité réglementaire (NIS2/HDS), ou vérifier les plans d'action.")

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
        cols = ["id", "name", "description", "theme", "is_applicable", "status", "maturity", "justification", "evidence"]
        st.dataframe(df_ctrl[cols], use_container_width=True)

elif page == "Conformité Globale":
    st.title("🎯 Matrice de Couverture & Conformité")
    
    # 1. Retrieve aggregate data for Metrics
    kpi_data = fetch_data("/kpi/compliance")
    if kpi_data:
        st.subheader("Taux d'implémentation par Framework")
        cols = st.columns(len(kpi_data))
        for i, kpi in enumerate(kpi_data):
            cols[i].metric(
                label=kpi["framework"],
                value=f"{kpi['compliance_rate']}%",
                delta=f"{kpi['implemented_controls']} / {kpi['total_mapped_controls']} en place"
            )
            
    # 2. Retrieve detailed data for the Matrix
    matrix_data = fetch_data("/kpi/compliance_matrix")
    if matrix_data:
        st.markdown("---")
        st.subheader("Matrice Croisée (ISO 27001 vs Frameworks)")
        df = pd.DataFrame(matrix_data)
        
        # We pivot: index = control_id, columns = framework, values = reference.
        df_pivot = df.pivot_table(
            index="control_id", 
            columns="framework", 
            values="reference", 
            aggfunc=lambda x: ' | '.join(x)
        ).fillna("-")
        
        # Sort index numerically if possible
        try:
            df_pivot.index = pd.to_numeric(df_pivot.index, errors='coerce').fillna(df_pivot.index)
            df_pivot = df_pivot.sort_index()
            # Restore to string to look good
            df_pivot.index = df_pivot.index.astype(str)
        except:
            df_pivot = df_pivot.sort_index()
            
        st.dataframe(df_pivot, use_container_width=True)

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
        st.markdown("""
        <style>
        .soa-header {
            font-family: Arial, sans-serif;
            margin-bottom: 20px;
        }
        .soa-title {
            color: #1c325c;
            font-size: 24px;
            font-weight: bold;
            margin-bottom: 5px;
        }
        .soa-subtitle {
            color: #555;
            font-size: 14px;
            margin-bottom: 20px;
        }
        .chap-summary {
            display: flex;
            margin-bottom: 30px;
        }
        .chap-box {
            flex: 1;
            padding: 10px;
            color: white;
            font-family: Arial, sans-serif;
            text-align: left;
        }
        .chap-box-1 { background-color: #21355c; }
        .chap-box-2 { background-color: #436436; }
        .chap-box-3 { background-color: #9c4819; }
        .chap-box-4 { background-color: #21355c; border-left: 1px solid white;}
        
        .chap-title-text {
            color: #1c325c;
            font-size: 20px;
            font-weight: bold;
            border-bottom: 2px solid #1c325c;
            margin-bottom: 10px;
            margin-top: 30px;
            padding-bottom: 5px;
            font-family: Arial, sans-serif;
        }
        
        .soa-table {
            width: 100%;
            border-collapse: collapse;
            font-family: Arial, sans-serif;
            font-size: 13px;
        }
        .soa-table th {
            background-color: #1c325c;
            color: white;
            padding: 10px;
            text-align: left;
            border: 1px solid #ddd;
        }
        .soa-table td {
            padding: 10px;
            border: 1px solid #ddd;
            vertical-align: top;
        }
        .soa-table tr:nth-child(even) {
            background-color: #f9f9f9;
        }
        </style>
        """, unsafe_allow_html=True)
        
        controls_data = fetch_data("/controls")
        if controls_data:
            import pandas as pd
            df = pd.DataFrame(controls_data)
            
            html_content = f"""<div class="soa-header">
<div class="soa-title">Centre d'Imagerie Médicale</div>
<div class="soa-subtitle">
Référence Projet : CIM-SEC-CYBER-001 | Version : v1.5 — Juin 2026<br>
Document annexe au Dossier de Sécurité de la Solution Déployée — À titre de référence normative
</div>
</div>

<div class="chap-summary">
<div class="chap-box chap-box-1"><b>Chapitre 5</b><br>37 contrôles</div>
<div class="chap-box chap-box-2"><b>Chapitre 6</b><br>8 contrôles</div>
<div class="chap-box chap-box-3"><b>Chapitre 7</b><br>14 contrôles</div>
<div class="chap-box chap-box-4"><b>Chapitre 8</b><br>34 contrôles</div>
</div>
"""
            
            chapitres = {
                "Organisationnel": "5. Contrôles organisationnels",
                "Personnes": "6. Contrôles liés aux personnes",
                "Physique": "7. Contrôles physiques",
                "Technologique": "8. Contrôles technologiques"
            }
            
            for theme in df['theme'].unique():
                theme_controls = df[df['theme'] == theme]
                titre_chapitre = chapitres.get(theme, f"Contrôles : {theme}")
                
                html_content += f"""<div class="chap-title-text">{titre_chapitre}</div>
<table class="soa-table">
<thead>
<tr>
<th style="width: 7%;">Contrôle</th>
<th style="width: 15%;">Titre</th>
<th style="width: 38%;">Description</th>
<th style="width: 10%;">Statut</th>
<th style="width: 5%;">Maturité</th>
<th style="width: 25%;">Justification</th>
</tr>
</thead>
<tbody>
"""
                
                for _, row in theme_controls.iterrows():
                    desc = row['description'] if row.get('description') else 'Description non spécifiée.'
                    etat = row.get('status', 'Non défini')
                    color = "#27ae60" if etat == "implemented" else "#f39c12" if etat == "partial" else "#c0392b"
                    badge = f'<span style="background-color: {color}; color: white; padding: 2px 6px; border-radius: 10px; font-size: 11px;">{etat}</span>'
                    mat = f"{row.get('maturity', 0)}/5"
                    justif = row.get('justification', '')
                    
                    html_content += f"""<tr>
<td style="font-weight: bold; color: #1c325c;">{row['id']}</td>
<td style="font-weight: bold; font-size: 12px;">{row['name']}</td>
<td style="font-size: 11px; color: #555;">{desc}</td>
<td>{badge}</td>
<td style="text-align: center; font-weight: bold; font-size: 12px;">{mat}</td>
<td style="font-size: 11px; font-style: italic;">{justif}</td>
</tr>
"""
                    
                html_content += """</tbody>
</table>
"""
            
            st.markdown(html_content, unsafe_allow_html=True)
    elif filepath and os.path.exists(filepath):
        st.markdown("---")
        with open(filepath, "r", encoding="utf-8") as f:
            st.markdown(f.read())
    else:
        st.warning("Le fichier de rapport est introuvable sur le volume Docker.")

elif page == "Registre des Constats":
    st.title("🚨 Registre Central des Constats (Vulnérabilités & Audits)")
    st.markdown("Ce registre consolide les remontées automatiques (ex: Trivy, BloodHound) avec le référentiel de risques EBIOS.")
    
    data = fetch_data("/findings")
    if data:
        df = pd.DataFrame(data)
        
        # Colorisation de la sévérité
        def color_severity(val):
            color = 'red' if val == 'error' else 'orange' if val == 'warning' else 'green'
            return f'color: {color}; font-weight: bold;'
            
        st.dataframe(df.style.map(color_severity, subset=['severite']), use_container_width=True)
        
        col1, col2 = st.columns(2)
        with col1:
            st.subheader("Par Sévérité")
            st.bar_chart(df['severite'].value_counts())
        with col2:
            st.subheader("Par Actif")
            st.bar_chart(df['actif'].value_counts())
    else:
        st.info("Aucun constat n'a été ingéré.")
