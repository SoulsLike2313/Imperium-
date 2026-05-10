#!/usr/bin/env python3
import argparse
import datetime as dt
import json
from pathlib import Path


def now_iso() -> str:
    return dt.datetime.now(dt.timezone.utc).isoformat()


def import_standard_validator(script_dir: Path):
    import sys

    if str(script_dir) not in sys.path:
        sys.path.insert(0, str(script_dir))
    import doctrinarium_validate_organ_standard as ovs

    return ovs


def is_skip_dir(name: str) -> bool:
    return name.lower() in {"archive", "_archive", "00_archive", "old", "deprecated"}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", default=r"E:\IMPERIUM")
    parser.add_argument("--output-json", required=True)
    parser.add_argument("--output-md", required=True)
    parser.add_argument("--copy-json", required=False)
    parser.add_argument("--copy-md", required=False)
    args = parser.parse_args()

    root = Path(args.root)
    organs_dir = root / "ORGANS"
    script_dir = root / "ORGANS" / "DOCTRINARIUM" / "SCRIPTS"
    ovs = import_standard_validator(script_dir)

    records = []
    skipped = []

    if not organs_dir.exists():
        report = {
            "schema_version": "ALL_ORGANS_GAP_REPORT_V0_1",
            "verdict": "REPAIR_REQUIRED",
            "blockers": [f"Missing ORGANS directory: {organs_dir}"],
            "created_at": now_iso(),
            "organs": [],
        }
        Path(args.output_json).write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
        Path(args.output_md).write_text("# ALL ORGANS GAP REPORT\n\n- Verdict: REPAIR_REQUIRED\n", encoding="utf-8")
        return 2

    for child in sorted(organs_dir.iterdir(), key=lambda p: p.name.lower()):
        if not child.is_dir():
            continue
        if is_skip_dir(child.name):
            skipped.append({"path": str(child), "reason": "archive-like-skip-name"})
            continue
        if child.name.upper() == "SANCTUM":
            skipped.append({"path": str(child), "reason": "sanctum-no-touch"})
            continue

        result = ovs.validate_organ(child, child.name.upper())

        contract = child / "ORGAN_CONTRACT.json"
        status = child / "ORGAN_STATUS.json"
        contract_data = {}
        status_data = {}
        if contract.exists():
            try:
                contract_data = json.loads(contract.read_text(encoding="utf-8-sig"))
            except Exception:
                pass
        if status.exists():
            try:
                status_data = json.loads(status.read_text(encoding="utf-8-sig"))
            except Exception:
                pass

        result["allowed_writes_present"] = isinstance(contract_data.get("allowed_write_roots"), list) and len(
            contract_data.get("allowed_write_roots")
        ) > 0
        result["forbidden_roots_present"] = isinstance(contract_data.get("forbidden_roots"), list) and len(
            contract_data.get("forbidden_roots")
        ) > 0
        result["entrypoints_present"] = isinstance(contract_data.get("entrypoints"), list) and len(
            contract_data.get("entrypoints")
        ) > 0
        result["required_receipts_present"] = isinstance(contract_data.get("required_receipts"), list)
        result["current_blockers"] = status_data.get("current_blockers", contract_data.get("current_blockers", []))
        result["owner_approval_state_value"] = status_data.get(
            "owner_approval_state", contract_data.get("owner_approval_state", "UNKNOWN")
        )
        result["why_not_canon"] = []
        if result["classification"] != "CANON_V0_1":
            if not result["organ_contract_exists"]:
                result["why_not_canon"].append("Missing ORGAN_CONTRACT.json")
            if not result["organ_status_exists"]:
                result["why_not_canon"].append("Missing ORGAN_STATUS.json")
            if result["blockers"]:
                result["why_not_canon"].append("Has standard validation blockers")
            if result["owner_approval_state"]["evidence_exists"] is False:
                result["why_not_canon"].append("No owner approval evidence for canon claim")

        records.append(result)

    total = len(records)
    by_class = {}
    for r in records:
        by_class[r["classification"]] = by_class.get(r["classification"], 0) + 1

    total_blockers = sum(len(r.get("blockers", [])) for r in records)
    major_gaps = []
    for r in records:
        for b in r.get("blockers", []):
            major_gaps.append({"organ": r["organ_id"], "gap": b})

    verdict = "PASS_ALL_ORGANS_GAP_REPORT_CREATED_WITH_EXPECTED_ERRORS"
    report = {
        "schema_version": "ALL_ORGANS_GAP_REPORT_V0_1",
        "verdict": verdict,
        "root_scanned": str(organs_dir),
        "total_organs_checked": total,
        "classification_summary": by_class,
        "total_blockers_found": total_blockers,
        "major_gaps": major_gaps,
        "skipped": skipped,
        "organs": records,
        "created_at": now_iso(),
    }

    out_json = Path(args.output_json)
    out_md = Path(args.output_md)
    out_json.parent.mkdir(parents=True, exist_ok=True)
    out_md.parent.mkdir(parents=True, exist_ok=True)
    out_json.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")

    md = [
        "# ALL ORGANS GAP REPORT",
        "",
        f"- Verdict: {verdict}",
        f"- Root scanned: {organs_dir}",
        f"- Total organs checked: {total}",
        f"- Total blockers found: {total_blockers}",
        "",
        "## Classification Summary",
    ]
    for k in sorted(by_class.keys()):
        md.append(f"- {k}: {by_class[k]}")
    md += ["", "## Top Gaps (first 40)"]
    for g in major_gaps[:40]:
        md.append(f"- {g['organ']}: {g['gap']}")
    md += ["", "## Skipped"]
    for s in skipped:
        md.append(f"- {s['path']} | {s['reason']}")
    out_md.write_text("\n".join(md) + "\n", encoding="utf-8")

    if args.copy_json:
        p = Path(args.copy_json)
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(out_json.read_text(encoding="utf-8"), encoding="utf-8")
    if args.copy_md:
        p = Path(args.copy_md)
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(out_md.read_text(encoding="utf-8"), encoding="utf-8")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
