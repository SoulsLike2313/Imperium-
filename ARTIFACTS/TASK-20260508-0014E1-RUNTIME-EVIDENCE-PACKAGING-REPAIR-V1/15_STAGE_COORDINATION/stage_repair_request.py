#!/usr/bin/env python3
import argparse
import sys
import uuid
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR / "lib"))

from common_runtime import add_common_args, validate_identity, resolve_within_task_root, read_json, write_json, write_receipt, append_ledger_event, owner_report, now_utc

STEP = "TASK-20260508-0014E::stage_repair_request.py"
FATAL_MARKERS = [
    "task_id mismatch",
    "stage_id mismatch",
    "run_id mismatch",
    "conflicting hashes",
    "unknown producer",
    "fallback",
    "latest",
    "throne transfer",
    "destructive action",
]


def parse_args():
    p = argparse.ArgumentParser(description="Create repair request for recoverable errors only")
    add_common_args(p, include_receipt=True, receipt_required=False)
    p.add_argument("--failure-receipt", required=True)
    p.add_argument("--repair-out", required=True)
    p.add_argument("--repair-type", required=True)
    p.add_argument("--proposed-repair-stage-id", required=True)
    p.add_argument("--proposed-repair-run-id", required=True)
    p.add_argument("--ledger-path", required=True)
    return p.parse_args()


def main():
    args = parse_args()
    errors = validate_identity(args)
    if errors:
        write_receipt(args, status="FAIL", action="STAGE_REPAIR_REQUEST", failure_reason=";".join(errors), extra={"errors": errors})
        owner_report(STEP, "N/A", "FAIL", [
            "Repair request остановлен fail-closed.",
            "Identity невалиден.",
            "VM2/E2E/THRONE/watchers не использовались.",
            "Исправьте входные параметры.",
        ])
        return 1

    task_root = Path(args.task_root)
    failure_path = resolve_within_task_root(task_root, Path(args.failure_receipt), allow_nonexistent=False)
    repair_out = resolve_within_task_root(task_root, Path(args.repair_out))

    try:
        failure = read_json(failure_path)
    except Exception as exc:
        write_receipt(args, status="FAIL", action="STAGE_REPAIR_REQUEST", failure_reason=f"failure_receipt_parse_error:{exc}")
        return 1

    failure_reason = str(failure.get("failure_reason", ""))
    joined = (failure_reason + " " + str(failure)).lower()
    fatal = any(marker in joined for marker in FATAL_MARKERS)

    status = "PASS"
    recoverable = not fatal
    requires_owner = fatal

    repair = {
        "repair_id": f"REPAIR-{uuid.uuid4()}",
        "task_id": args.task_id,
        "stage_id": args.stage_id,
        "run_id": args.run_id,
        "contour_id": args.contour_id,
        "actor_id": args.actor_id,
        "tool_id": args.tool_id,
        "timestamp_utc": now_utc(),
        "original_failure_receipt_ref": failure_path.relative_to(task_root).as_posix(),
        "original_stage_id": failure.get("stage_id"),
        "original_run_id": failure.get("run_id"),
        "repair_type": args.repair_type,
        "recoverable": recoverable,
        "requires_owner": requires_owner,
        "proposed_repair_stage_id": args.proposed_repair_stage_id,
        "proposed_repair_run_id": args.proposed_repair_run_id,
    }

    if not recoverable:
        status = "OWNER_DECISION_REQUIRED"

    write_json(repair_out, repair)

    append_ledger_event(
        args,
        ledger_path=Path(args.ledger_path),
        event_type="REPAIR_REQUESTED",
        status=status,
        evidence_refs=[repair_out.relative_to(task_root).as_posix(), failure_path.relative_to(task_root).as_posix()],
        extra={"recoverable": recoverable, "requires_owner": requires_owner},
    )

    write_receipt(args, status=status, action="STAGE_REPAIR_REQUEST", failure_reason="fatal_error_cannot_auto_repair" if not recoverable else None, extra={"repair_ref": repair_out.relative_to(task_root).as_posix(), "recoverable": recoverable, "requires_owner": requires_owner})
    owner_report(STEP, "N/A", status, [
        "Repair request обработан локально.",
        f"Recoverable: {recoverable}; requires_owner: {requires_owner}.",
        "VM2/E2E/THRONE/watchers не использовались.",
        "Фатальные ошибки не маскируются repair-потоком.",
    ])
    return 0 if recoverable else 2


if __name__ == "__main__":
    raise SystemExit(main())
