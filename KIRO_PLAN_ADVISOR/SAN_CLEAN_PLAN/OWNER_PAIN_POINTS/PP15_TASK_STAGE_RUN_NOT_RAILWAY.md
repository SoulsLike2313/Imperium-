# PP15: TASK/STAGE/RUN Model is Not Yet a Railway

## Проблема
Task ID, stage map, dependencies, gates, receipts и final verdict не достаточно enforced.
Агент может "сойти с рельсов" в любой момент.

## Требование Owner
Каждая задача должна иметь:
- Dependency map (карта зависимостей)
- Stage IDs (идентификаторы этапов)
- Allowed outputs (разрешённые выходы)
- Receipts (квитанции)
- Pass/fail criteria (критерии успеха/неудачи)
- Owner decision gates (точки решения Owner)

## Решение

### Архитектурный паттерн: Orchestration via Workflows
Источник: [System Design Patterns for Managing Long-Running Tasks](https://www.gyanblog.com/software-design/system-design-patterns-managing-long-running-tasks/)

> "Track state in a dedicated store, report progress to clients via polling or SSE, retry with exponential backoff + jitter, checkpoint periodically so crashed workers can resume, and use the saga pattern when tasks span multiple services."

Источник: [Orchestration coordinates a workflow](https://softwarepatternslexicon.com/event-driven-architecture-patterns/workflow-and-sagas/orchestration/)

> "Orchestration coordinates a workflow through an explicit controller that knows the steps, waits for replies or events, tracks state, and decides what to do next."

### Task Railway Model

```
┌─────────────────────────────────────────────────────────────────┐
│                        TASK RAILWAY                              │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  TASK_ID ──► STAGE_1 ──► GATE_1 ──► STAGE_2 ──► GATE_2 ──► ... │
│              │           │          │           │                │
│              ▼           ▼          ▼           ▼                │
│           RECEIPT_1   DECISION   RECEIPT_2   DECISION            │
│                                                                  │
│  ═══════════════════════════════════════════════════════════════│
│  RAILS: Dependencies, Allowed Outputs, Pass/Fail Criteria       │
└─────────────────────────────────────────────────────────────────┘
```

### Структура Task Definition

```json
{
  "schema_version": "task_definition_v0_1",
  "task_id": "TASK-20260514-SAN-CLEANING-PYTHON-FIRST-LAUNCHER-SPINE-V0_1",
  "name": "Python-First Launcher Spine",
  "description": "Создание Python лаунчеров для замены ad hoc PowerShell команд",
  "created": "2026-05-14",
  "owner": "MECHANICUS",
  "priority": "P0",
  
  "dependencies": {
    "tasks": [],
    "files": [
      "ORGANS/ADMINISTRATUM/REGISTRY/PROMPT_AND_BUNDLE_ROUTE_MAP_V0_1.md",
      "REGISTRY/SCRIPT_REGISTRY.json"
    ],
    "tools": ["git", "python3"]
  },
  
  "stages": [
    {
      "stage_id": "STAGE-001-PLANNING",
      "name": "Planning",
      "description": "Прочитать спецификацию и подготовить план",
      "order": 1,
      "required": true,
      "allowed_outputs": ["PLAN.md"],
      "pass_criteria": ["Plan document exists"],
      "fail_criteria": ["Missing dependencies"],
      "gate_after": false
    },
    {
      "stage_id": "STAGE-002-IMPLEMENTATION",
      "name": "Implementation",
      "description": "Создать все лаунчеры",
      "order": 2,
      "required": true,
      "allowed_outputs": [
        "TOOLS/imperium_launcher_v0_1.py",
        "TOOLS/launcher_fetch_bundle_v0_1.py",
        "TOOLS/launcher_apply_bundle_v0_1.py",
        "TOOLS/launcher_commit_push_v0_1.py",
        "TOOLS/launcher_sync_vm2_v0_1.py"
      ],
      "pass_criteria": [
        "All files created",
        "All files compile (py_compile)"
      ],
      "fail_criteria": ["Any file does not compile"],
      "gate_after": false
    },
    {
      "stage_id": "STAGE-003-VERIFICATION",
      "name": "Verification",
      "description": "Проверить все лаунчеры",
      "order": 3,
      "required": true,
      "allowed_outputs": ["VERIFICATION_RECEIPT.json"],
      "pass_criteria": [
        "All --help work",
        "All --dry-run work",
        "All receipts generated"
      ],
      "fail_criteria": ["Any verification fails"],
      "gate_after": true
    },
    {
      "stage_id": "STAGE-004-BUNDLE",
      "name": "Bundle Creation",
      "description": "Создать bundle для PC",
      "order": 4,
      "required": true,
      "allowed_outputs": ["BUNDLE/"],
      "pass_criteria": ["Bundle created with MANIFEST.json"],
      "fail_criteria": ["Bundle incomplete"],
      "gate_after": true
    }
  ],
  
  "gates": [
    {
      "gate_id": "GATE-001-VERIFICATION",
      "after_stage": "STAGE-003-VERIFICATION",
      "type": "auto",
      "condition": "All pass_criteria met",
      "on_pass": "Continue to STAGE-004-BUNDLE",
      "on_fail": "Return to STAGE-002-IMPLEMENTATION"
    },
    {
      "gate_id": "GATE-002-BUNDLE",
      "after_stage": "STAGE-004-BUNDLE",
      "type": "owner_decision",
      "condition": "Owner reviews bundle",
      "on_pass": "Task complete",
      "on_fail": "Return to appropriate stage"
    }
  ],
  
  "final_verdict": {
    "pass_criteria": [
      "All stages completed",
      "All gates passed",
      "Bundle accepted by Owner"
    ],
    "outputs": [
      "5 launcher files in TOOLS/",
      "CONFIG/launcher_routes_v0_1.json",
      "REGISTRY/LAUNCHER_REGISTRY.json",
      "schemas/launcher_receipt_v0_1.schema.json"
    ]
  }
}
```

### Stage Execution Protocol

```python
class StageExecutor:
    """Исполнитель этапов задачи."""
    
    def __init__(self, task_definition: Dict):
        self.task = task_definition
        self.current_stage_index = 0
        self.stage_receipts = []
    
    def execute_stage(self, stage: Dict) -> Dict:
        """Выполнить один этап."""
        receipt = {
            "stage_id": stage["stage_id"],
            "started_at_utc": datetime.now(timezone.utc).isoformat(),
            "status": "IN_PROGRESS"
        }
        
        try:
            # 1. Проверить pre-conditions
            if not self._check_preconditions(stage):
                receipt["status"] = "BLOCKED"
                receipt["reason"] = "Preconditions not met"
                return receipt
            
            # 2. Выполнить работу этапа
            outputs = self._do_stage_work(stage)
            
            # 3. Проверить pass criteria
            pass_check = self._check_pass_criteria(stage, outputs)
            
            if pass_check["all_passed"]:
                receipt["status"] = "PASS"
                receipt["outputs"] = outputs
            else:
                receipt["status"] = "FAIL"
                receipt["failed_criteria"] = pass_check["failed"]
            
        except Exception as e:
            receipt["status"] = "ERROR"
            receipt["error"] = str(e)
        
        receipt["completed_at_utc"] = datetime.now(timezone.utc).isoformat()
        self.stage_receipts.append(receipt)
        
        return receipt
    
    def check_gate(self, gate: Dict) -> Dict:
        """Проверить gate после этапа."""
        if gate["type"] == "auto":
            # Автоматическая проверка
            last_receipt = self.stage_receipts[-1]
            passed = last_receipt["status"] == "PASS"
            return {
                "gate_id": gate["gate_id"],
                "passed": passed,
                "decision": "auto",
                "next_action": gate["on_pass"] if passed else gate["on_fail"]
            }
        
        elif gate["type"] == "owner_decision":
            # Требуется решение Owner
            return {
                "gate_id": gate["gate_id"],
                "passed": None,
                "decision": "pending_owner",
                "next_action": "WAIT_FOR_OWNER"
            }
    
    def get_task_status(self) -> Dict:
        """Получить текущий статус задачи."""
        completed_stages = [r for r in self.stage_receipts if r["status"] == "PASS"]
        failed_stages = [r for r in self.stage_receipts if r["status"] == "FAIL"]
        
        if failed_stages:
            status = "BLOCKED"
        elif len(completed_stages) == len(self.task["stages"]):
            status = "COMPLETED"
        else:
            status = "IN_PROGRESS"
        
        return {
            "task_id": self.task["task_id"],
            "status": status,
            "completed_stages": len(completed_stages),
            "total_stages": len(self.task["stages"]),
            "current_stage": self.task["stages"][self.current_stage_index]["stage_id"],
            "receipts": self.stage_receipts
        }
```

### Task State Machine

```
                    ┌──────────────┐
                    │   CREATED    │
                    └──────┬───────┘
                           │
                           ▼
                    ┌──────────────┐
              ┌─────│  IN_PROGRESS │◄────┐
              │     └──────┬───────┘     │
              │            │             │
              │            ▼             │
              │     ┌──────────────┐     │
              │     │ STAGE_N_DONE │─────┤
              │     └──────┬───────┘     │
              │            │             │
              │            ▼             │
              │     ┌──────────────┐     │
              │     │  GATE_CHECK  │─────┘
              │     └──────┬───────┘
              │            │
              │            ▼
              │     ┌──────────────┐
              │     │OWNER_DECISION│
              │     └──────┬───────┘
              │            │
              ▼            ▼
       ┌──────────┐ ┌──────────────┐
       │  FAILED  │ │  COMPLETED   │
       └──────────┘ └──────────────┘
```

## Файлы для создания

| Файл | Назначение | TASK |
|------|------------|------|
| `schemas/task_definition_v0_1.schema.json` | Схема определения задачи | Отдельная арка |
| `src/imperium/task_executor.py` | Исполнитель задач | Отдельная арка |
| `TOOLS/task_status_v0_1.py` | Проверка статуса задачи | Отдельная арка |

## Проверка

```bash
# 1. Валидация task definition
python3 -c "import json; json.load(open('TASKS/TASK_01/task_definition.json'))"

# 2. Проверка статуса задачи
python3 TOOLS/task_status_v0_1.py --task TASK-20260514-001

# 3. Список всех задач
python3 TOOLS/task_status_v0_1.py --list
```

## Связь с задачами
- **Отдельная арка** — Task Railway Implementation
- **TASK_08** (Dashboard Data) — статус задач в dashboard

## Критерии успеха
- [ ] Каждая задача имеет task_definition.json
- [ ] Каждый этап имеет receipt
- [ ] Gates enforced (нельзя пропустить)
- [ ] Owner decision gates работают
- [ ] Статус задачи всегда известен
