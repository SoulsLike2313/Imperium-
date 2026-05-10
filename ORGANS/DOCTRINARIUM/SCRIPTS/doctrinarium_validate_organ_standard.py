#!/usr/bin/env python3
import argparse
import datetime as dt
import json
from pathlib import Path

ALLOWED_STATUSES = [
    "NOT_FOUND",
    "FOLDER_ONLY",
    "PLACEHOLDER",
    "SCAFFOLD",
    "BOOTSTRAP",
    "CANON_CANDIDATE",
    "CANON_V0_1",
    "DEGRADED",
    "BLOCKED",
    "DEPRECATED",
    "UNKNOWN",
]


def now_iso() -> str:
    return dt.datetime.now(dt.timezone.utc).isoformat()


def read_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8-sig"))


def classify_quick(folder_exists: bool, readme: bool, status: bool, contract: bool, scripts: bool, receipts: bool) -> str:
    if not folder_exists:
        return "NOT_FOUND"
    if not any([readme, status, contract, scripts, receipts]):
        return "FOLDER_ONLY"
    if readme and not status and not contract:
        return "PLACEHOLDER"
    if status and contract:
        return "SCAFFOLD"
    return "UNKNOWN"


def validate_organ(organ_path: Path, organ_id: str):
    checks = []
    blockers = []
    warnings = []

    folder_exists = organ_path.exists() and organ_path.is_dir()
    readme_path = organ_path / "README.md"
    status_path = organ_path / "ORGAN_STATUS.json"
    contract_path = organ_path / "ORGAN_CONTRACT.json"
    scripts_dir = organ_path / "SCRIPTS"
    receipts_dir = organ_path / "RECEIPTS"

    readme_exists = readme_path.exists()
    status_exists = status_path.exists()
    contract_exists = contract_path.exists()
    scripts_exists = scripts_dir.exists() and scripts_dir.is_dir()
    receipts_exists = receipts_dir.exists() and receipts_dir.is_dir()

    status_data = {}
    contract_data = {}
    if status_exists:
        try:
            status_data = read_json(status_path)
        except Exception as ex:
            blockers.append(f"Invalid ORGAN_STATUS.json: {ex}")
    if contract_exists:
        try:
            contract_data = read_json(contract_path)
        except Exception as ex:
            blockers.append(f"Invalid ORGAN_CONTRACT.json: {ex}")

    def ck(ok: bool, name: str, fail: str):
        checks.append({"check": name, "ok": ok, "detail": "ok" if ok else fail})
        if not ok:
            blockers.append(fail)

    ck(folder_exists, "organ folder exists", f"Organ folder missing: {organ_path}")
    ck(readme_exists, "README exists", f"Missing README.md: {readme_path}")
    ck(status_exists, "ORGAN_STATUS exists", f"Missing ORGAN_STATUS.json: {status_path}")
    ck(contract_exists, "ORGAN_CONTRACT exists", f"Missing ORGAN_CONTRACT.json: {contract_path}")

    non_script_role = bool(contract_data.get("non_script_role", False)) if isinstance(contract_data, dict) else False
    ck(
        scripts_exists or non_script_role,
        "SCRIPTS exists or non-script role explicit",
        "Missing SCRIPTS directory and non_script_role is not explicit",
    )
    ck(receipts_exists, "RECEIPTS exists", f"Missing RECEIPTS directory: {receipts_dir}")

    allowed_write = contract_data.get("allowed_write_roots") if isinstance(contract_data, dict) else None
    forbidden_roots = contract_data.get("forbidden_roots") if isinstance(contract_data, dict) else None
    entrypoints = contract_data.get("entrypoints") if isinstance(contract_data, dict) else None
    required_receipts = contract_data.get("required_receipts") if isinstance(contract_data, dict) else None
    responsibilities = contract_data.get("responsibilities") if isinstance(contract_data, dict) else None
    not_responsible = contract_data.get("explicitly_not_responsible_for") if isinstance(contract_data, dict) else None

    ck(
        isinstance(allowed_write, list) and len(allowed_write) > 0,
        "allowed_write_roots defined",
        "allowed_write_roots missing or empty in ORGAN_CONTRACT",
    )
    ck(
        isinstance(forbidden_roots, list) and len(forbidden_roots) > 0,
        "forbidden_roots defined",
        "forbidden_roots missing or empty in ORGAN_CONTRACT",
    )
    ck(
        isinstance(entrypoints, list) and len(entrypoints) > 0,
        "entrypoints defined",
        "entrypoints missing or empty in ORGAN_CONTRACT",
    )
    ck(isinstance(required_receipts, list), "required_receipts defined", "required_receipts missing in ORGAN_CONTRACT")
    ck(
        isinstance(responsibilities, list) and len(responsibilities) > 0,
        "responsibilities defined",
        "responsibilities missing or empty in ORGAN_CONTRACT",
    )
    ck(
        isinstance(not_responsible, list) and len(not_responsible) > 0,
        "excluded responsibilities defined",
        "explicitly_not_responsible_for missing or empty in ORGAN_CONTRACT",
    )

    self_report_candidates = [
        organ_path / "REPORTS" / "ORGAN_SELF_REPORT.json",
        organ_path / "REPORTS" / "ORGAN_SELF_REPORT.md",
        organ_path / "STATUS" / "ORGAN_STATUS_REPORT.json",
        organ_path / "STATUS" / "ORGAN_STATUS_REPORT.md",
    ]
    has_self_report = any(p.exists() for p in self_report_candidates)
    ck(has_self_report, "self-report or equivalent exists", "No self-report/status report file found")

    current_blockers = None
    if isinstance(status_data, dict):
        current_blockers = status_data.get("current_blockers")
    if current_blockers is None and isinstance(contract_data, dict):
        current_blockers = contract_data.get("current_blockers")
    ck(current_blockers is not None, "current blockers visible", "current_blockers field not found in status/contract")

    claimed_status = str(status_data.get("status", "")) if isinstance(status_data, dict) else ""
    claimed_doctrine_status = str(status_data.get("doctrine_status", "")) if isinstance(status_data, dict) else ""
    owner_approval_evidence = contract_data.get("owner_approval_evidence_path") if isinstance(contract_data, dict) else None
    owner_approval_ok = bool(owner_approval_evidence and Path(str(owner_approval_evidence)).exists())

    canon_claim_without_evidence = (
        claimed_status == "CANON_V0_1" or claimed_doctrine_status == "CANON_V0_1"
    ) and not owner_approval_ok
    ck(
        not canon_claim_without_evidence,
        "no CANON_V0_1 claim without owner evidence",
        "Organ claims CANON_V0_1 without owner approval evidence",
    )

    classification = classify_quick(
        folder_exists, readme_exists, status_exists, contract_exists, scripts_exists, receipts_exists
    )
    if classification == "SCAFFOLD" and blockers:
        classification = "BLOCKED"

    result = {
        "organ_id": organ_id,
        "path": str(organ_path),
        "classification": classification,
        "folder_exists": folder_exists,
        "readme_exists": readme_exists,
        "organ_status_exists": status_exists,
        "organ_contract_exists": contract_exists,
        "scripts_exists": scripts_exists,
        "receipts_exists": receipts_exists,
        "self_report_exists": has_self_report,
        "checks": checks,
        "blockers": blockers,
        "warnings": warnings,
        "owner_approval_state": {
            "evidence_path": owner_approval_evidence,
            "evidence_exists": owner_approval_ok,
        },
        "created_at": now_iso(),
    }
    return result


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--organ-path", required=True)
    parser.add_argument("--organ-id", required=True)
    parser.add_argument("--required-level", default="SCAFFOLD")
    parser.add_argument("--output-json")
    parser.add_argument("--output-md")
    args = parser.parse_args()

    result = validate_organ(Path(args.organ_path), args.organ_id)

    if args.output_json:
        p = Path(args.output_json)
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    if args.output_md:
        p = Path(args.output_md)
        p.parent.mkdir(parents=True, exist_ok=True)
        md = [
            f"# ORGAN STANDARD VALIDATION - {args.organ_id}",
            "",
            f"- Path: {result['path']}",
            f"- Classification: {result['classification']}",
            "",
            "## Checks",
        ]
        for c in result["checks"]:
            md.append(f"- {c['check']}: {c['ok']} ({c['detail']})")
        if result["blockers"]:
            md += ["", "## Blockers"]
            for b in result["blockers"]:
                md.append(f"- {b}")
        p.write_text("\n".join(md) + "\n", encoding="utf-8")

    print(json.dumps(result, ensure_ascii=False))
    return 0 if not result["blockers"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
