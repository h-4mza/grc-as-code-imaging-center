# 🛡️ GRC-as-Code : Plateforme de Pilotage Cybersécurité & Conformité

> **Passez de la conformité statique sur tableurs à une gouvernance de sécurité continue, versionnée et pilotée par les données.**  
> Une solution DevSecOps appliquée au secteur de la santé (Centre d'Imagerie Médicale) pour automatiser la méthode **EBIOS RM**, piloter les **93 contrôles ISO 27001:2022**, et réévaluer dynamiquement les risques résiduels via l'ingestion de scans de vulnérabilités (**SARIF**).

---

<!-- Badge CI GitHub Actions & Stack -->
[![CI Pipeline](https://github.com/h-4mza/grc-as-code-imaging-center/actions/workflows/ci.yml/badge.svg)](https://github.com/h-4mza/grc-as-code-imaging-center/actions)
[![Python Version](https://img.shields.io/badge/python-3.11-blue.svg?logo=python)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-009688.svg?logo=fastapi)](https://fastapi.tiangolo.com)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.28+-FF4B4B.svg?logo=streamlit)](https://streamlit.io)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15-336791.svg?logo=postgresql)](https://www.postgresql.org/)
[![Docker Compose](https://img.shields.io/badge/Docker-compose-2496ED.svg?logo=docker)](https://www.docker.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

---

## 🏗️ Architecture du Système

Le système implémente le paradigme **GRC-as-Code** : les référentiels de sécurité, les ateliers de risques et les contrôles sont décrits sous forme déclarative (YAML), versionnés sous Git, validés automatiquement et consommés par des microservices conteneurisés.

```mermaid
flowchart TD
    subgraph Git ["1. Déclaratif GRC-as-Code (Git)"]
        EBIOS["Ateliers EBIOS RM (1 à 5)<br>grc/ebios/*.yaml"]
        ISO["Annexe A ISO 27001:2022<br>grc/iso27001/annex_a.yaml"]
        MAP["Mappings Réglementaires<br>NIS2, NIST CSF, ATT&CK"]
    end

    subgraph SecOps ["2. Ingestion & Télémétrie Sécurité"]
        SARIF["Rapports SARIF<br>(Scans Trivy CVE, BloodHound AD)"]
        CLI["CLI Typer DevSecOps<br>'grc load' & 'grc ingest'"]
    end

    subgraph Core ["3. Backend & Persistance"]
        DB[("PostgreSQL 15<br>Modèle Relationnel & Graphe")]
        API["FastAPI Engine<br>Calculs Inhérent/Résiduel & Moteur API"]
    end

    subgraph Front ["4. Visualisation & Restitution"]
        DASH["Dashboard Streamlit<br>Heatmap dynamique, SoA d'Audit, KPIs"]
    end

    subgraph Ext ["5. Intégrations Externes"]
        JIRA["Jira Service Management<br>Synchronisation des traitements"]
    end

    Git -->|Parsé à l'init| CLI
    SARIF -->|Ingéré en continu| CLI
    CLI -->|Persiste & Lie| DB
    DB <-->|Relations & Métriques| API
    API <-->|Consommation REST / JSON| DASH
    API -.->|Export tickets| JIRA
```

---

## 📊 Chiffres Clés du Dossier

| Indicateur | Volume | Description & Impact Métier |
| :--- | :---: | :--- |
| **Scénarios de Risque EBIOS RM** | **10** | Modélisation des 5 ateliers : du ransomware PACS à la compromission supply-chain, avec scoring inhérent vs résiduel. |
| **Contrôles ISO 27001:2022 Évalués** | **93** | SoA complète (Thèmes 5 à 8) avec justifications médicales (PACS, VPN, HDS) et exclusion formelle du dev logiciel. |
| **Mappings Réglementaires Croisés** | **3** | Correspondance directe des contrôles avec **NIS2** (Art. 21), **NIST CSF 2.0** et **MITRE ATT&CK v14**. |
| **Sources de Télémétrie SecOps** | **2** | Ingestion native de rapports de scans **SARIF** (Trivy & Bloodhound) dégradant dynamiquement le risque résiduel. |
| **Plans de Traitement Opérationnels** | **10** | Décisions formelles (Réduire, Transférer, Accepter) avec échéances, porteurs et passerelle Jira. |

---

## ⚡ Démarrage Rapide (Quickstart)

Déployez l'ensemble de la stack (Base de données PostgreSQL, API FastAPI et Dashboard Streamlit) en quelques commandes grâce à Docker Compose.

### 1. Cloner le dépôt
```bash
git clone https://github.com/h-4mza/grc-as-code-imaging-center.git
cd grc-as-code-imaging-center
```

### 2. Démarrer les conteneurs
```bash
docker-compose up -d --build
```

### 3. Initialiser les données GRC & Ingestion des scans
Exécutez les commandes du CLI au sein du conteneur API pour charger le référentiel YAML et ingérer les constats techniques :

```bash
# Chargement du référentiel (EBIOS RM, ISO 27001, Mappings)
docker-compose exec -e DATABASE_URL="postgresql+psycopg2://grc_user:grc_password@postgres/grc_db" api python -m app.cli load

# Ingestion des constats techniques SecOps (Rapports SARIF)
docker-compose exec -e DATABASE_URL="postgresql+psycopg2://grc_user:grc_password@postgres/grc_db" api python -m app.cli ingest --source sarif --file grc/scans/projet1_trivy.sarif
docker-compose exec -e DATABASE_URL="postgresql+psycopg2://grc_user:grc_password@postgres/grc_db" api python -m app.cli ingest --source sarif --file grc/scans/projet3_ad_audit.sarif
```

### 4. Accéder aux applications
* 🖥️ **Dashboard CISO / Auditeur (Streamlit)** : [http://localhost:8501](http://localhost:8501)
* 📡 **API REST & Documentation interactive (Swagger)** : [http://localhost:8000/docs](http://localhost:8000/docs)

---

## 📸 Aperçu & Livrables

### Tableau de Bord Interactif (Heatmap & Pilotage CISO)
<!-- Insérer ici le GIF animé illustrant la navigation dans le dashboard, le passage inhérent/résiduel et la matrice croisée -->
![Aperçu interactif du Dashboard Streamlit - Heatmap et KPIs GRC](docs/images/dashboard_demo.gif)

### Déclaration d'Applicabilité (SoA) ISO 27001:2022
<!-- Insérer ici la capture d'écran du rapport SoA mis en forme avec ses statuts, maturités et justifications contextualisées -->
![Déclaration d'Applicabilité (SoA) ISO 27001:2022 générée pour audit](docs/images/soa_matrix_preview.png)

---

## 📁 Structure du Projet

```text
├── app/
│   ├── main.py              # Endpoints FastAPI (/kpi/heatmap, /kpi/compliance, /kpi/soa)
│   ├── cli.py               # Interface CLI Typer (commandes load & ingest)
│   ├── models.py            # Modèles SQLAlchemy relationnels
│   ├── parsers/sarif.py     # Parseur de rapports de scan SARIF
│   └── services/scoring.py  # Algorithme de calcul de risques EBIOS RM
├── dashboard/
│   └── streamlit_app.py     # Interface utilisateur Streamlit
├── docs/
│   ├── compliance/          # Note d'applicabilité réglementaire (NIS2, RGPD, HDS)
│   └── images/              # Captures et GIF pour la documentation
├── grc/
│   ├── ebios/               # Ateliers EBIOS RM au format YAML
│   ├── iso27001/            # 93 contrôles ISO 27001:2022 évalués
│   ├── mappings/            # Mappings formels (NIS2, NIST CSF, ATT&CK)
│   └── scans/               # Rapports SARIF d'exemple (Trivy, BloodHound)
├── docker-compose.yml       # Déploiement multi-conteneurs
└── Dockerfile               # Définition de l'image de l'API
```

---

## 📜 Licence
Ce projet est distribué sous licence MIT. Consultez le fichier [LICENSE](LICENSE) pour plus d'informations.
