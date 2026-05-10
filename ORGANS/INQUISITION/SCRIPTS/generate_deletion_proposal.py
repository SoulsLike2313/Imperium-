#!/usr/bin/env python3
"""Generate deletion proposal only. Never delete files."""

from __future__ import annotations

import argparse
from pathlib import Path


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Generate deletion proposal (no destructive action).")
    p.add_argument("--scan-dir", required=True)
    p.add_argument("--output-md", required=True)
    return p.parse_args()


def main() -> int:
    args = parse_args()
    scan_dir = Path(args.scan_dir).resolve()
    out_md = Path(args.output_md).resolve()
    candidates = []
    for p in scan_dir.rglob("*"):
        if p.is_file() and (p.name.endswith(".tmp") or p.name.endswith(".bak")):
            candidates.append(str(p))

    lines = [
        "# DELETION PROPOSALS",
        "",
        "This is proposal-only output.",
        "No file was deleted, moved, or renamed.",
        "",
        f"Scan root: {scan_dir}",
        "",
    ]
    if candidates:
        lines.append("## Candidate list")
        for c in candidates:
            lines.append(f"- {c}")
    else:
        lines.append("No deletion candidates detected in this dry-run scope.")

    out_md.parent.mkdir(parents=True, exist_ok=True)
    out_md.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"proposal_written: {out_md}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
