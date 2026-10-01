from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from app.db import get_db
from app.models import ScenarioOperationnel, Control
from app.services.scoring import get_risk_scores

app = FastAPI(
    title="GRC API",
    description="API de pilotage GRC as-code (EBIOS, ISO 27001, NIS2)",
    version="1.0.0",
)

@app.get("/")
def root():
    return {"message": "Bienvenue sur l'API GRC-as-code"}

@app.get("/risks")
def get_risks(db: Session = Depends(get_db)):
    scenarios = db.query(ScenarioOperationnel).all()
    results = []
    for sc in scenarios:
        # Mock maturity calculation (would be based on mapped controls later)
        scores = get_risk_scores(gravite=sc.gravite, vraisemblance=sc.vraisemblance, maturity_avg=2.0)
        results.append({
            "id": sc.id,
            "nom": sc.nom,
            "scores": scores
        })
    return results

@app.get("/controls")
def get_controls(db: Session = Depends(get_db)):
    controls = db.query(Control).all()
    return controls


@app.get("/kpi/overview")
def get_kpi_overview(db: Session = Depends(get_db)):
    from sqlalchemy import func
    from app.models import Control, ScenarioOperationnel, Finding, Treatment
    
    total_risks = db.query(ScenarioOperationnel).count()
    total_controls = db.query(Control).count()
    controls_en_place = db.query(Control).filter(Control.etat == "En place").count()
    total_findings = db.query(Finding).count()
    total_treatments = db.query(Treatment).count()
    
    # On recalcule les risques critiques pour la démo
    risques_critiques = 0
    for sc in db.query(ScenarioOperationnel).all():
        scores = get_risk_scores(sc.gravite, sc.vraisemblance, 2.0)
        if scores["niveau_residuel"] == "Critique" or scores["niveau_inherent"] == "Critique":
            risques_critiques += 1

    return {
        "total_risks": total_risks,
        "risques_critiques": risques_critiques,
        "controls_en_place_pct": round((controls_en_place / total_controls * 100) if total_controls else 0),
        "total_findings": total_findings,
        "total_treatments": total_treatments
    }

@app.get("/kpi/heatmap")
def get_kpi_heatmap(db: Session = Depends(get_db)):
    scenarios = db.query(ScenarioOperationnel).all()
    # Mock return format for a scatter plot or heatmap
    data = []
    for sc in scenarios:
        scores = get_risk_scores(sc.gravite, sc.vraisemblance, 2.0) # Maturity mocked at 2.0 for now
        data.append({
            "id": sc.id,
            "nom": sc.nom,
            "gravite": sc.gravite,
            "vraisemblance_inherente": sc.vraisemblance,
            "score_inherent": scores["score_inherent"],
            "niveau_inherent": scores["niveau_inherent"],
            "niveau_residuel": scores["niveau_residuel"]
        })
    return data

@app.get("/kpi/soa")
def get_kpi_soa(db: Session = Depends(get_db)):
    from sqlalchemy import func
    controls = db.query(Control.theme, func.count(Control.id).label('total'),
                        func.sum(case((Control.etat == 'En place', 1), else_=0)).label('en_place'))\
                 .group_by(Control.theme).all()
    
    # workaround for case not imported
    # Let's do it in memory for simplicity
    all_controls = db.query(Control).all()
    stats = {}
    for c in all_controls:
        if c.theme not in stats:
            stats[c.theme] = {"total": 0, "en_place": 0}
        stats[c.theme]["total"] += 1
        if c.etat == "En place":
            stats[c.theme]["en_place"] += 1
            
    return [{"theme": k, "total": v["total"], "en_place": v["en_place"]} for k, v in stats.items()]

@app.get("/kpi/treatments")
def get_kpi_treatments(db: Session = Depends(get_db)):
    treatments = db.query(Treatment).all()
    return [{"id": t.id, "nom": t.nom, "responsable": t.responsable, "echeance": t.echeance, "jira": t.jira_key} for t in treatments]

@app.get("/kpi/compliance")
def get_kpi_compliance(db: Session = Depends(get_db)):
    from app.models import ControlMapping
    from sqlalchemy import func
    
    mappings = db.query(ControlMapping.framework, func.count(ControlMapping.id).label('total')).group_by(ControlMapping.framework).all()
    return [{"framework": m[0], "total_mapped_controls": m[1]} for m in mappings]
