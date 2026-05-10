#!/usr/bin/env python3
"""Build TASK_LAUNCH_CARD and route outputs from Astra draft."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Build TASK_LAUNCH_CARD from Astra route.")
    p.add_argument("--astra-route-dir", required=True)
    p.add_argument("--output-dir", required=True)
    return p.parse_args()


def main() -> int:
    args = parse_args()
    astra_dir = Path(args.astra_route_dir).resolve()
    out = Path(args.output_dir).resolve()
    out.mkdir(parents=True, exist_ok=True)

    record = json.loads((astra_dir / "ASTRA_TASK_RECORD.json").read_text(encoding="utf-8"))
    stage_map = json.loads((astra_dir / "STAGE_MAP.json").read_text(encoding="utf-8"))
    task_id = record["task_id"]
    run_id = record["RUN_ID"]

    launch = {
        "schema_version": "TASK_LAUNCH_CARD_V0_2",
        "task_id": task_id,
        "run_id": run_id,
        "stage_id": "ADMINISTRATUM-STAGE-001",
        "task_route_version": record.get("TASK_ROUTE_VERSION", "0.1"),
        "astra_route_status": record.get("ASTRA_ROUTE_STATUS", "DRAFT"),
        "read_first_refs": [
            str(astra_dir / "ASTRA_TASK_RECORD.json"),
            str(astra_dir / "STAGE_MAP.json"),
            str(astra_dir / "PASS_CRITERIA.json"),
        ],
        "policy_refs": record.get("policy_refs", []),
        "policy_hashes": record.get("policy_hashes", []),
        "canonical_answer_refs": [],
        "allowed_tool_refs": [
            "TOOL-EXPLORER-RUN-STATIC-READONLY-SCAN",
            "TOOL-EXPLORER-RUN-TRUTH-AUDIT",
            "TOOL-EXPLORER-RUN-AUTOSCREENSHOT-CHECK",
        ],
        "expected_outputs": [
            {"id": "TASK_READ_FIRST", "output_path": str(out / "TASK_READ_FIRST.md")},
            {"id": "TASK_OUTPUT_MAP", "output_path": str(out / "TASK_OUTPUT_MAP.json")},
            {"id": "POLICY_REFS", "output_path": str(out / "POLICY_REFS.json")},
            {"id": "ADDRESS_REFS", "output_path": str(out / "ADDRESS_REFS.json")},
            {"id": "RECEIPT_REQUIREMENTS", "output_path": str(out / "RECEIPT_REQUIREMENTS.json")},
            {"id": "TASK_VERSION_CHAIN", "output_path": str(out / "TASK_VERSION_CHAIN.json")},
        ],
        "pass_criteria": ["All required route outputs created.", "Policy refs declared.", "No forbidden activations."],
        "partial_fail_behavior": "Write fail receipt and bounded repair attempt.",
        "next_allowed_action_ref": "MECHANICUS-STAGE-001",
    }
    (out / "TASK_LAUNCH_CARD.json").write_text(json.dumps(launch, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (out / "TASK_OUTPUT_MAP.json").write_text(
        json.dumps(
            {
                "task_id": task_id,
                "run_id": run_id,
                "outputs": launch["expected_outputs"],
                "source_stage_map_path": str(astra_dir / "STAGE_MAP.json"),
                "stage_count": len(stage_map.get("stages", [])),
            },
            ensure_ascii=False,
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    (out / "TASK_VERSION_CHAIN.json").write_text(
        json.dumps(
            {
                "task_id": task_id,
                "versions": [
                    {
                        "version": "0.1",
                        "type": "LOCAL_DRY_RUN_FOUNDATION",
                        "created_by": "build_task_launch_card_from_astra.py",
                    }
                ],
            },
            ensure_ascii=False,
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    print(f"launch card built: {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
