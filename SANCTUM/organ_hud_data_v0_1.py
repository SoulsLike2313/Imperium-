#!/usr/bin/env python3
"""Read-only Sanctum HUD data service for organ state aggregation (v0.1)."""

from __future__ import annotations

from datetime import datetime, timezone
import json
from pathlib import Path
import sys
from typing import Any, Optional


SCHEMA_VERSION = "imperium.sanctum.organ_hud_data.v0_1"
EXPECTED_ORGAN_COUNT = 10

CANONICAL_ORDER = [
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
CANONICAL_ORDER_MAP = {organ_id: idx + 1 for idx, organ_id in enumerate(CANONICAL_ORDER)}
INSIGHT_ORGANS = set(CANONICAL_ORDER[:4])


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def detect_repo_root(start: Optional[Path | str] = None) -> Path:
    """Detect repository root by walking up to a folder containing AGENTS.md and REGISTRY/."""
    if start is None:
        current = Path(__file__).resolve().parent
    else:
        current = Path(start).expanduser().resolve()

    if current.is_file():
        current = current.parent

    for candidate in [current, *current.parents]:
        if (candidate / "AGENTS.md").is_file() and (candidate / "REGISTRY").is_dir():
            return candidate

    raise FileNotFoundError("Could not detect IMPERIUM repo root from provided start path.")


def _load_json(path: Path) -> tuple[Any | None, str | None]:
    try:
        raw = path.read_text(encoding="utf-8")
    except FileNotFoundError:
        return None, f"Missing file: {path.as_posix()}"
    except Exception as exc:  # pragma: no cover - defensive
        return None, f"Failed reading file {path.as_posix()}: {exc}"

    try:
        return json.loads(raw), None
    except Exception as exc:
        return None, f"Invalid JSON in {path.as_posix()}: {exc}"


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
    if isinstance(value, str) and value.strip().isdigit():
        try:
            return int(value.strip())
        except Exception:
            return None
    return None


def _status_note_text(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, str):
        return value
    if isinstance(value, list):
        parts = [str(item).strip() for item in value if str(item).strip()]
        return "; ".join(parts)
    if isinstance(value, dict):
        return json.dumps(value, ensure_ascii=False)
    return str(value)


def _extract_registry_organs(payload: Any) -> tuple[list[dict[str, Any]], list[str]]:
    warnings: list[str] = []

    if isinstance(payload, dict):
        organs_value = payload.get("organs")
        if isinstance(organs_value, list):
            items = [item for item in organs_value if isinstance(item, dict)]
            if len(items) != len(organs_value):
                warnings.append("Registry organs list contains non-object entries; ignored non-object items.")
            return items, warnings

        for key in ("items", "entries", "data"):
            candidate = payload.get(key)
            if isinstance(candidate, list):
                items = [item for item in candidate if isinstance(item, dict)]
                if items:
                    warnings.append(f"Registry used fallback key '{key}' instead of 'organs'.")
                    return items, warnings

    if isinstance(payload, list):
        items = [item for item in payload if isinstance(item, dict)]
        warnings.append("Registry root is list; treated as organ entries list.")
        return items, warnings

    warnings.append("Registry structure is unsupported; no organ entries extracted.")
    return [], warnings


def _infer_operational(
    status_data: dict[str, Any] | None,
    entry: dict[str, Any],
    maturity: str,
    operational_status: str,
) -> bool:
    if status_data is not None:
        status_operational = _as_bool(status_data.get("operational"))
        if status_operational is not None:
            return status_operational

    entry_operational = _as_bool(entry.get("operational"))
    if entry_operational is not None:
        return entry_operational

    if isinstance(operational_status, str) and operational_status.strip().upper() == "OPERATIONAL":
        return True

    if "SCAFFOLD" in maturity.upper():
        return False

    return False


def _normalize_maturity(status_data: dict[str, Any] | None, entry: dict[str, Any]) -> str:
    status_maturity = None
    if status_data is not None:
        status_maturity = status_data.get("maturity")
        if isinstance(status_maturity, list):
            text_items = [str(item).strip() for item in status_maturity if str(item).strip()]
            if text_items:
                return "|".join(text_items)
        if isinstance(status_maturity, str) and status_maturity.strip():
            return status_maturity.strip()

    entry_maturity = entry.get("maturity")
    if isinstance(entry_maturity, list):
        text_items = [str(item).strip() for item in entry_maturity if str(item).strip()]
        if text_items:
            return "|".join(text_items)
    if isinstance(entry_maturity, str) and entry_maturity.strip():
        return entry_maturity.strip()

    for fallback_key in ("status", "operational_status"):
        value = entry.get(fallback_key)
        if isinstance(value, str) and value.strip():
            return value.strip()

    if status_data is not None:
        status_value = status_data.get("status")
        if isinstance(status_value, str) and status_value.strip():
            return status_value.strip()

    return "UNKNOWN"


def _is_scaffold(maturity: str, operational_status: str, status_raw: str) -> bool:
    tokens = " ".join([maturity or "", operational_status or "", status_raw or ""]).upper()
    return ("SCAFFOLD" in tokens) or ("NOT_IMPLEMENTED" in tokens)


def _safe_relative(path: Path, root: Path) -> str:
    try:
        return path.resolve().relative_to(root.resolve()).as_posix()
    except Exception:
        return path.as_posix()


def _find_latest_current_stage(tasks_root: Path) -> tuple[dict[str, Any] | None, dict[str, Any] | None, list[str]]:
    warnings: list[str] = []
    if not tasks_root.is_dir():
        return None, None, warnings

    candidates: list[Path] = []
    patterns = [
        "*/CURRENT_STAGE.json",
        "*/*/CURRENT_STAGE.json",
        "*/*/*/CURRENT_STAGE.json",
    ]
    for pattern in patterns:
        try:
            candidates.extend(list(tasks_root.glob(pattern)))
        except Exception as exc:
            warnings.append(f"Failed glob on TASKS with pattern '{pattern}': {exc}")

    # De-duplicate while preserving order
    unique: list[Path] = []
    seen: set[str] = set()
    for candidate in candidates:
        key = str(candidate.resolve())
        if key not in seen and candidate.is_file():
            seen.add(key)
            unique.append(candidate)

    if not unique:
        return None, None, warnings

    latest = max(unique, key=lambda p: p.stat().st_mtime)
    stage_data, stage_error = _load_json(latest)
    if stage_error is not None:
        warnings.append(stage_error)
        return None, None, warnings

    if not isinstance(stage_data, dict):
        warnings.append(f"CURRENT_STAGE payload is not JSON object: {latest.as_posix()}")
        return None, None, warnings

    stat = latest.stat()
    stage_payload = {
        "path": latest.as_posix(),
        "modified_at_utc": datetime.fromtimestamp(stat.st_mtime, tz=timezone.utc).isoformat(),
        "data": stage_data,
    }

    task_id = stage_data.get("task_id")
    active_task: dict[str, Any] = {
        "source": "ORGANS/ASTRONOMICON/TASKS",
        "task_id": task_id if isinstance(task_id, str) else None,
        "current_stage_path": latest.as_posix(),
    }
    if stage_payload["modified_at_utc"]:
        active_task["updated_at_utc"] = stage_payload["modified_at_utc"]

    return active_task, stage_payload, warnings


def _load_latest_preflight(repo_root: Path) -> tuple[dict[str, Any] | None, list[str]]:
    warnings: list[str] = []
    path = repo_root / ".imperium_runtime" / "doctrinarium" / "preflight" / "PREFLIGHT_RECEIPT.json"
    if not path.exists():
        return None, warnings

    payload, error = _load_json(path)
    if error is not None:
        warnings.append(error)
        return None, warnings

    if not isinstance(payload, dict):
        warnings.append(f"Preflight receipt is not JSON object: {path.as_posix()}")
        return None, warnings

    return {
        "path": _safe_relative(path, repo_root),
        "loaded": True,
        "verdict": payload.get("verdict"),
        "data": payload,
    }, warnings


def get_hud_data(repo_root: Optional[Path | str] = None) -> dict[str, Any]:
    warnings: list[str] = []

    try:
        resolved_root = detect_repo_root(repo_root)
    except Exception as exc:
        return {
            "schema_version": SCHEMA_VERSION,
            "repo_root": str(repo_root) if repo_root is not None else "",
            "generated_at_utc": utc_now_iso(),
            "registry": {
                "loaded": False,
                "path": "REGISTRY/ORGAN_REGISTRY.json",
                "organ_count": 0,
                "warnings": [f"repo_root_detection_failed: {exc}"],
            },
            "system_health": {
                "verdict": "UNKNOWN",
                "reason": "Repository root detection failed.",
                "operational_count": 0,
                "not_operational_count": 0,
                "scaffold_count": 0,
                "missing_status_count": 0,
                "organ_count": 0,
                "expected_organ_count": EXPECTED_ORGAN_COUNT,
                "honest_blockers": [f"repo_root_detection_failed: {exc}"],
            },
            "organs": [],
            "active_task": None,
            "current_stage": None,
            "latest_preflight": None,
            "warnings": [f"repo_root_detection_failed: {exc}"],
        }

    registry_path = resolved_root / "REGISTRY" / "ORGAN_REGISTRY.json"
    registry_payload, registry_error = _load_json(registry_path)
    registry_warnings: list[str] = []
    registry_loaded = registry_error is None

    registry_entries: list[dict[str, Any]] = []
    if registry_error is not None:
        registry_warnings.append(registry_error)
    else:
        registry_entries, extracted_warnings = _extract_registry_organs(registry_payload)
        registry_warnings.extend(extracted_warnings)
        if not registry_entries:
            registry_loaded = False
            registry_warnings.append("No organ entries extracted from registry payload.")

    warnings.extend(registry_warnings)

    if not registry_entries:
        # Fallback to canonical order with expected paths
        for organ_id in CANONICAL_ORDER:
            registry_entries.append(
                {
                    "organ_id": organ_id,
                    "name": organ_id.title().replace("_", " "),
                    "canonical_order": CANONICAL_ORDER_MAP[organ_id],
                    "path": f"ORGANS/{organ_id}",
                    "category": "unknown",
                }
            )

    normalized_organs: list[dict[str, Any]] = []

    for entry in registry_entries:
        organ_id_raw = entry.get("organ_id") or entry.get("organ") or entry.get("id") or ""
        organ_id = str(organ_id_raw).strip().upper()
        if not organ_id:
            warnings.append(f"Registry entry without organ_id ignored: {entry}")
            continue

        path_value = entry.get("path")
        if isinstance(path_value, str) and path_value.strip():
            rel_path = path_value.strip().replace("\\", "/")
        else:
            rel_path = f"ORGANS/{organ_id}"

        organ_root = (resolved_root / rel_path).resolve()
        exists = organ_root.exists() and organ_root.is_dir()
        issues: list[str] = []
        if not exists:
            issues.append(f"Organ directory missing: {rel_path}")

        status_file = organ_root / "ORGAN_STATUS.json"
        status_loaded = False
        status_payload: dict[str, Any] | None = None
        if status_file.exists():
            payload, error = _load_json(status_file)
            if error is not None:
                issues.append(error)
            elif isinstance(payload, dict):
                status_loaded = True
                status_payload = payload
            else:
                issues.append(f"ORGAN_STATUS must be JSON object: {status_file.as_posix()}")
        else:
            issues.append(f"Missing ORGAN_STATUS.json: {rel_path}/ORGAN_STATUS.json")

        canonical_order = _as_int(entry.get("canonical_order"))
        if canonical_order is None:
            canonical_order = CANONICAL_ORDER_MAP.get(organ_id)
        if canonical_order is None:
            canonical_order = 999

        if status_payload is not None:
            status_order = _as_int(status_payload.get("canonical_order"))
            if status_order is not None:
                canonical_order = status_order

        name = entry.get("name")
        if not isinstance(name, str) or not name.strip():
            name = organ_id.title().replace("_", " ")
        if status_payload is not None and isinstance(status_payload.get("name"), str):
            name = status_payload.get("name")

        category = entry.get("category") if isinstance(entry.get("category"), str) else "unknown"
        if status_payload is not None and isinstance(status_payload.get("category"), str):
            category = status_payload.get("category")

        maturity = _normalize_maturity(status_payload, entry)

        operational_status = entry.get("operational_status")
        if not isinstance(operational_status, str) or not operational_status.strip():
            status_text = entry.get("status")
            if isinstance(status_text, str) and status_text.strip():
                operational_status = status_text.strip()
            else:
                operational_status = "NOT_OPERATIONAL"
        if status_payload is not None and isinstance(status_payload.get("operational_status"), str):
            operational_status = status_payload.get("operational_status")

        status_raw = ""
        if status_payload is not None and isinstance(status_payload.get("status"), str):
            status_raw = status_payload.get("status")
        elif isinstance(entry.get("status"), str):
            status_raw = entry.get("status")

        operational = _infer_operational(status_payload, entry, maturity, operational_status)

        alive = None
        can_accept_tasks = None
        if status_payload is not None:
            alive = _as_bool(status_payload.get("alive"))
            can_accept_tasks = _as_bool(status_payload.get("can_accept_tasks"))
        if alive is None:
            alive = _as_bool(entry.get("alive"))
        if can_accept_tasks is None:
            can_accept_tasks = _as_bool(entry.get("can_accept_tasks"))

        note_source = None
        if status_payload is not None:
            if "status_note" in status_payload:
                note_source = status_payload.get("status_note")
            elif "notes" in status_payload:
                note_source = status_payload.get("notes")
        status_note = _status_note_text(note_source)

        normalized_organs.append(
            {
                "organ_id": organ_id,
                "name": name,
                "canonical_order": canonical_order,
                "category": category,
                "path": rel_path,
                "exists": bool(exists),
                "status_loaded": status_loaded,
                "maturity": maturity,
                "operational": operational,
                "alive": alive,
                "can_accept_tasks": can_accept_tasks,
                "operational_status": operational_status,
                "issues": issues,
                "status_note": status_note,
                "_is_scaffold": _is_scaffold(maturity, operational_status, status_raw),
            }
        )

    normalized_organs.sort(key=lambda item: (item.get("canonical_order", 999), item.get("organ_id", "")))

    organ_count = len(normalized_organs)
    operational_count = sum(1 for item in normalized_organs if item.get("operational") is True)
    not_operational_count = sum(1 for item in normalized_organs if item.get("operational") is not True)
    scaffold_count = sum(1 for item in normalized_organs if item.get("_is_scaffold"))
    missing_status_count = sum(1 for item in normalized_organs if not item.get("status_loaded"))

    honest_blockers: list[str] = []

    # Insight organs gate
    insight_missing = []
    for organ_id in INSIGHT_ORGANS:
        item = next((entry for entry in normalized_organs if entry.get("organ_id") == organ_id), None)
        if item is None:
            insight_missing.append(f"{organ_id}: missing from registry-derived organ list")
            continue
        if not item.get("exists"):
            insight_missing.append(f"{organ_id}: missing organ directory")
        if not item.get("status_loaded"):
            insight_missing.append(f"{organ_id}: missing or unreadable ORGAN_STATUS.json")

    if organ_count != EXPECTED_ORGAN_COUNT:
        honest_blockers.append(
            f"Organ count mismatch: expected {EXPECTED_ORGAN_COUNT}, got {organ_count}."
        )

    if missing_status_count > 0:
        honest_blockers.append(f"Missing/unreadable ORGAN_STATUS files: {missing_status_count}.")

    if scaffold_count > 0:
        honest_blockers.append(f"Scaffold/not-implemented organs detected: {scaffold_count}.")

    if not_operational_count > 0:
        honest_blockers.append(f"Not operational organs: {not_operational_count}.")

    if insight_missing:
        honest_blockers.extend(insight_missing)

    if not registry_loaded:
        verdict = "UNKNOWN"
        reason = "Registry could not be loaded or parsed reliably."
    elif insight_missing:
        verdict = "BLOCKED"
        reason = "One or more insight organs are missing or have no valid ORGAN_STATUS."
    elif organ_count == EXPECTED_ORGAN_COUNT and missing_status_count == 0 and operational_count == EXPECTED_ORGAN_COUNT:
        verdict = "CLEAR"
        reason = "All expected organs exist with status and are operational."
    else:
        verdict = "DEGRADED"
        reason = "System has scaffold/not-operational organs or incomplete readiness."

    active_task = None
    current_stage = None
    task_warnings: list[str] = []
    tasks_root = resolved_root / "ORGANS" / "ASTRONOMICON" / "TASKS"
    maybe_active_task, maybe_current_stage, task_warnings = _find_latest_current_stage(tasks_root)
    if maybe_active_task is not None:
        # Convert absolute path into repo-relative path for portability.
        stage_path = maybe_active_task.get("current_stage_path")
        if isinstance(stage_path, str):
            maybe_active_task["current_stage_path"] = _safe_relative(Path(stage_path), resolved_root)
        active_task = maybe_active_task
    if maybe_current_stage is not None:
        maybe_current_stage["path"] = _safe_relative(Path(maybe_current_stage["path"]), resolved_root)
        current_stage = maybe_current_stage

    latest_preflight, preflight_warnings = _load_latest_preflight(resolved_root)

    warnings.extend(task_warnings)
    warnings.extend(preflight_warnings)

    # Remove internal helper key before returning.
    for item in normalized_organs:
        item.pop("_is_scaffold", None)

    return {
        "schema_version": SCHEMA_VERSION,
        "repo_root": str(resolved_root),
        "generated_at_utc": utc_now_iso(),
        "registry": {
            "loaded": bool(registry_loaded),
            "path": "REGISTRY/ORGAN_REGISTRY.json",
            "organ_count": organ_count,
            "warnings": registry_warnings,
        },
        "system_health": {
            "verdict": verdict,
            "reason": reason,
            "operational_count": operational_count,
            "not_operational_count": not_operational_count,
            "scaffold_count": scaffold_count,
            "missing_status_count": missing_status_count,
            "organ_count": organ_count,
            "expected_organ_count": EXPECTED_ORGAN_COUNT,
            "honest_blockers": honest_blockers,
        },
        "organs": normalized_organs,
        "active_task": active_task,
        "current_stage": current_stage,
        "latest_preflight": latest_preflight,
        "warnings": warnings,
    }


def main() -> int:
    data = get_hud_data()
    print(json.dumps(data, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
