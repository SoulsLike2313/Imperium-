#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path
from typing import Any, Dict, List

from continuity_common import detect_task_id, now_utc, write_json, write_text


def has_any(folder: Path, pattern: str) -> bool:
    return any(folder.rglob(pattern))


def status_guess(rec: Dict[str, Any]) -> str:
    if not rec["detected_task_id"]:
        return "LEGACY"
    if rec["has_zip_bundle"] and rec["has_sha256"] and rec["has_manifest_json"] and rec["has_sha256s_txt"] and rec["has_owner_summary_md"]:
        return "PASS"
    if rec["has_zip_bundle"] or rec["has_sha256"] or rec["has_reports_folder"]:
        return "PARTIAL"
    return "REPAIR_REQUIRED"


def main() -> int:
    parser = argparse.ArgumentParser(description="Inventory normal artifact task folders")
    parser.add_argument("--imperium-root", required=True)
    parser.add_argument("--output-json", required=True)
    parser.add_argument("--output-md", required=True)
    args = parser.parse_args()

    root = Path(args.imperium_root).resolve()
    artifacts_root = root / "ARTIFACTS"
    records: List[Dict[str, Any]] = []

    if artifacts_root.exists():
        for child in sorted(artifacts_root.iterdir(), key=lambda p: p.name.lower()):
            if not child.is_dir() or child.name == "_MANUAL_PROOFS":
                continue
            rec: Dict[str, Any] = {
                "folder_name": child.name,
                "path": str(child),
                "detected_task_id": detect_task_id(child.name),
                "modified_time": child.stat().st_mtime,
                "has_final_step_bundle_folder": (child / "FINAL_STEP_BUNDLE").exists(),
                "has_zip_bundle": has_any(child, "*.zip"),
                "has_sha256": has_any(child, "*.sha256"),
                "has_manifest_json": has_any(child, "MANIFEST.json"),
                "has_sha256s_txt": has_any(child, "SHA256SUMS.txt"),
                "has_owner_summary_md": has_any(child, "OWNER_SUMMARY.md"),
                "has_agent_final_response_txt": has_any(child, "AGENT_FINAL_RESPONSE.txt"),
                "has_speculum_review_request_md": has_any(child, "SPECULUM_REVIEW_REQUEST.md"),
                "has_reports_folder": any(p.is_dir() and p.name.upper() == "REPORTS" for p in child.rglob("*")),
                "has_receipts_folder": any(p.is_dir() and p.name.upper() in {"RECEIPTS", "MANUAL_RECEIPTS"} for p in child.rglob("*")),
                "display_order": "folder_name",
            }
            rec["status_guess"] = status_guess(rec)
            records.append(rec)

    counts = {
        "total": len(records),
        "pass": sum(1 for r in records if r["status_guess"] == "PASS"),
        "partial": sum(1 for r in records if r["status_guess"] == "PARTIAL"),
        "repair_required": sum(1 for r in records if r["status_guess"] == "REPAIR_REQUIRED"),
        "legacy": sum(1 for r in records if r["status_guess"] == "LEGACY"),
        "unknown": sum(1 for r in records if r["status_guess"] == "UNKNOWN"),
    }

    verdict = "PASS" if counts["total"] > 0 else "PARTIAL"

    payload = {
        "generated_at_utc": now_utc(),
        "artifacts_root": str(artifacts_root),
        "counts": counts,
        "records": records,
        "verdict": verdict,
    }
    write_json(Path(args.output_json), payload)

    lines = [
        "# 0016A ARTIFACTS INVENTORY",
        "",
        f"generated_at_utc: {payload['generated_at_utc']}",
        f"artifacts_root: {payload['artifacts_root']}",
        f"total_folders: {counts['total']}",
        f"pass: {counts['pass']} partial: {counts['partial']} repair_required: {counts['repair_required']} legacy: {counts['legacy']}",
        "",
        "## Records",
    ]
    for r in records:
        lines.append(
            f"- {r['folder_name']} | task_id={r['detected_task_id']} | final_bundle={r['has_final_step_bundle_folder']} | zip={r['has_zip_bundle']} | sha256={r['has_sha256']} | status={r['status_guess']}"
        )
    write_text(Path(args.output_md), "\n".join(lines))

    print(f"continuity_inventory_artifacts: folders={counts['total']} verdict={verdict}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
