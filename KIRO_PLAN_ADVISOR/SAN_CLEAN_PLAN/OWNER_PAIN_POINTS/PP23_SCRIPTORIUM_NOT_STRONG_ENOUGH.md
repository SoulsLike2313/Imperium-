# PP23: SCRIPTORIUM is Not Strong Enough Yet

## Проблема
Скрипты существуют без полного registry status, purpose, platform, side effects, reliability и repair history.
Нет единого источника правды о скриптах.

## Требование Owner
SCRIPTORIUM под MECHANICUS должен регистрировать:
- Все скрипты
- Тесты
- Side effects (побочные эффекты)
- Risks (риски)
- Dependencies (зависимости)
- Failures (сбои)
- Growth (рост)

## Решение

### Расширенная схема SCRIPTORIUM Entry

```json
{
  "schema_version": "scriptorium_entry_v0_2",
  
  "identity": {
    "script_id": "SCRIPT-VERIFY-REPO",
    "name": "Repository Verification Script",
    "path": "scripts/verify_repo.py",
    "version": "0.1.0",
    "created": "2026-01-15",
    "updated": "2026-05-14"
  },
  
  "classification": {
    "type": "checker",
    "category": "verification",
    "language": "python",
    "platform": ["WINDOWS", "LINUX"],
    "owner": "ADMINISTRATUM",
    "status": "active"
  },
  
  "interface": {
    "cli_args": [
      {"name": "--verbose", "required": false, "type": "flag", "description": "Подробный вывод"},
      {"name": "--json", "required": false, "type": "flag", "description": "JSON вывод"},
      {"name": "--check", "required": false, "type": "string", "description": "Конкретная проверка"}
    ],
    "stdin": false,
    "stdout": true,
    "stderr": true,
    "exit_codes": {
      "0": "PASS",
      "1": "FAIL",
      "2": "ERROR"
    }
  },
  
  "execution": {
    "has_dry_run": false,
    "produces_receipt": false,
    "idempotent": true,
    "timeout_seconds": 60,
    "requires_network": false,
    "requires_git": true
  },
  
  "quality": {
    "compiles": true,
    "last_compile_check": "2026-05-14",
    "has_tests": true,
    "test_path": "tests/test_verify_repo.py",
    "test_coverage_percent": 75,
    "last_test_run": "2026-05-14",
    "lint_clean": true
  },
  
  "dependencies": {
    "python_version": ">=3.8",
    "internal_modules": [
      "src/imperium/config.py",
      "src/imperium/receipts.py"
    ],
    "external_packages": [],
    "tools": ["git"],
    "files": [
      "REGISTRY/SCRIPT_REGISTRY.json",
      "REGISTRY/ORGAN_REGISTRY.json"
    ]
  },
  
  "side_effects": {
    "reads": [
      "REGISTRY/*.json",
      "ORGANS/*/",
      ".git/"
    ],
    "writes": [
      ".imperium_runtime/verify_repo/"
    ],
    "network": [],
    "destructive": false
  },
  
  "risks": {
    "risk_level": "low",
    "risks": [
      {
        "risk_id": "RISK-001",
        "description": "Может занять много времени на большом репо",
        "mitigation": "Использовать --check для конкретных проверок"
      }
    ]
  },
  
  "reliability": {
    "stability": "stable",
    "known_issues": [],
    "failure_history": [
      {
        "date": "2026-03-10",
        "description": "Падал на Windows из-за path separator",
        "fix": "Использовать pathlib",
        "fixed_in_version": "0.0.5"
      }
    ],
    "mtbf_days": 30
  },
  
  "documentation": {
    "docstring": true,
    "readme": false,
    "examples": [
      "python3 scripts/verify_repo.py",
      "python3 scripts/verify_repo.py --verbose",
      "python3 scripts/verify_repo.py --check py_compile"
    ]
  },
  
  "metrics": {
    "lines_of_code": 450,
    "complexity": "medium",
    "last_modified": "2026-05-14",
    "modification_count": 15,
    "contributors": ["KIRO", "Owner"]
  }
}
```

### Автоматический сбор метаданных

```python
def collect_script_metadata(script_path: Path) -> Dict:
    """Автоматически собрать метаданные скрипта."""
    metadata = {}
    
    # 1. Базовая информация
    metadata["path"] = str(script_path)
    metadata["name"] = script_path.stem
    metadata["language"] = detect_language(script_path)
    
    # 2. Компиляция
    metadata["compiles"] = check_py_compile(script_path)
    
    # 3. Docstring
    metadata["docstring"] = extract_docstring(script_path)
    
    # 4. CLI args (из argparse)
    metadata["cli_args"] = extract_argparse_args(script_path)
    
    # 5. Imports (зависимости)
    metadata["imports"] = extract_imports(script_path)
    
    # 6. Метрики кода
    metadata["lines_of_code"] = count_lines(script_path)
    metadata["complexity"] = estimate_complexity(script_path)
    
    # 7. Git история
    metadata["last_modified"] = get_git_last_modified(script_path)
    metadata["modification_count"] = get_git_commit_count(script_path)
    
    return metadata


def extract_argparse_args(script_path: Path) -> List[Dict]:
    """Извлечь аргументы из argparse."""
    content = script_path.read_text()
    args = []
    
    # Паттерн для add_argument
    pattern = r'add_argument\s*\(\s*["\']([^"\']+)["\']'
    matches = re.findall(pattern, content)
    
    for match in matches:
        args.append({
            "name": match,
            "required": "--" not in match,  # Позиционные обычно required
            "description": None  # Нужен более сложный парсинг
        })
    
    return args


def extract_imports(script_path: Path) -> Dict:
    """Извлечь импорты."""
    content = script_path.read_text()
    
    stdlib = []
    internal = []
    external = []
    
    for line in content.split('\n'):
        if line.startswith('import ') or line.startswith('from '):
            module = extract_module_name(line)
            
            if is_stdlib(module):
                stdlib.append(module)
            elif module.startswith('src.imperium') or module.startswith('TOOLS'):
                internal.append(module)
            else:
                external.append(module)
    
    return {
        "stdlib": stdlib,
        "internal": internal,
        "external": external
    }
```

### SCRIPTORIUM Registry Structure

```json
{
  "schema_version": "scriptorium_registry_v0_2",
  "description": "SCRIPTORIUM — Реестр всех скриптов IMPERIUM",
  "owner": "MECHANICUS",
  "created": "2026-05-14",
  "updated": "2026-05-14",
  
  "scripts": [
    { "...": "scriptorium_entry_v0_2 objects" }
  ],
  
  "statistics": {
    "total": 45,
    "by_status": {
      "active": 40,
      "deprecated": 3,
      "legacy": 2
    },
    "by_type": {
      "checker": 12,
      "launcher": 5,
      "utility": 15,
      "generator": 8,
      "test": 5
    },
    "by_owner": {
      "MECHANICUS": 20,
      "ADMINISTRATUM": 15,
      "SANCTUM": 5,
      "UNASSIGNED": 5
    },
    "quality": {
      "compiles": 45,
      "has_tests": 20,
      "has_dry_run": 15,
      "produces_receipt": 10
    }
  },
  
  "coverage": {
    "total_py_files": 50,
    "registered": 45,
    "unregistered": 5,
    "coverage_percent": 90.0
  },
  
  "health": {
    "last_full_scan": "2026-05-14T12:00:00Z",
    "scripts_with_issues": 3,
    "issues": [
      {
        "script_id": "SCRIPT-OLD-CHECKER",
        "issue": "Does not compile",
        "severity": "high"
      }
    ]
  }
}
```

### Команды SCRIPTORIUM

```bash
# 1. Сканировать и зарегистрировать новые скрипты
python3 TOOLS/scriptorium_register_v0_1.py --scan --apply

# 2. Обновить метаданные существующих
python3 TOOLS/scriptorium_update_v0_1.py --all

# 3. Проверить здоровье реестра
python3 TOOLS/scriptorium_health_v0_1.py --verbose

# 4. Найти незарегистрированные скрипты
python3 TOOLS/scriptorium_orphans_v0_1.py

# 5. Сгенерировать отчёт
python3 TOOLS/scriptorium_report_v0_1.py --output CURRENT_STATE/SCRIPTORIUM_REPORT.md
```

## Файлы для создания

| Файл | Назначение | TASK |
|------|------------|------|
| `schemas/scriptorium_entry_v0_2.schema.json` | Расширенная схема | TASK_04 |
| `TOOLS/scriptorium_register_v0_1.py` | Регистрация | TASK_04 |
| `TOOLS/scriptorium_update_v0_1.py` | Обновление метаданных | TASK_04 |
| `TOOLS/scriptorium_health_v0_1.py` | Проверка здоровья | TASK_04 |
| `TOOLS/scriptorium_orphans_v0_1.py` | Поиск сирот | TASK_04 |

## Проверка

```bash
# 1. Полное сканирование
python3 TOOLS/scriptorium_register_v0_1.py --scan --dry-run --verbose

# 2. Проверка coverage
python3 TOOLS/scriptorium_health_v0_1.py --check coverage

# 3. Валидация реестра
python3 -c "import json; json.load(open('REGISTRY/SCRIPT_REGISTRY.json'))"
```

## Связь с задачами
- **TASK_04** (SCRIPTORIUM First Registration Wave) — первая волна регистрации

## Критерии успеха
- [ ] Coverage ≥ 90%
- [ ] Все записи валидны по схеме
- [ ] Все скрипты имеют owner
- [ ] Все скрипты имеют type
- [ ] Failure history записывается
- [ ] Health check проходит
