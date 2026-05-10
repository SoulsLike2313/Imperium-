#!/usr/bin/env python3
import argparse
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR / "lib"))

from common_runtime import add_common_args, validate_identity, resolve_within_task_root, read_ledger_events, write_json, write_receipt, owner_report

STEP = "TASK-20260508-0014E::stage_coordination_view.py"


def parse_args():
    p = argparse.ArgumentParser(description="Show local stage coordination view")
    add_common_args(p, include_receipt=True, receipt_required=False)
    p.add_argument("--task-map", required=False)
    p.add_argument("--dependency-map", required=False)
    p.add_argument("--ledger-path", required=False)
    p.add_argument("--signals-root", required=False)
    p.add_argument("--acks-root", required=False)
    p.add_argument("--receipts-root", required=False)
    p.add_argument("--gates-root", required=False)
    p.add_argument("--heartbeats-root", required=False)
    p.add_argument("--inquisition-root", required=False)
    p.add_argument("--json-out", required=False)
    return p.parse_args()


def count_json_files(path: Path) -> int:
    if not path.exists():
        return 0
    return len([p for p in path.rglob("*.json") if p.is_file()])


def main():
    args = parse_args()
    errors = validate_identity(args)
    if errors:
        write_receipt(args, status="FAIL", action="STAGE_COORDINATION_VIEW", failure_reason=";".join(errors), extra={"errors": errors})
        owner_report(STEP, "N/A", "FAIL", [
            "Coordination view остановлен fail-closed.",
            "Identity невалиден.",
            "VM2/E2E/THRONE/watchers не использовались.",
            "Исправьте параметры запуска.",
        ])
        return 1

    task_root = Path(args.task_root)

    summary = {
        "task_id": args.task_id,
        "stage_id": args.stage_id,
        "run_id": args.run_id,
        "contour_id": args.contour_id,
        "task_map_present": False,
        "dependency_map_present": False,
        "ledger_events": 0,
        "signals_count": 0,
        "acks_count": 0,
        "receipts_count": 0,
        "gates_count": 0,
        "heartbeats_count": 0,
        "inquisition_reports_count": 0,
        "note": "View is evidence-based and does not assert PASS without gate/receipt evidence.",
    }

    if args.task_map:
        p = resolve_within_task_root(task_root, Path(args.task_map))
        summary["task_map_present"] = p.exists()
    if args.dependency_map:
        p = resolve_within_task_root(task_root, Path(args.dependency_map))
        summary["dependency_map_present"] = p.exists()

    if args.ledger_path:
        p = resolve_within_task_root(task_root, Path(args.ledger_path))
        events, parse_errors = read_ledger_events(p)
        summary["ledger_events"] = len(events)
        summary["ledger_parse_errors"] = parse_errors

    for key, arg_name in [
        ("signals_count", "signals_root"),
        ("acks_count", "acks_root"),
        ("receipts_count", "receipts_root"),
        ("gates_count", "gates_root"),
        ("heartbeats_count", "heartbeats_root"),
        ("inquisition_reports_count", "inquisition_root"),
    ]:
        val = getattr(args, arg_name)
        if val:
            p = resolve_within_task_root(task_root, Path(val))
            summary[key] = count_json_files(p)

    print("Stage Coordination View")
    for k, v in summary.items():
        print(f"- {k}: {v}")

    if args.json_out:
        out = resolve_within_task_root(task_root, Path(args.json_out))
        write_json(out, summary)

    write_receipt(args, status="PASS", action="STAGE_COORDINATION_VIEW", extra=summary)
    owner_report(STEP, "N/A", "PASS", [
        "Сформирован локальный coordination view.",
        "Состояние отражено по карте, ledger, signal/ack и receipt данным.",
        "VM2/E2E/THRONE/watchers не использовались.",
        "View не подменяет gate/barrier решения.",
    ])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
