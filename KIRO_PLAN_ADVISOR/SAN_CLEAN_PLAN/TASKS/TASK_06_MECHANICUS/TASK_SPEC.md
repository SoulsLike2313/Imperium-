# TASK 06: MECHANICUS Formalization v0.1

## Метаданные
- task_id: `TASK-20260514-SAN-CLEANING-MECHANICUS-FORMALIZATION-V0_1`
- priority: P1 — ВЫСОКИЙ
- platform: VM2 разработка, PC приёмка
- estimated_files: 3-5
- dependencies: TASK_04 (SCRIPTORIUM), TASK_05 (ARSENAL)

## Цель
Создать формальный ORGAN_CONTRACT.json для MECHANICUS органа.

## Проблема
MECHANICUS — орган отвечающий за инструменты и скрипты — не имеет формального контракта.
Это создаёт неясность в ответственности и границах.

## Входные данные
- `REGISTRY/SCRIPT_REGISTRY.json` — скрипты под MECHANICUS
- `REGISTRY/ARSENAL_REGISTRY.json` — инструменты
- `REGISTRY/LAUNCHER_REGISTRY.json` — лаунчеры
- `ORGANS/MECHANICUS/` — текущая структура

## Выходные данные
- `ORGANS/MECHANICUS/ORGAN_CONTRACT.json`
- `ORGANS/MECHANICUS/MECHANICUS_MANIFEST.md`
- Обновлённый `REGISTRY/ORGAN_REGISTRY.json`

## Структура ORGAN_CONTRACT.json

```json
{
  "schema_version": "organ_contract_v0_1",
  "organ_id": "MECHANICUS",
  "name": "Adeptus Mechanicus",
  "description": "Орган отвечающий за инструменты, скрипты и техническую инфраструктуру",
  "created": "2026-05-14",
  "updated": "2026-05-14",
  
  "responsibilities": [
    "Управление SCRIPTORIUM (реестр скриптов)",
    "Управление ARSENAL (реестр инструментов)",
    "Управление LAUNCHER системой",
    "Техническая валидация (py_compile, lint)",
    "Инфраструктурные скрипты"
  ],
  
  "boundaries": {
    "owns": [
      "TOOLS/*",
      "REGISTRY/SCRIPT_REGISTRY.json",
      "REGISTRY/ARSENAL_REGISTRY.json",
      "REGISTRY/LAUNCHER_REGISTRY.json",
      "schemas/*_v0_1.schema.json"
    ],
    "does_not_own": [
      "SANCTUM/*",
      "scripts/verify_repo.py",
      "ORGANS/ADMINISTRATUM/*"
    ]
  },
  
  "interfaces": {
    "provides": [
      {
        "name": "script_registration",
        "description": "Регистрация скриптов в SCRIPTORIUM",
        "entry_point": "TOOLS/scriptorium_register_v0_1.py"
      },
      {
        "name": "tool_registration",
        "description": "Регистрация инструментов в ARSENAL",
        "entry_point": "TOOLS/arsenal_register_v0_1.py"
      },
      {
        "name": "launcher_framework",
        "description": "Framework для лаунчеров",
        "entry_point": "TOOLS/imperium_launcher_v0_1.py"
      }
    ],
    "requires": [
      {
        "name": "git",
        "provider": "ARSENAL",
        "tool_id": "TOOL-GIT"
      },
      {
        "name": "python3",
        "provider": "ARSENAL",
        "tool_id": "TOOL-PYTHON3"
      }
    ]
  },
  
  "quality_gates": {
    "all_scripts_compile": {
      "description": "Все скрипты должны проходить py_compile",
      "checker": "scripts/verify_repo.py",
      "threshold": "100%"
    },
    "script_registration_coverage": {
      "description": "Процент зарегистрированных скриптов",
      "threshold": "≥90%"
    },
    "tool_registration_coverage": {
      "description": "Процент зарегистрированных инструментов",
      "threshold": "≥80%"
    }
  },
  
  "status": "active",
  "maturity": "v0.1"
}
```

## Алгоритм

### Шаг 1: Анализ текущего состояния
```python
# Загрузить реестры
scripts = load_json('REGISTRY/SCRIPT_REGISTRY.json')
arsenal = load_json('REGISTRY/ARSENAL_REGISTRY.json')
launchers = load_json('REGISTRY/LAUNCHER_REGISTRY.json')

# Найти скрипты принадлежащие MECHANICUS
mechanicus_scripts = [s for s in scripts['scripts'] if s['owner'] == 'MECHANICUS']
```

### Шаг 2: Генерация контракта
```python
contract = {
    'schema_version': 'organ_contract_v0_1',
    'organ_id': 'MECHANICUS',
    # ... заполнить по шаблону выше
}
```

### Шаг 3: Генерация манифеста
```markdown
# MECHANICUS Manifest

## Обзор
MECHANICUS — орган отвечающий за техническую инфраструктуру IMPERIUM.

## Владение
- Скриптов: {count}
- Инструментов: {count}
- Лаунчеров: {count}

## Интерфейсы
...
```

### Шаг 4: Обновление ORGAN_REGISTRY
```python
organ_registry = load_json('REGISTRY/ORGAN_REGISTRY.json')
organ_registry['organs']['MECHANICUS']['contract_path'] = 'ORGANS/MECHANICUS/ORGAN_CONTRACT.json'
organ_registry['organs']['MECHANICUS']['status'] = 'active'
organ_registry['organs']['MECHANICUS']['updated'] = today()
```

## Файлы для создания

### 1. Contract Generator Script
**Путь:** `TOOLS/mechanicus_contract_generator_v0_1.py`

### 2. Organ Contract
**Путь:** `ORGANS/MECHANICUS/ORGAN_CONTRACT.json`

### 3. Manifest
**Путь:** `ORGANS/MECHANICUS/MECHANICUS_MANIFEST.md`

## Проверки

### Обязательные проверки
```bash
# 1. Компиляция генератора
python3 -m py_compile TOOLS/mechanicus_contract_generator_v0_1.py

# 2. Генерация контракта
python3 TOOLS/mechanicus_contract_generator_v0_1.py --dry-run --verbose
python3 TOOLS/mechanicus_contract_generator_v0_1.py --apply --verbose

# 3. Валидация JSON
python3 -c "import json; json.load(open('ORGANS/MECHANICUS/ORGAN_CONTRACT.json'))"

# 4. Проверка ORGAN_REGISTRY
python3 -c "import json; json.load(open('REGISTRY/ORGAN_REGISTRY.json'))"
```

## Критерии успеха
- [ ] Генератор создан и компилируется
- [ ] ORGAN_CONTRACT.json создан и валиден
- [ ] MECHANICUS_MANIFEST.md создан
- [ ] ORGAN_REGISTRY.json обновлён
- [ ] Receipt создан

## Критерии блокировки
- Генератор не компилируется
- Контракт невалидный JSON
- Конфликт с существующими данными

## Ожидаемый Servitor prompt outline

```
TASK: TASK-20260514-SAN-CLEANING-MECHANICUS-FORMALIZATION-V0_1
GOAL: Create formal ORGAN_CONTRACT for MECHANICUS

STEPS:
1. Read KIRO_PLAN_ADVISOR/SAN_CLEAN_PLAN/TASKS/TASK_06_MECHANICUS/
2. Read REGISTRY/SCRIPT_REGISTRY.json
3. Read REGISTRY/ARSENAL_REGISTRY.json
4. Read REGISTRY/LAUNCHER_REGISTRY.json
5. Create TOOLS/mechanicus_contract_generator_v0_1.py
6. Run py_compile
7. Run --dry-run --verbose
8. Run --apply --verbose
9. Validate ORGANS/MECHANICUS/ORGAN_CONTRACT.json
10. Validate REGISTRY/ORGAN_REGISTRY.json
11. Build bundle for PC review

CONSTRAINTS:
- Do NOT commit from VM2
- Preserve existing ORGAN_REGISTRY entries
- Contract must be valid JSON
```
