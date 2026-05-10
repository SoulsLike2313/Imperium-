#!/usr/bin/env python3
"""Build MANIFEST.json for a folder (excluding MANIFEST.json itself)."""

from __future__ import annotations

import argparse
import hashlib
import json
from datetime import datetime
from pathlib import Path


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Build MANIFEST.json for target folder.")
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

    output = Path(args.output_file).resolve() if args.output_file else target / "MANIFEST.json"
    files = [p for p in target.rglob("*") if p.is_file() and p.resolve() != output.resolve()]

    entries = []
    for p in sorted(files):
        entries.append(
            {
                "path": p.relative_to(target).as_posix(),
                "size_bytes": p.stat().st_size,
                "sha256": sha256_file(p),
            }
        )

    manifest = {
        "generated_at_local": datetime.now().isoformat(timespec="seconds"),
        "target_dir": str(target),
        "files_count": len(entries),
        "files": entries,
    }
    output.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"created: {output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

