#!/usr/bin/env python3
"""Build Administratum read-first route artifacts from Astra draft."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Build TASK_READ_FIRST and support refs from Astra route.")
    p.add_argument("--astra-route-dir", required=True)
    p.add_argument("--output-dir", required=True)
    return p.parse_args()


def main() -> int:
    args = parse_args()
    astra_dir = Path(args.astra_route_dir).resolve()
    out = Path(args.output_dir).resolve()
    out.mkdir(parents=True, exist_ok=True)

    astra_record = json.loads((astra_dir / "ASTRA_TASK_RECORD.json").read_text(encoding="utf-8"))
    task_id = astra_record["task_id"]
    run_id = astra_record["RUN_ID"]

    policy_refs = astra_record.get("policy_refs", [])
    (out / "POLICY_REFS.json").write_text(json.dumps({"task_id": task_id, "run_id": run_id, "policy_refs": policy_refs}, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    address_refs = {
        "task_id": task_id,
        "run_id": run_id,
        "input_refs": [str(astra_dir)],
        "output_root": str(out),
        "stage_receipts_root": str(out / "STAGE_RECEIPTS"),
        "validation_reports_root": str(out / "VALIDATION_REPORTS"),
    }
    (out / "ADDRESS_REFS.json").write_text(json.dumps(address_refs, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    receipt_reqs = {
        "task_id": task_id,
        "run_id": run_id,
        "required_per_stage": ["STAGE_PASS_RECEIPT", "STAGE_VALIDATION_REPORT"],
        "blocked_receipt_required_on_semantic_or_destructive_conflict": True,
    }
    (out / "RECEIPT_REQUIREMENTS.json").write_text(json.dumps(receipt_reqs, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    (out / "TASK_READ_FIRST.md").write_text(
        "# TASK READ FIRST\n\n"
        f"TASK_ID: {task_id}\n"
        f"RUN_ID: {run_id}\n\n"
        "1. Read ASTRA_TASK_RECORD.json\n"
        "2. Read STAGE_MAP.json\n"
        "3. Read PASS_CRITERIA.json\n"
        "4. Read POLICY_REFS.json\n"
        "5. Read ADDRESS_REFS.json\n"
        "6. Execute only current stage scope.\n",
        encoding="utf-8",
    )
    print(f"administratum read-first artifacts written: {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
