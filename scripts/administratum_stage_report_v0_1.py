#!/usr/bin/env python3
"""Record a stage report in an Administratum task session."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from administratum_lifecycle_common_v0_1 import (
    append_jsonl,
    read_json,
    session_dir,
    to_repo_rel,
    utc_now,
    write_json,
)


PASS_LIKE = {"PASS", "STAGE_PASS"}
VALID_STAGE_STATUS = {"PASS", "STAGE_PASS", "FAIL", "BLOCKED", "STOPPED", "STOPPED_PENDING_OWNER_APPROVAL"}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--task-id", required=True)
    parser.add_argument("--stage-id", required=True)
    parser.add_argument("--status", required=True, choices=sorted(VALID_STAGE_STATUS))
    parser.add_argument("--checker-status", required=True)
    parser.add_argument("--evidence-path", action="append", default=[])
    parser.add_argument("--summary", default="")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    now = utc_now()

    task_session_dir = session_dir(args.task_id)
    task_session_path = task_session_dir / "task_session.json"
    events_path = task_session_dir / "events.jsonl"
    stage_reports_dir = task_session_dir / "stage_reports"
    stage_report_path = stage_reports_dir / f"{args.stage_id}.json"

    if not task_session_path.exists():
        print(json.dumps({"status": "FAIL", "reason": "task session not found", "task_id": args.task_id}, ensure_ascii=True))
        return 1

    session = read_json(task_session_path)
    if stage_report_path.exists():
        print(json.dumps({"status": "FAIL", "reason": "stage report already exists", "stage_id": args.stage_id}, ensure_ascii=True))
        return 1

    evidence_paths = [item for item in args.evidence_path if item]
    missing_evidence: list[str] = []
    if args.status in PASS_LIKE:
        if not evidence_paths:
            print(json.dumps({"status": "FAIL", "reason": "PASS stage requires evidence paths"}, ensure_ascii=True))
            return 1
        for ev in evidence_paths:
            ev_path = Path(ev)
            if not ev_path.is_absolute():
                ev_path = Path(__file__).resolve().parents[1] / ev
            if not ev_path.exists():
                missing_evidence.append(ev)
    if missing_evidence:
        print(
            json.dumps(
                {
                    "status": "FAIL",
                    "reason": "missing required evidence path(s)",
                    "missing_evidence": missing_evidence,
                },
                ensure_ascii=True,
            )
        )
        return 1

    stage_payload = {
        "schema_version": "administratum_stage_report_v0_1",
        "task_id": args.task_id,
        "stage_id": args.stage_id,
        "status": args.status,
        "evidence_paths": evidence_paths,
        "checker_status": args.checker_status,
        "summary": args.summary,
        "timestamp_utc": now,
    }
    write_json(stage_report_path, stage_payload)

    session.setdefault("stage_reports", []).append(
        {
            "schema_version": "administratum_stage_report_v0_1",
            "task_id": args.task_id,
            "stage_id": args.stage_id,
            "status": args.status,
            "evidence_paths": evidence_paths,
            "checker_status": args.checker_status,
            "summary": args.summary,
            "timestamp_utc": now,
        }
    )
    if args.status in PASS_LIKE:
        session["status"] = "STAGE_PASS"
    elif args.status in {"FAIL", "BLOCKED"}:
        session["status"] = "BLOCKED"
    else:
        session["status"] = args.status
    session["updated_utc"] = now
    write_json(task_session_path, session)

    append_jsonl(
        events_path,
        {
            "timestamp_utc": now,
            "event_type": "STAGE_REPORTED",
            "task_id": args.task_id,
            "stage_id": args.stage_id,
            "status": args.status,
            "checker_status": args.checker_status,
            "evidence_paths": evidence_paths,
        },
    )

    print(
        json.dumps(
            {
                "status": "PASS",
                "task_id": args.task_id,
                "stage_id": args.stage_id,
                "stage_report_path": to_repo_rel(stage_report_path),
            },
            ensure_ascii=True,
        )
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
