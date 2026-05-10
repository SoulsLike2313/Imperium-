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
    has_latest_pattern,
    resolve_within_task_root,
    canonical_json_bytes,
    sha256_bytes,
    identity_block,
    write_json,
    write_receipt,
    append_ledger_event,
    owner_report,
)

STEP = "TASK-20260508-0014E::stage_signal_emit.py"
SIGNAL_TYPES = {
    "STAGE_READY", "STAGE_STARTED", "STAGE_PROGRESS", "STAGE_COMPLETED", "STAGE_FAILED", "STAGE_BLOCKED",
    "READY_FOR_NEXT", "REPAIR_REQUIRED", "REPAIR_VERIFIED", "OWNER_DECISION_REQUIRED"
}
COMPLETION_TYPES = {"STAGE_COMPLETED", "READY_FOR_NEXT"}


def parse_args():
    p = argparse.ArgumentParser(description="Emit stage signal and append ledger event")
    add_common_args(p, include_receipt=True, receipt_required=False)
    p.add_argument("--signal-type", required=True)
    p.add_argument("--status", required=False, default="INFO")
    p.add_argument("--signal-out", required=True)
    p.add_argument("--ledger-path", required=True)
    p.add_argument("--receipt-ref", required=False)
    p.add_argument("--artifact-manifest-ref", required=False)
    p.add_argument("--provenance-ref", required=False)
    return p.parse_args()


def main():
    args = parse_args()
    errors = validate_identity(args)
    if args.signal_type not in SIGNAL_TYPES:
        errors.append("invalid_signal_type")
    for p in [args.signal_out, args.ledger_path, args.receipt_ref or "", args.artifact_manifest_ref or "", args.provenance_ref or ""]:
        if p and has_latest_pattern(p):
            errors.append("latest_pattern_path")

    if args.signal_type in COMPLETION_TYPES and not args.receipt_ref:
        errors.append("completion_signal_requires_receipt_ref")

    if errors:
        write_receipt(args, status="FAIL", action="STAGE_SIGNAL_EMIT", failure_reason=";".join(errors), extra={"errors": errors})
        owner_report(STEP, "N/A", "FAIL", [
            "Emit signal остановлен fail-closed.",
            "Нарушены входные требования или completion-политика.",
            "VM2/E2E/THRONE/watchers не использовались.",
            "Исправьте параметры и повторите.",
        ])
        return 1

    task_root = Path(args.task_root)
    signal_out = resolve_within_task_root(task_root, Path(args.signal_out))
    _ = resolve_within_task_root(task_root, Path(args.ledger_path))

    if args.receipt_ref:
        rr = resolve_within_task_root(task_root, Path(args.receipt_ref), allow_nonexistent=False)
        if not rr.exists():
            write_receipt(args, status="FAIL", action="STAGE_SIGNAL_EMIT", failure_reason="receipt_ref_missing")
            return 1

    signal = {
        "signal_id": f"SIG-{uuid.uuid4()}",
        **identity_block(args),
        "signal_type": args.signal_type,
        "status": args.status,
        "receipt_ref": args.receipt_ref,
        "artifact_manifest_ref": args.artifact_manifest_ref,
        "provenance_ref": args.provenance_ref,
    }
    probe = dict(signal)
    signal["signal_hash"] = sha256_bytes(canonical_json_bytes(probe))

    write_json(signal_out, signal)

    append_ledger_event(
        args,
        ledger_path=Path(args.ledger_path),
        event_type="STAGE_SIGNAL_EMITTED",
        status=args.status,
        evidence_refs=[signal_out.relative_to(task_root).as_posix()],
        extra={"signal_id": signal["signal_id"], "signal_type": args.signal_type},
    )

    write_receipt(args, status="PASS", action="STAGE_SIGNAL_EMIT", extra={
        "signal_ref": signal_out.relative_to(task_root).as_posix(),
        "signal_type": args.signal_type,
        "signal_id": signal["signal_id"],
    })
    owner_report(STEP, "N/A", "PASS", [
        "Signal записан локально и связан с ledger.",
        "Completion-сигнал требует receipt_ref и это проверено.",
        "VM2/E2E/THRONE/watchers не использовались.",
        "Можно переходить к ACK/verify.",
    ])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
