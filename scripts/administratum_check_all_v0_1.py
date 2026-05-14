#!/usr/bin/env python3
"""Run Administratum MVP check suite (address book + chronicle + lifecycle)."""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any

from administratum_lifecycle_common_v0_1 import REPO_ROOT, SESSIONS_ROOT, read_json, session_dir, utc_now, write_json


EXPECTED_FAILSTOP_TASK_ID = "TASK-20260514-ADMINISTRATUM-PROOF-FAILSTOP-V0_1"


def run_cmd(args: list[str]) -> dict[str, Any]:
    proc = subprocess.run(args, cwd=REPO_ROOT, text=True, capture_output=True)
    stdout = proc.stdout.strip()
    stderr = proc.stderr.strip()
    parsed = None
    if stdout:
        try:
            parsed = json.loads(stdout)
        except Exception:
            parsed = None
    return {
        "command": " ".join(args),
        "returncode": proc.returncode,
        "stdout": stdout,
        "stderr": stderr,
        "stdout_json": parsed,
    }


def safe_reset_session(task_id: str) -> None:
    target = session_dir(task_id).resolve(strict=False)
    root = SESSIONS_ROOT.resolve(strict=False)
    try:
        target.relative_to(root)
    except Exception as exc:
        raise RuntimeError(f"refusing to remove non-session path: {target}") from exc
    if target.exists():
        shutil.rmtree(target)


def write_fixture_evidence(task_id: str, filename: str, payload: dict[str, Any]) -> str:
    evidence_dir = session_dir(task_id) / "evidence"
    evidence_dir.mkdir(parents=True, exist_ok=True)
    evidence_path = evidence_dir / filename
    evidence_path.write_text(json.dumps(payload, ensure_ascii=True, indent=2) + "\n", encoding="utf-8")
    return str(evidence_path.relative_to(REPO_ROOT)).replace("\\", "/")


def failstop_expectation_check(task_id: str) -> tuple[bool, str]:
    session_path = session_dir(task_id) / "task_session.json"
    if not session_path.exists():
        return True, "expected fail-stop task session not created yet; check is neutral PASS"
    session = read_json(session_path)
    status = str(session.get("status", ""))
    if status in {"STOPPED", "STOPPED_PENDING_OWNER_APPROVAL"}:
        return True, f"expected fail-stop task status is {status}"
    if status == "CLOSED_PASS":
        return False, "expected fail-stop task was incorrectly marked CLOSED_PASS"
    return True, f"expected fail-stop task exists with status {status}"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--report",
        default="ORGANS/ADMINISTRATUM/REPORTS/task_lifecycle_backend_check_report_v0_1.json",
    )
    parser.add_argument("--expected-failstop-task-id", default=EXPECTED_FAILSTOP_TASK_ID)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    py = sys.executable
    report_path = REPO_ROOT / args.report
    report_path.parent.mkdir(parents=True, exist_ok=True)

    checks: dict[str, bool] = {}
    failures: list[str] = []
    command_runs: list[dict[str, Any]] = []

    # Base checkers
    for script in [
        "scripts/administratum_address_book_check_v0_1.py",
        "scripts/administratum_chronicle_check_v0_1.py",
    ]:
        run = run_cmd([py, script])
        command_runs.append(run)
        check_key = f"{Path(script).stem}_pass"
        checks[check_key] = run["returncode"] == 0
        if run["returncode"] != 0:
            failures.append(f"{script} returned non-zero")

    # Guard 1: close should fail when required stages are missing.
    close_guard_task = "TASK-ADMINISTRATUM-CLOSE-GUARD-V0_1"
    safe_reset_session(close_guard_task)
    run_start_close_guard = run_cmd([py, "scripts/administratum_task_start_v0_1.py", "--task-id", close_guard_task, "--required-stage-id", "GUARD-STAGE-1"])
    command_runs.append(run_start_close_guard)
    run_bad_close = run_cmd([py, "scripts/administratum_task_close_v0_1.py", "--task-id", close_guard_task, "--final-status", "CLOSED_PASS", "--required-stage-id", "GUARD-STAGE-1"])
    command_runs.append(run_bad_close)
    checks["task_close_rejects_missing_required_stages"] = run_start_close_guard["returncode"] == 0 and run_bad_close["returncode"] != 0
    if not checks["task_close_rejects_missing_required_stages"]:
        failures.append("task_close did not reject missing required stages as expected")

    # Guard 2: stop record should prevent CLOSED_PASS.
    stop_guard_task = "TASK-ADMINISTRATUM-STOP-GUARD-V0_1"
    safe_reset_session(stop_guard_task)
    run_start_stop_guard = run_cmd([py, "scripts/administratum_task_start_v0_1.py", "--task-id", stop_guard_task, "--required-stage-id", "STOP-STAGE-1"])
    command_runs.append(run_start_stop_guard)
    run_stop_guard = run_cmd([
        py,
        "scripts/administratum_task_stop_v0_1.py",
        "--task-id",
        stop_guard_task,
        "--failed-stage-id",
        "STOP-STAGE-1",
        "--stop-reason",
        "synthetic stop guard check",
        "--status",
        "STOPPED_PENDING_OWNER_APPROVAL",
        "--owner-approval-required",
        "true",
    ])
    command_runs.append(run_stop_guard)
    run_close_after_stop = run_cmd([py, "scripts/administratum_task_close_v0_1.py", "--task-id", stop_guard_task, "--final-status", "CLOSED_PASS", "--required-stage-id", "STOP-STAGE-1"])
    command_runs.append(run_close_after_stop)
    checks["task_stop_records_reason_and_blocks_closed_pass"] = (
        run_start_stop_guard["returncode"] == 0
        and run_stop_guard["returncode"] == 0
        and run_close_after_stop["returncode"] != 0
    )
    if not checks["task_stop_records_reason_and_blocks_closed_pass"]:
        failures.append("task_stop guard failed (stop reason or close-block behavior)")

    # Success lifecycle fixture with bundle build.
    success_fixture_task = "TASK-ADMINISTRATUM-LIFECYCLE-FIXTURE-V0_1"
    safe_reset_session(success_fixture_task)
    run_start_success = run_cmd([py, "scripts/administratum_task_start_v0_1.py", "--task-id", success_fixture_task, "--required-stage-id", "FIXTURE-STAGE-1"])
    command_runs.append(run_start_success)
    evidence_rel = write_fixture_evidence(
        success_fixture_task,
        "fixture_stage_1_evidence.json",
        {"fixture": "lifecycle", "status": "PASS"},
    )
    run_stage_success = run_cmd([
        py,
        "scripts/administratum_stage_report_v0_1.py",
        "--task-id",
        success_fixture_task,
        "--stage-id",
        "FIXTURE-STAGE-1",
        "--status",
        "PASS",
        "--checker-status",
        "PASS",
        "--evidence-path",
        evidence_rel,
    ])
    command_runs.append(run_stage_success)
    run_close_success = run_cmd([
        py,
        "scripts/administratum_task_close_v0_1.py",
        "--task-id",
        success_fixture_task,
        "--final-status",
        "CLOSED_PASS",
        "--required-stage-id",
        "FIXTURE-STAGE-1",
    ])
    command_runs.append(run_close_success)
    run_bundle_success = run_cmd([
        py,
        "scripts/administratum_build_task_bundle_v0_1.py",
        "--task-id",
        success_fixture_task,
    ])
    command_runs.append(run_bundle_success)

    bundle_ok = run_bundle_success["returncode"] == 0
    if bundle_ok:
        manifest_path = Path(run_bundle_success["stdout_json"]["bundle_manifest_path"])
        try:
            manifest = read_json(manifest_path)
            manifest_sources = {item.get("source_path") for item in manifest.get("artifacts", [])}
            bundle_ok = evidence_rel in manifest_sources
            if not bundle_ok:
                failures.append("bundle manifest does not include fixture evidence artifact")
        except Exception:
            bundle_ok = False
            failures.append("failed to parse bundle manifest from success fixture")
    checks["bundle_builder_collects_session_evidence"] = (
        run_start_success["returncode"] == 0
        and run_stage_success["returncode"] == 0
        and run_close_success["returncode"] == 0
        and bundle_ok
    )
    if not checks["bundle_builder_collects_session_evidence"]:
        failures.append("success fixture lifecycle flow failed")

    failstop_ok, failstop_note = failstop_expectation_check(args.expected_failstop_task_id)
    checks["expected_failstop_semantics_ok"] = failstop_ok
    if not failstop_ok:
        failures.append(failstop_note)

    overall_status = "PASS" if all(checks.values()) else "FAIL"
    payload = {
        "schema_version": "administratum_check_all_report_v0_1",
        "status": overall_status,
        "checked_utc": utc_now(),
        "checks": checks,
        "failures": failures,
        "command_runs": command_runs,
        "notes": {
            "expected_failstop_check": failstop_note,
        },
    }
    write_json(report_path, payload)
    print(json.dumps(payload, ensure_ascii=True))
    return 0 if overall_status == "PASS" else 1


if __name__ == "__main__":
    sys.exit(main())
