#!/usr/bin/env python3
"""Select Mechanicus scripts for a route packet."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Build SCRIPT_SELECTION.json for route.")
    p.add_argument("--launch-card", required=True)
    p.add_argument("--script-registry", default=r"E:\IMPERIUM\ORGANS\MECHANICUS\SCRIPT_REGISTRY.json")
    p.add_argument("--output-dir", required=True)
    return p.parse_args()


def main() -> int:
    args = parse_args()
    launch = json.loads(Path(args.launch_card).read_text(encoding="utf-8"))
    registry = json.loads(Path(args.script_registry).read_text(encoding="utf-8"))
    out = Path(args.output_dir).resolve()
    out.mkdir(parents=True, exist_ok=True)

    selected_ids = [row.get("script_id") for row in registry.get("scripts", []) if row.get("script_id")]
    selected_ids = sorted(set(selected_ids))

    packet = {
        "task_id": launch.get("task_id"),
        "run_id": launch.get("run_id"),
        "stage_id": "MECHANICUS-STAGE-001",
        "selection_mode": "REGISTRY_CONTRACT_ONLY",
        "selected_script_ids": selected_ids,
        "notes": "Local-only, no VM2/THRONE/network/watchers.",
    }
    (out / "SCRIPT_SELECTION.json").write_text(json.dumps(packet, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(packet, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
