#!/usr/bin/env python3
from __future__ import annotations

import argparse
import datetime as dt
import json
import subprocess
from pathlib import Path
from typing import Any

TASK_ID = "TASK-20260513-FIRST-FOUR-ORGANS-ACT5-READINESS-V0_1"
SCHEMA_VERSION = "imperium.first_four_organs_act5_readiness_check.v0_1"
RUNTIME_REL = ".imperium_runtime/astronomicon/first_four_organs_act5_readiness_check"
REPORT_NAME = "FIRST_FOUR_ORGANS_ACT5_READINESS_CHECK_REPORT.json"
VERDICT_NAME = "FIRST_FOUR_ORGANS_ACT5_READINESS_CHECK_VERDICT.md"
RECEIPT_NAME = "FIRST_FOUR_ORGANS_ACT5_READINESS_CHECK_RECEIPT.json"

CONTRACT_SCHEMA_REL = "schemas/organ_contract_v0_2.schema.json"
SELF_REPORT_SCHEMA_REL = "schemas/organ_self_report_v0_1.schema.json"
READINESS_REGISTRY_REL = (
    "ORGANS/ASTRONOMICON/REGISTRY/ARC5_PREFIRE/FIRST_FOUR_ORGANS_ACT5_READINESS_20260513.json"
)
DOC_REL = "DOCS/FIRST_FOUR_ORGANS_ACT5_READINESS_V0_1.md"
START_HERE_REL = "START_HERE.md"
CURRENT_TRUTH_REL = "CURRENT_STATE/ARC5_PREFIRE_CURRENT_TRUTH_20260513.json"
ADVISORY_RESPONSE_REL = (
    "ORGANS/ASTRONOMICON/REGISTRY/ADVISORY_RESPONSES/ADVISORY-RESPONSE-20260513-KIRO-ACT5-PREFIRE-V0_1.json"
)

TARGET_MATURITY = "LEVEL_5_ACT5_GUIDE_MINIMAL_READY"

ORGANS = {
    "DOCTRINARIUM": {
        "dir": "ORGANS/DOCTRINARIUM",
        "contract": "ORGANS/DOCTRINARIUM/ORGAN_CONTRACT.json",
        "self_report": "ORGANS/DOCTRINARIUM/ORGAN_SELF_REPORT.json",
    },
    "ADMINISTRATUM": {
        "dir": "ORGANS/ADMINISTRATUM",
        "contract": "ORGANS/ADMINISTRATUM/ORGAN_CONTRACT.json",
        "self_report": "ORGANS/ADMINISTRATUM/ORGAN_SELF_REPORT.json",
    },
    "OFFICIO_AGENTIS": {
        "dir": "ORGANS/OFFICIO_AGENTIS",
        "contract": "ORGANS/OFFICIO_AGENTIS/ORGAN_CONTRACT.json",
        "self_report": "ORGANS/OFFICIO_AGENTIS/ORGAN_SELF_REPORT.json",
    },
    "ASTRONOMICON": {
        "dir": "ORGANS/ASTRONOMICON",
        "contract": "ORGANS/ASTRONOMICON/ORGAN_CONTRACT.json",
        "self_report": "ORGANS/ASTRONOMICON/ORGAN_SELF_REPORT.json",
    },
}

CONTRACT_REQUIRED_FIELDS = [
    "schema_version",
    "organ_id",
    "organ_name",
    "status",
    "maturity_level",
    "act5_role",
    "authority_scope",
    "not_authority",
    "owner_organs_or_zones",
    "read_zones",
    "write_zones",
    "forbidden_actions",
    "required_inputs",
    "required_outputs",
    "ports",
    "checks",
    "dashboards_or_utilities",
    "receipts",
    "known_blockers",
    "no_fake_green_rules",
    "readiness_claim",
    "evidence_files",
    "last_reviewed_task_id",
]

SELF_REPORT_REQUIRED_FIELDS = [
    "schema_version",
    "organ_id",
    "generated_at_utc",
    "repo_truth_at_generation",
    "current_status",
    "maturity_level_claim",
    "act5_readiness",
    "available_ports",
    "available_scripts",
    "available_dashboards_or_utilities",
    "known_blockers",
    "next_required_work",
    "evidence_files",
    "no_fake_green_statement",
]

MATURITY_LEVELS = {
    "LEVEL_0_NAME_ONLY",
    "LEVEL_1_SCAFFOLD",
    "LEVEL_2_DOCUMENTED",
    "LEVEL_3_CONTRACTED",
    "LEVEL_4_CHECKABLE",
    "LEVEL_5_ACT5_GUIDE_MINIMAL_READY",
    "LEVEL_6_OPERATIONAL_LIMITED",
    "LEVEL_7_FULLY_OPERATIONAL",
}

FORBIDDEN_READY_PATTERNS = [
    "act 5 execution is ready",
    "act5 execution is ready",
    "act 5 ready",
    "act5 ready",
    "act5_execution_ready: true",
    "act5_execution_ready=true",
]

ASSET_PATH_PREFIXES = ["ASSETS/", "SANCTUM/DESIGN_SYSTEM/", "SANCTUM/UI_LAB/"]


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


def run_git(repo_root: Path, args: list[str]) -> tuple[bool, str]:
    try:
        result = subprocess.run(
            ["git", *args],
            cwd=str(repo_root),
            capture_output=True,
            text=True,
            check=False,
        )
    except Exception as exc:  # noqa: BLE001
        return False, f"exception:{type(exc).__name__}:{exc}"
    if result.returncode != 0:
        return False, (result.stderr or result.stdout).strip()
    return True, result.stdout.strip()


def parse_status_paths(status_text: str) -> list[str]:
    paths: list[str] = []
    for raw_line in status_text.splitlines():
        line = raw_line.strip()
        if not line:
            continue
        content = line[3:] if len(line) >= 4 else line
        if " -> " in content:
            content = content.split(" -> ", 1)[1].strip()
        paths.append(content)
    return paths


def write_artifacts(repo_root: Path, report: dict[str, Any]) -> dict[str, str]:
    runtime_dir = repo_root / RUNTIME_REL
    runtime_dir.mkdir(parents=True, exist_ok=True)

    report_path = runtime_dir / REPORT_NAME
    verdict_path = runtime_dir / VERDICT_NAME
    receipt_path = runtime_dir / RECEIPT_NAME

    report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    lines: list[str] = [
        "# First Four Organs Act5 Readiness Check v0.1",
        "",
        f"- task_id: {TASK_ID}",
        f"- generated_at_utc: {report.get('generated_at_utc')}",
        f"- verdict: {report.get('verdict')}",
        f"- pass_count: {len(report.get('passes', []))}",
        f"- warn_count: {len(report.get('warnings', []))}",
        f"- blocked_count: {len(report.get('blocked', []))}",
    ]

    if report.get("blocked"):
        lines.extend(["", "## BLOCKED"])
        lines.extend(f"- {item}" for item in report["blocked"])

    if report.get("warnings"):
        lines.extend(["", "## WARN"])
        lines.extend(f"- {item}" for item in report["warnings"])

    if report.get("passes"):
        lines.extend(["", "## PASS"])
        lines.extend(f"- {item}" for item in report["passes"])

    verdict_path.write_text("\n".join(lines) + "\n", encoding="utf-8")

    receipt = {
        "schema_version": "imperium.first_four_organs_act5_readiness_check_receipt.v0_1",
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

    # Required non-organ files
    for rel in [CONTRACT_SCHEMA_REL, SELF_REPORT_SCHEMA_REL, READINESS_REGISTRY_REL, DOC_REL, START_HERE_REL]:
        path = repo_root / rel
        if path.exists():
            passes.append(f"file_exists:{rel}")
        else:
            add_unique(blocked, f"missing_required_file:{rel}")

    # Organs directory/contract/self report existence
    for organ_id, meta in ORGANS.items():
        dir_path = repo_root / meta["dir"]
        contract_path = repo_root / meta["contract"]
        self_report_path = repo_root / meta["self_report"]

        if dir_path.exists() and dir_path.is_dir():
            passes.append(f"organ_dir_exists:{organ_id}")
        else:
            add_unique(blocked, f"missing_organ_dir:{organ_id}:{meta['dir']}")

        if contract_path.exists():
            passes.append(f"organ_contract_exists:{organ_id}")
        else:
            add_unique(blocked, f"missing_organ_contract:{organ_id}:{meta['contract']}")

        if self_report_path.exists():
            passes.append(f"organ_self_report_exists:{organ_id}")
        else:
            add_unique(blocked, f"missing_organ_self_report:{organ_id}:{meta['self_report']}")

    contract_payloads: dict[str, dict[str, Any]] = {}
    self_report_payloads: dict[str, dict[str, Any]] = {}

    for organ_id, meta in ORGANS.items():
        contract_path = repo_root / meta["contract"]
        payload, err = read_json_obj(contract_path)
        if err:
            add_unique(blocked, err)
        elif payload is not None:
            contract_payloads[organ_id] = payload

            if payload.get("schema_version") == "imperium.organ_contract.v0_2":
                passes.append(f"contract_schema_version_ok:{organ_id}")
            else:
                add_unique(blocked, f"contract_schema_version_mismatch:{organ_id}")

            for field in CONTRACT_REQUIRED_FIELDS:
                if field in payload:
                    passes.append(f"contract_field_present:{organ_id}:{field}")
                else:
                    add_unique(blocked, f"contract_missing_field:{organ_id}:{field}")

            maturity = payload.get("maturity_level")
            if isinstance(maturity, str) and maturity in MATURITY_LEVELS:
                passes.append(f"contract_maturity_enum_ok:{organ_id}:{maturity}")
            else:
                add_unique(blocked, f"contract_maturity_invalid:{organ_id}")

            readiness = payload.get("readiness_claim")
            if isinstance(readiness, dict):
                full_claim = readiness.get("full_operational_claim")
                if maturity == "LEVEL_7_FULLY_OPERATIONAL":
                    evidence = readiness.get("full_operational_evidence")
                    if isinstance(evidence, list) and evidence:
                        add_unique(warnings, f"level7_claim_present_check_evidence_manually:{organ_id}")
                    else:
                        add_unique(blocked, f"level7_claim_without_explicit_evidence:{organ_id}")
                elif full_claim is True:
                    add_unique(blocked, f"full_operational_claim_true_without_level7:{organ_id}")
                else:
                    passes.append(f"no_full_operational_claim:{organ_id}")
            else:
                add_unique(blocked, f"contract_readiness_claim_not_object:{organ_id}")

            if maturity != TARGET_MATURITY:
                add_unique(warnings, f"organ_below_target_maturity:{organ_id}:{maturity}")

        self_report_path = repo_root / meta["self_report"]
        payload_sr, err_sr = read_json_obj(self_report_path)
        if err_sr:
            add_unique(blocked, err_sr)
        elif payload_sr is not None:
            self_report_payloads[organ_id] = payload_sr

            if payload_sr.get("schema_version") == "imperium.organ_self_report.v0_1":
                passes.append(f"self_report_schema_version_ok:{organ_id}")
            else:
                add_unique(blocked, f"self_report_schema_version_mismatch:{organ_id}")

            for field in SELF_REPORT_REQUIRED_FIELDS:
                if field in payload_sr:
                    passes.append(f"self_report_field_present:{organ_id}:{field}")
                else:
                    add_unique(blocked, f"self_report_missing_field:{organ_id}:{field}")

            sr_maturity = payload_sr.get("maturity_level_claim")
            if isinstance(sr_maturity, str) and sr_maturity in MATURITY_LEVELS:
                passes.append(f"self_report_maturity_enum_ok:{organ_id}:{sr_maturity}")
            else:
                add_unique(blocked, f"self_report_maturity_invalid:{organ_id}")

    # Readiness registry checks
    readiness_registry_path = repo_root / READINESS_REGISTRY_REL
    registry, reg_err = read_json_obj(readiness_registry_path)
    if reg_err:
        add_unique(blocked, reg_err)
        registry = None

    if registry is not None:
        if registry.get("schema_version") == "imperium.first_four_organs_act5_readiness.v0_1":
            passes.append("readiness_registry_schema_version_ok")
        else:
            add_unique(blocked, "readiness_registry_schema_version_mismatch")

        if registry.get("target_maturity") == TARGET_MATURITY:
            passes.append("readiness_registry_target_maturity_ok")
        else:
            add_unique(blocked, "readiness_registry_target_maturity_mismatch")

        if registry.get("act5_execution_ready") is False:
            passes.append("readiness_registry_act5_execution_ready_false")
        else:
            add_unique(blocked, "readiness_registry_act5_execution_ready_must_be_false")

        if registry.get("ready_for_agent_status") is False:
            passes.append("readiness_registry_ready_for_agent_false")
        else:
            add_unique(blocked, "readiness_registry_ready_for_agent_must_be_false")

        organs = registry.get("organs")
        if isinstance(organs, list):
            by_id = {
                item.get("organ_id"): item
                for item in organs
                if isinstance(item, dict) and isinstance(item.get("organ_id"), str)
            }
            missing = sorted(set(ORGANS.keys()).difference(set(by_id.keys())))
            if missing:
                add_unique(blocked, f"readiness_registry_missing_organs:{'|'.join(missing)}")
            else:
                passes.append("readiness_registry_contains_all_first_four_organs")

            for organ_id, item in by_id.items():
                if not isinstance(item, dict):
                    continue
                required = [
                    "organ_id",
                    "contract_file",
                    "self_report_file",
                    "current_maturity_claim",
                    "act5_guide_readiness",
                    "role_in_act5",
                    "blockers",
                    "evidence_files",
                    "next_required_work",
                ]
                for field in required:
                    if field in item:
                        passes.append(f"registry_organ_field_present:{organ_id}:{field}")
                    else:
                        add_unique(blocked, f"registry_organ_missing_field:{organ_id}:{field}")

                readiness_flag = item.get("act5_guide_readiness")
                if readiness_flag not in {"READY", "PARTIAL", "BLOCKED"}:
                    add_unique(blocked, f"registry_organ_invalid_readiness:{organ_id}")

                contract = contract_payloads.get(organ_id)
                if isinstance(contract, dict):
                    maturity = contract.get("maturity_level")
                    if maturity != TARGET_MATURITY and readiness_flag == "READY":
                        add_unique(blocked, f"registry_ready_but_maturity_below_target:{organ_id}:{maturity}")
        else:
            add_unique(blocked, "readiness_registry_organs_not_list")

    # Advisory source must remain non-execution authority
    advisory_path = repo_root / ADVISORY_RESPONSE_REL
    advisory, adv_err = read_json_obj(advisory_path)
    if adv_err:
        add_unique(blocked, adv_err)
    elif advisory is not None:
        source = advisory.get("source")
        if isinstance(source, dict) and source.get("source_authority") == "ADVISORY_ONLY_NOT_EXECUTION_AUTHORITY":
            passes.append("advisory_source_authority_non_execution_ok")
        else:
            add_unique(blocked, "advisory_source_authority_invalid")

        if advisory.get("must_not_execute_directly") is True:
            passes.append("advisory_must_not_execute_directly_true")
        else:
            add_unique(blocked, "advisory_must_not_execute_directly_must_be_true")

    # START_HERE should not claim Act 5 ready
    start_here = repo_root / START_HERE_REL
    if start_here.exists():
        text = start_here.read_text(encoding="utf-8").lower()
        hits = [p for p in FORBIDDEN_READY_PATTERNS if p in text]
        if hits:
            add_unique(blocked, f"start_here_claims_act5_ready:{'|'.join(hits)}")
        else:
            passes.append("start_here_does_not_claim_act5_ready")

    # Current truth should keep false flags
    current_truth_path = repo_root / CURRENT_TRUTH_REL
    if current_truth_path.exists():
        current_truth, ct_err = read_json_obj(current_truth_path)
        if ct_err:
            add_unique(blocked, ct_err)
        elif current_truth is not None:
            if current_truth.get("act5_execution_ready") is False:
                passes.append("current_truth_act5_execution_ready_false")
            else:
                add_unique(blocked, "current_truth_act5_execution_ready_must_be_false")

            if current_truth.get("ready_for_agent_status") is False:
                passes.append("current_truth_ready_for_agent_status_false")
            else:
                add_unique(blocked, "current_truth_ready_for_agent_status_must_be_false")

    # Assets/design-system/ui-lab not created by this step
    ok_status, status_text = run_git(repo_root, ["status", "--short"])
    if ok_status:
        changed_paths = parse_status_paths(status_text)
        for changed in changed_paths:
            for prefix in ASSET_PATH_PREFIXES:
                if changed.startswith(prefix):
                    add_unique(blocked, f"forbidden_early_asset_change_detected:{changed}")

        for prefix in ASSET_PATH_PREFIXES:
            path = repo_root / prefix.rstrip("/")
            if path.exists() and not any(ch.startswith(prefix) for ch in changed_paths):
                add_unique(warnings, f"asset_zone_exists_but_not_changed_in_step:{prefix}")

        if not any(ch.startswith(tuple(ASSET_PATH_PREFIXES)) for ch in changed_paths):
            passes.append("no_early_asset_designsystem_uilab_changes_detected")
    else:
        add_unique(warnings, f"git_status_unavailable:{status_text}")

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
    parser = argparse.ArgumentParser(description="Check first four organs Act5 readiness layer v0.1")
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
