#!/usr/bin/env python3
"""
DRIFT DETECTOR
Detects drift between registries and actual filesystem state.

Usage:
    py -3 drift_detector.py
    py -3 drift_detector.py --output REPORTS/drift_report.json
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


def scan_scripts():
    """Scan all Python scripts in test version."""
    root = get_test_version_root()
    scripts = []
    
    for py_file in root.rglob("*.py"):
        rel_path = py_file.relative_to(root)
        
        # Check syntax
        try:
            with open(py_file, "r", encoding="utf-8") as f:
                content = f.read()
            compile(content, str(py_file), "exec")
            syntax_valid = True
        except SyntaxError:
            syntax_valid = False
        except Exception:
            syntax_valid = None
        
        scripts.append({
            "path": str(rel_path),
            "name": py_file.name,
            "syntax_valid": syntax_valid,
            "size": py_file.stat().st_size
        })
    
    return scripts


def scan_json_files():
    """Scan all JSON files in test version."""
    root = get_test_version_root()
    json_files = []
    
    for json_file in root.rglob("*.json"):
        rel_path = json_file.relative_to(root)
        
        # Check validity
        try:
            with open(json_file, "r", encoding="utf-8-sig") as f:
                json.load(f)
            valid = True
        except:
            valid = False
        
        json_files.append({
            "path": str(rel_path),
            "name": json_file.name,
            "valid": valid,
            "size": json_file.stat().st_size
        })
    
    return json_files


def check_receipt_freshness(receipts_dir, threshold_hours=24):
    """Check freshness of receipts."""
    receipts_path = get_test_version_root() / receipts_dir
    
    if not receipts_path.exists():
        return {"error": "Receipts directory not found"}
    
    now = datetime.now(timezone.utc)
    stale = []
    fresh = []
    
    for receipt in receipts_path.glob("RCP-*.json"):
        try:
            mtime = datetime.fromtimestamp(receipt.stat().st_mtime, tz=timezone.utc)
            age_hours = (now - mtime).total_seconds() / 3600
            
            if age_hours > threshold_hours:
                stale.append({"file": receipt.name, "age_hours": round(age_hours, 1)})
            else:
                fresh.append({"file": receipt.name, "age_hours": round(age_hours, 1)})
        except:
            pass
    
    return {
        "total": len(stale) + len(fresh),
        "fresh": len(fresh),
        "stale": len(stale),
        "stale_files": stale[:10]  # Top 10 oldest
    }


def detect_drift():
    """Run full drift detection."""
    results = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "checks": []
    }
    
    # 1. Script health
    scripts = scan_scripts()
    invalid_scripts = [s for s in scripts if s["syntax_valid"] is False]
    results["checks"].append({
        "check": "script_syntax",
        "total": len(scripts),
        "valid": len(scripts) - len(invalid_scripts),
        "invalid": len(invalid_scripts),
        "invalid_files": [s["path"] for s in invalid_scripts],
        "status": "PASS" if not invalid_scripts else "FAIL"
    })
    
    # 2. JSON validity
    json_files = scan_json_files()
    invalid_json = [j for j in json_files if not j["valid"]]
    results["checks"].append({
        "check": "json_validity",
        "total": len(json_files),
        "valid": len(json_files) - len(invalid_json),
        "invalid": len(invalid_json),
        "invalid_files": [j["path"] for j in invalid_json],
        "status": "PASS" if not invalid_json else "FAIL"
    })
    
    # 3. Receipt freshness
    freshness = check_receipt_freshness("RECEIPTS")
    results["checks"].append({
        "check": "receipt_freshness",
        **freshness,
        "status": "PASS" if freshness.get("stale", 0) == 0 else "PARTIAL"
    })
    
    # 4. Required files
    required_files = [
        "RUN_ALL.ps1",
        "OWNER_CHRONOLOGY_RU.md",
        "BASELINE_STATUS.json",
        "REGISTRY/ORGAN_REGISTRY.json",
    ]
    missing = []
    for f in required_files:
        if not (get_test_version_root() / f).exists():
            missing.append(f)
    
    results["checks"].append({
        "check": "required_files",
        "total": len(required_files),
        "present": len(required_files) - len(missing),
        "missing": missing,
        "status": "PASS" if not missing else "FAIL"
    })
    
    # Overall verdict
    statuses = [c["status"] for c in results["checks"]]
    if "FAIL" in statuses:
        results["verdict"] = "FAIL"
    elif "PARTIAL" in statuses:
        results["verdict"] = "PARTIAL"
    else:
        results["verdict"] = "PASS"
    
    return results


def main():
    parser = argparse.ArgumentParser(description="Detect drift in test version")
    parser.add_argument("--output", help="Output file for report")
    args = parser.parse_args()
    
    results = detect_drift()
    
    print("=" * 60)
    print("DRIFT DETECTOR")
    print("=" * 60)
    print(f"Timestamp: {results['timestamp']}")
    print()
    
    for check in results["checks"]:
        icon = {"PASS": "✅", "PARTIAL": "⚠️", "FAIL": "❌"}.get(check["status"], "❓")
        print(f"  {icon} {check['check']}: {check['status']}")
        
        if check["status"] != "PASS":
            if check.get("invalid_files"):
                for f in check["invalid_files"][:5]:
                    print(f"     - {f}")
            if check.get("missing"):
                for f in check["missing"]:
                    print(f"     - Missing: {f}")
            if check.get("stale_files"):
                for f in check["stale_files"][:5]:
                    print(f"     - Stale: {f['file']} ({f['age_hours']}h)")
    
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
