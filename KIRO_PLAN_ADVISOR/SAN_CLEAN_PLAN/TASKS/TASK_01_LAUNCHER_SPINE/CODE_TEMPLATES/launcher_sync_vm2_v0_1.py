#!/usr/bin/env python3
"""
IMPERIUM Launcher: Sync VM2 v0.1

Синхронизация репозитория на VM2 с GitHub после push с PC.
Запускается на VM2 для получения последних изменений.

Usage:
    python3 launcher_sync_vm2_v0_1.py [--dry-run] [--verbose]

Author: KIRO Advisory
Date: 2026-05-14
"""

import sys
from pathlib import Path
from typing import Dict, Any

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

try:
    from TOOLS.imperium_launcher_v0_1 import (
        BaseLauncher, LauncherConfig, detect_platform
    )
except ImportError:
    print("ERROR: Cannot import imperium_launcher_v0_1. Run from repo root.")
    sys.exit(1)


class SyncVM2Launcher(BaseLauncher):
    """Лаунчер для синхронизации VM2 с GitHub."""
    
    LAUNCHER_ID = "SYNC_VM2"
    DESCRIPTION = "Sync VM2 repository with GitHub (git fetch + git pull)"
    
    def __init__(self, config: LauncherConfig, dry_run: bool = False,
                 verbose: bool = False, expected_head: str = None):
        super().__init__(config, dry_run, verbose)
        self.expected_head = expected_head
    
    def execute(self, **kwargs) -> Dict[str, Any]:
        """Выполнить синхронизацию VM2."""
        
        # Проверка платформы
        platform = detect_platform()
        if platform != "LINUX":
            return {
                "success": False,
                "error": f"This launcher runs on VM2 (Linux) only. Current: {platform}"
            }
        
        self.receipt.add_step("PLATFORM_CHECK", "PASS", {"platform": platform})
        
        repo_root = Path(self.config.vm2_repo_root)
        
        # Проверить что директория существует
        if not repo_root.exists():
            return {
                "success": False,
                "error": f"VM2 repo root not found: {repo_root}"
            }
        
        self.receipt.add_step("REPO_EXISTS", "PASS")
        
        # Получить текущий HEAD до синхронизации
        head_before = self.get_git_head(repo_root)
        self.log(f"HEAD before sync: {head_before}")
        self.receipt.add_step("HEAD_BEFORE", "PASS", {"head": head_before})
        
        # Проверить git status
        git_status = self.get_git_status(repo_root)
        if git_status:
            self.receipt.add_warning(f"VM2 has uncommitted changes:\n{git_status}")
            self.log("WARNING: VM2 has uncommitted changes. They may conflict with pull.")
        
        # Git fetch
        fetch_result = self.run_command(
            ["git", "fetch", "origin"],
            cwd=repo_root,
            timeout=120
        )
        
        if fetch_result.returncode != 0:
            self.receipt.add_step("GIT_FETCH", "FAIL", {
                "stderr": fetch_result.stderr[:300]
            })
            return {
                "success": False,
                "error": f"git fetch failed: {fetch_result.stderr}"
            }
        
        self.receipt.add_step("GIT_FETCH", "PASS")
        
        # Проверить origin/master
        origin_head_result = self.run_command(
            ["git", "rev-parse", "origin/master"],
            cwd=repo_root
        )
        origin_head = origin_head_result.stdout.strip() if origin_head_result.returncode == 0 else "UNKNOWN"
        self.log(f"origin/master: {origin_head}")
        
        # Git pull
        pull_result = self.run_command(
            ["git", "pull", "origin", "master"],
            cwd=repo_root,
            timeout=120
        )
        
        if pull_result.returncode != 0:
            # Проверить если конфликт
            if "conflict" in pull_result.stderr.lower() or "conflict" in pull_result.stdout.lower():
                self.receipt.add_step("GIT_PULL", "CONFLICT", {
                    "output": pull_result.stdout[:500]
                })
                return {
                    "success": False,
                    "error": "Git pull resulted in conflicts. Manual resolution required."
                }
            
            self.receipt.add_step("GIT_PULL", "FAIL", {
                "stderr": pull_result.stderr[:300]
            })
            return {
                "success": False,
                "error": f"git pull failed: {pull_result.stderr}"
            }
        
        self.receipt.add_step("GIT_PULL", "PASS", {
            "output": pull_result.stdout[:300]
        })
        
        # Получить новый HEAD
        head_after = self.get_git_head(repo_root)
        self.log(f"HEAD after sync: {head_after}")
        
        # Проверить expected_head если указан
        if self.expected_head:
            if head_after != self.expected_head:
                self.receipt.add_warning(
                    f"HEAD mismatch: expected {self.expected_head}, got {head_after}"
                )
            else:
                self.receipt.add_step("HEAD_VERIFY", "PASS")
        
        # Получить commit count
        count_result = self.run_command(
            ["git", "rev-list", "--count", "HEAD"],
            cwd=repo_root
        )
        commit_count = count_result.stdout.strip() if count_result.returncode == 0 else "?"
        
        # Определить сколько коммитов было получено
        if head_before != head_after:
            commits_pulled_result = self.run_command(
                ["git", "rev-list", "--count", f"{head_before}..{head_after}"],
                cwd=repo_root
            )
            commits_pulled = commits_pulled_result.stdout.strip() if commits_pulled_result.returncode == 0 else "?"
        else:
            commits_pulled = "0"
        
        self.receipt.add_step("SYNC_COMPLETE", "PASS", {
            "head_before": head_before,
            "head_after": head_after,
            "commits_pulled": commits_pulled,
            "total_commits": commit_count
        })
        
        return {
            "success": True,
            "head_before": head_before,
            "head_after": head_after,
            "commits_pulled": commits_pulled,
            "commit_count": commit_count
        }
    
    @classmethod
    def create_argument_parser(cls):
        """Создать argument parser с дополнительными аргументами."""
        parser = super().create_argument_parser()
        parser.add_argument(
            "--expected-head",
            help="Expected HEAD after sync (for verification)"
        )
        return parser


def main():
    parser = SyncVM2Launcher.create_argument_parser()
    args = parser.parse_args()
    
    try:
        config = LauncherConfig(args.config)
    except FileNotFoundError as e:
        print(f"ERROR: {e}", file=sys.stderr)
        sys.exit(1)
    
    launcher = SyncVM2Launcher(
        config=config,
        dry_run=args.dry_run,
        verbose=args.verbose,
        expected_head=args.expected_head
    )
    
    sys.exit(launcher.run())


if __name__ == "__main__":
    main()
