#!/usr/bin/env python3
"""Build SHA256SUMS.txt for a folder (excluding SHA256SUMS.txt itself)."""

from __future__ import annotations

import argparse
import hashlib
from pathlib import Path


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Build SHA256SUMS.txt for target folder.")
    p.add_argument("--target-dir", required=True)
    p.add_argument("--output-file", default="")
    return p.parse_args()


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def main() -> int:
    args = parse_args()
    target = Path(args.target_dir).resolve()
    if not target.exists() or not target.is_dir():
        raise NotADirectoryError(f"Target dir not found: {target}")

    output = Path(args.output_file).resolve() if args.output_file else target / "SHA256SUMS.txt"
    files = [p for p in target.rglob("*") if p.is_file()]

    lines = []
    for p in sorted(files):
        if p.resolve() == output.resolve():
            continue
        lines.append(f"{sha256_file(p)}  {p.relative_to(target).as_posix()}")

    output.write_text("\n".join(lines) + ("\n" if lines else ""), encoding="utf-8")
    print(f"created: {output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

