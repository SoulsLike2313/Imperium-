#!/usr/bin/env python3
"""Build read-only NewGen Sanctum truth state from bounded phase artifacts."""

from __future__ import annotations

import argparse
import datetime as dt
import json
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Any

TASK_ID = "TASK-20260522-NEWGEN-SANCTUM-TRUTH-SHELL-VM3-V0_1"
REQUIRED_STARTING_HEAD = "efe511428dce83e352a41a4d02b41ed618448d29"
MODE = "READ_ONLY_FOUNDATION"


@dataclass(frozen=True)
class PhaseSpec:
    phase_no: int
    name: str
    summary: str
    paths: list[str]
    report_paths: list[str]
    base_limitations: list[str]


def run_git(repo_root: Path, *args: str) -> str:
    proc = subprocess.run(
        ["git", *args],
        cwd=repo_root,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        check=False,
    )
    if proc.returncode != 0:
        return "UNKNOWN"
    return proc.stdout.strip()


def get_git_truth(repo_root: Path) -> dict[str, Any]:
    head = run_git(repo_root, "rev-parse", "HEAD")
    branch = run_git(repo_root, "branch", "--show-current")
    status_short = run_git(repo_root, "status", "--short")
    return {
        "head": head,
        "branch": branch,
        "worktree_dirty": bool(status_short),
        "required_starting_head": REQUIRED_STARTING_HEAD,
        "head_matches_required_start": head == REQUIRED_STARTING_HEAD,
    }


def relpath(path: Path, repo_root: Path) -> str:
    return path.relative_to(repo_root).as_posix()


def build_phase_specs() -> list[PhaseSpec]:
    return [
        PhaseSpec(
            phase_no=1,
            name="Architecture",
            summary="NewGen architecture map exists as foundation planning artifact.",
            paths=[
                "IMPERIUM_NEW_GENERATION/ARCHITECTURE/NEWGEN_ARCHITECTURE_MAP_V0_1.md",
            ],
            report_paths=[
                "IMPERIUM_NEW_GENERATION/REPORTS/TASK-20260521-NEWGEN-ARCHITECTURE-SKILL-SPINE-PC-V0_1/FINAL_RECEIPT.json",
            ],
            base_limitations=[
                "Architecture map is foundation and migration-language level, not full migration execution.",
            ],
        ),
        PhaseSpec(
            phase_no=2,
            name="Organ Packets",
            summary="Organ packet protocol and schemas define bounded 8-organ packet exchange.",
            paths=[
                "IMPERIUM_NEW_GENERATION/ARCHITECTURE/ORGAN_PACKET_PROTOCOL_V0_1.md",
                "IMPERIUM_NEW_GENERATION/CONTRACTS/ORGAN_PACKETS/ORGAN_PACKET_V0_1.schema.json",
                "IMPERIUM_NEW_GENERATION/CONTRACTS/ORGAN_PACKETS/ORGAN_PACKET_SET_V0_1.schema.json",
            ],
            report_paths=[
                "IMPERIUM_NEW_GENERATION/REPORTS/TASK-20260521-NEWGEN-ORGAN-PACKET-CONTRACT-PC-V0_1/FINAL_RECEIPT.json",
            ],
            base_limitations=[
                "Protocol defines contract surfaces; live organ dialogue is not claimed.",
            ],
        ),
        PhaseSpec(
            phase_no=3,
            name="Task Kernel",
            summary="Task kernel/registry contract layer is present as deterministic foundation.",
            paths=[
                "IMPERIUM_NEW_GENERATION/ARCHITECTURE/TASK_KERNEL_REGISTRY_V0_1.md",
                "IMPERIUM_NEW_GENERATION/CONTRACTS/TASK_KERNEL/TASK_KERNEL_V0_1.schema.json",
                "IMPERIUM_NEW_GENERATION/TASKS/REGISTRY/TASK_INDEX_V0_1.json",
            ],
            report_paths=[
                "IMPERIUM_NEW_GENERATION/REPORTS/TASK-20260521-NEWGEN-TASK-KERNEL-REGISTRY-PC-V0_1/FINAL_RECEIPT.json",
            ],
            base_limitations=[
                "Foundation contracts exist; live kernel runtime orchestration is not proven.",
            ],
        ),
        PhaseSpec(
            phase_no=4,
            name="Astronomicon",
            summary="Astronomicon task-formation contracts and builder foundation are present.",
            paths=[
                "IMPERIUM_NEW_GENERATION/ARCHITECTURE/ASTRONOMICON_TASK_FORMATION_V0_1.md",
                "IMPERIUM_NEW_GENERATION/CONTRACTS/ASTRONOMICON/TASK_FORMATION_RECORD_V0_1.schema.json",
            ],
            report_paths=[
                "IMPERIUM_NEW_GENERATION/REPORTS/TASK-20260521-NEWGEN-ASTRONOMICON-TASK-FORMATION-PC-V0_1/FINAL_RECEIPT.json",
            ],
            base_limitations=[
                "Formation is deterministic foundation and does not include autonomous execution loop.",
            ],
        ),
        PhaseSpec(
            phase_no=5,
            name="Authority Gates",
            summary="Officio/Doctrinarium ACK artifacts exist with explicit warning boundaries.",
            paths=[
                "IMPERIUM_NEW_GENERATION/REPORTS/TASK-20260522-NEWGEN-SANCTUM-TRUTH-SHELL-VM3-V0_1/OFFICIO_ROLE_ACK_OR_WARN.json",
                "IMPERIUM_NEW_GENERATION/REPORTS/TASK-20260522-NEWGEN-SANCTUM-TRUTH-SHELL-VM3-V0_1/DOCTRINARIUM_LAW_ACK_OR_WARN.json",
                "IMPERIUM_NEW_GENERATION/REPORTS/TASK-20260522-NEWGEN-SANCTUM-TRUTH-SHELL-VM3-V0_1/SUPER_SKEPTICISM_ACK.json",
                "IMPERIUM_NEW_GENERATION/AUTHORITY_DRAFTS/SUPER_SKEPTICISM_MODE_V0_1.md",
                "IMPERIUM_NEW_GENERATION/ORGAN_AGENTS/DOCTRINARIUM_AGENT/role_contract.md",
            ],
            report_paths=[
                "IMPERIUM_NEW_GENERATION/REPORTS/TASK-20260521-NEWGEN-SERVITOR-RUN-RERUN-LOOP-PC-V0_1/OFFICIO_ROLE_ACK_OR_WARN.json",
                "IMPERIUM_NEW_GENERATION/REPORTS/TASK-20260521-NEWGEN-SERVITOR-RUN-RERUN-LOOP-PC-V0_1/DOCTRINARIUM_LAW_ACK_OR_WARN.json",
            ],
            base_limitations=[
                "Doctrinarium role contract remains skeleton-only and keeps this phase warning-bounded.",
            ],
        ),
        PhaseSpec(
            phase_no=6,
            name="Servitor Loop",
            summary="Run/rerun loop architecture and receipts are present as foundation-only execution envelope.",
            paths=[
                "IMPERIUM_NEW_GENERATION/ARCHITECTURE/SERVITOR_RUN_RERUN_LOOP_V0_1.md",
            ],
            report_paths=[
                "IMPERIUM_NEW_GENERATION/REPORTS/TASK-20260521-NEWGEN-SERVITOR-RUN-RERUN-LOOP-PC-V0_1/FINAL_RECEIPT.json",
                "IMPERIUM_NEW_GENERATION/REPORTS/TASK-20260521-NEWGEN-SERVITOR-RUN-RERUN-LOOP-PC-V0_1/VALIDATOR_REPORT.json",
            ],
            base_limitations=[
                "Loop is receipt-driven foundation; no production autonomous executor claim.",
            ],
        ),
        PhaseSpec(
            phase_no=7,
            name="Evidence Binder",
            summary="Task state and evidence binder artifacts exist for replay/index foundation.",
            paths=[
                "IMPERIUM_NEW_GENERATION/ARCHITECTURE/TASK_STATE_EVIDENCE_BINDER_V0_1.md",
            ],
            report_paths=[
                "IMPERIUM_NEW_GENERATION/REPORTS/TASK-20260521-NEWGEN-TASK-STATE-EVIDENCE-BINDER-PC-V0_1/FINAL_RECEIPT.json",
                "IMPERIUM_NEW_GENERATION/REPORTS/TASK-20260521-NEWGEN-TASK-STATE-EVIDENCE-BINDER-PC-V0_1/VALIDATOR_REPORT.json",
            ],
            base_limitations=[
                "Evidence binder emits proposals and replay indexes, not live state mutation.",
            ],
        ),
        PhaseSpec(
            phase_no=8,
            name="Visual Brain",
            summary="Visual brain corridor and generated visual state exist as static truth surface.",
            paths=[
                "IMPERIUM_NEW_GENERATION/ARCHITECTURE/VISUAL_BRAIN_TASK_CORRIDOR_V0_1.md",
                "IMPERIUM_NEW_GENERATION/VISUAL_BRAIN/TASK_CORRIDOR_V0_1/index.html",
                "IMPERIUM_NEW_GENERATION/VISUAL_BRAIN/TASK_CORRIDOR_V0_1/data/visual_brain_task_corridor_state.generated.json",
            ],
            report_paths=[
                "IMPERIUM_NEW_GENERATION/REPORTS/TASK-20260521-NEWGEN-VISUAL-BRAIN-TASK-CORRIDOR-PC-V0_1/FINAL_RECEIPT.json",
            ],
            base_limitations=[
                "Visual corridor is read-only lab/foundation and does not imply backend autonomy.",
            ],
        ),
        PhaseSpec(
            phase_no=9,
            name="Skill Growth",
            summary="Skill growth contracts and generated indexes exist for learning-loop foundation.",
            paths=[
                "IMPERIUM_NEW_GENERATION/ARCHITECTURE/SKILL_GROWTH_SYSTEM_V0_1.md",
                "IMPERIUM_NEW_GENERATION/SKILLS/GROWTH/SKILL_GROWTH_INDEX_V0_1.json",
            ],
            report_paths=[
                "IMPERIUM_NEW_GENERATION/REPORTS/TASK-20260521-NEWGEN-SKILL-GROWTH-SYSTEM-VM3-V0_1/FINAL_RECEIPT.json",
            ],
            base_limitations=[
                "Growth loop is deterministic foundation; no live self-learning autonomy claim.",
            ],
        ),
        PhaseSpec(
            phase_no=10,
            name="Tool Admission",
            summary="Mechanicus tool-admission contracts/indexes exist for controlled candidate-to-decision flow.",
            paths=[
                "IMPERIUM_NEW_GENERATION/ARCHITECTURE/MECHANICUS_TOOL_ADMISSION_V0_1.md",
                "IMPERIUM_NEW_GENERATION/MECHANICUS/TOOL_ADMISSION/TOOL_ADMISSION_INDEX_V0_1.json",
            ],
            report_paths=[
                "IMPERIUM_NEW_GENERATION/REPORTS/TASK-20260521-NEWGEN-MECHANICUS-TOOL-ADMISSION-VM3-V0_1/FINAL_RECEIPT.json",
            ],
            base_limitations=[
                "Admission layer is contract/decision foundation and does not imply auto-install autonomy.",
            ],
        ),
    ]


def status_for_phase(spec: PhaseSpec, existing_paths: list[str]) -> str:
    existing_set = set(existing_paths)
    core_found = [path for path in spec.paths if path in existing_set]
    if spec.phase_no == 5:
        if len(core_found) >= 3:
            return "WARN"
        if core_found:
            return "PARTIAL"
        return "MISSING"
    if len(core_found) == len(spec.paths):
        return "FOUNDATION"
    if core_found:
        return "PARTIAL"
    return "MISSING"


def build_state(repo_root: Path) -> dict[str, Any]:
    phase_specs = build_phase_specs()
    phases: list[dict[str, Any]] = []
    warnings: list[str] = []

    for spec in phase_specs:
        existing_paths: list[str] = []
        missing_paths: list[str] = []

        for rel in spec.paths:
            full = repo_root / rel
            if full.exists():
                existing_paths.append(rel)
            else:
                missing_paths.append(rel)

        existing_reports: list[str] = []
        for rel in spec.report_paths:
            if (repo_root / rel).exists():
                existing_reports.append(rel)

        status = status_for_phase(spec, existing_paths)
        if status in {"MISSING", "WARN"}:
            warnings.append(f"PHASE_{spec.phase_no}_{status}")

        limitations = list(spec.base_limitations)
        if missing_paths:
            limitations.append("Missing expected artifacts: " + ", ".join(missing_paths))

        evidence_refs = [f"FILE:{path}" for path in existing_paths]
        evidence_refs.extend(f"REPORT:{path}" for path in existing_reports)

        phases.append(
            {
                "phase_no": spec.phase_no,
                "name": spec.name,
                "status": status,
                "summary": spec.summary,
                "evidence_refs": evidence_refs,
                "paths": existing_paths,
                "report_paths": existing_reports,
                "limitations": limitations,
            }
        )

    git_truth = get_git_truth(repo_root)

    state = {
        "schema_id": "SANCTUM_NG_STATE_V0_1",
        "task_id": TASK_ID,
        "mode": MODE,
        "generated_at_utc": dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
        "git": git_truth,
        "truth_flags": {
            "read_only": True,
            "foundation_only": True,
            "production_ready": False,
            "live_backend": False,
            "autonomous_execution": False,
        },
        "pipeline_shape": [
            {
                "phase_no": item["phase_no"],
                "name": item["name"],
                "status": item["status"],
            }
            for item in phases
        ],
        "phases": phases,
        "warnings": warnings,
        "limitations": [
            "Truth shell reflects bounded local artifacts and foundation phase evidence only.",
            "No live backend bridge is wired from browser local file mode.",
            "No autonomous organ dialogue or production readiness is claimed.",
            "No phase is shown as PROVED unless explicit evidence refs are present.",
        ],
        "forbidden_claims": [
            "LIVE_BACKEND_READY",
            "AUTONOMOUS_EXECUTION_READY",
            "PRODUCTION_READY",
            "LIVE_ORGAN_DIALOGUE",
        ],
        "actions": {
            "refresh_truth": "NOT_WIRED_LOCAL_FILE_ONLY",
            "open_reports": "PREVIEW_ONLY",
            "validate": "RUN_CLI_NOT_FROM_BROWSER",
            "create_task": "NOT_WIRED",
            "consult_organs": "NOT_WIRED",
        },
    }

    return state


def parse_args() -> argparse.Namespace:
    script_path = Path(__file__).resolve()
    default_repo_root = script_path.parents[3]
    default_output = default_repo_root / "IMPERIUM_NEW_GENERATION/SANCTUM_NG/DATA/sanctum_ng_state.generated.json"

    parser = argparse.ArgumentParser(description="Build Sanctum NG read-only state.")
    parser.add_argument("--repo-root", type=Path, default=default_repo_root)
    parser.add_argument("--output", type=Path, default=default_output)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    repo_root = args.repo_root.resolve()
    output = args.output.resolve()

    state = build_state(repo_root)

    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(state, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    print(f"state_written={relpath(output, repo_root)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
