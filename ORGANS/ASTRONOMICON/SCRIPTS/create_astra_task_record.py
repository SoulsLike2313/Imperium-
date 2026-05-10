#!/usr/bin/env python3
"""Create Astra route draft artifacts (foundation v0.1)."""

from __future__ import annotations

import argparse
import json
import re
from datetime import datetime
from pathlib import Path

RUN_RE = re.compile(r"^RUN-\d{8}-[A-Z0-9\-]{3,16}-\d{4}$")
TASK_ROUTE_VERSION = "0.1"
ROUTE_STATUS = "DRAFT"


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Create Astra route draft artifacts.")
    p.add_argument("--task-id", required=True)
    p.add_argument("--run-id", required=True)
    p.add_argument("--output-dir", required=True)
    p.add_argument("--owner-text", default="")
    p.add_argument("--owner-text-file", default="")
    return p.parse_args()


def stage_metrics_template() -> dict:
    return {
        "started_at": "",
        "ended_at": "",
        "duration_sec": 0,
        "files_read": 0,
        "files_written": 0,
        "scripts_run": 0,
        "validation_result": "NOT_RUN",
        "repair_attempts": 0,
        "max_repair_attempts": 2,
        "risk_score": 0,
        "confidence_score": 0,
        "usability_score": 0,
        "evidence_completeness_score": 0,
        "drift_count": 0,
        "duplicate_count": 0,
        "forbidden_ref_count": 0,
        "owner_approval_required": False,
        "owner_approval_reason": "",
        "next_allowed_action": "",
    }


def write_json(path: Path, data: dict) -> None:
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def main() -> int:
    args = parse_args()
    if not RUN_RE.fullmatch(args.run_id):
        raise ValueError(f"Invalid run_id format: {args.run_id}")

    owner_text = args.owner_text.strip()
    if args.owner_text_file:
        owner_text = Path(args.owner_text_file).read_text(encoding="utf-8", errors="ignore").strip()

    out = Path(args.output_dir).resolve()
    out.mkdir(parents=True, exist_ok=True)

    stages = [
        ("ASTRA-STAGE-001", "ASTRONOMICON"),
        ("ADMINISTRATUM-STAGE-001", "ADMINISTRATUM"),
        ("MECHANICUS-STAGE-001", "MECHANICUS"),
        ("INQUISITION-STAGE-001", "INQUISITION"),
        ("PC-STAGE-001", "PC_SERVITOR"),
        ("SPECULUM-STAGE-001", "SPECULUM_REVIEW_PLANNED"),
    ]
    stage_rows = []
    for i, (sid, organ) in enumerate(stages, start=1):
        stage_rows.append(
            {
                "stage_number": i,
                "stage_id": sid,
                "organ": organ,
                "status": "PLANNED",
                "stage_metrics_template": stage_metrics_template(),
            }
        )

    policy_refs = [
        {
            "policy_id": "POLICY-STAGE-ID-CANON-0_1",
            "path": r"E:\IMPERIUM\ORGANS\ADMINISTRATUM\POLICIES\STAGE_ID_POLICY.json",
        },
        {
            "policy_id": "POLICY-NO-THRONE-0_1",
            "path": r"E:\IMPERIUM\ORGANS\ADMINISTRATUM\POLICIES\NO_THRONE_POLICY.json",
        },
    ]
    policy_hashes = [
        {"policy_id": row["policy_id"], "sha256": "POLICY_HASH_PENDING", "status": "POLICY_HASH_PENDING"}
        for row in policy_refs
    ]

    record = {
        "schema_version": "ASTRA_TASK_RECORD_V0_4",
        "task_id": args.task_id,
        "RUN_ID": args.run_id,
        "TASK_ROUTE_VERSION": TASK_ROUTE_VERSION,
        "ASTRA_ROUTE_STATUS": ROUTE_STATUS,
        "created_at_local": datetime.now().isoformat(timespec="seconds"),
        "owner_task_text": owner_text,
        "policy_refs": policy_refs,
        "policy_hashes": policy_hashes,
        "stages": stage_rows,
    }
    write_json(out / "ASTRA_TASK_RECORD.json", record)
    write_json(
        out / "STAGE_MAP.json",
        {
            "schema_version": "ASTRA_STAGE_MAP_V0_4",
            "task_id": args.task_id,
            "RUN_ID": args.run_id,
            "TASK_ROUTE_VERSION": TASK_ROUTE_VERSION,
            "stages": stage_rows,
        },
    )
    write_json(
        out / "PASS_CRITERIA.json",
        {
            "schema_version": "ASTRA_PASS_CRITERIA_V0_4",
            "task_id": args.task_id,
            "RUN_ID": args.run_id,
            "minimum_requirements": [
                "stage receipts per stage",
                "validation reports per stage",
                "no fake green",
                "no VM2/THRONE/E2E activation",
            ],
        },
    )
    write_json(
        out / "NEXT_ALLOWED_ACTION.json",
        {
            "task_id": args.task_id,
            "RUN_ID": args.run_id,
            "next_action": "ADMINISTRATUM_BUILD_ROUTE",
            "blocked_actions": ["VM2_ACTIVATION", "THRONE_CONTACT", "E2E_ACTIVATION"],
        },
    )
    write_json(
        out / "PIPELINE_PROFILE.json",
        {
            "task_id": args.task_id,
            "RUN_ID": args.run_id,
            "TASK_ROUTE_VERSION": TASK_ROUTE_VERSION,
            "profile": "MANUAL_OWNER_ROUTE",
            "local_only": True,
        },
    )
    write_json(
        out / "ROUTE_STATUS.json",
        {
            "task_id": args.task_id,
            "RUN_ID": args.run_id,
            "TASK_ROUTE_VERSION": TASK_ROUTE_VERSION,
            "ASTRA_ROUTE_STATUS": ROUTE_STATUS,
            "allowed_values": [
                "DRAFT",
                "OWNER_REVIEW",
                "APPROVED_FOR_ADMINISTRATUM_ROUTE",
                "BLOCKED",
            ],
            "policy_hash_status": "POLICY_HASH_PENDING",
            "updated_at_local": datetime.now().isoformat(timespec="seconds"),
        },
    )
    (out / "OWNER_TASK_BRIEF.md").write_text(
        "# OWNER TASK BRIEF\n\n"
        f"TASK_ID: {args.task_id}\n"
        f"RUN_ID: {args.run_id}\n"
        f"TASK_ROUTE_VERSION: {TASK_ROUTE_VERSION}\n"
        f"ASTRA_ROUTE_STATUS: {ROUTE_STATUS}\n\n"
        "## Owner text\n\n"
        + (owner_text or "_EMPTY_")
        + "\n",
        encoding="utf-8",
    )
    (out / "ASTRA_PIPELINE_DRAFT.md").write_text(
        "# ASTRA PIPELINE DRAFT\n\n"
        f"TASK_ID: {args.task_id}\n"
        f"RUN_ID: {args.run_id}\n"
        f"TASK_ROUTE_VERSION: {TASK_ROUTE_VERSION}\n"
        f"ASTRA_ROUTE_STATUS: {ROUTE_STATUS}\n",
        encoding="utf-8",
    )
    print(f"created route draft: {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
