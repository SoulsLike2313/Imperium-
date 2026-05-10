#!/usr/bin/env python3
"""Manifest helpers for IMPERIUM pipeline bundles."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .sha256_utils import file_sha256

REQUIRED_ID_FIELDS = ["task_id", "stage_id", "run_id", "contour_id", "producer_type", "producer_id"]


def read_manifest(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def write_manifest(
    manifest_path: Path,
    identity: dict[str, str],
    files: list[Path],
    base_dir: Path,
    notes: list[str] | None = None,
) -> dict[str, Any]:
    for field in REQUIRED_ID_FIELDS:
        if field not in identity or not identity[field]:
            raise ValueError(f"Manifest identity missing required field: {field}")

    file_entries: list[dict[str, Any]] = []
    for file_path in files:
        if not file_path.exists() or not file_path.is_file():
            raise ValueError(f"Manifest file does not exist: {file_path}")
        rel_path = str(file_path.relative_to(base_dir)).replace("\\", "/")
        file_entries.append(
            {
                "relative_path": rel_path,
                "size_bytes": file_path.stat().st_size,
                "sha256": file_sha256(file_path),
            }
        )

    manifest = {
        "manifest_version": "IMPERIUM_MANIFEST_V1",
        "identity": identity,
        "file_count": len(file_entries),
        "files": file_entries,
        "notes": notes or [],
    }
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    return manifest


def verify_manifest_files_exist(manifest: dict[str, Any], base_dir: Path) -> list[str]:
    missing: list[str] = []
    for entry in manifest.get("files", []):
        rel = entry.get("relative_path", "")
        if not rel:
            missing.append("<missing-relative-path>")
            continue
        file_path = base_dir / rel
        if not file_path.exists():
            missing.append(str(file_path))
    return missing


def validate_manifest_identity(manifest: dict[str, Any], expected_identity: dict[str, str]) -> list[str]:
    errors: list[str] = []
    identity = manifest.get("identity", {})
    for field, expected in expected_identity.items():
        actual = identity.get(field)
        if actual != expected:
            errors.append(f"manifest identity mismatch for {field}: expected={expected} actual={actual}")
    return errors
