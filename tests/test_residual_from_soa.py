"""
tests/test_residual_from_soa.py

Tests validant le calcul du risque résiduel unifié via SoA (ISO 27001) et compute_risk_view :
1. Risque sans contrôle lié : résiduel = inhérent (maturité 0.0).
2. Maturité 4.5 (>= 4.0) : réduction de la vraisemblance de 2 crans.
3. Constat de sévérité error : augmentation de la vraisemblance de 1 cran (plafonnée à 4).
4. Contrôle non applicable (is_applicable=False) ignoré dans la moyenne.
5. Cohérence absolue : l'API /kpi/heatmap et la CLI grc validate retournent exactement les mêmes niveaux.
"""

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app import cli, db
from app.main import get_kpi_heatmap
from app.models import Base, Control, Finding, ScenarioOperationnel
from app.services.loader import load_grc_idempotent
from app.services.scoring import compute_risk_view
from app.services.validate import validate_grc_yaml


@pytest.fixture
def sqlite_test_db(monkeypatch):
    """Initialise un moteur SQLite en mémoire partagé avec les données GRC."""
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

    session = session_factory()
    load_grc_idempotent(session, grc_dir="grc")
    session.commit()
    session.close()

    yield session_factory

    engine.dispose()


def test_risk_without_controls_residual_equals_inherent():
    """Un risque sans contrôle lié a une maturité de 0.0 et son risque résiduel est égal à son inhérent."""
    risk = ScenarioOperationnel(
        id="R-TEST",
        nom="Risque de test sans contrôle",
        gravite=4,
        vraisemblance=3,
    )
    risk.controls_list = []
    risk.findings = []
    risk.treatments = []

    view = compute_risk_view(risk, findings=[])

    assert view["maturity_avg"] == 0.0
    assert view["likelihood_adjusted"] == 3
    assert view["inherent"]["score"] == 12
    assert view["inherent"]["niveau"] == "Critique"
    assert view["current_residual"]["score"] == 12
    assert view["current_residual"]["niveau"] == "Critique"
    assert view["current_residual"]["score"] == view["inherent"]["score"]
    assert view["current_residual"]["niveau"] == view["inherent"]["niveau"]


def test_high_maturity_4_5_reduces_two_steps():
    """Une maturité >= 4.0 réduit la vraisemblance de 2 crans."""
    c1 = Control(id="c1", name="Contrôle 1", is_applicable=True, maturity=4)
    c2 = Control(id="c2", name="Contrôle 2", is_applicable=True, maturity=5)

    risk = ScenarioOperationnel(
        id="R-TEST2",
        nom="Risque test haute maturité",
        gravite=4,
        vraisemblance=4,
    )
    risk.controls_list = [c1, c2]
    risk.findings = []
    risk.treatments = []

    view = compute_risk_view(risk, findings=[])

    assert view["maturity_avg"] == 4.5
    assert view["inherent"]["score"] == 16
    assert view["inherent"]["niveau"] == "Critique"
    # Vraisemblance 4 réduite de 2 crans -> 2 -> score 4 * 2 = 8 -> Élevé
    assert view["current_residual"]["score"] == 8
    assert view["current_residual"]["niveau"] == "Élevé"


def test_error_finding_increases_likelihood_by_one():
    """Un constat ouvert de sévérité error augmente la vraisemblance d'un cran (plafonnée à 4)."""
    risk = ScenarioOperationnel(
        id="R-TEST3",
        nom="Risque test avec constat error",
        gravite=3,
        vraisemblance=2,
    )
    risk.controls_list = []
    finding_error = Finding(id=1, severite="error", source="sarif", date="2026-10-12")
    risk.findings = [finding_error]
    risk.treatments = []

    view = compute_risk_view(risk, findings=[finding_error])

    assert view["likelihood_adjusted"] == 3  # 2 + 1
    assert view["inherent"]["score"] == 9  # 3 * 3
    assert view["inherent"]["niveau"] == "Élevé"

    # Plafonnement à 4 si vraisemblance initiale = 4
    risk_max = ScenarioOperationnel(id="R-MAX", nom="Max", gravite=4, vraisemblance=4)
    risk_max.controls_list = []
    view_max = compute_risk_view(risk_max, findings=[finding_error])
    assert view_max["likelihood_adjusted"] == 4


def test_not_applicable_control_is_ignored():
    """Un contrôle non applicable (is_applicable=False) est ignoré dans le calcul de la maturité."""
    c_app = Control(id="c_app", name="Applicable", is_applicable=True, maturity=4)
    c_na = Control(id="c_na", name="Non applicable", is_applicable=False, maturity=0)

    risk = ScenarioOperationnel(
        id="R-TEST4",
        nom="Risque test contrôle non applicable",
        gravite=3,
        vraisemblance=3,
    )
    risk.controls_list = [c_app, c_na]
    risk.findings = []
    risk.treatments = []

    view = compute_risk_view(risk, findings=[])

    # La moyenne doit être 4.0 et non (4 + 0) / 2 = 2.0
    assert view["maturity_avg"] == 4.0
    # Maturité 4.0 -> réduction de 2 crans : V = 3 -> V_res = 1 -> score 3 * 1 = 3 -> Faible
    assert view["current_residual"]["score"] == 3
    assert view["current_residual"]["niveau"] == "Faible"


def test_kpi_heatmap_and_grc_validate_match_levels(sqlite_test_db):
    """Vérifie que /kpi/heatmap et grc validate calculent exactement les mêmes niveaux."""
    session = sqlite_test_db()
    try:
        api_data = get_kpi_heatmap(db=session)
    finally:
        session.close()

    assert len(api_data) == 12
    api_map = {item["id"]: item for item in api_data}

    # 2. Niveaux calculés par grc validate
    report = validate_grc_yaml("grc")
    assert len(report.risk_summaries) == 12
    val_map = {item.id: item for item in report.risk_summaries}

    # 3. Comparaison stricte risque par risque
    assert set(api_map.keys()) == set(val_map.keys())
    for r_id in api_map:
        api_risk = api_map[r_id]
        val_risk = val_map[r_id]

        assert api_risk["niveau_inherent"] == val_risk.niveau_inherent, (
            f"Risque {r_id} : incohérence inhérente API ({api_risk['niveau_inherent']}) "
            f"vs Validate ({val_risk.niveau_inherent})"
        )
        assert api_risk["niveau_residuel"] == val_risk.niveau_residuel, (
            f"Risque {r_id} : incohérence résiduelle API ({api_risk['niveau_residuel']}) "
            f"vs Validate ({val_risk.niveau_residuel})"
        )
        assert api_risk["score_inherent"] == val_risk.score_inherent
        assert api_risk["score_residuel"] == val_risk.score_residuel
        assert api_risk["maturity_avg"] == val_risk.maturity_avg
        assert api_risk["target_residual"] == val_risk.target_residual
