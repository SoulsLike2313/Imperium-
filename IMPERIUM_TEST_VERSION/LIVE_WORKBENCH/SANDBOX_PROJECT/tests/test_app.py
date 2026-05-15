#!/usr/bin/env python3
"""
test_app.py - Tests for sandbox application.
"""

import sys
from pathlib import Path

# Add parent to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app import add, subtract, multiply, divide, is_even, factorial


def test_add():
    assert add(2, 3) == 5
    assert add(-1, 1) == 0
    assert add(0, 0) == 0


def test_subtract():
    assert subtract(5, 2) == 3
    assert subtract(2, 5) == -3
    assert subtract(0, 0) == 0


def test_multiply():
    assert multiply(4, 3) == 12
    assert multiply(-2, 3) == -6
    assert multiply(0, 100) == 0


def test_divide():
    assert divide(10, 2) == 5.0
    assert divide(7, 2) == 3.5
    try:
        divide(1, 0)
        assert False, "Should raise ValueError"
    except ValueError:
        pass


def test_is_even():
    assert is_even(4) == True
    assert is_even(3) == False
    assert is_even(0) == True


def test_factorial():
    assert factorial(0) == 1
    assert factorial(1) == 1
    assert factorial(5) == 120
    try:
        factorial(-1)
        assert False, "Should raise ValueError"
    except ValueError:
        pass


def run_all_tests():
    """Run all tests and return results."""
    tests = [
        ("test_add", test_add),
        ("test_subtract", test_subtract),
        ("test_multiply", test_multiply),
        ("test_divide", test_divide),
        ("test_is_even", test_is_even),
        ("test_factorial", test_factorial),
    ]
    
    results = []
    passed = 0
    failed = 0
    
    for name, test_func in tests:
        try:
            test_func()
            results.append({"name": name, "status": "PASS", "error": None})
            passed += 1
        except Exception as e:
            results.append({"name": name, "status": "FAIL", "error": str(e)})
            failed += 1
    
    return {
        "total": len(tests),
        "passed": passed,
        "failed": failed,
        "results": results
    }


if __name__ == "__main__":
    print("Running sandbox tests...")
    results = run_all_tests()
    
    for r in results["results"]:
        status = "[OK]" if r["status"] == "PASS" else "[XX]"
        print(f"  {status} {r['name']}")
        if r["error"]:
            print(f"      Error: {r['error']}")
    
    print()
    print(f"Total: {results['total']}")
    print(f"Passed: {results['passed']}")
    print(f"Failed: {results['failed']}")
    
    sys.exit(0 if results['failed'] == 0 else 1)
