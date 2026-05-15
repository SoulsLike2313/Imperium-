"""Evaluate organ health from collected self-reports for STAGE-4."""

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
STAGE_ID = "STAGE-4"
COLLECTION_REPORT = REPORTS_DIR / "organ_self_report_collection_report.json"
HEALTH_REPORT = REPORTS_DIR / "organ_health_verdict_report.json"
FRESHNESS_SECONDS_MAX = 86400  # 24h


def parse_utc(value: str) -> datetime:
    normalized = value.replace("Z", "+00:00")
    return datetime.fromisoformat(normalized).astimezone(timezone.utc)


def evaluate_freshness(checker_last_run_utc: str) -> int:
    now = datetime.now(timezone.utc)
    delta = now - parse_utc(checker_last_run_utc)
    return int(delta.total_seconds())


def main() -> int:
    blockers: List[str] = []
    warnings: List[str] = []
    reasons: List[str] = []
    evidence_paths: List[str] = []

    if not COLLECTION_REPORT.exists():
        blockers.append("missing_collection_report")
        collection = {}
    else:
        collection = load_json(COLLECTION_REPORT)
        evidence_paths.append(str(COLLECTION_REPORT.relative_to(REPO_ROOT)).replace("\\", "/"))

    collected_organs = collection.get("organs_collected", [])
    if not collected_organs:
        blockers.append("no_collected_organs")

    target_report_path = DOCTRINARIUM_ROOT / "ORGAN_HEALTH" / "COLLECTED_SELF_REPORTS" / "DOCTRINARIUM_self_report.json"
    if not target_report_path.exists():
        blockers.append("missing_doctrinarium_self_report")
        self_report: Dict[str, object] = {}
    else:
        self_report = load_json(target_report_path)
        evidence_paths.append(str(target_report_path.relative_to(REPO_ROOT)).replace("\\", "/"))

    checker_last_run_utc = str(self_report.get("checker_last_run_utc", "")) if self_report else ""
    freshness_seconds = None
    if checker_last_run_utc:
        freshness_seconds = evaluate_freshness(checker_last_run_utc)
        if freshness_seconds > FRESHNESS_SECONDS_MAX:
            blockers.append("stale_self_report")
            reasons.append("self_report_is_stale")
    else:
        blockers.append("missing_checker_last_run_utc")

    for organ in collection.get("missing_organs", []):
        warnings.append(f"missing_non_required_or_unavailable_self_report:{organ}")

    if blockers:
        health_verdict = "BLOCKED"
        checker_verdict = "FAIL"
    elif warnings:
        health_verdict = "DEGRADED"
        checker_verdict = "PASS_WITH_WARNINGS"
    else:
        health_verdict = "HEALTHY"
        checker_verdict = "PASS"

    report = build_report_base(
        report_id="doctrinarium.organ_health_verdict.v0_1",
        task_id=TASK_ID,
        stage_id=STAGE_ID,
    )
    report.update(
        {
            "started_utc": now_utc(),
            "completed_utc": now_utc(),
            "verdict": checker_verdict,
            "organ_id": "DOCTRINARIUM",
            "health_verdict": health_verdict,
            "checker_last_run_utc": checker_last_run_utc,
            "freshness_seconds": freshness_seconds,
            "required_freshness_seconds_max": FRESHNESS_SECONDS_MAX,
            "warnings": warnings,
            "blockers": blockers,
            "reasons": reasons,
            "evidence_paths": evidence_paths,
            "freshness_guard": {
                "stale_should_fail": True,
                "evaluated": True,
            },
        }
    )
    dump_json(HEALTH_REPORT, report)
    return 0 if checker_verdict in ("PASS", "PASS_WITH_WARNINGS") else 1


if __name__ == "__main__":
    raise SystemExit(main())

