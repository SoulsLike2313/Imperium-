# OWNER REVIEW CHECKLIST — Second Brain V0.3 Interactive

## Инструкция

Пройдите каждый пункт вручную. Отметьте ✅ или ❌.

---

## Блок A: Запуск

- [ ] A1. Сервер запускается без ошибок (`py -3.12 server.py`)
- [ ] A2. Браузер открывает `http://localhost:8765/`
- [ ] A3. UI загружается (тёмный sci-fi дашборд виден)
- [ ] A4. Статус-бар показывает `SERVER OK`
- [ ] A5. Счётчики задач/комментариев/связей/receipts отображаются

## Блок B: Task Intake

- [ ] B1. Seed-задача видна в списке задач
- [ ] B2. Можно ввести новую задачу и нажать «Принять задачу»
- [ ] B3. Новая задача появляется в списке со статусом `TASK_ACCEPTED`
- [ ] B4. `accepted_tasks.json` содержит новую задачу
- [ ] B5. Receipt создан в `RUNTIME/receipts/`

## Блок C: Owner Comments

- [ ] C1. Seed-комментарий виден в списке
- [ ] C2. Можно ввести новый комментарий и нажать «Захватить»
- [ ] C3. Комментарий появляется со статусом `COMMENT_CAPTURED`
- [ ] C4. `owner_comments_runtime.json` содержит новый комментарий
- [ ] C5. Receipt создан

## Блок D: Memory Links

- [ ] D1. Seed-связь видна в списке
- [ ] D2. Можно выбрать задачу и комментарий и создать связь
- [ ] D3. Связь появляется со статусом `LINK_CREATED`
- [ ] D4. Статус комментария меняется на `LINKED`
- [ ] D5. `task_comment_links.json` содержит новую связь
- [ ] D6. Receipt создан

## Блок E: Memory Thread

- [ ] E1. Можно выбрать задачу и загрузить thread
- [ ] E2. Thread показывает задачу + связи + комментарии + receipts
- [ ] E3. Кнопка «Thread» на карточке задачи работает

## Блок F: Checker

- [ ] F1. Checker запускается: `py -3.12 .\SECOND_BRAIN\TOOLS\check_second_brain_v0_3_interactive.py`
- [ ] F2. Verdict: PASS
- [ ] F3. Overall: READY_FOR_OWNER_REVIEW
- [ ] F4. `REPORTS/second_brain_v0_3_check_report.json` создан

## Блок G: Честность

- [ ] G1. UI показывает `PROTOTYPE_INTERACTIVE`, `RULE_BASED_ONLY`, `NO_LOCAL_LLM`, `NO_AGENT_API`
- [ ] G2. Нет заявлений `PRODUCTION_READY` или `FULLY_IMPLEMENTED`
- [ ] G3. V0.2 scaffold не тронут

## Блок H: Git

- [ ] H1. `git status --short` показывает только untracked файлы в `IMPERIUM_TEST_VERSION/`
- [ ] H2. Нет изменений в tracked source файлах
- [ ] H3. Нет коммитов, нет push

---

## Итоговый вердикт владельца

- [ ] **APPROVED** — V0.3 принят, готов к следующему шагу
- [ ] **NEEDS_FIXES** — требуются исправления (указать ниже)

Комментарий владельца:
_____________________
