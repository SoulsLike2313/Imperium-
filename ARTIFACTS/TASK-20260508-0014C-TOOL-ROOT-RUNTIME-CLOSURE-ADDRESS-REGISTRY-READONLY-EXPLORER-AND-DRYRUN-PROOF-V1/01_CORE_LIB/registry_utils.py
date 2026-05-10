#!/usr/bin/env python3
"""Registry helper utilities for tool index management."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def load_json(path: Path, default: Any) -> Any:
    if not path.exists():
        return default
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def is_within(base: Path, candidate: Path) -> bool:
    try:
        candidate.resolve().relative_to(base.resolve())
        return True
    except Exception:
        return False


def summarize_registry(index_payload: dict[str, Any]) -> dict[str, Any]:
    entries = index_payload.get("tools", []) if isinstance(index_payload, dict) else []
    classes: dict[str, int] = {}
    statuses: dict[str, int] = {}
    for item in entries:
        cls = str(item.get("tool_class", "UNKNOWN"))
        st = str(item.get("status", "UNKNOWN"))
        classes[cls] = classes.get(cls, 0) + 1
        statuses[st] = statuses.get(st, 0) + 1
    return {
        "tool_count": len(entries),
        "class_counts": classes,
        "status_counts": statuses,
    }
