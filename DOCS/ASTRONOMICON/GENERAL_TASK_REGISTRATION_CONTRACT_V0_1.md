# GENERAL_TASK_REGISTRATION_CONTRACT_V0_1

Статус: active v0.1 foundation contract.

## Цель

Зафиксировать минимальный канонический контракт регистрации `GENERAL_TASK` до декомпозиции в `TASK` и `STAGE`.

## Обязательное содержание GENERAL_TASK

- `general_task_id`, `title`
- `source_file`, `source_sha256`
- `git_head`, `tree_url`, `blob_url`
- `owner_decision_status`
- `registration_status`
- `decomposition_status`
- `technical_review_inputs`
- `task_candidate_status`
- `created_at_utc`, `created_by`, `notes`

## Ключевые правила

- Регистрация `GENERAL_TASK` не равна разрешению на исполнение.
- Advisory/review inputs не являются canon автоматически.
- Любая advisory-информация становится рабочим контрактом только после reconciliation и явной формализации.
- Нельзя заявлять `READY_FOR_AGENT` на уровне GENERAL_TASK.
- No fake green.

## Разрешенные статусы регистрации

- `REGISTERED_NOT_DECOMPOSED`
- `DECOMPOSED_TO_TASK_CANDIDATES`
- `UNDER_REVIEW`
- `REFINED`
- `BLOCKED`
- `ARCHIVED`

## Выход из этого контракта

Следующий этап — создание `TASK_CANDIDATES_DRAFT` и экспорт на technical review/advisory цикл.
