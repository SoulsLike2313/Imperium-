#!/usr/bin/env python3
"""Read-only CLI explorer for IMPERIUM tool registry."""

from __future__ import annotations

import argparse
import hashlib
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
ACTIVE_STATUSES = {"ACTIVE", "ACTIVE_NEEDS_SPECULUM"}


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Read-only explorer for TOOLS_MASTER_INDEX")
    parser.add_argument("--tools-index", required=True)
    parser.add_argument("--mode", required=True, choices=sorted(MODES))
    parser.add_argument("--tool-id", default="")
    parser.add_argument("--class", dest="tool_class", default="")
    parser.add_argument("--json-output", default="")
    parser.add_argument("--owner-report-output", default="")
    parser.add_argument("--readonly-assert", action="store_true")
    parser.add_argument("--verify-registry-hashes", action="store_true")
    return parser


def _sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest().lower()


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
        "legacy_or_blocked_count": len(
            [t for t in tools if t.get("status") in {"LEGACY_CANDIDATE", "LEGACY_QUARANTINE", "BLOCKED", "DEPRECATED"}]
        ),
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


def _infer_integrity_receipt_path(index_path: Path) -> Path:
    return index_path.parent.parent / "REGISTRY_INTEGRITY_RECEIPT.json"


def _load_integrity_receipt(index_path: Path) -> tuple[str, list[str], dict | None, Path]:
    receipt_path = _infer_integrity_receipt_path(index_path)
    warnings: list[str] = []
    status = "MISSING"
    payload: dict | None = None

    if not receipt_path.exists():
        warnings.append(f"registry integrity receipt missing: {receipt_path}")
        return status, warnings, payload, receipt_path

    try:
        payload = json.loads(receipt_path.read_text(encoding="utf-8"))
    except Exception as exc:  # pylint: disable=broad-except
        warnings.append(f"registry integrity receipt unreadable: {exc}")
        return "INVALID", warnings, None, receipt_path

    status = str(payload.get("verdict", payload.get("status", "UNKNOWN"))).upper()
    if status != "PASS":
        warnings.append(f"registry integrity receipt status is not PASS: {status}")
    return status, warnings, payload, receipt_path


def _resolve_tool_file(tool: dict, tools_root: Path) -> Path | None:
    rel = str(tool.get("relative_path_from_tools_root", "")).strip()
    abs_path = str(tool.get("absolute_path", "")).strip()

    candidates: list[Path] = []
    if rel:
        candidates.append((tools_root / rel).resolve())
    if abs_path:
        candidates.append(Path(abs_path).resolve())

    for candidate in candidates:
        if candidate.exists() and candidate.is_file():
            return candidate
    return None


def _verify_registry_hashes(data: dict) -> dict:
    tools_root = Path(str(data.get("tools_root", ""))).resolve()
    tools = data.get("tools", [])
    active = [t for t in tools if str(t.get("status", "")) in ACTIVE_STATUSES]

    checked = 0
    match = 0
    mismatch = 0
    missing = 0
    details: list[dict] = []

    for tool in active:
        tool_id = str(tool.get("tool_id", ""))
        registry_sha = str(tool.get("sha256", "")).lower().strip()
        path = _resolve_tool_file(tool, tools_root)
        checked += 1

        if path is None:
            missing += 1
            details.append(
                {
                    "tool_id": tool_id,
                    "status": tool.get("status", ""),
                    "path": "MISSING",
                    "registry_sha256": registry_sha,
                    "actual_sha256": "",
                    "match": "FAIL_MISSING_FILE",
                }
            )
            continue

        actual_sha = _sha256(path)
        if registry_sha == actual_sha:
            match += 1
            tool_match = "PASS"
        else:
            mismatch += 1
            tool_match = "FAIL_HASH_MISMATCH"

        details.append(
            {
                "tool_id": tool_id,
                "status": tool.get("status", ""),
                "path": str(path),
                "registry_sha256": registry_sha,
                "actual_sha256": actual_sha,
                "match": tool_match,
            }
        )

    return {
        "active_checked_count": checked,
        "active_hash_match_count": match,
        "active_hash_mismatch_count": mismatch,
        "missing_active_files_count": missing,
        "unknown_active_tools_count": 0,
        "details": details,
        "status": "PASS" if mismatch == 0 and missing == 0 else "FAIL",
    }


def main() -> int:
    args = build_parser().parse_args()

    verdict = "FAIL"
    bundle_ref = "N/A"

    try:
        readonly_assert = bool(args.readonly_assert)

        index_path = Path(args.tools_index).resolve()
        data = _load_index(index_path)
        tools = data.get("tools", [])

        integrity_status, integrity_warnings, integrity_payload, integrity_receipt_path = _load_integrity_receipt(index_path)
        hash_verify_payload = _verify_registry_hashes(data) if args.verify_registry_hashes else None

        output_payload: object
        if args.mode == "summary":
            payload = _summary(data)
            payload["registry_integrity_receipt_path"] = str(integrity_receipt_path)
            payload["registry_integrity_status"] = integrity_status
            payload["registry_integrity_warnings"] = integrity_warnings
            if integrity_payload is not None:
                payload["registry_integrity_receipt"] = integrity_payload
            if hash_verify_payload is not None:
                payload["registry_hash_verification"] = hash_verify_payload
            output_payload = payload
        elif args.mode == "details":
            output_payload = {
                "tools": tools,
                "registry_integrity_status": integrity_status,
                "registry_integrity_warnings": integrity_warnings,
                "registry_hash_verification": hash_verify_payload,
            }
        elif args.mode == "tool":
            if not args.tool_id:
                raise ValueError("--tool-id is required for mode=tool")
            matches = [t for t in tools if t.get("tool_id") == args.tool_id]
            if not matches:
                raise ValueError(f"tool_id not found: {args.tool_id}")
            tool = matches[0]
            tool_path = _resolve_tool_file(tool, Path(str(data.get("tools_root", ""))).resolve())
            tool_payload = dict(tool)
            tool_payload["registry_integrity_status"] = integrity_status
            tool_payload["registry_integrity_warnings"] = integrity_warnings
            if tool_path is not None:
                actual_sha = _sha256(tool_path)
                registry_sha = str(tool.get("sha256", "")).lower().strip()
                tool_payload["actual_sha256"] = actual_sha
                tool_payload["sha256_match"] = registry_sha == actual_sha
            else:
                tool_payload["actual_sha256"] = ""
                tool_payload["sha256_match"] = False
                tool_payload["tool_file_missing"] = True
            output_payload = tool_payload
        elif args.mode == "class":
            if not args.tool_class:
                raise ValueError("--class is required for mode=class")
            output_payload = {
                "tools": [t for t in tools if t.get("tool_class") == args.tool_class],
                "registry_integrity_status": integrity_status,
                "registry_integrity_warnings": integrity_warnings,
            }
        elif args.mode == "map":
            map_lines = [_render_map().rstrip()]  # preserve simple CLI map
            map_lines.append("")
            map_lines.append(f"REGISTRY_INTEGRITY_STATUS: {integrity_status}")
            if integrity_warnings:
                map_lines.append("REGISTRY_WARNINGS:")
                for warning in integrity_warnings:
                    map_lines.append(f"- {warning}")
            if hash_verify_payload is not None:
                map_lines.append(
                    "REGISTRY_HASH_VERIFY: "
                    f"{hash_verify_payload.get('status')} "
                    f"(checked={hash_verify_payload.get('active_checked_count')}, "
                    f"mismatch={hash_verify_payload.get('active_hash_mismatch_count')}, "
                    f"missing={hash_verify_payload.get('missing_active_files_count')})"
                )
            output_payload = {"flow_map": "\n".join(map_lines) + "\n"}
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
            "Показаны адреса, статусы и карта потока для Owner/PC/VM2 сценария с индикатором целостности реестра.",
            "Сетевые действия, VM2/THRONE доступ и автоматизация не выполнялись.",
            "Следующий шаг: использовать tool_id из реестра после Speculum go/no-go и registry integrity PASS.",
        ]
        if not readonly_assert:
            comments[0] = "Выполнен read-only обзор реестра без изменений; флаг --readonly-assert не был передан."

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
