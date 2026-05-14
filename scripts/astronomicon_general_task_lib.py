#!/usr/bin/env python3
"""Utilities for Astronomicon General Task parsing/validation."""

from __future__ import annotations

import json
import os
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Tuple

REQUIRED_YAML_FIELDS = [
    "general_task_id",
    "title",
    "owner_goal",
    "desired_outcome",
    "scope_in",
    "scope_out",
    "constraints",
    "forbidden_actions",
    "known_context",
    "unknowns",
    "success_criteria",
    "failure_criteria",
    "expected_deliverables",
    "target_organs",
    "risk_level",
    "owner_approval_points",
    "decomposition_hints",
    "local_task_candidate_count_hint",
    "priority",
    "dependencies",
    "local_private_boundary_notes",
    "dashboard_display_title",
    "tags",
    "created_by",
    "created_at",
    "current_status",
]

LIST_FIELDS = {
    "scope_in",
    "scope_out",
    "constraints",
    "forbidden_actions",
    "known_context",
    "unknowns",
    "success_criteria",
    "failure_criteria",
    "expected_deliverables",
    "target_organs",
    "owner_approval_points",
    "decomposition_hints",
    "dependencies",
    "local_private_boundary_notes",
    "tags",
}

REQUIRED_BODY_SECTIONS = [
    "Background",
    "Detailed Owner Intent",
    "Known Context",
    "Unknowns and Questions",
    "Notes for Decomposition",
    "Notes for Speculum",
    "Notes for Dashboard Display",
]


def repo_root() -> Path:
    return Path(__file__).resolve().parents[1]


def default_external_runtime() -> Path:
    return Path(r"E:\IMPERIUM_CONTEXT\LOCAL\RUNTIME") / "astronomicon"


def _parse_scalar(value: str) -> Any:
    text = value.strip()
    if text == "":
        return ""
    lower = text.lower()
    if lower in {"true", "false"}:
        return lower == "true"
    if lower in {"null", "none", "~"}:
        return None
    if re.fullmatch(r"[-+]?\d+", text):
        try:
            return int(text)
        except ValueError:
            return text
    if re.fullmatch(r"[-+]?\d+\.\d+", text):
        try:
            return float(text)
        except ValueError:
            return text
    if (text.startswith('"') and text.endswith('"')) or (
        text.startswith("'") and text.endswith("'")
    ):
        return text[1:-1]
    return text


def _parse_inline_list(value: str) -> List[Any]:
    cleaned = value.strip()
    if not (cleaned.startswith("[") and cleaned.endswith("]")):
        return [str(_parse_scalar(cleaned))]
    inner = cleaned[1:-1].strip()
    if not inner:
        return []
    parts = [part.strip() for part in inner.split(",")]
    return [_parse_scalar(part) for part in parts]


def _parse_frontmatter(frontmatter_text: str) -> Dict[str, Any]:
    result: Dict[str, Any] = {}
    current_list_key: str | None = None

    for raw_line in frontmatter_text.splitlines():
        line = raw_line.rstrip()
        stripped = line.strip()
        if stripped == "" or stripped.startswith("#"):
            continue

        if stripped.startswith("- "):
            if current_list_key is None:
                raise ValueError(f"List item without key: {raw_line}")
            result.setdefault(current_list_key, [])
            if not isinstance(result[current_list_key], list):
                raise ValueError(
                    f"Mixed scalar/list for key '{current_list_key}' in frontmatter"
                )
            result[current_list_key].append(_parse_scalar(stripped[2:]))
            continue

        if ":" not in line:
            raise ValueError(f"Invalid frontmatter line (missing colon): {raw_line}")

        key, raw_value = line.split(":", 1)
        key = key.strip()
        value = raw_value.strip()

        if key == "":
            raise ValueError(f"Empty key in frontmatter line: {raw_line}")

        if value == "":
            result[key] = []
            current_list_key = key
            continue

        current_list_key = None
        if value.startswith("[") and value.endswith("]"):
            result[key] = _parse_inline_list(value)
        else:
            result[key] = _parse_scalar(value)

    return result


def _parse_body_sections(body_markdown: str) -> Dict[str, str]:
    sections: Dict[str, List[str]] = {}
    current = None

    for line in body_markdown.splitlines():
        if line.startswith("## "):
            current = line[3:].strip()
            sections.setdefault(current, [])
            continue
        if current is not None:
            sections[current].append(line)

    return {name: "\n".join(lines).strip() for name, lines in sections.items()}


def parse_markdown_general_task(path: Path) -> Dict[str, Any]:
    text = path.read_text(encoding="utf-8")

    if not text.startswith("---\n") and not text.startswith("---\r\n"):
        raise ValueError("Frontmatter must start with '---' on first line")

    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        raise ValueError("Frontmatter opening delimiter missing")

    end_idx = None
    for idx in range(1, len(lines)):
        if lines[idx].strip() == "---":
            end_idx = idx
            break

    if end_idx is None:
        raise ValueError("Frontmatter closing delimiter missing")

    frontmatter_text = "\n".join(lines[1:end_idx])
    body_markdown = "\n".join(lines[end_idx + 1 :]).strip()
    frontmatter = _parse_frontmatter(frontmatter_text)
    sections = _parse_body_sections(body_markdown)

    return {
        "schema_version": "general_task_parsed_v0_1",
        "source_path": str(path.resolve()),
        "frontmatter": frontmatter,
        "body_markdown": body_markdown,
        "body_sections": sections,
        "parse_status": "PARSED",
    }


def validate_parsed_general_task(parsed: Dict[str, Any]) -> List[str]:
    errors: List[str] = []
    fm = parsed.get("frontmatter", {})
    sections = parsed.get("body_sections", {})

    for field in REQUIRED_YAML_FIELDS:
        if field not in fm:
            errors.append(f"Missing required YAML field: {field}")
            continue

        value = fm[field]
        if field in LIST_FIELDS:
            if not isinstance(value, list) or len(value) == 0:
                errors.append(f"Field '{field}' must be a non-empty list")
        elif field == "local_task_candidate_count_hint":
            if not isinstance(value, int) or value < 1:
                errors.append("local_task_candidate_count_hint must be integer >= 1")
        else:
            if not isinstance(value, str) or value.strip() == "":
                errors.append(f"Field '{field}' must be a non-empty string")

    for section in REQUIRED_BODY_SECTIONS:
        value = sections.get(section, "")
        if not isinstance(value, str) or value.strip() == "":
            errors.append(f"Missing or empty markdown section: {section}")

    return errors


def ensure_allowed_output_path(path: Path) -> None:
    resolved = path.resolve()
    roots = [
        (repo_root() / "ORGANS" / "ASTRONOMICON").resolve(),
        (repo_root() / "tests" / "fixtures" / "astronomicon").resolve(),
        default_external_runtime().resolve(),
    ]

    for root in roots:
        try:
            resolved.relative_to(root)
            return
        except ValueError:
            continue

    raise ValueError(
        f"Output path is outside allowed Astronomicon scope: {resolved}"
    )


def write_json(path: Path, payload: Dict[str, Any]) -> None:
    ensure_allowed_output_path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
