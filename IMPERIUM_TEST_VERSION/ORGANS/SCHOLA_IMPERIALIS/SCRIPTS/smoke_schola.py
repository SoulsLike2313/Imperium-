#!/usr/bin/env python3
"""
SCHOLA IMPERIALIS SMOKE TEST
Validates learning and memory infrastructure.
"""

import json
import sys
from pathlib import Path


def get_test_version_root():
    """Get the test version root directory."""
    return Path(__file__).parent.parent.parent.parent


def main():
    print("=" * 60)
    print("SCHOLA IMPERIALIS SMOKE TEST")
    print("=" * 60)
    print()
    
    root = get_test_version_root()
    results = []
    
    # Check 1: Contract exists
    contract_path = root / "ORGANS" / "SCHOLA_IMPERIALIS" / "ORGAN_CONTRACT.json"
    if contract_path.exists():
        results.append(("Contract exists", True))
        print("✅ Contract exists")
    else:
        results.append(("Contract exists", False))
        print("❌ Contract missing")
    
    # Check 2: Second Brain exists
    second_brain = root / "SECOND_BRAIN"
    if second_brain.exists():
        results.append(("Second Brain exists", True))
        print("✅ Second Brain exists")
    else:
        results.append(("Second Brain exists", False))
        print("❌ Second Brain missing")
    
    # Check 3: Memory schema exists
    memory_schema = root / "SECOND_BRAIN" / "MEMORY_SCHEMA.json"
    if memory_schema.exists():
        results.append(("Memory schema", True))
        print("✅ Memory schema exists")
    else:
        results.append(("Memory schema", False))
        print("❌ Memory schema missing")
    
    # Check 4: Memory scripts exist
    scripts_dir = root / "SECOND_BRAIN" / "SCRIPTS"
    scripts = list(scripts_dir.glob("*.py")) if scripts_dir.exists() else []
    if scripts:
        results.append(("Memory scripts", True))
        print(f"✅ Found {len(scripts)} memory scripts")
    else:
        results.append(("Memory scripts", False))
        print("❌ No memory scripts found")
    
    # Check 5: Memory reports exist
    reports_dir = root / "SECOND_BRAIN" / "REPORTS"
    reports = list(reports_dir.glob("*.json")) if reports_dir.exists() else []
    if reports:
        results.append(("Memory reports", True))
        print(f"✅ Found {len(reports)} memory reports")
    else:
        results.append(("Memory reports", False))
        print("⚠️ No memory reports yet")
    
    print()
    passed = sum(1 for _, ok in results if ok)
    total = len(results)
    
    print(f"Passed: {passed}/{total}")
    
    if passed == total:
        print("VERDICT: PASS")
        return 0
    elif passed >= 3:
        print("VERDICT: PARTIAL")
        return 0
    else:
        print("VERDICT: FAIL")
        return 1


if __name__ == "__main__":
    sys.exit(main())
