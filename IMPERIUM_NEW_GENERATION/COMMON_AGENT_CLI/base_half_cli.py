from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence, Tuple

TASK_ID = "TASK-20260519-ORGAN-AGENT-BASE-HALF-8-ORGANS-V0_1"
REQUIRED_COMMANDS = ["status", "check", "where", "identity", "pack", "shell", "help"]
REQUIRED_FILES = [
    "README.md",
    "AGENT_PROFILE.md",
    "agent_profile.json",
    "IDENTITY_BASELINE.md",
    "SHELL/SHELL_CONTRACT.md",
    "STATE/current_status.json",
    "REPORTS/base_half_check_report.json",
    "REPORTS/base_half_check_report.md",
    "EXAMPLES/README.md",
    "TESTS/README.md",
]


@dataclass
class OrganConfig:
    organ_name: str
    organ_slug: str
    root: Path
    identity_summary: str

    @property
    def runtime_root(self) -> Path:
        return Path("E:/IMPERIUM_CONTEXT/LOCAL/ORGAN_AGENT_BASE_HALF_RUNS") / TASK_ID / "ORGANS" / self.organ_name



def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()



def _write_json(path: Path, payload: Dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=True, indent=2) + "\n", encoding="utf-8")



def _read_json(path: Path) -> Dict[str, Any]:
    if not path.exists():
        return {}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        return data if isinstance(data, dict) else {}
    except Exception:
        return {}



def _read_text(path: Path) -> str:
    if not path.exists():
        return ""
    return path.read_text(encoding="utf-8").strip()



def _repo_root(start: Path) -> Path:
    current = start
    for candidate in [current, *current.parents]:
        if (candidate / ".git").exists():
            return candidate
    return start



def _git_info(repo_root: Path) -> Dict[str, Any]:
    def _run(*args: str) -> str:
        completed = subprocess.run(args, cwd=str(repo_root), capture_output=True, text=True)
        if completed.returncode != 0:
            return (completed.stderr or completed.stdout).strip()
        return completed.stdout.strip()

    return {
        "head": _run("git", "rev-parse", "HEAD"),
        "branch": _run("git", "branch", "--show-current"),
        "dirty": _run("git", "status", "--short"),
    }



def ensure_base_layout(config: OrganConfig) -> None:
    for rel in ["TOOLS", "LAUNCHERS", "SHELL", "STATE", "REPORTS", "RECEIPTS", "EXAMPLES", "TESTS"]:
        (config.root / rel).mkdir(parents=True, exist_ok=True)
    keep = config.root / "RECEIPTS" / ".gitkeep"
    if not keep.exists():
        keep.write_text("", encoding="utf-8")



def important_paths(config: OrganConfig) -> Dict[str, str]:
    return {
        "organ_root": str(config.root),
        "runner": str(config.root / "TOOLS" / f"{config.organ_slug}_agent_runner.py"),
        "launcher": str(config.root / "LAUNCHERS" / f"run_{config.organ_slug}_pc.ps1"),
        "identity_md": str(config.root / "IDENTITY_BASELINE.md"),
        "profile_md": str(config.root / "AGENT_PROFILE.md"),
        "profile_json": str(config.root / "agent_profile.json"),
        "state_json": str(config.root / "STATE" / "current_status.json"),
        "check_json": str(config.root / "REPORTS" / "base_half_check_report.json"),
        "runtime_root": str(config.runtime_root),
    }



def command_status(config: OrganConfig) -> Tuple[int, Path]:
    ensure_base_layout(config)
    repo = _repo_root(config.root)
    state_path = config.root / "STATE" / "current_status.json"
    payload: Dict[str, Any] = {
        "schema_version": "ORGAN_BASE_HALF_STATUS_V0_1",
        "task_id": TASK_ID,
        "organ": config.organ_name,
        "runner": f"{config.organ_slug}_agent_runner.py",
        "timestamp_utc": _utc_now(),
        "status": "READY",
        "visual_status": "WARN",
        "supported_commands": REQUIRED_COMMANDS,
        "identity_summary": config.identity_summary,
        "paths": important_paths(config),
        "git": _git_info(repo),
    }
    _write_json(state_path, payload)
    print(json.dumps(payload, ensure_ascii=True, indent=2))
    return 0, state_path



def _check_required_files(config: OrganConfig) -> List[Dict[str, Any]]:
    rows: List[Dict[str, Any]] = []
    for rel in REQUIRED_FILES:
        rel_path = Path(rel)
        path = config.root / rel_path
        rows.append({"file": rel, "exists": path.exists()})
    runner = config.root / "TOOLS" / f"{config.organ_slug}_agent_runner.py"
    rows.append({"file": f"TOOLS/{config.organ_slug}_agent_runner.py", "exists": runner.exists()})
    launcher = config.root / "LAUNCHERS" / f"run_{config.organ_slug}_pc.ps1"
    rows.append({"file": f"LAUNCHERS/run_{config.organ_slug}_pc.ps1", "exists": launcher.exists()})
    return rows



def command_check(config: OrganConfig) -> Tuple[int, Path, Path]:
    ensure_base_layout(config)
    status_code, state_path = command_status(config)
    _ = status_code
    check_rows = _check_required_files(config)
    missing = [row["file"] for row in check_rows if not bool(row.get("exists"))]
    verdict = "PASS" if not missing else "WARN"
    report = {
        "schema_version": "ORGAN_BASE_HALF_CHECK_REPORT_V0_1",
        "task_id": TASK_ID,
        "organ": config.organ_name,
        "timestamp_utc": _utc_now(),
        "verdict": verdict,
        "visual_status": "WARN",
        "supported_commands": REQUIRED_COMMANDS,
        "state_file": str(state_path),
        "checks": check_rows,
        "missing": missing,
        "notes": [
            "Base Half shell is minimal by design.",
            "Identity baseline is intentionally compact and owner-extensible.",
        ],
    }
    json_path = config.root / "REPORTS" / "base_half_check_report.json"
    md_path = config.root / "REPORTS" / "base_half_check_report.md"
    _write_json(json_path, report)
    lines = [
        f"# {config.organ_name} Base Half Check Report",
        "",
        f"- task_id: `{TASK_ID}`",
        f"- verdict: `{verdict}`",
        "- visual_status: `WARN`",
        f"- timestamp_utc: `{report['timestamp_utc']}`",
        "",
        "## Missing",
    ]
    if missing:
        lines.extend([f"- {item}" for item in missing])
    else:
        lines.append("- none")
    lines.extend(["", "## Commands", *[f"- {cmd}" for cmd in REQUIRED_COMMANDS], ""])
    md_path.write_text("\n".join(lines), encoding="utf-8")
    print(json.dumps(report, ensure_ascii=True, indent=2))
    return 0, json_path, md_path



def command_where(config: OrganConfig) -> int:
    ensure_base_layout(config)
    payload = {"organ": config.organ_name, "paths": important_paths(config), "timestamp_utc": _utc_now()}
    print(json.dumps(payload, ensure_ascii=True, indent=2))
    return 0



def command_identity(config: OrganConfig) -> int:
    ensure_base_layout(config)
    profile = _read_json(config.root / "agent_profile.json")
    identity_md = _read_text(config.root / "IDENTITY_BASELINE.md")
    payload = {
        "organ": config.organ_name,
        "summary": config.identity_summary,
        "profile": profile,
        "identity_baseline_excerpt": identity_md[:1200],
        "timestamp_utc": _utc_now(),
    }
    print(json.dumps(payload, ensure_ascii=True, indent=2))
    return 0



def command_pack(config: OrganConfig) -> Tuple[int, Path]:
    ensure_base_layout(config)
    run_token = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
    pack_root = config.runtime_root / "PACKS" / f"run_{run_token}"
    pack_root.mkdir(parents=True, exist_ok=True)

    # Ensure latest status/report are available for continuity package.
    if not (config.root / "STATE" / "current_status.json").exists():
        command_status(config)
    if not (config.root / "REPORTS" / "base_half_check_report.json").exists():
        command_check(config)

    copies = [
        "AGENT_PROFILE.md",
        "agent_profile.json",
        "IDENTITY_BASELINE.md",
        "STATE/current_status.json",
        "REPORTS/base_half_check_report.json",
        "REPORTS/base_half_check_report.md",
        "SHELL/SHELL_CONTRACT.md",
    ]
    copied: List[str] = []
    for rel in copies:
        src = config.root / Path(rel)
        if src.exists():
            dst = pack_root / Path(rel)
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src, dst)
            copied.append(rel)

    manifest = {
        "schema_version": "ORGAN_BASE_HALF_PACK_V0_1",
        "task_id": TASK_ID,
        "organ": config.organ_name,
        "pack_root": str(pack_root),
        "timestamp_utc": _utc_now(),
        "copied": copied,
        "commands": REQUIRED_COMMANDS,
    }
    _write_json(pack_root / "pack_manifest.json", manifest)
    print(json.dumps(manifest, ensure_ascii=True, indent=2))
    return 0, pack_root



def _shell_dispatch(config: OrganConfig, raw: str) -> Tuple[int, bool]:
    token = raw.strip()
    if not token:
        return 0, False
    if token in {"exit", "quit", "/exit", "/quit"}:
        return 0, True
    if token in {"help", "/help"}:
        command_help(config)
        return 0, False
    if token in {"status", "/status"}:
        command_status(config)
        return 0, False
    if token in {"check", "/check"}:
        command_check(config)
        return 0, False
    if token in {"where", "/where"}:
        command_where(config)
        return 0, False
    if token in {"identity", "/identity"}:
        command_identity(config)
        return 0, False
    if token in {"pack", "/pack"}:
        command_pack(config)
        return 0, False
    print("Unknown shell command. Use help.")
    return 2, False



def command_shell(config: OrganConfig, once: Optional[str]) -> int:
    ensure_base_layout(config)
    if once:
        code, _ = _shell_dispatch(config, once)
        return code

    print(f"{config.organ_name} shell (base-half, minimal).")
    print("Type: help, status, check, where, identity, pack, exit")
    while True:
        try:
            raw = input(f"{config.organ_slug}> ")
        except (EOFError, KeyboardInterrupt):
            print()
            return 0
        code, should_exit = _shell_dispatch(config, raw)
        if should_exit:
            return 0
        if code != 0:
            return code



def command_help(config: OrganConfig) -> int:
    payload = {
        "organ": config.organ_name,
        "runner": f"{config.organ_slug}_agent_runner.py",
        "commands": REQUIRED_COMMANDS,
        "shell_usage": f"py -3 TOOLS/{config.organ_slug}_agent_runner.py shell",
    }
    print(json.dumps(payload, ensure_ascii=True, indent=2))
    return 0



def run_cli(config: OrganConfig, argv: Optional[Sequence[str]] = None) -> int:
    parser = argparse.ArgumentParser(prog=f"{config.organ_slug}_agent_runner.py")
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("status")
    sub.add_parser("check")
    sub.add_parser("where")
    sub.add_parser("identity")
    sub.add_parser("pack")
    shell = sub.add_parser("shell")
    shell.add_argument("--once", default=None)
    sub.add_parser("help")
    args = parser.parse_args(list(argv) if argv is not None else None)

    if args.command == "status":
        return command_status(config)[0]
    if args.command == "check":
        return command_check(config)[0]
    if args.command == "where":
        return command_where(config)
    if args.command == "identity":
        return command_identity(config)
    if args.command == "pack":
        return command_pack(config)[0]
    if args.command == "shell":
        return command_shell(config, args.once)
    if args.command == "help":
        return command_help(config)
    return 2


__all__ = [
    "OrganConfig",
    "REQUIRED_COMMANDS",
    "TASK_ID",
    "ensure_base_layout",
    "run_cli",
]
