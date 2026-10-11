"""
tests/test_scoring_et_ingestion.py

Tests unitaires et d'intégration validant la logique mathématique GRC :
- Calcul de risque inhérent et résiduel selon la matrice 4x4 (EBIOS RM).
- Dégradation dynamique de la maturité des contrôles ISO en cas de failles SARIF.
- Augmentation mathématique du risque résiduel suite à l'ingestion d'un constat critique.
- Rattachement automatique technique MITRE ATT&CK <-> Scénarios de risque <-> ISO 8.8.
"""

import json
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.models import Base, ScenarioOperationnel, Control, Finding
from app.parsers.sarif import parse_sarif
from app.services.ingest import ingest_findings
from app.services.scoring import (
    calculate_level,
    adjust_vraisemblance,
    calculate_residual,
    get_risk_scores,
)


# ==============================================================================
# Fixtures pour base de données isolée en mémoire
# ==============================================================================

@pytest.fixture
def db_session():
    """Crée une base SQLite éphémère en mémoire pour les tests d'ingestion."""
    engine = create_engine("sqlite:///:memory:", echo=False)
    Base.metadata.create_all(bind=engine)
    Session = sessionmaker(bind=engine)
    session = Session()

    # Création du contrôle ISO 8.8 attendu par le rattachement de vulnérabilités
    ctrl_8_8 = Control(
        id="8.8",
        name="Gestion des vulnérabilités techniques",
        theme="Technologique",
        is_applicable=True,
        status="partial",
        maturity=2,
    )
    session.add(ctrl_8_8)

    # Création d'un scénario de risque EBIOS R-02 avec technique ATT&CK T1190
    risk_r02 = ScenarioOperationnel(
        id="R-02",
        nom="Exfiltration de données via faille VPN",
        vraisemblance=3,
        gravite=4,
        techniques_attack=json.dumps(["T1190", "T1005"]),
    )
    session.add(risk_r02)
    session.commit()

    yield session

    session.close()


@pytest.fixture
def sample_sarif_file(tmp_path):
    """Génère un rapport SARIF temporaire simulant un scan Trivy avec une CVE critique."""
    sarif_data = {
        "version": "2.1.0",
        "runs": [
            {
                "tool": {"driver": {"name": "Trivy"}},
                "results": [
                    {
                        "ruleId": "CVE-2024-1234",
                        "level": "error",
                        "properties": {
                            "tags": ["T1190"],
                            "asset_id": "ast_vpn",
                        },
                        "message": {
                            "text": "Exécution de code à distance (RCE) sur passerelle VPN"
                        },
                    }
                ],
            }
        ],
    }
    sarif_path = tmp_path / "test_scan.sarif"
    with open(sarif_path, "w", encoding="utf-8") as f:
        json.dump(sarif_data, f)
    return str(sarif_path)


# ==============================================================================
# 1. Tests unitaires : Matrice de Risque EBIOS RM & Plafonnement
# ==============================================================================

def test_scoring_baseline_risk_matrix():
    """Vérifie le calcul des seuils de la matrice 4x4 (Faible <=3, Moyen <=6, Élevé <=9, Critique >9)."""
    assert calculate_level(gravite=1, vraisemblance=1) == "Faible"   # Score 1
    assert calculate_level(gravite=2, vraisemblance=1) == "Faible"   # Score 2
    assert calculate_level(gravite=2, vraisemblance=2) == "Moyen"    # Score 4
    assert calculate_level(gravite=2, vraisemblance=3) == "Moyen"    # Score 6
    assert calculate_level(gravite=3, vraisemblance=3) == "Élevé"    # Score 9
    assert calculate_level(gravite=4, vraisemblance=3) == "Critique" # Score 12
    assert calculate_level(gravite=4, vraisemblance=4) == "Critique" # Score 16


def test_scoring_bounds_capping():
    """Vérifie que la gravité et la vraisemblance sont strictement bornées entre 1 et 4."""
    # Plafond à 4 même si les inputs dépassent
    assert calculate_level(gravite=5, vraisemblance=5) == "Critique"
    assert calculate_level(gravite=0, vraisemblance=0) == "Faible"


def test_adjust_vraisemblance_with_findings():
    """Vérifie l'augmentation de la vraisemblance d'un cran lorsqu'une vulnérabilité active est détectée."""
    # Sans constat
    assert adjust_vraisemblance(vraisemblance=2, has_high_severity_finding=False) == 2
    # Avec constat critique : 2 -> 3
    assert adjust_vraisemblance(vraisemblance=2, has_high_severity_finding=True) == 3
    # Plafonnement à 4
    assert adjust_vraisemblance(vraisemblance=4, has_high_severity_finding=True) == 4


# ==============================================================================
# 2. Tests de la logique mathématique : Maturité vs Risque Résiduel
# ==============================================================================

def test_maturity_reduction_on_residual_risk():
    """Vérifie l'impact direct du niveau de maturité des contrôles sur l'atténuation du risque."""
    gravite = 4
    vraisemblance = 4

    # Maturité nulle (< 2.5) : aucune atténuation (vraisemblance reste 4 -> score 16 -> Critique)
    assert calculate_residual(gravite, vraisemblance, maturity_avg=1.0) == "Critique"

    # Maturité intermédiaire (>= 2.5 et < 4.0) : réduction de 1 cran (vraisemblance passe à 3 -> score 12 -> Critique)
    assert calculate_residual(gravite, vraisemblance, maturity_avg=3.0) == "Critique"

    # Haute maturité (>= 4.0) : réduction de 2 crans (vraisemblance passe à 2 -> score 8 -> Élevé)
    assert calculate_residual(gravite, vraisemblance, maturity_avg=4.5) == "Élevé"


def test_mathematical_maturity_degradation_formula():
    """
    Vérifie la formule mathématique d'impact des constats sur la maturité :
    computed_maturity = max(0.0, base_maturity - (errors * 1.0) - (warnings * 0.5))
    """
    base_maturity = 3.0

    # 0 constat -> maturité intacte
    m0 = max(0.0, base_maturity - (0 * 1.0) - (0 * 0.5))
    assert m0 == 3.0

    # 1 faille critique (error) -> maturité baisse de 1.0 point
    m1 = max(0.0, base_maturity - (1 * 1.0) - (0 * 0.5))
    assert m1 == 2.0

    # 2 failles critiques -> maturité baisse de 2.0 points
    m2 = max(0.0, base_maturity - (2 * 1.0) - (0 * 0.5))
    assert m2 == 1.0

    # 3 failles critiques + avertissements -> plancher strict à 0.0
    m3 = max(0.0, base_maturity - (3 * 1.0) - (2 * 0.5))
    assert m3 == 0.0


def test_risk_escalation_upon_critical_finding():
    """
    Vérifie le scénario clé :
    Gravité 4, Vraisemblance 3.
    Avant faille : Maturité 3.0 -> Vraisemblance résiduelle réduite à 2 -> Score résiduel 8 (Élevé).
    Après faille critique : Maturité dégradée à 2.0 (< 2.5) -> Perte d'atténuation -> Score 12 (Critique).
    """
    gravite = 4
    vraisemblance = 3

    # État initial sain (maturité 3.0)
    score_avant = get_risk_scores(gravite, vraisemblance, maturity_avg=3.0)
    assert score_avant["score_residuel"] == 8
    assert score_avant["niveau_residuel"] == "Élevé"

    # Arrivée d'un constat critique : maturité tombe à 2.0
    maturite_degradee = max(0.0, 3.0 - (1 * 1.0))
    score_apres = get_risk_scores(gravite, vraisemblance, maturity_avg=maturite_degradee)
    assert score_apres["score_residuel"] == 12
    assert score_apres["niveau_residuel"] == "Critique"

    # Assertion mathématique d'escalade
    assert score_apres["score_residuel"] > score_avant["score_residuel"]


# ==============================================================================
# 3. Tests d'intégration : Ingestion SARIF et Rattachement Automatique
# ==============================================================================

def test_sarif_parser_extraction(sample_sarif_file):
    """Vérifie que le parseur SARIF extrait fidèlement la CVE, la sévérité, l'actif et la technique ATT&CK."""
    findings = parse_sarif(sample_sarif_file)
    assert len(findings) == 1

    finding = findings[0]
    assert finding["cve"] == "CVE-2024-1234"
    assert finding["severite"] == "error"
    assert finding["actif_id"] == "ast_vpn"
    assert finding["technique_attack"] == "T1190"


def test_ingest_attaches_findings_to_matching_risks(db_session, sample_sarif_file):
    """
    Vérifie que l'ingestion SARIF :
    1. Crée le constat en base.
    2. Le lie automatiquement au scénario de risque EBIOS partageant la technique T1190.
    3. Le lie au contrôle ISO 8.8 (Gestion des vulnérabilités).
    """
    count = ingest_findings(db_session, source="sarif", filepath=sample_sarif_file)
    assert count == 1

    finding = db_session.query(Finding).filter_by(cve="CVE-2024-1234").first()
    assert finding is not None
    assert finding.severite == "error"

    # Vérification du lien automatique vers le risque R-02 (T1190)
    assert len(finding.risks) == 1
    assert finding.risks[0].id == "R-02"

    # Vérification du lien automatique vers ISO 8.8
    assert len(finding.controls) == 1
    assert finding.controls[0].id == "8.8"


def test_end_to_end_finding_impact_on_risk_scoring(db_session, sample_sarif_file):
    """
    Test End-to-End :
    1. Récupère le scénario R-02 avant ingestion : 0 constat, maturité 3.0 -> Résiduel = Élevé (score 8).
    2. Ingère le scan SARIF contenant la faille critique.
    3. Recalcule la maturité et les scores pour R-02.
    4. Confirme l'augmentation du risque résiduel à Critique (score 12).
    """
    risk = db_session.query(ScenarioOperationnel).filter_by(id="R-02").first()

    # 1. Avant ingestion
    findings_avant = db_session.query(Finding).filter(Finding.risks.contains(risk)).all()
    assert len(findings_avant) == 0
    scores_init = get_risk_scores(risk.gravite, risk.vraisemblance, maturity_avg=3.0)
    assert scores_init["niveau_residuel"] == "Élevé"

    # 2. Ingestion SARIF
    ingest_findings(db_session, source="sarif", filepath=sample_sarif_file)

    # 3. Après ingestion : requête dynamique des constats
    findings_apres = db_session.query(Finding).filter(Finding.risks.contains(risk)).all()
    assert len(findings_apres) == 1

    errors = len([f for f in findings_apres if f.severite == "error"])
    computed_maturity = max(0.0, 3.0 - (errors * 1.0))
    assert computed_maturity == 2.0

    # 4. Calcul dynamique du nouveau score
    nouveaux_scores = get_risk_scores(risk.gravite, risk.vraisemblance, maturity_avg=computed_maturity)
    assert nouveaux_scores["score_residuel"] == 12
    assert nouveaux_scores["niveau_residuel"] == "Critique"


def test_multiple_warning_findings_cumulative_degradation():
    """Vérifie que plusieurs warnings cumulent un impact mathématique suffisant pour faire basculer le risque."""
    gravite = 4
    vraisemblance = 3
    base_maturity = 3.0

    # 4 warnings -> dégradation de 4 * 0.5 = 2.0 points -> maturité 1.0 (< 2.5)
    warnings = 4
    computed_maturity = max(0.0, base_maturity - (warnings * 0.5))
    assert computed_maturity == 1.0

    scores = get_risk_scores(gravite, vraisemblance, maturity_avg=computed_maturity)
    assert scores["niveau_residuel"] == "Critique"
    assert scores["score_residuel"] == 12
