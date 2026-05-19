from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


@dataclass
class CheckResult:
    errors: list[str]
    warnings: list[str]
    tool_count: int


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def load_json(path: Path) -> dict[str, Any]:
    raw = path.read_text(encoding="utf-8")
    data = json.loads(raw)
    if not isinstance(data, dict):
        raise ValueError(f"JSON root must be an object: {path}")
    return data


def parse_index(index_path: Path) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    payload = load_json(index_path)
    tools = payload.get("tools", [])
    if not isinstance(tools, list):
        raise ValueError(f".tools must be a list: {index_path}")
    parsed: list[dict[str, Any]] = []
    for item in tools:
        if not isinstance(item, dict):
            raise ValueError(f"Invalid tool record (not object): {item!r}")
        parsed.append(item)
    return payload, parsed


def check_registry(index_path: Path) -> CheckResult:
    errors: list[str] = []
    warnings: list[str] = []
    tool_count = 0
    try:
        payload, tools = parse_index(index_path)
    except Exception as err:
        return CheckResult(errors=[f"index_load_error: {err}"], warnings=[], tool_count=0)

    schema = str(payload.get("schema_version", ""))
    if not schema:
        errors.append("missing schema_version in TOOL_INDEX.json")
    if not schema.startswith("MECHANICUS_TOOL_INDEX_"):
        warnings.append(f"unexpected TOOL_INDEX schema_version: {schema}")

    root = index_path.parent
    seen_tool_ids: set[str] = set()
    for item in tools:
        tool_count += 1
        tool_id = str(item.get("tool_id", "")).strip()
        card_rel = str(item.get("tool_card_path", "")).strip()
        if not tool_id:
            errors.append("tool record missing tool_id")
            continue
        if tool_id in seen_tool_ids:
            errors.append(f"duplicate tool_id in index: {tool_id}")
            continue
        seen_tool_ids.add(tool_id)

        if not card_rel:
            errors.append(f"tool {tool_id} missing tool_card_path")
            continue
        card_path = (root / card_rel).resolve()
        if not card_path.exists():
            errors.append(f"tool card not found: tool_id={tool_id} path={card_path}")
            continue
        try:
            card = load_json(card_path)
        except Exception as err:
            errors.append(f"tool card invalid JSON: tool_id={tool_id} path={card_path} error={err}")
            continue

        card_tool_id = str(card.get("tool_id", "")).strip()
        if card_tool_id != tool_id:
            errors.append(f"tool_id mismatch index/card: index={tool_id} card={card_tool_id} path={card_path}")
        if str(card.get("schema_version", "")).strip() != "MECHANICUS_TOOL_CARD_V0_1":
            warnings.append(f"unexpected card schema_version for {tool_id}: {card.get('schema_version')}")

        required_fields = [
            "display_name",
            "owner_organ",
            "consumer_organs",
            "capability_summary",
            "allowed_use_cases",
            "forbidden_use_cases",
            "install_policy",
            "pc_status",
            "vm2_status",
            "version_pc",
            "version_vm2",
            "command_examples",
            "evidence_required",
            "failure_policy",
            "admission_status",
        ]
        for field in required_fields:
            if field not in card:
                errors.append(f"tool card missing field: tool_id={tool_id} field={field}")

    return CheckResult(errors=errors, warnings=warnings, tool_count=tool_count)


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=True, indent=2) + "\n", encoding="utf-8")


def cmd_list(index_path: Path, as_json: bool) -> int:
    _, tools = parse_index(index_path)
    rows = []
    for item in tools:
        rows.append(
            {
                "tool_id": str(item.get("tool_id", "")),
                "display_name": str(item.get("display_name", "")),
                "combined_status": str(item.get("combined_status", "")),
                "owner_organ": str(item.get("owner_organ", "")),
                "tool_card_path": str(item.get("tool_card_path", "")),
            }
        )
    if as_json:
        print(json.dumps({"schema_version": "MECHANICUS_TOOL_LIST_V0_1", "tools": rows}, ensure_ascii=True, indent=2))
        return 0

    print("MECHANICUS TOOL REGISTRY LIST")
    print("tool_id | owner_organ | combined_status | tool_card_path")
    for row in rows:
        print(f"{row['tool_id']} | {row['owner_organ']} | {row['combined_status']} | {row['tool_card_path']}")
    return 0


def cmd_check(index_path: Path, report_json: Path | None) -> int:
    result = check_registry(index_path)
    verdict = "PASS" if not result.errors else "BLOCKED_TOOL_REGISTRY_INVALID"
    payload = {
        "schema_version": "TOOL_REGISTRY_CHECK_REPORT_V0_1",
        "generated_at_utc": utc_now(),
        "index_path": str(index_path),
        "tool_count": result.tool_count,
        "errors": result.errors,
        "warnings": result.warnings,
        "verdict": verdict,
    }
    if report_json is not None:
        write_json(report_json, payload)
    print(json.dumps(payload, ensure_ascii=True, indent=2))
    return 0 if verdict == "PASS" else 1


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Read and validate Mechanicus Tool Registry.")
    sub = parser.add_subparsers(dest="command", required=True)

    p_list = sub.add_parser("list", help="List tools from TOOL_INDEX.json")
    p_list.add_argument("--index", required=True)
    p_list.add_argument("--as-json", action="store_true")

    p_check = sub.add_parser("check", help="Validate TOOL_INDEX.json and tool cards")
    p_check.add_argument("--index", required=True)
    p_check.add_argument("--report-json", default=None)
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    index_path = Path(args.index)
    if not index_path.exists():
        raise SystemExit(f"index not found: {index_path}")
    if args.command == "list":
        return cmd_list(index_path=index_path, as_json=bool(args.as_json))
    if args.command == "check":
        report_json = Path(args.report_json) if args.report_json else None
        return cmd_check(index_path=index_path, report_json=report_json)
    raise SystemExit(f"unsupported command: {args.command}")


if __name__ == "__main__":
    raise SystemExit(main())
