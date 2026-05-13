# ACT5 PREFIRE WARNING BUDGET V0.1

## Что создано

- `REGISTRY/WARNING_BUDGET.json` — machine-readable бюджет и классификация warning/fake-green политики.
- `DOCS/WARNING_BUDGET_POLICY_V0_1.md` — русскоязычная политика и semantics.
- `TOOLS/check_warning_budget_v0_1.py` — policy checker с verdict-разделами PASS/WARN/BLOCKED.
- Обновлены `CURRENT_STATE/NEXT_ATOMIC_STEP.md` и `CURRENT_STATE/ARC5_PREFIRE_CURRENT_TRUTH_20260513.json`.
- При необходимости обновлён `REGISTRY/SCRIPT_REGISTRY.json` для регистрации нового checker.

## Как запустить checker

```bash
python3 -m py_compile TOOLS/check_warning_budget_v0_1.py
python3 TOOLS/check_warning_budget_v0_1.py
python3 TOOLS/check_warning_budget_v0_1.py --json
```

## Что намеренно не решается в этом шаге

- Не выполняется массовая чистка legacy warning flood.
- Не запускается Inquisition execution.
- Не меняется READY_FOR_AGENT на true.
- Не выполняется Sanctum rewrite.

## Как это помогает Step 3 (Advisory Ingest)

Step 3 получает явные blocker rules: advisory не становится execution authority напрямую.
Это снижает риск архитектурного дрейфа и делает модернизацию task/stage решений доказуемой.

## Как это поддержит Inquisition позже

Inquisition v0.1 может принять warning classes как стартовый audit taxonomy.
Это даст единый язык для fake-green detection, budget drift и readiness блокировок.

## Почему assets остаются Step 7

Visual factory и asset-поток не должен смешиваться с governance-шагом.
Step 2 фиксирует policy-контур; Step 7 остаётся отдельной фазой после prefire-гейтов.
