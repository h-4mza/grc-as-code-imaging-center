import yaml

filepath = r"C:\Users\HP\Desktop\GRC\grc\iso27001\annex_a.yaml"

with open(filepath, 'r', encoding='utf-8') as f:
    data = yaml.safe_load(f)

# Thème 6 : Personnes
theme6_controls = [
    ("6.1", "Criblage (Screening)", True, "Vérification des antécédents du personnel.", "En place", 3, "Procédure RH"),
    ("6.2", "Termes et conditions d'embauche", True, "Contrats incluant les clauses de sécurité.", "En place", 4, "Contrat de travail type"),
    ("6.3", "Sensibilisation, formation et éducation à la SSI", True, "Formation contre le phishing.", "Partiel", 2, "Campagnes annuelles"),
    ("6.4", "Processus disciplinaire", True, "Sanctions en cas de non-respect.", "En place", 3, "Règlement intérieur"),
    ("6.5", "Responsabilités après la fin de contrat", True, "Restitution du matériel.", "En place", 3, "Checklist RH de départ"),
    ("6.6", "Accords de confidentialité", True, "Signature des NDAs par les partenaires.", "Partiel", 2, "Manque sur certains sous-traitants"),
    ("6.7", "Télétravail", True, "Règles pour le téléradiologue.", "En place", 3, "Charte télétravail"),
    ("6.8", "Signalement des événements de sécurité", True, "Déclaration des incidents.", "Partiel", 2, "Formulaire intranet peu utilisé")
]

# Thème 7 : Physique
theme7_controls = [
    ("7.1", "Périmètres de sécurité physique", True, "Accès réglementé aux salles d'imagerie.", "En place", 4, "Badges d'accès"),
    ("7.2", "Contrôles d'entrée physiques", True, "Contrôle à l'accueil du centre.", "En place", 4, "Vigile et accueil"),
    ("7.3", "Sécurisation des bureaux, salles et installations", True, "Bureaux des radiologues fermés.", "Partiel", 2, "Portes parfois ouvertes"),
    ("7.4", "Surveillance physique de la sécurité", True, "Caméras dans les zones communes.", "En place", 3, "Vidéosurveillance"),
    ("7.8", "Emplacement et protection des équipements", True, "Baie informatique sécurisée.", "Partiel", 2, "Local climatisé mais partagé"),
    ("7.10", "Supports de stockage", True, "Gestion des disques durs PACS.", "En place", 3, "Procédure de destruction certifiée"),
    ("7.14", "Élimination sécurisée", True, "Rebut du matériel médical obsolète.", "En place", 3, "Contrat avec prestataire DEEE")
]

for c in theme6_controls:
    data["controls"].append({
        "id": c[0],
        "nom": c[1],
        "theme": "Personnes",
        "applicable": c[2],
        "justification": c[3],
        "etat": c[4],
        "maturite": c[5],
        "preuve": c[6]
    })
    
for c in theme7_controls:
    data["controls"].append({
        "id": c[0],
        "nom": c[1],
        "theme": "Physique",
        "applicable": c[2],
        "justification": c[3],
        "etat": c[4],
        "maturite": c[5],
        "preuve": c[6]
    })

with open(filepath, "w", encoding="utf-8") as f:
    yaml.dump(data, f, allow_unicode=True, sort_keys=False, default_flow_style=False)
