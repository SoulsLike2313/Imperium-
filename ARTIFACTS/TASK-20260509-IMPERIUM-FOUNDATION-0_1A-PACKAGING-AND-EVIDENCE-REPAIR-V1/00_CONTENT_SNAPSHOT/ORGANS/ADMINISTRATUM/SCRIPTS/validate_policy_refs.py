#!/usr/bin/env python3
"""Validate that policy refs in launch card point to existing files."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Validate policy_refs existence in launch card.")
    p.add_argument("--launch-card", required=True)
    return p.parse_args()


def main() -> int:
    args = parse_args()
    card_path = Path(args.launch_card).resolve()
    if not card_path.exists():
        raise FileNotFoundError(f"Launch card not found: {card_path}")

    card = json.loads(card_path.read_text(encoding="utf-8"))
    refs = card.get("policy_refs")
    errors: list[str] = []

    if not isinstance(refs, list):
        errors.append("policy_refs must be list")
    else:
        for ref in refs:
            p = Path(str(ref))
            if not p.exists():
                errors.append(f"policy_ref_missing: {ref}")

    verdict = "PASS_VALIDATE_POLICY_REFS" if not errors else "FAIL_VALIDATE_POLICY_REFS"
    report = {"launch_card": str(card_path), "errors": errors, "verdict": verdict}
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())

