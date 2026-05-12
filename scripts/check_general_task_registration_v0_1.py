#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path
from typing import Any

EXPECTED_HEAD = "1603d09b60e4b305e8a431df3b7dd5cc53d6e534"
EXPECTED_GENERAL_TASK_ID = "GENERAL-TASK-20260512-IMPERIUM-FOUNDATION-ARCS-V0_1"
EXPECTED_PLAN = (
    "DOCS/OWNER_DOCTRINE/PLAN_REVIEWS/FIRST_12_STEPS_20260512/"
    "FIRST_12_STEPS_REFRAMED_FOUNDATION_ARCS_20260512.md"
)
EXPECTED_TREE_URL = f"https://github.com/SoulsLike2313/Imperium-/tree/{EXPECTED_HEAD}"
EXPECTED_BLOB_URL = (
    "https://github.com/SoulsLike2313/Imperium-/blob/"
    f"{EXPECTED_HEAD}/{EXPECTED_PLAN}"
)

SCHEMA_FILES = [
    "schemas/general_task.schema.json",
    "schemas/task.schema.json",
    "schemas/stage.schema.json",
    "schemas/run.schema.json",
    "schemas/stage_pass_criteria.schema.json",
    "schemas/technical_review_input.schema.json",
    "schemas/technical_review_response.schema.json",
]


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def add_blocker(blockers: list[str], message: str) -> None:
    if message not in blockers:
        blockers.append(message)


def add_warning(warnings: list[str], message: str) -> None:
    if message not in warnings:
        warnings.append(message)


def load_json(path: Path, blockers: list[str], label: str) -> dict[str, Any] | None:
    if not path.exists():
        add_blocker(blockers, f"missing_file:{label}:{path.as_posix()}")
        return None
    try:
        obj = json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        add_blocker(blockers, f"invalid_json:{label}:{path.as_posix()}:{type(exc).__name__}")
        return None
    if not isinstance(obj, dict):
        add_blocker(blockers, f"invalid_json_type:{label}:{path.as_posix()}")
        return None
    return obj


def main() -> int:
    repo = Path(__file__).resolve().parents[1]
    blockers: list[str] = []
    warnings: list[str] = []

    schema_status: dict[str, bool] = {}
    for rel in SCHEMA_FILES:
        schema_status[rel] = (repo / rel).exists()
        if not schema_status[rel]:
            add_blocker(blockers, f"missing_schema:{rel}")

    general_task_path = (
        repo
        / "ORGANS/ASTRONOMICON/REGISTRY/GENERAL_TASKS/"
        / "GENERAL-TASK-20260512-IMPERIUM-FOUNDATION-ARCS-V0_1.json"
    )
    candidates_path = (
        repo
        / "ORGANS/ASTRONOMICON/REGISTRY/GENERAL_TASKS/"
        / "GENERAL-TASK-20260512-IMPERIUM-FOUNDATION-ARCS-V0_1_TASK_CANDIDATES_DRAFT.json"
    )

    gt = load_json(general_task_path, blockers, "general_task")
    cand = load_json(candidates_path, blockers, "task_candidates_draft")

    plan_path = repo / EXPECTED_PLAN
    if not plan_path.exists():
        add_blocker(blockers, f"missing_source_plan:{EXPECTED_PLAN}")

    computed_plan_sha = sha256_file(plan_path) if plan_path.exists() else None

    if gt is not None:
        required_fields = [
            "schema_version",
            "general_task_id",
            "source_file",
            "source_sha256",
            "git_head",
            "tree_url",
            "blob_url",
            "registration_status",
            "decomposition_status",
            "technical_review_inputs",
            "task_candidate_status",
        ]
        for field in required_fields:
            if field not in gt:
                add_blocker(blockers, f"general_task_missing_field:{field}")

        if gt.get("general_task_id") != EXPECTED_GENERAL_TASK_ID:
            add_blocker(blockers, "general_task_id_mismatch")
        if gt.get("source_file") != EXPECTED_PLAN:
            add_blocker(blockers, "source_file_mismatch")
        if gt.get("source_sha256") != computed_plan_sha:
            add_blocker(blockers, "source_sha256_mismatch")
        if gt.get("git_head") != EXPECTED_HEAD:
            add_blocker(blockers, "git_head_mismatch")

        tree_url = str(gt.get("tree_url", ""))
        blob_url = str(gt.get("blob_url", ""))
        if tree_url != EXPECTED_TREE_URL:
            add_blocker(blockers, "tree_url_mismatch")
        if blob_url != EXPECTED_BLOB_URL:
            add_blocker(blockers, "blob_url_mismatch")

        if gt.get("registration_status") != "REGISTERED_NOT_DECOMPOSED":
            add_blocker(blockers, "registration_status_not_REGISTERED_NOT_DECOMPOSED")
        if gt.get("decomposition_status") != "PENDING_TASK_CANDIDATES":
            add_blocker(blockers, "decomposition_status_not_PENDING_TASK_CANDIDATES")
        if gt.get("task_candidate_status") != "NOT_CREATED":
            add_warning(warnings, "task_candidate_status_not_NOT_CREATED")

        tri = gt.get("technical_review_inputs")
        if not isinstance(tri, list) or not tri:
            add_blocker(blockers, "technical_review_inputs_missing_or_empty")
        else:
            required_tri_fields = {
                "input_id",
                "source_type",
                "source_path",
                "canonicality",
                "purpose",
                "status",
                "used_for",
            }
            allowed_source_types = {
                "external_research_advisory",
                "hard_red_team_architecture_review",
                "engineering_audit",
                "dependency_review",
                "security_boundary_review",
                "implementation_risk_review",
                "future_improvement_recommendations",
                "owner_uploaded_reference",
            }
            for idx, item in enumerate(tri):
                if not isinstance(item, dict):
                    add_blocker(blockers, f"technical_review_input_{idx}_not_object")
                    continue
                missing = sorted(required_tri_fields - set(item.keys()))
                if missing:
                    add_blocker(blockers, f"technical_review_input_{idx}_missing:{','.join(missing)}")
                source_type = item.get("source_type")
                if source_type not in allowed_source_types:
                    add_blocker(blockers, f"technical_review_input_{idx}_invalid_source_type:{source_type}")

    if cand is not None:
        if cand.get("status") != "DRAFT_TASK_CANDIDATES_NOT_OWNER_APPROVED":
            add_blocker(blockers, "task_candidates_draft_status_invalid")
        task_candidates = cand.get("task_candidates")
        if not isinstance(task_candidates, list) or not task_candidates:
            add_blocker(blockers, "task_candidates_missing_or_empty")

    result = {
        "schema_version": "imperium.general_task_registration_check.v0_1",
        "repo_root": str(repo),
        "general_task_path": str(general_task_path),
        "task_candidates_draft_path": str(candidates_path),
        "expected_head": EXPECTED_HEAD,
        "expected_general_task_id": EXPECTED_GENERAL_TASK_ID,
        "expected_source_file": EXPECTED_PLAN,
        "computed_source_sha256": computed_plan_sha,
        "schema_files_present": schema_status,
        "warnings": warnings,
        "blockers": blockers,
        "verdict": "PASS" if not blockers else "BLOCKED",
    }

    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if not blockers else 2


if __name__ == "__main__":
    raise SystemExit(main())
