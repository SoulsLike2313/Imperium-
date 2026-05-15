# ХРОНОЛОГИЯ ЭКСПЕРИМЕНТА IMPERIUM TEST VERSION

## Для Owner / Logos-Prime

Этот файл описывает по-русски всё, что было сделано в экспериментальной копии IMPERIUM.

---

## СЕССИЯ 1: 2026-05-15

### ЭТАП 0: Создание тестовой копии

**Что сделано:**
- Создана папка `E:\IMPERIUM\IMPERIUM_TEST_VERSION\`
- Добавлена в `.gitignore` основного repo
- Выбран вариант A (внутри repo) после того, как вариант B (sibling) оказался недоступен для записи

**Файлы:**
- `BASELINE_STATUS.json` — статус baseline (evidence-baseline, НЕ product-v1)
- `TASK_RULES.md` — правила выполнения задач

**Вердикт:** PASS

---

### ЭТАП 1: Testing Field MVP

**Что сделано:**
- Создана структура `TESTING_FIELD/`
- Папки: CANDIDATES, SMOKE_RESULTS, SCREENSHOTS, PROMOTION_LOG, CHECKLISTS, SCRIPTS, DOCS
- Smoke checklist для ручного тестирования
- Скрипт `smoke_sanctum.py` — проверяет Sanctum (существование, синтаксис, PyQt6)
- Скрипт `capture_screenshot.py` — захват скриншотов
- Документ решения по Qt smoke testing

**Файлы:**
- `TESTING_FIELD/README.md`
- `TESTING_FIELD/CHECKLISTS/SMOKE_CHECKLIST.md`
- `TESTING_FIELD/SCRIPTS/smoke_sanctum.py`
- `TESTING_FIELD/SCRIPTS/capture_screenshot.py`
- `TESTING_FIELD/DOCS/QT_SMOKE_DECISION.md`
- `TESTING_FIELD/PROMOTION_LOG/README.md`

**Команды для Owner:**
```powershell
py -3 IMPERIUM_TEST_VERSION\TESTING_FIELD\SCRIPTS\smoke_sanctum.py
```

**Вердикт:** PASS

---

### ЭТАП 2: Mechanicus MVP

**Что сделано:**
- Создан `ORGAN_CONTRACT.json` для Mechanicus
- Скрипт `script_scanner.py` — сканирует все скрипты в repo
- Скрипт `script_health_check.py` — проверяет существование и синтаксис
- Скрипт `command_gateway.py` — централизованное выполнение команд
- Структура `REPAIR_QUEUE/` для очереди ремонта

**Файлы:**
- `ORGANS/MECHANICUS/ORGAN_CONTRACT.json`
- `ORGANS/MECHANICUS/SCRIPTS/script_scanner.py`
- `ORGANS/MECHANICUS/SCRIPTS/script_health_check.py`
- `ORGANS/MECHANICUS/SCRIPTS/command_gateway.py`
- `ORGANS/MECHANICUS/REPAIR_QUEUE/README.md`

**Команды для Owner:**
```powershell
py -3 IMPERIUM_TEST_VERSION\ORGANS\MECHANICUS\SCRIPTS\script_scanner.py --repo-root E:\IMPERIUM
py -3 IMPERIUM_TEST_VERSION\ORGANS\MECHANICUS\SCRIPTS\script_health_check.py --repo-root E:\IMPERIUM
```

**Вердикт:** PASS

---

### ЭТАП 3: Inquisition MVP

**Что сделано:**
- Создан `ORGAN_CONTRACT.json` для Inquisition
- `WARNING_BUDGET.json` — бюджет предупреждений
- Скрипт `fake_green_detector.py` — детектор fake PASS
- Скрипт `stale_truth_detector.py` — детектор устаревших данных
- Скрипт `full_audit.py` — полный аудит

**Файлы:**
- `ORGANS/INQUISITION/ORGAN_CONTRACT.json`
- `ORGANS/INQUISITION/WARNING_BUDGET.json`
- `ORGANS/INQUISITION/SCRIPTS/fake_green_detector.py`
- `ORGANS/INQUISITION/SCRIPTS/stale_truth_detector.py`
- `ORGANS/INQUISITION/SCRIPTS/full_audit.py`

**Команды для Owner:**
```powershell
py -3 IMPERIUM_TEST_VERSION\ORGANS\INQUISITION\SCRIPTS\full_audit.py --repo-root E:\IMPERIUM
```

**Вердикт:** PASS

---

### ЭТАП 4: Truth Contract

**Что сделано:**
- Создан `truth_contract_v1.md` — спецификация truth claims

**Файлы:**
- `schemas/truth_contract_v1.md`

**Вердикт:** PASS

---

### ЭТАП 5: Error Memory

**Что сделано:**
- Создана структура `KNOWN_ERRORS/`
- Индекс известных ошибок
- Две записи: raw subprocess, warning flood
- Скрипт `error_precheck.py` — проверка на известные паттерны ошибок

**Файлы:**
- `ORGANS/ADMINISTRATUM/KNOWN_ERRORS/README.md`
- `ORGANS/ADMINISTRATUM/KNOWN_ERRORS/KNOWN_ERRORS_INDEX.json`
- `ORGANS/ADMINISTRATUM/KNOWN_ERRORS/errors/ERR-0001.json`
- `ORGANS/ADMINISTRATUM/KNOWN_ERRORS/errors/ERR-0002.json`
- `ORGANS/ADMINISTRATUM/SCRIPTS/error_precheck.py`

**Вердикт:** PASS

---

### ЭТАП 6: Agent Control

**Что сделано:**
- `SCOPE_CORRIDOR.json` — разрешённые/запрещённые зоны
- `OUTPUT_CONTRACT.json` — требования к выходным данным агентов

**Файлы:**
- `ORGANS/OFFICIO_AGENTIS/SCOPE_CORRIDOR.json`
- `ORGANS/OFFICIO_AGENTIS/OUTPUT_CONTRACT.json`

**Вердикт:** PASS

---

## СЕССИЯ 2: 2026-05-15 (продолжение)

### ЭТАП 7: Self-Inventory & Self-Diagnosis

**Что сделано:**
- Скрипт `self_inventory.py` — полная инвентаризация системы
- Скрипт `self_diagnosis.py` — диагностика проблем и bottlenecks

**Файлы:**
- `ORGANS/ADMINISTRATUM/SCRIPTS/self_inventory.py`
- `ORGANS/ADMINISTRATUM/SCRIPTS/self_diagnosis.py`

**Команды для Owner:**
```powershell
py -3 IMPERIUM_TEST_VERSION\ORGANS\ADMINISTRATUM\SCRIPTS\self_inventory.py --repo-root E:\IMPERIUM
py -3 IMPERIUM_TEST_VERSION\ORGANS\ADMINISTRATUM\SCRIPTS\self_diagnosis.py --repo-root E:\IMPERIUM
```

**Вердикт:** PASS

---

### ЭТАП 8: KPI Registry & Monitoring

**Что сделано:**
- `KPI_REGISTRY.json` — реестр 10 KPI
- `kpi_collector.py` — сборщик KPI с оценкой статуса

**Файлы:**
- `MONITORING/KPI_REGISTRY.json`
- `MONITORING/kpi_collector.py`

**Команды для Owner:**
```powershell
py -3 IMPERIUM_TEST_VERSION\MONITORING\kpi_collector.py --repo-root E:\IMPERIUM
```

**Вердикт:** PASS

---

### ЭТАП 9: Sanctum Mirror

**Что сделано:**
- `SANCTUM_MIRROR/README.md` — документация
- `SANCTUM_MIRROR/dashboard.html` — HTML dashboard для обзора

**Файлы:**
- `SANCTUM_MIRROR/README.md`
- `SANCTUM_MIRROR/dashboard.html`

**Что открыть Owner:**
- Открыть `dashboard.html` в браузере

**Вердикт:** PASS

---

### ЭТАП 10: Research / Reference Review

**Что сделано:**
- Анализ 35+ внешних проектов
- Топ-10 рекомендаций для IMPERIUM
- Категоризация по приоритету и риску

**Файлы:**
- `RESEARCH/REFERENCE_REVIEW_RU.md`
- `RESEARCH/reference_review.json`

**Топ рекомендации:**
1. Pydantic — validation
2. Typer — CLI
3. pre-commit — git hooks
4. Ruff — linting
5. pytest-qt — Qt testing

**Вердикт:** PASS

---

### ЭТАП 11: Дополнительные Known Errors

**Что сделано:**
- Добавлены 3 новые ошибки в базу
- ERR-0003: Mojibake/encoding
- ERR-0004: Stale dashboard HEAD
- ERR-0005: Fake PASS without evidence

**Файлы:**
- `ORGANS/ADMINISTRATUM/KNOWN_ERRORS/errors/ERR-0003.json`
- `ORGANS/ADMINISTRATUM/KNOWN_ERRORS/errors/ERR-0004.json`
- `ORGANS/ADMINISTRATUM/KNOWN_ERRORS/errors/ERR-0005.json`

**Вердикт:** PASS

---

### ЭТАП 12: Receipt Prototype

**Что сделано:**
- `RECEIPT_SCHEMA.md` — схема квитанций
- Первая квитанция создана

**Файлы:**
- `RECEIPTS/RECEIPT_SCHEMA.md`
- `RECEIPTS/RCP-20260515-220000-0001.json`

**Вердикт:** PASS

---

### ЭТАП 13: Owner Review Pack

**Что сделано:**
- `OWNER_REVIEW_RU.md` — полный обзор для Owner

**Файлы:**
- `OWNER_REVIEW_RU.md`

**Вердикт:** PASS

---

## ИТОГО НА ДАННЫЙ МОМЕНТ

| Компонент | Статус | Файлов |
|-----------|--------|--------|
| Baseline | ✅ DONE | 2 |
| Testing Field | ✅ DONE | 8 |
| Mechanicus | ✅ DONE | 5 |
| Inquisition | ✅ DONE | 5 |
| Truth Contract | ✅ DONE | 1 |
| Error Memory | ✅ DONE | 5 |
| Agent Control | ✅ DONE | 2 |
| **ВСЕГО** | | **28** |

---

## ЧТО OWNER МОЖЕТ СДЕЛАТЬ СЕЙЧАС

1. Открыть `E:\IMPERIUM\IMPERIUM_TEST_VERSION\` в проводнике
2. Запустить smoke test: `py -3 IMPERIUM_TEST_VERSION\TESTING_FIELD\SCRIPTS\smoke_sanctum.py`
3. Запустить script scan: `py -3 IMPERIUM_TEST_VERSION\ORGANS\MECHANICUS\SCRIPTS\script_scanner.py --repo-root E:\IMPERIUM`
4. Запустить full audit: `py -3 IMPERIUM_TEST_VERSION\ORGANS\INQUISITION\SCRIPTS\full_audit.py --repo-root E:\IMPERIUM`
5. Удалить эксперимент: `Remove-Item -Recurse -Force E:\IMPERIUM\IMPERIUM_TEST_VERSION`


---

## СЕССИЯ 3: 2026-05-15 (продолжение)

### ЭТАП 14: Рабочие Петли (Working Loops)

**Что сделано:**
- Созданы PowerShell скрипты для трёх рабочих петель:
  - `TESTING_FIELD/RUN_SMOKE.ps1` — smoke test (5 проверок)
  - `ORGANS/MECHANICUS/RUN_SCRIPT_HEALTH.ps1` — проверка здоровья скриптов
  - `ORGANS/INQUISITION/RUN_AUDIT.ps1` — аудит fake green / stale truth
- Каждый скрипт создаёт:
  - JSON report с данными
  - JSON receipt с метаданными
  - HTML dashboard (для Mechanicus и Inquisition)

**Результаты запуска:**
- Smoke Test: PASS (5/5 checks)
- Script Health: 823/824 healthy (99.9%)
- Audit: FAIL (100 issues: 2 fake green, 98 stale truth)

**Файлы:**
- `TESTING_FIELD/RUN_SMOKE.ps1`
- `ORGANS/MECHANICUS/RUN_SCRIPT_HEALTH.ps1`
- `ORGANS/INQUISITION/RUN_AUDIT.ps1`

**Вердикт:** PASS

---

### ЭТАП 15: Master Script & Dynamic Dashboard

**Что сделано:**
- `RUN_ALL.ps1` — мастер-скрипт, запускает все петли
- `SANCTUM_MIRROR/GENERATE_INDEX.ps1` — генерирует dashboard из reports
- Dashboard показывает реальные данные из JSON reports

**Файлы:**
- `RUN_ALL.ps1`
- `SANCTUM_MIRROR/GENERATE_INDEX.ps1`

**Команды для Owner:**
```powershell
.\IMPERIUM_TEST_VERSION\RUN_ALL.ps1
```

**Что открыть Owner:**
- `IMPERIUM_TEST_VERSION\SANCTUM_MIRROR\index.html`

**Вердикт:** PASS

---

## ИТОГО НА ДАННЫЙ МОМЕНТ

| Компонент | Статус | Файлов |
|-----------|--------|--------|
| Baseline | ✅ DONE | 2 |
| Testing Field | ✅ DONE | 9 |
| Mechanicus | ✅ DONE | 6 |
| Inquisition | ✅ DONE | 6 |
| Truth Contract | ✅ DONE | 1 |
| Error Memory | ✅ DONE | 5 |
| Agent Control | ✅ DONE | 2 |
| Self-Inventory | ✅ DONE | 2 |
| KPI/Monitoring | ✅ DONE | 2 |
| Sanctum Mirror | ✅ DONE | 3 |
| Research | ✅ DONE | 2 |
| Receipts | ✅ DONE | 2+ |
| Master Script | ✅ DONE | 1 |
| **ВСЕГО** | | **43+** |

---

## ЧТО OWNER МОЖЕТ СДЕЛАТЬ СЕЙЧАС

### Быстрый старт:
```powershell
cd E:\IMPERIUM
.\IMPERIUM_TEST_VERSION\RUN_ALL.ps1
start .\IMPERIUM_TEST_VERSION\SANCTUM_MIRROR\index.html
```

### Отдельные петли:
```powershell
# Smoke test
.\IMPERIUM_TEST_VERSION\TESTING_FIELD\RUN_SMOKE.ps1

# Script health
.\IMPERIUM_TEST_VERSION\ORGANS\MECHANICUS\RUN_SCRIPT_HEALTH.ps1

# Audit
.\IMPERIUM_TEST_VERSION\ORGANS\INQUISITION\RUN_AUDIT.ps1

# Regenerate dashboard
.\IMPERIUM_TEST_VERSION\SANCTUM_MIRROR\GENERATE_INDEX.ps1
```

### Dashboards:
- Main: `IMPERIUM_TEST_VERSION\SANCTUM_MIRROR\index.html`
- Mechanicus: `IMPERIUM_TEST_VERSION\ORGANS\MECHANICUS\DASHBOARD\index.html`
- Inquisition: `IMPERIUM_TEST_VERSION\ORGANS\INQUISITION\DASHBOARD\index.html`

### Удалить эксперимент:
```powershell
Remove-Item -Recurse -Force E:\IMPERIUM\IMPERIUM_TEST_VERSION
```

---

## СЕССИЯ 4: 2026-05-15 (продолжение)

### ЭТАП 16: Second Brain / Active Memory

**Что сделано:**
- Создана структура `SECOND_BRAIN/` — активная память агента
- `MEMORY_SCHEMA.json` — схема памяти
- `GOALS.json` — цели проекта
- `RULES.json` — правила работы
- `CONSTRAINTS.json` — ограничения
- `KNOWN_ERRORS_LINKS.json` — ссылки на известные ошибки
- `CONTEXT_INDEX.json` — индекс контекста
- `OWNER_PROFILE_SEED.json` — профиль Owner
- `MEMORY_QUERIES.json` — типовые запросы к памяти

**Скрипты:**
- `ask_memory.py` — запрос к памяти (TESTED ✅)
- `build_memory_summary.py` — сборка сводки памяти (TESTED ✅)
- `update_memory.py` — обновление памяти

**Файлы:**
- `SECOND_BRAIN/MEMORY_SCHEMA.json`
- `SECOND_BRAIN/GOALS.json`
- `SECOND_BRAIN/RULES.json`
- `SECOND_BRAIN/CONSTRAINTS.json`
- `SECOND_BRAIN/KNOWN_ERRORS_LINKS.json`
- `SECOND_BRAIN/CONTEXT_INDEX.json`
- `SECOND_BRAIN/OWNER_PROFILE_SEED.json`
- `SECOND_BRAIN/MEMORY_QUERIES.json`
- `SECOND_BRAIN/README_RU.md`
- `SECOND_BRAIN/SCRIPTS/ask_memory.py`
- `SECOND_BRAIN/SCRIPTS/build_memory_summary.py`
- `SECOND_BRAIN/SCRIPTS/update_memory.py`

**Команды для Owner:**
```powershell
py -3 IMPERIUM_TEST_VERSION\SECOND_BRAIN\SCRIPTS\ask_memory.py --query goals
py -3 IMPERIUM_TEST_VERSION\SECOND_BRAIN\SCRIPTS\build_memory_summary.py
```

**Вердикт:** PASS

---

### ЭТАП 17: Agent Memory Protocol

**Что сделано:**
- Создана структура `AGENT_MEMORY_PROTOCOL/`
- `AGENT_MEMORY_PROTOCOL.md` — документация протокола
- `REQUIRED_MEMORY_QUERIES.json` — обязательные запросы
- `AGENT_CONTEXT_HANDSHAKE.json` — формат handshake

**Скрипты:**
- `agent_context_handshake.py` — выполняет handshake при старте агента (TESTED ✅)

**Файлы:**
- `AGENT_MEMORY_PROTOCOL/AGENT_MEMORY_PROTOCOL.md`
- `AGENT_MEMORY_PROTOCOL/REQUIRED_MEMORY_QUERIES.json`
- `AGENT_MEMORY_PROTOCOL/AGENT_CONTEXT_HANDSHAKE.json`
- `AGENT_MEMORY_PROTOCOL/SCRIPTS/agent_context_handshake.py`

**Команды для Owner:**
```powershell
py -3 IMPERIUM_TEST_VERSION\AGENT_MEMORY_PROTOCOL\SCRIPTS\agent_context_handshake.py
```

**Вердикт:** PASS

---

### ЭТАП 18: Live Workbench

**Что сделано:**
- Создана структура `LIVE_WORKBENCH/`
- Sandbox project — калькулятор (calculator.py)
- Тесты — 6 тестов (test_calculator.py)
- Все тесты проходят

**Скрипты:**
- `run_sandbox_tests.py` — запуск тестов sandbox (TESTED ✅, fixed encoding)
- `generate_workbench_status.py` — генерация статуса (TESTED ✅)

**Файлы:**
- `LIVE_WORKBENCH/README_RU.md`
- `LIVE_WORKBENCH/SANDBOX_PROJECT/calculator.py`
- `LIVE_WORKBENCH/SANDBOX_PROJECT/test_calculator.py`
- `LIVE_WORKBENCH/SCRIPTS/run_sandbox_tests.py`
- `LIVE_WORKBENCH/SCRIPTS/generate_workbench_status.py`

**Команды для Owner:**
```powershell
py -3 IMPERIUM_TEST_VERSION\LIVE_WORKBENCH\SCRIPTS\run_sandbox_tests.py
py -3 IMPERIUM_TEST_VERSION\LIVE_WORKBENCH\SCRIPTS\generate_workbench_status.py
```

**Вердикт:** PASS

---

### ЭТАП 19: UF99 Prompt Standard

**Что сделано:**
- Создана структура `PROMPT_STANDARD/UF99/`
- 7 шаблонов промптов:
  - `UF99_CORE.md` — базовый шаблон
  - `UF99_REPAIR.md` — ремонт/исправление
  - `UF99_FEATURE.md` — новая функция
  - `UF99_TEST.md` — тестирование
  - `UF99_RESEARCH.md` — исследование
  - `UF99_REVIEW.md` — ревью
  - `UF99_WORK.md` — рабочая задача
- `UF99_CHECKLIST.json` — чеклист валидации

**Скрипты:**
- `validate_uf99_prompt.py` — валидатор промптов (TESTED ✅)

**Файлы:**
- `PROMPT_STANDARD/UF99/UF99_CORE.md`
- `PROMPT_STANDARD/UF99/UF99_REPAIR.md`
- `PROMPT_STANDARD/UF99/UF99_FEATURE.md`
- `PROMPT_STANDARD/UF99/UF99_TEST.md`
- `PROMPT_STANDARD/UF99/UF99_RESEARCH.md`
- `PROMPT_STANDARD/UF99/UF99_REVIEW.md`
- `PROMPT_STANDARD/UF99/UF99_WORK.md`
- `PROMPT_STANDARD/UF99/UF99_CHECKLIST.json`
- `PROMPT_STANDARD/UF99/SCRIPTS/validate_uf99_prompt.py`
- `PROMPT_STANDARD/UF99/EXAMPLES/example_repair_prompt.md`

**Команды для Owner:**
```powershell
py -3 IMPERIUM_TEST_VERSION\PROMPT_STANDARD\UF99\SCRIPTS\validate_uf99_prompt.py --file IMPERIUM_TEST_VERSION\PROMPT_STANDARD\UF99\EXAMPLES\example_repair_prompt.md
```

**Вердикт:** PASS

---

### ЭТАП 20: Communication Protocol

**Что сделано:**
- Создана структура `COMMUNICATION_PROTOCOL/`
- `COMMUNICATION_PROTOCOL_RU.md` — документация протокола
- `MESSAGE_TYPES.json` — типы сообщений
- `STATUS_FORMATS.json` — форматы статусов
- `STOP_ESCALATION_RULES.md` — правила эскалации и остановки

**Файлы:**
- `COMMUNICATION_PROTOCOL/COMMUNICATION_PROTOCOL_RU.md`
- `COMMUNICATION_PROTOCOL/MESSAGE_TYPES.json`
- `COMMUNICATION_PROTOCOL/STATUS_FORMATS.json`
- `COMMUNICATION_PROTOCOL/STOP_ESCALATION_RULES.md`

**Вердикт:** PASS

---

### ЭТАП 21: Integration & Dashboard Update

**Что сделано:**
- Обновлён `SANCTUM_MIRROR/GENERATE_INDEX.ps1` v2.0:
  - Добавлены секции для Second Brain
  - Добавлены секции для Agent Memory Protocol
  - Добавлены секции для Live Workbench
  - Добавлены секции для UF99 Prompt Standard
  - Добавлены секции для Communication Protocol
  - Новый дизайн с категориями
- Обновлён `RUN_ALL.ps1` v2.0:
  - Добавлен запуск `build_memory_summary.py`
  - Добавлен запуск `run_sandbox_tests.py`
  - Добавлен запуск `generate_workbench_status.py`
  - Добавлен запуск `agent_context_handshake.py`
  - Параметры `-SkipNewComponents`, `-OnlyCore`
- Обновлён `OWNER_CHRONOLOGY_RU.md` с этапами 16-21
- Обновлён `OWNER_REVIEW_RU.md`

**Файлы:**
- `SANCTUM_MIRROR/GENERATE_INDEX.ps1` (updated)
- `RUN_ALL.ps1` (updated)
- `OWNER_CHRONOLOGY_RU.md` (updated)
- `OWNER_REVIEW_RU.md` (updated)

**Команды для Owner:**
```powershell
.\IMPERIUM_TEST_VERSION\RUN_ALL.ps1
start .\IMPERIUM_TEST_VERSION\SANCTUM_MIRROR\index.html
```

**Вердикт:** PASS

---

## ИТОГО НА ДАННЫЙ МОМЕНТ (v2.0)

| Компонент | Статус | Файлов | Скриптов |
|-----------|--------|--------|----------|
| Baseline | ✅ DONE | 2 | 0 |
| Testing Field | ✅ DONE | 9 | 3 |
| Mechanicus | ✅ DONE | 6 | 3 |
| Inquisition | ✅ DONE | 6 | 3 |
| Truth Contract | ✅ DONE | 1 | 0 |
| Error Memory | ✅ DONE | 5 | 1 |
| Agent Control | ✅ DONE | 2 | 0 |
| Self-Inventory | ✅ DONE | 2 | 2 |
| KPI/Monitoring | ✅ DONE | 2 | 1 |
| Sanctum Mirror | ✅ DONE | 4 | 1 |
| Research | ✅ DONE | 2 | 0 |
| Receipts | ✅ DONE | 25+ | 0 |
| Master Script | ✅ DONE | 1 | 0 |
| **Second Brain** | ✅ NEW | 12 | 3 |
| **Agent Memory Protocol** | ✅ NEW | 4 | 1 |
| **Live Workbench** | ✅ NEW | 6 | 2 |
| **UF99 Prompt Standard** | ✅ NEW | 10 | 1 |
| **Communication Protocol** | ✅ NEW | 4 | 0 |
| **ВСЕГО** | | **95+** | **21** |

---

## ЧТО OWNER МОЖЕТ СДЕЛАТЬ СЕЙЧАС (v2.0)

### Быстрый старт:
```powershell
cd E:\IMPERIUM
.\IMPERIUM_TEST_VERSION\RUN_ALL.ps1
start .\IMPERIUM_TEST_VERSION\SANCTUM_MIRROR\index.html
```

### Только core системы:
```powershell
.\IMPERIUM_TEST_VERSION\RUN_ALL.ps1 -OnlyCore
```

### Отдельные новые компоненты:
```powershell
# Second Brain
py -3 .\IMPERIUM_TEST_VERSION\SECOND_BRAIN\SCRIPTS\ask_memory.py --query goals
py -3 .\IMPERIUM_TEST_VERSION\SECOND_BRAIN\SCRIPTS\build_memory_summary.py

# Live Workbench
py -3 .\IMPERIUM_TEST_VERSION\LIVE_WORKBENCH\SCRIPTS\run_sandbox_tests.py
py -3 .\IMPERIUM_TEST_VERSION\LIVE_WORKBENCH\SCRIPTS\generate_workbench_status.py

# Agent Memory Protocol
py -3 .\IMPERIUM_TEST_VERSION\AGENT_MEMORY_PROTOCOL\SCRIPTS\agent_context_handshake.py

# UF99 Prompt Validator
py -3 .\IMPERIUM_TEST_VERSION\PROMPT_STANDARD\UF99\SCRIPTS\validate_uf99_prompt.py --file <prompt_file>
```

### Dashboards:
- Main: `IMPERIUM_TEST_VERSION\SANCTUM_MIRROR\index.html`
- Mechanicus: `IMPERIUM_TEST_VERSION\ORGANS\MECHANICUS\DASHBOARD\index.html`
- Inquisition: `IMPERIUM_TEST_VERSION\ORGANS\INQUISITION\DASHBOARD\index.html`

### Удалить эксперимент:
```powershell
Remove-Item -Recurse -Force E:\IMPERIUM\IMPERIUM_TEST_VERSION
```
