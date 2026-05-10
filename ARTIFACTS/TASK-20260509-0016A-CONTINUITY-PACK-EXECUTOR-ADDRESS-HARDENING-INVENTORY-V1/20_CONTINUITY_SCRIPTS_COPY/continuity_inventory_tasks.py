#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path
from typing import Any, Dict, List

from continuity_common import detect_task_id, now_utc, write_json, write_text


def main() -> int:
    parser = argparse.ArgumentParser(description="Inventory all task folders across normal and manual layers")
    parser.add_argument("--imperium-root", required=True)
    parser.add_argument("--output-json", required=True)
    parser.add_argument("--output-md", required=True)
    args = parser.parse_args()

    root = Path(args.imperium_root).resolve()
    artifacts_root = root / "ARTIFACTS"
    manual_root = artifacts_root / "_MANUAL_PROOFS"
    records: List[Dict[str, Any]] = []

    if artifacts_root.exists():
        for child in sorted(artifacts_root.iterdir(), key=lambda p: p.name.lower()):
            if not child.is_dir() or child.name == "_MANUAL_PROOFS":
                continue
            tid = detect_task_id(child.name)
            records.append(
                {
                    "layer": "NORMAL_ARTIFACT",
                    "folder_name": child.name,
                    "path": str(child),
                    "task_id": tid,
                    "modified_time": child.stat().st_mtime,
                }
            )

    if manual_root.exists():
        for child in sorted(manual_root.iterdir(), key=lambda p: p.name.lower()):
            if not child.is_dir() or not child.name.upper().startswith("TASK-"):
                continue
            tid = detect_task_id(child.name)
            records.append(
                {
                    "layer": "OWNER_MANUAL_PROOF",
                    "folder_name": child.name,
                    "path": str(child),
                    "task_id": tid,
                    "modified_time": child.stat().st_mtime,
                }
            )

    records = sorted(records, key=lambda r: (r.get("task_id") or "", r["layer"], r["folder_name"]))

    payload = {
        "generated_at_utc": now_utc(),
        "records": records,
        "counts": {
            "total": len(records),
            "normal": sum(1 for r in records if r["layer"] == "NORMAL_ARTIFACT"),
            "manual": sum(1 for r in records if r["layer"] == "OWNER_MANUAL_PROOF"),
        },
        "verdict": "PASS" if records else "PARTIAL",
    }
    write_json(Path(args.output_json), payload)

    lines = [
        "# 0016A TASKS INVENTORY",
        "",
        f"generated_at_utc: {payload['generated_at_utc']}",
        f"total: {payload['counts']['total']} normal: {payload['counts']['normal']} manual: {payload['counts']['manual']}",
        "",
        "## Records",
    ]
    for r in records:
        lines.append(f"- {r['task_id']} | layer={r['layer']} | path={r['path']}")
    write_text(Path(args.output_md), "\n".join(lines))

    print(f"continuity_inventory_tasks: total={payload['counts']['total']} verdict={payload['verdict']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
