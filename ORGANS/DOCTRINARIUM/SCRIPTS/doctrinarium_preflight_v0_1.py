#!/usr/bin/env python3
"""Doctrinarium preflight gate v0.1 (read-only checks + runtime receipt)."""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
import sys
from typing import Any, Optional


SCHEMA_VERSION = "imperium.doctrinarium.preflight_receipt.v0_1"
EXPECTED_ORGAN_COUNT = 10
CANONICAL_ORGAN_ORDER = [
    "DOCTRINARIUM",
    "ADMINISTRATUM",
    "OFFICIO_AGENTIS",
    "ASTRONOMICON",
    "MECHANICUS",
    "INQUISITION",
    "THRONE",
    "CUSTODES",
    "STRATEGIUM",
    "SCHOLA_IMPERIALIS",
]
CRITICAL_INSIGHT_ORGANS = set(CANONICAL_ORGAN_ORDER[:4])


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def detect_repo_root(start: Optional[Path | str] = None) -> Path:
    """Detect repo root by walking upward until AGENTS.md and REGISTRY/ are found."""
    if start is None:
        current = Path(__file__).resolve().parent
    else:
        current = Path(start).expanduser().resolve()

    if current.is_file():
        current = current.parent

    for candidate in [current, *current.parents]:
        if (candidate / "AGENTS.md").is_file() and (candidate / "REGISTRY").is_dir():
            return candidate

    raise FileNotFoundError("Could not detect repository root (AGENTS.md + REGISTRY/ not found).")


def load_json_safely(path: Path) -> tuple[Any | None, list[str]]:
    """Read and parse JSON safely, returning payload and non-fatal issues."""
    issues: list[str] = []
    try:
        raw = path.read_text(encoding="utf-8")
    except FileNotFoundError:
        issues.append(f"missing_file:{path.as_posix()}")
        return None, issues
    except Exception as exc:  # pragma: no cover - defensive
        issues.append(f"read_error:{path.as_posix()}:{exc}")
        return None, issues

    try:
        return json.loads(raw), issues
    except Exception as exc:
        issues.append(f"invalid_json:{path.as_posix()}:{exc}")
        return None, issues


def _as_bool(value: Any) -> Optional[bool]:
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        lowered = value.strip().lower()
        if lowered in {"true", "yes", "1"}:
            return True
        if lowered in {"false", "no", "0"}:
            return False
    return None


def _as_int(value: Any) -> Optional[int]:
    if isinstance(value, bool):
        return None
    if isinstance(value, int):
        return value
    if isinstance(value, str):
        text = value.strip()
        if text.isdigit():
            try:
                return int(text)
            except Exception:
                return None
    return None


def _as_text(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, str):
        return value.strip()
    if isinstance(value, list):
        parts = [str(item).strip() for item in value if str(item).strip()]
        return "|".join(parts)
    if isinstance(value, dict):
        return json.dumps(value, ensure_ascii=False)
    return str(value)


def _safe_relative(path: Path, repo_root: Path) -> str:
    try:
        return path.resolve().relative_to(repo_root.resolve()).as_posix()
    except Exception:
        return path.as_posix()


def _extract_registry_entries(payload: Any) -> tuple[list[dict[str, Any]], list[str]]:
    warnings: list[str] = []

    if isinstance(payload, dict):
        organs = payload.get("organs")
        if isinstance(organs, list):
            entries = [item for item in organs if isinstance(item, dict)]
            if len(entries) != len(organs):
                warnings.append("registry_non_object_entries_ignored")
            return entries, warnings

        for fallback_key in ("items", "entries", "data"):
            candidate = payload.get(fallback_key)
            if isinstance(candidate, list):
                entries = [item for item in candidate if isinstance(item, dict)]
                if entries:
                    warnings.append(f"registry_fallback_key_used:{fallback_key}")
                    return entries, warnings

    if isinstance(payload, list):
        entries = [item for item in payload if isinstance(item, dict)]
        warnings.append("registry_root_list_used")
        return entries, warnings

    warnings.append("registry_structure_unsupported")
    return [], warnings


def _entry_organ_id(entry: dict[str, Any]) -> Optional[str]:
    for key in ("organ_id", "organ", "id"):
        value = entry.get(key)
        if isinstance(value, str) and value.strip():
            return value.strip().upper()

    path_value = entry.get("path")
    if isinstance(path_value, str) and path_value.strip():
        parts = [p for p in path_value.replace("\\", "/").split("/") if p]
        if len(parts) >= 2 and parts[-2].upper() == "ORGANS":
            return parts[-1].upper()

    return None


def _derive_maturity(status_data: dict[str, Any] | None, registry_entry: dict[str, Any] | None) -> str:
    if status_data is not None and "maturity" in status_data:
        text = _as_text(status_data.get("maturity"))
        if text:
            return text
    if registry_entry is not None:
        text = _as_text(registry_entry.get("maturity"))
        if text:
            return text
    if status_data is not None:
        text = _as_text(status_data.get("status"))
        if text:
            return text
    return "UNKNOWN"


def _derive_operational_status(status_data: dict[str, Any] | None, registry_entry: dict[str, Any] | None) -> str:
    if status_data is not None and "operational_status" in status_data:
        text = _as_text(status_data.get("operational_status"))
        if text:
            return text

    if registry_entry is not None:
        text = _as_text(registry_entry.get("operational_status"))
        if text:
            return text
        text = _as_text(registry_entry.get("status"))
        if text:
            return text

    if status_data is not None:
        text = _as_text(status_data.get("status"))
        if text:
            return text

    return "UNKNOWN"


def _derive_operational(
    status_data: dict[str, Any] | None,
    registry_entry: dict[str, Any] | None,
    operational_status: str,
    maturity: str,
) -> Optional[bool]:
    if status_data is not None:
        value = _as_bool(status_data.get("operational"))
        if value is not None:
            return value

    if registry_entry is not None:
        value = _as_bool(registry_entry.get("operational"))
        if value is not None:
            return value

    tokens = f"{operational_status} {maturity}".upper()
    if "NOT_OPERATIONAL" in tokens or "SCAFFOLD" in tokens or "NOT_IMPLEMENTED" in tokens:
        return False
    if "OPERATIONAL" in tokens and "NOT_OPERATIONAL" not in tokens:
        return True

    return None


def _derive_alive(status_data: dict[str, Any] | None, registry_entry: dict[str, Any] | None) -> Optional[bool]:
    if status_data is not None:
        value = _as_bool(status_data.get("alive"))
        if value is not None:
            return value
    if registry_entry is not None:
        value = _as_bool(registry_entry.get("alive"))
        if value is not None:
            return value
    return None


def _derive_can_accept_tasks(status_data: dict[str, Any] | None, registry_entry: dict[str, Any] | None) -> Optional[bool]:
    if status_data is not None:
        value = _as_bool(status_data.get("can_accept_tasks"))
        if value is not None:
            return value
    if registry_entry is not None:
        value = _as_bool(registry_entry.get("can_accept_tasks"))
        if value is not None:
            return value
    return None


def _derive_category(status_data: dict[str, Any] | None, registry_entry: dict[str, Any] | None) -> str:
    if status_data is not None:
        value = _as_text(status_data.get("category"))
        if value:
            return value
    if registry_entry is not None:
        value = _as_text(registry_entry.get("category"))
        if value:
            return value
    return "unknown"


def _is_scaffold(maturity: str, operational_status: str, status_raw: str) -> bool:
    tokens = f"{maturity} {operational_status} {status_raw}".upper()
    return (
        "LEVEL_0_SCAFFOLD" in tokens
        or "SCAFFOLD" in tokens
        or "NOT_IMPLEMENTED" in tokens
        or "CONTRACT_ONLY" in tokens
        or "READ_ROUTE_SCAFFOLD_PRESENT" in tokens
    )


def _load_verify_repo_signal(repo_root: Path) -> tuple[dict[str, Any], list[str]]:
    warnings: list[str] = []
    runtime_root = repo_root / ".imperium_runtime" / "verification_spine"
    report_path = runtime_root / "VERIFY_REPO_REPORT.json"
    verdict_path = runtime_root / "VERIFY_REPO_VERDICT.md"

    signal: dict[str, Any] = {
        "seen": False,
        "verdict": "UNKNOWN",
        "blockers": None,
        "warnings": None,
    }

    if report_path.is_file():
        payload, issues = load_json_safely(report_path)
        warnings.extend(issues)
        if isinstance(payload, dict):
            signal["seen"] = True
            signal["verdict"] = _as_text(payload.get("overall_verdict")) or "UNKNOWN"
            counts = payload.get("counts")
            if isinstance(counts, dict):
                signal["blockers"] = _as_int(counts.get("blockers"))
                signal["warnings"] = _as_int(counts.get("warnings"))
            return signal, warnings

        warnings.append("verify_repo_report_not_object")
        signal["seen"] = True
        return signal, warnings

    if verdict_path.is_file():
        signal["seen"] = True
        signal["verdict"] = "UNKNOWN"
        warnings.append("verify_repo_report_missing_using_verdict_markdown_only")
        return signal, warnings

    warnings.append("verify_repo_output_missing")
    return signal, warnings


def run_preflight(repo_root: Optional[Path | str] = None, task_id: Optional[str] = None) -> dict[str, Any]:
    blockers: list[str] = []
    warnings: list[str] = []
    honest_blockers: list[str] = []

    try:
        resolved_root = detect_repo_root(repo_root)
    except Exception as exc:
        reason = f"Repository root detection failed: {exc}"
        blockers.append(reason)
        honest_blockers.append(reason)
        return {
            "schema_version": SCHEMA_VERSION,
            "task_id": task_id,
            "timestamp_utc": utc_now_iso(),
            "repo_root": str(repo_root) if repo_root is not None else "",
            "overall_verdict": "BLOCKED",
            "reason": reason,
            "checks": {
                "organ_registry_loaded": False,
                "expected_organ_count": EXPECTED_ORGAN_COUNT,
                "registry_organ_count": None,
                "first_four_present": False,
                "all_organ_statuses_readable": False,
                "verify_repo_seen": False,
                "verify_repo_verdict": "UNKNOWN",
                "verify_repo_blockers": None,
                "verify_repo_warnings": None,
            },
            "organs": [],
            "clear_organs": [],
            "degraded_organs": [],
            "blocked_organs": [],
            "missing_organs": CANONICAL_ORGAN_ORDER[:],
            "not_operational_organs": [],
            "scaffold_organs": [],
            "blockers": blockers,
            "warnings": warnings,
            "honest_blockers": honest_blockers,
        }

    registry_path = resolved_root / "REGISTRY" / "ORGAN_REGISTRY.json"
    registry_payload, registry_issues = load_json_safely(registry_path)
    warnings.extend(registry_issues)

    registry_loaded = registry_payload is not None
    registry_entries: list[dict[str, Any]] = []

    if registry_loaded:
        extracted, extraction_warnings = _extract_registry_entries(registry_payload)
        registry_entries = extracted
        warnings.extend(extraction_warnings)
    else:
        msg = "organ_registry_unreadable"
        blockers.append(msg)
        honest_blockers.append(msg)

    canonical_order_valid = len(CANONICAL_ORGAN_ORDER) == EXPECTED_ORGAN_COUNT and len(set(CANONICAL_ORGAN_ORDER)) == EXPECTED_ORGAN_COUNT
    if not canonical_order_valid:
        msg = "canonical_order_definition_invalid"
        blockers.append(msg)
        honest_blockers.append(msg)

    registry_map: dict[str, dict[str, Any]] = {}
    for entry in registry_entries:
        organ_id = _entry_organ_id(entry)
        if organ_id and organ_id not in registry_map:
            registry_map[organ_id] = entry

    organs: list[dict[str, Any]] = []
    clear_organs: list[str] = []
    degraded_organs: list[str] = []
    blocked_organs: list[str] = []
    missing_organs: list[str] = []
    not_operational_organs: list[str] = []
    scaffold_organs: list[str] = []

    first_four_present = True
    all_organ_statuses_readable = True

    for index, organ_id in enumerate(CANONICAL_ORGAN_ORDER, start=1):
        critical = organ_id in CRITICAL_INSIGHT_ORGANS
        entry = registry_map.get(organ_id)
        issues: list[str] = []

        if entry is None:
            issues.append("missing_in_registry")

        path_text = _as_text((entry or {}).get("path")) or f"ORGANS/{organ_id}"
        organ_dir = resolved_root / Path(path_text)
        exists = organ_dir.is_dir()

        if not exists:
            issues.append("missing_on_filesystem")
            missing_organs.append(organ_id)

        status_path = organ_dir / "ORGAN_STATUS.json"
        status_payload, status_issues = load_json_safely(status_path)
        status_loaded = isinstance(status_payload, dict)

        if status_issues:
            issues.extend([f"status:{item}" for item in status_issues])

        if status_payload is not None and not isinstance(status_payload, dict):
            status_loaded = False
            issues.append("status_not_object")

        if not status_loaded:
            all_organ_statuses_readable = False

        if critical and (entry is None or not exists or not status_loaded):
            first_four_present = False
            blocked_organs.append(organ_id)
            if entry is None:
                msg = f"critical_organ_missing_in_registry:{organ_id}"
                blockers.append(msg)
                honest_blockers.append(msg)
            if not exists:
                msg = f"critical_organ_missing_on_filesystem:{organ_id}"
                blockers.append(msg)
                honest_blockers.append(msg)
            if not status_loaded:
                msg = f"critical_organ_status_unreadable:{organ_id}"
                blockers.append(msg)
                honest_blockers.append(msg)

        status_data = status_payload if isinstance(status_payload, dict) else None
        maturity = _derive_maturity(status_data, entry)
        operational_status = _derive_operational_status(status_data, entry)
        operational = _derive_operational(status_data, entry, operational_status, maturity)
        alive = _derive_alive(status_data, entry)
        can_accept_tasks = _derive_can_accept_tasks(status_data, entry)
        category = _derive_category(status_data, entry)

        if operational is False:
            not_operational_organs.append(organ_id)
        if can_accept_tasks is False:
            not_operational_organs.append(organ_id)

        status_raw = _as_text((status_data or {}).get("status"))
        if _is_scaffold(maturity, operational_status, status_raw):
            scaffold_organs.append(organ_id)

        if entry is None or not exists or not status_loaded:
            if organ_id not in blocked_organs:
                blocked_organs.append(organ_id)
        elif operational is True and (can_accept_tasks in (True, None)) and organ_id not in scaffold_organs:
            clear_organs.append(organ_id)
        else:
            degraded_organs.append(organ_id)

        organs.append(
            {
                "organ_id": organ_id,
                "canonical_order": index,
                "category": category,
                "path": path_text,
                "exists": exists,
                "status_loaded": status_loaded,
                "maturity": maturity,
                "operational": operational,
                "alive": alive,
                "can_accept_tasks": can_accept_tasks,
                "operational_status": operational_status,
                "critical_for_task_entry": critical,
                "issues": issues,
            }
        )

    # Deduplicate lists while preserving order.
    def _unique(items: list[str]) -> list[str]:
        seen: set[str] = set()
        result: list[str] = []
        for item in items:
            if item not in seen:
                seen.add(item)
                result.append(item)
        return result

    blocked_organs = _unique(blocked_organs)
    missing_organs = _unique(missing_organs)
    not_operational_organs = _unique(not_operational_organs)
    scaffold_organs = _unique(scaffold_organs)
    degraded_organs = _unique([item for item in degraded_organs if item not in blocked_organs])
    clear_organs = _unique([item for item in clear_organs if item not in blocked_organs and item not in degraded_organs])

    verify_signal, verify_warnings = _load_verify_repo_signal(resolved_root)
    warnings.extend(verify_warnings)

    verify_seen = bool(verify_signal.get("seen"))
    verify_verdict = _as_text(verify_signal.get("verdict")) or "UNKNOWN"
    verify_blockers = _as_int(verify_signal.get("blockers"))
    verify_warnings_count = _as_int(verify_signal.get("warnings"))

    if verify_seen:
        verdict_upper = verify_verdict.upper()
        if verify_blockers is not None and verify_blockers > 0:
            msg = f"verify_repo_blockers_detected:{verify_blockers}"
            blockers.append(msg)
            honest_blockers.append(msg)
        if verdict_upper in {"FAIL", "BLOCKED"}:
            msg = f"verify_repo_verdict_blocking:{verify_verdict}"
            blockers.append(msg)
            honest_blockers.append(msg)
    else:
        warnings.append("verify_repo_not_seen_degraded_by_policy")

    registry_organ_count = len(registry_entries) if registry_loaded else None

    if registry_organ_count != EXPECTED_ORGAN_COUNT:
        warnings.append(f"registry_organ_count_unexpected:{registry_organ_count}")

    checks = {
        "organ_registry_loaded": registry_loaded,
        "expected_organ_count": EXPECTED_ORGAN_COUNT,
        "registry_organ_count": registry_organ_count,
        "first_four_present": first_four_present,
        "all_organ_statuses_readable": all_organ_statuses_readable,
        "verify_repo_seen": verify_seen,
        "verify_repo_verdict": verify_verdict,
        "verify_repo_blockers": verify_blockers,
        "verify_repo_warnings": verify_warnings_count,
    }

    # Verdict evaluation.
    if blockers:
        overall_verdict = "BLOCKED"
        reason = "Critical preflight blockers detected."
    else:
        all_exist = all(item.get("exists") is True for item in organs)
        all_status_loaded = all(item.get("status_loaded") is True for item in organs)
        all_operational = all(item.get("operational") is True for item in organs)
        all_can_accept_ok = all(
            (item.get("can_accept_tasks") is True)
            or (item.get("can_accept_tasks") is None and item.get("operational") is True)
            for item in organs
        )
        verify_pass = verify_verdict.upper() == "PASS"

        clear_allowed = (
            registry_loaded
            and registry_organ_count == EXPECTED_ORGAN_COUNT
            and len(organs) == EXPECTED_ORGAN_COUNT
            and all_exist
            and all_status_loaded
            and all_operational
            and all_can_accept_ok
            and verify_pass
            and not scaffold_organs
        )

        if clear_allowed:
            overall_verdict = "CLEAR"
            reason = "All 10 organs are operational and verification spine is PASS."
        else:
            overall_verdict = "DEGRADED"
            reason = "System alive but not fully operational (scaffold/not-operational/warnings present)."

    report = {
        "schema_version": SCHEMA_VERSION,
        "task_id": task_id,
        "timestamp_utc": utc_now_iso(),
        "repo_root": resolved_root.as_posix(),
        "overall_verdict": overall_verdict,
        "reason": reason,
        "checks": checks,
        "organs": organs,
        "clear_organs": clear_organs,
        "degraded_organs": degraded_organs,
        "blocked_organs": blocked_organs,
        "missing_organs": missing_organs,
        "not_operational_organs": not_operational_organs,
        "scaffold_organs": scaffold_organs,
        "blockers": _unique(blockers),
        "warnings": _unique(warnings),
        "honest_blockers": _unique(honest_blockers),
    }

    return report


def write_preflight_outputs(report: dict[str, Any], repo_root: Path) -> dict[str, str]:
    runtime_dir = repo_root / ".imperium_runtime" / "doctrinarium" / "preflight"
    runtime_dir.mkdir(parents=True, exist_ok=True)

    receipt_path = runtime_dir / "PREFLIGHT_RECEIPT.json"
    report_path = runtime_dir / "PREFLIGHT_REPORT.json"
    verdict_path = runtime_dir / "PREFLIGHT_VERDICT.md"

    receipt_path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    checks = report.get("checks") if isinstance(report.get("checks"), dict) else {}
    verdict_lines = [
        "# DOCTRINARIUM PREFLIGHT VERDICT",
        "",
        f"- schema_version: {report.get('schema_version')}",
        f"- timestamp_utc: {report.get('timestamp_utc')}",
        f"- task_id: {report.get('task_id')}",
        f"- overall_verdict: {report.get('overall_verdict')}",
        f"- reason: {report.get('reason')}",
        f"- first_four_present: {checks.get('first_four_present')}",
        f"- registry_organ_count: {checks.get('registry_organ_count')}",
        f"- verify_repo_verdict: {checks.get('verify_repo_verdict')}",
        f"- verify_repo_blockers: {checks.get('verify_repo_blockers')}",
        f"- degraded_organs: {len(report.get('degraded_organs', []))}",
        f"- blocked_organs: {len(report.get('blocked_organs', []))}",
        f"- warnings: {len(report.get('warnings', []))}",
        f"- blockers: {len(report.get('blockers', []))}",
        "",
    ]
    verdict_path.write_text("\n".join(verdict_lines), encoding="utf-8")

    return {
        "receipt": _safe_relative(receipt_path, repo_root),
        "report": _safe_relative(report_path, repo_root),
        "verdict": _safe_relative(verdict_path, repo_root),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Run Doctrinarium preflight v0.1")
    parser.add_argument("--task-id", default=None, help="Optional task identifier")
    parser.add_argument("--repo-root", default=None, help="Optional explicit repository root")
    args = parser.parse_args()

    report = run_preflight(repo_root=args.repo_root, task_id=args.task_id)

    try:
        resolved_root = Path(report.get("repo_root") or detect_repo_root(args.repo_root))
    except Exception as exc:
        print(json.dumps({"overall_verdict": "BLOCKED", "error": str(exc)}, ensure_ascii=False, indent=2))
        return 2

    outputs = write_preflight_outputs(report, resolved_root)

    summary = {
        "schema_version": report.get("schema_version"),
        "overall_verdict": report.get("overall_verdict"),
        "reason": report.get("reason"),
        "blockers": len(report.get("blockers", [])),
        "warnings": len(report.get("warnings", [])),
        "paths": outputs,
    }
    print(json.dumps(summary, ensure_ascii=False, indent=2))

    if report.get("overall_verdict") == "BLOCKED":
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
