# TRUTH SPINE

## Назначение
Truth Spine — центральный компонент для управления истинностью данных в системе.

**Принцип:** PASS только с evidence + fresh timestamp. NO fake green.

## Компоненты

| Файл | Назначение | Статус |
|------|------------|--------|
| `truth_state_checker.py` | Проверка truth state | IMPLEMENTED |
| `freshness_validator.py` | Валидация свежести evidence | IMPLEMENTED |
| `truth_aggregator.py` | Агрегация truth state по компонентам | IMPLEMENTED |
| `TRUTH_STATE_SCHEMA.json` | Схема truth state | IMPLEMENTED |

## Использование

```powershell
# Проверить truth state файла
py -3 TRUTH_SPINE\truth_state_checker.py --file <path>

# Валидировать свежесть
py -3 TRUTH_SPINE\freshness_validator.py --receipts-dir RECEIPTS

# Агрегировать truth state
py -3 TRUTH_SPINE\truth_aggregator.py --output REPORTS\truth_aggregate.json
```

## Truth Semantics

| Status | Требования |
|--------|------------|
| PASS | evidence exists + fresh + exit_code=0 |
| PASS_WITH_WARNINGS | critical PASS + warnings documented |
| PARTIAL | some checks PASS, some not run |
| FAIL | exit_code != 0 OR assertion failed |
| UNKNOWN | check not run OR indeterminate |
| STALE | evidence older than threshold |
| NOT_IMPLEMENTED | feature does not exist |

## Anti-patterns

- PASS_ALL_SILENT — claiming PASS without running all checks
- STALE_AS_FRESH — using old evidence without STALE flag
- FAIL_HIDDEN — ignoring FAIL results
- PARTIAL_AS_PASS — claiming PASS when only some checks run
