#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Dict, List

from continuity_common import classify_manual_path, detect_task_id, now_utc, write_json, write_text


def main() -> int:
    parser = argparse.ArgumentParser(description="Scan ledger files across artifacts")
    parser.add_argument("--imperium-root", required=True)
    parser.add_argument("--output-json", required=True)
    parser.add_argument("--output-md", required=True)
    args = parser.parse_args()

    root = Path(args.imperium_root).resolve()
    artifacts_root = root / "ARTIFACTS"
    manual_root = artifacts_root / "_MANUAL_PROOFS"

    records: List[Dict[str, Any]] = []
    for p in sorted(artifacts_root.rglob("*LEDGER*.jsonl") if artifacts_root.exists() else []):
        lines = p.read_text(encoding="utf-8", errors="ignore").splitlines()
        parsed = 0
        last_event = None
        parse_errors = 0
        for line in lines:
            if not line.strip():
                continue
            try:
                obj = json.loads(line)
                parsed += 1
                last_event = obj.get("event_type")
            except Exception:
                parse_errors += 1
        rec = {
            "path": str(p),
            "relative_path": str(p.relative_to(root)) if root in p.parents else str(p),
            "task_id": detect_task_id(str(p)),
            "layer": "OWNER_MANUAL_PROOF" if classify_manual_path(p, manual_root) else "GENERATED_ARTIFACT",
            "line_count": len(lines),
            "parsed_event_count": parsed,
            "parse_error_count": parse_errors,
            "last_event_type": last_event,
        }
        records.append(rec)

    payload = {
        "generated_at_utc": now_utc(),
        "ledger_files_count": len(records),
        "records": records,
        "verdict": "PASS" if records else "PARTIAL",
    }
    write_json(Path(args.output_json), payload)

    lines = [
        "# 0016A LEDGER SCAN",
        "",
        f"generated_at_utc: {payload['generated_at_utc']}",
        f"ledger_files_count: {payload['ledger_files_count']}",
        "",
        "## Records",
    ]
    for r in records:
        lines.append(
            f"- {r['relative_path']} | task_id={r['task_id']} | layer={r['layer']} | parsed={r['parsed_event_count']} errors={r['parse_error_count']} last={r['last_event_type']}"
        )
    write_text(Path(args.output_md), "\n".join(lines))

    print(f"continuity_scan_ledgers: files={len(records)} verdict={payload['verdict']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
