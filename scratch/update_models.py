import os
import re

# 1. Update app/models.py
with open('app/models.py', 'r', encoding='utf-8') as f:
    models_code = f.read()

if 'risk_asset_table' not in models_code:
    assoc_tables = '''
risk_asset_table = Table(
    'risk_asset',
    Base.metadata,
    Column('risk_id', String, ForeignKey('scenarios_operationnels.id'), primary_key=True),
    Column('asset_id', String, ForeignKey('assets.id'), primary_key=True)
)

risk_control_table = Table(
    'risk_control',
    Base.metadata,
    Column('risk_id', String, ForeignKey('scenarios_operationnels.id'), primary_key=True),
    Column('control_id', String, ForeignKey('controls.id'), primary_key=True)
)
'''
    models_code = models_code.replace('class ScenarioOperationnel(Base):', assoc_tables + '\nclass ScenarioOperationnel(Base):')
    
    # Add fields to ScenarioOperationnel
    models_code = models_code.replace(
        'description = Column(String)',
        'description = Column(String)\n    nist_csf = Column(String, nullable=True)\n    assets = relationship("Asset", secondary=risk_asset_table)\n    controls_list = relationship("Control", secondary=risk_control_table)'
    )
    
    # Add status to Treatment
    models_code = models_code.replace(
        'jira_key = Column(String, nullable=True)',
        'jira_key = Column(String, nullable=True)\n    status = Column(String, default="todo")'
    )
    
    with open('app/models.py', 'w', encoding='utf-8') as f:
        f.write(models_code)


# 2. Update app/cli.py
cli_code = '''import typer
import yaml
import os
import json
from sqlalchemy.orm import Session
from app.db import SessionLocal, engine, Base
from app import models, schemas

app = typer.Typer()

def load_yaml(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)

@app.command()
def load():
    typer.echo("Initialisation de la base de données...")
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        # Business Values
        bv_data = load_yaml("grc/si/business_values.yaml")
        for bv in bv_data.get("business_values", []):
            db.merge(models.BusinessValue(id=bv["id"], nom=bv["name"], processus=bv.get("process"), evenement_redoute=bv.get("feared_event"), gravite=bv.get("severity")))
        db.commit()

        # Assets
        assets_data = load_yaml("grc/si/assets.yaml")
        for asset in assets_data.get("assets", []):
            bv_ids = asset.pop("business_values", [])
            db_asset = models.Asset(id=asset["id"], nom=asset["name"], type=asset.get("type"), criticite=asset.get("criticality"))
            db.merge(db_asset)
            db.commit()
            db_asset = db.query(models.Asset).filter_by(id=db_asset.id).first()
            if bv_ids:
                db_asset.valeurs_metier = db.query(models.BusinessValue).filter(models.BusinessValue.id.in_(bv_ids)).all()
        
        # Sources
        a2_data = load_yaml("grc/ebios/w2_sources.yaml")
        for sr in a2_data.get("risk_sources", []):
            db.merge(models.SourceRisque(id=sr["id"], nom=sr["name"], type=sr.get("type"), motivation=sr.get("motivation"), ressources=sr.get("resources")))
        for ov in a2_data.get("objectives", []):
            db.merge(models.ObjectifVise(id=ov["id"], nom=ov["name"], description=ov.get("description")))
        for srov in a2_data.get("sr_ov_pairs", []):
            db.merge(models.CoupleSROV(id=srov["id"], sr_id=srov.get("sr_id"), ov_id=srov.get("ov_id"), pertinence=srov.get("relevance"), description=srov.get("description")))
            
        # Strat
        a3_data = load_yaml("grc/ebios/w3_strategiques.yaml")
        for pp in a3_data.get("stakeholders", []):
            db.merge(models.PartiePrenante(id=pp["id"], nom=pp["name"], type=pp.get("type"), niveau_menace=pp.get("threat_level"), dependance=pp.get("dependency")))
        for sc in a3_data.get("strategic_scenarios", []):
            db.merge(models.ScenarioStrategique(id=sc["id"], nom=sc["name"], srov_id=sc.get("srov_id"), partie_prenante_id=sc.get("stakeholder_id"), vraisemblance=sc.get("likelihood"), description=sc.get("description")))
            
        # ISO Controls (Old schema)
        iso_data = load_yaml("grc/iso27001/annex_a.yaml")
        for ctrl in iso_data.get("controls", []):
            ctrl["id"] = str(ctrl["id"])
            db.merge(models.Control(**ctrl))
        db.commit()

        # Op
        a4_data = load_yaml("grc/ebios/w4_operationnels.yaml")
        for risk in a4_data.get("risks", []):
            asset_ids = risk.pop("assets", [])
            control_ids = risk.pop("controls", [])
            nist = risk.pop("nist_csf", [])
            db_risk = models.ScenarioOperationnel(
                id=risk["id"], nom=risk["name"], sc_strat_id=risk.get("strategic_scenario_id"),
                techniques_attack=json.dumps(risk.get("attack_techniques", [])),
                vraisemblance=risk.get("likelihood"), gravite=risk.get("severity"),
                description=risk.get("description"), nist_csf=json.dumps(nist)
            )
            db.merge(db_risk)
            db.commit()
            db_risk = db.query(models.ScenarioOperationnel).filter_by(id=db_risk.id).first()
            if asset_ids:
                db_risk.assets = db.query(models.Asset).filter(models.Asset.id.in_(asset_ids)).all()
            if control_ids:
                db_risk.controls_list = db.query(models.Control).filter(models.Control.id.in_(control_ids)).all()

        # Mappings (Old schema)
        for mapping_file in ["iso_nis2.yaml", "iso_attack.yaml", "iso_nist.yaml"]:
            mapping_data = load_yaml(f"grc/mappings/{mapping_file}")
            for m in mapping_data.get("mappings", []):
                m["control_id"] = str(m["control_id"])
                db.merge(models.ControlMapping(**m))
                
        # Treatments
        a5_data = load_yaml("grc/ebios/w5_traitements.yaml")
        for tr in a5_data.get("treatments", []):
            db.merge(models.Treatment(
                id=tr["id"], nom=tr["name"], risk_id=tr.get("risk_id"), option=tr.get("option"),
                echeance=tr.get("due_date"), responsable=tr.get("owner"), jira_key=tr.get("jira_key"), status=tr.get("status")
            ))

        db.commit()
        typer.echo("Données GRC chargées avec succès en base !")
    except Exception as e:
        db.rollback()
        typer.echo(f"Erreur lors du chargement : {e}", err=True)
    finally:
        db.close()

from app.services.ingest import ingest_findings
@app.command()
def ingest(source: str = typer.Option(...), file: str = typer.Option(...)):
    db = SessionLocal()
    try:
        count = ingest_findings(db, source, file)
        typer.echo(f"Succès : {count} constats ingérés.")
    finally:
        db.close()

from app.services.jira_client import JiraClient
@app.command()
def export_jira(dry_run: bool = True):
    db = SessionLocal()
    jira = JiraClient()
    try:
        treatments = db.query(models.Treatment).filter(models.Treatment.jira_key == None).all()
        for t in treatments:
            key = jira.export_treatment(t, t.risk, dry_run=dry_run)
            if key and not dry_run:
                t.jira_key = key
                db.commit()
            typer.echo(f"Traitement '{t.nom}' exporté -> {key}")
    finally:
        db.close()

if __name__ == "__main__":
    app()
'''
with open('app/cli.py', 'w', encoding='utf-8') as f:
    f.write(cli_code)
