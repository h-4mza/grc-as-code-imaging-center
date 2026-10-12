import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Set

import yaml

from app.services.scoring import compute_risk_view

NIST_CSF2_CATEGORIES = (
    "GV.OC",
    "GV.RM",
    "GV.RR",
    "GV.PO",
    "GV.OV",
    "GV.SC",
    "ID.AM",
    "ID.RA",
    "ID.IM",
    "PR.AA",
    "PR.AT",
    "PR.DS",
    "PR.PS",
    "PR.IR",
    "DE.CM",
    "DE.AE",
    "RS.MA",
    "RS.AN",
    "RS.CO",
    "RS.MI",
    "RC.RP",
    "RC.CO",
)


@dataclass
class RiskLevelInfo:
    id: str
    name: str
    gravite: int
    vraisemblance: int
    maturity_avg: float
    score_inherent: int
    niveau_inherent: str
    score_residuel: int
    niveau_residuel: str
    target_residual: Optional[str] = None


@dataclass
class ValidationReport:
    is_valid: bool
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    risk_summaries: List[RiskLevelInfo] = field(default_factory=list)


def _load_yaml_file(filepath: Path) -> Dict[str, Any]:
    if not filepath.exists():
        return {}
    with open(filepath, "r", encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


def _find_yaml(grc_dir: Path, relative_pattern: str) -> Optional[Path]:
    exact_path = grc_dir / relative_pattern
    if exact_path.exists():
        return exact_path
    filename = Path(relative_pattern).name
    matches = list(grc_dir.glob(f"**/{filename}"))
    if matches:
        return matches[0]
    return None


class GRCValidator:
    """Valide la cohérence, complétude et intégrité des référentiels GRC YAML."""

    def __init__(self, grc_dir: Path | str = "grc"):
        self.grc_dir = Path(grc_dir)
        self.errors: List[str] = []
        self.warnings: List[str] = []
        self.risk_summaries: List[RiskLevelInfo] = []

    def validate(self) -> ValidationReport:
        self.errors = []
        self.warnings = []
        self.risk_summaries = []

        # 1. Chargement des fichiers YAML
        bv_file = _find_yaml(self.grc_dir, "si/business_values.yaml")
        assets_file = _find_yaml(self.grc_dir, "si/assets.yaml")
        w2_file = _find_yaml(self.grc_dir, "ebios/w2_sources.yaml")
        w3_file = _find_yaml(self.grc_dir, "ebios/w3_strategiques.yaml")
        w4_file = _find_yaml(self.grc_dir, "ebios/w4_operationnels.yaml")
        w5_file = _find_yaml(self.grc_dir, "ebios/w5_traitements.yaml")
        annex_a_file = _find_yaml(self.grc_dir, "iso27001/annex_a.yaml")

        bv_data = _load_yaml_file(bv_file) if bv_file else {}
        assets_data = _load_yaml_file(assets_file) if assets_file else {}
        w2_data = _load_yaml_file(w2_file) if w2_file else {}
        w3_data = _load_yaml_file(w3_file) if w3_file else {}
        w4_data = _load_yaml_file(w4_file) if w4_file else {}
        w5_data = _load_yaml_file(w5_file) if w5_file else {}
        annex_a_data = _load_yaml_file(annex_a_file) if annex_a_file else {}

        business_values = bv_data.get("business_values", [])
        assets = assets_data.get("assets", [])
        risk_sources = w2_data.get("risk_sources", [])
        objectives = w2_data.get("objectives", [])
        sr_ov_pairs = w2_data.get("sr_ov_pairs", [])
        stakeholders = w3_data.get("stakeholders", [])
        strategic_scenarios = w3_data.get("strategic_scenarios", [])
        risks = w4_data.get("risks", [])
        treatments = w5_data.get("treatments", [])
        controls = annex_a_data.get("controls", [])

        # Dictionnaires et Ensembles d'IDs pour les références croisées
        bv_ids: Set[str] = {str(bv["id"]) for bv in business_values if "id" in bv}
        asset_ids: Set[str] = {str(a["id"]) for a in assets if "id" in a}
        sr_ids: Set[str] = {str(sr["id"]) for sr in risk_sources if "id" in sr}
        ov_ids: Set[str] = {str(ov["id"]) for ov in objectives if "id" in ov}
        srov_ids: Set[str] = {str(pair["id"]) for pair in sr_ov_pairs if "id" in pair}
        stakeholder_ids: Set[str] = {str(sh["id"]) for sh in stakeholders if "id" in sh}
        strat_sc_ids: Set[str] = {str(sc["id"]) for sc in strategic_scenarios if "id" in sc}
        risk_ids: Set[str] = {str(r["id"]) for r in risks if "id" in r}

        controls_dict: Dict[str, Dict[str, Any]] = {str(c["id"]): c for c in controls if "id" in c}
        control_ids: Set[str] = set(controls_dict.keys())

        # ---------------------------------------------------------------------
        # 1. Échelle : severity et likelihood dans [1, 4] partout. Aucune valeur 5.
        # ---------------------------------------------------------------------
        for bv in business_values:
            bv_id = bv.get("id", "inconnu")
            sev = bv.get("severity")
            if sev is None:
                self.errors.append(f"Échelle : Valeur métier '{bv_id}' n'a pas de champ 'severity'.")
            elif not isinstance(sev, int) or sev < 1 or sev > 4:
                self.errors.append(
                    f"Échelle : Valeur métier '{bv_id}' a une severity={sev} "
                    "hors de l'échelle autorisée [1, 4] (aucune valeur 5 autorisée)."
                )

        for sc in strategic_scenarios:
            sc_id = sc.get("id", "inconnu")
            lik = sc.get("likelihood")
            if lik is None:
                self.errors.append(f"Échelle : Scénario stratégique '{sc_id}' n'a pas de champ 'likelihood'.")
            elif not isinstance(lik, int) or lik < 1 or lik > 4:
                self.errors.append(
                    f"Échelle : Scénario stratégique '{sc_id}' a une likelihood={lik} "
                    "hors de l'échelle autorisée [1, 4] (aucune valeur 5 autorisée)."
                )

        for risk in risks:
            r_id = risk.get("id", "inconnu")
            sev = risk.get("severity")
            if sev is None:
                self.errors.append(f"Échelle : Risque '{r_id}' n'a pas de champ 'severity'.")
            elif not isinstance(sev, int) or sev < 1 or sev > 4:
                self.errors.append(
                    f"Échelle : Risque '{r_id}' a une severity={sev} "
                    "hors de l'échelle autorisée [1, 4] (aucune valeur 5 autorisée)."
                )

            lik = risk.get("likelihood")
            if lik is None:
                self.errors.append(f"Échelle : Risque '{r_id}' n'a pas de champ 'likelihood'.")
            elif not isinstance(lik, int) or lik < 1 or lik > 4:
                self.errors.append(
                    f"Échelle : Risque '{r_id}' a une likelihood={lik} "
                    "hors de l'échelle autorisée [1, 4] (aucune valeur 5 autorisée)."
                )

        # ---------------------------------------------------------------------
        # 2. Références croisées
        # ---------------------------------------------------------------------
        # assets.business_values -> business_values
        for asset in assets:
            a_id = asset.get("id", "inconnu")
            for b_id in asset.get("business_values", []):
                if str(b_id) not in bv_ids:
                    self.errors.append(
                        f"Références croisées : Actif '{a_id}' référence une valeur métier inexistante '{b_id}'."
                    )

        # sr_ov_pairs -> risk_sources / objectives
        for pair in sr_ov_pairs:
            pair_id = pair.get("id", "inconnu")
            sr_id = str(pair.get("sr_id"))
            if sr_id not in sr_ids:
                self.errors.append(
                    f"Références croisées : Couple SR/OV '{pair_id}' "
                    f"référence une source de risque inexistante '{sr_id}'."
                )
            ov_id = str(pair.get("ov_id"))
            if ov_id not in ov_ids:
                self.errors.append(
                    f"Références croisées : Couple SR/OV '{pair_id}' référence un objectif visé inexistant '{ov_id}'."
                )

        # strategic_scenarios -> sr_ov_pairs et stakeholders (stakeholder_id peut être null)
        for sc in strategic_scenarios:
            sc_id = sc.get("id", "inconnu")
            srov_id = str(sc.get("srov_id"))
            if srov_id not in srov_ids:
                self.errors.append(
                    f"Références croisées : Scénario stratégique '{sc_id}' "
                    f"référence un couple SR/OV inexistant '{srov_id}'."
                )
            sh_id = sc.get("stakeholder_id")
            if sh_id is not None and str(sh_id).strip().lower() not in ("", "null", "none"):
                if str(sh_id) not in stakeholder_ids:
                    self.errors.append(
                        f"Références croisées : Scénario stratégique '{sc_id}' "
                        f"référence une partie prenante inexistante '{sh_id}'."
                    )

        # risks.strategic_scenario_id -> strategic_scenarios (OBLIGATOIRE, non null)
        for risk in risks:
            r_id = risk.get("id", "inconnu")
            sc_id = risk.get("strategic_scenario_id")
            if sc_id is None or str(sc_id).strip().lower() in ("", "null", "none"):
                self.errors.append(
                    f"Références croisées : Risque '{r_id}' a un strategic_scenario_id "
                    "manquant ou null (OBLIGATOIRE, non null)."
                )
            elif str(sc_id) not in strat_sc_ids:
                self.errors.append(
                    f"Références croisées : Risque '{r_id}' référence un scénario stratégique inexistant '{sc_id}'."
                )

        # risks.assets -> assets
        for risk in risks:
            r_id = risk.get("id", "inconnu")
            for ast_id in risk.get("assets", []):
                if str(ast_id) not in asset_ids:
                    self.errors.append(
                        f"Références croisées : Risque '{r_id}' référence un actif inexistant '{ast_id}'."
                    )

        # risks.controls -> ids de annex_a.yaml (format "8.7", sans "A.")
        for risk in risks:
            r_id = risk.get("id", "inconnu")
            for ctrl_id in risk.get("controls", []):
                ctrl_str = str(ctrl_id).strip()
                if ctrl_str.startswith("A."):
                    self.errors.append(
                        f"Format : Risque '{r_id}' : contrôle '{ctrl_str}' doit être "
                        f"au format sans préfixe 'A.' (ex: '{ctrl_str[2:]}')."
                    )
                clean_ctrl_id = ctrl_str[2:] if ctrl_str.startswith("A.") else ctrl_str
                if clean_ctrl_id not in control_ids:
                    self.errors.append(
                        f"Références croisées : Risque '{r_id}' référence un contrôle ISO 27001 inconnu '{ctrl_str}'."
                    )

        # treatments.risk_id -> risks
        for tr in treatments:
            tr_id = tr.get("id", "inconnu")
            r_id = str(tr.get("risk_id"))
            if r_id not in risk_ids:
                self.errors.append(
                    f"Références croisées : Traitement '{tr_id}' référence un risque inexistant '{r_id}'."
                )

        # ---------------------------------------------------------------------
        # 3. Complétude
        # ---------------------------------------------------------------------
        srov_to_sr = {str(pair["id"]): str(pair.get("sr_id")) for pair in sr_ov_pairs if "id" in pair}
        sc_to_sr = {str(sc["id"]): srov_to_sr.get(str(sc.get("srov_id"))) for sc in strategic_scenarios if "id" in sc}
        risks_with_treatments = {str(tr["risk_id"]) for tr in treatments if tr.get("risk_id")}

        for risk in risks:
            r_id = risk.get("id", "inconnu")
            sc_id = str(risk.get("strategic_scenario_id"))
            risk_sr = sc_to_sr.get(sc_id)
            is_defaillance = (risk_sr == "sr_defaillance")

            # Au moins 1 actif
            if not risk.get("assets"):
                self.errors.append(f"Complétude : Risque '{r_id}' n'a aucun actif associé (au moins 1 requis).")

            # Au moins 1 technique ATT&CK au format Txxxx (sauf pour sr_defaillance)
            attack_techs = risk.get("attack_techniques", [])
            if not attack_techs:
                if not is_defaillance:
                    self.errors.append(
                        f"Complétude : Risque '{r_id}' n'a aucune technique ATT&CK associée (au moins 1 requise)."
                    )
            else:
                for tech in attack_techs:
                    if not re.match(r"^T\d{4}(\.\d{3})?$", str(tech).strip()):
                        self.errors.append(
                            f"Complétude : Risque '{r_id}' : technique ATT&CK '{tech}' "
                            "invalide (format attendu: Txxxx ou Txxxx.xxx)."
                        )

            # Au moins 1 contrôle
            if not risk.get("controls"):
                self.errors.append(
                    f"Complétude : Risque '{r_id}' n'a aucun contrôle ISO 27001 associé (au moins 1 requis)."
                )

            # Au moins 1 traitement
            if r_id not in risks_with_treatments:
                self.errors.append(
                    f"Complétude : Risque '{r_id}' n'a aucun traitement associé dans w5_traitements.yaml."
                )

        # Chaque traitement a un owner et une due_date
        for tr in treatments:
            tr_id = tr.get("id", "inconnu")
            if not tr.get("owner") or str(tr.get("owner")).strip() == "":
                self.errors.append(
                    f"Complétude : Traitement '{tr_id}' n'a pas de responsable ('owner' manquant ou vide)."
                )
            if not tr.get("due_date") or str(tr.get("due_date")).strip() == "":
                self.errors.append(
                    f"Complétude : Traitement '{tr_id}' n'a pas d'échéance ('due_date' manquante ou vide)."
                )

        # Chaque source de risque et chaque partie prenante est utilisée au moins une fois
        used_sr_ids = {str(pair["sr_id"]) for pair in sr_ov_pairs if pair.get("sr_id")}
        for sr_id in sr_ids:
            if sr_id not in used_sr_ids:
                self.errors.append(f"Complétude : Source de risque '{sr_id}' n'est utilisée dans aucun couple SR/OV.")

        used_stakeholder_ids = {
            str(sc["stakeholder_id"])
            for sc in strategic_scenarios
            if sc.get("stakeholder_id") and str(sc.get("stakeholder_id")).strip().lower() not in ("", "null", "none")
        }
        for sh_id in stakeholder_ids:
            if sh_id not in used_stakeholder_ids:
                self.errors.append(
                    f"Complétude : Partie prenante '{sh_id}' n'est utilisée dans aucun scénario stratégique."
                )

        # ---------------------------------------------------------------------
        # 4. Cohérence : Calcul de risque & Option "accept" <= Moyen
        # ---------------------------------------------------------------------
        for risk in risks:
            r_id = risk.get("id", "inconnu")
            r_name = risk.get("name", "")
            sev = risk.get("severity", 1) if isinstance(risk.get("severity"), int) else 1
            lik = risk.get("likelihood", 1) if isinstance(risk.get("likelihood"), int) else 1

            # Extraction des contrôles résolus
            ctrl_objs = []
            for c in risk.get("controls", []):
                clean_c = str(c).strip()
                if clean_c.startswith("A."):
                    clean_c = clean_c[2:]
                if clean_c in controls_dict:
                    ctrl_objs.append(controls_dict[clean_c])

            risk_treatments = [tr for tr in treatments if str(tr.get("risk_id")) == r_id]

            # Calcul unifié via compute_risk_view
            try:
                view = compute_risk_view(
                    risk=risk,
                    findings=[],
                    controls=ctrl_objs,
                    treatments=risk_treatments,
                )
                res_level = view["current_residual"]["niveau"]

                self.risk_summaries.append(
                    RiskLevelInfo(
                        id=r_id,
                        name=r_name,
                        gravite=sev,
                        vraisemblance=lik,
                        maturity_avg=view["maturity_avg"],
                        score_inherent=view["inherent"]["score"],
                        niveau_inherent=view["inherent"]["niveau"],
                        score_residuel=view["current_residual"]["score"],
                        niveau_residuel=view["current_residual"]["niveau"],
                        target_residual=view["target_residual"],
                    )
                )

                # Règle de cohérence pour l'option "accept"
                for tr in risk_treatments:
                    if str(tr.get("option", "")).strip().lower() == "accept":
                        if res_level not in ("Faible", "Moyen"):
                            self.errors.append(
                                f"Cohérence : Traitement '{tr.get('id')}' (risque '{r_id}') : "
                                f"l'option 'accept' exige un niveau résiduel cible <= Moyen (calculé: '{res_level}')."
                            )
            except ValueError:
                pass

        # ---------------------------------------------------------------------
        # 5. Identifiants NIST au format CSF 2.0 (signalement CSF 1.1)
        # ---------------------------------------------------------------------
        for risk in risks:
            r_id = risk.get("id", "inconnu")
            for nist_id in risk.get("nist_csf", []):
                nist_str = str(nist_id).strip()
                if nist_str.startswith("PR.AC"):
                    self.errors.append(
                        f"NIST CSF : Risque '{r_id}' utilise l'identifiant CSF 1.1 obsolète '{nist_str}' "
                        f"(la catégorie PR.AC est remplacée par PR.AA dans CSF 2.0)."
                    )
                elif nist_str.startswith("PR.PT"):
                    self.errors.append(
                        f"NIST CSF : Risque '{r_id}' utilise l'identifiant CSF 1.1 obsolète '{nist_str}' "
                        f"(la catégorie PR.PT est restructurée/supprimée dans CSF 2.0)."
                    )
                elif nist_str == "PR.DS-05" or nist_str.startswith("PR.DS-05"):
                    self.errors.append(
                        f"NIST CSF : Risque '{r_id}' utilise l'identifiant CSF 1.1 obsolète '{nist_str}' "
                        f"(sous-catégorie non reconnue dans CSF 2.0)."
                    )
                elif not any(nist_str.startswith(cat) for cat in NIST_CSF2_CATEGORIES):
                    self.errors.append(
                        f"NIST CSF : Risque '{r_id}' utilise l'identifiant '{nist_str}' "
                        "non conforme au format NIST CSF 2.0."
                    )

        # ---------------------------------------------------------------------
        # 6. Mappings réglementaires et techniques (NIS2, ATT&CK, NIST CSF 2.0)
        # ---------------------------------------------------------------------
        mappings_dir = self.grc_dir / "mappings"
        mapping_files: List[Path] = []
        if mappings_dir.exists():
            mapping_files = sorted(mappings_dir.glob("*.yaml"))
        else:
            mapping_files = sorted(self.grc_dir.glob("**/mappings/*.yaml"))

        all_mappings: List[Dict[str, Any]] = []
        for mf in mapping_files:
            m_data = _load_yaml_file(mf)
            m_list = m_data.get("mappings", [])
            if isinstance(m_list, list):
                for item in m_list:
                    if isinstance(item, dict):
                        all_mappings.append(item)

        allowed_mapping_keys = {
            "id",
            "control_id",
            "framework",
            "reference",
            "source",
            "confidence",
            "rationale",
        }
        allowed_frameworks = {"NIS2", "ATT&CK", "NIST CSF 2.0"}
        allowed_confidence = {"high", "medium", "low"}
        nist_csf2_prefixes = (
            "GV.",
            "ID.",
            "PR.AA",
            "PR.AT",
            "PR.DS",
            "PR.PS",
            "PR.IR",
            "DE.CM",
            "DE.AE",
            "RS.",
            "RC.",
        )

        seen_map_ids: Set[str] = set()

        for m in all_mappings:
            raw_mid = m.get("id")
            mid = str(raw_mid).strip() if raw_mid is not None else ""
            if not mid:
                self.errors.append("Mapping : Champ 'id' manquant ou vide.")
                continue

            # Unicité des identifiants
            if mid in seen_map_ids:
                self.errors.append(f"Mapping ID '{mid}' dupliqué.")
            else:
                seen_map_ids.add(mid)

            # Champs inconnus (schéma)
            extra_keys = set(m.keys()) - allowed_mapping_keys
            if extra_keys:
                self.errors.append(
                    f"Schéma : Mapping '{mid}' contient des champs non autorisés : {', '.join(sorted(extra_keys))}."
                )

            # Contrôle ISO associé
            raw_cid = m.get("control_id")
            if raw_cid is None:
                self.errors.append(f"Mapping '{mid}' : champ 'control_id' manquant.")
            else:
                str_cid = str(raw_cid).strip()
                if str_cid.startswith("A."):
                    self.errors.append(
                        f"Mapping '{mid}' : control_id '{str_cid}' doit être au format '8.7' sans 'A.'."
                    )
                elif str_cid not in controls_dict:
                    self.errors.append(
                        f"Mapping '{mid}' : control_id '{str_cid}' n'existe pas dans annex_a.yaml."
                    )

            # Framework
            fw = m.get("framework")
            if not fw or fw not in allowed_frameworks:
                self.errors.append(
                    f"Mapping '{mid}' : framework '{fw}' invalide (autorisés : NIS2, ATT&CK, NIST CSF 2.0)."
                )

            # Confidence
            conf = m.get("confidence")
            if conf is not None:
                conf_str = str(conf).strip().lower()
                if conf_str not in allowed_confidence:
                    self.errors.append(
                        f"Mapping '{mid}' : confidence '{conf}' invalide (autorisés : high, medium, low)."
                    )
                elif conf_str == "low":
                    self.warnings.append(
                        f"Mapping '{mid}' ({fw} -> {raw_cid}) : niveau de confiance faible (confidence: low)."
                    )

            # Format de reference
            ref = str(m.get("reference", "")).strip()
            if not ref:
                self.errors.append(f"Mapping '{mid}' : champ 'reference' manquant ou vide.")
            elif fw == "NIS2":
                if not re.match(r"^Article 21\s*\(2\)\s*[a-j](?:\b.*)?$", ref, re.IGNORECASE):
                    self.errors.append(
                        f"Mapping NIS2 '{mid}' : référence '{ref}' invalide "
                        "(format attendu : 'Article 21(2)x' avec x de a à j)."
                    )
            elif fw == "ATT&CK":
                if not re.match(r"^T\d{4}(?:\.\d{3})?(?:\s*[-:].*)?$", ref):
                    self.errors.append(
                        f"Mapping ATT&CK '{mid}' : référence '{ref}' invalide "
                        "(format attendu : Txxxx ou Txxxx.xxx)."
                    )
            elif fw == "NIST CSF 2.0":
                if not any(ref.startswith(prefix) for prefix in nist_csf2_prefixes):
                    self.errors.append(
                        f"Mapping NIST '{mid}' : référence '{ref}' non conforme au format NIST CSF 2.0 "
                        f"(attendu préfixe parmi {', '.join(nist_csf2_prefixes)})."
                    )

        # Couverture NIS2 : 10 mesures 21(2) a à j
        for letter in "abcdefghij":
            measure_label = f"Article 21(2){letter}"
            mapped_ctrl_ids = []
            for m in all_mappings:
                if m.get("framework") == "NIS2":
                    ref_str = str(m.get("reference", "")).strip()
                    m_match = re.match(r"^Article 21\s*\(2\)\s*([a-j])(?:\b.*)?$", ref_str, re.IGNORECASE)
                    if m_match and m_match.group(1).lower() == letter:
                        cid = str(m.get("control_id", "")).strip()
                        if cid and not cid.startswith("A.") and cid in controls_dict:
                            mapped_ctrl_ids.append(cid)

            unique_mapped = list(dict.fromkeys(mapped_ctrl_ids))
            applicable_ctrls = [
                cid for cid in unique_mapped if controls_dict.get(cid, {}).get("is_applicable") is True
            ]

            if not unique_mapped:
                self.errors.append(
                    f"Couverture NIS2 : La mesure {measure_label} n'est couverte par aucun contrôle."
                )
            elif not applicable_ctrls:
                self.errors.append(
                    f"Couverture NIS2 : La mesure {measure_label} n'est couverte que par des contrôles non "
                    f"applicables ({', '.join(unique_mapped)}). Au moins 1 contrôle applicable est requis."
                )

        # Couverture ATT&CK : techniques citées dans w4_operationnels.yaml
        cited_attack_techniques: Set[str] = set()
        for r in risks:
            for t in r.get("attack_techniques", []):
                t_clean = str(t).strip()
                if t_clean:
                    cited_attack_techniques.add(t_clean)

        for tech in sorted(cited_attack_techniques):
            mapped_ctrl_ids = []
            for m in all_mappings:
                if m.get("framework") == "ATT&CK":
                    ref_str = str(m.get("reference", "")).strip()
                    t_match = re.match(r"^(T\d{4}(?:\.\d{3})?)", ref_str)
                    if t_match:
                        m_tech = t_match.group(1)
                        if m_tech == tech or m_tech.split(".")[0] == tech or tech.split(".")[0] == m_tech:
                            cid = str(m.get("control_id", "")).strip()
                            if cid and not cid.startswith("A.") and cid in controls_dict:
                                mapped_ctrl_ids.append(cid)

            unique_mapped = list(dict.fromkeys(mapped_ctrl_ids))
            applicable_ctrls = [
                cid for cid in unique_mapped if controls_dict.get(cid, {}).get("is_applicable") is True
            ]

            if not unique_mapped:
                self.errors.append(
                    f"Couverture ATT&CK : La technique '{tech}' citée dans w4_operationnels.yaml "
                    "n'est couverte par aucun contrôle."
                )
            elif not applicable_ctrls:
                self.errors.append(
                    f"Couverture ATT&CK : La technique '{tech}' citée dans w4_operationnels.yaml "
                    f"n'est couverte que par des contrôles non applicables ({', '.join(unique_mapped)}). "
                    "Au moins 1 contrôle applicable est requis."
                )
            elif len(applicable_ctrls) == 1:
                self.warnings.append(
                    f"Couverture ATT&CK : La technique '{tech}' n'est couverte que par un seul "
                    f"contrôle applicable ({applicable_ctrls[0]})."
                )

        # ---------------------------------------------------------------------
        # 7. Cohérence de la Déclaration d'Applicabilité (SoA - ISO 27001)
        # ---------------------------------------------------------------------
        # a. Statut vs Maturité & Justification de non-applicabilité
        for ctrl in controls:
            cid = str(ctrl.get("id", "inconnu"))
            status = ctrl.get("status")
            maturity = ctrl.get("maturity")
            justif = str(ctrl.get("justification", "") or "").strip()

            if status == "not_implemented":
                if maturity is None or not isinstance(maturity, int) or not (0 <= maturity <= 1):
                    self.errors.append(
                        f"SoA Statut : Contrôle '{cid}' avec statut 'not_implemented' doit avoir une maturité "
                        f"entre 0 et 1 (valeur actuelle: {maturity})."
                    )
            elif status == "partial":
                if maturity is None or not isinstance(maturity, int) or not (1 <= maturity <= 3):
                    self.errors.append(
                        f"SoA Statut : Contrôle '{cid}' avec statut 'partial' doit avoir une maturité "
                        f"entre 1 et 3 (valeur actuelle: {maturity})."
                    )
            elif status == "implemented":
                if maturity is None or not isinstance(maturity, int) or not (3 <= maturity <= 5):
                    self.errors.append(
                        f"SoA Statut : Contrôle '{cid}' avec statut 'implemented' doit avoir une maturité "
                        f"entre 3 et 5 (valeur actuelle: {maturity})."
                    )
            elif status == "not_applicable":
                if maturity is not None:
                    self.errors.append(
                        f"SoA Statut : Contrôle non applicable '{cid}' ne doit pas avoir de maturité "
                        f"(valeur actuelle: {maturity}, attendu: null)."
                    )
                if not justif.startswith("Non applicable :") or len(justif[len("Non applicable :") :].strip()) == 0:
                    self.errors.append(
                        f"SoA Statut : Contrôle non applicable '{cid}' doit avoir une justification commençant "
                        "obligatoirement par 'Non applicable :' suivie du motif."
                    )
            else:
                self.errors.append(
                    f"SoA Statut : Contrôle '{cid}' a un statut '{status}' invalide ou manquant "
                    "(autorisés : not_implemented, partial, implemented, not_applicable)."
                )

        # b. Contrôle ciblé par un traitement 'todo' : pas implemented avec maturité >= 4
        for tr in treatments:
            tr_id = tr.get("id", "inconnu")
            if tr.get("status") == "todo":
                for c in tr.get("controls", []):
                    clean_c = str(c).strip()
                    if clean_c.startswith("A."):
                        clean_c = clean_c[2:]
                    ctrl = controls_dict.get(clean_c)
                    if ctrl:
                        c_status = ctrl.get("status")
                        c_mat = ctrl.get("maturity")
                        if c_status == "implemented" and c_mat is not None and isinstance(c_mat, int) and c_mat >= 4:
                            self.errors.append(
                                f"Cohérence Traitement : Contrôle '{clean_c}' ciblé par le traitement 'todo' "
                                f"'{tr_id}' ne peut pas être 'implemented' avec une maturité >= 4 "
                                f"(statut: '{c_status}', maturité: {c_mat})."
                            )

        # c. Justifications : Unicité (max 3 contrôles) et interdiction de la phrase générique
        forbidden_phrases = [
            "applicable pour la protection globale du centre d'imagerie",
            "applicable pour la protection globale",
        ]
        justification_to_controls: Dict[str, List[str]] = {}

        for ctrl in controls:
            cid = str(ctrl.get("id", "inconnu"))
            justif = str(ctrl.get("justification", "") or "").strip()
            if not justif:
                self.errors.append(f"SoA : Contrôle '{cid}' n'a pas de justification renseignée.")
                continue

            lowered_justif = justif.lower()
            for phrase in forbidden_phrases:
                if phrase in lowered_justif:
                    self.errors.append(
                        f"SoA : Contrôle '{cid}' utilise une justification générique interdite ('{justif}')."
                    )

            justification_to_controls.setdefault(justif, []).append(cid)

        for justif_text, cids in justification_to_controls.items():
            if len(cids) > 3:
                self.errors.append(
                    f"SoA : La justification suivante est partagée par plus de 3 contrôles ({len(cids)} contrôles : "
                    f"{', '.join(sorted(cids))}) : '{justif_text[:80]}...'"
                )

        # d. Preuves : tout contrôle applicable lié à un risque doit avoir un champ evidence non vide
        risk_linked_ctrl_ids: Set[str] = set()
        for r in risks:
            for c in r.get("controls", []):
                clean_c = str(c).strip()
                if clean_c.startswith("A."):
                    clean_c = clean_c[2:]
                risk_linked_ctrl_ids.add(clean_c)
        for tr in treatments:
            for c in tr.get("controls", []):
                clean_c = str(c).strip()
                if clean_c.startswith("A."):
                    clean_c = clean_c[2:]
                risk_linked_ctrl_ids.add(clean_c)

        for cid in sorted(risk_linked_ctrl_ids):
            ctrl = controls_dict.get(cid)
            if ctrl:
                is_app = ctrl.get("is_applicable")
                status = ctrl.get("status")
                if is_app is not False and status != "not_applicable":
                    ev = ctrl.get("evidence")
                    if not ev or not str(ev).strip():
                        self.errors.append(
                            f"SoA : Contrôle applicable '{cid}' lié à un risque n'a pas de champ 'evidence' "
                            "(preuve non vide requise)."
                        )

        return ValidationReport(
            is_valid=(len(self.errors) == 0),
            errors=self.errors,
            warnings=self.warnings,
            risk_summaries=self.risk_summaries,
        )


def validate_grc_yaml(grc_dir: Path | str = "grc") -> ValidationReport:
    validator = GRCValidator(grc_dir=grc_dir)
    return validator.validate()
