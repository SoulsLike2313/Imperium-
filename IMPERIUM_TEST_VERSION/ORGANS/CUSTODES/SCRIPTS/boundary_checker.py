#!/usr/bin/env python3
"""
CUSTODES - Boundary Checker
Manages boundaries, safety, access policy, and private/public split.
"""

import json
import re
from datetime import datetime
from pathlib import Path
from typing import List, Optional

POLICIES_DIR = Path(__file__).parent.parent / "POLICIES"
VIOLATIONS_DIR = POLICIES_DIR / "VIOLATIONS"
ACCESS_LOG_DIR = POLICIES_DIR / "ACCESS_LOG"


def ensure_dirs():
    """Ensure policy directories exist."""
    for d in [POLICIES_DIR, VIOLATIONS_DIR, ACCESS_LOG_DIR]:
        d.mkdir(parents=True, exist_ok=True)


# Default boundaries
PRIVATE_ZONES = [
    r".*IMPERIUM_TEST_VERSION.*",
    r".*\.env$",
    r".*credentials.*",
    r".*secrets.*",
    r".*\.pem$",
    r".*\.key$",
    r".*password.*",
]

PUBLIC_ZONES = [
    r".*\.md$",
    r".*\.json$",
    r".*\.py$",
    r".*schemas.*",
    r".*REGISTRY.*",
]

FORBIDDEN_PATTERNS = [
    r"password\s*=\s*['\"].*['\"]",
    r"api_key\s*=\s*['\"].*['\"]",
    r"secret\s*=\s*['\"].*['\"]",
    r"token\s*=\s*['\"].*['\"]",
]


def is_private_zone(path: str) -> bool:
    """Check if a path is in a private zone."""
    for pattern in PRIVATE_ZONES:
        if re.match(pattern, path, re.IGNORECASE):
            return True
    return False


def is_public_zone(path: str) -> bool:
    """Check if a path is in a public zone."""
    for pattern in PUBLIC_ZONES:
        if re.match(pattern, path, re.IGNORECASE):
            return True
    return False


def check_for_secrets(content: str) -> List[dict]:
    """Check content for potential secrets."""
    violations = []
    lines = content.split('\n')
    
    for i, line in enumerate(lines, 1):
        for pattern in FORBIDDEN_PATTERNS:
            if re.search(pattern, line, re.IGNORECASE):
                violations.append({
                    "line": i,
                    "pattern": pattern,
                    "content": line[:100] + "..." if len(line) > 100 else line
                })
    
    return violations


def log_access(actor: str, resource: str, action: str, allowed: bool) -> dict:
    """Log an access attempt."""
    ensure_dirs()
    
    log_id = f"ACC-{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}"
    log_entry = {
        "log_id": log_id,
        "actor": actor,
        "resource": resource,
        "action": action,
        "allowed": allowed,
        "timestamp": datetime.now().isoformat()
    }
    
    filepath = ACCESS_LOG_DIR / f"{log_id}.json"
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(log_entry, f, indent=2, ensure_ascii=False)
    
    return log_entry


def record_violation(violation_type: str, resource: str, details: dict) -> dict:
    """Record a boundary violation."""
    ensure_dirs()
    
    violation_id = f"VIO-{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    violation = {
        "violation_id": violation_id,
        "type": violation_type,
        "resource": resource,
        "details": details,
        "timestamp": datetime.now().isoformat(),
        "resolved": False,
        "resolved_at": None
    }
    
    filepath = VIOLATIONS_DIR / f"{violation_id}.json"
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(violation, f, indent=2, ensure_ascii=False)
    
    return violation


def check_boundary_crossing(source: str, destination: str) -> dict:
    """Check if a boundary crossing is allowed."""
    source_private = is_private_zone(source)
    dest_private = is_private_zone(destination)
    
    result = {
        "source": source,
        "destination": destination,
        "source_private": source_private,
        "dest_private": dest_private,
        "allowed": True,
        "reason": None
    }
    
    # Private to public is not allowed without explicit approval
    if source_private and not dest_private:
        result["allowed"] = False
        result["reason"] = "Cannot copy from private to public zone without approval"
    
    return result


def scan_file_for_violations(filepath: str) -> dict:
    """Scan a file for boundary violations."""
    path = Path(filepath)
    
    result = {
        "filepath": filepath,
        "exists": path.exists(),
        "is_private": is_private_zone(filepath),
        "violations": [],
        "verdict": "PASS"
    }
    
    if not path.exists():
        result["verdict"] = "SKIP"
        return result
    
    try:
        with open(path, "r", encoding="utf-8", errors="ignore") as f:
            content = f.read()
        
        # Check for secrets
        secret_violations = check_for_secrets(content)
        if secret_violations:
            result["violations"].extend([
                {"type": "SECRET_DETECTED", **v} for v in secret_violations
            ])
        
        # Check for private paths in public files
        if not result["is_private"]:
            for pattern in PRIVATE_ZONES:
                matches = re.findall(pattern, content, re.IGNORECASE)
                if matches:
                    result["violations"].append({
                        "type": "PRIVATE_PATH_IN_PUBLIC",
                        "pattern": pattern,
                        "matches": matches[:5]  # Limit to 5
                    })
        
        if result["violations"]:
            result["verdict"] = "FAIL"
            
    except Exception as e:
        result["error"] = str(e)
        result["verdict"] = "ERROR"
    
    return result


def get_violation_stats() -> dict:
    """Get violation statistics."""
    ensure_dirs()
    
    violations = list(VIOLATIONS_DIR.glob("VIO-*.json"))
    resolved = 0
    unresolved = 0
    by_type = {}
    
    for f in violations:
        with open(f, "r", encoding="utf-8") as fp:
            v = json.load(fp)
            if v["resolved"]:
                resolved += 1
            else:
                unresolved += 1
            vtype = v["type"]
            by_type[vtype] = by_type.get(vtype, 0) + 1
    
    return {
        "total": len(violations),
        "resolved": resolved,
        "unresolved": unresolved,
        "by_type": by_type
    }


def get_access_stats() -> dict:
    """Get access log statistics."""
    ensure_dirs()
    
    logs = list(ACCESS_LOG_DIR.glob("ACC-*.json"))
    allowed = 0
    denied = 0
    
    for f in logs:
        with open(f, "r", encoding="utf-8") as fp:
            log = json.load(fp)
            if log["allowed"]:
                allowed += 1
            else:
                denied += 1
    
    return {
        "total": len(logs),
        "allowed": allowed,
        "denied": denied
    }


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Custodes Boundary Checker")
    parser.add_argument("--action", choices=["stats", "scan", "check-crossing", "violations"],
                        default="stats", help="Action to perform")
    parser.add_argument("--file", help="File to scan")
    parser.add_argument("--source", help="Source path for crossing check")
    parser.add_argument("--dest", help="Destination path for crossing check")
    args = parser.parse_args()
    
    if args.action == "stats":
        v_stats = get_violation_stats()
        a_stats = get_access_stats()
        
        print("=" * 50)
        print("CUSTODES BOUNDARY CHECKER - STATISTICS")
        print("=" * 50)
        print("\nViolations:")
        print(f"  Total: {v_stats['total']}")
        print(f"  Resolved: {v_stats['resolved']}")
        print(f"  Unresolved: {v_stats['unresolved']}")
        if v_stats["by_type"]:
            print("  By Type:")
            for vtype, count in v_stats["by_type"].items():
                print(f"    {vtype}: {count}")
        
        print("\nAccess Log:")
        print(f"  Total: {a_stats['total']}")
        print(f"  Allowed: {a_stats['allowed']}")
        print(f"  Denied: {a_stats['denied']}")
        
    elif args.action == "scan":
        if not args.file:
            print("ERROR: --file required")
            return
        result = scan_file_for_violations(args.file)
        print(f"File: {result['filepath']}")
        print(f"Private zone: {result['is_private']}")
        print(f"Verdict: {result['verdict']}")
        if result["violations"]:
            print("Violations:")
            for v in result["violations"]:
                print(f"  - {v['type']}")
                
    elif args.action == "check-crossing":
        if not args.source or not args.dest:
            print("ERROR: --source and --dest required")
            return
        result = check_boundary_crossing(args.source, args.dest)
        print(f"Source: {result['source']} (private: {result['source_private']})")
        print(f"Dest: {result['destination']} (private: {result['dest_private']})")
        print(f"Allowed: {result['allowed']}")
        if result["reason"]:
            print(f"Reason: {result['reason']}")
            
    elif args.action == "violations":
        stats = get_violation_stats()
        print("=" * 50)
        print("UNRESOLVED VIOLATIONS")
        print("=" * 50)
        for f in VIOLATIONS_DIR.glob("VIO-*.json"):
            with open(f, "r", encoding="utf-8") as fp:
                v = json.load(fp)
                if not v["resolved"]:
                    print(f"\n[{v['violation_id']}]")
                    print(f"  Type: {v['type']}")
                    print(f"  Resource: {v['resource']}")
                    print(f"  Time: {v['timestamp']}")


if __name__ == "__main__":
    main()
