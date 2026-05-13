# SANCTUM ACTION REGISTRY v0.1

## Зачем нужен action registry
На этапе Step 6 Sanctum остаётся экспериментальным операторским shell, но кнопки уже не должны быть «произвольными кликами». Нужен машинно-проверяемый слой, где каждое действие зарегистрировано и ограничено политиками риска.

## Почему кнопка != доверенное действие
UI-кнопка — это только запрос оператора.
Доверенное действие появляется только когда есть:
- `ACTION_ID`;
- явный handler/script;
- precheck/gate;
- ожидаемые receipts/evidence;
- test/smoke-контракт;
- no-fake-green правила.

## Уровни риска
- `LOW_OPEN_READONLY`: навигация/чтение.
- `MEDIUM_STATE_REFRESH`: обновление состояния/верификация.
- `HIGH_FILE_TRANSFER`: передача файлов.
- `HIGH_GIT_WRITE`: потенциальные write-операции и реестровые изменения.
- `HIGH_REMOTE_SYNC`: remote route/sync операции.
- `BLOCKED_DANGEROUS`: запрещённые до отдельного hardening.

## Обязательные gate/receipt требования
Для high-risk действий обязательны:
- precheck цепочка;
- ожидаемый receipt;
- запрет на скрытие ошибок;
- запрет «PASS без доказательств».

## Как большие PowerShell flow становятся будущими кнопками
Сначала flow регистрируется как `REGISTERED_CONCEPT` или `REGISTERED_NEEDS_HANDLER` с явными условиями запуска.
Только после появления безопасного handler и smoke/evidence action может перейти в `REGISTERED_EXISTING_BEHAVIOR`.

## Как это предотвращает fake green
- Действия с отсутствующим handler/test не выдаются за реализованные.
- `READY_FOR_AGENT=true` в Step 6 запрещён политикой registry.
- Raw advisory не может использоваться как execution authority.
- Опасные действия без gate/receipt получают BLOCKED.

## Связь со Step 5 (Work Session / Administratum ACK)
Step 5 дал структуру длинной работы (`WORK_SESSION -> REPORT -> ACK`).
Step 6 фиксирует, какие Sanctum-действия вообще можно доверенно запускать, и какие из них пока только concept/skeleton.

## Почему это не rewrite Sanctum
В этой задаче не меняется визуальное ядро `SANCTUM/sanctum_v0_29_qt.py`.
Создан только control-layer реестр + test matrix + checker, чтобы будущие UI-кнопки подключались безопасно.

## Почему assets остаются Step 7
`ASSETS / DESIGN_SYSTEM / UI_LAB` не создаются на Step 6.
Visual Factory Minimum остаётся следующей фазой после принятия этого шага на PC.

## Что ещё не завершено
- Не все ACTION_ID имеют UI binding и production handler.
- Нет полного Playwright-покрытия действий.
- Нет единого runtime action-router (он остаётся следующей итерацией после Step 6 acceptance).
