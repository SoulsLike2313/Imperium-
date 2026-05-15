"""Check Doctrinarium law integrity for STAGE-3."""

from __future__ import annotations

from pathlib import Path
from typing import Dict, List, Tuple

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
STAGE_ID = "STAGE-3"
REPORT_PATH = REPORTS_DIR / "law_integrity_report.json"
FIXTURE_REPORT = DOCTRINARIUM_ROOT / "TESTS" / "law_integrity_fixture_results.json"


REQUIRED_FIELDS = {"law_id", "title", "status", "description", "provenance", "timestamp_utc"}


def detect_duplicates(laws: List[Dict[str, object]]) -> List[str]:
    law_ids = [str(law.get("law_id", "")) for law in laws]
    return sorted({law_id for law_id in law_ids if law_id and law_ids.count(law_id) > 1})


def detect_missing_fields(laws: List[Dict[str, object]]) -> Dict[str, List[str]]:
    out: Dict[str, List[str]] = {}
    for law in laws:
        law_id = str(law.get("law_id", "UNKNOWN"))
        missing = sorted(field for field in REQUIRED_FIELDS if field not in law)
        if missing:
            out[law_id] = missing
    return out


def detect_contradictions(laws: List[Dict[str, object]]) -> List[str]:
    active_rules_text = " ".join(
        " ".join(str(rule).lower() for rule in law.get("rules", []))
        for law in laws
        if str(law.get("status", "")).lower() == "active"
    )
    contradictions: List[str] = []
    if "no commit from vm2" in active_rules_text and "allow commit from vm2" in active_rules_text:
        contradictions.append("vm2_commit_rule_contradiction")
    return contradictions


def run_fixture_self_tests() -> Tuple[List[Dict[str, object]], List[str]]:
    fixture_dir = DOCTRINARIUM_ROOT / "TESTS" / "fixtures" / "law_integrity"
    results: List[Dict[str, object]] = []
    blockers: List[str] = []

    tests = [
        ("duplicate_law_ids_fixture.json", "expect_duplicate_detection"),
        ("missing_required_field_fixture.json", "expect_missing_fields_detection"),
        ("contradiction_fixture.json", "expect_contradiction_detection"),
    ]

    for file_name, expect in tests:
        path = fixture_dir / file_name
        case = {"fixture": file_name, "expectation": expect, "detected": False, "details": []}
        if not path.exists():
            case["details"].append("fixture_missing")
            blockers.append(f"missing_fixture:{file_name}")
            results.append(case)
            continue
        data = load_json(path)
        laws = data.get("laws", [])
        dup = detect_duplicates(laws)
        missing = detect_missing_fields(laws)
        contra = detect_contradictions(laws)
        if expect == "expect_duplicate_detection":
            case["detected"] = bool(dup)
            case["details"] = dup
        elif expect == "expect_missing_fields_detection":
            case["detected"] = bool(missing)
            case["details"] = [f"{k}:{v}" for k, v in missing.items()]
        elif expect == "expect_contradiction_detection":
            case["detected"] = bool(contra)
            case["details"] = contra
        if not case["detected"]:
            blockers.append(f"fixture_detection_failed:{file_name}")
        results.append(case)

    dump_json(FIXTURE_REPORT, {"timestamp_utc": now_utc(), "results": results})
    return results, blockers


def main() -> int:
    registry_path = DOCTRINARIUM_ROOT / "LAW_REGISTRY" / "LAW_REGISTRY_V0_1.json"
    law_paths = sorted((DOCTRINARIUM_ROOT / "LAWS").glob("LAW-*.json"))

    blockers: List[str] = []
    warnings: List[str] = []
    issues: List[str] = []

    if not registry_path.exists():
        blockers.append("missing_law_registry")
        registry = {}
    else:
        registry = load_json(registry_path)

    laws: List[Dict[str, object]] = []
    for path in law_paths:
        try:
            laws.append(load_json(path))
        except Exception as exc:  # pragma: no cover - diagnostic path
            blockers.append(f"law_json_parse_failed:{path.name}:{exc}")

    duplicates = detect_duplicates(laws)
    missing_fields = detect_missing_fields(laws)
    contradictions = detect_contradictions(laws)

    if duplicates:
        issues.append("duplicate_law_ids")
    if missing_fields:
        issues.append("missing_required_fields")
    if contradictions:
        issues.append("contradictions_detected")

    fixture_results, fixture_blockers = run_fixture_self_tests()
    blockers.extend(fixture_blockers)

    # In active registry we require clean law set.
    if duplicates:
        blockers.append("active_registry_has_duplicate_law_ids")
    if missing_fields:
        blockers.append("active_registry_has_missing_required_fields")
    if contradictions:
        blockers.append("active_registry_has_contradictions")

    verdict = "PASS" if not blockers else "FAIL"

    report = build_report_base(
        report_id="doctrinarium.law_integrity.v0_1",
        task_id=TASK_ID,
        stage_id=STAGE_ID,
    )
    report.update(
        {
            "started_utc": now_utc(),
            "completed_utc": now_utc(),
            "verdict": verdict,
            "registry_id": registry.get("registry_id", "UNKNOWN"),
            "law_files_checked": [str(path.relative_to(REPO_ROOT)).replace("\\", "/") for path in law_paths],
            "duplicate_law_ids": duplicates,
            "missing_required_fields": missing_fields,
            "contradiction_count": len(contradictions),
            "contradictions": contradictions,
            "fixture_results": fixture_results,
            "warnings": warnings,
            "blockers": blockers,
            "issues": issues,
            "evidence_paths": [
                str(registry_path.relative_to(REPO_ROOT)).replace("\\", "/"),
                str(FIXTURE_REPORT.relative_to(REPO_ROOT)).replace("\\", "/"),
            ]
            + [str(path.relative_to(REPO_ROOT)).replace("\\", "/") for path in law_paths],
        }
    )

    dump_json(REPORT_PATH, report)
    return 0 if verdict == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())

