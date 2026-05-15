#!/usr/bin/env python3
"""Aggregate checker for Officio Agentis MVP."""

from __future__ import annotations

import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


TASK_ID = "TASK-20260515-BUILD-OFFICIO-AGENTIS-MVP-V0_1"
ROLES = ["SERVITOR", "LOGOS_PRIME", "LOGOS_SPECULUM", "ADVISOR_SERVITOR"]


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def run_cmd(repo: Path, cmd: list[str]) -> dict[str, Any]:
    proc = subprocess.run(cmd, cwd=repo, text=True, capture_output=True)
    parsed = None
    if proc.stdout.strip():
        try:
            parsed = json.loads(proc.stdout.strip())
        except Exception:
            parsed = None
    return {
        "command": " ".join(cmd),
        "returncode": proc.returncode,
        "stdout": proc.stdout.strip(),
        "stderr": proc.stderr.strip(),
        "stdout_json": parsed,
    }


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> int:
    repo = Path(__file__).resolve().parents[1]
    py = sys.executable
    report_path = repo / "ORGANS/OFFICIO_AGENTIS/REPORTS/officio_agentis_check_all_report_v0_1.json"
    report_path.parent.mkdir(parents=True, exist_ok=True)

    command_runs: list[dict[str, Any]] = []
    checks: dict[str, bool] = {}
    failures: list[str] = []

    run = run_cmd(repo, [py, "scripts/officio_agentis_validate_foundation_v0_1.py"])
    command_runs.append(run)
    checks["foundation_check_pass"] = run["returncode"] == 0
    if run["returncode"] != 0:
        failures.append("Foundation check failed")

    for role in ROLES:
        run = run_cmd(repo, [py, "scripts/officio_agentis_validate_role_contract_v0_1.py", "--role", role])
        command_runs.append(run)
        key = f"role_{role.lower()}_check_pass"
        checks[key] = run["returncode"] == 0
        if run["returncode"] != 0:
            failures.append(f"Role check failed: {role}")

    run = run_cmd(repo, [py, "ORGANS/OFFICIO_AGENTIS/TESTS/run_role_tests.py", "--dry-run"])
    command_runs.append(run)
    checks["dry_run_tests_pass"] = run["returncode"] == 0
    if run["returncode"] != 0:
        failures.append("Dry-run tests failed")

    run = run_cmd(repo, [py, "ORGANS/OFFICIO_AGENTIS/TESTS/run_role_tests.py", "--critical-only", "--dry-run"])
    command_runs.append(run)
    checks["critical_dry_run_tests_pass"] = run["returncode"] == 0
    if run["returncode"] != 0:
        failures.append("Critical-only dry-run tests failed")

    # Registry sanity checks
    role_registry_path = repo / "ORGANS/OFFICIO_AGENTIS/REGISTRY/ROLE_REGISTRY.json"
    registry_ok = role_registry_path.exists()
    if registry_ok:
        role_registry = load_json(role_registry_path)
        role_ids = {entry.get("role_id") for entry in role_registry.get("roles", []) if isinstance(entry, dict)}
        registry_ok = set(ROLES).issubset(role_ids)
    checks["role_registry_has_all_roles"] = registry_ok
    if not registry_ok:
        failures.append("Role registry missing one or more required roles")

    status = "PASS" if all(checks.values()) else "FAIL"
    payload = {
        "schema_version": "officio_agentis_check_all_report_v0_1",
        "task_id": TASK_ID,
        "status": status,
        "checked_utc": utc_now(),
        "checks": checks,
        "failures": failures,
        "command_runs": command_runs,
    }
    report_path.write_text(json.dumps(payload, ensure_ascii=True, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(payload, ensure_ascii=True))
    return 0 if status == "PASS" else 1


if __name__ == "__main__":
    sys.exit(main())
