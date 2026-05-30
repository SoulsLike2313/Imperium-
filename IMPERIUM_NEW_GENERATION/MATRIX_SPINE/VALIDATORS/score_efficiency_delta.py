#!/usr/bin/env python3
"""Compute 5-scale efficiency delta receipt for Matrix Spine runtime corridor task."""

from __future__ import annotations

import argparse
import json
import math
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

TASK_ID_DEFAULT = "TASK-NEWGEN-MECHANICUS-MATRIX-SPINE-STATUS-NORMALIZATION-AND-RUNTIME-CORRIDOR-PROOF-VM3-V0_1"

BASELINE = {
    "mechanicus_validator_readiness": 64,
    "inquisition_fake_green_resistance": 41,
    "officio_entry_contract_readiness": 44,
    "administratum_receipt_closure_readiness": 46,
    "overall_candidate_usefulness": 69,
}


def utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def load_json(path: Path) -> tuple[Any | None, str | None]:
    try:
        return json.loads(path.read_text(encoding="utf-8")), None
    except Exception as exc:  # pragma: no cover - defensive
        return None, str(exc)


def clamp(value: int) -> int:
    return max(0, min(100, value))


def main() -> int:
    parser = argparse.ArgumentParser(description="Compute efficiency delta receipt.")
    parser.add_argument("--task-id", default=TASK_ID_DEFAULT)
    parser.add_argument("--repo-root", default="")
    parser.add_argument("--output-dir", default="")
    args = parser.parse_args()

    script_path = Path(__file__).resolve()
    repo_root = Path(args.repo_root).resolve() if args.repo_root else script_path.parents[3]
    if args.output_dir:
        output_dir = Path(args.output_dir).resolve()
    else:
        output_dir = (
            repo_root
            / "IMPERIUM_NEW_GENERATION/ORGANS/MECHANICUS/REPORTS"
            / TASK_ID_DEFAULT
        )

    validator_summary_path = output_dir / "matrix_validator_run" / "matrix_spine_validation_summary.json"
    corridor_receipt_path = output_dir / "synthetic_corridor_receipt.json"

    summary, summary_error = load_json(validator_summary_path)
    corridor, corridor_error = load_json(corridor_receipt_path)

    if summary_error is not None or not isinstance(summary, dict):
        print(f"[efficiency-delta] unable to read validator summary: {summary_error}", file=sys.stderr)
        return 1
    if corridor_error is not None or not isinstance(corridor, dict):
        print(f"[efficiency-delta] unable to read corridor receipt: {corridor_error}", file=sys.stderr)
        return 1

    issue_counts = summary.get("issue_counts", {})
    fail_count = int(issue_counts.get("FAIL", 0)) if isinstance(issue_counts, dict) else 0
    warn_count = int(issue_counts.get("WARN", 0)) if isinstance(issue_counts, dict) else 0
    negative_results = summary.get("negative_fixture_results", [])
    negative_count = len(negative_results) if isinstance(negative_results, list) else 0
    negative_detected = 0
    if isinstance(negative_results, list):
        negative_detected = sum(1 for item in negative_results if isinstance(item, dict) and item.get("detected") is True)

    corridor_steps = corridor.get("steps", [])
    passed_steps = 0
    if isinstance(corridor_steps, list):
        passed_steps = sum(1 for item in corridor_steps if isinstance(item, dict) and item.get("status") == "PASS")

    mechanicus_after = clamp(BASELINE["mechanicus_validator_readiness"] + 8 + min(12, negative_detected) - (3 * fail_count) - warn_count)
    inquisition_after = clamp(BASELINE["inquisition_fake_green_resistance"] + min(15, negative_detected) + (6 if fail_count == 0 else 0))
    officio_after = clamp(BASELINE["officio_entry_contract_readiness"] + (8 if passed_steps >= 1 else 0) + (3 if negative_detected >= 12 else 0))
    administratum_after = clamp(BASELINE["administratum_receipt_closure_readiness"] + (10 if passed_steps >= 5 else 0) + (4 if corridor.get("overall") == "PASS" else 0))

    overall_after = clamp(
        BASELINE["overall_candidate_usefulness"]
        + min(20, (2 * passed_steps) + (negative_detected // 2))
        - (4 * fail_count)
        - (2 * warn_count)
    )

    after = {
        "mechanicus_validator_readiness": mechanicus_after,
        "inquisition_fake_green_resistance": inquisition_after,
        "officio_entry_contract_readiness": officio_after,
        "administratum_receipt_closure_readiness": administratum_after,
        "overall_candidate_usefulness": overall_after,
    }

    delta = {key: after[key] - BASELINE[key] for key in BASELINE}
    positive_delta = all(value > 0 for value in delta.values())
    verdict = "PASS_WITH_WARNINGS" if positive_delta else "WARN"

    receipt = {
        "task_id": args.task_id,
        "timestamp_utc": utc_now(),
        "base_head": "922160728f64482a83f88e1e873a99b460094f8a",
        "implementation_head": "",
        "closure_head": "",
        "baseline": BASELINE,
        "after": after,
        "delta": delta,
        "scales": {
            "mechanicus_validator_readiness": {
                "before": BASELINE["mechanicus_validator_readiness"],
                "after": mechanicus_after,
                "delta": delta["mechanicus_validator_readiness"],
                "evidence": [str(validator_summary_path)],
            },
            "inquisition_fake_green_resistance": {
                "before": BASELINE["inquisition_fake_green_resistance"],
                "after": inquisition_after,
                "delta": delta["inquisition_fake_green_resistance"],
                "evidence": [str(validator_summary_path)],
            },
            "officio_entry_contract_readiness": {
                "before": BASELINE["officio_entry_contract_readiness"],
                "after": officio_after,
                "delta": delta["officio_entry_contract_readiness"],
                "evidence": [str(corridor_receipt_path)],
            },
            "administratum_receipt_closure_readiness": {
                "before": BASELINE["administratum_receipt_closure_readiness"],
                "after": administratum_after,
                "delta": delta["administratum_receipt_closure_readiness"],
                "evidence": [str(corridor_receipt_path)],
            },
            "overall_candidate_usefulness": {
                "before": BASELINE["overall_candidate_usefulness"],
                "after": overall_after,
                "delta": delta["overall_candidate_usefulness"],
                "evidence": [str(validator_summary_path), str(corridor_receipt_path)],
            },
        },
        "verdict": verdict,
        "confidence": "HIGH" if positive_delta else "MEDIUM",
        "caps_triggered": [] if positive_delta else ["CAP_NO_EFFICIENCY_DELTA"],
        "evidence": [
            {
                "path": str(validator_summary_path),
                "negative_fixture_total": negative_count,
                "negative_fixture_detected": negative_detected,
                "fail_count": fail_count,
                "warn_count": warn_count,
            },
            {
                "path": str(corridor_receipt_path),
                "passed_steps": passed_steps,
                "overall": corridor.get("overall"),
            },
        ],
        "notes": [
            "Five-scale score is deterministic and stdlib-only.",
            "Synthetic corridor is accepted by taskpack and marked not_real_warp=true.",
        ],
    }

    output_path = output_dir / "efficiency_delta_receipt.json"
    output_path.write_text(json.dumps(receipt, ensure_ascii=True, indent=2) + "\n", encoding="utf-8")

    print(f"[efficiency-delta] output={output_path}")
    print(
        "[efficiency-delta] "
        + f"overall_before={BASELINE['overall_candidate_usefulness']} "
        + f"overall_after={overall_after} "
        + f"delta={delta['overall_candidate_usefulness']}"
    )
    return 0 if positive_delta else 1


if __name__ == "__main__":
    sys.exit(main())
