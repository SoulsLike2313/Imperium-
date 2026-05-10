#!/usr/bin/env python3
"""SHA256 utilities with portable output formatting."""

from __future__ import annotations

import hashlib
from pathlib import Path, PurePosixPath
from typing import Iterable, Sequence


def file_sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest().lower()


def verify_file_sha256(path: Path, expected_sha256: str) -> bool:
    return file_sha256(path) == expected_sha256.lower().strip()


def parse_sha256_file(sha_path: Path) -> list[tuple[str, str]]:
    entries: list[tuple[str, str]] = []
    for raw_line in sha_path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line:
            continue
        parts = line.split()
        if len(parts) < 2:
            raise ValueError(f"Invalid sha256 line: {raw_line}")
        entries.append((parts[0].lower(), parts[-1]))
    return entries


def _portable_name(path: Path) -> str:
    name = path.name
    if not name:
        raise ValueError("Portable sha256 output requires a file name")
    return name


def _safe_relative_posix(path: Path, base_dir: Path) -> str:
    rel = path.resolve().relative_to(base_dir.resolve())
    rel_posix = rel.as_posix()
    if rel_posix.startswith("/") or rel_posix.startswith("\\"):
        raise ValueError(f"Unsafe absolute-like relative path: {rel_posix}")
    if rel_posix.startswith("../") or "/../" in f"/{rel_posix}/":
        raise ValueError(f"Unsafe traversal path in relative entry: {rel_posix}")
    if ":" in rel_posix:
        raise ValueError(f"Unsafe drive-like marker in relative entry: {rel_posix}")
    # Normalize to canonical POSIX path text.
    return str(PurePosixPath(rel_posix))


def write_sha256_file(files: Sequence[Path], output_path: Path, *, base_dir: Path | None = None) -> list[tuple[str, str]]:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    lines: list[str] = []
    entries: list[tuple[str, str]] = []
    for path in files:
        sha = file_sha256(path)
        if base_dir is None:
            entry = _portable_name(path)
        else:
            entry = _safe_relative_posix(path, base_dir)
        lines.append(f"{sha}  {entry}")
        entries.append((sha, entry))
    output_path.write_text("\n".join(lines) + ("\n" if lines else ""), encoding="utf-8")
    return entries


def write_single_sha256_file(file_path: Path, output_path: Path) -> tuple[str, str]:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    sha = file_sha256(file_path)
    name = _portable_name(file_path)
    output_path.write_text(f"{sha}  {name}\n", encoding="utf-8")
    return sha, name


def verify_sha_entries_exist(base_dir: Path, entries: Iterable[tuple[str, str]]) -> list[str]:
    missing: list[str] = []
    for _, filename in entries:
        candidate = base_dir / filename
        if not candidate.exists():
            missing.append(str(candidate))
    return missing
