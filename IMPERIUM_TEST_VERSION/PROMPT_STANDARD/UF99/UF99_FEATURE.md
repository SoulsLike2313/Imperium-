# UF99 FEATURE MODE

## Назначение
Создание новой функциональности.

## Специфика режима
- Чёткое описание требований
- Итеративная разработка
- Тесты обязательны

## Шаблон

```
---
TASK_ID: UF99-YYYY-MMDD-NNN
MODE: FEATURE
---

OWNER_GOAL:
Создать <описание функции>

SCOPE:
- Новые файлы: <paths>
- Изменяемые файлы: <paths>

INPUTS:
- Требования: <requirements>
- Примеры использования: <examples>
- Ограничения: <constraints>

ALLOWED_PATHS:
- <path1>
- <path2>

FORBIDDEN_ACTIONS:
- git commit
- git push
- Изменение production кода

REQUIRED_OUTPUTS:
- Код функции
- Тесты
- Документация
- Report

PASS_CRITERIA:
- Функция работает по требованиям
- Тесты проходят
- Документация написана

FAIL_CRITERIA:
- Функция не соответствует требованиям
- Тесты падают

VERIFICATION_COMMANDS:
- <test_command>
- <demo_command>

OWNER_REVIEW:
- Код
- Тесты
- Демонстрация

STOP_CONDITIONS:
- Если требования неясны
- Если нужны архитектурные решения
- Если scope расширяется

MEMORY_QUERIES_REQUIRED:
- Q002 (forbidden actions)
- Q003 (goals)

REPORT_FORMAT: JSON+MD
```
