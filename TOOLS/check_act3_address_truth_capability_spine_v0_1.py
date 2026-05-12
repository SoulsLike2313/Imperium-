#!/usr/bin/env python3
from __future__ import annotations

import argparse
import datetime as dt
import json
from pathlib import Path
from typing import Any

TASK_ID = "TASK-20260513-ACT3-ADDRESS-TRUTH-CAPABILITY-SPINE-SEED-V0_1"
EXPECTED_HEAD = "36ffba1883d895d3f0a880de6b72cd5046be2c24"
STATUS_ENUM = {"PROVEN", "WARNING", "UNKNOWN", "BLOCKED"}
RAW_ADVISORY_STATUS_REQUIRED = "RAW_ADVISORY_INPUT_NOT_YET_RECONCILED"
RAW_ADVISORY_STATUS_ALIAS = "REGISTERED_RAW_ADVISORY_NOT_RECONCILED"

REGISTRY_PATHS = {
    "zone_registry": "ORGANS/ADMINISTRATUM/REGISTRY/ZONE_REGISTRY_V0_1.json",
    "truth_source_registry": "ORGANS/ADMINISTRATUM/REGISTRY/TRUTH_SOURCE_REGISTRY_V0_1.json",
    "capability_spine": "ORGANS/ADMINISTRATUM/REGISTRY/CAPABILITY_SPINE_V0_1.json",
    "warning_stale_baseline": "ORGANS/ADMINISTRATUM/REGISTRY/WARNING_STALE_BASELINE_V0_1.json",
}

SCHEMA_PATHS = {
    "organ_contract_schema": "schemas/organ_contract.schema.json",
    "organ_self_report_schema": "schemas/organ_self_report.schema.json",
}

ADVISORY_REG_PATH = (
    "ORGANS/ASTRONOMICON/REGISTRY/ADVISORY_INPUTS/"
    "ADVISORY-20260513-KIRO-INQUISITION-SELF-BUILD-V0_1.json"
)

RUNTIME_DIR = Path(
    ".imperium_runtime/administratum/act3_address_truth_capability_spine_check"
)
RESULT_JSON_NAME = "ACT3_ADDRESS_TRUTH_CAPABILITY_SPINE_CHECK_RESULT.json"
VERDICT_MD_NAME = "ACT3_ADDRESS_TRUTH_CAPABILITY_SPINE_CHECK_VERDICT.md"
RECEIPT_JSON_NAME = "ACT3_ADDRESS_TRUTH_CAPABILITY_SPINE_CHECK_RECEIPT.json"


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


def ensure_status(
    value: Any,
    tag: str,
    blockers: list[str],
    warnings: list[str],
    allow_unknown_warning: bool = True,
) -> None:
    if not isinstance(value, str) or value not in STATUS_ENUM:
        add_unique(blockers, f"invalid_status:{tag}")
        return
    if value == "UNKNOWN" and allow_unknown_warning:
        add_unique(warnings, f"unknown_status:{tag}")
    if value == "WARNING":
        add_unique(warnings, f"warning_status:{tag}")


def check_zone_registry(
    payload: dict[str, Any], blockers: list[str], warnings: list[str]
) -> dict[str, Any]:
    required_top = ["schema_version", "updated_at_utc", "task_id", "zones"]
    for key in required_top:
        if key not in payload:
            add_unique(blockers, f"zone_registry_missing_field:{key}")

    zones = payload.get("zones")
    if not isinstance(zones, list):
        add_unique(blockers, "zone_registry_zones_not_list")
        return {"zones_count": 0}

    required_zone_fields = [
        "zone_id",
        "git_tracked_expected",
        "local_only",
        "purpose",
        "allowed_writes",
        "forbidden_writes",
        "receipt_policy",
        "stale_policy",
        "status",
    ]

    for idx, zone in enumerate(zones):
        tag = f"zone_registry:zone[{idx}]"
        if not isinstance(zone, dict):
            add_unique(blockers, f"{tag}:not_object")
            continue
        for key in required_zone_fields:
            if key not in zone:
                add_unique(blockers, f"{tag}:missing_field:{key}")

        gte = zone.get("git_tracked_expected")
        if gte not in {True, False, "unknown"}:
            add_unique(blockers, f"{tag}:invalid_git_tracked_expected")
        if not isinstance(zone.get("local_only"), bool):
            add_unique(blockers, f"{tag}:local_only_not_bool")

        for arr_key in ("allowed_writes", "forbidden_writes"):
            arr = zone.get(arr_key)
            if not isinstance(arr, list) or not all(isinstance(x, str) for x in arr):
                add_unique(blockers, f"{tag}:{arr_key}_not_string_list")

        ensure_status(zone.get("status"), tag, blockers, warnings)

    return {"zones_count": len(zones)}


def check_truth_registry(
    payload: dict[str, Any], blockers: list[str], warnings: list[str]
) -> dict[str, Any]:
    required_top = [
        "schema_version",
        "updated_at_utc",
        "task_id",
        "current_baseline_head",
        "git_truth",
        "authority",
        "truth_precedence",
        "status",
    ]
    for key in required_top:
        if key not in payload:
            add_unique(blockers, f"truth_source_registry_missing_field:{key}")

    current_head = payload.get("current_baseline_head")
    if current_head != EXPECTED_HEAD:
        add_unique(
            blockers,
            f"baseline_head_mismatch:expected={EXPECTED_HEAD}:actual={current_head}",
        )

    git_truth = payload.get("git_truth")
    if not isinstance(git_truth, dict):
        add_unique(blockers, "truth_source_registry_git_truth_not_object")
    else:
        for key in (
            "repo",
            "head_sha",
            "commit_count",
            "latest_commit_oneline",
            "exact_tree_url",
        ):
            if key not in git_truth:
                add_unique(blockers, f"truth_source_registry_git_truth_missing:{key}")
        if git_truth.get("head_sha") != EXPECTED_HEAD:
            add_unique(
                blockers,
                f"git_truth_head_mismatch:expected={EXPECTED_HEAD}:actual={git_truth.get('head_sha')}",
            )
        tree_url = str(git_truth.get("exact_tree_url", ""))
        if EXPECTED_HEAD not in tree_url:
            add_unique(blockers, "truth_source_registry_tree_url_missing_expected_head")

    precedence = payload.get("truth_precedence")
    if not isinstance(precedence, list) or not precedence:
        add_unique(blockers, "truth_source_registry_truth_precedence_not_list_or_empty")
        precedence = []
    for idx, item in enumerate(precedence):
        tag = f"truth_source_registry:truth_precedence[{idx}]"
        if not isinstance(item, dict):
            add_unique(blockers, f"{tag}:not_object")
            continue
        for key in ("rank", "source", "rule", "evidence_ref", "status"):
            if key not in item:
                add_unique(blockers, f"{tag}:missing_field:{key}")
        ensure_status(item.get("status"), tag, blockers, warnings)

    authority = payload.get("authority")
    if not isinstance(authority, dict):
        add_unique(blockers, "truth_source_registry_authority_not_object")
    else:
        if authority.get("commit_authority") != "PC_ONLY":
            add_unique(blockers, "truth_source_registry_commit_authority_not_pc_only")
        if authority.get("push_authority") != "PC_ONLY":
            add_unique(blockers, "truth_source_registry_push_authority_not_pc_only")
        if authority.get("vm2_commit_allowed") is not False:
            add_unique(blockers, "truth_source_registry_vm2_commit_allowed_not_false")
        if authority.get("vm2_push_allowed") is not False:
            add_unique(blockers, "truth_source_registry_vm2_push_allowed_not_false")

    ensure_status(payload.get("status"), "truth_source_registry", blockers, warnings)
    return {"truth_precedence_count": len(precedence)}


def check_capability_spine(
    payload: dict[str, Any],
    blockers: list[str],
    warnings: list[str],
    repo_root: Path,
) -> dict[str, Any]:
    required_top = [
        "schema_version",
        "updated_at_utc",
        "task_id",
        "support_layers",
        "allowed_scripts",
        "owner_gated_tools",
        "contour_specific_tools",
        "unknown_capabilities",
        "required_future_task_stage_run_fields",
        "install_status_requirements",
        "status",
    ]
    for key in required_top:
        if key not in payload:
            add_unique(blockers, f"capability_spine_missing_field:{key}")

    support = payload.get("support_layers")
    refs_checked: list[str] = []
    if not isinstance(support, dict):
        add_unique(blockers, "capability_spine_support_layers_not_object")
    else:
        for key in (
            "script_registry_ref",
            "arsenal_tool_index_ref",
            "arsenal_install_status_ref",
        ):
            ref = support.get(key)
            if not isinstance(ref, str) or not ref.strip():
                add_unique(blockers, f"capability_spine_missing_ref:{key}")
                continue
            refs_checked.append(ref)
            if not (repo_root / ref).exists():
                add_unique(blockers, f"capability_spine_ref_missing:{key}:{ref}")

    allowed_scripts = payload.get("allowed_scripts")
    if not isinstance(allowed_scripts, list):
        add_unique(blockers, "capability_spine_allowed_scripts_not_list")
        allowed_scripts = []

    script_registry_ref = None
    if isinstance(support, dict):
        script_registry_ref = support.get("script_registry_ref")
    script_ids: set[str] = set()
    if isinstance(script_registry_ref, str):
        sr_payload = load_json(repo_root / script_registry_ref, "script_registry_ref", blockers)
        if isinstance(sr_payload, dict):
            scripts = sr_payload.get("scripts")
            if isinstance(scripts, list):
                for item in scripts:
                    if isinstance(item, dict):
                        sid = item.get("script_id")
                        if isinstance(sid, str):
                            script_ids.add(sid)

    for sid in allowed_scripts:
        if not isinstance(sid, str):
            add_unique(blockers, "capability_spine_allowed_scripts_non_string")
            continue
        if script_ids and sid not in script_ids:
            add_unique(warnings, f"capability_spine:allowed_script_not_in_registry:{sid}")

    future_fields = payload.get("required_future_task_stage_run_fields")
    required_fields = {
        "required_capabilities",
        "allowed_scripts",
        "allowed_tools",
        "forbidden_tools",
        "tooling_refs",
        "install_status_requirements",
    }
    if not isinstance(future_fields, list):
        add_unique(blockers, "capability_spine_required_fields_not_list")
    else:
        missing = required_fields - {x for x in future_fields if isinstance(x, str)}
        for item in sorted(missing):
            add_unique(blockers, f"capability_spine_missing_future_field:{item}")

    future_needs = payload.get("kiro_future_needs", [])
    if isinstance(future_needs, list):
        for idx, item in enumerate(future_needs):
            tag = f"capability_spine:kiro_future_needs[{idx}]"
            if not isinstance(item, dict):
                add_unique(blockers, f"{tag}:not_object")
                continue
            for key in ("capability_id", "description", "status"):
                if key not in item:
                    add_unique(blockers, f"{tag}:missing_field:{key}")
            ensure_status(item.get("status"), tag, blockers, warnings)

    ensure_status(payload.get("status"), "capability_spine", blockers, warnings)
    return {
        "allowed_scripts_count": len(allowed_scripts),
        "refs_checked": refs_checked,
    }


def check_warning_baseline(
    payload: dict[str, Any], blockers: list[str], warnings: list[str]
) -> dict[str, Any]:
    required_top = [
        "schema_version",
        "updated_at_utc",
        "task_id",
        "baseline_head",
        "categories",
        "status",
    ]
    for key in required_top:
        if key not in payload:
            add_unique(blockers, f"warning_stale_baseline_missing_field:{key}")

    baseline_head = payload.get("baseline_head")
    if baseline_head != EXPECTED_HEAD:
        add_unique(
            blockers,
            f"warning_baseline_head_mismatch:expected={EXPECTED_HEAD}:actual={baseline_head}",
        )

    categories = payload.get("categories")
    if not isinstance(categories, list) or not categories:
        add_unique(blockers, "warning_stale_baseline_categories_not_list_or_empty")
        categories = []
    for idx, item in enumerate(categories):
        tag = f"warning_stale_baseline:categories[{idx}]"
        if not isinstance(item, dict):
            add_unique(blockers, f"{tag}:not_object")
            continue
        for key in ("category_id", "description", "status"):
            if key not in item:
                add_unique(blockers, f"{tag}:missing_field:{key}")
        ensure_status(item.get("status"), tag, blockers, warnings)

    required_categories = {
        "WARN-ENCODING-MOJIBAKE",
        "WARN-STALE-FILE-RISK",
        "WARN-FLOATING-MASTER-RISK",
        "WARN-MISSING-REGISTRY-REFERENCE",
        "WARN-PATH-MISMATCH-PC-VM2",
        "WARN-LOCAL-ONLY-MISUSED-AS-GIT-TRUTH",
        "WARN-UNTRACKED-TOOL-RISK",
        "WARN-WARNING-FLOOD-RISK",
        "WARN-UNKNOWN-INSTALL-STATUS",
        "WARN-ORPHAN-SCRIPT-TOOL",
        "WARN-FAKE-GREEN-RISK",
        "WARN-RAW-ADVISORY-AS-DOCTRINE",
        "WARN-STALE-BASELINE-HEAD",
        "WARN-DIRTY-VM2-WORKTREE",
    }
    present_categories = {
        item.get("category_id") for item in categories if isinstance(item, dict)
    }
    for missing in sorted(required_categories - present_categories):
        add_unique(blockers, f"warning_category_missing:{missing}")

    ensure_status(payload.get("status"), "warning_stale_baseline", blockers, warnings)
    return {"categories_count": len(categories)}


def check_advisory_registration(
    repo_root: Path, blockers: list[str], warnings: list[str]
) -> dict[str, Any]:
    advisory_payload = load_json(repo_root / ADVISORY_REG_PATH, "advisory_registration", blockers)
    if advisory_payload is None:
        return {"status": "MISSING"}

    status_value = advisory_payload.get("status")
    if status_value == RAW_ADVISORY_STATUS_REQUIRED:
        pass
    elif status_value == RAW_ADVISORY_STATUS_ALIAS:
        add_unique(
            warnings,
            "advisory_status_alias_detected:REGISTERED_RAW_ADVISORY_NOT_RECONCILED",
        )
    else:
        add_unique(
            blockers,
            f"advisory_status_not_raw:{status_value}",
        )

    if advisory_payload.get("not_a_claim_of_implementation") is not True:
        add_unique(blockers, "advisory_registration_missing_not_a_claim_flag")

    return {
        "status": status_value,
        "path": ADVISORY_REG_PATH,
    }


def render_verdict_md(report: dict[str, Any]) -> str:
    lines = [
        "# ACT3 ADDRESS/TRUTH/CAPABILITY SPINE CHECK VERDICT",
        "",
        f"- task_id: {TASK_ID}",
        f"- timestamp_utc: {report['timestamp_utc']}",
        f"- repo_root: {report['repo_root']}",
        f"- verdict: {report['verdict']}",
        f"- blockers: {report['counts']['blockers']}",
        f"- warnings: {report['counts']['warnings']}",
        f"- expected_baseline_head: {EXPECTED_HEAD}",
        "",
        "## Loaded Files",
    ]
    for key, path in REGISTRY_PATHS.items():
        lines.append(f"- {key}: {path}")
    lines.append("- organ_contract_schema: schemas/organ_contract.schema.json")
    lines.append("- organ_self_report_schema: schemas/organ_self_report.schema.json")
    lines.append(f"- advisory_registration: {ADVISORY_REG_PATH}")

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
    lines.append(f"=== DONE: ACT3 CHECK {report['verdict']} ===")
    return "\n".join(lines) + "\n"


def run_check(repo_root: Path) -> dict[str, Any]:
    blockers: list[str] = []
    warnings: list[str] = []
    details: dict[str, Any] = {}

    loaded_payloads: dict[str, dict[str, Any]] = {}
    for key, rel in REGISTRY_PATHS.items():
        payload = load_json(repo_root / rel, key, blockers)
        if payload is not None:
            loaded_payloads[key] = payload

    for key, rel in SCHEMA_PATHS.items():
        schema_payload = load_json(repo_root / rel, key, blockers)
        if schema_payload is not None:
            if schema_payload.get("type") != "object":
                add_unique(warnings, f"schema_not_object_type:{key}")

    details["advisory_registration"] = check_advisory_registration(
        repo_root, blockers, warnings
    )

    if "zone_registry" in loaded_payloads:
        details["zone_registry"] = check_zone_registry(
            loaded_payloads["zone_registry"], blockers, warnings
        )

    if "truth_source_registry" in loaded_payloads:
        details["truth_source_registry"] = check_truth_registry(
            loaded_payloads["truth_source_registry"], blockers, warnings
        )

    if "capability_spine" in loaded_payloads:
        details["capability_spine"] = check_capability_spine(
            loaded_payloads["capability_spine"], blockers, warnings, repo_root
        )

    if "warning_stale_baseline" in loaded_payloads:
        details["warning_stale_baseline"] = check_warning_baseline(
            loaded_payloads["warning_stale_baseline"], blockers, warnings
        )

    if blockers:
        verdict = "BLOCKED"
    elif warnings:
        verdict = "PASS_WITH_WARNINGS"
    else:
        verdict = "PASS"

    runtime_dir = (repo_root / RUNTIME_DIR).resolve()
    runtime_dir.mkdir(parents=True, exist_ok=True)

    result_json_path = runtime_dir / RESULT_JSON_NAME
    verdict_md_path = runtime_dir / VERDICT_MD_NAME
    receipt_json_path = runtime_dir / RECEIPT_JSON_NAME

    report = {
        "schema_version": "imperium.act3_address_truth_capability_spine_check.v0_1",
        "timestamp_utc": now_utc(),
        "task_id": TASK_ID,
        "repo_root": str(repo_root),
        "expected_head": EXPECTED_HEAD,
        "verdict": verdict,
        "blockers": blockers,
        "warnings": warnings,
        "counts": {
            "blockers": len(blockers),
            "warnings": len(warnings),
            "files_loaded": len(loaded_payloads),
            "files_expected": len(REGISTRY_PATHS),
        },
        "details": details,
        "outputs": {
            "result_json": str(result_json_path),
            "verdict_md": str(verdict_md_path),
            "receipt_json": str(receipt_json_path),
        },
    }

    result_json_path.write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    verdict_md_path.write_text(render_verdict_md(report), encoding="utf-8")

    receipt_payload = {
        "schema_version": "imperium.receipt.v0_1",
        "receipt_id": "RECEIPT-ACT3-ADDRESS-TRUTH-CAPABILITY-SPINE-CHECK-V0_1",
        "receipt_type": "act3_registry_check",
        "task_id": TASK_ID,
        "stage_id": "STAGE-001-ACT3-SEED-REGISTRIES-CHECKER-AND-BASELINES-V0_1",
        "run_id": None,
        "issuer": "VM2_SERVITOR",
        "created_at_utc": now_utc(),
        "command": "python3 TOOLS/check_act3_address_truth_capability_spine_v0_1.py --repo-root . --human",
        "inputs": [
            REGISTRY_PATHS["zone_registry"],
            REGISTRY_PATHS["truth_source_registry"],
            REGISTRY_PATHS["capability_spine"],
            REGISTRY_PATHS["warning_stale_baseline"],
            SCHEMA_PATHS["organ_contract_schema"],
            SCHEMA_PATHS["organ_self_report_schema"],
            ADVISORY_REG_PATH,
        ],
        "outputs": [
            str(result_json_path.relative_to(repo_root)),
            str(verdict_md_path.relative_to(repo_root)),
            str(receipt_json_path.relative_to(repo_root)),
        ],
        "verdict": verdict,
        "warnings": warnings,
        "blockers": blockers,
        "evidence_paths": [
            str(result_json_path.relative_to(repo_root)),
            str(verdict_md_path.relative_to(repo_root)),
        ],
        "git_truth_ref": "ORGANS/ADMINISTRATUM/REGISTRY/TRUTH_SOURCE_REGISTRY_V0_1.json",
    }

    receipt_json_path.write_text(
        json.dumps(receipt_payload, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )

    return report


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Check Act 3 address/truth/capability spine registries v0.1"
    )
    parser.add_argument("--repo-root", default=".", help="Repository root path")
    parser.add_argument("--human", action="store_true", help="Print readable summary")
    return parser.parse_args()


def print_human(report: dict[str, Any]) -> None:
    print("=== ACT3 ADDRESS/TRUTH/CAPABILITY SPINE CHECK ===")
    print(f"repo_root: {report['repo_root']}")
    print(f"expected_head: {report['expected_head']}")
    print(f"verdict: {report['verdict']}")
    print(f"blockers: {report['counts']['blockers']}")
    print(f"warnings: {report['counts']['warnings']}")
    print("files:")
    for key, rel in REGISTRY_PATHS.items():
        print(f"  - {key}: {rel}")


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
