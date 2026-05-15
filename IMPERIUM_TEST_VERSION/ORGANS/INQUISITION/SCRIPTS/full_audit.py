#!/usr/bin/env python3
"""
full_audit.py - Run all Inquisition audits and produce combined report.

Runs:
1. Fake green detector
2. Stale truth detector
3. Warning budget check

Usage:
    python full_audit.py [--repo-root PATH]

Exit codes:
    0 = All audits passed
    1 = One or more audits failed
"""

import sys
import os
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, Any

def find_repo_root() -> Path:
    """Find IMPERIUM repo root."""
    current = Path(__file__).resolve()
    for parent in current.parents:
        if (parent / "AGENTS.md").exists():
            return parent
    return Path.cwd()

def run_fake_green_audit(repo_root: Path) -> Dict[str, Any]:
    """Run fake green detector."""
    try:
        # Import and run
        script_dir = Path(__file__).parent
        sys.path.insert(0, str(script_dir))
        
        from fake_green_detector import generate_report
        
        output_dir = repo_root / "ORGANS" / "INQUISITION" / "REPORTS"
        output_dir.mkdir(parents=True, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_path = output_dir / f"fake_green_audit_{timestamp}.json"
        
        report = generate_report(repo_root, output_path)
        return {
            "audit": "fake_green",
            "passed": report["overall_passed"],
            "summary": report["summary"],
            "report_path": str(output_path)
        }
    except Exception as e:
        return {
            "audit": "fake_green",
            "passed": False,
            "error": str(e)
        }

def run_stale_truth_audit(repo_root: Path, max_age_hours: int = 24) -> Dict[str, Any]:
    """Run stale truth detector."""
    try:
        script_dir = Path(__file__).parent
        sys.path.insert(0, str(script_dir))
        
        from stale_truth_detector import generate_report
        
        output_dir = repo_root / "ORGANS" / "INQUISITION" / "REPORTS"
        output_dir.mkdir(parents=True, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_path = output_dir / f"stale_truth_audit_{timestamp}.json"
        
        report = generate_report(repo_root, max_age_hours, output_path)
        return {
            "audit": "stale_truth",
            "passed": report["overall_passed"],
            "summary": report["summary"],
            "report_path": str(output_path)
        }
    except Exception as e:
        return {
            "audit": "stale_truth",
            "passed": False,
            "error": str(e)
        }

def check_warning_budget(repo_root: Path) -> Dict[str, Any]:
    """Check warning budget compliance."""
    budget_path = repo_root / "ORGANS" / "INQUISITION" / "WARNING_BUDGET.json"
    
    if not budget_path.exists():
        return {
            "audit": "warning_budget",
            "passed": False,
            "error": "WARNING_BUDGET.json not found"
        }
    
    try:
        with open(budget_path, "r", encoding="utf-8") as f:
            budget = json.load(f)
        
        violations = []
        known_debt = budget.get("known_debt", {})
        
        for debt_name, debt_info in known_debt.items():
            if debt_info.get("over_budget"):
                violations.append({
                    "item": debt_name,
                    "current": debt_info.get("current"),
                    "budget": debt_info.get("budget"),
                    "reason": debt_info.get("reason")
                })
        
        return {
            "audit": "warning_budget",
            "passed": len(violations) == 0,
            "violations": violations,
            "budget_path": str(budget_path)
        }
    except Exception as e:
        return {
            "audit": "warning_budget",
            "passed": False,
            "error": str(e)
        }

def run_full_audit(repo_root: Path) -> Dict[str, Any]:
    """Run all audits and produce combined report."""
    timestamp = datetime.now().isoformat()
    
    audits = [
        run_fake_green_audit(repo_root),
        run_stale_truth_audit(repo_root),
        check_warning_budget(repo_root)
    ]
    
    all_passed = all(a["passed"] for a in audits)
    passed_count = sum(1 for a in audits if a["passed"])
    
    report = {
        "timestamp": timestamp,
        "repo_root": str(repo_root),
        "summary": {
            "total_audits": len(audits),
            "passed": passed_count,
            "failed": len(audits) - passed_count
        },
        "audits": audits,
        "overall_passed": all_passed,
        "verdict": "PASS" if all_passed else "FAIL"
    }
    
    # Save combined report
    output_dir = repo_root / "ORGANS" / "INQUISITION" / "REPORTS"
    output_dir.mkdir(parents=True, exist_ok=True)
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_path = output_dir / f"full_audit_{ts}.json"
    
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)
    
    report["report_path"] = str(output_path)
    return report

def main():
    import argparse
    parser = argparse.ArgumentParser(description="Run full Inquisition audit")
    parser.add_argument("--repo-root", type=Path, help="Repository root path")
    args = parser.parse_args()
    
    repo_root = args.repo_root or find_repo_root()
    
    print("=" * 60)
    print("INQUISITION FULL AUDIT")
    print("=" * 60)
    print(f"Repo root: {repo_root}")
    print()
    
    report = run_full_audit(repo_root)
    
    print("Audit Results:")
    print("-" * 40)
    for audit in report["audits"]:
        status = "PASS" if audit["passed"] else "FAIL"
        print(f"  [{status}] {audit['audit']}")
        if audit.get("error"):
            print(f"         Error: {audit['error']}")
        if audit.get("violations"):
            for v in audit["violations"]:
                print(f"         Violation: {v['item']}")
    
    print("-" * 40)
    print(f"Summary: {report['summary']['passed']}/{report['summary']['total_audits']} passed")
    print(f"Report saved: {report['report_path']}")
    
    if report["overall_passed"]:
        print("\n[PASS] All audits passed")
        sys.exit(0)
    else:
        print(f"\n[FAIL] {report['summary']['failed']} audit(s) failed")
        sys.exit(1)

if __name__ == "__main__":
    main()
