#!/usr/bin/env python3
"""
IMPERIUM Launcher Framework v0.1

Базовый framework для всех IMPERIUM лаунчеров.
Заменяет ad hoc PowerShell команды на зарегистрированные Python скрипты с receipts.

Usage:
    Этот файл не запускается напрямую.
    Импортируется другими лаунчерами.

Author: KIRO Advisory
Date: 2026-05-14
"""

import argparse
import json
import hashlib
import subprocess
import sys
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional, Dict, Any, List


class LauncherConfig:
    """Загрузка и валидация конфигурации лаунчера."""
    
    def __init__(self, config_path: Optional[Path] = None):
        if config_path is None:
            # Поиск конфига относительно скрипта
            script_dir = Path(__file__).parent.parent
            config_path = script_dir / "CONFIG" / "launcher_routes_v0_1.json"
        
        self.config_path = Path(config_path)
        self.config = self._load_config()
    
    def _load_config(self) -> Dict[str, Any]:
        """Загрузить конфигурацию из файла."""
        if not self.config_path.exists():
            raise FileNotFoundError(f"Config not found: {self.config_path}")
        
        with open(self.config_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    @property
    def pc_repo_root(self) -> str:
        return self.config.get("pc_repo_root", "E:\\IMPERIUM")
    
    @property
    def vm2_repo_root(self) -> str:
        return self.config.get("vm2_repo_root", "/home/vboxuser2/IMPERIUM_WORK/Imperium-")
    
    @property
    def external_context_local(self) -> str:
        return self.config.get("external_context_local", "E:\\IMPERIUM_CONTEXT\\LOCAL")
    
    @property
    def external_context_private(self) -> str:
        return self.config.get("external_context_private", "E:\\IMPERIUM_CONTEXT\\PRIVATE")
    
    @property
    def vm2_bundle_outbox(self) -> str:
        return self.config.get("vm2_bundle_outbox", "/home/vboxuser2/IMPERIUM_WORK/VM2_BUNDLES")
    
    @property
    def pc_bundle_inbox(self) -> str:
        return self.config.get("pc_bundle_inbox", "E:\\IMPERIUM_CONTEXT\\LOCAL\\VM2_BUNDLES")
    
    @property
    def pc_bundle_review(self) -> str:
        return self.config.get("pc_bundle_review", "E:\\IMPERIUM_CONTEXT\\LOCAL\\BUNDLE_REVIEWS")
    
    @property
    def ssh_pc_to_vm2(self) -> Dict[str, str]:
        return self.config.get("ssh_pc_to_vm2", {
            "user": "vboxuser2",
            "host": "127.0.0.1",
            "port": "2223",
            "key": "$env:USERPROFILE\\.ssh\\imperium_pc_to_vm2_ed25519_20260418"
        })
    
    @property
    def ssh_vm2_to_pc(self) -> Dict[str, str]:
        return self.config.get("ssh_vm2_to_pc", {
            "user": "pc",
            "host": "10.0.2.2",
            "key": "/home/vboxuser2/.ssh/imperium_vm2_to_pc_ed25519_20260418"
        })


class LauncherReceipt:
    """Генерация и валидация receipts лаунчера."""
    
    def __init__(self, launcher_id: str, task_id: Optional[str] = None):
        self.launcher_id = launcher_id
        self.task_id = task_id
        self.started_at = datetime.now(timezone.utc)
        self.steps: List[Dict[str, Any]] = []
        self.verdict = "NOT_STARTED"
        self.errors: List[str] = []
        self.warnings: List[str] = []
    
    def add_step(self, step_name: str, status: str, details: Optional[Dict] = None):
        """Добавить шаг в receipt."""
        self.steps.append({
            "step": step_name,
            "status": status,
            "timestamp_utc": datetime.now(timezone.utc).isoformat(),
            "details": details or {}
        })
    
    def set_verdict(self, verdict: str):
        """Установить финальный verdict."""
        self.verdict = verdict
    
    def add_error(self, error: str):
        """Добавить ошибку."""
        self.errors.append(error)
    
    def add_warning(self, warning: str):
        """Добавить предупреждение."""
        self.warnings.append(warning)
    
    def to_dict(self) -> Dict[str, Any]:
        """Конвертировать в словарь."""
        return {
            "schema_version": "launcher_receipt_v0_1",
            "launcher_id": self.launcher_id,
            "task_id": self.task_id,
            "started_at_utc": self.started_at.isoformat(),
            "completed_at_utc": datetime.now(timezone.utc).isoformat(),
            "verdict": self.verdict,
            "steps": self.steps,
            "errors": self.errors,
            "warnings": self.warnings
        }
    
    def save(self, output_path: Path):
        """Сохранить receipt в файл."""
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(self.to_dict(), f, indent=2, ensure_ascii=False)


class BaseLauncher:
    """Базовый класс для всех IMPERIUM лаунчеров."""
    
    LAUNCHER_ID = "BASE_LAUNCHER"
    DESCRIPTION = "Base launcher class"
    
    def __init__(self, config: LauncherConfig, dry_run: bool = False, verbose: bool = False):
        self.config = config
        self.dry_run = dry_run
        self.verbose = verbose
        self.receipt = LauncherReceipt(self.LAUNCHER_ID)
    
    def log(self, message: str):
        """Логировать сообщение если verbose."""
        if self.verbose:
            timestamp = datetime.now().strftime("%H:%M:%S")
            print(f"[{timestamp}] [{self.LAUNCHER_ID}] {message}")
    
    def log_error(self, message: str):
        """Логировать ошибку."""
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"[{timestamp}] [{self.LAUNCHER_ID}] ERROR: {message}", file=sys.stderr)
    
    def run_command(self, cmd: List[str], cwd: Optional[Path] = None, 
                    capture: bool = True, timeout: int = 300) -> subprocess.CompletedProcess:
        """Запустить команду с логированием и dry-run поддержкой."""
        cmd_str = ' '.join(cmd)
        self.log(f"Running: {cmd_str}")
        
        if self.dry_run:
            self.log(f"[DRY-RUN] Would execute: {cmd_str}")
            return subprocess.CompletedProcess(cmd, 0, stdout="[DRY-RUN]", stderr="")
        
        try:
            result = subprocess.run(
                cmd,
                cwd=cwd,
                capture_output=capture,
                text=True,
                timeout=timeout
            )
            
            if result.returncode != 0:
                self.log(f"Command failed with code {result.returncode}")
                if result.stderr:
                    self.log(f"stderr: {result.stderr[:500]}")
            
            return result
            
        except subprocess.TimeoutExpired as e:
            self.receipt.add_error(f"Command timed out after {timeout}s: {cmd_str}")
            raise
        except Exception as e:
            self.receipt.add_error(f"Command failed: {cmd_str} — {e}")
            raise
    
    def compute_sha256(self, file_path: Path) -> str:
        """Вычислить SHA256 хеш файла."""
        sha256 = hashlib.sha256()
        with open(file_path, 'rb') as f:
            for chunk in iter(lambda: f.read(8192), b''):
                sha256.update(chunk)
        return sha256.hexdigest()
    
    def get_git_head(self, repo_path: Optional[Path] = None) -> str:
        """Получить текущий Git HEAD."""
        cmd = ["git", "rev-parse", "HEAD"]
        result = self.run_command(cmd, cwd=repo_path)
        if result.returncode == 0:
            return result.stdout.strip()
        return "UNKNOWN"
    
    def get_git_status(self, repo_path: Optional[Path] = None) -> str:
        """Получить git status --short."""
        cmd = ["git", "status", "--short"]
        result = self.run_command(cmd, cwd=repo_path)
        return result.stdout if result.returncode == 0 else ""
    
    def execute(self, **kwargs) -> Dict[str, Any]:
        """Выполнить основную логику. Переопределить в подклассах."""
        raise NotImplementedError("Subclasses must implement execute()")
    
    def run(self, **kwargs) -> int:
        """Главная точка входа с обработкой receipts."""
        try:
            self.receipt.add_step("INIT", "STARTED")
            self.log(f"Starting {self.LAUNCHER_ID}")
            
            if self.dry_run:
                self.log("Running in DRY-RUN mode")
            
            result = self.execute(**kwargs)
            
            if result.get("success"):
                self.receipt.set_verdict("PASS")
                self.log("Completed successfully")
                return 0
            else:
                self.receipt.set_verdict("FAIL")
                self.log_error(f"Failed: {result.get('error', 'Unknown error')}")
                return 1
                
        except Exception as e:
            self.receipt.add_error(str(e))
            self.receipt.set_verdict("ERROR")
            self.log_error(f"Exception: {e}")
            return 2
            
        finally:
            # Сохранить receipt
            runtime_dir = Path(".imperium_runtime") / "launcher" / self.LAUNCHER_ID.lower()
            receipt_path = runtime_dir / f"{self.LAUNCHER_ID}_RECEIPT.json"
            self.receipt.save(receipt_path)
            self.log(f"Receipt saved: {receipt_path}")
    
    @classmethod
    def create_argument_parser(cls) -> argparse.ArgumentParser:
        """Создать базовый argument parser."""
        parser = argparse.ArgumentParser(
            description=cls.DESCRIPTION,
            formatter_class=argparse.RawDescriptionHelpFormatter
        )
        parser.add_argument(
            "--config",
            type=Path,
            help="Path to launcher config file"
        )
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Run in dry-run mode (no actual changes)"
        )
        parser.add_argument(
            "--verbose", "-v",
            action="store_true",
            help="Enable verbose output"
        )
        return parser


def detect_platform() -> str:
    """Определить текущую платформу."""
    if sys.platform == "win32":
        return "WINDOWS"
    elif sys.platform == "linux":
        return "LINUX"
    else:
        return "UNKNOWN"


def expand_path(path: str) -> str:
    """Раскрыть переменные окружения в пути."""
    # Обработка $env:USERPROFILE для PowerShell стиля
    if "$env:" in path:
        import re
        def replace_env(match):
            var_name = match.group(1)
            return os.environ.get(var_name, match.group(0))
        path = re.sub(r'\$env:(\w+)', replace_env, path)
    
    # Стандартное раскрытие
    return os.path.expandvars(os.path.expanduser(path))


if __name__ == "__main__":
    print("This module is not meant to be run directly.")
    print("Import it in other launcher scripts.")
    sys.exit(0)
