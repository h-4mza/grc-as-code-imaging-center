def calculate_level(gravite: int, vraisemblance: int) -> str:
    """Calcule le niveau de risque basé sur la matrice 4x4 (plan.md)."""
    # On plafonne à 4 pour correspondre à la règle du plan, même si EBIOS utilise 1-5
    g = min(max(gravite, 1), 4)
    v = min(max(vraisemblance, 1), 4)
    
    score = g * v
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
    v = min(max(vraisemblance, 1), 4)
    if has_high_severity_finding:
        v = min(4, v + 1)
    return v

def calculate_residual(gravite: int, vraisemblance_ajustee: int, maturity_avg: float) -> str:
    """Le niveau résiduel dépend de la maturité moyenne des contrôles."""
    v_res = vraisemblance_ajustee
    
    # Règle de réduction basée sur la maturité (0-5)
    if maturity_avg >= 4.0:
        v_res = max(1, v_res - 2)
    elif maturity_avg >= 2.5:
        v_res = max(1, v_res - 1)
        
    return calculate_level(gravite, v_res)

def get_risk_scores(gravite: int, vraisemblance: int, maturity_avg: float = 0.0, has_high_severity_finding: bool = False):
    """Renvoie un dictionnaire avec le niveau inhérent et résiduel."""
    v_ajustee = adjust_vraisemblance(vraisemblance, has_high_severity_finding)
    inherent_level = calculate_level(gravite, v_ajustee)
    residual_level = calculate_residual(gravite, v_ajustee, maturity_avg)
    
    return {
        "score_inherent": min(gravite, 4) * v_ajustee,
        "niveau_inherent": inherent_level,
        "score_residuel": min(gravite, 4) * min(4, max(1, v_ajustee - (2 if maturity_avg >= 4.0 else (1 if maturity_avg >= 2.5 else 0)))),
        "niveau_residuel": residual_level
    }
