#!/usr/bin/env python3
"""Deterministic dry-run role test validator for Officio Agentis."""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROLE_TEST_FILES = {
    "SERVITOR": "ORGANS/OFFICIO_AGENTIS/TESTS/SERVITOR_TESTS.json",
    "LOGOS_PRIME": "ORGANS/OFFICIO_AGENTIS/TESTS/LOGOS_PRIME_TESTS.json",
    "LOGOS_SPECULUM": "ORGANS/OFFICIO_AGENTIS/TESTS/LOGOS_SPECULUM_TESTS.json",
    "ADVISOR_SERVITOR": "ORGANS/OFFICIO_AGENTIS/TESTS/ADVISOR_SERVITOR_TESTS.json",
}
REQUIRED_TEST_FIELDS = [
    "test_id",
    "role_id",
    "mode_id",
    "scenario",
    "input_summary",
    "expected_behavior",
    "pass_criteria",
    "fail_criteria",
    "evidence_required",
    "risk_covered",
]
REQUIRED_CRITICAL_IDS = {
    "OA-CRIT-01",
    "OA-CRIT-02",
    "OA-CRIT-03",
    "OA-CRIT-04",
    "OA-CRIT-05",
    "OA-CRIT-06",
    "OA-CRIT-07",
    "OA-CRIT-08",
    "OA-CRIT-09",
    "OA-CRIT-10",
}


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def ensure_str(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--role", choices=sorted(ROLE_TEST_FILES.keys()))
    parser.add_argument("--critical-only", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument(
        "--report",
        default="ORGANS/OFFICIO_AGENTIS/REPORTS/role_test_dry_run_report_v0_1.json",
    )
    args = parser.parse_args()

    repo = Path(__file__).resolve().parents[3]
    report_path = repo / args.report
    report_path.parent.mkdir(parents=True, exist_ok=True)

    checks: dict[str, bool] = {}
    failures: list[str] = []
    loaded_role_tests: dict[str, list[dict[str, Any]]] = {}
    all_test_ids: dict[str, set[str]] = {}

    selected_roles = [args.role] if args.role else list(ROLE_TEST_FILES.keys())
    checks["dry_run_mode"] = bool(args.dry_run)
    if not checks["dry_run_mode"]:
        failures.append("Only --dry-run mode is supported in MVP test runner")

    # Load test case schema and required field contract.
    schema_path = repo / "ORGANS/OFFICIO_AGENTIS/SCHEMAS/agent_test_case.schema.json"
    schema_ok = schema_path.exists()
    if schema_ok:
        schema = load_json(schema_path)
        schema_required = schema.get("required", [])
        schema_ok = set(REQUIRED_TEST_FIELDS).issubset(set(schema_required))
    checks["test_case_schema_available"] = schema_ok
    if not schema_ok:
        failures.append("agent_test_case.schema.json missing or incompatible")

    for role_id in selected_roles:
        test_file = repo / ROLE_TEST_FILES[role_id]
        if not test_file.exists():
            failures.append(f"Missing role test file: {ROLE_TEST_FILES[role_id]}")
            continue
        payload = load_json(test_file)
        tests = payload.get("tests", [])
        if payload.get("role_id") != role_id:
            failures.append(f"role_id mismatch in {ROLE_TEST_FILES[role_id]}")
        if not isinstance(tests, list) or not tests:
            failures.append(f"tests list missing/empty in {ROLE_TEST_FILES[role_id]}")
            tests = []
        loaded_role_tests[role_id] = tests
        all_test_ids[role_id] = {entry.get("test_id") for entry in tests if isinstance(entry, dict)}

    checks["selected_role_files_loaded"] = len(loaded_role_tests) == len(selected_roles)
    checks["each_selected_role_has_tests"] = all(len(loaded_role_tests.get(role_id, [])) > 0 for role_id in selected_roles)

    field_errors: list[str] = []
    for role_id, tests in loaded_role_tests.items():
        for idx, test_case in enumerate(tests):
            if not isinstance(test_case, dict):
                field_errors.append(f"{role_id}[{idx}] not object")
                continue
            for field in REQUIRED_TEST_FIELDS:
                if field not in test_case:
                    field_errors.append(f"{role_id}[{idx}] missing '{field}'")
                elif not ensure_str(test_case[field]):
                    field_errors.append(f"{role_id}[{idx}] invalid '{field}' value")
            if test_case.get("role_id") != role_id:
                field_errors.append(f"{role_id}[{idx}] role_id mismatch")
    checks["test_fields_valid"] = len(field_errors) == 0
    failures.extend(field_errors)

    # Critical test inventory validation.
    critical_path = repo / "ORGANS/OFFICIO_AGENTIS/TESTS/OFFICIO_CRITICAL_TESTS.json"
    critical_ok = critical_path.exists()
    critical_payload = {"critical_tests": []}
    if critical_ok:
        critical_payload = load_json(critical_path)
    else:
        failures.append("Missing OFFICIO_CRITICAL_TESTS.json")
    checks["critical_inventory_exists"] = critical_ok

    critical_entries = critical_payload.get("critical_tests", []) if isinstance(critical_payload, dict) else []
    critical_ids = {entry.get("critical_id") for entry in critical_entries if isinstance(entry, dict)}
    checks["required_critical_ids_present"] = REQUIRED_CRITICAL_IDS.issubset(critical_ids)
    if not checks["required_critical_ids_present"]:
        missing = sorted(REQUIRED_CRITICAL_IDS - critical_ids)
        failures.append("Missing required critical IDs: " + ", ".join(missing))

    # For critical mapping checks, load all role tests regardless of --role filter.
    all_roles_tests: dict[str, set[str]] = {}
    for role_id, rel_path in ROLE_TEST_FILES.items():
        path = repo / rel_path
        if not path.exists():
            continue
        payload = load_json(path)
        all_roles_tests[role_id] = {entry.get("test_id") for entry in payload.get("tests", []) if isinstance(entry, dict)}

    mapping_errors: list[str] = []
    for entry in critical_entries:
        if not isinstance(entry, dict):
            continue
        role_id = entry.get("mapped_role_id")
        test_id = entry.get("mapped_test_id")
        if role_id not in all_roles_tests:
            mapping_errors.append(f"Critical mapping role missing: {role_id}")
            continue
        if test_id not in all_roles_tests[role_id]:
            mapping_errors.append(f"Critical mapping test missing: {role_id}/{test_id}")
    checks["critical_mappings_resolved"] = len(mapping_errors) == 0
    failures.extend(mapping_errors)

    if args.critical_only:
        # In critical-only mode only critical inventory and mappings determine PASS.
        status = "PASS" if all(
            checks.get(key, False)
            for key in [
                "dry_run_mode",
                "critical_inventory_exists",
                "required_critical_ids_present",
                "critical_mappings_resolved",
            ]
        ) else "FAIL"
    else:
        status = "PASS" if all(checks.values()) else "FAIL"

    report = {
        "schema_version": "officio_role_test_dry_run_report_v0_1",
        "status": status,
        "checked_utc": utc_now(),
        "dry_run": bool(args.dry_run),
        "critical_only": bool(args.critical_only),
        "role_filter": args.role,
        "checks": checks,
        "failures": failures,
        "selected_roles": selected_roles,
        "loaded_test_counts": {role_id: len(tests) for role_id, tests in loaded_role_tests.items()},
    }
    report_path.write_text(json.dumps(report, ensure_ascii=True, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, ensure_ascii=True))
    return 0 if status == "PASS" else 1


if __name__ == "__main__":
    sys.exit(main())
