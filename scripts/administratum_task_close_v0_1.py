#!/usr/bin/env python3
"""Close an Administratum task session with gating rules."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from administratum_lifecycle_common_v0_1 import (
    REPO_ROOT,
    append_jsonl,
    read_json,
    session_dir,
    to_repo_rel,
    utc_now,
    write_json,
)


PASS_LIKE = {"PASS", "STAGE_PASS"}
STOP_LIKE = {"STOPPED", "STOPPED_PENDING_OWNER_APPROVAL"}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--task-id", required=True)
    parser.add_argument("--final-status", choices=["CLOSED_PASS", "CLOSED_FAIL"], default="CLOSED_PASS")
    parser.add_argument("--required-stage-id", action="append", default=[])
    parser.add_argument("--reason", default="")
    return parser.parse_args()


def evidence_exists(path_value: str) -> bool:
    candidate = Path(path_value)
    if not candidate.is_absolute():
        candidate = REPO_ROOT / path_value
    return candidate.exists()


def main() -> int:
    args = parse_args()
    now = utc_now()

    task_session_dir = session_dir(args.task_id)
    task_session_path = task_session_dir / "task_session.json"
    events_path = task_session_dir / "events.jsonl"
    final_verdict_path = task_session_dir / "final_verdict.json"

    if not task_session_path.exists():
        print(json.dumps({"status": "FAIL", "reason": "task session not found"}, ensure_ascii=True))
        return 1

    session = read_json(task_session_path)
    current_status = str(session.get("status", ""))
    if current_status.startswith("CLOSED_"):
        print(json.dumps({"status": "FAIL", "reason": "task already closed", "task_status": current_status}, ensure_ascii=True))
        return 1

    stage_reports = session.get("stage_reports", [])
    stage_map = {entry.get("stage_id"): entry for entry in stage_reports if isinstance(entry, dict)}
    required_stage_ids = args.required_stage_id or session.get("required_stage_ids", [])

    validation_errors: list[str] = []
    if args.final_status == "CLOSED_PASS":
        if current_status in STOP_LIKE:
            validation_errors.append("cannot close as CLOSED_PASS when task is stopped")
        if session.get("owner_approval_required", False):
            validation_errors.append("cannot close as CLOSED_PASS while owner_approval_required is true")
        if not required_stage_ids:
            validation_errors.append("required_stage_ids must be defined for CLOSED_PASS")
        missing_stage_ids = [stage_id for stage_id in required_stage_ids if stage_id not in stage_map]
        if missing_stage_ids:
            validation_errors.append("missing required stage report(s): " + ", ".join(missing_stage_ids))

        bad_stage_status = [
            stage_id
            for stage_id in required_stage_ids
            if stage_id in stage_map and stage_map[stage_id].get("status") not in PASS_LIKE
        ]
        if bad_stage_status:
            validation_errors.append("required stages are not PASS/STAGE_PASS: " + ", ".join(bad_stage_status))

        for stage_id in required_stage_ids:
            entry = stage_map.get(stage_id, {})
            for ev in entry.get("evidence_paths", []):
                if not evidence_exists(str(ev)):
                    validation_errors.append(f"missing evidence path for {stage_id}: {ev}")

        any_fail_like = [
            entry.get("stage_id")
            for entry in stage_reports
            if entry.get("status") in {"FAIL", "BLOCKED", "STOPPED", "STOPPED_PENDING_OWNER_APPROVAL"}
        ]
        if any_fail_like:
            validation_errors.append("task contains fail/stopped stage reports: " + ", ".join(str(x) for x in any_fail_like))

    if validation_errors:
        payload = {
            "status": "FAIL",
            "task_id": args.task_id,
            "final_status_requested": args.final_status,
            "reason": "task close gates failed",
            "validation_errors": validation_errors,
        }
        print(json.dumps(payload, ensure_ascii=True))
        return 1

    final_payload = {
        "schema_version": "administratum_task_final_verdict_v0_1",
        "task_id": args.task_id,
        "status": args.final_status,
        "reason": args.reason,
        "required_stage_ids": required_stage_ids,
        "closed_utc": now,
    }
    write_json(final_verdict_path, final_payload)

    session["status"] = args.final_status
    session["final_status"] = args.final_status
    session["updated_utc"] = now
    write_json(task_session_path, session)

    append_jsonl(
        events_path,
        {
            "timestamp_utc": now,
            "event_type": "TASK_CLOSED",
            "task_id": args.task_id,
            "status": args.final_status,
            "required_stage_ids": required_stage_ids,
        },
    )

    payload = {
        "status": "PASS",
        "task_id": args.task_id,
        "final_status": args.final_status,
        "final_verdict_path": to_repo_rel(final_verdict_path),
    }
    print(json.dumps(payload, ensure_ascii=True))
    return 0


if __name__ == "__main__":
    sys.exit(main())
