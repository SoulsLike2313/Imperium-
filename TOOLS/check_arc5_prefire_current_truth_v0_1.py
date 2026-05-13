#!/usr/bin/env python3
from __future__ import annotations

import argparse
import datetime as dt
import json
import subprocess
from pathlib import Path
from typing import Any

TASK_ID = "TASK-20260513-ACT5-PREFIRE-SYNTHESIS-AND-CURRENT-TRUTH-REFRESH-V0_1"
SCHEMA_VERSION = "imperium.arc5_prefire_current_truth_check.v0_1"
RUNTIME_REL = ".imperium_runtime/astronomicon/arc5_prefire_current_truth_check"
REPORT_NAME = "ARC5_PREFIRE_CURRENT_TRUTH_CHECK_REPORT.json"
VERDICT_NAME = "ARC5_PREFIRE_CURRENT_TRUTH_CHECK_VERDICT.md"
RECEIPT_NAME = "ARC5_PREFIRE_CURRENT_TRUTH_CHECK_RECEIPT.json"

REQUIRED_FILES = {
    "arc5_prefire_readiness": "ORGANS/ASTRONOMICON/REGISTRY/ARC5_PREFIRE/ARC5_PREFIRE_READINESS_20260513.md",
    "arc5_prefire_synthesis": "ORGANS/ASTRONOMICON/REGISTRY/ARC5_PREFIRE/ARC5_PREFIRE_SYNTHESIS_20260513.md",
    "kiro_act5_audit": "ORGANS/ASTRONOMICON/ADVISORY_BUFFER/KIRO/20260513/KIRO_ACT5_PREFIRE_READINESS_AUDIT_20260513.md",
    "current_truth": "CURRENT_STATE/ARC5_PREFIRE_CURRENT_TRUTH_20260513.json",
    "next_atomic_step": "CURRENT_STATE/NEXT_ATOMIC_STEP.md",
    "start_here": "START_HERE.md",
}

REQUIRED_TRUTH_KEYS = [
    "schema_version",
    "generated_at_utc",
    "repo_head",
    "commit_count",
    "latest_commit_subject",
    "current_arc",
    "current_phase",
    "act5_execution_ready",
    "ready_for_agent_status",
    "sanctum_status",
    "sanctum_working_baseline",
    "rejected_sanctum_lines",
    "important_files",
    "next_allowed_actions",
    "blockers",
    "owner_notes_summary",
]

REQUIRED_REJECTED_SANCTUM_LINES = [
    "sanctum ee",
    "v0.30ee",
    "r1",
    "r2",
    "generic standalone html dashboard as accepted ui",
]


def now_utc() -> str:
    return dt.datetime.now(dt.timezone.utc).isoformat()


def add_unique(items: list[str], value: str) -> None:
    if value not in items:
        items.append(value)


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
        "# ARC5 Prefire Current Truth Check v0.1",
        "",
        f"- task_id: {TASK_ID}",
        f"- generated_at_utc: {report.get('generated_at_utc')}",
        f"- verdict: {report.get('verdict')}",
        f"- pass_count: {len(report.get('passes', []))}",
        f"- warn_count: {len(report.get('warnings', []))}",
        f"- blocked_count: {len(report.get('blocked', []))}",
    ]

    if report.get("blocked"):
        lines.append("")
        lines.append("## BLOCKED")
        for item in report["blocked"]:
            lines.append(f"- {item}")

    if report.get("warnings"):
        lines.append("")
        lines.append("## WARN")
        for item in report["warnings"]:
            lines.append(f"- {item}")

    if report.get("passes"):
        lines.append("")
        lines.append("## PASS")
        for item in report["passes"]:
            lines.append(f"- {item}")

    verdict_path.write_text("\n".join(lines) + "\n", encoding="utf-8")

    receipt = {
        "schema_version": "imperium.arc5_prefire_current_truth_check_receipt.v0_1",
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

    path_map: dict[str, Path] = {k: repo_root / rel for k, rel in REQUIRED_FILES.items()}

    for key, path in path_map.items():
        if path.exists():
            passes.append(f"file_exists:{key}:{path.relative_to(repo_root).as_posix()}")
        else:
            add_unique(blocked, f"missing_required_file:{key}:{path.relative_to(repo_root).as_posix()}")

    truth_payload: dict[str, Any] | None = None
    truth_path = path_map["current_truth"]
    truth_payload, truth_err = read_json_obj(truth_path)
    if truth_err:
        add_unique(blocked, truth_err)
    elif truth_payload is not None:
        for key in REQUIRED_TRUTH_KEYS:
            if key in truth_payload:
                passes.append(f"truth_key_present:{key}")
            else:
                add_unique(blocked, f"truth_missing_key:{key}")

    ok_head, git_head = run_git(repo_root, ["rev-parse", "HEAD"])
    ok_count, git_count_raw = run_git(repo_root, ["rev-list", "--count", "HEAD"])
    ok_subject, git_subject = run_git(repo_root, ["log", "-1", "--pretty=%s"])

    git_count: int | None = None
    if ok_count:
        try:
            git_count = int(git_count_raw)
        except Exception:  # noqa: BLE001
            add_unique(blocked, "git_commit_count_not_integer")

    if truth_payload is not None:
        repo_head = truth_payload.get("repo_head")
        if ok_head and repo_head == git_head:
            passes.append("repo_head_matches_current_git_head")
        else:
            add_unique(blocked, f"repo_head_mismatch:truth={repo_head}:git={git_head if ok_head else 'UNKNOWN'}")

        commit_count = truth_payload.get("commit_count")
        if isinstance(commit_count, int) and git_count is not None and commit_count == git_count:
            passes.append("commit_count_matches_current_git_count")
        else:
            add_unique(blocked, f"commit_count_mismatch:truth={commit_count}:git={git_count}")

        latest_subject = truth_payload.get("latest_commit_subject")
        if ok_subject and latest_subject == git_subject:
            passes.append("latest_commit_subject_matches_current_git_subject")
        else:
            add_unique(warnings, "latest_commit_subject_differs_from_current_git_subject")

        if truth_payload.get("act5_execution_ready") is False:
            passes.append("act5_execution_ready_is_false")
        else:
            add_unique(blocked, "act5_execution_ready_must_be_false")

        if truth_payload.get("ready_for_agent_status") is False:
            passes.append("ready_for_agent_status_is_false")
        else:
            add_unique(blocked, "ready_for_agent_status_must_be_false")

        if truth_payload.get("current_arc") == "ARC_5_PREFIRE":
            passes.append("current_arc_is_arc5_prefire")
        else:
            add_unique(warnings, "current_arc_is_not_arc5_prefire")

        if truth_payload.get("current_phase") == "PREFIRE_IMPLEMENTATION":
            passes.append("current_phase_is_prefire_implementation")
        else:
            add_unique(warnings, "current_phase_is_not_prefire_implementation")

        sanctum_status = str(truth_payload.get("sanctum_status", ""))
        if sanctum_status == "SUPER_EXPERIMENTAL_TRANSITIONAL_OPERATOR_DASHBOARD":
            passes.append("sanctum_status_matches_expected")
        else:
            add_unique(warnings, "sanctum_status_differs_from_expected")

        baseline = truth_payload.get("sanctum_working_baseline")
        if baseline == "SANCTUM/sanctum_v0_29_qt.py":
            passes.append("sanctum_working_baseline_matches_expected")
        else:
            add_unique(blocked, "sanctum_working_baseline_mismatch")

        rejected = truth_payload.get("rejected_sanctum_lines")
        if isinstance(rejected, list):
            lowered = [str(item).strip().lower() for item in rejected]
            for expected in REQUIRED_REJECTED_SANCTUM_LINES:
                if expected in lowered:
                    passes.append(f"rejected_sanctum_line_present:{expected}")
                else:
                    add_unique(blocked, f"missing_rejected_sanctum_line:{expected}")
        else:
            add_unique(blocked, "rejected_sanctum_lines_not_list")

        important = truth_payload.get("important_files")
        if isinstance(important, list):
            required_files = {
                "ARC5_PREFIRE_READINESS_20260513.md",
                "ARC5_PREFIRE_SYNTHESIS_20260513.md",
                "KIRO_ACT5_PREFIRE_READINESS_AUDIT_20260513.md",
                "README_SANCTUM_EXPERIMENTAL_STATUS.md",
            }
            joined = "\n".join(str(item) for item in important)
            for short_name in sorted(required_files):
                if short_name in joined:
                    passes.append(f"important_file_list_contains:{short_name}")
                else:
                    add_unique(blocked, f"important_file_list_missing:{short_name}")
        else:
            add_unique(blocked, "important_files_not_list")

    synthesis_path = path_map["arc5_prefire_synthesis"]
    if synthesis_path.exists():
        synthesis_text = synthesis_path.read_text(encoding="utf-8")
        if "KIRO_ACT5_PREFIRE_READINESS_AUDIT_20260513.md" in synthesis_text:
            passes.append("synthesis_mentions_kiro_audit")
        else:
            add_unique(blocked, "synthesis_missing_kiro_audit_reference")

        if "READY_FOR_AGENT remains false" in synthesis_text:
            passes.append("synthesis_declares_ready_for_agent_false")
        else:
            add_unique(blocked, "synthesis_missing_ready_for_agent_false_statement")

    start_here_path = path_map["start_here"]
    if start_here_path.exists():
        start_text = start_here_path.read_text(encoding="utf-8")
        if "CURRENT_STATE/ARC5_PREFIRE_CURRENT_TRUTH_20260513.json" in start_text:
            passes.append("start_here_points_to_arc5_current_truth")
        else:
            add_unique(blocked, "start_here_missing_arc5_current_truth_reference")

    next_path = path_map["next_atomic_step"]
    if next_path.exists():
        next_text = next_path.read_text(encoding="utf-8")
        next_lower = next_text.lower()
        has_forbidden = "forbidden next step" in next_lower and "direct inquisition execution" in next_lower
        has_ready_clause = "ready_for_agent true without evidence" in next_lower
        if has_forbidden and has_ready_clause:
            passes.append("next_atomic_step_forbids_direct_inquisition_execution")
        else:
            add_unique(blocked, "next_atomic_step_missing_forbidden_direct_execution_clause")

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
    parser = argparse.ArgumentParser(description="Check Arc 5 prefire synthesis and current truth coherence")
    parser.add_argument("--repo-root", default=".", help="Repository root")
    parser.add_argument("--human", action="store_true", help="Print PASS/WARN/BLOCKED sections")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    repo_root = Path(args.repo_root).resolve()

    report = build_report(repo_root)
    artifacts = write_artifacts(repo_root, report)

    if args.human:
        print("=== PASS ===")
        if report["passes"]:
            for item in report["passes"]:
                print(f"- {item}")
        else:
            print("- (none)")

        print("\n=== WARN ===")
        if report["warnings"]:
            for item in report["warnings"]:
                print(f"- {item}")
        else:
            print("- (none)")

        print("\n=== BLOCKED ===")
        if report["blocked"]:
            for item in report["blocked"]:
                print(f"- {item}")
        else:
            print("- (none)")

        print("\n=== VERDICT ===")
        print(report["verdict"])
        print(f"report: {artifacts['report']}")
        print(f"verdict_md: {artifacts['verdict']}")
        print(f"receipt: {artifacts['receipt']}")

    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 2 if report["blocked"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
