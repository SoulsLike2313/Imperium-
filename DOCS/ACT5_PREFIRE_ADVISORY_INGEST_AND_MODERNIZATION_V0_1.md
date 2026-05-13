# ACT5 PREFIRE Advisory Ingest And Modernization v0.1

## Зачем нужен этот шаг

Step 3 нужен как безопасный мост между сырой advisory-информацией и формальными prefire-записями.
Сырая консультация (Kiro audit) полезна, но не может напрямую запускать выполнение задач.

## Как зарегистрирован Kiro audit

Создана формальная запись:
- `ORGANS/ASTRONOMICON/REGISTRY/ADVISORY_RESPONSES/ADVISORY-RESPONSE-20260513-KIRO-ACT5-PREFIRE-V0_1.json`

Запись фиксирует источник как `ADVISORY_ONLY_NOT_EXECUTION_AUTHORITY`, добавляет repo truth и запрещает прямой execution path.

## Что принято / отклонено / отложено

Принято:
- необходимость current-truth refresh (Step 1);
- необходимость warning budget (Step 2);
- необходимость advisory ingest + modernization до execution;
- strict READY_FOR_AGENT policy;
- перенос visual factory на Step 7.

Отклонено/отложено:
- автоматический READY_FOR_AGENT true;
- giant Sanctum rewrite;
- auto-delete cleanup;
- запуск execution из raw advisory;
- asset stuffing до Step 7.

## Как работает modernization skeleton

Создана запись:
- `ORGANS/ASTRONOMICON/REGISTRY/TASK_MODERNIZATIONS/TASK-MODERNIZATION-20260513-ACT5-PREFIRE-V0_1.json`

Она фиксирует статус `MODERNIZATION_SKELETON_REGISTERED_PENDING_OWNER_APPROVAL`,
держит `act5_execution_ready=false`, `ready_for_agent_status=false`,
и задаёт 10-шаговую prefire-последовательность без запуска исполнения.

## Как получены prefire task candidates

Создан реестр кандидатов:
- `ORGANS/ASTRONOMICON/REGISTRY/ARC5_PREFIRE/ARC5_PREFIRE_PREPARATION_TASKS_20260513.json`

Он содержит 6 формальных кандидатов подготовки (first-four-organs, ACK model, Sanctum action registry,
visual factory minimum Step 7, Inquisition contract, READY_FOR_AGENT gate proof) со статусом
`CANDIDATE_NOT_READY_FOR_EXECUTION`.

## Почему Act 5 execution остаётся заблокирован

- `act5_execution_ready` во всех новых записях = `false`.
- `READY_FOR_AGENT` не повышается и остаётся policy-gated.
- Нет Owner approval на modernization/stage/gate proof.

## Почему READY_FOR_AGENT остаётся false

Переход в true разрешён только после завершения предыдущих шагов,
с доказательствами и явным Owner approval.

## Почему assets остаются Step 7

Visual Factory Minimum намеренно оставлен в Step 7,
чтобы не смешивать governance-prefire слой с визуальным производством.

## Следующий шаг

Рекомендованный следующий шаг после PC acceptance:
- `TASK-20260513-FIRST-FOUR-ORGANS-ACT5-READINESS-V0_1`

Альтернатива только по явному решению Owner:
- `TASK-20260513-WORK-SESSION-ADMINISTRATUM-ACK-V0_1`
