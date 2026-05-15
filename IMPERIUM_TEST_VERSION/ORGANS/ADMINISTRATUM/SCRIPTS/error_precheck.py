#!/usr/bin/env python3
"""
error_precheck.py - Check for known error patterns before execution.

Reads KNOWN_ERRORS database and warns if current context matches known error patterns.

Usage:
    python error_precheck.py [--repo-root PATH] [--files FILE1 FILE2 ...]

Exit codes:
    0 = No known error patterns detected
    1 = Known error patterns detected (warning)
    2 = Blocking error pattern detected
"""

import sys
import os
import json
import re
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any

def find_repo_root() -> Path:
    """Find IMPERIUM repo root."""
    current = Path(__file__).resolve()
    for parent in current.parents:
        if (parent / "AGENTS.md").exists():
            return parent
    return Path.cwd()

def load_known_errors(repo_root: Path) -> List[Dict[str, Any]]:
    """Load known errors from database."""
    errors_dir = repo_root / "ORGANS" / "ADMINISTRATUM" / "KNOWN_ERRORS" / "errors"
    errors = []
    
    if not errors_dir.exists():
        return errors
    
    for error_file in errors_dir.glob("ERR-*.json"):
        try:
            with open(error_file, "r", encoding="utf-8") as f:
                error = json.load(f)
                if error.get("status") == "ACTIVE":
                    errors.append(error)
        except:
            pass
    
    return errors

def check_file_for_patterns(
    file_path: Path,
    errors: List[Dict[str, Any]]
) -> List[Dict[str, Any]]:
    """Check single file for known error patterns."""
    matches = []
    
    if not file_path.exists():
        return matches
    
    try:
        content = file_path.read_text(encoding="utf-8")
    except:
        return matches
    
    for error in errors:
        # Check if file is in affected_files
        rel_path = str(file_path).replace("\\", "/")
        affected = error.get("affected_files", [])
        
        for affected_pattern in affected:
            if affected_pattern.endswith("*"):
                if rel_path.startswith(affected_pattern[:-1]):
                    matches.append({
                        "error_id": error["error_id"],
                        "title": error["title"],
                        "severity": error["severity"],
                        "match_type": "affected_file",
                        "file": str(file_path)
                    })
            elif affected_pattern in rel_path:
                matches.append({
                    "error_id": error["error_id"],
                    "title": error["title"],
                    "severity": error["severity"],
                    "match_type": "affected_file",
                    "file": str(file_path)
                })
        
        # Check for specific patterns in content
        precheck = error.get("prevention", {}).get("precheck_rule", "")
        if precheck and "|" in precheck:
            # Simple pattern matching
            patterns = precheck.split("|")
            for pattern in patterns:
                pattern = pattern.strip()
                if pattern and pattern in content:
                    matches.append({
                        "error_id": error["error_id"],
                        "title": error["title"],
                        "severity": error["severity"],
                        "match_type": "pattern",
                        "pattern": pattern,
                        "file": str(file_path)
                    })
    
    return matches

def run_precheck(
    repo_root: Path,
    files: List[Path] = None
) -> Dict[str, Any]:
    """Run precheck against known errors."""
    timestamp = datetime.now().isoformat()
    errors = load_known_errors(repo_root)
    
    if not files:
        # Default: check recently modified files or key files
        files = [
            repo_root / "SANCTUM" / "sanctum_v0_29_qt.py",
            repo_root / "scripts" / "verify_repo.py"
        ]
        files = [f for f in files if f.exists()]
    
    all_matches = []
    for file_path in files:
        matches = check_file_for_patterns(file_path, errors)
        all_matches.extend(matches)
    
    # Deduplicate
    seen = set()
    unique_matches = []
    for m in all_matches:
        key = (m["error_id"], m["file"])
        if key not in seen:
            seen.add(key)
            unique_matches.append(m)
    
    has_blocking = any(m["severity"] == "CRITICAL" for m in unique_matches)
    
    report = {
        "timestamp": timestamp,
        "repo_root": str(repo_root),
        "files_checked": [str(f) for f in files],
        "known_errors_loaded": len(errors),
        "matches": unique_matches,
        "summary": {
            "total_matches": len(unique_matches),
            "by_severity": {
                "CRITICAL": sum(1 for m in unique_matches if m["severity"] == "CRITICAL"),
                "HIGH": sum(1 for m in unique_matches if m["severity"] == "HIGH"),
                "MEDIUM": sum(1 for m in unique_matches if m["severity"] == "MEDIUM"),
                "LOW": sum(1 for m in unique_matches if m["severity"] == "LOW")
            }
        },
        "has_blocking": has_blocking,
        "verdict": "BLOCK" if has_blocking else ("WARN" if unique_matches else "PASS")
    }
    
    return report

def main():
    import argparse
    parser = argparse.ArgumentParser(description="Check for known error patterns")
    parser.add_argument("--repo-root", type=Path, help="Repository root path")
    parser.add_argument("--files", nargs="*", type=Path, help="Files to check")
    args = parser.parse_args()
    
    repo_root = args.repo_root or find_repo_root()
    files = args.files
    
    print("=" * 60)
    print("ADMINISTRATUM ERROR PRECHECK")
    print("=" * 60)
    print(f"Repo root: {repo_root}")
    
    report = run_precheck(repo_root, files)
    
    print(f"\nKnown errors loaded: {report['known_errors_loaded']}")
    print(f"Files checked: {len(report['files_checked'])}")
    print(f"\nMatches found: {report['summary']['total_matches']}")
    
    if report["matches"]:
        print("\nWarnings:")
        for m in report["matches"]:
            print(f"  [{m['severity']}] {m['error_id']}: {m['title']}")
            print(f"           File: {m['file']}")
    
    print(f"\nVerdict: {report['verdict']}")
    
    if report["verdict"] == "PASS":
        print("\n[PASS] No known error patterns detected")
        sys.exit(0)
    elif report["verdict"] == "WARN":
        print("\n[WARN] Known error patterns detected - proceed with caution")
        sys.exit(1)
    else:
        print("\n[BLOCK] Critical error pattern detected - do not proceed")
        sys.exit(2)

if __name__ == "__main__":
    main()
