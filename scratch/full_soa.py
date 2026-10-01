import yaml
import json

raw_controls = [
    # Chapitre 5 (Organisationnel)
    ("5.1", "Politiques de sécurité de l'information", "Des politiques de sécurité de l'information, leurs sujets spécifiques et leur mise en œuvre doivent être définis, approuvés par la direction...", "Organisationnel"),
    ("5.2", "Rôles et responsabilités en matière de sécurité de l'information", "Les rôles et responsabilités en matière de sécurité de l'information doivent être définis et attribués...", "Organisationnel"),
    ("5.3", "Séparation des tâches", "Les tâches conflictuelles et les domaines de responsabilités conflictuels doivent être séparés.", "Organisationnel"),
    ("5.4", "Responsabilités de la direction", "La direction doit exiger de tout le personnel qu'il applique la sécurité de l'information...", "Organisationnel"),
    ("5.5", "Contacts avec les autorités", "L'organisation doit établir et maintenir des contacts avec les autorités compétentes.", "Organisationnel"),
    ("5.6", "Contacts avec des groupes d'intérêts spéciaux", "L'organisation doit établir et maintenir des contacts avec des groupes d'intérêt particuliers...", "Organisationnel"),
    ("5.7", "Renseignements sur les menaces", "Des informations relatives aux menaces pour la sécurité de l'information doivent être recueillies...", "Organisationnel"),
    ("5.8", "Sécurité de l'information dans la gestion de projet", "La sécurité de l'information doit être intégrée dans la gestion de projet.", "Organisationnel"),
    ("5.9", "Inventaire des informations et des autres actifs associés", "Un inventaire des informations et des autres actifs associés, y compris leurs propriétaires, doit être élaboré...", "Organisationnel"),
    ("5.10", "Utilisation acceptable des informations et des autres actifs associés", "Des règles relatives à l'utilisation acceptable et aux procédures de traitement...", "Organisationnel"),
    ("5.11", "Restitution des actifs", "Le personnel et les autres parties intéressées concernés doivent restituer tous les actifs...", "Organisationnel"),
    ("5.12", "Classification des informations", "Les informations doivent être classifiées selon les besoins de sécurité...", "Organisationnel"),
    ("5.13", "Marquage des informations", "Un ensemble approprié de procédures de marquage des informations doit être élaboré...", "Organisationnel"),
    ("5.14", "Transfert d'information", "Des règles, procédures ou accords relatifs au transfert d'informations doivent être mis en place...", "Organisationnel"),
    ("5.15", "Contrôle d'accès", "Des règles de contrôle d'accès aux informations et aux autres actifs associés doivent être établies...", "Organisationnel"),
    ("5.16", "Gestion des identités", "Le cycle de vie complet des identités doit être géré.", "Organisationnel"),
    ("5.17", "Informations d'authentification", "L'attribution et la gestion des informations d'authentification doivent être contrôlées...", "Organisationnel"),
    ("5.18", "Droits d'accès", "Les droits d'accès aux informations et aux autres actifs associés doivent être provisionnés...", "Organisationnel"),
    ("5.19", "Sécurité de l'information dans les relations avec les fournisseurs", "Des processus et des procédures doivent être définis et mis en œuvre pour gérer les risques...", "Organisationnel"),
    ("5.20", "Prise en compte de la sécurité de l'information dans les contrats fournisseurs", "Les exigences pertinentes en matière de sécurité de l'information doivent être établies...", "Organisationnel"),
    ("5.21", "Gestion de la sécurité de l'information dans la chaîne d'approvisionnement des TIC", "Des processus et des procédures doivent être définis et mis en œuvre...", "Organisationnel"),
    ("5.22", "Surveillance, révision et gestion du changement des services fournisseurs", "L'organisation doit régulièrement surveiller, réviser, évaluer et gérer les changements...", "Organisationnel"),
    ("5.23", "Sécurité de l'information pour l'utilisation de services cloud", "Les processus d'acquisition, d'utilisation, de gestion et de cessation des services cloud...", "Organisationnel"),
    ("5.24", "Planification et préparation de la gestion des incidents de sécurité de l'information", "L'organisation doit planifier et se préparer à gérer les incidents...", "Organisationnel"),
    ("5.25", "Évaluation et décision sur les événements de sécurité de l'information", "L'organisation doit évaluer les événements de sécurité de l'information...", "Organisationnel"),
    ("5.26", "Réponse aux incidents de sécurité de l'information", "Les incidents de sécurité de l'information doivent faire l'objet d'une réponse...", "Organisationnel"),
    ("5.27", "Apprentissage des incidents de sécurité de l'information", "Les connaissances acquises à partir des incidents de sécurité de l'information doivent être utilisées...", "Organisationnel"),
    ("5.28", "Collecte de preuves", "L'organisation doit établir et mettre en œuvre des procédures pour l'identification...", "Organisationnel"),
    ("5.29", "Sécurité de l'information lors de perturbations", "L'organisation doit planifier comment maintenir la sécurité de l'information...", "Organisationnel"),
    ("5.30", "Préparation des TIC pour la continuité d'activité", "La préparation des TIC doit être planifiée, mise en œuvre, maintenue et testée...", "Organisationnel"),
    ("5.31", "Exigences légales, réglementaires et contractuelles", "Les exigences légales, réglementaires et contractuelles pertinentes à la sécurité...", "Organisationnel"),
    ("5.32", "Droits de propriété intellectuelle", "L'organisation doit mettre en œuvre des procédures appropriées pour protéger les droits...", "Organisationnel"),
    ("5.33", "Protection des enregistrements", "Les enregistrements doivent être protégés contre la perte, la destruction...", "Organisationnel"),
    ("5.34", "Confidentialité et protection des informations personnelles", "L'organisation doit identifier et satisfaire aux exigences relatives à la préservation...", "Organisationnel"),
    ("5.35", "Révision indépendante de la sécurité de l'information", "L'approche de l'organisation en matière de gestion de la sécurité de l'information...", "Organisationnel"),
    ("5.36", "Conformité aux politiques, règles et normes de sécurité de l'information", "La conformité à la politique de sécurité de l'information...", "Organisationnel"),
    ("5.37", "Procédures d'exploitation documentées", "Les procédures d'exploitation relatives aux installations de traitement de l'information...", "Organisationnel"),
    
    # Chapitre 6 (Personnes)
    ("6.1", "Sélection du personnel", "Les vérifications des antécédents de tous les candidats au recrutement doivent être effectuées...", "Personnes"),
    ("6.2", "Conditions d'emploi", "Les accords contractuels avec le personnel et les sous-traitants doivent énoncer leurs responsabilités...", "Personnes"),
    ("6.3", "Sensibilisation, éducation et formation à la sécurité de l'information", "Tout le personnel de l'organisation et les parties intéressées pertinentes doivent recevoir...", "Personnes"),
    ("6.4", "Processus disciplinaire", "Un processus disciplinaire doit être formalisé et communiqué...", "Personnes"),
    ("6.5", "Responsabilités après la fin ou le changement d'emploi", "Les responsabilités et obligations en matière de sécurité de l'information qui demeurent valables...", "Personnes"),
    ("6.6", "Accords de confidentialité ou de non-divulgation", "Des accords de confidentialité ou de non-divulgation reflétant les besoins de l'organisation...", "Personnes"),
    ("6.7", "Travail à distance", "Lorsque le personnel travaille à distance, des mesures de sécurité doivent être mises en œuvre...", "Personnes"),
    ("6.8", "Signalement des événements de sécurité de l'information", "L'organisation doit mettre à disposition du personnel un mécanisme lui permettant de signaler...", "Personnes"),
    
    # Chapitre 7 (Physique)
    ("7.1", "Périmètres de sécurité physique", "Des périmètres de sécurité doivent être définis et utilisés pour protéger les zones...", "Physique"),
    ("7.2", "Entrée physique", "Les zones sécurisées doivent être protégées par des contrôles d'entrée appropriés...", "Physique"),
    ("7.3", "Sécurisation des bureaux, salles et installations", "Une sécurité physique doit être conçue et mise en œuvre pour les bureaux, les salles...", "Physique"),
    # On ajoute quelques-uns manquants pour avoir une idée
    ("7.4", "Surveillance physique de la sécurité", "Les locaux doivent être surveillés en permanence contre les accès non autorisés.", "Physique"),
    ("7.14", "Élimination sécurisée", "L'élimination du matériel contenant des données doit être sécurisée.", "Physique"),
    
    # Chapitre 8 (Technologique)
    ("8.1", "Appareils terminaux", "Les terminaux utilisateurs doivent être protégés.", "Technologique"),
    ("8.5", "Authentification sécurisée", "L'authentification doit être forte.", "Technologique"),
    ("8.7", "Protection contre les logiciels malveillants", "Les systèmes doivent être protégés contre les malwares.", "Technologique"),
    ("8.8", "Gestion des vulnérabilités techniques", "Les failles doivent être identifiées et corrigées.", "Technologique"),
    ("8.9", "Gestion des configurations", "Les systèmes doivent être durcis.", "Technologique"),
    ("8.10", "Suppression de l'information", "L'information ne doit être conservée que si nécessaire.", "Technologique"),
    ("8.11", "Masquage des données", "Les données sensibles doivent être anonymisées si applicable.", "Technologique"),
    ("8.12", "Prévention des fuites de données (DLP)", "Des outils DLP doivent être mis en place.", "Technologique"),
    ("8.13", "Sauvegarde de l'information", "Les données doivent être sauvegardées régulièrement.", "Technologique"),
    ("8.16", "Activités de surveillance", "Les événements de sécurité doivent être surveillés.", "Technologique"),
    ("8.20", "Sécurité des réseaux", "Le réseau doit être segmenté et sécurisé.", "Technologique"),
    ("8.24", "Cryptographie", "La cryptographie doit être utilisée pour protéger les données.", "Technologique"),
]

controls = []
for c in raw_controls:
    controls.append({
        "id": c[0],
        "nom": c[1],
        "description": c[2],
        "theme": c[3],
        "applicable": True,
        "justification": "Applicable dans le cadre de la conformité ONDA-TNG-SEC.",
        "etat": "Partiel",
        "maturite": 2,
        "preuve": "A documenter"
    })

data = {"controls": controls}

with open(r"C:\Users\HP\Desktop\GRC\grc\iso27001\annex_a.yaml", "w", encoding="utf-8") as f:
    yaml.dump(data, f, allow_unicode=True, sort_keys=False, default_flow_style=False)
