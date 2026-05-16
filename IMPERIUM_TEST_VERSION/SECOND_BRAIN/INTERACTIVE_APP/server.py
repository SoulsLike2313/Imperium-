"""
Second Brain V0.3 — Interactive HTTP Server
Runtime mode: PROTOTYPE_INTERACTIVE | RULE_BASED_ONLY | NO_LOCAL_LLM | NO_AGENT_API

Serves the UI and provides REST API for:
  - Task intake
  - Owner comment capture
  - Memory link creation
  - Memory thread view
  - Runtime export

Port: 8765
"""

import json
import os
import sys
import datetime
import uuid
import shutil
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs

# ── Paths ──────────────────────────────────────────────────────────────────────
SERVER_DIR = os.path.dirname(os.path.abspath(__file__))
SECOND_BRAIN_ROOT = os.path.dirname(SERVER_DIR)
UI_DIR = os.path.join(SECOND_BRAIN_ROOT, "UI")
RUNTIME_DIR = os.path.join(SECOND_BRAIN_ROOT, "RUNTIME")
RECEIPTS_DIR = os.path.join(RUNTIME_DIR, "receipts")
EXPORTS_DIR = os.path.join(RUNTIME_DIR, "exports")

TASKS_FILE = os.path.join(SECOND_BRAIN_ROOT, "MEMORY_ZONES", "TASK_INTAKE", "accepted_tasks.json")
COMMENTS_FILE = os.path.join(SECOND_BRAIN_ROOT, "MEMORY_ZONES", "OWNER_COMMENTS", "owner_comments_runtime.json")
LINKS_FILE = os.path.join(SECOND_BRAIN_ROOT, "MEMORY_ZONES", "MEMORY_LINKS", "task_comment_links.json")

PORT = 8765

RUNTIME_STATUS = {
    "version": "V0.3",
    "mode": "PROTOTYPE_INTERACTIVE",
    "rule_based": True,
    "no_local_llm": True,
    "no_agent_api": True,
    "not_production_ready": True,
    "server": f"localhost:{PORT}",
    "honest_status": [
        "PROTOTYPE_INTERACTIVE",
        "RULE_BASED_ONLY",
        "NO_LOCAL_LLM",
        "NO_AGENT_API",
        "NOT_CONFIGURED"
    ]
}

# ── Helpers ────────────────────────────────────────────────────────────────────

def now_iso():
    return datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")

def now_stamp():
    return datetime.datetime.utcnow().strftime("%Y%m%d-%H%M%S")

def make_task_id():
    ts = datetime.datetime.utcnow().strftime("%Y%m%d-%H%M%S")
    suffix = str(uuid.uuid4().int)[:3].zfill(3)
    return f"TI-{ts}-{suffix}"

def make_comment_id():
    ts = datetime.datetime.utcnow().strftime("%Y%m%d-%H%M%S")
    suffix = str(uuid.uuid4().int)[:3].zfill(3)
    return f"OC-{ts}-{suffix}"

def make_link_id():
    ts = datetime.datetime.utcnow().strftime("%Y%m%d-%H%M%S")
    suffix = str(uuid.uuid4().int)[:3].zfill(3)
    return f"ML-{ts}-{suffix}"

def make_receipt_id():
    ts = datetime.datetime.utcnow().strftime("%Y%m%d-%H%M%S")
    suffix = str(uuid.uuid4().int)[:3].zfill(3)
    return f"RCP-{ts}-{suffix}"

def load_json(path):
    if not os.path.isfile(path):
        return None
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def save_json(path, data):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

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
    receipt_path = os.path.join(RECEIPTS_DIR, f"{receipt_id}.json")
    os.makedirs(RECEIPTS_DIR, exist_ok=True)
    save_json(receipt_path, receipt)
    return receipt

# ── API Handlers ───────────────────────────────────────────────────────────────

def api_status():
    data = load_json(TASKS_FILE) or {"tasks": []}
    tasks = data.get("tasks", [])
    cdata = load_json(COMMENTS_FILE) or {"comments": []}
    comments = cdata.get("comments", [])
    ldata = load_json(LINKS_FILE) or {"links": []}
    links = ldata.get("links", [])
    receipts = []
    if os.path.isdir(RECEIPTS_DIR):
        receipts = [f for f in os.listdir(RECEIPTS_DIR) if f.endswith(".json")]
    return {
        **RUNTIME_STATUS,
        "counts": {
            "tasks": len(tasks),
            "comments": len(comments),
            "links": len(links),
            "receipts": len(receipts)
        }
    }

def api_get_tasks():
    data = load_json(TASKS_FILE) or {"tasks": []}
    return data.get("tasks", [])

def api_create_task(body):
    source_text = body.get("source_text", "").strip()
    if not source_text:
        return None, "source_text is required"

    task_id = make_task_id()
    receipt_id = make_receipt_id()

    task = {
        "task_id": task_id,
        "created_at": now_iso(),
        "status": "TASK_ACCEPTED",
        "source_text": source_text,
        "owner_goal": body.get("owner_goal", None),
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

    data = load_json(TASKS_FILE) or {
        "schema_ref": "task_intake_runtime_v0.3",
        "runtime_mode": "PROTOTYPE_INTERACTIVE",
        "no_llm": True,
        "no_agent_api": True,
        "tasks": []
    }
    data["tasks"].append(task)
    save_json(TASKS_FILE, data)

    write_receipt(
        receipt_id, "TASK_CREATED", "TASK_ACCEPTED",
        "TASK", task_id,
        [f"SECOND_BRAIN/MEMORY_ZONES/TASK_INTAKE/accepted_tasks.json"]
    )

    return task, None

def api_get_comments():
    data = load_json(COMMENTS_FILE) or {"comments": []}
    return data.get("comments", [])

def api_create_comment(body):
    original_text = body.get("original_text", "").strip()
    if not original_text:
        return None, "original_text is required"

    comment_id = make_comment_id()
    receipt_id = make_receipt_id()

    comment = {
        "comment_id": comment_id,
        "created_at": now_iso(),
        "status": "COMMENT_CAPTURED",
        "original_text": original_text,
        "interpreted_meaning": body.get("interpreted_meaning", None),
        "comment_type": body.get("comment_type", "OBSERVATION"),
        "linked_zone": body.get("linked_zone", "TASK_INTAKE"),
        "action_required": body.get("action_required", None),
        "needs_owner_confirmation": body.get("needs_owner_confirmation", False),
        "linked_tasks": body.get("linked_tasks", []),
        "receipts": [receipt_id],
        "seed_demo": False
    }

    data = load_json(COMMENTS_FILE) or {
        "schema_ref": "comment_runtime_v0.3",
        "runtime_mode": "PROTOTYPE_INTERACTIVE",
        "no_llm": True,
        "no_agent_api": True,
        "comments": []
    }
    data["comments"].append(comment)
    save_json(COMMENTS_FILE, data)

    write_receipt(
        receipt_id, "COMMENT_CREATED", "COMMENT_CAPTURED",
        "COMMENT", comment_id,
        [f"SECOND_BRAIN/MEMORY_ZONES/OWNER_COMMENTS/owner_comments_runtime.json"]
    )

    return comment, None

def api_get_links():
    data = load_json(LINKS_FILE) or {"links": []}
    return data.get("links", [])

def api_create_link(body):
    source_id = body.get("source_id", "").strip()
    target_id = body.get("target_id", "").strip()
    if not source_id or not target_id:
        return None, "source_id and target_id are required"

    link_id = make_link_id()
    receipt_id = make_receipt_id()

    link = {
        "link_id": link_id,
        "created_at": now_iso(),
        "status": "LINK_CREATED",
        "source_type": body.get("source_type", "TASK"),
        "source_id": source_id,
        "target_type": body.get("target_type", "COMMENT"),
        "target_id": target_id,
        "link_reason": body.get("link_reason", None),
        "expected_use": body.get("expected_use", "Memory thread reconstruction"),
        "verification_status": "UNVERIFIED",
        "receipt_id": receipt_id,
        "seed_demo": False
    }

    data = load_json(LINKS_FILE) or {
        "schema_ref": "memory_link_runtime_v0.3",
        "runtime_mode": "PROTOTYPE_INTERACTIVE",
        "no_llm": True,
        "no_agent_api": True,
        "links": []
    }
    data["links"].append(link)
    save_json(LINKS_FILE, data)

    # Update comment status to LINKED if target is a comment
    if link["target_type"] == "COMMENT":
        cdata = load_json(COMMENTS_FILE) or {"comments": []}
        for c in cdata.get("comments", []):
            if c["comment_id"] == target_id:
                c["status"] = "LINKED"
                if source_id not in c.get("linked_tasks", []):
                    c.setdefault("linked_tasks", []).append(source_id)
        save_json(COMMENTS_FILE, cdata)

    # Update task links list
    if link["source_type"] == "TASK":
        tdata = load_json(TASKS_FILE) or {"tasks": []}
        for t in tdata.get("tasks", []):
            if t["task_id"] == source_id:
                if link_id not in t.get("links", []):
                    t.setdefault("links", []).append(link_id)
        save_json(TASKS_FILE, tdata)

    write_receipt(
        receipt_id, "LINK_CREATED", "LINK_CREATED",
        "LINK", link_id,
        [f"SECOND_BRAIN/MEMORY_ZONES/MEMORY_LINKS/task_comment_links.json"]
    )

    return link, None

def api_get_thread(task_id):
    tasks = api_get_tasks()
    task = next((t for t in tasks if t["task_id"] == task_id), None)
    if not task:
        return None, f"Task {task_id} not found"

    links = api_get_links()
    comments = api_get_comments()

    task_links = [l for l in links if l["source_id"] == task_id or l["target_id"] == task_id]
    linked_comment_ids = set()
    for l in task_links:
        if l["source_type"] == "COMMENT":
            linked_comment_ids.add(l["source_id"])
        if l["target_type"] == "COMMENT":
            linked_comment_ids.add(l["target_id"])

    linked_comments = [c for c in comments if c["comment_id"] in linked_comment_ids]

    receipts = []
    if os.path.isdir(RECEIPTS_DIR):
        for rfile in os.listdir(RECEIPTS_DIR):
            if rfile.endswith(".json"):
                r = load_json(os.path.join(RECEIPTS_DIR, rfile))
                if r and r.get("object_id") in ([task_id] + list(linked_comment_ids)):
                    receipts.append(r)

    return {
        "task": task,
        "links": task_links,
        "comments": linked_comments,
        "receipts": receipts,
        "thread_status": "PROTOTYPE_INTERACTIVE",
        "no_llm": True,
        "no_agent_api": True
    }, None

def api_export():
    stamp = now_stamp()
    export_dir = os.path.join(EXPORTS_DIR, f"export_{stamp}")
    os.makedirs(export_dir, exist_ok=True)

    files_to_export = [TASKS_FILE, COMMENTS_FILE, LINKS_FILE]
    exported = []
    for src in files_to_export:
        if os.path.isfile(src):
            dst = os.path.join(export_dir, os.path.basename(src))
            shutil.copy2(src, dst)
            exported.append(os.path.basename(src))

    # Copy receipts
    receipts_export = os.path.join(export_dir, "receipts")
    if os.path.isdir(RECEIPTS_DIR):
        shutil.copytree(RECEIPTS_DIR, receipts_export)
        exported.append("receipts/")

    manifest = {
        "export_id": f"EXP-{stamp}",
        "created_at": now_iso(),
        "exported_files": exported,
        "export_path": export_dir,
        "runtime_mode": "PROTOTYPE_INTERACTIVE",
        "no_llm": True,
        "no_agent_api": True
    }
    save_json(os.path.join(export_dir, "manifest.json"), manifest)

    return manifest, None

# ── HTTP Handler ───────────────────────────────────────────────────────────────

class SecondBrainHandler(BaseHTTPRequestHandler):

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
        parsed = urlparse(self.path)
        path = parsed.path.rstrip("/") or "/"

        if path == "/" or path == "/index.html":
            self.send_file(os.path.join(UI_DIR, "second_brain_interactive.html"), "text/html; charset=utf-8")
        elif path == "/second_brain_interactive.css":
            self.send_file(os.path.join(UI_DIR, "second_brain_interactive.css"), "text/css; charset=utf-8")
        elif path == "/second_brain_interactive.js":
            self.send_file(os.path.join(UI_DIR, "second_brain_interactive.js"), "application/javascript; charset=utf-8")
        elif path == "/api/status":
            self.send_json(api_status())
        elif path == "/api/tasks":
            self.send_json(api_get_tasks())
        elif path == "/api/comments":
            self.send_json(api_get_comments())
        elif path == "/api/links":
            self.send_json(api_get_links())
        elif path.startswith("/api/thread/"):
            task_id = path[len("/api/thread/"):]
            result, err = api_get_thread(task_id)
            if err:
                self.send_error_json(err, 404)
            else:
                self.send_json(result)
        else:
            self.send_error_json("Not found", 404)

    def do_POST(self):
        parsed = urlparse(self.path)
        path = parsed.path.rstrip("/")
        body = self.read_body()

        if path == "/api/tasks":
            result, err = api_create_task(body)
            if err:
                self.send_error_json(err)
            else:
                self.send_json(result, 201)
        elif path == "/api/comments":
            result, err = api_create_comment(body)
            if err:
                self.send_error_json(err)
            else:
                self.send_json(result, 201)
        elif path == "/api/links":
            result, err = api_create_link(body)
            if err:
                self.send_error_json(err)
            else:
                self.send_json(result, 201)
        elif path == "/api/export":
            result, err = api_export()
            if err:
                self.send_error_json(err)
            else:
                self.send_json(result, 201)
        else:
            self.send_error_json("Not found", 404)


# ── Entry Point ────────────────────────────────────────────────────────────────

def main():
    print("=" * 60)
    print("Second Brain V0.3 — Interactive Server")
    print("=" * 60)
    print(f"Mode:        PROTOTYPE_INTERACTIVE")
    print(f"Rule-based:  YES (no LLM, no agent API)")
    print(f"Port:        {PORT}")
    print(f"UI:          http://localhost:{PORT}/")
    print(f"Status API:  http://localhost:{PORT}/api/status")
    print()
    print("NOT PRODUCTION READY — PROTOTYPE ONLY")
    print("NO_LOCAL_LLM | NO_AGENT_API | RULE_BASED_ONLY")
    print("=" * 60)

    server = HTTPServer(("localhost", PORT), SecondBrainHandler)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nServer stopped.")
        server.server_close()


if __name__ == "__main__":
    main()
