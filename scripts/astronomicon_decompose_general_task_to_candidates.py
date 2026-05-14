#!/usr/bin/env python3
"""Decompose a General Task into Local Task candidate JSON files (MVP skeleton)."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any, Dict, List

from astronomicon_general_task_lib import parse_markdown_general_task, validate_parsed_general_task


def sanitize_id(raw: str) -> str:
    cleaned = re.sub(r"[^A-Za-z0-9_-]+", "-", raw).strip("-")
    return cleaned or "UNSPECIFIED"


def default_metric_zones() -> Dict[str, Any]:
    keys = [
        "scope_size",
        "touched_zones_count",
        "file_change_risk",
        "private_context_dependency",
        "external_tool_dependency",
        "ui_dependency",
        "schema_dependency",
        "script_dependency",
        "dashboard_dependency",
        "receipt_requirement_level",
        "checker_requirement_level",
        "owner_gate_level",
        "rollback_complexity",
        "artifact_complexity",
        "stage_count_estimate",
        "agent_context_load",
        "ambiguity_level",
        "dependency_count",
        "blocker_probability",
        "fake_green_risk",
        "stale_data_risk",
        "warning_noise_risk",
        "local_vs_repo_boundary_risk",
        "vm2_need_level",
        "commit_batching_suitability",
        "review_required_by_speculum",
    ]
    return {key: "PENDING" for key in keys}


def ensure_allowed_output(path: Path, repo_root: Path) -> None:
    allowed_roots = [
        (repo_root / "ORGANS" / "ASTRONOMICON" / "REGISTRY" / "TASKS" / "CANDIDATES").resolve(),
        (repo_root / "tests" / "fixtures" / "astronomicon").resolve(),
    ]
    resolved = path.resolve()
    for root in allowed_roots:
        try:
            resolved.relative_to(root)
            return
        except ValueError:
            continue
    raise ValueError(f"Output path outside allowed scope: {resolved}")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Decompose General Task into Local Task candidates.")
    parser.add_argument("input_path", help="Path to General Task markdown")
    parser.add_argument(
        "--out",
        default="tests/fixtures/astronomicon/generated_candidates",
        help="Output folder for candidate JSON files",
    )
    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    input_path = Path(args.input_path)

    if not input_path.exists():
        print(f"FAIL: input file not found: {input_path}")
        return 2

    repo = Path(__file__).resolve().parents[1]
    out_dir = Path(args.out)
    if not out_dir.is_absolute():
        out_dir = (repo / out_dir).resolve()

    try:
        ensure_allowed_output(out_dir, repo)
    except Exception as exc:
        print(f"FAIL: {exc}")
        return 3

    try:
        parsed = parse_markdown_general_task(input_path)
    except Exception as exc:
        print(f"FAIL: BLOCKED_GENERAL_TASK_PARSE_FAILED: {exc}")
        return 2

    errors = validate_parsed_general_task(parsed)
    if errors:
        print("FAIL: BLOCKED_GENERAL_TASK_FORMAT_INVALID")
        print(json.dumps({"errors": errors}, ensure_ascii=False, indent=2))
        return 1

    fm = parsed["frontmatter"]
    hints = fm.get("decomposition_hints", [])
    if not isinstance(hints, list) or len(hints) == 0:
        hints = ["Implement minimal candidate from owner goal"]

    requested_count = fm.get("local_task_candidate_count_hint", 1)
    if not isinstance(requested_count, int) or requested_count < 1:
        requested_count = 1
    candidate_count = min(requested_count, max(1, len(hints), 3))

    out_dir.mkdir(parents=True, exist_ok=True)

    generated_files: List[str] = []
    base_id = sanitize_id(fm["general_task_id"])
    title = fm["title"]

    for idx in range(candidate_count):
        hint = hints[idx % len(hints)]
        candidate_id = f"TC-{base_id}-{idx + 1:02d}"
        payload: Dict[str, Any] = {
            "schema_version": "task_candidate_v0_1",
            "task_candidate_id": candidate_id,
            "general_task_id": fm["general_task_id"],
            "title": f"{title} / Candidate {idx + 1}",
            "local_task_summary": str(hint),
            "scope_in": fm.get("scope_in", []),
            "scope_out": fm.get("scope_out", []),
            "target_organ": fm.get("target_organs", ["ASTRONOMICON"])[0],
            "files_likely_touched": [
                "ORGANS/ASTRONOMICON/SCHEMAS/",
                "ORGANS/ASTRONOMICON/TEMPLATES/",
                "scripts/",
            ],
            "dependencies": fm.get("dependencies", []),
            "unresolved_questions": fm.get("unknowns", []),
            "metric_zones": default_metric_zones(),
            "speculum_review_fields": [
                "review_verdict",
                "scope_corrections",
                "required_checkers",
                "required_receipts",
                "metric_updates",
                "final_recommendation",
            ],
            "speculum_review_status": "PENDING_NOT_REQUESTED",
            "modernized": False,
            "registered": False,
            "current_status": "DRAFT_TEST_NOT_ACTIVE"
            if "tests\\fixtures" in str(input_path)
            else "DRAFT_CANDIDATE_NOT_REGISTERED",
        }
        out_file = out_dir / f"{candidate_id}.json"
        out_file.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        generated_files.append(str(out_file))

    print(
        json.dumps(
            {
                "status": "PASS",
                "generated_count": len(generated_files),
                "output_dir": str(out_dir),
                "generated_files": generated_files,
            },
            ensure_ascii=False,
            indent=2,
        )
    )
    print("PASS: GENERAL_TASK_DECOMPOSED_TO_CANDIDATES")
    return 0


if __name__ == "__main__":
    sys.exit(main())
