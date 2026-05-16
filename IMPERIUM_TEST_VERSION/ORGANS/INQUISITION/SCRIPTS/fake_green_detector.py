#!/usr/bin/env python3
"""
fake_green_detector.py - Detect PASS verdicts without proper evidence.

Fake Green = claiming PASS/success without:
- Evidence file
- Test result
- Screenshot (for UI)
- Receipt

Usage:
    python fake_green_detector.py [--repo-root PATH] [--output PATH]

Exit codes:
    0 = No fake green detected
    1 = Fake green detected
"""

import sys
import os
import json
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any

def find_repo_root() -> Path:
    """Find IMPERIUM_TEST_VERSION root (not main repo)."""
    current = Path(__file__).resolve()
    for parent in current.parents:
        if parent.name == "IMPERIUM_TEST_VERSION":
            return parent
    # Fallback to script's test version root
    return Path(__file__).resolve().parent.parent.parent.parent

def scan_verdict_files(repo_root: Path) -> List[Dict[str, Any]]:
    """Scan for verdict/status files."""
    verdict_files = []
    
    # Patterns to look for
    patterns = [
        "**/VERDICT*.json",
        "**/VERDICT*.md",
        "**/STATUS*.json",
        "**/*_REPORT.json",
        "**/*_result*.json"
    ]
    
    for pattern in patterns:
        for path in repo_root.glob(pattern):
            if ".git" in str(path) or "__pycache__" in str(path):
                continue
            if "IMPERIUM_TEST_VERSION" in str(path):
                continue
            verdict_files.append({
                "path": str(path.relative_to(repo_root)),
                "full_path": path
            })
    
    return verdict_files

def check_verdict_for_fake_green(verdict_file: Dict[str, Any]) -> Dict[str, Any]:
    """Check single verdict file for fake green."""
    result = {
        "path": verdict_file["path"],
        "is_fake_green": False,
        "reason": None,
        "verdict_found": None,
        "evidence_found": False
    }
    
    path = verdict_file["full_path"]
    
    try:
        if path.suffix == ".json":
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
            
            # Look for PASS/success claims
            verdict = None
            for key in ["verdict", "status", "result", "overall_passed", "passed"]:
                if key in data:
                    verdict = data[key]
                    break
            
            result["verdict_found"] = verdict
            
            # Check if claiming PASS
            is_pass = False
            if isinstance(verdict, bool):
                is_pass = verdict
            elif isinstance(verdict, str):
                is_pass = verdict.upper() in ["PASS", "SUCCESS", "OK", "GREEN"]
            
            if is_pass:
                # Look for evidence
                evidence_keys = ["evidence", "evidence_path", "report_path", 
                               "screenshot", "receipt", "proof", "test_result"]
                has_evidence = any(
                    key in data and data[key] 
                    for key in evidence_keys
                )
                
                result["evidence_found"] = has_evidence
                
                if not has_evidence:
                    result["is_fake_green"] = True
                    result["reason"] = "PASS verdict without evidence reference"
        
        elif path.suffix == ".md":
            content = path.read_text(encoding="utf-8")
            
            # Simple check for PASS without evidence
            has_pass = "PASS" in content.upper() or "✅" in content
            has_evidence = "evidence" in content.lower() or "screenshot" in content.lower()
            
            if has_pass:
                result["verdict_found"] = "PASS (in markdown)"
                result["evidence_found"] = has_evidence
                
                if not has_evidence:
                    result["is_fake_green"] = True
                    result["reason"] = "PASS claim in markdown without evidence mention"
    
    except Exception as e:
        result["error"] = str(e)
    
    return result

def generate_report(repo_root: Path, output_path: Path = None) -> Dict[str, Any]:
    """Generate fake green detection report."""
    timestamp = datetime.now().isoformat()
    
    verdict_files = scan_verdict_files(repo_root)
    results = []
    
    for vf in verdict_files:
        result = check_verdict_for_fake_green(vf)
        results.append(result)
    
    fake_greens = [r for r in results if r["is_fake_green"]]
    
    report = {
        "timestamp": timestamp,
        "repo_root": str(repo_root),
        "summary": {
            "total_verdict_files": len(verdict_files),
            "checked": len(results),
            "fake_green_count": len(fake_greens),
            "clean_count": len(results) - len(fake_greens)
        },
        "fake_greens": fake_greens,
        "all_results": results,
        "overall_passed": len(fake_greens) == 0
    }
    
    if output_path:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2)
    
    return report

def main():
    import argparse
    parser = argparse.ArgumentParser(description="Detect fake green verdicts")
    parser.add_argument("--repo-root", type=Path, help="Repository root path")
    parser.add_argument("--output", type=Path, help="Output report path")
    args = parser.parse_args()
    
    repo_root = args.repo_root or find_repo_root()
    output_path = args.output
    
    if not output_path:
        output_dir = repo_root / "ORGANS" / "INQUISITION" / "REPORTS"
        output_dir.mkdir(parents=True, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_path = output_dir / f"fake_green_audit_{timestamp}.json"
    
    print("=" * 60)
    print("INQUISITION FAKE GREEN DETECTOR")
    print("=" * 60)
    print(f"Repo root: {repo_root}")
    
    report = generate_report(repo_root, output_path)
    
    print(f"\nSummary:")
    print(f"  Verdict files scanned: {report['summary']['total_verdict_files']}")
    print(f"  Fake green detected: {report['summary']['fake_green_count']}")
    print(f"  Clean: {report['summary']['clean_count']}")
    
    if report["fake_greens"]:
        print(f"\nFake greens found:")
        for fg in report["fake_greens"][:10]:
            print(f"  - {fg['path']}: {fg['reason']}")
    
    print(f"\nReport saved: {output_path}")
    
    if report["overall_passed"]:
        print("\n[PASS] No fake green detected")
        sys.exit(0)
    else:
        print(f"\n[FAIL] {report['summary']['fake_green_count']} fake green(s) detected")
        sys.exit(1)

if __name__ == "__main__":
    main()
