from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


TASK_ID = "TASK-NEWGEN-MECHANICUS-ARSENAL-INTAKE-FOUNDATION-PC-V0_1"

REQUIRED_CARD_FIELDS = [
    "capability_id",
    "name",
    "category",
    "status",
    "owner_organ",
    "purpose",
    "what_problem_it_solves",
    "source_type",
    "source_url_or_path",
    "license_or_trust_note",
    "install_required",
    "install_gate",
    "validation_commands",
    "expected_receipts",
    "safety_notes",
    "security_notes",
    "offline_or_network_dependency",
    "promoted_by_receipt",
    "last_reviewed_utc",
    "next_review_reason",
    "limitations",
    "allowed_use_cases",
    "forbidden_use_cases",
]

REQUIRED_DIRS = [
    "IMPERIUM_NEW_GENERATION/MECHANICUS/ARSENAL",
    "IMPERIUM_NEW_GENERATION/MECHANICUS/ARSENAL/REGISTRY",
    "IMPERIUM_NEW_GENERATION/MECHANICUS/ARSENAL/SCHEMAS",
    "IMPERIUM_NEW_GENERATION/MECHANICUS/ARSENAL/CANDIDATES",
    "IMPERIUM_NEW_GENERATION/MECHANICUS/ARSENAL/SANDBOX",
    "IMPERIUM_NEW_GENERATION/MECHANICUS/ARSENAL/CANON",
    "IMPERIUM_NEW_GENERATION/MECHANICUS/ARSENAL/QUARANTINE",
    "IMPERIUM_NEW_GENERATION/MECHANICUS/ARSENAL/RECEIPTS",
    "IMPERIUM_NEW_GENERATION/MECHANICUS/ARSENAL/VALIDATION",
    "IMPERIUM_NEW_GENERATION/MECHANICUS/ARSENAL/CATEGORIES",
    "IMPERIUM_NEW_GENERATION/MECHANICUS/ARSENAL/CATEGORIES/LANGUAGES",
    "IMPERIUM_NEW_GENERATION/MECHANICUS/ARSENAL/CATEGORIES/TOOLS",
    "IMPERIUM_NEW_GENERATION/MECHANICUS/ARSENAL/CATEGORIES/UTILITIES",
    "IMPERIUM_NEW_GENERATION/MECHANICUS/ARSENAL/CATEGORIES/UI_FRAMEWORKS",
    "IMPERIUM_NEW_GENERATION/MECHANICUS/ARSENAL/CATEGORIES/DATABASES",
    "IMPERIUM_NEW_GENERATION/MECHANICUS/ARSENAL/CATEGORIES/SEARCH_INDEXING",
    "IMPERIUM_NEW_GENERATION/MECHANICUS/ARSENAL/CATEGORIES/VISUAL_TESTING",
    "IMPERIUM_NEW_GENERATION/MECHANICUS/ARSENAL/CATEGORIES/CODE_QUALITY",
    "IMPERIUM_NEW_GENERATION/MECHANICUS/ARSENAL/CATEGORIES/LOCAL_LLM",
    "IMPERIUM_NEW_GENERATION/MECHANICUS/ARSENAL/CATEGORIES/CLOUD_LLM_ADAPTERS",
    "IMPERIUM_NEW_GENERATION/MECHANICUS/ARSENAL/CATEGORIES/PROMPTING_PATTERNS",
    "IMPERIUM_NEW_GENERATION/MECHANICUS/ARSENAL/CATEGORIES/ALGORITHMS",
    "IMPERIUM_NEW_GENERATION/MECHANICUS/ARSENAL/CATEGORIES/REFERENCE_CODE",
    "IMPERIUM_NEW_GENERATION/MECHANICUS/ARSENAL/CATEGORIES/EXAMPLES",
    "IMPERIUM_NEW_GENERATION/MECHANICUS/ARSENAL/CATEGORIES/PLAYBOOKS",
]


def now_utc() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def load_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def main() -> int:
    repo_root = Path(__file__).resolve().parents[3]
    arsenal_root = repo_root / "IMPERIUM_NEW_GENERATION" / "MECHANICUS" / "ARSENAL"
    report_root = (
        repo_root
        / "IMPERIUM_NEW_GENERATION"
        / "MECHANICUS"
        / "REPORTS"
        / TASK_ID
    )
    report_path = report_root / "arsenal_foundation_check_report.json"

    violations: list[str] = []
    warnings: list[str] = []
    info: list[str] = []

    # 1) Required directories
    missing_dirs = [rel for rel in REQUIRED_DIRS if not (repo_root / rel).is_dir()]
    if missing_dirs:
        violations.append(f"missing_required_dirs:{len(missing_dirs)}")
        for rel in missing_dirs:
            warnings.append(f"missing_dir:{rel}")
    else:
        info.append("required_directories_present")

    # 2) Required JSON artifacts parse check
    json_targets = [
        "IMPERIUM_NEW_GENERATION/MECHANICUS/ARSENAL/SCHEMAS/capability_card_schema_v0_1.json",
        "IMPERIUM_NEW_GENERATION/MECHANICUS/ARSENAL/SCHEMAS/arsenal_registry_schema_v0_1.json",
        "IMPERIUM_NEW_GENERATION/MECHANICUS/ARSENAL/SCHEMAS/validation_receipt_schema_v0_1.json",
        "IMPERIUM_NEW_GENERATION/MECHANICUS/ARSENAL/REGISTRY/arsenal_registry_v0_1.json",
        "IMPERIUM_NEW_GENERATION/MECHANICUS/ARSENAL/REGISTRY/category_registry_v0_1.json",
        "IMPERIUM_NEW_GENERATION/MECHANICUS/ARSENAL/REGISTRY/intake_queue_v0_1.json",
    ]
    json_parse_ok = 0
    for rel in json_targets:
        path = repo_root / rel
        if not path.is_file():
            violations.append(f"missing_json:{rel}")
            continue
        try:
            load_json(path)
            json_parse_ok += 1
        except Exception as exc:  # pragma: no cover
            violations.append(f"json_parse_error:{rel}:{exc}")
    info.append(f"json_parse_ok:{json_parse_ok}/{len(json_targets)}")

    # 3) Cards scan and field/category validation
    try:
        category_registry = load_json(
            repo_root / "IMPERIUM_NEW_GENERATION/MECHANICUS/ARSENAL/REGISTRY/category_registry_v0_1.json"
        )
        category_set = {item["category"] for item in category_registry.get("categories", [])}
    except Exception:
        category_set = set()
        violations.append("category_registry_unreadable")

    card_files = sorted((arsenal_root / "CATEGORIES").glob("*/*.json"))
    cards: list[dict[str, Any]] = []
    for card_file in card_files:
        try:
            payload = load_json(card_file)
            if not isinstance(payload, dict):
                violations.append(f"card_not_object:{card_file.relative_to(repo_root).as_posix()}")
                continue
            cards.append(payload)
        except Exception as exc:  # pragma: no cover
            violations.append(f"card_json_error:{card_file.relative_to(repo_root).as_posix()}:{exc}")

    for card in cards:
        cap = str(card.get("capability_id", "UNKNOWN"))
        missing = [k for k in REQUIRED_CARD_FIELDS if k not in card]
        if missing:
            violations.append(f"card_missing_fields:{cap}:{','.join(missing)}")
        category = str(card.get("category", ""))
        if category_set and category not in category_set:
            violations.append(f"card_unknown_category:{cap}:{category}")

        # Honest CANON checks
        status = str(card.get("status", ""))
        if status == "CANON":
            evidence_paths = card.get("canon_evidence_paths", [])
            has_valid_evidence = False
            if isinstance(evidence_paths, list) and evidence_paths:
                missing_evidence = []
                for rel in evidence_paths:
                    if not isinstance(rel, str):
                        missing_evidence.append("<non-string>")
                        continue
                    if not (repo_root / rel).exists():
                        missing_evidence.append(rel)
                if missing_evidence:
                    violations.append(f"canon_missing_evidence:{cap}:{';'.join(missing_evidence)}")
                else:
                    has_valid_evidence = True

            promoted_by = str(card.get("promoted_by_receipt", ""))
            if not has_valid_evidence and promoted_by.endswith(".json"):
                candidate_paths = [
                    repo_root / promoted_by,
                    arsenal_root / "RECEIPTS" / promoted_by,
                ]
                has_valid_evidence = any(path.exists() for path in candidate_paths)

            if not has_valid_evidence:
                violations.append(f"canon_without_evidence:{cap}")

            if bool(card.get("install_required", False)):
                violations.append(f"canon_requires_install:{cap}")

    # 4) No network install performed (heuristic: no install receipts / no canon requiring install)
    install_receipt_hits = list((arsenal_root / "RECEIPTS").glob("*install*"))
    if install_receipt_hits:
        warnings.append(f"install_receipt_files_present:{len(install_receipt_hits)}")
    info.append("network_install_check:heuristic")

    # 5) No runtime/generated junk committed in scoped folders
    junk_dirs = {"__pycache__", ".cache", "node_modules"}
    junk_exts = {".log", ".pid", ".tmp", ".cache", ".pyc", ".pyo"}
    junk_files: list[str] = []
    for root in [arsenal_root, report_root]:
        if not root.exists():
            continue
        for path in root.rglob("*"):
            rel = path.relative_to(repo_root).as_posix()
            if path.is_dir() and path.name in junk_dirs:
                junk_files.append(rel + "/")
            if path.is_file() and path.suffix.lower() in junk_exts:
                junk_files.append(rel)
    if junk_files:
        violations.append(f"junk_artifacts_found:{len(junk_files)}")
        warnings.extend([f"junk:{entry}" for entry in junk_files[:50]])
    else:
        info.append("junk_scan_clean")

    # 6) Build report
    status_counts = {"CANDIDATE": 0, "SANDBOX": 0, "CANON": 0, "QUARANTINE": 0, "REJECTED": 0}
    for card in cards:
        status = str(card.get("status", ""))
        if status in status_counts:
            status_counts[status] += 1

    verdict = "PASS"
    if violations:
        verdict = "FAIL"
    elif warnings:
        verdict = "PASS_WITH_WARNINGS"

    report_payload = {
        "task_id": TASK_ID,
        "checked_at_utc": now_utc(),
        "checker": "check_mechanicus_arsenal_foundation_v0_1.py",
        "verdict": verdict,
        "summary": {
            "card_count": len(cards),
            "status_counts": status_counts,
            "violations_count": len(violations),
            "warnings_count": len(warnings),
        },
        "checks": {
            "required_directories": {"ok": len(missing_dirs) == 0, "missing": missing_dirs},
            "json_parse_targets_count": len(json_targets),
            "cards_scanned": len(cards),
            "network_install_policy": "heuristic_no_install_receipt_and_no_canon_install",
            "junk_scan_paths": [
                "IMPERIUM_NEW_GENERATION/MECHANICUS/ARSENAL",
                f"IMPERIUM_NEW_GENERATION/MECHANICUS/REPORTS/{TASK_ID}",
            ],
        },
        "violations": violations,
        "warnings": warnings,
        "info": info,
    }
    report_root.mkdir(parents=True, exist_ok=True)
    report_path.write_text(json.dumps(report_payload, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")

    return 0 if verdict in {"PASS", "PASS_WITH_WARNINGS"} else 1


if __name__ == "__main__":
    raise SystemExit(main())
