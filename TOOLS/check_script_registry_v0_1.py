#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

REQUIRED_TOP = ["schema_version", "updated_at_utc", "generated_by", "scripts"]
REQUIRED_ENTRY = [
    "script_id",
    "path",
    "name",
    "owner_organ",
    "purpose",
    "platform",
    "runtime",
    "entrypoint_command",
    "required_args",
    "optional_args",
    "reads",
    "writes",
    "side_effects",
    "produces_receipts",
    "receipt_paths",
    "modifies_repo",
    "commit_push_capable",
    "vm2_sync_capable",
    "requires_owner_approval",
    "safe_for_servitor",
    "dangerous_if_misused",
    "known_dependencies",
    "expected_exit_codes",
    "example_safe_invocation",
    "verification_command",
    "last_verified_at",
    "status",
]

DANGEROUS_EFFECTS = {"DESTRUCTIVE", "COMMITS", "PUSHES", "SYNCS_VM2", "OWNER_ONLY", "BLOCKED"}


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def add_unique(items: list[str], value: str) -> None:
    if value not in items:
        items.append(value)


def run_check(repo_root: Path, registry_rel: str) -> dict[str, Any]:
    blockers: list[str] = []
    warnings: list[str] = []

    registry_path = (repo_root / registry_rel).resolve()
    if not registry_path.exists():
        return {
            "schema_version": "imperium.script_registry_check.v0_1",
            "registry_path": str(registry_path),
            "verdict": "BLOCKED",
            "blockers": ["missing_registry_file"],
            "warnings": [],
            "counts": {"entries": 0, "blockers": 1, "warnings": 0},
        }

    try:
        payload = load_json(registry_path)
    except Exception as exc:
        return {
            "schema_version": "imperium.script_registry_check.v0_1",
            "registry_path": str(registry_path),
            "verdict": "BLOCKED",
            "blockers": [f"invalid_json:{type(exc).__name__}"],
            "warnings": [],
            "counts": {"entries": 0, "blockers": 1, "warnings": 0},
        }

    if not isinstance(payload, dict):
        add_unique(blockers, "registry_root_not_object")

    for key in REQUIRED_TOP:
        if key not in payload:
            add_unique(blockers, f"missing_top_field:{key}")

    scripts = payload.get("scripts")
    if not isinstance(scripts, list):
        add_unique(blockers, "scripts_not_list")
        scripts = []

    for idx, item in enumerate(scripts):
        tag = f"entry[{idx}]"
        if not isinstance(item, dict):
            add_unique(blockers, f"{tag}:not_object")
            continue

        for key in REQUIRED_ENTRY:
            if key not in item:
                add_unique(blockers, f"{tag}:missing_field:{key}")

        status = str(item.get("status", ""))
        path_value = str(item.get("path", ""))
        path_exists = (repo_root / path_value).exists() if path_value and path_value != "UNKNOWN" else False

        if status in {"REGISTERED", "VERIFIED"} and not path_exists:
            add_unique(blockers, f"{tag}:path_missing_for_status:{path_value}")

        effects = item.get("side_effects")
        if isinstance(effects, list):
            dangerous_effect = any(str(e) in DANGEROUS_EFFECTS for e in effects)
            if dangerous_effect and not bool(item.get("requires_owner_approval", False)):
                add_unique(blockers, f"{tag}:dangerous_without_owner_approval")
        else:
            add_unique(blockers, f"{tag}:side_effects_not_list")

        if bool(item.get("commit_push_capable", False)) or bool(item.get("vm2_sync_capable", False)):
            if bool(item.get("safe_for_servitor", False)) and not bool(item.get("requires_owner_approval", False)):
                add_unique(blockers, f"{tag}:commit_or_sync_marked_safe_without_owner_gate")

        if bool(item.get("modifies_repo", False)) and not bool(item.get("dangerous_if_misused", False)):
            add_unique(warnings, f"{tag}:modifies_repo_but_dangerous_if_misused_false")

    verdict = "PASS"
    if blockers:
        verdict = "BLOCKED"
    elif warnings:
        verdict = "PASS_WITH_WARNINGS"

    return {
        "schema_version": "imperium.script_registry_check.v0_1",
        "registry_path": str(registry_path),
        "verdict": verdict,
        "blockers": blockers,
        "warnings": warnings,
        "counts": {
            "entries": len(scripts),
            "blockers": len(blockers),
            "warnings": len(warnings),
        },
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Check SCRIPTORIUM script registry v0.1")
    parser.add_argument("--repo-root", default=".", help="Repository root")
    parser.add_argument(
        "--registry",
        default="REGISTRY/SCRIPT_REGISTRY.json",
        help="Path to script registry relative to repo root",
    )
    parser.add_argument("--human", action="store_true", help="Print human-readable summary")
    return parser.parse_args()


def print_human(report: dict[str, Any]) -> None:
    print("=== IMPERIUM SCRIPTORIUM REGISTRY CHECK ===")
    print(f"registry: {report['registry_path']}")
    print(f"verdict: {report['verdict']}")
    print(f"entries: {report['counts']['entries']}")
    print(f"blockers: {report['counts']['blockers']}")
    print(f"warnings: {report['counts']['warnings']}")


def main() -> int:
    args = parse_args()
    repo_root = Path(args.repo_root).resolve()
    report = run_check(repo_root, args.registry)
    if args.human:
        print_human(report)
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0 if not report["blockers"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
