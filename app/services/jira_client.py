import os
import requests
from requests.auth import HTTPBasicAuth


class JiraClient:
    def __init__(self, project_key: str = None):
        """
        Initialise le client Jira Cloud (API v3).
        Priorité pour la clé de projet :
        argument > variable d'environnement JIRA_PROJECT_KEY > 'SEC'
        """
        self.url = os.getenv("JIRA_URL", "https://your-domain.atlassian.net").rstrip("/")
        self.email = os.getenv("JIRA_EMAIL", "admin@example.com")
        self.api_token = os.getenv("JIRA_API_TOKEN", "fake_token")
        self.project_key = project_key or os.getenv("JIRA_PROJECT_KEY") or "SEC"
        self.auth = HTTPBasicAuth(self.email, self.api_token)

    def export_treatment(self, treatment, risk=None, dry_run: bool = True):
        """Export un traitement en tant que ticket Jira (Task)."""
        # Construction des labels : risk-id et un label control-id par contrôle associé
        labels = [f"risk-{treatment.risk_id}"]
        if risk and hasattr(risk, "controls_list") and risk.controls_list:
            for ctrl in risk.controls_list:
                raw_id = str(getattr(ctrl, "id", ctrl)).strip().replace(" ", "")
                ctrl_id = raw_id if raw_id.startswith("A.") else f"A.{raw_id}"
                labels.append(f"control-{ctrl_id}")

        # Déduplication des labels en conservant l'ordre
        labels = list(dict.fromkeys(labels))

        # Description au format Atlassian Document Format (ADF)
        # Un paragraphe par ligne pour garantir un affichage correct sans retour à la ligne ignoré
        risk_name = risk.nom if (risk and hasattr(risk, "nom")) else (treatment.risk_id or "Non spécifié")
        description_paragraphs = [
            {
                "type": "paragraph",
                "content": [{"type": "text", "text": f"Risque couvert : {risk_name}"}],
            },
            {
                "type": "paragraph",
                "content": [{"type": "text", "text": f"Responsable : {treatment.responsable or 'Non assigné'}"}],
            },
            {
                "type": "paragraph",
                "content": [{"type": "text", "text": f"Échéance : {treatment.echeance or 'Non définie'}"}],
            },
            {
                "type": "paragraph",
                "content": [{"type": "text", "text": f"Option : {treatment.option or 'reduce'}"}],
            },
        ]

        payload = {
            "fields": {
                "project": {"key": self.project_key},
                "summary": f"[GRC] Traitement : {treatment.nom}",
                "description": {
                    "type": "doc",
                    "version": 1,
                    "content": description_paragraphs,
                },
                "issuetype": {"name": "Task"},
                "labels": labels,
            }
        }

        if dry_run:
            print(f"[DRY-RUN] Jira ticket would be created: {payload['fields']['summary']} (Project: {self.project_key}, Labels: {labels})")
            return f"DRYRUN-{treatment.id[-4:].upper()}"

        # Appel réel à l'API Jira Cloud v3
        try:
            response = requests.post(f"{self.url}/rest/api/3/issue", json=payload, auth=self.auth)
            response.raise_for_status()
            return response.json().get("key")
        except requests.exceptions.RequestException as e:
            print(f"[ERROR] Échec de l'export Jira pour {treatment.id} : {e}")
            if hasattr(e, "response") and e.response is not None:
                print(e.response.text)
            raise
