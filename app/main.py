import re

from fastapi import Depends, FastAPI
from sqlalchemy.orm import Session, selectinload

from app.db import get_db
from app.models import Control, Finding, ScenarioOperationnel, Treatment
from app.services.scoring import compute_risk_view

app = FastAPI(
    title="GRC API",
    description="API de pilotage GRC as-code (EBIOS, ISO 27001, NIS2)",
    version="1.0.0",
)


@app.get("/")
def root():
    return {"message": "Bienvenue sur l'API GRC-as-code"}


@app.get("/risks")
def get_risks(db: Session = Depends(get_db)):
    scenarios = (
        db.query(ScenarioOperationnel)
        .options(
            selectinload(ScenarioOperationnel.controls_list),
            selectinload(ScenarioOperationnel.findings),
            selectinload(ScenarioOperationnel.treatments),
        )
        .all()
    )
    results = []
    for sc in scenarios:
        view = compute_risk_view(sc, sc.findings)
        results.append(
            {
                "id": sc.id,
                "nom": sc.nom,
                "scores": {
                    "score_inherent": view["inherent"]["score"],
                    "niveau_inherent": view["inherent"]["niveau"],
                    "score_residuel": view["current_residual"]["score"],
                    "niveau_residuel": view["current_residual"]["niveau"],
                    "maturity_avg": view["maturity_avg"],
                    "likelihood_adjusted": view["likelihood_adjusted"],
                },
                "inherent": view["inherent"],
                "current_residual": view["current_residual"],
                "target_residual": view["target_residual"],
                "constats_ouverts": len(sc.findings),
            }
        )
    return results


@app.get("/controls")
def get_controls(db: Session = Depends(get_db)):
    controls = db.query(Control).all()
    return controls


@app.get("/kpi/overview")
def get_kpi_overview(db: Session = Depends(get_db)):
    total_risks = db.query(ScenarioOperationnel).count()
    total_controls = db.query(Control).count()
    controls_en_place = db.query(Control).filter(Control.status == "implemented").count()
    total_findings = db.query(Finding).count()
    total_treatments = db.query(Treatment).count()

    risques_critiques = 0
    scenarios = (
        db.query(ScenarioOperationnel)
        .options(
            selectinload(ScenarioOperationnel.controls_list),
            selectinload(ScenarioOperationnel.findings),
            selectinload(ScenarioOperationnel.treatments),
        )
        .all()
    )

    findings_stats = {"error": 0, "warning": 0, "info": 0}
    for f_obj in db.query(Finding).all():
        findings_stats[f_obj.severite] = findings_stats.get(f_obj.severite, 0) + 1

    for sc in scenarios:
        view = compute_risk_view(sc, sc.findings)
        if view["current_residual"]["niveau"] == "Critique":
            risques_critiques += 1

    return {
        "total_risks": total_risks,
        "risques_critiques": risques_critiques,
        "controls_en_place_pct": round((controls_en_place / total_controls * 100) if total_controls else 0),
        "total_findings": total_findings,
        "total_treatments": total_treatments,
        "findings_stats": findings_stats,
    }


@app.get("/kpi/heatmap")
def get_kpi_heatmap(db: Session = Depends(get_db)):
    scenarios = (
        db.query(ScenarioOperationnel)
        .options(
            selectinload(ScenarioOperationnel.controls_list),
            selectinload(ScenarioOperationnel.findings),
            selectinload(ScenarioOperationnel.treatments),
        )
        .all()
    )
    data = []
    for sc in scenarios:
        view = compute_risk_view(sc, sc.findings)
        treatment_status = sc.treatments[0].status if sc.treatments else None
        data.append(
            {
                "id": sc.id,
                "nom": sc.nom,
                "gravite": sc.gravite,
                "vraisemblance_inherente": sc.vraisemblance,
                "vraisemblance_ajustee": view["likelihood_adjusted"],
                "maturity_avg": view["maturity_avg"],
                "score_inherent": view["inherent"]["score"],
                "niveau_inherent": view["inherent"]["niveau"],
                "score_residuel": view["current_residual"]["score"],
                "niveau_residuel": view["current_residual"]["niveau"],
                "target_residual": view["target_residual"],
                "treatment_status": treatment_status,
            }
        )
    return data


@app.get("/kpi/soa")
def get_kpi_soa(db: Session = Depends(get_db)):
    all_controls = db.query(Control).all()
    stats = {}
    for c in all_controls:
        if c.theme not in stats:
            stats[c.theme] = {"total": 0, "en_place": 0}
        stats[c.theme]["total"] += 1
        if c.status == "implemented":
            stats[c.theme]["en_place"] += 1

    return [{"theme": k, "total": v["total"], "en_place": v["en_place"]} for k, v in stats.items()]


@app.get("/kpi/treatments")
def get_kpi_treatments(db: Session = Depends(get_db)):
    from app.models import Treatment

    treatments = db.query(Treatment).all()
    return [
        {"id": t.id, "nom": t.nom, "responsable": t.responsable, "echeance": t.echeance, "jira": t.jira_key}
        for t in treatments
    ]


@app.get("/kpi/compliance")
def get_kpi_compliance(db: Session = Depends(get_db)):
    from sqlalchemy import case, func

    from app.models import Control, ControlMapping

    results = (
        db.query(
            ControlMapping.framework,
            func.count(ControlMapping.id).label("total"),
            func.sum(case((Control.status == "implemented", 1), else_=0)).label("implemented"),
        )
        .join(Control, ControlMapping.control_id == Control.id)
        .group_by(ControlMapping.framework)
        .all()
    )

    return [
        {
            "framework": r[0],
            "total_mapped_controls": r[1],
            "implemented_controls": int(r[2] or 0),
            "compliance_rate": round((int(r[2] or 0) / r[1] * 100)) if r[1] > 0 else 0,
        }
        for r in results
    ]


@app.get("/kpi/compliance_matrix")
def get_kpi_compliance_matrix(db: Session = Depends(get_db)):
    from app.models import Control, ControlMapping

    mappings = (
        db.query(ControlMapping.control_id, ControlMapping.framework, ControlMapping.reference, Control.status)
        .join(Control, ControlMapping.control_id == Control.id)
        .all()
    )

    return [{"control_id": m[0], "framework": m[1], "reference": m[2], "status": m[3]} for m in mappings]


@app.get("/kpi/coverage")
def get_kpi_coverage(db: Session = Depends(get_db)):
    from app.models import Control, ControlMapping, ScenarioOperationnel

    controls = {c.id: c for c in db.query(Control).all()}

    # 1. Couverture NIS2 (10 mesures Article 21(2) a à j)
    nis2_mappings = db.query(ControlMapping).filter(ControlMapping.framework == "NIS2").all()

    nis2_letters = "abcdefghij"
    nis2_covered_count = 0
    nis2_status_counts = {"implemented": 0, "partial": 0, "planned": 0, "not_implemented": 0}
    nis2_measures_details = []

    for letter in nis2_letters:
        mesure_key = f"Article 21(2){letter}"
        matching_mappings = [
            m
            for m in nis2_mappings
            if re.search(rf"Article\s*21\(2\){letter}", m.reference or "", re.IGNORECASE)
        ]
        ctrl_ids = list(dict.fromkeys(m.control_id for m in matching_mappings if m.control_id))
        ctrl_objs = [controls[cid] for cid in ctrl_ids if cid in controls]
        applicable_ctrls = [c for c in ctrl_objs if c.is_applicable]

        is_covered = len(applicable_ctrls) > 0
        if is_covered:
            nis2_covered_count += 1

        measure_status_counts: dict[str, int] = {}
        for c in ctrl_objs:
            st = c.status or "implemented"
            measure_status_counts[st] = measure_status_counts.get(st, 0) + 1

        nis2_measures_details.append(
            {
                "measure": mesure_key,
                "letter": letter,
                "covered": is_covered,
                "controls_count": len(ctrl_objs),
                "controls": [c.id for c in ctrl_objs],
                "status_breakdown": measure_status_counts,
            }
        )

    all_nis2_ctrl_ids = list(dict.fromkeys(m.control_id for m in nis2_mappings if m.control_id))
    for cid in all_nis2_ctrl_ids:
        if cid in controls:
            st = controls[cid].status or "implemented"
            nis2_status_counts[st] = nis2_status_counts.get(st, 0) + 1

    # 2. Couverture MITRE ATT&CK (techniques citées dans w4_operationnels)
    import json

    scenarios = db.query(ScenarioOperationnel).all()
    cited_techniques = set()
    for sc in scenarios:
        if sc.techniques_attack:
            try:
                t_list = json.loads(sc.techniques_attack)
                if isinstance(t_list, list):
                    for t in t_list:
                        t_str = str(t).strip()
                        if t_str:
                            cited_techniques.add(t_str)
            except Exception:
                pass

    attack_mappings = db.query(ControlMapping).filter(ControlMapping.framework == "ATT&CK").all()

    attack_covered_count = 0
    attack_status_counts = {"implemented": 0, "partial": 0, "planned": 0, "not_implemented": 0}
    attack_techniques_details = []
    unimplemented_only_techniques = []
    alerts = []

    sorted_techniques = sorted(cited_techniques)
    for tech in sorted_techniques:
        matching_mappings = [
            m
            for m in attack_mappings
            if m.reference and (m.reference.startswith(tech) or re.match(rf"^{tech}(?:\.|\s|$)", m.reference))
        ]
        ctrl_ids = list(dict.fromkeys(m.control_id for m in matching_mappings if m.control_id))
        ctrl_objs = [controls[cid] for cid in ctrl_ids if cid in controls]
        applicable_ctrls = [c for c in ctrl_objs if c.is_applicable]

        is_covered = len(applicable_ctrls) > 0
        if is_covered:
            attack_covered_count += 1

        tech_status_counts: dict[str, int] = {}
        for c in ctrl_objs:
            st = c.status or "implemented"
            tech_status_counts[st] = tech_status_counts.get(st, 0) + 1

        # Alerte si la technique n'est couverte que par des contrôles non implémentés
        is_only_unimplemented = (
            len(ctrl_objs) > 0 and all(c.status in ("not_implemented", "planned") for c in ctrl_objs)
        )
        if is_only_unimplemented:
            unimplemented_only_techniques.append(tech)
            alerts.append(
                f"La technique ATT&CK '{tech}' n'est couverte que par des contrôles non implémentés "
                f"({', '.join(c.id for c in ctrl_objs)})."
            )

        attack_techniques_details.append(
            {
                "technique": tech,
                "covered": is_covered,
                "controls_count": len(ctrl_objs),
                "controls": [c.id for c in ctrl_objs],
                "status_breakdown": tech_status_counts,
                "only_unimplemented": is_only_unimplemented,
            }
        )

    all_att_ctrl_ids = list(dict.fromkeys(m.control_id for m in attack_mappings if m.control_id))
    for cid in all_att_ctrl_ids:
        if cid in controls:
            st = controls[cid].status or "implemented"
            attack_status_counts[st] = attack_status_counts.get(st, 0) + 1

    total_nis2 = 10
    total_attack = len(cited_techniques)

    return {
        "nis2": {
            "total_measures": total_nis2,
            "covered_measures": nis2_covered_count,
            "coverage_rate_pct": round(nis2_covered_count / total_nis2 * 100) if total_nis2 else 0,
            "breakdown_by_status": nis2_status_counts,
            "measures": nis2_measures_details,
        },
        "attack": {
            "total_techniques": total_attack,
            "covered_techniques": attack_covered_count,
            "coverage_rate_pct": round(attack_covered_count / total_attack * 100) if total_attack else 0,
            "breakdown_by_status": attack_status_counts,
            "techniques_only_non_implemented": unimplemented_only_techniques,
            "alerts": alerts,
            "techniques": attack_techniques_details,
        },
    }


@app.get("/findings")
def get_findings(db: Session = Depends(get_db)):
    from app.models import Finding

    findings = db.query(Finding).all()
    return [
        {
            "id": f.id,
            "source": f.source,
            "cve": f.cve,
            "severite": f.severite,
            "description": f.description,
            "actif": f.actif_id,
            "technique": f.technique_attack,
        }
        for f in findings
    ]
