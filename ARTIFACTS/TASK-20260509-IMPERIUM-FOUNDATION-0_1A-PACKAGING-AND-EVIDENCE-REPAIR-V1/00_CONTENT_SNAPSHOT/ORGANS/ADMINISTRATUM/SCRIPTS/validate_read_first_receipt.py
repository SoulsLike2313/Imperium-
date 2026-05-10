#!/usr/bin/env python3
"""Validate read-first receipt scaffold fields (0.1)."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parent
ADMIN_ROOT = SCRIPT_DIR.parent
DEFAULT_STAGE_POLICY = ADMIN_ROOT / "POLICIES" / "STAGE_ID_POLICY.json"


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Validate read-first receipt required fields.")
    p.add_argument("--receipt", required=True)
    p.add_argument("--stage-policy", default=str(DEFAULT_STAGE_POLICY))
    return p.parse_args()


def main() -> int:
    args = parse_args()
    receipt_path = Path(args.receipt).resolve()
    stage_policy_path = Path(args.stage_policy).resolve()

    if not receipt_path.exists():
        raise FileNotFoundError(f"Receipt not found: {receipt_path}")
    if not stage_policy_path.exists():
        raise FileNotFoundError(f"Stage policy not found: {stage_policy_path}")

    obj = json.loads(receipt_path.read_text(encoding="utf-8"))
    stage_policy = json.loads(stage_policy_path.read_text(encoding="utf-8"))
    stage_regex = str(stage_policy.get("canonical_regex", "")).strip()

    errors: list[str] = []
    for field in ["task_id", "stage_id", "run_id", "read_files", "policy_hashes"]:
        if field not in obj:
            errors.append(f"missing_required_field: {field}")

    if "read_files" in obj and not isinstance(obj["read_files"], list):
        errors.append("read_files must be list")
    if "policy_hashes" in obj and not isinstance(obj["policy_hashes"], dict):
        errors.append("policy_hashes must be dict")

    if stage_regex and not re.fullmatch(stage_regex, str(obj.get("stage_id", ""))):
        errors.append(f"invalid_stage_id_by_policy: {obj.get('stage_id')}")

    verdict = "PASS_VALIDATE_READ_FIRST_RECEIPT" if not errors else "FAIL_VALIDATE_READ_FIRST_RECEIPT"
    report = {"receipt": str(receipt_path), "errors": errors, "verdict": verdict}
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())

