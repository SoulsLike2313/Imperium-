"""Validate Doctrinarium foundation artifacts for STAGE-1."""

from __future__ import annotations

import json
from pathlib import Path
from typing import List

from doctrinarium_common_v0_1 import (
    DOCTRINARIUM_ROOT,
    REPORTS_DIR,
    REPO_ROOT,
    build_report_base,
    list_missing,
    now_utc,
    parse_json_files,
)


TASK_ID = "TASK-20260515-DOCTRINARIUM-MVP-V0_1"
STAGE_ID = "STAGE-1"
REPORT_PATH = REPORTS_DIR / "foundation_validation_report.json"


def expected_directories() -> List[Path]:
    rels = [
        "DOCS",
        "LAWS",
        "DOCTRINES",
        "LAW_REGISTRY",
        "GATES",
        "ORGAN_HEALTH",
        "VIOLATIONS",
        "INQUISITION_HOOKS",
        "REPORTS",
        "REGISTRY",
        "SCHEMAS",
        "TESTS",
        "CONTINUITY",
    ]
    return [DOCTRINARIUM_ROOT / rel for rel in rels]


def main() -> int:
    report = build_report_base(
        report_id="doctrinarium.foundation_validation.v0_1",
        task_id=TASK_ID,
        stage_id=STAGE_ID,
    )

    readme_path = DOCTRINARIUM_ROOT / "README.md"
    registry_path = DOCTRINARIUM_ROOT / "REGISTRY" / "DOCTRINARIUM_REGISTRY.json"
    schema_files = sorted((DOCTRINARIUM_ROOT / "SCHEMAS").glob("*.json"))

    missing = list_missing(expected_directories() + [readme_path, registry_path])
    errors = parse_json_files(schema_files + [registry_path])

    readme_non_empty = readme_path.exists() and readme_path.stat().st_size > 0
    if not readme_non_empty and str(readme_path.relative_to(REPO_ROOT)).replace("\\", "/") not in missing:
        missing.append(str(readme_path.relative_to(REPO_ROOT)).replace("\\", "/"))

    blockers: List[str] = []
    if missing:
        blockers.append("missing_required_foundation_paths")
    if errors:
        blockers.append("foundation_json_parse_errors")
    if not readme_non_empty:
        blockers.append("readme_missing_or_empty")

    verdict = "PASS" if not blockers else "FAIL"
    evidence_paths = [
        str(readme_path.relative_to(REPO_ROOT)).replace("\\", "/"),
        str(registry_path.relative_to(REPO_ROOT)).replace("\\", "/"),
    ] + [str(path.relative_to(REPO_ROOT)).replace("\\", "/") for path in schema_files]

    report.update(
        {
            "started_utc": now_utc(),
            "completed_utc": now_utc(),
            "verdict": verdict,
            "directories_checked": [str(path.relative_to(REPO_ROOT)).replace("\\", "/") for path in expected_directories()],
            "schema_files_checked": [str(path.relative_to(REPO_ROOT)).replace("\\", "/") for path in schema_files],
            "readme_non_empty": readme_non_empty,
            "missing_paths": sorted(set(missing)),
            "json_parse_errors": errors,
            "warnings": [],
            "blockers": blockers,
            "evidence_paths": evidence_paths,
        }
    )

    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    return 0 if verdict == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
