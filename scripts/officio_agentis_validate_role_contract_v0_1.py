#!/usr/bin/env python3
"""Validate Officio Agentis role contracts for MVP v0.1."""

from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


TASK_ID = "TASK-20260515-BUILD-OFFICIO-AGENTIS-MVP-V0_1"
VALID_ROLES = {"SERVITOR", "LOGOS_PRIME", "LOGOS_SPECULUM", "ADVISOR_SERVITOR"}
ROLE_REPORT_PATHS = {
    "SERVITOR": "ORGANS/OFFICIO_AGENTIS/REPORTS/servitor_contract_check_report_v0_1.json",
    "LOGOS_PRIME": "ORGANS/OFFICIO_AGENTIS/REPORTS/logos_prime_contract_check_report_v0_1.json",
    "LOGOS_SPECULUM": "ORGANS/OFFICIO_AGENTIS/REPORTS/logos_speculum_contract_check_report_v0_1.json",
    "ADVISOR_SERVITOR": "ORGANS/OFFICIO_AGENTIS/REPORTS/advisor_servitor_contract_check_report_v0_1.json",
}
ROLE_PATHS = {
    "SERVITOR": {
        "role_json": "ORGANS/OFFICIO_AGENTIS/ROLE_CONTRACTS/SERVITOR.json",
        "role_md": "ORGANS/OFFICIO_AGENTIS/ROLE_CONTRACTS/SERVITOR.md",
        "modes": "ORGANS/OFFICIO_AGENTIS/MODES/SERVITOR_MODES.json",
        "prompt": "ORGANS/OFFICIO_AGENTIS/PROMPTS/SERVITOR_SYSTEM_PROMPT.md",
        "tests": "ORGANS/OFFICIO_AGENTIS/TESTS/SERVITOR_TESTS.json",
    },
    "LOGOS_PRIME": {
        "role_json": "ORGANS/OFFICIO_AGENTIS/ROLE_CONTRACTS/LOGOS_PRIME.json",
        "role_md": "ORGANS/OFFICIO_AGENTIS/ROLE_CONTRACTS/LOGOS_PRIME.md",
        "modes": "ORGANS/OFFICIO_AGENTIS/MODES/LOGOS_PRIME_MODES.json",
        "prompt": "ORGANS/OFFICIO_AGENTIS/PROMPTS/LOGOS_PRIME_SYSTEM_PROMPT.md",
        "tests": "ORGANS/OFFICIO_AGENTIS/TESTS/LOGOS_PRIME_TESTS.json",
    },
    "LOGOS_SPECULUM": {
        "role_json": "ORGANS/OFFICIO_AGENTIS/ROLE_CONTRACTS/LOGOS_SPECULUM.json",
        "role_md": "ORGANS/OFFICIO_AGENTIS/ROLE_CONTRACTS/LOGOS_SPECULUM.md",
        "modes": "ORGANS/OFFICIO_AGENTIS/MODES/LOGOS_SPECULUM_MODES.json",
        "prompt": "ORGANS/OFFICIO_AGENTIS/PROMPTS/LOGOS_SPECULUM_SYSTEM_PROMPT.md",
        "tests": "ORGANS/OFFICIO_AGENTIS/TESTS/LOGOS_SPECULUM_TESTS.json",
    },
    "ADVISOR_SERVITOR": {
        "role_json": "ORGANS/OFFICIO_AGENTIS/ROLE_CONTRACTS/ADVISOR_SERVITOR.json",
        "role_md": "ORGANS/OFFICIO_AGENTIS/ROLE_CONTRACTS/ADVISOR_SERVITOR.md",
        "modes": "ORGANS/OFFICIO_AGENTIS/MODES/ADVISOR_SERVITOR_MODES.json",
        "prompt": "ORGANS/OFFICIO_AGENTIS/PROMPTS/ADVISOR_SERVITOR_SYSTEM_PROMPT.md",
        "tests": "ORGANS/OFFICIO_AGENTIS/TESTS/ADVISOR_SERVITOR_TESTS.json",
    },
}

COMMON_REQUIRED_ROLE_KEYS = [
    "schema_version",
    "task_id",
    "role_id",
    "role_name",
    "mission",
    "allowed_actions",
    "forbidden_actions",
    "question_policy",
    "autonomy_level",
    "evidence_requirement",
    "response_style",
    "artifact_style",
    "stop_conditions",
    "settings",
]
COMMON_REQUIRED_SETTINGS = [
    "temperature_concept",
    "verbosity",
    "autonomy",
    "question_threshold",
    "risk_tolerance",
    "execution_strictness",
    "evidence_strictness",
    "memory_behavior",
]
COMMON_REQUIRED_TEST_FIELDS = [
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
ROLE_RULES = {
    "SERVITOR": {
        "required_mode_ids": {"EXECUTE", "CHECK_ONLY", "REPAIR_WITHIN_SCOPE", "STOPPED_PENDING_OWNER"},
        "required_test_ids": {
            "SERVITOR-TEST-01-CLEAR-STAGE-NO-QUESTION",
            "SERVITOR-TEST-02-MISSING-INPUT-STOP",
            "SERVITOR-TEST-03-FAILED-CHECKER-STOP",
            "SERVITOR-TEST-04-BLOCKER-ONLY-QUESTION",
            "SERVITOR-TEST-05-TASK-ID-CONTRADICTION-STOP",
            "SERVITOR-TEST-06-OWNER-COMMENT-RUSSIAN",
            "SERVITOR-TEST-07-CANONICAL-ARTIFACT-ENGLISH",
        },
        "required_prompt_markers": [
            "cold exact executor",
            "questions only for blockers",
            "no fake green",
            "no pass without checker evidence",
        ],
    },
    "LOGOS_PRIME": {
        "required_mode_ids": {"CHAT_ASSIST", "PLANNING", "COMMAND_BUILDER", "HANDOFF", "REVIEW"},
        "required_test_ids": {
            "LOGOS-PRIME-TEST-01-PLAN-TABLE-PATH-FIRST",
            "LOGOS-PRIME-TEST-02-ENGLISH-WRITE-PROMPT-REFUSAL",
            "LOGOS-PRIME-TEST-03-EXACT-PISHI-PROMT-ALLOWED",
            "LOGOS-PRIME-TEST-04-BROKEN-COMMAND-SAFETY",
            "LOGOS-PRIME-TEST-05-PATH-CONFUSION-CLARIFY",
            "LOGOS-PRIME-TEST-06-MARK-ASSUMPTION",
            "LOGOS-PRIME-TEST-07-MARK-FACT-WITH-SOURCE",
        },
        "required_prompt_markers": [
            "table-first",
            "path-first",
            "fact",
            "assumption",
            "proposal",
            "Пиши промт",
        ],
    },
    "LOGOS_SPECULUM": {
        "required_mode_ids": {"RED_TEAM", "SPEC_REVIEW", "GATE_AUDIT", "CONTRADICTION_HUNT"},
        "required_test_ids": {
            "LOGOS-SPECULUM-TEST-01-FAKE-GREEN-DETECTION",
            "LOGOS-SPECULUM-TEST-02-CONTRADICTION-CROSS-PATH",
            "LOGOS-SPECULUM-TEST-03-REFUSE-QUICK-APPROVAL",
            "LOGOS-SPECULUM-TEST-04-WEAK-GATE-FINDING",
            "LOGOS-SPECULUM-TEST-05-CLEAN-ARTIFACT-NO-FALSE-POSITIVE",
            "LOGOS-SPECULUM-TEST-06-DUPLICATE-LOGIC-FINDING",
            "LOGOS-SPECULUM-TEST-07-HIDDEN-ASSUMPTION-FINDING",
        },
        "required_prompt_markers": [
            "no flattery",
            "no approval without evidence",
            "no execution",
            "severity",
            "pass criteria",
        ],
    },
    "ADVISOR_SERVITOR": {
        "required_mode_ids": {"RESEARCH", "PLAN_BUILDER", "OPTIONS_REVIEW", "TASK_CLARIFIER"},
        "required_test_ids": {
            "ADVISOR-SERVITOR-TEST-01-CLEAR-PLANNING-OPTIONS",
            "ADVISOR-SERVITOR-TEST-02-GENUINE-AMBIGUITY-QUESTION",
            "ADVISOR-SERVITOR-TEST-03-EXECUTION-REQUIRES-PROMOTION",
            "ADVISOR-SERVITOR-TEST-04-RESEARCH-SOURCE-CITATION",
            "ADVISOR-SERVITOR-TEST-05-RECOMMENDATION-WITH-REASONING",
            "ADVISOR-SERVITOR-TEST-06-IMPLEMENTATION-STEPS-PATH-SEQUENCE",
            "ADVISOR-SERVITOR-TEST-07-ADVISORY-ARTIFACT-ENGLISH",
        },
        "required_prompt_markers": [
            "planning",
            "research",
            "options",
            "no execution without explicit promotion",
            "source citation",
        ],
    },
}


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def ensure_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def contains_required_fields(obj: dict[str, Any], required: list[str]) -> list[str]:
    return [key for key in required if key not in obj]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--role", required=True, choices=sorted(VALID_ROLES))
    args = parser.parse_args()

    repo = Path(__file__).resolve().parents[1]
    role = args.role
    role_paths = ROLE_PATHS[role]
    role_rules = ROLE_RULES[role]

    checks: dict[str, bool] = {}
    failures: list[str] = []
    evidence_paths: list[str] = []

    resolved = {name: (repo / rel) for name, rel in role_paths.items()}
    for name, path in resolved.items():
        exists = path.exists()
        checks[f"{name}_exists"] = exists
        if not exists:
            failures.append(f"Missing required file: {role_paths[name]}")
        else:
            evidence_paths.append(role_paths[name])

    if not all(checks.values()):
        report = {
            "schema_version": "officio_role_contract_check_report_v0_1",
            "task_id": TASK_ID,
            "role_id": role,
            "status": "FAIL",
            "checked_utc": utc_now(),
            "checks": checks,
            "failures": failures,
            "evidence_paths": evidence_paths,
        }
        report_path = repo / ROLE_REPORT_PATHS[role]
        report_path.parent.mkdir(parents=True, exist_ok=True)
        report_path.write_text(json.dumps(report, ensure_ascii=True, indent=2) + "\n", encoding="utf-8")
        print(json.dumps(report, ensure_ascii=True))
        return 1

    role_json = load_json(resolved["role_json"])
    mode_json = load_json(resolved["modes"])
    tests_json = load_json(resolved["tests"])
    role_md_text = ensure_text(resolved["role_md"]).lower()
    prompt_text = ensure_text(resolved["prompt"])
    prompt_text_lower = prompt_text.lower()

    missing_role_keys = contains_required_fields(role_json, COMMON_REQUIRED_ROLE_KEYS)
    checks["role_json_has_required_keys"] = not missing_role_keys
    if missing_role_keys:
        failures.append("Missing role JSON keys: " + ", ".join(missing_role_keys))

    checks["task_id_exact"] = role_json.get("task_id") == TASK_ID
    if not checks["task_id_exact"]:
        failures.append("task_id mismatch in role JSON")

    checks["role_id_matches_argument"] = role_json.get("role_id") == role
    if not checks["role_id_matches_argument"]:
        failures.append("role_id does not match --role argument")

    settings = role_json.get("settings", {})
    settings_missing = contains_required_fields(settings, COMMON_REQUIRED_SETTINGS) if isinstance(settings, dict) else COMMON_REQUIRED_SETTINGS
    checks["settings_required_keys_present"] = len(settings_missing) == 0
    if settings_missing:
        failures.append("Missing settings keys: " + ", ".join(settings_missing))

    checks["owner_language_russian"] = role_json.get("response_style", {}).get("owner_language") == "RUSSIAN"
    if not checks["owner_language_russian"]:
        failures.append("response_style.owner_language must be RUSSIAN")

    checks["canonical_artifact_language_english"] = role_json.get("artifact_style", {}).get("canonical_language") == "ENGLISH"
    if not checks["canonical_artifact_language_english"]:
        failures.append("artifact_style.canonical_language must be ENGLISH")

    mode_ids = {entry.get("mode_id") for entry in mode_json.get("modes", []) if isinstance(entry, dict)}
    required_mode_ids = role_rules["required_mode_ids"]
    checks["required_modes_present"] = required_mode_ids.issubset(mode_ids)
    if not checks["required_modes_present"]:
        missing = sorted(required_mode_ids - mode_ids)
        failures.append("Missing required mode_id values: " + ", ".join(missing))

    tests = tests_json.get("tests", [])
    test_ids = {entry.get("test_id") for entry in tests if isinstance(entry, dict)}
    required_test_ids = role_rules["required_test_ids"]
    checks["required_tests_present"] = required_test_ids.issubset(test_ids)
    if not checks["required_tests_present"]:
        missing = sorted(required_test_ids - test_ids)
        failures.append("Missing required test_id values: " + ", ".join(missing))

    missing_test_fields: list[str] = []
    for idx, test_case in enumerate(tests):
        if not isinstance(test_case, dict):
            missing_test_fields.append(f"tests[{idx}] is not object")
            continue
        for field in COMMON_REQUIRED_TEST_FIELDS:
            if field not in test_case:
                missing_test_fields.append(f"tests[{idx}] missing field '{field}'")
    checks["tests_have_required_fields"] = len(missing_test_fields) == 0
    failures.extend(missing_test_fields)

    checks["prompt_required_markers_present"] = all(marker.lower() in prompt_text_lower for marker in role_rules["required_prompt_markers"])
    if not checks["prompt_required_markers_present"]:
        for marker in role_rules["required_prompt_markers"]:
            if marker.lower() not in prompt_text_lower:
                failures.append(f"Prompt marker missing: {marker}")

    checks["md_forbids_fake_green"] = "fake green" in role_md_text
    if not checks["md_forbids_fake_green"]:
        failures.append("Role markdown must explicitly forbid fake green")

    role_specific_ok = True
    if role == "SERVITOR":
        checks["question_policy_blocker_only"] = role_json.get("question_policy") == "BLOCKER_ONLY"
        checks["autonomy_low"] = role_json.get("autonomy_level") == "LOW"
        checks["evidence_mandatory"] = role_json.get("evidence_requirement") == "MANDATORY"
        checks["no_creative_drift_forbidden"] = any("creative" in item for item in role_json.get("forbidden_actions", []))
        checks["optional_questions_forbidden"] = any("optional" in item for item in role_json.get("forbidden_actions", []))
        checks["stop_contains_failed_checker"] = any("failed_checker" == item for item in role_json.get("stop_conditions", []))
        role_specific_ok = all(checks[key] for key in [
            "question_policy_blocker_only",
            "autonomy_low",
            "evidence_mandatory",
            "no_creative_drift_forbidden",
            "optional_questions_forbidden",
            "stop_contains_failed_checker",
        ])
    elif role == "LOGOS_PRIME":
        mission_text = " ".join(role_json.get("mission", [])).lower()
        checks["prompt_rule_exact_phrase_present"] = "Пиши промт" in prompt_text and "Пиши промт" in ensure_text(resolved["role_md"])
        checks["prompt_rule_in_tests_present"] = {
            "LOGOS-PRIME-TEST-02-ENGLISH-WRITE-PROMPT-REFUSAL",
            "LOGOS-PRIME-TEST-03-EXACT-PISHI-PROMT-ALLOWED"
        }.issubset(test_ids)
        checks["fact_assumption_proposal_split"] = bool(role_json.get("response_style", {}).get("fact_assumption_proposal_split"))
        checks["no_repo_execution_without_approval"] = "NO_REPO_CHANGES_WITHOUT_OWNER_APPROVAL" in str(role_json.get("settings", {}).get("execution_strictness", ""))
        checks["mission_protection_markers"] = all(
            marker in mission_text
            for marker in ["continuity", "planning", "command", "review", "fake green", "mojibake", "stale git truth"]
        )
        role_specific_ok = all(checks[key] for key in [
            "prompt_rule_exact_phrase_present",
            "prompt_rule_in_tests_present",
            "fact_assumption_proposal_split",
            "no_repo_execution_without_approval",
            "mission_protection_markers",
        ])
    elif role == "LOGOS_SPECULUM":
        forbidden_text = " ".join(role_json.get("forbidden_actions", [])).lower()
        checks["execution_forbidden"] = "forbidden" in str(role_json.get("settings", {}).get("execution_strictness", "")).lower() or "zero" in str(role_json.get("autonomy_level", "")).lower()
        checks["flattery_forbidden"] = "flattery" in forbidden_text
        checks["approval_without_audit_forbidden"] = "approval" in forbidden_text and "audit" in forbidden_text
        checks["evidence_mandatory"] = role_json.get("evidence_requirement") == "MANDATORY"
        checks["finding_fields_required"] = all(
            marker in prompt_text_lower
            for marker in ["source path", "artifact", "severity", "fix", "pass criteria"]
        )
        role_specific_ok = all(checks[key] for key in [
            "execution_forbidden",
            "flattery_forbidden",
            "approval_without_audit_forbidden",
            "evidence_mandatory",
            "finding_fields_required",
        ])
    elif role == "ADVISOR_SERVITOR":
        mission_text = " ".join(role_json.get("mission", [])).lower()
        checks["execution_boundary_no_promotion"] = "NO_EXECUTION_WITHOUT_EXPLICIT_PROMOTION" in str(role_json.get("settings", {}).get("execution_strictness", ""))
        checks["mission_planning_research_options"] = all(
            marker in mission_text for marker in ["planning", "research", "option", "clarification", "advisory"]
        )
        checks["question_policy_defined"] = role_json.get("question_policy") in {"WHEN_NEEDED", "NECESSARY_ONLY"}
        checks["source_citation_required"] = "CITE_SOURCES" in str(role_json.get("settings", {}).get("evidence_strictness", ""))
        role_specific_ok = all(checks[key] for key in [
            "execution_boundary_no_promotion",
            "mission_planning_research_options",
            "question_policy_defined",
            "source_citation_required",
        ])

    checks["role_specific_checks_pass"] = role_specific_ok
    if not role_specific_ok:
        failures.append(f"Role-specific checks failed for {role}")

    # Quick canonical artifact language scan for role JSON top-level string values.
    cyrillic_pattern = re.compile(r"[А-Яа-яЁё]")
    russian_hits = []
    for key, value in role_json.items():
        if isinstance(value, str) and cyrillic_pattern.search(value):
            russian_hits.append(key)
    checks["role_json_canonical_language_english_only"] = len(russian_hits) == 0
    if russian_hits:
        failures.append("Role JSON contains Russian in canonical string fields: " + ", ".join(russian_hits))

    status = "PASS" if all(checks.values()) else "FAIL"
    report = {
        "schema_version": "officio_role_contract_check_report_v0_1",
        "task_id": TASK_ID,
        "role_id": role,
        "status": status,
        "checked_utc": utc_now(),
        "checks": checks,
        "failures": failures,
        "evidence_paths": evidence_paths,
    }
    report_path = repo / ROLE_REPORT_PATHS[role]
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(json.dumps(report, ensure_ascii=True, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, ensure_ascii=True))
    return 0 if status == "PASS" else 1


if __name__ == "__main__":
    sys.exit(main())
