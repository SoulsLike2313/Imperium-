from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence, Tuple

try:
    from rich.console import Console
    from rich.panel import Panel

    HAVE_RICH = True
except Exception:
    HAVE_RICH = False
    Console = None  # type: ignore[assignment]
    Panel = None  # type: ignore[assignment]

TASK_ID_BASE_HALF = "TASK-20260519-ORGAN-AGENT-BASE-HALF-8-ORGANS-V0_1"
TASK_ID_IDENTITY_RICH = "TASK-20260519-ORGAN-AGENT-IDENTITY-HALF-RICH-SHELL-8-ORGANS-V0_1"
VISUAL_WARN = "WARN_VISUAL_NOT_REFERENCE"

BASE_COMMANDS = ["status", "check", "where", "identity", "pack", "shell", "help"]
BASE_REQUIRED_FILES = [
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
IDENTITY_REQUIRED_FILES = [
    "IDENTITY/IDENTITY_PROFILE.md",
    "IDENTITY/identity_profile.json",
    "IDENTITY/LORE_FUNCTIONS.md",
    "IDENTITY/lore_functions.json",
    "IDENTITY/DOMAIN_COMMANDS.md",
    "IDENTITY/domain_commands.json",
    "IDENTITY/SPECULUM_CHECKS.md",
]


@dataclass
class OrganConfig:
    organ_name: str
    organ_slug: str
    root: Path
    identity_summary: str
    domain_commands: Dict[str, str]
    domain_aliases: Dict[str, str] = field(default_factory=dict)

    @property
    def runtime_root(self) -> Path:
        return Path("E:/IMPERIUM_CONTEXT/LOCAL/ORGAN_AGENT_IDENTITY_RICH_SHELL_RUNS") / TASK_ID_IDENTITY_RICH / "ORGANS" / self.organ_name


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


def _visual_status() -> str:
    return "PASS_RICH" if HAVE_RICH else VISUAL_WARN


def _all_supported_commands(config: OrganConfig) -> List[str]:
    return BASE_COMMANDS + list(config.domain_commands.keys())


def _canonical_domain_command(config: OrganConfig, token: str) -> Optional[str]:
    value = token.strip().lstrip("/").lower()
    if not value:
        return None
    if value in config.domain_commands:
        return value
    return config.domain_aliases.get(value)


def ensure_base_layout(config: OrganConfig) -> None:
    for rel in ["TOOLS", "LAUNCHERS", "SHELL", "STATE", "REPORTS", "RECEIPTS", "EXAMPLES", "TESTS", "IDENTITY"]:
        (config.root / rel).mkdir(parents=True, exist_ok=True)
    keep = config.root / "RECEIPTS" / ".gitkeep"
    if not keep.exists():
        keep.write_text("", encoding="utf-8")


def _identity_required_rows(config: OrganConfig) -> List[Dict[str, Any]]:
    rows: List[Dict[str, Any]] = []
    for rel in IDENTITY_REQUIRED_FILES:
        rows.append({"file": rel, "exists": (config.root / rel).exists()})
    return rows


def important_paths(config: OrganConfig) -> Dict[str, str]:
    return {
        "organ_root": str(config.root),
        "runner": str(config.root / "TOOLS" / f"{config.organ_slug}_agent_runner.py"),
        "launcher": str(config.root / "LAUNCHERS" / f"run_{config.organ_slug}_pc.ps1"),
        "identity_baseline_md": str(config.root / "IDENTITY_BASELINE.md"),
        "identity_profile_md": str(config.root / "IDENTITY" / "IDENTITY_PROFILE.md"),
        "identity_profile_json": str(config.root / "IDENTITY" / "identity_profile.json"),
        "lore_functions_json": str(config.root / "IDENTITY" / "lore_functions.json"),
        "domain_commands_json": str(config.root / "IDENTITY" / "domain_commands.json"),
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
        "schema_version": "ORGAN_IDENTITY_RICH_STATUS_V0_1",
        "task_id": TASK_ID_IDENTITY_RICH,
        "base_half_task_id": TASK_ID_BASE_HALF,
        "organ": config.organ_name,
        "runner": f"{config.organ_slug}_agent_runner.py",
        "timestamp_utc": _utc_now(),
        "status": "READY",
        "visual_status": _visual_status(),
        "supported_commands": _all_supported_commands(config),
        "identity_summary": config.identity_summary,
        "paths": important_paths(config),
        "git": _git_info(repo),
        "rich_renderer_available": HAVE_RICH,
    }
    if not HAVE_RICH:
        payload["warnings"] = [VISUAL_WARN]
    _write_json(state_path, payload)
    print(json.dumps(payload, ensure_ascii=True, indent=2))
    return 0, state_path


def _check_required_files(config: OrganConfig) -> List[Dict[str, Any]]:
    rows: List[Dict[str, Any]] = []
    for rel in BASE_REQUIRED_FILES:
        rows.append({"file": rel, "exists": (config.root / rel).exists()})
    rows.extend(_identity_required_rows(config))
    runner = config.root / "TOOLS" / f"{config.organ_slug}_agent_runner.py"
    rows.append({"file": f"TOOLS/{config.organ_slug}_agent_runner.py", "exists": runner.exists()})
    launcher = config.root / "LAUNCHERS" / f"run_{config.organ_slug}_pc.ps1"
    rows.append({"file": f"LAUNCHERS/run_{config.organ_slug}_pc.ps1", "exists": launcher.exists()})
    return rows


def command_check(config: OrganConfig) -> Tuple[int, Path, Path]:
    ensure_base_layout(config)
    _, state_path = command_status(config)
    check_rows = _check_required_files(config)
    missing = [row["file"] for row in check_rows if not bool(row.get("exists"))]
    warnings = [VISUAL_WARN] if not HAVE_RICH else []
    verdict = "PASS" if (not missing and not warnings) else "WARN"
    report = {
        "schema_version": "ORGAN_IDENTITY_RICH_CHECK_REPORT_V0_1",
        "task_id": TASK_ID_IDENTITY_RICH,
        "organ": config.organ_name,
        "timestamp_utc": _utc_now(),
        "verdict": verdict,
        "visual_status": _visual_status(),
        "supported_commands": _all_supported_commands(config),
        "state_file": str(state_path),
        "checks": check_rows,
        "missing": missing,
        "warnings": warnings,
        "notes": [
            "Identity Half + Rich Shell uses shared common CLI layer.",
            "Visual fallback must report WARN_VISUAL_NOT_REFERENCE if rich is unavailable.",
        ],
    }
    json_path = config.root / "REPORTS" / "base_half_check_report.json"
    md_path = config.root / "REPORTS" / "base_half_check_report.md"
    _write_json(json_path, report)

    lines = [
        f"# {config.organ_name} Identity Rich Shell Check Report",
        "",
        f"- task_id: `{TASK_ID_IDENTITY_RICH}`",
        f"- verdict: `{verdict}`",
        f"- visual_status: `{_visual_status()}`",
        f"- timestamp_utc: `{report['timestamp_utc']}`",
        "",
        "## Missing",
    ]
    if missing:
        lines.extend([f"- {item}" for item in missing])
    else:
        lines.append("- none")
    lines.extend(["", "## Commands", *[f"- {cmd}" for cmd in _all_supported_commands(config)], ""])
    if warnings:
        lines.extend(["## Warnings", *[f"- {warning}" for warning in warnings], ""])
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
    payload = {
        "organ": config.organ_name,
        "summary": config.identity_summary,
        "profile": _read_json(config.root / "agent_profile.json"),
        "identity_profile": _read_json(config.root / "IDENTITY" / "identity_profile.json"),
        "lore_functions": _read_json(config.root / "IDENTITY" / "lore_functions.json"),
        "domain_commands": _read_json(config.root / "IDENTITY" / "domain_commands.json"),
        "identity_baseline_excerpt": _read_text(config.root / "IDENTITY_BASELINE.md")[:1200],
        "identity_profile_excerpt": _read_text(config.root / "IDENTITY" / "IDENTITY_PROFILE.md")[:1200],
        "timestamp_utc": _utc_now(),
    }
    print(json.dumps(payload, ensure_ascii=True, indent=2))
    return 0


def command_pack(config: OrganConfig) -> Tuple[int, Path]:
    ensure_base_layout(config)
    run_token = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
    pack_root = config.runtime_root / "PACKS" / f"run_{run_token}"
    pack_root.mkdir(parents=True, exist_ok=True)

    if not (config.root / "STATE" / "current_status.json").exists():
        command_status(config)
    if not (config.root / "REPORTS" / "base_half_check_report.json").exists():
        command_check(config)

    copies = [
        "AGENT_PROFILE.md",
        "agent_profile.json",
        "IDENTITY_BASELINE.md",
        "IDENTITY/IDENTITY_PROFILE.md",
        "IDENTITY/identity_profile.json",
        "IDENTITY/LORE_FUNCTIONS.md",
        "IDENTITY/lore_functions.json",
        "IDENTITY/DOMAIN_COMMANDS.md",
        "IDENTITY/domain_commands.json",
        "IDENTITY/SPECULUM_CHECKS.md",
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
        "schema_version": "ORGAN_IDENTITY_RICH_PACK_V0_1",
        "task_id": TASK_ID_IDENTITY_RICH,
        "organ": config.organ_name,
        "pack_root": str(pack_root),
        "timestamp_utc": _utc_now(),
        "copied": copied,
        "commands": _all_supported_commands(config),
        "visual_status": _visual_status(),
    }
    _write_json(pack_root / "pack_manifest.json", manifest)
    print(json.dumps(manifest, ensure_ascii=True, indent=2))
    return 0, pack_root


def _json_validity_report(config: OrganConfig) -> Dict[str, Any]:
    identity_dir = config.root / "IDENTITY"
    targets = [identity_dir / "identity_profile.json", identity_dir / "lore_functions.json", identity_dir / "domain_commands.json"]
    rows: List[Dict[str, Any]] = []
    for path in targets:
        ok = True
        error = ""
        if path.exists():
            try:
                json.loads(path.read_text(encoding="utf-8"))
            except Exception as exc:
                ok = False
                error = str(exc)
        else:
            ok = False
            error = "missing"
        rows.append({"path": str(path), "ok": ok, "error": error})
    failed = [row for row in rows if not row["ok"]]
    return {"checks": rows, "failed_count": len(failed)}


def _scope_drift(repo_root: Path) -> List[Dict[str, str]]:
    completed = subprocess.run(["git", "status", "--short"], cwd=str(repo_root), capture_output=True, text=True)
    lines = [line.rstrip() for line in completed.stdout.splitlines() if line.strip()]
    rows: List[Dict[str, str]] = []
    for line in lines:
        path = line[3:] if len(line) > 3 else line
        rows.append({"raw": line, "path": path})
    return rows


def _domain_output(config: OrganConfig, command: str) -> Dict[str, Any]:
    repo_root = _repo_root(config.root)
    domain_defs = _read_json(config.root / "IDENTITY" / "domain_commands.json")
    lore_defs = _read_json(config.root / "IDENTITY" / "lore_functions.json")
    description = config.domain_commands.get(command, "")
    raw_cmds = domain_defs.get("commands", {}) if isinstance(domain_defs, dict) else {}
    if isinstance(raw_cmds, dict):
        item = raw_cmds.get(command)
        if isinstance(item, dict):
            description = str(item.get("description", description))

    missing = [row["file"] for row in _identity_required_rows(config) if not row["exists"]]
    details: Dict[str, Any] = {
        "organ": config.organ_name,
        "command": command,
        "description": description,
        "identity_missing": missing,
        "git": _git_info(repo_root),
        "lore_function_count": len(lore_defs.get("functions", [])) if isinstance(lore_defs, dict) else 0,
    }
    warnings = [VISUAL_WARN] if not HAVE_RICH else []

    if command == "fake-green-check":
        details["audit"] = {
            "check_report_exists": (config.root / "REPORTS" / "base_half_check_report.json").exists(),
            "identity_missing_count": len(missing),
            "status": "WARN" if missing else "PASS",
        }
    elif command == "scope-drift-check":
        drift = _scope_drift(repo_root)
        details["scope_drift"] = {"changed_paths_count": len(drift), "changed_paths_preview": drift[:20]}
    elif command == "hygiene-scan":
        details["hygiene"] = {"missing_count": len(missing), "missing": missing}
    elif command == "audit-claims":
        details["claims"] = {
            "state_json": str(config.root / "STATE" / "current_status.json"),
            "check_report_json": str(config.root / "REPORTS" / "base_half_check_report.json"),
            "identity_files_ready": len(missing) == 0,
        }
    elif command == "tool-list":
        tools = sorted([p.name for p in (config.root / "TOOLS").glob("*") if p.is_file()])
        details["tools"] = {"count": len(tools), "items": tools}
    elif command == "validator-check":
        details["validator"] = _json_validity_report(config)
    elif command == "capability-map":
        details["capability_map"] = {"base_commands": BASE_COMMANDS, "domain_commands": list(config.domain_commands.keys())}
    elif command == "script-receipt-check":
        receipts = sorted([p.name for p in (config.root / "RECEIPTS").glob("*.json") if p.is_file()])
        details["receipt_scan"] = {"count": len(receipts), "files": receipts[:20]}
    elif command == "task-route":
        details["route"] = ["intake", "decompose", "execute", "verify", "report"]
    elif command == "stage-map-outline":
        details["stage_map"] = ["S1 intake", "S2 planning", "S3 execution", "S4 checks", "S5 closure"]
    elif command == "ready-for-agent-check":
        details["readiness"] = {"missing_identity_files": len(missing), "ready": len(missing) == 0}
    elif command == "route-report":
        details["route_report"] = {"paths": important_paths(config), "next": "status -> check -> domain"}
    elif command == "priority-matrix":
        details["priority_matrix"] = [
            {"priority": "P0", "item": "truth checks", "status": "active"},
            {"priority": "P1", "item": "scope boundary", "status": "active"},
            {"priority": "P2", "item": "packaging", "status": "queued"},
        ]
    elif command == "campaign-plan-outline":
        details["campaign_plan"] = ["admission", "identity", "commands", "sweep", "bundle"]
    elif command == "resource-estimate":
        details["resource_estimate"] = {"domain_commands": len(config.domain_commands), "files_under_organ": len(list(config.root.rglob("*")))}
    elif command == "freeze-list":
        details["freeze"] = ["THRONE*", "CUSTODES*", "forbidden out-of-scope paths"]
    elif command == "lesson-register":
        examples = sorted([p.name for p in (config.root / "EXAMPLES").glob("*") if p.is_file()])
        details["lessons"] = {"example_files": examples}
    elif command == "training-pack-outline":
        details["training_pack"] = {"required": ["IDENTITY_PROFILE.md", "LORE_FUNCTIONS.md", "DOMAIN_COMMANDS.md", "SPECULUM_CHECKS.md"]}
    elif command == "skill-map":
        skills = sorted([p.name for p in (config.root / "skills").glob("*") if p.exists()])
        details["skills"] = {"count": len(skills), "items": skills[:20]}
    elif command == "example-check":
        examples = sorted([p.name for p in (config.root / "EXAMPLES").glob("*") if p.is_file()])
        details["examples"] = {"count": len(examples), "files": examples}
    elif command == "law-list":
        gate_registry = _read_json(repo_root / "ORGANS" / "DOCTRINARIUM" / "GATES" / "GATE_REGISTRY_V0_1.json")
        gate_ids: List[str] = []
        if isinstance(gate_registry, dict):
            for gate in gate_registry.get("gates", []):
                if isinstance(gate, dict) and "gate_id" in gate:
                    gate_ids.append(str(gate["gate_id"]))
        details["laws"] = {"gate_count": len(gate_ids), "gates_preview": gate_ids[:20]}
    elif command == "doctrine-check":
        doctrine_files = [
            "ORGANS/DOCTRINARIUM/GATES/GATE_REGISTRY_V0_1.json",
            "ORGANS/DOCTRINARIUM/GATES/UNIVERSAL_GATE_LAWS_V0_1.md",
            "ORGANS/DOCTRINARIUM/GATES/BASE_MANDATORY_GATES_V0_1.md",
        ]
        details["doctrine"] = [{"file": rel, "exists": (repo_root / rel).exists()} for rel in doctrine_files]
    elif command == "violation-report":
        drift = _scope_drift(repo_root)
        forbidden_hits = [row for row in drift if ("THRONE" in row["path"].upper() or "CUSTODES" in row["path"].upper())]
        details["violations"] = {"forbidden_hits": len(forbidden_hits), "hits": forbidden_hits}
    elif command == "gate-before-work":
        details["gate_before_work"] = {
            "required_truth_checks": ["git status --short", "git rev-parse HEAD", "git branch --show-current"],
            "role_ack_required": True,
        }

    return {
        "schema_version": "ORGAN_DOMAIN_COMMAND_RESULT_V0_1",
        "task_id": TASK_ID_IDENTITY_RICH,
        "timestamp_utc": _utc_now(),
        "visual_status": _visual_status(),
        "warnings": warnings,
        "details": details,
    }


def command_domain(config: OrganConfig, command: str) -> int:
    ensure_base_layout(config)
    payload = _domain_output(config, command)
    receipt = config.root / "RECEIPTS" / f"domain_{command.replace('-', '_')}_latest.json"
    _write_json(receipt, payload)
    payload["receipt_path"] = str(receipt)
    print(json.dumps(payload, ensure_ascii=True, indent=2))
    return 0


def _render_shell_header(config: OrganConfig, warnings: List[str]) -> None:
    lines = [
        f"organ: {config.organ_name}",
        f"identity: {config.identity_summary}",
        f"visual_status: {_visual_status()}",
        f"backend_truth: head={_git_info(_repo_root(config.root)).get('head', '')}",
        f"command_count: {len(_all_supported_commands(config))}",
        f"warn_error_blocker: {warnings[-1] if warnings else 'none'}",
    ]
    if HAVE_RICH and Console is not None and Panel is not None:
        console = Console()
        console.print(Panel("\n".join(lines), title=f"{config.organ_name} RICH SHELL"))
    else:
        print(f"{config.organ_name} RICH SHELL")
        for row in lines:
            print(f"- {row}")


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

    domain = _canonical_domain_command(config, token)
    if domain:
        command_domain(config, domain)
        return 0, False

    print("Unknown shell command. Use help.")
    return 2, False


def command_shell(config: OrganConfig, once: Optional[str]) -> int:
    ensure_base_layout(config)
    warnings: List[str] = [VISUAL_WARN] if not HAVE_RICH else []
    if once:
        code, _ = _shell_dispatch(config, once)
        return code

    _render_shell_header(config, warnings)
    print("Type: help, status, check, where, identity, pack, <domain-command>, exit")
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
        "commands": _all_supported_commands(config),
        "domain_commands": config.domain_commands,
        "shell_usage": f"py -3 TOOLS/{config.organ_slug}_agent_runner.py shell",
        "visual_status": _visual_status(),
        "warnings": [VISUAL_WARN] if not HAVE_RICH else [],
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
    for domain_command in config.domain_commands:
        sub.add_parser(domain_command)

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

    domain = _canonical_domain_command(config, args.command)
    if domain:
        return command_domain(config, domain)
    return 2


__all__ = [
    "OrganConfig",
    "BASE_COMMANDS",
    "TASK_ID_BASE_HALF",
    "TASK_ID_IDENTITY_RICH",
    "ensure_base_layout",
    "run_cli",
]

