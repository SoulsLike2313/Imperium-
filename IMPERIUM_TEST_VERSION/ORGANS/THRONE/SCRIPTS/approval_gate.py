#!/usr/bin/env python3
"""
THRONE - Approval Gate
Manages Owner approval requests and decisions.
"""

import json
import os
import sys
from datetime import datetime
from pathlib import Path

APPROVALS_DIR = Path(__file__).parent.parent / "APPROVALS"
PENDING_DIR = APPROVALS_DIR / "PENDING"
APPROVED_DIR = APPROVALS_DIR / "APPROVED"
REJECTED_DIR = APPROVALS_DIR / "REJECTED"


def ensure_dirs():
    """Ensure approval directories exist."""
    for d in [APPROVALS_DIR, PENDING_DIR, APPROVED_DIR, REJECTED_DIR]:
        d.mkdir(parents=True, exist_ok=True)


def create_approval_request(action: str, scope: str, risk_level: str, 
                            requester: str = "Agent", evidence: dict = None) -> dict:
    """Create a new approval request."""
    ensure_dirs()
    
    request_id = f"REQ-{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    request = {
        "request_id": request_id,
        "requester": requester,
        "action": action,
        "scope": scope,
        "risk_level": risk_level,
        "evidence": evidence or {},
        "status": "PENDING",
        "created_at": datetime.now().isoformat(),
        "decision": None,
        "decided_at": None,
        "approver": None,
        "notes": None
    }
    
    filepath = PENDING_DIR / f"{request_id}.json"
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(request, f, indent=2, ensure_ascii=False)
    
    return request


def list_pending_requests() -> list:
    """List all pending approval requests."""
    ensure_dirs()
    requests = []
    for f in PENDING_DIR.glob("REQ-*.json"):
        with open(f, "r", encoding="utf-8") as fp:
            requests.append(json.load(fp))
    return sorted(requests, key=lambda x: x["created_at"])


def approve_request(request_id: str, approver: str = "Owner", notes: str = None) -> dict:
    """Approve a pending request."""
    ensure_dirs()
    
    pending_file = PENDING_DIR / f"{request_id}.json"
    if not pending_file.exists():
        raise ValueError(f"Request {request_id} not found in pending")
    
    with open(pending_file, "r", encoding="utf-8") as f:
        request = json.load(f)
    
    request["status"] = "APPROVED"
    request["decision"] = "APPROVED"
    request["decided_at"] = datetime.now().isoformat()
    request["approver"] = approver
    request["notes"] = notes
    
    approved_file = APPROVED_DIR / f"{request_id}.json"
    with open(approved_file, "w", encoding="utf-8") as f:
        json.dump(request, f, indent=2, ensure_ascii=False)
    
    pending_file.unlink()
    return request


def reject_request(request_id: str, approver: str = "Owner", 
                   reason: str = None, alternative: str = None) -> dict:
    """Reject a pending request."""
    ensure_dirs()
    
    pending_file = PENDING_DIR / f"{request_id}.json"
    if not pending_file.exists():
        raise ValueError(f"Request {request_id} not found in pending")
    
    with open(pending_file, "r", encoding="utf-8") as f:
        request = json.load(f)
    
    request["status"] = "REJECTED"
    request["decision"] = "REJECTED"
    request["decided_at"] = datetime.now().isoformat()
    request["approver"] = approver
    request["notes"] = reason
    request["alternative"] = alternative
    
    rejected_file = REJECTED_DIR / f"{request_id}.json"
    with open(rejected_file, "w", encoding="utf-8") as f:
        json.dump(request, f, indent=2, ensure_ascii=False)
    
    pending_file.unlink()
    return request


def check_approval_required(action: str, risk_level: str) -> bool:
    """Check if an action requires Owner approval."""
    high_risk_actions = [
        "delete", "commit", "push", "merge", "deploy",
        "modify_canon", "change_architecture", "mass_edit"
    ]
    
    if risk_level.upper() in ["HIGH", "CRITICAL"]:
        return True
    
    for hr_action in high_risk_actions:
        if hr_action in action.lower():
            return True
    
    return False


def get_approval_stats() -> dict:
    """Get approval statistics."""
    ensure_dirs()
    
    pending = len(list(PENDING_DIR.glob("REQ-*.json")))
    approved = len(list(APPROVED_DIR.glob("REQ-*.json")))
    rejected = len(list(REJECTED_DIR.glob("REQ-*.json")))
    
    return {
        "pending": pending,
        "approved": approved,
        "rejected": rejected,
        "total": pending + approved + rejected
    }


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Throne Approval Gate")
    parser.add_argument("--action", choices=["list", "stats", "create", "approve", "reject"],
                        default="stats", help="Action to perform")
    parser.add_argument("--request-id", help="Request ID for approve/reject")
    parser.add_argument("--create-action", help="Action description for new request")
    parser.add_argument("--scope", help="Scope for new request")
    parser.add_argument("--risk", default="MEDIUM", help="Risk level")
    parser.add_argument("--notes", help="Notes for decision")
    args = parser.parse_args()
    
    if args.action == "stats":
        stats = get_approval_stats()
        print("=" * 50)
        print("THRONE APPROVAL GATE - STATISTICS")
        print("=" * 50)
        print(f"Pending:  {stats['pending']}")
        print(f"Approved: {stats['approved']}")
        print(f"Rejected: {stats['rejected']}")
        print(f"Total:    {stats['total']}")
        
    elif args.action == "list":
        pending = list_pending_requests()
        print("=" * 50)
        print("PENDING APPROVAL REQUESTS")
        print("=" * 50)
        if not pending:
            print("No pending requests.")
        for req in pending:
            print(f"\n[{req['request_id']}]")
            print(f"  Action: {req['action']}")
            print(f"  Scope: {req['scope']}")
            print(f"  Risk: {req['risk_level']}")
            print(f"  Created: {req['created_at']}")
            
    elif args.action == "create":
        if not args.create_action or not args.scope:
            print("ERROR: --create-action and --scope required")
            sys.exit(1)
        req = create_approval_request(args.create_action, args.scope, args.risk)
        print(f"Created request: {req['request_id']}")
        
    elif args.action == "approve":
        if not args.request_id:
            print("ERROR: --request-id required")
            sys.exit(1)
        req = approve_request(args.request_id, notes=args.notes)
        print(f"Approved: {req['request_id']}")
        
    elif args.action == "reject":
        if not args.request_id:
            print("ERROR: --request-id required")
            sys.exit(1)
        req = reject_request(args.request_id, reason=args.notes)
        print(f"Rejected: {req['request_id']}")


if __name__ == "__main__":
    main()
