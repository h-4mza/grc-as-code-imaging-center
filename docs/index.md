# Plateforme GRC-as-Code — Centre d'Imagerie Médicale

> [!WARNING]
> **Avertissement méthodologique :**  
> Ce projet modélise le système d'information fictif d'un centre d'imagerie médicale dans un cadre pédagogique d'exercice. Les analyses de risques, politiques de sécurité, déclarations d'applicabilité et preuves documentaires constituent des artefacts méthodologiques illustratifs et ne reflètent pas des opérations médicales réelles ni un conseil juridique opposable.

Bienvenue sur la documentation officielle du projet **GRC-as-Code**, une approche moderne traitant la Gouvernance, la Gestion des Risques et la Conformité réglementaire avec les mêmes standards d'ingénierie que le code source logiciel : déclaratif, versionné sous Git, audité par des tests automatisés et validé en intégration continue (CI).

---

## 🏥 Périmètre de l'Organisation Modélisée

Le système d'information modélisé est celui d'un **Centre d'Imagerie Médicale (CIM)** structuré comme suit :
* **Effectif :** 16 collaborateurs (médecins radiologues, manipulateurs d'électroradiologie médicale, secrétaires médicales, référents informatiques et biomédicaux) ;
* **Plateau technique :** Modalités d'acquisition d'imagerie lourde (IRM, Scanner multi-barrettes, Mammographe numérique, Échographes) ;
* **Cœur applicatif :** Serveurs PACS (*Picture Archiving and Communication System*), RIS (*Radiology Information System*), Dossier Patient Informatisé (DPI) ;
* **Interconnexions réseau :** Passerelle de télémaintenance biomédicale sécurisée, liaisons de téléradiologie 24/7 pour les urgences nocturnes avec des cliniques partenaires locales et européennes, et réplication vers un hébergeur cloud souverain certifié HDS.

---

## 📊 Le Projet en Chiffres Réels (Sources YAML)

L'intégralité du corpus d'analyse est formalisée sous forme de fichiers déclaratifs YAML dans le dossier `grc/`. Les chiffres réels issus de ces référentiels sont les suivants :

| Composant | Fichier source | Métrique réelle | Description |
|:---|:---|:---:|:---|
| **Valeurs Métier** | `grc/si/business_values.yaml` | **7** | Processus vitaux (accueil, acquisition, interprétation, téléradiologie, archivage, facturation, confidentialité) |
| **Actifs de Soutien** | `grc/si/assets.yaml` | **9** | Actifs matériels et applicatifs (serveurs PACS/RIS, modalités IRM/Scanner, réseau LAN, postes de lecture) |
| **Sources de Risque & Objectifs** | `grc/ebios/w2_sources.yaml` | **4 SR / 4 OV** | 4 sources de risque, 4 objectifs visés, déclinés en **6 couples SR/OV** pertinents |
| **Écosystème & Scénarios Stratégiques** | `grc/ebios/w3_strategiques.yaml` | **5 PP / 9 Scénarios** | 5 parties prenantes modélisées et 9 scénarios stratégiques d'attaque de l'écosystème |
| **Scénarios Opérationnels EBIOS RM** | `grc/ebios/w4_operationnels.yaml` | **12 risques** | Scénarios **R-01 à R-12** cotés en Gravité ($G$) et Vraisemblance ($V$) sur une échelle stricte $1–4$ |
| **Plans de Traitement des Risques** | `grc/ebios/w5_traitements.yaml` | **13 traitements** | Mesures d'atténuation, de transfert ou d'acceptation couvrant l'intégralité des 12 risques |
| **Contrôles ISO 27001:2022 (Annexe A)** | `grc/iso27001/annex_a.yaml` | **93 contrôles** | **84 applicables** et **9 non applicables** (développement logiciel), tous justifiés individuellement |
| **Couverture Directive NIS 2** | `grc/mappings/iso_nis2.yaml` | **10 / 10 mesures** | **40 mappings** couvrant 100% des exigences de l'Article 21(2) a à j |
| **Mitigations MITRE ATT&CK** | `grc/mappings/iso_attack.yaml` | **61 mappings** | Mesures préventives et détectives associées aux techniques d'attaque observées |
| **Sous-catégories NIST CSF 2.0** | `grc/mappings/iso_nist.yaml` | **27 mappings** | Alignement officiel sur les fonctions Gouvernance, Identification, Protection, Détection et Réponse |

---

## ⚠️ Limites et Hypothèses d'Étude

La démarche adoptée dans ce référentiel respecte des frontières méthodologiques explicites :
1. **Caractère fictif et académique :** Le système d'information décrit ne contient aucune donnée à caractère personnel réelle. Les noms d'éditeurs et de partenaires sont génériques.
2. **Exclusion du développement logiciel interne :** En raison de la taille de l'équipe (16 personnes) et de son modèle d'exploitation basé sur des progiciels fermés du commerce, les 9 contrôles de l'Annexe A relatifs au cycle de vie logiciel (8.4, 8.25 à 8.31, 8.33) sont déclarés non applicables avec justification argumentée.
3. **Périmètre d'exécution technique :** Cette documentation en ligne sur GitHub Pages présente les éléments statiques et les rapports générés. Le moteur dynamique de calcul (API FastAPI), la base relationnelle PostgreSQL et l'interface de visualisation Streamlit s'exécutent en environnement conteneurisé local via Docker. Une visite illustrée des interfaces interactives est disponible dans la section [Aperçu du Dashboard](outil/apercu.md).

---

## 🗺️ Organisation de la Documentation

La documentation s'organise selon les piliers de la méthode :

* **[EBIOS RM](ebios/atelier1.md) :** Les 5 ateliers méthodologiques de l'ANSSI menés sur le cas du centre (cadrage, événements redoutés, scénarios stratégiques, scénarios opérationnels ATT&CK / NIST, stratégie de traitement).
* **[ISO 27001 (SoA)](iso27001/soa.md) :** Déclaration d'Applicabilité complète des 93 contrôles classés par clauses (Organisationnel, Personnes, Physique, Technologique) avec compteurs par statut.
* **[Conformité Réglementaire](compliance/applicabilite_reglementaire.md) :** Analyse d'applicabilité transfrontalière (Directive NIS 2, RGPD, Loi marocaine 09-08 / CNDP, Loi 05-20 / DGSSI, référentiel HDS).
* **[Matrice de Contrôles](compliance/matrice_controles.md) :** Matrice croisée reliant les contrôles ISO 27001 aux cadres NIS 2, NIST CSF 2.0 et MITRE ATT&CK.
* **[Outil & Dashboard](outil/scoring.md) :** Algorithmes mathématiques de cotation unifiée (`app/services/scoring.py`) et [captures d'écran du tableau de bord Streamlit](outil/apercu.md).
