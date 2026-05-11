# General Task

GENERAL_TASK_ID: GTASK-20260511-ASTRONOMICON-FORM-SMOKE-V0_1

TITLE:
Astronomicon General Task Form Smoke Test

STATUS:
REGISTERED

SOURCE_SHA256:
1cae3f5d4da064ede588d5ce3f3f94c9303c12e95a36053982d22dc055976513

GOAL:
Проверить, что Астрономикон может принять железную General Task форму

и разложить её на Local Tasks.

EXPECTED FINAL STATE:
- General Task сохранён как исходный текст.

- Скрипт выделяет PLAN ITEMS.

- По каждому PLAN ITEM создаётся Local Task.

- Каждый Local Task имеет ID, hash, parent_id и статус.

- Owner может взять LTASK-ID и отправить Servitor в работу.