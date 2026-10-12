import re
from pathlib import Path
from typing import Any, Dict, List, Tuple

import yaml


def _natural_key(cid: str) -> Tuple[Any, ...]:
    """Clé de tri naturel pour identifiants de contrôles ISO (ex: '5.2' < '5.10')."""
    parts = []
    for p in re.split(r"(\d+)", cid):
        if p.isdigit():
            parts.append(int(p))
        elif p:
            parts.append(p)
    return tuple(parts)


def _load_yaml(path: Path) -> Any:
    if not path.exists():
        return {}
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


def generate_compliance_matrix(
    grc_dir: Path | str = "grc",
    output_path: Path | str = "docs/compliance/matrice_controles.md",
) -> str:
    """Génère la matrice de conformité croisée sous format Markdown.

    Produit 3 tableaux :
    1. Contrôle ISO | Statut | Maturité | NIS2 | NIST CSF 2.0 | Techniques ATT&CK
    2. Mesure NIS2 -> Contrôles ISO
    3. Technique ATT&CK -> Contrôles ISO
    """
    grc_path = Path(grc_dir)
    out_path = Path(output_path)

    # 1. Chargement des données
    annex_a_file = grc_path / "iso27001" / "annex_a.yaml"
    if not annex_a_file.exists():
        annex_a_file = next(grc_path.glob("**/annex_a.yaml"), None)

    controls_data = _load_yaml(annex_a_file) if annex_a_file else {}
    controls: List[Dict[str, Any]] = controls_data.get("controls", [])
    ctrl_by_id = {c["id"]: c for c in controls if "id" in c}

    # Mappings
    mappings_dir = grc_path / "mappings"
    nis2_mappings = _load_yaml(mappings_dir / "iso_nis2.yaml").get("mappings", [])
    nist_mappings = _load_yaml(mappings_dir / "iso_nist.yaml").get("mappings", [])
    attack_mappings = _load_yaml(mappings_dir / "iso_attack.yaml").get("mappings", [])

    # Risques pour l'extraction des techniques w4
    w4_file = grc_path / "ebios" / "w4_operationnels.yaml"
    if not w4_file.exists():
        w4_file = next(grc_path.glob("**/w4_operationnels.yaml"), None)
    w4_data = _load_yaml(w4_file) if w4_file else {}
    risks = w4_data.get("risks", [])

    # Indexation des mappings par control_id
    nis2_by_ctrl: Dict[str, List[Dict[str, Any]]] = {}
    for m in nis2_mappings:
        cid = m.get("control_id")
        if cid:
            nis2_by_ctrl.setdefault(cid, []).append(m)

    nist_by_ctrl: Dict[str, List[Dict[str, Any]]] = {}
    for m in nist_mappings:
        cid = m.get("control_id")
        if cid:
            nist_by_ctrl.setdefault(cid, []).append(m)

    attack_by_ctrl: Dict[str, List[Dict[str, Any]]] = {}
    for m in attack_mappings:
        cid = m.get("control_id")
        if cid:
            attack_by_ctrl.setdefault(cid, []).append(m)

    # Noms des mesures NIS2
    nis2_titles = {
        "a": "Politiques relatives à l'analyse des risques et à la sécurité des SI",
        "b": "Gestion des incidents (détection, notification, réponse)",
        "c": "Continuité des activités (sauvegardes, PCA/PRA, gestion de crise)",
        "d": "Sécurité de la chaîne d'approvisionnement et relations tiers",
        "e": "Sécurité de l'acquisition, dev, maintenance et vulnérabilités",
        "f": "Évaluation de l'efficacité des mesures de sécurité (audits, tests)",
        "g": "Pratiques de base en hygiène informatique et formation",
        "h": "Politiques d'utilisation de la cryptographie et du chiffrement",
        "i": "Sécurité des ressources humaines, contrôle d'accès et actifs",
        "j": "Authentification multifacteur (MFA) et communications sécurisées",
    }

    # Liste triée des contrôles
    sorted_controls = sorted(controls, key=lambda c: _natural_key(c.get("id", "")))

    md_lines: List[str] = []

    md_lines.append("# Matrice de Conformité et Couverture des Contrôles")
    md_lines.append("")
    md_lines.append(
        "Ce document présente la cartographie croisée des mesures de sécurité du **Centre d'Imagerie Médicale (CIM)**. "
        "Il consolide l'alignement entre les contrôles de l'**ISO/IEC 27001:2022 (Annexe A)**, les exigences de la "
        "directive européenne **NIS 2 (Article 21(2))**, le référentiel **NIST Cybersecurity Framework (CSF 2.0)** "
        "et les techniques d'attaque **MITRE ATT&CK Enterprise v14** identifiées dans l'analyse de risques EBIOS RM."
    )
    md_lines.append("")
    md_lines.append("---")
    md_lines.append("")

    # =========================================================================
    # TABLEAU 1 : Matrice Principale (Contrôles ISO -> Frameworks)
    # =========================================================================
    md_lines.append("## 1. Matrice des Contrôles ISO 27001:2022 et Mappings Multi-Référentiels")
    md_lines.append("")
    md_lines.append(
        "Le tableau suivant détaille chaque contrôle ISO 27001:2022 de la Déclaration d'Applicabilité (SoA), "
        "son statut opérationnel, son niveau de maturité (0-5), ainsi que ses correspondances "
        "NIS2, NIST CSF 2.0 et ATT&CK."
    )
    md_lines.append("")
    md_lines.append(
        "| Contrôle ISO | Statut | Maturité | NIS2 (Art. 21(2)) | NIST CSF 2.0 | Techniques ATT&CK |"
    )
    md_lines.append(
        "| :--- | :--- | :---: | :--- | :--- | :--- |"
    )

    status_labels = {
        "implemented": "Implémenté",
        "partial": "Partiel",
        "planned": "Planifié",
        "not_implemented": "Non implémenté",
        "not_applicable": "Non applicable",
    }

    for c in sorted_controls:
        cid = c.get("id", "")
        cname = c.get("name", "")
        is_app = c.get("is_applicable", True)
        raw_status = c.get("status", "implemented" if is_app else "not_applicable")
        status_disp = status_labels.get(raw_status, raw_status)
        maturity_disp = f"{c.get('maturity', 0)}/5" if is_app else "N/A"

        # NIS2
        nis2_list = nis2_by_ctrl.get(cid, [])
        nis2_refs = []
        for m in nis2_list:
            ref = m.get("reference", "")
            match = re.search(r"Article\s*21\(2\)([a-j])", ref, re.IGNORECASE)
            if match:
                nis2_refs.append(f"Art. 21(2){match.group(1).lower()}")
            else:
                nis2_refs.append(ref)
        nis2_str = ", ".join(dict.fromkeys(nis2_refs)) if nis2_refs else "-"

        # NIST CSF 2.0
        nist_list = nist_by_ctrl.get(cid, [])
        nist_refs = [m.get("reference", "").split(" - ")[0].strip() for m in nist_list]
        nist_str = ", ".join(dict.fromkeys(nist_refs)) if nist_refs else "-"

        # ATT&CK
        att_list = attack_by_ctrl.get(cid, [])
        att_refs = []
        for m in att_list:
            ref = m.get("reference", "")
            match = re.match(r"^(T\d{4}(?:\.\d{3})?)", ref)
            if match:
                att_refs.append(match.group(1))
            else:
                att_refs.append(ref)
        att_str = ", ".join(dict.fromkeys(att_refs)) if att_refs else "-"

        md_lines.append(
            f"| **{cid}** - {cname} | {status_disp} | {maturity_disp} | {nis2_str} | {nist_str} | {att_str} |"
        )

    md_lines.append("")
    md_lines.append("---")
    md_lines.append("")

    # =========================================================================
    # TABLEAU 2 : Matrice Inversée NIS2 -> Contrôles ISO 27001
    # =========================================================================
    md_lines.append("## 2. Matrice Inversée : Directive NIS 2 -> Contrôles ISO 27001:2022")
    md_lines.append("")
    md_lines.append(
        "Cette vue synthétise la conformité aux **10 mesures obligatoires de gestion des risques** prescrites par "
        "l'Article 21 paragraphe 2 de la directive NIS 2 (UE 2022/2555). "
        "Chaque mesure est couverte par un ensemble de contrôles ISO 27001 applicables."
    )
    md_lines.append("")
    md_lines.append(
        "| Mesure NIS 2 | Intitulé de l'obligation | Contrôles ISO 27001 associés | "
        "Ventilation Statut | Couverture |"
    )
    md_lines.append(
        "| :--- | :--- | :--- | :--- | :---: |"
    )

    for letter in "abcdefghij":
        mesure_key = f"Article 21(2){letter}"
        title = nis2_titles.get(letter, "")

        # Récupérer les contrôles mappés à cette mesure
        ctrl_ids: List[str] = []
        for m in nis2_mappings:
            ref = m.get("reference", "")
            match = re.search(r"Article\s*21\(2\)([a-j])", ref, re.IGNORECASE)
            if match and match.group(1).lower() == letter:
                cid = m.get("control_id")
                if cid and cid not in ctrl_ids:
                    ctrl_ids.append(cid)

        # Trier par clé naturelle
        ctrl_ids = sorted(ctrl_ids, key=_natural_key)

        # Calculer le statut de mise en oeuvre
        status_counts: Dict[str, int] = {}
        ctrl_labels = []
        for cid in ctrl_ids:
            c = ctrl_by_id.get(cid, {})
            st = c.get("status", "implemented")
            status_counts[st] = status_counts.get(st, 0) + 1
            ctrl_labels.append(f"`{cid}` ({c.get('name', '')})")

        stats_parts = []
        if status_counts.get("implemented"):
            stats_parts.append(f"{status_counts['implemented']} implémenté(s)")
        if status_counts.get("partial"):
            stats_parts.append(f"{status_counts['partial']} partiel(s)")
        if status_counts.get("planned"):
            stats_parts.append(f"{status_counts['planned']} planifié(s)")
        if status_counts.get("not_implemented"):
            stats_parts.append(f"{status_counts['not_implemented']} non implémenté(s)")
        if status_counts.get("not_applicable"):
            stats_parts.append(f"{status_counts['not_applicable']} non applicable(s)")

        ventilation_str = ", ".join(stats_parts) if stats_parts else "-"
        ctrl_str = "<br>".join(ctrl_labels) if ctrl_labels else "-"
        couverture_str = "✅ Conforme" if ctrl_ids else "❌ Non couvert"

        md_lines.append(
            f"| **{mesure_key}** | {title} | {ctrl_str} | {ventilation_str} | {couverture_str} |"
        )

    md_lines.append("")
    md_lines.append("---")
    md_lines.append("")

    # =========================================================================
    # TABLEAU 3 : Matrice Inversée MITRE ATT&CK -> Contrôles ISO 27001
    # =========================================================================
    md_lines.append("## 3. Matrice Inversée : MITRE ATT&CK -> Contrôles ISO 27001:2022")
    md_lines.append("")
    md_lines.append(
        "Cette vue associe chaque **technique d'attaque MITRE ATT&CK** rencontrée dans les scénarios "
        "opérationnels EBIOS RM (Atelier 4) aux mesures préventives et détectives de l'ISO 27001:2022. "
        "Elle met en évidence les mitigations officielles et garantit une défense en profondeur équilibrée."
    )
    md_lines.append("")
    md_lines.append(
        "| Technique ATT&CK | Nom | Mitigations ATT&CK | Contrôles ISO 27001 Associés | Statuts | Défense |"
    )
    md_lines.append(
        "| :--- | :--- | :--- | :--- | :--- | :---: |"
    )

    # Récupération de toutes les techniques w4
    cited_techniques: Dict[str, List[str]] = {}
    for r in risks:
        for t in r.get("attack_techniques", []):
            t_clean = str(t).strip()
            if t_clean:
                cited_techniques.setdefault(t_clean, []).append(r.get("id", ""))

    sorted_techs = sorted(cited_techniques.keys())

    for tech in sorted_techs:
        # Trouver les mappings ATT&CK pour cette technique
        tech_mappings: List[Dict[str, Any]] = []
        for m in attack_mappings:
            ref = str(m.get("reference", "")).strip()
            match = re.match(r"^(T\d{4}(?:\.\d{3})?)", ref)
            if match and (match.group(1) == tech or match.group(1).split(".")[0] == tech):
                tech_mappings.append(m)

        # Extraire le nom de la technique depuis les mappings
        tech_name = tech
        if tech_mappings:
            ref_first = tech_mappings[0].get("reference", "")
            if " - " in ref_first:
                tech_name = ref_first.split(" - ", 1)[1].strip()

        # Extraire les mitigations ATT&CK mentionnées dans rationale
        mit_ids: List[str] = []
        ctrl_entries: List[str] = []
        status_counts: Dict[str, int] = {}
        has_detection = False
        has_prevention = False

        for m in tech_mappings:
            cid = m.get("control_id")
            c = ctrl_by_id.get(cid, {})
            c_name = c.get("name", "")
            c_stat = c.get("status", "implemented")
            status_counts[c_stat] = status_counts.get(c_stat, 0) + 1

            rat = m.get("rationale", "")
            mit_matches = re.findall(r"M10\d{2}", rat)
            for mm in mit_matches:
                if mm not in mit_ids:
                    mit_ids.append(mm)

            if "détect" in rat.lower() or "audit" in rat.lower() or cid == "8.16":
                has_detection = True
                ctrl_entries.append(f"`{cid}` ({c_name}) *(Détection)*")
            else:
                has_prevention = True
                ctrl_entries.append(f"`{cid}` ({c_name}) *(Préventif)*")

        mits_str = ", ".join(mit_ids) if mit_ids else "Audit / Monitoring"
        ctrls_str = "<br>".join(ctrl_entries) if ctrl_entries else "-"

        stats_parts = []
        if status_counts.get("implemented"):
            stats_parts.append(f"{status_counts['implemented']} implémenté(s)")
        if status_counts.get("partial"):
            stats_parts.append(f"{status_counts['partial']} partiel(s)")
        if status_counts.get("planned"):
            stats_parts.append(f"{status_counts['planned']} planifié(s)")
        if status_counts.get("not_implemented"):
            stats_parts.append(f"{status_counts['not_implemented']} non implémenté(s)")
        if status_counts.get("not_applicable"):
            stats_parts.append(f"{status_counts['not_applicable']} non applicable(s)")
        stats_str = ", ".join(stats_parts) if stats_parts else "-"

        if has_prevention and has_detection:
            defense_str = "🛡️ Prévention & Détection"
        elif has_prevention:
            defense_str = "🛡️ Préventif seul"
        elif has_detection:
            defense_str = "👁️ Détection seule"
        else:
            defense_str = "⚠️ Partiel"

        md_lines.append(
            f"| **{tech}** | {tech_name} | {mits_str} | {ctrls_str} | {stats_str} | {defense_str} |"
        )

    md_content = "\n".join(md_lines) + "\n"

    # Écriture dans le fichier
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(md_content)

    return md_content
