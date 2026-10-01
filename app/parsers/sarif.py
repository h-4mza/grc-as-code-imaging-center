import json

def parse_sarif(filepath: str):
    """Parse un fichier SARIF et retourne une liste de dictionnaires de constats."""
    findings = []
    with open(filepath, 'r', encoding='utf-8') as f:
        data = json.load(f)
        
    for run in data.get("runs", []):
        for result in run.get("results", []):
            finding = {
                "source": "SARIF_Scanner",
                "cve": result.get("ruleId"),
                "severite": result.get("level", "medium"),
                "date": "2026-10-01",
                # Logique simplifiée : on extrait l'actif cible depuis les tags ou les locations
                "actif_id": "ast_modalites", # Valeur par défaut pour l'exemple
                "technique_attack": None
            }
            # Tentative de récupération du tag ATT&CK
            if "properties" in result and "tags" in result["properties"]:
                for tag in result["properties"]["tags"]:
                    if tag.startswith("T"):
                        finding["technique_attack"] = tag
            
            findings.append(finding)
            
    return findings
