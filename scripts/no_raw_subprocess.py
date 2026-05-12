#!/usr/bin/env python3
"""Gate: find raw subprocess/process-shell usage outside approved gateway."""

from __future__ import annotations

import ast
import json
from pathlib import Path
import re
import sys
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = REPO_ROOT / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from imperium.receipts.model import Verdict, utc_timestamp
from imperium.security.command_gateway import run_allowed


APPROVED_GATEWAY = Path("src/imperium/security/command_gateway.py")
TARGET_SUBPROCESS_ATTRS = {"run", "Popen", "call", "check_output", "check_call"}
MAX_DETAIL_ITEMS = 200
PS1_PATTERNS = [
    re.compile(r"\bInvoke-Expression\b", re.IGNORECASE),
    re.compile(r"\bStart-Process\b", re.IGNORECASE),
]



def _truncate(items: list[str]) -> tuple[list[str], int]:
    if len(items) <= MAX_DETAIL_ITEMS:
        return items, 0
    return items[:MAX_DETAIL_ITEMS], len(items) - MAX_DETAIL_ITEMS



def _tracked_code_files(repo_root: Path) -> list[Path]:
    receipt = run_allowed(
        "git.ls_files",
        args=["*.py", "*.ps1"],
        cwd=repo_root,
        root=repo_root,
    )
    if receipt["verdict"] not in {Verdict.PASS.value, Verdict.PASS_WITH_WARNINGS.value}:
        return []
    return [Path(line.strip()) for line in receipt["stdout"].splitlines() if line.strip()]



def _python_findings(file_path: Path) -> list[str]:
    findings: list[str] = []
    source = file_path.read_text(encoding="utf-8", errors="replace")

    try:
        tree = ast.parse(source)
    except SyntaxError as exc:
        return [f"syntax_error:{exc.lineno}"]

    subprocess_aliases = {"subprocess"}
    os_aliases = {"os"}
    direct_subprocess_funcs: set[str] = set()
    direct_os_system_names: set[str] = set()

    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                if alias.name == "subprocess":
                    subprocess_aliases.add(alias.asname or alias.name)
                if alias.name == "os":
                    os_aliases.add(alias.asname or alias.name)
        elif isinstance(node, ast.ImportFrom):
            if node.module == "subprocess":
                for alias in node.names:
                    imported_name = alias.asname or alias.name
                    if alias.name in TARGET_SUBPROCESS_ATTRS:
                        direct_subprocess_funcs.add(imported_name)
            if node.module == "os":
                for alias in node.names:
                    imported_name = alias.asname or alias.name
                    if alias.name == "system":
                        direct_os_system_names.add(imported_name)

    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue

        func = node.func
        if isinstance(func, ast.Attribute) and isinstance(func.value, ast.Name):
            base = func.value.id
            name = func.attr
            if base in subprocess_aliases and name in TARGET_SUBPROCESS_ATTRS:
                findings.append(f"line {node.lineno}: subprocess.{name}")
            if base in os_aliases and name == "system":
                findings.append(f"line {node.lineno}: os.system")
        elif isinstance(func, ast.Name):
            called = func.id
            if called in direct_subprocess_funcs:
                findings.append(f"line {node.lineno}: subprocess import {called}")
            if called in direct_os_system_names:
                findings.append(f"line {node.lineno}: os import {called}")

    return findings



def _ps1_findings(file_path: Path) -> list[str]:
    findings: list[str] = []
    lines = file_path.read_text(encoding="utf-8", errors="replace").splitlines()
    for idx, line in enumerate(lines, start=1):
        for pattern in PS1_PATTERNS:
            if pattern.search(line):
                findings.append(f"line {idx}: {line.strip()}")
    return findings



def _classify(path: Path) -> str:
    if path == APPROVED_GATEWAY:
        return "approved"
    if path.parts and path.parts[0] in {"src", "scripts", "tests"}:
        return "new_spine"
    return "legacy"



def run_gate(root: Path | None = None) -> dict[str, Any]:
    repo_root = (root or REPO_ROOT).resolve()
    files = _tracked_code_files(repo_root)

    blockers: list[str] = []
    legacy_findings: list[str] = []
    warnings: list[str] = []
    errors: list[str] = []

    for rel_path in files:
        abs_path = repo_root / rel_path
        if not abs_path.exists():
            continue

        if rel_path.suffix == ".py":
            file_findings = _python_findings(abs_path)
        elif rel_path.suffix == ".ps1":
            file_findings = _ps1_findings(abs_path)
        else:
            file_findings = []

        if not file_findings:
            continue

        classification = _classify(rel_path)
        for finding in file_findings:
            formatted = f"{rel_path.as_posix()} :: {finding}"
            if classification == "approved":
                continue
            if classification == "new_spine":
                blockers.append(formatted)
            else:
                legacy_findings.append(formatted)

    if legacy_findings:
        warnings.append(
            f"Legacy raw subprocess/shell findings detected: {len(legacy_findings)}."
        )

    listed_blockers, omitted_blockers = _truncate(blockers)
    listed_legacy, omitted_legacy = _truncate(legacy_findings)
    if omitted_blockers:
        warnings.append(f"Omitted {omitted_blockers} new-spine blocker details from gate output.")
    if omitted_legacy:
        warnings.append(f"Omitted {omitted_legacy} legacy finding details from gate output.")

    verdict = Verdict.PASS.value
    if blockers:
        verdict = Verdict.FAIL.value
    elif warnings:
        verdict = Verdict.PASS_WITH_WARNINGS.value

    return {
        "schema_version": "imperium.verification_gate.v0_1",
        "gate_id": "no_raw_subprocess",
        "timestamp_utc": utc_timestamp(),
        "verdict": verdict,
        "blockers": listed_blockers,
        "legacy_findings": listed_legacy,
        "warnings": warnings,
        "errors": errors,
        "metrics": {
            "scanned_files": len(files),
            "blockers_new_spine": len(blockers),
            "legacy_findings": len(legacy_findings),
            "warnings": len(warnings),
            "listed_blockers": len(listed_blockers),
            "omitted_blockers": omitted_blockers,
            "listed_legacy_findings": len(listed_legacy),
            "omitted_legacy_findings": omitted_legacy,
        },
    }



def main() -> int:
    report = run_gate()
    print(json.dumps(report, indent=2))
    return 1 if report["verdict"] in {Verdict.FAIL.value, Verdict.BLOCKED.value} else 0


if __name__ == "__main__":
    raise SystemExit(main())
