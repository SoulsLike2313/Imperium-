"""
Second Brain Neural Map V0.6 — HTTP Server
Runtime mode: PROTOTYPE_INTERACTIVE | RULE_BASED_ONLY | NO_LOCAL_LLM | NO_AGENT_API

V0.6 additions:
  POST /api/tasks/register      → Create full machine-readable task package
  GET  /api/tasks/<id>          → Full task object with package_path
  GET  /api/tasks/<id>/validation → Validation report for task package
  POST /api/tasks/launch        → Create servitor handoff block + launch receipt
  GET  /api/task_packages       → List all task packages with count

Port: 8767
"""

import json
import os
import sys
import subprocess
import datetime
import uuid
import shutil
import time
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse

# ── Paths ──────────────────────────────────────────────────────────────────────
APP_DIR          = os.path.dirname(os.path.abspath(__file__))
V06_ROOT         = os.path.dirname(APP_DIR)
SECOND_BRAIN     = os.path.dirname(V06_ROOT)
TEST_VERSION     = os.path.dirname(SECOND_BRAIN)
REPO_ROOT        = os.path.dirname(TEST_VERSION)

REGISTRY_DIR     = os.path.join(V06_ROOT, "registry")
REPORTS_DIR      = os.path.join(V06_ROOT, "reports")
TOOLS_DIR        = os.path.join(V06_ROOT, "tools")
TRUTH_LOCK_DIR   = os.path.join(V06_ROOT, "TRUTH_LOCK_V0_2")

SNAPSHOT_FILE    = os.path.join(REPORTS_DIR, "neural_snapshot_live.json")
SNAPSHOT_BUILDER = os.path.join(TOOLS_DIR, "snapshot_builder_v0_6.py")
STALENESS_POLICY_FILE = os.path.join(TRUTH_LOCK_DIR, "contracts", "staleness_policy_v0_2.json")

TASKS_FILE       = os.path.join(SECOND_BRAIN, "MEMORY_ZONES", "TASK_INTAKE", "accepted_tasks.json")
COMMENTS_FILE    = os.path.join(SECOND_BRAIN, "MEMORY_ZONES", "OWNER_COMMENTS", "owner_comments_runtime.json")
LINKS_FILE       = os.path.join(SECOND_BRAIN, "MEMORY_ZONES", "MEMORY_LINKS", "task_comment_links.json")
RECEIPTS_DIR     = os.path.join(SECOND_BRAIN, "RUNTIME", "receipts")
EXPORTS_DIR      = os.path.join(SECOND_BRAIN, "RUNTIME", "exports")
TASK_PACKAGES_DIR = os.path.join(SECOND_BRAIN, "RUNTIME", "task_packages")

PORT = 8767

DEFAULT_STALENESS_POLICY = {
    "max_snapshot_age_seconds": 900,
    "stale_warning_threshold_seconds": 300,
    "stale_failure_threshold_seconds": 900,
}

RUNTIME_STATUS = {
    "version": "V0.6",
    "mode": "PROTOTYPE_INTERACTIVE",
    "rule_based": True,
    "no_local_llm": True,
    "no_agent_api": True,
    "not_production_ready": True,
    "server": f"localhost:{PORT}",
    "honest_status": ["PROTOTYPE_INTERACTIVE", "RULE_BASED_ONLY", "NO_LOCAL_LLM", "NO_AGENT_API"]
}

API_LATENCY_MS_BY_ENDPOINT = {}
API_FAIL_COUNT_BY_ENDPOINT = {}
LAST_SNAPSHOT_BUILD_TIME_MS = None


# ── Utilities ──────────────────────────────────────────────────────────────────

def now_iso():
    return datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")

def now_stamp():
    return datetime.datetime.utcnow().strftime("%Y%m%d-%H%M%S")

def make_id(prefix):
    ts = datetime.datetime.utcnow().strftime("%Y%m%d-%H%M%S")
    suffix = str(uuid.uuid4().int)[:3].zfill(3)
    return f"{prefix}-{ts}-{suffix}"

def load_json(path):
    if not os.path.isfile(path):
        return None
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return None

def save_json(path, data):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def safe_relative(path):
    try:
        return os.path.relpath(path, REPO_ROOT).replace("\\", "/")
    except Exception:
        return path.replace("\\", "/")

def parse_utc_iso(iso_text):
    if not iso_text:
        return None
    try:
        return datetime.datetime.strptime(iso_text, "%Y-%m-%dT%H:%M:%SZ")
    except Exception:
        return None

def load_staleness_policy():
    policy = dict(DEFAULT_STALENESS_POLICY)
    data = load_json(STALENESS_POLICY_FILE)
    if isinstance(data, dict):
        for key in DEFAULT_STALENESS_POLICY:
            value = data.get(key)
            if isinstance(value, int) and value > 0:
                policy[key] = value
    return policy

def compute_snapshot_freshness(snapshot):
    policy = load_staleness_policy()
    result = {
        "snapshot_age_seconds": None,
        "snapshot_freshness_state": "MISSING",
        "stale_warning_threshold_seconds": policy["stale_warning_threshold_seconds"],
        "stale_failure_threshold_seconds": policy["stale_failure_threshold_seconds"],
        "max_snapshot_age_seconds": policy["max_snapshot_age_seconds"],
    }
    if not snapshot:
        return result
    dt = parse_utc_iso(snapshot.get("timestamp_utc"))
    if not dt:
        result["snapshot_freshness_state"] = "ERROR"
        return result
    age = int((datetime.datetime.utcnow() - dt).total_seconds())
    result["snapshot_age_seconds"] = max(age, 0)
    if age > policy["stale_failure_threshold_seconds"]:
        result["snapshot_freshness_state"] = "STALE"
    elif age > policy["stale_warning_threshold_seconds"]:
        result["snapshot_freshness_state"] = "WARNING"
    else:
        result["snapshot_freshness_state"] = "FRESH"
    return result

def update_api_metrics(endpoint, started_at, success=True):
    latency_ms = round((time.perf_counter() - started_at) * 1000.0, 2)
    API_LATENCY_MS_BY_ENDPOINT[endpoint] = latency_ms
    if not success:
        API_FAIL_COUNT_BY_ENDPOINT[endpoint] = API_FAIL_COUNT_BY_ENDPOINT.get(endpoint, 0) + 1

def write_receipt(receipt_id, event_type, status, object_type, object_id, paths_written):
    receipt = {
        "receipt_id": receipt_id,
        "created_at": now_iso(),
        "event_type": event_type,
        "status": status,
        "object_type": object_type,
        "object_id": object_id,
        "paths_written": paths_written,
        "checker_relevant": True,
        "no_llm_used": True,
        "no_external_agent_used": True,
        "seed_demo": False
    }
    os.makedirs(RECEIPTS_DIR, exist_ok=True)
    save_json(os.path.join(RECEIPTS_DIR, f"{receipt_id}.json"), receipt)
    return receipt

def count_task_packages():
    if not os.path.isdir(TASK_PACKAGES_DIR):
        return 0
    return len([d for d in os.listdir(TASK_PACKAGES_DIR)
                if os.path.isdir(os.path.join(TASK_PACKAGES_DIR, d))])


# ── Validation logic ───────────────────────────────────────────────────────────

def validate_task_package(body):
    """
    Validate task fields and compute machine_readiness_score.
    Returns (verdict, score, checks, warnings, blockers).
    """
    checks = {}
    warnings = []
    blockers = []
    score = 0

    # task_title
    title = (body.get("task_title") or "").strip()
    if len(title) >= 5:
        checks["task_title"] = {"status": "OK", "value_length": len(title)}
        score += 1
    else:
        checks["task_title"] = {"status": "BLOCKER", "reason": "Required, min 5 chars"}
        blockers.append("task_title is empty or too short")

    # task_description
    desc = (body.get("task_description") or "").strip()
    if len(desc) >= 20:
        checks["task_description"] = {"status": "OK", "value_length": len(desc)}
        score += 1
    else:
        checks["task_description"] = {"status": "BLOCKER", "reason": "Required, min 20 chars"}
        blockers.append("task_description is empty or too short")

    # pass_criteria
    pass_raw = (body.get("pass_criteria") or "").strip()
    pass_lines = [l.strip() for l in pass_raw.splitlines() if l.strip()]
    if len(pass_lines) >= 1:
        checks["pass_criteria"] = {"status": "OK", "count": len(pass_lines)}
        score += 2
        if any(len(l) < 15 for l in pass_lines):
            warnings.append("One or more pass criteria may be too vague (< 15 chars)")
    else:
        checks["pass_criteria"] = {"status": "BLOCKER", "reason": "Required, min 1 criterion"}
        blockers.append("pass_criteria is empty")

    # fail_criteria
    fail_raw = (body.get("fail_criteria") or "").strip()
    fail_lines = [l.strip() for l in fail_raw.splitlines() if l.strip()]
    if len(fail_lines) >= 1:
        checks["fail_criteria"] = {"status": "OK", "count": len(fail_lines)}
        score += 2
    else:
        checks["fail_criteria"] = {"status": "BLOCKER", "reason": "Required, min 1 criterion"}
        blockers.append("fail_criteria is empty")

    # stop_conditions
    stop_raw = (body.get("stop_conditions") or "").strip()
    stop_lines = [l.strip() for l in stop_raw.splitlines() if l.strip()]
    if len(stop_lines) >= 1:
        checks["stop_conditions"] = {"status": "OK", "count": len(stop_lines)}
        score += 1
    else:
        checks["stop_conditions"] = {"status": "BLOCKER", "reason": "Required, min 1 condition"}
        blockers.append("stop_conditions is empty")

    # scope_paths
    scope_raw = (body.get("scope_paths") or "").strip()
    scope_lines = [l.strip() for l in scope_raw.splitlines() if l.strip()]
    all_within = all("IMPERIUM_TEST_VERSION" in p for p in scope_lines)
    if len(scope_lines) >= 1 and all_within:
        checks["scope_paths"] = {"status": "OK", "count": len(scope_lines), "all_within_test_version": True}
        score += 2
    elif len(scope_lines) >= 1 and not all_within:
        checks["scope_paths"] = {"status": "BLOCKER", "reason": "Path outside IMPERIUM_TEST_VERSION boundary"}
        blockers.append("scope_paths contains path outside allowed boundary")
    else:
        checks["scope_paths"] = {"status": "BLOCKER", "reason": "Required, min 1 path"}
        blockers.append("scope_paths is empty — Servitor cannot know what to touch")

    # forbidden_paths (optional)
    forbidden_raw = (body.get("forbidden_paths") or "").strip()
    if forbidden_raw:
        checks["forbidden_paths"] = {"status": "OK"}
    else:
        checks["forbidden_paths"] = {"status": "EMPTY", "severity": "WARNING"}
        warnings.append("forbidden_paths is empty — recommended to define")

    # owner_comment (optional but adds score)
    comment_text = (body.get("comment_text") or "").strip()
    if comment_text:
        checks["owner_comment"] = {"status": "PROVIDED"}
        score += 1
    else:
        checks["owner_comment"] = {"status": "EMPTY", "severity": "INFO"}

    # Determine verdict
    if blockers:
        if score < 4:
            verdict = "NOT_MACHINE_READABLE"
        else:
            verdict = "BLOCKED_INCOMPLETE"
    elif warnings:
        verdict = "OWNER_REVIEW_REQUIRED"
    else:
        verdict = "READY_FOR_LAUNCH"

    return verdict, score, checks, warnings, blockers


# ── Package builder ────────────────────────────────────────────────────────────

def build_task_package(task_id, body, verdict, score, checks, warnings, blockers,
                       comment_id=None, link_id=None,
                       task_receipt_id=None, comment_receipt_id=None, link_receipt_id=None):
    """
    Create all files in RUNTIME/task_packages/{task_id}/
    Returns package_dir path.
    """
    os.makedirs(TASK_PACKAGES_DIR, exist_ok=True)
    pkg_dir = os.path.join(TASK_PACKAGES_DIR, task_id)
    os.makedirs(pkg_dir, exist_ok=True)

    scope_lines = [l.strip() for l in (body.get("scope_paths") or "").splitlines() if l.strip()]
    forbidden_lines = [l.strip() for l in (body.get("forbidden_paths") or "").splitlines() if l.strip()]
    allowed_lines = [l.strip() for l in (body.get("allowed_actions") or "").splitlines() if l.strip()]
    forbidden_action_lines = [l.strip() for l in (body.get("forbidden_actions") or "").splitlines() if l.strip()]
    pass_lines = [l.strip() for l in (body.get("pass_criteria") or "").splitlines() if l.strip()]
    fail_lines = [l.strip() for l in (body.get("fail_criteria") or "").splitlines() if l.strip()]
    stop_lines = [l.strip() for l in (body.get("stop_conditions") or "").splitlines() if l.strip()]

    receipts_list = [r for r in [task_receipt_id, comment_receipt_id, link_receipt_id] if r]

    # ── task_manifest.json ────────────────────────────────────────────────────
    package_files = {
        "pass_fail_criteria": "pass_fail_criteria.json",
        "scope_policy": "scope_policy.json",
        "allowed_forbidden_actions": "allowed_forbidden_actions.json",
        "validation_report": "validation_report.json",
        "servitor_handoff_block": "servitor_handoff_block.md"
    }
    if comment_id:
        package_files["owner_comment"] = "owner_comment.json"
    if link_id:
        package_files["task_comment_link"] = "task_comment_link.json"

    manifest = {
        "schema": "task_manifest.v0.6",
        "task_id": task_id,
        "created_at": now_iso(),
        "status": "TASK_REGISTERED",
        "runtime_mode": "PROTOTYPE_INTERACTIVE",
        "no_llm": True,
        "no_agent_api": True,
        "task_title": body.get("task_title", "").strip(),
        "task_description": body.get("task_description", "").strip(),
        "priority": body.get("priority", "MEDIUM"),
        "tags": [t.strip() for t in (body.get("tags") or "").split(",") if t.strip()],
        "notes": body.get("notes", "").strip(),
        "package_dir": safe_relative(pkg_dir),
        "package_files": package_files,
        "receipts": receipts_list,
        "machine_readiness_verdict": verdict,
        "machine_readiness_score": score,
        "created_by": "OWNER_INTERACTIVE",
        "seed_demo": False
    }
    save_json(os.path.join(pkg_dir, "task_manifest.json"), manifest)

    # ── pass_fail_criteria.json ───────────────────────────────────────────────
    save_json(os.path.join(pkg_dir, "pass_fail_criteria.json"), {
        "schema": "pass_fail_criteria.v0.6",
        "task_id": task_id,
        "pass_criteria": pass_lines,
        "fail_criteria": fail_lines,
        "stop_conditions": stop_lines,
        "criteria_count": {"pass": len(pass_lines), "fail": len(fail_lines), "stop": len(stop_lines)},
        "machine_readiness": "STRUCTURED" if (pass_lines and fail_lines and stop_lines) else "INCOMPLETE"
    })

    # ── scope_policy.json ─────────────────────────────────────────────────────
    scope_breadth = "NARROW" if len(scope_lines) <= 3 else "BROAD"
    scope_warnings = []
    if any("IMPERIUM_TEST_VERSION" == p.strip() for p in scope_lines):
        scope_warnings.append("Scope covers entire TEST_VERSION — consider narrowing")
    save_json(os.path.join(pkg_dir, "scope_policy.json"), {
        "schema": "scope_policy.v0.6",
        "task_id": task_id,
        "allowed_paths": scope_lines,
        "forbidden_paths": forbidden_lines,
        "scope_breadth": scope_breadth,
        "scope_warnings": scope_warnings,
        "execution_requirements": body.get("execution_requirements", "").strip()
    })

    # ── allowed_forbidden_actions.json ────────────────────────────────────────
    save_json(os.path.join(pkg_dir, "allowed_forbidden_actions.json"), {
        "schema": "allowed_forbidden_actions.v0.6",
        "task_id": task_id,
        "allowed_actions": allowed_lines if allowed_lines else ["Edit files in scope_paths", "Run py_compile"],
        "forbidden_actions": forbidden_action_lines if forbidden_action_lines else ["git commit", "git push", "Delete files"],
        "commit_allowed": False,
        "push_allowed": False,
        "delete_allowed": False
    })

    # ── owner_comment.json (if provided) ─────────────────────────────────────
    if comment_id:
        save_json(os.path.join(pkg_dir, "owner_comment.json"), {
            "schema": "owner_comment.v0.6",
            "comment_id": comment_id,
            "task_id": task_id,
            "created_at": now_iso(),
            "comment_text": body.get("comment_text", "").strip(),
            "comment_type": body.get("comment_type", "OBSERVATION"),
            "language": "auto",
            "linked_to_task": True,
            "receipt_id": comment_receipt_id
        })

    # ── task_comment_link.json (if provided) ──────────────────────────────────
    if link_id and comment_id:
        save_json(os.path.join(pkg_dir, "task_comment_link.json"), {
            "schema": "task_comment_link.v0.6",
            "link_id": link_id,
            "source_type": "TASK",
            "source_id": task_id,
            "target_type": "COMMENT",
            "target_id": comment_id,
            "link_reason": "Owner comment created during task registration",
            "receipt_id": link_receipt_id
        })

    # ── validation_report.json ────────────────────────────────────────────────
    save_json(os.path.join(pkg_dir, "validation_report.json"), {
        "schema": "validation_report.v0.6",
        "task_id": task_id,
        "validated_at": now_iso(),
        "verdict": verdict,
        "checks": checks,
        "warnings": warnings,
        "blockers": blockers,
        "machine_readiness_score": score,
        "machine_readiness_max": 10
    })

    # ── servitor_handoff_block.md (placeholder until Launch) ─────────────────
    handoff_placeholder = f"""=== SERVITOR HANDOFF BLOCK ===
Status:            TASK_REGISTERED (not yet launched)
Task ID:           {task_id}
Task Title:        {body.get("task_title", "").strip()}
Machine Verdict:   {verdict}

NOTE: This task has been registered but not yet launched.
NOTE: Press Launch Task to generate the final handoff block.
=== END HANDOFF BLOCK ===
"""
    with open(os.path.join(pkg_dir, "servitor_handoff_block.md"), "w", encoding="utf-8") as f:
        f.write(handoff_placeholder)

    return pkg_dir


# ── API handlers — existing (ported from V0.5) ─────────────────────────────────

def api_snapshot():
    snap = load_json(SNAPSHOT_FILE)
    if snap:
        freshness = compute_snapshot_freshness(snap)
        snap["snapshot_age_seconds"] = freshness["snapshot_age_seconds"]
        snap["snapshot_freshness_state"] = freshness["snapshot_freshness_state"]
        if "truth_lock_run_id" not in snap:
            snap["truth_lock_run_id"] = snap.get("snapshot_id", "UNKNOWN")
        return snap
    return {"error": "Snapshot not found. Run snapshot_builder_v0_6.py first.", "status": "MISSING"}


def api_status():
    snap = load_json(SNAPSHOT_FILE)
    counts = {"tasks": 0, "comments": 0, "links": 0, "receipts": 0, "task_packages": 0}
    td = load_json(TASKS_FILE)
    if td:
        counts["tasks"] = len(td.get("tasks", []))
    cd = load_json(COMMENTS_FILE)
    if cd:
        counts["comments"] = len(cd.get("comments", []))
    ld = load_json(LINKS_FILE)
    if ld:
        counts["links"] = len(ld.get("links", []))
    if os.path.isdir(RECEIPTS_DIR):
        counts["receipts"] = len([f for f in os.listdir(RECEIPTS_DIR) if f.endswith(".json")])
    counts["task_packages"] = count_task_packages()

    result = {**RUNTIME_STATUS, "counts": counts}
    freshness = compute_snapshot_freshness(snap)
    result.update(freshness)
    if snap:
        result["health_score"] = snap.get("health_score", "?/12")
        result["snapshot_id"] = snap.get("snapshot_id", "UNKNOWN")
        result["snapshot_timestamp"] = snap.get("timestamp_utc", "UNKNOWN")
        result["truth_lock_run_id"] = snap.get("truth_lock_run_id", snap.get("snapshot_id", "UNKNOWN"))
        result["partial_count"] = snap.get("partial_count", 0)
        result["blocked_count"] = snap.get("blocked_count", 0)
        result["missing_source_count"] = snap.get("total_missing_sources", 0)
        result["warning_count"] = snap.get("warning_count", 0)
        result["stale_count"] = 1 if freshness.get("snapshot_freshness_state") == "STALE" else 0
    else:
        result["health_score"] = "?/12"
        result["snapshot_id"] = "MISSING"
        result["snapshot_timestamp"] = "MISSING"
        result["truth_lock_run_id"] = "MISSING"
        result["partial_count"] = "NOT_IMPLEMENTED"
        result["blocked_count"] = "NOT_IMPLEMENTED"
        result["missing_source_count"] = "NOT_IMPLEMENTED"
        result["warning_count"] = "NOT_IMPLEMENTED"
        result["stale_count"] = "NOT_IMPLEMENTED"

    result["telemetry"] = {
        "snapshot_age_seconds": freshness.get("snapshot_age_seconds", "NOT_IMPLEMENTED"),
        "api_latency_ms_by_endpoint": API_LATENCY_MS_BY_ENDPOINT if API_LATENCY_MS_BY_ENDPOINT else "NOT_IMPLEMENTED",
        "failed_api_count": sum(API_FAIL_COUNT_BY_ENDPOINT.values()),
        "last_snapshot_build_time_ms": LAST_SNAPSHOT_BUILD_TIME_MS if LAST_SNAPSHOT_BUILD_TIME_MS is not None else "NOT_IMPLEMENTED",
        "zone_render_count": snap.get("zone_count") if snap else "NOT_IMPLEMENTED",
        "page_load_ms": "NOT_IMPLEMENTED",
        "console_error_count": "NOT_IMPLEMENTED",
        "network_error_count": "NOT_IMPLEMENTED",
    }
    return result


def api_get_tasks():
    d = load_json(TASKS_FILE) or {"tasks": []}
    return d.get("tasks", [])


def api_get_task_by_id(task_id):
    tasks = api_get_tasks()
    task = next((t for t in tasks if t["task_id"] == task_id), None)
    if not task:
        return None, f"Task {task_id} not found"
    pkg_dir = os.path.join(TASK_PACKAGES_DIR, task_id)
    if os.path.isdir(pkg_dir):
        task["package_path"] = safe_relative(pkg_dir)
        task["package_exists"] = True
        manifest = load_json(os.path.join(pkg_dir, "task_manifest.json"))
        if manifest:
            task["machine_readiness_verdict"] = manifest.get("machine_readiness_verdict", "UNKNOWN")
            task["machine_readiness_score"] = manifest.get("machine_readiness_score", 0)
    else:
        task["package_path"] = None
        task["package_exists"] = False
    return task, None


def api_get_task_validation(task_id):
    pkg_dir = os.path.join(TASK_PACKAGES_DIR, task_id)
    vr_path = os.path.join(pkg_dir, "validation_report.json")
    vr = load_json(vr_path)
    if not vr:
        return None, f"Validation report not found for {task_id}"
    return vr, None


def api_get_task_packages():
    if not os.path.isdir(TASK_PACKAGES_DIR):
        return {"status": "MISSING", "task_package_count": 0, "packages": []}
    dirs = [d for d in os.listdir(TASK_PACKAGES_DIR)
            if os.path.isdir(os.path.join(TASK_PACKAGES_DIR, d))]
    dirs.sort(key=lambda d: os.path.getmtime(os.path.join(TASK_PACKAGES_DIR, d)), reverse=True)
    packages = []
    for name in dirs[:25]:
        pkg_path = os.path.join(TASK_PACKAGES_DIR, name)
        manifest = load_json(os.path.join(pkg_path, "task_manifest.json"))
        packages.append({
            "task_id": name,
            "path": safe_relative(pkg_path),
            "manifest_status": "JSON_OK" if manifest else "NOT_FOUND",
            "task_title": manifest.get("task_title") if manifest else None,
            "status": manifest.get("status") if manifest else None,
            "verdict": manifest.get("machine_readiness_verdict") if manifest else None,
            "created_at": manifest.get("created_at") if manifest else None,
        })
    return {
        "status": "PASS",
        "task_package_count": len(dirs),
        "packages": packages
    }


def api_get_comments():
    d = load_json(COMMENTS_FILE) or {"comments": []}
    return d.get("comments", [])


def api_get_links():
    d = load_json(LINKS_FILE) or {"links": []}
    return d.get("links", [])


def api_receipts(limit=25):
    rows = []
    parse_errors = 0
    if os.path.isdir(RECEIPTS_DIR):
        files = [f for f in os.listdir(RECEIPTS_DIR) if f.endswith(".json")]
        files.sort(key=lambda fn: os.path.getmtime(os.path.join(RECEIPTS_DIR, fn)), reverse=True)
        for rf in files[:limit]:
            full = os.path.join(RECEIPTS_DIR, rf)
            payload = load_json(full)
            if payload is None:
                parse_errors += 1
                rows.append({"file": rf, "path": safe_relative(full), "parse_status": "ERROR"})
                continue
            rows.append({
                "file": rf,
                "path": safe_relative(full),
                "parse_status": "JSON_OK",
                "receipt_id": payload.get("receipt_id"),
                "event_type": payload.get("event_type"),
                "created_at": payload.get("created_at"),
                "no_llm_used": payload.get("no_llm_used"),
            })
    return {
        "status": "PASS" if os.path.isdir(RECEIPTS_DIR) else "MISSING",
        "read_only": True,
        "receipts_dir": safe_relative(RECEIPTS_DIR),
        "receipt_count": len([f for f in os.listdir(RECEIPTS_DIR) if f.endswith(".json")]) if os.path.isdir(RECEIPTS_DIR) else 0,
        "parse_errors": parse_errors,
        "latest_receipts": rows,
        "no_mutation_performed": True,
    }


def api_export_status(limit=10):
    response = {
        "status": "MISSING", "read_only": True,
        "exports_dir": safe_relative(EXPORTS_DIR),
        "export_dir_exists": os.path.isdir(EXPORTS_DIR),
        "export_count": 0, "latest_exports": [],
        "no_mutation_performed": True,
    }
    if not os.path.isdir(EXPORTS_DIR):
        return response
    export_dirs = [d for d in os.listdir(EXPORTS_DIR) if os.path.isdir(os.path.join(EXPORTS_DIR, d))]
    export_dirs.sort(key=lambda d: os.path.getmtime(os.path.join(EXPORTS_DIR, d)), reverse=True)
    response["export_count"] = len(export_dirs)
    response["status"] = "PASS"
    rows = []
    for name in export_dirs[:limit]:
        item_path = os.path.join(EXPORTS_DIR, name)
        manifest = load_json(os.path.join(item_path, "manifest.json"))
        rows.append({
            "export_dir": name,
            "path": safe_relative(item_path),
            "manifest_status": "JSON_OK" if isinstance(manifest, dict) else "NOT_FOUND",
            "export_id": manifest.get("export_id") if isinstance(manifest, dict) else None,
            "created_at": manifest.get("created_at") if isinstance(manifest, dict) else None,
        })
    response["latest_exports"] = rows
    return response


def api_get_thread(task_id):
    tasks = api_get_tasks()
    task = next((t for t in tasks if t["task_id"] == task_id), None)
    if not task:
        return None, f"Task {task_id} not found"
    links = api_get_links()
    comments = api_get_comments()
    task_links = [l for l in links if l["source_id"] == task_id or l["target_id"] == task_id]
    linked_ids = set()
    for l in task_links:
        if l.get("source_type") == "COMMENT":
            linked_ids.add(l["source_id"])
        if l.get("target_type") == "COMMENT":
            linked_ids.add(l["target_id"])
    linked_comments = [c for c in comments if c["comment_id"] in linked_ids]
    receipts = []
    if os.path.isdir(RECEIPTS_DIR):
        for rf in os.listdir(RECEIPTS_DIR):
            if rf.endswith(".json"):
                r = load_json(os.path.join(RECEIPTS_DIR, rf))
                if r and r.get("object_id") in ([task_id] + list(linked_ids)):
                    receipts.append(r)
    return {"task": task, "links": task_links, "comments": linked_comments,
            "receipts": receipts, "thread_status": "PROTOTYPE_INTERACTIVE"}, None


def api_export():
    stamp = now_stamp()
    export_dir = os.path.join(EXPORTS_DIR, f"export_{stamp}")
    os.makedirs(export_dir, exist_ok=True)
    exported = []
    for src in [TASKS_FILE, COMMENTS_FILE, LINKS_FILE]:
        if os.path.isfile(src):
            shutil.copy2(src, os.path.join(export_dir, os.path.basename(src)))
            exported.append(os.path.basename(src))
    if os.path.isdir(RECEIPTS_DIR):
        shutil.copytree(RECEIPTS_DIR, os.path.join(export_dir, "receipts"))
        exported.append("receipts/")
    manifest = {"export_id": f"EXP-{stamp}", "created_at": now_iso(),
                "exported_files": exported, "runtime_mode": "PROTOTYPE_INTERACTIVE", "no_llm": True}
    save_json(os.path.join(export_dir, "manifest.json"), manifest)
    return manifest, None


def api_rebuild_snapshot():
    global LAST_SNAPSHOT_BUILD_TIME_MS
    started = time.perf_counter()
    try:
        result = subprocess.run(
            [sys.executable, SNAPSHOT_BUILDER],
            capture_output=True, text=True, timeout=30
        )
        LAST_SNAPSHOT_BUILD_TIME_MS = round((time.perf_counter() - started) * 1000.0, 2)
        snap = load_json(SNAPSHOT_FILE)
        return {
            "status": "REBUILT" if result.returncode == 0 else "REBUILD_FAILED",
            "returncode": result.returncode,
            "stdout": result.stdout[-500:] if result.stdout else "",
            "build_time_ms": LAST_SNAPSHOT_BUILD_TIME_MS,
            "snapshot": snap
        }, None
    except Exception as e:
        LAST_SNAPSHOT_BUILD_TIME_MS = None
        return None, str(e)


# ── API handlers — V0.6 NEW ────────────────────────────────────────────────────

def api_register_task(body):
    """
    Full Task Intake Corridor registration.
    Creates task in accepted_tasks.json + full package in task_packages/.
    """
    # Validate
    verdict, score, checks, warnings, blockers = validate_task_package(body)

    task_id = make_id("TI")
    task_receipt_id = make_id("RCP")
    comment_id = None
    comment_receipt_id = None
    link_id = None
    link_receipt_id = None

    # Create task in accepted_tasks.json
    task = {
        "task_id": task_id,
        "created_at": now_iso(),
        "status": "TASK_REGISTERED",
        "task_title": body.get("task_title", "").strip(),
        "task_description": body.get("task_description", "").strip(),
        "source_text": body.get("task_title", "").strip(),
        "priority": body.get("priority", "MEDIUM"),
        "tags": [t.strip() for t in (body.get("tags") or "").split(",") if t.strip()],
        "scope_paths": [l.strip() for l in (body.get("scope_paths") or "").splitlines() if l.strip()],
        "pass_criteria_raw": body.get("pass_criteria", "").strip(),
        "fail_criteria_raw": body.get("fail_criteria", "").strip(),
        "stop_conditions_raw": body.get("stop_conditions", "").strip(),
        "machine_readiness_verdict": verdict,
        "machine_readiness_score": score,
        "relevant_memory_zones": ["TASK_INTAKE"],
        "created_by": "OWNER_INTERACTIVE",
        "runtime_mode": "PROTOTYPE_INTERACTIVE",
        "receipts": [task_receipt_id],
        "links": [],
        "next_expected_action": "OWNER_REVIEW",
        "seed_demo": False
    }
    d = load_json(TASKS_FILE) or {
        "schema_ref": "task_intake_v0.6",
        "runtime_mode": "PROTOTYPE_INTERACTIVE",
        "no_llm": True,
        "tasks": []
    }
    d["tasks"].append(task)
    save_json(TASKS_FILE, d)
    write_receipt(task_receipt_id, "TASK_PACKAGE_CREATED", "TASK_REGISTERED",
                  "TASK", task_id,
                  [safe_relative(TASKS_FILE)])

    # Create comment if provided
    comment_text = (body.get("comment_text") or "").strip()
    if comment_text:
        comment_id = make_id("OC")
        comment_receipt_id = make_id("RCP")
        comment = {
            "comment_id": comment_id,
            "created_at": now_iso(),
            "status": "LINKED",
            "original_text": comment_text,
            "comment_type": body.get("comment_type", "OBSERVATION"),
            "linked_zone": "TASK_INTAKE",
            "linked_tasks": [task_id],
            "receipts": [comment_receipt_id],
            "seed_demo": False
        }
        cd = load_json(COMMENTS_FILE) or {
            "schema_ref": "comment_v0.6",
            "runtime_mode": "PROTOTYPE_INTERACTIVE",
            "no_llm": True,
            "comments": []
        }
        cd["comments"].append(comment)
        save_json(COMMENTS_FILE, cd)
        write_receipt(comment_receipt_id, "CORRIDOR_COMMENT_CREATED", "COMMENT_CAPTURED",
                      "COMMENT", comment_id,
                      [safe_relative(COMMENTS_FILE)])

        # Create link
        link_id = make_id("ML")
        link_receipt_id = make_id("RCP")
        link = {
            "link_id": link_id,
            "created_at": now_iso(),
            "status": "LINK_CREATED",
            "source_type": "TASK",
            "source_id": task_id,
            "target_type": "COMMENT",
            "target_id": comment_id,
            "link_reason": "Owner comment created during task registration",
            "receipt_id": link_receipt_id,
            "seed_demo": False
        }
        ld = load_json(LINKS_FILE) or {
            "schema_ref": "memory_link_v0.6",
            "runtime_mode": "PROTOTYPE_INTERACTIVE",
            "no_llm": True,
            "links": []
        }
        ld["links"].append(link)
        save_json(LINKS_FILE, ld)
        # Update task links
        for t in d["tasks"]:
            if t["task_id"] == task_id:
                t.setdefault("links", []).append(link_id)
        save_json(TASKS_FILE, d)
        write_receipt(link_receipt_id, "CORRIDOR_LINK_CREATED", "LINK_CREATED",
                      "LINK", link_id,
                      [safe_relative(LINKS_FILE)])

    # Build package
    pkg_dir = build_task_package(
        task_id, body, verdict, score, checks, warnings, blockers,
        comment_id=comment_id, link_id=link_id,
        task_receipt_id=task_receipt_id,
        comment_receipt_id=comment_receipt_id,
        link_receipt_id=link_receipt_id
    )

    return {
        "task_id": task_id,
        "status": "TASK_REGISTERED",
        "machine_readiness_verdict": verdict,
        "machine_readiness_score": score,
        "package_path": safe_relative(pkg_dir),
        "receipts": [r for r in [task_receipt_id, comment_receipt_id, link_receipt_id] if r],
        "comment_id": comment_id,
        "link_id": link_id,
        "warnings": warnings,
        "blockers": blockers,
        "launch_allowed": verdict in ("READY_FOR_LAUNCH", "OWNER_REVIEW_REQUIRED")
    }, None


def api_launch_task(body):
    """
    Launch a registered task: create final handoff block + launch receipt.
    Does NOT execute the task. Produces exact handoff for Servitor.
    """
    task_id = (body.get("task_id") or "").strip()
    if not task_id:
        return None, "task_id is required"

    pkg_dir = os.path.join(TASK_PACKAGES_DIR, task_id)
    if not os.path.isdir(pkg_dir):
        return None, f"Task package not found for {task_id}"

    manifest = load_json(os.path.join(pkg_dir, "task_manifest.json"))
    if not manifest:
        return None, f"task_manifest.json not found for {task_id}"

    verdict = manifest.get("machine_readiness_verdict", "UNKNOWN")
    if verdict == "BLOCKED_INCOMPLETE" or verdict == "NOT_MACHINE_READABLE":
        return None, f"Launch blocked: verdict is {verdict}. Fix blockers first."

    launch_receipt_id = make_id("RCP")
    launched_at = now_iso()

    # Update manifest status
    manifest["status"] = "TASK_READY_FOR_SERVITOR"
    manifest["launched_at"] = launched_at
    manifest["launch_receipt_id"] = launch_receipt_id
    save_json(os.path.join(pkg_dir, "task_manifest.json"), manifest)

    # Update accepted_tasks.json
    d = load_json(TASKS_FILE) or {"tasks": []}
    for t in d.get("tasks", []):
        if t["task_id"] == task_id:
            t["status"] = "TASK_READY_FOR_SERVITOR"
            t["launched_at"] = launched_at
            t["launch_receipt_id"] = launch_receipt_id
    save_json(TASKS_FILE, d)

    # Build handoff block
    pkg_rel = safe_relative(pkg_dir)
    receipts_rel = safe_relative(RECEIPTS_DIR)
    comment_path = f"{pkg_rel}/owner_comment.json" if os.path.isfile(os.path.join(pkg_dir, "owner_comment.json")) else "NOT_PROVIDED"
    link_path = f"{pkg_rel}/task_comment_link.json" if os.path.isfile(os.path.join(pkg_dir, "task_comment_link.json")) else "NOT_PROVIDED"

    handoff_block = f"""=== SERVITOR HANDOFF BLOCK ===
Generated:         {launched_at}
Runtime:           PROTOTYPE_INTERACTIVE | RULE_BASED_ONLY | NO_LLM | NO_AGENT_API

TASK_ID:           {task_id}
TASK_TITLE:        {manifest.get("task_title", "")}
STATUS:            TASK_READY_FOR_SERVITOR
PRIORITY:          {manifest.get("priority", "MEDIUM")}
MACHINE_VERDICT:   {verdict}

\u2500\u2500 READ FIRST \u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500
READ_HERE_FIRST:   {pkg_rel}/task_manifest.json

\u2500\u2500 PACKAGE FILES \u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500
PACKAGE_DIR:       {pkg_rel}/
MANIFEST:          {pkg_rel}/task_manifest.json
PASS_FAIL:         {pkg_rel}/pass_fail_criteria.json
SCOPE:             {pkg_rel}/scope_policy.json
ACTIONS:           {pkg_rel}/allowed_forbidden_actions.json
COMMENT:           {comment_path}
LINK:              {link_path}
VALIDATION:        {pkg_rel}/validation_report.json
HANDOFF:           {pkg_rel}/servitor_handoff_block.md

\u2500\u2500 RECEIPTS \u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500
RECEIPTS_DIR:      {receipts_rel}/
LAUNCH_RECEIPT:    {receipts_rel}/{launch_receipt_id}.json

\u2500\u2500 CONSTRAINTS \u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500
NO_COMMIT:         true
NO_PUSH:           true
NO_AUTO_EXECUTION: true
SCOPE_BOUNDARY:    IMPERIUM_TEST_VERSION only

\u2500\u2500 NOTES \u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500
This system does NOT execute tasks automatically.
Servitor must read task_manifest.json first, then pass_fail_criteria.json.
All actions must stay within scope_policy.json allowed_paths.
=== END HANDOFF BLOCK ===
"""

    # Write final handoff block to package
    with open(os.path.join(pkg_dir, "servitor_handoff_block.md"), "w", encoding="utf-8") as f:
        f.write(handoff_block)

    # Write launch receipt
    write_receipt(launch_receipt_id, "TASK_LAUNCHED", "TASK_READY_FOR_SERVITOR",
                  "TASK", task_id,
                  [safe_relative(os.path.join(pkg_dir, "servitor_handoff_block.md"))])

    return {
        "task_id": task_id,
        "status": "TASK_READY_FOR_SERVITOR",
        "launched_at": launched_at,
        "launch_receipt_id": launch_receipt_id,
        "handoff_block": handoff_block,
        "package_path": pkg_rel,
        "handoff_path": f"{pkg_rel}/servitor_handoff_block.md"
    }, None


# ── HTTP Handler ───────────────────────────────────────────────────────────────

class NeuralMapHandler(BaseHTTPRequestHandler):

    def log_message(self, format, *args):
        print(f"[{self.log_date_time_string()}] {format % args}")

    def send_json(self, data, status=200):
        body = json.dumps(data, indent=2, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(body)

    def send_error_json(self, message, status=400):
        self.send_json({"error": message, "status": "ERROR"}, status)

    def send_api_json(self, endpoint, started_at, data, status=200):
        update_api_metrics(endpoint, started_at, success=(status < 400))
        self.send_json(data, status)

    def send_api_error(self, endpoint, started_at, message, status=400):
        update_api_metrics(endpoint, started_at, success=False)
        self.send_error_json(message, status)

    def send_file(self, path, content_type):
        if not os.path.isfile(path):
            self.send_response(404)
            self.end_headers()
            return
        with open(path, "rb") as f:
            data = f.read()
        self.send_response(200)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def read_body(self):
        length = int(self.headers.get("Content-Length", 0))
        if length == 0:
            return {}
        raw = self.rfile.read(length)
        try:
            return json.loads(raw.decode("utf-8"))
        except Exception:
            return {}

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def do_GET(self):
        started = time.perf_counter()
        parsed = urlparse(self.path)
        path = parsed.path.rstrip("/") or "/"

        if path in ("/", "/index.html"):
            self.send_file(os.path.join(APP_DIR, "neural_map_v0_6.html"), "text/html; charset=utf-8")
        elif path == "/neural_map_v0_6.css":
            self.send_file(os.path.join(APP_DIR, "neural_map_v0_6.css"), "text/css; charset=utf-8")
        elif path == "/neural_map_v0_6.js":
            self.send_file(os.path.join(APP_DIR, "neural_map_v0_6.js"), "application/javascript; charset=utf-8")
        elif path == "/api/snapshot":
            self.send_api_json("/api/snapshot", started, api_snapshot())
        elif path == "/api/status":
            self.send_api_json("/api/status", started, api_status())
        elif path == "/api/tasks":
            self.send_api_json("/api/tasks", started, api_get_tasks())
        elif path == "/api/task_packages":
            self.send_api_json("/api/task_packages", started, api_get_task_packages())
        elif path.startswith("/api/tasks/") and path.endswith("/validation"):
            task_id = path[len("/api/tasks/"):-len("/validation")]
            result, err = api_get_task_validation(task_id)
            if err:
                self.send_api_error("/api/tasks/validation", started, err, 404)
            else:
                self.send_api_json("/api/tasks/validation", started, result)
        elif path.startswith("/api/tasks/") and not path.endswith("/register") and not path.endswith("/launch"):
            task_id = path[len("/api/tasks/"):]
            result, err = api_get_task_by_id(task_id)
            if err:
                self.send_api_error("/api/tasks/id", started, err, 404)
            else:
                self.send_api_json("/api/tasks/id", started, result)
        elif path == "/api/comments":
            self.send_api_json("/api/comments", started, api_get_comments())
        elif path == "/api/links":
            self.send_api_json("/api/links", started, api_get_links())
        elif path == "/api/receipts":
            self.send_api_json("/api/receipts", started, api_receipts())
        elif path == "/api/export/status":
            self.send_api_json("/api/export/status", started, api_export_status())
        elif path.startswith("/api/thread/"):
            task_id = path[len("/api/thread/"):]
            result, err = api_get_thread(task_id)
            if err:
                self.send_api_error("/api/thread", started, err, 404)
            else:
                self.send_api_json("/api/thread", started, result)
        else:
            self.send_api_error(path, started, "Not found", 404)

    def do_POST(self):
        started = time.perf_counter()
        parsed = urlparse(self.path)
        path = parsed.path.rstrip("/")
        body = self.read_body()

        if path == "/api/tasks/register":
            result, err = api_register_task(body)
            if err:
                self.send_api_error("/api/tasks/register", started, err)
            else:
                self.send_api_json("/api/tasks/register", started, result, 201)
        elif path == "/api/tasks/launch":
            result, err = api_launch_task(body)
            if err:
                self.send_api_error("/api/tasks/launch", started, err, 400)
            else:
                self.send_api_json("/api/tasks/launch", started, result, 200)
        elif path == "/api/tasks":
            # Legacy simple task creation (backward compat)
            source_text = body.get("source_text", "").strip()
            if not source_text:
                self.send_api_error("/api/tasks", started, "source_text is required")
                return
            body["task_title"] = source_text
            body["task_description"] = source_text
            result, err = api_register_task(body)
            if err:
                self.send_api_error("/api/tasks", started, err)
            else:
                self.send_api_json("/api/tasks", started, result, 201)
        elif path == "/api/comments":
            original_text = body.get("original_text", "").strip()
            if not original_text:
                self.send_api_error("/api/comments", started, "original_text is required")
                return
            comment_id = make_id("OC")
            receipt_id = make_id("RCP")
            comment = {
                "comment_id": comment_id, "created_at": now_iso(),
                "status": "COMMENT_CAPTURED", "original_text": original_text,
                "comment_type": body.get("comment_type", "OBSERVATION"),
                "linked_zone": body.get("linked_zone", "TASK_INTAKE"),
                "linked_tasks": body.get("linked_tasks", []),
                "receipts": [receipt_id], "seed_demo": False
            }
            cd = load_json(COMMENTS_FILE) or {"schema_ref": "comment_v0.6", "runtime_mode": "PROTOTYPE_INTERACTIVE", "no_llm": True, "comments": []}
            cd["comments"].append(comment)
            save_json(COMMENTS_FILE, cd)
            write_receipt(receipt_id, "COMMENT_CREATED", "COMMENT_CAPTURED", "COMMENT", comment_id, [safe_relative(COMMENTS_FILE)])
            self.send_api_json("/api/comments", started, comment, 201)
        elif path == "/api/links":
            source_id = body.get("source_id", "").strip()
            target_id = body.get("target_id", "").strip()
            if not source_id or not target_id:
                self.send_api_error("/api/links", started, "source_id and target_id are required")
                return
            link_id = make_id("ML")
            receipt_id = make_id("RCP")
            link = {
                "link_id": link_id, "created_at": now_iso(), "status": "LINK_CREATED",
                "source_type": body.get("source_type", "TASK"), "source_id": source_id,
                "target_type": body.get("target_type", "COMMENT"), "target_id": target_id,
                "link_reason": body.get("link_reason"), "receipt_id": receipt_id, "seed_demo": False
            }
            ld = load_json(LINKS_FILE) or {"schema_ref": "memory_link_v0.6", "runtime_mode": "PROTOTYPE_INTERACTIVE", "no_llm": True, "links": []}
            ld["links"].append(link)
            save_json(LINKS_FILE, ld)
            write_receipt(receipt_id, "LINK_CREATED", "LINK_CREATED", "LINK", link_id, [safe_relative(LINKS_FILE)])
            self.send_api_json("/api/links", started, link, 201)
        elif path == "/api/export":
            result, err = api_export()
            if err:
                self.send_api_error("/api/export", started, err)
            else:
                self.send_api_json("/api/export", started, result, 201)
        elif path == "/api/rebuild_snapshot":
            result, err = api_rebuild_snapshot()
            if err:
                self.send_api_error("/api/rebuild_snapshot", started, err)
            else:
                self.send_api_json("/api/rebuild_snapshot", started, result, 200)
        else:
            self.send_api_error(path, started, "Not found", 404)


def main():
    print("=" * 60)
    print("Second Brain Neural Map V0.6 — Server")
    print("=" * 60)
    print(f"Mode:        PROTOTYPE_INTERACTIVE")
    print(f"Port:        {PORT}")
    print(f"UI:          http://localhost:{PORT}/")
    print(f"Snapshot:    http://localhost:{PORT}/api/snapshot")
    print(f"Status:      http://localhost:{PORT}/api/status")
    print(f"Packages:    http://localhost:{PORT}/api/task_packages")
    print()
    print("V0.6 NEW: POST /api/tasks/register | POST /api/tasks/launch")
    print("NOT PRODUCTION READY | RULE_BASED_ONLY | NO_LOCAL_LLM | NO_AGENT_API")
    print("=" * 60)

    server = HTTPServer(("localhost", PORT), NeuralMapHandler)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nServer stopped.")
        server.server_close()


if __name__ == "__main__":
    main()
