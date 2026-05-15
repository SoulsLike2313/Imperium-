"""Self-build evaluation for Doctrinarium STAGE-8."""

from __future__ import annotations

from datetime import datetime, timezone
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
STAGE_ID = "STAGE-8"
REPORT_PATH = REPORTS_DIR / "self_build_evaluation_report.json"
RECEIPT_PATH = REPORTS_DIR / "self_build_receipt.json"
SELF_REPORT_MAX_AGE_SECONDS = 86400


def parse_utc(value: str) -> datetime:
    return datetime.fromisoformat(value.replace("Z", "+00:00")).astimezone(timezone.utc)


def freshness_seconds(ts: str) -> int:
    return int((datetime.now(timezone.utc) - parse_utc(ts)).total_seconds())


def main() -> int:
    blockers: List[str] = []
    warnings: List[str] = []
    evidence_graph: List[Dict[str, object]] = []

    self_report_path = REPORTS_DIR / "organ_self_report_v0_1.json"
    check_all_path = REPORTS_DIR / "check_all_report.json"

    if not self_report_path.exists():
        blockers.append("missing_doctrinarium_self_report")
        self_report = {}
    else:
        self_report = load_json(self_report_path)
        evidence_graph.append(
            {
                "path": str(self_report_path.relative_to(REPO_ROOT)).replace("\\", "/"),
                "exists": True,
                "type": "organ_self_report",
            }
        )

    if not check_all_path.exists():
        blockers.append("missing_check_all_report")
        check_all = {}
    else:
        check_all = load_json(check_all_path)
        evidence_graph.append(
            {
                "path": str(check_all_path.relative_to(REPO_ROOT)).replace("\\", "/"),
                "exists": True,
                "type": "integration_report",
            }
        )

    self_checker_ts = str(self_report.get("checker_last_run_utc", ""))
    if not self_checker_ts:
        blockers.append("self_report_missing_checker_last_run_utc")
        self_report_age = None
    else:
        self_report_age = freshness_seconds(self_checker_ts)
        if self_report_age > SELF_REPORT_MAX_AGE_SECONDS:
            blockers.append("self_report_stale")

    check_all_verdict = str(check_all.get("verdict", ""))
    if check_all_verdict not in ("PASS", "PASS_WITH_WARNINGS"):
        blockers.append("check_all_not_pass")

    check_all_warnings = check_all.get("warnings", [])
    if check_all_verdict == "PASS_WITH_WARNINGS" and (not isinstance(check_all_warnings, list) or len(check_all_warnings) == 0):
        blockers.append("fake_green_pass_with_warnings_but_empty_list")

    # Validate evidence paths from check_all point to real files.
    missing_evidence = []
    for rel in check_all.get("evidence_paths", []):
        target = REPO_ROOT / rel
        exists = target.exists()
        evidence_graph.append({"path": rel, "exists": exists, "type": "check_all_evidence"})
        if not exists:
            missing_evidence.append(rel)
    if missing_evidence:
        blockers.append("missing_check_all_evidence_paths")

    if blockers:
        verdict = "FAIL"
    elif warnings:
        verdict = "PASS_WITH_WARNINGS"
    else:
        verdict = "PASS"

    report = build_report_base(
        report_id="doctrinarium.self_build_evaluation.v0_1",
        task_id=TASK_ID,
        stage_id=STAGE_ID,
    )
    report.update(
        {
            "started_utc": now_utc(),
            "completed_utc": now_utc(),
            "verdict": verdict,
            "self_report_freshness_seconds": self_report_age,
            "self_report_freshness_seconds_max": SELF_REPORT_MAX_AGE_SECONDS,
            "check_all_verdict": check_all_verdict,
            "warnings": warnings,
            "blockers": blockers,
            "evidence_graph": evidence_graph,
            "evidence_paths": [node["path"] for node in evidence_graph],
        }
    )
    dump_json(REPORT_PATH, report)

    receipt = {
        "schema_version": "imperium.doctrinarium.receipt.v0_1",
        "receipt_id": f"SELF-BUILD-{now_utc().replace(':', '').replace('-', '')}",
        "task_id": TASK_ID,
        "stage_id": STAGE_ID,
        "verdict": verdict,
        "report_path": str(REPORT_PATH.relative_to(REPO_ROOT)).replace("\\", "/"),
        "evidence_paths": [str(REPORT_PATH.relative_to(REPO_ROOT)).replace("\\", "/")],
        "timestamp_utc": now_utc(),
    }
    dump_json(RECEIPT_PATH, receipt)
    return 0 if verdict in ("PASS", "PASS_WITH_WARNINGS") else 1


if __name__ == "__main__":
    raise SystemExit(main())
