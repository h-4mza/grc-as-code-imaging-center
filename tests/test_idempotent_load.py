"""
tests/test_idempotent_load.py

Tests de validation du chargement idempotent, de reset et de relink :
1. Deux 'load' de suite donnent exactement les mêmes comptages.
2. Ingest, puis load : les constats sont toujours là.
3. jira_key posée en base puis load : conservée (la base gagne si YAML a null).
4. Un risque retiré du YAML disparaît de la base, ses liaisons aussi (prune).
5. Un YAML invalide : exit code 1 et base inchangée.
6. Commande reset (--yes et confirmation interactive).
7. Commande relink.
"""

import json
import shutil
from pathlib import Path

import pytest
import yaml
from sqlalchemy import create_engine, select
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from typer.testing import CliRunner

from app import cli, db
from app.cli import app
from app.models import (
    Asset,
    Base,
    BusinessValue,
    Control,
    ControlMapping,
    CoupleSROV,
    Finding,
    ObjectifVise,
    PartiePrenante,
    ScenarioOperationnel,
    ScenarioStrategique,
    SourceRisque,
    Treatment,
    asset_bv_table,
    finding_risk_table,
    risk_asset_table,
    risk_control_table,
)
from app.services.ingest import ingest_findings

runner = CliRunner()


@pytest.fixture
def sqlite_db(monkeypatch):
    """Configure un moteur SQLite en mémoire partagé pour les tests."""
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


@pytest.fixture
def tmp_grc(tmp_path):
    """Copie l'intégralité du dossier référentiel grc/ dans un dossier temporaire isolé."""
    src = Path("grc")
    dst = tmp_path / "grc"
    shutil.copytree(src, dst)
    return dst


def get_db_counts(session):
    """Retourne les comptages de toutes les tables possédées et de liaison."""
    return {
        "business_values": session.query(BusinessValue).count(),
        "assets": session.query(Asset).count(),
        "risk_sources": session.query(SourceRisque).count(),
        "objectives": session.query(ObjectifVise).count(),
        "sr_ov_pairs": session.query(CoupleSROV).count(),
        "stakeholders": session.query(PartiePrenante).count(),
        "strategic_scenarios": session.query(ScenarioStrategique).count(),
        "controls": session.query(Control).count(),
        "risks": session.query(ScenarioOperationnel).count(),
        "mappings": session.query(ControlMapping).count(),
        "treatments": session.query(Treatment).count(),
        "risk_asset": len(session.execute(select(risk_asset_table)).all()),
        "risk_control": len(session.execute(select(risk_control_table)).all()),
        "asset_bv": len(session.execute(select(asset_bv_table)).all()),
    }


def test_two_consecutive_loads_give_identical_counts(sqlite_db, tmp_grc):
    """Vérifie que deux appels successifs à grc load sont strictement idempotents."""
    # Premier chargement
    res1 = runner.invoke(app, ["load", "--grc-dir", str(tmp_grc)])
    assert res1.exit_code == 0, f"Premier load échoué : {res1.stdout} {res1.stderr}"

    session = sqlite_db()
    try:
        counts1 = get_db_counts(session)
    finally:
        session.close()

    # Deuxième chargement
    res2 = runner.invoke(app, ["load", "--grc-dir", str(tmp_grc)])
    assert res2.exit_code == 0, f"Deuxième load échoué : {res2.stdout} {res2.stderr}"

    session = sqlite_db()
    try:
        counts2 = get_db_counts(session)
    finally:
        session.close()

    assert counts1 == counts2, f"Les comptages diffèrent entre les deux chargements : {counts1} vs {counts2}"


def test_ingest_then_load_preserves_findings(sqlite_db, tmp_grc, tmp_path):
    """Vérifie que grc load ne touche pas aux constats ingérés et préserve leurs liens."""
    # 1. Chargement initial du référentiel GRC
    res = runner.invoke(app, ["load", "--grc-dir", str(tmp_grc)])
    assert res.exit_code == 0

    # 2. Ingestion d'un constat SARIF (technique T1190 -> R-02, vulnérabilité -> 8.8)
    sarif_data = {
        "version": "2.1.0",
        "runs": [
            {
                "tool": {"driver": {"name": "Trivy"}},
                "results": [
                    {
                        "ruleId": "CVE-2024-9999",
                        "level": "error",
                        "properties": {
                            "tags": ["T1190"],
                            "asset_id": "ast_vpn",
                        },
                        "message": {"text": "Faille critique VPN SSL"},
                    }
                ],
            }
        ],
    }
    sarif_file = tmp_path / "test.sarif"
    with open(sarif_file, "w", encoding="utf-8") as f:
        json.dump(sarif_data, f)

    session = sqlite_db()
    try:
        count = ingest_findings(session, source="sarif", filepath=str(sarif_file))
        assert count == 1
        finding = session.query(Finding).filter_by(cve="CVE-2024-9999").first()
        assert finding is not None
        assert len(finding.risks) >= 1
        assert any(r.id == "R-02" for r in finding.risks)
        assert any(c.id == "8.8" for c in finding.controls)
    finally:
        session.close()

    # 3. Ré-exécution de grc load
    res_load2 = runner.invoke(app, ["load", "--grc-dir", str(tmp_grc)])
    assert res_load2.exit_code == 0

    # 4. Vérification que le constat et ses liens sont préservés
    session = sqlite_db()
    try:
        finding_after = session.query(Finding).filter_by(cve="CVE-2024-9999").first()
        assert finding_after is not None, "Le constat a été supprimé par grc load !"
        assert any(r.id == "R-02" for r in finding_after.risks), "Le rattachement au risque R-02 a été perdu"
        assert any(c.id == "8.8" for c in finding_after.controls), "Le rattachement au contrôle 8.8 a été perdu"
    finally:
        session.close()


def test_jira_key_in_db_preserved_on_load(sqlite_db, tmp_grc):
    """Vérifie que la clé Jira posée en base est conservée si le YAML a jira_key null."""
    # 1. Chargement initial
    res = runner.invoke(app, ["load", "--grc-dir", str(tmp_grc)])
    assert res.exit_code == 0

    # 2. Ajout manuel d'une clé Jira sur un traitement en base
    session = sqlite_db()
    try:
        tr = session.query(Treatment).first()
        assert tr is not None
        target_id = tr.id
        tr.jira_key = "SEC-4242"
        session.commit()
    finally:
        session.close()

    # 3. Re-chargement via YAML (où le traitement a jira_key: null)
    res2 = runner.invoke(app, ["load", "--grc-dir", str(tmp_grc)])
    assert res2.exit_code == 0

    # 4. Vérification que la clé Jira est intacte
    session = sqlite_db()
    try:
        tr_after = session.query(Treatment).filter_by(id=target_id).first()
        assert tr_after is not None
        assert tr_after.jira_key == "SEC-4242", (
            f"La clé Jira a été écrasée : attendu 'SEC-4242', reçu '{tr_after.jira_key}'"
        )
    finally:
        session.close()


def test_risk_removed_from_yaml_pruned_from_db_and_relations(sqlite_db, tmp_grc, tmp_path):
    """Vérifie qu'un risque retiré du YAML disparaît de la base ainsi que toutes ses liaisons."""
    # 1. Chargement initial
    res = runner.invoke(app, ["load", "--grc-dir", str(tmp_grc)])
    assert res.exit_code == 0

    # Ingestion préalable d'un constat lié à R-10 (T1110)
    sarif_data = {
        "version": "2.1.0",
        "runs": [
            {
                "tool": {"driver": {"name": "Trivy"}},
                "results": [
                    {
                        "ruleId": "CVE-2024-RDP",
                        "level": "error",
                        "properties": {"tags": ["T1110"], "asset_id": "ast_vpn"},
                        "message": {"text": "Brute force RDP"},
                    }
                ],
            }
        ],
    }
    sarif_file = tmp_path / "rdp.sarif"
    with open(sarif_file, "w", encoding="utf-8") as f:
        json.dump(sarif_data, f)

    session = sqlite_db()
    try:
        ingest_findings(session, source="sarif", filepath=str(sarif_file))
        assert session.query(ScenarioOperationnel).filter_by(id="R-10").first() is not None
        # Liaison finding_risk vérifiée
        fr_links = session.execute(
            select(finding_risk_table).where(finding_risk_table.c.risk_id == "R-10")
        ).all()
        assert len(fr_links) > 0
    finally:
        session.close()

    # 2. Retrait de R-10 dans w4_operationnels.yaml
    w4_file = tmp_grc / "ebios" / "w4_operationnels.yaml"
    with open(w4_file, "r", encoding="utf-8") as f:
        w4_data = yaml.safe_load(f)
    w4_data["risks"] = [r for r in w4_data["risks"] if r["id"] != "R-10"]
    with open(w4_file, "w", encoding="utf-8") as f:
        yaml.safe_dump(w4_data, f)

    # Retrait du traitement lié à R-10 dans w5_traitements.yaml pour que la validation passe
    w5_file = tmp_grc / "ebios" / "w5_traitements.yaml"
    with open(w5_file, "r", encoding="utf-8") as f:
        w5_data = yaml.safe_load(f)
    w5_data["treatments"] = [t for t in w5_data["treatments"] if t.get("risk_id") != "R-10"]
    with open(w5_file, "w", encoding="utf-8") as f:
        yaml.safe_dump(w5_data, f)

    # 3. Re-chargement
    res2 = runner.invoke(app, ["load", "--grc-dir", str(tmp_grc)])
    assert res2.exit_code == 0

    # 4. Vérification que R-10 et ses liaisons ont disparu
    session = sqlite_db()
    try:
        assert session.query(ScenarioOperationnel).filter_by(id="R-10").first() is None
        # Associations risk_asset
        ra_count = len(session.execute(select(risk_asset_table).where(risk_asset_table.c.risk_id == "R-10")).all())
        assert ra_count == 0
        # Associations risk_control
        rc_count = len(session.execute(select(risk_control_table).where(risk_control_table.c.risk_id == "R-10")).all())
        assert rc_count == 0
        # Associations finding_risk
        fr_count = len(session.execute(select(finding_risk_table).where(finding_risk_table.c.risk_id == "R-10")).all())
        assert fr_count == 0
        # Traitement associé
        tr_count = session.query(Treatment).filter_by(risk_id="R-10").count()
        assert tr_count == 0
        # Mais le constat existe toujours !
        finding = session.query(Finding).filter_by(cve="CVE-2024-RDP").first()
        assert finding is not None
    finally:
        session.close()


def test_invalid_yaml_fails_with_exit_code_1_and_leaves_db_untouched(sqlite_db, tmp_grc):
    """Vérifie qu'un YAML invalide échoue avec code 1 et ne modifie absolument pas la base."""
    # 1. Chargement initial valide
    res = runner.invoke(app, ["load", "--grc-dir", str(tmp_grc)])
    assert res.exit_code == 0

    session = sqlite_db()
    try:
        initial_counts = get_db_counts(session)
        r01 = session.query(ScenarioOperationnel).filter_by(id="R-01").first()
        assert r01.gravite == 4
    finally:
        session.close()

    # 2. Corruption du YAML (severity = 5 hors échelle)
    w4_file = tmp_grc / "ebios" / "w4_operationnels.yaml"
    with open(w4_file, "r", encoding="utf-8") as f:
        w4_data = yaml.safe_load(f)
    w4_data["risks"][0]["severity"] = 5
    with open(w4_file, "w", encoding="utf-8") as f:
        yaml.safe_dump(w4_data, f)

    # 3. Exécution de load : doit échouer dès la phase de validation
    res_invalid = runner.invoke(app, ["load", "--grc-dir", str(tmp_grc)])
    assert res_invalid.exit_code == 1
    assert "Validation échouée" in res_invalid.stderr or "Validation échouée" in res_invalid.stdout

    # 4. Vérification que la base de données est strictement inchangée
    session = sqlite_db()
    try:
        counts_after = get_db_counts(session)
        assert initial_counts == counts_after, "La base a été altérée malgré l'échec de validation !"
        r01_after = session.query(ScenarioOperationnel).filter_by(id="R-01").first()
        assert r01_after.gravite == 4, "La valeur de gravité a été modifiée en base !"
    finally:
        session.close()


def test_reset_command(sqlite_db, tmp_grc):
    """Teste la commande grc reset avec et sans confirmation interactive."""
    # Chargement initial
    res = runner.invoke(app, ["load", "--grc-dir", str(tmp_grc)])
    assert res.exit_code == 0

    session = sqlite_db()
    try:
        assert session.query(ScenarioOperationnel).count() > 0
    finally:
        session.close()

    # Reset avec refus interactif
    res_abort = runner.invoke(app, ["reset"], input="n\n")
    assert res_abort.exit_code != 0

    session = sqlite_db()
    try:
        assert session.query(ScenarioOperationnel).count() > 0
    finally:
        session.close()

    # Reset avec confirmation --yes
    res_yes = runner.invoke(app, ["reset", "--yes"])
    assert res_yes.exit_code == 0

    session = sqlite_db()
    try:
        assert session.query(ScenarioOperationnel).count() == 0
    finally:
        session.close()


def test_relink_command(sqlite_db, tmp_grc, tmp_path):
    """Teste la commande grc relink de manière autonome."""
    res = runner.invoke(app, ["load", "--grc-dir", str(tmp_grc)])
    assert res.exit_code == 0

    # Ingestion d'un constat
    sarif_data = {
        "version": "2.1.0",
        "runs": [
            {
                "tool": {"driver": {"name": "Trivy"}},
                "results": [
                    {
                        "ruleId": "CVE-2024-TEST",
                        "level": "error",
                        "properties": {"tags": ["T1566"], "asset_id": "ast_pacs"},
                        "message": {"text": "Phishing detection"},
                    }
                ],
            }
        ],
    }
    sarif_file = tmp_path / "phish.sarif"
    with open(sarif_file, "w", encoding="utf-8") as f:
        json.dump(sarif_data, f)

    session = sqlite_db()
    try:
        ingest_findings(session, source="sarif", filepath=str(sarif_file))
        # Dissociation volontaire des risques pour tester relink
        finding = session.query(Finding).filter_by(cve="CVE-2024-TEST").first()
        finding.risks = []
        finding.controls = []
        session.commit()
        assert len(finding.risks) == 0
    finally:
        session.close()

    # Exécution de relink
    res_relink = runner.invoke(app, ["relink", "--grc-dir", str(tmp_grc)])
    assert res_relink.exit_code == 0

    session = sqlite_db()
    try:
        finding = session.query(Finding).filter_by(cve="CVE-2024-TEST").first()
        assert len(finding.risks) >= 1
        assert any(r.id == "R-01" for r in finding.risks)
        assert any(c.id == "8.8" for c in finding.controls)
    finally:
        session.close()
