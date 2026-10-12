"""
tests/test_mappings_validate.py

Tests unitaires pour les règles de validation et de chargement des mappings (grc/mappings/*.yaml) :
1. Existence et format de control_id dans annex_a.yaml (format "8.7", sans "A.").
2. Unicité des identifiants de mapping.
3. Framework dans {NIS2, ATT&CK, NIST CSF 2.0}.
4. Format de reference (NIS2 Article 21(2)x a-j, ATT&CK Txxxx/Txxxx.xxx, NIST CSF 2.0).
5. Couverture NIS2 : 10 mesures 21(2) a à j couvertes par au moins 1 contrôle applicable.
6. Couverture ATT&CK : techniques de w4 couvertes par au moins 1 contrôle applicable (warning si 1 seul).
7. Un contrôle non applicable ne peut pas être la seule couverture d'une mesure ou technique.
8. Confidence low produit un avertissement (pas d'erreur).
9. Schéma strict : champ inconnu produit une erreur lisible dans validate et un ValueError dans le loader.
"""

from pathlib import Path

import pytest
import yaml
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.models import Base, Control
from app.services.loader import load_grc_idempotent
from app.services.validate import validate_grc_yaml


@pytest.fixture
def base_grc_setup(tmp_path: Path) -> Path:
    """Génère un squelette GRC de test complet et valide."""
    si_dir = tmp_path / "si"
    ebios_dir = tmp_path / "ebios"
    iso_dir = tmp_path / "iso27001"
    mappings_dir = tmp_path / "mappings"

    si_dir.mkdir()
    ebios_dir.mkdir()
    iso_dir.mkdir()
    mappings_dir.mkdir()

    # Valeurs métier
    bv_content = {
        "business_values": [
            {
                "id": "bv_test",
                "name": "Prise en charge",
                "process": "Accueil",
                "feared_event": "Retard",
                "severity": 3,
            }
        ]
    }
    with open(si_dir / "business_values.yaml", "w", encoding="utf-8") as f:
        yaml.safe_dump(bv_content, f)

    # Actifs
    assets_content = {
        "assets": [
            {
                "id": "ast_test",
                "name": "Serveur PACS",
                "type": "application",
                "criticality": 3,
                "business_values": ["bv_test"],
            }
        ]
    }
    with open(si_dir / "assets.yaml", "w", encoding="utf-8") as f:
        yaml.safe_dump(assets_content, f)

    # Contrôles ISO 27001 (deux applicables, un non-applicable)
    annex_content = {
        "controls": [
            {
                "id": "8.7",
                "name": "Protection antimalware",
                "theme": "Technologique",
                "is_applicable": True,
                "status": "implemented",
                "maturity": 4,
                "justification": "Déploiement de l'agent antimalware centralisé sur le parc.",
                "evidence": "Console de supervision antimalware",
            },
            {
                "id": "8.13",
                "name": "Sauvegardes",
                "theme": "Technologique",
                "is_applicable": True,
                "status": "implemented",
                "maturity": 4,
                "justification": "Stratégie de sauvegardes journalières externalisées et testées.",
                "evidence": "Rapports d'exécution des sauvegardes",
            },
            {
                "id": "8.25",
                "name": "Cycle de développement sécurisé",
                "theme": "Technologique",
                "is_applicable": False,
                "status": "not_applicable",
                "maturity": None,
                "justification": "Non applicable : Aucun développement interne de logiciel sur site.",
                "evidence": None,
            },
        ]
    }
    with open(iso_dir / "annex_a.yaml", "w", encoding="utf-8") as f:
        yaml.safe_dump(annex_content, f)

    # Sources & Objectifs EBIOS RM W2
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
            {"id": "ov_1", "name": "Extorsion", "description": "Ransomware"}
        ],
        "sr_ov_pairs": [
            {"id": "srov_1", "sr_id": "sr_1", "ov_id": "ov_1", "relevance": 3}
        ],
    }
    with open(ebios_dir / "w2_sources.yaml", "w", encoding="utf-8") as f:
        yaml.safe_dump(w2_content, f)

    # W3 Scénarios stratégiques
    w3_content = {
        "stakeholders": [
            {"id": "sh_1", "name": "Editeur PACS", "threat_level": 3, "dependency": "Forte"}
        ],
        "strategic_scenarios": [
            {
                "id": "sc_strat_1",
                "name": "Attaque supply chain",
                "srov_id": "srov_1",
                "stakeholder_id": "sh_1",
                "likelihood": 3,
            }
        ],
    }
    with open(ebios_dir / "w3_strategiques.yaml", "w", encoding="utf-8") as f:
        yaml.safe_dump(w3_content, f)

    # W4 Risques opérationnels
    w4_content = {
        "risks": [
            {
                "id": "R-01",
                "name": "Ransomware PACS",
                "strategic_scenario_id": "sc_strat_1",
                "assets": ["ast_test"],
                "attack_techniques": ["T1566", "T1486"],
                "likelihood": 3,
                "severity": 3,
                "controls": ["8.7", "8.13"],
                "nist_csf": ["PR.AT-01", "PR.DS-11"],
            }
        ]
    }
    with open(ebios_dir / "w4_operationnels.yaml", "w", encoding="utf-8") as f:
        yaml.safe_dump(w4_content, f)

    # W5 Traitements
    w5_content = {
        "treatments": [
            {
                "id": "tr_01",
                "name": "Plan de sauvegarde et EDR",
                "risk_id": "R-01",
                "option": "reduce",
                "owner": "RSSI",
                "due_date": "2026-12-31",
                "status": "in_progress",
            }
        ]
    }
    with open(ebios_dir / "w5_traitements.yaml", "w", encoding="utf-8") as f:
        yaml.safe_dump(w5_content, f)

    # Mappings valides de base
    nis2_data = {
        "mappings": [
            {
                "id": f"map_nis2_{letter}",
                "control_id": "8.7",
                "framework": "NIS2",
                "reference": f"Article 21(2){letter}",
                "confidence": "high",
                "source": "Directive NIS2",
                "rationale": f"Couverture mesure {letter}",
            }
            for letter in "abcdefghij"
        ]
    }
    with open(mappings_dir / "iso_nis2.yaml", "w", encoding="utf-8") as f:
        yaml.safe_dump(nis2_data, f)

    att_data = {
        "mappings": [
            {
                "id": "map_att_1",
                "control_id": "8.7",
                "framework": "ATT&CK",
                "reference": "T1566",
                "confidence": "high",
            },
            {
                "id": "map_att_2",
                "control_id": "8.13",
                "framework": "ATT&CK",
                "reference": "T1566",
                "confidence": "high",
            },
            {
                "id": "map_att_3",
                "control_id": "8.7",
                "framework": "ATT&CK",
                "reference": "T1486",
                "confidence": "high",
            },
            {
                "id": "map_att_4",
                "control_id": "8.13",
                "framework": "ATT&CK",
                "reference": "T1486",
                "confidence": "high",
            },
        ]
    }
    with open(mappings_dir / "iso_attack.yaml", "w", encoding="utf-8") as f:
        yaml.safe_dump(att_data, f)

    nist_data = {
        "mappings": [
            {
                "id": "map_nist_1",
                "control_id": "8.7",
                "framework": "NIST CSF 2.0",
                "reference": "PR.AT-01",
                "confidence": "medium",
            }
        ]
    }
    with open(mappings_dir / "iso_nist.yaml", "w", encoding="utf-8") as f:
        yaml.safe_dump(nist_data, f)

    return tmp_path


def test_mappings_valid_dataset(base_grc_setup):
    """Vérifie que le dataset avec mappings complets est valide sans erreurs ni avertissements."""
    report = validate_grc_yaml(base_grc_setup)
    assert report.is_valid is True
    assert len(report.errors) == 0
    assert len(report.warnings) == 0


def test_mapping_control_id_format_prefix_a_error(base_grc_setup):
    """Vérifie que control_id avec préfixe 'A.' est rejeté."""
    nis2_file = base_grc_setup / "mappings" / "iso_nis2.yaml"
    with open(nis2_file, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)
    data["mappings"][0]["control_id"] = "A.8.7"
    with open(nis2_file, "w", encoding="utf-8") as f:
        yaml.safe_dump(data, f)

    report = validate_grc_yaml(base_grc_setup)
    assert report.is_valid is False
    assert any("doit être au format '8.7' sans 'A.'" in err for err in report.errors)


def test_mapping_control_id_non_existent(base_grc_setup):
    """Vérifie que control_id absent d'annex_a.yaml est rejeté."""
    nis2_file = base_grc_setup / "mappings" / "iso_nis2.yaml"
    with open(nis2_file, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)
    data["mappings"][0]["control_id"] = "99.99"
    with open(nis2_file, "w", encoding="utf-8") as f:
        yaml.safe_dump(data, f)

    report = validate_grc_yaml(base_grc_setup)
    assert report.is_valid is False
    assert any("control_id '99.99' n'existe pas dans annex_a.yaml" in err for err in report.errors)


def test_mapping_duplicate_ids(base_grc_setup):
    """Vérifie que deux mappings ayant le même id déclenchent une erreur d'unicité."""
    att_file = base_grc_setup / "mappings" / "iso_attack.yaml"
    with open(att_file, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)
    data["mappings"][1]["id"] = data["mappings"][0]["id"]
    with open(att_file, "w", encoding="utf-8") as f:
        yaml.safe_dump(data, f)

    report = validate_grc_yaml(base_grc_setup)
    assert report.is_valid is False
    assert any("dupliqué" in err for err in report.errors)


def test_mapping_invalid_framework(base_grc_setup):
    """Vérifie que framework hors {NIS2, ATT&CK, NIST CSF 2.0} est rejeté."""
    nis2_file = base_grc_setup / "mappings" / "iso_nis2.yaml"
    with open(nis2_file, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)
    data["mappings"][0]["framework"] = "ISO_27002"
    with open(nis2_file, "w", encoding="utf-8") as f:
        yaml.safe_dump(data, f)

    report = validate_grc_yaml(base_grc_setup)
    assert report.is_valid is False
    assert any("framework 'ISO_27002' invalide" in err for err in report.errors)


def test_mapping_reference_format_nis2_invalid(base_grc_setup):
    """Vérifie qu'une référence NIS2 hors de Article 21(2)[a-j] est rejetée."""
    nis2_file = base_grc_setup / "mappings" / "iso_nis2.yaml"
    with open(nis2_file, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)
    data["mappings"][0]["reference"] = "Article 21(2)k"
    with open(nis2_file, "w", encoding="utf-8") as f:
        yaml.safe_dump(data, f)

    report = validate_grc_yaml(base_grc_setup)
    assert report.is_valid is False
    assert any("référence 'Article 21(2)k' invalide" in err for err in report.errors)


def test_mapping_reference_format_attack_invalid(base_grc_setup):
    """Vérifie qu'une référence ATT&CK non conforme Txxxx est rejetée."""
    att_file = base_grc_setup / "mappings" / "iso_attack.yaml"
    with open(att_file, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)
    data["mappings"][0]["reference"] = "TECH-INVALID"
    with open(att_file, "w", encoding="utf-8") as f:
        yaml.safe_dump(data, f)

    report = validate_grc_yaml(base_grc_setup)
    assert report.is_valid is False
    assert any("référence 'TECH-INVALID' invalide" in err for err in report.errors)


def test_mapping_reference_format_nist_invalid(base_grc_setup):
    """Vérifie qu'une référence NIST non conforme CSF 2.0 est rejetée."""
    nist_file = base_grc_setup / "mappings" / "iso_nist.yaml"
    with open(nist_file, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)
    data["mappings"][0]["reference"] = "PR.AC-01"  # Catégorie 1.1 obsolète
    with open(nist_file, "w", encoding="utf-8") as f:
        yaml.safe_dump(data, f)

    report = validate_grc_yaml(base_grc_setup)
    assert report.is_valid is False
    assert any("non conforme au format NIST CSF 2.0" in err for err in report.errors)


def test_mapping_nis2_coverage_missing_measure(base_grc_setup):
    """Vérifie qu'une mesure NIS2 21(2) non couverte provoque une erreur de validation."""
    nis2_file = base_grc_setup / "mappings" / "iso_nis2.yaml"
    with open(nis2_file, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)
    # Suppression de la mesure 'e'
    data["mappings"] = [m for m in data["mappings"] if not m["reference"].endswith("e")]
    with open(nis2_file, "w", encoding="utf-8") as f:
        yaml.safe_dump(data, f)

    report = validate_grc_yaml(base_grc_setup)
    assert report.is_valid is False
    assert any("La mesure Article 21(2)e n'est couverte par aucun contrôle" in err for err in report.errors)


def test_mapping_nis2_coverage_only_non_applicable_control(base_grc_setup):
    """Vérifie qu'un contrôle non applicable ne peut pas être la seule couverture d'une mesure NIS2."""
    nis2_file = base_grc_setup / "mappings" / "iso_nis2.yaml"
    with open(nis2_file, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)
    # Lier la mesure 'a' au contrôle 8.25 (qui a is_applicable: False)
    for m in data["mappings"]:
        if m["reference"].endswith("a"):
            m["control_id"] = "8.25"
    with open(nis2_file, "w", encoding="utf-8") as f:
        yaml.safe_dump(data, f)

    report = validate_grc_yaml(base_grc_setup)
    assert report.is_valid is False
    assert any("n'est couverte que par des contrôles non applicables" in err for err in report.errors)


def test_mapping_attack_coverage_missing_technique(base_grc_setup):
    """Vérifie qu'une technique ATT&CK citée dans w4 sans aucun contrôle mappé provoque une erreur."""
    att_file = base_grc_setup / "mappings" / "iso_attack.yaml"
    with open(att_file, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)
    # Suppression des mappings de T1566
    data["mappings"] = [m for m in data["mappings"] if "T1566" not in m["reference"]]
    with open(att_file, "w", encoding="utf-8") as f:
        yaml.safe_dump(data, f)

    report = validate_grc_yaml(base_grc_setup)
    assert report.is_valid is False
    expected_msg = "La technique 'T1566' citée dans w4_operationnels.yaml n'est couverte par aucun contrôle"
    assert any(expected_msg in err for err in report.errors)


def test_mapping_attack_coverage_only_non_applicable(base_grc_setup):
    """Vérifie qu'une technique ATT&CK couverte uniquement par un contrôle non applicable provoque une erreur."""
    att_file = base_grc_setup / "mappings" / "iso_attack.yaml"
    with open(att_file, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)
    # T1566 uniquement rattaché au contrôle 8.25 (non applicable)
    data["mappings"] = [m for m in data["mappings"] if "T1566" not in m["reference"]]
    data["mappings"].append({
        "id": "map_att_na",
        "control_id": "8.25",
        "framework": "ATT&CK",
        "reference": "T1566",
    })
    with open(att_file, "w", encoding="utf-8") as f:
        yaml.safe_dump(data, f)

    report = validate_grc_yaml(base_grc_setup)
    assert report.is_valid is False
    expected_msg = (
        "La technique 'T1566' citée dans w4_operationnels.yaml n'est couverte que par des contrôles non applicables"
    )
    assert any(expected_msg in err for err in report.errors)


def test_mapping_attack_coverage_single_control_warning(base_grc_setup):
    """Vérifie qu'une technique ATT&CK couverte par un seul contrôle applicable génère un avertissement."""
    att_file = base_grc_setup / "mappings" / "iso_attack.yaml"
    with open(att_file, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)
    # Garder un seul contrôle (8.7) pour T1566
    data["mappings"] = [m for m in data["mappings"] if not (m["id"] == "map_att_2" and "T1566" in m["reference"])]
    with open(att_file, "w", encoding="utf-8") as f:
        yaml.safe_dump(data, f)

    report = validate_grc_yaml(base_grc_setup)
    # Pas d'erreur, mais un avertissement
    assert report.is_valid is True
    assert any("La technique 'T1566' n'est couverte que par un seul contrôle applicable" in w for w in report.warnings)


def test_mapping_confidence_low_generates_warning(base_grc_setup):
    """Vérifie qu'un mapping avec confidence: low produit un avertissement sans bloquer la validation."""
    nis2_file = base_grc_setup / "mappings" / "iso_nis2.yaml"
    with open(nis2_file, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)
    data["mappings"][0]["confidence"] = "low"
    with open(nis2_file, "w", encoding="utf-8") as f:
        yaml.safe_dump(data, f)

    report = validate_grc_yaml(base_grc_setup)
    assert report.is_valid is True
    assert any("niveau de confiance faible (confidence: low)" in w for w in report.warnings)


def test_mapping_confidence_invalid_generates_error(base_grc_setup):
    """Vérifie qu'une valeur de confidence hors de {high, medium, low} déclenche une erreur."""
    nis2_file = base_grc_setup / "mappings" / "iso_nis2.yaml"
    with open(nis2_file, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)
    data["mappings"][0]["confidence"] = "ultra_high"
    with open(nis2_file, "w", encoding="utf-8") as f:
        yaml.safe_dump(data, f)

    report = validate_grc_yaml(base_grc_setup)
    assert report.is_valid is False
    assert any("confidence 'ultra_high' invalide" in err for err in report.errors)


def test_mapping_schema_unknown_field_in_validation_and_loader(base_grc_setup):
    """Vérifie qu'un champ inconnu est rejeté par validate et lève un ValueError dans le loader."""
    nis2_file = base_grc_setup / "mappings" / "iso_nis2.yaml"
    with open(nis2_file, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)
    data["mappings"][0]["champ_inconnu"] = "valeur_interdite"
    with open(nis2_file, "w", encoding="utf-8") as f:
        yaml.safe_dump(data, f)

    # 1. Validation
    report = validate_grc_yaml(base_grc_setup)
    assert report.is_valid is False
    assert any("contient des champs non autorisés : champ_inconnu" in err for err in report.errors)

    # 2. Loader idempotent
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(bind=engine)
    Session = sessionmaker(bind=engine)
    session = Session()

    # Charger d'abord les contrôles nécessaires pour les clés étrangères
    session.add(Control(id="8.7", name="Antimalware", theme="Tech", is_applicable=True, maturity=4))
    session.add(Control(id="8.13", name="Backup", theme="Tech", is_applicable=True, maturity=4))
    session.commit()

    with pytest.raises(ValueError) as excinfo:
        load_grc_idempotent(session, grc_dir=str(base_grc_setup))
    assert "Champ inconnu dans le mapping" in str(excinfo.value)
    assert "champ_inconnu" in str(excinfo.value)
    session.close()
