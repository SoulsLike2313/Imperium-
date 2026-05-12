#!/usr/bin/env python3
"""Administratum Git Sync Console v0.1 standalone utility."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
import json
from pathlib import Path
import platform
import re
import shlex
import sys
from typing import Any, Callable

try:
    from PySide6.QtCore import Qt, QThread, Signal
    from PySide6.QtGui import QColor, QFont
    from PySide6.QtWidgets import (
        QApplication,
        QComboBox,
        QFrame,
        QGroupBox,
        QHBoxLayout,
        QInputDialog,
        QLabel,
        QListWidget,
        QListWidgetItem,
        QMainWindow,
        QMessageBox,
        QPlainTextEdit,
        QPushButton,
        QSplitter,
        QVBoxLayout,
        QWidget,
    )

    PYSIDE6_AVAILABLE = True
    PYSIDE6_IMPORT_ERROR = ""
except Exception as exc:  # pragma: no cover - runtime availability guard
    PYSIDE6_AVAILABLE = False
    PYSIDE6_IMPORT_ERROR = str(exc)


APP_TITLE = "Administratum Git Sync Console v0.1"
TASK_ID_DEFAULT = "TASK-20260512-ADMINISTRATUM-GIT-SYNC-CONSOLE-V0_1"
STEP_NAME_DEFAULT = "VM2-BUILD-ADMINISTRATUM-GIT-SYNC-CONSOLE-V0_1"
RUNTIME_SUBDIR = Path(".imperium_runtime/administratum/git_sync_console")

NOISE_PREFIXES = (
    ".imperium_runtime/",
    "ORGANS/ADMINISTRATUM/CONTINUITY/PACKS/",
    "__pycache__/",
    ".pytest_cache/",
)
NOISE_CONTAINS = (
    "/__pycache__/",
    "/.pytest_cache/",
)
NOISE_SUFFIXES = (
    ".zip",
    ".pyc",
)

REDACT_PATTERNS = [
    re.compile(r"\b(ghp_[A-Za-z0-9_\-]{20,})\b"),
    re.compile(r"\b(glpat-[A-Za-z0-9_\-]{20,})\b"),
    re.compile(r"\b(AKIA[0-9A-Z]{16})\b"),
    re.compile(r"(?i)(password|token|secret|apikey|api_key)\s*[:=]\s*\S+"),
    re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----"),
]


# =============================================================================
# DATA CLASSES
# =============================================================================


@dataclass
class CommandResult:
    command_id: str
    argv: list[str]
    exit_code: int | None
    stdout: str
    stderr: str
    timed_out: bool = False
    timestamp_utc: str = ""

    def __post_init__(self) -> None:
        if not self.timestamp_utc:
            self.timestamp_utc = utc_now()

    @property
    def ok(self) -> bool:
        return self.exit_code == 0 and not self.timed_out


@dataclass
class FileEntry:
    path: str
    xy: str
    index_status: str
    worktree_status: str
    likely_runtime_noise: bool

    @property
    def is_untracked(self) -> bool:
        return self.xy == "??"

    @property
    def is_staged(self) -> bool:
        return self.index_status not in (" ", "?")

    @property
    def is_unstaged(self) -> bool:
        return self.worktree_status not in (" ", "?")

    @property
    def marker(self) -> str:
        markers: list[str] = []
        if self.is_staged:
            markers.append("staged")
        if self.is_unstaged:
            markers.append("unstaged")
        if self.is_untracked:
            markers.append("untracked")
        if self.likely_runtime_noise:
            markers.append("runtime/noise")
        if not markers:
            markers.append("clean?")
        return ",".join(markers)

    @property
    def display(self) -> str:
        return f"[{self.xy}] [{self.marker}] {self.path}"


@dataclass
class VerificationState:
    checks_run: int = 0
    last_run_timestamp_utc: str = ""
    results: list[dict[str, Any]] = field(default_factory=list)

    def add_result(self, command_id: str, verdict: str, exit_code: int | None) -> None:
        self.checks_run += 1
        self.last_run_timestamp_utc = utc_now()
        self.results.append(
            {
                "timestamp_utc": self.last_run_timestamp_utc,
                "command_id": command_id,
                "verdict": verdict,
                "exit_code": exit_code,
            }
        )

    def has_any_results(self) -> bool:
        return self.checks_run > 0

    def has_failures(self) -> bool:
        for item in self.results:
            if item.get("verdict") in {"FAIL", "BLOCKED", "UNKNOWN"}:
                return True
        return False

    def has_warnings(self) -> bool:
        for item in self.results:
            if item.get("verdict") == "PASS_WITH_WARNINGS":
                return True
        return False

    def has_non_pass(self) -> bool:
        return self.has_failures() or self.has_warnings()


@dataclass
class SessionState:
    task_id: str = TASK_ID_DEFAULT
    step_name: str = STEP_NAME_DEFAULT
    repo_root: str = ""
    branch: str = ""
    local_head: str = ""
    upstream_head: str = "n/a"
    worktree_clean: bool = False
    changed_files: list[str] = field(default_factory=list)
    staged_files: list[str] = field(default_factory=list)
    verification_state: VerificationState = field(default_factory=VerificationState)
    commands_run: list[dict[str, Any]] = field(default_factory=list)
    last_commit_hash: str = ""
    commit_done_this_session: bool = False
    pushed: bool = False
    started_utc: str = field(default_factory=lambda: utc_now())


# =============================================================================
# HELPERS
# =============================================================================


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def redact_text(text: str) -> str:
    result = text
    for pattern in REDACT_PATTERNS:
        result = pattern.sub("[REDACTED]", result)
    return result


def tail_text(text: str, max_chars: int = 4000) -> str:
    if len(text) <= max_chars:
        return text
    return "...[truncated]...\n" + text[-max_chars:]


def safe_argv_repr(argv: list[str]) -> str:
    try:
        return shlex.join([redact_text(part) for part in argv])
    except Exception:
        return " ".join(redact_text(part) for part in argv)


def normalize_rel_path(path: str) -> str:
    return path.replace("\\", "/")


def is_likely_runtime_noise(path: str) -> bool:
    normalized = normalize_rel_path(path)
    for prefix in NOISE_PREFIXES:
        if normalized.startswith(prefix):
            return True
    for chunk in NOISE_CONTAINS:
        if chunk in normalized:
            return True
    for suffix in NOISE_SUFFIXES:
        if normalized.endswith(suffix):
            return True
    return False


def parse_markdown_verdict(md_path: Path, key: str) -> str | None:
    if not md_path.exists():
        return None
    try:
        text = md_path.read_text(encoding="utf-8", errors="replace")
    except Exception:
        return None
    pattern = re.compile(rf"^\s*[-*]\s*{re.escape(key)}\s*:\s*(\S+)\s*$", re.MULTILINE)
    match = pattern.search(text)
    if not match:
        return None
    return match.group(1).strip()


# =============================================================================
# REPO ROOT DETECTOR
# =============================================================================


class RepoRootDetector:
    """Detect and validate repository root by `.git` presence."""

    @staticmethod
    def detect(start_path: Path | None = None) -> Path | None:
        current = (start_path or Path.cwd()).resolve()
        if current.is_file():
            current = current.parent
        for candidate in [current, *current.parents]:
            if (candidate / ".git").exists():
                return candidate
        return None

    @staticmethod
    def validate(path: Path) -> bool:
        return (path / ".git").exists()


# =============================================================================
# GIT COMMAND RUNNER (ONLY SUBPROCESS LAYER)
# =============================================================================


class GitCommandRunner:
    """Temporary subprocess adapter. No `shell=True`, only argv lists."""

    import subprocess as _subprocess

    def __init__(self, repo_root: Path, timeout_sec: int = 120):
        self.repo_root = repo_root.resolve()
        self.timeout_sec = timeout_sec
        if not RepoRootDetector.validate(self.repo_root):
            raise ValueError(f"Invalid repo root: {self.repo_root}")

    def is_inside_repo(self, repo_relative_path: str) -> bool:
        try:
            candidate = (self.repo_root / repo_relative_path).resolve()
            candidate.relative_to(self.repo_root)
            return True
        except Exception:
            return False

    def validate_paths(self, paths: list[str]) -> tuple[list[str], list[str]]:
        safe: list[str] = []
        rejected: list[str] = []
        for raw in paths:
            rel = normalize_rel_path(raw).strip()
            if not rel:
                continue
            if self.is_inside_repo(rel):
                safe.append(rel)
            else:
                rejected.append(raw)
        return safe, rejected

    def run(self, argv: list[str], command_id: str, timeout_sec: int | None = None) -> CommandResult:
        effective_timeout = timeout_sec or self.timeout_sec
        try:
            proc = self._subprocess.run(
                argv,
                cwd=str(self.repo_root),
                capture_output=True,
                text=True,
                shell=False,
                timeout=effective_timeout,
                check=False,
            )
            return CommandResult(
                command_id=command_id,
                argv=argv,
                exit_code=proc.returncode,
                stdout=proc.stdout,
                stderr=proc.stderr,
            )
        except self._subprocess.TimeoutExpired as exc:
            stdout = exc.stdout if isinstance(exc.stdout, str) else ""
            stderr = exc.stderr if isinstance(exc.stderr, str) else ""
            return CommandResult(
                command_id=command_id,
                argv=argv,
                exit_code=None,
                stdout=stdout,
                stderr=stderr or f"Command timed out after {effective_timeout}s",
                timed_out=True,
            )
        except FileNotFoundError as exc:
            return CommandResult(
                command_id=command_id,
                argv=argv,
                exit_code=None,
                stdout="",
                stderr=f"Executable not found: {exc}",
            )
        except Exception as exc:
            return CommandResult(
                command_id=command_id,
                argv=argv,
                exit_code=None,
                stdout="",
                stderr=f"Execution error: {exc}",
            )

    def run_git(self, git_args: list[str], command_id: str, timeout_sec: int | None = None) -> CommandResult:
        return self.run(["git", *git_args], command_id=command_id, timeout_sec=timeout_sec)


# =============================================================================
# STATUS / DIFF / STAGE SERVICES
# =============================================================================


class GitStatusService:
    def __init__(self, runner: GitCommandRunner):
        self.runner = runner

    def get_file_entries(self) -> tuple[list[FileEntry], CommandResult]:
        result = self.runner.run_git(
            ["status", "--porcelain=v1"],
            command_id="git.status_porcelain",
        )
        entries: list[FileEntry] = []
        if not result.ok:
            return entries, result

        for line in result.stdout.splitlines():
            if len(line) < 3:
                continue
            xy = line[:2]
            path = line[3:].strip()
            if " -> " in path:
                path = path.split(" -> ", 1)[1].strip()
            index_status = xy[0]
            worktree_status = xy[1]
            entries.append(
                FileEntry(
                    path=normalize_rel_path(path),
                    xy=xy,
                    index_status=index_status,
                    worktree_status=worktree_status,
                    likely_runtime_noise=is_likely_runtime_noise(path),
                )
            )
        return entries, result

    def get_branch(self) -> str:
        result = self.runner.run_git(["branch", "--show-current"], command_id="git.branch")
        return result.stdout.strip() if result.ok else "unknown"

    def get_local_head_short(self) -> str:
        result = self.runner.run_git(["rev-parse", "--short", "HEAD"], command_id="git.head.short")
        return result.stdout.strip() if result.ok else "unknown"

    def get_local_head_full(self) -> str:
        result = self.runner.run_git(["rev-parse", "HEAD"], command_id="git.head.full")
        return result.stdout.strip() if result.ok else ""

    def get_upstream_head_short(self) -> str:
        result = self.runner.run_git(["rev-parse", "--short", "@{u}"], command_id="git.upstream.short")
        return result.stdout.strip() if result.ok else "n/a"

    def is_worktree_clean(self) -> bool:
        result = self.runner.run_git(["status", "--porcelain=v1"], command_id="git.status.clean")
        return result.ok and result.stdout.strip() == ""

    @staticmethod
    def changed_files(entries: list[FileEntry]) -> list[str]:
        return sorted({entry.path for entry in entries})

    @staticmethod
    def staged_files(entries: list[FileEntry]) -> list[str]:
        return sorted({entry.path for entry in entries if entry.is_staged})


class GitDiffService:
    def __init__(self, runner: GitCommandRunner):
        self.runner = runner

    def get_diff_text(self, path: str, staged: bool) -> str:
        safe, rejected = self.runner.validate_paths([path])
        if not safe:
            return f"Path rejected (outside repo root): {path}\nRejected: {rejected}"
        args = ["diff"]
        if staged:
            args.append("--staged")
        args.extend(["--", safe[0]])
        result = self.runner.run_git(args, command_id="git.diff.path")
        if result.ok:
            return result.stdout or "(no diff output)"
        return f"Error:\n{result.stderr or '(unknown error)'}"

    def get_untracked_preview(self, path: str, max_bytes: int = 131072) -> str:
        safe, _ = self.runner.validate_paths([path])
        if not safe:
            return "(path rejected)"
        target = (self.runner.repo_root / safe[0]).resolve()
        if not target.exists():
            return "(file does not exist)"
        try:
            raw = target.read_bytes()
        except Exception as exc:
            return f"(cannot read file: {exc})"

        if b"\x00" in raw:
            return "(binary file preview is not shown in v0.1)"

        if len(raw) > max_bytes:
            raw = raw[:max_bytes]
            suffix = "\n\n...[truncated by size limit]..."
        else:
            suffix = ""

        try:
            text = raw.decode("utf-8", errors="replace")
        except Exception:
            text = raw.decode(errors="replace")
        return text + suffix


class GitStageService:
    def __init__(self, runner: GitCommandRunner):
        self.runner = runner

    def stage(self, paths: list[str]) -> CommandResult:
        safe, rejected = self.runner.validate_paths(paths)
        if not safe:
            return CommandResult(
                command_id="git.add",
                argv=["git", "add", "--"],
                exit_code=1,
                stdout="",
                stderr=f"No valid paths to stage. rejected={rejected}",
            )
        return self.runner.run_git(["add", "--", *safe], command_id="git.add")

    def unstage(self, paths: list[str]) -> CommandResult:
        safe, rejected = self.runner.validate_paths(paths)
        if not safe:
            return CommandResult(
                command_id="git.restore.staged",
                argv=["git", "restore", "--staged", "--"],
                exit_code=1,
                stdout="",
                stderr=f"No valid paths to unstage. rejected={rejected}",
            )
        return self.runner.run_git(
            ["restore", "--staged", "--", *safe],
            command_id="git.restore.staged",
        )

    def discard(self, entries: list[FileEntry]) -> CommandResult:
        if not entries:
            return CommandResult(
                command_id="git.restore.worktree",
                argv=["git", "restore", "--"],
                exit_code=1,
                stdout="",
                stderr="No files selected.",
            )

        untracked = [entry.path for entry in entries if entry.is_untracked]
        if untracked:
            return CommandResult(
                command_id="git.restore.worktree",
                argv=["git", "restore", "--"],
                exit_code=1,
                stdout="",
                stderr=(
                    "Discard for untracked files is blocked in v0.1. "
                    f"Blocked paths: {', '.join(untracked)}"
                ),
            )

        paths = [entry.path for entry in entries]
        safe, rejected = self.runner.validate_paths(paths)
        if not safe:
            return CommandResult(
                command_id="git.restore.worktree",
                argv=["git", "restore", "--"],
                exit_code=1,
                stdout="",
                stderr=f"No valid paths to discard. rejected={rejected}",
            )

        return self.runner.run_git(["restore", "--", *safe], command_id="git.restore.worktree")

    def commit(self, message: str) -> CommandResult:
        clean_message = message.strip()
        if not clean_message:
            return CommandResult(
                command_id="git.commit",
                argv=["git", "commit", "-m", ""],
                exit_code=1,
                stdout="",
                stderr="Commit message is empty.",
            )
        return self.runner.run_git(["commit", "-m", clean_message], command_id="git.commit")

    def push(self) -> CommandResult:
        return self.runner.run_git(["push"], command_id="git.push")


# =============================================================================
# VERIFICATION SERVICE
# =============================================================================


class VerificationService:
    def __init__(self, runner: GitCommandRunner):
        self.runner = runner

    @staticmethod
    def _python_argv() -> list[str]:
        if platform.system() == "Windows":
            return ["py", "-3"]
        return [sys.executable]

    def run_git_cli_check(self) -> CommandResult:
        if platform.system() == "Windows":
            return self.runner.run(
                [
                    "powershell",
                    "-ExecutionPolicy",
                    "Bypass",
                    "-NoProfile",
                    "-File",
                    "TOOLS/RUN_ADMINISTRATUM_GIT_CLI_CHECK.ps1",
                ],
                command_id="administratum.git_cli_check",
                timeout_sec=300,
            )
        return self.runner.run(
            ["bash", "TOOLS/run_administratum_git_cli_check.sh"],
            command_id="administratum.git_cli_check",
            timeout_sec=300,
        )

    def run_verify_repo(self) -> CommandResult:
        return self.runner.run(
            [*self._python_argv(), "scripts/verify_repo.py"],
            command_id="imperium.verify_repo",
            timeout_sec=300,
        )

    def run_agent_entrypoint_check(self) -> CommandResult:
        script = self.runner.repo_root / "scripts/check_agent_entrypoint.py"
        if not script.exists():
            return CommandResult(
                command_id="imperium.agent_entrypoint_check",
                argv=[*self._python_argv(), "scripts/check_agent_entrypoint.py"],
                exit_code=1,
                stdout="",
                stderr="Script not found: scripts/check_agent_entrypoint.py",
            )
        return self.runner.run(
            [*self._python_argv(), "scripts/check_agent_entrypoint.py"],
            command_id="imperium.agent_entrypoint_check",
            timeout_sec=180,
        )

    def run_pytest_quick(self) -> CommandResult:
        return self.runner.run(
            [*self._python_argv(), "-m", "pytest", "-q", "tests/test_agent_entrypoint_registry.py"],
            command_id="pytest.quick",
            timeout_sec=180,
        )


# =============================================================================
# RECEIPTS
# =============================================================================


class ReceiptWriter:
    def __init__(self, repo_root: Path):
        self.repo_root = repo_root
        self.runtime_dir = repo_root / RUNTIME_SUBDIR
        self.runtime_dir.mkdir(parents=True, exist_ok=True)

    def write_session_state(self, session: SessionState) -> Path:
        path = self.runtime_dir / "SESSION_STATE.json"
        payload = asdict(session)
        payload["timestamp_utc"] = utc_now()
        path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        return path

    def write_action_receipt(
        self,
        *,
        session: SessionState,
        action_id: str,
        result: CommandResult,
        local_head_before: str,
        local_head_after: str,
        commit_hash: str,
        pushed: bool,
        owner_override_used: bool,
        verdict: str,
    ) -> Path:
        stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        file_name = f"ACTION_RECEIPT_{stamp}_{action_id}.json"
        path = self.runtime_dir / file_name

        payload = {
            "schema_version": "imperium.git_sync_console_receipt.v0_1",
            "timestamp_utc": utc_now(),
            "task_id": session.task_id,
            "step_name": session.step_name,
            "repo_root": session.repo_root,
            "branch": session.branch,
            "local_head_before": local_head_before,
            "local_head_after": local_head_after,
            "upstream_head": session.upstream_head,
            "worktree_clean": session.worktree_clean,
            "changed_files": session.changed_files,
            "staged_files": session.staged_files,
            "command_id": result.command_id,
            "action_id": action_id,
            "argv": [redact_text(part) for part in result.argv],
            "safe_argv": safe_argv_repr(result.argv),
            "exit_code": result.exit_code,
            "timed_out": result.timed_out,
            "stdout_tail": redact_text(tail_text(result.stdout)),
            "stderr_tail": redact_text(tail_text(result.stderr)),
            "verification_results": session.verification_state.results,
            "commit_hash": commit_hash,
            "pushed": pushed,
            "owner_override_used": owner_override_used,
            "verdict": verdict,
        }
        path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

        latest = self.runtime_dir / "LAST_ACTION_RECEIPT.json"
        latest.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        return path

    def write_checks_summary_md(self, session: SessionState) -> Path:
        path = self.runtime_dir / "CHECKS_SUMMARY.md"
        lines = [
            "# CHECKS SUMMARY",
            "",
            f"- timestamp_utc: {utc_now()}",
            f"- repo_root: {session.repo_root}",
            f"- branch: {session.branch}",
            f"- local_head: {session.local_head}",
            "",
            "## Results",
        ]
        if not session.verification_state.results:
            lines.append("- no checks executed in this session")
        else:
            for result in session.verification_state.results:
                lines.append(
                    f"- {result.get('command_id')}: {result.get('verdict')} "
                    f"(exit={result.get('exit_code')})"
                )
        path.write_text("\n".join(lines) + "\n", encoding="utf-8")
        return path


# =============================================================================
# UI
# =============================================================================


if PYSIDE6_AVAILABLE:

    class CheckWorker(QThread):
        finished = Signal(str, object)

        def __init__(self, action_id: str, fn: Callable[[], CommandResult]):
            super().__init__()
            self.action_id = action_id
            self.fn = fn

        def run(self) -> None:
            result = self.fn()
            self.finished.emit(self.action_id, result)


    class GitSyncConsoleWindow(QMainWindow):
        def __init__(self, repo_root: Path):
            super().__init__()
            self.repo_root = repo_root.resolve()
            self.setWindowTitle(f"{APP_TITLE} — {self.repo_root}")
            self.resize(1500, 950)

            self.runner = GitCommandRunner(self.repo_root)
            self.status_service = GitStatusService(self.runner)
            self.diff_service = GitDiffService(self.runner)
            self.stage_service = GitStageService(self.runner)
            self.verification_service = VerificationService(self.runner)
            self.receipt_writer = ReceiptWriter(self.repo_root)

            self.session = SessionState(repo_root=str(self.repo_root))
            self.entries: list[FileEntry] = []
            self.workers: list[CheckWorker] = []
            self.check_labels: dict[str, QLabel] = {}
            self._build_ui()
            self.refresh_all()

        def _build_ui(self) -> None:
            root = QWidget()
            self.setCentralWidget(root)
            layout = QVBoxLayout(root)
            layout.setContentsMargins(8, 8, 8, 8)
            layout.setSpacing(8)

            layout.addWidget(self._build_top_bar())

            middle = QSplitter(Qt.Orientation.Horizontal)
            middle.addWidget(self._build_left_panel())
            middle.addWidget(self._build_diff_panel())
            middle.setSizes([520, 920])
            layout.addWidget(middle, stretch=3)

            bottom = QSplitter(Qt.Orientation.Horizontal)
            bottom.addWidget(self._build_checks_panel())
            bottom.addWidget(self._build_commit_panel())
            bottom.setSizes([840, 600])
            layout.addWidget(bottom, stretch=2)

        def _build_top_bar(self) -> QFrame:
            frame = QFrame()
            frame.setFrameShape(QFrame.Shape.StyledPanel)
            h = QHBoxLayout(frame)

            mono = QFont("Monospace")
            mono.setStyleHint(QFont.StyleHint.TypeWriter)

            self.lbl_repo = QLabel("repo: ...")
            self.lbl_branch = QLabel("branch: ...")
            self.lbl_head = QLabel("head: ...")
            self.lbl_upstream = QLabel("upstream: ...")
            self.lbl_clean = QLabel("worktree: ...")

            for lbl in [self.lbl_repo, self.lbl_branch, self.lbl_head, self.lbl_upstream, self.lbl_clean]:
                lbl.setFont(mono)
                h.addWidget(lbl)

            h.addStretch()
            btn_refresh = QPushButton("Refresh")
            btn_refresh.clicked.connect(self.refresh_all)
            h.addWidget(btn_refresh)
            return frame

        def _build_left_panel(self) -> QWidget:
            panel = QWidget()
            v = QVBoxLayout(panel)

            title = QLabel("Changed Files")
            title.setFont(QFont("Sans Serif", 10, QFont.Weight.Bold))
            v.addWidget(title)

            row = QHBoxLayout()
            row.addWidget(QLabel("Filter:"))
            self.filter_combo = QComboBox()
            self.filter_combo.addItems([
                "all",
                "staged",
                "unstaged",
                "untracked",
                "likely runtime/noise",
            ])
            self.filter_combo.currentIndexChanged.connect(self.apply_filter)
            row.addWidget(self.filter_combo)
            row.addStretch()
            v.addLayout(row)

            mono = QFont("Monospace")
            mono.setStyleHint(QFont.StyleHint.TypeWriter)

            self.file_list = QListWidget()
            self.file_list.setSelectionMode(QListWidget.SelectionMode.ExtendedSelection)
            self.file_list.setFont(mono)
            self.file_list.currentItemChanged.connect(self.on_file_selected)
            v.addWidget(self.file_list, stretch=1)

            buttons_row1 = QHBoxLayout()
            btn_stage = QPushButton("Stage selected")
            btn_stage.clicked.connect(self.stage_selected)
            btn_unstage = QPushButton("Unstage selected")
            btn_unstage.clicked.connect(self.unstage_selected)
            buttons_row1.addWidget(btn_stage)
            buttons_row1.addWidget(btn_unstage)
            v.addLayout(buttons_row1)

            buttons_row2 = QHBoxLayout()
            btn_stage_all = QPushButton("Stage all visible")
            btn_stage_all.clicked.connect(self.stage_all_visible)
            btn_discard = QPushButton("Discard selected")
            btn_discard.setStyleSheet("color: #cc3333;")
            btn_discard.clicked.connect(self.discard_selected)
            buttons_row2.addWidget(btn_stage_all)
            buttons_row2.addWidget(btn_discard)
            v.addLayout(buttons_row2)

            self.lbl_files_summary = QLabel("files: 0")
            self.lbl_files_summary.setFont(mono)
            v.addWidget(self.lbl_files_summary)
            return panel

        def _build_diff_panel(self) -> QWidget:
            panel = QWidget()
            v = QVBoxLayout(panel)

            title = QLabel("Diff / Untracked preview")
            title.setFont(QFont("Sans Serif", 10, QFont.Weight.Bold))
            v.addWidget(title)

            mono = QFont("Monospace")
            mono.setStyleHint(QFont.StyleHint.TypeWriter)

            self.diff_view = QPlainTextEdit()
            self.diff_view.setFont(mono)
            self.diff_view.setReadOnly(True)
            self.diff_view.setLineWrapMode(QPlainTextEdit.LineWrapMode.NoWrap)
            v.addWidget(self.diff_view, stretch=1)

            row = QHBoxLayout()
            btn_copy = QPushButton("Copy diff")
            btn_copy.clicked.connect(self.copy_diff)
            row.addWidget(btn_copy)
            row.addStretch()
            v.addLayout(row)
            return panel

        def _build_checks_panel(self) -> QGroupBox:
            group = QGroupBox("Checks")
            v = QVBoxLayout(group)

            checks = [
                ("run_git_cli_check", "Run Git CLI check", self.verification_service.run_git_cli_check),
                ("run_verify_repo", "Run verify_repo.py", self.verification_service.run_verify_repo),
                (
                    "run_agent_entrypoint_check",
                    "Run agent entrypoint check",
                    self.verification_service.run_agent_entrypoint_check,
                ),
                ("run_pytest_quick", "Run pytest quick", self.verification_service.run_pytest_quick),
            ]

            for action_id, label, fn in checks:
                row = QHBoxLayout()
                btn = QPushButton(label)
                btn.clicked.connect(lambda _=False, aid=action_id, call=fn: self.run_check(aid, call))
                verdict_lbl = QLabel("not run")
                verdict_lbl.setFont(QFont("Monospace", 9))
                self.check_labels[action_id] = verdict_lbl
                row.addWidget(btn)
                row.addWidget(verdict_lbl)
                row.addStretch()
                v.addLayout(row)

            mono = QFont("Monospace")
            mono.setStyleHint(QFont.StyleHint.TypeWriter)

            self.check_output = QPlainTextEdit()
            self.check_output.setReadOnly(True)
            self.check_output.setFont(mono)
            self.check_output.setLineWrapMode(QPlainTextEdit.LineWrapMode.NoWrap)
            self.check_output.setMaximumHeight(280)
            v.addWidget(self.check_output)

            self.lbl_checks_summary = QLabel("checks: not run")
            self.lbl_checks_summary.setFont(mono)
            v.addWidget(self.lbl_checks_summary)
            return group

        def _build_commit_panel(self) -> QGroupBox:
            group = QGroupBox("Commit / Push")
            v = QVBoxLayout(group)

            mono = QFont("Monospace")
            mono.setStyleHint(QFont.StyleHint.TypeWriter)

            self.lbl_staged = QLabel("staged: 0")
            self.lbl_staged.setFont(mono)
            v.addWidget(self.lbl_staged)

            v.addWidget(QLabel("Commit message:"))
            self.commit_message = QPlainTextEdit()
            self.commit_message.setMaximumHeight(100)
            self.commit_message.setFont(mono)
            self.commit_message.setPlaceholderText("TASK-YYYYMMDD: short description")
            v.addWidget(self.commit_message)

            row = QHBoxLayout()
            self.btn_commit = QPushButton("Commit staged changes")
            self.btn_commit.clicked.connect(self.commit_staged)
            self.btn_push = QPushButton("Push")
            self.btn_push.setEnabled(False)
            self.btn_push.clicked.connect(self.push_changes)
            row.addWidget(self.btn_commit)
            row.addWidget(self.btn_push)
            row.addStretch()
            v.addLayout(row)

            self.lbl_commit_push_status = QLabel("status: idle")
            self.lbl_commit_push_status.setFont(mono)
            v.addWidget(self.lbl_commit_push_status)
            return group

        # ------------------------------------------------------------------
        # State refresh
        # ------------------------------------------------------------------

        def refresh_all(self) -> None:
            self.session.branch = self.status_service.get_branch()
            self.session.local_head = self.status_service.get_local_head_short()
            self.session.upstream_head = self.status_service.get_upstream_head_short()
            self.session.worktree_clean = self.status_service.is_worktree_clean()

            entries, status_result = self.status_service.get_file_entries()
            self.entries = entries if status_result.ok else []
            self.session.changed_files = self.status_service.changed_files(self.entries)
            self.session.staged_files = self.status_service.staged_files(self.entries)

            self.lbl_repo.setText(f"repo: {self.repo_root}")
            self.lbl_branch.setText(f"branch: {self.session.branch}")
            self.lbl_head.setText(f"head: {self.session.local_head}")
            self.lbl_upstream.setText(f"upstream: {self.session.upstream_head}")

            if self.session.worktree_clean:
                self.lbl_clean.setText("worktree: clean")
                self.lbl_clean.setStyleSheet("color: #1e9f5c;")
            else:
                self.lbl_clean.setText("worktree: dirty")
                self.lbl_clean.setStyleSheet("color: #b57f00;")

            self.apply_filter()
            self.lbl_staged.setText(f"staged: {len(self.session.staged_files)}")
            self.lbl_files_summary.setText(
                f"files: changed={len(self.session.changed_files)} staged={len(self.session.staged_files)}"
            )
            self.update_checks_summary_label()
            self.receipt_writer.write_session_state(self.session)

        def apply_filter(self) -> None:
            selected_filter = self.filter_combo.currentText() if hasattr(self, "filter_combo") else "all"
            self.file_list.clear()
            for entry in self.entries:
                if selected_filter == "all":
                    show = True
                elif selected_filter == "staged":
                    show = entry.is_staged
                elif selected_filter == "unstaged":
                    show = entry.is_unstaged and not entry.is_untracked
                elif selected_filter == "untracked":
                    show = entry.is_untracked
                elif selected_filter == "likely runtime/noise":
                    show = entry.likely_runtime_noise
                else:
                    show = True

                if not show:
                    continue

                item = QListWidgetItem(entry.display)
                item.setData(Qt.ItemDataRole.UserRole, entry.path)
                item.setData(Qt.ItemDataRole.UserRole + 1, entry.is_staged)
                item.setData(Qt.ItemDataRole.UserRole + 2, entry.is_untracked)

                if entry.is_untracked:
                    item.setForeground(QColor("#4e7aa8"))
                elif entry.is_staged:
                    item.setForeground(QColor("#1e9f5c"))
                elif entry.likely_runtime_noise:
                    item.setForeground(QColor("#8a6d3b"))
                else:
                    item.setForeground(QColor("#b57f00"))

                self.file_list.addItem(item)

        # ------------------------------------------------------------------
        # Diff view
        # ------------------------------------------------------------------

        def selected_entries(self) -> list[FileEntry]:
            paths = [
                item.data(Qt.ItemDataRole.UserRole)
                for item in self.file_list.selectedItems()
                if item.data(Qt.ItemDataRole.UserRole)
            ]
            path_set = set(paths)
            return [entry for entry in self.entries if entry.path in path_set]

        def on_file_selected(self, current: QListWidgetItem | None, _previous: QListWidgetItem | None) -> None:
            if current is None:
                self.diff_view.setPlainText("")
                return
            path = str(current.data(Qt.ItemDataRole.UserRole))
            is_staged = bool(current.data(Qt.ItemDataRole.UserRole + 1))
            is_untracked = bool(current.data(Qt.ItemDataRole.UserRole + 2))

            if is_untracked:
                preview = self.diff_service.get_untracked_preview(path)
                text = f"=== UNTRACKED FILE PREVIEW: {path} ===\n\n{preview}"
            else:
                text = self.diff_service.get_diff_text(path=path, staged=is_staged)
            self.diff_view.setPlainText(text)

        def copy_diff(self) -> None:
            QApplication.clipboard().setText(self.diff_view.toPlainText())

        # ------------------------------------------------------------------
        # Stage operations
        # ------------------------------------------------------------------

        def stage_selected(self) -> None:
            entries = self.selected_entries()
            paths = [entry.path for entry in entries]
            if not paths:
                QMessageBox.information(self, APP_TITLE, "No selected files.")
                return
            self._run_mutating_action("stage_selected", self.stage_service.stage(paths), owner_override_used=False)

        def unstage_selected(self) -> None:
            entries = self.selected_entries()
            paths = [entry.path for entry in entries]
            if not paths:
                QMessageBox.information(self, APP_TITLE, "No selected files.")
                return
            self._run_mutating_action("unstage_selected", self.stage_service.unstage(paths), owner_override_used=False)

        def stage_all_visible(self) -> None:
            paths: list[str] = []
            for i in range(self.file_list.count()):
                item = self.file_list.item(i)
                path = item.data(Qt.ItemDataRole.UserRole)
                if path:
                    paths.append(str(path))
            if not paths:
                QMessageBox.information(self, APP_TITLE, "No visible files.")
                return

            answer = QMessageBox.question(
                self,
                "Confirm stage all visible",
                f"Stage all visible files ({len(paths)})?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No,
            )
            if answer != QMessageBox.StandardButton.Yes:
                return
            self._run_mutating_action("stage_all_visible", self.stage_service.stage(paths), owner_override_used=False)

        def discard_selected(self) -> None:
            entries = self.selected_entries()
            if not entries:
                QMessageBox.information(self, APP_TITLE, "No selected files.")
                return

            untracked = [entry.path for entry in entries if entry.is_untracked]
            if untracked:
                QMessageBox.warning(
                    self,
                    "Discard blocked",
                    "Discard for untracked files is blocked in v0.1.\n"
                    + "\n".join(untracked),
                )
                return

            answer = QMessageBox.warning(
                self,
                "Confirm discard",
                "This action is destructive for tracked local changes. Continue?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No,
            )
            if answer != QMessageBox.StandardButton.Yes:
                return

            self._run_mutating_action("discard_selected", self.stage_service.discard(entries), owner_override_used=False)

        # ------------------------------------------------------------------
        # Checks
        # ------------------------------------------------------------------

        def run_check(self, action_id: str, fn: Callable[[], CommandResult]) -> None:
            self.check_output.setPlainText("Running check...")
            worker = CheckWorker(action_id, fn)
            worker.finished.connect(self._on_check_finished)
            self.workers.append(worker)
            worker.start()

        def _on_check_finished(self, action_id: str, result: CommandResult) -> None:
            verdict = self.derive_check_verdict(action_id, result)
            self.session.verification_state.add_result(result.command_id, verdict, result.exit_code)
            self.receipt_writer.write_checks_summary_md(self.session)

            label = self.check_labels.get(action_id)
            if label is not None:
                label.setText(verdict)
                if verdict == "PASS":
                    label.setStyleSheet("color: #1e9f5c;")
                elif verdict == "PASS_WITH_WARNINGS":
                    label.setStyleSheet("color: #b57f00;")
                else:
                    label.setStyleSheet("color: #cc3333;")

            lines = [
                f"action_id: {action_id}",
                f"command_id: {result.command_id}",
                f"verdict: {verdict}",
                f"exit_code: {result.exit_code}",
                f"timed_out: {result.timed_out}",
                f"argv: {safe_argv_repr(result.argv)}",
                "",
                "[stdout tail]",
                tail_text(result.stdout, 7000),
                "",
                "[stderr tail]",
                tail_text(result.stderr, 4000),
            ]
            self.check_output.setPlainText("\n".join(lines))

            head_before = self.session.local_head
            self.refresh_all()
            head_after = self.session.local_head
            self.session.commands_run.append(
                {
                    "timestamp_utc": utc_now(),
                    "action_id": action_id,
                    "command_id": result.command_id,
                    "exit_code": result.exit_code,
                    "verdict": verdict,
                }
            )
            self.receipt_writer.write_action_receipt(
                session=self.session,
                action_id=action_id,
                result=result,
                local_head_before=head_before,
                local_head_after=head_after,
                commit_hash=self.session.last_commit_hash,
                pushed=self.session.pushed,
                owner_override_used=False,
                verdict=verdict,
            )
            self.update_checks_summary_label()
            self.workers = [w for w in self.workers if w.isRunning()]

        def derive_check_verdict(self, action_id: str, result: CommandResult) -> str:
            if result.timed_out:
                return "FAIL"
            if result.exit_code not in (0,):
                return "FAIL"

            if action_id == "run_verify_repo":
                value = parse_markdown_verdict(
                    self.repo_root / ".imperium_runtime/verification_spine/VERIFY_REPO_VERDICT.md",
                    "overall_verdict",
                )
                if value in {"PASS", "PASS_WITH_WARNINGS", "FAIL", "BLOCKED"}:
                    return value
            elif action_id == "run_git_cli_check":
                value = parse_markdown_verdict(
                    self.repo_root / ".imperium_runtime/administratum/git_cli_check/GIT_CLI_CHECK_VERDICT.md",
                    "verdict",
                )
                if value in {"PASS", "PASS_WITH_WARNINGS", "FAIL", "BLOCKED"}:
                    return value
            elif action_id == "run_agent_entrypoint_check":
                value = parse_markdown_verdict(
                    self.repo_root / ".imperium_runtime/agent_entrypoint_check/AGENT_ENTRYPOINT_VERDICT.md",
                    "overall_verdict",
                )
                if value in {"PASS", "PASS_WITH_WARNINGS", "FAIL", "BLOCKED"}:
                    return value

            joined = f"{result.stdout}\n{result.stderr}"
            if "PASS_WITH_WARNINGS" in joined:
                return "PASS_WITH_WARNINGS"
            if "FAIL" in joined or "BLOCKED" in joined:
                return "FAIL"
            return "PASS"

        def update_checks_summary_label(self) -> None:
            vs = self.session.verification_state
            if not vs.has_any_results():
                self.lbl_checks_summary.setText("checks: not run")
            else:
                non_pass = sum(1 for item in vs.results if item.get("verdict") != "PASS")
                self.lbl_checks_summary.setText(
                    f"checks: run={vs.checks_run} non_pass={non_pass} last={vs.last_run_timestamp_utc}"
                )

        # ------------------------------------------------------------------
        # Commit / push
        # ------------------------------------------------------------------

        def commit_staged(self) -> None:
            message = self.commit_message.toPlainText().strip()
            if not message:
                QMessageBox.warning(self, "Commit", "Commit message is empty.")
                return

            if not self.session.staged_files:
                QMessageBox.warning(self, "Commit", "No staged files.")
                return

            override_for_checks = False
            if not self.session.verification_state.has_any_results():
                answer = QMessageBox.warning(
                    self,
                    "Checks not run",
                    "Проверки в этой сессии не запускались.\n"
                    "Commit разрешён только после явного подтверждения Owner. Продолжить?",
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                    QMessageBox.StandardButton.No,
                )
                if answer != QMessageBox.StandardButton.Yes:
                    return
                override_for_checks = True
            elif self.session.verification_state.has_non_pass():
                answer = QMessageBox.warning(
                    self,
                    "Checks are not fully PASS",
                    "Есть FAIL/PASS_WITH_WARNINGS в текущей сессии.\n"
                    "Commit продолжить под ответственность Owner?",
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                    QMessageBox.StandardButton.No,
                )
                if answer != QMessageBox.StandardButton.Yes:
                    return
                override_for_checks = True

            answer = QMessageBox.question(
                self,
                "Confirm commit",
                f"Commit {len(self.session.staged_files)} staged files?\n\nMessage:\n{message}",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No,
            )
            if answer != QMessageBox.StandardButton.Yes:
                return

            head_before = self.status_service.get_local_head_full()
            result = self.stage_service.commit(message)
            self.refresh_all()
            head_after = self.status_service.get_local_head_full()

            verdict = "PASS" if result.ok else "FAIL"
            commit_hash = ""
            if result.ok:
                commit_hash = self.status_service.get_local_head_short()
                self.session.last_commit_hash = commit_hash
                self.session.commit_done_this_session = True
                self.btn_push.setEnabled(True)
                self.lbl_commit_push_status.setText(f"commit: success {commit_hash}")
                self.lbl_commit_push_status.setStyleSheet("color: #1e9f5c;")
            else:
                self.lbl_commit_push_status.setText("commit: failed")
                self.lbl_commit_push_status.setStyleSheet("color: #cc3333;")

            self.session.commands_run.append(
                {
                    "timestamp_utc": utc_now(),
                    "action_id": "commit_staged",
                    "command_id": result.command_id,
                    "exit_code": result.exit_code,
                    "verdict": verdict,
                    "override_for_checks": override_for_checks,
                }
            )
            self.receipt_writer.write_action_receipt(
                session=self.session,
                action_id="commit_staged",
                result=result,
                local_head_before=head_before,
                local_head_after=head_after,
                commit_hash=commit_hash,
                pushed=self.session.pushed,
                owner_override_used=override_for_checks,
                verdict=verdict,
            )
            self.refresh_all()

        def push_changes(self) -> None:
            if not self.session.commit_done_this_session:
                QMessageBox.warning(
                    self,
                    "Push blocked",
                    "Push button is enabled only after successful commit in this session.",
                )
                return

            override_used = False
            override_reason = ""
            if not self.session.verification_state.has_any_results():
                override_reason = "checks_not_run"
            elif self.session.verification_state.has_non_pass():
                override_reason = "checks_not_pass"

            if override_reason:
                ok = self._owner_override_dialog(
                    "Push override required",
                    "Для push нужен явный override Owner.\n"
                    "Введите OWNER_OVERRIDE_PUSH для подтверждения.",
                    "OWNER_OVERRIDE_PUSH",
                )
                if not ok:
                    return
                override_used = True

            answer = QMessageBox.question(
                self,
                "Confirm push",
                f"Push branch '{self.session.branch}' to origin?\n\n"
                f"local head: {self.session.local_head}\n"
                f"last commit: {self.session.last_commit_hash or 'n/a'}",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No,
            )
            if answer != QMessageBox.StandardButton.Yes:
                return

            head_before = self.status_service.get_local_head_full()
            result = self.stage_service.push()
            self.refresh_all()
            head_after = self.status_service.get_local_head_full()
            verdict = "PASS" if result.ok else "FAIL"

            if result.ok:
                self.session.pushed = True
                self.lbl_commit_push_status.setText("push: success")
                self.lbl_commit_push_status.setStyleSheet("color: #1e9f5c;")
                self.btn_push.setEnabled(False)
            else:
                self.lbl_commit_push_status.setText("push: failed")
                self.lbl_commit_push_status.setStyleSheet("color: #cc3333;")

            self.session.commands_run.append(
                {
                    "timestamp_utc": utc_now(),
                    "action_id": "push_origin",
                    "command_id": result.command_id,
                    "exit_code": result.exit_code,
                    "verdict": verdict,
                    "owner_override_used": override_used,
                    "override_reason": override_reason,
                }
            )
            self.receipt_writer.write_action_receipt(
                session=self.session,
                action_id="push_origin",
                result=result,
                local_head_before=head_before,
                local_head_after=head_after,
                commit_hash=self.session.last_commit_hash,
                pushed=self.session.pushed,
                owner_override_used=override_used,
                verdict=verdict,
            )
            self.refresh_all()

        def _owner_override_dialog(self, title: str, prompt: str, required_phrase: str) -> bool:
            typed, ok = QInputDialog.getText(self, title, prompt)
            if not ok:
                return False
            if typed.strip() != required_phrase:
                QMessageBox.warning(self, title, f"Неверная фраза override. Требуется: {required_phrase}")
                return False
            return True

        # ------------------------------------------------------------------
        # Generic action recorder
        # ------------------------------------------------------------------

        def _run_mutating_action(self, action_id: str, result: CommandResult, owner_override_used: bool) -> None:
            head_before = self.session.local_head
            self.refresh_all()
            head_after = self.session.local_head

            verdict = "PASS" if result.ok else "FAIL"
            if result.exit_code == 0 and "PASS_WITH_WARNINGS" in f"{result.stdout}\n{result.stderr}":
                verdict = "PASS_WITH_WARNINGS"

            self.session.commands_run.append(
                {
                    "timestamp_utc": utc_now(),
                    "action_id": action_id,
                    "command_id": result.command_id,
                    "exit_code": result.exit_code,
                    "verdict": verdict,
                }
            )

            self.receipt_writer.write_action_receipt(
                session=self.session,
                action_id=action_id,
                result=result,
                local_head_before=head_before,
                local_head_after=head_after,
                commit_hash=self.session.last_commit_hash,
                pushed=self.session.pushed,
                owner_override_used=owner_override_used,
                verdict=verdict,
            )

            if result.ok:
                self.lbl_commit_push_status.setText(f"{action_id}: ok")
                self.lbl_commit_push_status.setStyleSheet("color: #1e9f5c;")
            else:
                err_preview = tail_text(result.stderr or result.stdout, 240)
                self.lbl_commit_push_status.setText(f"{action_id}: fail - {err_preview}")
                self.lbl_commit_push_status.setStyleSheet("color: #cc3333;")
            self.refresh_all()

        def closeEvent(self, event) -> None:  # noqa: N802
            self.receipt_writer.write_session_state(self.session)
            self.receipt_writer.write_checks_summary_md(self.session)
            event.accept()

else:

    class GitSyncConsoleWindow:  # pragma: no cover - fallback class for missing PySide6
        def __init__(self, _repo_root: Path):
            raise RuntimeError(f"PySide6 is unavailable: {PYSIDE6_IMPORT_ERROR}")


# =============================================================================
# ENTRYPOINT
# =============================================================================


def main() -> int:
    repo_root = RepoRootDetector.detect()
    if repo_root is None:
        print("ERROR: repository root not found (.git missing in parent chain).", file=sys.stderr)
        return 1

    if not PYSIDE6_AVAILABLE:
        print(
            "ERROR: PySide6 is not available. "
            "Install PySide6 to launch GUI. "
            f"Details: {PYSIDE6_IMPORT_ERROR}",
            file=sys.stderr,
        )
        return 2

    app = QApplication(sys.argv)
    window = GitSyncConsoleWindow(repo_root)
    window.show()
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
