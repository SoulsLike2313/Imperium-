"""Allowlisted command execution gateway for IMPERIUM."""

from __future__ import annotations

from dataclasses import asdict, dataclass
import json
from pathlib import Path
import subprocess
from typing import Any

from imperium.config import load_config
from imperium.receipts.model import Verdict, utc_timestamp
from imperium.security.path_policy import require_inside_root


ALLOWLIST_SCHEMA_VERSION = "imperium.command_allowlist.v0_1"
COMMAND_RECEIPT_SCHEMA_VERSION = "imperium.command_receipt.v0_1"
DEFAULT_ALLOWLIST_RELATIVE_PATH = Path("REGISTRY/COMMAND_ALLOWLIST.json")


@dataclass
class CommandReceipt:
    schema_version: str
    command_id: str
    timestamp_utc: str
    dry_run: bool
    cwd: str
    argv: list[str]
    allowed: bool
    exit_code: int | None
    stdout: str
    stderr: str
    verdict: str
    warnings: list[str]
    errors: list[str]

    def as_dict(self) -> dict[str, Any]:
        return asdict(self)



def load_allowlist(allowlist_path: Path) -> dict[str, dict[str, Any]]:
    with allowlist_path.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)

    if payload.get("schema_version") != ALLOWLIST_SCHEMA_VERSION:
        raise ValueError(
            f"Unsupported allowlist schema_version: {payload.get('schema_version')}"
        )

    commands = payload.get("commands", [])
    if not isinstance(commands, list):
        raise ValueError("Allowlist 'commands' must be a list.")

    return {entry["command_id"]: entry for entry in commands}



def _build_argv(template: list[str], args: list[str] | None) -> list[str]:
    args = args or []
    if "{args}" not in template:
        if args:
            raise ValueError("Command template does not accept args.")
        return [str(piece) for piece in template]

    argv: list[str] = []
    for piece in template:
        if piece == "{args}":
            argv.extend(str(item) for item in args)
        else:
            argv.append(str(piece))
    return argv



def run_allowed(
    command_id: str,
    args: list[str] | None = None,
    *,
    dry_run: bool = False,
    cwd: str | Path | None = None,
    timeout: int = 60,
    allowlist_path: str | Path | None = None,
    root: str | Path | None = None,
    mode: str | None = None,
) -> dict[str, Any]:
    """Execute an allowlisted command and return command receipt."""
    config = load_config(explicit_root=root, mode=mode)
    runtime_root = config.root_path

    resolved_allowlist_path = (
        Path(allowlist_path).expanduser().resolve()
        if allowlist_path
        else (runtime_root / DEFAULT_ALLOWLIST_RELATIVE_PATH)
    )

    warnings: list[str] = []
    errors: list[str] = []

    execution_cwd_path = require_inside_root(cwd or runtime_root, runtime_root)
    execution_cwd = str(execution_cwd_path)

    try:
        allowlist = load_allowlist(resolved_allowlist_path)
    except Exception as exc:  # pragma: no cover - handled by receipt path
        receipt = CommandReceipt(
            schema_version=COMMAND_RECEIPT_SCHEMA_VERSION,
            command_id=command_id,
            timestamp_utc=utc_timestamp(),
            dry_run=dry_run,
            cwd=execution_cwd,
            argv=[],
            allowed=False,
            exit_code=None,
            stdout="",
            stderr="",
            verdict=Verdict.BLOCKED.value,
            warnings=[],
            errors=[f"Failed to load allowlist: {exc}"],
        )
        return receipt.as_dict()

    entry = allowlist.get(command_id)
    if not entry:
        receipt = CommandReceipt(
            schema_version=COMMAND_RECEIPT_SCHEMA_VERSION,
            command_id=command_id,
            timestamp_utc=utc_timestamp(),
            dry_run=dry_run,
            cwd=execution_cwd,
            argv=[],
            allowed=False,
            exit_code=None,
            stdout="",
            stderr="",
            verdict=Verdict.BLOCKED.value,
            warnings=[],
            errors=[f"Command id '{command_id}' is not allowlisted."],
        )
        return receipt.as_dict()

    allowed_modes = entry.get("allowed_modes", [])
    if config.mode not in allowed_modes:
        receipt = CommandReceipt(
            schema_version=COMMAND_RECEIPT_SCHEMA_VERSION,
            command_id=command_id,
            timestamp_utc=utc_timestamp(),
            dry_run=dry_run,
            cwd=execution_cwd,
            argv=[],
            allowed=False,
            exit_code=None,
            stdout="",
            stderr="",
            verdict=Verdict.BLOCKED.value,
            warnings=[],
            errors=[
                f"Mode '{config.mode}' is not allowed for command '{command_id}'."
            ],
        )
        return receipt.as_dict()

    try:
        argv = _build_argv(entry.get("allowed_argv_template", []), args)
    except Exception as exc:
        receipt = CommandReceipt(
            schema_version=COMMAND_RECEIPT_SCHEMA_VERSION,
            command_id=command_id,
            timestamp_utc=utc_timestamp(),
            dry_run=dry_run,
            cwd=execution_cwd,
            argv=[],
            allowed=False,
            exit_code=None,
            stdout="",
            stderr="",
            verdict=Verdict.BLOCKED.value,
            warnings=[],
            errors=[str(exc)],
        )
        return receipt.as_dict()

    if dry_run:
        warnings.append("Dry run enabled: command was not executed.")
        verdict = Verdict.PASS_WITH_WARNINGS.value if warnings else Verdict.PASS.value
        receipt = CommandReceipt(
            schema_version=COMMAND_RECEIPT_SCHEMA_VERSION,
            command_id=command_id,
            timestamp_utc=utc_timestamp(),
            dry_run=True,
            cwd=execution_cwd,
            argv=argv,
            allowed=True,
            exit_code=None,
            stdout="",
            stderr="",
            verdict=verdict,
            warnings=warnings,
            errors=[],
        )
        return receipt.as_dict()

    stdout = ""
    stderr = ""
    exit_code: int | None = None

    try:
        completed = subprocess.run(
            argv,
            cwd=execution_cwd,
            timeout=timeout,
            shell=False,
            check=False,
            capture_output=True,
            text=True,
        )
        exit_code = completed.returncode
        stdout = completed.stdout
        stderr = completed.stderr
    except subprocess.TimeoutExpired as exc:
        errors.append(f"Command timed out after {timeout}s: {exc}")
    except FileNotFoundError as exc:
        errors.append(f"Executable not found: {exc}")
    except Exception as exc:  # pragma: no cover - defensive
        errors.append(f"Command execution failed: {exc}")

    if errors:
        verdict = Verdict.FAIL.value
    elif exit_code == 0:
        verdict = Verdict.PASS.value
    else:
        verdict = Verdict.FAIL.value

    if verdict == Verdict.PASS.value and warnings:
        verdict = Verdict.PASS_WITH_WARNINGS.value

    receipt = CommandReceipt(
        schema_version=COMMAND_RECEIPT_SCHEMA_VERSION,
        command_id=command_id,
        timestamp_utc=utc_timestamp(),
        dry_run=False,
        cwd=execution_cwd,
        argv=argv,
        allowed=True,
        exit_code=exit_code,
        stdout=stdout,
        stderr=stderr,
        verdict=verdict,
        warnings=warnings,
        errors=errors,
    )
    return receipt.as_dict()
