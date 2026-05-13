# TASK 08: Backend Truth Dashboard Data v0.1

## Метаданные
- task_id: `TASK-20260514-SAN-CLEANING-DASHBOARD-DATA-V0_1`
- priority: P2 — СРЕДНИЙ
- platform: VM2 разработка, PC приёмка
- estimated_files: 1 скрипт + 1 data model
- dependencies: TASK_07 (Warning Budget)

## Цель
Создать data model для backend truth dashboard.

## Проблема
Нет единой точки правды для отображения состояния системы.
Dashboard должен показывать:
- Статус реестров
- Warning budget
- Покрытие регистрации
- Последние проверки

## Входные данные
- `REGISTRY/SCRIPT_REGISTRY.json`
- `REGISTRY/ARSENAL_REGISTRY.json`
- `REGISTRY/LAUNCHER_REGISTRY.json`
- `REGISTRY/ORGAN_REGISTRY.json`
- `CONFIG/warning_budget_v0_1.json`
- `.imperium_runtime/` — последние receipts

## Выходные данные
- `CURRENT_STATE/DASHBOARD_DATA.json`
- `CURRENT_STATE/DASHBOARD_DATA.md` (человекочитаемый)

## Структура DASHBOARD_DATA.json

```json
{
  "schema_version": "dashboard_data_v0_1",
  "generated_at_utc": "2026-05-14T12:00:00Z",
  "git_head": "9307c4883926edd3f843fd1224fdee244b47b1a0",
  "commit_count": 80,
  
  "overall_status": "PASS_WITH_WARNINGS",
  
  "registries": {
    "scriptorium": {
      "total": 45,
      "registered": 42,
      "coverage_percent": 93.3,
      "status": "HEALTHY"
    },
    "arsenal": {
      "total": 10,
      "available": 9,
      "blocked": 1,
      "coverage_percent": 90.0,
      "status": "HEALTHY"
    },
    "launchers": {
      "total": 5,
      "active": 5,
      "status": "HEALTHY"
    },
    "organs": {
      "total": 10,
      "active": 6,
      "missing": 4,
      "status": "INCOMPLETE"
    }
  },
  
  "warning_budget": {
    "legacy_allowed": 45,
    "legacy_current": 45,
    "new_allowed": 0,
    "new_current": 0,
    "verdict": "WITHIN_BUDGET",
    "status": "HEALTHY"
  },
  
  "quality_gates": {
    "all_scripts_compile": {
      "passed": true,
      "details": "45/45 scripts compile"
    },
    "no_stale_paths": {
      "passed": true,
      "details": "0 stale paths found"
    },
    "registry_coverage": {
      "passed": true,
      "details": "93.3% script coverage"
    }
  },
  
  "recent_checks": [
    {
      "check_id": "verify_repo",
      "timestamp_utc": "2026-05-14T11:55:00Z",
      "verdict": "PASS_WITH_WARNINGS",
      "duration_seconds": 12.5
    }
  ],
  
  "action_items": [
    {
      "priority": "P1",
      "description": "Register 3 remaining unregistered scripts",
      "task_ref": "TASK_04_SCRIPTORIUM"
    },
    {
      "priority": "P2",
      "description": "Create missing organs: Custodes, Strategium, Schola, Throne",
      "task_ref": null
    }
  ]
}
```

## Алгоритм

### Шаг 1: Сбор данных из реестров
```python
def collect_registry_stats() -> Dict:
    """Собрать статистику из всех реестров."""
    stats = {}
    
    # SCRIPTORIUM
    scripts = load_json('REGISTRY/SCRIPT_REGISTRY.json')
    stats['scriptorium'] = {
        'total': len(scripts.get('scripts', [])),
        'registered': len([s for s in scripts.get('scripts', []) if s.get('status') == 'active']),
    }
    stats['scriptorium']['coverage_percent'] = (
        stats['scriptorium']['registered'] / stats['scriptorium']['total'] * 100
        if stats['scriptorium']['total'] > 0 else 0
    )
    
    # ... аналогично для других реестров
    
    return stats
```

### Шаг 2: Сбор warning budget
```python
def collect_warning_budget() -> Dict:
    """Собрать данные warning budget."""
    budget = load_json('CONFIG/warning_budget_v0_1.json')
    return {
        'legacy_allowed': budget['budget']['legacy_allowed'],
        'legacy_current': budget['budget']['legacy_current'],
        'new_allowed': budget['budget']['new_allowed'],
        'new_current': budget['budget']['new_current'],
        'verdict': budget['verdict'],
        'status': 'HEALTHY' if budget['verdict'] == 'WITHIN_BUDGET' else 'UNHEALTHY'
    }
```

### Шаг 3: Сбор recent checks
```python
def collect_recent_checks() -> List[Dict]:
    """Собрать последние проверки из .imperium_runtime/."""
    checks = []
    runtime_dir = Path('.imperium_runtime')
    
    for receipt_file in runtime_dir.glob('**/*_RECEIPT.json'):
        receipt = load_json(receipt_file)
        checks.append({
            'check_id': receipt.get('launcher_id', 'unknown'),
            'timestamp_utc': receipt.get('completed_at_utc'),
            'verdict': receipt.get('verdict'),
        })
    
    # Сортировать по времени, взять последние 10
    checks.sort(key=lambda x: x['timestamp_utc'], reverse=True)
    return checks[:10]
```

### Шаг 4: Определение overall_status
```python
def determine_overall_status(data: Dict) -> str:
    """Определить общий статус."""
    if data['warning_budget']['status'] == 'UNHEALTHY':
        return 'FAIL'
    
    if any(r['status'] == 'UNHEALTHY' for r in data['registries'].values()):
        return 'PASS_WITH_WARNINGS'
    
    if data['registries']['organs']['status'] == 'INCOMPLETE':
        return 'PASS_WITH_WARNINGS'
    
    return 'PASS'
```

### Шаг 5: Генерация action items
```python
def generate_action_items(data: Dict) -> List[Dict]:
    """Сгенерировать список действий."""
    items = []
    
    # Незарегистрированные скрипты
    unregistered = data['registries']['scriptorium']['total'] - data['registries']['scriptorium']['registered']
    if unregistered > 0:
        items.append({
            'priority': 'P1',
            'description': f'Register {unregistered} remaining unregistered scripts',
            'task_ref': 'TASK_04_SCRIPTORIUM'
        })
    
    # Недостающие органы
    missing_organs = data['registries']['organs']['missing']
    if missing_organs > 0:
        items.append({
            'priority': 'P2',
            'description': f'Create {missing_organs} missing organs',
            'task_ref': None
        })
    
    return items
```

## Файлы для создания

### 1. Dashboard Data Generator
**Путь:** `TOOLS/dashboard_data_generator_v0_1.py`

```python
#!/usr/bin/env python3
"""
Dashboard Data Generator v0.1

Генерация данных для backend truth dashboard.

Usage:
    python3 dashboard_data_generator_v0_1.py [--dry-run] [--verbose]
"""
```

### 2. Dashboard Data
**Путь:** `CURRENT_STATE/DASHBOARD_DATA.json`

### 3. Dashboard Report
**Путь:** `CURRENT_STATE/DASHBOARD_DATA.md`

## Проверки

### Обязательные проверки
```bash
# 1. Компиляция
python3 -m py_compile TOOLS/dashboard_data_generator_v0_1.py

# 2. Dry-run
python3 TOOLS/dashboard_data_generator_v0_1.py --dry-run --verbose

# 3. Generate
python3 TOOLS/dashboard_data_generator_v0_1.py --verbose

# 4. Валидация JSON
python3 -c "import json; json.load(open('CURRENT_STATE/DASHBOARD_DATA.json'))"
```

## Критерии успеха
- [ ] Генератор создан и компилируется
- [ ] JSON output валиден
- [ ] Markdown отчёт читаем
- [ ] Все реестры включены
- [ ] Warning budget включён
- [ ] Action items сгенерированы
- [ ] Receipt создан

## Критерии блокировки
- Генератор не компилируется
- JSON невалиден
- Отсутствуют входные реестры

## Ожидаемый Servitor prompt outline

```
TASK: TASK-20260514-SAN-CLEANING-DASHBOARD-DATA-V0_1
GOAL: Generate backend truth dashboard data

STEPS:
1. Read KIRO_PLAN_ADVISOR/SAN_CLEAN_PLAN/TASKS/TASK_08_DASHBOARD_DATA/
2. Verify all input registries exist
3. Create TOOLS/dashboard_data_generator_v0_1.py
4. Run py_compile
5. Run --dry-run --verbose
6. Run --verbose (generate)
7. Validate CURRENT_STATE/DASHBOARD_DATA.json
8. Review CURRENT_STATE/DASHBOARD_DATA.md
9. Build bundle for PC review

CONSTRAINTS:
- Do NOT commit from VM2
- All registries must be included
- JSON must be valid
```
