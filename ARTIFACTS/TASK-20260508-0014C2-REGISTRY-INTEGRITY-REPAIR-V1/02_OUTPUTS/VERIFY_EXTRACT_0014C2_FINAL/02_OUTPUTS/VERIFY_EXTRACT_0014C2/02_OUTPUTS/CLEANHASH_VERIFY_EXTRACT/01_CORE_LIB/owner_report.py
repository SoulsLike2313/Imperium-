#!/usr/bin/env python3
"""Unified Owner-facing report output utilities."""

from __future__ import annotations

from pathlib import Path
from typing import Sequence

ALLOWED_VERDICTS = {
    "PASS",
    "PASS_FOR_PROTOCOL_BASE",
    "NEEDS_SPECULUM_REVIEW",
    "PARTIAL",
    "WAITING",
    "BLOCKED",
    "FAIL",
    "CONFLICT",
}


def build_owner_report(step: str, bundle: str, verdict: str, comment_lines: Sequence[str]) -> str:
    verdict = verdict.strip().upper()
    if verdict not in ALLOWED_VERDICTS:
        raise ValueError(f"Unsupported Owner verdict: {verdict}")
    if len(comment_lines) < 3 or len(comment_lines) > 4:
        raise ValueError("Owner comment must contain 3 or 4 lines")
    normalized_lines = [line.strip() for line in comment_lines if line.strip()]
    if len(normalized_lines) < 3 or len(normalized_lines) > 4:
        raise ValueError("Owner comment must contain 3 or 4 non-empty lines")

    return (
        f"ШАГ:\n{step}\n\n"
        f"БАНДЛ:\n{bundle}\n\n"
        f"ВЕРДИКТ:\n{verdict}\n\n"
        f"КОММЕНТАРИЙ ДЛЯ OWNER:\n" + "\n".join(normalized_lines) + "\n"
    )


def print_owner_report(step: str, bundle: str, verdict: str, comment_lines: Sequence[str]) -> str:
    text = build_owner_report(step, bundle, verdict, comment_lines)
    print(text)
    return text


def write_owner_report(output_path: Path, step: str, bundle: str, verdict: str, comment_lines: Sequence[str]) -> str:
    text = build_owner_report(step, bundle, verdict, comment_lines)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(text, encoding="utf-8")
    return text
