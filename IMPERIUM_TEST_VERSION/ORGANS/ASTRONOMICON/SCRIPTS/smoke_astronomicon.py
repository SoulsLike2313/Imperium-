#!/usr/bin/env python3
"""
ASTRONOMICON - Smoke Test
Verifies Astronomicon organ basic functionality.
"""

import sys
from pathlib import Path

# Add parent to path for imports
sys.path.insert(0, str(Path(__file__).parent))

def smoke_test() -> dict:
    """Run smoke test for Astronomicon organ."""
    results = {
        "organ": "ASTRONOMICON",
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
    
    # Check 2: task_manager.py exists and imports
    try:
        import task_manager
        results["checks"].append({"name": "task_manager_import", "status": "PASS"})
        results["passed"] += 1
    except ImportError as e:
        results["checks"].append({"name": "task_manager_import", "status": "FAIL", "error": str(e)})
        results["failed"] += 1
        results["verdict"] = "FAIL"
        return results
    
    # Check 3: Can create task
    try:
        task = task_manager.create_task(
            title="Smoke Test Task",
            description="Test task for smoke test",
            priority="LOW"
        )
        if task and "task_id" in task:
            results["checks"].append({"name": "create_task", "status": "PASS"})
            results["passed"] += 1
            test_task_id = task["task_id"]
        else:
            results["checks"].append({"name": "create_task", "status": "FAIL"})
            results["failed"] += 1
            test_task_id = None
    except Exception as e:
        results["checks"].append({"name": "create_task", "status": "FAIL", "error": str(e)})
        results["failed"] += 1
        test_task_id = None
    
    # Check 4: Can get stats
    try:
        stats = task_manager.get_task_stats()
        if "active" in stats and "completed" in stats:
            results["checks"].append({"name": "get_stats", "status": "PASS"})
            results["passed"] += 1
        else:
            results["checks"].append({"name": "get_stats", "status": "FAIL"})
            results["failed"] += 1
    except Exception as e:
        results["checks"].append({"name": "get_stats", "status": "FAIL", "error": str(e)})
        results["failed"] += 1
    
    # Check 5: Can add stage
    if test_task_id:
        try:
            task = task_manager.add_stage(test_task_id, "Planning", "Plan approved")
            if task and len(task["stages"]) > 0:
                results["checks"].append({"name": "add_stage", "status": "PASS"})
                results["passed"] += 1
            else:
                results["checks"].append({"name": "add_stage", "status": "FAIL"})
                results["failed"] += 1
        except Exception as e:
            results["checks"].append({"name": "add_stage", "status": "FAIL", "error": str(e)})
            results["failed"] += 1
    
    # Cleanup: complete the test task
    if test_task_id:
        try:
            task_manager.update_task_status(test_task_id, "COMPLETED")
        except:
            pass
    
    results["verdict"] = "PASS" if results["failed"] == 0 else "FAIL"
    return results


def main():
    results = smoke_test()
    
    print("=" * 50)
    print("ASTRONOMICON SMOKE TEST")
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
