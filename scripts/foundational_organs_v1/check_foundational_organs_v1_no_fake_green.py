from __future__ import annotations

import json
import subprocess
from pathlib import Path
from typing import Any

from common import (
    LIVE_TASK_ROOT,
    ORGANS,
    TASK_ID,
    hardening_stage_report_map,
    rel,
    utc_now,
    write_json,
    write_stage_artifacts,
)


def git_head() -> str:
    return subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip()


def evaluate_state(payload: dict[str, Any]) -> tuple[bool, str]:
    status = str(payload.get("status", "")).upper()
    warnings = payload.get("warnings") or []
    blockers = payload.get("blockers") or []
    evidence = payload.get("evidence_paths") or []
    stale = str(payload.get("stale_status", "unknown")).lower()
    if status == "PASS" and not evidence:
        return False, "pass_without_evidence"
    if status == "PASS_WITH_WARNINGS" and not warnings:
        return False, "pww_without_warnings"
    if blockers and status in {"PASS", "PASS_WITH_WARNINGS"}:
        return False, "pass_with_blockers"
    if stale in {"stale", "unknown"} and status in {"PASS", "PASS_WITH_WARNINGS"}:
        return False, "stale_or_unknown_marked_pass"
    return True, "ok"


def evaluate_action(payload: dict[str, Any]) -> tuple[bool, str]:
    for action in payload.get("actions", []):
        if action.get("enabled"):
            if not action.get("expected_receipt_path"):
                return False, "enabled_action_missing_receipt_path"
            if not action.get("failure_behavior"):
                return False, "enabled_action_missing_failure_behavior"
        if not action.get("enabled") and not action.get("disabled_reason"):
            return False, "disabled_action_missing_reason"
    return True, "ok"


def run() -> int:
    now = utc_now()
    head = git_head()
    stage_sources = hardening_stage_report_map()
    rows: list[dict[str, Any]] = []
    action_rows: list[dict[str, Any]] = []
    live_outputs: list[str] = []
    warnings: list[str] = []
    blockers: list[str] = []

    for organ in ORGANS:
        oid = str(organ["id"])
        state_path = Path(organ["base"]) / "V1" / "DASHBOARD_DATA" / "dashboard_state.json"
        actions_path = Path(organ["base"]) / "V1" / "DASHBOARD_DATA" / "dashboard_actions.json"
        if not state_path.exists():
            blockers.append(f"missing_state:{state_path}")
            continue
        state = json.loads(state_path.read_text(encoding="utf-8"))
        ok_state, reason_state = evaluate_state(state)
        rows.append(
            {
                "organ_id": oid,
                "path": rel(state_path),
                "status": state.get("status"),
                "result": "PASS" if ok_state else "FAIL",
                "reason": reason_state,
            }
        )
        live_outputs.append(rel(state_path))
        if not ok_state:
            blockers.append(f"{oid}:{reason_state}")

        if not actions_path.exists():
            blockers.append(f"missing_actions:{actions_path}")
            continue
        actions = json.loads(actions_path.read_text(encoding="utf-8"))
        ok_actions, reason_actions = evaluate_action(actions)
        action_rows.append(
            {
                "organ_id": oid,
                "path": rel(actions_path),
                "result": "PASS" if ok_actions else "FAIL",
                "reason": reason_actions,
            }
        )
        live_outputs.append(rel(actions_path))
        if not ok_actions:
            blockers.append(f"{oid}:{reason_actions}")

    bad_sample = {
        "status": "PASS",
        "warnings": [],
        "blockers": [],
        "evidence_paths": [],
        "stale_status": "fresh",
    }
    bad_ok, bad_reason = evaluate_state(bad_sample)
    fixture_checks = [
        {
            "fixture_id": "known_bad_missing_evidence",
            "expected": "FAIL",
            "actual": "PASS" if bad_ok else "FAIL",
            "reason": bad_reason,
            "match_expected": (not bad_ok),
        }
    ]
    if bad_ok:
        blockers.append("known_bad_sample_not_detected")

    verdict = "PASS" if not blockers else "FAIL"
    report_path = LIVE_TASK_ROOT / "CHECKS" / "no_fake_green_check_report_v1.json"
    write_json(
        report_path,
        {
            "task_id": TASK_ID,
            "stage_id": "STAGE-07",
            "generated_at_utc": now,
            "git_head": head,
            "state_checks": rows,
            "action_checks": action_rows,
            "fixture_checks": fixture_checks,
            "warnings": warnings,
            "blockers": blockers,
            "verdict": verdict,
        },
    )
    live_outputs.append(rel(report_path))
    checks = ["python scripts/foundational_organs_v1/check_foundational_organs_v1_no_fake_green.py"]
    write_stage_artifacts(
        7,
        source_hardening_report_path=stage_sources.get(7),
        live_outputs=live_outputs,
        checks_run=checks,
        verdict=verdict,
        warnings=warnings,
        blockers=blockers,
        self_repairs=[],
        retry_count=0,
        notes="live_no_fake_green_check",
    )
    print(verdict)
    print(rel(report_path))
    return 0 if verdict == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(run())
