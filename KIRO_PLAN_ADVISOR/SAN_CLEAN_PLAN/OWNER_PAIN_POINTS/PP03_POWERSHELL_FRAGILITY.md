# PP03: PowerShell Command Blocks Are Fragile and Irritating

## Проблема
Quoting, heredocs, `>>`, CRLF, variable interpolation, SSH nesting, и Windows paths постоянно вызывают ошибки.
Каждый раз когда агент генерирует PowerShell блок в чате — риск ошибки.

## Требование Owner
Перейти от chat-generated PowerShell блоков к reusable Python-first лаунчерам с тонкими PowerShell wrappers только где необходимо.

## Решение

### Архитектурный паттерн: CLI-First with Thin Wrappers
Источник: [CLI vs Decorators for ML Pipelines](https://velda.io/blog/the-hidden-cost-in-pythonic-workflows)

> "Senior engineers are stripping away the complex decorators and returning to where they started: the Command Line Interface."

### Принципы Python-First Launcher

1. **Вся логика в Python** — никакой бизнес-логики в PowerShell
2. **PowerShell только для вызова** — однострочные wrappers
3. **Argparse для всех параметров** — никаких позиционных аргументов
4. **Dry-run по умолчанию** — опасные операции требуют явного флага
5. **Receipt для каждого запуска** — доказательство выполнения

### Структура лаунчера

```python
#!/usr/bin/env python3
"""
IMPERIUM Launcher: {NAME} v0.1

{DESCRIPTION}

Usage:
    python3 {script_name}.py --task TASK-ID [--dry-run] [--verbose]
    
Author: KIRO Advisory
Date: 2026-05-14
"""

import argparse
import sys
from pathlib import Path

# Импорт базового framework
from TOOLS.imperium_launcher_v0_1 import (
    BaseLauncher, LauncherConfig, detect_platform
)


class {ClassName}Launcher(BaseLauncher):
    """Лаунчер для {description}."""
    
    LAUNCHER_ID = "{LAUNCHER_ID}"
    DESCRIPTION = "{description}"
    
    def execute(self, **kwargs) -> Dict[str, Any]:
        """Выполнить основную логику."""
        
        # 1. Проверка платформы
        platform = detect_platform()
        if platform != "{EXPECTED_PLATFORM}":
            return {"success": False, "error": f"Wrong platform: {platform}"}
        
        self.receipt.add_step("PLATFORM_CHECK", "PASS")
        
        # 2. Основная логика
        # ...
        
        # 3. Возврат результата
        return {"success": True, "result": result}
    
    @classmethod
    def create_argument_parser(cls):
        parser = super().create_argument_parser()
        parser.add_argument("--task", required=True, help="Task ID")
        # Добавить специфичные аргументы
        return parser


def main():
    parser = {ClassName}Launcher.create_argument_parser()
    args = parser.parse_args()
    
    config = LauncherConfig(args.config)
    launcher = {ClassName}Launcher(
        config=config,
        dry_run=args.dry_run,
        verbose=args.verbose
    )
    
    sys.exit(launcher.run())


if __name__ == "__main__":
    main()
```

### PowerShell Wrapper (тонкий)

```powershell
# launcher_fetch_bundle.ps1
# Thin wrapper for Python launcher
param(
    [Parameter(Mandatory=$true)]
    [string]$TaskId,
    
    [switch]$DryRun,
    [switch]$Verbose
)

$pythonArgs = @("TOOLS/launcher_fetch_bundle_v0_1.py", "--task", $TaskId)

if ($DryRun) { $pythonArgs += "--dry-run" }
if ($Verbose) { $pythonArgs += "--verbose" }

& python3 @pythonArgs
exit $LASTEXITCODE
```

### Замена типичных PowerShell команд

| Было (PowerShell в чате) | Стало (Python launcher) |
|--------------------------|-------------------------|
| `scp -r -i $key ...` | `python3 launcher_fetch_bundle_v0_1.py --task TASK-001` |
| `git add -A; git commit -m "..."` | `python3 launcher_commit_push_v0_1.py --task TASK-001` |
| `git pull origin master` | `python3 launcher_sync_vm2_v0_1.py` |
| `Copy-Item -Recurse ...` | `python3 launcher_apply_bundle_v0_1.py --task TASK-001` |

### Обработка проблемных случаев

#### CRLF vs LF
```python
def normalize_line_endings(content: str) -> str:
    """Нормализовать line endings к LF."""
    return content.replace('\r\n', '\n').replace('\r', '\n')
```

#### Windows Paths
```python
def normalize_path(path: str) -> Path:
    """Нормализовать путь для текущей платформы."""
    # Заменить forward/back slashes на os.sep
    normalized = path.replace('/', os.sep).replace('\\', os.sep)
    return Path(normalized)
```

#### SSH Nesting
```python
def build_ssh_command(config: Dict, remote_cmd: str) -> List[str]:
    """Построить SSH команду без nesting проблем."""
    return [
        "ssh",
        "-i", expand_path(config["key"]),
        "-p", config["port"],
        f"{config['user']}@{config['host']}",
        remote_cmd  # Одна строка, без вложенных кавычек
    ]
```

## Файлы для создания

| Файл | Назначение | TASK |
|------|------------|------|
| `TOOLS/imperium_launcher_v0_1.py` | Базовый framework | TASK_01 |
| `TOOLS/launcher_fetch_bundle_v0_1.py` | Fetch bundle | TASK_01 |
| `TOOLS/launcher_apply_bundle_v0_1.py` | Apply bundle | TASK_01 |
| `TOOLS/launcher_commit_push_v0_1.py` | Commit/push | TASK_01 |
| `TOOLS/launcher_sync_vm2_v0_1.py` | Sync VM2 | TASK_01 |

## Проверка

```bash
# 1. Все лаунчеры компилируются
for f in TOOLS/launcher_*.py; do python3 -m py_compile "$f"; done

# 2. Все имеют --help
python3 TOOLS/launcher_fetch_bundle_v0_1.py --help

# 3. Все имеют --dry-run
python3 TOOLS/launcher_fetch_bundle_v0_1.py --task TEST-001 --dry-run --verbose

# 4. Receipts создаются
ls .imperium_runtime/launcher/
```

## Связь с задачами
- **TASK_01** (Launcher Spine) — создание всех лаунчеров

## Критерии успеха
- [ ] 0 PowerShell блоков в чате для стандартных операций
- [ ] Все лаунчеры имеют --dry-run
- [ ] Все лаунчеры создают receipts
- [ ] Все лаунчеры компилируются
- [ ] Все лаунчеры имеют --help
