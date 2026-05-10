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
    load_signal_and_verify,
    canonical_json_bytes,
    sha256_bytes,
    identity_block,
    write_json,
    write_receipt,
    append_ledger_event,
    owner_report,
)

STEP = "TASK-20260508-0014E::stage_signal_ack.py"


def parse_args():
    p = argparse.ArgumentParser(description="Acknowledge stage signal")
    add_common_args(p, include_receipt=True, receipt_required=False)
    p.add_argument("--signal-path", required=True)
    p.add_argument("--ack-out", required=True)
    p.add_argument("--ledger-path", required=True)
    p.add_argument("--ack-status", required=False, default="ACKED")
    return p.parse_args()


def main():
    args = parse_args()
    errors = validate_identity(args)
    for p in [args.signal_path, args.ack_out, args.ledger_path]:
        if has_latest_pattern(p):
            errors.append("latest_pattern_path")
    if errors:
        write_receipt(args, status="FAIL", action="STAGE_SIGNAL_ACK", failure_reason=";".join(errors), extra={"errors": errors})
        owner_report(STEP, "N/A", "FAIL", [
            "ACK остановлен fail-closed.",
            "Identity или path-политика нарушены.",
            "VM2/E2E/THRONE/watchers не использовались.",
            "Исправьте входные данные.",
        ])
        return 1

    task_root = Path(args.task_root)
    signal_path = resolve_within_task_root(task_root, Path(args.signal_path), allow_nonexistent=False)
    ack_out = resolve_within_task_root(task_root, Path(args.ack_out))

    try:
        signal = load_signal_and_verify(signal_path)
    except Exception as exc:
        write_receipt(args, status="CONFLICT", action="STAGE_SIGNAL_ACK", failure_reason=f"signal_invalid:{exc}")
        owner_report(STEP, "N/A", "CONFLICT", [
            "ACK не создан: source signal отсутствует или невалиден.",
            str(exc),
            "VM2/E2E/THRONE/watchers не использовались.",
            "Требуется восстановление корректного signal.",
        ])
        return 2

    for k in ["task_id", "stage_id", "run_id"]:
        if signal.get(k) != getattr(args, k):
            write_receipt(args, status="FAIL", action="STAGE_SIGNAL_ACK", failure_reason=f"identity_mismatch:{k}")
            return 1

    ack = {
        "ack_id": f"ACK-{uuid.uuid4()}",
        "ack_for_signal_id": signal.get("signal_id"),
        **identity_block(args),
        "ack_by_contour_id": args.contour_id,
        "ack_status": args.ack_status,
        "signal_hash_seen": signal.get("signal_hash"),
    }
    probe = dict(ack)
    ack["ack_hash"] = sha256_bytes(canonical_json_bytes(probe))
    write_json(ack_out, ack)

    append_ledger_event(
        args,
        ledger_path=Path(args.ledger_path),
        event_type="STAGE_SIGNAL_ACKED",
        status=args.ack_status,
        evidence_refs=[ack_out.relative_to(task_root).as_posix(), signal_path.relative_to(task_root).as_posix()],
        extra={"ack_id": ack["ack_id"], "signal_id": signal.get("signal_id")},
    )

    write_receipt(args, status="PASS", action="STAGE_SIGNAL_ACK", extra={
        "ack_ref": ack_out.relative_to(task_root).as_posix(),
        "ack_id": ack["ack_id"],
        "signal_id": signal.get("signal_id"),
    })
    owner_report(STEP, "N/A", "PASS", [
        "ACK создан и связан с конкретным signal.",
        "Хэш signal зафиксирован в ACK.",
        "VM2/E2E/THRONE/watchers не использовались.",
        "Можно выполнять signal verify.",
    ])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
