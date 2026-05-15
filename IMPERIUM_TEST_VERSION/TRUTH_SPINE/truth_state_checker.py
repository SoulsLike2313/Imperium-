#!/usr/bin/env python3
"""
TRUTH STATE CHECKER
Validates truth state of a component based on evidence.

Usage:
    py -3 truth_state_checker.py --file <receipt_path>
    py -3 truth_state_checker.py --component <component_id> --receipts-dir <dir>
"""

import argparse
import json
import os
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path


def parse_timestamp(ts_str):
    """Parse ISO8601 timestamp string to datetime."""
    if not ts_str:
        return None
    # Handle various formats
    for fmt in [
        "%Y-%m-%dT%H:%M:%S.%f%z",
        "%Y-%m-%dT%H:%M:%S%z",
        "%Y-%m-%dT%H:%M:%S.%f",
        "%Y-%m-%dT%H:%M:%S",
        "%Y-%m-%d %H:%M:%S",
    ]:
        try:
            dt = datetime.strptime(ts_str, fmt)
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=timezone.utc)
            return dt
        except ValueError:
            continue
    return None


def check_freshness(evidence_timestamp, threshold_hours=24):
    """Check if evidence is fresh."""
    if not evidence_timestamp:
        return "UNKNOWN"
    
    now = datetime.now(timezone.utc)
    threshold = timedelta(hours=threshold_hours)
    
    if isinstance(evidence_timestamp, str):
        evidence_timestamp = parse_timestamp(evidence_timestamp)
    
    if not evidence_timestamp:
        return "UNKNOWN"
    
    age = now - evidence_timestamp
    if age <= threshold:
        return "FRESH"
    else:
        return "STALE"


def validate_truth_state(receipt_data, threshold_hours=24):
    """Validate truth state from receipt data."""
    result = {
        "component_id": receipt_data.get("component", receipt_data.get("type", "unknown")),
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "evidence_path": None,
        "evidence_timestamp": None,
        "freshness": "UNKNOWN",
        "check_count": 0,
        "pass_count": 0,
        "fail_count": 0,
        "warning_count": 0,
        "blockers": [],
        "source": "truth_state_checker.py",
        "notes": None
    }
    
    # Extract evidence timestamp
    evidence_ts = receipt_data.get("timestamp") or receipt_data.get("started")
    result["evidence_timestamp"] = evidence_ts
    
    # Check freshness
    result["freshness"] = check_freshness(evidence_ts, threshold_hours)
    
    # Extract check counts
    if "results" in receipt_data:
        results = receipt_data["results"]
        result["check_count"] = results.get("total", results.get("total_checks", 0))
        result["pass_count"] = results.get("passed", results.get("pass_count", 0))
        result["fail_count"] = results.get("failed", results.get("fail_count", 0))
        result["warning_count"] = results.get("warnings", 0)
    
    # Determine status
    verdict = receipt_data.get("verdict", receipt_data.get("status", "UNKNOWN"))
    
    # Apply truth semantics
    if verdict == "PASS":
        if result["freshness"] == "STALE":
            result["status"] = "STALE"
            result["blockers"].append("Evidence is stale")
        elif result["fail_count"] > 0:
            result["status"] = "FAIL"
            result["blockers"].append("PASS claimed but fail_count > 0 (FAKE GREEN)")
        elif result["evidence_timestamp"] is None:
            result["status"] = "UNKNOWN"
            result["blockers"].append("PASS claimed but no evidence timestamp")
        else:
            result["status"] = "PASS"
    elif verdict == "PASS_WITH_WARNINGS":
        if result["freshness"] == "STALE":
            result["status"] = "STALE"
        else:
            result["status"] = "PASS_WITH_WARNINGS"
    elif verdict == "PARTIAL":
        result["status"] = "PARTIAL"
    elif verdict == "FAIL":
        result["status"] = "FAIL"
    else:
        result["status"] = "UNKNOWN"
    
    return result


def check_file(file_path, threshold_hours=24):
    """Check truth state of a single receipt file."""
    try:
        # Try utf-8-sig first to handle BOM, fallback to utf-8
        try:
            with open(file_path, "r", encoding="utf-8-sig") as f:
                data = json.load(f)
        except UnicodeDecodeError:
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
        
        # Handle master receipt format (has overall_verdict and results array)
        if "overall_verdict" in data and "results" in data:
            results_list = data.get("results", [])
            data = {
                "type": "master",
                "component": "master",
                "results": {
                    "total": len(results_list),
                    "passed": sum(1 for r in results_list if r.get("verdict") == "PASS"),
                    "failed": sum(1 for r in results_list if r.get("verdict") == "FAIL"),
                },
                "timestamp": data.get("timestamp") or data.get("started"),
                "verdict": data.get("overall_verdict", "UNKNOWN")
            }
        # Handle case where data is a plain list
        elif isinstance(data, list):
            data = {
                "type": "master",
                "component": "master",
                "results": {
                    "total": len(data),
                    "passed": sum(1 for r in data if r.get("verdict") == "PASS" or r.get("status") == "PASS"),
                    "failed": sum(1 for r in data if r.get("verdict") == "FAIL" or r.get("status") == "FAIL"),
                },
                "timestamp": data[0].get("timestamp") if data else None,
                "verdict": "PASS" if all(r.get("verdict") in ["PASS", "PASS_WITH_WARNINGS"] or r.get("status") in ["PASS", "PASS_WITH_WARNINGS"] for r in data) else "FAIL"
            }
        
        result = validate_truth_state(data, threshold_hours)
        result["evidence_path"] = str(file_path)
        return result
    except Exception as e:
        return {
            "component_id": Path(file_path).stem,
            "status": "UNKNOWN",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "evidence_path": str(file_path),
            "freshness": "UNKNOWN",
            "blockers": [f"Error reading file: {e}"],
            "source": "truth_state_checker.py"
        }


def find_latest_receipt(component_id, receipts_dir):
    """Find the latest receipt for a component."""
    receipts_path = Path(receipts_dir)
    if not receipts_path.exists():
        return None
    
    # Map component to receipt prefix
    prefix_map = {
        "smoke": "RCP-SMOKE",
        "mechanicus": "RCP-MECH",
        "inquisition": "RCP-INQ",
        "master": "RCP-MASTER",
    }
    
    prefix = prefix_map.get(component_id.lower(), f"RCP-{component_id.upper()}")
    
    matching = list(receipts_path.glob(f"{prefix}*.json"))
    if not matching:
        return None
    
    # Sort by modification time, get latest
    matching.sort(key=lambda p: p.stat().st_mtime, reverse=True)
    return matching[0]


def main():
    parser = argparse.ArgumentParser(description="Check truth state of components")
    parser.add_argument("--file", help="Path to receipt file to check")
    parser.add_argument("--component", help="Component ID to check")
    parser.add_argument("--receipts-dir", default="RECEIPTS", help="Directory containing receipts")
    parser.add_argument("--threshold", type=int, default=24, help="Freshness threshold in hours")
    parser.add_argument("--output", help="Output file for result (JSON)")
    parser.add_argument("--quiet", action="store_true", help="Suppress output")
    
    args = parser.parse_args()
    
    if args.file:
        result = check_file(args.file, args.threshold)
    elif args.component:
        receipt = find_latest_receipt(args.component, args.receipts_dir)
        if receipt:
            result = check_file(receipt, args.threshold)
        else:
            result = {
                "component_id": args.component,
                "status": "UNKNOWN",
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "evidence_path": None,
                "freshness": "UNKNOWN",
                "blockers": [f"No receipt found for component: {args.component}"],
                "source": "truth_state_checker.py"
            }
    else:
        parser.print_help()
        sys.exit(1)
    
    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            json.dump(result, f, indent=2)
    
    if not args.quiet:
        print("=" * 60)
        print("TRUTH STATE CHECK")
        print("=" * 60)
        print(f"Component: {result['component_id']}")
        print(f"Status: {result['status']}")
        print(f"Freshness: {result.get('freshness', 'UNKNOWN')}")
        print(f"Evidence: {result.get('evidence_path', 'None')}")
        print(f"Timestamp: {result.get('evidence_timestamp', 'None')}")
        if result.get("blockers"):
            print(f"Blockers: {', '.join(result['blockers'])}")
        print()
        print(f"Checks: {result.get('check_count', 0)}")
        print(f"Passed: {result.get('pass_count', 0)}")
        print(f"Failed: {result.get('fail_count', 0)}")
        print(f"Warnings: {result.get('warning_count', 0)}")
    
    # Exit code based on status
    if result["status"] in ["PASS", "PASS_WITH_WARNINGS"]:
        sys.exit(0)
    else:
        sys.exit(1)


if __name__ == "__main__":
    main()
