#!/usr/bin/env python3
"""
ANTI-PATTERN SCANNER
Scans codebase for known anti-patterns.

Integrates with Inquisition to flag violations.

Usage:
    py -3 anti_pattern_scanner.py                    # Scan all
    py -3 anti_pattern_scanner.py --path ORGANS/     # Scan specific path
    py -3 anti_pattern_scanner.py --output report.json
"""

import argparse
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path


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


# Built-in anti-patterns
BUILTIN_ANTI_PATTERNS = [
    {
        "id": "AP001",
        "name": "Hardcoded PASS",
        "description": "Verdict hardcoded to PASS without evidence",
        "pattern": r'["\']PASS["\']',
        "context_check": lambda line: "verdict" in line.lower() and "if" not in line.lower(),
        "severity": "HIGH",
        "file_types": [".py", ".ps1"]
    },
    {
        "id": "AP002",
        "name": "Missing timestamp",
        "description": "JSON output without timestamp field",
        "pattern": r'"verdict":\s*"',
        "context_check": lambda content: '"timestamp"' not in content and '"generated_at"' not in content,
        "severity": "MEDIUM",
        "file_types": [".json"],
        "full_file_check": True
    },
    {
        "id": "AP003",
        "name": "Bare except",
        "description": "Catching all exceptions without specificity",
        "pattern": r'except\s*:',
        "severity": "LOW",
        "file_types": [".py"]
    },
    {
        "id": "AP004",
        "name": "TODO in production",
        "description": "TODO comments in production code",
        "pattern": r'#\s*TODO',
        "severity": "LOW",
        "file_types": [".py"]
    },
    {
        "id": "AP005",
        "name": "Fake green indicator",
        "description": "Suspicious PASS without checks",
        "pattern": r'return\s+["\']PASS["\']',
        "context_check": lambda line: "if" not in line.lower(),
        "severity": "HIGH",
        "file_types": [".py"]
    },
    {
        "id": "AP006",
        "name": "Exit 0 unconditional",
        "description": "Script always exits with success",
        "pattern": r'exit\s+0',
        "context_check": lambda content: content.count("exit 0") > 0 and content.count("exit 1") == 0,
        "severity": "MEDIUM",
        "file_types": [".ps1"],
        "full_file_check": True
    },
    {
        "id": "AP007",
        "name": "sys.exit(0) unconditional",
        "description": "Python script always exits with success",
        "pattern": r'sys\.exit\(0\)',
        "context_check": lambda content: content.count("sys.exit(0)") > 0 and content.count("sys.exit(1)") == 0,
        "severity": "MEDIUM",
        "file_types": [".py"],
        "full_file_check": True
    }
]


def load_custom_anti_patterns():
    """Load custom anti-patterns from patterns file."""
    root = get_test_version_root()
    patterns_file = root / "ORGANS" / "SCHOLA_IMPERIALIS" / "PATTERNS" / "anti_patterns.json"
    
    if not patterns_file.exists():
        return []
    
    data = load_json_safe(patterns_file)
    if not data:
        return []
    
    return data.get("anti_patterns", [])


def scan_file(filepath, anti_patterns):
    """Scan a single file for anti-patterns."""
    violations = []
    
    try:
        with open(filepath, "r", encoding="utf-8-sig") as f:
            content = f.read()
            lines = content.split("\n")
    except:
        return violations
    
    suffix = filepath.suffix.lower()
    
    for ap in anti_patterns:
        # Check file type
        if "file_types" in ap and suffix not in ap["file_types"]:
            continue
        
        # Full file check
        if ap.get("full_file_check"):
            if re.search(ap["pattern"], content):
                if "context_check" in ap:
                    if ap["context_check"](content):
                        violations.append({
                            "file": str(filepath),
                            "anti_pattern": ap["id"],
                            "name": ap["name"],
                            "severity": ap["severity"],
                            "line": None,
                            "description": ap["description"]
                        })
                else:
                    violations.append({
                        "file": str(filepath),
                        "anti_pattern": ap["id"],
                        "name": ap["name"],
                        "severity": ap["severity"],
                        "line": None,
                        "description": ap["description"]
                    })
            continue
        
        # Line-by-line check
        for i, line in enumerate(lines, 1):
            if re.search(ap["pattern"], line):
                # Context check
                if "context_check" in ap:
                    if not ap["context_check"](line):
                        continue
                
                violations.append({
                    "file": str(filepath),
                    "anti_pattern": ap["id"],
                    "name": ap["name"],
                    "severity": ap["severity"],
                    "line": i,
                    "content": line.strip()[:100],
                    "description": ap["description"]
                })
    
    return violations


def scan_directory(path, anti_patterns):
    """Scan directory for anti-patterns."""
    all_violations = []
    files_scanned = 0
    
    for ext in [".py", ".ps1", ".json"]:
        for filepath in path.rglob(f"*{ext}"):
            # Skip certain directories
            if any(skip in str(filepath) for skip in ["__pycache__", ".git", "node_modules"]):
                continue
            
            violations = scan_file(filepath, anti_patterns)
            all_violations.extend(violations)
            files_scanned += 1
    
    return all_violations, files_scanned


def main():
    parser = argparse.ArgumentParser(description="Scan for anti-patterns")
    parser.add_argument("--path", help="Path to scan (relative to test version root)")
    parser.add_argument("--output", help="Output file for report")
    args = parser.parse_args()
    
    print("=" * 60)
    print("ANTI-PATTERN SCANNER")
    print("=" * 60)
    print()
    
    root = get_test_version_root()
    
    # Determine scan path
    if args.path:
        scan_path = root / args.path
    else:
        scan_path = root
    
    print(f"Scanning: {scan_path}")
    print()
    
    # Load anti-patterns
    anti_patterns = BUILTIN_ANTI_PATTERNS.copy()
    custom = load_custom_anti_patterns()
    print(f"Built-in patterns: {len(BUILTIN_ANTI_PATTERNS)}")
    print(f"Custom patterns: {len(custom)}")
    
    # Note: Custom patterns from lessons are informational, not regex-based
    # They're tracked separately
    
    print()
    
    # Scan
    print("Scanning files...")
    violations, files_scanned = scan_directory(scan_path, anti_patterns)
    print(f"Files scanned: {files_scanned}")
    print(f"Violations found: {len(violations)}")
    print()
    
    # Group by severity
    by_severity = {"HIGH": [], "MEDIUM": [], "LOW": []}
    for v in violations:
        by_severity[v["severity"]].append(v)
    
    # Print results
    if violations:
        print("VIOLATIONS:")
        for severity in ["HIGH", "MEDIUM", "LOW"]:
            if by_severity[severity]:
                print(f"\n  {severity} ({len(by_severity[severity])}):")
                for v in by_severity[severity][:10]:  # Top 10 per severity
                    rel_path = Path(v["file"]).relative_to(root)
                    line_info = f":{v['line']}" if v["line"] else ""
                    print(f"    [{v['anti_pattern']}] {rel_path}{line_info}")
                    print(f"        {v['name']}")
                if len(by_severity[severity]) > 10:
                    print(f"        ... and {len(by_severity[severity]) - 10} more")
    else:
        print("No violations found! ✅")
    
    print()
    
    # Build report
    report = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "scan_path": str(scan_path.relative_to(root)),
        "files_scanned": files_scanned,
        "summary": {
            "total_violations": len(violations),
            "high": len(by_severity["HIGH"]),
            "medium": len(by_severity["MEDIUM"]),
            "low": len(by_severity["LOW"])
        },
        "violations": violations,
        "verdict": "FAIL" if by_severity["HIGH"] else "PARTIAL" if violations else "PASS"
    }
    
    # Save report
    output_dir = root / "ORGANS" / "SCHOLA_IMPERIALIS" / "REPORTS"
    output_dir.mkdir(parents=True, exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    report_path = output_dir / f"anti_pattern_scan_{timestamp}.json"
    
    with open(report_path, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)
    print(f"Report: {report_path}")
    
    # Save latest
    latest_path = output_dir / "latest_anti_pattern_scan.json"
    with open(latest_path, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)
    print(f"Latest: {latest_path}")
    
    print()
    print(f"VERDICT: {report['verdict']}")
    
    return 0 if report["verdict"] == "PASS" else 1


if __name__ == "__main__":
    sys.exit(main())
