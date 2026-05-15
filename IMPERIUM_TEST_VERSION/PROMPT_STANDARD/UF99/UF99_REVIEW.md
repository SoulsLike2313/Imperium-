# UF99 REVIEW MODE

## Назначение
Аудит, разбор, проверка качества.

## Шаблон

```
---
TASK_ID: UF99-YYYY-MMDD-NNN
MODE: REVIEW
---

OWNER_GOAL:
Проверить <объект проверки>

SCOPE:
- Проверяемые файлы: <paths>
- Критерии проверки: <criteria>

INPUTS:
- Код/документы для проверки: <paths>
- Стандарты: <standards>

ALLOWED_PATHS:
- <review_output_path>

FORBIDDEN_ACTIONS:
- git commit
- git push
- Изменение проверяемого кода

REQUIRED_OUTPUTS:
- Отчёт проверки
- Список issues
- Рекомендации

PASS_CRITERIA:
- Все критерии проверены
- Issues документированы

VERIFICATION_COMMANDS:
- (нет — ручная проверка)

OWNER_REVIEW:
- Отчёт
- Issues

STOP_CONDITIONS:
- Если код недоступен
- Если стандарты неясны

REPORT_FORMAT: JSON+MD
```
