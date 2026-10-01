import pytest
from app.services.scoring import calculate_level, adjust_vraisemblance, calculate_residual, get_risk_scores

def test_calculate_level():
    assert calculate_level(1, 1) == "Faible"
    assert calculate_level(2, 1) == "Faible"
    assert calculate_level(2, 2) == "Moyen"
    assert calculate_level(2, 3) == "Moyen"
    assert calculate_level(3, 3) == "Élevé"
    assert calculate_level(4, 3) == "Critique"
    assert calculate_level(4, 4) == "Critique"
    # Test capping
    assert calculate_level(5, 5) == "Critique" 

def test_adjust_vraisemblance():
    assert adjust_vraisemblance(3, False) == 3
    assert adjust_vraisemblance(3, True) == 4
    assert adjust_vraisemblance(4, True) == 4

def test_calculate_residual():
    # gravite 4, v 4 -> 16 (Critique)
    assert calculate_residual(4, 4, 0.0) == "Critique"
    # maturity 3.0 -> v reduced by 1 -> v=3 -> score 12 (Critique)
    assert calculate_residual(4, 4, 3.0) == "Critique"
    # maturity 4.5 -> v reduced by 2 -> v=2 -> score 8 (Élevé)
    assert calculate_residual(4, 4, 4.5) == "Élevé"
    # gravite 3, v 3 -> 9 (Élevé)
    # maturity 3.0 -> v reduced by 1 -> v=2 -> score 6 (Moyen)
    assert calculate_residual(3, 3, 3.0) == "Moyen"

def test_get_risk_scores():
    res = get_risk_scores(3, 2, maturity_avg=3.0, has_high_severity_finding=True)
    # v = 2 -> adjust -> 3. Inhérent: 3*3 = 9 (Élevé)
    # Maturité 3.0 -> v_res = 3-1 = 2. Résiduel: 3*2 = 6 (Moyen)
    assert res["niveau_inherent"] == "Élevé"
    assert res["niveau_residuel"] == "Moyen"
    assert res["score_inherent"] == 9
    assert res["score_residuel"] == 6
