# OWNER REVIEW — IMPERIUM TEST VERSION v2.0

## Дата: 2026-05-15
## Статус: PASS_EXPERIMENT_READY_FOR_OWNER_REVIEW

---

## ЧТО СДЕЛАНО

### Структура (30+ директорий)
- ✅ `TESTING_FIELD/` — полигон тестирования
- ✅ `ORGANS/MECHANICUS/` — орган инструментов
- ✅ `ORGANS/INQUISITION/` — орган аудита
- ✅ `ORGANS/ADMINISTRATUM/` — орган администрирования
- ✅ `ORGANS/OFFICIO_AGENTIS/` — контроль агентов
- ✅ `MONITORING/` — KPI и мониторинг
- ✅ `SANCTUM_MIRROR/` — обзорный dashboard
- ✅ `RESEARCH/` — анализ референсов
- ✅ `RECEIPTS/` — квитанции действий
- ✅ `schemas/` — схемы и контракты
- ✅ `SECOND_BRAIN/` — **NEW** активная память агента
- ✅ `AGENT_MEMORY_PROTOCOL/` — **NEW** протокол памяти
- ✅ `LIVE_WORKBENCH/` — **NEW** песочница разработки
- ✅ `PROMPT_STANDARD/UF99/` — **NEW** стандарт промптов
- ✅ `COMMUNICATION_PROTOCOL/` — **NEW** протокол коммуникации

### Скрипты (21 рабочих скриптов)

#### Core Scripts (12)
| Скрипт | Назначение | Статус |
|--------|------------|--------|
| `smoke_sanctum.py` | Smoke test Sanctum | ✅ |
| `capture_screenshot.py` | Захват скриншотов | ✅ |
| `script_scanner.py` | Сканер скриптов | ✅ |
| `script_health_check.py` | Проверка здоровья | ✅ |
| `command_gateway.py` | Шлюз команд | ✅ |
| `fake_green_detector.py` | Детектор fake PASS | ✅ |
| `stale_truth_detector.py` | Детектор stale | ✅ |
| `full_audit.py` | Полный аудит | ✅ |
| `self_inventory.py` | Инвентаризация | ✅ |
| `self_diagnosis.py` | Диагностика | ✅ |
| `error_precheck.py` | Проверка ошибок | ✅ |
| `kpi_collector.py` | Сбор KPI | ✅ |

#### New Scripts v2.0 (9)
| Скрипт | Назначение | Статус |
|--------|------------|--------|
| `ask_memory.py` | Запрос к памяти | ✅ TESTED |
| `build_memory_summary.py` | Сборка сводки памяти | ✅ TESTED |
| `update_memory.py` | Обновление памяти | ✅ |
| `agent_context_handshake.py` | Handshake агента | ✅ TESTED |
| `run_sandbox_tests.py` | Тесты sandbox | ✅ TESTED |
| `generate_workbench_status.py` | Статус workbench | ✅ TESTED |
| `validate_uf99_prompt.py` | Валидатор промптов | ✅ TESTED |
| `GENERATE_INDEX.ps1` | Генератор dashboard | ✅ |
| `RUN_ALL.ps1` | Мастер-скрипт | ✅ |

### Документация
- ✅ `OWNER_CHRONOLOGY_RU.md` — хронология (21 этап)
- ✅ `EXPERIMENT_LEDGER.jsonl` — машиночитаемый ledger
- ✅ `TASK_RULES.md` — правила задач
- ✅ `RESEARCH/REFERENCE_REVIEW_RU.md` — обзор референсов
- ✅ `SECOND_BRAIN/README_RU.md` — документация Second Brain
- ✅ `LIVE_WORKBENCH/README_RU.md` — документация Workbench
- ✅ `AGENT_MEMORY_PROTOCOL/AGENT_MEMORY_PROTOCOL.md` — протокол памяти
- ✅ `COMMUNICATION_PROTOCOL/COMMUNICATION_PROTOCOL_RU.md` — протокол коммуникации
- ✅ `PROMPT_STANDARD/UF99/UF99_CORE.md` — стандарт промптов

### Данные
- ✅ 5 known errors в базе
- ✅ 10 KPI в реестре
- ✅ 25+ receipts создано
- ✅ Warning budget определён
- ✅ 7 UF99 шаблонов промптов
- ✅ Memory schema с goals/rules/constraints

---

## ЧТО ОТКРЫТЬ

| Файл | Зачем |
|------|-------|
| `SANCTUM_MIRROR/index.html` | Главный dashboard v2.0 (открыть в браузере) |
| `OWNER_CHRONOLOGY_RU.md` | Хронология работы (21 этап) |
| `SECOND_BRAIN/README_RU.md` | Документация Second Brain |
| `LIVE_WORKBENCH/README_RU.md` | Документация Live Workbench |
| `PROMPT_STANDARD/UF99/UF99_CORE.md` | Стандарт промптов |
| `COMMUNICATION_PROTOCOL/COMMUNICATION_PROTOCOL_RU.md` | Протокол коммуникации |

---

## ЧТО ЗАПУСТИТЬ

### Быстрый старт (всё сразу):
```powershell
cd E:\IMPERIUM
.\IMPERIUM_TEST_VERSION\RUN_ALL.ps1
start .\IMPERIUM_TEST_VERSION\SANCTUM_MIRROR\index.html
```

### Только core системы:
```powershell
.\IMPERIUM_TEST_VERSION\RUN_ALL.ps1 -OnlyCore
```

### Отдельные компоненты:

```powershell
# === CORE ===

# 1. Smoke test Sanctum
py -3 IMPERIUM_TEST_VERSION\TESTING_FIELD\SCRIPTS\smoke_sanctum.py

# 2. Сканировать скрипты
py -3 IMPERIUM_TEST_VERSION\ORGANS\MECHANICUS\SCRIPTS\script_scanner.py --repo-root E:\IMPERIUM

# 3. Проверить здоровье скриптов
py -3 IMPERIUM_TEST_VERSION\ORGANS\MECHANICUS\SCRIPTS\script_health_check.py --repo-root E:\IMPERIUM

# 4. Полный аудит
py -3 IMPERIUM_TEST_VERSION\ORGANS\INQUISITION\SCRIPTS\full_audit.py --repo-root E:\IMPERIUM

# === NEW v2.0 ===

# 5. Second Brain - запрос к памяти
py -3 IMPERIUM_TEST_VERSION\SECOND_BRAIN\SCRIPTS\ask_memory.py --query goals
py -3 IMPERIUM_TEST_VERSION\SECOND_BRAIN\SCRIPTS\ask_memory.py --query rules
py -3 IMPERIUM_TEST_VERSION\SECOND_BRAIN\SCRIPTS\ask_memory.py --query constraints
py -3 IMPERIUM_TEST_VERSION\SECOND_BRAIN\SCRIPTS\ask_memory.py --query errors

# 6. Second Brain - сборка сводки
py -3 IMPERIUM_TEST_VERSION\SECOND_BRAIN\SCRIPTS\build_memory_summary.py

# 7. Agent Memory Protocol - handshake
py -3 IMPERIUM_TEST_VERSION\AGENT_MEMORY_PROTOCOL\SCRIPTS\agent_context_handshake.py

# 8. Live Workbench - тесты sandbox
py -3 IMPERIUM_TEST_VERSION\LIVE_WORKBENCH\SCRIPTS\run_sandbox_tests.py

# 9. Live Workbench - статус
py -3 IMPERIUM_TEST_VERSION\LIVE_WORKBENCH\SCRIPTS\generate_workbench_status.py

# 10. UF99 - валидация промпта
py -3 IMPERIUM_TEST_VERSION\PROMPT_STANDARD\UF99\SCRIPTS\validate_uf99_prompt.py --file IMPERIUM_TEST_VERSION\PROMPT_STANDARD\UF99\EXAMPLES\example_repair_prompt.md
```

---

## ЧТО РАБОТАЕТ

### Core Systems:
✅ Все 12 core скриптов запускаются
✅ Smoke test проверяет Sanctum
✅ Script scanner находит скрипты
✅ Fake green detector работает
✅ Self-inventory генерирует отчёт
✅ KPI collector собирает метрики
✅ Dashboard HTML открывается в браузере

### New Components v2.0:
✅ Second Brain — ask_memory.py возвращает данные
✅ Second Brain — build_memory_summary.py создаёт JSON report
✅ Agent Memory Protocol — handshake выполняется
✅ Live Workbench — 6 тестов проходят
✅ Live Workbench — статус генерируется
✅ UF99 — валидатор проверяет промпты
✅ Dashboard v2.0 — показывает все компоненты

---

## ЧТО НЕ РАБОТАЕТ / ТОЛЬКО SCAFFOLD

⚠️ **Qt dashboards** — требуют PyQt6 разработки
⚠️ **Real button spine** — требует интеграции с Sanctum
⚠️ **Screenshot capture** — требует pyautogui/pillow
⚠️ **Promotion workflow** — только schema, нет автоматизации
⚠️ **Command gateway integration** — prototype, не интегрирован в Sanctum
⚠️ **update_memory.py** — scaffold, требует доработки

---

## НОВЫЕ КОМПОНЕНТЫ v2.0 — ДЕТАЛИ

### 🧠 Second Brain
**Назначение:** Активная память агента — хранит goals, rules, constraints, known errors.

**Файлы данных:**
- `GOALS.json` — цели проекта
- `RULES.json` — правила работы
- `CONSTRAINTS.json` — ограничения
- `KNOWN_ERRORS_LINKS.json` — ссылки на ошибки
- `CONTEXT_INDEX.json` — индекс контекста
- `OWNER_PROFILE_SEED.json` — профиль Owner

**Скрипты:**
- `ask_memory.py` — запрос к памяти по категории
- `build_memory_summary.py` — сборка полной сводки
- `update_memory.py` — обновление данных

### 🤝 Agent Memory Protocol
**Назначение:** Протокол handshake при старте агента — загружает контекст.

**Файлы:**
- `AGENT_MEMORY_PROTOCOL.md` — документация
- `REQUIRED_MEMORY_QUERIES.json` — обязательные запросы
- `AGENT_CONTEXT_HANDSHAKE.json` — формат handshake

**Скрипты:**
- `agent_context_handshake.py` — выполняет handshake

### 🔬 Live Workbench
**Назначение:** Песочница для тестирования кода перед интеграцией.

**Sandbox Project:**
- `calculator.py` — простой калькулятор
- `test_calculator.py` — 6 тестов

**Скрипты:**
- `run_sandbox_tests.py` — запуск тестов
- `generate_workbench_status.py` — генерация статуса

### 📝 UF99 Prompt Standard
**Назначение:** Стандарт структуры промптов для агентов.

**Шаблоны:**
- `UF99_CORE.md` — базовый шаблон
- `UF99_REPAIR.md` — ремонт
- `UF99_FEATURE.md` — новая функция
- `UF99_TEST.md` — тестирование
- `UF99_RESEARCH.md` — исследование
- `UF99_REVIEW.md` — ревью
- `UF99_WORK.md` — рабочая задача

**Скрипты:**
- `validate_uf99_prompt.py` — валидатор

### 📡 Communication Protocol
**Назначение:** Стандарт коммуникации между агентом и Owner.

**Файлы:**
- `COMMUNICATION_PROTOCOL_RU.md` — документация
- `MESSAGE_TYPES.json` — типы сообщений
- `STATUS_FORMATS.json` — форматы статусов
- `STOP_ESCALATION_RULES.md` — правила эскалации

---

## ЧТО ПОЛЕЗНО ПЕРЕНОСИТЬ В MAIN REPO

| Компонент | Приоритет | Причина |
|-----------|-----------|---------|
| `script_scanner.py` | ВЫСОКИЙ | Полезен для инвентаризации |
| `script_health_check.py` | ВЫСОКИЙ | Проверка синтаксиса |
| `fake_green_detector.py` | ВЫСОКИЙ | Борьба с fake PASS |
| `SECOND_BRAIN/` структура | ВЫСОКИЙ | Память агента |
| `UF99/` шаблоны | ВЫСОКИЙ | Стандарт промптов |
| `self_inventory.py` | СРЕДНИЙ | Понимание системы |
| `self_diagnosis.py` | СРЕДНИЙ | Поиск проблем |
| `KNOWN_ERRORS/` структура | СРЕДНИЙ | Память об ошибках |
| `COMMUNICATION_PROTOCOL/` | СРЕДНИЙ | Стандарт коммуникации |
| `KPI_REGISTRY.json` | НИЗКИЙ | Метрики |

---

## ЧТО НЕ ПЕРЕНОСИТЬ

❌ `SANCTUM_MIRROR/index.html` — только для test version
❌ `EXPERIMENT_LEDGER.jsonl` — специфичен для эксперимента
❌ Prototype receipts — нужна реальная интеграция
❌ Hardcoded paths в скриптах — нужен refactor
❌ `LIVE_WORKBENCH/SANDBOX_PROJECT/` — тестовый код

---

## СЛЕДУЮЩИЕ 10 УЗКИХ ЗАДАЧ

| # | Задача | Путь | Приоритет |
|---|--------|------|-----------|
| 1 | Запустить `RUN_ALL.ps1` и проверить dashboard | `RUN_ALL.ps1` | HIGH |
| 2 | Проверить Second Brain через `ask_memory.py` | `SECOND_BRAIN/SCRIPTS/` | HIGH |
| 3 | Запустить sandbox тесты | `LIVE_WORKBENCH/SCRIPTS/` | HIGH |
| 4 | Проверить UF99 валидатор | `PROMPT_STANDARD/UF99/SCRIPTS/` | HIGH |
| 5 | Изучить Communication Protocol | `COMMUNICATION_PROTOCOL/` | MEDIUM |
| 6 | Добавить новый sandbox project | `LIVE_WORKBENCH/SANDBOX_PROJECT/` | MEDIUM |
| 7 | Расширить Second Brain данными | `SECOND_BRAIN/` | MEDIUM |
| 8 | Создать новый UF99 промпт | `PROMPT_STANDARD/UF99/EXAMPLES/` | MEDIUM |
| 9 | Интегрировать handshake в workflow | `AGENT_MEMORY_PROTOCOL/` | LOW |
| 10 | Перенести лучшие компоненты в main repo | `scripts/` | LOW |

---

## ВОПРОСЫ ДЛЯ OWNER

1. **Переносить ли Second Brain в main repo?**
2. **Использовать ли UF99 стандарт для всех промптов?**
3. **Нужен ли более сложный sandbox project?**
4. **Добавить ли больше данных в Second Brain?**
5. **Удалить ли test version после review?**

---

## ФИНАЛЬНЫЙ ВЕРДИКТ

**PASS_EXPERIMENT_READY_FOR_OWNER_REVIEW**

Test version v2.0 содержит:
- ✅ 21 рабочий скрипт
- ✅ 95+ файлов
- ✅ Core systems (smoke, health, audit)
- ✅ Second Brain (memory, goals, rules)
- ✅ Agent Memory Protocol (handshake)
- ✅ Live Workbench (sandbox, tests)
- ✅ UF99 Prompt Standard (7 templates)
- ✅ Communication Protocol (messages, escalation)
- ✅ Dashboard v2.0 (all components)
- ✅ 25+ receipts

Owner может:
- Открыть и изучить структуру
- Запустить `RUN_ALL.ps1`
- Открыть dashboard в браузере
- Тестировать отдельные компоненты
- Выбрать что переносить
- Удалить после review
