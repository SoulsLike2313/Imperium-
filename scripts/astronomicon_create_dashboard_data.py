#!/usr/bin/env python3
"""Create Astronomicon dashboard data JSON files from active state and registries."""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List


def repo_root() -> Path:
    return Path(__file__).resolve().parents[1]


def read_json(path: Path, default: Any) -> Any:
    if not path.exists():
        return default
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return default


def list_json_objects(folder: Path) -> List[Dict[str, Any]]:
    if not folder.exists():
        return []
    objects: List[Dict[str, Any]] = []
    for path in sorted(folder.glob("*.json")):
        try:
            obj = json.loads(path.read_text(encoding="utf-8"))
        except Exception:
            continue
        obj["_source_file"] = str(path)
        objects.append(obj)
    return objects


def write_json(path: Path, payload: Dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Generate Astronomicon dashboard data seed/current files.")
    parser.add_argument(
        "--out-dir",
        default=str(repo_root() / "ORGANS" / "ASTRONOMICON" / "DASHBOARD_DATA"),
        help="Output directory for dashboard data JSON files",
    )
    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()

    root = repo_root()
    out_dir = Path(args.out_dir).resolve()
    astro_root = (root / "ORGANS" / "ASTRONOMICON").resolve()

    try:
        out_dir.relative_to(astro_root)
    except ValueError:
        print(f"FAIL: output directory outside Astronomicon scope: {out_dir}")
        return 2

    active_state_path = root / "ORGANS" / "ASTRONOMICON" / "ACTIVE_STATE" / "current.json"
    active_state = read_json(
        active_state_path,
        {
            "schema_version": "astronomicon_active_state_v0_1",
            "active_general_task": None,
            "active_task": None,
            "active_stage": None,
            "active_run": None,
            "status": "NO_ACTIVE_GENERAL_TASK",
            "ready_for_new_general_task_intake": True,
            "ready_for_agent": False,
            "vm2_status": "DEFERRED_OFFLINE",
        },
    )

    gt_objects = list_json_objects(root / "ORGANS" / "ASTRONOMICON" / "REGISTRY" / "GENERAL_TASKS")
    candidate_objects = list_json_objects(
        root / "ORGANS" / "ASTRONOMICON" / "REGISTRY" / "TASKS" / "CANDIDATES"
    )
    stage_objects = list_json_objects(root / "ORGANS" / "ASTRONOMICON" / "REGISTRY" / "STAGES")

    now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    has_active = active_state.get("active_general_task") is not None

    active_state_dash = {
        "schema_version": "astronomicon_dashboard_active_state_v0_1",
        "last_generated_at_utc": now,
        "status": active_state.get("status", "NO_ACTIVE_GENERAL_TASK"),
        "active_general_task": active_state.get("active_general_task"),
        "active_task": active_state.get("active_task"),
        "active_stage": active_state.get("active_stage"),
        "active_run": active_state.get("active_run"),
        "ready_for_new_general_task_intake": bool(active_state.get("ready_for_new_general_task_intake", True)),
        "ready_for_agent": bool(active_state.get("ready_for_agent", False)),
        "vm2_status": active_state.get("vm2_status", "DEFERRED_OFFLINE"),
        "stale_status": "CURRENT",
        "fake_green_guard": "NO_ACTIVE_GENERAL_TASK_IF_NULL_POINTERS",
    }

    general_task_current = {
        "schema_version": "astronomicon_dashboard_general_task_current_v0_1",
        "last_generated_at_utc": now,
        "status": "NONE" if not has_active else "ACTIVE_PRESENT",
        "active_general_task": active_state.get("active_general_task"),
        "items_found_in_registry": len(gt_objects),
        "current": None,
    }

    task_candidates = {
        "schema_version": "astronomicon_dashboard_task_candidates_v0_1",
        "last_generated_at_utc": now,
        "count": len(candidate_objects),
        "items": candidate_objects,
    }

    selected_task = {
        "schema_version": "astronomicon_dashboard_selected_task_v0_1",
        "last_generated_at_utc": now,
        "selected_task_id": None,
        "selected_task": None,
        "status": "NO_SELECTION",
    }

    stage_map = {
        "schema_version": "astronomicon_dashboard_stage_map_v0_1",
        "last_generated_at_utc": now,
        "stage_count": len(stage_objects),
        "stages": stage_objects,
        "status": "EMPTY" if not stage_objects else "AVAILABLE",
    }

    speculum_review_state = {
        "schema_version": "astronomicon_dashboard_speculum_review_state_v0_1",
        "last_generated_at_utc": now,
        "task_review_status": "NOT_REQUESTED",
        "stage_review_status": "NOT_REQUESTED",
        "last_task_review_import": None,
        "last_stage_review_import": None,
    }

    blockers = {
        "schema_version": "astronomicon_dashboard_blockers_v0_1",
        "last_generated_at_utc": now,
        "items": [
            "NO_ACTIVE_GENERAL_TASK" if not has_active else "NONE",
            "REGISTER_BUTTON_DISABLED_UNTIL_VALIDATED_FLOW",
            "SPECULUM_IMPORT_NOT_FULLY_IMPLEMENTED",
        ],
    }

    workbench_meta = {
        "schema_version": "astronomicon_dashboard_workbench_meta_v0_1",
        "last_generated_at_utc": now,
        "status": "NO_ACTIVE_GENERAL_TASK" if not has_active else "ACTIVE_FLOW_IN_PROGRESS",
        "register_button_enabled": False,
        "decompose_button_enabled": has_active,
        "stale_status": "CURRENT",
        "data_source": "BACKEND_GENERATED_JSON",
    }

    write_json(out_dir / "active_state.json", active_state_dash)
    write_json(out_dir / "general_task_current.json", general_task_current)
    write_json(out_dir / "task_candidates.json", task_candidates)
    write_json(out_dir / "selected_task.json", selected_task)
    write_json(out_dir / "stage_map.json", stage_map)
    write_json(out_dir / "speculum_review_state.json", speculum_review_state)
    write_json(out_dir / "blockers.json", blockers)
    write_json(out_dir / "workbench_meta.json", workbench_meta)

    print("PASS: ASTRONOMICON_DASHBOARD_DATA_GENERATED")
    print(f"OUT_DIR: {out_dir}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
