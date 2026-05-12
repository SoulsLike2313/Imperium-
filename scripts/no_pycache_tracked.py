#!/usr/bin/env python3
"""Gate: fail when tracked pycache artifacts exist."""

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


MAX_DETAIL_ITEMS = 200



def _truncate(items: list[str]) -> tuple[list[str], int]:
    if len(items) <= MAX_DETAIL_ITEMS:
        return items, 0
    return items[:MAX_DETAIL_ITEMS], len(items) - MAX_DETAIL_ITEMS



def run_gate(root: Path | None = None) -> dict[str, Any]:
    repo_root = (root or REPO_ROOT).resolve()
    receipt = run_allowed("git.ls_files", cwd=repo_root, root=repo_root)

    warnings: list[str] = []
    errors: list[str] = []
    blockers: list[str] = []

    if receipt["verdict"] not in {Verdict.PASS.value, Verdict.PASS_WITH_WARNINGS.value}:
        errors.extend(receipt.get("errors", []))
        return {
            "schema_version": "imperium.verification_gate.v0_1",
            "gate_id": "no_pycache_tracked",
            "timestamp_utc": utc_timestamp(),
            "verdict": Verdict.FAIL.value,
            "blockers": blockers,
            "warnings": warnings,
            "errors": errors,
            "metrics": {"tracked_files": 0, "pycache_findings": 0, "listed_blockers": 0, "omitted_blockers": 0},
        }

    tracked_files = [line.strip() for line in receipt.get("stdout", "").splitlines() if line.strip()]
    for rel_path in tracked_files:
        if "__pycache__/" in rel_path or rel_path.endswith((".pyc", ".pyo", ".pyd")):
            blockers.append(rel_path)

    listed_blockers, omitted_blockers = _truncate(blockers)
    if omitted_blockers:
        warnings.append(f"Omitted {omitted_blockers} additional pycache findings from gate detail.")

    verdict = Verdict.FAIL.value if blockers else Verdict.PASS.value

    return {
        "schema_version": "imperium.verification_gate.v0_1",
        "gate_id": "no_pycache_tracked",
        "timestamp_utc": utc_timestamp(),
        "verdict": verdict,
        "blockers": listed_blockers,
        "warnings": warnings,
        "errors": errors,
        "metrics": {
            "tracked_files": len(tracked_files),
            "pycache_findings": len(blockers),
            "listed_blockers": len(listed_blockers),
            "omitted_blockers": omitted_blockers,
        },
    }



def main() -> int:
    report = run_gate()
    print(json.dumps(report, indent=2))
    return 1 if report["verdict"] in {Verdict.FAIL.value, Verdict.BLOCKED.value} else 0


if __name__ == "__main__":
    raise SystemExit(main())
