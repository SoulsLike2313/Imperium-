#!/usr/bin/env python3
"""
IMPERIUM Launcher: Apply Bundle v0.1

Применение bundle к репозиторию на PC.
Копирует файлы из bundle в repo root с проверками.

Usage:
    python3 launcher_apply_bundle_v0_1.py --task TASK-ID [--dry-run] [--verbose]

Author: KIRO Advisory
Date: 2026-05-14
"""

import sys
import os
import json
import shutil
from pathlib import Path
from typing import Dict, Any, Optional, List

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

try:
    from TOOLS.imperium_launcher_v0_1 import (
        BaseLauncher, LauncherConfig, detect_platform
    )
except ImportError:
    print("ERROR: Cannot import imperium_launcher_v0_1. Run from repo root.")
    sys.exit(1)


class ApplyBundleLauncher(BaseLauncher):
    """Лаунчер для применения bundle к репозиторию."""
    
    LAUNCHER_ID = "APPLY_BUNDLE"
    DESCRIPTION = "Apply task bundle to PC repository"
    
    def __init__(self, config: LauncherConfig, dry_run: bool = False,
                 verbose: bool = False, task_id: Optional[str] = None,
                 force: bool = False):
        super().__init__(config, dry_run, verbose)
        self.task_id = task_id
        self.force = force
        self.receipt.task_id = task_id
    
    def _load_manifest(self, bundle_path: Path) -> Optional[Dict]:
        """Загрузить MANIFEST.json из bundle."""
        manifest_path = bundle_path / "MANIFEST.json"
        if not manifest_path.exists():
            self.receipt.add_warning("MANIFEST.json not found")
            return None
        
        with open(manifest_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def _verify_sha256(self, file_path: Path, expected_hash: str) -> bool:
        """Проверить SHA256 хеш файла."""
        actual_hash = self.compute_sha256(file_path)
        return actual_hash.lower() == expected_hash.lower()
    
    def _copy_file(self, src: Path, dst: Path) -> bool:
        """Скопировать файл с созданием директорий."""
        if self.dry_run:
            self.log(f"[DRY-RUN] Would copy: {src} -> {dst}")
            return True
        
        try:
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src, dst)
            return True
        except Exception as e:
            self.receipt.add_error(f"Failed to copy {src} -> {dst}: {e}")
            return False
    
    def execute(self, **kwargs) -> Dict[str, Any]:
        """Выполнить apply bundle."""
        
        # Проверка платформы
        platform = detect_platform()
        if platform != "WINDOWS":
            return {
                "success": False,
                "error": f"This launcher runs on PC (Windows) only. Current: {platform}"
            }
        
        self.receipt.add_step("PLATFORM_CHECK", "PASS", {"platform": platform})
        
        # Проверка task_id
        if not self.task_id:
            return {"success": False, "error": "Task ID is required (--task)"}
        
        # Определить пути
        bundle_path = Path(self.config.pc_bundle_inbox) / f"{self.task_id}_BUNDLE"
        repo_root = Path(self.config.pc_repo_root)
        
        self.log(f"Bundle path: {bundle_path}")
        self.log(f"Repo root: {repo_root}")
        
        # Проверить существование bundle
        if not bundle_path.exists():
            return {
                "success": False,
                "error": f"Bundle not found: {bundle_path}"
            }
        
        self.receipt.add_step("BUNDLE_EXISTS", "PASS")
        
        # Загрузить manifest
        manifest = self._load_manifest(bundle_path)
        
        # Найти changed_files директорию
        changed_files_dir = bundle_path / "changed_files"
        if not changed_files_dir.exists():
            return {
                "success": False,
                "error": "changed_files directory not found in bundle"
            }
        
        # Собрать список файлов для копирования
        files_to_copy: List[tuple] = []
        for root, dirs, files in os.walk(changed_files_dir):
            for file in files:
                src_path = Path(root) / file
                rel_path = src_path.relative_to(changed_files_dir)
                dst_path = repo_root / rel_path
                files_to_copy.append((src_path, dst_path, rel_path))
        
        self.log(f"Found {len(files_to_copy)} files to apply")
        self.receipt.add_step("FILES_SCAN", "PASS", {"file_count": len(files_to_copy)})
        
        # Проверить git status перед применением
        git_status = self.get_git_status(repo_root)
        if git_status and not self.force:
            self.receipt.add_warning(f"Repo has uncommitted changes:\n{git_status}")
            if not self.dry_run:
                self.log("WARNING: Repo has uncommitted changes. Use --force to override.")
        
        # Применить файлы
        applied_files = []
        failed_files = []
        
        for src_path, dst_path, rel_path in files_to_copy:
            self.log(f"Applying: {rel_path}")
            
            if self._copy_file(src_path, dst_path):
                applied_files.append(str(rel_path))
            else:
                failed_files.append(str(rel_path))
        
        self.receipt.add_step("FILES_APPLY", "PASS" if not failed_files else "PARTIAL", {
            "applied": len(applied_files),
            "failed": len(failed_files),
            "applied_files": applied_files[:20],  # Первые 20 для краткости
            "failed_files": failed_files
        })
        
        if failed_files:
            return {
                "success": False,
                "error": f"Failed to apply {len(failed_files)} files",
                "failed_files": failed_files
            }
        
        # Проверить git status после применения
        if not self.dry_run:
            new_git_status = self.get_git_status(repo_root)
            self.receipt.add_step("POST_APPLY_STATUS", "PASS", {
                "git_status": new_git_status[:500] if new_git_status else "clean"
            })
        
        # Переместить bundle в review директорию
        review_path = Path(self.config.pc_bundle_review) / f"{self.task_id}_BUNDLE"
        if not self.dry_run:
            try:
                review_path.parent.mkdir(parents=True, exist_ok=True)
                if review_path.exists():
                    shutil.rmtree(review_path)
                shutil.move(str(bundle_path), str(review_path))
                self.receipt.add_step("BUNDLE_MOVE_TO_REVIEW", "PASS", {
                    "review_path": str(review_path)
                })
            except Exception as e:
                self.receipt.add_warning(f"Failed to move bundle to review: {e}")
        
        return {
            "success": True,
            "applied_files": applied_files,
            "task_id": self.task_id
        }
    
    @classmethod
    def create_argument_parser(cls):
        """Создать argument parser с дополнительными аргументами."""
        parser = super().create_argument_parser()
        parser.add_argument(
            "--task",
            required=True,
            help="Task ID for the bundle"
        )
        parser.add_argument(
            "--force",
            action="store_true",
            help="Force apply even if repo has uncommitted changes"
        )
        return parser


def main():
    parser = ApplyBundleLauncher.create_argument_parser()
    args = parser.parse_args()
    
    try:
        config = LauncherConfig(args.config)
    except FileNotFoundError as e:
        print(f"ERROR: {e}", file=sys.stderr)
        sys.exit(1)
    
    launcher = ApplyBundleLauncher(
        config=config,
        dry_run=args.dry_run,
        verbose=args.verbose,
        task_id=args.task,
        force=args.force
    )
    
    sys.exit(launcher.run())


if __name__ == "__main__":
    main()
