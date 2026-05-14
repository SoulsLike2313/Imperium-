#!/usr/bin/env python3
"""Stop an Administratum task session with explicit reason."""

from __future__ import annotations

import argparse
import json
import sys

from administratum_lifecycle_common_v0_1 import (
    append_jsonl,
    read_json,
    session_dir,
    to_repo_rel,
    utc_now,
    write_json,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--task-id", required=True)
    parser.add_argument("--failed-stage-id", required=True)
    parser.add_argument("--stop-reason", required=True)
    parser.add_argument(
        "--status",
        choices=["STOPPED", "STOPPED_PENDING_OWNER_APPROVAL"],
        default="STOPPED_PENDING_OWNER_APPROVAL",
    )
    parser.add_argument(
        "--owner-approval-required",
        choices=["true", "false"],
        default="true",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    now = utc_now()

    task_session_dir = session_dir(args.task_id)
    task_session_path = task_session_dir / "task_session.json"
    events_path = task_session_dir / "events.jsonl"
    stop_record_path = task_session_dir / "stop_record.json"

    if not task_session_path.exists():
        print(json.dumps({"status": "FAIL", "reason": "task session not found", "task_id": args.task_id}, ensure_ascii=True))
        return 1

    session = read_json(task_session_path)
    if str(session.get("status", "")).startswith("CLOSED_"):
        print(json.dumps({"status": "FAIL", "reason": "cannot stop a closed task"}, ensure_ascii=True))
        return 1

    owner_approval_required = args.owner_approval_required.lower() == "true"
    stop_payload = {
        "schema_version": "administratum_task_stop_record_v0_1",
        "task_id": args.task_id,
        "status": args.status,
        "failed_stage_id": args.failed_stage_id,
        "stop_reason": args.stop_reason,
        "owner_approval_required": owner_approval_required,
        "timestamp_utc": now,
    }
    write_json(stop_record_path, stop_payload)

    session["status"] = args.status
    session["failed_stage_id"] = args.failed_stage_id
    session["stop_reason"] = args.stop_reason
    session["owner_approval_required"] = owner_approval_required
    session["updated_utc"] = now
    write_json(task_session_path, session)

    append_jsonl(
        events_path,
        {
            "timestamp_utc": now,
            "event_type": "TASK_STOPPED",
            "task_id": args.task_id,
            "status": args.status,
            "failed_stage_id": args.failed_stage_id,
            "owner_approval_required": owner_approval_required,
        },
    )

    print(
        json.dumps(
            {
                "status": "PASS",
                "task_id": args.task_id,
                "stop_record_path": to_repo_rel(stop_record_path),
                "task_status": args.status,
                "owner_approval_required": owner_approval_required,
            },
            ensure_ascii=True,
        )
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
