#!/usr/bin/env python3
"""
Check strategic capability foundation for IMPERIUM_TEST_VERSION.
Run from: E:/IMPERIUM/IMPERIUM_TEST_VERSION
"""

from __future__ import annotations

import json
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

TASK_ID = "SERVITOR_PC_FINISH_KIRO_REPAIR_R2_1_STRATEGIC_CAPABILITY_FOUNDATION_20260516"
CYRILLIC_PATTERN = re.compile(r"[\u0400-\u04FF]")


def utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def run_command(args: list[str], cwd: Path) -> dict:
    try:
        proc = subprocess.run(args, cwd=str(cwd), capture_output=True, text=True, check=False)
        return {
            "command": " ".join(args),
            "exit_code": proc.returncode,
            "stdout": proc.stdout.strip(),
            "stderr": proc.stderr.strip(),
        }
    except Exception as exc:
        return {
            "command": " ".join(args),
            "exit_code": 99,
            "stdout": "",
            "stderr": str(exc),
        }


def add_check(checks: list[dict], failures: list[str], warnings: list[str], name: str, passed: bool, details: str, severity: str = "failure") -> None:
    checks.append({"name": name, "passed": passed, "details": details})
    if passed:
        return
    if severity == "warning":
        warnings.append(f"{name}: {details}")
    else:
        failures.append(f"{name}: {details}")


def file_nonempty(path: Path) -> bool:
    return path.exists() and path.is_file() and path.stat().st_size > 0


def parse_json(path: Path) -> tuple[bool, str]:
    try:
        with path.open("r", encoding="utf-8-sig") as handle:
            json.load(handle)
        return True, "ok"
    except Exception as exc:
        return False, str(exc)


def contains_cyrillic(path: Path) -> bool:
    text = path.read_text(encoding="utf-8-sig", errors="ignore")
    return bool(CYRILLIC_PATTERN.search(text))


def main() -> int:
    cwd = Path.cwd().resolve()
    if cwd.name != "IMPERIUM_TEST_VERSION":
        print("ERROR: run from E:/IMPERIUM/IMPERIUM_TEST_VERSION")
        return 2

    repo_root = cwd.parent
    run_dir = cwd / "RUNS" / "KIRO_REPAIR_R2_1_STRATEGIC_CAPABILITY_FOUNDATION_20260516"
    run_dir.mkdir(parents=True, exist_ok=True)

    required_outputs = [
        "AGENT_EXCHANGE/agent_exchange_window.html",
        "RUNS/KIRO_DELTA_R2_AGENT_EXCHANGE_WINDOW_R1_20260516/OWNER_USAGE_GUIDE_RU.md",
        "AGENT_EXCHANGE/OUTBOX/KIRO/KIRO_RESPONSE_BUNDLE_DELTA_R2_AGENT_EXCHANGE_R1_20260516.md",
        "AUDITS/KIRO_SELF_AUDIT_DELTA_R2_AGENT_EXCHANGE_R1_20260516",
        "RUNS/KIRO_REPAIR_R2_1_STRATEGIC_CAPABILITY_FOUNDATION_20260516/OWNER_FINAL_REPORT_RU.md",
        "RUNS/KIRO_REPAIR_R2_1_STRATEGIC_CAPABILITY_FOUNDATION_20260516/MANUAL_VERIFICATION_CHECKLIST_RU.md",
        "AUDITS/SERVITOR_PC_SELF_AUDIT_REPAIR_R2_1_STRATEGIC_CAPABILITY_FOUNDATION_20260516",
        "STRATEGIC_CAPABILITIES/CAPABILITY_MAP.md",
        "STRATEGIC_CAPABILITIES/CAPABILITY_MAP.json",
        "STRATEGIC_CAPABILITIES/strategic_capability_window.html",
        "STRATEGIC_CAPABILITIES/FREELANCE_EXECUTION/FREELANCE_TASK_CORRIDOR_SPEC.md",
        "STRATEGIC_CAPABILITIES/FREELANCE_EXECUTION/freelance_task_corridor.schema.json",
        "STRATEGIC_CAPABILITIES/FREELANCE_EXECUTION/SAMPLE_SYNTHETIC_TZ.md",
        "STRATEGIC_CAPABILITIES/FREELANCE_EXECUTION/SAMPLE_TASK_INTAKE.json",
        "STRATEGIC_CAPABILITIES/FREELANCE_EXECUTION/README.md",
        "STRATEGIC_CAPABILITIES/PRESENTATION_SYSTEM/PRESENTATION_SYSTEM_SPEC.md",
        "STRATEGIC_CAPABILITIES/PRESENTATION_SYSTEM/product_summary.schema.json",
        "STRATEGIC_CAPABILITIES/PRESENTATION_SYSTEM/IMPERIUM_SELF_SUMMARY_RU.md",
        "STRATEGIC_CAPABILITIES/PRESENTATION_SYSTEM/IMPERIUM_SELF_SUMMARY.json",
        "STRATEGIC_CAPABILITIES/PRESENTATION_SYSTEM/README.md",
        "STRATEGIC_CAPABILITIES/DISTRIBUTED_CONTOURS/DISTRIBUTED_CONTOURS_SPEC.md",
        "STRATEGIC_CAPABILITIES/DISTRIBUTED_CONTOURS/contour_profile.schema.json",
        "STRATEGIC_CAPABILITIES/DISTRIBUTED_CONTOURS/pc_contour_profile.template.json",
        "STRATEGIC_CAPABILITIES/DISTRIBUTED_CONTOURS/ubuntu_laptop_contour_profile.template.json",
        "STRATEGIC_CAPABILITIES/DISTRIBUTED_CONTOURS/ssh_capability_check.ps1",
        "STRATEGIC_CAPABILITIES/DISTRIBUTED_CONTOURS/README.md",
        "STRATEGIC_CAPABILITIES/SECOND_BRAIN/SECOND_BRAIN_MEMORY_ZONES_SPEC.md",
        "STRATEGIC_CAPABILITIES/SECOND_BRAIN/memory_zone.schema.json",
        "STRATEGIC_CAPABILITIES/SECOND_BRAIN/context_pack.schema.json",
        "STRATEGIC_CAPABILITIES/SECOND_BRAIN/SAMPLE_MEMORY_ZONES.json",
        "STRATEGIC_CAPABILITIES/SECOND_BRAIN/SAMPLE_CONTEXT_PACK.json",
        "STRATEGIC_CAPABILITIES/SECOND_BRAIN/README.md",
        "STRATEGIC_CAPABILITIES/CLI_AGENT_PORT/CLI_AGENT_PORT_SPEC.md",
        "STRATEGIC_CAPABILITIES/CLI_AGENT_PORT/cli_agent_request.schema.json",
        "STRATEGIC_CAPABILITIES/CLI_AGENT_PORT/cli_agent_response.schema.json",
        "STRATEGIC_CAPABILITIES/CLI_AGENT_PORT/imperium_cli_agent_port.py",
        "STRATEGIC_CAPABILITIES/CLI_AGENT_PORT/sample_request.json",
        "STRATEGIC_CAPABILITIES/CLI_AGENT_PORT/README.md",
        "STRATEGIC_CAPABILITIES/LOCAL_LLM_PORT/LOCAL_LLM_PORT_SPEC.md",
        "STRATEGIC_CAPABILITIES/LOCAL_LLM_PORT/local_llm_profile.schema.json",
        "STRATEGIC_CAPABILITIES/LOCAL_LLM_PORT/local_llm_request.schema.json",
        "STRATEGIC_CAPABILITIES/LOCAL_LLM_PORT/local_llm_response.schema.json",
        "STRATEGIC_CAPABILITIES/LOCAL_LLM_PORT/local_llm_config.template.json",
        "STRATEGIC_CAPABILITIES/LOCAL_LLM_PORT/local_llm_health_check.py",
        "STRATEGIC_CAPABILITIES/LOCAL_LLM_PORT/README.md",
        "TOOLS/check_strategic_capability_foundation.py",
    ]

    checks: list[dict] = []
    failures: list[str] = []
    warnings: list[str] = []

    for rel in required_outputs:
        path = cwd / rel
        exists = path.exists()
        add_check(checks, failures, warnings, f"exists:{rel}", exists, "exists" if exists else "missing")
        if exists and path.is_file():
            nonempty = path.stat().st_size > 20
            add_check(checks, failures, warnings, f"nonempty:{rel}", nonempty, f"size={path.stat().st_size}")

    json_paths = [cwd / rel for rel in required_outputs if rel.endswith(".json")]
    for path in json_paths:
        ok, reason = parse_json(path)
        add_check(checks, failures, warnings, f"json_parse:{path.relative_to(cwd)}", ok, reason)

    allow_cyrillic = {
        "STRATEGIC_CAPABILITIES/PRESENTATION_SYSTEM/IMPERIUM_SELF_SUMMARY_RU.md",
        "RUNS/KIRO_DELTA_R2_AGENT_EXCHANGE_WINDOW_R1_20260516/OWNER_USAGE_GUIDE_RU.md",
        "RUNS/KIRO_REPAIR_R2_1_STRATEGIC_CAPABILITY_FOUNDATION_20260516/OWNER_FINAL_REPORT_RU.md",
        "RUNS/KIRO_REPAIR_R2_1_STRATEGIC_CAPABILITY_FOUNDATION_20260516/MANUAL_VERIFICATION_CHECKLIST_RU.md",
    }
    for rel in required_outputs:
        if not any(rel.endswith(ext) for ext in (".md", ".json", ".schema.json", ".html", ".py", ".ps1")):
            continue
        if rel in allow_cyrillic:
            continue
        path = cwd / rel
        if path.exists() and path.is_file():
            cyr = contains_cyrillic(path)
            add_check(checks, failures, warnings, f"english_only:{rel}", not cyr, "contains Cyrillic" if cyr else "ok")

    sw_path = cwd / "STRATEGIC_CAPABILITIES/strategic_capability_window.html"
    if sw_path.exists():
        text = sw_path.read_text(encoding="utf-8", errors="ignore")
        required_phrases = [
            "Freelance Execution",
            "Presentation System",
            "Distributed Contours",
            "Second Brain",
            "CLI Agent Port",
            "Local LLM Port",
            "scope_safe_to_commit is not quality_green",
        ]
        missing = [p for p in required_phrases if p not in text]
        add_check(checks, failures, warnings, "strategic_window_useful", len(missing) == 0, f"missing={missing}" if missing else "ok")

    cli = cwd / "STRATEGIC_CAPABILITIES/CLI_AGENT_PORT/imperium_cli_agent_port.py"
    cli_commands = [
        [sys.executable, str(cli), "--mode", "health"],
        [sys.executable, str(cli), "--mode", "inspect-capabilities"],
        [
            sys.executable,
            str(cli),
            "--mode",
            "summarize",
            "--input",
            str(cwd / "STRATEGIC_CAPABILITIES/CLI_AGENT_PORT/sample_request.json"),
        ],
    ]
    cli_results = []
    for cmd in cli_commands:
        result = run_command(cmd, cwd)
        cli_results.append(result)
        add_check(checks, failures, warnings, f"cli_command:{' '.join(cmd[2:4])}", result["exit_code"] == 0, f"exit={result['exit_code']}; stderr={result['stderr']}")

    llm_cmd = [sys.executable, str(cwd / "STRATEGIC_CAPABILITIES/LOCAL_LLM_PORT/local_llm_health_check.py")]
    llm_result = run_command(llm_cmd, cwd)
    llm_status = "UNKNOWN"
    if llm_result["stdout"]:
        try:
            llm_json = json.loads(llm_result["stdout"])
            llm_status = llm_json.get("status", "UNKNOWN")
        except Exception:
            llm_status = "UNKNOWN"

    add_check(
        checks,
        failures,
        warnings,
        "local_llm_health_command",
        llm_result["exit_code"] in (0, 1),
        f"exit={llm_result['exit_code']} status={llm_status}",
    )

    add_check(
        checks,
        failures,
        warnings,
        "distributed_contour_script_exists",
        file_nonempty(cwd / "STRATEGIC_CAPABILITIES/DISTRIBUTED_CONTOURS/ssh_capability_check.ps1"),
        "present" if file_nonempty(cwd / "STRATEGIC_CAPABILITIES/DISTRIBUTED_CONTOURS/ssh_capability_check.ps1") else "missing",
    )

    status_result = run_command(["git", "status", "--short"], repo_root)
    out_lines = [line for line in status_result["stdout"].splitlines() if line.strip()]
    outside = []
    for line in out_lines:
        stripped = line.strip()
        parts = stripped.split(maxsplit=1)
        candidate = parts[1] if len(parts) > 1 else stripped
        normalized = candidate.replace("\\", "/")
        if not normalized.startswith("IMPERIUM_TEST_VERSION/"):
            outside.append(line)
    scope_safe = len(outside) == 0
    add_check(checks, failures, warnings, "scope_only_test_version", scope_safe, "ok" if scope_safe else f"outside_changes={outside}")

    quality_green = len(failures) == 0
    owner_ready_for_manual_review = True
    ready_for_promotion_to_main_canon = False

    final_verdict = "VERIFIED_TEST_VERSION_REPAIR_COMPLETE"
    if not scope_safe:
        final_verdict = "BLOCKED_SCOPE_VIOLATION"
    elif not quality_green:
        final_verdict = "REPAIR_REQUIRED"

    report = {
        "task_id": TASK_ID,
        "timestamp": utc_now(),
        "required_outputs": required_outputs,
        "checks": checks,
        "failures": failures,
        "warnings": warnings,
        "scope_safe_to_commit": scope_safe,
        "quality_green": quality_green,
        "owner_ready_for_manual_review": owner_ready_for_manual_review,
        "ready_for_promotion_to_main_canon": ready_for_promotion_to_main_canon,
        "local_llm_status": llm_status,
        "cli_results": cli_results,
        "local_llm_command_result": llm_result,
        "final_verdict": final_verdict,
    }

    report_path = run_dir / "STRATEGIC_CAPABILITY_CHECK_REPORT.json"
    with report_path.open("w", encoding="utf-8") as handle:
        json.dump(report, handle, indent=2, ensure_ascii=False)

    print("=== STRATEGIC CAPABILITY FOUNDATION CHECK ===")
    print(f"Checks: {len(checks)}")
    print(f"Failures: {len(failures)}")
    print(f"Warnings: {len(warnings)}")
    print(f"scope_safe_to_commit: {scope_safe}")
    print(f"quality_green: {quality_green}")
    print(f"owner_ready_for_manual_review: {owner_ready_for_manual_review}")
    print(f"ready_for_promotion_to_main_canon: {ready_for_promotion_to_main_canon}")
    print(f"final_verdict: {final_verdict}")
    print(f"report: {report_path}")

    return 0 if quality_green and scope_safe else 1


if __name__ == "__main__":
    sys.exit(main())
