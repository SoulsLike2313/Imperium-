from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shutil
import sys
import zipfile
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


TASK_ID_DEFAULT = "TASK-20260518-OFFICIO-AGENTIS-BASE-IDENTITY-FOUNDATION-V0_1"
STATUS_READY = "FOUNDATION_V0_1_READY_FOR_REVIEW"
DEFAULT_RUNTIME_ROOT = Path(r"E:\IMPERIUM_CONTEXT\LOCAL\OFFICIO_AGENTIS\RUNS")

ROOT = Path(__file__).resolve().parent.parent
ROLE_REGISTRY = ROOT / "ROLE_REGISTRY"
MODE_REGISTRY = ROOT / "MODE_REGISTRY"
SETTINGS_REGISTRY = ROOT / "SETTINGS_REGISTRY"
RESPONSE_CONTRACTS = ROOT / "RESPONSE_CONTRACTS"
EVIDENCE_POLICY_DIR = ROOT / "EVIDENCE_POLICY"
SCHEMAS_DIR = ROOT / "SCHEMAS"

ROLE_RESPONSE_CONTRACT_FILE = {
    "SERVITOR": "SERVITOR_EXECUTOR_RESPONSE_CONTRACT.md",
    "LOGOS_PRIME": "LOGOS_PRIME_RESPONSE_CONTRACT.md",
    "LOGOS_SPECULUM": "LOGOS_SPECULUM_RESPONSE_CONTRACT.md",
}


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


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


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
        "stop_conditions": stops["stop_conditions"],
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
            *[f"- {entry}" for entry in role.get("obligations", [])],
            "",
            "## Mode Intent",
            f"- {mode_profile.get('intent', 'n/a')}",
            "",
            "## Core Permissions",
            *[f"- {entry}" for entry in permissions.get("global_permissions", [])],
            "",
            "## Forbidden Actions",
            *[f"- {entry}" for entry in forbidden.get("forbidden_actions", [])],
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
    payload = {
        "task_id_default": TASK_ID_DEFAULT,
        "status": STATUS_READY,
        "root": str(ROOT),
        "runtime_root": str(ctx.runtime_root),
        "supported_agents": sorted(ROLE_RESPONSE_CONTRACT_FILE.keys()),
        "supported_modes": [
            "EXECUTOR",
            "AUDITOR",
            "ARCHITECT",
            "REPAIRER",
        ],
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
                "",
                "Supported agents:",
                "- SERVITOR",
                "- LOGOS_PRIME",
                "- LOGOS_SPECULUM",
            ]
        )
        + "\n",
    )
    receipt = emit_receipt(
        ctx,
        "status_receipt.json",
        {
            "command": "status",
            "timestamp_utc": utc_now(),
            "verdict": "PASS",
            "outputs": [str(status_json), str(status_md)],
        },
    )
    print_artifacts(
        {
            "STATUS_JSON": status_json,
            "STATUS_MD": status_md,
            "RECEIPT": receipt,
        }
    )
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
        {
            "command": "role-get",
            "agent": agent,
            "timestamp_utc": utc_now(),
            "verdict": "PASS",
            "outputs": [str(out_md), str(out_json)],
        },
    )
    print_artifacts(
        {
            "ROLE_PROFILE_MD": out_md,
            "ROLE_PROFILE_JSON": out_json,
            "RECEIPT": receipt,
        }
    )
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
                payload = json.loads(
                    archive.read("REQUIREMENTS/requirement_matrix_seed.json").decode("utf-8")
                )
                task_id = payload.get("task_id", TASK_ID_DEFAULT)
                requirements = payload.get("requirements", [])
                return task_id, requirements
            if "task_pack.json" in archive.namelist():
                payload = json.loads(archive.read("task_pack.json").decode("utf-8"))
                task_id = payload.get("task_id", TASK_ID_DEFAULT)
                return task_id, []
            raise FileNotFoundError("No supported requirement seed found inside zip.")

    if suffix == ".json":
        payload = read_json(task_pack_path)
        task_id = payload.get("task_id", TASK_ID_DEFAULT)
        if "requirements" in payload and isinstance(payload["requirements"], list):
            return task_id, payload["requirements"]
        return task_id, []

    if suffix == ".md":
        md_text = read_text(task_pack_path)
        task_id_match = re.search(r"TASK-[A-Z0-9\\-_]+", md_text)
        task_id = task_id_match.group(0) if task_id_match else TASK_ID_DEFAULT
        return task_id, parse_task_pack_from_md(md_text)

    raise ValueError("Unsupported task-pack extension. Use zip/json/md.")


def requirement_matrix_markdown(requirements: list[dict[str, Any]]) -> str:
    lines = [
        "# Requirement Matrix",
        "",
        "| REQ-ID | Requirement | Status | Evidence | Notes |",
        "|---|---|---|---|---|",
    ]
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

    matrix = {
        "task_id": task_id,
        "source_task_pack": str(task_pack_path),
        "generated_at_utc": utc_now(),
        "requirements": requirements,
    }

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
    print_artifacts(
        {
            "REQUIREMENT_MATRIX_JSON": json_path,
            "REQUIREMENT_MATRIX_MD": md_path,
            "RECEIPT": receipt,
        }
    )
    return 0


def build_pack_manifest(files: list[Path], base_dir: Path, agent: str) -> dict[str, Any]:
    records: list[dict[str, Any]] = []
    for file_path in files:
        rel = file_path.relative_to(base_dir).as_posix()
        records.append(
            {
                "path": rel,
                "size_bytes": file_path.stat().st_size,
                "sha256": sha256_file(file_path),
            }
        )
    return {
        "manifest_version": "OFFICIO_ROLE_PACK_MANIFEST_V0_1",
        "agent": agent,
        "created_at_utc": utc_now(),
        "files": records,
    }


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
    settings, settings_md = build_execution_settings(agent, mode)
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

    write_text(
        role_pack_md,
        "\n".join(
            [
                f"# Role Pack: {agent}",
                "",
                f"- generated_at_utc: {utc_now()}",
                f"- default_mode: {mode}",
                "- this pack is foundation V0.1 and evidence-first",
                "",
                "Use this order:",
                "1. Read role profile and contract.",
                "2. Read execution settings and stop conditions.",
                "3. Send ACK before main task execution.",
            ]
        )
        + "\n",
    )

    role_payload = {
        "agent": agent,
        "role_profile": role_profile,
        "default_mode": mode,
        "status": STATUS_READY,
        "generated_at_utc": utc_now(),
    }
    write_json(role_pack_json, role_payload)
    write_text(response_contract, read_text(response_contract_path_for(agent)))
    write_text(execution_settings, settings_md + "\n")
    write_json(stop_conditions, load_stop_conditions())
    write_text(evidence_policy, read_text(EVIDENCE_POLICY_DIR / "EVIDENCE_POLICY.md"))

    start_msg = [
        f"You are entering role: {agent}.",
        "Read ROLE_PACK.md first, then RESPONSE_CONTRACT.md.",
        "Acknowledge role and settings before task execution.",
    ]
    if agent == "LOGOS_PRIME":
        start_msg.append(
            "For new chat handoff: load this ZIP, read ROLE_PACK.md, then produce plan with clear truth/assumption split."
        )
    write_text(start_message, "\n".join(start_msg) + "\n")

    pre_manifest_files = [
        role_pack_md,
        role_pack_json,
        response_contract,
        execution_settings,
        stop_conditions,
        evidence_policy,
        start_message,
    ]

    manifest_payload = build_pack_manifest(pre_manifest_files, pack_root, agent)
    write_json(manifest, manifest_payload)
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
        {
            "command": "pack-build-role",
            "agent": agent,
            "mode": mode,
            "timestamp_utc": utc_now(),
            "verdict": "PASS",
            "zip_path": str(zip_path),
            "manifest_path": str(manifest),
            "sha256s_path": str(sha256s),
        },
    )
    print_artifacts(
        {
            "ROLE_PACK_ZIP": zip_path,
            "MANIFEST_JSON": manifest,
            "SHA256SUMS_TXT": sha256s,
            "RECEIPT": receipt,
        }
    )
    return 0


def cmd_compliance_check(args: argparse.Namespace) -> int:
    matrix_path = Path(args.matrix).resolve()
    if not matrix_path.exists():
        print(f"Matrix not found: {matrix_path}", file=sys.stderr)
        return 2

    ctx = create_context("compliance_check")
    payload = read_json(matrix_path)
    requirements = payload.get("requirements", [])

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

    summary = {
        "matrix_path": str(matrix_path),
        "checked_at_utc": utc_now(),
        "requirements_total": len(requirements),
        "unfinished_requirements": unfinished,
        "done_without_evidence": missing_evidence,
        "invalid_status_requirements": invalid_status,
        "evidence_input": args.evidence,
        "verdict": verdict,
        "skeleton_level": "V0.1",
    }

    out_dir = ctx.run_root / "compliance_check"
    summary_json = out_dir / "compliance_check.json"
    summary_md = out_dir / "COMPLIANCE_CHECK.md"
    write_json(summary_json, summary)
    unfinished_lines = [f"- {req_id}" for req_id in unfinished] if unfinished else ["- none"]
    write_text(
        summary_md,
        "\n".join(
            [
                "# Compliance Check",
                "",
                f"- verdict: `{verdict}`",
                f"- requirements_total: `{len(requirements)}`",
                f"- unfinished_count: `{len(unfinished)}`",
                f"- done_without_evidence_count: `{len(missing_evidence)}`",
                f"- invalid_status_count: `{len(invalid_status)}`",
                "",
                "Unfinished requirement IDs:",
                *unfinished_lines,
            ]
        )
        + "\n",
    )

    receipt = emit_receipt(
        ctx,
        "compliance_check_receipt.json",
        {
            "command": "compliance-check",
            "matrix": str(matrix_path),
            "timestamp_utc": utc_now(),
            "verdict": verdict,
            "outputs": [str(summary_json), str(summary_md)],
        },
    )
    print_artifacts(
        {
            "COMPLIANCE_JSON": summary_json,
            "COMPLIANCE_MD": summary_md,
            "RECEIPT": receipt,
        }
    )
    return 0 if verdict in {"PASS", "WARN"} else 1


def cmd_check_all(_args: argparse.Namespace) -> int:
    ctx = create_context("check_all")

    required_files = [
        ROOT / "README.md",
        ROOT / "BASE_HALF" / "runner_contract.md",
        ROOT / "IDENTITY_HALF" / "organ_identity.json",
        ROOT / "ROLE_REGISTRY" / "SERVITOR" / "role_profile.json",
        ROOT / "ROLE_REGISTRY" / "LOGOS_PRIME" / "role_profile.json",
        ROOT / "ROLE_REGISTRY" / "LOGOS_SPECULUM" / "role_profile.json",
        ROOT / "SETTINGS_REGISTRY" / "stop_conditions" / "stop_conditions.json",
        ROOT / "EVIDENCE_POLICY" / "evidence_policy.json",
        ROOT / "RESPONSE_CONTRACTS" / "SERVITOR_EXECUTOR_RESPONSE_CONTRACT.md",
    ]

    missing_files = [str(path) for path in required_files if not path.exists()]

    json_targets = [
        ROOT / "agent_manifest.json",
        ROOT / "IDENTITY_HALF" / "organ_identity.json",
        ROOT / "SETTINGS_REGISTRY" / "stop_conditions" / "stop_conditions.json",
        ROOT / "EVIDENCE_POLICY" / "evidence_policy.json",
        ROOT / "SCHEMAS" / "requirement_entry.schema.json",
        ROOT / "SCHEMAS" / "requirement_matrix.schema.json",
    ]

    invalid_json: list[dict[str, str]] = []
    for path in json_targets:
        try:
            read_json(path)
        except Exception as error:
            invalid_json.append({"path": str(path), "error": str(error)})

    verdict = "PASS" if not missing_files and not invalid_json else "FAIL"
    summary = {
        "checked_at_utc": utc_now(),
        "verdict": verdict,
        "missing_files": missing_files,
        "invalid_json": invalid_json,
        "required_files_count": len(required_files),
        "json_targets_count": len(json_targets),
    }

    out_dir = ctx.run_root / "check_all"
    report_json = out_dir / "check_all_report.json"
    report_md = out_dir / "CHECK_ALL.md"
    write_json(report_json, summary)
    write_text(
        report_md,
        "\n".join(
            [
                "# Check All",
                "",
                f"- verdict: `{verdict}`",
                f"- missing_files: `{len(missing_files)}`",
                f"- invalid_json: `{len(invalid_json)}`",
            ]
        )
        + "\n",
    )

    receipt = emit_receipt(
        ctx,
        "check_all_receipt.json",
        {
            "command": "check-all",
            "timestamp_utc": utc_now(),
            "verdict": verdict,
            "outputs": [str(report_json), str(report_md)],
        },
    )
    print_artifacts(
        {
            "CHECK_ALL_JSON": report_json,
            "CHECK_ALL_MD": report_md,
            "RECEIPT": receipt,
        }
    )
    return 0 if verdict == "PASS" else 1


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Officio Agent Runner V0.1")
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
    compliance.add_argument("--matrix", required=True)
    compliance.add_argument("--evidence", required=False, default=None)

    sub.add_parser("check-all")
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
    parser.print_help()
    return 2


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
