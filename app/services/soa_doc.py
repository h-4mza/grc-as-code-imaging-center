from pathlib import Path
from typing import Any, Dict, List, Optional

import yaml


def _load_annex_a(grc_dir: Path) -> List[Dict[str, Any]]:
    annex_path = grc_dir / "iso27001" / "annex_a.yaml"
    if not annex_path.exists():
        matches = list(grc_dir.glob("**/annex_a.yaml"))
        if matches:
            annex_path = matches[0]
        else:
            raise FileNotFoundError(f"Fichier annex_a.yaml introuvable dans {grc_dir}")

    with open(annex_path, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f) or {}
    return data.get("controls", [])


def generate_soa_markdown(
    grc_dir: Path | str = "grc",
    output_path: Optional[Path | str] = None,
) -> str:
    """Génère la Déclaration d'Applicabilité (SoA) complète en Markdown depuis annex_a.yaml."""
    grc_path = Path(grc_dir)
    controls = _load_annex_a(grc_path)

    # Dictionnaire de traduction des statuts
    status_labels = {
        "implemented": "Implémenté",
        "partial": "Partiel",
        "not_implemented": "Non implémenté",
        "not_applicable": "Non applicable",
    }

    # Thèmes ISO 27001:2022
    themes_order = [
        ("Organisationnel", "5", "Clause 5 - Contrôles organisationnels"),
        ("Personnes", "6", "Clause 6 - Contrôles liés aux personnes"),
        ("Physique", "7", "Clause 7 - Contrôles physiques"),
        ("Technologique", "8", "Clause 8 - Contrôles technologiques"),
    ]

    # Comptages globaux
    total_controls = len(controls)
    applicable_count = sum(1 for c in controls if c.get("is_applicable") is not False)
    na_count = total_controls - applicable_count

    global_status_counts: Dict[str, int] = {
        "implemented": 0,
        "partial": 0,
        "not_implemented": 0,
        "not_applicable": 0,
    }
    for c in controls:
        st = c.get("status", "not_implemented")
        if st in global_status_counts:
            global_status_counts[st] += 1

    lines: List[str] = []
    lines.append("# Déclaration d'Applicabilité (SoA) - ISO/IEC 27001:2022\n")
    lines.append("## 1. Contexte d'Application et Périmètre\n")
    lines.append(
        "La présente Déclaration d'Applicabilité (*Statement of Applicability* - SoA) documente l'état d'application, "
        "la maturité opérationnelle et les justifications de mise en œuvre pour l'ensemble des 93 contrôles de "
        "l'Annexe A de la norme ISO/IEC 27001:2022.\n"
    )
    lines.append(
        "> [!NOTE]\n"
        "> **Avertissement méthodologique :** Ce document décrit le système d'information fictif d'un centre "
        "d'imagerie médicale de 16 personnes (plateau technique d'imagerie, PACS, RIS, DPI, téléradiologie, "
        "télémaintenance biomédicale et hébergeur HDS infogéré). Les preuves documentaires et artefacts techniques "
        "mentionnés ont un caractère purement illustratif et ne constituent pas des documents réels.\n"
    )

    lines.append("## 2. Synthèse Globale des Contrôles\n")
    lines.append(f"- **Nombre total de contrôles :** {total_controls}")
    lines.append(f"- **Contrôles applicables :** {applicable_count}")
    lines.append(f"- **Contrôles non applicables :** {na_count} *(développement logiciel et ingénierie applicative)*")
    lines.append(
        f"- **Répartition par statut :** "
        f"**{global_status_counts['implemented']}** Implémenté | "
        f"**{global_status_counts['partial']}** Partiel | "
        f"**{global_status_counts['not_implemented']}** Non implémenté | "
        f"**{global_status_counts['not_applicable']}** Non applicable\n"
    )

    # Parcours des 4 thèmes
    section_index = 3
    for theme_name, clause_prefix, section_title in themes_order:
        theme_controls = [c for c in controls if str(c.get("theme", "")).strip().lower() == theme_name.lower()]

        theme_counts: Dict[str, int] = {
            "implemented": 0,
            "partial": 0,
            "not_implemented": 0,
            "not_applicable": 0,
        }
        for c in theme_controls:
            st = c.get("status", "not_implemented")
            if st in theme_counts:
                theme_counts[st] += 1

        lines.append(f"## {section_index}. Thème {theme_name} ({section_title})\n")
        lines.append("### Compteurs du thème")
        lines.append(f"- **Total contrôles :** {len(theme_controls)}")
        lines.append(
            f"- **Statuts :** "
            f"**{theme_counts['implemented']}** Implémenté(s) | "
            f"**{theme_counts['partial']}** Partiel(s) | "
            f"**{theme_counts['not_implemented']}** Non implémenté(s) | "
            f"**{theme_counts['not_applicable']}** Non applicable(s)\n"
        )

        lines.append("| ID | Nom du contrôle | Statut | Maturité | Justification | Preuve |")
        lines.append("|:---|:---|:---|:---:|:---|:---|")

        for c in theme_controls:
            cid = str(c.get("id", ""))
            cname = str(c.get("name", "")).replace("|", "\\|")
            st_raw = c.get("status", "not_implemented")
            st_display = status_labels.get(st_raw, st_raw)
            mat = c.get("maturity")
            mat_str = f"{mat}/5" if mat is not None else "-"
            justif = str(c.get("justification", "")).replace("|", "\\|").replace("\n", " ").strip()
            evidence = str(c.get("evidence", "") or "-").replace("|", "\\|").replace("\n", " ").strip()
            if not evidence:
                evidence = "-"

            lines.append(f"| **{cid}** | {cname} | {st_display} | {mat_str} | {justif} | {evidence} |")

        lines.append("")
        section_index += 1

    content = "\n".join(lines) + "\n"

    if output_path:
        out_p = Path(output_path)
        out_p.parent.mkdir(parents=True, exist_ok=True)
        with open(out_p, "w", encoding="utf-8") as f:
            f.write(content)

    return content
