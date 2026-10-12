import typer

from app import models
from app.db import Base, SessionLocal, engine
from app.services.ingest import ingest_findings
from app.services.jira_client import JiraClient
from app.services.loader import load_grc_idempotent, relink_findings
from app.services.validate import validate_grc_yaml

app = typer.Typer()


@app.command()
def load(
    grc_dir: str = typer.Option("grc", "--grc-dir", help="Dossier racine des référentiels GRC YAML"),
):
    """Charge de manière idempotente les référentiels GRC YAML en base."""
    typer.echo(f"🔍 Validation préalable des référentiels YAML GRC dans '{grc_dir}'...")
    report = validate_grc_yaml(grc_dir=grc_dir)
    if not report.is_valid:
        typer.echo(f"\n❌ Validation échouée : {len(report.errors)} erreur(s) détectée(s) :\n", err=True)
        for i, err in enumerate(report.errors, 1):
            typer.echo(f"  {i}. {err}", err=True)
        typer.echo("\nÉchec du chargement : YAML invalide.", err=True)
        raise typer.Exit(code=1)

    # Création des tables si besoin (jamais drop_all)
    Base.metadata.create_all(bind=engine)

    db = SessionLocal()
    try:
        counts = load_grc_idempotent(db, grc_dir=grc_dir)
        db.commit()
        typer.echo("Données GRC chargées avec succès en base !")
        typer.echo(
            f"  - {counts['risks']} scénarios de risque, {counts['controls']} contrôles, "
            f"{counts['treatments']} traitements"
        )
        if counts["relinked_findings"] > 0:
            typer.echo(f"  - {counts['relinked_findings']} constat(s) rattaché(s)")
    except Exception as e:
        db.rollback()
        typer.echo(f"Erreur lors du chargement : {e}", err=True)
        raise typer.Exit(code=1)
    finally:
        db.close()


@app.command()
def reset(
    yes: bool = typer.Option(
        False,
        "--yes",
        "-y",
        help="Confirmer la réinitialisation sans invite interactive",
    ),
):
    """Réinitialise complètement la base de données (drop_all puis create_all)."""
    if not yes:
        confirm = typer.confirm(
            "⚠️ Attention : Cette opération va supprimer toutes les tables et données en base. Continuer ?",
            default=False,
        )
        if not confirm:
            typer.echo("Opération annulée.")
            raise typer.Abort()

    typer.echo("Initialisation de la base de données...")
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    typer.echo("✅ Base de données réinitialisée avec succès !")


@app.command()
def relink(
    grc_dir: str = typer.Option("grc", "--grc-dir", help="Dossier racine des référentiels GRC YAML"),
):
    """Recalcule les liens constat -> scénario et constat -> contrôle."""
    db = SessionLocal()
    try:
        count = relink_findings(db)
        db.commit()
        typer.echo(f"✅ {count} constat(s) rattaché(s) avec succès aux scénarios et contrôles.")
    except Exception as e:
        db.rollback()
        typer.echo(f"Erreur lors du rattachement : {e}", err=True)
        raise typer.Exit(code=1)
    finally:
        db.close()


@app.command()
def ingest(source: str = typer.Option(...), file: str = typer.Option(...)):
    db = SessionLocal()
    try:
        count = ingest_findings(db, source, file)
        typer.echo(f"Succès : {count} constats ingérés.")
    finally:
        db.close()


@app.command()
def export_jira(
    project: str = typer.Option(None, "--project", help="Clé du projet Jira"),
    dry_run: bool = typer.Option(
        True, "--dry-run/--no-dry-run", help="Mode simulation sans appel API (défaut : dry-run)"
    ),
):
    db = SessionLocal()
    jira = JiraClient(project_key=project)
    try:
        treatments = db.query(models.Treatment).filter(models.Treatment.jira_key.is_(None)).all()
        for t in treatments:
            key = jira.export_treatment(t, t.risk, dry_run=dry_run)
            if key and not dry_run:
                t.jira_key = key
                db.commit()
            typer.echo(f"Traitement '{t.nom}' exporté -> {key}")
    finally:
        db.close()


@app.command()
def validate(
    grc_dir: str = typer.Option("grc", "--grc-dir", "--dir", "-d", help="Dossier racine des référentiels GRC YAML"),
):
    """Valide l'intégrité, la complétude et la cohérence des référentiels GRC YAML."""
    typer.echo(f"🔍 Validation des référentiels YAML GRC dans '{grc_dir}'...")
    report = validate_grc_yaml(grc_dir=grc_dir)

    # Affichage du calcul des niveaux de risque
    if report.risk_summaries:
        typer.echo("\n📊 Évaluation des Scénarios de Risque (scoring.py) :")
        typer.echo("-" * 88)
        typer.echo(f"{'ID':<6} | {'Nom du Risque':<35} | {'Inhérent':<14} | {'Résiduel':<14} | {'Maturité':<8}")
        typer.echo("-" * 88)
        for r in report.risk_summaries:
            nom_court = (r.name[:32] + "...") if len(r.name) > 35 else r.name
            inh_str = f"{r.niveau_inherent} ({r.score_inherent})"
            res_str = f"{r.niveau_residuel} ({r.score_residuel})"
            mat_str = f"{r.maturity_avg}/5"
            typer.echo(f"{r.id:<6} | {nom_court:<35} | {inh_str:<14} | {res_str:<14} | {mat_str:<8}")
        typer.echo("-" * 88)

    if not report.is_valid:
        typer.echo(f"\n❌ Validation échouée : {len(report.errors)} erreur(s) détectée(s) :\n", err=True)
        for i, err in enumerate(report.errors, 1):
            typer.echo(f"  {i}. {err}", err=True)
        typer.echo("\nÉchec de la validation GRC.", err=True)
        raise typer.Exit(code=1)

    typer.echo("\n✅ Succès : Tous les fichiers YAML GRC sont valides et cohérents !")


if __name__ == "__main__":
    app()
