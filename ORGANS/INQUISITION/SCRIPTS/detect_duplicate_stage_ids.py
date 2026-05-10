#!/usr/bin/env python3
"""Detect duplicate stage IDs across JSON files in route folder."""

from __future__ import annotations

import argparse
import json
from collections import defaultdict
from pathlib import Path


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Detect duplicate stage IDs.")
    p.add_argument("--scan-dir", required=True)
    p.add_argument("--output-json", required=True)
    return p.parse_args()


def collect_stage_ids(data, found: list[str]) -> None:
    if isinstance(data, dict):
        for k, v in data.items():
            if k == "stage_id" and isinstance(v, str):
                found.append(v)
            collect_stage_ids(v, found)
    elif isinstance(data, list):
        for item in data:
            collect_stage_ids(item, found)


def main() -> int:
    args = parse_args()
    scan_dir = Path(args.scan_dir).resolve()
    out_json = Path(args.output_json).resolve()
    index = defaultdict(list)

    for p in scan_dir.rglob("*.json"):
        try:
            data = json.loads(p.read_text(encoding="utf-8"))
        except Exception:
            continue
        ids = []
        collect_stage_ids(data, ids)
        rel = str(p.relative_to(scan_dir)).replace("\\", "/")
        for sid in ids:
            index[sid].append(rel)

    duplicates = {sid: paths for sid, paths in index.items() if len(paths) > 1}
    report = {
        "scan_dir": str(scan_dir),
        "stage_id_total": len(index),
        "duplicate_stage_ids": duplicates,
        "duplicate_count": len(duplicates),
        "verdict": "PASS_DUPLICATE_STAGE_ID_SCAN" if not duplicates else "WARN_DUPLICATE_STAGE_ID_SCAN",
    }
    out_json.parent.mkdir(parents=True, exist_ok=True)
    out_json.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
