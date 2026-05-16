#!/usr/bin/env python3
"""
GENERATE DELTA WINDOW
Creates HTML dashboard for Delta Window MVP.

Usage:
    py -3 generate_delta_window.py [--report REPORTS/latest_delta_report.json]
"""

import argparse
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path


HTML_TEMPLATE = '''<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>IMPERIUM TEST VERSION DELTA WINDOW</title>
    <style>
        :root {{
            --bg-dark: #1a1a2e;
            --bg-card: #16213e;
            --accent-gold: #d4af37;
            --accent-green: #00ff88;
            --accent-red: #ff4444;
            --accent-yellow: #ffaa00;
            --text-primary: #e8e8e8;
            --text-secondary: #a0a0a0;
        }}
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{
            font-family: 'Segoe UI', system-ui, sans-serif;
            background: var(--bg-dark);
            color: var(--text-primary);
            min-height: 100vh;
            padding: 20px;
        }}
        .header {{
            text-align: center;
            padding: 20px;
            border-bottom: 2px solid var(--accent-gold);
            margin-bottom: 20px;
        }}
        .header h1 {{
            color: var(--accent-gold);
            font-size: 1.8em;
            margin-bottom: 10px;
        }}
        .header .scope-badge {{
            background: var(--accent-gold);
            color: var(--bg-dark);
            padding: 5px 15px;
            border-radius: 20px;
            font-weight: bold;
            display: inline-block;
        }}
        .header .meta {{
            color: var(--text-secondary);
            margin-top: 10px;
            font-size: 0.9em;
        }}
        .grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
            gap: 20px;
        }}
        .card {{
            background: var(--bg-card);
            border-radius: 10px;
            padding: 20px;
            border: 1px solid #333;
        }}
        .card h2 {{
            color: var(--accent-gold);
            font-size: 1.1em;
            margin-bottom: 15px;
            padding-bottom: 10px;
            border-bottom: 1px solid #333;
        }}
        .verdict-block {{
            grid-column: 1 / -1;
            text-align: center;
            padding: 30px;
        }}
        .verdict {{
            font-size: 2em;
            font-weight: bold;
            padding: 20px 40px;
            border-radius: 10px;
            display: inline-block;
        }}
        .verdict.COMMIT_OK {{ background: var(--accent-green); color: var(--bg-dark); }}
        .verdict.REPAIR_REQUIRED {{ background: var(--accent-yellow); color: var(--bg-dark); }}
        .verdict.BLOCKED {{ background: var(--accent-red); color: white; }}
        .verdict.REJECT {{ background: var(--accent-red); color: white; }}
        .verdict.UNKNOWN {{ background: #666; color: white; }}
        .status-pass {{ color: var(--accent-green); }}
        .status-fail {{ color: var(--accent-red); }}
        .status-partial {{ color: var(--accent-yellow); }}
        .status-unknown {{ color: var(--text-secondary); }}
        .stat-row {{
            display: flex;
            justify-content: space-between;
            padding: 8px 0;
            border-bottom: 1px solid #333;
        }}
        .stat-row:last-child {{ border-bottom: none; }}
        .stat-label {{ color: var(--text-secondary); }}
        .stat-value {{ font-weight: bold; }}
        .file-list {{
            max-height: 200px;
            overflow-y: auto;
            font-family: monospace;
            font-size: 0.85em;
        }}
        .file-list div {{
            padding: 4px 0;
            border-bottom: 1px solid #222;
        }}
        .file-added {{ color: var(--accent-green); }}
        .file-modified {{ color: var(--accent-yellow); }}
        .file-deleted {{ color: var(--accent-red); }}
        .reasons-list {{
            list-style: none;
            padding: 0;
        }}
        .reasons-list li {{
            padding: 8px 0;
            border-bottom: 1px solid #333;
        }}
        .reasons-list li:last-child {{ border-bottom: none; }}
        .action-panel {{
            grid-column: 1 / -1;
            text-align: center;
            padding: 20px;
        }}
        .action-btn {{
            background: var(--bg-card);
            border: 2px solid var(--accent-gold);
            color: var(--accent-gold);
            padding: 10px 20px;
            margin: 5px;
            border-radius: 5px;
            cursor: pointer;
            font-size: 0.9em;
        }}
        .action-btn:hover {{
            background: var(--accent-gold);
            color: var(--bg-dark);
        }}
        .display-only {{
            font-size: 0.7em;
            color: var(--text-secondary);
            display: block;
            margin-top: 5px;
        }}
        .component-grid {{
            display: grid;
            grid-template-columns: 1fr auto;
            gap: 5px;
        }}
        .risk-indicator {{
            padding: 2px 8px;
            border-radius: 3px;
            font-size: 0.8em;
        }}
        .risk-low {{ background: var(--accent-green); color: var(--bg-dark); }}
        .risk-medium {{ background: var(--accent-yellow); color: var(--bg-dark); }}
        .risk-high {{ background: var(--accent-red); color: white; }}
        footer {{
            text-align: center;
            padding: 20px;
            color: var(--text-secondary);
            font-size: 0.8em;
            margin-top: 20px;
        }}
    </style>
</head>
<body>
    <div class="header">
        <h1>⚙️ IMPERIUM TEST VERSION DELTA WINDOW</h1>
        <div class="scope-badge">SCOPE: IMPERIUM_TEST_VERSION ONLY</div>
        <div class="meta">
            Generated: {generated_at}<br>
            Delta ID: {delta_id}<br>
            Mode: {mode}
        </div>
    </div>

    <div class="grid">
        <!-- Verdict Block -->
        <div class="card verdict-block">
            <div class="verdict {verdict_class}">{verdict}</div>
            <div style="margin-top: 15px;">
                <ul class="reasons-list">
                    {reasons_html}
                </ul>
            </div>
        </div>

        <!-- Git Truth -->
        <div class="card">
            <h2>📊 Git Truth</h2>
            <div class="stat-row">
                <span class="stat-label">Baseline</span>
                <span class="stat-value">{baseline_label}</span>
            </div>
            <div class="stat-row">
                <span class="stat-label">Current</span>
                <span class="stat-value">{current_label}</span>
            </div>
            <div class="stat-row">
                <span class="stat-label">Main Canon Touched</span>
                <span class="stat-value {main_canon_class}">{main_canon_touched}</span>
            </div>
        </div>

        <!-- File Delta -->
        <div class="card">
            <h2>📁 File Delta</h2>
            <div class="stat-row">
                <span class="stat-label">Added</span>
                <span class="stat-value file-added">{files_added}</span>
            </div>
            <div class="stat-row">
                <span class="stat-label">Modified</span>
                <span class="stat-value file-modified">{files_modified}</span>
            </div>
            <div class="stat-row">
                <span class="stat-label">Deleted</span>
                <span class="stat-value file-deleted">{files_deleted}</span>
            </div>
            <div class="stat-row">
                <span class="stat-label">Total Changes</span>
                <span class="stat-value">{total_changes}</span>
            </div>
        </div>

        <!-- Truth Delta -->
        <div class="card">
            <h2>✅ Truth State</h2>
            <div class="stat-row">
                <span class="stat-label">Current Status</span>
                <span class="stat-value {truth_status_class}">{truth_status}</span>
            </div>
            <div class="stat-row">
                <span class="stat-label">Pass Count</span>
                <span class="stat-value status-pass">{pass_count}</span>
            </div>
            <div class="stat-row">
                <span class="stat-label">Fail Count</span>
                <span class="stat-value status-fail">{fail_count}</span>
            </div>
            <div class="component-grid" style="margin-top: 10px;">
                {components_html}
            </div>
        </div>

        <!-- Risk Assessment -->
        <div class="card">
            <h2>⚠️ Risk Assessment</h2>
            <div class="stat-row">
                <span class="stat-label">Fake Green Risk</span>
                <span class="risk-indicator risk-{fake_green_risk}">{fake_green_risk}</span>
            </div>
            <div class="stat-row">
                <span class="stat-label">Stale Truth Risk</span>
                <span class="risk-indicator risk-{stale_truth_risk}">{stale_truth_risk}</span>
            </div>
            <div class="stat-row">
                <span class="stat-label">Generated Churn</span>
                <span class="risk-indicator risk-{generated_churn_risk}">{generated_churn_risk}</span>
            </div>
            <div class="stat-row">
                <span class="stat-label">Main Scope Risk</span>
                <span class="risk-indicator risk-{main_scope_risk}">{main_scope_risk}</span>
            </div>
        </div>

        <!-- Evidence Delta -->
        <div class="card">
            <h2>📋 New Evidence</h2>
            <div class="stat-row">
                <span class="stat-label">New Reports</span>
                <span class="stat-value">{new_reports_count}</span>
            </div>
            <div class="stat-row">
                <span class="stat-label">New Receipts</span>
                <span class="stat-value">{new_receipts_count}</span>
            </div>
            <div class="stat-row">
                <span class="stat-label">New Audits</span>
                <span class="stat-value">{new_audits_count}</span>
            </div>
            <div class="stat-row">
                <span class="stat-label">New Runs</span>
                <span class="stat-value">{new_runs_count}</span>
            </div>
        </div>

        <!-- Dashboards -->
        <div class="card">
            <h2>🖥️ Dashboards</h2>
            <div class="stat-row">
                <span class="stat-label">Found</span>
                <span class="stat-value">{dashboards_count}</span>
            </div>
            <div class="file-list" style="margin-top: 10px;">
                {dashboards_html}
            </div>
        </div>

        <!-- Changed Files -->
        <div class="card" style="grid-column: 1 / -1;">
            <h2>📝 Changed Files (Top 20)</h2>
            <div class="file-list">
                {changed_files_html}
            </div>
        </div>

        <!-- Action Panel -->
        <div class="card action-panel">
            <h2>🎯 Owner Actions</h2>
            <p style="color: var(--text-secondary); margin-bottom: 15px;">
                These buttons display recommended commands only. They do NOT execute git operations.
            </p>
            <button class="action-btn" onclick="alert('git add IMPERIUM_TEST_VERSION/\\ngit commit -m \\'[TEST] Delta Window changes\\'')">
                📦 Show Commit Command
                <span class="display-only">DISPLAY_ONLY_MVP</span>
            </button>
            <button class="action-btn" onclick="alert('cd IMPERIUM_TEST_VERSION\\n.\\\\RUN_ALL.ps1')">
                🔧 Show Repair Command
                <span class="display-only">DISPLAY_ONLY_MVP</span>
            </button>
            <button class="action-btn" onclick="alert('Request Servitor audit for test version')">
                🔍 Request Audit
                <span class="display-only">DISPLAY_ONLY_MVP</span>
            </button>
            <button class="action-btn" onclick="alert('git checkout -- IMPERIUM_TEST_VERSION/')">
                ↩️ Show Rollback Command
                <span class="display-only">DISPLAY_ONLY_MVP</span>
            </button>
        </div>

        <!-- Next Action -->
        <div class="card" style="grid-column: 1 / -1; text-align: center;">
            <h2>➡️ Recommended Next Step</h2>
            <p style="font-size: 1.2em; margin-top: 10px;">{next_action}</p>
        </div>
    </div>

    <footer>
        IMPERIUM TEST VERSION DELTA WINDOW MVP<br>
        Scope: IMPERIUM_TEST_VERSION only | Main canon: READ ONLY<br>
        This is not production UI. This is the first operator window for test-version evolution.
    </footer>
</body>
</html>
'''


def generate_html(report):
    """Generate HTML from delta report."""
    verdict = report["precommit_verdict"]["verdict"]
    
    # Reasons HTML
    reasons = report["precommit_verdict"].get("reasons", [])
    reasons_html = "\n".join(f"<li>{r}</li>" for r in reasons) if reasons else "<li>No issues</li>"
    
    # Components HTML
    components = report["truth_delta"].get("components", [])
    components_html = ""
    for c in components:
        status = c.get("status", "UNKNOWN")
        status_class = {
            "PASS": "status-pass",
            "FAIL": "status-fail",
            "PARTIAL": "status-partial"
        }.get(status, "status-unknown")
        components_html += f'<span>{c.get("name", "?")}</span><span class="{status_class}">{status}</span>\n'
    
    # Changed files HTML
    added = report["file_delta"].get("added", [])[:10]
    modified = report["file_delta"].get("modified", [])[:10]
    deleted = report["file_delta"].get("deleted", [])[:5]
    
    changed_files_html = ""
    for f in added:
        changed_files_html += f'<div class="file-added">+ {f}</div>\n'
    for f in modified:
        changed_files_html += f'<div class="file-modified">M {f}</div>\n'
    for f in deleted:
        changed_files_html += f'<div class="file-deleted">- {f}</div>\n'
    
    if not changed_files_html:
        changed_files_html = "<div>No changes detected</div>"
    
    # Dashboards HTML
    dashboards = report["dashboard_delta"].get("dashboards_found", [])
    dashboards_html = "\n".join(f"<div>{d}</div>" for d in dashboards) if dashboards else "<div>No dashboards found</div>"
    
    # Truth status class
    truth_status = report["truth_delta"].get("current_status", "UNKNOWN")
    truth_status_class = {
        "PASS": "status-pass",
        "FAIL": "status-fail",
        "PARTIAL": "status-partial"
    }.get(truth_status, "status-unknown")
    
    # Main canon class
    main_touched = report["scope"].get("main_canon_touched", False)
    main_canon_class = "status-fail" if main_touched else "status-pass"
    
    # Next action
    actions = report["precommit_verdict"].get("required_next_actions", [])
    if actions:
        next_action = actions[0]
    elif verdict == "COMMIT_OK":
        next_action = "Ready to commit. Run: git add IMPERIUM_TEST_VERSION/ && git commit"
    else:
        next_action = "Review issues and repair before commit"
    
    return HTML_TEMPLATE.format(
        generated_at=report.get("generated_at", "unknown"),
        delta_id=report.get("delta_id", "unknown"),
        mode=report.get("mode", "unknown"),
        verdict=verdict,
        verdict_class=verdict,
        reasons_html=reasons_html,
        baseline_label=report["baseline"].get("label", "unknown"),
        current_label=report["current"].get("label", "unknown"),
        main_canon_touched="YES" if main_touched else "NO",
        main_canon_class=main_canon_class,
        files_added=len(report["file_delta"].get("added", [])),
        files_modified=len(report["file_delta"].get("modified", [])),
        files_deleted=len(report["file_delta"].get("deleted", [])),
        total_changes=report["file_delta"].get("total_changes", 0),
        truth_status=truth_status,
        truth_status_class=truth_status_class,
        pass_count=report["truth_delta"].get("pass_count", 0),
        fail_count=report["truth_delta"].get("fail_count", 0),
        components_html=components_html,
        fake_green_risk=report["risk_delta"].get("fake_green_risk", "unknown"),
        stale_truth_risk=report["risk_delta"].get("stale_truth_risk", "unknown"),
        generated_churn_risk=report["risk_delta"].get("generated_churn_risk", "unknown"),
        main_scope_risk=report["risk_delta"].get("main_scope_risk", "unknown"),
        new_reports_count=len(report["evidence_delta"].get("new_reports", [])),
        new_receipts_count=len(report["evidence_delta"].get("new_receipts", [])),
        new_audits_count=len(report["evidence_delta"].get("new_audits", [])),
        new_runs_count=len(report["evidence_delta"].get("new_runs", [])),
        dashboards_count=len(dashboards),
        dashboards_html=dashboards_html,
        changed_files_html=changed_files_html,
        next_action=next_action
    )


def main():
    parser = argparse.ArgumentParser(description="Generate Delta Window HTML")
    parser.add_argument("--report", help="Path to delta report JSON")
    parser.add_argument("--output", help="Output HTML path")
    parser.add_argument("--test-version", default=".", help="Test version root")
    
    args = parser.parse_args()
    
    tv_root = Path(args.test_version).resolve()
    
    # Load report
    if args.report:
        report_path = Path(args.report)
    else:
        report_path = tv_root / "TESTING_FIELD" / "DELTA_WINDOW" / "REPORTS" / "latest_delta_report.json"
    
    if not report_path.exists():
        print(f"Error: Report not found: {report_path}")
        return 1
    
    with open(report_path, "r", encoding="utf-8") as f:
        report = json.load(f)
    
    # Generate HTML
    html = generate_html(report)
    
    # Output
    if args.output:
        output_path = Path(args.output)
    else:
        output_path = tv_root / "TESTING_FIELD" / "DELTA_WINDOW" / "delta_window.html"
    
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(html)
    
    print(f"Delta Window HTML generated: {output_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
