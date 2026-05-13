#!/usr/bin/env python3
"""Checker for repo parity and external context policy v0.2."""

from __future__ import annotations

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
    out: list[Path] = []
    for raw in status.splitlines():
        if not raw:
            continue
        payload = raw[3:]
        if " -> " in payload:
            payload = payload.split(" -> ", 1)[1]
        out.append(repo_root / payload)
    return out


def main() -> int:
    repo_root = Path(__file__).resolve().parents[1]

    passed: list[str] = []
    blocked: list[str] = []
    warned: list[str] = []

    def check(ok: bool, pass_msg: str, fail_msg: str) -> None:
        if ok:
            passed.append(pass_msg)
        else:
            blocked.append(fail_msg)

    def warn(msg: str) -> None:
        warned.append(msg)

    advisory = repo_root / (
        "ORGANS/ASTRONOMICON/REGISTRY/ADVISORY_RESPONSES/"
        "ADVISORY-RESPONSE-20260513-KIRO-SAN-CLEANING-BACKEND-TRUTH-V0_1.md"
    )
    check(advisory.is_file(), "Kiro advisory exists.", "Kiro advisory is missing.")

    required_files = [
        "ORGANS/ASTRONOMICON/REGISTRY/SAN_CLEANING/REPO_PARITY_AND_EXTERNAL_CONTEXT_POLICY_V0_2.md",
        "ORGANS/ASTRONOMICON/REGISTRY/SAN_CLEANING/LOCAL_PRIVATE_EXTERNALIZATION_PLAN_V0_2.md",
        "ORGANS/ASTRONOMICON/REGISTRY/SAN_CLEANING/REPO_PARITY_MIGRATION_REPORT_20260513.md",
        "ORGANS/ASTRONOMICON/REGISTRY/SAN_CLEANING/SAN_CLEANING_EXECUTION_PLAN_V0_1.md",
        "ORGANS/ASTRONOMICON/REGISTRY/SAN_CLEANING/REPO_TAXONOMY_TARGET_V0_1.md",
        "ORGANS/ADMINISTRATUM/REGISTRY/LOCAL_PRIVATE_CONTEXT_PATHS_V0_2.md",
        "CURRENT_STATE/REPO_PARITY_EXTERNALIZATION_V0_2_20260513_REPORT.md",
        "TOOLS/pc_externalize_local_private_context_v0_2.ps1",
        "TOOLS/check_repo_parity_external_context_v0_2.py",
    ]
    for rel in required_files:
        p = repo_root / rel
        check(p.is_file(), f"Required file exists: {rel}", f"Missing required file: {rel}")

    policy_files = [
        repo_root / "ORGANS/ASTRONOMICON/REGISTRY/SAN_CLEANING/REPO_PARITY_AND_EXTERNAL_CONTEXT_POLICY_V0_2.md",
        repo_root / "ORGANS/ASTRONOMICON/REGISTRY/SAN_CLEANING/LOCAL_PRIVATE_EXTERNALIZATION_PLAN_V0_2.md",
        repo_root / "ORGANS/ADMINISTRATUM/REGISTRY/LOCAL_PRIVATE_CONTEXT_PATHS_V0_2.md",
    ]
    combined_policy_text = "\n".join(
        p.read_text(encoding="utf-8", errors="ignore") for p in policy_files if p.is_file()
    )
    low = combined_policy_text.lower()

    check("E:\\IMPERIUM" in combined_policy_text, "Policy mentions E:\\IMPERIUM.", "Policy missing E:\\IMPERIUM.")
    check(
        "E:\\IMPERIUM_LOCAL" in combined_policy_text,
        "Policy mentions E:\\IMPERIUM_LOCAL.",
        "Policy missing E:\\IMPERIUM_LOCAL.",
    )
    check(
        "E:\\IMPERIUM_PRIVATE" in combined_policy_text,
        "Policy mentions E:\\IMPERIUM_PRIVATE.",
        "Policy missing E:\\IMPERIUM_PRIVATE.",
    )
    check(
        "/home/vboxuser2/IMPERIUM_WORK/Imperium-" in combined_policy_text,
        "Policy mentions VM2 root path.",
        "Policy missing VM2 root path.",
    )

    check(
        "canonical tracked worktree" in low or "canonical git worktree" in low,
        "Policy states canonical tracked/git worktree boundary.",
        "Policy does not clearly state canonical tracked/git worktree boundary.",
    )
    check(
        "outside" in low and "repo" in low,
        "Policy states local/private payloads must live outside repo.",
        "Policy does not clearly state local/private payloads must live outside repo.",
    )
    check(
        "scriptorium" in low and "arsenal" in low and "mechanicus" in low,
        "Policy states SCRIPTORIUM and ARSENAL live under MECHANICUS.",
        "Policy missing SCRIPTORIUM/ARSENAL under MECHANICUS statement.",
    )

    # Mechanicus seed docs exist in this repo; validate and warn if weak.
    mech_docs = [
        repo_root / "ORGANS/MECHANICUS/README_MECHANICUS_PENDING_FORMALIZATION.md",
        repo_root / "ORGANS/MECHANICUS/SCRIPTORIUM/README_SCRIPTORIUM_UNDER_MECHANICUS.md",
        repo_root / "ORGANS/MECHANICUS/ARSENAL/README_ARSENAL_UNDER_MECHANICUS.md",
    ]
    missing_mech = [str(p.relative_to(repo_root)) for p in mech_docs if not p.is_file()]
    if missing_mech:
        warn("Mechanicus hierarchy docs missing: " + ", ".join(missing_mech))
    else:
        mech_low = "\n".join(p.read_text(encoding="utf-8", errors="ignore") for p in mech_docs).lower()
        if "not an independent organ" not in mech_low:
            warn("Mechanicus hierarchy docs do not explicitly repeat 'not an independent organ'.")
        else:
            passed.append("Mechanicus hierarchy docs describe SCRIPTORIUM/ARSENAL as non-organs under MECHANICUS.")

    report_path = repo_root / "CURRENT_STATE/REPO_PARITY_EXTERNALIZATION_V0_2_20260513_REPORT.md"
    if report_path.is_file():
        report_text = report_path.read_text(encoding="utf-8", errors="ignore").lower()
        check(
            "pc_access_method" in report_text and "pc_access_verdict" in report_text,
            "Current-state report states PC access method and verdict.",
            "Current-state report missing PC access method/verdict fields.",
        )
    else:
        blocked.append("Current-state report missing; cannot verify PC access status language.")

    try:
        sanctum_status = run_git(repo_root, "status", "--short", "--", "SANCTUM/sanctum_v0_29_qt.py").strip()
        check(
            sanctum_status == "",
            "SANCTUM/sanctum_v0_29_qt.py is not modified.",
            "SANCTUM/sanctum_v0_29_qt.py is modified (forbidden).",
        )
    except Exception as exc:  # noqa: BLE001
        blocked.append(f"Could not verify SANCTUM file status: {exc}")

    try:
        changed = changed_paths(repo_root)
    except Exception as exc:  # noqa: BLE001
        blocked.append(f"Could not collect changed paths: {exc}")
        changed = []

    forbidden_added = []
    forbidden_re = re.compile(r"SANCTUM/.+(EE|R1|R2|v0_30EE)", re.IGNORECASE)
    for p in changed:
        rel = str(p.relative_to(repo_root)).replace("\\", "/")
        if forbidden_re.search(rel):
            forbidden_added.append(rel)

    check(
        not forbidden_added,
        "No forbidden Sanctum EE/R1/R2 path additions detected.",
        "Forbidden Sanctum EE/R1/R2 path changes detected: " + ", ".join(forbidden_added),
    )

    ready_pattern = re.compile(r'(?i)"?ready_for_agent"?\s*[:=]?\s*true')
    ready_hits: list[str] = []
    checker_self = (repo_root / "TOOLS/check_repo_parity_external_context_v0_2.py").resolve()

    for p in changed:
        if not p.exists() or not p.is_file():
            continue
        if p.resolve() == checker_self:
            continue
        if not is_text_file(p):
            continue
        text = p.read_text(encoding="utf-8", errors="ignore")
        if ready_pattern.search(text):
            ready_hits.append(str(p.relative_to(repo_root)))

    check(
        len(ready_hits) == 0,
        "No changed text file introduces READY_FOR_AGENT=true.",
        "READY_FOR_AGENT=true introduced in: " + ", ".join(ready_hits),
    )

    print("=== PASS ===")
    for msg in passed:
        print(f"[PASS] {msg}")
    if not passed:
        print("[PASS] none")

    print("\n=== WARN ===")
    for msg in warned:
        print(f"[WARN] {msg}")
    if not warned:
        print("[WARN] none")

    print("\n=== BLOCKED ===")
    for msg in blocked:
        print(f"[BLOCKED] {msg}")
    if not blocked:
        print("[BLOCKED] none")

    if blocked:
        print("\nFINAL VERDICT: BLOCKED")
        return 1

    print("\nFINAL VERDICT: PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
