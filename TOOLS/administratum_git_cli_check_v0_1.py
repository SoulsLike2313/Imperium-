#!/usr/bin/env python3
from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import platform
import shlex
import subprocess
import sys
import time
from pathlib import Path
from typing import Dict, List, Optional


DEFAULT_TASK_ID = "ADMINISTRATUM-GIT-CLI-CHECK-V0_1"
RUNTIME_RELATIVE_DIR = Path(".imperium_runtime/administratum/git_cli_check")
RESULT_FILENAME = "GIT_CLI_CHECK_RESULT.json"
VERDICT_FILENAME = "GIT_CLI_CHECK_VERDICT.md"
RECEIPT_FILENAME = "GIT_CLI_CHECK_RECEIPT.json"


def now_utc_iso() -> str:
    return dt.datetime.now(dt.timezone.utc).isoformat()


def command_to_string(args: List[str]) -> str:
    try:
        return shlex.join(args)
    except AttributeError:
        return " ".join(args)


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(65536), b""):
            digest.update(chunk)
    return digest.hexdigest()


def run_cmd(args: List[str], cwd: Path, timeout_sec: int) -> Dict[str, object]:
    started = time.time()
    command_str = command_to_string(args)
    try:
        proc = subprocess.run(
            args,
            cwd=str(cwd),
            capture_output=True,
            text=True,
            timeout=timeout_sec,
            check=False,
        )
        return {
            "command": command_str,
            "args": args,
            "exit_code": int(proc.returncode),
            "stdout": proc.stdout,
            "stderr": proc.stderr,
            "timed_out": False,
            "duration_ms": int((time.time() - started) * 1000),
            "exception": "",
        }
    except subprocess.TimeoutExpired as exc:
        stdout = exc.stdout if isinstance(exc.stdout, str) else (exc.stdout.decode("utf-8", errors="replace") if exc.stdout else "")
        stderr = exc.stderr if isinstance(exc.stderr, str) else (exc.stderr.decode("utf-8", errors="replace") if exc.stderr else "")
        return {
            "command": command_str,
            "args": args,
            "exit_code": -124,
            "stdout": stdout,
            "stderr": stderr,
            "timed_out": True,
            "duration_ms": int((time.time() - started) * 1000),
            "exception": "TIMEOUT",
        }
    except Exception as exc:  # pragma: no cover - defensive guard
        return {
            "command": command_str,
            "args": args,
            "exit_code": -1,
            "stdout": "",
            "stderr": "",
            "timed_out": False,
            "duration_ms": int((time.time() - started) * 1000),
            "exception": f"{type(exc).__name__}: {exc}",
        }


def try_git_toplevel(from_dir: Path, timeout_sec: int = 15) -> Optional[Path]:
    if not from_dir.exists():
        return None
    working = from_dir if from_dir.is_dir() else from_dir.parent
    result = run_cmd(["git", "rev-parse", "--show-toplevel"], cwd=working, timeout_sec=timeout_sec)
    if int(result["exit_code"]) != 0:
        return None
    top = str(result["stdout"]).strip()
    if not top:
        return None
    return Path(top).resolve()


def detect_repo_root(explicit_root: str, timeout_sec: int) -> Optional[Path]:
    if explicit_root:
        return try_git_toplevel(Path(explicit_root).resolve(), timeout_sec=timeout_sec)

    candidates: List[Path] = []
    cwd = Path.cwd().resolve()
    script_dir = Path(__file__).resolve().parent
    candidates.extend([cwd, script_dir, script_dir.parent])
    candidates.extend(cwd.parents)
    candidates.extend(script_dir.parents)

    seen = set()
    unique_candidates: List[Path] = []
    for c in candidates:
        key = str(c)
        if key not in seen:
            seen.add(key)
            unique_candidates.append(c)

    for c in unique_candidates:
        top = try_git_toplevel(c, timeout_sec=timeout_sec)
        if top:
            return top
    return None


def parse_origin_url(remote_v_output: str) -> str:
    lines = [line.strip() for line in remote_v_output.splitlines() if line.strip()]
    for line in lines:
        parts = line.split()
        if len(parts) >= 3 and parts[0] == "origin" and parts[2] == "(fetch)":
            return parts[1]
    for line in lines:
        parts = line.split()
        if len(parts) >= 2 and parts[0] == "origin":
            return parts[1]
    return ""


def normalize_remote_url(remote_url: str) -> str:
    value = remote_url.strip()
    if value.endswith(".git"):
        value = value[:-4]
    if value.startswith("git@github.com:"):
        value = "https://github.com/" + value[len("git@github.com:") :]
    return value


def build_tree_url(remote_url: str, head_sha: str) -> str:
    if not remote_url or not head_sha:
        return ""
    return f"{normalize_remote_url(remote_url)}/tree/{head_sha}"


def first_line(text: str) -> str:
    lines = [x.strip() for x in text.splitlines() if x.strip()]
    return lines[0] if lines else ""


def parse_ls_remote_head(ls_remote_output: str) -> str:
    line = first_line(ls_remote_output)
    if not line:
        return ""
    return line.split()[0]


def build_verdict(
    command_results: Dict[str, Dict[str, object]],
    local_head: str,
    origin_master_head: str,
    ls_remote_master_head: str,
    worktree_status_short: List[str],
    expected_head: str,
    expected_commit_count: Optional[int],
    commit_count: Optional[int],
) -> Dict[str, object]:
    warnings: List[str] = []
    errors: List[str] = []

    critical_commands = {
        "git fetch origin",
        "git rev-parse HEAD",
        "git rev-parse origin/master",
        "git ls-remote origin refs/heads/master",
        "git status --short",
    }
    noncritical_commands = {
        "git remote -v",
        "git rev-list --count HEAD",
        "git log -1 --oneline",
        "git log --oneline -5",
    }

    for cmd in critical_commands:
        result = command_results.get(cmd)
        if result is None:
            errors.append(f"Missing required command result: {cmd}")
            continue
        if int(result.get("exit_code", -1)) != 0:
            errors.append(f"Critical command failed: {cmd} (exit={result.get('exit_code')})")
        if bool(result.get("timed_out", False)):
            errors.append(f"Critical command timed out: {cmd}")
        if str(result.get("exception", "")):
            errors.append(f"Critical command exception: {cmd} -> {result.get('exception')}")

    for cmd in noncritical_commands:
        result = command_results.get(cmd)
        if result is None:
            warnings.append(f"Non-critical command missing from results: {cmd}")
            continue
        if bool(result.get("timed_out", False)):
            warnings.append(f"Non-critical command timed out: {cmd}")
        if int(result.get("exit_code", 0)) != 0:
            warnings.append(f"Non-critical command failed: {cmd} (exit={result.get('exit_code')})")
        stderr = str(result.get("stderr", "")).strip()
        if stderr:
            warnings.append(f"Non-critical command produced stderr: {cmd}: {stderr}")

    head_matches_origin = bool(local_head and origin_master_head and local_head == origin_master_head)
    head_matches_ls_remote = bool(local_head and ls_remote_master_head and local_head == ls_remote_master_head)
    origin_matches_ls_remote = bool(origin_master_head and ls_remote_master_head and origin_master_head == ls_remote_master_head)

    if not head_matches_origin:
        errors.append("HEAD does not match origin/master.")
    if not head_matches_ls_remote:
        errors.append("HEAD does not match ls-remote master head.")
    if not origin_matches_ls_remote:
        errors.append("origin/master does not match ls-remote master head.")

    clean_worktree = len(worktree_status_short) == 0
    if not clean_worktree and not errors:
        warnings.append("Worktree is dirty (git status --short is non-empty).")

    if expected_head:
        if local_head and local_head != expected_head:
            warnings.append(f"Expected HEAD mismatch: expected={expected_head}, actual={local_head}")

    if expected_commit_count is not None and commit_count is not None and expected_commit_count != commit_count:
        warnings.append(f"Commit count differs from expected: expected={expected_commit_count}, actual={commit_count}")

    if errors:
        verdict = "FAIL"
    elif warnings:
        verdict = "PASS_WITH_WARNINGS"
    else:
        verdict = "PASS"

    return {
        "verdict": verdict,
        "warnings": warnings,
        "errors": errors,
        "head_matches_origin": head_matches_origin,
        "head_matches_ls_remote": head_matches_ls_remote,
        "origin_matches_ls_remote": origin_matches_ls_remote,
        "worktree_clean": clean_worktree,
    }


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def write_json(path: Path, payload: Dict[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Administratum Git CLI checker v0.1")
    parser.add_argument("--task-id", default=DEFAULT_TASK_ID)
    parser.add_argument("--repo-root", default="")
    parser.add_argument("--expected-head", default="")
    parser.add_argument("--expected-commit-count", type=int, default=None)
    parser.add_argument("--timeout-sec", type=int, default=60)
    args = parser.parse_args()

    started_at = now_utc_iso()
    repo_root = detect_repo_root(args.repo_root, timeout_sec=max(5, args.timeout_sec))
    if repo_root is None:
        fallback_root = Path(__file__).resolve().parent.parent
        runtime_dir = fallback_root / RUNTIME_RELATIVE_DIR
        runtime_dir.mkdir(parents=True, exist_ok=True)
        result_path = runtime_dir / RESULT_FILENAME
        verdict_path = runtime_dir / VERDICT_FILENAME
        receipt_path = runtime_dir / RECEIPT_FILENAME

        fail_payload = {
            "task_id": args.task_id,
            "timestamp_utc": started_at,
            "repo_root": "",
            "platform": platform.platform(),
            "python_version": sys.version,
            "remote_url": "",
            "local_head": "",
            "origin_master_head": "",
            "ls_remote_master_head": "",
            "commit_count": None,
            "latest_commit_oneline": "",
            "last_5_commits": [],
            "worktree_status_short": [],
            "commands_run": [],
            "command_exit_codes": {},
            "command_stdout": {},
            "command_stderr": {},
            "verdict": "FAIL",
            "warnings": [],
            "errors": ["Repo root could not be found safely via Git CLI."],
        }
        write_json(result_path, fail_payload)
        write_text(
            verdict_path,
            "# GIT CLI CHECK VERDICT\n\n- verdict: FAIL\n- reason: Repo root could not be found safely via Git CLI.\n",
        )
        receipt = {
            "schema_version": "ADMINISTRATUM_GIT_CLI_CHECK_RECEIPT_V0_1",
            "task_id": args.task_id,
            "timestamp_utc": now_utc_iso(),
            "result_path": str(result_path),
            "verdict_path": str(verdict_path),
            "receipt_path": str(receipt_path),
            "result_sha256": sha256_file(result_path),
            "verdict_sha256": sha256_file(verdict_path),
            "verdict": "FAIL",
        }
        write_json(receipt_path, receipt)
        print(str(result_path))
        print(str(verdict_path))
        print(str(receipt_path))
        return 1

    runtime_dir = repo_root / RUNTIME_RELATIVE_DIR
    runtime_dir.mkdir(parents=True, exist_ok=True)
    result_path = runtime_dir / RESULT_FILENAME
    verdict_path = runtime_dir / VERDICT_FILENAME
    receipt_path = runtime_dir / RECEIPT_FILENAME

    commands = [
        ["git", "remote", "-v"],
        ["git", "fetch", "origin"],
        ["git", "rev-parse", "HEAD"],
        ["git", "rev-parse", "origin/master"],
        ["git", "ls-remote", "origin", "refs/heads/master"],
        ["git", "status", "--short"],
        ["git", "rev-list", "--count", "HEAD"],
        ["git", "log", "-1", "--oneline"],
        ["git", "log", "--oneline", "-5"],
    ]

    command_results: Dict[str, Dict[str, object]] = {}
    commands_run: List[str] = []
    for cmd in commands:
        cmd_str = command_to_string(cmd)
        commands_run.append(cmd_str)
        command_results[cmd_str] = run_cmd(cmd, cwd=repo_root, timeout_sec=max(5, args.timeout_sec))

    remote_url = parse_origin_url(str(command_results["git remote -v"]["stdout"]))
    local_head = first_line(str(command_results["git rev-parse HEAD"]["stdout"]))
    origin_master_head = first_line(str(command_results["git rev-parse origin/master"]["stdout"]))
    ls_remote_master_head = parse_ls_remote_head(str(command_results["git ls-remote origin refs/heads/master"]["stdout"]))
    status_lines = [line for line in str(command_results["git status --short"]["stdout"]).splitlines() if line.strip()]
    commit_count_text = first_line(str(command_results["git rev-list --count HEAD"]["stdout"]))
    commit_count = int(commit_count_text) if commit_count_text.isdigit() else None
    latest_commit_oneline = first_line(str(command_results["git log -1 --oneline"]["stdout"]))
    last_5_commits = [line.strip() for line in str(command_results["git log --oneline -5"]["stdout"]).splitlines() if line.strip()]

    verdict_info = build_verdict(
        command_results=command_results,
        local_head=local_head,
        origin_master_head=origin_master_head,
        ls_remote_master_head=ls_remote_master_head,
        worktree_status_short=status_lines,
        expected_head=args.expected_head.strip(),
        expected_commit_count=args.expected_commit_count,
        commit_count=commit_count,
    )

    command_exit_codes = {k: int(v.get("exit_code", -1)) for k, v in command_results.items()}
    command_stdout = {k: str(v.get("stdout", "")) for k, v in command_results.items()}
    command_stderr = {k: str(v.get("stderr", "")) for k, v in command_results.items()}

    tree_url = build_tree_url(remote_url, local_head)

    result = {
        "task_id": args.task_id,
        "timestamp_utc": now_utc_iso(),
        "repo_root": str(repo_root),
        "platform": platform.platform(),
        "python_version": sys.version,
        "remote_url": remote_url,
        "tree_url": tree_url,
        "local_head": local_head,
        "origin_master_head": origin_master_head,
        "ls_remote_master_head": ls_remote_master_head,
        "commit_count": commit_count,
        "latest_commit_oneline": latest_commit_oneline,
        "last_5_commits": last_5_commits,
        "worktree_status_short": status_lines,
        "commands_run": commands_run,
        "command_exit_codes": command_exit_codes,
        "command_stdout": command_stdout,
        "command_stderr": command_stderr,
        "verdict": verdict_info["verdict"],
        "warnings": verdict_info["warnings"],
        "errors": verdict_info["errors"],
        "expected_head": args.expected_head.strip(),
        "expected_commit_count": args.expected_commit_count,
        "head_matches_origin": verdict_info["head_matches_origin"],
        "head_matches_ls_remote": verdict_info["head_matches_ls_remote"],
        "origin_matches_ls_remote": verdict_info["origin_matches_ls_remote"],
        "worktree_clean": verdict_info["worktree_clean"],
    }
    write_json(result_path, result)

    verdict_lines = [
        "# GIT CLI CHECK VERDICT",
        "",
        f"- task_id: {args.task_id}",
        f"- timestamp_utc: {result['timestamp_utc']}",
        f"- repo_root: {repo_root}",
        f"- verdict: {result['verdict']}",
        f"- remote_url: {remote_url}",
        f"- tree_url: {tree_url}",
        f"- local_head: {local_head}",
        f"- origin_master_head: {origin_master_head}",
        f"- ls_remote_master_head: {ls_remote_master_head}",
        f"- commit_count: {commit_count if commit_count is not None else 'UNAVAILABLE'}",
        f"- latest_commit_oneline: {latest_commit_oneline}",
        f"- worktree_clean: {result['worktree_clean']}",
    ]
    if result["warnings"]:
        verdict_lines.append("")
        verdict_lines.append("## Warnings")
        for warning in result["warnings"]:
            verdict_lines.append(f"- {warning}")
    if result["errors"]:
        verdict_lines.append("")
        verdict_lines.append("## Errors")
        for error in result["errors"]:
            verdict_lines.append(f"- {error}")
    write_text(verdict_path, "\n".join(verdict_lines) + "\n")

    receipt = {
        "schema_version": "ADMINISTRATUM_GIT_CLI_CHECK_RECEIPT_V0_1",
        "task_id": args.task_id,
        "timestamp_utc": now_utc_iso(),
        "repo_root": str(repo_root),
        "result_path": str(result_path),
        "verdict_path": str(verdict_path),
        "receipt_path": str(receipt_path),
        "result_sha256": sha256_file(result_path),
        "verdict_sha256": sha256_file(verdict_path),
        "verdict": result["verdict"],
        "duration_note": "Command durations are recorded per command in RESULT.json.",
    }
    write_json(receipt_path, receipt)

    print(str(result_path))
    print(str(verdict_path))
    print(str(receipt_path))
    return 1 if result["verdict"] == "FAIL" else 0


if __name__ == "__main__":
    raise SystemExit(main())
