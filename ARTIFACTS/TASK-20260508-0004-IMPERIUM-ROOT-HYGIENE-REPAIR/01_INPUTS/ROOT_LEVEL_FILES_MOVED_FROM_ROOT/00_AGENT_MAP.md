# E:\IMPERIUM — ROOT AGENT MAP

## Назначение
E:\IMPERIUM = root операционной среды IMPERIUM на PC.
Корень должен содержать только крупные смысловые зоны.
Корень не должен быть складом zip/sha256/output-файлов.

## Главные законы корня

- В корне лежат только крупные папки и root-карты.
- Артефакты конкретных задач лежат в E:\IMPERIUM\ARTIFACTS\<TASK_ID>\...
- Инструменты лежат в профильных библиотеках.
- Доказательства применения инструментов лежат в ARTIFACTS.
- Ничего не удалять без owner approval.
- THRONE не трогать из PC root tasks.
- VM2/VM3 не трогать без отдельного route task.

## Папки верхнего уровня

### ARCHIVE

Адрес:
E:\IMPERIUM\ARCHIVE

Смысл:
Архивная зона старых или отложенных материалов.

Что здесь хранится:
Historical bundles, snapshots, legacy references.

Что сюда можно писать:
Писать только owner-approved archival materials.

Что сюда нельзя писать:
Нельзя использовать как активную рабочую зону без review.

Статус:
legacy

Связанные зоны:
docs

### ARTIFACTS

Адрес:
E:\IMPERIUM\ARTIFACTS

Смысл:
Корневой реестр артефактов задач по TASK_ID.

Что здесь хранится:
Task evidence, receipts, manifests, hashes, bundles, summaries.

Что сюда можно писать:
Писать только в структуру TASK_ID и индексные файлы ARTIFACTS.

Что сюда нельзя писать:
Нельзя складывать raw secrets и файлы без TASK_ID.

Статус:
active

Связанные зоны:
PC_ARTIFACTS_VAULT, SSH_COMMAND_LIBRARY

### docs

Адрес:
E:\IMPERIUM\docs

Смысл:
Документационная зона верхнего уровня.

Что здесь хранится:
Operational and descriptive documentation.

Что сюда можно писать:
Писать документацию по approved scope.

Что сюда нельзя писать:
Нельзя хранить runtime secrets и случайные outputs.

Статус:
active

Связанные зоны:
PC_ENGINEERING_ROOM, ARTIFACTS

### IMPERIUM_LIGHT_SNAPSHOT_20260507_164459

Адрес:
E:\IMPERIUM\IMPERIUM_LIGHT_SNAPSHOT_20260507_164459

Смысл:
Snapshot-зона состояния, сохраненная во времени.

Что здесь хранится:
Snapshot trees, manifests, sampled evidence.

Что сюда можно писать:
Писать только snapshot-related материалы при approved step.

Что сюда нельзя писать:
Нельзя смешивать с активными task outputs.

Статус:
legacy

Связанные зоны:
ARCHIVE

### OBSERVED

Адрес:
E:\IMPERIUM\OBSERVED

Смысл:
Observed-копии для read-only изучения контуров.

Что здесь хранится:
Read-only snapshots/copies без mutation.

Что сюда можно писать:
Только читать и ссылаться в отчетах.

Что сюда нельзя писать:
Нельзя мутировать observed-копии в root tasks.

Статус:
observed

Связанные зоны:
OBSERVED_VM3_REPO_COPY

### OBSERVED_VM3_REPO_COPY

Адрес:
E:\IMPERIUM\OBSERVED_VM3_REPO_COPY

Смысл:
Observed-копия VM3 репозитория для безопасного чтения.

Что здесь хранится:
Reference materials and VM3 historical outputs.

Что сюда можно писать:
Только read-only reference.

Что сюда нельзя писать:
Нельзя писать и изменять содержимое.

Статус:
observed

Связанные зоны:
OBSERVED

### PC_ARTIFACTS_VAULT

Адрес:
E:\IMPERIUM\PC_ARTIFACTS_VAULT

Смысл:
Ранее созданный vault доказательных артефактов PC-контура.

Что здесь хранится:
Route proofs, cards, pointers, index entries.

Что сюда можно писать:
Писать evidence-копии и registry материалы.

Что сюда нельзя писать:
Нельзя трактовать как canon/admission authority.

Статус:
needs_review

Связанные зоны:
ARTIFACTS

### PC_ENGINEERING_ROOM

Адрес:
E:\IMPERIUM\PC_ENGINEERING_ROOM

Смысл:
Инженерный штаб PC-контура для review/test/diagnostics.

Что здесь хранится:
Engineering plans, organ templates, policy drafts, lab notes.

Что сюда можно писать:
Писать инженерные материалы и рабочие baseline-файлы.

Что сюда нельзя писать:
Нельзя считать эту зону canon/admission authority.

Статус:
active

Связанные зоны:
ARTIFACTS, PC_OWNER_TEST_BENCH

### PC_LOCAL_IMPERIUM_ANALYSIS_20260507_1711

Адрес:
E:\IMPERIUM\PC_LOCAL_IMPERIUM_ANALYSIS_20260507_1711

Смысл:
Диагностический/аналитический пакет по отдельному шагу.

Что здесь хранится:
Audit findings, repair plans, mapped evidence.

Что сюда можно писать:
Писать step-bound analysis outputs.

Что сюда нельзя писать:
Нельзя считать зону постоянным artifacts-root.

Статус:
needs_review

Связанные зоны:
ARTIFACTS, PC_ENGINEERING_ROOM

### PC_OWNER_TEST_BENCH

Адрес:
E:\IMPERIUM\PC_OWNER_TEST_BENCH

Смысл:
Локальный тестовый контур Owner/PC для валидаций и приемки.

Что здесь хранится:
Inbox/outbox тестов, receipts, validation outputs.

Что сюда можно писать:
Писать тестовые артефакты и проверочные отчеты.

Что сюда нельзя писать:
Нельзя использовать как THRONE или canonical source.

Статус:
active

Связанные зоны:
SSH_COMMAND_LIBRARY, PC_ENGINEERING_ROOM

### PC_READ_ONLY_CLASSIFICATION_AND_REPAIR_PLAN_20260507_1813

Адрес:
E:\IMPERIUM\PC_READ_ONLY_CLASSIFICATION_AND_REPAIR_PLAN_20260507_1813

Смысл:
Диагностический/аналитический пакет по отдельному шагу.

Что здесь хранится:
Audit findings, repair plans, mapped evidence.

Что сюда можно писать:
Писать step-bound analysis outputs.

Что сюда нельзя писать:
Нельзя считать зону постоянным artifacts-root.

Статус:
needs_review

Связанные зоны:
ARTIFACTS, PC_ENGINEERING_ROOM

### PROMPT_OUTBOX_TO_VM3

Адрес:
E:\IMPERIUM\PROMPT_OUTBOX_TO_VM3

Смысл:
Локальная зона подготовки/отправки prompt-пакетов для VM3 lane.

Что здесь хранится:
Draft/ready/sent prompts и локальные receipts отправки.

Что сюда можно писать:
Писать только prompt-пакеты и transport receipts.

Что сюда нельзя писать:
Нельзя хранить unrelated bundles и secrets.

Статус:
active

Связанные зоны:
SSH_COMMAND_LIBRARY

### SSH_COMMAND_LIBRARY

Адрес:
E:\IMPERIUM\SSH_COMMAND_LIBRARY

Смысл:
Библиотека маршрутов и инструментов SSH/dispatch.

Что здесь хранится:
Route notes, scripts, manifests, tested recipes.

Что сюда можно писать:
Писать инструменты маршрутов и их manifests.

Что сюда нельзя писать:
Нельзя хранить private keys и raw credentials.

Статус:
active

Связанные зоны:
ARTIFACTS, PC_OWNER_TEST_BENCH

## Файлы в корне

Файлы zip/sha256/reports в корне являются cleanup candidates и должны быть перемещены в ARTIFACTS после отдельного owner-approved routing step.

## Куда класть новые outputs

E:\IMPERIUM\ARTIFACTS\<TASK_ID>\...

## Куда класть route/tools

E:\IMPERIUM\SSH_COMMAND_LIBRARY\
E:\IMPERIUM\SCRIPTORIUM\ (planned zone)
E:\IMPERIUM\ARSENAL\ (planned zone)

Если SCRIPTORIUM или ARSENAL ещё не существуют, они считаются planned zones и не создаются без отдельного task.

## Статус карты

Draft baseline.
Будет правиться вручную Owner/Logos по мере развития структуры.
