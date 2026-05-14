import argparse
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path
import hashlib
import sys

def utc_now():
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

def sha256_path(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest().upper()

def load_json(path: Path):
    with path.open("r", encoding="utf-8-sig") as f:
        return json.load(f)

def git_value(repo_root: Path, args):
    try:
        return subprocess.check_output(["git", *args], cwd=str(repo_root), text=True, stderr=subprocess.STDOUT).strip()
    except Exception as e:
        return f"GIT_ERROR:{e}"

def add_check(checks, name, status, detail, evidence=None):
    checks.append({
        "name": name,
        "status": status,
        "detail": detail,
        "evidence": evidence or {}
    })

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--repo-root", required=True)
    p.add_argument("--context-root", required=True)
    p.add_argument("--local-task-id", required=True)
    ns = p.parse_args()

    repo = Path(ns.repo_root)
    context = Path(ns.context_root)
    local_task_id = ns.local_task_id

    stage_map_path = repo / "ORGANS" / "ASTRONOMICON" / "REGISTRY" / "STAGES" / local_task_id / f"STAGE-MAP-{local_task_id}.json"
    stage_review_path = repo / "ORGANS" / "ASTRONOMICON" / "IMPORTS" / "SPECULUM_STAGE_REVIEW" / local_task_id / "speculum_stage_review_response.json"
    receipt_root = context / "ASTRONOMICON" / "RECEIPTS"
    receipt_root.mkdir(parents=True, exist_ok=True)

    git_head = git_value(repo, ["rev-parse", "HEAD"])
    commit_count = git_value(repo, ["rev-list", "--count", "HEAD"])

    checks = []
    overall = "PASS"

    def fail(name, detail, evidence=None):
        nonlocal overall
        overall = "BLOCKED"
        add_check(checks, name, "BLOCKED", detail, evidence)

    def ok(name, detail, evidence=None):
        add_check(checks, name, "PASS", detail, evidence)

    if not stage_map_path.exists():
        fail("stage_map_exists", "Stage map file missing", {"path": str(stage_map_path)})
        stage_map = None
    else:
        stage_map = load_json(stage_map_path)
        ok("stage_map_exists", "Stage map file exists", {"path": str(stage_map_path), "sha256": sha256_path(stage_map_path)})

    if not stage_review_path.exists():
        fail("stage_review_import_exists", "Speculum stage review import missing", {"path": str(stage_review_path)})
        review = None
    else:
        review = load_json(stage_review_path)
        ok("stage_review_import_exists", "Speculum stage review import exists", {"path": str(stage_review_path), "sha256": sha256_path(stage_review_path)})

    if stage_map:
        expected = {
            "status": "CORRECTED_PENDING_REGISTRATION_PRECHECK",
            "ready_for_agent": False,
            "registration_kind": "WORKBENCH_ACTIVE_STATE_ONLY",
            "authority_scope": "ASTRONOMICON_WORKBENCH_DASHBOARD_ONLY",
            "vm2_sync_requested": False,
            "servitor_handoff_created": False,
            "inquisition_build_requested": False,
        }
        for key, expected_value in expected.items():
            actual = stage_map.get(key)
            if actual == expected_value:
                ok(f"stage_map_{key}", f"{key} is correct", {"value": actual})
            else:
                fail(f"stage_map_{key}", f"{key} mismatch", {"expected": expected_value, "actual": actual})

        stages = stage_map.get("stages", [])
        if stage_map.get("stage_count") == 4 and len(stages) == 4:
            ok("stage_count_exact_4", "Stage map has exactly 4 stages")
        else:
            fail("stage_count_exact_4", "Stage count is not exactly 4", {"stage_count": stage_map.get("stage_count"), "len_stages": len(stages)})

        for i, st in enumerate(stages, start=1):
            missing = [k for k in ["stage_id", "title", "purpose", "scope_in", "scope_out", "expected_outputs", "required_checks", "pass_condition", "fail_condition"] if k not in st]
            if missing:
                fail(f"stage_{i}_required_fields", "Stage missing required fields", {"missing": missing, "stage": st.get("stage_id")})
            else:
                ok(f"stage_{i}_required_fields", "Stage has required fields", {"stage": st.get("stage_id")})

    if review:
        if review.get("reviewed_local_task_id") == local_task_id:
            ok("review_local_task_match", "Stage review local_task_id matches")
        else:
            fail("review_local_task_match", "Stage review local_task_id mismatch", {"actual": review.get("reviewed_local_task_id")})

        if review.get("review_verdict") == "APPROVE_STAGE_MAP_WITH_CORRECTIONS":
            ok("review_verdict", "Review verdict allows corrections path", {"review_verdict": review.get("review_verdict")})
        else:
            fail("review_verdict", "Unexpected or pending review verdict", {"review_verdict": review.get("review_verdict")})

        if review.get("final_recommendation") == "APPLY_CORRECTIONS_THEN_REGISTER_STAGE_MAP":
            ok("review_final_recommendation", "Final recommendation allows precheck path")
        else:
            fail("review_final_recommendation", "Bad final recommendation", {"final_recommendation": review.get("final_recommendation")})

    required_paths = [
        "ORGANS/ASTRONOMICON/SCHEMAS/general_task_intake_v0_1.schema.json",
        "ORGANS/ASTRONOMICON/SCHEMAS/workbench_active_state_v0_1.schema.json",
        "scripts/astronomicon_stage_map_schema_validate_v0_1.py",
        "scripts/astronomicon_contract_schema_validate_v0_1.py",
        "scripts/astronomicon_workbench_intake_e2e_check_v0_1.py",
        "scripts/astronomicon_active_state_validate_v0_1.py",
        "scripts/astronomicon_speculum_stage_review_import_guard_v0_1.py",
        "scripts/imperium_utf8_mojibake_guard_v0_1.py",
        "scripts/imperium_repo_purity_guard_v0_1.py",
        "scripts/astronomicon_workbench_check_all_v0_1.py",
    ]

    missing_required = []
    for rel in required_paths:
        path = repo / rel
        if path.exists():
            ok(f"required_path_exists:{rel}", "Required schema/checker path exists", {"path": rel})
        else:
            missing_required.append(rel)
            fail(f"required_path_missing:{rel}", "Required schema/checker path missing", {"path": rel})

    forbidden_names = {"OUTBOX", "RUNTIME", "HANDOFF", "TRANSPORT_ZIPS", "SECRET_NOTES"}
    found_forbidden = []
    for child in repo.rglob("*"):
        try:
            if child.is_dir() and child.name.upper() in forbidden_names:
                found_forbidden.append(str(child.relative_to(repo)))
        except Exception:
            pass

    if found_forbidden:
        fail("repo_purity_negative_path_scan", "Forbidden runtime/context-like directories found under repo", {"found": found_forbidden[:50]})
    else:
        ok("repo_purity_negative_path_scan", "No obvious runtime/context directories found under repo")

    receipt = {
        "schema_version": "STAGE_MAP_REGISTRATION_PRECHECK_RECEIPT_V0_1",
        "created_at_utc": utc_now(),
        "repo_root": str(repo),
        "context_root": str(context),
        "git_head": git_head,
        "commit_count": commit_count,
        "local_task_id": local_task_id,
        "stage_map_path": str(stage_map_path),
        "stage_map_sha256": sha256_path(stage_map_path) if stage_map_path.exists() else None,
        "stage_review_import_path": str(stage_review_path),
        "stage_review_import_sha256": sha256_path(stage_review_path) if stage_review_path.exists() else None,
        "overall_status": overall,
        "ready_for_agent": False,
        "registration_kind": "WORKBENCH_ACTIVE_STATE_ONLY",
        "vm2_sync_requested": False,
        "servitor_handoff_created": False,
        "inquisition_build_requested": False,
        "missing_required_paths": missing_required,
        "checks": checks,
        "next_gate": "CREATE_MISSING_SCHEMAS_AND_CHECKERS" if overall != "PASS" else "OWNER_MANUAL_GATE_FOR_LOCAL_STAGE_MAP_REGISTRATION"
    }

    safe_time = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H%M%SZ")
    receipt_path = receipt_root / f"STAGE_MAP_REGISTRATION_PRECHECK_{local_task_id}_{safe_time}.json"
    receipt_path.write_text(json.dumps(receipt, ensure_ascii=False, indent=2), encoding="utf-8")

    print(json.dumps({
        "overall_status": overall,
        "receipt_path": str(receipt_path),
        "missing_required_paths": missing_required,
        "ready_for_agent": False,
        "next_gate": receipt["next_gate"]
    }, ensure_ascii=False, indent=2))

    return 0 if overall == "PASS" else 2

if __name__ == "__main__":
    sys.exit(main())
