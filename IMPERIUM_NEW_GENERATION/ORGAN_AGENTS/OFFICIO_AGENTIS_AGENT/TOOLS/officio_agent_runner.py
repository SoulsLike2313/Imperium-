from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import zipfile
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

try:
    from rich.console import Console
    from rich.layout import Layout
    from rich.panel import Panel

    HAVE_RICH = True
except Exception:
    HAVE_RICH = False
    Console = None  # type: ignore[assignment]
    Layout = None  # type: ignore[assignment]
    Panel = None  # type: ignore[assignment]

TASK_ID_DEFAULT = "TASK-20260518-OFFICIO-SETTINGS-GOVERNANCE-RICH-CLI-V0_1"
STATUS_READY = "FOUNDATION_V0_1_READY_FOR_REVIEW"
DEFAULT_RUNTIME_ROOT = Path(r"E:\IMPERIUM_CONTEXT\LOCAL\OFFICIO_AGENTIS\RUNS")

ROOT = Path(__file__).resolve().parent.parent
REPO_ROOT = ROOT.parent.parent.parent
ROLE_REGISTRY = ROOT / "ROLE_REGISTRY"
MODE_REGISTRY = ROOT / "MODE_REGISTRY"
SETTINGS_REGISTRY = ROOT / "SETTINGS_REGISTRY"
RESPONSE_CONTRACTS = ROOT / "RESPONSE_CONTRACTS"
EVIDENCE_POLICY_DIR = ROOT / "EVIDENCE_POLICY"
SCHEMAS_DIR = ROOT / "SCHEMAS"
EXAMPLES_DIR = ROOT / "EXAMPLES"

ROLE_RESPONSE_CONTRACT_FILE = {
    "SERVITOR": "SERVITOR_EXECUTOR_RESPONSE_CONTRACT.md",
    "LOGOS_PRIME": "LOGOS_PRIME_RESPONSE_CONTRACT.md",
    "LOGOS_SPECULUM": "LOGOS_SPECULUM_RESPONSE_CONTRACT.md",
}

OFFICIO_SETTING_REQUIRED_FIELDS = [
    "setting_id",
    "title",
    "version",
    "state",
    "scope",
    "applies_to_roles",
    "applies_to_modes",
    "machine_rule",
    "human_summary",
    "acceptance_tests",
    "evidence_required",
    "dependencies",
    "conflicts_with",
    "supersedes",
    "rollback_plan",
    "owner_approval_required",
]


@dataclass
class CommandContext:
    command: str
    runtime_root: Path
    run_root: Path


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def utc_stamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def read_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        json.dump(payload, handle, ensure_ascii=False, indent=2)
        handle.write("\n")


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def get_runtime_root() -> Path:
    runtime_env = None
    for key in ("OFFICIO_RUNTIME_ROOT", "IMPERIUM_OFFICIO_RUNTIME_ROOT"):
        env_value = os.environ.get(key)
        if env_value:
            runtime_env = Path(env_value)
            break
    runtime_root = runtime_env if runtime_env else DEFAULT_RUNTIME_ROOT
    runtime_root.mkdir(parents=True, exist_ok=True)
    return runtime_root


def create_context(command: str) -> CommandContext:
    runtime_root = get_runtime_root()
    run_root = runtime_root / f"run_{utc_stamp()}_{command.replace('-', '_')}"
    run_root.mkdir(parents=True, exist_ok=True)
    return CommandContext(command=command, runtime_root=runtime_root, run_root=run_root)


def emit_receipt(ctx: CommandContext, receipt_name: str, payload: dict[str, Any]) -> Path:
    receipt_path = ctx.run_root / "receipts" / receipt_name
    write_json(receipt_path, payload)
    return receipt_path


def print_artifacts(label_to_path: dict[str, Path]) -> None:
    for label, path in label_to_path.items():
        print(f"{label}: {path}")


def git_info() -> dict[str, str]:
    def run(args: list[str]) -> str:
        try:
            out = subprocess.check_output(["git", *args], cwd=REPO_ROOT, text=True)
            return out.strip()
        except Exception:
            return "UNKNOWN"

    head = run(["rev-parse", "HEAD"])
    branch = run(["branch", "--show-current"])
    status = run(["status", "--short"])
    return {
        "head": head,
        "branch": branch,
        "dirty": "yes" if status else "no",
        "status_short": status if status else "<clean>",
    }


def valid_agent(value: str) -> str:
    normalized = value.strip().upper()
    if normalized not in ROLE_RESPONSE_CONTRACT_FILE:
        allowed = ", ".join(sorted(ROLE_RESPONSE_CONTRACT_FILE.keys()))
        raise ValueError(f"Unsupported agent '{value}'. Allowed: {allowed}")
    return normalized


def valid_mode(value: str) -> str:
    normalized = value.strip().upper()
    allowed = {"EXECUTOR", "AUDITOR", "ARCHITECT", "REPAIRER"}
    if normalized not in allowed:
        allowed_text = ", ".join(sorted(allowed))
        raise ValueError(f"Unsupported mode '{value}'. Allowed: {allowed_text}")
    return normalized


def safe_list(obj: dict[str, Any], key: str) -> list[str]:
    value = obj.get(key, [])
    if isinstance(value, list):
        return [str(item) for item in value]
    return []


def load_role_profile(agent: str) -> dict[str, Any]:
    return read_json(ROLE_REGISTRY / agent / "role_profile.json")


def load_mode_profile(mode: str) -> dict[str, Any]:
    return read_json(MODE_REGISTRY / mode / "mode_profile.json")


def load_permissions() -> dict[str, Any]:
    return read_json(SETTINGS_REGISTRY / "permissions" / "permissions.json")


def load_forbidden_actions() -> dict[str, Any]:
    return read_json(SETTINGS_REGISTRY / "forbidden_actions" / "forbidden_actions.json")


def load_stop_conditions() -> dict[str, Any]:
    return read_json(SETTINGS_REGISTRY / "stop_conditions" / "stop_conditions.json")


def load_evidence_policy() -> dict[str, Any]:
    return read_json(EVIDENCE_POLICY_DIR / "evidence_policy.json")


def load_settings_index() -> dict[str, Any]:
    return read_json(SETTINGS_REGISTRY / "settings_index.json")


def response_contract_path_for(agent: str) -> Path:
    return RESPONSE_CONTRACTS / ROLE_RESPONSE_CONTRACT_FILE[agent]


def build_execution_settings(agent: str, mode: str) -> tuple[dict[str, Any], str]:
    role = load_role_profile(agent)
    mode_profile = load_mode_profile(mode)
    permissions = load_permissions()
    forbidden = load_forbidden_actions()
    stops = load_stop_conditions()
    evidence = load_evidence_policy()
    contract_path = response_contract_path_for(agent)

    settings = {
        "task_id_default": TASK_ID_DEFAULT,
        "agent": agent,
        "mode": mode,
        "role_profile": role,
        "mode_profile": mode_profile,
        "permissions": permissions,
        "forbidden_actions": forbidden,
        "stop_conditions": stops.get("stop_conditions", []),
        "response_contract_file": str(contract_path.relative_to(ROOT)),
        "evidence_policy": evidence,
    }

    md = "\n".join(
        [
            f"# Execution Settings: {agent} / {mode}",
            "",
            f"- task_id_default: `{TASK_ID_DEFAULT}`",
            f"- response_contract: `{contract_path.name}`",
            "",
            "## Role Obligations",
            *[f"- {entry}" for entry in safe_list(role, "obligations")],
            "",
            "## Mode Intent",
            f"- {mode_profile.get('intent', 'n/a')}",
            "",
            "## Core Permissions",
            *[f"- {entry}" for entry in safe_list(permissions, "global_permissions")],
            "",
            "## Forbidden Actions",
            *[f"- {entry}" for entry in safe_list(forbidden, "forbidden_actions")],
            "",
            "## Stop Conditions",
            *[f"- {item.get('code', 'UNKNOWN')}" for item in stops.get("stop_conditions", [])],
            "",
            "## Evidence Law",
            "- No evidence = no DONE.",
        ]
    )
    return settings, md


def cmd_status(_args: argparse.Namespace) -> int:
    ctx = create_context("status")
    g = git_info()
    payload = {
        "task_id_default": TASK_ID_DEFAULT,
        "status": STATUS_READY,
        "root": str(ROOT),
        "runtime_root": str(ctx.runtime_root),
        "supported_agents": sorted(ROLE_RESPONSE_CONTRACT_FILE.keys()),
        "supported_modes": ["EXECUTOR", "AUDITOR", "ARCHITECT", "REPAIRER"],
        "git": g,
        "timestamp_utc": utc_now(),
    }
    status_json = ctx.run_root / "status" / "status.json"
    status_md = ctx.run_root / "status" / "STATUS.md"
    write_json(status_json, payload)
    write_text(
        status_md,
        "\n".join(
            [
                "# Officio Status",
                "",
                f"- status: `{STATUS_READY}`",
                f"- root: `{ROOT}`",
                f"- runtime_root: `{ctx.runtime_root}`",
                f"- git_head: `{g['head']}`",
                f"- git_branch: `{g['branch']}`",
                f"- git_dirty: `{g['dirty']}`",
            ]
        )
        + "\n",
    )
    receipt = emit_receipt(
        ctx,
        "status_receipt.json",
        {"command": "status", "timestamp_utc": utc_now(), "verdict": "PASS", "outputs": [str(status_json), str(status_md)]},
    )
    print_artifacts({"STATUS_JSON": status_json, "STATUS_MD": status_md, "RECEIPT": receipt})
    return 0


def cmd_role_get(args: argparse.Namespace) -> int:
    try:
        agent = valid_agent(args.agent)
    except ValueError as error:
        print(str(error), file=sys.stderr)
        return 2

    ctx = create_context("role_get")
    source_md = ROLE_REGISTRY / agent / "ROLE_PROFILE.md"
    source_json = ROLE_REGISTRY / agent / "role_profile.json"
    out_dir = ctx.run_root / "role_get" / agent
    out_md = out_dir / "ROLE_PROFILE.md"
    out_json = out_dir / "role_profile.json"
    out_dir.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source_md, out_md)
    shutil.copy2(source_json, out_json)

    receipt = emit_receipt(
        ctx,
        f"role_get_{agent}_receipt.json",
        {"command": "role-get", "agent": agent, "timestamp_utc": utc_now(), "verdict": "PASS", "outputs": [str(out_md), str(out_json)]},
    )
    print_artifacts({"ROLE_PROFILE_MD": out_md, "ROLE_PROFILE_JSON": out_json, "RECEIPT": receipt})
    return 0


def cmd_settings_get(args: argparse.Namespace) -> int:
    try:
        agent = valid_agent(args.agent)
        mode = valid_mode(args.mode)
    except ValueError as error:
        print(str(error), file=sys.stderr)
        return 2

    ctx = create_context("settings_get")
    settings, settings_md = build_execution_settings(agent, mode)
    out_dir = ctx.run_root / "settings_get" / f"{agent}_{mode}"
    out_dir.mkdir(parents=True, exist_ok=True)

    settings_md_path = out_dir / "EXECUTION_SETTINGS.md"
    settings_json_path = out_dir / "execution_settings.json"
    stop_conditions_path = out_dir / "STOP_CONDITIONS.json"
    response_contract_path = out_dir / "RESPONSE_CONTRACT.md"
    evidence_policy_path = out_dir / "EVIDENCE_POLICY.md"

    write_text(settings_md_path, settings_md + "\n")
    write_json(settings_json_path, settings)
    write_json(stop_conditions_path, load_stop_conditions())
    write_text(response_contract_path, read_text(response_contract_path_for(agent)))
    write_text(evidence_policy_path, read_text(EVIDENCE_POLICY_DIR / "EVIDENCE_POLICY.md"))

    receipt = emit_receipt(
        ctx,
        f"settings_get_{agent}_{mode}_receipt.json",
        {
            "command": "settings-get",
            "agent": agent,
            "mode": mode,
            "timestamp_utc": utc_now(),
            "verdict": "PASS",
            "outputs": [
                str(settings_md_path),
                str(settings_json_path),
                str(stop_conditions_path),
                str(response_contract_path),
                str(evidence_policy_path),
            ],
        },
    )
    print_artifacts(
        {
            "EXECUTION_SETTINGS_MD": settings_md_path,
            "EXECUTION_SETTINGS_JSON": settings_json_path,
            "STOP_CONDITIONS_JSON": stop_conditions_path,
            "RESPONSE_CONTRACT_MD": response_contract_path,
            "EVIDENCE_POLICY_MD": evidence_policy_path,
            "RECEIPT": receipt,
        }
    )
    return 0


def parse_task_pack_from_md(md_text: str) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for line in md_text.splitlines():
        line = line.strip()
        if not line.startswith("| REQ-"):
            continue
        cells = [cell.strip() for cell in line.strip("|").split("|")]
        if len(cells) < 3:
            continue
        req_id, requirement, acceptance = cells[0], cells[1], cells[2]
        rows.append(
            {
                "requirement_id": req_id,
                "source": "task_pack_md",
                "requirement": requirement,
                "acceptance": acceptance,
                "evidence_required": [],
                "status": "PENDING",
                "evidence_paths": [],
                "notes": "",
            }
        )
    return rows


def load_requirements_from_task_pack(task_pack_path: Path) -> tuple[str, list[dict[str, Any]]]:
    suffix = task_pack_path.suffix.lower()
    if suffix == ".zip":
        with zipfile.ZipFile(task_pack_path, "r") as archive:
            if "REQUIREMENTS/requirement_matrix_seed.json" in archive.namelist():
                payload = json.loads(archive.read("REQUIREMENTS/requirement_matrix_seed.json").decode("utf-8"))
                return payload.get("task_id", TASK_ID_DEFAULT), payload.get("requirements", [])
            if "task_pack.json" in archive.namelist():
                payload = json.loads(archive.read("task_pack.json").decode("utf-8"))
                return payload.get("task_id", TASK_ID_DEFAULT), []
            raise FileNotFoundError("No supported requirement seed found inside zip.")
    if suffix == ".json":
        payload = read_json(task_pack_path)
        if "requirements" in payload and isinstance(payload["requirements"], list):
            return payload.get("task_id", TASK_ID_DEFAULT), payload["requirements"]
        return payload.get("task_id", TASK_ID_DEFAULT), []
    if suffix == ".md":
        md_text = read_text(task_pack_path)
        task_id_match = re.search(r"TASK-[A-Z0-9\\-_]+", md_text)
        task_id = task_id_match.group(0) if task_id_match else TASK_ID_DEFAULT
        return task_id, parse_task_pack_from_md(md_text)
    raise ValueError("Unsupported task-pack extension. Use zip/json/md.")


def requirement_matrix_markdown(requirements: list[dict[str, Any]]) -> str:
    lines = ["# Requirement Matrix", "", "| REQ-ID | Requirement | Status | Evidence | Notes |", "|---|---|---|---|---|"]
    for req in requirements:
        req_id = str(req.get("requirement_id", "UNKNOWN"))
        requirement = str(req.get("requirement", "")).replace("|", "/")
        status = str(req.get("status", "PENDING"))
        evidence_paths = req.get("evidence_paths", [])
        evidence = "; ".join(str(item) for item in evidence_paths) if evidence_paths else "-"
        notes = str(req.get("notes", "")).replace("|", "/")
        lines.append(f"| {req_id} | {requirement} | {status} | {evidence} | {notes} |")
    lines.append("")
    return "\n".join(lines)


def cmd_requirements_compile(args: argparse.Namespace) -> int:
    task_pack_path = Path(args.task_pack).resolve()
    if not task_pack_path.exists():
        print(f"Task-pack not found: {task_pack_path}", file=sys.stderr)
        return 2
    ctx = create_context("requirements_compile")
    try:
        task_id, requirements = load_requirements_from_task_pack(task_pack_path)
    except Exception as error:
        print(f"Failed to parse task-pack: {error}", file=sys.stderr)
        return 2

    matrix = {"task_id": task_id, "source_task_pack": str(task_pack_path), "generated_at_utc": utc_now(), "requirements": requirements}
    out_dir = ctx.run_root / "requirements_compile"
    json_path = out_dir / "requirement_matrix.json"
    md_path = out_dir / "REQUIREMENT_MATRIX.md"
    write_json(json_path, matrix)
    write_text(md_path, requirement_matrix_markdown(requirements))

    receipt = emit_receipt(
        ctx,
        "requirements_compile_receipt.json",
        {
            "command": "requirements-compile",
            "task_pack": str(task_pack_path),
            "timestamp_utc": utc_now(),
            "verdict": "PASS",
            "requirements_count": len(requirements),
            "outputs": [str(json_path), str(md_path)],
        },
    )
    print_artifacts({"REQUIREMENT_MATRIX_JSON": json_path, "REQUIREMENT_MATRIX_MD": md_path, "RECEIPT": receipt})
    return 0


def build_pack_manifest(files: list[Path], base_dir: Path, agent: str) -> dict[str, Any]:
    records: list[dict[str, Any]] = []
    for file_path in files:
        rel = file_path.relative_to(base_dir).as_posix()
        records.append({"path": rel, "size_bytes": file_path.stat().st_size, "sha256": sha256_file(file_path)})
    return {"manifest_version": "OFFICIO_ROLE_PACK_MANIFEST_V0_1", "agent": agent, "created_at_utc": utc_now(), "files": records}


def create_sha256s_txt(files: list[Path], base_dir: Path) -> str:
    lines: list[str] = []
    for file_path in sorted(files, key=lambda item: item.name):
        rel = file_path.relative_to(base_dir).as_posix()
        lines.append(f"{sha256_file(file_path)}  {rel}")
    return "\n".join(lines) + "\n"


def cmd_pack_build_role(args: argparse.Namespace) -> int:
    try:
        agent = valid_agent(args.agent)
    except ValueError as error:
        print(str(error), file=sys.stderr)
        return 2

    role_profile = load_role_profile(agent)
    mode = str(role_profile.get("default_mode", "EXECUTOR"))
    _settings, settings_md = build_execution_settings(agent, mode)
    ctx = create_context("pack_build_role")

    pack_root = ctx.run_root / "role_pack_work" / agent
    pack_root.mkdir(parents=True, exist_ok=True)

    role_pack_md = pack_root / "ROLE_PACK.md"
    role_pack_json = pack_root / "role_pack.json"
    response_contract = pack_root / "RESPONSE_CONTRACT.md"
    execution_settings = pack_root / "EXECUTION_SETTINGS.md"
    stop_conditions = pack_root / "STOP_CONDITIONS.json"
    evidence_policy = pack_root / "EVIDENCE_POLICY.md"
    start_message = pack_root / "START_MESSAGE.txt"
    manifest = pack_root / "MANIFEST.json"
    sha256s = pack_root / "SHA256SUMS.txt"

    write_text(role_pack_md, f"# Role Pack: {agent}\n\n- generated_at_utc: {utc_now()}\n- default_mode: {mode}\n")
    write_json(role_pack_json, {"agent": agent, "role_profile": role_profile, "default_mode": mode, "status": STATUS_READY, "generated_at_utc": utc_now()})
    write_text(response_contract, read_text(response_contract_path_for(agent)))
    write_text(execution_settings, settings_md + "\n")
    write_json(stop_conditions, load_stop_conditions())
    write_text(evidence_policy, read_text(EVIDENCE_POLICY_DIR / "EVIDENCE_POLICY.md"))
    write_text(start_message, f"You are entering role: {agent}.\nRead ROLE_PACK.md first.\n")

    pre_manifest_files = [role_pack_md, role_pack_json, response_contract, execution_settings, stop_conditions, evidence_policy, start_message]
    write_json(manifest, build_pack_manifest(pre_manifest_files, pack_root, agent))
    all_files = pre_manifest_files + [manifest]
    write_text(sha256s, create_sha256s_txt(all_files, pack_root))

    zip_dir = ctx.run_root / "role_packs"
    zip_dir.mkdir(parents=True, exist_ok=True)
    zip_path = zip_dir / f"{agent}_ROLE_PACK.zip"
    with zipfile.ZipFile(zip_path, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for file_path in all_files + [sha256s]:
            archive.write(file_path, file_path.relative_to(pack_root).as_posix())

    receipt = emit_receipt(
        ctx,
        f"pack_build_role_{agent}_receipt.json",
        {"command": "pack-build-role", "agent": agent, "mode": mode, "timestamp_utc": utc_now(), "verdict": "PASS", "zip_path": str(zip_path), "outputs": [str(zip_path)]},
    )
    print_artifacts({"ROLE_PACK_ZIP": zip_path, "MANIFEST_JSON": manifest, "SHA256SUMS_TXT": sha256s, "RECEIPT": receipt})
    return 0


def resolve_matrix_from_input(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise FileNotFoundError(str(path))
    if path.suffix.lower() == ".zip":
        with zipfile.ZipFile(path, "r") as archive:
            if "requirement_matrix.json" in archive.namelist():
                return json.loads(archive.read("requirement_matrix.json").decode("utf-8"))
            raise ValueError("Zip does not contain requirement_matrix.json")
    if path.suffix.lower() == ".json":
        return read_json(path)
    raise ValueError("Unsupported compliance input. Use json or zip.")


def cmd_compliance_check(args: argparse.Namespace) -> int:
    matrix_input = args.matrix if args.matrix else args.input
    if not matrix_input:
        print("Provide --matrix or --input", file=sys.stderr)
        return 2

    matrix_path = Path(matrix_input).resolve()
    try:
        payload = resolve_matrix_from_input(matrix_path)
    except Exception as error:
        print(f"Compliance input error: {error}", file=sys.stderr)
        return 2

    requirements = payload.get("requirements", []) if isinstance(payload, dict) else []
    missing_evidence: list[str] = []
    unfinished: list[str] = []
    invalid_status: list[str] = []
    allowed_statuses = {"PENDING", "DONE", "BLOCKED", "NOT_DONE"}
    for req in requirements:
        req_id = str(req.get("requirement_id", "UNKNOWN"))
        status = str(req.get("status", "PENDING"))
        evidence_paths = req.get("evidence_paths", [])
        if status not in allowed_statuses:
            invalid_status.append(req_id)
        if status != "DONE":
            unfinished.append(req_id)
        if status == "DONE" and not evidence_paths:
            missing_evidence.append(req_id)

    verdict = "PASS"
    if invalid_status:
        verdict = "FAIL"
    elif missing_evidence or unfinished:
        verdict = "WARN"

    ctx = create_context("compliance_check")
    out_dir = ctx.run_root / "compliance_check"
    summary_json = out_dir / "compliance_check.json"
    summary_md = out_dir / "COMPLIANCE_CHECK.md"
    write_json(
        summary_json,
        {
            "matrix_input": str(matrix_path),
            "checked_at_utc": utc_now(),
            "requirements_total": len(requirements),
            "unfinished_requirements": unfinished,
            "done_without_evidence": missing_evidence,
            "invalid_status_requirements": invalid_status,
            "verdict": verdict,
        },
    )
    write_text(summary_md, f"# Compliance Check\n\n- verdict: `{verdict}`\n")

    receipt = emit_receipt(
        ctx,
        "compliance_check_receipt.json",
        {"command": "compliance-check", "matrix": str(matrix_path), "timestamp_utc": utc_now(), "verdict": verdict, "outputs": [str(summary_json), str(summary_md)]},
    )
    print_artifacts({"COMPLIANCE_JSON": summary_json, "COMPLIANCE_MD": summary_md, "RECEIPT": receipt})
    return 0 if verdict in {"PASS", "WARN"} else 1


def cmd_setting_list(_args: argparse.Namespace) -> int:
    ctx = create_context("setting_list")
    index = load_settings_index()
    settings = index.get("settings", [])
    out_dir = ctx.run_root / "setting_list"
    out_json = out_dir / "settings_registry_index.json"
    out_md = out_dir / "SETTING_LIST.md"
    write_json(out_json, index)
    lines = ["# Settings List", "", "| setting_id | state | path |", "|---|---|---|"]
    for entry in settings:
        lines.append(f"| {entry.get('setting_id', '')} | {entry.get('state', '')} | {entry.get('path', '')} |")
    lines.append("")
    write_text(out_md, "\n".join(lines))
    receipt = emit_receipt(ctx, "setting_list_receipt.json", {"command": "setting-list", "timestamp_utc": utc_now(), "verdict": "PASS", "outputs": [str(out_json), str(out_md)]})
    print_artifacts({"SETTINGS_INDEX_JSON": out_json, "SETTING_LIST_MD": out_md, "RECEIPT": receipt})
    return 0


def cmd_setting_show(args: argparse.Namespace) -> int:
    ctx = create_context("setting_show")
    index = load_settings_index()
    target = None
    for entry in index.get("settings", []):
        if str(entry.get("setting_id", "")) == args.setting_id:
            target = entry
            break
    if target is None:
        print(f"Unknown setting_id: {args.setting_id}", file=sys.stderr)
        return 1

    setting_path = ROOT / str(target.get("path", ""))
    if not setting_path.exists():
        print(f"Indexed setting file missing: {setting_path}", file=sys.stderr)
        return 1

    setting_json = read_json(setting_path)
    out_dir = ctx.run_root / "setting_show" / args.setting_id
    out_json = out_dir / "setting.json"
    out_md = out_dir / "SETTING_SHOW.md"
    write_json(out_json, setting_json)
    write_text(out_md, f"# Setting: {args.setting_id}\n\n- path: `{setting_path}`\n- state: `{setting_json.get('state', 'UNKNOWN')}`\n")
    receipt = emit_receipt(ctx, "setting_show_receipt.json", {"command": "setting-show", "setting_id": args.setting_id, "timestamp_utc": utc_now(), "verdict": "PASS", "outputs": [str(out_json), str(out_md)]})
    print_artifacts({"SETTING_JSON": out_json, "SETTING_MD": out_md, "RECEIPT": receipt})
    return 0


def validate_officio_setting(payload: dict[str, Any]) -> list[str]:
    problems: list[str] = []
    for field in OFFICIO_SETTING_REQUIRED_FIELDS:
        if field not in payload:
            problems.append(f"missing:{field}")
    state = str(payload.get("state", ""))
    if state and state not in {"DRAFT", "REVIEW", "ACTIVE", "DEPRECATED", "TOMBSTONE"}:
        problems.append(f"invalid_state:{state}")
    return problems


def cmd_setting_validate(_args: argparse.Namespace) -> int:
    ctx = create_context("setting_validate")
    index = load_settings_index()
    entries = index.get("settings", [])
    results: list[dict[str, Any]] = []
    errors: list[str] = []
    for entry in entries:
        sid = str(entry.get("setting_id", "UNKNOWN"))
        setting_path = ROOT / str(entry.get("path", ""))
        if not setting_path.exists():
            errors.append(f"{sid}:missing_file")
            continue
        try:
            payload = read_json(setting_path)
        except Exception as error:
            errors.append(f"{sid}:invalid_json:{error}")
            continue
        problems = validate_officio_setting(payload)
        results.append({"setting_id": sid, "path": str(setting_path), "problems": problems})
        errors.extend([f"{sid}:{problem}" for problem in problems])

    verdict = "PASS" if not errors else "FAIL"
    out_dir = ctx.run_root / "setting_validate"
    out_json = out_dir / "schema_validation_report.json"
    out_txt = out_dir / "setting_validate_output.txt"
    write_json(out_json, {"checked_at_utc": utc_now(), "verdict": verdict, "checked_settings": len(entries), "errors": errors, "results": results})
    write_text(out_txt, f"verdict={verdict}\nchecked_settings={len(entries)}\nerror_count={len(errors)}\n")
    receipt = emit_receipt(ctx, "setting_validate_receipt.json", {"command": "setting-validate", "timestamp_utc": utc_now(), "verdict": verdict, "outputs": [str(out_json), str(out_txt)]})
    print_artifacts({"SCHEMA_VALIDATION_REPORT": out_json, "SETTING_VALIDATE_OUTPUT": out_txt, "RECEIPT": receipt})
    return 0 if verdict == "PASS" else 1


def cmd_prompt_pack_validate(args: argparse.Namespace) -> int:
    ctx = create_context("prompt_pack_validate")
    zip_path = Path(args.zip_path).resolve()
    if not zip_path.exists() or zip_path.suffix.lower() != ".zip":
        print(f"Invalid zip path: {zip_path}", file=sys.stderr)
        return 2
    policy = read_json(SETTINGS_REGISTRY / "prompt_intake" / "prompt_intake_policy.json")
    required_files = policy.get("machine_rule", {}).get("required_files", [])
    with zipfile.ZipFile(zip_path, "r") as archive:
        names = set(archive.namelist())
    missing = [item for item in required_files if item not in names]
    verdict = "PASS" if not missing else "BLOCKED_PROMPT_PACK_INVALID"

    out_dir = ctx.run_root / "prompt_pack_validate"
    out_json = out_dir / "prompt_pack_validation.json"
    out_txt = out_dir / "prompt_pack_validation_output.txt"
    write_json(out_json, {"zip_path": str(zip_path), "missing_files": missing, "verdict": verdict, "checked_at_utc": utc_now()})
    write_text(out_txt, f"zip_path={zip_path}\nverdict={verdict}\nmissing_files={','.join(missing) if missing else '<none>'}\n")
    receipt = emit_receipt(ctx, "prompt_pack_validate_receipt.json", {"command": "prompt-pack-validate", "timestamp_utc": utc_now(), "verdict": "PASS" if verdict == "PASS" else "BLOCKED", "outputs": [str(out_json), str(out_txt)]})
    print_artifacts({"PROMPT_PACK_VALIDATION_JSON": out_json, "PROMPT_PACK_VALIDATION_OUTPUT": out_txt, "RECEIPT": receipt})
    return 0 if verdict == "PASS" else 1


def load_task_pack_payload(task_pack_path: Path) -> dict[str, Any]:
    if task_pack_path.suffix.lower() == ".zip":
        with zipfile.ZipFile(task_pack_path, "r") as archive:
            if "task_pack.json" not in archive.namelist():
                return {}
            return json.loads(archive.read("task_pack.json").decode("utf-8"))
    if task_pack_path.suffix.lower() == ".json":
        return read_json(task_pack_path)
    if task_pack_path.suffix.lower() == ".md":
        md = read_text(task_pack_path)
        task_id_match = re.search(r"TASK-[A-Z0-9\\-_]+", md)
        return {"task_id": task_id_match.group(0) if task_id_match else "UNKNOWN", "raw_md": md}
    return {}


def normalize_scope_values(payload: dict[str, Any]) -> list[str]:
    values: list[str] = []
    if isinstance(payload.get("allowed_scope"), list):
        values.extend([str(x) for x in payload["allowed_scope"]])
    scope = payload.get("scope")
    if isinstance(scope, dict) and isinstance(scope.get("allowed_paths"), list):
        values.extend([str(x) for x in scope["allowed_paths"]])
    return values


def cmd_task_acceptance_check(args: argparse.Namespace) -> int:
    ctx = create_context("task_acceptance_check")
    task_pack_path = Path(args.task_pack).resolve()
    if not task_pack_path.exists():
        print(f"Task pack not found: {task_pack_path}", file=sys.stderr)
        return 2

    payload = load_task_pack_payload(task_pack_path)
    policy = read_json(SETTINGS_REGISTRY / "task_acceptance" / "task_acceptance_policy.json")
    required_fields = policy.get("machine_rule", {}).get("required_task_fields", [])
    def has_required_field(field: str, obj: dict[str, Any]) -> bool:
        if field in obj:
            return True
        if field == "expected_base_head":
            repo_obj = obj.get("repo")
            return isinstance(repo_obj, dict) and "expected_base_head" in repo_obj
        return False

    missing_fields = [field for field in required_fields if not has_required_field(field, payload)]

    decision = "ACCEPT"
    reasons: list[str] = []
    if missing_fields:
        decision = "CLARIFICATION_REQUIRED"
        reasons.append("missing required fields: " + ", ".join(missing_fields))

    if decision == "ACCEPT":
        for scope in normalize_scope_values(payload):
            if any(marker in scope for marker in ["ORGANS/", "SANCTUM/", "IMPERIUM_TEST_VERSION/", "ADMINISTRATUM_AGENT/"]):
                decision = "BLOCKED_OUT_OF_SCOPE"
                reasons.append(f"forbidden scope marker in: {scope}")
                break

    text_blob = json.dumps(payload, ensure_ascii=False).lower()
    if decision == "ACCEPT" and any(k in text_blob for k in ["rm -rf", "wipe all", "delete all", "format disk"]):
        decision = "BLOCKED_UNSAFE"
        reasons.append("unsafe keyword detected")

    if decision == "ACCEPT" and isinstance(payload.get("requirements"), list) and len(payload["requirements"]) > 40:
        decision = "SPLIT_REQUIRED"
        reasons.append("too many requirements for a single bounded execution")

    if decision == "ACCEPT" and "evidence_policy_file" not in payload:
        decision = "ACCEPT_WITH_WARNINGS"
        reasons.append("explicit evidence_policy_file not found")

    out_dir = ctx.run_root / "task_acceptance_check"
    out_json = out_dir / "task_acceptance_check.json"
    out_txt = out_dir / "task_acceptance_check_output.txt"
    write_json(out_json, {"task_pack_path": str(task_pack_path), "checked_at_utc": utc_now(), "decision": decision, "reasons": reasons, "missing_fields": missing_fields})
    write_text(out_txt, f"task_pack_path={task_pack_path}\ndecision={decision}\nreasons={'; '.join(reasons) if reasons else '<none>'}\n")
    receipt = emit_receipt(ctx, "task_acceptance_check_receipt.json", {"command": "task-acceptance-check", "timestamp_utc": utc_now(), "verdict": "PASS", "decision": decision, "outputs": [str(out_json), str(out_txt)]})
    print_artifacts({"TASK_ACCEPTANCE_JSON": out_json, "TASK_ACCEPTANCE_OUTPUT": out_txt, "RECEIPT": receipt})
    return 0


def cmd_recent(args: argparse.Namespace) -> int:
    runtime_root = get_runtime_root()
    runs = [p for p in runtime_root.iterdir() if p.is_dir() and p.name.startswith("run_")]
    for item in sorted(runs, key=lambda i: i.name, reverse=True)[: max(1, int(args.limit))]:
        print(item)
    return 0


def cmd_check_all(_args: argparse.Namespace) -> int:
    ctx = create_context("check_all")
    required_files = [
        ROOT / "README.md",
        ROOT / "TOOLS" / "officio_agent_runner.py",
        SETTINGS_REGISTRY / "settings_index.json",
        SCHEMAS_DIR / "officio_setting.schema.json",
        SCHEMAS_DIR / "prompt_pack_contract.schema.json",
        SCHEMAS_DIR / "task_acceptance_policy.schema.json",
        ROLE_REGISTRY / "SERVITOR" / "role_profile.json",
        ROLE_REGISTRY / "SERVITOR" / "allowed_modes.json",
        ROLE_REGISTRY / "SERVITOR" / "read_order.json",
        ROLE_REGISTRY / "LOGOS_PRIME" / "role_profile.json",
        ROLE_REGISTRY / "LOGOS_PRIME" / "allowed_modes.json",
        ROLE_REGISTRY / "LOGOS_PRIME" / "read_order.json",
        ROLE_REGISTRY / "LOGOS_SPECULUM" / "role_profile.json",
        ROLE_REGISTRY / "LOGOS_SPECULUM" / "allowed_modes.json",
        ROLE_REGISTRY / "LOGOS_SPECULUM" / "read_order.json",
        EXAMPLES_DIR / "accepted_tasks" / "accepted_task_example.json",
        EXAMPLES_DIR / "rejected_tasks" / "rejected_task_out_of_scope.json",
        EXAMPLES_DIR / "valid_prompt_packs" / "valid_prompt_pack_manifest.json",
        EXAMPLES_DIR / "invalid_prompt_packs" / "missing_required_files.json",
    ]
    missing_files = [str(path) for path in required_files if not path.exists()]

    invalid_json: list[dict[str, str]] = []
    for path in ROOT.rglob("*.json"):
        try:
            read_json(path)
        except Exception as error:
            invalid_json.append({"path": str(path), "error": str(error)})

    settings_index_errors: list[str] = []
    try:
        idx = load_settings_index()
        for entry in idx.get("settings", []):
            setting_path = ROOT / str(entry.get("path", ""))
            if not setting_path.exists():
                settings_index_errors.append(f"missing_indexed_setting:{setting_path}")
            else:
                payload = read_json(setting_path)
                for field in OFFICIO_SETTING_REQUIRED_FIELDS:
                    if field not in payload:
                        settings_index_errors.append(f"missing_field:{setting_path.relative_to(ROOT)}:{field}")
    except Exception as error:
        settings_index_errors.append(f"settings_index_error:{error}")

    verdict = "PASS" if not missing_files and not invalid_json and not settings_index_errors else "FAIL"
    out_dir = ctx.run_root / "check_all"
    report_json = out_dir / "check_all_report.json"
    report_txt = out_dir / "check_all_output.txt"
    write_json(report_json, {"checked_at_utc": utc_now(), "verdict": verdict, "missing_files": missing_files, "invalid_json": invalid_json, "settings_index_errors": settings_index_errors})
    write_text(report_txt, f"verdict={verdict}\nmissing_files={len(missing_files)}\ninvalid_json={len(invalid_json)}\nsettings_index_errors={len(settings_index_errors)}\n")
    receipt = emit_receipt(ctx, "check_all_receipt.json", {"command": "check-all", "timestamp_utc": utc_now(), "verdict": verdict, "outputs": [str(report_json), str(report_txt)]})
    print_artifacts({"CHECK_ALL_JSON": report_json, "CHECK_ALL_OUTPUT": report_txt, "RECEIPT": receipt})
    return 0 if verdict == "PASS" else 1


def map_slash_to_runner_args(raw: str) -> list[str] | None:
    parts = raw.strip().split()
    if not parts:
        return None
    cmd = parts[0]
    if cmd == "/status":
        return ["status"]
    if cmd == "/check-all":
        return ["check-all"]
    if cmd == "/role-get" and len(parts) == 2:
        return ["role-get", "--agent", parts[1]]
    if cmd == "/settings-get" and len(parts) == 3:
        return ["settings-get", "--agent", parts[1], "--mode", parts[2]]
    if cmd == "/setting-list":
        return ["setting-list"]
    if cmd == "/setting-show" and len(parts) >= 2:
        return ["setting-show", "--setting-id", " ".join(parts[1:])]
    if cmd == "/setting-validate":
        return ["setting-validate"]
    if cmd == "/prompt-pack-validate" and len(parts) >= 2:
        return ["prompt-pack-validate", "--zip-path", " ".join(parts[1:])]
    if cmd == "/task-acceptance-check" and len(parts) >= 2:
        return ["task-acceptance-check", "--task-pack", " ".join(parts[1:])]
    if cmd == "/pack-build-role" and len(parts) == 2:
        return ["pack-build-role", "--agent", parts[1]]
    if cmd == "/compliance-check" and len(parts) >= 2:
        return ["compliance-check", "--input", " ".join(parts[1:])]
    if cmd == "/recent":
        return ["recent"]
    return None


def render_shell_view(console: Any, latest_output: str, warnings: list[str], run_id: str, artifacts: list[str]) -> None:
    command_list = [
        "/help",
        "/status",
        "/check-all",
        "/role-get <AGENT>",
        "/settings-get <AGENT> <MODE>",
        "/setting-list",
        "/setting-show <setting_id>",
        "/setting-validate",
        "/prompt-pack-validate <zip_path>",
        "/task-acceptance-check <task_pack_path>",
        "/pack-build-role <AGENT>",
        "/compliance-check <bundle_or_matrix_path>",
        "/recent",
        "/exit",
    ]
    g = git_info()
    header_text = "\n".join(
        [
            f"Officio Agentis | {STATUS_READY}",
            f"HEAD: {g['head']}",
            f"Dirty: {g['dirty']}",
            f"Runtime: {get_runtime_root()}",
            "Role count: 3 | Mode count: 4",
        ]
    )
    right_text = "\n".join(command_list)
    bottom_text = "\n".join(
        [
            f"run_id: {run_id}",
            "warnings: " + (", ".join(warnings) if warnings else "none"),
            "artifacts: " + (", ".join(artifacts[-3:]) if artifacts else "none"),
        ]
    )

    if HAVE_RICH and console is not None:
        layout = Layout()
        layout.split_column(Layout(name="header", size=6), Layout(name="body"), Layout(name="bottom", size=5))
        layout["body"].split_row(Layout(name="main"), Layout(name="right", size=45))
        layout["header"].update(Panel(header_text, title="HEADER"))
        layout["main"].update(Panel(latest_output or "No output yet.", title="LEFT MAIN ZONE"))
        layout["right"].update(Panel(right_text, title="RIGHT COMMAND ZONE"))
        layout["bottom"].update(Panel(bottom_text, title="BOTTOM STATUS ZONE"))
        console.clear()
        console.print(layout)
    else:
        print("=== HEADER ===")
        print(header_text)
        print("=== LEFT MAIN ZONE ===")
        print(latest_output or "No output yet.")
        print("=== RIGHT COMMAND ZONE ===")
        print(right_text)
        print("=== BOTTOM STATUS ZONE ===")
        print(bottom_text)


def cmd_shell(args: argparse.Namespace) -> int:
    ctx = create_context("shell")
    shell_dir = ctx.run_root / "shell"
    shell_dir.mkdir(parents=True, exist_ok=True)
    transcript_path = shell_dir / "shell_transcript.txt"
    color_diag_path = shell_dir / "rich_color_diagnostic.txt"

    color_diag = {"rich_available": HAVE_RICH, "python": sys.version, "runtime_root": str(ctx.runtime_root), "timestamp_utc": utc_now()}
    if HAVE_RICH:
        c = Console()  # type: ignore[misc]
        color_diag["color_system"] = str(c.color_system)
        console_obj = c
    else:
        color_diag["color_system"] = "none"
        console_obj = None
    write_text(color_diag_path, json.dumps(color_diag, ensure_ascii=False, indent=2) + "\n")

    command_lines: list[str] = []
    if args.commands_file:
        command_lines.extend([line.strip() for line in Path(args.commands_file).read_text(encoding="utf-8").splitlines()])

    latest_output = "Use /help to list commands."
    warnings: list[str] = []
    artifacts: list[str] = [str(color_diag_path)]
    transcript_rows: list[str] = [f"shell_run={ctx.run_root}"]
    run_id = ctx.run_root.name

    def execute_slash(raw: str) -> bool:
        nonlocal latest_output
        raw = raw.strip()
        if not raw:
            return True
        transcript_rows.append(f"> {raw}")
        if raw == "/help":
            latest_output = (
                "Commands:\n"
                "/help\n/status\n/check-all\n/role-get SERVITOR|LOGOS_PRIME|LOGOS_SPECULUM\n"
                "/settings-get <AGENT> <MODE>\n/setting-list\n/setting-show <setting_id>\n/setting-validate\n"
                "/prompt-pack-validate <zip_path>\n/task-acceptance-check <task_pack_path>\n"
                "/pack-build-role <AGENT>\n/compliance-check <bundle_or_matrix_path>\n/recent\n/exit"
            )
            transcript_rows.append(latest_output)
            return True
        if raw == "/exit":
            latest_output = "exit requested"
            transcript_rows.append(latest_output)
            return False
        mapped = map_slash_to_runner_args(raw)
        if mapped is None:
            latest_output = f"Unknown or malformed command: {raw}"
            warnings.append(latest_output)
            transcript_rows.append(latest_output)
            return True
        completed = subprocess.run([sys.executable, str(Path(__file__).resolve()), *mapped], capture_output=True, text=True)
        output = (completed.stdout + "\n" + completed.stderr).strip()
        latest_output = output if output else "<no output>"
        transcript_rows.append(latest_output)
        for line in completed.stdout.splitlines():
            if ": " in line:
                _, p = line.split(": ", 1)
                if p.startswith("E:\\") or p.startswith("C:\\"):
                    artifacts.append(p)
        if completed.returncode != 0:
            warnings.append(f"command_failed:{raw}:code={completed.returncode}")
        return True

    if command_lines:
        for line in command_lines:
            if not execute_slash(line):
                break
            render_shell_view(console_obj, latest_output, warnings, run_id, artifacts)

    if not args.non_interactive:
        while True:
            render_shell_view(console_obj, latest_output, warnings, run_id, artifacts)
            try:
                raw = input("officio> ").strip()
            except EOFError:
                break
            if not execute_slash(raw):
                break

    write_text(transcript_path, "\n".join(transcript_rows) + "\n")
    receipt = emit_receipt(
        ctx,
        "shell_receipt.json",
        {"command": "shell", "timestamp_utc": utc_now(), "verdict": "PASS", "warnings": warnings, "outputs": [str(transcript_path), str(color_diag_path)]},
    )
    print_artifacts({"SHELL_TRANSCRIPT": transcript_path, "RICH_COLOR_DIAGNOSTIC": color_diag_path, "RECEIPT": receipt})
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Officio Agent Runner V0.1+")
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("status")
    role_get = sub.add_parser("role-get")
    role_get.add_argument("--agent", required=True)
    settings_get = sub.add_parser("settings-get")
    settings_get.add_argument("--agent", required=True)
    settings_get.add_argument("--mode", required=True)
    req_compile = sub.add_parser("requirements-compile")
    req_compile.add_argument("--task-pack", required=True)
    pack_build = sub.add_parser("pack-build-role")
    pack_build.add_argument("--agent", required=True)
    compliance = sub.add_parser("compliance-check")
    compliance.add_argument("--matrix", required=False, default=None)
    compliance.add_argument("--input", required=False, default=None)
    compliance.add_argument("--evidence", required=False, default=None)
    sub.add_parser("check-all")
    sub.add_parser("setting-list")
    setting_show = sub.add_parser("setting-show")
    setting_show.add_argument("--setting-id", required=True)
    sub.add_parser("setting-validate")
    prompt_validate = sub.add_parser("prompt-pack-validate")
    prompt_validate.add_argument("--zip-path", required=True)
    acceptance = sub.add_parser("task-acceptance-check")
    acceptance.add_argument("--task-pack", required=True)
    recent = sub.add_parser("recent")
    recent.add_argument("--limit", default="20")
    shell = sub.add_parser("shell")
    shell.add_argument("--commands-file", required=False, default=None)
    shell.add_argument("--non-interactive", action="store_true")
    return parser


def main(argv: list[str]) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    if args.command == "status":
        return cmd_status(args)
    if args.command == "role-get":
        return cmd_role_get(args)
    if args.command == "settings-get":
        return cmd_settings_get(args)
    if args.command == "requirements-compile":
        return cmd_requirements_compile(args)
    if args.command == "pack-build-role":
        return cmd_pack_build_role(args)
    if args.command == "compliance-check":
        return cmd_compliance_check(args)
    if args.command == "check-all":
        return cmd_check_all(args)
    if args.command == "setting-list":
        return cmd_setting_list(args)
    if args.command == "setting-show":
        return cmd_setting_show(args)
    if args.command == "setting-validate":
        return cmd_setting_validate(args)
    if args.command == "prompt-pack-validate":
        return cmd_prompt_pack_validate(args)
    if args.command == "task-acceptance-check":
        return cmd_task_acceptance_check(args)
    if args.command == "recent":
        return cmd_recent(args)
    if args.command == "shell":
        return cmd_shell(args)
    parser.print_help()
    return 2


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
