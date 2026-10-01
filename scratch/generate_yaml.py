import yaml
import os

os.makedirs('grc/si', exist_ok=True)
os.makedirs('grc/ebios', exist_ok=True)

business_values = {
    "business_values": [
        {
            "id": "bv_prise_en_charge",
            "name": "Prise en charge patient",
            "process": "Accueil administratif, vérification des prescriptions, enregistrement DPI/RIS, consentement",
            "feared_event": "Impossibilité d'accueillir et d'enregistrer les patients, entraînant des retards de prise en charge.",
            "severity": 4
        },
        {
            "id": "bv_acquisition",
            "name": "Acquisition des images",
            "process": "Réalisation de l'examen par le manipulateur, acquisition et transfert DICOM vers le PACS",
            "feared_event": "Arrêt des équipements d'imagerie ou impossibilité de transférer les images, arrêt de la production de soins.",
            "severity": 4
        },
        {
            "id": "bv_interpretation",
            "name": "Interprétation et compte rendu",
            "process": "Visualisation PACS, rédaction CR dans le RIS, signature électronique, envoi MSSanté",
            "feared_event": "Indisponibilité des images ou du RIS retardant le diagnostic, ou erreur de compte rendu affectant la santé du patient.",
            "severity": 4
        },
        {
            "id": "bv_teleradiologie",
            "name": "Téléradiologie",
            "process": "Transfert chiffré VPN, interprétation à distance, retour CR signé",
            "feared_event": "Interception ou indisponibilité du flux de téléradiologie compromettant les gardes et urgences.",
            "severity": 4
        },
        {
            "id": "bv_archivage",
            "name": "Archivage légal",
            "process": "Stockage long terme, réplication sur site distant",
            "feared_event": "Perte définitive des historiques médicaux.",
            "severity": 4
        }
    ]
}

assets = {
    "assets": [
        {
            "id": "ast_pacs",
            "name": "PACS (Picture Archiving and Communication System)",
            "type": "application",
            "criticality": 4,
            "business_values": ["bv_acquisition", "bv_interpretation", "bv_teleradiologie", "bv_archivage"]
        },
        {
            "id": "ast_modalites",
            "name": "Scanner IRM / Scanner CT / Mammographe",
            "type": "device",
            "criticality": 4,
            "business_values": ["bv_acquisition"]
        },
        {
            "id": "ast_vpn",
            "name": "Connexion Internet / VPN téléradiologie",
            "type": "network",
            "criticality": 4,
            "business_values": ["bv_teleradiologie", "bv_archivage"]
        },
        {
            "id": "ast_postes_travail",
            "name": "Postes de travail (Secrétariat, Médecins)",
            "type": "device",
            "criticality": 3,
            "business_values": ["bv_prise_en_charge", "bv_interpretation"]
        },
        {
            "id": "ast_personnel",
            "name": "Personnel du centre (Administratif, Manipulateurs, Médecins)",
            "type": "human",
            "criticality": 4,
            "business_values": ["bv_prise_en_charge", "bv_acquisition", "bv_interpretation"]
        },
        {
            "id": "ast_ris",
            "name": "RIS (Radiological Information System)",
            "type": "application",
            "criticality": 4,
            "business_values": ["bv_prise_en_charge", "bv_interpretation", "bv_teleradiologie"]
        },
        {
            "id": "ast_donnees_identite",
            "name": "Données administratives et identité patient",
            "type": "data",
            "criticality": 4,
            "business_values": ["bv_prise_en_charge"]
        }
    ]
}

w2_sources = {
    "risk_sources": [
        {
            "id": "sr_cybercriminels",
            "name": "Groupe de cybercriminels",
            "type": "Malveillance externe",
            "motivation": "Gain financier (extorsion)",
            "resources": "Importantes (outils sophistiqués, botnets, RaaS)"
        },
        {
            "id": "sr_employe_malveillant",
            "name": "Employé malveillant",
            "type": "Malveillance interne",
            "motivation": "Vengeance ou gain financier (revente d'accès)",
            "resources": "Modérées (Accès légitimes internes)"
        }
    ],
    "objectives": [
        {
            "id": "ov_extorsion",
            "name": "Extorsion par paralysie du SI et/ou menace de divulgation",
            "description": "Chiffrement des données (PACS, DPI) et exfiltration préalable pour double extorsion."
        },
        {
            "id": "ov_sabotage",
            "name": "Sabotage des opérations de soins",
            "description": "Destruction des accès ou des équipements biomédicaux."
        }
    ],
    "sr_ov_pairs": [
        {
            "id": "srov_1",
            "sr_id": "sr_cybercriminels",
            "ov_id": "ov_extorsion",
            "relevance": 4,
            "description": "Un groupe de ransomwares cible le centre pour chiffrer le PACS et demander une rançon."
        },
        {
            "id": "srov_2",
            "sr_id": "sr_employe_malveillant",
            "ov_id": "ov_sabotage",
            "relevance": 3,
            "description": "Un employé utilise ses accès pour détruire des bases de données."
        }
    ]
}

w3_strategiques = {
    "stakeholders": [
        {
            "id": "pp_editeur_pacs",
            "name": "Éditeur du PACS",
            "type": "Fournisseur logiciel",
            "threat_level": 4,
            "dependency": "Critique (Cœur du SI, accès télémaintenance privilégié)"
        },
        {
            "id": "pp_maintenance",
            "name": "Prestataire maintenance biomédicale",
            "type": "Fournisseur service",
            "threat_level": 3,
            "dependency": "Forte (Accès réseau aux modalités IRM/Scanner)"
        }
    ],
    "strategic_scenarios": [
        {
            "id": "sc_strat_1",
            "name": "Compromission via l'éditeur PACS (Supply Chain)",
            "srov_id": "srov_1",
            "stakeholder_id": "pp_editeur_pacs",
            "likelihood": 3,
            "description": "Des cybercriminels compromettent l'éditeur du PACS et déploient une mise à jour malveillante (ransomware) chez tous ses clients, y compris le centre d'imagerie."
        },
        {
            "id": "sc_strat_2",
            "name": "Attaque via accès VPN partenaire",
            "srov_id": "srov_1",
            "stakeholder_id": "pp_maintenance",
            "likelihood": 4,
            "description": "Un prestataire externe se fait voler ses accès, permettant aux attaquants d'entrer sur le réseau."
        }
    ]
}

w4_operationnels = {
    "risks": [
        {
            "id": "R-01",
            "name": "Phishing et déploiement de Ransomware",
            "strategic_scenario_id": None,
            "assets": ["ast_pacs", "ast_postes_travail", "ast_personnel"],
            "attack_techniques": ["T1566", "T1078", "T1486"],
            "likelihood": 4,
            "severity": 4,
            "description": "Envoi d'un email de phishing à un secrétaire médical, vol d'identifiants, puis déploiement d'un ransomware chiffrant le PACS.",
            "controls": ["A.8.7", "A.8.13", "A.5.14"],
            "nist_csf": ["PR.AT-01", "PR.DS-11", "RC.RP-03"]
        },
        {
            "id": "R-02",
            "name": "Exfiltration de données via faille VPN",
            "strategic_scenario_id": "sc_strat_2",
            "assets": ["ast_vpn", "ast_ris", "ast_donnees_identite"],
            "attack_techniques": ["T1190", "T1005", "T1567"],
            "likelihood": 4,
            "severity": 4,
            "description": "Exploitation d'une vulnérabilité non patchée sur le pare-feu/VPN de téléradiologie pour accéder au RIS et exfiltrer les données.",
            "controls": ["A.8.20", "A.8.22", "A.8.8"],
            "nist_csf": ["ID.RA-01", "PR.PT-04"]
        },
        {
            "id": "R-03",
            "name": "Compromission de la chaîne logistique",
            "strategic_scenario_id": "sc_strat_1",
            "assets": ["ast_pacs"],
            "attack_techniques": ["T1195", "T1021", "T1486"],
            "likelihood": 3,
            "severity": 4,
            "description": "L'éditeur du PACS est piraté, poussant une mise à jour malveillante qui chiffre automatiquement les bases de données du centre.",
            "controls": ["A.5.19", "A.5.21", "A.8.19"],
            "nist_csf": ["GV.SC-04"]
        },
        {
            "id": "R-04",
            "name": "Attaque d'un équipement IRM via télémaintenance",
            "strategic_scenario_id": "sc_strat_2",
            "assets": ["ast_modalites"],
            "attack_techniques": ["T1078", "T1499", "T1190"],
            "likelihood": 3,
            "severity": 4,
            "description": "Utilisation d'identifiants de mainteneur volés pour accéder au réseau biomédical et paralyser le scanner IRM.",
            "controls": ["A.8.20", "A.5.15"],
            "nist_csf": ["PR.AC-01"]
        },
        {
            "id": "R-05",
            "name": "Vol de données internes (Insider Threat)",
            "strategic_scenario_id": None,
            "assets": ["ast_personnel", "ast_postes_travail", "ast_donnees_identite"],
            "attack_techniques": ["T1078", "T1213", "T1052"],
            "likelihood": 3,
            "severity": 4,
            "description": "Un employé télécharge massivement des dossiers patients depuis le DPI vers une clé USB.",
            "controls": ["A.8.12", "A.6.1"],
            "nist_csf": ["PR.DS-05"]
        },
        {
            "id": "R-06",
            "name": "Attaque DDoS sur la ligne Internet",
            "strategic_scenario_id": None,
            "assets": ["ast_vpn"],
            "attack_techniques": ["T1498"],
            "likelihood": 4,
            "severity": 4,
            "description": "Saturation de la bande passante du centre, bloquant l'accès au service de téléradiologie.",
            "controls": ["A.8.16"],
            "nist_csf": ["PR.PT-04"]
        },
        {
            "id": "R-07",
            "name": "Rebond via une clinique partenaire",
            "strategic_scenario_id": None,
            "assets": ["ast_vpn", "ast_ris"],
            "attack_techniques": ["T1190", "T1565"],
            "likelihood": 3,
            "severity": 4,
            "description": "Un poste infecté dans une clinique voisine utilise la connexion VPN inter-sites pour altérer des CR médicaux.",
            "controls": ["A.8.22"],
            "nist_csf": ["PR.AC-05"]
        },
        {
            "id": "R-08",
            "name": "Destruction des sauvegardes HDS",
            "strategic_scenario_id": None,
            "assets": ["ast_pacs"],
            "attack_techniques": ["T1531", "T1485"],
            "likelihood": 2,
            "severity": 4,
            "description": "L'attaquant accède à la console cloud HDS et supprime les snapshots du PACS.",
            "controls": ["A.8.13", "A.8.14"],
            "nist_csf": ["PR.DS-11"]
        },
        {
            "id": "R-09",
            "name": "Interception de trafic DICOM non chiffré",
            "strategic_scenario_id": None,
            "assets": ["ast_modalites", "ast_pacs"],
            "attack_techniques": ["T1557", "T1040"],
            "likelihood": 3,
            "severity": 4,
            "description": "Écoute du trafic sur le LAN interne pour intercepter des images médicales en clair.",
            "controls": ["A.8.24"],
            "nist_csf": ["PR.DS-02"]
        },
        {
            "id": "R-10",
            "name": "Compromission de compte Administrateur (Brute Force)",
            "strategic_scenario_id": None,
            "assets": ["ast_postes_travail", "ast_vpn"],
            "attack_techniques": ["T1110", "T1078", "T1547"],
            "likelihood": 4,
            "severity": 4,
            "description": "Attaque brute force sur RDP exposé, menant à la compromission d'un compte admin (absence MFA).",
            "controls": ["A.5.17", "A.8.5"],
            "nist_csf": ["PR.AA-01"]
        }
    ]
}

w5_traitements = {
    "treatments": [
        {
            "id": "tr_mfa",
            "name": "Déploiement MFA pour accès critiques",
            "risk_id": "R-10",
            "option": "reduce",
            "due_date": "2026-12-31",
            "owner": "DSSI",
            "jira_key": None,
            "status": "todo"
        },
        {
            "id": "tr_segmentation",
            "name": "Segmentation réseau et sauvegardes hors ligne testées",
            "risk_id": "R-01",
            "option": "reduce",
            "due_date": "2026-11-30",
            "owner": "IT",
            "jira_key": None,
            "status": "in_progress"
        },
        {
            "id": "tr_patch_vpn",
            "name": "Mise à jour d'urgence firmware VPN",
            "risk_id": "R-02",
            "option": "reduce",
            "due_date": "2026-10-15",
            "owner": "Réseau",
            "jira_key": None,
            "status": "todo"
        },
        {
            "id": "tr_dicom_tls",
            "name": "Chiffrement TLS flux DICOM",
            "risk_id": "R-09",
            "option": "reduce",
            "due_date": "2027-01-31",
            "owner": "Biomédical",
            "jira_key": None,
            "status": "todo"
        }
    ]
}

def dump_yaml(data, filepath):
    with open(filepath, 'w', encoding='utf-8') as f:
        yaml.dump(data, f, allow_unicode=True, default_flow_style=False, sort_keys=False)

dump_yaml(business_values, 'grc/si/business_values.yaml')
dump_yaml(assets, 'grc/si/assets.yaml')
dump_yaml(w2_sources, 'grc/ebios/w2_sources.yaml')
dump_yaml(w3_strategiques, 'grc/ebios/w3_strategiques.yaml')
dump_yaml(w4_operationnels, 'grc/ebios/w4_operationnels.yaml')
dump_yaml(w5_traitements, 'grc/ebios/w5_traitements.yaml')
