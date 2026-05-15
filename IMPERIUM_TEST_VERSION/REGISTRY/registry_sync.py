#!/usr/bin/env python3
"""
REGISTRY SYNC
Synchronizes registries with actual file system state.

Usage:
    py -3 registry_sync.py --check          # Check for drift
    py -3 registry_sync.py --sync           # Sync registries
    py -3 registry_sync.py --output report.json
"""

import argparse
import json
import os
import sys
from pathlib import Path
from datetime import datetime, timezone


def get_test_version_root():
    """Get the test version root directory."""
    return Path(__file__).parent.parent


def scan_organs():
    """Scan actual organ directories."""
    organs_dir = get_test_version_root() / "ORGANS"
    organs = []
    
    if not organs_dir.exists():
        return organs
    
    for organ_dir in organs_dir.iterdir():
        if not organ_dir.is_dir():
            continue
        
        organ_info = {
            "organ_id": organ_dir.name,
            "path": str(organ_dir.relative_to(get_test_version_root())),
            "has_contract": (organ_dir / "ORGAN_CONTRACT.json").exists(),
            "has_readme": (organ_dir / "README.md").exists(),
            "has_scripts": (organ_dir / "SCRIPTS").exists(),
            "has_dashboard": (organ_dir / "DASHBOARD").exists(),
        }
        
        # Read contract if exists
        contract_path = organ_dir / "ORGAN_CONTRACT.json"
        if contract_path.exists():
            try:
                with open(contract_path, "r", encoding="utf-8") as f:
                    contract = json.load(f)
                organ_info["status"] = contract.get("status", "UNKNOWN")
                organ_info["organ_name"] = contract.get("organ_name") or contract.get("name")
                organ_info["purpose"] = contract.get("purpose") or contract.get("responsibility")
            except:
                organ_info["status"] = "ERROR"
        else:
            organ_info["status"] = "NO_CONTRACT"
        
        organs.append(organ_info)
    
    # Add special organs only if not already found in ORGANS/
    existing_ids = {o["organ_id"] for o in organs}
    special = [
        {"organ_id": "DOCTRINARIUM", "path": "schemas", "status": "PARTIAL"},
        {"organ_id": "SCHOLA_IMPERIALIS", "path": "SECOND_BRAIN", "status": "SEED"},
    ]
    
    for s in special:
        # Skip if already found in ORGANS/
        if s["organ_id"] in existing_ids:
            continue
            
        s_path = get_test_version_root() / s["path"]
        if s_path.exists():
            s["has_contract"] = False
            s["has_readme"] = (s_path / "README.md").exists() or (s_path / "README_RU.md").exists()
            s["has_scripts"] = (s_path / "SCRIPTS").exists()
            s["has_dashboard"] = False
            organs.append(s)
    
    return organs


def load_organ_registry():
    """Load current organ registry."""
    registry_path = get_test_version_root() / "REGISTRY" / "ORGAN_REGISTRY.json"
    
    if not registry_path.exists():
        return None
    
    try:
        with open(registry_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return None


def compare_registries(actual, registered):
    """Compare actual state with registered state."""
    drift = {
        "missing_in_registry": [],
        "missing_in_filesystem": [],
        "status_mismatch": [],
        "path_mismatch": []
    }
    
    actual_ids = {o["organ_id"] for o in actual}
    registered_ids = {o["organ_id"] for o in registered.get("organs", [])}
    
    # Missing in registry
    for organ_id in actual_ids - registered_ids:
        drift["missing_in_registry"].append(organ_id)
    
    # Missing in filesystem
    for organ_id in registered_ids - actual_ids:
        drift["missing_in_filesystem"].append(organ_id)
    
    # Compare matching organs
    actual_map = {o["organ_id"]: o for o in actual}
    registered_map = {o["organ_id"]: o for o in registered.get("organs", [])}
    
    for organ_id in actual_ids & registered_ids:
        a = actual_map[organ_id]
        r = registered_map[organ_id]
        
        if a.get("status") != r.get("status"):
            drift["status_mismatch"].append({
                "organ_id": organ_id,
                "actual": a.get("status"),
                "registered": r.get("status")
            })
    
    return drift


def generate_registry(organs):
    """Generate new registry from actual state."""
    return {
        "schema_version": "IMPERIUM_ORGAN_REGISTRY_V0_1",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "source": "registry_sync.py",
        "organs": [
            {
                "organ_id": o["organ_id"],
                "name": o.get("organ_name", o["organ_id"]),
                "status": o.get("status", "UNKNOWN"),
                "backend_path": f"ORGANS/{o['organ_id']}/" if "ORGANS" in o.get("path", "") else o.get("path"),
                "frontend_path": f"ORGANS/{o['organ_id']}/DASHBOARD/" if o.get("has_dashboard") else None,
                "support_path": f"ORGANS/{o['organ_id']}/SCRIPTS/" if o.get("has_scripts") else None,
                "contract_path": f"ORGANS/{o['organ_id']}/ORGAN_CONTRACT.json" if o.get("has_contract") else None,
                "purpose": o.get("purpose", "")
            }
            for o in organs
        ],
        "status_summary": {},
        "total_organs": len(organs)
    }


def main():
    parser = argparse.ArgumentParser(description="Sync organ registry with filesystem")
    parser.add_argument("--check", action="store_true", help="Check for drift only")
    parser.add_argument("--sync", action="store_true", help="Sync registry with filesystem")
    parser.add_argument("--output", help="Output file for report")
    args = parser.parse_args()
    
    # Scan actual state
    actual_organs = scan_organs()
    
    # Load registered state
    registered = load_organ_registry()
    
    print("=" * 60)
    print("REGISTRY SYNC")
    print("=" * 60)
    print(f"Timestamp: {datetime.now(timezone.utc).isoformat()}")
    print()
    
    print("ACTUAL ORGANS:")
    for o in sorted(actual_organs, key=lambda x: x["organ_id"]):
        status = o.get("status", "?")
        print(f"  - {o['organ_id']}: {status}")
    print(f"  Total: {len(actual_organs)}")
    print()
    
    if registered:
        drift = compare_registries(actual_organs, registered)
        
        has_drift = any(drift[k] for k in drift)
        
        print("DRIFT ANALYSIS:")
        if drift["missing_in_registry"]:
            print(f"  Missing in registry: {drift['missing_in_registry']}")
        if drift["missing_in_filesystem"]:
            print(f"  Missing in filesystem: {drift['missing_in_filesystem']}")
        if drift["status_mismatch"]:
            print("  Status mismatches:")
            for m in drift["status_mismatch"]:
                print(f"    - {m['organ_id']}: {m['registered']} -> {m['actual']}")
        
        if not has_drift:
            print("  No drift detected")
        print()
        
        verdict = "PASS" if not has_drift else "DRIFT_DETECTED"
    else:
        print("DRIFT ANALYSIS:")
        print("  No existing registry found")
        drift = {"no_registry": True}
        verdict = "NO_REGISTRY"
    print()
    
    if args.sync:
        new_registry = generate_registry(actual_organs)
        
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
        
        print(f"Registry synced: {registry_path}")
        verdict = "SYNCED"
    
    print(f"VERDICT: {verdict}")
    
    # Save report
    if args.output:
        report = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "actual_organs": actual_organs,
            "drift": drift if registered else None,
            "verdict": verdict
        }
        with open(args.output, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2)
        print(f"Report: {args.output}")
    
    sys.exit(0 if verdict in ["PASS", "SYNCED"] else 1)


if __name__ == "__main__":
    main()
