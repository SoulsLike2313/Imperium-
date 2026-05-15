#!/usr/bin/env python3
"""
CUSTODES - Smoke Test
Verifies Custodes organ basic functionality.
"""

import sys
from pathlib import Path

# Add parent to path for imports
sys.path.insert(0, str(Path(__file__).parent))

def smoke_test() -> dict:
    """Run smoke test for Custodes organ."""
    results = {
        "organ": "CUSTODES",
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
    
    # Check 2: boundary_checker.py exists and imports
    try:
        import boundary_checker
        results["checks"].append({"name": "boundary_checker_import", "status": "PASS"})
        results["passed"] += 1
    except ImportError as e:
        results["checks"].append({"name": "boundary_checker_import", "status": "FAIL", "error": str(e)})
        results["failed"] += 1
        results["verdict"] = "FAIL"
        return results
    
    # Check 3: is_private_zone works
    try:
        is_private = boundary_checker.is_private_zone("E:\\IMPERIUM\\IMPERIUM_TEST_VERSION\\test.py")
        if is_private:
            results["checks"].append({"name": "private_zone_check", "status": "PASS"})
            results["passed"] += 1
        else:
            results["checks"].append({"name": "private_zone_check", "status": "FAIL"})
            results["failed"] += 1
    except Exception as e:
        results["checks"].append({"name": "private_zone_check", "status": "FAIL", "error": str(e)})
        results["failed"] += 1
    
    # Check 4: check_for_secrets works
    try:
        test_content = 'password = "secret123"\napi_key = "abc123"'
        violations = boundary_checker.check_for_secrets(test_content)
        if len(violations) >= 2:
            results["checks"].append({"name": "secret_detection", "status": "PASS"})
            results["passed"] += 1
        else:
            results["checks"].append({"name": "secret_detection", "status": "FAIL"})
            results["failed"] += 1
    except Exception as e:
        results["checks"].append({"name": "secret_detection", "status": "FAIL", "error": str(e)})
        results["failed"] += 1
    
    # Check 5: check_boundary_crossing works
    try:
        result = boundary_checker.check_boundary_crossing(
            "E:\\IMPERIUM\\IMPERIUM_TEST_VERSION\\secret.txt",
            "E:\\IMPERIUM\\public.md"
        )
        if not result["allowed"]:
            results["checks"].append({"name": "boundary_crossing", "status": "PASS"})
            results["passed"] += 1
        else:
            results["checks"].append({"name": "boundary_crossing", "status": "FAIL"})
            results["failed"] += 1
    except Exception as e:
        results["checks"].append({"name": "boundary_crossing", "status": "FAIL", "error": str(e)})
        results["failed"] += 1
    
    # Check 6: get_violation_stats works
    try:
        stats = boundary_checker.get_violation_stats()
        if "total" in stats and "resolved" in stats:
            results["checks"].append({"name": "get_stats", "status": "PASS"})
            results["passed"] += 1
        else:
            results["checks"].append({"name": "get_stats", "status": "FAIL"})
            results["failed"] += 1
    except Exception as e:
        results["checks"].append({"name": "get_stats", "status": "FAIL", "error": str(e)})
        results["failed"] += 1
    
    results["verdict"] = "PASS" if results["failed"] == 0 else "FAIL"
    return results


def main():
    results = smoke_test()
    
    print("=" * 50)
    print("CUSTODES SMOKE TEST")
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
