#!/usr/bin/env python3
"""Write lightweight VM worker signal and update LATEST_SIGNAL.json."""

from __future__ import annotations

import argparse
import json
import socket
import sys
from datetime import datetime, timezone
from pathlib import Path

ALLOWED_PHASES = {
    "TASK_STARTED",
    "PHASE_STARTED",
    "PHASE_COMPLETED",
    "BLOCKED",
    "LIMIT_NEAR",
    "BUNDLE_READY",
    "HANDOFF_READY",
    "TASK_DONE",
}

ALLOWED_STATUS = {"IN_PROGRESS", "WAITING", "DONE", "BLOCKED", "HANDOFF"}


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def utc_compact() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")


def fail(msg: str) -> None:
    print(f"ERROR: {msg}", file=sys.stderr)
    raise SystemExit(2)


def build_payload(args: argparse.Namespace) -> dict:
    if args.phase not in ALLOWED_PHASES:
        fail(f"invalid phase={args.phase}")
    if args.status not in ALLOWED_STATUS:
        fail(f"invalid status={args.status}")

    payload = {
        "schema_version": "WORKER_TASK_SIGNAL_V1",
        "contour_id": args.contour_id,
        "host": socket.gethostname(),
        "user": args.user,
        "repo_path": args.repo_path,
        "task_id_or_step_name": args.task,
        "phase": args.phase,
        "status": args.status,
        "timestamp_utc": utc_now_iso(),
        "artifact_path": args.artifact_path,
        "bundle_path": args.bundle_path,
        "next_expected_action": args.next_expected_action,
        "safe_for_pc_read": True,
        "not_truth_center": True,
        "owner_attention_required": args.owner_attention_required,
        "limitation_notes": args.limitation_notes,
    }
    return payload


def write_signal(root: Path, contour_id: str, payload: dict) -> Path:
    signal_dir = root / "runtime" / "contours" / "signals" / contour_id.lower()
    signal_dir.mkdir(parents=True, exist_ok=True)
    phase = payload["phase"]
    out_path = signal_dir / f"{utc_compact()}_{phase}.json"
    latest_path = signal_dir / "LATEST_SIGNAL.json"

    out_path.write_text(json.dumps(payload, ensure_ascii=True, indent=2) + "\n", encoding="utf-8")
    latest_path.write_text(json.dumps(payload, ensure_ascii=True, indent=2) + "\n", encoding="utf-8")
    return out_path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Write worker signal.")
    parser.add_argument("--repo-root", required=True)
    parser.add_argument("--contour-id", default="VM3")
    parser.add_argument("--user", required=True)
    parser.add_argument("--repo-path", required=True)
    parser.add_argument("--task", required=True)
    parser.add_argument("--phase", required=True)
    parser.add_argument("--status", required=True)
    parser.add_argument("--artifact-path", default=None)
    parser.add_argument("--bundle-path", default=None)
    parser.add_argument("--next-expected-action", default=None)
    parser.add_argument("--owner-attention-required", action="store_true")
    parser.add_argument("--limitation-notes", default=None)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    root = Path(args.repo_root).resolve()
    schema_path = root / "OPERATIONS" / "contours" / "signals" / "WORKER_SIGNAL_SCHEMA_V1.json"
    if not schema_path.exists():
        fail(f"missing schema: {schema_path}")

    payload = build_payload(args)
    out_path = write_signal(root, args.contour_id, payload)
    print(json.dumps({"status": "ok", "signal_path": str(out_path)}, ensure_ascii=True))


if __name__ == "__main__":
    main()
