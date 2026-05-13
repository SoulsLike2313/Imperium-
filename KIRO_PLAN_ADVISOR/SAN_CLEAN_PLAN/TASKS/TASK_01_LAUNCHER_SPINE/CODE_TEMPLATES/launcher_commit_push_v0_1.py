#!/usr/bin/env python3
"""
IMPERIUM Launcher: Commit Push v0.1

Коммит и push изменений на PC.
ТОЛЬКО PC может делать commit/push — VM2 запрещено.

Usage:
    python3 launcher_commit_push_v0_1.py --task TASK-ID --message "Commit message" [--dry-run] [--verbose]

Author: KIRO Advisory
Date: 2026-05-14
"""

import sys
import re
from pathlib import Path
from typing import Dict, Any, Optional

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

try:
    from TOOLS.imperium_launcher_v0_1 import (
        BaseLauncher, LauncherConfig, detect_platform
    )
except ImportError:
    print("ERROR: Cannot import imperium_launcher_v0_1. Run from repo root.")
    sys.exit(1)


class CommitPushLauncher(BaseLauncher):
    """Лаунчер для commit и push на PC."""
    
    LAUNCHER_ID = "COMMIT_PUSH"
    DESCRIPTION = "Commit and push changes from PC to GitHub"
    
    def __init__(self, config: LauncherConfig, dry_run: bool = False,
                 verbose: bool = False, task_id: Optional[str] = None,
                 message: Optional[str] = None, push: bool = True):
        super().__init__(config, dry_run, verbose)
        self.task_id = task_id
        self.message = message
        self.push = push
        self.receipt.task_id = task_id
    
    def _validate_commit_message(self, message: str) -> bool:
        """Проверить формат commit message."""
        # Должен содержать task ID или быть в формате [CATEGORY] Description
        patterns = [
            r'^TASK-\d{8}-\d{3,4}',  # TASK-20260514-001
            r'^\[[\w-]+\]',          # [CATEGORY]
            r'^(feat|fix|docs|style|refactor|test|chore):'  # Conventional commits
        ]
        return any(re.match(p, message) for p in patterns)
    
    def execute(self, **kwargs) -> Dict[str, Any]:
        """Выполнить commit и push."""
        
        # КРИТИЧЕСКАЯ ПРОВЕРКА: только PC
        platform = detect_platform()
        if platform != "WINDOWS":
            self.receipt.add_step("PLATFORM_BLOCK", "BLOCKED", {
                "reason": "Commit/push is FORBIDDEN on VM2",
                "platform": platform
            })
            return {
                "success": False,
                "error": "BLOCKED: Commit/push is ONLY allowed on PC (Windows). VM2 is forbidden."
            }
        
        self.receipt.add_step("PLATFORM_CHECK", "PASS", {"platform": platform})
        
        repo_root = Path(self.config.pc_repo_root)
        
        # Проверить что мы в правильном репозитории
        git_remote = self.run_command(["git", "remote", "-v"], cwd=repo_root)
        if "IMPERIUM" not in git_remote.stdout.upper():
            self.receipt.add_warning("Remote does not contain 'IMPERIUM'")
        
        self.receipt.add_step("REPO_CHECK", "PASS")
        
        # Получить текущий статус
        git_status = self.get_git_status(repo_root)
        if not git_status:
            return {
                "success": False,
                "error": "No changes to commit (working tree clean)"
            }
        
        self.log(f"Changes to commit:\n{git_status}")
        self.receipt.add_step("STATUS_CHECK", "PASS", {
            "changes": git_status[:500]
        })
        
        # Построить commit message
        if self.message:
            commit_message = self.message
        elif self.task_id:
            commit_message = f"{self.task_id}: Applied bundle changes"
        else:
            return {
                "success": False,
                "error": "Commit message is required (--message or --task)"
            }
        
        # Валидация commit message
        if not self._validate_commit_message(commit_message):
            self.receipt.add_warning(f"Commit message may not follow conventions: {commit_message}")
        
        self.receipt.add_step("MESSAGE_BUILD", "PASS", {
            "message": commit_message
        })
        
        # Git add
        add_result = self.run_command(["git", "add", "-A"], cwd=repo_root)
        if add_result.returncode != 0:
            return {
                "success": False,
                "error": f"git add failed: {add_result.stderr}"
            }
        
        self.receipt.add_step("GIT_ADD", "PASS")
        
        # Git commit
        commit_result = self.run_command(
            ["git", "commit", "-m", commit_message],
            cwd=repo_root
        )
        
        if commit_result.returncode != 0:
            # Проверить если "nothing to commit"
            if "nothing to commit" in commit_result.stdout.lower():
                return {
                    "success": False,
                    "error": "Nothing to commit after git add"
                }
            return {
                "success": False,
                "error": f"git commit failed: {commit_result.stderr}"
            }
        
        self.receipt.add_step("GIT_COMMIT", "PASS", {
            "output": commit_result.stdout[:300]
        })
        
        # Получить новый HEAD
        new_head = self.get_git_head(repo_root)
        self.log(f"New HEAD: {new_head}")
        
        # Git push (если не отключено)
        if self.push:
            push_result = self.run_command(
                ["git", "push", "origin", "master"],
                cwd=repo_root,
                timeout=120
            )
            
            if push_result.returncode != 0:
                self.receipt.add_step("GIT_PUSH", "FAIL", {
                    "stderr": push_result.stderr[:300]
                })
                return {
                    "success": False,
                    "error": f"git push failed: {push_result.stderr}"
                }
            
            self.receipt.add_step("GIT_PUSH", "PASS")
        else:
            self.receipt.add_step("GIT_PUSH", "SKIPPED", {
                "reason": "--no-push flag"
            })
        
        # Получить commit count
        count_result = self.run_command(
            ["git", "rev-list", "--count", "HEAD"],
            cwd=repo_root
        )
        commit_count = count_result.stdout.strip() if count_result.returncode == 0 else "?"
        
        return {
            "success": True,
            "new_head": new_head,
            "commit_count": commit_count,
            "message": commit_message,
            "pushed": self.push
        }
    
    @classmethod
    def create_argument_parser(cls):
        """Создать argument parser с дополнительными аргументами."""
        parser = super().create_argument_parser()
        parser.add_argument(
            "--task",
            help="Task ID (used for default commit message)"
        )
        parser.add_argument(
            "--message", "-m",
            help="Commit message (overrides task-based message)"
        )
        parser.add_argument(
            "--no-push",
            action="store_true",
            help="Commit only, do not push"
        )
        return parser


def main():
    parser = CommitPushLauncher.create_argument_parser()
    args = parser.parse_args()
    
    try:
        config = LauncherConfig(args.config)
    except FileNotFoundError as e:
        print(f"ERROR: {e}", file=sys.stderr)
        sys.exit(1)
    
    launcher = CommitPushLauncher(
        config=config,
        dry_run=args.dry_run,
        verbose=args.verbose,
        task_id=args.task,
        message=args.message,
        push=not args.no_push
    )
    
    sys.exit(launcher.run())


if __name__ == "__main__":
    main()
