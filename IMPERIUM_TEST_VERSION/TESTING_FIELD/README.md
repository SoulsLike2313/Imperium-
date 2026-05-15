# TESTING_FIELD

## Purpose
Полигон для тестирования кандидатов перед promotion в production.

## Structure

```
TESTING_FIELD/
├── CANDIDATES/           # Кандидаты на тестирование
├── SMOKE_RESULTS/        # Результаты smoke tests (gitignored)
├── SCREENSHOTS/          # Screenshots UI (evidence)
├── PROMOTION_LOG/        # Лог продвижения кандидатов
├── CHECKLISTS/           # Чеклисты для manual testing
└── REPORTS/              # Отчёты о тестировании
```

## Rules

1. **CANDIDATES ISOLATED** — кандидаты не попадают напрямую в production
2. **SMOKE REQUIRED** — каждый кандидат проходит smoke test
3. **SCREENSHOT REQUIRED** — UI кандидаты требуют screenshot
4. **PROMOTION LOGGED** — каждое продвижение записывается в лог
5. **GENERATED GITIGNORED** — SMOKE_RESULTS/ не в git

## Workflow

1. Кандидат → CANDIDATES/
2. Smoke test → SMOKE_RESULTS/
3. Screenshot → SCREENSHOTS/
4. Review → PASS/FAIL
5. PASS → PROMOTION_LOG/ entry → production
6. FAIL → CANDIDATES/ (fix and retry)
