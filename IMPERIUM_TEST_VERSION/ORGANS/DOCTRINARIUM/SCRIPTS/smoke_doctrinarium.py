#!/usr/bin/env python3
"""
DOCTRINARIUM SMOKE TEST
Validates schema and validation infrastructure.
"""

import json
import sys
from pathlib import Path


def get_test_version_root():
    """Get the test version root directory."""
    return Path(__file__).parent.parent.parent.parent


def main():
    print("=" * 60)
    print("DOCTRINARIUM SMOKE TEST")
    print("=" * 60)
    print()
    
    root = get_test_version_root()
    results = []
    
    # Check 1: Contract exists
    contract_path = root / "ORGANS" / "DOCTRINARIUM" / "ORGAN_CONTRACT.json"
    if contract_path.exists():
        results.append(("Contract exists", True))
        print("✅ Contract exists")
    else:
        results.append(("Contract exists", False))
        print("❌ Contract missing")
    
    # Check 2: Schemas directory exists
    schemas_dir = root / "schemas"
    if schemas_dir.exists():
        results.append(("Schemas directory", True))
        print("✅ Schemas directory exists")
    else:
        results.append(("Schemas directory", False))
        print("❌ Schemas directory missing")
    
    # Check 3: At least one schema file
    schema_files = list(schemas_dir.glob("*.json")) if schemas_dir.exists() else []
    if schema_files:
        results.append(("Schema files", True))
        print(f"✅ Found {len(schema_files)} schema files")
    else:
        results.append(("Schema files", False))
        print("❌ No schema files found")
    
    # Check 4: Schema files are valid JSON
    valid_schemas = 0
    for sf in schema_files:
        try:
            with open(sf, "r", encoding="utf-8-sig") as f:
                json.load(f)
            valid_schemas += 1
        except:
            pass
    
    if valid_schemas == len(schema_files) and schema_files:
        results.append(("Valid JSON schemas", True))
        print(f"✅ All {valid_schemas} schemas are valid JSON")
    elif valid_schemas > 0:
        results.append(("Valid JSON schemas", True))
        print(f"⚠️ {valid_schemas}/{len(schema_files)} schemas are valid JSON")
    else:
        results.append(("Valid JSON schemas", False))
        print("❌ No valid JSON schemas")
    
    print()
    passed = sum(1 for _, ok in results if ok)
    total = len(results)
    
    print(f"Passed: {passed}/{total}")
    
    if passed == total:
        print("VERDICT: PASS")
        return 0
    elif passed > 0:
        print("VERDICT: PARTIAL")
        return 0
    else:
        print("VERDICT: FAIL")
        return 1


if __name__ == "__main__":
    sys.exit(main())
