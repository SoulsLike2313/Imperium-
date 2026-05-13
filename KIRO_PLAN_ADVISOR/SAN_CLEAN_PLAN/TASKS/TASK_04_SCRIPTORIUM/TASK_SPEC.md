# TASK 04: SCRIPTORIUM First Registration Wave v0.1

## Метаданные
- task_id: `TASK-20260514-SAN-CLEANING-SCRIPTORIUM-FIRST-WAVE-V0_1`
- priority: P1 — ВЫСОКИЙ
- platform: VM2 разработка, PC приёмка
- estimated_files: 1 скрипт + обновление реестра
- dependencies: TASK_03 (нужен inventory)

## Цель
Зарегистрировать все незарегистрированные скрипты в SCRIPTORIUM.

## Проблема
По данным inventory (TASK_03) есть ~15 незарегистрированных скриптов.
Это создаёт drift между реальностью и реестром.

## Входные данные
- `CURRENT_STATE/INVENTORY_20260514/CURRENT_TRUTH_INVENTORY.json`
- `CURRENT_STATE/INVENTORY_20260514/INVENTORY_DIFF.md`
- `REGISTRY/SCRIPT_REGISTRY.json`
- `KIRO_PLAN_ADVISOR/SAN_CLEAN_PLAN/SCHEMAS/scriptorium_entry_v0_1.schema.json`

## Выходные данные
- Обновлённый `REGISTRY/SCRIPT_REGISTRY.json`
- `REGISTRY/SCRIPTORIUM_REGISTRATION_RECEIPT.json`

## Алгоритм

### Шаг 1: Загрузка данных
```python
inventory = load_json('CURRENT_STATE/INVENTORY_20260514/CURRENT_TRUTH_INVENTORY.json')
registry = load_json('REGISTRY/SCRIPT_REGISTRY.json')
schema = load_json('schemas/scriptorium_entry_v0_1.schema.json')
```

### Шаг 2: Идентификация незарегистрированных
```python
unregistered = [
    s for s in inventory['scripts']['items']
    if not s['registered']
]
```

### Шаг 3: Генерация записей
```python
for script in unregistered:
    entry = {
        'script_id': generate_script_id(script['path']),
        'name': extract_name(script['path']),
        'path': script['path'],
        'type': infer_type(script),
        'status': 'active' if script['compiles'] else 'legacy',
        'owner': infer_owner(script['path']),
        'platform': infer_platform(script),
        'has_dry_run': check_has_dry_run(script['path']),
        'produces_receipt': check_produces_receipt(script['path']),
        'compiles': script['compiles'],
        'created': today(),
    }
    
    # Валидация по схеме
    validate(entry, schema)
```

### Шаг 4: Обновление реестра
```python
# Добавить новые записи
registry['scripts'].extend(new_entries)

# Обновить статистику
registry['statistics']['total'] = len(registry['scripts'])
registry['statistics']['registered'] = len([s for s in registry['scripts'] if s['status'] == 'active'])

# Сохранить
save_json('REGISTRY/SCRIPT_REGISTRY.json', registry)
```

### Шаг 5: Генерация receipt
```python
receipt = {
    'task_id': 'TASK-20260514-SAN-CLEANING-SCRIPTORIUM-FIRST-WAVE-V0_1',
    'registered_count': len(new_entries),
    'registered_scripts': [e['script_id'] for e in new_entries],
    'skipped_count': len(skipped),
    'skipped_reasons': skipped_reasons,
    'verdict': 'PASS' if errors == 0 else 'PARTIAL'
}
```

## Файлы для создания

### 1. Registration Script
**Путь:** `TOOLS/scriptorium_register_v0_1.py`

```python
#!/usr/bin/env python3
"""
SCRIPTORIUM Registration Tool v0.1

Регистрация скриптов в SCRIPTORIUM реестре.

Usage:
    python3 scriptorium_register_v0_1.py --inventory PATH --dry-run --verbose
    python3 scriptorium_register_v0_1.py --inventory PATH --apply --verbose
"""
```

## Правила генерации script_id

```python
def generate_script_id(path: str) -> str:
    """
    Генерировать script_id из пути.
    
    Примеры:
    - scripts/verify_repo.py → SCRIPT-VERIFY-REPO
    - TOOLS/check_launcher_registry_v0_1.py → SCRIPT-CHECK-LAUNCHER-REGISTRY-V0-1
    - SANCTUM/sanctum_v0_29_qt.py → SCRIPT-SANCTUM-V0-29-QT
    """
    name = Path(path).stem  # без расширения
    name = name.upper()
    name = name.replace('_', '-')
    return f'SCRIPT-{name}'
```

## Правила определения owner

```python
def infer_owner(path: str) -> str:
    """
    Определить owner по пути.
    
    Правила:
    - ORGANS/ADMINISTRATUM/* → ADMINISTRATUM
    - ORGANS/MECHANICUS/* → MECHANICUS
    - SANCTUM/* → SANCTUM
    - scripts/* → ADMINISTRATUM
    - TOOLS/* → MECHANICUS
    - tests/* → INQUISITION
    """
    path_lower = path.lower()
    
    if 'organs/administratum' in path_lower:
        return 'ADMINISTRATUM'
    elif 'organs/mechanicus' in path_lower:
        return 'MECHANICUS'
    elif 'sanctum' in path_lower:
        return 'SANCTUM'
    elif 'tools' in path_lower:
        return 'MECHANICUS'
    elif 'scripts' in path_lower:
        return 'ADMINISTRATUM'
    elif 'tests' in path_lower:
        return 'INQUISITION'
    else:
        return 'UNASSIGNED'
```

## Проверки

### Обязательные проверки
```bash
# 1. Компиляция
python3 -m py_compile TOOLS/scriptorium_register_v0_1.py

# 2. Dry-run
python3 TOOLS/scriptorium_register_v0_1.py \
    --inventory CURRENT_STATE/INVENTORY_20260514/CURRENT_TRUTH_INVENTORY.json \
    --dry-run --verbose

# 3. Валидация сгенерированных записей
python3 -c "
import json
from jsonschema import validate
schema = json.load(open('schemas/scriptorium_entry_v0_1.schema.json'))
# validate each entry
"

# 4. Apply
python3 TOOLS/scriptorium_register_v0_1.py \
    --inventory CURRENT_STATE/INVENTORY_20260514/CURRENT_TRUTH_INVENTORY.json \
    --apply --verbose

# 5. Валидация обновлённого реестра
python3 -c "import json; json.load(open('REGISTRY/SCRIPT_REGISTRY.json'))"
```

## Критерии успеха
- [ ] Скрипт создан и компилируется
- [ ] Dry-run показывает корректные записи
- [ ] Все записи валидны по схеме
- [ ] Реестр обновлён
- [ ] Receipt создан
- [ ] Coverage ≥ 90%

## Критерии блокировки
- Скрипт не компилируется
- Записи не проходят валидацию
- Реестр становится невалидным JSON

## Ожидаемый Servitor prompt outline

```
TASK: TASK-20260514-SAN-CLEANING-SCRIPTORIUM-FIRST-WAVE-V0_1
GOAL: Register all unregistered scripts in SCRIPTORIUM

STEPS:
1. Read KIRO_PLAN_ADVISOR/SAN_CLEAN_PLAN/TASKS/TASK_04_SCRIPTORIUM/
2. Read CURRENT_STATE/INVENTORY_20260514/CURRENT_TRUTH_INVENTORY.json
3. Create TOOLS/scriptorium_register_v0_1.py
4. Run py_compile
5. Run --dry-run --verbose
6. Review generated entries
7. Run --apply --verbose
8. Validate updated registry
9. Build bundle for PC review

CONSTRAINTS:
- Do NOT commit from VM2
- All entries must validate against schema
- Preserve existing registry entries
```
