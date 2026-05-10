# PC_SERVICE_CONTOUR_MODEL_V1

## Назначение

Закрепить рабочую модель: PC не является writer-контуром и не является admission-контуром.
PC является только Windows/service/support-контуром для owner-facing запуска transfer/control операций.

## Жесткие границы

1. Единственный truth center и canon target: `Throne`.
2. Писать в рабочие копии могут только VM-контуры (`vm1`, `vm2`, `vm3`).
3. PC не выполняет direct write в репозиторий рабочих контуров.
4. PC не выполняет admission.
5. PC не является источником канонической истины.

## Операционная роль PC

1. Тонкий owner-facing shell (русский интерфейс) для запуска transfer скриптов.
2. Хранение service state/receipts/task queue в Windows-зонах сервиса.
3. Получение bundle в `E:\IMPERIUM\IMPERIUM_ALL_REVIEW\bundles\`.
4. Отправка prompt/ПРОМТ payload в active writer contour через lawful SSH/SCP route.

## Текущий активный контурный набор (до capsule)

- `Throne` — truth center, helper/hub для lawful channel bootstrap.
- `PC` — service/support-only contour, owner-facing runtime shell.
- `VM3` — текущий active worker для данного operation/session.

`VM1`, `VM2`, `VM3` принадлежат одному worker-классу без рангов.
`active_worker` определяется динамически по task/session signal state.
`VM1` доступен как evidence/continuation worker по команде Owner.
`VM2` зафиксирован как frozen/do-not-touch до явной команды Owner.

## Границы UI и логистики

1. UI не содержит SSH topology intelligence.
2. UI не содержит маршрутизацию admission/sync.
3. Логистика и transport находятся только в versioned script layer.
4. UI только вызывает backend scripts и читает JSON-результаты.
5. Минимальный owner flow текущей фазы: `send prompt` + `pull latest bundle`.

## Runtime/update граница для Windows приложения

1. Runtime-артефакт на PC (`EXE`/launcher package) — это operational surface, но не source-truth.
2. Локальные правки на PC допустимы только как `diagnostic/sandbox` до переноса в worker source.
3. Истинная форма приложения обновляется только worker-контуром:
   - правка source,
   - сборка пакета,
   - доставка новой версии на PC.
4. PC Servitor может тестировать, собирать логи и фикс-ноты, но не может canonize runtime-изменения напрямую.

## Активный writer

1. Active writer не хардкодится как VM3 «навсегда».
2. Active writer читается из канонической state surface (`CONTOUR_RUNTIME_BINDING_V1`).
3. При невозможности чтения live mirror разрешен bounded fallback к bundled snapshot c обязательной пометкой в receipt.

## Зоны Windows сервиса

Обязательные зоны:

- `E:\IMPERIUM\IMPERIUM_ALL_REVIEW\bundles\`
- `E:\IMPERIUM\IMPERIUM_ALL_REVIEW\receipts\`
- `E:\IMPERIUM\IMPERIUM_SERVICE_STATE\`
- `E:\IMPERIUM\IMPERIUM_SERVICE_TASKS\`
- `E:\IMPERIUM\IMPERIUM_SERVICE_MIRROR\canon\`

`IMPERIUM_SERVICE_MIRROR` является read-only/service-only и не может считаться writer source.

## Связанные законы

- `CANON/DOCTRINE/CROSS_CONTOUR_WORKING_ARTIFACT_RETRIEVAL_LAW_V1.md`
- `CANON/DOCTRINE/PC_RUNTIME_UPDATE_BOUNDARY_LAW_V1.md`
- `CANON/machine_readable/logistics/WORKING_ARTIFACT_SOURCE_PRIORITY_MODEL_V1.json`
- `CANON/machine_readable/optimization/CONTOUR_RUNTIME_BINDING_V1.json`
