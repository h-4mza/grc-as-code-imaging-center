from pathlib import Path

import pytest
import yaml
from typer.testing import CliRunner

from app.cli import app
from app.services.validate import validate_grc_yaml

runner = CliRunner()


@pytest.fixture
def valid_grc_dir(tmp_path: Path) -> Path:
    """Crée une arborescence YAML GRC minimale mais 100% valide et conforme."""
    si_dir = tmp_path / "si"
    ebios_dir = tmp_path / "ebios"
    iso_dir = tmp_path / "iso27001"
    si_dir.mkdir()
    ebios_dir.mkdir()
    iso_dir.mkdir()

    # 1. business_values.yaml
    bv_content = {
        "business_values": [
            {
                "id": "bv_test",
                "name": "Prise en charge",
                "process": "Accueil",
                "feared_event": "Retard",
                "severity": 4,
            }
        ]
    }
    with open(si_dir / "business_values.yaml", "w", encoding="utf-8") as f:
        yaml.safe_dump(bv_content, f)

    # 2. assets.yaml
    assets_content = {
        "assets": [
            {
                "id": "ast_test",
                "name": "Serveur PACS",
                "type": "application",
                "criticality": 4,
                "business_values": ["bv_test"],
            }
        ]
    }
    with open(si_dir / "assets.yaml", "w", encoding="utf-8") as f:
        yaml.safe_dump(assets_content, f)

    # 3. annex_a.yaml
    annex_content = {
        "controls": [
            {
                "id": "8.7",
                "name": "Protection contre logiciels malveillants",
                "theme": "Technologique",
                "maturity": 4,
            },
            {
                "id": "8.13",
                "name": "Sauvegardes",
                "theme": "Technologique",
                "maturity": 4,
            },
        ]
    }
    with open(iso_dir / "annex_a.yaml", "w", encoding="utf-8") as f:
        yaml.safe_dump(annex_content, f)

    # 4. w2_sources.yaml
    w2_content = {
        "risk_sources": [
            {
                "id": "sr_1",
                "name": "Cybercriminels",
                "type": "Externe",
                "motivation": "Finance",
                "resources": "Hautes",
            }
        ],
        "objectives": [
            {
                "id": "ov_1",
                "name": "Extorsion",
                "description": "Ransomware",
            }
        ],
        "sr_ov_pairs": [
            {
                "id": "srov_1",
                "sr_id": "sr_1",
                "ov_id": "ov_1",
                "relevance": 4,
            }
        ],
    }
    with open(ebios_dir / "w2_sources.yaml", "w", encoding="utf-8") as f:
        yaml.safe_dump(w2_content, f)

    # 5. w3_strategiques.yaml
    w3_content = {
        "stakeholders": [
            {
                "id": "sh_1",
                "name": "Editeur PACS",
                "threat_level": 4,
                "dependency": "Forte",
            }
        ],
        "strategic_scenarios": [
            {
                "id": "sc_strat_1",
                "name": "Attaque chaîne d'approvisionnement",
                "srov_id": "srov_1",
                "stakeholder_id": "sh_1",
                "likelihood": 3,
            }
        ],
    }
    with open(ebios_dir / "w3_strategiques.yaml", "w", encoding="utf-8") as f:
        yaml.safe_dump(w3_content, f)

    # 6. w4_operationnels.yaml
    w4_content = {
        "risks": [
            {
                "id": "R-01",
                "name": "Ransomware PACS",
                "strategic_scenario_id": "sc_strat_1",
                "assets": ["ast_test"],
                "attack_techniques": ["T1566", "T1486"],
                "likelihood": 3,
                "severity": 4,
                "controls": ["8.7", "8.13"],
                "nist_csf": ["GV.SC-04", "PR.AA-01", "PR.DS-11"],
            }
        ]
    }
    with open(ebios_dir / "w4_operationnels.yaml", "w", encoding="utf-8") as f:
        yaml.safe_dump(w4_content, f)

    # 7. w5_traitements.yaml
    w5_content = {
        "treatments": [
            {
                "id": "tr_01",
                "name": "Segmentation réseau",
                "risk_id": "R-01",
                "option": "reduce",
                "owner": "IT",
                "due_date": "2026-12-31",
                "status": "in_progress",
            }
        ]
    }
    with open(ebios_dir / "w5_traitements.yaml", "w", encoding="utf-8") as f:
        yaml.safe_dump(w5_content, f)

    return tmp_path


def test_validator_valid_dataset(valid_grc_dir):
    """Vérifie qu'un dataset complètement valide passe la validation à 100%."""
    report = validate_grc_yaml(valid_grc_dir)
    assert report.is_valid is True
    assert len(report.errors) == 0
    assert len(report.risk_summaries) == 1
    assert report.risk_summaries[0].id == "R-01"
    assert report.risk_summaries[0].score_inherent == 12  # 4 * 3
    assert report.risk_summaries[0].niveau_inherent == "Critique"


def test_validator_scale_error_severity_5(valid_grc_dir):
    """Vérifie que severity=5 ou likelihood=5 est strictement interdit."""
    w4_file = valid_grc_dir / "ebios" / "w4_operationnels.yaml"
    with open(w4_file, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)
    data["risks"][0]["severity"] = 5
    with open(w4_file, "w", encoding="utf-8") as f:
        yaml.safe_dump(data, f)

    report = validate_grc_yaml(valid_grc_dir)
    assert report.is_valid is False
    assert any("severity=5" in err for err in report.errors)


def test_validator_cross_ref_missing_strategic_scenario(valid_grc_dir):
    """Vérifie qu'un strategic_scenario_id null ou manquant déclenche une erreur obligatoire."""
    w4_file = valid_grc_dir / "ebios" / "w4_operationnels.yaml"
    with open(w4_file, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)
    data["risks"][0]["strategic_scenario_id"] = None
    with open(w4_file, "w", encoding="utf-8") as f:
        yaml.safe_dump(data, f)

    report = validate_grc_yaml(valid_grc_dir)
    assert report.is_valid is False
    assert any("strategic_scenario_id manquant ou null" in err for err in report.errors)


def test_validator_control_format_prefix_a(valid_grc_dir):
    """Vérifie qu'un contrôle préfixé par 'A.' est signalé comme une erreur de format."""
    w4_file = valid_grc_dir / "ebios" / "w4_operationnels.yaml"
    with open(w4_file, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)
    data["risks"][0]["controls"] = ["A.8.7"]
    with open(w4_file, "w", encoding="utf-8") as f:
        yaml.safe_dump(data, f)

    report = validate_grc_yaml(valid_grc_dir)
    assert report.is_valid is False
    assert any("sans préfixe 'A.'" in err for err in report.errors)


def test_validator_completeness_missing_treatment_or_attack_format(valid_grc_dir):
    """Vérifie les exigences de complétude : technique Txxxx et traitement associé."""
    w4_file = valid_grc_dir / "ebios" / "w4_operationnels.yaml"
    with open(w4_file, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)
    data["risks"][0]["attack_techniques"] = ["TECH_INVALID"]
    with open(w4_file, "w", encoding="utf-8") as f:
        yaml.safe_dump(data, f)

    w5_file = valid_grc_dir / "ebios" / "w5_traitements.yaml"
    with open(w5_file, "w", encoding="utf-8") as f:
        yaml.safe_dump({"treatments": []}, f)

    report = validate_grc_yaml(valid_grc_dir)
    assert report.is_valid is False
    assert any("technique ATT&CK 'TECH_INVALID' invalide" in err for err in report.errors)
    assert any("aucun traitement associé" in err for err in report.errors)


def test_validator_coherence_accept_option_requires_residual_le_moyen(valid_grc_dir):
    """Vérifie que l'option 'accept' échoue si le risque résiduel reste Élevé ou Critique."""
    # Score 4x4 avec maturité faible (0/5) -> résiduel = Critique (16)
    iso_file = valid_grc_dir / "iso27001" / "annex_a.yaml"
    with open(iso_file, "w", encoding="utf-8") as f:
        yaml.safe_dump({"controls": [{"id": "8.7", "maturity": 0}]}, f)

    w4_file = valid_grc_dir / "ebios" / "w4_operationnels.yaml"
    with open(w4_file, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)
    data["risks"][0]["severity"] = 4
    data["risks"][0]["likelihood"] = 4
    data["risks"][0]["controls"] = ["8.7"]
    with open(w4_file, "w", encoding="utf-8") as f:
        yaml.safe_dump(data, f)

    w5_file = valid_grc_dir / "ebios" / "w5_traitements.yaml"
    with open(w5_file, "r", encoding="utf-8") as f:
        t_data = yaml.safe_load(f)
    t_data["treatments"][0]["option"] = "accept"
    with open(w5_file, "w", encoding="utf-8") as f:
        yaml.safe_dump(t_data, f)

    report = validate_grc_yaml(valid_grc_dir)
    assert report.is_valid is False
    assert any("l'option 'accept' exige un niveau résiduel cible <= Moyen" in err for err in report.errors)


def test_validator_nist_csf_1_1_deprecated_identifiers(valid_grc_dir):
    """Vérifie la détection des identifiants obsolètes CSF 1.1 (PR.AC, PR.PT, PR.DS-05)."""
    w4_file = valid_grc_dir / "ebios" / "w4_operationnels.yaml"
    with open(w4_file, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)
    data["risks"][0]["nist_csf"] = ["PR.AC-01", "PR.PT-04", "PR.DS-05"]
    with open(w4_file, "w", encoding="utf-8") as f:
        yaml.safe_dump(data, f)

    report = validate_grc_yaml(valid_grc_dir)
    assert report.is_valid is False
    assert any("PR.AC-01" in err for err in report.errors)
    assert any("PR.PT-04" in err for err in report.errors)
    assert any("PR.DS-05" in err for err in report.errors)


def test_cli_validate_command_success(valid_grc_dir):
    """Teste la commande CLI grc validate sur un répertoire valide (exit code 0)."""
    result = runner.invoke(app, ["validate", "--dir", str(valid_grc_dir)])
    assert result.exit_code == 0
    assert "Tous les fichiers YAML GRC sont valides et cohérents" in result.stdout
    assert "Évaluation des Scénarios de Risque" in result.stdout


def test_cli_validate_command_failure_exit_code_1(valid_grc_dir):
    """Teste la commande CLI grc validate avec des erreurs (exit code 1)."""
    w4_file = valid_grc_dir / "ebios" / "w4_operationnels.yaml"
    with open(w4_file, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)
    data["risks"][0]["severity"] = 5
    with open(w4_file, "w", encoding="utf-8") as f:
        yaml.safe_dump(data, f)

    result = runner.invoke(app, ["validate", "--dir", str(valid_grc_dir)])
    assert result.exit_code == 1
    assert "Validation échouée" in result.stderr or "Validation échouée" in result.stdout


def test_validator_sr_defaillance_allows_empty_attack_techniques(valid_grc_dir):
    """Vérifie que les risques liés à sr_defaillance peuvent avoir attack_techniques vide."""
    # Ajouter sr_defaillance dans w2
    w2_file = valid_grc_dir / "ebios" / "w2_sources.yaml"
    with open(w2_file, "r", encoding="utf-8") as f:
        w2_data = yaml.safe_load(f)
    w2_data["risk_sources"].append(
        {
            "id": "sr_defaillance",
            "name": "Défaillance technique",
            "type": "Accidentel",
            "motivation": "N/A",
            "resources": "N/A",
        }
    )
    w2_data["sr_ov_pairs"].append(
        {"id": "srov_def", "sr_id": "sr_defaillance", "ov_id": "ov_1", "relevance": 3}
    )
    with open(w2_file, "w", encoding="utf-8") as f:
        yaml.safe_dump(w2_data, f)

    # Ajouter sc_defaillance dans w3
    w3_file = valid_grc_dir / "ebios" / "w3_strategiques.yaml"
    with open(w3_file, "r", encoding="utf-8") as f:
        w3_data = yaml.safe_load(f)
    w3_data["strategic_scenarios"].append(
        {
            "id": "sc_defaillance",
            "name": "Panne stockage",
            "srov_id": "srov_def",
            "stakeholder_id": None,
            "likelihood": 3,
        }
    )
    with open(w3_file, "w", encoding="utf-8") as f:
        yaml.safe_dump(w3_data, f)

    # Ajouter R-11 sans technique d'attaque dans w4
    w4_file = valid_grc_dir / "ebios" / "w4_operationnels.yaml"
    with open(w4_file, "r", encoding="utf-8") as f:
        w4_data = yaml.safe_load(f)
    w4_data["risks"].append(
        {
            "id": "R-11",
            "name": "Panne matérielle NAS",
            "strategic_scenario_id": "sc_defaillance",
            "assets": ["ast_test"],
            "attack_techniques": [],
            "likelihood": 3,
            "severity": 3,
            "controls": ["8.7"],
            "nist_csf": ["PR.IR-02"],
        }
    )
    with open(w4_file, "w", encoding="utf-8") as f:
        yaml.safe_dump(w4_data, f)

    # Ajouter traitement pour R-11 dans w5
    w5_file = valid_grc_dir / "ebios" / "w5_traitements.yaml"
    with open(w5_file, "r", encoding="utf-8") as f:
        w5_data = yaml.safe_load(f)
    w5_data["treatments"].append(
        {
            "id": "tr_11",
            "name": "Redondance NAS",
            "risk_id": "R-11",
            "option": "reduce",
            "owner": "IT",
            "due_date": "2026-12-31",
            "status": "todo",
        }
    )
    with open(w5_file, "w", encoding="utf-8") as f:
        yaml.safe_dump(w5_data, f)

    report = validate_grc_yaml(valid_grc_dir)
    assert report.is_valid is True
    assert len(report.errors) == 0
