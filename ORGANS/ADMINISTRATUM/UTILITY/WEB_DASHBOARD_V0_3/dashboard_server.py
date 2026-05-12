from __future__ import annotations

import json
import os
import subprocess
import sys
import traceback
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse
from typing import Any

ROUTE_TRUTH_RELATIVE = Path("ORGANS") / "ADMINISTRATUM" / "CONFIG" / "ADMINISTRATUM_ROUTE_TRUTH_V0_1.json"


DEFAULT_ROUTE_TRUTH: dict[str, Any] = {
    "schema_version": "ADMINISTRATUM_ROUTE_TRUTH_V0_1",
    "repository": {
        "remote_url": "https://github.com/SoulsLike2313/Imperium-",
        "tree_url_template": "https://github.com/SoulsLike2313/Imperium-/tree/{head_sha}",
    },
    "paths": {
        "pc_repo_root": "E:\\IMPERIUM",
        "vm2_repo_root": "/home/vboxuser2/IMPERIUM_WORK/Imperium-",
    },
    "vm2_ssh": {
        "user_host": "vboxuser2@127.0.0.1",
        "port": 2223,
        "key_path_powershell": "$env:USERPROFILE\\.ssh\\imperium_pc_to_vm2_ed25519_20260418",
    },
}


def detect_repo_root() -> Path:
    env_root = os.environ.get("IMPERIUM_ROOT")
    if env_root:
        return Path(env_root).expanduser()

    here = Path(__file__).resolve()
    if len(here.parents) >= 5:
        return here.parents[4]

    return Path.cwd()


ROOT = detect_repo_root()
HOST = os.environ.get("ADMINISTRATUM_HOST", "127.0.0.1")
PORT = int(os.environ.get("ADMINISTRATUM_PORT", "8792"))

BUILDER = ROOT / "ORGANS" / "ADMINISTRATUM" / "SCRIPTS" / "administratum_build_resume_continuity_pack_v0_2.py"
HERE = Path(__file__).resolve().parent
ROUTE_TRUTH_PATH = ROOT / ROUTE_TRUTH_RELATIVE

DASHBOARD_ID = "ADMINISTRATUM_WEB_DASHBOARD_V0_3"
DASHBOARD_VERSION = "0.3"


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def read_json(path: Path) -> dict[str, Any] | None:
    try:
        if not path.exists():
            return None
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return None


def merge_dict(base: dict[str, Any], overlay: dict[str, Any]) -> dict[str, Any]:
    merged = dict(base)
    for key, value in overlay.items():
        if isinstance(value, dict) and isinstance(merged.get(key), dict):
            merged[key] = merge_dict(merged[key], value)
        else:
            merged[key] = value
    return merged


def load_route_truth() -> dict[str, Any]:
    payload = read_json(ROUTE_TRUTH_PATH)
    truth = dict(DEFAULT_ROUTE_TRUTH)
    if isinstance(payload, dict):
        truth = merge_dict(truth, payload)
    truth["source_path"] = str(ROUTE_TRUTH_PATH)
    truth["source_exists"] = ROUTE_TRUTH_PATH.exists()
    return truth


def run_git(args: list[str]) -> tuple[bool, str]:
    proc = subprocess.run(
        ["git", *args],
        cwd=str(ROOT),
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        check=False,
    )
    output = (proc.stdout or proc.stderr or "").strip()
    return proc.returncode == 0, output


def first_line(text: str) -> str:
    for line in text.splitlines():
        value = line.strip()
        if value:
            return value
    return ""


def collect_git_truth(route_truth: dict[str, Any]) -> dict[str, Any]:
    ok_head, head_raw = run_git(["rev-parse", "HEAD"])
    ok_count, count_raw = run_git(["rev-list", "--count", "HEAD"])
    ok_latest, latest_raw = run_git(["log", "-1", "--oneline"])

    head_sha = first_line(head_raw) if ok_head else ""
    count_text = first_line(count_raw) if ok_count else ""
    latest_commit = first_line(latest_raw) if ok_latest else ""

    commit_count: int | None = int(count_text) if count_text.isdigit() else None

    repo_cfg = route_truth.get("repository") if isinstance(route_truth.get("repository"), dict) else {}
    remote_url = str(repo_cfg.get("remote_url", DEFAULT_ROUTE_TRUTH["repository"]["remote_url"]))
    tree_template = str(
        repo_cfg.get("tree_url_template", DEFAULT_ROUTE_TRUTH["repository"]["tree_url_template"])
    )
    tree_url = tree_template.format(head_sha=head_sha) if head_sha else ""

    return {
        "head_sha": head_sha,
        "commit_count": commit_count,
        "latest_commit_oneline": latest_commit,
        "tree_url": tree_url,
        "remote_url": remote_url,
    }


class Handler(BaseHTTPRequestHandler):
    server_version = "AdministratumResumeDashboardV03/0.3"

    def send_json(self, payload: dict[str, Any], status: int = 200) -> None:
        raw = json.dumps(payload, ensure_ascii=False, indent=2).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(raw)))
        self.end_headers()
        self.wfile.write(raw)

    def send_file(self, path: Path, content_type: str) -> None:
        if not path.exists():
            self.send_json({"ok": False, "error": "NOT_FOUND", "path": str(path)}, 404)
            return

        raw = path.read_bytes()
        self.send_response(200)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(raw)))
        self.end_headers()
        self.wfile.write(raw)

    def do_GET(self) -> None:
        route = urlparse(self.path).path

        if route in ["/", "/index.html"]:
            return self.send_file(HERE / "index.html", "text/html; charset=utf-8")

        if route == "/app.js":
            return self.send_file(HERE / "app.js", "application/javascript; charset=utf-8")

        if route == "/style.css":
            return self.send_file(HERE / "style.css", "text/css; charset=utf-8")

        if route == "/api/status":
            route_truth = load_route_truth()
            git_truth = collect_git_truth(route_truth)
            return self.send_json(
                {
                    "ok": True,
                    "dashboard_id": DASHBOARD_ID,
                    "version": DASHBOARD_VERSION,
                    "purpose_ru": "Ручная сборка точного Resume Continuity Pack для продолжения с последней рабочей точки.",
                    "root": str(ROOT),
                    "builder": str(BUILDER),
                    "builder_exists": BUILDER.exists(),
                    "ui_language": "ru",
                    "animation": "enabled",
                    "button": "Собрать Continuity Pack",
                    "forbidden_claims": ["green", "canon", "real-task-ready"],
                    "route_truth": route_truth,
                    "git_truth": git_truth,
                    "server_time_utc": utc_now(),
                }
            )

        return self.send_json({"ok": False, "error": "NOT_FOUND", "route": route}, 404)

    def do_POST(self) -> None:
        route = urlparse(self.path).path

        if route != "/api/build-resume-continuity-pack":
            return self.send_json({"ok": False, "error": "NOT_FOUND", "route": route}, 404)

        if not BUILDER.exists():
            return self.send_json({"ok": False, "error": "MISSING_BUILDER", "builder": str(BUILDER)}, 500)

        try:
            proc = subprocess.run(
                [sys.executable, str(BUILDER), "--root", str(ROOT), "--json"],
                cwd=str(ROOT),
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
                check=False,
            )

            payload: dict[str, Any] = {
                "ok": proc.returncode == 0,
                "dashboard_id": DASHBOARD_ID,
                "version": DASHBOARD_VERSION,
                "returncode": proc.returncode,
                "stdout_tail": proc.stdout[-12000:],
                "stderr_tail": proc.stderr[-12000:],
                "finished_at_utc": utc_now(),
            }

            try:
                payload["result"] = json.loads(proc.stdout)
            except Exception:
                payload["result_parse_warning"] = "Builder stdout is not pure JSON; see stdout_tail."

            return self.send_json(payload, 200 if proc.returncode == 0 else 500)

        except Exception as exc:
            return self.send_json(
                {
                    "ok": False,
                    "error": str(exc),
                    "traceback": traceback.format_exc(),
                },
                500,
            )


def main() -> None:
    httpd = ThreadingHTTPServer((HOST, PORT), Handler)
    print(f"Administratum Dashboard v0.3 running at http://{HOST}:{PORT}")
    print("Button: Собрать Continuity Pack")
    print(f"Builder: {BUILDER}")
    httpd.serve_forever()


if __name__ == "__main__":
    main()
