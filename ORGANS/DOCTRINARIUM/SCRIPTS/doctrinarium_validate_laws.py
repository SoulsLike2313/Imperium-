#!/usr/bin/env python3
import argparse
import datetime as dt
import json
from pathlib import Path

MANDATORY_IDS = [
    "LAW-001",
    "LAW-002",
    "LAW-003",
    "LAW-004",
    "LAW-005",
    "LAW-006",
    "LAW-007",
    "LAW-008",
    "LAW-009",
    "LAW-010",
    "LAW-011",
    "LAW-012",
    "LAW-013",
    "LAW-014",
    "LAW-015",
    "LAW-016",
    "LAW-017",
    "LAW-018",
    "LAW-019",
    "LAW-020",
    "LAW-021",
    "LAW-022",
    "LAW-023",
    "LAW-024",
    "LAW-025",
]


def now_iso() -> str:
    return dt.datetime.now(dt.timezone.utc).isoformat()


def read_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8-sig"))


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", default=r"E:\IMPERIUM")
    parser.add_argument("--output-json", required=True)
    parser.add_argument("--output-md", required=True)
    args = parser.parse_args()

    root = Path(args.root)
    laws_dir = root / "ORGANS" / "DOCTRINARIUM" / "LAWS"
    files = {
        "mandatory": laws_dir / "MANDATORY_LAWS.json",
        "index": laws_dir / "LAW_INDEX.json",
        "address": laws_dir / "LAW_ADDRESS_REGISTRY.json",
        "enforcement": laws_dir / "LAW_ENFORCEMENT_MAP.json",
    }

    blockers = []
    warnings = []
    limitations = []
    checks = []

    for key, path in files.items():
        ok = path.exists()
        checks.append({"check": f"{key} file exists", "ok": ok, "detail": str(path)})
        if not ok:
            blockers.append(f"Missing file: {path}")

    if blockers:
        verdict = "REPAIR_REQUIRED"
        report = {
            "schema_version": "LAW_REGISTRY_REPORT_V0_1",
            "verdict": verdict,
            "blockers": blockers,
            "warnings": warnings,
            "limitations": limitations,
            "checks": checks,
            "created_at": now_iso(),
        }
        Path(args.output_json).write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
        Path(args.output_md).write_text("# LAW REGISTRY REPORT\n\n- Verdict: REPAIR_REQUIRED\n", encoding="utf-8")
        return 2

    mandatory = read_json(files["mandatory"])
    index = read_json(files["index"])
    address = read_json(files["address"])
    enforcement = read_json(files["enforcement"])

    laws = mandatory.get("laws", [])
    ids = [str(x.get("law_id", "")) for x in laws]

    checks.append(
        {
            "check": "All 25 mandatory laws present",
            "ok": set(MANDATORY_IDS).issubset(set(ids)),
            "detail": f"present={len(set(ids))} required={len(MANDATORY_IDS)}",
        }
    )
    if not set(MANDATORY_IDS).issubset(set(ids)):
        blockers.append("Not all mandatory law IDs present in MANDATORY_LAWS.json")

    checks.append(
        {
            "check": "Law IDs unique",
            "ok": len(ids) == len(set(ids)),
            "detail": f"total={len(ids)} unique={len(set(ids))}",
        }
    )
    if len(ids) != len(set(ids)):
        blockers.append("Duplicate law IDs found")

    missing_verdict = []
    missing_severity = []
    missing_source = []
    missing_enforcement_status = []
    not_fully_enforced = []
    hard_no_enforcement = []

    for law in laws:
        lid = law.get("law_id")
        if not law.get("violation_verdict"):
            missing_verdict.append(lid)
        if not law.get("severity"):
            missing_severity.append(lid)
        if not law.get("source_document") or not law.get("source_document_path"):
            missing_source.append(lid)
        if not law.get("enforcement_status"):
            missing_enforcement_status.append(lid)
        if law.get("enforcement_status") != "LAW_ENFORCED":
            not_fully_enforced.append(lid)
        if law.get("severity") == "HARD_BLOCK" and law.get("enforcement_status") != "LAW_ENFORCED":
            hard_no_enforcement.append(lid)

    checks.append(
        {
            "check": "Each law has violation verdict",
            "ok": len(missing_verdict) == 0,
            "detail": str(missing_verdict),
        }
    )
    checks.append(
        {"check": "Each law has severity", "ok": len(missing_severity) == 0, "detail": str(missing_severity)}
    )
    checks.append(
        {
            "check": "Each law has source reference",
            "ok": len(missing_source) == 0,
            "detail": str(missing_source),
        }
    )
    checks.append(
        {
            "check": "Each law has enforcement status",
            "ok": len(missing_enforcement_status) == 0,
            "detail": str(missing_enforcement_status),
        }
    )

    if missing_verdict:
        blockers.append(f"Missing violation_verdict for laws: {missing_verdict}")
    if missing_severity:
        blockers.append(f"Missing severity for laws: {missing_severity}")
    if missing_source:
        blockers.append(f"Missing source reference for laws: {missing_source}")
    if missing_enforcement_status:
        blockers.append(f"Missing enforcement_status for laws: {missing_enforcement_status}")

    if not_fully_enforced:
        warnings.append(f"Laws not fully enforced: {not_fully_enforced}")
        limitations.append("Law registry is scaffold-level; several laws remain not fully enforced.")
    if hard_no_enforcement:
        warnings.append(f"HARD_BLOCK laws not fully enforced (real-task blockers): {hard_no_enforcement}")
        limitations.append("Real task execution is blocked until HARD_BLOCK laws are enforced or owner-approved.")

    index_ids = set(str(x.get("law_id")) for x in index.get("law_index", []))
    addr_ids = (
        set(address.get("law_address_registry", {}).keys())
        if isinstance(address.get("law_address_registry", {}), dict)
        else set()
    )
    enf_ids = (
        set(enforcement.get("law_enforcement_map", {}).keys())
        if isinstance(enforcement.get("law_enforcement_map", {}), dict)
        else set()
    )
    req_ids = set(MANDATORY_IDS)

    checks.append(
        {
            "check": "LAW_INDEX covers all mandatory laws",
            "ok": req_ids.issubset(index_ids),
            "detail": f"missing={sorted(list(req_ids - index_ids))}",
        }
    )
    checks.append(
        {
            "check": "LAW_ADDRESS_REGISTRY covers all mandatory laws",
            "ok": req_ids.issubset(addr_ids),
            "detail": f"missing={sorted(list(req_ids - addr_ids))}",
        }
    )
    checks.append(
        {
            "check": "LAW_ENFORCEMENT_MAP covers all mandatory laws",
            "ok": req_ids.issubset(enf_ids),
            "detail": f"missing={sorted(list(req_ids - enf_ids))}",
        }
    )

    if not req_ids.issubset(index_ids):
        blockers.append("LAW_INDEX missing mandatory IDs")
    if not req_ids.issubset(addr_ids):
        blockers.append("LAW_ADDRESS_REGISTRY missing mandatory IDs")
    if not req_ids.issubset(enf_ids):
        blockers.append("LAW_ENFORCEMENT_MAP missing mandatory IDs")

    verdict = "PASS_LAW_REGISTRY_CREATED_WITH_ENFORCEMENT_GAPS" if not blockers else "REPAIR_REQUIRED"

    report = {
        "schema_version": "LAW_REGISTRY_REPORT_V0_1",
        "verdict": verdict,
        "blockers": blockers,
        "warnings": warnings,
        "limitations": limitations,
        "not_fully_enforced_laws": not_fully_enforced,
        "hard_block_laws_without_full_enforcement": hard_no_enforcement,
        "checks": checks,
        "created_at": now_iso(),
    }

    Path(args.output_json).write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")

    md = ["# LAW REGISTRY REPORT", "", f"- Verdict: {verdict}", ""]
    md.append("## Checks")
    for c in checks:
        md.append(f"- {c['check']}: {c['ok']} ({c['detail']})")
    if warnings:
        md.append("")
        md.append("## Warnings")
        for w in warnings:
            md.append(f"- {w}")
    if blockers:
        md.append("")
        md.append("## Blockers")
        for b in blockers:
            md.append(f"- {b}")
    if limitations:
        md.append("")
        md.append("## Limitations")
        for l in limitations:
            md.append(f"- {l}")
    Path(args.output_md).write_text("\n".join(md) + "\n", encoding="utf-8")

    return 0 if not blockers else 2


if __name__ == "__main__":
    raise SystemExit(main())
