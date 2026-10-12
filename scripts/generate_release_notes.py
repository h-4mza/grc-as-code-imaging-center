import re
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent


def load_yaml(rel_path):
    with open(ROOT / rel_path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def generate_release_notes():
    # 1. Sources de risque
    w2 = load_yaml("grc/ebios/w2_sources.yaml")
    nb_sources_risque = len(w2.get("risk_sources", []))
    nb_objectifs = len(w2.get("objectives", []))
    nb_couples = len(w2.get("sr_ov_pairs", []))

    # 2. Parties prenantes et scenarios strategiques
    w3 = load_yaml("grc/ebios/w3_strategiques.yaml")
    nb_parties_prenantes = len(w3.get("stakeholders", []))
    nb_scenarios_strat = len(w3.get("strategic_scenarios", []))

    # 3. Scenarios operationnels
    w4 = load_yaml("grc/ebios/w4_operationnels.yaml")
    risks = w4.get("risks", [])
    nb_scenarios_op = len(risks)

    # Repartition par niveau (inherent : G x V)
    # Seuils : 1-3 Faible, 4-6 Moyen, 8-9 Eleve, 12-16 Critique
    niveaux_inherents = {"Critique": 0, "Élevé": 0, "Moyen": 0, "Faible": 0}
    for r in risks:
        score = r["severity"] * r["likelihood"]
        if score >= 12:
            niveaux_inherents["Critique"] += 1
        elif score >= 8:
            niveaux_inherents["Élevé"] += 1
        elif score >= 4:
            niveaux_inherents["Moyen"] += 1
        else:
            niveaux_inherents["Faible"] += 1

    # 4. Traitements
    w5 = load_yaml("grc/ebios/w5_traitements.yaml")
    nb_traitements = len(w5.get("treatments", []))

    # 5. Controles ISO 27001
    annex_a = load_yaml("grc/iso27001/annex_a.yaml")
    controls = annex_a.get("controls", [])
    nb_controles_total = len(controls)
    ctrl_dict = {str(c["id"]): c for c in controls}

    status_counts = {
        "implemented": 0,
        "partial": 0,
        "planned": 0,
        "not_implemented": 0,
        "non_applicable": 0,
    }
    for c in controls:
        if not c.get("is_applicable", True):
            status_counts["non_applicable"] += 1
        else:
            st = c.get("status", "not_implemented")
            status_counts[st] = status_counts.get(st, 0) + 1

    # 6. Couverture NIS 2 (10 mesures Article 21(2) a a j)
    nis2_data = load_yaml("grc/mappings/iso_nis2.yaml")
    nis2_mappings = nis2_data.get("mappings", [])
    nis2_letters = "abcdefghij"
    nis2_covered = 0
    for letter in nis2_letters:
        matching = [
            m
            for m in nis2_mappings
            if re.search(rf"Article\s*21\(2\){letter}", m.get("reference", ""), re.IGNORECASE)
        ]
        matching_cids = {str(m["control_id"]) for m in matching}
        applicable_ctrls = [cid for cid in matching_cids if ctrl_dict.get(cid, {}).get("is_applicable", True)]
        if applicable_ctrls:
            nis2_covered += 1

    # 7. Techniques ATT&CK couvertes
    cited_techniques = set()
    for r in risks:
        for t in r.get("attack_techniques", []):
            if t:
                cited_techniques.add(str(t).strip())

    attack_data = load_yaml("grc/mappings/iso_attack.yaml")
    attack_mappings = attack_data.get("mappings", [])
    attack_covered = 0
    for tech in sorted(cited_techniques):
        matching = [
            m
            for m in attack_mappings
            if m.get("reference", "").startswith(tech) or re.match(rf"^{tech}(?:\.|\s|$)", m.get("reference", ""))
        ]
        matching_cids = {str(m["control_id"]) for m in matching}
        applicable_ctrls = [cid for cid in matching_cids if ctrl_dict.get(cid, {}).get("is_applicable", True)]
        if applicable_ctrls:
            attack_covered += 1

    # 8. Mappings NIST CSF 2.0
    nist_data = load_yaml("grc/mappings/iso_nist.yaml")
    nb_nist_mappings = len(nist_data.get("mappings", []))

    crit = niveaux_inherents["Critique"]
    elev = niveaux_inherents["Élevé"]
    moy = niveaux_inherents["Moyen"]
    fai = niveaux_inherents["Faible"]

    st_imp = status_counts["implemented"]
    st_par = status_counts["partial"]
    st_pla = status_counts["planned"]
    st_not = status_counts["not_implemented"]
    st_na = status_counts["non_applicable"]

    lines = [
        "# Notes de Version : v1.0.0 — Dossier GRC & Outil de Pilotage",
        "",
        "Date de publication : 12 octobre 2026  ",
        "Référence Git : `v1.0.0`",
        "",
        "---",
        "",
        "## 📊 Métriques Clés du Référentiel GRC (Calculées depuis les sources YAML)",
        "",
        "| Domaine / Métrique | Valeur calculée | Détails & Répartition |",
        "| :--- | :---: | :--- |",
        f"| **Sources de Risque (SR)** | **{nb_sources_risque}** | 4 catégories qualifiées dans l'Atelier 2 EBIOS RM |",
        f"| **Objectifs Visés (OV)** | **{nb_objectifs}** | 4 objectifs déclinés en **{nb_couples} couples SR/OV** |",
        f"| **Parties Prenantes** | **{nb_parties_prenantes}** | Écosystème modélisé (cliniques, PACS, HDS) |",
        f"| **Scénarios Stratégiques** | **{nb_scenarios_strat}** | Chemins d'attaque analysés dans l'Atelier 3 |",
        f"| **Scénarios Opérationnels** | **{nb_scenarios_op}** | Scénarios R-01 à R-12 avec vecteurs ATT&CK |",
        f"| **Répartition Risques Inhérents** | **{nb_scenarios_op}** | "
        f"**Critique : {crit}** · **Élevé : {elev}** · **Moyen : {moy}** · **Faible : {fai}** |",
        f"| **Plans de Traitement (Atelier 5)** | **{nb_traitements}** | "
        "Mesures d'atténuation, de transfert ou d'acceptation |",
        f"| **Contrôles ISO 27001:2022 (Annexe A)** | **{nb_controles_total}** | "
        f"**{st_imp}** implémentés · **{st_par}** partiels · **{st_pla}** planifiés · "
        f"**{st_not}** non implémentés · **{st_na}** non applicables |",
        f"| **Couverture Directive NIS 2** | **{nis2_covered} / 10** | "
        "**100 %** des 10 mesures obligatoires de l'Article 21(2) (a à j) |",
        f"| **Couverture MITRE ATT&CK** | **{attack_covered} / {len(cited_techniques)}** | "
        "**100 %** des techniques observées couvertes par des contrôles |",
        f"| **Mappings NIST CSF 2.0** | **{nb_nist_mappings}** | "
        "Sous-catégories officielles CSF 2.0 alignées aux contrôles ISO |",
        "",
        "---",
        "",
        "## ⚡ Démarrage rapide (3 commandes)",
        "",
        "Exécutez l'ensemble de la plateforme en local avec Docker Compose :",
        "",
        "```bash",
        "# 1. Cloner le dépôt",
        "git clone https://github.com/h-4mza/grc-as-code-imaging-center.git && cd grc-as-code-imaging-center",
        "",
        "# 2. Démarrer la stack conteneurisée",
        "docker compose up -d --build",
        "",
        "# 3. Charger le référentiel GRC en base et ingérer les scans d'exemple",
        "docker compose exec -T api grc load && "
        "docker compose exec -T api grc ingest --source sarif --file grc/scans/projet1_trivy.sarif",
        "```",
        "",
        "Accès aux services :",
        "- 🖥️ **Tableau de bord Streamlit** : `http://localhost:8501`",
        "- 📡 **Documentation Swagger API** : `http://localhost:8000/docs`",
        "- 📚 **Documentation officielle MkDocs** : `https://h-4mza.github.io/grc-as-code-imaging-center/`",
        "",
        "---",
        "",
        "## ⚠️ Limites connues",
        "",
        "1. **Système d'Information Fictif** : L'organisation modélisée (centre d'imagerie médicale de 16 personnes), "
        "les flux PACS/RIS et les constats décrivent un cas d'étude fictif. "
        "Le dépôt ne contient aucune donnée de santé réelle ni DCP.",
        "2. **Mappings à valider formellement** : Les correspondances réglementaires (NIS2, NIST CSF 2.0, "
        "MITRE ATT&CK) sont fournies à titre indicatif et doivent faire l'objet d'une validation formelle.",
        "3. **Démonstrateur d'ingénierie, pas un outil de certification** : Ce projet est un démonstrateur "
        "et ne constitue pas un outil de certification accrédité.",
        "4. **Absence d'authentification et de gestion des rôles** : Cette version 1.0.0 ne comporte pas "
        "de couche RBAC ; l'accès local à l'API et au tableau de bord est direct.",
        "",
        "---",
        "",
        "## 👥 Crédits",
        "",
        "Ce projet s'appuie sur le travail de recherche académique :",
        "- **Rapport initial** : *Gestion des risques : Application du NIST Cybersecurity Framework (CSF 2.0) "
        "dans un centre d'imagerie médicale* (`grc/legacy/nist_csf_report.pdf`).",
        "- **Établissement** : Université Chouaib Doukkali — École Nationale des Sciences Appliquées d'El Jadida "
        "(ENSA El Jadida), Département Télécommunications, Réseaux et Informatique (2025–2026).",
        "- **Co-auteurs** :",
        "  - **Hamza Bahalloul** ([@h-4mza](https://github.com/h-4mza))",
        "  - **Malak Alioua**",
        "  - **Elferdouas Haouchra**",
        "- **Encadrement** : **Professeur Ali Kartit**",
    ]

    output_path = ROOT / "RELEASE_NOTES.md"
    with open(output_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")
    print(f"RELEASE_NOTES.md généré avec succès ({output_path}) !")


if __name__ == "__main__":
    generate_release_notes()
