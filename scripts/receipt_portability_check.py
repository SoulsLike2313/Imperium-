#!/usr/bin/env python3
"""Gate: detect non-portable absolute paths in receipt/manifest/hash artifacts."""

from __future__ import annotations

import json
from pathlib import Path
import sys
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = REPO_ROOT / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from imperium.receipts.model import Verdict, utc_timestamp
from imperium.security.command_gateway import run_allowed
from imperium.security.path_policy import find_absolute_local_paths


TARGET_KEYWORDS = {"receipt", "manifest", "hash", "sha256", "verdict", "report"}
SAFE_MARKERS = {"redacted", "fingerprint", "sha256", "hash"}
NEW_SPINE_PREFIXES = {"src/imperium", "scripts", "tests", "schemas", "DOCS"}
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



def _is_target(path: Path) -> bool:
    joined = path.as_posix().lower()
    return any(keyword in joined for keyword in TARGET_KEYWORDS)



def _is_new_spine(path: Path) -> bool:
    joined = path.as_posix()
    return any(joined.startswith(prefix + "/") or joined == prefix for prefix in NEW_SPINE_PREFIXES)



def run_gate(root: Path | None = None) -> dict[str, Any]:
    repo_root = (root or REPO_ROOT).resolve()
    files = _tracked_files(repo_root)

    blockers: list[str] = []
    warnings: list[str] = []
    errors: list[str] = []
    scanned_files = 0

    for rel_path in files:
        if not _is_target(rel_path):
            continue

        abs_path = repo_root / rel_path
        if not abs_path.exists() or abs_path.suffix.lower() not in {".json", ".md", ".txt", ".yaml", ".yml"}:
            continue

        scanned_files += 1

        try:
            lines = abs_path.read_text(encoding="utf-8", errors="replace").splitlines()
        except Exception as exc:
            errors.append(f"{rel_path.as_posix()} read error: {exc}")
            continue

        for line_number, line in enumerate(lines, start=1):
            tokens = find_absolute_local_paths(line)
            if not tokens:
                continue
            lowered = line.lower()
            has_safe_marker = any(marker in lowered for marker in SAFE_MARKERS)

            for token in tokens:
                finding = f"{rel_path.as_posix()}:{line_number} absolute path token: {token}"
                if _is_new_spine(rel_path) and not has_safe_marker:
                    blockers.append(finding)
                else:
                    warnings.append(finding)

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
        "gate_id": "receipt_portability_check",
        "timestamp_utc": utc_timestamp(),
        "verdict": verdict,
        "blockers": listed_blockers,
        "warnings": listed_warnings,
        "errors": errors,
        "metrics": {
            "scanned_files": scanned_files,
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
