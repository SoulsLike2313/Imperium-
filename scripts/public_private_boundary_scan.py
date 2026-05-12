#!/usr/bin/env python3
"""Gate: scan tracked text files for obvious secret and boundary leaks."""

from __future__ import annotations

import json
from pathlib import Path
import re
import sys
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = REPO_ROOT / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from imperium.receipts.model import Verdict, utc_timestamp
from imperium.security.command_gateway import run_allowed
from imperium.security.path_policy import find_absolute_local_paths


PRIVATE_KEY_RE = re.compile(r"-----BEGIN [A-Z0-9 ]*PRIVATE KEY-----")
GHP_TOKEN_RE = re.compile(r"\bghp_[A-Za-z0-9]{20,}\b")
ASSIGN_RE = re.compile(
    r"(?i)\b(password|secret|token|credential)\b\s*[:=]\s*[\"']([^\"']+)[\"']"
)
PLACEHOLDER_TOKENS = {"example", "placeholder", "sample", "redacted", "your", "change_me"}
MAX_DETAIL_ITEMS = 200



def _truncate(items: list[str]) -> tuple[list[str], int]:
    if len(items) <= MAX_DETAIL_ITEMS:
        return items, 0
    return items[:MAX_DETAIL_ITEMS], len(items) - MAX_DETAIL_ITEMS



def _tracked_files(repo_root: Path) -> list[Path]:
    receipt = run_allowed("git.ls_files", cwd=repo_root, root=repo_root)
    if receipt["verdict"] not in {Verdict.PASS.value, Verdict.PASS_WITH_WARNINGS.value}:
        return []
    return [Path(line.strip()) for line in receipt["stdout"].splitlines() if line.strip()]



def _is_text_file(file_path: Path) -> bool:
    try:
        sample = file_path.read_bytes()[:4096]
    except Exception:
        return False
    return b"\x00" not in sample



def run_gate(root: Path | None = None) -> dict[str, Any]:
    repo_root = (root or REPO_ROOT).resolve()
    files = _tracked_files(repo_root)

    blockers: list[str] = []
    warnings: list[str] = []
    errors: list[str] = []
    scanned_files = 0

    for rel_path in files:
        abs_path = repo_root / rel_path
        if not abs_path.exists() or not _is_text_file(abs_path):
            continue

        scanned_files += 1

        try:
            text = abs_path.read_text(encoding="utf-8", errors="replace")
        except Exception as exc:
            errors.append(f"{rel_path.as_posix()} read error: {exc}")
            continue

        if PRIVATE_KEY_RE.search(text):
            blockers.append(f"{rel_path.as_posix()} contains private key header.")

        if GHP_TOKEN_RE.search(text):
            blockers.append(f"{rel_path.as_posix()} contains ghp_ token-like pattern.")

        for match in ASSIGN_RE.finditer(text):
            key_name = match.group(1).lower()
            value = match.group(2).strip()
            lowered = value.lower()
            if any(token in lowered for token in PLACEHOLDER_TOKENS):
                continue
            if len(value) >= 20 and " " not in value:
                blockers.append(
                    f"{rel_path.as_posix()} contains {key_name} assignment with non-placeholder value."
                )

        for token in find_absolute_local_paths(text):
            warnings.append(f"{rel_path.as_posix()} contains absolute local path token: {token}")

    listed_blockers, omitted_blockers = _truncate(blockers)
    listed_warnings, omitted_warnings = _truncate(warnings)
    if omitted_blockers:
        listed_warnings.append(f"Omitted {omitted_blockers} blocker details from gate output.")
    if omitted_warnings:
        listed_warnings.append(f"Omitted {omitted_warnings} warning details from gate output.")

    verdict = Verdict.PASS.value
    if blockers:
        verdict = Verdict.FAIL.value
    elif warnings:
        verdict = Verdict.PASS_WITH_WARNINGS.value

    return {
        "schema_version": "imperium.verification_gate.v0_1",
        "gate_id": "public_private_boundary_scan",
        "timestamp_utc": utc_timestamp(),
        "verdict": verdict,
        "blockers": listed_blockers,
        "warnings": listed_warnings,
        "errors": errors,
        "metrics": {
            "scanned_text_files": scanned_files,
            "blockers": len(blockers),
            "warnings": len(warnings),
            "listed_blockers": len(listed_blockers),
            "omitted_blockers": omitted_blockers,
            "listed_warnings": len(listed_warnings),
            "omitted_warnings": omitted_warnings,
        },
    }



def main() -> int:
    report = run_gate()
    print(json.dumps(report, indent=2))
    return 1 if report["verdict"] in {Verdict.FAIL.value, Verdict.BLOCKED.value} else 0


if __name__ == "__main__":
    raise SystemExit(main())
