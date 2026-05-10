#!/usr/bin/env python3
"""File-backed resumable phase runner template for large PC scripts."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", required=True)
    parser.add_argument("--log-dir", required=True)
    parser.add_argument("--phase", required=True)
    args = parser.parse_args()

    log_dir = Path(args.log_dir)
    log_dir.mkdir(parents=True, exist_ok=True)

    stdout_path = log_dir / f"{args.phase}_stdout.log"
    stderr_path = log_dir / f"{args.phase}_stderr.log"
    exit_path = log_dir / f"{args.phase}_exit_code.txt"
    marker_path = log_dir / f"{args.phase}.done"

    try:
        config = json.loads(Path(args.config).read_text(encoding="utf-8"))
        stdout_path.write_text(
            "START_PHASE {phase}\nCONFIG_KEYS {keys}\n".format(
                phase=args.phase,
                keys=sorted(config.keys()),
            ),
            encoding="utf-8",
        )
        exit_path.write_text("0\n", encoding="ascii")
        marker_path.write_text("DONE\n", encoding="ascii")
        return 0
    except Exception as exc:  # noqa: BLE001
        stderr_path.write_text(f"{exc}\n", encoding="utf-8")
        exit_path.write_text("1\n", encoding="ascii")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
