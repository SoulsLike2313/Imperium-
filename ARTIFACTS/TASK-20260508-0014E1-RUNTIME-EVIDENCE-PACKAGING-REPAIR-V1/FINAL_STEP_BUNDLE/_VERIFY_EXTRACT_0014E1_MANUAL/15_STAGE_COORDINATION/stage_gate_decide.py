#!/usr/bin/env python3
import argparse
import sys
from pathlib import Path
from typing import List

SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR / "lib"))

from common_runtime import (
    add_common_args,
    validate_identity,
    resolve_within_task_root,
    read_json,
    load_signal_and_verify,
    write_json,
    write_receipt,
    append_ledger_event,
    owner_report,
    now_utc,
)

STEP = "TASK-20260508-0014E::stage_gate_decide.py"
COMPLETION_TYPES = {"STAGE_COMPLETED", "READY_FOR_NEXT"}


def parse_args():
    p = argparse.ArgumentParser(description="Gate authority for stage movement")
    add_common_args(p, include_receipt=True, receipt_required=False)
    p.add_argument("--dependency-map", required=True)
    p.add_argument("--ledger-path", required=True)
    p.add_argument("--signals-root", required=True)
    p.add_argument("--acks-root", required=True)
    p.add_argument("--receipts-root", required=True)
    p.add_argument("--manifests-root", required=False)
    p.add_argument("--provenance-root", required=False)
    p.add_argument("--gate-out", required=True)
    return p.parse_args()


def load_signals(task_root: Path, signals_root: Path):
    signals = []
    issues = []
    if not signals_root.exists():
        return signals, issues
    for fp in signals_root.rglob("*.json"):
        try:
            sig = load_signal_and_verify(fp)
            sig["__path"] = fp.relative_to(task_root).as_posix()
            signals.append(sig)
        except Exception as exc:
            issues.append(f"invalid_signal:{fp.name}:{exc}")
    return signals, issues


def load_acks(task_root: Path, acks_root: Path):
    acks = []
    issues = []
    if not acks_root.exists():
        return acks, issues
    for fp in acks_root.rglob("*.json"):
        try:
            ack = read_json(fp)
            ack["__path"] = fp.relative_to(task_root).as_posix()
            acks.append(ack)
        except Exception as exc:
            issues.append(f"invalid_ack:{fp.name}:{exc}")
    return acks, issues


def main():
    args = parse_args()
    errors = validate_identity(args)
    if errors:
        write_receipt(args, status="GATE_FAIL", action="STAGE_GATE_DECIDE", failure_reason=";".join(errors), extra={"errors": errors})
        owner_report(STEP, "N/A", "FAIL", [
            "Gate decide остановлен fail-closed.",
            "Identity невалиден.",
            "VM2/E2E/THRONE/watchers не использовались.",
            "Исправьте входные данные.",
        ])
        return 1

    task_root = Path(args.task_root)
    dep_map_path = resolve_within_task_root(task_root, Path(args.dependency_map), allow_nonexistent=False)
    signals_root = resolve_within_task_root(task_root, Path(args.signals_root))
    acks_root = resolve_within_task_root(task_root, Path(args.acks_root))
    receipts_root = resolve_within_task_root(task_root, Path(args.receipts_root))
    gate_out = resolve_within_task_root(task_root, Path(args.gate_out))

    dep_map = read_json(dep_map_path)
    entries = dep_map.get("dependencies", [])
    stage_entry = None
    for x in entries:
        if x.get("stage_id") == args.stage_id:
            stage_entry = x
            break

    reasons: List[str] = []
    decision = "GATE_WAITING"

    signals, signal_issues = load_signals(task_root, signals_root)
    acks, ack_issues = load_acks(task_root, acks_root)
    reasons.extend(signal_issues)
    reasons.extend(ack_issues)

    signal_ids = {s.get("signal_id") for s in signals}
    for ack in acks:
        if ack.get("ack_for_signal_id") not in signal_ids:
            decision = "GATE_CONFLICT"
            reasons.append(f"ack_without_signal:{ack.get('ack_for_signal_id')}")

    if decision != "GATE_CONFLICT":
        if stage_entry is None:
            reasons.append("stage_dependency_entry_missing")
            decision = "GATE_WAITING"
        else:
            depends_on = stage_entry.get("depends_on", [])
            mode = stage_entry.get("mode", "ALL")
            requires_ack = bool(stage_entry.get("requires_ack"))

            satisfied = []
            for dep_stage in depends_on:
                dep_signals = [
                    s for s in signals
                    if s.get("stage_id") == dep_stage and s.get("signal_type") in COMPLETION_TYPES
                ]
                if not dep_signals:
                    reasons.append(f"missing_completion_signal:{dep_stage}")
                    satisfied.append(False)
                    continue

                dep_ok = False
                for sig in dep_signals:
                    receipt_ref = sig.get("receipt_ref")
                    if not receipt_ref:
                        continue
                    rr = resolve_within_task_root(task_root, Path(receipt_ref))
                    if not rr.exists() or rr.is_dir():
                        continue
                    if requires_ack:
                        matched_ack = [a for a in acks if a.get("ack_for_signal_id") == sig.get("signal_id") and a.get("signal_hash_seen") == sig.get("signal_hash")]
                        if not matched_ack:
                            continue
                    dep_ok = True
                    break

                if dep_ok:
                    satisfied.append(True)
                else:
                    reasons.append(f"dependency_not_proven:{dep_stage}")
                    satisfied.append(False)

            if depends_on:
                dep_ready = any(satisfied) if mode == "ANY" else all(satisfied)
            else:
                dep_ready = False
                reasons.append("no_dependency_proof_default_waiting")

            if dep_ready and decision != "GATE_CONFLICT":
                decision = "GATE_READY"
            elif decision != "GATE_CONFLICT":
                decision = "GATE_WAITING"

    gate = {
        "task_id": args.task_id,
        "stage_id": args.stage_id,
        "run_id": args.run_id,
        "contour_id": args.contour_id,
        "actor_id": args.actor_id,
        "tool_id": args.tool_id,
        "timestamp_utc": now_utc(),
        "decision": decision,
        "reasons": reasons,
    }
    write_json(gate_out, gate)

    append_ledger_event(
        args,
        ledger_path=Path(args.ledger_path),
        event_type="GATE_DECISION",
        status=decision,
        evidence_refs=[gate_out.relative_to(task_root).as_posix()],
        extra={"reasons_count": len(reasons)},
    )

    write_receipt(args, status=decision, action="STAGE_GATE_DECIDE", failure_reason=";".join(reasons) if decision != "GATE_READY" else None, extra={"gate_ref": gate_out.relative_to(task_root).as_posix(), "decision": decision})
    owner_report(STEP, "N/A", decision, [
        "Gate decision рассчитан локально по dependency evidence.",
        f"Результат: {decision}.",
        "VM2/E2E/THRONE/watchers не использовались.",
        "Движение stage допустимо только при GATE_READY.",
    ])
    return 0 if decision == "GATE_READY" else (2 if decision == "GATE_CONFLICT" else 1)


if __name__ == "__main__":
    raise SystemExit(main())
