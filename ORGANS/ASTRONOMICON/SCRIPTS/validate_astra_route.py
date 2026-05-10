#!/usr/bin/env python3
"""Validate Astra route draft artifacts (foundation v0.1)."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

RUN_RE = re.compile(r"^RUN-\d{8}-[A-Z0-9\-]{3,16}-\d{4}$")
ALLOWED_ROUTE_STATUS = {"DRAFT", "OWNER_REVIEW", "APPROVED_FOR_ADMINISTRATUM_ROUTE", "BLOCKED"}
REQUIRED_FILES = [
    "ASTRA_TASK_RECORD.json",
    "STAGE_MAP.json",
    "PASS_CRITERIA.json",
    "NEXT_ALLOWED_ACTION.json",
    "PIPELINE_PROFILE.json",
    "ROUTE_STATUS.json",
    "OWNER_TASK_BRIEF.md",
    "ASTRA_PIPELINE_DRAFT.md",
]


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Validate Astra route files.")
    p.add_argument("--route-dir", required=True)
    p.add_argument("--report-out", default="")
    return p.parse_args()


def main() -> int:
    args = parse_args()
    route_dir = Path(args.route_dir).resolve()
    errors = []

    for name in REQUIRED_FILES:
        if not (route_dir / name).exists():
            errors.append(f"missing_file: {name}")

    record_path = route_dir / "ASTRA_TASK_RECORD.json"
    status_path = route_dir / "ROUTE_STATUS.json"
    if record_path.exists():
        record = json.loads(record_path.read_text(encoding="utf-8"))
        run_id = str(record.get("RUN_ID", ""))
        if not RUN_RE.fullmatch(run_id):
            errors.append(f"invalid_RUN_ID: {run_id}")
        if str(record.get("TASK_ROUTE_VERSION", "")).strip() == "":
            errors.append("missing_TASK_ROUTE_VERSION")
        if str(record.get("ASTRA_ROUTE_STATUS", "")) not in ALLOWED_ROUTE_STATUS:
            errors.append("invalid_ASTRA_ROUTE_STATUS")
    if status_path.exists():
        status = json.loads(status_path.read_text(encoding="utf-8"))
        if str(status.get("policy_hash_status", "")) != "POLICY_HASH_PENDING":
            errors.append("policy_hash_status_must_be_POLICY_HASH_PENDING_for_draft")

    verdict = "PASS_VALIDATE_ASTRA_ROUTE" if not errors else "FAIL_VALIDATE_ASTRA_ROUTE"
    report = {"route_dir": str(route_dir), "errors": errors, "verdict": verdict}
    if args.report_out:
        Path(args.report_out).write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
