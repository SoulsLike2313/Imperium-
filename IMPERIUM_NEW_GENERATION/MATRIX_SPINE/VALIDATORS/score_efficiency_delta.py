#!/usr/bin/env python3
"""Compute 5-scale efficiency delta receipt for Matrix Spine runtime corridor task."""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

TASK_ID_DEFAULT = "TASK-NEWGEN-MATRIX-SPINE-CLOSURE-PROVENANCE-CORRIDOR-NAMING-AND-REVIEW-PIPELINE-HARDENING-VM3-V0_1"

BASELINE = {
    "mechanicus_validator_readiness": 64,
    "inquisition_fake_green_resistance": 41,
    "officio_entry_contract_readiness": 44,
    "administratum_receipt_closure_readiness": 46,
    "overall_candidate_usefulness": 69,
}

SEVERE_RED_TEAM_CAPS = {
    "CAP_UNTYPED_RUNTIME_CLAIM",
    "CAP_SYNTHETIC_CLAIMED_AS_REAL",
    "CAP_WARP_CLAIMED_WITHOUT_UNLOCK",
    "CAP_NO_FINAL_CLOSURE_VERIFIER",
    "CAP_NO_NEXT_PIPELINE_HANDOFF",
    "CAP_RUNTIME_OUTPUT_UNCLASSIFIED",
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


def collect_cap_codes(payload: Any) -> list[str]:
    if not isinstance(payload, dict):
        return []

    caps: set[str] = set()
    for key in ["cap_codes_detected", "caps_triggered", "known_caps_or_warnings", "downgrade_rules_applied"]:
        value = payload.get(key)
        if isinstance(value, list):
            for item in value:
                if isinstance(item, str) and item.startswith("CAP_"):
                    caps.add(item)
    return sorted(caps)


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
    red_team_path = output_dir / "hard_red_team_verdict.json"

    summary, summary_error = load_json(validator_summary_path)
    corridor, corridor_error = load_json(corridor_receipt_path)

    if summary_error is not None or not isinstance(summary, dict):
        print(f"[efficiency-delta] unable to read validator summary: {summary_error}", file=sys.stderr)
        return 1
    if corridor_error is not None or not isinstance(corridor, dict):
        print(f"[efficiency-delta] unable to read corridor receipt: {corridor_error}", file=sys.stderr)
        return 1

    red_team, red_team_error = load_json(red_team_path)

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

    summary_caps = collect_cap_codes(summary)
    red_team_caps = collect_cap_codes(red_team)
    combined_caps = sorted(set(summary_caps) | set(red_team_caps))
    severe_caps_detected = sorted(cap for cap in combined_caps if cap in SEVERE_RED_TEAM_CAPS)
    red_team_missing = red_team_error is not None or not isinstance(red_team, dict)

    severe_cap_penalty = len(severe_caps_detected)
    if red_team_missing:
        severe_cap_penalty += 1

    mechanicus_after = clamp(
        BASELINE["mechanicus_validator_readiness"]
        + 8
        + min(12, negative_detected)
        - (3 * fail_count)
        - warn_count
        - (2 * severe_cap_penalty)
    )
    inquisition_after = clamp(
        BASELINE["inquisition_fake_green_resistance"]
        + min(15, negative_detected)
        + (6 if fail_count == 0 else 0)
        - (3 * severe_cap_penalty)
    )
    officio_after = clamp(
        BASELINE["officio_entry_contract_readiness"]
        + (8 if passed_steps >= 1 else 0)
        + (3 if negative_detected >= 12 else 0)
        - (2 * severe_cap_penalty)
    )
    administratum_after = clamp(
        BASELINE["administratum_receipt_closure_readiness"]
        + (10 if passed_steps >= 5 else 0)
        + (4 if corridor.get("overall") == "PASS" else 0)
        - (2 * severe_cap_penalty)
    )

    overall_after = clamp(
        BASELINE["overall_candidate_usefulness"]
        + min(20, (2 * passed_steps) + (negative_detected // 2))
        - (4 * fail_count)
        - (2 * warn_count)
        - (6 * severe_cap_penalty)
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

    caps_triggered: set[str] = set(severe_caps_detected)
    if red_team_missing:
        caps_triggered.add("CAP_REDTEAM_CAPS_NOT_APPLIED_TO_SCORE")
    if not positive_delta:
        caps_triggered.add("CAP_NO_EFFICIENCY_DELTA")

    if "CAP_WARP_CLAIMED_WITHOUT_UNLOCK" in caps_triggered or "CAP_SYNTHETIC_CLAIMED_AS_REAL" in caps_triggered:
        verdict = "BLOCK"
    elif positive_delta and not caps_triggered:
        verdict = "PASS_WITH_WARNINGS"
    else:
        verdict = "WARN"

    receipt = {
        "task_id": args.task_id,
        "timestamp_utc": utc_now(),
        "base_head": "935dc33b52e8915aae71611fad48c91135c4e800",
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
        "confidence": "HIGH" if positive_delta and not caps_triggered else "MEDIUM",
        "caps_triggered": sorted(caps_triggered),
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
            {
                "path": str(red_team_path),
                "read_ok": not red_team_missing,
                "caps_detected": red_team_caps,
                "error": red_team_error if red_team_missing else "",
            },
        ],
        "notes": [
            "Five-scale score is deterministic and stdlib-only.",
            "Synthetic corridor is accepted by taskpack and marked synthetic-only.",
            "Red-team caps are consumed by scorer penalties before verdict emission.",
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
    return 0 if verdict == "PASS_WITH_WARNINGS" else 1


if __name__ == "__main__":
    sys.exit(main())
