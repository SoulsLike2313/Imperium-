# SANCTUM MIRROR

## Зеркало / Обзор Test Version

Это НЕ production UI. Это экспериментальный обзор test version для Owner.

## Что здесь

| Компонент | Путь | Статус |
|-----------|------|--------|
| Dashboard HTML | `dashboard.html` | Prototype |
| Status JSON | `status.json` | Auto-generated |
| Quick Links | Ниже | — |

## Quick Links для Owner

### Testing Field
- 📁 `TESTING_FIELD/` — полигон тестирования
- 📋 `TESTING_FIELD/CHECKLISTS/SMOKE_CHECKLIST.md` — чеклист smoke
- 🔧 `TESTING_FIELD/SCRIPTS/smoke_sanctum.py` — smoke test

### Mechanicus
- 📁 `ORGANS/MECHANICUS/` — орган инструментов
- 📋 `ORGANS/MECHANICUS/ORGAN_CONTRACT.json` — контракт
- 🔧 `ORGANS/MECHANICUS/SCRIPTS/script_scanner.py` — сканер скриптов
- 🔧 `ORGANS/MECHANICUS/SCRIPTS/script_health_check.py` — проверка здоровья

### Inquisition
- 📁 `ORGANS/INQUISITION/` — орган аудита
- 📋 `ORGANS/INQUISITION/ORGAN_CONTRACT.json` — контракт
- 🔧 `ORGANS/INQUISITION/SCRIPTS/full_audit.py` — полный аудит
- ⚠️ `ORGANS/INQUISITION/WARNING_BUDGET.json` — бюджет предупреждений

### Administratum
- 📁 `ORGANS/ADMINISTRATUM/` — орган администрирования
- 🔧 `ORGANS/ADMINISTRATUM/SCRIPTS/self_inventory.py` — инвентаризация
- 🔧 `ORGANS/ADMINISTRATUM/SCRIPTS/self_diagnosis.py` — диагностика
- 📋 `ORGANS/ADMINISTRATUM/KNOWN_ERRORS/` — база известных ошибок

### Monitoring
- 📁 `MONITORING/` — мониторинг
- 📋 `MONITORING/KPI_REGISTRY.json` — реестр KPI
- 🔧 `MONITORING/kpi_collector.py` — сборщик KPI

### Documentation
- 📋 `OWNER_CHRONOLOGY_RU.md` — хронология для Owner
- 📋 `EXPERIMENT_LEDGER.jsonl` — машиночитаемый ledger
- 📋 `TASK_RULES.md` — правила задач

## Команды для Owner

```powershell
# Smoke test Sanctum
py -3 IMPERIUM_TEST_VERSION\TESTING_FIELD\SCRIPTS\smoke_sanctum.py

# Scan scripts
py -3 IMPERIUM_TEST_VERSION\ORGANS\MECHANICUS\SCRIPTS\script_scanner.py --repo-root E:\IMPERIUM

# Check script health
py -3 IMPERIUM_TEST_VERSION\ORGANS\MECHANICUS\SCRIPTS\script_health_check.py --repo-root E:\IMPERIUM

# Full audit
py -3 IMPERIUM_TEST_VERSION\ORGANS\INQUISITION\SCRIPTS\full_audit.py --repo-root E:\IMPERIUM

# Self inventory
py -3 IMPERIUM_TEST_VERSION\ORGANS\ADMINISTRATUM\SCRIPTS\self_inventory.py --repo-root E:\IMPERIUM

# Self diagnosis
py -3 IMPERIUM_TEST_VERSION\ORGANS\ADMINISTRATUM\SCRIPTS\self_diagnosis.py --repo-root E:\IMPERIUM

# Collect KPIs
py -3 IMPERIUM_TEST_VERSION\MONITORING\kpi_collector.py --repo-root E:\IMPERIUM
```

## Что работает

✅ Smoke test script
✅ Script scanner
✅ Script health check
✅ Fake green detector
✅ Stale truth detector
✅ Full audit
✅ Self inventory
✅ Self diagnosis
✅ KPI collector
✅ Error precheck
✅ Command gateway prototype

## Что НЕ работает / только scaffold

⚠️ Qt dashboards (требуют PyQt6 разработки)
⚠️ Real button spine (требует интеграции с Sanctum)
⚠️ Screenshot capture (требует pyautogui/pillow)
⚠️ Promotion workflow (только schema)

## Риски

1. **Raw subprocess** — Sanctum использует raw subprocess
2. **Warning flood** — 117838 warnings от continuity packs
3. **Registry drift** — регистры не синхронизированы с реальностью
4. **Organs scaffold** — все органы только scaffold, не operational
