# WARNING BUDGET POLICY V0.1

## Зачем нужен warning budget

Warning budget нужен, чтобы прекратить режим неуправляемого `PASS_WITH_WARNINGS` и отделить старый долг от новых рисков.
Цель шага — формализовать правило: legacy-долг фиксируется и сопровождается, а новые критические предупреждения не проходят в зелёный статус.

## Почему мы не чиним весь legacy прямо сейчас

Полный ремонт warning flood в одном шаге приведёт к хаосу и fake progress.
Act 5 Prefire требует сначала governance-уровень: классификация, бюджеты, blocker-правила и доказуемые verdict semantics.

## Legacy debt vs new warnings

- Legacy debt: уже существующие предупреждения, накопленные до текущего шага.
- New warnings: предупреждения, внесённые текущим изменением или новым execution-path.
- Политика: legacy долг отслеживается baseline-моделью, новые предупреждения проходят только по budget/классификации.

## Verdict semantics

- `PASS`: обязательные проверки пройдены, blockers нет, budget не превышен, evidence приложен.
- `PASS_WITH_WARNINGS`: blockers нет, но предупреждения есть; предупреждения обязаны быть классифицированы.
- `PASS_WITH_LEGACY_DEBT`: текущий шаг корректен, остался только старый долг, новых блокирующих рисков нет.
- `PASS_WITH_NEW_WARNINGS`: допустим только для низкорисковых классифицированных предупреждений с явным принятием.
- `FAIL`: проверка провалена, требуется исправление.
- `BLOCKED`: безопасное продолжение невозможно, причина должна быть явно указана.

## Immediate blocker types

Немедленные блокеры:
- `FAKE_GREEN_RISK`
- `READY_FOR_AGENT_POLICY`
- `ADVISORY_AS_AUTHORITY`
- `AUTO_DELETE_OR_CLEANUP_RISK`
- `BUNDLE_INTAKE_SCOPE`
- `SECURITY_SECRET_RISK`

## Как это предотвращает fake green

Политика запрещает PASS без evidence и запрещает перевод `READY_FOR_AGENT` в true без полного gate-пакета.
Любая попытка обойти advisory promotion path или скрыть blocker-класс автоматически переводит verdict в `BLOCKED`.

## Как это влияет на Act 5 Prefire

Step 2 не запускает execution.
Step 2 задаёт guardrails для Step 3 (Advisory Ingest + Modernization) и следующих шагов, чтобы новые изменения не утонули в warning flood.

## Как использовать в будущем Inquisition

Inquisition должен использовать классы и blocker rules как входной контракт:
- сравнивать baseline vs new warnings;
- блокировать fake-green / auto-delete / advisory-as-authority;
- выводить прозрачные PASS/WARN/BLOCKED отчёты.

## Что пока не завершено

- Полный инвентарь legacy warning baseline (`MEASURED_LATER`).
- Глубокая автоматическая классификация всех исторических предупреждений.
- Полная интеграция action registry и командного gateway в каждой UI-действии.
- Visual Factory остаётся Step 7 и не переносится в этот шаг.
