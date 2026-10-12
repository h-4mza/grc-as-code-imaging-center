# Notes de Version : v1.0.0 — Dossier GRC & Outil de Pilotage

Date de publication : 12 octobre 2026  
Référence Git : `v1.0.0`

---

## 📊 Métriques Clés du Référentiel GRC (Calculées depuis les sources YAML)

| Domaine / Métrique | Valeur calculée | Détails & Répartition |
| :--- | :---: | :--- |
| **Sources de Risque (SR)** | **4** | 4 catégories qualifiées dans l'Atelier 2 EBIOS RM |
| **Objectifs Visés (OV)** | **4** | 4 objectifs déclinés en **6 couples SR/OV** |
| **Parties Prenantes** | **5** | Écosystème modélisé (cliniques, PACS, HDS) |
| **Scénarios Stratégiques** | **9** | Chemins d'attaque analysés dans l'Atelier 3 |
| **Scénarios Opérationnels** | **12** | Scénarios R-01 à R-12 avec vecteurs ATT&CK |
| **Répartition Risques Inhérents** | **12** | **Critique : 3** · **Élevé : 6** · **Moyen : 3** · **Faible : 0** |
| **Plans de Traitement (Atelier 5)** | **13** | Mesures d'atténuation, de transfert ou d'acceptation |
| **Contrôles ISO 27001:2022 (Annexe A)** | **93** | **44** implémentés · **38** partiels · **0** planifiés · **2** non implémentés · **9** non applicables |
| **Couverture Directive NIS 2** | **10 / 10** | **100 %** des 10 mesures obligatoires de l'Article 21(2) (a à j) |
| **Couverture MITRE ATT&CK** | **20 / 20** | **100 %** des techniques observées couvertes par des contrôles |
| **Mappings NIST CSF 2.0** | **27** | Sous-catégories officielles CSF 2.0 alignées aux contrôles ISO |

---

## ⚡ Démarrage rapide (3 commandes)

Exécutez l'ensemble de la plateforme en local avec Docker Compose :

```bash
# 1. Cloner le dépôt
git clone https://github.com/h-4mza/grc-as-code-imaging-center.git && cd grc-as-code-imaging-center

# 2. Démarrer la stack conteneurisée
docker compose up -d --build

# 3. Charger le référentiel GRC en base et ingérer les scans d'exemple
docker compose exec -T api grc load && docker compose exec -T api grc ingest --source sarif --file grc/scans/projet1_trivy.sarif
```

Accès aux services :
- 🖥️ **Tableau de bord Streamlit** : `http://localhost:8501`
- 📡 **Documentation Swagger API** : `http://localhost:8000/docs`
- 📚 **Documentation officielle MkDocs** : `https://h-4mza.github.io/grc-as-code-imaging-center/`

---

## ⚠️ Limites connues

1. **Système d'Information Fictif** : L'organisation modélisée (centre d'imagerie médicale de 16 personnes), les flux PACS/RIS et les constats décrivent un cas d'étude fictif. Le dépôt ne contient aucune donnée de santé réelle ni DCP.
2. **Mappings à valider formellement** : Les correspondances réglementaires (NIS2, NIST CSF 2.0, MITRE ATT&CK) sont fournies à titre indicatif et doivent faire l'objet d'une validation formelle.
3. **Démonstrateur d'ingénierie, pas un outil de certification** : Ce projet est un démonstrateur et ne constitue pas un outil de certification accrédité.
4. **Absence d'authentification et de gestion des rôles** : Cette version 1.0.0 ne comporte pas de couche RBAC ; l'accès local à l'API et au tableau de bord est direct.

---

## 👥 Crédits

Ce projet s'appuie sur le travail de recherche académique :
- **Rapport initial** : *Gestion des risques : Application du NIST Cybersecurity Framework (CSF 2.0) dans un centre d'imagerie médicale* (`grc/legacy/nist_csf_report.pdf`).
- **Établissement** : Université Chouaib Doukkali — École Nationale des Sciences Appliquées d'El Jadida (ENSA El Jadida), Département Télécommunications, Réseaux et Informatique (2025–2026).
- **Co-auteurs** :
  - **Hamza Bahalloul** ([@h-4mza](https://github.com/h-4mza))
  - **Malak Alioua**
  - **Elferdouas Haouchra**
- **Encadrement** : **Professeur Ali Kartit**
