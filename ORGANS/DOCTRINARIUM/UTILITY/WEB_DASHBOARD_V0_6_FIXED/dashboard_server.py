import json
import os
import subprocess
import time
import webbrowser
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
from pathlib import Path
from urllib.parse import urlparse, parse_qs

ROOT = Path(r"E:\IMPERIUM")
DOC = ROOT / "ORGANS" / "DOCTRINARIUM"
WEB = DOC / "UTILITY" / "WEB_DASHBOARD_V0_6_FIXED"
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

def law_array(laws):
    if not isinstance(laws, dict):
        return []
    for key in ("laws", "mandatory_laws", "entries"):
        val = laws.get(key)
        if isinstance(val, list):
            return val
    return []

def compute_useful_metrics(status, gaps, utility, laws):
    gaps = gaps or {}
    utility = utility or {}
    laws = laws or {}

    organs = gaps.get("organs") or []
    major_gaps = gaps.get("major_gaps") or []
    utility_organs = utility.get("organs") or []
    law_arr = law_array(laws)

    by_organ = {}

    for organ in organs:
        oid = organ.get("organ_id") or "UNKNOWN_ORGAN"
        blockers = organ.get("blockers") or []
        risk_score = min(100, len(blockers) * 9 + (0 if organ.get("organ_contract_exists") else 20))

        by_organ[oid] = {
            "organ_id": oid,
            "classification": organ.get("classification"),
            "blockers": len(blockers),
            "missing_contract": not bool(organ.get("organ_contract_exists")),
            "missing_self_report": not bool(organ.get("self_report_exists")),
            "missing_receipts": not bool(organ.get("receipts_exists")),
            "why_not_canon": organ.get("why_not_canon") or [],
            "risk_score": risk_score,
            "priority": "HIGH" if risk_score >= 80 else ("MEDIUM" if risk_score >= 40 else "LOW"),
        }

    for u in utility_organs:
        oid = u.get("organ_id") or "UNKNOWN_ORGAN"
        if oid not in by_organ:
            by_organ[oid] = {"organ_id": oid}
        by_organ[oid]["utility_declared"] = bool(u.get("utility_declared"))
        by_organ[oid]["utility_script_backed"] = bool(u.get("script_backed"))
        by_organ[oid]["utility_warnings"] = len(u.get("warnings") or []) + len(u.get("blockers") or [])

    gap_types = {
        "missing_contract": 0,
        "missing_receipts": 0,
        "missing_self_report": 0,
        "missing_allowed_roots": 0,
        "missing_forbidden_roots": 0,
        "missing_entrypoints": 0,
        "missing_required_receipts": 0,
        "missing_responsibilities": 0,
        "missing_exclusions": 0,
        "missing_current_blockers": 0,
        "other": 0,
    }

    for gap in major_gaps:
        text = str(gap.get("gap", "")).lower()
        if "organ_contract" in text:
            gap_types["missing_contract"] += 1
        elif "receipts directory" in text:
            gap_types["missing_receipts"] += 1
        elif "self-report" in text or "status report" in text:
            gap_types["missing_self_report"] += 1
        elif "allowed_write_roots" in text:
            gap_types["missing_allowed_roots"] += 1
        elif "forbidden_roots" in text:
            gap_types["missing_forbidden_roots"] += 1
        elif "entrypoints" in text:
            gap_types["missing_entrypoints"] += 1
        elif "required_receipts" in text:
            gap_types["missing_required_receipts"] += 1
        elif "responsibilities missing" in text:
            gap_types["missing_responsibilities"] += 1
        elif "explicitly_not_responsible_for" in text:
            gap_types["missing_exclusions"] += 1
        elif "current_blockers" in text:
            gap_types["missing_current_blockers"] += 1
        else:
            gap_types["other"] += 1

    hard_laws = [law for law in law_arr if str(law.get("severity", "")).upper() == "HARD_BLOCK"]
    not_enforced = [
        law for law in law_arr
        if "NOT_FULLY" in str(law.get("enforcement_status", "")).upper()
        or "NOT_ENFORCED" in str(law.get("enforcement_status", "")).upper()
    ]

    priority_fixes = []
    for oid, data in sorted(by_organ.items(), key=lambda kv: kv[1].get("risk_score", 0), reverse=True):
        if oid == "_PORTS":
            continue

        if data.get("missing_contract"):
            priority_fixes.append({
                "organ": oid,
                "action": "Create ORGAN_CONTRACT.json",
                "reason": "Required for organ standard and clear responsibility boundaries."
            })

        if data.get("missing_self_report"):
            priority_fixes.append({
                "organ": oid,
                "action": "Create SELF_REPORT.json or equivalent status report",
                "reason": "Doctrinarium needs organ self-report evidence."
            })

        if data.get("missing_receipts"):
            priority_fixes.append({
                "organ": oid,
                "action": "Create RECEIPTS directory and first receipt",
                "reason": "No receipt means no proof."
            })

        if not data.get("utility_declared", False):
            priority_fixes.append({
                "organ": oid,
                "action": "Declare dedicated organ utility/dashboard",
                "reason": "Required before CANON_CANDIDATE / CANON_V0_1."
            })

        if len(priority_fixes) >= 24:
            break

    return {
        "dashboard_verdict": "USEFUL_DIAGNOSTIC_DASHBOARD_V0_6_FIXED",
        "organ_risk": list(by_organ.values()),
        "gap_types": gap_types,
        "law_metrics": {
            "total_laws": len(law_arr),
            "hard_laws": len(hard_laws),
            "not_fully_enforced": len(not_enforced),
            "enforced": max(0, len(law_arr) - len(not_enforced)),
        },
        "priority_fixes": priority_fixes,
    }

def api_data():
    status = read_json(STATUS / "DOCTRINARIUM_STATUS.json")
    gaps = read_json(REPORTS / "ALL_ORGANS_GAP_REPORT.json")
    utility = read_json(REPORTS / "ORGAN_UTILITY_GAP_REPORT.json")
    laws = read_json(LAWS / "LAW_INDEX.json")
    enforcement = read_json(LAWS / "LAW_ENFORCEMENT_MAP.json")
    doctrine = read_json(DOCTRINE / "DOCTRINE_INDEX.json")
    useful = compute_useful_metrics(status, gaps, utility, laws)

    return {
        "created_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "status": status,
        "gaps": gaps,
        "utility": utility,
        "laws": laws,
        "enforcement": enforcement,
        "doctrine": doctrine,
        "paths": PATHS,
        "useful": useful,
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

            try:
                result = subprocess.run(
                    ["pwsh", "-NoProfile", "-ExecutionPolicy", "Bypass", "-File", str(REFRESH)],
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
            allowed = {
                "reports": REPORTS,
                "status": STATUS,
                "doctrine": DOCTRINE,
                "laws": LAWS,
                "standards": STANDARDS,
                "utility": UTILITY,
                "root": ROOT,
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
            except Exception as e:
                self.send_json({"ok": False, "error": str(e)}, 500)
            return

        self.send_json({"ok": False, "error": "Not found"}, 404)

def main():
    port = 8789
    server = ThreadingHTTPServer(("127.0.0.1", port), Handler)
    url = f"http://127.0.0.1:{port}"
    print(f"Doctrinarium Dashboard v0.6 fixed running at {url}")
    webbrowser.open(url)
    server.serve_forever()

if __name__ == "__main__":
    main()
