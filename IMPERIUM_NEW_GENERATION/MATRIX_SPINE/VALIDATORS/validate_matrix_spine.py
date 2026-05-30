#!/usr/bin/env python3
"""Matrix Spine validator suite for Ghost_Evolve V2 tasks."""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

TASK_ID_DEFAULT = "TASK-NEWGEN-MECHANICUS-MATRIX-SPINE-VALIDATOR-SUITE-VM3-V0_1"

DEFAULT_ALLOWED_STATUS_VOCAB = {
    "CANDIDATE",
    "ACTIVE",
    "CANON",
    "DEPRECATED",
    "QUARANTINE",
    "BLOCKED",
    "WARN",
    "CANDIDATE_NOT_CANON",
}

MATRIX_STATUS_POLICY_PATH = "IMPERIUM_NEW_GENERATION/MATRIX_SPINE/SCHEMAS/matrix_status_policy.json"
NEGATIVE_FIXTURE_MANIFEST_PATH = "IMPERIUM_NEW_GENERATION/MATRIX_SPINE/FIXTURES/negative_fixture_manifest.json"

ALLOWED_OWNER_ORGANS = {
    "Global",
    "Administratum",
    "Astronomicon",
    "Doctrinarium",
    "Inquisition",
    "Mechanicus",
    "Officio Agentis",
    "Schola Imperialis",
    "Strategium",
}

ALLOWED_SUPPORT_ORGANS = set(ALLOWED_OWNER_ORGANS) | {"Agent IDE"}

REQUIRED_READ_FIRST_PACKETS = [
    "IMPERIUM_NEW_GENERATION/ORGANS/DOCTRINARIUM/READ_FIRST_GHOST_EVOLVE_PACKET.md",
    "IMPERIUM_NEW_GENERATION/ORGANS/OFFICIO_AGENTIS/READ_FIRST_GHOST_EVOLVE_PACKET.md",
    "IMPERIUM_NEW_GENERATION/ORGANS/ASTRONOMICON/READ_FIRST_GHOST_EVOLVE_PACKET.md",
    "IMPERIUM_NEW_GENERATION/ORGANS/ADMINISTRATUM/READ_FIRST_GHOST_EVOLVE_PACKET.md",
    "IMPERIUM_NEW_GENERATION/ORGANS/MECHANICUS/READ_FIRST_GHOST_EVOLVE_PACKET.md",
    "IMPERIUM_NEW_GENERATION/ORGANS/INQUISITION/READ_FIRST_GHOST_EVOLVE_PACKET.md",
    "IMPERIUM_NEW_GENERATION/ORGANS/STRATEGIUM/READ_FIRST_GHOST_EVOLVE_PACKET.md",
    "IMPERIUM_NEW_GENERATION/ORGANS/SCHOLA_IMPERIALIS/READ_FIRST_GHOST_EVOLVE_PACKET.md",
]

REQUIRED_VALIDATOR_FILES = [
    "IMPERIUM_NEW_GENERATION/MATRIX_SPINE/VALIDATORS/validate_matrix_spine.py",
    "IMPERIUM_NEW_GENERATION/MATRIX_SPINE/VALIDATORS/README_VALIDATORS.md",
    "IMPERIUM_NEW_GENERATION/MATRIX_SPINE/VALIDATORS/run_matrix_spine_validation.sh",
    "IMPERIUM_NEW_GENERATION/MATRIX_SPINE/VALIDATORS/run_matrix_spine_validation.ps1",
    "IMPERIUM_NEW_GENERATION/MATRIX_SPINE/VALIDATORS/run_synthetic_runtime_corridor.py",
    "IMPERIUM_NEW_GENERATION/MATRIX_SPINE/VALIDATORS/run_synthetic_runtime_corridor.sh",
    "IMPERIUM_NEW_GENERATION/MATRIX_SPINE/VALIDATORS/run_synthetic_runtime_corridor.ps1",
    "IMPERIUM_NEW_GENERATION/MATRIX_SPINE/VALIDATORS/score_efficiency_delta.py",
    "IMPERIUM_NEW_GENERATION/MATRIX_SPINE/VALIDATORS/run_efficiency_delta.sh",
    "IMPERIUM_NEW_GENERATION/MATRIX_SPINE/VALIDATORS/run_efficiency_delta.ps1",
]


@dataclass
class Issue:
    severity: str
    code: str
    message: str
    path: str = ""
    details: dict[str, Any] | None = None

    def to_json(self) -> dict[str, Any]:
        payload: dict[str, Any] = {
            "severity": self.severity,
            "code": self.code,
            "message": self.message,
        }
        if self.path:
            payload["path"] = self.path
        if self.details:
            payload["details"] = self.details
        return payload


def utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def add_issue(
    issues: list[Issue],
    severity: str,
    code: str,
    message: str,
    path: Path | str | None = None,
    details: dict[str, Any] | None = None,
) -> None:
    issues.append(
        Issue(
            severity=severity,
            code=code,
            message=message,
            path=str(path) if path is not None else "",
            details=details,
        )
    )


def read_json(path: Path) -> tuple[Any | None, str | None]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:  # pragma: no cover - defensive
        return None, str(exc)
    return data, None


def validate_value_against_rule(value: Any, rule: dict[str, Any]) -> list[str]:
    errors: list[str] = []

    if "oneOf" in rule:
        variants = rule["oneOf"]
        for variant in variants:
            if not validate_value_against_rule(value, variant):
                return []
        errors.append("value does not satisfy any oneOf variant")
        return errors

    expected_type = rule.get("type")
    if expected_type == "object" and not isinstance(value, dict):
        errors.append("expected object")
    elif expected_type == "array" and not isinstance(value, list):
        errors.append("expected array")
    elif expected_type == "string" and not isinstance(value, str):
        errors.append("expected string")
    elif expected_type == "number" and not isinstance(value, (int, float)):
        errors.append("expected number")
    elif expected_type == "integer" and not isinstance(value, int):
        errors.append("expected integer")
    elif expected_type == "boolean" and not isinstance(value, bool):
        errors.append("expected boolean")
    elif expected_type == "null" and value is not None:
        errors.append("expected null")

    if "enum" in rule and value not in rule["enum"]:
        errors.append("value not in enum")

    if isinstance(value, str) and "minLength" in rule and len(value) < int(rule["minLength"]):
        errors.append("string shorter than minLength")

    if isinstance(value, list):
        if "minItems" in rule and len(value) < int(rule["minItems"]):
            errors.append("array shorter than minItems")
        item_rule = rule.get("items")
        if isinstance(item_rule, dict):
            for idx, item in enumerate(value):
                nested_errors = validate_value_against_rule(item, item_rule)
                if nested_errors:
                    errors.append(f"array item {idx}: {', '.join(nested_errors)}")
                    break

    return errors


def validate_schema_object(
    *,
    data: Any,
    schema: dict[str, Any],
    context: str,
    issues: list[Issue],
    path: Path,
) -> None:
    if not isinstance(data, dict):
        add_issue(
            issues,
            "FAIL",
            f"{context}_ROOT_NOT_OBJECT",
            "JSON root is not an object.",
            path,
        )
        return

    required_keys = schema.get("required", [])
    if isinstance(required_keys, list):
        missing = [key for key in required_keys if key not in data]
        if missing:
            add_issue(
                issues,
                "FAIL",
                f"{context}_REQUIRED_MISSING",
                "Required schema keys are missing.",
                path,
                {"missing": missing},
            )

    properties = schema.get("properties", {})
    if isinstance(properties, dict):
        for key, rule in properties.items():
            if key not in data or not isinstance(rule, dict):
                continue
            errors = validate_value_against_rule(data[key], rule)
            if errors:
                add_issue(
                    issues,
                    "FAIL",
                    f"{context}_PROPERTY_INVALID",
                    f"Schema validation failed for property '{key}'.",
                    path,
                    {"property": key, "errors": errors},
                )


def validate_matrix_payload(
    data: dict[str, Any],
    path: Path,
    issues: list[Issue],
    allowed_status_vocab: set[str],
) -> None:
    matrix_id = data.get("matrix_id")
    if not isinstance(matrix_id, str) or not matrix_id.strip():
        add_issue(issues, "FAIL", "MATRIX_ID_MISSING", "matrix_id is missing or empty.", path)

    owner = data.get("owner_organ")
    if not isinstance(owner, str) or not owner.strip():
        add_issue(issues, "FAIL", "MATRIX_OWNER_MISSING", "owner_organ is missing.", path)
    elif owner not in ALLOWED_OWNER_ORGANS:
        add_issue(
            issues,
            "FAIL",
            "MATRIX_OWNER_UNKNOWN",
            "owner_organ is not in known organ vocabulary.",
            path,
            {"owner_organ": owner},
        )

    support = data.get("support_organs")
    if not isinstance(support, list) or not support:
        add_issue(
            issues,
            "FAIL",
            "MATRIX_SUPPORT_ORGANS_INVALID",
            "support_organs must be a non-empty list.",
            path,
        )
    else:
        for entry in support:
            if not isinstance(entry, str):
                add_issue(
                    issues,
                    "FAIL",
                    "MATRIX_SUPPORT_ORGAN_TYPE_INVALID",
                    "support_organs entries must be strings.",
                    path,
                )
                break
            if entry not in ALLOWED_SUPPORT_ORGANS:
                add_issue(
                    issues,
                    "WARN",
                    "MATRIX_SUPPORT_ORGAN_UNKNOWN",
                    "support_organs contains non-standard organ name.",
                    path,
                    {"support_organ": entry},
                )

    purpose = data.get("purpose")
    if not isinstance(purpose, str) or not purpose.strip():
        add_issue(issues, "FAIL", "MATRIX_PURPOSE_MISSING", "purpose is missing or empty.", path)

    status = data.get("current_status")
    if not isinstance(status, str) or not status.strip():
        add_issue(issues, "FAIL", "MATRIX_STATUS_MISSING", "current_status is missing.", path)
    elif status not in allowed_status_vocab:
        add_issue(
            issues,
            "FAIL",
            "MATRIX_STATUS_INVALID",
            "current_status is outside allowed vocabulary.",
            path,
            {"current_status": status, "allowed_statuses": sorted(allowed_status_vocab)},
        )

    structure_keys = [
        "required_questions",
        "required_fields",
        "pass_criteria",
        "warn_criteria",
        "block_criteria",
        "entries",
        "checks",
    ]
    has_structure = False
    for key in structure_keys:
        value = data.get(key)
        if isinstance(value, list) and value:
            has_structure = True
            break
    if not has_structure:
        add_issue(
            issues,
            "FAIL",
            "MATRIX_STRUCTURE_FIELDS_MISSING",
            "Matrix has no entries/checks-equivalent structure fields.",
            path,
            {"accepted_structure_keys": structure_keys},
        )


def validate_read_first_packets(repo_root: Path, issues: list[Issue]) -> None:
    for rel_path in REQUIRED_READ_FIRST_PACKETS:
        path = repo_root / rel_path
        if not path.exists():
            add_issue(
                issues,
                "FAIL",
                "READ_FIRST_PACKET_MISSING",
                "Required READ_FIRST packet is missing.",
                path,
            )


def validate_agents_bootloader(repo_root: Path, issues: list[Issue]) -> None:
    agents_path = repo_root / "AGENTS.md"
    if not agents_path.exists():
        add_issue(issues, "FAIL", "AGENTS_MISSING", "AGENTS.md is missing.", agents_path)
        return

    text = agents_path.read_text(encoding="utf-8")
    lines = text.splitlines()
    if len(lines) > 260:
        add_issue(
            issues,
            "FAIL",
            "AGENTS_BOOTLOADER_TOO_LARGE",
            "AGENTS.md exceeds bootloader size cap (260 lines).",
            agents_path,
            {"line_count": len(lines)},
        )

    required_markers = [
        "Bootloader",
        "MATRIX_SPINE_INDEX.md",
        "READ_FIRST_GHOST_EVOLVE_PACKET.md",
    ]
    for marker in required_markers:
        if marker not in text:
            add_issue(
                issues,
                "FAIL",
                "AGENTS_BOOTLOADER_ROUTE_MISSING",
                "AGENTS.md is missing required routing marker.",
                agents_path,
                {"missing_marker": marker},
            )


def validate_required_validator_files(repo_root: Path, issues: list[Issue]) -> None:
    for rel_path in REQUIRED_VALIDATOR_FILES:
        path = repo_root / rel_path
        if not path.exists():
            add_issue(
                issues,
                "FAIL",
                "VALIDATOR_SUITE_FILE_MISSING",
                "Required validator suite file is missing.",
                path,
            )


def validate_schema_file(
    repo_root: Path,
    rel_path: str,
    issues: list[Issue],
    context: str,
) -> dict[str, Any] | None:
    path = repo_root / rel_path
    if not path.exists():
        add_issue(issues, "FAIL", f"{context}_MISSING", "Required schema file is missing.", path)
        return None

    data, error = read_json(path)
    if error is not None:
        add_issue(
            issues,
            "FAIL",
            f"{context}_JSON_PARSE_FAIL",
            "Schema file is not valid JSON.",
            path,
            {"error": error},
        )
        return None

    if not isinstance(data, dict):
        add_issue(
            issues,
            "FAIL",
            f"{context}_ROOT_NOT_OBJECT",
            "Schema file root must be an object.",
            path,
        )
        return None

    for required_top_key in ("type", "properties"):
        if required_top_key not in data:
            add_issue(
                issues,
                "FAIL",
                f"{context}_SCHEMA_TOP_KEY_MISSING",
                "Schema file is missing required top-level key.",
                path,
                {"missing": required_top_key},
            )

    return data


def parse_utc_timestamp(value: Any) -> datetime | None:
    if not isinstance(value, str):
        return None
    try:
        parsed = datetime.strptime(value, "%Y-%m-%dT%H:%M:%SZ")
    except ValueError:
        return None
    return parsed.replace(tzinfo=timezone.utc)


def load_status_policy(
    repo_root: Path,
    issues: list[Issue],
    matrix_schema: dict[str, Any] | None,
) -> set[str]:
    path = repo_root / MATRIX_STATUS_POLICY_PATH
    data, error = read_json(path)
    if error is not None or not isinstance(data, dict):
        add_issue(
            issues,
            "FAIL",
            "MATRIX_STATUS_POLICY_PARSE_FAIL",
            "Status policy JSON is missing or invalid; default vocabulary fallback applied.",
            path,
            {"error": error or "root is not object"},
        )
        return set(DEFAULT_ALLOWED_STATUS_VOCAB)

    allowed = data.get("allowed_statuses")
    if not isinstance(allowed, list) or not allowed:
        add_issue(
            issues,
            "FAIL",
            "MATRIX_STATUS_POLICY_ALLOWED_MISSING",
            "Status policy has no non-empty allowed_statuses list; default vocabulary fallback applied.",
            path,
        )
        return set(DEFAULT_ALLOWED_STATUS_VOCAB)

    allowed_set: set[str] = set()
    for idx, value in enumerate(allowed):
        if not isinstance(value, str) or not value.strip():
            add_issue(
                issues,
                "FAIL",
                "MATRIX_STATUS_POLICY_ALLOWED_INVALID",
                "allowed_statuses contains non-string or empty value.",
                path,
                {"index": idx},
            )
            continue
        allowed_set.add(value)

    if not allowed_set:
        return set(DEFAULT_ALLOWED_STATUS_VOCAB)

    non_canon_statuses = data.get("non_canon_statuses", [])
    if isinstance(non_canon_statuses, list):
        for value in non_canon_statuses:
            if isinstance(value, str) and value not in allowed_set:
                add_issue(
                    issues,
                    "FAIL",
                    "MATRIX_STATUS_POLICY_NONCANON_OUTSIDE_ALLOWED",
                    "non_canon_statuses contains value outside allowed_statuses.",
                    path,
                    {"status": value},
                )

    if "CANDIDATE_NOT_CANON" not in allowed_set:
        add_issue(
            issues,
            "FAIL",
            "MATRIX_STATUS_POLICY_CANDIDATE_NOT_CANON_MISSING",
            "Status policy must explicitly include CANDIDATE_NOT_CANON for this taskpack.",
            path,
        )

    schema_enum: set[str] = set()
    if matrix_schema is not None:
        properties = matrix_schema.get("properties")
        if isinstance(properties, dict):
            current_status = properties.get("current_status")
            if isinstance(current_status, dict):
                enum_values = current_status.get("enum")
                if isinstance(enum_values, list):
                    for value in enum_values:
                        if isinstance(value, str):
                            schema_enum.add(value)

    if schema_enum:
        missing_in_schema = sorted(allowed_set - schema_enum)
        if missing_in_schema:
            add_issue(
                issues,
                "FAIL",
                "MATRIX_STATUS_POLICY_NOT_IN_SCHEMA",
                "Status policy contains values absent from matrix_definition_schema enum.",
                path,
                {"missing_in_schema": missing_in_schema},
            )

        missing_in_policy = sorted(schema_enum - allowed_set)
        if missing_in_policy:
            add_issue(
                issues,
                "FAIL",
                "MATRIX_STATUS_SCHEMA_NOT_IN_POLICY",
                "matrix_definition_schema enum contains statuses absent from status policy.",
                path,
                {"missing_in_policy": missing_in_policy},
            )

    return allowed_set


def validate_matrix_index_membership(
    matrix_id: Any,
    path: Path,
    matrix_index_owner_map: dict[str, str],
    issues: list[Issue],
) -> None:
    if not isinstance(matrix_id, str) or not matrix_id.strip():
        return
    if matrix_id not in matrix_index_owner_map:
        add_issue(
            issues,
            "FAIL",
            "MATRIX_ID_NOT_IN_INDEX",
            "matrix_id is missing from MATRIX_SPINE_INDEX.json.",
            path,
            {"matrix_id": matrix_id},
        )


def validate_capability_split_payload(data: dict[str, Any], path: Path, issues: list[Issue]) -> None:
    items = data.get("items")
    if not isinstance(items, list) or not items:
        add_issue(
            issues,
            "FAIL",
            "CAPABILITY_SPLIT_ITEMS_MISSING",
            "Capability split fixture must include non-empty items list.",
            path,
        )
        return

    replay_required_classes = {"LOCAL_SCRIPT_FIRST", "CANDIDATE_SCRIPT_FIRST"}
    for index, item in enumerate(items):
        if not isinstance(item, dict):
            add_issue(
                issues,
                "FAIL",
                "CAPABILITY_SPLIT_ITEM_NOT_OBJECT",
                "Capability split item must be an object.",
                path,
                {"index": index},
            )
            continue
        classification = item.get("classification")
        replay = item.get("gap_or_replay")
        if classification in replay_required_classes:
            if not isinstance(replay, str) or not replay.strip() or "replay" not in replay.lower():
                add_issue(
                    issues,
                    "FAIL",
                    "CAPABILITY_SPLIT_SCRIPT_FIRST_REPLAY_MISSING",
                    "Script-first capability item is missing explicit replay command.",
                    path,
                    {"index": index, "classification": classification},
                )


def validate_closure_receipt_payload(data: dict[str, Any], path: Path, issues: list[Issue]) -> None:
    required_nonempty = [
        ("base_head", "CLOSURE_RECEIPT_BASE_HEAD_MISSING"),
        ("implementation_head", "CLOSURE_RECEIPT_IMPLEMENTATION_HEAD_MISSING"),
        ("closure_head", "CLOSURE_RECEIPT_CLOSURE_HEAD_MISSING"),
        ("remote_head_after_push", "CLOSURE_RECEIPT_REMOTE_HEAD_MISSING"),
    ]
    for key, code in required_nonempty:
        value = data.get(key)
        if not isinstance(value, str) or not value.strip():
            add_issue(
                issues,
                "FAIL",
                code,
                f"{key} is missing or empty in closure receipt.",
                path,
            )

    clean = data.get("worktree_clean_after_push")
    if clean is not True:
        add_issue(
            issues,
            "FAIL",
            "CLOSURE_RECEIPT_WORKTREE_NOT_CLEAN",
            "worktree_clean_after_push must be true for closure PASS claims.",
            path,
        )

    verdict = data.get("verdict")
    if verdict in {"PASS", "PASS_WITH_WARNINGS"}:
        red_team = data.get("red_team_verdict_path")
        if not isinstance(red_team, str) or not red_team.strip():
            add_issue(
                issues,
                "FAIL",
                "CLOSURE_RECEIPT_RED_TEAM_MISSING",
                "PASS/PASS_WITH_WARNINGS closure receipt requires red_team_verdict_path.",
                path,
            )


def validate_runtime_output_payload(data: dict[str, Any], path: Path, issues: list[Issue]) -> None:
    allowed_output_kinds = {
        "REPORT",
        "RECEIPT",
        "TRANSCRIPT",
        "LOG",
        "FIXTURE",
        "SCHEMA",
        "SCRIPT",
        "SUMMARY",
    }
    outputs = data.get("runtime_outputs")
    if not isinstance(outputs, list) or not outputs:
        add_issue(
            issues,
            "FAIL",
            "RUNTIME_OUTPUTS_MISSING",
            "runtime_outputs list is missing or empty.",
            path,
        )
        return

    for index, item in enumerate(outputs):
        if not isinstance(item, dict):
            add_issue(
                issues,
                "FAIL",
                "RUNTIME_OUTPUT_ITEM_NOT_OBJECT",
                "runtime_outputs entry must be an object.",
                path,
                {"index": index},
            )
            continue
        kind = item.get("output_kind")
        if not isinstance(kind, str) or kind not in allowed_output_kinds:
            add_issue(
                issues,
                "FAIL",
                "RUNTIME_OUTPUT_UNCLASSIFIED",
                "runtime output has unknown output_kind classification.",
                path,
                {"index": index, "output_kind": kind},
            )


def validate_owner_language_contract_payload(data: dict[str, Any], path: Path, issues: list[Issue]) -> None:
    owner_language = data.get("owner_facing_language")
    if owner_language is None:
        add_issue(
            issues,
            "FAIL",
            "OWNER_LANGUAGE_CONTRACT_MISSING",
            "owner_facing_language field is missing.",
            path,
        )
        return
    if owner_language != "RU":
        add_issue(
            issues,
            "FAIL",
            "OWNER_LANGUAGE_CONTRACT_VIOLATION",
            "owner_facing_language must be RU.",
            path,
            {"owner_facing_language": owner_language},
        )


def validate_stale_receipt_payload(data: dict[str, Any], path: Path, issues: list[Issue]) -> None:
    generated_at = parse_utc_timestamp(data.get("receipt_generated_at_utc"))
    reference_at = parse_utc_timestamp(data.get("validation_reference_utc"))
    max_age_hours = data.get("max_age_hours")

    if generated_at is None or reference_at is None or not isinstance(max_age_hours, int):
        add_issue(
            issues,
            "FAIL",
            "STALE_RECEIPT_FIELDS_INVALID",
            "stale receipt fixture requires valid UTC timestamps and integer max_age_hours.",
            path,
        )
        return

    age_hours = (reference_at - generated_at).total_seconds() / 3600.0
    if age_hours > float(max_age_hours):
        add_issue(
            issues,
            "FAIL",
            "STALE_RECEIPT_DETECTED",
            "Receipt age exceeds max_age_hours threshold.",
            path,
            {
                "age_hours": round(age_hours, 2),
                "max_age_hours": max_age_hours,
            },
        )


def load_negative_fixture_manifest(repo_root: Path, issues: list[Issue]) -> list[dict[str, Any]]:
    path = repo_root / NEGATIVE_FIXTURE_MANIFEST_PATH
    data, error = read_json(path)
    if error is not None or not isinstance(data, dict):
        add_issue(
            issues,
            "FAIL",
            "NEGATIVE_FIXTURE_MANIFEST_PARSE_FAIL",
            "Negative fixture manifest is missing or invalid JSON.",
            path,
            {"error": error or "root is not object"},
        )
        return []

    fixtures = data.get("fixtures")
    if not isinstance(fixtures, list) or not fixtures:
        add_issue(
            issues,
            "FAIL",
            "NEGATIVE_FIXTURE_MANIFEST_EMPTY",
            "Negative fixture manifest has no fixtures list.",
            path,
        )
        return []

    minimum = data.get("minimum_negative_fixtures")
    if isinstance(minimum, int) and len(fixtures) < minimum:
        add_issue(
            issues,
            "FAIL",
            "NEGATIVE_FIXTURE_COUNT_BELOW_MINIMUM",
            "Negative fixture count is below declared manifest minimum.",
            path,
            {"minimum": minimum, "actual": len(fixtures)},
        )

    normalized: list[dict[str, Any]] = []
    for index, entry in enumerate(fixtures):
        if not isinstance(entry, dict):
            add_issue(
                issues,
                "FAIL",
                "NEGATIVE_FIXTURE_MANIFEST_ENTRY_NOT_OBJECT",
                "Negative fixture manifest entry must be an object.",
                path,
                {"index": index},
            )
            continue
        fixture_relpath = entry.get("fixture_relpath")
        fixture_type = entry.get("fixture_type")
        expected_issue_code = entry.get("expected_issue_code")
        title = entry.get("title")
        if not all(isinstance(value, str) and value.strip() for value in [fixture_relpath, fixture_type, expected_issue_code, title]):
            add_issue(
                issues,
                "FAIL",
                "NEGATIVE_FIXTURE_MANIFEST_ENTRY_INVALID",
                "Manifest entry is missing required string fields.",
                path,
                {"index": index},
            )
            continue
        normalized.append(entry)

    return normalized


def validate_claim_ledger_template(
    repo_root: Path,
    issues: list[Issue],
    claim_ledger_schema: dict[str, Any] | None,
) -> None:
    template_path = repo_root / "IMPERIUM_NEW_GENERATION/MATRIX_SPINE/TEMPLATES/CLAIM_LEDGER_TEMPLATE.jsonl"
    if not template_path.exists():
        add_issue(
            issues,
            "FAIL",
            "CLAIM_LEDGER_TEMPLATE_MISSING",
            "Claim ledger template file is missing.",
            template_path,
        )
        return

    raw_lines = template_path.read_text(encoding="utf-8").splitlines()
    lines = [line for line in raw_lines if line.strip()]
    if not lines:
        add_issue(
            issues,
            "FAIL",
            "CLAIM_LEDGER_TEMPLATE_EMPTY",
            "Claim ledger template has no JSONL entries.",
            template_path,
        )
        return

    required_fields: list[str] = []
    if claim_ledger_schema is not None and isinstance(claim_ledger_schema.get("required"), list):
        required_fields = [str(item) for item in claim_ledger_schema["required"]]

    for idx, line in enumerate(lines, start=1):
        try:
            entry = json.loads(line)
        except json.JSONDecodeError as exc:
            add_issue(
                issues,
                "FAIL",
                "CLAIM_LEDGER_TEMPLATE_JSONL_PARSE_FAIL",
                "Claim ledger template line is not valid JSON.",
                template_path,
                {"line": idx, "error": str(exc)},
            )
            continue

        if not isinstance(entry, dict):
            add_issue(
                issues,
                "FAIL",
                "CLAIM_LEDGER_TEMPLATE_LINE_NOT_OBJECT",
                "Claim ledger template line must be a JSON object.",
                template_path,
                {"line": idx},
            )
            continue

        if required_fields:
            missing = [key for key in required_fields if key not in entry]
            if missing:
                add_issue(
                    issues,
                    "FAIL",
                    "CLAIM_LEDGER_TEMPLATE_REQUIRED_KEYS_MISSING",
                    "Claim ledger template line is missing required schema keys.",
                    template_path,
                    {"line": idx, "missing": missing},
                )


def collect_matrix_files(repo_root: Path) -> list[Path]:
    matrix_root = repo_root / "IMPERIUM_NEW_GENERATION"
    return sorted(matrix_root.glob("**/MATRICES/*.json"))


def load_matrix_index_owner_map(repo_root: Path, issues: list[Issue]) -> dict[str, str]:
    index_path = repo_root / "IMPERIUM_NEW_GENERATION/MATRIX_SPINE/INDEX/MATRIX_SPINE_INDEX.json"
    data, error = read_json(index_path)
    if error is not None or not isinstance(data, dict):
        add_issue(
            issues,
            "FAIL",
            "MATRIX_INDEX_PARSE_FAIL",
            "Matrix spine index JSON cannot be parsed.",
            index_path,
            {"error": error or "root is not object"},
        )
        return {}

    matrices = data.get("matrices")
    if not isinstance(matrices, list):
        add_issue(
            issues,
            "FAIL",
            "MATRIX_INDEX_BAD_MATRICES_LIST",
            "Matrix spine index has invalid 'matrices' list.",
            index_path,
        )
        return {}

    mapping: dict[str, str] = {}
    for entry in matrices:
        if not isinstance(entry, dict):
            continue
        matrix_id = entry.get("matrix_id")
        owner_organ = entry.get("owner_organ")
        repo_json = entry.get("repo_json")
        if isinstance(matrix_id, str) and isinstance(owner_organ, str):
            mapping[matrix_id] = owner_organ
        if isinstance(repo_json, str):
            target = repo_root / repo_json
            if not target.exists():
                add_issue(
                    issues,
                    "FAIL",
                    "MATRIX_INDEX_REFERENCED_FILE_MISSING",
                    "Matrix spine index references missing repo_json file.",
                    target,
                    {"matrix_id": matrix_id},
                )
    return mapping


def run_negative_fixtures(
    repo_root: Path,
    matrix_schema: dict[str, Any] | None,
    red_team_schema: dict[str, Any] | None,
    allowed_status_vocab: set[str],
    matrix_index_owner_map: dict[str, str],
) -> tuple[list[dict[str, Any]], list[Issue]]:
    results: list[dict[str, Any]] = []
    issues: list[Issue] = []

    manifest_entries = load_negative_fixture_manifest(repo_root, issues)
    if not manifest_entries:
        return results, issues

    supported_fixture_types = {
        "matrix_payload",
        "matrix_not_indexed",
        "red_team_schema",
        "malformed_json",
        "stale_receipt",
        "closure_receipt",
        "capability_split",
        "runtime_output",
        "owner_language_contract",
    }

    for entry in manifest_entries:
        fixture_relpath = str(entry["fixture_relpath"])
        fixture_type = str(entry["fixture_type"])
        expected_code = str(entry["expected_issue_code"])
        title = str(entry["title"])
        fixture_id = str(entry.get("fixture_id", "UNSPECIFIED"))

        path = repo_root / fixture_relpath
        local_issues: list[Issue] = []

        if fixture_type not in supported_fixture_types:
            add_issue(
                issues,
                "FAIL",
                "NEGATIVE_FIXTURE_TYPE_UNKNOWN",
                "Negative fixture manifest contains unsupported fixture_type.",
                path,
                {"fixture_type": fixture_type},
            )
            results.append(
                {
                    "fixture_id": fixture_id,
                    "fixture_type": fixture_type,
                    "fixture": str(path),
                    "title": title,
                    "expected_issue_code": expected_code,
                    "detected": False,
                    "detected_codes": [],
                }
            )
            continue

        if fixture_type == "malformed_json":
            _, error = read_json(path)
            if error is not None:
                add_issue(
                    local_issues,
                    "FAIL",
                    "NEGATIVE_FIXTURE_PARSE_FAIL",
                    "Malformed JSON fixture failed to parse as expected.",
                    path,
                    {"error": error},
                )
            else:
                add_issue(
                    local_issues,
                    "FAIL",
                    "NEGATIVE_FIXTURE_EXPECTED_MALFORMED",
                    "Fixture declared malformed_json but parsed successfully.",
                    path,
                )
        else:
            data, error = read_json(path)
            if error is not None or not isinstance(data, dict):
                add_issue(
                    local_issues,
                    "FAIL",
                    "NEGATIVE_FIXTURE_PARSE_FAIL",
                    "Negative fixture cannot be parsed into JSON object.",
                    path,
                    {"error": error},
                )
            else:
                if fixture_type == "matrix_payload":
                    validate_matrix_payload(data, path, local_issues, allowed_status_vocab)
                    if matrix_schema is not None:
                        validate_schema_object(
                            data=data,
                            schema=matrix_schema,
                            context="MATRIX_SCHEMA",
                            issues=local_issues,
                            path=path,
                        )
                elif fixture_type == "matrix_not_indexed":
                    validate_matrix_payload(data, path, local_issues, allowed_status_vocab)
                    if matrix_schema is not None:
                        validate_schema_object(
                            data=data,
                            schema=matrix_schema,
                            context="MATRIX_SCHEMA",
                            issues=local_issues,
                            path=path,
                        )
                    validate_matrix_index_membership(
                        data.get("matrix_id"),
                        path,
                        matrix_index_owner_map,
                        local_issues,
                    )
                elif fixture_type == "red_team_schema":
                    if red_team_schema is not None:
                        validate_schema_object(
                            data=data,
                            schema=red_team_schema,
                            context="RED_TEAM_SCHEMA",
                            issues=local_issues,
                            path=path,
                        )
                elif fixture_type == "stale_receipt":
                    validate_stale_receipt_payload(data, path, local_issues)
                elif fixture_type == "closure_receipt":
                    validate_closure_receipt_payload(data, path, local_issues)
                elif fixture_type == "capability_split":
                    validate_capability_split_payload(data, path, local_issues)
                elif fixture_type == "runtime_output":
                    validate_runtime_output_payload(data, path, local_issues)
                elif fixture_type == "owner_language_contract":
                    validate_owner_language_contract_payload(data, path, local_issues)

        detected_codes = [issue.code for issue in local_issues]
        detected = expected_code in detected_codes
        if not detected:
            add_issue(
                issues,
                "FAIL",
                "NEGATIVE_FIXTURE_NOT_CAUGHT",
                "Negative fixture did not trigger expected failure code.",
                path,
                {
                    "fixture_id": fixture_id,
                    "expected_issue_code": expected_code,
                    "detected_codes": detected_codes,
                },
            )

        results.append(
            {
                "fixture_id": fixture_id,
                "fixture_type": fixture_type,
                "fixture": str(path),
                "title": title,
                "expected_issue_code": expected_code,
                "detected": detected,
                "detected_codes": detected_codes,
            }
        )

    return results, issues


def build_report_markdown(
    *,
    task_id: str,
    timestamp: str,
    matrix_count: int,
    parse_failures: int,
    fail_count: int,
    warn_count: int,
    info_count: int,
    verdict: str,
    issues: list[Issue],
    negative_fixture_results: list[dict[str, Any]],
) -> str:
    lines: list[str] = []
    lines.append(f"# Matrix Spine Validation Report — {task_id}")
    lines.append("")
    lines.append(f"Timestamp (UTC): {timestamp}")
    lines.append("")
    lines.append("## Summary")
    lines.append(f"- Matrix files scanned: {matrix_count}")
    lines.append(f"- Matrix parse failures: {parse_failures}")
    lines.append(f"- FAIL: {fail_count}")
    lines.append(f"- WARN: {warn_count}")
    lines.append(f"- INFO: {info_count}")
    lines.append(f"- Negative fixtures checked: {len(negative_fixture_results)}")
    lines.append(f"- Verdict: {verdict}")
    lines.append("")

    lines.append("## Negative Fixture Evidence")
    for item in negative_fixture_results:
        lines.append(
            "- "
            + f"{item['title']}: expected `{item['expected_issue_code']}` -> "
            + ("detected" if item["detected"] else "NOT detected")
        )
    lines.append("")

    lines.append("## Findings")
    if not issues:
        lines.append("- No findings.")
    else:
        for issue in issues:
            path_part = f" ({issue.path})" if issue.path else ""
            lines.append(f"- [{issue.severity}] {issue.code}: {issue.message}{path_part}")
    lines.append("")

    lines.append("## Replay")
    lines.append("- `bash IMPERIUM_NEW_GENERATION/MATRIX_SPINE/VALIDATORS/run_matrix_spine_validation.sh`")
    lines.append("- `pwsh IMPERIUM_NEW_GENERATION/MATRIX_SPINE/VALIDATORS/run_matrix_spine_validation.ps1`")
    lines.append("")

    return "\n".join(lines) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate IMPERIUM Matrix Spine artifacts.")
    parser.add_argument("--task-id", default=TASK_ID_DEFAULT)
    parser.add_argument("--repo-root", default="")
    parser.add_argument("--output-dir", default="")
    parser.add_argument("--skip-negative-fixtures", action="store_true")
    args = parser.parse_args()

    script_path = Path(__file__).resolve()
    default_repo_root = script_path.parents[3]
    repo_root = Path(args.repo_root).resolve() if args.repo_root else default_repo_root

    if args.output_dir:
        output_dir = Path(args.output_dir).resolve()
    else:
        output_dir = (
            repo_root
            / "IMPERIUM_NEW_GENERATION/MATRIX_SPINE/REPORTS"
            / TASK_ID_DEFAULT
        )
    output_dir.mkdir(parents=True, exist_ok=True)

    issues: list[Issue] = []

    matrix_schema = validate_schema_file(
        repo_root,
        "IMPERIUM_NEW_GENERATION/MATRIX_SPINE/SCHEMAS/matrix_definition_schema.json",
        issues,
        "MATRIX_SCHEMA",
    )
    claim_ledger_schema = validate_schema_file(
        repo_root,
        "IMPERIUM_NEW_GENERATION/MATRIX_SPINE/SCHEMAS/claim_ledger_schema.json",
        issues,
        "CLAIM_LEDGER_SCHEMA",
    )
    validate_schema_file(
        repo_root,
        "IMPERIUM_NEW_GENERATION/MATRIX_SPINE/SCHEMAS/capability_split_receipt_schema.json",
        issues,
        "CAPABILITY_SPLIT_SCHEMA",
    )
    red_team_schema = validate_schema_file(
        repo_root,
        "IMPERIUM_NEW_GENERATION/MATRIX_SPINE/SCHEMAS/red_team_verdict_schema.json",
        issues,
        "RED_TEAM_SCHEMA",
    )
    validate_schema_file(
        repo_root,
        "IMPERIUM_NEW_GENERATION/MATRIX_SPINE/SCHEMAS/efficiency_delta_receipt_schema.json",
        issues,
        "EFFICIENCY_DELTA_SCHEMA",
    )
    allowed_status_vocab = load_status_policy(repo_root, issues, matrix_schema)

    validate_required_validator_files(repo_root, issues)
    validate_read_first_packets(repo_root, issues)
    validate_agents_bootloader(repo_root, issues)
    validate_claim_ledger_template(repo_root, issues, claim_ledger_schema)

    matrix_index_owner_map = load_matrix_index_owner_map(repo_root, issues)
    matrix_files = collect_matrix_files(repo_root)

    matrix_parse_failures = 0
    for matrix_path in matrix_files:
        data, error = read_json(matrix_path)
        if error is not None or not isinstance(data, dict):
            matrix_parse_failures += 1
            add_issue(
                issues,
                "FAIL",
                "MATRIX_JSON_PARSE_FAIL",
                "Matrix JSON could not be parsed as object.",
                matrix_path,
                {"error": error},
            )
            continue

        validate_matrix_payload(data, matrix_path, issues, allowed_status_vocab)
        if matrix_schema is not None:
            validate_schema_object(
                data=data,
                schema=matrix_schema,
                context="MATRIX_SCHEMA",
                issues=issues,
                path=matrix_path,
            )

        matrix_id = data.get("matrix_id")
        validate_matrix_index_membership(matrix_id, matrix_path, matrix_index_owner_map, issues)
        expected_owner = matrix_index_owner_map.get(matrix_id)
        if isinstance(expected_owner, str) and data.get("owner_organ") != expected_owner:
            add_issue(
                issues,
                "FAIL",
                "MATRIX_OWNER_MISMATCH_INDEX",
                "owner_organ differs from MATRIX_SPINE_INDEX.json mapping.",
                matrix_path,
                {
                    "matrix_id": matrix_id,
                    "expected_owner": expected_owner,
                    "actual_owner": data.get("owner_organ"),
                },
            )

    negative_fixture_results: list[dict[str, Any]] = []
    if args.skip_negative_fixtures:
        add_issue(
            issues,
            "WARN",
            "NEGATIVE_FIXTURES_SKIPPED",
            "Negative fixture checks were skipped by CLI flag.",
        )
    else:
        negative_fixture_results, negative_issues = run_negative_fixtures(
            repo_root,
            matrix_schema,
            red_team_schema,
            allowed_status_vocab,
            matrix_index_owner_map,
        )
        issues.extend(negative_issues)

    fail_count = sum(1 for issue in issues if issue.severity == "FAIL")
    warn_count = sum(1 for issue in issues if issue.severity == "WARN")
    info_count = sum(1 for issue in issues if issue.severity == "INFO")

    if fail_count:
        verdict = "BLOCK"
    elif warn_count:
        verdict = "PASS_WITH_WARNINGS"
    else:
        verdict = "PASS"

    timestamp = utc_now()
    summary = {
        "task_id": args.task_id,
        "timestamp_utc": timestamp,
        "repo_root": str(repo_root),
        "matrix_files_scanned": len(matrix_files),
        "matrix_parse_failures": matrix_parse_failures,
        "issue_counts": {
            "FAIL": fail_count,
            "WARN": warn_count,
            "INFO": info_count,
        },
        "verdict": verdict,
        "allowed_status_vocab": sorted(allowed_status_vocab),
        "negative_fixture_results": negative_fixture_results,
    }

    summary_path = output_dir / "matrix_spine_validation_summary.json"
    failures_path = output_dir / "matrix_spine_validation_failures.jsonl"
    report_path = output_dir / "matrix_spine_validation_report.md"
    receipt_path = output_dir / "matrix_spine_validation_receipt.json"

    summary_path.write_text(json.dumps(summary, ensure_ascii=True, indent=2) + "\n", encoding="utf-8")

    with failures_path.open("w", encoding="utf-8") as handle:
        for issue in issues:
            if issue.severity in {"FAIL", "WARN"}:
                handle.write(json.dumps(issue.to_json(), ensure_ascii=True) + "\n")

    receipt = {
        "task_id": args.task_id,
        "timestamp_utc": timestamp,
        "checker": "validate_matrix_spine.py",
        "output_dir": str(output_dir),
        "replay_command_sh": "bash IMPERIUM_NEW_GENERATION/MATRIX_SPINE/VALIDATORS/run_matrix_spine_validation.sh",
        "replay_command_ps1": "pwsh IMPERIUM_NEW_GENERATION/MATRIX_SPINE/VALIDATORS/run_matrix_spine_validation.ps1",
        "summary_path": str(summary_path),
        "report_path": str(report_path),
        "failures_path": str(failures_path),
        "verdict": verdict,
        "issue_counts": summary["issue_counts"],
    }
    receipt_path.write_text(json.dumps(receipt, ensure_ascii=True, indent=2) + "\n", encoding="utf-8")

    report_text = build_report_markdown(
        task_id=args.task_id,
        timestamp=timestamp,
        matrix_count=len(matrix_files),
        parse_failures=matrix_parse_failures,
        fail_count=fail_count,
        warn_count=warn_count,
        info_count=info_count,
        verdict=verdict,
        issues=issues,
        negative_fixture_results=negative_fixture_results,
    )
    report_path.write_text(report_text, encoding="utf-8")

    print(f"[matrix-spine-validator] output_dir={output_dir}")
    print(
        "[matrix-spine-validator] "
        + f"verdict={verdict} fail={fail_count} warn={warn_count} info={info_count}"
    )

    return 1 if verdict == "BLOCK" else 0


if __name__ == "__main__":
    sys.exit(main())
