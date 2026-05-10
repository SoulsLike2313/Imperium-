#!/usr/bin/env python3
"""Create repair task stub from parent task + blockers (scaffold 0.1)."""

from __future__ import annotations

import argparse
import json
from datetime import datetime
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
    p = argparse.ArgumentParser(description="Create repair branch task stub only (no execution).")
    p.add_argument("--parent-task-id", required=True)
    p.add_argument("--new-task-id", required=True)
    p.add_argument("--blocker", action="append", default=[], help="Blocker line (repeatable).")
    p.add_argument("--tasks-root", default=str(DEFAULT_TASKS_ROOT))
    return p.parse_args()


def _load_json_if_exists(path: Path) -> dict | None:
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> int:
    args = parse_args()
    tasks_root = Path(args.tasks_root).resolve()
    parent_dir = _safe_within(tasks_root, tasks_root / args.parent_task_id)
    child_dir = _safe_within(tasks_root, tasks_root / args.new_task_id)
    child_dir.mkdir(parents=True, exist_ok=True)

    now = datetime.now().isoformat(timespec="seconds")
    stub = {
        "task_id": args.new_task_id,
        "parent_task_id": args.parent_task_id,
        "created_at_local": now,
        "status": "READ_ROUTE_SCAFFOLD_0_1",
        "repair_mode": "NOT_IMPLEMENTED",
        "blockers": args.blocker,
        "next_action": "Owner/Speculum review required before execution.",
    }
    stub_path = child_dir / "REPAIR_BRANCH_STUB.json"
    stub_path.write_text(json.dumps(stub, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    parent_chain_path = parent_dir / "TASK_VERSION_CHAIN.json"
    parent_chain = _load_json_if_exists(parent_chain_path)
    if parent_chain is not None:
        chain = parent_chain.get("chain", [])
        if not isinstance(chain, list):
            chain = []
        chain.append(
            {
                "task_id": args.new_task_id,
                "relation": "REPAIR_BRANCH",
                "created_at_local": now,
            }
        )
        parent_chain["chain"] = chain
        parent_chain["updated_at_local"] = now
        parent_chain_path.write_text(json.dumps(parent_chain, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    child_chain = {
        "task_id": args.new_task_id,
        "chain": [
            {
                "task_id": args.parent_task_id,
                "relation": "PARENT",
                "noted_at_local": now,
            },
            {
                "task_id": args.new_task_id,
                "relation": "SELF",
                "noted_at_local": now,
            },
        ],
    }
    (child_dir / "TASK_VERSION_CHAIN.json").write_text(
        json.dumps(child_chain, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )

    print(f"created: {stub_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

