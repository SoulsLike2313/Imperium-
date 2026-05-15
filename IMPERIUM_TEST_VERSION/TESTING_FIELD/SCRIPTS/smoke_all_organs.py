#!/usr/bin/env python3
"""
SMOKE ALL ORGANS
Runs smoke tests for all organs in the system.

Usage:
    py -3 smoke_all_organs.py
    py -3 smoke_all_organs.py --organ THRONE
"""

import argparse
import json
import os
import sys
from pathlib import Path
from datetime import datetime, timezone


def get_test_version_root():
    """Get the test version root directory."""
    return Path(__file__).parent.parent.parent


def get_organs_dir():
    """Get the ORGANS directory."""
    return get_test_version_root() / "ORGANS"


def check_organ_contract(organ_path):
    """Check if organ has valid ORGAN_CONTRACT.json."""
    contract_path = organ_path / "ORGAN_CONTRACT.json"
    
    if not contract_path.exists():
        return {"status": "FAIL", "reason": "ORGAN_CONTRACT.json not found"}
    
    try:
        with open(contract_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        
        # Accept both old and new field names
        organ_id = data.get("organ_id")
        organ_name = data.get("organ_name") or data.get("name")
        purpose = data.get("purpose") or data.get("responsibility")
        
        missing = []
        if not organ_id:
            missing.append("organ_id")
        if not organ_name:
            missing.append("organ_name/name")
        if not purpose:
            missing.append("purpose/responsibility")
        
        if missing:
            return {"status": "FAIL", "reason": f"Missing fields: {missing}"}
        
        return {"status": "PASS", "organ_id": organ_id, "organ_name": organ_name}
    except json.JSONDecodeError as e:
        return {"status": "FAIL", "reason": f"Invalid JSON: {e}"}
    except Exception as e:
        return {"status": "FAIL", "reason": str(e)}


def check_organ_readme(organ_path):
    """Check if organ has README.md."""
    readme_path = organ_path / "README.md"
    if readme_path.exists():
        return {"status": "PASS"}
    return {"status": "FAIL", "reason": "README.md not found"}


def check_organ_structure(organ_path):
    """Check organ directory structure."""
    checks = []
    
    # Contract check
    contract_result = check_organ_contract(organ_path)
    checks.append({"check": "contract", **contract_result})
    
    # README check
    readme_result = check_organ_readme(organ_path)
    checks.append({"check": "readme", **readme_result})
    
    # Scripts directory (optional but good to have)
    scripts_dir = organ_path / "SCRIPTS"
    if scripts_dir.exists():
        script_count = len(list(scripts_dir.glob("*.py")))
        checks.append({"check": "scripts", "status": "PASS", "count": script_count})
    else:
        checks.append({"check": "scripts", "status": "PARTIAL", "reason": "No SCRIPTS directory"})
    
    return checks


def smoke_test_organ(organ_name):
    """Run smoke test for a single organ."""
    organs_dir = get_organs_dir()
    organ_path = organs_dir / organ_name
    
    if not organ_path.exists():
        return {
            "organ": organ_name,
            "status": "FAIL",
            "reason": f"Organ directory not found: {organ_path}"
        }
    
    checks = check_organ_structure(organ_path)
    
    pass_count = sum(1 for c in checks if c["status"] == "PASS")
    fail_count = sum(1 for c in checks if c["status"] == "FAIL")
    partial_count = sum(1 for c in checks if c["status"] == "PARTIAL")
    
    if fail_count > 0:
        verdict = "FAIL"
    elif partial_count > 0:
        verdict = "PARTIAL"
    else:
        verdict = "PASS"
    
    return {
        "organ": organ_name,
        "path": str(organ_path),
        "checks": checks,
        "summary": {
            "total": len(checks),
            "passed": pass_count,
            "failed": fail_count,
            "partial": partial_count
        },
        "verdict": verdict
    }


def get_all_organs():
    """Get list of all organ directories."""
    organs_dir = get_organs_dir()
    if not organs_dir.exists():
        return []
    
    return [d.name for d in organs_dir.iterdir() if d.is_dir()]


def run_all_smoke_tests():
    """Run smoke tests for all organs."""
    organs = get_all_organs()
    
    results = []
    for organ in sorted(organs):
        result = smoke_test_organ(organ)
        results.append(result)
    
    # Also check special organs (Doctrinarium in schemas/, Schola in SECOND_BRAIN/)
    special_organs = [
        {"name": "DOCTRINARIUM", "path": get_test_version_root() / "schemas"},
        {"name": "SCHOLA_IMPERIALIS", "path": get_test_version_root() / "SECOND_BRAIN"},
    ]
    
    for special in special_organs:
        if special["path"].exists():
            # Simple existence check for special organs
            results.append({
                "organ": special["name"],
                "path": str(special["path"]),
                "checks": [{"check": "exists", "status": "PASS"}],
                "summary": {"total": 1, "passed": 1, "failed": 0, "partial": 0},
                "verdict": "PASS",
                "note": "Special organ location"
            })
    
    pass_count = sum(1 for r in results if r["verdict"] == "PASS")
    fail_count = sum(1 for r in results if r["verdict"] == "FAIL")
    partial_count = sum(1 for r in results if r["verdict"] == "PARTIAL")
    
    overall = "PASS" if fail_count == 0 and partial_count == 0 else "PARTIAL" if pass_count > 0 else "FAIL"
    
    return {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "organs_tested": len(results),
        "results": results,
        "summary": {
            "total": len(results),
            "passed": pass_count,
            "failed": fail_count,
            "partial": partial_count
        },
        "verdict": overall
    }


def main():
    parser = argparse.ArgumentParser(description="Smoke test all organs")
    parser.add_argument("--organ", help="Test specific organ only")
    parser.add_argument("--output", help="Output file for results")
    args = parser.parse_args()
    
    if args.organ:
        result = smoke_test_organ(args.organ)
        results = {"timestamp": datetime.now(timezone.utc).isoformat(), "results": [result], "verdict": result["verdict"]}
    else:
        results = run_all_smoke_tests()
    
    print("=" * 60)
    print("ORGAN SMOKE TEST")
    print("=" * 60)
    print(f"Timestamp: {results['timestamp']}")
    print()
    
    for r in results["results"]:
        icon = {"PASS": "✅", "PARTIAL": "⚠️", "FAIL": "❌"}.get(r["verdict"], "❓")
        print(f"  {icon} {r['organ']}: {r['verdict']}")
        if r["verdict"] != "PASS":
            for check in r.get("checks", []):
                if check["status"] != "PASS":
                    print(f"     - {check['check']}: {check.get('reason', check['status'])}")
    
    print()
    summary = results.get("summary", {})
    print(f"Total organs: {summary.get('total', len(results['results']))}")
    print(f"Passed: {summary.get('passed', 0)}")
    print(f"Partial: {summary.get('partial', 0)}")
    print(f"Failed: {summary.get('failed', 0)}")
    print()
    print(f"OVERALL VERDICT: {results['verdict']}")
    
    # Save report
    if args.output:
        output_path = Path(args.output)
    else:
        reports_dir = get_test_version_root() / "TESTING_FIELD" / "SMOKE_RESULTS"
        reports_dir.mkdir(parents=True, exist_ok=True)
        output_path = reports_dir / "organ_smoke_report.json"
    
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)
    
    print(f"\nReport: {output_path}")
    
    sys.exit(0 if results["verdict"] == "PASS" else 1)


if __name__ == "__main__":
    main()
