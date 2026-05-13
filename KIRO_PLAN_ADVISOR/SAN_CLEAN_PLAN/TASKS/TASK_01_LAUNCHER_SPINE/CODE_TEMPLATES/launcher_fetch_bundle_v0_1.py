#!/usr/bin/env python3
"""
IMPERIUM Launcher: Fetch Bundle v0.1

Получение bundle с VM2 на PC через SSH/SCP.
Заменяет ad hoc scp команды в чате.

Usage:
    python3 launcher_fetch_bundle_v0_1.py --task TASK-ID [--dry-run] [--verbose]

Author: KIRO Advisory
Date: 2026-05-14
"""

import sys
import os
from pathlib import Path
from typing import Dict, Any, Optional

# Добавить родительскую директорию для импорта
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

try:
    from TOOLS.imperium_launcher_v0_1 import (
        BaseLauncher, LauncherConfig, detect_platform, expand_path
    )
except ImportError:
    # Fallback для standalone запуска
    print("ERROR: Cannot import imperium_launcher_v0_1. Run from repo root.")
    sys.exit(1)


class FetchBundleLauncher(BaseLauncher):
    """Лаунчер для получения bundle с VM2."""
    
    LAUNCHER_ID = "FETCH_BUNDLE"
    DESCRIPTION = "Fetch task bundle from VM2 to PC via SSH/SCP"
    
    def __init__(self, config: LauncherConfig, dry_run: bool = False, 
                 verbose: bool = False, task_id: Optional[str] = None):
        super().__init__(config, dry_run, verbose)
        self.task_id = task_id
        self.receipt.task_id = task_id
    
    def execute(self, **kwargs) -> Dict[str, Any]:
        """Выполнить fetch bundle."""
        
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
        
        self.receipt.add_step("TASK_ID_CHECK", "PASS", {"task_id": self.task_id})
        
        # Определить пути
        vm2_bundle_path = f"{self.config.vm2_bundle_outbox}/{self.task_id}_BUNDLE"
        pc_inbox_path = Path(self.config.pc_bundle_inbox) / f"{self.task_id}_BUNDLE"
        
        self.log(f"VM2 source: {vm2_bundle_path}")
        self.log(f"PC destination: {pc_inbox_path}")
        
        # Построить SCP команду
        ssh_config = self.config.ssh_pc_to_vm2
        ssh_key = expand_path(ssh_config["key"])
        
        scp_cmd = [
            "scp",
            "-r",
            "-i", ssh_key,
            "-P", ssh_config["port"],
            f"{ssh_config['user']}@{ssh_config['host']}:{vm2_bundle_path}",
            str(pc_inbox_path)
        ]
        
        self.receipt.add_step("SCP_COMMAND_BUILD", "PASS", {"command": " ".join(scp_cmd)})
        
        # Создать inbox директорию если не существует
        if not self.dry_run:
            pc_inbox_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Выполнить SCP
        try:
            result = self.run_command(scp_cmd, timeout=600)
            
            if result.returncode != 0:
                self.receipt.add_step("SCP_EXECUTE", "FAIL", {
                    "returncode": result.returncode,
                    "stderr": result.stderr[:500] if result.stderr else ""
                })
                return {
                    "success": False,
                    "error": f"SCP failed with code {result.returncode}"
                }
            
            self.receipt.add_step("SCP_EXECUTE", "PASS")
            
        except Exception as e:
            self.receipt.add_step("SCP_EXECUTE", "ERROR", {"exception": str(e)})
            return {"success": False, "error": str(e)}
        
        # Проверить что bundle получен
        if not self.dry_run:
            if not pc_inbox_path.exists():
                self.receipt.add_step("BUNDLE_VERIFY", "FAIL", {
                    "expected_path": str(pc_inbox_path)
                })
                return {"success": False, "error": "Bundle not found after SCP"}
            
            # Проверить наличие MANIFEST.json
            manifest_path = pc_inbox_path / "MANIFEST.json"
            if not manifest_path.exists():
                self.receipt.add_warning("MANIFEST.json not found in bundle")
            else:
                self.receipt.add_step("MANIFEST_CHECK", "PASS")
        
        self.receipt.add_step("BUNDLE_VERIFY", "PASS", {
            "bundle_path": str(pc_inbox_path)
        })
        
        return {
            "success": True,
            "bundle_path": str(pc_inbox_path),
            "task_id": self.task_id
        }
    
    @classmethod
    def create_argument_parser(cls):
        """Создать argument parser с дополнительными аргументами."""
        parser = super().create_argument_parser()
        parser.add_argument(
            "--task",
            required=True,
            help="Task ID for the bundle (e.g., TASK-20260514-001)"
        )
        return parser


def main():
    parser = FetchBundleLauncher.create_argument_parser()
    args = parser.parse_args()
    
    try:
        config = LauncherConfig(args.config)
    except FileNotFoundError as e:
        print(f"ERROR: {e}", file=sys.stderr)
        print("Create CONFIG/launcher_routes_v0_1.json first.", file=sys.stderr)
        sys.exit(1)
    
    launcher = FetchBundleLauncher(
        config=config,
        dry_run=args.dry_run,
        verbose=args.verbose,
        task_id=args.task
    )
    
    sys.exit(launcher.run())


if __name__ == "__main__":
    main()
