#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import shutil
import sys
from pathlib import Path
from typing import Any

REQUIRED_FIELDS = [
    "schema_version",
    "report_id",
    "work_session_id",
    "task_id",
    "stage_id",
    "submitted_at_utc",
    "submitted_by",
    "repo_truth_at_submission",
    "completed_actions",
    "changed_files",
    "generated_receipts",
    "checks_run",
    "checker_verdicts",
    "blockers",
    "warnings",
    "next_requested_action",
    "servitor_claim",
    "evidence_paths",
    "no_fake_green_statement",
]

ALLOWED_NEXT_REQUESTED_ACTIONS = {
    "REQUEST_CONTINUE",
    "REQUEST_OWNER_DECISION",
    "REQUEST_REVIEW",
    "REQUEST_STOP",
}

FORBIDDEN_CONTINUATION_KEYS = {
    "continuation_allowed",
    "continue_allowed",
    "ready_for_agent",
    "ready_for_agent_status",
    "owner_approval",
}


def load_json(path: Path) -> dict[str, Any]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:  # noqa: BLE001
        raise ValueError(f"invalid_json:{path}:{type(exc).__name__}:{exc}") from exc
    if not isinstance(payload, dict):
        raise ValueError(f"invalid_json_type:{path}:expected_object")
    return payload


def validate_report(payload: dict[str, Any]) -> tuple[list[str], list[str], list[str]]:
    passes: list[str] = []
    warns: list[str] = []
    blocked: list[str] = []

    for field in REQUIRED_FIELDS:
        if field in payload:
            passes.append(f"field_present:{field}")
        else:
            blocked.append(f"missing_field:{field}")

    if payload.get("schema_version") == "imperium.stage_progress_report.v0_1":
        passes.append("schema_version_ok")
    else:
        blocked.append("schema_version_must_be:imperium.stage_progress_report.v0_1")

    next_action = payload.get("next_requested_action")
    if isinstance(next_action, str) and next_action in ALLOWED_NEXT_REQUESTED_ACTIONS:
        passes.append("next_requested_action_ok")
    else:
        blocked.append("next_requested_action_invalid")

    for key in FORBIDDEN_CONTINUATION_KEYS:
        if key in payload:
            value = payload.get(key)
            if isinstance(value, bool) and value:
                blocked.append(f"forbidden_self_authorization:{key}=true")
            elif isinstance(value, str) and "true" in value.lower():
                blocked.append(f"forbidden_self_authorization:{key}=true_text")
            else:
                warns.append(f"unexpected_field_present:{key}")

    serialized = json.dumps(payload, ensure_ascii=False).lower()
    if "continue_allowed" in serialized or "ready_for_agent true" in serialized:
        blocked.append("report_must_not_claim_continuation_or_ready_for_agent")

    no_fake = str(payload.get("no_fake_green_statement", "")).strip()
    if no_fake:
        passes.append("no_fake_green_statement_present")
    else:
        warns.append("no_fake_green_statement_empty")

    if payload.get("example_only") is True:
        warns.append("example_only_record_detected")

    return passes, warns, blocked


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Validate/register stage progress report v0.1. "
            "This tool never authorizes continuation."
        )
    )
    parser.add_argument("--input", type=Path, help="Path to stage progress report JSON.")
    parser.add_argument("--out", type=Path, help="Optional output path for validated copy.")
    parser.add_argument("--example", action="store_true", help="Print usage example.")
    return parser.parse_args()


def print_example() -> None:
    print("Example:")
    print(
        "  python3 TOOLS/register_stage_progress_report_v0_1.py "
        "--input ORGANS/ADMINISTRATUM/REGISTRY/STAGE_PROGRESS_REPORTS/EXAMPLES/"
        "STAGE_PROGRESS_REPORT_EXAMPLE_V0_1.json"
    )
    print(
        "  python3 TOOLS/register_stage_progress_report_v0_1.py "
        "--input <report.json> --out ORGANS/ADMINISTRATUM/REGISTRY/STAGE_PROGRESS_REPORTS/<id>.json"
    )
    print("Note: continuation permission is never issued by this tool.")


def main() -> int:
    args = parse_args()

    if args.example:
        print_example()
        return 0

    if args.input is None:
        print("PASS: no --input provided; nothing written (safe skeleton behavior).")
        print("WARN: provide --input to validate a report.")
        return 0

    if not args.input.exists():
        print(f"BLOCKED: missing_input_file:{args.input}")
        return 2

    try:
        payload = load_json(args.input)
    except ValueError as exc:
        print(f"BLOCKED: {exc}")
        return 2

    passes, warns, blocked = validate_report(payload)

    print("PASS:")
    for item in passes:
        print(f"- {item}")

    print("WARN:")
    for item in warns:
        print(f"- {item}")

    print("BLOCKED:")
    for item in blocked:
        print(f"- {item}")

    if blocked:
        return 2

    if args.out is not None:
        if args.out.resolve() == args.input.resolve():
            print("BLOCKED: --out must be different from --input")
            return 2
        args.out.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(args.input, args.out)
        print(f"PASS: wrote_validated_report_copy:{args.out}")
    else:
        print("WARN: validation-only mode (no write, because --out not provided).")

    print("PASS: continuation remains disallowed without Administratum ACK.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
