#!/usr/bin/env python3
"""Create an Administratum task session."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from administratum_lifecycle_common_v0_1 import (
    REPO_ROOT,
    append_jsonl,
    session_dir,
    to_repo_rel,
    utc_now,
    write_json,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--task-id", required=True)
    parser.add_argument("--task-title", default="")
    parser.add_argument("--required-stage-id", action="append", default=[])
    parser.add_argument("--allow-existing", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    now = utc_now()
    task_session_dir = session_dir(args.task_id)
    task_session_path = task_session_dir / "task_session.json"
    events_path = task_session_dir / "events.jsonl"
    stage_reports_dir = task_session_dir / "stage_reports"
    evidence_dir = task_session_dir / "evidence"

    if task_session_path.exists() and not args.allow_existing:
        payload = {
            "status": "FAIL",
            "reason": "task session already exists",
            "task_id": args.task_id,
            "task_session_path": to_repo_rel(task_session_path),
        }
        print(json.dumps(payload, ensure_ascii=True))
        return 1

    stage_reports_dir.mkdir(parents=True, exist_ok=True)
    evidence_dir.mkdir(parents=True, exist_ok=True)

    session_payload = {
        "schema_version": "administratum_task_session_v0_1",
        "task_id": args.task_id,
        "task_title": args.task_title,
        "status": "ACTIVE",
        "created_utc": now,
        "updated_utc": now,
        "required_stage_ids": args.required_stage_id,
        "stage_reports": [],
        "owner_approval_required": False,
        "failed_stage_id": None,
        "stop_reason": None,
        "final_status": None,
        "paths": {
            "session_dir": to_repo_rel(task_session_dir),
            "events_jsonl": to_repo_rel(events_path),
            "stage_reports_dir": to_repo_rel(stage_reports_dir),
            "evidence_dir": to_repo_rel(evidence_dir),
        },
    }
    write_json(task_session_path, session_payload)

    append_jsonl(
        events_path,
        {
            "timestamp_utc": now,
            "event_type": "TASK_STARTED",
            "task_id": args.task_id,
            "status": "ACTIVE",
            "required_stage_ids": args.required_stage_id,
        },
    )

    payload = {
        "status": "PASS",
        "task_id": args.task_id,
        "task_session_path": to_repo_rel(task_session_path),
        "events_path": to_repo_rel(events_path),
        "repo_root": str(REPO_ROOT).replace("/", "\\"),
    }
    print(json.dumps(payload, ensure_ascii=True))
    return 0


if __name__ == "__main__":
    sys.exit(main())
