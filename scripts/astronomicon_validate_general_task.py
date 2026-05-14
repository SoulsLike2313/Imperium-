#!/usr/bin/env python3
"""Validate Astronomicon General Task markdown format and required fields."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from astronomicon_general_task_lib import parse_markdown_general_task, validate_parsed_general_task


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Validate Astronomicon General Task markdown against MVP field contract."
    )
    parser.add_argument("input_path", help="Path to General Task markdown file")
    parser.add_argument("--quiet", action="store_true", help="Print concise output")
    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    input_path = Path(args.input_path)

    if not input_path.exists():
        print(f"FAIL: input file not found: {input_path}")
        return 2

    try:
        parsed = parse_markdown_general_task(input_path)
    except Exception as exc:
        print(f"FAIL: BLOCKED_GENERAL_TASK_PARSE_FAILED: {exc}")
        return 2

    errors = validate_parsed_general_task(parsed)
    payload = {
        "validation_status": "PASS" if not errors else "FAIL",
        "input_path": str(input_path.resolve()),
        "error_count": len(errors),
        "errors": errors,
    }

    if not args.quiet:
        print(json.dumps(payload, ensure_ascii=False, indent=2))

    if errors:
        print("FAIL: BLOCKED_GENERAL_TASK_FORMAT_INVALID")
        return 1

    print("PASS: GENERAL_TASK_VALID")
    return 0


if __name__ == "__main__":
    sys.exit(main())
