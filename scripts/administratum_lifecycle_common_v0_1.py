#!/usr/bin/env python3
"""Shared helpers for Administratum task lifecycle scripts v0.1."""

from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


LIFECYCLE_STATES = [
    "PLANNED",
    "ACTIVE",
    "STAGE_PASS",
    "BLOCKED",
    "STOPPED",
    "STOPPED_PENDING_OWNER_APPROVAL",
    "CLOSED_PASS",
    "CLOSED_FAIL",
    "BUNDLED",
]

REPO_ROOT = Path(__file__).resolve().parents[1]
SESSIONS_ROOT = REPO_ROOT / "ORGANS/ADMINISTRATUM/TASK_LIFECYCLE/SESSIONS"


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def to_repo_rel(path: Path) -> str:
    try:
        return str(path.relative_to(REPO_ROOT)).replace("\\", "/")
    except Exception:
        return str(path).replace("\\", "/")


def write_json(path: Path, payload: dict[str, Any], *, ensure_ascii: bool = True) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=ensure_ascii, indent=2) + "\n", encoding="utf-8")


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def append_jsonl(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8", newline="\n") as handle:
        handle.write(json.dumps(payload, ensure_ascii=True))
        handle.write("\n")


def session_dir(task_id: str) -> Path:
    return SESSIONS_ROOT / task_id


def ensure_external_path(path: Path) -> bool:
    try:
        resolved = path.resolve(strict=False)
        resolved_repo = REPO_ROOT.resolve(strict=False)
        resolved.relative_to(resolved_repo)
        return False
    except Exception:
        return True


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        while True:
            chunk = handle.read(65536)
            if not chunk:
                break
            digest.update(chunk)
    return digest.hexdigest()
