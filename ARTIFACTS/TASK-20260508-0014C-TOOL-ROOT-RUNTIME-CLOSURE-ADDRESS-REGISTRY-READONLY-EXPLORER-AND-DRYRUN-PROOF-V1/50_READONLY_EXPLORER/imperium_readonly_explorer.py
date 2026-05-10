#!/usr/bin/env python3
"""Read-only CLI explorer for IMPERIUM tool registry."""

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

from owner_report import print_owner_report, write_owner_report  # noqa: E402


MODES = {"summary", "details", "tool", "class", "map"}


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Read-only explorer for TOOLS_MASTER_INDEX")
    parser.add_argument("--tools-index", required=True)
    parser.add_argument("--mode", required=True, choices=sorted(MODES))
    parser.add_argument("--tool-id", default="")
    parser.add_argument("--class", dest="tool_class", default="")
    parser.add_argument("--json-output", default="")
    parser.add_argument("--owner-report-output", default="")
    parser.add_argument("--readonly-assert", default="true")
    return parser


def _load_index(path: Path) -> dict:
    if not path.exists():
        raise FileNotFoundError(f"tools index not found: {path}")
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict) or "tools" not in data:
        raise ValueError("invalid tools index format")
    return data


def _summary(data: dict) -> dict:
    tools = data.get("tools", [])
    class_counts: dict[str, int] = {}
    status_counts: dict[str, int] = {}
    for item in tools:
        cls = str(item.get("tool_class", "UNKNOWN"))
        st = str(item.get("status", "UNKNOWN"))
        class_counts[cls] = class_counts.get(cls, 0) + 1
        status_counts[st] = status_counts.get(st, 0) + 1
    return {
        "tools_root": data.get("tools_root", ""),
        "active_tools_count": len([t for t in tools if str(t.get("status", "")).startswith("ACTIVE")]),
        "class_count": len(class_counts),
        "legacy_or_blocked_count": len([t for t in tools if t.get("status") in {"LEGACY_CANDIDATE", "LEGACY_QUARANTINE", "BLOCKED", "DEPRECATED"}]),
        "last_verified_utc_max": max([str(t.get("last_verified_utc", "")) for t in tools] + [""]),
        "class_counts": class_counts,
        "status_counts": status_counts,
    }


def _render_map() -> str:
    return (
        "OWNER\n"
        "  -> PC_VM2_SEND_PROMPT\n"
        "      -> VM2_WORKER_STAGE\n"
        "          -> PC_VM2_FETCH_STAGE_BUNDLE\n"
        "              -> PC_BARRIER_VERIFY\n"
        "                  -> PC_FINAL_BUNDLE_ASSEMBLE\n\n"
        "OWNER\n"
        "  -> CONTINUITY_PACK_BUILD\n"
        "      -> CONTINUITY_PACK_VERIFY\n"
        "          -> CONTINUITY_PACK_REDACT\n"
    )


def main() -> int:
    args = build_parser().parse_args()

    verdict = "FAIL"
    bundle_ref = "N/A"

    try:
        readonly_assert = str(args.readonly_assert).strip().lower()
        if readonly_assert not in {"true", "1", "yes"}:
            raise ValueError("readonly assertion must be true")

        index_path = Path(args.tools_index).resolve()
        data = _load_index(index_path)
        tools = data.get("tools", [])

        output_payload: object
        if args.mode == "summary":
            output_payload = _summary(data)
        elif args.mode == "details":
            output_payload = tools
        elif args.mode == "tool":
            if not args.tool_id:
                raise ValueError("--tool-id is required for mode=tool")
            matches = [t for t in tools if t.get("tool_id") == args.tool_id]
            if not matches:
                raise ValueError(f"tool_id not found: {args.tool_id}")
            output_payload = matches[0]
        elif args.mode == "class":
            if not args.tool_class:
                raise ValueError("--class is required for mode=class")
            output_payload = [t for t in tools if t.get("tool_class") == args.tool_class]
        elif args.mode == "map":
            output_payload = {"flow_map": _render_map()}
        else:
            raise ValueError(f"unsupported mode: {args.mode}")

        if isinstance(output_payload, dict) and "flow_map" in output_payload:
            print(output_payload["flow_map"])
        else:
            print(json.dumps(output_payload, indent=2, ensure_ascii=False))

        if args.json_output:
            out = Path(args.json_output).resolve()
            out.parent.mkdir(parents=True, exist_ok=True)
            out.write_text(json.dumps(output_payload, indent=2, ensure_ascii=False), encoding="utf-8")
            bundle_ref = str(out)

        verdict = "PASS"
        comments = [
            "Выполнен read-only обзор реестра инструментов без изменений файлов системы.",
            "Показаны адреса, статусы и карта потока для Owner/PC/VM2 сценария.",
            "Сетевые действия, VM2/THRONE доступ и автоматизация не выполнялись.",
            "Следующий шаг: использовать tool_id из реестра в TASK-0015 после Speculum go/no-go.",
        ]

    except Exception as exc:  # pylint: disable=broad-except
        print(f"ERROR: {exc}", file=sys.stderr)
        comments = [
            "Read-only explorer завершился с ошибкой параметров или формата реестра.",
            "Система не изменялась: запись/перемещение/удаление не выполнялись.",
            "Внешние контуры и THRONE не затрагивались.",
            "Следующий шаг: исправить входные параметры и повторить read-only вызов.",
        ]

    step = f"READONLY_EXPLORER/{args.mode}"
    print_owner_report(step, bundle_ref, verdict, comments)
    if args.owner_report_output:
        write_owner_report(Path(args.owner_report_output).resolve(), step, bundle_ref, verdict, comments)
    return 0 if verdict == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
