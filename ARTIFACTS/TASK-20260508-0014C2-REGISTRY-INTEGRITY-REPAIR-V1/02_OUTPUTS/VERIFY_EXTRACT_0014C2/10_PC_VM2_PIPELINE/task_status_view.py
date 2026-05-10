#!/usr/bin/env python3
"""Read TASK_STATUS_LEDGER.jsonl and summarize task position."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
TOOLS_ROOT = SCRIPT_DIR.parent
CORE_LIB_DIR = TOOLS_ROOT / "01_CORE_LIB"
if str(CORE_LIB_DIR) not in sys.path:
    sys.path.insert(0, str(CORE_LIB_DIR))

from id_validation import validate_task_id  # noqa: E402
from ledger_utils import summarize_task_state  # noqa: E402
from owner_report import print_owner_report, write_owner_report  # noqa: E402


ALLOWED_HIGH_LEVEL_STATUSES = {"WAITING", "RUNNING", "PASS", "FAIL", "CONFLICT", "BLOCKED", "COMPLETED"}


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="View task status from append-only ledger")
    parser.add_argument("--ledger-path", required=True)
    parser.add_argument("--task-id", required=True)
    parser.add_argument("--json-output", default="")
    parser.add_argument("--owner-report-output", default="")
    return parser


def _normalize_status(summary: dict) -> str:
    state = str(summary.get("overall_status", "BLOCKED")).upper()
    if state not in ALLOWED_HIGH_LEVEL_STATUSES:
        return "BLOCKED"
    return state


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()

    verdict = "FAIL"
    bundle_ref = "N/A"

    try:
        task_id = validate_task_id(args.task_id)
        summary = summarize_task_state(Path(args.ledger_path).resolve(), task_id)
        summary["high_level_status"] = _normalize_status(summary)

        print(json.dumps(summary, indent=2, ensure_ascii=False))

        if args.json_output:
            out = Path(args.json_output).resolve()
            out.parent.mkdir(parents=True, exist_ok=True)
            out.write_text(json.dumps(summary, indent=2), encoding="utf-8")
            bundle_ref = str(out)

        verdict = "PASS"
        comments = [
            "Сформирована сводка статуса задачи из append-only ledger без изменения его содержимого.",
            "Показаны стадии, активные/проваленные run и флаги конфликтов/барьерных событий.",
            "Решение BARRIER_PASS не вычислялось этим скриптом и не подменялось.",
            "Следующий шаг: использовать barrier_verify.py для формального barrier verdict.",
        ]

    except Exception as exc:  # pylint: disable=broad-except
        comments = [
            "Не удалось построить сводку статуса из ledger из-за ошибки чтения или валидации TASK_ID.",
            "Append-only журнал не изменялся этим вызовом.",
            "THRONE и внешние контуры не затрагивались.",
            "Следующий шаг: исправить ledger-path/format и повторить просмотр статуса.",
        ]
        print(f"ERROR: {exc}", file=sys.stderr)

    step = f"{args.task_id}/task_status_view.py"
    print_owner_report(step, bundle_ref, verdict, comments)
    if args.owner_report_output:
        write_owner_report(Path(args.owner_report_output).resolve(), step, bundle_ref, verdict, comments)
    return 0 if verdict == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
