# GRC-as-code : Imaging Center

Outil de pilotage GRC as-code (EBIOS RM, ISO 27001, NIS2) pour un centre d'imagerie médicale fictif.

## Architecture

- **PostgreSQL** : Base de données
- **FastAPI** : API de pilotage
- **Streamlit** : Dashboard
- **YAML** : Source de vérité des données GRC

## Démarrage rapide

```bash
make demo
```
L'API sera disponible sur [http://localhost:8000/docs](http://localhost:8000/docs).
Le Dashboard sera disponible sur [http://localhost:8501](http://localhost:8501).
