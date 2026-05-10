import json
import os
import subprocess
import sys
import time
import webbrowser
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
from pathlib import Path
from urllib.parse import urlparse, parse_qs

ROOT = Path(r"E:\IMPERIUM")
DOC = ROOT / "ORGANS" / "DOCTRINARIUM"
WEB = DOC / "UTILITY" / "WEB_DASHBOARD"
REPORTS = DOC / "REPORTS"
STATUS = DOC / "STATUS"
DOCTRINE = DOC / "DOCTRINE"
LAWS = DOC / "LAWS"
STANDARDS = DOC / "STANDARDS"
UTILITY = DOC / "UTILITY"
REFRESH = UTILITY / "run_doctrinarium_workbench_refresh.ps1"

PATHS = {
    "root": str(ROOT),
    "doctrinarium": str(DOC),
    "reports": str(REPORTS),
    "status": str(STATUS),
    "doctrine": str(DOCTRINE),
    "laws": str(LAWS),
    "standards": str(STANDARDS),
    "utility": str(UTILITY),
    "web_dashboard": str(WEB),
    "refresh_launcher": str(REFRESH),
}

def read_json(path):
    try:
        if path.exists():
            return json.loads(path.read_text(encoding="utf-8"))
    except Exception as e:
        return {"_error": str(e), "_path": str(path)}
    return None

def api_data():
    return {
        "created_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "status": read_json(STATUS / "DOCTRINARIUM_STATUS.json"),
        "gaps": read_json(REPORTS / "ALL_ORGANS_GAP_REPORT.json"),
        "utility": read_json(REPORTS / "ORGAN_UTILITY_GAP_REPORT.json"),
        "laws": read_json(LAWS / "LAW_INDEX.json"),
        "enforcement": read_json(LAWS / "LAW_ENFORCEMENT_MAP.json"),
        "doctrine": read_json(DOCTRINE / "DOCTRINE_INDEX.json"),
        "paths": PATHS,
    }

class Handler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(WEB), **kwargs)

    def log_message(self, fmt, *args):
        return

    def send_json(self, obj, status=200):
        data = json.dumps(obj, ensure_ascii=False, indent=2).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def do_GET(self):
        parsed = urlparse(self.path)
        if parsed.path == "/api/data":
            self.send_json(api_data())
            return
        return super().do_GET()

    def do_POST(self):
        parsed = urlparse(self.path)

        if parsed.path == "/api/refresh":
            if not REFRESH.exists():
                self.send_json({"ok": False, "error": f"Refresh launcher not found: {REFRESH}"}, 404)
                return

            shell = "pwsh"
            try:
                result = subprocess.run(
                    [shell, "-NoProfile", "-ExecutionPolicy", "Bypass", "-File", str(REFRESH)],
                    capture_output=True,
                    text=True,
                    timeout=240,
                )
            except FileNotFoundError:
                result = subprocess.run(
                    ["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-File", str(REFRESH)],
                    capture_output=True,
                    text=True,
                    timeout=240,
                )
            except Exception as e:
                self.send_json({"ok": False, "error": str(e)}, 500)
                return

            self.send_json({
                "ok": result.returncode == 0,
                "exit_code": result.returncode,
                "stdout": result.stdout[-4000:],
                "stderr": result.stderr[-4000:],
            })
            return

        if parsed.path == "/api/open":
            qs = parse_qs(parsed.query)
            target = (qs.get("target") or [""])[0]
            allow = {
                "reports": REPORTS,
                "status": STATUS,
                "doctrine": DOCTRINE,
                "laws": LAWS,
                "standards": STANDARDS,
                "utility": UTILITY,
                "root": ROOT,
            }
            p = allow.get(target)
            if not p:
                self.send_json({"ok": False, "error": "Unknown target"}, 400)
                return
            if not p.exists():
                self.send_json({"ok": False, "error": f"Path not found: {p}"}, 404)
                return
            try:
                os.startfile(str(p))
                self.send_json({"ok": True, "path": str(p)})
            except Exception as e:
                self.send_json({"ok": False, "error": str(e)}, 500)
            return

        self.send_json({"ok": False, "error": "Not found"}, 404)

def main():
    port = 8787
    server = ThreadingHTTPServer(("127.0.0.1", port), Handler)
    url = f"http://127.0.0.1:{port}"
    print(f"Doctrinarium Dashboard v0.5 running at {url}")
    webbrowser.open(url)
    server.serve_forever()

if __name__ == "__main__":
    main()
