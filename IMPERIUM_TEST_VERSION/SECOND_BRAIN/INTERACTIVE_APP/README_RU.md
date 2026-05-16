# Second Brain V0.3 — Interactive App

## Статус

- **PROTOTYPE_INTERACTIVE** — реально интерактивный прототип
- **RULE_BASED_ONLY** — без LLM, без внешних агентов
- **NO_LOCAL_LLM** — локальная LLM не подключена (NOT_CONFIGURED)
- **NO_AGENT_API** — агентный API не реализован (NOT_IMPLEMENTED)
- **НЕ PRODUCTION_READY**

## Как запустить

### Вариант 1: PowerShell launcher

```powershell
cd E:\IMPERIUM\IMPERIUM_TEST_VERSION\SECOND_BRAIN\INTERACTIVE_APP
powershell -ExecutionPolicy Bypass -File launch_second_brain_v0_3.ps1
```

### Вариант 2: Напрямую через Python

```powershell
cd E:\IMPERIUM\IMPERIUM_TEST_VERSION\SECOND_BRAIN\INTERACTIVE_APP
py -3.12 server.py
```

Затем открыть в браузере: **http://localhost:8765/**

## API Endpoints

| Метод | URL | Описание |
|-------|-----|----------|
| GET | `/` | UI дашборд |
| GET | `/api/status` | Статус runtime |
| GET | `/api/tasks` | Список задач |
| POST | `/api/tasks` | Создать задачу |
| GET | `/api/comments` | Список комментариев |
| POST | `/api/comments` | Создать комментарий |
| GET | `/api/links` | Список связей |
| POST | `/api/links` | Создать связь |
| GET | `/api/thread/<task_id>` | Memory thread задачи |
| POST | `/api/export` | Экспорт runtime пакета |

## Что реально работает

- Ввод задачи через UI → сохраняется в JSON → receipt создаётся
- Ввод Owner-комментария → сохраняется в JSON → receipt создаётся
- Связывание комментария с задачей → link создаётся → receipt создаётся
- Memory thread view для задачи
- Экспорт runtime пакета

## Что НЕ реализовано (честно)

- Локальная LLM: NOT_CONFIGURED
- Агентный API: NOT_IMPLEMENTED
- Автоматическая интерпретация комментариев: NOT_IMPLEMENTED
- Персистентная база данных: используются JSON-файлы
- Аутентификация: отсутствует (локальный прототип)
