#!/usr/bin/env python3
"""Validate Officio Agentis foundation artifacts for MVP v0.1."""

from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


TASK_ID = "TASK-20260515-BUILD-OFFICIO-AGENTIS-MVP-V0_1"
ROLE_IDS = {"SERVITOR", "LOGOS_PRIME", "LOGOS_SPECULUM", "ADVISOR_SERVITOR"}
REQUIRED_FOLDERS = [
    "ORGANS/OFFICIO_AGENTIS/DOCS",
    "ORGANS/OFFICIO_AGENTIS/POLICIES",
    "ORGANS/OFFICIO_AGENTIS/ROLE_CONTRACTS",
    "ORGANS/OFFICIO_AGENTIS/MODES",
    "ORGANS/OFFICIO_AGENTIS/RESPONSE_CONTRACTS",
    "ORGANS/OFFICIO_AGENTIS/PROMPTS",
    "ORGANS/OFFICIO_AGENTIS/TESTS",
    "ORGANS/OFFICIO_AGENTIS/REPORTS",
    "ORGANS/OFFICIO_AGENTIS/REGISTRY/TASKS/TASK-20260515-BUILD-OFFICIO-AGENTIS-MVP-V0_1/PROMPTS",
    "ORGANS/OFFICIO_AGENTIS/REGISTRY/TASKS/TASK-20260515-BUILD-OFFICIO-AGENTIS-MVP-V0_1/STAGE_REPORTS",
    "ORGANS/OFFICIO_AGENTIS/SCHEMAS",
]
README_REQUIRED_MARKERS = [
    "purpose",
    "what officio agentis owns",
    "what officio agentis must not own",
    "servitor",
    "logos_prime",
    "logos_speculum",
    "advisor_servitor",
    "canonical machine-readable artifacts are english-only",
    "no pass without evidence",
]
NON_OWNERSHIP_MARKERS = [
    "astronomicon",
    "administratum",
    "doctrinarium",
    "mechanicus",
    "inquisition",
    "sanctum",
    "scriptorium",
    "arsenal",
]
REQUIRED_SCHEMA_PATHS = {
    "ORGANS/OFFICIO_AGENTIS/SCHEMAS/agent_role_contract.schema.json",
    "ORGANS/OFFICIO_AGENTIS/SCHEMAS/agent_mode.schema.json",
    "ORGANS/OFFICIO_AGENTIS/SCHEMAS/agent_settings.schema.json",
}


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def to_rel(repo_root: Path, path: Path) -> str:
    return str(path.relative_to(repo_root)).replace("\\", "/")


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> int:
    repo_root = Path(__file__).resolve().parents[1]
    readme_path = repo_root / "ORGANS/OFFICIO_AGENTIS/README.md"
    role_registry_path = repo_root / "ORGANS/OFFICIO_AGENTIS/REGISTRY/ROLE_REGISTRY.json"
    schema_registry_path = repo_root / "ORGANS/OFFICIO_AGENTIS/REGISTRY/SCHEMA_REGISTRY.json"
    report_path = repo_root / "ORGANS/OFFICIO_AGENTIS/REPORTS/foundation_check_report_v0_1.json"

    checks: dict[str, bool] = {}
    failures: list[str] = []

    checks["required_folders_exist"] = all((repo_root / folder).is_dir() for folder in REQUIRED_FOLDERS)
    if not checks["required_folders_exist"]:
        for folder in REQUIRED_FOLDERS:
            if not (repo_root / folder).is_dir():
                failures.append(f"Missing required folder: {folder}")

    if readme_path.exists():
        readme_text = readme_path.read_text(encoding="utf-8").lower()
    else:
        readme_text = ""
    checks["readme_exists"] = readme_path.exists()
    if not checks["readme_exists"]:
        failures.append("Missing README.md")

    checks["readme_markers_present"] = all(marker in readme_text for marker in README_REQUIRED_MARKERS)
    if not checks["readme_markers_present"]:
        for marker in README_REQUIRED_MARKERS:
            if marker not in readme_text:
                failures.append(f"README marker missing: {marker}")

    checks["non_ownership_markers_present"] = all(marker in readme_text for marker in NON_OWNERSHIP_MARKERS)
    if not checks["non_ownership_markers_present"]:
        for marker in NON_OWNERSHIP_MARKERS:
            if marker not in readme_text:
                failures.append(f"README non-ownership marker missing: {marker}")

    schema_parse_ok = True
    for schema_path in REQUIRED_SCHEMA_PATHS:
        path = repo_root / schema_path
        if not path.exists():
            failures.append(f"Missing schema file: {schema_path}")
            schema_parse_ok = False
            continue
        try:
            load_json(path)
        except Exception as exc:
            failures.append(f"Invalid schema JSON: {schema_path} ({exc})")
            schema_parse_ok = False
    checks["base_schema_json_valid"] = schema_parse_ok

    role_registry_ok = False
    roles_draft_ok = False
    try:
        registry = load_json(role_registry_path)
        roles = registry.get("roles", [])
        role_ids = {entry.get("role_id") for entry in roles if isinstance(entry, dict)}
        statuses = {entry.get("role_id"): entry.get("status") for entry in roles if isinstance(entry, dict)}
        role_registry_ok = role_ids == ROLE_IDS
        roles_draft_ok = all(statuses.get(role_id) == "DRAFT" for role_id in ROLE_IDS)
        if not role_registry_ok:
            failures.append("ROLE_REGISTRY.json role set mismatch")
        if not roles_draft_ok:
            failures.append("ROLE_REGISTRY.json role status must be DRAFT for all required roles")
    except Exception as exc:
        failures.append(f"Failed to parse ROLE_REGISTRY.json: {exc}")
    checks["role_registry_has_exact_roles"] = role_registry_ok
    checks["role_registry_roles_are_draft"] = roles_draft_ok

    schema_registry_ok = False
    try:
        schema_registry = load_json(schema_registry_path)
        registered_paths = {
            entry.get("path")
            for entry in schema_registry.get("schemas", [])
            if isinstance(entry, dict)
        }
        schema_registry_ok = REQUIRED_SCHEMA_PATHS.issubset(registered_paths)
        if not schema_registry_ok:
            failures.append("SCHEMA_REGISTRY.json does not include required base schema paths")
    except Exception as exc:
        failures.append(f"Failed to parse SCHEMA_REGISTRY.json: {exc}")
    checks["schema_registry_lists_base_schemas"] = schema_registry_ok

    status = "PASS" if all(checks.values()) else "FAIL"
    payload = {
        "schema_version": "officio_foundation_check_report_v0_1",
        "task_id": TASK_ID,
        "status": status,
        "checked_utc": utc_now(),
        "checks": checks,
        "failures": failures,
        "evidence_paths": [
            to_rel(repo_root, readme_path),
            to_rel(repo_root, role_registry_path),
            to_rel(repo_root, schema_registry_path),
            "ORGANS/OFFICIO_AGENTIS/SCHEMAS/agent_role_contract.schema.json",
            "ORGANS/OFFICIO_AGENTIS/SCHEMAS/agent_mode.schema.json",
            "ORGANS/OFFICIO_AGENTIS/SCHEMAS/agent_settings.schema.json"
        ]
    }
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(json.dumps(payload, ensure_ascii=True, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(payload, ensure_ascii=True))
    return 0 if status == "PASS" else 1


if __name__ == "__main__":
    sys.exit(main())
