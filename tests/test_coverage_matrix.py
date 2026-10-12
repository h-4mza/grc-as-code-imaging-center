from pathlib import Path

from typer.testing import CliRunner

from app.cli import app
from app.db import Base
from app.main import get_kpi_coverage
from app.models import Control, ControlMapping, ScenarioOperationnel
from app.services.loader import load_grc_idempotent
from app.services.matrix import generate_compliance_matrix

runner = CliRunner()


def test_export_matrix_cli(tmp_path: Path):
    """Vérifie que la commande CLI export-matrix génère correctement le fichier."""
    out_file = tmp_path / "matrice_test.md"
    result = runner.invoke(app, ["export-matrix", "--grc-dir", "grc", "--output", str(out_file)])
    assert result.exit_code == 0, f"Erreur CLI : {result.stdout}"
    assert out_file.exists()

    content = out_file.read_text(encoding="utf-8")
    # Vérification des 3 tableaux
    assert "## 1. Matrice des Contrôles ISO 27001:2022 et Mappings Multi-Référentiels" in content
    assert "## 2. Matrice Inversée : Directive NIS 2 -> Contrôles ISO 27001:2022" in content
    assert "## 3. Matrice Inversée : MITRE ATT&CK -> Contrôles ISO 27001:2022" in content

    # Vérification de quelques contrôles et techniques clés
    assert "**5.1**" in content
    assert "**8.5**" in content
    assert "**8.16**" in content
    assert "Article 21(2)a" in content
    assert "Article 21(2)j" in content
    assert "T1566" in content
    assert "T1110" in content
    assert "T1005" in content


def test_matrix_generation_service(tmp_path: Path):
    """Vérifie la fonction Python generate_compliance_matrix directement."""
    target_md = tmp_path / "matrice.md"
    generated_text = generate_compliance_matrix(grc_dir="grc", output_path=target_md)
    assert target_md.exists()
    assert len(generated_text) > 5000
    assert "Conforme" in generated_text
    assert "Prévention & Détection" in generated_text


def test_kpi_coverage_endpoint():
    """Vérifie le calcul des métriques de couverture NIS2 (10/10) et ATT&CK (20/20)."""
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker

    test_engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(bind=test_engine)
    TestSession = sessionmaker(bind=test_engine)
    db = TestSession()
    try:
        load_grc_idempotent(db, grc_dir="grc")
        db.commit()

        coverage = get_kpi_coverage(db=db)

        # NIS2 : 10 sur 10
        assert coverage["nis2"]["total_measures"] == 10
        assert coverage["nis2"]["covered_measures"] == 10
        assert coverage["nis2"]["coverage_rate_pct"] == 100
        assert len(coverage["nis2"]["measures"]) == 10
        assert coverage["nis2"]["breakdown_by_status"]["implemented"] > 0

        # ATT&CK : 20 sur 20 techniques
        assert coverage["attack"]["total_techniques"] == 20
        assert coverage["attack"]["covered_techniques"] == 20
        assert coverage["attack"]["coverage_rate_pct"] == 100
        assert len(coverage["attack"]["techniques"]) == 20

        # Vérification qu'aucune technique n'est laissée sans contrôle
        for t_info in coverage["attack"]["techniques"]:
            assert t_info["covered"] is True
            assert t_info["controls_count"] >= 1
    finally:
        db.close()


def test_kpi_coverage_alert_on_unimplemented_controls():
    """Vérifie le mécanisme d'alerte lorsqu'une technique n'est couverte que par des contrôles non implémentés."""
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker

    # Moteur SQLite en mémoire isolé pour ce test
    test_engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(bind=test_engine)
    TestSession = sessionmaker(bind=test_engine)
    db = TestSession()

    try:
        # Contrôle non implémenté
        c1 = Control(
            id="99.1",
            name="Contrôle Futur",
            theme="Technique",
            is_applicable=True,
            status="not_implemented",
            maturity=0,
        )
        db.add(c1)

        # Scénario avec une technique fictive T9999
        import json

        sc = ScenarioOperationnel(
            id="R-TEST",
            nom="Scénario Test Alerte",
            techniques_attack=json.dumps(["T9999"]),
            vraisemblance=3,
            gravite=3,
        )
        db.add(sc)

        # Mapping de T9999 vers le contrôle 99.1 (non implémenté)
        m = ControlMapping(
            id="map_test_alert",
            control_id="99.1",
            framework="ATT&CK",
            reference="T9999 - Fake Attack Technique",
            confidence="high",
            rationale="Test",
        )
        db.add(m)
        db.commit()

        coverage = get_kpi_coverage(db=db)

        # Doit déclencher une alerte
        assert "T9999" in coverage["attack"]["techniques_only_non_implemented"]
        assert len(coverage["attack"]["alerts"]) == 1
        assert "T9999" in coverage["attack"]["alerts"][0]
        assert "non implémentés" in coverage["attack"]["alerts"][0]
    finally:
        db.close()
