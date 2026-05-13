#!/usr/bin/env python3
from __future__ import annotations

import argparse
import datetime as dt
import json
from pathlib import Path
from typing import Any

TASK_ID = "TASK-20260513-ADVISORY-INGEST-AND-MODERNIZATION-V0_1"
SCHEMA_VERSION = "imperium.advisory_ingest_modernization_check.v0_1"
RUNTIME_REL = ".imperium_runtime/astronomicon/advisory_ingest_modernization_check"
REPORT_NAME = "ADVISORY_INGEST_MODERNIZATION_CHECK_REPORT.json"
VERDICT_NAME = "ADVISORY_INGEST_MODERNIZATION_CHECK_VERDICT.md"
RECEIPT_NAME = "ADVISORY_INGEST_MODERNIZATION_CHECK_RECEIPT.json"

ADVISORY_RESPONSE_REL = (
    "ORGANS/ASTRONOMICON/REGISTRY/ADVISORY_RESPONSES/"
    "ADVISORY-RESPONSE-20260513-KIRO-ACT5-PREFIRE-V0_1.json"
)
MODERNIZATION_REL = (
    "ORGANS/ASTRONOMICON/REGISTRY/TASK_MODERNIZATIONS/"
    "TASK-MODERNIZATION-20260513-ACT5-PREFIRE-V0_1.json"
)
PREPARATION_TASKS_REL = (
    "ORGANS/ASTRONOMICON/REGISTRY/ARC5_PREFIRE/"
    "ARC5_PREFIRE_PREPARATION_TASKS_20260513.json"
)
KIRO_AUDIT_REL = "ORGANS/ASTRONOMICON/ADVISORY_BUFFER/KIRO/20260513/KIRO_ACT5_PREFIRE_READINESS_AUDIT_20260513.md"
WARNING_BUDGET_REL = "REGISTRY/WARNING_BUDGET.json"
START_HERE_REL = "START_HERE.md"
CURRENT_TRUTH_REL = "CURRENT_STATE/ARC5_PREFIRE_CURRENT_TRUTH_20260513.json"

EXPECTED_ADVISORY_RECORD = "ADVISORY-RESPONSE-20260513-KIRO-ACT5-PREFIRE-V0_1"
EXPECTED_MODERNIZATION_ID = "TASK-MODERNIZATION-20260513-ACT5-PREFIRE-V0_1"
EXPECTED_VISUAL_TASK = "TASK-20260513-VISUAL-FACTORY-MINIMUM-V0_1"
EXPECTED_INQ_TASK = "TASK-20260513-INQUISITION-V0_1-CONTRACT-V0_1"
EXPECTED_RFA_TASK = "TASK-20260513-READY-FOR-AGENT-GATE-PROOF-V0_1"

REQUIRED_TASK_IDS = {
    "TASK-20260513-FIRST-FOUR-ORGANS-ACT5-READINESS-V0_1",
    "TASK-20260513-WORK-SESSION-ADMINISTRATUM-ACK-V0_1",
    "TASK-20260513-SANCTUM-ACTION-REGISTRY-V0_1",
    "TASK-20260513-VISUAL-FACTORY-MINIMUM-V0_1",
    "TASK-20260513-INQUISITION-V0_1-CONTRACT-V0_1",
    "TASK-20260513-READY-FOR-AGENT-GATE-PROOF-V0_1",
}

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
        "# Advisory Ingest + Modernization Check v0.1",
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
        "schema_version": "imperium.advisory_ingest_modernization_check_receipt.v0_1",
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

    advisory_path = repo_root / ADVISORY_RESPONSE_REL
    modernization_path = repo_root / MODERNIZATION_REL
    prep_path = repo_root / PREPARATION_TASKS_REL
    kiro_path = repo_root / KIRO_AUDIT_REL
    warning_budget_path = repo_root / WARNING_BUDGET_REL
    start_here_path = repo_root / START_HERE_REL
    current_truth_path = repo_root / CURRENT_TRUTH_REL

    required_paths = {
        "advisory_response": advisory_path,
        "modernization": modernization_path,
        "preparation_tasks": prep_path,
        "kiro_audit_source": kiro_path,
        "warning_budget": warning_budget_path,
        "start_here": start_here_path,
    }
    for key, path in required_paths.items():
        if path.exists():
            passes.append(f"file_exists:{key}:{path.relative_to(repo_root).as_posix()}")
        else:
            add_unique(blocked, f"missing_required_file:{key}:{path.relative_to(repo_root).as_posix()}")

    advisory, advisory_err = read_json_obj(advisory_path)
    if advisory_err:
        add_unique(blocked, advisory_err)
        advisory = None

    modernization, modernization_err = read_json_obj(modernization_path)
    if modernization_err:
        add_unique(blocked, modernization_err)
        modernization = None

    prep, prep_err = read_json_obj(prep_path)
    if prep_err:
        add_unique(blocked, prep_err)
        prep = None

    if advisory is not None:
        if advisory.get("schema_version") == "imperium.advisory_response.v0_1":
            passes.append("advisory_schema_version_ok")
        else:
            add_unique(blocked, "advisory_schema_version_mismatch")

        if advisory.get("record_id") == EXPECTED_ADVISORY_RECORD:
            passes.append("advisory_record_id_ok")
        else:
            add_unique(blocked, "advisory_record_id_mismatch")

        source = advisory.get("source")
        if isinstance(source, dict):
            if source.get("source_authority") == "ADVISORY_ONLY_NOT_EXECUTION_AUTHORITY":
                passes.append("advisory_source_authority_non_execution_ok")
            else:
                add_unique(blocked, "advisory_source_authority_must_be_advisory_only")

            source_file = source.get("source_file")
            if source_file == KIRO_AUDIT_REL:
                passes.append("advisory_source_file_path_ok")
            else:
                add_unique(blocked, "advisory_source_file_path_mismatch")

            if source.get("source_status") == "RAW_ADVISORY_INPUT":
                passes.append("advisory_source_status_raw_input_ok")
            else:
                add_unique(warnings, "advisory_source_status_not_raw_input")
        else:
            add_unique(blocked, "advisory_source_not_object")

        if advisory.get("must_not_execute_directly") is True:
            passes.append("advisory_must_not_execute_directly_true")
        else:
            add_unique(blocked, "advisory_must_not_execute_directly_must_be_true")

        if advisory.get("ready_for_agent_must_remain_false") is True:
            passes.append("advisory_ready_for_agent_must_remain_false_true")
        else:
            add_unique(blocked, "advisory_ready_for_agent_must_remain_false_must_be_true")

        if advisory.get("act5_execution_ready") is False:
            passes.append("advisory_act5_execution_ready_false")
        else:
            add_unique(blocked, "advisory_act5_execution_ready_must_be_false")

        if advisory.get("must_not_execute_directly") is not True:
            add_unique(blocked, "advisory_direct_execution_forbidden")

    if modernization is not None:
        if modernization.get("schema_version") == "imperium.task_modernization.v0_1":
            passes.append("modernization_schema_version_ok")
        else:
            add_unique(blocked, "modernization_schema_version_mismatch")

        if modernization.get("modernization_id") == EXPECTED_MODERNIZATION_ID:
            passes.append("modernization_id_ok")
        else:
            add_unique(blocked, "modernization_id_mismatch")

        if modernization.get("status") == "MODERNIZATION_SKELETON_REGISTERED_PENDING_OWNER_APPROVAL":
            passes.append("modernization_status_pending_owner_approval_ok")
        else:
            add_unique(blocked, "modernization_status_must_be_pending_owner_approval")

        if modernization.get("owner_approval_required_before_execution") is True:
            passes.append("modernization_owner_approval_required_true")
        else:
            add_unique(blocked, "modernization_owner_approval_required_must_be_true")

        if modernization.get("act5_execution_ready") is False:
            passes.append("modernization_act5_execution_ready_false")
        else:
            add_unique(blocked, "modernization_act5_execution_ready_must_be_false")

        if modernization.get("ready_for_agent_status") is False:
            passes.append("modernization_ready_for_agent_false")
        else:
            add_unique(blocked, "modernization_ready_for_agent_status_must_be_false")

        if modernization.get("source_advisory_response") == EXPECTED_ADVISORY_RECORD:
            passes.append("modernization_source_advisory_link_ok")
        else:
            add_unique(blocked, "modernization_source_advisory_link_mismatch")

        steps = modernization.get("preparation_steps")
        if isinstance(steps, list) and steps:
            passes.append("modernization_preparation_steps_present")
            step_by_id = {
                item.get("step_id"): item
                for item in steps
                if isinstance(item, dict) and isinstance(item.get("step_id"), str)
            }
            step3 = step_by_id.get("STEP-03")
            if isinstance(step3, dict) and step3.get("status") == "CURRENT":
                passes.append("modernization_step3_marked_current")
            else:
                add_unique(warnings, "modernization_step3_not_marked_current")

            step7 = step_by_id.get("STEP-07")
            if isinstance(step7, dict) and step7.get("status") == "PENDING":
                passes.append("modernization_step7_visual_factory_pending")
            else:
                add_unique(blocked, "modernization_step7_must_be_pending")
        else:
            add_unique(blocked, "modernization_preparation_steps_missing_or_empty")

    if prep is not None:
        if prep.get("schema_version") == "imperium.arc5_prefire_preparation_tasks.v0_1":
            passes.append("preparation_schema_version_ok")
        else:
            add_unique(blocked, "preparation_schema_version_mismatch")

        if prep.get("status") == "PREFIRE_TASK_CANDIDATES_REGISTERED":
            passes.append("preparation_status_ok")
        else:
            add_unique(blocked, "preparation_status_mismatch")

        if prep.get("source_advisory_response") == EXPECTED_ADVISORY_RECORD:
            passes.append("preparation_source_advisory_ok")
        else:
            add_unique(blocked, "preparation_source_advisory_mismatch")

        if prep.get("source_modernization") == EXPECTED_MODERNIZATION_ID:
            passes.append("preparation_source_modernization_ok")
        else:
            add_unique(blocked, "preparation_source_modernization_mismatch")

        if prep.get("act5_execution_ready") is False:
            passes.append("preparation_act5_execution_ready_false")
        else:
            add_unique(blocked, "preparation_act5_execution_ready_must_be_false")

        if prep.get("ready_for_agent_status") is False:
            passes.append("preparation_ready_for_agent_false")
        else:
            add_unique(blocked, "preparation_ready_for_agent_status_must_be_false")

        candidates = prep.get("task_candidates")
        if isinstance(candidates, list) and candidates:
            passes.append("preparation_task_candidates_present")
            by_id: dict[str, dict[str, Any]] = {}
            for item in candidates:
                if isinstance(item, dict) and isinstance(item.get("task_id"), str):
                    by_id[item["task_id"]] = item

            missing_ids = sorted(REQUIRED_TASK_IDS.difference(set(by_id.keys())))
            if missing_ids:
                add_unique(blocked, f"preparation_missing_required_task_ids:{'|'.join(missing_ids)}")
            else:
                passes.append("preparation_contains_all_required_task_candidates")

            for task_id in sorted(REQUIRED_TASK_IDS):
                entry = by_id.get(task_id)
                if isinstance(entry, dict):
                    if entry.get("status") == "CANDIDATE_NOT_READY_FOR_EXECUTION":
                        passes.append(f"task_status_not_ready:{task_id}")
                    else:
                        add_unique(blocked, f"task_status_must_be_candidate_not_ready:{task_id}")

            visual = by_id.get(EXPECTED_VISUAL_TASK)
            if isinstance(visual, dict):
                if visual.get("execution_now_allowed") is False:
                    passes.append("visual_factory_candidate_execution_now_allowed_false")
                else:
                    add_unique(blocked, "visual_factory_candidate_must_not_execute_now")

                if visual.get("sequence_step") == 7:
                    passes.append("visual_factory_candidate_sequence_step_7")
                else:
                    add_unique(blocked, "visual_factory_candidate_sequence_step_must_be_7")

                if visual.get("execution_status") == "PLANNED_NOT_EXECUTED":
                    passes.append("visual_factory_candidate_planned_not_executed")
                else:
                    add_unique(warnings, "visual_factory_candidate_missing_planned_not_executed_marker")
            else:
                add_unique(blocked, "visual_factory_candidate_missing")

            inq = by_id.get(EXPECTED_INQ_TASK)
            if isinstance(inq, dict):
                forbidden = inq.get("forbidden_actions")
                if isinstance(forbidden, list) and any(
                    "Do not build full Inquisition now" in str(item) for item in forbidden
                ):
                    passes.append("inquisition_candidate_forbids_full_build_now")
                else:
                    add_unique(blocked, "inquisition_candidate_must_forbid_full_build_now")

                if inq.get("build_inquisition_now") is False:
                    passes.append("inquisition_candidate_build_now_false")
                else:
                    add_unique(blocked, "inquisition_candidate_build_inquisition_now_must_be_false")
            else:
                add_unique(blocked, "inquisition_contract_candidate_missing")

            rfa = by_id.get(EXPECTED_RFA_TASK)
            if isinstance(rfa, dict):
                depends_on = rfa.get("depends_on")
                if isinstance(depends_on, list) and "OWNER_STAGE_MAP_APPROVAL_REQUIRED" in depends_on:
                    passes.append("ready_for_agent_candidate_depends_on_owner_stage_map_approval")
                else:
                    add_unique(blocked, "ready_for_agent_candidate_missing_owner_stage_map_dependency")

                if rfa.get("owner_approval_required") is True:
                    passes.append("ready_for_agent_candidate_owner_approval_required_true")
                else:
                    add_unique(blocked, "ready_for_agent_candidate_owner_approval_required_must_be_true")

                if rfa.get("evidence_required_before_status_change") is True:
                    passes.append("ready_for_agent_candidate_evidence_required_true")
                else:
                    add_unique(blocked, "ready_for_agent_candidate_evidence_required_must_be_true")
            else:
                add_unique(blocked, "ready_for_agent_candidate_missing")
        else:
            add_unique(blocked, "preparation_task_candidates_missing_or_empty")

    if start_here_path.exists():
        text = start_here_path.read_text(encoding="utf-8").lower()
        hits = [p for p in FORBIDDEN_READY_PATTERNS if p in text]
        if hits:
            add_unique(blocked, f"start_here_claims_act5_ready:{'|'.join(hits)}")
        else:
            passes.append("start_here_does_not_claim_act5_execution_ready")

    if current_truth_path.exists():
        current_truth, current_truth_err = read_json_obj(current_truth_path)
        if current_truth_err:
            add_unique(blocked, current_truth_err)
        elif current_truth is not None:
            if current_truth.get("act5_execution_ready") is False:
                passes.append("current_truth_act5_execution_ready_false")
            else:
                add_unique(blocked, "current_truth_act5_execution_ready_must_be_false")

            if current_truth.get("ready_for_agent_status") is False:
                passes.append("current_truth_ready_for_agent_status_false")
            else:
                add_unique(blocked, "current_truth_ready_for_agent_status_must_be_false")

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
    parser = argparse.ArgumentParser(description="Check Act 5 advisory ingest + modernization skeleton coherence")
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
