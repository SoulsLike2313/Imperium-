# Q06: Warning / Blocker Budget

## ВОПРОС
Какие warning/blocker метрики должны быть введены сейчас?

## РЕШЕНИЕ

### Классы предупреждений

| Warning Class | Severity | Allowed Count | Escalation | Owner Decision |
|---------------|----------|---------------|------------|----------------|
| `REPO_PARITY_WARNING` | BLOCKER | 0 | Немедленно | Да |
| `STALE_ADDRESS_WARNING` | MEDIUM | 20 | 7 дней | Нет |
| `LOCAL_PRIVATE_CONTEXT_WARNING` | MEDIUM | 5 | 3 дня | Да |
| `SCRIPT_REGISTRY_WARNING` | MEDIUM | 10 | При <70% | Нет |
| `TOOL_REGISTRY_WARNING` | LOW | 20 | Нет | Нет |
| `ROUTE_WARNING` | BLOCKER | 0 | Немедленно | Да |
| `DASHBOARD_TRUTH_WARNING` | LOW | 10 | Нет | Нет |
| `FAKE_GREEN_RISK` | BLOCKER | 0 | Немедленно | Да |
| `PRIVATE_PAYLOAD_LEAK_RISK` | BLOCKER | 0 | Немедленно | Да |
| `GENERATED_CACHE_POLLUTION` | LOW | 50 | Нет | Нет |
| `LEGACY_WARNING` | LOW | 10000 | Нет | Нет |

### Путь решения — Шаги

#### Шаг 1: Создать схему warning budget
Файл: `schemas/warning_budget_v0_1.schema.json`

#### Шаг 2: Создать скрипт классификации
Файл: `TOOLS/classify_warnings_v0_1.py`

```python
def classify_warning(warning: str) -> str:
    """Классифицировать warning."""
    
    # Repo parity
    if "parity" in warning.lower() or "head mismatch" in warning.lower():
        return "REPO_PARITY_WARNING"
    
    # Stale address
    if "E:\\IMPERIUM_LOCAL" in warning or "E:\\IMPERIUM_PRIVATE" in warning:
        return "STALE_ADDRESS_WARNING"
    
    # Script registry
    if "unregistered script" in warning.lower():
        return "SCRIPT_REGISTRY_WARNING"
    
    # Legacy (continuity packs, old artifacts)
    if "CONTINUITY" in warning or "ARTIFACTS" in warning:
        return "LEGACY_WARNING"
    
    return "UNKNOWN_WARNING"
```

#### Шаг 3: Собрать текущие warnings
```python
def collect_warnings(repo_root: Path) -> dict:
    """Собрать все warnings из verify_repo.py."""
    result = subprocess.run(
        ["python3", "scripts/verify_repo.py"],
        capture_output=True,
        text=True,
        cwd=repo_root
    )
    
    # Парсить output
    warnings = parse_warnings(result.stdout)
    
    # Классифицировать
    classified = {}
    for w in warnings:
        cls = classify_warning(w)
        if cls not in classified:
            classified[cls] = []
        classified[cls].append(w)
    
    return classified
```

#### Шаг 4: Создать warning budget registry
Файл: `REGISTRY/WARNING_BUDGET_V0_1.json`

#### Шаг 5: Создать отчёт классификации
Файл: `CURRENT_STATE/WARNING_CLASSIFICATION_20260514.json`

#### Шаг 6: Обновить чекер
Файл: `TOOLS/check_warning_budget_v0_1.py` (уже существует, обновить)

### Алгоритм определения verdict

```python
def calculate_verdict(budget: dict, current: dict) -> str:
    """Определить verdict на основе budget."""
    
    blockers = []
    over_budget = []
    
    for cls, config in budget.items():
        count = current.get(cls, 0)
        allowed = config["allowed_count"]
        severity = config["severity"]
        
        if severity == "BLOCKER" and count > 0:
            blockers.append(cls)
        elif count > allowed:
            over_budget.append(cls)
    
    if blockers:
        return "BLOCKED"
    elif over_budget:
        return "PASS_WITH_WARNINGS"
    else:
        return "PASS"
```

### Критерии успеха
- [ ] Все warning classes определены
- [ ] Budget thresholds установлены
- [ ] Классификация работает
- [ ] Legacy warnings отделены от new
- [ ] Чекер обновлён

### Критерии блокировки
- Классификация не работает
- Budget не определён

## ПРИМЕР СТРУКТУРЫ

См. `SCHEMAS/warning_budget_v0_1.schema.json` и `EXAMPLES/warning_budget_example.json`
