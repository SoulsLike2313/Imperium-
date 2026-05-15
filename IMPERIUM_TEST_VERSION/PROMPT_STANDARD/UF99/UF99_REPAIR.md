# UF99 REPAIR MODE

## Назначение
Исправление ошибки или бага.

## Специфика режима
- Фокус на конкретной проблеме
- Минимальные изменения
- Обязательная верификация до и после

## Шаблон

```
---
TASK_ID: UF99-YYYY-MMDD-NNN
MODE: REPAIR
---

OWNER_GOAL:
Исправить <описание проблемы>

SCOPE:
- Файл: <path>
- Функция: <name>

INPUTS:
- Описание бага: <description>
- Шаги воспроизведения: <steps>
- Ожидаемое поведение: <expected>
- Фактическое поведение: <actual>

ALLOWED_PATHS:
- <path_to_fix>

FORBIDDEN_ACTIONS:
- git commit
- git push
- Изменение других файлов

REQUIRED_OUTPUTS:
- Исправленный код
- Тест, подтверждающий исправление
- Report с описанием изменений

PASS_CRITERIA:
- Баг больше не воспроизводится
- Существующие тесты проходят
- Новый тест проходит

FAIL_CRITERIA:
- Баг остаётся
- Сломаны другие тесты

VERIFICATION_COMMANDS:
- <test_command>

OWNER_REVIEW:
- Diff изменений
- Результат тестов

STOP_CONDITIONS:
- Если баг не воспроизводится
- Если требуется изменение архитектуры
- Если затронуты другие компоненты

MEMORY_QUERIES_REQUIRED:
- Q002 (forbidden actions)
- Q005 (known errors)

REPORT_FORMAT: JSON+MD
```
