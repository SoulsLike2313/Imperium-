# UF99 WORK MODE

## Назначение
Общий рабочий режим для смешанных задач.

## Шаблон

```
---
TASK_ID: UF99-YYYY-MMDD-NNN
MODE: WORK
---

OWNER_GOAL:
<описание задачи>

SCOPE:
<границы работы>

INPUTS:
- <input1>

ALLOWED_PATHS:
- <path1>

FORBIDDEN_ACTIONS:
- git commit
- git push

REQUIRED_OUTPUTS:
- <output1>

PASS_CRITERIA:
- <criterion1>

VERIFICATION_COMMANDS:
- <command1>

OWNER_REVIEW:
- <item1>

STOP_CONDITIONS:
- При неясности
- При ошибках

REPORT_FORMAT: JSON+MD
```
