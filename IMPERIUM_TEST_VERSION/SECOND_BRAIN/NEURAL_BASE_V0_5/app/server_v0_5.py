"""
Second Brain Neural Map V0.5 — HTTP Server
Runtime mode: PROTOTYPE_INTERACTIVE | RULE_BASED_ONLY | NO_LOCAL_LLM | NO_AGENT_API

Serves the Neural Map UI and provides REST API:
  GET  /                        → Neural Map UI
  GET  /api/snapshot            → Live snapshot (all 12 zones)
  GET  /api/status              → Runtime status
  GET  /api/tasks               → Task list (from V0.3 runtime)
  GET  /api/comments            → Comment list
  GET  /api/links               → Link list
  GET  /api/receipts            → Receipts status (read-only)
  GET  /api/export/status       → Export status (read-only)
  POST /api/tasks               → Create task
  POST /api/comments            → Create comment
  POST /api/links               → Create link
  GET  /api/thread/<task_id>    → Memory thread
  POST /api/export              → Export runtime pack
  POST /api/rebuild_snapshot    → Rebuild snapshot (runs snapshot_builder)

Port: 8766 (V0.5 uses different port from V0.3 to allow both running)
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
APP_DIR         = os.path.dirname(os.path.abspath(__file__))
V05_ROOT        = os.path.dirname(APP_DIR)
SECOND_BRAIN    = os.path.dirname(V05_ROOT)
TEST_VERSION    = os.path.dirname(SECOND_BRAIN)
REPO_ROOT       = os.path.dirname(TEST_VERSION)

REGISTRY_DIR    = os.path.join(V05_ROOT, "registry")
REPORTS_DIR     = os.path.join(V05_ROOT, "reports")
TOOLS_DIR       = os.path.join(V05_ROOT, "tools")
TRUTH_LOCK_DIR  = os.path.join(V05_ROOT, "TRUTH_LOCK_V0_1")

SNAPSHOT_FILE   = os.path.join(REPORTS_DIR, "neural_snapshot_live.json")
SNAPSHOT_BUILDER= os.path.join(TOOLS_DIR, "snapshot_builder_v0_5.py")
STALENESS_POLICY_FILE = os.path.join(TRUTH_LOCK_DIR, "contracts", "staleness_policy_v0_2.json")

# V0.3 runtime files (reuse existing backend)
TASKS_FILE      = os.path.join(SECOND_BRAIN, "MEMORY_ZONES", "TASK_INTAKE", "accepted_tasks.json")
COMMENTS_FILE   = os.path.join(SECOND_BRAIN, "MEMORY_ZONES", "OWNER_COMMENTS", "owner_comments_runtime.json")
LINKS_FILE      = os.path.join(SECOND_BRAIN, "MEMORY_ZONES", "MEMORY_LINKS", "task_comment_links.json")
RECEIPTS_DIR    = os.path.join(SECOND_BRAIN, "RUNTIME", "receipts")
EXPORTS_DIR     = os.path.join(SECOND_BRAIN, "RUNTIME", "exports")

PORT = 8766
DEFAULT_STALENESS_POLICY = {
    "max_snapshot_age_seconds": 900,
    "stale_warning_threshold_seconds": 300,
    "stale_failure_threshold_seconds": 900,
}

RUNTIME_STATUS = {
    "version": "V0.5",
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


# ── API handlers ───────────────────────────────────────────────────────────────

def api_snapshot():
    snap = load_json(SNAPSHOT_FILE)
    if snap:
        freshness = compute_snapshot_freshness(snap)
        snap["snapshot_age_seconds"] = freshness["snapshot_age_seconds"]
        snap["snapshot_freshness_state"] = freshness["snapshot_freshness_state"]
        if "truth_lock_run_id" not in snap:
            snap["truth_lock_run_id"] = snap.get("snapshot_id", "UNKNOWN")
        return snap
    return {"error": "Snapshot not found. Run snapshot_builder_v0_5.py first.", "status": "MISSING"}


def api_status():
    snap = load_json(SNAPSHOT_FILE)
    counts = {"tasks": 0, "comments": 0, "links": 0, "receipts": 0}
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


def api_create_task(body):
    source_text = body.get("source_text", "").strip()
    if not source_text:
        return None, "source_text is required"
    task_id = make_id("TI")
    receipt_id = make_id("RCP")
    task = {
        "task_id": task_id,
        "created_at": now_iso(),
        "status": "TASK_ACCEPTED",
        "source_text": source_text,
        "owner_goal": body.get("owner_goal"),
        "priority": body.get("priority", "MEDIUM"),
        "tags": body.get("tags", []),
        "relevant_memory_zones": ["TASK_INTAKE"],
        "created_by": "OWNER_INTERACTIVE",
        "runtime_mode": "PROTOTYPE_INTERACTIVE",
        "receipts": [receipt_id],
        "links": [],
        "next_expected_action": "OWNER_REVIEW",
        "seed_demo": False
    }
    d = load_json(TASKS_FILE) or {"schema_ref": "task_intake_v0.5", "runtime_mode": "PROTOTYPE_INTERACTIVE", "no_llm": True, "tasks": []}
    d["tasks"].append(task)
    save_json(TASKS_FILE, d)
    write_receipt(receipt_id, "TASK_CREATED", "TASK_ACCEPTED", "TASK", task_id, ["SECOND_BRAIN/MEMORY_ZONES/TASK_INTAKE/accepted_tasks.json"])
    return task, None


def api_get_comments():
    d = load_json(COMMENTS_FILE) or {"comments": []}
    return d.get("comments", [])


def api_create_comment(body):
    original_text = body.get("original_text", "").strip()
    if not original_text:
        return None, "original_text is required"
    comment_id = make_id("OC")
    receipt_id = make_id("RCP")
    comment = {
        "comment_id": comment_id,
        "created_at": now_iso(),
        "status": "COMMENT_CAPTURED",
        "original_text": original_text,
        "interpreted_meaning": body.get("interpreted_meaning"),
        "comment_type": body.get("comment_type", "OBSERVATION"),
        "linked_zone": body.get("linked_zone", "TASK_INTAKE"),
        "action_required": body.get("action_required"),
        "needs_owner_confirmation": body.get("needs_owner_confirmation", False),
        "linked_tasks": body.get("linked_tasks", []),
        "receipts": [receipt_id],
        "seed_demo": False
    }
    d = load_json(COMMENTS_FILE) or {"schema_ref": "comment_v0.5", "runtime_mode": "PROTOTYPE_INTERACTIVE", "no_llm": True, "comments": []}
    d["comments"].append(comment)
    save_json(COMMENTS_FILE, d)
    write_receipt(receipt_id, "COMMENT_CREATED", "COMMENT_CAPTURED", "COMMENT", comment_id, ["SECOND_BRAIN/MEMORY_ZONES/OWNER_COMMENTS/owner_comments_runtime.json"])
    return comment, None


def api_get_links():
    d = load_json(LINKS_FILE) or {"links": []}
    return d.get("links", [])


def api_create_link(body):
    source_id = body.get("source_id", "").strip()
    target_id = body.get("target_id", "").strip()
    if not source_id or not target_id:
        return None, "source_id and target_id are required"
    link_id = make_id("ML")
    receipt_id = make_id("RCP")
    link = {
        "link_id": link_id,
        "created_at": now_iso(),
        "status": "LINK_CREATED",
        "source_type": body.get("source_type", "TASK"),
        "source_id": source_id,
        "target_type": body.get("target_type", "COMMENT"),
        "target_id": target_id,
        "link_reason": body.get("link_reason"),
        "expected_use": body.get("expected_use", "Memory thread reconstruction"),
        "verification_status": "UNVERIFIED",
        "receipt_id": receipt_id,
        "seed_demo": False
    }
    d = load_json(LINKS_FILE) or {"schema_ref": "memory_link_v0.5", "runtime_mode": "PROTOTYPE_INTERACTIVE", "no_llm": True, "links": []}
    d["links"].append(link)
    save_json(LINKS_FILE, d)
    # Update comment status
    cd = load_json(COMMENTS_FILE) or {"comments": []}
    for c in cd.get("comments", []):
        if c["comment_id"] == target_id:
            c["status"] = "LINKED"
            if source_id not in c.get("linked_tasks", []):
                c.setdefault("linked_tasks", []).append(source_id)
    save_json(COMMENTS_FILE, cd)
    # Update task links
    td = load_json(TASKS_FILE) or {"tasks": []}
    for t in td.get("tasks", []):
        if t["task_id"] == source_id:
            if link_id not in t.get("links", []):
                t.setdefault("links", []).append(link_id)
    save_json(TASKS_FILE, td)
    write_receipt(receipt_id, "LINK_CREATED", "LINK_CREATED", "LINK", link_id, ["SECOND_BRAIN/MEMORY_ZONES/MEMORY_LINKS/task_comment_links.json"])
    return link, None


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
    return {"task": task, "links": task_links, "comments": linked_comments, "receipts": receipts, "thread_status": "PROTOTYPE_INTERACTIVE"}, None


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
                "no_external_agent_used": payload.get("no_external_agent_used"),
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
        "status": "MISSING",
        "read_only": True,
        "exports_dir": safe_relative(EXPORTS_DIR),
        "export_dir_exists": os.path.isdir(EXPORTS_DIR),
        "export_count": 0,
        "latest_export_id": None,
        "latest_export_path": None,
        "latest_manifest_parse_status": "NOT_FOUND",
        "latest_exports": [],
        "no_mutation_performed": True,
    }
    if not os.path.isdir(EXPORTS_DIR):
        return response

    export_dirs = [d for d in os.listdir(EXPORTS_DIR) if os.path.isdir(os.path.join(EXPORTS_DIR, d))]
    export_dirs.sort(key=lambda d: os.path.getmtime(os.path.join(EXPORTS_DIR, d)), reverse=True)
    response["export_count"] = len(export_dirs)
    response["status"] = "PASS"

    if export_dirs:
        latest = export_dirs[0]
        latest_path = os.path.join(EXPORTS_DIR, latest)
        response["latest_export_path"] = safe_relative(latest_path)
        manifest_path = os.path.join(latest_path, "manifest.json")
        manifest = load_json(manifest_path)
        if isinstance(manifest, dict):
            response["latest_manifest_parse_status"] = "JSON_OK"
            response["latest_export_id"] = manifest.get("export_id", latest)
        elif os.path.isfile(manifest_path):
            response["latest_manifest_parse_status"] = "JSON_ERROR"
            response["latest_export_id"] = latest
        else:
            response["latest_manifest_parse_status"] = "NOT_FOUND"
            response["latest_export_id"] = latest

    rows = []
    for name in export_dirs[:limit]:
        item_path = os.path.join(EXPORTS_DIR, name)
        manifest_path = os.path.join(item_path, "manifest.json")
        manifest = load_json(manifest_path)
        rows.append({
            "export_dir": name,
            "path": safe_relative(item_path),
            "manifest_status": "JSON_OK" if isinstance(manifest, dict) else ("JSON_ERROR" if os.path.isfile(manifest_path) else "NOT_FOUND"),
            "export_id": manifest.get("export_id") if isinstance(manifest, dict) else None,
            "created_at": manifest.get("created_at") if isinstance(manifest, dict) else None,
        })
    response["latest_exports"] = rows
    return response


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
    manifest = {"export_id": f"EXP-{stamp}", "created_at": now_iso(), "exported_files": exported, "runtime_mode": "PROTOTYPE_INTERACTIVE", "no_llm": True}
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
            self.send_file(os.path.join(APP_DIR, "neural_map_v0_5.html"), "text/html; charset=utf-8")
        elif path == "/neural_map_v0_5.css":
            self.send_file(os.path.join(APP_DIR, "neural_map_v0_5.css"), "text/css; charset=utf-8")
        elif path == "/neural_map_v0_5.js":
            self.send_file(os.path.join(APP_DIR, "neural_map_v0_5.js"), "application/javascript; charset=utf-8")
        elif path == "/api/snapshot":
            self.send_api_json("/api/snapshot", started, api_snapshot())
        elif path == "/api/status":
            self.send_api_json("/api/status", started, api_status())
        elif path == "/api/tasks":
            self.send_api_json("/api/tasks", started, api_get_tasks())
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

        if path == "/api/tasks":
            result, err = api_create_task(body)
            if err:
                self.send_api_error("/api/tasks", started, err)
            else:
                self.send_api_json("/api/tasks", started, result, 201)
        elif path == "/api/comments":
            result, err = api_create_comment(body)
            if err:
                self.send_api_error("/api/comments", started, err)
            else:
                self.send_api_json("/api/comments", started, result, 201)
        elif path == "/api/links":
            result, err = api_create_link(body)
            if err:
                self.send_api_error("/api/links", started, err)
            else:
                self.send_api_json("/api/links", started, result, 201)
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
    print("Second Brain Neural Map V0.5 — Server")
    print("=" * 60)
    print(f"Mode:        PROTOTYPE_INTERACTIVE")
    print(f"Port:        {PORT}")
    print(f"UI:          http://localhost:{PORT}/")
    print(f"Snapshot:    http://localhost:{PORT}/api/snapshot")
    print(f"Status:      http://localhost:{PORT}/api/status")
    print()
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
