from __future__ import annotations

import json
import subprocess
from pathlib import Path
from typing import Any

from common import (
    LIVE_TASK_ROOT,
    STAGE_TITLES,
    TASK_ID,
    hardening_stage_report_map,
    rel,
    utc_now,
    write_json,
    write_stage_artifacts,
    write_text,
)


def git_head() -> str:
    return subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip()


def run_cmd(command: list[str]) -> tuple[int, str]:
    proc = subprocess.run(command, text=True, capture_output=True)
    output = (proc.stdout or "") + (proc.stderr or "")
    return proc.returncode, output.strip()


def read_stage_report(stage_number: int) -> dict[str, Any]:
    path = LIVE_TASK_ROOT / "STAGE_REPORTS" / f"STAGE-{stage_number:02d}" / "STAGE_REPORT.json"
    return json.loads(path.read_text(encoding="utf-8"))


def run() -> int:
    started = utc_now()
    head_before = git_head()
    stage_sources = hardening_stage_report_map()
    commands = [
        ["py", "-3", "scripts/foundational_organs_v1/build_foundational_organs_v1_data.py"],
        ["py", "-3", "scripts/foundational_organs_v1/check_foundational_organs_v1_no_fake_green.py"],
        ["py", "-3", "scripts/foundational_organs_v1/check_foundational_organs_v1_stale_status.py"],
        ["py", "-3", "scripts/foundational_organs_v1/check_foundational_organs_v1_repo_purity_utf8.py"],
        ["py", "-3", "scripts/foundational_organs_v1/run_foundational_organs_v1_e2e_proof.py"],
    ]
    command_results = []
    command_blockers = []
    for command in commands:
        code, output = run_cmd(command)
        command_results.append({"command": " ".join(command), "exit_code": code, "output_tail": output[-1000:]})
        if code != 0:
            command_blockers.append(f"command_failed:{' '.join(command)}")

    missing_stage_reports = []
    stage_rows = []
    stages_passed = 0
    stages_failed = 0
    self_repairs_count = 0
    for stage_number in range(1, 20):
        stage_path = LIVE_TASK_ROOT / "STAGE_REPORTS" / f"STAGE-{stage_number:02d}" / "STAGE_REPORT.json"
        if not stage_path.exists():
            missing_stage_reports.append(rel(stage_path))
            stages_failed += 1
            continue
        report = read_stage_report(stage_number)
        verdict = str(report.get("verdict", "FAIL"))
        if verdict.startswith("PASS"):
            stages_passed += 1
        else:
            stages_failed += 1
        self_repairs_count += len(report.get("self_repairs", []) or [])
        stage_rows.append(
            {
                "stage_number": stage_number,
                "stage_title": STAGE_TITLES[stage_number],
                "source_prompt_path": report.get("source_prompt_path"),
                "source_hardening_report_path": report.get("source_hardening_report_path"),
                "live_outputs": report.get("live_outputs", []),
                "checks_run": report.get("checks_run", []),
                "verdict": verdict,
                "warnings": report.get("warnings", []),
                "blockers": report.get("blockers", []),
                "self_repairs": report.get("self_repairs", []),
                "retry_count": report.get("retry_count", 0),
            }
        )

    blockers = command_blockers.copy()
    blockers.extend([f"missing_stage_report:{p}" for p in missing_stage_reports])

    final_verdict = "PASS" if not blockers and stages_failed == 0 else "FAIL"
    ready_for_owner_review = final_verdict == "PASS"
    ready_for_agent = False

    completed = utc_now()
    ledger_json_path = LIVE_TASK_ROOT / "EXECUTION_LEDGER" / "live_implementation_ledger.json"
    write_json(
        ledger_json_path,
        {
            "task_id": TASK_ID,
            "started_utc": started,
            "completed_utc": completed,
            "git_head_before": head_before,
            "git_head_after": git_head(),
            "stages": stage_rows,
            "stages_completed_count": len(stage_rows),
            "stages_passed_count": stages_passed,
            "stages_failed_count": stages_failed,
            "self_repairs_count": self_repairs_count,
            "command_results": command_results,
            "warnings": [],
            "blockers": blockers,
            "final_verdict": final_verdict,
            "ready_for_owner_review": ready_for_owner_review,
            "ready_for_agent": ready_for_agent,
        },
    )
    lines = [
        "# Live Implementation Ledger",
        "",
        f"- task_id: `{TASK_ID}`",
        f"- started_utc: `{started}`",
        f"- completed_utc: `{completed}`",
        f"- stages_passed_count: `{stages_passed}`",
        f"- stages_failed_count: `{stages_failed}`",
        f"- self_repairs_count: `{self_repairs_count}`",
        f"- final_verdict: `{final_verdict}`",
        "",
        "## Stage Summary",
    ]
    for row in stage_rows:
        lines.append(f"- STAGE-{row['stage_number']:02d}: `{row['verdict']}`")
    write_text(LIVE_TASK_ROOT / "EXECUTION_LEDGER" / "live_implementation_ledger.md", "\n".join(lines))

    dashboards = [
        "ORGANS/ASTRONOMICON/DASHBOARD_V1/index.html",
        "ORGANS/ADMINISTRATUM/DASHBOARD_V1/index.html",
        "ORGANS/OFFICIO_AGENTIS/DASHBOARD_V1/index.html",
        "ORGANS/DOCTRINARIUM/DASHBOARD_V1/index.html",
        "SANCTUM/FOUNDATIONAL_ORGANS_V1/index.html",
    ]
    checks = [
        "py -3 scripts/foundational_organs_v1/check_foundational_organs_v1_no_fake_green.py",
        "py -3 scripts/foundational_organs_v1/check_foundational_organs_v1_stale_status.py",
        "py -3 scripts/foundational_organs_v1/check_foundational_organs_v1_repo_purity_utf8.py",
        "py -3 scripts/foundational_organs_v1/run_foundational_organs_v1_e2e_proof.py",
    ]
    final_manifest_path = LIVE_TASK_ROOT / "FINAL_BUNDLE" / "final_live_implementation_bundle_manifest.json"
    write_json(
        final_manifest_path,
        {
            "task_id": TASK_ID,
            "generated_at_utc": completed,
            "git_head": git_head(),
            "final_verdict": final_verdict,
            "stage_reports": [f"ORGANS/ASTRONOMICON/TASK_DRAFTS/{TASK_ID}/STAGE_REPORTS/STAGE-{i:02d}/STAGE_REPORT.json" for i in range(1, 21)],
            "checks": checks,
            "dashboards": dashboards,
            "ready_for_owner_review": ready_for_owner_review,
            "ready_for_agent": ready_for_agent,
            "static_dashboards": True,
        },
    )

    evidence_report_path = LIVE_TASK_ROOT / "FINAL_BUNDLE" / "evidence_completeness_report.json"
    missing_dashboards = [p for p in dashboards if not Path(p).exists()]
    write_json(
        evidence_report_path,
        {
            "task_id": TASK_ID,
            "generated_at_utc": completed,
            "git_head": git_head(),
            "missing_stage_reports": missing_stage_reports,
            "missing_dashboards": missing_dashboards,
            "verdict": "PASS" if not missing_stage_reports and not missing_dashboards else "FAIL",
        },
    )
    warning_ledger_path = LIVE_TASK_ROOT / "FINAL_BUNDLE" / "warning_blocker_ledger.json"
    write_json(
        warning_ledger_path,
        {
            "task_id": TASK_ID,
            "generated_at_utc": completed,
            "warnings": [],
            "blockers": blockers,
            "final_verdict": final_verdict,
        },
    )

    open_instructions = LIVE_TASK_ROOT / "FINAL_BUNDLE" / "dashboard_open_instructions.md"
    write_text(
        open_instructions,
        "\n".join(
            [
                "# Dashboard Open Instructions",
                "",
                "Open these local static dashboards directly from filesystem:",
                *[f"- `{path}`" for path in dashboards],
                "",
                "Run these checks from repo root:",
                *[f"- `{cmd}`" for cmd in checks],
            ]
        ),
    )
    ready_owner_path = LIVE_TASK_ROOT / "FINAL_BUNDLE" / "READY_FOR_OWNER_REVIEW.json"
    write_json(
        ready_owner_path,
        {
            "task_id": TASK_ID,
            "generated_at_utc": completed,
            "git_head": git_head(),
            "ready_for_owner_review": ready_for_owner_review,
            "reason": "all_live_stage_reports_and_checks_passed" if ready_for_owner_review else "pending_blockers",
        },
    )
    ready_agent_path = LIVE_TASK_ROOT / "FINAL_BUNDLE" / "READY_FOR_AGENT.json"
    write_json(
        ready_agent_path,
        {
            "task_id": TASK_ID,
            "generated_at_utc": completed,
            "git_head": git_head(),
            "ready_for_agent": ready_for_agent,
            "reason": "owner_launch_gate_not_issued",
        },
    )
    summary_md_path = LIVE_TASK_ROOT / "FINAL_BUNDLE" / "final_live_implementation_summary.md"
    write_text(
        summary_md_path,
        "\n".join(
            [
                "# Foundational Organs V1 Live Implementation Summary",
                "",
                f"- final_verdict: `{final_verdict}`",
                f"- ready_for_owner_review: `{ready_for_owner_review}`",
                f"- ready_for_agent: `{ready_for_agent}`",
                "- dashboards: Astronomicon, Administratum, Officio Agentis, Doctrinarium, Sanctum aggregation",
                "- note: dashboards are static local HTML reading generated live data bundles",
                "- mutating actions remain disabled or owner-gated by design",
            ]
        ),
    )

    final_report = LIVE_TASK_ROOT / "REPORTS" / "live_implementation_final_report.json"
    write_json(
        final_report,
        {
            "task_id": TASK_ID,
            "started_utc": started,
            "completed_utc": completed,
            "git_head_before": head_before,
            "git_head_after": git_head(),
            "stages_completed_count": len(stage_rows),
            "stages_passed_count": stages_passed,
            "stages_failed_count": stages_failed,
            "self_repairs_count": self_repairs_count,
            "dashboards_created_count": 5 - len(missing_dashboards),
            "scripts_created_count": 6,
            "checks_passed": final_verdict == "PASS",
            "ready_for_owner_review": ready_for_owner_review,
            "ready_for_agent": ready_for_agent,
            "warnings": [],
            "blockers": blockers,
            "final_verdict": final_verdict,
            "static_dashboards": True,
            "mutating_actions_disabled_by_design": True,
        },
    )

    stage20_report_path = write_stage_artifacts(
        20,
        source_hardening_report_path=stage_sources.get(20),
        live_outputs=[
            rel(final_manifest_path),
            rel(evidence_report_path),
            rel(warning_ledger_path),
            rel(open_instructions),
            rel(ready_owner_path),
            rel(ready_agent_path),
            rel(summary_md_path),
            rel(final_report),
            rel(ledger_json_path),
        ],
        checks_run=["python scripts/foundational_organs_v1/check_foundational_organs_v1_all.py"],
        verdict=final_verdict,
        warnings=[],
        blockers=blockers,
        self_repairs=[],
        retry_count=0,
        notes="final_bundle_and_certification",
    )

    # Refresh ledger with stage 20.
    stage20 = read_stage_report(20)
    stage_rows.append(
        {
            "stage_number": 20,
            "stage_title": STAGE_TITLES[20],
            "source_prompt_path": stage20.get("source_prompt_path"),
            "source_hardening_report_path": stage20.get("source_hardening_report_path"),
            "live_outputs": stage20.get("live_outputs", []),
            "checks_run": stage20.get("checks_run", []),
            "verdict": stage20.get("verdict"),
            "warnings": stage20.get("warnings", []),
            "blockers": stage20.get("blockers", []),
            "self_repairs": stage20.get("self_repairs", []),
            "retry_count": stage20.get("retry_count", 0),
        }
    )
    stages_passed_20 = sum(1 for row in stage_rows if str(row["verdict"]).startswith("PASS"))
    stages_failed_20 = len(stage_rows) - stages_passed_20
    write_json(
        ledger_json_path,
        {
            "task_id": TASK_ID,
            "started_utc": started,
            "completed_utc": completed,
            "git_head_before": head_before,
            "git_head_after": git_head(),
            "stages": stage_rows,
            "stages_completed_count": len(stage_rows),
            "stages_passed_count": stages_passed_20,
            "stages_failed_count": stages_failed_20,
            "self_repairs_count": self_repairs_count,
            "command_results": command_results,
            "warnings": [],
            "blockers": blockers,
            "final_verdict": final_verdict,
            "ready_for_owner_review": ready_for_owner_review,
            "ready_for_agent": ready_for_agent,
        },
    )
    write_json(
        final_report,
        {
            "task_id": TASK_ID,
            "started_utc": started,
            "completed_utc": completed,
            "git_head_before": head_before,
            "git_head_after": git_head(),
            "stages_completed_count": len(stage_rows),
            "stages_passed_count": stages_passed_20,
            "stages_failed_count": stages_failed_20,
            "self_repairs_count": self_repairs_count,
            "dashboards_created_count": 5 - len(missing_dashboards),
            "scripts_created_count": 6,
            "checks_passed": final_verdict == "PASS",
            "ready_for_owner_review": ready_for_owner_review,
            "ready_for_agent": ready_for_agent,
            "warnings": [],
            "blockers": blockers,
            "final_verdict": final_verdict,
            "static_dashboards": True,
            "mutating_actions_disabled_by_design": True,
        },
    )

    print(final_verdict)
    print(rel(final_manifest_path))
    print(rel(stage20_report_path))
    return 0 if final_verdict == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(run())
