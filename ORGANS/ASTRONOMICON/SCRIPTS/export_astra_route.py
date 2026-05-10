#!/usr/bin/env python3
"""Export Astra route files to another local folder (copy only)."""

from __future__ import annotations

import argparse
import json
import shutil
from pathlib import Path


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Export Astra route by copying files only.")
    p.add_argument("--route-dir", required=True)
    p.add_argument("--export-dir", required=True)
    return p.parse_args()


def main() -> int:
    args = parse_args()
    src = Path(args.route_dir).resolve()
    dst = Path(args.export_dir).resolve()
    dst.mkdir(parents=True, exist_ok=True)

    copied = []
    for p in sorted(src.iterdir()):
        if p.is_file():
            target = dst / p.name
            shutil.copy2(p, target)
            copied.append(str(target))

    report = {
        "source": str(src),
        "export_dir": str(dst),
        "files_copied_count": len(copied),
        "files_copied": copied,
        "mode": "COPY_ONLY_NO_MOVE_NO_DELETE",
    }
    (dst / "EXPORT_REPORT.json").write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
