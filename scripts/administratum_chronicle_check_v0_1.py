#!/usr/bin/env python3
"""Administratum Chronicle Checker v0.1."""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


REQUIRED_INITIAL_SUMMARIES = [
    "Astronomicon backend corridor proved.",
    "Servitor execution intake proved.",
    "Language policy accepted.",
    "Handoff created.",
    "READY_FOR_AGENT remains false.",
    "VM2 remains DEFERRED_OFFLINE.",
    "Lesson: PowerShell ConvertTo-Json -Depth max is 100.",
    "Lesson: Task IDs must be copied exactly.",
    "Lesson: artifact provenance git_head is not current Git HEAD.",
    "Lesson: canonical machine/repo artifacts should be English-only by default.",
]

ALLOWED_PASS_EVENT_TYPES = {
    "SYSTEM_MILESTONE",
    "POLICY_EVENT",
    "TASK_STAGE",
    "TASK_RESULT",
}


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--chronicle",
        default="ORGANS/ADMINISTRATUM/CHRONICLE/imperium_chronicle_v0_1.jsonl",
    )
    parser.add_argument(
        "--schema",
        default="schemas/administratum_chronicle_entry.schema.json",
    )
    parser.add_argument(
        "--report",
        default="ORGANS/ADMINISTRATUM/REPORTS/chronicle_check_report_v0_1.json",
    )
    args = parser.parse_args()

    repo_root = Path(__file__).resolve().parents[1]
    chronicle_path = repo_root / args.chronicle
    schema_path = repo_root / args.schema
    report_path = repo_root / args.report
    report_path.parent.mkdir(parents=True, exist_ok=True)

    checks: dict[str, bool] = {}
    failures: list[str] = []
    parsed_events: list[dict[str, Any]] = []

    try:
        schema = load_json(schema_path)
        schema_required = schema.get("required", [])
    except Exception as exc:
        payload = {
            "schema_version": "administratum_chronicle_check_report_v0_1",
            "status": "FAIL",
            "checked_utc": utc_now(),
            "error": f"Failed to load schema: {exc}",
        }
        report_path.write_text(json.dumps(payload, ensure_ascii=True, indent=2) + "\n", encoding="utf-8")
        print(json.dumps(payload, ensure_ascii=True))
        return 2

    lines = chronicle_path.read_text(encoding="utf-8").splitlines()
    parse_errors: list[str] = []
    for idx, line in enumerate(lines, start=1):
        if not line.strip():
            continue
        try:
            entry = json.loads(line)
            if not isinstance(entry, dict):
                parse_errors.append(f"Line {idx} is not a JSON object")
                continue
            parsed_events.append(entry)
        except json.JSONDecodeError as exc:
            parse_errors.append(f"Line {idx} JSON parse error: {exc}")

    checks["jsonl_lines_parse"] = len(parse_errors) == 0
    failures.extend(parse_errors)

    field_errors: list[str] = []
    for idx, event in enumerate(parsed_events, start=1):
        for key in schema_required:
            if key not in event:
                field_errors.append(f"Line {idx} missing required field '{key}'")
        if "task_id" not in event and "global_scope" not in event:
            field_errors.append(f"Line {idx} requires task_id or global_scope")
    checks["required_fields_present"] = len(field_errors) == 0
    failures.extend(field_errors)

    event_ids = [str(event.get("event_id", "")) for event in parsed_events]
    dup_ids = sorted({event_id for event_id in event_ids if event_ids.count(event_id) > 1 and event_id})
    checks["event_ids_unique"] = len(dup_ids) == 0
    if dup_ids:
        failures.append(f"Duplicate event_id values: {', '.join(dup_ids)}")

    unsupported_pass: list[str] = []
    for event in parsed_events:
        if event.get("status") == "PASS" and event.get("event_type") not in ALLOWED_PASS_EVENT_TYPES:
            unsupported_pass.append(str(event.get("event_id")))
    checks["no_unsupported_pass_claims"] = len(unsupported_pass) == 0
    if unsupported_pass:
        failures.append(f"Unsupported PASS claim event_ids: {', '.join(unsupported_pass)}")

    provenance_errors: list[str] = []
    for event in parsed_events:
        current_truth = event.get("current_git_truth")
        artifact_provenance = event.get("artifact_provenance")
        if not isinstance(current_truth, dict) or not isinstance(artifact_provenance, dict):
            provenance_errors.append(f"{event.get('event_id')}: provenance fields must be objects")
            continue
        if current_truth == artifact_provenance:
            provenance_errors.append(f"{event.get('event_id')}: current_git_truth and artifact_provenance must be distinct")
    checks["provenance_fields_separate"] = len(provenance_errors) == 0
    failures.extend(provenance_errors)

    contradiction_errors: list[str] = []
    task_state: dict[str, str] = {}
    for event in parsed_events:
        task_id = event.get("task_id")
        if not task_id:
            continue
        status = str(event.get("status", ""))
        event_type = str(event.get("event_type", ""))
        last_status = task_state.get(task_id, "")

        if last_status.startswith("CLOSED_") and status in {"ACTIVE", "STAGE_PASS"} and event_type != "TASK_REOPENED":
            contradiction_errors.append(
                f"{event.get('event_id')}: task {task_id} reopened without TASK_REOPENED event"
            )
        if last_status == "CLOSED_PASS" and status == "CLOSED_FAIL":
            contradiction_errors.append(f"{event.get('event_id')}: task {task_id} contradictory CLOSED_FAIL after CLOSED_PASS")
        if last_status == "CLOSED_FAIL" and status == "CLOSED_PASS":
            contradiction_errors.append(f"{event.get('event_id')}: task {task_id} contradictory CLOSED_PASS after CLOSED_FAIL")

        task_state[task_id] = status

    checks["no_contradictory_status_entries"] = len(contradiction_errors) == 0
    failures.extend(contradiction_errors)

    lower_summaries = [str(event.get("summary", "")).lower() for event in parsed_events]
    missing_initial = [
        item for item in REQUIRED_INITIAL_SUMMARIES
        if item.lower() not in lower_summaries
    ]
    checks["required_initial_entries_present"] = len(missing_initial) == 0
    if missing_initial:
        failures.append("Missing initial memory entries: " + "; ".join(missing_initial))

    checks["line_count_at_least_required"] = len(parsed_events) >= len(REQUIRED_INITIAL_SUMMARIES)
    if len(parsed_events) < len(REQUIRED_INITIAL_SUMMARIES):
        failures.append("Chronicle has fewer events than required initial memory entries")

    status = "PASS" if all(checks.values()) else "FAIL"
    payload = {
        "schema_version": "administratum_chronicle_check_report_v0_1",
        "status": status,
        "checked_utc": utc_now(),
        "chronicle_path": str(chronicle_path.relative_to(repo_root)).replace("\\", "/"),
        "schema_path": str(schema_path.relative_to(repo_root)).replace("\\", "/"),
        "events_checked": len(parsed_events),
        "checks": checks,
        "failures": failures,
    }
    report_path.write_text(json.dumps(payload, ensure_ascii=True, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(payload, ensure_ascii=True))
    return 0 if status == "PASS" else 1


if __name__ == "__main__":
    sys.exit(main())
