#!/usr/bin/env python3
"""
script_scanner.py - Scan repository for all scripts and compare with registry.

Outputs:
- Total scripts found
- Registered scripts
- Unregistered scripts
- Missing scripts (registered but not found)

Usage:
    python script_scanner.py [--repo-root PATH] [--output PATH]
"""

import sys
import os
import json
from pathlib import Path
from datetime import datetime

# Script extensions to scan
SCRIPT_EXTENSIONS = {".py", ".ps1", ".sh", ".bat", ".cmd"}

# Directories to skip
SKIP_DIRS = {
    ".git", "__pycache__", "node_modules", ".venv", "venv",
    "IMPERIUM_TEST_VERSION", ".imperium_runtime", "INBOX", "OUTBOX"
}

def find_repo_root() -> Path:
    """Find IMPERIUM repo root."""
    current = Path(__file__).resolve()
    for parent in current.parents:
        if (parent / "AGENTS.md").exists():
            return parent
    return Path.cwd()

def scan_scripts(repo_root: Path) -> list:
    """Scan repository for all script files."""
    scripts = []
    
    for root, dirs, files in os.walk(repo_root):
        # Skip excluded directories
        dirs[:] = [d for d in dirs if d not in SKIP_DIRS]
        
        for file in files:
            if Path(file).suffix.lower() in SCRIPT_EXTENSIONS:
                full_path = Path(root) / file
                rel_path = full_path.relative_to(repo_root)
                scripts.append({
                    "path": str(rel_path).replace("\\", "/"),
                    "name": file,
                    "extension": Path(file).suffix.lower(),
                    "size_bytes": full_path.stat().st_size
                })
    
    return scripts

def load_registry(repo_root: Path) -> dict:
    """Load script registry if exists."""
    registry_path = repo_root / "REGISTRY" / "SCRIPT_REGISTRY.json"
    if registry_path.exists():
        with open(registry_path, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"scripts": []}

def compare_with_registry(found_scripts: list, registry: dict) -> dict:
    """Compare found scripts with registry."""
    found_paths = {s["path"] for s in found_scripts}
    registered_paths = set()
    
    # Extract paths from registry
    for script in registry.get("scripts", []):
        if "path" in script:
            registered_paths.add(script["path"].replace("\\", "/"))
    
    return {
        "total_found": len(found_scripts),
        "total_registered": len(registered_paths),
        "registered_and_found": len(found_paths & registered_paths),
        "unregistered": sorted(found_paths - registered_paths),
        "missing": sorted(registered_paths - found_paths)
    }

def generate_report(repo_root: Path, output_path: Path = None) -> dict:
    """Generate full scan report."""
    timestamp = datetime.now().isoformat()
    
    found_scripts = scan_scripts(repo_root)
    registry = load_registry(repo_root)
    comparison = compare_with_registry(found_scripts, registry)
    
    report = {
        "timestamp": timestamp,
        "repo_root": str(repo_root),
        "scan_result": {
            "total_scripts_found": len(found_scripts),
            "by_extension": {},
            "scripts": found_scripts
        },
        "registry_comparison": comparison,
        "health": {
            "unregistered_count": len(comparison["unregistered"]),
            "missing_count": len(comparison["missing"]),
            "passed": len(comparison["missing"]) == 0
        }
    }
    
    # Count by extension
    for script in found_scripts:
        ext = script["extension"]
        report["scan_result"]["by_extension"][ext] = \
            report["scan_result"]["by_extension"].get(ext, 0) + 1
    
    # Save report
    if output_path:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2)
    
    return report

def main():
    import argparse
    parser = argparse.ArgumentParser(description="Scan scripts in repository")
    parser.add_argument("--repo-root", type=Path, help="Repository root path")
    parser.add_argument("--output", type=Path, help="Output report path")
    args = parser.parse_args()
    
    repo_root = args.repo_root or find_repo_root()
    output_path = args.output
    
    if not output_path:
        # Default output in MECHANICUS reports
        output_dir = repo_root / "ORGANS" / "MECHANICUS" / "REPORTS"
        output_dir.mkdir(parents=True, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_path = output_dir / f"script_scan_{timestamp}.json"
    
    print("=" * 60)
    print("MECHANICUS SCRIPT SCANNER")
    print("=" * 60)
    print(f"Repo root: {repo_root}")
    
    report = generate_report(repo_root, output_path)
    
    print(f"\nTotal scripts found: {report['scan_result']['total_scripts_found']}")
    print(f"By extension: {report['scan_result']['by_extension']}")
    print(f"\nRegistry comparison:")
    print(f"  Registered: {report['registry_comparison']['total_registered']}")
    print(f"  Unregistered: {report['registry_comparison']['unregistered'][:5]}..." 
          if len(report['registry_comparison']['unregistered']) > 5 
          else f"  Unregistered: {report['registry_comparison']['unregistered']}")
    print(f"  Missing: {report['registry_comparison']['missing']}")
    
    print(f"\nReport saved: {output_path}")
    
    if report["health"]["passed"]:
        print("\n[PASS] No missing registered scripts")
        sys.exit(0)
    else:
        print(f"\n[FAIL] {report['health']['missing_count']} registered scripts missing")
        sys.exit(1)

if __name__ == "__main__":
    main()
