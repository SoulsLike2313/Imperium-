#!/usr/bin/env python3
"""Validate Transfer Action Runner foundation artifacts and safety boundaries."""

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
SAMPLES_BUILDER_REL = f"{BASE_REL}/TOOLS/build_transfer_action_samples_v0_1.py"
VIEW_STATE_REL = f"{BASE_REL}/DATA/TRANSFER_CONSOLE_VIEW_STATE.generated.json"
ACTION_RESULTS_DIR_REL = f"{BASE_REL}/DATA/action_results"

REQUIRED_NEW_ACTION_IDS = {
    "SEND_TASKPACK_ZIP",
    "FETCH_REPORT_BUNDLE_ZIP",
    "REGISTER_TRANSFER_RESULT",
    "VALIDATE_TRANSFER_REQUEST",
    "DRY_RUN_TRANSFER",
}


def utc_now() -> str:
    return dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def load_json(path: Path) -> tuple[dict[str, Any] | None, str | None]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        return None, "missing"
    except json.JSONDecodeError as exc:
        return None, f"json_decode_error:{exc}"
    if not isinstance(payload, dict):
        return None, "not_json_object"
    return payload, None


def add_check(
    checks: list[dict[str, str]],
    warnings: list[str],
    blockers: list[str],
    check_id: str,
    ok: bool,
    pass_detail: str,
    fail_detail: str,
    fail_level: str = "BLOCK",
) -> None:
    if ok:
        checks.append({"check_id": check_id, "status": "PASS", "details": pass_detail})
        return

    checks.append({"check_id": check_id, "status": fail_level, "details": fail_detail})
    if fail_level == "WARN":
        warnings.append(f"{check_id}:{fail_detail}")
    else:
        blockers.append(f"{check_id}:{fail_detail}")


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


def list_results(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    out: list[dict[str, Any]] = []
    for item in sorted(path.glob("*.json")):
        payload, _err = load_json(item)
        if payload is not None:
            payload["_path"] = item
            out.append(payload)
    return out


def parse_args() -> argparse.Namespace:
    script_path = Path(__file__).resolve()
    default_repo_root = script_path.parents[4]
    default_report_dir = default_repo_root / f"{BASE_REL}/REPORTS/{TASK_ID_DEFAULT}"
    default_output = default_report_dir / "transfer_action_runner_validator_report.json"

    parser = argparse.ArgumentParser(description="Validate transfer action runner foundation.")
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

    checks: list[dict[str, str]] = []
    warnings: list[str] = []
    blockers: list[str] = []

    required_files = [
        repo_root / f"{BASE_REL}/CONTRACTS/transfer_action_request.schema.json",
        repo_root / f"{BASE_REL}/CONTRACTS/transfer_action_result.schema.json",
        repo_root / f"{BASE_REL}/CONTRACTS/transfer_action_runner_policy.schema.json",
        repo_root / f"{BASE_REL}/TOOLS/transfer_action_runner_v0_1.py",
        repo_root / f"{BASE_REL}/TOOLS/build_transfer_action_samples_v0_1.py",
        repo_root / f"{BASE_REL}/TOOLS/validate_transfer_action_runner_v0_1.py",
        repo_root / f"{BASE_REL}/TOOLS/smoke_transfer_action_runner_v0_1.py",
        repo_root / "IMPERIUM_NEW_GENERATION/SANCTUM_NG/REGISTRY/SANCTUM_NG_ACTION_REGISTRY_V0_1.json",
        repo_root / "IMPERIUM_NEW_GENERATION/SANCTUM_NG/TOOLS/sanctum_ng_action_server.py",
        repo_root / "IMPERIUM_NEW_GENERATION/SANCTUM_NG/APP/index.html",
        repo_root / "IMPERIUM_NEW_GENERATION/SANCTUM_NG/APP/app.js",
    ]

    add_check(
        checks,
        warnings,
        blockers,
        "core_files_exist",
        all(path.exists() for path in required_files),
        "core transfer action runner files exist",
        "one or more required transfer action runner files are missing",
    )

    for schema_rel, check_id in [
        (f"{BASE_REL}/CONTRACTS/transfer_action_request.schema.json", "request_schema_parse"),
        (f"{BASE_REL}/CONTRACTS/transfer_action_result.schema.json", "result_schema_parse"),
        (f"{BASE_REL}/CONTRACTS/transfer_action_runner_policy.schema.json", "policy_schema_parse"),
    ]:
        schema, schema_err = load_json(repo_root / schema_rel)
        add_check(
            checks,
            warnings,
            blockers,
            check_id,
            schema is not None,
            f"{Path(schema_rel).name} parses",
            f"{Path(schema_rel).name} parse failed ({schema_err})",
        )

    runner_text = (repo_root / RUNNER_REL).read_text(encoding="utf-8")
    add_check(
        checks,
        warnings,
        blockers,
        "runner_no_shell_true",
        "shell=True" not in runner_text,
        "runner does not use shell=True",
        "runner contains shell=True",
    )

    add_check(
        checks,
        warnings,
        blockers,
        "runner_no_arbitrary_exec_patterns",
        all(token not in runner_text for token in ["os.system(", "bash -c", "powershell -Command"]),
        "runner does not use arbitrary command execution patterns",
        "runner includes forbidden arbitrary command execution pattern",
    )

    registry, registry_err = load_json(repo_root / "IMPERIUM_NEW_GENERATION/SANCTUM_NG/REGISTRY/SANCTUM_NG_ACTION_REGISTRY_V0_1.json")
    action_ids: set[str] = set()
    if registry is not None:
        raw_actions = registry.get("actions", [])
        if isinstance(raw_actions, list):
            for item in raw_actions:
                if isinstance(item, dict):
                    action_id = str(item.get("action_id", "")).strip()
                    if action_id:
                        action_ids.add(action_id)

    add_check(
        checks,
        warnings,
        blockers,
        "registry_has_new_action_runner_actions",
        REQUIRED_NEW_ACTION_IDS.issubset(action_ids),
        "action registry contains new transfer action runner action IDs",
        f"registry missing action runner IDs: {sorted(REQUIRED_NEW_ACTION_IDS - action_ids)}",
    )

    server_text = (repo_root / "IMPERIUM_NEW_GENERATION/SANCTUM_NG/TOOLS/sanctum_ng_action_server.py").read_text(encoding="utf-8")
    add_check(
        checks,
        warnings,
        blockers,
        "server_dispatch_has_new_actions",
        all(token in server_text for token in REQUIRED_NEW_ACTION_IDS),
        "action server dispatch includes new transfer action runner actions",
        "action server dispatch is missing one or more new transfer action runner actions",
    )

    add_check(
        checks,
        warnings,
        blockers,
        "server_points_to_new_runner",
        "transfer_action_runner_v0_1.py" in server_text,
        "action server references transfer action runner script",
        "action server does not reference transfer action runner script",
    )

    build_cmd = [
        "python3",
        str(repo_root / SAMPLES_BUILDER_REL),
        "--repo-root",
        str(repo_root),
        "--task-id",
        str(args.task_id),
        "--report-dir",
        str(report_dir),
        "--output",
        str(report_dir / "transfer_action_samples_build_report.json"),
    ]
    build_run = run_cmd(build_cmd, repo_root)
    build_verdict = str(build_run.get("parsed", {}).get("transfer_action_samples_build_verdict", "UNKNOWN"))
    add_check(
        checks,
        warnings,
        blockers,
        "samples_builder_runs",
        build_run["returncode"] == 0,
        f"sample builder ran (verdict={build_verdict})",
        f"sample builder failed: {build_run['stderr'] or build_run['stdout']}",
    )

    bad_action_request = {
        "schema_id": "TRANSFER_ACTION_REQUEST_V0_1",
        "request_id": "VALIDATOR-BAD-ACTION",
        "task_id": str(args.task_id),
        "action_type": "UNKNOWN_ACTION",
        "source_contour": "PC",
        "target_contour": "VM3",
        "artifact_type": "taskpack_zip",
        "artifact_name": "bad.zip",
        "source_path": "INBOX/VM3_TASKPACKS/TASK-20260523-NEWGEN-SANCTUM-TRANSFER-ACTION-RUNNER-VM3-V0_1/TASKPACK_TASK-20260523-NEWGEN-SANCTUM-TRANSFER-ACTION-RUNNER-VM3-V0_1.zip",
        "target_path": "/home/vboxuser3/IMPERIUM_WORK/Imperium-/INBOX/VM3_TASKPACKS/TASK-20260523-NEWGEN-SANCTUM-TRANSFER-ACTION-RUNNER-VM3-V0_1/target.zip",
        "mode": "DRY_RUN",
        "owner_approval_required": True,
        "owner_approved": False,
        "rollback_plan": "IMPERIUM_NEW_GENERATION/TRUTH/ACTION_ROLLBACK/ACTION_ROLLBACK_POLICY_V0_1.json",
        "allowed_command_profile": "DRY_RUN_ONLY",
        "created_at_utc": utc_now(),
        "status": "REQUESTED",
        "claim_boundary": "FOUNDATION_ONLY"
    }
    bad_contour_request = {**bad_action_request, "request_id": "VALIDATOR-BAD-CONTOUR", "action_type": "SEND_TASKPACK_ZIP", "source_contour": "VMX"}
    bad_path_request = {**bad_action_request, "request_id": "VALIDATOR-BAD-PATH", "action_type": "SEND_TASKPACK_ZIP", "source_path": "/tmp/unsafe_input.zip", "target_path": "/tmp/unsafe_output.zip"}

    bad_action_path = report_dir / "validator_bad_action_request.json"
    bad_contour_path = report_dir / "validator_bad_contour_request.json"
    bad_path_path = report_dir / "validator_bad_path_request.json"

    for path, payload in [
        (bad_action_path, bad_action_request),
        (bad_contour_path, bad_contour_request),
        (bad_path_path, bad_path_request),
    ]:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    def run_validate_case(case_path: Path, report_name: str) -> dict[str, Any]:
        return run_cmd(
            [
                "python3",
                str(repo_root / RUNNER_REL),
                "--repo-root",
                str(repo_root),
                "--task-id",
                str(args.task_id),
                "--action-id",
                "VALIDATE_TRANSFER_REQUEST",
                "--request-file",
                str(case_path),
                "--report-dir",
                str(report_dir),
                "--output-report",
                str(report_dir / report_name),
            ],
            repo_root,
        )

    bad_action_run = run_validate_case(bad_action_path, "validator_bad_action_action_report.json")
    bad_contour_run = run_validate_case(bad_contour_path, "validator_bad_contour_action_report.json")
    bad_path_run = run_validate_case(bad_path_path, "validator_bad_path_action_report.json")

    for check_id, run in [
        ("runner_rejects_unknown_action_type", bad_action_run),
        ("runner_rejects_unknown_contour", bad_contour_run),
        ("runner_rejects_unsafe_path", bad_path_run),
    ]:
        status = str(run.get("parsed", {}).get("transfer_action_runner_status", ""))
        ok = run["returncode"] != 0 and status == "BLOCK"
        add_check(
            checks,
            warnings,
            blockers,
            check_id,
            ok,
            "rejection produced BLOCK as expected",
            f"unexpected rejection result returncode={run['returncode']} status={status}",
        )

    dry_run_exec = run_cmd(
        [
            "python3",
            str(repo_root / RUNNER_REL),
            "--repo-root",
            str(repo_root),
            "--task-id",
            str(args.task_id),
            "--action-id",
            "DRY_RUN_TRANSFER",
            "--report-dir",
            str(report_dir),
            "--output-report",
            str(report_dir / "validator_dry_run_action_report.json"),
        ],
        repo_root,
    )

    dry_status = str(dry_run_exec.get("parsed", {}).get("transfer_action_runner_status", ""))
    dry_result_ref = dry_run_exec.get("parsed", {}).get("transfer_action_result_ref", "")
    dry_result_exists = bool(dry_result_ref) and (repo_root / str(dry_result_ref)).exists()

    add_check(
        checks,
        warnings,
        blockers,
        "dry_run_creates_result_receipt",
        dry_run_exec["returncode"] == 0 and dry_status in {"PASS", "WARN"} and dry_result_exists,
        "dry-run action generated a result receipt",
        f"dry-run receipt check failed returncode={dry_run_exec['returncode']} status={dry_status} result_ref={dry_result_ref}",
    )

    sent_without_evidence: list[str] = []
    for result in list_results(repo_root / ACTION_RESULTS_DIR_REL):
        status = str(result.get("status", ""))
        if status not in {"SENT", "FETCHED"}:
            continue
        refs = result.get("evidence_refs", [])
        if not isinstance(refs, list) or len(refs) == 0:
            sent_without_evidence.append(str(result.get("result_id", "UNKNOWN")))

    add_check(
        checks,
        warnings,
        blockers,
        "sent_fetched_require_evidence_refs",
        len(sent_without_evidence) == 0,
        "SENT/FETCHED result states include evidence refs",
        f"SENT/FETCHED missing evidence refs: {sent_without_evidence}",
    )

    view_state, view_state_err = load_json(repo_root / VIEW_STATE_REL)
    add_check(
        checks,
        warnings,
        blockers,
        "view_state_parse",
        view_state is not None,
        "transfer console view state parses",
        f"transfer console view state parse failed ({view_state_err})",
    )

    action_runner_state = view_state.get("action_runner_state", {}) if isinstance(view_state, dict) else {}
    add_check(
        checks,
        warnings,
        blockers,
        "view_state_has_action_runner_state",
        isinstance(action_runner_state, dict) and len(action_runner_state) > 0,
        "view state includes action_runner_state block",
        "view state does not include action_runner_state block",
    )

    add_check(
        checks,
        warnings,
        blockers,
        "view_state_no_arbitrary_shell_flag",
        bool(action_runner_state.get("no_arbitrary_shell_confirmed", False)),
        "view state confirms no-arbitrary-shell for action runner",
        "view state missing no_arbitrary_shell_confirmed=true",
    )

    report_bundle_files = [
        report_dir / "start_state.json",
        report_dir / "GATE_ACK.md",
        report_dir / "transfer_action_runner_validator_report.json",
        report_dir / "transfer_action_runner_smoke_report.json",
        report_dir / "implementation_manifest.json",
        report_dir / "context_source_mix.json",
        report_dir / "FINAL_REPORT.md",
    ]
    add_check(
        checks,
        warnings,
        blockers,
        "report_bundle_progress",
        all(path.exists() for path in report_bundle_files),
        "report bundle core files are present",
        "one or more report bundle core files are missing",
        fail_level="WARN",
    )

    verdict = "PASS"
    if blockers:
        verdict = "BLOCK"
    elif warnings:
        verdict = "WARN"

    report = {
        "schema_id": "TRANSFER_ACTION_RUNNER_VALIDATOR_REPORT_V0_1",
        "task_id": str(args.task_id),
        "generated_at_utc": utc_now(),
        "verdict": verdict,
        "checks": checks,
        "warnings": warnings,
        "blockers": blockers,
        "validator_runs": {
            "samples_builder": build_run,
            "bad_action": bad_action_run,
            "bad_contour": bad_contour_run,
            "bad_path": bad_path_run,
            "dry_run": dry_run_exec,
        },
        "no_fake_green_note": "Pass claims are constrained by receipt checks and explicit BLOCK/WARN branches.",
    }

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    print(f"transfer_action_runner_validator_verdict={verdict}")
    print(f"transfer_action_runner_validator_report={output_path.relative_to(repo_root).as_posix()}")
    return 0 if verdict in {"PASS", "WARN"} else 1


if __name__ == "__main__":
    raise SystemExit(main())
