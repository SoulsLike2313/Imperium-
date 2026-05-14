#!/usr/bin/env python3
from __future__ import annotations

import argparse
import re
from pathlib import Path


OWNER_SECTION_PATTERNS = {
    "owner_section_1": r"(?mi)^\s*1\)\s*Имя\s+шага\b",
    "owner_section_2": r"(?mi)^\s*2\)\s*Полный\s+путь\b",
    "owner_section_3": r"(?mi)^\s*3\)\s*Вердикт\b",
    "owner_section_4": r"(?mi)^\s*4\)\s*.*Комментар",
}

FORBIDDEN_MACHINE_FIELDS = [
    "TASK_ID:",
    "STAGE_ID:",
    "RUN_ID:",
    "HEAD_SHA:",
    "changed_files:",
    "checks_run:",
    "receipts_created:",
    "warnings:",
    "blockers:",
    "continue_decision:",
    "next_stage:",
    "BUNDLE_PATH:",
    "BLOCKERS_COUNT:",
    "WARNINGS_COUNT:",
    "NEXT_STAGE:",
]


def add_failure(failures: list[str], code: str) -> None:
    if code not in failures:
        failures.append(code)


def check_owner_sections(text: str, failures: list[str]) -> None:
    for label, pattern in OWNER_SECTION_PATTERNS.items():
        if re.search(pattern, text) is None:
            add_failure(failures, f"missing:{label}")


def extract_section_2_path(text: str) -> str | None:
    section_match = re.search(
        r"(?ms)^\s*2\)\s*Полный\s+путь.*?\n(.*?)(?=^\s*[34]\)|\Z)",
        text,
    )
    if section_match is None:
        return None
    lines = [line.strip() for line in section_match.group(1).splitlines() if line.strip()]
    return lines[0] if lines else ""


def check_forbidden_machine_summary(text: str, failures: list[str]) -> None:
    for marker in FORBIDDEN_MACHINE_FIELDS:
        if re.search(rf"(?mi)^\s*{re.escape(marker)}", text):
            add_failure(failures, f"forbidden_machine_summary_field:{marker.rstrip(':')}")


def check_chat_output_limits(text: str, failures: list[str]) -> None:
    non_empty_lines = [line for line in text.splitlines() if line.strip()]
    if len(non_empty_lines) > 45:
        add_failure(failures, "chat_too_long:non_empty_lines_gt_45")

    for label in ("changed_files", "checks_run", "receipts_created"):
        pattern = rf"(?mi)^\s*{label}\s*:\s*(.+)$"
        for match in re.finditer(pattern, text):
            if match.group(1).count(";") >= 2:
                add_failure(failures, f"forbidden:long_semicolon_list:{label}")

    path_like_pattern = re.compile(
        r"(?i)\b(?:[A-Z]:\\[^\s]+|\/[A-Za-z0-9._\-\/]+|[A-Za-z0-9._\-]+\/[A-Za-z0-9._\-\/]+|[A-Za-z0-9._\-]+\\[A-Za-z0-9._\-\\]+)\b"
    )
    if len(path_like_pattern.findall(text)) > 8:
        add_failure(failures, "forbidden:too_many_path_entries")

    command_like_pattern = re.compile(
        r"(?mi)^\s*(?:`)?(?:git|python|py|powershell|bash|sh|rg|pytest|cd|ls|Get-ChildItem|Test-Path)\b"
    )
    if len(command_like_pattern.findall(text)) > 5:
        add_failure(failures, "forbidden:too_many_command_entries")

    json_block_pattern = re.compile(r"(?s)\{[\s\S]*:[\s\S]*\}")
    if json_block_pattern.search(text):
        add_failure(failures, "forbidden:json_block_in_chat")


def check_fake_green_patterns(text: str, failures: list[str]) -> None:
    upper = text.upper()
    lower = text.lower()

    if "FULL_GREEN" in upper and (
        re.search(r"(?i)\bvm2_status\s*:\s*deferred\b", text)
        or "VM2_DEFERRED_OFFLINE" in upper
    ):
        add_failure(failures, "forbidden:full_green_when_vm2_deferred")

    if "VM2 EXACT SYNC OK" in upper and ("error" in lower or "unary operator expected" in lower):
        add_failure(failures, "forbidden:vm2_exact_sync_ok_with_error_signal")

    positive_claim = re.search(r"(?i)\b(full_green|canon|final|green)\b", text)
    has_negation = re.search(
        r"(?i)\b(not canon|not final|not green|no green|cannot be green|не заявляется|не canon|не final|не green)\b",
        text,
    )
    has_evidence_marker = re.search(
        r"(?i)\b(receipt|evidence|source|sha|hash|manifest|report|proof|доказ|источник|чек)\b",
        text,
    )
    if positive_claim and not has_negation and not has_evidence_marker:
        add_failure(failures, "forbidden:claim_without_evidence_marker")


def check_bundle_claim_requires_path(text: str, failures: list[str]) -> None:
    bundle_claim = re.search(
        r"(?i)\b(bundle (is )?(created|assembled|produced|ready|complete)|бандл (создан|собран|готов))\b",
        text,
    )
    section_2_path = extract_section_2_path(text)
    if section_2_path is not None and not section_2_path.strip():
        add_failure(failures, "missing:section_2_path")
    if bundle_claim and (section_2_path is None or not section_2_path.strip()):
        add_failure(failures, "bundle_claim_without_section_2_path")

    # Legacy compatibility check: explicit BUNDLE_PATH with empty value must fail.
    explicit_bundle_path = re.search(r"(?mi)^\s*BUNDLE_PATH\s*:\s*(.*)\s*$", text)
    if explicit_bundle_path and explicit_bundle_path.group(1).strip() == "":
        add_failure(failures, "empty_machine_field:BUNDLE_PATH")


def main() -> int:
    parser = argparse.ArgumentParser(description="Check servitor response contract v0.1 text/markdown.")
    parser.add_argument("response_path", help="Path to response markdown/text file.")
    args = parser.parse_args()

    path = Path(args.response_path)
    failures: list[str] = []

    if not path.exists():
        print("FAIL")
        print(f"- missing_file:{path.as_posix()}")
        return 2

    try:
        text = path.read_text(encoding="utf-8")
    except Exception as exc:  # pragma: no cover - defensive path
        print("FAIL")
        print(f"- unreadable_file:{path.as_posix()}:{type(exc).__name__}")
        return 2

    check_owner_sections(text, failures)
    check_forbidden_machine_summary(text, failures)
    check_chat_output_limits(text, failures)
    check_fake_green_patterns(text, failures)
    check_bundle_claim_requires_path(text, failures)

    if failures:
        print("FAIL")
        for item in failures:
            print(f"- {item}")
        return 1

    print("PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
