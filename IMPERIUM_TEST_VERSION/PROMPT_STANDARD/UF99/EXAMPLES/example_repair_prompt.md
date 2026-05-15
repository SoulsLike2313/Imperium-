---
TASK_ID: UF99-2026-0515-001
MODE: REPAIR
---

OWNER_GOAL:
Исправить ошибку кодировки в выводе тестов Live Workbench

SCOPE:
- Файл: IMPERIUM_TEST_VERSION/LIVE_WORKBENCH/SANDBOX_PROJECT/tests/test_app.py
- Проблема: Unicode символы не отображаются в Windows console

INPUTS:
- Описание бага: Символы ✅ и ❌ вызывают UnicodeEncodeError
- Шаги воспроизведения: py -3 test_app.py
- Ожидаемое поведение: Тесты выводят статус
- Фактическое поведение: UnicodeEncodeError

ALLOWED_PATHS:
- IMPERIUM_TEST_VERSION/LIVE_WORKBENCH/**

FORBIDDEN_ACTIONS:
- git commit
- git push
- Изменение файлов вне LIVE_WORKBENCH

REQUIRED_OUTPUTS:
- Исправленный test_app.py
- Report с описанием изменений

PASS_CRITERIA:
- Тесты запускаются без ошибок
- Статус отображается корректно

FAIL_CRITERIA:
- UnicodeEncodeError остаётся
- Тесты не проходят

VERIFICATION_COMMANDS:
- py -3 IMPERIUM_TEST_VERSION\LIVE_WORKBENCH\SANDBOX_PROJECT\tests\test_app.py

OWNER_REVIEW:
- Diff изменений
- Результат запуска тестов

STOP_CONDITIONS:
- Если проблема в системной кодировке
- Если требуется изменение других файлов

MEMORY_QUERIES_REQUIRED:
- Q002
- Q005

REPORT_FORMAT: JSON+MD
