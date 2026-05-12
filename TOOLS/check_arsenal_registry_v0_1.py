#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

VALID_PLATFORM = {"CROSS_PLATFORM", "WINDOWS_ONLY", "UBUNTU_ONLY"}
RISK_FIELDS = ["privacy_risk", "security_risk", "resource_cost", "complexity", "dependency_weight"]


def add_unique(items: list[str], value: str) -> None:
    if value not in items:
        items.append(value)


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def run_check(repo_root: Path, tool_index_rel: str, install_status_rel: str) -> dict[str, Any]:
    blockers: list[str] = []
    warnings: list[str] = []

    tool_index_path = (repo_root / tool_index_rel).resolve()
    install_status_path = (repo_root / install_status_rel).resolve()

    if not tool_index_path.exists():
        add_unique(blockers, "missing_tool_index")
    if not install_status_path.exists():
        add_unique(blockers, "missing_install_status")

    if blockers:
        return {
            "schema_version": "imperium.arsenal_registry_check.v0_1",
            "tool_index_path": str(tool_index_path),
            "install_status_path": str(install_status_path),
            "verdict": "BLOCKED",
            "blockers": blockers,
            "warnings": warnings,
            "counts": {"tools": 0, "installations": 0, "blockers": len(blockers), "warnings": 0},
        }

    try:
        tool_index = load_json(tool_index_path)
    except Exception as exc:
        add_unique(blockers, f"invalid_tool_index_json:{type(exc).__name__}")
        tool_index = {}

    try:
        install_status = load_json(install_status_path)
    except Exception as exc:
        add_unique(blockers, f"invalid_install_status_json:{type(exc).__name__}")
        install_status = {}

    required_top_tool_index = ["schema_version", "updated_at_utc", "generated_by", "tools"]
    for key in required_top_tool_index:
        if key not in tool_index:
            add_unique(blockers, f"tool_index_missing_top_field:{key}")

    required_top_install = ["schema_version", "checked_at_utc", "checked_on_contour", "installations"]
    for key in required_top_install:
        if key not in install_status:
            add_unique(blockers, f"install_status_missing_top_field:{key}")

    tools = tool_index.get("tools") if isinstance(tool_index, dict) else []
    if not isinstance(tools, list):
        add_unique(blockers, "tool_index_tools_not_list")
        tools = []

    installs = install_status.get("installations") if isinstance(install_status, dict) else []
    if not isinstance(installs, list):
        add_unique(blockers, "install_status_installations_not_list")
        installs = []

    install_by_tool_id: dict[str, dict[str, Any]] = {}
    for item in installs:
        if isinstance(item, dict):
            tool_id = item.get("tool_id")
            if isinstance(tool_id, str) and tool_id.strip():
                install_by_tool_id[tool_id] = item

    for idx, tool in enumerate(tools):
        tag = f"tool[{idx}]"
        if not isinstance(tool, dict):
            add_unique(blockers, f"{tag}:not_object")
            continue

        required_fields = [
            "tool_id",
            "name",
            "category",
            "platform",
            "tool_type",
            "purpose_for_imperium",
            "owner_use_case",
            "servitor_use_case",
            "installation_method",
            "license_cost",
            "offline_capability",
            "privacy_risk",
            "security_risk",
            "resource_cost",
            "complexity",
            "maturity",
            "dependency_weight",
            "recommended_phase",
            "install_now",
            "why_now_or_later",
            "alternatives",
            "official_url",
            "docs_url",
            "notes",
            "status",
        ]
        for key in required_fields:
            if key not in tool:
                add_unique(blockers, f"{tag}:missing_field:{key}")

        platform = str(tool.get("platform", ""))
        if platform not in VALID_PLATFORM:
            add_unique(blockers, f"{tag}:invalid_platform:{platform}")

        for risk_field in RISK_FIELDS:
            value = str(tool.get(risk_field, "")).strip()
            if not value:
                add_unique(blockers, f"{tag}:missing_risk_field:{risk_field}")

        install_now = str(tool.get("install_now", "")).lower()
        status = str(tool.get("status", ""))
        tool_id = str(tool.get("tool_id", ""))
        install_entry = install_by_tool_id.get(tool_id)

        if install_now == "yes" and status != "OWNER_APPROVED":
            add_unique(blockers, f"{tag}:install_now_yes_without_owner_approved_status")

        if install_entry is None:
            add_unique(warnings, f"{tag}:missing_install_status_entry")
        else:
            install_status_value = str(install_entry.get("status", ""))
            if install_now == "yes" and install_status_value not in {"AVAILABLE_CONFIRMED", "OWNER_APPROVED"}:
                add_unique(blockers, f"{tag}:install_now_yes_but_not_available_or_owner_approved")
            if install_status_value == "OWNER_APPROVED" and status != "OWNER_APPROVED":
                add_unique(blockers, f"{tag}:install_status_owner_approved_but_tool_not_owner_approved")

    verdict = "PASS"
    if blockers:
        verdict = "BLOCKED"
    elif warnings:
        verdict = "PASS_WITH_WARNINGS"

    return {
        "schema_version": "imperium.arsenal_registry_check.v0_1",
        "tool_index_path": str(tool_index_path),
        "install_status_path": str(install_status_path),
        "verdict": verdict,
        "blockers": blockers,
        "warnings": warnings,
        "counts": {
            "tools": len(tools),
            "installations": len(installs),
            "blockers": len(blockers),
            "warnings": len(warnings),
        },
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Check ARSENAL registries v0.1")
    parser.add_argument("--repo-root", default=".", help="Repository root")
    parser.add_argument("--tool-index", default="REGISTRY/ARSENAL_TOOL_INDEX.json")
    parser.add_argument("--install-status", default="REGISTRY/ARSENAL_INSTALL_STATUS.json")
    parser.add_argument("--human", action="store_true", help="Print human-readable summary")
    return parser.parse_args()


def print_human(report: dict[str, Any]) -> None:
    print("=== IMPERIUM ARSENAL REGISTRY CHECK ===")
    print(f"tool_index: {report['tool_index_path']}")
    print(f"install_status: {report['install_status_path']}")
    print(f"verdict: {report['verdict']}")
    print(f"tools: {report['counts']['tools']}")
    print(f"installations: {report['counts']['installations']}")
    print(f"blockers: {report['counts']['blockers']}")
    print(f"warnings: {report['counts']['warnings']}")


def main() -> int:
    args = parse_args()
    repo_root = Path(args.repo_root).resolve()
    report = run_check(repo_root, args.tool_index, args.install_status)
    if args.human:
        print_human(report)
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0 if not report["blockers"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
