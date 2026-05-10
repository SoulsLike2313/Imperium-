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
    read_json,
    read_ledger_events,
    verify_event_hash,
    load_signal_and_verify,
    write_json,
    write_receipt,
    owner_report,
)

STEP = "TASK-20260508-0014E::inquisition_trace_audit.py"
COMPLETION_TYPES = {"STAGE_COMPLETED", "READY_FOR_NEXT"}


def parse_args():
    p = argparse.ArgumentParser(description="Inquisition local trace audit")
    add_common_args(p, include_receipt=True, receipt_required=False)
    p.add_argument("--ledger-path", required=True)
    p.add_argument("--signals-root", required=True)
    p.add_argument("--acks-root", required=True)
    p.add_argument("--receipts-root", required=True)
    p.add_argument("--audit-out", required=True)
    return p.parse_args()


def main():
    args = parse_args()
    errors = validate_identity(args)
    if errors:
        write_receipt(args, status="FAIL", action="INQUISITION_TRACE_AUDIT", failure_reason=";".join(errors), extra={"errors": errors})
        owner_report(STEP, "N/A", "FAIL", [
            "Inquisition audit остановлен fail-closed.",
            "Identity невалиден.",
            "VM2/E2E/THRONE/watchers не использовались.",
            "Исправьте входные параметры.",
        ])
        return 1

    task_root = Path(args.task_root)
    ledger_path = resolve_within_task_root(task_root, Path(args.ledger_path), allow_nonexistent=False)
    signals_root = resolve_within_task_root(task_root, Path(args.signals_root))
    acks_root = resolve_within_task_root(task_root, Path(args.acks_root))
    receipts_root = resolve_within_task_root(task_root, Path(args.receipts_root))
    audit_out = resolve_within_task_root(task_root, Path(args.audit_out))

    issues = []
    warnings = []

    events, parse_errors = read_ledger_events(ledger_path)
    if parse_errors:
        issues.extend(parse_errors)

    prev = None
    for ev in events:
        if not verify_event_hash(ev):
            issues.append(f"event_hash_mismatch:{ev.get('event_id')}")
        if ev.get("previous_event_hash") != prev:
            issues.append(f"previous_event_hash_mismatch:{ev.get('event_id')}")
        prev = ev.get("event_hash")

    signals = []
    signal_ids = set()
    for fp in signals_root.rglob("*.json") if signals_root.exists() else []:
        try:
            sig = load_signal_and_verify(fp)
            sig["__path"] = fp.relative_to(task_root).as_posix()
            signals.append(sig)
            signal_ids.add(sig.get("signal_id"))

            if sig.get("signal_type") in COMPLETION_TYPES:
                rr = sig.get("receipt_ref")
                if not rr:
                    issues.append(f"completion_without_receipt:{sig.get('signal_id')}")
                else:
                    rp = resolve_within_task_root(task_root, Path(rr))
                    if not rp.exists():
                        issues.append(f"completion_receipt_missing:{sig.get('signal_id')}")

            if sig.get("signal_type") in COMPLETION_TYPES and sig.get("artifact_manifest_ref") and not sig.get("provenance_ref"):
                issues.append(f"missing_provenance_for_accepted_artifact:{sig.get('signal_id')}")

            joined = str(sig).lower()
            if "fallback" in joined:
                issues.append(f"fallback_detected:{sig.get('signal_id')}")
            if has_latest_pattern(joined):
                issues.append(f"latest_pattern_detected:{sig.get('signal_id')}")
        except Exception as exc:
            issues.append(f"invalid_signal:{fp.name}:{exc}")

    for fp in acks_root.rglob("*.json") if acks_root.exists() else []:
        try:
            ack = read_json(fp)
            sid = ack.get("ack_for_signal_id")
            if sid not in signal_ids:
                issues.append(f"ack_without_signal:{sid}")
        except Exception as exc:
            issues.append(f"invalid_ack:{fp.name}:{exc}")

    gate_ready_by_stage = set()
    started_without_gate = []
    for ev in events:
        key = (ev.get("task_id"), ev.get("stage_id"), ev.get("run_id"), ev.get("contour_id"))
        if ev.get("event_type") == "GATE_DECISION" and ev.get("status") == "GATE_READY":
            gate_ready_by_stage.add(key)
        if ev.get("event_type") == "STAGE_STARTED" and key not in gate_ready_by_stage:
            started_without_gate.append(key)
    for k in started_without_gate:
        issues.append(f"stage_started_without_gate_ready:{k}")

    verdict = "PASS"
    if issues:
        hard_conflict = any("ack_without_signal" in x or "event_hash_mismatch" in x or "previous_event_hash_mismatch" in x for x in issues)
        verdict = "CONFLICT" if hard_conflict else "REPAIR_REQUIRED"
    elif warnings:
        verdict = "WARNING"

    audit = {
        "task_id": args.task_id,
        "stage_id": args.stage_id,
        "run_id": args.run_id,
        "contour_id": args.contour_id,
        "verdict": verdict,
        "issues": issues,
        "warnings": warnings,
        "signals_count": len(signals),
        "ledger_events": len(events),
    }
    write_json(audit_out, audit)

    write_receipt(args, status=verdict, action="INQUISITION_TRACE_AUDIT", failure_reason=";".join(issues) if issues else None, extra={"audit_ref": audit_out.relative_to(task_root).as_posix(), "issues_count": len(issues)})
    owner_report(STEP, "N/A", verdict, [
        "Inquisition trace audit выполнен локально.",
        f"Вердикт: {verdict}; issues: {len(issues)}.",
        "VM2/E2E/THRONE/watchers не использовались.",
        "Desync/violation проверены по локальным следам.",
    ])
    return 0 if verdict == "PASS" else (2 if verdict == "CONFLICT" else 1)


if __name__ == "__main__":
    raise SystemExit(main())
