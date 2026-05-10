#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path
from typing import Any, Dict, List

from continuity_common import classify_manual_path, detect_task_id, now_utc, read_json_safe, write_json, write_text


def parse_receipt_status(path: Path) -> Dict[str, Any]:
    if path.suffix.lower() == ".json":
        obj, err = read_json_safe(path)
        if obj is not None:
            return {
                "status": obj.get("status") or obj.get("verdict"),
                "producer_type": obj.get("producer_type"),
                "task_id": obj.get("task_id"),
                "stage_id": obj.get("stage_id"),
                "run_id": obj.get("run_id"),
                "parse_error": None,
            }
        return {"status": None, "producer_type": None, "task_id": None, "stage_id": None, "run_id": None, "parse_error": err}
    return {"status": None, "producer_type": None, "task_id": None, "stage_id": None, "run_id": None, "parse_error": None}


def main() -> int:
    parser = argparse.ArgumentParser(description="Scan receipts and owner reports across artifacts")
    parser.add_argument("--imperium-root", required=True)
    parser.add_argument("--output-json", required=True)
    parser.add_argument("--output-md", required=True)
    args = parser.parse_args()

    root = Path(args.imperium_root).resolve()
    artifacts_root = root / "ARTIFACTS"
    manual_root = artifacts_root / "_MANUAL_PROOFS"

    candidate_files: List[Path] = []
    for pattern in ("*RECEIPT*.json", "*RECEIPT*.md", "AGENT_FINAL_RESPONSE.txt", "OWNER_SUMMARY*.md"):
        candidate_files.extend(artifacts_root.rglob(pattern) if artifacts_root.exists() else [])

    seen = set()
    records: List[Dict[str, Any]] = []
    for p in sorted(candidate_files):
        rp = str(p.resolve())
        if rp in seen:
            continue
        seen.add(rp)
        parsed = parse_receipt_status(p)
        detected_tid = parsed.get("task_id") or detect_task_id(rp)
        rec = {
            "path": str(p),
            "relative_path": str(p.relative_to(root)) if root in p.parents else str(p),
            "file_name": p.name,
            "task_id": detected_tid,
            "status_or_verdict": parsed.get("status"),
            "producer_type": parsed.get("producer_type"),
            "stage_id": parsed.get("stage_id"),
            "run_id": parsed.get("run_id"),
            "layer": "OWNER_MANUAL_PROOF" if classify_manual_path(p, manual_root) else "GENERATED_ARTIFACT",
            "parse_error": parsed.get("parse_error"),
        }
        records.append(rec)

    payload = {
        "generated_at_utc": now_utc(),
        "receipts_count": len(records),
        "records": records,
        "verdict": "PASS" if records else "PARTIAL",
    }
    write_json(Path(args.output_json), payload)

    lines = [
        "# 0016A RECEIPTS SCAN",
        "",
        f"generated_at_utc: {payload['generated_at_utc']}",
        f"receipts_count: {payload['receipts_count']}",
        "",
        "## Sample",
    ]
    for r in records[:60]:
        lines.append(f"- {r['file_name']} | task_id={r['task_id']} | layer={r['layer']} | status={r['status_or_verdict']}")
    if len(records) > 60:
        lines.append(f"- ... truncated in markdown sample, full records in json: {len(records)} entries")
    write_text(Path(args.output_md), "\n".join(lines))

    print(f"continuity_scan_receipts: count={len(records)} verdict={payload['verdict']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
