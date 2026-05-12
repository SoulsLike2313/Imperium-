#!/usr/bin/env python3
from __future__ import annotations

import argparse
import datetime as dt
import json
import subprocess
import sys
from pathlib import Path
from typing import Any


TASK_ID = "TASK-20260513-SANCTUM-V0_30-TRUTH-DASHBOARD-LAYOUT-AND-BUNDLE-FETCH-FIX-V0_1"
STAGE_ID = "STAGE-001-SANCTUM-V0_30-UI-TRUTH-BINDING-VISUAL-AND-FETCH-REPAIR-V0_1"
STATE_REL = ".imperium_runtime/sanctum/state/SANCTUM_STATE_V0_1.json"
CHECK_DIR_REL = ".imperium_runtime/sanctum/checks"
REPORT_NAME = "SANCTUM_ADAPTIVE_OPERATOR_LAYER_CHECK.json"
VERDICT_NAME = "SANCTUM_ADAPTIVE_OPERATOR_LAYER_VERDICT.md"
RECEIPT_NAME = "SANCTUM_ADAPTIVE_OPERATOR_LAYER_RECEIPT.json"
EXPECTED_FRONTEND_MARKERS = [
    "IMPERIUM Sanctum v0.30 Adaptive Operator Dashboard",
    "Sanctum v0.30 UI shell + Adaptive Operator Layer v0.1",
    "Refresh Bundles",
    "Fetch Selected",
    "Fetch Latest",
    "ADAPTIVE OPERATOR CORE",
]


def utc_now_iso() -> str:
    return dt.datetime.now(dt.timezone.utc).isoformat()


def add_unique(items: list[str], value: str) -> None:
    if value not in items:
        items.append(value)


def read_json(path: Path) -> tuple[dict[str, Any] | None, str | None]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        return None, f"missing_file:{path.as_posix()}"
    except Exception as exc:  # noqa: BLE001
        return None, f"invalid_json:{path.as_posix()}:{type(exc).__name__}"
    if not isinstance(payload, dict):
        return None, f"invalid_json_type:{path.as_posix()}"
    return payload, None


def run_builder(repo_root: Path, state_path: Path) -> tuple[int, str]:
    command = [
        sys.executable,
        str(repo_root / "TOOLS/build_sanctum_state_v0_1.py"),
        "--repo-root",
        str(repo_root),
        "--out",
        str(state_path),
        "--human",
    ]
    result = subprocess.run(command, capture_output=True, text=True, check=False)
    output = "\n".join(
        [
            f"command: {' '.join(command)}",
            f"exit_code: {result.returncode}",
            "",
            "stdout:",
            result.stdout[-6000:],
            "",
            "stderr:",
            result.stderr[-6000:],
        ]
    )
    return result.returncode, output


def build_report(repo_root: Path) -> dict[str, Any]:
    blockers: list[str] = []
    warnings: list[str] = []
    details: dict[str, Any] = {}

    builder_path = repo_root / "TOOLS/build_sanctum_state_v0_1.py"
    checker_path = repo_root / "TOOLS/check_sanctum_adaptive_operator_layer_v0_1.py"
    frontend_path = repo_root / "SANCTUM/sanctum_v0_29_qt.py"
    state_path = repo_root / STATE_REL

    for required in (builder_path, checker_path, frontend_path):
        if not required.exists():
            add_unique(blockers, f"required_file_missing:{required.relative_to(repo_root).as_posix()}")

    if not blockers:
        exit_code, builder_output = run_builder(repo_root, state_path)
        details["builder_output"] = builder_output
        details["builder_exit_code"] = exit_code
        if exit_code != 0:
            add_unique(blockers, f"builder_nonzero_exit:{exit_code}")

    state_payload = None
    if not blockers:
        state_payload, err = read_json(state_path)
        if err:
            add_unique(blockers, err)

    if isinstance(state_payload, dict):
        required_top = [
            "schema_version",
            "generated_at_utc",
            "repo_root",
            "git_truth",
            "bundles",
            "receipts",
            "scriptorium",
            "arsenal",
            "act3_spine",
            "warnings",
            "operator_actions",
            "verdict",
        ]
        for key in required_top:
            if key not in state_payload:
                add_unique(blockers, f"state_missing_field:{key}")

        bundles = state_payload.get("bundles")
        if not isinstance(bundles, dict):
            add_unique(blockers, "state_bundles_not_object")
        else:
            for key in ("inboxes", "handoff_out", "discovered_bundles", "latest_bundle", "status_enum"):
                if key not in bundles:
                    add_unique(blockers, f"state_bundles_missing:{key}")
            status_enum = bundles.get("status_enum")
            expected_statuses = {
                "UNKNOWN",
                "REMOTE_ONLY",
                "FETCHED",
                "SHA_MISSING",
                "SHA_PASS",
                "SHA_FAIL",
                "REVIEWED",
                "NEEDS_OWNER_DECISION",
                "APPLIED",
                "COMMITTED",
                "STALE",
                "BLOCKED",
            }
            if isinstance(status_enum, list):
                missing = expected_statuses - {str(x) for x in status_enum}
                for item in sorted(missing):
                    add_unique(warnings, f"state_bundles_status_enum_missing:{item}")
            else:
                add_unique(blockers, "state_bundles_status_enum_not_list")

            discovered = bundles.get("discovered_bundles")
            if isinstance(discovered, list):
                for idx, item in enumerate(discovered[:10]):
                    if not isinstance(item, dict):
                        add_unique(warnings, f"state_bundles_discovered_item_not_object:{idx}")
                        continue
                    if "bundle_status" not in item:
                        add_unique(warnings, f"state_bundles_discovered_missing_bundle_status:{idx}")
                    if "sha256_pair_status" not in item:
                        add_unique(warnings, f"state_bundles_discovered_missing_sha_status:{idx}")
            else:
                add_unique(blockers, "state_bundles_discovered_not_list")

        truth = state_payload.get("git_truth")
        if not isinstance(truth, dict):
            add_unique(blockers, "state_git_truth_not_object")
        else:
            for key in (
                "local_head",
                "origin_master_head",
                "remote_master_head",
                "commit_count",
                "latest_commit_oneline",
                "exact_tree_url",
                "worktree_clean",
                "verdict",
            ):
                if key not in truth:
                    add_unique(blockers, f"state_git_truth_missing:{key}")

        scriptorium = state_payload.get("scriptorium")
        if isinstance(scriptorium, dict):
            reg_rel = scriptorium.get("registry_path")
            if isinstance(reg_rel, str):
                if not (repo_root / reg_rel).exists():
                    add_unique(blockers, f"scriptorium_registry_ref_missing:{reg_rel}")
        else:
            add_unique(blockers, "state_scriptorium_not_object")

        arsenal = state_payload.get("arsenal")
        if isinstance(arsenal, dict):
            for key in ("tool_index_path", "install_status_path"):
                rel = arsenal.get(key)
                if isinstance(rel, str):
                    if not (repo_root / rel).exists():
                        add_unique(blockers, f"arsenal_ref_missing:{key}:{rel}")
                else:
                    add_unique(blockers, f"state_arsenal_missing_ref:{key}")
        else:
            add_unique(blockers, "state_arsenal_not_object")

        act3 = state_payload.get("act3_spine")
        if isinstance(act3, dict):
            for key in (
                "zone_registry_status",
                "truth_source_registry_status",
                "capability_spine_status",
                "warning_stale_baseline_status",
            ):
                if key not in act3:
                    add_unique(blockers, f"state_act3_missing:{key}")
        else:
            add_unique(blockers, "state_act3_spine_not_object")

        receipts = state_payload.get("receipts")
        if isinstance(receipts, dict):
            for key in (
                "latest_git_cli_check",
                "latest_bundle_intake_review",
                "latest_act3_check",
                "latest_sanctum_state_receipt",
                "latest_sanctum_adaptive_check",
            ):
                if key not in receipts:
                    add_unique(blockers, f"state_receipts_missing:{key}")
        else:
            add_unique(blockers, "state_receipts_not_object")

        frontend_text = frontend_path.read_text(encoding="utf-8")
        if "AdaptiveOperatorPanel" not in frontend_text:
            add_unique(warnings, "frontend_adaptive_operator_panel_not_detected")
        if "build_sanctum_state_v0_1.py" not in frontend_text:
            add_unique(warnings, "frontend_state_refresh_hook_not_detected")
        if "TransferPanel" not in frontend_text:
            add_unique(warnings, "frontend_transfer_panel_not_detected")
        for marker in EXPECTED_FRONTEND_MARKERS:
            if marker not in frontend_text:
                add_unique(warnings, f"frontend_marker_missing:{marker}")

        state_verdict = str(state_payload.get("verdict", "UNKNOWN"))
        if state_verdict == "BLOCKED":
            add_unique(warnings, "state_verdict_blocked")

    verdict = "PASS"
    if blockers:
        verdict = "BLOCKED"
    elif warnings:
        verdict = "PASS_WITH_WARNINGS"

    return {
        "schema_version": "imperium.sanctum_adaptive_operator_layer_check.v0_1",
        "task_id": TASK_ID,
        "stage_id": STAGE_ID,
        "checked_at_utc": utc_now_iso(),
        "repo_root": str(repo_root),
        "state_path": STATE_REL,
        "frontend_path": "SANCTUM/sanctum_v0_29_qt.py",
        "verdict": verdict,
        "blockers": blockers,
        "warnings": warnings,
        "counts": {
            "blockers": len(blockers),
            "warnings": len(warnings),
        },
        "details": details,
    }


def write_outputs(repo_root: Path, report: dict[str, Any]) -> tuple[Path, Path, Path]:
    check_dir = repo_root / CHECK_DIR_REL
    check_dir.mkdir(parents=True, exist_ok=True)
    report_path = check_dir / REPORT_NAME
    verdict_path = check_dir / VERDICT_NAME
    receipt_path = check_dir / RECEIPT_NAME

    report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    lines = [
        "# SANCTUM ADAPTIVE OPERATOR LAYER CHECK",
        "",
        f"- task_id: {TASK_ID}",
        f"- stage_id: {STAGE_ID}",
        f"- checked_at_utc: {report.get('checked_at_utc')}",
        f"- verdict: {report.get('verdict')}",
        f"- blockers: {report['counts']['blockers']}",
        f"- warnings: {report['counts']['warnings']}",
        "",
    ]
    if report["blockers"]:
        lines.append("## Blockers")
        lines.extend([f"- {item}" for item in report["blockers"]])
        lines.append("")
    if report["warnings"]:
        lines.append("## Warnings")
        lines.extend([f"- {item}" for item in report["warnings"]])
        lines.append("")
    lines.append(f"=== DONE: SANCTUM ADAPTIVE CHECK {report.get('verdict')} ===")
    lines.append("")
    verdict_path.write_text("\n".join(lines), encoding="utf-8")

    receipt = {
        "schema_version": "imperium.receipt.v0_1",
        "receipt_id": "RECEIPT-SANCTUM-ADAPTIVE-OPERATOR-LAYER-CHECK-V0_1",
        "receipt_type": "sanctum_adaptive_operator_layer_check",
        "task_id": TASK_ID,
        "stage_id": STAGE_ID,
        "run_id": None,
        "issuer": "VM2_SERVITOR",
        "created_at_utc": utc_now_iso(),
        "command": "python3 TOOLS/check_sanctum_adaptive_operator_layer_v0_1.py --repo-root . --human",
        "inputs": [
            "TOOLS/build_sanctum_state_v0_1.py",
            "SANCTUM/sanctum_v0_29_qt.py",
            STATE_REL,
        ],
        "outputs": [
            report_path.relative_to(repo_root).as_posix(),
            verdict_path.relative_to(repo_root).as_posix(),
            receipt_path.relative_to(repo_root).as_posix(),
        ],
        "verdict": report.get("verdict"),
        "warnings": report.get("warnings", []),
        "blockers": report.get("blockers", []),
        "evidence_paths": [
            report_path.relative_to(repo_root).as_posix(),
            verdict_path.relative_to(repo_root).as_posix(),
        ],
        "git_truth_ref": ".imperium_runtime/sanctum/state/SANCTUM_STATE_V0_1.json",
    }
    receipt_path.write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    return report_path, verdict_path, receipt_path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Check Sanctum adaptive operator layer v0.1")
    parser.add_argument("--repo-root", default=".", help="Repository root")
    parser.add_argument("--human", action="store_true", help="Print human-readable summary")
    return parser.parse_args()


def print_human(report: dict[str, Any], report_path: Path, verdict_path: Path, receipt_path: Path) -> None:
    print("=== SANCTUM ADAPTIVE OPERATOR LAYER CHECK ===")
    print(f"repo_root: {report.get('repo_root')}")
    print(f"verdict: {report.get('verdict')}")
    print(f"blockers: {report['counts']['blockers']}")
    print(f"warnings: {report['counts']['warnings']}")
    print("outputs:")
    print(f"  report_json: {report_path}")
    print(f"  verdict_md: {verdict_path}")
    print(f"  receipt_json: {receipt_path}")


def main() -> int:
    args = parse_args()
    repo_root = Path(args.repo_root).resolve()
    report = build_report(repo_root)
    report_path, verdict_path, receipt_path = write_outputs(repo_root, report)
    if args.human:
        print_human(report, report_path, verdict_path, receipt_path)
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0 if report.get("verdict") in {"PASS", "PASS_WITH_WARNINGS"} else 2


if __name__ == "__main__":
    raise SystemExit(main())
