#!/usr/bin/env python3
"""Checker for external context registry and address repair v0.1."""

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
    return b"\x00" not in data


def changed_paths(repo_root: Path) -> list[Path]:
    status = run_git(repo_root, "status", "--porcelain")
    out: list[Path] = []
    for line in status.splitlines():
        if not line:
            continue
        payload = line[3:]
        if " -> " in payload:
            payload = payload.split(" -> ", 1)[1]
        out.append(repo_root / payload)
    return out


def main() -> int:
    repo_root = Path(__file__).resolve().parents[1]
    passes: list[str] = []
    warns: list[str] = []
    blocks: list[str] = []

    def check(ok: bool, ok_msg: str, bad_msg: str) -> None:
        if ok:
            passes.append(ok_msg)
        else:
            blocks.append(bad_msg)

    required_files = [
        "ORGANS/ADMINISTRATUM/REGISTRY/EXTERNAL_CONTEXT_PATHS_V0_1.md",
        "ORGANS/ADMINISTRATUM/REGISTRY/PROMPT_AND_BUNDLE_ROUTE_MAP_V0_1.md",
        "ORGANS/ADMINISTRATUM/REGISTRY/CONTINUITY_AND_HANDOFF_CONTEXT_PATHS_V0_1.md",
        "ORGANS/ASTRONOMICON/REGISTRY/SAN_CLEANING/EXTERNAL_CONTEXT_REGISTRY_PLAN_V0_1.md",
        "ORGANS/ASTRONOMICON/REGISTRY/SAN_CLEANING/ADDRESS_REPAIR_PLAN_V0_1.md",
        "ORGANS/ASTRONOMICON/REGISTRY/SAN_CLEANING/EXTERNAL_CONTEXT_AND_ADDRESS_REPAIR_REPORT_20260514.md",
        "ORGANS/ASTRONOMICON/REGISTRY/SAN_CLEANING/SAN_CLEANING_EXECUTION_PLAN_V0_1.md",
        "CURRENT_STATE/EXTERNAL_CONTEXT_INDEX_20260514.json",
        "CURRENT_STATE/EXTERNAL_CONTEXT_INDEX_20260514.md",
        "CURRENT_STATE/ADDRESS_REPAIR_REPORT_20260514.md",
        "TOOLS/pc_index_external_context_v0_1.ps1",
        "TOOLS/check_external_context_registry_v0_1.py",
    ]
    for rel in required_files:
        p = repo_root / rel
        check(p.is_file(), f"Required file exists: {rel}", f"Missing required file: {rel}")

    kiro = repo_root / "ORGANS/ASTRONOMICON/REGISTRY/ADVISORY_RESPONSES/ADVISORY-RESPONSE-20260513-KIRO-SAN-CLEANING-BACKEND-TRUTH-V0_1.md"
    check(kiro.is_file(), "Kiro advisory exists.", "Kiro advisory missing.")

    idx_path = repo_root / "CURRENT_STATE/EXTERNAL_CONTEXT_INDEX_20260514.json"
    idx = None
    if idx_path.is_file():
        try:
            idx = json.loads(idx_path.read_text(encoding="utf-8"))
            passes.append("External context index JSON parses.")
        except Exception as exc:  # noqa: BLE001
            blocks.append(f"External context index JSON parse failed: {exc}")

    if isinstance(idx, dict):
        text = json.dumps(idx, ensure_ascii=True)
        check(
            "E:\\\\IMPERIUM_CONTEXT\\\\LOCAL" in text,
            "Index mentions E:\\IMPERIUM_CONTEXT\\LOCAL.",
            "Index missing E:\\IMPERIUM_CONTEXT\\LOCAL.",
        )
        check(
            "E:\\\\IMPERIUM_CONTEXT\\\\PRIVATE" in text,
            "Index mentions E:\\IMPERIUM_CONTEXT\\PRIVATE.",
            "Index missing E:\\IMPERIUM_CONTEXT\\PRIVATE.",
        )

    docs_to_scan = [
        repo_root / "ORGANS/ADMINISTRATUM/REGISTRY/EXTERNAL_CONTEXT_PATHS_V0_1.md",
        repo_root / "ORGANS/ADMINISTRATUM/REGISTRY/PROMPT_AND_BUNDLE_ROUTE_MAP_V0_1.md",
        repo_root / "ORGANS/ADMINISTRATUM/REGISTRY/CONTINUITY_AND_HANDOFF_CONTEXT_PATHS_V0_1.md",
        repo_root / "ORGANS/ASTRONOMICON/REGISTRY/SAN_CLEANING/ADDRESS_REPAIR_PLAN_V0_1.md",
        repo_root / "ORGANS/ASTRONOMICON/REGISTRY/SAN_CLEANING/EXTERNAL_CONTEXT_REGISTRY_PLAN_V0_1.md",
        repo_root / "ORGANS/ASTRONOMICON/REGISTRY/SAN_CLEANING/EXTERNAL_CONTEXT_AND_ADDRESS_REPAIR_REPORT_20260514.md",
        repo_root / "CURRENT_STATE/ADDRESS_REPAIR_REPORT_20260514.md",
    ]
    merged = "\n".join(
        p.read_text(encoding="utf-8", errors="ignore") for p in docs_to_scan if p.is_file()
    )
    low = merged.lower()

    check(
        "pc -> vm2" in low or "pc->vm2" in low,
        "Docs mention PC->VM2 route.",
        "Docs missing PC->VM2 route mention.",
    )
    check(
        "vm2 -> pc" in low or "vm2->pc" in low,
        "Docs mention VM2->PC route.",
        "Docs missing VM2->PC route mention.",
    )
    check(
        "owner-controlled" in low or "owner controlled" in low,
        "Docs mention Owner-controlled private context.",
        "Docs missing Owner-controlled private context mention.",
    )
    check(
        "must never be committed" in low or "not committed" in low,
        "Docs mention no private payload committed policy.",
        "Docs missing no-private-payload-commit policy language.",
    )
    check(
        "scriptorium" in low and "arsenal" in low and "mechanicus" in low,
        "Docs preserve Mechanicus ownership for SCRIPTORIUM/ARSENAL.",
        "Docs missing Mechanicus ownership reminder for SCRIPTORIUM/ARSENAL.",
    )
    check(
        ("route_verdict: `pass`" in low)
        or ("route_verdict: `blocked`" in low)
        or ("pc access worked" in low)
        or ("pc access is blocked" in low),
        "Report states whether PC access worked or was blocked.",
        "Report does not clearly state whether PC access worked or was blocked.",
    )

    # Sanity checks for forbidden edits.
    try:
        sanctum_status = run_git(repo_root, "status", "--short", "--", "SANCTUM/sanctum_v0_29_qt.py").strip()
        check(
            sanctum_status == "",
            "SANCTUM/sanctum_v0_29_qt.py not modified.",
            "SANCTUM/sanctum_v0_29_qt.py modified (forbidden).",
        )
    except Exception as exc:  # noqa: BLE001
        blocks.append(f"Could not verify SANCTUM file status: {exc}")

    try:
        changed = changed_paths(repo_root)
    except Exception as exc:  # noqa: BLE001
        blocks.append(f"Could not get changed paths: {exc}")
        changed = []

    forb = []
    forb_re = re.compile(r"SANCTUM/.+(EE|R1|R2|v0_30EE)", re.IGNORECASE)
    for p in changed:
        rel = str(p.relative_to(repo_root)).replace("\\", "/")
        if forb_re.search(rel):
            forb.append(rel)
    check(
        len(forb) == 0,
        "No forbidden Sanctum EE/R1/R2 path changes.",
        "Forbidden Sanctum EE/R1/R2 path changes detected: " + ", ".join(forb),
    )

    ready_re = re.compile(r'(?i)"?ready_for_agent"?\s*[:=]?\s*true')
    ready_hits: list[str] = []
    self_path = (repo_root / "TOOLS/check_external_context_registry_v0_1.py").resolve()
    for p in changed:
        if not p.exists() or not p.is_file():
            continue
        if p.resolve() == self_path:
            continue
        if not is_text_file(p):
            continue
        txt = p.read_text(encoding="utf-8", errors="ignore")
        if ready_re.search(txt):
            ready_hits.append(str(p.relative_to(repo_root)))
    check(
        len(ready_hits) == 0,
        "No changed text file introduces READY_FOR_AGENT=true.",
        "READY_FOR_AGENT=true introduced in: " + ", ".join(ready_hits),
    )

    # Optional schema warning.
    schema = repo_root / "schemas/external_context_index_v0_1.schema.json"
    if schema.is_file():
        warns.append("Optional schema present: schemas/external_context_index_v0_1.schema.json")
    else:
        warns.append("Optional schema missing (allowed).")

    print("=== PASS ===")
    for m in passes:
        print(f"[PASS] {m}")
    if not passes:
        print("[PASS] none")

    print("\n=== WARN ===")
    for m in warns:
        print(f"[WARN] {m}")
    if not warns:
        print("[WARN] none")

    print("\n=== BLOCKED ===")
    for m in blocks:
        print(f"[BLOCKED] {m}")
    if not blocks:
        print("[BLOCKED] none")

    if blocks:
        print("\nFINAL VERDICT: BLOCKED")
        return 1

    print("\nFINAL VERDICT: PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
