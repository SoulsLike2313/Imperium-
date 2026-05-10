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

ROOT = Path(os.environ.get("IMPERIUM_ROOT", r"E:\IMPERIUM"))
HOST = os.environ.get("ADMINISTRATUM_HOST", "127.0.0.1")
PORT = int(os.environ.get("ADMINISTRATUM_PORT", "8792"))

BUILDER = ROOT / "ORGANS" / "ADMINISTRATUM" / "SCRIPTS" / "administratum_build_resume_continuity_pack_v0_2.py"
HERE = Path(__file__).resolve().parent

DASHBOARD_ID = "ADMINISTRATUM_WEB_DASHBOARD_V0_3"
DASHBOARD_VERSION = "0.3"


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


class Handler(BaseHTTPRequestHandler):
    server_version = "AdministratumResumeDashboardV03/0.3"

    def send_json(self, payload: dict, status: int = 200) -> None:
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
            return self.send_json({
                "ok": True,
                "dashboard_id": DASHBOARD_ID,
                "version": DASHBOARD_VERSION,
                "purpose_ru": "Р СѓС‡РЅР°СЏ СЃР±РѕСЂРєР° С‚РѕС‡РЅРѕРіРѕ Resume Continuity Pack РґР»СЏ РїСЂРѕРґРѕР»Р¶РµРЅРёСЏ СЃ РїРѕСЃР»РµРґРЅРµР№ СЂР°Р±РѕС‡РµР№ С‚РѕС‡РєРё.",
                "root": str(ROOT),
                "builder": str(BUILDER),
                "builder_exists": BUILDER.exists(),
                "ui_language": "ru",
                "animation": "enabled",
                "button": "РЎРѕР±СЂР°С‚СЊ Continuity Pack",
                "forbidden_claims": ["green", "canon", "real-task-ready"],
                "server_time_utc": utc_now(),
            })

        return self.send_json({"ok": False, "error": "NOT_FOUND", "route": route}, 404)

    def do_POST(self) -> None:
        route = urlparse(self.path).path

        if route != "/api/build-resume-continuity-pack":
            return self.send_json({"ok": False, "error": "NOT_FOUND", "route": route}, 404)

        if not BUILDER.exists():
            return self.send_json({
                "ok": False,
                "error": "MISSING_BUILDER",
                "builder": str(BUILDER),
            }, 500)

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
            return self.send_json({
                "ok": False,
                "error": str(exc),
                "traceback": traceback.format_exc(),
            }, 500)


def main() -> None:
    httpd = ThreadingHTTPServer((HOST, PORT), Handler)
    print(f"Administratum Dashboard v0.3 running at http://{HOST}:{PORT}")
    print("Button: РЎРѕР±СЂР°С‚СЊ Continuity Pack")
    print(f"Builder: {BUILDER}")
    httpd.serve_forever()


if __name__ == "__main__":
    main()