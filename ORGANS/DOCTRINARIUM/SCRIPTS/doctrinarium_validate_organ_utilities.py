import argparse
import json
from pathlib import Path
from datetime import datetime, timezone

CANON_BLOCKING_STATUSES = {"CANON_CANDIDATE", "CANON_V0_1"}

UTILITY_DIR_NAMES = [
    "UTILITY",
    "UTILITIES",
    "WORKBENCH",
    "CONSOLE",
    "UI",
    "PANEL"
]

UTILITY_FILE_NAMES = [
    "UTILITY_REQUIREMENTS.md",
    "UTILITY_REQUIREMENTS.json",
    "ORGAN_UTILITY.json",
    "WORKBENCH_REQUIREMENTS.md",
    "WORKBENCH_STATUS.json",
    "UTILITY_STATUS.json"
]

SCRIPT_BACKING_NAMES = [
    "SCRIPT_BACKING_MAP.json",
    "UTILITY_SCRIPT_MAP.json",
    "REGISTERED_SCRIPTS.json"
]


def utc_now():
    return datetime.now(timezone.utc).isoformat()


def read_json(path):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return None


def organ_status_from_files(organ_path):
    status_path = organ_path / "ORGAN_STATUS.json"
    contract_path = organ_path / "ORGAN_CONTRACT.json"

    for p in [status_path, contract_path]:
        data = read_json(p)
        if isinstance(data, dict):
            for key in ["status", "organ_status", "canon_status", "classification"]:
                val = data.get(key)
                if isinstance(val, str) and val.strip():
                    return val.strip()

    return "UNKNOWN"


def has_any_dir(organ_path, names):
    for name in names:
        if (organ_path / name).exists() and (organ_path / name).is_dir():
            return True, str(organ_path / name)
    return False, None


def has_any_file(organ_path, names):
    for name in names:
        p = organ_path / name
        if p.exists() and p.is_file():
            return True, str(p)
    return False, None


def has_script_backing(organ_path):
    # A real utility must be backed by scripts/reports/receipts/status.
    scripts_exists = (organ_path / "SCRIPTS").exists()
    reports_exists = (organ_path / "REPORTS").exists()
    receipts_exists = (organ_path / "RECEIPTS").exists()
    status_exists = (organ_path / "STATUS").exists() or (organ_path / "ORGAN_STATUS.json").exists()

    map_exists, map_path = has_any_file(organ_path, SCRIPT_BACKING_NAMES)

    evidence = {
        "scripts_exists": scripts_exists,
        "reports_exists": reports_exists,
        "receipts_exists": receipts_exists,
        "status_exists": status_exists,
        "script_backing_map_exists": map_exists,
        "script_backing_map_path": map_path
    }

    # For scaffold/bootstrap we only report readiness.
    # For canon candidate / canon v0.1 we require the full utility backing.
    backed = scripts_exists and receipts_exists and status_exists and (reports_exists or map_exists)

    return backed, evidence


def classify_utility(organ_path, organ_status):
    utility_dir_exists, utility_dir_path = has_any_dir(organ_path, UTILITY_DIR_NAMES)
    utility_file_exists, utility_file_path = has_any_file(organ_path, UTILITY_FILE_NAMES)
    utility_declared = utility_dir_exists or utility_file_exists

    script_backed, backing_evidence = has_script_backing(organ_path)

    checks = []
    blockers = []
    warnings = []

    checks.append({
        "check": "dedicated utility declared",
        "ok": utility_declared,
        "detail": utility_dir_path or utility_file_path or "No dedicated utility/workbench/console declaration found"
    })

    checks.append({
        "check": "utility backed by scripts/reports/receipts/status",
        "ok": script_backed,
        "detail": backing_evidence
    })

    if organ_status in CANON_BLOCKING_STATUSES:
        if not utility_declared:
            blockers.append("BLOCKED_ORGAN_UTILITY_MISSING: canon-candidate/canon organ requires dedicated utility")
        if utility_declared and not script_backed:
            blockers.append("BLOCKED_DECORATIVE_UTILITY: utility exists or is claimed but lacks script/report/receipt/status backing")
    else:
        if not utility_declared:
            warnings.append("ORGAN_REQUIRES_DEDICATED_UTILITY before CANON_CANDIDATE/CANON_V0_1 promotion")
        if utility_declared and not script_backed:
            warnings.append("ORGAN_UTILITY_REQUIRES_SCRIPTS before CANON_CANDIDATE/CANON_V0_1 promotion")

    return {
        "utility_declared": utility_declared,
        "utility_path": utility_dir_path or utility_file_path,
        "script_backed": script_backed,
        "backing_evidence": backing_evidence,
        "checks": checks,
        "blockers": blockers,
        "warnings": warnings
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", required=True, help="IMPERIUM root, e.g. E:\\IMPERIUM")
    ap.add_argument("--output-json", required=True)
    ap.add_argument("--output-md", required=True)
    ap.add_argument("--copy-json", default=None)
    ap.add_argument("--copy-md", default=None)
    args = ap.parse_args()

    root = Path(args.root)
    organs_root = root / "ORGANS"

    report = {
        "schema_version": "ORGAN_UTILITY_GAP_REPORT_V0_1",
        "verdict": "PASS_ORGAN_UTILITY_REPORT_CREATED",
        "root_scanned": str(organs_root),
        "utility_rules": [
            "ORGAN_REQUIRES_DEDICATED_UTILITY",
            "ORGAN_UTILITY_REQUIRES_SCRIPTS"
        ],
        "created_at": utc_now(),
        "organs": [],
        "summary": {
            "total_organs_checked": 0,
            "utility_declared_count": 0,
            "script_backed_count": 0,
            "blocking_utility_failures": 0,
            "warnings_count": 0
        }
    }

    if not organs_root.exists():
        report["verdict"] = "REPAIR_REQUIRED"
        report["blockers"] = [f"Missing ORGANS directory: {organs_root}"]
    else:
        for organ_path in sorted([p for p in organs_root.iterdir() if p.is_dir()], key=lambda p: p.name.upper()):
            organ_id = organ_path.name
            organ_status = organ_status_from_files(organ_path)
            utility = classify_utility(organ_path, organ_status)

            item = {
                "organ_id": organ_id,
                "path": str(organ_path),
                "organ_status": organ_status,
                **utility
            }

            report["organs"].append(item)

        report["summary"]["total_organs_checked"] = len(report["organs"])
        report["summary"]["utility_declared_count"] = sum(1 for o in report["organs"] if o["utility_declared"])
        report["summary"]["script_backed_count"] = sum(1 for o in report["organs"] if o["script_backed"])
        report["summary"]["blocking_utility_failures"] = sum(len(o["blockers"]) for o in report["organs"])
        report["summary"]["warnings_count"] = sum(len(o["warnings"]) for o in report["organs"])

        if report["summary"]["blocking_utility_failures"] > 0:
            report["verdict"] = "BLOCKED_ORGAN_UTILITY_REQUIREMENTS_FAILED"
        elif report["summary"]["warnings_count"] > 0:
            report["verdict"] = "PASS_WITH_UTILITY_WARNINGS"

    out_json = Path(args.output_json)
    out_md = Path(args.output_md)
    out_json.parent.mkdir(parents=True, exist_ok=True)
    out_md.parent.mkdir(parents=True, exist_ok=True)

    out_json.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")

    lines = []
    lines.append("# ORGAN UTILITY GAP REPORT")
    lines.append("")
    lines.append(f"- Verdict: {report.get('verdict')}")
    lines.append(f"- Root scanned: {report.get('root_scanned')}")
    lines.append(f"- Organs checked: {report['summary']['total_organs_checked']}")
    lines.append(f"- Utility declared: {report['summary']['utility_declared_count']}")
    lines.append(f"- Script-backed utilities: {report['summary']['script_backed_count']}")
    lines.append(f"- Blocking utility failures: {report['summary']['blocking_utility_failures']}")
    lines.append(f"- Warnings: {report['summary']['warnings_count']}")
    lines.append("")
    lines.append("## Organs")
    lines.append("")

    for o in report.get("organs", []):
        lines.append(f"### {o['organ_id']}")
        lines.append("")
        lines.append(f"- Status: {o['organ_status']}")
        lines.append(f"- Utility declared: {o['utility_declared']}")
        lines.append(f"- Utility path: {o.get('utility_path')}")
        lines.append(f"- Script backed: {o['script_backed']}")
        if o["blockers"]:
            lines.append("- Blockers:")
            for b in o["blockers"]:
                lines.append(f"  - {b}")
        if o["warnings"]:
            lines.append("- Warnings:")
            for w in o["warnings"]:
                lines.append(f"  - {w}")
        lines.append("")

    out_md.write_text("\n".join(lines), encoding="utf-8")

    if args.copy_json:
        copy_json = Path(args.copy_json)
        copy_json.parent.mkdir(parents=True, exist_ok=True)
        copy_json.write_text(out_json.read_text(encoding="utf-8"), encoding="utf-8")

    if args.copy_md:
        copy_md = Path(args.copy_md)
        copy_md.parent.mkdir(parents=True, exist_ok=True)
        copy_md.write_text(out_md.read_text(encoding="utf-8"), encoding="utf-8")


if __name__ == "__main__":
    main()