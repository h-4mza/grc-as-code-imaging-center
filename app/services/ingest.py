from sqlalchemy.orm import Session
from app.models import Finding, ScenarioOperationnel, Control
from app.parsers.sarif import parse_sarif

def ingest_findings(db: Session, source: str, filepath: str):
    """Ingère les constats d'un fichier en base."""
    findings_data = []
    
    if source.lower() == "sarif":
        findings_data = parse_sarif(filepath)
    else:
        raise ValueError(f"Source de données non supportée : {source}")
        
    for data in findings_data:
        finding = Finding(
            source=data["source"],
            severite=data["severite"],
            actif_id=data["actif_id"],
            cve=data["cve"],
            technique_attack=data["technique_attack"],
            description=data.get("message", ""),
            date=data["date"]
        )
        db.add(finding)
        db.flush() # Pour récupérer l'ID
        
        # Logique de rattachement automatique : 
        # Si un constat a une technique ATT&CK, on le lie aux risques (SC_OP) qui ont cette technique.
        if finding.technique_attack:
            # Recherche de correspondances partielles dans la chaîne JSON
            related_risks = db.query(ScenarioOperationnel).filter(
                ScenarioOperationnel.techniques_attack.contains(finding.technique_attack)
            ).all()
            for r in related_risks:
                finding.risks.append(r)
                
        # Idéalement, on lie aussi au contrôle défaillant (ex: Vulnérabilité -> 8.8 Gestion des vuln)
        ctrl_vuln = db.query(Control).filter_by(id="8.8").first()
        if ctrl_vuln:
            finding.controls.append(ctrl_vuln)

    db.commit()
    return len(findings_data)
