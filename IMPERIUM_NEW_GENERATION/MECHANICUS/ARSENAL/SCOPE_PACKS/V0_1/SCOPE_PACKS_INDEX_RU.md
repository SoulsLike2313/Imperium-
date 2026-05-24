# Mechanicus Scope Packs Index RU (V0.1)

Назначение: быстрый доступ будущего Servitor/local-agent к разрешенным capability-срезам по типам задач.

| Scope ID | Файл | CANON | SANDBOX | CANDIDATE | OWNER_DECISION | FORBIDDEN |
|---|---|---:|---:|---:|---:|---:|
| code_quality_task | scope_code_quality_task_v0_1.json | 2 | 14 | 1 | 12 | 1 |
| json_schema_validation_task | scope_json_schema_validation_task_v0_1.json | 3 | 4 | 7 | 12 | 0 |
| mechanicus_tool_validation_task | scope_mechanicus_tool_validation_task_v0_1.json | 3 | 4 | 12 | 12 | 0 |
| controlled_tool_provision_task | scope_controlled_tool_provision_task_v0_1.json | 2 | 13 | 4 | 12 | 0 |
| repo_hygiene_task | scope_repo_hygiene_task_v0_1.json | 1 | 5 | 12 | 12 | 0 |
| taskpack_generation_task | scope_taskpack_generation_task_v0_1.json | 1 | 1 | 15 | 12 | 0 |
| visual_readiness_task | scope_visual_readiness_task_v0_1.json | 0 | 2 | 13 | 12 | 2 |

## Важные правила
- `visual_readiness_task` = только readiness; без запуска визуальных прототипов.
- `controlled_tool_provision_task` = только Owner-approved install lane; silent install запрещен.
- Во всех scope действует запрет на LLM/cloud activation без отдельного Owner gate.

## Как применять
1. Определи тип задачи.
2. Открой соответствующий scope pack.
3. Используй только `canon_allowed`/`sandbox_allowed` по условиям gates/receipts.
4. `candidate_context_only` — для планирования, не для исполнения.
5. Проверь `forbidden_actions` до запуска команд.
