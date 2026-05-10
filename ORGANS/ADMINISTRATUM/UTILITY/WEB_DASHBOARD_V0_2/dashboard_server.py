from __future__ import annotations

import json
import os
import subprocess
import sys
import traceback
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(os.environ.get("IMPERIUM_ROOT", r"E:\IMPERIUM"))
HOST = os.environ.get("ADMINISTRATUM_HOST", "127.0.0.1")
PORT = int(os.environ.get("ADMINISTRATUM_PORT", "8792"))
BUILDER = ROOT / "ORGANS" / "ADMINISTRATUM" / "SCRIPTS" / "administratum_build_resume_continuity_pack_v0_2.py"
HERE = Path(__file__).resolve().parent

class Handler(BaseHTTPRequestHandler):
    server_version = "AdministratumResumeDashboardV02/0.2"

    def send_json(self, payload, status=200):
        raw = json.dumps(payload, ensure_ascii=False, indent=2).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(raw)))
        self.end_headers()
        self.wfile.write(raw)

    def send_file(self, path: Path, content_type: str):
        if not path.exists():
            self.send_json({"ok": False, "error": "NOT_FOUND", "path": str(path)}, 404)
            return
        raw = path.read_bytes()
        self.send_response(200)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(raw)))
        self.end_headers()
        self.wfile.write(raw)

    def do_GET(self):
        p = urlparse(self.path).path
        if p in ["/", "/index.html"]:
            return self.send_file(HERE / "index.html", "text/html; charset=utf-8")
        if p == "/app.js":
            return self.send_file(HERE / "app.js", "application/javascript; charset=utf-8")
        if p == "/style.css":
            return self.send_file(HERE / "style.css", "text/css; charset=utf-8")
        if p == "/api/status":
            return self.send_json({
                "ok": True,
                "dashboard_id": "ADMINISTRATUM_WEB_DASHBOARD_V0_2",
                "version": "0.2",
                "purpose": "Resume-first Continuity Pack, not generic system summary",
                "root": str(ROOT),
                "builder": str(BUILDER),
                "builder_exists": BUILDER.exists(),
                "button": "Build Resume Continuity Pack v0.2",
                "forbidden_claims": ["green", "canon", "real-task-ready"],
            })
        return self.send_json({"ok": False, "error": "NOT_FOUND"}, 404)

    def do_POST(self):
        p = urlparse(self.path).path
        if p != "/api/build-resume-continuity-pack":
            return self.send_json({"ok": False, "error": "NOT_FOUND"}, 404)
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
            payload = {
                "ok": proc.returncode == 0,
                "returncode": proc.returncode,
                "stdout": proc.stdout[-12000:],
                "stderr": proc.stderr[-12000:],
            }
            try:
                payload["result"] = json.loads(proc.stdout)
            except Exception:
                pass
            return self.send_json(payload, 200 if proc.returncode == 0 else 500)
        except Exception as e:
            return self.send_json({"ok": False, "error": str(e), "traceback": traceback.format_exc()}, 500)

def main():
    httpd = ThreadingHTTPServer((HOST, PORT), Handler)
    print(f"Administratum Dashboard v0.2 running at http://{HOST}:{PORT}")
    print("Button: Build Resume Continuity Pack v0.2")
    httpd.serve_forever()

if __name__ == "__main__":
    main()