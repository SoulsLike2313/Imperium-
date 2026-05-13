#!/usr/bin/env python3
"""San-Cleaning entry checker v0.1."""

from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path


def run_git(repo_root: Path, *args: str) -> str:
    result = subprocess.run(
        ["git", *args],
        cwd=str(repo_root),
        check=False,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        raise RuntimeError(f"git {' '.join(args)} failed: {result.stderr.strip()}")
    return result.stdout


def is_text_file(path: Path) -> bool:
    try:
        data = path.read_bytes()
    except OSError:
        return False
    if b"\x00" in data:
        return False
    return True


def changed_paths(repo_root: Path) -> list[Path]:
    status = run_git(repo_root, "status", "--porcelain")
    paths: list[Path] = []
    for raw_line in status.splitlines():
        if not raw_line:
            continue
        line = raw_line.rstrip("\n")
        payload = line[3:]
        if " -> " in payload:
            payload = payload.split(" -> ", 1)[1]
        p = repo_root / payload
        if p.exists() and p.is_file():
            paths.append(p)
    # De-duplicate while preserving order.
    seen = set()
    unique_paths = []
    for p in paths:
        s = str(p)
        if s in seen:
            continue
        seen.add(s)
        unique_paths.append(p)
    return unique_paths


def main() -> int:
    repo_root = Path(__file__).resolve().parents[1]

    pass_msgs: list[str] = []
    fail_msgs: list[str] = []

    def check(ok: bool, pass_msg: str, fail_msg: str) -> None:
        if ok:
            pass_msgs.append(pass_msg)
        else:
            fail_msgs.append(fail_msg)

    archive_dir = repo_root / "ARCHIVE"
    observed_dir = repo_root / "OBSERVED"
    check(
        not archive_dir.exists(),
        "ARCHIVE directory is absent.",
        "ARCHIVE directory is present.",
    )
    check(
        not observed_dir.exists(),
        "OBSERVED directory is absent.",
        "OBSERVED directory is present.",
    )

    kiro_advisory = repo_root / (
        "ORGANS/ASTRONOMICON/REGISTRY/ADVISORY_RESPONSES/"
        "ADVISORY-RESPONSE-20260513-KIRO-SAN-CLEANING-BACKEND-TRUTH-V0_1.md"
    )
    check(
        kiro_advisory.is_file(),
        "Kiro advisory file exists.",
        "Kiro advisory file is missing.",
    )

    san_cleaning_dir = repo_root / "ORGANS/ASTRONOMICON/REGISTRY/SAN_CLEANING"
    check(
        san_cleaning_dir.is_dir(),
        "SAN_CLEANING registry directory exists.",
        "SAN_CLEANING registry directory is missing.",
    )

    required_files = [
        "ORGANS/ASTRONOMICON/REGISTRY/SAN_CLEANING/README_SAN_CLEANING.md",
        "ORGANS/ASTRONOMICON/REGISTRY/SAN_CLEANING/KIRO_ADVISORY_SECTION_MAP_20260513.md",
        "ORGANS/ASTRONOMICON/REGISTRY/SAN_CLEANING/SAN_CLEANING_EXECUTION_PLAN_V0_1.md",
        "ORGANS/ASTRONOMICON/REGISTRY/SAN_CLEANING/REPO_TAXONOMY_TARGET_V0_1.md",
        "ORGANS/ASTRONOMICON/REGISTRY/SAN_CLEANING/APPROVED_DELETION_MANIFEST_20260513.json",
        "CURRENT_STATE/SAN_CLEANING_ENTRY_20260513_REPORT.md",
        "ORGANS/MECHANICUS/README_MECHANICUS_PENDING_FORMALIZATION.md",
        "ORGANS/MECHANICUS/SCRIPTORIUM/README_SCRIPTORIUM_UNDER_MECHANICUS.md",
        "ORGANS/MECHANICUS/ARSENAL/README_ARSENAL_UNDER_MECHANICUS.md",
    ]
    for rel in required_files:
        p = repo_root / rel
        check(p.is_file(), f"Required file exists: {rel}", f"Missing required file: {rel}")

    manifest_path = repo_root / (
        "ORGANS/ASTRONOMICON/REGISTRY/SAN_CLEANING/"
        "APPROVED_DELETION_MANIFEST_20260513.json"
    )
    manifest = None
    if manifest_path.is_file():
        try:
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
            pass_msgs.append("Deletion manifest parses as valid JSON.")
        except Exception as exc:  # noqa: BLE001
            fail_msgs.append(f"Deletion manifest JSON parse failed: {exc}")

    if manifest is not None:
        owner_auth = manifest.get("owner_authorization", {})
        owner_targets = set(owner_auth.get("authorized_targets", []))
        owner_allowed = bool(owner_auth.get("authorized", False))
        entries = manifest.get("entries", [])
        by_target = {
            str(entry.get("target_path", "")).strip(): entry
            for entry in entries
            if isinstance(entry, dict)
        }
        for target in ("ARCHIVE", "OBSERVED"):
            entry = by_target.get(target)
            check(
                isinstance(entry, dict),
                f"Manifest includes entry for {target}.",
                f"Manifest missing entry for {target}.",
            )
            if isinstance(entry, dict):
                check(
                    bool(entry.get("deletion_authorized_by_owner", False)),
                    f"Manifest entry marks owner authorization for {target}.",
                    f"Manifest entry missing owner authorization for {target}.",
                )
                check(
                    bool(entry.get("checked_absent_after", False)),
                    f"Manifest confirms {target} absent after deletion check.",
                    f"Manifest does not confirm {target} absent after deletion check.",
                )
        check(
            owner_allowed and {"ARCHIVE", "OBSERVED"}.issubset(owner_targets),
            "Manifest owner authorization includes ARCHIVE and OBSERVED.",
            "Manifest owner authorization is incomplete for ARCHIVE/OBSERVED.",
        )

    mechanicus_file = repo_root / "ORGANS/MECHANICUS/README_MECHANICUS_PENDING_FORMALIZATION.md"
    scriptorium_file = repo_root / "ORGANS/MECHANICUS/SCRIPTORIUM/README_SCRIPTORIUM_UNDER_MECHANICUS.md"
    arsenal_file = repo_root / "ORGANS/MECHANICUS/ARSENAL/README_ARSENAL_UNDER_MECHANICUS.md"
    taxonomy_file = repo_root / "ORGANS/ASTRONOMICON/REGISTRY/SAN_CLEANING/REPO_TAXONOMY_TARGET_V0_1.md"

    combined_text = "\n".join(
        p.read_text(encoding="utf-8")
        for p in (mechanicus_file, scriptorium_file, arsenal_file, taxonomy_file)
        if p.is_file()
    ).lower()
    check(
        "scriptorium" in combined_text and "mechanicus" in combined_text,
        "Files state that SCRIPTORIUM lives under MECHANICUS.",
        "Could not verify SCRIPTORIUM-under-MECHANICUS statement.",
    )
    check(
        "arsenal" in combined_text and "mechanicus" in combined_text,
        "Files state that ARSENAL lives under MECHANICUS.",
        "Could not verify ARSENAL-under-MECHANICUS statement.",
    )

    try:
        sanctum_status = run_git(repo_root, "status", "--short", "--", "SANCTUM/sanctum_v0_29_qt.py").strip()
        check(
            sanctum_status == "",
            "SANCTUM/sanctum_v0_29_qt.py is not modified.",
            "SANCTUM/sanctum_v0_29_qt.py was modified, which is forbidden.",
        )
    except Exception as exc:  # noqa: BLE001
        fail_msgs.append(f"Could not verify SANCTUM file status: {exc}")

    ready_pattern = re.compile(r'(?i)"?ready_for_agent"?\s*[:=]?\s*true')
    try:
        changed = changed_paths(repo_root)
    except Exception as exc:  # noqa: BLE001
        fail_msgs.append(f"Could not list changed files for READY_FOR_AGENT scan: {exc}")
        changed = []

    ready_hits: list[str] = []
    scanner_self = (repo_root / "TOOLS/check_san_cleaning_entry_v0_1.py").resolve()
    for file_path in changed:
        if file_path.resolve() == scanner_self:
            continue
        if not is_text_file(file_path):
            continue
        try:
            text = file_path.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            continue
        if ready_pattern.search(text):
            ready_hits.append(str(file_path.relative_to(repo_root)))

    check(
        len(ready_hits) == 0,
        "No changed text file introduces READY_FOR_AGENT true.",
        "READY_FOR_AGENT true introduced in: " + ", ".join(ready_hits),
    )

    print("=== PASS ===")
    if pass_msgs:
        for msg in pass_msgs:
            print(f"[PASS] {msg}")
    else:
        print("[PASS] none")

    print("\n=== BLOCKED ===")
    if fail_msgs:
        for msg in fail_msgs:
            print(f"[BLOCKED] {msg}")
    else:
        print("[BLOCKED] none")

    if fail_msgs:
        print("\nFINAL VERDICT: BLOCKED")
        return 1

    print("\nFINAL VERDICT: PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
