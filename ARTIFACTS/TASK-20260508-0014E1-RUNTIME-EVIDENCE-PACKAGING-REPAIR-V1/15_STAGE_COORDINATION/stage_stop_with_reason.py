#!/usr/bin/env python3
import argparse
import sys
import uuid
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR / "lib"))

from common_runtime import (
    add_common_args,
    validate_identity,
    resolve_within_task_root,
    identity_block,
    canonical_json_bytes,
    sha256_bytes,
    write_json,
    write_receipt,
    append_ledger_event,
    owner_report,
)

STEP = "TASK-20260508-0014E::stage_stop_with_reason.py"


def parse_args():
    p = argparse.ArgumentParser(description="Stop stage/task with explicit reason")
    add_common_args(p, include_receipt=True, receipt_required=False)
    p.add_argument("--stop-out", required=True)
    p.add_argument("--ledger-path", required=True)
    p.add_argument("--stop-type", required=True)
    p.add_argument("--status", required=True)
    p.add_argument("--reason", required=True)
    p.add_argument("--next-allowed-action", required=True)
    p.add_argument("--evidence-ref", action="append", default=[])
    p.add_argument("--signal-out", required=False)
    return p.parse_args()


def main():
    args = parse_args()
    errors = validate_identity(args)
    if errors:
        write_receipt(args, status="FAIL", action="STAGE_STOP_WITH_REASON", failure_reason=";".join(errors), extra={"errors": errors})
        owner_report(STEP, "N/A", "FAIL", [
            "Stop-with-reason остановлен fail-closed.",
            "Identity невалиден.",
            "VM2/E2E/THRONE/watchers не использовались.",
            "Исправьте параметры.",
        ])
        return 1

    task_root = Path(args.task_root)
    stop_out = resolve_within_task_root(task_root, Path(args.stop_out))

    payload = {
        "stop_id": f"STOP-{uuid.uuid4()}",
        **identity_block(args),
        "stop_type": args.stop_type,
        "status": args.status,
        "human_readable_reason": args.reason,
        "evidence_refs": args.evidence_ref,
        "next_allowed_action": args.next_allowed_action,
    }
    write_json(stop_out, payload)

    signal_ref = None
    if args.signal_out:
        signal_out = resolve_within_task_root(task_root, Path(args.signal_out))
        signal = {
            "signal_id": f"SIG-{uuid.uuid4()}",
            **identity_block(args),
            "signal_type": "STAGE_BLOCKED" if "BLOCK" in args.stop_type else "STAGE_FAILED",
            "status": args.status,
            "receipt_ref": str(Path(args.receipt_out).as_posix()) if args.receipt_out else None,
            "artifact_manifest_ref": None,
            "provenance_ref": None,
        }
        probe = dict(signal)
        signal["signal_hash"] = sha256_bytes(canonical_json_bytes(probe))
        write_json(signal_out, signal)
        signal_ref = signal_out.relative_to(task_root).as_posix()

    append_ledger_event(
        args,
        ledger_path=Path(args.ledger_path),
        event_type="STAGE_STOPPED",
        status=args.status,
        evidence_refs=[stop_out.relative_to(task_root).as_posix()] + ([signal_ref] if signal_ref else []),
        extra={"stop_type": args.stop_type},
    )

    write_receipt(args, status=args.status, action="STAGE_STOP_WITH_REASON", failure_reason=args.reason, extra={
        "stop_ref": stop_out.relative_to(task_root).as_posix(),
        "signal_ref": signal_ref,
    })
    owner_report(STEP, "N/A", args.status, [
        "Stage остановлен с явной причиной и evidence.",
        "STOP receipt и ledger event записаны локально.",
        "VM2/E2E/THRONE/watchers не использовались.",
        "Дальнейшее действие ограничено next_allowed_action.",
    ])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
