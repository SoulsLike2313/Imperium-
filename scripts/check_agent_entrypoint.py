#!/usr/bin/env python3
"""Check AGENTS entrypoint and registry navigation layer integrity."""

from __future__ import annotations

import json
from pathlib import Path
import sys
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = REPO_ROOT / "src"
SCRIPT_ROOT = REPO_ROOT / "scripts"
for candidate in (SRC_ROOT, SCRIPT_ROOT):
    if str(candidate) not in sys.path:
        sys.path.insert(0, str(candidate))

from imperium.config import load_config
from imperium.receipts.model import Verdict, create_basic_receipt, utc_timestamp


RUNTIME_SUBDIR = Path(".imperium_runtime/agent_entrypoint_check")
REPORT_FILE = "AGENT_ENTRYPOINT_REPORT.json"
VERDICT_FILE = "AGENT_ENTRYPOINT_VERDICT.md"
RECEIPT_FILE = "AGENT_ENTRYPOINT_RECEIPT.json"

AGENTS_FILE = Path("AGENTS.md")
REGISTRY_FILE = Path("REGISTRY/AGENT_ENTRYPOINT_REGISTRY.json")
SCHEMA_FILE = Path("schemas/agent_entrypoint_registry.schema.json")

REQUIRED_SECTIONS = [
    "## Purpose",
    "## Current Truth Check",
    "## Safe First Commands",
    "## Active Source Zones",
    "## Current Active Entrypoints",
    "## Registries",
    "## Runtime / Generated / Local-Only Zones",
    "## Legacy / Caution Zones",
    "## Known Current Debt",
    "## Do Not Touch Without Owner Approval",
    "## How To Prepare A Safe Patch",
    "## Task Lifecycle Summary",
    "## Kiro Audit Follow-up Order",
]

REQUIRED_REGISTRY_KEYS = [
    "schema_version",
    "registry_name",
    "status",
    "active_source_zones",
    "active_entrypoints",
    "safe_readonly_commands",
    "safe_validation_commands",
    "runtime_zones",
    "legacy_caution_zones",
    "do_not_touch_without_owner_approval",
    "known_current_debt",
    "patch_bundle_rules",
    "next_recommended_tasks",
    "responsible_organs",
]

REQUIRED_PATHS = [
    Path("src/imperium"),
    Path("scripts/verify_repo.py"),
    Path("TOOLS/run_administratum_git_cli_check.sh"),
    Path("SANCTUM/sanctum_v0_29_qt.py"),
    Path("REGISTRY/COMMAND_ALLOWLIST.json"),
    Path("schemas/schema_registry.json"),
]

OPTIONAL_PATHS = [
    Path("SANCTUM/sanctum_git_cli_check_service_v0_1.py"),
    Path("SANCTUM/RUN_SANCTUM_V0_29_QT.ps1"),
    Path("DOCS/AGENT_NAVIGATION_AND_REPO_BOUNDARY_V0_1.md"),
]


def _read_text(path: Path) -> tuple[str | None, str | None]:
    try:
        return path.read_text(encoding="utf-8"), None
    except FileNotFoundError:
        return None, f"Missing file: {path.as_posix()}"
    except Exception as exc:
        return None, f"Failed reading {path.as_posix()}: {exc}"


def _read_json(path: Path) -> tuple[dict[str, Any] | None, str | None]:
    text, error = _read_text(path)
    if error is not None:
        return None, error
    try:
        payload = json.loads(text or "")
    except Exception as exc:
        return None, f"Invalid JSON at {path.as_posix()}: {exc}"
    if not isinstance(payload, dict):
        return None, f"JSON root must be object: {path.as_posix()}"
    return payload, None


def _validate_registry_structure(payload: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    missing = [key for key in REQUIRED_REGISTRY_KEYS if key not in payload]
    if missing:
        errors.append(f"Missing required registry keys: {', '.join(missing)}")

    if payload.get("schema_version") != "imperium.agent_entrypoint_registry.v0_1":
        errors.append("registry schema_version must be imperium.agent_entrypoint_registry.v0_1")
    if payload.get("registry_name") != "AGENT_ENTRYPOINT_REGISTRY":
        errors.append("registry_name must be AGENT_ENTRYPOINT_REGISTRY")

    for key in REQUIRED_REGISTRY_KEYS:
        if key in {"schema_version", "registry_name", "status"}:
            continue
        value = payload.get(key)
        if not isinstance(value, list):
            errors.append(f"registry key '{key}' must be a list")
            continue
        if not all(isinstance(item, str) and item.strip() for item in value):
            errors.append(f"registry key '{key}' must contain non-empty strings only")

    if not isinstance(payload.get("status"), str) or not str(payload.get("status")).strip():
        errors.append("registry status must be a non-empty string")

    return errors


def _validate_registry_against_schema(
    payload: dict[str, Any],
    schema_path: Path,
) -> tuple[list[str], list[str], bool]:
    warnings: list[str] = []
    errors: list[str] = []
    attempted = False

    try:
        import jsonschema  # type: ignore
    except ImportError:
        warnings.append("jsonschema is not installed; schema validation skipped (structural validation only).")
        return warnings, errors, attempted

    attempted = True
    schema_payload, schema_error = _read_json(schema_path)
    if schema_error is not None:
        errors.append(f"Schema unavailable for registry validation: {schema_error}")
        return warnings, errors, attempted

    try:
        jsonschema.validate(instance=payload, schema=schema_payload)
    except Exception as exc:
        errors.append(f"Schema validation failed: {exc}")

    return warnings, errors, attempted


def _missing_sections(markdown_text: str) -> list[str]:
    return [section for section in REQUIRED_SECTIONS if section not in markdown_text]


def _missing_paths(repo_root: Path, rel_paths: list[Path]) -> list[str]:
    missing: list[str] = []
    for rel_path in rel_paths:
        if not (repo_root / rel_path).exists():
            missing.append(rel_path.as_posix())
    return missing


def _overall_verdict(errors: list[str], warnings: list[str]) -> str:
    if errors:
        return Verdict.FAIL.value
    if warnings:
        return Verdict.PASS_WITH_WARNINGS.value
    return Verdict.PASS.value


def _write_verdict_md(path: Path, report: dict[str, Any]) -> None:
    lines = [
        "# AGENT ENTRYPOINT CHECK VERDICT",
        "",
        f"- schema_version: {report['schema_version']}",
        f"- timestamp_utc: {report['timestamp_utc']}",
        f"- repo_root: {report['repo_root']}",
        f"- overall_verdict: {report['overall_verdict']}",
        f"- blockers: {report['counts']['blockers']}",
        f"- warnings: {report['counts']['warnings']}",
        "",
        "## Key Checks",
        f"- agents_md_exists: {report['checks']['agents_md_exists']}",
        f"- required_sections_missing: {len(report['checks']['required_sections_missing'])}",
        f"- registry_loaded: {report['checks']['registry_loaded']}",
        f"- registry_schema_validation_attempted: {report['checks']['registry_schema_validation_attempted']}",
        f"- required_paths_missing: {len(report['checks']['required_paths_missing'])}",
        f"- optional_paths_missing: {len(report['checks']['optional_paths_missing'])}",
    ]

    if report["errors"]:
        lines.append("")
        lines.append("## Errors")
        for item in report["errors"]:
            lines.append(f"- {item}")

    if report["warnings"]:
        lines.append("")
        lines.append("## Warnings")
        for item in report["warnings"]:
            lines.append(f"- {item}")

    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def run_check(root: Path | None = None) -> dict[str, Any]:
    config = load_config(explicit_root=root, mode="dev")
    repo_root = config.root_path

    warnings: list[str] = []
    errors: list[str] = []

    agents_path = repo_root / AGENTS_FILE
    registry_path = repo_root / REGISTRY_FILE
    schema_path = repo_root / SCHEMA_FILE

    agents_text, agents_error = _read_text(agents_path)
    agents_exists = agents_error is None
    required_sections_missing: list[str] = []
    if agents_error is not None:
        errors.append(agents_error)
    else:
        required_sections_missing = _missing_sections(agents_text or "")
        if required_sections_missing:
            errors.append(
                "AGENTS.md missing required sections: "
                + ", ".join(required_sections_missing)
            )

    registry_payload, registry_error = _read_json(registry_path)
    registry_loaded = registry_error is None
    if registry_error is not None:
        errors.append(registry_error)
        registry_structure_errors: list[str] = []
        schema_validation_attempted = False
    else:
        registry_structure_errors = _validate_registry_structure(registry_payload or {})
        errors.extend(registry_structure_errors)
        schema_warnings, schema_errors, schema_validation_attempted = _validate_registry_against_schema(
            registry_payload or {},
            schema_path,
        )
        warnings.extend(schema_warnings)
        errors.extend(schema_errors)

    required_paths_missing = _missing_paths(repo_root, REQUIRED_PATHS)
    if required_paths_missing:
        errors.append(
            "Required paths missing: " + ", ".join(required_paths_missing)
        )

    optional_paths_missing = _missing_paths(repo_root, OPTIONAL_PATHS)
    if optional_paths_missing:
        warnings.append(
            "Optional paths missing: " + ", ".join(optional_paths_missing)
        )

    overall = _overall_verdict(errors, warnings)
    report = {
        "schema_version": "imperium.agent_entrypoint_check_report.v0_1",
        "timestamp_utc": utc_timestamp(),
        "repo_root": str(repo_root),
        "overall_verdict": overall,
        "warnings": warnings,
        "errors": errors,
        "counts": {
            "blockers": len(errors),
            "warnings": len(warnings),
        },
        "checks": {
            "agents_md_exists": agents_exists,
            "required_sections_missing": required_sections_missing,
            "registry_loaded": registry_loaded,
            "registry_structure_errors": registry_structure_errors if registry_loaded else [],
            "registry_schema_validation_attempted": schema_validation_attempted if registry_loaded else False,
            "required_paths_missing": required_paths_missing,
            "optional_paths_missing": optional_paths_missing,
        },
    }

    runtime_dir = repo_root / RUNTIME_SUBDIR
    runtime_dir.mkdir(parents=True, exist_ok=True)

    report_path = runtime_dir / REPORT_FILE
    verdict_path = runtime_dir / VERDICT_FILE
    receipt_path = runtime_dir / RECEIPT_FILE

    report_path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    _write_verdict_md(verdict_path, report)

    receipt = create_basic_receipt(
        "imperium.agent_entrypoint_check",
        overall,
        schema_version="imperium.agent_entrypoint_check_receipt.v0_1",
        warnings=warnings,
        errors=errors,
        report_path=str(report_path),
        verdict_path=str(verdict_path),
        counts=report["counts"],
    )
    receipt_path.write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")

    report["artifacts"] = {
        "report": str(report_path),
        "verdict": str(verdict_path),
        "receipt": str(receipt_path),
    }
    return report


def main() -> int:
    report = run_check()
    summary = {
        "schema_version": report["schema_version"],
        "timestamp_utc": report["timestamp_utc"],
        "repo_root": report["repo_root"],
        "overall_verdict": report["overall_verdict"],
        "counts": report["counts"],
        "artifacts": report.get("artifacts", {}),
    }
    print(json.dumps(summary, indent=2))
    return 1 if report["overall_verdict"] == Verdict.FAIL.value else 0


if __name__ == "__main__":
    raise SystemExit(main())
