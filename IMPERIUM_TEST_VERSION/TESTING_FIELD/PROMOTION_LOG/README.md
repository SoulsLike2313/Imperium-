# PROMOTION_LOG

## Purpose
Записывает каждое продвижение кандидата из Testing Field в production.

## Entry Format

Каждая запись — JSON файл с именем `PROMO-YYYYMMDD-NNNN.json`:

```json
{
  "entry_id": "PROMO-20260515-0001",
  "timestamp": "2026-05-15T22:00:00+00:00",
  "candidate": {
    "name": "smoke_sanctum.py",
    "type": "script",
    "source_path": "TESTING_FIELD/CANDIDATES/smoke_sanctum.py",
    "version": "0.1"
  },
  "smoke_result": {
    "passed": true,
    "report_path": "TESTING_FIELD/SMOKE_RESULTS/sanctum_smoke_20260515_220000.json",
    "screenshot_path": "TESTING_FIELD/SCREENSHOTS/screenshot_20260515_220000.png"
  },
  "verdict": "PROMOTED",
  "promoted_to": "TESTING_FIELD/SCRIPTS/smoke_sanctum.py",
  "reviewer": "Owner",
  "notes": "First smoke script promoted"
}
```

## Verdicts

| Verdict | Meaning |
|---------|---------|
| PROMOTED | Кандидат прошёл smoke, перемещён в production |
| REJECTED | Кандидат не прошёл smoke, остаётся в CANDIDATES |
| DEFERRED | Кандидат отложен для доработки |

## Rules

1. **NO SILENT PROMOTION** — каждое продвижение записывается
2. **SMOKE REQUIRED** — нет записи без smoke_result
3. **REVIEWER REQUIRED** — кто-то должен подтвердить
4. **IMMUTABLE** — записи не редактируются после создания
