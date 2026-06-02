#!/usr/bin/env python3
"""Export a minimal Throne commit evidence smoke bundle."""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
import tarfile
from datetime import datetime, timezone
from pathlib import Path


SCHEMA_VERSION = "THRONE_COMMIT_EVIDENCE_BUNDLE_MANIFEST_V0_1"
CAP_TREE_ARCHIVE_OMITTED = "CAP_TREE_ARCHIVE_OMITTED_PROTOTYPE_SMOKE"


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def run_git(git_args: list[str], repo_root: Path | None, git_dir: Path | None) -> str:
    base = ["git"]
    if git_dir is not None:
        base.extend([f"--git-dir={git_dir}"])
    elif repo_root is not None:
        base.extend(["-C", str(repo_root)])
    else:
        raise ValueError("repo_root or git_dir is required")

    completed = subprocess.run(
        [*base, *git_args],
        check=True,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    return completed.stdout


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def write_json(path: Path, payload: object) -> None:
    write_text(path, json.dumps(payload, ensure_ascii=True, indent=2) + "\n")


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def git_lines(git_args: list[str], repo_root: Path | None, git_dir: Path | None) -> list[str]:
    output = run_git(git_args, repo_root, git_dir).strip()
    return [line for line in output.splitlines() if line.strip()]


def commit_metadata(commit: str, repo_root: Path | None, git_dir: Path | None) -> dict:
    fmt = "%H%x1f%P%x1f%T%x1f%an%x1f%ae%x1f%aI%x1f%cn%x1f%ce%x1f%cI%x1f%s"
    raw = run_git(["show", "-s", f"--format={fmt}", commit], repo_root, git_dir).strip()
    (
        full_sha,
        parents,
        tree_sha,
        author_name,
        author_email,
        author_date,
        committer_name,
        committer_email,
        committer_date,
        subject,
    ) = raw.split("\x1f", 9)
    return {
        "commit_sha": full_sha,
        "parent_shas": parents.split() if parents.strip() else [],
        "primary_parent_sha": parents.split()[0] if parents.strip() else None,
        "tree_sha": tree_sha,
        "author_name": author_name,
        "author_email": author_email,
        "author_date": author_date,
        "committer_name": committer_name,
        "committer_email": committer_email,
        "committer_date": committer_date,
        "subject": subject,
    }


def changed_files(commit: str, parent_sha: str | None, repo_root: Path | None, git_dir: Path | None) -> list[dict]:
    if parent_sha:
        args = ["diff", "--name-status", parent_sha, commit]
    else:
        args = ["diff-tree", "--root", "--no-commit-id", "--name-status", "-r", commit]
    records = []
    for line in git_lines(args, repo_root, git_dir):
        parts = line.split("\t")
        records.append({"status": parts[0], "path": parts[-1]})
    return records


def create_content_tar(output_dir: Path, files: list[Path]) -> Path:
    tar_path = output_dir / "commit_evidence_bundle_smoke.tar.gz"
    with tarfile.open(tar_path, "w:gz") as tar:
        for path in files:
            tar.add(path, arcname=path.name)
    return tar_path


def write_sha256s(output_dir: Path, paths: list[Path]) -> Path:
    sha_path = output_dir / "sha256sums.txt"
    lines = [f"{sha256_file(path)}  {path.name}" for path in paths]
    write_text(sha_path, "\n".join(lines) + "\n")
    return sha_path


def export_bundle(args: argparse.Namespace) -> dict:
    repo_root = Path(args.repo_root).resolve() if args.repo_root else None
    git_dir = Path(args.git_dir).resolve() if args.git_dir else None
    output_dir = Path(args.output_dir).resolve()
    output_dir.mkdir(parents=True, exist_ok=True)

    commit = run_git(["rev-parse", args.commit], repo_root, git_dir).strip()
    run_git(["cat-file", "-e", f"{commit}^{{commit}}"], repo_root, git_dir)

    metadata = commit_metadata(commit, repo_root, git_dir)
    parent_sha = metadata["primary_parent_sha"]
    changed = changed_files(commit, parent_sha, repo_root, git_dir)

    metadata_path = output_dir / "commit_metadata.json"
    changed_path = output_dir / "changed_files_manifest.json"
    show_path = output_dir / "git_show.txt"
    diff_path = output_dir / "diff.patch"
    receipts_path = output_dir / "receipts_manifest.json"
    tree_note_path = output_dir / "tree_archive_omission_reason.txt"

    write_json(metadata_path, metadata)
    write_json(
        changed_path,
        {
            "schema_version": "THRONE_CHANGED_FILES_MANIFEST_V0_1",
            "commit_sha": commit,
            "parent_sha": parent_sha,
            "changed_files_count": len(changed),
            "changed_files": changed,
        },
    )
    write_text(show_path, run_git(["show", "--stat", "--summary", "--format=fuller", commit], repo_root, git_dir))
    if parent_sha:
        diff_text = run_git(["diff", "--binary", parent_sha, commit], repo_root, git_dir)
    else:
        diff_text = run_git(["show", "--binary", "--format=", commit], repo_root, git_dir)
    write_text(diff_path, diff_text)

    content_files = [metadata_path, changed_path, show_path, diff_path]
    caps_triggered: list[str] = []
    tree_archive_included = False
    if args.include_tree_archive:
        tree_path = output_dir / "tree_archive.tar"
        archive_base = ["git"]
        if git_dir is not None:
            archive_base.extend([f"--git-dir={git_dir}"])
        else:
            archive_base.extend(["-C", str(repo_root)])
        with tree_path.open("wb") as handle:
            subprocess.run([*archive_base, "archive", "--format=tar", commit], check=True, stdout=handle)
        content_files.append(tree_path)
        tree_archive_included = True
    else:
        write_text(
            tree_note_path,
            "Tree archive omitted in this smoke bundle to avoid committing a duplicate repository snapshot; "
            "the verified commit SHA can reproduce the tree from the Throne mirror.\n",
        )
        content_files.append(tree_note_path)
        caps_triggered.append(CAP_TREE_ARCHIVE_OMITTED)

    write_json(
        receipts_path,
        {
            "schema_version": "THRONE_RECEIPTS_MANIFEST_V0_1",
            "generated_at_utc": utc_now(),
            "commit_sha": commit,
            "files": [path.name for path in content_files],
        },
    )
    content_files.append(receipts_path)
    content_tar = create_content_tar(output_dir, content_files)

    manifest_path = output_dir / "commit_evidence_bundle_manifest.json"
    manifest = {
        "schema_version": SCHEMA_VERSION,
        "commit_sha": commit,
        "parent_sha": parent_sha,
        "exported_for": args.exported_for,
        "exported_at_utc": utc_now(),
        "git_object_verified": True,
        "tree_archive_included": tree_archive_included,
        "diff_patch_included": True,
        "changed_files_manifest_included": True,
        "receipts_manifest_included": True,
        "sha256sums_included": True,
        "bundle_sha256": sha256_file(content_tar),
        "caps_triggered": caps_triggered,
    }
    write_json(manifest_path, manifest)

    sha_path = write_sha256s(output_dir, [*content_files, content_tar, manifest_path])
    return {
        "status": "PASS",
        "commit_sha": commit,
        "output_dir": str(output_dir),
        "manifest_path": str(manifest_path),
        "sha256sums_path": str(sha_path),
        "bundle_artifact_path": str(content_tar),
        "bundle_sha256": manifest["bundle_sha256"],
        "tree_archive_included": tree_archive_included,
        "caps_triggered": caps_triggered,
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    source = parser.add_mutually_exclusive_group(required=True)
    source.add_argument("--repo-root")
    source.add_argument("--git-dir")
    parser.add_argument("--commit", required=True)
    parser.add_argument("--output-dir", required=True)
    parser.add_argument("--exported-for", default="OWNER", choices=["LOGOS_PRIME", "INQUISITION", "SPECULUM", "OWNER", "GENERAL_REVIEW"])
    parser.add_argument("--include-tree-archive", action="store_true")
    return parser.parse_args()


def main() -> int:
    try:
        result = export_bundle(parse_args())
    except subprocess.CalledProcessError as exc:
        print(json.dumps({"status": "BLOCK", "reason": "git_command_failed", "stderr": exc.stderr}, ensure_ascii=True))
        return 2
    except Exception as exc:
        print(json.dumps({"status": "BLOCK", "reason": repr(exc)}, ensure_ascii=True))
        return 2
    print(json.dumps(result, ensure_ascii=True))
    return 0


if __name__ == "__main__":
    sys.exit(main())
