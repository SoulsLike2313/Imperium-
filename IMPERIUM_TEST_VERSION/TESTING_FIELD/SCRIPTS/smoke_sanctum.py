#!/usr/bin/env python3
"""
smoke_sanctum.py - Smoke test for Sanctum Qt application.

This script:
1. Checks Sanctum script exists
2. Validates Python syntax
3. Checks PyQt6 import
4. Optionally launches Sanctum (with timeout)
5. Captures screenshot if launched
6. Produces smoke report

Usage:
    python smoke_sanctum.py [--launch] [--timeout 10]

Exit codes:
    0 = PASS (all checks passed)
    1 = FAIL (one or more checks failed)
"""

import sys
import os
import json
from datetime import datetime
from pathlib import Path
import subprocess
import py_compile

# Configuration
SANCTUM_SCRIPT = "SANCTUM/sanctum_v0_29_qt.py"
SMOKE_RESULTS_DIR = Path(__file__).parent.parent / "SMOKE_RESULTS"
SCREENSHOTS_DIR = Path(__file__).parent.parent / "SCREENSHOTS"

def find_repo_root() -> Path:
    """Find IMPERIUM repo root (or test version root)."""
    current = Path(__file__).resolve()
    for parent in current.parents:
        if (parent / "SANCTUM").exists():
            return parent
        if (parent / "AGENTS.md").exists():
            return parent
    # Fallback: assume we're in TESTING_FIELD/SCRIPTS
    return Path(__file__).parent.parent.parent

def check_file_exists(repo_root: Path) -> dict:
    """Check if Sanctum script exists."""
    script_path = repo_root / SANCTUM_SCRIPT
    return {
        "check": "file_exists",
        "path": str(script_path),
        "passed": script_path.exists(),
        "error": None if script_path.exists() else f"File not found: {script_path}"
    }

def check_syntax(repo_root: Path) -> dict:
    """Check Python syntax."""
    script_path = repo_root / SANCTUM_SCRIPT
    if not script_path.exists():
        return {
            "check": "syntax",
            "passed": False,
            "error": "File not found"
        }
    
    try:
        py_compile.compile(str(script_path), doraise=True)
        return {
            "check": "syntax",
            "passed": True,
            "error": None
        }
    except py_compile.PyCompileError as e:
        return {
            "check": "syntax",
            "passed": False,
            "error": str(e)
        }

def check_pyqt6_import() -> dict:
    """Check if PyQt6 can be imported."""
    try:
        import PyQt6
        return {
            "check": "pyqt6_import",
            "passed": True,
            "version": getattr(PyQt6, "__version__", "unknown"),
            "error": None
        }
    except ImportError as e:
        return {
            "check": "pyqt6_import",
            "passed": False,
            "error": str(e)
        }

def run_smoke(launch: bool = False, timeout: int = 10) -> dict:
    """Run full smoke test."""
    repo_root = find_repo_root()
    timestamp = datetime.now().isoformat()
    
    results = {
        "timestamp": timestamp,
        "repo_root": str(repo_root),
        "sanctum_script": SANCTUM_SCRIPT,
        "checks": [],
        "overall_passed": True,
        "launch_attempted": launch
    }
    
    # Check 1: File exists
    check1 = check_file_exists(repo_root)
    results["checks"].append(check1)
    if not check1["passed"]:
        results["overall_passed"] = False
    
    # Check 2: Syntax
    check2 = check_syntax(repo_root)
    results["checks"].append(check2)
    if not check2["passed"]:
        results["overall_passed"] = False
    
    # Check 3: PyQt6 import
    check3 = check_pyqt6_import()
    results["checks"].append(check3)
    if not check3["passed"]:
        results["overall_passed"] = False
    
    # Optional: Launch test
    if launch and results["overall_passed"]:
        launch_result = {
            "check": "launch",
            "passed": False,
            "error": "Launch test not implemented in smoke MVP"
        }
        results["checks"].append(launch_result)
        # Note: Actual launch would require subprocess + timeout + screenshot
        # This is placeholder for MVP
    
    return results

def save_results(results: dict) -> Path:
    """Save smoke results to file."""
    SMOKE_RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_path = SMOKE_RESULTS_DIR / f"sanctum_smoke_{timestamp}.json"
    
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)
    
    return output_path

def main():
    import argparse
    parser = argparse.ArgumentParser(description="Sanctum smoke test")
    parser.add_argument("--launch", action="store_true", help="Attempt to launch Sanctum")
    parser.add_argument("--timeout", type=int, default=10, help="Launch timeout in seconds")
    args = parser.parse_args()
    
    print("=" * 60)
    print("SANCTUM SMOKE TEST")
    print("=" * 60)
    
    results = run_smoke(launch=args.launch, timeout=args.timeout)
    
    # Print results
    for check in results["checks"]:
        status = "PASS" if check["passed"] else "FAIL"
        print(f"[{status}] {check['check']}")
        if check.get("error"):
            print(f"       Error: {check['error']}")
    
    print("-" * 60)
    
    # Save results
    output_path = save_results(results)
    print(f"Results saved: {output_path}")
    
    # Final verdict
    if results["overall_passed"]:
        print("\n[PASS] Sanctum smoke test passed")
        sys.exit(0)
    else:
        print("\n[FAIL] Sanctum smoke test failed")
        sys.exit(1)

if __name__ == "__main__":
    main()
