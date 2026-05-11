# Servitor Route Test

Purpose:
Проверить, что Servitor можно направить в работу по Local Task ID.

General Task:
GTASK-20260511-ASTRONOMICON-GENERAL-TASK-V0_1

Example route:

1. Servitor receives LOCAL_TASK_ID: LTASK-001
2. Servitor opens: LOCAL_TASKS/LTASK-001/LOCAL_TASK.json
3. Servitor reads parent_general_task_id, scope_text, expected_output, required_organs, execution_mode.
4. Servitor goes to Administratum for context/readiness.
5. Servitor follows required organs route.

Available Local Tasks:

- LTASK-001: First local task title
- LTASK-002: Second local task title