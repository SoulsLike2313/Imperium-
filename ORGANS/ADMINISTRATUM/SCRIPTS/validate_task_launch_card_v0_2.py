#!/usr/bin/env python3
"""Validate TASK_LAUNCH_CARD v0.2 with stage-id and policy checks."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Validate TASK_LAUNCH_CARD v0.2.")
    p.add_argument("--launch-card", required=True)
    p.add_argument("--stage-policy", default=r"E:\IMPERIUM\ORGANS\ADMINISTRATUM\POLICIES\STAGE_ID_POLICY.json")
    p.add_argument("--report-out", default="")
    return p.parse_args()


def main() -> int:
    args = parse_args()
    card_path = Path(args.launch_card).resolve()
    policy_path = Path(args.stage_policy).resolve()

    card = json.loads(card_path.read_text(encoding="utf-8"))
    stage_policy = json.loads(policy_path.read_text(encoding="utf-8"))
    stage_re = re.compile(str(stage_policy.get("canonical_regex", "")))
    errors = []

    required = [
        "task_id",
        "run_id",
        "stage_id",
        "read_first_refs",
        "policy_refs",
        "policy_hashes",
        "expected_outputs",
        "pass_criteria",
        "next_allowed_action_ref",
    ]
    for key in required:
        if key not in card:
            errors.append(f"missing_required_field: {key}")

    stage_id = str(card.get("stage_id", ""))
    if not stage_re.fullmatch(stage_id):
        errors.append(f"invalid_stage_id: {stage_id}")

    for row in card.get("policy_refs", []):
        p = row.get("path", "")
        if p and not Path(str(p)).exists():
            errors.append(f"policy_ref_missing: {p}")

    # DRAFT route may keep POLICY_HASH_PENDING, PASS receipts must not.
    hash_statuses = {str(x.get("status", "")) for x in card.get("policy_hashes", [])}
    if hash_statuses and hash_statuses == {"POLICY_HASH_PENDING"}:
        if card.get("astra_route_status") not in {"DRAFT", "OWNER_REVIEW"}:
            errors.append("POLICY_HASH_PENDING not allowed outside DRAFT/OWNER_REVIEW")

    verdict = "PASS_VALIDATE_TASK_LAUNCH_CARD_V0_2" if not errors else "FAIL_VALIDATE_TASK_LAUNCH_CARD_V0_2"
    report = {"launch_card": str(card_path), "stage_policy": str(policy_path), "errors": errors, "verdict": verdict}
    if args.report_out:
        Path(args.report_out).write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
