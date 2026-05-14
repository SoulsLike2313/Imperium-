#!/usr/bin/env python3
"""Parse YAML-frontmatter + Markdown General Task into normalized JSON."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from astronomicon_general_task_lib import parse_markdown_general_task, write_json


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Parse Astronomicon General Task markdown (YAML frontmatter + body)."
    )
    parser.add_argument("input_path", help="Path to General Task markdown file")
    parser.add_argument(
        "--out",
        dest="out_path",
        help="Optional output JSON file path (allowed: Astronomicon/tests fixtures/external runtime)",
    )
    parser.add_argument("--pretty", action="store_true", help="Pretty-print JSON to stdout")
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
        print(
            json.dumps(
                {
                    "parse_status": "BLOCKED_GENERAL_TASK_PARSE_FAILED",
                    "input_path": str(input_path),
                    "error": str(exc),
                },
                ensure_ascii=False,
                indent=2,
            )
        )
        return 2

    if args.out_path:
        out_path = Path(args.out_path)
        try:
            write_json(out_path, parsed)
        except Exception as exc:
            print(f"FAIL: cannot write output JSON: {exc}")
            return 3

    if args.pretty:
        print(json.dumps(parsed, ensure_ascii=False, indent=2))
    else:
        print(json.dumps(parsed, ensure_ascii=False))

    print("PASS: GENERAL_TASK_PARSED")
    return 0


if __name__ == "__main__":
    sys.exit(main())
