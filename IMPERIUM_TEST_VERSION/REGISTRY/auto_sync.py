#!/usr/bin/env python3
"""
AUTO SYNC
Automated registry synchronization and health check.

Combines registry_sync and drift_detector into a single automated workflow.

Usage:
    py -3 auto_sync.py                    # Full check and report
    py -3 auto_sync.py --fix              # Auto-fix detected issues
    py -3 auto_sync.py --output report.json
"""

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

# Import sibling modules
sys.path.insert(0, str(Path(__file__).parent))
import registry_sync
import drift_detector


def get_test_version_root():
    """Get the test version root directory."""
    return Path(__file__).parent.parent


def run_full_check():
    """Run full registry and drift check."""
    results = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "checks": [],
        "actions_taken": [],
        "recommendations": []
    }
    
    # 1. Registry sync check
    print("=" * 60)
    print("AUTO SYNC - REGISTRY CHECK")
    print("=" * 60)
    print()
    
    actual_organs = registry_sync.scan_organs()
    registered = registry_sync.load_organ_registry()
    
    if registered:
        drift = registry_sync.compare_registries(actual_organs, registered)
        has_drift = any(drift[k] for k in drift)
        
        results["checks"].append({
            "check": "registry_sync",
            "status": "PASS" if not has_drift else "DRIFT",
            "drift": drift
        })
        
        if has_drift:
            results["recommendations"].append({
                "issue": "Registry drift detected",
                "action": "Run: py -3 registry_sync.py --sync"
            })
    else:
        results["checks"].append({
            "check": "registry_sync",
            "status": "NO_REGISTRY"
        })
        results["recommendations"].append({
            "issue": "No registry found",
            "action": "Run: py -3 registry_sync.py --sync"
        })
    
    # 2. Drift detection
    drift_results = drift_detector.detect_drift()
    results["checks"].extend(drift_results["checks"])
    
    # 3. Organ health check
    organ_health = []
    for organ in actual_organs:
        health = {
            "organ_id": organ["organ_id"],
            "status": organ.get("status", "UNKNOWN"),
            "has_contract": organ.get("has_contract", False),
            "has_readme": organ.get("has_readme", False),
            "has_scripts": organ.get("has_scripts", False),
            "health": "GOOD"
        }
        
        if not health["has_contract"]:
            health["health"] = "PARTIAL"
            results["recommendations"].append({
                "issue": f"{organ['organ_id']} missing contract",
                "action": f"Create ORGANS/{organ['organ_id']}/ORGAN_CONTRACT.json"
            })
        
        organ_health.append(health)
    
    results["checks"].append({
        "check": "organ_health",
        "organs": organ_health,
        "total": len(organ_health),
        "healthy": sum(1 for o in organ_health if o["health"] == "GOOD"),
        "status": "PASS" if all(o["health"] == "GOOD" for o in organ_health) else "PARTIAL"
    })
    
    # Overall verdict
    statuses = [c["status"] for c in results["checks"]]
    if "FAIL" in statuses or "NO_REGISTRY" in statuses:
        results["verdict"] = "FAIL"
    elif "DRIFT" in statuses or "PARTIAL" in statuses:
        results["verdict"] = "PARTIAL"
    else:
        results["verdict"] = "PASS"
    
    return results


def auto_fix(results):
    """Auto-fix detected issues."""
    actions = []
    
    # Fix registry drift
    for check in results["checks"]:
        if check.get("check") == "registry_sync" and check.get("status") == "DRIFT":
            print("Fixing: Registry drift...")
            actual_organs = registry_sync.scan_organs()
            new_registry = registry_sync.generate_registry(actual_organs)
            
            # Update status summary
            status_counts = {}
            for o in new_registry["organs"]:
                status = o.get("status", "UNKNOWN")
                if status not in status_counts:
                    status_counts[status] = []
                status_counts[status].append(o["organ_id"])
            new_registry["status_summary"] = status_counts
            
            registry_path = get_test_version_root() / "REGISTRY" / "ORGAN_REGISTRY.json"
            with open(registry_path, "w", encoding="utf-8") as f:
                json.dump(new_registry, f, indent=2)
            
            actions.append(f"Synced registry: {registry_path}")
    
    return actions


def main():
    parser = argparse.ArgumentParser(description="Automated registry sync and health check")
    parser.add_argument("--fix", action="store_true", help="Auto-fix detected issues")
    parser.add_argument("--output", help="Output file for report")
    args = parser.parse_args()
    
    results = run_full_check()
    
    print()
    print("SUMMARY:")
    print("-" * 40)
    
    for check in results["checks"]:
        icon = {"PASS": "✅", "PARTIAL": "⚠️", "FAIL": "❌", "DRIFT": "🔄", "NO_REGISTRY": "❓"}.get(check["status"], "❓")
        print(f"  {icon} {check['check']}: {check['status']}")
    
    print()
    
    if results["recommendations"]:
        print("RECOMMENDATIONS:")
        for rec in results["recommendations"]:
            print(f"  - {rec['issue']}")
            print(f"    Action: {rec['action']}")
        print()
    
    if args.fix:
        print("AUTO-FIX:")
        actions = auto_fix(results)
        results["actions_taken"] = actions
        for action in actions:
            print(f"  ✅ {action}")
        if not actions:
            print("  No auto-fixable issues found")
        print()
    
    print(f"VERDICT: {results['verdict']}")
    
    if args.output:
        output_path = Path(args.output)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(results, f, indent=2)
        print(f"Report: {args.output}")
    
    sys.exit(0 if results["verdict"] == "PASS" else 1)


if __name__ == "__main__":
    main()
