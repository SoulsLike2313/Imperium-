from __future__ import annotations

import json
import subprocess
from datetime import datetime, timezone
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


def parse_utc(value: str) -> datetime:
    return datetime.fromisoformat(value.replace("Z", "+00:00")).astimezone(timezone.utc)


def evaluate_state(payload: dict[str, Any], now: datetime) -> tuple[bool, str]:
    required = [
        "generated_at_utc",
        "checked_at_utc",
        "expires_after_seconds",
        "stale_status",
        "status",
        "git_head",
    ]
    for field in required:
        if field not in payload:
            return False, f"missing_{field}"
    stale_status = str(payload["stale_status"]).lower()
    if stale_status not in {"fresh", "stale", "unknown", "not_applicable"}:
        return False, "invalid_stale_status"
    expires = int(payload["expires_after_seconds"])
    age = (now - parse_utc(str(payload["checked_at_utc"]))).total_seconds()
    computed = "fresh" if age <= expires else "stale"
    if stale_status != computed and stale_status != "unknown":
        return False, "stale_status_mismatch"
    if stale_status in {"stale", "unknown"} and str(payload.get("status", "")).upper() in {"PASS", "PASS_WITH_WARNINGS"}:
        return False, "stale_or_unknown_marked_pass"
    return True, "ok"


def run() -> int:
    now_str = utc_now()
    head = git_head()
    now_dt = datetime.fromisoformat(now_str.replace("Z", "+00:00"))
    stage_sources = hardening_stage_report_map()

    rows = []
    blockers: list[str] = []
    live_outputs: list[str] = []
    for organ in ORGANS:
        state_path = Path(organ["base"]) / "V1" / "DASHBOARD_DATA" / "dashboard_state.json"
        if not state_path.exists():
            blockers.append(f"missing_state:{state_path}")
            continue
        payload = json.loads(state_path.read_text(encoding="utf-8"))
        ok, reason = evaluate_state(payload, now_dt)
        rows.append(
            {
                "organ_id": organ["id"],
                "path": rel(state_path),
                "result": "PASS" if ok else "FAIL",
                "reason": reason,
                "declared_stale_status": payload.get("stale_status"),
            }
        )
        live_outputs.append(rel(state_path))
        if not ok:
            blockers.append(f"{organ['id']}:{reason}")

    stale_bad_sample = {
        "generated_at_utc": now_str,
        "checked_at_utc": "2000-01-01T00:00:00Z",
        "expires_after_seconds": 60,
        "stale_status": "fresh",
        "status": "PASS",
        "git_head": head,
    }
    stale_ok, stale_reason = evaluate_state(stale_bad_sample, now_dt)
    fixture = {
        "fixture_id": "known_bad_stale_marked_fresh",
        "expected": "FAIL",
        "actual": "PASS" if stale_ok else "FAIL",
        "reason": stale_reason,
        "match_expected": (not stale_ok),
    }
    if stale_ok:
        blockers.append("known_bad_stale_fixture_not_detected")

    verdict = "PASS" if not blockers else "FAIL"
    report_path = LIVE_TASK_ROOT / "CHECKS" / "stale_status_check_report_v1.json"
    write_json(
        report_path,
        {
            "task_id": TASK_ID,
            "stage_id": "STAGE-08",
            "generated_at_utc": now_str,
            "git_head": head,
            "rows": rows,
            "fixture_check": fixture,
            "warnings": [],
            "blockers": blockers,
            "verdict": verdict,
        },
    )
    live_outputs.append(rel(report_path))
    write_stage_artifacts(
        8,
        source_hardening_report_path=stage_sources.get(8),
        live_outputs=live_outputs,
        checks_run=["python scripts/foundational_organs_v1/check_foundational_organs_v1_stale_status.py"],
        verdict=verdict,
        warnings=[],
        blockers=blockers,
        self_repairs=[],
        retry_count=0,
        notes="live_stale_status_check",
    )
    print(verdict)
    print(rel(report_path))
    return 0 if verdict == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(run())
