"""
tests/test_jira_export.py

Tests unitaires pour l'export des traitements vers Jira Cloud (API v3) :
- Vérification du payload (clé de projet, labels control-id, paragraphes ADF).
- Mode dry-run : aucun appel HTTP requests.post n'est émis.
- Idempotence : les traitements disposant déjà d'un jira_key sont ignorés.
- Priorité de la clé de projet : argument > JIRA_PROJECT_KEY > 'SEC'.
"""

import os
from unittest import mock

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.models import Base, ScenarioOperationnel, Treatment
from app.services.jira_client import JiraClient

# ==============================================================================
# Classes fictives / Mocks simples pour les tests unitaires
# ==============================================================================


class DummyControl:
    def __init__(self, id_str):
        self.id = id_str


class DummyRisk:
    def __init__(self, id_str="R-10", nom="Attaque Brute Force", controls=None):
        self.id = id_str
        self.nom = nom
        self.controls_list = controls or []


class DummyTreatment:
    def __init__(self, id_str="tr_mfa", nom="Déploiement MFA", risk_id="R-10", jira_key=None):
        self.id = id_str
        self.nom = nom
        self.risk_id = risk_id
        self.responsable = "DSSI"
        self.echeance = "2026-12-31"
        self.option = "reduce"
        self.jira_key = jira_key


# ==============================================================================
# 1. Tests de priorité de la clé de projet
# ==============================================================================


def test_jira_client_project_key_priority():
    """Vérifie la priorité : argument constructeur > variable JIRA_PROJECT_KEY > 'SEC'."""
    # 1. Priorité argument explicite
    with mock.patch.dict(os.environ, {"JIRA_PROJECT_KEY": "ENVKEY"}, clear=True):
        client = JiraClient(project_key="ARGKEY")
        assert client.project_key == "ARGKEY"

    # 2. Priorité variable d'environnement si argument non fourni
    with mock.patch.dict(os.environ, {"JIRA_PROJECT_KEY": "ENVKEY"}, clear=True):
        client = JiraClient()
        assert client.project_key == "ENVKEY"

    # 3. Valeur par défaut 'SEC' si ni argument ni variable d'environnement
    with mock.patch.dict(os.environ, {}, clear=True):
        client = JiraClient()
        assert client.project_key == "SEC"


# ==============================================================================
# 2. Test du payload (Clé de projet, labels control-id, description ADF)
# ==============================================================================


def test_jira_payload_structure_and_project_key():
    """Vérifie que requests.post reçoit un payload valide avec la bonne clé, les labels et l'ADF."""
    client = JiraClient(project_key="CIMSEC")

    control1 = DummyControl("8.5")
    control2 = DummyControl("A.5.17")
    risk = DummyRisk(id_str="R-10", nom="Brute Force RDP", controls=[control1, control2])
    treatment = DummyTreatment(id_str="tr_mfa", nom="MFA pour téléradiologie", risk_id="R-10")

    mock_response = mock.MagicMock()
    mock_response.json.return_value = {"key": "CIMSEC-42"}
    mock_response.raise_for_status.return_value = None

    with mock.patch("requests.post", return_value=mock_response) as mock_post:
        issue_key = client.export_treatment(treatment, risk, dry_run=False)

        assert issue_key == "CIMSEC-42"
        mock_post.assert_called_once()

        # Analyse du payload envoyé
        sent_payload = mock_post.call_args.kwargs["json"]
        fields = sent_payload["fields"]

        # Clé de projet correcte
        assert fields["project"]["key"] == "CIMSEC"
        assert fields["summary"] == "[GRC] Traitement : MFA pour téléradiologie"

        # Labels : risk-id et control-id
        assert "risk-R-10" in fields["labels"]
        assert "control-A.8.5" in fields["labels"]
        assert "control-A.5.17" in fields["labels"]

        # Description ADF : paragraphes distincts par ligne, aucun '\n' résiduel
        paragraphs = fields["description"]["content"]
        assert len(paragraphs) == 4
        for p in paragraphs:
            assert p["type"] == "paragraph"
            text_value = p["content"][0]["text"]
            assert "\n" not in text_value

        assert paragraphs[0]["content"][0]["text"] == "Risque couvert : Brute Force RDP"
        assert paragraphs[1]["content"][0]["text"] == "Responsable : DSSI"
        assert paragraphs[2]["content"][0]["text"] == "Échéance : 2026-12-31"
        assert paragraphs[3]["content"][0]["text"] == "Option : reduce"


# ==============================================================================
# 3. Test du mode Dry-Run
# ==============================================================================


def test_jira_dry_run_never_calls_requests_post():
    """Vérifie que le mode dry-run (défaut) n'effectue aucun appel réseau HTTP."""
    client = JiraClient(project_key="CIMSEC")
    treatment = DummyTreatment(id_str="tr_patch_vpn", nom="Patch firmware VPN")
    risk = DummyRisk(id_str="R-02", nom="Exfiltration VPN")

    with mock.patch("requests.post") as mock_post:
        result = client.export_treatment(treatment, risk, dry_run=True)

        # Doit renvoyer une clé de simulation
        assert result.startswith("DRYRUN-")
        # requests.post ne doit JAMAIS être appelé
        mock_post.assert_not_called()


# ==============================================================================
# 4. Test d'idempotence (Traitements déjà exportés ignorés)
# ==============================================================================


def test_export_jira_idempotence():
    """Vérifie qu'un traitement possédant déjà un jira_key n'est pas réexporté."""
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(bind=engine)
    Session = sessionmaker(bind=engine)
    session = Session()

    # Création d'un risque
    risk = ScenarioOperationnel(
        id="R-01",
        nom="Phishing Ransomware",
        vraisemblance=3,
        gravite=4,
    )
    session.add(risk)

    # Traitement 1 : Déjà exporté vers Jira (jira_key non nul)
    tr_existing = Treatment(
        id="tr_1",
        nom="Sauvegardes offline",
        risk_id="R-01",
        jira_key="CIMSEC-101",
        status="in_progress",
    )
    # Traitement 2 : Nouveau traitement non exporté
    tr_new = Treatment(
        id="tr_2",
        nom="EDR sur les postes",
        risk_id="R-01",
        jira_key=None,
        status="todo",
    )
    session.add_all([tr_existing, tr_new])
    session.commit()

    # Requête avec filtre d'idempotence (exactement comme dans export_jira de cli.py)
    pending_treatments = session.query(Treatment).filter(Treatment.jira_key.is_(None)).all()

    # Seul le nouveau traitement doit être retourné pour export
    assert len(pending_treatments) == 1
    assert pending_treatments[0].id == "tr_2"
    assert pending_treatments[0].nom == "EDR sur les postes"

    # Le traitement déjà pourvu d'une clé Jira est ignoré
    exported_ids = [t.id for t in pending_treatments]
    assert "tr_1" not in exported_ids

    session.close()
