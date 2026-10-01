Projet GRC-as-code : architecture globale et plan d'exécution
1. Objectif et livrables

Le projet livre trois choses, qui doivent rester cohérentes entre elles :

Un dossier GRC sur le centre d'imagerie médicale : 5 ateliers EBIOS RM, SoA ISO 27001:2022 (93 contrôles), plan de traitement (logique ISO 27005), cartographie NIS2/RGPD/HDS.
Un outil de pilotage (FastAPI, Postgres, Streamlit) qui charge ce dossier, y rattache les constats techniques de vos projets 1 et 3, calcule les scores et exporte vers Jira.
Un repo GitHub vitrine : README, CI, documentation en ligne, release.
2. Architecture globale
 SOURCES (as-code, versionnées dans Git)                ENTRÉES TECHNIQUES
 ┌───────────────────────────────────┐             ┌──────────────────────────┐
 │ grc/si/        actifs, valeurs    │             │ Projet 1 (scans, pentest)│
 │ grc/ebios/     ateliers 1→5       │             │ Projet 3 (détection/logs)│
 │ grc/iso27001/  annex_a (93)       │             │ → SARIF / JSON / Nmap XML│
 │ grc/mappings/  NIS2, ATT&CK, NIST │             └────────────┬─────────────┘
 │ grc/rgpd/      art.30, AIPD       │                          │ grc ingest
 └─────────────────┬─────────────────┘                          │
                   │ grc validate  →  grc load                  │
                   ▼                                            ▼
        ┌───────────────────────────────────────────────────────────┐
        │                    PostgreSQL (Alembic)                   │
        └───────────────────────────┬───────────────────────────────┘
                                    │
        ┌───────────────────────────▼───────────────────────────────┐
        │ FastAPI                                                   │
        │  routers : risks · controls · findings · kpi · jira       │
        │  services: scoring · mapping · ingest · jira_client       │
        └──────┬──────────────────────┬─────────────────────┬───────┘
               ▼                      ▼                     ▼
        Streamlit (dashboard)   Jira Cloud (tickets)   Exports CSV (Power BI)

 CI GitHub Actions : ruff → pytest → validation YAML → build MkDocs → Pages

Principes de conception

Le YAML est la source de vérité. La base est reconstructible à tout moment (make reset && make load).
Aucun score ni niveau écrit à la main : tout vient de scoring.py.
Les liens sont explicites et vérifiés par la CI : risque → contrôles → mappings, constat → actif → contrôle → risque.
3. Structure du repo
grc-as-code/
├── README.md
├── LICENSE (MIT)
├── Makefile                  # demo, load, test, lint, docs
├── docker-compose.yml        # postgres + api + dashboard
├── pyproject.toml
├── .github/workflows/ci.yml
├── docs/                     # MkDocs Material
│   ├── index.md
│   ├── 00-contexte-si.md
│   ├── ebios/atelier1.md … atelier5.md
│   ├── iso27001/soa.md, plan-traitement.md
│   ├── nis2-rgpd/applicabilite.md, cartographie.md
│   └── outil/architecture.md, api.md, kpi.md
├── grc/
│   ├── si/ (assets.yaml, business_values.yaml)
│   ├── ebios/ (w1…w5)
│   ├── iso27001/annex_a.yaml
│   ├── mappings/ (iso_nis2.yaml, iso_attack.yaml, iso_nist.yaml)
│   ├── rgpd/ (art30.yaml, aipd.yaml)
│   └── legacy/nist_csf_report.pdf     # le rapport d'origine, avec crédits
├── app/
│   ├── main.py, config.py, db.py
│   ├── models.py, schemas.py
│   ├── routers/
│   ├── services/ (scoring.py, mapping.py, ingest.py, jira_client.py)
│   ├── parsers/ (sarif.py, nmap.py, generic_json.py)
│   └── cli.py                # Typer : validate | load | ingest | export-jira
├── dashboard/streamlit_app.py
├── migrations/               # Alembic
├── samples/findings/         # constats de démo (anonymisés)
└── tests/
4. Modèle de données
Table	Contenu clé
business_value	id, nom, processus, événement redouté, gravité
asset	id, nom, type, criticité, valeurs métier liées
risk_source, objective	couples SR/OV, pertinence
stakeholder	partie prenante de l'écosystème, niveau de menace (atelier 3)
strategic_scenario, operational_scenario	chemin d'attaque, techniques ATT&CK, vraisemblance
risk	gravité, vraisemblance, niveau inhérent et résiduel, propriétaire, statut
control	id ISO, thème, applicable, justification, état, maturité 0-5, preuve
control_mapping	control_id, framework (NIS2, ATT&CK, NIST), référence
treatment	option, échéance, responsable, jira_key
finding	source (projet 1 ou 3), sévérité, actif, CVE, technique ATT&CK, date
finding_control, finding_risk	liens constat → contrôle défaillant, constat → risque
regulation_scope	NIS2 / RGPD / HDS : applicable ou non, justification

Logique de scoring (à documenter dans docs/outil/kpi.md) :

Niveau = gravité (1-4) × vraisemblance (1-4), avec des seuils fixes (1-3 Faible, 4-6 Moyen, 8-9 Élevé, 12-16 Critique).
La vraisemblance augmente d'un cran (plafonnée à 4) si un constat ouvert de sévérité haute touche un actif du risque.
Le résiduel dépend de la maturité moyenne des contrôles liés au risque.
Tests unitaires sur chaque seuil et chaque règle.
5. API et CLI

Endpoints

GET /risks, GET /risks/{id} (contrôles, constats, traitements liés)
GET /controls, PATCH /controls/{id}
POST /findings, GET /findings
GET /kpi/overview, /kpi/heatmap, /kpi/soa, /kpi/nis2
POST /jira/export?dry_run=true

CLI

grc validate : schémas, références croisées, cohérence des niveaux
grc load : charge le YAML en base
grc ingest --source projet1 --file scan.sarif
grc export-jira --dry-run

Jira : API REST v3, authentification par e-mail + token API, un ticket par traitement, labels risk-id et control-id, priorité dérivée du niveau, idempotence via jira_key.

6. Dashboard (Streamlit)

Cinq pages :

Vue d'ensemble : nombre de risques par niveau, contrôles implémentés, constats ouverts.
Heatmap 4×4 des risques, inhérent vs résiduel.
SoA : statut des 93 contrôles par thème (organisationnel 37, personnes 8, physique 14, technologique 34).
Conformité : mesures de l'article 21 NIS2, couverture ATT&CK, registre RGPD.
Plan de traitement : avancement, retards, tickets Jira.
7. Plan en 3 semaines

Chaque tâche a un livrable vérifiable.

Semaine 1 : fondations et contenu
Jour	Tâches	Livrable
1	Créer le repo, docker-compose, Postgres, squelette FastAPI, pyproject, pre-commit	make demo démarre une API vide
2	Convertir les 12 actifs et les valeurs métier du PDF en YAML, écrire les schémas Pydantic, A1	assets.yaml, atelier1.md
3	A2 : couples SR/OV (4 à 6)	w2_sources.yaml, atelier2.md
4	A3 : écosystème (cliniques, téléradiologie, éditeur PACS, hébergeur HDS, mainteneurs)	w3_strategiques.yaml, atelier3.md
5	Début d'A4 : 10 à 12 scénarios opérationnels avec séquences ATT&CK	w4_operationnels.yaml (brouillon)
6-7	SoA, passe 1 : thèmes 5 (organisationnel) et 8 (technologique)	annex_a.yaml 60 % complété
Semaine 2 : outil et intégration
Jour	Tâches	Livrable
8	Modèles SQLAlchemy, Alembic, grc validate et grc load	Base chargée depuis le YAML
9	scoring.py + tests, endpoints risks et controls	Niveaux calculés, tests verts
10	Parsers et grc ingest, rattachement constat → actif → contrôle → risque	Constats de démo ingérés
11	Mappings NIS2 / ATT&CK / NIST, SoA complète (93 contrôles, thèmes 6 et 7 inclus)	annex_a.yaml 100 %
12	A5 : traitements, risques résiduels, suivi ; export Jira en dry-run, puis réel	Tickets de test créés
13-14	Dashboard Streamlit (5 pages), endpoints /kpi	Dashboard fonctionnel avec données seedées
Semaine 3 : conformité, documentation, publication
Jour	Tâches	Livrable
15	Applicabilité NIS2/HDS/RGPD du centre, registre art. 30, AIPD simplifiée	nis2-rgpd/*.md, rgpd/*.yaml
16	CI complète (ruff, pytest, validate, build docs), badges	Pipeline vert
17	MkDocs Material, publication sur GitHub Pages	Site en ligne
18	Captures du dashboard, GIF de démo, README final	README abouti
19	Relecture croisée : chaque chiffre du CV et du README est tiré de la base, section « Limites »	Cohérence validée
20-21	Marge, release v1.0.0, post LinkedIn, mise à jour du CV	Release publiée
8. Règles de cohérence vérifiées par la CI
Chaque risque a un propriétaire, un traitement et au moins un contrôle existant dans annex_a.yaml.
Chaque contrôle applicable: true a une justification et un état ; chaque contrôle non applicable a une justification d'exclusion.
Chaque scénario opérationnel référence au moins un actif et une technique ATT&CK valide.
Le niveau de chaque risque correspond au calcul de scoring.py.
Aucun lien cassé dans la documentation.
9. Définition de « terminé »
 5 ateliers EBIOS RM rédigés, avec 10 à 12 scénarios de risque
 93 contrôles évalués dans la SoA, chacun avec statut et justification
 Matrice contrôles ↔ NIS2 ↔ ATT&CK ↔ NIST générée
 Applicabilité NIS2, RGPD et HDS argumentée
 Constats des projets 1 et 3 visibles dans le registre et impactant les scores
 Export Jira fonctionnel (démo avec captures)
 make demo lance tout en une commande
 CI verte, documentation en ligne, release v1.0.0
 README avec schéma, captures, crédits des co-auteurs du rapport d'origine, section « Limites »
10. Visibilité GitHub
Nom du repo : grc-as-code-imaging-center ou similaire, description claire, topics grc, ebios-rm, iso27001, nis2, fastapi, risk-management.
Épingler le repo sur votre profil.
Commits en conventional commits, milestones « Semaine 1/2/3 », release avec notes.
Un docs/ lisible sans cloner, c'est ce qu'un recruteur ouvrira en premier.
11. Ligne de CV (à ajuster avec les vrais chiffres)

Dossier GRC complet (EBIOS RM, ISO 27001/27005, NIS2/RGPD) sur SI fictif de santé + outil de pilotage (FastAPI, PostgreSQL, Streamlit, API Jira) : 11 scénarios de risque, 93 contrôles évalués, constats techniques intégrés au registre.

12. Points de vigilance
Ne pas viser l'exhaustivité : 10 à 12 scénarios bien argumentés valent mieux que 25 superficiels.
Contenu avant outil : si vous prenez du retard, sacrifiez le dashboard (une version simple suffit) mais pas la SoA ni l'EBIOS.
Mappings : vérifiez-les contre les sources officielles et documentez leurs limites.
Marge : les jours 20-21 sont volontairement libres, vous en aurez besoin.