#!/usr/bin/env python3
"""
fetch_vm2_stage_bundle.py

Purpose:
Fetch a VM2 stage bundle by exact TASK/STAGE/CONTOUR/RUN identifiers,
copy bundle and checksum into ARTIFACTS, verify sha256, write receipts,
and optionally open the local bundle folder.

No global latest logic.
No THRONE writes.
No VM3 writes.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
from datetime import datetime
from pathlib import Path


DEFAULT_CONFIG = Path(r"E:\IMPERIUM\SSH_COMMAND_LIBRARY\00_CONNECTION_PROFILES\VM2_ROUTE.local.json")


def load_config(path: Path) -> dict:
    if not path.exists():
        raise FileNotFoundError(f"Config not found: {path}")
    return json.loads(path.read_text(encoding="utf-8"))


def run_cmd(cmd: list[str]) -> subprocess.CompletedProcess:
    return subprocess.run(cmd, text=True, capture_output=True, shell=False, check=False)


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser(description="Fetch VM2 stage bundle by exact identifiers.")
    parser.add_argument("--task-id", required=True)
    parser.add_argument("--stage-id", required=True)
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--contour-id", default="VM2")
    parser.add_argument("--config", default=str(DEFAULT_CONFIG))
    parser.add_argument("--open-folder", action="store_true")
    parser.add_argument("--allow-targz", action="store_true")
    args = parser.parse_args()

    config = load_config(Path(args.config))
    key_path = config["key_path"]
    port = str(config["port"])
    user_host = config["user_host"]
    remote_root = config["remote_worker_root"]
    pc_root = Path(config["pc_root"])

    base_name = f"{args.task_id}__{args.stage_id}__CONTOUR-{args.contour_id}__{args.run_id}__STAGE_BUNDLE"
    remote_dir = f"{remote_root}/03_OUTBOX/stage_bundles"
    remote_bundle = f"{remote_dir}/{base_name}.zip"
    remote_sha = f"{remote_bundle}.sha256"

    local_task_root = pc_root / "ARTIFACTS" / args.task_id
    local_bundle_dir = local_task_root / "06_BUNDLES" / args.contour_id
    receipt_dir = local_task_root / "03_RECEIPTS"
    manifest_dir = local_task_root / "04_MANIFESTS"
    hash_dir = local_task_root / "05_HASHES"
    report_dir = local_task_root / "07_REPORTS"
    summary_dir = local_task_root / "08_OWNER_SUMMARY"
    for d in [local_bundle_dir, receipt_dir, manifest_dir, hash_dir, report_dir, summary_dir]:
        d.mkdir(parents=True, exist_ok=True)

    remote_check = run_cmd(["ssh", "-i", key_path, "-p", port, user_host, f"test -f '{remote_bundle}' && test -f '{remote_sha}' && echo OK"])
    if remote_check.returncode != 0 and args.allow_targz:
        remote_bundle = f"{remote_dir}/{base_name}.tar.gz"
        remote_sha = f"{remote_bundle}.sha256"
        remote_check = run_cmd(["ssh", "-i", key_path, "-p", port, user_host, f"test -f '{remote_bundle}' && test -f '{remote_sha}' && echo OK"])

    if remote_check.returncode != 0:
        (report_dir / "FETCH_BLOCKED_MISSING_REMOTE_BUNDLE.md").write_text(
            "# FETCH BLOCKED\n\n"
            f"Remote bundle or checksum was not found.\n\n"
            f"Expected bundle:\n{remote_bundle}\n\n"
            f"Expected checksum:\n{remote_sha}\n\n"
            f"stderr:\n{remote_check.stderr}\n",
            encoding="utf-8"
        )
        print("BLOCKED: remote bundle or sha256 file not found", file=sys.stderr)
        return 2

    local_bundle = local_bundle_dir / Path(remote_bundle).name
    local_sha = local_bundle_dir / Path(remote_sha).name

    scp_bundle = run_cmd(["scp", "-i", key_path, "-P", port, f"{user_host}:{remote_bundle}", str(local_bundle)])
    if scp_bundle.returncode != 0:
        print(scp_bundle.stderr, file=sys.stderr)
        return 3

    scp_sha = run_cmd(["scp", "-i", key_path, "-P", port, f"{user_host}:{remote_sha}", str(local_sha)])
    if scp_sha.returncode != 0:
        print(scp_sha.stderr, file=sys.stderr)
        return 4

    local_hash = sha256_file(local_bundle)
    remote_hash_raw = local_sha.read_text(encoding="utf-8", errors="replace")
    remote_hash = remote_hash_raw.split()[0].strip().lower()
    match = "YES" if local_hash == remote_hash else "NO"
    verdict = "PASS" if match == "YES" else "BLOCKED"

    timestamp = datetime.now().isoformat(timespec="seconds")
    receipt = f"""# VM2 STAGE BUNDLE FETCH RECEIPT

task_id:
{args.task_id}

stage_id:
{args.stage_id}

run_id:
{args.run_id}

contour:
{args.contour_id}

timestamp:
{timestamp}

remote_bundle:
{remote_bundle}

remote_sha256_file:
{remote_sha}

local_bundle:
{local_bundle}

local_sha256_file:
{local_sha}

local_sha256:
{local_hash}

remote_sha256:
{remote_hash}

sha256_match:
{match}

fetched_by:
fetch_vm2_stage_bundle.py

deleted_anything:
NO

touched_throne:
NO

touched_vm3:
NO

autosync_used:
NO

latest_bundle_logic_used:
NO

verdict:
{verdict}

notes:
Bundle was fetched by exact TASK/STAGE/CONTOUR/RUN path, not by latest logic.
"""
    (receipt_dir / "VM2_STAGE_BUNDLE_FETCH_SCRIPT_RECEIPT.md").write_text(receipt, encoding="utf-8")

    (manifest_dir / "VM2_FETCH_MANIFEST.csv").write_text(
        "remote_bundle,remote_sha256,local_bundle,local_sha256_file,sha256_match,verdict\n"
        f"{remote_bundle},{remote_sha},{local_bundle},{local_sha},{match},{verdict}\n",
        encoding="utf-8"
    )

    (hash_dir / "VM2_FETCHED_BUNDLE_SHA256SUMS.txt").write_text(f"{local_hash}  {local_bundle}\n", encoding="utf-8")

    (report_dir / "VM2_FETCH_VERDICT.md").write_text(
        f"# VM2 FETCH VERDICT\n\n"
        f"Task: {args.task_id}\n\n"
        f"Stage: {args.stage_id}\n\n"
        f"Run: {args.run_id}\n\n"
        f"Bundle: {local_bundle}\n\n"
        f"SHA256 match: {match}\n\n"
        f"Verdict: {verdict}\n",
        encoding="utf-8"
    )

    (summary_dir / "OWNER_SUMMARY.md").write_text(
        f"# OWNER SUMMARY\n\n"
        f"VM2 stage bundle was fetched by exact TASK/STAGE/CONTOUR/RUN path.\n"
        f"Local and remote SHA256 match: {match}.\n"
        f"Fetch verdict: {verdict}.\n"
        f"Bundle folder: {local_bundle_dir}\n",
        encoding="utf-8"
    )

    if args.open_folder:
        subprocess.run(["explorer", str(local_bundle_dir)], check=False)

    print(f"task_id: {args.task_id}")
    print(f"bundle: {local_bundle}")
    print(f"sha256_match: {match}")
    print(f"verdict: {verdict}")
    return 0 if verdict == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
