"""
Second Brain V0.3 — Runtime Pack Exporter
Exports all runtime data (tasks, comments, links, receipts) into a timestamped bundle.

Usage:
    py -3.12 export_second_brain_runtime_pack.py

Output: SECOND_BRAIN/RUNTIME/exports/export_YYYYMMDD-HHMMSS/
"""

import json
import os
import sys
import shutil
import datetime

TOOLS_DIR = os.path.dirname(os.path.abspath(__file__))
SECOND_BRAIN_ROOT = os.path.dirname(TOOLS_DIR)
RUNTIME_DIR = os.path.join(SECOND_BRAIN_ROOT, "RUNTIME")
EXPORTS_DIR = os.path.join(RUNTIME_DIR, "exports")

TASKS_FILE    = os.path.join(SECOND_BRAIN_ROOT, "MEMORY_ZONES", "TASK_INTAKE", "accepted_tasks.json")
COMMENTS_FILE = os.path.join(SECOND_BRAIN_ROOT, "MEMORY_ZONES", "OWNER_COMMENTS", "owner_comments_runtime.json")
LINKS_FILE    = os.path.join(SECOND_BRAIN_ROOT, "MEMORY_ZONES", "MEMORY_LINKS", "task_comment_links.json")
RECEIPTS_DIR  = os.path.join(RUNTIME_DIR, "receipts")


def main():
    stamp = datetime.datetime.utcnow().strftime("%Y%m%d-%H%M%S")
    export_dir = os.path.join(EXPORTS_DIR, f"export_{stamp}")
    os.makedirs(export_dir, exist_ok=True)

    print("=" * 60)
    print("Second Brain V0.3 — Runtime Pack Exporter")
    print("=" * 60)
    print(f"Export dir: {export_dir}")
    print()

    exported = []

    for src, label in [
        (TASKS_FILE,    "accepted_tasks.json"),
        (COMMENTS_FILE, "owner_comments_runtime.json"),
        (LINKS_FILE,    "task_comment_links.json"),
    ]:
        if os.path.isfile(src):
            dst = os.path.join(export_dir, os.path.basename(src))
            shutil.copy2(src, dst)
            exported.append(label)
            print(f"  [OK] Copied: {label}")
        else:
            print(f"  [SKIP] Not found: {label}")

    # Copy receipts
    receipts_export = os.path.join(export_dir, "receipts")
    if os.path.isdir(RECEIPTS_DIR):
        shutil.copytree(RECEIPTS_DIR, receipts_export)
        rcount = len([f for f in os.listdir(RECEIPTS_DIR) if f.endswith(".json")])
        exported.append(f"receipts/ ({rcount} files)")
        print(f"  [OK] Copied receipts: {rcount} files")
    else:
        print("  [SKIP] No receipts directory")

    # Write manifest
    manifest = {
        "export_id": f"EXP-{stamp}",
        "created_at": datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ"),
        "exported_files": exported,
        "export_path": export_dir,
        "runtime_mode": "PROTOTYPE_INTERACTIVE",
        "no_llm": True,
        "no_agent_api": True,
        "not_production_ready": True
    }
    manifest_path = os.path.join(export_dir, "manifest.json")
    with open(manifest_path, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2, ensure_ascii=False)

    print()
    print(f"Manifest: {manifest_path}")
    print(f"Export ID: {manifest['export_id']}")
    print(f"Files exported: {len(exported)}")
    print()
    print("DONE — runtime pack exported.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
