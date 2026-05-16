#!/usr/bin/env python3
"""
DELTA ANALYZER
Compares baseline vs current state for Delta Window.

Usage:
    py -3 delta_analyzer.py --mode precommit
    py -3 delta_analyzer.py --mode historical --old-commit <sha> --new-commit <sha>
"""

import argparse
import json
import os
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path


def get_git_diff_files(repo_root, test_version_path, old_ref="HEAD", new_ref=None):
    """Get changed files between refs, scoped to test version."""
    rel_path = test_version_path.relative_to(repo_root)
    
    if new_ref:
        # Historical: compare two commits
        cmd = ["git", "diff", "--name-status", old_ref, new_ref, "--", str(rel_path)]
    else:
        # Precommit: compare HEAD to worktree
        cmd = ["git", "diff", "--name-status", "HEAD", "--", str(rel_path)]
    
    result = subprocess.run(cmd, cwd=repo_root, capture_output=True, text=True)
    
    added = []
    modified = []
    deleted = []
    renamed = []
    
    for line in result.stdout.strip().split("\n"):
        if not line:
            continue
        parts = line.split("\t")
        status = parts[0]
        filepath = parts[1] if len(parts) > 1 else ""
        
        if status.startswith("A"):
            added.append(filepath)
        elif status.startswith("M"):
            modified.append(filepath)
        elif status.startswith("D"):
            deleted.append(filepath)
        elif status.startswith("R"):
            renamed.append({"from": filepath, "to": parts[2] if len(parts) > 2 else ""})
    
    # Also check untracked files for precommit
    if not new_ref:
        untracked_cmd = ["git", "ls-files", "--others", "--exclude-standard", "--", str(rel_path)]
        untracked = subprocess.run(untracked_cmd, cwd=repo_root, capture_output=True, text=True)
        for line in untracked.stdout.strip().split("\n"):
            if line and line not in added:
                added.append(line)
    
    return {
        "added": added,
        "modified": modified,
        "deleted": deleted,
        "renamed": renamed
    }


def get_diff_stat(repo_root, test_version_path, old_ref="HEAD", new_ref=None):
    """Get diff statistics."""
    rel_path = test_version_path.relative_to(repo_root)
    
    if new_ref:
        cmd = ["git", "diff", "--stat", old_ref, new_ref, "--", str(rel_path)]
    else:
        cmd = ["git", "diff", "--stat", "HEAD", "--", str(rel_path)]
    
    result = subprocess.run(cmd, cwd=repo_root, capture_output=True, text=True)
    return result.stdout.strip().split("\n") if result.stdout.strip() else []


def check_main_canon_touched(repo_root, test_version_path):
    """Check if files outside test version are modified."""
    rel_path = test_version_path.relative_to(repo_root)
    
    # Get all changed files
    cmd = ["git", "diff", "--name-only", "HEAD"]
    result = subprocess.run(cmd, cwd=repo_root, capture_output=True, text=True)
    
    for line in result.stdout.strip().split("\n"):
        if line and not line.startswith(str(rel_path)):
            return True, line
    
    # Check untracked
    cmd = ["git", "ls-files", "--others", "--exclude-standard"]
    result = subprocess.run(cmd, cwd=repo_root, capture_output=True, text=True)
    
    for line in result.stdout.strip().split("\n"):
        if line and not line.startswith(str(rel_path)):
            return True, line
    
    return False, None


def read_json_safe(path):
    """Read JSON safely."""
    try:
        with open(path, "r", encoding="utf-8-sig") as f:
            return json.load(f)
    except:
        return None


def analyze_truth_delta(test_version_path):
    """Analyze truth state changes."""
    truth_path = test_version_path / "REPORTS" / "truth_aggregate.json"
    
    if not truth_path.exists():
        return {
            "baseline_status": "UNKNOWN",
            "current_status": "UNKNOWN",
            "improved": [],
            "worsened": [],
            "unchanged": [],
            "unknown": ["truth_aggregate.json not found"]
        }
    
    truth = read_json_safe(truth_path)
    if not truth:
        return {
            "baseline_status": "UNKNOWN",
            "current_status": "UNKNOWN",
            "improved": [],
            "worsened": [],
            "unchanged": [],
            "unknown": ["Failed to read truth_aggregate.json"]
        }
    
    return {
        "baseline_status": "N/A (precommit mode)",
        "current_status": truth.get("overall_status", "UNKNOWN"),
        "pass_count": truth.get("pass_count", 0),
        "fail_count": truth.get("fail_count", 0),
        "components": [
            {
                "name": c.get("component_name", "unknown"),
                "status": c.get("status", "UNKNOWN")
            }
            for c in truth.get("components", [])
        ],
        "improved": [],
        "worsened": [],
        "unchanged": [],
        "unknown": []
    }


def analyze_dashboard_delta(test_version_path):
    """Analyze dashboard state."""
    dashboards = []
    
    patterns = [
        "SANCTUM_MIRROR/index.html",
        "SANCTUM_MIRROR/master_dashboard.html",
        "ORGANS/*/DASHBOARD/index.html",
        "LIVE_WORKBENCH/DASHBOARD/index.html",
    ]
    
    for pattern in patterns:
        for p in test_version_path.glob(pattern):
            dashboards.append({
                "path": str(p.relative_to(test_version_path)),
                "exists": True,
                "size": p.stat().st_size
            })
    
    return {
        "dashboards_found": [d["path"] for d in dashboards],
        "baseline_screenshots": [],
        "current_screenshots": [],
        "broken_links": [],
        "plastic_risks": []
    }


def analyze_evidence_delta(test_version_path, file_delta):
    """Analyze new evidence files."""
    new_reports = [f for f in file_delta["added"] if "REPORTS" in f and f.endswith(".json")]
    new_receipts = [f for f in file_delta["added"] if "RECEIPTS" in f and f.endswith(".json")]
    new_audits = [f for f in file_delta["added"] if "AUDITS" in f]
    new_runs = [f for f in file_delta["added"] if "RUNS" in f]
    
    return {
        "new_reports": new_reports,
        "new_receipts": new_receipts,
        "new_audits": new_audits,
        "new_runs": new_runs
    }


def calculate_risk(file_delta, main_canon_touched, truth_delta):
    """Calculate risk levels."""
    # Fake green risk
    fake_green_risk = "low"
    if truth_delta.get("current_status") == "PASS" and truth_delta.get("fail_count", 0) > 0:
        fake_green_risk = "high"
    
    # Stale truth risk
    stale_risk = "low"
    if truth_delta.get("current_status") == "UNKNOWN":
        stale_risk = "medium"
    
    # Generated churn
    generated_count = sum(1 for f in file_delta["added"] + file_delta["modified"] 
                         if any(x in f for x in [".pyc", "__pycache__", "SNAPSHOTS", "SCREENSHOTS"]))
    generated_risk = "low" if generated_count < 10 else "medium" if generated_count < 50 else "high"
    
    # Main scope risk
    main_risk = "high" if main_canon_touched else "low"
    
    return {
        "fake_green_risk": fake_green_risk,
        "stale_truth_risk": stale_risk,
        "generated_churn_risk": generated_risk,
        "main_scope_risk": main_risk
    }


def calculate_verdict(file_delta, main_canon_touched, risk_delta, truth_delta):
    """Calculate precommit verdict."""
    reasons = []
    
    # Check blockers
    if main_canon_touched:
        reasons.append("Main canon files modified outside test version")
        return {
            "safe_to_commit": False,
            "verdict": "BLOCKED",
            "reasons": reasons,
            "required_next_actions": ["Revert or move main canon changes"]
        }
    
    if risk_delta["fake_green_risk"] == "high":
        reasons.append("Fake green detected in truth state")
        return {
            "safe_to_commit": False,
            "verdict": "REPAIR_REQUIRED",
            "reasons": reasons,
            "required_next_actions": ["Fix fake green claims before commit"]
        }
    
    if truth_delta.get("current_status") == "FAIL":
        reasons.append(f"Truth state is FAIL (pass: {truth_delta.get('pass_count', 0)}, fail: {truth_delta.get('fail_count', 0)})")
    
    if truth_delta.get("current_status") == "UNKNOWN":
        reasons.append("Truth state is UNKNOWN")
    
    # Determine verdict
    if not reasons:
        return {
            "safe_to_commit": True,
            "verdict": "COMMIT_OK",
            "reasons": ["All checks passed", "Scope limited to test version"],
            "required_next_actions": []
        }
    
    if truth_delta.get("current_status") == "FAIL":
        return {
            "safe_to_commit": False,
            "verdict": "REPAIR_REQUIRED",
            "reasons": reasons,
            "required_next_actions": ["Fix failing components before commit"]
        }
    
    return {
        "safe_to_commit": True,
        "verdict": "COMMIT_OK",
        "reasons": reasons + ["Minor issues, commit allowed"],
        "required_next_actions": []
    }


def analyze_delta(repo_root, test_version_path, mode="precommit", old_commit=None, new_commit=None):
    """Main analysis function."""
    repo_root = Path(repo_root).resolve()
    test_version_path = Path(test_version_path).resolve()
    
    # Get git info
    head_result = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=repo_root, capture_output=True, text=True
    )
    current_head = head_result.stdout.strip()
    
    # File delta
    if mode == "precommit":
        file_delta = get_git_diff_files(repo_root, test_version_path)
        diff_stat = get_diff_stat(repo_root, test_version_path)
        baseline_commit = current_head
        current_commit = "worktree"
    else:
        file_delta = get_git_diff_files(repo_root, test_version_path, old_commit, new_commit)
        diff_stat = get_diff_stat(repo_root, test_version_path, old_commit, new_commit)
        baseline_commit = old_commit
        current_commit = new_commit
    
    # Check main canon
    main_touched, main_file = check_main_canon_touched(repo_root, test_version_path)
    
    # Truth delta
    truth_delta = analyze_truth_delta(test_version_path)
    
    # Dashboard delta
    dashboard_delta = analyze_dashboard_delta(test_version_path)
    
    # Evidence delta
    evidence_delta = analyze_evidence_delta(test_version_path, file_delta)
    
    # Risk calculation
    risk_delta = calculate_risk(file_delta, main_touched, truth_delta)
    
    # Verdict
    verdict = calculate_verdict(file_delta, main_touched, risk_delta, truth_delta)
    
    return {
        "delta_id": f"DELTA-{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "repo_root": str(repo_root),
        "scope_root": str(test_version_path),
        "mode": mode,
        "baseline": {
            "type": "git_head" if mode == "precommit" else "commit",
            "commit": baseline_commit,
            "label": f"HEAD ({baseline_commit[:8]})" if mode == "precommit" else baseline_commit[:8]
        },
        "current": {
            "type": "worktree" if mode == "precommit" else "commit",
            "commit": current_commit if mode == "historical" else None,
            "label": "Current worktree" if mode == "precommit" else current_commit[:8]
        },
        "scope": {
            "test_version_only": True,
            "main_canon_touched": main_touched,
            "main_canon_file": main_file
        },
        "file_delta": {
            "added": file_delta["added"],
            "modified": file_delta["modified"],
            "deleted": file_delta["deleted"],
            "renamed": file_delta["renamed"],
            "diff_stat": diff_stat,
            "total_changes": len(file_delta["added"]) + len(file_delta["modified"]) + len(file_delta["deleted"])
        },
        "truth_delta": truth_delta,
        "dashboard_delta": dashboard_delta,
        "evidence_delta": evidence_delta,
        "risk_delta": risk_delta,
        "precommit_verdict": verdict
    }


def main():
    parser = argparse.ArgumentParser(description="Analyze delta for Delta Window")
    parser.add_argument("--mode", choices=["precommit", "historical"], default="precommit")
    parser.add_argument("--old-commit", help="Old commit for historical mode")
    parser.add_argument("--new-commit", help="New commit for historical mode")
    parser.add_argument("--test-version", default=".", help="Test version root")
    parser.add_argument("--repo-root", help="Repository root")
    parser.add_argument("--output", help="Output file path")
    
    args = parser.parse_args()
    
    tv_root = Path(args.test_version).resolve()
    repo_root = Path(args.repo_root).resolve() if args.repo_root else tv_root.parent
    
    report = analyze_delta(
        repo_root, tv_root, args.mode,
        args.old_commit, args.new_commit
    )
    
    # Output
    if args.output:
        output_path = Path(args.output)
    else:
        output_path = tv_root / "TESTING_FIELD" / "DELTA_WINDOW" / "REPORTS" / "latest_delta_report.json"
    
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    
    print(f"Delta report saved: {output_path}")
    print(f"Mode: {report['mode']}")
    print(f"Changes: {report['file_delta']['total_changes']}")
    print(f"Verdict: {report['precommit_verdict']['verdict']}")
    
    return 0 if report['precommit_verdict']['safe_to_commit'] else 1


if __name__ == "__main__":
    sys.exit(main())
