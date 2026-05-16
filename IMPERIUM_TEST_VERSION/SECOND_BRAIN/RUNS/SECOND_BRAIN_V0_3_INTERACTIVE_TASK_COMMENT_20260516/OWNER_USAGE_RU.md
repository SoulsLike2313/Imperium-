# OWNER USAGE — Second Brain V0.3 Interactive

## Как запустить

### Шаг 1: Запустить сервер

```powershell
cd E:\IMPERIUM\IMPERIUM_TEST_VERSION\SECOND_BRAIN\INTERACTIVE_APP
powershell -ExecutionPolicy Bypass -File launch_second_brain_v0_3.ps1
```

Или напрямую:
```powershell
py -3.12 E:\IMPERIUM\IMPERIUM_TEST_VERSION\SECOND_BRAIN\INTERACTIVE_APP\server.py
```

### Шаг 2: Открыть браузер

Перейти по адресу: **http://localhost:8765/**

---

## Что делать в UI

### Создать задачу
1. Панель **Task Intake** (слева)
2. Ввести текст задачи в поле «Текст задачи»
3. Опционально: цель владельца, приоритет, теги
4. Нажать **⚡ Принять задачу**
5. Задача появится в списке со статусом `TASK_ACCEPTED`
6. Receipt создаётся автоматически

### Создать Owner-комментарий
1. Панель **Owner Comments** (центр)
2. Ввести текст комментария
3. Выбрать тип (OBSERVATION, INSTRUCTION, QUESTION, …)
4. Опционально: интерпретация
5. Нажать **💬 Захватить комментарий**
6. Комментарий появится со статусом `COMMENT_CAPTURED`

### Связать комментарий с задачей
1. Панель **Memory Links** (справа)
2. Выбрать задачу из выпадающего списка
3. Выбрать комментарий из выпадающего списка
4. Опционально: причина связи
5. Нажать **🔗 Создать связь**
6. Статус комментария изменится на `LINKED`

### Просмотреть Memory Thread
1. Панель **Memory Thread** (внизу)
2. Выбрать задачу из выпадающего списка
3. Нажать **🧵 Загрузить**
4. Или нажать кнопку **🧵 Thread** на карточке задачи
5. Увидеть: задача + связи + комментарии + receipts

### Экспортировать runtime пакет
- Нажать **📦 Экспорт пакета** в верхней панели
- Пакет сохранится в `RUNTIME/exports/export_YYYYMMDD-HHMMSS/`

---

## Что проверить вручную

1. Открыть `MEMORY_ZONES/TASK_INTAKE/accepted_tasks.json` — задачи там?
2. Открыть `MEMORY_ZONES/OWNER_COMMENTS/owner_comments_runtime.json` — комментарии там?
3. Открыть `MEMORY_ZONES/MEMORY_LINKS/task_comment_links.json` — связи там?
4. Открыть `RUNTIME/receipts/` — receipts созданы?
5. Запустить checker:
   ```powershell
   cd E:\IMPERIUM\IMPERIUM_TEST_VERSION
   py -3.12 .\SECOND_BRAIN\TOOLS\check_second_brain_v0_3_interactive.py
   ```

---

## Честные ограничения

- **NO_LOCAL_LLM** — интерпретация комментариев не автоматическая
- **NO_AGENT_API** — агенты не подключены
- **RULE_BASED_ONLY** — вся логика детерминированная
- **PROTOTYPE** — не для production использования
