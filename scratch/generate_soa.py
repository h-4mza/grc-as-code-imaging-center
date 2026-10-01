import yaml

controls = []

# Thème 5 : Organisationnel (Sélection des plus pertinents pour l'imagerie médicale)
theme5_controls = [
    ("5.1", "Politiques en matière de sécurité de l'information", True, "Nécessaire pour définir le cadre général.", "En place", 3, "P-SSI-01 signée par la direction"),
    ("5.2", "Rôles et responsabilités", True, "Nécessaire pour répartir les tâches (RSSI, DPO, admins).", "Partiel", 2, "Fiches de poste, charte IT"),
    ("5.3", "Séparation des tâches", True, "Évite les conflits d'intérêts et la fraude.", "En place", 3, "Matrice des droits (Matrice_RBAC_v1.xlsx)"),
    ("5.7", "Veille sur les menaces", True, "Identification des menaces du secteur santé.", "En place", 2, "Abonnement CERT-Santé"),
    ("5.8", "Sécurité dans la gestion de projet", True, "Intégration de la sécurité (Security by design).", "Non initié", 1, "Aucune procédure formalisée"),
    ("5.9", "Inventaire des informations et autres actifs", True, "Base de l'analyse de risque.", "En place", 3, "Fichier assets.yaml"),
    ("5.10", "Utilisation acceptable des actifs", True, "Encadrement de l'utilisation des postes et équipements.", "En place", 4, "Charte d'utilisation du SI signée"),
    ("5.15", "Contrôle d'accès", True, "Gestion stricte des accès au PACS et DPI.", "Partiel", 2, "Politique d'accès, mais révisions incomplètes"),
    ("5.19", "Sécurité des informations dans les relations fournisseurs", True, "Contrôle des éditeurs PACS et mainteneurs.", "Partiel", 2, "Contrats avec clauses cyber, mais sans audit"),
    ("5.24", "Gestion des incidents de cybersécurité", True, "Réponse aux attaques (ex: ransomware).", "En place", 2, "Procédure P-INC-01, mais non testée"),
    ("5.29", "Continuité de la sécurité de l'information", True, "Maintien de la sécurité en cas de crise.", "Partiel", 2, "PRA technique existant, PCA métier à revoir"),
]

for c in theme5_controls:
    controls.append({
        "id": c[0],
        "nom": c[1],
        "theme": "Organisationnel",
        "applicable": c[2],
        "justification": c[3],
        "etat": c[4],
        "maturite": c[5],
        "preuve": c[6]
    })

# Thème 8 : Technologique (Sélection)
theme8_controls = [
    ("8.1", "Appareils terminaux (Endpoint devices)", True, "Protection des postes radiologues.", "Partiel", 2, "Antivirus standard, pas d'EDR"),
    ("8.2", "Droits d'accès privilégiés", True, "Protection des comptes admins du PACS/Domaine.", "Partiel", 1, "Comptes partagés sur certains équipements"),
    ("8.3", "Restriction d'accès à l'information", True, "Cloisonnement des dossiers patients.", "En place", 3, "Droits RBAC dans le DPI"),
    ("8.4", "Accès au code source", False, "Le centre ne développe pas de logiciels.", "N/A", 0, "Exclusion validée par la direction"),
    ("8.5", "Authentification sécurisée", True, "Protection contre les vols de mots de passe.", "Non initié", 1, "MFA non déployé"),
    ("8.7", "Protection contre les logiciels malveillants", True, "Lutte contre les ransomwares.", "Partiel", 2, "Antivirus déployé mais non géré centralement"),
    ("8.8", "Gestion des vulnérabilités techniques", True, "Patch management des serveurs et scanners.", "Partiel", 1, "Scanners médicaux obsolètes (Win 7)"),
    ("8.9", "Gestion des configurations", True, "Durcissement des systèmes.", "Non initié", 1, "Installations par défaut, pas de master"),
    ("8.10", "Suppression de l'information", True, "Purge des anciens dossiers selon réglementation.", "En place", 3, "Script de purge > 10 ans sur le PACS"),
    ("8.11", "Masquage des données", True, "Anonymisation pour recherche/téléradiologie.", "En place", 3, "Module d'anonymisation DICOM actif"),
    ("8.12", "Prévention des fuites de données (DLP)", True, "Éviter l'exfiltration de données patients.", "Non initié", 0, "Aucun outil DLP"),
    ("8.13", "Sauvegarde de l'information", True, "Protection contre les ransomwares.", "En place", 3, "Sauvegardes 3-2-1 chez l'hébergeur HDS"),
    ("8.16", "Activités de surveillance (Monitoring)", True, "Détection d'intrusions (SIEM).", "Non initié", 0, "Pas de centralisation des logs"),
    ("8.20", "Sécurité des réseaux", True, "Segmentation des modalités d'imagerie.", "Partiel", 2, "VLANs existants mais règles de firewall permissives"),
    ("8.24", "Cryptographie", True, "Chiffrement des données en transit et au repos.", "Partiel", 2, "VPN pour téléradiologie (TLS), mais PACS non chiffré au repos"),
]

for c in theme8_controls:
    controls.append({
        "id": c[0],
        "nom": c[1],
        "theme": "Technologique",
        "applicable": c[2],
        "justification": c[3],
        "etat": c[4],
        "maturite": c[5],
        "preuve": c[6]
    })

data = {"controls": controls}

with open(r"C:\Users\HP\Desktop\GRC\grc\iso27001\annex_a.yaml", "w", encoding="utf-8") as f:
    yaml.dump(data, f, allow_unicode=True, sort_keys=False, default_flow_style=False)
