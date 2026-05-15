#!/usr/bin/env python3
"""
generate_workbench_status.py - Generate Live Workbench status and dashboard.

Usage:
    py -3 IMPERIUM_TEST_VERSION\\LIVE_WORKBENCH\\SCRIPTS\\generate_workbench_status.py
"""

import json
import os
import sys
from datetime import datetime
from pathlib import Path

# Paths
SCRIPT_DIR = Path(__file__).parent
WORKBENCH_ROOT = SCRIPT_DIR.parent
SANDBOX_ROOT = WORKBENCH_ROOT / "SANDBOX_PROJECT"
REPORTS_DIR = WORKBENCH_ROOT / "REPORTS"
DASHBOARD_DIR = WORKBENCH_ROOT / "DASHBOARD"


def get_sandbox_files() -> list:
    """Get list of files in sandbox project."""
    files = []
    if SANDBOX_ROOT.exists():
        for f in SANDBOX_ROOT.rglob("*"):
            if f.is_file() and "__pycache__" not in str(f):
                rel_path = f.relative_to(SANDBOX_ROOT)
                stat = f.stat()
                files.append({
                    "path": str(rel_path),
                    "size": stat.st_size,
                    "modified": datetime.fromtimestamp(stat.st_mtime).isoformat()
                })
    return files


def load_latest_test_report() -> dict:
    """Load latest test report if exists."""
    latest_path = REPORTS_DIR / "latest_test_report.json"
    if latest_path.exists():
        with open(latest_path, "r", encoding="utf-8") as f:
            return json.load(f)
    return None


def generate_status() -> dict:
    """Generate workbench status."""
    timestamp = datetime.now().isoformat()
    
    sandbox_files = get_sandbox_files()
    test_report = load_latest_test_report()
    
    status = {
        "schema_version": "IMPERIUM_WORKBENCH_STATUS_V0_1",
        "generated_at": timestamp,
        "workbench_root": str(WORKBENCH_ROOT),
        "sandbox": {
            "path": str(SANDBOX_ROOT),
            "exists": SANDBOX_ROOT.exists(),
            "files": sandbox_files,
            "file_count": len(sandbox_files)
        },
        "latest_test": {
            "available": test_report is not None,
            "status": test_report.get("status") if test_report else None,
            "timestamp": test_report.get("timestamp") if test_report else None,
            "summary": test_report.get("summary") if test_report else None
        }
    }
    
    return status


def generate_dashboard_html(status: dict) -> str:
    """Generate dashboard HTML."""
    test_status = status["latest_test"]["status"] or "NO_DATA"
    test_class = "pass" if test_status == "PASS" else "fail" if test_status == "FAIL" else "nodata"
    
    test_summary = status["latest_test"]["summary"]
    if test_summary:
        test_info = f"{test_summary['passed']}/{test_summary['total']} passed"
    else:
        test_info = "No tests run yet"
    
    files_html = ""
    for f in status["sandbox"]["files"]:
        files_html += f"<tr><td>{f['path']}</td><td>{f['size']} bytes</td><td>{f['modified']}</td></tr>\\n"
    
    html = f"""<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <title>Live Workbench</title>
    <style>
        body {{ font-family: 'Segoe UI', sans-serif; background: #1a1a2e; color: #ecf0f1; padding: 20px; }}
        .header {{ text-align: center; border-bottom: 2px solid #d4af37; padding-bottom: 20px; margin-bottom: 20px; }}
        .header h1 {{ color: #d4af37; }}
        .card {{ background: #16213e; border-radius: 10px; padding: 20px; margin: 10px 0; }}
        .metric {{ display: flex; justify-content: space-between; padding: 10px 0; border-bottom: 1px solid #2c3e50; }}
        .metric:last-child {{ border-bottom: none; }}
        .value {{ font-size: 1.5em; font-weight: bold; }}
        .pass {{ color: #27ae60; }}
        .fail {{ color: #e74c3c; }}
        .nodata {{ color: #95a5a6; }}
        .timestamp {{ color: #7f8c8d; font-size: 0.9em; }}
        table {{ width: 100%; border-collapse: collapse; margin-top: 10px; }}
        th, td {{ padding: 8px; text-align: left; border-bottom: 1px solid #2c3e50; }}
        th {{ color: #d4af37; }}
        code {{ background: #0d1117; padding: 2px 6px; border-radius: 3px; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>LIVE WORKBENCH</h1>
        <p class="timestamp">Generated: {status['generated_at']}</p>
    </div>
    
    <div class="card">
        <h2>Test Status</h2>
        <div class="metric">
            <span>Latest Test</span>
            <span class="value {test_class}">{test_status}</span>
        </div>
        <div class="metric">
            <span>Results</span>
            <span class="value">{test_info}</span>
        </div>
        <div class="metric">
            <span>Last Run</span>
            <span>{status['latest_test']['timestamp'] or 'Never'}</span>
        </div>
    </div>
    
    <div class="card">
        <h2>Sandbox Project</h2>
        <div class="metric">
            <span>Path</span>
            <span><code>{status['sandbox']['path']}</code></span>
        </div>
        <div class="metric">
            <span>Files</span>
            <span class="value">{status['sandbox']['file_count']}</span>
        </div>
        <table>
            <tr><th>File</th><th>Size</th><th>Modified</th></tr>
            {files_html}
        </table>
    </div>
    
    <div class="card">
        <h2>Commands</h2>
        <p><strong>Run tests:</strong></p>
        <code>py -3 IMPERIUM_TEST_VERSION\\LIVE_WORKBENCH\\SCRIPTS\\run_sandbox_tests.py</code>
        <p style="margin-top: 15px;"><strong>Refresh status:</strong></p>
        <code>py -3 IMPERIUM_TEST_VERSION\\LIVE_WORKBENCH\\SCRIPTS\\generate_workbench_status.py</code>
    </div>
</body>
</html>"""
    
    return html


def main():
    print("Generating Live Workbench status...")
    
    status = generate_status()
    
    # Save status JSON
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    status_path = REPORTS_DIR / "latest_workbench_status.json"
    with open(status_path, "w", encoding="utf-8") as f:
        json.dump(status, f, indent=2, ensure_ascii=False)
    print(f"Status JSON: {status_path}")
    
    # Generate dashboard
    DASHBOARD_DIR.mkdir(parents=True, exist_ok=True)
    html = generate_dashboard_html(status)
    dashboard_path = DASHBOARD_DIR / "index.html"
    with open(dashboard_path, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"Dashboard: {dashboard_path}")
    
    # Print summary
    print()
    print("=" * 50)
    print("WORKBENCH STATUS")
    print("=" * 50)
    print(f"Sandbox files: {status['sandbox']['file_count']}")
    print(f"Latest test: {status['latest_test']['status'] or 'None'}")
    if status['latest_test']['summary']:
        s = status['latest_test']['summary']
        print(f"Test results: {s['passed']}/{s['total']} passed")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
