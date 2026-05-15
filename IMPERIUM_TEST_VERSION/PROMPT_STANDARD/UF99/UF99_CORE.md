# UF99 PROMPT STANDARD — CORE

## Назначение

UF99 — единая компактная форма инженерного общения между Owner и агентами.

## Принципы

1. **Компактность** — prompt должен быть коротким
2. **Структурность** — одинаковая форма для всех задач
3. **Полнота** — все необходимые поля присутствуют
4. **Машиночитаемость** — можно валидировать автоматически

## Обязательные поля

| Поле | Описание | Пример |
|------|----------|--------|
| TASK_ID | Уникальный ID задачи | UF99-2026-0515-001 |
| MODE | Режим работы | REPAIR / RESEARCH / FEATURE / TEST / REVIEW / WORK |
| OWNER_GOAL | Цель Owner | Исправить ошибку X |
| SCOPE | Границы работы | Только файл Y |
| INPUTS | Входные данные | Путь к файлу, описание бага |
| ALLOWED_PATHS | Разрешённые пути | IMPERIUM_TEST_VERSION/** |
| FORBIDDEN_ACTIONS | Запрещённые действия | git commit, git push |
| REQUIRED_OUTPUTS | Требуемые выходы | Report, receipt |
| PASS_CRITERIA | Критерии успеха | Тест проходит |
| FAIL_CRITERIA | Критерии провала | Тест падает |
| VERIFICATION_COMMANDS | Команды проверки | py -3 test.py |
| OWNER_REVIEW | Что проверит Owner | Dashboard, report |
| STOP_CONDITIONS | Когда остановиться | При ошибке, при неясности |
| MEMORY_QUERIES_REQUIRED | Запросы к памяти | Q001, Q002 |
| REPORT_FORMAT | Формат отчёта | JSON + MD |

## Формат prompt

```
---
TASK_ID: UF99-YYYY-MMDD-NNN
MODE: <mode>
---

OWNER_GOAL:
<goal>

SCOPE:
<scope>

INPUTS:
- <input1>
- <input2>

ALLOWED_PATHS:
- <path1>

FORBIDDEN_ACTIONS:
- <action1>

REQUIRED_OUTPUTS:
- <output1>

PASS_CRITERIA:
- <criterion1>

FAIL_CRITERIA:
- <criterion1>

VERIFICATION_COMMANDS:
- <command1>

OWNER_REVIEW:
- <item1>

STOP_CONDITIONS:
- <condition1>

MEMORY_QUERIES_REQUIRED:
- <query_id>

REPORT_FORMAT: <format>
```

## Режимы (MODE)

- **REPAIR** — исправление ошибки
- **RESEARCH** — исследование
- **FEATURE** — новая функция
- **TEST** — тестирование
- **REVIEW** — аудит/разбор
- **WORK** — рабочий режим
