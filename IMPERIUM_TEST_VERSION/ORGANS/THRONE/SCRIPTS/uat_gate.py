#!/usr/bin/env python3
"""
UAT GATE
Owner User Acceptance Testing gate for promotion.

This script manages the UAT approval process:
1. Displays pending UAT requests
2. Allows Owner to approve/reject
3. Records decision with audit trail

Usage:
    py -3 uat_gate.py --list                     # List pending requests
    py -3 uat_gate.py --approve <request_id>     # Approve request
    py -3 uat_gate.py --reject <request_id>      # Reject request
    py -3 uat_gate.py --status                   # Show UAT status
"""

import argparse
import json
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


def get_promotion_dir():
    """Get promotion directory."""
    return get_test_version_root() / "ORGANS" / "THRONE" / "PROMOTION"


def list_pending_requests():
    """List all pending UAT requests."""
    promotion_dir = get_promotion_dir()
    
    if not promotion_dir.exists():
        return []
    
    pending = []
    for req_file in promotion_dir.glob("UAT_REQUEST_*.json"):
        req = load_json_safe(req_file)
        if req and req.get("approval_status") == "PENDING":
            pending.append({
                "file": req_file,
                "request": req
            })
    
    return sorted(pending, key=lambda x: x["request"].get("timestamp", ""), reverse=True)


def approve_request(request_id, notes=None):
    """Approve a UAT request."""
    promotion_dir = get_promotion_dir()
    
    # Find request
    request_file = None
    for f in promotion_dir.glob("UAT_REQUEST_*.json"):
        req = load_json_safe(f)
        if req and req.get("request_id") == request_id:
            request_file = f
            break
    
    if not request_file:
        print(f"❌ Request not found: {request_id}")
        return False
    
    # Load and update request
    req = load_json_safe(request_file)
    req["approval_status"] = "APPROVED"
    req["owner_decision"] = "APPROVED"
    req["owner_notes"] = notes
    req["decision_timestamp"] = datetime.now(timezone.utc).isoformat()
    
    # Save updated request
    with open(request_file, "w", encoding="utf-8") as f:
        json.dump(req, f, indent=2)
    
    # Create UAT_APPROVAL.json
    approval = {
        "request_id": request_id,
        "approval_status": "APPROVED",
        "owner_decision": "APPROVED",
        "owner_notes": notes,
        "decision_timestamp": datetime.now(timezone.utc).isoformat(),
        "preflight_status": req.get("preflight_status"),
        "components_approved": [c["organ_id"] for c in req.get("components_for_promotion", [])]
    }
    
    approval_path = promotion_dir / "UAT_APPROVAL.json"
    with open(approval_path, "w", encoding="utf-8") as f:
        json.dump(approval, f, indent=2)
    
    print(f"✅ Request approved: {request_id}")
    print(f"Approval file: {approval_path}")
    
    # Create receipt
    receipt = {
        "receipt_id": f"RCP-UAT-{datetime.now().strftime('%Y%m%d_%H%M%S')}",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "action": "uat_approval",
        "request_id": request_id,
        "decision": "APPROVED",
        "notes": notes,
        "verdict": "PASS"
    }
    
    receipts_dir = get_test_version_root() / "RECEIPTS"
    receipt_path = receipts_dir / f"{receipt['receipt_id']}.json"
    with open(receipt_path, "w", encoding="utf-8") as f:
        json.dump(receipt, f, indent=2)
    
    print(f"Receipt: {receipt_path}")
    
    return True


def reject_request(request_id, reason=None):
    """Reject a UAT request."""
    promotion_dir = get_promotion_dir()
    
    # Find request
    request_file = None
    for f in promotion_dir.glob("UAT_REQUEST_*.json"):
        req = load_json_safe(f)
        if req and req.get("request_id") == request_id:
            request_file = f
            break
    
    if not request_file:
        print(f"❌ Request not found: {request_id}")
        return False
    
    # Load and update request
    req = load_json_safe(request_file)
    req["approval_status"] = "REJECTED"
    req["owner_decision"] = "REJECTED"
    req["owner_notes"] = reason
    req["decision_timestamp"] = datetime.now(timezone.utc).isoformat()
    
    # Save updated request
    with open(request_file, "w", encoding="utf-8") as f:
        json.dump(req, f, indent=2)
    
    print(f"❌ Request rejected: {request_id}")
    if reason:
        print(f"Reason: {reason}")
    
    # Create receipt
    receipt = {
        "receipt_id": f"RCP-UAT-{datetime.now().strftime('%Y%m%d_%H%M%S')}",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "action": "uat_rejection",
        "request_id": request_id,
        "decision": "REJECTED",
        "reason": reason,
        "verdict": "FAIL"
    }
    
    receipts_dir = get_test_version_root() / "RECEIPTS"
    receipt_path = receipts_dir / f"{receipt['receipt_id']}.json"
    with open(receipt_path, "w", encoding="utf-8") as f:
        json.dump(receipt, f, indent=2)
    
    print(f"Receipt: {receipt_path}")
    
    return True


def show_status():
    """Show UAT gate status."""
    promotion_dir = get_promotion_dir()
    
    print("=" * 60)
    print("UAT GATE STATUS")
    print("=" * 60)
    print()
    
    # Current approval
    approval_path = promotion_dir / "UAT_APPROVAL.json"
    if approval_path.exists():
        approval = load_json_safe(approval_path)
        if approval:
            print("CURRENT APPROVAL:")
            print(f"  Request: {approval.get('request_id')}")
            print(f"  Status: {approval.get('approval_status')}")
            print(f"  Decision: {approval.get('owner_decision')}")
            print(f"  Timestamp: {approval.get('decision_timestamp')}")
            if approval.get("owner_notes"):
                print(f"  Notes: {approval['owner_notes']}")
            print()
    else:
        print("CURRENT APPROVAL: None")
        print()
    
    # Pending requests
    pending = list_pending_requests()
    print(f"PENDING REQUESTS: {len(pending)}")
    for p in pending:
        req = p["request"]
        print(f"  - {req.get('request_id')}")
        print(f"    Preflight: {req.get('preflight_status')}")
        print(f"    Components: {len(req.get('components_for_promotion', []))}")
        print(f"    Timestamp: {req.get('timestamp')}")
    
    if not pending:
        print("  None")
    
    print()
    
    # All requests
    all_requests = list(promotion_dir.glob("UAT_REQUEST_*.json")) if promotion_dir.exists() else []
    approved = sum(1 for f in all_requests if load_json_safe(f) and load_json_safe(f).get("approval_status") == "APPROVED")
    rejected = sum(1 for f in all_requests if load_json_safe(f) and load_json_safe(f).get("approval_status") == "REJECTED")
    
    print("HISTORY:")
    print(f"  Total requests: {len(all_requests)}")
    print(f"  Approved: {approved}")
    print(f"  Rejected: {rejected}")
    print(f"  Pending: {len(pending)}")


def main():
    parser = argparse.ArgumentParser(description="UAT gate management")
    parser.add_argument("--list", action="store_true", help="List pending requests")
    parser.add_argument("--approve", metavar="REQUEST_ID", help="Approve a request")
    parser.add_argument("--reject", metavar="REQUEST_ID", help="Reject a request")
    parser.add_argument("--notes", help="Notes for approval/rejection")
    parser.add_argument("--status", action="store_true", help="Show UAT status")
    args = parser.parse_args()
    
    if args.list:
        pending = list_pending_requests()
        print("=" * 60)
        print("PENDING UAT REQUESTS")
        print("=" * 60)
        print()
        
        if pending:
            for p in pending:
                req = p["request"]
                print(f"Request: {req.get('request_id')}")
                print(f"  Timestamp: {req.get('timestamp')}")
                print(f"  Preflight: {req.get('preflight_status')}")
                print(f"  Components: {len(req.get('components_for_promotion', []))}")
                print()
        else:
            print("No pending requests")
        
        return 0
    
    elif args.approve:
        success = approve_request(args.approve, args.notes)
        return 0 if success else 1
    
    elif args.reject:
        success = reject_request(args.reject, args.notes)
        return 0 if success else 1
    
    elif args.status:
        show_status()
        return 0
    
    else:
        show_status()
        return 0


if __name__ == "__main__":
    sys.exit(main())
