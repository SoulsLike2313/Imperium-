#!/usr/bin/env python3
"""
PROMOTION WORKFLOW
Manages the promotion of test version components to canon.

Workflow:
1. Pre-flight checks (all tests pass, no fake green)
2. Owner UAT gate (requires explicit approval)
3. Bundle creation (package for transfer)
4. Canon import (with full audit trail)

Usage:
    py -3 promotion_workflow.py --check          # Run pre-flight checks
    py -3 promotion_workflow.py --bundle         # Create promotion bundle
    py -3 promotion_workflow.py --status         # Show promotion status
"""

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
import shutil


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


def check_preflight():
    """Run pre-flight checks for promotion."""
    root = get_test_version_root()
    checks = []
    
    print("Running pre-flight checks...")
    print()
    
    # Check 1: Latest master receipt
    receipts_dir = root / "RECEIPTS"
    master_receipts = sorted(receipts_dir.glob("RCP-MASTER-*.json"), reverse=True)
    
    if master_receipts:
        latest = load_json_safe(master_receipts[0])
        if latest:
            verdict = latest.get("overall_verdict", "UNKNOWN")
            checks.append({
                "check": "master_receipt",
                "status": "PASS" if verdict == "PASS" else "FAIL",
                "details": f"Latest master receipt: {verdict}"
            })
            print(f"  {'✅' if verdict == 'PASS' else '❌'} Master receipt: {verdict}")
        else:
            checks.append({"check": "master_receipt", "status": "FAIL", "details": "Cannot read receipt"})
            print("  ❌ Master receipt: Cannot read")
    else:
        checks.append({"check": "master_receipt", "status": "FAIL", "details": "No master receipt found"})
        print("  ❌ Master receipt: Not found")
    
    # Check 2: Smoke test
    smoke_report = load_json_safe(root / "TESTING_FIELD" / "SMOKE_RESULTS" / "latest_smoke_report.json")
    if smoke_report:
        verdict = smoke_report.get("summary", {}).get("verdict", "UNKNOWN")
        checks.append({
            "check": "smoke_test",
            "status": "PASS" if verdict == "PASS" else "PARTIAL" if verdict == "PARTIAL" else "FAIL",
            "details": f"Smoke test: {verdict}"
        })
        print(f"  {'✅' if verdict == 'PASS' else '⚠️' if verdict == 'PARTIAL' else '❌'} Smoke test: {verdict}")
    else:
        checks.append({"check": "smoke_test", "status": "FAIL", "details": "No smoke report"})
        print("  ❌ Smoke test: No report")
    
    # Check 3: Audit (no fake green)
    audit_report = load_json_safe(root / "ORGANS" / "INQUISITION" / "REPORTS" / "latest_audit.json")
    if audit_report:
        fake_green = audit_report.get("summary", {}).get("fake_green_count", 0)
        checks.append({
            "check": "fake_green",
            "status": "PASS" if fake_green == 0 else "FAIL",
            "details": f"Fake green count: {fake_green}"
        })
        print(f"  {'✅' if fake_green == 0 else '❌'} Fake green: {fake_green}")
    else:
        checks.append({"check": "fake_green", "status": "UNKNOWN", "details": "No audit report"})
        print("  ❓ Fake green: No audit report")
    
    # Check 4: Registry sync
    registry_sync = load_json_safe(root / "REPORTS" / "drift_report.json")
    if registry_sync:
        verdict = registry_sync.get("verdict", "UNKNOWN")
        checks.append({
            "check": "registry_sync",
            "status": "PASS" if verdict == "PASS" else "FAIL",
            "details": f"Registry sync: {verdict}"
        })
        print(f"  {'✅' if verdict == 'PASS' else '❌'} Registry sync: {verdict}")
    else:
        checks.append({"check": "registry_sync", "status": "UNKNOWN", "details": "No drift report"})
        print("  ❓ Registry sync: No drift report")
    
    # Check 5: All organs have contracts
    organs_dir = root / "ORGANS"
    organs_ok = 0
    organs_total = 0
    for organ_dir in organs_dir.iterdir():
        if organ_dir.is_dir():
            organs_total += 1
            if (organ_dir / "ORGAN_CONTRACT.json").exists():
                organs_ok += 1
    
    checks.append({
        "check": "organ_contracts",
        "status": "PASS" if organs_ok == organs_total else "PARTIAL",
        "details": f"Organ contracts: {organs_ok}/{organs_total}"
    })
    print(f"  {'✅' if organs_ok == organs_total else '⚠️'} Organ contracts: {organs_ok}/{organs_total}")
    
    print()
    
    # Overall
    statuses = [c["status"] for c in checks]
    if "FAIL" in statuses:
        overall = "FAIL"
    elif "PARTIAL" in statuses or "UNKNOWN" in statuses:
        overall = "PARTIAL"
    else:
        overall = "PASS"
    
    return {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "checks": checks,
        "overall": overall,
        "ready_for_promotion": overall == "PASS"
    }


def check_uat_approval():
    """Check if Owner UAT approval exists."""
    root = get_test_version_root()
    approval_file = root / "ORGANS" / "THRONE" / "PROMOTION" / "UAT_APPROVAL.json"
    
    if not approval_file.exists():
        return None
    
    return load_json_safe(approval_file)


def create_uat_request():
    """Create UAT approval request."""
    root = get_test_version_root()
    
    # Run preflight
    preflight = check_preflight()
    
    request = {
        "request_id": f"UAT-{datetime.now().strftime('%Y%m%d_%H%M%S')}",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "type": "UAT_APPROVAL_REQUEST",
        "preflight_status": preflight["overall"],
        "preflight_checks": preflight["checks"],
        "components_for_promotion": [],
        "approval_status": "PENDING",
        "owner_decision": None,
        "owner_notes": None
    }
    
    # List components for promotion
    organs_dir = root / "ORGANS"
    for organ_dir in organs_dir.iterdir():
        if organ_dir.is_dir():
            contract = load_json_safe(organ_dir / "ORGAN_CONTRACT.json")
            if contract:
                request["components_for_promotion"].append({
                    "organ_id": organ_dir.name,
                    "status": contract.get("status", "UNKNOWN"),
                    "has_scripts": (organ_dir / "SCRIPTS").exists(),
                    "has_dashboard": (organ_dir / "DASHBOARD").exists()
                })
    
    # Save request
    request_dir = root / "ORGANS" / "THRONE" / "PROMOTION"
    request_dir.mkdir(parents=True, exist_ok=True)
    
    request_path = request_dir / f"UAT_REQUEST_{request['request_id']}.json"
    with open(request_path, "w", encoding="utf-8") as f:
        json.dump(request, f, indent=2)
    
    return request, request_path


def create_promotion_bundle():
    """Create promotion bundle for canon import."""
    root = get_test_version_root()
    
    # Check UAT approval
    approval = check_uat_approval()
    if not approval or approval.get("approval_status") != "APPROVED":
        print("❌ UAT approval required before creating bundle")
        return None
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    bundle_name = f"PROMOTION_BUNDLE_{timestamp}"
    bundle_dir = root / "ORGANS" / "THRONE" / "PROMOTION" / bundle_name
    bundle_dir.mkdir(parents=True, exist_ok=True)
    
    print(f"Creating promotion bundle: {bundle_name}")
    print()
    
    # Copy key components
    components = []
    
    # 1. Organs
    organs_src = root / "ORGANS"
    organs_dst = bundle_dir / "ORGANS"
    if organs_src.exists():
        shutil.copytree(organs_src, organs_dst, dirs_exist_ok=True)
        components.append("ORGANS")
        print("  ✅ Copied ORGANS")
    
    # 2. Registry
    registry_src = root / "REGISTRY"
    registry_dst = bundle_dir / "REGISTRY"
    if registry_src.exists():
        shutil.copytree(registry_src, registry_dst, dirs_exist_ok=True)
        components.append("REGISTRY")
        print("  ✅ Copied REGISTRY")
    
    # 3. Schemas
    schemas_src = root / "schemas"
    schemas_dst = bundle_dir / "schemas"
    if schemas_src.exists():
        shutil.copytree(schemas_src, schemas_dst, dirs_exist_ok=True)
        components.append("schemas")
        print("  ✅ Copied schemas")
    
    # 4. Truth Spine
    truth_src = root / "TRUTH_SPINE"
    truth_dst = bundle_dir / "TRUTH_SPINE"
    if truth_src.exists():
        shutil.copytree(truth_src, truth_dst, dirs_exist_ok=True)
        components.append("TRUTH_SPINE")
        print("  ✅ Copied TRUTH_SPINE")
    
    # Create bundle manifest
    manifest = {
        "bundle_id": bundle_name,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "uat_approval": approval,
        "components": components,
        "source": "IMPERIUM_TEST_VERSION",
        "target": "IMPERIUM (canon)",
        "status": "READY_FOR_IMPORT"
    }
    
    manifest_path = bundle_dir / "BUNDLE_MANIFEST.json"
    with open(manifest_path, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2)
    
    print()
    print(f"Bundle created: {bundle_dir}")
    print(f"Components: {len(components)}")
    
    return manifest, bundle_dir


def show_status():
    """Show current promotion status."""
    root = get_test_version_root()
    
    print("=" * 60)
    print("PROMOTION STATUS")
    print("=" * 60)
    print()
    
    # Pre-flight status
    print("PRE-FLIGHT:")
    preflight = check_preflight()
    print(f"  Overall: {preflight['overall']}")
    print(f"  Ready for promotion: {'Yes' if preflight['ready_for_promotion'] else 'No'}")
    print()
    
    # UAT status
    print("UAT APPROVAL:")
    approval = check_uat_approval()
    if approval:
        print(f"  Status: {approval.get('approval_status', 'UNKNOWN')}")
        print(f"  Decision: {approval.get('owner_decision', 'N/A')}")
        if approval.get("owner_notes"):
            print(f"  Notes: {approval['owner_notes']}")
    else:
        print("  Status: NOT_REQUESTED")
    print()
    
    # Pending requests
    print("PENDING REQUESTS:")
    promotion_dir = root / "ORGANS" / "THRONE" / "PROMOTION"
    requests = list(promotion_dir.glob("UAT_REQUEST_*.json")) if promotion_dir.exists() else []
    if requests:
        for req_file in sorted(requests, reverse=True)[:3]:
            req = load_json_safe(req_file)
            if req:
                print(f"  - {req.get('request_id')}: {req.get('approval_status')}")
    else:
        print("  None")
    print()
    
    # Bundles
    print("PROMOTION BUNDLES:")
    bundles = [d for d in promotion_dir.iterdir() if d.is_dir() and d.name.startswith("PROMOTION_BUNDLE")] if promotion_dir.exists() else []
    if bundles:
        for bundle in sorted(bundles, reverse=True)[:3]:
            manifest = load_json_safe(bundle / "BUNDLE_MANIFEST.json")
            if manifest:
                print(f"  - {manifest.get('bundle_id')}: {manifest.get('status')}")
    else:
        print("  None")
    
    return preflight


def main():
    parser = argparse.ArgumentParser(description="Promotion workflow management")
    parser.add_argument("--check", action="store_true", help="Run pre-flight checks")
    parser.add_argument("--request-uat", action="store_true", help="Create UAT approval request")
    parser.add_argument("--bundle", action="store_true", help="Create promotion bundle")
    parser.add_argument("--status", action="store_true", help="Show promotion status")
    args = parser.parse_args()
    
    print("=" * 60)
    print("PROMOTION WORKFLOW")
    print("=" * 60)
    print()
    
    if args.check:
        result = check_preflight()
        print(f"OVERALL: {result['overall']}")
        print(f"Ready for promotion: {'Yes' if result['ready_for_promotion'] else 'No'}")
        
        # Save result
        root = get_test_version_root()
        output_dir = root / "ORGANS" / "THRONE" / "PROMOTION"
        output_dir.mkdir(parents=True, exist_ok=True)
        
        output_path = output_dir / "latest_preflight.json"
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(result, f, indent=2)
        print(f"Report: {output_path}")
        
        return 0 if result["ready_for_promotion"] else 1
    
    elif args.request_uat:
        request, path = create_uat_request()
        print()
        print(f"UAT request created: {path}")
        print()
        print("NEXT STEPS:")
        print("  1. Owner reviews the request")
        print("  2. Owner creates UAT_APPROVAL.json with decision")
        print("  3. Run --bundle to create promotion bundle")
        return 0
    
    elif args.bundle:
        result = create_promotion_bundle()
        if result:
            print()
            print("VERDICT: PASS")
            return 0
        else:
            print()
            print("VERDICT: FAIL")
            return 1
    
    elif args.status:
        show_status()
        return 0
    
    else:
        # Default: show status
        show_status()
        return 0


if __name__ == "__main__":
    sys.exit(main())
