#!/usr/bin/env python3
"""
THRONE - Smoke Test
Verifies Throne organ basic functionality.
"""

import sys
from pathlib import Path

# Add parent to path for imports
sys.path.insert(0, str(Path(__file__).parent))

def smoke_test() -> dict:
    """Run smoke test for Throne organ."""
    results = {
        "organ": "THRONE",
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
    
    # Check 2: approval_gate.py exists and imports
    try:
        import approval_gate
        results["checks"].append({"name": "approval_gate_import", "status": "PASS"})
        results["passed"] += 1
    except ImportError as e:
        results["checks"].append({"name": "approval_gate_import", "status": "FAIL", "error": str(e)})
        results["failed"] += 1
    
    # Check 3: Can create approval request
    try:
        req = approval_gate.create_approval_request(
            action="test_action",
            scope="smoke_test",
            risk_level="LOW",
            requester="SmokeTest"
        )
        if req and "request_id" in req:
            results["checks"].append({"name": "create_request", "status": "PASS"})
            results["passed"] += 1
            
            # Cleanup: reject the test request
            approval_gate.reject_request(req["request_id"], reason="Smoke test cleanup")
        else:
            results["checks"].append({"name": "create_request", "status": "FAIL"})
            results["failed"] += 1
    except Exception as e:
        results["checks"].append({"name": "create_request", "status": "FAIL", "error": str(e)})
        results["failed"] += 1
    
    # Check 4: Can get stats
    try:
        stats = approval_gate.get_approval_stats()
        if "pending" in stats and "approved" in stats:
            results["checks"].append({"name": "get_stats", "status": "PASS"})
            results["passed"] += 1
        else:
            results["checks"].append({"name": "get_stats", "status": "FAIL"})
            results["failed"] += 1
    except Exception as e:
        results["checks"].append({"name": "get_stats", "status": "FAIL", "error": str(e)})
        results["failed"] += 1
    
    # Check 5: check_approval_required works
    try:
        needs_approval = approval_gate.check_approval_required("delete_files", "HIGH")
        if needs_approval:
            results["checks"].append({"name": "approval_check", "status": "PASS"})
            results["passed"] += 1
        else:
            results["checks"].append({"name": "approval_check", "status": "FAIL"})
            results["failed"] += 1
    except Exception as e:
        results["checks"].append({"name": "approval_check", "status": "FAIL", "error": str(e)})
        results["failed"] += 1
    
    results["verdict"] = "PASS" if results["failed"] == 0 else "FAIL"
    return results


def main():
    results = smoke_test()
    
    print("=" * 50)
    print("THRONE SMOKE TEST")
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
