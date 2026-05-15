# UF99 TEST MODE

## Назначение
Тестирование существующего кода.

## Шаблон

```
---
TASK_ID: UF99-YYYY-MMDD-NNN
MODE: TEST
---

OWNER_GOAL:
Протестировать <компонент>

SCOPE:
- Тестируемый код: <path>
- Тестовые файлы: <path>

INPUTS:
- Код для тестирования: <path>
- Существующие тесты: <path>

ALLOWED_PATHS:
- <test_path>

FORBIDDEN_ACTIONS:
- git commit
- git push
- Изменение production кода

REQUIRED_OUTPUTS:
- Тесты
- Report с результатами
- Coverage report (если возможно)

PASS_CRITERIA:
- Все тесты проходят
- Coverage >= <threshold>

VERIFICATION_COMMANDS:
- <test_command>

OWNER_REVIEW:
- Результаты тестов
- Coverage

STOP_CONDITIONS:
- Если код не компилируется
- Если нужны моки/стабы

REPORT_FORMAT: JSON+MD
```
