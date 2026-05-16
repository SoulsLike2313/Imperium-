#!/usr/bin/env python3
"""
SNAPSHOT COLLECTOR
Collects current state of IMPERIUM_TEST_VERSION for Delta Window.

Usage:
    py -3 snapshot_collector.py [--output SNAPSHOTS/SNAPSHOT_<timestamp>]
"""

import argparse
import json
import os
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path


def get_git_info(repo_root):
    """Get git HEAD and status."""
    try:
        head = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=repo_root, capture_output=True, text=True
        ).stdout.strip()
        
        log = subprocess.run(
            ["git", "log", "-1", "--oneline"],
            cwd=repo_root, capture_output=True, text=True
        ).stdout.strip()
        
        status = subprocess.run(
            ["git", "status", "--short"],
            cwd=repo_root, capture_output=True, text=True
        ).stdout.strip()
        
        commit_count = subprocess.run(
            ["git", "rev-list", "--count", "HEAD"],
            cwd=repo_root, capture_output=True, text=True
        ).stdout.strip()
        
        return {
            "head": head,
            "log": log,
            "status_lines": status.split("\n") if status else [],
            "commit_count": int(commit_count) if commit_count.isdigit() else 0,
            "is_clean": len(status) == 0
        }
    except Exception as e:
        return {"error": str(e)}


def count_files_by_extension(root_path):
    """Count files by extension."""
    counts = {}
    for path in Path(root_path).rglob("*"):
        if path.is_file():
            ext = path.suffix.lower() or "(no ext)"
            counts[ext] = counts.get(ext, 0) + 1
    return counts


def find_files(root_path, patterns):
    """Find files matching patterns."""
    found = []
    for pattern in patterns:
        for path in Path(root_path).rglob(pattern):
            if path.is_file():
                found.append(str(path.relative_to(root_path)))
    return found


def read_json_safe(path):
    """Read JSON file safely."""
    try:
        with open(path, "r", encoding="utf-8-sig") as f:
            return json.load(f)
    except Exception as e:
        return {"error": str(e), "path": str(path)}


def collect_snapshot(test_version_root, repo_root):
    """Collect full snapshot of test version state."""
    tv_path = Path(test_version_root)
    
    snapshot = {
        "snapshot_id": f"SNAP-{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "repo_root": str(repo_root),
        "test_version_root": str(test_version_root),
        "scope": "IMPERIUM_TEST_VERSION_ONLY",
        "git": get_git_info(repo_root),
        "file_counts": {},
        "dashboards": [],
        "reports": [],
        "receipts": [],
        "audits": [],
        "runs": [],
        "truth_state": None,
        "smoke_report": None,
        "inquisition_audit": None,
        "mechanicus_health": None,
        "generated_artifacts": {
            "pyc_count": 0,
            "pycache_dirs": 0,
            "zip_count": 0,
            "screenshot_count": 0
        }
    }
    
    # File counts
    snapshot["file_counts"] = count_files_by_extension(tv_path)
    
    # Dashboards
    dashboard_patterns = [
        "SANCTUM_MIRROR/index.html",
        "SANCTUM_MIRROR/master_dashboard.html",
        "ORGANS/*/DASHBOARD/index.html",
        "LIVE_WORKBENCH/DASHBOARD/index.html",
    ]
    for pattern in dashboard_patterns:
        for p in tv_path.glob(pattern):
            snapshot["dashboards"].append(str(p.relative_to(tv_path)))
    
    # Reports
    reports_dir = tv_path / "REPORTS"
    if reports_dir.exists():
        snapshot["reports"] = [f.name for f in reports_dir.glob("*.json")]
        snapshot["reports"].extend([f.name for f in reports_dir.glob("*.md")])
    
    # Receipts
    receipts_dir = tv_path / "RECEIPTS"
    if receipts_dir.exists():
        snapshot["receipts"] = [f.name for f in receipts_dir.glob("RCP-*.json")]
    
    # Audits
    audits_dir = tv_path / "AUDITS"
    if audits_dir.exists():
        snapshot["audits"] = [d.name for d in audits_dir.iterdir() if d.is_dir()]
    
    # Runs
    runs_dir = tv_path / "RUNS"
    if runs_dir.exists():
        snapshot["runs"] = [d.name for d in runs_dir.iterdir() if d.is_dir()]
    
    # Truth aggregate
    truth_path = tv_path / "REPORTS" / "truth_aggregate.json"
    if truth_path.exists():
        snapshot["truth_state"] = read_json_safe(truth_path)
    
    # Smoke report
    smoke_path = tv_path / "TESTING_FIELD" / "SMOKE_RESULTS" / "latest_smoke_report.json"
    if smoke_path.exists():
        snapshot["smoke_report"] = read_json_safe(smoke_path)
    
    # Inquisition audit
    inq_path = tv_path / "ORGANS" / "INQUISITION" / "REPORTS" / "latest_audit.json"
    if inq_path.exists():
        snapshot["inquisition_audit"] = read_json_safe(inq_path)
    
    # Mechanicus health
    mech_path = tv_path / "ORGANS" / "MECHANICUS" / "REPORTS" / "latest_script_health.json"
    if mech_path.exists():
        snapshot["mechanicus_health"] = read_json_safe(mech_path)
    
    # Generated artifacts
    snapshot["generated_artifacts"]["pyc_count"] = len(list(tv_path.rglob("*.pyc")))
    snapshot["generated_artifacts"]["pycache_dirs"] = len(list(tv_path.rglob("__pycache__")))
    snapshot["generated_artifacts"]["zip_count"] = len(list(tv_path.rglob("*.zip")))
    snapshot["generated_artifacts"]["screenshot_count"] = len(list(tv_path.rglob("*.png")))
    
    return snapshot


def main():
    parser = argparse.ArgumentParser(description="Collect test version snapshot")
    parser.add_argument("--output", help="Output directory for snapshot")
    parser.add_argument("--test-version", default=".", help="Test version root")
    parser.add_argument("--repo-root", help="Repository root (for git info)")
    
    args = parser.parse_args()
    
    # Determine paths
    tv_root = Path(args.test_version).resolve()
    if args.repo_root:
        repo_root = Path(args.repo_root).resolve()
    else:
        # Assume repo root is parent of test version
        repo_root = tv_root.parent
    
    # Collect snapshot
    snapshot = collect_snapshot(tv_root, repo_root)
    
    # Output
    if args.output:
        output_dir = Path(args.output)
        output_dir.mkdir(parents=True, exist_ok=True)
        output_path = output_dir / "snapshot.json"
    else:
        output_dir = tv_root / "TESTING_FIELD" / "DELTA_WINDOW" / "SNAPSHOTS" / snapshot["snapshot_id"]
        output_dir.mkdir(parents=True, exist_ok=True)
        output_path = output_dir / "snapshot.json"
    
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(snapshot, f, indent=2, ensure_ascii=False)
    
    print(f"Snapshot saved: {output_path}")
    print(f"Snapshot ID: {snapshot['snapshot_id']}")
    print(f"Git HEAD: {snapshot['git'].get('head', 'unknown')[:8]}")
    print(f"Dashboards: {len(snapshot['dashboards'])}")
    print(f"Reports: {len(snapshot['reports'])}")
    print(f"Receipts: {len(snapshot['receipts'])}")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
