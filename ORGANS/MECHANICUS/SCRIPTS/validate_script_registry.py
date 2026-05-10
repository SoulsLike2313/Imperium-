#!/usr/bin/env python3
"""Validate Mechanicus script registry contains required IDs."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

REQUIRED_IDS = {
    "TOOL-ADMIN-CREATE-TASK-LAUNCH-CARD",
    "TOOL-ADMIN-CREATE-REPAIR-BRANCH",
    "TOOL-ADMIN-VALIDATE-TASK-LAUNCH-CARD",
    "TOOL-ADMIN-VALIDATE-READ-FIRST-RECEIPT",
    "TOOL-ADMIN-VALIDATE-POLICY-REFS",
    "TOOL-EXPLORER-RUN-TRUTH-AUDIT",
    "TOOL-EXPLORER-RUN-AUTOSCREENSHOT-CHECK",
    "TOOL-EXPLORER-RUN-STATIC-READONLY-SCAN",
}


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Validate SCRIPT_REGISTRY required IDs.")
    p.add_argument("--script-registry", default=r"E:\IMPERIUM\ORGANS\MECHANICUS\SCRIPT_REGISTRY.json")
    return p.parse_args()


def main() -> int:
    args = parse_args()
    path = Path(args.script_registry).resolve()
    reg = json.loads(path.read_text(encoding="utf-8"))
    ids = {row.get("script_id") for row in reg.get("scripts", []) if row.get("script_id")}
    missing = sorted(REQUIRED_IDS - ids)
    verdict = "PASS_VALIDATE_SCRIPT_REGISTRY" if not missing else "FAIL_VALIDATE_SCRIPT_REGISTRY"
    report = {"script_registry": str(path), "missing_ids": missing, "verdict": verdict}
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0 if not missing else 1


if __name__ == "__main__":
    raise SystemExit(main())
