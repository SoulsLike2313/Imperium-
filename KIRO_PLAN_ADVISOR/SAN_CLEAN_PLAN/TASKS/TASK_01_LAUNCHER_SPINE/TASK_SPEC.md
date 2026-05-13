# TASK 01: Python-First Launcher Spine v0.1

## Метаданные
- task_id: `TASK-20260514-SAN-CLEANING-PYTHON-FIRST-LAUNCHER-SPINE-V0_1`
- priority: P0 — КРИТИЧЕСКИЙ
- platform: VM2 разработка, PC приёмка
- estimated_files: 8
- dependencies: none

## Цель
Заменить ad hoc PowerShell команды в чате на зарегистрированные Python лаунчеры с receipts.

## Входные данные
- `ORGANS/ADMINISTRATUM/REGISTRY/PROMPT_AND_BUNDLE_ROUTE_MAP_V0_1.md`
- `ORGANS/ADMINISTRATUM/REGISTRY/EXTERNAL_CONTEXT_PATHS_V0_1.md`
- `REGISTRY/SCRIPT_REGISTRY.json`

## Файлы для создания

### 1. Core Framework
**Путь:** `TOOLS/imperium_launcher_v0_1.py`
**Содержимое:** См. `CODE_TEMPLATES/imperium_launcher_v0_1.py`

### 2. Fetch Bundle Launcher
**Путь:** `TOOLS/launcher_fetch_bundle_v0_1.py`
**Содержимое:** См. `CODE_TEMPLATES/launcher_fetch_bundle_v0_1.py`

### 3. Apply Bundle Launcher
**Путь:** `TOOLS/launcher_apply_bundle_v0_1.py`
**Содержимое:** См. `CODE_TEMPLATES/launcher_apply_bundle_v0_1.py`

### 4. Commit Push Launcher
**Путь:** `TOOLS/launcher_commit_push_v0_1.py`
**Содержимое:** См. `CODE_TEMPLATES/launcher_commit_push_v0_1.py`

### 5. Sync VM2 Launcher
**Путь:** `TOOLS/launcher_sync_vm2_v0_1.py`
**Содержимое:** См. `CODE_TEMPLATES/launcher_sync_vm2_v0_1.py`

### 6. Route Configuration
**Путь:** `CONFIG/launcher_routes_v0_1.json`
**Содержимое:** См. `CODE_TEMPLATES/launcher_routes_v0_1.json`

### 7. Receipt Schema
**Путь:** `schemas/launcher_receipt_v0_1.schema.json`
**Содержимое:** См. `../SCHEMAS/launcher_receipt_v0_1.schema.json`

### 8. Launcher Registry
**Путь:** `REGISTRY/LAUNCHER_REGISTRY.json`
**Содержимое:** См. `CODE_TEMPLATES/launcher_registry.json`

## Файлы для обновления
- `REGISTRY/SCRIPT_REGISTRY.json` — добавить записи для лаунчеров

## Проверки

### Обязательные проверки
```bash
# 1. Компиляция всех Python файлов
python3 -m py_compile TOOLS/imperium_launcher_v0_1.py
python3 -m py_compile TOOLS/launcher_fetch_bundle_v0_1.py
python3 -m py_compile TOOLS/launcher_apply_bundle_v0_1.py
python3 -m py_compile TOOLS/launcher_commit_push_v0_1.py
python3 -m py_compile TOOLS/launcher_sync_vm2_v0_1.py

# 2. Проверка help
python3 TOOLS/launcher_fetch_bundle_v0_1.py --help
python3 TOOLS/launcher_apply_bundle_v0_1.py --help
python3 TOOLS/launcher_commit_push_v0_1.py --help
python3 TOOLS/launcher_sync_vm2_v0_1.py --help

# 3. Dry-run тест
python3 TOOLS/launcher_fetch_bundle_v0_1.py --task TEST-001 --dry-run --verbose
```

### Чекер
```bash
python3 TOOLS/check_launcher_registry_v0_1.py --repo-root . --human
```

## Критерии успеха
- [ ] 5 лаунчеров созданы
- [ ] Все компилируются
- [ ] Все имеют `--help`
- [ ] Все имеют `--dry-run`
- [ ] Все производят receipts
- [ ] Конфигурация создана
- [ ] Схема создана
- [ ] Реестр создан
- [ ] Чекер проходит

## Критерии блокировки
- Любой лаунчер не компилируется
- Receipt schema невалидна
- Конфигурация невалидна

## Формат bundle для PC
```
TASK-20260514-SAN-CLEANING-PYTHON-FIRST-LAUNCHER-SPINE-V0_1_BUNDLE/
├── MANIFEST.json
├── RECEIPT.json
├── VERDICT.md
├── changed_files/
│   ├── TOOLS/
│   │   ├── imperium_launcher_v0_1.py
│   │   ├── launcher_fetch_bundle_v0_1.py
│   │   ├── launcher_apply_bundle_v0_1.py
│   │   ├── launcher_commit_push_v0_1.py
│   │   └── launcher_sync_vm2_v0_1.py
│   ├── CONFIG/
│   │   └── launcher_routes_v0_1.json
│   ├── schemas/
│   │   └── launcher_receipt_v0_1.schema.json
│   └── REGISTRY/
│       └── LAUNCHER_REGISTRY.json
└── SHA256SUMS.txt
```

## Ожидаемый Servitor prompt outline

```
TASK: TASK-20260514-SAN-CLEANING-PYTHON-FIRST-LAUNCHER-SPINE-V0_1
GOAL: Create Python-first launcher spine to replace ad hoc PowerShell commands

STEPS:
1. Read KIRO_PLAN_ADVISOR/SAN_CLEAN_PLAN/TASKS/TASK_01_LAUNCHER_SPINE/
2. Create TOOLS/imperium_launcher_v0_1.py (base framework)
3. Create TOOLS/launcher_fetch_bundle_v0_1.py
4. Create TOOLS/launcher_apply_bundle_v0_1.py
5. Create TOOLS/launcher_commit_push_v0_1.py
6. Create TOOLS/launcher_sync_vm2_v0_1.py
7. Create CONFIG/launcher_routes_v0_1.json
8. Create schemas/launcher_receipt_v0_1.schema.json
9. Create REGISTRY/LAUNCHER_REGISTRY.json
10. Run py_compile on all Python files
11. Run --help on all launchers
12. Run --dry-run test
13. Update REGISTRY/SCRIPT_REGISTRY.json
14. Build bundle for PC review

CONSTRAINTS:
- Do NOT commit from VM2
- Do NOT modify Sanctum runtime
- All scripts must compile
- All scripts must have --dry-run mode
```
