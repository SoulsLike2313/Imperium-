# DESIGN DECISIONS — Second Brain V0.3 Interactive

## Архитектурные решения

### 1. Python stdlib HTTP server
**Решение:** `http.server.HTTPServer` + `BaseHTTPRequestHandler`  
**Причина:** Нет зависимостей, работает из коробки с Python 3.12, соответствует требованию «Python standard library local HTTP server»  
**Альтернатива:** Flask/FastAPI — отклонено (тяжёлые фреймворки)

### 2. JSON-файлы как хранилище
**Решение:** `accepted_tasks.json`, `owner_comments_runtime.json`, `task_comment_links.json`  
**Причина:** Простота, читаемость, соответствие V0.2 паттернам, нет зависимостей  
**Ограничение:** Нет транзакций, нет concurrent write safety — приемлемо для прототипа

### 3. Receipts как отдельные JSON-файлы
**Решение:** Каждый receipt — отдельный файл `RCP-YYYYMMDD-HHMMSS-NNN.json`  
**Причина:** Соответствует паттерну IMPERIUM, легко проверяется checker'ом, атомарно

### 4. Seed data в MEMORY_ZONES
**Решение:** Seed task, comment, link записаны прямо в runtime JSON-файлы  
**Причина:** Checker может сразу проверить наличие данных без запуска сервера

### 5. UI без фреймворков
**Решение:** Чистый HTML/CSS/JS, fetch API  
**Причина:** Требование «без тяжёлых фреймворков», работает локально из браузера

### 6. Честные статусы
**Решение:** `PROTOTYPE_INTERACTIVE`, `RULE_BASED_ONLY`, `NO_LOCAL_LLM`, `NO_AGENT_API` — везде  
**Причина:** NO FAKE GREEN policy, AGENTS.md требования

### 7. Разделение V0.2 и V0.3
**Решение:** Все V0.3 файлы в новых папках (`INTERACTIVE_APP/`, `RUNTIME/`, `MEMORY_ZONES/MEMORY_LINKS/`)  
**Причина:** V0.2 scaffold не должен быть разрушен

## Что намеренно НЕ реализовано

| Функция | Статус | Причина |
|---------|--------|---------|
| Локальная LLM | NOT_CONFIGURED | Не требуется для V0.3 |
| Агентный API | NOT_IMPLEMENTED | Не требуется для V0.3 |
| Автоинтерпретация комментариев | NOT_IMPLEMENTED | Требует LLM |
| База данных | NOT_IMPLEMENTED | JSON достаточно для прототипа |
| Аутентификация | NOT_IMPLEMENTED | Локальный прототип |
| WebSocket | NOT_IMPLEMENTED | Polling достаточно |

## Что готово для V0.4

- Подключение локальной LLM для интерпретации комментариев
- Агентный API для автоматической маршрутизации задач
- Persistent storage (SQLite или подобное)
- Memory thread автоматическое построение
