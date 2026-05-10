#!/usr/bin/env python3
from __future__ import annotations

import argparse
import zipfile
from pathlib import Path
from typing import Any, Dict, List

from continuity_common import now_utc, read_json_safe, sha256_file, verify_sha256s_file, write_json, write_text


def main() -> int:
    parser = argparse.ArgumentParser(description="Verify continuity pack integrity")
    parser.add_argument("--task-root", required=True)
    parser.add_argument("--pack-dir", required=True)
    parser.add_argument("--output-json", required=True)
    parser.add_argument("--output-md", required=True)
    args = parser.parse_args()

    task_root = Path(args.task_root).resolve()
    pack_dir = Path(args.pack_dir).resolve()
    zip_path = task_root / "CONTINUITY_PACK.zip"
    sidecar_path = task_root / "CONTINUITY_PACK.zip.sha256"

    required_files = [
        pack_dir / "MANIFEST.json",
        pack_dir / "SHA256SUMS.txt",
        pack_dir / "CONTINUITY_INDEX.json",
        pack_dir / "METRICS.json",
        pack_dir / "CONTINUITY_OWNER_SUMMARY.md",
    ]
    missing_required = [str(p) for p in required_files if not p.exists()]

    sha_result = {
        "verified_count": 0,
        "missing_count": 0,
        "mismatch_count": 0,
        "invalid_count": 0,
        "errors": [],
    }
    if (pack_dir / "SHA256SUMS.txt").exists():
        sha_result = verify_sha256s_file(pack_dir, pack_dir / "SHA256SUMS.txt")

    sidecar_matches_zip = False
    zip_hash = None
    if zip_path.exists():
        zip_hash = sha256_file(zip_path)
        if sidecar_path.exists():
            text = sidecar_path.read_text(encoding="utf-8", errors="ignore").strip()
            sidecar_matches_zip = text == f"{zip_hash}  CONTINUITY_PACK.zip"

    zip_bad_paths: List[str] = []
    cache_entries: List[str] = []
    if zip_path.exists():
        with zipfile.ZipFile(zip_path, "r") as zf:
            for n in zf.namelist():
                if "\\" in n or n.startswith("/") or "../" in n or (len(n) > 1 and n[1] == ":"):
                    zip_bad_paths.append(n)
                low = n.lower()
                if "/__pycache__/" in f"/{low}/" or low.endswith(".pyc") or low.endswith(".pyo"):
                    cache_entries.append(n)

    latest_source_findings = []
    idx_path = pack_dir / "CONTINUITY_INDEX.json"
    if idx_path.exists():
        idx, _ = read_json_safe(idx_path)
        if isinstance(idx, dict):
            for _, rel in (idx.get("paths") or {}).items():
                if isinstance(rel, str) and "latest" in rel.lower():
                    latest_source_findings.append(rel)

    verdict = "PASS"
    if missing_required:
        verdict = "BLOCKED"
    if sha_result["missing_count"] or sha_result["mismatch_count"] or sha_result["invalid_count"]:
        verdict = "BLOCKED"
    if not zip_path.exists() or not sidecar_path.exists() or not sidecar_matches_zip:
        verdict = "BLOCKED"
    if zip_bad_paths or cache_entries:
        verdict = "BLOCKED"

    payload: Dict[str, Any] = {
        "generated_at_utc": now_utc(),
        "task_root": str(task_root),
        "pack_dir": str(pack_dir),
        "required_files_missing": missing_required,
        "internal_sha256s": sha_result,
        "zip_exists": zip_path.exists(),
        "zip_sha256": zip_hash,
        "sidecar_exists": sidecar_path.exists(),
        "sidecar_matches_zip": sidecar_matches_zip,
        "zip_bad_paths": zip_bad_paths,
        "zip_cache_entries": cache_entries,
        "latest_source_findings": latest_source_findings,
        "verdict": verdict,
        "no_vm2_contact": True,
        "no_real_e2e": True,
        "no_throne": True,
        "no_watchers": True,
        "no_latest_logic": True,
    }

    write_json(Path(args.output_json), payload)

    lines = [
        "# 0016A PACK VERIFY REPORT",
        "",
        f"generated_at_utc: {payload['generated_at_utc']}",
        f"pack_dir: {payload['pack_dir']}",
        f"zip_exists: {str(payload['zip_exists']).lower()} sidecar_exists: {str(payload['sidecar_exists']).lower()} sidecar_matches_zip: {str(sidecar_matches_zip).lower()}",
        f"internal_sha_verified: {sha_result['verified_count']} missing={sha_result['missing_count']} mismatch={sha_result['mismatch_count']} invalid={sha_result['invalid_count']}",
        f"zip_bad_paths_count: {len(zip_bad_paths)}",
        f"zip_cache_entries_count: {len(cache_entries)}",
        f"required_files_missing_count: {len(missing_required)}",
        f"latest_source_findings_count: {len(latest_source_findings)}",
        f"verdict: {verdict}",
    ]
    write_text(Path(args.output_md), "\n".join(lines))

    print(f"continuity_pack_verify: verdict={verdict} sidecar_matches_zip={sidecar_matches_zip}")
    return 0 if verdict == "PASS" else 2


if __name__ == "__main__":
    raise SystemExit(main())
