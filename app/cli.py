import typer
import yaml
import os
import json
from sqlalchemy.orm import Session
from app.db import SessionLocal, engine, Base
from app import models, schemas

app = typer.Typer()

@app.command()
def validate():
    """Valide les schémas YAML (A implémenter)."""
    typer.echo("Validation des schémas... (à implémenter)")

def load_yaml(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)

@app.command()
def load():
    """Charge le YAML en base de données."""
    typer.echo("Initialisation de la base de données...")
    Base.metadata.create_all(bind=engine)
    
    db: Session = SessionLocal()
    
    try:
        # Load Business Values
        bv_data = load_yaml("grc/si/business_values.yaml")
        for bv in bv_data.get("business_values", []):
            db.merge(models.BusinessValue(**bv))
            
        # Load Assets
        assets_data = load_yaml("grc/si/assets.yaml")
        for asset in assets_data.get("assets", []):
            bv_ids = asset.pop("valeurs_metier_liees", [])
            db_asset = models.Asset(**asset)
            db.merge(db_asset)
            db.commit() # Commit pour avoir l'objet en base
            
            # Associate BVs
            db_asset = db.query(models.Asset).filter_by(id=db_asset.id).first()
            db_asset.valeurs_metier = db.query(models.BusinessValue).filter(models.BusinessValue.id.in_(bv_ids)).all()
            
        # Load A2 (SR, OV, SROV)
        a2_data = load_yaml("grc/ebios/w2_sources.yaml")
        for sr in a2_data.get("sources_risques", []): db.merge(models.SourceRisque(**sr))
        for ov in a2_data.get("objectifs_vises", []): db.merge(models.ObjectifVise(**ov))
        for srov in a2_data.get("couples_sr_ov", []): db.merge(models.CoupleSROV(**srov))
        
        # Load A3 (Parties Prenantes, SC Strat)
        a3_data = load_yaml("grc/ebios/w3_strategiques.yaml")
        for pp in a3_data.get("parties_prenantes", []): db.merge(models.PartiePrenante(**pp))
        for sc in a3_data.get("scenarios_strategiques", []): db.merge(models.ScenarioStrategique(**sc))
        
        # Load A4 (SC Op)
        a4_data = load_yaml("grc/ebios/w4_operationnels.yaml")
        for sc_op in a4_data.get("scenarios_operationnels", []):
            sc_op["techniques_attack"] = json.dumps(sc_op["techniques_attack"])
            db.merge(models.ScenarioOperationnel(**sc_op))
            
        # Load ISO Controls
        iso_data = load_yaml("grc/iso27001/annex_a.yaml")
        for ctrl in iso_data.get("controls", []):
            # Check ID as string
            ctrl["id"] = str(ctrl["id"])
            db.merge(models.Control(**ctrl))
            
        # Load Mappings
        for mapping_file in ["iso_nis2.yaml", "iso_attack.yaml", "iso_nist.yaml"]:
            mapping_data = load_yaml(f"grc/mappings/{mapping_file}")
            for m in mapping_data.get("mappings", []):
                # Ensure control_id is string
                m["control_id"] = str(m["control_id"])
                db.merge(models.ControlMapping(**m))
                
        # Load A5 (Traitements)
        a5_data = load_yaml("grc/ebios/w5_traitements.yaml")
        for tr in a5_data.get("traitements", []):
            db.merge(models.Treatment(**tr))

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
    """Ingère des constats techniques."""
    typer.echo(f"Ingestion de {file} depuis {source}...")
    db: Session = SessionLocal()
    try:
        count = ingest_findings(db, source, file)
        typer.echo(f"Succès : {count} constats ingérés et rattachés.")
    except Exception as e:
        typer.echo(f"Erreur lors de l'ingestion : {e}", err=True)
    finally:
        db.close()

from app.services.jira_client import JiraClient

@app.command()
def export_jira(dry_run: bool = True):
    """Exporte les traitements vers Jira."""
    typer.echo(f"Export Jira (dry-run: {dry_run})...")
    db: Session = SessionLocal()
    jira = JiraClient()
    try:
        # On sélectionne les traitements qui n'ont pas encore de clé Jira (idempotence)
        treatments = db.query(models.Treatment).filter(models.Treatment.jira_key == None).all()
        if not treatments:
            typer.echo("Aucun nouveau traitement à exporter vers Jira.")
            return

        for t in treatments:
            key = jira.export_treatment(t, t.risk, dry_run=dry_run)
            if key and not dry_run:
                t.jira_key = key
                db.commit()
            typer.echo(f"Traitement '{t.nom}' exporté avec succès -> {key}")
            
    except Exception as e:
        typer.echo(f"Erreur lors de l'export Jira : {e}", err=True)
    finally:
        db.close()

if __name__ == "__main__":
    app()
