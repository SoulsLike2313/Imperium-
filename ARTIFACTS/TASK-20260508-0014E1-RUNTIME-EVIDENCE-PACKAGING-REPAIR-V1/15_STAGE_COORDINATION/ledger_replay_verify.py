#!/usr/bin/env python3
import argparse
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR / "lib"))

from common_runtime import (
    add_common_args,
    validate_identity,
    resolve_within_task_root,
    read_ledger_events,
    verify_event_hash,
    write_json,
    write_receipt,
    owner_report,
)

STEP = "TASK-20260508-0014E::ledger_replay_verify.py"


def parse_args():
    p = argparse.ArgumentParser(description="Replay and verify ledger hash chain")
    add_common_args(p, include_receipt=True, receipt_required=False)
    p.add_argument("--ledger-path", required=True)
    p.add_argument("--summary-out", required=False)
    return p.parse_args()


def main():
    args = parse_args()
    errors = validate_identity(args)
    if errors:
        write_receipt(args, status="FAIL", action="LEDGER_REPLAY_VERIFY", failure_reason=";".join(errors), extra={"errors": errors})
        owner_report(STEP, "N/A", "FAIL", [
            "Replay ledger остановлен fail-closed.",
            "Identity невалиден.",
            "VM2/E2E/THRONE/watchers не использовались.",
            "Исправьте identity и повторите.",
        ])
        return 1

    ledger_path = resolve_within_task_root(Path(args.task_root), Path(args.ledger_path), allow_nonexistent=False)
    events, parse_errors = read_ledger_events(ledger_path)

    seen_event_ids = set()
    chain_errors = []
    conflicts = []
    prev_hash = None
    evidence_map = {}

    for i, ev in enumerate(events, start=1):
        for k in ["event_id", "task_id", "stage_id", "run_id", "contour_id", "actor_id", "tool_id", "timestamp_utc", "event_type", "status", "previous_event_hash", "event_hash"]:
            if k not in ev:
                chain_errors.append(f"missing_field_line_{i}:{k}")

        eid = ev.get("event_id")
        if eid in seen_event_ids:
            chain_errors.append(f"duplicate_event_id:{eid}")
        seen_event_ids.add(eid)

        if not verify_event_hash(ev):
            chain_errors.append(f"event_hash_mismatch:{eid}")

        if ev.get("previous_event_hash") != prev_hash:
            chain_errors.append(f"previous_event_hash_mismatch:{eid}")
        prev_hash = ev.get("event_hash")

        art_ref = ev.get("artifact_ref")
        art_sha = ev.get("artifact_sha256")
        if art_ref and art_sha:
            key = (ev.get("task_id"), ev.get("stage_id"), ev.get("run_id"), ev.get("contour_id"), art_ref)
            old = evidence_map.get(key)
            if old and old != art_sha:
                conflicts.append(f"same_identity_different_hash:{art_ref}")
            evidence_map[key] = art_sha

    status = "PASS"
    if conflicts:
        status = "CONFLICT"
    elif parse_errors or chain_errors:
        status = "FAIL"

    summary = {
        "task_id": args.task_id,
        "stage_id": args.stage_id,
        "run_id": args.run_id,
        "contour_id": args.contour_id,
        "status": status,
        "events_count": len(events),
        "parse_errors": parse_errors,
        "chain_errors": chain_errors,
        "conflicts": conflicts,
    }

    if args.summary_out:
        out = resolve_within_task_root(Path(args.task_root), Path(args.summary_out))
        write_json(out, summary)

    write_receipt(args, status=status, action="LEDGER_REPLAY_VERIFY", failure_reason=";".join(parse_errors + chain_errors + conflicts) if status != "PASS" else None, extra=summary)
    owner_report(STEP, "N/A", status, [
        "Replay ledger выполнен локально.",
        f"Результат: {status}.",
        "VM2/E2E/THRONE/watchers не использовались.",
        "Hash-chain и конфликты проверены.",
    ])
    return 0 if status == "PASS" else (2 if status == "CONFLICT" else 1)


if __name__ == "__main__":
    raise SystemExit(main())
