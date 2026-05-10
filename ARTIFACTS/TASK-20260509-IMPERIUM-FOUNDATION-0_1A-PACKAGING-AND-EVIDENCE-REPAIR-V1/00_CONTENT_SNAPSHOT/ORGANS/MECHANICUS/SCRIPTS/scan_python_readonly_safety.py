#!/usr/bin/env python3
"""Scan Python source for forbidden safety patterns (scaffold 0.1)."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path


FORBIDDEN_PATTERNS = {
    "write_text": r"\.write_text\s*\(",
    "open_write_mode": r"open\s*\([^)]*[\"']w[\"']",
    "unlink": r"\.unlink\s*\(",
    "remove": r"(?:os\.remove|remove)\s*\(",
    "rmdir": r"(?:os\.rmdir|rmdir)\s*\(",
    "shutil_move": r"shutil\.move\s*\(",
    "requests": r"\brequests\b",
    "urllib": r"\burllib\b",
    "socket": r"\bsocket\b",
    "paramiko": r"\bparamiko\b",
    "watchdog": r"\bwatchdog\b",
    "threading": r"\bthreading\b",
    "multiprocessing": r"\bmultiprocessing\b",
}


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Scan python files for forbidden read/write/network/daemon patterns.")
    p.add_argument("--source", required=True, help="Python file or directory to scan.")
    p.add_argument("--output-json", required=True, help="Output report JSON path.")
    return p.parse_args()


def iter_py_files(source: Path) -> list[Path]:
    if source.is_file():
        return [source] if source.suffix.lower() == ".py" else []
    return sorted([p for p in source.rglob("*.py") if p.is_file()])


def main() -> int:
    args = parse_args()
    source = Path(args.source).resolve()
    out = Path(args.output_json).resolve()
    if not source.exists():
        raise FileNotFoundError(f"Source not found: {source}")

    files = iter_py_files(source)
    findings: list[dict] = []
    for py_path in files:
        text = py_path.read_text(encoding="utf-8", errors="replace")
        for pattern_id, pattern in FORBIDDEN_PATTERNS.items():
            hits = list(re.finditer(pattern, text))
            if hits:
                findings.append(
                    {
                        "file": str(py_path),
                        "pattern_id": pattern_id,
                        "matches_count": len(hits),
                    }
                )

    verdict = "PASS_READONLY_SAFETY_SCAN" if not findings else "FAIL_READONLY_SAFETY_SCAN_FINDINGS"
    report = {
        "source": str(source),
        "files_scanned": len(files),
        "forbidden_patterns_checked": list(FORBIDDEN_PATTERNS.keys()),
        "findings": findings,
        "verdict": verdict,
    }
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0 if not findings else 1


if __name__ == "__main__":
    raise SystemExit(main())

