# Astra Pipeline Draft

TASK_ID: `TASK-20260509-ASTRA-UTILITY-BASE-SCRIPTS-V0_1-V1`
STATUS: `ASTRA_ROUTE_DRAFT`
PROFILE: `PC_LOCAL_ROUTE` — PC Local Route
CREATED_AT: `2026-05-09T13:15:58`

## Owner task

Нужно подготовить базовые скрипты Астрономикона v0.1 для локальной работы IMPERIUM.

Цель:
Создать минимальный набор скриптов, которые помогают Owner/Logos формировать task route внутри Astronomicon.

Нужно получить:
1. Скрипт создания ASTRA_TASK_RECORD из текстовой задачи Owner.
2. Скрипт создания STAGE_MAP.
3. Скрипт проверки STAGE_MAP.
4. Скрипт экспорта pipeline draft в md/json.
5. Скрипт проверки, что task route не заявляет fake green, organs implemented, THRONE, E2E, VM2 или watchers без явного разрешения.

Границы scope:
- не реализовывать живой орган;
- не запускать E2E;
- не трогать VM2;
- не трогать THRONE;
- не создавать watchers;
- не создавать background automation;
- не переносить файлы;
- не удалять файлы;
- не объявлять Astronomicon implemented;
- не объявлять CONTINUITY_GREEN.

Ожидаемый результат:
- новые скрипты лежат в E:\IMPERIUM\ORGANS\ASTRONOMICON\SCRIPTS;
- каждый скрипт поддерживает --help;
- есть README по использованию;
- есть validation report;
- есть receipt;
- есть artifact bundle;
- Explorer должен видеть новые файлы.

Дополнительное требование:
Задача должна идти stage-by-stage:
1. Astra формирует смысловую карту задачи.
2. Administratum задает адреса чтения/записи и policy refs.
3. Mechanicus задает список скриптов и проверок.
4. Inquisition проверяет дрифт, fake green, forbidden refs и опасные действия.
5. PC Servitor выполняет локальное создание скриптов.
6. Speculum потом проверяет bundle.

## Scope analysis

- word_count: `191`
- scope_width: `MEDIUM`
- detected_risk_terms: `vm2, throne, e2e, delete, watchers, inquisition, mechanicus, administratum, astronomicon`

### Scope blockers
- VM2 mentioned but selected pipeline does not allow VM2.
- THRONE mentioned; THRONE remains blocked.
- Deletion language detected; Inquisition deletion proposal + Owner approval required.
- Watcher/autosync language detected; background automation forbidden.

### Scope tightening suggestions
- Scope можно использовать для первичного route draft.

## Policy extension required
- STAGE_ID_POLICY should include INQUISITION-STAGE-### before strict validator enforcement.

## Stage map

### 1. `ASTRA-STAGE-001` — Смысловая карта задачи

- organ: `ASTRONOMICON`
- purpose: Зафиксировать цель, scope, stage map, pass criteria и blockers.
- status: `PLANNED`

Pass criteria:
- Owner goal сохранён без расширения scope.
- Stage map создан.
- Pass criteria заданы.
- Next allowed action задан.
- Blockers перечислены.
- Stage receipt создан.
- Stage validation report создан.
- No fake green claims.
- No THRONE contact.
- No watcher/background automation.

Stage loop:
- do_stage: `True`
- run_validation: `True`
- if_pass: `write_STAGE_PASS_RECEIPT_and_continue`
- if_fail_safe_repair: `repair_report_or_local_artifact_then_rerun_validation`
- if_fail_semantic_or_destructive: `write_BLOCKED_RECEIPT_and_stop_for_Owner`
- max_safe_repair_attempts: `2`

### 2. `ADMINISTRATUM-STAGE-001` — Read-first и адреса

- organ: `ADMINISTRATUM`
- purpose: Определить что читать, куда писать, какие policies и receipts нужны.
- status: `PLANNED`

Pass criteria:
- Read-first route создан.
- Policy refs перечислены.
- Output root задан.
- Receipt requirements заданы.
- No latest-bundle logic.
- Stage receipt создан.
- Stage validation report создан.
- No fake green claims.
- No THRONE contact.
- No watcher/background automation.

Stage loop:
- do_stage: `True`
- run_validation: `True`
- if_pass: `write_STAGE_PASS_RECEIPT_and_continue`
- if_fail_safe_repair: `repair_report_or_local_artifact_then_rerun_validation`
- if_fail_semantic_or_destructive: `write_BLOCKED_RECEIPT_and_stop_for_Owner`
- max_safe_repair_attempts: `2`

### 3. `MECHANICUS-STAGE-001` — Tool/script route

- organ: `MECHANICUS`
- purpose: Выдать список локальных скриптов, validators и test commands.
- status: `PLANNED`

Pass criteria:
- Allowed scripts/tools перечислены.
- Validator commands перечислены.
- Tool risk classification указана.
- No unsafe script execution.
- Stage receipt создан.
- Stage validation report создан.
- No fake green claims.
- No THRONE contact.
- No watcher/background automation.

Stage loop:
- do_stage: `True`
- run_validation: `True`
- if_pass: `write_STAGE_PASS_RECEIPT_and_continue`
- if_fail_safe_repair: `repair_report_or_local_artifact_then_rerun_validation`
- if_fail_semantic_or_destructive: `write_BLOCKED_RECEIPT_and_stop_for_Owner`
- max_safe_repair_attempts: `2`

### 4. `INQUISITION-STAGE-001` — Preflight heresy check

- organ: `INQUISITION`
- purpose: Проверить route на дрифт, дубли, fake green, latest/throne/watchers/delete.
- status: `PLANNED`

Pass criteria:
- Drift/duplicate/fake-green checks выполнены.
- Legacy stage IDs проверены.
- Placeholder hashes проверены.
- Deletion only as proposal.
- Stage receipt создан.
- Stage validation report создан.
- No fake green claims.
- No THRONE contact.
- No watcher/background automation.

Stage loop:
- do_stage: `True`
- run_validation: `True`
- if_pass: `write_STAGE_PASS_RECEIPT_and_continue`
- if_fail_safe_repair: `repair_report_or_local_artifact_then_rerun_validation`
- if_fail_semantic_or_destructive: `write_BLOCKED_RECEIPT_and_stop_for_Owner`
- max_safe_repair_attempts: `2`

### 5. `PC-STAGE-001` — Локальное выполнение

- organ: `PC_SERVITOR`
- purpose: Выполнить задачу локально по route, без VM2/THRONE/E2E.
- status: `PLANNED`

Pass criteria:
- Stage выполнен по утверждённому route.
- Validation PASS before next stage.
- Safe repair attempted only if bounded.
- BLOCKED_RECEIPT created if semantic conflict.
- Stage receipt создан.
- Stage validation report создан.
- No fake green claims.
- No THRONE contact.
- No watcher/background automation.

Stage loop:
- do_stage: `True`
- run_validation: `True`
- if_pass: `write_STAGE_PASS_RECEIPT_and_continue`
- if_fail_safe_repair: `repair_report_or_local_artifact_then_rerun_validation`
- if_fail_semantic_or_destructive: `write_BLOCKED_RECEIPT_and_stop_for_Owner`
- max_safe_repair_attempts: `2`

### 6. `PC-STAGE-002` — Packaging and proof

- organ: `PC_SERVITOR`
- purpose: Собрать reports, receipts, manifest, hashes, final bundle.
- status: `PLANNED`

Pass criteria:
- Stage выполнен по утверждённому route.
- Validation PASS before next stage.
- Safe repair attempted only if bounded.
- BLOCKED_RECEIPT created if semantic conflict.
- Stage receipt создан.
- Stage validation report создан.
- No fake green claims.
- No THRONE contact.
- No watcher/background automation.

Stage loop:
- do_stage: `True`
- run_validation: `True`
- if_pass: `write_STAGE_PASS_RECEIPT_and_continue`
- if_fail_safe_repair: `repair_report_or_local_artifact_then_rerun_validation`
- if_fail_semantic_or_destructive: `write_BLOCKED_RECEIPT_and_stop_for_Owner`
- max_safe_repair_attempts: `2`

### 7. `SPECULUM-STAGE-001` — Hard review

- organ: `LOGOS_SPECULUM`
- purpose: Speculum проверяет evidence bundle.
- status: `PLANNED`

Pass criteria:
- Bundle + sidecar provided.
- Evidence reviewed.
- Verdict issued.
- Next action or blockers listed.

Stage loop:
- do_stage: `True`
- run_validation: `True`
- if_pass: `write_STAGE_PASS_RECEIPT_and_continue`
- if_fail_safe_repair: `repair_report_or_local_artifact_then_rerun_validation`
- if_fail_semantic_or_destructive: `write_BLOCKED_RECEIPT_and_stop_for_Owner`
- max_safe_repair_attempts: `2`

## Forbidden activations
- NO_THRONE_CONTACT
- NO_E2E_RUN_UNLESS_EXPLICIT_STAGE
- NO_WATCHERS
- NO_BACKGROUND_AUTOMATION
- NO_DELETE_WITHOUT_OWNER_APPROVAL
- NO_ORGAN_IMPLEMENTED_CLAIM
- NO_CONTINUITY_GREEN_CLAIM
- NO_LATEST_BUNDLE_LOGIC

## Next allowed action
- action: `OWNER_REVIEW_ASTRA_ROUTE`
- then: `ADMINISTRATUM_READ_ROUTE_BUILD`
