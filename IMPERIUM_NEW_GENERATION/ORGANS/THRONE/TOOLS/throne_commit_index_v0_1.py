#!/usr/bin/env python3
"""Read-only Throne commit index prototype."""

import argparse
import json
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path


TASK_ID_RE = re.compile(r"TASK-[A-Z0-9][A-Z0-9_-]*-V[0-9_]+")


def run_git(repo_root: Path, args: list[str]) -> str:
    completed = subprocess.run(
        ["git", "-C", str(repo_root), *args],
        check=True,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    return completed.stdout.strip()


def detect_task_id(summary: str) -> str:
    match = TASK_ID_RE.search(summary)
    return match.group(0) if match else "UNKNOWN"


def changed_files_count(repo_root: Path, commit_sha: str) -> int:
    output = run_git(repo_root, ["diff-tree", "--no-commit-id", "--name-only", "-r", commit_sha])
    if not output:
        return 0
    return len([line for line in output.splitlines() if line.strip()])


def verify_commit_object(repo_root: Path, commit_sha: str) -> bool:
    try:
        run_git(repo_root, ["cat-file", "-e", f"{commit_sha}^{{commit}}"])
        return True
    except subprocess.CalledProcessError:
        return False


def build_index(repo_root: Path, limit: int) -> dict:
    branch = run_git(repo_root, ["rev-parse", "--abbrev-ref", "HEAD"])
    head = run_git(repo_root, ["rev-parse", "HEAD"])
    log_format = "%H%x1f%h%x1f%P%x1f%cI%x1f%s"
    raw = run_git(repo_root, ["log", f"--format={log_format}", f"-n{limit}"])
    records = []

    for line in raw.splitlines():
        full_sha, short_sha, parents, committed_at, summary = line.split("\x1f", 4)
        parent_sha = parents.split()[0] if parents.strip() else None
        task_id = detect_task_id(summary)
        object_verified = verify_commit_object(repo_root, full_sha)
        records.append(
            {
                "schema_version": "THRONE_COMMIT_INDEX_RECORD_V0_1",
                "commit_sha": full_sha,
                "short_sha": short_sha,
                "parent_sha": parent_sha,
                "commit_datetime_utc": committed_at.replace("+00:00", "Z"),
                "branch": branch,
                "task_id": task_id,
                "summary": summary,
                "changed_files_count": changed_files_count(repo_root, full_sha),
                "task_group_id": task_id if task_id != "UNKNOWN" else full_sha,
                "bundle_available": False,
                "admission_status": "INDEXED_ONLY" if object_verified else "CUSTODES_PENDING",
            }
        )

    return {
        "schema_version": "THRONE_COMMIT_INDEX_V0_1",
        "generated_at_utc": datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
        "repo_root": str(repo_root.resolve()),
        "branch": branch,
        "head": head,
        "limit": limit,
        "records": records,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", default=".")
    parser.add_argument("--limit", type=int, default=10)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()

    repo_root = Path(args.repo_root)
    output_path = Path(args.output)
    if args.limit < 1:
        raise SystemExit("--limit must be >= 1")

    index = build_index(repo_root, args.limit)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(index, ensure_ascii=True, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"status": "PASS", "output": str(output_path), "records": len(index["records"])}, ensure_ascii=True))
    return 0


if __name__ == "__main__":
    sys.exit(main())
