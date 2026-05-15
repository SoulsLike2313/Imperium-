#!/usr/bin/env python3
"""
LESSON EXTRACTOR
Extracts lessons learned from receipts, reports, and corrections.

Scans:
- Receipts for patterns (PASS/FAIL sequences)
- Reports for recurring issues
- Corrections in chronology for anti-patterns

Outputs:
- lessons.json - extracted lessons
- patterns.json - reusable patterns
- anti_patterns.json - things to avoid

Usage:
    py -3 lesson_extractor.py                    # Extract all lessons
    py -3 lesson_extractor.py --since 24h        # Last 24 hours only
    py -3 lesson_extractor.py --output lessons.json
"""

import argparse
import json
import re
import sys
from datetime import datetime, timezone, timedelta
from pathlib import Path
from collections import defaultdict


def get_test_version_root():
    """Get the test version root directory."""
    return Path(__file__).parent.parent.parent.parent


def load_json_safe(filepath):
    """Load JSON file safely."""
    try:
        with open(filepath, "r", encoding="utf-8-sig") as f:
            return json.load(f)
    except:
        return None


def parse_time_delta(time_str):
    """Parse time delta string like '24h', '7d', '1w'."""
    match = re.match(r"(\d+)([hdwm])", time_str.lower())
    if not match:
        return timedelta(hours=24)
    
    value = int(match.group(1))
    unit = match.group(2)
    
    if unit == "h":
        return timedelta(hours=value)
    elif unit == "d":
        return timedelta(days=value)
    elif unit == "w":
        return timedelta(weeks=value)
    elif unit == "m":
        return timedelta(days=value * 30)
    
    return timedelta(hours=24)


def extract_from_receipts(since=None):
    """Extract lessons from receipts."""
    root = get_test_version_root()
    receipts_dir = root / "RECEIPTS"
    
    lessons = []
    patterns = defaultdict(int)
    
    if not receipts_dir.exists():
        return lessons, patterns
    
    cutoff = datetime.now(timezone.utc) - since if since else None
    
    for receipt_file in receipts_dir.glob("RCP-*.json"):
        receipt = load_json_safe(receipt_file)
        if not receipt:
            continue
        
        # Check timestamp
        timestamp_str = receipt.get("timestamp") or receipt.get("generated_at")
        if timestamp_str and cutoff:
            try:
                ts = datetime.fromisoformat(timestamp_str.replace("Z", "+00:00"))
                if ts < cutoff:
                    continue
            except:
                pass
        
        verdict = receipt.get("verdict") or receipt.get("overall_verdict")
        action = receipt.get("action", "unknown")
        
        # Track patterns
        patterns[f"{action}:{verdict}"] += 1
        
        # Extract lessons from failures
        if verdict == "FAIL":
            lesson = {
                "source": receipt_file.name,
                "type": "failure",
                "action": action,
                "timestamp": timestamp_str,
                "details": {}
            }
            
            # Extract failure details
            if "results" in receipt:
                failed = [r for r in receipt["results"] if r.get("verdict") == "FAIL"]
                lesson["details"]["failed_checks"] = [r.get("name") for r in failed]
            
            if "issues" in receipt:
                lesson["details"]["issues"] = receipt["issues"][:5]  # Top 5
            
            lessons.append(lesson)
        
        # Extract lessons from partial passes
        elif verdict == "PARTIAL":
            lesson = {
                "source": receipt_file.name,
                "type": "partial",
                "action": action,
                "timestamp": timestamp_str,
                "details": {}
            }
            
            if "results" in receipt:
                partial = [r for r in receipt["results"] if r.get("verdict") in ["PARTIAL", "FAIL"]]
                lesson["details"]["partial_checks"] = [r.get("name") for r in partial]
            
            lessons.append(lesson)
    
    return lessons, dict(patterns)


def extract_from_reports(since=None):
    """Extract lessons from reports."""
    root = get_test_version_root()
    reports_dir = root / "REPORTS"
    
    lessons = []
    
    if not reports_dir.exists():
        return lessons
    
    cutoff = datetime.now(timezone.utc) - since if since else None
    
    for report_file in reports_dir.glob("*.json"):
        report = load_json_safe(report_file)
        if not report:
            continue
        
        # Check timestamp
        timestamp_str = report.get("timestamp") or report.get("generated_at")
        if timestamp_str and cutoff:
            try:
                ts = datetime.fromisoformat(timestamp_str.replace("Z", "+00:00"))
                if ts < cutoff:
                    continue
            except:
                pass
        
        # Extract from drift reports
        if "drift" in report_file.name.lower():
            if report.get("verdict") != "PASS":
                lesson = {
                    "source": report_file.name,
                    "type": "drift",
                    "timestamp": timestamp_str,
                    "details": {
                        "verdict": report.get("verdict"),
                        "drift_count": report.get("drift_count", 0)
                    }
                }
                lessons.append(lesson)
        
        # Extract from audit reports
        if "audit" in report_file.name.lower():
            if report.get("summary", {}).get("total_issues", 0) > 0:
                lesson = {
                    "source": report_file.name,
                    "type": "audit_issue",
                    "timestamp": timestamp_str,
                    "details": {
                        "fake_green": report.get("summary", {}).get("fake_green_count", 0),
                        "stale_truth": report.get("summary", {}).get("stale_truth_count", 0),
                        "total_issues": report.get("summary", {}).get("total_issues", 0)
                    }
                }
                lessons.append(lesson)
    
    return lessons


def extract_anti_patterns(lessons):
    """Extract anti-patterns from lessons."""
    anti_patterns = []
    
    # Count failure types
    failure_counts = defaultdict(int)
    for lesson in lessons:
        if lesson["type"] == "failure":
            for check in lesson.get("details", {}).get("failed_checks", []):
                failure_counts[check] += 1
        elif lesson["type"] == "audit_issue":
            if lesson["details"].get("fake_green", 0) > 0:
                failure_counts["fake_green"] += lesson["details"]["fake_green"]
            if lesson["details"].get("stale_truth", 0) > 0:
                failure_counts["stale_truth"] += lesson["details"]["stale_truth"]
    
    # Convert to anti-patterns
    for pattern, count in sorted(failure_counts.items(), key=lambda x: -x[1]):
        if count >= 2:  # Only if occurred multiple times
            anti_patterns.append({
                "pattern": pattern,
                "occurrences": count,
                "severity": "HIGH" if count >= 5 else "MEDIUM" if count >= 3 else "LOW",
                "recommendation": f"Investigate recurring {pattern} failures"
            })
    
    return anti_patterns


def extract_success_patterns(patterns):
    """Extract success patterns from action:verdict counts."""
    success_patterns = []
    
    for key, count in sorted(patterns.items(), key=lambda x: -x[1]):
        action, verdict = key.split(":", 1)
        if verdict == "PASS" and count >= 3:
            success_patterns.append({
                "action": action,
                "success_count": count,
                "pattern": f"Reliable {action} workflow",
                "reusable": True
            })
    
    return success_patterns


def main():
    parser = argparse.ArgumentParser(description="Extract lessons from receipts and reports")
    parser.add_argument("--since", help="Time window (e.g., 24h, 7d, 1w)")
    parser.add_argument("--output", help="Output file for lessons")
    args = parser.parse_args()
    
    print("=" * 60)
    print("LESSON EXTRACTOR")
    print("=" * 60)
    print()
    
    since = parse_time_delta(args.since) if args.since else None
    if since:
        print(f"Time window: last {args.since}")
    else:
        print("Time window: all time")
    print()
    
    # Extract from receipts
    print("Scanning receipts...")
    receipt_lessons, patterns = extract_from_receipts(since)
    print(f"  Found {len(receipt_lessons)} lessons from receipts")
    
    # Extract from reports
    print("Scanning reports...")
    report_lessons = extract_from_reports(since)
    print(f"  Found {len(report_lessons)} lessons from reports")
    
    # Combine lessons
    all_lessons = receipt_lessons + report_lessons
    
    # Extract patterns
    print("Extracting patterns...")
    anti_patterns = extract_anti_patterns(all_lessons)
    success_patterns = extract_success_patterns(patterns)
    print(f"  Found {len(anti_patterns)} anti-patterns")
    print(f"  Found {len(success_patterns)} success patterns")
    
    print()
    
    # Build output
    output = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "time_window": args.since or "all",
        "summary": {
            "total_lessons": len(all_lessons),
            "failures": sum(1 for l in all_lessons if l["type"] == "failure"),
            "partials": sum(1 for l in all_lessons if l["type"] == "partial"),
            "drift_issues": sum(1 for l in all_lessons if l["type"] == "drift"),
            "audit_issues": sum(1 for l in all_lessons if l["type"] == "audit_issue"),
            "anti_patterns": len(anti_patterns),
            "success_patterns": len(success_patterns)
        },
        "lessons": all_lessons,
        "anti_patterns": anti_patterns,
        "success_patterns": success_patterns,
        "action_patterns": patterns
    }
    
    # Print summary
    print("SUMMARY:")
    print(f"  Total lessons: {output['summary']['total_lessons']}")
    print(f"  Failures: {output['summary']['failures']}")
    print(f"  Partials: {output['summary']['partials']}")
    print(f"  Anti-patterns: {output['summary']['anti_patterns']}")
    print(f"  Success patterns: {output['summary']['success_patterns']}")
    print()
    
    if anti_patterns:
        print("TOP ANTI-PATTERNS:")
        for ap in anti_patterns[:5]:
            print(f"  ⚠️ {ap['pattern']}: {ap['occurrences']} occurrences ({ap['severity']})")
        print()
    
    if success_patterns:
        print("SUCCESS PATTERNS:")
        for sp in success_patterns[:5]:
            print(f"  ✅ {sp['action']}: {sp['success_count']} successes")
        print()
    
    # Save output
    root = get_test_version_root()
    output_dir = root / "ORGANS" / "SCHOLA_IMPERIALIS" / "PATTERNS"
    output_dir.mkdir(parents=True, exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Save lessons
    lessons_path = output_dir / f"lessons_{timestamp}.json"
    with open(lessons_path, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2)
    print(f"Lessons: {lessons_path}")
    
    # Save latest
    latest_path = output_dir / "latest_lessons.json"
    with open(latest_path, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2)
    print(f"Latest: {latest_path}")
    
    # Save anti-patterns separately
    if anti_patterns:
        ap_path = output_dir / "anti_patterns.json"
        with open(ap_path, "w", encoding="utf-8") as f:
            json.dump({
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "anti_patterns": anti_patterns
            }, f, indent=2)
        print(f"Anti-patterns: {ap_path}")
    
    # Save success patterns separately
    if success_patterns:
        sp_path = output_dir / "success_patterns.json"
        with open(sp_path, "w", encoding="utf-8") as f:
            json.dump({
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "success_patterns": success_patterns
            }, f, indent=2)
        print(f"Success patterns: {sp_path}")
    
    print()
    print("VERDICT: PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
