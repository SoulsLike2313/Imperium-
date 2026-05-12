# DECOMPOSITION_AND_REVIEW_LOOP_V0_1

Статус: active v0.1 loop outline.

## Контур цикла

1. `GENERAL_TASK` зарегистрирован.
2. Формируются `TASK` кандидаты (`DRAFT_TASK_CANDIDATES_NOT_OWNER_APPROVED`).
3. Кандидаты экспортируются в universal technical review/advisory формат.
4. Получаются структурированные `technical_review_response`.
5. Выполняется модернизация/уточнение TASK-кандидатов.
6. Для уточненных TASK создается `STAGE_MAP`.
7. `STAGE_MAP` снова экспортируется на technical review.
8. После stage-modernization TASK может перейти в `REGISTERED_READY_FOR_AGENT`.

## Исторически выполненные задачи

Если часть работ уже выполнена до полного red-team/registration цикла, это маркируется явно:

- `DONE_BEFORE_FULL_REGISTRATION_CYCLE`
- `DONE_BEFORE_FULL_RED_TEAM_CYCLE`
- `PARTIALLY_DONE_NEEDS_CONTRACT_BACKFILL`

Такие статусы не отменяют необходимость контрактного backfill.

## Advisory inputs

- Advisory input = инженерный сигнал/критика/рекомендации.
- Advisory input не равен канону.
- До reconciliation любой advisory имеет режим `NON_CANON_UNTIL_RECONCILED` или `ADVISORY_ONLY`.

## No fake green

- Нельзя пропускать review loop из-за того, что «уже работает вручную».
- Нельзя назначать `REGISTERED_READY_FOR_AGENT` без stage-pass criteria и review следа.
