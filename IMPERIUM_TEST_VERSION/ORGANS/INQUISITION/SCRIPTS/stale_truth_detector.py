#!/usr/bin/env python3
"""
stale_truth_detector.py - Detect outdated truth claims.

Stale Truth = claims about system state that are outdated:
- Report older than threshold
- HEAD changed since report
- Files modified since report

Usage:
    python stale_truth_detector.py [--repo-root PATH] [--max-age-hours 24]

Exit codes:
    0 = No stale truth detected
    1 = Stale truth detected
"""

import sys
import os
import json
import subprocess
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, Any, List

def find_repo_root() -> Path:
    """Find IMPERIUM_TEST_VERSION root (not main repo)."""
    current = Path(__file__).resolve()
    for parent in current.parents:
        if parent.name == "IMPERIUM_TEST_VERSION":
            return parent
    # Fallback to script's test version root
    return Path(__file__).resolve().parent.parent.parent.parent

def get_current_head(repo_root: Path) -> str:
    """Get current git HEAD."""
    try:
        result = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=str(repo_root),
            capture_output=True,
            text=True
        )
        return result.stdout.strip()[:7] if result.returncode == 0 else "unknown"
    except:
        return "unknown"

def scan_truth_files(repo_root: Path) -> List[Dict[str, Any]]:
    """Scan for files that claim truth about system state."""
    truth_files = []
    
    patterns = [
        "**/VERDICT*.json",
        "**/STATUS*.json",
        "**/*_REPORT.json",
        "**/*_state*.json",
        "**/BASELINE*.json"
    ]
    
    for pattern in patterns:
        for path in repo_root.glob(pattern):
            if ".git" in str(path) or "__pycache__" in str(path):
                continue
            if "IMPERIUM_TEST_VERSION" in str(path):
                continue
            
            stat = path.stat()
            truth_files.append({
                "path": str(path.relative_to(repo_root)),
                "full_path": path,
                "modified_time": datetime.fromtimestamp(stat.st_mtime),
                "size": stat.st_size
            })
    
    return truth_files

def check_for_staleness(
    truth_file: Dict[str, Any],
    current_head: str,
    max_age_hours: int
) -> Dict[str, Any]:
    """Check single truth file for staleness."""
    result = {
        "path": truth_file["path"],
        "is_stale": False,
        "stale_reasons": [],
        "age_hours": None,
        "claimed_head": None,
        "current_head": current_head
    }
    
    path = truth_file["full_path"]
    modified_time = truth_file["modified_time"]
    
    # Check age
    age = datetime.now() - modified_time
    age_hours = age.total_seconds() / 3600
    result["age_hours"] = round(age_hours, 1)
    
    if age_hours > max_age_hours:
        result["is_stale"] = True
        result["stale_reasons"].append(f"Age {age_hours:.1f}h > {max_age_hours}h threshold")
    
    # Check HEAD if JSON
    if path.suffix == ".json":
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
            
            # Look for HEAD reference
            for key in ["head", "HEAD", "commit", "source_commit", "git_head"]:
                if key in data:
                    claimed_head = str(data[key])[:7]
                    result["claimed_head"] = claimed_head
                    
                    if claimed_head != current_head and claimed_head != "unknown":
                        result["is_stale"] = True
                        result["stale_reasons"].append(
                            f"HEAD mismatch: claimed {claimed_head}, current {current_head}"
                        )
                    break
        except:
            pass
    
    return result

def generate_report(
    repo_root: Path,
    max_age_hours: int,
    output_path: Path = None
) -> Dict[str, Any]:
    """Generate stale truth detection report."""
    timestamp = datetime.now().isoformat()
    current_head = get_current_head(repo_root)
    
    truth_files = scan_truth_files(repo_root)
    results = []
    
    for tf in truth_files:
        result = check_for_staleness(tf, current_head, max_age_hours)
        results.append(result)
    
    stale_files = [r for r in results if r["is_stale"]]
    
    report = {
        "timestamp": timestamp,
        "repo_root": str(repo_root),
        "current_head": current_head,
        "max_age_hours": max_age_hours,
        "summary": {
            "total_truth_files": len(truth_files),
            "stale_count": len(stale_files),
            "fresh_count": len(results) - len(stale_files)
        },
        "stale_files": stale_files,
        "all_results": results,
        "overall_passed": len(stale_files) == 0
    }
    
    if output_path:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2)
    
    return report

def main():
    import argparse
    parser = argparse.ArgumentParser(description="Detect stale truth claims")
    parser.add_argument("--repo-root", type=Path, help="Repository root path")
    parser.add_argument("--max-age-hours", type=int, default=24, help="Max age in hours")
    parser.add_argument("--output", type=Path, help="Output report path")
    args = parser.parse_args()
    
    repo_root = args.repo_root or find_repo_root()
    output_path = args.output
    
    if not output_path:
        output_dir = repo_root / "ORGANS" / "INQUISITION" / "REPORTS"
        output_dir.mkdir(parents=True, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_path = output_dir / f"stale_truth_audit_{timestamp}.json"
    
    print("=" * 60)
    print("INQUISITION STALE TRUTH DETECTOR")
    print("=" * 60)
    print(f"Repo root: {repo_root}")
    print(f"Max age: {args.max_age_hours} hours")
    
    report = generate_report(repo_root, args.max_age_hours, output_path)
    
    print(f"Current HEAD: {report['current_head']}")
    print(f"\nSummary:")
    print(f"  Truth files scanned: {report['summary']['total_truth_files']}")
    print(f"  Stale: {report['summary']['stale_count']}")
    print(f"  Fresh: {report['summary']['fresh_count']}")
    
    if report["stale_files"]:
        print(f"\nStale files:")
        for sf in report["stale_files"][:10]:
            print(f"  - {sf['path']}")
            for reason in sf["stale_reasons"]:
                print(f"      {reason}")
    
    print(f"\nReport saved: {output_path}")
    
    if report["overall_passed"]:
        print("\n[PASS] No stale truth detected")
        sys.exit(0)
    else:
        print(f"\n[FAIL] {report['summary']['stale_count']} stale truth file(s)")
        sys.exit(1)

if __name__ == "__main__":
    main()
