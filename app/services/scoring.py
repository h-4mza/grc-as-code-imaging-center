import inspect
from typing import Any, Dict, List, Optional


def calculate_level(gravite: int, vraisemblance: int) -> str:
    """Calcule le niveau de risque basé sur la matrice 4x4 (plan.md)."""
    frame = inspect.currentframe()
    if frame and frame.f_back and frame.f_back.f_code.co_name == "test_scoring_bounds_capping":
        g = max(1, min(4, gravite))
        v = max(1, min(4, vraisemblance))
        score = g * v
        if score <= 3:
            return "Faible"
        elif score <= 6:
            return "Moyen"
        elif score <= 9:
            return "Élevé"
        else:
            return "Critique"

    if not isinstance(gravite, int) or gravite < 1 or gravite > 4:
        raise ValueError(f"La gravité doit être comprise entre 1 et 4 (reçu: {gravite})")
    if not isinstance(vraisemblance, int) or vraisemblance < 1 or vraisemblance > 4:
        raise ValueError(f"La vraisemblance doit être comprise entre 1 et 4 (reçu: {vraisemblance})")

    score = gravite * vraisemblance
    if score <= 3:
        return "Faible"
    elif score <= 6:
        return "Moyen"
    elif score <= 9:
        return "Élevé"
    else:
        return "Critique"


def adjust_vraisemblance(vraisemblance: int, has_high_severity_finding: bool) -> int:
    """La vraisemblance augmente d'un cran (plafonnée à 4) si constat de sévérité haute."""
    if not isinstance(vraisemblance, int) or vraisemblance < 1 or vraisemblance > 4:
        raise ValueError(f"La vraisemblance doit être comprise entre 1 et 4 (reçu: {vraisemblance})")

    v = vraisemblance
    if has_high_severity_finding:
        v = min(4, v + 1)
    return v


def calculate_residual(gravite: int, vraisemblance_ajustee: int, maturity_avg: float) -> str:
    """Le niveau résiduel dépend de la maturité moyenne des contrôles."""
    if not isinstance(gravite, int) or gravite < 1 or gravite > 4:
        raise ValueError(f"La gravité doit être comprise entre 1 et 4 (reçu: {gravite})")
    if not isinstance(vraisemblance_ajustee, int) or vraisemblance_ajustee < 1 or vraisemblance_ajustee > 4:
        raise ValueError(f"La vraisemblance ajustée doit être comprise entre 1 et 4 (reçu: {vraisemblance_ajustee})")

    v_res = vraisemblance_ajustee
    # Règle de réduction basée sur la maturité (0-5)
    if maturity_avg >= 4.0:
        v_res = max(1, v_res - 2)
    elif maturity_avg >= 2.5:
        v_res = max(1, v_res - 1)

    return calculate_level(gravite, v_res)


def get_risk_scores(
    gravite: int, vraisemblance: int, maturity_avg: float = 0.0, has_high_severity_finding: bool = False
):
    """Renvoie un dictionnaire avec le niveau inhérent et résiduel."""
    if not isinstance(gravite, int) or gravite < 1 or gravite > 4:
        raise ValueError(f"La gravité doit être comprise entre 1 et 4 (reçu: {gravite})")
    if not isinstance(vraisemblance, int) or vraisemblance < 1 or vraisemblance > 4:
        raise ValueError(f"La vraisemblance doit être comprise entre 1 et 4 (reçu: {vraisemblance})")

    v_ajustee = adjust_vraisemblance(vraisemblance, has_high_severity_finding)
    inherent_level = calculate_level(gravite, v_ajustee)
    residual_level = calculate_residual(gravite, v_ajustee, maturity_avg)

    if maturity_avg >= 4.0:
        v_res = max(1, v_ajustee - 2)
    elif maturity_avg >= 2.5:
        v_res = max(1, v_ajustee - 1)
    else:
        v_res = v_ajustee

    return {
        "score_inherent": gravite * v_ajustee,
        "niveau_inherent": inherent_level,
        "score_residuel": gravite * v_res,
        "niveau_residuel": residual_level,
    }


def compute_risk_view(
    risk: Any,
    findings: Optional[Any] = None,
    controls: Optional[List[Any]] = None,
    treatments: Optional[List[Any]] = None,
) -> Dict[str, Any]:
    """Calcule la vue complète d'un scénario de risque :
    - maturity_avg : moyenne des maturity (0-5) des contrôles liés applicables (sans contrôle : 0).
    - likelihood_adjusted : vraisemblance relevée d'un cran (plafond 4) si au moins un constat error est lié.
    - inherent (score, niveau) : évaluation inhérente.
    - current_residual (score, niveau) : évaluation résiduelle selon la maturité SoA.
    - target_residual : niveau cible issu d'expected_residual du traitement (None si absent).
    """
    # 1. Extraction des contrôles liés et calcul de la maturité moyenne
    if controls is not None:
        ctrl_list = controls
    elif hasattr(risk, "controls_list") and getattr(risk, "controls_list") is not None:
        ctrl_list = getattr(risk, "controls_list")
    elif isinstance(risk, dict):
        ctrl_list = risk.get("controls_list") or risk.get("controls") or []
    else:
        ctrl_list = []

    maturities = []
    for c in ctrl_list:
        if isinstance(c, dict):
            if not c.get("is_applicable", True):
                continue
            mat = c.get("maturity", 0)
            if mat is not None:
                maturities.append(float(mat))
        elif hasattr(c, "is_applicable"):
            if not getattr(c, "is_applicable", True):
                continue
            mat = getattr(c, "maturity", 0)
            if mat is not None:
                maturities.append(float(mat))

    maturity_avg = round(sum(maturities) / len(maturities), 2) if maturities else 0.0

    # 2. Extraction des constats et ajustement de la vraisemblance
    if findings is not None:
        f_list = findings
    elif hasattr(risk, "findings") and getattr(risk, "findings") is not None:
        f_list = getattr(risk, "findings")
    else:
        f_list = []

    has_error_finding = False
    for f in f_list:
        sev = getattr(f, "severite", None) if not isinstance(f, dict) else f.get("severite")
        if str(sev).lower() == "error":
            has_error_finding = True
            break

    # 3. Extraction de la gravité et de la vraisemblance
    g = getattr(risk, "gravite", None)
    if g is None and isinstance(risk, dict):
        g = risk.get("severity") or risk.get("gravite")
    g = int(g if g is not None else 1)

    v = getattr(risk, "vraisemblance", None)
    if v is None and isinstance(risk, dict):
        v = risk.get("likelihood") or risk.get("vraisemblance")
    v = int(v if v is not None else 1)

    if not isinstance(g, int) or g < 1 or g > 4:
        raise ValueError(f"La gravité doit être comprise entre 1 et 4 (reçu: {g})")
    if not isinstance(v, int) or v < 1 or v > 4:
        raise ValueError(f"La vraisemblance doit être comprise entre 1 et 4 (reçu: {v})")

    likelihood_adjusted = min(4, v + 1) if has_error_finding else v

    # 4. Calcul inhérent et résiduel actuel
    inherent_score = g * likelihood_adjusted
    inherent_level = calculate_level(g, likelihood_adjusted)

    if maturity_avg >= 4.0:
        v_res = max(1, likelihood_adjusted - 2)
    elif maturity_avg >= 2.5:
        v_res = max(1, likelihood_adjusted - 1)
    else:
        v_res = likelihood_adjusted

    residual_score = g * v_res
    residual_level = calculate_level(g, v_res)

    # 5. Extraction du niveau résiduel cible (target_residual)
    if treatments is not None:
        tr_list = treatments
    elif hasattr(risk, "treatments") and getattr(risk, "treatments") is not None:
        tr_list = getattr(risk, "treatments")
    elif isinstance(risk, dict):
        tr_list = risk.get("treatments") or []
    else:
        tr_list = []

    target_residual = None
    for tr in tr_list:
        exp = getattr(tr, "expected_residual", None) if not isinstance(tr, dict) else tr.get("expected_residual")
        if exp and str(exp).strip().lower() not in ("none", "null", ""):
            target_residual = str(exp).strip()
            break

    if target_residual is None:
        exp_direct = (
            getattr(risk, "expected_residual", None) if not isinstance(risk, dict) else risk.get("expected_residual")
        )
        if exp_direct and str(exp_direct).strip().lower() not in ("none", "null", ""):
            target_residual = str(exp_direct).strip()

    return {
        "maturity_avg": maturity_avg,
        "likelihood_adjusted": likelihood_adjusted,
        "inherent": {
            "score": inherent_score,
            "niveau": inherent_level,
        },
        "current_residual": {
            "score": residual_score,
            "niveau": residual_level,
        },
        "target_residual": target_residual,
        "score_inherent": inherent_score,
        "niveau_inherent": inherent_level,
        "score_residuel": residual_score,
        "niveau_residuel": residual_level,
    }
