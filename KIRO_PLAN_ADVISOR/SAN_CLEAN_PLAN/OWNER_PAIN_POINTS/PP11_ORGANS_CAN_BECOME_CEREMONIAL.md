# PP11: Organs Can Become Ceremonial

## Проблема
Имена органов существуют до того, как существуют их контракты, self-reports, dashboards и границы авторитета.
Орган может быть "на бумаге" но не иметь реальной функциональности.

## Требование Owner
Каждый орган должен иметь:
- Contract (контракт)
- Status (статус)
- Self-report (самоотчёт)
- Dashboard data (данные для dashboard)
- Authority boundary (границы авторитета)
- Checkable outputs (проверяемые выходы)

## Решение

### Архитектурный паттерн: Capability-Oriented Service with Clear Boundaries
Источник: [Capability-Oriented Service Pattern](https://softwarepatternslexicon.com/microservices-boundaries-and-service-decomposition/decomposition-patterns/capability-oriented-pattern/)

> "A capability-oriented service owns a clear business function, the core rules that make that function meaningful, and the authoritative data needed to support it."

Источник: [What a Boundary Is in Software Architecture](https://softwarepatternslexicon.com/microservices-boundaries-and-service-decomposition/why-boundaries-matter/what-boundary-is/)

> "A boundary in software architecture is the line that separates responsibility, ownership, and decision-making authority."

### Структура ORGAN_CONTRACT.json

```json
{
  "schema_version": "organ_contract_v0_1",
  "organ_id": "MECHANICUS",
  "name": "Adeptus Mechanicus",
  "description": "Орган отвечающий за инструменты, скрипты и техническую инфраструктуру",
  "created": "2026-05-14",
  "updated": "2026-05-14",
  "status": "active",
  "maturity": "v0.1",
  
  "responsibilities": [
    {
      "id": "RESP-MECH-001",
      "description": "Управление SCRIPTORIUM (реестр скриптов)",
      "checkable": true,
      "checker": "TOOLS/check_scriptorium_v0_1.py"
    },
    {
      "id": "RESP-MECH-002",
      "description": "Управление ARSENAL (реестр инструментов)",
      "checkable": true,
      "checker": "TOOLS/check_arsenal_v0_1.py"
    }
  ],
  
  "boundaries": {
    "owns": [
      "TOOLS/*",
      "REGISTRY/SCRIPT_REGISTRY.json",
      "REGISTRY/ARSENAL_REGISTRY.json",
      "REGISTRY/LAUNCHER_REGISTRY.json"
    ],
    "does_not_own": [
      "SANCTUM/*",
      "scripts/verify_repo.py",
      "ORGANS/ADMINISTRATUM/*"
    ],
    "shared_with": {
      "ADMINISTRATUM": ["REGISTRY/ORGAN_REGISTRY.json"]
    }
  },
  
  "interfaces": {
    "provides": [
      {
        "interface_id": "IF-MECH-001",
        "name": "script_registration",
        "description": "Регистрация скриптов в SCRIPTORIUM",
        "entry_point": "TOOLS/scriptorium_register_v0_1.py",
        "input_schema": "schemas/scriptorium_entry_v0_1.schema.json",
        "output": "Updated REGISTRY/SCRIPT_REGISTRY.json"
      }
    ],
    "requires": [
      {
        "interface_id": "IF-EXT-001",
        "name": "git",
        "provider": "ARSENAL",
        "tool_id": "TOOL-GIT",
        "required_version": ">=2.30"
      }
    ]
  },
  
  "quality_gates": {
    "all_scripts_compile": {
      "id": "QG-MECH-001",
      "description": "Все скрипты должны проходить py_compile",
      "checker": "scripts/verify_repo.py",
      "threshold": "100%",
      "current_value": null,
      "last_check": null
    },
    "script_registration_coverage": {
      "id": "QG-MECH-002",
      "description": "Процент зарегистрированных скриптов",
      "threshold": ">=90%",
      "current_value": null,
      "last_check": null
    }
  },
  
  "self_report": {
    "generator": "TOOLS/mechanicus_self_report_v0_1.py",
    "output_path": "ORGANS/MECHANICUS/SELF_REPORT.json",
    "schedule": "on_demand",
    "last_generated": null
  },
  
  "dashboard_data": {
    "generator": "TOOLS/mechanicus_dashboard_data_v0_1.py",
    "output_path": "ORGANS/MECHANICUS/DASHBOARD_DATA.json",
    "fields": [
      "total_scripts",
      "registered_scripts",
      "registration_coverage",
      "total_tools",
      "available_tools",
      "quality_gate_status"
    ]
  }
}
```

### Чеклист "Орган не церемониальный"

```python
def check_organ_not_ceremonial(organ_id: str) -> Dict:
    """Проверить что орган не церемониальный."""
    checks = []
    
    # 1. Contract exists
    contract_path = Path(f"ORGANS/{organ_id}/ORGAN_CONTRACT.json")
    checks.append({
        "check": "contract_exists",
        "passed": contract_path.exists()
    })
    
    # 2. Contract is valid JSON
    if contract_path.exists():
        try:
            contract = json.load(open(contract_path))
            checks.append({"check": "contract_valid_json", "passed": True})
        except:
            checks.append({"check": "contract_valid_json", "passed": False})
            return {"organ_id": organ_id, "ceremonial": True, "checks": checks}
    
    # 3. Has responsibilities
    has_responsibilities = len(contract.get("responsibilities", [])) > 0
    checks.append({
        "check": "has_responsibilities",
        "passed": has_responsibilities
    })
    
    # 4. Has boundaries
    has_boundaries = "boundaries" in contract and "owns" in contract["boundaries"]
    checks.append({
        "check": "has_boundaries",
        "passed": has_boundaries
    })
    
    # 5. Has quality gates
    has_quality_gates = len(contract.get("quality_gates", {})) > 0
    checks.append({
        "check": "has_quality_gates",
        "passed": has_quality_gates
    })
    
    # 6. Quality gates have checkers
    all_gates_have_checkers = all(
        "checker" in gate 
        for gate in contract.get("quality_gates", {}).values()
    )
    checks.append({
        "check": "quality_gates_have_checkers",
        "passed": all_gates_have_checkers
    })
    
    # 7. Self-report generator exists
    self_report_gen = contract.get("self_report", {}).get("generator")
    if self_report_gen:
        gen_exists = Path(self_report_gen).exists()
    else:
        gen_exists = False
    checks.append({
        "check": "self_report_generator_exists",
        "passed": gen_exists
    })
    
    # 8. Dashboard data generator exists
    dashboard_gen = contract.get("dashboard_data", {}).get("generator")
    if dashboard_gen:
        dash_exists = Path(dashboard_gen).exists()
    else:
        dash_exists = False
    checks.append({
        "check": "dashboard_data_generator_exists",
        "passed": dash_exists
    })
    
    # Verdict
    all_passed = all(c["passed"] for c in checks)
    
    return {
        "organ_id": organ_id,
        "ceremonial": not all_passed,
        "checks": checks,
        "passed_count": len([c for c in checks if c["passed"]]),
        "total_checks": len(checks)
    }
```

### Минимальный набор для "не церемониального" органа

| Компонент | Обязательно | Файл |
|-----------|-------------|------|
| Contract | ✅ | `ORGANS/{ORGAN}/ORGAN_CONTRACT.json` |
| Manifest | ✅ | `ORGANS/{ORGAN}/{ORGAN}_MANIFEST.md` |
| Self-report generator | ✅ | `TOOLS/{organ}_self_report_v0_1.py` |
| Dashboard data generator | ✅ | `TOOLS/{organ}_dashboard_data_v0_1.py` |
| At least 1 quality gate | ✅ | В contract |
| At least 1 checker | ✅ | В TOOLS/ |
| Boundary definition | ✅ | В contract |

### Статусы органов

```python
ORGAN_STATUSES = {
    "active": "Орган функционирует, все проверки проходят",
    "degraded": "Орган функционирует, но некоторые проверки не проходят",
    "ceremonial": "Орган существует только на бумаге",
    "missing": "Орган не создан",
    "deprecated": "Орган устарел, будет удалён"
}
```

## Файлы для создания

| Файл | Назначение | TASK |
|------|------------|------|
| `schemas/organ_contract_v0_1.schema.json` | Схема контракта | TASK_06 |
| `TOOLS/check_organ_ceremonial_v0_1.py` | Проверка церемониальности | TASK_06 |
| `ORGANS/MECHANICUS/ORGAN_CONTRACT.json` | Контракт MECHANICUS | TASK_06 |
| `TOOLS/mechanicus_self_report_v0_1.py` | Self-report генератор | TASK_06 |

## Проверка

```bash
# 1. Проверить все органы на церемониальность
python3 TOOLS/check_organ_ceremonial_v0_1.py --all --verbose

# 2. Проверить конкретный орган
python3 TOOLS/check_organ_ceremonial_v0_1.py --organ MECHANICUS --verbose

# 3. Сгенерировать self-report
python3 TOOLS/mechanicus_self_report_v0_1.py --output ORGANS/MECHANICUS/SELF_REPORT.json
```

## Связь с задачами
- **TASK_06** (MECHANICUS Formalization) — создание контракта MECHANICUS

## Критерии успеха
- [ ] Каждый активный орган имеет ORGAN_CONTRACT.json
- [ ] Каждый контракт валиден по схеме
- [ ] Каждый орган имеет self-report generator
- [ ] Каждый орган имеет dashboard data generator
- [ ] check_organ_ceremonial возвращает "not ceremonial" для всех активных органов
