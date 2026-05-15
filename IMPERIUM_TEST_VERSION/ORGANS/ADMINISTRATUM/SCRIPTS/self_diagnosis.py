#!/usr/bin/env python3
"""
self_diagnosis.py - System self-diagnosis: what hurts, what is broken, what needs attention.

Analyzes the system and identifies:
- Bottlenecks
- Broken components
- Missing dependencies
- Stale data
- Known issues
- Recommended actions

Usage:
    python self_diagnosis.py [--repo-root PATH] [--output PATH]
"""

import sys
import os
import json
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, Any, List
import subprocess

def find_repo_root() -> Path:
    """Find IMPERIUM repo root."""
    current = Path(__file__).resolve()
    for parent in current.parents:
        if (parent / "AGENTS.md").exists():
            return parent
    return Path.cwd()

def check_git_health(repo_root: Path) -> Dict[str, Any]:
    """Check git repository health."""
    issues = []
    
    try:
        # Check if clean
        result = subprocess.run(
            ["git", "status", "--short"],
            cwd=str(repo_root), capture_output=True, text=True
        )
        if result.returncode == 0 and result.stdout.strip():
            issues.append({
                "type": "dirty_worktree",
                "severity": "MEDIUM",
                "description": "Working directory has uncommitted changes",
                "recommendation": "Review and commit or stash changes"
            })
        
        # Check if ahead/behind origin
        result = subprocess.run(
            ["git", "status", "-sb"],
            cwd=str(repo_root), capture_output=True, text=True
        )
        if result.returncode == 0:
            status = result.stdout
            if "ahead" in status:
                issues.append({
                    "type": "unpushed_commits",
                    "severity": "LOW",
                    "description": "Local commits not pushed to origin",
                    "recommendation": "Push commits when ready"
                })
            if "behind" in status:
                issues.append({
                    "type": "behind_origin",
                    "severity": "MEDIUM",
                    "description": "Local branch is behind origin",
                    "recommendation": "Pull latest changes"
                })
    except:
        issues.append({
            "type": "git_error",
            "severity": "HIGH",
            "description": "Cannot check git status",
            "recommendation": "Verify git is installed and repo is valid"
        })
    
    return {
        "component": "git",
        "issues": issues,
        "healthy": len(issues) == 0
    }

def check_organ_health(repo_root: Path) -> Dict[str, Any]:
    """Check organ health."""
    issues = []
    organs_dir = repo_root / "ORGANS"
    
    if not organs_dir.exists():
        issues.append({
            "type": "missing_organs_dir",
            "severity": "CRITICAL",
            "description": "ORGANS directory not found",
            "recommendation": "Create ORGANS directory structure"
        })
        return {"component": "organs", "issues": issues, "healthy": False}
    
    # Check each organ
    for organ_dir in organs_dir.iterdir():
        if not organ_dir.is_dir():
            continue
        
        organ_name = organ_dir.name
        
        # Check for contract
        if not (organ_dir / "ORGAN_CONTRACT.json").exists():
            issues.append({
                "type": "missing_contract",
                "severity": "MEDIUM",
                "organ": organ_name,
                "description": f"Organ {organ_name} has no ORGAN_CONTRACT.json",
                "recommendation": f"Create contract for {organ_name}"
            })
        
        # Check for README
        if not (organ_dir / "README.md").exists():
            issues.append({
                "type": "missing_readme",
                "severity": "LOW",
                "organ": organ_name,
                "description": f"Organ {organ_name} has no README.md",
                "recommendation": f"Document {organ_name}"
            })
    
    return {
        "component": "organs",
        "issues": issues,
        "healthy": len([i for i in issues if i["severity"] in ["CRITICAL", "HIGH"]]) == 0
    }

def check_registry_health(repo_root: Path) -> Dict[str, Any]:
    """Check registry health."""
    issues = []
    registry_dir = repo_root / "REGISTRY"
    
    if not registry_dir.exists():
        issues.append({
            "type": "missing_registry_dir",
            "severity": "HIGH",
            "description": "REGISTRY directory not found",
            "recommendation": "Create REGISTRY directory"
        })
        return {"component": "registry", "issues": issues, "healthy": False}
    
    # Check script registry
    script_reg = registry_dir / "SCRIPT_REGISTRY.json"
    if script_reg.exists():
        try:
            with open(script_reg, "r", encoding="utf-8") as f:
                data = json.load(f)
                scripts = data.get("scripts", [])
                
                # Check for missing scripts
                for script in scripts:
                    script_path = repo_root / script.get("path", "")
                    if not script_path.exists():
                        issues.append({
                            "type": "missing_registered_script",
                            "severity": "HIGH",
                            "script": script.get("path"),
                            "description": f"Registered script not found: {script.get('path')}",
                            "recommendation": "Remove from registry or restore script"
                        })
        except json.JSONDecodeError:
            issues.append({
                "type": "invalid_registry",
                "severity": "HIGH",
                "registry": "SCRIPT_REGISTRY.json",
                "description": "Script registry has invalid JSON",
                "recommendation": "Fix JSON syntax"
            })
    
    return {
        "component": "registry",
        "issues": issues,
        "healthy": len([i for i in issues if i["severity"] in ["CRITICAL", "HIGH"]]) == 0
    }

def check_entrypoint_health(repo_root: Path) -> Dict[str, Any]:
    """Check entrypoint health."""
    issues = []
    
    entrypoints = [
        ("SANCTUM/sanctum_v0_29_qt.py", "Sanctum main UI"),
        ("scripts/verify_repo.py", "Repository verification"),
        ("TOOLS/RUN_ADMINISTRATUM_GIT_CLI_CHECK.ps1", "Git CLI check")
    ]
    
    for path, name in entrypoints:
        full_path = repo_root / path
        if not full_path.exists():
            issues.append({
                "type": "missing_entrypoint",
                "severity": "HIGH",
                "path": path,
                "description": f"Entrypoint not found: {name}",
                "recommendation": f"Restore or update path for {name}"
            })
    
    return {
        "component": "entrypoints",
        "issues": issues,
        "healthy": len(issues) == 0
    }

def check_known_debt(repo_root: Path) -> Dict[str, Any]:
    """Check known technical debt."""
    issues = []
    
    # Known debt items from AGENTS.md
    known_debt = [
        {
            "type": "warning_flood",
            "severity": "MEDIUM",
            "description": "Warning flood from legacy/continuity packs creates noisy PASS_WITH_WARNINGS",
            "recommendation": "Clean up continuity packs or exclude from scan"
        },
        {
            "type": "raw_subprocess",
            "severity": "HIGH",
            "description": "Sanctum raw subprocess usage is not yet migrated to command gateway",
            "recommendation": "Migrate to command gateway"
        },
        {
            "type": "registry_drift",
            "severity": "MEDIUM",
            "description": "Registry drift between declared state and real active files",
            "recommendation": "Sync registries with actual files"
        }
    ]
    
    issues.extend(known_debt)
    
    return {
        "component": "known_debt",
        "issues": issues,
        "healthy": False  # Known debt exists
    }

def identify_bottlenecks(all_checks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Identify top bottlenecks from all checks."""
    bottlenecks = []
    
    # Collect all high/critical issues
    for check in all_checks:
        for issue in check.get("issues", []):
            if issue["severity"] in ["CRITICAL", "HIGH"]:
                bottlenecks.append({
                    "component": check["component"],
                    "issue": issue["type"],
                    "severity": issue["severity"],
                    "description": issue["description"],
                    "recommendation": issue["recommendation"]
                })
    
    # Sort by severity
    severity_order = {"CRITICAL": 0, "HIGH": 1, "MEDIUM": 2, "LOW": 3}
    bottlenecks.sort(key=lambda x: severity_order.get(x["severity"], 99))
    
    return bottlenecks[:10]  # Top 10

def generate_diagnosis(repo_root: Path, output_path: Path = None) -> Dict[str, Any]:
    """Generate full system diagnosis."""
    timestamp = datetime.now().isoformat()
    
    checks = [
        check_git_health(repo_root),
        check_organ_health(repo_root),
        check_registry_health(repo_root),
        check_entrypoint_health(repo_root),
        check_known_debt(repo_root)
    ]
    
    total_issues = sum(len(c["issues"]) for c in checks)
    critical_count = sum(1 for c in checks for i in c["issues"] if i["severity"] == "CRITICAL")
    high_count = sum(1 for c in checks for i in c["issues"] if i["severity"] == "HIGH")
    
    bottlenecks = identify_bottlenecks(checks)
    
    diagnosis = {
        "schema_version": "IMPERIUM_SELF_DIAGNOSIS_V0_1",
        "generated_at": timestamp,
        "repo_root": str(repo_root),
        "summary": {
            "total_issues": total_issues,
            "critical": critical_count,
            "high": high_count,
            "components_checked": len(checks),
            "healthy_components": sum(1 for c in checks if c["healthy"]),
            "overall_health": "CRITICAL" if critical_count > 0 else ("DEGRADED" if high_count > 0 else "HEALTHY")
        },
        "checks": checks,
        "top_bottlenecks": bottlenecks,
        "recommended_actions": [b["recommendation"] for b in bottlenecks[:5]]
    }
    
    if output_path:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(diagnosis, f, indent=2, ensure_ascii=False)
    
    return diagnosis

def main():
    import argparse
    parser = argparse.ArgumentParser(description="Generate system self-diagnosis")
    parser.add_argument("--repo-root", type=Path, help="Repository root path")
    parser.add_argument("--output", type=Path, help="Output path")
    args = parser.parse_args()
    
    repo_root = args.repo_root or find_repo_root()
    output_path = args.output
    
    if not output_path:
        output_dir = repo_root / "ORGANS" / "ADMINISTRATUM" / "REPORTS"
        output_dir.mkdir(parents=True, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_path = output_dir / f"self_diagnosis_{timestamp}.json"
    
    print("=" * 60)
    print("ADMINISTRATUM SELF-DIAGNOSIS")
    print("=" * 60)
    print(f"Repo root: {repo_root}")
    
    diagnosis = generate_diagnosis(repo_root, output_path)
    
    print(f"\nOverall Health: {diagnosis['summary']['overall_health']}")
    print(f"Total Issues: {diagnosis['summary']['total_issues']}")
    print(f"  Critical: {diagnosis['summary']['critical']}")
    print(f"  High: {diagnosis['summary']['high']}")
    
    if diagnosis["top_bottlenecks"]:
        print(f"\nTop Bottlenecks:")
        for i, b in enumerate(diagnosis["top_bottlenecks"][:5], 1):
            print(f"  {i}. [{b['severity']}] {b['component']}: {b['issue']}")
    
    if diagnosis["recommended_actions"]:
        print(f"\nRecommended Actions:")
        for i, action in enumerate(diagnosis["recommended_actions"], 1):
            print(f"  {i}. {action}")
    
    print(f"\nDiagnosis saved: {output_path}")
    
    if diagnosis["summary"]["overall_health"] == "HEALTHY":
        sys.exit(0)
    else:
        sys.exit(1)

if __name__ == "__main__":
    main()
