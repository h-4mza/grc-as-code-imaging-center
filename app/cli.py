import typer

app = typer.Typer()

@app.command()
def validate():
    """Valide les schémas YAML et les références croisées."""
    print("Validation des schémas... (à implémenter)")

@app.command()
def load():
    """Charge le YAML en base de données."""
    print("Chargement des données... (à implémenter)")

@app.command()
def ingest(source: str = typer.Option(...), file: str = typer.Option(...)):
    """Ingère des constats techniques."""
    print(f"Ingestion de {file} depuis {source}... (à implémenter)")

@app.command()
def export_jira(dry_run: bool = True):
    """Exporte les traitements vers Jira."""
    print(f"Export Jira (dry-run: {dry_run})... (à implémenter)")

if __name__ == "__main__":
    app()
