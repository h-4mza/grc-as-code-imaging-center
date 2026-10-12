import csv
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent


def export_soa_csv(output_path=None):
    if output_path is None:
        output_path = ROOT / "soa_export.csv"
    else:
        output_path = Path(output_path)

    with open(ROOT / "grc/iso27001/annex_a.yaml", "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)

    controls = data.get("controls", [])
    fieldnames = [
        "id",
        "theme",
        "name",
        "is_applicable",
        "status",
        "maturity",
        "justification",
        "evidence",
    ]

    with open(output_path, "w", newline="", encoding="utf-8-sig") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames, delimiter=";")
        writer.writeheader()
        for c in controls:
            writer.writerow(
                {
                    "id": c.get("id"),
                    "theme": c.get("theme"),
                    "name": c.get("name"),
                    "is_applicable": "Oui" if c.get("is_applicable", True) else "Non",
                    "status": c.get("status", ""),
                    "maturity": c.get("maturity", 0),
                    "justification": c.get("justification", ""),
                    "evidence": c.get("evidence", ""),
                }
            )

    print(f"Export CSV de la SoA genere : {output_path} ({len(controls)} controles)")


if __name__ == "__main__":
    export_soa_csv()
