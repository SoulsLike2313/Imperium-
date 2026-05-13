# TASK 03: Current Truth Inventory v0.1

## Метаданные
- task_id: `TASK-20260514-SAN-CLEANING-CURRENT-TRUTH-INVENTORY-V0_1`
- priority: P1 — ВЫСОКИЙ
- platform: VM2 или PC (read-only)
- estimated_files: 1 скрипт + 3 output файла
- dependencies: TASK_02 (пути должны быть исправлены)

## Цель
Полная read-only инвентаризация всех скриптов, инструментов и сирот в репозитории.

## Проблема
Текущие реестры (`SCRIPT_REGISTRY.json`, `ORGAN_REGISTRY.json`) могут дрейфовать от реальности.
Нужен свежий snapshot того, что реально есть в репозитории.

## Входные данные
- Весь репозиторий (read-only scan)
- `REGISTRY/SCRIPT_REGISTRY.json` — для сравнения
- `REGISTRY/ORGAN_REGISTRY.json` — для сравнения

## Выходные данные

### 1. CURRENT_TRUTH_INVENTORY.json
```json
{
  "schema_version": "current_truth_inventory_v0_1",
  "generated_at_utc": "2026-05-14T...",
  "git_head": "9307c4883926edd3f843fd1224fdee244b47b1a0",
  
  "scripts": {
    "total": 45,
    "by_type": {
      "checker": 12,
      "launcher": 5,
      "utility": 8,
      "...": "..."
    },
    "by_status": {
      "registered": 30,
      "unregistered": 15
    },
    "items": [
      {
        "path": "scripts/verify_repo.py",
        "type": "checker",
        "compiles": true,
        "registered": true,
        "registry_id": "SCRIPT-VERIFY-REPO"
      }
    ]
  },
  
  "tools": {
    "total": 10,
    "items": [
      {
        "name": "git",
        "type": "vcs",
        "verified": true,
        "version": "2.40.0"
      }
    ]
  },
  
  "orphans": {
    "total": 5,
    "items": [
      {
        "path": "old_script.py",
        "reason": "not_in_registry",
        "recommendation": "register_or_archive"
      }
    ]
  }
}
```

### 2. CURRENT_TRUTH_INVENTORY.md
Человекочитаемый отчёт с таблицами и статистикой.

### 3. INVENTORY_DIFF.md
Сравнение с текущими реестрами — что добавить, что удалить.

## Алгоритм

### Шаг 1: Сканирование скриптов
```python
# Найти все .py, .ps1, .sh файлы
# Исключить: .git, __pycache__, .imperium_runtime, ARTIFACTS

for file in repo.glob('**/*.py'):
    if should_exclude(file):
        continue
    
    script_info = {
        'path': str(file.relative_to(repo)),
        'compiles': check_py_compile(file),
        'has_main': has_main_block(file),
        'has_argparse': has_argparse(file),
        'docstring': extract_docstring(file),
    }
```

### Шаг 2: Сопоставление с реестром
```python
# Загрузить SCRIPT_REGISTRY.json
# Для каждого найденного скрипта проверить:
# - Есть ли в реестре?
# - Совпадает ли путь?
# - Совпадает ли статус?
```

### Шаг 3: Сканирование инструментов
```python
# Проверить наличие и версии:
tools_to_check = ['git', 'python3', 'pip', 'ssh', 'scp', 'rsync']

for tool in tools_to_check:
    version = get_tool_version(tool)
    available = version is not None
```

### Шаг 4: Идентификация сирот
```python
# Сироты = файлы которые:
# - Выглядят как скрипты (имеют shebang или main)
# - Не в реестре
# - Не в известных legacy/archive папках
```

## Файлы для создания

### 1. Inventory Script
**Путь:** `TOOLS/current_truth_inventory_v0_1.py`

### 2. Output Directory
**Путь:** `CURRENT_STATE/INVENTORY_20260514/`

## Проверки

### Обязательные проверки
```bash
# 1. Компиляция
python3 -m py_compile TOOLS/current_truth_inventory_v0_1.py

# 2. Dry-run
python3 TOOLS/current_truth_inventory_v0_1.py --dry-run --verbose

# 3. Full run
python3 TOOLS/current_truth_inventory_v0_1.py --output CURRENT_STATE/INVENTORY_20260514/

# 4. Валидация JSON
python3 -c "import json; json.load(open('CURRENT_STATE/INVENTORY_20260514/CURRENT_TRUTH_INVENTORY.json'))"
```

## Критерии успеха
- [ ] Скрипт создан и компилируется
- [ ] JSON output валиден
- [ ] Markdown отчёт читаем
- [ ] Все скрипты просканированы
- [ ] Diff с реестрами сгенерирован
- [ ] Receipt создан

## Критерии блокировки
- Скрипт не компилируется
- JSON невалиден
- Пропущены важные директории

## Ожидаемый Servitor prompt outline

```
TASK: TASK-20260514-SAN-CLEANING-CURRENT-TRUTH-INVENTORY-V0_1
GOAL: Create comprehensive read-only inventory of all scripts and tools

STEPS:
1. Read KIRO_PLAN_ADVISOR/SAN_CLEAN_PLAN/TASKS/TASK_03_CURRENT_TRUTH_INVENTORY/
2. Create TOOLS/current_truth_inventory_v0_1.py
3. Run py_compile
4. Run --dry-run --verbose
5. Run full inventory
6. Validate JSON output
7. Review markdown report
8. Build bundle for PC review

CONSTRAINTS:
- READ-ONLY operation
- Do NOT modify any files except output
- Do NOT commit from VM2
```
