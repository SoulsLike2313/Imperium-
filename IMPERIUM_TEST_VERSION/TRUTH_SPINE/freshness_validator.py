#!/usr/bin/env python3
"""
FRESHNESS VALIDATOR
Validates freshness of all receipts in a directory.

Usage:
    py -3 freshness_validator.py --receipts-dir RECEIPTS
    py -3 freshness_validator.py --receipts-dir RECEIPTS --threshold 12
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


def validate_receipt_freshness(receipt_path, threshold_hours=24):
    """Validate freshness of a single receipt."""
    try:
        with open(receipt_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        
        ts_str = data.get("timestamp") or data.get("started") or data.get("finished")
        ts = parse_timestamp(ts_str)
        
        if not ts:
            return {
                "file": str(receipt_path),
                "freshness": "UNKNOWN",
                "age_hours": None,
                "timestamp": None,
                "reason": "No valid timestamp found"
            }
        
        now = datetime.now(timezone.utc)
        age = now - ts
        age_hours = age.total_seconds() / 3600
        
        freshness = "FRESH" if age_hours <= threshold_hours else "STALE"
        
        return {
            "file": str(receipt_path),
            "freshness": freshness,
            "age_hours": round(age_hours, 2),
            "timestamp": ts.isoformat(),
            "threshold_hours": threshold_hours
        }
    except Exception as e:
        return {
            "file": str(receipt_path),
            "freshness": "UNKNOWN",
            "age_hours": None,
            "timestamp": None,
            "reason": str(e)
        }


def validate_all_receipts(receipts_dir, threshold_hours=24):
    """Validate freshness of all receipts in directory."""
    receipts_path = Path(receipts_dir)
    if not receipts_path.exists():
        return {"error": f"Directory not found: {receipts_dir}", "results": []}
    
    results = []
    for receipt_file in receipts_path.glob("RCP-*.json"):
        result = validate_receipt_freshness(receipt_file, threshold_hours)
        results.append(result)
    
    # Sort by age (oldest first)
    results.sort(key=lambda x: x.get("age_hours") or float("inf"), reverse=True)
    
    # Summary
    fresh_count = sum(1 for r in results if r["freshness"] == "FRESH")
    stale_count = sum(1 for r in results if r["freshness"] == "STALE")
    unknown_count = sum(1 for r in results if r["freshness"] == "UNKNOWN")
    
    return {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "receipts_dir": str(receipts_dir),
        "threshold_hours": threshold_hours,
        "summary": {
            "total": len(results),
            "fresh": fresh_count,
            "stale": stale_count,
            "unknown": unknown_count,
            "freshness_rate": round(fresh_count / len(results) * 100, 1) if results else 0
        },
        "verdict": "PASS" if stale_count == 0 and unknown_count == 0 else "FAIL",
        "results": results
    }


def main():
    parser = argparse.ArgumentParser(description="Validate freshness of receipts")
    parser.add_argument("--receipts-dir", default="RECEIPTS", help="Directory containing receipts")
    parser.add_argument("--threshold", type=int, default=24, help="Freshness threshold in hours")
    parser.add_argument("--output", help="Output file for result (JSON)")
    parser.add_argument("--quiet", action="store_true", help="Suppress detailed output")
    
    args = parser.parse_args()
    
    result = validate_all_receipts(args.receipts_dir, args.threshold)
    
    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            json.dump(result, f, indent=2)
    
    print("=" * 60)
    print("FRESHNESS VALIDATION")
    print("=" * 60)
    print(f"Directory: {result.get('receipts_dir')}")
    print(f"Threshold: {result.get('threshold_hours')} hours")
    print()
    
    summary = result.get("summary", {})
    print(f"Total receipts: {summary.get('total', 0)}")
    print(f"Fresh: {summary.get('fresh', 0)}")
    print(f"Stale: {summary.get('stale', 0)}")
    print(f"Unknown: {summary.get('unknown', 0)}")
    print(f"Freshness rate: {summary.get('freshness_rate', 0)}%")
    print()
    print(f"VERDICT: {result.get('verdict', 'UNKNOWN')}")
    
    if not args.quiet and result.get("results"):
        print()
        print("STALE RECEIPTS:")
        stale = [r for r in result["results"] if r["freshness"] == "STALE"]
        if stale:
            for r in stale[:10]:  # Show top 10
                print(f"  - {Path(r['file']).name}: {r.get('age_hours', '?')} hours old")
            if len(stale) > 10:
                print(f"  ... and {len(stale) - 10} more")
        else:
            print("  None")
    
    sys.exit(0 if result.get("verdict") == "PASS" else 1)


if __name__ == "__main__":
    main()
