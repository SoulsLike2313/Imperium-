from __future__ import annotations

import json
import shutil
import subprocess
from dataclasses import dataclass
from pathlib import Path


@dataclass
class GitCliCheckPaths:
    repo_root: Path
    wrapper_path: Path
    runtime_dir: Path
    result_path: Path
    verdict_path: Path
    receipt_path: Path


class GitCliCheckServiceError(RuntimeError):
    pass


class GitCliCheckService:
    def __init__(self, repo_root: Path):
        self.repo_root = Path(repo_root)
        runtime_dir = self.repo_root / ".imperium_runtime" / "administratum" / "git_cli_check"
        self.paths = GitCliCheckPaths(
            repo_root=self.repo_root,
            wrapper_path=self.repo_root / "TOOLS" / "RUN_ADMINISTRATUM_GIT_CLI_CHECK.ps1",
            runtime_dir=runtime_dir,
            result_path=runtime_dir / "GIT_CLI_CHECK_RESULT.json",
            verdict_path=runtime_dir / "GIT_CLI_CHECK_VERDICT.md",
            receipt_path=runtime_dir / "GIT_CLI_CHECK_RECEIPT.json",
        )

    def _resolve_powershell(self) -> str:
        command = shutil.which("powershell")
        if not command:
            raise GitCliCheckServiceError("PowerShell executable not found in PATH.")
        return command

    def run_wrapper(self, timeout_sec: int = 300) -> subprocess.CompletedProcess:
        if not self.paths.wrapper_path.exists():
            raise FileNotFoundError(f"Wrapper not found: {self.paths.wrapper_path}")

        powershell = self._resolve_powershell()
        args = [
            powershell,
            "-ExecutionPolicy",
            "Bypass",
            "-NoProfile",
            "-File",
            str(self.paths.wrapper_path),
        ]

        try:
            return subprocess.run(
                args,
                cwd=str(self.paths.repo_root),
                capture_output=True,
                text=True,
                timeout=timeout_sec,
                check=False,
            )
        except subprocess.TimeoutExpired as exc:
            raise GitCliCheckServiceError(
                f"Checker command timed out after {timeout_sec}s."
            ) from exc

    def load_result_json(self) -> dict:
        if not self.paths.result_path.exists():
            raise FileNotFoundError(f"Result JSON missing: {self.paths.result_path}")
        try:
            return json.loads(self.paths.result_path.read_text(encoding="utf-8-sig"))
        except json.JSONDecodeError as exc:
            raise ValueError(f"Result JSON parse failed: {self.paths.result_path}") from exc

    def load_verdict_md(self) -> str:
        if not self.paths.verdict_path.exists():
            raise FileNotFoundError(f"Verdict file missing: {self.paths.verdict_path}")
        return self.paths.verdict_path.read_text(encoding="utf-8-sig")

    def summarize(self, payload: dict) -> dict:
        return {
            "verdict": str(payload.get("verdict", "UNKNOWN")),
            "local_head": str(payload.get("local_head", "")),
            "origin_master_head": str(payload.get("origin_master_head", "")),
            "ls_remote_master_head": str(payload.get("ls_remote_master_head", "")),
            "commit_count": payload.get("commit_count"),
            "latest_commit_oneline": str(payload.get("latest_commit_oneline", "")),
            "worktree_clean": payload.get("worktree_clean"),
            "runtime_dir": str(self.paths.runtime_dir),
            "result_path": str(self.paths.result_path),
            "verdict_path": str(self.paths.verdict_path),
            "receipt_path": str(self.paths.receipt_path),
        }

    def format_summary_text(self, summary: dict) -> str:
        lines = [
            f"verdict: {summary.get('verdict', 'UNKNOWN')}",
            f"local_head: {summary.get('local_head', '')}",
            f"origin_master_head: {summary.get('origin_master_head', '')}",
            f"ls_remote_master_head: {summary.get('ls_remote_master_head', '')}",
            f"commit_count: {summary.get('commit_count')}",
            f"latest_commit_oneline: {summary.get('latest_commit_oneline', '')}",
            f"worktree_clean: {summary.get('worktree_clean')}",
            "",
            f"runtime_dir: {summary.get('runtime_dir', '')}",
            f"result_path: {summary.get('result_path', '')}",
            f"verdict_path: {summary.get('verdict_path', '')}",
            f"receipt_path: {summary.get('receipt_path', '')}",
        ]
        return "\n".join(lines)
