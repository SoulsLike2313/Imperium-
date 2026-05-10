#!/usr/bin/env python3
import json
import os
import subprocess
import sys
import time
import webbrowser
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
from pathlib import Path
from urllib.parse import parse_qs, urlparse

ROOT = Path(r"E:\IMPERIUM")
ADMIN = ROOT / "ORGANS" / "ADMINISTRATUM"
WEB = ADMIN / "UTILITY" / "WEB_DASHBOARD_V0_1"
SCRIPTS = ADMIN / "SCRIPTS"
CONT_PACKS = ADMIN / "CONTINUITY" / "PACKS"
CONT_COMPS = ADMIN / "CONTINUITY" / "COMPARISONS"
REPORTS = ADMIN / "REPORTS"

BUILD_SCRIPT = SCRIPTS / "administratum_build_continuity_pack.py"
COMPARE_SCRIPT = SCRIPTS / "administratum_compare_continuity_pack.py"

PATHS = {
    "root": str(ROOT),
    "administratum": str(ADMIN),
    "dashboard_root": str(WEB),
    "continuity_packs": str(CONT_PACKS),
    "continuity_comparisons": str(CONT_COMPS),
    "reports": str(REPORTS),
}


def read_json(path: Path, default=None):
    if not path.exists():
        return {} if default is None else default
    try:
        return json.loads(path.read_text(encoding="utf-8-sig"))
    except Exception as ex:
        return {"_error": str(ex), "_path": str(path)}


def latest_dir(root: Path, pattern: str):
    items = sorted([x for x in root.glob(pattern) if x.is_dir()], key=lambda x: x.name)
    return items[-1] if items else None


def latest_file(root: Path, pattern: str):
    items = sorted([x for x in root.glob(pattern) if x.is_file()], key=lambda x: x.name)
    return items[-1] if items else None


def collect_data():
    organ_status = read_json(ADMIN / "ORGAN_STATUS.json", {})
    self_report = read_json(ADMIN / "SELF_REPORT.json", {})
    continuity_status = read_json(REPORTS / "ADMINISTRATUM_CONTINUITY_STATUS.json", {})
    doctr_status = read_json(ROOT / "ORGANS" / "DOCTRINARIUM" / "STATUS" / "DOCTRINARIUM_STATUS.json", {})

    lp = latest_dir(CONT_PACKS, "CONTINUITY_PACK_*")
    lc = latest_file(CONT_COMPS, "CONTINUITY_COMPARISON_*.json")
    br = read_json(lp / "BUILD_RECEIPT.json", {}) if lp else {}
    cmp = read_json(lc, {}) if lc else {}

    missing_evidence = []
    for req in [
        ADMIN / "ORGAN_CONTRACT.json",
        ADMIN / "ORGAN_STATUS.json",
        ADMIN / "SELF_REPORT.json",
        BUILD_SCRIPT,
        COMPARE_SCRIPT,
    ]:
        if not req.exists():
            missing_evidence.append(str(req))

    return {
        "created_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "organ_status": organ_status,
        "self_report": self_report,
        "continuity_status": continuity_status,
        "doctrinarium_status": doctr_status,
        "latest_continuity_pack_path": str(lp) if lp else None,
        "latest_continuity_comparison_path": str(lc) if lc else None,
        "latest_build_receipt": br,
        "latest_comparison": cmp,
        "continuity_health": {
            "pack_exists": lp is not None,
            "comparison_exists": lc is not None,
            "comparison_verdict": cmp.get("verdict") if isinstance(cmp, dict) else None,
        },
        "missing_evidence": missing_evidence,
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
        if parsed.path == "/favicon.ico":
            self.send_response(204)
            self.end_headers()
            return
        if parsed.path == "/api/data":
            self.send_json(collect_data())
            return
        return super().do_GET()

    def _run_python(self, script_path: Path, extra_args: list):
        py = sys.executable or "python"
        cmd = [py, str(script_path)] + extra_args
        return subprocess.run(cmd, capture_output=True, text=True, timeout=240)

    def do_POST(self):
        parsed = urlparse(self.path)

        if parsed.path == "/api/build-continuity-pack":
            if not BUILD_SCRIPT.exists():
                self.send_json({"ok": False, "error": f"Build script missing: {BUILD_SCRIPT}"}, 404)
                return

            try:
                run_id = "DASHBOARD-" + time.strftime("%Y%m%d-%H%M%S", time.gmtime())
                b = self._run_python(BUILD_SCRIPT, ["--root", str(ROOT), "--trigger", "dashboard_button", "--run-id", run_id])
            except Exception as ex:
                self.send_json({"ok": False, "error": str(ex)}, 500)
                return

            build_ok = b.returncode == 0
            build_payload = None
            try:
                build_payload = json.loads((b.stdout or "").strip().splitlines()[-1])
            except Exception:
                build_payload = {"raw_stdout": b.stdout[-4000:] if b.stdout else ""}

            compare_payload = None
            compare_ok = False
            compare_exit = None
            compare_stdout = ""
            compare_stderr = ""

            if COMPARE_SCRIPT.exists() and build_ok:
                try:
                    c = self._run_python(COMPARE_SCRIPT, ["--root", str(ROOT)])
                    compare_ok = c.returncode == 0
                    compare_exit = c.returncode
                    compare_stdout = c.stdout[-4000:]
                    compare_stderr = c.stderr[-4000:]
                    try:
                        compare_payload = json.loads((c.stdout or "").strip().splitlines()[-1])
                    except Exception:
                        compare_payload = {"raw_stdout": compare_stdout}
                except Exception as ex:
                    compare_ok = False
                    compare_payload = {"error": str(ex)}

            data = collect_data()
            self.send_json(
                {
                    "ok": build_ok,
                    "build_exit_code": b.returncode,
                    "build_stdout": (b.stdout or "")[-4000:],
                    "build_stderr": (b.stderr or "")[-4000:],
                    "build_result": build_payload,
                    "compare_ran": COMPARE_SCRIPT.exists() and build_ok,
                    "compare_ok": compare_ok,
                    "compare_exit_code": compare_exit,
                    "compare_stdout": compare_stdout,
                    "compare_stderr": compare_stderr,
                    "compare_result": compare_payload,
                    "data": data,
                },
                200 if build_ok else 500,
            )
            return

        if parsed.path == "/api/open":
            qs = parse_qs(parsed.query)
            target = (qs.get("target") or [""])[0]
            allowed = {
                "packs": CONT_PACKS,
                "reports": REPORTS,
                "administratum": ADMIN,
            }
            p = allowed.get(target)
            if not p:
                self.send_json({"ok": False, "error": "Unknown target"}, 400)
                return
            if not p.exists():
                self.send_json({"ok": False, "error": f"Path not found: {p}"}, 404)
                return
            try:
                os.startfile(str(p))
                self.send_json({"ok": True, "path": str(p)})
            except Exception as ex:
                self.send_json({"ok": False, "error": str(ex)}, 500)
            return

        self.send_json({"ok": False, "error": "Not found"}, 404)


def main():
    port = 8792
    server = ThreadingHTTPServer(("127.0.0.1", port), Handler)
    url = f"http://127.0.0.1:{port}"
    print(f"Administratum Dashboard v0.1 running at {url}")
    webbrowser.open(url)
    server.serve_forever()


if __name__ == "__main__":
    main()
