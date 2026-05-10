#!/usr/bin/env python3
"""Detect forbidden refs in a local folder (foundation dry-run)."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

PATTERNS = {
    "latest_bundle": re.compile(r"latest[-_ ]bundle", re.IGNORECASE),
    "throne": re.compile(r"(throne[_\-\s]?(contact|connect|activate|enable))|(contact\s+throne)", re.IGNORECASE),
    "watcher_autosync": re.compile(
        r"(enable|start|create|launch)[^\n]{0,24}(watcher|autosync|background automation)"
        r"|((watcher|autosync)[^\n]{0,24}(enable|start|create|launch))",
        re.IGNORECASE,
    ),
    "destructive_delete": re.compile(
        r"rm\s+-rf|Remove-Item\s+.+-Recurse|shutil\.rmtree|os\.remove\(|unlink\(|rmdir\(|delete\s+(file|folder)",
        re.IGNORECASE,
    ),
}


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Detect forbidden references.")
    p.add_argument("--scan-dir", required=True)
    p.add_argument("--output-json", required=True)
    return p.parse_args()


def main() -> int:
    args = parse_args()
    scan_dir = Path(args.scan_dir).resolve()
    out_json = Path(args.output_json).resolve()
    findings = {k: [] for k in PATTERNS}

    for p in scan_dir.rglob("*"):
        if not p.is_file() or p.suffix.lower() not in {".md", ".txt", ".json", ".py"}:
            continue
        text = p.read_text(encoding="utf-8", errors="ignore")
        rel = str(p.relative_to(scan_dir)).replace("\\", "/")
        for key, rx in PATTERNS.items():
            matches = rx.findall(text)
            if matches:
                findings[key].append({"path": rel, "count": len(matches)})

    destructive_effective = [
        row for row in findings["destructive_delete"] if not row["path"].lower().endswith("deletion_proposals.md")
    ]

    verdict = "PASS_FORBIDDEN_REFS_SCAN"
    if findings["latest_bundle"] or findings["throne"] or findings["watcher_autosync"] or destructive_effective:
        verdict = "FAIL_FORBIDDEN_REFS_SCAN"

    report = {
        "scan_dir": str(scan_dir),
        "findings": findings,
        "destructive_effective": destructive_effective,
        "forbidden_ref_count": sum(len(v) for v in findings.values()),
        "verdict": verdict,
    }
    out_json.parent.mkdir(parents=True, exist_ok=True)
    out_json.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0 if verdict.startswith("PASS") else 1


if __name__ == "__main__":
    raise SystemExit(main())
