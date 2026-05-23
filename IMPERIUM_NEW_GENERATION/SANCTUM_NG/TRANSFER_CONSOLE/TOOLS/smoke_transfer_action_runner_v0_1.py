#!/usr/bin/env python3
"""Smoke-test Transfer Action Runner foundation via bounded local receipts."""

from __future__ import annotations

import argparse
import datetime as dt
import json
import subprocess
from pathlib import Path
from typing import Any

TASK_ID_DEFAULT = "TASK-20260523-NEWGEN-SANCTUM-TRANSFER-ACTION-RUNNER-VM3-V0_1"
BASE_REL = "IMPERIUM_NEW_GENERATION/SANCTUM_NG/TRANSFER_CONSOLE"
RUNNER_REL = f"{BASE_REL}/TOOLS/transfer_action_runner_v0_1.py"
VALIDATOR_REL = f"{BASE_REL}/TOOLS/validate_transfer_action_runner_v0_1.py"
VIEW_STATE_REL = f"{BASE_REL}/DATA/TRANSFER_CONSOLE_VIEW_STATE.generated.json"


EXPECTED_PASS_ACTIONS = [
    "VALIDATE_TRANSFER_REQUEST",
    "DRY_RUN_TRANSFER",
    "SEND_TASKPACK_ZIP",
    "FETCH_REPORT_BUNDLE_ZIP",
    "REGISTER_TRANSFER_RESULT",
]


def utc_now() -> str:
    return dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def parse_kv(stdout: str) -> dict[str, str]:
    out: dict[str, str] = {}
    for line in stdout.splitlines():
        line = line.strip()
        if "=" not in line:
            continue
        key, value = line.split("=", 1)
        out[key.strip()] = value.strip()
    return out


def run_cmd(cmd: list[str], repo_root: Path) -> dict[str, Any]:
    proc = subprocess.run(
        cmd,
        cwd=repo_root,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        check=False,
    )
    return {
        "command": cmd,
        "returncode": proc.returncode,
        "stdout": proc.stdout.strip(),
        "stderr": proc.stderr.strip(),
        "parsed": parse_kv(proc.stdout.strip()),
    }


def add_step(
    steps: list[dict[str, Any]],
    warnings: list[str],
    blockers: list[str],
    step: str,
    status: str,
    details: Any,
    warning_id: str | None = None,
    blocker_id: str | None = None,
) -> None:
    steps.append({"step": step, "status": status, "details": details})
    if status == "WARN" and warning_id:
        warnings.append(warning_id)
    if status == "BLOCK" and blocker_id:
        blockers.append(blocker_id)


def parse_args() -> argparse.Namespace:
    script_path = Path(__file__).resolve()
    default_repo_root = script_path.parents[4]
    default_report_dir = default_repo_root / f"{BASE_REL}/REPORTS/{TASK_ID_DEFAULT}"
    default_output = default_report_dir / "transfer_action_runner_smoke_report.json"

    parser = argparse.ArgumentParser(description="Smoke test transfer action runner foundation.")
    parser.add_argument("--repo-root", type=Path, default=default_repo_root)
    parser.add_argument("--task-id", default=TASK_ID_DEFAULT)
    parser.add_argument("--report-dir", type=Path, default=default_report_dir)
    parser.add_argument("--output", type=Path, default=default_output)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    repo_root = args.repo_root.resolve()
    report_dir = args.report_dir.resolve()
    output_path = args.output.resolve()

    steps: list[dict[str, Any]] = []
    warnings: list[str] = []
    blockers: list[str] = []

    runner = repo_root / RUNNER_REL
    validator = repo_root / VALIDATOR_REL

    for action_id in EXPECTED_PASS_ACTIONS:
        cmd = [
            "python3",
            str(runner),
            "--repo-root",
            str(repo_root),
            "--task-id",
            str(args.task_id),
            "--action-id",
            action_id,
            "--report-dir",
            str(report_dir),
        ]
        run = run_cmd(cmd, repo_root)
        runner_status = str(run.get("parsed", {}).get("transfer_action_runner_status", ""))
        ok = run["returncode"] == 0 and runner_status in {"PASS", "WARN"}
        add_step(
            steps,
            warnings,
            blockers,
            f"action_{action_id}",
            "PASS" if ok else "BLOCK",
            run,
            blocker_id=f"action_{action_id.lower()}_failed",
        )

    execute_block_cmd = [
        "python3",
        str(runner),
        "--repo-root",
        str(repo_root),
        "--task-id",
        str(args.task_id),
        "--action-id",
        "SEND_TASKPACK_ZIP",
        "--mode",
        "EXECUTE",
        "--report-dir",
        str(report_dir),
    ]
    execute_block_run = run_cmd(execute_block_cmd, repo_root)
    execute_block_status = str(execute_block_run.get("parsed", {}).get("transfer_action_runner_status", ""))
    execute_block_ok = execute_block_run["returncode"] != 0 and execute_block_status == "BLOCK"
    add_step(
        steps,
        warnings,
        blockers,
        "execute_requires_owner_approval",
        "PASS" if execute_block_ok else "BLOCK",
        execute_block_run,
        blocker_id="execute_owner_approval_gate_failed",
    )

    view_state_path = repo_root / VIEW_STATE_REL
    try:
        view_state = json.loads(view_state_path.read_text(encoding="utf-8"))
    except Exception as exc:  # defensive
        view_state = None
        add_step(
            steps,
            warnings,
            blockers,
            "view_state_parse",
            "BLOCK",
            str(exc),
            blocker_id="view_state_parse_failed",
        )
    else:
        add_step(steps, warnings, blockers, "view_state_parse", "PASS", "view state parse ok")

    if isinstance(view_state, dict):
        runner_state = view_state.get("action_runner_state", {})
        contour_cards = view_state.get("contour_cards", [])
        has_runner_state = isinstance(runner_state, dict) and len(runner_state) > 0
        has_contours = isinstance(contour_cards, list) and len(contour_cards) >= 3
        has_requests = isinstance(runner_state.get("latest_action_requests", []), list)
        has_results = isinstance(runner_state.get("latest_action_results", []), list)

        add_step(
            steps,
            warnings,
            blockers,
            "runner_state_visible",
            "PASS" if has_runner_state else "BLOCK",
            {"has_runner_state": has_runner_state},
            blocker_id="runner_state_missing",
        )
        add_step(
            steps,
            warnings,
            blockers,
            "contour_cards_visible",
            "PASS" if has_contours else "BLOCK",
            {"contour_count": len(contour_cards) if isinstance(contour_cards, list) else 0},
            blocker_id="contour_cards_missing",
        )
        add_step(
            steps,
            warnings,
            blockers,
            "runner_request_result_lists",
            "PASS" if has_requests and has_results else "BLOCK",
            {
                "has_request_list": has_requests,
                "has_result_list": has_results,
            },
            blocker_id="runner_request_result_lists_missing",
        )

    validator_cmd = [
        "python3",
        str(validator),
        "--repo-root",
        str(repo_root),
        "--task-id",
        str(args.task_id),
        "--report-dir",
        str(report_dir),
        "--output",
        str(report_dir / "transfer_action_runner_validator_report.json"),
    ]
    validator_run = run_cmd(validator_cmd, repo_root)
    validator_verdict = str(validator_run.get("parsed", {}).get("transfer_action_runner_validator_verdict", "UNKNOWN"))
    validator_ok = validator_run["returncode"] == 0 and validator_verdict in {"PASS", "WARN"}
    add_step(
        steps,
        warnings,
        blockers,
        "validator_run",
        "PASS" if validator_ok else "BLOCK",
        validator_run,
        blocker_id="validator_run_failed",
    )

    verdict = "PASS"
    if blockers:
        verdict = "BLOCK"
    elif warnings:
        verdict = "WARN"

    report = {
        "schema_id": "TRANSFER_ACTION_RUNNER_SMOKE_REPORT_V0_1",
        "task_id": str(args.task_id),
        "generated_at_utc": utc_now(),
        "verdict": verdict,
        "steps": steps,
        "warnings": warnings,
        "blockers": blockers,
        "claim_boundary": "FOUNDATION_ONLY",
        "no_fake_green_note": "Smoke requires receipts and explicit negative-case blocking checks.",
    }

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    print(f"transfer_action_runner_smoke_verdict={verdict}")
    print(f"transfer_action_runner_smoke_report={output_path.relative_to(repo_root).as_posix()}")
    return 0 if verdict in {"PASS", "WARN"} else 1


if __name__ == "__main__":
    raise SystemExit(main())
