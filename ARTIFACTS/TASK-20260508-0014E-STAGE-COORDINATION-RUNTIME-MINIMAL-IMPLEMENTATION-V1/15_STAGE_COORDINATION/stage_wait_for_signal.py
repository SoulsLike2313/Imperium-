#!/usr/bin/env python3
import argparse
import sys
import time
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR / "lib"))

from common_runtime import (
    add_common_args,
    validate_identity,
    resolve_within_task_root,
    load_signal_and_verify,
    read_json,
    write_json,
    write_receipt,
    append_ledger_event,
    owner_report,
    now_utc,
)

STEP = "TASK-20260508-0014E::stage_wait_for_signal.py"


def parse_args():
    p = argparse.ArgumentParser(description="Bounded wait for dependency signal")
    add_common_args(p, include_receipt=True, receipt_required=False)
    p.add_argument("--waiting-for-stage-id", required=True)
    p.add_argument("--signals-root", required=True)
    p.add_argument("--acks-root", required=True)
    p.add_argument("--receipts-root", required=True)
    p.add_argument("--heartbeats-root", required=True)
    p.add_argument("--ledger-path", required=True)
    p.add_argument("--stop-out", required=True)
    p.add_argument("--wait-out", required=True)
    p.add_argument("--poll-interval-sec", required=True, type=int)
    p.add_argument("--max-attempts", required=True, type=int)
    p.add_argument("--timeout-sec", required=True, type=int)
    p.add_argument("--require-ack", action="store_true")
    return p.parse_args()


def check_ready(task_root: Path, waiting_stage: str, signals_root: Path, acks_root: Path, receipts_root: Path, require_ack: bool):
    signals = []
    if signals_root.exists():
        for fp in signals_root.rglob("*.json"):
            try:
                sig = load_signal_and_verify(fp)
                signals.append(sig)
            except Exception:
                continue

    acks = []
    if acks_root.exists():
        for fp in acks_root.rglob("*.json"):
            try:
                acks.append(read_json(fp))
            except Exception:
                continue

    dep_signals = [s for s in signals if s.get("stage_id") == waiting_stage and s.get("signal_type") in {"STAGE_COMPLETED", "READY_FOR_NEXT"}]
    if not dep_signals:
        return "WAITING", "missing_completion_signal"

    for sig in dep_signals:
        receipt_ref = sig.get("receipt_ref")
        if not receipt_ref:
            continue
        rr = resolve_within_task_root(task_root, Path(receipt_ref))
        if not rr.exists() or rr.is_dir():
            continue
        if require_ack:
            ok = any(a.get("ack_for_signal_id") == sig.get("signal_id") and a.get("signal_hash_seen") == sig.get("signal_hash") for a in acks)
            if not ok:
                continue
        return "READY", "dependency_proven"

    return "WAITING", "dependency_not_proven"


def write_stop(stop_out: Path, args, stop_type: str, reason: str):
    payload = {
        "task_id": args.task_id,
        "stage_id": args.stage_id,
        "run_id": args.run_id,
        "contour_id": args.contour_id,
        "actor_id": args.actor_id,
        "tool_id": args.tool_id,
        "timestamp_utc": now_utc(),
        "stop_type": stop_type,
        "status": stop_type,
        "human_readable_reason": reason,
        "next_allowed_action": "owner_or_repair_decision",
    }
    write_json(stop_out, payload)


def main():
    args = parse_args()
    errors = validate_identity(args)
    if args.max_attempts <= 0 or args.timeout_sec <= 0 or args.poll_interval_sec <= 0:
        errors.append("invalid_wait_bounds")
    if errors:
        write_receipt(args, status="FAIL", action="STAGE_WAIT_FOR_SIGNAL", failure_reason=";".join(errors), extra={"errors": errors})
        owner_report(STEP, "N/A", "FAIL", [
            "Bounded wait остановлен fail-closed.",
            "Identity или bounds невалидны.",
            "VM2/E2E/THRONE/watchers не использовались.",
            "Исправьте параметры ожидания.",
        ])
        return 1

    task_root = Path(args.task_root)
    signals_root = resolve_within_task_root(task_root, Path(args.signals_root))
    acks_root = resolve_within_task_root(task_root, Path(args.acks_root))
    receipts_root = resolve_within_task_root(task_root, Path(args.receipts_root))
    heartbeats_root = resolve_within_task_root(task_root, Path(args.heartbeats_root))
    stop_out = resolve_within_task_root(task_root, Path(args.stop_out))
    wait_out = resolve_within_task_root(task_root, Path(args.wait_out))

    start = time.time()
    final_status = "GATE_WAITING"
    final_reason = "not_ready"

    for attempt in range(1, args.max_attempts + 1):
        state, reason = check_ready(task_root, args.waiting_for_stage_id, signals_root, acks_root, receipts_root, args.require_ack)

        hb = {
            "task_id": args.task_id,
            "stage_id": args.stage_id,
            "run_id": args.run_id,
            "contour_id": args.contour_id,
            "actor_id": args.actor_id,
            "tool_id": args.tool_id,
            "timestamp_utc": now_utc(),
            "attempt": attempt,
            "status": "WAITING" if state != "READY" else "READY",
            "reason": reason,
            "waiting_for_stage_id": args.waiting_for_stage_id,
        }
        hb_path = heartbeats_root / f"heartbeat_{attempt:03d}.json"
        write_json(hb_path, hb)

        append_ledger_event(
            args,
            ledger_path=Path(args.ledger_path),
            event_type="STAGE_WAIT_HEARTBEAT",
            status=hb["status"],
            evidence_refs=[hb_path.relative_to(task_root).as_posix()],
            extra={"attempt": attempt, "waiting_for": args.waiting_for_stage_id},
        )

        elapsed = time.time() - start
        if state == "READY":
            final_status = "GATE_READY"
            final_reason = "dependency_proven"
            break

        if elapsed >= args.timeout_sec:
            final_status = "GATE_TIMEOUT"
            final_reason = "timeout_reached"
            break

        if attempt < args.max_attempts:
            time.sleep(args.poll_interval_sec)

    if final_status not in {"GATE_READY", "GATE_TIMEOUT"}:
        final_status = "GATE_TIMEOUT"
        final_reason = "max_attempts_reached"

    if final_status != "GATE_READY":
        write_stop(stop_out, args, stop_type=final_status, reason=final_reason)
        append_ledger_event(
            args,
            ledger_path=Path(args.ledger_path),
            event_type="STAGE_STOPPED",
            status=final_status,
            evidence_refs=[stop_out.relative_to(task_root).as_posix()],
            extra={"reason": final_reason},
        )

    result = {
        "task_id": args.task_id,
        "stage_id": args.stage_id,
        "run_id": args.run_id,
        "contour_id": args.contour_id,
        "waiting_for_stage_id": args.waiting_for_stage_id,
        "status": final_status,
        "reason": final_reason,
        "max_attempts": args.max_attempts,
        "timeout_sec": args.timeout_sec,
    }
    write_json(wait_out, result)

    write_receipt(args, status=final_status, action="STAGE_WAIT_FOR_SIGNAL", failure_reason=final_reason if final_status != "GATE_READY" else None, extra={"wait_result_ref": wait_out.relative_to(task_root).as_posix()})
    owner_report(STEP, "N/A", final_status, [
        "Bounded wait выполнен локально без watcher-режима.",
        f"Итог ожидания: {final_status}.",
        "VM2/E2E/THRONE/watchers не использовались.",
        "Переход возможен только при GATE_READY.",
    ])
    return 0 if final_status == "GATE_READY" else 1


if __name__ == "__main__":
    raise SystemExit(main())
