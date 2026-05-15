# TRUTH CONTRACT V1

## Purpose
Defines what constitutes "truth" in IMPERIUM dashboards and reports.

## Core Principles

1. **NO CLAIM WITHOUT EVIDENCE** — каждое утверждение должно иметь доказательство
2. **NO STALE TRUTH** — устаревшие данные помечаются как STALE
3. **SOURCE TRACEABLE** — каждое значение можно проследить до источника
4. **FRESHNESS VISIBLE** — возраст данных виден пользователю

## Truth Claim Structure

Каждое утверждение о состоянии системы должно содержать:

```json
{
  "claim": {
    "type": "status|metric|verdict",
    "value": "PASS|FAIL|number|string",
    "description": "Human-readable description"
  },
  "evidence": {
    "type": "file|command|test|manual",
    "path": "path/to/evidence",
    "hash": "sha256 of evidence (optional)"
  },
  "freshness": {
    "timestamp": "ISO 8601 timestamp",
    "age_seconds": 123,
    "is_stale": false,
    "stale_threshold_seconds": 86400
  },
  "source": {
    "script": "path/to/script.py",
    "command": "command that produced this",
    "git_head": "abc1234"
  }
}
```

## Freshness Rules

| Data Type | Stale Threshold | Reason |
|-----------|-----------------|--------|
| Git HEAD | 0 (always check) | HEAD can change any time |
| Script health | 1 hour | Scripts don't change often |
| Audit report | 24 hours | Daily audit sufficient |
| Registry state | 1 hour | Registry can be updated |
| Dashboard status | 5 minutes | User expects fresh data |

## Staleness Indicators

Dashboard должен показывать:

- 🟢 FRESH — данные актуальны
- 🟡 AGING — данные приближаются к stale threshold
- 🔴 STALE — данные устарели, требуется обновление
- ⚫ UNKNOWN — возраст данных неизвестен

## Evidence Types

| Type | Description | Example |
|------|-------------|---------|
| file | Файл с результатом | `REPORTS/audit_20260515.json` |
| command | Вывод команды | `git status --short` |
| test | Результат теста | `pytest output` |
| manual | Ручная проверка | `Owner verified UI` |
| screenshot | Скриншот UI | `SCREENSHOTS/sanctum_20260515.png` |

## Verification

Для проверки truth claim:

1. Evidence существует по указанному пути
2. Evidence hash совпадает (если указан)
3. Timestamp не старше threshold
4. Source script/command существует
5. Git HEAD совпадает с текущим (если критично)

## Anti-Patterns

❌ **FAKE GREEN**: `{"verdict": "PASS"}` без evidence
❌ **STALE AS FRESH**: Показывать старые данные как актуальные
❌ **UNTRACEABLE**: Значение без source
❌ **MAGIC NUMBER**: Метрика без объяснения откуда взялась
