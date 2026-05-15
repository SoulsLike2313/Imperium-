# INQUISITION

## Назначение
Inquisition — орган аудита. Audit authority, fake-green/stale truth police.

## Статус: TESTED

## Ответственности

### Backend Face
- Audit authority
- Fake-green detection
- Stale truth detection
- Evidence validation

### Frontend Face
- Audit verdicts dashboard
- Blocker list
- Evidence drilldown

### Support Face
- Fake-green scanners
- Stale truth detectors
- Evidence validators

## Скрипты

| Скрипт | Назначение |
|--------|------------|
| `fake_green_detector.py` | Детектор fake PASS |
| `stale_truth_detector.py` | Детектор устаревших данных |
| `full_audit.py` | Полный аудит |

## Команды

```powershell
# Full audit
py -3 ORGANS\INQUISITION\SCRIPTS\full_audit.py --repo-root E:\IMPERIUM

# Run audit loop
.\ORGANS\INQUISITION\RUN_AUDIT.ps1
```

## Warning Budget

- fake_green_budget: 0 (zero tolerance)
- stale_truth_budget: 10 (acceptable for legacy)
- missing_evidence_budget: 0 (zero tolerance)
