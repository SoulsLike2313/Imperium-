# TASK SEQUENCE — Строгий порядок выполнения

## Обзор последовательности

```
TASK 1: Python-First Launcher Spine v0.1
    ↓
TASK 2: Address Rewrite Implementation v0.1
    ↓
TASK 3: Current Truth Inventory v0.1
    ↓
TASK 4: SCRIPTORIUM First Registration Wave v0.1
    ↓
TASK 5: ARSENAL First Registration Wave v0.1
    ↓
TASK 6: MECHANICUS Formalization v0.1
    ↓
TASK 7: Warning Budget Classification v0.1
    ↓
TASK 8: Backend Truth Dashboard Data v0.1
```

## Детали задач

### TASK 1: Python-First Launcher Spine v0.1
- **Цель**: Заменить ad hoc PowerShell команды на Python лаунчеры с receipts
- **Приоритет**: P0 — КРИТИЧЕСКИЙ
- **Платформа**: VM2 разработка, PC приёмка
- **Папка**: `TASKS/TASK_01_LAUNCHER_SPINE/`
- **Вопрос**: `QUESTIONS/Q01_LAUNCHER_SPINE.md`

### TASK 2: Address Rewrite Implementation v0.1
- **Цель**: Обновить 20 must_update_soon скриптов на новые пути
- **Приоритет**: P0 — КРИТИЧЕСКИЙ
- **Платформа**: VM2 разработка, PC приёмка
- **Папка**: `TASKS/TASK_02_ADDRESS_REWRITE/`
- **Вопрос**: `QUESTIONS/Q02_ADDRESS_REWRITE.md`
- **Зависимость**: После TASK 1 (нужны лаунчеры для тестирования)

### TASK 3: Current Truth Inventory v0.1
- **Цель**: Полная read-only инвентаризация всех скриптов, инструментов, сирот
- **Приоритет**: P1 — ВЫСОКИЙ
- **Платформа**: VM2 или PC
- **Папка**: `TASKS/TASK_03_CURRENT_TRUTH_INVENTORY/`
- **Вопрос**: `QUESTIONS/Q03_CURRENT_TRUTH_INVENTORY.md`
- **Зависимость**: После TASK 2 (пути должны быть исправлены)

### TASK 4: SCRIPTORIUM First Registration Wave v0.1
- **Цель**: Зарегистрировать все незарегистрированные скрипты
- **Приоритет**: P1 — ВЫСОКИЙ
- **Платформа**: VM2 разработка, PC приёмка
- **Папка**: `TASKS/TASK_04_SCRIPTORIUM/`
- **Вопрос**: `QUESTIONS/Q04_SCRIPTORIUM_REGISTRY.md`
- **Зависимость**: После TASK 3 (нужен inventory)

### TASK 5: ARSENAL First Registration Wave v0.1
- **Цель**: Зарегистрировать все внешние инструменты
- **Приоритет**: P1 — ВЫСОКИЙ
- **Платформа**: PC и VM2
- **Папка**: `TASKS/TASK_05_ARSENAL/`
- **Вопрос**: `QUESTIONS/Q05_ARSENAL_REGISTRY.md`
- **Зависимость**: После TASK 3 (нужен inventory)

### TASK 6: MECHANICUS Formalization v0.1
- **Цель**: Создать ORGAN_CONTRACT.json для MECHANICUS
- **Приоритет**: P1 — ВЫСОКИЙ
- **Платформа**: VM2 разработка, PC приёмка
- **Папка**: `TASKS/TASK_06_MECHANICUS/`
- **Зависимость**: После TASK 4 и TASK 5 (нужны реестры)

### TASK 7: Warning Budget Classification v0.1
- **Цель**: Классифицировать warnings как legacy vs new
- **Приоритет**: P2 — СРЕДНИЙ
- **Платформа**: VM2 или PC
- **Папка**: `TASKS/TASK_07_WARNING_BUDGET/`
- **Вопрос**: `QUESTIONS/Q06_WARNING_BUDGET.md`
- **Зависимость**: После TASK 6

### TASK 8: Backend Truth Dashboard Data v0.1
- **Цель**: Создать data model для dashboard
- **Приоритет**: P2 — СРЕДНИЙ
- **Платформа**: VM2 разработка, PC приёмка
- **Папка**: `TASKS/TASK_08_DASHBOARD_DATA/`
- **Вопрос**: `QUESTIONS/Q07_DASHBOARD_DATA.md`
- **Зависимость**: После TASK 7

## Критерии завершения арки

| Критерий | Порог |
|----------|-------|
| Script registration coverage | ≥ 90% |
| Tool registration coverage | ≥ 80% |
| Stale address count | 0 |
| Launcher coverage | 5 core launchers |
| MECHANICUS contract | EXISTS |
| Warning budget | DEFINED |
| Dashboard data | GENERATED |
