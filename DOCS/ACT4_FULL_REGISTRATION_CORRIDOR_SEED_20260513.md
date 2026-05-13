# ACT4 Full Registration Corridor Seed (2026-05-13)

## Назначение Act 4
Act 4 строит первый машинно-проверяемый коридор полной регистрации работ IMPERIUM:
GENERAL_TASK -> TASK candidate -> review export -> advisory response ingest -> modernization -> stage map -> stage review -> stage modernization -> READY_FOR_AGENT gate.

## Почему Act 4 идет после Act 3
Act 3 дал базу адресов, truth-приоритетов, capability-слоя и warning/stale baseline.
Act 4 использует эту базу как зависимость, чтобы этапы регистрации проверялись фактами, а не только текстовыми заявками.

## Роль Astronomicon в коридоре
ASTRONOMICON выступает владельцем коридора регистрации:
- ведет registry-файлы фаз;
- хранит TASK_CANDIDATES, REVIEW_PACKS, STAGE_MAPS и READY_FOR_AGENT gate записи;
- обеспечивает правило no-fake-green через machine checks.

## Raw advisory vs doctrine vs modernization
- Raw advisory: технический внешний вход, не доктрина до формального согласования.
- Doctrine/accepted direction: только после Owner decision и reconciliation.
- Modernization: фиксируем, что принято/отклонено из advisory и почему.
- READY_FOR_AGENT: разрешается только при наличии доказательств, required checks и owner gate.

## Dry-run цель для Act 5
В этом seed создается dry-run кандидат для будущей задачи:
`TASK-CANDIDATE-20260513-BUILD-INQUISITION-V0_1-SELF-DESCRIPTIVE-ORGAN`.
Это только регистрация и review-коридор; реализация Inquisition v0.1 в Act 4 не выполняется.

## No fake green правила для READY_FOR_AGENT
READY_FOR_AGENT запрещен, если отсутствует хотя бы одно из:
- ingest advisory responses;
- task modernization;
- approved stage map;
- required checks/receipts;
- явное Owner approval.

## Что намеренно НЕ сделано в этом seed
- Не начат Act 5.
- Не создана реализация Inquisition organ contract/runtime/checkers.
- Не автоматизированы commit/push/sync действия.
- Не внедрена полная оркестрация всех циклов; только минимальный проверяемый backbone.
