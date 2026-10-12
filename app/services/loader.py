"""
app/services/loader.py

Service de chargement idempotent et de synchronisation des référentiels GRC YAML en base :
- Validation préalable stricte (abandon immédiat sans toucher à la base en cas d'erreur).
- Upsert de toutes les entités définies dans les fichiers YAML (dans une transaction unique).
- Élagage (prune) des entités et relations orphelines retirées des YAML.
- Préservation absolue des constats (findings) et des clés Jira existantes en base.
- Rattachement dynamique (relink) des constats aux scénarios opérationnels et contrôles.
"""

import json
from pathlib import Path
from typing import Any, Dict, List, Optional

import yaml
from sqlalchemy.orm import Session

from app import models
from app.models import (
    asset_bv_table,
    finding_control_table,
    finding_risk_table,
    risk_asset_table,
    risk_control_table,
)


def load_yaml(filepath: Path | str) -> Dict[str, Any]:
    """Charge un fichier YAML en dictionnaire de manière sécurisée."""
    path = Path(filepath)
    if not path.exists():
        return {}
    with open(path, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)
        return data if isinstance(data, dict) else {}


def relink_findings(db: Session) -> int:
    """
    Recalcule les liens constat -> scénario et constat -> contrôle :
    - constat -> scénario selon les techniques MITRE ATT&CK actuelles.
    - constat -> contrôle selon la règle d'ingestion (ex: contrôle 8.8 Gestion des vulnérabilités).
    """
    findings = db.query(models.Finding).all()
    all_risks = db.query(models.ScenarioOperationnel).all()
    ctrl_vuln = db.query(models.Control).filter_by(id="8.8").first()

    for finding in findings:
        # 1. Rattachement constat -> scénarios de risque
        if finding.technique_attack:
            matched_risks = []
            for r in all_risks:
                if not r.techniques_attack:
                    continue
                try:
                    techniques = json.loads(r.techniques_attack)
                    if isinstance(techniques, list) and finding.technique_attack in techniques:
                        matched_risks.append(r)
                    elif finding.technique_attack in str(r.techniques_attack):
                        matched_risks.append(r)
                except Exception:
                    if finding.technique_attack in str(r.techniques_attack):
                        matched_risks.append(r)
            finding.risks = matched_risks
        else:
            finding.risks = []

        # 2. Rattachement constat -> contrôle (règle d'ingestion standard)
        if ctrl_vuln:
            finding.controls = [ctrl_vuln]
        else:
            finding.controls = []

    return len(findings)


def load_grc_idempotent(db: Session, grc_dir: str = "grc") -> Dict[str, int]:
    """
    Charge de manière idempotente les données GRC en base :
    1. Lecture de tous les fichiers YAML.
    2. Prune des enregistrements supprimés des YAML (en respectant l'ordre des clés étrangères).
    3. Upsert des entités YAML (conservation des jira_key en base si YAML a null).
    4. Relink des constats existants.
    """
    root = Path(grc_dir)

    # 1. Chargement des fichiers YAML
    bv_data = load_yaml(root / "si" / "business_values.yaml")
    assets_data = load_yaml(root / "si" / "assets.yaml")
    w2_data = load_yaml(root / "ebios" / "w2_sources.yaml")
    w3_data = load_yaml(root / "ebios" / "w3_strategiques.yaml")
    iso_data = load_yaml(root / "iso27001" / "annex_a.yaml")
    w4_data = load_yaml(root / "ebios" / "w4_operationnels.yaml")
    w5_data = load_yaml(root / "ebios" / "w5_traitements.yaml")

    # Mappings ISO / NIS2 / ATT&CK / NIST
    mapping_files = ["iso_nis2.yaml", "iso_attack.yaml", "iso_nist.yaml"]
    all_mappings: List[Dict[str, Any]] = []
    mappings_dir = root / "mappings"
    if mappings_dir.exists():
        for mf in sorted(mappings_dir.glob("*.yaml")):
            m_data = load_yaml(mf)
            all_mappings.extend(m_data.get("mappings", []))
    else:
        for mf_name in mapping_files:
            m_data = load_yaml(root / "mappings" / mf_name)
            all_mappings.extend(m_data.get("mappings", []))

    # Collecte des identifiants YAML cibles
    yaml_bv_ids = {bv["id"] for bv in bv_data.get("business_values", []) if "id" in bv}
    yaml_asset_ids = {a["id"] for a in assets_data.get("assets", []) if "id" in a}
    yaml_sr_ids = {sr["id"] for sr in w2_data.get("risk_sources", []) if "id" in sr}
    yaml_ov_ids = {ov["id"] for ov in w2_data.get("objectives", []) if "id" in ov}
    yaml_srov_ids = {srov["id"] for srov in w2_data.get("sr_ov_pairs", []) if "id" in srov}
    yaml_pp_ids = {pp["id"] for pp in w3_data.get("stakeholders", []) if "id" in pp}
    yaml_strat_ids = {sc["id"] for sc in w3_data.get("strategic_scenarios", []) if "id" in sc}
    yaml_ctrl_ids = {str(c["id"]) for c in iso_data.get("controls", []) if "id" in c}
    yaml_risk_ids = {r["id"] for r in w4_data.get("risks", []) if "id" in r}
    yaml_mapping_ids = {m["id"] for m in all_mappings if "id" in m}
    yaml_treatment_ids = {t["id"] for t in w5_data.get("treatments", []) if "id" in t}

    # 2. PRUNE (Ordre inverse des dépendances pour respecter les contraintes d'intégrité)

    # 2.1 Traitements
    for tr in db.query(models.Treatment).all():
        if tr.id not in yaml_treatment_ids:
            db.delete(tr)

    # 2.2 Mappings de contrôles
    for m in db.query(models.ControlMapping).all():
        if m.id not in yaml_mapping_ids:
            db.delete(m)

    # 2.3 Scénarios opérationnels (risques) et leurs tables d'association
    for r in db.query(models.ScenarioOperationnel).all():
        if r.id not in yaml_risk_ids:
            db.execute(risk_asset_table.delete().where(risk_asset_table.c.risk_id == r.id))
            db.execute(risk_control_table.delete().where(risk_control_table.c.risk_id == r.id))
            db.execute(finding_risk_table.delete().where(finding_risk_table.c.risk_id == r.id))
            for tr in db.query(models.Treatment).filter_by(risk_id=r.id).all():
                db.delete(tr)
            db.delete(r)

    # 2.4 Scénarios stratégiques
    for s in db.query(models.ScenarioStrategique).all():
        if s.id not in yaml_strat_ids:
            db.delete(s)

    # 2.5 Parties prenantes
    for pp in db.query(models.PartiePrenante).all():
        if pp.id not in yaml_pp_ids:
            db.delete(pp)

    # 2.6 Couples SR-OV
    for srov in db.query(models.CoupleSROV).all():
        if srov.id not in yaml_srov_ids:
            db.delete(srov)

    # 2.7 Objectifs visés
    for ov in db.query(models.ObjectifVise).all():
        if ov.id not in yaml_ov_ids:
            db.delete(ov)

    # 2.8 Sources de risques
    for sr in db.query(models.SourceRisque).all():
        if sr.id not in yaml_sr_ids:
            db.delete(sr)

    # 2.9 Contrôles ISO
    for ctrl in db.query(models.Control).all():
        if ctrl.id not in yaml_ctrl_ids:
            db.execute(risk_control_table.delete().where(risk_control_table.c.control_id == ctrl.id))
            db.execute(finding_control_table.delete().where(finding_control_table.c.control_id == ctrl.id))
            for m in db.query(models.ControlMapping).filter_by(control_id=ctrl.id).all():
                db.delete(m)
            db.delete(ctrl)

    # 2.10 Actifs
    for asset in db.query(models.Asset).all():
        if asset.id not in yaml_asset_ids:
            db.execute(asset_bv_table.delete().where(asset_bv_table.c.asset_id == asset.id))
            db.execute(risk_asset_table.delete().where(risk_asset_table.c.asset_id == asset.id))
            db.delete(asset)

    # 2.11 Valeurs métier
    for bv in db.query(models.BusinessValue).all():
        if bv.id not in yaml_bv_ids:
            db.execute(asset_bv_table.delete().where(asset_bv_table.c.bv_id == bv.id))
            db.delete(bv)

    db.flush()

    # 3. UPSERT (Ordre direct des dépendances)

    # 3.1 Valeurs métier
    for bv in bv_data.get("business_values", []):
        existing_bv = db.query(models.BusinessValue).filter_by(id=bv["id"]).first()
        if existing_bv:
            existing_bv.nom = bv["name"]
            existing_bv.processus = bv.get("process")
            existing_bv.evenement_redoute = bv.get("feared_event")
            existing_bv.gravite = bv.get("severity")
        else:
            db.add(
                models.BusinessValue(
                    id=bv["id"],
                    nom=bv["name"],
                    processus=bv.get("process"),
                    evenement_redoute=bv.get("feared_event"),
                    gravite=bv.get("severity"),
                )
            )
    db.flush()

    # 3.2 Actifs et rattachement aux valeurs métier
    for asset in assets_data.get("assets", []):
        existing_asset = db.query(models.Asset).filter_by(id=asset["id"]).first()
        if existing_asset:
            existing_asset.nom = asset["name"]
            existing_asset.type = asset.get("type")
            existing_asset.criticite = asset.get("criticality")
        else:
            existing_asset = models.Asset(
                id=asset["id"],
                nom=asset["name"],
                type=asset.get("type"),
                criticite=asset.get("criticality"),
            )
            db.add(existing_asset)

        bv_ids = asset.get("business_values", [])
        if bv_ids:
            existing_asset.valeurs_metier = (
                db.query(models.BusinessValue).filter(models.BusinessValue.id.in_(bv_ids)).all()
            )
        else:
            existing_asset.valeurs_metier = []
    db.flush()

    # 3.3 Sources de risques
    for sr in w2_data.get("risk_sources", []):
        existing_sr = db.query(models.SourceRisque).filter_by(id=sr["id"]).first()
        if existing_sr:
            existing_sr.nom = sr["name"]
            existing_sr.type = sr.get("type")
            existing_sr.motivation = sr.get("motivation")
            existing_sr.ressources = sr.get("resources")
            existing_sr.rationale = sr.get("rationale")
        else:
            db.add(
                models.SourceRisque(
                    id=sr["id"],
                    nom=sr["name"],
                    type=sr.get("type"),
                    motivation=sr.get("motivation"),
                    ressources=sr.get("resources"),
                    rationale=sr.get("rationale"),
                )
            )

    # 3.4 Objectifs visés
    for ov in w2_data.get("objectives", []):
        existing_ov = db.query(models.ObjectifVise).filter_by(id=ov["id"]).first()
        if existing_ov:
            existing_ov.nom = ov["name"]
            existing_ov.description = ov.get("description")
        else:
            db.add(models.ObjectifVise(id=ov["id"], nom=ov["name"], description=ov.get("description")))

    # 3.5 Couples SR-OV
    for srov in w2_data.get("sr_ov_pairs", []):
        existing_srov = db.query(models.CoupleSROV).filter_by(id=srov["id"]).first()
        if existing_srov:
            existing_srov.sr_id = srov.get("sr_id")
            existing_srov.ov_id = srov.get("ov_id")
            existing_srov.pertinence = srov.get("relevance")
            existing_srov.description = srov.get("description")
        else:
            db.add(
                models.CoupleSROV(
                    id=srov["id"],
                    sr_id=srov.get("sr_id"),
                    ov_id=srov.get("ov_id"),
                    pertinence=srov.get("relevance"),
                    description=srov.get("description"),
                )
            )
    db.flush()

    # 3.6 Parties prenantes
    for pp in w3_data.get("stakeholders", []):
        existing_pp = db.query(models.PartiePrenante).filter_by(id=pp["id"]).first()
        if existing_pp:
            existing_pp.nom = pp["name"]
            existing_pp.type = pp.get("type")
            existing_pp.niveau_menace = pp.get("threat_level")
            existing_pp.dependance = str(pp.get("dependency"))
            existing_pp.penetration = pp.get("penetration")
            existing_pp.maturity = pp.get("maturity")
            existing_pp.trust = pp.get("trust")
            existing_pp.description = pp.get("description")
        else:
            db.add(
                models.PartiePrenante(
                    id=pp["id"],
                    nom=pp["name"],
                    type=pp.get("type"),
                    niveau_menace=pp.get("threat_level"),
                    dependance=str(pp.get("dependency")),
                    penetration=pp.get("penetration"),
                    maturity=pp.get("maturity"),
                    trust=pp.get("trust"),
                    description=pp.get("description"),
                )
            )
    db.flush()

    # 3.7 Scénarios stratégiques
    for sc in w3_data.get("strategic_scenarios", []):
        sh_id: Optional[str] = sc.get("stakeholder_id")
        if sh_id and str(sh_id).strip().lower() in ("none", "null", ""):
            sh_id = None

        existing_sc = db.query(models.ScenarioStrategique).filter_by(id=sc["id"]).first()
        if existing_sc:
            existing_sc.nom = sc["name"]
            existing_sc.srov_id = sc.get("srov_id")
            existing_sc.partie_prenante_id = sh_id
            existing_sc.vraisemblance = sc.get("likelihood")
            existing_sc.description = sc.get("description")
            existing_sc.attack_path = json.dumps(sc.get("attack_path", []))
            existing_sc.ecosystem_measures = json.dumps(sc.get("ecosystem_measures", []))
        else:
            db.add(
                models.ScenarioStrategique(
                    id=sc["id"],
                    nom=sc["name"],
                    srov_id=sc.get("srov_id"),
                    partie_prenante_id=sh_id,
                    vraisemblance=sc.get("likelihood"),
                    description=sc.get("description"),
                    attack_path=json.dumps(sc.get("attack_path", [])) if sc.get("attack_path") else None,
                    ecosystem_measures=json.dumps(sc.get("ecosystem_measures", []))
                    if sc.get("ecosystem_measures")
                    else None,
                )
            )
    db.flush()

    # 3.8 Contrôles ISO
    for ctrl in iso_data.get("controls", []):
        cid = str(ctrl["id"])
        existing_ctrl = db.query(models.Control).filter_by(id=cid).first()
        if existing_ctrl:
            existing_ctrl.name = ctrl["name"]
            existing_ctrl.description = ctrl.get("description")
            existing_ctrl.theme = ctrl.get("theme")
            existing_ctrl.is_applicable = ctrl.get("is_applicable", True)
            existing_ctrl.justification = ctrl.get("justification")
            existing_ctrl.status = ctrl.get("status")
            existing_ctrl.maturity = ctrl.get("maturity")
            existing_ctrl.evidence = ctrl.get("evidence")
        else:
            db.add(
                models.Control(
                    id=cid,
                    name=ctrl["name"],
                    description=ctrl.get("description"),
                    theme=ctrl.get("theme"),
                    is_applicable=ctrl.get("is_applicable", True),
                    justification=ctrl.get("justification"),
                    status=ctrl.get("status"),
                    maturity=ctrl.get("maturity"),
                    evidence=ctrl.get("evidence"),
                )
            )
    db.flush()

    # 3.9 Scénarios opérationnels
    for risk in w4_data.get("risks", []):
        rid = risk["id"]
        asset_ids = risk.get("assets", [])
        control_ids = risk.get("controls", [])
        nist = risk.get("nist_csf", [])

        existing_risk = db.query(models.ScenarioOperationnel).filter_by(id=rid).first()
        if existing_risk:
            existing_risk.nom = risk["name"]
            existing_risk.sc_strat_id = risk.get("strategic_scenario_id")
            existing_risk.techniques_attack = json.dumps(risk.get("attack_techniques", []))
            existing_risk.vraisemblance = risk.get("likelihood")
            existing_risk.gravite = risk.get("severity")
            existing_risk.rationale = risk.get("rationale")
            existing_risk.description = risk.get("description")
            existing_risk.nist_csf = json.dumps(nist)
        else:
            existing_risk = models.ScenarioOperationnel(
                id=rid,
                nom=risk["name"],
                sc_strat_id=risk.get("strategic_scenario_id"),
                techniques_attack=json.dumps(risk.get("attack_techniques", [])),
                vraisemblance=risk.get("likelihood"),
                gravite=risk.get("severity"),
                rationale=risk.get("rationale"),
                description=risk.get("description"),
                nist_csf=json.dumps(nist),
            )
            db.add(existing_risk)

        if asset_ids:
            existing_risk.assets = db.query(models.Asset).filter(models.Asset.id.in_(asset_ids)).all()
        else:
            existing_risk.assets = []

        if control_ids:
            search_cids = list(set([str(c) for c in control_ids] + [str(c).replace("A.", "") for c in control_ids]))
            existing_risk.controls_list = db.query(models.Control).filter(models.Control.id.in_(search_cids)).all()
        else:
            existing_risk.controls_list = []
    db.flush()

    # 3.10 Mappings
    allowed_mapping_fields = {
        "id",
        "control_id",
        "framework",
        "reference",
        "source",
        "confidence",
        "rationale",
    }
    for m in all_mappings:
        mid = m["id"]
        extra_keys = set(m.keys()) - allowed_mapping_fields
        if extra_keys:
            raise ValueError(
                f"Champ inconnu dans le mapping '{mid}' : {', '.join(sorted(extra_keys))}. "
                f"Champs autorisés : {', '.join(sorted(allowed_mapping_fields))}."
            )
        existing_m = db.query(models.ControlMapping).filter_by(id=mid).first()
        if existing_m:
            existing_m.control_id = str(m["control_id"])
            existing_m.framework = m.get("framework")
            existing_m.reference = m.get("reference")
            existing_m.source = m.get("source")
            existing_m.confidence = m.get("confidence")
            existing_m.rationale = m.get("rationale")
        else:
            db.add(
                models.ControlMapping(
                    id=mid,
                    control_id=str(m["control_id"]),
                    framework=m.get("framework"),
                    reference=m.get("reference"),
                    source=m.get("source"),
                    confidence=m.get("confidence"),
                    rationale=m.get("rationale"),
                )
            )
    db.flush()

    # 3.11 Traitements (Règle clé Jira : si YAML a null et la base a une clé, la base gagne)
    for tr in w5_data.get("treatments", []):
        tid = tr["id"]
        ctrls = tr.get("controls", [])
        ctrls_val = json.dumps(ctrls) if isinstance(ctrls, list) else ctrls
        existing_tr = db.query(models.Treatment).filter_by(id=tid).first()

        yaml_jira = tr.get("jira_key")
        if existing_tr and existing_tr.jira_key and (
            yaml_jira is None or str(yaml_jira).strip().lower() in ("none", "null", "")
        ):
            final_jira = existing_tr.jira_key
        else:
            final_jira = yaml_jira

        if existing_tr:
            existing_tr.nom = tr["name"]
            existing_tr.risk_id = tr.get("risk_id")
            existing_tr.option = tr.get("option")
            existing_tr.echeance = tr.get("due_date")
            existing_tr.responsable = tr.get("owner")
            existing_tr.jira_key = final_jira
            existing_tr.status = tr.get("status", "todo")
            existing_tr.expected_residual = tr.get("expected_residual")
            existing_tr.accepted_by = tr.get("accepted_by")
            existing_tr.review_date = tr.get("review_date")
            existing_tr.controls = ctrls_val
        else:
            db.add(
                models.Treatment(
                    id=tid,
                    nom=tr["name"],
                    risk_id=tr.get("risk_id"),
                    option=tr.get("option"),
                    echeance=tr.get("due_date"),
                    responsable=tr.get("owner"),
                    jira_key=final_jira,
                    status=tr.get("status", "todo"),
                    expected_residual=tr.get("expected_residual"),
                    accepted_by=tr.get("accepted_by"),
                    review_date=tr.get("review_date"),
                    controls=ctrls_val,
                )
            )
    db.flush()

    # 4. Relink des constats existants
    relinked_count = relink_findings(db)

    return {
        "business_values": len(yaml_bv_ids),
        "assets": len(yaml_asset_ids),
        "risk_sources": len(yaml_sr_ids),
        "objectives": len(yaml_ov_ids),
        "sr_ov_pairs": len(yaml_srov_ids),
        "stakeholders": len(yaml_pp_ids),
        "strategic_scenarios": len(yaml_strat_ids),
        "controls": len(yaml_ctrl_ids),
        "risks": len(yaml_risk_ids),
        "mappings": len(yaml_mapping_ids),
        "treatments": len(yaml_treatment_ids),
        "relinked_findings": relinked_count,
    }
