import json
import yaml
import random

# All 93 ISO 27001:2022 Controls
raw_controls = [
    # Chapter 5 - 37 controls
    ("5.1", "Politiques de sécurité de l'information", "Organisationnel"),
    ("5.2", "Rôles et responsabilités", "Organisationnel"),
    ("5.3", "Séparation des tâches", "Organisationnel"),
    ("5.4", "Responsabilités de la direction", "Organisationnel"),
    ("5.5", "Contacts avec les autorités", "Organisationnel"),
    ("5.6", "Contacts avec des groupes d'intérêts", "Organisationnel"),
    ("5.7", "Renseignements sur les menaces", "Organisationnel"),
    ("5.8", "Sécurité dans la gestion de projet", "Organisationnel"),
    ("5.9", "Inventaire des actifs", "Organisationnel"),
    ("5.10", "Utilisation acceptable des actifs", "Organisationnel"),
    ("5.11", "Restitution des actifs", "Organisationnel"),
    ("5.12", "Classification des informations", "Organisationnel"),
    ("5.13", "Marquage des informations", "Organisationnel"),
    ("5.14", "Transfert d'information", "Organisationnel"),
    ("5.15", "Contrôle d'accès", "Organisationnel"),
    ("5.16", "Gestion des identités", "Organisationnel"),
    ("5.17", "Informations d'authentification", "Organisationnel"),
    ("5.18", "Droits d'accès", "Organisationnel"),
    ("5.19", "Sécurité fournisseurs", "Organisationnel"),
    ("5.20", "Sécurité dans les contrats fournisseurs", "Organisationnel"),
    ("5.21", "Sécurité chaîne d'approvisionnement TIC", "Organisationnel"),
    ("5.22", "Surveillance des fournisseurs", "Organisationnel"),
    ("5.23", "Sécurité des services cloud", "Organisationnel"),
    ("5.24", "Préparation gestion incidents", "Organisationnel"),
    ("5.25", "Évaluation des événements", "Organisationnel"),
    ("5.26", "Réponse aux incidents", "Organisationnel"),
    ("5.27", "Apprentissage des incidents", "Organisationnel"),
    ("5.28", "Collecte de preuves", "Organisationnel"),
    ("5.29", "Sécurité lors de perturbations", "Organisationnel"),
    ("5.30", "Préparation TIC pour continuité", "Organisationnel"),
    ("5.31", "Exigences légales", "Organisationnel"),
    ("5.32", "Propriété intellectuelle", "Organisationnel"),
    ("5.33", "Protection des enregistrements", "Organisationnel"),
    ("5.34", "Données personnelles", "Organisationnel"),
    ("5.35", "Révision indépendante", "Organisationnel"),
    ("5.36", "Conformité aux politiques", "Organisationnel"),
    ("5.37", "Procédures d'exploitation", "Organisationnel"),

    # Chapter 6 - 8 controls
    ("6.1", "Sélection du personnel", "Personnes"),
    ("6.2", "Conditions d'emploi", "Personnes"),
    ("6.3", "Sensibilisation", "Personnes"),
    ("6.4", "Processus disciplinaire", "Personnes"),
    ("6.5", "Fin d'emploi", "Personnes"),
    ("6.6", "Accords de confidentialité", "Personnes"),
    ("6.7", "Travail à distance", "Personnes"),
    ("6.8", "Signalement", "Personnes"),

    # Chapter 7 - 14 controls
    ("7.1", "Périmètres de sécurité", "Physique"),
    ("7.2", "Entrée physique", "Physique"),
    ("7.3", "Sécurisation bureaux/salles", "Physique"),
    ("7.4", "Surveillance physique", "Physique"),
    ("7.5", "Protection contre menaces externes", "Physique"),
    ("7.6", "Travail dans zones sécurisées", "Physique"),
    ("7.7", "Bureaux et écrans dégagés", "Physique"),
    ("7.8", "Emplacement des équipements", "Physique"),
    ("7.9", "Sécurité des actifs hors site", "Physique"),
    ("7.10", "Supports de stockage", "Physique"),
    ("7.11", "Services généraux", "Physique"),
    ("7.12", "Sécurité câblage", "Physique"),
    ("7.13", "Maintenance des équipements", "Physique"),
    ("7.14", "Élimination sécurisée", "Physique"),

    # Chapter 8 - 34 controls
    ("8.1", "Appareils terminaux", "Technologique"),
    ("8.2", "Privilèges d'accès", "Technologique"),
    ("8.3", "Restriction d'accès", "Technologique"),
    ("8.4", "Code source", "Technologique"),
    ("8.5", "Authentification sécurisée", "Technologique"),
    ("8.6", "Gestion de capacité", "Technologique"),
    ("8.7", "Protection malwares", "Technologique"),
    ("8.8", "Vulnérabilités techniques", "Technologique"),
    ("8.9", "Configurations", "Technologique"),
    ("8.10", "Suppression de l'information", "Technologique"),
    ("8.11", "Masquage des données", "Technologique"),
    ("8.12", "Prévention des fuites (DLP)", "Technologique"),
    ("8.13", "Sauvegarde", "Technologique"),
    ("8.14", "Redondance", "Technologique"),
    ("8.15", "Journalisation", "Technologique"),
    ("8.16", "Surveillance", "Technologique"),
    ("8.17", "Synchronisation horloges", "Technologique"),
    ("8.18", "Utilisation de programmes", "Technologique"),
    ("8.19", "Installation logiciels", "Technologique"),
    ("8.20", "Sécurité réseaux", "Technologique"),
    ("8.21", "Services réseau", "Technologique"),
    ("8.22", "Ségrégation réseaux", "Technologique"),
    ("8.23", "Filtrage Web", "Technologique"),
    ("8.24", "Cryptographie", "Technologique"),
    ("8.25", "Cycle de vie développement", "Technologique"),
    ("8.26", "Exigences sécurité", "Technologique"),
    ("8.27", "Architecture sécurité", "Technologique"),
    ("8.28", "Sécurité du codage", "Technologique"),
    ("8.29", "Tests de sécurité", "Technologique"),
    ("8.30", "Développement externalisé", "Technologique"),
    ("8.31", "Séparation environnements", "Technologique"),
    ("8.32", "Gestion des changements", "Technologique"),
    ("8.33", "Informations de test", "Technologique"),
    ("8.34", "Protection systèmes d'audit", "Technologique")
]

controls = []
statuses = ["implemented", "partial", "not_implemented"]

for c in raw_controls:
    cid = c[0]
    name = c[1]
    theme = c[2]
    
    # Custom Contextual Justifications and statuses for a Medical Imaging Center
    status = "partial"
    maturity = 2
    evidence = "A documenter"
    justification = "Applicable pour la protection globale du centre d'imagerie."
    
    if cid == "6.7":
        status = "implemented"
        maturity = 4
        justification = "Contrôle essentiel pour les médecins pratiquant la téléradiologie (VPN IPSec, poste durci)."
        evidence = "Charte de télétravail"
    elif cid == "8.13":
        status = "partial"
        maturity = 3
        justification = "Le PACS est sauvegardé quotidiennement mais l'immutabilité cloud reste à finaliser."
        evidence = "Rapport de sauvegarde Veeam"
    elif cid == "8.5":
        status = "not_implemented"
        maturity = 1
        justification = "Le MFA n'est pas encore déployé sur les postes RDP administratifs."
        evidence = "Audit interne"
    elif cid == "5.34":
        status = "implemented"
        maturity = 4
        justification = "Conformité RGPD et HDS strictement respectée pour les dossiers patients et comptes-rendus."
        evidence = "Registre RGPD"
    elif cid == "7.3":
        status = "implemented"
        maturity = 4
        justification = "Accès aux salles d'interprétation et aux salles machines par badge RFID nominatif."
        evidence = "Logs contrôle d'accès"
    elif cid == "8.24":
        status = "partial"
        maturity = 2
        justification = "Le flux DICOM en interne n'est pas encore chiffré TLS, mais le VPN externe l'est."
        evidence = "Analyse réseau"
    else:
        # Randomize for realistic feeling
        status = random.choice(statuses)
        if status == "implemented":
            maturity = random.choice([3, 4])
        elif status == "partial":
            maturity = random.choice([1, 2])
        else:
            maturity = 0

    controls.append({
        "id": cid,
        "name": name,
        "description": "Contrôle " + cid + " - " + name,
        "theme": theme,
        "is_applicable": True,
        "justification": justification,
        "status": status,
        "maturity": maturity,
        "evidence": evidence
    })

data = {"controls": controls}

with open("grc/iso27001/annex_a.yaml", "w", encoding="utf-8") as f:
    yaml.dump(data, f, allow_unicode=True, sort_keys=False, default_flow_style=False)
