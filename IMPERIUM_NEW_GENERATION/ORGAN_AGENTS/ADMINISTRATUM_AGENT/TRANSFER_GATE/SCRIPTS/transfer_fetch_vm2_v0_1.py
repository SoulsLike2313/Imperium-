#!/usr/bin/env python3
"""Fetch and verify a VM2 response bundle by exact expected filename."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from transfer_gate_core_v0_1 import DEFAULT_TRANSFER_ROOT, fetch_vm2_response_bundle


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Fetch a VM2 response bundle from the transfer outbox.")
    parser.add_argument("--task-id", required=True)
    parser.add_argument("--expected-filename", default=None)
    parser.add_argument("--correlation-id", default=None)
    parser.add_argument("--runtime-root", default=str(DEFAULT_TRANSFER_ROOT))
    parser.add_argument("--no-quarantine", action="store_true")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    result = fetch_vm2_response_bundle(
        task_id=args.task_id,
        expected_filename=args.expected_filename,
        correlation_id=args.correlation_id,
        runtime_root=Path(args.runtime_root),
        quarantine_on_mismatch=not args.no_quarantine,
    )
    print(json.dumps(result, indent=2, ensure_ascii=False))
    return 0 if not str(result.get("verdict", "")).startswith("BLOCKED") else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
