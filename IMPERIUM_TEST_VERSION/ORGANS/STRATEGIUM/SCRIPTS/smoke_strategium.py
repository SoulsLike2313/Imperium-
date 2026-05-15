#!/usr/bin/env python3
"""
STRATEGIUM - Smoke Test
Verifies Strategium organ basic functionality.
"""

import sys
from pathlib import Path

# Add parent to path for imports
sys.path.insert(0, str(Path(__file__).parent))

def smoke_test() -> dict:
    """Run smoke test for Strategium organ."""
    results = {
        "organ": "STRATEGIUM",
        "checks": [],
        "passed": 0,
        "failed": 0
    }
    
    # Check 1: Contract exists
    contract_path = Path(__file__).parent.parent / "ORGAN_CONTRACT.json"
    if contract_path.exists():
        results["checks"].append({"name": "contract_exists", "status": "PASS"})
        results["passed"] += 1
    else:
        results["checks"].append({"name": "contract_exists", "status": "FAIL"})
        results["failed"] += 1
    
    # Check 2: roadmap_manager.py exists and imports
    try:
        import roadmap_manager
        results["checks"].append({"name": "roadmap_manager_import", "status": "PASS"})
        results["passed"] += 1
    except ImportError as e:
        results["checks"].append({"name": "roadmap_manager_import", "status": "FAIL", "error": str(e)})
        results["failed"] += 1
        results["verdict"] = "FAIL"
        return results
    
    # Check 3: Can create roadmap entry
    try:
        entry = roadmap_manager.create_roadmap_entry(
            title="Smoke Test Entry",
            phase="TEST",
            priority="LOW"
        )
        if entry and "entry_id" in entry:
            results["checks"].append({"name": "create_entry", "status": "PASS"})
            results["passed"] += 1
            test_entry_id = entry["entry_id"]
        else:
            results["checks"].append({"name": "create_entry", "status": "FAIL"})
            results["failed"] += 1
            test_entry_id = None
    except Exception as e:
        results["checks"].append({"name": "create_entry", "status": "FAIL", "error": str(e)})
        results["failed"] += 1
        test_entry_id = None
    
    # Check 4: Can get stats
    try:
        stats = roadmap_manager.get_roadmap_stats()
        if "total" in stats and "by_status" in stats:
            results["checks"].append({"name": "get_stats", "status": "PASS"})
            results["passed"] += 1
        else:
            results["checks"].append({"name": "get_stats", "status": "FAIL"})
            results["failed"] += 1
    except Exception as e:
        results["checks"].append({"name": "get_stats", "status": "FAIL", "error": str(e)})
        results["failed"] += 1
    
    # Check 5: Can update status
    if test_entry_id:
        try:
            entry = roadmap_manager.update_entry_status(test_entry_id, "COMPLETED")
            if entry["status"] == "COMPLETED":
                results["checks"].append({"name": "update_status", "status": "PASS"})
                results["passed"] += 1
            else:
                results["checks"].append({"name": "update_status", "status": "FAIL"})
                results["failed"] += 1
        except Exception as e:
            results["checks"].append({"name": "update_status", "status": "FAIL", "error": str(e)})
            results["failed"] += 1
    
    results["verdict"] = "PASS" if results["failed"] == 0 else "FAIL"
    return results


def main():
    results = smoke_test()
    
    print("=" * 50)
    print("STRATEGIUM SMOKE TEST")
    print("=" * 50)
    
    for check in results["checks"]:
        status = "✅" if check["status"] == "PASS" else "❌"
        print(f"  {status} {check['name']}")
        if "error" in check:
            print(f"      Error: {check['error']}")
    
    print()
    print(f"Passed: {results['passed']}")
    print(f"Failed: {results['failed']}")
    print(f"Verdict: {results['verdict']}")
    
    sys.exit(0 if results["verdict"] == "PASS" else 1)


if __name__ == "__main__":
    main()
