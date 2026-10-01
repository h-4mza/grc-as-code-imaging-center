import os
import requests
from requests.auth import HTTPBasicAuth

class JiraClient:
    def __init__(self):
        self.url = os.getenv("JIRA_URL", "https://your-domain.atlassian.net")
        self.email = os.getenv("JIRA_EMAIL", "admin@example.com")
        self.api_token = os.getenv("JIRA_API_TOKEN", "fake_token")
        self.project_key = os.getenv("JIRA_PROJECT_KEY", "SEC")
        self.auth = HTTPBasicAuth(self.email, self.api_token)
        
    def export_treatment(self, treatment, risk, dry_run=True):
        """Export un traitement en tant que ticket Jira."""
        
        # Structure payload basique pour Jira Cloud REST API v3
        payload = {
            "fields": {
                "project": {"key": self.project_key},
                "summary": f"[GRC] Traitement : {treatment.nom}",
                "description": {
                    "type": "doc",
                    "version": 1,
                    "content": [
                        {
                            "type": "paragraph",
                            "content": [
                                {"type": "text", "text": f"Risque couvert : {risk.nom if risk else treatment.risk_id}\n"},
                                {"type": "text", "text": f"Responsable : {treatment.responsable}\n"},
                                {"type": "text", "text": f"Échéance : {treatment.echeance}\n"},
                                {"type": "text", "text": f"Option : {treatment.option}"}
                            ]
                        }
                    ]
                },
                "issuetype": {"name": "Task"},
                "labels": [f"risk-{treatment.risk_id}"]
            }
        }
        
        if dry_run:
            print(f"[DRY-RUN] Jira ticket would be created: {payload['fields']['summary']}")
            return f"DRYRUN-{treatment.id[-4:].upper()}"
            
        # Appel réel à l'API Jira
        try:
            response = requests.post(f"{self.url}/rest/api/3/issue", json=payload, auth=self.auth)
            response.raise_for_status()
            return response.json().get("key")
        except requests.exceptions.RequestException as e:
            print(f"[ERROR] Échec de l'export Jira pour {treatment.id} : {e}")
            if e.response:
                print(e.response.text)
            raise
