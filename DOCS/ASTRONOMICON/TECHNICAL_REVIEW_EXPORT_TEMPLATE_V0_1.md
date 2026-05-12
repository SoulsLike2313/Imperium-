# TECHNICAL_REVIEW_EXPORT_TEMPLATE_V0_1

Универсальный шаблон для external/internal technical reviewer или advisory reviewer.

---

## 1. Target object

- `target_type`: GENERAL_TASK / TASK / STAGE_MAP
- `target_id`:
- `registration_status`:
- `decomposition_status`:

## 2. Git truth

- `git_head`:
- `tree_url`:
- `blob_urls`:
- `commit_count`:
- `latest_commit_oneline`:

## 3. Source files

- Основной source file:
- Source sha256:
- Связанные контракты/схемы:
- Связанные evidence paths:

## 4. Current status

- Что уже формализовано:
- Что еще draft:
- Какие поля блокируют переход в следующий статус:

## 5. Known constraints

- No commit/no push (если применимо):
- Forbidden zones:
- Allowed scope:
- No fake green rules:

## 6. Already done

- Что уже завершено исторически:
- Какие элементы имеют статус `DONE_BEFORE_FULL_REGISTRATION_CYCLE` / `DONE_BEFORE_FULL_RED_TEAM_CYCLE`:
- Какие элементы требуют contract backfill:

## 7. Not done

- Отсутствующие контракты:
- Отсутствующие evidence:
- Непокрытые зависимости:

## 8. Allowed scope

- Разрешенные директории/файлы для ревью-предложений:
- Разрешенные типы изменений:

## 9. Forbidden scope

- Нельзя предлагать rewrite архитектуры вне задачи:
- Нельзя предлагать массовый cleanup без отдельного Owner task:
- Нельзя выдавать advisory как canon без reconciliation:

## 10. Required questions

1. Какие blockers должны быть закрыты до следующего статуса?
2. Какие acceptance criteria недостаточно строгие?
3. Какие зависимости/границы нарушены?
4. Как лучше разбить TASK/STAGE без потери контроля?

## 11. Limited free-advisory section

- Reviewer может добавить ограниченные улучшения, не ломающие scope.
- Любая такая рекомендация должна быть отдельно помечена как advisory.

## 12. Required answer format

Ответ должен быть структурирован как `technical_review_response`:

- `response_id`
- `target_type`
- `target_id`
- `reviewer_type`
- `verdict`
- `required_answers`
- `scope_risks`
- `missing_artifacts`
- `dependency_violations`
- `suggested_tightening`
- `suggested_acceptance_criteria`
- `suggested_stage_split`
- `blockers`
- `limited_free_advisory`
- `machine_readable_recommendations`
- `status`

## 13. Re-ingest rule

- Ответ review/advisory не применяется напрямую.
- Сначала response попадает в реестр review inputs/responses.
- Затем выполняется reconciliation и только после этого task/stage modernization.

## 14. No fake green

- Reviewer не должен ставить `ready` без проверки evidence.
- Любой неясный пункт должен быть помечен как blocker/warning, а не скрыт.
