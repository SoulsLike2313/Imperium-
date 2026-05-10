#!/usr/bin/env python3
import argparse
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR / "lib"))

from common_runtime import (
    add_common_args,
    validate_identity,
    has_latest_pattern,
    resolve_within_task_root,
    load_signal_and_verify,
    read_json,
    write_json,
    write_receipt,
    owner_report,
)

STEP = "TASK-20260508-0014E::stage_signal_verify.py"
COMPLETION_TYPES = {"STAGE_COMPLETED", "READY_FOR_NEXT"}


def parse_args():
    p = argparse.ArgumentParser(description="Verify signal and optional ACK pair")
    add_common_args(p, include_receipt=True, receipt_required=False)
    p.add_argument("--signal-path", required=True)
    p.add_argument("--ack-path", required=False)
    p.add_argument("--require-ack", action="store_true")
    p.add_argument("--verify-out", required=False)
    return p.parse_args()


def main():
    args = parse_args()
    errors = validate_identity(args)
    for p in [args.signal_path, args.ack_path or ""]:
        if p and has_latest_pattern(p):
            errors.append("latest_pattern_path")
    if errors:
        write_receipt(args, status="FAIL", action="STAGE_SIGNAL_VERIFY", failure_reason=";".join(errors), extra={"errors": errors})
        owner_report(STEP, "N/A", "FAIL", [
            "Signal verify остановлен fail-closed.",
            "Identity или path-политика нарушены.",
            "VM2/E2E/THRONE/watchers не использовались.",
            "Исправьте входные данные.",
        ])
        return 1

    task_root = Path(args.task_root)
    signal_path = resolve_within_task_root(task_root, Path(args.signal_path), allow_nonexistent=False)

    status = "PASS"
    issues = []

    try:
        signal = load_signal_and_verify(signal_path)
    except Exception as exc:
        status = "FAIL"
        issues.append(f"signal_invalid:{exc}")
        signal = None

    ack = None
    if status == "PASS" and args.require_ack:
        if not args.ack_path:
            status = "WAITING"
            issues.append("ack_required_but_missing_path")
        else:
            ack_path = resolve_within_task_root(task_root, Path(args.ack_path), allow_nonexistent=False)
            if not ack_path.exists():
                status = "WAITING"
                issues.append("ack_required_but_missing_file")
            else:
                ack = read_json(ack_path)
                if ack.get("ack_for_signal_id") != signal.get("signal_id"):
                    status = "CONFLICT"
                    issues.append("ack_signal_id_mismatch")
                if ack.get("signal_hash_seen") != signal.get("signal_hash"):
                    status = "CONFLICT"
                    issues.append("ack_signal_hash_mismatch")

    if status == "PASS" and signal is not None:
        for k in ["task_id", "stage_id", "run_id"]:
            if signal.get(k) != getattr(args, k):
                status = "FAIL"
                issues.append(f"signal_identity_mismatch:{k}")

        if signal.get("signal_type") in COMPLETION_TYPES:
            receipt_ref = signal.get("receipt_ref")
            if not receipt_ref:
                status = "BLOCKED"
                issues.append("completion_signal_without_receipt_ref")
            else:
                rr = resolve_within_task_root(task_root, Path(receipt_ref), allow_nonexistent=False)
                if not rr.exists():
                    status = "BLOCKED"
                    issues.append("receipt_ref_missing")

        manifest_ref = signal.get("artifact_manifest_ref")
        if manifest_ref:
            mf = resolve_within_task_root(task_root, Path(manifest_ref), allow_nonexistent=False)
            if not mf.exists():
                status = "WAITING"
                issues.append("artifact_manifest_missing")

    out = {
        "task_id": args.task_id,
        "stage_id": args.stage_id,
        "run_id": args.run_id,
        "contour_id": args.contour_id,
        "status": status,
        "issues": issues,
        "signal_ref": signal_path.relative_to(task_root).as_posix(),
        "ack_required": args.require_ack,
    }

    if args.verify_out:
        verify_out = resolve_within_task_root(task_root, Path(args.verify_out))
        write_json(verify_out, out)

    write_receipt(args, status=status, action="STAGE_SIGNAL_VERIFY", failure_reason=";".join(issues) if status != "PASS" else None, extra=out)
    owner_report(STEP, "N/A", status, [
        "Signal/ACK verify выполнен локально.",
        f"Результат: {status}.",
        "VM2/E2E/THRONE/watchers не использовались.",
        "Решение готово для gate слоя.",
    ])
    return 0 if status == "PASS" else (2 if status == "CONFLICT" else 1)


if __name__ == "__main__":
    raise SystemExit(main())
