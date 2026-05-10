#!/usr/bin/env python3
import argparse
import datetime as dt
import json
from pathlib import Path


def now_iso() -> str:
    return dt.datetime.now(dt.timezone.utc).isoformat()


def read_json(path: Path, default=None):
    if not path.exists():
        return default if default is not None else {}
    try:
        return json.loads(path.read_text(encoding="utf-8-sig"))
    except Exception:
        return default if default is not None else {}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", default=r"E:\IMPERIUM")
    parser.add_argument("--task-artifact-root", required=True)
    parser.add_argument("--output-json", required=True)
    parser.add_argument("--output-md", required=True)
    parser.add_argument("--copy-json", required=True)
    parser.add_argument("--copy-md", required=True)
    args = parser.parse_args()

    root = Path(args.root)
    task_root = Path(args.task_artifact_root)

    doctrine_index_path = root / "ORGANS" / "DOCTRINARIUM" / "DOCTRINE" / "DOCTRINE_INDEX.json"
    mandatory_laws_path = root / "ORGANS" / "DOCTRINARIUM" / "LAWS" / "MANDATORY_LAWS.json"
    law_index_path = root / "ORGANS" / "DOCTRINARIUM" / "LAWS" / "LAW_INDEX.json"
    law_enforcement_path = root / "ORGANS" / "DOCTRINARIUM" / "LAWS" / "LAW_ENFORCEMENT_MAP.json"
    organ_status_path = root / "ORGANS" / "DOCTRINARIUM" / "ORGAN_STATUS.json"
    gap_report_path = task_root / "06_ALL_ORGANS_GAP_REPORT" / "ALL_ORGANS_GAP_REPORT.json"
    receipts_dir = task_root / "08_RECEIPTS"

    doctrine_index = read_json(doctrine_index_path, {})
    mandatory_laws = read_json(mandatory_laws_path, {})
    _law_index = read_json(law_index_path, {})
    _law_enf = read_json(law_enforcement_path, {})
    organ_status = read_json(organ_status_path, {})
    gap_report = read_json(gap_report_path, {})

    primary_docs = doctrine_index.get("primary_documents", []) if isinstance(doctrine_index, dict) else []
    docs_status = []
    for d in primary_docs:
        docs_status.append(
            {
                "document_id": d.get("document_id"),
                "status": d.get("status"),
                "owner_approved": d.get("owner_approved", False),
                "canon_for_real_task_execution": d.get("canon_for_real_task_execution", False),
            }
        )

    laws = mandatory_laws.get("laws", []) if isinstance(mandatory_laws, dict) else []
    not_fully = [x.get("law_id") for x in laws if x.get("enforcement_status") != "LAW_ENFORCED"]
    hard_not_fully = [
        x.get("law_id")
        for x in laws
        if x.get("severity") == "HARD_BLOCK" and x.get("enforcement_status") != "LAW_ENFORCED"
    ]

    gap_summary = {
        "total_organs_checked": gap_report.get("total_organs_checked", 0),
        "classification_summary": gap_report.get("classification_summary", {}),
        "total_blockers_found": gap_report.get("total_blockers_found", 0),
    }

    latest_receipts = []
    if receipts_dir.exists():
        for rp in sorted(receipts_dir.glob("*.json")):
            rj = read_json(rp, {})
            latest_receipts.append({"name": rp.name, "verdict": rj.get("verdict", "UNKNOWN")})

    real_task_allowed = bool(doctrine_index.get("canon_for_real_task_execution", False))
    bootstrap_review_allowed = True
    if hard_not_fully:
        real_task_allowed = False

    blockers = []
    if not doctrine_index_path.exists():
        blockers.append("Missing DOCTRINE_INDEX.json")
    if not mandatory_laws_path.exists():
        blockers.append("Missing MANDATORY_LAWS.json")
    if not law_index_path.exists():
        blockers.append("Missing LAW_INDEX.json")
    if not law_enforcement_path.exists():
        blockers.append("Missing LAW_ENFORCEMENT_MAP.json")

    verdict = "PASS_DOCTRINARIUM_STATUS_REPORT_CREATED_REAL_TASKS_BLOCKED"
    if blockers:
        verdict = "REPAIR_REQUIRED"

    status_json = {
        "schema_version": "DOCTRINARIUM_STATUS_V0_1",
        "verdict": verdict,
        "passport_status": next((x["status"] for x in docs_status if x["document_id"] == "PASSPORT_OF_EMPEROR"), "UNKNOWN"),
        "constitution_status": next(
            (x["status"] for x in docs_status if x["document_id"] == "CONSTITUTION_OF_IMPERIUM"), "UNKNOWN"
        ),
        "codex_status": next((x["status"] for x in docs_status if x["document_id"] == "CODEX_IMPERIUM"), "UNKNOWN"),
        "doctrine_index_status": doctrine_index.get("status", "UNKNOWN"),
        "real_task_execution_allowed": real_task_allowed,
        "bootstrap_review_allowed": bootstrap_review_allowed,
        "law_registry_status": {
            "total_laws": len(laws),
            "not_fully_enforced_count": len(not_fully),
            "hard_not_fully_enforced_count": len(hard_not_fully),
        },
        "laws_not_fully_enforced": not_fully,
        "hard_law_blockers_for_real_task": hard_not_fully,
        "organ_gap_summary": gap_summary,
        "blockers": blockers,
        "next_recommended_steps": [
            "Owner review and approval workflow for doctrine candidates.",
            "Increase LAW_ENFORCED coverage for HARD_BLOCK laws.",
            "Close top organ contract/status gaps from all-organs gap report.",
        ],
        "latest_receipts": latest_receipts,
        "doctrinarium_organ_status": organ_status,
        "created_at": now_iso(),
    }

    out_json = Path(args.output_json)
    out_md = Path(args.output_md)
    copy_json = Path(args.copy_json)
    copy_md = Path(args.copy_md)

    for p in [out_json, out_md, copy_json, copy_md]:
        p.parent.mkdir(parents=True, exist_ok=True)

    out_json.write_text(json.dumps(status_json, ensure_ascii=False, indent=2), encoding="utf-8")

    md = [
        "# DOCTRINARIUM STATUS REPORT",
        "",
        f"- Verdict: {verdict}",
        f"- Passport status: {status_json['passport_status']}",
        f"- Constitution status: {status_json['constitution_status']}",
        f"- Codex status: {status_json['codex_status']}",
        f"- Doctrine index status: {status_json['doctrine_index_status']}",
        f"- Real task execution allowed: {status_json['real_task_execution_allowed']}",
        f"- Bootstrap/review allowed: {status_json['bootstrap_review_allowed']}",
        "",
        "## Law Registry",
    ]
    md.append(f"- Total laws: {status_json['law_registry_status']['total_laws']}")
    md.append(f"- Not fully enforced: {status_json['law_registry_status']['not_fully_enforced_count']}")
    md.append(f"- HARD_BLOCK not fully enforced: {status_json['law_registry_status']['hard_not_fully_enforced_count']}")
    md += ["", "## Organ Gap Summary"]
    md.append(f"- Total organs checked: {gap_summary['total_organs_checked']}")
    md.append(f"- Total blockers found: {gap_summary['total_blockers_found']}")
    md += ["", "## Blockers"]
    if blockers:
        for b in blockers:
            md.append(f"- {b}")
    else:
        md.append("- none")
    md += ["", "## Next Recommended Steps"]
    for s in status_json["next_recommended_steps"]:
        md.append(f"- {s}")

    out_md.write_text("\n".join(md) + "\n", encoding="utf-8")
    copy_json.write_text(out_json.read_text(encoding="utf-8"), encoding="utf-8")
    copy_md.write_text(out_md.read_text(encoding="utf-8"), encoding="utf-8")

    local_status = root / "ORGANS" / "DOCTRINARIUM" / "STATUS" / "DOCTRINARIUM_STATUS.json"
    local_status.parent.mkdir(parents=True, exist_ok=True)
    local_status.write_text(json.dumps(status_json, ensure_ascii=False, indent=2), encoding="utf-8")

    return 0 if not blockers else 2


if __name__ == "__main__":
    raise SystemExit(main())
