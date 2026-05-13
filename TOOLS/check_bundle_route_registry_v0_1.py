#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

TASK_ID = "TASK-20260513-STEP7_1F-STEP7_2-BUNDLE-ROUTE-ASSET-REGISTRATION-SANCTUM-V0_4"

REGISTRY_REL = "REGISTRY/BUNDLE_ROUTE_REGISTRY.json"
POLICY_DOC_REL = "DOCS/BUNDLE_ROUTE_POLICY_V0_1.md"
SCHEMA_REL = "schemas/bundle_route_registry_v0_1.schema.json"
SANCTUM_STATE_BUILDER_REL = "TOOLS/build_sanctum_state_v0_1.py"

EXPECTED_CANONICAL_VM2 = "/home/vboxuser2/IMPERIUM_WORK/VM2_BUNDLES/"
EXPECTED_PC_INBOX = "E:\\IMPERIUM\\INBOX\\VM2_BUNDLES\\"
EXPECTED_LEGACY = {
    "/home/vboxuser2/IMPERIUM_WORK/_handoff_out/",
    "/home/vboxuser2/IMPERIUM_PRIVATE/OUTBOX/",
}

REQUIRED_FIELDS = [
    "schema_version",
    "task_id",
    "canonical_vm2_outbox",
    "canonical_pc_inbox",
    "legacy_scan_dirs",
    "source_priority_order",
    "fetch_latest_policy",
    "dedupe_policy",
    "notes",
    "owner_rule",
]


def add_unique(items: list[str], value: str) -> None:
    if value not in items:
        items.append(value)


def load_json(path: Path) -> tuple[dict[str, Any] | None, str | None]:
    if not path.exists():
        return None, f"missing_file:{path.as_posix()}"
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:  # noqa: BLE001
        return None, f"invalid_json:{path.as_posix()}:{type(exc).__name__}"
    if not isinstance(payload, dict):
        return None, f"invalid_json_type:{path.as_posix()}:expected_object"
    return payload, None


def normalize_paths(values: Any) -> list[str]:
    if not isinstance(values, list):
        return []
    out: list[str] = []
    for item in values:
        if not isinstance(item, str):
            continue
        cleaned = item.strip()
        if cleaned and cleaned not in out:
            out.append(cleaned)
    return out


def build_report(repo_root: Path) -> dict[str, Any]:
    passes: list[str] = []
    warnings: list[str] = []
    blocked: list[str] = []

    registry_path = repo_root / REGISTRY_REL
    policy_path = repo_root / POLICY_DOC_REL
    schema_path = repo_root / SCHEMA_REL
    state_builder_path = repo_root / SANCTUM_STATE_BUILDER_REL

    if policy_path.exists():
        passes.append(f"file_exists:{POLICY_DOC_REL}")
    else:
        add_unique(blocked, f"missing_required_file:{POLICY_DOC_REL}")

    if schema_path.exists():
        passes.append(f"file_exists:{SCHEMA_REL}")
    else:
        add_unique(warnings, f"optional_schema_missing:{SCHEMA_REL}")

    registry, err = load_json(registry_path)
    if err:
        add_unique(blocked, err)
        registry = None

    if registry is not None:
        for field in REQUIRED_FIELDS:
            if field in registry:
                passes.append(f"registry_field_present:{field}")
            else:
                add_unique(blocked, f"registry_missing_field:{field}")

        canonical = registry.get("canonical_vm2_outbox")
        if canonical == EXPECTED_CANONICAL_VM2:
            passes.append("canonical_vm2_outbox_exact_match")
        else:
            add_unique(blocked, f"canonical_vm2_outbox_mismatch:{canonical}")

        pc_inbox = registry.get("canonical_pc_inbox")
        if pc_inbox == EXPECTED_PC_INBOX:
            passes.append("canonical_pc_inbox_exact_match")
        else:
            add_unique(blocked, f"canonical_pc_inbox_mismatch:{pc_inbox}")

        priority = normalize_paths(registry.get("source_priority_order"))
        if not priority:
            add_unique(blocked, "source_priority_order_invalid_or_empty")
        else:
            if priority[0] == EXPECTED_CANONICAL_VM2:
                passes.append("source_priority_canonical_first")
            else:
                add_unique(blocked, "source_priority_first_is_not_canonical")

        legacy = normalize_paths(registry.get("legacy_scan_dirs"))
        if not legacy:
            add_unique(blocked, "legacy_scan_dirs_invalid_or_empty")
        else:
            unknown = [item for item in legacy if item not in EXPECTED_LEGACY]
            missing_expected = [item for item in EXPECTED_LEGACY if item not in legacy]
            if unknown:
                add_unique(blocked, f"legacy_scan_dirs_unexpected:{unknown}")
            if missing_expected:
                add_unique(blocked, f"legacy_scan_dirs_missing_expected:{missing_expected}")
            if not unknown and not missing_expected:
                passes.append("legacy_scan_dirs_match_expected")

        owner_rule = str(registry.get("owner_rule", ""))
        if "mandatory primary source" in owner_rule.lower() and "vm2_bundles" in owner_rule.lower():
            passes.append("owner_rule_mandatory_primary_source_present")
        else:
            add_unique(blocked, "owner_rule_missing_mandatory_primary_source_clause")

        if registry.get("ready_for_agent_status") is False:
            passes.append("ready_for_agent_status_false")
        else:
            add_unique(blocked, "ready_for_agent_status_must_be_false")

        if registry.get("act5_execution_ready") is False:
            passes.append("act5_execution_ready_false")
        else:
            add_unique(blocked, "act5_execution_ready_must_be_false")

    if state_builder_path.exists():
        source = state_builder_path.read_text(encoding="utf-8", errors="replace")
        if "REGISTRY/BUNDLE_ROUTE_REGISTRY.json" in source:
            passes.append("sanctum_state_builder_references_bundle_route_registry")
        else:
            add_unique(warnings, "sanctum_state_builder_not_yet_bound_to_bundle_route_registry")
    else:
        add_unique(warnings, f"missing_optional_file:{SANCTUM_STATE_BUILDER_REL}")

    verdict = "PASS" if not blocked else "BLOCKED"
    return {
        "task_id": TASK_ID,
        "repo_root": str(repo_root),
        "verdict": verdict,
        "passes": passes,
        "warnings": warnings,
        "blocked": blocked,
    }


def print_human(report: dict[str, Any]) -> None:
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

    print("\n=== SUMMARY ===")
    print(f"task_id: {report['task_id']}")
    print(f"verdict: {report['verdict']}")


def main() -> int:
    parser = argparse.ArgumentParser(description="Check bundle route registry v0.1")
    parser.add_argument("--repo-root", default=".", help="Repository root")
    parser.add_argument("--json", action="store_true", help="Print JSON report")
    args = parser.parse_args()

    repo_root = Path(args.repo_root).resolve()
    report = build_report(repo_root)

    if args.json:
        print(json.dumps(report, ensure_ascii=False, indent=2))
    else:
        print_human(report)

    return 0 if report["verdict"] == "PASS" else 2


if __name__ == "__main__":
    sys.exit(main())
