#!/usr/bin/env python3
"""
CANON IMPORT
Imports approved promotion bundles into canon repository.

This is the final step in the promotion workflow:
1. Validates bundle integrity
2. Checks UAT approval
3. Creates import manifest
4. Generates import instructions (actual import done by Owner on PC)

Usage:
    py -3 canon_import.py --validate <bundle_path>   # Validate bundle
    py -3 canon_import.py --prepare <bundle_path>    # Prepare import
    py -3 canon_import.py --list                     # List available bundles
"""

import argparse
import json
import hashlib
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


def calculate_file_hash(filepath):
    """Calculate SHA256 hash of a file."""
    sha256 = hashlib.sha256()
    try:
        with open(filepath, "rb") as f:
            for chunk in iter(lambda: f.read(8192), b""):
                sha256.update(chunk)
        return sha256.hexdigest()
    except:
        return None


def get_promotion_dir():
    """Get promotion directory."""
    return get_test_version_root() / "ORGANS" / "THRONE" / "PROMOTION"


def list_bundles():
    """List available promotion bundles."""
    promotion_dir = get_promotion_dir()
    
    if not promotion_dir.exists():
        return []
    
    bundles = []
    for bundle_dir in promotion_dir.iterdir():
        if bundle_dir.is_dir() and bundle_dir.name.startswith("PROMOTION_BUNDLE"):
            manifest = load_json_safe(bundle_dir / "BUNDLE_MANIFEST.json")
            if manifest:
                bundles.append({
                    "path": bundle_dir,
                    "manifest": manifest
                })
    
    return sorted(bundles, key=lambda x: x["manifest"].get("created_at", ""), reverse=True)


def validate_bundle(bundle_path):
    """Validate a promotion bundle."""
    bundle_dir = Path(bundle_path)
    
    if not bundle_dir.exists():
        return {"valid": False, "error": "Bundle not found"}
    
    # Check manifest
    manifest_path = bundle_dir / "BUNDLE_MANIFEST.json"
    if not manifest_path.exists():
        return {"valid": False, "error": "Missing BUNDLE_MANIFEST.json"}
    
    manifest = load_json_safe(manifest_path)
    if not manifest:
        return {"valid": False, "error": "Invalid manifest JSON"}
    
    # Check UAT approval
    uat_approval = manifest.get("uat_approval")
    if not uat_approval or uat_approval.get("approval_status") != "APPROVED":
        return {"valid": False, "error": "Missing or invalid UAT approval"}
    
    # Check components
    components = manifest.get("components", [])
    missing = []
    for comp in components:
        comp_path = bundle_dir / comp
        if not comp_path.exists():
            missing.append(comp)
    
    if missing:
        return {"valid": False, "error": f"Missing components: {missing}"}
    
    # Calculate integrity hashes
    hashes = {}
    file_count = 0
    for comp in components:
        comp_path = bundle_dir / comp
        if comp_path.is_dir():
            for f in comp_path.rglob("*"):
                if f.is_file():
                    rel_path = str(f.relative_to(bundle_dir))
                    hashes[rel_path] = calculate_file_hash(f)
                    file_count += 1
    
    return {
        "valid": True,
        "bundle_id": manifest.get("bundle_id"),
        "created_at": manifest.get("created_at"),
        "uat_approval": uat_approval,
        "components": components,
        "file_count": file_count,
        "integrity_hashes": hashes
    }


def prepare_import(bundle_path):
    """Prepare import instructions for a bundle."""
    validation = validate_bundle(bundle_path)
    
    if not validation["valid"]:
        print(f"❌ Bundle validation failed: {validation['error']}")
        return None
    
    bundle_dir = Path(bundle_path)
    manifest = load_json_safe(bundle_dir / "BUNDLE_MANIFEST.json")
    
    # Create import instructions
    instructions = {
        "import_id": f"IMP-{datetime.now().strftime('%Y%m%d_%H%M%S')}",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "bundle_id": manifest.get("bundle_id"),
        "bundle_path": str(bundle_dir),
        "source": "IMPERIUM_TEST_VERSION",
        "target": "E:\\IMPERIUM (canon)",
        "uat_approval": validation["uat_approval"],
        "components": validation["components"],
        "file_count": validation["file_count"],
        "integrity_hashes": validation["integrity_hashes"],
        "status": "READY_FOR_IMPORT",
        "instructions": [
            "1. Review this import manifest",
            "2. Verify UAT approval is valid",
            "3. On PC, navigate to E:\\IMPERIUM",
            "4. Create backup: git stash or git branch backup-pre-import",
            "5. Copy components from bundle to canon:",
        ]
    }
    
    # Add specific copy instructions
    for comp in validation["components"]:
        instructions["instructions"].append(f"   - Copy {comp}/ to E:\\IMPERIUM\\{comp}/")
    
    instructions["instructions"].extend([
        "6. Run verification: py -3 scripts/verify_repo.py",
        "7. Review changes: git status",
        "8. Commit if satisfied: git add . && git commit -m 'Import from test version'",
        "9. Create import receipt"
    ])
    
    # Save import manifest
    import_manifest_path = bundle_dir / "IMPORT_MANIFEST.json"
    with open(import_manifest_path, "w", encoding="utf-8") as f:
        json.dump(instructions, f, indent=2)
    
    # Save to promotion dir
    promotion_dir = get_promotion_dir()
    import_ready_path = promotion_dir / f"IMPORT_READY_{instructions['import_id']}.json"
    with open(import_ready_path, "w", encoding="utf-8") as f:
        json.dump(instructions, f, indent=2)
    
    # Create receipt
    receipt = {
        "receipt_id": f"RCP-IMPORT-PREP-{datetime.now().strftime('%Y%m%d_%H%M%S')}",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "action": "import_preparation",
        "import_id": instructions["import_id"],
        "bundle_id": manifest.get("bundle_id"),
        "file_count": validation["file_count"],
        "verdict": "PASS"
    }
    
    receipts_dir = get_test_version_root() / "RECEIPTS"
    receipt_path = receipts_dir / f"{receipt['receipt_id']}.json"
    with open(receipt_path, "w", encoding="utf-8") as f:
        json.dump(receipt, f, indent=2)
    
    return instructions


def show_import_status():
    """Show import status."""
    promotion_dir = get_promotion_dir()
    
    print("=" * 60)
    print("CANON IMPORT STATUS")
    print("=" * 60)
    print()
    
    # List bundles
    bundles = list_bundles()
    print(f"AVAILABLE BUNDLES: {len(bundles)}")
    for b in bundles:
        m = b["manifest"]
        print(f"  - {m.get('bundle_id')}")
        print(f"    Status: {m.get('status')}")
        print(f"    Components: {len(m.get('components', []))}")
        print(f"    Created: {m.get('created_at')}")
    
    if not bundles:
        print("  None")
    print()
    
    # List ready imports
    ready_imports = list(promotion_dir.glob("IMPORT_READY_*.json")) if promotion_dir.exists() else []
    print(f"READY FOR IMPORT: {len(ready_imports)}")
    for imp_file in sorted(ready_imports, reverse=True)[:3]:
        imp = load_json_safe(imp_file)
        if imp:
            print(f"  - {imp.get('import_id')}")
            print(f"    Bundle: {imp.get('bundle_id')}")
            print(f"    Files: {imp.get('file_count')}")
    
    if not ready_imports:
        print("  None")
    print()
    
    # Import history
    receipts_dir = get_test_version_root() / "RECEIPTS"
    import_receipts = list(receipts_dir.glob("RCP-IMPORT-*.json")) if receipts_dir.exists() else []
    print(f"IMPORT HISTORY: {len(import_receipts)} receipts")


def main():
    parser = argparse.ArgumentParser(description="Canon import management")
    parser.add_argument("--validate", metavar="BUNDLE_PATH", help="Validate a bundle")
    parser.add_argument("--prepare", metavar="BUNDLE_PATH", help="Prepare import")
    parser.add_argument("--list", action="store_true", help="List available bundles")
    parser.add_argument("--status", action="store_true", help="Show import status")
    args = parser.parse_args()
    
    if args.validate:
        print("=" * 60)
        print("BUNDLE VALIDATION")
        print("=" * 60)
        print()
        
        result = validate_bundle(args.validate)
        
        if result["valid"]:
            print(f"✅ Bundle is valid")
            print(f"  Bundle ID: {result['bundle_id']}")
            print(f"  Created: {result['created_at']}")
            print(f"  Components: {result['components']}")
            print(f"  Files: {result['file_count']}")
            print(f"  UAT Approval: {result['uat_approval'].get('approval_status')}")
            return 0
        else:
            print(f"❌ Bundle is invalid: {result['error']}")
            return 1
    
    elif args.prepare:
        print("=" * 60)
        print("IMPORT PREPARATION")
        print("=" * 60)
        print()
        
        result = prepare_import(args.prepare)
        
        if result:
            print(f"✅ Import prepared: {result['import_id']}")
            print()
            print("INSTRUCTIONS:")
            for inst in result["instructions"]:
                print(f"  {inst}")
            print()
            print(f"Import manifest: {args.prepare}/IMPORT_MANIFEST.json")
            return 0
        else:
            return 1
    
    elif args.list:
        bundles = list_bundles()
        print("=" * 60)
        print("AVAILABLE BUNDLES")
        print("=" * 60)
        print()
        
        if bundles:
            for b in bundles:
                m = b["manifest"]
                print(f"Bundle: {m.get('bundle_id')}")
                print(f"  Path: {b['path']}")
                print(f"  Status: {m.get('status')}")
                print(f"  Components: {m.get('components')}")
                print(f"  Created: {m.get('created_at')}")
                print()
        else:
            print("No bundles available")
        
        return 0
    
    elif args.status:
        show_import_status()
        return 0
    
    else:
        show_import_status()
        return 0


if __name__ == "__main__":
    sys.exit(main())
