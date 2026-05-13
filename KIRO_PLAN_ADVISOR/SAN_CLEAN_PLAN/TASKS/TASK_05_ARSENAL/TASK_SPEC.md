# TASK 05: ARSENAL First Registration Wave v0.1

## Метаданные
- task_id: `TASK-20260514-SAN-CLEANING-ARSENAL-FIRST-WAVE-V0_1`
- priority: P1 — ВЫСОКИЙ
- platform: PC и VM2
- estimated_files: 1 скрипт + новый реестр
- dependencies: TASK_03 (нужен inventory)

## Цель
Зарегистрировать все внешние инструменты в ARSENAL реестре.

## Проблема
Внешние инструменты (git, python, ssh, scp, etc.) не зарегистрированы формально.
Это создаёт неявные зависимости и затрудняет воспроизводимость.

## Входные данные
- `CURRENT_STATE/INVENTORY_20260514/CURRENT_TRUTH_INVENTORY.json` — список инструментов
- `KIRO_PLAN_ADVISOR/SAN_CLEAN_PLAN/SCHEMAS/arsenal_entry_v0_1.schema.json`

## Выходные данные
- Новый `REGISTRY/ARSENAL_REGISTRY.json`
- `REGISTRY/ARSENAL_REGISTRATION_RECEIPT.json`

## Список инструментов для регистрации

### Обязательные (PC и VM2)
| Tool | Type | Category | Verification |
|------|------|----------|--------------|
| git | vcs | version_control | `git --version` |
| python3 | runtime | development | `python3 --version` |
| pip | cli | development | `pip --version` |
| ssh | cli | communication | `ssh -V` |
| scp | cli | communication | `scp` (no version) |

### PC Only
| Tool | Type | Category | Verification |
|------|------|----------|--------------|
| PowerShell | cli | development | `$PSVersionTable.PSVersion` |
| VirtualBox | vm | virtualization | `VBoxManage --version` |
| VS Code | ide | development | `code --version` |
| Kiro | ide | development | N/A |

### VM2 Only
| Tool | Type | Category | Verification |
|------|------|----------|--------------|
| bash | cli | development | `bash --version` |
| rsync | cli | communication | `rsync --version` |

## Алгоритм

### Шаг 1: Определение платформы
```python
import platform
current_platform = 'WINDOWS' if platform.system() == 'Windows' else 'LINUX'
```

### Шаг 2: Проверка инструментов
```python
def check_tool(tool_name: str, version_cmd: str) -> Dict:
    """Проверить наличие и версию инструмента."""
    try:
        result = subprocess.run(
            version_cmd.split(),
            capture_output=True,
            text=True,
            timeout=10
        )
        return {
            'available': result.returncode == 0,
            'version': extract_version(result.stdout or result.stderr),
            'path': shutil.which(tool_name)
        }
    except Exception as e:
        return {'available': False, 'error': str(e)}
```

### Шаг 3: Генерация записей
```python
for tool in tools_to_check:
    check_result = check_tool(tool['name'], tool['version_cmd'])
    
    entry = {
        'tool_id': f"TOOL-{tool['name'].upper()}",
        'name': tool['name'],
        'type': tool['type'],
        'category': tool['category'],
        'status': 'active' if check_result['available'] else 'blocked',
        'platform': tool['platform'],
        'version': check_result.get('version'),
        'install_path': {current_platform.lower(): check_result.get('path')},
        'verification': {
            'command': tool['version_cmd'],
            'expected_output_contains': tool.get('expected_output')
        },
        'last_verified': today(),
        'created': today()
    }
```

### Шаг 4: Сохранение реестра
```python
registry = {
    'schema_version': 'arsenal_registry_v0_1',
    'created': today(),
    'updated': today(),
    'tools': entries,
    'statistics': {
        'total': len(entries),
        'available': len([e for e in entries if e['status'] == 'active']),
        'blocked': len([e for e in entries if e['status'] == 'blocked'])
    }
}

save_json('REGISTRY/ARSENAL_REGISTRY.json', registry)
```

## Файлы для создания

### 1. Arsenal Registration Script
**Путь:** `TOOLS/arsenal_register_v0_1.py`

```python
#!/usr/bin/env python3
"""
ARSENAL Registration Tool v0.1

Регистрация внешних инструментов в ARSENAL реестре.

Usage:
    python3 arsenal_register_v0_1.py --scan [--dry-run] [--verbose]
    python3 arsenal_register_v0_1.py --apply [--dry-run] [--verbose]
"""
```

### 2. Arsenal Registry
**Путь:** `REGISTRY/ARSENAL_REGISTRY.json`

## Проверки

### Обязательные проверки
```bash
# 1. Компиляция
python3 -m py_compile TOOLS/arsenal_register_v0_1.py

# 2. Scan
python3 TOOLS/arsenal_register_v0_1.py --scan --verbose

# 3. Apply dry-run
python3 TOOLS/arsenal_register_v0_1.py --apply --dry-run --verbose

# 4. Apply
python3 TOOLS/arsenal_register_v0_1.py --apply --verbose

# 5. Валидация реестра
python3 -c "import json; json.load(open('REGISTRY/ARSENAL_REGISTRY.json'))"
```

## Критерии успеха
- [ ] Скрипт создан и компилируется
- [ ] Все обязательные инструменты проверены
- [ ] Реестр создан и валиден
- [ ] Coverage ≥ 80%
- [ ] Receipt создан

## Критерии блокировки
- Скрипт не компилируется
- Обязательный инструмент недоступен
- Реестр невалидный JSON

## Ожидаемый Servitor prompt outline

```
TASK: TASK-20260514-SAN-CLEANING-ARSENAL-FIRST-WAVE-V0_1
GOAL: Register all external tools in ARSENAL

STEPS:
1. Read KIRO_PLAN_ADVISOR/SAN_CLEAN_PLAN/TASKS/TASK_05_ARSENAL/
2. Create TOOLS/arsenal_register_v0_1.py
3. Run py_compile
4. Run --scan --verbose
5. Review tool availability
6. Run --apply --dry-run --verbose
7. Run --apply --verbose
8. Validate REGISTRY/ARSENAL_REGISTRY.json
9. Build bundle for PC review

CONSTRAINTS:
- Do NOT commit from VM2
- All entries must validate against schema
- Report blocked tools clearly
```
