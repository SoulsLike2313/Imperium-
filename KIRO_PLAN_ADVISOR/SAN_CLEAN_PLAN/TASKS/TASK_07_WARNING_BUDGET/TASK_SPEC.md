# TASK 07: Warning Budget Classification v0.1

## Метаданные
- task_id: `TASK-20260514-SAN-CLEANING-WARNING-BUDGET-V0_1`
- priority: P2 — СРЕДНИЙ
- platform: VM2 или PC
- estimated_files: 1 скрипт + 1 конфиг
- dependencies: TASK_06 (MECHANICUS)

## Цель
Классифицировать все warnings как legacy vs new и установить бюджет.

## Проблема
Текущий `PASS_WITH_WARNINGS` вердикт не различает:
- Legacy warnings от continuity packs (допустимы)
- Новые warnings от свежего кода (недопустимы)

Это создаёт "warning flood" и маскирует реальные проблемы.

## Входные данные
- Вывод `python3 scripts/verify_repo.py`
- Вывод `./TOOLS/run_administratum_git_cli_check.sh`
- `KIRO_PLAN_ADVISOR/SAN_CLEAN_PLAN/SCHEMAS/warning_budget_v0_1.schema.json`

## Выходные данные
- `CONFIG/warning_budget_v0_1.json`
- `CURRENT_STATE/WARNING_CLASSIFICATION_REPORT.md`

## Алгоритм

### Шаг 1: Сбор warnings
```python
# Запустить verify_repo.py и собрать warnings
result = subprocess.run(
    ['python3', 'scripts/verify_repo.py'],
    capture_output=True,
    text=True
)

# Парсить вывод
warnings = parse_warnings(result.stdout + result.stderr)
```

### Шаг 2: Классификация
```python
LEGACY_PATTERNS = [
    r'ORGANS/.*/CONTINUITY/PACKS/',
    r'CURRENT_STATE/',
    r'ARTIFACTS/',
    r'PC_ENGINEERING_ROOM/',
    r'sanctum_v0_\d+',  # старые версии Sanctum
]

def classify_warning(warning: Dict) -> str:
    """Классифицировать warning."""
    source = warning.get('source', '')
    
    for pattern in LEGACY_PATTERNS:
        if re.search(pattern, source):
            return 'legacy'
    
    # Проверить дату файла
    if is_old_file(source):
        return 'legacy'
    
    return 'new'
```

### Шаг 3: Установка бюджета
```python
budget = {
    'legacy_allowed': len([w for w in warnings if w['classification'] == 'legacy']),
    'new_allowed': 0,  # Новые warnings недопустимы
    'total_current': len(warnings),
    'legacy_current': len([w for w in warnings if w['classification'] == 'legacy']),
    'new_current': len([w for w in warnings if w['classification'] == 'new']),
}
```

### Шаг 4: Генерация конфига
```json
{
  "schema_version": "warning_budget_v0_1",
  "created": "2026-05-14",
  "updated": "2026-05-14",
  
  "budget": {
    "legacy_allowed": 45,
    "new_allowed": 0,
    "total_current": 45,
    "legacy_current": 45,
    "new_current": 0
  },
  
  "classifications": [
    {
      "warning_id": "WARN-CONTINUITY-PACK-001",
      "source": "ORGANS/ADMINISTRATUM/CONTINUITY/PACKS/",
      "message_pattern": ".*continuity pack.*",
      "classification": "legacy",
      "reason": "Historical continuity data, not active code"
    }
  ],
  
  "sources": {
    "ORGANS/ADMINISTRATUM/CONTINUITY/PACKS/": {
      "legacy_count": 30,
      "new_count": 0,
      "notes": "Continuity packs — historical data"
    },
    "CURRENT_STATE/": {
      "legacy_count": 10,
      "new_count": 0,
      "notes": "State snapshots — not active code"
    }
  },
  
  "verdict": "WITHIN_BUDGET"
}
```

## Файлы для создания

### 1. Warning Budget Script
**Путь:** `TOOLS/warning_budget_classifier_v0_1.py`

```python
#!/usr/bin/env python3
"""
Warning Budget Classifier v0.1

Классификация warnings и управление бюджетом.

Usage:
    python3 warning_budget_classifier_v0_1.py --scan [--verbose]
    python3 warning_budget_classifier_v0_1.py --apply [--verbose]
    python3 warning_budget_classifier_v0_1.py --check [--verbose]
"""
```

### 2. Warning Budget Config
**Путь:** `CONFIG/warning_budget_v0_1.json`

## Интеграция с verify_repo.py

После создания бюджета, `verify_repo.py` должен:
1. Загрузить `CONFIG/warning_budget_v0_1.json`
2. Классифицировать каждый warning
3. Проверить что new_current ≤ new_allowed
4. Вернуть `PASS` если в бюджете, `FAIL` если превышен

```python
def check_warning_budget() -> str:
    """Проверить warning budget."""
    budget = load_json('CONFIG/warning_budget_v0_1.json')
    
    if budget['budget']['new_current'] > budget['budget']['new_allowed']:
        return 'OVER_BUDGET'
    
    return 'WITHIN_BUDGET'
```

## Проверки

### Обязательные проверки
```bash
# 1. Компиляция
python3 -m py_compile TOOLS/warning_budget_classifier_v0_1.py

# 2. Scan
python3 TOOLS/warning_budget_classifier_v0_1.py --scan --verbose

# 3. Apply
python3 TOOLS/warning_budget_classifier_v0_1.py --apply --verbose

# 4. Check
python3 TOOLS/warning_budget_classifier_v0_1.py --check --verbose

# 5. Валидация конфига
python3 -c "import json; json.load(open('CONFIG/warning_budget_v0_1.json'))"
```

## Критерии успеха
- [ ] Скрипт создан и компилируется
- [ ] Все warnings классифицированы
- [ ] Бюджет установлен
- [ ] new_current = 0 (или обоснованно > 0)
- [ ] Конфиг валиден
- [ ] Receipt создан

## Критерии блокировки
- Скрипт не компилируется
- Конфиг невалидный JSON
- new_current > 0 без обоснования

## Ожидаемый Servitor prompt outline

```
TASK: TASK-20260514-SAN-CLEANING-WARNING-BUDGET-V0_1
GOAL: Classify warnings and establish budget

STEPS:
1. Read KIRO_PLAN_ADVISOR/SAN_CLEAN_PLAN/TASKS/TASK_07_WARNING_BUDGET/
2. Run python3 scripts/verify_repo.py and capture output
3. Create TOOLS/warning_budget_classifier_v0_1.py
4. Run py_compile
5. Run --scan --verbose
6. Review classifications
7. Run --apply --verbose
8. Run --check --verbose
9. Validate CONFIG/warning_budget_v0_1.json
10. Build bundle for PC review

CONSTRAINTS:
- Do NOT commit from VM2
- new_allowed must be 0 unless justified
- All warnings must be classified
```
