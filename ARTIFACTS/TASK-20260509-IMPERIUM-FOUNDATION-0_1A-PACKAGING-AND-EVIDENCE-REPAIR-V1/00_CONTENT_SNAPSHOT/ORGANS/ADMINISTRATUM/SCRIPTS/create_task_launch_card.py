#!/usr/bin/env python3
"""Create TASK_LAUNCH_CARD.json from simple input JSON (scaffold 0.1)."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parent
ADMIN_ROOT = SCRIPT_DIR.parent
DEFAULT_TASKS_ROOT = ADMIN_ROOT / "TASKS"


def _safe_within(base: Path, candidate: Path) -> Path:
    resolved_base = base.resolve()
    resolved_candidate = candidate.resolve()
    resolved_candidate.relative_to(resolved_base)
    return resolved_candidate


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Create TASK_LAUNCH_CARD.json in Administratum TASKS root.")
    p.add_argument("--input-json", required=True, help="Path to simple JSON source for launch card.")
    p.add_argument("--task-id", default="", help="Override task_id from input JSON.")
    p.add_argument("--tasks-root", default=str(DEFAULT_TASKS_ROOT))
    p.add_argument("--output-task-folder", default="", help="Optional explicit task folder name.")
    return p.parse_args()


def main() -> int:
    args = parse_args()
    input_path = Path(args.input_json).resolve()
    tasks_root = Path(args.tasks_root).resolve()

    if not input_path.exists():
        raise FileNotFoundError(f"Input JSON not found: {input_path}")

    payload = json.loads(input_path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError("Input JSON must be an object.")

    task_id = args.task_id.strip() or str(payload.get("task_id", "")).strip()
    if not task_id:
        raise ValueError("task_id is required in input or --task-id.")

    folder_name = args.output_task_folder.strip() or task_id
    out_dir = _safe_within(tasks_root, tasks_root / folder_name)
    out_dir.mkdir(parents=True, exist_ok=True)

    payload["task_id"] = task_id
    payload["generated_by"] = "create_task_launch_card.py"
    payload["status"] = payload.get("status", "READ_ROUTE_SCAFFOLD_0_1")
    payload.setdefault("execution_mode", "NOT_IMPLEMENTED")

    out_path = out_dir / "TASK_LAUNCH_CARD.json"
    out_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    print(f"created: {out_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

