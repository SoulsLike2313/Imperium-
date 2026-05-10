#!/usr/bin/env python3
"""Path safety helpers, including latest-path rejection."""

from __future__ import annotations

import re
from pathlib import Path
from typing import Iterable

LATEST_PATTERN = re.compile(r"(?i)(latest|newest|most[-_ ]?recent)")
SENSITIVE_NAME_PATTERN = re.compile(r"(?i)(\.local\.|local_access|id_rsa|id_ed25519|private[_-]?key|token|password|secret)")


def assert_no_latest_pattern(value: str, field_name: str) -> None:
    if LATEST_PATTERN.search(value):
        raise ValueError(f"{field_name} contains forbidden latest-pattern: {value}")


def assert_paths_no_latest(paths: Iterable[Path], field_name: str) -> None:
    for path in paths:
        assert_no_latest_pattern(str(path), field_name)


def is_safe_shareable_path(path: Path) -> bool:
    return not bool(SENSITIVE_NAME_PATTERN.search(str(path)))


def assert_safe_shareable_path(path: Path, field_name: str) -> None:
    if not is_safe_shareable_path(path):
        raise ValueError(f"{field_name} appears sensitive for shareable artifacts: {path}")
