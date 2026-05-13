# Q07: Backend Truth Dashboard Data Model

## ВОПРОС
Что должна показывать backend truth dashboard data model до добавления интерактивных кнопок?

## РЕШЕНИЕ

### Принцип
**Сначала данные, потом красота.** Dashboard должен показывать правду, а не красивую ложь.

### Компоненты data model

| View | Файл | Описание |
|------|------|----------|
| Main Index | `BACKEND_TRUTH_INDEX_V0_1.json` | Главный индекс |
| Script Registry | `SCRIPTORIUM_VIEW_V0_1.json` | Данные SCRIPTORIUM |
| Arsenal Registry | `ARSENAL_VIEW_V0_1.json` | Данные ARSENAL |
| Route Health | `ROUTE_HEALTH_VIEW_V0_1.json` | Здоровье маршрутов |
| Repo Parity | `REPO_PARITY_VIEW_V0_1.json` | Паритет репо |
| External Context | `EXTERNAL_CONTEXT_VIEW_V0_1.json` | Внешний контекст |
| Warning Budget | `WARNING_BUDGET_VIEW_V0_1.json` | Бюджет warnings |
| Recent Receipts | `RECENT_RECEIPTS_VIEW_V0_1.json` | Последние receipts |
| Blocked Tasks | `BLOCKED_TASKS_VIEW_V0_1.json` | Заблокированные задачи |

### Путь решения — Шаги

#### Шаг 1: Создать структуру папок
```
DASHBOARD/
└── DATA/
    ├── BACKEND_TRUTH_INDEX_V0_1.json
    ├── SCRIPTORIUM_VIEW_V0_1.json
    ├── ARSENAL_VIEW_V0_1.json
    ├── ROUTE_HEALTH_VIEW_V0_1.json
    ├── REPO_PARITY_VIEW_V0_1.json
    ├── EXTERNAL_CONTEXT_VIEW_V0_1.json
    ├── WARNING_BUDGET_VIEW_V0_1.json
    ├── RECENT_RECEIPTS_VIEW_V0_1.json
    └── BLOCKED_TASKS_VIEW_V0_1.json
```

#### Шаг 2: Создать схему главного индекса
Файл: `schemas/backend_truth_dashboard_v0_1.schema.json`

```json
{
  "schema_version": "backend_truth_dashboard_v0_1",
  "generated_at_utc": "2026-05-14T12:00:00Z",
  "repo_head": "9307c48...",
  "views": {
    "scriptorium": {"path": "SCRIPTORIUM_VIEW_V0_1.json", "fresh": true},
    "arsenal": {"path": "ARSENAL_VIEW_V0_1.json", "fresh": true},
    "route_health": {"path": "ROUTE_HEALTH_VIEW_V0_1.json", "fresh": true},
    ...
  },
  "summary": {
    "script_coverage": 90,
    "tool_coverage": 80,
    "warning_count": 100,
    "blocker_count": 0,
    "overall_verdict": "PASS_WITH_WARNINGS"
  }
}
```

#### Шаг 3: Создать билдер данных
Файл: `TOOLS/build_backend_truth_dashboard_data_v0_1.py`

```python
def build_dashboard_data(repo_root: Path) -> dict:
    """Собрать все данные для dashboard."""
    
    # Собрать SCRIPTORIUM view
    scriptorium = build_scriptorium_view(repo_root)
    
    # Собрать ARSENAL view
    arsenal = build_arsenal_view(repo_root)
    
    # Собрать Route Health view
    route_health = build_route_health_view(repo_root)
    
    # Собрать Warning Budget view
    warning_budget = build_warning_budget_view(repo_root)
    
    # Собрать Recent Receipts view
    receipts = build_recent_receipts_view(repo_root)
    
    # Создать главный индекс
    index = {
        "schema_version": "backend_truth_dashboard_v0_1",
        "generated_at_utc": datetime.utcnow().isoformat(),
        "repo_head": get_git_head(repo_root),
        "views": {...},
        "summary": {...}
    }
    
    return index
```

#### Шаг 4: Создать чекер данных
Файл: `TOOLS/check_backend_truth_dashboard_v0_1.py`

```python
def check_dashboard_data(repo_root: Path) -> dict:
    """Проверить данные dashboard."""
    
    data_dir = repo_root / "DASHBOARD" / "DATA"
    
    checks = []
    
    # Проверить наличие файлов
    required_files = [
        "BACKEND_TRUTH_INDEX_V0_1.json",
        "SCRIPTORIUM_VIEW_V0_1.json",
        "ARSENAL_VIEW_V0_1.json",
        ...
    ]
    
    for f in required_files:
        path = data_dir / f
        if path.exists():
            checks.append({"file": f, "exists": True})
        else:
            checks.append({"file": f, "exists": False})
    
    # Проверить свежесть данных
    # ...
    
    return {"checks": checks, "verdict": "PASS" if all_pass else "FAIL"}
```

#### Шаг 5: Сгенерировать данные

```bash
python3 TOOLS/build_backend_truth_dashboard_data_v0_1.py --repo-root . --out DASHBOARD/DATA/
```

### Структура SCRIPTORIUM_VIEW

```json
{
  "schema_version": "scriptorium_view_v0_1",
  "generated_at_utc": "...",
  "summary": {
    "total_scripts": 98,
    "registered": 90,
    "unregistered": 8,
    "coverage_percent": 91.8
  },
  "by_status": {
    "REGISTERED": 50,
    "ACTIVE": 30,
    "CANDIDATE": 10,
    "DEPRECATED": 5,
    "BROKEN": 3
  },
  "by_organ": {
    "ADMINISTRATUM": 25,
    "ASTRONOMICON": 15,
    "MECHANICUS": 20,
    ...
  },
  "unregistered_list": [
    "TOOLS/some_script.py",
    ...
  ]
}
```

### Критерии успеха
- [ ] Все view файлы созданы
- [ ] Главный индекс создан
- [ ] Билдер работает
- [ ] Чекер проходит
- [ ] Данные соответствуют реальности

### Критерии блокировки
- Данные не генерируются
- Схема невалидна

## ПРИМЕР СТРУКТУРЫ

См. `SCHEMAS/backend_truth_dashboard_v0_1.schema.json` и `TASKS/TASK_08_DASHBOARD_DATA/`
