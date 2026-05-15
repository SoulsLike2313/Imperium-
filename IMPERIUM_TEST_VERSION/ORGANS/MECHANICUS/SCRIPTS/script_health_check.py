#!/usr/bin/env python3
"""
script_health_check.py - Check health of all scripts (existence + syntax).

Checks:
1. File exists at declared path
2. Python syntax valid (for .py files)
3. PowerShell syntax valid (for .ps1 files) - basic check

Usage:
    python script_health_check.py [--repo-root PATH] [--output PATH]

Exit codes:
    0 = All scripts healthy
    1 = One or more scripts unhealthy
"""

import sys
import os
import json
import py_compile
import subprocess
from pathlib import Path
from datetime import datetime

def find_repo_root() -> Path:
    """Find IMPERIUM repo root."""
    current = Path(__file__).resolve()
    for parent in current.parents:
        if (parent / "AGENTS.md").exists():
            return parent
    return Path.cwd()

def check_python_syntax(script_path: Path) -> dict:
    """Check Python script syntax."""
    try:
        py_compile.compile(str(script_path), doraise=True)
        return {"passed": True, "error": None}
    except py_compile.PyCompileError as e:
        return {"passed": False, "error": str(e)}
    except Exception as e:
        return {"passed": False, "error": f"Unexpected error: {e}"}

def check_powershell_syntax(script_path: Path) -> dict:
    """Check PowerShell script syntax (basic)."""
    try:
        # Use PowerShell to parse the script
        result = subprocess.run(
            ["powershell", "-NoProfile", "-Command", 
             f"$null = [System.Management.Automation.Language.Parser]::ParseFile('{script_path}', [ref]$null, [ref]$errors); $errors.Count"],
            capture_output=True,
            text=True,
            timeout=10
        )
        error_count = int(result.stdout.strip()) if result.stdout.strip().isdigit() else -1
        if error_count == 0:
            return {"passed": True, "error": None}
        else:
            return {"passed": False, "error": f"PowerShell parse errors: {error_count}"}
    except subprocess.TimeoutExpired:
        return {"passed": False, "error": "Syntax check timed out"}
    except Exception as e:
        return {"passed": False, "error": f"Cannot check PowerShell syntax: {e}"}

def check_script_health(script_path: Path, repo_root: Path) -> dict:
    """Check single script health."""
    full_path = repo_root / script_path if not script_path.is_absolute() else script_path
    
    result = {
        "path": str(script_path),
        "exists": full_path.exists(),
        "syntax_checked": False,
        "syntax_passed": None,
        "syntax_error": None,
        "healthy": False
    }
    
    if not result["exists"]:
        result["syntax_error"] = "File not found"
        return result
    
    ext = full_path.suffix.lower()
    
    if ext == ".py":
        syntax_result = check_python_syntax(full_path)
        result["syntax_checked"] = True
        result["syntax_passed"] = syntax_result["passed"]
        result["syntax_error"] = syntax_result["error"]
    elif ext == ".ps1":
        syntax_result = check_powershell_syntax(full_path)
        result["syntax_checked"] = True
        result["syntax_passed"] = syntax_result["passed"]
        result["syntax_error"] = syntax_result["error"]
    else:
        # For other scripts, just check existence
        result["syntax_checked"] = False
        result["syntax_passed"] = None
    
    # Healthy = exists AND (syntax not checked OR syntax passed)
    result["healthy"] = result["exists"] and (
        not result["syntax_checked"] or result["syntax_passed"]
    )
    
    return result

def load_script_list(repo_root: Path) -> list:
    """Load list of scripts to check from registry or scan."""
    registry_path = repo_root / "REGISTRY" / "SCRIPT_REGISTRY.json"
    
    if registry_path.exists():
        with open(registry_path, "r", encoding="utf-8") as f:
            registry = json.load(f)
            return [s.get("path") for s in registry.get("scripts", []) if s.get("path")]
    
    # Fallback: scan for scripts
    scripts = []
    for ext in [".py", ".ps1", ".sh"]:
        for path in repo_root.rglob(f"*{ext}"):
            if ".git" not in str(path) and "__pycache__" not in str(path):
                scripts.append(str(path.relative_to(repo_root)))
    return scripts[:50]  # Limit for MVP

def generate_health_report(repo_root: Path, output_path: Path = None) -> dict:
    """Generate script health report."""
    timestamp = datetime.now().isoformat()
    script_list = load_script_list(repo_root)
    
    results = []
    for script_path in script_list:
        result = check_script_health(Path(script_path), repo_root)
        results.append(result)
    
    # Aggregate stats
    total = len(results)
    exists_count = sum(1 for r in results if r["exists"])
    healthy_count = sum(1 for r in results if r["healthy"])
    syntax_checked = sum(1 for r in results if r["syntax_checked"])
    syntax_passed = sum(1 for r in results if r["syntax_passed"])
    
    report = {
        "timestamp": timestamp,
        "repo_root": str(repo_root),
        "summary": {
            "total_scripts": total,
            "exists": exists_count,
            "missing": total - exists_count,
            "syntax_checked": syntax_checked,
            "syntax_passed": syntax_passed,
            "syntax_failed": syntax_checked - syntax_passed,
            "healthy": healthy_count,
            "unhealthy": total - healthy_count,
            "health_percent": round(healthy_count / total * 100, 1) if total > 0 else 0
        },
        "scripts": results,
        "unhealthy_scripts": [r for r in results if not r["healthy"]],
        "overall_passed": healthy_count == total
    }
    
    if output_path:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2)
    
    return report

def main():
    import argparse
    parser = argparse.ArgumentParser(description="Check script health")
    parser.add_argument("--repo-root", type=Path, help="Repository root path")
    parser.add_argument("--output", type=Path, help="Output report path")
    args = parser.parse_args()
    
    repo_root = args.repo_root or find_repo_root()
    output_path = args.output
    
    if not output_path:
        output_dir = repo_root / "ORGANS" / "MECHANICUS" / "REPORTS"
        output_dir.mkdir(parents=True, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_path = output_dir / f"script_health_{timestamp}.json"
    
    print("=" * 60)
    print("MECHANICUS SCRIPT HEALTH CHECK")
    print("=" * 60)
    print(f"Repo root: {repo_root}")
    
    report = generate_health_report(repo_root, output_path)
    
    print(f"\nSummary:")
    print(f"  Total scripts: {report['summary']['total_scripts']}")
    print(f"  Exists: {report['summary']['exists']}")
    print(f"  Missing: {report['summary']['missing']}")
    print(f"  Syntax checked: {report['summary']['syntax_checked']}")
    print(f"  Syntax passed: {report['summary']['syntax_passed']}")
    print(f"  Healthy: {report['summary']['healthy']}")
    print(f"  Health %: {report['summary']['health_percent']}%")
    
    if report["unhealthy_scripts"]:
        print(f"\nUnhealthy scripts:")
        for s in report["unhealthy_scripts"][:10]:
            print(f"  - {s['path']}: {s.get('syntax_error', 'missing')}")
    
    print(f"\nReport saved: {output_path}")
    
    if report["overall_passed"]:
        print("\n[PASS] All scripts healthy")
        sys.exit(0)
    else:
        print(f"\n[FAIL] {report['summary']['unhealthy']} unhealthy scripts")
        sys.exit(1)

if __name__ == "__main__":
    main()
