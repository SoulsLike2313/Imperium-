#!/usr/bin/env python3
"""
send_prompt_to_vm2.py

Purpose:
Create or use a local PROMPT.md, send it to VM2 worker inbox by TASK_ID,
verify remote sha256, optionally open the prompt on VM2 with gnome-text-editor,
and write a PC-side receipt.

This is a controlled PC -> VM2 dispatch helper.
It does not write to THRONE.
It does not touch VM3.
It does not use latest logic.
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


def run_cmd(cmd: list[str], *, capture: bool = True) -> subprocess.CompletedProcess:
    return subprocess.run(
        cmd,
        text=True,
        capture_output=capture,
        shell=False,
        check=False,
    )


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def ensure_prompt(local_prompt: Path, task_id: str, stage_id: str) -> None:
    local_prompt.parent.mkdir(parents=True, exist_ok=True)
    if local_prompt.exists():
        return
    text = f"""# VM2 TASK PROMPT

TASK_ID:
{task_id}

STAGE_ID:
{stage_id}

CONTOUR:
VM2

INSTRUCTION:
Replace this text with the actual VM2 task prompt.

RULES:
- Work only inside /home/vboxuser2/IMPERIUM_WORKER_ROOM.
- Do not touch THRONE.
- Do not touch VM3.
- Do not delete files.
- Do not auto-sync.
- Emit receipt, manifest, hashes, and stage bundle if this is an execution task.
"""
    local_prompt.write_text(text, encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Send PROMPT.md to VM2 worker inbox.")
    parser.add_argument("--task-id", required=True)
    parser.add_argument("--stage-id", default="STAGE-001-VM2")
    parser.add_argument("--config", default=str(DEFAULT_CONFIG))
    parser.add_argument("--local-prompt", default="")
    parser.add_argument("--open-remote", action="store_true")
    parser.add_argument("--no-create", action="store_true", help="Do not create local prompt if missing.")
    args = parser.parse_args()

    config = load_config(Path(args.config))
    key_path = config["key_path"]
    port = str(config["port"])
    user_host = config["user_host"]
    remote_root = config["remote_worker_root"]
    pc_root = Path(config["pc_root"])

    task_root = pc_root / "ARTIFACTS" / args.task_id
    local_prompt = Path(args.local_prompt) if args.local_prompt else task_root / "01_INPUTS" / "PROMPT.md"

    if not local_prompt.exists():
        if args.no_create:
            print(f"BLOCKED: local prompt does not exist: {local_prompt}", file=sys.stderr)
            return 2
        ensure_prompt(local_prompt, args.task_id, args.stage_id)

    remote_dir = f"{remote_root}/01_INBOX/tasks/{args.task_id}"
    remote_prompt = f"{remote_dir}/PROMPT.md"

    receipt_dir = task_root / "03_RECEIPTS"
    report_dir = task_root / "07_REPORTS"
    hash_dir = task_root / "05_HASHES"
    manifest_dir = task_root / "04_MANIFESTS"
    for d in [receipt_dir, report_dir, hash_dir, manifest_dir]:
        d.mkdir(parents=True, exist_ok=True)

    local_hash = sha256_file(local_prompt)

    mkdir_cmd = ["ssh", "-i", key_path, "-p", port, user_host, f"mkdir -p '{remote_dir}'"]
    mkdir_result = run_cmd(mkdir_cmd)
    if mkdir_result.returncode != 0:
        print(mkdir_result.stderr, file=sys.stderr)
        verdict = "BLOCKED"
        remote_hash = ""
        match = "NO"
    else:
        scp_cmd = ["scp", "-i", key_path, "-P", port, str(local_prompt), f"{user_host}:{remote_prompt}"]
        scp_result = run_cmd(scp_cmd)
        if scp_result.returncode != 0:
            print(scp_result.stderr, file=sys.stderr)
            verdict = "BLOCKED"
            remote_hash = ""
            match = "NO"
        else:
            verify_cmd = ["ssh", "-i", key_path, "-p", port, user_host, f"sha256sum '{remote_prompt}'"]
            verify_result = run_cmd(verify_cmd)
            if verify_result.returncode != 0:
                print(verify_result.stderr, file=sys.stderr)
                verdict = "BLOCKED"
                remote_hash = ""
                match = "NO"
            else:
                remote_hash = verify_result.stdout.strip().split()[0].lower()
                match = "YES" if remote_hash == local_hash else "NO"
                verdict = "PASS" if match == "YES" else "BLOCKED"

    open_attempted = "NO"
    if args.open_remote and verdict == "PASS":
        open_cmd = [
            "ssh", "-i", key_path, "-p", port, user_host,
            "export DISPLAY=:0; export XDG_RUNTIME_DIR=/run/user/1000; "
            "export DBUS_SESSION_BUS_ADDRESS=unix:path=/run/user/1000/bus; "
            f"nohup gnome-text-editor '{remote_prompt}' >/tmp/imperium_open_prompt.log 2>&1 &"
        ]
        open_result = run_cmd(open_cmd)
        open_attempted = "YES"
        if open_result.returncode != 0:
            (report_dir / "OPEN_REMOTE_PROMPT_WARNING.md").write_text(
                "# OPEN REMOTE PROMPT WARNING\n\n"
                f"Return code: {open_result.returncode}\n\n"
                f"stderr:\n{open_result.stderr}\n",
                encoding="utf-8"
            )

    timestamp = datetime.now().isoformat(timespec="seconds")
    receipt = f"""# SEND PROMPT TO VM2 RECEIPT

task_id:
{args.task_id}

stage_id:
{args.stage_id}

timestamp:
{timestamp}

local_prompt:
{local_prompt}

remote_prompt:
{remote_prompt}

local_sha256:
{local_hash}

remote_sha256:
{remote_hash}

sha256_match:
{match}

open_remote_attempted:
{open_attempted}

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
Prompt was dispatched by TASK_ID-specific path.
"""
    (receipt_dir / "SEND_PROMPT_TO_VM2_SCRIPT_RECEIPT.md").write_text(receipt, encoding="utf-8")
    (hash_dir / "PROMPT_SHA256SUMS.txt").write_text(f"{local_hash}  {local_prompt}\n", encoding="utf-8")
    (manifest_dir / "SEND_PROMPT_MANIFEST.csv").write_text(
        "local_prompt,remote_prompt,local_sha256,remote_sha256,sha256_match,verdict\n"
        f"{local_prompt},{remote_prompt},{local_hash},{remote_hash},{match},{verdict}\n",
        encoding="utf-8"
    )

    print(f"task_id: {args.task_id}")
    print(f"local_prompt: {local_prompt}")
    print(f"remote_prompt: {remote_prompt}")
    print(f"sha256_match: {match}")
    print(f"verdict: {verdict}")
    return 0 if verdict == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
