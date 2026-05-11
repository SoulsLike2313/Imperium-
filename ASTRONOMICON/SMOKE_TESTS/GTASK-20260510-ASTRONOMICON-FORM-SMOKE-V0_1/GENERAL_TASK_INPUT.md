# GENERAL TASK

GENERAL_TASK_TITLE:
Astronomicon General Task Form Smoke Test

GENERAL_TASK_CODE:
ASTRONOMICON_FORM_SMOKE

AUTHOR:
Owner

CREATED_AT:
AUTO

EXECUTION_INTENT:
manual

PRIORITY:
high

---

## 1. GOAL

Проверить, что Астрономикон может принять железную General Task форму и разложить её на Local Tasks.

---

## 2. CONTEXT

IMPERIUM переходит от ручных разрозненных действий к task pipeline:
General Task -> Local Tasks -> Stages -> Readiness -> Manual Workflow -> Artifact -> Commit/Push.

---

## 3. CURRENT PROBLEM

Пока нет проверенной формы, которую Owner может заполнить руками, а скрипт может разобрать без догадок.

---

## 4. EXPECTED FINAL STATE

- General Task сохранён как исходный текст.
- Скрипт выделяет PLAN ITEMS.
- По каждому PLAN ITEM создаётся Local Task.
- Каждый Local Task имеет ID, hash, parent_id и статус.
- Owner может взять LTASK-ID и отправить Servitor в работу.

---

## 5. HARD CONSTRAINTS

- Не трогать THRONE.
- Не публиковать секреты.
- Не использовать SSH_COMMAND_LIBRARY.
- Не делать fake green.
- Не строить dashboard на этом шаге.

---

## 6. DO NOT DO

- Не делать полноценный Astronomicon UI.
- Не делать stage decomposition.
- Не делать Speculum import.
- Не делать автоматическое исполнение.
- Не делать git add . вслепую.

---

## 7. PLAN ITEMS

1. ITEM_ID: PI-001
   TITLE: Define General Task form contract
   TEXT: Зафиксировать минимальную форму General Task, которую Owner может заполнить руками.
   EXPECTED_OUTPUT: SOURCE_TEXT.md and parsed GENERAL_TASK.json.
   REQUIRED_ORGANS: Astronomicon, Administratum
   EXECUTION_MODE: manual
   DEPENDS_ON: none

2. ITEM_ID: PI-002
   TITLE: Parse Plan Items into Local Tasks
   TEXT: Прочитать секцию PLAN ITEMS и создать Local Task для каждого numbered item.
   EXPECTED_OUTPUT: LTASK-001, LTASK-002, LTASK-003 folders with JSON and markdown records.
   REQUIRED_ORGANS: Astronomicon, Mechanicus
   EXECUTION_MODE: scripted
   DEPENDS_ON: PI-001

3. ITEM_ID: PI-003
   TITLE: Verify Servitor routing by Local Task ID
   TEXT: Проверить, что по LTASK-ID можно понять parent General Task, scope, expected output and execution mode.
   EXPECTED_OUTPUT: SERVITOR_ROUTE_TEST.md showing how to send Servitor to LTASK-001.
   REQUIRED_ORGANS: Astronomicon, Administratum, Officio Agentis
   EXECUTION_MODE: manual
   DEPENDS_ON: PI-002

---

## 8. KNOWN RISKS

- Parser может неверно разрезать пункты.
- В форме может не хватать обязательных полей.
- Local Task может получить слишком широкий scope.
- ID и hash могут быть нестабильными.

---

## 9. REQUIRED ORGANS

- Astronomicon
- Administratum
- Mechanicus
- Officio Agentis

---

## 10. REQUIRED INPUTS

- This General Task form.
- Current Git repository.
- No private bundle required for this smoke test.

---

## 11. EXPECTED ARTIFACTS

- ASTRONOMICON smoke test folder.
- Local Task registry.
- Local Task files.
- Smoke test receipt.
- Servitor route test file.

---

## 12. OWNER NOTES

Это тестовая форма. Цель — проверить не красоту, а то, что скриптовый pipeline может родить первые адресуемые Local Tasks.
