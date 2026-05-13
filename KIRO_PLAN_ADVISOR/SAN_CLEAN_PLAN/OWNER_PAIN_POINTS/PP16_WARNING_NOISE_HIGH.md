# PP16: Warning Noise is High

## Проблема
Warnings от dirt, old paths, partial registration, stale reports и real blockers смешаны.
Невозможно отличить критический warning от legacy шума.

## Требование Owner
Warning budget должен классифицировать:
- Severity (серьёзность)
- Source (источник)
- TTL (время жизни)
- Owner decision requirement (требуется ли решение Owner)
- Escalation rule (правило эскалации)

## Решение

### Архитектурный паттерн: Technical Debt Classification
Источник: [Technical Debt Prioritisation Framework](https://941consulting.com/en/resources/articles/technical-debt-prioritisation-framework/)

> "Every engineering team has technical debt. The ones that succeed aren't debt-free—they're skilled at managing debt strategically."

Источник: [Managing Technical Debt: How to Quantify and Prioritise](https://www.em-tools.io/managing-teams/managing-technical-debt)

> "Use a simple prioritisation matrix: high-severity, high-impact debt is urgent; high-severity, low-impact debt is important but can be scheduled; low-severity debt in any impact category can typically wait."

### Warning Classification Schema

```json
{
  "schema_version": "warning_budget_v0_1",
  "created": "2026-05-14",
  "updated": "2026-05-14",
  
  "budget": {
    "legacy_allowed": 50,
    "new_allowed": 0,
    "transient_allowed": 10,
    "total_current": 55,
    "legacy_current": 50,
    "new_current": 0,
    "transient_current": 5
  },
  
  "classifications": [
    {
      "warning_id": "WARN-LEGACY-CONTINUITY-001",
      "source": "ORGANS/ADMINISTRATUM/CONTINUITY/PACKS/",
      "message_pattern": ".*continuity pack.*",
      "classification": "legacy",
      "severity": "low",
      "reason": "Historical continuity data, not active code",
      "ttl_days": null,
      "owner_decision_required": false,
      "escalation_rule": "none",
      "fix_task": null
    },
    {
      "warning_id": "WARN-PATH-STALE-001",
      "source": "scripts/*.py",
      "message_pattern": ".*IMPERIUM_LOCAL.*",
      "classification": "new",
      "severity": "high",
      "reason": "Stale path after migration",
      "ttl_days": 7,
      "owner_decision_required": false,
      "escalation_rule": "auto_task",
      "fix_task": "TASK-20260514-SAN-CLEANING-ADDRESS-REWRITE-V0_1"
    }
  ],
  
  "severity_definitions": {
    "critical": {
      "description": "Блокирует работу, требует немедленного исправления",
      "max_ttl_days": 1,
      "owner_decision_required": true,
      "escalation": "immediate"
    },
    "high": {
      "description": "Влияет на качество, требует исправления в текущей арке",
      "max_ttl_days": 7,
      "owner_decision_required": false,
      "escalation": "auto_task"
    },
    "medium": {
      "description": "Технический долг, можно запланировать",
      "max_ttl_days": 30,
      "owner_decision_required": false,
      "escalation": "backlog"
    },
    "low": {
      "description": "Косметический или legacy, можно игнорировать",
      "max_ttl_days": null,
      "owner_decision_required": false,
      "escalation": "none"
    }
  },
  
  "classification_rules": {
    "legacy": {
      "description": "Исторический код/данные, не активная разработка",
      "patterns": [
        "CONTINUITY/PACKS/",
        "CURRENT_STATE/",
        "ARTIFACTS/",
        "PC_ENGINEERING_ROOM/",
        "sanctum_v0_[0-2][0-9]"
      ],
      "default_severity": "low",
      "counts_against_budget": true
    },
    "new": {
      "description": "Новый код, требует исправления",
      "patterns": [],
      "default_severity": "high",
      "counts_against_budget": true
    },
    "transient": {
      "description": "Временное состояние, исчезнет после операции",
      "patterns": [
        ".imperium_runtime/",
        "INBOX/",
        "OUTBOX/"
      ],
      "default_severity": "low",
      "counts_against_budget": false
    },
    "ignored": {
      "description": "Явно игнорируемые warnings",
      "patterns": [],
      "default_severity": "none",
      "counts_against_budget": false
    }
  },
  
  "verdict": "WITHIN_BUDGET"
}
```

### Алгоритм классификации

```python
def classify_warning(warning: Dict, rules: Dict) -> Dict:
    """Классифицировать warning."""
    source = warning.get("source", "")
    message = warning.get("message", "")
    
    # 1. Проверить явные паттерны
    for classification, rule in rules["classification_rules"].items():
        for pattern in rule["patterns"]:
            if re.search(pattern, source) or re.search(pattern, message):
                return {
                    "classification": classification,
                    "severity": rule["default_severity"],
                    "matched_pattern": pattern,
                    "counts_against_budget": rule["counts_against_budget"]
                }
    
    # 2. По умолчанию — new
    return {
        "classification": "new",
        "severity": "high",
        "matched_pattern": None,
        "counts_against_budget": True
    }


def check_warning_budget(warnings: List[Dict], budget: Dict) -> Dict:
    """Проверить warning budget."""
    classified = [classify_warning(w, budget) for w in warnings]
    
    counts = {
        "legacy": len([c for c in classified if c["classification"] == "legacy"]),
        "new": len([c for c in classified if c["classification"] == "new"]),
        "transient": len([c for c in classified if c["classification"] == "transient"]),
        "ignored": len([c for c in classified if c["classification"] == "ignored"])
    }
    
    # Проверить бюджет
    over_budget = []
    
    if counts["legacy"] > budget["budget"]["legacy_allowed"]:
        over_budget.append({
            "type": "legacy",
            "current": counts["legacy"],
            "allowed": budget["budget"]["legacy_allowed"]
        })
    
    if counts["new"] > budget["budget"]["new_allowed"]:
        over_budget.append({
            "type": "new",
            "current": counts["new"],
            "allowed": budget["budget"]["new_allowed"]
        })
    
    verdict = "WITHIN_BUDGET" if not over_budget else "OVER_BUDGET"
    
    return {
        "verdict": verdict,
        "counts": counts,
        "over_budget": over_budget,
        "classified_warnings": classified
    }
```

### Интеграция с verify_repo.py

```python
# В verify_repo.py добавить:

def run_with_warning_budget():
    """Запустить проверку с учётом warning budget."""
    
    # 1. Собрать все warnings
    warnings = collect_all_warnings()
    
    # 2. Загрузить budget
    budget = load_json("CONFIG/warning_budget_v0_1.json")
    
    # 3. Проверить budget
    result = check_warning_budget(warnings, budget)
    
    # 4. Вернуть verdict
    if result["verdict"] == "OVER_BUDGET":
        # Показать только new warnings (не legacy)
        new_warnings = [w for w in result["classified_warnings"] 
                       if w["classification"] == "new"]
        print(f"OVER_BUDGET: {len(new_warnings)} new warnings")
        for w in new_warnings:
            print(f"  - {w['source']}: {w['message']}")
        return "FAIL"
    
    return "PASS_WITH_WARNINGS" if warnings else "PASS"
```

### Отчёт по warnings

```markdown
# Warning Budget Report

## Summary
- **Verdict**: WITHIN_BUDGET
- **Total warnings**: 55
- **Legacy**: 50 / 50 allowed
- **New**: 0 / 0 allowed
- **Transient**: 5 / 10 allowed

## By Source

| Source | Legacy | New | Transient |
|--------|--------|-----|-----------|
| CONTINUITY/PACKS/ | 30 | 0 | 0 |
| CURRENT_STATE/ | 15 | 0 | 0 |
| ARTIFACTS/ | 5 | 0 | 0 |
| .imperium_runtime/ | 0 | 0 | 5 |

## Action Items
- None (within budget)
```

## Файлы для создания

| Файл | Назначение | TASK |
|------|------------|------|
| `CONFIG/warning_budget_v0_1.json` | Конфигурация бюджета | TASK_07 |
| `schemas/warning_budget_v0_1.schema.json` | Схема | TASK_07 |
| `TOOLS/warning_budget_classifier_v0_1.py` | Классификатор | TASK_07 |
| `TOOLS/warning_budget_report_v0_1.py` | Генератор отчёта | TASK_07 |

## Проверка

```bash
# 1. Классифицировать все warnings
python3 TOOLS/warning_budget_classifier_v0_1.py --scan --verbose

# 2. Проверить бюджет
python3 TOOLS/warning_budget_classifier_v0_1.py --check --verbose

# 3. Сгенерировать отчёт
python3 TOOLS/warning_budget_report_v0_1.py --output CURRENT_STATE/WARNING_BUDGET_REPORT.md
```

## Связь с задачами
- **TASK_07** (Warning Budget Classification) — полная реализация

## Критерии успеха
- [ ] Все warnings классифицированы
- [ ] new_current = 0
- [ ] legacy_current ≤ legacy_allowed
- [ ] Отчёт генерируется
- [ ] verify_repo.py использует budget
