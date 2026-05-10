#!/usr/bin/env python3
import argparse
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR / "lib"))

from common_runtime import add_common_args, validate_identity, append_ledger_event, resolve_within_task_root, write_json, write_receipt, owner_report

STEP = "TASK-20260508-0014E::ledger_append.py"


def parse_args():
    p = argparse.ArgumentParser(description="Append event to TASK_STATUS_LEDGER.jsonl")
    add_common_args(p, include_receipt=True, receipt_required=False)
    p.add_argument("--ledger-path", required=True)
    p.add_argument("--event-type", required=True)
    p.add_argument("--status", required=True)
    p.add_argument("--evidence-ref", action="append", default=[])
    p.add_argument("--artifact-ref", required=False)
    p.add_argument("--artifact-sha256", required=False)
    p.add_argument("--event-out", required=False)
    return p.parse_args()


def main():
    args = parse_args()
    errors = validate_identity(args)
    if errors:
        write_receipt(args, status="FAIL", action="LEDGER_APPEND", failure_reason=";".join(errors), extra={"errors": errors})
        owner_report(STEP, "N/A", "FAIL", [
            "Append в ledger остановлен fail-closed.",
            "Identity невалиден.",
            "VM2/E2E/THRONE/watchers не использовались.",
            "Исправьте входные поля.",
        ])
        return 1

    extra = {
        "artifact_ref": args.artifact_ref,
        "artifact_sha256": args.artifact_sha256,
    }

    try:
        event = append_ledger_event(
            args,
            ledger_path=Path(args.ledger_path),
            event_type=args.event_type,
            status=args.status,
            evidence_refs=args.evidence_ref,
            extra=extra,
        )
    except Exception as exc:
        write_receipt(args, status="FAIL", action="LEDGER_APPEND", failure_reason=str(exc))
        owner_report(STEP, "N/A", "FAIL", [
            "Append в ledger завершился ошибкой.",
            str(exc),
            "VM2/E2E/THRONE/watchers не использовались.",
            "Проверьте ledger и параметры.",
        ])
        return 1

    if args.event_out:
        event_out = resolve_within_task_root(Path(args.task_root), Path(args.event_out))
        write_json(event_out, event)

    write_receipt(args, status="PASS", action="LEDGER_APPEND", extra={
        "event_id": event.get("event_id"),
        "event_hash": event.get("event_hash"),
    })
    owner_report(STEP, "N/A", "PASS", [
        "Ledger event добавлен локально.",
        "Hash-chain обновлен append-only.",
        "VM2/E2E/THRONE/watchers не использовались.",
        "Событие готово для replay/verify.",
    ])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
