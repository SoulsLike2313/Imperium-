"""Validate Doctrinarium law files and law registry for STAGE-2."""

from __future__ import annotations

import re
from pathlib import Path
from typing import Dict, List

from doctrinarium_common_v0_1 import (
    DOCTRINARIUM_ROOT,
    REPORTS_DIR,
    REPO_ROOT,
    build_report_base,
    dump_json,
    load_json,
    now_utc,
)


TASK_ID = "TASK-20260515-DOCTRINARIUM-MVP-V0_1"
STAGE_ID = "STAGE-2"
SCHEMA_REPORT_PATH = REPORTS_DIR / "schema_validation_report.json"
REGISTRY_REPORT_PATH = REPORTS_DIR / "law_registry_validation_report.json"
LAW_ID_RE = re.compile(r"^LAW-[0-9]{3}$")


def validate_schema_files() -> Dict[str, object]:
    schema_dir = DOCTRINARIUM_ROOT / "SCHEMAS"
    required = ["law.schema.json", "doctrine.schema.json", "law_registry.schema.json"]
    validated: List[str] = []
    errors: Dict[str, str] = {}
    for name in required:
        path = schema_dir / name
        rel = str(path.relative_to(REPO_ROOT)).replace("\\", "/")
        if not path.exists():
            errors[rel] = "missing schema file"
            continue
        try:
            doc = load_json(path)
            if doc.get("type") != "object":
                errors[rel] = "schema type must be object"
            else:
                validated.append(rel)
        except Exception as exc:  # pragma: no cover - diagnostic path
            errors[rel] = str(exc)
    verdict = "PASS" if not errors else "FAIL"
    report = build_report_base(
        report_id="doctrinarium.schema_validation.v0_1",
        task_id=TASK_ID,
        stage_id=STAGE_ID,
    )
    report.update(
        {
            "started_utc": now_utc(),
            "completed_utc": now_utc(),
            "verdict": verdict,
            "validated_schemas": validated,
            "errors": errors,
            "warnings": [],
            "blockers": ["invalid_or_missing_schema_files"] if errors else [],
            "evidence_paths": validated,
        }
    )
    dump_json(SCHEMA_REPORT_PATH, report)
    return report


def validate_law_registry() -> Dict[str, object]:
    laws_dir = DOCTRINARIUM_ROOT / "LAWS"
    registry_path = DOCTRINARIUM_ROOT / "LAW_REGISTRY" / "LAW_REGISTRY_V0_1.json"

    report = build_report_base(
        report_id="doctrinarium.law_registry_validation.v0_1",
        task_id=TASK_ID,
        stage_id=STAGE_ID,
    )
    report["started_utc"] = now_utc()

    blockers: List[str] = []
    warnings: List[str] = []
    law_files = sorted(laws_dir.glob("LAW-*.json"))
    parsed_laws: List[Dict[str, object]] = []
    invalid_laws: List[str] = []

    for file_path in law_files:
        rel = str(file_path.relative_to(REPO_ROOT)).replace("\\", "/")
        try:
            doc = load_json(file_path)
            required_fields = ["law_id", "title", "status", "description", "provenance", "timestamp_utc"]
            missing = [field for field in required_fields if field not in doc]
            if missing:
                invalid_laws.append(f"{rel}: missing fields {missing}")
                continue
            law_id = str(doc["law_id"])
            if not LAW_ID_RE.match(law_id):
                invalid_laws.append(f"{rel}: invalid law_id format")
                continue
            parsed_laws.append(doc)
        except Exception as exc:  # pragma: no cover - diagnostic path
            invalid_laws.append(f"{rel}: {exc}")

    law_ids = [str(item["law_id"]) for item in parsed_laws]
    duplicate_ids = sorted({law_id for law_id in law_ids if law_ids.count(law_id) > 1})
    if duplicate_ids:
        blockers.append("duplicate_law_id_detected")

    if invalid_laws:
        blockers.append("invalid_law_documents")

    if not registry_path.exists():
        blockers.append("missing_law_registry")
        registry_doc = {}
    else:
        try:
            registry_doc = load_json(registry_path)
        except Exception as exc:  # pragma: no cover - diagnostic path
            blockers.append("law_registry_json_parse_failed")
            registry_doc = {"_parse_error": str(exc)}

    registry_required = ["registry_id", "laws", "provenance", "timestamp_utc"]
    missing_registry_fields = [field for field in registry_required if field not in registry_doc]
    if missing_registry_fields:
        blockers.append("law_registry_missing_required_fields")

    registry_law_ids: List[str] = []
    registry_path_errors: List[str] = []
    for row in registry_doc.get("laws", []):
        law_id = str(row.get("law_id", ""))
        law_path = str(row.get("path", ""))
        registry_law_ids.append(law_id)
        if law_path:
            full_path = REPO_ROOT / law_path
            if not full_path.exists():
                registry_path_errors.append(f"missing file for {law_id}: {law_path}")
    if registry_path_errors:
        blockers.append("law_registry_references_missing_files")

    law_id_set = set(law_ids)
    missing_in_registry = sorted(law_id_set - set(registry_law_ids))
    if missing_in_registry:
        blockers.append("law_registry_missing_law_entries")

    registry_duplicates = sorted({law_id for law_id in registry_law_ids if registry_law_ids.count(law_id) > 1})
    if registry_duplicates:
        blockers.append("law_registry_duplicate_entries")

    verdict = "PASS" if not blockers else "FAIL"
    report.update(
        {
            "completed_utc": now_utc(),
            "registry_id": registry_doc.get("registry_id", "UNKNOWN"),
            "verdict": verdict,
            "provenance": registry_doc.get("provenance", {}),
            "law_files_checked": [str(path.relative_to(REPO_ROOT)).replace("\\", "/") for path in law_files],
            "law_count": len(parsed_laws),
            "duplicate_law_ids": duplicate_ids,
            "invalid_laws": invalid_laws,
            "registry_missing_required_fields": missing_registry_fields,
            "registry_duplicate_law_entries": registry_duplicates,
            "registry_missing_law_entries": missing_in_registry,
            "registry_path_errors": registry_path_errors,
            "warnings": warnings,
            "blockers": blockers,
            "evidence_paths": [
                str(registry_path.relative_to(REPO_ROOT)).replace("\\", "/"),
                str(SCHEMA_REPORT_PATH.relative_to(REPO_ROOT)).replace("\\", "/"),
            ]
            + [str(path.relative_to(REPO_ROOT)).replace("\\", "/") for path in law_files],
        }
    )
    dump_json(REGISTRY_REPORT_PATH, report)
    return report


def main() -> int:
    schema_report = validate_schema_files()
    registry_report = validate_law_registry()
    if schema_report["verdict"] != "PASS":
        return 1
    return 0 if registry_report["verdict"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())

