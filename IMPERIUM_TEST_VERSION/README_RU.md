# IMPERIUM TEST VERSION — СВОДКА

## Что это такое

**IMPERIUM_TEST_VERSION** — это экспериментальная лаборатория для развития системы IMPERIUM. Здесь тестируются новые компоненты, органы и workflow перед интеграцией в основной репозиторий.

---

## Что мы получили за эти сессии

### 🏗️ 7 завершённых фаз эволюции

| Фаза | Название | Результат |
|------|----------|-----------|
| 0 | Foundation | K00-K12 forensic synthesis, архитектура блоков |
| 1 | Truth Spine | Невозможность fake green, детекция stale truth |
| 2 | Missing Organs | 4 новых органа: Throne, Astronomicon, Strategium, Custodes |
| 3 | Registry Sync | Автоматическая синхронизация реестров |
| 4 | Frontend Projection | Дашборды из backend truth |
| 5 | Learning Loop | Автоматическое извлечение уроков и паттернов |
| 6 | Promotion Gates | Полный pipeline для promotion в canon |

### 🏛️ 10 функциональных органов

| Орган | Назначение | Ключевые скрипты |
|-------|------------|------------------|
| **ADMINISTRATUM** | Адресная книга, история, бандлы | self_inventory.py |
| **ASTRONOMICON** | Задачи, декомпозиция, stage maps | task_manager.py |
| **CUSTODES** | Границы, безопасность, private/public | boundary_checker.py |
| **DOCTRINARIUM** | Правила, схемы, контракты | smoke_doctrinarium.py |
| **INQUISITION** | Аудит, fake green police | full_audit.py, fake_green_detector.py |
| **MECHANICUS** | Инструменты, скрипты, command gateway | script_health_checker.py |
| **OFFICIO_AGENTIS** | Роли агентов, контракты | smoke_officio.py |
| **SCHOLA_IMPERIALIS** | Обучение, память, паттерны | lesson_extractor.py, anti_pattern_scanner.py |
| **STRATEGIUM** | Roadmap, приоритеты | roadmap_manager.py |
| **THRONE** | Owner authority, approval gates | promotion_workflow.py, uat_gate.py, canon_import.py |

### 📊 Ключевые метрики

| Метрика | Значение |
|---------|----------|
| Органы с контрактами | 10/10 |
| Органы с дашбордами | 10/10 |
| Скрипты | 824 |
| Здоровье скриптов | 99.9% |
| Извлечённые уроки | 54 |
| Обнаруженные anti-patterns | 4 |

---

## Структура Test Version

```
IMPERIUM_TEST_VERSION/
├── ORGANS/                      # 10 органов системы
│   ├── ADMINISTRATUM/
│   ├── ASTRONOMICON/
│   ├── CUSTODES/
│   ├── DOCTRINARIUM/
│   ├── INQUISITION/
│   ├── MECHANICUS/
│   ├── OFFICIO_AGENTIS/
│   ├── SCHOLA_IMPERIALIS/
│   ├── STRATEGIUM/
│   └── THRONE/
├── REGISTRY/                    # Реестры и синхронизация
│   ├── ORGAN_REGISTRY.json
│   ├── registry_sync.py
│   ├── drift_detector.py
│   └── auto_sync.py
├── TRUTH_SPINE/                 # Truth state management
│   ├── truth_aggregator.py
│   └── freshness_validator.py
├── SANCTUM_MIRROR/              # Дашборды
│   ├── dashboard_generator.py
│   ├── master_dashboard.html
│   └── index.html
├── SECOND_BRAIN/                # Память агента
│   ├── MEMORY/
│   └── SCRIPTS/
├── AGENT_MEMORY_PROTOCOL/       # Протокол памяти агента
├── LIVE_WORKBENCH/              # Sandbox для тестов
├── TESTING_FIELD/               # Smoke tests
├── KIRO_FORENSIC_SYNTHESIS/     # K00-K12 артефакты
├── RECEIPTS/                    # Квитанции операций
├── REPORTS/                     # Отчёты
└── RUN_ALL.ps1                  # Master script v2.2
```

---

## Соприкосновение с Main Repo

### Что есть в Test Version, чего нет в Main:

| Компонент | Test Version | Main Repo |
|-----------|--------------|-----------|
| 10 органов с контрактами | ✅ | ❌ (частично) |
| Truth Spine | ✅ | ❌ |
| Dashboard Generator | ✅ | ❌ |
| Learning Loop | ✅ | ❌ |
| Promotion Pipeline | ✅ | ❌ |
| Registry Auto-Sync | ✅ | ❌ |
| Agent Memory Protocol | ✅ | ❌ |
| RUN_ALL.ps1 v2.2 | ✅ | ❌ |

### Что общего:

| Компонент | Описание |
|-----------|----------|
| AGENTS.md | Правила для агентов (в main) |
| schemas/ | JSON схемы (в main) |
| scripts/ | Базовые скрипты (в main) |
| SANCTUM/ | UI runtime (в main) |

### Путь интеграции:

```
Test Version → UAT Approval → Bundle → Canon Import → Main Repo
```

---

## Как использовать

### Полный запуск всех проверок:
```powershell
.\IMPERIUM_TEST_VERSION\RUN_ALL.ps1
```

### Проверка статуса promotion:
```powershell
py -3 .\IMPERIUM_TEST_VERSION\ORGANS\THRONE\SCRIPTS\promotion_workflow.py --status
```

### Генерация дашбордов:
```powershell
py -3 .\IMPERIUM_TEST_VERSION\SANCTUM_MIRROR\dashboard_generator.py --all
```

### Извлечение уроков:
```powershell
py -3 .\IMPERIUM_TEST_VERSION\ORGANS\SCHOLA_IMPERIALIS\SCRIPTS\lesson_extractor.py
```

---

## Promotion Workflow

1. **Pre-flight checks** — `promotion_workflow.py --check`
2. **UAT Request** — `promotion_workflow.py --request-uat`
3. **Owner Approval** — `uat_gate.py --approve <id>`
4. **Bundle Creation** — `promotion_workflow.py --bundle`
5. **Canon Import** — `canon_import.py --prepare <bundle>`

---

## Статус

- **Все 7 фаз roadmap:** ✅ COMPLETE
- **Готовность к promotion:** Требуется исправление fake green и stale truth в main
- **Owner UAT:** Ожидает

---

*Документ создан: 2026-05-16*
