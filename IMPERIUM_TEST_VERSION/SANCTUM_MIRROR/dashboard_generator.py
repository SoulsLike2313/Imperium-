#!/usr/bin/env python3
"""
DASHBOARD GENERATOR
Generates HTML dashboards from backend truth data.

Features:
- Evidence links to source receipts
- Freshness indicators (stale data warnings)
- Auto-generated from backend truth

Usage:
    py -3 dashboard_generator.py                    # Generate all dashboards
    py -3 dashboard_generator.py --organ THRONE    # Generate specific organ dashboard
    py -3 dashboard_generator.py --master          # Generate master dashboard only
"""

import argparse
import json
from datetime import datetime, timezone, timedelta
from pathlib import Path


FRESHNESS_THRESHOLD_HOURS = 24


def get_test_version_root():
    """Get the test version root directory."""
    return Path(__file__).parent.parent


def load_json_safe(filepath):
    """Load JSON file safely."""
    try:
        with open(filepath, "r", encoding="utf-8-sig") as f:
            return json.load(f)
    except:
        return None


def get_file_freshness(filepath):
    """Get freshness info for a file."""
    try:
        path = Path(filepath)
        if not path.exists():
            return {"fresh": False, "age_hours": None, "status": "MISSING"}
        
        mtime = datetime.fromtimestamp(path.stat().st_mtime, tz=timezone.utc)
        now = datetime.now(timezone.utc)
        age = now - mtime
        age_hours = age.total_seconds() / 3600
        
        if age_hours < FRESHNESS_THRESHOLD_HOURS:
            return {"fresh": True, "age_hours": round(age_hours, 1), "status": "FRESH", "mtime": mtime.isoformat()}
        else:
            return {"fresh": False, "age_hours": round(age_hours, 1), "status": "STALE", "mtime": mtime.isoformat()}
    except:
        return {"fresh": False, "age_hours": None, "status": "ERROR"}


def get_latest_receipt(organ_id):
    """Get latest receipt for an organ."""
    root = get_test_version_root()
    receipts_dir = root / "RECEIPTS"
    
    # Map organ to receipt prefix
    prefix_map = {
        "MECHANICUS": "RCP-MECH-",
        "INQUISITION": "RCP-INQ-",
        "SMOKE": "RCP-SMOKE-",
        "MASTER": "RCP-MASTER-"
    }
    
    prefix = prefix_map.get(organ_id, f"RCP-{organ_id[:4].upper()}-")
    
    receipts = list(receipts_dir.glob(f"{prefix}*.json"))
    if not receipts:
        return None
    
    latest = max(receipts, key=lambda x: x.stat().st_mtime)
    return {
        "path": str(latest.relative_to(root)),
        "name": latest.name,
        "freshness": get_file_freshness(latest)
    }


def get_status_color(status):
    """Get color for status."""
    colors = {
        "PASS": "#28a745",
        "TESTED": "#28a745",
        "COMPLETE": "#28a745",
        "SEED": "#17a2b8",
        "PARTIAL": "#ffc107",
        "IN_PROGRESS": "#ffc107",
        "FAIL": "#dc3545",
        "SCAFFOLD": "#6c757d",
        "NOT_STARTED": "#6c757d",
        "UNKNOWN": "#6c757d"
    }
    return colors.get(status, "#6c757d")


def get_status_icon(status):
    """Get icon for status."""
    icons = {
        "PASS": "✅",
        "TESTED": "✅",
        "COMPLETE": "✅",
        "SEED": "🌱",
        "PARTIAL": "⚠️",
        "IN_PROGRESS": "⏳",
        "FAIL": "❌",
        "SCAFFOLD": "🏗️",
        "NOT_STARTED": "⏸️",
        "UNKNOWN": "❓"
    }
    return icons.get(status, "❓")


def generate_organ_dashboard(organ_id):
    """Generate dashboard for a specific organ."""
    root = get_test_version_root()
    organ_dir = root / "ORGANS" / organ_id
    
    if not organ_dir.exists():
        return None
    
    # Load contract
    contract = load_json_safe(organ_dir / "ORGAN_CONTRACT.json")
    contract_freshness = get_file_freshness(organ_dir / "ORGAN_CONTRACT.json")
    
    # Get scripts
    scripts_dir = organ_dir / "SCRIPTS"
    scripts = list(scripts_dir.glob("*.py")) if scripts_dir.exists() else []
    
    # Get reports with freshness
    reports_dir = organ_dir / "REPORTS"
    reports = []
    if reports_dir.exists():
        for r in reports_dir.glob("*.json"):
            reports.append({
                "path": r,
                "name": r.name,
                "freshness": get_file_freshness(r)
            })
    reports = sorted(reports, key=lambda x: x["path"].stat().st_mtime, reverse=True)[:5]
    
    # Get latest receipt
    receipt = get_latest_receipt(organ_id)
    
    # Build HTML
    status = contract.get("status", "UNKNOWN") if contract else "UNKNOWN"
    purpose = contract.get("purpose", "") if contract else ""
    
    # Freshness indicator
    freshness_html = ""
    if contract_freshness["status"] == "STALE":
        freshness_html = f'<span style="color: #ffc107; font-size: 0.8em;">⚠️ Contract stale ({contract_freshness["age_hours"]}h)</span>'
    elif contract_freshness["status"] == "FRESH":
        freshness_html = f'<span style="color: #28a745; font-size: 0.8em;">✅ Fresh ({contract_freshness["age_hours"]}h)</span>'
    
    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{organ_id} Dashboard</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ 
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: #1a1a2e; color: #eee; padding: 20px;
        }}
        .header {{ 
            background: linear-gradient(135deg, #16213e 0%, #0f3460 100%);
            padding: 30px; border-radius: 10px; margin-bottom: 20px;
        }}
        .header h1 {{ font-size: 2em; margin-bottom: 10px; }}
        .status-badge {{
            display: inline-block; padding: 5px 15px; border-radius: 20px;
            font-weight: bold; background: {get_status_color(status)};
        }}
        .freshness {{ margin-top: 10px; }}
        .card {{ 
            background: #16213e; border-radius: 10px; padding: 20px; 
            margin-bottom: 15px;
        }}
        .card h2 {{ color: #e94560; margin-bottom: 15px; font-size: 1.2em; }}
        .card ul {{ list-style: none; }}
        .card li {{ padding: 8px 0; border-bottom: 1px solid #0f3460; }}
        .card li:last-child {{ border-bottom: none; }}
        .grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 20px; }}
        .meta {{ color: #888; font-size: 0.9em; }}
        a {{ color: #e94560; text-decoration: none; }}
        a:hover {{ text-decoration: underline; }}
        .timestamp {{ color: #666; font-size: 0.8em; margin-top: 20px; }}
        .evidence-link {{ 
            background: #0f3460; padding: 10px; border-radius: 5px; 
            margin-top: 15px; font-size: 0.9em;
        }}
        .stale {{ color: #ffc107; }}
        .fresh {{ color: #28a745; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>{get_status_icon(status)} {organ_id}</h1>
        <span class="status-badge">{status}</span>
        <p class="meta" style="margin-top: 10px;">{purpose}</p>
        <div class="freshness">{freshness_html}</div>
    </div>
    
    <div class="grid">
        <div class="card">
            <h2>📜 Contract</h2>
            <ul>
                <li><strong>Status:</strong> {status}</li>
                <li><strong>Purpose:</strong> {purpose}</li>
                <li><strong>Backend:</strong> {contract.get('backend_face', {}).get('responsibility', 'N/A') if contract else 'N/A'}</li>
                <li><strong>Frontend:</strong> {contract.get('frontend_face', {}).get('responsibility', 'N/A') if contract else 'N/A'}</li>
                <li><strong>Support:</strong> {contract.get('support_face', {}).get('responsibility', 'N/A') if contract else 'N/A'}</li>
            </ul>
            <div class="evidence-link">
                📎 Evidence: <a href="../ORGAN_CONTRACT.json">ORGAN_CONTRACT.json</a>
            </div>
        </div>
        
        <div class="card">
            <h2>🔧 Scripts ({len(scripts)})</h2>
            <ul>
"""
    
    for script in scripts:
        html += f'                <li>📄 <a href="../SCRIPTS/{script.name}">{script.name}</a></li>\n'
    
    if not scripts:
        html += "                <li class='meta'>No scripts found</li>\n"
    
    html += """            </ul>
        </div>
        
        <div class="card">
            <h2>📊 Reports</h2>
            <ul>
"""
    
    for report in reports:
        freshness_class = "fresh" if report["freshness"]["fresh"] else "stale"
        freshness_icon = "✅" if report["freshness"]["fresh"] else "⚠️"
        age = report["freshness"].get("age_hours", "?")
        html += f'                <li><span class="{freshness_class}">{freshness_icon}</span> <a href="../REPORTS/{report["name"]}">{report["name"]}</a> <span class="meta">({age}h)</span></li>\n'
    
    if not reports:
        html += "                <li class='meta'>No reports found</li>\n"
    
    # Evidence section
    evidence_html = ""
    if receipt:
        receipt_freshness = receipt["freshness"]
        freshness_class = "fresh" if receipt_freshness["fresh"] else "stale"
        freshness_icon = "✅" if receipt_freshness["fresh"] else "⚠️"
        evidence_html = f"""
        <div class="card">
            <h2>🧾 Latest Evidence</h2>
            <ul>
                <li><strong>Receipt:</strong> <a href="../../RECEIPTS/{receipt['name']}">{receipt['name']}</a></li>
                <li><strong>Freshness:</strong> <span class="{freshness_class}">{freshness_icon} {receipt_freshness['status']} ({receipt_freshness.get('age_hours', '?')}h)</span></li>
            </ul>
        </div>
"""
    
    html += f"""            </ul>
        </div>
        {evidence_html}
    </div>
    
    <p class="timestamp">Generated: {datetime.now(timezone.utc).isoformat()}</p>
    <p><a href="../../SANCTUM_MIRROR/master_dashboard.html">← Back to Master Dashboard</a></p>
</body>
</html>
"""
    
    # Save dashboard
    dashboard_dir = organ_dir / "DASHBOARD"
    dashboard_dir.mkdir(parents=True, exist_ok=True)
    
    dashboard_path = dashboard_dir / "index.html"
    with open(dashboard_path, "w", encoding="utf-8") as f:
        f.write(html)
    
    return dashboard_path


def generate_master_dashboard():
    """Generate master dashboard from all backend data."""
    root = get_test_version_root()
    
    # Load organ registry
    registry = load_json_safe(root / "REGISTRY" / "ORGAN_REGISTRY.json")
    registry_freshness = get_file_freshness(root / "REGISTRY" / "ORGAN_REGISTRY.json")
    organs = registry.get("organs", []) if registry else []
    
    # Load roadmap
    roadmap = load_json_safe(root / "KIRO_FORENSIC_SYNTHESIS" / "K10_KIRO_LAB_ROADMAP.json")
    phases = roadmap.get("phases", []) if roadmap else []
    current_phase = roadmap.get("current_phase", "UNKNOWN") if roadmap else "UNKNOWN"
    
    # Load latest reports with freshness
    smoke_report_path = root / "TESTING_FIELD" / "SMOKE_RESULTS" / "organ_smoke_report.json"
    smoke_report = load_json_safe(smoke_report_path)
    smoke_freshness = get_file_freshness(smoke_report_path)
    
    drift_report_path = root / "REPORTS" / "drift_report.json"
    drift_report = load_json_safe(drift_report_path)
    drift_freshness = get_file_freshness(drift_report_path)
    
    truth_report_path = root / "REPORTS" / "truth_aggregate.json"
    truth_report = load_json_safe(truth_report_path)
    truth_freshness = get_file_freshness(truth_report_path)
    
    # Get latest master receipt
    master_receipt = get_latest_receipt("MASTER")
    
    # Build HTML
    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>IMPERIUM Master Dashboard</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ 
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: #1a1a2e; color: #eee; padding: 20px;
        }}
        .header {{ 
            background: linear-gradient(135deg, #16213e 0%, #0f3460 100%);
            padding: 30px; border-radius: 10px; margin-bottom: 20px;
            text-align: center;
        }}
        .header h1 {{ font-size: 2.5em; margin-bottom: 10px; color: #e94560; }}
        .header .subtitle {{ color: #888; }}
        .stats {{ 
            display: flex; justify-content: center; gap: 30px; 
            margin-top: 20px; flex-wrap: wrap;
        }}
        .stat {{ text-align: center; }}
        .stat .value {{ font-size: 2em; font-weight: bold; color: #e94560; }}
        .stat .label {{ color: #888; font-size: 0.9em; }}
        .section {{ margin-bottom: 30px; }}
        .section h2 {{ 
            color: #e94560; margin-bottom: 15px; padding-bottom: 10px;
            border-bottom: 2px solid #0f3460;
        }}
        .grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 15px; }}
        .card {{ 
            background: #16213e; border-radius: 10px; padding: 20px;
            transition: transform 0.2s;
        }}
        .card:hover {{ transform: translateY(-3px); }}
        .card h3 {{ margin-bottom: 10px; }}
        .card .status {{ 
            display: inline-block; padding: 3px 10px; border-radius: 15px;
            font-size: 0.8em; font-weight: bold;
        }}
        .card a {{ color: #e94560; text-decoration: none; }}
        .card a:hover {{ text-decoration: underline; }}
        .phase-list {{ list-style: none; }}
        .phase-list li {{ 
            padding: 10px; margin-bottom: 5px; border-radius: 5px;
            background: #0f3460;
        }}
        .timestamp {{ color: #666; font-size: 0.8em; margin-top: 30px; text-align: center; }}
        .evidence-section {{ 
            background: #0f3460; padding: 15px; border-radius: 5px; 
            margin-top: 20px;
        }}
        .evidence-section h3 {{ color: #e94560; margin-bottom: 10px; }}
        .evidence-item {{ padding: 5px 0; }}
        .stale {{ color: #ffc107; }}
        .fresh {{ color: #28a745; }}
        .freshness-badge {{
            display: inline-block; padding: 2px 8px; border-radius: 10px;
            font-size: 0.7em; margin-left: 10px;
        }}
        .freshness-badge.fresh {{ background: #28a745; }}
        .freshness-badge.stale {{ background: #ffc107; color: #000; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>⚔️ IMPERIUM</h1>
        <p class="subtitle">Master Dashboard — Test Version</p>
        <div class="stats">
            <div class="stat">
                <div class="value">{len(organs)}</div>
                <div class="label">Organs</div>
            </div>
            <div class="stat">
                <div class="value">{sum(1 for p in phases if p.get('status') == 'COMPLETE')}/{len(phases)}</div>
                <div class="label">Phases Complete</div>
            </div>
            <div class="stat">
                <div class="value">{smoke_report.get('summary', {}).get('passed', 0) if smoke_report else '?'}/{smoke_report.get('summary', {}).get('total', 0) if smoke_report else '?'}</div>
                <div class="label">Smoke Tests</div>
            </div>
            <div class="stat">
                <div class="value">{drift_report.get('verdict', '?') if drift_report else '?'}</div>
                <div class="label">Drift Status</div>
            </div>
        </div>
    </div>
    
    <div class="section">
        <h2>📊 Roadmap Progress</h2>
        <ul class="phase-list">
"""
    
    for phase in phases:
        status = phase.get("status", "UNKNOWN")
        icon = get_status_icon(status)
        color = get_status_color(status)
        is_current = phase.get("phase_id") == current_phase
        
        html += f"""            <li style="border-left: 4px solid {color}; {'background: #1a3a5c;' if is_current else ''}">
                {icon} <strong>{phase.get('name', 'Unknown')}</strong>
                <span style="float: right; color: {color};">{status}</span>
                {'<span style="color: #e94560; margin-left: 10px;">← CURRENT</span>' if is_current else ''}
            </li>
"""
    
    html += """        </ul>
    </div>
    
    <div class="section">
        <h2>🏛️ Organs</h2>
        <div class="grid">
"""
    
    for organ in sorted(organs, key=lambda x: x.get("organ_id", "")):
        status = organ.get("status", "UNKNOWN")
        icon = get_status_icon(status)
        color = get_status_color(status)
        organ_id = organ.get("organ_id", "UNKNOWN")
        
        # Check if dashboard exists
        dashboard_path = root / "ORGANS" / organ_id / "DASHBOARD" / "index.html"
        has_dashboard = dashboard_path.exists()
        
        html += f"""            <div class="card">
                <h3>{icon} {organ.get('name', organ_id)}</h3>
                <span class="status" style="background: {color};">{status}</span>
                <p style="color: #888; font-size: 0.9em; margin-top: 10px;">{organ.get('purpose', '')[:60]}...</p>
                {'<p style="margin-top: 10px;"><a href="../ORGANS/' + organ_id + '/DASHBOARD/index.html">View Dashboard →</a></p>' if has_dashboard else ''}
            </div>
"""
    
    # Evidence section
    smoke_fresh_class = "fresh" if smoke_freshness["fresh"] else "stale"
    smoke_fresh_icon = "✅" if smoke_freshness["fresh"] else "⚠️"
    drift_fresh_class = "fresh" if drift_freshness["fresh"] else "stale"
    drift_fresh_icon = "✅" if drift_freshness["fresh"] else "⚠️"
    truth_fresh_class = "fresh" if truth_freshness["fresh"] else "stale"
    truth_fresh_icon = "✅" if truth_freshness["fresh"] else "⚠️"
    registry_fresh_class = "fresh" if registry_freshness["fresh"] else "stale"
    registry_fresh_icon = "✅" if registry_freshness["fresh"] else "⚠️"
    
    html += f"""        </div>
    </div>
    
    <div class="section">
        <h2>🔍 System Health</h2>
        <div class="grid">
            <div class="card">
                <h3>Smoke Tests <span class="freshness-badge {smoke_fresh_class}">{smoke_fresh_icon} {smoke_freshness.get('age_hours', '?')}h</span></h3>
                <p>Passed: {smoke_report.get('summary', {}).get('passed', '?') if smoke_report else '?'}</p>
                <p>Failed: {smoke_report.get('summary', {}).get('failed', '?') if smoke_report else '?'}</p>
                <p>Verdict: <strong>{smoke_report.get('verdict', '?') if smoke_report else '?'}</strong></p>
                <p style="margin-top: 10px;"><a href="../TESTING_FIELD/SMOKE_RESULTS/organ_smoke_report.json">📎 Evidence</a></p>
            </div>
            <div class="card">
                <h3>Drift Detection <span class="freshness-badge {drift_fresh_class}">{drift_fresh_icon} {drift_freshness.get('age_hours', '?')}h</span></h3>
                <p>Verdict: <strong>{drift_report.get('verdict', '?') if drift_report else '?'}</strong></p>
                <p style="margin-top: 10px;"><a href="../REPORTS/drift_report.json">📎 Evidence</a></p>
            </div>
            <div class="card">
                <h3>Truth Spine <span class="freshness-badge {truth_fresh_class}">{truth_fresh_icon} {truth_freshness.get('age_hours', '?')}h</span></h3>
                <p>Status: <strong>{truth_report.get('overall_status', '?') if truth_report else '?'}</strong></p>
                <p style="margin-top: 10px;"><a href="../REPORTS/truth_aggregate.json">📎 Evidence</a></p>
            </div>
        </div>
    </div>
    
    <div class="evidence-section">
        <h3>🧾 Evidence Trail</h3>
        <div class="evidence-item">
            <span class="{registry_fresh_class}">{registry_fresh_icon}</span> 
            <a href="../REGISTRY/ORGAN_REGISTRY.json">ORGAN_REGISTRY.json</a> 
            <span class="meta">({registry_freshness.get('age_hours', '?')}h)</span>
        </div>
"""
    
    if master_receipt:
        mr_fresh = master_receipt["freshness"]
        mr_class = "fresh" if mr_fresh["fresh"] else "stale"
        mr_icon = "✅" if mr_fresh["fresh"] else "⚠️"
        html += f"""        <div class="evidence-item">
            <span class="{mr_class}">{mr_icon}</span> 
            <a href="../{master_receipt['path']}">{master_receipt['name']}</a> 
            <span class="meta">({mr_fresh.get('age_hours', '?')}h)</span>
        </div>
"""
    
    html += f"""    </div>
    
    <p class="timestamp">Generated: {datetime.now(timezone.utc).isoformat()}</p>
</body>
</html>
"""
    
    # Save master dashboard
    dashboard_path = root / "SANCTUM_MIRROR" / "master_dashboard.html"
    with open(dashboard_path, "w", encoding="utf-8") as f:
        f.write(html)
    
    return dashboard_path


def main():
    parser = argparse.ArgumentParser(description="Generate dashboards from backend truth")
    parser.add_argument("--organ", help="Generate dashboard for specific organ")
    parser.add_argument("--master", action="store_true", help="Generate master dashboard only")
    parser.add_argument("--all", action="store_true", help="Generate all dashboards")
    args = parser.parse_args()
    
    print("=" * 60)
    print("DASHBOARD GENERATOR")
    print("=" * 60)
    print()
    
    generated = []
    
    if args.organ:
        path = generate_organ_dashboard(args.organ)
        if path:
            generated.append(str(path))
            print(f"✅ Generated: {path}")
        else:
            print(f"❌ Failed to generate dashboard for {args.organ}")
    
    elif args.master:
        path = generate_master_dashboard()
        generated.append(str(path))
        print(f"✅ Generated: {path}")
    
    else:  # Generate all
        # Master dashboard
        path = generate_master_dashboard()
        generated.append(str(path))
        print(f"✅ Master: {path}")
        
        # Organ dashboards
        root = get_test_version_root()
        organs_dir = root / "ORGANS"
        
        for organ_dir in organs_dir.iterdir():
            if organ_dir.is_dir():
                path = generate_organ_dashboard(organ_dir.name)
                if path:
                    generated.append(str(path))
                    print(f"✅ {organ_dir.name}: {path}")
    
    print()
    print(f"Total generated: {len(generated)}")


if __name__ == "__main__":
    main()
