# PP01: Memory / Continuity Loss Between Chats

## Проблема
Новый Logos / Servitor может не войти в точную текущую точку работы.
Контекст теряется между сессиями, агент начинает с нуля или с неполной картиной.

## Требование Owner
Continuity handoff должен доказывать:
- Текущую Git правду (HEAD, commit count)
- Состояние PC/VM2
- Историю последних действий
- Следующий шаг
- Блокеры
- Релевантные ссылки на local/private контекст

## Решение

### Архитектурный паттерн: Warm Transfer with Context Payload
Источник: [Context Preservation: Seamless AI Handoffs](https://www.operion.io/learn/component/context-preservation)

> "Context preservation maintains relevant history, decisions, and state when work transitions between handlers."

### Структура Continuity Pack v2

```json
{
  "schema_version": "continuity_pack_v2",
  "generated_at_utc": "2026-05-14T12:00:00Z",
  "generator": "continuity_pack_generator_v0_2.py",
  
  "git_truth": {
    "pc_head": "9307c4883926edd3f843fd1224fdee244b47b1a0",
    "vm2_head": "9307c4883926edd3f843fd1224fdee244b47b1a0",
    "github_head": "9307c4883926edd3f843fd1224fdee244b47b1a0",
    "commit_count": 80,
    "last_commit_message": "[TASK-001] Applied bundle changes",
    "parity_status": "SYNCED"
  },
  
  "platform_state": {
    "pc": {
      "repo_clean": true,
      "uncommitted_changes": [],
      "last_action": "commit_push",
      "last_action_time": "2026-05-14T11:55:00Z"
    },
    "vm2": {
      "repo_clean": true,
      "uncommitted_changes": [],
      "last_action": "git_pull",
      "last_action_time": "2026-05-14T11:56:00Z"
    }
  },
  
  "work_context": {
    "current_arc": "San-Cleaning",
    "current_task": "TASK-20260514-SAN-CLEANING-PYTHON-FIRST-LAUNCHER-SPINE-V0_1",
    "current_stage": "IMPLEMENTATION",
    "completed_stages": ["PLANNING", "DESIGN"],
    "next_atomic_step": "Create TOOLS/launcher_fetch_bundle_v0_1.py",
    "blockers": [],
    "warnings": ["20 scripts need path update"]
  },
  
  "history": {
    "last_5_actions": [
      {"action": "Created imperium_launcher_v0_1.py", "time": "2026-05-14T10:00:00Z"},
      {"action": "Ran py_compile", "time": "2026-05-14T10:05:00Z"},
      {"action": "Created launcher_routes_v0_1.json", "time": "2026-05-14T10:10:00Z"},
      {"action": "Built bundle", "time": "2026-05-14T11:00:00Z"},
      {"action": "PC applied bundle", "time": "2026-05-14T11:55:00Z"}
    ],
    "last_receipt": ".imperium_runtime/launcher/COMMIT_PUSH_RECEIPT.json"
  },
  
  "external_context_refs": {
    "local_manifest": "E:\\IMPERIUM_CONTEXT\\LOCAL\\MANIFEST.json",
    "private_manifest": "E:\\IMPERIUM_CONTEXT\\PRIVATE\\MANIFEST_REDACTED.json",
    "relevant_files": [
      "CURRENT_STATE/ADDRESS_REPAIR_REPORT_20260514.md",
      "REGISTRY/SCRIPT_REGISTRY.json"
    ]
  },
  
  "agent_instructions": {
    "read_first": [
      "AGENTS.md",
      "KIRO_PLAN_ADVISOR/SAN_CLEAN_PLAN/00_SERVITOR_ENTRY.md"
    ],
    "do_not": [
      "Commit from VM2",
      "Modify sanctum_v0_29_qt.py",
      "Set READY_FOR_AGENT=true"
    ],
    "verify_before_work": [
      "git rev-parse HEAD == {pc_head}",
      "python3 scripts/verify_repo.py"
    ]
  }
}
```

### Алгоритм генерации

```python
def generate_continuity_pack() -> Dict:
    """Генерировать Continuity Pack v2."""
    pack = {
        'schema_version': 'continuity_pack_v2',
        'generated_at_utc': datetime.now(timezone.utc).isoformat(),
    }
    
    # 1. Git Truth
    pack['git_truth'] = collect_git_truth()
    
    # 2. Platform State
    pack['platform_state'] = collect_platform_state()
    
    # 3. Work Context
    pack['work_context'] = collect_work_context()
    
    # 4. History
    pack['history'] = collect_recent_history()
    
    # 5. External Context Refs
    pack['external_context_refs'] = collect_external_refs()
    
    # 6. Agent Instructions
    pack['agent_instructions'] = generate_agent_instructions()
    
    return pack
```

## Файлы для создания

| Файл | Назначение |
|------|------------|
| `TOOLS/continuity_pack_generator_v0_2.py` | Генератор Continuity Pack v2 |
| `schemas/continuity_pack_v2.schema.json` | JSON схема |
| `CONFIG/continuity_pack_config.json` | Конфигурация генератора |

## Проверка

```bash
# 1. Генерация pack
python3 TOOLS/continuity_pack_generator_v0_2.py --output CURRENT_STATE/CONTINUITY_PACK.json

# 2. Валидация
python3 -c "import json; json.load(open('CURRENT_STATE/CONTINUITY_PACK.json'))"

# 3. Проверка полноты
python3 TOOLS/continuity_pack_validator_v0_1.py --pack CURRENT_STATE/CONTINUITY_PACK.json
```

## Связь с задачами
- **TASK_08** (Dashboard Data) — включить continuity status в dashboard
- **Отдельная арка** — Continuity Pack v2 Implementation

## Критерии успеха
- [ ] Новый агент может начать работу за < 2 минуты чтения
- [ ] Git truth доказан (не предполагается)
- [ ] Следующий шаг явно указан
- [ ] Блокеры явно указаны
- [ ] История последних действий доступна
