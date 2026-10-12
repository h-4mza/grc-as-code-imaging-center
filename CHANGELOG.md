# Changelog

Toutes les modifications notables apportées à ce projet seront documentées dans ce fichier.

Le format est basé sur [Keep a Changelog](https://keepachangelog.com/fr/1.0.0/),
et ce projet adhère à [Semantic Versioning](https://semver.org/lang/fr/).

## [1.0.0] - 2026-10-12

### Ajouté

#### EBIOS RM (Ateliers 1 à 5)
- **Atelier 1 (Périmètre & Actifs)** : Modélisation formelle de 7 valeurs métier et 9 actifs de soutien (`grc/si/`) pour un centre d'imagerie médicale fictif (PACS, RIS, modalité IRM/Scanner, réseau interne, passerelle de télémaintenance).
- **Atelier 2 (Sources de Risque & Objectifs Visés)** : Identification de 4 sources de risque et 4 objectifs visés déclinés en 6 couples SR/OV pertinents (`grc/ebios/w2_sources.yaml`).
- **Atelier 3 (Écosystème & Scénarios Stratégiques)** : Cartographie de 5 parties prenantes clés et formalisation de 9 scénarios stratégiques d'attaque par rebond (`grc/ebios/w3_strategiques.yaml`).
- **Atelier 4 (Scénarios Opérationnels)** : 12 scénarios de risque opérationnels (R-01 à R-12) cotés sur une échelle stricte 1–4 ($G \times V$), associés à des techniques d'attaque MITRE ATT&CK (`grc/ebios/w4_operationnels.yaml`).
- **Atelier 5 (Traitements des Risques)** : 13 plans d'action de traitement avec responsable, échéance, option ISO 27005 (réduire, transférer, accepter) et projection du risque cible (`grc/ebios/w5_traitements.yaml`).

#### SoA ISO 27001:2022
- Évaluation exhaustive des **93 contrôles de l'Annexe A** (`grc/iso27001/annex_a.yaml`) : 84 contrôles applicables et 9 non applicables (développement logiciel interne exclu avec motif argumenté).
- Justifications contextualisées pour le secteur de la santé (PACS, VPN, passerelle télémaintenance biomédicale, réplication HDS) et statuts d'implémentation opérationnels.
- Références d'artefacts documentaires et preuves types (`evidence`).
- Génération automatisée de la Déclaration d'Applicabilité dans la documentation (`docs/iso27001/soa.md`).

#### Mappings Réglementaires & Techniques
- **Directive NIS 2 (Article 21(2))** : Couverture des 10 mesures obligatoires (a à j) par 40 mappings de contrôles ISO 27001 (`grc/mappings/iso_nis2.yaml`).
- **NIST CSF 2.0** : Correspondance officielle entre les contrôles ISO 27001 et 27 sous-catégories NIST CSF 2.0 (`grc/mappings/iso_nist.yaml`).
- **MITRE ATT&CK v14** : Cartographie de 61 correspondances techniques associant mitigations ATT&CK (M10xx) et contrôles préventifs/détectifs (`grc/mappings/iso_attack.yaml`).
- **Matrice de Contrôles Croisée** : Commande `grc export-matrix` générant la table croisée de synthèse (`docs/compliance/matrice_controles.md`).

#### API REST (FastAPI)
- Endpoints de consultation des risques (`GET /risks`, `GET /risks/{id}`) et des contrôles (`GET /controls`).
- Ingestion des constats de sécurité techniques (`POST /findings`, `GET /findings`).
- Indicateurs clés et reporting : `/kpi/overview`, `/kpi/heatmap`, `/kpi/soa`, `/kpi/compliance`, `/kpi/coverage`.
- Calcul centralisé du risque résiduel (`app/services/scoring.py`) tenant compte de la maturité des contrôles ISO et de la sévérité des constats ouverts.
- Optimisation des performances avec chargement anticipé SQLAlchemy (`selectinload`) éliminant les requêtes N+1.

#### CLI & SecOps (`grc`)
- Commande `grc validate` vérifiant l'intégrité référentielle, les formats d'identifiants et la complétude des mappings sans toucher à la base.
- Commande `grc load` idempotente avec transaction unique, upsert des entités déclaratives, élagage (prune) et préservation stricte des constats et clés Jira.
- Commande `grc reset --yes` permettant la réinitialisation contrôlée de la base PostgreSQL.
- Commande `grc ingest` supportant les formats de scan SARIF (Trivy, BloodHound).
- Commande `grc export-jira` avec synchronisation vers Atlassian Jira Cloud (API v3, format ADF, labels `risk-*` et `control-*`, simulation dry-run par défaut).

#### Dashboard (Streamlit)
- Tableau de bord décisionnel multi-pages :
  - Vue d'ensemble des métriques de gouvernance ;
  - Matrice de risques Heatmap 4×4 dynamique (inhérent vs résiduel vs cible) ;
  - Suivi de la Déclaration d'Applicabilité ISO 27001 par clause ;
  - Couverture réglementaire NIS2, NIST CSF et MITRE ATT&CK ;
  - Suivi d'avancement des plans de traitement des risques.

#### CI/CD, Documentation & Packaging
- Pipeline d'intégration continue GitHub Actions (`.github/workflows/ci.yml`) validant `ruff`, `pytest`, `grc validate` et le build MkDocs.
- Déploiement automatique de la documentation sur GitHub Pages via GitHub Actions (`.github/workflows/docs.yml`).
- Site de documentation interactif sous thème Material for MkDocs avec bascule clair/sombre.
- Politique de sécurité ([`SECURITY.md`](SECURITY.md)), fichier d'environnement modèle ([`.env.example`](.env.example)), et intégration Docker Compose.
