"""Write violation record artifacts from task gate verdict for STAGE-5."""

from __future__ import annotations

from pathlib import Path

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
STAGE_ID = "STAGE-5"
GATE_REPORT = REPORTS_DIR / "task_start_gate_verdict_report.json"
VIOLATION_FILE = DOCTRINARIUM_ROOT / "VIOLATIONS" / "violation_record_v0_1.json"
VIOLATION_REPORT = REPORTS_DIR / "violation_record_report.json"


def main() -> int:
    if not GATE_REPORT.exists():
        report = build_report_base(
            report_id="doctrinarium.violation_record.v0_1",
            task_id=TASK_ID,
            stage_id=STAGE_ID,
        )
        report.update(
            {
                "started_utc": now_utc(),
                "completed_utc": now_utc(),
                "verdict": "FAIL",
                "violation_id": "N/A",
                "severity": "HIGH",
                "source": "task_start_gate",
                "warnings": [],
                "blockers": ["missing_task_start_gate_report"],
                "evidence_paths": [],
            }
        )
        dump_json(VIOLATION_REPORT, report)
        return 1

    gate = load_json(GATE_REPORT)
    allow = bool(gate.get("allow_execution", False))

    violation_record = {
        "schema_version": "imperium.doctrinarium.violation_record.v0_1",
        "violation_id": f"VIOL-{now_utc().replace(':', '').replace('-', '')}",
        "severity": "LOW" if allow else "HIGH",
        "source": "task_start_gate",
        "description": "No blocking violation. Gate allowed execution." if allow else "Blocking condition detected by task start gate.",
        "evidence_paths": gate.get("evidence_paths", []),
        "provenance": {"source": "doctrinarium_record_violation_v0_1.py"},
        "timestamp_utc": now_utc(),
    }
    dump_json(VIOLATION_FILE, violation_record)

    report = build_report_base(
        report_id="doctrinarium.violation_record.v0_1",
        task_id=TASK_ID,
        stage_id=STAGE_ID,
    )
    report.update(
        {
            "started_utc": now_utc(),
            "completed_utc": now_utc(),
            "verdict": "PASS",
            "violation_id": violation_record["violation_id"],
            "severity": violation_record["severity"],
            "source": violation_record["source"],
            "warnings": [],
            "blockers": [],
            "evidence_paths": [
                str(GATE_REPORT.relative_to(REPO_ROOT)).replace("\\", "/"),
                str(VIOLATION_FILE.relative_to(REPO_ROOT)).replace("\\", "/"),
            ],
        }
    )
    dump_json(VIOLATION_REPORT, report)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

