# AGENT_EXCHANGE (RU)

## Назначение
Файловая зона обмена evidence-bundles между KIRO, SERVITOR, LOGOS_PRIME и OWNER внутри `IMPERIUM_TEST_VERSION`.

## Базовый workflow
1. KIRO выполняет задачу и формирует response bundle по `TEMPLATES/KIRO_RESPONSE_BUNDLE_TEMPLATE.md`.
2. KIRO кладёт bundle в `OUTBOX/KIRO/` и копию в thread `THREADS/<thread_id>/messages/`.
3. SERVITOR читает bundle, делает аудит, формирует advice bundle.
4. SERVITOR кладёт advice в `INBOX/KIRO/` и в `THREADS/<thread_id>/bundles/`.
5. LOGOS_PRIME читает `thread_index.json` + bundles и готовит owner-facing synthesis.
6. OWNER принимает решение через decision record.

## Правила качества
- No claim without evidence path.
- No PASS without criteria matrix.
- Все риски и открытые вопросы должны быть перечислены явно.
- Scope строго внутри `IMPERIUM_TEST_VERSION`.

## Куда класть файлы
- KIRO outputs: `OUTBOX/KIRO/`
- SERVITOR outputs: `OUTBOX/SERVITOR/` и `INBOX/KIRO/`
- LOGOS outputs: `OUTBOX/LOGOS_PRIME/`
- Thread memory: `THREADS/<thread_id>/messages|bundles|decisions|evidence`
