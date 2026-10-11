<div align="center">

# 🛡️ GRC-as-Code

### Piloter la cybersécurité et la conformité comme on pilote du code

**EBIOS RM · ISO 27001:2022 · NIS2 · NIST CSF 2.0 · MITRE ATT&CK**
*Appliqué à un Centre d'Imagerie Médicale (cas fictif)*

[![CI](https://github.com/h-4mza/grc-as-code-imaging-center/actions/workflows/ci.yml/badge.svg)](https://github.com/h-4mza/grc-as-code-imaging-center/actions)
[![Python](https://img.shields.io/badge/python-3.11-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-009688?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?logo=streamlit&logoColor=white)](https://streamlit.io)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15-336791?logo=postgresql&logoColor=white)](https://www.postgresql.org/)
[![Docker](https://img.shields.io/badge/Docker-compose-2496ED?logo=docker&logoColor=white)](https://www.docker.com/)
[![License: MIT](https://img.shields.io/badge/license-MIT-yellow.svg)](LICENSE)

![Aperçu du dashboard](docs/images/dashboard_demo.gif)

</div>

---

## 💡 Le problème

Dans la plupart des organisations, la conformité vit dans des tableurs et des documents Word : ils deviennent obsolètes dès le lendemain de l'audit, personne ne sait qui a modifié quoi, et les résultats des scans de vulnérabilités n'ont aucun lien avec le registre des risques.

## ✅ L'approche

**GRC-as-Code** traite la gouvernance, les risques et la conformité comme du code :

| Principe | Concrètement |
| :-- | :-- |
| **Déclaratif** | Risques, contrôles et mappings sont des fichiers YAML dans `grc/` |
| **Versionné** | Chaque changement passe par Git : historique, revue, traçabilité d'audit |
| **Automatisé** | Les rapports (SoA, heatmap, KPIs) sont générés, jamais rédigés à la main |
| **Connecté** | Un scan SARIF ingéré réévalue automatiquement le risque résiduel |

## 📊 Le projet en chiffres

| **10** | **93** | **3** | **2** | **10** |
| :--: | :--: | :--: | :--: | :--: |
| scénarios EBIOS RM | contrôles ISO 27001 évalués | référentiels mappés | sources SARIF | plans de traitement |

---

## 📑 Sommaire

[Fonctionnalités](#-fonctionnalités) · [Architecture](#-architecture) · [Démarrage rapide](#-démarrage-rapide) · [CLI](#-cli) · [API](#-api) · [Structure](#-structure-du-projet) · [Feuille de route](#-feuille-de-route) · [Licence](#-licence)

---

## ✨ Fonctionnalités

### 🎯 Analyse de risques EBIOS RM
Les 5 ateliers sont modélisés : valeurs métier (base patients, PACS), événements redoutés, scénarios stratégiques et opérationnels, puis traitements. Chaque risque porte un score **inhérent** et un score **résiduel** (gravité × vraisemblance).

### 📋 Conformité ISO 27001:2022
Les 93 contrôles de l'Annexe A sont évalués dans une Déclaration d'Applicabilité (SoA) avec statut, maturité et justification contextualisée (PACS, VPN, HDS), y compris l'exclusion motivée du développement logiciel.

### 🔗 Mappings réglementaires croisés
Chaque contrôle est relié à **NIS2** (art. 21), **NIST CSF 2.0** et **MITRE ATT&CK v14**, ce qui permet de mesurer la couverture réglementaire d'un seul coup d'œil.

### 🔍 Télémétrie sécurité (SARIF)
Les rapports de scan (**Trivy** pour les CVE, **BloodHound** pour Active Directory) sont ingérés et reliés aux scénarios de risque : une vulnérabilité critique dégrade le risque résiduel.

### 🎫 Suivi des traitements
Les plans de traitement (réduire, transférer, accepter) ont un porteur, une échéance, et peuvent être exportés vers **Jira Service Management**.

### 📈 Dashboard CISO / auditeur
Cinq vues : vue d'ensemble, heatmap inhérent vs résiduel, avancement de la SoA, conformité globale (NIS2 / NIST / ATT&CK) et rapports exportables.

![SoA ISO 27001](docs/images/soa_matrix_preview.png)

---

## 🏗️ Architecture

```mermaid
flowchart LR
    subgraph Git["📁 Git : source de vérité"]
        EBIOS["EBIOS RM<br>grc/ebios/*.yaml"]
        ISO["ISO 27001<br>grc/iso27001/"]
        MAP["Mappings<br>NIS2 · NIST · ATT&CK"]
    end

    subgraph Ops["⚙️ SecOps"]
        SARIF["Rapports SARIF<br>Trivy · BloodHound"]
        CLI["CLI Typer<br>load · ingest · export-jira"]
    end

    subgraph Core["🧠 Backend"]
        DB[("PostgreSQL 15")]
        API["FastAPI<br>scoring inhérent / résiduel"]
    end

    DASH["📈 Dashboard<br>Streamlit"]
    JIRA["🎫 Jira"]

    Git --> CLI
    SARIF --> CLI
    CLI --> DB
    DB <--> API
    API --> DASH
    API -.-> JIRA
```

**Stack :** Python 3.11 · FastAPI · SQLAlchemy · PostgreSQL 15 · Typer · Streamlit · Docker Compose.

---

## ⚡ Démarrage rapide

**Prérequis :** Docker et Docker Compose (Make est optionnel).

```bash
git clone https://github.com/h-4mza/grc-as-code-imaging-center.git
cd grc-as-code-imaging-center
make demo
```

`make demo` construit les conteneurs, démarre la stack et charge le référentiel.

<details>
<summary><b>Sans Make (commandes manuelles)</b></summary>

```bash
docker-compose up -d --build

# Variable pratique pour les commandes suivantes
export DB="postgresql+psycopg2://grc_user:grc_password@postgres/grc_db"

# 1. Charger le référentiel (EBIOS RM, ISO 27001, mappings)
docker-compose exec -e DATABASE_URL=$DB api python -m app.cli load

# 2. Ingérer les scans SARIF d'exemple
docker-compose exec -e DATABASE_URL=$DB api python -m app.cli ingest --source sarif --file grc/scans/projet1_trivy.sarif
docker-compose exec -e DATABASE_URL=$DB api python -m app.cli ingest --source sarif --file grc/scans/projet3_ad_audit.sarif
```
</details>

| Service | URL |
| :-- | :-- |
| 🖥️ Dashboard | http://localhost:8501 |
| 📡 API (Swagger) | http://localhost:8000/docs |

> 🔐 Les identifiants de `docker-compose.yml` sont destinés à la démo locale. Ne les réutilisez jamais en production.

---

## 🧰 CLI

| Commande | Rôle |
| :-- | :-- |
| `grc load` | Charge les YAML (`grc/`) en base |
| `grc ingest --source sarif --file <fichier>` | Ingère un rapport de scan et réévalue le risque résiduel |
| `grc export-jira --project CIMSEC` | Synchronise les plans de traitement vers Jira |

Exécution dans le conteneur : `docker-compose exec api python -m app.cli <commande>`

## 📡 API

| Endpoint | Retourne |
| :-- | :-- |
| `GET /kpi/heatmap` | Matrice de risques inhérent / résiduel |
| `GET /kpi/compliance` | Couverture NIS2 / NIST CSF / ATT&CK |
| `GET /kpi/soa` | Avancement de la SoA par thème |

Documentation interactive complète sur `/docs`.

---

## 📁 Structure du projet

```text
├── app/
│   ├── main.py              # Endpoints FastAPI
│   ├── cli.py               # CLI Typer
│   ├── models.py            # Modèles SQLAlchemy
│   ├── parsers/sarif.py     # Parseur SARIF
│   └── services/scoring.py  # Calcul des risques EBIOS RM
├── dashboard/streamlit_app.py
├── grc/
│   ├── ebios/               # Ateliers EBIOS RM (YAML)
│   ├── iso27001/            # 93 contrôles Annexe A
│   ├── mappings/            # NIS2, NIST CSF, ATT&CK
│   └── scans/               # Rapports SARIF d'exemple
├── docs/                    # Documentation, note d'applicabilité (NIS2, RGPD, HDS)
├── tests/
├── docker-compose.yml
└── Dockerfile
```

---

## 🧪 Qualité

- Tests automatisés dans `tests/`
- Hooks `pre-commit` (voir `.pre-commit-config.yaml`)
- Pipeline CI GitHub Actions
- Documentation générée avec MkDocs (`mkdocs.yml`)

## 🗺️ Feuille de route

- [ ] Ingestion d'autres formats (Nessus, OpenVAS, CycloneDX)
- [ ] Authentification et rôles (CISO, auditeur, lecture seule)
- [ ] Export PDF de la SoA et du registre des risques
- [ ] Mapping RGPD et HDS au niveau contrôle
- [ ] Historisation des scores pour suivre la tendance du risque

## ⚠️ Avertissement

Ce projet est une **preuve de concept pédagogique**. Le centre d'imagerie, ses actifs et ses données sont fictifs. Il ne remplace pas une analyse de risques réelle ni un conseil de conformité.

## 📜 Licence

Distribué sous licence [MIT](LICENSE).

<div align="center">

**Développé par [h-4mza](https://github.com/h-4mza)** · Si le projet vous est utile, une ⭐ fait plaisir.

</div>