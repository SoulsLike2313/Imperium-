#!/usr/bin/env python3
"""Validate TASK_LAUNCH_CARD scaffold requirements (0.1)."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parent
ADMIN_ROOT = SCRIPT_DIR.parent
DEFAULT_STAGE_POLICY = ADMIN_ROOT / "POLICIES" / "STAGE_ID_POLICY.json"

REQUIRED_FIELDS = [
    "task_id",
    "stage_id",
    "run_id",
    "read_first_refs",
    "policy_refs",
    "canonical_answer_refs",
    "allowed_tool_refs",
    "expected_outputs",
    "pass_criteria",
    "partial_fail_behavior",
    "next_allowed_action_ref",
]


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Validate TASK_LAUNCH_CARD required fields and refs.")
    p.add_argument("--launch-card", required=True)
    p.add_argument("--stage-policy", default=str(DEFAULT_STAGE_POLICY))
    p.add_argument("--report-out", default="")
    return p.parse_args()


def _check_policy_refs(card: dict, errors: list[str]) -> None:
    refs = card.get("policy_refs")
    if not isinstance(refs, list):
        errors.append("policy_refs must be list")
        return
    for ref in refs:
        try:
            p = Path(str(ref))
            if not p.exists():
                errors.append(f"policy_ref_missing: {ref}")
        except Exception:
            errors.append(f"policy_ref_invalid: {ref}")


def _check_output_roots(card: dict, errors: list[str]) -> None:
    if "output_root" in card:
        p = Path(str(card["output_root"]))
        if not p.exists() and not p.parent.exists():
            errors.append(f"output_root_missing_and_parent_missing: {p}")

    expected = card.get("expected_outputs")
    if isinstance(expected, list):
        for item in expected:
            if isinstance(item, dict) and "output_path" in item:
                p = Path(str(item["output_path"]))
                if not p.exists() and not p.parent.exists():
                    errors.append(f"expected_output_parent_missing: {p}")


def main() -> int:
    args = parse_args()
    card_path = Path(args.launch_card).resolve()
    stage_policy_path = Path(args.stage_policy).resolve()

    errors: list[str] = []
    if not card_path.exists():
        raise FileNotFoundError(f"Launch card not found: {card_path}")
    if not stage_policy_path.exists():
        raise FileNotFoundError(f"Stage policy not found: {stage_policy_path}")

    card = json.loads(card_path.read_text(encoding="utf-8"))
    stage_policy = json.loads(stage_policy_path.read_text(encoding="utf-8"))
    stage_regex = str(stage_policy.get("canonical_regex", "")).strip()
    if not stage_regex:
        errors.append("stage_policy.canonical_regex missing")

    for field in REQUIRED_FIELDS:
        value = card.get(field)
        if value is None or (isinstance(value, str) and not value.strip()):
            errors.append(f"missing_required_field: {field}")

    stage_id = str(card.get("stage_id", ""))
    if stage_regex and not re.fullmatch(stage_regex, stage_id):
        errors.append(f"invalid_stage_id_by_policy: {stage_id}")

    _check_policy_refs(card, errors)
    _check_output_roots(card, errors)

    verdict = "PASS_VALIDATE_TASK_LAUNCH_CARD" if not errors else "FAIL_VALIDATE_TASK_LAUNCH_CARD"
    report = {
        "launch_card": str(card_path),
        "stage_policy": str(stage_policy_path),
        "errors": errors,
        "verdict": verdict,
    }
    if args.report_out:
        Path(args.report_out).write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())

