# UF99 RESEARCH MODE

## Назначение
Исследование, анализ, сбор информации.

## Шаблон

```
---
TASK_ID: UF99-YYYY-MMDD-NNN
MODE: RESEARCH
---

OWNER_GOAL:
Исследовать <тема>

SCOPE:
- Область исследования: <area>
- Глубина: <depth>

INPUTS:
- Вопросы: <questions>
- Контекст: <context>

ALLOWED_PATHS:
- <research_output_path>

FORBIDDEN_ACTIONS:
- git commit
- git push
- Изменение кода

REQUIRED_OUTPUTS:
- Отчёт исследования
- Рекомендации
- Ссылки на источники

PASS_CRITERIA:
- Вопросы отвечены
- Рекомендации обоснованы

VERIFICATION_COMMANDS:
- (нет — ручная проверка)

OWNER_REVIEW:
- Отчёт
- Рекомендации

STOP_CONDITIONS:
- Если информация недоступна
- Если требуется доступ к закрытым ресурсам

REPORT_FORMAT: MD
```
