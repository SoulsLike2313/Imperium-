#!/usr/bin/env python3
"""
IMPERIUM Local LLM health check.

Behavior:
- Output JSON only.
- Load default config from LOCAL_LLM_PORT/local_llm_config.template.json.
- Optional --config path override.
- Return NOT_CONFIGURED if command is empty/template.
- Return NOT_INSTALLED if command is configured but not found.
- Return PASS only if configured command executes safely.
"""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path


def utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def json_out(payload: dict, exit_code: int = 0) -> int:
    print(json.dumps(payload, ensure_ascii=False))
    return exit_code


def load_json(path: Path) -> dict:
    with path.open("r", encoding="utf-8-sig") as handle:
        return json.load(handle)


def looks_like_template(value: str) -> bool:
    marker = value.strip().lower()
    if not marker:
        return True
    template_tokens = ["<", "template", "changeme", "todo", "example", "your_", "set_me"]
    return any(token in marker for token in template_tokens)


def resolve_executable(command: str) -> str | None:
    direct = Path(command)
    if direct.is_file():
        return str(direct)
    return shutil.which(command)


def safe_run(executable: str, args: list[str], cwd: str | None, timeout_seconds: int) -> tuple[bool, str, str, int | None]:
    cmd = [executable] + args
    try:
        proc = subprocess.run(
            cmd,
            cwd=cwd or None,
            capture_output=True,
            text=True,
            timeout=max(1, timeout_seconds),
            check=False,
        )
        success = proc.returncode == 0
        return success, proc.stdout.strip(), proc.stderr.strip(), proc.returncode
    except subprocess.TimeoutExpired:
        return False, "", f"health probe timeout after {timeout_seconds}s", None
    except Exception as exc:
        return False, "", str(exc), None


def main() -> int:
    parser = argparse.ArgumentParser(description="IMPERIUM local LLM health check")
    parser.add_argument("--config", help="Optional config path")
    args = parser.parse_args()

    script_dir = Path(__file__).resolve().parent
    default_config = script_dir / "local_llm_config.template.json"
    config_path = Path(args.config).resolve() if args.config else default_config

    base_payload = {
        "check_id": f"LOCAL_LLM_HEALTH_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}",
        "timestamp": utc_now(),
        "config_path": str(config_path),
        "status": "UNKNOWN",
        "evidence": {
            "default_config": str(default_config),
            "script_path": str(Path(__file__).resolve()),
        },
        "details": {},
    }

    if not config_path.exists():
        base_payload["status"] = "NOT_CONFIGURED"
        base_payload["details"] = {"reason": "config file not found"}
        return json_out(base_payload, 0)

    try:
        config = load_json(config_path)
    except Exception as exc:
        base_payload["status"] = "FAIL"
        base_payload["details"] = {"reason": f"invalid config JSON: {exc}"}
        return json_out(base_payload, 1)

    model_command = str(config.get("model_command", "")).strip()
    probe_args = config.get("health_probe_args") or ["--version"]
    if not isinstance(probe_args, list) or not all(isinstance(item, str) for item in probe_args):
        base_payload["status"] = "FAIL"
        base_payload["details"] = {"reason": "health_probe_args must be string array"}
        return json_out(base_payload, 1)

    if looks_like_template(model_command):
        base_payload["status"] = "NOT_CONFIGURED"
        base_payload["details"] = {
            "reason": "model_command is empty or template",
            "expected_action": "configure local_llm_config.template.json or pass --config",
        }
        return json_out(base_payload, 0)

    executable = resolve_executable(model_command)
    if not executable:
        base_payload["status"] = "NOT_INSTALLED"
        base_payload["details"] = {
            "reason": "configured command not found",
            "configured_command": model_command,
        }
        return json_out(base_payload, 0)

    timeout_seconds = int(config.get("timeout_seconds", 10) or 10)
    working_directory = str(config.get("working_directory", "")).strip()
    cwd = working_directory if working_directory else None

    ok, stdout, stderr, return_code = safe_run(executable, probe_args, cwd, timeout_seconds)
    base_payload["details"] = {
        "configured_command": model_command,
        "resolved_executable": executable,
        "probe_args": probe_args,
        "return_code": return_code,
        "stdout": stdout,
        "stderr": stderr,
    }

    if ok:
        base_payload["status"] = "PASS"
        return json_out(base_payload, 0)

    base_payload["status"] = "FAIL"
    return json_out(base_payload, 1)


if __name__ == "__main__":
    sys.exit(main())
