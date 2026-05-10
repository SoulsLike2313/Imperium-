# ARTIFACT ROUTING POLICY

## Правило 1
Корень E:\IMPERIUM не является местом хранения outputs конкретных задач.

## Правило 2
Каждый output задачи должен иметь TASK_ID и лежать в:
E:\IMPERIUM\ARTIFACTS\<TASK_ID>\...

## Правило 3
Если artifact также важен для профильной библиотеки, он может остаться в библиотеке, но копия или source pointer должны быть в ARTIFACTS.

## Правило 4
Библиотека хранит инструмент.
ARTIFACTS хранит доказательство применения инструмента.

## Примеры

SSH_COMMAND_LIBRARY:
хранит route/scripts/instructions.

ARTIFACTS:
хранит proof, что route/script реально был использован и сработал.

PC_ENGINEERING_ROOM:
хранит рабочую инженерную среду.

ARTIFACTS:
хранит итоговые доказательства задач, выполненных в этой среде.

## Перемещения
Ничего не перемещать без отдельного owner-approved routing task.
Любое перемещение должно иметь:
- source path
- target path
- sha256
- reason
- owner approval marker
- rollback note
