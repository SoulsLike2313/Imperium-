#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path
from typing import Any, Dict, List

from continuity_common import detect_task_id, now_utc, parse_verdict_from_text, safe_read_text, write_json, write_text


def has_any(folder: Path, pattern: str) -> bool:
    return any(folder.rglob(pattern))


def detect_evidence_verdict(folder: Path) -> str:
    summary_files = [p for p in folder.rglob("*.md") if "SUMMARY" in p.name.upper() or "OWNER" in p.name.upper()]
    for f in summary_files:
        verdict = parse_verdict_from_text(safe_read_text(f))
        if verdict:
            return verdict
    return "UNKNOWN"


def proof_scope(folder: Path) -> str:
    text_parts: List[str] = []
    for f in folder.rglob("*.md"):
        name = f.name.upper()
        if "SUMMARY" in name or "PROBE" in name or "OWNER" in name:
            text_parts.append(safe_read_text(f)[:4000])
    text = "\n".join(text_parts).lower()
    if "not full e2e" in text or "manual probe" in text or "live manual probe" in text:
        return "MANUAL_PROBE"
    if "full e2e" in text:
        return "FULL_E2E"
    return "MANUAL_PROOF"


def main() -> int:
    parser = argparse.ArgumentParser(description="Inventory OWNER_MANUAL proofs")
    parser.add_argument("--imperium-root", required=True)
    parser.add_argument("--output-json", required=True)
    parser.add_argument("--output-md", required=True)
    args = parser.parse_args()

    root = Path(args.imperium_root).resolve()
    manual_root = root / "ARTIFACTS" / "_MANUAL_PROOFS"
    records: List[Dict[str, Any]] = []

    if manual_root.exists():
        for child in sorted(manual_root.iterdir(), key=lambda p: p.name.lower()):
            if not child.is_dir() or not child.name.upper().startswith("TASK-"):
                continue
            task_id = detect_task_id(child.name)
            important: List[str] = []
            summary_text = ""
            summary_file = None
            for md in child.rglob("*.md"):
                if "SUMMARY" in md.name.upper() or "OWNER" in md.name.upper():
                    summary_text = safe_read_text(md)
                    summary_file = md
                    break
            if "rejects pc-stage-001" in summary_text.lower() and "accepts stage-pc-001" in summary_text.lower():
                important.append("stage_id_schema_mismatch_detected")

            rec = {
                "task_id": task_id,
                "proof_path": str(child),
                "proof_type": "OWNER_MANUAL_PROOF",
                "has_zip": has_any(child, "*.zip"),
                "has_zip_sha256": has_any(child, "*.zip.sha256"),
                "has_receipt": has_any(child, "*RECEIPT*.json") or has_any(child, "*RECEIPT*.md"),
                "has_receipt_sha256": has_any(child, "*RECEIPT*.sha256"),
                "has_summary": bool(summary_file),
                "has_ledger_event": has_any(child, "*LEDGER*.jsonl"),
                "has_manifest": has_any(child, "MANIFEST.json"),
                "has_sha256s": has_any(child, "SHA256SUMS.txt"),
                "evidence_verdict": detect_evidence_verdict(child),
                "scope": proof_scope(child),
                "important_findings": important,
                "modified_time": child.stat().st_mtime,
            }
            records.append(rec)

    counts = {
        "total": len(records),
        "manual_probe": sum(1 for r in records if r["scope"] == "MANUAL_PROBE"),
        "full_e2e": sum(1 for r in records if r["scope"] == "FULL_E2E"),
        "unknown": sum(1 for r in records if r["evidence_verdict"] == "UNKNOWN"),
    }
    verdict = "PASS" if counts["total"] > 0 else "PARTIAL"

    payload = {
        "generated_at_utc": now_utc(),
        "manual_proofs_root": str(manual_root),
        "counts": counts,
        "records": records,
        "verdict": verdict,
    }
    write_json(Path(args.output_json), payload)

    lines = [
        "# 0016A MANUAL PROOFS INVENTORY",
        "",
        f"generated_at_utc: {payload['generated_at_utc']}",
        f"manual_proofs_root: {payload['manual_proofs_root']}",
        f"total: {counts['total']} manual_probe: {counts['manual_probe']} full_e2e: {counts['full_e2e']}",
        "",
        "## Records",
    ]
    for r in records:
        lines.append(
            f"- {r['task_id']} | type={r['proof_type']} | scope={r['scope']} | zip={r['has_zip']} | receipt={r['has_receipt']} | verdict={r['evidence_verdict']} | findings={','.join(r['important_findings']) if r['important_findings'] else 'none'}"
        )
    write_text(Path(args.output_md), "\n".join(lines))

    print(f"continuity_inventory_manual_proofs: folders={counts['total']} verdict={verdict}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
