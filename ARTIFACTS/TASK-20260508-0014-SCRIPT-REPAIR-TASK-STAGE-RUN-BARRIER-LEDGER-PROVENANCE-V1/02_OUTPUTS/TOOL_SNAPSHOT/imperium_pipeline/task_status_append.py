#!/usr/bin/env python3
"""Append one event to append-only TASK_STATUS_LEDGER.jsonl."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from lib.id_validation import (  # noqa: E402
    validate_contour_id,
    validate_event_type,
    validate_producer_id,
    validate_producer_type,
    validate_run_id,
    validate_stage_id,
    validate_task_id,
)
from lib.ledger_utils import append_event  # noqa: E402
from lib.owner_report import print_owner_report, write_owner_report  # noqa: E402


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Append one event to TASK_STATUS_LEDGER.jsonl")
    parser.add_argument("--ledger-path", required=True)
    parser.add_argument("--event-type", required=True)
    parser.add_argument("--task-id", required=True)
    parser.add_argument("--stage-id", required=True)
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--contour-id", required=True)
    parser.add_argument("--producer-type", required=True)
    parser.add_argument("--producer-id", required=True)
    parser.add_argument("--status", required=True)
    parser.add_argument("--artifact-ref", default="")
    parser.add_argument("--artifact-sha256", default="")
    parser.add_argument("--receipt-ref", default="")
    parser.add_argument("--provenance-ref", default="")
    parser.add_argument("--origin-key", default="")
    parser.add_argument("--notes", default="")
    parser.add_argument("--owner-report-output", default="")
    parser.add_argument("--json-output", default="")
    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()

    verdict = "FAIL"
    bundle_ref = args.artifact_ref if args.artifact_ref else "N/A"

    try:
        task_id = validate_task_id(args.task_id)
        stage_id = validate_stage_id(args.stage_id)
        run_id = validate_run_id(args.run_id)
        contour_id = validate_contour_id(args.contour_id)
        producer_type = validate_producer_type(args.producer_type)
        producer_id = validate_producer_id(args.producer_id)
        event_type = validate_event_type(args.event_type)

        event = {
            "task_id": task_id,
            "stage_id": stage_id,
            "run_id": run_id,
            "contour_id": contour_id,
            "producer_type": producer_type,
            "producer_id": producer_id,
            "event_type": event_type,
            "status": args.status.strip().upper(),
            "artifact_ref": args.artifact_ref,
            "artifact_sha256": args.artifact_sha256,
            "previous_event_ref": "",
            "timestamp_utc": "",
            "receipt_ref": args.receipt_ref,
            "notes": args.notes,
            "provenance_ref": args.provenance_ref,
            "origin_key": args.origin_key,
        }

        appended = append_event(Path(args.ledger_path).resolve(), event)

        if args.json_output:
            out = Path(args.json_output).resolve()
            out.parent.mkdir(parents=True, exist_ok=True)
            out.write_text(json.dumps(appended, indent=2), encoding="utf-8")

        verdict = "PASS"
        comments = [
            "Добавлено одно событие в append-only ledger без перезаписи предыдущих состояний.",
            "Проверены обязательные TASK/STAGE/RUN/CONTOUR и producer поля перед записью.",
            "Единый mutable status.json как источник истины не использовался.",
            "Следующий шаг: проверить агрегированное состояние через task_status_view.py.",
        ]

    except Exception as exc:  # pylint: disable=broad-except
        comments = [
            "Запись в ledger отклонена из-за ошибки в обязательных полях или формате события.",
            "Append-only контракт не был нарушен, перезапись статусов не выполнялась.",
            "THRONE и внешние контуры не затрагивались.",
            "Следующий шаг: исправить параметры события и повторить append.",
        ]
        print(f"ERROR: {exc}", file=sys.stderr)

    step = f"{args.task_id}/{args.stage_id}/task_status_append.py"
    print_owner_report(step, bundle_ref, verdict, comments)
    if args.owner_report_output:
        write_owner_report(Path(args.owner_report_output).resolve(), step, bundle_ref, verdict, comments)
    return 0 if verdict == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
