# PP36: Backend Truth Must Come Before UI Beauty

## Проблема
Визуальная работа без backend truth тратит время впустую.
UI может выглядеть красиво, но показывать ложь.

## Требование Owner
Перед основной UI polish должны существовать:
- Dashboard backend indexes
- Route health
- Warning budget
- Registry coverage
- Receipts

## Решение

### Архитектурный паттерн: Schema-Driven Development
Источник: [Schema Driven Development And Single Source of Truth](https://godspeed.systems/blog/schema-driven-development-and-single-source-of-truth)

> "Validation of data at exchange boundaries. Generation of Swagger, Graphql & other schemas and CRUD APIs from DB schema."

Источник: [JSON Schema validators for real-time dashboards](https://umatechnology.org/long-term-retention-planning-for-json-schema-validators-used-in-real-time-dashboards/)

> "JSON Schema ensures that the data flowing into dashboards complies with the expected format, making downstream processing more reliable."

### Принцип: Data → Schema → Backend → UI

```
┌─────────────────────────────────────────────────────────────────┐
│                    TRUTH-FIRST PIPELINE                          │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  1. RAW DATA        2. SCHEMA           3. BACKEND    4. UI     │
│  ───────────        ──────────          ──────────    ────      │
│  Registries    →    JSON Schema    →    Validators →  Display   │
│  Receipts      →    Contracts      →    Checkers   →  Widgets   │
│  Reports       →    Types          →    APIs       →  Charts    │
│                                                                  │
│  ═══════════════════════════════════════════════════════════════│
│  RULE: No UI element without backing data + schema + checker    │
└─────────────────────────────────────────────────────────────────┘
```

### Dashboard Data Model

```json
{
  "schema_version": "dashboard_data_v0_1",
  "generated_at_utc": "2026-05-14T12:00:00Z",
  "generator": "dashboard_data_generator_v0_1.py",
  "git_head": "9307c4883926edd3f843fd1224fdee244b47b1a0",
  
  "data_sources": {
    "scriptorium": {
      "source_file": "REGISTRY/SCRIPT_REGISTRY.json",
      "last_modified": "2026-05-14T11:00:00Z",
      "schema": "schemas/scriptorium_registry_v0_2.schema.json",
      "validated": true
    },
    "arsenal": {
      "source_file": "REGISTRY/ARSENAL_REGISTRY.json",
      "last_modified": "2026-05-14T11:00:00Z",
      "schema": "schemas/arsenal_registry_v0_1.schema.json",
      "validated": true
    },
    "warning_budget": {
      "source_file": "CONFIG/warning_budget_v0_1.json",
      "last_modified": "2026-05-14T10:00:00Z",
      "schema": "schemas/warning_budget_v0_1.schema.json",
      "validated": true
    }
  },
  
  "widgets": {
    "overall_status": {
      "widget_id": "WIDGET-OVERALL-STATUS",
      "type": "status_indicator",
      "data": {
        "status": "PASS_WITH_WARNINGS",
        "color": "yellow"
      },
      "backed_by": ["scriptorium", "arsenal", "warning_budget"],
      "checker": "scripts/verify_repo.py"
    },
    
    "scriptorium_coverage": {
      "widget_id": "WIDGET-SCRIPTORIUM-COVERAGE",
      "type": "progress_bar",
      "data": {
        "current": 45,
        "total": 50,
        "percent": 90.0,
        "threshold": 90.0,
        "status": "HEALTHY"
      },
      "backed_by": ["scriptorium"],
      "checker": "TOOLS/scriptorium_health_v0_1.py"
    },
    
    "warning_budget": {
      "widget_id": "WIDGET-WARNING-BUDGET",
      "type": "budget_meter",
      "data": {
        "legacy": {"current": 50, "allowed": 50, "status": "AT_LIMIT"},
        "new": {"current": 0, "allowed": 0, "status": "HEALTHY"},
        "verdict": "WITHIN_BUDGET"
      },
      "backed_by": ["warning_budget"],
      "checker": "TOOLS/warning_budget_classifier_v0_1.py"
    },
    
    "route_health": {
      "widget_id": "WIDGET-ROUTE-HEALTH",
      "type": "status_list",
      "data": {
        "routes": [
          {"name": "PC→VM2", "status": "OK", "last_test": "2026-05-14T11:00:00Z"},
          {"name": "VM2→PC", "status": "OK", "last_test": "2026-05-14T11:00:00Z"},
          {"name": "PC→GitHub", "status": "OK", "last_test": "2026-05-14T11:55:00Z"}
        ]
      },
      "backed_by": ["route_health"],
      "checker": "TOOLS/route_health_v0_1.py"
    }
  },
  
  "validation": {
    "all_sources_validated": true,
    "all_widgets_backed": true,
    "stale_data": [],
    "missing_checkers": []
  }
}
```

### Чеклист "Backend Truth Ready"

```python
def check_backend_truth_ready() -> Dict:
    """Проверить готовность backend truth для UI."""
    checks = []
    
    # 1. Все реестры существуют
    registries = [
        "REGISTRY/SCRIPT_REGISTRY.json",
        "REGISTRY/ARSENAL_REGISTRY.json",
        "REGISTRY/LAUNCHER_REGISTRY.json",
        "REGISTRY/ORGAN_REGISTRY.json"
    ]
    for reg in registries:
        checks.append({
            "check": f"registry_exists:{reg}",
            "passed": Path(reg).exists()
        })
    
    # 2. Все реестры валидны
    for reg in registries:
        if Path(reg).exists():
            try:
                json.load(open(reg))
                checks.append({"check": f"registry_valid:{reg}", "passed": True})
            except:
                checks.append({"check": f"registry_valid:{reg}", "passed": False})
    
    # 3. Warning budget существует
    checks.append({
        "check": "warning_budget_exists",
        "passed": Path("CONFIG/warning_budget_v0_1.json").exists()
    })
    
    # 4. Dashboard data generator существует
    checks.append({
        "check": "dashboard_generator_exists",
        "passed": Path("TOOLS/dashboard_data_generator_v0_1.py").exists()
    })
    
    # 5. Все checkers существуют
    checkers = [
        "scripts/verify_repo.py",
        "TOOLS/scriptorium_health_v0_1.py",
        "TOOLS/warning_budget_classifier_v0_1.py"
    ]
    for checker in checkers:
        checks.append({
            "check": f"checker_exists:{checker}",
            "passed": Path(checker).exists()
        })
    
    # Verdict
    all_passed = all(c["passed"] for c in checks)
    
    return {
        "backend_truth_ready": all_passed,
        "checks": checks,
        "passed_count": len([c for c in checks if c["passed"]]),
        "total_checks": len(checks),
        "recommendation": "Ready for UI work" if all_passed else "Complete backend first"
    }
```

### Запрещённые паттерны (Decorative Dashboard)

```python
# ❌ DECORATIVE: Hardcoded данные в UI
def bad_dashboard():
    return {
        "status": "PASS",  # Откуда это?
        "coverage": 95,    # Откуда это?
        "warnings": 0      # Откуда это?
    }

# ✅ TRUTHFUL: Данные из backend
def good_dashboard():
    # Загрузить из источников
    scriptorium = load_json("REGISTRY/SCRIPT_REGISTRY.json")
    warning_budget = load_json("CONFIG/warning_budget_v0_1.json")
    
    # Вычислить из данных
    coverage = scriptorium["coverage"]["coverage_percent"]
    warnings = warning_budget["budget"]["new_current"]
    
    # Проверить checker
    verify_result = run_checker("scripts/verify_repo.py")
    
    return {
        "status": verify_result["verdict"],
        "coverage": coverage,
        "warnings": warnings,
        "backed_by": ["SCRIPT_REGISTRY.json", "warning_budget_v0_1.json"],
        "verified_by": "verify_repo.py"
    }
```

### Порядок работы над Dashboard

```
1. BACKEND PHASE (обязательно первым)
   ├── Создать/обновить реестры
   ├── Создать schemas
   ├── Создать checkers
   ├── Создать dashboard_data_generator
   └── Проверить check_backend_truth_ready() == True

2. DATA PHASE
   ├── Запустить dashboard_data_generator
   ├── Валидировать output по schema
   └── Проверить все widgets backed

3. UI PHASE (только после 1 и 2)
   ├── Создать UI компоненты
   ├── Привязать к dashboard_data
   └── Добавить refresh механизм
```

## Файлы для создания

| Файл | Назначение | TASK |
|------|------------|------|
| `TOOLS/dashboard_data_generator_v0_1.py` | Генератор данных | TASK_08 |
| `schemas/dashboard_data_v0_1.schema.json` | Схема данных | TASK_08 |
| `TOOLS/check_backend_truth_ready_v0_1.py` | Проверка готовности | TASK_08 |
| `CURRENT_STATE/DASHBOARD_DATA.json` | Данные для dashboard | TASK_08 |

## Проверка

```bash
# 1. Проверить готовность backend
python3 TOOLS/check_backend_truth_ready_v0_1.py --verbose

# 2. Сгенерировать dashboard data
python3 TOOLS/dashboard_data_generator_v0_1.py --output CURRENT_STATE/DASHBOARD_DATA.json

# 3. Валидировать данные
python3 -c "
import json
from jsonschema import validate
data = json.load(open('CURRENT_STATE/DASHBOARD_DATA.json'))
schema = json.load(open('schemas/dashboard_data_v0_1.schema.json'))
validate(data, schema)
print('VALID')
"
```

## Связь с задачами
- **TASK_08** (Backend Truth Dashboard Data) — полная реализация

## Критерии успеха
- [ ] check_backend_truth_ready() == True
- [ ] Все widgets имеют backed_by
- [ ] Все widgets имеют checker
- [ ] Dashboard data валиден по schema
- [ ] Нет hardcoded данных в UI
