"""
tests/test_load_and_scoring.py

Tests de validation de la commande grc load et de non-régression du scoring :
- Ingestion des YAML sur SQLite en mémoire.
- Vérification de l'intégrité relationnelle (12 risques, contrôles, traitements, sources, parties prenantes).
- Non-régression de la matrice de scoring EBIOS RM (G x V).
"""

import pytest
from sqlalchemy import create_engine, select
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from typer.testing import CliRunner

from app import cli, db
from app.cli import app
from app.models import (
    Base,
    CoupleSROV,
    PartiePrenante,
    ScenarioOperationnel,
    ScenarioStrategique,
    SourceRisque,
    Treatment,
    risk_control_table,
)
from app.services.scoring import calculate_level

runner = CliRunner()


@pytest.fixture
def sqlite_in_memory(monkeypatch):
    """Configure un moteur SQLite en mémoire partagé pour l'exécution de la CLI grc load."""
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(bind=engine)
    session_factory = sessionmaker(autocommit=False, autoflush=False, bind=engine)

    monkeypatch.setattr(cli, "engine", engine)
    monkeypatch.setattr(cli, "SessionLocal", session_factory)
    monkeypatch.setattr(db, "engine", engine)
    monkeypatch.setattr(db, "SessionLocal", session_factory)

    yield session_factory

    engine.dispose()


def test_grc_load_in_memory_sqlite(sqlite_in_memory):
    """
    Exécute grc load sur SQLite en mémoire et vérifie :
    - Présence exacte de 12 risques opérationnels.
    - Chaque risque est rattaché à un scénario stratégique parent.
    - Chaque risque a au moins 1 contrôle lié (table risk_control non vide).
    - Chaque risque a au moins 1 traitement associé.
    - Aucune source de risque ou partie prenante n'est orpheline.
    """
    result = runner.invoke(app, ["load"])
    assert result.exit_code == 0, f"Erreur lors de grc load : {result.stdout} {result.stderr}"

    session = sqlite_in_memory()
    try:
        # 1. Exactement 12 risques opérationnels
        risks = session.query(ScenarioOperationnel).all()
        assert len(risks) == 12, f"Attendu 12 risques, trouvé {len(risks)}"

        # 2. Vérification des liaisons pour chaque risque
        for risk in risks:
            # Parent stratégique
            assert risk.sc_strat_id is not None, f"Le risque {risk.id} n'a pas de sc_strat_id"
            assert risk.scenario_strategique is not None, f"Le risque {risk.id} n'a pas de scénario stratégique lié"

            # Contrôles liés
            assert len(risk.controls_list) >= 1, f"Le risque {risk.id} n'a aucun contrôle lié dans controls_list"

            # Au moins 1 traitement
            treatments = session.query(Treatment).filter_by(risk_id=risk.id).all()
            assert len(treatments) >= 1, f"Le risque {risk.id} n'a aucun traitement dans la table treatments"

        # Table d'association risk_control non vide au global
        rc_rows = session.execute(select(risk_control_table)).all()
        assert len(rc_rows) > 0, "La table d'association risk_control est vide"

        # 3. Aucune source de risque orpheline (toutes utilisées dans CoupleSROV)
        all_sources = session.query(SourceRisque).all()
        referenced_source_ids = {row[0] for row in session.query(CoupleSROV.sr_id).distinct().all()}
        orphan_sources = [s.id for s in all_sources if s.id not in referenced_source_ids]
        assert len(orphan_sources) == 0, f"Sources de risque orphelines détectées : {orphan_sources}"

        # 4. Aucune partie prenante orpheline (toutes utilisées dans ScenarioStrategique)
        all_stakeholders = session.query(PartiePrenante).all()
        referenced_stakeholder_ids = {
            row[0] for row in session.query(ScenarioStrategique.partie_prenante_id).distinct().all() if row[0]
        }
        orphan_stakeholders = [p.id for p in all_stakeholders if p.id not in referenced_stakeholder_ids]
        assert len(orphan_stakeholders) == 0, f"Parties prenantes orphelines détectées : {orphan_stakeholders}"

    finally:
        session.close()


def test_non_regression_risk_levels(sqlite_in_memory):
    """
    Test de non-régression :
    Vérifie que les niveaux de R-01..R-12 correspondent exactement à la table de cotation
    attendue selon la formule G x V et les seuils de scoring.py :
    - R-01: 4 x 4 = 16 -> Critique
    - R-02: 4 x 3 = 12 -> Critique
    - R-03: 4 x 2 = 8  -> Élevé
    - R-04: 3 x 3 = 9  -> Élevé
    - R-05: 4 x 2 = 8  -> Élevé
    - R-06: 2 x 3 = 6  -> Moyen
    - R-07: 4 x 2 = 8  -> Élevé
    - R-08: 4 x 2 = 8  -> Élevé
    - R-09: 3 x 2 = 6  -> Moyen
    - R-10: 4 x 3 = 12 -> Critique
    - R-11: 3 x 3 = 9  -> Élevé
    - R-12: 2 x 3 = 6  -> Moyen
    """
    result = runner.invoke(app, ["load"])
    assert result.exit_code == 0

    expected_ratings = {
        "R-01": {"gravite": 4, "vraisemblance": 4, "score": 16, "level": "Critique"},
        "R-02": {"gravite": 4, "vraisemblance": 3, "score": 12, "level": "Critique"},
        "R-03": {"gravite": 4, "vraisemblance": 2, "score": 8, "level": "Élevé"},
        "R-04": {"gravite": 3, "vraisemblance": 3, "score": 9, "level": "Élevé"},
        "R-05": {"gravite": 4, "vraisemblance": 2, "score": 8, "level": "Élevé"},
        "R-06": {"gravite": 2, "vraisemblance": 3, "score": 6, "level": "Moyen"},
        "R-07": {"gravite": 4, "vraisemblance": 2, "score": 8, "level": "Élevé"},
        "R-08": {"gravite": 4, "vraisemblance": 2, "score": 8, "level": "Élevé"},
        "R-09": {"gravite": 3, "vraisemblance": 2, "score": 6, "level": "Moyen"},
        "R-10": {"gravite": 4, "vraisemblance": 3, "score": 12, "level": "Critique"},
        "R-11": {"gravite": 3, "vraisemblance": 3, "score": 9, "level": "Élevé"},
        "R-12": {"gravite": 2, "vraisemblance": 3, "score": 6, "level": "Moyen"},
    }

    session = sqlite_in_memory()
    try:
        risks = session.query(ScenarioOperationnel).all()
        risk_map = {r.id: r for r in risks}

        for r_id, exp in expected_ratings.items():
            assert r_id in risk_map, f"Risque {r_id} absent de la base"
            risk = risk_map[r_id]

            assert risk.gravite == exp["gravite"], (
                f"Risque {r_id}: gravité attendue {exp['gravite']}, trouvée {risk.gravite}"
            )
            assert risk.vraisemblance == exp["vraisemblance"], (
                f"Risque {r_id}: vraisemblance attendue {exp['vraisemblance']}, trouvée {risk.vraisemblance}"
            )

            score = risk.gravite * risk.vraisemblance
            assert score == exp["score"], f"Risque {r_id}: score attendu {exp['score']}, calculé {score}"

            level = calculate_level(risk.gravite, risk.vraisemblance)
            assert level == exp["level"], f"Risque {r_id}: niveau attendu {exp['level']}, calculé {level}"
    finally:
        session.close()
