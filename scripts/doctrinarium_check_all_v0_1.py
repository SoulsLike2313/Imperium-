"""Run integrated Doctrinarium checks and anti-fake-green tests for STAGE-7."""

from __future__ import annotations

import json
import re
import subprocess
from pathlib import Path
from typing import Dict, List

from doctrinarium_common_v0_1 import (
    DOCTRINARIUM_ROOT,
    REPORTS_DIR,
    REPO_ROOT,
    build_report_base,
    dump_json,
    load_json,
    now_utc,
)


TASK_ID = "TASK-20260515-DOCTRINARIUM-MVP-V0_1"
STAGE_ID = "STAGE-7"
CHECK_ALL_REPORT = REPORTS_DIR / "check_all_report.json"
FAKE_GREEN_REPORT = DOCTRINARIUM_ROOT / "TESTS" / "fake_green_test_report.json"


def run_command(command: List[str]) -> Dict[str, object]:
    completed = subprocess.run(command, cwd=REPO_ROOT, capture_output=True, text=True, check=False)
    return {
        "command": " ".join(command),
        "exit_code": completed.returncode,
        "stdout_tail": completed.stdout[-800:] if completed.stdout else "",
        "stderr_tail": completed.stderr[-800:] if completed.stderr else "",
    }


def report_has_evidence(report_doc: Dict[str, object]) -> bool:
    evidence_paths = report_doc.get("evidence_paths", [])
    return isinstance(evidence_paths, list) and len(evidence_paths) > 0


def check_canonical_language() -> Dict[str, object]:
    cyr = re.compile(r"[\u0400-\u04FF]")
    hits: List[str] = []
    scope_roots = [
        DOCTRINARIUM_ROOT / "README.md",
        DOCTRINARIUM_ROOT / "DOCS",
        DOCTRINARIUM_ROOT / "DOCTRINES",
        DOCTRINARIUM_ROOT / "LAWS",
        DOCTRINARIUM_ROOT / "LAW_REGISTRY",
        DOCTRINARIUM_ROOT / "GATES",
        DOCTRINARIUM_ROOT / "ORGAN_HEALTH",
        DOCTRINARIUM_ROOT / "VIOLATIONS",
        DOCTRINARIUM_ROOT / "INQUISITION_HOOKS",
        DOCTRINARIUM_ROOT / "REGISTRY",
        DOCTRINARIUM_ROOT / "SCHEMAS",
        DOCTRINARIUM_ROOT / "TESTS",
        DOCTRINARIUM_ROOT / "REPORTS",
    ]
    for root in scope_roots:
        if not root.exists():
            continue
        paths = [root] if root.is_file() else [p for p in root.rglob("*") if p.is_file()]
        for path in paths:
            if path.suffix.lower() not in {".json", ".md"}:
                continue
            text = path.read_text(encoding="utf-8", errors="ignore")
            if cyr.search(text):
                hits.append(str(path.relative_to(REPO_ROOT)).replace("\\", "/"))
    return {"cyrillic_hits": hits, "ok": len(hits) == 0}


def build_fake_green_report(live_reports: Dict[str, Dict[str, object]]) -> Dict[str, object]:
    scenarios = []

    synthetic_pass_no_evidence = {"verdict": "PASS", "evidence_paths": []}
    scenarios.append(
        {
            "scenario_id": "FG-001",
            "name": "pass_without_evidence_paths",
            "expected_risk": True,
            "risk_detected": not report_has_evidence(synthetic_pass_no_evidence),
        }
    )

    synthetic_pass_warn_empty = {"verdict": "PASS_WITH_WARNINGS", "warnings": []}
    scenarios.append(
        {
            "scenario_id": "FG-002",
            "name": "pass_with_warnings_but_empty_warning_list",
            "expected_risk": True,
            "risk_detected": synthetic_pass_warn_empty["verdict"] == "PASS_WITH_WARNINGS"
            and len(synthetic_pass_warn_empty["warnings"]) == 0,
        }
    )

    live_hook = live_reports.get("inquisition_hook_disabled_report.json", {})
    scenarios.append(
        {
            "scenario_id": "FG-003",
            "name": "disabled_hook_must_not_appear_active",
            "expected_risk": False,
            "risk_detected": live_hook.get("hook_state") != "disabled" or live_hook.get("send_attempted") is not False,
        }
    )

    live_evidence_missing = []
    for name, report_doc in live_reports.items():
        if not report_has_evidence(report_doc):
            live_evidence_missing.append(name)
    scenarios.append(
        {
            "scenario_id": "FG-004",
            "name": "live_reports_must_have_evidence_paths",
            "expected_risk": False,
            "risk_detected": len(live_evidence_missing) > 0,
            "details": live_evidence_missing,
        }
    )

    bad = []
    for row in scenarios:
        expected_risk = bool(row.get("expected_risk"))
        risk_detected = bool(row.get("risk_detected"))
        if expected_risk and not risk_detected:
            bad.append(f"{row['scenario_id']}:expected_risk_not_detected")
        if not expected_risk and risk_detected:
            bad.append(f"{row['scenario_id']}:false_positive_or_live_risk")

    verdict = "PASS" if not bad else "FAIL"
    report = {
        "schema_version": "imperium.doctrinarium.fake_green_test_report.v0_1",
        "task_id": TASK_ID,
        "stage_id": STAGE_ID,
        "timestamp_utc": now_utc(),
        "scenarios": scenarios,
        "verdict": verdict,
        "warnings": [],
        "blockers": bad,
        "evidence_paths": [
            str((REPORTS_DIR / "foundation_validation_report.json").relative_to(REPO_ROOT)).replace("\\", "/"),
            str((REPORTS_DIR / "law_registry_validation_report.json").relative_to(REPO_ROOT)).replace("\\", "/"),
            str((REPORTS_DIR / "law_integrity_report.json").relative_to(REPO_ROOT)).replace("\\", "/"),
            str((REPORTS_DIR / "organ_health_verdict_report.json").relative_to(REPO_ROOT)).replace("\\", "/"),
            str((REPORTS_DIR / "task_start_gate_verdict_report.json").relative_to(REPO_ROOT)).replace("\\", "/"),
            str((REPORTS_DIR / "inquisition_hook_disabled_report.json").relative_to(REPO_ROOT)).replace("\\", "/"),
        ],
    }
    dump_json(FAKE_GREEN_REPORT, report)
    return report


def main() -> int:
    commands = [
        ["py", "-3", "scripts/doctrinarium_validate_foundation_v0_1.py"],
        ["py", "-3", "scripts/doctrinarium_validate_law_registry_v0_1.py"],
        ["py", "-3", "scripts/doctrinarium_check_law_integrity_v0_1.py"],
        ["py", "-3", "scripts/doctrinarium_collect_organ_self_reports_v0_1.py"],
        ["py", "-3", "scripts/doctrinarium_evaluate_organ_health_v0_1.py"],
        [
            "py",
            "-3",
            "scripts/doctrinarium_task_start_gate_v0_1.py",
            "--task-id",
            TASK_ID,
            "--requesting-agent",
            "PC Servitor",
            "--mode",
            "cold_executor",
        ],
        ["py", "-3", "scripts/doctrinarium_record_violation_v0_1.py"],
        ["py", "-3", "scripts/doctrinarium_verify_inquisition_hook_disabled_v0_1.py"],
    ]

    checker_results = [run_command(command) for command in commands]
    checker_failures = [row["command"] for row in checker_results if int(row["exit_code"]) != 0]

    report_files = [
        "foundation_validation_report.json",
        "schema_validation_report.json",
        "law_registry_validation_report.json",
        "law_integrity_report.json",
        "organ_self_report_collection_report.json",
        "organ_health_verdict_report.json",
        "task_start_gate_verdict_report.json",
        "violation_record_report.json",
        "inquisition_hook_disabled_report.json",
    ]
    live_reports: Dict[str, Dict[str, object]] = {}
    missing_reports: List[str] = []
    for name in report_files:
        path = REPORTS_DIR / name
        if not path.exists():
            missing_reports.append(name)
            continue
        live_reports[name] = load_json(path)

    fake_green_report = build_fake_green_report(live_reports)
    language_scan = check_canonical_language()

    blockers: List[str] = []
    warnings: List[str] = []
    if checker_failures:
        blockers.append("subcheck_failures")
    if missing_reports:
        blockers.append("missing_required_reports")
    if fake_green_report.get("verdict") != "PASS":
        blockers.append("fake_green_checks_failed")
    if not language_scan["ok"]:
        blockers.append("canonical_language_scan_failed")

    evidence_paths: List[str] = []
    for name in report_files:
        evidence_paths.append(str((REPORTS_DIR / name).relative_to(REPO_ROOT)).replace("\\", "/"))
    evidence_paths.append(str(FAKE_GREEN_REPORT.relative_to(REPO_ROOT)).replace("\\", "/"))

    if blockers:
        verdict = "FAIL"
    elif warnings:
        verdict = "PASS_WITH_WARNINGS"
    else:
        verdict = "PASS"

    report = build_report_base(
        report_id="doctrinarium.check_all.v0_1",
        task_id=TASK_ID,
        stage_id=STAGE_ID,
    )
    report.update(
        {
            "started_utc": now_utc(),
            "completed_utc": now_utc(),
            "verdict": verdict,
            "checker_results": checker_results,
            "checker_failures": checker_failures,
            "missing_reports": missing_reports,
            "stage_reports": report_files,
            "warnings": warnings,
            "blockers": blockers,
            "fake_green_test_verdict": fake_green_report.get("verdict"),
            "canonical_language_scan": language_scan,
            "evidence_paths": evidence_paths,
        }
    )
    dump_json(CHECK_ALL_REPORT, report)
    return 0 if verdict in ("PASS", "PASS_WITH_WARNINGS") else 1


if __name__ == "__main__":
    raise SystemExit(main())
