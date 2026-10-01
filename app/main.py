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

