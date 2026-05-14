#!/usr/bin/env python3
"""Administratum Address Book Checker v0.1."""

from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


REQUIRED_ZONE_IDS = {
    "pc_git_repo",
    "local_context_root",
    "private_context_root",
    "handoff_root",
    "task_bundles_root",
    "github_exact_tree_url",
    "vm2_repo_root",
    "vm2_status",
}

ENTRY_REQUIRED_FIELDS = [
    "zone_id",
    "path_or_url",
    "scope",
    "privacy_class",
    "agent_access_rule",
    "git_tracked_expected",
    "description",
    "verification_method",
    "last_verified_utc",
]

GITHUB_TREE_PATTERN = re.compile(r"^https://github\.com/.+/tree/[0-9a-f]{40}$")


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def validate_schema_contract(address_book: dict[str, Any], schema: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    schema_required = schema.get("required", [])
    for key in schema_required:
        if key not in address_book:
            errors.append(f"Top-level required key missing: {key}")

    entry_schema_required = (
        schema.get("$defs", {})
        .get("address_entry", {})
        .get("required", [])
    )
    entries = address_book.get("addresses")
    if not isinstance(entries, list):
        errors.append("addresses must be a list")
        return errors

    for idx, entry in enumerate(entries):
        if not isinstance(entry, dict):
            errors.append(f"addresses[{idx}] must be an object")
            continue
        for key in entry_schema_required:
            if key not in entry:
                errors.append(f"addresses[{idx}] missing required key: {key}")
    return errors


def path_inside_repo(candidate: str, repo_root: Path) -> bool:
    candidate_path = Path(candidate.replace("\\", "/"))
    if not candidate_path.is_absolute():
        return False
    try:
        resolved_candidate = Path(str(candidate_path)).resolve(strict=False)
        resolved_repo = repo_root.resolve(strict=False)
        resolved_candidate.relative_to(resolved_repo)
        return True
    except Exception:
        return False


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--address-book",
        default="ORGANS/ADMINISTRATUM/ADDRESS_BOOK/imperium_address_book_v0_1.json",
    )
    parser.add_argument(
        "--schema",
        default="schemas/administratum_address_book.schema.json",
    )
    parser.add_argument(
        "--report",
        default="ORGANS/ADMINISTRATUM/REPORTS/address_book_check_report_v0_1.json",
    )
    args = parser.parse_args()

    repo_root = Path(__file__).resolve().parents[1]
    address_book_path = repo_root / args.address_book
    schema_path = repo_root / args.schema
    report_path = repo_root / args.report
    report_path.parent.mkdir(parents=True, exist_ok=True)

    checks: dict[str, bool] = {}
    failures: list[str] = []

    try:
        address_book = load_json(address_book_path)
        schema = load_json(schema_path)
    except Exception as exc:
        payload = {
            "status": "FAIL",
            "checked_utc": utc_now(),
            "error": f"Failed to load input JSON: {exc}",
            "address_book_path": str(address_book_path),
            "schema_path": str(schema_path),
        }
        report_path.write_text(json.dumps(payload, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")
        print(json.dumps(payload, ensure_ascii=True))
        return 2

    schema_errors = validate_schema_contract(address_book, schema)
    checks["schema_contract_valid"] = not schema_errors
    failures.extend(schema_errors)

    entries = address_book.get("addresses", [])
    zone_map = {entry.get("zone_id"): entry for entry in entries if isinstance(entry, dict)}

    missing_zone_ids = sorted(REQUIRED_ZONE_IDS - set(zone_map.keys()))
    checks["required_entries_present"] = not missing_zone_ids
    if missing_zone_ids:
        failures.append(f"Missing required zone_id entries: {', '.join(missing_zone_ids)}")

    field_failures: list[str] = []
    for zone_id in REQUIRED_ZONE_IDS & set(zone_map.keys()):
        entry = zone_map[zone_id]
        for key in ENTRY_REQUIRED_FIELDS:
            if key not in entry or entry[key] in ("", None):
                field_failures.append(f"{zone_id}: missing/empty field '{key}'")
    checks["required_entry_fields_present"] = not field_failures
    failures.extend(field_failures)

    local_entry = zone_map.get("local_context_root", {})
    private_entry = zone_map.get("private_context_root", {})
    local_inside_repo = path_inside_repo(str(local_entry.get("path_or_url", "")), repo_root)
    private_inside_repo = path_inside_repo(str(private_entry.get("path_or_url", "")), repo_root)
    checks["local_private_outside_repo"] = not local_inside_repo and not private_inside_repo
    if local_inside_repo or private_inside_repo:
        failures.append("local/private context path must not be inside E:\\IMPERIUM")

    private_rule_ok = (
        private_entry.get("privacy_class") == "private_index_only"
        and "index" in str(private_entry.get("agent_access_rule", "")).lower()
    )
    checks["private_context_redacted_index_only"] = private_rule_ok
    if not private_rule_ok:
        failures.append("private_context_root must be redacted/index-only")

    github_entry = zone_map.get("github_exact_tree_url", {})
    github_url = str(github_entry.get("path_or_url", ""))
    github_url_ok = bool(GITHUB_TREE_PATTERN.match(github_url)) and "/tree/master" not in github_url and "/tree/main" not in github_url
    checks["exact_tree_url_present"] = github_url_ok
    if not github_url_ok:
        failures.append("github_exact_tree_url must be exact /tree/<40-hex> URL and not floating master/main")

    usage_policy = address_book.get("usage_policy", {})
    policy_ok = all(
        isinstance(usage_policy.get(key), str) and usage_policy.get(key).strip()
        for key in [
            "default_agent_workspace",
            "local_context_rule",
            "private_context_rule",
            "external_bundle_rule",
        ]
    )
    checks["usage_policy_explicit"] = policy_ok
    if not policy_ok:
        failures.append("usage_policy is incomplete")

    status = "PASS" if all(checks.values()) else "FAIL"
    payload = {
        "schema_version": "administratum_address_book_check_report_v0_1",
        "status": status,
        "checked_utc": utc_now(),
        "address_book_path": str(address_book_path.relative_to(repo_root)).replace("\\", "/"),
        "schema_path": str(schema_path.relative_to(repo_root)).replace("\\", "/"),
        "checks": checks,
        "failures": failures,
        "required_zone_ids": sorted(REQUIRED_ZONE_IDS),
    }
    report_path.write_text(json.dumps(payload, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")
    print(json.dumps(payload, ensure_ascii=True))
    return 0 if status == "PASS" else 1


if __name__ == "__main__":
    sys.exit(main())
