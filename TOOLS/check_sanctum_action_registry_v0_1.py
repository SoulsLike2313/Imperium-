#!/usr/bin/env python3
from __future__ import annotations

import argparse
import datetime as dt
import json
import subprocess
import sys
from pathlib import Path
from typing import Any

TASK_ID = "TASK-20260513-SANCTUM-ACTION-REGISTRY-V0_1"
SCHEMA_VERSION = "imperium.sanctum_action_registry_check.v0_1"
RUNTIME_REL = ".imperium_runtime/sanctum/action_registry_check"
REPORT_NAME = "SANCTUM_ACTION_REGISTRY_CHECK_REPORT.json"
VERDICT_NAME = "SANCTUM_ACTION_REGISTRY_CHECK_VERDICT.md"
RECEIPT_NAME = "SANCTUM_ACTION_REGISTRY_CHECK_RECEIPT.json"

SCHEMA_REL = "schemas/sanctum_action_registry_v0_1.schema.json"
REGISTRY_REL = "SANCTUM/ACTIONS/ACTION_REGISTRY.json"
MATRIX_REL = "SANCTUM/ACTIONS/ACTION_TEST_MATRIX_V0_1.json"
DOC_REL = "DOCS/SANCTUM_ACTION_REGISTRY_V0_1.md"
NEXT_STEP_REL = "CURRENT_STATE/NEXT_ATOMIC_STEP.md"
CURRENT_TRUTH_REL = "CURRENT_STATE/ARC5_PREFIRE_CURRENT_TRUTH_20260513.json"
SANCTUM_BASELINE_REL = "SANCTUM/sanctum_v0_29_qt.py"

ASSET_PATHS = [
    "ASSETS",
    "SANCTUM/DESIGN_SYSTEM",
    "SANCTUM/UI_LAB",
]

REQUIRED_TOP_FIELDS = [
    "schema_version",
    "registry_id",
    "status",
    "created_at_utc",
    "task_id",
    "repo_truth_at_creation",
    "purpose",
    "sanctum_baseline",
    "act5_execution_ready",
    "ready_for_agent_status",
    "actions",
    "global_rules",
    "forbidden_patterns",
    "receipt_policy",
    "test_policy",
    "risk_policy",
    "next_steps",
]

REQUIRED_ACTION_FIELDS = [
    "action_id",
    "title",
    "status",
    "category",
    "risk_level",
    "handler_reference",
    "required_prechecks",
    "expected_receipts",
    "test_or_smoke_check",
    "no_fake_green_rules",
]

REQUIRED_ACTION_IDS = {
    "ACTION-REFRESH-CURRENT-TRUTH",
    "ACTION-RUN-GIT-CLI-CHECK",
    "ACTION-TEST-VM2-ROUTE",
    "ACTION-LIST-VM2-BUNDLES",
    "ACTION-FETCH-SELECTED-VM2-BUNDLE",
    "ACTION-ACCEPT-VM2-HANDOFF-PC-INTAKE",
    "ACTION-SYNC-VM2-EXACT-HEAD",
    "ACTION-OPEN-CURRENT-TASK-FOLDER",
    "ACTION-OPEN-ADVISORY-BUFFER",
    "ACTION-OPEN-ARC5-PREFIRE-ZONE",
    "ACTION-RUN-ACT5-PREFIRE-CHECKS",
    "ACTION-REGISTER-STAGE-PROGRESS-REPORT",
    "ACTION-ISSUE-ADMINISTRATUM-ACK",
    "ACTION-READY-FOR-AGENT-GATE-CHECK",
}

HIGH_RISK_LEVELS = {"HIGH_FILE_TRANSFER", "HIGH_GIT_WRITE", "HIGH_REMOTE_SYNC", "BLOCKED_DANGEROUS"}

ALLOWED_ACTION_STATUS = {
    "REGISTERED_CONCEPT",
    "REGISTERED_EXISTING_BEHAVIOR",
    "REGISTERED_NEEDS_HANDLER",
    "REGISTERED_NEEDS_TEST",
    "BLOCKED_UNSAFE",
    "DEPRECATED_DO_NOT_USE",
}

ALLOWED_RISK = {
    "LOW_OPEN_READONLY",
    "MEDIUM_STATE_REFRESH",
    "HIGH_FILE_TRANSFER",
    "HIGH_GIT_WRITE",
    "HIGH_REMOTE_SYNC",
    "BLOCKED_DANGEROUS",
}

ALLOWED_TEST_STATUS = {
    "TESTED_EXISTING",
    "SMOKE_DEFINED_NOT_RUN",
    "NEEDS_HANDLER_BEFORE_TEST",
    "BLOCKED_UNSAFE",
    "MANUAL_ONLY_FOR_NOW",
}


def now_utc() -> str:
    return dt.datetime.now(dt.timezone.utc).isoformat()


def add_unique(items: list[str], value: str) -> None:
    if value not in items:
        items.append(value)


def read_json_obj(path: Path) -> tuple[dict[str, Any] | None, str | None]:
    if not path.exists():
        return None, f"missing_file:{path.as_posix()}"
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:  # noqa: BLE001
        return None, f"invalid_json:{path.as_posix()}:{type(exc).__name__}"
    if not isinstance(payload, dict):
        return None, f"invalid_json_type:{path.as_posix()}"
    return payload, None


def run_git(repo_root: Path, args: list[str]) -> tuple[bool, str]:
    try:
        result = subprocess.run(
            ["git", *args],
            cwd=str(repo_root),
            capture_output=True,
            text=True,
            check=False,
        )
    except Exception as exc:  # noqa: BLE001
        return False, f"exception:{type(exc).__name__}:{exc}"
    if result.returncode != 0:
        return False, (result.stderr or result.stdout).strip()
    return True, result.stdout.strip()


def write_artifacts(repo_root: Path, report: dict[str, Any]) -> dict[str, str]:
    runtime_dir = repo_root / RUNTIME_REL
    runtime_dir.mkdir(parents=True, exist_ok=True)

    report_path = runtime_dir / REPORT_NAME
    verdict_path = runtime_dir / VERDICT_NAME
    receipt_path = runtime_dir / RECEIPT_NAME

    report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    lines: list[str] = [
        "# Sanctum Action Registry Check v0.1",
        "",
        f"- task_id: {TASK_ID}",
        f"- generated_at_utc: {report.get('generated_at_utc')}",
        f"- verdict: {report.get('verdict')}",
        f"- pass_count: {len(report.get('passes', []))}",
        f"- warn_count: {len(report.get('warnings', []))}",
        f"- blocked_count: {len(report.get('blocked', []))}",
    ]

    if report.get("blocked"):
        lines.extend(["", "## BLOCKED"])
        lines.extend(f"- {item}" for item in report["blocked"])

    if report.get("warnings"):
        lines.extend(["", "## WARN"])
        lines.extend(f"- {item}" for item in report["warnings"])

    if report.get("passes"):
        lines.extend(["", "## PASS"])
        lines.extend(f"- {item}" for item in report["passes"])

    verdict_path.write_text("\n".join(lines) + "\n", encoding="utf-8")

    receipt = {
        "schema_version": "imperium.sanctum_action_registry_check_receipt.v0_1",
        "task_id": TASK_ID,
        "generated_at_utc": now_utc(),
        "verdict": report.get("verdict"),
        "report_path": str(report_path),
        "verdict_path": str(verdict_path),
    }
    receipt_path.write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    return {
        "report": str(report_path),
        "verdict": str(verdict_path),
        "receipt": str(receipt_path),
    }


def build_report(repo_root: Path) -> dict[str, Any]:
    passes: list[str] = []
    warnings: list[str] = []
    blocked: list[str] = []

    required_paths = {
        "schema": repo_root / SCHEMA_REL,
        "registry": repo_root / REGISTRY_REL,
        "matrix": repo_root / MATRIX_REL,
        "doc": repo_root / DOC_REL,
        "next_step": repo_root / NEXT_STEP_REL,
        "current_truth": repo_root / CURRENT_TRUTH_REL,
        "sanctum_baseline": repo_root / SANCTUM_BASELINE_REL,
    }

    for key, path in required_paths.items():
        if path.exists():
            passes.append(f"file_exists:{key}:{path.relative_to(repo_root).as_posix()}")
        else:
            add_unique(blocked, f"missing_required_file:{key}:{path.relative_to(repo_root).as_posix()}")

    registry, reg_err = read_json_obj(required_paths["registry"])
    if reg_err:
        add_unique(blocked, reg_err)
        registry = None

    matrix, matrix_err = read_json_obj(required_paths["matrix"])
    if matrix_err:
        add_unique(blocked, matrix_err)
        matrix = None

    current_truth, truth_err = read_json_obj(required_paths["current_truth"])
    if truth_err:
        add_unique(blocked, truth_err)
        current_truth = None

    matrix_entries: dict[str, dict[str, Any]] = {}
    if matrix is not None:
        entries = matrix.get("entries")
        if not isinstance(entries, list):
            add_unique(blocked, "matrix_entries_not_list")
        else:
            for idx, entry in enumerate(entries):
                if not isinstance(entry, dict):
                    add_unique(blocked, f"matrix_entry_not_object:{idx}")
                    continue
                action_id = entry.get("action_id")
                if not isinstance(action_id, str) or not action_id.strip():
                    add_unique(blocked, f"matrix_entry_missing_action_id:{idx}")
                    continue
                matrix_entries[action_id] = entry

                test_status = entry.get("test_status")
                if test_status in ALLOWED_TEST_STATUS:
                    passes.append(f"matrix_test_status_allowed:{action_id}:{test_status}")
                else:
                    add_unique(blocked, f"matrix_invalid_test_status:{action_id}:{test_status}")

    if registry is not None:
        for field in REQUIRED_TOP_FIELDS:
            if field in registry:
                passes.append(f"registry_top_field_present:{field}")
            else:
                add_unique(blocked, f"registry_missing_top_field:{field}")

        if registry.get("schema_version") == "imperium.sanctum_action_registry.v0_1":
            passes.append("registry_schema_version_ok")
        else:
            add_unique(blocked, "registry_schema_version_mismatch")

        if registry.get("act5_execution_ready") is False:
            passes.append("registry_act5_execution_ready_false")
        else:
            add_unique(blocked, "registry_act5_execution_ready_must_be_false")

        if registry.get("ready_for_agent_status") is False:
            passes.append("registry_ready_for_agent_status_false")
        else:
            add_unique(blocked, "registry_ready_for_agent_status_must_be_false")

        if registry.get("sanctum_baseline") == SANCTUM_BASELINE_REL:
            passes.append("registry_sanctum_baseline_ok")
        else:
            add_unique(blocked, "registry_sanctum_baseline_mismatch")

        if isinstance(registry.get("risk_policy"), dict):
            passes.append("registry_risk_policy_present")
        else:
            add_unique(blocked, "registry_risk_policy_missing_or_invalid")

        global_rules = registry.get("global_rules")
        if isinstance(global_rules, list):
            global_text = "\n".join(str(item).lower() for item in global_rules)
            if "fake green" in global_text:
                passes.append("global_rules_include_no_fake_green")
            else:
                add_unique(blocked, "global_rules_missing_no_fake_green_clause")
            if "ready_for_agent true" in global_text:
                passes.append("global_rules_include_no_ready_for_agent_true_clause")
            else:
                add_unique(blocked, "global_rules_missing_ready_for_agent_true_clause")
        else:
            add_unique(blocked, "global_rules_not_list")

        actions = registry.get("actions")
        action_map: dict[str, dict[str, Any]] = {}
        if not isinstance(actions, list):
            add_unique(blocked, "actions_not_list")
        else:
            for idx, action in enumerate(actions):
                if not isinstance(action, dict):
                    add_unique(blocked, f"action_not_object:{idx}")
                    continue
                action_id = action.get("action_id")
                if not isinstance(action_id, str) or not action_id.strip():
                    add_unique(blocked, f"action_missing_id:{idx}")
                    continue
                action_map[action_id] = action

                for field in REQUIRED_ACTION_FIELDS:
                    if field in action:
                        passes.append(f"action_field_present:{action_id}:{field}")
                    else:
                        add_unique(blocked, f"action_missing_field:{action_id}:{field}")

                status = action.get("status")
                if status not in ALLOWED_ACTION_STATUS:
                    add_unique(blocked, f"action_invalid_status:{action_id}:{status}")

                risk = action.get("risk_level")
                if risk not in ALLOWED_RISK:
                    add_unique(blocked, f"action_invalid_risk_level:{action_id}:{risk}")

                handler_ref = str(action.get("handler_reference", "")).strip()
                handler_type = str(action.get("handler_type", "")).strip()
                impl_status = str(action.get("implementation_status", "")).strip()

                if not handler_ref:
                    add_unique(blocked, f"action_missing_handler_reference:{action_id}")

                lower_ref = handler_ref.lower()
                if "sanctum ee" in lower_ref or "v0.30ee" in lower_ref or "/r1" in lower_ref or "/r2" in lower_ref:
                    add_unique(blocked, f"action_references_rejected_ee_r2_line:{action_id}")

                if handler_type.upper() == "RAW_SHELL_COMMAND":
                    add_unique(blocked, f"action_uses_raw_shell_handler_type:{action_id}")

                if ("bash -lc" in lower_ref or "powershell -executionpolicy" in lower_ref) and handler_type in {
                    "PYTHON_METHOD_VIA_UI",
                    "DIRECT_UI_CALL",
                    "RAW_SHELL_COMMAND",
                }:
                    add_unique(blocked, f"direct_ui_shell_string_forbidden:{action_id}")

                prechecks = action.get("required_prechecks")
                receipts = action.get("expected_receipts")
                if risk in HIGH_RISK_LEVELS:
                    if not isinstance(prechecks, list) or len(prechecks) == 0:
                        add_unique(blocked, f"high_risk_missing_prechecks:{action_id}")
                    else:
                        passes.append(f"high_risk_prechecks_present:{action_id}")
                    if not isinstance(receipts, list) or len(receipts) == 0:
                        add_unique(blocked, f"high_risk_missing_expected_receipts:{action_id}")
                    else:
                        passes.append(f"high_risk_receipts_present:{action_id}")

                if action_id in matrix_entries:
                    test_entry = matrix_entries[action_id]
                    test_status = str(test_entry.get("test_status", ""))
                else:
                    test_entry = None
                    test_status = "MISSING"
                    add_unique(blocked, f"action_missing_test_matrix_entry:{action_id}")

                # No false claims of full implementation without test/handler evidence.
                if status == "REGISTERED_EXISTING_BEHAVIOR":
                    if "missing" in lower_ref:
                        add_unique(blocked, f"existing_behavior_with_missing_handler:{action_id}")
                    if test_status == "NEEDS_HANDLER_BEFORE_TEST":
                        add_unique(blocked, f"existing_behavior_without_testability:{action_id}")
                if "FULLY_IMPLEMENTED" in impl_status.upper() and test_status in {"NEEDS_HANDLER_BEFORE_TEST", "MISSING"}:
                    add_unique(blocked, f"full_implementation_claim_without_test_evidence:{action_id}")

                if status in {"REGISTERED_CONCEPT", "REGISTERED_NEEDS_HANDLER"}:
                    if "IMPLEMENTED_IN_SANCTUM_BASELINE" in impl_status.upper():
                        add_unique(blocked, f"concept_or_needs_handler_claims_implemented_baseline:{action_id}")
                    else:
                        add_unique(warnings, f"action_not_yet_implemented:{action_id}:{status}")

            missing_required_actions = sorted(REQUIRED_ACTION_IDS - set(action_map.keys()))
            if missing_required_actions:
                add_unique(blocked, f"missing_required_actions:{'|'.join(missing_required_actions)}")
            else:
                passes.append("all_required_actions_present")

    if current_truth is not None:
        if current_truth.get("act5_execution_ready") is False:
            passes.append("current_truth_act5_execution_ready_false")
        else:
            add_unique(blocked, "current_truth_act5_execution_ready_must_be_false")

        if current_truth.get("ready_for_agent_status") is False:
            passes.append("current_truth_ready_for_agent_status_false")
        else:
            add_unique(blocked, "current_truth_ready_for_agent_status_must_be_false")

    next_step_path = required_paths["next_step"]
    if next_step_path.exists():
        next_text = next_step_path.read_text(encoding="utf-8").lower()
        if "step 6 completed by this task" in next_text and "sanctum action registry v0.1" in next_text:
            passes.append("next_atomic_step_mentions_step6_completion")
        else:
            add_unique(blocked, "next_atomic_step_missing_step6_completion")

        if "dangerous button without action registry/gates/receipts" in next_text:
            passes.append("next_atomic_step_forbids_ungated_dangerous_buttons")
        else:
            add_unique(blocked, "next_atomic_step_missing_dangerous_button_forbidden_clause")

    # Detect early asset creation.
    for rel in ASSET_PATHS:
        path = repo_root / rel
        if path.exists():
            add_unique(blocked, f"assets_created_too_early:{rel}")
        else:
            passes.append(f"assets_not_created_in_step6:{rel}")

    # Detect forbidden Sanctum rewrite (baseline file changed in working tree).
    ok_status, status_text = run_git(repo_root, ["status", "--short"])
    if not ok_status:
        add_unique(warnings, f"git_status_unavailable:{status_text}")
    else:
        if "SANCTUM/sanctum_v0_29_qt.py" in status_text:
            add_unique(blocked, "sanctum_baseline_file_modified_detected")
        else:
            passes.append("sanctum_baseline_file_not_modified_in_step6")

    verdict = "PASS"
    if blocked:
        verdict = "BLOCKED"
    elif warnings:
        verdict = "WARN"

    return {
        "schema_version": SCHEMA_VERSION,
        "task_id": TASK_ID,
        "generated_at_utc": now_utc(),
        "repo_root": str(repo_root),
        "verdict": verdict,
        "passes": passes,
        "warnings": warnings,
        "blocked": blocked,
        "counts": {
            "pass": len(passes),
            "warn": len(warnings),
            "blocked": len(blocked),
        },
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Check Sanctum Action Registry v0.1 contracts and guardrails.")
    parser.add_argument("--repo-root", default=".", help="Repository root path")
    parser.add_argument("--human", action="store_true", help="Print human-readable output")
    parser.add_argument("--json", action="store_true", help="Print JSON output")
    return parser.parse_args()


def print_human(report: dict[str, Any], artifacts: dict[str, str]) -> None:
    print("PASS")
    for item in report.get("passes", []):
        print(f"- {item}")

    print("WARN")
    for item in report.get("warnings", []):
        print(f"- {item}")

    print("BLOCKED")
    for item in report.get("blocked", []):
        print(f"- {item}")

    print(f"VERDICT: {report.get('verdict')}")
    print(f"REPORT: {artifacts['report']}")
    print(f"VERDICT_MD: {artifacts['verdict']}")
    print(f"RECEIPT: {artifacts['receipt']}")


def main() -> int:
    args = parse_args()
    repo_root = Path(args.repo_root).resolve()

    report = build_report(repo_root)
    artifacts = write_artifacts(repo_root, report)

    if args.json:
        print(json.dumps(report, ensure_ascii=False, indent=2))

    if args.human or not args.json:
        print_human(report, artifacts)

    return 2 if report.get("blocked") else 0


if __name__ == "__main__":
    sys.exit(main())
