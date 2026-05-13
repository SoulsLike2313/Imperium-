#!/usr/bin/env python3
from __future__ import annotations

import argparse
import datetime as dt
import json
from pathlib import Path
from typing import Any

TASK_ID = "TASK-20260513-WARNING-BUDGET-V0_1"
SCHEMA_VERSION = "imperium.warning_budget_check.v0_1"
RUNTIME_REL = ".imperium_runtime/astronomicon/warning_budget_check"
REPORT_NAME = "WARNING_BUDGET_CHECK_REPORT.json"
VERDICT_NAME = "WARNING_BUDGET_CHECK_VERDICT.md"
RECEIPT_NAME = "WARNING_BUDGET_CHECK_RECEIPT.json"

WARNING_BUDGET_PATH = "REGISTRY/WARNING_BUDGET.json"
POLICY_DOC_PATH = "DOCS/WARNING_BUDGET_POLICY_V0_1.md"
START_HERE_PATH = "START_HERE.md"
CURRENT_TRUTH_PATH = "CURRENT_STATE/ARC5_PREFIRE_CURRENT_TRUTH_20260513.json"
SYNTHESIS_PATH = "ORGANS/ASTRONOMICON/REGISTRY/ARC5_PREFIRE/ARC5_PREFIRE_SYNTHESIS_20260513.md"

REQUIRED_TOP_LEVEL_FIELDS = [
    "schema_version",
    "status",
    "created_at_utc",
    "task_id",
    "repo_head_at_creation",
    "commit_count_at_creation",
    "latest_commit_subject_at_creation",
    "purpose",
    "act5_execution_ready",
    "ready_for_agent_must_remain_false",
    "policy_summary",
    "verdict_semantics",
    "warning_classes",
    "budgets",
    "blocker_rules",
    "legacy_debt_policy",
    "new_warning_policy",
    "required_evidence_for_pass",
    "next_steps",
]

REQUIRED_WARNING_CLASS_IDS = [
    "FAKE_GREEN_RISK",
    "CURRENT_TRUTH_STALE",
    "ADVISORY_AS_AUTHORITY",
    "READY_FOR_AGENT_POLICY",
    "BUNDLE_INTAKE_SCOPE",
    "RAW_SUBPROCESS_OR_UNGATED_ACTION",
    "PATH_BOUNDARY_OR_PORTABILITY",
    "REGISTRY_DRIFT",
    "VISUAL_RUNTIME_COUPLING",
    "AUTO_DELETE_OR_CLEANUP_RISK",
    "WARNING_FLOOD",
    "SECURITY_SECRET_RISK",
]

REQUIRED_BLOCKER_RULE_TOKENS = [
    "FAKE_GREEN_RISK",
    "READY_FOR_AGENT_POLICY",
    "ADVISORY_AS_AUTHORITY",
    "AUTO_DELETE_OR_CLEANUP_RISK",
    "BUNDLE_INTAKE_SCOPE",
]

FORBIDDEN_READY_PATTERNS = [
    "act 5 execution is ready",
    "act5 execution is ready",
    "act 5 ready",
    "act5 ready",
    "act5_execution_ready: true",
    "act5_execution_ready=true",
]


def now_utc() -> str:
    return dt.datetime.now(dt.timezone.utc).isoformat()


def add_unique(items: list[str], value: str) -> None:
    if value not in items:
        items.append(value)


def read_json_obj(path: Path) -> tuple[dict[str, Any] | None, str | None]:
    if not path.exists():
        return None, f"missing_file:{path.as_posix()}"
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:  # noqa: BLE001
        return None, f"invalid_json:{path.as_posix()}:{type(exc).__name__}"
    if not isinstance(payload, dict):
        return None, f"invalid_json_type:{path.as_posix()}"
    return payload, None


def write_artifacts(repo_root: Path, report: dict[str, Any]) -> dict[str, str]:
    runtime_dir = repo_root / RUNTIME_REL
    runtime_dir.mkdir(parents=True, exist_ok=True)

    report_path = runtime_dir / REPORT_NAME
    verdict_path = runtime_dir / VERDICT_NAME
    receipt_path = runtime_dir / RECEIPT_NAME

    report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    lines: list[str] = [
        "# Warning Budget Check v0.1",
        "",
        f"- task_id: {TASK_ID}",
        f"- generated_at_utc: {report.get('generated_at_utc')}",
        f"- verdict: {report.get('verdict')}",
        f"- pass_count: {len(report.get('passes', []))}",
        f"- warn_count: {len(report.get('warnings', []))}",
        f"- blocked_count: {len(report.get('blocked', []))}",
    ]

    if report.get("blocked"):
        lines.append("")
        lines.append("## BLOCKED")
        for item in report["blocked"]:
            lines.append(f"- {item}")

    if report.get("warnings"):
        lines.append("")
        lines.append("## WARN")
        for item in report["warnings"]:
            lines.append(f"- {item}")

    if report.get("passes"):
        lines.append("")
        lines.append("## PASS")
        for item in report["passes"]:
            lines.append(f"- {item}")

    verdict_path.write_text("\n".join(lines) + "\n", encoding="utf-8")

    receipt = {
        "schema_version": "imperium.warning_budget_check_receipt.v0_1",
        "task_id": TASK_ID,
        "generated_at_utc": now_utc(),
        "verdict": report.get("verdict"),
        "report_path": str(report_path),
        "verdict_path": str(verdict_path),
    }
    receipt_path.write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    return {
        "report": str(report_path),
        "verdict": str(verdict_path),
        "receipt": str(receipt_path),
    }


def build_report(repo_root: Path) -> dict[str, Any]:
    passes: list[str] = []
    warnings: list[str] = []
    blocked: list[str] = []

    budget_path = repo_root / WARNING_BUDGET_PATH
    policy_doc_path = repo_root / POLICY_DOC_PATH
    start_here_path = repo_root / START_HERE_PATH
    current_truth_path = repo_root / CURRENT_TRUTH_PATH
    synthesis_path = repo_root / SYNTHESIS_PATH

    payload, payload_err = read_json_obj(budget_path)
    if payload_err:
        add_unique(blocked, payload_err)
        payload = None
    else:
        passes.append(f"file_exists:{WARNING_BUDGET_PATH}")

    if policy_doc_path.exists():
        passes.append(f"file_exists:{POLICY_DOC_PATH}")
    else:
        add_unique(blocked, f"missing_required_file:{POLICY_DOC_PATH}")

    if start_here_path.exists():
        passes.append(f"file_exists:{START_HERE_PATH}")
    else:
        add_unique(blocked, f"missing_required_file:{START_HERE_PATH}")

    if synthesis_path.exists():
        passes.append(f"file_exists:{SYNTHESIS_PATH}")
    else:
        add_unique(blocked, f"missing_required_file:{SYNTHESIS_PATH}")

    if payload is not None:
        for field in REQUIRED_TOP_LEVEL_FIELDS:
            if field in payload:
                passes.append(f"warning_budget_field_present:{field}")
            else:
                add_unique(blocked, f"warning_budget_missing_field:{field}")

        if payload.get("schema_version") == "imperium.warning_budget.v0_1":
            passes.append("schema_version_matches_expected")
        else:
            add_unique(blocked, "warning_budget_schema_version_mismatch")

        if payload.get("act5_execution_ready") is False:
            passes.append("act5_execution_ready_is_false")
        else:
            add_unique(blocked, "act5_execution_ready_must_be_false")

        if payload.get("ready_for_agent_must_remain_false") is True:
            passes.append("ready_for_agent_must_remain_false_is_true")
        else:
            add_unique(blocked, "ready_for_agent_must_remain_false_must_be_true")

        classes = payload.get("warning_classes")
        class_ids: set[str] = set()
        if isinstance(classes, list):
            for idx, entry in enumerate(classes):
                if not isinstance(entry, dict):
                    add_unique(blocked, f"warning_class_not_object:{idx}")
                    continue
                class_id = entry.get("class_id")
                if not isinstance(class_id, str) or not class_id.strip():
                    add_unique(blocked, f"warning_class_missing_class_id:{idx}")
                    continue
                class_ids.add(class_id.strip())
        else:
            add_unique(blocked, "warning_classes_not_list")

        for class_id in REQUIRED_WARNING_CLASS_IDS:
            if class_id in class_ids:
                passes.append(f"warning_class_present:{class_id}")
            else:
                add_unique(blocked, f"missing_warning_class:{class_id}")

        rules = payload.get("blocker_rules")
        if isinstance(rules, list):
            flat_rules = "\n".join(str(item) for item in rules)
            for token in REQUIRED_BLOCKER_RULE_TOKENS:
                if token in flat_rules:
                    passes.append(f"blocker_rule_present:{token}")
                else:
                    add_unique(blocked, f"missing_blocker_rule:{token}")
        else:
            add_unique(blocked, "blocker_rules_not_list")

    if start_here_path.exists():
        start_text = start_here_path.read_text(encoding="utf-8")
        start_lower = start_text.lower()
        forbidden_hits = [pattern for pattern in FORBIDDEN_READY_PATTERNS if pattern in start_lower]
        if forbidden_hits:
            add_unique(blocked, f"start_here_claims_act5_ready:{'|'.join(forbidden_hits)}")
        else:
            passes.append("start_here_does_not_claim_act5_execution_ready")

        if "do not start act 5 self-build execution yet" in start_lower:
            passes.append("start_here_explicitly_blocks_act5_self_build_execution")
        else:
            add_unique(warnings, "start_here_missing_explicit_execution_block_phrase")

    if current_truth_path.exists():
        truth, truth_err = read_json_obj(current_truth_path)
        if truth_err:
            add_unique(blocked, truth_err)
        elif truth is not None:
            passes.append(f"file_exists:{CURRENT_TRUTH_PATH}")
            if truth.get("act5_execution_ready") is False:
                passes.append("current_truth_act5_execution_ready_is_false")
            else:
                add_unique(blocked, "current_truth_act5_execution_ready_must_be_false")
    else:
        add_unique(warnings, f"optional_file_missing:{CURRENT_TRUTH_PATH}")

    if synthesis_path.exists():
        synthesis_text = synthesis_path.read_text(encoding="utf-8")
        if "KIRO_ACT5_PREFIRE_READINESS_AUDIT_20260513.md" in synthesis_text:
            passes.append("synthesis_mentions_kiro_audit")
        else:
            add_unique(blocked, "synthesis_missing_kiro_audit_reference")

        if "READY_FOR_AGENT remains false" in synthesis_text:
            passes.append("synthesis_declares_ready_for_agent_false")
        else:
            add_unique(blocked, "synthesis_missing_ready_for_agent_false_statement")

    verdict = "PASS"
    if blocked:
        verdict = "BLOCKED"
    elif warnings:
        verdict = "WARN"

    return {
        "schema_version": SCHEMA_VERSION,
        "task_id": TASK_ID,
        "generated_at_utc": now_utc(),
        "repo_root": str(repo_root),
        "verdict": verdict,
        "passes": passes,
        "warnings": warnings,
        "blocked": blocked,
        "counts": {
            "pass": len(passes),
            "warn": len(warnings),
            "blocked": len(blocked),
        },
    }


def print_human(report: dict[str, Any], artifacts: dict[str, str]) -> None:
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

    print("\n=== VERDICT ===")
    print(report["verdict"])
    print(f"report: {artifacts['report']}")
    print(f"verdict_md: {artifacts['verdict']}")
    print(f"receipt: {artifacts['receipt']}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Check WARNING_BUDGET v0.1 policy coherence")
    parser.add_argument("--repo-root", default=".", help="Repository root")
    parser.add_argument("--human", action="store_true", help="Print PASS/WARN/BLOCKED sections")
    parser.add_argument("--json", action="store_true", help="Print JSON report")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    repo_root = Path(args.repo_root).resolve()

    report = build_report(repo_root)
    artifacts = write_artifacts(repo_root, report)

    if args.human or not args.json:
        print_human(report, artifacts)

    if args.json or not args.human:
        print(json.dumps(report, ensure_ascii=False, indent=2))

    return 2 if report["blocked"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
