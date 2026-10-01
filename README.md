# 🛡️ GRC As-Code : Centre d'Imagerie Médicale

Un système de pilotage de la sécurité de l'information (GRC : Gouvernance, Risques, Conformité) innovant, entièrement géré **"As-Code"**. Conçu pour un Centre d'Imagerie Médicale fictif, ce projet démontre comment automatiser, versionner et piloter la conformité cybersécurité via des pipelines CI/CD modernes.

---

## 🎯 Objectifs du Projet

- **Versionner la conformité (GitOps)** : Les risques EBIOS RM, les contrôles ISO 27001 et les plans de traitement sont stockés sous forme de fichiers YAML (`grc/`).
- **Générer dynamiquement les rapports** : Fini les fichiers Word obsolètes ! Les documents normatifs comme la Déclaration d'Applicabilité (SoA) sont générés en temps réel.
- **Automatiser l'ingestion des vulnérabilités** : Intégration continue avec des outils de scan de sécurité (SARIF) pour relier automatiquement les vulnérabilités techniques aux risques opérationnels (ATT&CK).
- **Synchroniser la remédiation** : Connecteur Jira pour créer et suivre automatiquement les tickets de traitement des risques.

## 🏗️ Architecture Technique

La solution repose sur une stack moderne, légère et orientée API. Le schéma ci-dessous illustre le flux de données de l'approche "GRC As-Code" :

```mermaid
flowchart TD
    subgraph Data ["GRC As-Code Data (Git)"]
        EBIOS["Fichiers YAML<br>EBIOS RM"]
        ISO["Fichiers YAML<br>ISO 27001"]
        MAP["Mappings<br>NIS2, NIST, ATT&CK"]
    end

    subgraph Operations ["Administration (DevSecOps)"]
        SARIF["Rapports de Scan<br>(Format SARIF)"]
        CLI["CLI Typer<br>'grc load' / 'grc ingest'"]
    end

    subgraph Core ["Backend Services"]
        DB[("PostgreSQL<br>Base GRC")]
        API["FastAPI<br>Moteur de règles & API"]
    end

    subgraph Users ["Interfaces"]
        DASH["Dashboard Streamlit<br>(Heatmap, SoA, KPIs)"]
    end
    
    subgraph External ["Outils Tiers"]
        JIRA["Jira / ITSM<br>(Suivi des traitements)"]
    end

    Data -->|Parsé par CLI| CLI
    SARIF -->|Ingéré par CLI| CLI
    CLI -->|Alimente| DB
    DB <-->|Interroge| API
    API <-->|Consomme les KPIs| DASH
    API -->|Synchronise| JIRA
```

- **Base de données** : PostgreSQL (stockage relationnel des risques, contrôles, et mappings).
- **Backend / API** : FastAPI (Python 3.11), exposant les endpoints de pilotage et les KPIs (`http://localhost:8000/docs`).
- **CLI d'Administration** : Typer (commandes `grc load`, `grc ingest`, `grc export-jira` pour les administrateurs).
- **Dashboard / Frontend** : Streamlit (tableau de bord de pilotage CISO interactif).
- **Infrastructure** : Docker & Docker-Compose (conteneurisation complète).

## ✨ Fonctionnalités Implémentées

### 1. Analyse de Risques (EBIOS RM)
Modélisation complète des 5 ateliers de la méthode EBIOS RM :
- **Atelier 1 & 2** : Valeurs métiers (Base de données patients, PACS) et Événements redoutés.
- **Atelier 3** : Scénarios stratégiques et profils d'attaquants.
- **Atelier 4** : Scénarios opérationnels et matrice de risques (Gravité / Vraisemblance inhérente & résiduelle).
- **Atelier 5** : Traitements de sécurité.

### 2. Référentiels et Conformité
- **ISO 27001:2022** : Intégration complète des 93 contrôles de l'Annexe A.
- **Mappings Croisés** : Alignement des mesures de sécurité avec les directives **NIS2**, le framework **NIST CSF 2.0**, et les techniques du **MITRE ATT&CK**.

### 3. Tableau de Bord (Dashboard)
Interface d'administration (Streamlit) proposant 5 vues de pilotage :
1. **Vue d'ensemble** : KPIs globaux (Risques critiques, vulnérabilités).
2. **Heatmap des Risques** : Matrice dynamique des scores de risque inhérent vs résiduel.
3. **SoA (ISO 27001)** : État d'avancement par chapitre (Organisationnel, Personnes, Physique, Tech).
4. **Conformité Globale** : Statistiques de couverture NIS2 / NIST / ATT&CK.
5. **Rapports Documentaires** : Génération visuelle, formelle et exportable de la Déclaration d'Applicabilité (SoA) prête pour l'audit.

---

## 🚀 Démarrage Rapide (Local)

### Prérequis
- `Docker` et `Docker Compose`
- `Make` (optionnel)

### Lancement via Make
Si vous disposez de l'utilitaire Make, exécutez simplement :
```bash
make demo
```
*Cela construira les conteneurs, lancera la base de données, l'API et le Dashboard, et peuplera automatiquement la base via la CLI (commande `grc load`).*

### Lancement manuel (Docker Compose)
Si vous préférez lancer manuellement :
```bash
# 1. Démarrer les services
docker-compose up -d --build

# 2. Peupler la base de données avec le référentiel YAML
docker-compose exec -e DATABASE_URL="postgresql+psycopg2://grc_user:grc_password@postgres/grc_db" api python -m app.cli load
```

### Accès aux interfaces
- **Dashboard Streamlit** (Pilotage) : [http://localhost:8501](http://localhost:8501)
- **API FastAPI** (Documentation Swagger) : [http://localhost:8000/docs](http://localhost:8000/docs)

---

## 💻 Exemples d'utilisation du CLI GRC

L'outil dispose d'une ligne de commande intégrée au conteneur API pour les tâches DevSecOps :

**Recharger le référentiel YAML en base de données :**
```bash
docker-compose exec api python -m app.cli load
```

**Ingérer un rapport de scan de vulnérabilités (format SARIF) :**
```bash
docker-compose exec api python -m app.cli ingest samples/trivy_report.sarif
```

**Exporter les plans de traitement vers Jira (Synchronisation) :**
```bash
docker-compose exec api python -m app.cli export-jira --project CIMSEC
```

---

*Développé dans le cadre d'un PoC de GRC-as-Code pour démontrer les capacités de l'automatisation de la conformité.*
