#!/usr/bin/env python3
from __future__ import annotations

import argparse
import datetime as dt
import json
import subprocess
import sys
from pathlib import Path
from typing import Any

REQUIRED_REPORT_FIELDS = [
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

ALLOWED_ACK_DECISIONS = {
    "CONTINUE_ALLOWED",
    "STOP_OWNER_REQUIRED",
    "BLOCKED",
    "NEEDS_REVIEW",
    "ACK_RECORDED_NO_CONTINUATION",
}


def now_utc() -> str:
    return dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def run_git(repo_root: Path, args: list[str]) -> str:
    result = subprocess.run(
        ["git", *args],
        cwd=str(repo_root),
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode != 0:
        raise RuntimeError((result.stderr or result.stdout).strip())
    return result.stdout.strip()


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

    for field in REQUIRED_REPORT_FIELDS:
        if field in payload:
            passes.append(f"field_present:{field}")
        else:
            blocked.append(f"missing_field:{field}")

    if payload.get("schema_version") == "imperium.stage_progress_report.v0_1":
        passes.append("report_schema_version_ok")
    else:
        blocked.append("report_schema_version_must_be:imperium.stage_progress_report.v0_1")

    text_blob = json.dumps(payload, ensure_ascii=False).lower()
    if "ready_for_agent true" in text_blob:
        blocked.append("report_contains_ready_for_agent_true_claim")

    if "continue_allowed" in text_blob:
        warns.append("report_contains_continue_allowed_token_verify_context")

    return passes, warns, blocked


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Create Administratum ACK skeleton from stage progress report v0.1. "
            "Default decision is NEEDS_REVIEW."
        )
    )
    parser.add_argument("--input", type=Path, help="Stage progress report JSON path.")
    parser.add_argument("--out", type=Path, help="Output ACK JSON path.")
    parser.add_argument("--decision", choices=sorted(ALLOWED_ACK_DECISIONS), default="NEEDS_REVIEW")
    parser.add_argument("--decision-reason", default="Skeleton ACK requires explicit review before continuation.")
    parser.add_argument("--required-next-action", default="REQUEST_REVIEW")
    parser.add_argument("--allowed-next-stage", action="append", default=[])
    parser.add_argument("--issued-by", default="ADMINISTRATUM_V0_1_SKELETON")
    parser.add_argument("--allow-continue", action="store_true", help="Required to emit CONTINUE_ALLOWED.")
    parser.add_argument("--example", action="store_true", help="Print usage example.")
    return parser.parse_args()


def print_example() -> None:
    print("Example:")
    print(
        "  python3 TOOLS/administratum_ack_stage_progress_v0_1.py "
        "--input ORGANS/ADMINISTRATUM/REGISTRY/STAGE_PROGRESS_REPORTS/EXAMPLES/"
        "STAGE_PROGRESS_REPORT_EXAMPLE_V0_1.json"
    )
    print(
        "  python3 TOOLS/administratum_ack_stage_progress_v0_1.py "
        "--input <report.json> --out ORGANS/ADMINISTRATUM/REGISTRY/ACKS/<ack_id>.json"
    )
    print("Note: default decision is NEEDS_REVIEW; no READY_FOR_AGENT approval is ever created.")


def main() -> int:
    args = parse_args()

    if args.example:
        print_example()
        return 0

    if args.input is None:
        print("PASS: no --input provided; nothing written (safe skeleton behavior).")
        print("WARN: provide --input and --out to generate ACK skeleton.")
        return 0

    if not args.input.exists():
        print(f"BLOCKED: missing_input_file:{args.input}")
        return 2

    try:
        report = load_json(args.input)
    except ValueError as exc:
        print(f"BLOCKED: {exc}")
        return 2

    passes, warns, blocked = validate_report(report)

    decision = args.decision
    if decision == "CONTINUE_ALLOWED" and not args.allow_continue:
        blocked.append("continue_allowed_requires_explicit_flag:--allow-continue")

    if decision == "CONTINUE_ALLOWED" and not args.allowed_next_stage:
        blocked.append("continue_allowed_requires_at_least_one_allowed_next_stage")

    if decision == "CONTINUE_ALLOWED" and args.required_next_action == "REQUEST_OWNER_DECISION":
        warns.append("continue_allowed_with_owner_decision_requested_verify_policy")

    if decision != "CONTINUE_ALLOWED" and args.allow_continue:
        warns.append("--allow-continue_ignored_because_decision_is_not_continue_allowed")

    if "ready_for_agent" in args.decision_reason.lower():
        blocked.append("decision_reason_must_not_claim_ready_for_agent")

    repo_root = Path.cwd()
    try:
        head = run_git(repo_root, ["rev-parse", "HEAD"])
        commit_count = int(run_git(repo_root, ["rev-list", "--count", "HEAD"]))
        latest_subject = run_git(repo_root, ["log", "-1", "--pretty=%s"])
    except Exception as exc:  # noqa: BLE001
        blocked.append(f"git_truth_unavailable:{type(exc).__name__}:{exc}")
        head = "UNKNOWN"
        commit_count = -1
        latest_subject = "UNKNOWN"

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

    if args.out is None:
        print("WARN: validation-only mode (no write, because --out not provided).")
        print("PASS: continuation remains governed by explicit ACK + Owner boundaries.")
        return 0

    if args.out.resolve() == args.input.resolve():
        print("BLOCKED: --out must be different from --input")
        return 2

    ack_id = f"ADMIN-ACK-{report.get('report_id', 'UNKNOWN')}"
    ack_payload = {
        "schema_version": "imperium.administratum_ack.v0_1",
        "ack_id": ack_id,
        "work_session_id": report.get("work_session_id"),
        "report_id": report.get("report_id"),
        "issued_at_utc": now_utc(),
        "issued_by": args.issued_by,
        "repo_truth_at_ack": {
            "head": head,
            "commit_count": commit_count,
            "latest_commit_subject": latest_subject,
        },
        "decision": decision,
        "decision_reason": args.decision_reason,
        "evidence_checked": list(report.get("evidence_paths", [])),
        "required_next_action": args.required_next_action,
        "allowed_next_stage_ids": args.allowed_next_stage,
        "forbidden_actions": [
            "Do not set READY_FOR_AGENT true",
            "Do not claim Owner approval from ACK",
            "Do not claim Act 5 execution ready",
        ],
        "owner_required": decision in {"STOP_OWNER_REQUIRED", "NEEDS_REVIEW", "BLOCKED"},
        "receipt_path": ".imperium_runtime/administratum/work_session_ack_flow/ACK_RECEIPT_PENDING.json",
        "no_fake_green_statement": (
            "Administratum ACK grants only continuity routing decision and never upgrades "
            "READY_FOR_AGENT or Act 5 execution readiness."
        ),
    }

    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(ack_payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"PASS: wrote_ack_skeleton:{args.out}")
    print("PASS: READY_FOR_AGENT approval was not created.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
