#!/usr/bin/env python3
"""
TRUTH AGGREGATOR
Aggregates truth state across all components.

Usage:
    py -3 truth_aggregator.py --receipts-dir RECEIPTS
    py -3 truth_aggregator.py --receipts-dir RECEIPTS --output REPORTS/truth_aggregate.json
"""

import argparse
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

# Import from sibling module
sys.path.insert(0, str(Path(__file__).parent))
from truth_state_checker import check_file, find_latest_receipt


COMPONENTS = [
    {"id": "smoke", "name": "Smoke Test", "prefix": "RCP-SMOKE"},
    {"id": "mechanicus", "name": "Mechanicus Health", "prefix": "RCP-MECH"},
    {"id": "inquisition", "name": "Inquisition Audit", "prefix": "RCP-INQ"},
    {"id": "master", "name": "Master Verification", "prefix": "RCP-MASTER"},
]


def aggregate_truth_state(receipts_dir, threshold_hours=24):
    """Aggregate truth state across all components."""
    receipts_path = Path(receipts_dir)
    
    components = []
    for comp in COMPONENTS:
        receipt = find_latest_receipt(comp["id"], receipts_dir)
        if receipt:
            state = check_file(receipt, threshold_hours)
            state["component_name"] = comp["name"]
        else:
            state = {
                "component_id": comp["id"],
                "component_name": comp["name"],
                "status": "UNKNOWN",
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "evidence_path": None,
                "freshness": "UNKNOWN",
                "blockers": ["No receipt found"],
                "source": "truth_aggregator.py"
            }
        components.append(state)
    
    # Calculate aggregate
    status_counts = {}
    for comp in components:
        status = comp.get("status", "UNKNOWN")
        status_counts[status] = status_counts.get(status, 0) + 1
    
    # Determine overall status
    if status_counts.get("FAIL", 0) > 0:
        overall_status = "FAIL"
    elif status_counts.get("UNKNOWN", 0) > 0:
        overall_status = "PARTIAL"
    elif status_counts.get("STALE", 0) > 0:
        overall_status = "STALE"
    elif status_counts.get("PARTIAL", 0) > 0:
        overall_status = "PARTIAL"
    elif status_counts.get("PASS_WITH_WARNINGS", 0) > 0:
        overall_status = "PASS_WITH_WARNINGS"
    elif status_counts.get("PASS", 0) == len(components):
        overall_status = "PASS"
    else:
        overall_status = "UNKNOWN"
    
    # Collect all blockers
    all_blockers = []
    for comp in components:
        for blocker in comp.get("blockers", []):
            all_blockers.append(f"[{comp['component_id']}] {blocker}")
    
    return {
        "schema_version": "IMPERIUM_TRUTH_AGGREGATE_V0_1",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "receipts_dir": str(receipts_dir),
        "threshold_hours": threshold_hours,
        "overall_status": overall_status,
        "status_counts": status_counts,
        "total_components": len(components),
        "pass_count": status_counts.get("PASS", 0) + status_counts.get("PASS_WITH_WARNINGS", 0),
        "fail_count": status_counts.get("FAIL", 0),
        "stale_count": status_counts.get("STALE", 0),
        "unknown_count": status_counts.get("UNKNOWN", 0),
        "blockers": all_blockers,
        "components": components,
        "source": "truth_aggregator.py"
    }


def main():
    parser = argparse.ArgumentParser(description="Aggregate truth state across components")
    parser.add_argument("--receipts-dir", default="RECEIPTS", help="Directory containing receipts")
    parser.add_argument("--threshold", type=int, default=24, help="Freshness threshold in hours")
    parser.add_argument("--output", help="Output file for result (JSON)")
    parser.add_argument("--quiet", action="store_true", help="Suppress detailed output")
    
    args = parser.parse_args()
    
    result = aggregate_truth_state(args.receipts_dir, args.threshold)
    
    if args.output:
        output_path = Path(args.output)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(result, f, indent=2)
        print(f"Output saved: {args.output}")
    
    print("=" * 60)
    print("TRUTH STATE AGGREGATE")
    print("=" * 60)
    print(f"Timestamp: {result['timestamp']}")
    print(f"Threshold: {result['threshold_hours']} hours")
    print()
    
    print("COMPONENT STATUS:")
    for comp in result["components"]:
        status_icon = {
            "PASS": "[OK]",
            "PASS_WITH_WARNINGS": "[WW]",
            "PARTIAL": "[XX]",
            "FAIL": "[XX]",
            "STALE": "[ST]",
            "UNKNOWN": "[??]",
        }.get(comp["status"], "[??]")
        freshness = f" ({comp.get('freshness', '?')})" if comp.get("freshness") else ""
        print(f"  {status_icon} {comp['component_name']}: {comp['status']}{freshness}")
    
    print()
    print("SUMMARY:")
    print(f"  Total: {result['total_components']}")
    print(f"  Pass: {result['pass_count']}")
    print(f"  Fail: {result['fail_count']}")
    print(f"  Stale: {result['stale_count']}")
    print(f"  Unknown: {result['unknown_count']}")
    
    if result["blockers"]:
        print()
        print("BLOCKERS:")
        for blocker in result["blockers"][:10]:
            print(f"  - {blocker}")
        if len(result["blockers"]) > 10:
            print(f"  ... and {len(result['blockers']) - 10} more")
    
    print()
    print(f"OVERALL STATUS: {result['overall_status']}")
    
    sys.exit(0 if result["overall_status"] in ["PASS", "PASS_WITH_WARNINGS"] else 1)


if __name__ == "__main__":
    main()
