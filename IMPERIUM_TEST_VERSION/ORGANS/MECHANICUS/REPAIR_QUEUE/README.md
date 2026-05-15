# MECHANICUS REPAIR QUEUE

## Purpose
Очередь для скриптов/инструментов, требующих ремонта.

## Entry Format

Каждая запись — JSON файл `REPAIR-YYYYMMDD-NNNN.json`:

```json
{
  "repair_id": "REPAIR-20260515-0001",
  "created_at": "2026-05-15T22:00:00+00:00",
  "item": {
    "type": "script",
    "path": "scripts/broken_script.py",
    "name": "broken_script.py"
  },
  "issue": {
    "type": "syntax_error",
    "description": "SyntaxError: invalid syntax at line 42",
    "detected_by": "script_health_check.py",
    "detection_report": "ORGANS/MECHANICUS/REPORTS/script_health_20260515.json"
  },
  "priority": "HIGH",
  "status": "PENDING",
  "assigned_to": null,
  "resolution": null,
  "resolved_at": null
}
```

## Statuses

| Status | Meaning |
|--------|---------|
| PENDING | Ожидает ремонта |
| IN_PROGRESS | Ремонт в процессе |
| RESOLVED | Исправлено |
| WONTFIX | Не будет исправлено (с причиной) |
| DEFERRED | Отложено |

## Priorities

| Priority | Meaning |
|----------|---------|
| CRITICAL | Блокирует работу системы |
| HIGH | Важный скрипт не работает |
| MEDIUM | Скрипт работает с ошибками |
| LOW | Косметические проблемы |

## Workflow

1. `script_health_check.py` находит проблему
2. Создаётся запись в REPAIR_QUEUE/
3. Агент/Owner берёт задачу
4. Исправление → smoke test
5. Статус → RESOLVED
