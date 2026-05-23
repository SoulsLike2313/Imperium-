#!/usr/bin/env python3
"""Bounded allowlisted Transfer Action Runner for Sanctum NG foundation layer."""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import subprocess
import uuid
from pathlib import Path
from typing import Any

TASK_ID_DEFAULT = "TASK-20260523-NEWGEN-SANCTUM-TRANSFER-ACTION-RUNNER-VM3-V0_1"
BASE_REL = "IMPERIUM_NEW_GENERATION/SANCTUM_NG/TRANSFER_CONSOLE"

REQUEST_SCHEMA_REL = f"{BASE_REL}/CONTRACTS/transfer_action_request.schema.json"
RESULT_SCHEMA_REL = f"{BASE_REL}/CONTRACTS/transfer_action_result.schema.json"
POLICY_SCHEMA_REL = f"{BASE_REL}/CONTRACTS/transfer_action_runner_policy.schema.json"

ACTION_REQUEST_DIR_REL = f"{BASE_REL}/DATA/action_requests"
ACTION_RESULT_DIR_REL = f"{BASE_REL}/DATA/action_results"
ACTION_LEDGER_DIR_REL = f"{BASE_REL}/DATA/ledgers"
ACTION_LEDGER_REL = f"{ACTION_LEDGER_DIR_REL}/transfer_action_runner_ledger.jsonl"
ACTION_SAMPLE_DIR_REL = f"{BASE_REL}/DATA/samples"
POLICY_SNAPSHOT_REL = f"{ACTION_SAMPLE_DIR_REL}/transfer_action_runner_policy.v0_1.json"
VIEW_STATE_REL = f"{BASE_REL}/DATA/TRANSFER_CONSOLE_VIEW_STATE.generated.json"

ROLLBACK_POLICY_REL = "IMPERIUM_NEW_GENERATION/TRUTH/ACTION_ROLLBACK/ACTION_ROLLBACK_POLICY_V0_1.json"

ALLOWED_ACTION_TYPES = {
    "SEND_TASKPACK_ZIP",
    "FETCH_REPORT_BUNDLE_ZIP",
    "REGISTER_TRANSFER_RESULT",
    "VALIDATE_TRANSFER_REQUEST",
    "DRY_RUN_TRANSFER",
}
ALLOWED_CONTOURS = {"PC", "VM2", "VM3"}
ALLOWED_MODES = {"DRY_RUN", "EXECUTE"}
FORBIDDEN_REQUEST_FIELDS = {
    "command",
    "shell",
    "exec",
    "powershell",
    "bash",
    "cmd",
    "arbitrary_command",
    "remote_command",
}

SAFE_TARGET_ROOTS = {
    "VM2_TASKPACK_INBOX": "/home/vboxuser2/IMPERIUM_WORK/Imperium-/INBOX/VM2_TASKPACKS/",
    "VM3_TASKPACK_INBOX": "/home/vboxuser3/IMPERIUM_WORK/Imperium-/INBOX/VM3_TASKPACKS/",
    "VM2_REPORT_OUTBOX_CANDIDATE": "/home/vboxuser2/IMPERIUM_WORK/Imperium-/IMPERIUM_NEW_GENERATION/",
    "VM3_REPORT_OUTBOX_CANDIDATE": "/home/vboxuser3/IMPERIUM_WORK/Imperium-/IMPERIUM_NEW_GENERATION/",
}


def utc_now() -> str:
    return dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def relpath(path: Path, repo_root: Path) -> str:
    return path.resolve().relative_to(repo_root.resolve()).as_posix()


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def load_json(path: Path) -> dict[str, Any] | None:
    if not path.exists():
        return None
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return None
    if not isinstance(payload, dict):
        return None
    return payload


def append_jsonl(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(payload, ensure_ascii=False) + "\n")


def list_json_records(directory: Path) -> list[dict[str, Any]]:
    if not directory.exists():
        return []
    out: list[dict[str, Any]] = []
    for item in sorted(directory.glob("*.json"), key=lambda path: path.stat().st_mtime, reverse=True):
        payload = load_json(item)
        if payload is None:
            continue
        payload["_path"] = item
        out.append(payload)
    return out


def list_jsonl(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    out: list[dict[str, Any]] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        row = line.strip()
        if not row:
            continue
        try:
            payload = json.loads(row)
        except json.JSONDecodeError:
            continue
        if isinstance(payload, dict):
            out.append(payload)
    return out


def new_id(prefix: str) -> str:
    stamp = utc_now().replace("-", "").replace(":", "")
    return f"{prefix}-{stamp}-{uuid.uuid4().hex[:8].upper()}"


def sha256_file(path: Path) -> str | None:
    if not path.exists() or not path.is_file():
        return None
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(65536), b""):
            digest.update(chunk)
    return digest.hexdigest()


def resolve_candidate_path(candidate: str, repo_root: Path) -> Path:
    raw = Path(candidate)
    if raw.is_absolute():
        return raw.resolve()
    return (repo_root / raw).resolve()


def safe_roots_abs() -> list[Path]:
    return [Path(root).resolve() for root in SAFE_TARGET_ROOTS.values()]


def is_under_root(candidate: Path, root: Path) -> bool:
    try:
        candidate.relative_to(root)
        return True
    except ValueError:
        return False


def is_safe_path(candidate: str, repo_root: Path) -> tuple[bool, str]:
    resolved = resolve_candidate_path(candidate, repo_root)
    for root in safe_roots_abs():
        if is_under_root(resolved, root):
            return True, str(resolved)
    return False, str(resolved)


def ensure_layout(repo_root: Path) -> dict[str, Path]:
    request_dir = repo_root / ACTION_REQUEST_DIR_REL
    result_dir = repo_root / ACTION_RESULT_DIR_REL
    sample_dir = repo_root / ACTION_SAMPLE_DIR_REL
    ledger_path = repo_root / ACTION_LEDGER_REL

    request_dir.mkdir(parents=True, exist_ok=True)
    result_dir.mkdir(parents=True, exist_ok=True)
    sample_dir.mkdir(parents=True, exist_ok=True)
    ledger_path.parent.mkdir(parents=True, exist_ok=True)
    if not ledger_path.exists():
        ledger_path.write_text("", encoding="utf-8")

    policy_snapshot = {
        "schema_id": "TRANSFER_ACTION_RUNNER_POLICY_V0_1",
        "claim_boundary": "FOUNDATION_ONLY",
        "allowed_action_types": sorted(ALLOWED_ACTION_TYPES),
        "allowed_contours": sorted(ALLOWED_CONTOURS),
        "allowed_modes": sorted(ALLOWED_MODES),
        "safe_target_roots": SAFE_TARGET_ROOTS,
        "forbidden_request_fields": sorted(FORBIDDEN_REQUEST_FIELDS),
        "no_shell_true": True,
        "no_arbitrary_shell": True,
        "generated_at_utc": utc_now(),
    }
    write_json(repo_root / POLICY_SNAPSHOT_REL, policy_snapshot)

    return {
        "request_dir": request_dir,
        "result_dir": result_dir,
        "sample_dir": sample_dir,
        "ledger_path": ledger_path,
        "view_state": repo_root / VIEW_STATE_REL,
        "policy_snapshot": repo_root / POLICY_SNAPSHOT_REL,
    }


def default_artifact(action_id: str, task_id: str) -> tuple[str, str, str, str, str]:
    taskpack_name = "TASKPACK_TASK-20260523-NEWGEN-SANCTUM-TRANSFER-ACTION-RUNNER-VM3-V0_1.zip"
    taskpack_rel = (
        "INBOX/VM3_TASKPACKS/TASK-20260523-NEWGEN-SANCTUM-TRANSFER-ACTION-RUNNER-VM3-V0_1/"
        f"{taskpack_name}"
    )

    report_name = "TRANSFER_REPORT_BUNDLE_PLACEHOLDER.zip"
    report_rel = f"{BASE_REL}/REPORTS/{task_id}/{report_name}"

    if action_id == "FETCH_REPORT_BUNDLE_ZIP":
        return "VM3", "PC", "report_bundle", report_name, report_rel
    if action_id == "REGISTER_TRANSFER_RESULT":
        return "VM3", "PC", "report_bundle", report_name, report_rel
    return "PC", "VM3", "taskpack_zip", taskpack_name, taskpack_rel


def default_target_path(action_id: str, task_id: str, artifact_name: str) -> str:
    if action_id == "FETCH_REPORT_BUNDLE_ZIP":
        return f"/home/vboxuser3/IMPERIUM_WORK/Imperium-/IMPERIUM_NEW_GENERATION/SANCTUM_NG/TRANSFER_CONSOLE/REPORTS/{task_id}/{artifact_name}"
    return (
        f"/home/vboxuser3/IMPERIUM_WORK/Imperium-/INBOX/VM3_TASKPACKS/"
        f"{task_id}/{artifact_name}"
    )


def build_request_from_args(args: argparse.Namespace, repo_root: Path) -> dict[str, Any]:
    source_default, target_default, artifact_type_default, artifact_name_default, source_path_default = default_artifact(
        args.action_id,
        args.task_id,
    )

    action_type = str(args.action_id)
    source_contour = str(args.source_contour or source_default).upper()
    target_contour = str(args.target_contour or target_default).upper()
    artifact_type = str(args.artifact_type or artifact_type_default)
    artifact_name = str(args.artifact_name or artifact_name_default)
    source_path = str(args.source_path or source_path_default)
    target_path = str(args.target_path or default_target_path(action_type, args.task_id, artifact_name))
    mode = str(args.mode or "DRY_RUN").upper()

    owner_approval_required = action_type in {"SEND_TASKPACK_ZIP", "FETCH_REPORT_BUNDLE_ZIP"}
    owner_approved = bool(args.owner_approved)

    if action_type in {"DRY_RUN_TRANSFER", "VALIDATE_TRANSFER_REQUEST", "REGISTER_TRANSFER_RESULT"}:
        owner_approval_required = False

    command_profile = "DRY_RUN_ONLY" if mode == "DRY_RUN" else "PROFILE_NOT_READY"
    if mode == "EXECUTE" and source_contour == "VM3" and target_contour == "VM3":
        command_profile = "VM3_LOCAL_COPY"

    request = {
        "schema_id": "TRANSFER_ACTION_REQUEST_V0_1",
        "request_id": new_id("TRANSFER-ACTION-REQ"),
        "task_id": str(args.task_id),
        "action_type": action_type,
        "source_contour": source_contour,
        "target_contour": target_contour,
        "artifact_type": artifact_type,
        "artifact_name": artifact_name,
        "source_path": source_path,
        "target_path": target_path,
        "mode": mode,
        "owner_approval_required": owner_approval_required,
        "owner_approved": owner_approved,
        "rollback_plan": ROLLBACK_POLICY_REL,
        "allowed_command_profile": command_profile,
        "created_at_utc": utc_now(),
        "status": "REQUESTED",
        "claim_boundary": "FOUNDATION_ONLY",
        "requester": str(args.requester),
        "no_arbitrary_shell_confirmed": True,
        "notes": [
            "Foundation-only transfer action runner request.",
            "No arbitrary shell command text is accepted."
        ],
    }

    if args.request_file:
        incoming = load_json(args.request_file.resolve())
        if incoming is not None:
            request = incoming
            request.setdefault("request_id", new_id("TRANSFER-ACTION-REQ"))
            request.setdefault("created_at_utc", utc_now())
            request.setdefault("claim_boundary", "FOUNDATION_ONLY")
            request.setdefault("schema_id", "TRANSFER_ACTION_REQUEST_V0_1")
            request.setdefault("requester", str(args.requester))
            request.setdefault("no_arbitrary_shell_confirmed", True)

    _ = repo_root
    return request


def validate_request(request: dict[str, Any], repo_root: Path) -> tuple[list[str], list[str], list[str]]:
    errors: list[str] = []
    warnings: list[str] = []
    paths_verified: list[str] = []

    required_fields = [
        "schema_id",
        "request_id",
        "task_id",
        "action_type",
        "source_contour",
        "target_contour",
        "artifact_type",
        "artifact_name",
        "source_path",
        "target_path",
        "mode",
        "owner_approval_required",
        "owner_approved",
        "rollback_plan",
        "allowed_command_profile",
        "created_at_utc",
        "status",
        "claim_boundary",
    ]
    missing = [field for field in required_fields if field not in request]
    if missing:
        errors.append(f"missing_fields:{missing}")

    schema_id = str(request.get("schema_id", ""))
    if schema_id != "TRANSFER_ACTION_REQUEST_V0_1":
        errors.append(f"invalid_schema_id:{schema_id}")

    forbidden = sorted([field for field in request.keys() if field in FORBIDDEN_REQUEST_FIELDS])
    if forbidden:
        errors.append(f"forbidden_request_fields:{forbidden}")

    action_type = str(request.get("action_type", ""))
    if action_type not in ALLOWED_ACTION_TYPES:
        errors.append(f"unknown_action_type:{action_type}")

    source_contour = str(request.get("source_contour", "")).upper()
    target_contour = str(request.get("target_contour", "")).upper()
    if source_contour not in ALLOWED_CONTOURS:
        errors.append(f"unknown_source_contour:{source_contour}")
    if target_contour not in ALLOWED_CONTOURS:
        errors.append(f"unknown_target_contour:{target_contour}")

    mode = str(request.get("mode", "")).upper()
    if mode not in ALLOWED_MODES:
        errors.append(f"unsupported_mode:{mode}")

    artifact_type = str(request.get("artifact_type", ""))
    if artifact_type not in {"taskpack_zip", "report_bundle"}:
        errors.append(f"unsupported_artifact_type:{artifact_type}")

    source_path = str(request.get("source_path", ""))
    target_path = str(request.get("target_path", ""))

    source_safe, source_resolved = is_safe_path(source_path, repo_root)
    target_safe, target_resolved = is_safe_path(target_path, repo_root)
    if not source_safe:
        errors.append(f"unsafe_source_path:{source_path}")
    else:
        paths_verified.append(source_resolved)

    if not target_safe:
        errors.append(f"unsafe_target_path:{target_path}")
    else:
        paths_verified.append(target_resolved)

    owner_approval_required = bool(request.get("owner_approval_required", False))
    owner_approved = bool(request.get("owner_approved", False))
    if mode == "EXECUTE" and owner_approval_required and not owner_approved:
        errors.append("execute_requires_owner_approval")

    claim_boundary = str(request.get("claim_boundary", ""))
    if claim_boundary != "FOUNDATION_ONLY":
        errors.append(f"invalid_claim_boundary:{claim_boundary}")

    profile = str(request.get("allowed_command_profile", ""))
    if profile not in {"DRY_RUN_ONLY", "VM3_LOCAL_COPY", "PROFILE_NOT_READY"}:
        warnings.append(f"unknown_command_profile:{profile}")

    return errors, warnings, paths_verified


def write_request_record(request: dict[str, Any], request_dir: Path, repo_root: Path) -> tuple[Path, str]:
    request_id = str(request.get("request_id") or new_id("TRANSFER-ACTION-REQ"))
    request["request_id"] = request_id
    request_path = request_dir / f"{request_id}.json"
    write_json(request_path, request)
    return request_path, relpath(request_path, repo_root)


def run_local_copy(source: Path, target: Path) -> tuple[bool, str]:
    target.parent.mkdir(parents=True, exist_ok=True)
    proc = subprocess.run(
        ["cp", "--", str(source), str(target)],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        check=False,
    )
    if proc.returncode == 0:
        return True, proc.stdout.strip()
    err = proc.stderr.strip() or proc.stdout.strip() or f"cp_returncode_{proc.returncode}"
    return False, err


def build_result(
    request: dict[str, Any],
    status: str,
    evidence_refs: list[str],
    paths_verified: list[str],
    limitations: list[str],
    error: str | None,
    sha_before: str | None,
    sha_after: str | None,
) -> dict[str, Any]:
    return {
        "schema_id": "TRANSFER_ACTION_RESULT_V0_1",
        "result_id": new_id("TRANSFER-ACTION-RESULT"),
        "request_id": str(request.get("request_id", "UNKNOWN_REQUEST")),
        "task_id": str(request.get("task_id", TASK_ID_DEFAULT)),
        "action_type": str(request.get("action_type", "UNKNOWN_ACTION")),
        "status": status,
        "started_at_utc": utc_now(),
        "finished_at_utc": utc_now(),
        "evidence_refs": evidence_refs,
        "stdout_log_ref": None,
        "stderr_log_ref": None,
        "paths_verified": paths_verified,
        "sha256_before_after": {
            "before": sha_before,
            "after": sha_after,
        },
        "no_arbitrary_shell_confirmed": True,
        "limitations": limitations,
        "claim_boundary": "FOUNDATION_ONLY",
        "error": error,
        "mode": str(request.get("mode", "DRY_RUN")),
    }


def run_action_logic(
    request: dict[str, Any],
    request_ref: str,
    repo_root: Path,
) -> dict[str, Any]:
    action_type = str(request.get("action_type", ""))
    mode = str(request.get("mode", "DRY_RUN")).upper()
    errors, warnings, paths_verified = validate_request(request, repo_root)

    limitations = [
        "Foundation-only transfer action runner.",
        "No production remote orchestration claim.",
        "No arbitrary shell execution path is accepted.",
    ]
    if warnings:
        limitations.extend([f"warn:{item}" for item in warnings])

    source_abs = resolve_candidate_path(str(request.get("source_path", "")), repo_root)
    target_abs = resolve_candidate_path(str(request.get("target_path", "")), repo_root)

    evidence_refs = [
        request_ref,
        REQUEST_SCHEMA_REL,
        RESULT_SCHEMA_REL,
        POLICY_SCHEMA_REL,
        POLICY_SNAPSHOT_REL,
    ]

    if errors:
        result = build_result(
            request=request,
            status="BLOCKED",
            evidence_refs=evidence_refs,
            paths_verified=paths_verified,
            limitations=limitations + [f"error:{item}" for item in errors],
            error="; ".join(errors),
            sha_before=sha256_file(source_abs),
            sha_after=sha256_file(target_abs),
        )
        return result

    if action_type == "VALIDATE_TRANSFER_REQUEST":
        result = build_result(
            request=request,
            status="REGISTERED",
            evidence_refs=evidence_refs,
            paths_verified=paths_verified,
            limitations=limitations + ["Validation-only action; no transfer attempt."],
            error=None,
            sha_before=sha256_file(source_abs),
            sha_after=sha256_file(target_abs),
        )
        return result

    if action_type == "REGISTER_TRANSFER_RESULT":
        result = build_result(
            request=request,
            status="REGISTERED",
            evidence_refs=evidence_refs,
            paths_verified=paths_verified,
            limitations=limitations + ["Result registration action only; no transfer execution."],
            error=None,
            sha_before=sha256_file(source_abs),
            sha_after=sha256_file(target_abs),
        )
        return result

    if mode == "DRY_RUN" or action_type == "DRY_RUN_TRANSFER":
        result = build_result(
            request=request,
            status="DRY_RUN_OK",
            evidence_refs=evidence_refs,
            paths_verified=paths_verified,
            limitations=limitations + ["Dry-run proof only. No live send/fetch executed."],
            error=None,
            sha_before=sha256_file(source_abs),
            sha_after=None,
        )
        return result

    owner_approval_required = bool(request.get("owner_approval_required", False))
    owner_approved = bool(request.get("owner_approved", False))
    profile = str(request.get("allowed_command_profile", "PROFILE_NOT_READY"))

    if mode == "EXECUTE" and owner_approval_required and not owner_approved:
        result = build_result(
            request=request,
            status="BLOCKED",
            evidence_refs=evidence_refs,
            paths_verified=paths_verified,
            limitations=limitations + ["Execute mode blocked: owner_approved=false."],
            error="owner approval missing",
            sha_before=sha256_file(source_abs),
            sha_after=sha256_file(target_abs),
        )
        return result

    if profile == "VM3_LOCAL_COPY" and str(request.get("source_contour", "")).upper() == "VM3" and str(request.get("target_contour", "")).upper() == "VM3":
        if not source_abs.exists() or not source_abs.is_file():
            return build_result(
                request=request,
                status="NOT_READY",
                evidence_refs=evidence_refs,
                paths_verified=paths_verified,
                limitations=limitations + ["VM3 local copy profile selected but source file does not exist."],
                error="source_file_missing",
                sha_before=None,
                sha_after=None,
            )

        before_hash = sha256_file(source_abs)
        ok, copy_detail = run_local_copy(source_abs, target_abs)
        after_hash = sha256_file(target_abs)

        if ok:
            status = "SENT" if action_type == "SEND_TASKPACK_ZIP" else "FETCHED"
            return build_result(
                request=request,
                status=status,
                evidence_refs=evidence_refs + [str(target_abs)],
                paths_verified=paths_verified,
                limitations=limitations + ["Execute mode used bounded local VM3 copy profile."],
                error=None,
                sha_before=before_hash,
                sha_after=after_hash,
            )

        return build_result(
            request=request,
            status="FAILED",
            evidence_refs=evidence_refs,
            paths_verified=paths_verified,
            limitations=limitations + ["Local bounded copy failed."],
            error=copy_detail,
            sha_before=before_hash,
            sha_after=after_hash,
        )

    return build_result(
        request=request,
        status="NOT_READY",
        evidence_refs=evidence_refs,
        paths_verified=paths_verified,
        limitations=limitations + [
            "Execute profile for multi-contour live transfer is not proven on VM3 in this task.",
            "Use dry-run receipts or owner-approved contour-specific route enablement task."
        ],
        error=None,
        sha_before=sha256_file(source_abs),
        sha_after=sha256_file(target_abs),
    )


def write_result_record(result: dict[str, Any], result_dir: Path, repo_root: Path) -> tuple[Path, str]:
    result_id = str(result.get("result_id") or new_id("TRANSFER-ACTION-RESULT"))
    result["result_id"] = result_id
    result_path = result_dir / f"{result_id}.json"
    write_json(result_path, result)
    return result_path, relpath(result_path, repo_root)


def append_ledger(
    ledger_path: Path,
    action_id: str,
    request_ref: str,
    result_ref: str,
    result_status: str,
    mode: str,
) -> None:
    entry = {
        "schema_id": "TRANSFER_ACTION_RUNNER_LEDGER_ENTRY_V0_1",
        "entry_id": new_id("TRANSFER-ACTION-LEDGER"),
        "timestamp_utc": utc_now(),
        "action_id": action_id,
        "request_ref": request_ref,
        "result_ref": result_ref,
        "result_status": result_status,
        "mode": mode,
        "claim_boundary": "FOUNDATION_ONLY",
    }
    append_jsonl(ledger_path, entry)


def ensure_transfer_view_seed(task_id: str) -> dict[str, Any]:
    return {
        "schema_id": "TRANSFER_CONSOLE_VIEW_STATE_V0_1",
        "task_id": task_id,
        "generated_at_utc": utc_now(),
        "claim_boundary": "FOUNDATION_ONLY",
        "contour_cards": [],
        "latest_requests": [],
        "latest_results": [],
        "action_ledger": [],
        "transfer_routes": [],
        "source_refs": [],
        "context_source_mix": {
            "taskpack_percent": 70,
            "existing_newgen_repo_percent": 20,
            "owner_handoff_percent": 4,
            "organ_registry_percent": 2,
            "servitor_inference_percent": 4,
            "external_local_private_percent": 0,
        },
        "truth_labels": [
            "FOUNDATION_ONLY",
            "NO_PRODUCTION_REMOTE_ORCHESTRATION",
            "NO_ARBITRARY_SHELL",
            "NO_FAKE_GREEN",
        ],
    }


def refresh_view_state(
    repo_root: Path,
    task_id: str,
    layout: dict[str, Path],
    last_action_id: str,
    request_ref: str,
    result_ref: str,
) -> str:
    view_path = layout["view_state"]
    view = load_json(view_path)
    if view is None:
        view = ensure_transfer_view_seed(task_id)

    latest_action_requests: list[dict[str, Any]] = []
    for item in list_json_records(layout["request_dir"])[:12]:
        clean = {k: v for k, v in item.items() if k != "_path"}
        clean["source_record_path"] = relpath(Path(item["_path"]), repo_root)
        latest_action_requests.append(clean)

    latest_action_results: list[dict[str, Any]] = []
    for item in list_json_records(layout["result_dir"])[:12]:
        clean = {k: v for k, v in item.items() if k != "_path"}
        clean["source_record_path"] = relpath(Path(item["_path"]), repo_root)
        latest_action_results.append(clean)

    runner_ledger = list_jsonl(layout["ledger_path"])

    view["generated_at_utc"] = utc_now()
    view["task_id"] = task_id
    view["claim_boundary"] = "FOUNDATION_ONLY"

    action_runner_state = {
        "schema_id": "TRANSFER_ACTION_RUNNER_STATE_V0_1",
        "generated_at_utc": utc_now(),
        "claim_boundary": "FOUNDATION_ONLY",
        "no_arbitrary_shell_confirmed": True,
        "supported_action_types": sorted(ALLOWED_ACTION_TYPES),
        "allowed_contours": sorted(ALLOWED_CONTOURS),
        "safe_target_roots": SAFE_TARGET_ROOTS,
        "latest_action_requests": latest_action_requests,
        "latest_action_results": latest_action_results,
        "latest_runner_ledger": runner_ledger[-40:],
        "last_action": {
            "action_id": last_action_id,
            "request_ref": request_ref,
            "result_ref": result_ref,
        },
        "status_labels": [
            "DRY_RUN_OK",
            "SENT",
            "FETCHED",
            "REGISTERED",
            "FAILED",
            "BLOCKED",
            "NOT_READY",
            "PREVIEW_ONLY",
            "NOT_WIRED",
        ],
        "known_limitations": [
            "Foundation-only action runner state.",
            "No production remote orchestration claim.",
            "Execute path may return NOT_READY without proven contour command profile."
        ],
    }
    view["action_runner_state"] = action_runner_state

    source_refs = view.get("source_refs", [])
    if not isinstance(source_refs, list):
        source_refs = []
    for item in [
        REQUEST_SCHEMA_REL,
        RESULT_SCHEMA_REL,
        POLICY_SCHEMA_REL,
        ACTION_REQUEST_DIR_REL,
        ACTION_RESULT_DIR_REL,
        ACTION_LEDGER_REL,
        POLICY_SNAPSHOT_REL,
    ]:
        if item not in source_refs:
            source_refs.append(item)
    view["source_refs"] = source_refs

    truth_labels = view.get("truth_labels", [])
    if not isinstance(truth_labels, list):
        truth_labels = []
    for label in [
        "FOUNDATION_ONLY",
        "NO_PRODUCTION_REMOTE_ORCHESTRATION",
        "NO_ARBITRARY_SHELL",
        "NO_FAKE_GREEN",
        "TRANSFER_ACTION_RUNNER_FOUNDATION",
    ]:
        if label not in truth_labels:
            truth_labels.append(label)
    view["truth_labels"] = truth_labels

    write_json(view_path, view)
    return relpath(view_path, repo_root)


def runner_status_from_result_status(result_status: str) -> str:
    if result_status in {"DRY_RUN_OK", "REGISTERED", "SENT", "FETCHED"}:
        return "PASS"
    if result_status == "NOT_READY":
        return "WARN"
    return "BLOCK"


def action_report(
    task_id: str,
    action_id: str,
    runner_status: str,
    request_ref: str,
    result_ref: str,
    view_state_ref: str,
    result: dict[str, Any],
) -> dict[str, Any]:
    return {
        "schema_id": "TRANSFER_ACTION_RUNNER_ACTION_REPORT_V0_1",
        "task_id": task_id,
        "generated_at_utc": utc_now(),
        "action_id": action_id,
        "status": runner_status,
        "result_status": str(result.get("status", "BLOCKED")),
        "request_ref": request_ref,
        "result_ref": result_ref,
        "view_state_ref": view_state_ref,
        "evidence_refs": list(result.get("evidence_refs", [])),
        "no_arbitrary_shell_confirmed": bool(result.get("no_arbitrary_shell_confirmed", False)),
        "claim_boundary": "FOUNDATION_ONLY",
        "known_limitations": list(result.get("limitations", [])),
        "not_proven": [
            "Production remote orchestration is not proven by this foundation action runner.",
            "SENT/FETCHED states require bounded evidence refs and may be NOT_READY in multi-contour mode."
        ],
    }


def parse_args() -> argparse.Namespace:
    script_path = Path(__file__).resolve()
    default_repo_root = script_path.parents[4]
    default_report_dir = default_repo_root / f"{BASE_REL}/REPORTS/{TASK_ID_DEFAULT}"

    parser = argparse.ArgumentParser(description="Run bounded Transfer Action Runner action.")
    parser.add_argument("--repo-root", type=Path, default=default_repo_root)
    parser.add_argument("--task-id", default=TASK_ID_DEFAULT)
    parser.add_argument("--action-id", required=True, choices=sorted(ALLOWED_ACTION_TYPES))
    parser.add_argument("--request-file", type=Path, default=None)
    parser.add_argument("--source-contour", default=None)
    parser.add_argument("--target-contour", default=None)
    parser.add_argument("--artifact-type", default=None)
    parser.add_argument("--artifact-name", default=None)
    parser.add_argument("--source-path", default=None)
    parser.add_argument("--target-path", default=None)
    parser.add_argument("--mode", default="DRY_RUN", choices=sorted(ALLOWED_MODES))
    parser.add_argument("--owner-approved", action="store_true")
    parser.add_argument("--requester", default="SANCTUM_NG_TRANSFER_ACTION_RUNNER")
    parser.add_argument("--report-dir", type=Path, default=default_report_dir)
    parser.add_argument("--output-report", type=Path, default=None)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    repo_root = args.repo_root.resolve()
    task_id = str(args.task_id)
    action_id = str(args.action_id)

    layout = ensure_layout(repo_root)

    request = build_request_from_args(args, repo_root)
    request["task_id"] = task_id
    if "action_type" not in request:
        request["action_type"] = action_id
    if action_id != "VALIDATE_TRANSFER_REQUEST":
        request["action_type"] = action_id
    request_path, request_ref = write_request_record(request, layout["request_dir"], repo_root)
    _ = request_path

    result = run_action_logic(request, request_ref=request_ref, repo_root=repo_root)
    result_path, result_ref = write_result_record(result, layout["result_dir"], repo_root)
    _ = result_path

    append_ledger(
        ledger_path=layout["ledger_path"],
        action_id=action_id,
        request_ref=request_ref,
        result_ref=result_ref,
        result_status=str(result.get("status", "BLOCKED")),
        mode=str(request.get("mode", "DRY_RUN")),
    )

    view_state_ref = refresh_view_state(
        repo_root=repo_root,
        task_id=task_id,
        layout=layout,
        last_action_id=action_id,
        request_ref=request_ref,
        result_ref=result_ref,
    )

    runner_status = runner_status_from_result_status(str(result.get("status", "BLOCKED")))
    report_payload = action_report(
        task_id=task_id,
        action_id=action_id,
        runner_status=runner_status,
        request_ref=request_ref,
        result_ref=result_ref,
        view_state_ref=view_state_ref,
        result=result,
    )

    report_dir = args.report_dir.resolve()
    report_dir.mkdir(parents=True, exist_ok=True)
    if args.output_report is None:
        report_path = report_dir / "ACTION_LOGS" / "TRANSFER_ACTION_RUNNER_REPORTS" / f"{new_id('ACTION-RUNNER-REPORT')}.json"
    else:
        report_path = args.output_report.resolve()

    write_json(report_path, report_payload)

    print(f"transfer_action_runner_status={runner_status}")
    print(f"transfer_action_runner_report={relpath(report_path, repo_root)}")
    print(f"transfer_action_request_ref={request_ref}")
    print(f"transfer_action_result_ref={result_ref}")
    print(f"transfer_console_view_state={view_state_ref}")

    return 0 if runner_status in {"PASS", "WARN"} else 1


if __name__ == "__main__":
    raise SystemExit(main())
