#!/usr/bin/env python3
from __future__ import annotations

import argparse
import datetime as dt
import json
import py_compile
import sys
from pathlib import Path
from typing import Any

TASK_ID = "TASK-20260513-WORK-SESSION-ADMINISTRATUM-ACK-V0_1"
SCHEMA_VERSION = "imperium.work_session_administratum_ack_check.v0_1"
RUNTIME_REL = ".imperium_runtime/administratum/work_session_ack_check"
REPORT_NAME = "WORK_SESSION_ADMINISTRATUM_ACK_CHECK_REPORT.json"
VERDICT_NAME = "WORK_SESSION_ADMINISTRATUM_ACK_CHECK_VERDICT.md"
RECEIPT_NAME = "WORK_SESSION_ADMINISTRATUM_ACK_CHECK_RECEIPT.json"

REQUIRED_FILES = {
    "work_session_schema": "schemas/work_session_v0_1.schema.json",
    "stage_progress_report_schema": "schemas/stage_progress_report_v0_1.schema.json",
    "administratum_ack_schema": "schemas/administratum_ack_v0_1.schema.json",
    "work_sessions_readme": "ORGANS/ADMINISTRATUM/REGISTRY/WORK_SESSIONS/README_WORK_SESSIONS_V0_1.md",
    "work_session_example": "ORGANS/ADMINISTRATUM/REGISTRY/WORK_SESSIONS/EXAMPLES/WORK_SESSION_EXAMPLE_V0_1.json",
    "stage_progress_example": "ORGANS/ADMINISTRATUM/REGISTRY/STAGE_PROGRESS_REPORTS/EXAMPLES/STAGE_PROGRESS_REPORT_EXAMPLE_V0_1.json",
    "ack_example": "ORGANS/ADMINISTRATUM/REGISTRY/ACKS/EXAMPLES/ADMINISTRATUM_ACK_EXAMPLE_V0_1.json",
    "register_tool": "TOOLS/register_stage_progress_report_v0_1.py",
    "ack_tool": "TOOLS/administratum_ack_stage_progress_v0_1.py",
    "next_atomic_step": "CURRENT_STATE/NEXT_ATOMIC_STEP.md",
    "current_truth": "CURRENT_STATE/ARC5_PREFIRE_CURRENT_TRUTH_20260513.json",
}

REQUIRED_DIRS = [
    "ORGANS/ADMINISTRATUM/REGISTRY/WORK_SESSIONS",
    "ORGANS/ADMINISTRATUM/REGISTRY/STAGE_PROGRESS_REPORTS",
    "ORGANS/ADMINISTRATUM/REGISTRY/ACKS",
]

REQUIRED_ACK_DECISIONS = {
    "CONTINUE_ALLOWED",
    "STOP_OWNER_REQUIRED",
    "BLOCKED",
    "NEEDS_REVIEW",
    "ACK_RECORDED_NO_CONTINUATION",
}

ASSET_PATH_PREFIXES = ["ASSETS", "SANCTUM/DESIGN_SYSTEM", "SANCTUM/UI_LAB"]
FORBIDDEN_READY_PATTERNS = [
    '"ready_for_agent_status": true',
    '"ready_for_agent": true',
    "ready_for_agent=true",
    "act5_execution_ready: true",
    '"act5_execution_ready": true',
]


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


def write_artifacts(repo_root: Path, report: dict[str, Any]) -> dict[str, str]:
    runtime_dir = repo_root / RUNTIME_REL
    runtime_dir.mkdir(parents=True, exist_ok=True)

    report_path = runtime_dir / REPORT_NAME
    verdict_path = runtime_dir / VERDICT_NAME
    receipt_path = runtime_dir / RECEIPT_NAME

    report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    lines: list[str] = [
        "# Work Session / Administratum ACK Check v0.1",
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
        "schema_version": "imperium.work_session_administratum_ack_check_receipt.v0_1",
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

    path_map: dict[str, Path] = {key: repo_root / rel for key, rel in REQUIRED_FILES.items()}

    for rel in REQUIRED_DIRS:
        path = repo_root / rel
        if path.exists() and path.is_dir():
            passes.append(f"dir_exists:{rel}")
        else:
            add_unique(blocked, f"missing_required_dir:{rel}")

    for key, path in path_map.items():
        if path.exists():
            passes.append(f"file_exists:{key}:{path.relative_to(repo_root).as_posix()}")
        else:
            add_unique(blocked, f"missing_required_file:{key}:{path.relative_to(repo_root).as_posix()}")

    for key in ["register_tool", "ack_tool"]:
        script_path = path_map[key]
        if script_path.exists():
            try:
                py_compile.compile(str(script_path), doraise=True)
                passes.append(f"py_compile_ok:{script_path.relative_to(repo_root).as_posix()}")
            except Exception as exc:  # noqa: BLE001
                add_unique(blocked, f"py_compile_failed:{script_path.relative_to(repo_root).as_posix()}:{type(exc).__name__}")

    ack_schema_path = path_map["administratum_ack_schema"]
    ack_schema, ack_schema_err = read_json_obj(ack_schema_path)
    if ack_schema_err:
        add_unique(blocked, ack_schema_err)
    elif ack_schema is not None:
        try:
            decisions = set(
                ack_schema["properties"]["decision"]["enum"]
            )
            missing = sorted(REQUIRED_ACK_DECISIONS - decisions)
            if missing:
                add_unique(blocked, f"ack_schema_missing_decisions:{'|'.join(missing)}")
            else:
                passes.append("ack_schema_decision_enum_complete")
        except Exception:  # noqa: BLE001
            add_unique(blocked, "ack_schema_decision_enum_not_readable")

    work_session_path = path_map["work_session_example"]
    stage_report_path = path_map["stage_progress_example"]
    ack_example_path = path_map["ack_example"]

    work_session, work_session_err = read_json_obj(work_session_path)
    stage_report, stage_report_err = read_json_obj(stage_report_path)
    ack_example, ack_example_err = read_json_obj(ack_example_path)

    for err in [work_session_err, stage_report_err, ack_example_err]:
        if err:
            add_unique(blocked, err)

    if work_session is not None:
        if work_session.get("example_only") is True or work_session.get("status") == "EXAMPLE_ONLY_NOT_ACTIVE":
            passes.append("work_session_example_marked_example_only")
        else:
            add_unique(blocked, "work_session_example_not_marked_example_only")

        if work_session.get("status") == "CONTINUE_ALLOWED":
            add_unique(blocked, "work_session_example_must_not_be_continue_allowed")

        if work_session.get("status") not in {"EXAMPLE_ONLY_NOT_ACTIVE", "SESSION_DRAFT", "WAITING_FOR_ADMINISTRATUM_ACK"}:
            add_unique(warnings, "work_session_example_status_is_unusual_for_example")

        if work_session.get("status") == "CONTINUE_ALLOWED" and not work_session.get("administratum_acks"):
            add_unique(blocked, "active_continuation_without_ack_detected")

    if stage_report is not None:
        if stage_report.get("example_only") is True:
            passes.append("stage_progress_example_marked_example_only")
        else:
            add_unique(blocked, "stage_progress_example_not_marked_example_only")

        if stage_report.get("next_requested_action") == "REQUEST_CONTINUE":
            add_unique(warnings, "stage_progress_example_requests_continue_but_example_only")

    if ack_example is not None:
        if ack_example.get("example_only") is True or ack_example.get("decision") == "EXAMPLE_ONLY_NOT_ACTIVE":
            passes.append("ack_example_marked_example_only")
        else:
            add_unique(blocked, "ack_example_not_marked_example_only")

    for label, path in {
        "work_session_example": work_session_path,
        "stage_progress_example": stage_report_path,
        "ack_example": ack_example_path,
        "readme": path_map["work_sessions_readme"],
    }.items():
        if path.exists():
            text = path.read_text(encoding="utf-8").lower()
            bad_hits = [pattern for pattern in FORBIDDEN_READY_PATTERNS if pattern in text]
            if bad_hits:
                add_unique(blocked, f"forbidden_ready_claim_in_{label}:{'|'.join(bad_hits)}")
            else:
                passes.append(f"no_ready_for_agent_true_claim:{label}")

    current_truth_path = path_map["current_truth"]
    current_truth, current_truth_err = read_json_obj(current_truth_path)
    if current_truth_err:
        add_unique(blocked, current_truth_err)
    elif current_truth is not None:
        if current_truth.get("act5_execution_ready") is False:
            passes.append("current_truth_act5_execution_ready_false")
        else:
            add_unique(blocked, "current_truth_act5_execution_ready_must_be_false")

        if current_truth.get("ready_for_agent_status") is False:
            passes.append("current_truth_ready_for_agent_status_false")
        else:
            add_unique(blocked, "current_truth_ready_for_agent_status_must_be_false")

    for rel in ASSET_PATH_PREFIXES:
        path = repo_root / rel
        if path.exists():
            add_unique(blocked, f"assets_created_too_early:{rel}")
        else:
            passes.append(f"assets_zone_not_created:{rel}")

    next_atomic_path = path_map["next_atomic_step"]
    if next_atomic_path.exists():
        next_text = next_atomic_path.read_text(encoding="utf-8")
        lowered = next_text.lower()
        if "step 5 completed by this task" in lowered and "work session / administratum ack v0.1" in lowered:
            passes.append("next_atomic_step_mentions_step5_completion")
        else:
            add_unique(blocked, "next_atomic_step_missing_step5_completion")

        if "servitor self-authorizing continuation" in lowered:
            passes.append("next_atomic_step_forbids_servitor_self_authorization")
        else:
            add_unique(blocked, "next_atomic_step_missing_servitor_self_authorization_forbidden_clause")

    if not (repo_root / "SANCTUM/sanctum_v0_29_qt.py").exists():
        add_unique(warnings, "sanctum_baseline_file_missing_unexpected")
    else:
        warnings.append("skeleton_scope_only:no_sanctum_ui_integration_in_step5")

    warnings.append("skeleton_scope_only:no_active_long_work_sessions_registered")

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
    parser = argparse.ArgumentParser(description="Check Work Session / Administratum ACK v0.1 skeleton files.")
    parser.add_argument("--repo-root", default=".", help="Repository root path.")
    parser.add_argument("--human", action="store_true", help="Print human-readable output.")
    parser.add_argument("--json", action="store_true", help="Print JSON output.")
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

    if report.get("blocked"):
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
