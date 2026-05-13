#!/usr/bin/env python3
from __future__ import annotations

import argparse
import datetime as dt
import json
from pathlib import Path
from typing import Any

TASK_ID = "TASK-20260513-ACT4-FULL-REGISTRATION-CORRIDOR-SEED-V0_1"
STAGE_ID = "STAGE-001-ACT4-SCHEMAS-REGISTRIES-CHECKER-AND-INQUISITION-DRY-RUN-CANDIDATE-V0_1"
EXPECTED_HEAD = "cfe0c317172b8de8efff186bc9c0a4fa18dc96ad"
EXPECTED_TREE_URL = f"https://github.com/SoulsLike2313/Imperium-/tree/{EXPECTED_HEAD}"

STATUS_ENUM = {"PROVEN", "WARNING", "UNKNOWN", "BLOCKED"}
RAW_ADVISORY_STATUS = "RAW_ADVISORY_INPUT_NOT_YET_RECONCILED"
RAW_ADVISORY_STATUS_ALIAS = "REGISTERED_RAW_ADVISORY_NOT_RECONCILED"

CORRIDOR_PATH = "ORGANS/ASTRONOMICON/REGISTRY/CORRIDOR/ACT4_REGISTRATION_CORRIDOR_V0_1.json"
TASK_CANDIDATE_PATH = (
    "ORGANS/ASTRONOMICON/REGISTRY/TASK_CANDIDATES/"
    "TASK-CANDIDATE-20260513-BUILD-INQUISITION-V0_1-SELF-DESCRIPTIVE-ORGAN.json"
)
REVIEW_PACK_PATH = (
    "ORGANS/ASTRONOMICON/REGISTRY/REVIEW_PACKS/"
    "REVIEW-PACK-20260513-INQUISITION-V0_1-SELF-BUILD-ADVISORY-V0_1.json"
)
STAGE_MAP_PATH = (
    "ORGANS/ASTRONOMICON/REGISTRY/STAGE_MAPS/"
    "STAGE-MAP-DRAFT-20260513-INQUISITION-V0_1-SELF-BUILD-V0_1.json"
)
READY_GATE_PATH = (
    "ORGANS/ASTRONOMICON/REGISTRY/READY_FOR_AGENT/"
    "READY-FOR-AGENT-20260513-INQUISITION-V0_1-SELF-BUILD-BLOCKED-V0_1.json"
)
ADVISORY_REG_PATH = (
    "ORGANS/ASTRONOMICON/REGISTRY/ADVISORY_INPUTS/"
    "ADVISORY-20260513-KIRO-INQUISITION-SELF-BUILD-V0_1.json"
)

SCHEMA_PATHS = [
    "schemas/task_candidate.schema.json",
    "schemas/advisory_review_pack.schema.json",
    "schemas/advisory_response.schema.json",
    "schemas/task_modernization.schema.json",
    "schemas/stage_map.schema.json",
    "schemas/ready_for_agent.schema.json",
    "schemas/registration_corridor.schema.json",
]

ACT3_DEP_PATHS = [
    "ORGANS/ADMINISTRATUM/REGISTRY/ZONE_REGISTRY_V0_1.json",
    "ORGANS/ADMINISTRATUM/REGISTRY/TRUTH_SOURCE_REGISTRY_V0_1.json",
    "ORGANS/ADMINISTRATUM/REGISTRY/CAPABILITY_SPINE_V0_1.json",
    "ORGANS/ADMINISTRATUM/REGISTRY/WARNING_STALE_BASELINE_V0_1.json",
]

SUPPORT_REF_PATHS = [
    "REGISTRY/SCRIPT_REGISTRY.json",
    "REGISTRY/ARSENAL_TOOL_INDEX.json",
    "REGISTRY/ARSENAL_INSTALL_STATUS.json",
]

REQUIRED_REGISTRY_DIRS = [
    "ORGANS/ASTRONOMICON/REGISTRY/TASK_CANDIDATES",
    "ORGANS/ASTRONOMICON/REGISTRY/REVIEW_PACKS",
    "ORGANS/ASTRONOMICON/REGISTRY/ADVISORY_RESPONSES",
    "ORGANS/ASTRONOMICON/REGISTRY/TASK_MODERNIZATIONS",
    "ORGANS/ASTRONOMICON/REGISTRY/STAGE_MAPS",
    "ORGANS/ASTRONOMICON/REGISTRY/READY_FOR_AGENT",
]

RUNTIME_DIR = Path(".imperium_runtime/astronomicon/act4_registration_corridor_check")
RESULT_JSON_NAME = "ACT4_REGISTRATION_CORRIDOR_CHECK_RESULT.json"
VERDICT_MD_NAME = "ACT4_REGISTRATION_CORRIDOR_CHECK_VERDICT.md"
RECEIPT_JSON_NAME = "ACT4_REGISTRATION_CORRIDOR_CHECK_RECEIPT.json"



def now_utc() -> str:
    return dt.datetime.now(dt.timezone.utc).isoformat()



def add_unique(items: list[str], value: str) -> None:
    if value not in items:
        items.append(value)



def load_json(path: Path, tag: str, blockers: list[str]) -> dict[str, Any] | None:
    if not path.exists():
        add_unique(blockers, f"missing_file:{tag}:{path.as_posix()}")
        return None
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:  # noqa: BLE001
        add_unique(blockers, f"invalid_json:{tag}:{type(exc).__name__}")
        return None
    if not isinstance(payload, dict):
        add_unique(blockers, f"invalid_json_type:{tag}")
        return None
    return payload



def ensure_status(value: Any, tag: str, blockers: list[str], warnings: list[str]) -> None:
    if not isinstance(value, str) or value not in STATUS_ENUM:
        add_unique(blockers, f"invalid_status:{tag}")
        return
    if value in {"WARNING", "UNKNOWN"}:
        add_unique(warnings, f"status_not_proven:{tag}:{value}")



def check_schema_registry(repo_root: Path, blockers: list[str], warnings: list[str]) -> dict[str, Any]:
    path = repo_root / "schemas/schema_registry.json"
    payload = load_json(path, "schema_registry", blockers)
    if payload is None:
        return {"registered_count": 0}

    schemas = payload.get("schemas")
    if not isinstance(schemas, list):
        add_unique(blockers, "schema_registry_schemas_not_list")
        return {"registered_count": 0}

    schema_paths = {
        item.get("path")
        for item in schemas
        if isinstance(item, dict) and isinstance(item.get("path"), str)
    }

    for rel in SCHEMA_PATHS:
        if rel not in schema_paths:
            add_unique(blockers, f"schema_registry_missing_entry:{rel}")

    if payload.get("schema_version") != "imperium.schema_registry.v0_1":
        add_unique(warnings, "schema_registry_schema_version_unexpected")

    return {"registered_count": len(schema_paths)}



def check_corridor(payload: dict[str, Any], blockers: list[str], warnings: list[str]) -> dict[str, Any]:
    required = [
        "schema_version",
        "corridor_id",
        "task_id",
        "stage_id",
        "updated_at_utc",
        "owner_organ",
        "lifecycle_phases",
        "required_act3_dependencies",
        "ready_for_agent_gate_rules",
        "no_fake_green_rules",
        "status",
        "base_git_truth",
    ]
    for key in required:
        if key not in payload:
            add_unique(blockers, f"corridor_missing_field:{key}")

    if payload.get("schema_version") != "imperium.registration_corridor.v0_1":
        add_unique(blockers, "corridor_schema_version_mismatch")

    if payload.get("owner_organ") != "ASTRONOMICON":
        add_unique(blockers, "corridor_owner_organ_not_astronomicon")

    base_truth = payload.get("base_git_truth")
    if not isinstance(base_truth, dict):
        add_unique(blockers, "corridor_base_git_truth_not_object")
    else:
        if base_truth.get("head") != EXPECTED_HEAD:
            add_unique(blockers, "corridor_head_mismatch")
        if base_truth.get("exact_tree_url") != EXPECTED_TREE_URL:
            add_unique(blockers, "corridor_tree_url_mismatch")

    phases = payload.get("lifecycle_phases")
    if not isinstance(phases, list) or not phases:
        add_unique(blockers, "corridor_lifecycle_phases_not_list_or_empty")
        phases = []
    for idx, phase in enumerate(phases):
        tag = f"corridor_phase[{idx}]"
        if not isinstance(phase, dict):
            add_unique(blockers, f"{tag}:not_object")
            continue
        for key in ("phase_id", "required_inputs", "required_outputs", "status"):
            if key not in phase:
                add_unique(blockers, f"{tag}:missing_field:{key}")
        ensure_status(phase.get("status"), tag, blockers, warnings)

    deps = payload.get("required_act3_dependencies")
    if not isinstance(deps, list) or not deps:
        add_unique(blockers, "corridor_required_act3_dependencies_not_list_or_empty")
    else:
        for rel in ACT3_DEP_PATHS:
            if rel not in deps:
                add_unique(blockers, f"corridor_missing_act3_dependency:{rel}")

    return {"phase_count": len(phases)}



def check_task_candidate(
    payload: dict[str, Any], blockers: list[str], warnings: list[str], repo_root: Path
) -> dict[str, Any]:
    required = [
        "schema_version",
        "task_id",
        "source_general_task_id",
        "title",
        "status",
        "goal",
        "scope",
        "non_goals",
        "owner_intent",
        "base_git_truth",
        "required_capabilities",
        "allowed_scripts",
        "forbidden_tools",
        "related_advisory_inputs",
        "risks",
        "open_questions",
        "next_required_phase",
    ]
    for key in required:
        if key not in payload:
            add_unique(blockers, f"task_candidate_missing_field:{key}")

    if payload.get("schema_version") != "imperium.task_candidate.v0_1":
        add_unique(blockers, "task_candidate_schema_version_mismatch")

    if payload.get("status") != "REGISTERED_CANDIDATE_NEEDS_REVIEW":
        add_unique(blockers, "task_candidate_status_unexpected")

    if payload.get("next_required_phase") != "REVIEW_PACK_REQUIRED":
        add_unique(blockers, "task_candidate_next_phase_unexpected")

    base_truth = payload.get("base_git_truth")
    if isinstance(base_truth, dict):
        if base_truth.get("head") != EXPECTED_HEAD:
            add_unique(blockers, "task_candidate_head_mismatch")
    else:
        add_unique(blockers, "task_candidate_base_git_truth_not_object")

    advisory_inputs = payload.get("related_advisory_inputs")
    if isinstance(advisory_inputs, list):
        if ADVISORY_REG_PATH not in advisory_inputs:
            add_unique(blockers, "task_candidate_missing_advisory_registration_ref")
    else:
        add_unique(blockers, "task_candidate_related_advisory_inputs_not_list")

    tooling_refs = payload.get("tooling_refs")
    if isinstance(tooling_refs, list):
        for rel in SUPPORT_REF_PATHS:
            if rel not in tooling_refs:
                add_unique(warnings, f"task_candidate_missing_tooling_ref:{rel}")
            elif not (repo_root / rel).exists():
                add_unique(blockers, f"task_candidate_tooling_ref_missing_file:{rel}")
    else:
        add_unique(warnings, "task_candidate_tooling_refs_not_list")

    return {
        "required_capabilities_count": len(payload.get("required_capabilities", []))
        if isinstance(payload.get("required_capabilities"), list)
        else 0
    }



def check_review_pack(payload: dict[str, Any], blockers: list[str]) -> dict[str, Any]:
    required = [
        "schema_version",
        "review_pack_id",
        "task_id",
        "status",
        "reviewer_target",
        "source_task_candidate",
        "context_files",
        "questions",
        "constraints",
        "required_response_format",
        "no_fake_green_rules",
    ]
    for key in required:
        if key not in payload:
            add_unique(blockers, f"review_pack_missing_field:{key}")

    if payload.get("schema_version") != "imperium.advisory_review_pack.v0_1":
        add_unique(blockers, "review_pack_schema_version_mismatch")

    if payload.get("status") != "READY_TO_EXPORT":
        add_unique(blockers, "review_pack_status_unexpected")

    src = payload.get("source_task_candidate")
    if src != TASK_CANDIDATE_PATH:
        add_unique(blockers, "review_pack_source_task_candidate_mismatch")

    if payload.get("raw_advisory_input") != "RAW_ADVISORY_INPUT_NOT_YET_RECONCILED":
        add_unique(blockers, "review_pack_raw_advisory_flag_missing")

    return {
        "questions_count": len(payload.get("questions", []))
        if isinstance(payload.get("questions"), list)
        else 0
    }



def check_stage_map(payload: dict[str, Any], blockers: list[str], warnings: list[str]) -> dict[str, Any]:
    required = ["schema_version", "stage_map_id", "task_id", "status", "stages"]
    for key in required:
        if key not in payload:
            add_unique(blockers, f"stage_map_missing_field:{key}")

    if payload.get("schema_version") != "imperium.stage_map.v0_1":
        add_unique(blockers, "stage_map_schema_version_mismatch")

    status = payload.get("status")
    if status != "DRAFT_NEEDS_REVIEW":
        add_unique(blockers, "stage_map_status_unexpected")
    else:
        add_unique(warnings, "stage_map_is_draft_needs_review")

    stages = payload.get("stages")
    if not isinstance(stages, list) or not stages:
        add_unique(blockers, "stage_map_stages_not_list_or_empty")
        stages = []

    for idx, stage in enumerate(stages):
        tag = f"stage_map_stage[{idx}]"
        if not isinstance(stage, dict):
            add_unique(blockers, f"{tag}:not_object")
            continue
        for key in (
            "stage_id",
            "goal",
            "inputs",
            "outputs",
            "allowed_paths",
            "forbidden_paths",
            "required_scripts",
            "required_capabilities",
            "checks",
            "receipts",
            "owner_decision_gates",
            "pass_criteria",
            "fail_criteria",
            "bundle_policy",
        ):
            if key not in stage:
                add_unique(blockers, f"{tag}:missing_field:{key}")

    return {"stages_count": len(stages)}



def check_ready_gate(payload: dict[str, Any], blockers: list[str], warnings: list[str]) -> dict[str, Any]:
    required = [
        "schema_version",
        "ready_id",
        "task_id",
        "stage_map_id",
        "status",
        "ready_for_agent",
        "blocking_conditions",
        "evidence_refs",
        "required_checks",
        "owner_approval",
        "no_fake_green_verdict",
    ]
    for key in required:
        if key not in payload:
            add_unique(blockers, f"ready_gate_missing_field:{key}")

    if payload.get("schema_version") != "imperium.ready_for_agent.v0_1":
        add_unique(blockers, "ready_gate_schema_version_mismatch")

    if payload.get("status") != "BLOCKED_PENDING_REVIEW_AND_MODERNIZATION":
        add_unique(blockers, "ready_gate_status_unexpected")

    if payload.get("ready_for_agent") is not False:
        add_unique(blockers, "ready_gate_ready_for_agent_must_be_false")

    owner_approval = payload.get("owner_approval")
    if not isinstance(owner_approval, dict):
        add_unique(blockers, "ready_gate_owner_approval_not_object")
    else:
        if owner_approval.get("required") is not True:
            add_unique(blockers, "ready_gate_owner_approval_required_not_true")
        if owner_approval.get("granted") is not False:
            add_unique(blockers, "ready_gate_owner_approval_granted_not_false")

    blocking_conditions = payload.get("blocking_conditions")
    if not isinstance(blocking_conditions, list) or len(blocking_conditions) < 3:
        add_unique(blockers, "ready_gate_blocking_conditions_insufficient")

    if payload.get("no_fake_green_verdict") != "READY_FOR_AGENT_FALSE_BY_DESIGN":
        add_unique(warnings, "ready_gate_no_fake_green_verdict_not_expected_phrase")

    return {
        "blocking_conditions_count": len(blocking_conditions)
        if isinstance(blocking_conditions, list)
        else 0
    }



def check_advisory_registration(payload: dict[str, Any], blockers: list[str], warnings: list[str]) -> dict[str, Any]:
    status = payload.get("status")
    if status == RAW_ADVISORY_STATUS:
        pass
    elif status == RAW_ADVISORY_STATUS_ALIAS:
        add_unique(warnings, "advisory_status_alias_detected")
    else:
        add_unique(blockers, f"advisory_status_invalid:{status}")

    if payload.get("not_a_claim_of_implementation") is not True:
        add_unique(blockers, "advisory_missing_not_a_claim_of_implementation")

    if payload.get("owner_decision_required_before_doctrine") is not True:
        add_unique(blockers, "advisory_missing_owner_decision_required_before_doctrine")

    return {"status": status}



def render_verdict_md(report: dict[str, Any]) -> str:
    lines = [
        "# ACT4 REGISTRATION CORRIDOR CHECK VERDICT",
        "",
        f"- task_id: {TASK_ID}",
        f"- stage_id: {STAGE_ID}",
        f"- timestamp_utc: {report['timestamp_utc']}",
        f"- repo_root: {report['repo_root']}",
        f"- expected_head: {EXPECTED_HEAD}",
        f"- verdict: {report['verdict']}",
        f"- blockers: {report['counts']['blockers']}",
        f"- warnings: {report['counts']['warnings']}",
        "",
        "## Checked Files",
        f"- corridor: {CORRIDOR_PATH}",
        f"- task_candidate: {TASK_CANDIDATE_PATH}",
        f"- review_pack: {REVIEW_PACK_PATH}",
        f"- stage_map: {STAGE_MAP_PATH}",
        f"- ready_gate: {READY_GATE_PATH}",
        f"- advisory_registration: {ADVISORY_REG_PATH}",
    ]

    if report["blockers"]:
        lines.append("")
        lines.append("## Blockers")
        for item in report["blockers"]:
            lines.append(f"- {item}")

    if report["warnings"]:
        lines.append("")
        lines.append("## Warnings")
        for item in report["warnings"]:
            lines.append(f"- {item}")

    lines.append("")
    lines.append(f"=== DONE: ACT4 CORRIDOR CHECK {report['verdict']} ===")
    return "\n".join(lines) + "\n"



def run_check(repo_root: Path) -> dict[str, Any]:
    blockers: list[str] = []
    warnings: list[str] = []
    details: dict[str, Any] = {}

    for rel in REQUIRED_REGISTRY_DIRS:
        if not (repo_root / rel).is_dir():
            add_unique(blockers, f"missing_registry_dir:{rel}")

    for rel in ACT3_DEP_PATHS + SUPPORT_REF_PATHS + SCHEMA_PATHS:
        if not (repo_root / rel).exists():
            add_unique(blockers, f"missing_required_ref:{rel}")

    details["schema_registry"] = check_schema_registry(repo_root, blockers, warnings)

    corridor = load_json(repo_root / CORRIDOR_PATH, "corridor", blockers)
    task_candidate = load_json(repo_root / TASK_CANDIDATE_PATH, "task_candidate", blockers)
    review_pack = load_json(repo_root / REVIEW_PACK_PATH, "review_pack", blockers)
    stage_map = load_json(repo_root / STAGE_MAP_PATH, "stage_map", blockers)
    ready_gate = load_json(repo_root / READY_GATE_PATH, "ready_gate", blockers)
    advisory_reg = load_json(repo_root / ADVISORY_REG_PATH, "advisory_registration", blockers)

    if corridor is not None:
        details["corridor"] = check_corridor(corridor, blockers, warnings)

    if task_candidate is not None:
        details["task_candidate"] = check_task_candidate(task_candidate, blockers, warnings, repo_root)

    if review_pack is not None:
        details["review_pack"] = check_review_pack(review_pack, blockers)

    if stage_map is not None:
        details["stage_map"] = check_stage_map(stage_map, blockers, warnings)

    if ready_gate is not None:
        details["ready_gate"] = check_ready_gate(ready_gate, blockers, warnings)

    if advisory_reg is not None:
        details["advisory_registration"] = check_advisory_registration(advisory_reg, blockers, warnings)

    if blockers:
        verdict = "BLOCKED"
    elif warnings:
        verdict = "PASS_WITH_WARNINGS"
    else:
        verdict = "PASS"

    runtime_dir = (repo_root / RUNTIME_DIR).resolve()
    runtime_dir.mkdir(parents=True, exist_ok=True)

    result_json = runtime_dir / RESULT_JSON_NAME
    verdict_md = runtime_dir / VERDICT_MD_NAME
    receipt_json = runtime_dir / RECEIPT_JSON_NAME

    report = {
        "schema_version": "imperium.act4_registration_corridor_check.v0_1",
        "timestamp_utc": now_utc(),
        "task_id": TASK_ID,
        "stage_id": STAGE_ID,
        "repo_root": str(repo_root),
        "expected_head": EXPECTED_HEAD,
        "expected_tree_url": EXPECTED_TREE_URL,
        "verdict": verdict,
        "blockers": blockers,
        "warnings": warnings,
        "counts": {
            "blockers": len(blockers),
            "warnings": len(warnings),
            "schemas_expected": len(SCHEMA_PATHS),
            "act3_deps_expected": len(ACT3_DEP_PATHS),
        },
        "details": details,
        "outputs": {
            "result_json": str(result_json),
            "verdict_md": str(verdict_md),
            "receipt_json": str(receipt_json),
        },
    }

    result_json.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    verdict_md.write_text(render_verdict_md(report), encoding="utf-8")

    receipt = {
        "schema_version": "imperium.receipt.v0_1",
        "receipt_id": "RECEIPT-ACT4-REGISTRATION-CORRIDOR-CHECK-V0_1",
        "receipt_type": "act4_registration_corridor_check",
        "task_id": TASK_ID,
        "stage_id": STAGE_ID,
        "run_id": None,
        "issuer": "VM2_SERVITOR",
        "created_at_utc": now_utc(),
        "command": "python3 TOOLS/check_act4_registration_corridor_v0_1.py --repo-root . --human",
        "inputs": [
            CORRIDOR_PATH,
            TASK_CANDIDATE_PATH,
            REVIEW_PACK_PATH,
            STAGE_MAP_PATH,
            READY_GATE_PATH,
            ADVISORY_REG_PATH,
            "schemas/schema_registry.json",
        ]
        + SCHEMA_PATHS
        + ACT3_DEP_PATHS
        + SUPPORT_REF_PATHS,
        "outputs": [
            str(result_json.relative_to(repo_root)),
            str(verdict_md.relative_to(repo_root)),
            str(receipt_json.relative_to(repo_root)),
        ],
        "verdict": verdict,
        "warnings": warnings,
        "blockers": blockers,
        "evidence_paths": [
            str(result_json.relative_to(repo_root)),
            str(verdict_md.relative_to(repo_root)),
        ],
        "git_truth_ref": "ORGANS/ADMINISTRATUM/REGISTRY/TRUTH_SOURCE_REGISTRY_V0_1.json",
    }
    receipt_json.write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    return report



def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Check Act 4 full registration corridor seed v0.1")
    parser.add_argument("--repo-root", default=".", help="Repository root path")
    parser.add_argument("--human", action="store_true", help="Print readable summary")
    return parser.parse_args()



def print_human(report: dict[str, Any]) -> None:
    print("=== ACT4 FULL REGISTRATION CORRIDOR CHECK ===")
    print(f"repo_root: {report['repo_root']}")
    print(f"expected_head: {report['expected_head']}")
    print(f"verdict: {report['verdict']}")
    print(f"blockers: {report['counts']['blockers']}")
    print(f"warnings: {report['counts']['warnings']}")



def main() -> int:
    args = parse_args()
    repo_root = Path(args.repo_root).resolve()
    report = run_check(repo_root)
    if args.human:
        print_human(report)
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0 if report["counts"]["blockers"] == 0 else 2


if __name__ == "__main__":
    raise SystemExit(main())
